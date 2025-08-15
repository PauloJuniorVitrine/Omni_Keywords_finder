"""
Auto-Recovery System for Omni Keywords Finder

This package provides automatic recovery mechanisms for different types of failures.

Author: Paulo Júnior
Date: 2025-01-27
Tracing ID: RECOVERY_INIT_001
"""

from .auto_recovery import (
    RecoveryStatus,
    RecoveryType,
    FailureType,
    RecoveryAction,
    RecoveryResult,
    RecoveryConfig,
    BaseRecoveryStrategy,
    ServiceRestartStrategy,
    ConnectionRecoveryStrategy,
    ResourceCleanupStrategy,
    ConfigurationReloadStrategy,
    AutoRecoveryManager,
    auto_recovery_manager,
    add_recovery_strategy,
    remove_recovery_strategy,
    trigger_recovery,
    get_recovery_summary,
    add_notification_callback,
    add_metrics_callback
)

from .recovery_strategies import (
    DatabaseRecoveryStrategy,
    CacheRecoveryStrategy
)

from .recovery_manager import (
    RecoveryManager,
    recovery_manager
)

__version__ = "1.0.0"
__author__ = "Paulo Júnior"

__all__ = [
    "RecoveryStatus",
    "RecoveryType",
    "FailureType",
    "RecoveryAction",
    "RecoveryResult",
    "RecoveryConfig",
    "BaseRecoveryStrategy",
    "ServiceRestartStrategy",
    "ConnectionRecoveryStrategy",
    "ResourceCleanupStrategy",
    "ConfigurationReloadStrategy",
    "AutoRecoveryManager",
    "auto_recovery_manager",
    "add_recovery_strategy",
    "remove_recovery_strategy",
    "trigger_recovery",
    "get_recovery_summary",
    "add_notification_callback",
    "add_metrics_callback",
    "DatabaseRecoveryStrategy",
    "CacheRecoveryStrategy",
    "RecoveryManager",
    "recovery_manager"
] 