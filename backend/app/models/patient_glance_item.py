"""Materialized, source-linked read model for the warm Glance path."""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, new_id, utcnow


class PatientGlanceItem(Base):
    __tablename__ = "patient_glance_items"
    __table_args__ = (UniqueConstraint("highlight_id", name="uq_patient_glance_item_highlight"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    highlight_id: Mapped[str] = mapped_column(
        ForeignKey("highlights.id"), index=True, nullable=False
    )
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), index=True, nullable=False)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True, nullable=False)
    source_entry_id: Mapped[str] = mapped_column(
        ForeignKey("entries.id"), index=True, nullable=False
    )
    source_version_id: Mapped[str] = mapped_column(
        ForeignKey("entry_versions.id"), index=True, nullable=False
    )
    start_offset: Mapped[int] = mapped_column(Integer, nullable=False)
    end_offset: Mapped[int] = mapped_column(Integer, nullable=False)
    quote_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    offset_unit: Mapped[str] = mapped_column(String(30), nullable=False)
    content_summary: Mapped[str] = mapped_column(Text, nullable=False)
    feature_signature: Mapped[str] = mapped_column(String(300), index=True, nullable=False)
    item_kind: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    base_priority: Mapped[float] = mapped_column(Float, nullable=False)
    recency_contribution: Mapped[float] = mapped_column(Float, nullable=False)
    explicit_risk_contribution: Mapped[float] = mapped_column(Float, nullable=False)
    unresolved_action_contribution: Mapped[float] = mapped_column(Float, nullable=False)
    clinician_confirmation_contribution: Mapped[float] = mapped_column(Float, nullable=False)
    adaptive_feedback_adjustment: Mapped[float] = mapped_column(Float, nullable=False)
    ranking_explanation: Mapped[str] = mapped_column(Text, nullable=False)
    display_priority: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    risk_reason: Mapped[str] = mapped_column(String(300), nullable=False)
    action_label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    action_state: Mapped[str] = mapped_column(String(30), nullable=False)
    clinical_conflict_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    safety_class: Mapped[str | None] = mapped_column(String(50), nullable=True)
    safety_floor: Mapped[float | None] = mapped_column(Float, nullable=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    current_entry_version: Mapped[int] = mapped_column(Integer, nullable=False)
    source_label: Mapped[str] = mapped_column(String(120), nullable=False)
    entry_type: Mapped[str] = mapped_column(String(50), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    quote: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
