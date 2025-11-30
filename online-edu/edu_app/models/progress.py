from typing import Optional
from enum import Enum
from pydantic import BaseModel


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
