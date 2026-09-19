"""add image quality and analysis jobs

Revision ID: a1b2c3d4e5f6
Revises: 8f4e21a69b12
Create Date: 2026-09-19 01:20:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '8f4e21a69b12'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create analysis_jobs table
    op.create_table(
        'analysis_jobs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('inspection_id', sa.String(length=36), nullable=False),
        sa.Column('evidence_id', sa.String(length=36), nullable=True),
        sa.Column('job_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('worker_id', sa.String(length=100), nullable=True),
        sa.Column('lease_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_attempts', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['inspection_id'], ['inspections.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['evidence_id'], ['evidence_assets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analysis_jobs_inspection_id'), 'analysis_jobs', ['inspection_id'], unique=False)
    op.create_index(op.f('ix_analysis_jobs_evidence_id'), 'analysis_jobs', ['evidence_id'], unique=False)
    op.create_index(op.f('ix_analysis_jobs_job_type'), 'analysis_jobs', ['job_type'], unique=False)
    op.create_index(op.f('ix_analysis_jobs_status'), 'analysis_jobs', ['status'], unique=False)

    # 2. Create image_quality_assessments table
    op.create_table(
        'image_quality_assessments',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('evidence_id', sa.String(length=36), nullable=False),
        sa.Column('inspection_id', sa.String(length=36), nullable=False),
        sa.Column('quality_status', sa.String(length=50), nullable=False),
        sa.Column('assessment_version', sa.String(length=50), nullable=False),
        sa.Column('width', sa.Integer(), nullable=False),
        sa.Column('height', sa.Integer(), nullable=False),
        sa.Column('total_pixels', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('is_decoded', sa.Boolean(), nullable=False),
        sa.Column('sharpness_score', sa.Float(), nullable=True),
        sa.Column('brightness_score', sa.Float(), nullable=True),
        sa.Column('contrast_score', sa.Float(), nullable=True),
        sa.Column('reason_codes', sa.JSON(), nullable=False),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['evidence_id'], ['evidence_assets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['inspection_id'], ['inspections.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_image_quality_assessments_evidence_id'), 'image_quality_assessments', ['evidence_id'], unique=True)
    op.create_index(op.f('ix_image_quality_assessments_inspection_id'), 'image_quality_assessments', ['inspection_id'], unique=False)
    op.create_index(op.f('ix_image_quality_assessments_quality_status'), 'image_quality_assessments', ['quality_status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_image_quality_assessments_quality_status'), table_name='image_quality_assessments')
    op.drop_index(op.f('ix_image_quality_assessments_inspection_id'), table_name='image_quality_assessments')
    op.drop_index(op.f('ix_image_quality_assessments_evidence_id'), table_name='image_quality_assessments')
    op.drop_table('image_quality_assessments')

    op.drop_index(op.f('ix_analysis_jobs_status'), table_name='analysis_jobs')
    op.drop_index(op.f('ix_analysis_jobs_job_type'), table_name='analysis_jobs')
    op.drop_index(op.f('ix_analysis_jobs_evidence_id'), table_name='analysis_jobs')
    op.drop_index(op.f('ix_analysis_jobs_inspection_id'), table_name='analysis_jobs')
    op.drop_table('analysis_jobs')
