from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from .. import schemas, models
from ..deps import get_current_user, require_role
import grpc
from services.grades_service import grades_pb2, grades_pb2_grpc

router = APIRouter(prefix="/api/faculty", tags=["grades"])

# gRPC channel + stub for grades-service
grades_channel = grpc.insecure_channel("localhost:50053")
grades_stub = grades_pb2_grpc.GradesServiceStub(grades_channel)


@router.post("/courses/{course_id}/grades", dependencies=[Depends(require_role("faculty"))])
def upload_grades(course_id: int, payload: schemas.GradeUpload, current_user: models.User = Depends(get_current_user)):
    """
    Upload grades for a course. Faculty only. Can overwrite existing grades.
    """
    # Convert payload entries → GradeUpload proto
    payload_proto = grades_pb2.GradeUpload(
        entries=[
            grades_pb2.GradeEntry(
                student_id=entry["student_id"],
                grade_value=entry["grade_value"]
            )
            for entry in payload.entries
        ]
    )

    request = grades_pb2.UploadGradesRequest(
        course_id=course_id,
        uploaded_by=current_user.id,
        payload=payload_proto
    )

    try:
        response = grades_stub.UploadGrades(request)
        return {"created": response.created}
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")


@router.get("/me/grades", response_model=List[schemas.GradeRead])
def get_my_grades(current_user: models.User = Depends(get_current_user)):
    """
    Get grades for the authenticated faculty (or could be student, if needed).
    """
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
                uploaded_at=g.uploaded_at  # already ISO string
            )
            for g in response.grades
        ]
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")
