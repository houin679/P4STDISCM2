"""gRPC Course Service Implementation"""
import grpc
from . import course_service_pb2, course_service_pb2_grpc
from ..crud import (
    get_courses, get_course, create_course, update_course, delete_course
)
from .. import schemas
from ..database import SessionLocal


class CourseServicer(course_service_pb2_grpc.CourseServiceServicer):
    """gRPC service for course operations"""

    def ListCourses(self, request, context):
        """List all courses"""
        db = SessionLocal()
        try:
            courses = get_courses(db)
            course_records = []
            for c in courses:
                course_records.append(
                    course_service_pb2.CourseRecord(
                        id=c.id,
                        code=c.code,
                        name=c.name,
                        instructor=c.instructor or "",
                        capacity=c.capacity,
                        created_at=int(c.created_at.timestamp()) if c.created_at else 0,
                    )
                )
            return course_service_pb2.CoursesResponse(courses=course_records, count=len(course_records))
        except Exception as e:
            context.set_details(f"Error retrieving courses: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return course_service_pb2.CoursesResponse()
        finally:
            db.close()

    def GetCourse(self, request, context):
        """Get a specific course by ID"""
        db = SessionLocal()
        try:
            course = get_course(db, request.course_id)
            if not course:
                context.set_details("Course not found")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return course_service_pb2.CourseRecord()
            
            return course_service_pb2.CourseRecord(
                id=course.id,
                code=course.code,
                name=course.name,
                instructor=course.instructor or "",
                capacity=course.capacity,
                created_at=int(course.created_at.timestamp()) if course.created_at else 0,
            )
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return course_service_pb2.CourseRecord()
        finally:
            db.close()

    def CreateCourse(self, request, context):
        """Create a new course"""
        db = SessionLocal()
        try:
            course_in = schemas.CourseCreate(
                code=request.code,
                name=request.name,
                instructor=request.instructor,
                capacity=request.capacity,
            )
            course = create_course(db, course_in)
            return course_service_pb2.CourseRecord(
                id=course.id,
                code=course.code,
                name=course.name,
                instructor=course.instructor or "",
                capacity=course.capacity,
                created_at=int(course.created_at.timestamp()) if course.created_at else 0,
            )
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return course_service_pb2.CourseRecord()
        finally:
            db.close()

    def UpdateCourse(self, request, context):
        """Update an existing course"""
        db = SessionLocal()
        try:
            course_data = {
                "code": request.code,
                "name": request.name,
                "instructor": request.instructor,
                "capacity": request.capacity,
            }
            course = update_course(db, request.id, course_data)
            if not course:
                context.set_details("Course not found")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return course_service_pb2.CourseRecord()
            
            return course_service_pb2.CourseRecord(
                id=course.id,
                code=course.code,
                name=course.name,
                instructor=course.instructor or "",
                capacity=course.capacity,
                created_at=int(course.created_at.timestamp()) if course.created_at else 0,
            )
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return course_service_pb2.CourseRecord()
        finally:
            db.close()

    def DeleteCourse(self, request, context):
        """Delete a course"""
        db = SessionLocal()
        try:
            success = delete_course(db, request.course_id)
            if not success:
                context.set_details("Course not found")
                context.set_code(grpc.StatusCode.NOT_FOUND)
            return course_service_pb2.DeleteResponse(
                success=success,
                message="Course deleted successfully" if success else "Course not found"
            )
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return course_service_pb2.DeleteResponse(success=False, message=str(e))
        finally:
            db.close()
