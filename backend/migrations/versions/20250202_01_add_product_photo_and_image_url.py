"""Ensure product photo and image_url columns exist

Revision ID: 20250202_01_add_product_photo_and_image_url
Revises: 20250101_add_missing_columns
Create Date: 2025-02-02
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "20250202_01_add_product_photo_and_image_url"
down_revision = "20250101_add_missing_columns"
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

    if _column_missing(inspector, "products", "photo"):
        op.add_column("products", sa.Column("photo", sa.String(length=500), nullable=True))


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    if not _column_missing(inspector, "products", "photo"):
        op.drop_column("products", "photo")

    if not _column_missing(inspector, "products", "image_url"):
        op.drop_column("products", "image_url")
