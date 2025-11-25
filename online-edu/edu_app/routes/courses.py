from bson import ObjectId
from fastapi import Depends, HTTPException, APIRouter
from pymongo import MongoClient

from ..db.mongo import get_mongo_db
from ..models.courses import Course, CourseCreate

def get_courses_collection(db: MongoClient):
    """Pequeña función helper para obtener la colección de cursos."""
    return db["courses"]

router = APIRouter(
    prefix="/courses",
    tags=["courses"]
)

@router.post("/", response_model=Course)
def create_course(
    payload: CourseCreate,
    db: MongoClient = Depends(get_mongo_db)
):
    courses = get_courses_collection(db)

    # Verificar si ya existe un curso con ese nombre
    existing = courses.find_one({"course_name": payload.course_name})
    if existing:
        raise HTTPException(
            status_code=400,
            detail="That course already exists. Add another title"
        )

    # Generar un id propio (además del _id de Mongo)
    course_id = str(ObjectId())

    course_doc = {
        "id": course_id,                    # id que usarás en tu API
        "course_name": payload.course_name,
        "taught_by": payload.taught_by,
        "lessons": [],                      # siempre empieza vacío
    }

    courses.insert_one(course_doc)

    # Devolver un Course que coincida con el response_model
    return Course(**course_doc)


@router.get("/", response_model=list[Course])
def courses_get(db: MongoClient = Depends(get_mongo_db)):
    courses = get_courses_collection(db)

    docs = courses.find({})
    result: list[Course] = []

    for doc in docs:
        result.append(
            Course(
                id=doc.get("id"),                       # el id que tú guardaste
                course_name=doc["course_name"],
                taught_by=doc["taught_by"],
            )
        )
    return result
