"""Metadata-only Glance exposure capture and summary."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import utcnow
from app.models import GlanceImpressionBatch, GlanceImpressionItem
from app.services.entries import record_audit
from app.services.glance_read import (
    ALGORITHM_VERSION,
    GlanceCandidateSnapshot,
)


class ImpressionPayloadConflict(ValueError):
    """Raised when an idempotency key is reused for another payload."""


class InvalidImpression(ValueError):
    """Raised when surfaced resources do not match the current eligible snapshot."""


@dataclass(frozen=True)
class ExposureFeatureSummary:
    feature_signature: str
    candidate_count: int
    surfaced_count: int
    exposure_rate: float
    protected_count: int


@dataclass(frozen=True)
class ExposureSafetySummary:
    safety_class: str
    candidate_count: int
    surfaced_count: int
    exposure_rate: float


@dataclass(frozen=True)
class ExposureSummary:
    patient_id: str
    algorithm_versions: tuple[str, ...]
    batch_count: int
    eligible_candidate_count: int
    candidate_item_count: int
    surfaced_item_count: int
    truncated_batch_count: int
    feature_summaries: tuple[ExposureFeatureSummary, ...]
    safety_summaries: tuple[ExposureSafetySummary, ...]


def _resource_key(resource_type: str, resource_id: str) -> tuple[str, str]:
    return resource_type, resource_id


def impression_batch_items(
    db: Session,
    batch_id: str,
) -> list[GlanceImpressionItem]:
    return list(
        db.scalars(
            select(GlanceImpressionItem)
            .where(GlanceImpressionItem.batch_id == batch_id)
            .order_by(GlanceImpressionItem.candidate_rank, GlanceImpressionItem.id)
        )
    )


def _stored_surface_keys(db: Session, batch_id: str) -> set[tuple[str, str]]:
    return {
        _resource_key(item.resource_type, item.resource_id)
        for item in impression_batch_items(db, batch_id)
        if item.surfaced
    }


def create_glance_impression(
    db: Session,
    *,
    clinic_id: str,
    patient_id: str,
    actor_user_id: str,
    actor_role: str,
    idempotency_key: str,
    requested_limit: int,
    surfaced_items: Iterable[tuple[str, str]],
    snapshot: GlanceCandidateSnapshot,
    request_id: str,
) -> GlanceImpressionBatch:
    """Persist one bounded candidate/surface snapshot without changing ranking."""

    if not 1 <= requested_limit <= 6:
        raise InvalidImpression("requested_limit_out_of_range")
    surfaced_keys = list(surfaced_items)
    if len(surfaced_keys) != len(set(surfaced_keys)):
        raise InvalidImpression("duplicate_surfaced_resource")
    if len(surfaced_keys) > requested_limit:
        raise InvalidImpression("surfaced_count_exceeds_requested_limit")

    existing = db.scalar(
        select(GlanceImpressionBatch).where(
            GlanceImpressionBatch.clinic_id == clinic_id,
            GlanceImpressionBatch.idempotency_key == idempotency_key,
        )
    )
    if existing is not None:
        previous_keys = _stored_surface_keys(db, existing.id)
        if (
            existing.patient_id != patient_id
            or existing.actor_user_id != actor_user_id
            or existing.requested_limit != requested_limit
            or previous_keys != set(surfaced_keys)
        ):
            raise ImpressionPayloadConflict("impression_idempotency_key_reused")
        return existing

    candidate_by_key = {
        _resource_key(candidate.resource_type, candidate.resource_id): candidate
        for candidate in snapshot.candidates
    }
    if any(key not in candidate_by_key for key in surfaced_keys):
        raise InvalidImpression("surfaced_resource_not_currently_eligible")

    batch = GlanceImpressionBatch(
        clinic_id=clinic_id,
        patient_id=patient_id,
        actor_user_id=actor_user_id,
        actor_role=actor_role,
        idempotency_key=idempotency_key,
        algorithm_version=ALGORITHM_VERSION,
        requested_limit=requested_limit,
        eligible_count=snapshot.eligible_count,
        stored_candidate_count=len(snapshot.candidates),
        surfaced_count=len(surfaced_keys),
        candidate_truncated=snapshot.candidate_truncated,
        created_at=utcnow(),
    )
    db.add(batch)
    db.flush()
    surfaced_set = set(surfaced_keys)
    for rank, candidate in enumerate(snapshot.candidates, start=1):
        db.add(
            GlanceImpressionItem(
                batch_id=batch.id,
                resource_type=candidate.resource_type,
                resource_id=candidate.resource_id,
                feature_signature=candidate.feature_signature,
                candidate_rank=rank,
                surfaced=_resource_key(candidate.resource_type, candidate.resource_id)
                in surfaced_set,
                display_priority=candidate.display_priority,
                safety_class=candidate.safety_class,
                safety_floor=candidate.safety_floor,
                created_at=batch.created_at,
            )
        )
    record_audit(
        db,
        clinic_id=clinic_id,
        patient_id=patient_id,
        actor_user_id=actor_user_id,
        actor_role=actor_role,
        action="glance_impression_recorded",
        entity_type="glance_impression_batch",
        entity_id=batch.id,
        request_id=request_id,
    )
    db.commit()
    db.refresh(batch)
    return batch


def summarize_glance_exposure(
    db: Session,
    *,
    clinic_id: str,
    patient_id: str,
) -> ExposureSummary:
    batches = list(
        db.scalars(
            select(GlanceImpressionBatch)
            .where(
                GlanceImpressionBatch.clinic_id == clinic_id,
                GlanceImpressionBatch.patient_id == patient_id,
            )
            .order_by(GlanceImpressionBatch.created_at, GlanceImpressionBatch.id)
        )
    )
    items = list(
        db.scalars(
            select(GlanceImpressionItem)
            .join(
                GlanceImpressionBatch,
                GlanceImpressionBatch.id == GlanceImpressionItem.batch_id,
            )
            .where(
                GlanceImpressionBatch.clinic_id == clinic_id,
                GlanceImpressionBatch.patient_id == patient_id,
            )
            .order_by(GlanceImpressionItem.feature_signature, GlanceImpressionItem.id)
        )
    )
    features: dict[str, dict[str, int]] = {}
    safety: dict[str, dict[str, int]] = {}
    for item in items:
        feature = features.setdefault(
            item.feature_signature,
            {"candidate": 0, "surfaced": 0, "protected": 0},
        )
        feature["candidate"] += 1
        feature["surfaced"] += int(item.surfaced)
        feature["protected"] += int(item.safety_class is not None)
        if item.safety_class is not None:
            safety_row = safety.setdefault(item.safety_class, {"candidate": 0, "surfaced": 0})
            safety_row["candidate"] += 1
            safety_row["surfaced"] += int(item.surfaced)

    feature_summaries = tuple(
        ExposureFeatureSummary(
            feature_signature=key,
            candidate_count=values["candidate"],
            surfaced_count=values["surfaced"],
            exposure_rate=round(values["surfaced"] / values["candidate"], 6)
            if values["candidate"]
            else 0.0,
            protected_count=values["protected"],
        )
        for key, values in sorted(features.items())
    )
    safety_summaries = tuple(
        ExposureSafetySummary(
            safety_class=key,
            candidate_count=values["candidate"],
            surfaced_count=values["surfaced"],
            exposure_rate=round(values["surfaced"] / values["candidate"], 6)
            if values["candidate"]
            else 0.0,
        )
        for key, values in sorted(safety.items())
    )
    return ExposureSummary(
        patient_id=patient_id,
        algorithm_versions=tuple(sorted({batch.algorithm_version for batch in batches})),
        batch_count=len(batches),
        eligible_candidate_count=sum(batch.eligible_count for batch in batches),
        candidate_item_count=len(items),
        surfaced_item_count=sum(int(item.surfaced) for item in items),
        truncated_batch_count=sum(int(batch.candidate_truncated) for batch in batches),
        feature_summaries=feature_summaries,
        safety_summaries=safety_summaries,
    )
