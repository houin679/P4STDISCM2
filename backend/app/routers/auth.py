from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from .. import crud, schemas
from ..database import SessionLocal
from ..deps import get_db
from .. import config
from datetime import timedelta
import typing

router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_db():
    # local compatibility wrapper; real dependency is in `deps.get_db`
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), response: Response = None, db: Session = Depends(get_db)):
    """Authenticate user, return access token in body and set HttpOnly refresh cookie.

    For development we set a refresh token cookie; in production set `secure=True`.
    """
    user = crud.get_user_by_username(db, form_data.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    # Check account lockout
    if user.locked_until and user.locked_until > __import__("datetime").datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account locked. Try again later.")
    # Verify password (this will also update failed attempts in crud.authenticate_user)
    auth_user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not auth_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    # Create access token
    access_token = crud.create_access_token(subject=str(auth_user.id))
    # Create refresh token (stored hashed in DB), return raw token in HttpOnly cookie
    raw_rt, rt_row = crud.create_refresh_token(db, user_id=auth_user.id)
    # Set cookie
    # For local development `secure=False`; in production set secure=True and samesite='lax' or 'strict' as needed.
    response.set_cookie(
        key="refresh_token",
        value=raw_rt,
        httponly=True,
        secure=False,  # set to True in production
        samesite="lax",
        max_age=config.REFRESH_TOKEN_EXPIRE_SECONDS,
    )
    # Return token + role so frontend can set UI role state
    return {"access_token": access_token, "token_type": "bearer", "role": auth_user.role}


@router.post("/refresh", response_model=schemas.Token)
def refresh_token(refresh_token: typing.Optional[str] = Cookie(None), response: Response = None, db: Session = Depends(get_db)):
    """Read refresh token from HttpOnly cookie, verify, and issue a new access token.

    This simple implementation does not rotate refresh tokens; it verifies the
    cookie value against the hashed token stored in DB and returns a new access
    token. You can extend this to rotate refresh tokens and revoke the old one.
    """
    rt = crud.verify_refresh_token(db, refresh_token)
    if not rt:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    # Optional: check expiry done in verify_refresh_token
    access_token = crud.create_access_token(subject=str(rt.user_id))
    return {"access_token": access_token, "token_type": "bearer", "role": rt.user.role}


@router.post("/logout")
def logout(refresh_token: typing.Optional[str] = Cookie(None), response: Response = None, db: Session = Depends(get_db)):
    """Revoke the refresh token and clear cookie."""
    if refresh_token:
        rt = crud.verify_refresh_token(db, refresh_token)
        if rt:
            crud.revoke_refresh_token(db, rt)
    # Clear cookie
    response.delete_cookie("refresh_token")
    return {"ok": True}
