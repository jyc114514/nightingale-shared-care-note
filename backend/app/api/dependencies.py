"""Reusable FastAPI dependencies for authentication and request metadata."""

from uuid import uuid4

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.core.security import SESSION_COOKIE, decode_session_token
from app.db.session import get_db
from app.models import User


def require_allowed_origin(
    request: Request,
    app_settings: Settings = Depends(get_settings),
) -> None:
    """Reject credentialed browser writes from origins outside the allowlist."""

    origin = request.headers.get("origin")
    if origin is not None and origin not in app_settings.allowed_origin_list:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Origin is not allowed for this state-changing request",
        )


def get_request_id(request: Request) -> str:
    """Use a caller-provided correlation ID or create a local opaque ID."""

    return request.headers.get("X-Request-ID") or str(uuid4())


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    app_settings: Settings = Depends(get_settings),
) -> User:
    """Authenticate solely from the HttpOnly session cookie."""

    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = decode_session_token(token, app_settings)
    user = db.scalar(select(User).where(User.id == user_id, User.is_active.is_(True)))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
