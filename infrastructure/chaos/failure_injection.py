"""
🔍 Failure Injection System
📅 Generated: 2025-01-27
🎯 Purpose: Controlled failure injection to test system resilience
📋 Tracing ID: FAILURE_INJECTION_001_20250127
"""

import logging
import time
import asyncio
import random
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import threading
from datetime import datetime, timedelta
import signal
import os
import sys
from contextlib import contextmanager
from functools import wraps

logger = logging.getLogger(__name__)


class FailureType(Enum):
    """Types of failures to inject"""
    TIMEOUT = "timeout"
    EXCEPTION = "exception"
    MEMORY_LEAK = "memory_leak"
    CPU_SPIKE = "cpu_spike"
    NETWORK_ERROR = "network_error"
    DATABASE_ERROR = "database_error"
    CACHE_ERROR = "cache_error"
    DISK_ERROR = "disk_error"
    RANDOM_FAILURE = "random_failure"
    CUSTOM = "custom"


class InjectionMode(Enum):
    """Injection modes"""
    IMMEDIATE = "immediate"
    DELAYED = "delayed"
    RANDOM = "random"
    CONDITIONAL = "conditional"
    PROBABILISTIC = "probabilistic"


class FailureSeverity(Enum):
    """Failure severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FailureConfig:
    """Configuration for failure injection"""
    failure_type: FailureType
    injection_mode: InjectionMode = InjectionMode.IMMEDIATE
    severity: FailureSeverity = FailureSeverity.MEDIUM
    probability: float = 0.1  # 10% chance
    delay_seconds: float = 0.0
    duration_seconds: float = 30.0
    target_functions: List[str] = field(default_factory=list)
    target_modules: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    custom_script: Optional[str] = None
    auto_recovery: bool = True
    recovery_timeout: float = 60.0
    monitoring_enabled: bool = True
    alert_on_failure: bool = True


@dataclass
class InjectionResult:
    """Result of failure injection"""
    injection_id: str
    failure_type: FailureType
    success: bool
    start_time: float
    end_time: Optional[float] = None
    duration: float = 0.0
    error_message: str = ""
    affected_functions: List[str] = field(default_factory=list)
    recovery_successful: bool = True
    impact_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class FailureInjector:
    """
    System for injecting controlled failures
    """
    
    def __init__(self, config: FailureConfig):
        self.config = config
        self.injection_id = self._generate_injection_id()
        self.active_injections = {}
        self.recovery_handlers = {}
        self.monitoring_callbacks = []
        self.lock = threading.RLock()
        self.injection_count = 0
        self.success_count = 0
        
    def _generate_injection_id(self) -> str:
        """Generate unique injection ID"""
        timestamp = int(time.time())
        random_suffix = random.randint(1000, 9999)
        return f"failure_{self.config.failure_type.value}_{timestamp}_{random_suffix}"
    
    def inject_failure(self, target_func: Optional[Callable] = None) -> InjectionResult:
        """
        Inject a failure based on configuration
        
        Args:
            target_func: Optional target function to inject failure into
            
        Returns:
            Injection result
        """
        start_time = time.time()
        
        try:
            # Check if injection should occur
            if not self._should_inject():
                return InjectionResult(
                    injection_id=self.injection_id,
                    failure_type=self.config.failure_type,
                    success=False,
                    start_time=start_time,
                    error_message="Injection skipped based on configuration"
                )
            
            # Apply delay if configured
            if self.config.delay_seconds > 0:
                time.sleep(self.config.delay_seconds)
            
            # Execute failure injection
            self._execute_failure_injection(target_func)
            
            # Wait for duration
            time.sleep(self.config.duration_seconds)
            
            # Auto-recovery if enabled
            recovery_successful = True
            if self.config.auto_recovery:
                recovery_successful = self._perform_recovery()
            
            end_time = time.time()
            
            result = InjectionResult(
                injection_id=self.injection_id,
                failure_type=self.config.failure_type,
                success=True,
                start_time=start_time,
                end_time=end_time,
                duration=end_time - start_time,
                recovery_successful=recovery_successful,
                impact_score=self._calculate_impact_score()
            )
            
            self.injection_count += 1
            self.success_count += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Failure injection failed: {e}")
            end_time = time.time()
            
            # Attempt recovery
            recovery_successful = self._perform_recovery()
            
            return InjectionResult(
                injection_id=self.injection_id,
                failure_type=self.config.failure_type,
                success=False,
                start_time=start_time,
                end_time=end_time,
                duration=end_time - start_time,
                error_message=str(e),
                recovery_successful=recovery_successful
            )
    
    def _should_inject(self) -> bool:
        """Determine if failure should be injected"""
        if self.config.injection_mode == InjectionMode.IMMEDIATE:
            return True
        elif self.config.injection_mode == InjectionMode.PROBABILISTIC:
            return random.random() < self.config.probability
        elif self.config.injection_mode == InjectionMode.CONDITIONAL:
            return self._check_conditions()
        else:
            return True
    
    def _check_conditions(self) -> bool:
        """Check if conditions are met for injection"""
        conditions = self.config.conditions
        
        # Check time-based conditions
        if 'time_window' in conditions:
            current_hour = datetime.now().hour
            start_hour = conditions['time_window'].get('start', 0)
            end_hour = conditions['time_window'].get('end', 24)
            
            if not (start_hour <= current_hour <= end_hour):
                return False
        
        # Check load-based conditions
        if 'cpu_threshold' in conditions:
            import psutil
            if psutil.cpu_percent() < conditions['cpu_threshold']:
                return False
        
        # Check memory-based conditions
        if 'memory_threshold' in conditions:
            import psutil
            if psutil.virtual_memory().percent < conditions['memory_threshold']:
                return False
        
        return True
    
    def _execute_failure_injection(self, target_func: Optional[Callable] = None):
        """Execute the specific failure injection"""
        if self.config.failure_type == FailureType.TIMEOUT:
            self._inject_timeout()
        elif self.config.failure_type == FailureType.EXCEPTION:
            self._inject_exception()
        elif self.config.failure_type == FailureType.MEMORY_LEAK:
            self._inject_memory_leak()
        elif self.config.failure_type == FailureType.CPU_SPIKE:
            self._inject_cpu_spike()
        elif self.config.failure_type == FailureType.NETWORK_ERROR:
            self._inject_network_error()
        elif self.config.failure_type == FailureType.DATABASE_ERROR:
            self._inject_database_error()
        elif self.config.failure_type == FailureType.CACHE_ERROR:
            self._inject_cache_error()
        elif self.config.failure_type == FailureType.DISK_ERROR:
            self._inject_disk_error()
        elif self.config.failure_type == FailureType.RANDOM_FAILURE:
            self._inject_random_failure()
        elif self.config.failure_type == FailureType.CUSTOM:
            self._inject_custom_failure()
        else:
            raise ValueError(f"Unsupported failure type: {self.config.failure_type}")
    
    def _inject_timeout(self):
        """Inject timeout failure"""
        logger.info(f"Injecting timeout failure: {self.injection_id}")
        
        # Simulate timeout by sleeping
        time.sleep(self.config.duration_seconds)
        
        # Add recovery handler
        self.recovery_handlers[self.injection_id] = self._recover_timeout
    
    def _inject_exception(self):
        """Inject exception failure"""
        logger.info(f"Injecting exception failure: {self.injection_id}")
        
        # Raise a controlled exception
        exception_type = self.config.conditions.get('exception_type', RuntimeError)
        exception_message = self.config.conditions.get('exception_message', 'Injected failure')
        
        raise exception_type(exception_message)
    
    def _inject_memory_leak(self):
        """Inject memory leak failure"""
        logger.info(f"Injecting memory leak failure: {self.injection_id}")
        
        # Allocate memory and don't release it
        memory_mb = self.config.conditions.get('memory_mb', 100)
        memory_data = []
        
        for i in range(memory_mb):
            # Allocate 1MB of data
            memory_data.append('x' * 1024 * 1024)
        
        # Store reference to prevent garbage collection
        self.active_injections[self.injection_id] = memory_data
        
        # Add recovery handler
        self.recovery_handlers[self.injection_id] = self._recover_memory_leak
    
    def _inject_cpu_spike(self):
        """Inject CPU spike failure"""
        logger.info(f"Injecting CPU spike failure: {self.injection_id}")
        
        # Start CPU-intensive task
        def cpu_intensive_task():
            while True:
                # Perform CPU-intensive calculations
                sum(range(1000000))
        
        # Start thread for CPU spike
        cpu_thread = threading.Thread(target=cpu_intensive_task, daemon=True)
        cpu_thread.start()
        
        self.active_injections[self.injection_id] = cpu_thread
        
        # Add recovery handler
        self.recovery_handlers[self.injection_id] = self._recover_cpu_spike
    
    def _inject_network_error(self):
        """Inject network error failure"""
        logger.info(f"Injecting network error failure: {self.injection_id}")
        
        # Simulate network error by raising connection error
        import socket
        raise socket.error("Injected network failure")
    
    def _inject_database_error(self):
        """Inject database error failure"""
        logger.info(f"Injecting database error failure: {self.injection_id}")
        
        # Simulate database error
        class DatabaseError(Exception):
            pass
        
        raise DatabaseError("Injected database failure")
    
    def _inject_cache_error(self):
        """Inject cache error failure"""
        logger.info(f"Injecting cache error failure: {self.injection_id}")
        
        # Simulate cache error
        class CacheError(Exception):
            pass
        
        raise CacheError("Injected cache failure")
    
    def _inject_disk_error(self):
        """Inject disk error failure"""
        logger.info(f"Injecting disk error failure: {self.injection_id}")
        
        # Simulate disk error
        class DiskError(Exception):
            pass
        
        raise DiskError("Injected disk failure")
    
    def _inject_random_failure(self):
        """Inject random failure"""
        logger.info(f"Injecting random failure: {self.injection_id}")
        
        # Choose random failure type
        failure_types = [
            self._inject_timeout,
            self._inject_exception,
            self._inject_memory_leak,
            self._inject_cpu_spike,
            self._inject_network_error
        ]
        
        random_failure = random.choice(failure_types)
        random_failure()
    
    def _inject_custom_failure(self):
        """Inject custom failure using script"""
        logger.info(f"Injecting custom failure: {self.injection_id}")
        
        if not self.config.custom_script:
            raise ValueError("Custom script not specified")
        
        # Execute custom script
        import subprocess
        result = subprocess.run(
            self.config.custom_script,
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Custom failure script failed: {result.stderr}")
    
    def _perform_recovery(self) -> bool:
        """Perform recovery from failure"""
        try:
            if self.injection_id in self.recovery_handlers:
                recovery_handler = self.recovery_handlers[self.injection_id]
                recovery_handler()
            
            # Clean up active injections
            if self.injection_id in self.active_injections:
                del self.active_injections[self.injection_id]
            
            # Remove recovery handler
            if self.injection_id in self.recovery_handlers:
                del self.recovery_handlers[self.injection_id]
            
            logger.info(f"Recovery completed for injection: {self.injection_id}")
            return True
            
        except Exception as e:
            logger.error(f"Recovery failed for injection {self.injection_id}: {e}")
            return False
    
    def _recover_timeout(self):
        """Recover from timeout injection"""
        logger.info(f"Recovering from timeout injection: {self.injection_id}")
        # Timeout recovery is automatic - just log it
    
    def _recover_memory_leak(self):
        """Recover from memory leak injection"""
        logger.info(f"Recovering from memory leak injection: {self.injection_id}")
        
        if self.injection_id in self.active_injections:
            # Clear the memory data
            del self.active_injections[self.injection_id]
    
    def _recover_cpu_spike(self):
        """Recover from CPU spike injection"""
        logger.info(f"Recovering from CPU spike injection: {self.injection_id}")
        
        if self.injection_id in self.active_injections:
            # The thread will terminate automatically when daemon=True
            del self.active_injections[self.injection_id]
    
    def _calculate_impact_score(self) -> float:
        """Calculate impact score of the failure"""
        impact_score = 0.0
        
        # Base impact based on severity
        severity_impact = {
            FailureSeverity.LOW: 0.1,
            FailureSeverity.MEDIUM: 0.3,
            FailureSeverity.HIGH: 0.6,
            FailureSeverity.CRITICAL: 1.0
        }
        
        impact_score += severity_impact.get(self.config.severity, 0.3)
        
        # Duration impact
        duration_impact = min(self.config.duration_seconds / 300.0, 1.0)  # Normalize to 5 minutes
        impact_score += duration_impact * 0.2
        
        # Probability impact
        impact_score += self.config.probability * 0.1
        
        return min(impact_score, 1.0)
    
    def add_monitoring_callback(self, callback: Callable):
        """Add monitoring callback"""
        self.monitoring_callbacks.append(callback)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get injection statistics"""
        return {
            'total_injections': self.injection_count,
            'successful_injections': self.success_count,
            'success_rate': self.success_count / self.injection_count if self.injection_count > 0 else 0.0,
            'active_injections': len(self.active_injections),
            'failure_type': self.config.failure_type.value,
            'severity': self.config.severity.value
        }


class FailureInjectionDecorator:
    """Decorator for injecting failures into functions"""
    
    def __init__(self, config: FailureConfig):
        self.config = config
        self.injector = FailureInjector(config)
    
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if failure should be injected
            if self.injector._should_inject():
                try:
                    # Inject failure
                    result = self.injector.inject_failure(func)
                    
                    if result.success:
                        # If injection was successful, raise an exception
                        if self.config.failure_type == FailureType.TIMEOUT:
                            raise TimeoutError("Injected timeout failure")
                        elif self.config.failure_type == FailureType.EXCEPTION:
                            raise RuntimeError("Injected exception failure")
                        else:
                            raise RuntimeError(f"Injected {self.config.failure_type.value} failure")
                    
                except Exception as e:
                    # Re-raise the injected failure
                    raise e
            
            # If no failure injected, call original function
            return func(*args, **kwargs)
        
        return wrapper


class FailureInjectionManager:
    """Manager for multiple failure injections"""
    
    def __init__(self):
        self.injectors = {}
        self.global_config = {}
        self.lock = threading.RLock()
    
    def add_injector(self, name: str, config: FailureConfig) -> FailureInjector:
        """Add a new failure injector"""
        with self.lock:
            injector = FailureInjector(config)
            self.injectors[name] = injector
            return injector
    
    def get_injector(self, name: str) -> Optional[FailureInjector]:
        """Get injector by name"""
        return self.injectors.get(name)
    
    def remove_injector(self, name: str) -> bool:
        """Remove injector by name"""
        with self.lock:
            if name in self.injectors:
                del self.injectors[name]
                return True
            return False
    
    def inject_failure(self, name: str) -> Optional[InjectionResult]:
        """Inject failure using named injector"""
        injector = self.get_injector(name)
        if injector:
            return injector.inject_failure()
        return None
    
    def get_all_statistics(self) -> Dict[str, Any]:
        """Get statistics for all injectors"""
        stats = {}
        for name, injector in self.injectors.items():
            stats[name] = injector.get_statistics()
        return stats
    
    def cleanup_all(self):
        """Cleanup all active injections"""
        with self.lock:
            for injector in self.injectors.values():
                injector._perform_recovery()


# Global failure injection manager
_failure_manager: Optional[FailureInjectionManager] = None


def get_failure_manager() -> FailureInjectionManager:
    """Get global failure injection manager"""
    global _failure_manager
    if _failure_manager is None:
        _failure_manager = FailureInjectionManager()
    return _failure_manager


def inject_failure(config: FailureConfig) -> InjectionResult:
    """Global function to inject failure"""
    injector = FailureInjector(config)
    return injector.inject_failure()


def inject_failure_decorator(config: FailureConfig):
    """Global decorator for failure injection"""
    return FailureInjectionDecorator(config)


def add_failure_injector(name: str, config: FailureConfig) -> FailureInjector:
    """Add named failure injector"""
    manager = get_failure_manager()
    return manager.add_injector(name, config)


def get_failure_injector(name: str) -> Optional[FailureInjector]:
    """Get named failure injector"""
    manager = get_failure_manager()
    return manager.get_injector(name)


def inject_named_failure(name: str) -> Optional[InjectionResult]:
    """Inject failure using named injector"""
    manager = get_failure_manager()
    return manager.inject_failure(name)


def get_failure_statistics() -> Dict[str, Any]:
    """Get all failure injection statistics"""
    manager = get_failure_manager()
    return manager.get_all_statistics()


def cleanup_failures():
    """Cleanup all active failure injections"""
    manager = get_failure_manager()
    manager.cleanup_all() 