"""Clinic-scoped internal assignment/task records."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, new_id, utcnow
from app.models.enums import TaskStatus


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), index=True, nullable=False)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True, nullable=False)
    source_entry_id: Mapped[str | None] = mapped_column(
        ForeignKey("entries.id"), index=True, nullable=True
    )
    source_comment_id: Mapped[str | None] = mapped_column(
        ForeignKey("comments.id"), index=True, nullable=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    assigned_to_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[TaskStatus] = mapped_column(
        String(20), default=TaskStatus.OPEN, index=True, nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
