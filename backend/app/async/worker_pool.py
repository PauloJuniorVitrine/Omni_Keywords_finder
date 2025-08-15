"""
Worker Thread Pool for Async Processing
======================================

This module implements a worker thread pool for asynchronous processing
of NLP and ML tasks in the Omni Keywords Finder system.

Author: Omni Keywords Finder Team
Date: 2025-01-27
Tracing ID: WORKER_POOL_20250127_001
"""

import asyncio
import threading
import time
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, Future
import queue
import weakref

logger = logging.getLogger(__name__)


@dataclass
class WorkerTask:
    """Represents a task to be processed by a worker."""
    id: str
    task_type: str  # "nlp", "ml", "analysis", "preprocessing"
    function: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: int = 5  # 1-10, higher is more important
    created_at: datetime = field(default_factory=datetime.now)
    timeout: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkerStats:
    """Statistics for a worker thread."""
    worker_id: str
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    total_processing_time: float = 0.0
    avg_processing_time: float = 0.0
    last_task_time: Optional[datetime] = None
    current_task: Optional[str] = None
    status: str = "idle"  # idle, busy, error


class WorkerPool:
    """
    Thread pool for processing NLP and ML tasks asynchronously.
    
    Features:
    - Configurable pool size per task type
    - Priority-based task scheduling
    - Task dependencies and retry logic
    - Performance monitoring and statistics
    - Graceful shutdown and resource cleanup
    """
    
    def __init__(self, 
                 max_workers: int = 10,
                 task_type_limits: Optional[Dict[str, int]] = None):
        """Initialize worker pool."""
        self.max_workers = max_workers
        self.task_type_limits = task_type_limits or {
            "nlp": 4,
            "ml": 3,
            "analysis": 2,
            "preprocessing": 1
        }
        
        # Thread pool executor
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="OmniWorker"
        )
        
        # Task management
        self.pending_tasks: Dict[str, WorkerTask] = {}
        self.running_tasks: Dict[str, WorkerTask] = {}
        self.completed_tasks: Dict[str, Any] = {}
        self.failed_tasks: Dict[str, Exception] = {}
        
        # Worker statistics
        self.worker_stats: Dict[str, WorkerStats] = {}
        self.task_queue = queue.PriorityQueue()
        
        # Performance tracking
        self.performance_history = deque(maxlen=100)
        self.start_time = datetime.now()
        
        # Control flags
        self.shutdown_event = threading.Event()
        self.is_running = True
        
        # Start worker threads
        self._start_workers()
        
        logger.info(f"Worker pool initialized with {max_workers} workers")
    
    def _start_workers(self) -> None:
        """Start worker threads."""
        for i in range(self.max_workers):
            worker_id = f"worker_{i}"
            self.worker_stats[worker_id] = WorkerStats(worker_id=worker_id)
            
            # Start worker thread
            thread = threading.Thread(
                target=self._worker_loop,
                args=(worker_id,),
                daemon=True,
                name=f"Worker-{worker_id}"
            )
            thread.start()
    
    def _worker_loop(self, worker_id: str) -> None:
        """Main worker loop for processing tasks."""
        logger.info(f"Worker {worker_id} started")
        
        while not self.shutdown_event.is_set():
            try:
                # Get task from queue with timeout
                try:
                    priority, task_id = self.task_queue.get(timeout=1.0)
                    task = self.pending_tasks.get(task_id)
                    
                    if task is None:
                        continue
                    
                    # Process task
                    self._process_task(worker_id, task)
                    
                except queue.Empty:
                    continue
                    
            except Exception as e:
                logger.error(f"Worker {worker_id} encountered error: {e}")
                self.worker_stats[worker_id].status = "error"
        
        logger.info(f"Worker {worker_id} stopped")
    
    def _process_task(self, worker_id: str, task: WorkerTask) -> None:
        """Process a single task."""
        worker_stats = self.worker_stats[worker_id]
        worker_stats.status = "busy"
        worker_stats.current_task = task.id
        worker_stats.last_task_time = datetime.now()
        
        start_time = time.time()
        
        try:
            # Check dependencies
            if not self._check_dependencies(task):
                logger.warning(f"Task {task.id} dependencies not met, requeuing")
                self._requeue_task(task)
                return
            
            # Execute task
            logger.info(f"Worker {worker_id} processing task {task.id} ({task.task_type})")
            
            # Submit to thread pool
            future = self.executor.submit(task.function, *task.args, **task.kwargs)
            
            # Wait for completion with timeout
            if task.timeout:
                result = future.result(timeout=task.timeout)
            else:
                result = future.result()
            
            # Task completed successfully
            processing_time = time.time() - start_time
            self._update_worker_stats(worker_stats, True, processing_time)
            
            self.completed_tasks[task.id] = result
            logger.info(f"Task {task.id} completed successfully in {processing_time:.2f}s")
            
        except Exception as e:
            # Task failed
            processing_time = time.time() - start_time
            self._update_worker_stats(worker_stats, False, processing_time)
            
            logger.error(f"Task {task.id} failed: {e}")
            
            # Handle retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                logger.info(f"Retrying task {task.id} (attempt {task.retry_count})")
                self._requeue_task(task)
            else:
                self.failed_tasks[task.id] = e
                logger.error(f"Task {task.id} failed after {task.max_retries} retries")
        
        finally:
            # Cleanup
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]
            
            worker_stats.status = "idle"
            worker_stats.current_task = None
    
    def _update_worker_stats(self, worker_stats: WorkerStats, success: bool, processing_time: float) -> None:
        """Update worker statistics."""
        worker_stats.total_tasks += 1
        worker_stats.total_processing_time += processing_time
        worker_stats.avg_processing_time = worker_stats.total_processing_time / worker_stats.total_tasks
        
        if success:
            worker_stats.successful_tasks += 1
        else:
            worker_stats.failed_tasks += 1
        
        # Update performance history
        self.performance_history.append({
            "worker_id": worker_stats.worker_id,
            "processing_time": processing_time,
            "success": success,
            "timestamp": datetime.now()
        })
    
    def _check_dependencies(self, task: WorkerTask) -> bool:
        """Check if task dependencies are met."""
        for dep_id in task.dependencies:
            if dep_id not in self.completed_tasks:
                return False
        return True
    
    def _requeue_task(self, task: WorkerTask) -> None:
        """Requeue a task for retry."""
        # Add back to pending tasks
        self.pending_tasks[task.id] = task
        
        # Add to queue with priority
        priority = task.priority - task.retry_count  # Lower priority for retries
        self.task_queue.put((priority, task.id))
    
    async def submit_task(self, 
                         task_type: str,
                         function: Callable,
                         *args,
                         task_id: Optional[str] = None,
                         priority: int = 5,
                         timeout: Optional[float] = None,
                         dependencies: Optional[List[str]] = None,
                         **kwargs) -> str:
        """Submit a task to the worker pool."""
        if not self.is_running:
            raise RuntimeError("Worker pool is not running")
        
        # Generate task ID if not provided
        if task_id is None:
            task_id = f"{task_type}_{int(time.time() * 1000)}"
        
        # Create task
        task = WorkerTask(
            id=task_id,
            task_type=task_type,
            function=function,
            args=args,
            kwargs=kwargs,
            priority=priority,
            timeout=timeout,
            dependencies=dependencies or []
        )
        
        # Add to pending tasks
        self.pending_tasks[task_id] = task
        
        # Add to queue
        self.task_queue.put((priority, task_id))
        
        logger.info(f"Task {task_id} submitted to worker pool")
        return task_id
    
    async def get_task_result(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """Get the result of a completed task."""
        start_time = time.time()
        
        while True:
            # Check if task is completed
            if task_id in self.completed_tasks:
                return self.completed_tasks[task_id]
            
            # Check if task failed
            if task_id in self.failed_tasks:
                raise self.failed_tasks[task_id]
            
            # Check timeout
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Task {task_id} result not available within timeout")
            
            # Wait a bit before checking again
            await asyncio.sleep(0.1)
    
    async def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """Wait for a task to complete and return its result."""
        return await self.get_task_result(task_id, timeout)
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task."""
        if task_id in self.pending_tasks:
            del self.pending_tasks[task_id]
            logger.info(f"Task {task_id} cancelled")
            return True
        return False
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get worker pool statistics."""
        total_tasks = len(self.completed_tasks) + len(self.failed_tasks) + len(self.running_tasks)
        success_rate = (len(self.completed_tasks) / total_tasks * 100) if total_tasks > 0 else 0
        
        # Calculate average processing time
        if self.performance_history:
            avg_processing_time = sum(
                entry["processing_time"] for entry in self.performance_history
            ) / len(self.performance_history)
        else:
            avg_processing_time = 0.0
        
        return {
            "total_workers": self.max_workers,
            "active_workers": len([w for w in self.worker_stats.values() if w.status == "busy"]),
            "idle_workers": len([w for w in self.worker_stats.values() if w.status == "idle"]),
            "error_workers": len([w for w in self.worker_stats.values() if w.status == "error"]),
            "pending_tasks": len(self.pending_tasks),
            "running_tasks": len(self.running_tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "success_rate": round(success_rate, 2),
            "avg_processing_time": round(avg_processing_time, 3),
            "uptime": str(datetime.now() - self.start_time),
            "task_type_limits": self.task_type_limits
        }
    
    def get_worker_stats(self, worker_id: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for specific worker or all workers."""
        if worker_id:
            if worker_id in self.worker_stats:
                stats = self.worker_stats[worker_id]
                return {
                    "worker_id": stats.worker_id,
                    "status": stats.status,
                    "total_tasks": stats.total_tasks,
                    "successful_tasks": stats.successful_tasks,
                    "failed_tasks": stats.failed_tasks,
                    "avg_processing_time": round(stats.avg_processing_time, 3),
                    "current_task": stats.current_task,
                    "last_task_time": stats.last_task_time.isoformat() if stats.last_task_time else None
                }
            else:
                return {}
        
        # Return all worker stats
        return {
            worker_id: {
                "status": stats.status,
                "total_tasks": stats.total_tasks,
                "successful_tasks": stats.successful_tasks,
                "failed_tasks": stats.failed_tasks,
                "avg_processing_time": round(stats.avg_processing_time, 3),
                "current_task": stats.current_task
            }
            for worker_id, stats in self.worker_stats.items()
        }
    
    def shutdown(self, timeout: Optional[float] = None) -> None:
        """Shutdown the worker pool gracefully."""
        logger.info("Shutting down worker pool...")
        
        self.is_running = False
        self.shutdown_event.set()
        
        # Wait for workers to finish
        if timeout:
            self.shutdown_event.wait(timeout)
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("Worker pool shutdown complete")


# Global worker pool instance
worker_pool: Optional[WorkerPool] = None


def get_worker_pool() -> WorkerPool:
    """Get the global worker pool instance."""
    global worker_pool
    if worker_pool is None:
        worker_pool = WorkerPool()
    return worker_pool


async def submit_nlp_task(function: Callable, *args, **kwargs) -> str:
    """Submit an NLP task to the worker pool."""
    pool = get_worker_pool()
    return await pool.submit_task("nlp", function, *args, **kwargs)


async def submit_ml_task(function: Callable, *args, **kwargs) -> str:
    """Submit an ML task to the worker pool."""
    pool = get_worker_pool()
    return await pool.submit_task("ml", function, *args, **kwargs)


async def submit_analysis_task(function: Callable, *args, **kwargs) -> str:
    """Submit an analysis task to the worker pool."""
    pool = get_worker_pool()
    return await pool.submit_task("analysis", function, *args, **kwargs)


# Example usage and testing
if __name__ == "__main__":
    async def test_worker_pool():
        # Initialize worker pool
        pool = WorkerPool(max_workers=4)
        
        # Define test functions
        def nlp_task(text: str) -> Dict[str, Any]:
            """Simulate NLP processing."""
            time.sleep(1)  # Simulate processing time
            return {
                "text": text,
                "tokens": len(text.split()),
                "sentiment": "positive",
                "keywords": ["test", "nlp", "processing"]
            }
        
        def ml_task(data: List[float]) -> Dict[str, Any]:
            """Simulate ML processing."""
            time.sleep(2)  # Simulate processing time
            return {
                "input_data": data,
                "prediction": sum(data) / len(data),
                "confidence": 0.85,
                "model_version": "1.0"
            }
        
        # Submit tasks
        task1_id = await pool.submit_task("nlp", nlp_task, "This is a test text for NLP processing")
        task2_id = await pool.submit_task("ml", ml_task, [1.0, 2.0, 3.0, 4.0, 5.0])
        
        # Wait for results
        result1 = await pool.wait_for_task(task1_id)
        result2 = await pool.wait_for_task(task2_id)
        
        print(f"NLP Task Result: {result1}")
        print(f"ML Task Result: {result2}")
        
        # Get statistics
        stats = pool.get_pool_stats()
        print(f"Pool Statistics: {stats}")
        
        # Shutdown
        pool.shutdown()
    
    # Run test
    asyncio.run(test_worker_pool()) 