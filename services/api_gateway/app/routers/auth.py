from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from .. import schemas, config
import typing
import grpc

# gRPC imports
from services.auth_service import auth_pb2, auth_pb2_grpc

router = APIRouter(prefix="/api/auth", tags=["auth"])

# gRPC channel + stub
auth_channel = grpc.insecure_channel("localhost:50050")
auth_stub = auth_pb2_grpc.AuthServiceStub(auth_channel)


# ---------------------------
# LOGIN
# ---------------------------
@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), response: Response = None):
    grpc_req = auth_pb2.LoginRequest(
        username=form_data.username,
        password=form_data.password
    )

    try:
        token = auth_stub.Login(grpc_req)
    except grpc.RpcError as e:
        raise HTTPException(status_code=401, detail=e.details() or "Authentication failed")

    # Set refresh token cookie
    if token.refresh_token:
        response.set_cookie(
            key="refresh_token",
            value=token.refresh_token,
            httponly=True,
            secure=False,  # True in production
            samesite="lax",
            max_age=config.REFRESH_TOKEN_EXPIRE_SECONDS,
        )

    return {
        "access_token": token.access_token,
        "token_type": token.token_type,
        "role": token.role,
    }


# ---------------------------
# REFRESH
# ---------------------------
@router.post("/refresh", response_model=schemas.Token)
def refresh_token(
    refresh_token: typing.Optional[str] = Cookie(None),
    response: Response = None
):
    """Call AuthService.Refresh() using cookie refresh token.
    Auth-service validates & issues a new access token.
    """

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    grpc_req = auth_pb2.RefreshRequest(refresh_token=refresh_token)

    try:
        token = auth_stub.Refresh(grpc_req)
    except grpc.RpcError as e:
        raise HTTPException(status_code=401, detail=e.details() or "Refresh failed")

    return {
        "access_token": token.access_token,
        "token_type": token.token_type,
        "role": token.role,
    }


# ---------------------------
# LOGOUT
# ---------------------------
@router.post("/logout")
def logout(
    refresh_token: typing.Optional[str] = Cookie(None),
    response: Response = None
):
    """Call AuthService.Logout and clear the cookie."""

    if refresh_token:
        grpc_req = auth_pb2.LogoutRequest(refresh_token=refresh_token)
        try:
            auth_stub.Logout(grpc_req)
        except grpc.RpcError:
            pass  # ignore errors; logout is always OK

    response.delete_cookie("refresh_token")
    return {"ok": True}
