"""Merge heads for stock constraints and expenses branch

Revision ID: 8ffb3c4c3d7c
Revises: 1c42f6c52c1d, 4b3de2be4b1d
Create Date: 2025-07-01 00:00:00.000000
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "8ffb3c4c3d7c"
down_revision = ("1c42f6c52c1d", "4b3de2be4b1d")
branch_labels = None
depends_on = None


def upgrade() -> None:
    # This migration merges two branches without applying schema changes.
    pass


def downgrade() -> None:
    # Downgrade is not supported for merge migrations.
    pass
