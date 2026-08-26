"""Safe API contracts for the optional prerecorded voice prototype."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


VoiceSampleScope = Literal["patient", "clinical"]
VoiceSessionStatus = Literal[
    "processing",
    "completed",
    "failed_asr",
    "failed_redaction",
    "failed_provider",
    "failed_provenance",
]


class VoiceSampleOut(BaseModel):
    sample_id: str
    label: str
    scope: VoiceSampleScope
    interaction_type: str
    duration_ms: int
    audio_url: str
    provider_disclosure: str


class VoiceSessionCreate(BaseModel):
    sample_id: str = Field(min_length=1, max_length=80)
    idempotency_key: str = Field(min_length=1, max_length=200)

    model_config = ConfigDict(extra="ignore")


class TranscriptSegmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    segment_index: int
    start_ms: int
    end_ms: int
    text: str
    confidence: float | None


class VoiceSessionOut(BaseModel):
    id: str
    clinic_id: str
    patient_id: str
    actor_role: str
    interaction_type: str
    sample_id: str
    audio_sha256: str
    audio_duration_ms: int
    asr_provider: str
    asr_model: str
    language: str
    language_probability: float | None
    status: VoiceSessionStatus
    error_code: str | None
    entry_id: str | None
    highlight_id: str | None
    source_segment_id: str | None
    created_at: datetime
    completed_at: datetime | None
    segments: list[TranscriptSegmentOut] = Field(default_factory=list)
    patient_safe: bool = False


class VoiceProviderOut(BaseModel):
    provider_name: str
    model: str
    mode: Literal["disabled", "fixture", "local_whisper"]
    enabled: bool
    disclosure: str
