"""Metadata-only candidate rows belonging to a Glance impression batch."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, new_id, utcnow


class GlanceImpressionItem(Base):
    __tablename__ = "glance_impression_items"
    __table_args__ = (
        UniqueConstraint(
            "batch_id",
            "resource_type",
            "resource_id",
            name="uq_glance_impression_item_resource",
        ),
        CheckConstraint("candidate_rank >= 1", name="ck_glance_impression_item_rank"),
        Index(
            "ix_glance_impression_items_feature_surfaced",
            "feature_signature",
            "surfaced",
        ),
        Index("ix_glance_impression_items_surfaced", "surfaced"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    batch_id: Mapped[str] = mapped_column(
        ForeignKey("glance_impression_batches.id"), index=True, nullable=False
    )
    resource_type: Mapped[str] = mapped_column(String(20), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(36), nullable=False)
    feature_signature: Mapped[str] = mapped_column(String(300), index=True, nullable=False)
    candidate_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    surfaced: Mapped[bool] = mapped_column(Boolean, nullable=False)
    display_priority: Mapped[float] = mapped_column(Float, nullable=False)
    safety_class: Mapped[str | None] = mapped_column(String(50), index=True, nullable=True)
    safety_floor: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
