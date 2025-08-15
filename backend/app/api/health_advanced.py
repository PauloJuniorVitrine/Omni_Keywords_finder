"""
Advanced Health Checks API
Tracing ID: FINE_TUNING_IMPLEMENTATION_20250127_001
Created: 2025-01-27
Version: 1.0

This module provides comprehensive health checks for the Omni Keywords Finder system,
including service-specific checks, dependency verification, and performance metrics.
"""

import time
import psutil
import sqlite3
import redis
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from flask import Blueprint, jsonify, current_app
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from backend.app.middleware.tracing_middleware import trace_operation, get_current_correlation_id

# Health check blueprint
health_bp = Blueprint('health_advanced', __name__, url_prefix='/api/health')

class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class HealthCheckResult:
    """Result of a health check."""
    name: str
    status: HealthStatus
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    duration: float
    correlation_id: Optional[str] = None

@dataclass
class SystemMetrics:
    """System performance metrics."""
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io: Dict[str, float]
    uptime: float
    load_average: List[float]

class HealthChecker:
    """
    Comprehensive health checker for the Omni Keywords Finder system.
    
    Provides:
    - Service-specific health checks
    - Dependency verification
    - Performance metrics collection
    - Detailed status reporting
    """
    
    def __init__(self):
        self.start_time = time.time()
        self.check_results: List[HealthCheckResult] = []
    
    def check_database_health(self) -> HealthCheckResult:
        """Check database connectivity and performance."""
        start_time = time.time()
        correlation_id = get_current_correlation_id()
        
        try:
            # Test basic connectivity
            db = current_app.db
            result = db.session.execute(text("SELECT 1")).fetchone()
            
            if not result or result[0] != 1:
                return HealthCheckResult(
                    name="database_connectivity",
                    status=HealthStatus.UNHEALTHY,
                    message="Database connectivity test failed",
                    details={"error": "SELECT 1 returned unexpected result"},
                    timestamp=datetime.utcnow(),
                    duration=time.time() - start_time,
                    correlation_id=correlation_id
                )
            
            # Test query performance
            query_start = time.time()
            db.session.execute(text("SELECT COUNT(*) FROM nichos"))
            query_duration = time.time() - query_start
            
            # Check database size
            db_size = self._get_database_size()
            
            details = {
                "query_performance_ms": round(query_duration * 1000, 2),
                "database_size_mb": db_size,
                "connection_pool_size": db.engine.pool.size(),
                "connection_pool_checked_in": db.engine.pool.checkedin(),
                "connection_pool_checked_out": db.engine.pool.checkedout(),
            }
            
            status = HealthStatus.HEALTHY
            if query_duration > 1.0:  # More than 1 second
                status = HealthStatus.DEGRADED
                details["warning"] = "Query performance is degraded"
            
            return HealthCheckResult(
                name="database_health",
                status=status,
                message="Database is operational",
                details=details,
                timestamp=datetime.utcnow(),
                duration=time.time() - start_time,
                correlation_id=correlation_id
            )
            
        except SQLAlchemyError as e:
            return HealthCheckResult(
                name="database_health",
                status=HealthStatus.UNHEALTHY,
                message="Database connection failed",
                details={"error": str(e), "error_type": type(e).__name__},
                timestamp=datetime.utcnow(),
                duration=time.time() - start_time,
                correlation_id=correlation_id
            )
        except Exception as e:
            return HealthCheckResult(
                name="database_health",
                status=HealthStatus.UNKNOWN,
                message="Database check failed with unexpected error",
                details={"error": str(e), "error_type": type(e).__name__},
                timestamp=datetime.utcnow(),
                duration=time.time() - start_time,
                correlation_id=correlation_id
            )
    
    def check_redis_health(self) -> HealthCheckResult:
        """Check Redis connectivity and performance."""
        start_time = time.time()
        correlation_id = get_current_correlation_id()
        
        try:
            # Get Redis connection
            redis_client = current_app.redis if hasattr(current_app, 'redis') else None
            
            if not redis_client:
                return HealthCheckResult(
                    name="redis_health",
                    status=HealthStatus.UNKNOWN,
                    message="Redis client not configured",
                    details={"warning": "Redis client not available"},
                    timestamp=datetime.utcnow(),
                    duration=time.time() - start_time,
                    correlation_id=correlation_id
                )
            
            # Test basic connectivity
            redis_client.ping()
            
            # Test write/read performance
            test_key = f"health_check_{int(time.time())}"
            test_value = "test_value"
            
            write_start = time.time()
            redis_client.set(test_key, test_value, ex=60)  # 60 seconds TTL
            write_duration = time.time() - write_start
            
            read_start = time.time()
            retrieved_value = redis_client.get(test_key)
            read_duration = time.time() - read_start
            
            # Clean up
            redis_client.delete(test_key)
            
            # Get Redis info
            info = redis_client.info()
            
            details = {
                "write_performance_ms": round(write_duration * 1000, 2),
                "read_performance_ms": round(read_duration * 1000, 2),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "N/A"),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
            }
            
            # Calculate hit rate
            total_requests = details["keyspace_hits"] + details["keyspace_misses"]
            if total_requests > 0:
                details["hit_rate_percent"] = round(
                    (details["keyspace_hits"] / total_requests) * 100, 2
                )
            
            status = HealthStatus.HEALTHY
            if write_duration > 0.1 or read_duration > 0.1:  # More than 100ms
                status = HealthStatus.DEGRADED
                details["warning"] = "Redis performance is degraded"
            
            return HealthCheckResult(
                name="redis_health",
                status=status,
                message="Redis is operational",
                details=details,
                timestamp=datetime.utcnow(),
                duration=time.time() - start_time,
                correlation_id=correlation_id
            )
            
        except redis.ConnectionError as e:
            return HealthCheckResult(
                name="redis_health",
                status=HealthStatus.UNHEALTHY,
                message="Redis connection failed",
                details={"error": str(e), "error_type": "ConnectionError"},
                timestamp=datetime.utcnow(),
                duration=time.time() - start_time,
                correlation_id=correlation_id
            )
        except Exception as e:
            return HealthCheckResult(
                name="redis_health",
                status=HealthStatus.UNKNOWN,
                message="Redis check failed with unexpected error",
                details={"error": str(e), "error_type": type(e).__name__},
                timestamp=datetime.utcnow(),
                duration=time.time() - start_time,
                correlation_id=correlation_id
            )
    
    def check_external_services(self) -> HealthCheckResult:
        """Check external service dependencies."""
        start_time = time.time()
        correlation_id = get_current_correlation_id()
        
        services = {
            "google_search": "https://www.google.com",
            "github_api": "https://api.github.com",
            "openai_api": "https://api.openai.com/v1/models",
        }
        
        results = {}
        overall_status = HealthStatus.HEALTHY
        
        for service_name, url in services.items():
            try:
                service_start = time.time()
                response = requests.get(url, timeout=5)
                service_duration = time.time() - service_start
                
                if response.status_code < 400:
                    results[service_name] = {
                        "status": "healthy",
                        "response_time_ms": round(service_duration * 1000, 2),
                        "status_code": response.status_code
                    }
                else:
                    results[service_name] = {
                        "status": "degraded",
                        "response_time_ms": round(service_duration * 1000, 2),
                        "status_code": response.status_code,
                        "warning": f"HTTP {response.status_code}"
                    }
                    overall_status = HealthStatus.DEGRADED
                    
            except requests.exceptions.Timeout:
                results[service_name] = {
                    "status": "unhealthy",
                    "error": "Timeout after 5 seconds"
                }
                overall_status = HealthStatus.UNHEALTHY
            except requests.exceptions.ConnectionError:
                results[service_name] = {
                    "status": "unhealthy",
                    "error": "Connection failed"
                }
                overall_status = HealthStatus.UNHEALTHY
            except Exception as e:
                results[service_name] = {
                    "status": "unknown",
                    "error": str(e)
                }
                if overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.UNKNOWN
        
        message = "External services check completed"
        if overall_status == HealthStatus.DEGRADED:
            message = "Some external services are degraded"
        elif overall_status == HealthStatus.UNHEALTHY:
            message = "External services are unhealthy"
        
        return HealthCheckResult(
            name="external_services",
            status=overall_status,
            message=message,
            details={"services": results},
            timestamp=datetime.utcnow(),
            duration=time.time() - start_time,
            correlation_id=correlation_id
        )
    
    def check_system_metrics(self) -> HealthCheckResult:
        """Check system performance metrics."""
        start_time = time.time()
        correlation_id = get_current_correlation_id()
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Network I/O
            network = psutil.net_io_counters()
            network_io = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv,
            }
            
            # System uptime
            uptime = time.time() - psutil.boot_time()
            
            # Load average (Unix-like systems)
            try:
                load_average = psutil.getloadavg()
            except AttributeError:
                load_average = [0, 0, 0]  # Windows doesn't have load average
            
            # Determine status based on thresholds
            status = HealthStatus.HEALTHY
            warnings = []
            
            if cpu_percent > 80:
                status = HealthStatus.DEGRADED
                warnings.append("High CPU usage")
            
            if memory_percent > 85:
                status = HealthStatus.DEGRADED
                warnings.append("High memory usage")
            
            if disk_percent > 90:
                status = HealthStatus.DEGRADED
                warnings.append("High disk usage")
            
            if status == HealthStatus.DEGRADED and len(warnings) > 2:
                status = HealthStatus.UNHEALTHY
            
            details = {
                "cpu_percent": round(cpu_percent, 2),
                "memory_percent": round(memory_percent, 2),
                "disk_percent": round(disk_percent, 2),
                "network_io": network_io,
                "uptime_seconds": round(uptime, 2),
                "load_average": [round(load, 2) for load in load_average],
                "warnings": warnings if warnings else None
            }
            
            message = "System metrics are normal"
            if warnings:
                message = f"System warnings: {', '.join(warnings)}"
            
            return HealthCheckResult(
                name="system_metrics",
                status=status,
                message=message,
                details=details,
                timestamp=datetime.utcnow(),
                duration=time.time() - start_time,
                correlation_id=correlation_id
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="system_metrics",
                status=HealthStatus.UNKNOWN,
                message="Failed to collect system metrics",
                details={"error": str(e), "error_type": type(e).__name__},
                timestamp=datetime.utcnow(),
                duration=time.time() - start_time,
                correlation_id=correlation_id
            )
    
    def check_application_health(self) -> HealthCheckResult:
        """Check application-specific health indicators."""
        start_time = time.time()
        correlation_id = get_current_correlation_id()
        
        try:
            # Check application uptime
            app_uptime = time.time() - self.start_time
            
            # Check active sessions (if available)
            active_sessions = 0
            if hasattr(current_app, 'session_interface'):
                # This would need to be implemented based on your session storage
                active_sessions = 0
            
            # Check background tasks (if available)
            background_tasks = {
                "running": 0,
                "queued": 0,
                "failed": 0
            }
            
            # Check feature flags
            feature_flags = {
                "enabled": 0,
                "disabled": 0,
                "total": 0
            }
            
            details = {
                "application_uptime_seconds": round(app_uptime, 2),
                "active_sessions": active_sessions,
                "background_tasks": background_tasks,
                "feature_flags": feature_flags,
                "version": current_app.config.get('VERSION', 'unknown'),
                "environment": current_app.config.get('ENVIRONMENT', 'unknown'),
            }
            
            return HealthCheckResult(
                name="application_health",
                status=HealthStatus.HEALTHY,
                message="Application is healthy",
                details=details,
                timestamp=datetime.utcnow(),
                duration=time.time() - start_time,
                correlation_id=correlation_id
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="application_health",
                status=HealthStatus.UNKNOWN,
                message="Application health check failed",
                details={"error": str(e), "error_type": type(e).__name__},
                timestamp=datetime.utcnow(),
                duration=time.time() - start_time,
                correlation_id=correlation_id
            )
    
    def _get_database_size(self) -> float:
        """Get database size in MB."""
        try:
            db_path = current_app.config.get('DATABASE_PATH', 'backend/db.sqlite3')
            import os
            size_bytes = os.path.getsize(db_path)
            return round(size_bytes / (1024 * 1024), 2)  # Convert to MB
        except Exception:
            return 0.0
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks and return comprehensive results."""
        checks = [
            self.check_database_health,
            self.check_redis_health,
            self.check_external_services,
            self.check_system_metrics,
            self.check_application_health,
        ]
        
        results = []
        overall_status = HealthStatus.HEALTHY
        
        for check_func in checks:
            result = check_func()
            results.append(result)
            
            # Determine overall status
            if result.status == HealthStatus.UNHEALTHY:
                overall_status = HealthStatus.UNHEALTHY
            elif result.status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                overall_status = HealthStatus.DEGRADED
            elif result.status == HealthStatus.UNKNOWN and overall_status == HealthStatus.HEALTHY:
                overall_status = HealthStatus.UNKNOWN
        
        # Calculate total duration
        total_duration = sum(result.duration for result in results)
        
        return {
            "status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "duration_ms": round(total_duration * 1000, 2),
            "checks": [asdict(result) for result in results],
            "summary": {
                "total_checks": len(results),
                "healthy": len([r for r in results if r.status == HealthStatus.HEALTHY]),
                "degraded": len([r for r in results if r.status == HealthStatus.DEGRADED]),
                "unhealthy": len([r for r in results if r.status == HealthStatus.UNHEALTHY]),
                "unknown": len([r for r in results if r.status == HealthStatus.UNKNOWN]),
            }
        }


# Global health checker instance
health_checker = HealthChecker()


@health_bp.route('/detailed', methods=['GET'])
@trace_operation("health_check_detailed")
def detailed_health_check():
    """Comprehensive health check endpoint."""
    try:
        results = health_checker.run_all_checks()
        return jsonify(results), 200 if results["status"] != "unhealthy" else 503
    except Exception as e:
        return jsonify({
            "status": "unknown",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500


@health_bp.route('/simple', methods=['GET'])
@trace_operation("health_check_simple")
def simple_health_check():
    """Simple health check endpoint for load balancers."""
    try:
        # Quick database check
        db = current_app.db
        db.session.execute(text("SELECT 1"))
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 503


@health_bp.route('/database', methods=['GET'])
@trace_operation("health_check_database")
def database_health_check():
    """Database-specific health check."""
    result = health_checker.check_database_health()
    return jsonify(asdict(result)), 200 if result.status != HealthStatus.UNHEALTHY else 503


@health_bp.route('/redis', methods=['GET'])
@trace_operation("health_check_redis")
def redis_health_check():
    """Redis-specific health check."""
    result = health_checker.check_redis_health()
    return jsonify(asdict(result)), 200 if result.status != HealthStatus.UNHEALTHY else 503


@health_bp.route('/system', methods=['GET'])
@trace_operation("health_check_system")
def system_health_check():
    """System metrics health check."""
    result = health_checker.check_system_metrics()
    return jsonify(asdict(result)), 200 if result.status != HealthStatus.UNHEALTHY else 503


@health_bp.route('/external', methods=['GET'])
@trace_operation("health_check_external")
def external_services_health_check():
    """External services health check."""
    result = health_checker.check_external_services()
    return jsonify(asdict(result)), 200 if result.status != HealthStatus.UNHEALTHY else 503 