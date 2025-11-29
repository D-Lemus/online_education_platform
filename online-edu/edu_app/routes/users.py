from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from pymongo import MongoClient
from pymongo.collection import Collection

from os import getenv
from ..db.mongo import get_mongo_db
from ..models.user import User, UserCreate, UserLogin
from edu_app.services.audit_service import log_query, log_security_event


router = APIRouter(
    prefix="/users",
    tags=["users"]
)

def get_users_collection(db):
    """small funtion to make sure
    we are using the same database"""
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

    #Aqui insertamos el log query de cassandra
    try:
        log_query(
            user_id=str(payload.email),
            query_text="CREATE_USER",
            params={
                "email": payload.email,
                "full_name": payload.email,
                "role":payload.role,
            }
        )
    except Exception:
        pass


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

@router.post("/login", response_model=User)
def login_user(payload: UserLogin, db=Depends(get_mongo_db)):
    users = get_users_collection(db)

    user_doc = users.find_one({"email": payload.email})
    if not user_doc:
        try:
            log_security_event(
                user_id=str(payload.email),
                action="LOGIN_FAILED",
                details="User entered an Invalid email or password"
                )
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            )

    stored_password = user_doc.get("hashed_password")
    if stored_password != payload.password:
        try:
            log_security_event(
                user_id=str(payload.email),
                action="LOGIN_FAILED",
                details="User entered an Invalid email or password"
                )
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail ="Invalid email or password",
        )

    try:
        log_security_event(
            user_id=str(payload.email),
            action="LOGIN_SUCCESS",
            details= "User logged in successfully"
        )
    except Exception:
        pass

    return User(
        email=user_doc["email"],
        full_name=user_doc["full_name"],
        role=user_doc.get("role", "Student"),
    )


