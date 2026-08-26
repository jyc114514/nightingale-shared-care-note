"""Materialized active task actions for the Glance read path."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, new_id, utcnow


class TaskGlanceItem(Base):
    __tablename__ = "task_glance_items"
    __table_args__ = (UniqueConstraint("task_id", name="uq_task_glance_task"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    task_id: Mapped[str] = mapped_column(ForeignKey("tasks.id"), index=True, nullable=False)
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), index=True, nullable=False)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True, nullable=False)
    source_entry_id: Mapped[str | None] = mapped_column(
        ForeignKey("entries.id"), index=True, nullable=True
    )
    source_comment_id: Mapped[str | None] = mapped_column(
        ForeignKey("comments.id"), index=True, nullable=True
    )
    content_summary: Mapped[str] = mapped_column(Text, nullable=False)
    display_priority: Mapped[float] = mapped_column(Integer, nullable=False)
    action_label: Mapped[str] = mapped_column(String(200), nullable=False)
    action_state: Mapped[str] = mapped_column(String(20), nullable=False)
    assigned_to_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    assigned_to_display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    task_status: Mapped[str] = mapped_column(String(20), nullable=False)
    task_version: Mapped[int] = mapped_column(Integer, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
