"""Make product fields optional with sane defaults

Revision ID: 20250315_update_product_nullable_defaults
Revises: 20250308_make_product_images_nullable
Create Date: 2025-03-15
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20250315_update_product_nullable_defaults"
down_revision = "20250308_make_product_images_nullable"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(sa.text("UPDATE products SET unit = COALESCE(NULLIF(TRIM(unit), ''), 'шт')"))
    op.execute(sa.text('UPDATE products SET "limit" = COALESCE("limit", 0)'))
    op.execute(sa.text("UPDATE products SET purchase_price = COALESCE(purchase_price, 0)"))
    op.execute(sa.text("UPDATE products SET sale_price = COALESCE(sale_price, 0)"))
    op.execute(sa.text("UPDATE products SET wholesale_price = COALESCE(wholesale_price, 0)"))
    op.execute(sa.text("UPDATE products SET quantity = COALESCE(quantity, 0)"))

    op.alter_column(
        "products",
        "unit",
        existing_type=sa.String(length=50),
        nullable=True,
        server_default=sa.text("'шт'"),
    )
    op.alter_column(
        "products",
        "purchase_price",
        existing_type=sa.Float(),
        nullable=True,
        server_default=sa.text("0"),
    )
    op.alter_column(
        "products",
        "sale_price",
        existing_type=sa.Float(),
        nullable=True,
        server_default=sa.text("0"),
    )
    op.alter_column(
        "products",
        "wholesale_price",
        existing_type=sa.Float(),
        nullable=True,
        server_default=sa.text("0"),
    )
    op.alter_column(
        "products",
        "limit",
        existing_type=sa.Integer(),
        nullable=True,
        server_default=sa.text("0"),
    )
    op.alter_column(
        "products",
        "quantity",
        existing_type=sa.Integer(),
        nullable=False,
        server_default=sa.text("0"),
    )
    op.alter_column(
        "products",
        "photo",
        existing_type=sa.String(length=500),
        nullable=True,
    )
    op.alter_column(
        "products",
        "image_url",
        existing_type=sa.String(length=500),
        nullable=True,
    )


def downgrade():
    op.alter_column(
        "products",
        "image_url",
        existing_type=sa.String(length=500),
        nullable=False,
    )
    op.alter_column(
        "products",
        "photo",
        existing_type=sa.String(length=500),
        nullable=False,
    )
    op.alter_column(
        "products",
        "quantity",
        existing_type=sa.Integer(),
        nullable=False,
        server_default=None,
    )
    op.alter_column(
        "products",
        "limit",
        existing_type=sa.Integer(),
        nullable=False,
        server_default=None,
    )
    op.alter_column(
        "products",
        "wholesale_price",
        existing_type=sa.Float(),
        nullable=False,
        server_default=None,
    )
    op.alter_column(
        "products",
        "sale_price",
        existing_type=sa.Float(),
        nullable=False,
        server_default=None,
    )
    op.alter_column(
        "products",
        "purchase_price",
        existing_type=sa.Float(),
        nullable=False,
        server_default=None,
    )
    op.alter_column(
        "products",
        "unit",
        existing_type=sa.String(length=50),
        nullable=False,
        server_default=None,
    )
