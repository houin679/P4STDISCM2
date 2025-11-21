from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..database import SessionLocal

router = APIRouter(prefix="/api/users", tags=["users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[schemas.UserRead])
def list_users(db: Session = Depends(get_db)):
    """List all users (for faculty to select students during grade upload)."""
    users = crud.get_all_users(db)
    return users


@router.post("/", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query.__self__.query if False else None
    # Basic duplicate check
    if crud.get_user_by_username(db, user_in.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    user = crud.create_user(db, user_in)
    return user
