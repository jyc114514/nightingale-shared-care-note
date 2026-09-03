"""Real application tests for allergy conflicts, safety floors, and adjudication."""

from dataclasses import dataclass
from hashlib import sha256

import httpx
import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    AssertionVerificationStatus,
    AuditLog,
    ClinicalAssertion,
    ClinicalConflict,
    ClinicalConflictStatus,
    Entry,
    EntryOwnerRole,
    EntryType,
    EntryVersion,
    EntryVisibility,
    Highlight,
    HighlightFeedbackEvent,
    ImportanceProfile,
    PatientGlanceItem,
    HighlightStatus,
)
from app.services.entries import create_entry_record, update_entry_content
from app.services.highlights import create_highlight_record
from conftest import DemoData, TEST_PASSWORD


async def login(client: httpx.AsyncClient, email: str) -> None:
    response = await client.post("/auth/login", json={"email": email, "password": TEST_PASSWORD})
    assert response.status_code == 200, response.text


@dataclass(frozen=True)
class ConflictFixture:
    positive_entry: Entry
    negative_entry: Entry
    conflict: ClinicalConflict
    positive: ClinicalAssertion
    negative: ClinicalAssertion
    highlight: Highlight


def make_conflict(db: Session, demo_data: DemoData) -> ConflictFixture:
    positive_entry = create_entry_record(
        db,
        clinic_id=demo_data.clinic_a.id,
        patient_id=demo_data.patient_a.id,
        entry_type=EntryType.STAFF_NOTE,
        owner_role=EntryOwnerRole.STAFF,
        visibility=EntryVisibility.INTERNAL,
        content="Nurse records penicillin allergy.",
        created_by_user_id=demo_data.staff_a.id,
        created_by_role="staff",
        request_id="clinical-conflict-positive",
        source_kind="manual",
        source_reference="synthetic-nurse-note",
    )
    negative_entry = create_entry_record(
        db,
        clinic_id=demo_data.clinic_a.id,
        patient_id=demo_data.patient_a.id,
        entry_type=EntryType.AI_PATIENT_SESSION_SUMMARY,
        owner_role=EntryOwnerRole.SYSTEM,
        visibility=EntryVisibility.INTERNAL,
        content="Patient reports no known drug allergies.",
        created_by_user_id=None,
        created_by_role="system",
        request_id="clinical-conflict-negative",
        source_kind="patient_ai_session",
        source_reference="synthetic-patient-session-allergy",
    )
    conflict = db.scalar(
        select(ClinicalConflict)
        .where(
            ClinicalConflict.clinic_id == demo_data.clinic_a.id,
            ClinicalConflict.patient_id == demo_data.patient_a.id,
        )
        .order_by(ClinicalConflict.created_at, ClinicalConflict.id)
    )
    assert conflict is not None
    positive = db.get(ClinicalAssertion, conflict.positive_assertion_id)
    negative = db.get(ClinicalAssertion, conflict.negative_assertion_id)
    highlight = db.scalar(select(Highlight).where(Highlight.clinical_conflict_id == conflict.id))
    assert positive is not None and negative is not None and highlight is not None
    return ConflictFixture(positive_entry, negative_entry, conflict, positive, negative, highlight)


@pytest.mark.asyncio
async def test_conflict_has_dual_provenance_protected_glance_floor_and_safe_api(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    fixture = make_conflict(db_session, demo_data)
    projection = db_session.get(PatientGlanceItem, fixture.highlight.id)
    assert projection is not None
    assert fixture.conflict.status == ClinicalConflictStatus.OPEN.value
    assert fixture.highlight.safety_class == "allergy_conflict"
    assert fixture.highlight.safety_floor == 95.0
    assert projection.safety_class == "allergy_conflict"
    assert projection.safety_floor == 95.0
    assert projection.display_priority >= 95.0
    explanation = __import__("json").loads(projection.ranking_explanation)
    assert explanation["safety_floor"] == 95.0
    assert explanation["floor_applied"] == 1.0

    await login(client, "staff@clinic-a.test")
    listing = await client.get(f"/patients/{demo_data.patient_a.id}/clinical-conflicts")
    assert listing.status_code == 200, listing.text
    payload = listing.json()
    assert len(payload) == 1
    row = payload[0]
    assert row["positive_assertion"]["source_entry_id"] == fixture.positive.source_entry_id
    assert row["negative_assertion"]["source_entry_id"] == fixture.negative.source_entry_id
    assert row["positive_assertion"]["quote"] == "penicillin allergy"
    assert row["negative_assertion"]["quote"] == "no known drug allergies"
    assert row["positive_assertion"]["start_offset"] >= 0
    assert row["negative_assertion"]["end_offset"] > row["negative_assertion"]["start_offset"]
    audit_rows = list(
        db_session.scalars(
            select(AuditLog).where(
                AuditLog.entity_type.in_(["clinical_assertion", "clinical_conflict", "highlight"])
            )
        )
    )
    assert audit_rows
    assert all(
        not hasattr(audit, field)
        for audit in audit_rows
        for field in ("quote", "content", "raw_text")
    )


@pytest.mark.asyncio
async def test_protected_conflict_survives_six_higher_priority_ordinary_items(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    fixture = make_conflict(db_session, demo_data)
    ordinary_entries = [
        demo_data.patient_summary,
        demo_data.patient_instruction,
        demo_data.staff_note,
        demo_data.clinician_section,
        demo_data.ai_summary,
        demo_data.ai_doctor,
    ]
    for index, entry in enumerate(ordinary_entries):
        version = db_session.scalar(
            select(EntryVersion).where(
                EntryVersion.entry_id == entry.id,
                EntryVersion.version_number == 1,
            )
        )
        assert version is not None
        create_highlight_record(
            db_session,
            source_version_id=version.id,
            start_offset=0,
            end_offset=len(version.content),
            quote=version.content,
            item_kind="information",
            status=HighlightStatus.SUGGESTED,
            display_priority=100,
            risk_level=None,
            risk_reason="Ordinary synthetic attention item",
            action_label=f"Review ordinary item {index}",
            action_state="open",
            created_by_role="system",
            created_by_user_id=None,
            request_id=f"protected-first-ordinary-{index}",
            commit=False,
        )
    db_session.commit()

    await login(client, "staff@clinic-a.test")
    response = await client.get(f"/patients/{demo_data.patient_a.id}/glance")

    assert response.status_code == 200, response.text
    items = response.json()
    assert len(items) == 6
    assert items[0]["clinical_conflict_id"] == fixture.conflict.id
    assert items[0]["safety_class"] == "allergy_conflict"
    assert items[0]["display_priority"] == 95.0
    assert len({item["id"] for item in items}) == 6


@pytest.mark.asyncio
async def test_assertion_source_endpoint_revalidates_exact_span_after_source_edit(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    fixture = make_conflict(db_session, demo_data)
    await login(client, "staff@clinic-a.test")
    first = await client.get(f"/clinical-assertions/{fixture.positive.id}/source")
    assert first.status_code == 200, first.text
    body = first.json()
    assert body["source_entry_id"] == fixture.positive.source_entry_id
    assert body["source_version_id"] == fixture.positive.source_version_id
    assert body["version_content"] == "Nurse records penicillin allergy."
    assert body["quote"] == "penicillin allergy"
    assert body["quote_sha256"] == sha256(body["quote"].encode("utf-8")).hexdigest()
    assert body["source_is_current_version"] is True

    updated = update_entry_content(
        db_session,
        entry=fixture.positive_entry,
        expected_version=1,
        content="Nurse records a penicillin allergy.",
        actor_user_id=demo_data.staff_a.id,
        actor_role="staff",
        request_id="assertion-source-edit",
    )
    assert updated.current_version == 2
    old_source = await client.get(f"/clinical-assertions/{fixture.positive.id}/source")
    assert old_source.status_code == 200, old_source.text
    old_body = old_source.json()
    assert old_body["version_content"] == "Nurse records penicillin allergy."
    assert old_body["source_is_current_version"] is False
    assert old_body["version_number"] == 1


@pytest.mark.asyncio
async def test_corrupt_assertion_provenance_returns_safe_error_without_quote_details(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    fixture = make_conflict(db_session, demo_data)
    assertion = db_session.get(ClinicalAssertion, fixture.positive.id)
    assert assertion is not None
    assertion.quote = "forged clinical content"
    db_session.commit()
    await login(client, "staff@clinic-a.test")
    response = await client.get(f"/clinical-assertions/{fixture.positive.id}/source")
    assert response.status_code == 422
    assert response.json()["detail"] == "Clinical assertion source could not be verified"
    assert "forged clinical content" not in response.text


@pytest.mark.asyncio
async def test_generic_highlight_review_cannot_handle_clinical_conflict(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    fixture = make_conflict(db_session, demo_data)
    await login(client, "clinician@clinic-a.test")
    response = await client.patch(
        f"/highlights/{fixture.highlight.id}/review",
        json={"status": "accepted"},
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "Clinical conflicts require adjudication"
    db_session.expire_all()
    highlight = db_session.get(Highlight, fixture.highlight.id)
    assert highlight is not None
    assert highlight.status == "conflict_review"


@pytest.mark.asyncio
async def test_conflict_detection_is_idempotent_and_clinic_patient_scoped(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    fixture = make_conflict(db_session, demo_data)
    version = db_session.scalar(
        select(EntryVersion).where(EntryVersion.id == fixture.negative.source_version_id)
    )
    assert version is not None
    from app.services.clinical_assertions import sync_assertions_for_entry_version

    rerun = sync_assertions_for_entry_version(
        db_session,
        entry=fixture.negative_entry,
        version=version,
        asserted_by_role="system",
        asserted_by_user_id=None,
        request_id="clinical-conflict-rerun",
    )
    db_session.commit()
    assert rerun.created
    assert (
        db_session.scalar(
            select(func.count(ClinicalConflict.id)).where(
                ClinicalConflict.patient_id == demo_data.patient_a.id
            )
        )
        == 1
    )

    create_entry_record(
        db_session,
        clinic_id=demo_data.clinic_b.id,
        patient_id=demo_data.patient_b.id,
        entry_type=EntryType.STAFF_NOTE,
        owner_role=EntryOwnerRole.STAFF,
        visibility=EntryVisibility.INTERNAL,
        content="Clinic B records penicillin allergy.",
        created_by_user_id=demo_data.staff_b.id,
        created_by_role="staff",
        request_id="clinic-b-positive-only",
    )
    assert (
        db_session.scalar(
            select(func.count(ClinicalConflict.id)).where(
                ClinicalConflict.patient_id == demo_data.patient_b.id
            )
        )
        == 0
    )

    await login(client, "staff@clinic-b.test")
    foreign = await client.get(f"/patients/{demo_data.patient_a.id}/clinical-conflicts")
    assert foreign.status_code == 404


@pytest.mark.asyncio
async def test_patient_is_denied_and_only_clinician_can_adjudicate(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    fixture = make_conflict(db_session, demo_data)
    await login(client, "patient@clinic-a.test")
    patient_read = await client.get(f"/patients/{demo_data.patient_a.id}/clinical-conflicts")
    assert patient_read.status_code == 403
    patient_detail = await client.get(f"/clinical-conflicts/{fixture.conflict.id}")
    assert patient_detail.status_code == 403

    await login(client, "staff@clinic-a.test")
    staff_write = await client.patch(
        f"/clinical-conflicts/{fixture.conflict.id}/adjudicate",
        json={"expected_version": 1, "resolution": "confirmed_present"},
    )
    assert staff_write.status_code == 403
    staff_read = await client.get(f"/clinical-conflicts/{fixture.conflict.id}")
    assert staff_read.status_code == 200


@pytest.mark.asyncio
async def test_confirmed_present_keeps_sources_and_protects_confirmed_item(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    fixture = make_conflict(db_session, demo_data)
    await login(client, "clinician@clinic-a.test")
    response = await client.patch(
        f"/clinical-conflicts/{fixture.conflict.id}/adjudicate",
        json={"expected_version": 1, "resolution": "confirmed_present"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "adjudicated"
    assert body["resolution"] == "confirmed_present"
    assert body["version"] == 2
    db_session.expire_all()
    positive = db_session.get(ClinicalAssertion, fixture.positive.id)
    negative = db_session.get(ClinicalAssertion, fixture.negative.id)
    highlight = db_session.get(Highlight, fixture.highlight.id)
    assert positive is not None and negative is not None and highlight is not None
    assert positive.verification_status == AssertionVerificationStatus.CONFIRMED.value
    assert negative.verification_status == AssertionVerificationStatus.REFUTED.value
    assert highlight.status == "accepted"
    assert highlight.safety_class == "confirmed_allergy"
    assert highlight.safety_floor == 95.0
    source = await client.get(f"/highlights/{highlight.id}/source")
    assert source.status_code == 200
    assert source.json()["version_content"] == "Nurse records penicillin allergy."


@pytest.mark.asyncio
async def test_confirmed_absent_supersedes_protected_glance_item(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    fixture = make_conflict(db_session, demo_data)
    await login(client, "clinician@clinic-a.test")
    response = await client.patch(
        f"/clinical-conflicts/{fixture.conflict.id}/adjudicate",
        json={"expected_version": 1, "resolution": "confirmed_absent"},
    )
    assert response.status_code == 200, response.text
    db_session.expire_all()
    conflict = db_session.get(ClinicalConflict, fixture.conflict.id)
    positive = db_session.get(ClinicalAssertion, fixture.positive.id)
    negative = db_session.get(ClinicalAssertion, fixture.negative.id)
    highlight = db_session.get(Highlight, fixture.highlight.id)
    assert conflict is not None and positive is not None and negative is not None
    assert highlight is not None
    assert conflict.status == ClinicalConflictStatus.ADJUDICATED.value
    assert positive.verification_status == AssertionVerificationStatus.REFUTED.value
    assert negative.verification_status == AssertionVerificationStatus.CONFIRMED.value
    assert highlight.status == "superseded"
    glance = await client.get(f"/patients/{demo_data.patient_a.id}/glance")
    assert glance.status_code == 200
    assert all(item.get("clinical_conflict_id") != fixture.conflict.id for item in glance.json())


@pytest.mark.asyncio
async def test_needs_more_information_stays_open_and_stale_adjudication_is_409(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    fixture = make_conflict(db_session, demo_data)
    await login(client, "clinician@clinic-a.test")
    first = await client.patch(
        f"/clinical-conflicts/{fixture.conflict.id}/adjudicate",
        json={"expected_version": 1, "resolution": "needs_more_information"},
    )
    assert first.status_code == 200, first.text
    assert first.json()["status"] == "open"
    assert first.json()["version"] == 2
    stale = await client.patch(
        f"/clinical-conflicts/{fixture.conflict.id}/adjudicate",
        json={"expected_version": 1, "resolution": "confirmed_absent"},
    )
    assert stale.status_code == 409
    detail = stale.json()["detail"]
    assert detail["actual_version"] == 2
    assert detail["attempted_resolution"] == "confirmed_absent"
    db_session.expire_all()
    conflict = db_session.get(ClinicalConflict, fixture.conflict.id)
    highlight = db_session.get(Highlight, fixture.highlight.id)
    assert conflict is not None and highlight is not None
    assert conflict.status == "open"
    assert highlight.status == "conflict_review"
    assert highlight.safety_floor == 95.0


@pytest.mark.asyncio
async def test_entered_in_error_preserves_canonical_sources_and_hides_flag(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    fixture = make_conflict(db_session, demo_data)
    await login(client, "clinician@clinic-a.test")
    response = await client.patch(
        f"/clinical-conflicts/{fixture.conflict.id}/adjudicate",
        json={"expected_version": 1, "resolution": "entered_in_error"},
    )
    assert response.status_code == 200, response.text
    db_session.expire_all()
    positive = db_session.get(ClinicalAssertion, fixture.positive.id)
    negative = db_session.get(ClinicalAssertion, fixture.negative.id)
    highlight = db_session.get(Highlight, fixture.highlight.id)
    assert positive is not None and negative is not None and highlight is not None
    assert positive.verification_status == AssertionVerificationStatus.ENTERED_IN_ERROR.value
    assert negative.verification_status == AssertionVerificationStatus.ENTERED_IN_ERROR.value
    assert highlight.status == "superseded"
    assert db_session.get(Entry, fixture.positive_entry.id) is not None
    assert db_session.get(EntryVersion, fixture.positive.source_version_id) is not None


@pytest.mark.asyncio
async def test_protected_feedback_is_recorded_but_does_not_train_profile(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    fixture = make_conflict(db_session, demo_data)
    await login(client, "clinician@clinic-a.test")
    response = None
    for index in range(10):
        response = await client.post(
            f"/highlights/{fixture.highlight.id}/feedback",
            json={
                "event_type": "rejected",
                "idempotency_key": f"protected-reject-{index}",
            },
        )
        assert response.status_code == 200, response.text
    assert response is not None
    body = response.json()
    assert body["applied_to_profile"] is False
    assert body["suppression_reason"] == "protected_safety_class"
    assert body["profile"] is None
    assert body["ranking_explanation"]["safety_floor"] == 95.0
    assert body["ranking_explanation"]["final"] >= 95.0
    assert db_session.scalar(select(func.count(ImportanceProfile.id))) == 0
    event = db_session.scalar(
        select(HighlightFeedbackEvent).where(
            HighlightFeedbackEvent.highlight_id == fixture.highlight.id
        )
    )
    assert event is not None
    assert event.applied_to_profile is False
    assert event.suppression_reason == "protected_safety_class"


def test_source_edit_supersedes_derived_assertion_and_preserves_old_provenance(
    db_session: Session,
    demo_data: DemoData,
) -> None:
    fixture = make_conflict(db_session, demo_data)
    updated = update_entry_content(
        db_session,
        entry=fixture.positive_entry,
        expected_version=1,
        content="Nurse records no known allergies.",
        actor_user_id=demo_data.staff_a.id,
        actor_role="staff",
        request_id="clinical-conflict-source-edit",
    )
    db_session.expire_all()
    old_assertion = db_session.get(ClinicalAssertion, fixture.positive.id)
    old_conflict = db_session.get(ClinicalConflict, fixture.conflict.id)
    old_highlight = db_session.get(Highlight, fixture.highlight.id)
    old_source = db_session.get(EntryVersion, fixture.positive.source_version_id)
    assert updated.current_version == 2
    assert old_assertion is not None
    assert old_conflict is not None
    assert old_highlight is not None
    assert old_source is not None
    assert old_assertion.status == "superseded"
    assert old_conflict.status == "superseded"
    assert old_highlight.status == "superseded"
    assert old_source.content == "Nurse records penicillin allergy."


@pytest.mark.asyncio
async def test_external_payload_cannot_set_safety_fields(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    entry = create_entry_record(
        db_session,
        clinic_id=demo_data.clinic_a.id,
        patient_id=demo_data.patient_a.id,
        entry_type=EntryType.STAFF_NOTE,
        owner_role=EntryOwnerRole.STAFF,
        visibility=EntryVisibility.INTERNAL,
        content="Ordinary note for safety payload test.",
        created_by_user_id=demo_data.staff_a.id,
        created_by_role="staff",
        request_id="safety-payload-entry",
    )
    version = db_session.scalar(select(EntryVersion).where(EntryVersion.entry_id == entry.id))
    assert version is not None
    await login(client, "clinician@clinic-a.test")
    response = await client.post(
        f"/entry-versions/{version.id}/highlights",
        json={
            "start_offset": 0,
            "end_offset": 8,
            "quote": "Ordinary",
            "item_kind": "flag",
            "display_priority": 20,
            "risk_reason": "Safety payload test",
            "safety_class": "allergy_conflict",
            "safety_floor": 100,
            "clinical_conflict_id": "forged",
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["safety_class"] is None
    assert body["safety_floor"] is None
    assert body["clinical_conflict_id"] is None
