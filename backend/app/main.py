from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .config import CORS_ORIGINS
from .routers import auth, courses, grades, users

app = FastAPI(title="P4STDISCM2 Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Initialize the database at application startup for development convenience.

    In production you would use Alembic migrations instead of `create_all`.
    """
    init_db()


app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(grades.router)
app.include_router(users.router)


@app.get("/")
def root():
    return {"ok": True, "message": "P4STDISCM2 backend running"}
