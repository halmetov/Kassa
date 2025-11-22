"""ensure sales total_amount and user_roles consistency

Revision ID: 9f2b7a54f4a5
Revises: 2f7687c57499
Create Date: 2024-06-11 00:00:00
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "9f2b7a54f4a5"
down_revision = "2f7687c57499"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    sales_columns = {column["name"] for column in inspector.get_columns("sales")}
    if "total_amount" not in sales_columns:
        if "total" in sales_columns:
            op.alter_column("sales", "total", new_column_name="total_amount")
        else:
            op.add_column("sales", sa.Column("total_amount", sa.Float(), server_default="0"))

    op.execute(
        """
        UPDATE sales
        SET total_amount = COALESCE(total_amount, 0)
        """
    )
    op.execute(
        """
        WITH item_totals AS (
            SELECT si.sale_id, COALESCE(SUM(si.total), SUM((si.price - COALESCE(si.discount, 0)) * si.quantity), 0) AS total
            FROM sales_items si
            GROUP BY si.sale_id
        )
        UPDATE sales s
        SET total_amount = it.total
        FROM item_totals it
        WHERE s.id = it.sale_id AND (s.total_amount IS NULL OR s.total_amount = 0)
        """
    )

    op.execute("ALTER TYPE user_roles ADD VALUE IF NOT EXISTS 'employee';")
    op.execute("UPDATE users SET role = 'employee' WHERE role = 'seller';")


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    sales_columns = {column["name"] for column in inspector.get_columns("sales")}
    if "total_amount" in sales_columns and "total" not in sales_columns:
        op.alter_column("sales", "total_amount", new_column_name="total")

    # Cannot remove enum values in PostgreSQL safely; downgrade is a no-op for enum changes
