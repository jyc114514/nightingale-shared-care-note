"""Read-only patient context and explicit archival refresh endpoints."""

from hashlib import sha256

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_allowed_origin
from app.db.session import get_db
from app.models import Entry, EntryVersion, User
from app.schemas.context import (
    ArchivalSummaryOut,
    ArchivalSummarySourceOut,
    ContextEntryOut,
    ContextRefreshOut,
    PatientContextOut,
    WarmContextEntryOut,
)
from app.services.archival import (
    POLICY_VERSION,
    PatientContext,
    build_patient_context,
    patient_visible_entry,
    refresh_archival_summaries,
)
from app.services.authorization import enum_value, get_patient_context, require_internal


router = APIRouter(tags=["context"])


def _entry_hash_sources(sources: list[ArchivalSummarySourceOut]) -> str:
    canonical = "\n".join(
        f"{source.source_entry_id}:{source.source_version_id}:{source.occurred_at.isoformat()}"
        for source in sources
    )
    return sha256(canonical.encode("utf-8")).hexdigest()


def _context_response(
    db: Session,
    *,
    patient_id: str,
    context: PatientContext,
    internal: bool,
) -> PatientContextOut:
    hot_entries: list[ContextEntryOut] = []
    for item in context.hot_entries:
        if not internal and not patient_visible_entry(item.entry):
            continue
        hot_entries.append(
            ContextEntryOut(
                id=item.entry.id,
                patient_id=item.entry.patient_id,
                entry_type=enum_value(item.entry.entry_type),
                owner_role=enum_value(item.entry.owner_role) if internal else "patient",
                author_role=item.version.created_by_role if internal else "system",
                current_version=item.entry.current_version,
                content=item.version.content,
                occurred_at=item.entry.occurred_at,
                source_kind=enum_value(item.entry.source_kind) if internal else "system_event",
                source_reference=item.entry.source_reference if internal else None,
                protection_reason=item.protection_reason if internal else None,
            )
        )

    warm_entries: list[WarmContextEntryOut] = []
    for item in context.warm_entries:
        if not internal and not patient_visible_entry(item.entry):
            continue
        warm_entries.append(
            WarmContextEntryOut(
                id=item.entry.id,
                patient_id=item.entry.patient_id,
                entry_type=enum_value(item.entry.entry_type),
                owner_role=enum_value(item.entry.owner_role) if internal else "patient",
                author_role=item.version.created_by_role if internal else "system",
                current_version=item.entry.current_version,
                occurred_at=item.entry.occurred_at,
                source_kind=enum_value(item.entry.source_kind) if internal else "system_event",
                protection_reason=item.protection_reason if internal else None,
            )
        )

    summaries: list[ArchivalSummaryOut] = []
    for summary_item in context.archival_summaries:
        visible_sources: list[ArchivalSummarySourceOut] = []
        for source in summary_item.sources:
            entry = db.get(Entry, source.source_entry_id)
            if entry is None or (not internal and not patient_visible_entry(entry)):
                continue
            version = db.get(EntryVersion, source.source_version_id)
            if version is None or version.entry_id != entry.id:
                continue
            visible_sources.append(
                ArchivalSummarySourceOut(
                    source_entry_id=source.source_entry_id,
                    source_version_id=source.source_version_id,
                    entry_type=enum_value(entry.entry_type),
                    version_number=version.version_number,
                    occurred_at=source.occurred_at,
                    source_order=source.source_order,
                )
            )
        if not visible_sources:
            continue
        summaries.append(
            ArchivalSummaryOut(
                id=summary_item.summary.id,
                period_start=summary_item.summary.period_start,
                period_end=summary_item.summary.period_end,
                summary_text=(
                    summary_item.summary.summary_text
                    if internal
                    else "Derived historical context; patient-facing source details remain canonical."
                ),
                source_count=(
                    summary_item.summary.source_count if internal else len(visible_sources)
                ),
                source_manifest_hash=(
                    summary_item.summary.source_manifest_hash
                    if internal
                    else _entry_hash_sources(visible_sources)
                ),
                generated_by=summary_item.summary.generated_by,
                created_at=summary_item.summary.created_at,
                refreshed_at=summary_item.summary.refreshed_at,
                policy_version=summary_item.summary.policy_version,
                sources=visible_sources,
            )
        )

    return PatientContextOut(
        patient_id=patient_id,
        policy_version=POLICY_VERSION,
        hot_entries=hot_entries,
        warm_entries=warm_entries,
        archival_summaries=summaries,
    )


@router.get("/patients/{patient_id}/context", response_model=PatientContextOut)
def get_context(
    patient_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PatientContextOut:
    access = get_patient_context(db, user, patient_id)
    context = build_patient_context(db, clinic_id=access.clinic_id, patient_id=patient_id)
    return _context_response(
        db,
        patient_id=patient_id,
        context=context,
        internal=not access.is_patient,
    )


@router.post(
    "/patients/{patient_id}/context/refresh",
    response_model=ContextRefreshOut,
    dependencies=[Depends(require_allowed_origin)],
)
def refresh_context(
    patient_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ContextRefreshOut:
    access = get_patient_context(db, user, patient_id)
    require_internal(access)
    if access.actor_role not in {"staff", "clinician"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff or clinicians can refresh derived context",
        )
    context = refresh_archival_summaries(
        db,
        clinic_id=access.clinic_id,
        patient_id=patient_id,
    )
    source_count = sum(len(summary.sources) for summary in context.archival_summaries)
    return ContextRefreshOut(
        patient_id=patient_id,
        policy_version=POLICY_VERSION,
        archival_summary_count=len(context.archival_summaries),
        archival_source_count=source_count,
    )
