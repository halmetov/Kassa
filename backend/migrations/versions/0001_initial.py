"""initial tables

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00
"""

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("login", sa.String(length=255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.Enum("admin", "employee", name="user_roles"), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id", ondelete="SET NULL")),
        sa.Column("photo", sa.String(500)),
        sa.Column("unit", sa.String(50)),
        sa.Column("barcode", sa.String(255), unique=True),
        sa.Column("purchase_price", sa.Float(), server_default="0"),
        sa.Column("sale_price", sa.Float(), server_default="0"),
        sa.Column("wholesale_price", sa.Float(), server_default="0"),
        sa.Column("limit", sa.Integer()),
        sa.Column("quantity", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "branches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), unique=True, nullable=False),
        sa.Column("address", sa.String(255)),
        sa.Column("active", sa.Boolean(), server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(50)),
        sa.Column("total_debt", sa.Float(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "stock",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("branch_id", sa.Integer(), sa.ForeignKey("branches.id", ondelete="CASCADE")),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE")),
        sa.Column("quantity", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "income",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("branch_id", sa.Integer(), sa.ForeignKey("branches.id")),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "income_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("income_id", sa.Integer(), sa.ForeignKey("income.id", ondelete="CASCADE")),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id")),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("purchase_price", sa.Float(), nullable=False),
        sa.Column("sale_price", sa.Float(), nullable=False),
    )
    op.create_table(
        "sales",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("branch_id", sa.Integer(), sa.ForeignKey("branches.id")),
        sa.Column("seller_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("client_id", sa.Integer(), sa.ForeignKey("clients.id")),
        sa.Column("cash", sa.Float(), server_default="0"),
        sa.Column("kaspi", sa.Float(), server_default="0"),
        sa.Column("credit", sa.Float(), server_default="0"),
        sa.Column("total", sa.Float(), server_default="0"),
        sa.Column("payment_type", sa.String(50), server_default="cash"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "sales_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sale_id", sa.Integer(), sa.ForeignKey("sales.id", ondelete="CASCADE")),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id")),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
    )
    op.create_table(
        "debts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("client_id", sa.Integer(), sa.ForeignKey("clients.id")),
        sa.Column("sale_id", sa.Integer(), sa.ForeignKey("sales.id")),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("paid", sa.Float(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "returns",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sale_id", sa.Integer(), sa.ForeignKey("sales.id")),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id")),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("processed_by", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("action", sa.String(255), nullable=False),
        sa.Column("payload", sa.Text()),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    for table in [
        "logs",
        "returns",
        "debts",
        "sales_items",
        "sales",
        "income_items",
        "income",
        "stock",
        "clients",
        "branches",
        "products",
        "categories",
        "users",
    ]:
        op.drop_table(table)
    op.execute("DROP TYPE IF EXISTS user_roles")
