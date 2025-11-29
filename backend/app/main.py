from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .config import CORS_ORIGINS
from .routers import auth, courses, grades, users, student_grades, student
from .grpc_server import start_grpc_server
import threading
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="P4STDISCM2 Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global gRPC server reference
grpc_server = None


@app.on_event("startup")
def on_startup():
    """Initialize the database and start gRPC server at application startup.

    In production you would use Alembic migrations instead of `create_all`.
    """
    global grpc_server
    
    # Initialize database
    init_db()
    
    # Start gRPC server in a separate daemon thread
    try:
        grpc_server = start_grpc_server(port=50051)
        grpc_thread = threading.Thread(target=lambda: grpc_server.wait_for_termination(), daemon=True)
        grpc_thread.start()
    except Exception as e:
        logger.error(f"Failed to start gRPC server: {e}")
        print(f"⚠️ gRPC server failed to start: {e}, continuing with REST API only")


app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(grades.router)
app.include_router(users.router)
app.include_router(student.router)
app.include_router(student_grades.router)


@app.get("/")
def root():
    return {
        "ok": True,
        "message": "P4STDISCM2 backend running",
        "services": {
            "rest": "Available on HTTP/1.1",
            "grpc": "Available on port 50051 (HTTP/2)"
        }
    }


@app.on_event("shutdown")
def on_shutdown():
    """Clean up resources on shutdown"""
    global grpc_server
    if grpc_server:
        grpc_server.stop(0)
        logger.info("gRPC server stopped")
