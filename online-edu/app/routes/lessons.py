from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo import MongoClient
from pymongo.collection import Collection

from ..db.mongo import get_mongo_db
from ..models.courses import Lesson
from .courses import get_courses_collection  # ajusta el import según tu estructura

router = APIRouter(
    prefix="/courses",
    tags=["lessons"]
)


@router.post("/{course_id}/lessons", response_model=Lesson)
def create_lesson_for_course(
    course_id: str,
    payload: Lesson,
    db: MongoClient = Depends(get_mongo_db)
):
    courses: Collection = get_courses_collection(db)


    course = courses.find_one({"id": course_id})
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    lessons = course.get("lessons", [])


    for l in lessons:
        if l.get("title") == payload.title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A lesson with that title already exists in this course"
            )
        if l.get("order") == payload.order:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A lesson with that order already exists in this course"
            )

    # 3) Crear el documento de la lección
    lesson_id = str(ObjectId())
    lesson_doc = {
        "id": lesson_id,
        "title": payload.title,
        "content": payload.content,
        "order": payload.order,
    }

    result = courses.update_one(
        {"id": course_id},
        {"$push": {"lessons": lesson_doc}}
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found while updating"
        )

    return Lesson(**lesson_doc)


@router.get("/{course_id}/lessons", response_model=list[Lesson])
def lessons_per_course(
    course_id: str,
    db: MongoClient = Depends(get_mongo_db)
):
    courses: Collection = get_courses_collection(db)

    course = courses.find_one({"id": course_id})
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    lessons = course.get("lessons", [])

    results: list[Lesson] = []

    for l in lessons:
        results.append(
            Lesson(
                id=l.get("id"),
                title=l.get("title"),
                content=l.get("content"),
                order=l.get("order"),
            )

        )

    return results
