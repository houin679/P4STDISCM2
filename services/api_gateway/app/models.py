"""SQLAlchemy ORM models for the backend.

This file defines the database schema using SQLAlchemy `Base` declarative models.
Start here to understand the domain objects: `User`, `Course`, `Enrollment`, `Grade`.

Note: Keeping models in a single file is fine for a small project. If the project grows,
split models into domain modules (e.g., `models/users.py`, `models/courses.py`).
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(128), unique=True, index=True, nullable=False)
    email = Column(String(256), unique=True, index=True, nullable=True)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(50), default="student")
    is_active = Column(Boolean, default=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    enrollments = relationship("Enrollment", back_populates="student")
    # `grades` are grades where this user is the student. Specify foreign_keys
    # to disambiguate from `uploaded_by` which also references `users.id`.
    grades = relationship("Grade", back_populates="student", foreign_keys='Grade.student_id')
    # `uploaded_grades` are grades uploaded/entered by this user (grader/uploader).
    uploaded_grades = relationship("Grade", back_populates="uploader", foreign_keys='Grade.uploaded_by')


class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(32), unique=True, index=True, nullable=False)
    name = Column(String(256), nullable=False)
    instructor = Column(String(128), nullable=True)
    capacity = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    enrollments = relationship("Enrollment", back_populates="course")
    grades = relationship("Grade", back_populates="course")


class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    enrolled_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")


class Grade(Base):
    __tablename__ = "grades"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    grade_value = Column(String(16), nullable=False)
    semester = Column(String(64), nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("User", back_populates="grades", foreign_keys=[student_id])
    course = relationship("Course", back_populates="grades")
    # uploader: user who uploaded/entered this grade (may be null)
    uploaded_by_user = Column('uploaded_by', Integer, ForeignKey("users.id"), nullable=True) if False else None
    # Keep original uploaded_by column and expose relationship as `uploader`.
    uploader = relationship("User", back_populates="uploaded_grades", foreign_keys=[uploaded_by])


class RefreshToken(Base):
    """Simple refresh token table.

    We store a hash of the token for revocation and verification. Each login
    creates a refresh token record with an expiry. The raw token value is only
    returned once (on login) and must be stored by the client (HttpOnly cookie
    is recommended).
    """
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_hash = Column(String(256), nullable=False)
    revoked = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
