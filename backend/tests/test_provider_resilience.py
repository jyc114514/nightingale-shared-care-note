"""Integration checks for total provider budgets, persistent circuits, and status scope."""

from datetime import timedelta
import logging
import time

import httpx
import pytest
from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.ai.deepseek import DeepSeekProvider, ProviderError
from app.ai.redaction import RedactionFailure
from app.ai.schemas import RedactedPayload
from app.config import Settings
from app.db.base import utcnow
from app.models import AIProcessingJob, AIProviderCircuit, Entry, Highlight
from app.services.provider_resilience import (
    acquire_provider_permission,
    get_provider_availability,
    provider_status_for_clinic,
    record_provider_failure,
    record_provider_success,
)
from conftest import DemoData, TEST_PASSWORD


def resilience_settings() -> Settings:
    return Settings(
        app_env="test",
        database_url="sqlite:///unused.sqlite",
        session_secret="test-only-session-secret-with-at-least-32-chars",
        cookie_secure=False,
        allowed_origins="http://testserver",
        llm_provider="deepseek",
        deepseek_api_key=SecretStr("test-deepseek-key"),
        deepseek_timeout_seconds=0.2,
        deepseek_total_budget_seconds=0.3,
        deepseek_max_attempts=2,
        deepseek_circuit_failure_threshold=3,
        deepseek_circuit_cooldown_seconds=60,
    )


def test_deepseek_total_budget_bounds_attempts_without_real_sleep() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        raise httpx.ReadTimeout("synthetic 45 second hang", request=request)

    provider = DeepSeekProvider(
        SecretStr("test-deepseek-key"),
        timeout_seconds=0.2,
        total_budget_seconds=0.3,
        max_attempts=2,
        transport=httpx.MockTransport(handler),
    )
    started = time.monotonic()
    with pytest.raises(ProviderError, match="provider_timeout"):
        provider.process(
            RedactedPayload(
                interaction_type="ai_nurse_consult_summary",
                redacted_text="safe synthetic text",
                source_reference="synthetic-reference",
            )
        )
    assert calls == 2
    assert provider.last_attempt_count == 2
    assert time.monotonic() - started < 1
    provider.close()


def test_deepseek_total_budget_rejects_a_response_after_deadline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0
    clock = iter((10.0, 10.0, 10.4))

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200, json={"choices": []})

    monkeypatch.setattr("app.ai.deepseek.time.monotonic", lambda: next(clock))
    provider = DeepSeekProvider(
        SecretStr("test-deepseek-key"),
        timeout_seconds=0.2,
        total_budget_seconds=0.3,
        max_attempts=2,
        transport=httpx.MockTransport(handler),
    )
    with pytest.raises(ProviderError, match="provider_timeout"):
        provider.process(
            RedactedPayload(
                interaction_type="ai_nurse_consult_summary",
                redacted_text="safe synthetic text",
                source_reference="synthetic-reference",
            )
        )
    assert calls == 1
    provider.close()


def test_persistent_circuit_threshold_half_open_probe_and_success(
    db_session: Session, demo_data: DemoData
) -> None:
    settings = resilience_settings()
    provider_name = "deepseek-v4-flash"
    for index in range(3):
        permission = acquire_provider_permission(
            db_session,
            clinic_id=demo_data.clinic_a.id,
            provider_name=provider_name,
            app_settings=settings,
            request_id=f"circuit-request-{index}",
        )
        assert permission.allowed is True
        record_provider_failure(
            db_session,
            clinic_id=demo_data.clinic_a.id,
            provider_name=provider_name,
            error_code="provider_unavailable",
            app_settings=settings,
            request_id=f"circuit-failure-{index}",
        )
    status = get_provider_availability(
        db_session,
        clinic_id=demo_data.clinic_a.id,
        provider_name=provider_name,
        app_settings=settings,
    )
    assert status.circuit_state == "open"
    assert status.consecutive_failures == 3
    blocked = acquire_provider_permission(
        db_session,
        clinic_id=demo_data.clinic_a.id,
        provider_name=provider_name,
        app_settings=settings,
        request_id="circuit-blocked",
    )
    assert blocked.allowed is False
    assert blocked.circuit_state == "open"
    circuit = db_session.scalar(
        select(AIProviderCircuit).where(
            AIProviderCircuit.clinic_id == demo_data.clinic_a.id,
            AIProviderCircuit.provider_name == provider_name,
        )
    )
    assert circuit is not None
    circuit.open_until = utcnow() - timedelta(seconds=1)
    db_session.commit()
    probe = acquire_provider_permission(
        db_session,
        clinic_id=demo_data.clinic_a.id,
        provider_name=provider_name,
        app_settings=settings,
        request_id="circuit-probe",
    )
    assert probe.allowed is True
    assert probe.probe is True
    second_probe = acquire_provider_permission(
        db_session,
        clinic_id=demo_data.clinic_a.id,
        provider_name=provider_name,
        app_settings=settings,
        request_id="circuit-second-probe",
    )
    assert second_probe.allowed is False
    assert second_probe.circuit_state == "half_open"
    record_provider_success(
        db_session,
        clinic_id=demo_data.clinic_a.id,
        provider_name=provider_name,
        app_settings=settings,
        request_id="circuit-success",
    )
    closed = get_provider_availability(
        db_session,
        clinic_id=demo_data.clinic_a.id,
        provider_name=provider_name,
        app_settings=settings,
    )
    assert closed.circuit_state == "closed"
    assert closed.consecutive_failures == 0
    assert closed.last_failure_code is None

    for index in range(3):
        assert acquire_provider_permission(
            db_session,
            clinic_id=demo_data.clinic_a.id,
            provider_name=provider_name,
            app_settings=settings,
            request_id=f"circuit-reopen-request-{index}",
        ).allowed
        record_provider_failure(
            db_session,
            clinic_id=demo_data.clinic_a.id,
            provider_name=provider_name,
            error_code="provider_unavailable",
            app_settings=settings,
            request_id=f"circuit-reopen-failure-{index}",
        )
    circuit = db_session.scalar(
        select(AIProviderCircuit).where(
            AIProviderCircuit.clinic_id == demo_data.clinic_a.id,
            AIProviderCircuit.provider_name == provider_name,
        )
    )
    assert circuit is not None
    circuit.open_until = utcnow() - timedelta(seconds=1)
    db_session.commit()
    assert acquire_provider_permission(
        db_session,
        clinic_id=demo_data.clinic_a.id,
        provider_name=provider_name,
        app_settings=settings,
        request_id="circuit-reopen-probe",
    ).probe
    record_provider_failure(
        db_session,
        clinic_id=demo_data.clinic_a.id,
        provider_name=provider_name,
        error_code="provider_timeout",
        app_settings=settings,
        request_id="circuit-reopen-probe-failure",
    )
    reopened = get_provider_availability(
        db_session,
        clinic_id=demo_data.clinic_a.id,
        provider_name=provider_name,
        app_settings=settings,
    )
    assert reopened.circuit_state == "open"


def test_non_counted_provider_output_failure_is_degraded_not_open(
    db_session: Session, demo_data: DemoData
) -> None:
    settings = resilience_settings()
    record_provider_failure(
        db_session,
        clinic_id=demo_data.clinic_a.id,
        provider_name="deepseek-v4-flash",
        error_code="provider_output_invalid",
        app_settings=settings,
        request_id="invalid-output",
    )
    status = provider_status_for_clinic(
        db_session,
        clinic_id=demo_data.clinic_a.id,
        app_settings=settings,
    )
    assert status.availability == "degraded"
    assert status.circuit_state == "closed"
    assert status.consecutive_failures == 0
    assert status.new_suggestions_available is True


def test_half_open_probe_is_reserved_across_two_database_sessions(
    db_session: Session, test_engine: Engine, demo_data: DemoData
) -> None:
    settings = resilience_settings()
    provider_name = "deepseek-v4-flash"
    for index in range(3):
        assert acquire_provider_permission(
            db_session,
            clinic_id=demo_data.clinic_a.id,
            provider_name=provider_name,
            app_settings=settings,
            request_id=f"multi-session-request-{index}",
        ).allowed
        record_provider_failure(
            db_session,
            clinic_id=demo_data.clinic_a.id,
            provider_name=provider_name,
            error_code="provider_unavailable",
            app_settings=settings,
            request_id=f"multi-session-failure-{index}",
        )
    circuit = db_session.scalar(
        select(AIProviderCircuit).where(
            AIProviderCircuit.clinic_id == demo_data.clinic_a.id,
            AIProviderCircuit.provider_name == provider_name,
        )
    )
    assert circuit is not None
    circuit.open_until = utcnow() - timedelta(seconds=1)
    db_session.commit()
    other_session = sessionmaker(
        bind=test_engine, autoflush=False, expire_on_commit=False, class_=Session
    )()
    try:
        first = acquire_provider_permission(
            db_session,
            clinic_id=demo_data.clinic_a.id,
            provider_name=provider_name,
            app_settings=settings,
            request_id="multi-session-probe-one",
        )
        second = acquire_provider_permission(
            other_session,
            clinic_id=demo_data.clinic_a.id,
            provider_name=provider_name,
            app_settings=settings,
            request_id="multi-session-probe-two",
        )
    finally:
        other_session.close()
    assert first.probe is True
    assert second.allowed is False
    assert second.circuit_state == "half_open"


@pytest.mark.asyncio
async def test_provider_status_is_internal_and_patient_scoped(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    test_settings: Settings,
) -> None:
    test_settings.llm_provider = "deepseek"
    test_settings.deepseek_api_key = SecretStr("test-deepseek-key")
    staff = await client.post(
        "/auth/login", json={"email": "staff@clinic-a.test", "password": TEST_PASSWORD}
    )
    assert staff.status_code == 200
    status = await client.get(f"/patients/{demo_data.patient_a.id}/ai-processing/provider-status")
    assert status.status_code == 200, status.text
    body = status.json()
    assert body["availability"] == "available"
    assert body["circuit_state"] == "closed"
    assert body["existing_records_available"] is True
    assert "test-deepseek-key" not in status.text
    assert "api.deepseek.com" not in status.text
    patient = await client.post(
        "/auth/login", json={"email": "patient@clinic-a.test", "password": TEST_PASSWORD}
    )
    assert patient.status_code == 200
    denied = await client.get(f"/patients/{demo_data.patient_a.id}/ai-processing/provider-status")
    assert denied.status_code == 403


@pytest.mark.asyncio
async def test_circuit_open_persists_failed_job_and_skips_fourth_provider_call(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
    test_settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    test_settings.llm_provider = "deepseek"
    test_settings.deepseek_api_key = SecretStr("test-deepseek-key")
    test_settings.deepseek_circuit_failure_threshold = 3
    calls = 0

    class FailingProvider:
        name = "deepseek-v4-flash"
        last_attempt_count = 2

        def process(self, payload: object) -> object:
            nonlocal calls
            del payload
            calls += 1
            raise ProviderError("provider_unavailable")

    monkeypatch.setattr(
        "app.services.ai_processing.get_provider", lambda *_args, **_kwargs: FailingProvider()
    )
    login = await client.post(
        "/auth/login", json={"email": "staff@clinic-a.test", "password": TEST_PASSWORD}
    )
    assert login.status_code == 200
    path = f"/patients/{demo_data.patient_a.id}/ai-processing"
    for index in range(3):
        response = await client.post(
            path,
            json={
                "interaction_type": "ai_doctor_consult_summary",
                "text": f"Safe synthetic failure {index}",
                "source_reference": f"synthetic-failure-{index}",
                "idempotency_key": f"resilience-failure-{index}",
            },
        )
        assert response.status_code == 200, response.text
        assert response.json()["status"] == "failed_provider"
        assert response.json()["error_code"] == "provider_unavailable"
    fourth = await client.post(
        path,
        json={
            "interaction_type": "ai_doctor_consult_summary",
            "text": "Safe synthetic circuit-open failure",
            "source_reference": "synthetic-circuit-open",
            "idempotency_key": "resilience-failure-4",
        },
    )
    assert fourth.status_code == 200, fourth.text
    assert fourth.json()["error_code"] == "provider_circuit_open"
    assert fourth.json()["retry_after_seconds"] is not None
    assert calls == 3
    assert db_session.query(Entry).count() == 7
    assert db_session.query(Highlight).count() == 0
    glance = await client.get(f"/patients/{demo_data.patient_a.id}/glance")
    assert glance.status_code == 200, glance.text
    assert len(glance.json()) == 0
    job = db_session.scalar(
        select(AIProcessingJob).where(AIProcessingJob.idempotency_key == "resilience-failure-4")
    )
    assert job is not None
    assert job.entry_id is None


@pytest.mark.asyncio
async def test_ai_events_prove_redaction_precedes_provider_and_failure_is_metadata_only(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    test_settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    test_settings.llm_provider = "fixture"
    provider_calls = 0

    class SpyProvider:
        name = "fixture-redacted-v1"

        def process(self, payload: object) -> object:
            nonlocal provider_calls
            provider_calls += 1
            raise ProviderError("provider_unavailable")

    event_codes: list[str] = []

    def capture_event(logger: logging.Logger, event_code: str, **kwargs: object) -> None:
        del logger, kwargs
        event_codes.append(event_code)

    monkeypatch.setattr(
        "app.services.ai_processing.get_provider", lambda *_args, **_kwargs: SpyProvider()
    )
    monkeypatch.setattr("app.services.ai_processing.safe_event", capture_event)
    login = await client.post(
        "/auth/login", json={"email": "staff@clinic-a.test", "password": TEST_PASSWORD}
    )
    assert login.status_code == 200
    response = await client.post(
        f"/patients/{demo_data.patient_a.id}/ai-processing",
        json={
            "interaction_type": "ai_doctor_consult_summary",
            "text": "Sarah Tan S1234567D +65 9123 4567",
            "source_reference": "synthetic-ordering",
            "idempotency_key": "ordering-provider-failure",
        },
    )
    assert response.status_code == 200
    assert event_codes[:4] == [
        "ai_job_created",
        "ai_redaction_completed",
        "ai_provider_call_started",
        "ai_provider_failed",
    ]
    assert provider_calls == 1


@pytest.mark.asyncio
async def test_redaction_failure_has_no_provider_started_event_or_call(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider_calls = 0

    class SpyProvider:
        name = "external-test-provider"

        def process(self, payload: object) -> object:
            nonlocal provider_calls
            provider_calls += 1
            raise AssertionError("provider must not be called")

    monkeypatch.setattr(
        "app.services.ai_processing.get_provider", lambda *_args, **_kwargs: SpyProvider()
    )

    def fail_redaction(*_args: object, **_kwargs: object) -> None:
        raise RedactionFailure("sensitive_token_remaining")

    event_codes: list[str] = []

    def capture_event(logger: logging.Logger, event_code: str, **kwargs: object) -> None:
        del logger, kwargs
        event_codes.append(event_code)

    monkeypatch.setattr("app.services.ai_processing.redact_text", fail_redaction)
    monkeypatch.setattr("app.services.ai_processing.safe_event", capture_event)
    await client.post(
        "/auth/login", json={"email": "staff@clinic-a.test", "password": TEST_PASSWORD}
    )
    response = await client.post(
        f"/patients/{demo_data.patient_a.id}/ai-processing",
        json={
            "interaction_type": "ai_doctor_consult_summary",
            "text": "synthetic input",
            "source_reference": "synthetic-redaction-failure",
            "idempotency_key": "ordering-redaction-failure",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "failed_redaction"
    assert event_codes[:2] == ["ai_job_created", "ai_redaction_failed"]
    assert "ai_provider_call_started" not in event_codes
    assert provider_calls == 0
