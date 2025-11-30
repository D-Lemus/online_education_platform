from bson import ObjectId
from cassandra.cqlengine.columns import Boolean
from fastapi import Depends, HTTPException, APIRouter
from pymongo import MongoClient

from ..db.mongo import get_mongo_db
from ..models.courses import Course, CourseCreate

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
