"""Versioned clinician publication workflow for the patient portal."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, new_id, utcnow
from app.models.enums import (
    PatientPublicationSeverity,
    PatientPublicationState,
    PublicationEvidenceStatus,
    PublicationEvidenceType,
)


class PatientPublication(Base):
    """Workflow state; patient visibility is derived from this record, not Entry.visibility."""

    __tablename__ = "patient_publications"
    __table_args__ = (
        Index("ix_patient_publications_clinic_patient", "clinic_id", "patient_id"),
        Index("ix_patient_publications_state", "state"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), index=True, nullable=False)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True, nullable=False)
    source_entry_id: Mapped[str] = mapped_column(
        ForeignKey("entries.id"), index=True, nullable=False
    )
    source_version_id: Mapped[str] = mapped_column(
        ForeignKey("entry_versions.id"), index=True, nullable=False
    )
    state: Mapped[PatientPublicationState] = mapped_column(String(30), index=True, nullable=False)
    content_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    workflow_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    severity_class: Mapped[PatientPublicationSeverity] = mapped_column(
        String(30), nullable=False, default=PatientPublicationSeverity.GENERAL
    )
    published_entry_id: Mapped[str | None] = mapped_column(ForeignKey("entries.id"), nullable=True)
    correction_of_publication_id: Mapped[str | None] = mapped_column(
        ForeignKey("patient_publications.id"), nullable=True
    )
    superseded_by_publication_id: Mapped[str | None] = mapped_column(
        ForeignKey("patient_publications.id"), nullable=True
    )
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_by_role: Mapped[str] = mapped_column(String(20), nullable=False)
    approved_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_content_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    published_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    recalled_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    recalled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    recall_reason_code: Mapped[str | None] = mapped_column(String(40), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )


class PatientPublicationVersion(Base):
    """Append-only content snapshot for one publication workflow."""

    __tablename__ = "patient_publication_versions"
    __table_args__ = (
        UniqueConstraint(
            "publication_id",
            "version_number",
            name="uq_patient_publication_version_number",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    publication_id: Mapped[str] = mapped_column(
        ForeignKey("patient_publications.id"), index=True, nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_by_role: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )


class PatientPublicationEvidence(Base):
    """Deterministic source evidence linked to one immutable publication version."""

    __tablename__ = "patient_publication_evidence"
    __table_args__ = (
        Index("ix_patient_publication_evidence_publication_id", "publication_id"),
        Index("ix_patient_publication_evidence_source_version_id", "source_version_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    publication_id: Mapped[str] = mapped_column(
        ForeignKey("patient_publications.id"), nullable=False
    )
    publication_version_id: Mapped[str] = mapped_column(
        ForeignKey("patient_publication_versions.id"), nullable=False
    )
    evidence_type: Mapped[PublicationEvidenceType] = mapped_column(String(40), nullable=False)
    concept_key: Mapped[str] = mapped_column(String(100), nullable=False)
    normalized_value: Mapped[str | None] = mapped_column(String(100), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(30), nullable=True)
    frequency: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source_entry_id: Mapped[str] = mapped_column(ForeignKey("entries.id"), nullable=False)
    source_version_id: Mapped[str] = mapped_column(ForeignKey("entry_versions.id"), nullable=False)
    start_offset: Mapped[int] = mapped_column(Integer, nullable=False)
    end_offset: Mapped[int] = mapped_column(Integer, nullable=False)
    quote: Mapped[str] = mapped_column(Text, nullable=False)
    quote_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    offset_unit: Mapped[str] = mapped_column(String(30), nullable=False)
    validation_status: Mapped[PublicationEvidenceStatus] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
