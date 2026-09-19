"""add phase5 performance indexes

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-09-19 20:10:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6a7b8c9d0e1'
down_revision: Union[str, None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Composite index for inspections filtering by category and status
    op.create_index(
        'idx_inspections_category_status',
        'inspections',
        ['product_category', 'status'],
        unique=False
    )

    # 2. Index for sorting/filtering inspections by created_at
    op.create_index(
        'idx_inspections_created_at',
        'inspections',
        ['created_at'],
        unique=False
    )

    # 3. Composite index for chronological audit event queries per inspection
    op.create_index(
        'idx_audit_events_inspection_created',
        'audit_events',
        ['inspection_id', 'created_at'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('idx_audit_events_inspection_created', table_name='audit_events')
    op.drop_index('idx_inspections_created_at', table_name='inspections')
    op.drop_index('idx_inspections_category_status', table_name='inspections')
