"""add employee to user_roles enum

Revision ID: 8f2e92c6c7e4
Revises: 7bb00c40f9a4
Create Date: 2025-05-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "8f2e92c6c7e4"
down_revision = "7bb00c40f9a4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE user_roles ADD VALUE IF NOT EXISTS 'employee';")


def downgrade() -> None:
    pass
