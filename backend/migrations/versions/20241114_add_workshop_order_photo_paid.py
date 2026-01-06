"""
Add photo and paid_amount to workshop orders
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20241114_add_workshop_order_photo_paid"
down_revision = "20240930_add_workshop_module"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("workshop_orders", sa.Column("photo", sa.String(length=500), nullable=True))
    op.add_column("workshop_orders", sa.Column("paid_amount", sa.Numeric(12, 2), nullable=True))


def downgrade() -> None:
    op.drop_column("workshop_orders", "paid_amount")
    op.drop_column("workshop_orders", "photo")
