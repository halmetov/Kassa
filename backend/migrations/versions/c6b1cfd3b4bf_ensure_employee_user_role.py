"""ensure employee role exists in user_roles enum

Revision ID: c6b1cfd3b4bf
Revises: 9f2b7a54f4a5
Create Date: 2024-07-01 00:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "c6b1cfd3b4bf"
down_revision = "9f2b7a54f4a5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE user_roles ADD VALUE IF NOT EXISTS 'employee';")


def downgrade() -> None:
    # Removing values from enums in PostgreSQL requires recreating the type; skipping for safety.
    pass
