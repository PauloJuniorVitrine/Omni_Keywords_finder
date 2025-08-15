"""
Resilience Module
Omni Keywords Finder - Infrastructure Resilience

Tracing ID: RESILIENCE_INIT_001_20250127
Versão: 1.0
Autor: IA-Cursor
Status: ✅ IMPLEMENTADO
"""

from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    circuit_breaker
)

from .advanced_circuit_breaker import (
    AdvancedCircuitBreaker,
    AdvancedCircuitBreakerConfig,
    AdvancedCircuitState,
    advanced_circuit_breaker
)

from .circuit_breaker_factory import (
    CircuitBreakerFactory,
    CircuitBreakerType,
    get_circuit_breaker_factory,
    create_circuit_breaker,
    get_circuit_breaker,
    get_or_create_circuit_breaker
)

__all__ = [
    # Circuit Breaker Básico
    'CircuitBreaker',
    'CircuitBreakerConfig',
    'CircuitState',
    'circuit_breaker',
    
    # Circuit Breaker Avançado
    'AdvancedCircuitBreaker',
    'AdvancedCircuitBreakerConfig',
    'AdvancedCircuitState',
    'advanced_circuit_breaker',
    
    # Factory
    'CircuitBreakerFactory',
    'CircuitBreakerType',
    'get_circuit_breaker_factory',
    'create_circuit_breaker',
    'get_circuit_breaker',
    'get_or_create_circuit_breaker'
]

__version__ = "1.0.0"
__author__ = "IA-Cursor"
__description__ = "Módulo de resiliência para Omni Keywords Finder" 