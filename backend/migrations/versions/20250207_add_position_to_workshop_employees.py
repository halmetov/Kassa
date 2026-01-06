"""Add position to workshop employees

Revision ID: 20250207_add_workshop_employee_position
Revises: 20241114_add_workshop_order_photo_paid
Create Date: 2025-02-07
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20250207_add_workshop_employee_position"
down_revision = "20241114_add_workshop_order_photo_paid"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("workshop_employees", sa.Column("position", sa.String(length=120), nullable=True, server_default=""))
    op.alter_column("workshop_employees", "position", server_default=None)


def downgrade() -> None:
    op.drop_column("workshop_employees", "position")
