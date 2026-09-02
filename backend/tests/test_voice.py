"""Real-application checks for the Level-C synthetic voice path."""

from dataclasses import replace
from hashlib import sha256
import builtins
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from sqlalchemy import select

from app.config import Settings
from app.services.authorization import get_patient_context
from app.services.voice import (
    VoiceProviderError,
    get_voice_provider,
    inspect_audio_fixture,
    process_voice_session,
)
from app.voice.fixtures import CLINICAL_SAMPLE, PATIENT_SAMPLE
from app.voice.providers import FasterWhisperProvider, TranscriptResult
from app.models import TranscriptSegment, VoiceSession


async def login(client: Any, email: str) -> None:
    response = await client.post(
        "/auth/login",
        json={"email": email, "password": "test-password-only"},
    )
    assert response.status_code == 200, response.text


@pytest.mark.asyncio
async def test_voice_samples_and_audio_are_role_scoped(
    client: Any, test_settings: Settings, demo_data: Any
) -> None:
    test_settings.voice_provider = "fixture"
    patient_id = demo_data.patient_a.id

    await login(client, "staff@clinic-a.test")
    provider = await client.get("/voice/provider")
    assert provider.status_code == 200
    assert provider.json()["mode"] == "fixture"
    assert provider.json()["enabled"] is True
    samples = await client.get(f"/patients/{patient_id}/voice/samples")
    assert samples.status_code == 200
    assert [row["sample_id"] for row in samples.json()] == ["nurse-follow-up"]
    audio = await client.get(
        f"/patients/{patient_id}/voice/samples/{CLINICAL_SAMPLE.sample_id}/audio"
    )
    assert audio.status_code == 200
    assert audio.headers["content-type"].startswith("audio/wav")
    assert len(audio.content) == CLINICAL_SAMPLE.audio_path.stat().st_size
    patient_sample = await client.get(
        f"/patients/{patient_id}/voice/samples/{PATIENT_SAMPLE.sample_id}/audio"
    )
    assert patient_sample.status_code == 403

    client.cookies.clear()
    await login(client, "patient@clinic-a.test")
    patient_samples = await client.get(f"/patients/{patient_id}/voice/samples")
    assert patient_samples.status_code == 200
    assert [row["sample_id"] for row in patient_samples.json()] == ["patient-follow-up"]
    internal_audio = await client.get(
        f"/patients/{patient_id}/voice/samples/{CLINICAL_SAMPLE.sample_id}/audio"
    )
    assert internal_audio.status_code == 403

    client.cookies.clear()
    await login(client, "staff@clinic-b.test")
    cross_clinic = await client.get(f"/patients/{patient_id}/voice/samples")
    assert cross_clinic.status_code == 404


@pytest.mark.asyncio
async def test_voice_audio_requires_authentication(
    client: Any, test_settings: Settings, demo_data: Any
) -> None:
    test_settings.voice_provider = "fixture"
    provider = await client.get("/voice/provider")
    assert provider.status_code == 401
    response = await client.get(
        f"/patients/{demo_data.patient_a.id}/voice/samples/{CLINICAL_SAMPLE.sample_id}/audio"
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_voice_disabled_is_explicit_and_does_not_crash(
    client: Any, test_settings: Settings, demo_data: Any
) -> None:
    test_settings.voice_provider = "disabled"
    await login(client, "staff@clinic-a.test")
    provider = await client.get("/voice/provider")
    assert provider.status_code == 200
    assert provider.json() == {
        "provider_name": "disabled",
        "model": "none",
        "mode": "disabled",
        "enabled": False,
        "disclosure": "Voice is disabled in this environment.",
    }
    patient_id = demo_data.patient_a.id
    samples = await client.get(f"/patients/{patient_id}/voice/samples")
    assert samples.status_code == 200
    assert samples.json() == []
    process = await client.post(
        f"/patients/{patient_id}/voice/sessions",
        json={"sample_id": CLINICAL_SAMPLE.sample_id, "idempotency_key": "voice-disabled"},
    )
    assert process.status_code == 503
    assert process.json()["detail"] == "voice_provider_disabled"


@pytest.mark.asyncio
async def test_staff_voice_fixture_creates_immutable_transcript_and_source(
    client: Any,
    test_settings: Settings,
    demo_data: Any,
    caplog: pytest.LogCaptureFixture,
) -> None:
    test_settings.voice_provider = "fixture"
    await login(client, "staff@clinic-a.test")
    patient_id = demo_data.patient_a.id
    payload = {
        "sample_id": CLINICAL_SAMPLE.sample_id,
        "idempotency_key": "voice-test-clinical-1",
    }
    created = await client.post(f"/patients/{patient_id}/voice/sessions", json=payload)
    assert created.status_code == 200, created.text
    body = created.json()
    assert body["status"] == "completed"
    assert body["patient_safe"] is False
    assert body["asr_provider"] == "mock-transcript-fixture"
    assert body["asr_model"] == "precomputed-v1"
    assert body["audio_duration_ms"] == 24000
    assert len(body["audio_sha256"]) == 64
    assert body["entry_id"]
    assert body["highlight_id"]
    assert body["source_segment_id"] == body["segments"][0]["id"]
    assert len(body["segments"]) == 3
    assert all(segment["confidence"] is None for segment in body["segments"])
    assert all(segment["start_ms"] < segment["end_ms"] for segment in body["segments"])
    assert [segment["segment_index"] for segment in body["segments"]] == [0, 1, 2]
    assert "This is a synthetic nurse follow-up" not in caplog.text

    fetched = await client.get(f"/patients/{patient_id}/voice/sessions/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["segments"] == body["segments"]
    repeated = await client.post(f"/patients/{patient_id}/voice/sessions", json=payload)
    assert repeated.status_code == 200
    assert repeated.json()["id"] == body["id"]


@pytest.mark.asyncio
async def test_patient_voice_is_limited_to_patient_sample_and_hides_internal_source(
    client: Any, test_settings: Settings, demo_data: Any
) -> None:
    test_settings.voice_provider = "fixture"
    await login(client, "patient@clinic-a.test")
    patient_id = demo_data.patient_a.id
    created = await client.post(
        f"/patients/{patient_id}/voice/sessions",
        json={
            "sample_id": PATIENT_SAMPLE.sample_id,
            "idempotency_key": "voice-test-patient-1",
        },
    )
    assert created.status_code == 200, created.text
    body = created.json()
    assert body["patient_safe"] is True
    assert body["status"] == "completed"
    assert body["entry_id"] is None
    assert body["highlight_id"] is None
    assert len(body["segments"]) == 3
    denied = await client.post(
        f"/patients/{patient_id}/voice/sessions",
        json={
            "sample_id": CLINICAL_SAMPLE.sample_id,
            "idempotency_key": "voice-test-patient-clinical",
        },
    )
    assert denied.status_code == 403

    fetched = await client.get(f"/patients/{patient_id}/voice/sessions/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["patient_safe"] is True
    timeline = await client.get(f"/patients/{patient_id}/timeline")
    assert timeline.status_code == 200
    assert all(
        row["entry_type"] in {"patient_facing_summary", "patient_instruction"}
        for row in timeline.json()
    )


def test_audio_hash_and_duration_are_bound_to_synthetic_fixture() -> None:
    metadata = inspect_audio_fixture(PATIENT_SAMPLE)
    assert metadata.duration_ms == PATIENT_SAMPLE.duration_ms
    assert metadata.sha256 == sha256(PATIENT_SAMPLE.audio_path.read_bytes()).hexdigest()
    missing = replace(PATIENT_SAMPLE, audio_filename="missing.wav")
    with pytest.raises(VoiceProviderError, match="audio_fixture_missing"):
        inspect_audio_fixture(missing)


def test_fixture_provider_does_not_import_optional_asr(monkeypatch: pytest.MonkeyPatch) -> None:
    original_import = builtins.__import__

    def guarded_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "faster_whisper" or name.startswith("faster_whisper."):
            raise AssertionError("fixture provider must not import faster-whisper")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    provider = get_voice_provider(Settings(voice_provider="fixture"))
    result = provider.transcribe(PATIENT_SAMPLE.audio_path, PATIENT_SAMPLE)
    assert result.language == "en"
    assert len(result.segments) == 3
    assert all(segment.confidence is None for segment in result.segments)


def test_faster_whisper_adapter_is_unit_testable_without_model_download() -> None:
    fake_model = SimpleNamespace(
        transcribe=lambda *args, **kwargs: (
            iter(
                [
                    SimpleNamespace(
                        start=0.0,
                        end=1.5,
                        text=" hello",
                        words=[
                            SimpleNamespace(probability=0.8),
                            SimpleNamespace(probability=0.9),
                        ],
                    )
                ]
            ),
            SimpleNamespace(language="en", language_probability=0.99),
        )
    )
    provider = FasterWhisperProvider(model=fake_model)
    result = provider.transcribe(Path("synthetic.wav"), PATIENT_SAMPLE)
    assert isinstance(result, TranscriptResult)
    assert result.word_timestamps_available is True
    assert result.confidence_available is True
    assert result.segments[0].start_ms == 0
    assert result.segments[0].end_ms == 1500
    assert result.segments[0].confidence == pytest.approx(0.85)


@pytest.mark.asyncio
async def test_asr_failure_has_safe_status_and_no_summary(
    db_session: Any,
    test_settings: Settings,
    demo_data: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FailingProvider:
        name = "faster-whisper"
        model = "turbo"

        def transcribe(self, audio_path: Path, sample: Any) -> None:
            raise VoiceProviderError("asr_inference_failed")

    def failing_provider(settings: Settings) -> FailingProvider:
        del settings
        return FailingProvider()

    monkeypatch.setattr("app.services.voice.get_voice_provider", failing_provider)
    context = get_patient_context(db_session, demo_data.staff_a, demo_data.patient_a.id)
    session = process_voice_session(
        db_session,
        context=context,
        sample=CLINICAL_SAMPLE,
        idempotency_key="voice-test-asr-failure",
        request_id="voice-test-request",
        app_settings=test_settings,
    )
    assert session.status == "failed_asr"
    assert session.error_code == "asr_inference_failed"
    assert session.entry_id is None
    assert (
        db_session.scalar(
            select(TranscriptSegment).where(TranscriptSegment.voice_session_id == session.id)
        )
        is None
    )


@pytest.mark.asyncio
async def test_provider_failure_preserves_local_transcript(
    db_session: Any, test_settings: Settings, demo_data: Any
) -> None:
    test_settings.voice_provider = "fixture"
    test_settings.llm_provider = "deepseek"
    test_settings.deepseek_api_key = None
    context = get_patient_context(db_session, demo_data.staff_a, demo_data.patient_a.id)
    session = process_voice_session(
        db_session,
        context=context,
        sample=CLINICAL_SAMPLE,
        idempotency_key="voice-test-provider-failure",
        request_id="voice-test-request-provider",
        app_settings=test_settings,
    )
    assert session.status == "failed_provider"
    assert session.error_code == "provider_configuration_missing_key"
    assert (
        db_session.scalar(
            select(TranscriptSegment).where(TranscriptSegment.voice_session_id == session.id)
        )
        is not None
    )
    assert (
        db_session.scalar(select(VoiceSession).where(VoiceSession.id == session.id)).entry_id
        is None
    )
