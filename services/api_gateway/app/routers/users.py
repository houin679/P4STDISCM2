from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from .. import schemas, models
import grpc
from proto import users_pb2, users_pb2_grpc
from ..deps import get_current_user, require_role  
import os

USERS_SERVICE_HOST = os.environ.get("USERS_SERVICE_HOST", "users_service")
USERS_SERVICE_PORT = os.environ.get("USERS_SERVICE_PORT", "50054")

router = APIRouter(prefix="/api/users", tags=["users"])

# gRPC channel + stub
users_channel = grpc.insecure_channel(f"{USERS_SERVICE_HOST}:{USERS_SERVICE_PORT}")
users_stub = users_pb2_grpc.UsersServiceStub(users_channel)


@router.get("/", response_model=List[schemas.UserRead])
def list_users():
    """List all students (via gRPC)."""
    try:
        request = users_pb2.ListUsersRequest()
        response = users_stub.ListUsers(request)
        # Only include students
        students = [u for u in response.users if u.role == "student"]
        return [
            schemas.UserRead(
                id=u.id,
                username=u.username,
                email=u.email or "",
                role=u.role,
                is_active=u.is_active,
                created_at=u.created_at
            )
            for u in students
        ]
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")


@router.post("/", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_in: schemas.UserCreate):
    """Create a new user (via gRPC)."""
    try:
        request = users_pb2.CreateUserRequest(
            username=user_in.username,
            email=user_in.email or "",
            password=user_in.password,
            role=user_in.role or "student"
        )
        response = users_stub.CreateUser(request)
        return schemas.UserRead(
            id=response.id,
            username=response.username,
            email=response.email or "",
            role=response.role,
            is_active=response.is_active,
            created_at=response.created_at
        )
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.INVALID_ARGUMENT:
            raise HTTPException(status_code=400, detail=e.details())
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")


@router.get("/{user_id}", response_model=schemas.UserRead)
def get_user(user_id: int):
    """Get a user by ID (via gRPC)."""
    try:
        request = users_pb2.GetUserByIdRequest(user_id=user_id)
        response = users_stub.GetUserById(request)
        return schemas.UserRead(
            id=response.id,
            username=response.username,
            email=response.email or "",
            role=response.role,
            is_active=response.is_active,
            created_at=response.created_at
        )
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail=e.details())
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")
