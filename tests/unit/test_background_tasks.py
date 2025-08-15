"""
Testes Unitários para Background Tasks
Sistema de Tarefas em Background - Omni Keywords Finder

Prompt: Implementação de testes unitários para sistema de tarefas em background
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from infrastructure.performance.background_tasks import (
    BackgroundTaskManager, TaskStatus, TaskPriority, TaskType,
    TaskConfig, Task, TaskMetrics, create_background_task_manager
)


class TestTaskConfig:
    """Testes para TaskConfig"""
    
    def test_task_config_initialization(self):
        """Testa inicialização de TaskConfig"""
        config = TaskConfig(
            name="test-task",
            task_type=TaskType.DATA_PROCESSING,
            priority=TaskPriority.HIGH,
            max_retries=5,
            retry_delay=120,
            timeout=600,
            max_workers=8,
            enable_logging=True,
            enable_metrics=True,
            enable_notifications=True,
            notification_emails=["admin@example.com", "dev@example.com"],
            tags=["critical", "data"],
            metadata={"department": "engineering"}
        )
        
        assert config.name == "test-task"
        assert config.task_type == TaskType.DATA_PROCESSING
        assert config.priority == TaskPriority.HIGH
        assert config.max_retries == 5
        assert config.retry_delay == 120
        assert config.timeout == 600
        assert config.max_workers == 8
        assert config.enable_logging is True
        assert config.enable_metrics is True
        assert config.enable_notifications is True
        assert config.notification_emails == ["admin@example.com", "dev@example.com"]
        assert config.tags == ["critical", "data"]
        assert config.metadata == {"department": "engineering"}
    
    def test_task_config_validation_name_empty(self):
        """Testa validação de nome vazio"""
        with pytest.raises(ValueError, match="Nome da tarefa não pode ser vazio"):
            TaskConfig(name="", task_type=TaskType.CUSTOM)
    
    def test_task_config_validation_max_retries_negative(self):
        """Testa validação de max retries negativo"""
        with pytest.raises(ValueError, match="Max retries não pode ser negativo"):
            TaskConfig(name="test", task_type=TaskType.CUSTOM, max_retries=-1)
    
    def test_task_config_validation_retry_delay_negative(self):
        """Testa validação de retry delay negativo"""
        with pytest.raises(ValueError, match="Retry delay não pode ser negativo"):
            TaskConfig(name="test", task_type=TaskType.CUSTOM, retry_delay=-1)
    
    def test_task_config_validation_timeout_invalid(self):
        """Testa validação de timeout inválido"""
        with pytest.raises(ValueError, match="Timeout deve ser pelo menos 1 segundo"):
            TaskConfig(name="test", task_type=TaskType.CUSTOM, timeout=0)
    
    def test_task_config_validation_max_workers_invalid(self):
        """Testa validação de max workers inválido"""
        with pytest.raises(ValueError, match="Max workers deve ser pelo menos 1"):
            TaskConfig(name="test", task_type=TaskType.CUSTOM, max_workers=0)


class TestTask:
    """Testes para Task"""
    
    @pytest.fixture
    def sample_function(self):
        """Função de exemplo para testes"""
        def test_function(x, y=0):
            return x + y
        return test_function
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo para testes"""
        return TaskConfig(
            name="test-config",
            task_type=TaskType.DATA_PROCESSING,
            priority=TaskPriority.HIGH,
            max_retries=3,
            retry_delay=60,
            timeout=300
        )
    
    def test_task_initialization(self, sample_function):
        """Testa inicialização de Task"""
        task = Task(
            id="task-123",
            name="test-task",
            task_type=TaskType.EMAIL_SENDING,
            function=sample_function,
            args=(10,),
            kwargs={"y": 5},
            priority=TaskPriority.NORMAL,
            retry_count=1,
            max_retries=3,
            retry_delay=60,
            timeout=300,
            progress=50.0,
            tags=["email", "notification"]
        )
        
        assert task.id == "task-123"
        assert task.name == "test-task"
        assert task.task_type == TaskType.EMAIL_SENDING
        assert task.function == sample_function
        assert task.args == (10,)
        assert task.kwargs == {"y": 5}
        assert task.priority == TaskPriority.NORMAL
        assert task.retry_count == 1
        assert task.max_retries == 3
        assert task.retry_delay == 60
        assert task.timeout == 300
        assert task.progress == 50.0
        assert task.tags == ["email", "notification"]
    
    def test_task_initialization_with_config(self, sample_function, sample_config):
        """Testa inicialização de Task com configuração"""
        task = Task(
            id="task-123",
            name="test-task",
            task_type=TaskType.DATA_PROCESSING,
            function=sample_function,
            config=sample_config
        )
        
        # Verificar se configuração foi aplicada
        assert task.priority == TaskPriority.HIGH
        assert task.max_retries == 3
        assert task.retry_delay == 60
        assert task.timeout == 300
        assert task.tags == []
        assert task.metadata == {}
    
    def test_task_validation_id_empty(self, sample_function):
        """Testa validação de ID vazio"""
        with pytest.raises(ValueError, match="ID da tarefa não pode ser vazio"):
            Task(id="", name="test", task_type=TaskType.CUSTOM, function=sample_function)
    
    def test_task_validation_name_empty(self, sample_function):
        """Testa validação de nome vazio"""
        with pytest.raises(ValueError, match="Nome da tarefa não pode ser vazio"):
            Task(id="test", name="", task_type=TaskType.CUSTOM, function=sample_function)
    
    def test_task_validation_retry_count_negative(self, sample_function):
        """Testa validação de retry count negativo"""
        with pytest.raises(ValueError, match="Retry count não pode ser negativo"):
            Task(id="test", name="test", task_type=TaskType.CUSTOM, function=sample_function, retry_count=-1)
    
    def test_task_validation_max_retries_negative(self, sample_function):
        """Testa validação de max retries negativo"""
        with pytest.raises(ValueError, match="Max retries não pode ser negativo"):
            Task(id="test", name="test", task_type=TaskType.CUSTOM, function=sample_function, max_retries=-1)
    
    def test_task_validation_retry_delay_negative(self, sample_function):
        """Testa validação de retry delay negativo"""
        with pytest.raises(ValueError, match="Retry delay não pode ser negativo"):
            Task(id="test", name="test", task_type=TaskType.CUSTOM, function=sample_function, retry_delay=-1)
    
    def test_task_validation_timeout_invalid(self, sample_function):
        """Testa validação de timeout inválido"""
        with pytest.raises(ValueError, match="Timeout deve ser pelo menos 1 segundo"):
            Task(id="test", name="test", task_type=TaskType.CUSTOM, function=sample_function, timeout=0)
    
    def test_task_validation_progress_invalid(self, sample_function):
        """Testa validação de progress inválido"""
        with pytest.raises(ValueError, match="Progress deve estar entre 0 e 100"):
            Task(id="test", name="test", task_type=TaskType.CUSTOM, function=sample_function, progress=150)
    
    def test_is_completed(self, sample_function):
        """Testa verificação se tarefa foi concluída"""
        # Tarefa não concluída
        pending_task = Task(
            id="pending",
            name="pending",
            task_type=TaskType.CUSTOM,
            function=sample_function,
            status=TaskStatus.PENDING
        )
        assert pending_task.is_completed() is False
        
        # Tarefa concluída
        completed_task = Task(
            id="completed",
            name="completed",
            task_type=TaskType.CUSTOM,
            function=sample_function,
            status=TaskStatus.COMPLETED
        )
        assert completed_task.is_completed() is True
        
        # Tarefa falhou
        failed_task = Task(
            id="failed",
            name="failed",
            task_type=TaskType.CUSTOM,
            function=sample_function,
            status=TaskStatus.FAILED
        )
        assert failed_task.is_completed() is True
        
        # Tarefa cancelada
        cancelled_task = Task(
            id="cancelled",
            name="cancelled",
            task_type=TaskType.CUSTOM,
            function=sample_function,
            status=TaskStatus.CANCELLED
        )
        assert cancelled_task.is_completed() is True
    
    def test_can_retry(self, sample_function):
        """Testa verificação se tarefa pode ser retentada"""
        # Tarefa que pode ser retentada
        retryable_task = Task(
            id="retryable",
            name="retryable",
            task_type=TaskType.CUSTOM,
            function=sample_function,
            status=TaskStatus.FAILED,
            retry_count=1,
            max_retries=3
        )
        assert retryable_task.can_retry() is True
        
        # Tarefa que não pode ser retentada (muitas tentativas)
        max_retries_task = Task(
            id="max-retries",
            name="max-retries",
            task_type=TaskType.CUSTOM,
            function=sample_function,
            status=TaskStatus.FAILED,
            retry_count=3,
            max_retries=3
        )
        assert max_retries_task.can_retry() is False
        
        # Tarefa que não pode ser retentada (não falhou)
        not_failed_task = Task(
            id="not-failed",
            name="not-failed",
            task_type=TaskType.CUSTOM,
            function=sample_function,
            status=TaskStatus.COMPLETED
        )
        assert not_failed_task.can_retry() is False
    
    def test_get_duration(self, sample_function):
        """Testa cálculo de duração da tarefa"""
        task = Task(
            id="test",
            name="test",
            task_type=TaskType.CUSTOM,
            function=sample_function,
            started_at=datetime.utcnow() - timedelta(minutes=5),
            completed_at=datetime.utcnow()
        )
        
        duration = task.get_duration()
        assert duration is not None
        assert duration.total_seconds() >= 300  # Pelo menos 5 minutos
    
    def test_get_duration_running(self, sample_function):
        """Testa cálculo de duração de tarefa em execução"""
        task = Task(
            id="test",
            name="test",
            task_type=TaskType.CUSTOM,
            function=sample_function,
            started_at=datetime.utcnow() - timedelta(minutes=2)
        )
        
        duration = task.get_duration()
        assert duration is not None
        assert duration.total_seconds() >= 120  # Pelo menos 2 minutos
    
    def test_get_duration_not_started(self, sample_function):
        """Testa cálculo de duração de tarefa não iniciada"""
        task = Task(
            id="test",
            name="test",
            task_type=TaskType.CUSTOM,
            function=sample_function
        )
        
        duration = task.get_duration()
        assert duration is None
    
    def test_get_wait_time(self, sample_function):
        """Testa cálculo de tempo de espera"""
        scheduled_at = datetime.utcnow() - timedelta(minutes=10)
        started_at = datetime.utcnow() - timedelta(minutes=5)
        
        task = Task(
            id="test",
            name="test",
            task_type=TaskType.CUSTOM,
            function=sample_function,
            scheduled_at=scheduled_at,
            started_at=started_at
        )
        
        wait_time = task.get_wait_time()
        assert wait_time is not None
        assert wait_time.total_seconds() >= 300  # Pelo menos 5 minutos


class TestTaskMetrics:
    """Testes para TaskMetrics"""
    
    def test_task_metrics_initialization(self):
        """Testa inicialização de TaskMetrics"""
        metrics = TaskMetrics(
            total_tasks=100,
            completed_tasks=80,
            failed_tasks=10,
            cancelled_tasks=5,
            retried_tasks=15,
            avg_duration=120.5,
            avg_wait_time=30.2,
            success_rate=0.8,
            active_workers=3,
            queue_size=7
        )
        
        assert metrics.total_tasks == 100
        assert metrics.completed_tasks == 80
        assert metrics.failed_tasks == 10
        assert metrics.cancelled_tasks == 5
        assert metrics.retried_tasks == 15
        assert metrics.avg_duration == 120.5
        assert metrics.avg_wait_time == 30.2
        assert metrics.success_rate == 0.8
        assert metrics.active_workers == 3
        assert metrics.queue_size == 7
    
    def test_update_success_rate_with_tasks(self):
        """Testa atualização de taxa de sucesso com tarefas"""
        metrics = TaskMetrics(
            total_tasks=100,
            completed_tasks=80,
            failed_tasks=10
        )
        
        metrics.update_success_rate()
        assert metrics.success_rate == 0.8
    
    def test_update_success_rate_no_tasks(self):
        """Testa atualização de taxa de sucesso sem tarefas"""
        metrics = TaskMetrics(total_tasks=0)
        
        metrics.update_success_rate()
        assert metrics.success_rate == 0.0


class TestBackgroundTaskManager:
    """Testes para BackgroundTaskManager"""
    
    @pytest.fixture
    def task_manager(self):
        """Instância de BackgroundTaskManager para testes"""
        return BackgroundTaskManager(max_workers=2, enable_monitoring=False)
    
    @pytest.fixture
    def sample_function(self):
        """Função de exemplo para testes"""
        def test_function(x, y=0):
            return x + y
        return test_function
    
    @pytest.fixture
    def async_function(self):
        """Função assíncrona de exemplo para testes"""
        async def test_async_function(x, y=0):
            await asyncio.sleep(0.1)  # Simular trabalho
            return x + y
        return test_async_function
    
    def test_background_task_manager_initialization(self):
        """Testa inicialização do BackgroundTaskManager"""
        manager = BackgroundTaskManager(max_workers=5, enable_monitoring=True)
        
        assert manager.max_workers == 5
        assert manager.enable_monitoring is True
        assert len(manager.tasks) == 0
        assert len(manager.task_queue) == 0
        assert len(manager.scheduled_tasks) == 0
        assert manager.running is False
        assert manager.thread_pool is not None
        assert manager.process_pool is not None
    
    def test_register_task_config(self, task_manager):
        """Testa registro de configuração de tarefa"""
        config = TaskConfig(
            name="test-config",
            task_type=TaskType.DATA_PROCESSING,
            priority=TaskPriority.HIGH
        )
        
        task_manager.register_task_config(config)
        
        assert "test-config" in task_manager.task_configs
        assert task_manager.task_configs["test-config"] == config
    
    def test_submit_task(self, task_manager, sample_function):
        """Testa submissão de tarefa"""
        task_id = task_manager.submit_task(
            name="test-task",
            function=sample_function,
            task_type=TaskType.DATA_PROCESSING,
            args=(10,),
            kwargs={"y": 5},
            priority=TaskPriority.HIGH
        )
        
        assert task_id is not None
        assert task_id in task_manager.tasks
        
        task = task_manager.tasks[task_id]
        assert task.name == "test-task"
        assert task.task_type == TaskType.DATA_PROCESSING
        assert task.function == sample_function
        assert task.args == (10,)
        assert task.kwargs == {"y": 5}
        assert task.priority == TaskPriority.HIGH
        assert task.status == TaskStatus.PENDING
        assert len(task_manager.task_queue) == 1
    
    def test_submit_task_with_config(self, task_manager, sample_function):
        """Testa submissão de tarefa com configuração"""
        # Registrar configuração
        config = TaskConfig(
            name="test-config",
            task_type=TaskType.DATA_PROCESSING,
            priority=TaskPriority.CRITICAL,
            max_retries=5
        )
        task_manager.register_task_config(config)
        
        # Submeter tarefa com configuração
        task_id = task_manager.submit_task(
            name="test-task",
            function=sample_function,
            config_name="test-config"
        )
        
        task = task_manager.tasks[task_id]
        assert task.priority == TaskPriority.CRITICAL
        assert task.max_retries == 5
    
    def test_submit_scheduled_task(self, task_manager, sample_function):
        """Testa submissão de tarefa agendada"""
        scheduled_at = datetime.utcnow() + timedelta(minutes=5)
        
        task_id = task_manager.submit_task(
            name="scheduled-task",
            function=sample_function,
            scheduled_at=scheduled_at
        )
        
        task = task_manager.tasks[task_id]
        assert task.status == TaskStatus.SCHEDULED
        assert task.scheduled_at == scheduled_at
        assert len(task_manager.scheduled_tasks) == 1
        assert len(task_manager.task_queue) == 0
    
    def test_get_task(self, task_manager, sample_function):
        """Testa obtenção de tarefa"""
        task_id = task_manager.submit_task(
            name="test-task",
            function=sample_function
        )
        
        task = task_manager.get_task(task_id)
        assert task is not None
        assert task.name == "test-task"
        
        # Tarefa inexistente
        nonexistent_task = task_manager.get_task("nonexistent")
        assert nonexistent_task is None
    
    def test_cancel_task(self, task_manager, sample_function):
        """Testa cancelamento de tarefa"""
        task_id = task_manager.submit_task(
            name="test-task",
            function=sample_function
        )
        
        success = task_manager.cancel_task(task_id)
        assert success is True
        
        task = task_manager.tasks[task_id]
        assert task.status == TaskStatus.CANCELLED
        assert task.completed_at is not None
        assert len(task_manager.task_queue) == 0
    
    def test_cancel_nonexistent_task(self, task_manager):
        """Testa cancelamento de tarefa inexistente"""
        success = task_manager.cancel_task("nonexistent")
        assert success is False
    
    def test_cancel_running_task(self, task_manager, sample_function):
        """Testa cancelamento de tarefa em execução"""
        task_id = task_manager.submit_task(
            name="test-task",
            function=sample_function
        )
        
        # Simular tarefa em execução
        task = task_manager.tasks[task_id]
        task.status = TaskStatus.RUNNING
        
        success = task_manager.cancel_task(task_id)
        assert success is False  # Não pode cancelar tarefa em execução
    
    def test_retry_task(self, task_manager, sample_function):
        """Testa retry de tarefa"""
        task_id = task_manager.submit_task(
            name="test-task",
            function=sample_function
        )
        
        # Simular tarefa falhada
        task = task_manager.tasks[task_id]
        task.status = TaskStatus.FAILED
        task.retry_count = 1
        task.max_retries = 3
        
        success = task_manager.retry_task(task_id)
        assert success is True
        
        task = task_manager.tasks[task_id]
        assert task.status == TaskStatus.RETRYING
        assert task.retry_count == 2
        assert task.scheduled_at is not None
        assert len(task_manager.scheduled_tasks) == 1
    
    def test_retry_task_max_retries(self, task_manager, sample_function):
        """Testa retry de tarefa com máximo de tentativas"""
        task_id = task_manager.submit_task(
            name="test-task",
            function=sample_function
        )
        
        # Simular tarefa com máximo de tentativas
        task = task_manager.tasks[task_id]
        task.status = TaskStatus.FAILED
        task.retry_count = 3
        task.max_retries = 3
        
        success = task_manager.retry_task(task_id)
        assert success is False
    
    def test_retry_task_not_failed(self, task_manager, sample_function):
        """Testa retry de tarefa que não falhou"""
        task_id = task_manager.submit_task(
            name="test-task",
            function=sample_function
        )
        
        # Tarefa não falhou
        task = task_manager.tasks[task_id]
        task.status = TaskStatus.COMPLETED
        
        success = task_manager.retry_task(task_id)
        assert success is False
    
    def test_get_tasks_no_filters(self, task_manager, sample_function):
        """Testa obtenção de tarefas sem filtros"""
        task_manager.submit_task("task1", sample_function)
        task_manager.submit_task("task2", sample_function)
        
        tasks = task_manager.get_tasks()
        assert len(tasks) == 2
    
    def test_get_tasks_with_status_filter(self, task_manager, sample_function):
        """Testa obtenção de tarefas com filtro de status"""
        task_manager.submit_task("task1", sample_function)
        task_manager.submit_task("task2", sample_function)
        
        # Simular uma tarefa concluída
        task = task_manager.tasks[list(task_manager.tasks.keys())[0]]
        task.status = TaskStatus.COMPLETED
        
        completed_tasks = task_manager.get_tasks(status=TaskStatus.COMPLETED)
        assert len(completed_tasks) == 1
        
        pending_tasks = task_manager.get_tasks(status=TaskStatus.PENDING)
        assert len(pending_tasks) == 1
    
    def test_get_tasks_with_type_filter(self, task_manager, sample_function):
        """Testa obtenção de tarefas com filtro de tipo"""
        task_manager.submit_task("task1", sample_function, task_type=TaskType.DATA_PROCESSING)
        task_manager.submit_task("task2", sample_function, task_type=TaskType.EMAIL_SENDING)
        
        data_tasks = task_manager.get_tasks(task_type=TaskType.DATA_PROCESSING)
        assert len(data_tasks) == 1
        
        email_tasks = task_manager.get_tasks(task_type=TaskType.EMAIL_SENDING)
        assert len(email_tasks) == 1
    
    def test_get_metrics(self, task_manager, sample_function):
        """Testa obtenção de métricas"""
        # Submeter algumas tarefas
        task_manager.submit_task("task1", sample_function)
        task_manager.submit_task("task2", sample_function)
        
        metrics = task_manager.get_metrics()
        
        assert "total_tasks" in metrics
        assert "completed_tasks" in metrics
        assert "failed_tasks" in metrics
        assert "cancelled_tasks" in metrics
        assert "retried_tasks" in metrics
        assert "success_rate" in metrics
        assert "active_workers" in metrics
        assert "queue_size" in metrics
        assert "scheduled_tasks" in metrics
        assert "last_updated" in metrics
    
    def test_clear_completed_tasks(self, task_manager, sample_function):
        """Testa limpeza de tarefas concluídas"""
        # Submeter tarefas
        task_id1 = task_manager.submit_task("task1", sample_function)
        task_id2 = task_manager.submit_task("task2", sample_function)
        
        # Simular tarefas concluídas antigas
        task1 = task_manager.tasks[task_id1]
        task1.status = TaskStatus.COMPLETED
        task1.completed_at = datetime.utcnow() - timedelta(days=10)
        
        task2 = task_manager.tasks[task_id2]
        task2.status = TaskStatus.FAILED
        task2.completed_at = datetime.utcnow() - timedelta(days=5)
        
        # Limpar tarefas mais antigas que 7 dias
        removed_count = task_manager.clear_completed_tasks(older_than_days=7)
        assert removed_count == 1  # Apenas task1 tem mais de 7 dias
        
        assert task_id1 not in task_manager.tasks
        assert task_id2 in task_manager.tasks  # task2 ainda está lá
    
    @pytest.mark.asyncio
    async def test_start_stop_manager(self, task_manager):
        """Testa início e parada do gerenciador"""
        # Iniciar
        await task_manager.start()
        assert task_manager.running is True
        assert len(task_manager.workers) > 0
        
        # Parar
        await task_manager.stop()
        assert task_manager.running is False
    
    @pytest.mark.asyncio
    async def test_execute_sync_task(self, task_manager, sample_function):
        """Testa execução de tarefa síncrona"""
        await task_manager.start()
        
        # Submeter tarefa
        task_id = task_manager.submit_task(
            name="sync-task",
            function=sample_function,
            args=(10,),
            kwargs={"y": 5}
        )
        
        # Aguardar execução
        await asyncio.sleep(0.5)
        
        task = task_manager.get_task(task_id)
        assert task.status == TaskStatus.COMPLETED
        assert task.result == 15
        
        await task_manager.stop()
    
    @pytest.mark.asyncio
    async def test_execute_async_task(self, task_manager, async_function):
        """Testa execução de tarefa assíncrona"""
        await task_manager.start()
        
        # Submeter tarefa assíncrona
        task_id = task_manager.submit_task(
            name="async-task",
            function=async_function,
            args=(20,),
            kwargs={"y": 10}
        )
        
        # Aguardar execução
        await asyncio.sleep(0.5)
        
        task = task_manager.get_task(task_id)
        assert task.status == TaskStatus.COMPLETED
        assert task.result == 30
        
        await task_manager.stop()
    
    @pytest.mark.asyncio
    async def test_task_timeout(self, task_manager):
        """Testa timeout de tarefa"""
        def slow_function():
            import time
            time.sleep(2)  # Função lenta
            return "done"
        
        await task_manager.start()
        
        # Submeter tarefa com timeout curto
        task_id = task_manager.submit_task(
            name="slow-task",
            function=slow_function,
            timeout=1  # 1 segundo de timeout
        )
        
        # Aguardar execução
        await asyncio.sleep(2)
        
        task = task_manager.get_task(task_id)
        assert task.status == TaskStatus.FAILED
        assert "Timeout" in task.error
        
        await task_manager.stop()
    
    @pytest.mark.asyncio
    async def test_task_failure(self, task_manager):
        """Testa falha de tarefa"""
        def failing_function():
            raise ValueError("Test error")
        
        await task_manager.start()
        
        # Submeter tarefa que falha
        task_id = task_manager.submit_task(
            name="failing-task",
            function=failing_function
        )
        
        # Aguardar execução
        await asyncio.sleep(0.5)
        
        task = task_manager.get_task(task_id)
        assert task.status == TaskStatus.FAILED
        assert "Test error" in task.error
        assert task.error_traceback is not None
        
        await task_manager.stop()
    
    @pytest.mark.asyncio
    async def test_scheduled_task_execution(self, task_manager, sample_function):
        """Testa execução de tarefa agendada"""
        await task_manager.start()
        
        # Agendar tarefa para 1 segundo no futuro
        scheduled_at = datetime.utcnow() + timedelta(seconds=1)
        
        task_id = task_manager.submit_task(
            name="scheduled-task",
            function=sample_function,
            args=(5, 3),
            scheduled_at=scheduled_at
        )
        
        # Verificar que está agendada
        task = task_manager.get_task(task_id)
        assert task.status == TaskStatus.SCHEDULED
        
        # Aguardar execução
        await asyncio.sleep(2)
        
        # Verificar que foi executada
        task = task_manager.get_task(task_id)
        assert task.status == TaskStatus.COMPLETED
        assert task.result == 8
        
        await task_manager.stop()


class TestCreateFunctions:
    """Testes para funções de criação"""
    
    def test_create_background_task_manager_default(self):
        """Testa criação de BackgroundTaskManager com configurações padrão"""
        manager = create_background_task_manager()
        
        assert isinstance(manager, BackgroundTaskManager)
        assert manager.max_workers == 10
        assert manager.enable_monitoring is True
    
    def test_create_background_task_manager_custom(self):
        """Testa criação de BackgroundTaskManager com configurações customizadas"""
        manager = create_background_task_manager(max_workers=5, enable_monitoring=False)
        
        assert manager.max_workers == 5
        assert manager.enable_monitoring is False


class TestBackgroundTasksIntegration:
    """Testes de integração para Background Tasks"""
    
    @pytest.mark.asyncio
    async def test_complete_task_workflow(self):
        """Testa workflow completo de tarefas"""
        manager = create_background_task_manager(max_workers=2, enable_monitoring=False)
        
        # Registrar configuração
        config = TaskConfig(
            name="data-processing",
            task_type=TaskType.DATA_PROCESSING,
            priority=TaskPriority.HIGH,
            max_retries=2
        )
        manager.register_task_config(config)
        
        # Função de teste
        def process_data(data, multiplier=1):
            return [x * multiplier for x in data]
        
        await manager.start()
        
        # Submeter tarefas
        task_id1 = manager.submit_task(
            name="process-1",
            function=process_data,
            args=([1, 2, 3],),
            kwargs={"multiplier": 2},
            config_name="data-processing"
        )
        
        task_id2 = manager.submit_task(
            name="process-2",
            function=process_data,
            args=([4, 5, 6],),
            kwargs={"multiplier": 3}
        )
        
        # Aguardar execução
        await asyncio.sleep(1)
        
        # Verificar resultados
        task1 = manager.get_task(task_id1)
        task2 = manager.get_task(task_id2)
        
        assert task1.status == TaskStatus.COMPLETED
        assert task1.result == [2, 4, 6]
        assert task1.priority == TaskPriority.HIGH
        
        assert task2.status == TaskStatus.COMPLETED
        assert task2.result == [12, 15, 18]
        
        # Verificar métricas
        metrics = manager.get_metrics()
        assert metrics["total_tasks"] == 2
        assert metrics["completed_tasks"] == 2
        assert metrics["success_rate"] == 1.0
        
        await manager.stop()
    
    @pytest.mark.asyncio
    async def test_task_retry_workflow(self):
        """Testa workflow de retry de tarefas"""
        manager = create_background_task_manager(max_workers=1, enable_monitoring=False)
        
        # Contador de tentativas
        attempt_count = 0
        
        def failing_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ValueError(f"Attempt {attempt_count}")
            return "success"
        
        await manager.start()
        
        # Submeter tarefa que falha nas primeiras tentativas
        task_id = manager.submit_task(
            name="retry-test",
            function=failing_function,
            max_retries=3,
            retry_delay=0.1  # Delay curto para teste
        )
        
        # Aguardar execução
        await asyncio.sleep(2)
        
        task = manager.get_task(task_id)
        assert task.status == TaskStatus.COMPLETED
        assert task.result == "success"
        assert task.retry_count == 2  # 2 retries + 1 sucesso = 3 tentativas
        
        await manager.stop()
    
    @pytest.mark.asyncio
    async def test_task_priority_workflow(self):
        """Testa workflow de prioridade de tarefas"""
        manager = create_background_task_manager(max_workers=1, enable_monitoring=False)
        
        results = []
        
        def priority_function(name):
            results.append(name)
            return name
        
        await manager.start()
        
        # Submeter tarefas com diferentes prioridades
        manager.submit_task("low", priority_function, priority=TaskPriority.LOW, args=("low",))
        manager.submit_task("high", priority_function, priority=TaskPriority.HIGH, args=("high",))
        manager.submit_task("normal", priority_function, priority=TaskPriority.NORMAL, args=("normal",))
        
        # Aguardar execução
        await asyncio.sleep(1)
        
        # Verificar ordem de execução (HIGH deve ser primeiro)
        assert len(results) == 3
        assert results[0] == "high"  # Prioridade mais alta primeiro
        
        await manager.stop()


if __name__ == "__main__":
    pytest.main([__file__]) 