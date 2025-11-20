"""add branch_id to users

Revision ID: 35c52240b62f
Revises: 0001
Create Date: 2025-11-20 17:46:05.836266

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '35c52240b62f'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column("branch_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "users_branch_id_fkey",
        "users",
        "branches",
        ["branch_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade():
    op.drop_constraint("users_branch_id_fkey", "users", type_="foreignkey")
    op.drop_column("users", "branch_id")
