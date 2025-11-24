"""add total_amount to sales

Revision ID: e4025d85b1e6
Revises: b3e7784ff5e1
Create Date: 2025-11-24 10:37:10.907964
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e4025d85b1e6'
down_revision = 'b3e7784ff5e1'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    sales_columns = {column["name"] for column in inspector.get_columns("sales")}
    added_column = False

    if "total_amount" not in sales_columns:
        op.add_column(
            "sales",
            sa.Column(
                "total_amount",
                sa.Numeric(12, 2),
                nullable=False,
                server_default="0",
            ),
        )
        added_column = True
    else:
        op.alter_column("sales", "total_amount", type_=sa.Numeric(12, 2))

    op.execute(sa.text("UPDATE sales SET total_amount = COALESCE(total_amount, 0)"))

    items_table = None
    for candidate in ("sale_items", "sales_items"):
        if candidate in inspector.get_table_names():
            items_table = candidate
            break

    if items_table:
        op.execute(
            sa.text(
                f"""
                UPDATE sales s
                SET total_amount = sub.total
                FROM (
                    SELECT sale_id, SUM(quantity * price) AS total
                    FROM {items_table}
                    GROUP BY sale_id
                ) AS sub
                WHERE sub.sale_id = s.id;
                """
            )
        )

    if added_column:
        op.alter_column("sales", "total_amount", server_default=None)


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    sales_columns = {column["name"] for column in inspector.get_columns("sales")}

    if "total_amount" in sales_columns:
        op.alter_column("sales", "total_amount", type_=sa.Float())
