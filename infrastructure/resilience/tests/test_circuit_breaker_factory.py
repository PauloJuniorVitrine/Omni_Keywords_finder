"""
Testes para Circuit Breaker Factory
Omni Keywords Finder - Infrastructure Resilience

Tracing ID: TEST_CIRCUIT_BREAKER_FACTORY_001_20250127
Versão: 1.0
Autor: IA-Cursor
Status: ✅ IMPLEMENTADO
"""

import unittest
from unittest.mock import Mock, patch
from ..circuit_breaker_factory import (
    CircuitBreakerFactory,
    CircuitBreakerType,
    get_circuit_breaker_factory,
    create_circuit_breaker,
    get_circuit_breaker,
    get_or_create_circuit_breaker
)
from ..circuit_breaker import CircuitBreakerConfig
from ..advanced_circuit_breaker import AdvancedCircuitBreakerConfig


class TestCircuitBreakerFactory(unittest.TestCase):
    """Testes para Circuit Breaker Factory"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.factory = CircuitBreakerFactory()
    
    def test_initial_state(self):
        """Testa estado inicial do factory"""
        self.assertEqual(len(self.factory._circuit_breakers), 0)
        self.assertEqual(len(self.factory._advanced_circuit_breakers), 0)
        self.assertGreater(len(self.factory._default_configs), 0)
        self.assertGreater(len(self.factory._default_advanced_configs), 0)
    
    def test_create_basic_circuit_breaker(self):
        """Testa criação de circuit breaker básico"""
        name = "test_basic"
        cb = self.factory.create_circuit_breaker(name, CircuitBreakerType.BASIC)
        
        self.assertIsInstance(cb, type(self.factory._circuit_breakers[name]))
        self.assertEqual(len(self.factory._circuit_breakers), 1)
        self.assertIn(name, self.factory._circuit_breakers)
    
    def test_create_advanced_circuit_breaker(self):
        """Testa criação de circuit breaker avançado"""
        name = "test_advanced"
        cb = self.factory.create_circuit_breaker(name, CircuitBreakerType.ADVANCED)
        
        self.assertIsInstance(cb, type(self.factory._advanced_circuit_breakers[name]))
        self.assertEqual(len(self.factory._advanced_circuit_breakers), 1)
        self.assertIn(name, self.factory._advanced_circuit_breakers)
    
    def test_create_circuit_breaker_with_service_type(self):
        """Testa criação com tipo de serviço"""
        name = "test_service"
        cb = self.factory.create_circuit_breaker(
            name, 
            CircuitBreakerType.BASIC, 
            service_type="external_api"
        )
        
        self.assertIsInstance(cb, type(self.factory._circuit_breakers[name]))
        # Verificar se configuração padrão foi aplicada
        self.assertEqual(cb.config.failure_threshold, 5)
        self.assertEqual(cb.config.recovery_timeout, 60)
    
    def test_create_circuit_breaker_with_custom_config(self):
        """Testa criação com configuração personalizada"""
        name = "test_custom"
        custom_config = CircuitBreakerConfig(
            failure_threshold=10,
            recovery_timeout=30,
            name=name
        )
        
        cb = self.factory.create_circuit_breaker(
            name, 
            CircuitBreakerType.BASIC, 
            config=custom_config
        )
        
        self.assertEqual(cb.config.failure_threshold, 10)
        self.assertEqual(cb.config.recovery_timeout, 30)
    
    def test_create_duplicate_circuit_breaker(self):
        """Testa criação de circuit breaker duplicado"""
        name = "test_duplicate"
        
        # Criar primeiro
        cb1 = self.factory.create_circuit_breaker(name, CircuitBreakerType.BASIC)
        
        # Tentar criar novamente
        cb2 = self.factory.create_circuit_breaker(name, CircuitBreakerType.BASIC)
        
        # Deve retornar a mesma instância
        self.assertIs(cb1, cb2)
        self.assertEqual(len(self.factory._circuit_breakers), 1)
    
    def test_get_circuit_breaker_existing(self):
        """Testa obtenção de circuit breaker existente"""
        name = "test_get"
        created_cb = self.factory.create_circuit_breaker(name, CircuitBreakerType.BASIC)
        
        retrieved_cb = self.factory.get_circuit_breaker(name, CircuitBreakerType.BASIC)
        
        self.assertIs(created_cb, retrieved_cb)
    
    def test_get_circuit_breaker_nonexistent(self):
        """Testa obtenção de circuit breaker inexistente"""
        retrieved_cb = self.factory.get_circuit_breaker("nonexistent", CircuitBreakerType.BASIC)
        
        self.assertIsNone(retrieved_cb)
    
    def test_get_or_create_circuit_breaker_existing(self):
        """Testa get_or_create com circuit breaker existente"""
        name = "test_get_or_create"
        created_cb = self.factory.create_circuit_breaker(name, CircuitBreakerType.BASIC)
        
        retrieved_cb = self.factory.get_or_create_circuit_breaker(name, CircuitBreakerType.BASIC)
        
        self.assertIs(created_cb, retrieved_cb)
    
    def test_get_or_create_circuit_breaker_nonexistent(self):
        """Testa get_or_create com circuit breaker inexistente"""
        name = "test_get_or_create_new"
        
        cb = self.factory.get_or_create_circuit_breaker(name, CircuitBreakerType.BASIC)
        
        self.assertIsInstance(cb, type(self.factory._circuit_breakers[name]))
        self.assertIn(name, self.factory._circuit_breakers)
    
    def test_remove_circuit_breaker_existing(self):
        """Testa remoção de circuit breaker existente"""
        name = "test_remove"
        self.factory.create_circuit_breaker(name, CircuitBreakerType.BASIC)
        
        result = self.factory.remove_circuit_breaker(name, CircuitBreakerType.BASIC)
        
        self.assertTrue(result)
        self.assertNotIn(name, self.factory._circuit_breakers)
        self.assertEqual(len(self.factory._circuit_breakers), 0)
    
    def test_remove_circuit_breaker_nonexistent(self):
        """Testa remoção de circuit breaker inexistente"""
        result = self.factory.remove_circuit_breaker("nonexistent", CircuitBreakerType.BASIC)
        
        self.assertFalse(result)
    
    def test_get_all_circuit_breakers(self):
        """Testa obtenção de todos os circuit breakers"""
        # Criar alguns circuit breakers
        self.factory.create_circuit_breaker("cb1", CircuitBreakerType.BASIC)
        self.factory.create_circuit_breaker("cb2", CircuitBreakerType.BASIC)
        self.factory.create_circuit_breaker("cb3", CircuitBreakerType.ADVANCED)
        
        basic_cbs = self.factory.get_all_circuit_breakers(CircuitBreakerType.BASIC)
        advanced_cbs = self.factory.get_all_circuit_breakers(CircuitBreakerType.ADVANCED)
        
        self.assertEqual(len(basic_cbs), 2)
        self.assertEqual(len(advanced_cbs), 1)
        self.assertIn("cb1", basic_cbs)
        self.assertIn("cb2", basic_cbs)
        self.assertIn("cb3", advanced_cbs)
    
    def test_get_all_circuit_breakers_stats(self):
        """Testa obtenção de estatísticas de todos os circuit breakers"""
        # Criar alguns circuit breakers
        self.factory.create_circuit_breaker("cb1", CircuitBreakerType.BASIC)
        self.factory.create_circuit_breaker("cb2", CircuitBreakerType.ADVANCED)
        
        stats = self.factory.get_all_circuit_breakers_stats()
        
        self.assertIn("basic_cb1", stats)
        self.assertIn("advanced_cb2", stats)
        self.assertEqual(len(stats), 2)
    
    def test_reset_all_circuit_breakers(self):
        """Testa reset de todos os circuit breakers"""
        # Criar circuit breakers e simular falhas
        cb1 = self.factory.create_circuit_breaker("cb1", CircuitBreakerType.BASIC)
        cb2 = self.factory.create_circuit_breaker("cb2", CircuitBreakerType.ADVANCED)
        
        # Simular falhas para abrir circuits
        def failing_function():
            raise Exception("Test error")
        
        for _ in range(cb1.config.failure_threshold):
            cb1.call(failing_function)
        
        for _ in range(cb2.config.failure_threshold):
            cb2.call(failing_function)
        
        # Verificar que circuits estão abertos
        self.assertEqual(cb1.get_state().value, "OPEN")
        self.assertEqual(cb2.get_state().value, "OPEN")
        
        # Resetar todos
        self.factory.reset_all_circuit_breakers()
        
        # Verificar que circuits foram resetados
        self.assertEqual(cb1.get_state().value, "CLOSED")
        self.assertEqual(cb2.get_state().value, "CLOSED")
    
    def test_get_open_circuit_breakers(self):
        """Testa obtenção de circuit breakers abertos"""
        # Criar circuit breakers
        cb1 = self.factory.create_circuit_breaker("cb1", CircuitBreakerType.BASIC)
        cb2 = self.factory.create_circuit_breaker("cb2", CircuitBreakerType.ADVANCED)
        
        # Simular falhas para abrir um circuit
        def failing_function():
            raise Exception("Test error")
        
        for _ in range(cb1.config.failure_threshold):
            cb1.call(failing_function)
        
        open_cbs = self.factory.get_open_circuit_breakers()
        
        self.assertIn("cb1", open_cbs)
        self.assertEqual(open_cbs["cb1"], "basic")
        self.assertNotIn("cb2", open_cbs)
    
    def test_get_circuit_breaker_count(self):
        """Testa contagem de circuit breakers"""
        # Criar alguns circuit breakers
        self.factory.create_circuit_breaker("cb1", CircuitBreakerType.BASIC)
        self.factory.create_circuit_breaker("cb2", CircuitBreakerType.BASIC)
        self.factory.create_circuit_breaker("cb3", CircuitBreakerType.ADVANCED)
        
        count = self.factory.get_circuit_breaker_count()
        
        self.assertEqual(count["basic"], 2)
        self.assertEqual(count["advanced"], 1)
        self.assertEqual(count["total"], 3)
    
    def test_add_default_config(self):
        """Testa adição de configuração padrão"""
        custom_config = CircuitBreakerConfig(
            failure_threshold=15,
            recovery_timeout=45,
            name="custom_service"
        )
        
        self.factory.add_default_config("custom_service", custom_config)
        
        self.assertIn("custom_service", self.factory._default_configs)
        self.assertEqual(
            self.factory._default_configs["custom_service"].failure_threshold, 
            15
        )
    
    def test_add_default_advanced_config(self):
        """Testa adição de configuração padrão avançada"""
        custom_config = AdvancedCircuitBreakerConfig(
            failure_threshold=20,
            recovery_timeout=60,
            name="custom_advanced_service"
        )
        
        self.factory.add_default_advanced_config("custom_advanced_service", custom_config)
        
        self.assertIn("custom_advanced_service", self.factory._default_advanced_configs)
        self.assertEqual(
            self.factory._default_advanced_configs["custom_advanced_service"].failure_threshold, 
            20
        )
    
    def test_invalid_circuit_type(self):
        """Testa tipo de circuit breaker inválido"""
        with self.assertRaises(ValueError):
            self.factory.create_circuit_breaker("test", "invalid_type")
        
        with self.assertRaises(ValueError):
            self.factory.get_circuit_breaker("test", "invalid_type")
        
        with self.assertRaises(ValueError):
            self.factory.get_all_circuit_breakers("invalid_type")


class TestCircuitBreakerFactoryGlobalFunctions(unittest.TestCase):
    """Testes para funções globais do factory"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        # Reset factory global
        from ..circuit_breaker_factory import circuit_breaker_factory
        circuit_breaker_factory._circuit_breakers.clear()
        circuit_breaker_factory._advanced_circuit_breakers.clear()
    
    def test_get_circuit_breaker_factory(self):
        """Testa obtenção do factory global"""
        factory = get_circuit_breaker_factory()
        
        self.assertIsInstance(factory, CircuitBreakerFactory)
    
    def test_create_circuit_breaker_global(self):
        """Testa criação global de circuit breaker"""
        name = "test_global"
        cb = create_circuit_breaker(name, CircuitBreakerType.BASIC)
        
        self.assertIsInstance(cb, type(get_circuit_breaker_factory()._circuit_breakers[name]))
    
    def test_get_circuit_breaker_global(self):
        """Testa obtenção global de circuit breaker"""
        name = "test_global_get"
        created_cb = create_circuit_breaker(name, CircuitBreakerType.BASIC)
        
        retrieved_cb = get_circuit_breaker(name, CircuitBreakerType.BASIC)
        
        self.assertIs(created_cb, retrieved_cb)
    
    def test_get_or_create_circuit_breaker_global(self):
        """Testa get_or_create global"""
        name = "test_global_get_or_create"
        
        cb = get_or_create_circuit_breaker(name, CircuitBreakerType.BASIC)
        
        self.assertIsInstance(cb, type(get_circuit_breaker_factory()._circuit_breakers[name]))
    
    def test_create_circuit_breaker_with_service_type_global(self):
        """Testa criação global com tipo de serviço"""
        name = "test_global_service"
        cb = create_circuit_breaker(
            name, 
            CircuitBreakerType.BASIC, 
            service_type="database"
        )
        
        # Verificar se configuração padrão foi aplicada
        self.assertEqual(cb.config.failure_threshold, 3)
        self.assertEqual(cb.config.recovery_timeout, 30)


class TestCircuitBreakerFactoryDefaultConfigs(unittest.TestCase):
    """Testes para configurações padrão do factory"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.factory = CircuitBreakerFactory()
    
    def test_external_api_default_config(self):
        """Testa configuração padrão para API externa"""
        cb = self.factory.create_circuit_breaker(
            "external_api_test", 
            CircuitBreakerType.BASIC, 
            service_type="external_api"
        )
        
        self.assertEqual(cb.config.failure_threshold, 5)
        self.assertEqual(cb.config.recovery_timeout, 60)
    
    def test_database_default_config(self):
        """Testa configuração padrão para banco de dados"""
        cb = self.factory.create_circuit_breaker(
            "database_test", 
            CircuitBreakerType.BASIC, 
            service_type="database"
        )
        
        self.assertEqual(cb.config.failure_threshold, 3)
        self.assertEqual(cb.config.recovery_timeout, 30)
    
    def test_cache_default_config(self):
        """Testa configuração padrão para cache"""
        cb = self.factory.create_circuit_breaker(
            "cache_test", 
            CircuitBreakerType.BASIC, 
            service_type="cache"
        )
        
        self.assertEqual(cb.config.failure_threshold, 10)
        self.assertEqual(cb.config.recovery_timeout, 15)
    
    def test_internal_service_default_config(self):
        """Testa configuração padrão para serviço interno"""
        cb = self.factory.create_circuit_breaker(
            "internal_service_test", 
            CircuitBreakerType.BASIC, 
            service_type="internal_service"
        )
        
        self.assertEqual(cb.config.failure_threshold, 7)
        self.assertEqual(cb.config.recovery_timeout, 45)
    
    def test_advanced_external_api_default_config(self):
        """Testa configuração padrão avançada para API externa"""
        cb = self.factory.create_circuit_breaker(
            "external_api_advanced_test", 
            CircuitBreakerType.ADVANCED, 
            service_type="external_api"
        )
        
        self.assertEqual(cb.config.failure_threshold, 5)
        self.assertEqual(cb.config.recovery_timeout, 60)
        self.assertEqual(cb.config.timeout, 30.0)
        self.assertEqual(cb.config.max_concurrent_calls, 10)
        self.assertEqual(cb.config.error_percentage_threshold, 50.0)
    
    def test_unknown_service_type(self):
        """Testa tipo de serviço desconhecido"""
        cb = self.factory.create_circuit_breaker(
            "unknown_test", 
            CircuitBreakerType.BASIC, 
            service_type="unknown_service"
        )
        
        # Deve usar configuração padrão genérica
        self.assertEqual(cb.config.failure_threshold, 5)  # Valor padrão
        self.assertEqual(cb.config.recovery_timeout, 60)  # Valor padrão


if __name__ == '__main__':
    unittest.main() 