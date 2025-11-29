"""gRPC User Service Implementation"""
import grpc
from . import user_service_pb2, user_service_pb2_grpc
from ..crud import (
    get_user_by_id, get_user_by_username, authenticate_user, create_user, get_all_users, create_access_token
)
from .. import schemas
from ..database import SessionLocal


class UserServicer(user_service_pb2_grpc.UserServiceServicer):
    """gRPC service for user operations"""

    def AuthenticateUser(self, request, context):
        """Authenticate a user with username and password"""
        db = SessionLocal()
        try:
            user = authenticate_user(db, request.username, request.password)
            if not user:
                return user_service_pb2.AuthResponse(
                    success=False,
                    message="Invalid credentials"
                )
            
            access_token = create_access_token(subject=str(user.id))
            return user_service_pb2.AuthResponse(
                success=True,
                user=user_service_pb2.UserRecord(
                    id=user.id,
                    username=user.username,
                    email=user.email or "",
                    role=user.role,
                    created_at=int(user.created_at.timestamp()) if user.created_at else 0,
                ),
                token=access_token,
                message="Authentication successful"
            )
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return user_service_pb2.AuthResponse(
                success=False,
                message=f"Error during authentication: {str(e)}"
            )
        finally:
            db.close()

    def GetUser(self, request, context):
        """Get a specific user by ID"""
        db = SessionLocal()
        try:
            user = get_user_by_id(db, request.user_id)
            if not user:
                context.set_details("User not found")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return user_service_pb2.UserRecord()
            
            return user_service_pb2.UserRecord(
                id=user.id,
                username=user.username,
                email=user.email or "",
                role=user.role,
                created_at=int(user.created_at.timestamp()) if user.created_at else 0,
            )
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return user_service_pb2.UserRecord()
        finally:
            db.close()

    def ListUsers(self, request, context):
        """List all users"""
        db = SessionLocal()
        try:
            users = get_all_users(db)
            user_records = []
            for u in users:
                user_records.append(
                    user_service_pb2.UserRecord(
                        id=u.id,
                        username=u.username,
                        email=u.email or "",
                        role=u.role,
                        created_at=int(u.created_at.timestamp()) if u.created_at else 0,
                    )
                )
            return user_service_pb2.UsersResponse(users=user_records, count=len(user_records))
        except Exception as e:
            context.set_details(f"Error retrieving users: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return user_service_pb2.UsersResponse()
        finally:
            db.close()

    def CreateUser(self, request, context):
        """Create a new user"""
        db = SessionLocal()
        try:
            user_in = schemas.UserCreate(
                username=request.username,
                email=request.email,
                password=request.password,
                role=request.role or "student",
            )
            user = create_user(db, user_in)
            return user_service_pb2.UserRecord(
                id=user.id,
                username=user.username,
                email=user.email or "",
                role=user.role,
                created_at=int(user.created_at.timestamp()) if user.created_at else 0,
            )
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return user_service_pb2.UserRecord()
        finally:
            db.close()
