"""Deterministic, source-anchored evidence for the bounded publication slice."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re

from app.models import (
    PatientPublicationEvidence,
    PatientPublicationSeverity,
    PublicationEvidenceStatus,
    PublicationEvidenceType,
)


SUPPORTED_DOSAGE_RE = re.compile(
    r"(?P<concept>\bmetformin)\s+(?P<value>\d+)\s*(?P<unit>mg)\s+"
    r"(?P<frequency>once daily|twice daily)\b",
    re.IGNORECASE,
)
DOSAGE_LIKE_RE = re.compile(
    r"\b(?P<concept>[A-Za-z][A-Za-z-]*)\s+"
    r"(?P<value>\d+(?:\.\d+)?)\s*"
    r"(?P<unit>mg|mcg|micrograms?|g|units?)\b",
    re.IGNORECASE,
)
NUMBER_UNIT_RE = re.compile(
    r"\b\d+(?:\.\d+)?(?:\s*[-–]\s*\d+(?:\.\d+)?)?\s*"
    r"(?:mg|mcg|micrograms?|g|units?)\b",
    re.IGNORECASE,
)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class DosageObservation:
    status: PublicationEvidenceStatus
    concept_key: str | None = None
    normalized_value: str | None = None
    unit: str | None = None
    frequency: str | None = None
    start_offset: int = 0
    end_offset: int = 0
    quote: str = ""


@dataclass(frozen=True)
class DosageValidation:
    status: PublicationEvidenceStatus
    severity_class: PatientPublicationSeverity
    source: DosageObservation
    draft: DosageObservation


def _observation_from_match(
    match: re.Match[str],
    *,
    status: PublicationEvidenceStatus = PublicationEvidenceStatus.MATCHED,
) -> DosageObservation:
    groups = match.groupdict()
    return DosageObservation(
        status=status,
        concept_key=groups.get("concept", "").lower() or None,
        normalized_value=groups.get("value"),
        unit=(groups.get("unit") or "").lower() or None,
        frequency=(groups.get("frequency") or "").lower() or None,
        start_offset=len(list(match.string[: match.start()])),
        end_offset=len(list(match.string[: match.end()])),
        quote=match.group(0),
    )


def extract_dosage(text: str) -> DosageObservation:
    """Extract only the exact supported metformin dosage grammar.

    Offsets are Python/Unicode codepoint offsets. Anything outside the deliberately
    small grammar is retained as a blocking observation rather than normalized.
    """

    supported = list(SUPPORTED_DOSAGE_RE.finditer(text))
    dosage_like = list(DOSAGE_LIKE_RE.finditer(text))
    if len(supported) > 1 or len(dosage_like) > 1:
        match = dosage_like[0] if dosage_like else supported[0]
        return _observation_from_match(match, status=PublicationEvidenceStatus.AMBIGUOUS)
    if supported:
        return _observation_from_match(supported[0])
    if dosage_like:
        return _observation_from_match(dosage_like[0], status=PublicationEvidenceStatus.UNSUPPORTED)
    if NUMBER_UNIT_RE.search(text):
        return DosageObservation(status=PublicationEvidenceStatus.UNSUPPORTED)
    return DosageObservation(status=PublicationEvidenceStatus.MISSING)


def compare_dosage(source_content: str, draft_content: str) -> DosageValidation:
    source = extract_dosage(source_content)
    draft = extract_dosage(draft_content)
    if source.status is PublicationEvidenceStatus.MATCHED:
        status: PublicationEvidenceStatus
        if draft.status is not PublicationEvidenceStatus.MATCHED:
            status = (
                draft.status
                if draft.status
                in {
                    PublicationEvidenceStatus.AMBIGUOUS,
                    PublicationEvidenceStatus.UNSUPPORTED,
                }
                else PublicationEvidenceStatus.MISMATCH
            )
        elif (
            source.concept_key != draft.concept_key
            or source.normalized_value != draft.normalized_value
            or source.unit != draft.unit
            or source.frequency != draft.frequency
        ):
            status = PublicationEvidenceStatus.MISMATCH
        else:
            status = PublicationEvidenceStatus.MATCHED
        return DosageValidation(
            status=status,
            severity_class=PatientPublicationSeverity.MEDICATION_DOSAGE,
            source=source,
            draft=draft,
        )

    if source.status is PublicationEvidenceStatus.MISSING:
        status = (
            PublicationEvidenceStatus.MISSING
            if draft.status is PublicationEvidenceStatus.MISSING
            else draft.status
        )
        return DosageValidation(
            status=status,
            severity_class=PatientPublicationSeverity.GENERAL,
            source=source,
            draft=draft,
        )

    return DosageValidation(
        status=source.status,
        severity_class=PatientPublicationSeverity.MEDICATION_DOSAGE,
        source=source,
        draft=draft,
    )


def evidence_row(
    *,
    publication_id: str,
    publication_version_id: str,
    source_entry_id: str,
    source_version_id: str,
    validation: DosageValidation,
) -> PatientPublicationEvidence:
    source = validation.source
    return PatientPublicationEvidence(
        publication_id=publication_id,
        publication_version_id=publication_version_id,
        evidence_type=PublicationEvidenceType.MEDICATION_DOSAGE,
        concept_key=source.concept_key or "none",
        normalized_value=source.normalized_value,
        unit=source.unit,
        frequency=source.frequency,
        source_entry_id=source_entry_id,
        source_version_id=source_version_id,
        start_offset=source.start_offset,
        end_offset=source.end_offset,
        quote=source.quote,
        quote_sha256=sha256_text(source.quote),
        offset_unit="unicode_codepoint",
        validation_status=validation.status,
    )
