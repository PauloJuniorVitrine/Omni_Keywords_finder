"""
Task Queue System
================

This module implements a task queue system with priorities and retry logic
for the Omni Keywords Finder system.

Author: Omni Keywords Finder Team
Date: 2025-01-27
Tracing ID: TASK_QUEUE_20250127_001
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    NORMAL = 5
    HIGH = 8
    CRITICAL = 10


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


@dataclass
class QueueTask:
    """Represents a task in the queue."""
    id: str
    name: str
    function: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    retry_delay: float = 1.0  # seconds
    timeout: Optional[float] = None
    dependencies: List[str] = field(default_factory=list)
    result: Any = None
    error: Optional[Exception] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class QueueConfig:
    """Configuration for task queue."""
    max_concurrent_tasks: int = 10
    max_queue_size: int = 1000
    default_timeout: float = 300.0  # 5 minutes
    default_retry_delay: float = 1.0
    max_retry_delay: float = 60.0
    retry_backoff_factor: float = 2.0
    cleanup_interval: float = 3600.0  # 1 hour
    max_task_history: int = 1000


class TaskQueue:
    """
    Task queue system with priorities, retry logic, and dependency management.
    
    Features:
    - Priority-based task scheduling
    - Automatic retry with exponential backoff
    - Task dependencies
    - Timeout handling
    - Performance monitoring
    - Task history and cleanup
    """
    
    def __init__(self, config: Optional[QueueConfig] = None):
        """Initialize task queue."""
        self.config = config or QueueConfig()
        
        # Task storage
        self.pending_tasks: Dict[str, QueueTask] = {}
        self.running_tasks: Dict[str, QueueTask] = {}
        self.completed_tasks: Dict[str, QueueTask] = {}
        self.failed_tasks: Dict[str, QueueTask] = {}
        
        # Priority queues
        self.priority_queues: Dict[TaskPriority, deque] = {
            priority: deque() for priority in TaskPriority
        }
        
        # Statistics
        self.stats = defaultdict(int)
        self.performance_history = deque(maxlen=100)
        
        # Control flags
        self.is_running = True
        self.shutdown_event = asyncio.Event()
        
        # Start background tasks
        self._start_background_tasks()
        
        logger.info("Task queue system initialized")
    
    def _start_background_tasks(self) -> None:
        """Start background tasks for queue management."""
        asyncio.create_task(self._task_processor())
        asyncio.create_task(self._cleanup_old_tasks())
        asyncio.create_task(self._monitor_queue_health())
    
    async def submit_task(self,
                         name: str,
                         function: Callable,
                         *args,
                         task_id: Optional[str] = None,
                         priority: TaskPriority = TaskPriority.NORMAL,
                         timeout: Optional[float] = None,
                         max_retries: int = 3,
                         retry_delay: float = 1.0,
                         dependencies: Optional[List[str]] = None,
                         tags: Optional[List[str]] = None,
                         **kwargs) -> str:
        """Submit a task to the queue."""
        if not self.is_running:
            raise RuntimeError("Task queue is not running")
        
        # Generate task ID if not provided
        if task_id is None:
            task_id = str(uuid.uuid4())
        
        # Check queue size limit
        total_tasks = (len(self.pending_tasks) + len(self.running_tasks) + 
                      len(self.completed_tasks) + len(self.failed_tasks))
        
        if total_tasks >= self.config.max_queue_size:
            raise RuntimeError("Task queue is full")
        
        # Create task
        task = QueueTask(
            id=task_id,
            name=name,
            function=function,
            args=args,
            kwargs=kwargs,
            priority=priority,
            timeout=timeout or self.config.default_timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
            dependencies=dependencies or [],
            tags=tags or []
        )
        
        # Add to pending tasks
        self.pending_tasks[task_id] = task
        
        # Add to priority queue
        self.priority_queues[priority].append(task_id)
        
        # Update statistics
        self.stats["submitted_tasks"] += 1
        
        logger.info(f"Task {task_id} ({name}) submitted with priority {priority.value}")
        return task_id
    
    async def _task_processor(self) -> None:
        """Main task processing loop."""
        logger.info("Task processor started")
        
        while not self.shutdown_event.is_set():
            try:
                # Check if we can start new tasks
                if len(self.running_tasks) < self.config.max_concurrent_tasks:
                    # Get next task from highest priority queue
                    task = await self._get_next_task()
                    
                    if task:
                        # Start task
                        asyncio.create_task(self._execute_task(task))
                
                # Wait a bit before checking again
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in task processor: {e}")
                await asyncio.sleep(1)
        
        logger.info("Task processor stopped")
    
    async def _get_next_task(self) -> Optional[QueueTask]:
        """Get the next task from the highest priority queue."""
        # Check queues in priority order (highest first)
        for priority in sorted(TaskPriority, key=lambda p: p.value, reverse=True):
            queue = self.priority_queues[priority]
            
            if queue:
                # Find a task with satisfied dependencies
                for _ in range(len(queue)):
                    task_id = queue.popleft()
                    task = self.pending_tasks.get(task_id)
                    
                    if task and self._check_dependencies(task):
                        return task
                    elif task:
                        # Dependencies not met, put back at end
                        queue.append(task_id)
        
        return None
    
    def _check_dependencies(self, task: QueueTask) -> bool:
        """Check if task dependencies are satisfied."""
        for dep_id in task.dependencies:
            if dep_id not in self.completed_tasks:
                return False
        return True
    
    async def _execute_task(self, task: QueueTask) -> None:
        """Execute a single task."""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        
        # Move from pending to running
        if task.id in self.pending_tasks:
            del self.pending_tasks[task.id]
        self.running_tasks[task.id] = task
        
        start_time = time.time()
        
        try:
            logger.info(f"Executing task {task.id} ({task.name})")
            
            # Execute task with timeout
            if task.timeout:
                result = await asyncio.wait_for(
                    self._run_task_function(task),
                    timeout=task.timeout
                )
            else:
                result = await self._run_task_function(task)
            
            # Task completed successfully
            processing_time = time.time() - start_time
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result
            
            # Move to completed tasks
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]
            self.completed_tasks[task.id] = task
            
            # Update statistics
            self.stats["completed_tasks"] += 1
            self._update_performance_history(task, processing_time, True)
            
            logger.info(f"Task {task.id} completed successfully in {processing_time:.2f}s")
            
        except asyncio.TimeoutError:
            # Task timed out
            processing_time = time.time() - start_time
            task.error = TimeoutError(f"Task {task.id} timed out after {task.timeout}s")
            await self._handle_task_failure(task, processing_time)
            
        except Exception as e:
            # Task failed
            processing_time = time.time() - start_time
            task.error = e
            await self._handle_task_failure(task, processing_time)
    
    async def _run_task_function(self, task: QueueTask) -> Any:
        """Run the task function."""
        # Check if function is async
        if asyncio.iscoroutinefunction(task.function):
            return await task.function(*task.args, **task.kwargs)
        else:
            # Run sync function in thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None, task.function, *task.args, **task.kwargs
            )
    
    async def _handle_task_failure(self, task: QueueTask, processing_time: float) -> None:
        """Handle task failure with retry logic."""
        task.retry_count += 1
        
        if task.retry_count <= task.max_retries:
            # Retry task
            task.status = TaskStatus.RETRYING
            retry_delay = min(
                task.retry_delay * (self.config.retry_backoff_factor ** (task.retry_count - 1)),
                self.config.max_retry_delay
            )
            
            logger.info(f"Retrying task {task.id} in {retry_delay:.2f}s (attempt {task.retry_count})")
            
            # Schedule retry
            asyncio.create_task(self._schedule_retry(task, retry_delay))
            
        else:
            # Max retries exceeded
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            
            # Move to failed tasks
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]
            self.failed_tasks[task.id] = task
            
            # Update statistics
            self.stats["failed_tasks"] += 1
            self._update_performance_history(task, processing_time, False)
            
            logger.error(f"Task {task.id} failed after {task.max_retries} retries")
    
    async def _schedule_retry(self, task: QueueTask, delay: float) -> None:
        """Schedule a task for retry."""
        await asyncio.sleep(delay)
        
        if not self.shutdown_event.is_set():
            # Reset task for retry
            task.status = TaskStatus.PENDING
            task.started_at = None
            task.completed_at = None
            task.error = None
            
            # Add back to pending tasks and priority queue
            self.pending_tasks[task.id] = task
            self.priority_queues[task.priority].append(task.id)
    
    async def _cleanup_old_tasks(self) -> None:
        """Clean up old completed and failed tasks."""
        while not self.shutdown_event.is_set():
            try:
                await asyncio.sleep(self.config.cleanup_interval)
                
                cutoff_time = datetime.now() - timedelta(hours=24)  # Keep 24 hours
                
                # Clean up completed tasks
                old_completed = [
                    task_id for task_id, task in self.completed_tasks.items()
                    if task.completed_at and task.completed_at < cutoff_time
                ]
                
                for task_id in old_completed:
                    del self.completed_tasks[task_id]
                
                # Clean up failed tasks
                old_failed = [
                    task_id for task_id, task in self.failed_tasks.items()
                    if task.completed_at and task.completed_at < cutoff_time
                ]
                
                for task_id in old_failed:
                    del self.failed_tasks[task_id]
                
                if old_completed or old_failed:
                    logger.info(f"Cleaned up {len(old_completed)} completed and {len(old_failed)} failed tasks")
                
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
    
    async def _monitor_queue_health(self) -> None:
        """Monitor queue health and performance."""
        while not self.shutdown_event.is_set():
            try:
                await asyncio.sleep(60)  # Check every minute
                
                # Check for stuck tasks
                current_time = datetime.now()
                stuck_tasks = []
                
                for task in self.running_tasks.values():
                    if (task.started_at and 
                        (current_time - task.started_at).total_seconds() > task.timeout * 2):
                        stuck_tasks.append(task.id)
                
                if stuck_tasks:
                    logger.warning(f"Found {len(stuck_tasks)} potentially stuck tasks")
                
                # Log queue statistics
                if self.stats["submitted_tasks"] % 100 == 0:  # Log every 100 tasks
                    stats = self.get_queue_stats()
                    logger.info(f"Queue statistics: {stats}")
                
            except Exception as e:
                logger.error(f"Error in queue health monitor: {e}")
    
    def _update_performance_history(self, task: QueueTask, processing_time: float, success: bool) -> None:
        """Update performance history."""
        self.performance_history.append({
            "task_id": task.id,
            "task_name": task.name,
            "priority": task.priority.value,
            "processing_time": processing_time,
            "success": success,
            "retry_count": task.retry_count,
            "timestamp": datetime.now()
        })
    
    async def get_task_result(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """Get the result of a completed task."""
        start_time = time.time()
        
        while True:
            # Check if task is completed
            if task_id in self.completed_tasks:
                task = self.completed_tasks[task_id]
                return task.result
            
            # Check if task failed
            if task_id in self.failed_tasks:
                task = self.failed_tasks[task_id]
                raise task.error or Exception(f"Task {task_id} failed")
            
            # Check timeout
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Task {task_id} result not available within timeout")
            
            # Wait a bit before checking again
            await asyncio.sleep(0.1)
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task."""
        if task_id in self.pending_tasks:
            task = self.pending_tasks[task_id]
            task.status = TaskStatus.CANCELLED
            
            # Remove from pending tasks and priority queue
            del self.pending_tasks[task_id]
            self.priority_queues[task.priority].remove(task_id)
            
            self.stats["cancelled_tasks"] += 1
            logger.info(f"Task {task_id} cancelled")
            return True
        
        return False
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task."""
        # Check all task collections
        for task_dict in [self.pending_tasks, self.running_tasks, self.completed_tasks, self.failed_tasks]:
            if task_id in task_dict:
                task = task_dict[task_id]
                return {
                    "id": task.id,
                    "name": task.name,
                    "status": task.status.value,
                    "priority": task.priority.value,
                    "created_at": task.created_at.isoformat(),
                    "started_at": task.started_at.isoformat() if task.started_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "retry_count": task.retry_count,
                    "max_retries": task.max_retries,
                    "dependencies": task.dependencies,
                    "tags": task.tags,
                    "error": str(task.error) if task.error else None
                }
        
        return None
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        total_tasks = (self.stats["submitted_tasks"] + 
                      self.stats["completed_tasks"] + 
                      self.stats["failed_tasks"] + 
                      self.stats["cancelled_tasks"])
        
        success_rate = (self.stats["completed_tasks"] / total_tasks * 100) if total_tasks > 0 else 0
        
        # Calculate average processing time
        if self.performance_history:
            successful_tasks = [entry for entry in self.performance_history if entry["success"]]
            if successful_tasks:
                avg_processing_time = sum(
                    entry["processing_time"] for entry in successful_tasks
                ) / len(successful_tasks)
            else:
                avg_processing_time = 0.0
        else:
            avg_processing_time = 0.0
        
        return {
            "submitted_tasks": self.stats["submitted_tasks"],
            "pending_tasks": len(self.pending_tasks),
            "running_tasks": len(self.running_tasks),
            "completed_tasks": self.stats["completed_tasks"],
            "failed_tasks": self.stats["failed_tasks"],
            "cancelled_tasks": self.stats["cancelled_tasks"],
            "success_rate": round(success_rate, 2),
            "avg_processing_time": round(avg_processing_time, 3),
            "max_concurrent_tasks": self.config.max_concurrent_tasks,
            "queue_utilization": len(self.running_tasks) / self.config.max_concurrent_tasks * 100
        }
    
    def shutdown(self, timeout: Optional[float] = None) -> None:
        """Shutdown the task queue gracefully."""
        logger.info("Shutting down task queue...")
        
        self.is_running = False
        self.shutdown_event.set()
        
        # Cancel all pending tasks
        for task_id in list(self.pending_tasks.keys()):
            self.cancel_task(task_id)
        
        logger.info("Task queue shutdown complete")


# Global task queue instance
task_queue: Optional[TaskQueue] = None


def get_task_queue() -> TaskQueue:
    """Get the global task queue instance."""
    global task_queue
    if task_queue is None:
        task_queue = TaskQueue()
    return task_queue


# Example usage and testing
if __name__ == "__main__":
    async def test_task_queue():
        # Initialize task queue
        queue = TaskQueue()
        
        # Define test functions
        async def test_task(name: str, delay: float = 1.0) -> str:
            """Test async task."""
            await asyncio.sleep(delay)
            return f"Task {name} completed"
        
        def sync_test_task(name: str, delay: float = 1.0) -> str:
            """Test sync task."""
            time.sleep(delay)
            return f"Sync task {name} completed"
        
        # Submit tasks
        task1_id = await queue.submit_task(
            "async_task_1", test_task, "async_1", 1.0,
            priority=TaskPriority.HIGH
        )
        
        task2_id = await queue.submit_task(
            "sync_task_1", sync_test_task, "sync_1", 2.0,
            priority=TaskPriority.NORMAL
        )
        
        # Wait for results
        result1 = await queue.get_task_result(task1_id)
        result2 = await queue.get_task_result(task2_id)
        
        print(f"Task 1 Result: {result1}")
        print(f"Task 2 Result: {result2}")
        
        # Get statistics
        stats = queue.get_queue_stats()
        print(f"Queue Statistics: {stats}")
        
        # Shutdown
        queue.shutdown()
    
    # Run test
    asyncio.run(test_task_queue()) 