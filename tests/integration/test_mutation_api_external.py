"""
Testes de Mutação para APIs Externas
Prompt: Testes de Integração - Fase 2
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27T15:35:00Z
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
from infrastructure.coleta.instagram_collector import InstagramCollector
from infrastructure.coleta.twitter_collector import TwitterCollector
from infrastructure.coleta.linkedin_collector import LinkedInCollector
from infrastructure.cache.redis_cache import RedisCache
from infrastructure.logging.structured_logger import StructuredLogger
from infrastructure.monitoring.metrics_collector import MetricsCollector
from infrastructure.resilience.circuit_breaker import CircuitBreaker
from infrastructure.rate_limiting.token_bucket import TokenBucket

# Configuração de mutação
from .mutation_config import MUTATION_CONFIG

class TestMutationAPIExternal:
    """
    Testes de mutação específicos para APIs externas
    com validação de circuit breakers e rate limiting.
    """
    
    @pytest.fixture(autouse=True)
    def setup_mutation_environment(self):
        """Configuração do ambiente de mutação."""
        self.logger = StructuredLogger(
            module="test_mutation_api_external",
            tracing_id="mutation_ext_001"
        )
        
        self.metrics = MetricsCollector()
        self.cache = RedisCache()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60
        )
        self.rate_limiter = TokenBucket(
            capacity=100,
            refill_rate=10
        )
        
        # Dados reais para mutação
        self.base_api_response = {
            "status": "success",
            "data": {
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
            },
            "rate_limit": {
                "remaining": 950,
                "reset": int(time.time()) + 3600
            }
        }
        
        yield
        
        # Cleanup
        asyncio.run(self.cache.clear())
    
    @mutation_testing
    @circuit_breaker_testing
    @pytest.mark.asyncio
    async def test_mutation_api_timeout_handling(self):
        """
        Teste de mutação: Timeout em APIs externas.
        """
        # Arrange
        collector = InstagramCollector(
            api_key="test_key",
            cache=self.cache,
            logger=self.logger,
            circuit_breaker=self.circuit_breaker,
            rate_limiter=self.rate_limiter
        )
        
        # Mutação: Timeout na API
        with patch.object(collector, '_make_api_request') as mock_api:
            mock_api.side_effect = asyncio.TimeoutError("API timeout")
            
            # Act
            start_time = time.time()
            try:
                result = await collector.collect_data("test_user")
                execution_time = time.time() - start_time
            except Exception as e:
                execution_time = time.time() - start_time
                result = None
            
            # Assert - Validação de timeout
            assert result is None
            assert execution_time < 30.0  # Timeout deve ser < 30s
            
            # Validação de circuit breaker
            circuit_status = self.circuit_breaker.get_status()
            assert circuit_status["failure_count"] > 0
            
            # Validação de logs de timeout
            timeout_logs = self.logger.get_recent_logs(level="ERROR")
            assert any("timeout" in log["message"].lower() for log in timeout_logs)
    
    @mutation_testing
    @circuit_breaker_testing
    @pytest.mark.asyncio
    async def test_mutation_api_rate_limit_exceeded(self):
        """
        Teste de mutação: Rate limit excedido.
        """
        # Arrange
        collector = TwitterCollector(
            api_key="test_key",
            cache=self.cache,
            logger=self.logger,
            circuit_breaker=self.circuit_breaker,
            rate_limiter=self.rate_limiter
        )
        
        # Mutação: Rate limit excedido
        with patch.object(collector, '_make_api_request') as mock_api:
            mock_api.side_effect = Exception("Rate limit exceeded (429)")
            
            # Act - Múltiplas tentativas
            results = []
            for i in range(5):
                try:
                    result = await collector.collect_data("test_user")
                    results.append(result)
                except Exception as e:
                    results.append(None)
            
            # Assert - Validação de rate limiting
            assert all(result is None for result in results)
            
            # Validação de circuit breaker
            circuit_status = self.circuit_breaker.get_status()
            assert circuit_status["state"] == "OPEN"
            
            # Validação de métricas de rate limiting
            rate_limit_metrics = self.metrics.get_metrics("rate_limiting")
            assert rate_limit_metrics["rate_limit_exceeded_count"] > 0
    
    @mutation_testing
    @circuit_breaker_testing
    @pytest.mark.asyncio
    async def test_mutation_api_invalid_response_format(self):
        """
        Teste de mutação: Formato de resposta inválido.
        """
        # Arrange
        collector = LinkedInCollector(
            api_key="test_key",
            cache=self.cache,
            logger=self.logger,
            circuit_breaker=self.circuit_breaker,
            rate_limiter=self.rate_limiter
        )
        
        # Mutação: Resposta malformada
        invalid_responses = [
            {"invalid": "format"},
            {"status": "success", "data": None},
            {"status": "error", "data": "invalid_data_type"},
            {"status": "success", "data": {"incomplete": "data"}},
            None
        ]
        
        with patch.object(collector, '_make_api_request') as mock_api:
            mock_api.side_effect = invalid_responses
            
            # Act - Teste com diferentes formatos inválidos
            results = []
            for i in range(len(invalid_responses)):
                try:
                    result = await collector.collect_data("test_user")
                    results.append(result)
                except Exception as e:
                    results.append(None)
            
            # Assert - Validação de tratamento de formato inválido
            assert all(result is None for result in results)
            
            # Validação de logs de formato inválido
            format_logs = self.logger.get_recent_logs(level="ERROR")
            assert any("invalid format" in log["message"].lower() for log in format_logs)
    
    @mutation_testing
    @circuit_breaker_testing
    @pytest.mark.asyncio
    async def test_mutation_api_authentication_failure(self):
        """
        Teste de mutação: Falha de autenticação.
        """
        # Arrange
        collector = InstagramCollector(
            api_key="invalid_key",
            cache=self.cache,
            logger=self.logger,
            circuit_breaker=self.circuit_breaker,
            rate_limiter=self.rate_limiter
        )
        
        # Mutação: Falhas de autenticação
        auth_errors = [
            Exception("Invalid API key (401)"),
            Exception("Unauthorized access (403)"),
            Exception("Token expired (401)"),
            Exception("Invalid credentials (401)")
        ]
        
        with patch.object(collector, '_make_api_request') as mock_api:
            mock_api.side_effect = auth_errors
            
            # Act - Teste de diferentes falhas de auth
            results = []
            for i in range(len(auth_errors)):
                try:
                    result = await collector.collect_data("test_user")
                    results.append(result)
                except Exception as e:
                    results.append(None)
            
            # Assert - Validação de falhas de autenticação
            assert all(result is None for result in results)
            
            # Validação de circuit breaker
            circuit_status = self.circuit_breaker.get_status()
            assert circuit_status["state"] == "OPEN"
            
            # Validação de logs de auth
            auth_logs = self.logger.get_recent_logs(level="ERROR")
            assert any("401" in log["message"] or "403" in log["message"] for log in auth_logs)
    
    @mutation_testing
    @circuit_breaker_testing
    @pytest.mark.asyncio
    async def test_mutation_api_server_errors(self):
        """
        Teste de mutação: Erros de servidor (5xx).
        """
        # Arrange
        collector = TwitterCollector(
            api_key="test_key",
            cache=self.cache,
            logger=self.logger,
            circuit_breaker=self.circuit_breaker,
            rate_limiter=self.rate_limiter
        )
        
        # Mutação: Erros de servidor
        server_errors = [
            Exception("Internal server error (500)"),
            Exception("Service unavailable (503)"),
            Exception("Gateway timeout (504)"),
            Exception("Bad gateway (502)")
        ]
        
        with patch.object(collector, '_make_api_request') as mock_api:
            mock_api.side_effect = server_errors
            
            # Act - Teste de diferentes erros de servidor
            results = []
            for i in range(len(server_errors)):
                try:
                    result = await collector.collect_data("test_user")
                    results.append(result)
                except Exception as e:
                    results.append(None)
            
            # Assert - Validação de erros de servidor
            assert all(result is None for result in results)
            
            # Validação de circuit breaker
            circuit_status = self.circuit_breaker.get_status()
            assert circuit_status["state"] == "OPEN"
            
            # Validação de logs de servidor
            server_logs = self.logger.get_recent_logs(level="ERROR")
            assert any("500" in log["message"] or "503" in log["message"] for log in server_logs)
    
    @mutation_testing
    @circuit_breaker_testing
    @pytest.mark.asyncio
    async def test_mutation_api_partial_data_response(self):
        """
        Teste de mutação: Resposta com dados parciais.
        """
        # Arrange
        collector = LinkedInCollector(
            api_key="test_key",
            cache=self.cache,
            logger=self.logger,
            circuit_breaker=self.circuit_breaker,
            rate_limiter=self.rate_limiter
        )
        
        # Mutação: Dados parciais
        partial_responses = [
            {
                "status": "partial",
                "data": {
                    "username": "test_user",
                    "posts": []  # Posts vazios
                }
            },
            {
                "status": "success",
                "data": {
                    "username": "test_user",
                    "posts": None  # Posts nulos
                }
            },
            {
                "status": "success",
                "data": {
                    "username": "test_user",
                    "metrics": {}  # Métricas vazias
                }
            }
        ]
        
        with patch.object(collector, '_make_api_request') as mock_api:
            mock_api.side_effect = partial_responses
            
            # Act - Teste com dados parciais
            results = []
            for i in range(len(partial_responses)):
                try:
                    result = await collector.collect_data("test_user")
                    results.append(result)
                except Exception as e:
                    results.append(None)
            
            # Assert - Validação de dados parciais
            # Alguns podem ser válidos, outros não
            assert len([r for r in results if r is not None]) < len(results)
            
            # Validação de logs de dados parciais
            partial_logs = self.logger.get_recent_logs(level="WARNING")
            assert any("partial" in log["message"].lower() for log in partial_logs)
    
    @mutation_testing
    @circuit_breaker_testing
    @pytest.mark.asyncio
    async def test_mutation_api_circuit_breaker_recovery(self):
        """
        Teste de mutação: Recuperação do circuit breaker.
        """
        # Arrange
        collector = InstagramCollector(
            api_key="test_key",
            cache=self.cache,
            logger=self.logger,
            circuit_breaker=self.circuit_breaker,
            rate_limiter=self.rate_limiter
        )
        
        # Mutação: Falhas seguidas de sucesso
        with patch.object(collector, '_make_api_request') as mock_api:
            # Primeiro: 3 falhas para abrir o circuit breaker
            mock_api.side_effect = [
                Exception("API Error"),
                Exception("API Error"),
                Exception("API Error"),
                # Depois: Sucesso para testar recuperação
                {"status": "success", "data": self.base_api_response["data"]}
            ]
            
            # Act - Falhas para abrir circuit breaker
            for i in range(3):
                try:
                    await collector.collect_data("test_user")
                except Exception:
                    pass
            
            # Verificar se circuit breaker está aberto
            circuit_status_before = self.circuit_breaker.get_status()
            assert circuit_status_before["state"] == "OPEN"
            
            # Aguardar tempo de recuperação
            await asyncio.sleep(0.1)  # Simular tempo de recuperação
            
            # Tentar novamente - deve falhar rapidamente
            start_time = time.time()
            try:
                result = await collector.collect_data("test_user")
                execution_time = time.time() - start_time
            except Exception:
                execution_time = time.time() - start_time
                result = None
            
            # Assert - Validação de circuit breaker
            assert result is None
            assert execution_time < 1.0  # Falha rápida
            
            # Verificar estado final
            circuit_status_after = self.circuit_breaker.get_status()
            assert circuit_status_after["state"] == "OPEN"
    
    @mutation_testing
    @circuit_breaker_testing
    @pytest.mark.asyncio
    async def test_mutation_api_cache_corruption(self):
        """
        Teste de mutação: Corrupção de cache.
        """
        # Arrange
        collector = TwitterCollector(
            api_key="test_key",
            cache=self.cache,
            logger=self.logger,
            circuit_breaker=self.circuit_breaker,
            rate_limiter=self.rate_limiter
        )
        
        # Mutação: Dados corrompidos no cache
        corrupted_cache_data = {
            "username": "test_user",
            "posts": "invalid_posts_data",  # String em vez de lista
            "metrics": None  # Métricas nulas
        }
        
        # Inserir dados corrompidos no cache
        await self.cache.set("twitter:test_user", corrupted_cache_data, ttl=300)
        
        with patch.object(collector, '_make_api_request') as mock_api:
            mock_api.return_value = {
                "status": "success",
                "data": self.base_api_response["data"]
            }
            
            # Act - Tentar coletar dados (deve falhar no cache)
            try:
                result = await collector.collect_data("test_user")
            except Exception as e:
                result = None
            
            # Assert - Validação de cache corrompido
            # O sistema deve detectar corrupção e usar API
            assert result is not None
            
            # Validação de logs de corrupção
            corruption_logs = self.logger.get_recent_logs(level="WARNING")
            assert any("cache" in log["message"].lower() for log in corruption_logs)
    
    @mutation_testing
    @circuit_breaker_testing
    @pytest.mark.asyncio
    async def test_mutation_api_concurrent_requests(self):
        """
        Teste de mutação: Requisições concorrentes.
        """
        # Arrange
        collector = LinkedInCollector(
            api_key="test_key",
            cache=self.cache,
            logger=self.logger,
            circuit_breaker=self.circuit_breaker,
            rate_limiter=self.rate_limiter
        )
        
        # Mutação: Múltiplas requisições simultâneas
        with patch.object(collector, '_make_api_request') as mock_api:
            mock_api.return_value = {
                "status": "success",
                "data": self.base_api_response["data"]
            }
            
            # Act - Requisições concorrentes
            async def make_request(user_id):
                return await collector.collect_data(f"user_{user_id}")
            
            # Executar 10 requisições simultâneas
            tasks = [make_request(i) for i in range(10)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Assert - Validação de concorrência
            # Algumas devem ser rate limited
            success_count = len([r for r in results if r is not None])
            assert success_count > 0  # Pelo menos algumas devem funcionar
            assert success_count < 10  # Nem todas devem funcionar devido ao rate limiting
            
            # Validação de métricas de concorrência
            concurrency_metrics = self.metrics.get_metrics("concurrency")
            assert concurrency_metrics["concurrent_requests"] > 0
    
    @mutation_testing
    @circuit_breaker_testing
    @pytest.mark.asyncio
    async def test_mutation_api_data_consistency_validation(self):
        """
        Teste de mutação: Validação de consistência de dados.
        """
        # Arrange
        collector = InstagramCollector(
            api_key="test_key",
            cache=self.cache,
            logger=self.logger,
            circuit_breaker=self.circuit_breaker,
            rate_limiter=self.rate_limiter
        )
        
        # Mutação: Dados inconsistentes
        inconsistent_responses = [
            {
                "status": "success",
                "data": {
                    "username": "user1",
                    "posts": [{"id": "1", "likes": 100}]
                }
            },
            {
                "status": "success", 
                "data": {
                    "username": "user1",  # Mesmo usuário
                    "posts": [{"id": "2", "likes": 200}]  # Dados diferentes
                }
            },
            {
                "status": "success",
                "data": {
                    "username": "user1",
                    "posts": [{"id": "1", "likes": 150}]  # Dados modificados
                }
            }
        ]
        
        with patch.object(collector, '_make_api_request') as mock_api:
            mock_api.side_effect = inconsistent_responses
            
            # Act - Coletas consecutivas
            results = []
            for i in range(len(inconsistent_responses)):
                result = await collector.collect_data("user1")
                results.append(result)
            
            # Assert - Validação de consistência
            # Dados devem ser consistentes entre coletas
            assert results[0]["username"] == results[1]["username"]
            assert results[1]["username"] == results[2]["username"]
            
            # Validação de logs de consistência
            consistency_logs = self.logger.get_recent_logs(level="INFO")
            assert any("consistency" in log["message"].lower() for log in consistency_logs) 