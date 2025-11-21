"""sync models with database

Revision ID: 4da0cd4e82b0
Revises: 42a39ac573f4
Create Date: 2024-05-08 00:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "4da0cd4e82b0"
down_revision = "42a39ac573f4"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("income", schema=None) as batch_op:
        batch_op.alter_column(
            "created_by",
            new_column_name="created_by_id",
            existing_type=sa.Integer(),
            nullable=False,
        )

    with op.batch_alter_table("returns", schema=None) as batch_op:
        batch_op.alter_column(
            "processed_by",
            new_column_name="processed_by_id",
            existing_type=sa.Integer(),
            nullable=False,
        )

    with op.batch_alter_table("logs", schema=None) as batch_op:
        batch_op.alter_column(
            "created_by",
            new_column_name="created_by_id",
            existing_type=sa.Integer(),
            nullable=True,
        )


def downgrade():
    with op.batch_alter_table("logs", schema=None) as batch_op:
        batch_op.alter_column(
            "created_by_id",
            new_column_name="created_by",
            existing_type=sa.Integer(),
            nullable=True,
        )

    with op.batch_alter_table("returns", schema=None) as batch_op:
        batch_op.alter_column(
            "processed_by_id",
            new_column_name="processed_by",
            existing_type=sa.Integer(),
            nullable=False,
        )

    with op.batch_alter_table("income", schema=None) as batch_op:
        batch_op.alter_column(
            "created_by_id",
            new_column_name="created_by",
            existing_type=sa.Integer(),
            nullable=False,
        )
