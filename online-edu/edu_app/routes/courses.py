from bson import ObjectId
from cassandra.cqlengine.columns import Boolean
from fastapi import Depends, HTTPException, APIRouter
from pymongo import MongoClient
from edu_app.routes.enrollments import auto_enroll_teacher
from . import lessons

from ..db.mongo import get_mongo_db
from ..models.courses import Course, CourseCreate, Lesson, CourseUpdate
from ..services.audit_service import log_query


def get_courses_collection(db = Depends(get_mongo_db)):
    """Pequeña función helper para obtener la colección de cursos."""
    return db["courses"]

router = APIRouter(
    prefix="/courses",
    tags=["courses"]
)

@router.post("/", response_model=Course)
def create_course(payload: CourseCreate, db = Depends(get_mongo_db)):
    """Functino that creates a new course """
    courses = get_courses_collection(db)
    course_name = payload.course_name
    existing= courses.find_one({"course_name": course_name})

    if existing:
        raise HTTPException(
            status_code=400,
            detail="That course already exists. Add another title"
            )

    course_id = str(ObjectId())

    course_doc = {
            "id": course_id,
            "course_name": payload.course_name,
            "taught_by": payload.taught_by,
            "lessons": [],
            "enrolled_count": 0,
        }

    courses.insert_one(course_doc)
    # Auto-enroll Teacher in Dgraph
    try:
        auto_enroll_teacher(
            course_id=course_id,
            teacher_email=payload.taught_by
        )
    except Exception as e:
        print(f"Auto enrolliar of teacher failed")

    return Course(**course_doc)


@router.get("/", response_model=list[Course])
def courses_get(db: MongoClient = Depends(get_mongo_db)):
    """Function that show a list of courses """
    courses = get_courses_collection(db)

    docs = courses.find({})
    result: list[Course] = []

    for doc in docs:
        result.append(
            Course(
                id=doc.get("id"),
                course_name=doc["course_name"],
                taught_by=doc["taught_by"],
                enrolled_count=doc.get("enrolled_count", 0),
            )
        )
    return result
@router.get("/by-teacher/{teacher_email}", response_model=list[Course])
def get_courses_by_teacher(
    teacher_email: str,
    db: MongoClient = Depends(get_mongo_db)
):

    courses = get_courses_collection(db)

    docs = courses.find({"taught_by": teacher_email})

    result: list[Course] = []
    for doc in docs:
        result.append(
            Course(
                id=doc.get("id"),
                course_name=doc["course_name"],
                taught_by=doc["taught_by"],
                enrolled_count=doc.get("enrolled_count", 0),
            )
        )

    return result

@router.get("/{course_id}", response_model=Course)
def get_course_by_id(course_id: str, db: MongoClient = Depends(get_mongo_db)):
    """Function that show a list of courses filtered by id"""

    courses = get_courses_collection(db)

    doc = courses.find_one({"id": course_id})
    if not doc:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return Course(
        id=doc["id"],
        course_name=doc["course_name"],
        taught_by=doc["taught_by"],
        lessons=doc.get("lessons", []),
        enrolled_count=doc.get("enrolled_count", 0),
    )

@router.put("/{course_id}", response_model=CourseUpdate)
def update_course(course_id:str, payload : CourseUpdate, db = Depends(get_mongo_db)):
    """Function that updates a course """
    courses = get_courses_collection(db)

    update_data = {}
    if payload.course_name is not None:
        update_data["course_name"]=payload.course_name
    if payload.taught_by is not None:
        update_data["taught_by"]=payload.taught_by
    if payload.enrolled_count is not None:
        update_data["enrolled_count"]=payload.enrolled_count

    doc = courses.find_one({"id": course_id})
    if doc is None:
        raise HTTPException(status_code=404, detail="Course not found")

    results = courses.update_one({'id': course_id}, {'$set': update_data})
    if results.modified_count == 0:
        raise HTTPException(status_code= 404, detail="Course not found")

    log_query(
        user_id="God",
        query_text ="UPDATE_COURSE",
        params={
            "course_id": course_id,
            "course_name": payload.course_name,
            "taught_by": payload.taught_by,
        }
    )

    updated = courses.find_one({"id": course_id})

    return CourseUpdate(
        course_name=updated["course_name"],
        taught_by=updated["taught_by"],
        enrolled_count=updated.get("enrolled_count", 0),
    )

@router.put("/{course_id}/lessons/{lesson_id}", response_model=Lesson)
def update_lesson(course_id: str, lesson_id: str, payload: Lesson, db = Depends(get_mongo_db)):
    """Function that updates a lesson """
    courses = get_courses_collection(db)

    doc = courses.find_one({"id": course_id, "lessons.id":lesson_id})
    if doc is None:
        raise HTTPException(status_code=404, detail="Course or lesson not found")


    results = courses.update_one(
        {"id": course_id, "lessons.id":lesson_id},
        {
            "$set":{
                'lessons.$.title': payload.title,
                'lessons.$.content': payload.content,
                'lessons.$.order': payload.order,
            }
        }
    )

    if results.modified_count == 0:
        raise HTTPException(status_code= 404, detail="lesson unable to be modified.")


    updated = courses.find_one({"id": course_id})

    lesson = None
    for l in updated["lessons"]:
        if l["id"]==lesson_id:
            lesson =  l
            break

    log_query(
        user_id="Teacher or Admin",
        query_text="UPDATE_LESSON",
        params={
            "lesson_id": lesson_id,
            "course_id": course_id,
        }
    )

    return Lesson(**lesson)

@router.delete("/{course_id}/lesson/{lesson_id}", response_model=Lesson)
def delete_lesson(course_id: str, lesson_id: str, db = Depends(get_mongo_db)):
    """Function that deletes a lesson"""
    courses = get_courses_collection(db)

    doc = courses.find_one({"id": course_id, "lessons.id":lesson_id})
    if doc is None:
        raise HTTPException(status_code=404, detail="Course or lesson not found")


    result = courses.update_one(
        {"id": course_id},{"$pull":{"lessons":{"id":lesson_id}}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Course or lesson not found")

    log_query(
        user_id="Teacher or Admin",
        query_text="DELETE_LESSON",
        params={
            "less_id":lesson_id,
        }
    )

    lesson_to_delete = None
    for l in doc["lessons"]:
        if l["id"] == lesson_id:
            lesson_to_delete = l
            break

    return Lesson(**lesson_to_delete)







