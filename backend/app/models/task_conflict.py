"""Preserved stale task submissions for deterministic CAS review."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, new_id, utcnow


class TaskConflict(Base):
    __tablename__ = "task_conflicts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), index=True, nullable=False)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True, nullable=False)
    task_id: Mapped[str] = mapped_column(ForeignKey("tasks.id"), index=True, nullable=False)
    submitted_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    expected_version: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_version: Mapped[int] = mapped_column(Integer, nullable=False)
    attempted_title: Mapped[str] = mapped_column(String(200), nullable=False)
    attempted_assignee_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    attempted_status: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
