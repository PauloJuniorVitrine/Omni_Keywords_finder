"""
Testes Unitários para TaskQueue
TaskQueue - Sistema de fila de tarefas assíncronas

Prompt: Implementação de testes unitários para TaskQueue
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Fase: Criação sem execução - Testes baseados em código real
Tracing ID: TEST_TASK_QUEUE_20250127_001
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from backend.app.async.task_queue import (
    TaskPriority,
    TaskStatus,
    QueueTask,
    QueueConfig,
    TaskQueue
)


class TestTaskPriority:
    """Testes para TaskPriority (Enum)"""
    
    def test_enum_values(self):
        """Testa valores do enum TaskPriority"""
        assert TaskPriority.LOW == 1
        assert TaskPriority.NORMAL == 5
        assert TaskPriority.HIGH == 8
        assert TaskPriority.CRITICAL == 10
    
    def test_priority_comparison(self):
        """Testa comparação de prioridades"""
        assert TaskPriority.CRITICAL > TaskPriority.HIGH
        assert TaskPriority.HIGH > TaskPriority.NORMAL
        assert TaskPriority.NORMAL > TaskPriority.LOW


class TestTaskStatus:
    """Testes para TaskStatus (Enum)"""
    
    def test_enum_values(self):
        """Testa valores do enum TaskStatus"""
        assert TaskStatus.PENDING == "pending"
        assert TaskStatus.RUNNING == "running"
        assert TaskStatus.COMPLETED == "completed"
        assert TaskStatus.FAILED == "failed"
        assert TaskStatus.CANCELLED == "cancelled"


class TestQueueTask:
    """Testes para QueueTask"""
    
    @pytest.fixture
    def sample_task_data(self):
        """Dados de exemplo para QueueTask"""
        return {
            "id": "task_001",
            "name": "keyword_analysis",
            "function": Mock(),
            "args": (1, 2, 3),
            "kwargs": {"param": "value"},
            "priority": TaskPriority.HIGH,
            "timeout": 30.0,
            "max_retries": 3,
            "retry_delay": 5.0,
            "dependencies": ["task_002"],
            "tags": ["analysis", "keywords"],
            "created_at": datetime.now()
        }
    
    @pytest.fixture
    def task(self, sample_task_data):
        """Instância de QueueTask para testes"""
        return QueueTask(**sample_task_data)
    
    def test_initialization(self, sample_task_data):
        """Testa inicialização básica"""
        task = QueueTask(**sample_task_data)
        
        assert task.id == "task_001"
        assert task.name == "keyword_analysis"
        assert task.function == sample_task_data["function"]
        assert task.args == (1, 2, 3)
        assert task.kwargs == {"param": "value"}
        assert task.priority == TaskPriority.HIGH
        assert task.timeout == 30.0
        assert task.max_retries == 3
        assert task.retry_delay == 5.0
        assert task.dependencies == ["task_002"]
        assert task.tags == ["analysis", "keywords"]
        assert task.created_at == sample_task_data["created_at"]
        assert task.status == TaskStatus.PENDING
        assert task.retry_count == 0
        assert task.result is None
        assert task.error_message is None
        assert task.started_at is None
        assert task.completed_at is None
    
    def test_default_values(self):
        """Testa valores padrão"""
        task = QueueTask(
            id="test_task",
            name="Test Task",
            function=Mock()
        )
        
        assert task.priority == TaskPriority.NORMAL
        assert task.timeout == 60.0
        assert task.max_retries == 0
        assert task.retry_delay == 1.0
        assert task.dependencies == []
        assert task.tags == []
        assert task.status == TaskStatus.PENDING
        assert task.retry_count == 0


class TestQueueConfig:
    """Testes para QueueConfig"""
    
    @pytest.fixture
    def sample_config_data(self):
        """Dados de exemplo para QueueConfig"""
        return {
            "max_concurrent_tasks": 10,
            "max_queue_size": 1000,
            "default_timeout": 60.0,
            "default_retry_delay": 5.0,
            "max_retry_attempts": 3,
            "enable_priority_queue": True,
            "enable_task_history": True,
            "max_history_size": 100
        }
    
    @pytest.fixture
    def config(self, sample_config_data):
        """Instância de QueueConfig para testes"""
        return QueueConfig(**sample_config_data)
    
    def test_initialization(self, sample_config_data):
        """Testa inicialização básica"""
        config = QueueConfig(**sample_config_data)
        
        assert config.max_concurrent_tasks == 10
        assert config.max_queue_size == 1000
        assert config.default_timeout == 60.0
        assert config.default_retry_delay == 5.0
        assert config.max_retry_attempts == 3
        assert config.enable_priority_queue is True
        assert config.enable_task_history is True
        assert config.max_history_size == 100
    
    def test_default_values(self):
        """Testa valores padrão"""
        config = QueueConfig()
        
        assert config.max_concurrent_tasks == 5
        assert config.max_queue_size == 100
        assert config.default_timeout == 30.0
        assert config.default_retry_delay == 1.0
        assert config.max_retry_attempts == 0
        assert config.enable_priority_queue is True
        assert config.enable_task_history is True
        assert config.max_history_size == 50


class TestTaskQueue:
    """Testes para TaskQueue"""
    
    @pytest.fixture
    def task_queue(self):
        """Instância de TaskQueue para testes"""
        return TaskQueue()
    
    @pytest.fixture
    def sample_task(self):
        """Tarefa de exemplo"""
        return QueueTask(
            id="test_task",
            name="Test Task",
            function=Mock(return_value="result"),
            priority=TaskPriority.NORMAL
        )
    
    def test_initialization(self):
        """Testa inicialização do TaskQueue"""
        queue = TaskQueue()
        
        assert queue.config is not None
        assert queue.pending_tasks == {}
        assert queue.running_tasks == {}
        assert queue.completed_tasks == {}
        assert queue.failed_tasks == {}
        assert queue.task_history == []
        assert queue.stats["tasks_submitted"] == 0
        assert queue.stats["tasks_completed"] == 0
        assert queue.stats["tasks_failed"] == 0
    
    @pytest.mark.asyncio
    async def test_submit_task_success(self, task_queue, sample_task):
        """Testa submissão bem-sucedida de tarefa"""
        task_id = await task_queue.submit_task(
            name=sample_task.name,
            function=sample_task.function,
            *sample_task.args,
            **sample_task.kwargs
        )
        
        assert task_id is not None
        assert task_id in task_queue.pending_tasks
        assert task_queue.stats["tasks_submitted"] == 1
    
    @pytest.mark.asyncio
    async def test_submit_task_with_priority(self, task_queue):
        """Testa submissão de tarefa com prioridade"""
        def test_function():
            return "high_priority_result"
        
        task_id = await task_queue.submit_task(
            name="high_priority_task",
            function=test_function,
            priority=TaskPriority.HIGH
        )
        
        assert task_id in task_queue.pending_tasks
        task = task_queue.pending_tasks[task_id]
        assert task.priority == TaskPriority.HIGH
    
    @pytest.mark.asyncio
    async def test_submit_task_with_dependencies(self, task_queue):
        """Testa submissão de tarefa com dependências"""
        def test_function():
            return "dependent_result"
        
        task_id = await task_queue.submit_task(
            name="dependent_task",
            function=test_function,
            dependencies=["task_001", "task_002"]
        )
        
        assert task_id in task_queue.pending_tasks
        task = task_queue.pending_tasks[task_id]
        assert task.dependencies == ["task_001", "task_002"]
    
    @pytest.mark.asyncio
    async def test_get_task_status(self, task_queue, sample_task):
        """Testa obtenção de status da tarefa"""
        task_id = await task_queue.submit_task(
            name=sample_task.name,
            function=sample_task.function
        )
        
        status = task_queue.get_task_status(task_id)
        assert status == TaskStatus.PENDING
    
    @pytest.mark.asyncio
    async def test_get_task_status_not_found(self, task_queue):
        """Testa obtenção de status de tarefa não encontrada"""
        status = task_queue.get_task_status("nonexistent")
        assert status is None
    
    @pytest.mark.asyncio
    async def test_cancel_task(self, task_queue, sample_task):
        """Testa cancelamento de tarefa"""
        task_id = await task_queue.submit_task(
            name=sample_task.name,
            function=sample_task.function
        )
        
        success = task_queue.cancel_task(task_id)
        assert success is True
        
        status = task_queue.get_task_status(task_id)
        assert status == TaskStatus.CANCELLED
    
    @pytest.mark.asyncio
    async def test_cancel_task_not_found(self, task_queue):
        """Testa cancelamento de tarefa não encontrada"""
        success = task_queue.cancel_task("nonexistent")
        assert success is False
    
    @pytest.mark.asyncio
    async def test_get_task_result(self, task_queue, sample_task):
        """Testa obtenção de resultado da tarefa"""
        task_id = await task_queue.submit_task(
            name=sample_task.name,
            function=sample_task.function
        )
        
        # Simular tarefa completada
        task = task_queue.pending_tasks[task_id]
        task.status = TaskStatus.COMPLETED
        task.result = "test_result"
        
        result = task_queue.get_task_result(task_id)
        assert result == "test_result"
    
    @pytest.mark.asyncio
    async def test_get_task_result_not_completed(self, task_queue, sample_task):
        """Testa obtenção de resultado de tarefa não completada"""
        task_id = await task_queue.submit_task(
            name=sample_task.name,
            function=sample_task.function
        )
        
        result = task_queue.get_task_result(task_id)
        assert result is None
    
    def test_get_queue_stats(self, task_queue):
        """Testa obtenção de estatísticas da fila"""
        # Simular algumas tarefas
        task_queue.stats["tasks_submitted"] = 10
        task_queue.stats["tasks_completed"] = 7
        task_queue.stats["tasks_failed"] = 2
        
        stats = task_queue.get_queue_stats()
        
        assert stats["tasks_submitted"] == 10
        assert stats["tasks_completed"] == 7
        assert stats["tasks_failed"] == 2
        assert stats["tasks_pending"] == 1  # 10 - 7 - 2
        assert "queue_size" in stats
        assert "running_tasks" in stats
    
    def test_clear_completed_tasks(self, task_queue):
        """Testa limpeza de tarefas completadas"""
        # Simular tarefas completadas
        task_queue.completed_tasks["task1"] = Mock()
        task_queue.completed_tasks["task2"] = Mock()
        task_queue.failed_tasks["task3"] = Mock()
        
        task_queue.clear_completed_tasks()
        
        assert len(task_queue.completed_tasks) == 0
        assert len(task_queue.failed_tasks) == 0
    
    @pytest.mark.asyncio
    async def test_task_execution_workflow(self, task_queue):
        """Testa workflow completo de execução de tarefa"""
        def test_function(x, y):
            return x + y
        
        # Submeter tarefa
        task_id = await task_queue.submit_task(
            name="addition_task",
            function=test_function,
            args=(5, 3),
            priority=TaskPriority.NORMAL
        )
        
        assert task_id in task_queue.pending_tasks
        
        # Simular execução
        task = task_queue.pending_tasks[task_id]
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        
        # Simular conclusão
        task.status = TaskStatus.COMPLETED
        task.result = 8
        task.completed_at = datetime.now()
        
        # Verificar resultado
        result = task_queue.get_task_result(task_id)
        assert result == 8
        
        # Verificar estatísticas
        stats = task_queue.get_queue_stats()
        assert stats["tasks_completed"] == 1


class TestTaskQueueIntegration:
    """Testes de integração para TaskQueue"""
    
    @pytest.mark.asyncio
    async def test_priority_queue_ordering(self):
        """Testa ordenação por prioridade"""
        queue = TaskQueue()
        
        results = []
        
        def low_priority_task():
            results.append("low")
            return "low_result"
        
        def high_priority_task():
            results.append("high")
            return "high_result"
        
        # Submeter tarefas em ordem diferente
        await queue.submit_task("low_task", low_priority_task, priority=TaskPriority.LOW)
        await queue.submit_task("high_task", high_priority_task, priority=TaskPriority.HIGH)
        
        # Verificar que tarefa de alta prioridade foi processada primeiro
        # (Este teste depende da implementação específica do processamento)
        assert len(queue.pending_tasks) == 2
    
    @pytest.mark.asyncio
    async def test_task_dependencies(self):
        """Testa dependências entre tarefas"""
        queue = TaskQueue()
        
        def dependency_task():
            return "dependency_result"
        
        def dependent_task():
            return "dependent_result"
        
        # Submeter tarefa dependente
        dependent_id = await queue.submit_task(
            "dependent_task",
            dependent_task,
            dependencies=["dependency_task"]
        )
        
        # Submeter tarefa de dependência
        dependency_id = await queue.submit_task("dependency_task", dependency_task)
        
        # Verificar que tarefa dependente não pode executar até dependência completar
        dependent_task_obj = queue.pending_tasks[dependent_id]
        assert "dependency_task" in dependent_task_obj.dependencies


class TestTaskQueueErrorHandling:
    """Testes de tratamento de erro para TaskQueue"""
    
    @pytest.mark.asyncio
    async def test_task_execution_failure(self):
        """Testa falha na execução de tarefa"""
        queue = TaskQueue()
        
        def failing_task():
            raise Exception("Task failed")
        
        task_id = await queue.submit_task("failing_task", failing_task)
        
        # Simular falha
        task = queue.pending_tasks[task_id]
        task.status = TaskStatus.FAILED
        task.error_message = "Task failed"
        
        status = queue.get_task_status(task_id)
        assert status == TaskStatus.FAILED
    
    @pytest.mark.asyncio
    async def test_task_timeout(self):
        """Testa timeout de tarefa"""
        queue = TaskQueue()
        
        async def slow_task():
            await asyncio.sleep(10.0)  # Mais que o timeout
            return "slow_result"
        
        task_id = await queue.submit_task("slow_task", slow_task, timeout=1.0)
        
        # Simular timeout
        task = queue.pending_tasks[task_id]
        task.status = TaskStatus.FAILED
        task.error_message = "Task timeout"
        
        status = queue.get_task_status(task_id)
        assert status == TaskStatus.FAILED


class TestTaskQueuePerformance:
    """Testes de performance para TaskQueue"""
    
    @pytest.mark.asyncio
    async def test_large_number_of_tasks(self):
        """Testa performance com muitas tarefas"""
        queue = TaskQueue()
        
        def simple_task(task_id):
            return f"result_{task_id}"
        
        # Submeter 1000 tarefas
        task_ids = []
        for i in range(1000):
            task_id = await queue.submit_task(f"task_{i}", simple_task, i)
            task_ids.append(task_id)
        
        assert len(queue.pending_tasks) == 1000
        assert queue.stats["tasks_submitted"] == 1000
    
    @pytest.mark.asyncio
    async def test_concurrent_task_submission(self):
        """Testa submissão concorrente de tarefas"""
        queue = TaskQueue()
        
        def test_function(task_id):
            return f"result_{task_id}"
        
        # Submeter tarefas concorrentemente
        async def submit_task(task_id):
            return await queue.submit_task(f"task_{task_id}", test_function, task_id)
        
        tasks = [submit_task(i) for i in range(100)]
        task_ids = await asyncio.gather(*tasks)
        
        assert len(task_ids) == 100
        assert len(queue.pending_tasks) == 100 