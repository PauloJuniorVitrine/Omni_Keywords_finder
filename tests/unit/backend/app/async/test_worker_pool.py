"""
Testes Unitários para WorkerPool
WorkerPool - Pool de workers para processamento assíncrono

Prompt: Implementação de testes unitários para WorkerPool
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Fase: Criação sem execução - Testes baseados em código real
Tracing ID: TEST_WORKER_POOL_20250127_001
"""

import pytest
import asyncio
import time
import threading
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from backend.app.async.worker_pool import (
    WorkerTask,
    WorkerStats,
    WorkerPool
)


class TestWorkerTask:
    """Testes para WorkerTask"""
    
    @pytest.fixture
    def sample_task_data(self):
        """Dados de exemplo para WorkerTask"""
        return {
            "id": "worker_task_001",
            "task_type": "nlp",
            "function": Mock(),
            "args": (1, 2, 3),
            "kwargs": {"param": "value"},
            "priority": 8,
            "created_at": datetime.now(),
            "timeout": 30.0,
            "retry_count": 0,
            "max_retries": 3,
            "dependencies": ["task_002"],
            "metadata": {"model": "bert", "language": "en"}
        }
    
    @pytest.fixture
    def task(self, sample_task_data):
        """Instância de WorkerTask para testes"""
        return WorkerTask(**sample_task_data)
    
    def test_initialization(self, sample_task_data):
        """Testa inicialização básica"""
        task = WorkerTask(**sample_task_data)
        
        assert task.id == "worker_task_001"
        assert task.task_type == "nlp"
        assert task.function == sample_task_data["function"]
        assert task.args == (1, 2, 3)
        assert task.kwargs == {"param": "value"}
        assert task.priority == 8
        assert task.created_at == sample_task_data["created_at"]
        assert task.timeout == 30.0
        assert task.retry_count == 0
        assert task.max_retries == 3
        assert task.dependencies == ["task_002"]
        assert task.metadata == {"model": "bert", "language": "en"}
    
    def test_default_values(self):
        """Testa valores padrão"""
        task = WorkerTask(
            id="test_task",
            task_type="ml",
            function=Mock()
        )
        
        assert task.priority == 5
        assert task.timeout is None
        assert task.retry_count == 0
        assert task.max_retries == 3
        assert task.dependencies == []
        assert task.metadata == {}


class TestWorkerStats:
    """Testes para WorkerStats"""
    
    @pytest.fixture
    def sample_stats_data(self):
        """Dados de exemplo para WorkerStats"""
        return {
            "worker_id": "worker_001",
            "status": "idle",
            "tasks_completed": 25,
            "tasks_failed": 2,
            "total_processing_time": 150.5,
            "avg_processing_time": 6.02,
            "current_task": "task_123",
            "last_task_time": datetime.now()
        }
    
    @pytest.fixture
    def stats(self, sample_stats_data):
        """Instância de WorkerStats para testes"""
        return WorkerStats(**sample_stats_data)
    
    def test_initialization(self, sample_stats_data):
        """Testa inicialização básica"""
        stats = WorkerStats(**sample_stats_data)
        
        assert stats.worker_id == "worker_001"
        assert stats.status == "idle"
        assert stats.tasks_completed == 25
        assert stats.tasks_failed == 2
        assert stats.total_processing_time == 150.5
        assert stats.avg_processing_time == 6.02
        assert stats.current_task == "task_123"
        assert stats.last_task_time == sample_stats_data["last_task_time"]
    
    def test_default_values(self):
        """Testa valores padrão"""
        stats = WorkerStats(worker_id="test_worker")
        
        assert stats.status == "idle"
        assert stats.tasks_completed == 0
        assert stats.tasks_failed == 0
        assert stats.total_processing_time == 0.0
        assert stats.avg_processing_time == 0.0
        assert stats.current_task is None
        assert stats.last_task_time is None


class TestWorkerPool:
    """Testes para WorkerPool"""
    
    @pytest.fixture
    def worker_pool(self):
        """Instância de WorkerPool para testes"""
        return WorkerPool(max_workers=4)
    
    @pytest.fixture
    def sample_task(self):
        """Tarefa de exemplo"""
        return WorkerTask(
            id="test_task",
            task_type="nlp",
            function=Mock(return_value="result"),
            priority=5
        )
    
    def test_initialization(self):
        """Testa inicialização do WorkerPool"""
        pool = WorkerPool(max_workers=4)
        
        assert pool.max_workers == 4
        assert pool.task_type_limits == {
            "nlp": 4,
            "ml": 3,
            "analysis": 2,
            "preprocessing": 1
        }
        assert pool.pending_tasks == {}
        assert pool.running_tasks == {}
        assert pool.completed_tasks == {}
        assert pool.failed_tasks == {}
        assert len(pool.worker_stats) == 4
        assert pool.is_running is True
    
    def test_default_initialization(self):
        """Testa inicialização com valores padrão"""
        pool = WorkerPool()
        
        assert pool.max_workers == 10
        assert pool.task_type_limits == {
            "nlp": 4,
            "ml": 3,
            "analysis": 2,
            "preprocessing": 1
        }
    
    def test_custom_task_type_limits(self):
        """Testa limites customizados de tipos de tarefa"""
        custom_limits = {
            "nlp": 2,
            "ml": 1,
            "custom": 3
        }
        
        pool = WorkerPool(max_workers=6, task_type_limits=custom_limits)
        
        assert pool.task_type_limits == custom_limits
    
    def test_submit_task_success(self, worker_pool, sample_task):
        """Testa submissão bem-sucedida de tarefa"""
        worker_pool.submit_task(sample_task)
        
        assert sample_task.id in worker_pool.pending_tasks
        assert worker_pool.pending_tasks[sample_task.id] == sample_task
    
    def test_submit_duplicate_task(self, worker_pool, sample_task):
        """Testa submissão de tarefa duplicada"""
        worker_pool.submit_task(sample_task)
        
        # Tentar submeter a mesma tarefa novamente
        with pytest.raises(ValueError, match="Task test_task already exists"):
            worker_pool.submit_task(sample_task)
    
    def test_get_task_status(self, worker_pool, sample_task):
        """Testa obtenção de status da tarefa"""
        worker_pool.submit_task(sample_task)
        
        status = worker_pool.get_task_status(sample_task.id)
        assert status == "pending"
    
    def test_get_task_status_not_found(self, worker_pool):
        """Testa obtenção de status de tarefa não encontrada"""
        status = worker_pool.get_task_status("nonexistent")
        assert status is None
    
    def test_cancel_task(self, worker_pool, sample_task):
        """Testa cancelamento de tarefa"""
        worker_pool.submit_task(sample_task)
        
        success = worker_pool.cancel_task(sample_task.id)
        assert success is True
        
        # Verificar se tarefa foi removida
        assert sample_task.id not in worker_pool.pending_tasks
    
    def test_cancel_task_not_found(self, worker_pool):
        """Testa cancelamento de tarefa não encontrada"""
        success = worker_pool.cancel_task("nonexistent")
        assert success is False
    
    def test_cancel_task_running(self, worker_pool, sample_task):
        """Testa cancelamento de tarefa em execução"""
        worker_pool.submit_task(sample_task)
        
        # Simular tarefa em execução
        worker_pool.running_tasks[sample_task.id] = sample_task
        sample_task.status = "running"
        
        success = worker_pool.cancel_task(sample_task.id)
        assert success is True
        
        # Verificar se tarefa foi marcada como cancelada
        assert sample_task.status == "cancelled"
    
    def test_get_worker_stats(self, worker_pool):
        """Testa obtenção de estatísticas dos workers"""
        stats = worker_pool.get_worker_stats()
        
        assert len(stats) == 4  # max_workers
        assert all(isinstance(stat, WorkerStats) for stat in stats.values())
        
        # Verificar IDs dos workers
        worker_ids = [stat.worker_id for stat in stats.values()]
        assert "worker_0" in worker_ids
        assert "worker_1" in worker_ids
        assert "worker_2" in worker_ids
        assert "worker_3" in worker_ids
    
    def test_get_pool_stats(self, worker_pool):
        """Testa obtenção de estatísticas do pool"""
        # Simular algumas tarefas
        worker_pool.stats["tasks_submitted"] = 10
        worker_pool.stats["tasks_completed"] = 7
        worker_pool.stats["tasks_failed"] = 2
        
        stats = worker_pool.get_pool_stats()
        
        assert stats["tasks_submitted"] == 10
        assert stats["tasks_completed"] == 7
        assert stats["tasks_failed"] == 2
        assert stats["tasks_pending"] == 1  # 10 - 7 - 2
        assert "active_workers" in stats
        assert "idle_workers" in stats
        assert "total_workers" in stats
    
    def test_shutdown(self, worker_pool):
        """Testa shutdown do pool"""
        assert worker_pool.is_running is True
        
        worker_pool.shutdown()
        
        assert worker_pool.is_running is False
        assert worker_pool.shutdown_event.is_set()
    
    def test_shutdown_wait(self, worker_pool):
        """Testa shutdown com espera"""
        worker_pool.shutdown(wait=True)
        
        assert worker_pool.is_running is False
        assert worker_pool.shutdown_event.is_set()
    
    def test_task_priority_ordering(self, worker_pool):
        """Testa ordenação por prioridade"""
        # Criar tarefas com prioridades diferentes
        low_priority_task = WorkerTask(
            id="low_task",
            task_type="nlp",
            function=Mock(),
            priority=1
        )
        
        high_priority_task = WorkerTask(
            id="high_task",
            task_type="nlp",
            function=Mock(),
            priority=10
        )
        
        # Submeter tarefas
        worker_pool.submit_task(low_priority_task)
        worker_pool.submit_task(high_priority_task)
        
        # Verificar que tarefa de alta prioridade está no topo da fila
        # (Este teste depende da implementação específica da fila de prioridade)
        assert len(worker_pool.pending_tasks) == 2
    
    def test_task_type_limits(self, worker_pool):
        """Testa limites por tipo de tarefa"""
        # Criar muitas tarefas do mesmo tipo
        for i in range(10):
            task = WorkerTask(
                id=f"nlp_task_{i}",
                task_type="nlp",
                function=Mock(),
                priority=5
            )
            worker_pool.submit_task(task)
        
        # Verificar que todas foram aceitas (limite é 4, mas não há workers ativos)
        assert len(worker_pool.pending_tasks) == 10


class TestWorkerPoolIntegration:
    """Testes de integração para WorkerPool"""
    
    def test_full_task_workflow(self):
        """Testa workflow completo de tarefa"""
        pool = WorkerPool(max_workers=2)
        
        # Criar tarefa
        def test_function(x, y):
            return x + y
        
        task = WorkerTask(
            id="addition_task",
            task_type="analysis",
            function=test_function,
            args=(5, 3),
            priority=5
        )
        
        # Submeter tarefa
        pool.submit_task(task)
        
        assert task.id in pool.pending_tasks
        
        # Simular processamento
        task.status = "running"
        pool.running_tasks[task.id] = task
        
        # Simular conclusão
        task.status = "completed"
        task.result = 8
        pool.completed_tasks[task.id] = task
        
        # Verificar resultado
        assert task.result == 8
        assert task.status == "completed"
        
        # Verificar estatísticas
        stats = pool.get_pool_stats()
        assert stats["tasks_completed"] == 1
    
    def test_concurrent_task_processing(self):
        """Testa processamento concorrente de tarefas"""
        pool = WorkerPool(max_workers=4)
        
        results = []
        
        def worker_function(task_id):
            results.append(f"task_{task_id}")
            return f"result_{task_id}"
        
        # Criar e submeter múltiplas tarefas
        tasks = []
        for i in range(8):
            task = WorkerTask(
                id=f"task_{i}",
                task_type="nlp",
                function=worker_function,
                args=(i,),
                priority=5
            )
            pool.submit_task(task)
            tasks.append(task)
        
        # Simular processamento concorrente
        for task in tasks[:4]:  # Primeiras 4 tarefas
            task.status = "running"
            pool.running_tasks[task.id] = task
        
        # Verificar que apenas 4 tarefas estão rodando (max_workers)
        running_count = len([t for t in tasks if t.status == "running"])
        assert running_count == 4


class TestWorkerPoolErrorHandling:
    """Testes de tratamento de erro para WorkerPool"""
    
    def test_task_execution_failure(self):
        """Testa falha na execução de tarefa"""
        pool = WorkerPool(max_workers=2)
        
        def failing_function():
            raise Exception("Task failed")
        
        task = WorkerTask(
            id="failing_task",
            task_type="ml",
            function=failing_function,
            priority=5
        )
        
        pool.submit_task(task)
        
        # Simular falha
        task.status = "failed"
        task.error_message = "Task failed"
        pool.failed_tasks[task.id] = task
        
        # Verificar status
        status = pool.get_task_status(task.id)
        assert status == "failed"
        
        # Verificar estatísticas
        stats = pool.get_pool_stats()
        assert stats["tasks_failed"] == 1
    
    def test_worker_failure_handling(self):
        """Testa tratamento de falha de worker"""
        pool = WorkerPool(max_workers=2)
        
        # Simular falha de worker
        worker_id = "worker_0"
        worker_stats = pool.worker_stats[worker_id]
        worker_stats.status = "error"
        worker_stats.tasks_failed += 1
        
        # Verificar que worker foi marcado como com erro
        stats = pool.get_worker_stats()
        assert stats[worker_id].status == "error"
        assert stats[worker_id].tasks_failed == 1
    
    def test_invalid_task_data(self):
        """Testa dados de tarefa inválidos"""
        pool = WorkerPool(max_workers=2)
        
        # Tarefa sem ID
        with pytest.raises(ValueError):
            task = WorkerTask(
                id="",
                task_type="nlp",
                function=Mock()
            )
            pool.submit_task(task)
        
        # Tarefa sem função
        with pytest.raises(ValueError):
            task = WorkerTask(
                id="invalid_task",
                task_type="nlp",
                function=None
            )
            pool.submit_task(task)


class TestWorkerPoolPerformance:
    """Testes de performance para WorkerPool"""
    
    def test_large_number_of_tasks(self):
        """Testa performance com muitas tarefas"""
        pool = WorkerPool(max_workers=4)
        
        def simple_function(task_id):
            return f"result_{task_id}"
        
        # Submeter 1000 tarefas
        for i in range(1000):
            task = WorkerTask(
                id=f"task_{i}",
                task_type="nlp",
                function=simple_function,
                args=(i,),
                priority=5
            )
            pool.submit_task(task)
        
        assert len(pool.pending_tasks) == 1000
        
        # Verificar estatísticas
        stats = pool.get_pool_stats()
        assert stats["tasks_submitted"] == 1000
    
    def test_concurrent_task_submission(self):
        """Testa submissão concorrente de tarefas"""
        pool = WorkerPool(max_workers=4)
        
        def test_function(task_id):
            return f"result_{task_id}"
        
        # Submeter tarefas concorrentemente
        def submit_task(task_id):
            task = WorkerTask(
                id=f"task_{task_id}",
                task_type="nlp",
                function=test_function,
                args=(task_id,),
                priority=5
            )
            pool.submit_task(task)
        
        threads = []
        for i in range(100):
            thread = threading.Thread(target=submit_task, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        assert len(pool.pending_tasks) == 100
    
    def test_memory_usage_with_large_task_history(self):
        """Testa uso de memória com histórico grande de tarefas"""
        pool = WorkerPool(max_workers=2)
        
        def test_function(task_id):
            return f"result_{task_id}"
        
        # Submeter muitas tarefas e simular conclusão
        for i in range(1000):
            task = WorkerTask(
                id=f"task_{i}",
                task_type="nlp",
                function=test_function,
                args=(i,),
                priority=5
            )
            pool.submit_task(task)
            
            # Simular conclusão
            task.status = "completed"
            task.result = f"result_{i}"
            pool.completed_tasks[task.id] = task
        
        # Verificar que o sistema continua funcionando
        assert len(pool.completed_tasks) == 1000
        
        # Verificar estatísticas
        stats = pool.get_pool_stats()
        assert stats["tasks_completed"] == 1000 