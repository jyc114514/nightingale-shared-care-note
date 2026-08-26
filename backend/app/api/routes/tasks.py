"""Clinic-scoped mentions directory and internal assignment/task APIs."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_request_id, require_allowed_origin
from app.db.base import utcnow
from app.db.session import get_db
from app.models import Comment, Task, TaskConflict, User
from app.models.enums import TaskStatus
from app.schemas.collaboration import MentionUserOut, TaskCreate, TaskOut, TaskUpdate
from app.services.authorization import get_entry_context, get_patient_context, require_internal
from app.services.collaboration import active_collaborators, task_out, validate_collaborator_ids
from app.services.entries import record_audit
from app.services.tasks import sync_task_projection


router = APIRouter(tags=["collaboration"])


def require_task_writer(actor_role: str) -> None:
    if actor_role not in {"staff", "clinician"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff or clinicians can mutate internal tasks",
        )


def validate_task_source(
    db: Session,
    *,
    clinic_id: str,
    patient_id: str,
    source_entry_id: str | None,
    source_comment_id: str | None,
    user: User,
) -> None:
    if source_entry_id is not None:
        source_context, source_entry = get_entry_context(db, user, source_entry_id)
        if source_context.clinic_id != clinic_id or source_entry.patient_id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task source entry is outside the patient scope",
            )
    if source_comment_id is not None:
        comment = db.get(Comment, source_comment_id)
        if comment is None or comment.clinic_id != clinic_id or comment.patient_id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task source comment is outside the patient scope",
            )


@router.get(
    "/patients/{patient_id}/mentionable-users",
    response_model=list[MentionUserOut],
)
def mentionable_users(
    patient_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MentionUserOut]:
    context = get_patient_context(db, user, patient_id)
    require_internal(context)
    return active_collaborators(db, context.clinic_id)


@router.get("/patients/{patient_id}/tasks", response_model=list[TaskOut])
def list_tasks(
    patient_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TaskOut]:
    context = get_patient_context(db, user, patient_id)
    require_internal(context)
    tasks = list(
        db.scalars(
            select(Task)
            .where(Task.patient_id == patient_id, Task.clinic_id == context.clinic_id)
            .order_by(Task.updated_at.desc(), Task.id.desc())
        )
    )
    return [task_out(db, task) for task in tasks]


@router.post(
    "/patients/{patient_id}/tasks",
    response_model=TaskOut,
    dependencies=[Depends(require_allowed_origin)],
)
def create_task(
    patient_id: str,
    payload: TaskCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> TaskOut:
    context = get_patient_context(db, user, patient_id)
    require_internal(context)
    require_task_writer(context.actor_role)
    try:
        assignee = validate_collaborator_ids(
            db,
            clinic_id=context.clinic_id,
            user_ids=[payload.assigned_to_user_id],
        )[0]
    except (ValueError, IndexError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="assigned_to_user_id must be an active staff or clinician in this clinic",
        ) from exc
    validate_task_source(
        db,
        clinic_id=context.clinic_id,
        patient_id=patient_id,
        source_entry_id=payload.source_entry_id,
        source_comment_id=payload.source_comment_id,
        user=user,
    )
    task = Task(
        clinic_id=context.clinic_id,
        patient_id=patient_id,
        source_entry_id=payload.source_entry_id,
        source_comment_id=payload.source_comment_id,
        title=payload.title,
        created_by_user_id=user.id,
        assigned_to_user_id=assignee.id,
        status=TaskStatus.OPEN,
        version=1,
        updated_at=utcnow(),
    )
    db.add(task)
    db.flush()
    sync_task_projection(db, task)
    record_audit(
        db,
        clinic_id=context.clinic_id,
        patient_id=patient_id,
        actor_user_id=user.id,
        actor_role=context.actor_role,
        action="task_created",
        entity_type="task",
        entity_id=task.id,
        request_id=request_id,
    )
    db.commit()
    db.refresh(task)
    return task_out(db, task)


@router.patch(
    "/tasks/{task_id}",
    response_model=TaskOut,
    dependencies=[Depends(require_allowed_origin)],
)
def update_task(
    task_id: str,
    payload: TaskUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> TaskOut:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    context = get_patient_context(db, user, task.patient_id)
    require_internal(context)
    require_task_writer(context.actor_role)
    if task.clinic_id != context.clinic_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    next_assignee_id = payload.assigned_to_user_id or task.assigned_to_user_id
    try:
        validate_collaborator_ids(
            db,
            clinic_id=context.clinic_id,
            user_ids=[next_assignee_id],
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="assigned_to_user_id must be an active staff or clinician in this clinic",
        ) from exc
    next_status = payload.status or task.status
    if payload.expected_version != task.version:
        conflict = TaskConflict(
            clinic_id=task.clinic_id,
            patient_id=task.patient_id,
            task_id=task.id,
            submitted_by_user_id=user.id,
            expected_version=payload.expected_version,
            actual_version=task.version,
            attempted_title=payload.title or task.title,
            attempted_assignee_user_id=next_assignee_id,
            attempted_status=next_status.value
            if isinstance(next_status, TaskStatus)
            else str(next_status),
        )
        db.add(conflict)
        db.flush()
        record_audit(
            db,
            clinic_id=context.clinic_id,
            patient_id=task.patient_id,
            actor_user_id=user.id,
            actor_role=context.actor_role,
            action="task_conflict",
            entity_type="task",
            entity_id=task.id,
            request_id=request_id,
            from_version=payload.expected_version,
            to_version=task.version,
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Task version is stale",
                "conflict_id": conflict.id,
                "expected_version": payload.expected_version,
                "actual_version": task.version,
            },
        )

    task.title = payload.title or task.title
    task.assigned_to_user_id = next_assignee_id
    task.status = next_status
    task.version += 1
    task.updated_at = utcnow()
    task.completed_at = task.updated_at if next_status is TaskStatus.DONE else None
    sync_task_projection(db, task)
    record_audit(
        db,
        clinic_id=context.clinic_id,
        patient_id=task.patient_id,
        actor_user_id=user.id,
        actor_role=context.actor_role,
        action="task_updated" if next_status is not TaskStatus.DONE else "task_completed",
        entity_type="task",
        entity_id=task.id,
        request_id=request_id,
        from_version=payload.expected_version,
        to_version=task.version,
    )
    db.commit()
    db.refresh(task)
    return task_out(db, task)
