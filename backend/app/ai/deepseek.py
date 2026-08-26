"""Optional DeepSeek V4 Flash adapter behind the redacted provider boundary."""

from __future__ import annotations

import json
from typing import Any

import httpx
from pydantic import SecretStr, ValidationError

from app.ai.redaction import secondary_detector
from app.ai.schemas import DeepSeekSuggestion, ProviderOutput, RedactedPayload


DEEPSEEK_DEFAULT_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_DEFAULT_MODEL = "deepseek-v4-flash"
DEEPSEEK_MAX_RESPONSE_BYTES = 64 * 1024

SYSTEM_INSTRUCTION = """You are producing a small structured suggestion for a clinician review workflow.
The input is synthetic and already redacted. Return JSON only and use exactly the requested fields.
Do not diagnose. Do not recommend treatment. Do not invent facts. Preserve uncertainty.
Use only facts explicitly present in the input. The result remains a suggestion and never sets medical
risk, clinician confirmation, provenance, offsets, roles, or patient visibility.
"""

OUTPUT_SHAPE_EXAMPLE = {
    "summary": "A concise summary using only the supplied synthetic facts.",
    "highlight_quote": "An exact phrase copied from summary.",
    "item_kind": "information",
    "priority_reason": "Why this should be reviewed.",
    "action_label": None,
    "action_state": "not_applicable",
}


class ProviderError(RuntimeError):
    """A provider failure represented only by a safe, enumerable error code."""

    def __init__(self, error_code: str):
        super().__init__(error_code)
        self.error_code = error_code


class DeepSeekProvider:
    """Synchronous, bounded Chat Completions adapter for DeepSeek V4 Flash."""

    name = DEEPSEEK_DEFAULT_MODEL

    def __init__(
        self,
        api_key: SecretStr | str,
        *,
        base_url: str = DEEPSEEK_DEFAULT_BASE_URL,
        model: str = DEEPSEEK_DEFAULT_MODEL,
        timeout_seconds: float = 20.0,
        max_tokens: int = 600,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        key = api_key.get_secret_value() if isinstance(api_key, SecretStr) else api_key
        if not isinstance(key, str) or not key.strip():
            raise ProviderError("provider_configuration_missing_key")
        if timeout_seconds <= 0 or timeout_seconds > 120:
            raise ProviderError("provider_configuration_invalid_timeout")
        if max_tokens <= 0 or max_tokens > 4_096:
            raise ProviderError("provider_configuration_invalid_max_tokens")
        normalized_base_url = base_url.strip().rstrip("/")
        if not normalized_base_url:
            raise ProviderError("provider_configuration_invalid_base_url")
        if model.strip() != DEEPSEEK_DEFAULT_MODEL:
            raise ProviderError("provider_configuration_invalid_model")

        self.model = model.strip()
        self._client = httpx.Client(
            base_url=normalized_base_url,
            headers={"Authorization": f"Bearer {key.strip()}"},
            timeout=httpx.Timeout(
                timeout_seconds,
                connect=min(5.0, timeout_seconds),
            ),
            transport=transport,
        )
        self._max_tokens = max_tokens
        self.last_usage: dict[str, int] | None = None

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> DeepSeekProvider:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    @staticmethod
    def _validate_payload(payload: RedactedPayload) -> None:
        if not isinstance(payload, RedactedPayload):
            raise ProviderError("provider_payload_invalid")
        findings = secondary_detector(payload.redacted_text, [])
        if findings:
            raise ProviderError("provider_payload_not_redacted")

    def _request(self, body: dict[str, Any]) -> dict[str, Any]:
        for attempt in range(2):
            try:
                response = self._client.post("/chat/completions", json=body)
            except httpx.TimeoutException as exc:
                if attempt == 0:
                    continue
                raise ProviderError("provider_timeout") from exc
            except httpx.RequestError as exc:
                if attempt == 0:
                    continue
                raise ProviderError("provider_unavailable") from exc

            if response.status_code >= 500:
                if attempt == 0:
                    continue
                raise ProviderError("provider_unavailable")
            if response.status_code in {401, 403}:
                raise ProviderError("provider_auth_failed")
            if response.status_code == 402:
                raise ProviderError("provider_insufficient_balance")
            if response.status_code == 429:
                raise ProviderError("provider_rate_limited")
            if response.status_code >= 400:
                raise ProviderError("provider_bad_request")
            if len(response.content) > DEEPSEEK_MAX_RESPONSE_BYTES:
                raise ProviderError("provider_output_invalid")
            try:
                decoded = response.json()
            except ValueError as exc:
                raise ProviderError("provider_output_invalid") from exc
            if not isinstance(decoded, dict):
                raise ProviderError("provider_output_invalid")
            usage = decoded.get("usage")
            if isinstance(usage, dict):
                safe_usage = {
                    key: value
                    for key, value in usage.items()
                    if key in {"prompt_tokens", "completion_tokens", "total_tokens"}
                    and isinstance(value, int)
                }
                self.last_usage = safe_usage or None
            return decoded
        raise ProviderError("provider_unavailable")

    @staticmethod
    def _content(response: dict[str, Any]) -> str:
        choices = response.get("choices")
        if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
            raise ProviderError("provider_output_invalid")
        choice = choices[0]
        if choice.get("finish_reason") == "length":
            raise ProviderError("provider_output_truncated")
        message = choice.get("message")
        if not isinstance(message, dict):
            raise ProviderError("provider_output_invalid")
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ProviderError("provider_empty_output")
        return content

    @staticmethod
    def _to_provider_output(suggestion: DeepSeekSuggestion) -> ProviderOutput:
        occurrences = suggestion.summary.count(suggestion.highlight_quote)
        if occurrences == 0:
            raise ProviderError("provider_span_invalid")
        if occurrences != 1:
            raise ProviderError("provider_span_invalid")
        start_offset = suggestion.summary.find(suggestion.highlight_quote)
        if start_offset < 0:
            raise ProviderError("provider_span_invalid")
        try:
            return ProviderOutput(
                summary=suggestion.summary,
                quote=suggestion.highlight_quote,
                start_offset=start_offset,
                end_offset=start_offset + len(suggestion.highlight_quote),
                item_kind=suggestion.item_kind,
                risk_level=None,
                risk_reason=suggestion.priority_reason,
                action_label=suggestion.action_label,
                action_state=suggestion.action_state,
            )
        except ValidationError as exc:
            raise ProviderError("provider_output_invalid") from exc

    def process(self, payload: RedactedPayload) -> ProviderOutput:
        self._validate_payload(payload)
        self.last_usage = None
        user_payload = json.dumps(
            {
                "interaction_type": payload.interaction_type,
                "redacted_text": payload.redacted_text,
                "output_shape": OUTPUT_SHAPE_EXAMPLE,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
        response = self._request(
            {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": SYSTEM_INSTRUCTION},
                    {"role": "user", "content": user_payload},
                ],
                "response_format": {"type": "json_object"},
                "thinking": {"type": "disabled"},
                "temperature": 0.1,
                "max_tokens": self._max_tokens,
            }
        )
        content = self._content(response)
        try:
            suggestion = DeepSeekSuggestion.model_validate(json.loads(content))
        except (ValueError, TypeError, ValidationError) as exc:
            raise ProviderError("provider_output_invalid") from exc
        return self._to_provider_output(suggestion)
