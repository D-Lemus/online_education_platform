
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from datetime import datetime
from edu_app.db.cassandra import get_cassandra_session
from edu_app.services.audit_service import log_lesson_progress
from edu_app.models.progress import LessonStatus, LessonProgressEvent, LessonProgressRecord


router = APIRouter(
    prefix="/progress",
    tags=["progress"]
)

# --------- ENDPOINTS ---------

@router.post("/complete-lesson")
def complete_lesson(payload: LessonProgressEvent):

    if isinstance(payload.status, LessonStatus):
        status_value = payload.status.value
    else:
        status_value = str(payload.status)

    log_result = log_lesson_progress(
        user_id=payload.user_id,
        course_id=payload.course_id,
        lesson_id=payload.lesson_id,
        status=status_value,
    )

    return {
        "message": "Lesson progress recorded",
        "log": log_result,
    }

@router.get("/my-progress/{course_id}",response_model=list[LessonProgressRecord])
def my_progress(
    course_id: str,
    user_id: str = Query(..., description="Id del usuario (por ejemplo email)"),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Consults the progress of a student in a course
    reads the table *lesson_progress* filtered by the user_id & course_id
    """
    session = get_cassandra_session()

    cql = """
        SELECT user_id, course_id, lesson_id, ts, status
        FROM lesson_progress
        WHERE user_id = %s AND course_id = %s
        LIMIT %s
        """

    rows = session.execute(cql, (user_id, course_id, limit))

    result: list[LessonProgressRecord] = []
    for row in rows:
        result.append(
            LessonProgressRecord(
                user_id=row.user_id,
                course_id=row.course_id,
                lesson_id=row.lesson_id,
                ts=row.ts.isoformat(),
                status=row.status,
            )
        )

    return result
