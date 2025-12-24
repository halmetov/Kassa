"""Add debt payment links and created by

Revision ID: 0f78a5e29f1e
Revises: d5e5d45f742a
Create Date: 2025-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0f78a5e29f1e"
down_revision = "d5e5d45f742a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("debt_payments", sa.Column("debt_id", sa.Integer(), nullable=True))
    op.add_column("debt_payments", sa.Column("created_by_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_debt_payments_debt_id_debts",
        "debt_payments",
        "debts",
        ["debt_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_debt_payments_created_by_id_users",
        "debt_payments",
        "users",
        ["created_by_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_debt_payments_created_by_id_users", "debt_payments", type_="foreignkey")
    op.drop_constraint("fk_debt_payments_debt_id_debts", "debt_payments", type_="foreignkey")
    op.drop_column("debt_payments", "created_by_id")
    op.drop_column("debt_payments", "debt_id")
