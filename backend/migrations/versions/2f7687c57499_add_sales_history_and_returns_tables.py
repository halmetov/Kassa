"""add sales history and returns tables

Revision ID: 2f7687c57499
Revises: 2aab57f9e3c3
Create Date: 2025-11-21 13:34:49.061576

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2f7687c57499'
down_revision = '2aab57f9e3c3'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    sales_columns = {column["name"] for column in inspector.get_columns("sales")}
    if "total" in sales_columns:
        op.alter_column("sales", "total", new_column_name="total_amount")
    if "cash" in sales_columns:
        op.alter_column("sales", "cash", new_column_name="paid_cash")
    if "kaspi" in sales_columns:
        op.alter_column("sales", "kaspi", new_column_name="paid_card")
    if "credit" in sales_columns:
        op.alter_column("sales", "credit", new_column_name="paid_debt")

    sales_item_columns = {column["name"] for column in inspector.get_columns("sales_items")}
    if "discount" not in sales_item_columns:
        op.add_column("sales_items", sa.Column("discount", sa.Float(), server_default="0"))
    if "total" not in sales_item_columns:
        op.add_column("sales_items", sa.Column("total", sa.Float(), server_default="0"))

    existing_tables = inspector.get_table_names()
    if "return_items" in existing_tables:
        op.drop_table("return_items")
    if "returns" in existing_tables:
        op.drop_table("returns")

    return_type_enum = sa.Enum("by_receipt", "by_item", name="return_type")
    return_type_enum.create(bind, checkfirst=True)

    op.create_table(
        "returns",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sale_id", sa.Integer(), sa.ForeignKey("sales.id", ondelete="CASCADE"), nullable=False),
        sa.Column("branch_id", sa.Integer(), sa.ForeignKey("branches.id"), nullable=False),
        sa.Column("type", return_type_enum, nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "return_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("return_id", sa.Integer(), sa.ForeignKey("returns.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sale_item_id", sa.Integer(), sa.ForeignKey("sales_items.id"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False, server_default="0"),
    )


def downgrade():
    op.drop_table("return_items")
    op.drop_table("returns")

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    sales_columns = {column["name"] for column in inspector.get_columns("sales")}
    if "paid_debt" in sales_columns:
        op.alter_column("sales", "paid_debt", new_column_name="credit")
    if "paid_card" in sales_columns:
        op.alter_column("sales", "paid_card", new_column_name="kaspi")
    if "paid_cash" in sales_columns:
        op.alter_column("sales", "paid_cash", new_column_name="cash")
    if "total_amount" in sales_columns:
        op.alter_column("sales", "total_amount", new_column_name="total")

    sales_item_columns = {column["name"] for column in inspector.get_columns("sales_items")}
    if "discount" in sales_item_columns:
        op.drop_column("sales_items", "discount")
    if "total" in sales_item_columns:
        op.drop_column("sales_items", "total")
