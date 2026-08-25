"""Gate C processing, idempotency, provenance, and privacy tests."""

from typing import Any

import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AIProcessingJob, Entry, EntryType, Highlight
from conftest import DemoData, TEST_PASSWORD


async def login(client: httpx.AsyncClient, email: str) -> None:
    response = await client.post("/auth/login", json={"email": email, "password": TEST_PASSWORD})
    assert response.status_code == 200, response.text


@pytest.mark.asyncio
async def test_three_interaction_types_are_redacted_and_create_new_suggestions(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    await login(client, "staff@clinic-a.test")
    jobs: list[dict[str, Any]] = []
    for index, interaction_type in enumerate(
        (
            "ai_doctor_consult_summary",
            "ai_nurse_consult_summary",
            "ai_patient_session_summary",
        )
    ):
        response = await client.post(
            f"/patients/{demo_data.patient_a.id}/ai-processing",
            json={
                "interaction_type": interaction_type,
                "text": (
                    "Sarah Tan reported pain; NRIC S1234567D; "
                    "+65 9123 4567; dose change \U0001f600."
                ),
                "source_reference": f"synthetic-ai-{index}",
                "idempotency_key": f"gate-c-{index}",
            },
        )
        assert response.status_code == 200, response.text
        job = response.json()
        jobs.append(job)
        assert job["status"] == "completed"
        assert job["entry_id"]
        assert job["highlight_id"]
        assert job["error_code"] is None

    assert {
        row.entry_type
        for row in db_session.scalars(
            select(Entry).where(Entry.id.in_([job["entry_id"] for job in jobs]))
        )
    } == {
        EntryType.AI_DOCTOR_CONSULT_SUMMARY,
        EntryType.AI_NURSE_CONSULT_SUMMARY,
        EntryType.AI_PATIENT_SESSION_SUMMARY,
    }
    for job in jobs:
        stored_job = db_session.get(AIProcessingJob, job["id"])
        assert stored_job is not None
        assert stored_job.redacted_payload is not None
        assert "Sarah Tan" not in stored_job.redacted_payload
        assert "S1234567D" not in stored_job.redacted_payload
        assert "9123" not in stored_job.redacted_payload
        source = await client.get(f"/highlights/{job['highlight_id']}/source")
        assert source.status_code == 200, source.text
        body = source.json()
        assert body["version_content"][body["start_offset"] : body["end_offset"]] == body["quote"]
        timeline = await client.get(f"/patients/{demo_data.patient_a.id}/timeline")
        created = next(item for item in timeline.json() if item["id"] == job["entry_id"])
        assert created["author_role"] == "system"
        assert created["owner_role"] == "system"


@pytest.mark.asyncio
async def test_ai_processing_is_idempotent_and_redaction_failure_never_calls_provider(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0
    seen_payloads: list[Any] = []

    class SpyProvider:
        name = "spy"

        def process(self, payload: Any) -> Any:
            nonlocal calls
            calls += 1
            seen_payloads.append(payload)
            from app.ai.provider import FixtureProvider

            return FixtureProvider().process(payload)

    monkeypatch.setattr("app.services.ai_processing.get_provider", lambda: SpyProvider())
    await login(client, "clinician@clinic-a.test")
    payload = {
        "interaction_type": "ai_nurse_consult_summary",
        "text": "Sarah Tan has a stable synthetic note.",
        "source_reference": "synthetic-idempotent",
        "idempotency_key": "same-key",
    }
    first = await client.post(f"/patients/{demo_data.patient_a.id}/ai-processing", json=payload)
    second = await client.post(f"/patients/{demo_data.patient_a.id}/ai-processing", json=payload)
    assert first.status_code == 200, first.text
    assert second.status_code == 200, second.text
    assert first.json()["id"] == second.json()["id"]
    assert calls == 1
    assert "Sarah Tan" not in repr(seen_payloads[0])
    assert "S1234567D" not in repr(seen_payloads[0])
    assert "9123" not in repr(seen_payloads[0])

    monkeypatch.setattr(
        "app.ai.redaction.secondary_detector",
        lambda text, known_names: ["id"],
    )
    before_entries = db_session.query(Entry).count()
    failed = await client.post(
        f"/patients/{demo_data.patient_a.id}/ai-processing",
        json={
            **payload,
            "text": "Unknown raw ID S1234567D and phone +65 9123 4567.",
            "source_reference": "synthetic-redaction-failure",
            "idempotency_key": "redaction-failure",
        },
    )
    assert failed.status_code == 200, failed.text
    assert failed.json()["status"] == "failed_redaction"
    assert failed.json()["error_code"] in {
        "sensitive_token_remaining",
        "secondary_detector_failed",
    }
    assert failed.json()["entry_id"] is None
    assert calls == 1
    assert db_session.query(Entry).count() == before_entries
    failed_job = db_session.get(AIProcessingJob, failed.json()["id"])
    assert failed_job is not None
    assert failed_job.redacted_payload is None
    assert "S1234567D" not in (failed_job.source_reference or "")


@pytest.mark.asyncio
async def test_malformed_provider_output_does_not_create_entry_or_highlight(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class MalformedProvider:
        name = "malformed"

        def process(self, payload: Any) -> Any:
            del payload
            return {"summary": "not a complete provider output"}

    monkeypatch.setattr("app.services.ai_processing.get_provider", lambda: MalformedProvider())
    await login(client, "staff@clinic-a.test")
    before_ai_entries = (
        db_session.query(Entry).filter(Entry.entry_type == "ai_doctor_consult_summary").count()
    )
    before_highlights = db_session.query(Highlight).count()
    response = await client.post(
        f"/patients/{demo_data.patient_a.id}/ai-processing",
        json={
            "interaction_type": "ai_doctor_consult_summary",
            "text": "Synthetic malformed output input.",
            "source_reference": "synthetic-malformed",
            "idempotency_key": "malformed-output",
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "failed_provider"
    assert response.json()["error_code"] == "provider_output_invalid"
    assert (
        db_session.query(Entry).filter(Entry.entry_type == "ai_doctor_consult_summary").count()
        == before_ai_entries
    )
    assert db_session.query(Highlight).count() == before_highlights


@pytest.mark.asyncio
async def test_provider_unavailable_returns_safe_error_without_raw_logs(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class UnavailableProvider:
        name = "unavailable"

        def process(self, payload: Any) -> Any:
            del payload
            raise RuntimeError("raw sentinel Sarah Tan S1234567D +65 9123 4567")

    monkeypatch.setattr("app.services.ai_processing.get_provider", lambda: UnavailableProvider())
    await login(client, "staff@clinic-a.test")
    response = await client.post(
        f"/patients/{demo_data.patient_a.id}/ai-processing",
        json={
            "interaction_type": "ai_patient_session_summary",
            "text": "raw sentinel Sarah Tan S1234567D +65 9123 4567",
            "source_reference": "synthetic-provider-unavailable",
            "idempotency_key": "provider-unavailable",
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "failed_provider"
    assert response.json()["error_code"] == "provider_unavailable"
    assert "raw sentinel" not in caplog.text
    assert "Sarah Tan" not in caplog.text
    assert "S1234567D" not in caplog.text
    assert "9123" not in caplog.text


@pytest.mark.asyncio
async def test_patient_cannot_submit_or_read_ai_job(
    client: httpx.AsyncClient,
    demo_data: DemoData,
) -> None:
    await login(client, "patient@clinic-a.test")
    denied = await client.post(
        f"/patients/{demo_data.patient_a.id}/ai-processing",
        json={
            "interaction_type": "ai_doctor_consult_summary",
            "text": "synthetic",
            "source_reference": "synthetic",
            "idempotency_key": "patient-denied",
        },
    )
    assert denied.status_code == 403
