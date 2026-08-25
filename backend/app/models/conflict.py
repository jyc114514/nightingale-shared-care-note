"""Optimistic-concurrency conflict model."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, new_id, utcnow
from app.models.enums import ConflictStatus


class Conflict(Base):
    __tablename__ = "conflicts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), index=True, nullable=False)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True, nullable=False)
    entry_id: Mapped[str] = mapped_column(ForeignKey("entries.id"), index=True, nullable=False)
    submitted_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    expected_version: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_version: Mapped[int] = mapped_column(Integer, nullable=False)
    attempted_content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ConflictStatus] = mapped_column(
        String(20), default=ConflictStatus.OPEN, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
