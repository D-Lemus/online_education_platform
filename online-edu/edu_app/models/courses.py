from pydantic import BaseModel
from typing import List, Optional

class Lesson(BaseModel):
    """Lesson model with title content and order within the course."""
    id: Optional[str] = None
    title: str
    content: str
    order: int

class Course(BaseModel):
    """Course model with  lessons."""
    id: Optional[str] = None
    course_name: str
    taught_by: str
    lessons: List[Lesson] = []
    enrolled_count: int = 0

class CourseCreate(BaseModel):
    """Inputs required to create a new course."""
    course_name: str
    taught_by: str

class CourseUpdate(BaseModel):
    course_name: Optional[str] = None
    taught_by: Optional[str] = None
    enrolled_count: Optional[int] = None
