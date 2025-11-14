from fastapi import FastAPI, Depends, HTTPException
from app.routes import users
app = FastAPI(
    title="Online Education Platform",
)

app.include_router(users.router, tags=["users"])
