"""Shared, provider-free Glance candidate selection for reads and impressions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models import PatientGlanceItem, TaskGlanceItem


MAX_STORED_CANDIDATES = 500
ALGORITHM_VERSION = "importance-v3-protected-first"
GlanceResourceType = Literal["highlight", "task"]
GlanceProjection = PatientGlanceItem | TaskGlanceItem


@dataclass(frozen=True)
class GlanceCandidate:
    resource_type: GlanceResourceType
    resource_id: str
    feature_signature: str
    display_priority: float
    occurred_at: datetime
    safety_class: str | None
    safety_floor: float | None
    projection: GlanceProjection


@dataclass(frozen=True)
class GlanceCandidateSnapshot:
    eligible_count: int
    candidates: tuple[GlanceCandidate, ...]
    candidate_truncated: bool


def _sort_key(candidate: GlanceCandidate) -> tuple[int, float, datetime, str]:
    """Keep active protected safety candidates ahead of ordinary ranking."""

    return (
        1 if candidate.safety_class is not None else 0,
        candidate.display_priority,
        candidate.occurred_at,
        candidate.resource_id,
    )


def build_glance_candidates(
    db: Session,
    *,
    clinic_id: str,
    patient_id: str,
) -> GlanceCandidateSnapshot:
    """Build the bounded candidate snapshot without writes or provider calls."""

    highlight_filter = (
        PatientGlanceItem.patient_id == patient_id,
        PatientGlanceItem.clinic_id == clinic_id,
        PatientGlanceItem.status.not_in(["rejected", "superseded"]),
    )
    task_filter = (
        TaskGlanceItem.patient_id == patient_id,
        TaskGlanceItem.clinic_id == clinic_id,
    )
    highlight_count = int(
        db.scalar(select(func.count(PatientGlanceItem.id)).where(*highlight_filter)) or 0
    )
    task_count = int(db.scalar(select(func.count(TaskGlanceItem.id)).where(*task_filter)) or 0)

    highlight_rows = list(
        db.scalars(
            select(PatientGlanceItem)
            .where(*highlight_filter)
            .order_by(
                case(
                    (PatientGlanceItem.safety_class.is_not(None), 1),
                    else_=0,
                ).desc(),
                PatientGlanceItem.display_priority.desc(),
                PatientGlanceItem.occurred_at.desc(),
                PatientGlanceItem.id.desc(),
            )
            .limit(MAX_STORED_CANDIDATES)
        )
    )
    task_rows = list(
        db.scalars(
            select(TaskGlanceItem)
            .where(*task_filter)
            .order_by(
                TaskGlanceItem.display_priority.desc(),
                TaskGlanceItem.occurred_at.desc(),
                TaskGlanceItem.id.desc(),
            )
            .limit(MAX_STORED_CANDIDATES)
        )
    )
    candidates = [
        GlanceCandidate(
            resource_type="highlight",
            resource_id=row.highlight_id,
            feature_signature=row.feature_signature,
            display_priority=row.display_priority,
            occurred_at=row.occurred_at,
            safety_class=row.safety_class,
            safety_floor=row.safety_floor,
            projection=row,
        )
        for row in highlight_rows
    ]
    candidates.extend(
        GlanceCandidate(
            resource_type="task",
            resource_id=row.task_id,
            feature_signature="task",
            display_priority=float(row.display_priority),
            occurred_at=row.occurred_at,
            safety_class=None,
            safety_floor=None,
            projection=row,
        )
        for row in task_rows
    )
    candidates.sort(key=_sort_key, reverse=True)
    eligible_count = highlight_count + task_count
    stored = tuple(candidates[:MAX_STORED_CANDIDATES])
    return GlanceCandidateSnapshot(
        eligible_count=eligible_count,
        candidates=stored,
        candidate_truncated=eligible_count > len(stored),
    )


def select_glance_items(
    snapshot: GlanceCandidateSnapshot,
    *,
    limit: int,
) -> tuple[GlanceCandidate, ...]:
    """Select the same deterministic protected-first top-N used by Glance and impressions."""

    if not 1 <= limit <= 6:
        raise ValueError("Glance limit must be between 1 and 6")
    return snapshot.candidates[:limit]
