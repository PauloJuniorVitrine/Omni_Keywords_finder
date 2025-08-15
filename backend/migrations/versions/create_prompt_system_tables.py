from typing import Dict, List, Optional, Any
"""
Migration: Create Prompt System Tables
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'prompt_system_v1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create prompt system tables"""
    
    # Create nichos table
    op.create_table(
        'nichos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_nichos_id'), 'nichos', ['id'], unique=False)
    op.create_index(op.f('ix_nichos_nome'), 'nichos', ['nome'], unique=True)
    
    # Create categorias table
    op.create_table(
        'categorias',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nicho_id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['nicho_id'], ['nichos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_categorias_id'), 'categorias', ['id'], unique=False)
    op.create_index(op.f('ix_categorias_nicho_id'), 'categorias', ['nicho_id'], unique=False)
    op.create_index(op.f('ix_categorias_nome'), 'categorias', ['nome'], unique=False)
    
    # Create prompts_base table
    op.create_table(
        'prompts_base',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('categoria_id', sa.Integer(), nullable=False),
        sa.Column('nome_arquivo', sa.String(length=255), nullable=False),
        sa.Column('conteudo', sa.Text(), nullable=False),
        sa.Column('hash_conteudo', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['categoria_id'], ['categorias.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prompts_base_id'), 'prompts_base', ['id'], unique=False)
    op.create_index(op.f('ix_prompts_base_categoria_id'), 'prompts_base', ['categoria_id'], unique=True)
    op.create_index(op.f('ix_prompts_base_hash_conteudo'), 'prompts_base', ['hash_conteudo'], unique=False)
    
    # Create dados_coletados table
    op.create_table(
        'dados_coletados',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nicho_id', sa.Integer(), nullable=False),
        sa.Column('categoria_id', sa.Integer(), nullable=False),
        sa.Column('primary_keyword', sa.String(length=255), nullable=False),
        sa.Column('secondary_keywords', sa.Text(), nullable=True),
        sa.Column('cluster_content', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['categoria_id'], ['categorias.id'], ),
        sa.ForeignKeyConstraint(['nicho_id'], ['nichos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dados_coletados_id'), 'dados_coletados', ['id'], unique=False)
    op.create_index(op.f('ix_dados_coletados_nicho_id'), 'dados_coletados', ['nicho_id'], unique=False)
    op.create_index(op.f('ix_dados_coletados_categoria_id'), 'dados_coletados', ['categoria_id'], unique=False)
    op.create_index(op.f('ix_dados_coletados_status'), 'dados_coletados', ['status'], unique=False)
    
    # Create prompts_preenchidos table
    op.create_table(
        'prompts_preenchidos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dados_coletados_id', sa.Integer(), nullable=False),
        sa.Column('prompt_base_id', sa.Integer(), nullable=False),
        sa.Column('prompt_original', sa.Text(), nullable=False),
        sa.Column('prompt_preenchido', sa.Text(), nullable=False),
        sa.Column('lacunas_detectadas', sa.Text(), nullable=True),
        sa.Column('lacunas_preenchidas', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('tempo_processamento', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['dados_coletados_id'], ['dados_coletados.id'], ),
        sa.ForeignKeyConstraint(['prompt_base_id'], ['prompts_base.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prompts_preenchidos_id'), 'prompts_preenchidos', ['id'], unique=False)
    op.create_index(op.f('ix_prompts_preenchidos_dados_coletados_id'), 'prompts_preenchidos', ['dados_coletados_id'], unique=False)
    op.create_index(op.f('ix_prompts_preenchidos_prompt_base_id'), 'prompts_preenchidos', ['prompt_base_id'], unique=False)
    op.create_index(op.f('ix_prompts_preenchidos_status'), 'prompts_preenchidos', ['status'], unique=False)
    
    # Create logs_operacao table
    op.create_table(
        'logs_operacao',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tipo_operacao', sa.String(length=50), nullable=False),
        sa.Column('entidade', sa.String(length=50), nullable=False),
        sa.Column('entidade_id', sa.Integer(), nullable=True),
        sa.Column('detalhes', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('tempo_execucao', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_logs_operacao_id'), 'logs_operacao', ['id'], unique=False)
    op.create_index(op.f('ix_logs_operacao_tipo_operacao'), 'logs_operacao', ['tipo_operacao'], unique=False)
    op.create_index(op.f('ix_logs_operacao_entidade'), 'logs_operacao', ['entidade'], unique=False)
    op.create_index(op.f('ix_logs_operacao_status'), 'logs_operacao', ['status'], unique=False)
    op.create_index(op.f('ix_logs_operacao_created_at'), 'logs_operacao', ['created_at'], unique=False)


def downgrade():
    """Drop prompt system tables"""
    op.drop_index(op.f('ix_logs_operacao_created_at'), table_name='logs_operacao')
    op.drop_index(op.f('ix_logs_operacao_status'), table_name='logs_operacao')
    op.drop_index(op.f('ix_logs_operacao_entidade'), table_name='logs_operacao')
    op.drop_index(op.f('ix_logs_operacao_tipo_operacao'), table_name='logs_operacao')
    op.drop_index(op.f('ix_logs_operacao_id'), table_name='logs_operacao')
    op.drop_table('logs_operacao')
    
    op.drop_index(op.f('ix_prompts_preenchidos_status'), table_name='prompts_preenchidos')
    op.drop_index(op.f('ix_prompts_preenchidos_prompt_base_id'), table_name='prompts_preenchidos')
    op.drop_index(op.f('ix_prompts_preenchidos_dados_coletados_id'), table_name='prompts_preenchidos')
    op.drop_index(op.f('ix_prompts_preenchidos_id'), table_name='prompts_preenchidos')
    op.drop_table('prompts_preenchidos')
    
    op.drop_index(op.f('ix_dados_coletados_status'), table_name='dados_coletados')
    op.drop_index(op.f('ix_dados_coletados_categoria_id'), table_name='dados_coletados')
    op.drop_index(op.f('ix_dados_coletados_nicho_id'), table_name='dados_coletados')
    op.drop_index(op.f('ix_dados_coletados_id'), table_name='dados_coletados')
    op.drop_table('dados_coletados')
    
    op.drop_index(op.f('ix_prompts_base_hash_conteudo'), table_name='prompts_base')
    op.drop_index(op.f('ix_prompts_base_categoria_id'), table_name='prompts_base')
    op.drop_index(op.f('ix_prompts_base_id'), table_name='prompts_base')
    op.drop_table('prompts_base')
    
    op.drop_index(op.f('ix_categorias_nome'), table_name='categorias')
    op.drop_index(op.f('ix_categorias_nicho_id'), table_name='categorias')
    op.drop_index(op.f('ix_categorias_id'), table_name='categorias')
    op.drop_table('categorias')
    
    op.drop_index(op.f('ix_nichos_nome'), table_name='nichos')
    op.drop_index(op.f('ix_nichos_id'), table_name='nichos')
    op.drop_table('nichos') 