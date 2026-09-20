"""forensic remediation schema updates

Revision ID: g7h8i9j0k1l2
Revises: f6a7b8c9d0e1
Create Date: 2026-09-20 12:25:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'g7h8i9j0k1l2'
down_revision: Union[str, None] = 'f6a7b8c9d0e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Expand block_reason to TEXT and add block_code & telemetry to structured_declaration_results
    with op.batch_alter_table('structured_declaration_results') as batch_op:
        batch_op.alter_column('block_reason', type_=sa.Text(), existing_type=sa.String(length=100), nullable=True)
        batch_op.add_column(sa.Column('block_code', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('telemetry', sa.JSON(), nullable=True))

    # 2. Create product_declarations table for multi-image deterministic synthesis
    op.create_table(
        'product_declarations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('inspection_id', sa.String(length=36), nullable=False),
        sa.Column('synthesis_version', sa.String(length=50), nullable=False, server_default='v1.0'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='SYNTHESIZED'),
        sa.Column('total_evidence_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('synthesized_declarations', sa.JSON(), nullable=False),
        sa.Column('conflict_summary', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['inspection_id'], ['inspections.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('inspection_id', 'synthesis_version', name='uq_product_declaration_inspection_version')
    )
    op.create_index(op.f('ix_product_declarations_inspection_id'), 'product_declarations', ['inspection_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_product_declarations_inspection_id'), table_name='product_declarations')
    op.drop_table('product_declarations')

    with op.batch_alter_table('structured_declaration_results') as batch_op:
        batch_op.drop_column('telemetry')
        batch_op.drop_column('block_code')
        batch_op.alter_column('block_reason', type_=sa.String(length=100), existing_type=sa.Text(), nullable=True)
