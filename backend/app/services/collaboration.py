"""Shared authorization and response helpers for optional collaboration features."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ClinicMembership, Comment, Mention, Task, User
from app.schemas.collaboration import MentionOut, MentionUserOut, TaskOut
from app.services.authorization import enum_value


COLLABORATOR_ROLES = {"staff", "clinician"}


def active_collaborators(db: Session, clinic_id: str) -> list[MentionUserOut]:
    rows = db.execute(
        select(User, ClinicMembership.role)
        .join(ClinicMembership, ClinicMembership.user_id == User.id)
        .where(
            ClinicMembership.clinic_id == clinic_id,
            User.is_active.is_(True),
            ClinicMembership.role.in_(sorted(COLLABORATOR_ROLES)),
        )
        .order_by(User.display_name, User.id)
    ).all()
    return [
        MentionUserOut(
            user_id=user.id,
            display_name=user.display_name,
            role=enum_value(role),
        )
        for user, role in rows
    ]


def validate_collaborator_ids(
    db: Session,
    *,
    clinic_id: str,
    user_ids: list[str],
) -> list[User]:
    unique_ids = list(dict.fromkeys(user_ids))
    if not unique_ids:
        return []
    rows = (
        db.execute(
            select(User)
            .join(ClinicMembership, ClinicMembership.user_id == User.id)
            .where(
                User.id.in_(unique_ids),
                User.is_active.is_(True),
                ClinicMembership.clinic_id == clinic_id,
                ClinicMembership.role.in_(sorted(COLLABORATOR_ROLES)),
            )
        )
        .scalars()
        .all()
    )
    by_id = {user.id: user for user in rows}
    if len(by_id) != len(unique_ids):
        raise ValueError("Every mentioned or assigned user must be an active clinic collaborator")
    return [by_id[user_id] for user_id in unique_ids]


def comment_mentions(db: Session, comment: Comment) -> list[MentionOut]:
    rows = db.execute(
        select(Mention, User)
        .join(User, User.id == Mention.mentioned_user_id)
        .where(Mention.comment_id == comment.id)
        .order_by(Mention.created_at, Mention.id)
    ).all()
    return [
        MentionOut(
            id=mention.id,
            mentioned_user_id=user.id,
            display_name=user.display_name,
            role=enum_value(
                db.scalar(
                    select(ClinicMembership.role).where(
                        ClinicMembership.user_id == user.id,
                        ClinicMembership.clinic_id == comment.clinic_id,
                    )
                )
            ),
            created_at=mention.created_at,
        )
        for mention, user in rows
    ]


def task_out(db: Session, task: Task) -> TaskOut:
    assignee = db.get(User, task.assigned_to_user_id)
    if assignee is None:
        raise RuntimeError("Task assignee disappeared from the canonical user table")
    membership_role = db.scalar(
        select(ClinicMembership.role).where(
            ClinicMembership.user_id == assignee.id,
            ClinicMembership.clinic_id == task.clinic_id,
        )
    )
    if membership_role is None:
        raise RuntimeError("Task assignee is outside the canonical clinic membership")
    return TaskOut(
        id=task.id,
        clinic_id=task.clinic_id,
        patient_id=task.patient_id,
        source_entry_id=task.source_entry_id,
        source_comment_id=task.source_comment_id,
        title=task.title,
        created_by_user_id=task.created_by_user_id,
        assigned_to=MentionUserOut(
            user_id=assignee.id,
            display_name=assignee.display_name,
            role=enum_value(membership_role),
        ),
        status=task.status,
        version=task.version,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at,
    )
