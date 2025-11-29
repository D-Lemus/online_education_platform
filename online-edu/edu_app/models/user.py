"""
user.py right now is a imple pydantic model for the user enity.
This should be enough to start coding routes
"""

from pydantic import BaseModel, EmailStr
from typing import Optional

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
    """thi is representing what we store in databases. the only difference
    is that we store hashed password instead of the real password"""
    hashed_password: str

class UserLogin(BaseModel):
    """
    Model for login requests.
    Only requires email and password.
    """
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    """Datos que el usuario puede actualizar de su perfil."""
    full_name: Optional[str]=None
    email:Optional[EmailStr]=None

