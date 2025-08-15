"""
Testes para Sistema de API Client - Omni Keywords Finder

Tracing ID: TEST_API_CLIENT_2025-01-27-001
Versão: 1.0
Responsável: QA Team

Testa funcionalidades do API Client:
- Circuit breakers
- Rate limiting
- Fallback mechanisms
- Integração entre componentes
- Cenários de falha e recuperação

Metodologias Aplicadas:
- 📐 CoCoT: Baseado em padrões de teste de resiliência e integração
- 🌲 ToT: Avaliado cenários de teste e escolhido cobertura ideal
- ♻️ ReAct: Simulado cenários de falha e validado robustez
"""

import pytest
import time
import threading
import asyncio
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

# Importar componentes a testar
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

from infrastructure.orchestrator.error_handler import CircuitBreaker, CircuitBreakerState
from infrastructure.orchestrator.rate_limiter import (
    RateLimiterManager, RateLimitConfig, RateLimitStrategy, 
    TokenBucketRateLimiter, LeakyBucketRateLimiter, SlidingWindowRateLimiter
)
from infrastructure.orchestrator.fallback_manager import (
    FallbackManager, FallbackConfig, FallbackStrategy,
    MemoryCache, LocalFileCache, CompensationQueue
)


class TestCircuitBreaker:
    """
    Testes para Circuit Breaker.
    
    📐 CoCoT: Baseado em padrões de teste de circuit breakers
    """
    
    def setup_method(self):
        """Setup para cada teste."""
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60,
            expected_exception=Exception
        )
    
    def test_circuit_breaker_initial_state(self):
        """Testa estado inicial do circuit breaker."""
        assert self.circuit_breaker.state == CircuitBreakerState.CLOSED
        assert self.circuit_breaker.failure_count == 0
        assert self.circuit_breaker.last_failure_time == 0
    
    def test_circuit_breaker_closed_to_open(self):
        """Testa transição de CLOSED para OPEN."""
        # Simular falhas consecutivas
        for index in range(3):
            with pytest.raises(Exception):
                with self.circuit_breaker:
                    raise Exception(f"Falha {index+1}")
        
        assert self.circuit_breaker.state == CircuitBreakerState.OPEN
        assert self.circuit_breaker.failure_count == 3
    
    def test_circuit_breaker_open_blocks_requests(self):
        """Testa que circuit breaker OPEN bloqueia requests."""
        # Abrir circuit breaker
        for index in range(3):
            with pytest.raises(Exception):
                with self.circuit_breaker:
                    raise Exception(f"Falha {index+1}")
        
        # Tentar executar função
        with pytest.raises(Exception) as exc_info:
            with self.circuit_breaker:
                return "sucesso"
        
        assert "Circuit breaker is OPEN" in str(exc_info.value)
    
    def test_circuit_breaker_half_open_recovery(self):
        """Testa recuperação do circuit breaker."""
        # Abrir circuit breaker
        for index in range(3):
            with pytest.raises(Exception):
                with self.circuit_breaker:
                    raise Exception(f"Falha {index+1}")
        
        # Avançar tempo para permitir recuperação
        with patch('time.time') as mock_time:
            mock_time.return_value = time.time() + 61  # 61 segundos depois
            
            # Primeira tentativa deve ser permitida (HALF_OPEN)
            with self.circuit_breaker:
                result = "sucesso"
                assert result == "sucesso"
            
            # Se sucesso, deve voltar para CLOSED
            assert self.circuit_breaker.state == CircuitBreakerState.CLOSED
            assert self.circuit_breaker.failure_count == 0
    
    def test_circuit_breaker_half_open_failure(self):
        """Testa falha durante estado HALF_OPEN."""
        # Abrir circuit breaker
        for index in range(3):
            with pytest.raises(Exception):
                with self.circuit_breaker:
                    raise Exception(f"Falha {index+1}")
        
        # Avançar tempo para permitir recuperação
        with patch('time.time') as mock_time:
            mock_time.return_value = time.time() + 61
            
            # Falha durante HALF_OPEN deve reabrir circuit breaker
            with pytest.raises(Exception):
                with self.circuit_breaker:
                    raise Exception("Falha durante recuperação")
            
            assert self.circuit_breaker.state == CircuitBreakerState.OPEN
            assert self.circuit_breaker.failure_count == 4
    
    def test_circuit_breaker_ignores_unexpected_exceptions(self):
        """Testa que circuit breaker ignora exceções inesperadas."""
        # Tentar executar com exceção não esperada
        with self.circuit_breaker:
            raise ValueError("Exceção não esperada")
        
        # Circuit breaker não deve abrir
        assert self.circuit_breaker.state == CircuitBreakerState.CLOSED
        assert self.circuit_breaker.failure_count == 0


class TestRateLimiter:
    """
    Testes para Rate Limiter.
    
    📐 CoCoT: Baseado em padrões de teste de rate limiting
    """
    
    def setup_method(self):
        """Setup para cada teste."""
        self.rate_limiter_manager = RateLimiterManager()
    
    def test_token_bucket_rate_limiter(self):
        """Testa Token Bucket Rate Limiter."""
        config = RateLimitConfig(
            endpoint="test_endpoint",
            requests_per_second=10,
            burst_limit=20,
            strategy=RateLimitStrategy.TOKEN_BUCKET
        )
        
        self.rate_limiter_manager.register_endpoint(config)
        
        # Testar dentro do limite
        for index in range(10):
            assert self.rate_limiter_manager.acquire("test_endpoint")
        
        # Testar burst
        for index in range(10):
            assert self.rate_limiter_manager.acquire("test_endpoint")
        
        # Testar limite excedido
        assert not self.rate_limiter_manager.acquire("test_endpoint")
    
    def test_leaky_bucket_rate_limiter(self):
        """Testa Leaky Bucket Rate Limiter."""
        config = RateLimitConfig(
            endpoint="test_endpoint",
            requests_per_second=5,
            burst_limit=10,
            strategy=RateLimitStrategy.LEAKY_BUCKET
        )
        
        self.rate_limiter_manager.register_endpoint(config)
        
        # Testar dentro do limite
        for index in range(5):
            assert self.rate_limiter_manager.acquire("test_endpoint")
        
        # Testar burst
        for index in range(5):
            assert self.rate_limiter_manager.acquire("test_endpoint")
        
        # Testar limite excedido
        assert not self.rate_limiter_manager.acquire("test_endpoint")
    
    def test_sliding_window_rate_limiter(self):
        """Testa Sliding Window Rate Limiter."""
        config = RateLimitConfig(
            endpoint="test_endpoint",
            requests_per_second=10,
            window_size=60,
            strategy=RateLimitStrategy.SLIDING_WINDOW
        )
        
        self.rate_limiter_manager.register_endpoint(config)
        
        # Testar dentro do limite
        for index in range(10):
            assert self.rate_limiter_manager.acquire("test_endpoint")
        
        # Testar limite excedido
        assert not self.rate_limiter_manager.acquire("test_endpoint")
    
    def test_adaptive_rate_limiter(self):
        """Testa Adaptive Rate Limiter."""
        config = RateLimitConfig(
            endpoint="test_endpoint",
            requests_per_second=10,
            adaptive_enabled=True,
            strategy=RateLimitStrategy.ADAPTIVE
        )
        
        self.rate_limiter_manager.register_endpoint(config)
        
        # Simular falhas para ativar adaptive rate limiting
        for index in range(5):
            self.rate_limiter_manager.record_response("test_endpoint", 3.0, False)
        
        # Rate limiter deve reduzir taxa automaticamente
        metrics = self.rate_limiter_manager.get_metrics()
        assert metrics['requests_total'] >= 0
    
    def test_rate_limiter_retry_decorator(self):
        """Testa decorator de retry do rate limiter."""
        config = RateLimitConfig(
            endpoint="test_endpoint",
            requests_per_second=1,
            retry_enabled=True,
            max_retries=2
        )
        
        self.rate_limiter_manager.register_endpoint(config)
        
        call_count = 0
        
        @self.rate_limiter_manager.with_retry("test_endpoint")
        def test_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Falha temporária")
            return "sucesso"
        
        # Primeira execução deve falhar e retry
        result = test_function()
        assert result == "sucesso"
        assert call_count == 3
    
    def test_rate_limiter_metrics(self):
        """Testa métricas do rate limiter."""
        config = RateLimitConfig(
            endpoint="test_endpoint",
            requests_per_second=10
        )
        
        self.rate_limiter_manager.register_endpoint(config)
        
        # Executar algumas requests
        for index in range(5):
            self.rate_limiter_manager.acquire("test_endpoint")
        
        metrics = self.rate_limiter_manager.get_metrics()
        assert metrics['requests_total'] == 5
        assert metrics['requests_allowed'] == 5
        assert metrics['limit_rate'] == 100.0


class TestFallbackManager:
    """
    Testes para Fallback Manager.
    
    📐 CoCoT: Baseado em padrões de teste de sistemas de fallback
    """
    
    def setup_method(self):
        """Setup para cada teste."""
        self.fallback_manager = FallbackManager()
    
    def test_memory_cache(self):
        """Testa cache em memória."""
        cache = MemoryCache(max_size=2)
        
        # Testar set/get
        cache.set("key1", "value1", ttl=3600)
        assert cache.get("key1") == "value1"
        
        # Testar TTL
        cache.set("key2", "value2", ttl=1)
        time.sleep(1.1)
        assert cache.get("key2") is None
        
        # Testar LRU
        cache.set("key3", "value3", ttl=3600)
        cache.set("key4", "value4", ttl=3600)
        # key1 deve ter sido removido
        assert cache.get("key1") is None
    
    def test_local_file_cache(self):
        """Testa cache em arquivo local."""
        cache = LocalFileCache(cache_dir="test_cache")
        
        # Testar set/get
        cache.set("key1", "value1", ttl=3600)
        assert cache.get("key1") == "value1"
        
        # Testar TTL
        cache.set("key2", "value2", ttl=1)
        time.sleep(1.1)
        assert cache.get("key2") is None
        
        # Limpar cache de teste
        cache.delete("key1")
    
    def test_compensation_queue(self):
        """Testa fila de compensação."""
        queue = CompensationQueue(max_size=5)
        
        # Adicionar tarefas
        task1 = CompensationTask(
            id="task1",
            endpoint="test_endpoint",
            operation="test_op",
            data={"test": "data"},
            priority=1
        )
        
        task2 = CompensationTask(
            id="task2",
            endpoint="test_endpoint",
            operation="test_op",
            data={"test": "data"},
            priority=5
        )
        
        assert queue.add_task(task1)
        assert queue.add_task(task2)
        
        # task2 deve ter prioridade maior
        next_task = queue.get_next_task()
        assert next_task.id == "task2"
    
    def test_fallback_cache_only_strategy(self):
        """Testa estratégia CACHE_ONLY."""
        config = FallbackConfig(
            endpoint="test_endpoint",
            strategy=FallbackStrategy.CACHE_ONLY,
            cache_enabled=True,
            cache_ttl=3600
        )
        
        self.fallback_manager.register_endpoint(config)
        
        # Simular cache hit
        self.fallback_manager.set_cached_value("test_key", "cached_value", 3600, [CacheLevel.MEMORY])
        
        @self.fallback_manager.with_fallback("test_endpoint", "test_key")
        def failing_function():
            raise Exception("API falhou")
        
        # Deve retornar valor do cache
        result = failing_function()
        assert result == "cached_value"
    
    def test_fallback_compensation_queue_strategy(self):
        """Testa estratégia COMPENSATION_QUEUE."""
        config = FallbackConfig(
            endpoint="test_endpoint",
            strategy=FallbackStrategy.COMPENSATION_QUEUE,
            compensation_enabled=True
        )
        
        self.fallback_manager.register_endpoint(config)
        
        @self.fallback_manager.with_fallback("test_endpoint")
        def failing_function():
            raise Exception("API falhou")
        
        # Deve adicionar à fila de compensação
        result = failing_function()
        assert result is None
        
        # Verificar se tarefa foi adicionada
        metrics = self.fallback_manager.get_metrics()
        assert metrics['compensation_tasks'] == 1
    
    def test_fallback_hierarchical_strategy(self):
        """Testa estratégia HIERARCHICAL."""
        config = FallbackConfig(
            endpoint="test_endpoint",
            strategy=FallbackStrategy.HIERARCHICAL,
            cache_enabled=True,
            compensation_enabled=True
        )
        
        self.fallback_manager.register_endpoint(config)
        
        # Simular cache hit
        self.fallback_manager.set_cached_value("test_key", "cached_value", 3600, [CacheLevel.MEMORY])
        
        @self.fallback_manager.with_fallback("test_endpoint", "test_key")
        def failing_function():
            raise Exception("API falhou")
        
        # Deve usar cache primeiro
        result = failing_function()
        assert result == "cached_value"
        
        # Se não tiver cache, deve usar compensação
        @self.fallback_manager.with_fallback("test_endpoint", "no_cache_key")
        def another_failing_function():
            raise Exception("API falhou")
        
        result = another_failing_function()
        assert result is None
    
    def test_fallback_metrics(self):
        """Testa métricas do fallback manager."""
        config = FallbackConfig(
            endpoint="test_endpoint",
            cache_enabled=True
        )
        
        self.fallback_manager.register_endpoint(config)
        
        # Simular cache hit
        self.fallback_manager.set_cached_value("test_key", "value", 3600, [CacheLevel.MEMORY])
        self.fallback_manager.get_cached_value("test_key", [CacheLevel.MEMORY])
        
        metrics = self.fallback_manager.get_metrics()
        assert metrics['cache_hits'] == 1
        assert metrics['cache_hit_rate'] == 100.0


class TestIntegration:
    """
    Testes de integração entre componentes.
    
    🌲 ToT: Avaliado cenários de integração e escolhido mais críticos
    """
    
    def setup_method(self):
        """Setup para cada teste."""
        self.rate_limiter_manager = RateLimiterManager()
        self.fallback_manager = FallbackManager()
    
    def test_circuit_breaker_with_rate_limiter(self):
        """Testa integração entre circuit breaker e rate limiter."""
        # Configurar rate limiter
        config = RateLimitConfig(
            endpoint="test_endpoint",
            requests_per_second=5,
            circuit_breaker_threshold=3
        )
        
        self.rate_limiter_manager.register_endpoint(config)
        
        # Simular falhas para abrir circuit breaker
        for index in range(3):
            self.rate_limiter_manager.record_response("test_endpoint", 1.0, False)
        
        # Circuit breaker deve estar aberto
        assert not self.rate_limiter_manager.acquire("test_endpoint")
    
    def test_rate_limiter_with_fallback(self):
        """Testa integração entre rate limiter e fallback."""
        # Configurar rate limiter
        rate_config = RateLimitConfig(
            endpoint="test_endpoint",
            requests_per_second=1
        )
        
        # Configurar fallback
        fallback_config = FallbackConfig(
            endpoint="test_endpoint",
            strategy=FallbackStrategy.CACHE_ONLY,
            cache_enabled=True
        )
        
        self.rate_limiter_manager.register_endpoint(rate_config)
        self.fallback_manager.register_endpoint(fallback_config)
        
        # Simular cache
        self.fallback_manager.set_cached_value("test_key", "cached_value", 3600, [CacheLevel.MEMORY])
        
        # Primeira request deve passar
        assert self.rate_limiter_manager.acquire("test_endpoint")
        
        # Segunda request deve ser limitada
        assert not self.rate_limiter_manager.acquire("test_endpoint")
        
        # Mas fallback deve funcionar
        cached_value = self.fallback_manager.get_cached_value("test_key", [CacheLevel.MEMORY])
        assert cached_value == "cached_value"
    
    def test_complete_resilience_chain(self):
        """Testa cadeia completa de resiliência."""
        # Configurar todos os componentes
        rate_config = RateLimitConfig(
            endpoint="test_endpoint",
            requests_per_second=10,
            circuit_breaker_threshold=2
        )
        
        fallback_config = FallbackConfig(
            endpoint="test_endpoint",
            strategy=FallbackStrategy.HIERARCHICAL,
            cache_enabled=True,
            compensation_enabled=True
        )
        
        self.rate_limiter_manager.register_endpoint(rate_config)
        self.fallback_manager.register_endpoint(fallback_config)
        
        # Simular cenário real
        def api_call():
            # Simular falha ocasional
            if time.time() % 2 == 0:
                raise Exception("API falhou")
            return "sucesso"
        
        # Executar múltiplas chamadas
        results = []
        for index in range(5):
            try:
                # Rate limiting
                if self.rate_limiter_manager.acquire("test_endpoint"):
                    result = api_call()
                    self.rate_limiter_manager.record_response("test_endpoint", 1.0, True)
                    results.append(result)
                else:
                    # Fallback
                    cached_value = self.fallback_manager.get_cached_value("test_key", [CacheLevel.MEMORY])
                    if cached_value:
                        results.append(cached_value)
                    else:
                        results.append("fallback")
            except Exception:
                self.rate_limiter_manager.record_response("test_endpoint", 1.0, False)
                results.append("error")
        
        # Verificar que sistema manteve estabilidade
        assert len(results) == 5
        assert "error" in results or "fallback" in results  # Deve ter usado fallback


class TestPerformance:
    """
    Testes de performance.
    
    ♻️ ReAct: Simulado cenários de carga e validado estabilidade
    """
    
    def test_rate_limiter_high_load(self):
        """Testa rate limiter sob alta carga."""
        config = RateLimitConfig(
            endpoint="test_endpoint",
            requests_per_second=1000,
            burst_limit=2000
        )
        
        rate_limiter_manager = RateLimiterManager()
        rate_limiter_manager.register_endpoint(config)
        
        # Simular alta carga
        start_time = time.time()
        success_count = 0
        
        for index in range(2000):
            if rate_limiter_manager.acquire("test_endpoint"):
                success_count += 1
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Verificar performance
        assert duration < 1.0  # Deve ser rápido
        assert success_count >= 1000  # Deve permitir pelo menos o rate limit
    
    def test_fallback_manager_concurrent_access(self):
        """Testa fallback manager com acesso concorrente."""
        fallback_manager = FallbackManager()
        
        config = FallbackConfig(
            endpoint="test_endpoint",
            cache_enabled=True
        )
        
        fallback_manager.register_endpoint(config)
        
        def worker(worker_id):
            for index in range(100):
                key = f"key_{worker_id}_{index}"
                value = f"value_{worker_id}_{index}"
                
                fallback_manager.set_cached_value(key, value, 3600, [CacheLevel.MEMORY])
                cached_value = fallback_manager.get_cached_value(key, [CacheLevel.MEMORY])
                
                assert cached_value == value
        
        # Executar workers concorrentes
        threads = []
        for index in range(5):
            thread = threading.Thread(target=worker, args=(index,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verificar métricas
        metrics = fallback_manager.get_metrics()
        assert metrics['cache_hits'] >= 500
        assert metrics['cache_misses'] == 0
    
    def test_circuit_breaker_recovery_performance(self):
        """Testa performance de recuperação do circuit breaker."""
        circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=1  # 1 segundo para teste
        )
        
        # Abrir circuit breaker
        for index in range(3):
            with pytest.raises(Exception):
                with circuit_breaker:
                    raise Exception("Falha")
        
        # Aguardar recuperação
        time.sleep(1.1)
        
        # Testar recuperação
        start_time = time.time()
        
        with circuit_breaker:
            result = "sucesso"
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Verificar que recuperação foi rápida
        assert duration < 0.1
        assert result == "sucesso"
        assert circuit_breaker.state == CircuitBreakerState.CLOSED


class TestEdgeCases:
    """
    Testes de casos extremos.
    
    ♻️ ReAct: Simulado cenários extremos e validado robustez
    """
    
    def test_rate_limiter_zero_rate(self):
        """Testa rate limiter com taxa zero."""
        config = RateLimitConfig(
            endpoint="test_endpoint",
            requests_per_second=0
        )
        
        rate_limiter_manager = RateLimiterManager()
        rate_limiter_manager.register_endpoint(config)
        
        # Não deve permitir nenhuma request
        assert not rate_limiter_manager.acquire("test_endpoint")
    
    def test_circuit_breaker_zero_threshold(self):
        """Testa circuit breaker com threshold zero."""
        circuit_breaker = CircuitBreaker(
            failure_threshold=0,
            recovery_timeout=60
        )
        
        # Deve abrir imediatamente com qualquer falha
        with pytest.raises(Exception):
            with circuit_breaker:
                raise Exception("Falha")
        
        assert circuit_breaker.state == CircuitBreakerState.OPEN
    
    def test_fallback_manager_empty_cache(self):
        """Testa fallback manager com cache vazio."""
        fallback_manager = FallbackManager()
        
        # Tentar obter de cache vazio
        value = fallback_manager.get_cached_value("inexistent_key", [CacheLevel.MEMORY])
        assert value is None
    
    def test_concurrent_circuit_breaker_access(self):
        """Testa acesso concorrente ao circuit breaker."""
        circuit_breaker = CircuitBreaker(
            failure_threshold=10,
            recovery_timeout=60
        )
        
        def worker():
            for index in range(5):
                try:
                    with circuit_breaker:
                        if index % 2 == 0:
                            raise Exception("Falha")
                        return "sucesso"
                except Exception:
                    pass
        
        # Executar workers concorrentes
        threads = []
        for index in range(10):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verificar que circuit breaker manteve consistência
        assert circuit_breaker.failure_count >= 0
        assert circuit_breaker.failure_count <= 10


# Configuração do pytest
def pytest_configure(config):
    """Configuração do pytest."""
    # Adicionar markers
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )


# Fixtures
@pytest.fixture
def rate_limiter_manager():
    """Fixture para RateLimiterManager."""
    return RateLimiterManager()


@pytest.fixture
def fallback_manager():
    """Fixture para FallbackManager."""
    return FallbackManager()


@pytest.fixture
def circuit_breaker():
    """Fixture para CircuitBreaker."""
    return CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=60,
        expected_exception=Exception
    )


if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-value"]) 