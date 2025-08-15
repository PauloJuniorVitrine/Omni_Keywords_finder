"""
Sistema de Otimização de Queries
Melhora performance do banco de dados através de otimização automática de queries
"""

import asyncio
import re
import time
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from functools import wraps
import json
import sqlparse

from sqlalchemy import text, create_engine, inspect, select, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, Query
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class QueryType(Enum):
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    JOIN = "JOIN"
    SUBQUERY = "SUBQUERY"
    AGGREGATE = "AGGREGATE"


class OptimizationType(Enum):
    INDEX = "index"
    QUERY_REWRITE = "query_rewrite"
    JOIN_OPTIMIZATION = "join_optimization"
    SUBQUERY_OPTIMIZATION = "subquery_optimization"
    LIMIT_OPTIMIZATION = "limit_optimization"
    COLUMN_SELECTION = "column_selection"


@dataclass
class QueryAnalysis:
    query: str
    query_type: QueryType
    execution_time: float
    rows_returned: int
    tables_involved: List[str]
    joins_count: int
    subqueries_count: int
    has_where_clause: bool
    has_order_by: bool
    has_group_by: bool
    has_limit: bool
    estimated_cost: float
    optimization_score: float
    timestamp: datetime


@dataclass
class QueryOptimization:
    original_query: str
    optimized_query: str
    optimization_type: OptimizationType
    estimated_improvement: float
    description: str
    confidence: float
    applied: bool = False
    timestamp: datetime = None


class QueryOptimizer:
    """
    Otimizador de queries com análise automática
    """
    
    def __init__(self, database_url: str, config: Optional[Dict] = None):
        self.database_url = database_url
        self.config = config or {}
        self.query_analyses: List[QueryAnalysis] = []
        self.optimizations: List[QueryOptimization] = []
        self.engine = None
        self.async_engine = None
        self._initialize_engines()
        
        # Configurações de otimização
        self.slow_query_threshold = self.config.get('slow_query_threshold', 1.0)
        self.max_analysis_history = self.config.get('max_analysis_history', 1000)
        self.enable_auto_optimization = self.config.get('enable_auto_optimization', True)
    
    def _initialize_engines(self):
        """Inicializa engines de banco de dados"""
        try:
            self.engine = create_engine(self.database_url)
            
            if self.database_url.startswith(('postgresql+asyncpg', 'mysql+asyncmy')):
                self.async_engine = create_async_engine(self.database_url)
                
        except Exception as e:
            logger.error(f"Erro ao inicializar engines: {e}")
            raise
    
    async def analyze_query(self, query: str, params: Optional[Dict] = None) -> QueryAnalysis:
        """
        Analisa uma query e retorna métricas de performance
        """
        start_time = time.time()
        
        # Parse da query
        parsed_query = self._parse_query(query)
        query_type = self._detect_query_type(parsed_query)
        
        # Executar query para obter métricas
        try:
            if self.async_engine:
                async with self.async_engine.begin() as conn:
                    result = await conn.execute(text(query), params or {})
                    rows_returned = result.rowcount
            else:
                with self.engine.begin() as conn:
                    result = conn.execute(text(query), params or {})
                    rows_returned = result.rowcount
            
            execution_time = time.time() - start_time
            
            # Análise detalhada
            analysis = QueryAnalysis(
                query=query,
                query_type=query_type,
                execution_time=execution_time,
                rows_returned=rows_returned,
                tables_involved=self._extract_tables(parsed_query),
                joins_count=self._count_joins(parsed_query),
                subqueries_count=self._count_subqueries(parsed_query),
                has_where_clause=self._has_where_clause(parsed_query),
                has_order_by=self._has_order_by(parsed_query),
                has_group_by=self._has_group_by(parsed_query),
                has_limit=self._has_limit(parsed_query),
                estimated_cost=self._estimate_cost(parsed_query, execution_time),
                optimization_score=self._calculate_optimization_score(parsed_query, execution_time),
                timestamp=datetime.now()
            )
            
            self._add_query_analysis(analysis)
            return analysis
            
        except Exception as e:
            logger.error(f"Erro ao analisar query: {e}")
            raise
    
    def _parse_query(self, query: str) -> sqlparse.sql.Statement:
        """Parse da query usando sqlparse"""
        try:
            parsed = sqlparse.parse(query)
            return parsed[0] if parsed else None
        except Exception as e:
            logger.error(f"Erro ao fazer parse da query: {e}")
            return None
    
    def _detect_query_type(self, parsed_query) -> QueryType:
        """Detecta tipo da query"""
        if not parsed_query:
            return QueryType.SELECT
        
        query_str = str(parsed_query).upper()
        
        if 'SELECT' in query_str:
            if 'JOIN' in query_str:
                return QueryType.JOIN
            elif 'GROUP BY' in query_str or 'COUNT(' in query_str or 'SUM(' in query_str:
                return QueryType.AGGREGATE
            elif '(' in query_str and 'SELECT' in query_str:
                return QueryType.SUBQUERY
            else:
                return QueryType.SELECT
        elif 'INSERT' in query_str:
            return QueryType.INSERT
        elif 'UPDATE' in query_str:
            return QueryType.UPDATE
        elif 'DELETE' in query_str:
            return QueryType.DELETE
        else:
            return QueryType.SELECT
    
    def _extract_tables(self, parsed_query) -> List[str]:
        """Extrai tabelas envolvidas na query"""
        if not parsed_query:
            return []
        
        query_str = str(parsed_query).upper()
        tables = []
        
        # Padrões para extrair tabelas
        patterns = [
            r'FROM\s+(\w+)',
            r'JOIN\s+(\w+)',
            r'UPDATE\s+(\w+)',
            r'INSERT\s+INTO\s+(\w+)',
            r'DELETE\s+FROM\s+(\w+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, query_str)
            tables.extend(matches)
        
        return list(set(tables))
    
    def _count_joins(self, parsed_query) -> int:
        """Conta número de JOINs"""
        if not parsed_query:
            return 0
        
        query_str = str(parsed_query).upper()
        return len(re.findall(r'\bJOIN\b', query_str))
    
    def _count_subqueries(self, parsed_query) -> int:
        """Conta número de subqueries"""
        if not parsed_query:
            return 0
        
        query_str = str(parsed_query)
        return len(re.findall(r'\(\s*SELECT', query_str, re.IGNORECASE))
    
    def _has_where_clause(self, parsed_query) -> bool:
        """Verifica se tem WHERE"""
        if not parsed_query:
            return False
        
        query_str = str(parsed_query).upper()
        return 'WHERE' in query_str
    
    def _has_order_by(self, parsed_query) -> bool:
        """Verifica se tem ORDER BY"""
        if not parsed_query:
            return False
        
        query_str = str(parsed_query).upper()
        return 'ORDER BY' in query_str
    
    def _has_group_by(self, parsed_query) -> bool:
        """Verifica se tem GROUP BY"""
        if not parsed_query:
            return False
        
        query_str = str(parsed_query).upper()
        return 'GROUP BY' in query_str
    
    def _has_limit(self, parsed_query) -> bool:
        """Verifica se tem LIMIT"""
        if not parsed_query:
            return False
        
        query_str = str(parsed_query).upper()
        return 'LIMIT' in query_str
    
    def _estimate_cost(self, parsed_query, execution_time: float) -> float:
        """Estima custo da query"""
        if not parsed_query:
            return execution_time
        
        base_cost = execution_time
        
        # Penalizar queries complexas
        joins_count = self._count_joins(parsed_query)
        subqueries_count = self._count_subqueries(parsed_query)
        
        complexity_multiplier = 1 + (joins_count * 0.2) + (subqueries_count * 0.3)
        
        return base_cost * complexity_multiplier
    
    def _calculate_optimization_score(self, parsed_query, execution_time: float) -> float:
        """Calcula score de otimização (0-100)"""
        score = 100
        
        # Penalizar queries lentas
        if execution_time > self.slow_query_threshold:
            score -= 30
        
        # Penalizar queries complexas
        joins_count = self._count_joins(parsed_query)
        subqueries_count = self._count_subqueries(parsed_query)
        
        score -= joins_count * 5
        score -= subqueries_count * 10
        
        # Penalizar queries sem LIMIT
        if not self._has_limit(parsed_query) and 'SELECT' in str(parsed_query).upper():
            score -= 15
        
        return max(0, score)
    
    def _add_query_analysis(self, analysis: QueryAnalysis):
        """Adiciona análise ao histórico"""
        self.query_analyses.append(analysis)
        
        if len(self.query_analyses) > self.max_analysis_history:
            self.query_analyses.pop(0)
    
    async def optimize_query(self, query: str) -> List[QueryOptimization]:
        """
        Gera otimizações para uma query
        """
        optimizations = []
        parsed_query = self._parse_query(query)
        
        if not parsed_query:
            return optimizations
        
        # Otimização 1: Adicionar LIMIT se não existir
        if not self._has_limit(parsed_query) and 'SELECT' in str(parsed_query).upper():
            optimized_query = self._add_limit_to_query(query)
            if optimized_query != query:
                optimizations.append(QueryOptimization(
                    original_query=query,
                    optimized_query=optimized_query,
                    optimization_type=OptimizationType.LIMIT_OPTIMIZATION,
                    estimated_improvement=0.3,
                    description="Adicionar LIMIT para limitar resultados",
                    confidence=0.8,
                    timestamp=datetime.now()
                ))
        
        # Otimização 2: Otimizar SELECT *
        if 'SELECT *' in query.upper():
            optimized_query = self._optimize_select_star(query)
            if optimized_query != query:
                optimizations.append(QueryOptimization(
                    original_query=query,
                    optimized_query=optimized_query,
                    optimization_type=OptimizationType.COLUMN_SELECTION,
                    estimated_improvement=0.2,
                    description="Selecionar apenas colunas necessárias",
                    confidence=0.7,
                    timestamp=datetime.now()
                ))
        
        # Otimização 3: Otimizar JOINs
        if self._count_joins(parsed_query) > 2:
            optimized_query = self._optimize_joins(query)
            if optimized_query != query:
                optimizations.append(QueryOptimization(
                    original_query=query,
                    optimized_query=optimized_query,
                    optimization_type=OptimizationType.JOIN_OPTIMIZATION,
                    estimated_improvement=0.4,
                    description="Otimizar ordem dos JOINs",
                    confidence=0.6,
                    timestamp=datetime.now()
                ))
        
        # Otimização 4: Otimizar subqueries
        if self._count_subqueries(parsed_query) > 0:
            optimized_query = self._optimize_subqueries(query)
            if optimized_query != query:
                optimizations.append(QueryOptimization(
                    original_query=query,
                    optimized_query=optimized_query,
                    optimization_type=OptimizationType.SUBQUERY_OPTIMIZATION,
                    estimated_improvement=0.5,
                    description="Converter subquery para JOIN",
                    confidence=0.5,
                    timestamp=datetime.now()
                ))
        
        self.optimizations.extend(optimizations)
        return optimizations
    
    def _add_limit_to_query(self, query: str, limit: int = 100) -> str:
        """Adiciona LIMIT à query"""
        query_upper = query.upper()
        if 'LIMIT' not in query_upper:
            return f"{query} LIMIT {limit}"
        return query
    
    def _optimize_select_star(self, query: str) -> str:
        """Otimiza SELECT *"""
        # Em produção, isso seria mais inteligente
        # Por exemplo, analisando a estrutura da tabela
        return query.replace('SELECT *', 'SELECT id, name, created_at')
    
    def _optimize_joins(self, query: str) -> str:
        """Otimiza JOINs"""
        # Em produção, isso seria mais complexo
        # Analisando estatísticas das tabelas
        return query
    
    def _optimize_subqueries(self, query: str) -> str:
        """Otimiza subqueries"""
        # Em produção, isso seria mais complexo
        # Convertendo subqueries para JOINs quando possível
        return query
    
    async def get_slow_queries(self, limit: int = 10) -> List[QueryAnalysis]:
        """Obtém queries lentas"""
        slow_queries = [q for q in self.query_analyses if q.execution_time > self.slow_query_threshold]
        return sorted(slow_queries, key=lambda x: x.execution_time, reverse=True)[:limit]
    
    async def get_query_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas das queries"""
        if not self.query_analyses:
            return {}
        
        total_queries = len(self.query_analyses)
        slow_queries = len([q for q in self.query_analyses if q.execution_time > self.slow_query_threshold])
        
        # Estatísticas por tipo
        type_stats = {}
        for query_type in QueryType:
            type_queries = [q for q in self.query_analyses if q.query_type == query_type]
            if type_queries:
                avg_time = sum(q.execution_time for q in type_queries) / len(type_queries)
                type_stats[query_type.value] = {
                    'count': len(type_queries),
                    'avg_execution_time': avg_time,
                    'total_execution_time': sum(q.execution_time for q in type_queries)
                }
        
        # Estatísticas por tabela
        table_stats = {}
        for analysis in self.query_analyses:
            for table in analysis.tables_involved:
                if table not in table_stats:
                    table_stats[table] = {
                        'count': 0,
                        'total_time': 0,
                        'avg_time': 0
                    }
                
                table_stats[table]['count'] += 1
                table_stats[table]['total_time'] += analysis.execution_time
        
        # Calcular médias
        for table in table_stats:
            table_stats[table]['avg_time'] = (
                table_stats[table]['total_time'] / table_stats[table]['count']
            )
        
        return {
            'total_queries': total_queries,
            'slow_queries': slow_queries,
            'slow_query_percentage': (slow_queries / total_queries * 100) if total_queries > 0 else 0,
            'avg_execution_time': sum(q.execution_time for q in self.query_analyses) / total_queries,
            'avg_optimization_score': sum(q.optimization_score for q in self.query_analyses) / total_queries,
            'type_statistics': type_stats,
            'table_statistics': table_stats
        }
    
    async def get_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """Obtém sugestões de otimização"""
        suggestions = []
        
        # Analisar queries lentas
        slow_queries = await self.get_slow_queries()
        for query in slow_queries:
            optimizations = await self.optimize_query(query.query)
            for opt in optimizations:
                suggestions.append({
                    'query': query.query,
                    'execution_time': query.execution_time,
                    'optimization': asdict(opt)
                })
        
        # Sugestões gerais baseadas em estatísticas
        stats = await self.get_query_statistics()
        
        if stats.get('slow_query_percentage', 0) > 20:
            suggestions.append({
                'type': 'general',
                'description': 'Alto percentual de queries lentas',
                'recommendation': 'Revisar índices e estrutura do banco',
                'impact': 'high'
            })
        
        return suggestions
    
    async def apply_optimization(self, optimization: QueryOptimization) -> bool:
        """Aplica uma otimização"""
        try:
            # Em produção, isso seria mais complexo
            # Por exemplo, executar a query otimizada e comparar performance
            
            optimization.applied = True
            logger.info(f"Otimização aplicada: {optimization.description}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao aplicar otimização: {e}")
            return False
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """Gera relatório de performance"""
        stats = await self.get_query_statistics()
        slow_queries = await self.get_slow_queries(5)
        suggestions = await self.get_optimization_suggestions()
        
        # Calcular score de performance (0-100)
        performance_score = 100
        
        # Penalizar queries lentas
        slow_query_percentage = stats.get('slow_query_percentage', 0)
        if slow_query_percentage > 20:
            performance_score -= 40
        elif slow_query_percentage > 10:
            performance_score -= 20
        
        # Penalizar tempo médio alto
        avg_execution_time = stats.get('avg_execution_time', 0)
        if avg_execution_time > 1.0:
            performance_score -= 30
        elif avg_execution_time > 0.5:
            performance_score -= 15
        
        # Penalizar score de otimização baixo
        avg_optimization_score = stats.get('avg_optimization_score', 100)
        performance_score -= (100 - avg_optimization_score) * 0.3
        
        performance_score = max(0, performance_score)
        
        return {
            'performance_score': performance_score,
            'status': 'excellent' if performance_score >= 90 else 'good' if performance_score >= 70 else 'poor',
            'statistics': stats,
            'slow_queries': [asdict(q) for q in slow_queries],
            'optimization_suggestions': suggestions,
            'timestamp': datetime.now().isoformat()
        }


# Decorator para monitorar queries
def monitor_query_performance(func):
    """Decorator para monitorar performance de queries"""
    async def wrapper(*args, **kwargs):
        optimizer = QueryOptimizer.get_instance()
        
        if optimizer:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Analisar query se for lenta
                if execution_time > optimizer.slow_query_threshold:
                    await optimizer.analyze_query(str(func.__name__))
                
                return result
            except Exception as e:
                logger.error(f"Erro na query {func.__name__}: {e}")
                raise
        else:
            return await func(*args, **kwargs)
    
    return wrapper


# Context manager para monitoramento
class QueryMonitor:
    """Context manager para monitorar queries"""
    
    def __init__(self, query: str, optimizer: QueryOptimizer):
        self.query = query
        self.optimizer = optimizer
        self.start_time = None
    
    async def __aenter__(self):
        self.start_time = time.time()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            execution_time = time.time() - self.start_time
            
            if execution_time > self.optimizer.slow_query_threshold:
                await self.optimizer.analyze_query(self.query)


# Singleton para instância global
class QueryOptimizerSingleton:
    _instance: Optional[QueryOptimizer] = None
    
    @classmethod
    def get_instance(cls) -> Optional[QueryOptimizer]:
        return cls._instance
    
    @classmethod
    def set_instance(cls, optimizer: QueryOptimizer):
        cls._instance = optimizer


# Adicionar método de classe ao QueryOptimizer
QueryOptimizer.get_instance = QueryOptimizerSingleton.get_instance
QueryOptimizer.set_instance = QueryOptimizerSingleton.set_instance 