from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from .. import schemas
from ..deps import require_role
import grpc
from services.course_service import course_pb2, course_pb2_grpc

router = APIRouter(prefix="/api/courses", tags=["courses"])

# gRPC channel + stub
course_channel = grpc.insecure_channel("localhost:50051")
course_stub = course_pb2_grpc.CourseServiceStub(course_channel)


@router.get("/", response_model=List[schemas.CourseRead])
def list_courses():
    """Fetch all courses via gRPC from course-service."""
    try:
        response = course_stub.ListCourses(course_pb2.Empty())
        return [
            schemas.CourseRead(
                id=c.id,
                code=c.code,
                name=c.name,
                instructor=c.instructor,
                capacity=c.capacity
            ) for c in response.courses
        ]
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")


@router.post("/", response_model=schemas.CourseRead, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role("course_audit_admin"))])
def create_course(course_in: schemas.CourseCreate):
    """Create a new course via gRPC. Restricted to `course_audit_admin` role."""
    request = course_pb2.CourseCreate(
        code=course_in.code,
        name=course_in.name,
        instructor=course_in.instructor or "",
        capacity=course_in.capacity
    )
    try:
        created = course_stub.CreateCourse(request)
        return schemas.CourseRead(
            id=created.id,
            code=created.code,
            name=created.name,
            instructor=created.instructor,
            capacity=created.capacity
        )
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")


@router.put("/{course_id}", response_model=schemas.CourseRead,
            dependencies=[Depends(require_role("course_audit_admin"))])
def update_course(course_id: int, course_in: schemas.CourseCreate):
    """Update an existing course via gRPC. Restricted to `course_audit_admin`."""
    request = course_pb2.UpdateCourseRequest(
        course_id=course_id,
        course=course_pb2.CourseCreate(
            code=course_in.code,
            name=course_in.name,
            instructor=course_in.instructor or "",
            capacity=course_in.capacity
        )
    )
    try:
        updated = course_stub.UpdateCourse(request)
        if updated.id == 0:
            raise HTTPException(status_code=404, detail="Course not found")
        return schemas.CourseRead(
            id=updated.id,
            code=updated.code,
            name=updated.name,
            instructor=updated.instructor,
            capacity=updated.capacity
        )
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")


@router.delete("/{course_id}", dependencies=[Depends(require_role("course_audit_admin"))])
def delete_course(course_id: int):
    """Delete a course via gRPC. Restricted to `course_audit_admin`."""
    request = course_pb2.DeleteCourseRequest(course_id=course_id)
    try:
        response = course_stub.DeleteCourse(request)
        if not response.deleted:
            raise HTTPException(status_code=404, detail="Course not found")
        return {"deleted": True}
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")
