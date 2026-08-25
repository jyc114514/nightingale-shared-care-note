"""Synchronous local AI write path with redaction and idempotency."""

import hashlib
import json

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.provider import AIProvider, get_provider
from app.ai.redaction import RedactionFailure, redact_text
from app.ai.schemas import AIInteractionType, ProviderOutput, RedactedPayload
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
from app.services.highlights import create_highlight_record


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
    del error
    return fallback


def _set_failed(
    db: Session,
    job: AIProcessingJob,
    *,
    status: str,
    error_code: str,
) -> AIProcessingJob:
    now = utcnow()
    job.status = status
    job.error_code = error_code
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
) -> AIProcessingJob:
    """Process one redacted request and create only a new suggested source."""

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

    safe_source_reference = "redaction-failed"
    try:
        known_names = _known_names(db, patient)
        redacted = redact_text(text, known_names)
        redacted_reference = redact_text(source_reference, known_names)
        safe_source_reference = redacted_reference.redacted_text[:200]
    except RedactionFailure as exc:
        job = AIProcessingJob(
            clinic_id=patient.clinic_id,
            patient_id=patient.id,
            interaction_type=interaction_type,
            provider_name="fixture-redacted-v1",
            status="failed_redaction",
            idempotency_key=idempotency_key,
            input_hash=input_hash,
            source_reference=safe_source_reference,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return _set_failed(
            db,
            job,
            status="failed_redaction",
            error_code=exc.error_code,
        )

    job = AIProcessingJob(
        clinic_id=patient.clinic_id,
        patient_id=patient.id,
        interaction_type=interaction_type,
        provider_name="fixture-redacted-v1",
        status="processing",
        idempotency_key=idempotency_key,
        input_hash=input_hash,
        source_reference=safe_source_reference,
        redacted_payload=_safe_payload(
            interaction_type=interaction_type,
            redacted_text=redacted.redacted_text,
            source_reference=safe_source_reference,
            replacement_counts=redacted.replacement_counts,
        ),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    provider_instance = provider or get_provider()
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
        return _set_failed(
            db,
            job,
            status="failed_provider",
            error_code="provider_output_invalid",
        )
    except Exception as exc:
        return _set_failed(
            db,
            job,
            status="failed_provider",
            error_code=_safe_error_code(exc, "provider_unavailable"),
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
        return _set_failed(
            db,
            job,
            status="failed_provenance",
            error_code="provenance_creation_failed",
        )

    job.entry_id = entry.id
    job.highlight_id = highlight.id
    job.status = "completed"
    job.error_code = None
    now = utcnow()
    job.updated_at = now
    job.completed_at = now
    db.commit()
    db.refresh(job)
    return job
