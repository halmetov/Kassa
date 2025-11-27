"""add movements tables

Revision ID: 1c0d7f5a9c2b
Revises: f0f6af3a443a
Create Date: 2024-11-25 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1c0d7f5a9c2b"
down_revision = "f0f6af3a443a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "movements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("from_branch_id", sa.Integer(), nullable=False),
        sa.Column("to_branch_id", sa.Integer(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="draft"),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["from_branch_id"], ["branches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["to_branch_id"], ["branches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
    )

    op.create_table(
        "movement_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("movement_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("purchase_price", sa.Float(), nullable=True),
        sa.Column("selling_price", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["movement_id"], ["movements.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
    )

    op.create_index("ix_movements_from_branch_id", "movements", ["from_branch_id"])
    op.create_index("ix_movements_to_branch_id", "movements", ["to_branch_id"])


def downgrade() -> None:
    op.drop_index("ix_movements_to_branch_id", table_name="movements")
    op.drop_index("ix_movements_from_branch_id", table_name="movements")
    op.drop_table("movement_items")
    op.drop_table("movements")

