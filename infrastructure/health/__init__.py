"""
Health Check System for Omni Keywords Finder

This package provides comprehensive health checking capabilities including:
- Advanced health checks for different services
- Health check registry and scheduling
- Metrics collection and monitoring
- Integration with observability systems

Author: Paulo Júnior
Date: 2025-01-27
Tracing ID: HEALTH_INIT_001
"""

from .advanced_health_check import (
    HealthStatus,
    HealthCheckType,
    HealthCheckResult,
    HealthCheckConfig,
    BaseHealthCheck,
    DatabaseHealthCheck,
    RedisHealthCheck,
    ExternalAPICheck,
    SystemResourceCheck,
    CustomHealthCheck,
    AdvancedHealthChecker,
    create_database_health_check,
    create_redis_health_check,
    create_external_api_check,
    create_system_resource_check,
    create_custom_health_check
)

from .health_check_registry import (
    HealthCheckPriority,
    HealthCheckCategory,
    HealthCheckMetadata,
    HealthCheckRegistry,
    health_check_registry,
    register_health_check,
    unregister_health_check,
    get_health_check,
    list_health_checks,
    get_registry_summary
)

from .health_check_scheduler import (
    SchedulerState,
    SchedulerConfig,
    SchedulerMetrics,
    HealthCheckScheduler,
    health_check_scheduler,
    start_health_check_scheduler,
    stop_health_check_scheduler,
    get_scheduler_status,
    add_notification_callback,
    add_error_callback
)

from .health_metrics import (
    MetricType,
    HealthMetric,
    HealthCheckMetrics,
    HealthMetricsCollector,
    health_metrics_collector,
    record_health_check_result,
    get_check_metrics,
    get_metrics_summary,
    get_prometheus_metrics,
    get_grafana_dashboard_config,
    add_metric_callback,
    add_alert_callback,
    clear_metrics
)

__version__ = "1.0.0"
__author__ = "Paulo Júnior"
__email__ = "paulo.junior@omni-keywords-finder.com"

__all__ = [
    # Advanced Health Check
    "HealthStatus",
    "HealthCheckType", 
    "HealthCheckResult",
    "HealthCheckConfig",
    "BaseHealthCheck",
    "DatabaseHealthCheck",
    "RedisHealthCheck",
    "ExternalAPICheck",
    "SystemResourceCheck",
    "CustomHealthCheck",
    "AdvancedHealthChecker",
    "create_database_health_check",
    "create_redis_health_check",
    "create_external_api_check",
    "create_system_resource_check",
    "create_custom_health_check",
    
    # Health Check Registry
    "HealthCheckPriority",
    "HealthCheckCategory",
    "HealthCheckMetadata",
    "HealthCheckRegistry",
    "health_check_registry",
    "register_health_check",
    "unregister_health_check",
    "get_health_check",
    "list_health_checks",
    "get_registry_summary",
    
    # Health Check Scheduler
    "SchedulerState",
    "SchedulerConfig",
    "SchedulerMetrics",
    "HealthCheckScheduler",
    "health_check_scheduler",
    "start_health_check_scheduler",
    "stop_health_check_scheduler",
    "get_scheduler_status",
    "add_notification_callback",
    "add_error_callback",
    
    # Health Metrics
    "MetricType",
    "HealthMetric",
    "HealthCheckMetrics",
    "HealthMetricsCollector",
    "health_metrics_collector",
    "record_health_check_result",
    "get_check_metrics",
    "get_metrics_summary",
    "get_prometheus_metrics",
    "get_grafana_dashboard_config",
    "add_metric_callback",
    "add_alert_callback",
    "clear_metrics"
] 