from fastapi import FastAPI
from edu_app.routes import users, courses, lessons, progress

app = FastAPI(
    title="Online Education Platform",
)

app.include_router(users.router)
app.include_router(courses.router)
app.include_router(lessons.router)
app.include_router(progress.router)

