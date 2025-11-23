"""ensure sales total amount column exists and is populated"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a5b7cbcfcb14"
down_revision = "f0f6af3a443a"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    sales_columns = {column["name"] for column in inspector.get_columns("sales")}
    added_column = False

    if "total_amount" not in sales_columns:
        if "total" in sales_columns:
            op.alter_column("sales", "total", new_column_name="total_amount")
        else:
            op.add_column(
                "sales",
                sa.Column("total_amount", sa.Float(), nullable=False, server_default="0"),
            )
            added_column = True

    sales_item_columns = {column["name"] for column in inspector.get_columns("sales_items")}
    discount_expr = "COALESCE(si.discount, 0)" if "discount" in sales_item_columns else "0"

    op.execute(
        """
        UPDATE sales
        SET total_amount = COALESCE(total_amount, 0)
        """
    )

    op.execute(
        f"""
        UPDATE sales s
        SET total_amount = totals.total
        FROM (
            SELECT si.sale_id, COALESCE(SUM((si.price - {discount_expr}) * si.quantity), 0) AS total
            FROM sales_items si
            GROUP BY si.sale_id
        ) totals
        WHERE s.id = totals.sale_id
        """
    )

    if added_column:
        op.alter_column("sales", "total_amount", server_default=None)


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    sales_columns = {column["name"] for column in inspector.get_columns("sales")}

    if "total_amount" in sales_columns:
        if "total" in sales_columns:
            op.drop_column("sales", "total_amount")
        else:
            op.alter_column("sales", "total_amount", new_column_name="total")
