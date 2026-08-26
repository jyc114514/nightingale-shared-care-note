"""Mocked contract tests for the optional DeepSeek V4 Flash provider."""

import json
from collections.abc import Callable
from typing import Any

import httpx
import pytest
from pydantic import SecretStr

from app.ai.deepseek import DeepSeekProvider, ProviderError
from app.ai.provider import (
    FixtureProvider,
    ProviderConfigurationError,
    get_provider,
    get_provider_info,
)
from app.ai.schemas import RedactedPayload
from app.config import Settings


def completion_body(
    *,
    summary: str = "The synthetic follow-up remains pending.",
    quote: str = "remains pending",
    **extra: Any,
) -> dict[str, Any]:
    suggestion = {
        "summary": summary,
        "highlight_quote": quote,
        "item_kind": "information",
        "priority_reason": "The synthetic follow-up needs clinician review.",
        "action_label": "Review synthetic suggestion",
        "action_state": "open",
        **extra,
    }
    return {
        "id": "synthetic-completion",
        "choices": [
            {
                "finish_reason": "stop",
                "message": {"role": "assistant", "content": json.dumps(suggestion)},
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
    }


def provider_for(
    handler: Callable[[httpx.Request], httpx.Response],
    *,
    max_tokens: int = 600,
) -> DeepSeekProvider:
    return DeepSeekProvider(
        SecretStr("test-deepseek-key"),
        transport=httpx.MockTransport(handler),
        max_tokens=max_tokens,
    )


def redacted_payload() -> RedactedPayload:
    return RedactedPayload(
        interaction_type="ai_nurse_consult_summary",
        redacted_text=(
            "[REDACTED_NAME] reported pain [REDACTED_ID] "
            "[REDACTED_PHONE] during a synthetic follow-up."
        ),
        source_reference="synthetic-nurse-follow-up",
    )


def test_success_sends_only_redacted_typed_input_and_computes_local_span() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json=completion_body())

    with provider_for(handler) as provider:
        output = provider.process(redacted_payload())

    assert len(requests) == 1
    request = requests[0]
    body = json.loads(request.content)
    assert request.method == "POST"
    assert str(request.url) == "https://api.deepseek.com/chat/completions"
    assert request.headers["authorization"].startswith("Bearer ")
    assert body["model"] == "deepseek-v4-flash"
    assert body["response_format"] == {"type": "json_object"}
    assert body["thinking"] == {"type": "disabled"}
    assert body["max_tokens"] == 600
    assert "source_reference" not in body
    serialized = json.dumps(body)
    assert "synthetic-nurse-follow-up" not in serialized
    assert "Sarah Tan" not in serialized
    assert "S1234567D" not in serialized
    assert "9123" not in serialized
    assert "clinic-a" not in serialized
    assert "patient-a" not in serialized
    assert "user-a" not in serialized
    assert "[REDACTED_NAME]" in serialized
    assert "[REDACTED_ID]" in serialized
    assert "[REDACTED_PHONE]" in serialized
    assert output.risk_level is None
    assert list(output.summary)[output.start_offset : output.end_offset]
    assert "".join(list(output.summary)[output.start_offset : output.end_offset]) == output.quote


def test_provider_rejects_unredacted_payload_before_network() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200, json=completion_body())

    payload = RedactedPayload(
        interaction_type="ai_doctor_consult_summary",
        redacted_text="Synthetic ID S1234567D and phone +65 9123 4567",
        source_reference="synthetic-source",
    )
    with provider_for(handler) as provider:
        with pytest.raises(ProviderError, match="provider_payload_not_redacted"):
            provider.process(payload)
    assert calls == 0


def test_provider_rejects_non_typed_payload_before_network() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200, json=completion_body())

    with provider_for(handler) as provider:
        with pytest.raises(ProviderError, match="provider_payload_invalid"):
            provider.process(object())  # type: ignore[arg-type]
    assert calls == 0


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        (completion_body(summary="No matching phrase", quote="missing"), "provider_span_invalid"),
        (completion_body(summary="pain pain", quote="pain"), "provider_span_invalid"),
        (completion_body(extra={"unsupported": True}), "provider_output_invalid"),
    ],
)
def test_provider_rejects_invalid_or_ambiguous_structured_output(
    body: dict[str, Any], expected: str
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        suggestion_content = body["choices"][0]["message"]["content"]
        return httpx.Response(
            200,
            json={
                "choices": [{"finish_reason": "stop", "message": {"content": suggestion_content}}]
            },
        )

    with provider_for(handler) as provider:
        with pytest.raises(ProviderError, match=expected):
            provider.process(redacted_payload())


@pytest.mark.parametrize(
    ("content", "finish_reason", "expected"),
    [
        ("not-json", "stop", "provider_output_invalid"),
        ("", "stop", "provider_empty_output"),
        ('{"summary":', "length", "provider_output_truncated"),
    ],
)
def test_provider_maps_empty_invalid_and_truncated_content(
    content: str, finish_reason: str, expected: str
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "finish_reason": finish_reason,
                        "message": {"content": content},
                    }
                ]
            },
        )

    with provider_for(handler) as provider:
        with pytest.raises(ProviderError, match=expected):
            provider.process(redacted_payload())


@pytest.mark.parametrize(
    ("status_code", "expected"),
    [
        (401, "provider_auth_failed"),
        (402, "provider_insufficient_balance"),
        (429, "provider_rate_limited"),
        (500, "provider_unavailable"),
    ],
)
def test_provider_maps_http_failures_and_retries_only_transient_5xx(
    status_code: int, expected: str
) -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(status_code)

    with provider_for(handler) as provider:
        with pytest.raises(ProviderError, match=expected):
            provider.process(redacted_payload())
    assert calls == (2 if status_code >= 500 else 1)


def test_provider_retries_one_timeout_then_returns_safe_code() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        raise httpx.ReadTimeout("synthetic timeout", request=request)

    with provider_for(handler) as provider:
        with pytest.raises(ProviderError, match="provider_timeout"):
            provider.process(redacted_payload())
    assert calls == 2


def test_provider_errors_never_log_raw_response_or_key(caplog: pytest.LogCaptureFixture) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, content=b"raw provider response secret-key-sentinel")

    with provider_for(handler) as provider:
        with pytest.raises(ProviderError, match="provider_unavailable"):
            provider.process(redacted_payload())
    assert "secret-key-sentinel" not in caplog.text
    assert "raw provider response" not in caplog.text


def test_provider_selection_is_fixture_by_default_and_deepseek_is_explicit() -> None:
    fixture_settings = Settings(llm_provider=None)
    assert isinstance(get_provider(fixture_settings), FixtureProvider)
    fixture_info = get_provider_info(fixture_settings)
    assert fixture_info.mode == "fixture"
    assert fixture_info.configured is True

    missing_settings = Settings(llm_provider="deepseek")
    assert get_provider_info(missing_settings).configured is False
    with pytest.raises(ProviderConfigurationError, match="provider_configuration_missing_key"):
        get_provider(missing_settings)

    unknown_settings = Settings(llm_provider="other")
    with pytest.raises(ProviderConfigurationError, match="provider_configuration_unknown"):
        get_provider(unknown_settings)

    deepseek_settings = Settings(
        llm_provider="deepseek",
        deepseek_api_key=SecretStr("test-key"),
    )
    provider = get_provider(deepseek_settings)
    assert provider.name == "deepseek-v4-flash"
    assert isinstance(provider, DeepSeekProvider)
    provider.close()
