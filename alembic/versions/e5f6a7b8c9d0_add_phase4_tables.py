"""add phase4 tables

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-09-19 16:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Declaration Corrections
    op.create_table(
        'declaration_corrections',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('inspection_id', sa.String(length=36), nullable=False),
        sa.Column('evidence_id', sa.String(length=36), nullable=True),
        sa.Column('requirement_name', sa.String(length=100), nullable=False),
        sa.Column('field_name', sa.String(length=100), nullable=True),
        sa.Column('previous_value', sa.JSON(), nullable=True),
        sa.Column('corrected_value', sa.JSON(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('inspector_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['evidence_id'], ['evidence_assets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['inspection_id'], ['inspections.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['inspector_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_declaration_corrections_inspection_id'), 'declaration_corrections', ['inspection_id'], unique=False)
    op.create_index(op.f('ix_declaration_corrections_evidence_id'), 'declaration_corrections', ['evidence_id'], unique=False)
    op.create_index(op.f('ix_declaration_corrections_requirement_name'), 'declaration_corrections', ['requirement_name'], unique=False)

    # 2. Manual Observations
    op.create_table(
        'manual_observations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('inspection_id', sa.String(length=36), nullable=False),
        sa.Column('requirement_name', sa.String(length=100), nullable=False),
        sa.Column('observation_text', sa.Text(), nullable=False),
        sa.Column('inspector_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['inspection_id'], ['inspections.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['inspector_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_manual_observations_inspection_id'), 'manual_observations', ['inspection_id'], unique=False)
    op.create_index(op.f('ix_manual_observations_requirement_name'), 'manual_observations', ['requirement_name'], unique=False)

    # 3. Reviewer Decisions
    op.create_table(
        'reviewer_decisions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('inspection_id', sa.String(length=36), nullable=False),
        sa.Column('finding_id', sa.String(length=36), nullable=True),
        sa.Column('requirement_name', sa.String(length=100), nullable=False),
        sa.Column('reviewer_id', sa.String(length=36), nullable=False),
        sa.Column('determination', sa.String(length=50), nullable=False),
        sa.Column('original_result', sa.String(length=50), nullable=True),
        sa.Column('adjudicated_result', sa.String(length=50), nullable=False),
        sa.Column('is_override', sa.Boolean(), nullable=False),
        sa.Column('rationale', sa.Text(), nullable=False),
        sa.Column('rule_set_id', sa.String(length=100), nullable=False, server_default='LMPC-2011-MVP-RULES'),
        sa.Column('rule_set_version', sa.String(length=50), nullable=False, server_default='v1.0'),
        sa.Column('evaluation_version', sa.String(length=50), nullable=False, server_default='v1.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['finding_id'], ['compliance_findings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['inspection_id'], ['inspections.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('inspection_id', 'requirement_name', name='uq_reviewer_decision_inspection_req')
    )
    op.create_index(op.f('ix_reviewer_decisions_inspection_id'), 'reviewer_decisions', ['inspection_id'], unique=False)
    op.create_index(op.f('ix_reviewer_decisions_finding_id'), 'reviewer_decisions', ['finding_id'], unique=False)
    op.create_index(op.f('ix_reviewer_decisions_requirement_name'), 'reviewer_decisions', ['requirement_name'], unique=False)
    op.create_index(op.f('ix_reviewer_decisions_reviewer_id'), 'reviewer_decisions', ['reviewer_id'], unique=False)

    # 4. Evidence Requests
    op.create_table(
        'evidence_requests',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('inspection_id', sa.String(length=36), nullable=False),
        sa.Column('reviewer_id', sa.String(length=36), nullable=False),
        sa.Column('requirement_name', sa.String(length=100), nullable=False),
        sa.Column('request_reason', sa.Text(), nullable=False),
        sa.Column('requested_condition', sa.Text(), nullable=False),
        sa.Column('requested_evidence_type', sa.String(length=50), nullable=False, server_default='SUPPLEMENTAL'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='OPEN'),
        sa.Column('response_evidence_id', sa.String(length=36), nullable=True),
        sa.Column('response_note', sa.Text(), nullable=True),
        sa.Column('resolved_by_id', sa.String(length=36), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['inspection_id'], ['inspections.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id']),
        sa.ForeignKeyConstraint(['resolved_by_id'], ['users.id']),
        sa.ForeignKeyConstraint(['response_evidence_id'], ['evidence_assets.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_evidence_requests_inspection_id'), 'evidence_requests', ['inspection_id'], unique=False)
    op.create_index(op.f('ix_evidence_requests_reviewer_id'), 'evidence_requests', ['reviewer_id'], unique=False)
    op.create_index(op.f('ix_evidence_requests_requirement_name'), 'evidence_requests', ['requirement_name'], unique=False)
    op.create_index(op.f('ix_evidence_requests_status'), 'evidence_requests', ['status'], unique=False)

    # 5. Final Audit Records
    op.create_table(
        'final_audit_records',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('inspection_id', sa.String(length=36), nullable=False),
        sa.Column('finalized_by_id', sa.String(length=36), nullable=False),
        sa.Column('finalized_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('final_decision', sa.String(length=50), nullable=False),
        sa.Column('final_rationale', sa.Text(), nullable=False),
        sa.Column('inspection_context_snapshot', sa.JSON(), nullable=False),
        sa.Column('evidence_snapshot', sa.JSON(), nullable=False),
        sa.Column('declaration_snapshot', sa.JSON(), nullable=False),
        sa.Column('applicability_snapshot', sa.JSON(), nullable=False),
        sa.Column('compliance_findings_snapshot', sa.JSON(), nullable=False),
        sa.Column('reviewer_decisions_snapshot', sa.JSON(), nullable=False),
        sa.Column('rule_set_id', sa.String(length=100), nullable=False, server_default='LMPC-2011-MVP-RULES'),
        sa.Column('rule_set_version', sa.String(length=50), nullable=False, server_default='v1.0'),
        sa.Column('evaluation_version', sa.String(length=50), nullable=False, server_default='v1.0'),
        sa.Column('source_evidence_hashes', sa.JSON(), nullable=False),
        sa.Column('audit_metadata', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['finalized_by_id'], ['users.id']),
        sa.ForeignKeyConstraint(['inspection_id'], ['inspections.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('inspection_id', name='uq_final_audit_inspection_id')
    )
    op.create_index(op.f('ix_final_audit_records_inspection_id'), 'final_audit_records', ['inspection_id'], unique=True)
    op.create_index(op.f('ix_final_audit_records_final_decision'), 'final_audit_records', ['final_decision'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_final_audit_records_final_decision'), table_name='final_audit_records')
    op.drop_index(op.f('ix_final_audit_records_inspection_id'), table_name='final_audit_records')
    op.drop_table('final_audit_records')

    op.drop_index(op.f('ix_evidence_requests_status'), table_name='evidence_requests')
    op.drop_index(op.f('ix_evidence_requests_requirement_name'), table_name='evidence_requests')
    op.drop_index(op.f('ix_evidence_requests_reviewer_id'), table_name='evidence_requests')
    op.drop_index(op.f('ix_evidence_requests_inspection_id'), table_name='evidence_requests')
    op.drop_table('evidence_requests')

    op.drop_index(op.f('ix_reviewer_decisions_reviewer_id'), table_name='reviewer_decisions')
    op.drop_index(op.f('ix_reviewer_decisions_requirement_name'), table_name='reviewer_decisions')
    op.drop_index(op.f('ix_reviewer_decisions_finding_id'), table_name='reviewer_decisions')
    op.drop_index(op.f('ix_reviewer_decisions_inspection_id'), table_name='reviewer_decisions')
    op.drop_table('reviewer_decisions')

    op.drop_index(op.f('ix_manual_observations_requirement_name'), table_name='manual_observations')
    op.drop_index(op.f('ix_manual_observations_inspection_id'), table_name='manual_observations')
    op.drop_table('manual_observations')

    op.drop_index(op.f('ix_declaration_corrections_requirement_name'), table_name='declaration_corrections')
    op.drop_index(op.f('ix_declaration_corrections_evidence_id'), table_name='declaration_corrections')
    op.drop_index(op.f('ix_declaration_corrections_inspection_id'), table_name='declaration_corrections')
    op.drop_table('declaration_corrections')
