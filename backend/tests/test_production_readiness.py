"""Production URL/static-serving checks without requiring Docker or hosted resources."""

from pathlib import Path

import httpx
import pytest

from app.config import Settings, normalize_database_url
from app.ai.deepseek import DeepSeekProvider, ProviderError
from pydantic import SecretStr
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

    fixture = Settings(
        app_env="production",
        database_url="postgresql://user:password@db.internal/nightingale",
        session_secret="a" * 40,
        cookie_secure=True,
        allowed_origins="https://nightingale-shared-care-note.onrender.com",
        llm_provider="fixture",
        voice_provider="fixture",
    )
    fixture.validate_runtime_security()

    local_whisper = Settings(
        app_env="production",
        database_url="postgresql://user:password@db.internal/nightingale",
        session_secret="a" * 40,
        cookie_secure=True,
        allowed_origins="https://nightingale-shared-care-note.onrender.com",
        llm_provider="fixture",
        voice_provider="local_whisper",
    )
    with pytest.raises(ValueError, match="disabled or fixture"):
        local_whisper.validate_runtime_security()

    unknown = Settings(
        app_env="production",
        database_url="postgresql://user:password@db.internal/nightingale",
        session_secret="a" * 40,
        cookie_secure=True,
        allowed_origins="https://nightingale-shared-care-note.onrender.com",
        llm_provider="fixture",
        voice_provider="unknown",
    )
    with pytest.raises(ValueError, match="disabled, fixture, or local_whisper"):
        unknown.validate_runtime_security()


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("deepseek_total_budget_seconds", 0.09, "TOTAL_BUDGET"),
        ("deepseek_total_budget_seconds", 121, "TOTAL_BUDGET"),
        ("deepseek_max_attempts", 0, "MAX_ATTEMPTS"),
        ("deepseek_max_attempts", 4, "MAX_ATTEMPTS"),
        ("deepseek_circuit_failure_threshold", 0, "FAILURE_THRESHOLD"),
        ("deepseek_circuit_cooldown_seconds", 0, "COOLDOWN_SECONDS"),
    ],
)
def test_external_provider_resilience_settings_are_bounded(
    field: str, value: float | int, message: str
) -> None:
    settings = Settings()
    setattr(settings, field, value)
    with pytest.raises(ValueError, match=message):
        settings.validate_runtime_security()


def test_deepseek_provider_rejects_invalid_budget_and_attempt_count() -> None:
    with pytest.raises(ProviderError, match="invalid_total_budget"):
        DeepSeekProvider(
            SecretStr("synthetic-key"),
            total_budget_seconds=0.09,
        )
    with pytest.raises(ProviderError, match="invalid_max_attempts"):
        DeepSeekProvider(
            SecretStr("synthetic-key"),
            max_attempts=4,
        )


def test_render_configuration_keeps_voice_fixture_outside_the_docker_image() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    dockerfile = (repository_root / "Dockerfile").read_text(encoding="utf-8").lower()
    render_blueprint = (repository_root / "render.yaml").read_text(encoding="utf-8")
    assert "requirements.voice.lock" not in dockerfile
    assert "faster-whisper" not in dockerfile
    assert "voice_model_cache" not in dockerfile
    assert "key: VOICE_PROVIDER\n        value: fixture" in render_blueprint
    assert "key: LLM_PROVIDER\n        value: fixture" in render_blueprint
    assert "DEEPSEEK" not in render_blueprint


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
