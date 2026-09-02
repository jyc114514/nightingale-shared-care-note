"""Versioned semantic conflicts between source-anchored assertions."""

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, new_id, utcnow
from app.models.enums import (
    ClinicalConflictResolution,
    ClinicalConflictStatus,
    ClinicalConflictType,
)


class ClinicalConflict(Base):
    """A preserved contradiction that only a clinician can adjudicate."""

    __tablename__ = "clinical_conflicts"
    __table_args__ = (
        UniqueConstraint(
            "positive_assertion_id",
            "negative_assertion_id",
            name="uq_clinical_conflict_assertion_pair",
        ),
        CheckConstraint(
            "positive_assertion_id <> negative_assertion_id",
            name="ck_clinical_conflict_distinct_assertions",
        ),
        CheckConstraint("version >= 1", name="ck_clinical_conflict_version_positive"),
        Index("ix_clinical_conflicts_clinic_patient", "clinic_id", "patient_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), index=True, nullable=False)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True, nullable=False)
    conflict_type: Mapped[ClinicalConflictType] = mapped_column(String(50), nullable=False)
    status: Mapped[ClinicalConflictStatus] = mapped_column(String(20), index=True, nullable=False)
    positive_assertion_id: Mapped[str] = mapped_column(
        ForeignKey("clinical_assertions.id"), nullable=False
    )
    negative_assertion_id: Mapped[str] = mapped_column(
        ForeignKey("clinical_assertions.id"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    resolution: Mapped[ClinicalConflictResolution | None] = mapped_column(String(40), nullable=True)
    adjudicated_by_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    adjudicated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
