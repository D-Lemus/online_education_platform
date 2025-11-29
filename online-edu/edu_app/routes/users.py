from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from pymongo import MongoClient

from pymongo.collection import Collection


from ..db.mongo import get_mongo_db
from ..models.user import User, UserCreate, UserLogin, UserUpdate, UserRoleUpdate
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
                "full_name": payload.full_name,
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
@router.get("/{email}", response_model=User)
def get_user_profile(email: str, db: Collection =Depends(get_mongo_db)):
    users = get_users_collection(db)

    doc = users.find_one({"email":email})
    if not doc:
        raise HTTPException(status_code=404, detail="User not found")
    return  User(
        email=doc["email"],
        full_name=doc["full_name"],
        role=doc.get("role", "student"),
    )


def update_user_basic_data_service(email: str, payload: UserUpdate, db):
    users = get_users_collection(db)

    update_data = {}
    if payload.email is not None:
        update_data["email"] = payload.email
    if payload.full_name is not None:
        update_data["full_name"] = payload.full_name

    if not update_data:
        raise HTTPException(status_code=404, detail="No user data found")

    doc = users.find_one({"email": email})
    if doc:
        raise HTTPException(status_code=400, detail="This email already exists. Add another one")
    else:
        result = users.update_one({"email": email}, {"$set": update_data})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="No user data found")

    log_query(
        user_id=str(payload.email),
        query_text="UPDATE_USER",
        params={
            "email": payload.email,
            "full_name": payload.full_name,
        }
    )

    return update_data


@router.put("/{email}", response_model=User)
def update_user_basic_data(email: str, payload: UserUpdate, db=Depends(get_mongo_db)):
    return update_user_basic_data_service(email, payload, db)


@router.post("/login", response_model=User)
def login_user(payload: UserLogin, db=Depends(get_mongo_db)):
    users = get_users_collection(db)

    user_doc = users.find_one({"email": payload.email})
    if not user_doc:
        try:
            log_security_event(
                user_id=str(payload.email),
                action="LOGIN_FAILED",
                details="User entered an Invalid email"
                )
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email",
            )

    stored_password = user_doc.get("hashed_password")
    if stored_password != payload.password:
        try:
            log_security_event(
                user_id=str(payload.email),
                action="LOGIN_FAILED",
                details="User entered an Invalid password"
                )
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail ="Invalid password",
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


#ADMIN QUERIES
@router.put('/{email}/role', response_model=UserRoleUpdate)
def update_user_role(email:str, payload: UserRoleUpdate, db = Depends(get_mongo_db)):
    users = get_users_collection(db)

    doc = users.find_one({"email": email})

    if doc is None:
        raise HTTPException(status_code=404, detail="No user data found")

    result= users.update_one({'email':email},{'$set': {'role':payload.role}})

    if result.modified_count == 0:
        print("Role was the same or nothng was updated")


    log_query(
        user_id=email,
        query_text="UPDATE_USER_ROLE_BY_ADMIN",
        params={
            "new_role": payload.role,
        }
    )

    return UserRoleUpdate(role=payload.role)

@router.delete('/{email}')
def delete_user(email: str, db=Depends(get_mongo_db)):
    users = get_users_collection(db)

    doc = users.find_one({"email": email})

    if doc is None:
        raise HTTPException(status_code=404, detail="No user data found")

    result=users.delete_one({'email':email})
    if result.deleted_count == 0:
        print("Unable to delete user")

    log_query(
        user_id="God",
        query_text="DELETED USER",
        params={
            "deleted_user_email": email,
        }
    )




