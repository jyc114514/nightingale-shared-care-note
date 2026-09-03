"""Coverage for deterministic benchmark/report helpers and the real Glance probe."""

from pathlib import Path
import importlib

import httpx
import pytest
from fastapi import FastAPI
from sqlalchemy.orm import Session

from conftest import DemoData, TEST_PASSWORD


def test_percentile_helpers_keep_bounded_sorted_semantics() -> None:
    from app.scripts.benchmark_circuit_failfast import percentile as circuit_percentile
    from app.scripts.benchmark_patient_publication import percentile as publication_percentile
    from app.scripts.benchmark_warm_path import percentile as warm_percentile

    values = [30.0, 10.0, 20.0]
    for percentile in (circuit_percentile, publication_percentile, warm_percentile):
        assert percentile(values, 0.0) == 10.0
        assert percentile(values, 0.5) == 20.0
        assert percentile(values, 1.0) == 30.0


def test_benchmark_environments_are_explicit_synthetic_overlays() -> None:
    from app.scripts.benchmark_circuit_failfast import environment as circuit_environment
    from app.scripts.benchmark_patient_publication import environment as publication_environment
    from app.scripts.benchmark_warm_path import benchmark_environment

    warm = benchmark_environment("sqlite:///synthetic-warm")
    publication = publication_environment("sqlite:///synthetic-publication")
    circuit = circuit_environment("sqlite:///synthetic-circuit")

    assert warm["DATABASE_URL"] == "sqlite:///synthetic-warm"
    assert publication["DATABASE_URL"] == "sqlite:///synthetic-publication"
    assert circuit["DATABASE_URL"] == "sqlite:///synthetic-circuit"
    assert warm["COOKIE_SECURE"] == "false"
    assert publication["COOKIE_SECURE"] == "false"
    assert circuit["LLM_PROVIDER"] == "deepseek"
    assert circuit["ALLOWED_ORIGINS"] == "http://testserver"


@pytest.mark.parametrize("target_met", [True, False])
def test_warm_path_markdown_report_describes_target_state(target_met: bool) -> None:
    from app.scripts.benchmark_warm_path import markdown_report

    result = {
        "target_met": target_met,
        "commit": "synthetic-commit",
        "python": "3.10.20",
        "database": "file-backed SQLite local approximation",
        "transport": "real TCP HTTP via Uvicorn and httpx.Client",
        "dataset": {
            "patients": 1,
            "benchmark_entries": 8,
            "benchmark_highlights": 8,
        },
        "metrics": {
            "warmup_requests": 20,
            "request_count": 100,
            "concurrency": 10,
            "response_item_count": 6,
            "error_count": 0,
            "p50_ms": 10.0,
            "p95_ms": 20.0,
            "p99_ms": 25.0,
            "max_ms": 30.0,
        },
    }

    report = markdown_report(result)

    expected_state = "PASS" if target_met else "IN PROGRESS"
    assert f"Result: **{expected_state}**" in report
    assert "GET /patients/{patient_id}/glance" in report
    assert "real" in report and "cookie session" in report


@pytest.mark.asyncio
async def test_glance_benchmark_measure_uses_real_application_read_path(
    application: FastAPI,
    demo_data: DemoData,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    demo_data.staff_a.email = "staff.a@clinic-a.test"
    db_session.commit()
    monkeypatch.setenv("DEMO_SEED_PASSWORD", TEST_PASSWORD)
    from app.scripts import benchmark_glance

    result = await benchmark_glance.measure()

    assert result["transport"] == "httpx ASGITransport"
    assert result["warmup_requests"] == 20
    assert result["measured_requests"] == 100
    assert result["glance_items"] == 0
    del application


def test_audit_cli_main_uses_explicit_paths_without_echoing_values(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from app.scripts.audit_phi_logs import main

    clean = tmp_path / "clean.log"
    clean.write_text('{"event_code":"health_checked"}\n', encoding="utf-8")

    assert main([str(clean)]) == 0
    output = capsys.readouterr().out
    assert '"status": "clean"' in output


@pytest.mark.parametrize(
    "module_name,port_function_name",
    [
        ("app.scripts.round7_bridge_smoke", "free_port"),
        ("app.scripts.round7_baseline_compat_probe", "find_free_port"),
    ],
)
def test_compatibility_probe_health_helpers_use_http_status_and_free_ports(
    module_name: str,
    port_function_name: str,
) -> None:
    module = importlib.import_module(module_name)
    transport = httpx.MockTransport(lambda request: httpx.Response(200, request=request))
    with httpx.Client(transport=transport, base_url="http://synthetic") as client:
        module.wait_for_health(client)
    port = getattr(module, port_function_name)()
    assert isinstance(port, int)
    assert 1 <= port <= 65535
