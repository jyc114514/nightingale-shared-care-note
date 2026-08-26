"""Task mutation and materialized Glance projection helpers."""

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.base import utcnow
from app.models import Task, TaskGlanceItem, User
from app.models.enums import TaskStatus


def sync_task_projection(db: Session, task: Task) -> TaskGlanceItem | None:
    projection = db.scalar(select(TaskGlanceItem).where(TaskGlanceItem.task_id == task.id))
    if task.status == TaskStatus.DONE:
        if projection is not None:
            db.delete(projection)
            db.flush()
        return None

    assignee = db.get(User, task.assigned_to_user_id)
    if assignee is None:
        raise RuntimeError("Task assignee is missing")
    if projection is None:
        projection = TaskGlanceItem(id=task.id, task_id=task.id)
        db.add(projection)
    projection.clinic_id = task.clinic_id
    projection.patient_id = task.patient_id
    projection.source_entry_id = task.source_entry_id
    projection.source_comment_id = task.source_comment_id
    projection.content_summary = task.title
    projection.display_priority = 96 if task.status == TaskStatus.OPEN else 88
    projection.action_label = "Assigned task"
    projection.action_state = task.status.value
    projection.assigned_to_user_id = assignee.id
    projection.assigned_to_display_name = assignee.display_name
    projection.task_status = task.status.value
    projection.task_version = task.version
    projection.occurred_at = task.updated_at
    projection.updated_at = utcnow()
    db.flush()
    return projection


def delete_task_projection(db: Session, task_id: str) -> None:
    db.execute(delete(TaskGlanceItem).where(TaskGlanceItem.task_id == task_id))
