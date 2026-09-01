"""Round 4 patient-publication safety gate tests through the real API."""

import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    AuditLog,
    Entry,
    EntryOwnerRole,
    EntryType,
    EntryVisibility,
    PatientPublication,
    PatientPublicationEvidence,
    PatientPublicationVersion,
)
from app.services.entries import create_entry_record
from app.services.publication_evidence import compare_dosage, extract_dosage
from conftest import DemoData, TEST_PASSWORD


async def login(client: httpx.AsyncClient, email: str) -> None:
    response = await client.post("/auth/login", json={"email": email, "password": TEST_PASSWORD})
    assert response.status_code == 200, response.text


def make_dosage_source(
    db: Session, demo_data: DemoData, content: str = "Continue metformin 500 mg twice daily."
) -> Entry:
    return create_entry_record(
        db,
        clinic_id=demo_data.clinic_a.id,
        patient_id=demo_data.patient_a.id,
        entry_type=EntryType.STAFF_NOTE,
        owner_role=EntryOwnerRole.STAFF,
        visibility=EntryVisibility.INTERNAL,
        content=content,
        created_by_user_id=demo_data.staff_a.id,
        created_by_role="staff",
        request_id="test-publication-source",
        source_kind="manual",
        source_reference="test-medication-source",
    )


@pytest.mark.asyncio
async def test_dosage_slice_is_deterministic_and_codepoint_anchored() -> None:
    source = "Continue metformin 500 mg twice daily."
    observation = extract_dosage(source)
    assert observation.status.value == "matched"
    assert observation.quote == "metformin 500 mg twice daily"
    assert source[observation.start_offset : observation.end_offset] == observation.quote
    assert extract_dosage("Take metformin 500 mg as needed.").status.value == "unsupported"
    assert (
        extract_dosage("Take metformin 500 mg and metformin 250 mg twice daily.").status.value
        == "ambiguous"
    )
    assert extract_dosage("Continue metformin.").status.value == "missing"


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        ("Take metformin 500 mg once daily.", "matched"),
        ("Take metformin 500 mg twice daily.", "matched"),
        ("Take metformin 500 mg as needed.", "unsupported"),
        ("Take metformin 500.5 mg twice daily.", "unsupported"),
        ("Take metformin 500 mcg twice daily.", "unsupported"),
        ("Take metformin 500 mg.", "unsupported"),
        ("Take metformin 500 mg twice per day.", "unsupported"),
        ("Take metformin 500-1000 mg twice daily.", "unsupported"),
        ("Take metformin 500 mg twice daily and metformin 250 mg once daily.", "ambiguous"),
        ("Take amoxicillin 500 mg twice daily.", "unsupported"),
        ("Continue metformin.", "missing"),
        ("The synthetic follow-up plan is ready.", "missing"),
    ],
)
def test_dosage_boundary_cases_are_fail_closed(content: str, expected: str) -> None:
    assert extract_dosage(content).status.value == expected


@pytest.mark.parametrize(
    ("source", "draft", "expected", "severity"),
    [
        (
            "Continue metformin 500 mg twice daily.",
            "Take metformin 500 mg twice daily.",
            "matched",
            "medication_dosage",
        ),
        (
            "Continue metformin 500 mg twice daily.",
            "Take metformin 1000 mg twice daily.",
            "mismatch",
            "medication_dosage",
        ),
        (
            "Continue metformin 500 mg twice daily.",
            "Take the medication as directed.",
            "mismatch",
            "medication_dosage",
        ),
        (
            "Continue metformin 500 mg twice daily.",
            "Take metformin 500 mg as needed.",
            "unsupported",
            "medication_dosage",
        ),
        (
            "Continue metformin 500 mg twice daily.",
            "Take metformin 500 mg twice daily and metformin 250 mg once daily.",
            "ambiguous",
            "medication_dosage",
        ),
        ("The synthetic plan is ready.", "The synthetic plan is ready.", "missing", "general"),
        (
            "The synthetic plan is ready.",
            "Take metformin 500 mg twice daily.",
            "unsupported",
            "general",
        ),
        (
            "Take amoxicillin 500 mg twice daily.",
            "Take amoxicillin 500 mg twice daily.",
            "unsupported",
            "medication_dosage",
        ),
    ],
)
def test_dosage_comparison_matrix_is_explicit(
    source: str, draft: str, expected: str, severity: str
) -> None:
    validation = compare_dosage(source, draft)
    assert validation.status.value == expected
    assert validation.severity_class.value == severity


@pytest.mark.asyncio
async def test_wrong_dosage_is_internal_only_and_accept_is_not_publish(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    source = make_dosage_source(db_session, demo_data)
    await login(client, "staff@clinic-a.test")
    created = await client.post(
        f"/entries/{source.id}/patient-publications",
        json={"content": "Take metformin 1000 mg twice daily."},
    )
    assert created.status_code == 200, created.text
    draft = created.json()
    assert draft["state"] == "draft"
    assert draft["dosage"]["status"] == "mismatch"
    assert draft["source"]["quote"] == "metformin 500 mg twice daily"
    assert draft["source"]["source_is_current_version"] is True

    repeated = await client.post(f"/entries/{source.id}/patient-publications", json={})
    assert repeated.status_code == 200
    assert repeated.json()["id"] == draft["id"]
    assert repeated.json()["content_version"] == 1

    staff_approve = await client.post(
        f"/patient-publications/{draft['id']}/approve",
        json={"expected_workflow_version": 1},
    )
    assert staff_approve.status_code == 403

    await login(client, "clinician@clinic-a.test")
    blocked = await client.post(
        f"/patient-publications/{draft['id']}/approve",
        json={"expected_workflow_version": 1},
    )
    assert blocked.status_code == 422
    assert "dosage" in blocked.text.lower()
    patient_projection = await client.get(f"/patients/{demo_data.patient_a.id}/published-care")
    assert patient_projection.status_code == 200
    assert patient_projection.json() == {"updates": []}

    await login(client, "patient@clinic-a.test")
    patient_detail = await client.get(f"/patient-publications/{draft['id']}")
    assert patient_detail.status_code == 403
    patient_timeline = await client.get(f"/patients/{demo_data.patient_a.id}/timeline")
    assert patient_timeline.status_code == 200
    assert all("metformin" not in row["content"].lower() for row in patient_timeline.json())


@pytest.mark.asyncio
async def test_corrected_dosage_requires_clinician_approval_then_explicit_publish(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    source = make_dosage_source(db_session, demo_data)
    await login(client, "staff@clinic-a.test")
    created = await client.post(
        f"/entries/{source.id}/patient-publications",
        json={"content": "Take metformin 1000 mg twice daily."},
    )
    publication = created.json()
    edited = await client.patch(
        f"/patient-publications/{publication['id']}",
        json={
            "expected_workflow_version": publication["workflow_version"],
            "content": "Take metformin 500 mg twice daily.",
        },
    )
    assert edited.status_code == 200, edited.text
    corrected = edited.json()
    assert corrected["state"] == "draft"
    assert corrected["content_version"] == 2
    assert corrected["dosage"]["status"] == "matched"
    assert len(corrected["versions"]) == 2
    assert len(corrected["evidence"]) == 2

    await login(client, "clinician@clinic-a.test")
    approved = await client.post(
        f"/patient-publications/{publication['id']}/approve",
        json={"expected_workflow_version": corrected["workflow_version"]},
    )
    assert approved.status_code == 200, approved.text
    approved_body = approved.json()
    assert approved_body["state"] == "clinician_approved"
    assert approved_body["approved_content_version"] == 2

    before_publish = await client.get(f"/patients/{demo_data.patient_a.id}/published-care")
    assert before_publish.json() == {"updates": []}
    published = await client.post(
        f"/patient-publications/{publication['id']}/publish",
        json={"expected_workflow_version": approved_body["workflow_version"]},
    )
    assert published.status_code == 200, published.text
    assert published.json()["state"] == "published"
    care = await client.get(f"/patients/{demo_data.patient_a.id}/published-care")
    assert care.status_code == 200
    updates = care.json()["updates"]
    assert len(updates) == 1
    assert updates[0] == {
        "kind": "published",
        "published_at": updates[0]["published_at"],
        "content": "Take metformin 500 mg twice daily.",
        "notice": None,
    }
    assert "source_entry_id" not in updates[0]
    assert "workflow_version" not in updates[0]


@pytest.mark.asyncio
async def test_source_change_after_approval_blocks_publish_and_preserves_patient_empty(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    source = make_dosage_source(db_session, demo_data)
    await login(client, "staff@clinic-a.test")
    created = await client.post(
        f"/entries/{source.id}/patient-publications",
        json={"content": "Take metformin 500 mg twice daily."},
    )
    publication = created.json()
    await login(client, "clinician@clinic-a.test")
    approved = await client.post(
        f"/patient-publications/{publication['id']}/approve",
        json={"expected_workflow_version": 1},
    )
    assert approved.status_code == 200

    await login(client, "staff@clinic-a.test")
    changed = await client.patch(
        f"/entries/{source.id}",
        json={
            "expected_version": 1,
            "new_content": "Continue metformin 750 mg twice daily.",
        },
    )
    assert changed.status_code == 200, changed.text
    await login(client, "clinician@clinic-a.test")
    blocked = await client.post(
        f"/patient-publications/{publication['id']}/publish",
        json={"expected_workflow_version": approved.json()["workflow_version"]},
    )
    assert blocked.status_code == 409
    assert blocked.json()["detail"]["source_changed"] is True
    assert (await client.get(f"/patients/{demo_data.patient_a.id}/published-care")).json() == {
        "updates": []
    }


@pytest.mark.asyncio
async def test_recall_and_correction_replace_patient_projection_without_erasing_history(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    source = make_dosage_source(db_session, demo_data)
    await login(client, "clinician@clinic-a.test")
    created = await client.post(
        f"/entries/{source.id}/patient-publications",
        json={"content": "Take metformin 500 mg twice daily."},
    )
    publication = created.json()
    approved = await client.post(
        f"/patient-publications/{publication['id']}/approve",
        json={"expected_workflow_version": 1},
    )
    published = await client.post(
        f"/patient-publications/{publication['id']}/publish",
        json={"expected_workflow_version": approved.json()["workflow_version"]},
    )
    assert published.status_code == 200
    recalled = await client.post(
        f"/patient-publications/{publication['id']}/recall",
        json={
            "expected_workflow_version": published.json()["workflow_version"],
            "reason_code": "clinical_correction",
        },
    )
    assert recalled.status_code == 200
    assert recalled.json()["state"] == "recalled"
    withdrawn = await client.get(f"/patients/{demo_data.patient_a.id}/published-care")
    assert withdrawn.json()["updates"] == [
        {
            "kind": "withdrawn",
            "published_at": withdrawn.json()["updates"][0]["published_at"],
            "content": None,
            "notice": "This care update was withdrawn by the clinic. Contact the clinic if you have questions.",
        }
    ]

    correction = await client.post(f"/patient-publications/{publication['id']}/corrections")
    assert correction.status_code == 200, correction.text
    correction_body = correction.json()
    assert correction_body["state"] == "draft"
    changed = await client.patch(
        f"/patient-publications/{correction_body['id']}",
        json={
            "expected_workflow_version": correction_body["workflow_version"],
            "content": "Please take metformin 500 mg twice daily.",
        },
    )
    assert changed.status_code == 200
    correction_approved = await client.post(
        f"/patient-publications/{correction_body['id']}/approve",
        json={"expected_workflow_version": changed.json()["workflow_version"]},
    )
    assert correction_approved.status_code == 200
    correction_published = await client.post(
        f"/patient-publications/{correction_body['id']}/publish",
        json={"expected_workflow_version": correction_approved.json()["workflow_version"]},
    )
    assert correction_published.status_code == 200
    assert correction_published.json()["state"] == "published"
    old = await client.get(f"/patient-publications/{publication['id']}")
    assert old.json()["state"] == "superseded"
    latest = await client.get(f"/patients/{demo_data.patient_a.id}/published-care")
    assert latest.json()["updates"] == [
        {
            "kind": "corrected",
            "published_at": latest.json()["updates"][0]["published_at"],
            "content": "Please take metformin 500 mg twice daily.",
            "notice": "This care update was corrected by the clinic.",
        }
    ]


@pytest.mark.asyncio
async def test_publication_workflow_version_is_compare_and_swap(
    client: httpx.AsyncClient,
    second_client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    source = make_dosage_source(db_session, demo_data)
    await login(client, "staff@clinic-a.test")
    created = await client.post(f"/entries/{source.id}/patient-publications", json={})
    publication = created.json()
    await login(client, "clinician@clinic-a.test")
    await login(second_client, "clinician@clinic-a.test")
    first = await client.post(
        f"/patient-publications/{publication['id']}/approve",
        json={"expected_workflow_version": 1},
    )
    second = await second_client.post(
        f"/patient-publications/{publication['id']}/approve",
        json={"expected_workflow_version": 1},
    )
    assert first.status_code == 200
    assert second.status_code == 409
    assert second.json()["detail"]["actual_workflow_version"] == 2
    latest = await second_client.get(f"/patient-publications/{publication['id']}")
    assert latest.status_code == 200
    assert latest.json()["state"] == "clinician_approved"


@pytest.mark.asyncio
async def test_general_publication_without_dosage_can_be_approved_but_is_still_explicit(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    source = make_dosage_source(
        db_session,
        demo_data,
        content="The next follow-up is scheduled for the synthetic care team.",
    )
    await login(client, "clinician@clinic-a.test")
    created = await client.post(f"/entries/{source.id}/patient-publications", json={})
    assert created.status_code == 200
    body = created.json()
    assert body["severity_class"] == "general"
    assert body["dosage"]["status"] == "missing"
    approved = await client.post(
        f"/patient-publications/{body['id']}/approve",
        json={"expected_workflow_version": 1},
    )
    assert approved.status_code == 200
    assert approved.json()["state"] == "clinician_approved"
    assert (await client.get(f"/patients/{demo_data.patient_a.id}/published-care")).json() == {
        "updates": []
    }


@pytest.mark.parametrize(
    ("path_suffix", "method"),
    [
        ("/publish", "post"),
        ("/recall", "post"),
        ("/corrections", "post"),
    ],
)
@pytest.mark.asyncio
async def test_invalid_draft_transitions_are_rejected(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
    path_suffix: str,
    method: str,
) -> None:
    source = make_dosage_source(
        db_session,
        demo_data,
        content="The synthetic follow-up plan is ready.",
    )
    await login(client, "clinician@clinic-a.test")
    created = await client.post(f"/entries/{source.id}/patient-publications", json={})
    publication_id = created.json()["id"]
    response = await getattr(client, method)(
        f"/patient-publications/{publication_id}{path_suffix}",
        json={"expected_workflow_version": 1},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_roles_clinic_scope_audit_and_immutable_publication_rows(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    source = make_dosage_source(db_session, demo_data)
    await login(client, "staff@clinic-a.test")
    created = await client.post(
        f"/entries/{source.id}/patient-publications",
        json={"content": "Take metformin 500 mg twice daily."},
    )
    assert created.status_code == 200
    publication_id = created.json()["id"]
    staff_detail = await client.get(f"/patient-publications/{publication_id}")
    assert staff_detail.status_code == 200
    staff_approval = await client.post(
        f"/patient-publications/{publication_id}/approve",
        json={"expected_workflow_version": 1},
    )
    assert staff_approval.status_code == 403

    await login(client, "staff@clinic-b.test")
    foreign_detail = await client.get(f"/patient-publications/{publication_id}")
    foreign_list = await client.get(f"/patients/{demo_data.patient_a.id}/patient-publications")
    assert foreign_detail.status_code == 404
    assert foreign_list.status_code == 404

    await login(client, "admin@clinic-a.test")
    admin_read = await client.get(f"/patient-publications/{publication_id}")
    admin_edit = await client.patch(
        f"/patient-publications/{publication_id}",
        json={
            "expected_workflow_version": 1,
            "content": "forged admin update",
        },
    )
    assert admin_read.status_code == 200
    assert admin_edit.status_code == 403

    await login(client, "clinician@clinic-a.test")
    approved = await client.post(
        f"/patient-publications/{publication_id}/approve",
        json={"expected_workflow_version": 1},
    )
    published = await client.post(
        f"/patient-publications/{publication_id}/publish",
        json={"expected_workflow_version": approved.json()["workflow_version"]},
    )
    assert approved.status_code == 200
    assert published.status_code == 200
    publication_rows = list(
        db_session.scalars(
            select(PatientPublication).where(PatientPublication.id == publication_id)
        )
    )
    versions = list(
        db_session.scalars(
            select(PatientPublicationVersion).where(
                PatientPublicationVersion.publication_id == publication_id
            )
        )
    )
    evidence = list(
        db_session.scalars(
            select(PatientPublicationEvidence).where(
                PatientPublicationEvidence.publication_id == publication_id
            )
        )
    )
    audits = list(
        db_session.scalars(
            select(AuditLog).where(
                AuditLog.entity_type == "patient_publication",
                AuditLog.entity_id == publication_id,
            )
        )
    )
    assert len(publication_rows) == 1
    assert len(versions) == 1
    assert versions[0].content == "Take metformin 500 mg twice daily."
    assert len(evidence) == 1
    assert str(evidence[0].validation_status) == "matched"
    assert {audit.action for audit in audits} >= {
        "publication_draft_created",
        "publication_clinician_approved",
        "publication_published",
    }
    assert all(not hasattr(audit, "content") for audit in audits)
    delivery = await client.post(f"/patient-publications/{publication_id}/deliver", json={})
    assert delivery.status_code == 404


@pytest.mark.asyncio
async def test_entered_in_error_is_not_patient_visible_before_or_after_publish(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    unpublished_source = make_dosage_source(
        db_session,
        demo_data,
        content="The unpublished synthetic note is incorrect.",
    )
    await login(client, "clinician@clinic-a.test")
    unpublished = await client.post(
        f"/entries/{unpublished_source.id}/patient-publications", json={}
    )
    entered = await client.post(
        f"/patient-publications/{unpublished.json()['id']}/recall",
        json={"expected_workflow_version": 1, "reason_code": "entered_in_error"},
    )
    assert entered.status_code == 200
    assert entered.json()["state"] == "entered_in_error"
    assert (await client.get(f"/patients/{demo_data.patient_a.id}/published-care")).json() == {
        "updates": []
    }

    published_source = make_dosage_source(
        db_session,
        demo_data,
        content="The published synthetic note is ready.",
    )
    published_draft = await client.post(
        f"/entries/{published_source.id}/patient-publications", json={}
    )
    approved = await client.post(
        f"/patient-publications/{published_draft.json()['id']}/approve",
        json={"expected_workflow_version": 1},
    )
    published = await client.post(
        f"/patient-publications/{published_draft.json()['id']}/publish",
        json={"expected_workflow_version": approved.json()["workflow_version"]},
    )
    entered_after_publish = await client.post(
        f"/patient-publications/{published_draft.json()['id']}/recall",
        json={
            "expected_workflow_version": published.json()["workflow_version"],
            "reason_code": "entered_in_error",
        },
    )
    assert entered_after_publish.status_code == 200
    updates = (await client.get(f"/patients/{demo_data.patient_a.id}/published-care")).json()[
        "updates"
    ]
    assert len(updates) == 1
    assert updates[0]["kind"] == "withdrawn"
    assert updates[0]["content"] is None
