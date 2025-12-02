# services/users_service/service.py
import grpc
from concurrent import futures
from sqlalchemy.orm import Session
from datetime import datetime

# Generated gRPC code
from . import users_pb2
from . import users_pb2_grpc

# Import DB + CRUD from API gateway
from ..api_gateway.app import crud, database
from fastapi import HTTPException


class UsersService(users_pb2_grpc.UsersServiceServicer):

    def CreateUser(self, request: users_pb2.CreateUserRequest, context) -> users_pb2.UserRead:
        db: Session = database.SessionLocal()
        try:
            # Prepare input for CRUD
            user_in = crud.schemas.UserCreate(
                username=request.username,
                email=request.email,
                password=request.password,
                role=request.role if request.role else "student"
            )

            # Check for duplicates
            if crud.get_user_by_username(db, user_in.username):
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Username already exists")
                return users_pb2.UserRead()

            user = crud.create_user(db, user_in)

            return users_pb2.UserRead(
                id=user.id,
                username=user.username,
                email=user.email or "",
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at.isoformat() if user.created_at else ""
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to create user: {str(e)}")
            return users_pb2.UserRead()
        finally:
            db.close()

    def GetUser(self, request: users_pb2.GetUserRequest, context) -> users_pb2.UserRead:
        db: Session = database.SessionLocal()
        try:
            user = crud.get_user_by_id(db, request.user_id)
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with id {request.user_id} not found")
                return users_pb2.UserRead()

            return users_pb2.UserRead(
                id=user.id,
                username=user.username,
                email=user.email or "",
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at.isoformat() if user.created_at else ""
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to fetch user: {str(e)}")
            return users_pb2.UserRead()
        finally:
            db.close()


    def ListUsers(self, request: users_pb2.ListUsersRequest, context) -> users_pb2.ListUsersResponse:
        db: Session = database.SessionLocal()
        try:
            users = crud.get_all_users(db)
            resp = users_pb2.ListUsersResponse()
            for u in users:
                resp.users.append(
                    users_pb2.UserRead(
                        id=u.id,
                        username=u.username,
                        email=u.email or "",
                        role=u.role,
                        is_active=u.is_active,
                        created_at=u.created_at.isoformat() if u.created_at else ""
                    )
                )
            return resp
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to list users: {str(e)}")
            return users_pb2.ListUsersResponse()
        finally:
            db.close()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    users_pb2_grpc.add_UsersServiceServicer_to_server(UsersService(), server)
    server.add_insecure_port("[::]:50054")
    print("Users service running on port 50054...")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
