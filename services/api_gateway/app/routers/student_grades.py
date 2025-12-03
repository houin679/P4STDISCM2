from fastapi import APIRouter, Depends, HTTPException
from typing import List
from .. import schemas, models
from ..deps import get_current_user
import grpc
from proto import grades_pb2, grades_pb2_grpc
import os

GRADES_SERVICE_HOST = os.environ.get("GRADES_SERVICE_HOST", "grades_service")
GRADES_SERVICE_PORT = os.environ.get("GRADES_SERVICE_PORT", "50053")

router = APIRouter(prefix="/api/student", tags=["student-grades"])

# gRPC channel + stub for grades-service
grades_channel = grpc.insecure_channel(f"{GRADES_SERVICE_HOST}:{GRADES_SERVICE_PORT}")
grades_stub = grades_pb2_grpc.GradesServiceStub(grades_channel)


@router.get("/me/grades", response_model=List[schemas.GradeRead])
def get_student_grades(current_user: models.User = Depends(get_current_user)):
    """Return grades for the authenticated student via gRPC."""

    request = grades_pb2.GetGradesRequest(student_id=current_user.id)

    try:
        response = grades_stub.GetMyGrades(request)

        return [
            schemas.GradeRead(
                id=g.id,
                student_id=g.student_id,
                course_id=g.course_id,
                grade_value=g.grade_value,
                semester=g.semester or None,
                uploaded_by=g.uploaded_by if g.uploaded_by != 0 else None,
                uploaded_at=g.uploaded_at  # ISO string from gRPC
            )
            for g in response.grades
        ]

    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")
