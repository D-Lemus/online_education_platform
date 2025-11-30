from pydantic import BaseModel
from typing import Optional
class EnrollmentRequest(BaseModel):

    user_id: str
    course_id: str

class EnrollmentInfo(BaseModel):
    user_id: str
    course_id: str

