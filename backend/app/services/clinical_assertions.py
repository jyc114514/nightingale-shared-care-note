"""Closed-vocabulary, source-anchored allergy assertion extraction."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import utcnow
from app.models import (
    AssertionCriticality,
    AssertionDomain,
    AssertionPolarity,
    AssertionStatus,
    AssertionVerificationStatus,
    ClinicalAssertion,
    Entry,
    EntryVersion,
)
from app.services.entries import record_audit


SUPPORTED_CONCEPT = "penicillin"
GENERAL_NEGATIVE_CONCEPT = "all_drug_allergies"
OFFSET_UNIT = "unicode_codepoint"


@dataclass(frozen=True)
class AllergyAssertionCandidate:
    """One exact, deterministic assertion candidate from an immutable text value."""

    domain: str
    concept_key: str
    polarity: str
    start_offset: int
    end_offset: int
    quote: str
    quote_sha256: str
    offset_unit: str = OFFSET_UNIT
    verification_status: str = AssertionVerificationStatus.UNCONFIRMED.value
    criticality: str = AssertionCriticality.UNABLE_TO_ASSESS.value


@dataclass(frozen=True)
class ExtractionResult:
    """Accepted candidates plus safe reasons for refusing ambiguous text."""

    candidates: tuple[AllergyAssertionCandidate, ...]
    abstention_reasons: tuple[str, ...] = ()

    @property
    def assertions(self) -> tuple[AllergyAssertionCandidate, ...]:
        """Compatibility alias for callers that describe candidates as assertions."""

        return self.candidates

    @property
    def accepted_candidates(self) -> tuple[AllergyAssertionCandidate, ...]:
        return self.candidates

    @property
    def abstained(self) -> bool:
        return bool(self.abstention_reasons)


@dataclass(frozen=True)
class AssertionSyncResult:
    """Persistence outcome; callers own the surrounding commit boundary."""

    extraction: ExtractionResult
    created: tuple[ClinicalAssertion, ...]
    superseded_count: int
    conflict_ids: tuple[str, ...]


@dataclass(frozen=True)
class _Pattern:
    polarity: str
    concept_key: str
    expression: re.Pattern[str]


_PATTERNS = (
    _Pattern(
        AssertionPolarity.ABSENT.value,
        SUPPORTED_CONCEPT,
        re.compile(r"(?<!\w)not\s+allergic\s+to\s+penicillin(?!\w)", re.IGNORECASE),
    ),
    _Pattern(
        AssertionPolarity.ABSENT.value,
        SUPPORTED_CONCEPT,
        re.compile(r"(?<!\w)denies\s+penicillin\s+allergy(?!\w)", re.IGNORECASE),
    ),
    _Pattern(
        AssertionPolarity.ABSENT.value,
        GENERAL_NEGATIVE_CONCEPT,
        re.compile(r"(?<!\w)no\s+known\s+drug\s+allerg(?:y|ies)(?!\w)", re.IGNORECASE),
    ),
    _Pattern(
        AssertionPolarity.ABSENT.value,
        GENERAL_NEGATIVE_CONCEPT,
        re.compile(r"(?<!\w)no\s+known\s+allerg(?:y|ies)(?!\w)", re.IGNORECASE),
    ),
    _Pattern(
        AssertionPolarity.PRESENT.value,
        SUPPORTED_CONCEPT,
        re.compile(r"(?<!\w)penicillin\s+allerg(?:y|ies)(?!\w)", re.IGNORECASE),
    ),
    _Pattern(
        AssertionPolarity.PRESENT.value,
        SUPPORTED_CONCEPT,
        re.compile(r"(?<!\w)allergic\s+to\s+penicillin(?!\w)", re.IGNORECASE),
    ),
    _Pattern(
        AssertionPolarity.PRESENT.value,
        SUPPORTED_CONCEPT,
        re.compile(r"(?<!\w)allerg(?:y|ies)\s+to\s+penicillin(?!\w)", re.IGNORECASE),
    ),
)

_SUPPORTED_ALLERGY_PHRASE = (
    r"(?:penicillin\s+allerg(?:y|ies)|"
    r"allergic\s+to\s+penicillin|"
    r"allerg(?:y|ies)\s+to\s+penicillin)"
)
_AMBIGUOUS_PATTERNS = (
    re.compile(
        rf"(?i)\b(?:possible|suspected|probable|maybe)\b.{{0,80}}\b{_SUPPORTED_ALLERGY_PHRASE}\b"
    ),
    re.compile(rf"(?i)\bfamily\s+history\b.{{0,80}}\b{_SUPPORTED_ALLERGY_PHRASE}\b"),
    re.compile(
        rf"(?i)\b(?:history\s+of|past|previous|remote)\b.{{0,80}}\b{_SUPPORTED_ALLERGY_PHRASE}\b"
    ),
    re.compile(rf"(?i)\bcannot\s+rule\s+out\b.{{0,80}}\b{_SUPPORTED_ALLERGY_PHRASE}\b"),
    re.compile(r"(?i)\b(?:not|never|without)\s+(?:no|none|never)\b.{0,80}\ballerg"),
    re.compile(r"(?i)\bno\b.{0,40}\bnot\b.{0,40}\ballerg"),
)

_UNSUPPORTED_PREFIX = re.compile(
    r"(?i)\b(?:allergic|allergy|allergies)\s+to\s+"
    r"(?P<substance>[a-z][a-z-]{2,})\b"
)
_UNSUPPORTED_SUFFIX = re.compile(r"(?i)\b(?P<substance>[a-z][a-z-]{2,})\s+allerg(?:y|ies)\b")
_IGNORED_SUBSTANCES = frozenset({"known", "drug", "history"})


def _invalid_unicode(text: str) -> bool:
    return any(0xD800 <= ord(character) <= 0xDFFF for character in text)


def _unsupported_concept(text: str) -> bool:
    for expression in (_UNSUPPORTED_PREFIX, _UNSUPPORTED_SUFFIX):
        for match in expression.finditer(text):
            substance = match.group("substance").lower()
            if substance != SUPPORTED_CONCEPT and substance not in _IGNORED_SUBSTANCES:
                return True
    return False


def _candidate(pattern: _Pattern, match: re.Match[str]) -> AllergyAssertionCandidate:
    quote = match.group(0)
    start = match.start()
    end = match.end()
    return AllergyAssertionCandidate(
        domain=AssertionDomain.ALLERGY.value,
        concept_key=pattern.concept_key,
        polarity=pattern.polarity,
        start_offset=start,
        end_offset=end,
        quote=quote,
        quote_sha256=sha256(quote.encode("utf-8")).hexdigest(),
    )


def _select_non_overlapping(
    matches: list[AllergyAssertionCandidate],
) -> tuple[tuple[AllergyAssertionCandidate, ...], bool]:
    """Prefer the most specific enclosing match and reject partial ambiguity."""

    ordered = sorted(
        matches,
        key=lambda item: (item.start_offset, -(item.end_offset - item.start_offset)),
    )
    selected: list[AllergyAssertionCandidate] = []
    for item in ordered:
        overlaps = [
            existing
            for existing in selected
            if item.start_offset < existing.end_offset and existing.start_offset < item.end_offset
        ]
        if not overlaps:
            selected.append(item)
            continue
        if all(
            existing.start_offset <= item.start_offset and item.end_offset <= existing.end_offset
            for existing in overlaps
        ):
            continue
        if all(
            item.start_offset <= existing.start_offset and existing.end_offset <= item.end_offset
            for existing in overlaps
        ):
            selected = [existing for existing in selected if existing not in overlaps]
            selected.append(item)
            continue
        return (), True
    selected.sort(key=lambda item: (item.start_offset, item.end_offset, item.polarity))
    return tuple(selected), False


def extract_allergy_assertions(content: str) -> ExtractionResult:
    """Extract only explicit penicillin assertions, abstaining when meaning is unsafe."""

    if not isinstance(content, str) or not content:
        return ExtractionResult((), ("assertion_span_invalid",))
    if _invalid_unicode(content):
        return ExtractionResult((), ("assertion_span_invalid",))
    try:
        content.encode("utf-8")
    except UnicodeEncodeError:
        return ExtractionResult((), ("assertion_span_invalid",))

    if any(expression.search(content) for expression in _AMBIGUOUS_PATTERNS):
        return ExtractionResult((), ("assertion_ambiguous",))
    if _unsupported_concept(content):
        return ExtractionResult((), ("assertion_unsupported_concept",))

    matches = [
        _candidate(pattern, match)
        for pattern in _PATTERNS
        for match in pattern.expression.finditer(content)
    ]
    selected, has_overlap_ambiguity = _select_non_overlapping(matches)
    if has_overlap_ambiguity or len({item.polarity for item in selected}) > 1:
        return ExtractionResult((), ("assertion_ambiguous",))

    for item in selected:
        if (
            item.start_offset < 0
            or item.end_offset <= item.start_offset
            or item.end_offset > len(content)
            or content[item.start_offset : item.end_offset] != item.quote
        ):
            return ExtractionResult((), ("assertion_span_invalid",))
    return ExtractionResult(selected)


def sync_assertions_for_entry_version(
    db: Session,
    *,
    entry: Entry,
    version: EntryVersion,
    asserted_by_role: str,
    asserted_by_user_id: str | None,
    request_id: str,
) -> AssertionSyncResult:
    """Derive one version after it is committed; no canonical text is ever replaced."""

    if version.entry_id != entry.id or version.version_number != entry.current_version:
        raise ValueError("Assertion source version is not the current entry version")

    existing = list(
        db.scalars(
            select(ClinicalAssertion).where(ClinicalAssertion.source_version_id == version.id)
        )
    )
    if existing:
        return AssertionSyncResult(ExtractionResult(()), tuple(existing), 0, ())

    extraction = extract_allergy_assertions(version.content)
    now = utcnow()
    prior_active = list(
        db.scalars(
            select(ClinicalAssertion).where(
                ClinicalAssertion.source_entry_id == entry.id,
                ClinicalAssertion.status == AssertionStatus.ACTIVE.value,
            )
        )
    )
    for prior in prior_active:
        prior.status = AssertionStatus.SUPERSEDED
        prior.superseded_at = now
        prior.updated_at = now
        record_audit(
            db,
            clinic_id=entry.clinic_id,
            patient_id=entry.patient_id,
            actor_user_id=asserted_by_user_id,
            actor_role=asserted_by_role,
            action="clinical_assertion_superseded",
            entity_type="clinical_assertion",
            entity_id=prior.id,
            request_id=request_id,
        )

    created: list[ClinicalAssertion] = []
    for candidate in extraction.candidates:
        assertion = ClinicalAssertion(
            clinic_id=entry.clinic_id,
            patient_id=entry.patient_id,
            domain=candidate.domain,
            concept_key=candidate.concept_key,
            polarity=candidate.polarity,
            verification_status=candidate.verification_status,
            criticality=candidate.criticality,
            source_entry_id=entry.id,
            source_version_id=version.id,
            start_offset=candidate.start_offset,
            end_offset=candidate.end_offset,
            quote=candidate.quote,
            quote_sha256=candidate.quote_sha256,
            offset_unit=candidate.offset_unit,
            asserted_by_role=asserted_by_role,
            asserted_by_user_id=asserted_by_user_id,
            status=AssertionStatus.ACTIVE.value,
            created_at=now,
            updated_at=now,
        )
        db.add(assertion)
        created.append(assertion)
    db.flush()

    for assertion in created:
        record_audit(
            db,
            clinic_id=entry.clinic_id,
            patient_id=entry.patient_id,
            actor_user_id=asserted_by_user_id,
            actor_role=asserted_by_role,
            action="clinical_assertion_created",
            entity_type="clinical_assertion",
            entity_id=assertion.id,
            request_id=request_id,
        )
    for reason in extraction.abstention_reasons:
        record_audit(
            db,
            clinic_id=entry.clinic_id,
            patient_id=entry.patient_id,
            actor_user_id=asserted_by_user_id,
            actor_role=asserted_by_role,
            action=f"clinical_assertion_abstained_{reason}",
            entity_type="entry",
            entity_id=entry.id,
            request_id=request_id,
        )

    from app.services.clinical_conflicts import recompute_clinical_conflicts

    conflict_ids = recompute_clinical_conflicts(
        db,
        clinic_id=entry.clinic_id,
        patient_id=entry.patient_id,
        request_id=request_id,
    )
    return AssertionSyncResult(
        extraction=extraction,
        created=tuple(created),
        superseded_count=len(prior_active),
        conflict_ids=tuple(conflict_ids),
    )


def sync_entry_assertions_safely(
    db: Session,
    *,
    entry: Entry,
    version: EntryVersion,
    request_id: str,
) -> AssertionSyncResult | None:
    """Keep a successful canonical write if derived assertion work fails."""

    clinic_id = entry.clinic_id
    patient_id = entry.patient_id
    entry_id = entry.id
    actor_user_id = version.created_by_user_id
    actor_role = version.created_by_role
    try:
        result = sync_assertions_for_entry_version(
            db,
            entry=entry,
            version=version,
            asserted_by_role=actor_role,
            asserted_by_user_id=actor_user_id,
            request_id=request_id,
        )
        db.commit()
        return result
    except Exception:
        db.rollback()
        record_audit(
            db,
            clinic_id=clinic_id,
            patient_id=patient_id,
            actor_user_id=actor_user_id,
            actor_role=actor_role,
            action="clinical_assertion_sync_failed",
            entity_type="entry",
            entity_id=entry_id,
            request_id=request_id,
        )
        db.commit()
        return None
