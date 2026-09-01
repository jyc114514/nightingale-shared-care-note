"""Clinic-scoped, explainable and bounded importance adaptation."""

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import utcnow
from app.models import (
    Entry,
    FeedbackEventType,
    Highlight,
    HighlightFeedbackEvent,
    ImportanceProfile,
    PatientGlanceItem,
)
from app.services.entries import enum_value, record_audit


MAX_ADAPTIVE_ADJUSTMENT = 12.0
ALLOWED_SAFETY_CLASSES = frozenset({"allergy_conflict", "confirmed_allergy"})
POSITIVE_EVENTS = frozenset(
    {
        FeedbackEventType.ACCEPTED.value,
        FeedbackEventType.PINNED.value,
        FeedbackEventType.MANUALLY_HIGHLIGHTED.value,
        FeedbackEventType.COMMENTED.value,
        FeedbackEventType.RESOLVED_AFTER_ACTION.value,
    }
)
NEGATIVE_EVENTS = frozenset({FeedbackEventType.REJECTED.value, FeedbackEventType.UNPINNED.value})
ALLOWED_FEEDBACK_EVENTS = POSITIVE_EVENTS | NEGATIVE_EVENTS


class FeedbackIdempotencyConflict(ValueError):
    """Raised when an idempotency key is reused for another feedback action."""


@dataclass(frozen=True)
class RankingBreakdown:
    feature_signature: str
    base_priority: float
    recency_contribution: float
    explicit_risk_contribution: float
    unresolved_action_contribution: float
    clinician_confirmation_contribution: float
    adaptive_feedback_adjustment: float
    pre_floor: float
    safety_class: str | None
    safety_floor: float | None
    floor_applied: bool
    final_display_priority: float

    @property
    def explanation(self) -> dict[str, float]:
        return {
            "base": self.base_priority,
            "recency": self.recency_contribution,
            "explicit_risk": self.explicit_risk_contribution,
            "unresolved_action": self.unresolved_action_contribution,
            "clinician_confirmation": self.clinician_confirmation_contribution,
            "adaptive_feedback": self.adaptive_feedback_adjustment,
            "pre_floor": self.pre_floor,
            "safety_floor": self.safety_floor or 0.0,
            "floor_applied": 1.0 if self.floor_applied else 0.0,
            "final": self.final_display_priority,
        }


@dataclass(frozen=True)
class FeedbackResult:
    event: HighlightFeedbackEvent
    profile: ImportanceProfile | None
    projection: PatientGlanceItem | None
    created: bool


def _token(value: object, *, fallback: str = "none") -> str:
    normalized = re.sub(r"[^a-z0-9_.:-]+", "_", str(value).lower()).strip("_")
    return normalized[:60] or fallback


def feature_signature(highlight: Highlight, entry: Entry) -> str:
    """Build a stable cross-patient key from structured fields only.

    Patient names, identifiers, quotes and other free text intentionally never enter
    this key.  The version prefix makes a future feature-definition change explicit.
    """

    risk = _token(highlight.risk_level) if highlight.risk_level else "none"
    action = enum_value(highlight.action_state)
    topic = "risk" if risk != "none" else "action" if action == "open" else "context"
    return "|".join(
        (
            "v1",
            f"entry_type={_token(entry.entry_type)}",
            f"item_kind={_token(highlight.item_kind)}",
            f"source_kind={_token(entry.source_kind)}",
            f"action_state={_token(action)}",
            f"risk={risk}",
            f"topic={topic}",
        )
    )


def _age_days(occurred_at: datetime) -> float:
    timestamp = occurred_at
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    return max(0.0, (utcnow() - timestamp).total_seconds() / 86400)


def _recency_contribution(occurred_at: datetime) -> float:
    age_days = _age_days(occurred_at)
    if age_days <= 7:
        return 8.0
    if age_days <= 30:
        return 4.0
    if age_days <= 90:
        return 2.0
    return 0.0


def calculate_ranking(
    highlight: Highlight,
    entry: Entry,
    *,
    adaptive_feedback_adjustment: float = 0.0,
) -> RankingBreakdown:
    """Calculate a bounded display ranking without changing clinical source fields."""

    base = float(highlight.display_priority)
    recency = _recency_contribution(entry.occurred_at)
    risk = 12.0 if highlight.risk_level else 0.0
    action = 15.0 if enum_value(highlight.action_state) == "open" else 0.0
    confirmed = (
        8.0
        if (
            enum_value(highlight.status) == "accepted"
            or highlight.created_by_role == "clinician"
            or highlight.reviewed_by_user_id is not None
        )
        else 0.0
    )
    adaptive = max(
        -MAX_ADAPTIVE_ADJUSTMENT, min(MAX_ADAPTIVE_ADJUSTMENT, adaptive_feedback_adjustment)
    )
    safety_class = getattr(highlight, "safety_class", None)
    safety_floor = getattr(highlight, "safety_floor", None)
    if safety_class is not None and safety_class not in ALLOWED_SAFETY_CLASSES:
        raise ValueError("Unsupported safety class")
    if safety_floor is not None and not 0.0 <= float(safety_floor) <= 100.0:
        raise ValueError("Safety floor must be between 0 and 100")
    if safety_class is None and safety_floor is not None:
        raise ValueError("Safety floor requires a safety class")
    pre_floor = round(base + recency + risk + action + confirmed + adaptive, 3)
    floor_applied = safety_floor is not None and pre_floor < float(safety_floor)
    floor_limited = max(pre_floor, float(safety_floor)) if safety_floor is not None else pre_floor
    final = max(
        0.0,
        min(
            100.0,
            round(floor_limited, 3),
        ),
    )
    return RankingBreakdown(
        feature_signature=feature_signature(highlight, entry),
        base_priority=base,
        recency_contribution=recency,
        explicit_risk_contribution=risk,
        unresolved_action_contribution=action,
        clinician_confirmation_contribution=confirmed,
        adaptive_feedback_adjustment=adaptive,
        pre_floor=pre_floor,
        safety_class=safety_class,
        safety_floor=float(safety_floor) if safety_floor is not None else None,
        floor_applied=floor_applied,
        final_display_priority=final,
    )


def _profile(db: Session, clinic_id: str, feature_key: str) -> ImportanceProfile | None:
    return db.scalar(
        select(ImportanceProfile).where(
            ImportanceProfile.clinic_id == clinic_id,
            ImportanceProfile.feature_key == feature_key,
        )
    )


def apply_ranking(
    db: Session,
    *,
    highlight: Highlight,
    entry: Entry,
    projection: PatientGlanceItem,
) -> RankingBreakdown:
    """Write the materialized ranking fields; callers own the transaction."""

    key = feature_signature(highlight, entry)
    profile = _profile(db, highlight.clinic_id, key)
    breakdown = calculate_ranking(
        highlight,
        entry,
        adaptive_feedback_adjustment=profile.bounded_weight if profile else 0.0,
    )
    projection.feature_signature = breakdown.feature_signature
    projection.base_priority = breakdown.base_priority
    projection.recency_contribution = breakdown.recency_contribution
    projection.explicit_risk_contribution = breakdown.explicit_risk_contribution
    projection.unresolved_action_contribution = breakdown.unresolved_action_contribution
    projection.clinician_confirmation_contribution = breakdown.clinician_confirmation_contribution
    projection.adaptive_feedback_adjustment = breakdown.adaptive_feedback_adjustment
    projection.display_priority = breakdown.final_display_priority
    projection.ranking_explanation = json.dumps(
        breakdown.explanation, sort_keys=True, separators=(",", ":")
    )
    return breakdown


def refresh_feature_projections(
    db: Session,
    *,
    clinic_id: str,
    feature_key: str,
) -> None:
    """Refresh affected materialized rows after a profile update, off the read path."""

    rows = db.execute(
        select(PatientGlanceItem, Highlight, Entry)
        .join(Highlight, Highlight.id == PatientGlanceItem.highlight_id)
        .join(Entry, Entry.id == PatientGlanceItem.source_entry_id)
        .where(
            PatientGlanceItem.clinic_id == clinic_id,
            PatientGlanceItem.feature_signature == feature_key,
        )
    )
    for projection, highlight, entry in rows:
        apply_ranking(db, highlight=highlight, entry=entry, projection=projection)
        projection.updated_at = utcnow()


def record_feedback_event(
    db: Session,
    *,
    highlight: Highlight,
    actor_user_id: str,
    actor_role: str,
    event_type: FeedbackEventType | str,
    idempotency_key: str,
    request_id: str,
) -> FeedbackResult:
    """Append one feedback event and rebuild only its clinic/feature projection."""

    event_value = enum_value(event_type)
    if event_value not in ALLOWED_FEEDBACK_EVENTS:
        raise ValueError("Unsupported feedback event type")
    existing = db.scalar(
        select(HighlightFeedbackEvent).where(
            HighlightFeedbackEvent.clinic_id == highlight.clinic_id,
            HighlightFeedbackEvent.idempotency_key == idempotency_key,
        )
    )
    source_entry = db.get(Entry, highlight.source_entry_id)
    if source_entry is None:
        raise ValueError("Highlight source entry not found")
    key = feature_signature(highlight, source_entry)
    if existing is not None:
        if existing.highlight_id != highlight.id or existing.event_type != event_value:
            raise FeedbackIdempotencyConflict("idempotency_key_reused_for_different_feedback")
        profile = _profile(db, highlight.clinic_id, key)
        if existing.applied_to_profile and profile is None:
            raise RuntimeError("Feedback profile is missing for an existing event")
        projection = db.get(PatientGlanceItem, highlight.id)
        return FeedbackResult(event=existing, profile=profile, projection=projection, created=False)

    protected = highlight.safety_class is not None
    profile = _profile(db, highlight.clinic_id, key)
    if not protected:
        if profile is None:
            profile = ImportanceProfile(clinic_id=highlight.clinic_id, feature_key=key)
            db.add(profile)
            db.flush()
        if event_value in POSITIVE_EVENTS:
            profile.positive_count += 1
        else:
            profile.negative_count += 1
        profile.bounded_weight = max(
            -MAX_ADAPTIVE_ADJUSTMENT,
            min(
                MAX_ADAPTIVE_ADJUSTMENT,
                float(profile.positive_count - profile.negative_count) * 2.0,
            ),
        )
        profile.version += 1
        profile.updated_at = utcnow()
    event = HighlightFeedbackEvent(
        clinic_id=highlight.clinic_id,
        patient_id=highlight.patient_id,
        highlight_id=highlight.id,
        actor_user_id=actor_user_id,
        actor_role=actor_role,
        event_type=event_value,
        feature_signature=key,
        idempotency_key=idempotency_key,
        applied_to_profile=not protected,
        suppression_reason="protected_safety_class" if protected else None,
    )
    db.add(event)
    db.flush()
    if not protected:
        refresh_feature_projections(db, clinic_id=highlight.clinic_id, feature_key=key)
    record_audit(
        db,
        clinic_id=highlight.clinic_id,
        patient_id=highlight.patient_id,
        actor_user_id=actor_user_id,
        actor_role=actor_role,
        action="protected_feedback_suppressed" if protected else "importance_feedback_recorded",
        entity_type="highlight_feedback_event",
        entity_id=event.id,
        request_id=request_id,
    )
    db.commit()
    db.refresh(event)
    if profile is not None:
        db.refresh(profile)
    projection = db.get(PatientGlanceItem, highlight.id)
    return FeedbackResult(event=event, profile=profile, projection=projection, created=True)
