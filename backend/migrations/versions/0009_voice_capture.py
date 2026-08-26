"""Add metadata and immutable segments for the optional synthetic voice prototype."""

import sqlalchemy as sa
from alembic import op


revision = "0009_voice_capture"
down_revision = "0008_collaboration_events"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "voice_sessions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("clinic_id", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.String(length=36), nullable=False),
        sa.Column("created_by_user_id", sa.String(length=36), nullable=False),
        sa.Column("actor_role", sa.String(length=20), nullable=False),
        sa.Column("interaction_type", sa.String(length=50), nullable=False),
        sa.Column("sample_id", sa.String(length=80), nullable=False),
        sa.Column("audio_reference", sa.String(length=200), nullable=False),
        sa.Column("audio_sha256", sa.String(length=64), nullable=False),
        sa.Column("audio_duration_ms", sa.Integer(), nullable=False),
        sa.Column("asr_provider", sa.String(length=50), nullable=False),
        sa.Column("asr_model", sa.String(length=100), nullable=False),
        sa.Column("language", sa.String(length=20), nullable=False),
        sa.Column("language_probability", sa.Float(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("error_code", sa.String(length=100), nullable=True),
        sa.Column("idempotency_key", sa.String(length=200), nullable=False),
        sa.Column("entry_id", sa.String(length=36), nullable=True),
        sa.Column("highlight_id", sa.String(length=36), nullable=True),
        sa.Column("source_segment_id", sa.String(length=36), nullable=True),
        sa.Column("transcript_sha256", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["entry_id"], ["entries.id"]),
        sa.ForeignKeyConstraint(["highlight_id"], ["highlights.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("clinic_id", "patient_id", "sample_id", "status"):
        op.create_index(f"ix_voice_sessions_{column}", "voice_sessions", [column])
    op.create_index(
        "uq_voice_session_clinic_idempotency",
        "voice_sessions",
        ["clinic_id", "idempotency_key"],
        unique=True,
    )

    op.create_table(
        "transcript_segments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("voice_session_id", sa.String(length=36), nullable=False),
        sa.Column("segment_index", sa.Integer(), nullable=False),
        sa.Column("start_ms", sa.Integer(), nullable=False),
        sa.Column("end_ms", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["voice_session_id"], ["voice_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "voice_session_id",
            "segment_index",
            name="uq_transcript_segment_session_index",
        ),
    )
    op.create_index(
        "ix_transcript_segments_voice_session_id",
        "transcript_segments",
        ["voice_session_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_transcript_segments_voice_session_id",
        table_name="transcript_segments",
    )
    op.drop_table("transcript_segments")
    op.drop_index(
        "uq_voice_session_clinic_idempotency",
        table_name="voice_sessions",
    )
    for column in ("status", "sample_id", "patient_id", "clinic_id"):
        op.drop_index(f"ix_voice_sessions_{column}", table_name="voice_sessions")
    op.drop_table("voice_sessions")
