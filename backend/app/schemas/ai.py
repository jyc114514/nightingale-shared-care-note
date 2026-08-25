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
    entry_id: str | None
    highlight_id: str | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None


AIJobStatus = Literal[
    "processing",
    "completed",
    "failed_redaction",
    "failed_provider",
    "failed_provenance",
]
