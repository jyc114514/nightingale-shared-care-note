"""Immutable pointers from a derived archival period to canonical sources."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ArchivalSummarySource(Base):
    """A source pointer; the underlying entry/version is never deleted by archival."""

    __tablename__ = "archival_summary_sources"
    __table_args__ = (
        PrimaryKeyConstraint(
            "archival_summary_id",
            "source_entry_id",
            "source_version_id",
            name="pk_archival_summary_sources",
        ),
        Index("ix_archival_summary_sources_entry", "source_entry_id"),
        Index("ix_archival_summary_sources_version", "source_version_id"),
    )

    archival_summary_id: Mapped[str] = mapped_column(
        ForeignKey("archival_summaries.id"), nullable=False
    )
    source_entry_id: Mapped[str] = mapped_column(ForeignKey("entries.id"), nullable=False)
    source_version_id: Mapped[str] = mapped_column(ForeignKey("entry_versions.id"), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source_order: Mapped[int] = mapped_column(Integer, nullable=False)
