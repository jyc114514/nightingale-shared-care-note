"""Deterministic synthetic identifier redaction tests."""

import pytest

from app.ai.redaction import RedactionFailure, redact_text


def test_known_names_are_case_insensitive_and_do_not_match_substrings() -> None:
    result = redact_text(
        "sArAh TaN met Sarah Tanley; Sarah Tan reported pain.",
        ["Sarah Tan"],
    )
    assert result.redacted_text == (
        "[REDACTED_NAME] met Sarah Tanley; [REDACTED_NAME] reported pain."
    )
    assert result.replacement_counts["name"] == 2


def test_sg_ids_fin_and_phone_formats_are_replaced_with_stable_tokens() -> None:
    result = redact_text(
        "NRIC: S1234567D, FIN G1234567X, +65 9123 4567, +6591234567, 8123-4567.",
        [],
    )
    assert result.redacted_text == (
        "NRIC: [REDACTED_ID], FIN [REDACTED_ID], [REDACTED_PHONE], "
        "[REDACTED_PHONE], [REDACTED_PHONE]."
    )
    assert result.replacement_counts == {"name": 0, "id": 2, "phone": 3}


def test_redaction_preserves_unicode_and_fails_closed_if_second_detector_breaks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = redact_text("Dose change \U0001f600 is documented.", [])
    assert result.redacted_text == "Dose change \U0001f600 is documented."

    def broken_detector(text: str, known_names: list[str]) -> list[str]:
        del text, known_names
        raise RuntimeError("detector unavailable")

    monkeypatch.setattr("app.ai.redaction.secondary_detector", broken_detector)
    with pytest.raises(RedactionFailure, match="secondary_detector_failed"):
        redact_text("safe synthetic text", [])
