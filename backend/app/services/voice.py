"""Level-C synthetic voice processing with an optional local ASR adapter."""

from dataclasses import dataclass
from hashlib import sha256
import wave
from typing import cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.provider import ProviderError
from app.ai.schemas import AIInteractionType
from app.config import Settings
from app.db.base import utcnow
from app.models import TranscriptSegment, VoiceSession
from app.services.ai_processing import process_ai_job
from app.services.authorization import AccessContext
from app.services.events import append_event
from app.voice.fixtures import (
    VOICE_SCOPE_DISCLOSURE,
    VoiceSample,
    VOICE_SAMPLES,
    get_voice_sample,
)
from app.voice.providers import (
    ASRProvider,
    FasterWhisperProvider,
    FixtureTranscriptProvider,
    TranscriptResult,
    VoiceProviderError,
)


MAX_AUDIO_BYTES = 10 * 1024 * 1024
MIN_AUDIO_DURATION_MS = 20_000
MAX_AUDIO_DURATION_MS = 30_000


class VoiceAuthorizationError(ValueError):
    """Raised when a role selects a sample outside its permitted scope."""


class VoiceIdempotencyConflict(ValueError):
    """Raised when one idempotency key is reused for another sample."""


class VoiceConfigurationError(ValueError):
    """Raised when Voice is disabled or misconfigured."""

    def __init__(self, error_code: str) -> None:
        super().__init__(error_code)
        self.error_code = error_code


@dataclass(frozen=True)
class AudioMetadata:
    sha256: str
    duration_ms: int


@dataclass(frozen=True)
class VoiceProviderInfo:
    provider_name: str
    model: str
    mode: str
    enabled: bool
    disclosure: str


def is_sample_allowed(context: AccessContext, sample: VoiceSample) -> bool:
    if context.is_patient:
        return sample.scope == "patient"
    return context.actor_role in {"staff", "clinician"} and sample.scope == "clinical"


def samples_for_context(context: AccessContext) -> tuple[VoiceSample, ...]:
    return tuple(sample for sample in VOICE_SAMPLES if is_sample_allowed(context, sample))


def require_voice_sample(context: AccessContext, sample_id: str) -> VoiceSample:
    sample = get_voice_sample(sample_id)
    if sample is None or not is_sample_allowed(context, sample):
        raise VoiceAuthorizationError("voice_sample_not_allowed")
    return sample


def _voice_provider_name(settings: Settings) -> str:
    return settings.voice_provider.strip().lower()


def get_voice_provider_info(settings: Settings) -> VoiceProviderInfo:
    provider = _voice_provider_name(settings)
    if provider == "disabled":
        return VoiceProviderInfo(
            provider_name="disabled",
            model="none",
            mode="disabled",
            enabled=False,
            disclosure="Voice is disabled in this environment.",
        )
    if provider == "fixture":
        return VoiceProviderInfo(
            provider_name=FixtureTranscriptProvider.name,
            model=FixtureTranscriptProvider.model,
            mode="fixture",
            enabled=True,
            disclosure=VOICE_SCOPE_DISCLOSURE,
        )
    if provider == "local_whisper":
        return VoiceProviderInfo(
            provider_name=FasterWhisperProvider.name,
            model=settings.voice_model,
            mode="local_whisper",
            enabled=True,
            disclosure="Partial local Whisper prototype; microphone and production PHI audio are disabled.",
        )
    raise VoiceConfigurationError("voice_provider_unknown")


def get_voice_provider(settings: Settings) -> ASRProvider:
    provider = _voice_provider_name(settings)
    if provider == "fixture":
        return FixtureTranscriptProvider()
    if provider == "local_whisper":
        return FasterWhisperProvider(
            model_id=settings.voice_model,
            device=settings.voice_device,
            compute_type=settings.voice_compute_type,
            cache_dir=settings.voice_model_cache_dir,
        )
    if provider == "disabled":
        raise VoiceConfigurationError("voice_provider_disabled")
    raise VoiceConfigurationError("voice_provider_unknown")


def inspect_audio_fixture(sample: VoiceSample) -> AudioMetadata:
    path = sample.audio_path.resolve()
    root = sample.audio_path.parent.resolve()
    if not path.is_file() or not path.is_relative_to(root):
        raise VoiceProviderError("audio_fixture_missing")
    if path.suffix.lower() != ".wav":
        raise VoiceProviderError("audio_type_invalid")
    if path.stat().st_size <= 0 or path.stat().st_size > MAX_AUDIO_BYTES:
        raise VoiceProviderError("audio_size_invalid")
    try:
        with wave.open(str(path), "rb") as audio:
            frames = audio.getnframes()
            rate = audio.getframerate()
            channels = audio.getnchannels()
            sample_width = audio.getsampwidth()
    except (OSError, wave.Error) as exc:
        raise VoiceProviderError("audio_format_invalid") from exc
    if rate <= 0 or channels != 1 or sample_width not in {1, 2, 3, 4}:
        raise VoiceProviderError("audio_format_invalid")
    duration_ms = round(frames * 1000 / rate)
    if not MIN_AUDIO_DURATION_MS <= duration_ms <= MAX_AUDIO_DURATION_MS:
        raise VoiceProviderError("audio_duration_invalid")
    return AudioMetadata(
        sha256=sha256(path.read_bytes()).hexdigest(),
        duration_ms=duration_ms,
    )


def _validate_transcript(result: TranscriptResult, duration_ms: int) -> None:
    if not result.segments:
        raise VoiceProviderError("transcript_empty")
    previous_end = -1
    for expected_index, segment in enumerate(result.segments):
        if segment.segment_index != expected_index:
            raise VoiceProviderError("transcript_order_invalid")
        if (
            segment.start_ms < 0
            or segment.end_ms <= segment.start_ms
            or segment.end_ms > duration_ms
            or segment.start_ms < previous_end
            or not segment.text.strip()
        ):
            raise VoiceProviderError("transcript_timestamp_invalid")
        if segment.confidence is not None and not 0 <= segment.confidence <= 1:
            raise VoiceProviderError("transcript_confidence_invalid")
        previous_end = segment.end_ms
    if result.language_probability is not None and not 0 <= result.language_probability <= 1:
        raise VoiceProviderError("language_probability_invalid")


def _set_session_failure(
    db: Session,
    session: VoiceSession,
    *,
    status: str,
    error_code: str,
) -> VoiceSession:
    now = utcnow()
    session.status = status
    session.error_code = error_code
    session.completed_at = now
    db.commit()
    db.refresh(session)
    append_event(
        db,
        clinic_id=session.clinic_id,
        patient_id=session.patient_id,
        resource_type="voice_session",
        resource_id=session.id,
        event_kind="voice_session_failed",
        actor_user_id=session.created_by_user_id,
        actor_role=session.actor_role,
    )
    db.commit()
    return session


def _load_existing_session(
    db: Session,
    *,
    clinic_id: str,
    idempotency_key: str,
    sample_id: str,
) -> VoiceSession | None:
    existing = db.scalar(
        select(VoiceSession).where(
            VoiceSession.clinic_id == clinic_id,
            VoiceSession.idempotency_key == idempotency_key,
        )
    )
    if existing is not None and existing.sample_id != sample_id:
        raise VoiceIdempotencyConflict("voice_idempotency_key_reused_for_different_sample")
    return existing


def process_voice_session(
    db: Session,
    *,
    context: AccessContext,
    sample: VoiceSample,
    idempotency_key: str,
    request_id: str,
    app_settings: Settings,
) -> VoiceSession:
    existing = _load_existing_session(
        db,
        clinic_id=context.clinic_id,
        idempotency_key=idempotency_key,
        sample_id=sample.sample_id,
    )
    if existing is not None:
        return existing
    audio = inspect_audio_fixture(sample)
    provider = get_voice_provider(app_settings)
    session = VoiceSession(
        clinic_id=context.clinic_id,
        patient_id=context.patient.id,
        created_by_user_id=context.user.id,
        actor_role=context.actor_role,
        interaction_type=sample.interaction_type,
        sample_id=sample.sample_id,
        audio_reference=f"fixture://{sample.sample_id}",
        audio_sha256=audio.sha256,
        audio_duration_ms=audio.duration_ms,
        asr_provider=provider.name,
        asr_model=provider.model,
        language="en",
        status="processing",
        idempotency_key=idempotency_key,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    try:
        transcript = provider.transcribe(sample.audio_path, sample)
        _validate_transcript(transcript, audio.duration_ms)
    except VoiceProviderError as exc:
        return _set_session_failure(
            db,
            session,
            status="failed_asr",
            error_code=exc.error_code,
        )
    except Exception:
        return _set_session_failure(
            db,
            session,
            status="failed_asr",
            error_code="asr_inference_failed",
        )

    persisted_segments: list[TranscriptSegment] = []
    for segment in transcript.segments:
        row = TranscriptSegment(
            voice_session_id=session.id,
            segment_index=segment.segment_index,
            start_ms=segment.start_ms,
            end_ms=segment.end_ms,
            text=segment.text,
            confidence=segment.confidence,
        )
        db.add(row)
        persisted_segments.append(row)
    transcript_text = " ".join(segment.text.strip() for segment in transcript.segments)
    session.language = transcript.language
    session.language_probability = transcript.language_probability
    session.transcript_sha256 = sha256(transcript_text.encode("utf-8")).hexdigest()
    db.flush()
    session.source_segment_id = persisted_segments[0].id
    db.commit()
    db.refresh(session)

    try:
        ai_job = process_ai_job(
            db,
            patient=context.patient,
            interaction_type=cast(AIInteractionType, sample.interaction_type),
            text=transcript_text,
            source_reference=f"voice_session:{session.id}",
            idempotency_key=f"voice-ai:{session.id}",
            request_id=request_id,
            app_settings=app_settings,
        )
    except ProviderError as exc:
        return _set_session_failure(
            db,
            session,
            status="failed_provider",
            error_code=exc.error_code,
        )
    if ai_job.status != "completed":
        return _set_session_failure(
            db,
            session,
            status=ai_job.status if ai_job.status.startswith("failed_") else "failed_provider",
            error_code=ai_job.error_code or "provider_failed",
        )

    try:
        session.entry_id = ai_job.entry_id
        session.highlight_id = ai_job.highlight_id
        session.status = "completed"
        session.error_code = None
        session.completed_at = utcnow()
        db.flush()
        append_event(
            db,
            clinic_id=session.clinic_id,
            patient_id=session.patient_id,
            resource_type="voice_session",
            resource_id=session.id,
            event_kind="voice_session_completed",
            actor_user_id=session.created_by_user_id,
            actor_role=session.actor_role,
        )
        db.commit()
        db.refresh(session)
    except Exception:
        return _set_session_failure(
            db,
            session,
            status="failed_provenance",
            error_code="voice_provenance_creation_failed",
        )
    return session


def get_session_segments(db: Session, session_id: str) -> list[TranscriptSegment]:
    return list(
        db.scalars(
            select(TranscriptSegment)
            .where(TranscriptSegment.voice_session_id == session_id)
            .order_by(TranscriptSegment.segment_index)
        )
    )


def session_for_user(db: Session, context: AccessContext, session_id: str) -> VoiceSession:
    session = db.get(VoiceSession, session_id)
    if session is None or session.patient_id != context.patient.id:
        raise VoiceAuthorizationError("voice_session_not_found")
    sample = get_voice_sample(session.sample_id)
    if sample is None or not is_sample_allowed(context, sample):
        raise VoiceAuthorizationError("voice_session_not_allowed")
    return session
