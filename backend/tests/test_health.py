"""Application-level health endpoint test."""

import httpx
import pytest

from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint_uses_the_real_application() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "phase": "2-gate-b"}
