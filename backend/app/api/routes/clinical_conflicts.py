"""Clinic-scoped allergy conflict inspection and clinician adjudication APIs."""

from typing import Literal, cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_request_id, require_allowed_origin
from app.db.session import get_db
from app.models import (
    ClinicalAssertion,
    ClinicalConflict,
    ClinicalConflictResolution,
    User,
)
from app.schemas.clinical import (
    ClinicalAssertionOut,
    ClinicalConflictAdjudication,
    ClinicalConflictOut,
)
from app.services.authorization import (
    AccessContext,
    enum_value,
    get_patient_context,
    require_internal,
)
from app.services.clinical_conflicts import (
    ClinicalConflictConcurrencyError,
    ClinicalConflictStateError,
    adjudicate_clinical_conflict,
)


router = APIRouter(tags=["clinical-safety"])


def _require_clinician(context: AccessContext) -> None:
    if context.actor_role != "clinician":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only clinicians can adjudicate clinical conflicts",
        )


def _get_scoped_conflict(
    db: Session,
    *,
    user: User,
    conflict_id: str,
) -> tuple[AccessContext, ClinicalConflict]:
    conflict = db.get(ClinicalConflict, conflict_id)
    if conflict is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Clinical conflict not found"
        )
    context = get_patient_context(db, user, conflict.patient_id)
    require_internal(context)
    if conflict.clinic_id != context.clinic_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Clinical conflict not found"
        )
    return context, conflict


def clinical_conflict_out(db: Session, conflict: ClinicalConflict) -> ClinicalConflictOut:
    positive = db.get(ClinicalAssertion, conflict.positive_assertion_id)
    negative = db.get(ClinicalAssertion, conflict.negative_assertion_id)
    if positive is None or negative is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical conflict provenance is incomplete",
        )
    return ClinicalConflictOut(
        id=conflict.id,
        clinic_id=conflict.clinic_id,
        patient_id=conflict.patient_id,
        conflict_type=cast(
            Literal["allergy_assertion_conflict"], enum_value(conflict.conflict_type)
        ),
        status=cast(Literal["open", "adjudicated", "superseded"], enum_value(conflict.status)),
        positive_assertion_id=conflict.positive_assertion_id,
        negative_assertion_id=conflict.negative_assertion_id,
        version=conflict.version,
        resolution=cast(
            Literal[
                "confirmed_present",
                "confirmed_absent",
                "needs_more_information",
                "entered_in_error",
            ]
            | None,
            enum_value(conflict.resolution) if conflict.resolution is not None else None,
        ),
        adjudicated_by_user_id=conflict.adjudicated_by_user_id,
        adjudicated_at=conflict.adjudicated_at,
        created_at=conflict.created_at,
        updated_at=conflict.updated_at,
        positive_assertion=ClinicalAssertionOut.model_validate(positive),
        negative_assertion=ClinicalAssertionOut.model_validate(negative),
    )


@router.get(
    "/patients/{patient_id}/clinical-conflicts",
    response_model=list[ClinicalConflictOut],
)
def list_clinical_conflicts(
    patient_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ClinicalConflictOut]:
    context = get_patient_context(db, user, patient_id)
    require_internal(context)
    conflicts = list(
        db.scalars(
            select(ClinicalConflict)
            .where(
                ClinicalConflict.patient_id == patient_id,
                ClinicalConflict.clinic_id == context.clinic_id,
            )
            .order_by(ClinicalConflict.created_at, ClinicalConflict.id)
        )
    )
    return [clinical_conflict_out(db, conflict) for conflict in conflicts]


@router.get("/clinical-conflicts/{conflict_id}", response_model=ClinicalConflictOut)
def get_clinical_conflict(
    conflict_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ClinicalConflictOut:
    _, conflict = _get_scoped_conflict(db, user=user, conflict_id=conflict_id)
    return clinical_conflict_out(db, conflict)


@router.patch(
    "/clinical-conflicts/{conflict_id}/adjudicate",
    response_model=ClinicalConflictOut,
    dependencies=[Depends(require_allowed_origin)],
)
def adjudicate_clinical_conflict_route(
    conflict_id: str,
    payload: ClinicalConflictAdjudication,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> ClinicalConflictOut:
    context, conflict = _get_scoped_conflict(db, user=user, conflict_id=conflict_id)
    _require_clinician(context)
    resolution = ClinicalConflictResolution(payload.resolution)
    try:
        adjudicated = adjudicate_clinical_conflict(
            db,
            conflict=conflict,
            expected_version=payload.expected_version,
            resolution=resolution,
            clinician_user_id=user.id,
            request_id=request_id,
        )
    except ClinicalConflictConcurrencyError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Clinical conflict version is stale",
                "conflict_id": exc.conflict_id,
                "expected_version": exc.expected_version,
                "actual_version": exc.actual_version,
                "attempted_resolution": payload.resolution,
            },
        ) from exc
    except ClinicalConflictStateError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    return clinical_conflict_out(db, adjudicated)
