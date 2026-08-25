"""Normalize indexes left divergent by the published Gate A migration."""

import sqlalchemy as sa
from alembic import op


revision = "0003_gate_b_repair"
down_revision = "0002_gate_b"
branch_labels = None
depends_on = None


def _index_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    """Make both fresh and legacy Gate A databases use the normalized indexes."""

    # The already-published 0001 revision existed in two forms: an older local copy
    # created a non-unique email index and a patient_id index, while the committed
    # revision later expected a unique email index and no patient_id index. Drop and
    # recreate only these indexes so existing rows and all other indexes remain intact.
    if "ix_users_email" in _index_names("users"):
        op.drop_index("ix_users_email", table_name="users")
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    if "ix_patient_user_links_patient_id" in _index_names("patient_user_links"):
        op.drop_index(
            "ix_patient_user_links_patient_id",
            table_name="patient_user_links",
        )


def downgrade() -> None:
    """Intentionally leave normalized indexes in place when returning to 0002.

    Gate 0002's ORM metadata and the current application contract require these
    normalized indexes. Reintroducing the historical drift during downgrade would
    make ``alembic check`` fail and would recreate the defect this corrective
    migration repairs, so this downgrade is a documented schema no-op.
    """

    return None
