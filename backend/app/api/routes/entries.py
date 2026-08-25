"""Entry reads, role-derived creates, immutable revisions, diffs, and reverts."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_request_id, require_allowed_origin
from app.api.routes.patients import _current_content, internal_entry_out, patient_entry_out
from app.db.session import get_db
from app.models import Entry, EntryVersion, User
from app.schemas.entry import (
    DiffOut,
    EntryCreate,
    EntryUpdate,
    InternalEntryOut,
    PatientEntryOut,
    RevertRequest,
    VersionOut,
)
from app.services.authorization import (
    AccessContext,
    authorize_entry_create,
    authorize_entry_write,
    authorize_patient_read,
    get_entry_context,
    get_patient_context,
    require_internal,
)
from app.services.entries import (
    EntryConflictError,
    TargetVersionNotFound,
    revert_entry_content,
    update_entry_content,
    create_entry_record,
)


router = APIRouter(tags=["entries"])
EntryRead = InternalEntryOut | PatientEntryOut


def entry_response(
    db: Session,
    context: AccessContext,
    entry: Entry,
) -> EntryRead:
    content = _current_content(db, entry)
    if context.is_patient:
        authorize_patient_read(context, entry)
        return patient_entry_out(entry, content)
    return internal_entry_out(entry, content)


def conflict_http_error(exc: EntryConflictError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "message": "The entry changed before this write was applied",
            "conflict_id": exc.conflict_id,
            "expected_version": exc.expected_version,
            "actual_version": exc.actual_version,
        },
    )


@router.post(
    "/patients/{patient_id}/entries",
    response_model=InternalEntryOut,
    dependencies=[Depends(require_allowed_origin)],
)
def create_entry(
    patient_id: str,
    payload: EntryCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> InternalEntryOut:
    context = get_patient_context(db, user, patient_id)
    owner_role, visibility = authorize_entry_create(context, payload.entry_type)
    entry = create_entry_record(
        db,
        clinic_id=context.clinic_id,
        patient_id=patient_id,
        entry_type=payload.entry_type,
        owner_role=owner_role,
        visibility=visibility,
        content=payload.content,
        created_by_user_id=user.id,
        created_by_role=context.actor_role,
        request_id=request_id,
    )
    return internal_entry_out(entry, payload.content)


@router.get("/entries/{entry_id}", response_model=EntryRead)
def get_entry(
    entry_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EntryRead:
    context, entry = get_entry_context(db, user, entry_id)
    return entry_response(db, context, entry)


@router.patch(
    "/entries/{entry_id}",
    response_model=InternalEntryOut,
    dependencies=[Depends(require_allowed_origin)],
)
def update_entry(
    entry_id: str,
    payload: EntryUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> InternalEntryOut:
    context, entry = get_entry_context(db, user, entry_id)
    authorize_entry_write(context, entry)
    try:
        updated = update_entry_content(
            db,
            entry=entry,
            expected_version=payload.expected_version,
            content=payload.new_content,
            actor_user_id=user.id,
            actor_role=context.actor_role,
            request_id=request_id,
        )
    except EntryConflictError as exc:
        raise conflict_http_error(exc) from exc
    return internal_entry_out(updated, payload.new_content)


@router.get("/entries/{entry_id}/versions", response_model=list[VersionOut])
def list_versions(
    entry_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[VersionOut]:
    context, _ = get_entry_context(db, user, entry_id)
    require_internal(context)
    versions = list(
        db.scalars(
            select(EntryVersion)
            .where(EntryVersion.entry_id == entry_id)
            .order_by(EntryVersion.version_number)
        )
    )
    return [VersionOut.model_validate(version) for version in versions]


@router.get("/entries/{entry_id}/diff", response_model=DiffOut)
def diff_entry(
    entry_id: str,
    from_version: int = Query(ge=1),
    to_version: int = Query(ge=1),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DiffOut:
    context, _ = get_entry_context(db, user, entry_id)
    require_internal(context)
    versions = list(
        db.scalars(
            select(EntryVersion).where(
                EntryVersion.entry_id == entry_id,
                EntryVersion.version_number.in_([from_version, to_version]),
            )
        )
    )
    by_number = {version.version_number: version for version in versions}
    if from_version not in by_number or to_version not in by_number:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")
    return DiffOut(
        entry_id=entry_id,
        from_version=from_version,
        to_version=to_version,
        from_content=by_number[from_version].content,
        to_content=by_number[to_version].content,
        changed=by_number[from_version].content != by_number[to_version].content,
    )


@router.post(
    "/entries/{entry_id}/revert",
    response_model=InternalEntryOut,
    dependencies=[Depends(require_allowed_origin)],
)
def revert_entry(
    entry_id: str,
    payload: RevertRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> InternalEntryOut:
    context, entry = get_entry_context(db, user, entry_id)
    authorize_entry_write(context, entry)
    try:
        reverted = revert_entry_content(
            db,
            entry=entry,
            target_version=payload.target_version,
            expected_current_version=payload.expected_current_version,
            actor_user_id=user.id,
            actor_role=context.actor_role,
            request_id=request_id,
        )
    except TargetVersionNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Version not found"
        ) from exc
    except EntryConflictError as exc:
        raise conflict_http_error(exc) from exc
    return internal_entry_out(reverted, _current_content(db, reverted))
