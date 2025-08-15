"""
Testes de Mutação para Circuit Breakers
Prompt: Testes de Integração - Fase 2
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27T15:40:00Z
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List
import json
import time
from datetime import datetime, timedelta

# Importações dos decorators
from .decorators import (
    risk_score_calculation,
    semantic_validation,
    real_data_validation,
    production_scenario,
    side_effects_monitoring,
    performance_monitoring,
    mutation_testing,
    circuit_breaker_testing
)

# Importações do sistema real
from infrastructure.resilience.circuit_breaker import CircuitBreaker
from infrastructure.coleta.instagram_collector import InstagramCollector
from infrastructure.coleta.twitter_collector import TwitterCollector
from infrastructure.cache.redis_cache import RedisCache
from infrastructure.logging.structured_logger import StructuredLogger
from infrastructure.monitoring.metrics_collector import MetricsCollector
from infrastructure.rate_limiting.token_bucket import TokenBucket

class TestMutationCircuitBreaker:
    """
    Testes de mutação específicos para circuit breakers
    com validação de estados e transições.
    """
    
    @pytest.fixture(autouse=True)
    def setup_circuit_breaker_environment(self):
        """Configuração do ambiente de circuit breaker."""
        self.logger = StructuredLogger(
            module="test_mutation_circuit_breaker",
            tracing_id="mutation_cb_001"
        )
        
        self.metrics = MetricsCollector()
        self.cache = RedisCache()
        
        # Circuit breakers com diferentes configurações
        self.circuit_breaker_strict = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=30
        )
        
        self.circuit_breaker_lenient = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=120
        )
        
        self.circuit_breaker_fast = CircuitBreaker(
            failure_threshold=1,
            recovery_timeout=10
        )
        
        self.rate_limiter = TokenBucket(
            capacity=100,
            refill_rate=10
        )
        
        # Dados reais para teste
        self.test_data = {
            "username": "test_user",
            "posts": [
                {
                    "id": "post_1",
                    "content": "Test content",
                    "engagement": 100
                }
            ],
            "metrics": {
                "followers": 1000,
                "engagement_rate": 0.05
            }
        }
        
        yield
        
        # Cleanup
        asyncio.run(self.cache.clear())
    
    @mutation_testing
    @circuit_breaker_testing
    @pytest.mark.asyncio
    async def test_mutation_circuit_breaker_state_transitions(self):
        """
        Teste de mutação: Transições de estado do circuit breaker.
        """
        # Arrange
        collector = InstagramCollector(
            api_key="test_key",
            cache=self.cache,
            logger=self.logger,
            circuit_breaker=self.circuit_breaker_strict,
            rate_limiter=self.rate_limiter
        )
        
        # Mutação: Sequência de falhas e sucessos
        with patch.object(collector, '_make_api_request') as mock_api:
            # Sequência: Falha, Falha, Sucesso, Falha, Sucesso
            mock_api.side_effect = [
                Exception("API Error 1"),
                Exception("API Error 2"),
                {"status": "success", "data": self.test_data},
                Exception("API Error 3"),
                {"status": "success", "data": self.test_data}
            ]
            
            # Act - Executar sequência
            results = []
            circuit_states = []
            
            for i in range(5):
                try:
                    result = await collector.collect_data("test_user")
                    results.append(result)
                except Exception:
                    results.append(None)
                
                # Capturar estado do circuit breaker
                circuit_states.append(self.circuit_breaker_strict.get_status()["state"])
            
            # Assert - Validação de transições
            # Estados esperados: CLOSED -> CLOSED -> OPEN -> OPEN -> HALF_OPEN
            assert circuit_states[0] == "CLOSED"  # Inicial
            assert circuit_states[1] == "CLOSED"  # Após 1 falha
            assert circuit_states[2] == "OPEN"    # Após 2 falhas
            assert circuit_states[3] == "OPEN"    # Ainda aberto
            assert circuit_states[4] == "HALF_OPEN"  # Tentativa de recuperação
            
            # Validação de resultados
            assert results[0] is None  # Falha
            assert results[1] is None  # Falha
            assert results[2] is None  # Circuit breaker aberto
            assert results[3] is None  # Circuit breaker aberto
            assert results[4] is not None  # Sucesso na recuperação
    
    @mutation_testing
    @circuit_breaker_testing
    @pytest.mark.asyncio
    async def test_mutation_circuit_breaker_failure_threshold_variations(self):
        """
        Teste de mutação: Diferentes thresholds de falha.
        """
        # Arrange
        collectors = []
        
        # Criar collectors com diferentes thresholds
        for cb in [self.circuit_breaker_strict, self.circuit_breaker_lenient, self.circuit_breaker_fast]:
            collector = TwitterCollector(
                api_key="test_key",
                cache=self.cache,
                logger=self.logger,
                circuit_breaker=cb,
                rate_limiter=self.rate_limiter
            )
            collectors.append(collector)
        
        # Mutação: Sequência de falhas
        with patch.object(collectors[0], '_make_api_request') as mock_api:
            mock_api.side_effect = [Exception("API Error")] * 6
            
            # Act - Testar diferentes thresholds
            results_by_threshold = {}
            
            for i, collector in enumerate(collectors):
                results = []
                for j in range(6):
                    try:
                        result = await collector.collect_data("test_user")
                        results.append(result)
                    except Exception:
                        results.append(None)
                
                results_by_threshold[f"threshold_{i+1}"] = results
            
            # Assert - Validação de thresholds
            # Strict (threshold=2): Deve abrir após 2 falhas
            strict_results = results_by_threshold["threshold_1"]
            assert strict_results[0] is None  # 1ª falha
            assert strict_results[1] is None  # 2ª falha
            assert strict_results[2] is None  # Circuit breaker aberto
            
            # Lenient (threshold=5): Deve abrir após 5 falhas
            lenient_results = results_by_threshold["threshold_2"]
            assert lenient_results[4] is None  # 5ª falha
            assert lenient_results[5] is None  # Circuit breaker aberto
            
            # Fast (threshold=1): Deve abrir após 1 falha
            fast_results = results_by_threshold["threshold_3"]
            assert fast_results[0] is None  # 1ª falha
            assert fast_results[1] is None  # Circuit breaker aberto
    
    @mutation_testing
    @circuit_breaker_testing
    @pytest.mark.asyncio
    async def test_mutation_circuit_breaker_recovery_timeout(self):
        """
        Teste de mutação: Timeout de recuperação.
        """
        # Arrange
        collector = InstagramCollector(
            api_key="test_key",
            cache=self.cache,
            logger=self.logger,
            circuit_breaker=self.circuit_breaker_fast,  # Timeout de 10s
            rate_limiter=self.rate_limiter
        )
        
        # Mutação: Falha seguida de tentativa prematura de recuperação
        with patch.object(collector, '_make_api_request') as mock_api:
            mock_api.side_effect = [
                Exception("API Error"),  # Falha inicial
                {"status": "success", "data": self.test_data}  # Sucesso posterior
            ]
            
            # Act - Falha para abrir circuit breaker
            try:
                await collector.collect_data("test_user")
            except Exception:
                pass
            
            # Verificar se está aberto
            circuit_status_before = self.circuit_breaker_fast.get_status()
            assert circuit_status_before["state"] == "OPEN"
            
            # Tentar imediatamente (deve falhar rapidamente)
            start_time = time.time()
            try:
                result = await collector.collect_data("test_user")
                execution_time = time.time() - start_time
            except Exception:
                execution_time = time.time() - start_time
                result = None
            
            # Assert - Validação de timeout
            assert result is None
            assert execution_time < 1.0  # Falha rápida
            
            # Aguardar tempo de recuperação
            await asyncio.sleep(0.1)  # Simular tempo de recuperação
            
            # Tentar novamente - deve estar em HALF_OPEN
            circuit_status_after = self.circuit_breaker_fast.get_status()
            assert circuit_status_after["state"] == "HALF_OPEN"
    
    @mutation_testing
    @circuit_breaker_testing
    @pytest.mark.asyncio
    async def test_mutation_circuit_breaker_half_open_state(self):
        """
        Teste de mutação: Estado HALF_OPEN do circuit breaker.
        """
        # Arrange
        collector = TwitterCollector(
            api_key="test_key",
            cache=self.cache,
            logger=self.logger,
            circuit_breaker=self.circuit_breaker_strict,
            rate_limiter=self.rate_limiter
        )
        
        # Mutação: Transição para HALF_OPEN
        with patch.object(collector, '_make_api_request') as mock_api:
            # Sequência: Falhas -> Timeout -> Sucesso -> Falha
            mock_api.side_effect = [
                Exception("API Error"),  # 1ª falha
                Exception("API Error"),  # 2ª falha (abre circuit breaker)
                {"status": "success", "data": self.test_data},  # Sucesso em HALF_OPEN
                Exception("API Error")   # Falha em HALF_OPEN
            ]
            
            # Act - Falhas para abrir circuit breaker
            for i in range(2):
                try:
                    await collector.collect_data("test_user")
                except Exception:
                    pass
            
            # Aguardar tempo de recuperação
            await asyncio.sleep(0.1)
            
            # Tentar sucesso em HALF_OPEN
            result_success = await collector.collect_data("test_user")
            
            # Tentar falha em HALF_OPEN
            try:
                result_failure = await collector.collect_data("test_user")
            except Exception:
                result_failure = None
            
            # Assert - Validação de HALF_OPEN
            assert result_success is not None  # Sucesso deve funcionar
            assert result_failure is None      # Falha deve reabrir circuit breaker
            
            # Verificar estado final
            circuit_status = self.circuit_breaker_strict.get_status()
            assert circuit_status["state"] == "OPEN"  # Deve reabrir após falha
    
    @mutation_testing
    @circuit_breaker_testing
    @pytest.mark.asyncio
    async def test_mutation_circuit_breaker_concurrent_failures(self):
        """
        Teste de mutação: Falhas concorrentes no circuit breaker.
        """
        # Arrange
        collector = InstagramCollector(
            api_key="test_key",
            cache=self.cache,
            logger=self.logger,
            circuit_breaker=self.circuit_breaker_strict,
            rate_limiter=self.rate_limiter
        )
        
        # Mutação: Falhas simultâneas
        with patch.object(collector, '_make_api_request') as mock_api:
            mock_api.side_effect = Exception("API Error")
            
            # Act - Requisições concorrentes
            async def make_request():
                try:
                    return await collector.collect_data("test_user")
                except Exception:
                    return None
            
            # Executar 5 requisições simultâneas
            tasks = [make_request() for _ in range(5)]
            results = await asyncio.gather(*tasks)
            
            # Assert - Validação de falhas concorrentes
            assert all(result is None for result in results)
            
            # Verificar se circuit breaker abriu
            circuit_status = self.circuit_breaker_strict.get_status()
            assert circuit_status["state"] == "OPEN"
            assert circuit_status["failure_count"] >= 2  # Pelo menos 2 falhas
    
    @mutation_testing
    @circuit_breaker_testing
    @pytest.mark.asyncio
    async def test_mutation_circuit_breaker_metrics_tracking(self):
        """
        Teste de mutação: Rastreamento de métricas do circuit breaker.
        """
        # Arrange
        collector = TwitterCollector(
            api_key="test_key",
            cache=self.cache,
            logger=self.logger,
            circuit_breaker=self.circuit_breaker_strict,
            rate_limiter=self.rate_limiter
        )
        
        # Mutação: Sequência de operações para gerar métricas
        with patch.object(collector, '_make_api_request') as mock_api:
            # Sequência: Sucesso, Falha, Falha, Sucesso
            mock_api.side_effect = [
                {"status": "success", "data": self.test_data},
                Exception("API Error"),
                Exception("API Error"),
                {"status": "success", "data": self.test_data}
            ]
            
            # Act - Executar sequência
            results = []
            for i in range(4):
                try:
                    result = await collector.collect_data("test_user")
                    results.append(result)
                except Exception:
                    results.append(None)
            
            # Assert - Validação de métricas
            circuit_metrics = self.metrics.get_metrics("circuit_breaker")
            
            assert circuit_metrics["total_requests"] >= 4
            assert circuit_metrics["success_count"] >= 2
            assert circuit_metrics["failure_count"] >= 2
            assert circuit_metrics["circuit_open_count"] > 0
            
            # Validação de logs de métricas
            metric_logs = self.logger.get_recent_logs(level="INFO")
            assert any("circuit_breaker" in log["message"].lower() for log in metric_logs)
    
    @mutation_testing
    @circuit_breaker_testing
    @pytest.mark.asyncio
    async def test_mutation_circuit_breaker_state_persistence(self):
        """
        Teste de mutação: Persistência de estado do circuit breaker.
        """
        # Arrange
        collector = InstagramCollector(
            api_key="test_key",
            cache=self.cache,
            logger=self.logger,
            circuit_breaker=self.circuit_breaker_strict,
            rate_limiter=self.rate_limiter
        )
        
        # Mutação: Falhas para abrir circuit breaker
        with patch.object(collector, '_make_api_request') as mock_api:
            mock_api.side_effect = [
                Exception("API Error"),
                Exception("API Error"),
                {"status": "success", "data": self.test_data}
            ]
            
            # Act - Falhas para abrir circuit breaker
            for i in range(2):
                try:
                    await collector.collect_data("test_user")
                except Exception:
                    pass
            
            # Verificar estado
            circuit_status_before = self.circuit_breaker_strict.get_status()
            assert circuit_status_before["state"] == "OPEN"
            
            # Simular reinicialização (novo collector com mesmo circuit breaker)
            collector2 = InstagramCollector(
                api_key="test_key",
                cache=self.cache,
                logger=self.logger,
                circuit_breaker=self.circuit_breaker_strict,  # Mesmo circuit breaker
                rate_limiter=self.rate_limiter
            )
            
            # Tentar com novo collector
            try:
                result = await collector2.collect_data("test_user")
            except Exception:
                result = None
            
            # Assert - Validação de persistência
            assert result is None  # Deve falhar rapidamente
            
            circuit_status_after = self.circuit_breaker_strict.get_status()
            assert circuit_status_after["state"] == "OPEN"  # Estado deve persistir
    
    @mutation_testing
    @circuit_breaker_testing
    @pytest.mark.asyncio
    async def test_mutation_circuit_breaker_error_classification(self):
        """
        Teste de mutação: Classificação de erros no circuit breaker.
        """
        # Arrange
        collector = TwitterCollector(
            api_key="test_key",
            cache=self.cache,
            logger=self.logger,
            circuit_breaker=self.circuit_breaker_strict,
            rate_limiter=self.rate_limiter
        )
        
        # Mutação: Diferentes tipos de erro
        with patch.object(collector, '_make_api_request') as mock_api:
            # Erros que devem contar para circuit breaker
            circuit_breaker_errors = [
                Exception("Connection timeout"),
                Exception("Server error 500"),
                Exception("Rate limit exceeded"),
                Exception("Service unavailable")
            ]
            
            # Erros que NÃO devem contar para circuit breaker
            non_circuit_breaker_errors = [
                Exception("Invalid API key"),  # Erro de configuração
                Exception("User not found"),   # Erro de negócio
                Exception("Invalid parameters") # Erro de validação
            ]
            
            mock_api.side_effect = circuit_breaker_errors + non_circuit_breaker_errors
            
            # Act - Testar erros que contam para circuit breaker
            circuit_breaker_results = []
            for i in range(len(circuit_breaker_errors)):
                try:
                    result = await collector.collect_data("test_user")
                    circuit_breaker_results.append(result)
                except Exception:
                    circuit_breaker_results.append(None)
            
            # Testar erros que NÃO contam para circuit breaker
            non_circuit_breaker_results = []
            for i in range(len(non_circuit_breaker_errors)):
                try:
                    result = await collector.collect_data("test_user")
                    non_circuit_breaker_results.append(result)
                except Exception:
                    non_circuit_breaker_results.append(None)
            
            # Assert - Validação de classificação
            # Circuit breaker deve abrir após erros de infraestrutura
            circuit_status = self.circuit_breaker_strict.get_status()
            assert circuit_status["state"] == "OPEN"
            assert circuit_status["failure_count"] >= len(circuit_breaker_errors)
            
            # Todos os erros devem resultar em falha
            assert all(result is None for result in circuit_breaker_results)
            assert all(result is None for result in non_circuit_breaker_results)
    
    @mutation_testing
    @circuit_breaker_testing
    @pytest.mark.asyncio
    async def test_mutation_circuit_breaker_performance_impact(self):
        """
        Teste de mutação: Impacto de performance do circuit breaker.
        """
        # Arrange
        collector = InstagramCollector(
            api_key="test_key",
            cache=self.cache,
            logger=self.logger,
            circuit_breaker=self.circuit_breaker_strict,
            rate_limiter=self.rate_limiter
        )
        
        # Mutação: Medição de performance
        with patch.object(collector, '_make_api_request') as mock_api:
            mock_api.side_effect = [
                Exception("API Error"),
                Exception("API Error"),
                {"status": "success", "data": self.test_data}
            ]
            
            # Act - Medir performance de falhas
            failure_times = []
            for i in range(2):
                start_time = time.time()
                try:
                    await collector.collect_data("test_user")
                except Exception:
                    pass
                failure_times.append(time.time() - start_time)
            
            # Medir performance com circuit breaker aberto
            start_time = time.time()
            try:
                await collector.collect_data("test_user")
            except Exception:
                pass
            open_circuit_time = time.time() - start_time
            
            # Medir performance de sucesso
            start_time = time.time()
            result = await collector.collect_data("test_user")
            success_time = time.time() - start_time
            
            # Assert - Validação de performance
            # Falhas devem ser rápidas
            assert all(t < 5.0 for t in failure_times)
            
            # Circuit breaker aberto deve ser muito rápido
            assert open_circuit_time < 0.1
            
            # Sucesso deve ser normal
            assert success_time < 5.0
            assert result is not None
            
            # Performance deve melhorar com circuit breaker
            assert open_circuit_time < min(failure_times) 