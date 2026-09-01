"""Real application tests for source-anchored allergy assertion extraction."""

from hashlib import sha256

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    AssertionStatus,
    ClinicalAssertion,
    Entry,
    EntryOwnerRole,
    EntryType,
    EntryVersion,
    EntryVisibility,
)
from app.services.clinical_assertions import (
    extract_allergy_assertions,
    sync_assertions_for_entry_version,
)
from app.services.entries import create_entry_record, update_entry_content
from conftest import DemoData


def test_explicit_closed_vocabulary_patterns_produce_exact_candidates() -> None:
    cases = [
        ("penicillin allergy", "present", "penicillin"),
        ("allergic to penicillin", "present", "penicillin"),
        ("allergy to penicillin", "present", "penicillin"),
        ("not allergic to penicillin", "absent", "penicillin"),
        ("denies penicillin allergy", "absent", "penicillin"),
        ("no known allergies", "absent", "all_drug_allergies"),
        ("no known drug allergies", "absent", "all_drug_allergies"),
    ]
    for content, polarity, concept_key in cases:
        result = extract_allergy_assertions(content)
        assert result.abstention_reasons == ()
        assert len(result.candidates) == 1
        candidate = result.candidates[0]
        assert candidate.polarity == polarity
        assert candidate.concept_key == concept_key
        assert content[candidate.start_offset : candidate.end_offset] == candidate.quote
        assert candidate.quote_sha256 == sha256(candidate.quote.encode("utf-8")).hexdigest()


def test_unicode_prefix_uses_python_codepoint_offsets() -> None:
    content = "前缀😀：patient is allergic to penicillin."
    result = extract_allergy_assertions(content)
    assert len(result.candidates) == 1
    candidate = result.candidates[0]
    assert candidate.start_offset == content.index("allergic")
    assert content[candidate.start_offset : candidate.end_offset] == "allergic to penicillin"
    assert candidate.offset_unit == "unicode_codepoint"


def test_repeated_occurrences_keep_occurrence_specific_spans() -> None:
    content = "penicillin allergy noted; repeat penicillin allergy confirmed."
    result = extract_allergy_assertions(content)
    assert len(result.candidates) == 2
    assert [candidate.start_offset for candidate in result.candidates] == [
        content.index("penicillin allergy"),
        content.rindex("penicillin allergy"),
    ]
    assert all(
        content[candidate.start_offset : candidate.end_offset] == candidate.quote
        for candidate in result.candidates
    )


def test_ambiguous_unsupported_and_malformed_inputs_abstain_safely() -> None:
    cases = [
        ("possible penicillin allergy", "assertion_ambiguous"),
        ("family history of penicillin allergy", "assertion_ambiguous"),
        ("past penicillin allergy", "assertion_ambiguous"),
        ("cannot rule out penicillin allergy", "assertion_ambiguous"),
        ("not no known allergies", "assertion_ambiguous"),
        ("allergic to amoxicillin", "assertion_unsupported_concept"),
        ("malformed \ud800 penicillin allergy", "assertion_span_invalid"),
    ]
    for content, reason in cases:
        result = extract_allergy_assertions(content)
        assert result.candidates == ()
        assert result.abstention_reasons == (reason,)


def test_assertion_persistence_is_idempotent_and_revision_preserves_old_source(
    db_session: Session,
    demo_data: DemoData,
) -> None:
    entry = create_entry_record(
        db_session,
        clinic_id=demo_data.clinic_a.id,
        patient_id=demo_data.patient_a.id,
        entry_type=EntryType.STAFF_NOTE,
        owner_role=EntryOwnerRole.STAFF,
        visibility=EntryVisibility.INTERNAL,
        content="The patient has penicillin allergy.",
        created_by_user_id=demo_data.staff_a.id,
        created_by_role="staff",
        request_id="assertion-idempotency-create",
    )
    first = list(
        db_session.scalars(
            select(ClinicalAssertion).where(ClinicalAssertion.source_entry_id == entry.id)
        )
    )
    assert len(first) == 1
    first_assertion = first[0]
    first_version = db_session.scalar(
        select(EntryVersion).where(
            EntryVersion.entry_id == entry.id,
            EntryVersion.version_number == 1,
        )
    )
    assert first_version is not None
    rerun = sync_assertions_for_entry_version(
        db_session,
        entry=entry,
        version=first_version,
        asserted_by_role="staff",
        asserted_by_user_id=demo_data.staff_a.id,
        request_id="assertion-idempotency-rerun",
    )
    db_session.commit()
    assert len(rerun.created) == 1
    assert (
        db_session.scalar(
            select(func.count(ClinicalAssertion.id)).where(
                ClinicalAssertion.source_entry_id == entry.id
            )
        )
        == 1
    )

    updated = update_entry_content(
        db_session,
        entry=entry,
        expected_version=1,
        content="The patient has no known drug allergies.",
        actor_user_id=demo_data.staff_a.id,
        actor_role="staff",
        request_id="assertion-revision-update",
    )
    current = list(
        db_session.scalars(
            select(ClinicalAssertion)
            .where(ClinicalAssertion.source_entry_id == entry.id)
            .order_by(ClinicalAssertion.created_at, ClinicalAssertion.id)
        )
    )
    assert updated.current_version == 2
    assert len(current) == 2
    assert first_assertion.status == AssertionStatus.SUPERSEDED.value
    assert first_assertion.source_version_id != current[1].source_version_id
    assert first_assertion.quote == "penicillin allergy"
    assert current[1].quote == "no known drug allergies"
    assert current[1].status == AssertionStatus.ACTIVE.value


def test_derived_failure_does_not_lose_canonical_human_note(
    db_session: Session,
    demo_data: DemoData,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def broken_extractor(_content: str) -> object:
        raise RuntimeError("synthetic extractor failure")

    monkeypatch.setattr(
        "app.services.clinical_assertions.extract_allergy_assertions",
        broken_extractor,
    )
    entry = create_entry_record(
        db_session,
        clinic_id=demo_data.clinic_a.id,
        patient_id=demo_data.patient_a.id,
        entry_type=EntryType.STAFF_NOTE,
        owner_role=EntryOwnerRole.STAFF,
        visibility=EntryVisibility.INTERNAL,
        content="Human note remains committed.",
        created_by_user_id=demo_data.staff_a.id,
        created_by_role="staff",
        request_id="assertion-failure-human-write",
    )
    assert db_session.get(Entry, entry.id) is not None
    assert (
        db_session.scalar(
            select(func.count(ClinicalAssertion.id)).where(
                ClinicalAssertion.source_entry_id == entry.id
            )
        )
        == 0
    )
