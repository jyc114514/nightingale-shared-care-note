"""Production URL/static-serving checks without requiring Docker or hosted resources."""

from pathlib import Path

import httpx
import pytest

from app.config import Settings, normalize_database_url
from app.main import create_app


def test_postgresql_urls_use_psycopg_without_changing_credentials_or_query() -> None:
    raw = "postgresql://demo_user:p%40ss@db.internal:5432/nightingale?sslmode=require"
    assert normalize_database_url(raw) == (
        "postgresql+psycopg://demo_user:p%40ss@db.internal:5432/nightingale?sslmode=require"
    )
    assert normalize_database_url("postgres://user:password@host/db") == (
        "postgresql+psycopg://user:password@host/db"
    )
    assert normalize_database_url("postgresql+psycopg://user:password@host/db") == (
        "postgresql+psycopg://user:password@host/db"
    )
    assert normalize_database_url("sqlite:///./nightingale.db") == "sqlite:///./nightingale.db"


def test_production_validation_requires_secure_hosting_values() -> None:
    insecure = Settings(
        app_env="production",
        session_secret="a" * 40,
        cookie_secure=False,
    )
    with pytest.raises(ValueError, match="COOKIE_SECURE"):
        insecure.validate_runtime_security()

    secure = Settings(
        app_env="production",
        database_url="postgresql://user:password@db.internal/nightingale",
        session_secret="a" * 40,
        cookie_secure=True,
        allowed_origins="https://nightingale-shared-care-note.onrender.com",
        llm_provider="fixture",
        voice_provider="disabled",
    )
    secure.validate_runtime_security()


@pytest.mark.asyncio
async def test_production_app_serves_same_origin_spa_without_catching_health(
    tmp_path: Path,
) -> None:
    (tmp_path / "assets").mkdir()
    (tmp_path / "index.html").write_text(
        "<html><body>synthetic app</body></html>", encoding="utf-8"
    )
    (tmp_path / "assets" / "main.js").write_text("console.log('safe');", encoding="utf-8")
    application = create_app(static_directory=tmp_path)
    transport = httpx.ASGITransport(app=application)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        root = await client.get("/")
        asset = await client.get("/assets/main.js")
        deep_link = await client.get("/?patient=patient-a&highlight=highlight-0")
        health = await client.get("/health")
    assert root.status_code == 200
    assert root.text == "<html><body>synthetic app</body></html>"
    assert asset.status_code == 200
    assert "console.log" in asset.text
    assert deep_link.status_code == 200
    assert deep_link.text == root.text
    assert health.status_code == 200
    assert health.json() == {"status": "ok", "phase": "4-bonus-local"}
