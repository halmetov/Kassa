"""ensure users table with branch_id

Revision ID: 42a39ac573f4
Revises: 35c52240b62f
Create Date: 2025-11-20 17:59:32.681057

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '42a39ac573f4'
down_revision = '35c52240b62f'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [column["name"] for column in inspector.get_columns("users")]

    if "branch_id" not in columns:
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
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [column["name"] for column in inspector.get_columns("users")]

    if "branch_id" in columns:
        with op.batch_alter_table("users") as batch_op:
            batch_op.drop_constraint("users_branch_id_fkey", type_="foreignkey")
            batch_op.drop_column("branch_id")
