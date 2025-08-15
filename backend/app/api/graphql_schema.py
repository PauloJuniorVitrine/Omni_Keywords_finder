"""
GraphQL Schema - Omni Keywords Finder

Este módulo implementa o schema GraphQL completo para o sistema,
incluindo tipos, queries, mutations e subscriptions.

Autor: Sistema Omni Keywords Finder
Data: 2024-12-19
Versão: 1.0.0
"""

import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from flask import g, request
from datetime import datetime, timedelta
from typing import List, Optional
import json

# Importa modelos existentes
from ..models import (
    Nicho, Categoria, Execucao, ExecucaoAgendada, 
    Cliente, Pagamento, Log, Notificacao
)

# Importa serviços existentes
from ...infrastructure.processamento.api_keywords import APIKeywords
from ...infrastructure.coleta.utils.cache_keywords_v1 import CacheKeywords
from ...infrastructure.monitoramento.business_metrics import BusinessMetrics

# =============================================================================
# TIPOS GRAPHQL
# =============================================================================

class NichoType(SQLAlchemyObjectType):
    """Tipo GraphQL para Nicho"""
    class Meta:
        model = Nicho
        interfaces = (graphene.relay.Node,)

class CategoriaType(SQLAlchemyObjectType):
    """Tipo GraphQL para Categoria"""
    class Meta:
        model = Categoria
        interfaces = (graphene.relay.Node,)

class ExecucaoType(SQLAlchemyObjectType):
    """Tipo GraphQL para Execução"""
    class Meta:
        model = Execucao
        interfaces = (graphene.relay.Node,)

class ExecucaoAgendadaType(SQLAlchemyObjectType):
    """Tipo GraphQL para Execução Agendada"""
    class Meta:
        model = ExecucaoAgendada
        interfaces = (graphene.relay.Node,)

class ClienteType(SQLAlchemyObjectType):
    """Tipo GraphQL para Cliente"""
    class Meta:
        model = Cliente
        interfaces = (graphene.relay.Node,)

class PagamentoType(SQLAlchemyObjectType):
    """Tipo GraphQL para Pagamento"""
    class Meta:
        model = Pagamento
        interfaces = (graphene.relay.Node,)

class LogType(SQLAlchemyObjectType):
    """Tipo GraphQL para Log"""
    class Meta:
        model = Log
        interfaces = (graphene.relay.Node,)

class NotificacaoType(SQLAlchemyObjectType):
    """Tipo GraphQL para Notificação"""
    class Meta:
        model = Notificacao
        interfaces = (graphene.relay.Node,)

# =============================================================================
# TIPOS CUSTOMIZADOS
# =============================================================================

class KeywordType(graphene.ObjectType):
    """Tipo GraphQL para Keyword"""
    id = graphene.ID()
    keyword = graphene.String()
    volume = graphene.Int()
    dificuldade = graphene.Float()
    cpc = graphene.Float()
    categoria = graphene.String()
    nicho = graphene.String()
    data_coleta = graphene.DateTime()
    score = graphene.Float()

class ClusterType(graphene.ObjectType):
    """Tipo GraphQL para Cluster"""
    id = graphene.ID()
    nome = graphene.String()
    keywords = graphene.List(KeywordType)
    score_medio = graphene.Float()
    volume_total = graphene.Int()
    data_criacao = graphene.DateTime()

class BusinessMetricType(graphene.ObjectType):
    """Tipo GraphQL para Métrica de Negócio"""
    id = graphene.ID()
    nome = graphene.String()
    valor = graphene.Float()
    tipo = graphene.String()
    periodo = graphene.String()
    data_calculo = graphene.DateTime()
    tendencia = graphene.String()

class PerformanceMetricType(graphene.ObjectType):
    """Tipo GraphQL para Métrica de Performance"""
    id = graphene.ID()
    nome = graphene.String()
    valor = graphene.Float()
    unidade = graphene.String()
    timestamp = graphene.DateTime()
    categoria = graphene.String()

# =============================================================================
# INPUTS PARA MUTATIONS
# =============================================================================

class NichoInput(graphene.InputObjectType):
    """Input para criação/atualização de Nicho"""
    nome = graphene.String(required=True)
    descricao = graphene.String()
    ativo = graphene.Boolean()

class CategoriaInput(graphene.InputObjectType):
    """Input para criação/atualização de Categoria"""
    nome = graphene.String(required=True)
    descricao = graphene.String()
    nicho_id = graphene.ID(required=True)
    ativo = graphene.Boolean()

class ExecucaoInput(graphene.InputObjectType):
    """Input para criação de Execução"""
    nicho_id = graphene.ID(required=True)
    categoria_id = graphene.ID()
    parametros = graphene.String()  # JSON string
    agendada = graphene.Boolean()

class KeywordFilterInput(graphene.InputObjectType):
    """Input para filtros de keywords"""
    nicho_id = graphene.ID()
    categoria_id = graphene.ID()
    volume_min = graphene.Int()
    volume_max = graphene.Int()
    dificuldade_min = graphene.Float()
    dificuldade_max = graphene.Float()
    cpc_min = graphene.Float()
    cpc_max = graphene.Float()
    data_inicio = graphene.DateTime()
    data_fim = graphene.DateTime()
    limit = graphene.Int()
    offset = graphene.Int()

# =============================================================================
# QUERIES
# =============================================================================

class Query(graphene.ObjectType):
    """Queries GraphQL principais"""
    
    # ===== NICHOS =====
    nichos = graphene.List(
        NichoType,
        ativo=graphene.Boolean(),
        descricao=graphene.String()
    )
    
    nicho = graphene.Field(
        NichoType,
        id=graphene.ID(required=True)
    )
    
    # ===== CATEGORIAS =====
    categorias = graphene.List(
        CategoriaType,
        nicho_id=graphene.ID(),
        ativo=graphene.Boolean()
    )
    
    categoria = graphene.Field(
        CategoriaType,
        id=graphene.ID(required=True)
    )
    
    # ===== EXECUÇÕES =====
    execucoes = graphene.List(
        ExecucaoType,
        nicho_id=graphene.ID(),
        status=graphene.String(),
        data_inicio=graphene.DateTime(),
        data_fim=graphene.DateTime(),
        limit=graphene.Int(),
        offset=graphene.Int()
    )
    
    execucao = graphene.Field(
        ExecucaoType,
        id=graphene.ID(required=True)
    )
    
    # ===== EXECUÇÕES AGENDADAS =====
    execucoes_agendadas = graphene.List(
        ExecucaoAgendadaType,
        ativo=graphene.Boolean(),
        proxima_execucao=graphene.DateTime()
    )
    
    # ===== KEYWORDS =====
    keywords = graphene.List(
        KeywordType,
        filtros=KeywordFilterInput()
    )
    
    keyword = graphene.Field(
        KeywordType,
        id=graphene.ID(required=True)
    )
    
    # ===== CLUSTERS =====
    clusters = graphene.List(
        ClusterType,
        nicho_id=graphene.ID(),
        score_min=graphene.Float()
    )
    
    cluster = graphene.Field(
        ClusterType,
        id=graphene.ID(required=True)
    )
    
    # ===== MÉTRICAS DE NEGÓCIO =====
    business_metrics = graphene.List(
        BusinessMetricType,
        tipo=graphene.String(),
        periodo=graphene.String(),
        data_inicio=graphene.DateTime(),
        data_fim=graphene.DateTime()
    )
    
    # ===== MÉTRICAS DE PERFORMANCE =====
    performance_metrics = graphene.List(
        PerformanceMetricType,
        categoria=graphene.String(),
        ultimas_horas=graphene.Int()
    )
    
    # ===== LOGS =====
    logs = graphene.List(
        LogType,
        nivel=graphene.String(),
        modulo=graphene.String(),
        data_inicio=graphene.DateTime(),
        data_fim=graphene.DateTime(),
        limit=graphene.Int()
    )
    
    # ===== NOTIFICAÇÕES =====
    notificacoes = graphene.List(
        NotificacaoType,
        tipo=graphene.String(),
        lida=graphene.Boolean(),
        limit=graphene.Int()
    )
    
    # ===== ESTATÍSTICAS GERAIS =====
    estatisticas_gerais = graphene.Field(
        graphene.JSONString,
        periodo=graphene.String(default_value="30d")
    )

    # ===== RESOLVERS =====
    
    def resolve_nichos(self, info, ativo=None, descricao=None):
        """Resolve lista de nichos"""
        query = Nicho.query
        
        if ativo is not None:
            query = query.filter(Nicho.ativo == ativo)
        
        if descricao:
            query = query.filter(Nicho.descricao.ilike(f"%{descricao}%"))
        
        return query.all()
    
    def resolve_nicho(self, info, id):
        """Resolve nicho específico"""
        return Nicho.query.get(id)
    
    def resolve_categorias(self, info, nicho_id=None, ativo=None):
        """Resolve lista de categorias"""
        query = Categoria.query
        
        if nicho_id:
            query = query.filter(Categoria.nicho_id == nicho_id)
        
        if ativo is not None:
            query = query.filter(Categoria.ativo == ativo)
        
        return query.all()
    
    def resolve_categoria(self, info, id):
        """Resolve categoria específica"""
        return Categoria.query.get(id)
    
    def resolve_execucoes(self, info, nicho_id=None, status=None, 
                         data_inicio=None, data_fim=None, limit=None, offset=None):
        """Resolve lista de execuções"""
        query = Execucao.query
        
        if nicho_id:
            query = query.filter(Execucao.nicho_id == nicho_id)
        
        if status:
            query = query.filter(Execucao.status == status)
        
        if data_inicio:
            query = query.filter(Execucao.data_inicio >= data_inicio)
        
        if data_fim:
            query = query.filter(Execucao.data_fim <= data_fim)
        
        if offset:
            query = query.offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        return query.order_by(Execucao.data_inicio.desc()).all()
    
    def resolve_execucao(self, info, id):
        """Resolve execução específica"""
        return Execucao.query.get(id)
    
    def resolve_execucoes_agendadas(self, info, ativo=None, proxima_execucao=None):
        """Resolve execuções agendadas"""
        query = ExecucaoAgendada.query
        
        if ativo is not None:
            query = query.filter(ExecucaoAgendada.ativo == ativo)
        
        if proxima_execucao:
            query = query.filter(ExecucaoAgendada.proxima_execucao >= proxima_execucao)
        
        return query.order_by(ExecucaoAgendada.proxima_execucao).all()
    
    def resolve_keywords(self, info, filtros=None):
        """Resolve keywords com filtros"""
        try:
            # Usa o serviço de API de keywords
            api_keywords = APIKeywords()
            
            # Converte filtros para formato esperado pelo serviço
            params = {}
            if filtros:
                if filtros.nicho_id:
                    params['nicho_id'] = filtros.nicho_id
                if filtros.categoria_id:
                    params['categoria_id'] = filtros.categoria_id
                if filtros.volume_min:
                    params['volume_min'] = filtros.volume_min
                if filtros.volume_max:
                    params['volume_max'] = filtros.volume_max
                if filtros.dificuldade_min:
                    params['dificuldade_min'] = filtros.dificuldade_min
                if filtros.dificuldade_max:
                    params['dificuldade_max'] = filtros.dificuldade_max
                if filtros.cpc_min:
                    params['cpc_min'] = filtros.cpc_min
                if filtros.cpc_max:
                    params['cpc_max'] = filtros.cpc_max
                if filtros.data_inicio:
                    params['data_inicio'] = filtros.data_inicio.isoformat()
                if filtros.data_fim:
                    params['data_fim'] = filtros.data_fim.isoformat()
                if filtros.limit:
                    params['limit'] = filtros.limit
                if filtros.offset:
                    params['offset'] = filtros.offset
            
            # Busca keywords
            keywords_data = api_keywords.buscar_keywords(**params)
            
            # Converte para tipos GraphQL
            keywords = []
            for kw in keywords_data:
                keywords.append(KeywordType(
                    id=kw.get('id'),
                    keyword=kw.get('keyword'),
                    volume=kw.get('volume'),
                    dificuldade=kw.get('dificuldade'),
                    cpc=kw.get('cpc'),
                    categoria=kw.get('categoria'),
                    nicho=kw.get('nicho'),
                    data_coleta=datetime.fromisoformat(kw.get('data_coleta')) if kw.get('data_coleta') else None,
                    score=kw.get('score')
                ))
            
            return keywords
            
        except Exception as e:
            # Log do erro
            print(f"Erro ao buscar keywords: {e}")
            return []
    
    def resolve_keyword(self, info, id):
        """Resolve keyword específica"""
        try:
            api_keywords = APIKeywords()
            keyword_data = api_keywords.buscar_keyword_por_id(id)
            
            if keyword_data:
                return KeywordType(
                    id=keyword_data.get('id'),
                    keyword=keyword_data.get('keyword'),
                    volume=keyword_data.get('volume'),
                    dificuldade=keyword_data.get('dificuldade'),
                    cpc=keyword_data.get('cpc'),
                    categoria=keyword_data.get('categoria'),
                    nicho=keyword_data.get('nicho'),
                    data_coleta=datetime.fromisoformat(keyword_data.get('data_coleta')) if keyword_data.get('data_coleta') else None,
                    score=keyword_data.get('score')
                )
            
            return None
            
        except Exception as e:
            print(f"Erro ao buscar keyword {id}: {e}")
            return None
    
    def resolve_clusters(self, info, nicho_id=None, score_min=None):
        """Resolve clusters"""
        try:
            # Usa o serviço de clusterização
            from ...infrastructure.processamento.clusterizador_semantico import ClusterizadorSemantico
            
            clusterizador = ClusterizadorSemantico()
            clusters_data = clusterizador.listar_clusters(nicho_id=nicho_id, score_min=score_min)
            
            clusters = []
            for cluster in clusters_data:
                keywords = []
                for kw in cluster.get('keywords', []):
                    keywords.append(KeywordType(
                        id=kw.get('id'),
                        keyword=kw.get('keyword'),
                        volume=kw.get('volume'),
                        dificuldade=kw.get('dificuldade'),
                        cpc=kw.get('cpc'),
                        categoria=kw.get('categoria'),
                        nicho=kw.get('nicho'),
                        data_coleta=datetime.fromisoformat(kw.get('data_coleta')) if kw.get('data_coleta') else None,
                        score=kw.get('score')
                    ))
                
                clusters.append(ClusterType(
                    id=cluster.get('id'),
                    nome=cluster.get('nome'),
                    keywords=keywords,
                    score_medio=cluster.get('score_medio'),
                    volume_total=cluster.get('volume_total'),
                    data_criacao=datetime.fromisoformat(cluster.get('data_criacao')) if cluster.get('data_criacao') else None
                ))
            
            return clusters
            
        except Exception as e:
            print(f"Erro ao buscar clusters: {e}")
            return []
    
    def resolve_cluster(self, info, id):
        """Resolve cluster específico"""
        try:
            from ...infrastructure.processamento.clusterizador_semantico import ClusterizadorSemantico
            
            clusterizador = ClusterizadorSemantico()
            cluster_data = clusterizador.buscar_cluster_por_id(id)
            
            if cluster_data:
                keywords = []
                for kw in cluster_data.get('keywords', []):
                    keywords.append(KeywordType(
                        id=kw.get('id'),
                        keyword=kw.get('keyword'),
                        volume=kw.get('volume'),
                        dificuldade=kw.get('dificuldade'),
                        cpc=kw.get('cpc'),
                        categoria=kw.get('categoria'),
                        nicho=kw.get('nicho'),
                        data_coleta=datetime.fromisoformat(kw.get('data_coleta')) if kw.get('data_coleta') else None,
                        score=kw.get('score')
                    ))
                
                return ClusterType(
                    id=cluster_data.get('id'),
                    nome=cluster_data.get('nome'),
                    keywords=keywords,
                    score_medio=cluster_data.get('score_medio'),
                    volume_total=cluster_data.get('volume_total'),
                    data_criacao=datetime.fromisoformat(cluster_data.get('data_criacao')) if cluster_data.get('data_criacao') else None
                )
            
            return None
            
        except Exception as e:
            print(f"Erro ao buscar cluster {id}: {e}")
            return None
    
    def resolve_business_metrics(self, info, tipo=None, periodo=None, 
                               data_inicio=None, data_fim=None):
        """Resolve métricas de negócio"""
        try:
            business_metrics = BusinessMetrics()
            metrics_data = business_metrics.obter_metricas(
                tipo=tipo,
                periodo=periodo,
                data_inicio=data_inicio,
                data_fim=data_fim
            )
            
            metrics = []
            for metric in metrics_data:
                metrics.append(BusinessMetricType(
                    id=metric.get('id'),
                    nome=metric.get('nome'),
                    valor=metric.get('valor'),
                    tipo=metric.get('tipo'),
                    periodo=metric.get('periodo'),
                    data_calculo=datetime.fromisoformat(metric.get('data_calculo')) if metric.get('data_calculo') else None,
                    tendencia=metric.get('tendencia')
                ))
            
            return metrics
            
        except Exception as e:
            print(f"Erro ao buscar métricas de negócio: {e}")
            return []
    
    def resolve_performance_metrics(self, info, categoria=None, ultimas_horas=None):
        """Resolve métricas de performance"""
        try:
            from ...infrastructure.monitoramento.performance_monitor import PerformanceMonitor
            
            monitor = PerformanceMonitor()
            metrics_data = monitor.obter_metricas(
                categoria=categoria,
                ultimas_horas=ultimas_horas or 24
            )
            
            metrics = []
            for metric in metrics_data:
                metrics.append(PerformanceMetricType(
                    id=metric.get('id'),
                    nome=metric.get('nome'),
                    valor=metric.get('valor'),
                    unidade=metric.get('unidade'),
                    timestamp=datetime.fromisoformat(metric.get('timestamp')) if metric.get('timestamp') else None,
                    categoria=metric.get('categoria')
                ))
            
            return metrics
            
        except Exception as e:
            print(f"Erro ao buscar métricas de performance: {e}")
            return []
    
    def resolve_logs(self, info, nivel=None, modulo=None, 
                    data_inicio=None, data_fim=None, limit=None):
        """Resolve logs"""
        query = Log.query
        
        if nivel:
            query = query.filter(Log.nivel == nivel)
        
        if modulo:
            query = query.filter(Log.modulo == modulo)
        
        if data_inicio:
            query = query.filter(Log.timestamp >= data_inicio)
        
        if data_fim:
            query = query.filter(Log.timestamp <= data_fim)
        
        if limit:
            query = query.limit(limit)
        
        return query.order_by(Log.timestamp.desc()).all()
    
    def resolve_notificacoes(self, info, tipo=None, lida=None, limit=None):
        """Resolve notificações"""
        query = Notificacao.query
        
        if tipo:
            query = query.filter(Notificacao.tipo == tipo)
        
        if lida is not None:
            query = query.filter(Notificacao.lida == lida)
        
        if limit:
            query = query.limit(limit)
        
        return query.order_by(Notificacao.data_criacao.desc()).all()
    
    def resolve_estatisticas_gerais(self, info, periodo="30d"):
        """Resolve estatísticas gerais do sistema"""
        try:
            # Calcula período
            if periodo == "7d":
                data_inicio = datetime.now() - timedelta(days=7)
            elif periodo == "30d":
                data_inicio = datetime.now() - timedelta(days=30)
            elif periodo == "90d":
                data_inicio = datetime.now() - timedelta(days=90)
            else:
                data_inicio = datetime.now() - timedelta(days=30)
            
            # Estatísticas básicas
            total_nichos = Nicho.query.count()
            total_categorias = Categoria.query.count()
            total_execucoes = Execucao.query.filter(
                Execucao.data_inicio >= data_inicio
            ).count()
            total_keywords = 0  # Seria calculado pelo serviço de keywords
            
            # Execuções por status
            execucoes_por_status = {}
            for status in ['pendente', 'em_andamento', 'concluida', 'erro']:
                count = Execucao.query.filter(
                    Execucao.status == status,
                    Execucao.data_inicio >= data_inicio
                ).count()
                execucoes_por_status[status] = count
            
            # Notificações não lidas
            notificacoes_nao_lidas = Notificacao.query.filter(
                Notificacao.lida == False
            ).count()
            
            return {
                'total_nichos': total_nichos,
                'total_categorias': total_categorias,
                'total_execucoes': total_execucoes,
                'total_keywords': total_keywords,
                'execucoes_por_status': execucoes_por_status,
                'notificacoes_nao_lidas': notificacoes_nao_lidas,
                'periodo': periodo,
                'data_inicio': data_inicio.isoformat(),
                'data_fim': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Erro ao calcular estatísticas gerais: {e}")
            return {}

# =============================================================================
# MUTATIONS
# =============================================================================

class CreateNicho(graphene.Mutation):
    """Mutation para criar nicho"""
    class Arguments:
        input = NichoInput(required=True)
    
    nicho = graphene.Field(NichoType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, input):
        try:
            nicho = Nicho(
                nome=input.nome,
                descricao=input.descricao,
                ativo=input.ativo if input.ativo is not None else True
            )
            
            from ... import db
            db.session.add(nicho)
            db.session.commit()
            
            return CreateNicho(
                nicho=nicho,
                success=True,
                message="Nicho criado com sucesso"
            )
            
        except Exception as e:
            return CreateNicho(
                nicho=None,
                success=False,
                message=f"Erro ao criar nicho: {str(e)}"
            )

class UpdateNicho(graphene.Mutation):
    """Mutation para atualizar nicho"""
    class Arguments:
        id = graphene.ID(required=True)
        input = NichoInput(required=True)
    
    nicho = graphene.Field(NichoType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, id, input):
        try:
            nicho = Nicho.query.get(id)
            if not nicho:
                return UpdateNicho(
                    nicho=None,
                    success=False,
                    message="Nicho não encontrado"
                )
            
            if input.nome:
                nicho.nome = input.nome
            if input.descricao is not None:
                nicho.descricao = input.descricao
            if input.ativo is not None:
                nicho.ativo = input.ativo
            
            from ... import db
            db.session.commit()
            
            return UpdateNicho(
                nicho=nicho,
                success=True,
                message="Nicho atualizado com sucesso"
            )
            
        except Exception as e:
            return UpdateNicho(
                nicho=None,
                success=False,
                message=f"Erro ao atualizar nicho: {str(e)}"
            )

class CreateExecucao(graphene.Mutation):
    """Mutation para criar execução"""
    class Arguments:
        input = ExecucaoInput(required=True)
    
    execucao = graphene.Field(ExecucaoType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, input):
        try:
            # Valida nicho
            nicho = Nicho.query.get(input.nicho_id)
            if not nicho:
                return CreateExecucao(
                    execucao=None,
                    success=False,
                    message="Nicho não encontrado"
                )
            
            # Cria execução
            execucao = Execucao(
                nicho_id=input.nicho_id,
                categoria_id=input.categoria_id,
                parametros=input.parametros,
                status='pendente',
                data_inicio=datetime.now()
            )
            
            from ... import db
            db.session.add(execucao)
            db.session.commit()
            
            # Se não for agendada, inicia execução
            if not input.agendada:
                # Aqui você chamaria o serviço de execução
                pass
            
            return CreateExecucao(
                execucao=execucao,
                success=True,
                message="Execução criada com sucesso"
            )
            
        except Exception as e:
            return CreateExecucao(
                execucao=None,
                success=False,
                message=f"Erro ao criar execução: {str(e)}"
            )

class Mutation(graphene.ObjectType):
    """Mutations GraphQL principais"""
    
    create_nicho = CreateNicho.Field()
    update_nicho = UpdateNicho.Field()
    create_execucao = CreateExecucao.Field()

# =============================================================================
# SCHEMA PRINCIPAL
# =============================================================================

schema = graphene.Schema(query=Query, mutation=Mutation) 