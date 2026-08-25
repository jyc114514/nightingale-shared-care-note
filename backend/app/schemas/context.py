"""Hot/warm/cold patient context response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ContextEntryOut(BaseModel):
    id: str
    patient_id: str
    entry_type: str
    owner_role: str
    author_role: str
    current_version: int
    content: str | None
    occurred_at: datetime
    source_kind: str
    source_reference: str | None
    protection_reason: str | None
    canonical: bool = True


class WarmContextEntryOut(BaseModel):
    id: str
    patient_id: str
    entry_type: str
    owner_role: str
    author_role: str
    current_version: int
    occurred_at: datetime
    source_kind: str
    protection_reason: str | None
    canonical: bool = True


class ArchivalSummarySourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source_entry_id: str
    source_version_id: str
    occurred_at: datetime
    source_order: int


class ArchivalSummaryOut(BaseModel):
    id: str
    period_start: datetime
    period_end: datetime
    summary_text: str
    source_count: int
    source_manifest_hash: str
    generated_by: str
    created_at: datetime
    refreshed_at: datetime
    policy_version: str
    sources: list[ArchivalSummarySourceOut]
    derived: bool = True


class PatientContextOut(BaseModel):
    patient_id: str
    policy_version: str
    hot_entries: list[ContextEntryOut]
    warm_entries: list[WarmContextEntryOut]
    archival_summaries: list[ArchivalSummaryOut]


class ContextRefreshOut(BaseModel):
    patient_id: str
    policy_version: str
    archival_summary_count: int
    archival_source_count: int
