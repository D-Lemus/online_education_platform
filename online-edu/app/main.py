from fastapi import FastAPI

from routes import users, courses, lessons

app = FastAPI(
    title="Online Education Platform",
)

app.include_router(users.router)
app.include_router(courses.router)
app.include_router(lessons.router)


