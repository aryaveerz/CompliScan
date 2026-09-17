"""make users hashed_password nullable

Revision ID: 8f4e21a69b12
Revises: cd32f3498b6b
Create Date: 2026-09-17

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f4e21a69b12'
down_revision = 'cd32f3498b6b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        'users',
        'hashed_password',
        existing_type=sa.String(length=255),
        nullable=True,
    )


def downgrade() -> None:
    # Fail explicitly if any users have NULL hashed_password rather than fabricating credentials.
    conn = op.get_bind()
    null_count = conn.execute(
        sa.text("SELECT COUNT(*) FROM users WHERE hashed_password IS NULL")
    ).scalar()
    if null_count and null_count > 0:
        raise RuntimeError(
            f"Cannot downgrade migration: {null_count} user(s) have NULL hashed_password. "
            "Restoring NOT NULL without valid password hashes would cause data corruption or invalid state."
        )

    op.alter_column(
        'users',
        'hashed_password',
        existing_type=sa.String(length=255),
        nullable=False,
    )
