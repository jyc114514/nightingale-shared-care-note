"""Add the versioned patient publication safety gate."""

import sqlalchemy as sa
from alembic import op


revision = "0014_patient_publications"
down_revision = "0013_ai_provider_resilience"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "patient_publications",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("clinic_id", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.String(length=36), nullable=False),
        sa.Column("source_entry_id", sa.String(length=36), nullable=False),
        sa.Column("source_version_id", sa.String(length=36), nullable=False),
        sa.Column("state", sa.String(length=30), nullable=False),
        sa.Column("content_version", sa.Integer(), nullable=False),
        sa.Column("workflow_version", sa.Integer(), nullable=False),
        sa.Column("severity_class", sa.String(length=30), nullable=False),
        sa.Column("published_entry_id", sa.String(length=36), nullable=True),
        sa.Column("correction_of_publication_id", sa.String(length=36), nullable=True),
        sa.Column("superseded_by_publication_id", sa.String(length=36), nullable=True),
        sa.Column("created_by_user_id", sa.String(length=36), nullable=False),
        sa.Column("created_by_role", sa.String(length=20), nullable=False),
        sa.Column("approved_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_content_version", sa.Integer(), nullable=True),
        sa.Column("published_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("recalled_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("recalled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("recall_reason_code", sa.String(length=40), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.ForeignKeyConstraint(["source_entry_id"], ["entries.id"]),
        sa.ForeignKeyConstraint(["source_version_id"], ["entry_versions.id"]),
        sa.ForeignKeyConstraint(["published_entry_id"], ["entries.id"]),
        sa.ForeignKeyConstraint(
            ["correction_of_publication_id"], ["patient_publications.id"]
        ),
        sa.ForeignKeyConstraint(
            ["superseded_by_publication_id"], ["patient_publications.id"]
        ),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["published_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["recalled_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "state IN ('draft', 'clinician_approved', 'published', 'recalled', "
            "'superseded', 'entered_in_error')",
            name="ck_patient_publication_state",
        ),
        sa.CheckConstraint(
            "severity_class IN ('general', 'medication_dosage')",
            name="ck_patient_publication_severity",
        ),
        sa.CheckConstraint(
            "content_version >= 1 AND workflow_version >= 1",
            name="ck_patient_publication_versions_positive",
        ),
    )
    for name, columns in {
        "ix_patient_publications_clinic_id": ["clinic_id"],
        "ix_patient_publications_patient_id": ["patient_id"],
        "ix_patient_publications_clinic_patient": ["clinic_id", "patient_id"],
        "ix_patient_publications_source_entry_id": ["source_entry_id"],
        "ix_patient_publications_source_version_id": ["source_version_id"],
        "ix_patient_publications_state": ["state"],
    }.items():
        op.create_index(name, "patient_publications", columns)

    op.create_table(
        "patient_publication_versions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("publication_id", sa.String(length=36), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_sha256", sa.String(length=64), nullable=False),
        sa.Column("created_by_user_id", sa.String(length=36), nullable=False),
        sa.Column("created_by_role", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["publication_id"], ["patient_publications.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "publication_id",
            "version_number",
            name="uq_patient_publication_version_number",
        ),
    )
    op.create_index(
        "ix_patient_publication_versions_publication_id",
        "patient_publication_versions",
        ["publication_id"],
    )

    op.create_table(
        "patient_publication_evidence",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("publication_id", sa.String(length=36), nullable=False),
        sa.Column("publication_version_id", sa.String(length=36), nullable=False),
        sa.Column("evidence_type", sa.String(length=40), nullable=False),
        sa.Column("concept_key", sa.String(length=100), nullable=False),
        sa.Column("normalized_value", sa.String(length=100), nullable=True),
        sa.Column("unit", sa.String(length=30), nullable=True),
        sa.Column("frequency", sa.String(length=50), nullable=True),
        sa.Column("source_entry_id", sa.String(length=36), nullable=False),
        sa.Column("source_version_id", sa.String(length=36), nullable=False),
        sa.Column("start_offset", sa.Integer(), nullable=False),
        sa.Column("end_offset", sa.Integer(), nullable=False),
        sa.Column("quote", sa.Text(), nullable=False),
        sa.Column("quote_sha256", sa.String(length=64), nullable=False),
        sa.Column("offset_unit", sa.String(length=30), nullable=False),
        sa.Column("validation_status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["publication_id"], ["patient_publications.id"]),
        sa.ForeignKeyConstraint(
            ["publication_version_id"], ["patient_publication_versions.id"]
        ),
        sa.ForeignKeyConstraint(["source_entry_id"], ["entries.id"]),
        sa.ForeignKeyConstraint(["source_version_id"], ["entry_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("start_offset >= 0 AND end_offset >= start_offset", name="ck_patient_publication_evidence_offsets"),
        sa.CheckConstraint(
            "validation_status IN ('matched', 'mismatch', 'ambiguous', 'unsupported', 'missing')",
            name="ck_patient_publication_evidence_status",
        ),
    )
    for name, columns in {
        "ix_patient_publication_evidence_publication_id": ["publication_id"],
        "ix_patient_publication_evidence_source_version_id": ["source_version_id"],
    }.items():
        op.create_index(name, "patient_publication_evidence", columns)


def downgrade() -> None:
    op.drop_index(
        "ix_patient_publication_evidence_source_version_id",
        table_name="patient_publication_evidence",
    )
    op.drop_index(
        "ix_patient_publication_evidence_publication_id",
        table_name="patient_publication_evidence",
    )
    op.drop_table("patient_publication_evidence")
    op.drop_index(
        "ix_patient_publication_versions_publication_id",
        table_name="patient_publication_versions",
    )
    op.drop_table("patient_publication_versions")
    for name in (
        "ix_patient_publications_state",
        "ix_patient_publications_source_version_id",
        "ix_patient_publications_source_entry_id",
        "ix_patient_publications_clinic_patient",
        "ix_patient_publications_patient_id",
        "ix_patient_publications_clinic_id",
    ):
        op.drop_index(name, table_name="patient_publications")
    op.drop_table("patient_publications")
