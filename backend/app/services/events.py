"""Metadata-only persisted collaboration invalidation events."""

from sqlalchemy.orm import Session

from app.db.base import utcnow
from app.models import CollaborationEvent


def append_event(
    db: Session,
    *,
    clinic_id: str,
    patient_id: str,
    resource_type: str,
    resource_id: str,
    event_kind: str,
    actor_user_id: str | None,
    actor_role: str,
) -> CollaborationEvent:
    event = CollaborationEvent(
        clinic_id=clinic_id,
        patient_id=patient_id,
        resource_type=resource_type,
        resource_id=resource_id,
        event_kind=event_kind,
        actor_user_id=actor_user_id,
        actor_role=actor_role,
        created_at=utcnow(),
    )
    db.add(event)
    db.flush()
    return event
