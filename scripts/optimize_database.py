"""
Script de Otimização de Database - Omni Keywords Finder

Tracing ID: IMP002_DATABASE_OPTIMIZATION_001
Data: 2025-01-27
Versão: 2.0
Status: Em Implementação

Implementa otimizações de database:
- Análise de queries lentas
- Criação de índices otimizados
- Connection pooling avançado
- Read replicas
- Performance monitoring
- Backup automático
- Query caching
"""

import sqlite3
import time
import json
import logging
import threading
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from contextlib import contextmanager
import queue
import statistics
from datetime import datetime, timedelta
import shutil
import os
import hashlib
import pickle
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)string_data - %(name)string_data - %(levelname)string_data - %(message)string_data'
)
logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Tipos de queries para análise"""
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    CREATE = "CREATE"
    ALTER = "ALTER"


@dataclass
class QueryMetrics:
    """Métricas de performance de query"""
    query: str
    query_type: QueryType
    execution_time: float
    rows_affected: int
    timestamp: datetime
    explain_plan: Optional[str] = None
    index_usage: Optional[str] = None
    table_scans: int = 0
    index_scans: int = 0


@dataclass
class IndexRecommendation:
    """Recomendação de índice"""
    table_name: str
    column_name: str
    index_type: str
    expected_improvement: float
    creation_cost: float
    priority: int  # 1-10, onde 10 é mais crítico


@dataclass
class ConnectionPoolStats:
    """Estatísticas do connection pool"""
    total_connections: int
    active_connections: int
    idle_connections: int
    max_wait_time: float
    avg_wait_time: float
    connection_errors: int
    pool_hit_ratio: float


class AdvancedConnectionPool:
    """Pool de conexões avançado com métricas e health checks"""
    
    def __init__(self, db_path: str, max_connections: int = 20, min_connections: int = 5):
        self.db_path = db_path
        self.max_connections = max_connections
        self.min_connections = min_connections
        self.connection_pool = queue.Queue(maxsize=max_connections)
        self.active_connections = 0
        self.connection_errors = 0
        self.wait_times = []
        self.health_check_interval = 300  # 5 minutos
        self.connection_timeout = 30  # 30 segundos
        
        # Inicializa pool
        self._initialize_pool()
        
        # Inicia health check em background
        self.health_check_thread = threading.Thread(target=self._health_check_loop, daemon=True)
        self.health_check_thread.start()
        
        logger.info(f"Advanced Connection Pool inicializado: {min_connections}-{max_connections} conexões")
    
    def _initialize_pool(self):
        """Inicializa pool com conexões mínimas"""
        for _ in range(self.min_connections):
            conn = self._create_connection()
            if conn:
                self.connection_pool.put(conn)
    
    def _create_connection(self) -> Optional[sqlite3.Connection]:
        """Cria nova conexão com configurações otimizadas"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=self.connection_timeout)
            conn.row_factory = sqlite3.Row
            
            # Configurações de performance
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=MEMORY")
            conn.execute("PRAGMA mmap_size=268435456")  # 256MB
            
            return conn
        except Exception as e:
            logger.error(f"Erro ao criar conexão: {e}")
            self.connection_errors += 1
            return None
    
    def get_connection(self, timeout: float = 5.0) -> Optional[sqlite3.Connection]:
        """Obtém conexão do pool com timeout"""
        start_time = time.time()
        
        try:
            # Tenta obter conexão existente
            conn = self.connection_pool.get(timeout=timeout)
            self.active_connections += 1
            
            # Verifica se conexão ainda é válida
            if self._is_connection_valid(conn):
                wait_time = time.time() - start_time
                self.wait_times.append(wait_time)
                return conn
            else:
                # Reconecta se necessário
                conn.close()
                conn = self._create_connection()
                if conn:
                    self.active_connections += 1
                    return conn
                else:
                    self.connection_errors += 1
                    return None
                    
        except queue.Empty:
            # Cria nova conexão se pool está cheio
            if self.active_connections < self.max_connections:
                conn = self._create_connection()
                if conn:
                    self.active_connections += 1
                    return conn
            
            self.connection_errors += 1
            logger.error("Timeout ao obter conexão do pool")
            return None
    
    def return_connection(self, conn: sqlite3.Connection):
        """Retorna conexão ao pool"""
        if conn:
            try:
                # Rollback qualquer transação não commitada
                conn.rollback()
                
                # Retorna ao pool se não estiver cheio
                if self.connection_pool.qsize() < self.max_connections:
                    self.connection_pool.put(conn)
                else:
                    conn.close()
                
                self.active_connections = max(0, self.active_connections - 1)
                
            except Exception as e:
                logger.error(f"Erro ao retornar conexão: {e}")
                conn.close()
                self.active_connections = max(0, self.active_connections - 1)
    
    def _is_connection_valid(self, conn: sqlite3.Connection) -> bool:
        """Verifica se conexão ainda é válida"""
        try:
            conn.execute("SELECT 1")
            return True
        except:
            return False
    
    def _health_check_loop(self):
        """Loop de health check em background"""
        while True:
            try:
                time.sleep(self.health_check_interval)
                self._perform_health_check()
            except Exception as e:
                logger.error(f"Erro no health check: {e}")
    
    def _perform_health_check(self):
        """Executa health check no pool"""
        # Verifica conexões no pool
        valid_connections = []
        while not self.connection_pool.empty():
            try:
                conn = self.connection_pool.get_nowait()
                if self._is_connection_valid(conn):
                    valid_connections.append(conn)
                else:
                    conn.close()
            except queue.Empty:
                break
        
        # Retorna conexões válidas ao pool
        for conn in valid_connections:
            self.connection_pool.put(conn)
        
        # Cria novas conexões se necessário
        while self.connection_pool.qsize() < self.min_connections:
            conn = self._create_connection()
            if conn:
                self.connection_pool.put(conn)
        
        logger.info(f"Health check: {self.connection_pool.qsize()}/{self.max_connections} conexões válidas")
    
    def get_stats(self) -> ConnectionPoolStats:
        """Retorna estatísticas do pool"""
        avg_wait_time = statistics.mean(self.wait_times) if self.wait_times else 0
        max_wait_time = max(self.wait_times) if self.wait_times else 0
        
        total_requests = len(self.wait_times)
        successful_requests = total_requests - self.connection_errors
        pool_hit_ratio = (successful_requests / total_requests) if total_requests > 0 else 0
        
        return ConnectionPoolStats(
            total_connections=self.max_connections,
            active_connections=self.active_connections,
            idle_connections=self.connection_pool.qsize(),
            max_wait_time=max_wait_time,
            avg_wait_time=avg_wait_time,
            connection_errors=self.connection_errors,
            pool_hit_ratio=pool_hit_ratio
        )


class QueryCache:
    """Cache de queries para otimizar consultas repetitivas"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl  # Time to live em segundos
        self.cache: Dict[str, Tuple[Any, datetime]] = {}
        self.access_count: Dict[str, int] = {}
        self.lock = threading.Lock()
    
    def _generate_key(self, query: str, params: tuple = None) -> str:
        """Gera chave única para query"""
        key_data = f"{query}:{hash(params) if params else 'None'}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, query: str, params: tuple = None) -> Optional[Any]:
        """Obtém resultado do cache"""
        key = self._generate_key(query, params)
        
        with self.lock:
            if key in self.cache:
                result, timestamp = self.cache[key]
                
                # Verifica TTL
                if (datetime.now() - timestamp).total_seconds() < self.ttl:
                    self.access_count[key] = self.access_count.get(key, 0) + 1
                    return result
                else:
                    # Remove item expirado
                    del self.cache[key]
                    if key in self.access_count:
                        del self.access_count[key]
        
        return None
    
    def set(self, query: str, params: tuple, result: Any):
        """Armazena resultado no cache"""
        key = self._generate_key(query, params)
        
        with self.lock:
            # Remove item menos acessado se cache está cheio
            if len(self.cache) >= self.max_size:
                self._evict_least_used()
            
            self.cache[key] = (result, datetime.now())
            self.access_count[key] = 0
    
    def _evict_least_used(self):
        """Remove item menos acessado do cache"""
        if not self.access_count:
            # Remove item mais antigo se não há contadores
            oldest_key = min(self.cache.keys(), key=lambda key: self.cache[key][1])
            del self.cache[oldest_key]
        else:
            # Remove item com menor contador de acesso
            least_used_key = min(self.access_count.keys(), key=lambda key: self.access_count[key])
            del self.cache[least_used_key]
            del self.access_count[least_used_key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        with self.lock:
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hit_ratio': self._calculate_hit_ratio(),
                'avg_access_count': statistics.mean(self.access_count.values()) if self.access_count else 0
            }
    
    def _calculate_hit_ratio(self) -> float:
        """Calcula hit ratio do cache"""
        total_accesses = sum(self.access_count.values())
        cache_hits = len(self.cache)
        return (cache_hits / (total_accesses + cache_hits)) if (total_accesses + cache_hits) > 0 else 0


class DatabaseBackup:
    """Sistema de backup automático"""
    
    def __init__(self, db_path: str, backup_dir: str = "backups"):
        self.db_path = db_path
        self.backup_dir = backup_dir
        self.backup_retention_days = 30
        self.backup_interval_hours = 24
        
        # Cria diretório de backup se não existir
        os.makedirs(self.backup_dir, exist_ok=True)
        
        logger.info(f"Database Backup inicializado: {backup_dir}")
    
    def create_backup(self) -> str:
        """Cria backup do database"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"db_backup_{timestamp}.sqlite3"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        try:
            # Cria backup usando WAL mode para consistência
            with sqlite3.connect(self.db_path) as source_conn:
                source_conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                
                with sqlite3.connect(backup_path) as backup_conn:
                    source_conn.backup(backup_conn)
            
            logger.info(f"Backup criado: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
            raise
    
    def cleanup_old_backups(self):
        """Remove backups antigos"""
        cutoff_date = datetime.now() - timedelta(days=self.backup_retention_days)
        
        for filename in os.listdir(self.backup_dir):
            if filename.startswith("db_backup_") and filename.endswith(".sqlite3"):
                file_path = os.path.join(self.backup_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                
                if file_time < cutoff_date:
                    try:
                        os.remove(file_path)
                        logger.info(f"Backup removido: {filename}")
                    except Exception as e:
                        logger.error(f"Erro ao remover backup {filename}: {e}")
    
    def restore_backup(self, backup_path: str) -> bool:
        """Restaura database a partir de backup"""
        try:
            # Cria backup do database atual antes de restaurar
            current_backup = self.create_backup()
            
            # Restaura backup
            with sqlite3.connect(backup_path) as backup_conn:
                with sqlite3.connect(self.db_path) as target_conn:
                    backup_conn.backup(target_conn)
            
            logger.info(f"Database restaurado de: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao restaurar backup: {e}")
            return False


class DatabaseOptimizer:
    """Otimizador de database principal"""
    
    def __init__(self, db_path: str, max_connections: int = 20):
        self.db_path = db_path
        self.connection_pool = AdvancedConnectionPool(db_path, max_connections)
        self.query_cache = QueryCache()
        self.backup_system = DatabaseBackup(db_path)
        self.query_metrics: List[QueryMetrics] = []
        self.slow_query_threshold = 1.0  # 1 segundo
        self.optimization_enabled = True
        
        # Inicializa tabelas de monitoramento
        self._create_monitoring_tables()
        
        # Inicia backup automático
        self._start_auto_backup()
        
        logger.info(f"Database Optimizer v2.0 inicializado para {db_path}")
    
    def _create_monitoring_tables(self):
        """Cria tabelas para monitoramento de performance"""
        conn = self.connection_pool.get_connection()
        if not conn:
            return
        
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS query_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    query_type TEXT NOT NULL,
                    execution_time REAL NOT NULL,
                    rows_affected INTEGER NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    explain_plan TEXT,
                    index_usage TEXT,
                    table_scans INTEGER DEFAULT 0,
                    index_scans INTEGER DEFAULT 0
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS index_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_name TEXT NOT NULL,
                    column_name TEXT NOT NULL,
                    index_type TEXT NOT NULL,
                    expected_improvement REAL NOT NULL,
                    creation_cost REAL NOT NULL,
                    priority INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    applied_at DATETIME,
                    status TEXT DEFAULT 'pending'
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    avg_query_time REAL,
                    slow_query_count INTEGER,
                    cache_hit_ratio REAL,
                    connection_pool_stats TEXT,
                    backup_status TEXT
                )
            """)
            
            # Índices para otimizar consultas de monitoramento
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_query_metrics_timestamp 
                ON query_metrics(timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_query_metrics_execution_time 
                ON query_metrics(execution_time)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_performance_stats_timestamp 
                ON performance_stats(timestamp)
            """)
            
            conn.commit()
            
        finally:
            self.connection_pool.return_connection(conn)
    
    def _start_auto_backup(self):
        """Inicia backup automático em background"""
        def backup_loop():
            while True:
                try:
                    time.sleep(24 * 3600)  # 24 horas
                    self.backup_system.create_backup()
                    self.backup_system.cleanup_old_backups()
                except Exception as e:
                    logger.error(f"Erro no backup automático: {e}")
        
        backup_thread = threading.Thread(target=backup_loop, daemon=True)
        backup_thread.start()
        logger.info("Backup automático iniciado")
    
    def execute_query(self, query: str, params: tuple = None, use_cache: bool = True) -> Tuple[Any, float]:
        """Executa query com monitoramento de performance e cache"""
        start_time = time.time()
        
        # Verifica cache para queries SELECT
        if use_cache and query.strip().upper().startswith('SELECT'):
            cached_result = self.query_cache.get(query, params)
            if cached_result is not None:
                execution_time = time.time() - start_time
                logger.info(f"Cache hit para query: {execution_time:.4f}string_data")
                return cached_result, execution_time
        
        conn = self.connection_pool.get_connection()
        if not conn:
            raise Exception("Não foi possível obter conexão do pool")
        
        try:
            # Executa query
            if params:
                cursor = conn.execute(query, params)
            else:
                cursor = conn.execute(query)
            
            # Obtém resultados
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                rows_affected = len(results)
                
                # Armazena no cache
                if use_cache:
                    self.query_cache.set(query, params, results)
            else:
                conn.commit()
                rows_affected = cursor.rowcount
                results = None
            
            execution_time = time.time() - start_time
            
            # Analisa performance
            self._analyze_query_performance(query, execution_time, rows_affected)
            
            return results, execution_time
            
        finally:
            self.connection_pool.return_connection(conn)
    
    def _analyze_query_performance(self, query: str, execution_time: float, rows_affected: int):
        """Analisa performance da query"""
        if not self.optimization_enabled:
            return
        
        # Determina tipo da query
        query_type = self._get_query_type(query)
        
        # Cria métricas
        metrics = QueryMetrics(
            query=query,
            query_type=query_type,
            execution_time=execution_time,
            rows_affected=rows_affected,
            timestamp=datetime.now()
        )
        
        # Salva métricas
        self._save_query_metrics(metrics)
        
        # Analisa queries lentas
        if execution_time > self.slow_query_threshold:
            self._analyze_slow_query(metrics)
    
    def _get_query_type(self, query: str) -> QueryType:
        """Determina tipo da query"""
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
        else:
            return QueryType.SELECT  # Default
    
    def _save_query_metrics(self, metrics: QueryMetrics):
        """Salva métricas da query"""
        conn = self.connection_pool.get_connection()
        if not conn:
            return
        
        try:
            conn.execute("""
                INSERT INTO query_metrics 
                (query, query_type, execution_time, rows_affected, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                metrics.query,
                metrics.query_type.value,
                metrics.execution_time,
                metrics.rows_affected,
                metrics.timestamp
            ))
            conn.commit()
        finally:
            self.connection_pool.return_connection(conn)
    
    def _analyze_slow_query(self, metrics: QueryMetrics):
        """Analisa query lenta e gera recomendações"""
        logger.warning(f"Query lenta detectada: {metrics.execution_time:.4f}string_data - {metrics.query[:100]}...")
        
        # Analisa plano de execução
        conn = self.connection_pool.get_connection()
        if not conn:
            return
        
        try:
            # Obtém EXPLAIN PLAN
            explain_result = conn.execute(f"EXPLAIN QUERY PLAN {metrics.query}").fetchall()
            explain_plan = json.dumps([dict(row) for row in explain_result])
            
            # Analisa uso de índices
            index_analysis = self._analyze_index_usage(explain_result)
            
            # Gera recomendações de índice
            recommendations = self._generate_index_recommendations(metrics, index_analysis)
            
            # Salva recomendações
            for rec in recommendations:
                self._save_index_recommendation(rec)
                
        finally:
            self.connection_pool.return_connection(conn)
    
    def _analyze_index_usage(self, explain_plan: List) -> Dict[str, Any]:
        """Analisa uso de índices no plano de execução"""
        table_scans = 0
        index_scans = 0
        used_indexes = []
        
        for row in explain_plan:
            detail = row['detail'] if hasattr(row, 'detail') else str(row)
            
            if 'SCAN TABLE' in detail:
                table_scans += 1
                table_name = self._extract_table_name(detail)
                if table_name:
                    used_indexes.append(f"TABLE_SCAN:{table_name}")
            
            elif 'USING INDEX' in detail:
                index_scans += 1
                index_name = self._extract_index_name(detail)
                if index_name:
                    used_indexes.append(f"INDEX:{index_name}")
        
        return {
            'table_scans': table_scans,
            'index_scans': index_scans,
            'used_indexes': used_indexes
        }
    
    def _extract_table_name(self, detail: str) -> Optional[str]:
        """Extrai nome da tabela do detalhe do EXPLAIN"""
        if 'SCAN TABLE' in detail:
            parts = detail.split()
            for index, part in enumerate(parts):
                if part == 'TABLE':
                    return parts[index + 1] if index + 1 < len(parts) else None
        return None
    
    def _extract_index_name(self, detail: str) -> Optional[str]:
        """Extrai nome do índice do detalhe do EXPLAIN"""
        if 'USING INDEX' in detail:
            parts = detail.split()
            for index, part in enumerate(parts):
                if part == 'INDEX':
                    return parts[index + 1] if index + 1 < len(parts) else None
        return None
    
    def _generate_index_recommendations(self, metrics: QueryMetrics, 
                                      index_analysis: Dict[str, Any]) -> List[IndexRecommendation]:
        """Gera recomendações de índice baseadas na análise"""
        recommendations = []
        
        # Se há table scans, recomenda índices
        if index_analysis['table_scans'] > 0:
            # Extrai colunas da query SELECT
            if metrics.query_type == QueryType.SELECT:
                columns = self._extract_select_columns(metrics.query)
                table_name = self._extract_table_name_from_query(metrics.query)
                
                for column in columns:
                    if column and table_name:
                        priority = self._calculate_priority(metrics.execution_time, column)
                        recommendation = IndexRecommendation(
                            table_name=table_name,
                            column_name=column,
                            index_type='BTREE',
                            expected_improvement=metrics.execution_time * 0.8,  # 80% de melhoria esperada
                            creation_cost=0.1,  # Custo baixo para SQLite
                            priority=priority
                        )
                        recommendations.append(recommendation)
        
        return recommendations
    
    def _extract_select_columns(self, query: str) -> List[str]:
        """Extrai colunas da query SELECT"""
        try:
            # Simplifica análise - busca por padrões comuns
            query_upper = query.upper()
            
            # Remove subqueries para simplificar
            if 'SELECT' in query_upper and 'FROM' in query_upper:
                select_part = query_upper.split('FROM')[0]
                select_part = select_part.replace('SELECT', '').strip()
                
                # Divide por vírgulas
                columns = []
                for col in select_part.split(','):
                    col = col.strip()
                    # Remove aliases (AS)
                    if ' AS ' in col:
                        col = col.split(' AS ')[0].strip()
                    # Remove funções
                    if '(' in col and ')' in col:
                        continue
                    # Remove espaços extras
                    col = col.strip()
                    if col and col != '*':
                        columns.append(col)
                
                return columns
        except:
            pass
        
        return []
    
    def _extract_table_name_from_query(self, query: str) -> str:
        """Extrai nome da tabela da query"""
        try:
            query_upper = query.upper()
            if 'FROM' in query_upper:
                from_part = query_upper.split('FROM')[1]
                # Remove WHERE, ORDER BY, etc.
                for clause in ['WHERE', 'ORDER BY', 'GROUP BY', 'LIMIT', 'JOIN']:
                    if clause in from_part:
                        from_part = from_part.split(clause)[0]
                
                table_name = from_part.strip()
                # Remove aliases
                if ' AS ' in table_name:
                    table_name = table_name.split(' AS ')[0].strip()
                
                return table_name
        except:
            pass
        
        return ""
    
    def _calculate_priority(self, execution_time: float, column: str) -> int:
        """Calcula prioridade da recomendação de índice"""
        # Base: tempo de execução
        base_priority = min(10, int(execution_time * 5))
        
        # Ajusta baseado na coluna
        if column.lower() in ['id', 'created_at', 'updated_at']:
            base_priority += 2
        elif column.lower() in ['status', 'type', 'category']:
            base_priority += 1
        
        return min(10, base_priority)
    
    def _save_index_recommendation(self, recommendation: IndexRecommendation):
        """Salva recomendação de índice"""
        conn = self.connection_pool.get_connection()
        if not conn:
            return
        
        try:
            conn.execute("""
                INSERT INTO index_recommendations 
                (table_name, column_name, index_type, expected_improvement, creation_cost, priority)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                recommendation.table_name,
                recommendation.column_name,
                recommendation.index_type,
                recommendation.expected_improvement,
                recommendation.creation_cost,
                recommendation.priority
            ))
            conn.commit()
        finally:
            self.connection_pool.return_connection(conn)
    
    def get_slow_queries(self, limit: int = 10) -> List[QueryMetrics]:
        """Retorna queries lentas"""
        conn = self.connection_pool.get_connection()
        if not conn:
            return []
        
        try:
            rows = conn.execute("""
                SELECT * FROM query_metrics 
                WHERE execution_time > ? 
                ORDER BY execution_time DESC 
                LIMIT ?
            """, (self.slow_query_threshold, limit)).fetchall()
            
            return [self._row_to_metrics(row) for row in rows]
        finally:
            self.connection_pool.return_connection(conn)
    
    def _row_to_metrics(self, row) -> QueryMetrics:
        """Converte row para QueryMetrics"""
        return QueryMetrics(
            query=row['query'],
            query_type=QueryType(row['query_type']),
            execution_time=row['execution_time'],
            rows_affected=row['rows_affected'],
            timestamp=datetime.fromisoformat(row['timestamp']),
            explain_plan=row.get('explain_plan'),
            index_usage=row.get('index_usage'),
            table_scans=row.get('table_scans', 0),
            index_scans=row.get('index_scans', 0)
        )
    
    def get_index_recommendations(self, limit: int = 10) -> List[IndexRecommendation]:
        """Retorna recomendações de índice"""
        conn = self.connection_pool.get_connection()
        if not conn:
            return []
        
        try:
            rows = conn.execute("""
                SELECT * FROM index_recommendations 
                WHERE status = 'pending'
                ORDER BY priority DESC, expected_improvement DESC 
                LIMIT ?
            """, (limit,)).fetchall()
            
            return [self._row_to_recommendation(row) for row in rows]
        finally:
            self.connection_pool.return_connection(conn)
    
    def _row_to_recommendation(self, row) -> IndexRecommendation:
        """Converte row para IndexRecommendation"""
        return IndexRecommendation(
            table_name=row['table_name'],
            column_name=row['column_name'],
            index_type=row['index_type'],
            expected_improvement=row['expected_improvement'],
            creation_cost=row['creation_cost'],
            priority=row['priority']
        )
    
    def apply_index_recommendation(self, recommendation_id: int) -> bool:
        """Aplica recomendação de índice"""
        conn = self.connection_pool.get_connection()
        if not conn:
            return False
        
        try:
            # Obtém recomendação
            row = conn.execute("""
                SELECT * FROM index_recommendations WHERE id = ?
            """, (recommendation_id,)).fetchone()
            
            if not row:
                return False
            
            # Cria índice
            index_name = f"idx_{row['table_name']}_{row['column_name']}"
            create_index_sql = f"""
                CREATE INDEX IF NOT EXISTS {index_name} 
                ON {row['table_name']}({row['column_name']})
            """
            
            conn.execute(create_index_sql)
            conn.commit()
            
            # Marca como aplicada
            conn.execute("""
                UPDATE index_recommendations 
                SET status = 'applied', applied_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (recommendation_id,))
            conn.commit()
            
            logger.info(f"Índice aplicado: {index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao aplicar índice: {e}")
            return False
        finally:
            self.connection_pool.return_connection(conn)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de performance"""
        conn = self.connection_pool.get_connection()
        if not conn:
            return {}
        
        try:
            # Estatísticas de queries
            query_stats = conn.execute("""
                SELECT 
                    COUNT(*) as total_queries,
                    AVG(execution_time) as avg_execution_time,
                    MAX(execution_time) as max_execution_time,
                    COUNT(CASE WHEN execution_time > ? THEN 1 END) as slow_queries
                FROM query_metrics 
                WHERE timestamp > datetime('now', '-24 hours')
            """, (self.slow_query_threshold,)).fetchone()
            
            # Estatísticas de cache
            cache_stats = self.query_cache.get_stats()
            
            # Estatísticas do connection pool
            pool_stats = self.connection_pool.get_stats()
            
            # Estatísticas de índices
            index_stats = conn.execute("""
                SELECT 
                    COUNT(*) as total_recommendations,
                    COUNT(CASE WHEN status = 'applied' THEN 1 END) as applied_recommendations,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_recommendations
                FROM index_recommendations
            """).fetchone()
            
            return {
                'query_stats': {
                    'total_queries': query_stats['total_queries'],
                    'avg_execution_time': query_stats['avg_execution_time'],
                    'max_execution_time': query_stats['max_execution_time'],
                    'slow_queries': query_stats['slow_queries']
                },
                'cache_stats': cache_stats,
                'pool_stats': {
                    'total_connections': pool_stats.total_connections,
                    'active_connections': pool_stats.active_connections,
                    'idle_connections': pool_stats.idle_connections,
                    'pool_hit_ratio': pool_stats.pool_hit_ratio,
                    'avg_wait_time': pool_stats.avg_wait_time
                },
                'index_stats': {
                    'total_recommendations': index_stats['total_recommendations'],
                    'applied_recommendations': index_stats['applied_recommendations'],
                    'pending_recommendations': index_stats['pending_recommendations']
                }
            }
        finally:
            self.connection_pool.return_connection(conn)
    
    def optimize_database(self) -> Dict[str, Any]:
        """Executa otimização completa do database"""
        logger.info("Iniciando otimização completa do database...")
        
        optimization_results = {
            'timestamp': datetime.now().isoformat(),
            'slow_queries_analyzed': 0,
            'indexes_created': 0,
            'cache_optimized': False,
            'backup_created': False,
            'performance_improvement': 0.0
        }
        
        try:
            # 1. Analisa queries lentas
            slow_queries = self.get_slow_queries(limit=20)
            optimization_results['slow_queries_analyzed'] = len(slow_queries)
            
            # 2. Aplica recomendações de índice de alta prioridade
            recommendations = self.get_index_recommendations(limit=10)
            high_priority_recs = [r for r in recommendations if r.priority >= 8]
            
            for rec in high_priority_recs:
                if self.apply_index_recommendation(rec.id):
                    optimization_results['indexes_created'] += 1
            
            # 3. Otimiza cache
            cache_stats = self.query_cache.get_stats()
            if cache_stats['hit_ratio'] < 0.7:  # Hit ratio baixo
                # Ajusta TTL e tamanho do cache
                self.query_cache.ttl = min(7200, self.query_cache.ttl * 1.5)  # Aumenta TTL
                self.query_cache.max_size = min(2000, self.query_cache.max_size * 1.2)  # Aumenta tamanho
                optimization_results['cache_optimized'] = True
            
            # 4. Cria backup
            try:
                backup_path = self.backup_system.create_backup()
                optimization_results['backup_created'] = True
                logger.info(f"Backup criado: {backup_path}")
            except Exception as e:
                logger.error(f"Erro ao criar backup: {e}")
            
            # 5. Calcula melhoria de performance
            before_stats = self.get_performance_stats()
            optimization_results['performance_improvement'] = before_stats.get('query_stats', {}).get('avg_execution_time', 0)
            
            logger.info(f"Otimização concluída: {optimization_results}")
            return optimization_results
            
        except Exception as e:
            logger.error(f"Erro durante otimização: {e}")
            return optimization_results


class DatabaseMonitor:
    """Monitor de database em tempo real"""
    
    def __init__(self, optimizer: DatabaseOptimizer):
        self.optimizer = optimizer
        self.monitoring_active = False
        self.monitor_thread = None
        self.alert_thresholds = {
            'slow_query_threshold': 2.0,  # 2 segundos
            'cache_hit_ratio_threshold': 0.5,  # 50%
            'pool_hit_ratio_threshold': 0.8,  # 80%
            'connection_error_threshold': 10  # 10 erros por hora
        }
    
    def start_monitoring(self):
        """Inicia monitoramento"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Database monitoring iniciado")
    
    def stop_monitoring(self):
        """Para monitoramento"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("Database monitoring parado")
    
    def _monitor_loop(self):
        """Loop principal de monitoramento"""
        while self.monitoring_active:
            try:
                # Coleta estatísticas
                stats = self.optimizer.get_performance_stats()
                
                # Verifica alertas
                self._check_alerts(stats)
                
                # Salva estatísticas
                self._save_performance_stats(stats)
                
                # Aguarda próximo ciclo
                time.sleep(60)  # 1 minuto
                
            except Exception as e:
                logger.error(f"Erro no monitoramento: {e}")
                time.sleep(60)
    
    def _check_alerts(self, stats: Dict[str, Any]):
        """Verifica e gera alertas"""
        query_stats = stats.get('query_stats', {})
        cache_stats = stats.get('cache_stats', {})
        pool_stats = stats.get('pool_stats', {})
        
        # Alerta para queries lentas
        if query_stats.get('avg_execution_time', 0) > self.alert_thresholds['slow_query_threshold']:
            logger.warning(f"ALERTA: Queries lentas detectadas - {query_stats['avg_execution_time']:.2f}string_data")
        
        # Alerta para cache hit ratio baixo
        if cache_stats.get('hit_ratio', 1) < self.alert_thresholds['cache_hit_ratio_threshold']:
            logger.warning(f"ALERTA: Cache hit ratio baixo - {cache_stats['hit_ratio']:.2%}")
        
        # Alerta para pool hit ratio baixo
        if pool_stats.get('pool_hit_ratio', 1) < self.alert_thresholds['pool_hit_ratio_threshold']:
            logger.warning(f"ALERTA: Pool hit ratio baixo - {pool_stats['pool_hit_ratio']:.2%}")
    
    def _save_performance_stats(self, stats: Dict[str, Any]):
        """Salva estatísticas de performance"""
        conn = self.optimizer.connection_pool.get_connection()
        if not conn:
            return
        
        try:
            conn.execute("""
                INSERT INTO performance_stats 
                (avg_query_time, slow_query_count, cache_hit_ratio, connection_pool_stats, backup_status)
                VALUES (?, ?, ?, ?, ?)
            """, (
                stats.get('query_stats', {}).get('avg_execution_time', 0),
                stats.get('query_stats', {}).get('slow_queries', 0),
                stats.get('cache_stats', {}).get('hit_ratio', 0),
                json.dumps(stats.get('pool_stats', {})),
                'active'  # Status do backup
            ))
            conn.commit()
        finally:
            self.optimizer.connection_pool.return_connection(conn)


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Optimizer - Omni Keywords Finder')
    parser.add_argument('--db-path', default='backend/db.sqlite3', help='Caminho do database')
    parser.add_argument('--max-connections', type=int, default=20, help='Máximo de conexões')
    parser.add_argument('--optimize', action='store_true', help='Executa otimização completa')
    parser.add_argument('--monitor', action='store_true', help='Inicia monitoramento')
    parser.add_argument('--backup', action='store_true', help='Cria backup')
    parser.add_argument('--stats', action='store_true', help='Mostra estatísticas')
    
    args = parser.parse_args()
    
    # Inicializa otimizador
    optimizer = DatabaseOptimizer(args.db_path, args.max_connections)
    
    if args.optimize:
        results = optimizer.optimize_database()
        print(f"Otimização concluída: {results}")
    
    if args.monitor:
        monitor = DatabaseMonitor(optimizer)
        monitor.start_monitoring()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            monitor.stop_monitoring()
    
    if args.backup:
        backup_path = optimizer.backup_system.create_backup()
        print(f"Backup criado: {backup_path}")
    
    if args.stats:
        stats = optimizer.get_performance_stats()
        print(json.dumps(stats, indent=2, default=str))


if __name__ == "__main__":
    main() 