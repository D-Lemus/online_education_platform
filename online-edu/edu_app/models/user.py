"""
user.py right now is a imple pydantic model for the user enity.
This should be enough to start coding routes
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, Literal

class User(BaseModel):
    """Basic user model with email, full name and its role in the system"""
    email: EmailStr
    full_name: str
    role: str = "Student"

class UserCreate(BaseModel):
    """
    This is used when you create a user, its just adds a new passford fiels
    """
    email: EmailStr
    full_name: str
    password: str
    role: str = "Student"



class UserInDB(User):
    """this is representing what we store in databases but the only difference
    is that we store hashed password instead of the real password NOTE(we were not able to create a hashed password)"""
    hashed_password: str

class UserLogin(BaseModel):
    """
    Model for login requests
    Only requires email and password
    """
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    """Data that the user needs to introduce in order to
    update their password """
    full_name: Optional[str]=None
    email:Optional[EmailStr]=None

class UserRoleUpdate(BaseModel):
    """Data that the Admin needs to introduce in order to change a users role"""
    role: Literal["Student","Admin","Teacher"]
