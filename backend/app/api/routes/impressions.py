"""Internal Glance exposure telemetry APIs."""

from typing import Literal, cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_request_id, require_allowed_origin
from app.db.session import get_db
from app.models import GlanceImpressionBatch, GlanceImpressionItem, User
from app.schemas.impressions import (
    ExposureFeatureSummaryOut,
    ExposureSafetySummaryOut,
    GlanceImpressionBatchOut,
    GlanceImpressionCreate,
    GlanceImpressionItemOut,
    GlanceExposureSummaryOut,
)
from app.services.authorization import get_patient_context, require_internal
from app.services.glance_read import build_glance_candidates
from app.services.impressions import (
    ImpressionPayloadConflict,
    InvalidImpression,
    create_glance_impression,
    impression_batch_items,
    summarize_glance_exposure,
)


router = APIRouter(tags=["glance-telemetry"])


def _item_out(item: GlanceImpressionItem) -> GlanceImpressionItemOut:
    return GlanceImpressionItemOut(
        id=item.id,
        resource_type=cast(Literal["highlight", "task"], item.resource_type),
        resource_id=item.resource_id,
        feature_signature=item.feature_signature,
        candidate_rank=item.candidate_rank,
        surfaced=item.surfaced,
        display_priority=item.display_priority,
        safety_class=item.safety_class,
        safety_floor=item.safety_floor,
        created_at=item.created_at,
    )


def _batch_out(db: Session, batch: GlanceImpressionBatch) -> GlanceImpressionBatchOut:
    return GlanceImpressionBatchOut(
        id=batch.id,
        clinic_id=batch.clinic_id,
        patient_id=batch.patient_id,
        actor_user_id=batch.actor_user_id,
        actor_role=batch.actor_role,
        idempotency_key=batch.idempotency_key,
        algorithm_version=batch.algorithm_version,
        requested_limit=batch.requested_limit,
        eligible_count=batch.eligible_count,
        stored_candidate_count=batch.stored_candidate_count,
        surfaced_count=batch.surfaced_count,
        candidate_truncated=batch.candidate_truncated,
        created_at=batch.created_at,
        items=[_item_out(item) for item in impression_batch_items(db, batch.id)],
    )


@router.post(
    "/patients/{patient_id}/glance-impressions",
    response_model=GlanceImpressionBatchOut,
    dependencies=[Depends(require_allowed_origin)],
)
def record_glance_impression(
    patient_id: str,
    payload: GlanceImpressionCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> GlanceImpressionBatchOut:
    context = get_patient_context(db, user, patient_id)
    require_internal(context)
    snapshot = build_glance_candidates(
        db,
        clinic_id=context.clinic_id,
        patient_id=patient_id,
    )
    surfaced_items = [(item.resource_type, item.resource_id) for item in payload.surfaced_items]
    try:
        batch = create_glance_impression(
            db,
            clinic_id=context.clinic_id,
            patient_id=patient_id,
            actor_user_id=user.id,
            actor_role=context.actor_role,
            idempotency_key=payload.idempotency_key,
            requested_limit=payload.requested_limit,
            surfaced_items=surfaced_items,
            snapshot=snapshot,
            request_id=request_id,
        )
    except ImpressionPayloadConflict as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except InvalidImpression as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    return _batch_out(db, batch)


@router.get(
    "/patients/{patient_id}/glance-impressions/summary",
    response_model=GlanceExposureSummaryOut,
)
def glance_exposure_summary(
    patient_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GlanceExposureSummaryOut:
    context = get_patient_context(db, user, patient_id)
    require_internal(context)
    summary = summarize_glance_exposure(
        db,
        clinic_id=context.clinic_id,
        patient_id=patient_id,
    )
    return GlanceExposureSummaryOut(
        patient_id=summary.patient_id,
        algorithm_versions=list(summary.algorithm_versions),
        batch_count=summary.batch_count,
        eligible_candidate_count=summary.eligible_candidate_count,
        candidate_item_count=summary.candidate_item_count,
        surfaced_item_count=summary.surfaced_item_count,
        truncated_batch_count=summary.truncated_batch_count,
        feature_summaries=[
            ExposureFeatureSummaryOut(
                feature_signature=item.feature_signature,
                candidate_count=item.candidate_count,
                surfaced_count=item.surfaced_count,
                exposure_rate=item.exposure_rate,
                protected_count=item.protected_count,
            )
            for item in summary.feature_summaries
        ],
        safety_summaries=[
            ExposureSafetySummaryOut(
                safety_class=item.safety_class,
                candidate_count=item.candidate_count,
                surfaced_count=item.surfaced_count,
                exposure_rate=item.exposure_rate,
            )
            for item in summary.safety_summaries
        ],
    )
