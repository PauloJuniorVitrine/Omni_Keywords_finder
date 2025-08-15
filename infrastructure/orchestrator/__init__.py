from typing import Dict, List, Optional, Any
"""
Orchestrator Module - Omni Keywords Finder

Este módulo contém o orquestrador principal que coordena todo o fluxo
de coleta → validação → processamento → preenchimento → exportação.

Tracing ID: ORCHESTRATOR_001_20241227
Versão: 1.0
Autor: IA-Cursor
"""

from .fluxo_completo_orchestrator import FluxoCompletoOrchestrator
from .progress_tracker import ProgressTracker
from .error_handler import ErrorHandler
from .config import OrchestratorConfig

# Fase 3: Módulos de Integração e Qualidade
from .integration import SystemIntegration, IntegrationConfig
from .notifications import NotificationManager, NotificationConfig, NotificationType
from .metrics import MetricsCollector, MetricConfig, MetricType
from .validation import DataValidator, ValidationConfig, ValidationResult

# Fase 4: Otimizações e Melhorias
from .optimizations import OptimizationManager, OptimizationConfig
from .advanced_features import AdvancedFeaturesManager, Scheduler, TemplateManager

__all__ = [
    # Fase 1: Fundação Crítica
    'FluxoCompletoOrchestrator',
    'ProgressTracker', 
    'ErrorHandler',
    'OrchestratorConfig',
    
    # Fase 3: Integração e Qualidade
    'SystemIntegration',
    'IntegrationConfig',
    'NotificationManager',
    'NotificationConfig',
    'NotificationType',
    'MetricsCollector',
    'MetricConfig',
    'MetricType',
    'DataValidator',
    'ValidationConfig',
    'ValidationResult',
    
    # Fase 4: Otimizações e Melhorias
    'OptimizationManager',
    'OptimizationConfig',
    'IntelligentCache',
    'ParallelProcessor',
    'AdvancedFeaturesManager',
    'Scheduler',
    'TemplateManager'
]

__version__ = "1.0.0" 