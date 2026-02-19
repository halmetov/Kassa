"""ensure branch_id in users

Revision ID: 8d5d37de6062
Revises: 4da0cd4e82b0
Create Date: 2025-11-21 06:42:21.501356

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8d5d37de6062"
down_revision = "4da0cd4e82b0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    columns = [column["name"] for column in inspector.get_columns("users")]

    if "branch_id" not in columns:
        op.add_column("users", sa.Column("branch_id", sa.Integer(), nullable=True))
        fk_names = [fk["name"] for fk in inspector.get_foreign_keys("users")]
        if "users_branch_id_fkey" not in fk_names:
            op.create_foreign_key(
                "users_branch_id_fkey",
                "users",
                "branches",
                ["branch_id"],
                ["id"],
                ondelete="SET NULL",
            )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    columns = [column["name"] for column in inspector.get_columns("users")]
    if "branch_id" in columns:
        fk_names = [fk["name"] for fk in inspector.get_foreign_keys("users")]
        if "users_branch_id_fkey" in fk_names:
            op.drop_constraint("users_branch_id_fkey", "users", type_="foreignkey")
        op.drop_column("users", "branch_id")
