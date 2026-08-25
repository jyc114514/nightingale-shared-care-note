"""Typed deterministic provider interface; no network or external model adapter."""

from typing import Literal, Protocol

from app.ai.schemas import ProviderOutput, RedactedPayload


class AIProvider(Protocol):
    """Provider implementations can only receive a validated redacted payload."""

    name: str

    def process(self, payload: RedactedPayload) -> ProviderOutput:
        """Produce a schema-validated suggestion from redacted synthetic text."""


class FixtureProvider:
    """Deterministic local fixture provider used for Gate C tests and demos."""

    name = "fixture-redacted-v1"

    def process(self, payload: RedactedPayload) -> ProviderOutput:
        prefix = "Fixture suggestion: "
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
            risk_reason="Synthetic fixture output requires clinician review.",
            action_label=action_label,
            action_state="open",
        )


def get_provider() -> AIProvider:
    """Return the only local provider; a real external adapter is out of scope."""

    return FixtureProvider()
