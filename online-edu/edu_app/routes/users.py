from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from pymongo import MongoClient
from pymongo.collection import Collection

from os import getenv
from ..db.mongo import get_mongo_db
from ..models.user import User, UserCreate

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

def get_users_collection(db):
    """small funtion to make sure
    we are using the smae database"""
    return db["users"]

@router.post("/", response_model=User)

def create_user(payload: UserCreate, db= Depends(get_mongo_db)):
    users=get_users_collection(db)
    existing = users.find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=400, detail="This email already exists. Add another one")

    user_doc = {
        "email": payload.email,
        "full_name": payload.full_name,
        "role": payload.role,
        "hashed_password": payload.password,  # TODO: real hashing later
    }

    users.insert_one(user_doc)

    # 4. Return public user data (no password)
    return User(
        email=user_doc["email"],
        full_name=user_doc["full_name"],
        role=user_doc["role"],
    )


@router.get("/", response_model=list[User])
def list_users(db = Depends(get_mongo_db)):
    """
    Return all users from MongoDB (without passwords).
    """
    users = get_users_collection(db)

    docs = users.find({})
    result: list[User] = []

    for doc in docs:
        result.append(
            User(
                email=doc["email"],
                full_name=doc["full_name"],
                role=doc.get("role", "student"),
            )
        )

    return result


