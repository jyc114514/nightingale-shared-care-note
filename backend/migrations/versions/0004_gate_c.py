"""Add the Gate C redacted processing job and materialized Glance read model."""

import sqlalchemy as sa
from alembic import op


revision = "0004_gate_c"
down_revision = "0003_gate_b_repair"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create Gate C tables and materialize all existing synthetic highlights."""

    op.create_table(
        "ai_processing_jobs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("clinic_id", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.String(length=36), nullable=False),
        sa.Column("interaction_type", sa.String(length=50), nullable=False),
        sa.Column("provider_name", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("idempotency_key", sa.String(length=200), nullable=False),
        sa.Column("input_hash", sa.String(length=64), nullable=False),
        sa.Column("source_reference", sa.String(length=200), nullable=False),
        sa.Column("redacted_payload", sa.Text(), nullable=True),
        sa.Column("error_code", sa.String(length=100), nullable=True),
        sa.Column("entry_id", sa.String(length=36), nullable=True),
        sa.Column("highlight_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.ForeignKeyConstraint(["entry_id"], ["entries.id"]),
        sa.ForeignKeyConstraint(["highlight_id"], ["highlights.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "clinic_id",
            "idempotency_key",
            name="uq_ai_processing_job_clinic_idempotency",
        ),
    )
    for column in ("clinic_id", "patient_id", "status"):
        op.create_index(f"ix_ai_processing_jobs_{column}", "ai_processing_jobs", [column])

    op.create_table(
        "patient_glance_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("highlight_id", sa.String(length=36), nullable=False),
        sa.Column("clinic_id", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.String(length=36), nullable=False),
        sa.Column("source_entry_id", sa.String(length=36), nullable=False),
        sa.Column("source_version_id", sa.String(length=36), nullable=False),
        sa.Column("start_offset", sa.Integer(), nullable=False),
        sa.Column("end_offset", sa.Integer(), nullable=False),
        sa.Column("quote_sha256", sa.String(length=64), nullable=False),
        sa.Column("offset_unit", sa.String(length=30), nullable=False),
        sa.Column("content_summary", sa.Text(), nullable=False),
        sa.Column("item_kind", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("display_priority", sa.Float(), nullable=False),
        sa.Column("risk_level", sa.String(length=50), nullable=True),
        sa.Column("risk_reason", sa.String(length=300), nullable=False),
        sa.Column("action_label", sa.String(length=200), nullable=True),
        sa.Column("action_state", sa.String(length=30), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("current_entry_version", sa.Integer(), nullable=False),
        sa.Column("source_label", sa.String(length=120), nullable=False),
        sa.Column("entry_type", sa.String(length=50), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("quote", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["highlight_id"], ["highlights.id"]),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.ForeignKeyConstraint(["source_entry_id"], ["entries.id"]),
        sa.ForeignKeyConstraint(["source_version_id"], ["entry_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("highlight_id", name="uq_patient_glance_item_highlight"),
    )
    for column in (
        "highlight_id",
        "clinic_id",
        "patient_id",
        "source_entry_id",
        "source_version_id",
        "status",
    ):
        op.create_index(f"ix_patient_glance_items_{column}", "patient_glance_items", [column])

    op.execute(
        sa.text(
            """
            INSERT INTO patient_glance_items (
                id, highlight_id, clinic_id, patient_id, source_entry_id,
                source_version_id, content_summary, item_kind, status,
                start_offset, end_offset, quote_sha256, offset_unit,
                display_priority, risk_level, risk_reason, action_label,
                action_state, version_number, current_entry_version,
                source_label, entry_type, occurred_at, quote, created_at, updated_at
            )
            SELECT
                h.id, h.id, h.clinic_id, h.patient_id, h.source_entry_id,
                h.source_version_id, h.quote, h.item_kind, h.status,
                h.start_offset, h.end_offset, h.quote_sha256, h.offset_unit,
                h.display_priority, h.risk_level, h.risk_reason, h.action_label,
                h.action_state, v.version_number, e.current_version,
                CASE e.source_kind
                    WHEN 'doctor_consult' THEN 'AI-scribed - Doctor consult'
                    WHEN 'nurse_consult' THEN 'AI-scribed - Nurse consult'
                    WHEN 'patient_ai_session' THEN 'AI-scribed - Patient session'
                    WHEN 'system_event' THEN 'System event'
                    ELSE 'Manual note'
                END,
                e.entry_type, e.occurred_at, h.quote, h.created_at, h.updated_at
            FROM highlights h
            JOIN entries e ON e.id = h.source_entry_id
            JOIN entry_versions v ON v.id = h.source_version_id
            """
        )
    )


def downgrade() -> None:
    """Remove only Gate C tables; Gate B source and highlight history remains."""

    for column in (
        "highlight_id",
        "clinic_id",
        "patient_id",
        "source_entry_id",
        "source_version_id",
        "status",
    ):
        op.drop_index(f"ix_patient_glance_items_{column}", table_name="patient_glance_items")
    op.drop_table("patient_glance_items")
    for column in ("clinic_id", "patient_id", "status"):
        op.drop_index(f"ix_ai_processing_jobs_{column}", table_name="ai_processing_jobs")
    op.drop_table("ai_processing_jobs")
