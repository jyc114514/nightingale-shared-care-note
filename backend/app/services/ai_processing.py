"""Synchronous local AI write path with redaction and idempotency."""

import hashlib
import json
import logging
import time

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.provider import AIProvider, ProviderError, get_provider
from app.ai.redaction import RedactionFailure, redact_text
from app.ai.schemas import AIInteractionType, ProviderOutput, RedactedPayload
from app.config import Settings, settings as runtime_settings
from app.db.base import utcnow
from app.models import (
    AIProcessingJob,
    EntryOwnerRole,
    EntryType,
    EntryVisibility,
    EntryVersion,
    ClinicMembership,
    HighlightStatus,
    Patient,
    User,
)
from app.services.entries import create_entry_record
from app.services.events import append_event
from app.services.highlights import create_highlight_record
from app.observability.safe_logging import safe_event
from app.observability.safe_logging import SAFE_ERROR_CODES
from app.services.provider_resilience import (
    acquire_provider_permission,
    is_external_provider,
    record_provider_failure,
    record_provider_success,
    normalize_provider_error,
)


_LOGGER = logging.getLogger("nightingale")


class AIIdempotencyConflict(ValueError):
    """Raised when an idempotency key is reused for different input."""


def _input_hash(
    interaction_type: AIInteractionType,
    text: str,
    source_reference: str,
) -> str:
    canonical = "\x00".join((interaction_type, text, source_reference))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _safe_error_code(error: Exception, fallback: str) -> str:
    if isinstance(error, ProviderError):
        return normalize_provider_error(error.error_code)
    if isinstance(error, ValueError) and error.args and error.args[0] == "provider_span_invalid":
        return "provider_span_invalid"
    return normalize_provider_error(fallback)


def _safe_redaction_error(error_code: str) -> str:
    return (
        error_code
        if error_code in {"empty_input", "secondary_detector_failed", "sensitive_token_remaining"}
        and error_code in SAFE_ERROR_CODES
        else "sensitive_token_remaining"
    )


def _selected_provider_name(app_settings: Settings | None) -> str:
    selected = (app_settings.llm_provider if app_settings else None) or "fixture"
    if selected.strip().lower() == "deepseek":
        return "deepseek-v4-flash"
    if selected.strip().lower() == "fixture":
        return "fixture-redacted-v1"
    return "unconfigured-provider"


def _provider_attempt_count(provider: AIProvider) -> int:
    value = getattr(provider, "last_attempt_count", 1)
    return value if isinstance(value, int) and 1 <= value <= 3 else 1


def _duration_ms(started: float) -> float:
    return round(max(0.0, (time.monotonic() - started) * 1000), 3)


def _close_provider(provider: AIProvider) -> None:
    close = getattr(provider, "close", None)
    if not callable(close):
        return
    try:
        close()
    except Exception:
        # A client cleanup failure must not change the persisted job result.
        return


def _set_failed(
    db: Session,
    job: AIProcessingJob,
    *,
    status: str,
    error_code: str,
    retry_after_seconds: float | None = None,
) -> AIProcessingJob:
    now = utcnow()
    job.status = status
    job.error_code = error_code
    job.retry_after_seconds = retry_after_seconds
    job.updated_at = now
    job.completed_at = now
    db.commit()
    db.refresh(job)
    return job


def _known_names(db: Session, patient: Patient) -> list[str]:
    """Return only synthetic names deliberately supplied to the fixture redactor."""

    staff_names = list(
        db.scalars(
            select(User.display_name)
            .join(ClinicMembership, ClinicMembership.user_id == User.id)
            .where(ClinicMembership.clinic_id == patient.clinic_id)
        )
    )
    return [patient.synthetic_display_name, *staff_names]


def _safe_payload(
    *,
    interaction_type: str,
    redacted_text: str,
    source_reference: str,
    replacement_counts: dict[str, int],
) -> str:
    return json.dumps(
        {
            "interaction_type": interaction_type,
            "redacted_text": redacted_text,
            "source_reference": source_reference,
            "replacement_categories": sorted(
                category for category, count in replacement_counts.items() if count
            ),
        },
        sort_keys=True,
        ensure_ascii=True,
    )


def _validate_span(output: ProviderOutput) -> None:
    codepoints = list(output.summary)
    if (
        output.end_offset <= output.start_offset
        or output.end_offset > len(codepoints)
        or "".join(codepoints[output.start_offset : output.end_offset]) != output.quote
    ):
        raise ValueError("provider_span_invalid")


def process_ai_job(
    db: Session,
    *,
    patient: Patient,
    interaction_type: AIInteractionType,
    text: str,
    source_reference: str,
    idempotency_key: str,
    request_id: str,
    provider: AIProvider | None = None,
    app_settings: Settings | None = None,
) -> AIProcessingJob:
    """Process one redacted request and create only a new suggested source."""

    effective_settings = app_settings or runtime_settings
    input_hash = _input_hash(interaction_type, text, source_reference)
    existing = db.scalar(
        select(AIProcessingJob).where(
            AIProcessingJob.clinic_id == patient.clinic_id,
            AIProcessingJob.idempotency_key == idempotency_key,
        )
    )
    if existing is not None:
        if existing.input_hash != input_hash:
            raise AIIdempotencyConflict("idempotency_key_reused_for_different_input")
        return existing

    provider_name = (
        provider.name if provider is not None else _selected_provider_name(effective_settings)
    )
    job = AIProcessingJob(
        clinic_id=patient.clinic_id,
        patient_id=patient.id,
        interaction_type=interaction_type,
        provider_name=provider_name,
        status="processing",
        idempotency_key=idempotency_key,
        input_hash=input_hash,
        source_reference="pending",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    safe_event(
        _LOGGER,
        "ai_job_created",
        request_id=request_id,
        clinic_id=patient.clinic_id,
        patient_id=patient.id,
        entity_type="ai_processing_job",
        entity_id=job.id,
        provider_name=provider_name,
        status="processing",
        input_hash=input_hash,
    )

    try:
        known_names = _known_names(db, patient)
        redacted = redact_text(text, known_names)
        redacted_reference = redact_text(source_reference, known_names)
        safe_source_reference = redacted_reference.redacted_text[:200]
    except RedactionFailure as exc:
        error_code = _safe_redaction_error(exc.error_code)
        job.source_reference = "redaction-failed"
        db.commit()
        safe_event(
            _LOGGER,
            "ai_redaction_failed",
            request_id=request_id,
            clinic_id=patient.clinic_id,
            patient_id=patient.id,
            entity_type="ai_processing_job",
            entity_id=job.id,
            provider_name=provider_name,
            status="failed_redaction",
            error_code=error_code,
        )
        return _set_failed(
            db,
            job,
            status="failed_redaction",
            error_code=error_code,
        )

    job.source_reference = safe_source_reference
    job.redacted_payload = _safe_payload(
        interaction_type=interaction_type,
        redacted_text=redacted.redacted_text,
        source_reference=safe_source_reference,
        replacement_counts=redacted.replacement_counts,
    )
    db.commit()
    db.refresh(job)
    replacement_categories = ",".join(
        sorted(category for category, count in redacted.replacement_counts.items() if count)
    )
    safe_event(
        _LOGGER,
        "ai_redaction_completed",
        request_id=request_id,
        clinic_id=patient.clinic_id,
        patient_id=patient.id,
        entity_type="ai_processing_job",
        entity_id=job.id,
        provider_name=provider_name,
        status="redacted",
        input_hash=input_hash,
        replacement_categories=replacement_categories or None,
        replacement_count=sum(redacted.replacement_counts.values()),
    )

    try:
        provider_instance = provider or get_provider(effective_settings)
        provider_name = provider_instance.name
        if provider_name != job.provider_name:
            job.provider_name = provider_name
            db.commit()
    except ProviderError as exc:
        error_code = _safe_error_code(exc, "provider_unavailable")
        safe_event(
            _LOGGER,
            "ai_provider_failed",
            request_id=request_id,
            clinic_id=patient.clinic_id,
            patient_id=patient.id,
            entity_type="ai_processing_job",
            entity_id=job.id,
            provider_name=provider_name,
            status="failed_provider",
            error_code=error_code,
        )
        return _set_failed(db, job, status="failed_provider", error_code=error_code)
    except Exception:
        error_code = "provider_unavailable"
        safe_event(
            _LOGGER,
            "ai_provider_failed",
            request_id=request_id,
            clinic_id=patient.clinic_id,
            patient_id=patient.id,
            entity_type="ai_processing_job",
            entity_id=job.id,
            provider_name=provider_name,
            status="failed_provider",
            error_code=error_code,
        )
        return _set_failed(db, job, status="failed_provider", error_code=error_code)

    permission = acquire_provider_permission(
        db,
        clinic_id=patient.clinic_id,
        provider_name=provider_name,
        app_settings=effective_settings,
        request_id=request_id,
    )
    if not permission.allowed:
        _close_provider(provider_instance)
        return _set_failed(
            db,
            job,
            status="failed_provider",
            error_code="provider_circuit_open",
            retry_after_seconds=permission.retry_after_seconds,
        )

    safe_event(
        _LOGGER,
        "ai_provider_call_started",
        request_id=request_id,
        clinic_id=patient.clinic_id,
        patient_id=patient.id,
        entity_type="ai_processing_job",
        entity_id=job.id,
        provider_name=provider_name,
        status="started",
        retry_count=0,
    )
    call_started = time.monotonic()
    try:
        payload = RedactedPayload(
            interaction_type=interaction_type,
            redacted_text=redacted.redacted_text,
            source_reference=safe_source_reference,
        )
        raw_output = provider_instance.process(payload)
        output = ProviderOutput.model_validate(raw_output)
        _validate_span(output)
    except ValidationError:
        _close_provider(provider_instance)
        if is_external_provider(provider_name):
            record_provider_failure(
                db,
                clinic_id=patient.clinic_id,
                provider_name=provider_name,
                error_code="provider_output_invalid",
                app_settings=effective_settings,
                request_id=request_id,
            )
        safe_event(
            _LOGGER,
            "ai_provider_failed",
            request_id=request_id,
            clinic_id=patient.clinic_id,
            patient_id=patient.id,
            entity_type="ai_processing_job",
            entity_id=job.id,
            provider_name=provider_name,
            status="failed_provider",
            error_code="provider_output_invalid",
            duration_ms=_duration_ms(call_started),
            retry_count=max(_provider_attempt_count(provider_instance) - 1, 0),
        )
        return _set_failed(
            db,
            job,
            status="failed_provider",
            error_code="provider_output_invalid",
        )
    except Exception as exc:
        _close_provider(provider_instance)
        error_code = _safe_error_code(exc, "provider_unavailable")
        if is_external_provider(provider_name):
            record_provider_failure(
                db,
                clinic_id=patient.clinic_id,
                provider_name=provider_name,
                error_code=error_code,
                app_settings=effective_settings,
                request_id=request_id,
            )
        safe_event(
            _LOGGER,
            "ai_provider_failed",
            request_id=request_id,
            clinic_id=patient.clinic_id,
            patient_id=patient.id,
            entity_type="ai_processing_job",
            entity_id=job.id,
            provider_name=provider_name,
            status="failed_provider",
            error_code=error_code,
            duration_ms=_duration_ms(call_started),
            retry_count=max(_provider_attempt_count(provider_instance) - 1, 0),
        )
        return _set_failed(
            db,
            job,
            status="failed_provider",
            error_code=error_code,
        )

    if is_external_provider(provider_name):
        record_provider_success(
            db,
            clinic_id=patient.clinic_id,
            provider_name=provider_name,
            app_settings=effective_settings,
            request_id=request_id,
        )
    safe_event(
        _LOGGER,
        "ai_provider_call_completed",
        request_id=request_id,
        clinic_id=patient.clinic_id,
        patient_id=patient.id,
        entity_type="ai_processing_job",
        entity_id=job.id,
        provider_name=provider_name,
        status="completed",
        duration_ms=_duration_ms(call_started),
        retry_count=max(_provider_attempt_count(provider_instance) - 1, 0),
    )

    try:
        entry_type = EntryType(interaction_type)
        source_kind = {
            EntryType.AI_DOCTOR_CONSULT_SUMMARY: "doctor_consult",
            EntryType.AI_NURSE_CONSULT_SUMMARY: "nurse_consult",
            EntryType.AI_PATIENT_SESSION_SUMMARY: "patient_ai_session",
        }[entry_type]
        entry = create_entry_record(
            db,
            clinic_id=patient.clinic_id,
            patient_id=patient.id,
            entry_type=entry_type,
            owner_role=EntryOwnerRole.SYSTEM,
            visibility=EntryVisibility.INTERNAL,
            content=output.summary,
            created_by_user_id=None,
            created_by_role="system",
            request_id=request_id,
            source_kind=source_kind,
            source_reference=safe_source_reference,
        )
        highlight = create_highlight_record(
            db,
            source_version_id=db.scalar(
                select(EntryVersion.id).where(EntryVersion.entry_id == entry.id)
            )
            or "",
            start_offset=output.start_offset,
            end_offset=output.end_offset,
            quote=output.quote,
            item_kind=output.item_kind,
            status=HighlightStatus.SUGGESTED,
            display_priority=60,
            risk_level=output.risk_level,
            risk_reason=output.risk_reason,
            action_label=output.action_label,
            action_state=output.action_state,
            created_by_role="system",
            created_by_user_id=None,
            request_id=request_id,
        )
    except Exception:
        _close_provider(provider_instance)
        safe_event(
            _LOGGER,
            "ai_provenance_failed",
            request_id=request_id,
            clinic_id=patient.clinic_id,
            patient_id=patient.id,
            entity_type="ai_processing_job",
            entity_id=job.id,
            provider_name=provider_name,
            status="failed_provenance",
            error_code="provenance_creation_failed",
        )
        return _set_failed(
            db,
            job,
            status="failed_provenance",
            error_code="provenance_creation_failed",
        )

    job.entry_id = entry.id
    job.highlight_id = highlight.id
    append_event(
        db,
        clinic_id=patient.clinic_id,
        patient_id=patient.id,
        resource_type="ai_processing",
        resource_id=job.id,
        event_kind="ai_processing_completed",
        actor_user_id=None,
        actor_role="system",
    )
    job.status = "completed"
    job.error_code = None
    job.retry_after_seconds = None
    now = utcnow()
    job.updated_at = now
    job.completed_at = now
    db.commit()
    db.refresh(job)
    safe_event(
        _LOGGER,
        "ai_provenance_completed",
        request_id=request_id,
        clinic_id=patient.clinic_id,
        patient_id=patient.id,
        entity_type="ai_processing_job",
        entity_id=job.id,
        provider_name=provider_name,
        status="completed",
    )
    _close_provider(provider_instance)
    return job
