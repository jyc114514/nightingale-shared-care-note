"""Add metadata-only Glance exposure impression batches and candidates."""

import sqlalchemy as sa
from alembic import op


revision = "0012_glance_impressions"
down_revision = "0011_real_clinic_safety"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "glance_impression_batches",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("clinic_id", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.String(length=36), nullable=False),
        sa.Column("actor_user_id", sa.String(length=36), nullable=False),
        sa.Column("actor_role", sa.String(length=20), nullable=False),
        sa.Column("idempotency_key", sa.String(length=200), nullable=False),
        sa.Column("algorithm_version", sa.String(length=80), nullable=False),
        sa.Column("requested_limit", sa.Integer(), nullable=False),
        sa.Column("eligible_count", sa.Integer(), nullable=False),
        sa.Column("stored_candidate_count", sa.Integer(), nullable=False),
        sa.Column("surfaced_count", sa.Integer(), nullable=False),
        sa.Column("candidate_truncated", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "clinic_id",
            "idempotency_key",
            name="uq_glance_impression_batch_clinic_idempotency",
        ),
        sa.CheckConstraint(
            "requested_limit >= 1 AND requested_limit <= 6",
            name="ck_glance_impression_batch_limit",
        ),
        sa.CheckConstraint(
            "eligible_count >= 0 AND stored_candidate_count >= 0 AND surfaced_count >= 0",
            name="ck_glance_impression_batch_counts",
        ),
    )
    for column in ("clinic_id", "patient_id", "actor_user_id"):
        op.create_index(
            f"ix_glance_impression_batches_{column}",
            "glance_impression_batches",
            [column],
        )

    op.create_table(
        "glance_impression_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("batch_id", sa.String(length=36), nullable=False),
        sa.Column("resource_type", sa.String(length=20), nullable=False),
        sa.Column("resource_id", sa.String(length=36), nullable=False),
        sa.Column("feature_signature", sa.String(length=300), nullable=False),
        sa.Column("candidate_rank", sa.Integer(), nullable=False),
        sa.Column("surfaced", sa.Boolean(), nullable=False),
        sa.Column("display_priority", sa.Float(), nullable=False),
        sa.Column("safety_class", sa.String(length=50), nullable=True),
        sa.Column("safety_floor", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["batch_id"], ["glance_impression_batches.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "batch_id",
            "resource_type",
            "resource_id",
            name="uq_glance_impression_item_resource",
        ),
        sa.CheckConstraint("candidate_rank >= 1", name="ck_glance_impression_item_rank"),
    )
    op.create_index("ix_glance_impression_items_batch_id", "glance_impression_items", ["batch_id"])
    op.create_index(
        "ix_glance_impression_items_feature_signature",
        "glance_impression_items",
        ["feature_signature"],
    )
    op.create_index(
        "ix_glance_impression_items_safety_class",
        "glance_impression_items",
        ["safety_class"],
    )
    op.create_index(
        "ix_glance_impression_items_feature_surfaced",
        "glance_impression_items",
        ["feature_signature", "surfaced"],
    )
    op.create_index(
        "ix_glance_impression_items_surfaced",
        "glance_impression_items",
        ["surfaced"],
    )


def downgrade() -> None:
    op.drop_index("ix_glance_impression_items_surfaced", table_name="glance_impression_items")
    op.drop_index(
        "ix_glance_impression_items_feature_surfaced",
        table_name="glance_impression_items",
    )
    op.drop_index(
        "ix_glance_impression_items_safety_class",
        table_name="glance_impression_items",
    )
    op.drop_index(
        "ix_glance_impression_items_feature_signature",
        table_name="glance_impression_items",
    )
    op.drop_index("ix_glance_impression_items_batch_id", table_name="glance_impression_items")
    op.drop_table("glance_impression_items")
    for column in ("actor_user_id", "patient_id", "clinic_id"):
        op.drop_index(
            f"ix_glance_impression_batches_{column}",
            table_name="glance_impression_batches",
        )
    op.drop_table("glance_impression_batches")
