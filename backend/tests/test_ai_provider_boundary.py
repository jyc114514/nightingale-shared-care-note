"""Provider boundary tests: only validated redacted payloads cross the seam."""

from app.ai.provider import FixtureProvider
from app.ai.schemas import RedactedPayload


def test_fixture_provider_accepts_typed_redacted_payload_only() -> None:
    payload = RedactedPayload(
        interaction_type="ai_doctor_consult_summary",
        redacted_text="[REDACTED_NAME] reported pain [REDACTED_PHONE].",
        source_reference="synthetic-consult",
    )
    output = FixtureProvider().process(payload)
    assert output.quote == payload.redacted_text
    assert output.summary[output.start_offset : output.end_offset] == output.quote
    assert "Sarah Tan" not in output.summary
    assert "9123" not in output.summary
