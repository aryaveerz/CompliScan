"""add structured declarations table

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-09-19 13:10:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'structured_declaration_results',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('evidence_id', sa.String(length=36), nullable=False),
        sa.Column('inspection_id', sa.String(length=36), nullable=False),
        sa.Column('ocr_result_id', sa.String(length=36), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False, server_default='google'),
        sa.Column('model_name', sa.String(length=100), nullable=False, server_default='gemini-2.5-flash'),
        sa.Column('model_version', sa.String(length=100), nullable=True),
        sa.Column('prompt_version', sa.String(length=50), nullable=False, server_default='v1.0'),
        sa.Column('extraction_version', sa.String(length=50), nullable=False, server_default='v1.0'),
        sa.Column('extraction_status', sa.String(length=50), nullable=False, server_default='COMPLETED'),
        sa.Column('processing_blocked', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('block_reason', sa.String(length=100), nullable=True),
        sa.Column('declarations', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['evidence_id'], ['evidence_assets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['inspection_id'], ['inspections.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ocr_result_id'], ['ocr_results.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('evidence_id', 'extraction_version', 'model_name', name='uq_extraction_evidence_version_model')
    )
    op.create_index(op.f('ix_structured_declaration_results_evidence_id'), 'structured_declaration_results', ['evidence_id'], unique=False)
    op.create_index(op.f('ix_structured_declaration_results_inspection_id'), 'structured_declaration_results', ['inspection_id'], unique=False)
    op.create_index(op.f('ix_structured_declaration_results_ocr_result_id'), 'structured_declaration_results', ['ocr_result_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_structured_declaration_results_ocr_result_id'), table_name='structured_declaration_results')
    op.drop_index(op.f('ix_structured_declaration_results_inspection_id'), table_name='structured_declaration_results')
    op.drop_index(op.f('ix_structured_declaration_results_evidence_id'), table_name='structured_declaration_results')
    op.drop_table('structured_declaration_results')
