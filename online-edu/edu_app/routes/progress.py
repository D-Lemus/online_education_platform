
from typing import Optional
from enum import Enum
from fastapi import APIRouter, Query
from pydantic import BaseModel

from edu_app.db.cassandra import get_cassandra_session
from edu_app.services.audit_service import log_lesson_progress


router = APIRouter(
    prefix="/progress",
    tags=["progress"]
)


# --------- MODELOS ---------
class LessonStatus(str, Enum):
    ENTREGADA = "entregada"
    NO_ENTREGADA = "no_entregada"

class LessonProgressEvent(BaseModel):
    user_id: str
    course_id: str
    lesson_id: str
    status: LessonStatus = LessonStatus.NO_ENTREGADA

class LessonProgressRecord(BaseModel):
    """
    Registro leído desde Cassandra.
    """
    user_id: str
    course_id: str
    lesson_id: str
    ts: str
    status: Optional[str] = None


# --------- ENDPOINTS ---------

@router.post("/complete-lesson")
def complete_lesson(payload: LessonProgressEvent):
    """
    RF-28: Registrar lección completada por estudiante.
    """
    log_result = log_lesson_progress(
        user_id=payload.user_id,
        course_id=payload.course_id,
        lesson_id=payload.lesson_id,
        status=payload.status,
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
    RF-29: Consultar progreso del estudiante en un curso.
    Lee de la tabla lesson_progress filtrando por (user_id, course_id).
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
