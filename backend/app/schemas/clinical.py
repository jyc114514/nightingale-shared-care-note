"""Typed internal API contracts for the bounded allergy safety slice."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ClinicalAssertionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    clinic_id: str
    patient_id: str
    domain: Literal["allergy"]
    concept_key: str
    polarity: Literal["present", "absent"]
    verification_status: Literal[
        "unconfirmed",
        "confirmed",
        "refuted",
        "entered_in_error",
    ]
    criticality: Literal["unable_to_assess", "high"]
    source_entry_id: str
    source_version_id: str
    start_offset: int
    end_offset: int
    quote: str
    quote_sha256: str
    offset_unit: Literal["unicode_codepoint"]
    asserted_by_role: str
    asserted_by_user_id: str | None
    status: Literal["active", "superseded"]
    superseded_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ClinicalConflictOut(BaseModel):
    id: str
    clinic_id: str
    patient_id: str
    conflict_type: Literal["allergy_assertion_conflict"]
    status: Literal["open", "adjudicated", "superseded"]
    positive_assertion_id: str
    negative_assertion_id: str
    version: int
    resolution: (
        Literal[
            "confirmed_present",
            "confirmed_absent",
            "needs_more_information",
            "entered_in_error",
        ]
        | None
    )
    adjudicated_by_user_id: str | None
    adjudicated_at: datetime | None
    created_at: datetime
    updated_at: datetime
    positive_assertion: ClinicalAssertionOut
    negative_assertion: ClinicalAssertionOut


class ClinicalConflictAdjudication(BaseModel):
    expected_version: int = Field(ge=1)
    resolution: Literal[
        "confirmed_present",
        "confirmed_absent",
        "needs_more_information",
        "entered_in_error",
    ]

    model_config = ConfigDict(extra="ignore")


class ClinicalAssertionSourceOut(BaseModel):
    assertion: ClinicalAssertionOut
    source_entry_id: str
    source_version_id: str
    version_number: int
    current_entry_version: int
    version_content: str
    entry_type: str
    source_kind: str
    source_reference: str | None
    author_role: str
    author_id: str | None
    occurred_at: datetime
    quote: str
    start_offset: int
    end_offset: int
    quote_sha256: str
    offset_unit: Literal["unicode_codepoint"]
    source_is_current_version: bool
