"""
Circuit Breaker Factory
Omni Keywords Finder - Infrastructure Resilience

Tracing ID: CIRCUIT_BREAKER_FACTORY_001_20250127
Versão: 1.0
Autor: IA-Cursor
Status: ✅ IMPLEMENTADO
"""

import logging
from typing import Dict, Optional, Type
from dataclasses import dataclass
from .circuit_breaker import CircuitBreaker, CircuitBreakerConfig
from .advanced_circuit_breaker import AdvancedCircuitBreaker, AdvancedCircuitBreakerConfig

logger = logging.getLogger(__name__)

@dataclass
class CircuitBreakerType:
    """Tipos de circuit breaker disponíveis"""
    BASIC = "basic"
    ADVANCED = "advanced"


class CircuitBreakerFactory:
    """
    Factory para criação e gerenciamento de circuit breakers
    
    Permite criar circuit breakers com configurações específicas
    e gerenciar instâncias de forma centralizada.
    """
    
    def __init__(self):
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._advanced_circuit_breakers: Dict[str, AdvancedCircuitBreaker] = {}
        self._default_configs: Dict[str, CircuitBreakerConfig] = {}
        self._default_advanced_configs: Dict[str, AdvancedCircuitBreakerConfig] = {}
        
        # Configurar configurações padrão
        self._setup_default_configs()
    
    def _setup_default_configs(self):
        """Configura configurações padrão para diferentes tipos de serviço"""
        
        # Configurações para APIs externas
        self._default_configs['external_api'] = CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=Exception,
            name="external_api"
        )
        
        self._default_advanced_configs['external_api'] = AdvancedCircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=60,
            success_threshold=3,
            expected_exception=Exception,
            name="external_api",
            timeout=30.0,
            max_concurrent_calls=10,
            error_percentage_threshold=50.0,
            window_size=100,
            enable_metrics=True,
            enable_async=False
        )
        
        # Configurações para banco de dados
        self._default_configs['database'] = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=30,
            expected_exception=Exception,
            name="database"
        )
        
        self._default_advanced_configs['database'] = AdvancedCircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=30,
            success_threshold=2,
            expected_exception=Exception,
            name="database",
            timeout=10.0,
            max_concurrent_calls=20,
            error_percentage_threshold=30.0,
            window_size=50,
            enable_metrics=True,
            enable_async=False
        )
        
        # Configurações para cache
        self._default_configs['cache'] = CircuitBreakerConfig(
            failure_threshold=10,
            recovery_timeout=15,
            expected_exception=Exception,
            name="cache"
        )
        
        self._default_advanced_configs['cache'] = AdvancedCircuitBreakerConfig(
            failure_threshold=10,
            recovery_timeout=15,
            success_threshold=5,
            expected_exception=Exception,
            name="cache",
            timeout=5.0,
            max_concurrent_calls=50,
            error_percentage_threshold=70.0,
            window_size=200,
            enable_metrics=True,
            enable_async=False
        )
        
        # Configurações para serviços internos
        self._default_configs['internal_service'] = CircuitBreakerConfig(
            failure_threshold=7,
            recovery_timeout=45,
            expected_exception=Exception,
            name="internal_service"
        )
        
        self._default_advanced_configs['internal_service'] = AdvancedCircuitBreakerConfig(
            failure_threshold=7,
            recovery_timeout=45,
            success_threshold=4,
            expected_exception=Exception,
            name="internal_service",
            timeout=20.0,
            max_concurrent_calls=15,
            error_percentage_threshold=40.0,
            window_size=150,
            enable_metrics=True,
            enable_async=True
        )
    
    def create_circuit_breaker(
        self, 
        name: str, 
        circuit_type: str = CircuitBreakerType.BASIC,
        config: Optional[CircuitBreakerConfig] = None,
        service_type: Optional[str] = None
    ) -> CircuitBreaker:
        """
        Cria um novo circuit breaker
        
        Args:
            name: Nome único do circuit breaker
            circuit_type: Tipo do circuit breaker (basic ou advanced)
            config: Configuração personalizada
            service_type: Tipo de serviço para usar configuração padrão
            
        Returns:
            Instância do circuit breaker criado
        """
        if circuit_type == CircuitBreakerType.BASIC:
            return self._create_basic_circuit_breaker(name, config, service_type)
        elif circuit_type == CircuitBreakerType.ADVANCED:
            return self._create_advanced_circuit_breaker(name, config, service_type)
        else:
            raise ValueError(f"Tipo de circuit breaker inválido: {circuit_type}")
    
    def _create_basic_circuit_breaker(
        self, 
        name: str, 
        config: Optional[CircuitBreakerConfig] = None,
        service_type: Optional[str] = None
    ) -> CircuitBreaker:
        """Cria circuit breaker básico"""
        if name in self._circuit_breakers:
            logger.warning(f"Circuit breaker básico '{name}' já existe, retornando instância existente")
            return self._circuit_breakers[name]
        
        # Usar configuração padrão se não fornecida
        if config is None and service_type:
            if service_type in self._default_configs:
                config = self._default_configs[service_type]
                config.name = name  # Sobrescrever nome
            else:
                logger.warning(f"Tipo de serviço '{service_type}' não encontrado, usando configuração padrão")
                config = CircuitBreakerConfig(name=name)
        elif config is None:
            config = CircuitBreakerConfig(name=name)
        
        circuit_breaker = CircuitBreaker(config)
        self._circuit_breakers[name] = circuit_breaker
        
        logger.info(f"Circuit breaker básico '{name}' criado com configuração: {config}")
        return circuit_breaker
    
    def _create_advanced_circuit_breaker(
        self, 
        name: str, 
        config: Optional[AdvancedCircuitBreakerConfig] = None,
        service_type: Optional[str] = None
    ) -> AdvancedCircuitBreaker:
        """Cria circuit breaker avançado"""
        if name in self._advanced_circuit_breakers:
            logger.warning(f"Circuit breaker avançado '{name}' já existe, retornando instância existente")
            return self._advanced_circuit_breakers[name]
        
        # Usar configuração padrão se não fornecida
        if config is None and service_type:
            if service_type in self._default_advanced_configs:
                config = self._default_advanced_configs[service_type]
                config.name = name  # Sobrescrever nome
            else:
                logger.warning(f"Tipo de serviço '{service_type}' não encontrado, usando configuração padrão")
                config = AdvancedCircuitBreakerConfig(name=name)
        elif config is None:
            config = AdvancedCircuitBreakerConfig(name=name)
        
        circuit_breaker = AdvancedCircuitBreaker(config)
        self._advanced_circuit_breakers[name] = circuit_breaker
        
        logger.info(f"Circuit breaker avançado '{name}' criado com configuração: {config}")
        return circuit_breaker
    
    def get_circuit_breaker(self, name: str, circuit_type: str = CircuitBreakerType.BASIC) -> Optional[CircuitBreaker]:
        """
        Obtém circuit breaker existente
        
        Args:
            name: Nome do circuit breaker
            circuit_type: Tipo do circuit breaker
            
        Returns:
            Instância do circuit breaker ou None se não existir
        """
        if circuit_type == CircuitBreakerType.BASIC:
            return self._circuit_breakers.get(name)
        elif circuit_type == CircuitBreakerType.ADVANCED:
            return self._advanced_circuit_breakers.get(name)
        else:
            raise ValueError(f"Tipo de circuit breaker inválido: {circuit_type}")
    
    def get_or_create_circuit_breaker(
        self, 
        name: str, 
        circuit_type: str = CircuitBreakerType.BASIC,
        config: Optional[CircuitBreakerConfig] = None,
        service_type: Optional[str] = None
    ) -> CircuitBreaker:
        """
        Obtém circuit breaker existente ou cria novo
        
        Args:
            name: Nome do circuit breaker
            circuit_type: Tipo do circuit breaker
            config: Configuração personalizada
            service_type: Tipo de serviço
            
        Returns:
            Instância do circuit breaker
        """
        existing = self.get_circuit_breaker(name, circuit_type)
        if existing:
            return existing
        
        return self.create_circuit_breaker(name, circuit_type, config, service_type)
    
    def remove_circuit_breaker(self, name: str, circuit_type: str = CircuitBreakerType.BASIC) -> bool:
        """
        Remove circuit breaker
        
        Args:
            name: Nome do circuit breaker
            circuit_type: Tipo do circuit breaker
            
        Returns:
            True se removido, False se não existia
        """
        if circuit_type == CircuitBreakerType.BASIC:
            if name in self._circuit_breakers:
                del self._circuit_breakers[name]
                logger.info(f"Circuit breaker básico '{name}' removido")
                return True
        elif circuit_type == CircuitBreakerType.ADVANCED:
            if name in self._advanced_circuit_breakers:
                del self._advanced_circuit_breakers[name]
                logger.info(f"Circuit breaker avançado '{name}' removido")
                return True
        
        return False
    
    def get_all_circuit_breakers(self, circuit_type: str = CircuitBreakerType.BASIC) -> Dict[str, CircuitBreaker]:
        """
        Obtém todos os circuit breakers de um tipo
        
        Args:
            circuit_type: Tipo do circuit breaker
            
        Returns:
            Dicionário com todos os circuit breakers
        """
        if circuit_type == CircuitBreakerType.BASIC:
            return self._circuit_breakers.copy()
        elif circuit_type == CircuitBreakerType.ADVANCED:
            return self._advanced_circuit_breakers.copy()
        else:
            raise ValueError(f"Tipo de circuit breaker inválido: {circuit_type}")
    
    def get_all_circuit_breakers_stats(self) -> Dict[str, Dict]:
        """
        Obtém estatísticas de todos os circuit breakers
        
        Returns:
            Dicionário com estatísticas de todos os circuit breakers
        """
        stats = {}
        
        # Estatísticas dos circuit breakers básicos
        for name, cb in self._circuit_breakers.items():
            stats[f"basic_{name}"] = cb.get_stats()
        
        # Estatísticas dos circuit breakers avançados
        for name, cb in self._advanced_circuit_breakers.items():
            stats[f"advanced_{name}"] = cb.get_stats()
        
        return stats
    
    def reset_all_circuit_breakers(self):
        """Reseta todos os circuit breakers"""
        for cb in self._circuit_breakers.values():
            cb.reset()
        
        for cb in self._advanced_circuit_breakers.values():
            cb.reset()
        
        logger.info("Todos os circuit breakers foram resetados")
    
    def get_open_circuit_breakers(self) -> Dict[str, str]:
        """
        Obtém lista de circuit breakers abertos
        
        Returns:
            Dicionário com nome e tipo dos circuit breakers abertos
        """
        open_circuit_breakers = {}
        
        for name, cb in self._circuit_breakers.items():
            if cb.get_state().value == "OPEN":
                open_circuit_breakers[name] = "basic"
        
        for name, cb in self._advanced_circuit_breakers.items():
            if cb.get_state().value == "OPEN":
                open_circuit_breakers[name] = "advanced"
        
        return open_circuit_breakers
    
    def get_circuit_breaker_count(self) -> Dict[str, int]:
        """
        Obtém contagem de circuit breakers por tipo
        
        Returns:
            Dicionário com contagem por tipo
        """
        return {
            "basic": len(self._circuit_breakers),
            "advanced": len(self._advanced_circuit_breakers),
            "total": len(self._circuit_breakers) + len(self._advanced_circuit_breakers)
        }
    
    def add_default_config(self, service_type: str, config: CircuitBreakerConfig):
        """Adiciona configuração padrão para um tipo de serviço"""
        self._default_configs[service_type] = config
        logger.info(f"Configuração padrão adicionada para tipo de serviço: {service_type}")
    
    def add_default_advanced_config(self, service_type: str, config: AdvancedCircuitBreakerConfig):
        """Adiciona configuração padrão avançada para um tipo de serviço"""
        self._default_advanced_configs[service_type] = config
        logger.info(f"Configuração padrão avançada adicionada para tipo de serviço: {service_type}")


# Instância global do factory
circuit_breaker_factory = CircuitBreakerFactory()


def get_circuit_breaker_factory() -> CircuitBreakerFactory:
    """Obtém instância global do factory"""
    return circuit_breaker_factory


def create_circuit_breaker(
    name: str, 
    circuit_type: str = CircuitBreakerType.BASIC,
    config: Optional[CircuitBreakerConfig] = None,
    service_type: Optional[str] = None
) -> CircuitBreaker:
    """
    Função utilitária para criar circuit breaker
    
    Args:
        name: Nome do circuit breaker
        circuit_type: Tipo do circuit breaker
        config: Configuração personalizada
        service_type: Tipo de serviço
        
    Returns:
        Instância do circuit breaker
    """
    return circuit_breaker_factory.create_circuit_breaker(name, circuit_type, config, service_type)


def get_circuit_breaker(name: str, circuit_type: str = CircuitBreakerType.BASIC) -> Optional[CircuitBreaker]:
    """
    Função utilitária para obter circuit breaker
    
    Args:
        name: Nome do circuit breaker
        circuit_type: Tipo do circuit breaker
        
    Returns:
        Instância do circuit breaker ou None
    """
    return circuit_breaker_factory.get_circuit_breaker(name, circuit_type)


def get_or_create_circuit_breaker(
    name: str, 
    circuit_type: str = CircuitBreakerType.BASIC,
    config: Optional[CircuitBreakerConfig] = None,
    service_type: Optional[str] = None
) -> CircuitBreaker:
    """
    Função utilitária para obter ou criar circuit breaker
    
    Args:
        name: Nome do circuit breaker
        circuit_type: Tipo do circuit breaker
        config: Configuração personalizada
        service_type: Tipo de serviço
        
    Returns:
        Instância do circuit breaker
    """
    return circuit_breaker_factory.get_or_create_circuit_breaker(name, circuit_type, config, service_type) 