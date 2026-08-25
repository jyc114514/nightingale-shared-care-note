"""Add clinic-scoped adaptive importance feedback and ranking explanations."""

import sqlalchemy as sa
from alembic import op


revision = "0005_gate_d_importance"
down_revision = "0004_gate_c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create append-only feedback/profile tables and extend the read model."""

    op.create_table(
        "highlight_feedback_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("clinic_id", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.String(length=36), nullable=False),
        sa.Column("highlight_id", sa.String(length=36), nullable=False),
        sa.Column("actor_user_id", sa.String(length=36), nullable=False),
        sa.Column("actor_role", sa.String(length=20), nullable=False),
        sa.Column("event_type", sa.String(length=40), nullable=False),
        sa.Column("feature_signature", sa.String(length=300), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("idempotency_key", sa.String(length=200), nullable=False),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.ForeignKeyConstraint(["highlight_id"], ["highlights.id"]),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "clinic_id",
            "idempotency_key",
            name="uq_highlight_feedback_clinic_idempotency",
        ),
    )
    for column in ("clinic_id", "patient_id", "highlight_id", "feature_signature"):
        op.create_index(
            f"ix_highlight_feedback_events_{column}",
            "highlight_feedback_events",
            [column],
        )

    op.create_table(
        "importance_profiles",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("clinic_id", sa.String(length=36), nullable=False),
        sa.Column("feature_key", sa.String(length=300), nullable=False),
        sa.Column("positive_count", sa.Integer(), nullable=False),
        sa.Column("negative_count", sa.Integer(), nullable=False),
        sa.Column("bounded_weight", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "clinic_id",
            "feature_key",
            name="uq_importance_profile_clinic_feature",
        ),
    )
    op.create_index("ix_importance_profiles_clinic_id", "importance_profiles", ["clinic_id"])

    with op.batch_alter_table("patient_glance_items") as batch:
        batch.add_column(sa.Column("feature_signature", sa.String(length=300), nullable=True))
        batch.add_column(sa.Column("base_priority", sa.Float(), nullable=True))
        batch.add_column(sa.Column("recency_contribution", sa.Float(), nullable=True))
        batch.add_column(sa.Column("explicit_risk_contribution", sa.Float(), nullable=True))
        batch.add_column(sa.Column("unresolved_action_contribution", sa.Float(), nullable=True))
        batch.add_column(
            sa.Column("clinician_confirmation_contribution", sa.Float(), nullable=True)
        )
        batch.add_column(sa.Column("adaptive_feedback_adjustment", sa.Float(), nullable=True))
        batch.add_column(sa.Column("ranking_explanation", sa.Text(), nullable=True))

    op.execute(
        sa.text(
            """
            UPDATE patient_glance_items
            SET
                feature_signature = 'v1|entry_type=' || e.entry_type
                    || '|item_kind=' || h.item_kind
                    || '|source_kind=' || e.source_kind
                    || '|action_state=' || h.action_state
                    || '|risk=' || COALESCE(h.risk_level, 'none')
                    || '|topic=' || CASE
                        WHEN h.risk_level IS NOT NULL THEN 'risk'
                        WHEN h.action_state = 'open' THEN 'action'
                        ELSE 'context'
                    END,
                base_priority = h.display_priority,
                recency_contribution = 0.0,
                explicit_risk_contribution = CASE
                    WHEN h.risk_level IS NOT NULL THEN 12.0 ELSE 0.0 END,
                unresolved_action_contribution = CASE
                    WHEN h.action_state = 'open' THEN 15.0 ELSE 0.0 END,
                clinician_confirmation_contribution = CASE
                    WHEN h.status = 'accepted'
                      OR h.created_by_role = 'clinician'
                      OR h.reviewed_by_user_id IS NOT NULL
                    THEN 8.0 ELSE 0.0 END,
                adaptive_feedback_adjustment = 0.0,
                display_priority = CASE
                    WHEN h.display_priority
                        + CASE WHEN h.risk_level IS NOT NULL THEN 12.0 ELSE 0.0 END
                        + CASE WHEN h.action_state = 'open' THEN 15.0 ELSE 0.0 END
                        + CASE
                            WHEN h.status = 'accepted'
                              OR h.created_by_role = 'clinician'
                              OR h.reviewed_by_user_id IS NOT NULL
                            THEN 8.0 ELSE 0.0 END > 100.0
                    THEN 100.0
                    ELSE h.display_priority
                        + CASE WHEN h.risk_level IS NOT NULL THEN 12.0 ELSE 0.0 END
                        + CASE WHEN h.action_state = 'open' THEN 15.0 ELSE 0.0 END
                        + CASE
                            WHEN h.status = 'accepted'
                              OR h.created_by_role = 'clinician'
                              OR h.reviewed_by_user_id IS NOT NULL
                            THEN 8.0 ELSE 0.0 END
                END,
                ranking_explanation = '{}'
            FROM highlights h
            JOIN entries e ON e.id = h.source_entry_id
            WHERE h.id = patient_glance_items.highlight_id
            """
        )
    )

    with op.batch_alter_table("patient_glance_items") as batch:
        batch.alter_column("feature_signature", existing_type=sa.String(length=300), nullable=False)
        batch.alter_column("base_priority", existing_type=sa.Float(), nullable=False)
        batch.alter_column("recency_contribution", existing_type=sa.Float(), nullable=False)
        batch.alter_column("explicit_risk_contribution", existing_type=sa.Float(), nullable=False)
        batch.alter_column(
            "unresolved_action_contribution", existing_type=sa.Float(), nullable=False
        )
        batch.alter_column(
            "clinician_confirmation_contribution", existing_type=sa.Float(), nullable=False
        )
        batch.alter_column("adaptive_feedback_adjustment", existing_type=sa.Float(), nullable=False)
        batch.alter_column("ranking_explanation", existing_type=sa.Text(), nullable=False)

    op.create_index(
        "ix_patient_glance_items_feature_signature",
        "patient_glance_items",
        ["feature_signature"],
    )


def downgrade() -> None:
    """Remove adaptive state while preserving Gate C source and highlight data."""

    op.drop_index("ix_patient_glance_items_feature_signature", table_name="patient_glance_items")
    with op.batch_alter_table("patient_glance_items") as batch:
        for column in (
            "ranking_explanation",
            "adaptive_feedback_adjustment",
            "clinician_confirmation_contribution",
            "unresolved_action_contribution",
            "explicit_risk_contribution",
            "recency_contribution",
            "base_priority",
            "feature_signature",
        ):
            batch.drop_column(column)
    for column in ("clinic_id",):
        op.drop_index(f"ix_importance_profiles_{column}", table_name="importance_profiles")
    op.drop_table("importance_profiles")
    for column in ("feature_signature", "highlight_id", "patient_id", "clinic_id"):
        op.drop_index(
            f"ix_highlight_feedback_events_{column}",
            table_name="highlight_feedback_events",
        )
    op.drop_table("highlight_feedback_events")
