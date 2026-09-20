"""production identity and location schema updates

Revision ID: h8i9j0k1l2m3
Revises: g7h8i9j0k1l2
Create Date: 2026-09-20 14:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'h8i9j0k1l2m3'
down_revision: Union[str, None] = 'g7h8i9j0k1l2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add officer identity columns to users table
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('officer_id', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('designation', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('department', sa.String(length=150), nullable=True))
        batch_op.add_column(sa.Column('unit_office', sa.String(length=150), nullable=True))

    # 2. Add location_data and inspection timestamps to inspections table
    with op.batch_alter_table('inspections') as batch_op:
        batch_op.add_column(sa.Column('location_data', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('inspection_started_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('inspection_completed_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('inspections') as batch_op:
        batch_op.drop_column('inspection_completed_at')
        batch_op.drop_column('inspection_started_at')
        batch_op.drop_column('location_data')

    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('unit_office')
        batch_op.drop_column('department')
        batch_op.drop_column('designation')
        batch_op.drop_column('officer_id')
