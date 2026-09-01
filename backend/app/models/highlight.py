"""Immutable-version anchored Glance items and highlight provenance."""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, new_id, utcnow
from app.models.enums import HighlightActionState, HighlightItemKind, HighlightStatus


class Highlight(Base):
    __tablename__ = "highlights"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
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
    quote: Mapped[str] = mapped_column(Text, nullable=False)
    quote_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    offset_unit: Mapped[str] = mapped_column(
        String(30), nullable=False, default="unicode_codepoint"
    )
    item_kind: Mapped[HighlightItemKind] = mapped_column(String(20), nullable=False)
    status: Mapped[HighlightStatus] = mapped_column(String(30), index=True, nullable=False)
    display_priority: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    risk_reason: Mapped[str] = mapped_column(String(300), nullable=False)
    action_label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    action_state: Mapped[HighlightActionState] = mapped_column(String(30), nullable=False)
    clinical_conflict_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    safety_class: Mapped[str | None] = mapped_column(String(50), nullable=True)
    safety_floor: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_by_role: Mapped[str] = mapped_column(String(20), nullable=False)
    reviewed_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
