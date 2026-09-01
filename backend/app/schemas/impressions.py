"""Typed metadata-only Glance exposure contracts."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


GlanceResourceType = Literal["highlight", "task"]


class GlanceSurfacedItem(BaseModel):
    resource_type: GlanceResourceType
    resource_id: str = Field(min_length=1, max_length=36)

    model_config = ConfigDict(extra="ignore")


class GlanceImpressionCreate(BaseModel):
    idempotency_key: str = Field(min_length=1, max_length=200)
    requested_limit: int = Field(ge=1, le=6)
    surfaced_items: list[GlanceSurfacedItem] = Field(max_length=6)

    model_config = ConfigDict(extra="ignore")


class GlanceImpressionItemOut(BaseModel):
    id: str
    resource_type: GlanceResourceType
    resource_id: str
    feature_signature: str
    candidate_rank: int
    surfaced: bool
    display_priority: float
    safety_class: str | None
    safety_floor: float | None
    created_at: datetime


class GlanceImpressionBatchOut(BaseModel):
    id: str
    clinic_id: str
    patient_id: str
    actor_user_id: str
    actor_role: str
    idempotency_key: str
    algorithm_version: str
    requested_limit: int
    eligible_count: int
    stored_candidate_count: int
    surfaced_count: int
    candidate_truncated: bool
    created_at: datetime
    items: list[GlanceImpressionItemOut]


class ExposureFeatureSummaryOut(BaseModel):
    feature_signature: str
    candidate_count: int
    surfaced_count: int
    exposure_rate: float
    protected_count: int


class ExposureSafetySummaryOut(BaseModel):
    safety_class: str
    candidate_count: int
    surfaced_count: int
    exposure_rate: float


class GlanceExposureSummaryOut(BaseModel):
    patient_id: str
    algorithm_versions: list[str]
    batch_count: int
    eligible_candidate_count: int
    candidate_item_count: int
    surfaced_item_count: int
    truncated_batch_count: int
    feature_summaries: list[ExposureFeatureSummaryOut]
    safety_summaries: list[ExposureSafetySummaryOut]
