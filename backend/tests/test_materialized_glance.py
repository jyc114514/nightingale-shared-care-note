"""Materialized Glance read-model and no-provider-read-path tests."""

from typing import Any

import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import EntryVersion, PatientGlanceItem
from conftest import DemoData, TEST_PASSWORD


async def login(client: httpx.AsyncClient, email: str) -> None:
    response = await client.post("/auth/login", json={"email": email, "password": TEST_PASSWORD})
    assert response.status_code == 200, response.text


def source_version_id(db_session: Session, entry_id: str) -> str:
    version = db_session.scalar(
        select(EntryVersion).where(
            EntryVersion.entry_id == entry_id,
            EntryVersion.version_number == 1,
        )
    )
    assert version is not None
    return version.id


@pytest.mark.asyncio
async def test_highlight_writes_projection_and_glance_reads_only_materialized_rows(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider_calls = 0

    def unexpected_provider() -> Any:
        nonlocal provider_calls
        provider_calls += 1
        raise AssertionError("Glance read path must not create a provider")

    monkeypatch.setattr("app.services.ai_processing.get_provider", unexpected_provider)
    await login(client, "clinician@clinic-a.test")
    entries = [
        demo_data.patient_summary,
        demo_data.patient_instruction,
        demo_data.staff_note,
        demo_data.clinician_section,
        demo_data.ai_doctor,
        demo_data.ai_nurse,
        demo_data.ai_summary,
    ]
    highlight_ids: list[str] = []
    for index, entry in enumerate(entries):
        content = db_session.scalar(
            select(EntryVersion.content).where(
                EntryVersion.entry_id == entry.id,
                EntryVersion.version_number == 1,
            )
        )
        assert content is not None
        response = await client.post(
            f"/entry-versions/{source_version_id(db_session, entry.id)}/highlights",
            json={
                "start_offset": 0,
                "end_offset": len(content),
                "quote": content,
                "item_kind": "action",
                "display_priority": 10 + index,
                "risk_reason": "Synthetic materialized read-model test",
                "action_label": "Review synthetic item",
                "action_state": "open",
            },
        )
        assert response.status_code == 200, response.text
        highlight_ids.append(response.json()["id"])

    rows = list(
        db_session.scalars(
            select(PatientGlanceItem).where(PatientGlanceItem.highlight_id.in_(highlight_ids))
        )
    )
    assert len(rows) == len(highlight_ids)
    assert all(row.source_version_id and row.quote_sha256 for row in rows)
    assert all(row.offset_unit == "unicode_codepoint" for row in rows)

    first = await client.get(f"/patients/{demo_data.patient_a.id}/glance")
    second = await client.get(f"/patients/{demo_data.patient_a.id}/glance")
    assert first.status_code == 200, first.text
    assert second.status_code == 200, second.text
    assert len(first.json()) == 6
    assert [item["id"] for item in first.json()] == [item["id"] for item in second.json()]
    assert provider_calls == 0

    rejected = await client.patch(
        f"/highlights/{highlight_ids[-1]}/review",
        json={"status": "rejected"},
    )
    assert rejected.status_code == 200, rejected.text
    active_ids = {
        item["id"]
        for item in (await client.get(f"/patients/{demo_data.patient_a.id}/glance")).json()
    }
    assert highlight_ids[-1] not in active_ids
    db_session.expire_all()
    projected = db_session.get(PatientGlanceItem, highlight_ids[-1])
    assert projected is not None
    assert projected.status == "rejected"
