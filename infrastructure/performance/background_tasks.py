"""
Módulo de Tarefas em Background para Sistemas Enterprise
Sistema de agendamento e execução de tarefas assíncronas - Omni Keywords Finder

Prompt: Implementação de sistema de tarefas em background enterprise
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import statistics
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import pickle
import base64
import traceback

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Status das tarefas."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"
    SCHEDULED = "scheduled"


class TaskPriority(Enum):
    """Prioridades das tarefas."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    URGENT = 5


class TaskType(Enum):
    """Tipos de tarefas."""
    DATA_PROCESSING = "data_processing"
    EMAIL_SENDING = "email_sending"
    REPORT_GENERATION = "report_generation"
    DATA_SYNC = "data_sync"
    CLEANUP = "cleanup"
    BACKUP = "backup"
    ANALYSIS = "analysis"
    NOTIFICATION = "notification"
    CUSTOM = "custom"


@dataclass
class TaskConfig:
    """Configuração de uma tarefa."""
    name: str
    task_type: TaskType
    priority: TaskPriority = TaskPriority.NORMAL
    max_retries: int = 3
    retry_delay: int = 60  # segundos
    timeout: int = 300  # segundos
    max_workers: int = 4
    enable_logging: bool = True
    enable_metrics: bool = True
    enable_notifications: bool = False
    notification_emails: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validações pós-inicialização."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Nome da tarefa não pode ser vazio")
        if self.max_retries < 0:
            raise ValueError("Max retries não pode ser negativo")
        if self.retry_delay < 0:
            raise ValueError("Retry delay não pode ser negativo")
        if self.timeout < 1:
            raise ValueError("Timeout deve ser pelo menos 1 segundo")
        if self.max_workers < 1:
            raise ValueError("Max workers deve ser pelo menos 1")
        
        # Normalizar campos
        self.name = self.name.strip()
        self.notification_emails = [email.strip() for email in self.notification_emails if email.strip()]


@dataclass
class Task:
    """Representa uma tarefa em background."""
    id: str
    name: str
    task_type: TaskType
    function: Callable
    args: Tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    config: TaskConfig = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    created_at: datetime = field(default_factory=datetime.utcnow)
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    retry_delay: int = 60
    timeout: int = 300
    result: Any = None
    error: Optional[str] = None
    error_traceback: Optional[str] = None
    progress: float = 0.0  # 0-100
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validações pós-inicialização."""
        if not self.id or len(self.id.strip()) == 0:
            raise ValueError("ID da tarefa não pode ser vazio")
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Nome da tarefa não pode ser vazio")
        if self.retry_count < 0:
            raise ValueError("Retry count não pode ser negativo")
        if self.max_retries < 0:
            raise ValueError("Max retries não pode ser negativo")
        if self.retry_delay < 0:
            raise ValueError("Retry delay não pode ser negativo")
        if self.timeout < 1:
            raise ValueError("Timeout deve ser pelo menos 1 segundo")
        if not 0 <= self.progress <= 100:
            raise ValueError("Progress deve estar entre 0 e 100")
        
        # Normalizar campos
        self.id = self.id.strip()
        self.name = self.name.strip()
        
        # Aplicar configuração se fornecida
        if self.config:
            self.priority = self.config.priority
            self.max_retries = self.config.max_retries
            self.retry_delay = self.config.retry_delay
            self.timeout = self.config.timeout
            self.tags = self.config.tags.copy()
            self.metadata.update(self.config.metadata)
    
    def is_completed(self) -> bool:
        """Verifica se a tarefa foi concluída."""
        return self.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
    
    def can_retry(self) -> bool:
        """Verifica se a tarefa pode ser retentada."""
        return (self.status == TaskStatus.FAILED and 
                self.retry_count < self.max_retries)
    
    def get_duration(self) -> Optional[timedelta]:
        """Calcula duração da tarefa."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        elif self.started_at:
            return datetime.utcnow() - self.started_at
        return None
    
    def get_wait_time(self) -> Optional[timedelta]:
        """Calcula tempo de espera da tarefa."""
        if self.scheduled_at and self.started_at:
            return self.started_at - self.scheduled_at
        return None


@dataclass
class TaskMetrics:
    """Métricas de tarefas."""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    cancelled_tasks: int = 0
    retried_tasks: int = 0
    avg_duration: float = 0.0  # segundos
    avg_wait_time: float = 0.0  # segundos
    success_rate: float = 0.0  # 0-1
    active_workers: int = 0
    queue_size: int = 0
    last_updated: datetime = field(default_factory=datetime.utcnow)

    def update_success_rate(self) -> None:
        """Atualiza taxa de sucesso."""
        if self.total_tasks > 0:
            self.success_rate = self.completed_tasks / self.total_tasks
        else:
            self.success_rate = 0.0


class BackgroundTaskManager:
    """Gerenciador de tarefas em background enterprise."""
    
    def __init__(self, max_workers: int = 10, enable_monitoring: bool = True):
        """
        Inicializa o gerenciador de tarefas.
        
        Args:
            max_workers: Número máximo de workers
            enable_monitoring: Habilitar monitoramento
        """
        self.max_workers = max_workers
        self.enable_monitoring = enable_monitoring
        
        # Tarefas
        self.tasks: Dict[str, Task] = {}
        self.task_queue: List[Task] = []
        self.scheduled_tasks: List[Task] = []
        
        # Workers
        self.workers: List[asyncio.Task] = []
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=max_workers)
        
        # Configurações
        self.task_configs: Dict[str, TaskConfig] = {}
        self.running = False
        
        # Métricas
        self.metrics = TaskMetrics()
        
        # Callbacks
        self.on_task_complete: Optional[Callable[[Task], None]] = None
        self.on_task_failed: Optional[Callable[[Task], None]] = None
        self.on_task_retry: Optional[Callable[[Task], None]] = None
        
        logger.info(f"BackgroundTaskManager inicializado - Max workers: {max_workers}")
    
    def register_task_config(self, config: TaskConfig) -> None:
        """
        Registra configuração de tarefa.
        
        Args:
            config: Configuração da tarefa
        """
        self.task_configs[config.name] = config
        logger.info(f"Configuração de tarefa registrada: {config.name}")
    
    def submit_task(self, name: str, function: Callable, 
                   task_type: TaskType = TaskType.CUSTOM,
                   args: Tuple = (), kwargs: Dict[str, Any] = None,
                   priority: TaskPriority = TaskPriority.NORMAL,
                   scheduled_at: Optional[datetime] = None,
                   config_name: Optional[str] = None) -> str:
        """
        Submete uma tarefa para execução.
        
        Args:
            name: Nome da tarefa
            function: Função a ser executada
            task_type: Tipo da tarefa
            args: Argumentos posicionais
            kwargs: Argumentos nomeados
            priority: Prioridade da tarefa
            scheduled_at: Data/hora agendada
            config_name: Nome da configuração
            
        Returns:
            ID da tarefa criada
        """
        task_id = str(uuid.uuid4())
        kwargs = kwargs or {}
        
        # Obter configuração
        config = None
        if config_name and config_name in self.task_configs:
            config = self.task_configs[config_name]
        
        # Criar tarefa
        task = Task(
            id=task_id,
            name=name,
            task_type=task_type,
            function=function,
            args=args,
            kwargs=kwargs,
            config=config,
            priority=priority,
            scheduled_at=scheduled_at
        )
        
        # Adicionar à fila apropriada
        if scheduled_at and scheduled_at > datetime.utcnow():
            self.scheduled_tasks.append(task)
            task.status = TaskStatus.SCHEDULED
            logger.info(f"Tarefa agendada: {name} para {scheduled_at}")
        else:
            self._add_to_queue(task)
        
        self.tasks[task_id] = task
        self.metrics.total_tasks += 1
        self.metrics.queue_size = len(self.task_queue)
        
        logger.info(f"Tarefa submetida: {name} (ID: {task_id})")
        return task_id
    
    def _add_to_queue(self, task: Task) -> None:
        """Adiciona tarefa à fila de execução."""
        # Inserir baseado na prioridade
        for i, queued_task in enumerate(self.task_queue):
            if task.priority.value > queued_task.priority.value:
                self.task_queue.insert(i, task)
                break
        else:
            self.task_queue.append(task)
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Obtém uma tarefa pelo ID.
        
        Args:
            task_id: ID da tarefa
            
        Returns:
            Tarefa ou None se não encontrada
        """
        return self.tasks.get(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancela uma tarefa.
        
        Args:
            task_id: ID da tarefa
            
        Returns:
            True se cancelada com sucesso, False caso contrário
        """
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        if task.status in [TaskStatus.PENDING, TaskStatus.SCHEDULED]:
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.utcnow()
            
            # Remover da fila
            if task in self.task_queue:
                self.task_queue.remove(task)
            if task in self.scheduled_tasks:
                self.scheduled_tasks.remove(task)
            
            self.metrics.cancelled_tasks += 1
            self.metrics.queue_size = len(self.task_queue)
            
            logger.info(f"Tarefa cancelada: {task.name} (ID: {task_id})")
            return True
        
        return False
    
    def retry_task(self, task_id: str) -> bool:
        """
        Tenta executar uma tarefa novamente.
        
        Args:
            task_id: ID da tarefa
            
        Returns:
            True se retentada com sucesso, False caso contrário
        """
        task = self.tasks.get(task_id)
        if not task or not task.can_retry():
            return False
        
        task.retry_count += 1
        task.status = TaskStatus.RETRYING
        task.error = None
        task.error_traceback = None
        task.progress = 0.0
        
        # Agendar retry
        retry_at = datetime.utcnow() + timedelta(seconds=task.retry_delay)
        task.scheduled_at = retry_at
        
        self.scheduled_tasks.append(task)
        self.metrics.retried_tasks += 1
        
        if self.on_task_retry:
            self.on_task_retry(task)
        
        logger.info(f"Tarefa agendada para retry: {task.name} (ID: {task_id})")
        return True
    
    async def start(self) -> None:
        """Inicia o gerenciador de tarefas."""
        if self.running:
            return
        
        self.running = True
        
        # Iniciar workers
        for _ in range(self.max_workers):
            worker = asyncio.create_task(self._worker_loop())
            self.workers.append(worker)
        
        # Iniciar scheduler
        scheduler = asyncio.create_task(self._scheduler_loop())
        self.workers.append(scheduler)
        
        # Iniciar monitor
        if self.enable_monitoring:
            monitor = asyncio.create_task(self._monitor_loop())
            self.workers.append(monitor)
        
        logger.info(f"BackgroundTaskManager iniciado - {self.max_workers} workers")
    
    async def stop(self) -> None:
        """Para o gerenciador de tarefas."""
        if not self.running:
            return
        
        self.running = False
        
        # Cancelar workers
        for worker in self.workers:
            worker.cancel()
        
        # Aguardar workers terminarem
        if self.workers:
            await asyncio.gather(*self.workers, return_exceptions=True)
        
        # Fechar pools
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
        
        logger.info("BackgroundTaskManager parado")
    
    async def _worker_loop(self) -> None:
        """Loop principal do worker."""
        while self.running:
            try:
                # Obter próxima tarefa
                task = await self._get_next_task()
                if task:
                    await self._execute_task(task)
                else:
                    await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro no worker loop: {e}")
                await asyncio.sleep(5)
    
    async def _get_next_task(self) -> Optional[Task]:
        """Obtém próxima tarefa da fila."""
        if not self.task_queue:
            return None
        
        return self.task_queue.pop(0)
    
    async def _execute_task(self, task: Task) -> None:
        """Executa uma tarefa."""
        try:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            self.metrics.active_workers += 1
            self.metrics.queue_size = len(self.task_queue)
            
            logger.info(f"Executando tarefa: {task.name} (ID: {task.id})")
            
            # Executar função
            if asyncio.iscoroutinefunction(task.function):
                # Função assíncrona
                result = await asyncio.wait_for(
                    task.function(*task.args, **task.kwargs),
                    timeout=task.timeout
                )
            else:
                # Função síncrona - executar em thread pool
                loop = asyncio.get_event_loop()
                result = await asyncio.wait_for(
                    loop.run_in_executor(
                        self.thread_pool,
                        task.function,
                        *task.args,
                        **task.kwargs
                    ),
                    timeout=task.timeout
                )
            
            # Tarefa concluída com sucesso
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.progress = 100.0
            task.completed_at = datetime.utcnow()
            
            self.metrics.completed_tasks += 1
            
            if self.on_task_complete:
                self.on_task_complete(task)
            
            logger.info(f"Tarefa concluída: {task.name} (ID: {task.id})")
            
        except asyncio.TimeoutError:
            task.status = TaskStatus.FAILED
            task.error = f"Timeout após {task.timeout} segundos"
            task.completed_at = datetime.utcnow()
            
            self.metrics.failed_tasks += 1
            
            if self.on_task_failed:
                self.on_task_failed(task)
            
            logger.error(f"Tarefa timeout: {task.name} (ID: {task.id})")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.error_traceback = traceback.format_exc()
            task.completed_at = datetime.utcnow()
            
            self.metrics.failed_tasks += 1
            
            if self.on_task_failed:
                self.on_task_failed(task)
            
            logger.error(f"Tarefa falhou: {task.name} (ID: {task.id}) - {e}")
            
        finally:
            self.metrics.active_workers -= 1
            self.metrics.queue_size = len(self.task_queue)
            self.metrics.last_updated = datetime.utcnow()
            self.metrics.update_success_rate()
    
    async def _scheduler_loop(self) -> None:
        """Loop do scheduler para tarefas agendadas."""
        while self.running:
            try:
                current_time = datetime.utcnow()
                tasks_to_run = []
                
                # Verificar tarefas agendadas
                for task in self.scheduled_tasks[:]:
                    if task.scheduled_at and task.scheduled_at <= current_time:
                        tasks_to_run.append(task)
                        self.scheduled_tasks.remove(task)
                
                # Adicionar tarefas à fila
                for task in tasks_to_run:
                    task.status = TaskStatus.PENDING
                    self._add_to_queue(task)
                    logger.info(f"Tarefa agendada movida para fila: {task.name}")
                
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro no scheduler loop: {e}")
                await asyncio.sleep(5)
    
    async def _monitor_loop(self) -> None:
        """Loop de monitoramento."""
        while self.running:
            try:
                # Atualizar métricas
                self.metrics.queue_size = len(self.task_queue)
                self.metrics.active_workers = sum(
                    1 for task in self.tasks.values() 
                    if task.status == TaskStatus.RUNNING
                )
                
                # Log de status
                if self.metrics.total_tasks > 0:
                    logger.debug(
                        f"Status: {self.metrics.active_workers} ativas, "
                        f"{self.metrics.queue_size} na fila, "
                        f"Sucesso: {self.metrics.success_rate:.2%}"
                    )
                
                await asyncio.sleep(30)  # Verificar a cada 30 segundos
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro no monitor loop: {e}")
                await asyncio.sleep(30)
    
    def get_tasks(self, status: TaskStatus = None, 
                  task_type: TaskType = None) -> List[Task]:
        """
        Obtém lista de tarefas com filtros opcionais.
        
        Args:
            status: Filtrar por status
            task_type: Filtrar por tipo
            
        Returns:
            Lista de tarefas
        """
        tasks = list(self.tasks.values())
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        if task_type:
            tasks = [t for t in tasks if t.task_type == task_type]
        
        return tasks
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtém métricas do gerenciador."""
        return {
            "total_tasks": self.metrics.total_tasks,
            "completed_tasks": self.metrics.completed_tasks,
            "failed_tasks": self.metrics.failed_tasks,
            "cancelled_tasks": self.metrics.cancelled_tasks,
            "retried_tasks": self.metrics.retried_tasks,
            "avg_duration": self.metrics.avg_duration,
            "avg_wait_time": self.metrics.avg_wait_time,
            "success_rate": self.metrics.success_rate,
            "active_workers": self.metrics.active_workers,
            "queue_size": self.metrics.queue_size,
            "scheduled_tasks": len(self.scheduled_tasks),
            "last_updated": self.metrics.last_updated.isoformat()
        }
    
    def clear_completed_tasks(self, older_than_days: int = 7) -> int:
        """
        Remove tarefas concluídas antigas.
        
        Args:
            older_than_days: Remover tarefas mais antigas que X dias
            
        Returns:
            Número de tarefas removidas
        """
        cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
        tasks_to_remove = []
        
        for task_id, task in self.tasks.items():
            if (task.is_completed() and 
                task.completed_at and 
                task.completed_at < cutoff_date):
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            del self.tasks[task_id]
        
        logger.info(f"Removidas {len(tasks_to_remove)} tarefas antigas")
        return len(tasks_to_remove)


# Função de conveniência para criar task manager
def create_background_task_manager(max_workers: int = 10, 
                                  enable_monitoring: bool = True) -> BackgroundTaskManager:
    """
    Cria um gerenciador de tarefas em background com configurações padrão.
    
    Args:
        max_workers: Número máximo de workers
        enable_monitoring: Habilitar monitoramento
        
    Returns:
        Instância configurada do BackgroundTaskManager
    """
    return BackgroundTaskManager(max_workers, enable_monitoring) 