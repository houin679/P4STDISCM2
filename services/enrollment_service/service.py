# services/enrollment_service/service.py
import grpc
from concurrent import futures
from sqlalchemy.orm import Session
from datetime import datetime

from . import enrollment_pb2
from . import enrollment_pb2_grpc

from ..api_gateway.app import crud, database
from fastapi import HTTPException


class EnrollmentService(enrollment_pb2_grpc.EnrollmentServiceServicer):

    def ListCourses(self, request: enrollment_pb2.Empty, context):
        db: Session = database.SessionLocal()
        try:
            courses = crud.get_courses(db)
            response = enrollment_pb2.ListCoursesResponse()

            for c in courses:
                response.courses.append(
                    enrollment_pb2.Course(
                        id=c.id,
                        code=c.code,
                        name=c.name,
                        instructor=c.instructor or "",
                        capacity=c.capacity
                    )
                )

            return response

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to fetch courses: {str(e)}")
            return enrollment_pb2.ListCoursesResponse()

        finally:
            db.close()

    def EnrollStudent(self, request: enrollment_pb2.EnrollStudentRequest, context):
        db: Session = database.SessionLocal()
        try:
            try:
                crud.enroll_student(db, request.student_id, request.course_id)
                return enrollment_pb2.EnrollStudentResponse(enrolled=True)

            except HTTPException as e:
                # Example: "already enrolled"
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details(e.detail)
                return enrollment_pb2.EnrollStudentResponse(enrolled=False)

            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Enrollment failed: {str(e)}")
                return enrollment_pb2.EnrollStudentResponse(enrolled=False)

        finally:
            db.close()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    enrollment_pb2_grpc.add_EnrollmentServiceServicer_to_server(EnrollmentService(), server)
    server.add_insecure_port('[::]:50052')
    print("Enrollment service running on port 50052...")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
