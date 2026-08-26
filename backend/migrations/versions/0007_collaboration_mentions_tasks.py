"""Add clinic-scoped mentions, assignments, task conflicts, and task projections."""

import sqlalchemy as sa
from alembic import op


revision = "0007_collaboration_mentions_tasks"
down_revision = "0006_gate_d_archival"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "mentions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("clinic_id", sa.String(length=36), nullable=False),
        sa.Column("comment_id", sa.String(length=36), nullable=False),
        sa.Column("mentioned_user_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"]),
        sa.ForeignKeyConstraint(["comment_id"], ["comments.id"]),
        sa.ForeignKeyConstraint(["mentioned_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("comment_id", "mentioned_user_id", name="uq_mention_comment_user"),
    )
    op.create_index("ix_mentions_clinic_id", "mentions", ["clinic_id"])
    op.create_index("ix_mentions_comment_id", "mentions", ["comment_id"])
    op.create_index("ix_mentions_mentioned_user_id", "mentions", ["mentioned_user_id"])

    op.create_table(
        "tasks",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("clinic_id", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.String(length=36), nullable=False),
        sa.Column("source_entry_id", sa.String(length=36), nullable=True),
        sa.Column("source_comment_id", sa.String(length=36), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("created_by_user_id", sa.String(length=36), nullable=False),
        sa.Column("assigned_to_user_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.ForeignKeyConstraint(["source_entry_id"], ["entries.id"]),
        sa.ForeignKeyConstraint(["source_comment_id"], ["comments.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["assigned_to_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("clinic_id", "patient_id", "source_entry_id", "source_comment_id", "status"):
        op.create_index(f"ix_tasks_{column}", "tasks", [column])

    op.create_table(
        "task_conflicts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("clinic_id", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.String(length=36), nullable=False),
        sa.Column("task_id", sa.String(length=36), nullable=False),
        sa.Column("submitted_by_user_id", sa.String(length=36), nullable=False),
        sa.Column("expected_version", sa.Integer(), nullable=False),
        sa.Column("actual_version", sa.Integer(), nullable=False),
        sa.Column("attempted_title", sa.String(length=200), nullable=False),
        sa.Column("attempted_assignee_user_id", sa.String(length=36), nullable=False),
        sa.Column("attempted_status", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"]),
        sa.ForeignKeyConstraint(["submitted_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["attempted_assignee_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("clinic_id", "patient_id", "task_id"):
        op.create_index(f"ix_task_conflicts_{column}", "task_conflicts", [column])

    op.create_table(
        "task_glance_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("task_id", sa.String(length=36), nullable=False),
        sa.Column("clinic_id", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.String(length=36), nullable=False),
        sa.Column("source_entry_id", sa.String(length=36), nullable=True),
        sa.Column("source_comment_id", sa.String(length=36), nullable=True),
        sa.Column("content_summary", sa.Text(), nullable=False),
        sa.Column("display_priority", sa.Integer(), nullable=False),
        sa.Column("action_label", sa.String(length=200), nullable=False),
        sa.Column("action_state", sa.String(length=20), nullable=False),
        sa.Column("assigned_to_user_id", sa.String(length=36), nullable=False),
        sa.Column("assigned_to_display_name", sa.String(length=200), nullable=False),
        sa.Column("task_status", sa.String(length=20), nullable=False),
        sa.Column("task_version", sa.Integer(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"]),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.ForeignKeyConstraint(["source_entry_id"], ["entries.id"]),
        sa.ForeignKeyConstraint(["source_comment_id"], ["comments.id"]),
        sa.ForeignKeyConstraint(["assigned_to_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("task_id", name="uq_task_glance_task"),
    )
    for column in ("task_id", "clinic_id", "patient_id", "source_entry_id", "source_comment_id"):
        op.create_index(f"ix_task_glance_items_{column}", "task_glance_items", [column])


def downgrade() -> None:
    for column in ("task_id", "clinic_id", "patient_id", "source_entry_id", "source_comment_id"):
        op.drop_index(f"ix_task_glance_items_{column}", table_name="task_glance_items")
    op.drop_table("task_glance_items")
    for column in ("task_id", "patient_id", "clinic_id"):
        op.drop_index(f"ix_task_conflicts_{column}", table_name="task_conflicts")
    op.drop_table("task_conflicts")
    for column in ("status", "source_comment_id", "source_entry_id", "patient_id", "clinic_id"):
        op.drop_index(f"ix_tasks_{column}", table_name="tasks")
    op.drop_table("tasks")
    op.drop_index("ix_mentions_mentioned_user_id", table_name="mentions")
    op.drop_index("ix_mentions_comment_id", table_name="mentions")
    op.drop_index("ix_mentions_clinic_id", table_name="mentions")
    op.drop_table("mentions")
