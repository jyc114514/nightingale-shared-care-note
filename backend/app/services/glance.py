"""Projection maintenance for the materialized Glance read model."""

from app.db.base import utcnow
from app.models import Entry, EntryVersion, Highlight, PatientGlanceItem
from app.services.importance import apply_ranking
from app.services.entries import enum_value
from sqlalchemy.orm import Session


def source_label(entry: Entry) -> str:
    labels = {
        "doctor_consult": "AI-scribed - Doctor consult",
        "nurse_consult": "AI-scribed - Nurse consult",
        "patient_ai_session": "AI-scribed - Patient session",
        "system_event": "System event",
        "manual": "Manual note",
    }
    return labels.get(enum_value(entry.source_kind), "Care note")


def sync_highlight_projection(db: Session, highlight: Highlight) -> PatientGlanceItem:
    """Upsert one highlight without recalculating it on the read path."""

    entry = db.get(Entry, highlight.source_entry_id)
    version = db.get(EntryVersion, highlight.source_version_id)
    if entry is None or version is None or version.entry_id != entry.id:
        raise RuntimeError("Highlight source is missing from the immutable entry graph")
    projected = db.get(PatientGlanceItem, highlight.id)
    if projected is None:
        projected = PatientGlanceItem(id=highlight.id, highlight_id=highlight.id)
        db.add(projected)
    projected.clinic_id = highlight.clinic_id
    projected.patient_id = highlight.patient_id
    projected.source_entry_id = highlight.source_entry_id
    projected.source_version_id = highlight.source_version_id
    projected.start_offset = highlight.start_offset
    projected.end_offset = highlight.end_offset
    projected.quote_sha256 = highlight.quote_sha256
    projected.offset_unit = highlight.offset_unit
    projected.content_summary = highlight.quote
    projected.item_kind = enum_value(highlight.item_kind)
    projected.status = enum_value(highlight.status)
    projected.risk_level = highlight.risk_level
    projected.risk_reason = highlight.risk_reason
    projected.action_label = highlight.action_label
    projected.action_state = enum_value(highlight.action_state)
    projected.clinical_conflict_id = highlight.clinical_conflict_id
    projected.safety_class = highlight.safety_class
    projected.safety_floor = highlight.safety_floor
    projected.version_number = version.version_number
    projected.current_entry_version = entry.current_version
    projected.source_label = source_label(entry)
    projected.entry_type = enum_value(entry.entry_type)
    projected.occurred_at = entry.occurred_at
    projected.quote = highlight.quote
    apply_ranking(db, highlight=highlight, entry=entry, projection=projected)
    projected.updated_at = utcnow()
    db.flush()
    return projected
