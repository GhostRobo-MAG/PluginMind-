"""Initial PluginMind Schema - Foundation Tables

Revision ID: 001
Revises: 
Create Date: 2025-08-20

Creates the foundational database schema for PluginMind AI processing platform.
Includes tables for analysis jobs, users, query logs, and generic AI result storage.
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema - Create PluginMind foundation tables."""
    
    # Create analysis_jobs table
    op.create_table(
        'analysis_jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('user_input', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('status', sa.Enum('QUEUED', 'PROCESSING', 'COMPLETED', 'FAILED', name='jobstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('optimized_prompt', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('analysis', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('error', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('cost', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analysis_jobs_job_id'), 'analysis_jobs', ['job_id'], unique=True)
    op.create_index(op.f('ix_analysis_jobs_user_id'), 'analysis_jobs', ['user_id'], unique=False)

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('subscription_tier', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('queries_used', sa.Integer(), nullable=False),
        sa.Column('queries_limit', sa.Integer(), nullable=False),
        sa.Column('google_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_google_id'), 'users', ['google_id'], unique=True)

    # Create query_logs table
    op.create_table(
        'query_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('user_input', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('optimized_prompt', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('ai_result', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('error_message', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('openai_cost', sa.Float(), nullable=True),
        sa.Column('grok_cost', sa.Float(), nullable=True),
        sa.Column('total_cost', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_query_logs_user_id'), 'query_logs', ['user_id'], unique=False)

    # Create analysis_results table for generic AI processing results
    op.create_table(
        'analysis_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('result_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('analysis_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('input_data', sa.JSON(), nullable=False),
        sa.Column('result_data', sa.JSON(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('ai_service_used', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('cost', sa.Float(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', name='analysisresultstatus'), nullable=False),
        sa.Column('error_details', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analysis_results_result_id'), 'analysis_results', ['result_id'], unique=True)
    op.create_index(op.f('ix_analysis_results_user_id'), 'analysis_results', ['user_id'], unique=False)
    op.create_index(op.f('ix_analysis_results_analysis_type'), 'analysis_results', ['analysis_type'], unique=False)
    op.create_index(op.f('ix_analysis_results_created_at'), 'analysis_results', ['created_at'], unique=False)


def downgrade() -> None:
    """Downgrade database schema - Remove PluginMind foundation tables."""
    
    # Drop tables in reverse order
    op.drop_index(op.f('ix_analysis_results_created_at'), table_name='analysis_results')
    op.drop_index(op.f('ix_analysis_results_analysis_type'), table_name='analysis_results')
    op.drop_index(op.f('ix_analysis_results_user_id'), table_name='analysis_results')
    op.drop_index(op.f('ix_analysis_results_result_id'), table_name='analysis_results')
    op.drop_table('analysis_results')
    
    op.drop_index(op.f('ix_query_logs_user_id'), table_name='query_logs')
    op.drop_table('query_logs')
    
    op.drop_index(op.f('ix_users_google_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    
    op.drop_index(op.f('ix_analysis_jobs_user_id'), table_name='analysis_jobs')
    op.drop_index(op.f('ix_analysis_jobs_job_id'), table_name='analysis_jobs')
    op.drop_table('analysis_jobs')
    
    # Drop custom enums
    sa.Enum(name='analysisresultstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='jobstatus').drop(op.get_bind(), checkfirst=True)