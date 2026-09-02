"""Measure the patient published-care projection over real local TCP HTTP."""

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
ARTIFACT_JSON = ARTIFACT_ROOT / "round4_patient_publication_p95.json"
DATABASE_PATH = REPOSITORY_ROOT / ".uv-cache" / "round4-publication-benchmark.sqlite"
BASE_URL = "http://127.0.0.1:8011"
SEED_PASSWORD = "round4-local-benchmark-password"
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


def environment(database_url: str) -> dict[str, str]:
    return {
        **os.environ,
        "APP_ENV": "test",
        "DATABASE_URL": database_url,
        "DEMO_SEED_PASSWORD": SEED_PASSWORD,
        "SESSION_SECRET": "round4-publication-benchmark-session-secret-32",
        "COOKIE_SECURE": "false",
        "ALLOWED_ORIGINS": "http://127.0.0.1:5173,http://localhost:5173",
    }


def run_local_command(arguments: list[str], env: dict[str, str]) -> None:
    subprocess.run(
        [sys.executable, *arguments],
        cwd=BACKEND_ROOT,
        env=env,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def prepare_published_update() -> str:
    from app.db.session import SessionLocal
    from app.models import Clinic, EntryOwnerRole, EntryType, EntryVisibility, Patient, User
    from app.services.entries import create_entry_record
    from app.services.patient_publications import (
        approve_publication,
        create_publication_draft,
        publish_publication,
    )

    db = SessionLocal()
    try:
        clinic = db.scalar(select(Clinic).where(Clinic.name == "Nightingale Demo Clinic A"))
        patient = db.scalar(select(Patient).where(Patient.synthetic_display_name == "Sarah Tan"))
        staff = db.scalar(select(User).where(User.email == "staff.a@clinic-a.test"))
        clinician = db.scalar(select(User).where(User.email == "clinician.a@clinic-a.test"))
        if clinic is None or patient is None or staff is None or clinician is None:
            raise RuntimeError("Seed did not create the publication benchmark personas")
        source = create_entry_record(
            db,
            clinic_id=clinic.id,
            patient_id=patient.id,
            entry_type=EntryType.STAFF_NOTE,
            owner_role=EntryOwnerRole.STAFF,
            visibility=EntryVisibility.INTERNAL,
            content="The synthetic benchmark follow-up is ready for the patient portal.",
            created_by_user_id=staff.id,
            created_by_role="staff",
            request_id="round4-publication-benchmark-source",
            source_kind="manual",
            source_reference="round4-publication-benchmark-source",
        )
        draft = create_publication_draft(
            db,
            clinic_id=clinic.id,
            patient_id=patient.id,
            source_entry_id=source.id,
            actor=staff,
            actor_role="staff",
            request_id="round4-publication-benchmark-draft",
        )
        approved = approve_publication(
            db,
            publication=draft,
            actor=clinician,
            actor_role="clinician",
            expected_workflow_version=1,
            request_id="round4-publication-benchmark-approve",
        )
        published = publish_publication(
            db,
            publication=approved,
            actor=clinician,
            actor_role="clinician",
            expected_workflow_version=2,
            request_id="round4-publication-benchmark-publish",
        )
        return published.patient_id
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
            json={"email": "clinician.a@clinic-a.test", "password": SEED_PASSWORD},
        )
        response.raise_for_status()
        return "; ".join(f"{name}={value}" for name, value in client.cookies.items())


def measure(patient_id: str, cookie_header: str) -> dict[str, Any]:
    path = f"/patients/{patient_id}/published-care"
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
            payload = {}
        updates = payload.get("updates", []) if isinstance(payload, dict) else []
        return elapsed_ms, response.status_code, len(updates) if isinstance(updates, list) else 0

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        warmup = list(executor.map(request_once, range(WARMUP_COUNT)))
        measured = list(executor.map(request_once, range(SAMPLE_COUNT)))
    latencies = [item[0] for item in measured]
    return {
        "warmup_requests": WARMUP_COUNT,
        "request_count": SAMPLE_COUNT,
        "concurrency": CONCURRENCY,
        "p50_ms": round(percentile(latencies, 0.50), 3),
        "p95_ms": round(percentile(latencies, 0.95), 3),
        "p99_ms": round(percentile(latencies, 0.99), 3),
        "max_ms": round(max(latencies), 3),
        "error_count": sum(item[1] != 200 for item in measured),
        "warmup_error_count": sum(item[1] != 200 for item in warmup),
        "response_item_count": max(item[2] for item in measured),
    }


def main() -> None:
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()
    database_url = "sqlite:///" + DATABASE_PATH.as_posix()
    env = environment(database_url)
    os.environ.update(env)
    server: subprocess.Popen[bytes] | None = None
    try:
        run_local_command(["-m", "alembic", "upgrade", "head"], env)
        run_local_command(["-m", "app.scripts.seed_demo"], env)
        patient_id = prepare_published_update()
        server = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "--host",
                "127.0.0.1",
                "--port",
                str(urlparse(BASE_URL).port or 8011),
                "app.main:app",
            ],
            cwd=BACKEND_ROOT,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        wait_for_server(server)
        metrics = measure(patient_id, login_cookie())
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
            "endpoint": "GET /patients/{patient_id}/published-care",
            "metrics": metrics,
            "target_p95_ms": 300,
            "target_met": metrics["p95_ms"] <= 300 and metrics["error_count"] == 0,
        }
        ARTIFACT_JSON.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
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
