# =============================================================================
# Testes Unitários - Circuit Breakers e Resiliência
# =============================================================================
# 
# Este arquivo contém testes unitários para validar a implementação
# de circuit breakers e resiliência no Omni Keywords Finder.
#
# Tracing ID: test-resilience-2025-01-27-001
# Versão: 1.0
# Responsável: DevOps Team
# =============================================================================

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Importar módulos de resiliência
from infrastructure.resilience.circuit_breakers import (
from typing import Dict, List, Optional, Any
    CircuitBreaker,
    CircuitBreakerConfig,
    RetryPolicy,
    RetryConfig,
    TimeoutPolicy,
    TimeoutConfig,
    Bulkhead,
    BulkheadConfig,
    ResilienceManager,
    CircuitBreakerOpenError,
    BulkheadFullError
)

from backend.app.services.resilient_keywords_service import ResilientKeywordsService


class TestCircuitBreaker:
    """Testes para Circuit Breaker"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=10,
            timeout=5.0,
            max_retries=2,
            retry_delay=1.0,
            success_threshold=2
        )
        self.circuit_breaker = CircuitBreaker("test_cb", self.config)
    
    def test_circuit_breaker_initial_state(self):
        """Testa estado inicial do circuit breaker"""
        assert self.circuit_breaker.state.value == "closed"
        assert self.circuit_breaker.failure_count == 0
        assert self.circuit_breaker.success_count == 0
    
    def test_successful_call(self):
        """Testa chamada bem-sucedida"""
        def success_func():
            return "success"
        
        result = self.circuit_breaker.call(success_func)
        assert result == "success"
        assert self.circuit_breaker.state.value == "closed"
        assert self.circuit_breaker.success_count == 1
        assert self.circuit_breaker.failure_count == 0
    
    def test_failed_call(self):
        """Testa chamada que falha"""
        def fail_func():
            raise Exception("Test error")
        
        with pytest.raises(Exception):
            self.circuit_breaker.call(fail_func)
        
        assert self.circuit_breaker.failure_count == 1
        assert self.circuit_breaker.state.value == "closed"
    
    def test_circuit_breaker_opens_after_threshold(self):
        """Testa se circuit breaker abre após threshold de falhas"""
        def fail_func():
            raise Exception("Test error")
        
        # Fazer falhas até atingir threshold
        for _ in range(self.config.failure_threshold):
            with pytest.raises(Exception):
                self.circuit_breaker.call(fail_func)
        
        assert self.circuit_breaker.state.value == "open"
        
        # Tentar chamada quando aberto
        def success_func():
            return "success"
        
        with pytest.raises(CircuitBreakerOpenError):
            self.circuit_breaker.call(success_func)
    
    def test_circuit_breaker_half_open_recovery(self):
        """Testa recuperação do circuit breaker em half-open"""
        # Abrir circuit breaker
        def fail_func():
            raise Exception("Test error")
        
        for _ in range(self.config.failure_threshold):
            with pytest.raises(Exception):
                self.circuit_breaker.call(fail_func)
        
        assert self.circuit_breaker.state.value == "open"
        
        # Simular tempo de recuperação
        self.circuit_breaker.last_failure_time = datetime.now() - timedelta(seconds=15)
        
        # Tentar chamada (deve ir para half-open)
        def success_func():
            return "success"
        
        result = self.circuit_breaker.call(success_func)
        assert result == "success"
        assert self.circuit_breaker.state.value == "half_open"
        
        # Mais um sucesso deve fechar o circuit breaker
        result = self.circuit_breaker.call(success_func)
        assert result == "success"
        assert self.circuit_breaker.state.value == "closed"
    
    def test_async_circuit_breaker(self):
        """Testa circuit breaker assíncrono"""
        async def async_success_func():
            await asyncio.sleep(0.1)
            return "async_success"
        
        async def async_fail_func():
            await asyncio.sleep(0.1)
            raise Exception("Async error")
        
        # Teste de sucesso
        result = asyncio.run(self.circuit_breaker.call_async(async_success_func))
        assert result == "async_success"
        assert self.circuit_breaker.state.value == "closed"
        
        # Teste de falha
        with pytest.raises(Exception):
            asyncio.run(self.circuit_breaker.call_async(async_fail_func))
        
        assert self.circuit_breaker.failure_count == 1


class TestRetryPolicy:
    """Testes para Retry Policy"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.config = RetryConfig(
            max_attempts=3,
            base_delay=0.1,
            max_delay=1.0,
            exponential_base=2.0,
            jitter=True
        )
        self.retry_policy = RetryPolicy(self.config)
    
    def test_successful_call_no_retry(self):
        """Testa chamada bem-sucedida sem retry"""
        def success_func():
            return "success"
        
        result = self.retry_policy.execute(success_func)
        assert result == "success"
    
    def test_retry_on_failure(self):
        """Testa retry em caso de falha"""
        call_count = 0
        
        def fail_then_success():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary error")
            return "success"
        
        result = self.retry_policy.execute(fail_then_success)
        assert result == "success"
        assert call_count == 3
    
    def test_max_retries_exceeded(self):
        """Testa quando máximo de retries é excedido"""
        def always_fail():
            raise Exception("Persistent error")
        
        with pytest.raises(Exception):
            self.retry_policy.execute(always_fail)
    
    def test_async_retry_policy(self):
        """Testa retry policy assíncrono"""
        call_count = 0
        
        async def async_fail_then_success():
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.1)
            if call_count < 3:
                raise Exception("Async temporary error")
            return "async_success"
        
        result = asyncio.run(self.retry_policy.execute_async(async_fail_then_success))
        assert result == "async_success"
        assert call_count == 3


class TestTimeoutPolicy:
    """Testes para Timeout Policy"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.config = TimeoutConfig(
            default_timeout=1.0,
            connection_timeout=0.5,
            read_timeout=1.0,
            write_timeout=1.0
        )
        self.timeout_policy = TimeoutPolicy(self.config)
    
    def test_successful_call_within_timeout(self):
        """Testa chamada bem-sucedida dentro do timeout"""
        def quick_func():
            time.sleep(0.1)
            return "success"
        
        result = self.timeout_policy.execute(quick_func)
        assert result == "success"
    
    def test_timeout_exceeded(self):
        """Testa quando timeout é excedido"""
        def slow_func():
            time.sleep(2.0)
            return "success"
        
        with pytest.raises(TimeoutError):
            self.timeout_policy.execute(slow_func)
    
    def test_custom_timeout(self):
        """Testa timeout customizado"""
        def slow_func():
            time.sleep(0.5)
            return "success"
        
        # Timeout customizado menor que o tempo da função
        with pytest.raises(TimeoutError):
            self.timeout_policy.execute(slow_func, timeout=0.1)
        
        # Timeout customizado maior que o tempo da função
        result = self.timeout_policy.execute(slow_func, timeout=1.0)
        assert result == "success"


class TestBulkhead:
    """Testes para Bulkhead Pattern"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.config = BulkheadConfig(
            max_concurrent_calls=2,
            max_wait_duration=1.0,
            max_queue_size=5
        )
        self.bulkhead = Bulkhead("test_bulkhead", self.config)
    
    async def test_concurrent_calls_within_limit(self):
        """Testa chamadas concorrentes dentro do limite"""
        results = []
        
        async def test_func(delay):
            await asyncio.sleep(delay)
            return f"result_{delay}"
        
        # Executar 2 chamadas concorrentes
        tasks = [
            self.bulkhead.execute(test_func, 0.1),
            self.bulkhead.execute(test_func, 0.1)
        ]
        
        results = await asyncio.gather(*tasks)
        assert len(results) == 2
        assert "result_0.1" in results
    
    async def test_bulkhead_full(self):
        """Testa quando bulkhead está cheio"""
        async def slow_func():
            await asyncio.sleep(1.0)
            return "slow_result"
        
        # Executar chamadas até encher o bulkhead
        tasks = []
        for index in range(3):  # Mais que max_concurrent_calls
            tasks.append(self.bulkhead.execute(slow_func))
        
        # A terceira chamada deve falhar
        with pytest.raises(BulkheadFullError):
            await asyncio.gather(*tasks)


class TestResilienceManager:
    """Testes para Resilience Manager"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.manager = ResilienceManager()
    
    def test_add_circuit_breaker(self):
        """Testa adição de circuit breaker"""
        config = CircuitBreakerConfig(failure_threshold=5)
        cb = self.manager.add_circuit_breaker("test_cb", config)
        
        assert cb.name == "test_cb"
        assert "test_cb" in self.manager.circuit_breakers
    
    def test_add_retry_policy(self):
        """Testa adição de retry policy"""
        config = RetryConfig(max_attempts=3)
        rp = self.manager.add_retry_policy("test_retry", config)
        
        assert rp.config.max_attempts == 3
        assert "test_retry" in self.manager.retry_policies
    
    def test_execute_resilient(self):
        """Testa execução resiliente"""
        # Adicionar circuit breaker
        cb_config = CircuitBreakerConfig(failure_threshold=3)
        self.manager.add_circuit_breaker("test_cb", cb_config)
        
        def success_func():
            return "success"
        
        result = self.manager.execute_resilient(
            func=success_func,
            circuit_breaker_name="test_cb"
        )
        
        assert result == "success"
    
    def test_execute_resilient_with_fallback(self):
        """Testa execução resiliente com fallback"""
        # Adicionar circuit breaker
        cb_config = CircuitBreakerConfig(failure_threshold=1)
        self.manager.add_circuit_breaker("test_cb", cb_config)
        
        # Adicionar fallback strategy
        def fallback_func(*args, **kwargs):
            return "fallback_result"
        
        self.manager.add_fallback_strategy("test_fallback", fallback_func)
        
        def fail_func():
            raise Exception("Test error")
        
        result = self.manager.execute_resilient(
            func=fail_func,
            circuit_breaker_name="test_cb",
            fallback_strategy_name="test_fallback"
        )
        
        assert result == "fallback_result"


class TestResilientKeywordsService:
    """Testes para Resilient Keywords Service"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.service = ResilientKeywordsService()
    
    async def test_get_keywords_success(self):
        """Testa busca de keywords bem-sucedida"""
        with patch.object(self.service, '_fetch_keywords_from_api') as mock_fetch:
            mock_fetch.return_value = {
                "keywords": [{"keyword": "test", "volume": 100}],
                "total": 1,
                "query": "test",
                "source": "api"
            }
            
            result = await self.service.get_keywords("test", 10)
            
            assert result["keywords"][0]["keyword"] == "test"
            assert result["source"] == "api"
            mock_fetch.assert_called_once_with("test", 10)
    
    async def test_get_keywords_fallback(self):
        """Testa fallback quando API falha"""
        with patch.object(self.service, '_fetch_keywords_from_api') as mock_fetch:
            mock_fetch.side_effect = Exception("API error")
            
            result = await self.service.get_keywords("seo", 10)
            
            assert result["source"] == "fallback"
            assert "message" in result
            assert "fallback" in result["message"]
    
    async def test_analyze_keywords_success(self):
        """Testa análise de keywords bem-sucedida"""
        keywords = ["test1", "test2"]
        
        with patch('asyncio.sleep'):  # Mock sleep para acelerar teste
            result = await self.service.analyze_keywords(keywords)
            
            assert result["summary"]["total_keywords"] == 2
            assert len(result["keywords"]) == 2
            assert "recommendations" in result["summary"]
    
    async def test_analyze_keywords_fallback(self):
        """Testa fallback na análise de keywords"""
        keywords = ["test1", "test2"]
        
        with patch('asyncio.sleep'), patch('random.random', return_value=0.1):  # Forçar falha
            result = await self.service.analyze_keywords(keywords)
            
            assert result["source"] == "fallback"
            assert result["keywords"][0]["volume"] == "N/A"
    
    async def test_get_keyword_suggestions(self):
        """Testa obtenção de sugestões de keywords"""
        result = await self.service.get_keyword_suggestions("seo")
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert all("seo" in suggestion.lower() for suggestion in result)
    
    def test_service_health(self):
        """Testa status de saúde do serviço"""
        health = self.service.get_service_health()
        
        assert health["status"] == "healthy"
        assert "cache" in health
        assert "fallback_usage" in health
        assert "timestamp" in health


class TestResilienceIntegration:
    """Testes de integração de resiliência"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.manager = ResilienceManager()
    
    async def test_full_resilience_chain(self):
        """Testa cadeia completa de resiliência"""
        # Configurar circuit breaker
        cb_config = CircuitBreakerConfig(failure_threshold=2)
        self.manager.add_circuit_breaker("test_cb", cb_config)
        
        # Configurar retry policy
        retry_config = RetryConfig(max_attempts=2)
        self.manager.add_retry_policy("test_retry", retry_config)
        
        # Configurar timeout policy
        timeout_config = TimeoutConfig(default_timeout=1.0)
        self.manager.add_timeout_policy("test_timeout", timeout_config)
        
        # Configurar fallback
        def fallback_func(*args, **kwargs):
            return "fallback_result"
        
        self.manager.add_fallback_strategy("test_fallback", fallback_func)
        
        # Função que falha
        call_count = 0
        async def fail_func():
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.1)
            raise Exception("Test error")
        
        # Executar com todas as políticas
        result = await self.manager.execute_resilient_async(
            func=fail_func,
            circuit_breaker_name="test_cb",
            retry_policy_name="test_retry",
            timeout_policy_name="test_timeout",
            fallback_strategy_name="test_fallback"
        )
        
        assert result == "fallback_result"
        assert call_count > 0


if __name__ == "__main__":
    pytest.main([__file__, "-value"]) 