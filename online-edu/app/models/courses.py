
from pydantic import BaseModel
from typing import List, Optional

class Lesson(BaseModel):
    """Lesson model: title, content, author, and order within the course."""
    id: Optional[str]=None
    title: str
    content: str
    order: int

class Course(BaseModel):
    '''Basic model that includes the name of the course, who
     is taught by and the lessons it has '''
    id: Optional[str]=None
    course_name: str
    taught_by: str
    lessons: List[Lesson] = []


class createCourse(BaseModel):
    '''inputs required in order to create a new course'''
    course_name: str
    taught_by: str

class CourseInDB(Course):
    '''how the course will be stored in mongo, you have to
    make an id fo it'''
    id: str