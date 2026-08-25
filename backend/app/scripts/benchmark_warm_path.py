"""Run the reproducible local Gate C real-TCP warm Glance benchmark."""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx
from sqlalchemy import select


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = REPOSITORY_ROOT / "backend"
ARTIFACT_ROOT = REPOSITORY_ROOT / "docs" / "evidence"
ARTIFACT_JSON = ARTIFACT_ROOT / "gate_c_warm_path.json"
ARTIFACT_MARKDOWN = ARTIFACT_ROOT / "gate_c_warm_path.md"
DATABASE_PATH = REPOSITORY_ROOT / ".uv-cache" / "gate-c-benchmark.sqlite"
BASE_URL = "http://127.0.0.1:8010"
SEED_PASSWORD = "gate-c-local-benchmark-password"
SAMPLE_COUNT = 1000
WARMUP_COUNT = 50
CONCURRENCY = 10
GIT_EXECUTABLE = (
    r"C:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE"
    r"\CommonExtensions\Microsoft\TeamFoundation\Team Explorer\Git\cmd\git.exe"
)


def percentile(values: list[float], quantile: float) -> float:
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil(quantile * len(ordered)) - 1))
    return ordered[index]


def benchmark_environment(database_url: str) -> dict[str, str]:
    return {
        **os.environ,
        "APP_ENV": "test",
        "DATABASE_URL": database_url,
        "DEMO_SEED_PASSWORD": SEED_PASSWORD,
        "SESSION_SECRET": "gate-c-local-benchmark-session-secret-32",
        "COOKIE_SECURE": "false",
        "ALLOWED_ORIGINS": "http://127.0.0.1:5173,http://localhost:5173",
    }


def run_local_command(arguments: list[str], environment: dict[str, str]) -> None:
    subprocess.run(
        [sys.executable, *arguments],
        cwd=BACKEND_ROOT,
        env=environment,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def prepare_dataset(database_url: str, environment: dict[str, str]) -> dict[str, int | str]:
    from app.db.session import SessionLocal
    from app.models import (
        Clinic,
        EntryOwnerRole,
        EntryType,
        EntryVersion,
        EntryVisibility,
        HighlightActionState,
        HighlightItemKind,
        HighlightStatus,
        Patient,
        User,
    )
    from app.services.entries import create_entry_record
    from app.services.highlights import create_highlight_record

    del database_url, environment
    db = SessionLocal()
    try:
        clinic = db.scalar(select(Clinic).where(Clinic.name == "Nightingale Demo Clinic A"))
        staff = db.scalar(select(User).where(User.email == "staff.a@clinic-a.test"))
        if clinic is None or staff is None:
            raise RuntimeError("Seed did not create the benchmark clinic and staff persona")
        target_patient = Patient(
            clinic_id=clinic.id,
            synthetic_display_name="Synthetic Benchmark Patient 000",
        )
        db.add(target_patient)
        db.commit()
        db.refresh(target_patient)

        patient_count = 1
        entry_count = 0
        highlight_count = 0
        for patient_index in range(26):
            if patient_index == 0:
                patient = target_patient
            else:
                patient = Patient(
                    clinic_id=clinic.id,
                    synthetic_display_name=f"Synthetic Benchmark Patient {patient_index:03d}",
                )
                db.add(patient)
                db.commit()
                db.refresh(patient)
                patient_count += 1
            for item_index in range(8):
                content = (
                    f"Synthetic benchmark item {patient_index:03d}-{item_index:02d} "
                    "requires routine care coordination."
                )
                entry = create_entry_record(
                    db,
                    clinic_id=clinic.id,
                    patient_id=patient.id,
                    entry_type=EntryType.STAFF_NOTE,
                    owner_role=EntryOwnerRole.STAFF,
                    visibility=EntryVisibility.INTERNAL,
                    content=content,
                    created_by_user_id=staff.id,
                    created_by_role="staff",
                    request_id=f"benchmark-entry-{patient_index}-{item_index}",
                    source_kind="manual",
                    source_reference=f"synthetic-benchmark-{patient_index}-{item_index}",
                )
                version_id = db.scalar(
                    select(EntryVersion.id).where(EntryVersion.entry_id == entry.id)
                )
                if version_id is None:
                    raise RuntimeError("Benchmark entry has no immutable source version")
                create_highlight_record(
                    db,
                    source_version_id=version_id,
                    start_offset=0,
                    end_offset=len(content),
                    quote=content,
                    item_kind=HighlightItemKind.INFORMATION,
                    status=HighlightStatus.ACCEPTED,
                    display_priority=float(100 - item_index),
                    risk_level=None,
                    risk_reason="Synthetic benchmark item for warm-path measurement.",
                    action_label=None,
                    action_state=HighlightActionState.NOT_APPLICABLE,
                    created_by_role="staff",
                    created_by_user_id=staff.id,
                    reviewed_by_user_id=staff.id,
                    request_id=f"benchmark-highlight-{patient_index}-{item_index}",
                )
                entry_count += 1
                highlight_count += 1
        return {
            "patients": patient_count,
            "benchmark_entries": entry_count,
            "benchmark_highlights": highlight_count,
            "target_patient_id": target_patient.id,
        }
    finally:
        db.close()


def wait_for_server(process: subprocess.Popen[bytes]) -> None:
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError("Benchmark Uvicorn exited before health became ready")
        try:
            response = httpx.get(BASE_URL + "/health", timeout=1)
            if response.status_code == 200:
                return
        except httpx.HTTPError:
            pass
        time.sleep(0.2)
    raise TimeoutError("Benchmark Uvicorn did not become ready within 30 seconds")


def login_cookie() -> str:
    with httpx.Client(base_url=BASE_URL, timeout=10) as client:
        response = client.post(
            "/auth/login",
            json={"email": "staff.a@clinic-a.test", "password": SEED_PASSWORD},
        )
        response.raise_for_status()
        return "; ".join(f"{name}={value}" for name, value in client.cookies.items())


def measure(target_patient_id: str, cookie_header: str) -> dict[str, Any]:
    path = f"/patients/{target_patient_id}/glance"
    thread_local = threading.local()

    def request_once(_: int) -> tuple[float, int, int]:
        client = getattr(thread_local, "client", None)
        if client is None:
            client = httpx.Client(
                base_url=BASE_URL,
                headers={"Cookie": cookie_header},
                timeout=30,
            )
            thread_local.client = client
        started = time.perf_counter()
        response = client.get(path)
        elapsed_ms = (time.perf_counter() - started) * 1000
        try:
            payload = response.json()
        except ValueError:
            payload = []
        item_count = len(payload) if isinstance(payload, list) else 0
        return elapsed_ms, response.status_code, item_count

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        warmup = list(executor.map(request_once, range(WARMUP_COUNT)))
        measured = list(executor.map(request_once, range(SAMPLE_COUNT)))
    latencies = [item[0] for item in measured]
    errors = sum(item[1] != 200 for item in measured)
    item_counts = [item[2] for item in measured]
    return {
        "warmup_requests": WARMUP_COUNT,
        "request_count": SAMPLE_COUNT,
        "concurrency": CONCURRENCY,
        "p50_ms": round(percentile(latencies, 0.50), 3),
        "p95_ms": round(percentile(latencies, 0.95), 3),
        "p99_ms": round(percentile(latencies, 0.99), 3),
        "max_ms": round(max(latencies), 3),
        "error_count": errors,
        "response_item_count": max(set(item_counts), key=item_counts.count),
        "warmup_error_count": sum(item[1] != 200 for item in warmup),
    }


def markdown_report(result: dict[str, Any]) -> str:
    metrics = result["metrics"]
    dataset = result["dataset"]
    target_state = "PASS" if result["target_met"] else "IN PROGRESS"
    return f"""# Gate C warm-path benchmark

Result: **{target_state}** for the local approximation target P95 <= 300 ms.

This is a measured local SQLite + Uvicorn TCP benchmark, not a hosted PostgreSQL
production result and not evidence of deployment TLS or encryption-at-rest.

| Field | Value |
| --- | --- |
| Commit | {result["commit"]} |
| Python | {result["python"]} |
| Database | {result["database"]} |
| Transport | {result["transport"]} |
| Patients | {dataset["patients"]} |
| Benchmark entries | {dataset["benchmark_entries"]} |
| Benchmark highlights/materialized rows | {dataset["benchmark_highlights"]} |
| Warm-up | {metrics["warmup_requests"]} |
| Measured requests | {metrics["request_count"]} |
| Concurrency | {metrics["concurrency"]} |
| Response item count | {metrics["response_item_count"]} |
| Errors | {metrics["error_count"]} |
| P50 | {metrics["p50_ms"]} ms |
| P95 | {metrics["p95_ms"]} ms |
| P99 | {metrics["p99_ms"]} ms |
| Max | {metrics["max_ms"]} ms |

The measured endpoint is GET /patients/{{patient_id}}/glance with a real
cookie session. It reads patient_glance_items; provider processing is only on
the authenticated write path.
"""


def main() -> None:
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()
    database_url = "sqlite:///" + DATABASE_PATH.as_posix()
    environment = benchmark_environment(database_url)
    os.environ.update(environment)
    server: subprocess.Popen[bytes] | None = None
    try:
        run_local_command(["-m", "alembic", "upgrade", "head"], environment)
        run_local_command(["-m", "app.scripts.seed_demo"], environment)
        dataset = prepare_dataset(database_url, environment)
        server = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "--host",
                "127.0.0.1",
                "--port",
                str(urlparse(BASE_URL).port or 8010),
                "app.main:app",
            ],
            cwd=BACKEND_ROOT,
            env=environment,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        wait_for_server(server)
        metrics = measure(str(dataset["target_patient_id"]), login_cookie())
        try:
            commit = (
                subprocess.run(
                    [GIT_EXECUTABLE, "rev-parse", "--short", "HEAD"],
                    cwd=REPOSITORY_ROOT,
                    capture_output=True,
                    text=True,
                    check=False,
                ).stdout.strip()
                or "unknown"
            )
        except OSError:
            commit = "unknown"
        result: dict[str, Any] = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "commit": commit,
            "python": sys.version.split()[0],
            "database": "file-backed SQLite local approximation",
            "transport": "real TCP HTTP via Uvicorn and httpx.Client",
            "dataset": dataset,
            "metrics": metrics,
            "target_p95_ms": 300,
            "target_met": metrics["p95_ms"] <= 300 and metrics["error_count"] == 0,
        }
        ARTIFACT_JSON.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        ARTIFACT_MARKDOWN.write_text(markdown_report(result), encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True))
    finally:
        if server is not None:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=10)
        if DATABASE_PATH.exists():
            DATABASE_PATH.unlink()


if __name__ == "__main__":
    main()
