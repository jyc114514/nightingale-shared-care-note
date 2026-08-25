"""Threaded internal comments with resolution metadata."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_request_id, require_allowed_origin
from app.db.base import utcnow
from app.db.session import get_db
from app.models import Comment, User
from app.schemas.entry import CommentCreate, CommentOut, CommentResolution
from app.services.authorization import get_entry_context, get_patient_context, require_internal
from app.services.entries import record_audit


router = APIRouter(tags=["comments"])


def require_comment_writer(actor_role: str) -> None:
    if actor_role not in {"staff", "clinician"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff or clinicians can mutate comments",
        )


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


@router.post(
    "/entries/{entry_id}/comments",
    response_model=CommentOut,
    dependencies=[Depends(require_allowed_origin)],
)
def create_comment(
    entry_id: str,
    payload: CommentCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> CommentOut:
    context, entry = get_entry_context(db, user, entry_id)
    require_internal(context)
    require_comment_writer(context.actor_role)
    if payload.parent_comment_id is not None:
        parent = db.get(Comment, payload.parent_comment_id)
        if parent is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Parent comment not found"
            )
        if parent.entry_id != entry.id or parent.clinic_id != context.clinic_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent comment must belong to the same entry",
            )
    comment = Comment(
        clinic_id=context.clinic_id,
        patient_id=entry.patient_id,
        entry_id=entry.id,
        parent_comment_id=payload.parent_comment_id,
        author_user_id=user.id,
        body=payload.body,
        updated_at=utcnow(),
    )
    db.add(comment)
    db.flush()
    record_audit(
        db,
        clinic_id=context.clinic_id,
        patient_id=entry.patient_id,
        actor_user_id=user.id,
        actor_role=context.actor_role,
        action="comment_created",
        entity_type="comment",
        entity_id=comment.id,
        request_id=request_id,
    )
    db.commit()
    db.refresh(comment)
    return CommentOut.model_validate(comment)


@router.patch(
    "/comments/{comment_id}/resolution",
    response_model=CommentOut,
    dependencies=[Depends(require_allowed_origin)],
)
def update_comment_resolution(
    comment_id: str,
    payload: CommentResolution,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> CommentOut:
    comment = db.get(Comment, comment_id)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    context = get_patient_context(db, user, comment.patient_id)
    require_internal(context)
    require_comment_writer(context.actor_role)
    comment.is_resolved = payload.is_resolved
    comment.resolved_at = utcnow() if payload.is_resolved else None
    comment.resolved_by_user_id = user.id if payload.is_resolved else None
    comment.updated_at = utcnow()
    record_audit(
        db,
        clinic_id=context.clinic_id,
        patient_id=comment.patient_id,
        actor_user_id=user.id,
        actor_role=context.actor_role,
        action="comment_resolved" if payload.is_resolved else "comment_unresolved",
        entity_type="comment",
        entity_id=comment.id,
        request_id=request_id,
    )
    db.commit()
    db.refresh(comment)
    return CommentOut.model_validate(comment)
