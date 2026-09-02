"""Strict immutable-version provenance and Glance item persistence."""

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import utcnow
from app.models import (
    Entry,
    EntryVersion,
    Highlight,
    HighlightActionState,
    HighlightItemKind,
    HighlightStatus,
)
from app.services.entries import enum_value, record_audit
from app.services.glance import sync_highlight_projection


class HighlightValidationError(Exception):
    """Raised when a highlight cannot be resolved to an exact immutable span."""


@dataclass(frozen=True)
class SourceContext:
    entry: Entry
    version: EntryVersion


def get_source_context(db: Session, source_version_id: str) -> SourceContext:
    row = db.execute(
        select(Entry, EntryVersion)
        .join(EntryVersion, EntryVersion.entry_id == Entry.id)
        .where(EntryVersion.id == source_version_id)
    ).one_or_none()
    if row is None:
        raise HighlightValidationError("Source version not found")
    entry, version = row
    return SourceContext(entry=entry, version=version)


def get_highlight_source(db: Session, highlight_id: str) -> tuple[Highlight, SourceContext]:
    highlight = db.get(Highlight, highlight_id)
    if highlight is None:
        raise HighlightValidationError("Highlight not found")
    source = get_source_context(db, highlight.source_version_id)
    if (
        source.entry.id != highlight.source_entry_id
        or source.entry.patient_id != highlight.patient_id
        or source.entry.clinic_id != highlight.clinic_id
    ):
        raise HighlightValidationError("Highlight provenance is inconsistent")
    validate_span(
        source.version.content, highlight.start_offset, highlight.end_offset, highlight.quote
    )
    expected_hash = sha256(highlight.quote.encode("utf-8")).hexdigest()
    if highlight.quote_sha256 != expected_hash:
        raise HighlightValidationError("Highlight quote hash is inconsistent")
    if highlight.offset_unit != "unicode_codepoint":
        raise HighlightValidationError("Unsupported highlight offset unit")
    return highlight, source


def validate_span(content: str, start_offset: int, end_offset: int, quote: str) -> None:
    """Validate Python Unicode-codepoint offsets and exact quoted content."""

    if start_offset < 0 or end_offset <= start_offset or end_offset > len(content):
        raise HighlightValidationError("Highlight offsets are outside the immutable content")
    if content[start_offset:end_offset] != quote:
        raise HighlightValidationError("Highlight quote does not match the immutable content slice")


def create_highlight_record(
    db: Session,
    *,
    source_version_id: str,
    start_offset: int,
    end_offset: int,
    quote: str,
    item_kind: HighlightItemKind | str,
    status: HighlightStatus | str,
    display_priority: float,
    risk_level: str | None,
    risk_reason: str,
    action_label: str | None,
    action_state: HighlightActionState | str,
    created_by_role: str,
    created_by_user_id: str | None,
    request_id: str,
    reviewed_by_user_id: str | None = None,
    reviewed_at: datetime | None = None,
    clinical_conflict_id: str | None = None,
    safety_class: str | None = None,
    safety_floor: float | None = None,
    commit: bool = True,
) -> Highlight:
    source = get_source_context(db, source_version_id)
    validate_span(source.version.content, start_offset, end_offset, quote)
    if safety_floor is not None and not 0.0 <= safety_floor <= 100.0:
        raise ValueError("Safety floor must be between 0 and 100")
    if safety_class is None and safety_floor is not None:
        raise ValueError("Safety floor requires a safety class")
    highlight = Highlight(
        clinic_id=source.entry.clinic_id,
        patient_id=source.entry.patient_id,
        source_entry_id=source.entry.id,
        source_version_id=source.version.id,
        start_offset=start_offset,
        end_offset=end_offset,
        quote=quote,
        quote_sha256=sha256(quote.encode("utf-8")).hexdigest(),
        offset_unit="unicode_codepoint",
        item_kind=enum_value(item_kind),
        status=enum_value(status),
        display_priority=display_priority,
        risk_level=risk_level,
        risk_reason=risk_reason,
        action_label=action_label,
        action_state=enum_value(action_state),
        clinical_conflict_id=clinical_conflict_id,
        safety_class=safety_class,
        safety_floor=safety_floor,
        created_by_user_id=created_by_user_id,
        created_by_role=created_by_role,
        reviewed_by_user_id=reviewed_by_user_id,
        reviewed_at=reviewed_at or (utcnow() if reviewed_by_user_id else None),
    )
    db.add(highlight)
    db.flush()
    sync_highlight_projection(db, highlight)
    record_audit(
        db,
        clinic_id=highlight.clinic_id,
        patient_id=highlight.patient_id,
        actor_user_id=created_by_user_id,
        actor_role=created_by_role,
        action="highlight_created",
        entity_type="highlight",
        entity_id=highlight.id,
        request_id=request_id,
    )
    if commit:
        db.commit()
        db.refresh(highlight)
    return highlight


def review_highlight(
    db: Session,
    *,
    highlight: Highlight,
    status: HighlightStatus,
    reviewer_user_id: str,
    request_id: str,
) -> Highlight:
    if status is HighlightStatus.SUGGESTED:
        raise HighlightValidationError("Review status must be a human decision")
    if highlight.clinical_conflict_id is not None:
        raise HighlightValidationError("Clinical conflicts require adjudication")
    if highlight.safety_class is not None:
        raise HighlightValidationError("Protected safety highlights require adjudication")
    reviewed_at = utcnow()
    highlight.status = status.value
    highlight.reviewed_by_user_id = reviewer_user_id
    highlight.reviewed_at = reviewed_at
    highlight.updated_at = reviewed_at
    sync_highlight_projection(db, highlight)
    record_audit(
        db,
        clinic_id=highlight.clinic_id,
        patient_id=highlight.patient_id,
        actor_user_id=reviewer_user_id,
        actor_role="clinician",
        action=f"highlight_{status.value}",
        entity_type="highlight",
        entity_id=highlight.id,
        request_id=request_id,
    )
    db.commit()
    db.refresh(highlight)
    return highlight
