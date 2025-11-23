"""normalize user_roles enum to lowercase values and clean data

Revision ID: f0f6af3a443a
Revises: c6b1cfd3b4bf
Create Date: 2024-08-25 00:00:00.000000
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "f0f6af3a443a"
down_revision = "c6b1cfd3b4bf"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_enum e ON t.oid = e.enumtypid
                WHERE t.typname = 'user_roles' AND e.enumlabel = 'ADMIN'
            ) THEN
                ALTER TYPE user_roles RENAME VALUE 'ADMIN' TO 'admin';
            END IF;

            IF EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_enum e ON t.oid = e.enumtypid
                WHERE t.typname = 'user_roles' AND e.enumlabel = 'EMPLOYEE'
            ) THEN
                ALTER TYPE user_roles RENAME VALUE 'EMPLOYEE' TO 'employee';
            END IF;
        END $$;
        """
    )

    op.execute("ALTER TYPE user_roles ADD VALUE IF NOT EXISTS 'employee';")

    op.execute("UPDATE users SET role = 'admin' WHERE role IN ('ADMIN', 'Admin', 'Админ');")
    op.execute(
        "UPDATE users SET role = 'employee' WHERE role IN ('EMPLOYEE', 'Employee', 'Сотрудник', 'seller');"
    )


def downgrade() -> None:
    # Reverting enum changes safely would require recreating the type; skipping for safety.
    pass
