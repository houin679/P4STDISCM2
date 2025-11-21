from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..database import SessionLocal
from ..deps import get_current_user, require_role

router = APIRouter(prefix="/api/faculty", tags=["grades"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/courses/{course_id}/grades", dependencies=[Depends(require_role("faculty"))])
def upload_grades(course_id: int, payload: schemas.GradeUpload, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Faculty-only endpoint to upload grades for a course.

    `current_user` is the authenticated faculty member and will be recorded as `uploaded_by`.
    """
    created = crud.upload_grades(db, course_id=course_id, entries=payload.entries, uploaded_by=current_user.id)
    return {"created": len(created)}


@router.get("/me/grades", tags=["grades"])  # note: path under /api/faculty for this scaffold
def get_my_grades(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Get grades for the authenticated user.

    The frontend will call `/api/faculty/me/grades` with the user's access token.
    """
    grades = crud.get_grades_for_student(db, student_id=current_user.id)
    return grades
