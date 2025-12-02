# services/course_service/service.py
import grpc
from concurrent import futures
from sqlalchemy.orm import Session

from . import course_pb2
from . import course_pb2_grpc

from ..api_gateway.app import crud, database


class CourseService(course_pb2_grpc.CourseServiceServicer):

    def ListCourses(self, request: course_pb2.Empty, context) -> course_pb2.ListCoursesResponse:
        db: Session = database.SessionLocal()
        try:
            courses = crud.get_courses(db)
            return course_pb2.ListCoursesResponse(
                courses=[
                    course_pb2.Course(
                        id=c.id,
                        code=c.code,
                        name=c.name,
                        instructor=c.instructor or "",
                        capacity=c.capacity
                    ) for c in courses
                ]
            )
        finally:
            db.close()

    def CreateCourse(self, request: course_pb2.CourseCreate, context) -> course_pb2.Course:
        db: Session = database.SessionLocal()
        try:
            course = crud.create_course(db, request)
            return course_pb2.Course(
                id=course.id,
                code=course.code,
                name=course.name,
                instructor=course.instructor or "",
                capacity=course.capacity
            )
        finally:
            db.close()

    def UpdateCourse(self, request: course_pb2.UpdateCourseRequest, context) -> course_pb2.Course:
        db: Session = database.SessionLocal()
        try:
            updated = crud.update_course(db, request.course_id, request.course.__dict__)
            if not updated:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Course not found")
                return course_pb2.Course()
            return course_pb2.Course(
                id=updated.id,
                code=updated.code,
                name=updated.name,
                instructor=updated.instructor or "",
                capacity=updated.capacity
            )
        finally:
            db.close()

    def DeleteCourse(self, request: course_pb2.DeleteCourseRequest, context) -> course_pb2.DeleteCourseResponse:
        db: Session = database.SessionLocal()
        try:
            deleted = crud.delete_course(db, request.course_id)
            return course_pb2.DeleteCourseResponse(deleted=deleted)
        finally:
            db.close()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    course_pb2_grpc.add_CourseServiceServicer_to_server(CourseService(), server)
    server.add_insecure_port("[::]:50051")
    print("Course service running on port 50051...")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
