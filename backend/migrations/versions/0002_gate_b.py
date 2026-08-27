"""Add Gate B timeline metadata, threaded comments, and provenance highlights."""

import sqlalchemy as sa
from alembic import op


revision = "0002_gate_b"
down_revision = "0001_gate_a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Extend existing Gate A rows without replacing immutable history."""

    op.add_column("entries", sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("entries", sa.Column("source_kind", sa.String(length=40), nullable=True))
    op.add_column("entries", sa.Column("source_reference", sa.String(length=200), nullable=True))
    op.execute(sa.text("UPDATE entries SET occurred_at = created_at WHERE occurred_at IS NULL"))
    op.execute(
        sa.text(
            """
            UPDATE entries
            SET source_kind = CASE
                WHEN entry_type = 'ai_doctor_consult_summary' THEN 'doctor_consult'
                WHEN entry_type = 'ai_nurse_consult_summary' THEN 'nurse_consult'
                WHEN entry_type = 'ai_patient_session_summary' THEN 'patient_ai_session'
                WHEN entry_type = 'system_event' THEN 'system_event'
                ELSE 'manual'
            END
            WHERE source_kind IS NULL
            """
        )
    )
    op.execute(
        sa.text(
            "UPDATE entries SET source_reference = 'migrated-' || id "
            "WHERE entry_type IN "
            "('ai_doctor_consult_summary', 'ai_nurse_consult_summary', "
            "'ai_patient_session_summary') AND source_reference IS NULL"
        )
    )
    if op.get_bind().dialect.name == "postgresql":
        # PostgreSQL can alter these columns in place. Recreate-always would
        # try to drop entries_pkey while entry_versions/comments/conflicts
        # still reference it during a fresh deployment.
        op.alter_column(
            "entries",
            "occurred_at",
            existing_type=sa.DateTime(timezone=True),
            nullable=False,
        )
        op.alter_column(
            "entries",
            "source_kind",
            existing_type=sa.String(length=40),
            nullable=False,
        )
    else:
        with op.batch_alter_table("entries", recreate="always") as batch:
            batch.alter_column("occurred_at", nullable=False)
            batch.alter_column("source_kind", nullable=False)

    with op.batch_alter_table("comments", recreate="always") as batch:
        batch.add_column(sa.Column("parent_comment_id", sa.String(length=36), nullable=True))
        batch.add_column(sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("resolved_by_user_id", sa.String(length=36), nullable=True))
        batch.add_column(sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))
        batch.create_foreign_key(
            "fk_comments_parent_comment_id", "comments", ["parent_comment_id"], ["id"]
        )
        batch.create_foreign_key(
            "fk_comments_resolved_by_user_id", "users", ["resolved_by_user_id"], ["id"]
        )
    op.execute(sa.text("UPDATE comments SET updated_at = created_at WHERE updated_at IS NULL"))
    with op.batch_alter_table("comments", recreate="always") as batch:
        batch.alter_column("updated_at", nullable=False)
    op.create_index("ix_comments_parent_comment_id", "comments", ["parent_comment_id"])

    op.create_table(
        "highlights",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("clinic_id", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.String(length=36), nullable=False),
        sa.Column("source_entry_id", sa.String(length=36), nullable=False),
        sa.Column("source_version_id", sa.String(length=36), nullable=False),
        sa.Column("start_offset", sa.Integer(), nullable=False),
        sa.Column("end_offset", sa.Integer(), nullable=False),
        sa.Column("quote", sa.Text(), nullable=False),
        sa.Column("quote_sha256", sa.String(length=64), nullable=False),
        sa.Column("offset_unit", sa.String(length=30), nullable=False),
        sa.Column("item_kind", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("display_priority", sa.Float(), nullable=False),
        sa.Column("risk_level", sa.String(length=50), nullable=True),
        sa.Column("risk_reason", sa.String(length=300), nullable=False),
        sa.Column("action_label", sa.String(length=200), nullable=True),
        sa.Column("action_state", sa.String(length=30), nullable=False),
        sa.Column("created_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("created_by_role", sa.String(length=20), nullable=False),
        sa.Column("reviewed_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.ForeignKeyConstraint(["reviewed_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["source_entry_id"], ["entries.id"]),
        sa.ForeignKeyConstraint(["source_version_id"], ["entry_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("clinic_id", "patient_id", "source_entry_id", "source_version_id", "status"):
        op.create_index(f"ix_highlights_{column}", "highlights", [column])


def downgrade() -> None:
    """Remove Gate B tables/columns while leaving Gate A history intact."""

    for column in ("clinic_id", "patient_id", "source_entry_id", "source_version_id", "status"):
        op.drop_index(f"ix_highlights_{column}", table_name="highlights")
    op.drop_table("highlights")
    op.drop_index("ix_comments_parent_comment_id", table_name="comments")
    with op.batch_alter_table("comments", recreate="always") as batch:
        batch.drop_constraint("fk_comments_parent_comment_id", type_="foreignkey")
        batch.drop_constraint("fk_comments_resolved_by_user_id", type_="foreignkey")
        batch.drop_column("parent_comment_id")
        batch.drop_column("resolved_at")
        batch.drop_column("resolved_by_user_id")
        batch.drop_column("updated_at")
    with op.batch_alter_table("entries", recreate="always") as batch:
        batch.drop_column("occurred_at")
        batch.drop_column("source_kind")
        batch.drop_column("source_reference")
