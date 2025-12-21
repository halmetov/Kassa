"""Make product photo fields nullable

Revision ID: 20250308_make_product_images_nullable
Revises: 20250202_01_add_product_photo_and_image_url
Create Date: 2025-03-08
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "20250308_make_product_images_nullable"
down_revision = "20250202_01_add_product_photo_and_image_url"
branch_labels = None
depends_on = None


def _get_column_info(inspector, table: str, column: str) -> dict | None:
    for col in inspector.get_columns(table):  # type: ignore[arg-type]
        if col["name"] == column:
            return col
    return None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    for column in ("photo", "image_url"):
        column_info = _get_column_info(inspector, "products", column)
        if column_info is None:
            op.add_column("products", sa.Column(column, sa.String(length=500), nullable=True))
        elif not column_info.get("nullable", True):
            op.alter_column(
                "products",
                column,
                existing_type=sa.String(length=500),
                nullable=True,
            )


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    for column in ("photo", "image_url"):
        column_info = _get_column_info(inspector, "products", column)
        if column_info is not None:
            op.alter_column(
                "products",
                column,
                existing_type=sa.String(length=500),
                nullable=False,
            )
