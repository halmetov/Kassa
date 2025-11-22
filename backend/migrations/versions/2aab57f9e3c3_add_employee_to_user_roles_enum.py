"""add employee to user_roles enum

Revision ID: 2aab57f9e3c3
Revises: 8f2e92c6c7e4
Create Date: 2025-11-21 13:34:41.080844

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2aab57f9e3c3'
down_revision = '8f2e92c6c7e4'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE user_roles ADD VALUE IF NOT EXISTS 'employee';")
    op.execute("UPDATE users SET role = 'employee' WHERE role = 'seller';")


def downgrade():
    pass
