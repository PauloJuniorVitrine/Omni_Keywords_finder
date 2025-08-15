#!/usr/bin/env python3
"""
🎯 Script de Otimização de Processamento Assíncrono
📋 Objetivo: Otimizar performance através de processamento assíncrono
🔧 Tracing ID: ASYNC_OPTIMIZATION_20250127_001
📅 Data: 2025-01-27
"""

import os
import sys
import json
import asyncio
import time
import logging
import aiohttp
import aiofiles
import aioredis
from typing import Dict, List, Any, Optional, Callable, Coroutine
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing
import psutil
import uvloop

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/async_optimization.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class AsyncConfig:
    """Configuração para processamento assíncrono"""
    max_concurrent_tasks: int = 100
    max_workers_thread: int = 20
    max_workers_process: int = multiprocessing.cpu_count()
    timeout_seconds: int = 30
    retry_attempts: int = 3
    batch_size: int = 50
    enable_uvloop: bool = True
    enable_connection_pooling: bool = True
    pool_size: int = 100
    keepalive_timeout: int = 60

@dataclass
class PerformanceMetrics:
    """Métricas de performance"""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_time: float = 0.0
    avg_task_time: float = 0.0
    throughput: float = 0.0  # tasks/second
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    concurrent_tasks: int = 0

class AsyncTaskManager:
    """Gerenciador de tarefas assíncronas"""
    
    def __init__(self, config: AsyncConfig):
        self.config = config
        self.metrics = PerformanceMetrics()
        self.session = None
        self.redis_pool = None
        self.thread_pool = ThreadPoolExecutor(max_workers=config.max_workers_thread)
        self.process_pool = ProcessPoolExecutor(max_workers=config.max_workers_process)
        self.semaphore = asyncio.Semaphore(config.max_concurrent_tasks)
        
        # Configurar uvloop se habilitado
        if config.enable_uvloop:
            try:
                uvloop.install()
                logger.info("✅ uvloop habilitado para melhor performance")
            except ImportError:
                logger.warning("⚠️ uvloop não disponível, usando asyncio padrão")
    
    async def __aenter__(self):
        """Context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.cleanup()
    
    async def initialize(self):
        """Inicializa recursos assíncronos"""
        # Criar session HTTP com pooling
        if self.config.enable_connection_pooling:
            connector = aiohttp.TCPConnector(
                limit=self.config.pool_size,
                limit_per_host=50,
                keepalive_timeout=self.config.keepalive_timeout
            )
            self.session = aiohttp.ClientSession(connector=connector)
            logger.info("✅ Session HTTP com pooling criada")
        
        # Conectar ao Redis se disponível
        try:
            self.redis_pool = await aioredis.create_redis_pool('redis://localhost')
            logger.info("✅ Pool Redis criado")
        except Exception as e:
            logger.warning(f"⚠️ Redis não disponível: {e}")
    
    async def cleanup(self):
        """Limpa recursos assíncronos"""
        if self.session:
            await self.session.close()
            logger.info("✅ Session HTTP fechada")
        
        if self.redis_pool:
            self.redis_pool.close()
            await self.redis_pool.wait_closed()
            logger.info("✅ Pool Redis fechado")
        
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
        logger.info("✅ Pools de threads e processos fechados")
    
    async def execute_with_semaphore(self, coro: Coroutine) -> Any:
        """Executa corotina com controle de concorrência"""
        async with self.semaphore:
            self.metrics.concurrent_tasks += 1
            try:
                start_time = time.time()
                result = await coro
                execution_time = time.time() - start_time
                
                self.metrics.completed_tasks += 1
                self.metrics.total_time += execution_time
                self.metrics.avg_task_time = (
                    self.metrics.total_time / self.metrics.completed_tasks
                )
                
                return result
            except Exception as e:
                self.metrics.failed_tasks += 1
                logger.error(f"❌ Erro na execução da tarefa: {e}")
                raise
            finally:
                self.metrics.concurrent_tasks -= 1
    
    async def execute_batch(self, tasks: List[Coroutine]) -> List[Any]:
        """Executa lote de tarefas assíncronas"""
        self.metrics.total_tasks += len(tasks)
        start_time = time.time()
        
        # Executar tarefas em paralelo
        results = await asyncio.gather(
            *[self.execute_with_semaphore(task) for task in tasks],
            return_exceptions=True
        )
        
        # Calcular throughput
        total_time = time.time() - start_time
        self.metrics.throughput = len(tasks) / total_time if total_time > 0 else 0
        
        # Atualizar métricas do sistema
        self.metrics.memory_usage = psutil.virtual_memory().percent
        self.metrics.cpu_usage = psutil.cpu_percent()
        
        return results
    
    async def execute_with_retry(self, coro: Coroutine, max_retries: Optional[int] = None) -> Any:
        """Executa corotina com retry automático"""
        max_retries = max_retries or self.config.retry_attempts
        
        for attempt in range(max_retries + 1):
            try:
                return await coro
            except Exception as e:
                if attempt == max_retries:
                    logger.error(f"❌ Falha após {max_retries} tentativas: {e}")
                    raise
                
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"⚠️ Tentativa {attempt + 1} falhou, aguardando {wait_time}s: {e}")
                await asyncio.sleep(wait_time)

class AsyncDataProcessor:
    """Processador de dados assíncrono"""
    
    def __init__(self, task_manager: AsyncTaskManager):
        self.task_manager = task_manager
    
    async def process_data_batch(self, data_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Processa lote de dados de forma assíncrona"""
        tasks = []
        
        for item in data_batch:
            task = self.process_single_item(item)
            tasks.append(task)
        
        results = await self.task_manager.execute_batch(tasks)
        return [r for r in results if not isinstance(r, Exception)]
    
    async def process_single_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Processa item individual"""
        # Simular processamento
        await asyncio.sleep(0.01)  # Simular I/O
        
        # Aplicar transformações
        processed_item = {
            'id': item.get('id'),
            'processed_at': datetime.now().isoformat(),
            'status': 'processed',
            'data': item.get('data', {})
        }
        
        return processed_item
    
    async def fetch_data_async(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Busca dados de múltiplas URLs de forma assíncrona"""
        if not self.task_manager.session:
            raise RuntimeError("Session HTTP não inicializada")
        
        async def fetch_url(url: str) -> Dict[str, Any]:
            try:
                async with self.task_manager.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {'url': url, 'data': data, 'status': 'success'}
                    else:
                        return {'url': url, 'data': None, 'status': f'error_{response.status}'}
            except Exception as e:
                return {'url': url, 'data': None, 'status': f'error: {str(e)}'}
        
        tasks = [fetch_url(url) for url in urls]
        return await self.task_manager.execute_batch(tasks)
    
    async def save_data_async(self, data: List[Dict[str, Any]], file_path: str):
        """Salva dados de forma assíncrona"""
        async def save_chunk(chunk: List[Dict[str, Any]], chunk_id: int):
            chunk_file = f"{file_path}_chunk_{chunk_id}.json"
            async with aiofiles.open(chunk_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(chunk, indent=2, default=str))
            return chunk_file
        
        # Dividir dados em chunks
        chunk_size = self.task_manager.config.batch_size
        chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
        
        tasks = [save_chunk(chunk, i) for i, chunk in enumerate(chunks)]
        saved_files = await self.task_manager.execute_batch(tasks)
        
        return [f for f in saved_files if not isinstance(f, Exception)]

class AsyncCacheManager:
    """Gerenciador de cache assíncrono"""
    
    def __init__(self, task_manager: AsyncTaskManager):
        self.task_manager = task_manager
    
    async def get_cached_data(self, key: str) -> Optional[Any]:
        """Obtém dados do cache"""
        if not self.task_manager.redis_pool:
            return None
        
        try:
            data = await self.task_manager.redis_pool.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao obter cache para {key}: {e}")
            return None
    
    async def set_cached_data(self, key: str, data: Any, ttl: int = 3600) -> bool:
        """Define dados no cache"""
        if not self.task_manager.redis_pool:
            return False
        
        try:
            serialized_data = json.dumps(data, default=str)
            await self.task_manager.redis_pool.setex(key, ttl, serialized_data)
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao definir cache para {key}: {e}")
            return False
    
    async def invalidate_cache(self, pattern: str) -> int:
        """Invalida cache por padrão"""
        if not self.task_manager.redis_pool:
            return 0
        
        try:
            keys = await self.task_manager.redis_pool.keys(pattern)
            if keys:
                await self.task_manager.redis_pool.delete(*keys)
                return len(keys)
            return 0
        except Exception as e:
            logger.error(f"❌ Erro ao invalidar cache: {e}")
            return 0

def create_async_optimization_config():
    """Cria configuração de otimização assíncrona"""
    config = {
        "async_config": {
            "max_concurrent_tasks": 100,
            "max_workers_thread": 20,
            "max_workers_process": multiprocessing.cpu_count(),
            "timeout_seconds": 30,
            "retry_attempts": 3,
            "batch_size": 50,
            "enable_uvloop": True,
            "enable_connection_pooling": True,
            "pool_size": 100,
            "keepalive_timeout": 60
        },
        "optimization_strategies": {
            "connection_pooling": {
                "description": "Reutilização de conexões HTTP",
                "enabled": True,
                "max_connections": 100
            },
            "batch_processing": {
                "description": "Processamento em lotes",
                "enabled": True,
                "batch_size": 50
            },
            "caching": {
                "description": "Cache Redis para dados frequentes",
                "enabled": True,
                "default_ttl": 3600
            },
            "retry_logic": {
                "description": "Retry automático com backoff exponencial",
                "enabled": True,
                "max_retries": 3
            }
        },
        "monitoring": {
            "enable_metrics": True,
            "metrics_interval": 60,
            "alert_thresholds": {
                "memory_usage": 80,
                "cpu_usage": 90,
                "error_rate": 5
            }
        }
    }
    
    config_path = "config/async_optimization_config.json"
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, default=str)
    
    logger.info(f"✅ Configuração de otimização assíncrona salva em {config_path}")
    return config_path

def create_async_monitoring():
    """Cria sistema de monitoramento assíncrono"""
    monitoring_code = '''
import asyncio
import time
import psutil
from datetime import datetime
from typing import Dict, List

class AsyncPerformanceMonitor:
    """Monitor de performance assíncrono"""
    
    def __init__(self, task_manager):
        self.task_manager = task_manager
        self.metrics_history = []
        self.monitoring_task = None
    
    async def start_monitoring(self, interval: int = 60):
        """Inicia monitoramento contínuo"""
        self.monitoring_task = asyncio.create_task(
            self._monitor_loop(interval)
        )
        logger.info(f"✅ Monitoramento iniciado com intervalo de {interval}s")
    
    async def stop_monitoring(self):
        """Para monitoramento"""
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            logger.info("✅ Monitoramento parado")
    
    async def _monitor_loop(self, interval: int):
        """Loop de monitoramento"""
        while True:
            try:
                metrics = await self._collect_metrics()
                self.metrics_history.append(metrics)
                
                # Verificar alertas
                await self._check_alerts(metrics)
                
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erro no monitoramento: {e}")
                await asyncio.sleep(interval)
    
    async def _collect_metrics(self) -> Dict[str, Any]:
        """Coleta métricas atuais"""
        metrics = self.task_manager.metrics
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_tasks': metrics.total_tasks,
            'completed_tasks': metrics.completed_tasks,
            'failed_tasks': metrics.failed_tasks,
            'throughput': metrics.throughput,
            'avg_task_time': metrics.avg_task_time,
            'concurrent_tasks': metrics.concurrent_tasks,
            'memory_usage': psutil.virtual_memory().percent,
            'cpu_usage': psutil.cpu_percent(),
            'error_rate': (
                metrics.failed_tasks / metrics.total_tasks * 100
                if metrics.total_tasks > 0 else 0
            )
        }
    
    async def _check_alerts(self, metrics: Dict[str, Any]):
        """Verifica e gera alertas"""
        alerts = []
        
        if metrics['memory_usage'] > 80:
            alerts.append(f"⚠️ Uso de memória alto: {metrics['memory_usage']:.1f}%")
        
        if metrics['cpu_usage'] > 90:
            alerts.append(f"⚠️ Uso de CPU alto: {metrics['cpu_usage']:.1f}%")
        
        if metrics['error_rate'] > 5:
            alerts.append(f"⚠️ Taxa de erro alta: {metrics['error_rate']:.1f}%")
        
        for alert in alerts:
            logger.warning(alert)
    
    def generate_report(self) -> Dict[str, Any]:
        """Gera relatório de performance"""
        if not self.metrics_history:
            return {}
        
        latest = self.metrics_history[-1]
        avg_throughput = sum(m['throughput'] for m in self.metrics_history) / len(self.metrics_history)
        avg_error_rate = sum(m['error_rate'] for m in self.metrics_history) / len(self.metrics_history)
        
        return {
            'current_metrics': latest,
            'average_throughput': avg_throughput,
            'average_error_rate': avg_error_rate,
            'total_measurements': len(self.metrics_history),
            'recommendations': self._generate_recommendations(latest, avg_throughput, avg_error_rate)
        }
    
    def _generate_recommendations(self, current: Dict[str, Any], avg_throughput: float, avg_error_rate: float) -> List[str]:
        """Gera recomendações baseadas nas métricas"""
        recommendations = []
        
        if avg_throughput < 10:
            recommendations.append("Considerar aumentar concorrência")
        
        if avg_error_rate > 2:
            recommendations.append("Revisar lógica de retry e tratamento de erros")
        
        if current['memory_usage'] > 70:
            recommendations.append("Monitorar uso de memória e considerar otimizações")
        
        if current['concurrent_tasks'] < 10:
            recommendations.append("Aumentar número de tarefas concorrentes")
        
        return recommendations
'''
    
    monitoring_path = "infrastructure/async/async_monitor.py"
    os.makedirs(os.path.dirname(monitoring_path), exist_ok=True)
    
    with open(monitoring_path, 'w', encoding='utf-8') as f:
        f.write(monitoring_code)
    
    logger.info(f"✅ Monitor assíncrono criado em {monitoring_path}")

def create_async_tests():
    """Cria testes para o sistema assíncrono"""
    test_code = '''
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from scripts.optimize_async_processing import (
    AsyncTaskManager, 
    AsyncDataProcessor, 
    AsyncCacheManager,
    AsyncConfig,
    PerformanceMetrics
)

class TestAsyncTaskManager:
    """Testes para o gerenciador de tarefas assíncronas"""
    
    @pytest.fixture
    def config(self):
        return AsyncConfig(
            max_concurrent_tasks=10,
            max_workers_thread=5,
            timeout_seconds=5
        )
    
    @pytest.fixture
    async def task_manager(self, config):
        async with AsyncTaskManager(config) as tm:
            yield tm
    
    @pytest.mark.asyncio
    async def test_task_manager_initialization(self, config):
        """Testa inicialização do gerenciador de tarefas"""
        async with AsyncTaskManager(config) as tm:
            assert tm.config == config
            assert tm.metrics.total_tasks == 0
            assert tm.semaphore._value == config.max_concurrent_tasks
    
    @pytest.mark.asyncio
    async def test_execute_with_semaphore(self, task_manager):
        """Testa execução com semáforo"""
        async def test_task():
            await asyncio.sleep(0.1)
            return "success"
        
        result = await task_manager.execute_with_semaphore(test_task())
        assert result == "success"
        assert task_manager.metrics.completed_tasks == 1
    
    @pytest.mark.asyncio
    async def test_execute_batch(self, task_manager):
        """Testa execução em lote"""
        async def test_task(i):
            await asyncio.sleep(0.01)
            return f"task_{i}"
        
        tasks = [test_task(i) for i in range(5)]
        results = await task_manager.execute_batch(tasks)
        
        assert len(results) == 5
        assert task_manager.metrics.total_tasks == 5
        assert task_manager.metrics.completed_tasks == 5
        assert task_manager.metrics.throughput > 0

class TestAsyncDataProcessor:
    """Testes para o processador de dados assíncrono"""
    
    @pytest.fixture
    async def processor(self, task_manager):
        return AsyncDataProcessor(task_manager)
    
    @pytest.mark.asyncio
    async def test_process_single_item(self, processor):
        """Testa processamento de item individual"""
        item = {"id": 1, "data": {"test": "value"}}
        result = await processor.process_single_item(item)
        
        assert result["id"] == 1
        assert result["status"] == "processed"
        assert "processed_at" in result
    
    @pytest.mark.asyncio
    async def test_process_data_batch(self, processor):
        """Testa processamento em lote"""
        data_batch = [
            {"id": i, "data": {"value": i}} 
            for i in range(3)
        ]
        
        results = await processor.process_data_batch(data_batch)
        assert len(results) == 3
        assert all(r["status"] == "processed" for r in results)

class TestAsyncCacheManager:
    """Testes para o gerenciador de cache assíncrono"""
    
    @pytest.fixture
    async def cache_manager(self, task_manager):
        return AsyncCacheManager(task_manager)
    
    @pytest.mark.asyncio
    async def test_cache_operations(self, cache_manager):
        """Testa operações de cache"""
        # Mock Redis pool
        mock_redis = AsyncMock()
        cache_manager.task_manager.redis_pool = mock_redis
        
        # Teste set
        mock_redis.setex.return_value = True
        result = await cache_manager.set_cached_data("test_key", {"data": "value"})
        assert result is True
        
        # Teste get
        mock_redis.get.return_value = '{"data": "value"}'
        result = await cache_manager.get_cached_data("test_key")
        assert result == {"data": "value"}
    
    @pytest.mark.asyncio
    async def test_cache_without_redis(self, cache_manager):
        """Testa cache sem Redis disponível"""
        cache_manager.task_manager.redis_pool = None
        
        result = await cache_manager.get_cached_data("test_key")
        assert result is None
        
        result = await cache_manager.set_cached_data("test_key", "value")
        assert result is False
'''
    
    test_path = "tests/unit/test_async_optimization.py"
    os.makedirs(os.path.dirname(test_path), exist_ok=True)
    
    with open(test_path, 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    logger.info(f"✅ Testes assíncronos criados em {test_path}")

async def demonstrate_async_optimization():
    """Demonstra otimizações assíncronas"""
    config = AsyncConfig()
    
    async with AsyncTaskManager(config) as task_manager:
        processor = AsyncDataProcessor(task_manager)
        cache_manager = AsyncCacheManager(task_manager)
        
        # Exemplo: Processar dados em lote
        sample_data = [
            {"id": i, "data": {"value": f"item_{i}"}}
            for i in range(100)
        ]
        
        logger.info("🚀 Iniciando processamento assíncrono de exemplo")
        
        # Processar dados
        start_time = time.time()
        results = await processor.process_data_batch(sample_data)
        processing_time = time.time() - start_time
        
        logger.info(f"✅ Processamento concluído:")
        logger.info(f"   - Itens processados: {len(results)}")
        logger.info(f"   - Tempo total: {processing_time:.2f}s")
        logger.info(f"   - Throughput: {len(results)/processing_time:.1f} itens/s")
        
        # Exemplo: Buscar dados de URLs
        urls = [
            "https://jsonplaceholder.typicode.com/posts/1",
            "https://jsonplaceholder.typicode.com/posts/2",
            "https://jsonplaceholder.typicode.com/posts/3"
        ]
        
        logger.info("🌐 Buscando dados de URLs de exemplo")
        fetched_data = await processor.fetch_data_async(urls)
        
        logger.info(f"✅ Dados buscados: {len(fetched_data)} URLs")
        
        # Exemplo: Cache
        await cache_manager.set_cached_data("example_key", {"cached": "data"})
        cached_data = await cache_manager.get_cached_data("example_key")
        
        if cached_data:
            logger.info("✅ Cache funcionando corretamente")
        
        return {
            "processed_items": len(results),
            "processing_time": processing_time,
            "throughput": len(results)/processing_time,
            "fetched_urls": len(fetched_data),
            "cache_working": cached_data is not None
        }

def main():
    """Função principal"""
    logger.info("🚀 Iniciando otimização de processamento assíncrono")
    
    try:
        # Criar configuração
        config_path = create_async_optimization_config()
        logger.info(f"✅ Configuração criada: {config_path}")
        
        # Criar monitoramento
        create_async_monitoring()
        logger.info("✅ Sistema de monitoramento criado")
        
        # Criar testes
        create_async_tests()
        logger.info("✅ Testes assíncronos criados")
        
        # Executar demonstração
        logger.info("🎯 Executando demonstração de otimizações")
        results = asyncio.run(demonstrate_async_optimization())
        
        logger.info("✅ Demonstração concluída")
        logger.info(f"📊 Resultados da demonstração:")
        logger.info(f"   - Itens processados: {results['processed_items']}")
        logger.info(f"   - Tempo de processamento: {results['processing_time']:.2f}s")
        logger.info(f"   - Throughput: {results['throughput']:.1f} itens/s")
        logger.info(f"   - URLs buscadas: {results['fetched_urls']}")
        logger.info(f"   - Cache funcionando: {results['cache_working']}")
        
        # Salvar relatório
        report = {
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "files_created": [
                "config/async_optimization_config.json",
                "infrastructure/async/async_monitor.py",
                "tests/unit/test_async_optimization.py"
            ],
            "features": [
                "Gerenciamento assíncrono de tarefas",
                "Processamento em lotes",
                "Connection pooling HTTP",
                "Cache Redis assíncrono",
                "Retry automático com backoff",
                "Monitoramento de performance",
                "Suporte a uvloop",
                "Pools de threads e processos"
            ],
            "demonstration_results": results,
            "recommendations": [
                "Configurar Redis para cache em produção",
                "Ajustar limites de concorrência baseado na carga",
                "Monitorar métricas de performance regularmente",
                "Implementar circuit breakers para serviços externos",
                "Usar load balancing para distribuir carga"
            ]
        }
        
        report_path = "docs/RELATORIO_OTIMIZACAO_ASSINCRONA.md"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# Relatório de Otimização Assíncrona\n\n")
            f.write(f"**Data**: {report['timestamp']}\n")
            f.write(f"**Status**: {report['status']}\n\n")
            f.write("## Arquivos Criados\n")
            for file in report['files_created']:
                f.write(f"- `{file}`\n")
            f.write("\n## Funcionalidades\n")
            for feature in report['features']:
                f.write(f"- {feature}\n")
            f.write("\n## Resultados da Demonstração\n")
            f.write(f"- Itens processados: {results['processed_items']}\n")
            f.write(f"- Tempo de processamento: {results['processing_time']:.2f}s\n")
            f.write(f"- Throughput: {results['throughput']:.1f} itens/s\n")
            f.write(f"- URLs buscadas: {results['fetched_urls']}\n")
            f.write(f"- Cache funcionando: {results['cache_working']}\n")
            f.write("\n## Recomendações\n")
            for rec in report['recommendations']:
                f.write(f"- {rec}\n")
        
        logger.info(f"✅ Relatório salvo em {report_path}")
        
    except Exception as e:
        logger.error(f"❌ Erro na otimização: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 