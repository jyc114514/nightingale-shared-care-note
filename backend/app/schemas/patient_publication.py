"""API contracts for the explicit patient publication gate."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    PatientPublicationSeverity,
    PatientPublicationState,
    PublicationEvidenceStatus,
)


class PatientPublicationCreate(BaseModel):
    """Create an internal draft; content defaults to the selected source snapshot."""

    content: str | None = Field(default=None, min_length=1, max_length=20000)

    model_config = ConfigDict(extra="ignore")


class PatientPublicationUpdate(BaseModel):
    expected_workflow_version: int = Field(ge=1)
    content: str = Field(min_length=1, max_length=20000)

    model_config = ConfigDict(extra="ignore")


class PatientPublicationTransition(BaseModel):
    expected_workflow_version: int = Field(ge=1)

    model_config = ConfigDict(extra="ignore")


class PatientPublicationRecall(BaseModel):
    expected_workflow_version: int = Field(ge=1)
    reason_code: Literal[
        "dosage_error", "clinical_correction", "entered_in_error", "other_safe_code"
    ]

    model_config = ConfigDict(extra="ignore")


class PublicationEvidenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    publication_id: str
    publication_version_id: str
    evidence_type: str
    concept_key: str
    normalized_value: str | None
    unit: str | None
    frequency: str | None
    source_entry_id: str
    source_version_id: str
    start_offset: int
    end_offset: int
    quote: str
    quote_sha256: str
    offset_unit: str
    validation_status: PublicationEvidenceStatus
    created_at: datetime


class PublicationVersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    publication_id: str
    version_number: int
    content: str
    content_sha256: str
    created_by_user_id: str
    created_by_role: str
    created_at: datetime


class PublicationDosageOut(BaseModel):
    status: PublicationEvidenceStatus
    severity_class: PatientPublicationSeverity
    source_concept_key: str | None
    source_value: str | None
    source_unit: str | None
    source_frequency: str | None
    draft_concept_key: str | None
    draft_value: str | None
    draft_unit: str | None
    draft_frequency: str | None
    source_quote: str
    source_start_offset: int
    source_end_offset: int


class PublicationSourceOut(BaseModel):
    source_entry_id: str
    source_version_id: str
    version_number: int
    current_entry_version: int
    entry_type: str
    source_kind: str
    source_reference: str | None
    occurred_at: datetime
    version_content: str
    quote: str
    start_offset: int
    end_offset: int
    quote_sha256: str
    offset_unit: str
    source_is_current_version: bool


class PatientPublicationOut(BaseModel):
    id: str
    clinic_id: str
    patient_id: str
    source_entry_id: str
    source_version_id: str
    state: PatientPublicationState
    content_version: int
    workflow_version: int
    severity_class: PatientPublicationSeverity
    published_entry_id: str | None
    correction_of_publication_id: str | None
    superseded_by_publication_id: str | None
    created_by_user_id: str
    created_by_role: str
    approved_by_user_id: str | None
    approved_at: datetime | None
    approved_content_version: int | None
    published_by_user_id: str | None
    published_at: datetime | None
    recalled_by_user_id: str | None
    recalled_at: datetime | None
    recall_reason_code: str | None
    created_at: datetime
    updated_at: datetime
    current_content: str
    source: PublicationSourceOut
    dosage: PublicationDosageOut
    versions: list[PublicationVersionOut]
    evidence: list[PublicationEvidenceOut]


class PatientCareUpdateOut(BaseModel):
    """Patient-safe response with no workflow/source/internal identifiers."""

    kind: Literal["published", "withdrawn", "corrected"]
    published_at: datetime | None
    content: str | None
    notice: str | None


class PatientCareOut(BaseModel):
    updates: list[PatientCareUpdateOut]
