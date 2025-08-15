"""
🧪 Teste de Integração - Processamento de Filas

Tracing ID: integration-queue-processing-test-2025-01-27-001
Timestamp: 2025-01-27T21:00:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Testes baseados em processamento real de filas do sistema Omni Keywords Finder
🌲 ToT: Avaliadas múltiplas estratégias de processamento (FIFO, LIFO, Priority, Batch)
♻️ ReAct: Simulado cenários de produção e validada eficiência de processamento

Testa processamento de filas incluindo:
- Processamento FIFO (First In, First Out)
- Processamento LIFO (Last In, First Out)
- Processamento por prioridade
- Processamento em lote
- Processamento concorrente
- Processamento com retry
- Processamento com dead letter queue
- Processamento com métricas
- Processamento com monitoramento
- Processamento com logging estruturado
"""

import pytest
import asyncio
import time
import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from unittest.mock import Mock, patch, AsyncMock
import logging
from dataclasses import dataclass
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

# Importações do sistema real
from infrastructure.queue.redis_queue import RedisQueue
from infrastructure.queue.memory_queue import MemoryQueue
from infrastructure.queue.priority_queue import PriorityQueue
from infrastructure.queue.batch_processor import BatchProcessor
from infrastructure.queue.dead_letter_queue import DeadLetterQueue
from infrastructure.queue.queue_manager import QueueManager
from infrastructure.queue.queue_worker import QueueWorker
from infrastructure.monitoring.metrics_collector import MetricsCollector
from infrastructure.logging.structured_logger import StructuredLogger
from infrastructure.resilience.retry_mechanisms import RetryMechanism

# Configuração de logging
logger = logging.getLogger(__name__)

@dataclass
class QueueProcessingTestConfig:
    """Configuração para testes de processamento de filas"""
    queue_type: str = "redis"  # redis, memory, priority
    max_queue_size: int = 10000
    processing_timeout: float = 30.0
    enable_batch_processing: bool = True
    batch_size: int = 10
    batch_timeout: float = 5.0
    enable_priority_processing: bool = True
    enable_dead_letter_queue: bool = True
    enable_retry_logic: bool = True
    max_retry_attempts: int = 3
    enable_metrics: bool = True
    enable_monitoring: bool = True
    enable_logging: bool = True
    max_concurrent_workers: int = 5
    enable_compression: bool = True
    enable_serialization: bool = True

class QueueProcessingIntegrationTest:
    """Teste de integração para processamento de filas"""
    
    def __init__(self, config: Optional[QueueProcessingTestConfig] = None):
        self.config = config or QueueProcessingTestConfig()
        self.logger = StructuredLogger(
            module="queue_processing_integration_test",
            tracing_id="queue_processing_test_001"
        )
        self.metrics = MetricsCollector()
        
        # Inicializar filas
        self.redis_queue = RedisQueue()
        self.memory_queue = MemoryQueue()
        self.priority_queue = PriorityQueue()
        
        # Processadores
        self.batch_processor = BatchProcessor()
        self.dead_letter_queue = DeadLetterQueue()
        self.queue_manager = QueueManager()
        
        # Workers
        self.workers: List[QueueWorker] = []
        
        # Retry mechanism
        self.retry_mechanism = RetryMechanism("queue_retry", {
            "max_attempts": self.config.max_retry_attempts,
            "base_delay": 1.0
        })
        
        # Métricas de teste
        self.processing_events: List[Dict[str, Any]] = []
        self.batch_processing_events: List[Dict[str, Any]] = []
        self.dead_letter_events: List[Dict[str, Any]] = []
        self.performance_metrics: List[Dict[str, float]] = []
        
        logger.info(f"Queue Processing Integration Test inicializado com configuração: {self.config}")
    
    async def setup_test_environment(self):
        """Configura ambiente de teste"""
        try:
            # Conectar filas
            await self.redis_queue.connect()
            await self.memory_queue.connect()
            await self.priority_queue.connect()
            
            # Configurar gerenciador de filas
            self.queue_manager.configure({
                "max_queue_size": self.config.max_queue_size,
                "processing_timeout": self.config.processing_timeout,
                "enable_batch_processing": self.config.enable_batch_processing,
                "batch_size": self.config.batch_size,
                "batch_timeout": self.config.batch_timeout,
                "enable_priority_processing": self.config.enable_priority_processing,
                "enable_dead_letter_queue": self.config.enable_dead_letter_queue,
                "enable_retry_logic": self.config.enable_retry_logic,
                "max_concurrent_workers": self.config.max_concurrent_workers
            })
            
            # Configurar processadores
            self.batch_processor.configure({
                "batch_size": self.config.batch_size,
                "batch_timeout": self.config.batch_timeout,
                "enable_metrics": self.config.enable_metrics
            })
            
            self.dead_letter_queue.configure({
                "max_retry_attempts": self.config.max_retry_attempts,
                "enable_monitoring": self.config.enable_monitoring
            })
            
            # Criar workers
            for i in range(self.config.max_concurrent_workers):
                worker = QueueWorker(f"worker-{i}")
                worker.configure({
                    "enable_retry": self.config.enable_retry_logic,
                    "enable_metrics": self.config.enable_metrics
                })
                self.workers.append(worker)
            
            logger.info("Ambiente de teste configurado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao configurar ambiente de teste: {e}")
            raise
    
    async def test_fifo_processing(self):
        """Testa processamento FIFO (First In, First Out)"""
        queue = self.memory_queue
        
        # Enfileirar itens
        test_items = [
            {"id": 1, "data": "item_1", "timestamp": datetime.now()},
            {"id": 2, "data": "item_2", "timestamp": datetime.now()},
            {"id": 3, "data": "item_3", "timestamp": datetime.now()},
            {"id": 4, "data": "item_4", "timestamp": datetime.now()},
            {"id": 5, "data": "item_5", "timestamp": datetime.now()}
        ]
        
        start_time = time.time()
        
        # Enfileirar itens
        for item in test_items:
            await queue.enqueue("fifo_test", item)
        
        enqueue_time = time.time() - start_time
        
        # Processar itens
        processed_items = []
        start_time = time.time()
        
        for _ in range(len(test_items)):
            item = await queue.dequeue("fifo_test")
            if item:
                processed_items.append(item)
        
        processing_time = time.time() - start_time
        
        # Verificar ordem FIFO
        fifo_correct = True
        for i, (original, processed) in enumerate(zip(test_items, processed_items)):
            if original["id"] != processed["id"]:
                fifo_correct = False
                logger.warning(f"Ordem FIFO incorreta na posição {i}: esperado {original['id']}, obtido {processed['id']}")
        
        assert fifo_correct, "Processamento FIFO não funcionou corretamente"
        assert len(processed_items) == len(test_items), "Nem todos os itens foram processados"
        
        logger.info(f"Processamento FIFO testado com sucesso: enfileiramento {enqueue_time:.3f}s, processamento {processing_time:.3f}s")
        
        return {
            "success": True,
            "enqueue_time": enqueue_time,
            "processing_time": processing_time,
            "fifo_correct": fifo_correct,
            "items_processed": len(processed_items)
        }
    
    async def test_lifo_processing(self):
        """Testa processamento LIFO (Last In, First Out)"""
        queue = self.memory_queue
        
        # Enfileirar itens
        test_items = [
            {"id": 1, "data": "item_1", "timestamp": datetime.now()},
            {"id": 2, "data": "item_2", "timestamp": datetime.now()},
            {"id": 3, "data": "item_3", "timestamp": datetime.now()},
            {"id": 4, "data": "item_4", "timestamp": datetime.now()},
            {"id": 5, "data": "item_5", "timestamp": datetime.now()}
        ]
        
        # Enfileirar itens
        for item in test_items:
            await queue.enqueue("lifo_test", item, lifo=True)
        
        # Processar itens
        processed_items = []
        for _ in range(len(test_items)):
            item = await queue.dequeue("lifo_test")
            if item:
                processed_items.append(item)
        
        # Verificar ordem LIFO (último a entrar, primeiro a sair)
        lifo_correct = True
        for i, (original, processed) in enumerate(zip(test_items[::-1], processed_items)):
            if original["id"] != processed["id"]:
                lifo_correct = False
                logger.warning(f"Ordem LIFO incorreta na posição {i}: esperado {original['id']}, obtido {processed['id']}")
        
        assert lifo_correct, "Processamento LIFO não funcionou corretamente"
        assert len(processed_items) == len(test_items), "Nem todos os itens foram processados"
        
        logger.info("Processamento LIFO testado com sucesso")
        
        return {
            "success": True,
            "lifo_correct": lifo_correct,
            "items_processed": len(processed_items)
        }
    
    async def test_priority_processing(self):
        """Testa processamento por prioridade"""
        queue = self.priority_queue
        
        # Enfileirar itens com diferentes prioridades
        test_items = [
            {"id": 1, "data": "low_priority", "priority": 3},
            {"id": 2, "data": "high_priority", "priority": 1},
            {"id": 3, "data": "medium_priority", "priority": 2},
            {"id": 4, "data": "very_high_priority", "priority": 0},
            {"id": 5, "data": "low_priority_2", "priority": 3}
        ]
        
        # Enfileirar itens
        for item in test_items:
            await queue.enqueue("priority_test", item, priority=item["priority"])
        
        # Processar itens
        processed_items = []
        for _ in range(len(test_items)):
            item = await queue.dequeue("priority_test")
            if item:
                processed_items.append(item)
        
        # Verificar ordem de prioridade (menor número = maior prioridade)
        priority_correct = True
        expected_order = [4, 2, 3, 1, 5]  # IDs na ordem de prioridade
        
        for i, (expected_id, processed) in enumerate(zip(expected_order, processed_items)):
            if expected_id != processed["id"]:
                priority_correct = False
                logger.warning(f"Ordem de prioridade incorreta na posição {i}: esperado {expected_id}, obtido {processed['id']}")
        
        assert priority_correct, "Processamento por prioridade não funcionou corretamente"
        assert len(processed_items) == len(test_items), "Nem todos os itens foram processados"
        
        logger.info("Processamento por prioridade testado com sucesso")
        
        return {
            "success": True,
            "priority_correct": priority_correct,
            "items_processed": len(processed_items)
        }
    
    async def test_batch_processing(self):
        """Testa processamento em lote"""
        queue = self.memory_queue
        
        # Enfileirar muitos itens
        num_items = 50
        test_items = []
        
        for i in range(num_items):
            item = {
                "id": i,
                "data": f"batch_item_{i}",
                "timestamp": datetime.now()
            }
            test_items.append(item)
            await queue.enqueue("batch_test", item)
        
        start_time = time.time()
        
        # Processar em lotes
        batch_size = self.config.batch_size
        processed_batches = []
        
        while True:
            batch = await self.batch_processor.process_batch(queue, "batch_test", batch_size)
            if not batch:
                break
            processed_batches.append(batch)
        
        processing_time = time.time() - start_time
        
        # Verificar processamento
        total_processed = sum(len(batch) for batch in processed_batches)
        assert total_processed == num_items, f"Processamento em lote incompleto: {total_processed}/{num_items}"
        
        # Verificar tamanho dos lotes
        batch_sizes = [len(batch) for batch in processed_batches]
        assert all(size <= batch_size for size in batch_sizes), "Lotes excederam tamanho máximo"
        
        logger.info(f"Processamento em lote testado com sucesso: {len(processed_batches)} lotes, {processing_time:.3f}s")
        
        return {
            "success": True,
            "processing_time": processing_time,
            "num_batches": len(processed_batches),
            "total_processed": total_processed,
            "batch_sizes": batch_sizes
        }
    
    async def test_concurrent_processing(self):
        """Testa processamento concorrente"""
        queue = self.memory_queue
        
        # Enfileirar itens
        num_items = 100
        for i in range(num_items):
            item = {
                "id": i,
                "data": f"concurrent_item_{i}",
                "timestamp": datetime.now()
            }
            await queue.enqueue("concurrent_test", item)
        
        # Função de processamento para worker
        async def worker_process(worker_id: int):
            processed_items = []
            while True:
                try:
                    item = await queue.dequeue("concurrent_test", timeout=1.0)
                    if item is None:
                        break
                    
                    # Simular processamento
                    await asyncio.sleep(random.uniform(0.01, 0.1))
                    processed_items.append(item)
                    
                except Exception as e:
                    logger.error(f"Erro no worker {worker_id}: {e}")
                    break
            
            return {
                "worker_id": worker_id,
                "processed_items": processed_items
            }
        
        start_time = time.time()
        
        # Executar workers concorrentes
        tasks = [worker_process(i) for i in range(self.config.max_concurrent_workers)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        processing_time = time.time() - start_time
        
        # Analisar resultados
        successful_workers = [r for r in results if isinstance(r, dict)]
        failed_workers = [r for r in results if isinstance(r, Exception)]
        
        total_processed = sum(len(r["processed_items"]) for r in successful_workers)
        
        assert len(successful_workers) > 0, "Nenhum worker foi bem-sucedido"
        assert total_processed == num_items, f"Processamento concorrente incompleto: {total_processed}/{num_items}"
        
        logger.info(f"Processamento concorrente testado: {len(successful_workers)} workers, {processing_time:.3f}s")
        
        return {
            "success": True,
            "processing_time": processing_time,
            "successful_workers": len(successful_workers),
            "failed_workers": len(failed_workers),
            "total_processed": total_processed
        }
    
    async def test_retry_processing(self):
        """Testa processamento com retry"""
        queue = self.memory_queue
        
        # Enfileirar itens
        test_items = [
            {"id": 1, "data": "retry_item_1", "attempts": 0},
            {"id": 2, "data": "retry_item_2", "attempts": 0},
            {"id": 3, "data": "retry_item_3", "attempts": 0}
        ]
        
        for item in test_items:
            await queue.enqueue("retry_test", item)
        
        # Função de processamento com falha simulada
        async def process_with_retry(item):
            item["attempts"] += 1
            
            # Simular falha nas primeiras tentativas
            if item["attempts"] < 3:
                raise Exception(f"Simulated failure on attempt {item['attempts']}")
            
            return {"processed": True, "item": item}
        
        # Processar itens com retry
        processed_items = []
        for _ in range(len(test_items)):
            item = await queue.dequeue("retry_test")
            if item:
                try:
                    result = await self.retry_mechanism.execute(
                        lambda: process_with_retry(item)
                    )
                    processed_items.append(result)
                except Exception as e:
                    logger.error(f"Item falhou após retry: {e}")
        
        # Verificar que todos os itens foram processados com retry
        assert len(processed_items) == len(test_items), "Nem todos os itens foram processados"
        
        # Verificar que todos tiveram 3 tentativas
        for item in test_items:
            assert item["attempts"] == 3, f"Item {item['id']} não teve 3 tentativas: {item['attempts']}"
        
        logger.info("Processamento com retry testado com sucesso")
        
        return {
            "success": True,
            "items_processed": len(processed_items),
            "retry_attempts": [item["attempts"] for item in test_items]
        }
    
    async def test_dead_letter_queue(self):
        """Testa dead letter queue"""
        queue = self.memory_queue
        
        # Enfileirar itens
        test_items = [
            {"id": 1, "data": "successful_item"},
            {"id": 2, "data": "failed_item"},
            {"id": 3, "data": "successful_item_2"}
        ]
        
        for item in test_items:
            await queue.enqueue("dlq_test", item)
        
        # Função de processamento que falha para item específico
        async def process_with_failure(item):
            if item["id"] == 2:  # Item que deve falhar
                raise Exception("Simulated processing failure")
            return {"processed": True, "item": item}
        
        # Processar itens
        processed_items = []
        dead_letter_items = []
        
        for _ in range(len(test_items)):
            item = await queue.dequeue("dlq_test")
            if item:
                try:
                    result = await process_with_failure(item)
                    processed_items.append(result)
                except Exception as e:
                    # Enviar para dead letter queue
                    await self.dead_letter_queue.enqueue("dlq_test", item, error=str(e))
                    dead_letter_items.append(item)
        
        # Verificar processamento
        assert len(processed_items) == 2, "Itens bem-sucedidos não processados corretamente"
        assert len(dead_letter_items) == 1, "Item falhado não foi para dead letter queue"
        assert dead_letter_items[0]["id"] == 2, "Item incorreto foi para dead letter queue"
        
        logger.info("Dead letter queue testado com sucesso")
        
        return {
            "success": True,
            "processed_items": len(processed_items),
            "dead_letter_items": len(dead_letter_items)
        }
    
    async def test_performance_monitoring(self):
        """Testa monitoramento de performance"""
        queue = self.memory_queue
        
        # Executar operações para gerar métricas
        for i in range(100):
            item = {"id": i, "data": f"perf_item_{i}"}
            await queue.enqueue("perf_test", item)
        
        for i in range(100):
            await queue.dequeue("perf_test")
        
        # Obter métricas de performance
        performance_metrics = self.queue_manager.get_performance_metrics()
        
        # Verificar métricas
        assert "total_enqueued" in performance_metrics
        assert "total_dequeued" in performance_metrics
        assert "avg_processing_time" in performance_metrics
        assert "throughput" in performance_metrics
        
        # Verificar valores razoáveis
        assert performance_metrics["total_enqueued"] > 0
        assert performance_metrics["total_dequeued"] > 0
        assert performance_metrics["avg_processing_time"] > 0
        assert performance_metrics["throughput"] > 0
        
        logger.info(f"Monitoramento de performance testado: {performance_metrics}")
        
        return {
            "success": True,
            "performance_metrics": performance_metrics
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de performance dos testes"""
        return {
            "total_processing_events": len(self.processing_events),
            "total_batch_processing_events": len(self.batch_processing_events),
            "total_dead_letter_events": len(self.dead_letter_events),
            "processing_events": self.processing_events,
            "batch_processing_events": self.batch_processing_events,
            "dead_letter_events": self.dead_letter_events
        }
    
    async def cleanup(self):
        """Limpa recursos de teste"""
        try:
            await self.redis_queue.disconnect()
            await self.memory_queue.disconnect()
            await self.priority_queue.disconnect()
            await self.dead_letter_queue.disconnect()
            logger.info("Recursos de teste limpos com sucesso")
        except Exception as e:
            logger.error(f"Erro ao limpar recursos: {e}")

# Testes pytest
@pytest.mark.asyncio
class TestQueueProcessingIntegration:
    """Testes de integração para processamento de filas"""
    
    @pytest.fixture(autouse=True)
    async def setup_test(self):
        """Configuração do teste"""
        self.test_instance = QueueProcessingIntegrationTest()
        await self.test_instance.setup_test_environment()
        yield
        await self.test_instance.cleanup()
    
    async def test_fifo_processing(self):
        """Testa processamento FIFO"""
        result = await self.test_instance.test_fifo_processing()
        assert result["success"] is True
        assert result["fifo_correct"] is True
    
    async def test_lifo_processing(self):
        """Testa processamento LIFO"""
        result = await self.test_instance.test_lifo_processing()
        assert result["success"] is True
        assert result["lifo_correct"] is True
    
    async def test_priority_processing(self):
        """Testa processamento por prioridade"""
        result = await self.test_instance.test_priority_processing()
        assert result["success"] is True
        assert result["priority_correct"] is True
    
    async def test_batch_processing(self):
        """Testa processamento em lote"""
        result = await self.test_instance.test_batch_processing()
        assert result["success"] is True
        assert result["total_processed"] == 50
    
    async def test_concurrent_processing(self):
        """Testa processamento concorrente"""
        result = await self.test_instance.test_concurrent_processing()
        assert result["success"] is True
        assert result["successful_workers"] > 0
    
    async def test_retry_processing(self):
        """Testa processamento com retry"""
        result = await self.test_instance.test_retry_processing()
        assert result["success"] is True
        assert all(attempts == 3 for attempts in result["retry_attempts"])
    
    async def test_dead_letter_queue(self):
        """Testa dead letter queue"""
        result = await self.test_instance.test_dead_letter_queue()
        assert result["success"] is True
        assert result["dead_letter_items"] == 1
    
    async def test_performance_monitoring(self):
        """Testa monitoramento de performance"""
        result = await self.test_instance.test_performance_monitoring()
        assert result["success"] is True
    
    async def test_overall_queue_processing_metrics(self):
        """Testa métricas gerais de processamento de filas"""
        # Executar todos os testes
        await self.test_instance.test_fifo_processing()
        await self.test_instance.test_lifo_processing()
        await self.test_instance.test_priority_processing()
        await self.test_instance.test_batch_processing()
        await self.test_instance.test_concurrent_processing()
        await self.test_instance.test_retry_processing()
        await self.test_instance.test_dead_letter_queue()
        await self.test_instance.test_performance_monitoring()
        
        # Obter métricas
        metrics = self.test_instance.get_performance_metrics()
        
        # Verificar métricas
        assert metrics["total_processing_events"] > 0
        assert metrics["total_batch_processing_events"] > 0
        assert metrics["total_dead_letter_events"] > 0

if __name__ == "__main__":
    # Execução direta do teste
    async def main():
        test_instance = QueueProcessingIntegrationTest()
        try:
            await test_instance.setup_test_environment()
            
            # Executar todos os testes
            await test_instance.test_fifo_processing()
            await test_instance.test_lifo_processing()
            await test_instance.test_priority_processing()
            await test_instance.test_batch_processing()
            await test_instance.test_concurrent_processing()
            await test_instance.test_retry_processing()
            await test_instance.test_dead_letter_queue()
            await test_instance.test_performance_monitoring()
            
            # Obter métricas finais
            metrics = test_instance.get_performance_metrics()
            print(f"Métricas de Processamento de Filas: {json.dumps(metrics, indent=2, default=str)}")
            
        finally:
            await test_instance.cleanup()
    
    asyncio.run(main()) 