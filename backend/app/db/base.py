"""SQLAlchemy declarative base and portable identifiers."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all Gate A ORM models."""


def new_id() -> str:
    """Return a portable string UUID usable by SQLite and PostgreSQL."""

    return str(uuid4())


def utcnow() -> datetime:
    """Return an aware UTC timestamp for application-created records."""

    return datetime.now(timezone.utc)


# Import models after Base exists so Alembic and create_all see every table.
import app.models  # noqa: E402,F401
