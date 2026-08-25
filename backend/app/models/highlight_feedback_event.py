"""Append-only, clinic-scoped feedback events for importance adaptation."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, new_id, utcnow


class HighlightFeedbackEvent(Base):
    __tablename__ = "highlight_feedback_events"
    __table_args__ = (
        UniqueConstraint(
            "clinic_id",
            "idempotency_key",
            name="uq_highlight_feedback_clinic_idempotency",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), index=True, nullable=False)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True, nullable=False)
    highlight_id: Mapped[str] = mapped_column(
        ForeignKey("highlights.id"), index=True, nullable=False
    )
    actor_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    actor_role: Mapped[str] = mapped_column(String(20), nullable=False)
    event_type: Mapped[str] = mapped_column(String(40), nullable=False)
    feature_signature: Mapped[str] = mapped_column(String(300), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    idempotency_key: Mapped[str] = mapped_column(String(200), nullable=False)
