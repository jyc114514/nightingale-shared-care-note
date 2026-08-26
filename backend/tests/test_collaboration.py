"""Real application tests for optional clinic-scoped mentions and tasks."""

import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AuditLog, Mention, Task, TaskConflict
from conftest import DemoData, TEST_PASSWORD


async def login(client: httpx.AsyncClient, email: str) -> None:
    response = await client.post("/auth/login", json={"email": email, "password": TEST_PASSWORD})
    assert response.status_code == 200, response.text


@pytest.mark.asyncio
async def test_mentions_are_clinic_scoped_deduplicated_and_projected_safely(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    await login(client, "staff@clinic-a.test")
    directory = await client.get(f"/patients/{demo_data.patient_a.id}/mentionable-users")
    assert directory.status_code == 200, directory.text
    clinician = next(row for row in directory.json() if row["role"] == "clinician")
    staff = next(row for row in directory.json() if row["role"] == "staff")
    assert all(set(row) == {"user_id", "display_name", "role"} for row in directory.json())

    created = await client.post(
        f"/entries/{demo_data.staff_note.id}/comments",
        json={
            "body": "Coordinate with @clinician",
            "mentioned_user_ids": [clinician["user_id"], clinician["user_id"], staff["user_id"]],
        },
    )
    assert created.status_code == 200, created.text
    assert {mention["mentioned_user_id"] for mention in created.json()["mentions"]} == {
        clinician["user_id"],
        staff["user_id"],
    }
    listed = await client.get(f"/entries/{demo_data.staff_note.id}/comments")
    assert listed.status_code == 200
    assert len(listed.json()[-1]["mentions"]) == 2

    invalid = await client.post(
        f"/entries/{demo_data.staff_note.id}/comments",
        json={"body": "bad mention", "mentioned_user_ids": [demo_data.staff_b.id]},
    )
    assert invalid.status_code == 422

    await login(client, "patient@clinic-a.test")
    patient_denied = await client.get(f"/patients/{demo_data.patient_a.id}/mentionable-users")
    assert patient_denied.status_code == 403
    patient_comment = await client.post(
        f"/entries/{demo_data.staff_note.id}/comments",
        json={"body": "patient internal mention", "mentioned_user_ids": [clinician["user_id"]]},
    )
    assert patient_comment.status_code == 403

    assert db_session.scalar(
        select(Mention).where(Mention.mentioned_user_id == clinician["user_id"])
    )
    audit_rows = list(
        db_session.scalars(select(AuditLog).where(AuditLog.action == "mention_created"))
    )
    assert audit_rows
    assert all("Coordinate" not in str(row.__dict__) for row in audit_rows)


@pytest.mark.asyncio
async def test_tasks_support_assignment_sources_cas_and_materialized_glance(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    await login(client, "staff@clinic-a.test")
    directory = await client.get(f"/patients/{demo_data.patient_a.id}/mentionable-users")
    clinician_id = next(row["user_id"] for row in directory.json() if row["role"] == "clinician")
    created = await client.post(
        f"/patients/{demo_data.patient_a.id}/tasks",
        json={
            "title": "Confirm the next appointment window",
            "assigned_to_user_id": clinician_id,
            "source_entry_id": demo_data.staff_note.id,
        },
    )
    assert created.status_code == 200, created.text
    task = created.json()
    assert task["assigned_to"]["user_id"] == clinician_id
    assert task["source_entry_id"] == demo_data.staff_note.id
    assert task["status"] == "open"

    glance = await client.get(f"/patients/{demo_data.patient_a.id}/glance")
    assert glance.status_code == 200
    task_items = [item for item in glance.json() if item["resource_type"] == "task"]
    assert task_items and task_items[0]["task_id"] == task["id"]
    assert task_items[0]["assigned_to_user_id"] == clinician_id

    progress = await client.patch(
        f"/tasks/{task['id']}",
        json={
            "expected_version": 1,
            "status": "in_progress",
            "title": "Confirm the next appointment window",
            "assigned_to_user_id": clinician_id,
        },
    )
    assert progress.status_code == 200, progress.text
    assert progress.json()["version"] == 2
    stale = await client.patch(
        f"/tasks/{task['id']}",
        json={
            "expected_version": 1,
            "status": "done",
            "title": "Stale task submission",
            "assigned_to_user_id": clinician_id,
        },
    )
    assert stale.status_code == 409, stale.text
    assert stale.json()["detail"]["actual_version"] == 2

    done = await client.patch(
        f"/tasks/{task['id']}",
        json={
            "expected_version": 2,
            "status": "done",
            "assigned_to_user_id": clinician_id,
        },
    )
    assert done.status_code == 200, done.text
    assert done.json()["completed_at"]
    glance_after_done = await client.get(f"/patients/{demo_data.patient_a.id}/glance")
    assert task["id"] not in {item.get("task_id") for item in glance_after_done.json()}

    invalid_assignee = await client.post(
        f"/patients/{demo_data.patient_a.id}/tasks",
        json={
            "title": "Cross clinic task",
            "assigned_to_user_id": demo_data.staff_b.id,
        },
    )
    assert invalid_assignee.status_code == 422

    await login(client, "admin@clinic-a.test")
    admin_read = await client.get(f"/patients/{demo_data.patient_a.id}/tasks")
    assert admin_read.status_code == 200
    admin_write = await client.post(
        f"/patients/{demo_data.patient_a.id}/tasks",
        json={"title": "admin write", "assigned_to_user_id": clinician_id},
    )
    assert admin_write.status_code == 403

    await login(client, "patient@clinic-a.test")
    patient_read = await client.get(f"/patients/{demo_data.patient_a.id}/tasks")
    assert patient_read.status_code == 403
    patient_write = await client.post(
        f"/patients/{demo_data.patient_a.id}/tasks",
        json={"title": "patient task", "assigned_to_user_id": clinician_id},
    )
    assert patient_write.status_code == 403

    assert db_session.scalar(select(Task).where(Task.id == task["id"]))
    assert db_session.scalar(select(TaskConflict).where(TaskConflict.task_id == task["id"]))
    audit_rows = list(db_session.scalars(select(AuditLog).where(AuditLog.entity_type == "task")))
    assert {row.action for row in audit_rows} >= {
        "task_created",
        "task_updated",
        "task_completed",
        "task_conflict",
    }
    assert all("Confirm the next appointment" not in str(row.__dict__) for row in audit_rows)


@pytest.mark.asyncio
async def test_task_can_be_sourced_from_a_threaded_comment(
    client: httpx.AsyncClient,
    demo_data: DemoData,
) -> None:
    await login(client, "staff@clinic-a.test")
    comment = await client.post(
        f"/entries/{demo_data.staff_note.id}/comments",
        json={"body": "Assign this follow-up"},
    )
    assert comment.status_code == 200, comment.text
    directory = await client.get(f"/patients/{demo_data.patient_a.id}/mentionable-users")
    staff_id = next(row["user_id"] for row in directory.json() if row["role"] == "staff")
    task = await client.post(
        f"/patients/{demo_data.patient_a.id}/tasks",
        json={
            "title": "Follow up on the comment",
            "assigned_to_user_id": staff_id,
            "source_comment_id": comment.json()["id"],
        },
    )
    assert task.status_code == 200, task.text
    assert task.json()["source_comment_id"] == comment.json()["id"]
