"""Round 4 patient-publication safety gate tests through the real API."""

import httpx
import pytest
from sqlalchemy.orm import Session

from app.models import Entry, EntryOwnerRole, EntryType, EntryVisibility
from app.services.entries import create_entry_record
from app.services.publication_evidence import extract_dosage
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
