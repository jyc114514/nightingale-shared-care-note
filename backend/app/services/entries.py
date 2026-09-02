"""Entry persistence, immutable snapshots, audit metadata, and CAS conflicts."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models import (
    AuditLog,
    Conflict,
    ConflictStatus,
    Entry,
    EntryOwnerRole,
    EntryType,
    EntryVersion,
    EntryVisibility,
)
from app.db.base import utcnow


def enum_value(value: object) -> str:
    """Convert either a Python enum or a String-backed ORM value to text."""

    return value.value if isinstance(value, Enum) else str(value)


@dataclass(frozen=True)
class EntryConflictError(Exception):
    """Raised after preserving a stale submission as a conflict record."""

    conflict_id: str
    expected_version: int
    actual_version: int


class TargetVersionNotFound(Exception):
    """Raised when a revert points to a missing immutable version."""


def record_audit(
    db: Session,
    *,
    clinic_id: str,
    patient_id: str,
    actor_user_id: str | None,
    actor_role: str,
    action: str,
    entity_type: str,
    entity_id: str,
    request_id: str,
    from_version: int | None = None,
    to_version: int | None = None,
) -> AuditLog:
    """Record metadata only; note content never enters the audit row."""

    audit = AuditLog(
        clinic_id=clinic_id,
        patient_id=patient_id,
        actor_user_id=actor_user_id,
        actor_role=actor_role,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        request_id=request_id,
        from_version=from_version,
        to_version=to_version,
    )
    db.add(audit)
    return audit


def _sync_entry_assertions_after_commit(
    db: Session,
    *,
    entry: Entry,
    version: EntryVersion,
    request_id: str,
) -> None:
    """Run derived safety extraction only after the canonical version is durable."""

    from app.services.clinical_assertions import sync_entry_assertions_safely

    sync_entry_assertions_safely(
        db,
        entry=entry,
        version=version,
        request_id=request_id,
    )


def create_entry_record(
    db: Session,
    *,
    clinic_id: str,
    patient_id: str,
    entry_type: EntryType | str,
    owner_role: EntryOwnerRole | str,
    visibility: EntryVisibility | str,
    content: str,
    created_by_user_id: str | None,
    created_by_role: str,
    request_id: str,
    occurred_at: datetime | None = None,
    source_kind: str | None = None,
    source_reference: str | None = None,
) -> Entry:
    """Create an entry and its first immutable version in one transaction."""

    entry_type_value = enum_value(entry_type)
    if (
        entry_type_value
        in {
            EntryType.AI_DOCTOR_CONSULT_SUMMARY.value,
            EntryType.AI_NURSE_CONSULT_SUMMARY.value,
            EntryType.AI_PATIENT_SESSION_SUMMARY.value,
        }
        and not source_reference
    ):
        raise ValueError("AI-scribed entries require a non-empty source_reference")
    entry = Entry(
        clinic_id=clinic_id,
        patient_id=patient_id,
        entry_type=entry_type_value,
        owner_role=enum_value(owner_role),
        visibility=enum_value(visibility),
        current_version=1,
        created_by_user_id=created_by_user_id,
        occurred_at=occurred_at or utcnow(),
        source_kind=source_kind or ("system_event" if created_by_role == "system" else "manual"),
        source_reference=source_reference,
    )
    db.add(entry)
    db.flush()
    version = EntryVersion(
        entry_id=entry.id,
        version_number=1,
        content=content,
        created_by_user_id=created_by_user_id,
        created_by_role=created_by_role,
        base_version=0,
    )
    db.add(version)
    record_audit(
        db,
        clinic_id=clinic_id,
        patient_id=patient_id,
        actor_user_id=created_by_user_id,
        actor_role=created_by_role,
        action="entry_created",
        entity_type="entry",
        entity_id=entry.id,
        request_id=request_id,
        to_version=1,
    )
    db.commit()
    db.refresh(entry)
    _sync_entry_assertions_after_commit(
        db,
        entry=entry,
        version=version,
        request_id=request_id,
    )
    db.refresh(entry)
    return entry


def update_entry_content(
    db: Session,
    *,
    entry: Entry,
    expected_version: int,
    content: str,
    actor_user_id: str,
    actor_role: str,
    request_id: str,
    reverted_from_version: int | None = None,
) -> Entry:
    """Append a snapshot only if the caller's expected version still matches."""

    next_version = expected_version + 1
    result = db.execute(
        update(Entry)
        .where(Entry.id == entry.id, Entry.current_version == expected_version)
        .values(current_version=next_version, updated_at=utcnow())
        .execution_options(synchronize_session=False)
    )
    if getattr(result, "rowcount", 0) != 1:
        db.expire(entry)
        actual_entry = db.get(Entry, entry.id)
        actual_version = (
            actual_entry.current_version if actual_entry is not None else expected_version
        )
        conflict = Conflict(
            clinic_id=entry.clinic_id,
            patient_id=entry.patient_id,
            entry_id=entry.id,
            submitted_by_user_id=actor_user_id,
            expected_version=expected_version,
            actual_version=actual_version,
            attempted_content=content,
            status=ConflictStatus.OPEN.value,
        )
        db.add(conflict)
        db.commit()
        raise EntryConflictError(conflict.id, expected_version, actual_version)

    version = EntryVersion(
        entry_id=entry.id,
        version_number=next_version,
        content=content,
        created_by_user_id=actor_user_id,
        created_by_role=actor_role,
        base_version=expected_version,
        reverted_from_version=reverted_from_version,
    )
    db.add(version)
    record_audit(
        db,
        clinic_id=entry.clinic_id,
        patient_id=entry.patient_id,
        actor_user_id=actor_user_id,
        actor_role=actor_role,
        action="entry_reverted" if reverted_from_version is not None else "entry_updated",
        entity_type="entry",
        entity_id=entry.id,
        request_id=request_id,
        from_version=expected_version,
        to_version=next_version,
    )
    db.commit()
    db.expire(entry)
    fresh_entry = db.get(Entry, entry.id)
    if fresh_entry is None:
        raise RuntimeError("Entry disappeared after a successful update")
    fresh_version = db.scalar(
        select(EntryVersion).where(
            EntryVersion.entry_id == fresh_entry.id,
            EntryVersion.version_number == fresh_entry.current_version,
        )
    )
    if fresh_version is None:
        raise RuntimeError("Entry has no immutable version after a successful update")
    _sync_entry_assertions_after_commit(
        db,
        entry=fresh_entry,
        version=fresh_version,
        request_id=request_id,
    )
    db.refresh(fresh_entry)
    return fresh_entry


def revert_entry_content(
    db: Session,
    *,
    entry: Entry,
    target_version: int,
    expected_current_version: int,
    actor_user_id: str,
    actor_role: str,
    request_id: str,
) -> Entry:
    """Copy an earlier snapshot into a new version without deleting history."""

    target = db.scalar(
        select(EntryVersion).where(
            EntryVersion.entry_id == entry.id,
            EntryVersion.version_number == target_version,
        )
    )
    if target is None:
        raise TargetVersionNotFound()
    return update_entry_content(
        db,
        entry=entry,
        expected_version=expected_current_version,
        content=target.content,
        actor_user_id=actor_user_id,
        actor_role=actor_role,
        request_id=request_id,
        reverted_from_version=target_version,
    )
