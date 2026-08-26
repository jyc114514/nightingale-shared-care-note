"""Threaded internal comments with resolution metadata."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_request_id, require_allowed_origin
from app.db.base import utcnow
from app.db.session import get_db
from app.models import Comment, Mention, User
from app.schemas.entry import CommentCreate, CommentOut, CommentResolution
from app.services.authorization import get_entry_context, get_patient_context, require_internal
from app.services.collaboration import comment_mentions, validate_collaborator_ids
from app.services.entries import record_audit
from app.services.events import append_event


router = APIRouter(tags=["comments"])


def require_comment_writer(actor_role: str) -> None:
    if actor_role not in {"staff", "clinician"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff or clinicians can mutate comments",
        )


def comment_out(db: Session, comment: Comment) -> CommentOut:
    return CommentOut(
        id=comment.id,
        entry_id=comment.entry_id,
        parent_comment_id=comment.parent_comment_id,
        author_user_id=comment.author_user_id,
        body=comment.body,
        is_resolved=comment.is_resolved,
        resolved_at=comment.resolved_at,
        resolved_by_user_id=comment.resolved_by_user_id,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        mentions=comment_mentions(db, comment),
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
    return [comment_out(db, comment) for comment in comments]


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
    try:
        mentioned_users = validate_collaborator_ids(
            db,
            clinic_id=context.clinic_id,
            user_ids=payload.mentioned_user_ids,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)
        ) from exc
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
    for mentioned_user in mentioned_users:
        mention = Mention(
            clinic_id=context.clinic_id,
            comment_id=comment.id,
            mentioned_user_id=mentioned_user.id,
        )
        db.add(mention)
        db.flush()
        record_audit(
            db,
            clinic_id=context.clinic_id,
            patient_id=entry.patient_id,
            actor_user_id=user.id,
            actor_role=context.actor_role,
            action="mention_created",
            entity_type="mention",
            entity_id=mention.id,
            request_id=request_id,
        )
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
    append_event(
        db,
        clinic_id=context.clinic_id,
        patient_id=entry.patient_id,
        resource_type="comment",
        resource_id=comment.id,
        event_kind="comment_created",
        actor_user_id=user.id,
        actor_role=context.actor_role,
    )
    db.commit()
    db.refresh(comment)
    return comment_out(db, comment)


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
    append_event(
        db,
        clinic_id=context.clinic_id,
        patient_id=comment.patient_id,
        resource_type="comment",
        resource_id=comment.id,
        event_kind="comment_updated",
        actor_user_id=user.id,
        actor_role=context.actor_role,
    )
    db.commit()
    db.refresh(comment)
    return comment_out(db, comment)
