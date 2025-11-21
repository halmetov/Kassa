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
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("branch_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "users_branch_id_fkey",
            "branches",
            ["branch_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_constraint("users_branch_id_fkey", type_="foreignkey")
        batch_op.drop_column("branch_id")
