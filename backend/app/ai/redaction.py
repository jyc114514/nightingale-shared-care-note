"""Deterministic synthetic PHI redaction with a fail-closed second scan."""

from dataclasses import dataclass
import re
from collections.abc import Iterable


class RedactionFailure(ValueError):
    """Raised when sensitive content cannot be proven absent after redaction."""

    def __init__(self, error_code: str):
        super().__init__(error_code)
        self.error_code = error_code


@dataclass(frozen=True)
class RedactionResult:
    redacted_text: str
    replacement_counts: dict[str, int]


SG_ID_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])(?:"
    r"(?P<label>NRIC|FIN|IC|ID)\s*[:#-]?\s*"
    r")?(?P<identifier>[STFGM]\d{7}[A-Z])(?![A-Za-z0-9])",
    re.IGNORECASE,
)
PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:"
    r"\+65[\s-]*[689]\d{3}[\s-]?\d{4}"
    r"|[689]\d{3}[\s-]?\d{4}"
    r")(?!\d)"
)


def _name_pattern(known_names: Iterable[str]) -> re.Pattern[str] | None:
    names = sorted(
        {name.strip() for name in known_names if name and name.strip()},
        key=len,
        reverse=True,
    )
    if not names:
        return None
    escaped = "|".join(re.escape(name) for name in names)
    return re.compile(r"(?<![\w])(?:" + escaped + r")(?![\w])", re.IGNORECASE)


def secondary_detector(text: str, known_names: Iterable[str]) -> list[str]:
    """Return only safe category codes for sensitive matches left in text."""

    findings: list[str] = []
    name_detector = _name_pattern(known_names)
    if name_detector is not None and name_detector.search(text):
        findings.append("name")
    if SG_ID_PATTERN.search(text):
        findings.append("id")
    if PHONE_PATTERN.search(text):
        findings.append("phone")
    return findings


def redact_text(text: str, known_names: Iterable[str]) -> RedactionResult:
    """Replace supported synthetic identifiers and fail closed on leftovers."""

    if not isinstance(text, str) or not text:
        raise RedactionFailure("empty_input")
    redacted = text
    counts = {"name": 0, "id": 0, "phone": 0}
    name_pattern = _name_pattern(known_names)
    if name_pattern is not None:
        redacted, counts["name"] = name_pattern.subn("[REDACTED_NAME]", redacted)

    def replace_id(match: re.Match[str]) -> str:
        identifier = match.group("identifier")
        return match.group(0)[: -len(identifier)] + "[REDACTED_ID]"

    redacted, counts["id"] = SG_ID_PATTERN.subn(replace_id, redacted)
    redacted, counts["phone"] = PHONE_PATTERN.subn("[REDACTED_PHONE]", redacted)
    try:
        findings = secondary_detector(redacted, known_names)
    except Exception as exc:
        raise RedactionFailure("secondary_detector_failed") from exc
    if findings:
        raise RedactionFailure("sensitive_token_remaining")
    return RedactionResult(redacted_text=redacted, replacement_counts=counts)
