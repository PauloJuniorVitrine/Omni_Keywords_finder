"""
Testes para Circuit Breaker Pattern
Omni Keywords Finder - Infrastructure Resilience

Tracing ID: TEST_CIRCUIT_BREAKER_001_20250127
Versão: 1.0
Autor: IA-Cursor
Status: ✅ IMPLEMENTADO
"""

import unittest
import time
import threading
from unittest.mock import Mock, patch
from ..circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitState, circuit_breaker


class TestCircuitBreaker(unittest.TestCase):
    """Testes para Circuit Breaker básico"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=1,
            name="test_circuit_breaker"
        )
        self.circuit_breaker = CircuitBreaker(self.config)
    
    def test_initial_state(self):
        """Testa estado inicial do circuit breaker"""
        self.assertEqual(self.circuit_breaker.get_state(), CircuitState.CLOSED)
        self.assertEqual(self.circuit_breaker.failure_count, 0)
        self.assertEqual(self.circuit_breaker.success_count, 0)
    
    def test_successful_call(self):
        """Testa chamada bem-sucedida"""
        def successful_function():
            return "success"
        
        result = self.circuit_breaker.call(successful_function)
        self.assertEqual(result, "success")
        self.assertEqual(self.circuit_breaker.get_state(), CircuitState.CLOSED)
        self.assertEqual(self.circuit_breaker.success_count, 1)
        self.assertEqual(self.circuit_breaker.failure_count, 0)
    
    def test_failed_call(self):
        """Testa chamada que falha"""
        def failing_function():
            raise Exception("Test error")
        
        result = self.circuit_breaker.call(failing_function)
        self.assertIsNone(result)  # Fallback padrão
        self.assertEqual(self.circuit_breaker.get_state(), CircuitState.CLOSED)
        self.assertEqual(self.circuit_breaker.failure_count, 1)
        self.assertEqual(self.circuit_breaker.success_count, 0)
    
    def test_circuit_opens_after_threshold(self):
        """Testa abertura do circuit após threshold de falhas"""
        def failing_function():
            raise Exception("Test error")
        
        # Executar falhas até atingir threshold
        for _ in range(self.config.failure_threshold):
            self.circuit_breaker.call(failing_function)
        
        self.assertEqual(self.circuit_breaker.get_state(), CircuitState.OPEN)
        self.assertEqual(self.circuit_breaker.failure_count, self.config.failure_threshold)
    
    def test_circuit_half_open_after_timeout(self):
        """Testa transição para half-open após timeout"""
        def failing_function():
            raise Exception("Test error")
        
        # Abrir circuit
        for _ in range(self.config.failure_threshold):
            self.circuit_breaker.call(failing_function)
        
        self.assertEqual(self.circuit_breaker.get_state(), CircuitState.OPEN)
        
        # Aguardar timeout
        time.sleep(self.config.recovery_timeout + 0.1)
        
        # Próxima chamada deve tentar half-open
        def successful_function():
            return "success"
        
        result = self.circuit_breaker.call(successful_function)
        self.assertEqual(result, "success")
        self.assertEqual(self.circuit_breaker.get_state(), CircuitState.CLOSED)
    
    def test_circuit_closes_after_successful_half_open(self):
        """Testa fechamento do circuit após sucesso no half-open"""
        def failing_function():
            raise Exception("Test error")
        
        # Abrir circuit
        for _ in range(self.config.failure_threshold):
            self.circuit_breaker.call(failing_function)
        
        # Aguardar timeout
        time.sleep(self.config.recovery_timeout + 0.1)
        
        # Sucesso no half-open deve fechar circuit
        def successful_function():
            return "success"
        
        result = self.circuit_breaker.call(successful_function)
        self.assertEqual(result, "success")
        self.assertEqual(self.circuit_breaker.get_state(), CircuitState.CLOSED)
        self.assertEqual(self.circuit_breaker.failure_count, 0)
    
    def test_circuit_opens_again_after_half_open_failure(self):
        """Testa reabertura do circuit após falha no half-open"""
        def failing_function():
            raise Exception("Test error")
        
        # Abrir circuit
        for _ in range(self.config.failure_threshold):
            self.circuit_breaker.call(failing_function)
        
        # Aguardar timeout
        time.sleep(self.config.recovery_timeout + 0.1)
        
        # Falha no half-open deve reabrir circuit
        result = self.circuit_breaker.call(failing_function)
        self.assertIsNone(result)
        self.assertEqual(self.circuit_breaker.get_state(), CircuitState.OPEN)
    
    def test_fallback_function(self):
        """Testa função de fallback personalizada"""
        def failing_function():
            raise Exception("Test error")
        
        def fallback_function():
            return "fallback result"
        
        config_with_fallback = CircuitBreakerConfig(
            failure_threshold=1,
            recovery_timeout=1,
            name="test_with_fallback",
            fallback_function=fallback_function
        )
        
        cb_with_fallback = CircuitBreaker(config_with_fallback)
        
        # Falha deve usar fallback
        result = cb_with_fallback.call(failing_function)
        self.assertEqual(result, "fallback result")
    
    def test_reset_function(self):
        """Testa função de reset manual"""
        def failing_function():
            raise Exception("Test error")
        
        # Abrir circuit
        for _ in range(self.config.failure_threshold):
            self.circuit_breaker.call(failing_function)
        
        self.assertEqual(self.circuit_breaker.get_state(), CircuitState.OPEN)
        
        # Reset manual
        self.circuit_breaker.reset()
        
        self.assertEqual(self.circuit_breaker.get_state(), CircuitState.CLOSED)
        self.assertEqual(self.circuit_breaker.failure_count, 0)
        self.assertEqual(self.circuit_breaker.success_count, 0)
    
    def test_get_stats(self):
        """Testa obtenção de estatísticas"""
        def successful_function():
            return "success"
        
        def failing_function():
            raise Exception("Test error")
        
        # Executar algumas chamadas
        self.circuit_breaker.call(successful_function)
        self.circuit_breaker.call(failing_function)
        
        stats = self.circuit_breaker.get_stats()
        
        self.assertEqual(stats['name'], self.config.name)
        self.assertEqual(stats['state'], CircuitState.CLOSED.value)
        self.assertEqual(stats['failure_count'], 1)
        self.assertEqual(stats['success_count'], 1)
        self.assertEqual(stats['failure_threshold'], self.config.failure_threshold)
        self.assertEqual(stats['recovery_timeout'], self.config.recovery_timeout)
    
    def test_decorator_usage(self):
        """Testa uso do decorator"""
        @circuit_breaker(self.config)
        def test_function():
            return "decorated success"
        
        result = test_function()
        self.assertEqual(result, "decorated success")
        
        # Verificar se atributos foram adicionados
        self.assertTrue(hasattr(test_function, 'circuit_breaker'))
        self.assertTrue(hasattr(test_function, 'get_state'))
        self.assertTrue(hasattr(test_function, 'get_stats'))
        self.assertTrue(hasattr(test_function, 'reset'))


class TestCircuitBreakerConcurrency(unittest.TestCase):
    """Testes de concorrência para Circuit Breaker"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.config = CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=1,
            name="concurrency_test"
        )
        self.circuit_breaker = CircuitBreaker(self.config)
        self.results = []
        self.lock = threading.Lock()
    
    def test_concurrent_calls(self):
        """Testa chamadas concorrentes"""
        def test_function():
            time.sleep(0.1)  # Simular trabalho
            return "success"
        
        def worker():
            result = self.circuit_breaker.call(test_function)
            with self.lock:
                self.results.append(result)
        
        # Criar threads concorrentes
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # Aguardar todas as threads
        for thread in threads:
            thread.join()
        
        # Verificar resultados
        self.assertEqual(len(self.results), 10)
        self.assertTrue(all(result == "success" for result in self.results))
    
    def test_concurrent_failures(self):
        """Testa falhas concorrentes"""
        def failing_function():
            time.sleep(0.1)  # Simular trabalho
            raise Exception("Concurrent error")
        
        def worker():
            result = self.circuit_breaker.call(failing_function)
            with self.lock:
                self.results.append(result)
        
        # Criar threads concorrentes
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # Aguardar todas as threads
        for thread in threads:
            thread.join()
        
        # Verificar que circuit foi aberto
        self.assertEqual(self.circuit_breaker.get_state(), CircuitState.OPEN)
        self.assertEqual(self.circuit_breaker.failure_count, 5)  # Threshold atingido


class TestCircuitBreakerMetrics(unittest.TestCase):
    """Testes para métricas do Circuit Breaker"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=1,
            name="metrics_test"
        )
        self.circuit_breaker = CircuitBreaker(self.config)
    
    @patch('infrastructure.resilience.circuit_breaker.Counter')
    @patch('infrastructure.resilience.circuit_breaker.Histogram')
    @patch('infrastructure.resilience.circuit_breaker.Gauge')
    def test_metrics_initialization(self, mock_gauge, mock_histogram, mock_counter):
        """Testa inicialização das métricas"""
        # Criar novo circuit breaker para testar inicialização
        cb = CircuitBreaker(self.config)
        
        # Verificar se métricas foram criadas
        mock_counter.assert_called()
        mock_histogram.assert_called()
        mock_gauge.assert_called()
    
    def test_metrics_update_on_success(self):
        """Testa atualização de métricas em sucesso"""
        def successful_function():
            return "success"
        
        # Mock das métricas
        with patch.object(self.circuit_breaker, 'success_counter') as mock_success_counter:
            with patch.object(self.circuit_breaker, 'call_duration') as mock_call_duration:
                self.circuit_breaker.call(successful_function)
                
                # Verificar se métricas foram atualizadas
                mock_success_counter.inc.assert_called_once()
                mock_call_duration.time.assert_called_once()
    
    def test_metrics_update_on_failure(self):
        """Testa atualização de métricas em falha"""
        def failing_function():
            raise Exception("Test error")
        
        # Mock das métricas
        with patch.object(self.circuit_breaker, 'failure_counter') as mock_failure_counter:
            self.circuit_breaker.call(failing_function)
            
            # Verificar se métricas foram atualizadas
            mock_failure_counter.inc.assert_called_once()


if __name__ == '__main__':
    unittest.main() 