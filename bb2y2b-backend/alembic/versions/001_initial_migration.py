"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create spaces table
    op.create_table('spaces',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('space_id', sa.String(length=50), nullable=False),
        sa.Column('space_name', sa.String(length=200), nullable=False),
        sa.Column('video_keyword', sa.Text(), nullable=True),
        sa.Column('video_type', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_scan_time', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_spaces_id'), 'spaces', ['id'], unique=False)
    op.create_index(op.f('ix_spaces_space_id'), 'spaces', ['space_id'], unique=True)

    # Create videos table
    op.create_table('videos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('video_id', sa.String(length=50), nullable=False),
        sa.Column('video_title', sa.Text(), nullable=False),
        sa.Column('video_url', sa.Text(), nullable=False),
        sa.Column('video_type', sa.String(length=50), nullable=False),
        sa.Column('space_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('start_p', sa.Integer(), nullable=True),
        sa.Column('end_p', sa.Integer(), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('file_size', sa.BigInteger(), nullable=True),
        sa.Column('download_path', sa.Text(), nullable=True),
        sa.Column('cover_path', sa.Text(), nullable=True),
        sa.Column('youtube_id', sa.String(length=50), nullable=True),
        sa.Column('upload_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['space_id'], ['spaces.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_videos_id'), 'videos', ['id'], unique=False)
    op.create_index(op.f('ix_videos_video_id'), 'videos', ['video_id'], unique=True)

    # Create tasks table
    op.create_table('tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.String(length=100), nullable=False),
        sa.Column('task_type', sa.String(length=50), nullable=False),
        sa.Column('video_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('progress', sa.Float(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_id'), 'tasks', ['id'], unique=False)
    op.create_index(op.f('ix_tasks_task_id'), 'tasks', ['task_id'], unique=True)

    # Create ai_providers table
    op.create_table('ai_providers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider_id', sa.String(length=50), nullable=False),
        sa.Column('provider_name', sa.String(length=100), nullable=False),
        sa.Column('provider_type', sa.String(length=50), nullable=False),
        sa.Column('api_key_encrypted', sa.Text(), nullable=False),
        sa.Column('api_endpoint', sa.Text(), nullable=True),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('max_tokens', sa.Integer(), nullable=True),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('usage_quota', sa.Integer(), nullable=True),
        sa.Column('current_usage', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_providers_id'), 'ai_providers', ['id'], unique=False)
    op.create_index(op.f('ix_ai_providers_provider_id'), 'ai_providers', ['provider_id'], unique=True)

    # Create prompt_templates table
    op.create_table('prompt_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('prompt_id', sa.String(length=50), nullable=False),
        sa.Column('template_name', sa.String(length=200), nullable=False),
        sa.Column('template_content', sa.Text(), nullable=False),
        sa.Column('variables', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('use_case', sa.String(length=100), nullable=False),
        sa.Column('provider_type', sa.String(length=50), nullable=True),
        sa.Column('version', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prompt_templates_id'), 'prompt_templates', ['id'], unique=False)
    op.create_index(op.f('ix_prompt_templates_prompt_id'), 'prompt_templates', ['prompt_id'], unique=True)

    # Create ai_analysis_logs table
    op.create_table('ai_analysis_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('video_id', sa.Integer(), nullable=True),
        sa.Column('provider_id', sa.Integer(), nullable=True),
        sa.Column('prompt_id', sa.Integer(), nullable=True),
        sa.Column('input_content', sa.Text(), nullable=False),
        sa.Column('output_content', sa.Text(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('analysis_type', sa.String(length=50), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('processing_time', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['provider_id'], ['ai_providers.id'], ),
        sa.ForeignKeyConstraint(['prompt_id'], ['prompt_templates.id'], ),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_analysis_logs_id'), 'ai_analysis_logs', ['id'], unique=False)

    # Create system_configs table
    op.create_table('system_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('config_key', sa.String(length=100), nullable=False),
        sa.Column('config_value', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_system_configs_id'), 'system_configs', ['id'], unique=False)
    op.create_index(op.f('ix_system_configs_config_key'), 'system_configs', ['config_key'], unique=True)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('system_configs')
    op.drop_table('ai_analysis_logs')
    op.drop_table('prompt_templates')
    op.drop_table('ai_providers')
    op.drop_table('tasks')
    op.drop_table('videos')
    op.drop_table('spaces')