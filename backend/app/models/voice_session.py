"""Metadata and provenance for one synthetic voice-processing session."""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, new_id, utcnow


class VoiceSession(Base):
    __tablename__ = "voice_sessions"
    __table_args__ = (
        Index(
            "uq_voice_session_clinic_idempotency",
            "clinic_id",
            "idempotency_key",
            unique=True,
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), index=True, nullable=False)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True, nullable=False)
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    actor_role: Mapped[str] = mapped_column(String(20), nullable=False)
    interaction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    sample_id: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    audio_reference: Mapped[str] = mapped_column(String(200), nullable=False)
    audio_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    audio_duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    asr_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    asr_model: Mapped[str] = mapped_column(String(100), nullable=False)
    language: Mapped[str] = mapped_column(String(20), nullable=False)
    language_probability: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    error_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(200), nullable=False)
    entry_id: Mapped[str | None] = mapped_column(ForeignKey("entries.id"), nullable=True)
    highlight_id: Mapped[str | None] = mapped_column(ForeignKey("highlights.id"), nullable=True)
    source_segment_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    transcript_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
