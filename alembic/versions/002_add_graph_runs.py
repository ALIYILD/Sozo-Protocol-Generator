"""Add graph_runs table for LangGraph pipeline persistence.

Revision ID: 002
Revises: 001
Create Date: 2026-04-03
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'graph_runs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('thread_id', sa.String(256), nullable=False),
        sa.Column('status', sa.String(64), nullable=False, server_default='pending'),
        sa.Column('condition_slug', sa.String(128), nullable=False),
        sa.Column('condition_name', sa.String(256), nullable=True),
        sa.Column('source_mode', sa.String(32), nullable=False, server_default='prompt'),
        sa.Column('user_prompt', sa.Text(), nullable=True),
        sa.Column('evidence_article_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('evidence_sufficient', sa.Boolean(), nullable=True),
        sa.Column('evidence_grade_distribution', sa.JSON(), nullable=True),
        sa.Column('safety_cleared', sa.Boolean(), nullable=True),
        sa.Column('blocking_contraindications', sa.JSON(), nullable=True),
        sa.Column('sections_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('grounding_score', sa.Float(), nullable=True),
        sa.Column('composed_sections', sa.JSON(), nullable=True),
        sa.Column('reviewer_id', sa.String(256), nullable=True),
        sa.Column('review_decision', sa.String(32), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('revision_number', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('output_paths', sa.JSON(), nullable=True),
        sa.Column('audit_record_id', sa.String(256), nullable=True),
        sa.Column('final_state', sa.JSON(), nullable=True),
        sa.Column('node_history', sa.JSON(), nullable=True),
        sa.Column('errors', sa.JSON(), nullable=True),
        sa.Column('graph_version', sa.String(64), nullable=True),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
    )
    op.create_index('ix_graph_runs_thread_id', 'graph_runs', ['thread_id'], unique=True)
    op.create_index('ix_graph_runs_status', 'graph_runs', ['status'])
    op.create_index('ix_graph_runs_condition', 'graph_runs', ['condition_slug'])
    op.create_index('ix_graph_runs_reviewer', 'graph_runs', ['reviewer_id'])


def downgrade() -> None:
    op.drop_index('ix_graph_runs_reviewer', table_name='graph_runs')
    op.drop_index('ix_graph_runs_condition', table_name='graph_runs')
    op.drop_index('ix_graph_runs_status', table_name='graph_runs')
    op.drop_index('ix_graph_runs_thread_id', table_name='graph_runs')
    op.drop_table('graph_runs')
