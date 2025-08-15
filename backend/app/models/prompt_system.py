from typing import Dict, List, Optional, Any
"""
Modelos para o Sistema de Preenchimento de Lacunas em Prompts
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Nicho(Base):
    """Modelo para nichos de conteúdo"""
    __tablename__ = 'nichos'
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), unique=True, nullable=False, index=True)
    descricao = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    categorias = relationship("Categoria", back_populates="nicho", cascade="all, delete-orphan")
    dados_coletados = relationship("DadosColetados", back_populates="nicho")


class Categoria(Base):
    """Modelo para categorias dentro de nichos"""
    __tablename__ = 'categorias'
    
    id = Column(Integer, primary_key=True, index=True)
    nicho_id = Column(Integer, ForeignKey('nichos.id'), nullable=False, index=True)
    nome = Column(String(100), nullable=False, index=True)
    descricao = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    nicho = relationship("Nicho", back_populates="categorias")
    prompt_base = relationship("PromptBase", back_populates="categoria", uselist=False)
    dados_coletados = relationship("DadosColetados", back_populates="categoria")


class PromptBase(Base):
    """Modelo para prompts base (arquivos TXT)"""
    __tablename__ = 'prompts_base'
    
    id = Column(Integer, primary_key=True, index=True)
    categoria_id = Column(Integer, ForeignKey('categorias.id'), unique=True, nullable=False, index=True)
    nome_arquivo = Column(String(255), nullable=False)
    conteudo = Column(Text, nullable=False)
    hash_conteudo = Column(String(64), nullable=False, index=True)  # Para cache e versionamento
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    categoria = relationship("Categoria", back_populates="prompt_base")
    prompts_preenchidos = relationship("PromptPreenchido", back_populates="prompt_base")


class DadosColetados(Base):
    """Modelo para dados coletados (keywords e clusters)"""
    __tablename__ = 'dados_coletados'
    
    id = Column(Integer, primary_key=True, index=True)
    nicho_id = Column(Integer, ForeignKey('nichos.id'), nullable=False, index=True)
    categoria_id = Column(Integer, ForeignKey('categorias.id'), nullable=False, index=True)
    primary_keyword = Column(String(255), nullable=False)
    secondary_keywords = Column(Text, nullable=True)  # Lista separada por vírgula
    cluster_content = Column(Text, nullable=False)
    status = Column(String(50), default='ativo', index=True)  # ativo, inativo, processando
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    nicho = relationship("Nicho", back_populates="dados_coletados")
    categoria = relationship("Categoria", back_populates="dados_coletados")
    prompts_preenchidos = relationship("PromptPreenchido", back_populates="dados_coletados")


class PromptPreenchido(Base):
    """Modelo para prompts preenchidos"""
    __tablename__ = 'prompts_preenchidos'
    
    id = Column(Integer, primary_key=True, index=True)
    dados_coletados_id = Column(Integer, ForeignKey('dados_coletados.id'), nullable=False, index=True)
    prompt_base_id = Column(Integer, ForeignKey('prompts_base.id'), nullable=False, index=True)
    prompt_original = Column(Text, nullable=False)
    prompt_preenchido = Column(Text, nullable=False)
    lacunas_detectadas = Column(Text, nullable=True)  # JSON com lacunas encontradas
    lacunas_preenchidas = Column(Text, nullable=True)  # JSON com lacunas preenchidas
    status = Column(String(50), default='pronto', index=True)  # pronto, processando, erro
    tempo_processamento = Column(Integer, nullable=True)  # em milissegundos
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    dados_coletados = relationship("DadosColetados", back_populates="prompts_preenchidos")
    prompt_base = relationship("PromptBase", back_populates="prompts_preenchidos")


class LogOperacao(Base):
    """Modelo para logs de operações"""
    __tablename__ = 'logs_operacao'
    
    id = Column(Integer, primary_key=True, index=True)
    tipo_operacao = Column(String(50), nullable=False, index=True)  # create, update, delete, process
    entidade = Column(String(50), nullable=False, index=True)  # nicho, categoria, prompt, dados
    entidade_id = Column(Integer, nullable=True)
    detalhes = Column(Text, nullable=True)  # JSON com detalhes da operação
    status = Column(String(50), default='sucesso', index=True)  # sucesso, erro, aviso
    tempo_execucao = Column(Integer, nullable=True)  # em milissegundos
    created_at = Column(DateTime, default=datetime.utcnow, index=True) 