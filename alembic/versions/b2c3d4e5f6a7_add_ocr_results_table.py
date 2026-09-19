"""add ocr results table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-09-19 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'ocr_results',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('evidence_id', sa.String(length=36), nullable=False),
        sa.Column('inspection_id', sa.String(length=36), nullable=False),
        sa.Column('ocr_engine', sa.String(length=50), nullable=False),
        sa.Column('ocr_engine_version', sa.String(length=100), nullable=False),
        sa.Column('processing_version', sa.String(length=50), nullable=False),
        sa.Column('processing_blocked', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('block_reason', sa.String(length=100), nullable=True),
        sa.Column('total_tokens', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('full_text', sa.Text(), nullable=True),
        sa.Column('tokens', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['evidence_id'], ['evidence_assets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['inspection_id'], ['inspections.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('evidence_id', 'processing_version', name='uq_ocr_evidence_version')
    )
    op.create_index(op.f('ix_ocr_results_evidence_id'), 'ocr_results', ['evidence_id'], unique=False)
    op.create_index(op.f('ix_ocr_results_inspection_id'), 'ocr_results', ['inspection_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_ocr_results_inspection_id'), table_name='ocr_results')
    op.drop_index(op.f('ix_ocr_results_evidence_id'), table_name='ocr_results')
    op.drop_table('ocr_results')
