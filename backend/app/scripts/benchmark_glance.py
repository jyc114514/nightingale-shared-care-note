"""Measure the current deterministic Glance endpoint without a provider call.

This is an exploratory Gate B measurement, not the Gate C materialized-read benchmark.
It uses the real FastAPI application through HTTPX ASGITransport and prints only aggregate
timings and counts.
"""

import asyncio
import json
import os
import time
from statistics import quantiles

import httpx

from app.main import app


async def measure() -> dict[str, float | int | str]:
    password = os.environ.get("DEMO_SEED_PASSWORD")
    if not password:
        raise SystemExit("DEMO_SEED_PASSWORD must be set for the local benchmark")

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://benchmark") as client:
        login = await client.post(
            "/auth/login",
            json={"email": "staff.a@clinic-a.test", "password": password},
        )
        login.raise_for_status()
        patients = await client.get("/patients")
        patients.raise_for_status()
        patient_id = patients.json()[0]["id"]

        path = f"/patients/{patient_id}/glance"
        for _ in range(20):
            response = await client.get(path)
            response.raise_for_status()

        durations_ms: list[float] = []
        for _ in range(100):
            started = time.perf_counter()
            response = await client.get(path)
            response.raise_for_status()
            durations_ms.append((time.perf_counter() - started) * 1000)

    ordered = sorted(durations_ms)
    p95 = quantiles(ordered, n=20, method="inclusive")[18]
    return {
        "path": path,
        "transport": "httpx ASGITransport",
        "warmup_requests": 20,
        "measured_requests": len(ordered),
        "glance_items": len(response.json()),
        "p50_ms": round(ordered[49], 3),
        "p95_ms": round(p95, 3),
        "max_ms": round(ordered[-1], 3),
    }


if __name__ == "__main__":
    print(json.dumps(asyncio.run(measure()), sort_keys=True))
