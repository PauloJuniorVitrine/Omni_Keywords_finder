"""
Testes para Advanced Circuit Breaker Pattern
Omni Keywords Finder - Infrastructure Resilience

Tracing ID: TEST_ADVANCED_CIRCUIT_BREAKER_001_20250127
Versão: 1.0
Autor: IA-Cursor
Status: ✅ IMPLEMENTADO
"""

import unittest
import time
import asyncio
import threading
from unittest.mock import Mock, patch, MagicMock
from ..advanced_circuit_breaker import (
    AdvancedCircuitBreaker, 
    AdvancedCircuitBreakerConfig, 
    AdvancedCircuitState, 
    advanced_circuit_breaker
)


class TestAdvancedCircuitBreaker(unittest.TestCase):
    """Testes para Advanced Circuit Breaker"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.config = AdvancedCircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=1,
            success_threshold=2,
            name="test_advanced_circuit_breaker",
            timeout=5.0,
            max_concurrent_calls=5,
            error_percentage_threshold=50.0,
            window_size=10,
            enable_metrics=True,
            enable_async=False
        )
        self.circuit_breaker = AdvancedCircuitBreaker(self.config)
    
    def test_initial_state(self):
        """Testa estado inicial do circuit breaker avançado"""
        self.assertEqual(self.circuit_breaker.get_state(), AdvancedCircuitState.CLOSED)
        self.assertEqual(self.circuit_breaker.failure_count, 0)
        self.assertEqual(self.circuit_breaker.success_count, 0)
        self.assertEqual(len(self.circuit_breaker.call_results), 0)
    
    def test_successful_call(self):
        """Testa chamada bem-sucedida"""
        def successful_function():
            return "success"
        
        result = self.circuit_breaker.call(successful_function)
        self.assertEqual(result, "success")
        self.assertEqual(self.circuit_breaker.get_state(), AdvancedCircuitState.CLOSED)
        self.assertEqual(self.circuit_breaker.success_count, 1)
        self.assertEqual(self.circuit_breaker.failure_count, 0)
        self.assertEqual(len(self.circuit_breaker.call_results), 1)
        self.assertTrue(self.circuit_breaker.call_results[0].success)
    
    def test_failed_call(self):
        """Testa chamada que falha"""
        def failing_function():
            raise Exception("Test error")
        
        result = self.circuit_breaker.call(failing_function)
        self.assertIsNone(result)  # Fallback padrão
        self.assertEqual(self.circuit_breaker.get_state(), AdvancedCircuitState.CLOSED)
        self.assertEqual(self.circuit_breaker.failure_count, 1)
        self.assertEqual(self.circuit_breaker.success_count, 0)
        self.assertEqual(len(self.circuit_breaker.call_results), 1)
        self.assertFalse(self.circuit_breaker.call_results[0].success)
    
    def test_circuit_opens_after_threshold(self):
        """Testa abertura do circuit após threshold de falhas"""
        def failing_function():
            raise Exception("Test error")
        
        # Executar falhas até atingir threshold
        for _ in range(self.config.failure_threshold):
            self.circuit_breaker.call(failing_function)
        
        self.assertEqual(self.circuit_breaker.get_state(), AdvancedCircuitState.OPEN)
        self.assertEqual(self.circuit_breaker.failure_count, self.config.failure_threshold)
    
    def test_circuit_opens_after_error_percentage(self):
        """Testa abertura do circuit após threshold de porcentagem de erro"""
        config_high_percentage = AdvancedCircuitBreakerConfig(
            failure_threshold=10,  # Alto threshold
            error_percentage_threshold=30.0,  # Baixa porcentagem
            name="percentage_test",
            window_size=10
        )
        cb = AdvancedCircuitBreaker(config_high_percentage)
        
        def failing_function():
            raise Exception("Test error")
        
        def successful_function():
            return "success"
        
        # 3 falhas em 10 chamadas = 30% de erro
        for _ in range(3):
            cb.call(failing_function)
        
        for _ in range(7):
            cb.call(successful_function)
        
        # Circuit deve abrir por porcentagem de erro
        self.assertEqual(cb.get_state(), AdvancedCircuitState.OPEN)
    
    def test_circuit_half_open_after_timeout(self):
        """Testa transição para half-open após timeout"""
        def failing_function():
            raise Exception("Test error")
        
        # Abrir circuit
        for _ in range(self.config.failure_threshold):
            self.circuit_breaker.call(failing_function)
        
        self.assertEqual(self.circuit_breaker.get_state(), AdvancedCircuitState.OPEN)
        
        # Aguardar timeout
        time.sleep(self.config.recovery_timeout + 0.1)
        
        # Próxima chamada deve tentar half-open
        def successful_function():
            return "success"
        
        result = self.circuit_breaker.call(successful_function)
        self.assertEqual(result, "success")
        self.assertEqual(self.circuit_breaker.get_state(), AdvancedCircuitState.HALF_OPEN)
    
    def test_circuit_closes_after_success_threshold(self):
        """Testa fechamento do circuit após threshold de sucessos no half-open"""
        def failing_function():
            raise Exception("Test error")
        
        # Abrir circuit
        for _ in range(self.config.failure_threshold):
            self.circuit_breaker.call(failing_function)
        
        # Aguardar timeout
        time.sleep(self.config.recovery_timeout + 0.1)
        
        # Sucessos no half-open devem fechar circuit
        def successful_function():
            return "success"
        
        for _ in range(self.config.success_threshold):
            result = self.circuit_breaker.call(successful_function)
            self.assertEqual(result, "success")
        
        self.assertEqual(self.circuit_breaker.get_state(), AdvancedCircuitState.CLOSED)
        self.assertEqual(self.circuit_breaker.failure_count, 0)
        self.assertEqual(self.circuit_breaker.success_count, 0)
    
    def test_timeout_functionality(self):
        """Testa funcionalidade de timeout"""
        def slow_function():
            time.sleep(10)  # Função muito lenta
            return "success"
        
        # Configurar timeout baixo
        config_timeout = AdvancedCircuitBreakerConfig(
            failure_threshold=1,
            recovery_timeout=1,
            name="timeout_test",
            timeout=1.0
        )
        cb = AdvancedCircuitBreaker(config_timeout)
        
        result = cb.call(slow_function)
        self.assertIsNone(result)  # Deve falhar por timeout
        self.assertEqual(cb.get_state(), AdvancedCircuitState.OPEN)
    
    def test_concurrent_calls_limit(self):
        """Testa limite de chamadas concorrentes"""
        def slow_function():
            time.sleep(0.5)  # Função lenta
            return "success"
        
        results = []
        lock = threading.Lock()
        
        def worker():
            result = self.circuit_breaker.call(slow_function)
            with lock:
                results.append(result)
        
        # Criar mais threads que o limite
        threads = []
        for _ in range(10):  # Mais que max_concurrent_calls (5)
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # Aguardar todas as threads
        for thread in threads:
            thread.join()
        
        # Verificar que algumas chamadas foram rejeitadas
        self.assertEqual(len(results), 10)
        # Algumas devem ter retornado None (fallback) devido ao limite de concorrência
        self.assertTrue(any(result is None for result in results))
    
    def test_forced_states(self):
        """Testa estados forçados"""
        # Forçar abertura
        self.circuit_breaker.force_open()
        self.assertEqual(self.circuit_breaker.get_state(), AdvancedCircuitState.FORCED_OPEN)
        
        # Tentar chamada deve usar fallback
        def successful_function():
            return "success"
        
        result = self.circuit_breaker.call(successful_function)
        self.assertIsNone(result)
        
        # Forçar fechamento
        self.circuit_breaker.force_closed()
        self.assertEqual(self.circuit_breaker.get_state(), AdvancedCircuitState.FORCED_CLOSED)
        
        # Chamada deve funcionar
        result = self.circuit_breaker.call(successful_function)
        self.assertEqual(result, "success")
    
    def test_window_size_limit(self):
        """Testa limite do tamanho da janela"""
        def successful_function():
            return "success"
        
        # Executar mais chamadas que o tamanho da janela
        for _ in range(self.config.window_size + 5):
            self.circuit_breaker.call(successful_function)
        
        # Verificar que apenas as últimas chamadas estão na janela
        self.assertEqual(len(self.circuit_breaker.call_results), self.config.window_size)
    
    def test_get_stats(self):
        """Testa obtenção de estatísticas detalhadas"""
        def successful_function():
            return "success"
        
        def failing_function():
            raise Exception("Test error")
        
        # Executar algumas chamadas
        self.circuit_breaker.call(successful_function)
        self.circuit_breaker.call(failing_function)
        
        stats = self.circuit_breaker.get_stats()
        
        self.assertEqual(stats['name'], self.config.name)
        self.assertEqual(stats['state'], AdvancedCircuitState.CLOSED.value)
        self.assertEqual(stats['failure_count'], 1)
        self.assertEqual(stats['success_count'], 1)
        self.assertEqual(stats['failure_threshold'], self.config.failure_threshold)
        self.assertEqual(stats['recovery_timeout'], self.config.recovery_timeout)
        self.assertEqual(stats['window_size'], 2)
        self.assertEqual(stats['max_concurrent_calls'], self.config.max_concurrent_calls)
        self.assertIn('error_percentage', stats)
    
    def test_decorator_usage(self):
        """Testa uso do decorator"""
        @advanced_circuit_breaker(self.config)
        def test_function():
            return "decorated success"
        
        result = test_function()
        self.assertEqual(result, "decorated success")
        
        # Verificar se atributos foram adicionados
        self.assertTrue(hasattr(test_function, 'circuit_breaker'))
        self.assertTrue(hasattr(test_function, 'get_state'))
        self.assertTrue(hasattr(test_function, 'get_stats'))
        self.assertTrue(hasattr(test_function, 'reset'))
        self.assertTrue(hasattr(test_function, 'force_open'))
        self.assertTrue(hasattr(test_function, 'force_closed'))


class TestAdvancedCircuitBreakerAsync(unittest.TestCase):
    """Testes assíncronos para Advanced Circuit Breaker"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.config = AdvancedCircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=1,
            success_threshold=2,
            name="test_async_circuit_breaker",
            timeout=5.0,
            max_concurrent_calls=5,
            error_percentage_threshold=50.0,
            window_size=10,
            enable_metrics=True,
            enable_async=True
        )
        self.circuit_breaker = AdvancedCircuitBreaker(self.config)
    
    def test_async_call_success(self):
        """Testa chamada assíncrona bem-sucedida"""
        async def async_successful_function():
            await asyncio.sleep(0.1)
            return "async success"
        
        async def test():
            result = await self.circuit_breaker.call_async(async_successful_function)
            self.assertEqual(result, "async success")
            self.assertEqual(self.circuit_breaker.get_state(), AdvancedCircuitState.CLOSED)
            self.assertEqual(self.circuit_breaker.success_count, 1)
        
        asyncio.run(test())
    
    def test_async_call_failure(self):
        """Testa chamada assíncrona que falha"""
        async def async_failing_function():
            await asyncio.sleep(0.1)
            raise Exception("Async test error")
        
        async def test():
            result = await self.circuit_breaker.call_async(async_failing_function)
            self.assertIsNone(result)
            self.assertEqual(self.circuit_breaker.get_state(), AdvancedCircuitState.CLOSED)
            self.assertEqual(self.circuit_breaker.failure_count, 1)
        
        asyncio.run(test())
    
    def test_async_timeout(self):
        """Testa timeout em chamada assíncrona"""
        async def async_slow_function():
            await asyncio.sleep(10)  # Função muito lenta
            return "success"
        
        config_timeout = AdvancedCircuitBreakerConfig(
            failure_threshold=1,
            recovery_timeout=1,
            name="async_timeout_test",
            timeout=1.0,
            enable_async=True
        )
        cb = AdvancedCircuitBreaker(config_timeout)
        
        async def test():
            result = await cb.call_async(async_slow_function)
            self.assertIsNone(result)
            self.assertEqual(cb.get_state(), AdvancedCircuitState.OPEN)
        
        asyncio.run(test())
    
    def test_async_fallback(self):
        """Testa fallback assíncrono"""
        async def async_failing_function():
            raise Exception("Async error")
        
        async def async_fallback_function():
            return "async fallback"
        
        config_with_fallback = AdvancedCircuitBreakerConfig(
            failure_threshold=1,
            recovery_timeout=1,
            name="async_fallback_test",
            fallback_function=async_fallback_function,
            enable_async=True
        )
        cb = AdvancedCircuitBreaker(config_with_fallback)
        
        async def test():
            result = await cb.call_async(async_failing_function)
            self.assertEqual(result, "async fallback")
        
        asyncio.run(test())
    
    def test_async_decorator(self):
        """Testa decorator assíncrono"""
        @advanced_circuit_breaker(self.config)
        async def async_test_function():
            await asyncio.sleep(0.1)
            return "async decorated success"
        
        async def test():
            result = await async_test_function()
            self.assertEqual(result, "async decorated success")
            
            # Verificar se atributos foram adicionados
            self.assertTrue(hasattr(async_test_function, 'circuit_breaker'))
            self.assertTrue(hasattr(async_test_function, 'get_state'))
            self.assertTrue(hasattr(async_test_function, 'get_stats'))
            self.assertTrue(hasattr(async_test_function, 'reset'))
            self.assertTrue(hasattr(async_test_function, 'force_open'))
            self.assertTrue(hasattr(async_test_function, 'force_closed'))
        
        asyncio.run(test())


class TestAdvancedCircuitBreakerMetrics(unittest.TestCase):
    """Testes para métricas do Advanced Circuit Breaker"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.config = AdvancedCircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=1,
            name="metrics_test",
            enable_metrics=True
        )
        self.circuit_breaker = AdvancedCircuitBreaker(self.config)
    
    @patch('infrastructure.resilience.advanced_circuit_breaker.Counter')
    @patch('infrastructure.resilience.advanced_circuit_breaker.Histogram')
    @patch('infrastructure.resilience.advanced_circuit_breaker.Gauge')
    def test_metrics_initialization(self, mock_gauge, mock_histogram, mock_counter):
        """Testa inicialização das métricas"""
        # Criar novo circuit breaker para testar inicialização
        cb = AdvancedCircuitBreaker(self.config)
        
        # Verificar se métricas foram criadas
        mock_counter.assert_called()
        mock_histogram.assert_called()
        mock_gauge.assert_called()
    
    def test_metrics_disabled(self):
        """Testa circuit breaker com métricas desabilitadas"""
        config_no_metrics = AdvancedCircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=1,
            name="no_metrics_test",
            enable_metrics=False
        )
        
        # Não deve lançar erro
        cb = AdvancedCircuitBreaker(config_no_metrics)
        
        def successful_function():
            return "success"
        
        result = cb.call(successful_function)
        self.assertEqual(result, "success")
    
    def test_error_percentage_calculation(self):
        """Testa cálculo de porcentagem de erro"""
        def failing_function():
            raise Exception("Test error")
        
        def successful_function():
            return "success"
        
        # 3 falhas, 2 sucessos = 60% de erro
        for _ in range(3):
            self.circuit_breaker.call(failing_function)
        
        for _ in range(2):
            self.circuit_breaker.call(successful_function)
        
        error_percentage = self.circuit_breaker._get_error_percentage()
        self.assertEqual(error_percentage, 60.0)
    
    def test_empty_window_error_percentage(self):
        """Testa porcentagem de erro com janela vazia"""
        error_percentage = self.circuit_breaker._get_error_percentage()
        self.assertEqual(error_percentage, 0.0)


if __name__ == '__main__':
    unittest.main() 