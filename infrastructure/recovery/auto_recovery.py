"""
Auto-Recovery System for Omni Keywords Finder

This module provides automatic recovery mechanisms for different types of failures,
including service restart, connection recovery, and resource cleanup.

Author: Paulo Júnior
Date: 2025-01-27
Tracing ID: AUTO_RECOVERY_001
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union
import subprocess
import signal
import os
import psutil

logger = logging.getLogger(__name__)


class RecoveryStatus(Enum):
    """Recovery status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    SKIPPED = "skipped"


class RecoveryType(Enum):
    """Types of recovery actions"""
    SERVICE_RESTART = "service_restart"
    CONNECTION_RECOVERY = "connection_recovery"
    RESOURCE_CLEANUP = "resource_cleanup"
    CONFIGURATION_RELOAD = "configuration_reload"
    CACHE_CLEAR = "cache_clear"
    DATABASE_RECOVERY = "database_recovery"
    CUSTOM = "custom"


class FailureType(Enum):
    """Types of failures"""
    SERVICE_CRASH = "service_crash"
    CONNECTION_LOST = "connection_lost"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    CONFIGURATION_ERROR = "configuration_error"
    CACHE_CORRUPTION = "cache_corruption"
    DATABASE_ERROR = "database_error"
    TIMEOUT = "timeout"
    MEMORY_LEAK = "memory_leak"
    CUSTOM = "custom"


@dataclass
class RecoveryAction:
    """Represents a recovery action"""
    name: str
    recovery_type: RecoveryType
    description: str = ""
    max_attempts: int = 3
    timeout_seconds: float = 30.0
    delay_between_attempts: float = 5.0
    dependencies: List[str] = field(default_factory=list)
    rollback_action: Optional[str] = None
    success_criteria: Optional[Callable] = None
    enabled: bool = True


@dataclass
class RecoveryResult:
    """Result of a recovery action"""
    action_name: str
    recovery_type: RecoveryType
    status: RecoveryStatus
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    attempts: int = 0
    error_message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryConfig:
    """Configuration for auto-recovery system"""
    enabled: bool = True
    max_concurrent_recoveries: int = 5
    global_timeout_seconds: float = 300.0  # 5 minutes
    enable_rollback: bool = True
    enable_metrics: bool = True
    enable_notifications: bool = True
    recovery_cooldown_seconds: float = 60.0  # 1 minute between recoveries
    max_recovery_frequency: int = 10  # Max recoveries per hour


class BaseRecoveryStrategy(ABC):
    """Base class for recovery strategies"""
    
    def __init__(self, name: str, config: Optional[RecoveryConfig] = None):
        self.name = name
        self.config = config or RecoveryConfig()
        self.recovery_history: List[RecoveryResult] = []
        self.max_history_size = 100
    
    @abstractmethod
    async def can_recover(self, failure_type: FailureType, context: Dict[str, Any]) -> bool:
        """Check if this strategy can handle the failure"""
        pass
    
    @abstractmethod
    async def execute_recovery(self, failure_type: FailureType, context: Dict[str, Any]) -> RecoveryResult:
        """Execute the recovery action"""
        pass
    
    def add_to_history(self, result: RecoveryResult):
        """Add result to history, maintaining max size"""
        self.recovery_history.append(result)
        if len(self.recovery_history) > self.max_history_size:
            self.recovery_history.pop(0)
    
    def get_success_rate(self, window_minutes: int = 60) -> float:
        """Calculate success rate in the given time window"""
        if not self.recovery_history:
            return 0.0
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
        recent_recoveries = [
            recovery for recovery in self.recovery_history 
            if recovery.start_time >= cutoff_time
        ]
        
        if not recent_recoveries:
            return 0.0
        
        successful_recoveries = sum(
            1 for recovery in recent_recoveries 
            if recovery.status == RecoveryStatus.SUCCESSFUL
        )
        
        return successful_recoveries / len(recent_recoveries)


class ServiceRestartStrategy(BaseRecoveryStrategy):
    """Strategy for restarting services"""
    
    def __init__(self, service_name: str, restart_command: str, **kwargs):
        super().__init__(f"service_restart_{service_name}", **kwargs)
        self.service_name = service_name
        self.restart_command = restart_command
    
    async def can_recover(self, failure_type: FailureType, context: Dict[str, Any]) -> bool:
        """Check if service restart can handle the failure"""
        return failure_type in [
            FailureType.SERVICE_CRASH,
            FailureType.TIMEOUT,
            FailureType.MEMORY_LEAK
        ]
    
    async def execute_recovery(self, failure_type: FailureType, context: Dict[str, Any]) -> RecoveryResult:
        """Execute service restart recovery"""
        result = RecoveryResult(
            action_name=self.name,
            recovery_type=RecoveryType.SERVICE_RESTART,
            status=RecoveryStatus.IN_PROGRESS
        )
        
        try:
            logger.info(f"Starting service restart recovery for {self.service_name}")
            
            # Check if service is running
            if await self._is_service_running():
                logger.info(f"Service {self.service_name} is already running, stopping first")
                await self._stop_service()
                await asyncio.sleep(2)  # Wait for service to stop
            
            # Start service
            await self._start_service()
            
            # Wait for service to be ready
            if await self._wait_for_service_ready():
                result.status = RecoveryStatus.SUCCESSFUL
                result.details = {"service_name": self.service_name, "restart_successful": True}
                logger.info(f"Service restart recovery successful for {self.service_name}")
            else:
                result.status = RecoveryStatus.FAILED
                result.error_message = f"Service {self.service_name} failed to start properly"
                logger.error(f"Service restart recovery failed for {self.service_name}")
        
        except Exception as e:
            result.status = RecoveryStatus.FAILED
            result.error_message = str(e)
            logger.error(f"Service restart recovery failed for {self.service_name}: {str(e)}")
        
        finally:
            result.end_time = datetime.utcnow()
            result.duration_seconds = (result.end_time - result.start_time).total_seconds()
            self.add_to_history(result)
        
        return result
    
    async def _is_service_running(self) -> bool:
        """Check if service is running"""
        try:
            # Check if process exists
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if self.service_name.lower() in proc.info['name'].lower():
                    return True
            return False
        except Exception as e:
            logger.warning(f"Error checking if service {self.service_name} is running: {str(e)}")
            return False
    
    async def _stop_service(self):
        """Stop the service"""
        try:
            # Try graceful stop first
            for proc in psutil.process_iter(['pid', 'name']):
                if self.service_name.lower() in proc.info['name'].lower():
                    proc.terminate()
                    proc.wait(timeout=10)
                    break
        except Exception as e:
            logger.warning(f"Error stopping service {self.service_name}: {str(e)}")
    
    async def _start_service(self):
        """Start the service"""
        try:
            # Execute restart command
            process = await asyncio.create_subprocess_shell(
                self.restart_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.config.global_timeout_seconds
            )
            
            if process.returncode != 0:
                raise Exception(f"Service start failed: {stderr.decode()}")
        
        except Exception as e:
            logger.error(f"Error starting service {self.service_name}: {str(e)}")
            raise
    
    async def _wait_for_service_ready(self, timeout_seconds: float = 30.0) -> bool:
        """Wait for service to be ready"""
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            if await self._is_service_running():
                # Additional health check could be added here
                return True
            await asyncio.sleep(1)
        
        return False


class ConnectionRecoveryStrategy(BaseRecoveryStrategy):
    """Strategy for recovering lost connections"""
    
    def __init__(self, connection_name: str, connection_factory: Callable, **kwargs):
        super().__init__(f"connection_recovery_{connection_name}", **kwargs)
        self.connection_name = connection_name
        self.connection_factory = connection_factory
        self.current_connection = None
    
    async def can_recover(self, failure_type: FailureType, context: Dict[str, Any]) -> bool:
        """Check if connection recovery can handle the failure"""
        return failure_type in [
            FailureType.CONNECTION_LOST,
            FailureType.TIMEOUT
        ]
    
    async def execute_recovery(self, failure_type: FailureType, context: Dict[str, Any]) -> RecoveryResult:
        """Execute connection recovery"""
        result = RecoveryResult(
            action_name=self.name,
            recovery_type=RecoveryType.CONNECTION_RECOVERY,
            status=RecoveryStatus.IN_PROGRESS
        )
        
        try:
            logger.info(f"Starting connection recovery for {self.connection_name}")
            
            # Close existing connection if any
            if self.current_connection:
                try:
                    await self._close_connection(self.current_connection)
                except Exception as e:
                    logger.warning(f"Error closing existing connection: {str(e)}")
            
            # Create new connection
            self.current_connection = await self._create_connection()
            
            # Test connection
            if await self._test_connection(self.current_connection):
                result.status = RecoveryStatus.SUCCESSFUL
                result.details = {"connection_name": self.connection_name, "recovery_successful": True}
                logger.info(f"Connection recovery successful for {self.connection_name}")
            else:
                result.status = RecoveryStatus.FAILED
                result.error_message = f"Connection {self.connection_name} failed to establish"
                logger.error(f"Connection recovery failed for {self.connection_name}")
        
        except Exception as e:
            result.status = RecoveryStatus.FAILED
            result.error_message = str(e)
            logger.error(f"Connection recovery failed for {self.connection_name}: {str(e)}")
        
        finally:
            result.end_time = datetime.utcnow()
            result.duration_seconds = (result.end_time - result.start_time).total_seconds()
            self.add_to_history(result)
        
        return result
    
    async def _create_connection(self):
        """Create a new connection"""
        if asyncio.iscoroutinefunction(self.connection_factory):
            return await self.connection_factory()
        else:
            return self.connection_factory()
    
    async def _close_connection(self, connection):
        """Close the connection"""
        if hasattr(connection, 'close'):
            if asyncio.iscoroutinefunction(connection.close):
                await connection.close()
            else:
                connection.close()
        elif hasattr(connection, 'disconnect'):
            if asyncio.iscoroutinefunction(connection.disconnect):
                await connection.disconnect()
            else:
                connection.disconnect()
    
    async def _test_connection(self, connection) -> bool:
        """Test if connection is working"""
        try:
            # Try a simple operation to test connection
            if hasattr(connection, 'ping'):
                if asyncio.iscoroutinefunction(connection.ping):
                    await connection.ping()
                else:
                    connection.ping()
                return True
            elif hasattr(connection, 'execute'):
                if asyncio.iscoroutinefunction(connection.execute):
                    await connection.execute("SELECT 1")
                else:
                    connection.execute("SELECT 1")
                return True
            else:
                # Assume connection is working if no test method available
                return True
        except Exception as e:
            logger.warning(f"Connection test failed: {str(e)}")
            return False


class ResourceCleanupStrategy(BaseRecoveryStrategy):
    """Strategy for cleaning up resources"""
    
    def __init__(self, resource_type: str, cleanup_function: Callable, **kwargs):
        super().__init__(f"resource_cleanup_{resource_type}", **kwargs)
        self.resource_type = resource_type
        self.cleanup_function = cleanup_function
    
    async def can_recover(self, failure_type: FailureType, context: Dict[str, Any]) -> bool:
        """Check if resource cleanup can handle the failure"""
        return failure_type in [
            FailureType.RESOURCE_EXHAUSTION,
            FailureType.MEMORY_LEAK,
            FailureType.CACHE_CORRUPTION
        ]
    
    async def execute_recovery(self, failure_type: FailureType, context: Dict[str, Any]) -> RecoveryResult:
        """Execute resource cleanup"""
        result = RecoveryResult(
            action_name=self.name,
            recovery_type=RecoveryType.RESOURCE_CLEANUP,
            status=RecoveryStatus.IN_PROGRESS
        )
        
        try:
            logger.info(f"Starting resource cleanup for {self.resource_type}")
            
            # Execute cleanup function
            if asyncio.iscoroutinefunction(self.cleanup_function):
                cleanup_result = await self.cleanup_function(context)
            else:
                cleanup_result = self.cleanup_function(context)
            
            result.status = RecoveryStatus.SUCCESSFUL
            result.details = {
                "resource_type": self.resource_type,
                "cleanup_result": cleanup_result
            }
            logger.info(f"Resource cleanup successful for {self.resource_type}")
        
        except Exception as e:
            result.status = RecoveryStatus.FAILED
            result.error_message = str(e)
            logger.error(f"Resource cleanup failed for {self.resource_type}: {str(e)}")
        
        finally:
            result.end_time = datetime.utcnow()
            result.duration_seconds = (result.end_time - result.start_time).total_seconds()
            self.add_to_history(result)
        
        return result


class ConfigurationReloadStrategy(BaseRecoveryStrategy):
    """Strategy for reloading configuration"""
    
    def __init__(self, config_manager: Any, **kwargs):
        super().__init__("configuration_reload", **kwargs)
        self.config_manager = config_manager
    
    async def can_recover(self, failure_type: FailureType, context: Dict[str, Any]) -> bool:
        """Check if configuration reload can handle the failure"""
        return failure_type == FailureType.CONFIGURATION_ERROR
    
    async def execute_recovery(self, failure_type: FailureType, context: Dict[str, Any]) -> RecoveryResult:
        """Execute configuration reload"""
        result = RecoveryResult(
            action_name=self.name,
            recovery_type=RecoveryType.CONFIGURATION_RELOAD,
            status=RecoveryStatus.IN_PROGRESS
        )
        
        try:
            logger.info("Starting configuration reload recovery")
            
            # Reload configuration
            if hasattr(self.config_manager, 'reload'):
                if asyncio.iscoroutinefunction(self.config_manager.reload):
                    await self.config_manager.reload()
                else:
                    self.config_manager.reload()
            
            result.status = RecoveryStatus.SUCCESSFUL
            result.details = {"reload_successful": True}
            logger.info("Configuration reload recovery successful")
        
        except Exception as e:
            result.status = RecoveryStatus.FAILED
            result.error_message = str(e)
            logger.error(f"Configuration reload recovery failed: {str(e)}")
        
        finally:
            result.end_time = datetime.utcnow()
            result.duration_seconds = (result.end_time - result.start_time).total_seconds()
            self.add_to_history(result)
        
        return result


class AutoRecoveryManager:
    """Manager for auto-recovery operations"""
    
    def __init__(self, config: Optional[RecoveryConfig] = None):
        self.config = config or RecoveryConfig()
        self.recovery_strategies: Dict[str, BaseRecoveryStrategy] = {}
        self.recovery_history: List[RecoveryResult] = []
        self.active_recoveries: Dict[str, asyncio.Task] = {}
        self.recovery_cooldowns: Dict[str, datetime] = {}
        self._notification_callbacks: List[Callable] = []
        self._metrics_callbacks: List[Callable] = []
    
    def add_recovery_strategy(self, strategy: BaseRecoveryStrategy):
        """Add a recovery strategy"""
        self.recovery_strategies[strategy.name] = strategy
        logger.info(f"Added recovery strategy: {strategy.name}")
    
    def remove_recovery_strategy(self, strategy_name: str):
        """Remove a recovery strategy"""
        if strategy_name in self.recovery_strategies:
            del self.recovery_strategies[strategy_name]
            logger.info(f"Removed recovery strategy: {strategy_name}")
    
    async def trigger_recovery(self, failure_type: FailureType, context: Dict[str, Any]) -> List[RecoveryResult]:
        """Trigger recovery for a failure"""
        if not self.config.enabled:
            logger.info("Auto-recovery is disabled")
            return []
        
        # Check cooldown
        if self._is_in_cooldown(failure_type):
            logger.info(f"Recovery for {failure_type.value} is in cooldown")
            return []
        
        # Find applicable strategies
        applicable_strategies = []
        for strategy in self.recovery_strategies.values():
            if await strategy.can_recover(failure_type, context):
                applicable_strategies.append(strategy)
        
        if not applicable_strategies:
            logger.warning(f"No recovery strategy found for failure type: {failure_type.value}")
            return []
        
        # Check concurrent recovery limit
        if len(self.active_recoveries) >= self.config.max_concurrent_recoveries:
            logger.warning("Maximum concurrent recoveries reached")
            return []
        
        # Execute recoveries
        recovery_tasks = []
        for strategy in applicable_strategies:
            task = asyncio.create_task(self._execute_recovery(strategy, failure_type, context))
            recovery_tasks.append(task)
            self.active_recoveries[strategy.name] = task
        
        try:
            results = await asyncio.gather(*recovery_tasks, return_exceptions=True)
            
            # Process results
            recovery_results = []
            for i, result in enumerate(results):
                strategy = applicable_strategies[i]
                
                if isinstance(result, Exception):
                    # Handle failed recovery
                    recovery_result = RecoveryResult(
                        action_name=strategy.name,
                        recovery_type=RecoveryType.CUSTOM,
                        status=RecoveryStatus.FAILED,
                        error_message=str(result)
                    )
                else:
                    recovery_result = result
                
                recovery_results.append(recovery_result)
                self.recovery_history.append(recovery_result)
                
                # Trigger callbacks
                await self._trigger_callbacks(recovery_result)
                
                # Set cooldown
                self._set_cooldown(failure_type)
            
            return recovery_results
        
        finally:
            # Clean up active recoveries
            for strategy in applicable_strategies:
                self.active_recoveries.pop(strategy.name, None)
    
    async def _execute_recovery(self, strategy: BaseRecoveryStrategy, failure_type: FailureType, context: Dict[str, Any]) -> RecoveryResult:
        """Execute a single recovery strategy"""
        try:
            result = await strategy.execute_recovery(failure_type, context)
            return result
        except Exception as e:
            logger.error(f"Error executing recovery strategy {strategy.name}: {str(e)}")
            raise
    
    def _is_in_cooldown(self, failure_type: FailureType) -> bool:
        """Check if recovery is in cooldown"""
        if failure_type.value not in self.recovery_cooldowns:
            return False
        
        cooldown_time = self.recovery_cooldowns[failure_type.value]
        return datetime.utcnow() < cooldown_time
    
    def _set_cooldown(self, failure_type: FailureType):
        """Set cooldown for failure type"""
        cooldown_time = datetime.utcnow() + timedelta(seconds=self.config.recovery_cooldown_seconds)
        self.recovery_cooldowns[failure_type.value] = cooldown_time
    
    async def _trigger_callbacks(self, result: RecoveryResult):
        """Trigger notification and metrics callbacks"""
        # Notification callbacks
        for callback in self._notification_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(result)
                else:
                    callback(result)
            except Exception as e:
                logger.error(f"Error in notification callback: {str(e)}")
        
        # Metrics callbacks
        for callback in self._metrics_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(result)
                else:
                    callback(result)
            except Exception as e:
                logger.error(f"Error in metrics callback: {str(e)}")
    
    def add_notification_callback(self, callback: Callable):
        """Add a notification callback"""
        self._notification_callbacks.append(callback)
    
    def add_metrics_callback(self, callback: Callable):
        """Add a metrics callback"""
        self._metrics_callbacks.append(callback)
    
    def get_recovery_summary(self) -> Dict[str, Any]:
        """Get summary of recovery operations"""
        total_recoveries = len(self.recovery_history)
        successful_recoveries = sum(
            1 for recovery in self.recovery_history 
            if recovery.status == RecoveryStatus.SUCCESSFUL
        )
        failed_recoveries = sum(
            1 for recovery in self.recovery_history 
            if recovery.status == RecoveryStatus.FAILED
        )
        
        success_rate = successful_recoveries / total_recoveries if total_recoveries > 0 else 0.0
        
        # Strategy breakdown
        strategy_stats = {}
        for strategy in self.recovery_strategies.values():
            strategy_stats[strategy.name] = {
                "success_rate": strategy.get_success_rate(),
                "total_recoveries": len(strategy.recovery_history)
            }
        
        return {
            "total_recoveries": total_recoveries,
            "successful_recoveries": successful_recoveries,
            "failed_recoveries": failed_recoveries,
            "success_rate": success_rate,
            "active_recoveries": len(self.active_recoveries),
            "strategy_stats": strategy_stats,
            "enabled": self.config.enabled
        }


# Global auto-recovery manager
auto_recovery_manager = AutoRecoveryManager()


# Convenience functions
def add_recovery_strategy(strategy: BaseRecoveryStrategy):
    """Add a recovery strategy to the global manager"""
    auto_recovery_manager.add_recovery_strategy(strategy)


def remove_recovery_strategy(strategy_name: str):
    """Remove a recovery strategy from the global manager"""
    auto_recovery_manager.remove_recovery_strategy(strategy_name)


async def trigger_recovery(failure_type: FailureType, context: Dict[str, Any]) -> List[RecoveryResult]:
    """Trigger recovery using the global manager"""
    return await auto_recovery_manager.trigger_recovery(failure_type, context)


def get_recovery_summary() -> Dict[str, Any]:
    """Get recovery summary from the global manager"""
    return auto_recovery_manager.get_recovery_summary()


def add_notification_callback(callback: Callable):
    """Add a notification callback to the global manager"""
    auto_recovery_manager.add_notification_callback(callback)


def add_metrics_callback(callback: Callable):
    """Add a metrics callback to the global manager"""
    auto_recovery_manager.add_metrics_callback(callback) 