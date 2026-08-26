"""Gate B API checks for timeline, Glance, comments, trust, and browser boundaries."""

from datetime import datetime, timezone
from typing import cast

import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings
from app.models import Entry, EntryVersion
from conftest import DemoData, TEST_PASSWORD


async def login(client: httpx.AsyncClient, email: str) -> None:
    response = await client.post("/auth/login", json={"email": email, "password": TEST_PASSWORD})
    assert response.status_code == 200, response.text


def version_id(db_session: Session, entry_id: str) -> str:
    version = db_session.scalar(
        select(EntryVersion).where(
            EntryVersion.entry_id == entry_id,
            EntryVersion.version_number == 1,
        )
    )
    assert version is not None
    return version.id


async def create_highlight(
    client: httpx.AsyncClient,
    db_session: Session,
    entry: Entry,
    *,
    display_priority: float,
    risk_level: str | None,
    quote: str | None = None,
) -> str:
    content = cast(
        str | None,
        db_session.scalar(
            select(EntryVersion.content).where(
                EntryVersion.entry_id == entry.id,
                EntryVersion.version_number == 1,
            )
        ),
    )
    assert content is not None
    selected_quote = quote or content
    start = content.index(selected_quote)
    response = await client.post(
        f"/entry-versions/{version_id(db_session, entry.id)}/highlights",
        json={
            "start_offset": start,
            "end_offset": start + len(selected_quote),
            "quote": selected_quote,
            "item_kind": "action",
            "display_priority": display_priority,
            "risk_level": risk_level,
            "risk_reason": "Synthetic Glance reason",
            "action_label": "Review synthetic item",
            "action_state": "open",
        },
    )
    assert response.status_code == 200, response.text
    return cast(str, response.json()["id"])


@pytest.mark.asyncio
async def test_timeline_is_occurred_at_descending_and_ai_sources_are_explicit(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    ordered = [
        (demo_data.staff_note, datetime(2026, 8, 25, tzinfo=timezone.utc)),
        (demo_data.ai_nurse, datetime(2026, 8, 24, tzinfo=timezone.utc)),
        (demo_data.ai_summary, datetime(2026, 8, 20, tzinfo=timezone.utc)),
        (demo_data.ai_doctor, datetime(2026, 2, 6, tzinfo=timezone.utc)),
    ]
    for entry, occurred_at in ordered:
        entry.occurred_at = occurred_at
    db_session.commit()

    await login(client, "staff@clinic-a.test")
    response = await client.get(f"/patients/{demo_data.patient_a.id}/timeline")
    assert response.status_code == 200, response.text
    entries = response.json()
    assert entries == sorted(
        entries,
        key=lambda entry: (entry["occurred_at"], entry["id"]),
        reverse=True,
    )
    ai_entries = {
        entry["entry_type"]: entry for entry in entries if entry["entry_type"].startswith("ai_")
    }
    assert set(ai_entries) == {
        "ai_doctor_consult_summary",
        "ai_nurse_consult_summary",
        "ai_patient_session_summary",
    }
    assert {entry["source_kind"] for entry in ai_entries.values()} == {
        "doctor_consult",
        "nurse_consult",
        "patient_ai_session",
    }
    assert all(entry["source_reference"] for entry in ai_entries.values())
    assert (
        next(entry for entry in entries if entry["entry_type"] == "patient_facing_summary")[
            "owner_role"
        ]
        == "patient"
    )
    assert (
        next(entry for entry in entries if entry["entry_type"] == "patient_facing_summary")[
            "author_role"
        ]
        == "system"
    )
    assert (
        next(entry for entry in entries if entry["entry_type"] == "patient_facing_summary")[
            "author_id"
        ]
        is None
    )
    assert ai_entries["ai_doctor_consult_summary"]["owner_role"] == "system"
    assert ai_entries["ai_doctor_consult_summary"]["author_role"] == "system"
    assert ai_entries["ai_doctor_consult_summary"]["author_id"] is None
    assert (
        next(entry for entry in entries if entry["entry_type"] == "staff_note")["author_id"]
        == demo_data.staff_a.id
    )


@pytest.mark.asyncio
async def test_glance_has_six_item_cap_deterministic_priority_and_separate_risk(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    await login(client, "clinician@clinic-a.test")
    entries = [
        demo_data.patient_summary,
        demo_data.patient_instruction,
        demo_data.staff_note,
        demo_data.clinician_section,
        demo_data.ai_summary,
        demo_data.ai_doctor,
        demo_data.ai_nurse,
    ]
    highlight_ids = []
    for index, entry in enumerate(entries):
        highlight_ids.append(
            await create_highlight(
                client,
                db_session,
                entry,
                display_priority=10 + index,
                risk_level="high" if index == 0 else "low",
            )
        )
    glance = await client.get(f"/patients/{demo_data.patient_a.id}/glance")
    assert glance.status_code == 200, glance.text
    items = glance.json()
    assert len(items) == 6
    assert items == sorted(
        items,
        key=lambda item: (item["display_priority"], item["occurred_at"], item["id"]),
        reverse=True,
    )
    assert items[0]["base_priority"] == 16
    assert items[0]["display_priority"] > items[0]["base_priority"]
    assert items[0]["ranking_explanation"]["final"] == items[0]["display_priority"]
    assert items[0]["risk_level"] == "low"
    assert all(
        item["version_number"] >= 1 and item["current_entry_version"] >= item["version_number"]
        for item in items
    )
    assert highlight_ids[0] not in {item["id"] for item in items}


@pytest.mark.asyncio
async def test_rejected_and_superseded_items_leave_glance_but_keep_source(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    await login(client, "clinician@clinic-a.test")
    rejected_id = await create_highlight(
        client,
        db_session,
        demo_data.ai_doctor,
        display_priority=95,
        risk_level="high",
    )
    superseded_id = await create_highlight(
        client,
        db_session,
        demo_data.ai_nurse,
        display_priority=94,
        risk_level="medium",
    )
    rejected = await client.patch(f"/highlights/{rejected_id}/review", json={"status": "rejected"})
    superseded = await client.patch(
        f"/highlights/{superseded_id}/review", json={"status": "superseded"}
    )
    assert rejected.status_code == 200, rejected.text
    assert superseded.status_code == 200, superseded.text
    glance = await client.get(f"/patients/{demo_data.patient_a.id}/glance")
    assert glance.status_code == 200, glance.text
    visible_ids = {item["id"] for item in glance.json()}
    assert rejected_id not in visible_ids
    assert superseded_id not in visible_ids
    assert (await client.get(f"/highlights/{rejected_id}/source")).status_code == 200
    assert (await client.get(f"/highlights/{superseded_id}/source")).status_code == 200


@pytest.mark.asyncio
async def test_threaded_comments_resolution_and_patient_denial(
    client: httpx.AsyncClient,
    demo_data: DemoData,
) -> None:
    await login(client, "staff@clinic-a.test")
    root = await client.post(
        f"/entries/{demo_data.staff_note.id}/comments",
        json={"body": "Synthetic root comment"},
    )
    assert root.status_code == 200, root.text
    reply = await client.post(
        f"/entries/{demo_data.staff_note.id}/comments",
        json={
            "body": "Synthetic threaded reply",
            "parent_comment_id": root.json()["id"],
        },
    )
    assert reply.status_code == 200, reply.text
    assert reply.json()["parent_comment_id"] == root.json()["id"]
    listed = await client.get(f"/entries/{demo_data.staff_note.id}/comments")
    assert listed.status_code == 200
    assert {comment["body"] for comment in listed.json()} >= {
        "Synthetic root comment",
        "Synthetic threaded reply",
    }
    resolved = await client.patch(
        f"/comments/{root.json()['id']}/resolution", json={"is_resolved": True}
    )
    assert resolved.status_code == 200, resolved.text
    assert resolved.json()["is_resolved"] is True
    assert resolved.json()["resolved_by_user_id"]
    unresolved = await client.patch(
        f"/comments/{root.json()['id']}/resolution", json={"is_resolved": False}
    )
    assert unresolved.status_code == 200
    assert unresolved.json()["resolved_at"] is None

    await login(client, "patient@clinic-a.test")
    patient_read = await client.get(f"/entries/{demo_data.staff_note.id}/comments")
    patient_write = await client.post(
        f"/entries/{demo_data.staff_note.id}/comments", json={"body": "forbidden"}
    )
    assert patient_read.status_code == 403
    assert patient_write.status_code == 403


@pytest.mark.asyncio
async def test_foreign_origin_is_rejected_for_cookie_authenticated_writes(
    client: httpx.AsyncClient,
    demo_data: DemoData,
) -> None:
    await login(client, "staff@clinic-a.test")
    foreign = await client.post(
        f"/entries/{demo_data.staff_note.id}/comments",
        json={"body": "foreign origin"},
        headers={"Origin": "https://evil.example"},
    )
    allowed = await client.post(
        f"/entries/{demo_data.staff_note.id}/comments",
        json={"body": "allowed origin"},
        headers={"Origin": "http://testserver"},
    )
    assert foreign.status_code == 403
    assert allowed.status_code == 200, allowed.text


def test_production_security_validation_fails_closed() -> None:
    insecure = Settings(
        app_env="production",
        session_secret="a" * 40,
        cookie_secure=False,
    )
    with pytest.raises(ValueError, match="COOKIE_SECURE"):
        insecure.validate_runtime_security()
    secure = Settings(
        app_env="production",
        database_url="postgresql://user:password@db.internal/nightingale",
        session_secret="a" * 40,
        cookie_secure=True,
        allowed_origins="https://nightingale-shared-care-note.onrender.com",
        llm_provider="fixture",
        voice_provider="disabled",
    )
    secure.validate_runtime_security()
