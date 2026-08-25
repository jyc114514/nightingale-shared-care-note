"""Add rebuildable hot/warm/cold context summaries with canonical source pointers."""

import sqlalchemy as sa
from alembic import op


revision = "0006_gate_d_archival"
down_revision = "0005_gate_d_importance"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "archival_summaries",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("clinic_id", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.String(length=36), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("summary_text", sa.Text(), nullable=False),
        sa.Column("source_count", sa.Integer(), nullable=False),
        sa.Column("source_manifest_hash", sa.String(length=64), nullable=False),
        sa.Column("generated_by", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("refreshed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("policy_version", sa.String(length=40), nullable=False),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "clinic_id",
            "patient_id",
            "period_start",
            "period_end",
            "policy_version",
            name="uq_archival_summary_period_policy",
        ),
    )
    op.create_index("ix_archival_summaries_clinic_id", "archival_summaries", ["clinic_id"])
    op.create_index("ix_archival_summaries_patient_id", "archival_summaries", ["patient_id"])

    op.create_table(
        "archival_summary_sources",
        sa.Column("archival_summary_id", sa.String(length=36), nullable=False),
        sa.Column("source_entry_id", sa.String(length=36), nullable=False),
        sa.Column("source_version_id", sa.String(length=36), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["archival_summary_id"], ["archival_summaries.id"]),
        sa.ForeignKeyConstraint(["source_entry_id"], ["entries.id"]),
        sa.ForeignKeyConstraint(["source_version_id"], ["entry_versions.id"]),
        sa.PrimaryKeyConstraint(
            "archival_summary_id",
            "source_entry_id",
            "source_version_id",
            name="pk_archival_summary_sources",
        ),
    )
    op.create_index(
        "ix_archival_summary_sources_entry",
        "archival_summary_sources",
        ["source_entry_id"],
    )
    op.create_index(
        "ix_archival_summary_sources_version",
        "archival_summary_sources",
        ["source_version_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_archival_summary_sources_version", table_name="archival_summary_sources")
    op.drop_index("ix_archival_summary_sources_entry", table_name="archival_summary_sources")
    op.drop_table("archival_summary_sources")
    op.drop_index("ix_archival_summaries_patient_id", table_name="archival_summaries")
    op.drop_index("ix_archival_summaries_clinic_id", table_name="archival_summaries")
    op.drop_table("archival_summaries")
