from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Optional[str] = None


class TokenPayload(BaseModel):
    sub: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    password: str
    role: Optional[str] = "student"


class UserRead(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    role: str

    class Config:
        orm_mode = True


class CourseCreate(BaseModel):
    code: str
    name: str
    instructor: Optional[str] = None
    capacity: Optional[int] = 0


class CourseRead(BaseModel):
    id: int
    code: str
    name: str
    instructor: Optional[str]
    capacity: int

    class Config:
        orm_mode = True


class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int


class GradeEntry(BaseModel):
    studentId: str
    grade: str


class GradeUpload(BaseModel):
    entries: List[dict]


class GradeRead(BaseModel):
    id: int
    student_id: int
    course_id: int
    grade_value: str
    semester: Optional[str]
    uploaded_by: int | None = None
    uploaded_at: datetime

    class Config:
        orm_mode = True
