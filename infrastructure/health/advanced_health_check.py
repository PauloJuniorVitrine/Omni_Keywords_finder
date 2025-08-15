"""
Advanced Health Check System for Omni Keywords Finder

This module provides comprehensive health checking capabilities including:
- Custom health checks for different services
- External dependency monitoring
- Performance metrics collection
- Integration with observability systems

Author: Paulo Júnior
Date: 2025-01-27
Tracing ID: HEALTH_CHECK_001
"""

import asyncio
import time
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
import aiohttp
import psutil
import redis
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class HealthCheckType(Enum):
    """Types of health checks"""
    LIVENESS = "liveness"
    READINESS = "readiness"
    STARTUP = "startup"
    CUSTOM = "custom"


@dataclass
class HealthCheckResult:
    """Result of a health check"""
    name: str
    status: HealthStatus
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    duration_ms: float = 0.0
    check_type: HealthCheckType = HealthCheckType.CUSTOM


@dataclass
class HealthCheckConfig:
    """Configuration for health checks"""
    timeout_seconds: float = 30.0
    retry_attempts: int = 3
    retry_delay_seconds: float = 1.0
    critical_threshold: float = 0.8  # 80% success rate
    warning_threshold: float = 0.9   # 90% success rate


class BaseHealthCheck(ABC):
    """Base class for health checks"""
    
    def __init__(self, name: str, config: Optional[HealthCheckConfig] = None):
        self.name = name
        self.config = config or HealthCheckConfig()
        self.last_check: Optional[HealthCheckResult] = None
        self.check_history: List[HealthCheckResult] = []
        self.max_history_size = 100
    
    @abstractmethod
    async def check(self) -> HealthCheckResult:
        """Perform the health check"""
        pass
    
    def get_success_rate(self, window_minutes: int = 5) -> float:
        """Calculate success rate in the given time window"""
        if not self.check_history:
            return 0.0
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
        recent_checks = [
            check for check in self.check_history 
            if check.timestamp >= cutoff_time
        ]
        
        if not recent_checks:
            return 0.0
        
        successful_checks = sum(
            1 for check in recent_checks 
            if check.status == HealthStatus.HEALTHY
        )
        
        return successful_checks / len(recent_checks)
    
    def _add_to_history(self, result: HealthCheckResult):
        """Add result to history, maintaining max size"""
        self.check_history.append(result)
        if len(self.check_history) > self.max_history_size:
            self.check_history.pop(0)
        self.last_check = result


class DatabaseHealthCheck(BaseHealthCheck):
    """Health check for database connectivity"""
    
    def __init__(self, connection_string: str, **kwargs):
        super().__init__("database", **kwargs)
        self.connection_string = connection_string
    
    async def check(self) -> HealthCheckResult:
        start_time = time.time()
        
        try:
            # Create engine and test connection
            engine = create_engine(self.connection_string)
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                result.fetchone()
            
            duration_ms = (time.time() - start_time) * 1000
            
            result = HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="Database connection successful",
                details={"connection_string": self.connection_string},
                duration_ms=duration_ms,
                check_type=HealthCheckType.READINESS
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            result = HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection failed: {str(e)}",
                details={"error": str(e)},
                duration_ms=duration_ms,
                check_type=HealthCheckType.READINESS
            )
        
        self._add_to_history(result)
        return result


class RedisHealthCheck(BaseHealthCheck):
    """Health check for Redis connectivity"""
    
    def __init__(self, redis_url: str, **kwargs):
        super().__init__("redis", **kwargs)
        self.redis_url = redis_url
    
    async def check(self) -> HealthCheckResult:
        start_time = time.time()
        
        try:
            # Test Redis connection
            r = redis.from_url(self.redis_url)
            r.ping()
            
            # Test basic operations
            test_key = f"health_check_{int(time.time())}"
            r.set(test_key, "test", ex=60)
            value = r.get(test_key)
            r.delete(test_key)
            
            if value != b"test":
                raise Exception("Redis read/write test failed")
            
            duration_ms = (time.time() - start_time) * 1000
            
            result = HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="Redis connection and operations successful",
                details={"redis_url": self.redis_url},
                duration_ms=duration_ms,
                check_type=HealthCheckType.READINESS
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            result = HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Redis connection failed: {str(e)}",
                details={"error": str(e)},
                duration_ms=duration_ms,
                check_type=HealthCheckType.READINESS
            )
        
        self._add_to_history(result)
        return result


class ExternalAPICheck(BaseHealthCheck):
    """Health check for external API dependencies"""
    
    def __init__(self, name: str, url: str, expected_status: int = 200, **kwargs):
        super().__init__(name, **kwargs)
        self.url = url
        self.expected_status = expected_status
    
    async def check(self) -> HealthCheckResult:
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url, timeout=self.config.timeout_seconds) as response:
                    duration_ms = (time.time() - start_time) * 1000
                    
                    if response.status == self.expected_status:
                        result = HealthCheckResult(
                            name=self.name,
                            status=HealthStatus.HEALTHY,
                            message=f"External API {self.name} is healthy",
                            details={
                                "url": self.url,
                                "status_code": response.status,
                                "response_time_ms": duration_ms
                            },
                            duration_ms=duration_ms,
                            check_type=HealthCheckType.CUSTOM
                        )
                    else:
                        result = HealthCheckResult(
                            name=self.name,
                            status=HealthStatus.DEGRADED,
                            message=f"External API {self.name} returned unexpected status",
                            details={
                                "url": self.url,
                                "status_code": response.status,
                                "expected_status": self.expected_status
                            },
                            duration_ms=duration_ms,
                            check_type=HealthCheckType.CUSTOM
                        )
        
        except asyncio.TimeoutError:
            duration_ms = (time.time() - start_time) * 1000
            result = HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"External API {self.name} timeout",
                details={"url": self.url, "timeout_seconds": self.config.timeout_seconds},
                duration_ms=duration_ms,
                check_type=HealthCheckType.CUSTOM
            )
        
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            result = HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"External API {self.name} failed: {str(e)}",
                details={"url": self.url, "error": str(e)},
                duration_ms=duration_ms,
                check_type=HealthCheckType.CUSTOM
            )
        
        self._add_to_history(result)
        return result


class SystemResourceCheck(BaseHealthCheck):
    """Health check for system resources"""
    
    def __init__(self, **kwargs):
        super().__init__("system_resources", **kwargs)
    
    async def check(self) -> HealthCheckResult:
        start_time = time.time()
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Determine overall status
            status = HealthStatus.HEALTHY
            issues = []
            
            if cpu_percent > 90:
                status = HealthStatus.DEGRADED
                issues.append(f"High CPU usage: {cpu_percent}%")
            
            if memory_percent > 90:
                status = HealthStatus.DEGRADED
                issues.append(f"High memory usage: {memory_percent}%")
            
            if disk_percent > 90:
                status = HealthStatus.DEGRADED
                issues.append(f"High disk usage: {disk_percent}%")
            
            if cpu_percent > 95 or memory_percent > 95 or disk_percent > 95:
                status = HealthStatus.UNHEALTHY
            
            duration_ms = (time.time() - start_time) * 1000
            
            message = "System resources are healthy"
            if issues:
                message = f"System resource issues: {', '.join(issues)}"
            
            result = HealthCheckResult(
                name=self.name,
                status=status,
                message=message,
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent,
                    "disk_percent": disk_percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_free_gb": disk.free / (1024**3)
                },
                duration_ms=duration_ms,
                check_type=HealthCheckType.CUSTOM
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            result = HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"System resource check failed: {str(e)}",
                details={"error": str(e)},
                duration_ms=duration_ms,
                check_type=HealthCheckType.CUSTOM
            )
        
        self._add_to_history(result)
        return result


class CustomHealthCheck(BaseHealthCheck):
    """Custom health check using a callable function"""
    
    def __init__(self, name: str, check_function: Callable, **kwargs):
        super().__init__(name, **kwargs)
        self.check_function = check_function
    
    async def check(self) -> HealthCheckResult:
        start_time = time.time()
        
        try:
            # Execute the custom check function
            if asyncio.iscoroutinefunction(self.check_function):
                result_data = await self.check_function()
            else:
                result_data = self.check_function()
            
            duration_ms = (time.time() - start_time) * 1000
            
            # Determine status based on result
            if isinstance(result_data, dict):
                status = result_data.get('status', HealthStatus.HEALTHY)
                message = result_data.get('message', 'Custom check passed')
                details = result_data.get('details', {})
            else:
                status = HealthStatus.HEALTHY if result_data else HealthStatus.UNHEALTHY
                message = 'Custom check passed' if result_data else 'Custom check failed'
                details = {'result': result_data}
            
            result = HealthCheckResult(
                name=self.name,
                status=status,
                message=message,
                details=details,
                duration_ms=duration_ms,
                check_type=HealthCheckType.CUSTOM
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            result = HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Custom check failed: {str(e)}",
                details={"error": str(e)},
                duration_ms=duration_ms,
                check_type=HealthCheckType.CUSTOM
            )
        
        self._add_to_history(result)
        return result


class AdvancedHealthChecker:
    """Advanced health checker that manages multiple health checks"""
    
    def __init__(self, config: Optional[HealthCheckConfig] = None):
        self.config = config or HealthCheckConfig()
        self.health_checks: Dict[str, BaseHealthCheck] = {}
        self.overall_status = HealthStatus.UNKNOWN
        self.last_check_time: Optional[datetime] = None
    
    def add_health_check(self, health_check: BaseHealthCheck):
        """Add a health check to the registry"""
        self.health_checks[health_check.name] = health_check
        logger.info(f"Added health check: {health_check.name}")
    
    def remove_health_check(self, name: str):
        """Remove a health check from the registry"""
        if name in self.health_checks:
            del self.health_checks[name]
            logger.info(f"Removed health check: {name}")
    
    async def run_all_checks(self) -> Dict[str, HealthCheckResult]:
        """Run all registered health checks concurrently"""
        if not self.health_checks:
            return {}
        
        # Run all checks concurrently
        tasks = [
            health_check.check() 
            for health_check in self.health_checks.values()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        check_results = {}
        for i, (name, result) in enumerate(zip(self.health_checks.keys(), results)):
            if isinstance(result, Exception):
                # Handle failed health checks
                check_results[name] = HealthCheckResult(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health check failed: {str(result)}",
                    details={"error": str(result)},
                    check_type=HealthCheckType.CUSTOM
                )
            else:
                check_results[name] = result
        
        self.last_check_time = datetime.utcnow()
        self._update_overall_status(check_results)
        
        return check_results
    
    def _update_overall_status(self, results: Dict[str, HealthCheckResult]):
        """Update overall system status based on individual check results"""
        if not results:
            self.overall_status = HealthStatus.UNKNOWN
            return
        
        # Count statuses
        status_counts = {
            HealthStatus.HEALTHY: 0,
            HealthStatus.DEGRADED: 0,
            HealthStatus.UNHEALTHY: 0,
            HealthStatus.UNKNOWN: 0
        }
        
        for result in results.values():
            status_counts[result.status] += 1
        
        total_checks = len(results)
        
        # Determine overall status
        if status_counts[HealthStatus.UNHEALTHY] > 0:
            self.overall_status = HealthStatus.UNHEALTHY
        elif status_counts[HealthStatus.DEGRADED] > 0:
            self.overall_status = HealthStatus.DEGRADED
        elif status_counts[HealthStatus.HEALTHY] == total_checks:
            self.overall_status = HealthStatus.HEALTHY
        else:
            self.overall_status = HealthStatus.UNKNOWN
    
    def get_overall_status(self) -> Dict[str, Any]:
        """Get overall system health status"""
        return {
            "status": self.overall_status.value,
            "timestamp": self.last_check_time.isoformat() if self.last_check_time else None,
            "total_checks": len(self.health_checks),
            "last_check_time": self.last_check_time.isoformat() if self.last_check_time else None
        }
    
    def get_check_summary(self) -> Dict[str, Any]:
        """Get summary of all health checks"""
        summary = {
            "overall_status": self.get_overall_status(),
            "checks": {}
        }
        
        for name, health_check in self.health_checks.items():
            summary["checks"][name] = {
                "last_check": health_check.last_check.to_dict() if health_check.last_check else None,
                "success_rate": health_check.get_success_rate(),
                "check_count": len(health_check.check_history)
            }
        
        return summary


# Convenience functions for common health checks
async def create_database_health_check(connection_string: str) -> DatabaseHealthCheck:
    """Create a database health check"""
    return DatabaseHealthCheck(connection_string)


async def create_redis_health_check(redis_url: str) -> RedisHealthCheck:
    """Create a Redis health check"""
    return RedisHealthCheck(redis_url)


async def create_external_api_check(name: str, url: str, expected_status: int = 200) -> ExternalAPICheck:
    """Create an external API health check"""
    return ExternalAPICheck(name, url, expected_status)


async def create_system_resource_check() -> SystemResourceCheck:
    """Create a system resource health check"""
    return SystemResourceCheck()


def create_custom_health_check(name: str, check_function: Callable) -> CustomHealthCheck:
    """Create a custom health check"""
    return CustomHealthCheck(name, check_function) 