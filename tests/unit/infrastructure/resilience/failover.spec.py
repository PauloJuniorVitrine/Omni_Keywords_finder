# =============================================================================
# Testes de Failover - Circuit Breakers e Resiliência
# =============================================================================
# 
# Este arquivo contém testes de failover para validar a capacidade
# do sistema de se recuperar de falhas e manter operação.
#
# Tracing ID: test-failover-2025-01-27-001
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

from backend.app.middleware.resilience import ResilienceMiddleware
from backend.app.services.resilient_keywords_service import ResilientKeywordsService


class TestFailoverScenarios:
    """Testes de cenários de failover"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.resilience_manager = ResilienceManager()
        self.keywords_service = ResilientKeywordsService()
        
        # Configurar circuit breakers para teste
        self.resilience_manager.add_circuit_breaker(
            "test_api",
            CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=5,
                timeout=2.0,
                max_retries=2,
                retry_delay=0.1,
                success_threshold=2
            )
        )
        
        self.resilience_manager.add_retry_policy(
            "test_retry",
            RetryConfig(
                max_attempts=3,
                base_delay=0.1,
                max_delay=1.0,
                exponential_base=2.0,
                jitter=True
            )
        )
    
    def test_circuit_breaker_failover(self):
        """Testa failover quando circuit breaker abre"""
        call_count = 0
        
        def failing_service():
            nonlocal call_count
            call_count += 1
            raise Exception("Service unavailable")
        
        def fallback_service():
            return {"status": "fallback", "data": "cached_data"}
        
        # Adicionar fallback strategy
        self.resilience_manager.add_fallback_strategy(
            "test_fallback",
            fallback_service
        )
        
        # Executar com resiliência
        result = self.resilience_manager.execute_resilient(
            func=failing_service,
            circuit_breaker_name="test_api",
            retry_policy_name="test_retry",
            fallback_strategy_name="test_fallback"
        )
        
        # Verificar que fallback foi usado
        assert result["status"] == "fallback"
        assert result["data"] == "cached_data"
        
        # Verificar que circuit breaker abriu
        cb = self.resilience_manager.circuit_breakers["test_api"]
        assert cb.state.value == "open"
    
    def test_retry_policy_failover(self):
        """Testa failover com retry policy"""
        call_count = 0
        
        def intermittent_service():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return {"status": "success", "attempt": call_count}
        
        # Executar com retry
        result = self.resilience_manager.execute_resilient(
            func=intermittent_service,
            retry_policy_name="test_retry"
        )
        
        # Verificar que funcionou após retries
        assert result["status"] == "success"
        assert result["attempt"] == 3
        assert call_count == 3
    
    def test_timeout_failover(self):
        """Testa failover por timeout"""
        def slow_service():
            time.sleep(3)  # Mais que o timeout de 2s
            return "success"
        
        def timeout_fallback():
            return {"status": "timeout_fallback", "message": "Service timeout"}
        
        # Adicionar fallback para timeout
        self.resilience_manager.add_fallback_strategy(
            "timeout_fallback",
            timeout_fallback
        )
        
        # Executar com timeout
        result = self.resilience_manager.execute_resilient(
            func=slow_service,
            timeout_policy_name="test_timeout",
            fallback_strategy_name="timeout_fallback"
        )
        
        # Verificar que fallback foi usado
        assert result["status"] == "timeout_fallback"
    
    def test_bulkhead_failover(self):
        """Testa failover quando bulkhead está cheio"""
        async def test_bulkhead_failover():
            # Configurar bulkhead pequeno
            self.resilience_manager.add_bulkhead(
                "test_bulkhead",
                BulkheadConfig(
                    max_concurrent_calls=2,
                    max_wait_duration=1.0,
                    max_queue_size=1
                )
            )
            
            def slow_service():
                time.sleep(0.5)
                return "success"
            
            def bulkhead_fallback():
                return {"status": "bulkhead_fallback", "message": "Too many requests"}
            
            # Adicionar fallback
            self.resilience_manager.add_fallback_strategy(
                "bulkhead_fallback",
                bulkhead_fallback
            )
            
            # Executar múltiplas chamadas simultâneas
            tasks = []
            for index in range(5):
                task = self.resilience_manager.execute_resilient_async(
                    func=slow_service,
                    bulkhead_name="test_bulkhead",
                    fallback_strategy_name="bulkhead_fallback"
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Verificar que algumas chamadas usaram fallback
            fallback_count = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "bulkhead_fallback")
            assert fallback_count > 0
        
        asyncio.run(test_bulkhead_failover())
    
    def test_graceful_degradation(self):
        """Testa degradação graciosa do serviço"""
        async def test_graceful_degradation():
            # Simular serviço com degradação gradual
            service_health = 100  # 100% saudável
            
            def degrading_service():
                nonlocal service_health
                if service_health < 20:
                    raise Exception("Service completely down")
                elif service_health < 50:
                    # Retorna dados limitados
                    service_health -= 10
                    return {"status": "degraded", "data": "limited_data"}
                else:
                    # Funciona normalmente
                    service_health -= 5
                    return {"status": "healthy", "data": "full_data"}
            
            def graceful_fallback():
                return {"status": "fallback", "data": "essential_data"}
            
            # Adicionar fallback
            self.resilience_manager.add_fallback_strategy(
                "graceful_fallback",
                graceful_fallback
            )
            
            results = []
            for _ in range(10):
                try:
                    result = self.resilience_manager.execute_resilient(
                        func=degrading_service,
                        fallback_strategy_name="graceful_fallback"
                    )
                    results.append(result)
                except Exception:
                    results.append({"status": "error"})
            
            # Verificar que o serviço degradou graciosamente
            statuses = [r.get("status") for r in results]
            assert "healthy" in statuses
            assert "degraded" in statuses
            assert "fallback" in statuses or "error" in statuses
        
        asyncio.run(test_graceful_degradation())


class TestKeywordsServiceFailover:
    """Testes de failover específicos do serviço de keywords"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.service = ResilientKeywordsService()
    
    async def test_keywords_api_failover(self):
        """Testa failover quando API de keywords falha"""
        # Simular falha da API
        with patch.object(self.service, '_fetch_keywords_from_api') as mock_api:
            mock_api.side_effect = Exception("API unavailable")
            
            # Buscar keywords
            result = await self.service.get_keywords("test query", limit=5)
            
            # Verificar que fallback foi usado
            assert result["source"] == "fallback"
            assert "message" in result
            assert "indisponibilidade" in result["message"]
            assert len(result["keywords"]) > 0
    
    async def test_analysis_service_failover(self):
        """Testa failover quando serviço de análise falha"""
        # Simular falha do serviço de análise
        with patch.object(self.service, 'analyze_keywords') as mock_analysis:
            mock_analysis.side_effect = Exception("Analysis service down")
            
            # Tentar analisar keywords
            with pytest.raises(Exception):
                await self.service.analyze_keywords(["test", "keywords"])
    
    async def test_suggestions_service_failover(self):
        """Testa failover quando serviço de sugestões falha"""
        # Simular falha do serviço de sugestões
        with patch.object(self.service, 'get_keyword_suggestions') as mock_suggestions:
            mock_suggestions.side_effect = Exception("Suggestions service unavailable")
            
            # Tentar obter sugestões
            with pytest.raises(Exception):
                await self.service.get_keyword_suggestions("test keyword")


class TestResilienceMiddlewareFailover:
    """Testes de failover do middleware de resiliência"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.resilience_manager = ResilienceManager()
        self.middleware = ResilienceMiddleware(None, self.resilience_manager)
    
    async def test_middleware_circuit_breaker_failover(self):
        """Testa failover do middleware quando circuit breaker abre"""
        # Simular request
        mock_request = Mock()
        mock_request.url.path = "/api/v1/keywords/search"
        mock_request.method = "GET"
        
        # Simular call_next que falha
        async def failing_call_next(request):
            raise Exception("Service unavailable")
        
        # Executar middleware
        response = await self.middleware.dispatch(mock_request, failing_call_next)
        
        # Verificar que fallback response foi retornado
        assert response.status_code == 503
        assert "circuit_breaker_open" in response.body.decode()
    
    async def test_middleware_bulkhead_failover(self):
        """Testa failover do middleware quando bulkhead está cheio"""
        # Simular request
        mock_request = Mock()
        mock_request.url.path = "/api/v1/ml/analyze"
        mock_request.method = "POST"
        
        # Simular call_next que demora muito
        async def slow_call_next(request):
            await asyncio.sleep(2)
            return Mock()
        
        # Configurar bulkhead pequeno
        self.resilience_manager.add_bulkhead(
            "api_bulkhead",
            BulkheadConfig(
                max_concurrent_calls=1,
                max_wait_duration=0.1,
                max_queue_size=1
            )
        )
        
        # Executar múltiplas requests simultâneas
        tasks = []
        for _ in range(3):
            task = self.middleware.dispatch(mock_request, slow_call_next)
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verificar que algumas requests falharam por bulkhead cheio
        bulkhead_errors = sum(1 for r in responses if isinstance(r, Exception) or 
                             (hasattr(r, 'body') and 'bulkhead_full' in r.body.decode()))
        assert bulkhead_errors > 0


class TestFailoverMetrics:
    """Testes de métricas de failover"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.resilience_manager = ResilienceManager()
        
        # Adicionar circuit breaker para teste
        self.resilience_manager.add_circuit_breaker(
            "test_metrics",
            CircuitBreakerConfig(
                failure_threshold=2,
                recovery_timeout=5,
                timeout=1.0,
                max_retries=1,
                retry_delay=0.1,
                success_threshold=1
            )
        )
    
    def test_failover_metrics_collection(self):
        """Testa coleta de métricas durante failover"""
        def failing_service():
            raise Exception("Service failure")
        
        def successful_service():
            return "success"
        
        # Executar algumas falhas
        for _ in range(3):
            try:
                self.resilience_manager.execute_resilient(
                    func=failing_service,
                    circuit_breaker_name="test_metrics"
                )
            except Exception:
                pass
        
        # Executar alguns sucessos
        for _ in range(2):
            self.resilience_manager.execute_resilient(
                func=successful_service,
                circuit_breaker_name="test_metrics"
            )
        
        # Obter métricas
        metrics = self.resilience_manager.get_all_metrics()
        
        # Verificar que métricas foram coletadas
        assert "test_metrics" in metrics["circuit_breakers"]
        cb_metrics = metrics["circuit_breakers"]["test_metrics"]
        
        assert cb_metrics["total_requests"] >= 5
        assert cb_metrics["total_failures"] >= 3
        assert cb_metrics["total_successes"] >= 2
        assert "failure_rate" in cb_metrics
        assert "success_rate" in cb_metrics
    
    def test_failover_recovery_metrics(self):
        """Testa métricas de recuperação após failover"""
        cb = self.resilience_manager.circuit_breakers["test_metrics"]
        
        # Simular falhas até abrir circuit breaker
        def failing_service():
            raise Exception("Service failure")
        
        for _ in range(2):
            try:
                cb.call(failing_service)
            except Exception:
                pass
        
        # Verificar que circuit breaker abriu
        assert cb.state.value == "open"
        
        # Simular tempo de recuperação
        cb.last_failure_time = datetime.now() - timedelta(seconds=10)
        
        # Tentar recuperação
        def successful_service():
            return "success"
        
        result = cb.call(successful_service)
        assert result == "success"
        
        # Verificar métricas de recuperação
        metrics = cb.get_metrics()
        assert metrics["state"] == "half_open" or metrics["state"] == "closed"
        assert metrics["total_successes"] > 0


if __name__ == "__main__":
    pytest.main([__file__]) 