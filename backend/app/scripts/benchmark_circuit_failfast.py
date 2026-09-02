"""Measure circuit-open AI submission latency with no provider calls after opening."""

from __future__ import annotations

import asyncio
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

import httpx


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = REPOSITORY_ROOT / "backend"
DATABASE_PATH = REPOSITORY_ROOT / ".uv-cache" / "round3-circuit-benchmark.sqlite"
BASE_URL = "http://testserver"
PASSWORD = "round3-circuit-benchmark-password"
SAMPLES = 100


def percentile(values: list[float], quantile: float) -> float:
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil(quantile * len(ordered)) - 1))
    return ordered[index]


def environment(database_url: str) -> dict[str, str]:
    return {
        **os.environ,
        "APP_ENV": "test",
        "DATABASE_URL": database_url,
        "DEMO_SEED_PASSWORD": PASSWORD,
        "SESSION_SECRET": "round3-circuit-benchmark-session-secret-32",
        "COOKIE_SECURE": "false",
        "ALLOWED_ORIGINS": "http://testserver",
        "LLM_PROVIDER": "deepseek",
        "DEEPSEEK_API_KEY": "synthetic-test-key",
        "DEEPSEEK_CIRCUIT_FAILURE_THRESHOLD": "3",
        "DEEPSEEK_CIRCUIT_COOLDOWN_SECONDS": "60",
    }


def run_local(arguments: list[str], env: dict[str, str]) -> None:
    subprocess.run(
        [sys.executable, *arguments],
        cwd=BACKEND_ROOT,
        env=env,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


async def measure() -> dict[str, Any]:
    from app.ai.deepseek import ProviderError
    from app.services import ai_processing
    from app.main import app

    provider_calls = 0

    class FailingProvider:
        name = "deepseek-v4-flash"

        def process(self, payload: object) -> object:
            nonlocal provider_calls
            del payload
            provider_calls += 1
            raise ProviderError("provider_unavailable")

    setattr(ai_processing, "get_provider", lambda *_args, **_kwargs: FailingProvider())
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=BASE_URL) as client:
        login = await client.post(
            "/auth/login",
            json={"email": "staff.a@clinic-a.test", "password": PASSWORD},
        )
        login.raise_for_status()
        patients = await client.get("/patients")
        patients.raise_for_status()
        patient_id = patients.json()[0]["id"]
        path = f"/patients/{patient_id}/ai-processing"
        for index in range(3):
            response = await client.post(
                path,
                json={
                    "interaction_type": "ai_doctor_consult_summary",
                    "text": f"Synthetic bootstrap failure {index}",
                    "source_reference": f"synthetic-bootstrap-{index}",
                    "idempotency_key": f"round3-bootstrap-{index}",
                },
            )
            if (
                response.status_code != 200
                or response.json().get("error_code") != "provider_unavailable"
            ):
                raise RuntimeError("Circuit bootstrap did not produce the expected safe failure")
        latencies: list[float] = []
        errors = 0
        for index in range(SAMPLES):
            started = time.perf_counter()
            response = await client.post(
                path,
                json={
                    "interaction_type": "ai_doctor_consult_summary",
                    "text": f"Synthetic circuit-open sample {index}",
                    "source_reference": f"synthetic-circuit-sample-{index}",
                    "idempotency_key": f"round3-sample-{index}",
                },
            )
            latencies.append((time.perf_counter() - started) * 1000)
            body = response.json()
            if response.status_code != 200 or body.get("error_code") != "provider_circuit_open":
                errors += 1
        return {
            "request_count": SAMPLES,
            "error_count": errors,
            "provider_calls_during_measured_open_window": provider_calls - 3,
            "bootstrap_provider_calls": 3,
            "p50_ms": round(percentile(latencies, 0.50), 3),
            "p95_ms": round(percentile(latencies, 0.95), 3),
            "p99_ms": round(percentile(latencies, 0.99), 3),
            "max_ms": round(max(latencies), 3),
            "target_p95_ms": 300,
            "target_met": errors == 0 and percentile(latencies, 0.95) <= 300,
            "transport": "in-process HTTPX ASGITransport; synthetic provider was opened first",
        }


def main() -> None:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATABASE_PATH.unlink(missing_ok=True)
    database_url = "sqlite:///" + DATABASE_PATH.as_posix()
    env = environment(database_url)
    os.environ.update(env)
    try:
        run_local(["-m", "alembic", "upgrade", "head"], env)
        run_local(["-m", "app.scripts.seed_demo"], env)
        result = asyncio.run(measure())
        print(json.dumps(result, indent=2, sort_keys=True))
    finally:
        DATABASE_PATH.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
