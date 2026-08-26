"""Clinic-scoped API for the optional prerecorded synthetic voice prototype."""

from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_request_id, require_allowed_origin
from app.config import Settings, get_settings
from app.db.session import get_db
from app.models import User, VoiceSession
from app.schemas.voice import (
    TranscriptSegmentOut,
    VoiceProviderOut,
    VoiceSampleOut,
    VoiceSessionCreate,
    VoiceSessionOut,
    VoiceSampleScope,
    VoiceSessionStatus,
)
from app.services.authorization import get_patient_context
from app.services.voice import (
    VoiceAuthorizationError,
    VoiceConfigurationError,
    VoiceIdempotencyConflict,
    get_session_segments,
    get_voice_provider_info,
    process_voice_session,
    require_voice_sample,
    samples_for_context,
    session_for_user,
)
from app.voice.providers import VoiceProviderError


router = APIRouter(tags=["voice"])


def _provider_error(exc: Exception) -> HTTPException:
    if isinstance(exc, VoiceConfigurationError):
        return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=exc.error_code)
    if isinstance(exc, VoiceIdempotencyConflict):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if isinstance(exc, VoiceAuthorizationError):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="voice_processing_failed",
    )


def _session_out(
    db: Session,
    session: VoiceSession,
    *,
    patient_safe: bool,
) -> VoiceSessionOut:
    segments = get_session_segments(db, session.id)
    return VoiceSessionOut(
        id=session.id,
        clinic_id=session.clinic_id,
        patient_id=session.patient_id,
        actor_role=session.actor_role,
        interaction_type=session.interaction_type,
        sample_id=session.sample_id,
        audio_sha256=session.audio_sha256,
        audio_duration_ms=session.audio_duration_ms,
        asr_provider=session.asr_provider,
        asr_model=session.asr_model,
        language=session.language,
        language_probability=session.language_probability,
        status=cast(VoiceSessionStatus, session.status),
        error_code=session.error_code,
        entry_id=None if patient_safe else session.entry_id,
        highlight_id=None if patient_safe else session.highlight_id,
        source_segment_id=session.source_segment_id,
        created_at=session.created_at,
        completed_at=session.completed_at,
        segments=[TranscriptSegmentOut.model_validate(segment) for segment in segments],
        patient_safe=patient_safe,
    )


@router.get("/voice/provider", response_model=VoiceProviderOut)
def voice_provider_info(
    app_settings: Settings = Depends(get_settings),
) -> VoiceProviderOut:
    try:
        return VoiceProviderOut(**get_voice_provider_info(app_settings).__dict__)
    except VoiceConfigurationError as exc:
        raise _provider_error(exc) from exc


@router.get(
    "/patients/{patient_id}/voice/samples",
    response_model=list[VoiceSampleOut],
)
def list_voice_samples(
    patient_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    app_settings: Settings = Depends(get_settings),
) -> list[VoiceSampleOut]:
    context = get_patient_context(db, user, patient_id)
    try:
        provider_info = get_voice_provider_info(app_settings)
    except VoiceConfigurationError as exc:
        raise _provider_error(exc) from exc
    if not provider_info.enabled:
        return []
    return [
        VoiceSampleOut(
            sample_id=sample.sample_id,
            label=sample.label,
            scope=cast(VoiceSampleScope, sample.scope),
            interaction_type=sample.interaction_type,
            duration_ms=sample.duration_ms,
            audio_url=f"/patients/{patient_id}/voice/samples/{sample.sample_id}/audio",
            provider_disclosure=sample.provider_disclosure,
        )
        for sample in samples_for_context(context)
    ]


@router.get("/patients/{patient_id}/voice/samples/{sample_id}/audio")
def voice_sample_audio(
    patient_id: str,
    sample_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    app_settings: Settings = Depends(get_settings),
) -> FileResponse:
    context = get_patient_context(db, user, patient_id)
    try:
        get_voice_provider_info(app_settings)
        sample = require_voice_sample(context, sample_id)
    except (
        VoiceAuthorizationError,
        VoiceConfigurationError,
        VoiceProviderError,
    ) as exc:
        raise _provider_error(exc) from exc
    return FileResponse(
        sample.audio_path,
        media_type="audio/wav",
        filename=sample.audio_filename,
        headers={"Cache-Control": "no-store"},
    )


@router.post(
    "/patients/{patient_id}/voice/sessions",
    response_model=VoiceSessionOut,
    dependencies=[Depends(require_allowed_origin)],
)
def create_voice_session(
    patient_id: str,
    payload: VoiceSessionCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
    app_settings: Settings = Depends(get_settings),
) -> VoiceSessionOut:
    context = get_patient_context(db, user, patient_id)
    try:
        sample = require_voice_sample(context, payload.sample_id)
        session = process_voice_session(
            db,
            context=context,
            sample=sample,
            idempotency_key=payload.idempotency_key,
            request_id=request_id,
            app_settings=app_settings,
        )
    except (
        VoiceAuthorizationError,
        VoiceConfigurationError,
        VoiceIdempotencyConflict,
        VoiceProviderError,
    ) as exc:
        raise _provider_error(exc) from exc
    return _session_out(db, session, patient_safe=context.is_patient)


@router.get(
    "/patients/{patient_id}/voice/sessions/{session_id}",
    response_model=VoiceSessionOut,
)
def get_voice_session(
    patient_id: str,
    session_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VoiceSessionOut:
    context = get_patient_context(db, user, patient_id)
    try:
        session = session_for_user(db, context, session_id)
    except VoiceAuthorizationError as exc:
        raise _provider_error(exc) from exc
    return _session_out(db, session, patient_safe=context.is_patient)
