"""Gate A independent-session concurrent edit and conflict tests."""

import asyncio

import httpx
import pytest

from conftest import DemoData, TEST_PASSWORD


async def login(client: httpx.AsyncClient, email: str) -> None:
    response = await client.post("/auth/login", json={"email": email, "password": TEST_PASSWORD})
    assert response.status_code == 200, response.text


@pytest.mark.asyncio
async def test_different_sections_do_not_overwrite_each_other(
    client: httpx.AsyncClient,
    second_client: httpx.AsyncClient,
    demo_data: DemoData,
) -> None:
    await login(client, "staff@clinic-a.test")
    await login(second_client, "clinician@clinic-a.test")
    staff_write, clinician_write = await asyncio.gather(
        client.patch(
            f"/entries/{demo_data.staff_note.id}",
            json={"expected_version": 1, "new_content": "Parallel staff update"},
        ),
        second_client.patch(
            f"/entries/{demo_data.clinician_section.id}",
            json={"expected_version": 1, "new_content": "Parallel clinician update"},
        ),
    )
    assert staff_write.status_code == 200, staff_write.text
    assert clinician_write.status_code == 200, clinician_write.text

    staff_read = await client.get(f"/entries/{demo_data.staff_note.id}")
    clinician_read = await second_client.get(f"/entries/{demo_data.clinician_section.id}")
    assert staff_read.json()["content"] == "Parallel staff update"
    assert clinician_read.json()["content"] == "Parallel clinician update"


@pytest.mark.asyncio
async def test_same_section_stale_write_returns_409_and_preserves_submission(
    client: httpx.AsyncClient,
    second_client: httpx.AsyncClient,
    demo_data: DemoData,
) -> None:
    await login(client, "staff@clinic-a.test")
    await login(second_client, "staff@clinic-a.test")
    first, second = await asyncio.gather(
        client.patch(
            f"/entries/{demo_data.staff_note.id}",
            json={"expected_version": 1, "new_content": "First concurrent submission"},
        ),
        second_client.patch(
            f"/entries/{demo_data.staff_note.id}",
            json={"expected_version": 1, "new_content": "Second concurrent submission"},
        ),
    )
    statuses = {first.status_code, second.status_code}
    assert statuses == {200, 409}
    conflict_response = first if first.status_code == 409 else second
    accepted_response = first if first.status_code == 200 else second
    conflict_detail = conflict_response.json()["detail"]
    assert conflict_detail["expected_version"] == 1
    assert conflict_detail["actual_version"] == 2
    assert accepted_response.json()["current_version"] == 2

    conflicts = await client.get(f"/entries/{demo_data.staff_note.id}/conflicts")
    assert conflicts.status_code == 200
    payload = conflicts.json()
    assert len(payload) == 1
    assert payload[0]["attempted_content"] in {
        "First concurrent submission",
        "Second concurrent submission",
    }
    current = await client.get(f"/entries/{demo_data.staff_note.id}")
    assert current.json()["content"] == accepted_response.json()["content"]
