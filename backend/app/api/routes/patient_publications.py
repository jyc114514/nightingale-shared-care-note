"""Explicit clinician publication gate and patient-safe publication projection."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_request_id, require_allowed_origin
from app.db.session import get_db
from app.models import PatientPublication, User
from app.schemas.patient_publication import (
    PatientCareOut,
    PatientPublicationCreate,
    PatientPublicationOut,
    PatientPublicationRecall,
    PatientPublicationTransition,
    PatientPublicationUpdate,
)
from app.services.authorization import (
    AccessContext,
    get_entry_context,
    get_patient_context,
    require_internal,
)
from app.services.patient_publications import (
    PublicationConflictError,
    PublicationError,
    PublicationSourceChangedError,
    approve_publication,
    create_correction_draft,
    create_publication_draft,
    edit_publication_draft,
    list_publications,
    patient_care_projection,
    publication_detail,
    publish_publication,
    recall_publication,
)


router = APIRouter(tags=["patient-publications"])


def _require_staff_or_clinician(context: AccessContext) -> None:
    if context.actor_role not in {"staff", "clinician"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff or clinicians can prepare a patient update",
        )


def _require_clinician(context: AccessContext) -> None:
    if context.actor_role != "clinician":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only clinicians can approve, publish, or withdraw a patient update",
        )


def _publication_context(
    db: Session, user: User, publication_id: str
) -> tuple[AccessContext, PatientPublication]:
    publication = db.get(PatientPublication, publication_id)
    if publication is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")
    context = get_patient_context(db, user, publication.patient_id)
    require_internal(context)
    if publication.clinic_id != context.clinic_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")
    return context, publication


def _publication_error(exc: Exception) -> HTTPException:
    if isinstance(exc, PublicationConflictError):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "The publication changed before this workflow action was applied",
                "publication_id": exc.publication_id,
                "expected_workflow_version": exc.expected_workflow_version,
                "actual_workflow_version": exc.actual_workflow_version,
            },
        )
    if isinstance(exc, PublicationSourceChangedError):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "The source changed; review the latest immutable source before continuing",
                "source_changed": True,
            },
        )
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail=str(exc),
    )


@router.post(
    "/entries/{source_entry_id}/patient-publications",
    response_model=PatientPublicationOut,
    dependencies=[Depends(require_allowed_origin)],
)
def create_patient_publication(
    source_entry_id: str,
    payload: PatientPublicationCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> PatientPublicationOut:
    context, entry = get_entry_context(db, user, source_entry_id)
    require_internal(context)
    _require_staff_or_clinician(context)
    try:
        publication = create_publication_draft(
            db,
            clinic_id=context.clinic_id,
            patient_id=entry.patient_id,
            source_entry_id=entry.id,
            actor=user,
            actor_role=context.actor_role,
            request_id=request_id,
            content=payload.content,
        )
        return publication_detail(db, publication)
    except PublicationError as exc:
        raise _publication_error(exc) from exc


@router.get(
    "/patients/{patient_id}/patient-publications",
    response_model=list[PatientPublicationOut],
)
def list_patient_publications(
    patient_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[PatientPublicationOut]:
    context = get_patient_context(db, user, patient_id)
    require_internal(context)
    return [
        publication_detail(db, publication)
        for publication in list_publications(db, clinic_id=context.clinic_id, patient_id=patient_id)
    ]


@router.get(
    "/patient-publications/{publication_id}",
    response_model=PatientPublicationOut,
)
def get_patient_publication(
    publication_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PatientPublicationOut:
    _, publication = _publication_context(db, user, publication_id)
    try:
        return publication_detail(db, publication)
    except PublicationError as exc:
        raise _publication_error(exc) from exc


@router.patch(
    "/patient-publications/{publication_id}",
    response_model=PatientPublicationOut,
    dependencies=[Depends(require_allowed_origin)],
)
def update_patient_publication(
    publication_id: str,
    payload: PatientPublicationUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> PatientPublicationOut:
    context, publication = _publication_context(db, user, publication_id)
    _require_staff_or_clinician(context)
    try:
        updated = edit_publication_draft(
            db,
            publication=publication,
            content=payload.content,
            actor=user,
            actor_role=context.actor_role,
            expected_workflow_version=payload.expected_workflow_version,
            request_id=request_id,
        )
        return publication_detail(db, updated)
    except PublicationError as exc:
        raise _publication_error(exc) from exc


@router.post(
    "/patient-publications/{publication_id}/approve",
    response_model=PatientPublicationOut,
    dependencies=[Depends(require_allowed_origin)],
)
def approve_patient_publication(
    publication_id: str,
    payload: PatientPublicationTransition,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> PatientPublicationOut:
    context, publication = _publication_context(db, user, publication_id)
    _require_clinician(context)
    try:
        approved = approve_publication(
            db,
            publication=publication,
            actor=user,
            actor_role=context.actor_role,
            expected_workflow_version=payload.expected_workflow_version,
            request_id=request_id,
        )
        return publication_detail(db, approved)
    except PublicationError as exc:
        raise _publication_error(exc) from exc


@router.post(
    "/patient-publications/{publication_id}/publish",
    response_model=PatientPublicationOut,
    dependencies=[Depends(require_allowed_origin)],
)
def publish_patient_publication(
    publication_id: str,
    payload: PatientPublicationTransition,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> PatientPublicationOut:
    context, publication = _publication_context(db, user, publication_id)
    _require_clinician(context)
    try:
        published = publish_publication(
            db,
            publication=publication,
            actor=user,
            actor_role=context.actor_role,
            expected_workflow_version=payload.expected_workflow_version,
            request_id=request_id,
        )
        return publication_detail(db, published)
    except PublicationError as exc:
        raise _publication_error(exc) from exc


@router.post(
    "/patient-publications/{publication_id}/recall",
    response_model=PatientPublicationOut,
    dependencies=[Depends(require_allowed_origin)],
)
def recall_patient_publication(
    publication_id: str,
    payload: PatientPublicationRecall,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> PatientPublicationOut:
    context, publication = _publication_context(db, user, publication_id)
    _require_clinician(context)
    try:
        recalled = recall_publication(
            db,
            publication=publication,
            actor=user,
            actor_role=context.actor_role,
            expected_workflow_version=payload.expected_workflow_version,
            reason_code=payload.reason_code,
            request_id=request_id,
        )
        return publication_detail(db, recalled)
    except PublicationError as exc:
        raise _publication_error(exc) from exc


@router.post(
    "/patient-publications/{publication_id}/corrections",
    response_model=PatientPublicationOut,
    dependencies=[Depends(require_allowed_origin)],
)
def correct_patient_publication(
    publication_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> PatientPublicationOut:
    context, publication = _publication_context(db, user, publication_id)
    _require_clinician(context)
    try:
        correction = create_correction_draft(
            db,
            publication=publication,
            actor=user,
            actor_role=context.actor_role,
            request_id=request_id,
        )
        return publication_detail(db, correction)
    except PublicationError as exc:
        raise _publication_error(exc) from exc


@router.get(
    "/patients/{patient_id}/published-care",
    response_model=PatientCareOut,
)
def published_care(
    patient_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PatientCareOut:
    get_patient_context(db, user, patient_id)
    return patient_care_projection(db, patient_id=patient_id)
