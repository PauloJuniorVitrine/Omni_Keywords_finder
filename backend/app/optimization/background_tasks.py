"""
Sistema de Tarefas em Background
Otimiza processamento assíncrono através de tarefas em background
"""

import asyncio
import time
import uuid
import json
import logging
from typing import Any, Dict, List, Optional, Callable, Union, Coroutine
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from functools import wraps
import traceback
import weakref
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class TaskPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class TaskType(Enum):
    ASYNC = "async"
    THREAD = "thread"
    PROCESS = "process"
    SCHEDULED = "scheduled"
    PERIODIC = "periodic"


@dataclass
class TaskInfo:
    id: str
    name: str
    task_type: TaskType
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    retry_delay: int = 60  # segundos
    progress: float = 0.0
    metadata: Dict[str, Any] = None


@dataclass
class TaskMetrics:
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    running_tasks: int
    pending_tasks: int
    avg_execution_time: float
    success_rate: float
    total_execution_time: float


class BackgroundTaskManager:
    """
    Gerenciador de tarefas em background
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.tasks: Dict[str, TaskInfo] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.scheduled_tasks: Dict[str, asyncio.Task] = {}
        
        # Executores
        self.thread_executor = ThreadPoolExecutor(
            max_workers=self.config.get('max_thread_workers', 10)
        )
        self.process_executor = ProcessPoolExecutor(
            max_workers=self.config.get('max_process_workers', 4)
        )
        
        # Configurações
        self.max_concurrent_tasks = self.config.get('max_concurrent_tasks', 50)
        self.task_timeout = self.config.get('task_timeout', 300)  # 5 minutos
        self.enable_metrics = self.config.get('enable_metrics', True)
        
        # Métricas
        self.metrics = TaskMetrics(
            total_tasks=0,
            completed_tasks=0,
            failed_tasks=0,
            running_tasks=0,
            pending_tasks=0,
            avg_execution_time=0.0,
            success_rate=0.0,
            total_execution_time=0.0
        )
        
        # Event loop
        self.loop = None
        self.is_running = False
        self._task_lock = asyncio.Lock()
    
    async def start(self):
        """Inicia o gerenciador de tarefas"""
        if self.is_running:
            return
        
        self.loop = asyncio.get_event_loop()
        self.is_running = True
        
        # Iniciar worker principal
        asyncio.create_task(self._worker_loop())
        
        # Iniciar scheduler
        asyncio.create_task(self._scheduler_loop())
        
        # Iniciar cleanup
        asyncio.create_task(self._cleanup_loop())
        
        logger.info("Background task manager started")
    
    async def stop(self):
        """Para o gerenciador de tarefas"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancelar tarefas em execução
        for task in self.running_tasks.values():
            task.cancel()
        
        # Aguardar cancelamento
        if self.running_tasks:
            await asyncio.gather(*self.running_tasks.values(), return_exceptions=True)
        
        # Fechar executores
        self.thread_executor.shutdown(wait=True)
        self.process_executor.shutdown(wait=True)
        
        logger.info("Background task manager stopped")
    
    async def submit_task(self, func: Callable, *args, task_type: TaskType = TaskType.ASYNC,
                         priority: TaskPriority = TaskPriority.NORMAL, name: str = None,
                         max_retries: int = 3, retry_delay: int = 60, **kwargs) -> str:
        """
        Submete uma tarefa para execução
        """
        task_id = str(uuid.uuid4())
        task_name = name or func.__name__
        
        task_info = TaskInfo(
            id=task_id,
            name=task_name,
            task_type=task_type,
            priority=priority,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            max_retries=max_retries,
            retry_delay=retry_delay,
            metadata={'args': args, 'kwargs': kwargs}
        )
        
        async with self._task_lock:
            self.tasks[task_id] = task_info
            self.metrics.total_tasks += 1
            self.metrics.pending_tasks += 1
        
        # Adicionar à fila
        await self.task_queue.put((priority.value, task_id))
        
        logger.info(f"Task submitted: {task_id} ({task_name})")
        return task_id
    
    async def schedule_task(self, func: Callable, delay: Union[int, timedelta],
                           *args, **kwargs) -> str:
        """
        Agenda uma tarefa para execução futura
        """
        if isinstance(delay, timedelta):
            delay_seconds = delay.total_seconds()
        else:
            delay_seconds = delay
        
        task_id = str(uuid.uuid4())
        
        async def delayed_task():
            await asyncio.sleep(delay_seconds)
            await self.submit_task(func, *args, **kwargs)
        
        scheduled_task = asyncio.create_task(delayed_task())
        self.scheduled_tasks[task_id] = scheduled_task
        
        logger.info(f"Task scheduled: {task_id} (delay: {delay_seconds}s)")
        return task_id
    
    async def schedule_periodic_task(self, func: Callable, interval: Union[int, timedelta],
                                   *args, **kwargs) -> str:
        """
        Agenda uma tarefa periódica
        """
        if isinstance(interval, timedelta):
            interval_seconds = interval.total_seconds()
        else:
            interval_seconds = interval
        
        task_id = str(uuid.uuid4())
        
        async def periodic_task():
            while self.is_running:
                try:
                    await self.submit_task(func, *args, **kwargs)
                    await asyncio.sleep(interval_seconds)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in periodic task {task_id}: {e}")
                    await asyncio.sleep(interval_seconds)
        
        periodic_task_obj = asyncio.create_task(periodic_task())
        self.scheduled_tasks[task_id] = periodic_task_obj
        
        logger.info(f"Periodic task scheduled: {task_id} (interval: {interval_seconds}s)")
        return task_id
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancela uma tarefa"""
        async with self._task_lock:
            if task_id in self.tasks:
                task_info = self.tasks[task_id]
                
                if task_info.status == TaskStatus.RUNNING:
                    if task_id in self.running_tasks:
                        self.running_tasks[task_id].cancel()
                
                task_info.status = TaskStatus.CANCELLED
                task_info.completed_at = datetime.now()
                
                self.metrics.pending_tasks = max(0, self.metrics.pending_tasks - 1)
                self.metrics.running_tasks = max(0, self.metrics.running_tasks - 1)
                
                logger.info(f"Task cancelled: {task_id}")
                return True
        
        return False
    
    async def get_task_status(self, task_id: str) -> Optional[TaskInfo]:
        """Obtém status de uma tarefa"""
        return self.tasks.get(task_id)
    
    async def get_task_result(self, task_id: str) -> Any:
        """Obtém resultado de uma tarefa"""
        task_info = await self.get_task_status(task_id)
        if task_info and task_info.status == TaskStatus.COMPLETED:
            return task_info.result
        return None
    
    async def _worker_loop(self):
        """Loop principal do worker"""
        while self.is_running:
            try:
                # Aguardar tarefa da fila
                priority, task_id = await self.task_queue.get()
                
                # Verificar limite de tarefas concorrentes
                if len(self.running_tasks) >= self.max_concurrent_tasks:
                    # Recolocar na fila
                    await self.task_queue.put((priority, task_id))
                    await asyncio.sleep(1)
                    continue
                
                # Executar tarefa
                asyncio.create_task(self._execute_task(task_id))
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in worker loop: {e}")
    
    async def _execute_task(self, task_id: str):
        """Executa uma tarefa"""
        async with self._task_lock:
            if task_id not in self.tasks:
                return
            
            task_info = self.tasks[task_id]
            task_info.status = TaskStatus.RUNNING
            task_info.started_at = datetime.now()
            
            self.metrics.pending_tasks = max(0, self.metrics.pending_tasks - 1)
            self.metrics.running_tasks += 1
        
        start_time = time.time()
        
        try:
            # Executar baseado no tipo
            if task_info.task_type == TaskType.ASYNC:
                result = await self._execute_async_task(task_info)
            elif task_info.task_type == TaskType.THREAD:
                result = await self._execute_thread_task(task_info)
            elif task_info.task_type == TaskType.PROCESS:
                result = await self._execute_process_task(task_info)
            else:
                raise ValueError(f"Unknown task type: {task_info.task_type}")
            
            # Sucesso
            async with self._task_lock:
                task_info.status = TaskStatus.COMPLETED
                task_info.completed_at = datetime.now()
                task_info.result = result
                task_info.progress = 100.0
                
                self.metrics.completed_tasks += 1
                self.metrics.running_tasks = max(0, self.metrics.running_tasks - 1)
            
            execution_time = time.time() - start_time
            self._update_metrics(execution_time, success=True)
            
            logger.info(f"Task completed: {task_id}")
            
        except Exception as e:
            # Falha
            error_msg = str(e)
            logger.error(f"Task failed: {task_id} - {error_msg}")
            
            async with self._task_lock:
                task_info.error = error_msg
                task_info.retry_count += 1
                
                if task_info.retry_count <= task_info.max_retries:
                    task_info.status = TaskStatus.RETRYING
                    # Reagendar para retry
                    asyncio.create_task(self._retry_task(task_id, task_info.retry_delay))
                else:
                    task_info.status = TaskStatus.FAILED
                    task_info.completed_at = datetime.now()
                    
                    self.metrics.failed_tasks += 1
                    self.metrics.running_tasks = max(0, self.metrics.running_tasks - 1)
            
            execution_time = time.time() - start_time
            self._update_metrics(execution_time, success=False)
        
        finally:
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
    
    async def _execute_async_task(self, task_info: TaskInfo) -> Any:
        """Executa tarefa assíncrona"""
        func = task_info.metadata.get('func')
        args = task_info.metadata.get('args', ())
        kwargs = task_info.metadata.get('kwargs', {})
        
        # Criar task com timeout
        task = asyncio.create_task(func(*args, **kwargs))
        self.running_tasks[task_info.id] = task
        
        try:
            result = await asyncio.wait_for(task, timeout=self.task_timeout)
            return result
        except asyncio.TimeoutError:
            task.cancel()
            raise TimeoutError(f"Task {task_info.id} timed out after {self.task_timeout}s")
    
    async def _execute_thread_task(self, task_info: TaskInfo) -> Any:
        """Executa tarefa em thread"""
        func = task_info.metadata.get('func')
        args = task_info.metadata.get('args', ())
        kwargs = task_info.metadata.get('kwargs', {})
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(self.thread_executor, func, *args, **kwargs)
        return result
    
    async def _execute_process_task(self, task_info: TaskInfo) -> Any:
        """Executa tarefa em processo"""
        func = task_info.metadata.get('func')
        args = task_info.metadata.get('args', ())
        kwargs = task_info.metadata.get('kwargs', {})
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(self.process_executor, func, *args, **kwargs)
        return result
    
    async def _retry_task(self, task_id: str, delay: int):
        """Reexecuta tarefa após delay"""
        await asyncio.sleep(delay)
        
        async with self._task_lock:
            if task_id in self.tasks:
                task_info = self.tasks[task_id]
                task_info.status = TaskStatus.PENDING
                self.metrics.pending_tasks += 1
        
        # Recolocar na fila
        await self.task_queue.put((task_info.priority.value, task_id))
    
    async def _scheduler_loop(self):
        """Loop do scheduler"""
        while self.is_running:
            try:
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
    
    async def _cleanup_loop(self):
        """Loop de limpeza"""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # 5 minutos
                await self._cleanup_old_tasks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    async def _cleanup_old_tasks(self):
        """Remove tarefas antigas"""
        cutoff_time = datetime.now() - timedelta(hours=24)  # 24 horas
        
        async with self._task_lock:
            old_tasks = [
                task_id for task_id, task_info in self.tasks.items()
                if task_info.completed_at and task_info.completed_at < cutoff_time
            ]
            
            for task_id in old_tasks:
                del self.tasks[task_id]
        
        if old_tasks:
            logger.info(f"Cleaned up {len(old_tasks)} old tasks")
    
    def _update_metrics(self, execution_time: float, success: bool):
        """Atualiza métricas"""
        if not self.enable_metrics:
            return
        
        self.metrics.total_execution_time += execution_time
        self.metrics.avg_execution_time = (
            self.metrics.total_execution_time / self.metrics.total_tasks
        )
        
        total_completed = self.metrics.completed_tasks + self.metrics.failed_tasks
        if total_completed > 0:
            self.metrics.success_rate = self.metrics.completed_tasks / total_completed
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtém métricas"""
        return asdict(self.metrics)
    
    def get_task_list(self, status: Optional[TaskStatus] = None, limit: int = 100) -> List[TaskInfo]:
        """Obtém lista de tarefas"""
        tasks = list(self.tasks.values())
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        # Ordenar por data de criação (mais recentes primeiro)
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        return tasks[:limit]


# Instância global
task_manager = BackgroundTaskManager()


# Decorators para facilitar uso
def background_task(task_type: TaskType = TaskType.ASYNC, 
                   priority: TaskPriority = TaskPriority.NORMAL,
                   max_retries: int = 3, retry_delay: int = 60):
    """Decorator para marcar função como tarefa em background"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            task_id = await task_manager.submit_task(
                func, *args, task_type=task_type, priority=priority,
                max_retries=max_retries, retry_delay=retry_delay, **kwargs
            )
            return task_id
        return wrapper
    return decorator


def scheduled_task(delay: Union[int, timedelta]):
    """Decorator para tarefa agendada"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            task_id = await task_manager.schedule_task(func, delay, *args, **kwargs)
            return task_id
        return wrapper
    return decorator


def periodic_task(interval: Union[int, timedelta]):
    """Decorator para tarefa periódica"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            task_id = await task_manager.schedule_periodic_task(func, interval, *args, **kwargs)
            return task_id
        return wrapper
    return decorator


# Funções utilitárias
async def submit_background_task(func: Callable, *args, **kwargs) -> str:
    """Submete tarefa em background"""
    return await task_manager.submit_task(func, *args, **kwargs)


async def get_task_status(task_id: str) -> Optional[TaskInfo]:
    """Obtém status da tarefa"""
    return await task_manager.get_task_status(task_id)


async def cancel_background_task(task_id: str) -> bool:
    """Cancela tarefa em background"""
    return await task_manager.cancel_task(task_id)


def get_background_metrics() -> Dict[str, Any]:
    """Obtém métricas das tarefas em background"""
    return task_manager.get_metrics()


def get_background_tasks(status: Optional[TaskStatus] = None, limit: int = 100) -> List[TaskInfo]:
    """Obtém lista de tarefas em background"""
    return task_manager.get_task_list(status, limit)


# Inicialização automática
async def initialize_background_tasks():
    """Inicializa sistema de tarefas em background"""
    await task_manager.start()


async def shutdown_background_tasks():
    """Desliga sistema de tarefas em background"""
    await task_manager.stop() 