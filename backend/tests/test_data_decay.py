"""Real API checks for deterministic hybrid context and archival source preservation."""

from datetime import datetime, timedelta, timezone

import httpx
import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    ArchivalSummary,
    ArchivalSummarySource,
    Conflict,
    ConflictStatus,
    Entry,
    EntryOwnerRole,
    EntryType,
    EntryVersion,
    EntryVisibility,
    Highlight,
    HighlightActionState,
    HighlightItemKind,
    HighlightStatus,
)
from app.services.entries import create_entry_record
from app.services.highlights import create_highlight_record
from conftest import DemoData, TEST_PASSWORD


async def login(client: httpx.AsyncClient, email: str) -> None:
    response = await client.post("/auth/login", json={"email": email, "password": TEST_PASSWORD})
    assert response.status_code == 200, response.text


def old_entry(
    db: Session,
    demo_data: DemoData,
    *,
    content: str,
    entry_type: EntryType = EntryType.STAFF_NOTE,
    created_by_role: str = "staff",
    created_by_user_id: str | None = None,
) -> Entry:
    return create_entry_record(
        db,
        clinic_id=demo_data.clinic_a.id,
        patient_id=demo_data.patient_a.id,
        entry_type=entry_type,
        owner_role=(
            EntryOwnerRole.STAFF if entry_type is EntryType.STAFF_NOTE else EntryOwnerRole.SYSTEM
        ),
        visibility=(
            EntryVisibility.INTERNAL
            if entry_type is not EntryType.PATIENT_FACING_SUMMARY
            else EntryVisibility.PATIENT_FACING
        ),
        content=content,
        created_by_user_id=(
            created_by_user_id
            if created_by_user_id is not None or created_by_role == "system"
            else demo_data.staff_a.id
        ),
        created_by_role=created_by_role,
        request_id=f"decay-{content[:12]}",
        occurred_at=datetime.now(timezone.utc) - timedelta(days=200),
        source_kind="manual" if created_by_role != "system" else "doctor_consult",
        source_reference="synthetic-decay-source",
    )


def make_highlight(
    db: Session,
    entry: Entry,
    *,
    status: str = "suggested",
    risk: str | None = None,
    action_state: str = "not_applicable",
) -> Highlight:
    version = db.scalar(
        select(EntryVersion).where(
            EntryVersion.entry_id == entry.id,
            EntryVersion.version_number == entry.current_version,
        )
    )
    assert version is not None
    return create_highlight_record(
        db,
        source_version_id=version.id,
        start_offset=0,
        end_offset=len(version.content),
        quote=version.content,
        item_kind=HighlightItemKind.FLAG,
        status=HighlightStatus(status),
        display_priority=30,
        risk_level=risk,
        risk_reason="Synthetic archival protection fixture",
        action_label="Review synthetic item",
        action_state=HighlightActionState(action_state),
        created_by_role="system",
        created_by_user_id=None,
        request_id=f"decay-highlight-{entry.id}-{status}-{action_state}",
    )


@pytest.mark.asyncio
async def test_archival_refresh_preserves_sources_and_protection_overrides(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    eligible = old_entry(db_session, demo_data, content="Canonical old staff source")
    open_action_entry = old_entry(db_session, demo_data, content="Protected open action")
    high_risk_entry = old_entry(db_session, demo_data, content="Protected explicit risk")
    pinned_entry = old_entry(db_session, demo_data, content="Protected pinned source")
    conflict_entry = old_entry(db_session, demo_data, content="Protected active conflict")
    open_highlight = make_highlight(
        db_session, open_action_entry, action_state=HighlightActionState.OPEN.value
    )
    make_highlight(db_session, high_risk_entry, risk="high")
    pinned_highlight = make_highlight(db_session, pinned_entry)
    db_session.add(
        Conflict(
            clinic_id=demo_data.clinic_a.id,
            patient_id=demo_data.patient_a.id,
            entry_id=conflict_entry.id,
            submitted_by_user_id=demo_data.staff_a.id,
            expected_version=1,
            actual_version=2,
            attempted_content="Synthetic stale submission",
            status=ConflictStatus.OPEN,
        )
    )
    db_session.commit()
    before_entry_count = db_session.scalar(select(func.count(Entry.id)))
    before_version_count = db_session.scalar(select(func.count(EntryVersion.id)))

    await login(client, "clinician@clinic-a.test")
    pinned = await client.post(
        f"/highlights/{pinned_highlight.id}/feedback",
        json={"event_type": "pinned", "idempotency_key": "decay-pin"},
    )
    assert pinned.status_code == 200, pinned.text
    refreshed = await client.post(f"/patients/{demo_data.patient_a.id}/context/refresh")
    assert refreshed.status_code == 200, refreshed.text
    assert refreshed.json()["archival_summary_count"] >= 1

    context_response = await client.get(f"/patients/{demo_data.patient_a.id}/context")
    assert context_response.status_code == 200, context_response.text
    context = context_response.json()
    source_ids = {
        source["source_entry_id"]
        for summary in context["archival_summaries"]
        for source in summary["sources"]
    }
    assert eligible.id in source_ids
    assert open_action_entry.id not in source_ids
    assert high_risk_entry.id not in source_ids
    assert pinned_entry.id not in source_ids
    assert conflict_entry.id not in source_ids
    hot_reasons = {item["id"]: item["protection_reason"] for item in context["hot_entries"]}
    assert hot_reasons[open_action_entry.id] == "open_action"
    assert hot_reasons[high_risk_entry.id] == "explicit_risk"
    assert hot_reasons[pinned_entry.id] == "pinned"
    assert hot_reasons[conflict_entry.id] == "active_conflict"
    assert context["archival_summaries"][0]["derived"] is True
    assert "raw" not in context["archival_summaries"][0]["summary_text"].lower()

    summary_count = db_session.scalar(select(func.count(ArchivalSummary.id)))
    source_count = db_session.scalar(select(func.count(ArchivalSummarySource.source_entry_id)))
    assert db_session.scalar(select(func.count(Entry.id))) == before_entry_count
    assert db_session.scalar(select(func.count(EntryVersion.id))) == before_version_count

    eligible_version = db_session.scalar(
        select(EntryVersion).where(
            EntryVersion.entry_id == eligible.id,
            EntryVersion.version_number == 1,
        )
    )
    assert eligible_version is not None
    await login(client, "staff@clinic-a.test")
    update = await client.patch(
        f"/entries/{eligible.id}",
        json={"expected_version": 1, "new_content": "Updated but old source remains canonical"},
    )
    assert update.status_code == 200, update.text
    repeat = await client.post(f"/patients/{demo_data.patient_a.id}/context/refresh")
    assert repeat.status_code == 200, repeat.text
    assert db_session.scalar(select(func.count(ArchivalSummary.id))) == summary_count
    assert (
        db_session.scalar(select(func.count(ArchivalSummarySource.source_entry_id))) == source_count
    )
    pointer = db_session.scalar(
        select(ArchivalSummarySource).where(ArchivalSummarySource.source_entry_id == eligible.id)
    )
    assert pointer is not None
    assert pointer.source_version_id == eligible_version.id
    old_source = await client.get(f"/highlights/{open_highlight.id}/source")
    assert old_source.status_code == 200, old_source.text


@pytest.mark.asyncio
async def test_context_patient_projection_and_scope_are_server_side(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    old_public = old_entry(
        db_session,
        demo_data,
        content="Patient-safe historical instruction",
        entry_type=EntryType.PATIENT_FACING_SUMMARY,
        created_by_role="system",
        created_by_user_id=None,
    )
    old_internal = old_entry(
        db_session,
        demo_data,
        content="RAW_AI_INTERNAL_SENTINEL",
        entry_type=EntryType.AI_DOCTOR_CONSULT_SUMMARY,
        created_by_role="system",
        created_by_user_id=None,
    )
    await login(client, "staff@clinic-a.test")
    refreshed = await client.post(f"/patients/{demo_data.patient_a.id}/context/refresh")
    assert refreshed.status_code == 200, refreshed.text

    admin_login = await client.post(
        "/auth/login", json={"email": "admin@clinic-a.test", "password": TEST_PASSWORD}
    )
    assert admin_login.status_code == 200
    admin_refresh = await client.post(f"/patients/{demo_data.patient_a.id}/context/refresh")
    assert admin_refresh.status_code == 403

    patient_login = await client.post(
        "/auth/login", json={"email": "patient@clinic-a.test", "password": TEST_PASSWORD}
    )
    assert patient_login.status_code == 200
    patient_context = await client.get(f"/patients/{demo_data.patient_a.id}/context")
    assert patient_context.status_code == 200, patient_context.text
    payload = patient_context.json()
    visible_ids = {item["id"] for item in payload["hot_entries"]} | {
        source["source_entry_id"]
        for summary in payload["archival_summaries"]
        for source in summary["sources"]
    }
    assert old_public.id in visible_ids
    assert old_internal.id not in visible_ids
    assert "RAW_AI_INTERNAL_SENTINEL" not in patient_context.text
    assert all(item["content"] is not None for item in payload["hot_entries"])

    cross_clinic = await client.get(f"/patients/{demo_data.patient_b.id}/context")
    assert cross_clinic.status_code == 404
    patient_refresh = await client.post(f"/patients/{demo_data.patient_a.id}/context/refresh")
    assert patient_refresh.status_code == 403
