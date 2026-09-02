"""Metadata-only snapshots of one internal Glance surface."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, new_id, utcnow


class GlanceImpressionBatch(Base):
    __tablename__ = "glance_impression_batches"
    __table_args__ = (
        UniqueConstraint(
            "clinic_id",
            "idempotency_key",
            name="uq_glance_impression_batch_clinic_idempotency",
        ),
        CheckConstraint(
            "requested_limit >= 1 AND requested_limit <= 6",
            name="ck_glance_impression_batch_limit",
        ),
        CheckConstraint(
            "eligible_count >= 0 AND stored_candidate_count >= 0 AND surfaced_count >= 0",
            name="ck_glance_impression_batch_counts",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), index=True, nullable=False)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True, nullable=False)
    actor_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    actor_role: Mapped[str] = mapped_column(String(20), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(200), nullable=False)
    algorithm_version: Mapped[str] = mapped_column(String(80), nullable=False)
    requested_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    eligible_count: Mapped[int] = mapped_column(Integer, nullable=False)
    stored_candidate_count: Mapped[int] = mapped_column(Integer, nullable=False)
    surfaced_count: Mapped[int] = mapped_column(Integer, nullable=False)
    candidate_truncated: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
