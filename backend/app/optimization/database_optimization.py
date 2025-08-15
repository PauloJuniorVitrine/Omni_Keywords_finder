"""
Sistema de Otimização de Banco de Dados
Melhora performance das queries através de otimizações automáticas
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import time
from contextlib import asynccontextmanager

from sqlalchemy import text, create_engine, inspect
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class QueryType(Enum):
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    CREATE = "CREATE"
    ALTER = "ALTER"
    DROP = "DROP"


@dataclass
class QueryMetrics:
    query: str
    query_type: QueryType
    execution_time: float
    rows_affected: int
    timestamp: datetime
    table_name: Optional[str] = None
    index_used: Optional[str] = None
    full_table_scan: bool = False
    slow_query: bool = False


@dataclass
class OptimizationSuggestion:
    type: str
    description: str
    impact: str  # 'high', 'medium', 'low'
    estimated_improvement: float
    sql_statement: Optional[str] = None
    table_name: Optional[str] = None


class DatabaseOptimizer:
    """
    Otimizador de banco de dados com análise de performance
    """
    
    def __init__(self, database_url: str, config: Optional[Dict] = None):
        self.database_url = database_url
        self.config = config or {}
        self.query_metrics: List[QueryMetrics] = []
        self.slow_query_threshold = self.config.get('slow_query_threshold', 1.0)  # 1 segundo
        self.max_metrics_history = self.config.get('max_metrics_history', 10000)
        self.optimization_suggestions: List[OptimizationSuggestion] = []
        
        # Configuração do pool de conexões
        self.pool_config = {
            'pool_size': self.config.get('pool_size', 10),
            'max_overflow': self.config.get('max_overflow', 20),
            'pool_timeout': self.config.get('pool_timeout', 30),
            'pool_recycle': self.config.get('pool_recycle', 3600),
            'pool_pre_ping': self.config.get('pool_pre_ping', True)
        }
        
        self.engine = None
        self.async_engine = None
        self._initialize_engines()
    
    def _initialize_engines(self):
        """Inicializa engines síncrono e assíncrono"""
        try:
            # Engine síncrono
            self.engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                **self.pool_config
            )
            
            # Engine assíncrono (se suportado)
            if self.database_url.startswith(('postgresql+asyncpg', 'mysql+asyncmy')):
                self.async_engine = create_async_engine(
                    self.database_url,
                    poolclass=QueuePool,
                    **self.pool_config
                )
                
        except Exception as e:
            logger.error(f"Erro ao inicializar engines: {e}")
            raise
    
    async def analyze_query_performance(self, query: str, params: Optional[Dict] = None) -> QueryMetrics:
        """
        Analisa performance de uma query específica
        """
        start_time = time.time()
        query_type = self._detect_query_type(query)
        table_name = self._extract_table_name(query)
        
        try:
            if self.async_engine:
                async with self.async_engine.begin() as conn:
                    result = await conn.execute(text(query), params or {})
                    rows_affected = result.rowcount
            else:
                with self.engine.begin() as conn:
                    result = conn.execute(text(query), params or {})
                    rows_affected = result.rowcount
            
            execution_time = time.time() - start_time
            
            metrics = QueryMetrics(
                query=query,
                query_type=query_type,
                execution_time=execution_time,
                rows_affected=rows_affected,
                timestamp=datetime.now(),
                table_name=table_name,
                slow_query=execution_time > self.slow_query_threshold
            )
            
            self._add_query_metrics(metrics)
            return metrics
            
        except Exception as e:
            logger.error(f"Erro ao executar query: {e}")
            raise
    
    def _detect_query_type(self, query: str) -> QueryType:
        """Detecta o tipo de query"""
        query_upper = query.strip().upper()
        
        if query_upper.startswith('SELECT'):
            return QueryType.SELECT
        elif query_upper.startswith('INSERT'):
            return QueryType.INSERT
        elif query_upper.startswith('UPDATE'):
            return QueryType.UPDATE
        elif query_upper.startswith('DELETE'):
            return QueryType.DELETE
        elif query_upper.startswith('CREATE'):
            return QueryType.CREATE
        elif query_upper.startswith('ALTER'):
            return QueryType.ALTER
        elif query_upper.startswith('DROP'):
            return QueryType.DROP
        else:
            return QueryType.SELECT
    
    def _extract_table_name(self, query: str) -> Optional[str]:
        """Extrai nome da tabela da query"""
        import re
        
        # Padrões para extrair nome da tabela
        patterns = [
            r'FROM\s+(\w+)',
            r'UPDATE\s+(\w+)',
            r'INSERT\s+INTO\s+(\w+)',
            r'DELETE\s+FROM\s+(\w+)',
            r'CREATE\s+TABLE\s+(\w+)',
            r'ALTER\s+TABLE\s+(\w+)',
            r'DROP\s+TABLE\s+(\w+)'
        ]
        
        query_upper = query.upper()
        for pattern in patterns:
            match = re.search(pattern, query_upper)
            if match:
                return match.group(1).lower()
        
        return None
    
    def _add_query_metrics(self, metrics: QueryMetrics):
        """Adiciona métricas de query ao histórico"""
        self.query_metrics.append(metrics)
        
        # Limitar histórico
        if len(self.query_metrics) > self.max_metrics_history:
            self.query_metrics.pop(0)
    
    async def get_slow_queries(self, limit: int = 10) -> List[QueryMetrics]:
        """Obtém queries lentas"""
        slow_queries = [q for q in self.query_metrics if q.slow_query]
        return sorted(slow_queries, key=lambda x: x.execution_time, reverse=True)[:limit]
    
    async def get_query_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas das queries"""
        if not self.query_metrics:
            return {}
        
        total_queries = len(self.query_metrics)
        slow_queries = len([q for q in self.query_metrics if q.slow_query])
        
        # Estatísticas por tipo de query
        query_types = {}
        for query_type in QueryType:
            type_queries = [q for q in self.query_metrics if q.query_type == query_type]
            if type_queries:
                avg_time = sum(q.execution_time for q in type_queries) / len(type_queries)
                query_types[query_type.value] = {
                    'count': len(type_queries),
                    'avg_execution_time': avg_time,
                    'total_execution_time': sum(q.execution_time for q in type_queries)
                }
        
        # Estatísticas por tabela
        table_stats = {}
        for metrics in self.query_metrics:
            if metrics.table_name:
                if metrics.table_name not in table_stats:
                    table_stats[metrics.table_name] = {
                        'count': 0,
                        'total_time': 0,
                        'avg_time': 0
                    }
                
                table_stats[metrics.table_name]['count'] += 1
                table_stats[metrics.table_name]['total_time'] += metrics.execution_time
        
        # Calcular médias
        for table in table_stats:
            table_stats[table]['avg_time'] = (
                table_stats[table]['total_time'] / table_stats[table]['count']
            )
        
        return {
            'total_queries': total_queries,
            'slow_queries': slow_queries,
            'slow_query_percentage': (slow_queries / total_queries * 100) if total_queries > 0 else 0,
            'avg_execution_time': sum(q.execution_time for q in self.query_metrics) / total_queries,
            'query_types': query_types,
            'table_statistics': table_stats
        }
    
    async def analyze_index_usage(self) -> List[Dict[str, Any]]:
        """Analisa uso de índices"""
        if not self.engine:
            return []
        
        inspector = inspect(self.engine)
        index_analysis = []
        
        for table_name in inspector.get_table_names():
            indexes = inspector.get_indexes(table_name)
            columns = inspector.get_columns(table_name)
            
            # Verificar queries que usam esta tabela
            table_queries = [q for q in self.query_metrics if q.table_name == table_name]
            
            index_analysis.append({
                'table_name': table_name,
                'indexes': indexes,
                'columns': [col['name'] for col in columns],
                'query_count': len(table_queries),
                'avg_query_time': sum(q.execution_time for q in table_queries) / len(table_queries) if table_queries else 0
            })
        
        return index_analysis
    
    async def generate_optimization_suggestions(self) -> List[OptimizationSuggestion]:
        """Gera sugestões de otimização"""
        suggestions = []
        
        # Analisar queries lentas
        slow_queries = await self.get_slow_queries()
        for query in slow_queries:
            if query.query_type == QueryType.SELECT:
                suggestions.append(OptimizationSuggestion(
                    type='index_creation',
                    description=f'Query lenta detectada em {query.table_name}',
                    impact='high',
                    estimated_improvement=query.execution_time * 0.8,
                    table_name=query.table_name,
                    sql_statement=f"CREATE INDEX idx_{query.table_name}_optimized ON {query.table_name} (column_name)"
                ))
        
        # Analisar estatísticas
        stats = await self.get_query_statistics()
        
        # Sugerir otimizações de pool
        if stats.get('total_queries', 0) > 1000:
            suggestions.append(OptimizationSuggestion(
                type='pool_optimization',
                description='Alto volume de queries detectado',
                impact='medium',
                estimated_improvement=0.2,
                sql_statement=None
            ))
        
        # Sugerir análise de tabelas
        table_stats = stats.get('table_statistics', {})
        for table_name, table_stat in table_stats.items():
            if table_stat['avg_time'] > 0.5:  # Mais de 500ms
                suggestions.append(OptimizationSuggestion(
                    type='table_optimization',
                    description=f'Tabela {table_name} com performance baixa',
                    impact='medium',
                    estimated_improvement=table_stat['avg_time'] * 0.6,
                    table_name=table_name,
                    sql_statement=f"ANALYZE {table_name}"
                ))
        
        self.optimization_suggestions = suggestions
        return suggestions
    
    async def optimize_connection_pool(self) -> Dict[str, Any]:
        """Otimiza configuração do pool de conexões"""
        stats = await self.get_query_statistics()
        
        # Ajustar tamanho do pool baseado no volume de queries
        current_pool_size = self.pool_config['pool_size']
        total_queries = stats.get('total_queries', 0)
        
        if total_queries > 10000:
            recommended_pool_size = min(50, current_pool_size * 2)
        elif total_queries < 1000:
            recommended_pool_size = max(5, current_pool_size // 2)
        else:
            recommended_pool_size = current_pool_size
        
        return {
            'current_pool_size': current_pool_size,
            'recommended_pool_size': recommended_pool_size,
            'total_queries': total_queries,
            'optimization_needed': recommended_pool_size != current_pool_size
        }
    
    async def create_performance_indexes(self, table_name: str, columns: List[str]) -> bool:
        """Cria índices de performance"""
        try:
            index_name = f"idx_{table_name}_{'_'.join(columns)}"
            index_columns = ', '.join(columns)
            
            create_index_sql = f"""
            CREATE INDEX IF NOT EXISTS {index_name} 
            ON {table_name} ({index_columns})
            """
            
            if self.async_engine:
                async with self.async_engine.begin() as conn:
                    await conn.execute(text(create_index_sql))
            else:
                with self.engine.begin() as conn:
                    conn.execute(text(create_index_sql))
            
            logger.info(f"Índice criado: {index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar índice: {e}")
            return False
    
    async def analyze_table_structure(self, table_name: str) -> Dict[str, Any]:
        """Analisa estrutura de uma tabela"""
        if not self.engine:
            return {}
        
        inspector = inspect(self.engine)
        
        try:
            columns = inspector.get_columns(table_name)
            indexes = inspector.get_indexes(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)
            
            # Estatísticas da tabela
            with self.engine.begin() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                row_count = result.scalar()
                
                # Tamanho aproximado da tabela
                if 'postgresql' in self.database_url:
                    size_query = f"""
                    SELECT pg_size_pretty(pg_total_relation_size('{table_name}'))
                    """
                else:
                    size_query = f"SELECT COUNT(*) FROM {table_name}"  # Fallback
                
                result = conn.execute(text(size_query))
                table_size = result.scalar()
            
            return {
                'table_name': table_name,
                'columns': columns,
                'indexes': indexes,
                'foreign_keys': foreign_keys,
                'row_count': row_count,
                'table_size': table_size,
                'query_count': len([q for q in self.query_metrics if q.table_name == table_name])
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar tabela {table_name}: {e}")
            return {}
    
    async def get_database_health_report(self) -> Dict[str, Any]:
        """Gera relatório de saúde do banco de dados"""
        stats = await self.get_query_statistics()
        slow_queries = await self.get_slow_queries(5)
        index_analysis = await self.analyze_index_usage()
        pool_optimization = await self.optimize_connection_pool()
        suggestions = await self.generate_optimization_suggestions()
        
        # Calcular score de saúde (0-100)
        health_score = 100
        
        # Penalizar queries lentas
        slow_query_percentage = stats.get('slow_query_percentage', 0)
        if slow_query_percentage > 10:
            health_score -= 30
        elif slow_query_percentage > 5:
            health_score -= 15
        
        # Penalizar tempo médio alto
        avg_execution_time = stats.get('avg_execution_time', 0)
        if avg_execution_time > 1.0:
            health_score -= 25
        elif avg_execution_time > 0.5:
            health_score -= 10
        
        # Penalizar pool não otimizado
        if pool_optimization.get('optimization_needed', False):
            health_score -= 10
        
        health_score = max(0, health_score)
        
        return {
            'health_score': health_score,
            'status': 'healthy' if health_score >= 80 else 'warning' if health_score >= 60 else 'critical',
            'statistics': stats,
            'slow_queries': [q.__dict__ for q in slow_queries],
            'index_analysis': index_analysis,
            'pool_optimization': pool_optimization,
            'optimization_suggestions': [s.__dict__ for s in suggestions],
            'timestamp': datetime.now().isoformat()
        }
    
    async def cleanup_old_metrics(self, days: int = 30):
        """Remove métricas antigas"""
        cutoff_date = datetime.now() - timedelta(days=days)
        self.query_metrics = [
            q for q in self.query_metrics 
            if q.timestamp > cutoff_date
        ]
        logger.info(f"Métricas antigas removidas. Mantidas: {len(self.query_metrics)}")
    
    def export_metrics(self, filepath: str):
        """Exporta métricas para arquivo JSON"""
        try:
            data = {
                'query_metrics': [q.__dict__ for q in self.query_metrics],
                'optimization_suggestions': [s.__dict__ for s in self.optimization_suggestions],
                'export_timestamp': datetime.now().isoformat()
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"Métricas exportadas para: {filepath}")
            
        except Exception as e:
            logger.error(f"Erro ao exportar métricas: {e}")


# Decorator para monitorar queries
def monitor_query(func):
    """Decorator para monitorar performance de queries"""
    async def wrapper(*args, **kwargs):
        optimizer = DatabaseOptimizer.get_instance()
        
        if optimizer:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Adicionar métricas
                metrics = QueryMetrics(
                    query=str(func.__name__),
                    query_type=QueryType.SELECT,
                    execution_time=execution_time,
                    rows_affected=len(result) if hasattr(result, '__len__') else 0,
                    timestamp=datetime.now()
                )
                optimizer._add_query_metrics(metrics)
                
                return result
            except Exception as e:
                logger.error(f"Erro na query {func.__name__}: {e}")
                raise
        else:
            return await func(*args, **kwargs)
    
    return wrapper


# Context manager para monitoramento
@asynccontextmanager
async def monitored_query(query: str, params: Optional[Dict] = None):
    """Context manager para monitorar queries"""
    optimizer = DatabaseOptimizer.get_instance()
    
    if optimizer:
        start_time = time.time()
        try:
            yield
            execution_time = time.time() - start_time
            
            metrics = QueryMetrics(
                query=query,
                query_type=optimizer._detect_query_type(query),
                execution_time=execution_time,
                rows_affected=0,
                timestamp=datetime.now(),
                table_name=optimizer._extract_table_name(query)
            )
            optimizer._add_query_metrics(metrics)
            
        except Exception as e:
            logger.error(f"Erro na query monitorada: {e}")
            raise
    else:
        yield


# Singleton para instância global
class DatabaseOptimizerSingleton:
    _instance: Optional[DatabaseOptimizer] = None
    
    @classmethod
    def get_instance(cls) -> Optional[DatabaseOptimizer]:
        return cls._instance
    
    @classmethod
    def set_instance(cls, optimizer: DatabaseOptimizer):
        cls._instance = optimizer


# Adicionar método de classe ao DatabaseOptimizer
DatabaseOptimizer.get_instance = DatabaseOptimizerSingleton.get_instance
DatabaseOptimizer.set_instance = DatabaseOptimizerSingleton.set_instance 