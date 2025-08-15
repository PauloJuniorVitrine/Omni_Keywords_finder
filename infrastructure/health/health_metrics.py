"""
Health Metrics System for Omni Keywords Finder

This module provides comprehensive metrics collection for health checks,
including integration with Prometheus and Grafana for monitoring and alerting.

Author: Paulo Júnior
Date: 2025-01-27
Tracing ID: HEALTH_METRICS_001
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
import json
import statistics

from .advanced_health_check import HealthStatus, HealthCheckResult
from .health_check_registry import HealthCheckCategory, HealthCheckPriority

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class HealthMetric:
    """Base health metric"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    labels: Dict[str, str] = field(default_factory=dict)
    description: str = ""


@dataclass
class HealthCheckMetrics:
    """Metrics for a specific health check"""
    check_name: str
    category: HealthCheckCategory
    priority: HealthCheckPriority
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    total_duration_ms: float = 0.0
    average_duration_ms: float = 0.0
    min_duration_ms: float = float('inf')
    max_duration_ms: float = 0.0
    last_success_time: Optional[datetime] = None
    last_failure_time: Optional[datetime] = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    status_distribution: Dict[HealthStatus, int] = field(default_factory=dict)
    error_counts: Dict[str, int] = field(default_factory=dict)
    response_time_history: List[float] = field(default_factory=list)
    max_history_size: int = 1000


class HealthMetricsCollector:
    """Collector for health check metrics"""
    
    def __init__(self):
        self.metrics: Dict[str, HealthCheckMetrics] = {}
        self.global_metrics: Dict[str, HealthMetric] = {}
        self.metric_callbacks: List[Callable] = []
        self.alert_callbacks: List[Callable] = []
        self._start_time = datetime.utcnow()
    
    def record_health_check_result(self, result: HealthCheckResult, metadata: Any):
        """Record metrics for a health check result"""
        check_name = result.name
        
        # Get or create metrics for this check
        if check_name not in self.metrics:
            self.metrics[check_name] = HealthCheckMetrics(
                check_name=check_name,
                category=getattr(metadata, 'category', HealthCheckCategory.CUSTOM),
                priority=getattr(metadata, 'priority', HealthCheckPriority.MEDIUM)
            )
        
        metrics = self.metrics[check_name]
        
        # Update basic metrics
        metrics.total_runs += 1
        metrics.total_duration_ms += result.duration_ms
        
        # Update success/failure counts
        if result.status == HealthStatus.HEALTHY:
            metrics.successful_runs += 1
            metrics.last_success_time = result.timestamp
            metrics.consecutive_successes += 1
            metrics.consecutive_failures = 0
        else:
            metrics.failed_runs += 1
            metrics.last_failure_time = result.timestamp
            metrics.consecutive_failures += 1
            metrics.consecutive_successes = 0
        
        # Update duration statistics
        if result.duration_ms < metrics.min_duration_ms:
            metrics.min_duration_ms = result.duration_ms
        if result.duration_ms > metrics.max_duration_ms:
            metrics.max_duration_ms = result.duration_ms
        
        # Update average duration
        metrics.average_duration_ms = metrics.total_duration_ms / metrics.total_runs
        
        # Update status distribution
        metrics.status_distribution[result.status] = (
            metrics.status_distribution.get(result.status, 0) + 1
        )
        
        # Update response time history
        metrics.response_time_history.append(result.duration_ms)
        if len(metrics.response_time_history) > metrics.max_history_size:
            metrics.response_time_history.pop(0)
        
        # Update error counts if there's an error
        if result.status != HealthStatus.HEALTHY and result.message:
            error_key = result.message.split(':')[0] if ':' in result.message else result.message
            metrics.error_counts[error_key] = metrics.error_counts.get(error_key, 0) + 1
        
        # Trigger callbacks
        self._trigger_metric_callbacks(check_name, metrics, result)
        
        # Check for alerts
        self._check_alerts(check_name, metrics, result)
    
    def _trigger_metric_callbacks(self, check_name: str, metrics: HealthCheckMetrics, result: HealthCheckResult):
        """Trigger metric callbacks"""
        for callback in self.metric_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(check_name, metrics, result))
                else:
                    callback(check_name, metrics, result)
            except Exception as e:
                logger.error(f"Error in metric callback: {str(e)}")
    
    def _check_alerts(self, check_name: str, metrics: HealthCheckMetrics, result: HealthCheckResult):
        """Check for alert conditions"""
        alerts = []
        
        # Check for consecutive failures
        if metrics.consecutive_failures >= 3:
            alerts.append({
                "type": "consecutive_failures",
                "check_name": check_name,
                "count": metrics.consecutive_failures,
                "threshold": 3,
                "severity": "warning"
            })
        
        if metrics.consecutive_failures >= 5:
            alerts.append({
                "type": "consecutive_failures",
                "check_name": check_name,
                "count": metrics.consecutive_failures,
                "threshold": 5,
                "severity": "critical"
            })
        
        # Check for high response times
        if result.duration_ms > 5000:  # 5 seconds
            alerts.append({
                "type": "high_response_time",
                "check_name": check_name,
                "duration_ms": result.duration_ms,
                "threshold": 5000,
                "severity": "warning"
            })
        
        if result.duration_ms > 10000:  # 10 seconds
            alerts.append({
                "type": "high_response_time",
                "check_name": check_name,
                "duration_ms": result.duration_ms,
                "threshold": 10000,
                "severity": "critical"
            })
        
        # Check for low success rate
        success_rate = metrics.successful_runs / metrics.total_runs if metrics.total_runs > 0 else 0.0
        if success_rate < 0.8:  # 80%
            alerts.append({
                "type": "low_success_rate",
                "check_name": check_name,
                "success_rate": success_rate,
                "threshold": 0.8,
                "severity": "warning"
            })
        
        if success_rate < 0.5:  # 50%
            alerts.append({
                "type": "low_success_rate",
                "check_name": check_name,
                "success_rate": success_rate,
                "threshold": 0.5,
                "severity": "critical"
            })
        
        # Trigger alert callbacks
        for alert in alerts:
            for callback in self.alert_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        asyncio.create_task(callback(alert))
                    else:
                        callback(alert)
                except Exception as e:
                    logger.error(f"Error in alert callback: {str(e)}")
    
    def add_metric_callback(self, callback: Callable):
        """Add a metric callback"""
        self.metric_callbacks.append(callback)
    
    def add_alert_callback(self, callback: Callable):
        """Add an alert callback"""
        self.alert_callbacks.append(callback)
    
    def get_check_metrics(self, check_name: str) -> Optional[HealthCheckMetrics]:
        """Get metrics for a specific health check"""
        return self.metrics.get(check_name)
    
    def get_all_metrics(self) -> Dict[str, HealthCheckMetrics]:
        """Get all health check metrics"""
        return self.metrics.copy()
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics"""
        total_checks = len(self.metrics)
        total_runs = sum(m.total_runs for m in self.metrics.values())
        total_successful = sum(m.successful_runs for m in self.metrics.values())
        total_failed = sum(m.failed_runs for m in self.metrics.values())
        
        overall_success_rate = total_successful / total_runs if total_runs > 0 else 0.0
        
        # Calculate average response times
        all_response_times = []
        for metrics in self.metrics.values():
            all_response_times.extend(metrics.response_time_history)
        
        avg_response_time = statistics.mean(all_response_times) if all_response_times else 0.0
        p95_response_time = statistics.quantiles(all_response_times, n=20)[-1] if len(all_response_times) >= 20 else 0.0
        p99_response_time = statistics.quantiles(all_response_times, n=100)[-1] if len(all_response_times) >= 100 else 0.0
        
        # Category breakdown
        category_metrics = {}
        for category in HealthCheckCategory:
            category_checks = [m for m in self.metrics.values() if m.category == category]
            if category_checks:
                category_runs = sum(m.total_runs for m in category_checks)
                category_successful = sum(m.successful_runs for m in category_checks)
                category_success_rate = category_successful / category_runs if category_runs > 0 else 0.0
                
                category_metrics[category.value] = {
                    "total_checks": len(category_checks),
                    "total_runs": category_runs,
                    "success_rate": category_success_rate,
                    "average_response_time_ms": statistics.mean(
                        [m.average_duration_ms for m in category_checks]
                    ) if category_checks else 0.0
                }
        
        return {
            "total_checks": total_checks,
            "total_runs": total_runs,
            "total_successful": total_successful,
            "total_failed": total_failed,
            "overall_success_rate": overall_success_rate,
            "average_response_time_ms": avg_response_time,
            "p95_response_time_ms": p95_response_time,
            "p99_response_time_ms": p99_response_time,
            "category_metrics": category_metrics,
            "collector_uptime_seconds": (datetime.utcnow() - self._start_time).total_seconds()
        }
    
    def get_prometheus_metrics(self) -> str:
        """Generate Prometheus format metrics"""
        lines = []
        
        # Health check metrics
        for check_name, metrics in self.metrics.items():
            labels = f'check_name="{check_name}",category="{metrics.category.value}",priority="{metrics.priority.value}"'
            
            # Success rate
            success_rate = metrics.successful_runs / metrics.total_runs if metrics.total_runs > 0 else 0.0
            lines.append(f'health_check_success_rate{{{labels}}} {success_rate}')
            
            # Total runs
            lines.append(f'health_check_total_runs{{{labels}}} {metrics.total_runs}')
            
            # Successful runs
            lines.append(f'health_check_successful_runs{{{labels}}} {metrics.successful_runs}')
            
            # Failed runs
            lines.append(f'health_check_failed_runs{{{labels}}} {metrics.failed_runs}')
            
            # Response time metrics
            lines.append(f'health_check_average_response_time_ms{{{labels}}} {metrics.average_duration_ms}')
            lines.append(f'health_check_min_response_time_ms{{{labels}}} {metrics.min_duration_ms}')
            lines.append(f'health_check_max_response_time_ms{{{labels}}} {metrics.max_duration_ms}')
            
            # Consecutive failures
            lines.append(f'health_check_consecutive_failures{{{labels}}} {metrics.consecutive_failures}')
            
            # Consecutive successes
            lines.append(f'health_check_consecutive_successes{{{labels}}} {metrics.consecutive_successes}')
        
        # Global metrics
        summary = self.get_metrics_summary()
        lines.append(f'health_check_overall_success_rate {summary["overall_success_rate"]}')
        lines.append(f'health_check_total_checks {summary["total_checks"]}')
        lines.append(f'health_check_total_runs {summary["total_runs"]}')
        lines.append(f'health_check_average_response_time_ms {summary["average_response_time_ms"]}')
        lines.append(f'health_check_p95_response_time_ms {summary["p95_response_time_ms"]}')
        lines.append(f'health_check_p99_response_time_ms {summary["p99_response_time_ms"]}')
        
        return '\n'.join(lines)
    
    def get_grafana_dashboard_config(self) -> Dict[str, Any]:
        """Generate Grafana dashboard configuration"""
        dashboard = {
            "dashboard": {
                "id": None,
                "title": "Omni Keywords Finder - Health Checks",
                "tags": ["health-checks", "omni-keywords-finder"],
                "timezone": "browser",
                "panels": [],
                "time": {
                    "from": "now-1h",
                    "to": "now"
                },
                "refresh": "30s"
            }
        }
        
        # Success rate panel
        success_rate_panel = {
            "id": 1,
            "title": "Health Check Success Rate",
            "type": "graph",
            "targets": [
                {
                    "expr": "health_check_success_rate",
                    "legendFormat": "{{check_name}}"
                }
            ],
            "yAxes": [
                {
                    "min": 0,
                    "max": 1,
                    "format": "percentunit"
                }
            ]
        }
        dashboard["dashboard"]["panels"].append(success_rate_panel)
        
        # Response time panel
        response_time_panel = {
            "id": 2,
            "title": "Health Check Response Time",
            "type": "graph",
            "targets": [
                {
                    "expr": "health_check_average_response_time_ms",
                    "legendFormat": "{{check_name}}"
                }
            ],
            "yAxes": [
                {
                    "format": "ms"
                }
            ]
        }
        dashboard["dashboard"]["panels"].append(response_time_panel)
        
        # Overall success rate panel
        overall_panel = {
            "id": 3,
            "title": "Overall System Health",
            "type": "stat",
            "targets": [
                {
                    "expr": "health_check_overall_success_rate",
                    "legendFormat": "Overall Success Rate"
                }
            ],
            "fieldConfig": {
                "defaults": {
                    "unit": "percentunit",
                    "thresholds": {
                        "steps": [
                            {"color": "red", "value": 0.8},
                            {"color": "yellow", "value": 0.9},
                            {"color": "green", "value": 1.0}
                        ]
                    }
                }
            }
        }
        dashboard["dashboard"]["panels"].append(overall_panel)
        
        return dashboard
    
    def clear_metrics(self, check_name: Optional[str] = None):
        """Clear metrics for a specific check or all checks"""
        if check_name:
            if check_name in self.metrics:
                del self.metrics[check_name]
                logger.info(f"Cleared metrics for health check '{check_name}'")
        else:
            self.metrics.clear()
            logger.info("Cleared all health check metrics")


# Global metrics collector
health_metrics_collector = HealthMetricsCollector()


# Convenience functions
def record_health_check_result(result: HealthCheckResult, metadata: Any):
    """Record health check result in the global metrics collector"""
    health_metrics_collector.record_health_check_result(result, metadata)


def get_check_metrics(check_name: str) -> Optional[HealthCheckMetrics]:
    """Get metrics for a specific health check from the global collector"""
    return health_metrics_collector.get_check_metrics(check_name)


def get_metrics_summary() -> Dict[str, Any]:
    """Get metrics summary from the global collector"""
    return health_metrics_collector.get_metrics_summary()


def get_prometheus_metrics() -> str:
    """Get Prometheus format metrics from the global collector"""
    return health_metrics_collector.get_prometheus_metrics()


def get_grafana_dashboard_config() -> Dict[str, Any]:
    """Get Grafana dashboard configuration from the global collector"""
    return health_metrics_collector.get_grafana_dashboard_config()


def add_metric_callback(callback: Callable):
    """Add a metric callback to the global collector"""
    health_metrics_collector.add_metric_callback(callback)


def add_alert_callback(callback: Callable):
    """Add an alert callback to the global collector"""
    health_metrics_collector.add_alert_callback(callback)


def clear_metrics(check_name: Optional[str] = None):
    """Clear metrics from the global collector"""
    health_metrics_collector.clear_metrics(check_name) 