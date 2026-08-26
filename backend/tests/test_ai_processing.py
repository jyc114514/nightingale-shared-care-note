"""Gate C/Phase 8 processing, idempotency, provenance, and privacy tests."""

import json
from typing import Any

import httpx
import pytest
from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.deepseek import DeepSeekProvider
from app.models import AIProcessingJob, CollaborationEvent, Entry, EntryType, Highlight
from app.config import Settings
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

    monkeypatch.setattr(
        "app.services.ai_processing.get_provider", lambda *args, **kwargs: SpyProvider()
    )
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

    monkeypatch.setattr(
        "app.services.ai_processing.get_provider", lambda *args, **kwargs: MalformedProvider()
    )
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

    monkeypatch.setattr(
        "app.services.ai_processing.get_provider", lambda *args, **kwargs: UnavailableProvider()
    )
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


@pytest.mark.asyncio
async def test_deepseek_mock_success_uses_redacted_boundary_and_emits_safe_event(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    requests: list[httpx.Request] = []
    suggestion = {
        "summary": "The synthetic follow-up remains pending.",
        "highlight_quote": "remains pending",
        "item_kind": "action",
        "priority_reason": "The follow-up needs clinician review.",
        "action_label": "Review synthetic follow-up",
        "action_state": "open",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {"content": json.dumps(suggestion)},
                    }
                ]
            },
        )

    provider = DeepSeekProvider(
        SecretStr("test-deepseek-key"),
        transport=httpx.MockTransport(handler),
    )
    monkeypatch.setattr(
        "app.services.ai_processing.get_provider",
        lambda *args, **kwargs: provider,
    )
    await login(client, "staff@clinic-a.test")
    response = await client.post(
        f"/patients/{demo_data.patient_a.id}/ai-processing",
        json={
            "interaction_type": "ai_nurse_consult_summary",
            "text": "Sarah Tan reported pain; NRIC S1234567D; +65 9123 4567.",
            "source_reference": "synthetic-phase-8-success",
            "idempotency_key": "phase-8-success",
        },
    )
    assert response.status_code == 200, response.text
    job = response.json()
    assert job["provider_name"] == "deepseek-v4-flash"
    assert job["status"] == "completed"
    assert job["entry_id"] and job["highlight_id"]
    assert requests
    request_body = json.loads(requests[0].content)
    serialized = json.dumps(request_body)
    assert "Sarah Tan" not in serialized
    assert "S1234567D" not in serialized
    assert "9123" not in serialized
    assert "synthetic-phase-8-success" not in serialized
    assert "source_reference" not in request_body

    source = await client.get(f"/highlights/{job['highlight_id']}/source")
    assert source.status_code == 200, source.text
    source_body = source.json()
    assert source_body["quote"] == "remains pending"
    assert (
        source_body["version_content"][source_body["start_offset"] : source_body["end_offset"]]
        == source_body["quote"]
    )
    event = db_session.scalar(
        select(CollaborationEvent).where(
            CollaborationEvent.resource_id == job["id"],
            CollaborationEvent.resource_type == "ai_processing",
        )
    )
    assert event is not None
    assert event.event_kind == "ai_processing_completed"
    assert event.actor_user_id is None

    await login(client, "patient@clinic-a.test")
    patient_timeline = await client.get(f"/patients/{demo_data.patient_a.id}/timeline")
    assert patient_timeline.status_code == 200
    assert job["entry_id"] not in {row["id"] for row in patient_timeline.json()}


@pytest.mark.asyncio
async def test_deepseek_mock_failure_keeps_provider_identity_and_creates_no_source(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = DeepSeekProvider(
        SecretStr("test-deepseek-key"),
        transport=httpx.MockTransport(
            lambda request: httpx.Response(401, content=b"secret response must not be exposed")
        ),
    )
    monkeypatch.setattr(
        "app.services.ai_processing.get_provider",
        lambda *args, **kwargs: provider,
    )
    await login(client, "staff@clinic-a.test")
    before_entries = db_session.query(Entry).count()
    before_highlights = db_session.query(Highlight).count()
    response = await client.post(
        f"/patients/{demo_data.patient_a.id}/ai-processing",
        json={
            "interaction_type": "ai_doctor_consult_summary",
            "text": "Synthetic provider failure input.",
            "source_reference": "synthetic-phase-8-failure",
            "idempotency_key": "phase-8-failure",
        },
    )
    assert response.status_code == 200, response.text
    job = response.json()
    assert job["provider_name"] == "deepseek-v4-flash"
    assert job["status"] == "failed_provider"
    assert job["error_code"] == "provider_auth_failed"
    assert job["entry_id"] is None
    assert job["highlight_id"] is None
    assert db_session.query(Entry).count() == before_entries
    assert db_session.query(Highlight).count() == before_highlights


@pytest.mark.asyncio
async def test_provider_info_is_safe_and_restricted_to_staff_or_clinicians(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    test_settings: Settings,
) -> None:
    await login(client, "staff@clinic-a.test")
    fixture_info = await client.get("/ai-processing/provider")
    assert fixture_info.status_code == 200, fixture_info.text
    assert fixture_info.json() == {
        "provider_name": "fixture-redacted-v1",
        "model": "deterministic-local",
        "configured": True,
        "mode": "fixture",
    }
    assert "api_key" not in fixture_info.text.lower()
    assert "base_url" not in fixture_info.text.lower()

    test_settings.llm_provider = "deepseek"
    test_settings.deepseek_api_key = SecretStr("test-deepseek-key")
    deepseek_info = await client.get("/ai-processing/provider")
    assert deepseek_info.status_code == 200, deepseek_info.text
    assert deepseek_info.json() == {
        "provider_name": "deepseek-v4-flash",
        "model": "deepseek-v4-flash",
        "configured": True,
        "mode": "deepseek",
    }
    assert "test-deepseek-key" not in deepseek_info.text
    await login(client, "patient@clinic-a.test")
    denied = await client.get("/ai-processing/provider")
    assert denied.status_code == 403
