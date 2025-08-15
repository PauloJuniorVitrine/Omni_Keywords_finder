"""
Módulo de Integração - Omni Keywords Finder

Responsável por conectar módulos funcionais ao orquestrador,
resolvendo problemas de integração identificados.

Tracing ID: INTEGRATION_BRIDGE_001_20250127
Versão: 1.0
Autor: IA-Cursor
Status: ✅ IMPLEMENTAÇÃO CRÍTICA
"""

from .integration_bridge import IntegrationBridge
from .module_connector import ModuleConnector
from .flow_coordinator import FlowCoordinator

__all__ = [
    'IntegrationBridge',
    'ModuleConnector', 
    'FlowCoordinator'
]

__version__ = "1.0.0"
