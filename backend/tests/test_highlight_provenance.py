"""Gate B's twelve focused immutable-source and provenance checks."""

import hashlib

import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    AuditLog,
    EntryOwnerRole,
    EntryType,
    EntryVersion,
    EntryVisibility,
    Highlight,
)
from app.services.entries import create_entry_record
from conftest import DemoData, TEST_PASSWORD


async def login(client: httpx.AsyncClient, email: str) -> None:
    response = await client.post("/auth/login", json={"email": email, "password": TEST_PASSWORD})
    assert response.status_code == 200, response.text


def version_id(db_session: Session, entry_id: str, version_number: int = 1) -> str:
    version = db_session.scalar(
        select(EntryVersion).where(
            EntryVersion.entry_id == entry_id,
            EntryVersion.version_number == version_number,
        )
    )
    assert version is not None
    return version.id


async def create_highlight(
    client: httpx.AsyncClient,
    source_version_id: str,
    content: str,
    quote: str,
    **overrides: object,
) -> httpx.Response:
    start = content.index(quote) if quote in content else 0
    payload: dict[str, object] = {
        "start_offset": start,
        "end_offset": start + len(quote),
        "quote": quote,
        "item_kind": "information",
        "display_priority": 50,
        "risk_reason": "Synthetic provenance test reason",
        "action_state": "not_applicable",
    }
    payload.update(overrides)
    return await client.post(
        f"/entry-versions/{source_version_id}/highlights",
        json=payload,
    )


@pytest.mark.asyncio
async def test_manual_highlight_keeps_source_entry_and_version_ids(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    await login(client, "clinician@clinic-a.test")
    content = "Original staff note"
    response = await create_highlight(
        client,
        version_id(db_session, demo_data.staff_note.id),
        content,
        content,
        item_kind="action",
        display_priority=80,
        risk_level="low",
        risk_reason="Synthetic manual action",
        action_label="Review note",
        action_state="open",
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["source_entry_id"] == demo_data.staff_note.id
    assert body["source_version_id"] == version_id(db_session, demo_data.staff_note.id)
    assert body["created_by_role"] == "clinician"


@pytest.mark.asyncio
async def test_ai_highlight_has_source_reference_and_sha256(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    await login(client, "clinician@clinic-a.test")
    content = "Synthetic doctor consult finding"
    response = await create_highlight(
        client,
        version_id(db_session, demo_data.ai_doctor.id),
        content,
        "doctor consult finding",
        item_kind="information",
        display_priority=70,
        risk_reason="Synthetic AI source needs review",
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["source_entry_id"] == demo_data.ai_doctor.id
    source = await client.get(f"/highlights/{body['id']}/source")
    assert source.status_code == 200, source.text
    source_body = source.json()
    assert source_body["source_reference"] == "fixture-doctor-consult"
    assert source_body["quote"] == "doctor consult finding"
    assert body["quote_sha256"] == hashlib.sha256(b"doctor consult finding").hexdigest()


@pytest.mark.asyncio
async def test_unicode_offsets_are_python_codepoint_offsets(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    content = "Dose change \U0001f600 requires review"
    entry = create_entry_record(
        db_session,
        clinic_id=demo_data.clinic_a.id,
        patient_id=demo_data.patient_a.id,
        entry_type=EntryType.STAFF_NOTE,
        owner_role=EntryOwnerRole.STAFF,
        visibility=EntryVisibility.INTERNAL,
        content=content,
        created_by_user_id=demo_data.staff_a.id,
        created_by_role="staff",
        request_id="unicode-highlight-test",
        source_kind="manual",
        source_reference="synthetic-unicode-note",
    )
    quote = "\U0001f600 requires"
    await login(client, "clinician@clinic-a.test")
    response = await create_highlight(
        client,
        version_id(db_session, entry.id),
        content,
        quote,
        item_kind="flag",
        display_priority=60,
        risk_reason="Unicode span test",
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert content[body["start_offset"] : body["end_offset"]] == quote
    assert body["offset_unit"] == "unicode_codepoint"


@pytest.mark.asyncio
async def test_repeated_non_bmp_quote_uses_the_requested_occurrence(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    content = "Repeat \U0001f600. Repeat \U0001f600."
    quote = "Repeat \U0001f600"
    entry = create_entry_record(
        db_session,
        clinic_id=demo_data.clinic_a.id,
        patient_id=demo_data.patient_a.id,
        entry_type=EntryType.STAFF_NOTE,
        owner_role=EntryOwnerRole.STAFF,
        visibility=EntryVisibility.INTERNAL,
        content=content,
        created_by_user_id=demo_data.staff_a.id,
        created_by_role="staff",
        request_id="repeated-unicode-highlight-test",
    )
    start = content.rfind(quote)
    await login(client, "clinician@clinic-a.test")
    response = await client.post(
        f"/entry-versions/{version_id(db_session, entry.id)}/highlights",
        json={
            "start_offset": start,
            "end_offset": start + len(quote),
            "quote": quote,
            "item_kind": "information",
            "display_priority": 55,
            "risk_reason": "Repeated Unicode span test",
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["start_offset"] == start
    source = await client.get(f"/highlights/{response.json()['id']}/source")
    assert source.status_code == 200, source.text
    source_body = source.json()
    assert source_body["version_content"][start : start + len(quote)] == quote


@pytest.mark.asyncio
async def test_source_endpoint_resolves_exact_immutable_quote(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    await login(client, "clinician@clinic-a.test")
    content = "Original staff note"
    created = await create_highlight(
        client,
        version_id(db_session, demo_data.staff_note.id),
        content,
        "staff note",
    )
    assert created.status_code == 200, created.text
    source = await client.get(f"/highlights/{created.json()['id']}/source")
    assert source.status_code == 200, source.text
    assert source.json()["version_content"] == content
    assert source.json()["version_content"][
        source.json()["start_offset"] : source.json()["end_offset"]
    ] == ("staff note")


@pytest.mark.asyncio
async def test_highlight_stays_on_old_version_after_entry_update(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    await login(client, "clinician@clinic-a.test")
    created = await create_highlight(
        client,
        version_id(db_session, demo_data.staff_note.id),
        "Original staff note",
        "Original staff",
    )
    assert created.status_code == 200, created.text
    highlight = created.json()
    await login(client, "staff@clinic-a.test")
    updated = await client.patch(
        f"/entries/{demo_data.staff_note.id}",
        json={"expected_version": 1, "new_content": "New immutable staff note"},
    )
    assert updated.status_code == 200, updated.text
    source = await client.get(f"/highlights/{highlight['id']}/source")
    assert source.status_code == 200, source.text
    assert source.json()["source_version_id"] == highlight["source_version_id"]
    assert source.json()["version_content"] == "Original staff note"


@pytest.mark.asyncio
async def test_bad_offsets_are_rejected(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    await login(client, "clinician@clinic-a.test")
    response = await client.post(
        f"/entry-versions/{version_id(db_session, demo_data.staff_note.id)}/highlights",
        json={
            "start_offset": 0,
            "end_offset": 999,
            "quote": "Original staff note",
            "item_kind": "information",
            "display_priority": 20,
            "risk_reason": "Invalid offset test",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_bad_quote_is_rejected(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    await login(client, "clinician@clinic-a.test")
    response = await client.post(
        f"/entry-versions/{version_id(db_session, demo_data.staff_note.id)}/highlights",
        json={
            "start_offset": 0,
            "end_offset": 8,
            "quote": "Forged quote",
            "item_kind": "information",
            "display_priority": 20,
            "risk_reason": "Invalid quote test",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_cross_source_provenance_is_rejected(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    await login(client, "clinician@clinic-a.test")
    response = await create_highlight(
        client,
        version_id(db_session, demo_data.staff_note.id),
        "Original staff note",
        "Synthetic doctor consult finding",
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_patient_cannot_read_or_create_internal_highlights(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    await login(client, "patient@clinic-a.test")
    glance = await client.get(f"/patients/{demo_data.patient_a.id}/glance")
    assert glance.status_code == 403
    create = await client.post(
        f"/entry-versions/{version_id(db_session, demo_data.ai_summary.id)}/highlights",
        json={
            "start_offset": 0,
            "end_offset": 3,
            "quote": "Raw",
            "item_kind": "flag",
            "display_priority": 30,
            "risk_reason": "Patient must not create internal item",
        },
    )
    assert create.status_code == 403


@pytest.mark.asyncio
async def test_cross_clinic_user_cannot_resolve_source(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    await login(client, "clinician@clinic-a.test")
    created = await create_highlight(
        client,
        version_id(db_session, demo_data.staff_note.id),
        "Original staff note",
        "Original staff",
    )
    assert created.status_code == 200, created.text
    await login(client, "staff@clinic-b.test")
    response = await client.get(f"/highlights/{created.json()['id']}/source")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_provenance_inconsistency_is_not_resolved(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    await login(client, "clinician@clinic-a.test")
    created = await create_highlight(
        client,
        version_id(db_session, demo_data.staff_note.id),
        "Original staff note",
        "Original staff",
    )
    assert created.status_code == 200, created.text
    highlight = db_session.get(Highlight, created.json()["id"])
    assert highlight is not None
    highlight.source_entry_id = demo_data.ai_summary.id
    db_session.commit()
    response = await client.get(f"/highlights/{highlight.id}/source")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_staff_cannot_review_highlight_and_clinician_can_change_status(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    await login(client, "clinician@clinic-a.test")
    created = await create_highlight(
        client,
        version_id(db_session, demo_data.ai_nurse.id),
        "Synthetic nurse consult finding",
        "nurse consult finding",
        display_priority=90,
        risk_level="high",
        risk_reason="Synthetic referral requires review",
        action_state="open",
    )
    assert created.status_code == 200, created.text
    highlight_id = created.json()["id"]
    await login(client, "staff@clinic-a.test")
    denied = await client.patch(f"/highlights/{highlight_id}/review", json={"status": "rejected"})
    assert denied.status_code == 403
    await login(client, "clinician@clinic-a.test")
    reviewed = await client.patch(
        f"/highlights/{highlight_id}/review", json={"status": "conflict_review"}
    )
    assert reviewed.status_code == 200, reviewed.text
    assert reviewed.json()["status"] == "conflict_review"
    assert reviewed.json()["display_priority"] == 90
    assert reviewed.json()["risk_level"] == "high"


@pytest.mark.asyncio
async def test_highlight_review_audit_distinguishes_decisions_and_keeps_source_immutable(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    await login(client, "clinician@clinic-a.test")
    created = await create_highlight(
        client,
        version_id(db_session, demo_data.ai_doctor.id),
        "Synthetic doctor consult finding",
        "doctor consult finding",
        display_priority=88,
        risk_level="high",
        risk_reason="Synthetic review decision",
    )
    assert created.status_code == 200, created.text
    highlight_id = created.json()["id"]
    source_version = db_session.scalar(
        select(EntryVersion).where(EntryVersion.id == created.json()["source_version_id"])
    )
    assert source_version is not None

    rejected = await client.patch(f"/highlights/{highlight_id}/review", json={"status": "rejected"})
    assert rejected.status_code == 200, rejected.text
    accepted = await client.patch(f"/highlights/{highlight_id}/review", json={"status": "accepted"})
    assert accepted.status_code == 200, accepted.text
    assert accepted.json()["reviewed_at"]
    assert accepted.json()["reviewed_at"] >= source_version.created_at.isoformat()

    audit_rows = list(
        db_session.scalars(
            select(AuditLog)
            .where(
                AuditLog.entity_type == "highlight",
                AuditLog.entity_id == highlight_id,
            )
            .order_by(AuditLog.created_at)
        )
    )
    assert [row.action for row in audit_rows[-2:]] == [
        "highlight_rejected",
        "highlight_accepted",
    ]
    assert all(row.request_id for row in audit_rows)
    assert not any(
        hasattr(row, field) for row in audit_rows for field in ("quote", "content", "raw_text")
    )
    source = await client.get(f"/highlights/{highlight_id}/source")
    assert source.status_code == 200, source.text
    assert source.json()["version_content"] == "Synthetic doctor consult finding"
