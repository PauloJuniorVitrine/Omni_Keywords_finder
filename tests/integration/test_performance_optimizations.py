"""
⚡ Testes de Performance e Otimizações

Tracing ID: performance-tests-2025-01-27-001
Timestamp: 2025-01-27T19:30:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Testes baseados em cenários reais de performance
🌲 ToT: Avaliadas múltiplas estratégias de otimização
♻️ ReAct: Simulado cenários de carga e validada performance

Testa otimizações de performance incluindo:
- Connection pooling
- Async/await patterns
- Batch processing
- Lazy loading
- Caching strategies
- Compression
- Query optimization
- Memory management
- CPU optimization
- Network optimization
"""

import asyncio
import time
import psutil
import gc
import tracemalloc
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import statistics
import json
import logging
from datetime import datetime, timedelta
import pytest
import pytest_asyncio
from unittest.mock import Mock, patch, AsyncMock

# Configuração de logging
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Métricas de performance"""
    operation_name: str
    execution_time: float
    memory_usage: int
    cpu_usage: float
    throughput: float
    latency: float
    error_count: int
    success_count: int
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'operation_name': self.operation_name,
            'execution_time_ms': self.execution_time * 1000,
            'memory_usage_mb': self.memory_usage / (1024 * 1024),
            'cpu_usage_percent': self.cpu_usage,
            'throughput_ops_per_sec': self.throughput,
            'latency_ms': self.latency * 1000,
            'error_count': self.error_count,
            'success_count': self.success_count,
            'timestamp': self.timestamp.isoformat()
        }

class PerformanceMonitor:
    """Monitor de performance"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.start_time: Optional[float] = None
        self.start_memory: Optional[int] = None
        self.start_cpu: Optional[float] = None
        
    def start_monitoring(self):
        """Inicia monitoramento"""
        self.start_time = time.time()
        self.start_memory = psutil.Process().memory_info().rss
        self.start_cpu = psutil.cpu_percent()
        
    def stop_monitoring(self, operation_name: str, success_count: int = 1, error_count: int = 0) -> PerformanceMetrics:
        """Para monitoramento e retorna métricas"""
        if self.start_time is None:
            raise ValueError("Monitoramento não foi iniciado")
            
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        end_cpu = psutil.cpu_percent()
        
        execution_time = end_time - self.start_time
        memory_usage = end_memory - (self.start_memory or 0)
        cpu_usage = (end_cpu + (self.start_cpu or 0)) / 2
        throughput = success_count / execution_time if execution_time > 0 else 0
        latency = execution_time / success_count if success_count > 0 else 0
        
        metrics = PerformanceMetrics(
            operation_name=operation_name,
            execution_time=execution_time,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            throughput=throughput,
            latency=latency,
            error_count=error_count,
            success_count=success_count,
            timestamp=datetime.now()
        )
        
        self.metrics.append(metrics)
        return metrics
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo das métricas"""
        if not self.metrics:
            return {}
            
        execution_times = [m.execution_time for m in self.metrics]
        memory_usages = [m.memory_usage for m in self.metrics]
        cpu_usages = [m.cpu_usage for m in self.metrics]
        throughputs = [m.throughput for m in self.metrics]
        latencies = [m.latency for m in self.metrics]
        
        return {
            'total_operations': len(self.metrics),
            'total_execution_time_ms': sum(execution_times) * 1000,
            'average_execution_time_ms': statistics.mean(execution_times) * 1000,
            'min_execution_time_ms': min(execution_times) * 1000,
            'max_execution_time_ms': max(execution_times) * 1000,
            'p95_execution_time_ms': statistics.quantiles(execution_times, n=20)[18] * 1000 if len(execution_times) >= 20 else 0,
            'p99_execution_time_ms': statistics.quantiles(execution_times, n=100)[98] * 1000 if len(execution_times) >= 100 else 0,
            'total_memory_usage_mb': sum(memory_usages) / (1024 * 1024),
            'average_memory_usage_mb': statistics.mean(memory_usages) / (1024 * 1024),
            'total_cpu_usage_percent': sum(cpu_usages),
            'average_cpu_usage_percent': statistics.mean(cpu_usages),
            'total_throughput_ops_per_sec': sum(throughputs),
            'average_throughput_ops_per_sec': statistics.mean(throughputs),
            'total_latency_ms': sum(latencies) * 1000,
            'average_latency_ms': statistics.mean(latencies) * 1000,
            'total_errors': sum(m.error_count for m in self.metrics),
            'total_successes': sum(m.success_count for m in self.metrics),
            'error_rate': sum(m.error_count for m in self.metrics) / sum(m.success_count + m.error_count for m in self.metrics) if sum(m.success_count + m.error_count for m in self.metrics) > 0 else 0
        }

class ConnectionPool:
    """Pool de conexões para teste"""
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.connections: List[Any] = []
        self.in_use: List[Any] = []
        self._lock = asyncio.Lock()
        
    async def get_connection(self) -> Any:
        """Obtém conexão do pool"""
        async with self._lock:
            if self.connections:
                conn = self.connections.pop()
                self.in_use.append(conn)
                return conn
            elif len(self.in_use) < self.max_connections:
                conn = Mock()
                conn.id = len(self.in_use)
                self.in_use.append(conn)
                return conn
            else:
                # Aguardar conexão disponível
                while not self.connections:
                    await asyncio.sleep(0.001)
                conn = self.connections.pop()
                self.in_use.append(conn)
                return conn
    
    async def release_connection(self, conn: Any):
        """Libera conexão para o pool"""
        async with self._lock:
            if conn in self.in_use:
                self.in_use.remove(conn)
                self.connections.append(conn)

class BatchProcessor:
    """Processador em lote"""
    
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
        self.batch: List[Any] = []
        self._lock = asyncio.Lock()
        
    async def add_item(self, item: Any) -> bool:
        """Adiciona item ao lote"""
        async with self._lock:
            self.batch.append(item)
            return len(self.batch) >= self.batch_size
    
    async def process_batch(self) -> List[Any]:
        """Processa lote atual"""
        async with self._lock:
            if not self.batch:
                return []
            
            batch = self.batch.copy()
            self.batch.clear()
            return batch
    
    async def get_batch_size(self) -> int:
        """Retorna tamanho do lote atual"""
        async with self._lock:
            return len(self.batch)

class LazyLoader:
    """Carregador lazy"""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._loading: Dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()
        
    async def get(self, key: str, loader_func: callable) -> Any:
        """Obtém valor com carregamento lazy"""
        # Verificar cache
        if key in self._cache:
            return self._cache[key]
        
        # Verificar se já está carregando
        if key in self._loading:
            return await self._loading[key]
        
        # Iniciar carregamento
        async with self._lock:
            if key in self._cache:
                return self._cache[key]
            if key in self._loading:
                return await self._loading[key]
            
            task = asyncio.create_task(self._load_and_cache(key, loader_func))
            self._loading[key] = task
            
        return await task
    
    async def _load_and_cache(self, key: str, loader_func: callable):
        """Carrega e cacheia valor"""
        try:
            value = await loader_func()
            self._cache[key] = value
            return value
        finally:
            async with self._lock:
                if key in self._loading:
                    del self._loading[key]

class QueryOptimizer:
    """Otimizador de queries"""
    
    def __init__(self):
        self.query_cache: Dict[str, Any] = {}
        self.query_stats: Dict[str, Dict[str, Any]] = {}
        
    def optimize_query(self, query: str, params: Dict[str, Any] = None) -> str:
        """Otimiza query"""
        # Simular otimização
        optimized = query.strip()
        
        # Cache de query
        cache_key = f"{optimized}:{hash(str(params))}"
        if cache_key in self.query_cache:
            return self.query_cache[cache_key]
        
        # Aplicar otimizações
        if "SELECT *" in optimized:
            optimized = optimized.replace("SELECT *", "SELECT id, name, created_at")
        
        if "ORDER BY" not in optimized and "LIMIT" not in optimized:
            optimized += " ORDER BY created_at DESC LIMIT 100"
        
        self.query_cache[cache_key] = optimized
        return optimized
    
    def get_query_stats(self, query: str) -> Dict[str, Any]:
        """Obtém estatísticas da query"""
        if query not in self.query_stats:
            self.query_stats[query] = {
                'execution_count': 0,
                'average_time': 0.0,
                'last_execution': None
            }
        return self.query_stats[query]

class CompressionOptimizer:
    """Otimizador de compressão"""
    
    def __init__(self):
        self.compression_stats: Dict[str, Dict[str, Any]] = {}
        
    def compress_data(self, data: bytes, algorithm: str = "gzip") -> Tuple[bytes, float]:
        """Comprime dados"""
        import gzip
        import lzma
        import bz2
        
        original_size = len(data)
        
        if algorithm == "gzip":
            compressed = gzip.compress(data)
        elif algorithm == "lzma":
            compressed = lzma.compress(data)
        elif algorithm == "bz2":
            compressed = bz2.compress(data)
        else:
            compressed = data
        
        compressed_size = len(compressed)
        compression_ratio = (original_size - compressed_size) / original_size
        
        # Atualizar estatísticas
        if algorithm not in self.compression_stats:
            self.compression_stats[algorithm] = {
                'total_original_size': 0,
                'total_compressed_size': 0,
                'compression_count': 0,
                'average_ratio': 0.0
            }
        
        stats = self.compression_stats[algorithm]
        stats['total_original_size'] += original_size
        stats['total_compressed_size'] += compressed_size
        stats['compression_count'] += 1
        stats['average_ratio'] = (stats['total_original_size'] - stats['total_compressed_size']) / stats['total_original_size']
        
        return compressed, compression_ratio
    
    def get_compression_stats(self) -> Dict[str, Dict[str, Any]]:
        """Obtém estatísticas de compressão"""
        return self.compression_stats

@pytest.fixture
def performance_monitor():
    """Fixture para monitor de performance"""
    return PerformanceMonitor()

@pytest.fixture
def connection_pool():
    """Fixture para pool de conexões"""
    return ConnectionPool(max_connections=10)

@pytest.fixture
def batch_processor():
    """Fixture para processador em lote"""
    return BatchProcessor(batch_size=100)

@pytest.fixture
def lazy_loader():
    """Fixture para carregador lazy"""
    return LazyLoader()

@pytest.fixture
def query_optimizer():
    """Fixture para otimizador de queries"""
    return QueryOptimizer()

@pytest.fixture
def compression_optimizer():
    """Fixture para otimizador de compressão"""
    return CompressionOptimizer()

class TestConnectionPooling:
    """Testes de connection pooling"""
    
    @pytest.mark.asyncio
    async def test_connection_pool_creation(self, connection_pool):
        """Testa criação de pool de conexões"""
        assert connection_pool.max_connections == 10
        assert len(connection_pool.connections) == 0
        assert len(connection_pool.in_use) == 0
    
    @pytest.mark.asyncio
    async def test_connection_acquire_release(self, connection_pool):
        """Testa aquisição e liberação de conexões"""
        # Adquirir conexões
        conn1 = await connection_pool.get_connection()
        conn2 = await connection_pool.get_connection()
        
        assert len(connection_pool.in_use) == 2
        assert len(connection_pool.connections) == 0
        
        # Liberar conexões
        await connection_pool.release_connection(conn1)
        await connection_pool.release_connection(conn2)
        
        assert len(connection_pool.in_use) == 0
        assert len(connection_pool.connections) == 2
    
    @pytest.mark.asyncio
    async def test_connection_pool_concurrent_access(self, connection_pool):
        """Testa acesso concorrente ao pool"""
        async def acquire_connection():
            conn = await connection_pool.get_connection()
            await asyncio.sleep(0.01)
            await connection_pool.release_connection(conn)
            return conn
        
        # Executar múltiplas aquisições concorrentes
        tasks = [acquire_connection() for _ in range(20)]
        connections = await asyncio.gather(*tasks)
        
        assert len(connections) == 20
        assert len(connection_pool.in_use) == 0
        assert len(connection_pool.connections) <= connection_pool.max_connections
    
    @pytest.mark.asyncio
    async def test_connection_pool_performance(self, connection_pool, performance_monitor):
        """Testa performance do pool de conexões"""
        performance_monitor.start_monitoring()
        
        async def connection_operation():
            conn = await connection_pool.get_connection()
            await asyncio.sleep(0.001)  # Simular operação
            await connection_pool.release_connection(conn)
        
        # Executar operações
        tasks = [connection_operation() for _ in range(100)]
        await asyncio.gather(*tasks)
        
        metrics = performance_monitor.stop_monitoring("connection_pool_operations", 100)
        
        assert metrics.execution_time < 1.0  # Deve ser rápido
        assert metrics.throughput > 50  # Pelo menos 50 ops/seg
        assert metrics.error_count == 0

class TestAsyncAwaitPatterns:
    """Testes de padrões async/await"""
    
    @pytest.mark.asyncio
    async def test_async_function_performance(self, performance_monitor):
        """Testa performance de funções async"""
        async def async_operation(delay: float):
            await asyncio.sleep(delay)
            return f"result_{delay}"
        
        performance_monitor.start_monitoring()
        
        # Executar operações sequenciais vs paralelas
        start_time = time.time()
        
        # Sequencial
        results_seq = []
        for i in range(10):
            result = await async_operation(0.01)
            results_seq.append(result)
        
        seq_time = time.time() - start_time
        
        # Paralelo
        start_time = time.time()
        tasks = [async_operation(0.01) for _ in range(10)]
        results_par = await asyncio.gather(*tasks)
        par_time = time.time() - start_time
        
        metrics = performance_monitor.stop_monitoring("async_parallel_vs_sequential", 20)
        
        # Paralelo deve ser mais rápido
        assert par_time < seq_time
        assert len(results_seq) == 10
        assert len(results_par) == 10
    
    @pytest.mark.asyncio
    async def test_async_generator_performance(self, performance_monitor):
        """Testa performance de generators async"""
        async def async_generator():
            for i in range(100):
                await asyncio.sleep(0.001)
                yield i
        
        performance_monitor.start_monitoring()
        
        results = []
        async for item in async_generator():
            results.append(item)
        
        metrics = performance_monitor.stop_monitoring("async_generator", 100)
        
        assert len(results) == 100
        assert metrics.execution_time < 0.5
        assert metrics.throughput > 100
    
    @pytest.mark.asyncio
    async def test_async_context_manager_performance(self, performance_monitor):
        """Testa performance de context managers async"""
        class AsyncContextManager:
            async def __aenter__(self):
                await asyncio.sleep(0.001)
                return self
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                await asyncio.sleep(0.001)
        
        performance_monitor.start_monitoring()
        
        for _ in range(50):
            async with AsyncContextManager():
                await asyncio.sleep(0.001)
        
        metrics = performance_monitor.stop_monitoring("async_context_manager", 50)
        
        assert metrics.execution_time < 0.3
        assert metrics.error_count == 0

class TestBatchProcessing:
    """Testes de processamento em lote"""
    
    @pytest.mark.asyncio
    async def test_batch_processor_creation(self, batch_processor):
        """Testa criação do processador em lote"""
        assert batch_processor.batch_size == 100
        assert len(batch_processor.batch) == 0
    
    @pytest.mark.asyncio
    async def test_batch_processing_operations(self, batch_processor):
        """Testa operações de processamento em lote"""
        # Adicionar itens
        for i in range(50):
            is_full = await batch_processor.add_item(f"item_{i}")
            assert not is_full
        
        # Adicionar mais itens até encher o lote
        for i in range(50, 100):
            is_full = await batch_processor.add_item(f"item_{i}")
            if i == 99:
                assert is_full
        
        # Processar lote
        batch = await batch_processor.process_batch()
        assert len(batch) == 100
        assert batch[0] == "item_0"
        assert batch[99] == "item_99"
        
        # Verificar se lote foi limpo
        batch_size = await batch_processor.get_batch_size()
        assert batch_size == 0
    
    @pytest.mark.asyncio
    async def test_batch_processing_performance(self, batch_processor, performance_monitor):
        """Testa performance do processamento em lote"""
        performance_monitor.start_monitoring()
        
        # Adicionar muitos itens
        for i in range(1000):
            await batch_processor.add_item(f"item_{i}")
        
        # Processar todos os lotes
        total_processed = 0
        while True:
            batch = await batch_processor.process_batch()
            if not batch:
                break
            total_processed += len(batch)
        
        metrics = performance_monitor.stop_monitoring("batch_processing", 1000)
        
        assert total_processed == 1000
        assert metrics.execution_time < 0.1
        assert metrics.throughput > 5000

class TestLazyLoading:
    """Testes de carregamento lazy"""
    
    @pytest.mark.asyncio
    async def test_lazy_loader_creation(self, lazy_loader):
        """Testa criação do carregador lazy"""
        assert len(lazy_loader._cache) == 0
        assert len(lazy_loader._loading) == 0
    
    @pytest.mark.asyncio
    async def test_lazy_loading_operations(self, lazy_loader):
        """Testa operações de carregamento lazy"""
        call_count = 0
        
        async def loader_func():
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)
            return f"loaded_data_{call_count}"
        
        # Primeira chamada - deve carregar
        result1 = await lazy_loader.get("key1", loader_func)
        assert result1 == "loaded_data_1"
        assert call_count == 1
        
        # Segunda chamada - deve usar cache
        result2 = await lazy_loader.get("key1", loader_func)
        assert result2 == "loaded_data_1"
        assert call_count == 1  # Não deve chamar novamente
        
        # Nova chave - deve carregar
        result3 = await lazy_loader.get("key2", loader_func)
        assert result3 == "loaded_data_2"
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_lazy_loading_concurrent_access(self, lazy_loader):
        """Testa acesso concorrente ao carregador lazy"""
        call_count = 0
        
        async def loader_func():
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)
            return f"loaded_data_{call_count}"
        
        # Múltiplas chamadas concorrentes para a mesma chave
        tasks = [lazy_loader.get("key1", loader_func) for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # Todas devem retornar o mesmo resultado
        assert all(r == results[0] for r in results)
        assert call_count == 1  # Deve carregar apenas uma vez
    
    @pytest.mark.asyncio
    async def test_lazy_loading_performance(self, lazy_loader, performance_monitor):
        """Testa performance do carregamento lazy"""
        async def loader_func():
            await asyncio.sleep(0.01)
            return "loaded_data"
        
        performance_monitor.start_monitoring()
        
        # Carregar múltiplas chaves
        for i in range(50):
            await lazy_loader.get(f"key_{i}", loader_func)
        
        metrics = performance_monitor.stop_monitoring("lazy_loading", 50)
        
        assert metrics.execution_time < 1.0
        assert metrics.error_count == 0

class TestCachingStrategies:
    """Testes de estratégias de cache"""
    
    @pytest.mark.asyncio
    async def test_cache_performance(self, performance_monitor):
        """Testa performance de cache"""
        cache = {}
        
        async def expensive_operation(key: str):
            await asyncio.sleep(0.01)  # Simular operação cara
            return f"result_{key}"
        
        async def cached_operation(key: str):
            if key in cache:
                return cache[key]
            
            result = await expensive_operation(key)
            cache[key] = result
            return result
        
        performance_monitor.start_monitoring()
        
        # Primeira execução - sem cache
        for i in range(20):
            await cached_operation(f"key_{i}")
        
        # Segunda execução - com cache
        for i in range(20):
            await cached_operation(f"key_{i}")
        
        metrics = performance_monitor.stop_monitoring("caching_strategy", 40)
        
        assert metrics.execution_time < 0.5
        assert len(cache) == 20
    
    @pytest.mark.asyncio
    async def test_cache_eviction_performance(self, performance_monitor):
        """Testa performance de evição de cache"""
        from collections import OrderedDict
        
        class LRUCache:
            def __init__(self, capacity: int):
                self.capacity = capacity
                self.cache = OrderedDict()
            
            async def get(self, key: str):
                if key in self.cache:
                    self.cache.move_to_end(key)
                    return self.cache[key]
                return None
            
            async def put(self, key: str, value: str):
                if key in self.cache:
                    self.cache.move_to_end(key)
                else:
                    if len(self.cache) >= self.capacity:
                        self.cache.popitem(last=False)
                self.cache[key] = value
        
        cache = LRUCache(capacity=10)
        
        performance_monitor.start_monitoring()
        
        # Adicionar mais itens que a capacidade
        for i in range(20):
            await cache.put(f"key_{i}", f"value_{i}")
        
        # Acessar itens
        for i in range(20):
            await cache.get(f"key_{i}")
        
        metrics = performance_monitor.stop_monitoring("cache_eviction", 40)
        
        assert len(cache.cache) == 10  # Deve manter apenas 10 itens
        assert metrics.execution_time < 0.1

class TestCompression:
    """Testes de compressão"""
    
    @pytest.mark.asyncio
    async def test_compression_optimizer_creation(self, compression_optimizer):
        """Testa criação do otimizador de compressão"""
        assert len(compression_optimizer.compression_stats) == 0
    
    @pytest.mark.asyncio
    async def test_compression_algorithms(self, compression_optimizer):
        """Testa diferentes algoritmos de compressão"""
        # Dados de teste
        test_data = b"Este é um texto de teste para compressão. " * 1000
        
        # Testar diferentes algoritmos
        algorithms = ["gzip", "lzma", "bz2"]
        
        for algorithm in algorithms:
            compressed, ratio = compression_optimizer.compress_data(test_data, algorithm)
            
            assert len(compressed) < len(test_data)
            assert ratio > 0.1  # Pelo menos 10% de compressão
            assert algorithm in compression_optimizer.compression_stats
    
    @pytest.mark.asyncio
    async def test_compression_performance(self, compression_optimizer, performance_monitor):
        """Testa performance da compressão"""
        # Dados de teste
        test_data = b"Este é um texto de teste para compressão. " * 1000
        
        performance_monitor.start_monitoring()
        
        # Comprimir múltiplas vezes
        for i in range(100):
            compressed, ratio = compression_optimizer.compress_data(test_data, "gzip")
        
        metrics = performance_monitor.stop_monitoring("compression_performance", 100)
        
        assert metrics.execution_time < 1.0
        assert metrics.throughput > 50
        
        # Verificar estatísticas
        stats = compression_optimizer.get_compression_stats()
        assert "gzip" in stats
        assert stats["gzip"]["compression_count"] == 100

class TestQueryOptimization:
    """Testes de otimização de queries"""
    
    @pytest.mark.asyncio
    async def test_query_optimizer_creation(self, query_optimizer):
        """Testa criação do otimizador de queries"""
        assert len(query_optimizer.query_cache) == 0
        assert len(query_optimizer.query_stats) == 0
    
    @pytest.mark.asyncio
    async def test_query_optimization(self, query_optimizer):
        """Testa otimização de queries"""
        # Query não otimizada
        original_query = "SELECT * FROM users WHERE active = true"
        
        # Otimizar query
        optimized_query = query_optimizer.optimize_query(original_query)
        
        assert "SELECT *" not in optimized_query
        assert "ORDER BY" in optimized_query
        assert "LIMIT" in optimized_query
        
        # Verificar cache
        assert len(query_optimizer.query_cache) == 1
    
    @pytest.mark.asyncio
    async def test_query_optimization_performance(self, query_optimizer, performance_monitor):
        """Testa performance da otimização de queries"""
        queries = [
            "SELECT * FROM users WHERE active = true",
            "SELECT * FROM products WHERE category = 'electronics'",
            "SELECT * FROM orders WHERE status = 'pending'",
            "SELECT * FROM customers WHERE email LIKE '%@gmail.com'"
        ]
        
        performance_monitor.start_monitoring()
        
        # Otimizar queries múltiplas vezes
        for _ in range(50):
            for query in queries:
                optimized = query_optimizer.optimize_query(query)
        
        metrics = performance_monitor.stop_monitoring("query_optimization", 200)
        
        assert metrics.execution_time < 0.1
        assert metrics.throughput > 1000

class TestMemoryManagement:
    """Testes de gerenciamento de memória"""
    
    @pytest.mark.asyncio
    async def test_memory_usage_monitoring(self, performance_monitor):
        """Testa monitoramento de uso de memória"""
        # Iniciar monitoramento de memória
        tracemalloc.start()
        
        performance_monitor.start_monitoring()
        
        # Alocar memória
        data = []
        for i in range(1000):
            data.append(f"string_{i}" * 100)
        
        # Forçar garbage collection
        gc.collect()
        
        metrics = performance_monitor.stop_monitoring("memory_allocation", 1)
        
        # Parar monitoramento
        tracemalloc.stop()
        
        assert metrics.memory_usage > 0
        assert metrics.memory_usage < 100 * 1024 * 1024  # Menos de 100MB
    
    @pytest.mark.asyncio
    async def test_memory_cleanup_performance(self, performance_monitor):
        """Testa performance de limpeza de memória"""
        performance_monitor.start_monitoring()
        
        # Alocar e liberar memória múltiplas vezes
        for _ in range(100):
            data = [f"string_{i}" * 100 for i in range(100)]
            del data
            gc.collect()
        
        metrics = performance_monitor.stop_monitoring("memory_cleanup", 100)
        
        assert metrics.execution_time < 1.0
        assert metrics.error_count == 0

class TestCPUOptimization:
    """Testes de otimização de CPU"""
    
    @pytest.mark.asyncio
    async def test_cpu_intensive_operations(self, performance_monitor):
        """Testa operações intensivas de CPU"""
        performance_monitor.start_monitoring()
        
        # Operação intensiva de CPU
        def cpu_intensive():
            result = 0
            for i in range(100000):
                result += i * i
            return result
        
        # Executar em loop
        for _ in range(10):
            cpu_intensive()
        
        metrics = performance_monitor.stop_monitoring("cpu_intensive", 10)
        
        assert metrics.execution_time < 1.0
        assert metrics.cpu_usage > 0
    
    @pytest.mark.asyncio
    async def test_cpu_optimization_with_threading(self, performance_monitor):
        """Testa otimização de CPU com threading"""
        import concurrent.futures
        
        def cpu_task(n):
            result = 0
            for i in range(n):
                result += i * i
            return result
        
        performance_monitor.start_monitoring()
        
        # Executar com ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(cpu_task, 10000) for _ in range(20)]
            results = [future.result() for future in futures]
        
        metrics = performance_monitor.stop_monitoring("cpu_threading", 20)
        
        assert len(results) == 20
        assert metrics.execution_time < 2.0

class TestNetworkOptimization:
    """Testes de otimização de rede"""
    
    @pytest.mark.asyncio
    async def test_network_request_batching(self, performance_monitor):
        """Testa batching de requisições de rede"""
        # Simular requisições de rede
        async def network_request(data):
            await asyncio.sleep(0.01)  # Simular latência de rede
            return f"response_{data}"
        
        performance_monitor.start_monitoring()
        
        # Requisições individuais
        individual_results = []
        for i in range(10):
            result = await network_request(i)
            individual_results.append(result)
        
        # Requisições em lote
        batch_results = await asyncio.gather(*[network_request(i) for i in range(10)])
        
        metrics = performance_monitor.stop_monitoring("network_batching", 20)
        
        assert len(individual_results) == 10
        assert len(batch_results) == 10
        assert metrics.execution_time < 0.5
    
    @pytest.mark.asyncio
    async def test_network_connection_pooling(self, performance_monitor):
        """Testa pooling de conexões de rede"""
        class NetworkConnection:
            def __init__(self, id):
                self.id = id
                self.connected = True
            
            async def request(self, data):
                await asyncio.sleep(0.001)
                return f"response_{data}_from_conn_{self.id}"
        
        # Pool de conexões
        connections = [NetworkConnection(i) for i in range(5)]
        connection_pool = connections.copy()
        
        async def get_connection():
            if connection_pool:
                return connection_pool.pop()
            return connections[0]  # Fallback
        
        async def release_connection(conn):
            if conn not in connection_pool:
                connection_pool.append(conn)
        
        performance_monitor.start_monitoring()
        
        # Usar pool de conexões
        for i in range(20):
            conn = await get_connection()
            result = await conn.request(i)
            await release_connection(conn)
        
        metrics = performance_monitor.stop_monitoring("network_connection_pooling", 20)
        
        assert metrics.execution_time < 0.1
        assert metrics.error_count == 0

class TestOverallPerformance:
    """Testes de performance geral"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_performance(self, performance_monitor):
        """Testa performance end-to-end"""
        # Simular operação completa
        async def complete_operation():
            # Simular diferentes etapas
            await asyncio.sleep(0.001)  # I/O
            _ = sum(i * i for i in range(1000))  # CPU
            await asyncio.sleep(0.001)  # Network
            return "success"
        
        performance_monitor.start_monitoring()
        
        # Executar operações
        results = await asyncio.gather(*[complete_operation() for _ in range(50)])
        
        metrics = performance_monitor.stop_monitoring("end_to_end_performance", 50)
        
        assert len(results) == 50
        assert all(r == "success" for r in results)
        assert metrics.execution_time < 1.0
        assert metrics.error_count == 0
    
    @pytest.mark.asyncio
    async def test_performance_under_load(self, performance_monitor):
        """Testa performance sob carga"""
        async def load_operation():
            # Simular operação sob carga
            await asyncio.sleep(0.01)
            _ = sum(i * i for i in range(100))
            return "load_complete"
        
        performance_monitor.start_monitoring()
        
        # Executar com diferentes níveis de concorrência
        concurrency_levels = [1, 5, 10, 20]
        
        for concurrency in concurrency_levels:
            tasks = [load_operation() for _ in range(concurrency)]
            results = await asyncio.gather(*tasks)
            assert len(results) == concurrency
        
        metrics = performance_monitor.stop_monitoring("performance_under_load", sum(concurrency_levels))
        
        assert metrics.execution_time < 5.0
        assert metrics.throughput > 10
    
    @pytest.mark.asyncio
    async def test_performance_regression_detection(self, performance_monitor):
        """Testa detecção de regressão de performance"""
        # Baseline
        async def baseline_operation():
            await asyncio.sleep(0.01)
            return "baseline"
        
        performance_monitor.start_monitoring()
        await baseline_operation()
        baseline_metrics = performance_monitor.stop_monitoring("baseline", 1)
        
        # Operação com regressão
        async def regression_operation():
            await asyncio.sleep(0.05)  # 5x mais lento
            return "regression"
        
        performance_monitor.start_monitoring()
        await regression_operation()
        regression_metrics = performance_monitor.stop_monitoring("regression", 1)
        
        # Detectar regressão
        regression_factor = regression_metrics.execution_time / baseline_metrics.execution_time
        
        assert regression_factor > 3.0  # Deve detectar regressão significativa
        assert baseline_metrics.execution_time < 0.1
        assert regression_metrics.execution_time > 0.04

# Teste de funcionalidade
if __name__ == "__main__":
    async def test_performance():
        monitor = PerformanceMonitor()
        
        # Teste básico
        monitor.start_monitoring()
        await asyncio.sleep(0.1)
        metrics = monitor.stop_monitoring("test_operation", 1)
        
        print(f"Métricas: {metrics.to_dict()}")
        print(f"Resumo: {monitor.get_summary()}")
    
    asyncio.run(test_performance()) 