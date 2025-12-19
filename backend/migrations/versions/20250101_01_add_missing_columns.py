"""Add missing product image_url and sales total_amount columns

Revision ID: 20250101_add_missing_columns
Revises: 347276f5ad8c
Create Date: 2025-01-01
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "20250101_add_missing_columns"
down_revision = "347276f5ad8c"
branch_labels = None
depends_on = None


def _column_missing(inspector, table: str, column: str) -> bool:
    columns = inspector.get_columns(table)  # type: ignore[arg-type]
    return all(col["name"] != column for col in columns)


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    if _column_missing(inspector, "products", "image_url"):
        op.add_column("products", sa.Column("image_url", sa.String(length=500), nullable=True))

    if _column_missing(inspector, "sales", "total_amount"):
        op.add_column(
            "sales",
            sa.Column(
                "total_amount",
                sa.Numeric(precision=12, scale=2),
                nullable=False,
                server_default="0",
            ),
        )
        op.execute(sa.text("UPDATE sales SET total_amount = 0 WHERE total_amount IS NULL"))
        op.alter_column("sales", "total_amount", server_default=None)


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    if not _column_missing(inspector, "sales", "total_amount"):
        op.drop_column("sales", "total_amount")
    if not _column_missing(inspector, "products", "image_url"):
        op.drop_column("products", "image_url")
