"""
Dependency helpers for FastAPI routes.

Provides:
- `get_db` - yields a SQLAlchemy session
- `get_current_user` - decodes JWT from Authorization bearer header and returns the DB user
- `require_role(role)` - returns a dependency that enforces a specific user role

Place role checks in routers like:
    from .deps import require_role
    @router.post(..., dependencies=[Depends(require_role("faculty"))])

This keeps HTTP-level concerns (auth/roles) out of CRUD/service functions.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import crud, config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_db():
    """Yield a SQLAlchemy session for a request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Decode JWT access token and return the current user.

    Raises 401 if token invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_id(db, int(sub))
    if user is None:
        raise credentials_exception
    return user


def require_role(role: str):
    """Return a dependency that ensures the current user has the given role.

    Usage:
      @router.post("/secure", dependencies=[Depends(require_role("faculty"))])
    """
    def role_checker(current_user = Depends(get_current_user)):
        if current_user.role != role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
        return current_user

    return role_checker
