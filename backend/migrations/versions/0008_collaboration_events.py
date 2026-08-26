"""Add persisted metadata-only collaboration invalidation events."""

import sqlalchemy as sa
from alembic import op


revision = "0008_collaboration_events"
down_revision = "0007_collaboration_mentions_tasks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "collaboration_events",
        sa.Column("event_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("clinic_id", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.String(length=36), nullable=False),
        sa.Column("resource_type", sa.String(length=40), nullable=False),
        sa.Column("resource_id", sa.String(length=36), nullable=False),
        sa.Column("event_kind", sa.String(length=60), nullable=False),
        sa.Column("actor_user_id", sa.String(length=36), nullable=True),
        sa.Column("actor_role", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("event_id"),
    )
    op.create_index("ix_collaboration_events_patient_id", "collaboration_events", ["patient_id"])
    op.create_index("ix_collaboration_events_clinic_id", "collaboration_events", ["clinic_id"])


def downgrade() -> None:
    op.drop_index("ix_collaboration_events_clinic_id", table_name="collaboration_events")
    op.drop_index("ix_collaboration_events_patient_id", table_name="collaboration_events")
    op.drop_table("collaboration_events")
