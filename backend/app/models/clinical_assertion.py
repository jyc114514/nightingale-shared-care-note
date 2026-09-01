"""Source-anchored deterministic clinical assertions."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, new_id, utcnow
from app.models.enums import (
    AssertionCriticality,
    AssertionDomain,
    AssertionPolarity,
    AssertionStatus,
    AssertionVerificationStatus,
)


class ClinicalAssertion(Base):
    """An immutable-source-derived assertion with an explicit lifecycle."""

    __tablename__ = "clinical_assertions"
    __table_args__ = (
        UniqueConstraint(
            "source_version_id",
            "start_offset",
            "end_offset",
            "domain",
            "concept_key",
            "polarity",
            name="uq_clinical_assertion_source_span",
        ),
        Index(
            "ix_clinical_assertions_concept_polarity",
            "concept_key",
            "polarity",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), index=True, nullable=False)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True, nullable=False)
    domain: Mapped[AssertionDomain] = mapped_column(String(30), nullable=False)
    concept_key: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    polarity: Mapped[AssertionPolarity] = mapped_column(String(20), nullable=False)
    verification_status: Mapped[AssertionVerificationStatus] = mapped_column(
        String(30), nullable=False
    )
    criticality: Mapped[AssertionCriticality] = mapped_column(String(30), nullable=False)
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
    offset_unit: Mapped[str] = mapped_column(String(30), nullable=False)
    asserted_by_role: Mapped[str] = mapped_column(String(20), nullable=False)
    asserted_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[AssertionStatus] = mapped_column(String(20), index=True, nullable=False)
    superseded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
