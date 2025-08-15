"""
Health Check Registry for Omni Keywords Finder

This module provides a centralized registry for managing health checks,
including categorization, prioritization, and dynamic registration.

Author: Paulo Júnior
Date: 2025-01-27
Tracing ID: HEALTH_REGISTRY_001
"""

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Set
from datetime import datetime, timedelta
from .advanced_health_check import BaseHealthCheck, HealthStatus, HealthCheckResult

logger = logging.getLogger(__name__)


class HealthCheckPriority(Enum):
    """Priority levels for health checks"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class HealthCheckCategory(Enum):
    """Categories for health checks"""
    INFRASTRUCTURE = "infrastructure"
    DATABASE = "database"
    CACHE = "cache"
    EXTERNAL_API = "external_api"
    SYSTEM_RESOURCES = "system_resources"
    BUSINESS_LOGIC = "business_logic"
    SECURITY = "security"
    PERFORMANCE = "performance"


@dataclass
class HealthCheckMetadata:
    """Metadata for health checks"""
    name: str
    category: HealthCheckCategory
    priority: HealthCheckPriority
    description: str = ""
    tags: Set[str] = field(default_factory=set)
    enabled: bool = True
    timeout_seconds: float = 30.0
    retry_attempts: int = 3
    check_interval_seconds: float = 60.0
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    failure_count: int = 0
    success_count: int = 0
    total_runs: int = 0


class HealthCheckRegistry:
    """Centralized registry for health checks"""
    
    def __init__(self):
        self._health_checks: Dict[str, BaseHealthCheck] = {}
        self._metadata: Dict[str, HealthCheckMetadata] = {}
        self._categories: Dict[HealthCheckCategory, Set[str]] = {
            category: set() for category in HealthCheckCategory
        }
        self._priorities: Dict[HealthCheckPriority, Set[str]] = {
            priority: set() for priority in HealthCheckPriority
        }
        self._enabled_checks: Set[str] = set()
        self._disabled_checks: Set[str] = set()
        self._last_registry_update: Optional[datetime] = None
    
    def register_health_check(
        self,
        health_check: BaseHealthCheck,
        category: HealthCheckCategory,
        priority: HealthCheckPriority,
        description: str = "",
        tags: Optional[Set[str]] = None,
        enabled: bool = True,
        timeout_seconds: float = 30.0,
        retry_attempts: int = 3,
        check_interval_seconds: float = 60.0
    ) -> bool:
        """
        Register a health check with metadata
        
        Returns:
            bool: True if registration was successful, False otherwise
        """
        try:
            name = health_check.name
            
            # Check if already registered
            if name in self._health_checks:
                logger.warning(f"Health check '{name}' is already registered")
                return False
            
            # Register health check
            self._health_checks[name] = health_check
            
            # Create metadata
            metadata = HealthCheckMetadata(
                name=name,
                category=category,
                priority=priority,
                description=description,
                tags=tags or set(),
                enabled=enabled,
                timeout_seconds=timeout_seconds,
                retry_attempts=retry_attempts,
                check_interval_seconds=check_interval_seconds
            )
            self._metadata[name] = metadata
            
            # Update indexes
            self._categories[category].add(name)
            self._priorities[priority].add(name)
            
            if enabled:
                self._enabled_checks.add(name)
            else:
                self._disabled_checks.add(name)
            
            self._last_registry_update = datetime.utcnow()
            
            logger.info(f"Registered health check '{name}' in category '{category.value}' with priority '{priority.value}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register health check '{health_check.name}': {str(e)}")
            return False
    
    def unregister_health_check(self, name: str) -> bool:
        """
        Unregister a health check
        
        Returns:
            bool: True if unregistration was successful, False otherwise
        """
        try:
            if name not in self._health_checks:
                logger.warning(f"Health check '{name}' is not registered")
                return False
            
            # Get metadata for cleanup
            metadata = self._metadata.get(name)
            
            # Remove from health checks
            del self._health_checks[name]
            
            # Remove metadata
            if metadata:
                del self._metadata[name]
                
                # Clean up indexes
                self._categories[metadata.category].discard(name)
                self._priorities[metadata.priority].discard(name)
                self._enabled_checks.discard(name)
                self._disabled_checks.discard(name)
            
            self._last_registry_update = datetime.utcnow()
            
            logger.info(f"Unregistered health check '{name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister health check '{name}': {str(e)}")
            return False
    
    def get_health_check(self, name: str) -> Optional[BaseHealthCheck]:
        """Get a health check by name"""
        return self._health_checks.get(name)
    
    def get_metadata(self, name: str) -> Optional[HealthCheckMetadata]:
        """Get metadata for a health check"""
        return self._metadata.get(name)
    
    def list_health_checks(
        self,
        category: Optional[HealthCheckCategory] = None,
        priority: Optional[HealthCheckPriority] = None,
        enabled_only: bool = False
    ) -> List[str]:
        """List health check names based on filters"""
        checks = set(self._health_checks.keys())
        
        if category:
            checks &= self._categories[category]
        
        if priority:
            checks &= self._priorities[priority]
        
        if enabled_only:
            checks &= self._enabled_checks
        
        return sorted(list(checks))
    
    def get_health_checks_by_category(self, category: HealthCheckCategory) -> Dict[str, BaseHealthCheck]:
        """Get all health checks in a specific category"""
        check_names = self._categories[category]
        return {name: self._health_checks[name] for name in check_names if name in self._health_checks}
    
    def get_health_checks_by_priority(self, priority: HealthCheckPriority) -> Dict[str, BaseHealthCheck]:
        """Get all health checks with a specific priority"""
        check_names = self._priorities[priority]
        return {name: self._health_checks[name] for name in check_names if name in self._health_checks}
    
    def enable_health_check(self, name: str) -> bool:
        """Enable a health check"""
        if name not in self._health_checks:
            logger.warning(f"Health check '{name}' is not registered")
            return False
        
        if name in self._enabled_checks:
            logger.info(f"Health check '{name}' is already enabled")
            return True
        
        self._enabled_checks.add(name)
        self._disabled_checks.discard(name)
        
        if name in self._metadata:
            self._metadata[name].enabled = True
        
        logger.info(f"Enabled health check '{name}'")
        return True
    
    def disable_health_check(self, name: str) -> bool:
        """Disable a health check"""
        if name not in self._health_checks:
            logger.warning(f"Health check '{name}' is not registered")
            return False
        
        if name in self._disabled_checks:
            logger.info(f"Health check '{name}' is already disabled")
            return True
        
        self._disabled_checks.add(name)
        self._enabled_checks.discard(name)
        
        if name in self._metadata:
            self._metadata[name].enabled = False
        
        logger.info(f"Disabled health check '{name}'")
        return True
    
    def update_metadata(
        self,
        name: str,
        category: Optional[HealthCheckCategory] = None,
        priority: Optional[HealthCheckPriority] = None,
        description: Optional[str] = None,
        tags: Optional[Set[str]] = None,
        timeout_seconds: Optional[float] = None,
        retry_attempts: Optional[int] = None,
        check_interval_seconds: Optional[float] = None
    ) -> bool:
        """Update metadata for a health check"""
        if name not in self._metadata:
            logger.warning(f"Health check '{name}' metadata not found")
            return False
        
        try:
            metadata = self._metadata[name]
            
            # Update category if provided
            if category and category != metadata.category:
                self._categories[metadata.category].discard(name)
                self._categories[category].add(name)
                metadata.category = category
            
            # Update priority if provided
            if priority and priority != metadata.priority:
                self._priorities[metadata.priority].discard(name)
                self._priorities[priority].add(name)
                metadata.priority = priority
            
            # Update other fields
            if description is not None:
                metadata.description = description
            
            if tags is not None:
                metadata.tags = tags
            
            if timeout_seconds is not None:
                metadata.timeout_seconds = timeout_seconds
            
            if retry_attempts is not None:
                metadata.retry_attempts = retry_attempts
            
            if check_interval_seconds is not None:
                metadata.check_interval_seconds = check_interval_seconds
            
            self._last_registry_update = datetime.utcnow()
            
            logger.info(f"Updated metadata for health check '{name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update metadata for health check '{name}': {str(e)}")
            return False
    
    def get_registry_summary(self) -> Dict[str, Any]:
        """Get a summary of the registry"""
        total_checks = len(self._health_checks)
        enabled_checks = len(self._enabled_checks)
        disabled_checks = len(self._disabled_checks)
        
        category_counts = {
            category.value: len(checks) 
            for category, checks in self._categories.items()
        }
        
        priority_counts = {
            priority.value: len(checks) 
            for priority, checks in self._priorities.items()
        }
        
        return {
            "total_checks": total_checks,
            "enabled_checks": enabled_checks,
            "disabled_checks": disabled_checks,
            "category_counts": category_counts,
            "priority_counts": priority_counts,
            "last_update": self._last_registry_update.isoformat() if self._last_registry_update else None
        }
    
    def get_health_check_status(self, name: str) -> Optional[Dict[str, Any]]:
        """Get detailed status for a health check"""
        if name not in self._health_checks or name not in self._metadata:
            return None
        
        health_check = self._health_checks[name]
        metadata = self._metadata[name]
        
        return {
            "name": name,
            "category": metadata.category.value,
            "priority": metadata.priority.value,
            "description": metadata.description,
            "tags": list(metadata.tags),
            "enabled": metadata.enabled,
            "timeout_seconds": metadata.timeout_seconds,
            "retry_attempts": metadata.retry_attempts,
            "check_interval_seconds": metadata.check_interval_seconds,
            "last_run": metadata.last_run.isoformat() if metadata.last_run else None,
            "next_run": metadata.next_run.isoformat() if metadata.next_run else None,
            "failure_count": metadata.failure_count,
            "success_count": metadata.success_count,
            "total_runs": metadata.total_runs,
            "success_rate": metadata.success_count / metadata.total_runs if metadata.total_runs > 0 else 0.0,
            "last_check_result": health_check.last_check.to_dict() if health_check.last_check else None
        }
    
    def update_check_statistics(self, name: str, result: HealthCheckResult):
        """Update statistics for a health check after execution"""
        if name not in self._metadata:
            return
        
        metadata = self._metadata[name]
        metadata.last_run = datetime.utcnow()
        metadata.next_run = metadata.last_run + timedelta(seconds=metadata.check_interval_seconds)
        metadata.total_runs += 1
        
        if result.status == HealthStatus.HEALTHY:
            metadata.success_count += 1
        else:
            metadata.failure_count += 1
    
    def get_due_checks(self) -> List[str]:
        """Get list of health checks that are due to run"""
        now = datetime.utcnow()
        due_checks = []
        
        for name in self._enabled_checks:
            metadata = self._metadata.get(name)
            if metadata and metadata.next_run and metadata.next_run <= now:
                due_checks.append(name)
        
        return due_checks
    
    def clear_statistics(self, name: Optional[str] = None):
        """Clear statistics for health checks"""
        if name:
            if name in self._metadata:
                metadata = self._metadata[name]
                metadata.failure_count = 0
                metadata.success_count = 0
                metadata.total_runs = 0
                metadata.last_run = None
                metadata.next_run = None
                logger.info(f"Cleared statistics for health check '{name}'")
        else:
            for metadata in self._metadata.values():
                metadata.failure_count = 0
                metadata.success_count = 0
                metadata.total_runs = 0
                metadata.last_run = None
                metadata.next_run = None
            logger.info("Cleared statistics for all health checks")


# Global registry instance
health_check_registry = HealthCheckRegistry()


# Convenience functions
def register_health_check(
    health_check: BaseHealthCheck,
    category: HealthCheckCategory,
    priority: HealthCheckPriority,
    description: str = "",
    tags: Optional[Set[str]] = None,
    enabled: bool = True,
    timeout_seconds: float = 30.0,
    retry_attempts: int = 3,
    check_interval_seconds: float = 60.0
) -> bool:
    """Register a health check in the global registry"""
    return health_check_registry.register_health_check(
        health_check=health_check,
        category=category,
        priority=priority,
        description=description,
        tags=tags,
        enabled=enabled,
        timeout_seconds=timeout_seconds,
        retry_attempts=retry_attempts,
        check_interval_seconds=check_interval_seconds
    )


def unregister_health_check(name: str) -> bool:
    """Unregister a health check from the global registry"""
    return health_check_registry.unregister_health_check(name)


def get_health_check(name: str) -> Optional[BaseHealthCheck]:
    """Get a health check from the global registry"""
    return health_check_registry.get_health_check(name)


def list_health_checks(
    category: Optional[HealthCheckCategory] = None,
    priority: Optional[HealthCheckPriority] = None,
    enabled_only: bool = False
) -> List[str]:
    """List health checks from the global registry"""
    return health_check_registry.list_health_checks(category, priority, enabled_only)


def get_registry_summary() -> Dict[str, Any]:
    """Get summary of the global registry"""
    return health_check_registry.get_registry_summary() 