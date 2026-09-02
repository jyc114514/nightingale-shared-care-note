"""Provider selection with a deterministic default and optional live adapter."""

from dataclasses import dataclass
from typing import Literal, Protocol

from app.ai.deepseek import (
    DEEPSEEK_DEFAULT_BASE_URL,
    DEEPSEEK_DEFAULT_MODEL,
    DeepSeekProvider,
    ProviderError,
)
from app.ai.schemas import ProviderOutput, RedactedPayload
from app.config import Settings, settings as runtime_settings


class AIProvider(Protocol):
    """Provider implementations can only receive a validated redacted payload."""

    name: str

    def process(self, payload: RedactedPayload) -> ProviderOutput:
        """Produce a schema-validated suggestion from redacted synthetic text."""


class FixtureProvider:
    """Deterministic local fixture provider used for Gate C tests and demos."""

    name = "fixture-redacted-v1"

    def process(self, payload: RedactedPayload) -> ProviderOutput:
        prefix = "Care note suggestion: "
        summary = prefix + payload.redacted_text
        start_offset = len(prefix)
        end_offset = start_offset + len(payload.redacted_text)
        action_label = {
            "ai_doctor_consult_summary": "Review doctor suggestion",
            "ai_nurse_consult_summary": "Review nurse suggestion",
            "ai_patient_session_summary": "Review session suggestion",
        }[payload.interaction_type]
        item_kind: Literal["information", "flag"] = (
            "flag" if payload.interaction_type == "ai_patient_session_summary" else "information"
        )
        return ProviderOutput(
            summary=summary,
            quote=payload.redacted_text,
            start_offset=start_offset,
            end_offset=end_offset,
            item_kind=item_kind,
            risk_level=None,
            risk_reason="This suggestion is ready for clinician review.",
            action_label=action_label,
            action_state="open",
        )


class ProviderConfigurationError(ProviderError):
    """Raised when an explicitly selected provider is not safely configured."""


@dataclass(frozen=True)
class ProviderInfo:
    provider_name: str
    model: str
    configured: bool
    mode: Literal["fixture", "deepseek"]


def _selected_name(app_settings: Settings) -> str:
    return (app_settings.llm_provider or "fixture").strip().lower() or "fixture"


def get_provider_info(app_settings: Settings | None = None) -> ProviderInfo:
    """Return safe provider metadata without exposing a key, path, or base URL."""

    selected = _selected_name(app_settings or runtime_settings)
    if selected == "fixture":
        return ProviderInfo(
            provider_name="fixture-redacted-v1",
            model="deterministic-local",
            configured=True,
            mode="fixture",
        )
    if selected == "deepseek":
        config = app_settings or runtime_settings
        key = config.deepseek_api_key
        return ProviderInfo(
            provider_name=DEEPSEEK_DEFAULT_MODEL,
            model=config.deepseek_model,
            configured=bool(key and key.get_secret_value().strip()),
            mode="deepseek",
        )
    raise ProviderConfigurationError("provider_configuration_unknown")


def get_provider(app_settings: Settings | None = None) -> AIProvider:
    """Select fixture by default or DeepSeek only after explicit safe configuration."""

    config = app_settings or runtime_settings
    info = get_provider_info(config)
    if info.mode == "fixture":
        return FixtureProvider()
    key = config.deepseek_api_key
    if key is None or not key.get_secret_value().strip():
        raise ProviderConfigurationError("provider_configuration_missing_key")
    if config.deepseek_model != DEEPSEEK_DEFAULT_MODEL:
        raise ProviderConfigurationError("provider_configuration_invalid_model")
    return DeepSeekProvider(
        key,
        base_url=config.deepseek_base_url or DEEPSEEK_DEFAULT_BASE_URL,
        model=config.deepseek_model,
        timeout_seconds=config.deepseek_timeout_seconds,
        total_budget_seconds=config.deepseek_total_budget_seconds,
        max_attempts=config.deepseek_max_attempts,
        max_tokens=config.deepseek_max_tokens,
    )
