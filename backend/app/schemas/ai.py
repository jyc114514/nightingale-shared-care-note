"""API contracts for redacted local AI processing jobs."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.ai.schemas import AIInteractionType


class AIProcessingRequest(BaseModel):
    interaction_type: AIInteractionType
    text: str = Field(min_length=1, max_length=20_000)
    source_reference: str = Field(min_length=1, max_length=200)
    idempotency_key: str = Field(min_length=1, max_length=200)

    model_config = ConfigDict(extra="ignore")


class AIJobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    clinic_id: str
    patient_id: str
    interaction_type: str
    provider_name: str
    status: str
    idempotency_key: str
    input_hash: str
    source_reference: str
    error_code: str | None
    retry_after_seconds: float | None
    entry_id: str | None
    highlight_id: str | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None


class AIProviderOut(BaseModel):
    """Safe provider metadata for the internal demo panel."""

    provider_name: str
    model: str
    configured: bool
    mode: Literal["fixture", "deepseek"]


class AIProviderStatusOut(BaseModel):
    """Safe per-patient provider availability metadata for internal users."""

    provider_name: str
    model: str
    mode: Literal["fixture", "deepseek"]
    configured: bool
    availability: Literal["available", "degraded", "temporarily_unavailable"]
    circuit_state: Literal["closed", "open", "half_open"]
    retry_after_seconds: float | None
    last_failure_code: str | None
    consecutive_failures: int
    new_suggestions_available: bool
    existing_records_available: bool
    observed_at: datetime
    limitations: list[str]


AIJobStatus = Literal[
    "processing",
    "completed",
    "failed_redaction",
    "failed_provider",
    "failed_provenance",
]
