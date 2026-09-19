"""add phase3 compliance tables

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-09-19 14:35:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Applicability Results Table
    op.create_table(
        'applicability_results',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('inspection_id', sa.String(length=36), nullable=False),
        sa.Column('requirement_name', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('basis', sa.Text(), nullable=False),
        sa.Column('rule_citation', sa.String(length=100), nullable=False),
        sa.Column('context_used', sa.JSON(), nullable=False),
        sa.Column('rule_set_id', sa.String(length=100), nullable=False, server_default='LMPC-2011-MVP-RULES'),
        sa.Column('rule_set_version', sa.String(length=50), nullable=False, server_default='v1.0'),
        sa.Column('evaluation_version', sa.String(length=50), nullable=False, server_default='v1.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['inspection_id'], ['inspections.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('inspection_id', 'requirement_name', 'evaluation_version', name='uq_applicability_inspection_req_version')
    )
    op.create_index(op.f('ix_applicability_results_inspection_id'), 'applicability_results', ['inspection_id'], unique=False)
    op.create_index(op.f('ix_applicability_results_requirement_name'), 'applicability_results', ['requirement_name'], unique=False)

    # 2. Compliance Findings Table
    op.create_table(
        'compliance_findings',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('inspection_id', sa.String(length=36), nullable=False),
        sa.Column('evidence_id', sa.String(length=36), nullable=True),
        sa.Column('ocr_result_id', sa.String(length=36), nullable=True),
        sa.Column('structured_declaration_result_id', sa.String(length=36), nullable=True),
        sa.Column('requirement_name', sa.String(length=100), nullable=False),
        sa.Column('result', sa.String(length=50), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('applicability_status', sa.String(length=50), nullable=False),
        sa.Column('rule_citation', sa.String(length=100), nullable=False),
        sa.Column('rule_set_id', sa.String(length=100), nullable=False, server_default='LMPC-2011-MVP-RULES'),
        sa.Column('rule_set_version', sa.String(length=50), nullable=False, server_default='v1.0'),
        sa.Column('evaluation_version', sa.String(length=50), nullable=False, server_default='v1.0'),
        sa.Column('source_token_indices', sa.JSON(), nullable=False),
        sa.Column('metadata_payload', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['evidence_id'], ['evidence_assets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['inspection_id'], ['inspections.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ocr_result_id'], ['ocr_results.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['structured_declaration_result_id'], ['structured_declaration_results.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('inspection_id', 'evidence_id', 'requirement_name', 'evaluation_version', name='uq_finding_inspection_evidence_req_version')
    )
    op.create_index(op.f('ix_compliance_findings_inspection_id'), 'compliance_findings', ['inspection_id'], unique=False)
    op.create_index(op.f('ix_compliance_findings_evidence_id'), 'compliance_findings', ['evidence_id'], unique=False)
    op.create_index(op.f('ix_compliance_findings_requirement_name'), 'compliance_findings', ['requirement_name'], unique=False)
    op.create_index(op.f('ix_compliance_findings_result'), 'compliance_findings', ['result'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_compliance_findings_result'), table_name='compliance_findings')
    op.drop_index(op.f('ix_compliance_findings_requirement_name'), table_name='compliance_findings')
    op.drop_index(op.f('ix_compliance_findings_evidence_id'), table_name='compliance_findings')
    op.drop_index(op.f('ix_compliance_findings_inspection_id'), table_name='compliance_findings')
    op.drop_table('compliance_findings')

    op.drop_index(op.f('ix_applicability_results_requirement_name'), table_name='applicability_results')
    op.drop_index(op.f('ix_applicability_results_inspection_id'), table_name='applicability_results')
    op.drop_table('applicability_results')
