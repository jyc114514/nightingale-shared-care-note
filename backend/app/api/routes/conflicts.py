"""Read-only internal optimistic-concurrency conflict endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models import Conflict, User
from app.schemas.entry import ConflictOut
from app.services.authorization import get_entry_context, require_internal


router = APIRouter(tags=["conflicts"])


@router.get("/entries/{entry_id}/conflicts", response_model=list[ConflictOut])
def list_conflicts(
    entry_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ConflictOut]:
    context, _ = get_entry_context(db, user, entry_id)
    require_internal(context)
    conflicts = list(
        db.scalars(
            select(Conflict)
            .where(Conflict.entry_id == entry_id, Conflict.clinic_id == context.clinic_id)
            .order_by(Conflict.created_at, Conflict.id)
        )
    )
    return [ConflictOut.model_validate(conflict) for conflict in conflicts]
