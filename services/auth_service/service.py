# services/auth_service/service.py
import grpc
from concurrent import futures
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from google.protobuf import empty_pb2

# Import generated gRPC code
from proto import auth_pb2, auth_pb2_grpc


# Import DB + CRUD from API gateway
from api_gateway.app import crud, database

class AuthService(auth_pb2_grpc.AuthServiceServicer):

    def Login(self, request: auth_pb2.LoginRequest, context) -> auth_pb2.Token:
        db: Session = database.SessionLocal()
        try:
            user = crud.authenticate_user(db, request.username, request.password)
            if not user:
                # Check if account is locked for a better error message
                db_user = crud.get_user_by_username(db, request.username)
                if db_user and db_user.locked_until and db_user.locked_until > datetime.utcnow():
                    context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                    context.set_details("Account locked. Try again later.")
                else:
                    context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                    context.set_details("Invalid credentials")
                return auth_pb2.Token()  # empty token on error

            # Create access and refresh tokens
            access_token = crud.create_access_token(subject=str(user.id))
            raw_rt, _ = crud.create_refresh_token(db, user_id=user.id)

            return auth_pb2.Token(
                access_token=access_token,
                token_type="bearer",
                role=user.role or "",
                refresh_token=raw_rt
            )
        finally:
            db.close()

    def Refresh(self, request: auth_pb2.RefreshRequest, context) -> auth_pb2.Token:
        db: Session = database.SessionLocal()
        try:
            rt = crud.verify_refresh_token(db, request.refresh_token)
            if not rt:
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details("Invalid refresh token")
                return auth_pb2.Token()

            access_token = crud.create_access_token(subject=str(rt.user_id))
            role = getattr(rt.user, "role", "") if hasattr(rt, "user") else ""

            # Return a new access token; keep refresh token the same
            return auth_pb2.Token(
                access_token=access_token,
                token_type="bearer",
                role=role,
                refresh_token=""  # raw refresh token not returned here
            )
        finally:
            db.close()

    def Logout(self, request: auth_pb2.LogoutRequest, context) -> auth_pb2.LogoutResponse:
        db: Session = database.SessionLocal()
        try:
            rt = crud.verify_refresh_token(db, request.refresh_token)
            if rt:
                crud.revoke_refresh_token(db, rt)
            return auth_pb2.LogoutResponse(ok=True)
        finally:
            db.close()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthService(), server)
    server.add_insecure_port('[::]:50050')
    print("Auth service running on port 50050...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
