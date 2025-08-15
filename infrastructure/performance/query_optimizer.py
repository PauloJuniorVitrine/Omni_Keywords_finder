#!/usr/bin/env python3
"""
🎯 Otimizador de Queries - IMP-016
==================================

Tracing ID: QUERY_OPTIMIZER_IMP016_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Sistema avançado de otimização de queries que:
- Analisa performance de queries
- Sugere otimizações automáticas
- Identifica queries lentas
- Recomenda índices
- Monitora execução
- Fornece relatórios detalhados

Prompt: CHECKLIST_CONFIABILIDADE.md - IMP-016
Ruleset: enterprise_control_layer.yaml
"""

import time
import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import statistics
import threading
from functools import wraps

# SQL parsing
import sqlparse
from sqlparse.sql import Token, TokenList, Identifier, Function, Where, Comparison

# Logging estruturado
from shared.logger import logger

# Observabilidade
from infrastructure.observability.metrics import MetricsCollector
from infrastructure.observability.tracing import trace_function


class QueryType(Enum):
    """Tipos de queries."""
    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    CREATE = "create"
    ALTER = "alter"
    DROP = "drop"


class OptimizationLevel(Enum):
    """Níveis de otimização."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class QueryMetrics:
    """Métricas de uma query."""
    sql: str
    execution_time: float
    rows_returned: int
    rows_affected: int
    cpu_usage: float
    memory_usage: float
    io_operations: int
    timestamp: datetime = field(default_factory=datetime.now)
    query_type: QueryType = QueryType.SELECT
    optimization_level: OptimizationLevel = OptimizationLevel.LOW


@dataclass
class QueryAnalysis:
    """Análise de uma query."""
    sql: str
    query_type: QueryType
    tables: List[str]
    columns: List[str]
    where_conditions: List[str]
    joins: List[str]
    order_by: List[str]
    group_by: List[str]
    has_limit: bool
    limit_value: Optional[int]
    complexity_score: float
    optimization_suggestions: List[str]
    recommended_indexes: List[str]
    estimated_improvement: float


@dataclass
class QueryOptimizerConfig:
    """Configuração do otimizador de queries."""
    slow_query_threshold: float = 1.0  # segundos
    max_query_history: int = 10000
    analysis_interval: int = 300  # 5 minutos
    enable_auto_optimization: bool = True
    enable_index_suggestions: bool = True
    enable_query_rewriting: bool = True
    max_suggestions_per_query: int = 5
    complexity_threshold: float = 0.7


class QueryOptimizer:
    """
    Sistema de otimização de queries.
    
    Responsável por:
    - Analisar performance de queries
    - Identificar queries lentas
    - Sugerir otimizações
    - Recomendar índices
    - Monitorar execução
    """
    
    def __init__(self, config: QueryOptimizerConfig):
        self.config = config
        self.metrics_collector = MetricsCollector()
        
        # Histórico de queries
        self.query_history = deque(maxlen=config.max_query_history)
        self.slow_queries = deque(maxlen=1000)
        
        # Análises
        self.query_analyses = {}
        self.optimization_suggestions = defaultdict(list)
        
        # Threading
        self.analysis_thread = None
        self.optimization_thread = None
        self.monitoring_active = False
        
        # Locks
        self.history_lock = threading.RLock()
        self.analysis_lock = threading.RLock()
        
        logger.info(f"QueryOptimizer inicializado com threshold: {config.slow_query_threshold}s")
    
    @trace_function(operation_name="start_monitoring", service_name="query-optimizer")
    def start_monitoring(self) -> bool:
        """Inicia o monitoramento de queries."""
        try:
            if self.monitoring_active:
                logger.warning("Monitoramento de queries já está ativo")
                return True
            
            self.monitoring_active = True
            
            # Iniciar thread de análise
            self.analysis_thread = threading.Thread(
                target=self._analysis_loop,
                daemon=True
            )
            self.analysis_thread.start()
            
            # Iniciar thread de otimização
            if self.config.enable_auto_optimization:
                self.optimization_thread = threading.Thread(
                    target=self._optimization_loop,
                    daemon=True
                )
                self.optimization_thread.start()
            
            logger.info("Monitoramento de queries iniciado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao iniciar monitoramento de queries: {str(e)}")
            return False
    
    @trace_function(operation_name="stop_monitoring", service_name="query-optimizer")
    def stop_monitoring(self) -> bool:
        """Para o monitoramento de queries."""
        try:
            self.monitoring_active = False
            
            if self.analysis_thread:
                self.analysis_thread.join(timeout=5)
            
            if self.optimization_thread:
                self.optimization_thread.join(timeout=5)
            
            logger.info("Monitoramento de queries parado")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao parar monitoramento de queries: {str(e)}")
            return False
    
    @trace_function(operation_name="record_query", service_name="query-optimizer")
    def record_query(self, sql: str, execution_time: float, **kwargs) -> bool:
        """Registra execução de uma query."""
        try:
            # Criar métricas
            metrics = QueryMetrics(
                sql=sql,
                execution_time=execution_time,
                rows_returned=kwargs.get('rows_returned', 0),
                rows_affected=kwargs.get('rows_affected', 0),
                cpu_usage=kwargs.get('cpu_usage', 0.0),
                memory_usage=kwargs.get('memory_usage', 0.0),
                io_operations=kwargs.get('io_operations', 0),
                query_type=self._detect_query_type(sql)
            )
            
            # Adicionar ao histórico
            with self.history_lock:
                self.query_history.append(metrics)
            
            # Verificar se é query lenta
            if execution_time > self.config.slow_query_threshold:
                with self.history_lock:
                    self.slow_queries.append(metrics)
                
                # Analisar automaticamente
                self._analyze_slow_query(metrics)
            
            # Enviar métricas
            self._send_query_metrics(metrics)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao registrar query: {str(e)}")
            return False
    
    @trace_function(operation_name="analyze_query", service_name="query-optimizer")
    def analyze_query(self, sql: str) -> QueryAnalysis:
        """Analisa uma query e fornece sugestões de otimização."""
        try:
            # Parse da query
            parsed = sqlparse.parse(sql)[0]
            
            # Extrair informações
            query_type = self._detect_query_type(sql)
            tables = self._extract_tables(parsed)
            columns = self._extract_columns(parsed)
            where_conditions = self._extract_where_conditions(parsed)
            joins = self._extract_joins(parsed)
            order_by = self._extract_order_by(parsed)
            group_by = self._extract_group_by(parsed)
            has_limit, limit_value = self._extract_limit(parsed)
            
            # Calcular complexidade
            complexity_score = self._calculate_complexity(
                tables, columns, where_conditions, joins, order_by, group_by
            )
            
            # Gerar sugestões
            optimization_suggestions = self._generate_optimization_suggestions(
                sql, tables, columns, where_conditions, joins, order_by, group_by, has_limit
            )
            
            # Recomendar índices
            recommended_indexes = self._recommend_indexes(
                tables, columns, where_conditions, joins, order_by, group_by
            )
            
            # Estimar melhoria
            estimated_improvement = self._estimate_improvement(
                complexity_score, len(optimization_suggestions), len(recommended_indexes)
            )
            
            analysis = QueryAnalysis(
                sql=sql,
                query_type=query_type,
                tables=tables,
                columns=columns,
                where_conditions=where_conditions,
                joins=joins,
                order_by=order_by,
                group_by=group_by,
                has_limit=has_limit,
                limit_value=limit_value,
                complexity_score=complexity_score,
                optimization_suggestions=optimization_suggestions,
                recommended_indexes=recommended_indexes,
                estimated_improvement=estimated_improvement
            )
            
            # Armazenar análise
            with self.analysis_lock:
                self.query_analyses[sql] = analysis
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erro ao analisar query: {str(e)}")
            return QueryAnalysis(
                sql=sql,
                query_type=QueryType.SELECT,
                tables=[],
                columns=[],
                where_conditions=[],
                joins=[],
                order_by=[],
                group_by=[],
                has_limit=False,
                limit_value=None,
                complexity_score=1.0,
                optimization_suggestions=[f"Erro na análise: {str(e)}"],
                recommended_indexes=[],
                estimated_improvement=0.0
            )
    
    @trace_function(operation_name="optimize_query", service_name="query-optimizer")
    def optimize_query(self, sql: str) -> Dict[str, Any]:
        """Otimiza uma query automaticamente."""
        try:
            # Analisar query
            analysis = self.analyze_query(sql)
            
            # Aplicar otimizações
            optimizations = []
            
            # Rewrite da query se habilitado
            if self.config.enable_query_rewriting:
                optimized_sql = self._rewrite_query(analysis)
                if optimized_sql != sql:
                    optimizations.append({
                        'type': 'query_rewrite',
                        'original': sql,
                        'optimized': optimized_sql,
                        'improvement': analysis.estimated_improvement
                    })
            
            # Sugerir índices
            if self.config.enable_index_suggestions and analysis.recommended_indexes:
                optimizations.append({
                    'type': 'index_suggestions',
                    'indexes': analysis.recommended_indexes,
                    'improvement': analysis.estimated_improvement * 0.5
                })
            
            # Sugestões de otimização
            if analysis.optimization_suggestions:
                optimizations.append({
                    'type': 'optimization_suggestions',
                    'suggestions': analysis.optimization_suggestions[:self.config.max_suggestions_per_query],
                    'improvement': analysis.estimated_improvement * 0.3
                })
            
            return {
                'original_query': sql,
                'analysis': analysis,
                'optimizations': optimizations,
                'total_improvement': sum(o.get('improvement', 0) for o in optimizations)
            }
            
        except Exception as e:
            logger.error(f"Erro ao otimizar query: {str(e)}")
            return {"error": str(e)}
    
    @trace_function(operation_name="get_slow_queries", service_name="query-optimizer")
    def get_slow_queries(self, limit: int = 10) -> List[QueryMetrics]:
        """Obtém queries lentas."""
        try:
            with self.history_lock:
                return list(self.slow_queries)[-limit:]
        except Exception as e:
            logger.error(f"Erro ao obter queries lentas: {str(e)}")
            return []
    
    @trace_function(operation_name="get_query_stats", service_name="query-optimizer")
    def get_query_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas de queries."""
        try:
            with self.history_lock:
                if not self.query_history:
                    return {"error": "Nenhuma query registrada"}
                
                # Estatísticas gerais
                total_queries = len(self.query_history)
                slow_queries_count = len(self.slow_queries)
                
                # Tempos de execução
                execution_times = [q.execution_time for q in self.query_history]
                avg_execution_time = statistics.mean(execution_times)
                max_execution_time = max(execution_times)
                min_execution_time = min(execution_times)
                
                # Por tipo de query
                query_types = defaultdict(int)
                for query in self.query_history:
                    query_types[query.query_type.value] += 1
                
                # Queries mais lentas
                slowest_queries = sorted(
                    self.query_history,
                    key=lambda q: q.execution_time,
                    reverse=True
                )[:5]
                
                stats = {
                    'total_queries': total_queries,
                    'slow_queries': slow_queries_count,
                    'slow_query_percentage': (slow_queries_count / total_queries) * 100,
                    'execution_times': {
                        'average': avg_execution_time,
                        'maximum': max_execution_time,
                        'minimum': min_execution_time,
                        'median': statistics.median(execution_times)
                    },
                    'query_types': dict(query_types),
                    'slowest_queries': [
                        {
                            'sql': q.sql[:100] + '...' if len(q.sql) > 100 else q.sql,
                            'execution_time': q.execution_time,
                            'query_type': q.query_type.value,
                            'timestamp': q.timestamp.isoformat()
                        }
                        for q in slowest_queries
                    ],
                    'optimization_suggestions': len(self.optimization_suggestions),
                    'analyzed_queries': len(self.query_analyses)
                }
                
                return stats
                
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return {"error": str(e)}
    
    def _analysis_loop(self):
        """Loop de análise de queries."""
        while self.monitoring_active:
            try:
                # Analisar queries lentas
                slow_queries = self.get_slow_queries(50)
                for query in slow_queries:
                    self._analyze_slow_query(query)
                
                time.sleep(self.config.analysis_interval)
            except Exception as e:
                logger.error(f"Erro no loop de análise: {str(e)}")
                time.sleep(60)
    
    def _optimization_loop(self):
        """Loop de otimização."""
        while self.monitoring_active:
            try:
                # Otimizar queries frequentes
                frequent_queries = self._get_frequent_queries()
                for sql in frequent_queries:
                    self.optimize_query(sql)
                
                time.sleep(self.config.analysis_interval * 2)
            except Exception as e:
                logger.error(f"Erro no loop de otimização: {str(e)}")
                time.sleep(120)
    
    def _analyze_slow_query(self, metrics: QueryMetrics):
        """Analisa uma query lenta."""
        try:
            analysis = self.analyze_query(metrics.sql)
            
            # Armazenar sugestões
            if analysis.optimization_suggestions:
                with self.analysis_lock:
                    self.optimization_suggestions[metrics.sql].extend(
                        analysis.optimization_suggestions
                    )
            
            logger.info(f"Query lenta analisada: {metrics.execution_time}s - {len(analysis.optimization_suggestions)} sugestões")
            
        except Exception as e:
            logger.error(f"Erro ao analisar query lenta: {str(e)}")
    
    def _detect_query_type(self, sql: str) -> QueryType:
        """Detecta o tipo de query."""
        sql_lower = sql.strip().lower()
        
        if sql_lower.startswith('select'):
            return QueryType.SELECT
        elif sql_lower.startswith('insert'):
            return QueryType.INSERT
        elif sql_lower.startswith('update'):
            return QueryType.UPDATE
        elif sql_lower.startswith('delete'):
            return QueryType.DELETE
        elif sql_lower.startswith('create'):
            return QueryType.CREATE
        elif sql_lower.startswith('alter'):
            return QueryType.ALTER
        elif sql_lower.startswith('drop'):
            return QueryType.DROP
        else:
            return QueryType.SELECT
    
    def _extract_tables(self, parsed) -> List[str]:
        """Extrai tabelas da query."""
        tables = []
        
        for token in parsed.tokens:
            if hasattr(token, 'tokens'):
                tables.extend(self._extract_tables(token))
            elif isinstance(token, Identifier) and token.get_name():
                tables.append(token.get_name())
        
        return list(set(tables))
    
    def _extract_columns(self, parsed) -> List[str]:
        """Extrai colunas da query."""
        columns = []
        
        for token in parsed.tokens:
            if hasattr(token, 'tokens'):
                columns.extend(self._extract_columns(token))
            elif isinstance(token, Identifier) and token.get_name():
                columns.append(token.get_name())
        
        return list(set(columns))
    
    def _extract_where_conditions(self, parsed) -> List[str]:
        """Extrai condições WHERE."""
        conditions = []
        
        for token in parsed.tokens:
            if isinstance(token, Where):
                conditions.append(str(token))
            elif hasattr(token, 'tokens'):
                conditions.extend(self._extract_where_conditions(token))
        
        return conditions
    
    def _extract_joins(self, parsed) -> List[str]:
        """Extrai JOINs da query."""
        joins = []
        
        # Implementação simplificada
        sql_str = str(parsed).lower()
        if 'join' in sql_str:
            joins.append('join_detected')
        
        return joins
    
    def _extract_order_by(self, parsed) -> List[str]:
        """Extrai ORDER BY da query."""
        order_by = []
        
        # Implementação simplificada
        sql_str = str(parsed).lower()
        if 'order by' in sql_str:
            order_by.append('order_by_detected')
        
        return order_by
    
    def _extract_group_by(self, parsed) -> List[str]:
        """Extrai GROUP BY da query."""
        group_by = []
        
        # Implementação simplificada
        sql_str = str(parsed).lower()
        if 'group by' in sql_str:
            group_by.append('group_by_detected')
        
        return group_by
    
    def _extract_limit(self, parsed) -> Tuple[bool, Optional[int]]:
        """Extrai LIMIT da query."""
        # Implementação simplificada
        sql_str = str(parsed).lower()
        if 'limit' in sql_str:
            return True, None
        return False, None
    
    def _calculate_complexity(self, tables: List[str], columns: List[str], 
                            where_conditions: List[str], joins: List[str],
                            order_by: List[str], group_by: List[str]) -> float:
        """Calcula complexidade da query."""
        complexity = 0.0
        
        # Número de tabelas
        complexity += len(tables) * 0.1
        
        # Número de colunas
        complexity += len(columns) * 0.05
        
        # Condições WHERE
        complexity += len(where_conditions) * 0.2
        
        # JOINs
        complexity += len(joins) * 0.3
        
        # ORDER BY
        complexity += len(order_by) * 0.1
        
        # GROUP BY
        complexity += len(group_by) * 0.2
        
        return min(complexity, 1.0)
    
    def _generate_optimization_suggestions(self, sql: str, tables: List[str],
                                         columns: List[str], where_conditions: List[str],
                                         joins: List[str], order_by: List[str],
                                         group_by: List[str], has_limit: bool) -> List[str]:
        """Gera sugestões de otimização."""
        suggestions = []
        
        # Verificar SELECT *
        if 'select *' in sql.lower():
            suggestions.append("Evite usar SELECT *. Especifique apenas as colunas necessárias.")
        
        # Verificar LIMIT
        if not has_limit and len(tables) > 0:
            suggestions.append("Considere adicionar LIMIT para limitar o número de resultados.")
        
        # Verificar múltiplas tabelas sem JOIN
        if len(tables) > 1 and not joins:
            suggestions.append("Use JOINs explícitos em vez de múltiplas tabelas no FROM.")
        
        # Verificar condições WHERE
        if len(where_conditions) > 3:
            suggestions.append("Considere simplificar as condições WHERE ou criar índices compostos.")
        
        # Verificar ORDER BY sem índice
        if order_by and not where_conditions:
            suggestions.append("Considere adicionar condições WHERE antes de ORDER BY.")
        
        return suggestions
    
    def _recommend_indexes(self, tables: List[str], columns: List[str],
                          where_conditions: List[str], joins: List[str],
                          order_by: List[str], group_by: List[str]) -> List[str]:
        """Recomenda índices para a query."""
        indexes = []
        
        # Índices para condições WHERE
        for condition in where_conditions:
            if '=' in condition:
                indexes.append(f"idx_{tables[0]}_where_condition")
        
        # Índices para JOINs
        if joins:
            indexes.append(f"idx_{tables[0]}_join_key")
        
        # Índices para ORDER BY
        if order_by:
            indexes.append(f"idx_{tables[0]}_order_by")
        
        # Índices para GROUP BY
        if group_by:
            indexes.append(f"idx_{tables[0]}_group_by")
        
        return list(set(indexes))
    
    def _estimate_improvement(self, complexity: float, suggestions_count: int,
                            indexes_count: int) -> float:
        """Estima melhoria de performance."""
        improvement = 0.0
        
        # Melhoria baseada na complexidade
        improvement += complexity * 0.3
        
        # Melhoria baseada nas sugestões
        improvement += min(suggestions_count * 0.1, 0.3)
        
        # Melhoria baseada nos índices
        improvement += min(indexes_count * 0.2, 0.4)
        
        return min(improvement, 1.0)
    
    def _rewrite_query(self, analysis: QueryAnalysis) -> str:
        """Reescreve a query para otimização."""
        # Implementação simplificada
        sql = analysis.sql
        
        # Adicionar LIMIT se não existir
        if not analysis.has_limit and analysis.query_type == QueryType.SELECT:
            sql += " LIMIT 1000"
        
        return sql
    
    def _get_frequent_queries(self) -> List[str]:
        """Obtém queries frequentes."""
        try:
            with self.history_lock:
                # Agrupar por SQL
                query_counts = defaultdict(int)
                for query in self.query_history:
                    query_counts[query.sql] += 1
                
                # Retornar as mais frequentes
                frequent_queries = sorted(
                    query_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
                
                return [sql for sql, count in frequent_queries if count > 5]
                
        except Exception as e:
            logger.error(f"Erro ao obter queries frequentes: {str(e)}")
            return []
    
    def _send_query_metrics(self, metrics: QueryMetrics):
        """Envia métricas de query para observabilidade."""
        try:
            self.metrics_collector.record_metric("query.execution_time", metrics.execution_time)
            self.metrics_collector.record_metric("query.rows_returned", metrics.rows_returned)
            self.metrics_collector.record_metric("query.rows_affected", metrics.rows_affected)
            self.metrics_collector.record_metric("query.cpu_usage", metrics.cpu_usage)
            self.metrics_collector.record_metric("query.memory_usage", metrics.memory_usage)
            self.metrics_collector.record_metric("query.io_operations", metrics.io_operations)
            
            # Métricas por tipo
            self.metrics_collector.record_metric(f"query.{metrics.query_type.value}.count", 1)
            
        except Exception as e:
            logger.error(f"Erro ao enviar métricas de query: {str(e)}")


# Decorator para monitoramento de queries
def monitor_query(optimizer: QueryOptimizer):
    """Decorator para monitoramento automático de queries."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                # Registrar query se for uma função de banco
                if hasattr(func, '__name__') and 'query' in func.__name__.lower():
                    execution_time = time.time() - start_time
                    optimizer.record_query(
                        sql=str(args[0]) if args else "unknown",
                        execution_time=execution_time,
                        rows_returned=len(result) if isinstance(result, (list, tuple)) else 1
                    )
                
                return result
                
            except Exception as e:
                # Registrar erro
                execution_time = time.time() - start_time
                optimizer.record_query(
                    sql=str(args[0]) if args else "error",
                    execution_time=execution_time,
                    rows_returned=0
                )
                raise
                
        return wrapper
    return decorator


# Função global para inicializar otimizador de queries
def initialize_query_optimizer(config: Optional[QueryOptimizerConfig] = None) -> QueryOptimizer:
    """Inicializa o otimizador de queries global."""
    if config is None:
        config = QueryOptimizerConfig()
    
    optimizer = QueryOptimizer(config)
    optimizer.start_monitoring()
    
    logger.info("Otimizador de queries inicializado globalmente")
    return optimizer


# Instância global
_global_query_optimizer: Optional[QueryOptimizer] = None


def get_global_query_optimizer() -> Optional[QueryOptimizer]:
    """Obtém a instância global do otimizador de queries."""
    return _global_query_optimizer


def set_global_query_optimizer(optimizer: QueryOptimizer):
    """Define a instância global do otimizador de queries."""
    global _global_query_optimizer
    _global_query_optimizer = optimizer 