"""Application-level health endpoint test."""

from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_uses_the_real_application() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok", "phase": "0-scaffold"}
