"""
Health Check Scheduler for Omni Keywords Finder

This module provides a scheduler for running health checks at specified intervals,
with support for prioritization, concurrent execution, and integration with
the health check registry.

Author: Paulo Júnior
Date: 2025-01-27
Tracing ID: HEALTH_SCHEDULER_001
"""

import asyncio
import logging
import signal
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
import weakref

from .health_check_registry import health_check_registry, HealthCheckPriority, HealthCheckCategory
from .advanced_health_check import HealthCheckResult, HealthStatus

logger = logging.getLogger(__name__)


class SchedulerState(Enum):
    """Scheduler state enumeration"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class SchedulerConfig:
    """Configuration for the health check scheduler"""
    check_interval_seconds: float = 60.0
    max_concurrent_checks: int = 10
    priority_execution: bool = True
    enable_graceful_shutdown: bool = True
    shutdown_timeout_seconds: float = 30.0
    enable_metrics: bool = True
    enable_notifications: bool = True
    retry_failed_checks: bool = True
    retry_delay_seconds: float = 30.0
    max_retry_attempts: int = 3


@dataclass
class SchedulerMetrics:
    """Metrics for the health check scheduler"""
    total_checks_executed: int = 0
    successful_checks: int = 0
    failed_checks: int = 0
    total_execution_time_ms: float = 0.0
    average_execution_time_ms: float = 0.0
    last_execution_time: Optional[datetime] = None
    scheduler_start_time: Optional[datetime] = None
    scheduler_uptime_seconds: float = 0.0
    concurrent_executions: int = 0
    max_concurrent_executions: int = 0


class HealthCheckScheduler:
    """Scheduler for health checks with prioritization and concurrent execution"""
    
    def __init__(self, config: Optional[SchedulerConfig] = None):
        self.config = config or SchedulerConfig()
        self.state = SchedulerState.STOPPED
        self.metrics = SchedulerMetrics()
        self._running_tasks: Set[asyncio.Task] = set()
        self._scheduler_task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()
        self._execution_semaphore = asyncio.Semaphore(self.config.max_concurrent_checks)
        self._notification_callbacks: List[Callable] = []
        self._error_callbacks: List[Callable] = []
        self._start_time: Optional[datetime] = None
        
        # Setup graceful shutdown
        if self.config.enable_graceful_shutdown:
            self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown")
            asyncio.create_task(self.stop())
        
        try:
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
        except NotImplementedError:
            # Windows doesn't support SIGTERM
            pass
    
    async def start(self) -> bool:
        """Start the health check scheduler"""
        if self.state != SchedulerState.STOPPED:
            logger.warning(f"Scheduler is already in state: {self.state}")
            return False
        
        try:
            self.state = SchedulerState.STARTING
            self._start_time = datetime.utcnow()
            self.metrics.scheduler_start_time = self._start_time
            self._stop_event.clear()
            
            # Start the main scheduler loop
            self._scheduler_task = asyncio.create_task(self._scheduler_loop())
            
            self.state = SchedulerState.RUNNING
            logger.info("Health check scheduler started successfully")
            return True
            
        except Exception as e:
            self.state = SchedulerState.ERROR
            logger.error(f"Failed to start health check scheduler: {str(e)}")
            return False
    
    async def stop(self) -> bool:
        """Stop the health check scheduler gracefully"""
        if self.state not in [SchedulerState.RUNNING, SchedulerState.ERROR]:
            logger.warning(f"Cannot stop scheduler in state: {self.state}")
            return False
        
        try:
            self.state = SchedulerState.STOPPING
            logger.info("Stopping health check scheduler...")
            
            # Signal stop
            self._stop_event.set()
            
            # Cancel scheduler task
            if self._scheduler_task:
                self._scheduler_task.cancel()
                try:
                    await self._scheduler_task
                except asyncio.CancelledError:
                    pass
            
            # Wait for running tasks to complete
            if self._running_tasks:
                logger.info(f"Waiting for {len(self._running_tasks)} running tasks to complete...")
                try:
                    await asyncio.wait_for(
                        asyncio.gather(*self._running_tasks, return_exceptions=True),
                        timeout=self.config.shutdown_timeout_seconds
                    )
                except asyncio.TimeoutError:
                    logger.warning("Timeout waiting for tasks to complete, cancelling remaining tasks")
                    for task in self._running_tasks:
                        task.cancel()
            
            self.state = SchedulerState.STOPPED
            logger.info("Health check scheduler stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping health check scheduler: {str(e)}")
            self.state = SchedulerState.ERROR
            return False
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        logger.info("Health check scheduler loop started")
        
        while not self._stop_event.is_set():
            try:
                # Get due checks
                due_checks = health_check_registry.get_due_checks()
                
                if due_checks:
                    logger.debug(f"Found {len(due_checks)} due health checks")
                    
                    # Prioritize checks if enabled
                    if self.config.priority_execution:
                        due_checks = self._prioritize_checks(due_checks)
                    
                    # Execute checks
                    await self._execute_checks(due_checks)
                
                # Wait for next check interval
                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=self.config.check_interval_seconds
                )
                
            except asyncio.TimeoutError:
                # This is expected, continue the loop
                pass
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}")
                await asyncio.sleep(1)  # Brief pause before retrying
        
        logger.info("Health check scheduler loop stopped")
    
    def _prioritize_checks(self, check_names: List[str]) -> List[str]:
        """Prioritize health checks based on priority and category"""
        priority_order = [
            HealthCheckPriority.CRITICAL,
            HealthCheckPriority.HIGH,
            HealthCheckPriority.MEDIUM,
            HealthCheckPriority.LOW
        ]
        
        categorized_checks = {priority: [] for priority in priority_order}
        
        for name in check_names:
            metadata = health_check_registry.get_metadata(name)
            if metadata:
                categorized_checks[metadata.priority].append(name)
        
        # Return checks in priority order
        prioritized_checks = []
        for priority in priority_order:
            prioritized_checks.extend(categorized_checks[priority])
        
        return prioritized_checks
    
    async def _execute_checks(self, check_names: List[str]):
        """Execute health checks with concurrency control"""
        if not check_names:
            return
        
        # Create tasks for all checks
        tasks = []
        for name in check_names:
            task = asyncio.create_task(self._execute_single_check(name))
            tasks.append(task)
            self._running_tasks.add(task)
        
        # Execute tasks with concurrency control
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(results):
                check_name = check_names[i]
                if isinstance(result, Exception):
                    logger.error(f"Health check '{check_name}' failed with exception: {str(result)}")
                    await self._handle_check_failure(check_name, result)
                else:
                    await self._handle_check_result(check_name, result)
                    
        finally:
            # Clean up tasks
            for task in tasks:
                self._running_tasks.discard(task)
    
    async def _execute_single_check(self, check_name: str) -> HealthCheckResult:
        """Execute a single health check with concurrency control"""
        async with self._execution_semaphore:
            self.metrics.concurrent_executions += 1
            self.metrics.max_concurrent_executions = max(
                self.metrics.max_concurrent_executions,
                self.metrics.concurrent_executions
            )
            
            try:
                health_check = health_check_registry.get_health_check(check_name)
                if not health_check:
                    raise ValueError(f"Health check '{check_name}' not found")
                
                start_time = datetime.utcnow()
                result = await health_check.check()
                execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                # Update metrics
                self.metrics.total_checks_executed += 1
                self.metrics.total_execution_time_ms += execution_time
                self.metrics.average_execution_time_ms = (
                    self.metrics.total_execution_time_ms / self.metrics.total_checks_executed
                )
                self.metrics.last_execution_time = datetime.utcnow()
                
                if result.status == HealthStatus.HEALTHY:
                    self.metrics.successful_checks += 1
                else:
                    self.metrics.failed_checks += 1
                
                # Update registry statistics
                health_check_registry.update_check_statistics(check_name, result)
                
                return result
                
            finally:
                self.metrics.concurrent_executions -= 1
    
    async def _handle_check_result(self, check_name: str, result: HealthCheckResult):
        """Handle successful health check result"""
        metadata = health_check_registry.get_metadata(check_name)
        
        if result.status != HealthStatus.HEALTHY:
            logger.warning(f"Health check '{check_name}' returned status: {result.status.value}")
            
            # Send notifications
            if self.config.enable_notifications:
                await self._send_notification(check_name, result, metadata)
        
        # Log result
        logger.debug(f"Health check '{check_name}' completed: {result.status.value} ({result.duration_ms:.2f}ms)")
    
    async def _handle_check_failure(self, check_name: str, error: Exception):
        """Handle health check execution failure"""
        logger.error(f"Health check '{check_name}' execution failed: {str(error)}")
        
        # Create failure result
        failure_result = HealthCheckResult(
            name=check_name,
            status=HealthStatus.UNHEALTHY,
            message=f"Health check execution failed: {str(error)}",
            details={"error": str(error)},
            duration_ms=0.0
        )
        
        # Update registry statistics
        health_check_registry.update_check_statistics(check_name, failure_result)
        
        # Send error notifications
        if self.config.enable_notifications:
            metadata = health_check_registry.get_metadata(check_name)
            await self._send_error_notification(check_name, error, metadata)
        
        # Retry failed checks if enabled
        if self.config.retry_failed_checks:
            await self._schedule_retry(check_name)
    
    async def _schedule_retry(self, check_name: str):
        """Schedule a retry for a failed health check"""
        metadata = health_check_registry.get_metadata(check_name)
        if not metadata:
            return
        
        # Check if we should retry
        if metadata.failure_count >= self.config.max_retry_attempts:
            logger.warning(f"Health check '{check_name}' exceeded max retry attempts")
            return
        
        # Schedule retry
        retry_time = datetime.utcnow() + timedelta(seconds=self.config.retry_delay_seconds)
        metadata.next_run = retry_time
        
        logger.info(f"Scheduled retry for health check '{check_name}' at {retry_time}")
    
    async def _send_notification(self, check_name: str, result: HealthCheckResult, metadata):
        """Send notification for health check result"""
        for callback in self._notification_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(check_name, result, metadata)
                else:
                    callback(check_name, result, metadata)
            except Exception as e:
                logger.error(f"Error in notification callback: {str(e)}")
    
    async def _send_error_notification(self, check_name: str, error: Exception, metadata):
        """Send error notification"""
        for callback in self._error_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(check_name, error, metadata)
                else:
                    callback(check_name, error, metadata)
            except Exception as e:
                logger.error(f"Error in error notification callback: {str(e)}")
    
    def add_notification_callback(self, callback: Callable):
        """Add a notification callback"""
        self._notification_callbacks.append(callback)
    
    def add_error_callback(self, callback: Callable):
        """Add an error notification callback"""
        self._error_callbacks.append(callback)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get scheduler metrics"""
        if self._start_time:
            self.metrics.scheduler_uptime_seconds = (
                datetime.utcnow() - self._start_time
            ).total_seconds()
        
        return {
            "state": self.state.value,
            "total_checks_executed": self.metrics.total_checks_executed,
            "successful_checks": self.metrics.successful_checks,
            "failed_checks": self.metrics.failed_checks,
            "success_rate": (
                self.metrics.successful_checks / self.metrics.total_checks_executed
                if self.metrics.total_checks_executed > 0 else 0.0
            ),
            "average_execution_time_ms": self.metrics.average_execution_time_ms,
            "concurrent_executions": self.metrics.concurrent_executions,
            "max_concurrent_executions": self.metrics.max_concurrent_executions,
            "scheduler_uptime_seconds": self.metrics.scheduler_uptime_seconds,
            "last_execution_time": (
                self.metrics.last_execution_time.isoformat()
                if self.metrics.last_execution_time else None
            ),
            "running_tasks": len(self._running_tasks)
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            "state": self.state.value,
            "config": {
                "check_interval_seconds": self.config.check_interval_seconds,
                "max_concurrent_checks": self.config.max_concurrent_checks,
                "priority_execution": self.config.priority_execution,
                "enable_graceful_shutdown": self.config.enable_graceful_shutdown,
                "enable_metrics": self.config.enable_metrics,
                "enable_notifications": self.config.enable_notifications,
                "retry_failed_checks": self.config.retry_failed_checks
            },
            "metrics": self.get_metrics(),
            "registry_summary": health_check_registry.get_registry_summary()
        }


# Global scheduler instance
health_check_scheduler = HealthCheckScheduler()


# Convenience functions
async def start_health_check_scheduler(config: Optional[SchedulerConfig] = None) -> bool:
    """Start the global health check scheduler"""
    if config:
        health_check_scheduler.config = config
    return await health_check_scheduler.start()


async def stop_health_check_scheduler() -> bool:
    """Stop the global health check scheduler"""
    return await health_check_scheduler.stop()


def get_scheduler_status() -> Dict[str, Any]:
    """Get status of the global health check scheduler"""
    return health_check_scheduler.get_status()


def add_notification_callback(callback: Callable):
    """Add a notification callback to the global scheduler"""
    health_check_scheduler.add_notification_callback(callback)


def add_error_callback(callback: Callable):
    """Add an error callback to the global scheduler"""
    health_check_scheduler.add_error_callback(callback) 