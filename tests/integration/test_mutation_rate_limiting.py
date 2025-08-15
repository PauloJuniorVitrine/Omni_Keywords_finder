"""
Testes de Mutação para Rate Limiting
Prompt: Testes de Integração - Fase 2
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27T15:45:00Z
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
from infrastructure.rate_limiting.token_bucket import TokenBucket
from infrastructure.rate_limiting.leaky_bucket import LeakyBucket
from infrastructure.rate_limiting.fixed_window import FixedWindow
from infrastructure.coleta.instagram_collector import InstagramCollector
from infrastructure.coleta.twitter_collector import TwitterCollector
from infrastructure.cache.redis_cache import RedisCache
from infrastructure.logging.structured_logger import StructuredLogger
from infrastructure.monitoring.metrics_collector import MetricsCollector
from infrastructure.resilience.circuit_breaker import CircuitBreaker

class TestMutationRateLimiting:
    """
    Testes de mutação específicos para rate limiting
    com validação de diferentes algoritmos e cenários.
    """
    
    @pytest.fixture(autouse=True)
    def setup_rate_limiting_environment(self):
        """Configuração do ambiente de rate limiting."""
        self.logger = StructuredLogger(
            module="test_mutation_rate_limiting",
            tracing_id="mutation_rl_001"
        )
        
        self.metrics = MetricsCollector()
        self.cache = RedisCache()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60
        )
        
        # Diferentes algoritmos de rate limiting
        self.token_bucket = TokenBucket(
            capacity=10,
            refill_rate=2
        )
        
        self.leaky_bucket = LeakyBucket(
            capacity=10,
            leak_rate=2
        )
        
        self.fixed_window = FixedWindow(
            max_requests=10,
            window_size=60
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
    async def test_mutation_token_bucket_algorithm(self):
        """
        Teste de mutação: Algoritmo Token Bucket.
        """
        # Arrange
        collector = InstagramCollector(
            api_key="test_key",
            cache=self.cache,
            logger=self.logger,
            circuit_breaker=self.circuit_breaker,
            rate_limiter=self.token_bucket
        )
        
        # Mutação: Sequência de requisições para testar token bucket
        with patch.object(collector, '_make_api_request') as mock_api:
            mock_api.return_value = {
                "status": "success",
                "data": self.test_data
            }
            
            # Act - Requisições consecutivas
            results = []
            for i in range(15):  # Mais que a capacidade (10)
                try:
                    result = await collector.collect_data("test_user")
                    results.append(result)
                except Exception as e:
                    results.append(None)
            
            # Assert - Validação de token bucket
            # Primeiras 10 devem funcionar (capacidade inicial)
            assert all(result is not None for result in results[:10])
            
            # Próximas 5 devem falhar (sem tokens)
            assert all(result is None for result in results[10:])
            
            # Validação de métricas
            rate_limit_metrics = self.metrics.get_metrics("rate_limiting")
            assert rate_limit_metrics["rate_limit_exceeded_count"] >= 5
    
    @mutation_testing
    @circuit_breaker_testing
    @pytest.mark.asyncio
    async def test_mutation_leaky_bucket_algorithm(self):
        """
        Teste de mutação: Algoritmo Leaky Bucket.
        """
        # Arrange
        collector = TwitterCollector(
            api_key="test_key",
            cache=self.cache,
            logger=self.logger,
            circuit_breaker=self.circuit_breaker,
            rate_limiter=self.leaky_bucket
        )
        
        # Mutação: Teste de vazamento do bucket
        with patch.object(collector, '_make_api_request') as mock_api:
            mock_api.return_value = {
                "status": "success",
                "data": self.test_data
            }
            
            # Act - Encher o bucket
            initial_results = []
            for i in range(10):
                result = await collector.collector.collect_data("test_user")
                initial_results.append(result)
            
            # Aguardar vazamento
            await asyncio.sleep(0.1)  # Simular tempo de vazamento
            
            # Tentar mais requisições
            leak_results = []
            for i in range(5):
                try:
                    result = await collector.collect_data("test_user")
                    leak_results.append(result)
                except Exception:
                    leak_results.append(None)
            
            # Assert - Validação de leaky bucket
            # Algumas requisições devem funcionar após vazamento
            assert any(result is not None for result in leak_results)
            
            # Validação de logs de vazamento
            leak_logs = self.logger.get_recent_logs(level="INFO")
            assert any("leak" in log["message"].lower() for log in leak_logs)
    
    @mutation_testing
    @circuit_breaker_testing
    @pytest.mark.asyncio
    async def test_mutation_fixed_window_algorithm(self):
        """
        Teste de mutação: Algoritmo Fixed Window.
        """
        # Arrange
        collector = InstagramCollector(
            api_key="test_key",
            cache=self.cache,
            logger=self.logger,
            circuit_breaker=self.circuit_breaker,
            rate_limiter=self.fixed_window
        )
        
        # Mutação: Teste de janela fixa
        with patch.object(collector, '_make_api_request') as mock_api:
            mock_api.return_value = {
                "status": "success",
                "data": self.test_data
            }
            
            # Act - Requisições dentro da janela
            window_results = []
            for i in range(12):  # Mais que o limite (10)
                try:
                    result = await collector.collect_data("test_user")
                    window_results.append(result)
                except Exception:
                    window_results.append(None)
            
            # Aguardar nova janela
            await asyncio.sleep(0.1)  # Simular nova janela
            
            # Tentar na nova janela
            new_window_results = []
            for i in range(5):
                try:
                    result = await collector.collect_data("test_user")
                    new_window_results.append(result)
                except Exception:
                    new_window_results.append(None)
            
            # Assert - Validação de fixed window
            # Primeiras 10 devem funcionar
            assert all(result is not None for result in window_results[:10])
            
            # Próximas 2 devem falhar
            assert all(result is None for result in window_results[10:])
            
            # Nova janela deve permitir requisições
            assert all(result is not None for result in new_window_results)
    
    @mutation_testing
    @circuit_breaker_testing
    @pytest.mark.asyncio
    async def test_mutation_rate_limiting_concurrent_requests(self):
        """
        Teste de mutação: Requisições concorrentes com rate limiting.
        """
        # Arrange
        collector = TwitterCollector(
            api_key="test_key",
            cache=self.cache,
            logger=self.logger,
            circuit_breaker=self.circuit_breaker,
            rate_limiter=self.token_bucket
        )
        
        # Mutação: Requisições simultâneas
        with patch.object(collector, '_make_api_request') as mock_api:
            mock_api.return_value = {
                "status": "success",
                "data": self.test_data
            }
            
            # Act - Requisições concorrentes
            async def make_request():
                try:
                    return await collector.collect_data("test_user")
                except Exception:
                    return None
            
            # Executar 15 requisições simultâneas
            tasks = [make_request() for _ in range(15)]
            results = await asyncio.gather(*tasks)
            
            # Assert - Validação de concorrência
            success_count = len([r for r in results if r is not None])
            failure_count = len([r for r in results if r is None])
            
            # Deve ter exatamente 10 sucessos (capacidade do bucket)
            assert success_count == 10
            assert failure_count == 5
            
            # Validação de métricas de concorrência
            concurrency_metrics = self.metrics.get_metrics("concurrency")
            assert concurrency_metrics["concurrent_requests"] == 15
    
    @mutation_testing
    @circuit_breaker_testing
    @pytest.mark.asyncio
    async def test_mutation_rate_limiting_different_users(self):
        """
        Teste de mutação: Rate limiting para diferentes usuários.
        """
        # Arrange
        collector = InstagramCollector(
            api_key="test_key",
            cache=self.cache,
            logger=self.logger,
            circuit_breaker=self.circuit_breaker,
            rate_limiter=self.token_bucket
        )
        
        # Mutação: Rate limiting por usuário
        with patch.object(collector, '_make_api_request') as mock_api:
            mock_api.return_value = {
                "status": "success",
                "data": self.test_data
            }
            
            # Act - Requisições para diferentes usuários
            users = ["user1", "user2", "user3"]
            results_by_user = {}
            
            for user in users:
                results = []
                for i in range(12):  # Mais que o limite
                    try:
                        result = await collector.collect_data(user)
                        results.append(result)
                    except Exception:
                        results.append(None)
                results_by_user[user] = results
            
            # Assert - Validação por usuário
            for user, results in results_by_user.items():
                # Cada usuário deve ter 10 sucessos e 2 falhas
                success_count = len([r for r in results if r is not None])
                failure_count = len([r for r in results if r is None])
                
                assert success_count == 10
                assert failure_count == 2
    
    @mutation_testing
    @circuit_breaker_testing
    @pytest.mark.asyncio
    async def test_mutation_rate_limiting_recovery_after_timeout(self):
        """
        Teste de mutação: Recuperação após timeout do rate limiting.
        """
        # Arrange
        collector = TwitterCollector(
            api_key="test_key",
            cache=self.cache,
            logger=self.logger,
            circuit_breaker=self.circuit_breaker,
            rate_limiter=self.token_bucket
        )
        
        # Mutação: Recuperação de tokens
        with patch.object(collector, '_make_api_request') as mock_api:
            mock_api.return_value = {
                "status": "success",
                "data": self.test_data
            }
            
            # Act - Esgotar tokens
            for i in range(10):
                await collector.collect_data("test_user")
            
            # Tentar mais requisições (devem falhar)
            failed_results = []
            for i in range(5):
                try:
                    result = await collector.collect_data("test_user")
                    failed_results.append(result)
                except Exception:
                    failed_results.append(None)
            
            # Aguardar recuperação de tokens
            await asyncio.sleep(0.1)  # Simular tempo de recuperação
            
            # Tentar novamente (algumas devem funcionar)
            recovery_results = []
            for i in range(5):
                try:
                    result = await collector.collect_data("test_user")
                    recovery_results.append(result)
                except Exception:
                    recovery_results.append(None)
            
            # Assert - Validação de recuperação
            assert all(result is None for result in failed_results)
            assert any(result is not None for result in recovery_results)
            
            # Validação de logs de recuperação
            recovery_logs = self.logger.get_recent_logs(level="INFO")
            assert any("recovery" in log["message"].lower() for log in recovery_logs)
    
    @mutation_testing
    @circuit_breaker_testing
    @pytest.mark.asyncio
    async def test_mutation_rate_limiting_burst_handling(self):
        """
        Teste de mutação: Tratamento de bursts de requisições.
        """
        # Arrange
        collector = InstagramCollector(
            api_key="test_key",
            cache=self.cache,
            logger=self.logger,
            circuit_breaker=self.circuit_breaker,
            rate_limiter=self.token_bucket
        )
        
        # Mutação: Burst de requisições
        with patch.object(collector, '_make_api_request') as mock_api:
            mock_api.return_value = {
                "status": "success",
                "data": self.test_data
            }
            
            # Act - Burst inicial
            burst_results = []
            for i in range(20):  # Burst grande
                try:
                    result = await collector.collect_data("test_user")
                    burst_results.append(result)
                except Exception:
                    burst_results.append(None)
            
            # Aguardar e tentar burst menor
            await asyncio.sleep(0.1)
            
            small_burst_results = []
            for i in range(5):
                try:
                    result = await collector.collect_data("test_user")
                    small_burst_results.append(result)
                except Exception:
                    small_burst_results.append(None)
            
            # Assert - Validação de burst
            # Primeiro burst deve ter 10 sucessos e 10 falhas
            burst_success = len([r for r in burst_results if r is not None])
            burst_failure = len([r for r in burst_results if r is None])
            
            assert burst_success == 10
            assert burst_failure == 10
            
            # Segundo burst deve ter alguns sucessos
            small_burst_success = len([r for r in small_burst_results if r is not None])
            assert small_burst_success > 0
    
    @mutation_testing
    @circuit_breaker_testing
    @pytest.mark.asyncio
    async def test_mutation_rate_limiting_error_handling(self):
        """
        Teste de mutação: Tratamento de erros com rate limiting.
        """
        # Arrange
        collector = TwitterCollector(
            api_key="test_key",
            cache=self.cache,
            logger=self.logger,
            circuit_breaker=self.circuit_breaker,
            rate_limiter=self.token_bucket
        )
        
        # Mutação: Erros que não devem consumir tokens
        with patch.object(collector, '_make_api_request') as mock_api:
            # Sequência: Sucesso, Erro, Sucesso, Erro
            mock_api.side_effect = [
                {"status": "success", "data": self.test_data},
                Exception("API Error"),
                {"status": "success", "data": self.test_data},
                Exception("API Error")
            ]
            
            # Act - Executar sequência
            results = []
            for i in range(4):
                try:
                    result = await collector.collect_data("test_user")
                    results.append(result)
                except Exception:
                    results.append(None)
            
            # Assert - Validação de erro
            # Sucessos devem funcionar
            assert results[0] is not None
            assert results[2] is not None
            
            # Erros devem falhar mas não consumir tokens
            assert results[1] is None
            assert results[3] is None
            
            # Verificar se ainda há tokens disponíveis
            remaining_tokens = self.token_bucket.get_remaining_tokens()
            assert remaining_tokens > 0
    
    @mutation_testing
    @circuit_breaker_testing
    @pytest.mark.asyncio
    async def test_mutation_rate_limiting_metrics_tracking(self):
        """
        Teste de mutação: Rastreamento de métricas de rate limiting.
        """
        # Arrange
        collector = InstagramCollector(
            api_key="test_key",
            cache=self.cache,
            logger=self.logger,
            circuit_breaker=self.circuit_breaker,
            rate_limiter=self.token_bucket
        )
        
        # Mutação: Sequência para gerar métricas
        with patch.object(collector, '_make_api_request') as mock_api:
            mock_api.return_value = {
                "status": "success",
                "data": self.test_data
            }
            
            # Act - Requisições para gerar métricas
            for i in range(15):  # Mais que o limite
                try:
                    await collector.collect_data("test_user")
                except Exception:
                    pass
            
            # Assert - Validação de métricas
            rate_limit_metrics = self.metrics.get_metrics("rate_limiting")
            
            assert rate_limit_metrics["total_requests"] >= 15
            assert rate_limit_metrics["successful_requests"] >= 10
            assert rate_limit_metrics["rate_limit_exceeded_count"] >= 5
            assert rate_limit_metrics["average_response_time"] > 0
            
            # Validação de logs de métricas
            metric_logs = self.logger.get_recent_logs(level="INFO")
            assert any("rate_limit" in log["message"].lower() for log in metric_logs)
    
    @mutation_testing
    @circuit_breaker_testing
    @pytest.mark.asyncio
    async def test_mutation_rate_limiting_performance_impact(self):
        """
        Teste de mutação: Impacto de performance do rate limiting.
        """
        # Arrange
        collector = TwitterCollector(
            api_key="test_key",
            cache=self.cache,
            logger=self.logger,
            circuit_breaker=self.circuit_breaker,
            rate_limiter=self.token_bucket
        )
        
        # Mutação: Medição de performance
        with patch.object(collector, '_make_api_request') as mock_api:
            mock_api.return_value = {
                "status": "success",
                "data": self.test_data
            }
            
            # Act - Medir performance de sucessos
            success_times = []
            for i in range(5):
                start_time = time.time()
                result = await collector.collect_data("test_user")
                success_times.append(time.time() - start_time)
            
            # Medir performance de falhas por rate limiting
            failure_times = []
            for i in range(5):
                start_time = time.time()
                try:
                    result = await collector.collect_data("test_user")
                except Exception:
                    pass
                failure_times.append(time.time() - start_time)
            
            # Assert - Validação de performance
            # Sucessos devem ser normais
            assert all(t < 5.0 for t in success_times)
            
            # Falhas por rate limiting devem ser rápidas
            assert all(t < 1.0 for t in failure_times)
            
            # Falhas devem ser mais rápidas que sucessos
            avg_success_time = sum(success_times) / len(success_times)
            avg_failure_time = sum(failure_times) / len(failure_times)
            
            assert avg_failure_time < avg_success_time 