"""
Add workshop module tables and workshop flag

Revision ID: 20240930_add_workshop_module
Revises: 20240918_add_production
Create Date: 2024-09-30
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20240930_add_workshop_module"
down_revision = "20240918_add_production"
branch_labels = None
depends_on = None


user_roles_enum_name = "user_roles"


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type t JOIN pg_enum e ON t.oid = e.enumtypid WHERE t.typname = 'user_roles' AND e.enumlabel = 'manager') THEN
                ALTER TYPE user_roles ADD VALUE 'manager';
            END IF;
        END$$;
        """
        )

    op.add_column("branches", sa.Column("is_workshop", sa.Boolean(), server_default=sa.text("false"), nullable=False))
    op.execute("UPDATE branches SET is_workshop = true WHERE name = 'Цех'")

    op.create_table(
        "workshop_employees",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("first_name", sa.String(length=255), nullable=False),
        sa.Column("last_name", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("total_salary", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "workshop_orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("customer_name", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default=sa.text("'open'")),
        sa.Column("created_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("branch_id", sa.Integer(), sa.ForeignKey("branches.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "workshop_order_materials",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("workshop_orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("quantity", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("unit", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "workshop_order_payouts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("workshop_orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("employee_id", sa.Integer(), sa.ForeignKey("workshop_employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "workshop_order_closures",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("workshop_orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("order_amount", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("paid_amount", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_unique_constraint(
        "uq_workshop_closure_order", "workshop_order_closures", ["order_id"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_workshop_closure_order", "workshop_order_closures", type_="unique")
    op.drop_table("workshop_order_closures")
    op.drop_table("workshop_order_payouts")
    op.drop_table("workshop_order_materials")
    op.drop_table("workshop_orders")
    op.drop_table("workshop_employees")
    op.drop_column("branches", "is_workshop")
