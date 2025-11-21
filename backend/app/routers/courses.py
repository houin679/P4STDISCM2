from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..database import SessionLocal
from ..deps import get_current_user, require_role, get_db

router = APIRouter(prefix="/api/courses", tags=["courses"])


# `get_db` is provided in `deps.get_db` but the module still defines a local one for backward compatibility.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[schemas.CourseRead])
def list_courses(db: Session = Depends(get_db)):
    return crud.get_courses(db)


@router.post("/", response_model=schemas.CourseRead, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role("course_audit_admin"))])
def create_course(course_in: schemas.CourseCreate, db: Session = Depends(get_db)):
    """Create a new course. Restricted to `course_audit_admin` role."""
    return crud.create_course(db, course_in)


@router.put("/{course_id}", response_model=schemas.CourseRead, dependencies=[Depends(require_role("course_audit_admin"))])
def update_course(course_id: int, course_in: schemas.CourseCreate, db: Session = Depends(get_db)):
    """Update an existing course. Restricted to `course_audit_admin`."""
    updated = crud.update_course(db, course_id, course_in.dict())
    if not updated:
        raise HTTPException(status_code=404, detail="Course not found")
    return updated


@router.delete("/{course_id}", dependencies=[Depends(require_role("course_audit_admin"))])
def delete_course(course_id: int, db: Session = Depends(get_db)):
    """Delete a course. Restricted to `course_audit_admin`."""
    ok = crud.delete_course(db, course_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"deleted": True}


@router.post("/{course_id}/enroll")
def enroll(course_id: int, student_id: int = None, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Enroll a student in a course. The `student_id` is optional and if omitted the requester's id is used.

    In the real app, use the authenticated user (current_user) for student enrollment rather than passing an id.
    """
    sid = student_id or current_user.id
    enrollment = crud.enroll_student(db, student_id=sid, course_id=course_id)
    return {"enrolled": True, "id": enrollment.id}
