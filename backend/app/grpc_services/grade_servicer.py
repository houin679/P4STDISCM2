"""gRPC Grade Service Implementation"""
import grpc
from . import grade_service_pb2, grade_service_pb2_grpc
from ..crud import get_grades_for_student, upload_grades
from ..database import SessionLocal
from datetime import datetime


class GradeServicer(grade_service_pb2_grpc.GradeServiceServicer):
    """gRPC service for grade operations"""

    def GetStudentGrades(self, request, context):
        """Get all grades for a specific student"""
        db = SessionLocal()
        try:
            grades = get_grades_for_student(db, student_id=request.student_id)
            if not grades:
                return grade_service_pb2.GradesResponse(grades=[], count=0)
            
            grade_records = []
            for g in grades:
                grade_records.append(
                    grade_service_pb2.GradeRecord(
                        id=g.id,
                        student_id=g.student_id,
                        course_id=g.course_id,
                        grade_value=g.grade_value,
                        course_code=g.course.code if g.course else "",
                        course_name=g.course.name if g.course else "",
                        uploaded_at=int(g.uploaded_at.timestamp()) if g.uploaded_at else 0,
                        uploaded_by=g.uploaded_by or 0,
                    )
                )
            return grade_service_pb2.GradesResponse(grades=grade_records, count=len(grade_records))
        except Exception as e:
            context.set_details(f"Error retrieving grades: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return grade_service_pb2.GradesResponse()
        finally:
            db.close()

    def UploadGrades(self, request, context):
        """Upload/create grades for a course"""
        db = SessionLocal()
        try:
            entries = [
                {"studentId": str(e.student_id), "grade": e.grade_value}
                for e in request.entries
            ]
            created = upload_grades(
                db,
                course_id=request.course_id,
                entries=entries,
                uploaded_by=request.uploaded_by
            )
            return grade_service_pb2.UploadGradesResponse(
                created_count=len(created),
                success=True,
                message=f"Successfully uploaded {len(created)} grades"
            )
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return grade_service_pb2.UploadGradesResponse(
                success=False,
                message=f"Error uploading grades: {str(e)}"
            )
        finally:
            db.close()

    def StreamStudentGrades(self, request, context):
        """Stream grades for a student (for large datasets)"""
        db = SessionLocal()
        try:
            grades = get_grades_for_student(db, student_id=request.student_id)
            for g in grades:
                yield grade_service_pb2.GradeRecord(
                    id=g.id,
                    student_id=g.student_id,
                    course_id=g.course_id,
                    grade_value=g.grade_value,
                    course_code=g.course.code if g.course else "",
                    course_name=g.course.name if g.course else "",
                    uploaded_at=int(g.uploaded_at.timestamp()) if g.uploaded_at else 0,
                    uploaded_by=g.uploaded_by or 0,
                )
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
        finally:
            db.close()
