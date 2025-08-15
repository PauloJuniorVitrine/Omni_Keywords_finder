"""
Recovery Manager for Omni Keywords Finder

This module provides integration between health checks and recovery strategies.

Author: Paulo Júnior
Date: 2025-01-27
Tracing ID: RECOVERY_MANAGER_001
"""

from .auto_recovery import (
    AutoRecoveryManager,
    RecoveryConfig,
    FailureType,
    RecoveryResult
)
from infrastructure.health import HealthStatus, HealthCheckResult
from typing import Dict, Any, List
import asyncio
import logging

logger = logging.getLogger(__name__)


class RecoveryManager:
    """Manager that integrates health checks with recovery strategies"""
    
    def __init__(self, config: RecoveryConfig = None):
        self.auto_recovery_manager = AutoRecoveryManager(config)
        self.health_to_failure_mapping = {
            HealthStatus.UNHEALTHY: FailureType.SERVICE_CRASH,
            HealthStatus.DEGRADED: FailureType.TIMEOUT
        }
    
    async def handle_health_check_result(self, health_result: HealthCheckResult) -> List[RecoveryResult]:
        """Handle health check result and trigger recovery if needed"""
        if health_result.status == HealthStatus.HEALTHY:
            return []
        
        # Map health status to failure type
        failure_type = self.health_to_failure_mapping.get(health_result.status, FailureType.CUSTOM)
        
        # Create context from health check result
        context = {
            "health_check_name": health_result.name,
            "health_check_message": health_result.message,
            "health_check_details": health_result.details,
            "health_check_duration_ms": health_result.duration_ms
        }
        
        # Trigger recovery
        return await self.auto_recovery_manager.trigger_recovery(failure_type, context)
    
    def add_recovery_strategy(self, strategy):
        """Add a recovery strategy"""
        self.auto_recovery_manager.add_recovery_strategy(strategy)
    
    def get_recovery_summary(self) -> Dict[str, Any]:
        """Get recovery summary"""
        return self.auto_recovery_manager.get_recovery_summary()


# Global recovery manager
recovery_manager = RecoveryManager() 