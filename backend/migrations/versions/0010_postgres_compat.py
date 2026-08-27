"""Normalize the redundant PostgreSQL users email uniqueness constraint."""

import sqlalchemy as sa
from alembic import op


revision = "0010_postgres_compat"
down_revision = "0009_voice_capture"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Keep the ORM's unique email index without a duplicate table constraint."""

    if op.get_bind().dialect.name != "postgresql":
        return

    inspector = sa.inspect(op.get_bind())
    for constraint in inspector.get_unique_constraints("users"):
        if constraint.get("column_names") == ["email"] and constraint.get("name"):
            op.drop_constraint(constraint["name"], "users", type_="unique")


def downgrade() -> None:
    """Leave the normalized index in place when returning to 0009."""

    return None
