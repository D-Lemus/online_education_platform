from pydantic import BaseModel
from typing import List, Optional

class Lesson(BaseModel):
    """Lesson model: title, content, and order within the course."""
    id: Optional[str] = None
    title: str
    content: str
    order: int


class Course(BaseModel):
    """Course model with embedded lessons."""
    id: Optional[str] = None
    course_name: str
    taught_by: str
    lessons: List[Lesson] = []


class CourseCreate(BaseModel):
    """Inputs required to create a new course."""
    course_name: str
    taught_by: str
