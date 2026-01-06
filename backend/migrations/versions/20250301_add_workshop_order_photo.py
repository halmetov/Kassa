"""Ensure workshop order photo column exists

Revision ID: 20250301_add_workshop_order_photo
Revises: 20250207_add_workshop_employee_position
Create Date: 2025-03-01
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20250301_add_workshop_order_photo"
down_revision = "20250207_add_workshop_employee_position"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [column["name"] for column in inspector.get_columns("workshop_orders")]
    if "photo" not in columns:
        op.add_column("workshop_orders", sa.Column("photo", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("workshop_orders", "photo")
