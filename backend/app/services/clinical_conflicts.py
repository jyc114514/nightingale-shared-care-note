"""Deterministic allergy contradiction detection and clinician adjudication."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.db.base import utcnow
from app.models import (
    AssertionStatus,
    AssertionVerificationStatus,
    ClinicalAssertion,
    ClinicalConflict,
    ClinicalConflictResolution,
    ClinicalConflictStatus,
    ClinicalConflictType,
    Highlight,
    HighlightActionState,
    HighlightItemKind,
    HighlightStatus,
)
from app.services.entries import record_audit
from app.services.events import append_event


SAFETY_CLASS = "allergy_conflict"
CONFIRMED_SAFETY_CLASS = "confirmed_allergy"
SAFETY_FLOOR = 95.0
CONFLICT_RISK_REASON = "Conflicting allergy assertions require clinician review."
CONFIRMED_RISK_REASON = "Clinician confirmed an allergy assertion."


class ClinicalConflictConcurrencyError(Exception):
    """Raised when a clinician adjudicates an obsolete conflict version."""

    def __init__(self, conflict_id: str, expected_version: int, actual_version: int):
        super().__init__("clinical_conflict_version_stale")
        self.conflict_id = conflict_id
        self.expected_version = expected_version
        self.actual_version = actual_version


class ClinicalConflictStateError(ValueError):
    """Raised when a non-open conflict is submitted for adjudication."""


@dataclass(frozen=True)
class ConflictSyncResult:
    open_conflict_ids: tuple[str, ...]
    created_count: int
    superseded_count: int


def _comparable(assertion: ClinicalAssertion) -> bool:
    return (
        assertion.status == AssertionStatus.ACTIVE.value
        and assertion.verification_status
        not in {
            AssertionVerificationStatus.REFUTED.value,
            AssertionVerificationStatus.ENTERED_IN_ERROR.value,
        }
    )


def _pairs(
    assertions: list[ClinicalAssertion],
) -> dict[tuple[str, str], tuple[ClinicalAssertion, ClinicalAssertion]]:
    present = sorted(
        (
            assertion
            for assertion in assertions
            if _comparable(assertion)
            and assertion.domain == "allergy"
            and assertion.polarity == "present"
            and assertion.concept_key == "penicillin"
        ),
        key=lambda assertion: (assertion.source_version_id, assertion.start_offset, assertion.id),
    )
    absent = sorted(
        (
            assertion
            for assertion in assertions
            if _comparable(assertion)
            and assertion.domain == "allergy"
            and assertion.polarity == "absent"
            and assertion.concept_key in {"penicillin", "all_drug_allergies"}
        ),
        key=lambda assertion: (assertion.source_version_id, assertion.start_offset, assertion.id),
    )
    pairs: dict[tuple[str, str], tuple[ClinicalAssertion, ClinicalAssertion]] = {}
    for positive in present:
        for negative in absent:
            if positive.source_version_id == negative.source_version_id:
                continue
            pairs[(positive.id, negative.id)] = (positive, negative)
    return pairs


def _set_conflict_highlight(
    db: Session,
    *,
    conflict: ClinicalConflict,
    positive: ClinicalAssertion,
    request_id: str,
) -> Highlight:
    """Keep one protected primary span anchored to the positive assertion."""

    existing = db.scalar(select(Highlight).where(Highlight.clinical_conflict_id == conflict.id))
    if existing is not None:
        if (
            existing.source_entry_id != positive.source_entry_id
            or existing.source_version_id != positive.source_version_id
            or existing.start_offset != positive.start_offset
            or existing.end_offset != positive.end_offset
            or existing.quote != positive.quote
        ):
            raise ValueError("Clinical conflict highlight provenance is inconsistent")
        existing.status = HighlightStatus.CONFLICT_REVIEW
        existing.item_kind = HighlightItemKind.FLAG
        existing.action_state = HighlightActionState.OPEN
        existing.action_label = "Review allergy conflict"
        existing.risk_level = None
        existing.risk_reason = CONFLICT_RISK_REASON
        existing.safety_class = SAFETY_CLASS
        existing.safety_floor = SAFETY_FLOOR
        existing.updated_at = utcnow()
        from app.services.glance import sync_highlight_projection

        sync_highlight_projection(db, existing)
        return existing

    from app.services.highlights import create_highlight_record

    return create_highlight_record(
        db,
        source_version_id=positive.source_version_id,
        start_offset=positive.start_offset,
        end_offset=positive.end_offset,
        quote=positive.quote,
        item_kind=HighlightItemKind.FLAG,
        status=HighlightStatus.CONFLICT_REVIEW,
        display_priority=70.0,
        risk_level=None,
        risk_reason=CONFLICT_RISK_REASON,
        action_label="Review allergy conflict",
        action_state=HighlightActionState.OPEN,
        created_by_role="system",
        created_by_user_id=None,
        request_id=request_id,
        clinical_conflict_id=conflict.id,
        safety_class=SAFETY_CLASS,
        safety_floor=SAFETY_FLOOR,
        commit=False,
    )


def _supersede_conflict_highlight(db: Session, conflict_id: str) -> None:
    existing = db.scalar(select(Highlight).where(Highlight.clinical_conflict_id == conflict_id))
    if existing is None:
        return
    existing.status = HighlightStatus.SUPERSEDED
    existing.action_state = HighlightActionState.NOT_APPLICABLE
    existing.updated_at = utcnow()
    from app.services.glance import sync_highlight_projection

    sync_highlight_projection(db, existing)


def recompute_clinical_conflicts(
    db: Session,
    *,
    clinic_id: str,
    patient_id: str,
    request_id: str,
) -> tuple[str, ...]:
    """Reconcile active assertion pairs without deciding clinical truth."""

    assertions = list(
        db.scalars(
            select(ClinicalAssertion)
            .where(
                ClinicalAssertion.clinic_id == clinic_id,
                ClinicalAssertion.patient_id == patient_id,
                ClinicalAssertion.domain == "allergy",
            )
            .order_by(ClinicalAssertion.source_version_id, ClinicalAssertion.start_offset)
        )
    )
    active_pairs = _pairs(assertions)
    conflicts = list(
        db.scalars(
            select(ClinicalConflict).where(
                ClinicalConflict.clinic_id == clinic_id,
                ClinicalConflict.patient_id == patient_id,
            )
        )
    )
    by_pair = {
        (conflict.positive_assertion_id, conflict.negative_assertion_id): conflict
        for conflict in conflicts
    }
    open_ids: list[str] = []
    for pair, (positive, negative) in active_pairs.items():
        conflict = by_pair.get(pair)
        if conflict is None:
            conflict = ClinicalConflict(
                clinic_id=clinic_id,
                patient_id=patient_id,
                conflict_type=ClinicalConflictType.ALLERGY_ASSERTION_CONFLICT.value,
                status=ClinicalConflictStatus.OPEN.value,
                positive_assertion_id=positive.id,
                negative_assertion_id=negative.id,
                version=1,
                resolution=None,
            )
            db.add(conflict)
            db.flush()
            record_audit(
                db,
                clinic_id=clinic_id,
                patient_id=patient_id,
                actor_user_id=None,
                actor_role="system",
                action="clinical_conflict_created",
                entity_type="clinical_conflict",
                entity_id=conflict.id,
                request_id=request_id,
            )
            append_event(
                db,
                clinic_id=clinic_id,
                patient_id=patient_id,
                resource_type="clinical_conflict",
                resource_id=conflict.id,
                event_kind="clinical_conflict_created",
                actor_user_id=None,
                actor_role="system",
            )
        elif conflict.status == ClinicalConflictStatus.SUPERSEDED.value:
            conflict.status = ClinicalConflictStatus.OPEN
            conflict.resolution = None
            conflict.adjudicated_by_user_id = None
            conflict.adjudicated_at = None
            conflict.version += 1
            conflict.updated_at = utcnow()
            record_audit(
                db,
                clinic_id=clinic_id,
                patient_id=patient_id,
                actor_user_id=None,
                actor_role="system",
                action="clinical_conflict_reopened",
                entity_type="clinical_conflict",
                entity_id=conflict.id,
                request_id=request_id,
            )
        if conflict.status == ClinicalConflictStatus.OPEN.value:
            _set_conflict_highlight(
                db,
                conflict=conflict,
                positive=positive,
                request_id=request_id,
            )
            open_ids.append(conflict.id)

    active_pair_keys = set(active_pairs)
    for conflict in conflicts:
        pair = (conflict.positive_assertion_id, conflict.negative_assertion_id)
        if conflict.status == ClinicalConflictStatus.OPEN.value and pair not in active_pair_keys:
            conflict.status = ClinicalConflictStatus.SUPERSEDED
            conflict.version += 1
            conflict.updated_at = utcnow()
            _supersede_conflict_highlight(db, conflict.id)
            record_audit(
                db,
                clinic_id=clinic_id,
                patient_id=patient_id,
                actor_user_id=None,
                actor_role="system",
                action="clinical_conflict_superseded",
                entity_type="clinical_conflict",
                entity_id=conflict.id,
                request_id=request_id,
            )
            append_event(
                db,
                clinic_id=clinic_id,
                patient_id=patient_id,
                resource_type="clinical_conflict",
                resource_id=conflict.id,
                event_kind="clinical_conflict_superseded",
                actor_user_id=None,
                actor_role="system",
            )
    return tuple(open_ids)


def _transition_highlight_for_resolution(
    db: Session,
    *,
    conflict_id: str,
    resolution: ClinicalConflictResolution,
    user_id: str,
) -> None:
    rows = list(db.scalars(select(Highlight).where(Highlight.clinical_conflict_id == conflict_id)))
    now = utcnow()
    for highlight in rows:
        if resolution is ClinicalConflictResolution.CONFIRMED_PRESENT:
            highlight.status = HighlightStatus.ACCEPTED
            highlight.action_state = HighlightActionState.NOT_APPLICABLE
            highlight.action_label = "Confirmed allergy"
            highlight.safety_class = CONFIRMED_SAFETY_CLASS
            highlight.safety_floor = SAFETY_FLOOR
            highlight.risk_level = None
            highlight.risk_reason = CONFIRMED_RISK_REASON
        elif resolution is ClinicalConflictResolution.NEEDS_MORE_INFORMATION:
            highlight.status = HighlightStatus.CONFLICT_REVIEW
            highlight.action_state = HighlightActionState.OPEN
            highlight.action_label = "Review allergy conflict"
            highlight.safety_class = SAFETY_CLASS
            highlight.safety_floor = SAFETY_FLOOR
            highlight.risk_level = None
            highlight.risk_reason = CONFLICT_RISK_REASON
        else:
            highlight.status = HighlightStatus.SUPERSEDED
            highlight.action_state = HighlightActionState.NOT_APPLICABLE
        highlight.reviewed_by_user_id = user_id
        highlight.reviewed_at = now
        highlight.updated_at = now
        from app.services.glance import sync_highlight_projection

        sync_highlight_projection(db, highlight)


def adjudicate_clinical_conflict(
    db: Session,
    *,
    conflict: ClinicalConflict,
    expected_version: int,
    resolution: ClinicalConflictResolution,
    clinician_user_id: str,
    request_id: str,
) -> ClinicalConflict:
    """Apply a clinician decision with a database conditional version update."""

    now = utcnow()
    next_version = expected_version + 1
    result = db.execute(
        update(ClinicalConflict)
        .where(
            ClinicalConflict.id == conflict.id,
            ClinicalConflict.version == expected_version,
            ClinicalConflict.status == ClinicalConflictStatus.OPEN.value,
        )
        .values(
            status=(
                ClinicalConflictStatus.OPEN.value
                if resolution is ClinicalConflictResolution.NEEDS_MORE_INFORMATION
                else ClinicalConflictStatus.ADJUDICATED.value
            ),
            version=next_version,
            resolution=resolution.value,
            adjudicated_by_user_id=clinician_user_id,
            adjudicated_at=now,
            updated_at=now,
        )
        .execution_options(synchronize_session=False)
    )
    if getattr(result, "rowcount", 0) != 1:
        db.expire(conflict)
        current = db.get(ClinicalConflict, conflict.id)
        actual_version = current.version if current is not None else expected_version
        if current is not None and current.version == expected_version:
            raise ClinicalConflictStateError("Clinical conflict is not open")
        record_audit(
            db,
            clinic_id=conflict.clinic_id,
            patient_id=conflict.patient_id,
            actor_user_id=clinician_user_id,
            actor_role="clinician",
            action=f"clinical_conflict_stale_{resolution.value}",
            entity_type="clinical_conflict",
            entity_id=conflict.id,
            request_id=request_id,
            from_version=expected_version,
            to_version=actual_version,
        )
        db.commit()
        raise ClinicalConflictConcurrencyError(
            conflict.id,
            expected_version,
            actual_version,
        )

    db.refresh(conflict)
    positive = db.get(ClinicalAssertion, conflict.positive_assertion_id)
    negative = db.get(ClinicalAssertion, conflict.negative_assertion_id)
    if positive is None or negative is None:
        raise ValueError("Clinical conflict assertion source is missing")
    if resolution is ClinicalConflictResolution.CONFIRMED_PRESENT:
        positive.verification_status = AssertionVerificationStatus.CONFIRMED
        negative.verification_status = AssertionVerificationStatus.REFUTED
    elif resolution is ClinicalConflictResolution.CONFIRMED_ABSENT:
        negative.verification_status = AssertionVerificationStatus.CONFIRMED
        positive.verification_status = AssertionVerificationStatus.REFUTED
    elif resolution is ClinicalConflictResolution.ENTERED_IN_ERROR:
        positive.verification_status = AssertionVerificationStatus.ENTERED_IN_ERROR
        negative.verification_status = AssertionVerificationStatus.ENTERED_IN_ERROR
    positive.updated_at = now
    negative.updated_at = now
    _transition_highlight_for_resolution(
        db,
        conflict_id=conflict.id,
        resolution=resolution,
        user_id=clinician_user_id,
    )
    from app.services.clinical_conflicts import recompute_clinical_conflicts

    recompute_clinical_conflicts(
        db,
        clinic_id=conflict.clinic_id,
        patient_id=conflict.patient_id,
        request_id=request_id,
    )
    record_audit(
        db,
        clinic_id=conflict.clinic_id,
        patient_id=conflict.patient_id,
        actor_user_id=clinician_user_id,
        actor_role="clinician",
        action="clinical_conflict_adjudicated",
        entity_type="clinical_conflict",
        entity_id=conflict.id,
        request_id=request_id,
        from_version=expected_version,
        to_version=next_version,
    )
    append_event(
        db,
        clinic_id=conflict.clinic_id,
        patient_id=conflict.patient_id,
        resource_type="clinical_conflict",
        resource_id=conflict.id,
        event_kind="clinical_conflict_adjudicated",
        actor_user_id=clinician_user_id,
        actor_role="clinician",
    )
    db.commit()
    db.refresh(conflict)
    return conflict
