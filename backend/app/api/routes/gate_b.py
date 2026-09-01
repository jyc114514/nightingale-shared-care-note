"""Timeline, Glance View, provenance, trust-state, and importance endpoints."""

import json
from typing import cast

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_request_id, require_allowed_origin
from app.api.routes.patients import _current_content, _current_version
from app.db.session import get_db
from app.models import (
    Entry,
    EntryType,
    EntryVersion,
    FeedbackEventType,
    HighlightStatus,
    PatientGlanceItem,
    TaskGlanceItem,
    User,
)
from app.schemas.gate_b import (
    GlanceItemOut,
    HighlightCreate,
    HighlightFeedbackCreate,
    HighlightFeedbackOut,
    HighlightOut,
    HighlightReview,
    ImportanceProfileOut,
    ProvenanceSourceOut,
    TimelineEntryOut,
)
from app.services.authorization import (
    AccessContext,
    enum_value,
    get_patient_context,
    require_internal,
)
from app.services.highlights import (
    HighlightValidationError,
    create_highlight_record,
    get_highlight_source,
    get_source_context,
    review_highlight,
)
from app.services.importance import (
    FeedbackIdempotencyConflict,
    record_feedback_event,
)
from app.services.glance_read import build_glance_candidates, select_glance_items


router = APIRouter(tags=["gate-b"])


def timeline_entry_out(
    entry: Entry,
    current_version: EntryVersion,
    content: str,
    *,
    internal: bool,
) -> TimelineEntryOut:
    author_role = current_version.created_by_role
    author_id = current_version.created_by_user_id
    return TimelineEntryOut(
        id=entry.id,
        clinic_id=entry.clinic_id if internal else None,
        patient_id=entry.patient_id,
        entry_type=enum_value(entry.entry_type),
        owner_role=enum_value(entry.owner_role),
        author_role=str(author_role),
        author_id=author_id if internal else None,
        created_by_user_id=author_id if internal else None,
        current_version=entry.current_version,
        content=content,
        occurred_at=entry.occurred_at,
        source_kind=enum_value(entry.source_kind),
        source_reference=entry.source_reference if internal else None,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
    )


def require_clinician(context: AccessContext) -> None:
    if context.actor_role != "clinician":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only clinicians can perform this trust action",
        )


@router.get("/patients/{patient_id}/timeline", response_model=list[TimelineEntryOut])
def timeline(
    patient_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TimelineEntryOut]:
    context = get_patient_context(db, user, patient_id)
    entries = list(
        db.scalars(
            select(Entry)
            .where(Entry.patient_id == patient_id)
            .order_by(Entry.occurred_at.desc(), Entry.id.desc())
        )
    )
    result: list[TimelineEntryOut] = []
    for entry in entries:
        if context.is_patient and (
            enum_value(entry.entry_type)
            not in {
                EntryType.PATIENT_FACING_SUMMARY.value,
                EntryType.PATIENT_INSTRUCTION.value,
            }
            or enum_value(entry.visibility) != "patient_facing"
        ):
            continue
        result.append(
            timeline_entry_out(
                entry,
                _current_version(db, entry),
                _current_content(db, entry),
                internal=not context.is_patient,
            )
        )
    return result


@router.get("/patients/{patient_id}/glance", response_model=list[GlanceItemOut])
def glance(
    patient_id: str,
    limit: int = Query(default=6, ge=1, le=6),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[GlanceItemOut]:
    context = get_patient_context(db, user, patient_id)
    require_internal(context)
    snapshot = build_glance_candidates(
        db,
        clinic_id=context.clinic_id,
        patient_id=patient_id,
    )
    result: list[GlanceItemOut] = []
    for candidate in select_glance_items(snapshot, limit=limit):
        resource_type = candidate.resource_type
        item = candidate.projection
        if resource_type == "highlight":
            highlight_item = cast(PatientGlanceItem, item)
            result.append(
                GlanceItemOut(
                    id=highlight_item.highlight_id,
                    resource_type="highlight",
                    content_summary=highlight_item.content_summary,
                    feature_signature=highlight_item.feature_signature,
                    item_kind=highlight_item.item_kind,
                    status=highlight_item.status,
                    base_priority=highlight_item.base_priority,
                    recency_contribution=highlight_item.recency_contribution,
                    explicit_risk_contribution=highlight_item.explicit_risk_contribution,
                    unresolved_action_contribution=highlight_item.unresolved_action_contribution,
                    clinician_confirmation_contribution=highlight_item.clinician_confirmation_contribution,
                    adaptive_feedback_adjustment=highlight_item.adaptive_feedback_adjustment,
                    ranking_explanation=json.loads(highlight_item.ranking_explanation),
                    display_priority=highlight_item.display_priority,
                    risk_level=highlight_item.risk_level,
                    risk_reason=highlight_item.risk_reason,
                    action_label=highlight_item.action_label,
                    action_state=highlight_item.action_state,
                    clinical_conflict_id=highlight_item.clinical_conflict_id,
                    safety_class=highlight_item.safety_class,
                    safety_floor=highlight_item.safety_floor,
                    source_entry_id=highlight_item.source_entry_id,
                    source_version_id=highlight_item.source_version_id,
                    version_number=highlight_item.version_number,
                    current_entry_version=highlight_item.current_entry_version,
                    source_label=highlight_item.source_label,
                    entry_type=highlight_item.entry_type,
                    occurred_at=highlight_item.occurred_at,
                    quote=highlight_item.quote,
                )
            )
        else:
            task_item = cast(TaskGlanceItem, item)
            result.append(
                GlanceItemOut(
                    id=task_item.task_id,
                    resource_type="task",
                    task_id=task_item.task_id,
                    content_summary=task_item.content_summary,
                    feature_signature="task",
                    item_kind="action",
                    status="accepted",
                    base_priority=float(task_item.display_priority),
                    recency_contribution=0.0,
                    explicit_risk_contribution=0.0,
                    unresolved_action_contribution=0.0,
                    clinician_confirmation_contribution=0.0,
                    adaptive_feedback_adjustment=0.0,
                    ranking_explanation={"task": 1.0},
                    display_priority=float(task_item.display_priority),
                    risk_level=None,
                    risk_reason="Assigned internal task",
                    action_label=task_item.action_label,
                    action_state=task_item.action_state,
                    source_entry_id=task_item.source_entry_id,
                    source_version_id=None,
                    version_number=None,
                    current_entry_version=None,
                    source_label="Assigned task",
                    entry_type="task",
                    occurred_at=task_item.occurred_at,
                    quote=task_item.content_summary,
                    assigned_to_user_id=task_item.assigned_to_user_id,
                    assigned_to_display_name=task_item.assigned_to_display_name,
                    task_status=task_item.task_status,
                    task_version=task_item.task_version,
                )
            )
    return result


@router.get("/highlights/{highlight_id}/source", response_model=ProvenanceSourceOut)
def highlight_source(
    highlight_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProvenanceSourceOut:
    try:
        highlight, source = get_highlight_source(db, highlight_id)
    except HighlightValidationError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    context = get_patient_context(db, user, highlight.patient_id)
    require_internal(context)
    return ProvenanceSourceOut(
        highlight=HighlightOut.model_validate(highlight),
        source_entry_id=source.entry.id,
        source_version_id=source.version.id,
        version_number=source.version.version_number,
        current_entry_version=source.entry.current_version,
        entry_type=enum_value(source.entry.entry_type),
        source_kind=enum_value(source.entry.source_kind),
        source_reference=source.entry.source_reference,
        occurred_at=source.entry.occurred_at,
        version_content=source.version.content,
        quote=highlight.quote,
        start_offset=highlight.start_offset,
        end_offset=highlight.end_offset,
    )


@router.post(
    "/entry-versions/{version_id}/highlights",
    response_model=HighlightOut,
    dependencies=[Depends(require_allowed_origin)],
)
def create_highlight(
    version_id: str,
    payload: HighlightCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> HighlightOut:
    try:
        source = get_source_context(db, version_id)
    except HighlightValidationError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    context = get_patient_context(db, user, source.entry.patient_id)
    require_internal(context)
    require_clinician(context)
    try:
        highlight = create_highlight_record(
            db,
            source_version_id=version_id,
            start_offset=payload.start_offset,
            end_offset=payload.end_offset,
            quote=payload.quote,
            item_kind=payload.item_kind,
            status=HighlightStatus.ACCEPTED,
            display_priority=payload.display_priority,
            risk_level=payload.risk_level,
            risk_reason=payload.risk_reason,
            action_label=payload.action_label,
            action_state=payload.action_state,
            created_by_role=context.actor_role,
            created_by_user_id=user.id,
            reviewed_by_user_id=user.id,
            request_id=request_id,
        )
    except HighlightValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)
        ) from exc
    record_feedback_event(
        db,
        highlight=highlight,
        actor_user_id=user.id,
        actor_role=context.actor_role,
        event_type=FeedbackEventType.MANUALLY_HIGHLIGHTED,
        idempotency_key=f"manual-highlight:{request_id}",
        request_id=request_id,
    )
    return HighlightOut.model_validate(highlight)


@router.patch(
    "/highlights/{highlight_id}/review",
    response_model=HighlightOut,
    dependencies=[Depends(require_allowed_origin)],
)
def review_highlight_route(
    highlight_id: str,
    payload: HighlightReview,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> HighlightOut:
    try:
        highlight, _ = get_highlight_source(db, highlight_id)
    except HighlightValidationError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    context = get_patient_context(db, user, highlight.patient_id)
    require_internal(context)
    require_clinician(context)
    try:
        reviewed = review_highlight(
            db,
            highlight=highlight,
            status=payload.status,
            reviewer_user_id=user.id,
            request_id=request_id,
        )
    except HighlightValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)
        ) from exc
    if payload.status in {HighlightStatus.ACCEPTED, HighlightStatus.REJECTED}:
        try:
            record_feedback_event(
                db,
                highlight=reviewed,
                actor_user_id=user.id,
                actor_role=context.actor_role,
                event_type=(
                    FeedbackEventType.ACCEPTED
                    if payload.status is HighlightStatus.ACCEPTED
                    else FeedbackEventType.REJECTED
                ),
                idempotency_key=f"review:{reviewed.id}:{request_id}",
                request_id=request_id,
            )
        except FeedbackIdempotencyConflict as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return HighlightOut.model_validate(reviewed)


def require_feedback_role(actor_role: str, event_type: FeedbackEventType) -> None:
    if actor_role not in {"staff", "clinician"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff or clinicians can provide importance feedback",
        )
    clinician_only = {
        FeedbackEventType.ACCEPTED,
        FeedbackEventType.REJECTED,
        FeedbackEventType.MANUALLY_HIGHLIGHTED,
    }
    if event_type in clinician_only and actor_role != "clinician":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This importance feedback requires clinician authority",
        )


@router.post(
    "/highlights/{highlight_id}/feedback",
    response_model=HighlightFeedbackOut,
    dependencies=[Depends(require_allowed_origin)],
)
def feedback_highlight(
    highlight_id: str,
    payload: HighlightFeedbackCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> HighlightFeedbackOut:
    try:
        highlight, _ = get_highlight_source(db, highlight_id)
    except HighlightValidationError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    context = get_patient_context(db, user, highlight.patient_id)
    require_internal(context)
    require_feedback_role(context.actor_role, payload.event_type)
    try:
        result = record_feedback_event(
            db,
            highlight=highlight,
            actor_user_id=user.id,
            actor_role=context.actor_role,
            event_type=payload.event_type,
            idempotency_key=payload.idempotency_key,
            request_id=request_id,
        )
    except FeedbackIdempotencyConflict as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    projection = result.projection
    explanation = (
        json.loads(projection.ranking_explanation)
        if projection is not None
        else {
            "adaptive_feedback": result.profile.bounded_weight
            if result.profile is not None
            else 0.0
        }
    )
    return HighlightFeedbackOut(
        event_id=result.event.id,
        event_type=FeedbackEventType(result.event.event_type),
        created=result.created,
        feature_signature=result.event.feature_signature,
        profile=(
            ImportanceProfileOut.model_validate(result.profile)
            if result.profile is not None
            else None
        ),
        ranking_explanation=explanation,
        applied_to_profile=result.event.applied_to_profile,
        suppression_reason=result.event.suppression_reason,
    )
