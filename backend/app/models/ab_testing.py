from typing import Dict, List, Optional, Any
"""
Modelos de A/B Testing - Omni Keywords Finder

Este módulo define os modelos de dados para o sistema de A/B Testing,
incluindo experimentos, variantes, participantes e resultados.

Autor: Sistema Omni Keywords Finder
Data: 2024-12-19
Versão: 1.0.0
"""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid
import json

Base = declarative_base()

class Experimento(Base):
    """Modelo para experimentos de A/B Testing"""
    __tablename__ = 'experimentos'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String(255), nullable=False, unique=True)
    descricao = Column(Text)
    
    # Configurações do experimento
    tipo = Column(String(50), nullable=False)  # 'feature', 'ui', 'algorithm', 'content'
    area_teste = Column(String(100), nullable=False)  # 'dashboard', 'keywords', 'execucoes', etc.
    
    # Status e controle
    ativo = Column(Boolean, default=True)
    status = Column(String(20), default='draft')  # draft, running, paused, completed
    
    # Configurações de tráfego
    percentual_trafego = Column(Float, default=100.0)  # Percentual de usuários que participam
    duracao_dias = Column(Integer, default=30)
    
    # Critérios de sucesso
    metricas_primarias = Column(JSON)  # Lista de métricas principais
    metricas_secundarias = Column(JSON)  # Lista de métricas secundárias
    hipotese = Column(Text)  # Hipótese do experimento
    
    # Configurações estatísticas
    nivel_significancia = Column(Float, default=0.05)  # 5% por padrão
    poder_estatistico = Column(Float, default=0.8)  # 80% por padrão
    tamanho_amostra_minimo = Column(Integer, default=100)
    
    # Datas
    data_criacao = Column(DateTime, default=func.now())
    data_inicio = Column(DateTime)
    data_fim = Column(DateTime)
    data_termino_planejado = Column(DateTime)
    
    # Criador e responsável
    criado_por = Column(String(100))
    responsavel = Column(String(100))
    
    # Relacionamentos
    variantes = relationship("Variante", back_populates="experimento", cascade="all, delete-orphan")
    participantes = relationship("Participante", back_populates="experimento", cascade="all, delete-orphan")
    eventos = relationship("EventoExperimento", back_populates="experimento", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Experimento(id='{self.id}', nome='{self.nome}', status='{self.status}')>"
    
    @property
    def duracao_atual(self):
        """Retorna a duração atual do experimento em dias"""
        if not self.data_inicio:
            return 0
        fim = self.data_fim or datetime.now()
        return (fim - self.data_inicio).days
    
    @property
    def percentual_conclusao(self):
        """Retorna o percentual de conclusão do experimento"""
        if not self.data_inicio or not self.data_termino_planejado:
            return 0
        total = (self.data_termino_planejado - self.data_inicio).days
        atual = self.duracao_atual
        return min(100, (atual / total) * 100) if total > 0 else 0
    
    @property
    def esta_ativo(self):
        """Verifica se o experimento está ativo e em execução"""
        if not self.ativo or self.status != 'running':
            return False
        if not self.data_inicio:
            return False
        if self.data_fim:
            return False
        if self.data_termino_planejado and datetime.now() > self.data_termino_planejado:
            return False
        return True

class Variante(Base):
    """Modelo para variantes de um experimento"""
    __tablename__ = 'variantes'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    experimento_id = Column(String(36), ForeignKey('experimentos.id'), nullable=False)
    
    # Identificação da variante
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    tipo = Column(String(20), default='test')  # 'control', 'test'
    
    # Configuração da variante
    configuracao = Column(JSON)  # Configurações específicas da variante
    peso = Column(Float, default=50.0)  # Percentual de tráfego para esta variante
    
    # Status
    ativo = Column(Boolean, default=True)
    
    # Datas
    data_criacao = Column(DateTime, default=func.now())
    
    # Relacionamentos
    experimento = relationship("Experimento", back_populates="variantes")
    participantes = relationship("Participante", back_populates="variante")
    
    def __repr__(self):
        return f"<Variante(id='{self.id}', nome='{self.nome}', tipo='{self.tipo}')>"
    
    @property
    def eh_controle(self):
        """Verifica se é a variante de controle"""
        return self.tipo == 'control'

class Participante(Base):
    """Modelo para participantes de experimentos"""
    __tablename__ = 'participantes'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    experimento_id = Column(String(36), ForeignKey('experimentos.id'), nullable=False)
    variante_id = Column(String(36), ForeignKey('variantes.id'), nullable=False)
    
    # Identificação do participante
    usuario_id = Column(String(100), nullable=False)
    sessao_id = Column(String(100))
    dispositivo_id = Column(String(100))
    
    # Informações do participante
    ip_address = Column(String(45))
    user_agent = Column(Text)
    localizacao = Column(String(100))
    
    # Status
    ativo = Column(Boolean, default=True)
    
    # Datas
    data_entrada = Column(DateTime, default=func.now())
    data_saida = Column(DateTime)
    ultima_atividade = Column(DateTime, default=func.now())
    
    # Relacionamentos
    experimento = relationship("Experimento", back_populates="participantes")
    variante = relationship("Variante", back_populates="participantes")
    eventos = relationship("EventoParticipante", back_populates="participante", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Participante(id='{self.id}', usuario_id='{self.usuario_id}', variante_id='{self.variante_id}')>"

class EventoExperimento(Base):
    """Modelo para eventos de experimento (logs)"""
    __tablename__ = 'eventos_experimento'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    experimento_id = Column(String(36), ForeignKey('experimentos.id'), nullable=False)
    
    # Informações do evento
    tipo = Column(String(50), nullable=False)  # 'started', 'paused', 'completed', 'stopped'
    descricao = Column(Text)
    dados = Column(JSON)  # Dados adicionais do evento
    
    # Usuário que executou
    executado_por = Column(String(100))
    
    # Data
    data_evento = Column(DateTime, default=func.now())
    
    # Relacionamentos
    experimento = relationship("Experimento", back_populates="eventos")
    
    def __repr__(self):
        return f"<EventoExperimento(id='{self.id}', tipo='{self.tipo}', experimento_id='{self.experimento_id}')>"

class EventoParticipante(Base):
    """Modelo para eventos de participantes (conversões, métricas)"""
    __tablename__ = 'eventos_participante'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    participante_id = Column(String(36), ForeignKey('participantes.id'), nullable=False)
    
    # Informações do evento
    tipo = Column(String(50), nullable=False)  # 'page_view', 'click', 'conversion', 'metric'
    nome = Column(String(100), nullable=False)
    valor = Column(Float)
    dados = Column(JSON)  # Dados adicionais do evento
    
    # Contexto
    url = Column(String(500))
    elemento = Column(String(100))  # ID do elemento HTML
    contexto = Column(JSON)  # Contexto adicional
    
    # Data
    data_evento = Column(DateTime, default=func.now())
    
    # Relacionamentos
    participante = relationship("Participante", back_populates="eventos")
    
    def __repr__(self):
        return f"<EventoParticipante(id='{self.id}', tipo='{self.tipo}', nome='{self.nome}')>"

class Segmento(Base):
    """Modelo para segmentação de usuários"""
    __tablename__ = 'segmentos'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String(100), nullable=False, unique=True)
    descricao = Column(Text)
    
    # Critérios de segmentação
    criterios = Column(JSON, nullable=False)  # Critérios de segmentação
    
    # Status
    ativo = Column(Boolean, default=True)
    
    # Datas
    data_criacao = Column(DateTime, default=func.now())
    data_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Segmento(id='{self.id}', nome='{self.nome}')>"

class ExperimentoSegmento(Base):
    """Tabela de relacionamento entre experimentos e segmentos"""
    __tablename__ = 'experimento_segmento'
    
    experimento_id = Column(String(36), ForeignKey('experimentos.id'), primary_key=True)
    segmento_id = Column(String(36), ForeignKey('segmentos.id'), primary_key=True)
    
    # Configurações específicas
    peso = Column(Float, default=100.0)  # Peso do segmento no experimento
    
    # Datas
    data_criacao = Column(DateTime, default=func.now())

class ResultadoExperimento(Base):
    """Modelo para resultados calculados de experimentos"""
    __tablename__ = 'resultados_experimento'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    experimento_id = Column(String(36), ForeignKey('experimentos.id'), nullable=False)
    
    # Informações do resultado
    metrica = Column(String(100), nullable=False)
    variante_id = Column(String(36), ForeignKey('variantes.id'), nullable=False)
    
    # Valores estatísticos
    valor_medio = Column(Float)
    desvio_padrao = Column(Float)
    tamanho_amostra = Column(Integer)
    erro_padrao = Column(Float)
    
    # Intervalo de confiança
    ic_inferior = Column(Float)
    ic_superior = Column(Float)
    
    # Teste de significância
    p_valor = Column(Float)
    estatistica_teste = Column(Float)
    significativo = Column(Boolean)
    
    # Comparação com controle
    diferenca_controle = Column(Float)
    percentual_melhoria = Column(Float)
    
    # Datas
    data_calculo = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<ResultadoExperimento(id='{self.id}', metrica='{self.metrica}', variante_id='{self.variante_id}')>"

# Funções utilitárias
def criar_experimento_padrao(nome, descricao, tipo, area_teste, criado_por):
    """Cria um experimento padrão com variantes de controle e teste"""
    experimento = Experimento(
        nome=nome,
        descricao=descricao,
        tipo=tipo,
        area_teste=area_teste,
        criado_por=criado_por,
        responsavel=criado_por,
        data_termino_planejado=datetime.now() + timedelta(days=30)
    )
    
    # Cria variantes padrão
    variante_controle = Variante(
        nome="Controle",
        descricao="Versão atual (controle)",
        tipo="control",
        peso=50.0,
        configuracao={"version": "current"}
    )
    
    variante_teste = Variante(
        nome="Teste",
        descricao="Versão nova (teste)",
        tipo="test",
        peso=50.0,
        configuracao={"version": "new"}
    )
    
    experimento.variantes = [variante_controle, variante_teste]
    
    return experimento

def calcular_tamanho_amostra(alpha=0.05, power=0.8, effect_size=0.1):
    """Calcula o tamanho mínimo da amostra para um experimento"""
    # Implementação simplificada - em produção usar biblioteca estatística
    from scipy import stats
    
    # Calcula tamanho da amostra para teste t de duas amostras
    n = stats.norm.ppf(1 - alpha/2) + stats.norm.ppf(power)
    n = (n / effect_size) ** 2
    
    return int(n * 2)  # Duas variantes

def verificar_significancia(p_valor, alpha=0.05):
    """Verifica se o resultado é estatisticamente significativo"""
    return p_valor < alpha 