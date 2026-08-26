"""Typed payload and output contracts at the local provider boundary."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


AIInteractionType = Literal[
    "ai_doctor_consult_summary",
    "ai_nurse_consult_summary",
    "ai_patient_session_summary",
]


class RedactedPayload(BaseModel):
    interaction_type: AIInteractionType
    redacted_text: str = Field(min_length=1, max_length=20_000)
    source_reference: str = Field(min_length=1, max_length=200)

    model_config = ConfigDict(extra="forbid")


class DeepSeekSuggestion(BaseModel):
    """The only structured fields accepted from the external provider."""

    summary: str = Field(min_length=1, max_length=20_000)
    highlight_quote: str = Field(min_length=1, max_length=5_000)
    item_kind: Literal["information", "action", "flag"]
    priority_reason: str = Field(min_length=1, max_length=300)
    action_label: str | None = Field(default=None, max_length=200)
    action_state: Literal["open", "completed", "not_applicable"]

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ProviderOutput(BaseModel):
    summary: str = Field(min_length=1, max_length=20_000)
    quote: str = Field(min_length=1, max_length=5_000)
    start_offset: int = Field(ge=0)
    end_offset: int = Field(ge=1)
    item_kind: Literal["information", "action", "flag"]
    risk_level: str | None = Field(default=None, max_length=50)
    risk_reason: str = Field(min_length=1, max_length=300)
    action_label: str | None = Field(default=None, max_length=200)
    action_state: Literal["open", "completed", "not_applicable"]

    model_config = ConfigDict(extra="forbid")
