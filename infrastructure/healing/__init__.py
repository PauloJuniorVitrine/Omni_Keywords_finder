"""
Self-Healing System - Sistema de Auto-Cura

Tracing ID: HEALING_INIT_001_20250127
Versão: 1.0
Data: 2025-01-27
Objetivo: Sistema completo de auto-cura para serviços

Este módulo implementa um sistema completo de self-healing que monitora
serviços e aplica correções automáticas quando detecta problemas.
"""

from .self_healing_service import (
    SelfHealingService,
    ServiceStatus,
    ServiceInfo,
    ProblemReport,
    ProblemType
)

from .healing_strategies import (
    HealingStrategy,
    ServiceRestartStrategy,
    ConnectionRecoveryStrategy,
    ResourceCleanupStrategy,
    ConfigurationReloadStrategy,
    HealingStrategyFactory,
    HealingResult
)

from .healing_monitor import (
    HealingMonitor,
    ServiceMetrics
)

from .healing_config import (
    HealingConfig,
    load_healing_config,
    DEFAULT_CONFIG
)

__all__ = [
    # Serviço principal
    'SelfHealingService',
    'ServiceStatus',
    'ServiceInfo',
    'ProblemReport',
    'ProblemType',
    
    # Estratégias
    'HealingStrategy',
    'ServiceRestartStrategy',
    'ConnectionRecoveryStrategy',
    'ResourceCleanupStrategy',
    'ConfigurationReloadStrategy',
    'HealingStrategyFactory',
    'HealingResult',
    
    # Monitor
    'HealingMonitor',
    'ServiceMetrics',
    
    # Configuração
    'HealingConfig',
    'load_healing_config',
    'DEFAULT_CONFIG'
]

__version__ = "1.0.0"
__author__ = "Omni Keywords Finder Team"
__description__ = "Sistema de Auto-Cura para Serviços" 