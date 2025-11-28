from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud, schemas, models
from ..database import SessionLocal
from ..deps import get_current_user

router = APIRouter(prefix="/api/student", tags=["student-grades"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/me/grades", response_model=list[schemas.GradeRead])
def get_student_grades(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Return grades for the authenticated student."""
    return crud.get_grades_for_student(db, student_id=current_user.id)
