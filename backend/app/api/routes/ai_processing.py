"""Authenticated local AI processing endpoint; provider work stays off Glance reads."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_request_id, require_allowed_origin
from app.db.session import get_db
from app.models import AIProcessingJob, User
from app.schemas.ai import AIJobOut, AIProcessingRequest
from app.services.ai_processing import AIIdempotencyConflict, process_ai_job
from app.services.authorization import get_patient_context, require_internal


router = APIRouter(tags=["ai-processing"])


def require_processing_role(actor_role: str) -> None:
    if actor_role not in {"staff", "clinician"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff or clinicians can submit synthetic AI processing",
        )


@router.post(
    "/patients/{patient_id}/ai-processing",
    response_model=AIJobOut,
    dependencies=[Depends(require_allowed_origin)],
)
def submit_ai_processing(
    patient_id: str,
    payload: AIProcessingRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> AIJobOut:
    context = get_patient_context(db, user, patient_id)
    require_internal(context)
    require_processing_role(context.actor_role)
    try:
        job = process_ai_job(
            db,
            patient=context.patient,
            interaction_type=payload.interaction_type,
            text=payload.text,
            source_reference=payload.source_reference,
            idempotency_key=payload.idempotency_key,
            request_id=request_id,
        )
    except AIIdempotencyConflict as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return AIJobOut.model_validate(job)


@router.get("/ai-processing/{job_id}", response_model=AIJobOut)
def get_ai_processing(
    job_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AIJobOut:
    job = db.get(AIProcessingJob, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI job not found")
    context = get_patient_context(db, user, job.patient_id)
    require_internal(context)
    return AIJobOut.model_validate(job)
