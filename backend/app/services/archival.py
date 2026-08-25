"""Deterministic hot/warm/cold context projection with source preservation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.base import new_id, utcnow
from app.models import (
    ArchivalSummary,
    ArchivalSummarySource,
    Comment,
    Conflict,
    Entry,
    EntryVersion,
    FeedbackEventType,
    Highlight,
    HighlightStatus,
)
from app.services.entries import enum_value


POLICY_VERSION = "gate-d-v1"
GENERATED_BY = "deterministic-local-archive"
HOT_DAYS = 14
COLD_AFTER_DAYS = 90


@dataclass(frozen=True)
class ContextEntry:
    entry: Entry
    version: EntryVersion
    protection_reason: str | None


@dataclass(frozen=True)
class ContextSummary:
    summary: ArchivalSummary
    sources: tuple[ArchivalSummarySource, ...]


@dataclass(frozen=True)
class PatientContext:
    hot_entries: tuple[ContextEntry, ...]
    warm_entries: tuple[ContextEntry, ...]
    archival_summaries: tuple[ContextSummary, ...]
    refreshed_summary_count: int = 0


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _current_version(db: Session, entry: Entry) -> EntryVersion:
    version = db.scalar(
        select(EntryVersion).where(
            EntryVersion.entry_id == entry.id,
            EntryVersion.version_number == entry.current_version,
        )
    )
    if version is None:
        raise RuntimeError("Entry has no current immutable version")
    return version


def patient_visible_entry(entry: Entry) -> bool:
    return enum_value(entry.visibility) == "patient_facing" and enum_value(entry.entry_type) in {
        "patient_facing_summary",
        "patient_instruction",
    }


def _latest_pin_state(db: Session, highlight_id: str) -> bool:
    from app.models import HighlightFeedbackEvent

    latest = db.scalar(
        select(HighlightFeedbackEvent)
        .where(
            HighlightFeedbackEvent.highlight_id == highlight_id,
            HighlightFeedbackEvent.event_type.in_(
                [FeedbackEventType.PINNED.value, FeedbackEventType.UNPINNED.value]
            ),
        )
        .order_by(
            HighlightFeedbackEvent.created_at.desc(),
            HighlightFeedbackEvent.id.desc(),
        )
    )
    return latest is not None and enum_value(latest.event_type) == FeedbackEventType.PINNED.value


def protection_reason(db: Session, entry: Entry) -> str | None:
    """Return the strongest non-compression reason for one canonical entry."""

    active_conflict = db.scalar(
        select(Conflict.id).where(
            Conflict.entry_id == entry.id,
            Conflict.status == "open",
        )
    )
    if active_conflict is not None:
        return "active_conflict"

    unresolved_comment = db.scalar(
        select(Comment.id).where(
            Comment.entry_id == entry.id,
            Comment.is_resolved.is_(False),
        )
    )
    if unresolved_comment is not None:
        return "unresolved_discussion"

    highlights = list(
        db.scalars(
            select(Highlight).where(
                Highlight.source_entry_id == entry.id,
                Highlight.status.not_in(
                    [HighlightStatus.REJECTED.value, HighlightStatus.SUPERSEDED.value]
                ),
            )
        )
    )
    for highlight in highlights:
        if enum_value(highlight.action_state) == "open":
            return "open_action"
        if highlight.risk_level:
            return "explicit_risk"
        if _latest_pin_state(db, highlight.id):
            return "pinned"
        if (
            enum_value(highlight.status) == HighlightStatus.ACCEPTED.value
            or highlight.created_by_role == "clinician"
            or highlight.reviewed_by_user_id is not None
        ):
            return "clinician_confirmed"

    if enum_value(entry.entry_type) == "clinician_section":
        return "care_plan"
    return None


def _period_bounds(occurred_at: datetime) -> tuple[datetime, datetime]:
    occurred = _as_utc(occurred_at)
    start = datetime(occurred.year, occurred.month, 1, tzinfo=timezone.utc)
    if occurred.month == 12:
        end = datetime(occurred.year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime(occurred.year, occurred.month + 1, 1, tzinfo=timezone.utc)
    return start, end


def _manifest(sources: list[tuple[Entry, EntryVersion]]) -> str:
    canonical = "\n".join(
        f"{entry.id}:{version.id}:{_as_utc(entry.occurred_at).isoformat()}"
        for entry, version in sources
    )
    return sha256(canonical.encode("utf-8")).hexdigest()


def _summary_text(period_start: datetime, source_count: int) -> str:
    return (
        f"Derived historical context for {period_start.year:04d}-{period_start.month:02d}: "
        f"{source_count} source entr{'y' if source_count == 1 else 'ies'} remain canonical. "
        "Open the source pointers for the immutable detail."
    )


def _load_summary_sources(db: Session, summary_id: str) -> tuple[ArchivalSummarySource, ...]:
    return tuple(
        db.scalars(
            select(ArchivalSummarySource)
            .where(ArchivalSummarySource.archival_summary_id == summary_id)
            .order_by(ArchivalSummarySource.source_order)
        )
    )


def refresh_archival_summaries(
    db: Session,
    *,
    clinic_id: str,
    patient_id: str,
    now: datetime | None = None,
) -> PatientContext:
    """Refresh only derivative summaries; canonical entries and versions are untouched."""

    current_time = _as_utc(now or utcnow())
    hot_cutoff = current_time - timedelta(days=HOT_DAYS)
    cold_cutoff = current_time - timedelta(days=COLD_AFTER_DAYS)
    entries = list(
        db.scalars(
            select(Entry)
            .where(Entry.clinic_id == clinic_id, Entry.patient_id == patient_id)
            .order_by(Entry.occurred_at.desc(), Entry.id.desc())
        )
    )

    hot_entries: list[ContextEntry] = []
    warm_entries: list[ContextEntry] = []
    eligible: dict[tuple[datetime, datetime], list[tuple[Entry, EntryVersion]]] = {}
    for entry in entries:
        version = _current_version(db, entry)
        reason = protection_reason(db, entry)
        occurred_at = _as_utc(entry.occurred_at)
        if reason is not None or occurred_at >= hot_cutoff:
            hot_entries.append(ContextEntry(entry, version, reason))
        elif occurred_at >= cold_cutoff:
            warm_entries.append(ContextEntry(entry, version, None))
        else:
            eligible.setdefault(_period_bounds(occurred_at), []).append((entry, version))

    existing = {
        (_as_utc(summary.period_start), _as_utc(summary.period_end)): summary
        for summary in db.scalars(
            select(ArchivalSummary).where(
                ArchivalSummary.clinic_id == clinic_id,
                ArchivalSummary.patient_id == patient_id,
                ArchivalSummary.policy_version == POLICY_VERSION,
            )
        )
    }
    retained_keys = set(eligible)
    for key, existing_summary in existing.items():
        if key in retained_keys:
            continue
        db.execute(
            delete(ArchivalSummarySource).where(
                ArchivalSummarySource.archival_summary_id == existing_summary.id
            )
        )
        db.delete(existing_summary)

    for (period_start, period_end), source_entries in sorted(eligible.items()):
        archival_summary = existing.get((period_start, period_end))
        if archival_summary is None:
            archival_summary = ArchivalSummary(
                id=new_id(),
                clinic_id=clinic_id,
                patient_id=patient_id,
                period_start=period_start,
                period_end=period_end,
                summary_text="",
                source_count=0,
                source_manifest_hash="",
                generated_by=GENERATED_BY,
                policy_version=POLICY_VERSION,
            )
            db.add(archival_summary)
            db.flush()

        prior_sources = {
            source.source_entry_id: source.source_version_id
            for source in _load_summary_sources(db, archival_summary.id)
        }
        resolved_sources: list[tuple[Entry, EntryVersion]] = []
        for entry, current_version in source_entries:
            prior_version_id = prior_sources.get(entry.id)
            prior_version = db.get(EntryVersion, prior_version_id) if prior_version_id else None
            version = (
                prior_version
                if prior_version is not None and prior_version.entry_id == entry.id
                else current_version
            )
            resolved_sources.append((entry, version))

        resolved_sources.sort(key=lambda pair: (_as_utc(pair[0].occurred_at), pair[0].id))
        db.execute(
            delete(ArchivalSummarySource).where(
                ArchivalSummarySource.archival_summary_id == archival_summary.id
            )
        )
        for order, (entry, version) in enumerate(resolved_sources):
            db.add(
                ArchivalSummarySource(
                    archival_summary_id=archival_summary.id,
                    source_entry_id=entry.id,
                    source_version_id=version.id,
                    occurred_at=entry.occurred_at,
                    source_order=order,
                )
            )
        archival_summary.summary_text = _summary_text(period_start, len(resolved_sources))
        archival_summary.source_count = len(resolved_sources)
        archival_summary.source_manifest_hash = _manifest(resolved_sources)
        archival_summary.generated_by = GENERATED_BY
        archival_summary.refreshed_at = current_time
        archival_summary.policy_version = POLICY_VERSION

    db.commit()
    return build_patient_context(db, clinic_id=clinic_id, patient_id=patient_id, now=current_time)


def build_patient_context(
    db: Session,
    *,
    clinic_id: str,
    patient_id: str,
    now: datetime | None = None,
) -> PatientContext:
    """Build a read-only context response from materialized summaries and canonical records."""

    current_time = _as_utc(now or utcnow())
    hot_cutoff = current_time - timedelta(days=HOT_DAYS)
    cold_cutoff = current_time - timedelta(days=COLD_AFTER_DAYS)
    entries = list(
        db.scalars(
            select(Entry)
            .where(Entry.clinic_id == clinic_id, Entry.patient_id == patient_id)
            .order_by(Entry.occurred_at.desc(), Entry.id.desc())
        )
    )
    hot_entries: list[ContextEntry] = []
    warm_entries: list[ContextEntry] = []
    for entry in entries:
        version = _current_version(db, entry)
        reason = protection_reason(db, entry)
        occurred_at = _as_utc(entry.occurred_at)
        if reason is not None or occurred_at >= hot_cutoff:
            hot_entries.append(ContextEntry(entry, version, reason))
        elif occurred_at >= cold_cutoff:
            warm_entries.append(ContextEntry(entry, version, None))

    summaries = []
    for summary in db.scalars(
        select(ArchivalSummary)
        .where(
            ArchivalSummary.clinic_id == clinic_id,
            ArchivalSummary.patient_id == patient_id,
            ArchivalSummary.policy_version == POLICY_VERSION,
        )
        .order_by(ArchivalSummary.period_start.desc(), ArchivalSummary.id.desc())
    ):
        summaries.append(ContextSummary(summary, _load_summary_sources(db, summary.id)))
    return PatientContext(tuple(hot_entries), tuple(warm_entries), tuple(summaries))
