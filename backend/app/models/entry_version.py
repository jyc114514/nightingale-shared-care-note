"""Immutable entry version snapshots."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, new_id, utcnow


class EntryVersion(Base):
    __tablename__ = "entry_versions"
    __table_args__ = (
        UniqueConstraint("entry_id", "version_number", name="uq_entry_version_number"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    entry_id: Mapped[str] = mapped_column(ForeignKey("entries.id"), index=True, nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_by_role: Mapped[str] = mapped_column(String(20), nullable=False)
    base_version: Mapped[int] = mapped_column(Integer, nullable=False)
    reverted_from_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
