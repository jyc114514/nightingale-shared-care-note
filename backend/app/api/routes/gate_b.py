"""Gate B timeline, Glance View, provenance, and trust-state endpoints."""

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
    HighlightActionState,
    HighlightItemKind,
    HighlightStatus,
    PatientGlanceItem,
    User,
)
from app.schemas.gate_b import (
    GlanceItemOut,
    HighlightCreate,
    HighlightOut,
    HighlightReview,
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
    rows = db.scalars(
        select(PatientGlanceItem)
        .where(
            PatientGlanceItem.patient_id == patient_id,
            PatientGlanceItem.clinic_id == context.clinic_id,
            PatientGlanceItem.status.not_in(
                [HighlightStatus.REJECTED.value, HighlightStatus.SUPERSEDED.value]
            ),
        )
        .order_by(
            PatientGlanceItem.display_priority.desc(),
            PatientGlanceItem.occurred_at.desc(),
            PatientGlanceItem.id.desc(),
        )
        .limit(limit)
    )
    return [
        GlanceItemOut(
            id=item.highlight_id,
            content_summary=item.content_summary,
            item_kind=HighlightItemKind(item.item_kind),
            status=HighlightStatus(item.status),
            display_priority=item.display_priority,
            risk_level=item.risk_level,
            risk_reason=item.risk_reason,
            action_label=item.action_label,
            action_state=HighlightActionState(item.action_state),
            source_entry_id=item.source_entry_id,
            source_version_id=item.source_version_id,
            version_number=item.version_number,
            current_entry_version=item.current_entry_version,
            source_label=item.source_label,
            entry_type=item.entry_type,
            occurred_at=item.occurred_at,
            quote=item.quote,
        )
        for item in rows
    ]


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
    return HighlightOut.model_validate(reviewed)
