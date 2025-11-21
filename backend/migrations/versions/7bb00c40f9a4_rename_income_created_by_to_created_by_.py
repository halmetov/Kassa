"""rename income.created_by to created_by_id

Revision ID: 7bb00c40f9a4
Revises: 4da0cd4e82b0
Create Date: 2025-11-21 07:54:01.261753

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7bb00c40f9a4'
down_revision = '4da0cd4e82b0'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    cols = [c["name"] for c in inspector.get_columns("income")]

    if "created_by_id" not in cols and "created_by" in cols:
        op.alter_column("income", "created_by", new_column_name="created_by_id")


def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    cols = [c["name"] for c in inspector.get_columns("income")]

    if "created_by" not in cols and "created_by_id" in cols:
        op.alter_column("income", "created_by_id", new_column_name="created_by")
