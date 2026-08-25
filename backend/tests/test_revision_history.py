"""Gate A immutable snapshots, diff, revert, and metadata-only audit tests."""

import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AuditLog
from conftest import DemoData, TEST_PASSWORD


async def login(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/auth/login",
        json={"email": "staff@clinic-a.test", "password": TEST_PASSWORD},
    )
    assert response.status_code == 200, response.text


@pytest.mark.asyncio
async def test_edit_diff_and_revert_preserve_full_history(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    await login(client)
    update = await client.patch(
        f"/entries/{demo_data.staff_note.id}",
        json={"expected_version": 1, "new_content": "Updated staff note"},
    )
    assert update.status_code == 200
    assert update.json()["current_version"] == 2
    assert update.json()["content"] == "Updated staff note"

    versions_response = await client.get(f"/entries/{demo_data.staff_note.id}/versions")
    assert versions_response.status_code == 200
    versions = versions_response.json()
    assert [version["version_number"] for version in versions] == [1, 2]
    assert versions[0]["content"] == "Original staff note"
    assert versions[1]["content"] == "Updated staff note"

    diff = await client.get(
        f"/entries/{demo_data.staff_note.id}/diff",
        params={"from_version": 1, "to_version": 2},
    )
    assert diff.status_code == 200
    assert diff.json() == {
        "entry_id": demo_data.staff_note.id,
        "from_version": 1,
        "to_version": 2,
        "from_content": "Original staff note",
        "to_content": "Updated staff note",
        "changed": True,
    }

    revert = await client.post(
        f"/entries/{demo_data.staff_note.id}/revert",
        json={"target_version": 1, "expected_current_version": 2},
    )
    assert revert.status_code == 200
    assert revert.json()["current_version"] == 3
    assert revert.json()["content"] == "Original staff note"

    final_versions = await client.get(f"/entries/{demo_data.staff_note.id}/versions")
    assert final_versions.status_code == 200
    final_payload = final_versions.json()
    assert [version["version_number"] for version in final_payload] == [1, 2, 3]
    assert final_payload[2]["content"] == "Original staff note"
    assert final_payload[2]["reverted_from_version"] == 1

    audits = list(
        db_session.scalars(
            select(AuditLog).where(
                AuditLog.entity_id == demo_data.staff_note.id,
                AuditLog.entity_type == "entry",
            )
        )
    )
    assert {audit.action for audit in audits} == {
        "entry_created",
        "entry_updated",
        "entry_reverted",
    }
    assert all(audit.actor_role == "staff" for audit in audits)
    assert all(not hasattr(audit, "content") for audit in audits)
    audit_columns = set(AuditLog.__table__.columns.keys())
    assert "content" not in audit_columns
    assert "Original staff note" not in str([audit.__dict__ for audit in audits])
    assert "Updated staff note" not in str([audit.__dict__ for audit in audits])
