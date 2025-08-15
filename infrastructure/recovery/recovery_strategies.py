"""
Recovery Strategies for Omni Keywords Finder

This module provides specific recovery strategies for the Omni Keywords Finder system.

Author: Paulo Júnior
Date: 2025-01-27
Tracing ID: RECOVERY_STRATEGIES_001
"""

from .auto_recovery import (
    BaseRecoveryStrategy,
    RecoveryResult,
    RecoveryStatus,
    RecoveryType,
    FailureType
)
from typing import Dict, Any
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DatabaseRecoveryStrategy(BaseRecoveryStrategy):
    """Strategy for database recovery"""
    
    def __init__(self, database_manager, **kwargs):
        super().__init__("database_recovery", **kwargs)
        self.database_manager = database_manager
    
    async def can_recover(self, failure_type: FailureType, context: Dict[str, Any]) -> bool:
        return failure_type == FailureType.DATABASE_ERROR
    
    async def execute_recovery(self, failure_type: FailureType, context: Dict[str, Any]) -> RecoveryResult:
        result = RecoveryResult(
            action_name=self.name,
            recovery_type=RecoveryType.DATABASE_RECOVERY,
            status=RecoveryStatus.IN_PROGRESS
        )
        
        try:
            logger.info("Starting database recovery")
            
            # Attempt to reconnect to database
            if hasattr(self.database_manager, 'reconnect'):
                await self.database_manager.reconnect()
            
            result.status = RecoveryStatus.SUCCESSFUL
            result.details = {"database_recovery": "successful"}
            
        except Exception as e:
            result.status = RecoveryStatus.FAILED
            result.error_message = str(e)
        
        finally:
            result.end_time = datetime.utcnow()
            result.duration_seconds = (result.end_time - result.start_time).total_seconds()
            self.add_to_history(result)
        
        return result


class CacheRecoveryStrategy(BaseRecoveryStrategy):
    """Strategy for cache recovery"""
    
    def __init__(self, cache_manager, **kwargs):
        super().__init__("cache_recovery", **kwargs)
        self.cache_manager = cache_manager
    
    async def can_recover(self, failure_type: FailureType, context: Dict[str, Any]) -> bool:
        return failure_type == FailureType.CACHE_CORRUPTION
    
    async def execute_recovery(self, failure_type: FailureType, context: Dict[str, Any]) -> RecoveryResult:
        result = RecoveryResult(
            action_name=self.name,
            recovery_type=RecoveryType.CACHE_CLEAR,
            status=RecoveryStatus.IN_PROGRESS
        )
        
        try:
            logger.info("Starting cache recovery")
            
            # Clear and reinitialize cache
            if hasattr(self.cache_manager, 'clear'):
                await self.cache_manager.clear()
            
            result.status = RecoveryStatus.SUCCESSFUL
            result.details = {"cache_recovery": "successful"}
            
        except Exception as e:
            result.status = RecoveryStatus.FAILED
            result.error_message = str(e)
        
        finally:
            result.end_time = datetime.utcnow()
            result.duration_seconds = (result.end_time - result.start_time).total_seconds()
            self.add_to_history(result)
        
        return result 