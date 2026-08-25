"""Read-only internal comments endpoint for the Gate A access boundary."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models import Comment, User
from app.schemas.entry import CommentOut
from app.services.authorization import get_entry_context, require_internal


router = APIRouter(tags=["comments"])


@router.get("/entries/{entry_id}/comments", response_model=list[CommentOut])
def list_comments(
    entry_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CommentOut]:
    context, _ = get_entry_context(db, user, entry_id)
    require_internal(context)
    comments = list(
        db.scalars(
            select(Comment)
            .where(Comment.entry_id == entry_id, Comment.clinic_id == context.clinic_id)
            .order_by(Comment.created_at, Comment.id)
        )
    )
    return [CommentOut.model_validate(comment) for comment in comments]
