"""Clinic-scoped stable user mentions attached to internal comments."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, new_id, utcnow


class Mention(Base):
    __tablename__ = "mentions"
    __table_args__ = (
        UniqueConstraint("comment_id", "mentioned_user_id", name="uq_mention_comment_user"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), index=True, nullable=False)
    comment_id: Mapped[str] = mapped_column(ForeignKey("comments.id"), index=True, nullable=False)
    mentioned_user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"), index=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
