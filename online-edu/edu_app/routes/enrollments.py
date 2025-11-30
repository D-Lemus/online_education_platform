# edu_app/routes/enrollments.py
from fastapi import APIRouter, Depends, HTTPException
import json
import pydgraph

from pymongo.database import Database
from edu_app.db.dgraph import get_dgraph_client
from edu_app.db.mongo import get_mongo_db
from edu_app.models.enrollments import EnrollmentRequest, EnrollmentInfo


router = APIRouter(
    prefix="/enrollments",
    tags=["enrollments"],
)


# ---------- Dgraph helper functions ----------

def run_query(client: pydgraph.DgraphClient, query: str, variables: dict | None = None) -> dict:
    """
    Execute a Dgraph query and return the JSON as a Python dict.
    """
    txn = client.txn(read_only=True)
    try:
        res = txn.query(query, variables=variables or {})
        return json.loads(res.json)
    finally:
        txn.discard()


def mutate_nquads(
    client: pydgraph.DgraphClient,
    nquads_set: str | None = None,
    nquads_del: str | None = None,
):
    """
    Execute a Dgraph mutation using N-Quads (set / delete).
    """
    txn = client.txn()
    try:
        mu = pydgraph.Mutation()
        if nquads_set:
            mu.set_nquads = nquads_set.encode("utf-8")
        if nquads_del:
            mu.del_nquads = nquads_del.encode("utf-8")

        res = txn.mutate(mu)
        txn.commit()
        return res
    finally:
        txn.discard()


def get_or_create_user_uid(client: pydgraph.DgraphClient, user_id: str) -> str:
    """
    Look up a User node by user_id. If it does not exist, create it.
    Returns the uid of the node.
    """
    query = """
    query q($uid: string) {
      user(func: eq(user_id, $uid)) {
        uid
      }
    }
    """
    data = run_query(client, query, {"$uid": user_id})
    users = data.get("user", [])
    if users:
        return users[0]["uid"]

    # Create new User
    txn = client.txn()
    try:
        obj = {
            "uid": "_:newuser",
            "dgraph.type": "User",
            "user_id": user_id,
        }
        mu = pydgraph.Mutation(set_json=json.dumps(obj).encode("utf-8"))
        res = txn.mutate(mu, commit_now=True)
        # uid assigned by Dgraph
        return res.uids["newuser"]
    finally:
        txn.discard()


def get_or_create_course_uid(client: pydgraph.DgraphClient, course_id: str) -> str:
    """
    Look up a Course node by course_id. If it does not exist, create it.
    Returns the uid of the node.
    """
    query = """
    query q($cid: string) {
      course(func: eq(course_id, $cid)) {
        uid
      }
    }
    """
    data = run_query(client, query, {"$cid": course_id})
    courses = data.get("course", [])
    if courses:
        return courses[0]["uid"]

    txn = client.txn()
    try:
        obj = {
            "uid": "_:newcourse",
            "dgraph.type": "Course",
            "course_id": course_id,
        }
        mu = pydgraph.Mutation(set_json=json.dumps(obj).encode("utf-8"))
        res = txn.mutate(mu, commit_now=True)
        return res.uids["newcourse"]
    finally:
        txn.discard()


# ---------- ENDPOINTS ----------

@router.post("/enroll")
def enroll_user(payload: EnrollmentRequest):
    """
    RF-21: Enroll a user (student) in a course.
    Creates (if needed) the User and Course nodes in Dgraph
    and adds the edge user --enrolled_in--> course.
    """
    client = get_dgraph_client()

    user_uid = get_or_create_user_uid(client, payload.user_id)
    course_uid = get_or_create_course_uid(client, payload.course_id)

    # Create edge user -> enrolled_in -> course
    nquads = f"<{user_uid}> <enrolled_in> <{course_uid}> ."
    mutate_nquads(client, nquads_set=nquads)

    return {
        "message": "Student enrolled in course (Dgraph)",
        "user_id": payload.user_id,
        "course_id": payload.course_id,
    }


@router.post("/unenroll")
def unenroll_user(payload: EnrollmentRequest):
    """
    RF-22: Unenroll a user (student) from a course.
    Removes the edge user --enrolled_in--> course in Dgraph.
    """
    client = get_dgraph_client()

    user_uid = get_or_create_user_uid(client, payload.user_id)
    course_uid = get_or_create_course_uid(client, payload.course_id)

    nquads = f"<{user_uid}> <enrolled_in> <{course_uid}> ."
    mutate_nquads(client, nquads_del=nquads)

    return {
        "message": "Student unenrolled from course (Dgraph)",
        "user_id": payload.user_id,
        "course_id": payload.course_id,
    }


@router.get("/me", response_model=list[EnrollmentInfo])
def my_enrollments(
    user_id: str,
    db: Database = Depends(get_mongo_db),
):
    """
    RF-23: List the courses a user is enrolled in.
    Reads the User node by user_id in Dgraph and follows enrolled_in -> Course.
    Then, for each course_id, it looks up the course_name in MongoDB.
    """
    client = get_dgraph_client()

    try:
        query = """
            query q($uid: string) {
              user(func: eq(user_id, $uid)) {
                enrolled_in {
                  course_id
                }
              }
            }
            """

        # 1) Ask Dgraph for the enrolled course_ids
        data = run_query(client, query, {"$uid": user_id})
        users = data.get("user", [])
        if not users:
            return []

        enrolled = users[0].get("enrolled_in", [])
        courses_collection = db["courses"]

        result: list[EnrollmentInfo] = []

        # 2) For each course_id, look up the course_name in Mongo
        for c in enrolled:
            cid = c.get("course_id")
            if not cid:
                continue

            doc = courses_collection.find_one({"id": cid})
            course_name = doc.get("course_name") if doc else None

            result.append(
                EnrollmentInfo(
                    user_id=user_id,
                    course_id=cid,

                )
            )

        return result

    except Exception as e:
        # This will make FastAPI return a JSON with the real error message
        raise HTTPException(
            status_code=500,
            detail=f"Error in /enrollments/me: {e}"
        )


@router.get("/courses/{course_id}/students", response_model=list[EnrollmentInfo])
def students_in_course(course_id: str):
    """
    RF-24: List the students enrolled in a given course.
    Looks up the Course node by course_id and follows the reverse edge ~enrolled_in.
    """
    client = get_dgraph_client()

    query = """
    query q($cid: string) {
      course(func: eq(course_id, $cid)) {
        ~enrolled_in {
          user_id
        }
      }
    }
    """

    data = run_query(client, query, {"$cid": course_id})
    courses = data.get("course", [])
    if not courses:
        return []

    users = courses[0].get("~enrolled_in", [])
    result: list[EnrollmentInfo] = []
    for u in users:
        uid_val = u.get("user_id")
        if uid_val:
            # course_name is not resolved here (could be added similar to /me)
            result.append(
                EnrollmentInfo(
                    user_id=uid_val,
                    course_id=course_id,
                )
            )

    return result

def auto_enroll_teacher(course_id: str, teacher_email: str):
    """
    Automatically enrolls a teacher in a newly created course.
    This is used when a course is created in MongoDB.
    """
    client = get_dgraph_client()

    # teacher_email acts as user_id in Dgraph
    user_uid = get_or_create_user_uid(client, teacher_email)
    course_uid = get_or_create_course_uid(client, course_id)

    nquads = f"<{user_uid}> <enrolled_in> <{course_uid}> ."
    mutate_nquads(client, nquads_set=nquads)

    return {
        "message": "Teacher auto-enrolled (Dgraph)",
        "teacher": teacher_email,
        "course_id": course_id
    }

