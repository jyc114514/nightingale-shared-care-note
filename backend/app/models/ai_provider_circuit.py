"""Clinic-scoped persistent state for the optional external AI provider circuit."""

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, new_id, utcnow


class AIProviderCircuit(Base):
    __tablename__ = "ai_provider_circuits"
    __table_args__ = (
        UniqueConstraint(
            "clinic_id",
            "provider_name",
            name="uq_ai_provider_circuit_clinic_provider",
        ),
        CheckConstraint(
            "state IN ('closed', 'open', 'half_open')",
            name="ck_ai_provider_circuit_state",
        ),
        CheckConstraint(
            "consecutive_failures >= 0 AND failure_threshold >= 1 AND cooldown_seconds > 0",
            name="ck_ai_provider_circuit_thresholds",
        ),
        CheckConstraint("version >= 1", name="ck_ai_provider_circuit_version_positive"),
        Index("ix_ai_provider_circuits_clinic_state", "clinic_id", "state"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), index=True, nullable=False)
    provider_name: Mapped[str] = mapped_column(String(80), nullable=False)
    state: Mapped[str] = mapped_column(String(20), nullable=False, default="closed")
    consecutive_failures: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failure_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    cooldown_seconds: Mapped[float] = mapped_column(Float, nullable=False, default=60.0)
    opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    open_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_failure_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
