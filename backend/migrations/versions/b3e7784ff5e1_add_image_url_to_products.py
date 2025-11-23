"""add image url to products"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b3e7784ff5e1"
down_revision = "a5b7cbcfcb14"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("products", sa.Column("image_url", sa.String(length=500), nullable=True))
    op.execute(
        """
        UPDATE products
        SET image_url = photo
        WHERE image_url IS NULL AND photo IS NOT NULL
        """
    )


def downgrade():
    op.drop_column("products", "image_url")
