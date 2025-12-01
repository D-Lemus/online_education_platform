# edu_app/routes/enrollments.py
from fastapi import APIRouter, Depends, HTTPException
import json
import pydgraph

from edu_app.services.audit_service import log_query
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


@router.post("/enroll")
def enroll_user(
    payload: EnrollmentRequest,
    db: Database = Depends(get_mongo_db),
):
    """
    RF-21: Enroll a user (student) in a course.

    - Ensures the User and Course nodes exist in Dgraph.
    - Checks in Dgraph if the user is ALREADY enrolled in that course.
      - If yes: do NOT create a new edge, do NOT increment enrolled_count.
      - If no: create edge user --enrolled_in--> course and increment enrolled_count in Mongo.
    """
    client = get_dgraph_client()

    # 1) Ensure user and course nodes exist (or create them)
    user_uid = get_or_create_user_uid(client, payload.user_id)
    course_uid = get_or_create_course_uid(client, payload.course_id)

    # 2) Check in Dgraph if the user is already enrolled in this course
    check_query = """
        query q($uid: string, $cid: string) {
          user(func: eq(user_id, $uid)) {
            enrolled_in @filter(eq(course_id, $cid)) {
              course_id
            }
          }
        }
    """

    data = run_query(client, check_query, {"$uid": payload.user_id, "$cid": payload.course_id})
    users = data.get("user", [])
    already_enrolled = False

    if users:
        enrolled_edges = users[0].get("enrolled_in", [])
        if enrolled_edges:
            already_enrolled = True

    if already_enrolled:
        # No-op: user is already enrolled, do not create duplicate edge or increment counter
        return {
            "message": "User was already enrolled in this course. No changes applied.",
            "user_id": payload.user_id,
            "course_id": payload.course_id,
            "enrolled": False,
        }

    # 3) User is NOT yet enrolled: create edge user -> enrolled_in -> course in Dgraph
    nquads = f"<{user_uid}> <enrolled_in> <{course_uid}> ."
    mutate_nquads(client, nquads_set=nquads)

    log_query(
        user_id=user_uid,
        query_text="ENROLLED_IN",
        params={
            "course_uid": payload.course_id,
        },
    )

    # 4) Increment enrolled_count in Mongo atomically
    courses_collection = db["courses"]
    courses_collection.update_one(
        {"id": payload.course_id},
        {"$inc": {"enrolled_count": 1}}
    )

    return {
        "message": "Student enrolled in course (Dgraph edge created, Mongo counter incremented).",
        "user_id": payload.user_id,
        "course_id": payload.course_id,
        "enrolled": True,
    }

@router.post("/unenroll")
def unenroll_user(
    payload: EnrollmentRequest,
    db: Database = Depends(get_mongo_db),
):
    """
    RF-22: Unenroll a user (student) from a course.
    - Ensures the User and Course nodes exist in Dgraph.
    - Checks in Dgraph if the user is currently enrolled in that course.
      - If NOT enrolled: do NOT delete edge, do NOT decrement enrolled_count.
      - If enrolled: delete edge and decrement enrolled_count in Mongo (not below 0).
    """
    client = get_dgraph_client()

    user_uid = get_or_create_user_uid(client, payload.user_id)
    course_uid = get_or_create_course_uid(client, payload.course_id)

    # 1) Check if the user is currently enrolled in the course
    check_query = """
        query q($uid: string, $cid: string) {
          user(func: eq(user_id, $uid)) {
            enrolled_in @filter(eq(course_id, $cid)) {
              course_id
            }
          }
        }
    """

    data = run_query(client, check_query, {"$uid": payload.user_id, "$cid": payload.course_id})
    users = data.get("user", [])
    is_enrolled = False

    if users:
        enrolled_edges = users[0].get("enrolled_in", [])
        if enrolled_edges:
            is_enrolled = True

    if not is_enrolled:
        # No-op: user is not actually enrolled, do not delete edge or decrement counter
        return {
            "message": "User is not enrolled in this course. No changes applied.",
            "user_id": payload.user_id,
            "course_id": payload.course_id,
            "unenrolled": False,
        }

    # 2) User IS enrolled: remove edge user -> enrolled_in -> course in Dgraph
    nquads = f"<{user_uid}> <enrolled_in> <{course_uid}> ."
    mutate_nquads(client, nquads_del=nquads)

    log_query(
        user_id=user_uid,
        query_text="UNENROLLED_FROM",
        params={
            "course_uid": payload.course_id,
        },
    )

    # 3) Decrement enrolled_count in Mongo, but not below 0
    courses_collection = db["courses"]
    courses_collection.update_one(
        {"id": payload.course_id, "enrolled_count": {"$gt": 0}},
        {"$inc": {"enrolled_count": -1}}
    )

    return {
        "message": "Student unenrolled from course (Dgraph edge removed, Mongo counter decremented).",
        "user_id": payload.user_id,
        "course_id": payload.course_id,
        "unenrolled": True,
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
                    course_name=course_name,  # 🔹 AHORA SÍ LO MANDAMOS
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
def remove_enrollments_for_course_in_dgraph(course_id: str):
    """
    Remove all enrollments for a given course in Dgraph.
    This is intended to be called when a course is deleted in MongoDB.

    Strategy:
    - Find the Course node by course_id.
    - Delete the Course node completely: <course_uid> * * .
      This automatically removes all incoming/outgoing edges,
      including user --enrolled_in--> course.
    """
    client = get_dgraph_client()

    # 1) Find the course node by course_id in Dgraph
    query = """
    query q($cid: string) {
      course(func: eq(course_id, $cid)) {
        uid
        ~enrolled_in { uid }
      }
    }
    """
    data = run_query(client, query, {"$cid": course_id})
    courses = data.get("course", [])
    if not courses:
        # Nothing to clean up (no course node found in Dgraph)
        return

    course_uid = courses[0]["uid"]

    # 2) Delete the Course node completely.
    # This removes all edges related to this course (including ~enrolled_in).
    nquads_del = f"<{course_uid}> * * ."
    mutate_nquads(client, nquads_del=nquads_del)

