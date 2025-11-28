from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas, models
from ..database import SessionLocal
from ..deps import get_current_user, require_role

router = APIRouter(prefix="/api/student", tags=["student"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/courses", response_model=list[schemas.CourseRead])
def list_courses(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_courses(db)

@router.post("/courses/{course_id}/enroll")
def enroll_in_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.enroll_student(db, current_user.id, course_id)
