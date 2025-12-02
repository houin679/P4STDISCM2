# services/grades_service/service.py
import grpc
from concurrent import futures
from sqlalchemy.orm import Session
from datetime import datetime

# Generated gRPC code (placed in the same folder by protoc)
from . import grades_pb2
from . import grades_pb2_grpc

# Import DB + CRUD from API gateway
from ..api_gateway.app import crud, database
from fastapi import HTTPException


class GradesService(grades_pb2_grpc.GradesServiceServicer):

    def UploadGrades(self, request: grades_pb2.UploadGradesRequest, context) -> grades_pb2.UploadGradesResponse:
        db: Session = database.SessionLocal()
        try:
            # Convert proto GradeEntry -> list[dict] expected by crud.upload_grades
            entries = [
                {"student_id": entry.student_id, "grade_value": entry.grade_value}
                for entry in request.payload.entries
            ]
            try:
                created_grades = crud.upload_grades(
                    db,
                    course_id=request.course_id,
                    entries=entries,
                    uploaded_by=request.uploaded_by
                )
                return grades_pb2.UploadGradesResponse(created=len(created_grades))
            except HTTPException as e:
                # Known validation error from CRUD (e.g., student not enrolled)
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                # HTTPException.detail may be a str or dict; ensure string
                detail = e.detail if isinstance(e.detail, str) else str(e.detail)
                context.set_details(detail)
                return grades_pb2.UploadGradesResponse(created=0)
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Upload failed: {str(e)}")
                return grades_pb2.UploadGradesResponse(created=0)
        finally:
            db.close()

    def GetMyGrades(self, request: grades_pb2.GetGradesRequest, context) -> grades_pb2.GetGradesResponse:
        db: Session = database.SessionLocal()
        try:
            grades = crud.get_grades_for_student(db, student_id=request.student_id)
            resp = grades_pb2.GetGradesResponse()
            for g in grades:
                uploaded_by = g.uploaded_by if (g.uploaded_by is not None) else 0
                uploaded_at = ""
                try:
                    if getattr(g, "uploaded_at", None):
                        # Convert to ISO string
                        uploaded_at = g.uploaded_at.isoformat()
                except Exception:
                    uploaded_at = ""
                resp.grades.append(
                    grades_pb2.GradeRead(
                        id=g.id,
                        student_id=g.student_id,
                        course_id=g.course_id,
                        grade_value=g.grade_value,
                        semester=g.semester or "",
                        uploaded_by=uploaded_by,
                        uploaded_at=uploaded_at
                    )
                )
            return resp
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to fetch grades: {str(e)}")
            return grades_pb2.GetGradesResponse()
        finally:
            db.close()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grades_pb2_grpc.add_GradesServiceServicer_to_server(GradesService(), server)
    server.add_insecure_port('[::]:50053')
    print("Grades service running on port 50053...")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
