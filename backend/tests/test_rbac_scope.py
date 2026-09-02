"""Gate A server-side role and clinic scope tests through the real API."""

import httpx
import pytest

from conftest import DemoData, TEST_PASSWORD


async def login(client: httpx.AsyncClient, email: str) -> None:
    response = await client.post("/auth/login", json={"email": email, "password": TEST_PASSWORD})
    assert response.status_code == 200, response.text
    assert "token" not in response.text.lower()
    assert client.cookies.get("nightingale_session") is not None


@pytest.mark.asyncio
async def test_unauthenticated_requests_are_rejected(
    client: httpx.AsyncClient, demo_data: DemoData
) -> None:
    response = await client.get(f"/patients/{demo_data.patient_a.id}")
    assert response.status_code == 401

    logout = await client.post(
        "/auth/logout",
        headers={"Origin": "http://testserver"},
    )
    assert logout.status_code == 401


@pytest.mark.asyncio
async def test_patient_sees_only_safe_patient_facing_fields(
    client: httpx.AsyncClient,
    demo_data: DemoData,
) -> None:
    await login(client, "patient@clinic-a.test")
    entries_response = await client.get(f"/patients/{demo_data.patient_a.id}/entries")
    assert entries_response.status_code == 200
    entries = entries_response.json()
    assert {entry["entry_type"] for entry in entries} == {
        "patient_facing_summary",
        "patient_instruction",
    }
    assert all("owner_role" not in entry for entry in entries)
    assert all("visibility" not in entry for entry in entries)
    assert all("Raw synthetic AI session summary" not in entry["content"] for entry in entries)

    comments = await client.get(f"/entries/{demo_data.ai_summary.id}/comments")
    assert comments.status_code == 403
    raw_ai = await client.get(f"/entries/{demo_data.ai_summary.id}")
    assert raw_ai.status_code == 403
    versions = await client.get(f"/entries/{demo_data.patient_summary.id}/versions")
    assert versions.status_code == 403
    cross_patient = await client.get(f"/patients/{demo_data.patient_b.id}")
    assert cross_patient.status_code == 404


@pytest.mark.asyncio
async def test_staff_and_clinician_writes_are_role_derived(
    client: httpx.AsyncClient,
    demo_data: DemoData,
) -> None:
    await login(client, "staff@clinic-a.test")
    staff_create = await client.post(
        f"/patients/{demo_data.patient_a.id}/entries",
        json={
            "entry_type": "staff_note",
            "content": "A new staff note",
            "owner_role": "clinician",
            "clinic_id": demo_data.clinic_b.id,
        },
    )
    assert staff_create.status_code == 200
    assert staff_create.json()["owner_role"] == "staff"
    assert staff_create.json()["clinic_id"] == demo_data.clinic_a.id

    staff_clinician_create = await client.post(
        f"/patients/{demo_data.patient_a.id}/entries",
        json={"entry_type": "clinician_section", "content": "forged clinician content"},
    )
    assert staff_clinician_create.status_code == 403
    staff_edit_clinician = await client.patch(
        f"/entries/{demo_data.clinician_section.id}",
        json={"expected_version": 1, "new_content": "staff overwrite"},
    )
    assert staff_edit_clinician.status_code == 403

    await login(client, "clinician@clinic-a.test")
    clinician_create = await client.post(
        f"/patients/{demo_data.patient_a.id}/entries",
        json={"entry_type": "clinician_section", "content": "A new clinician section"},
    )
    assert clinician_create.status_code == 200
    assert clinician_create.json()["owner_role"] == "clinician"
    clinician_staff_create = await client.post(
        f"/patients/{demo_data.patient_a.id}/entries",
        json={"entry_type": "staff_note", "content": "forged staff content"},
    )
    assert clinician_staff_create.status_code == 403
    clinician_edit_staff = await client.patch(
        f"/entries/{demo_data.staff_note.id}",
        json={"expected_version": 1, "new_content": "clinician overwrite"},
    )
    assert clinician_edit_staff.status_code == 403
    clinician_edit_ai = await client.patch(
        f"/entries/{demo_data.ai_summary.id}",
        json={"expected_version": 1, "new_content": "clinician overwrite AI"},
    )
    assert clinician_edit_ai.status_code == 403


@pytest.mark.asyncio
async def test_clinic_scope_and_admin_read_only_are_enforced(
    client: httpx.AsyncClient,
    demo_data: DemoData,
) -> None:
    await login(client, "staff@clinic-a.test")
    own = await client.get(f"/patients/{demo_data.patient_a.id}")
    foreign = await client.get(f"/patients/{demo_data.patient_b.id}")
    listed = await client.get("/patients")
    assert own.status_code == 200
    assert foreign.status_code == 404
    assert {patient["id"] for patient in listed.json()} == {demo_data.patient_a.id}

    await login(client, "staff@clinic-b.test")
    foreign_for_b = await client.get(f"/patients/{demo_data.patient_a.id}")
    assert foreign_for_b.status_code == 404

    await login(client, "admin@clinic-a.test")
    admin_read = await client.get(f"/entries/{demo_data.ai_summary.id}")
    assert admin_read.status_code == 200
    admin_write = await client.patch(
        f"/entries/{demo_data.staff_note.id}",
        json={"expected_version": 1, "new_content": "admin edit"},
    )
    assert admin_write.status_code == 403
