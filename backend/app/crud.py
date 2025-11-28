from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt
from typing import List
from . import models, schemas, config
import secrets
import hashlib

# Use argon2 with bcrypt fallback for password hashing
# argon2 is more secure and avoids bcrypt's 72-byte password length limitation
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_user(db: Session, user_in: schemas.UserCreate) -> models.User:
    user = models.User(
        username=user_in.username,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        role=user_in.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_id(db: Session, user_id: int):
    """Return a user by numeric id."""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_all_users(db: Session):
    """Return all users (for faculty grade entry student dropdown)."""
    return db.query(models.User).all()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return None
    # Check for account lockout
    if user.locked_until and user.locked_until > datetime.utcnow():
        return None
    if not verify_password(password, user.password_hash):
        # increment failed attempts and possibly lock account
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
        if user.failed_login_attempts >= config.MAX_LOGIN_ATTEMPTS:
            user.locked_until = datetime.utcnow() + timedelta(seconds=config.LOCKOUT_DURATION_SECONDS)
            user.failed_login_attempts = 0
        db.add(user)
        db.commit()
        return None
    # Successful login -> reset counters
    user.failed_login_attempts = 0
    user.locked_until = None
    db.add(user)
    db.commit()
    return user


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_refresh_token(db: Session, user_id: int, expires_delta: int = config.REFRESH_TOKEN_EXPIRE_SECONDS):
    """Create a refresh token record and return the raw token."""
    raw = secrets.token_urlsafe(32)
    token_hash = _hash_token(raw)
    expires_at = datetime.utcnow() + timedelta(seconds=expires_delta)
    rt = models.RefreshToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
    db.add(rt)
    db.commit()
    db.refresh(rt)
    return raw, rt


def verify_refresh_token(db: Session, raw_token: str):
    """Return the RefreshToken row if valid and not revoked/expired, else None."""
    if not raw_token:
        return None
    token_hash = _hash_token(raw_token)
    rt = db.query(models.RefreshToken).filter(models.RefreshToken.token_hash == token_hash).first()
    if not rt or rt.revoked:
        return None
    if rt.expires_at and rt.expires_at < datetime.utcnow():
        return None
    return rt


def revoke_refresh_token(db: Session, rt: models.RefreshToken):
    rt.revoked = True
    db.add(rt)
    db.commit()
    return True


def revoke_user_refresh_tokens(db: Session, user_id: int):
    db.query(models.RefreshToken).filter(models.RefreshToken.user_id == user_id).update({"revoked": True})
    db.commit()


def create_access_token(subject: str, expires_delta: int = config.ACCESS_TOKEN_EXPIRE_SECONDS) -> str:
    to_encode = {"sub": str(subject), "exp": datetime.utcnow() + timedelta(seconds=expires_delta)}
    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)


# Course CRUD
def create_course(db: Session, course_in: schemas.CourseCreate) -> models.Course:
    course = models.Course(code=course_in.code, name=course_in.name, instructor=course_in.instructor, capacity=course_in.capacity)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def get_courses(db: Session) -> List[models.Course]:
    return db.query(models.Course).all()


def get_course(db: Session, course_id: int):
    return db.query(models.Course).filter(models.Course.id == course_id).first()


def update_course(db: Session, course_id: int, data: dict):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        return None
    for k, v in data.items():
        setattr(course, k, v)
    db.commit()
    db.refresh(course)
    return course


def delete_course(db: Session, course_id: int) -> bool:
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        return False
    db.delete(course)
    db.commit()
    return True


# Enrollment
def enroll_student(db: Session, student_id: int, course_id: int):
    enrollment = models.Enrollment(student_id=student_id, course_id=course_id)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


def upload_grades(db: Session, course_id: int, entries: list[dict], uploaded_by: int):
    result_grades = []

    for entry in entries:
        grade = (
            db.query(models.Grade)
            .filter(models.Grade.student_id == entry["student_id"],
                    models.Grade.course_id == course_id)
            .first()
        )

        if grade:
            # Update existing grade
            grade.grade_value = entry["grade_value"]
            grade.uploaded_by = uploaded_by
        else:
            # Create new grade
            grade = models.Grade(
                student_id=entry["student_id"],
                course_id=course_id,
                grade_value=entry["grade_value"],
                uploaded_by=uploaded_by
            )
            db.add(grade)

        result_grades.append(grade)

    db.commit()
    return result_grades


def get_grades_for_student(db: Session, student_id: int):
    return db.query(models.Grade).filter(models.Grade.student_id == student_id).all()
