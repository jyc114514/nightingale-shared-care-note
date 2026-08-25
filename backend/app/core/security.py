"""Password hashing and short-lived, cookie-backed session tokens."""

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import HTTPException, status
from pwdlib import PasswordHash

from app.config import Settings


SESSION_COOKIE = "nightingale_session"
JWT_ALGORITHM = "HS256"
password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a password with pwdlib's recommended Argon2 configuration."""

    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password without exposing hash details to callers."""

    return password_hasher.verify(password, password_hash)


def require_session_secret(app_settings: Settings) -> str:
    """Fail closed if a session secret is absent or obviously too weak."""

    secret = app_settings.session_secret
    if secret is None or len(secret) < 32:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session secret is not configured",
        )
    return secret


def create_session_token(user_id: str, app_settings: Settings) -> str:
    """Create a signed JWT containing only the user subject and expiry."""

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=app_settings.session_ttl_minutes)
    payload: dict[str, Any] = {"sub": user_id, "iat": now, "exp": expires_at}
    return jwt.encode(payload, require_session_secret(app_settings), algorithm=JWT_ALGORITHM)


def decode_session_token(token: str, app_settings: Settings) -> str:
    """Validate a session JWT and return its user subject."""

    try:
        payload = jwt.decode(
            token,
            require_session_secret(app_settings),
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "exp"]},
        )
    except (jwt.InvalidTokenError, HTTPException) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session subject",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return subject
