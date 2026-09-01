"""Add source-anchored allergy assertions and protected clinical conflicts."""

import sqlalchemy as sa
from alembic import op


revision = "0011_real_clinic_safety"
down_revision = "0010_postgres_compat"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add the additive clinical safety tables and nullable projection fields."""

    op.create_table(
        "clinical_assertions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("clinic_id", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.String(length=36), nullable=False),
        sa.Column("domain", sa.String(length=30), nullable=False),
        sa.Column("concept_key", sa.String(length=100), nullable=False),
        sa.Column("polarity", sa.String(length=20), nullable=False),
        sa.Column("verification_status", sa.String(length=30), nullable=False),
        sa.Column("criticality", sa.String(length=30), nullable=False),
        sa.Column("source_entry_id", sa.String(length=36), nullable=False),
        sa.Column("source_version_id", sa.String(length=36), nullable=False),
        sa.Column("start_offset", sa.Integer(), nullable=False),
        sa.Column("end_offset", sa.Integer(), nullable=False),
        sa.Column("quote", sa.Text(), nullable=False),
        sa.Column("quote_sha256", sa.String(length=64), nullable=False),
        sa.Column("offset_unit", sa.String(length=30), nullable=False),
        sa.Column("asserted_by_role", sa.String(length=20), nullable=False),
        sa.Column("asserted_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("superseded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.ForeignKeyConstraint(["source_entry_id"], ["entries.id"]),
        sa.ForeignKeyConstraint(["source_version_id"], ["entry_versions.id"]),
        sa.ForeignKeyConstraint(["asserted_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source_version_id",
            "start_offset",
            "end_offset",
            "domain",
            "concept_key",
            "polarity",
            name="uq_clinical_assertion_source_span",
        ),
    )
    for column in (
        "clinic_id",
        "patient_id",
        "concept_key",
        "source_entry_id",
        "source_version_id",
        "status",
    ):
        op.create_index(f"ix_clinical_assertions_{column}", "clinical_assertions", [column])
    op.create_index(
        "ix_clinical_assertions_concept_polarity",
        "clinical_assertions",
        ["concept_key", "polarity"],
    )

    op.create_table(
        "clinical_conflicts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("clinic_id", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.String(length=36), nullable=False),
        sa.Column("conflict_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("positive_assertion_id", sa.String(length=36), nullable=False),
        sa.Column("negative_assertion_id", sa.String(length=36), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("resolution", sa.String(length=40), nullable=True),
        sa.Column("adjudicated_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("adjudicated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.ForeignKeyConstraint(["positive_assertion_id"], ["clinical_assertions.id"]),
        sa.ForeignKeyConstraint(["negative_assertion_id"], ["clinical_assertions.id"]),
        sa.ForeignKeyConstraint(["adjudicated_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "positive_assertion_id",
            "negative_assertion_id",
            name="uq_clinical_conflict_assertion_pair",
        ),
        sa.CheckConstraint(
            "positive_assertion_id <> negative_assertion_id",
            name="ck_clinical_conflict_distinct_assertions",
        ),
        sa.CheckConstraint("version >= 1", name="ck_clinical_conflict_version_positive"),
    )
    for column in ("clinic_id", "patient_id", "status"):
        op.create_index(f"ix_clinical_conflicts_{column}", "clinical_conflicts", [column])
    op.create_index(
        "ix_clinical_conflicts_clinic_patient",
        "clinical_conflicts",
        ["clinic_id", "patient_id"],
    )

    op.add_column(
        "highlights",
        sa.Column("clinical_conflict_id", sa.String(length=36), nullable=True),
    )
    op.add_column("highlights", sa.Column("safety_class", sa.String(length=50), nullable=True))
    op.add_column("highlights", sa.Column("safety_floor", sa.Float(), nullable=True))
    op.create_index("ix_highlights_clinical_conflict_id", "highlights", ["clinical_conflict_id"])

    op.add_column(
        "patient_glance_items",
        sa.Column("clinical_conflict_id", sa.String(length=36), nullable=True),
    )
    op.add_column(
        "patient_glance_items",
        sa.Column("safety_class", sa.String(length=50), nullable=True),
    )
    op.add_column("patient_glance_items", sa.Column("safety_floor", sa.Float(), nullable=True))
    op.create_index(
        "ix_patient_glance_items_clinical_conflict_id",
        "patient_glance_items",
        ["clinical_conflict_id"],
    )

    default = sa.text("TRUE") if op.get_bind().dialect.name == "postgresql" else sa.text("1")
    op.add_column(
        "highlight_feedback_events",
        sa.Column("applied_to_profile", sa.Boolean(), nullable=False, server_default=default),
    )
    op.add_column(
        "highlight_feedback_events",
        sa.Column("suppression_reason", sa.String(length=100), nullable=True),
    )
    if op.get_bind().dialect.name == "postgresql":
        op.alter_column("highlight_feedback_events", "applied_to_profile", server_default=None)


def downgrade() -> None:
    """Remove only the additive Round 1 safety schema."""

    op.drop_column("highlight_feedback_events", "suppression_reason")
    op.drop_column("highlight_feedback_events", "applied_to_profile")

    op.drop_index(
        "ix_patient_glance_items_clinical_conflict_id",
        table_name="patient_glance_items",
    )
    op.drop_column("patient_glance_items", "safety_floor")
    op.drop_column("patient_glance_items", "safety_class")
    op.drop_column("patient_glance_items", "clinical_conflict_id")

    op.drop_index("ix_highlights_clinical_conflict_id", table_name="highlights")
    op.drop_column("highlights", "safety_floor")
    op.drop_column("highlights", "safety_class")
    op.drop_column("highlights", "clinical_conflict_id")

    op.drop_index(
        "ix_clinical_conflicts_clinic_patient",
        table_name="clinical_conflicts",
    )
    for column in ("status", "patient_id", "clinic_id"):
        op.drop_index(f"ix_clinical_conflicts_{column}", table_name="clinical_conflicts")
    op.drop_table("clinical_conflicts")

    op.drop_index(
        "ix_clinical_assertions_concept_polarity",
        table_name="clinical_assertions",
    )
    for column in (
        "status",
        "source_version_id",
        "source_entry_id",
        "concept_key",
        "patient_id",
        "clinic_id",
    ):
        op.drop_index(f"ix_clinical_assertions_{column}", table_name="clinical_assertions")
    op.drop_table("clinical_assertions")
