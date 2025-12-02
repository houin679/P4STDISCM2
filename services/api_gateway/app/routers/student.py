from fastapi import APIRouter, Depends, HTTPException
from typing import List
from .. import schemas, models
from ..deps import get_current_user
import grpc
from services.enrollment_service import enrollment_pb2, enrollment_pb2_grpc

router = APIRouter(prefix="/api/student", tags=["student"])

# gRPC channel + stub for enrollment-service
enroll_channel = grpc.insecure_channel("localhost:50052")
enroll_stub = enrollment_pb2_grpc.EnrollmentServiceStub(enroll_channel)


@router.get("/courses", response_model=List[schemas.CourseRead])
def list_courses(current_user: models.User = Depends(get_current_user)):
    """Fetch all courses via gRPC from enrollment-service."""
    try:
        response = enroll_stub.ListCourses(enrollment_pb2.Empty())
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


@router.post("/courses/{course_id}/enroll")
def enroll_in_course(course_id: int, current_user: models.User = Depends(get_current_user)):
    """Enroll the authenticated student in a course via gRPC."""
    request = enrollment_pb2.EnrollStudentRequest(
        student_id=current_user.id,
        course_id=course_id
    )
    try:
        response = enroll_stub.EnrollStudent(request)
        if not response.enrolled:
            raise HTTPException(status_code=400, detail="Enrollment failed")
        return {"enrolled": True}
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")
