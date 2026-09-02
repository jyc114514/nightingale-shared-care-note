"""Restore a default for legacy importance-feedback writers."""

import sqlalchemy as sa
from alembic import op


revision = "0015_feedback_backward_compat"
down_revision = "0014_patient_publications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Keep pre-0011 writers able to omit the newly added boolean column."""

    is_postgresql = op.get_bind().dialect.name == "postgresql"
    if is_postgresql:
        op.execute(
            sa.text(
                "UPDATE highlight_feedback_events "
                "SET applied_to_profile = TRUE "
                "WHERE applied_to_profile IS NULL"
            )
        )
        op.alter_column(
            "highlight_feedback_events",
            "applied_to_profile",
            existing_type=sa.Boolean(),
            nullable=False,
            server_default=sa.text("TRUE"),
        )
        return

    op.execute(
        sa.text(
            "UPDATE highlight_feedback_events "
            "SET applied_to_profile = 1 "
            "WHERE applied_to_profile IS NULL"
        )
    )
    with op.batch_alter_table("highlight_feedback_events") as batch:
        batch.alter_column(
            "applied_to_profile",
            existing_type=sa.Boolean(),
            nullable=False,
            server_default=sa.text("1"),
        )


def downgrade() -> None:
    """Remove only the compatibility default in disposable databases."""

    is_postgresql = op.get_bind().dialect.name == "postgresql"
    if is_postgresql:
        op.alter_column(
            "highlight_feedback_events",
            "applied_to_profile",
            existing_type=sa.Boolean(),
            existing_nullable=False,
            nullable=False,
            server_default=None,
        )
        return

    with op.batch_alter_table("highlight_feedback_events") as batch:
        batch.alter_column(
            "applied_to_profile",
            existing_type=sa.Boolean(),
            existing_nullable=False,
            nullable=False,
            server_default=None,
        )
