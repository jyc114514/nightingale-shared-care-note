"""Pydantic contracts for timeline, highlights, provenance, and Glance View."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    FeedbackEventType,
    HighlightActionState,
    HighlightItemKind,
    HighlightStatus,
)


class TimelineEntryOut(BaseModel):
    id: str
    clinic_id: str | None = None
    patient_id: str
    entry_type: str
    owner_role: str
    author_role: str
    author_id: str | None = None
    created_by_user_id: str | None = None
    current_version: int
    content: str
    occurred_at: datetime
    source_kind: str
    source_reference: str | None = None
    created_at: datetime
    updated_at: datetime


class HighlightCreate(BaseModel):
    start_offset: int = Field(ge=0)
    end_offset: int = Field(ge=1)
    quote: str = Field(min_length=1)
    item_kind: HighlightItemKind
    display_priority: float = Field(ge=0, le=100)
    risk_level: str | None = Field(default=None, max_length=50)
    risk_reason: str = Field(min_length=1, max_length=300)
    action_label: str | None = Field(default=None, max_length=200)
    action_state: HighlightActionState = HighlightActionState.NOT_APPLICABLE

    model_config = ConfigDict(extra="ignore")


class HighlightReview(BaseModel):
    status: HighlightStatus

    model_config = ConfigDict(extra="ignore")


class HighlightFeedbackCreate(BaseModel):
    event_type: FeedbackEventType
    idempotency_key: str = Field(min_length=1, max_length=200)

    model_config = ConfigDict(extra="ignore")


class HighlightOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    clinic_id: str
    patient_id: str
    source_entry_id: str
    source_version_id: str
    start_offset: int
    end_offset: int
    quote: str
    quote_sha256: str
    offset_unit: str
    item_kind: HighlightItemKind
    status: HighlightStatus
    display_priority: float
    risk_level: str | None
    risk_reason: str
    action_label: str | None
    action_state: HighlightActionState
    created_by_role: str
    created_by_user_id: str | None
    reviewed_by_user_id: str | None
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class GlanceItemOut(BaseModel):
    id: str
    content_summary: str
    feature_signature: str
    item_kind: HighlightItemKind
    status: HighlightStatus
    base_priority: float
    recency_contribution: float
    explicit_risk_contribution: float
    unresolved_action_contribution: float
    clinician_confirmation_contribution: float
    adaptive_feedback_adjustment: float
    ranking_explanation: dict[str, float]
    display_priority: float
    risk_level: str | None
    risk_reason: str
    action_label: str | None
    action_state: HighlightActionState
    source_entry_id: str
    source_version_id: str
    version_number: int
    current_entry_version: int
    source_label: str
    entry_type: str
    occurred_at: datetime
    quote: str


class ImportanceProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    clinic_id: str
    feature_key: str
    positive_count: int
    negative_count: int
    bounded_weight: float
    updated_at: datetime
    version: int


class HighlightFeedbackOut(BaseModel):
    event_id: str
    event_type: FeedbackEventType
    created: bool
    feature_signature: str
    profile: ImportanceProfileOut
    ranking_explanation: dict[str, float]


class ProvenanceSourceOut(BaseModel):
    highlight: HighlightOut
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
