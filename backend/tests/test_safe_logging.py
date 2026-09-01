"""Tests for the allowlisted application log boundary and explicit log audit tool."""

import json
import logging
from pathlib import Path

import httpx
import pytest
from starlette.types import Receive, Scope, Send

from app.middleware.safe_exceptions import SafeExceptionMiddleware
from app.observability.safe_logging import configure_safe_logging, safe_event
from app.scripts.audit_phi_logs import audit_paths


def test_safe_event_emits_only_bounded_metadata(caplog: pytest.LogCaptureFixture) -> None:
    configure_safe_logging(["Sarah Tan"])
    logger = logging.getLogger("nightingale")
    with caplog.at_level(logging.INFO, logger="nightingale"):
        safe_event(
            logger,
            "ai_redaction_completed",
            request_id="request-1",
            clinic_id="clinic-a",
            patient_id="patient-a",
            entity_type="ai_processing_job",
            entity_id="job-a",
            provider_name="deepseek-v4-flash",
            status="redacted",
            input_hash="a" * 64,
            replacement_categories="id,name,phone",
            replacement_count=3,
        )
    record = json.loads(caplog.records[-1].getMessage())
    assert record == {
        "clinic_id": "clinic-a",
        "entity_id": "job-a",
        "entity_type": "ai_processing_job",
        "event_code": "ai_redaction_completed",
        "input_hash": "a" * 64,
        "patient_id": "patient-a",
        "provider_name": "deepseek-v4-flash",
        "replacement_categories": "id,name,phone",
        "replacement_count": 3,
        "request_id": "request-1",
        "status": "redacted",
    }


def test_defensive_filter_removes_phi_credentials_and_injection(
    caplog: pytest.LogCaptureFixture,
) -> None:
    configure_safe_logging(["Sarah Tan"])
    logger = logging.getLogger("nightingale")
    with caplog.at_level(logging.WARNING, logger="nightingale"):
        logger.warning(
            "raw Sarah Tan S1234567D +65 9123 4567 Authorization: Bearer token-sentinel\nforged"
        )
    message = caplog.records[-1].getMessage()
    assert "Sarah Tan" not in message
    assert "S1234567D" not in message
    assert "9123" not in message
    assert "token-sentinel" not in message
    assert "\n" not in message
    assert r"\n" in message


def test_sanitizer_failure_discards_the_entire_message(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    import app.observability.safe_logging as safe_logging

    configure_safe_logging([])
    monkeypatch.setattr(
        safe_logging,
        "sanitize_log_text",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("raw sentinel")),
    )
    logger = logging.getLogger("nightingale")
    with caplog.at_level(logging.WARNING, logger="nightingale"):
        logger.warning("raw sentinel Sarah Tan")
    assert caplog.records[-1].getMessage() == "log_sanitization_failed"
    assert "raw sentinel" not in caplog.text


def test_safe_event_rejects_unknown_event_or_field() -> None:
    logger = logging.getLogger("nightingale")
    with pytest.raises(ValueError, match="unknown safe event code"):
        safe_event(logger, "arbitrary_event", request_id="request-1")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        safe_event(  # type: ignore[call-arg]
            logger,
            "ai_job_created",
            request_id="request-1",
            arbitrary="not-allowed",
        )


def test_explicit_log_audit_reports_categories_without_echoing_values(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    clean = tmp_path / "clean.log"
    dirty = tmp_path / "dirty.log"
    clean.write_text('{"event_code":"ai_job_created","request_id":"job-1"}\n', encoding="utf-8")
    dirty.write_text(
        "Sarah Tan S1234567D +65 9123 4567 Authorization: Bearer token-sentinel\n",
        encoding="utf-8",
    )
    assert audit_paths([clean], ["Sarah Tan"]) == 0
    clean_output = capsys.readouterr().out
    assert '"status": "clean"' in clean_output
    assert audit_paths([dirty], ["Sarah Tan"]) == 1
    dirty_output = capsys.readouterr().out
    assert '"category": "known_name"' in dirty_output
    assert '"category": "sg_id"' in dirty_output
    assert '"category": "phone"' in dirty_output
    assert "Sarah Tan" not in dirty_output
    assert "S1234567D" not in dirty_output
    assert "token-sentinel" not in dirty_output
    assert audit_paths([tmp_path / "missing.log"]) == 1
    missing_output = capsys.readouterr().out
    assert '"category": "unreadable"' in missing_output


@pytest.mark.asyncio
async def test_unexpected_exception_boundary_returns_generic_response_and_safe_log(
    caplog: pytest.LogCaptureFixture,
) -> None:
    configure_safe_logging(["Sarah Tan"])

    async def failing_app(scope: Scope, receive: Receive, send: Send) -> None:
        del scope, receive, send
        raise RuntimeError("raw Sarah Tan S1234567D +65 9123 4567")

    application = SafeExceptionMiddleware(failing_app)
    with caplog.at_level("INFO", logger="nightingale"):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=application),
            base_url="http://testserver",
        ) as client:
            response = await client.get(
                "/synthetic-error?raw=Sarah%20Tan",
                headers={"X-Request-ID": "request-safe"},
            )
    assert response.status_code == 500
    assert response.json() == {
        "detail": "Internal server error",
        "request_id": "request-safe",
    }
    assert "raw Sarah Tan" not in caplog.text
    assert "S1234567D" not in caplog.text
    assert "9123" not in caplog.text
    events = [
        json.loads(record.getMessage())
        for record in caplog.records
        if record.name == "nightingale" and record.getMessage().startswith("{")
    ]
    assert events[-1]["event_code"] == "request_internal_error"
    assert events[-1]["exception_code"] == "internal_error"
    assert "raw" not in events[-1]
