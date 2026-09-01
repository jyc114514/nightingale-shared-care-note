"""Add persistent external AI provider circuit state and safe job retry metadata."""

import sqlalchemy as sa
from alembic import op


revision = "0013_ai_provider_resilience"
down_revision = "0012_glance_impressions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ai_processing_jobs",
        sa.Column("retry_after_seconds", sa.Float(), nullable=True),
    )
    op.create_table(
        "ai_provider_circuits",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("clinic_id", sa.String(length=36), nullable=False),
        sa.Column("provider_name", sa.String(length=80), nullable=False),
        sa.Column("state", sa.String(length=20), nullable=False),
        sa.Column("consecutive_failures", sa.Integer(), nullable=False),
        sa.Column("failure_threshold", sa.Integer(), nullable=False),
        sa.Column("cooldown_seconds", sa.Float(), nullable=False),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("open_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_failure_code", sa.String(length=100), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "clinic_id",
            "provider_name",
            name="uq_ai_provider_circuit_clinic_provider",
        ),
        sa.CheckConstraint(
            "state IN ('closed', 'open', 'half_open')",
            name="ck_ai_provider_circuit_state",
        ),
        sa.CheckConstraint(
            "consecutive_failures >= 0 AND failure_threshold >= 1 AND cooldown_seconds > 0",
            name="ck_ai_provider_circuit_thresholds",
        ),
        sa.CheckConstraint("version >= 1", name="ck_ai_provider_circuit_version_positive"),
    )
    op.create_index(
        "ix_ai_provider_circuits_clinic_id",
        "ai_provider_circuits",
        ["clinic_id"],
    )
    op.create_index(
        "ix_ai_provider_circuits_clinic_state",
        "ai_provider_circuits",
        ["clinic_id", "state"],
    )


def downgrade() -> None:
    op.drop_index("ix_ai_provider_circuits_clinic_state", table_name="ai_provider_circuits")
    op.drop_index("ix_ai_provider_circuits_clinic_id", table_name="ai_provider_circuits")
    op.drop_table("ai_provider_circuits")
    op.drop_column("ai_processing_jobs", "retry_after_seconds")
