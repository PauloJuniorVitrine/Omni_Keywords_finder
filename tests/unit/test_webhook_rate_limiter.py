"""
Testes Unitários para Webhook Rate Limiter
Rate Limiter Especializado para Webhooks - Omni Keywords Finder

Prompt: Implementação de testes unitários para rate limiter de webhooks
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import time
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any

from backend.app.utils.webhook_rate_limiter import (
    WebhookRateLimiter,
    ClientTier,
    RateLimitConfig,
    RateLimitResult
)


class TestClientTier:
    """Testes para enum ClientTier"""
    
    def test_client_tier_values(self):
        """Testa valores do enum ClientTier"""
        assert ClientTier.FREE.value == "free"
        assert ClientTier.BASIC.value == "basic"
        assert ClientTier.PREMIUM.value == "premium"
        assert ClientTier.ENTERPRISE.value == "enterprise"
    
    def test_client_tier_comparison(self):
        """Testa comparação entre tiers de cliente"""
        assert ClientTier.FREE != ClientTier.BASIC
        assert ClientTier.PREMIUM != ClientTier.ENTERPRISE
        assert ClientTier.FREE == ClientTier.FREE


class TestRateLimitConfig:
    """Testes para RateLimitConfig"""
    
    def test_rate_limit_config_creation(self):
        """Testa criação de RateLimitConfig"""
        config = RateLimitConfig(
            requests_per_hour=1000,
            requests_per_minute=100,
            burst_limit=20,
            window_size=3600
        )
        
        assert config.requests_per_hour == 1000
        assert config.requests_per_minute == 100
        assert config.burst_limit == 20
        assert config.window_size == 3600
    
    def test_rate_limit_config_default_window_size(self):
        """Testa RateLimitConfig com window_size padrão"""
        config = RateLimitConfig(
            requests_per_hour=1000,
            requests_per_minute=100,
            burst_limit=20
        )
        
        assert config.window_size == 3600  # Valor padrão


class TestRateLimitResult:
    """Testes para RateLimitResult"""
    
    def test_rate_limit_result_creation(self):
        """Testa criação de RateLimitResult"""
        result = RateLimitResult(
            allowed=True,
            remaining=50,
            reset_time=1234567890,
            retry_after=None,
            reason=None
        )
        
        assert result.allowed is True
        assert result.remaining == 50
        assert result.reset_time == 1234567890
        assert result.retry_after is None
        assert result.reason is None
    
    def test_rate_limit_result_with_reason(self):
        """Testa RateLimitResult com motivo de bloqueio"""
        result = RateLimitResult(
            allowed=False,
            remaining=0,
            reset_time=1234567890,
            retry_after=60,
            reason="Rate limit exceeded"
        )
        
        assert result.allowed is False
        assert result.remaining == 0
        assert result.retry_after == 60
        assert result.reason == "Rate limit exceeded"


class TestWebhookRateLimiter:
    """Testes para WebhookRateLimiter"""
    
    @pytest.fixture
    def rate_limiter(self):
        """Instância do WebhookRateLimiter para testes"""
        return WebhookRateLimiter()
    
    def test_rate_limiter_initialization(self, rate_limiter):
        """Testa inicialização do WebhookRateLimiter"""
        assert rate_limiter.redis_client is None
        assert rate_limiter.use_redis is False
        assert len(rate_limiter.client_configs) == 4
        assert ClientTier.FREE in rate_limiter.client_configs
        assert ClientTier.BASIC in rate_limiter.client_configs
        assert ClientTier.PREMIUM in rate_limiter.client_configs
        assert ClientTier.ENTERPRISE in rate_limiter.client_configs
        assert len(rate_limiter.memory_storage) == 0
        assert rate_limiter.logger is not None
    
    def test_rate_limiter_with_redis(self, rate_limiter):
        """Testa inicialização do WebhookRateLimiter com Redis"""
        mock_redis = Mock()
        mock_redis.ping.return_value = True
        
        with patch('backend.app.utils.webhook_rate_limiter.redis') as mock_redis_module:
            mock_redis_module.from_url.return_value = mock_redis
            
            rate_limiter = WebhookRateLimiter(redis_url="redis://localhost:6379")
            
            assert rate_limiter.redis_client is not None
            assert rate_limiter.use_redis is True
    
    def test_rate_limiter_redis_fallback(self, rate_limiter):
        """Testa fallback para memória quando Redis falha"""
        with patch('backend.app.utils.webhook_rate_limiter.redis') as mock_redis_module:
            mock_redis_module.from_url.side_effect = Exception("Redis connection failed")
            
            rate_limiter = WebhookRateLimiter(redis_url="redis://localhost:6379")
            
            assert rate_limiter.redis_client is None
            assert rate_limiter.use_redis is False
    
    def test_get_client_tier_by_api_key_enterprise(self, rate_limiter):
        """Testa determinação de tier por API key enterprise"""
        tier = rate_limiter._get_client_tier(api_key="enterprise_key_123")
        
        assert tier == ClientTier.ENTERPRISE
    
    def test_get_client_tier_by_api_key_premium(self, rate_limiter):
        """Testa determinação de tier por API key premium"""
        tier = rate_limiter._get_client_tier(api_key="premium_key_123")
        
        assert tier == ClientTier.PREMIUM
    
    def test_get_client_tier_by_api_key_basic(self, rate_limiter):
        """Testa determinação de tier por API key basic"""
        tier = rate_limiter._get_client_tier(api_key="basic_key_123")
        
        assert tier == ClientTier.BASIC
    
    def test_get_client_tier_by_api_key_free(self, rate_limiter):
        """Testa determinação de tier por API key free"""
        tier = rate_limiter._get_client_tier(api_key="free_key_123")
        
        assert tier == ClientTier.FREE
    
    def test_get_client_tier_by_user_id(self, rate_limiter):
        """Testa determinação de tier por user_id"""
        tier = rate_limiter._get_client_tier(user_id="user123")
        
        assert tier == ClientTier.BASIC
    
    def test_get_client_tier_no_credentials(self, rate_limiter):
        """Testa determinação de tier sem credenciais"""
        tier = rate_limiter._get_client_tier()
        
        assert tier == ClientTier.FREE
    
    def test_get_identifier_with_api_key(self, rate_limiter):
        """Testa geração de identificador com API key"""
        identifier = rate_limiter._get_identifier("192.168.1.1", api_key="test_key")
        
        assert identifier == "webhook:api:test_key"
    
    def test_get_identifier_with_user_id(self, rate_limiter):
        """Testa geração de identificador com user_id"""
        identifier = rate_limiter._get_identifier("192.168.1.1", user_id="user123")
        
        assert identifier == "webhook:user:user123"
    
    def test_get_identifier_with_ip_only(self, rate_limiter):
        """Testa geração de identificador apenas com IP"""
        identifier = rate_limiter._get_identifier("192.168.1.1")
        
        assert identifier == "webhook:ip:192.168.1.1"
    
    def test_check_memory_rate_limit_allowed(self, rate_limiter):
        """Testa verificação de rate limit em memória - permitido"""
        current_time = int(time.time())
        identifier = "test_identifier"
        config = RateLimitConfig(
            requests_per_hour=100,
            requests_per_minute=10,
            burst_limit=5
        )
        
        result = rate_limiter._check_memory_rate_limit(identifier, config, current_time)
        
        assert result.allowed is True
        assert result.remaining >= 0
        assert result.reset_time > current_time
        assert result.reason is None
    
    def test_check_memory_rate_limit_hourly_exceeded(self, rate_limiter):
        """Testa verificação de rate limit em memória - limite horário excedido"""
        current_time = int(time.time())
        identifier = "test_identifier"
        config = RateLimitConfig(
            requests_per_hour=2,
            requests_per_minute=10,
            burst_limit=5
        )
        
        # Adicionar requisições para exceder limite horário
        rate_limiter.memory_storage[identifier] = [current_time - 100, current_time - 200]
        
        result = rate_limiter._check_memory_rate_limit(identifier, config, current_time)
        
        assert result.allowed is False
        assert result.remaining == 0
        assert "Hourly limit exceeded" in result.reason
    
    def test_check_memory_rate_limit_minute_exceeded(self, rate_limiter):
        """Testa verificação de rate limit em memória - limite por minuto excedido"""
        current_time = int(time.time())
        identifier = "test_identifier"
        config = RateLimitConfig(
            requests_per_hour=100,
            requests_per_minute=2,
            burst_limit=5
        )
        
        # Adicionar requisições para exceder limite por minuto
        rate_limiter.memory_storage[identifier] = [current_time - 30, current_time - 45]
        
        result = rate_limiter._check_memory_rate_limit(identifier, config, current_time)
        
        assert result.allowed is False
        assert result.remaining == 0
        assert "Minute limit exceeded" in result.reason
    
    def test_check_memory_rate_limit_burst_exceeded(self, rate_limiter):
        """Testa verificação de rate limit em memória - limite de burst excedido"""
        current_time = int(time.time())
        identifier = "test_identifier"
        config = RateLimitConfig(
            requests_per_hour=100,
            requests_per_minute=10,
            burst_limit=2
        )
        
        # Adicionar requisições para exceder limite de burst
        rate_limiter.memory_storage[identifier] = [current_time, current_time]
        
        result = rate_limiter._check_memory_rate_limit(identifier, config, current_time)
        
        assert result.allowed is False
        assert result.remaining == 0
        assert "Burst limit exceeded" in result.reason
    
    def test_cleanup_old_records(self, rate_limiter):
        """Testa limpeza de registros antigos"""
        current_time = int(time.time())
        identifier = "test_identifier"
        
        # Adicionar registros antigos e recentes
        rate_limiter.memory_storage[identifier] = [
            current_time - 7200,  # 2 horas atrás (antigo)
            current_time - 1800,  # 30 minutos atrás (recente)
            current_time - 300,   # 5 minutos atrás (recente)
            current_time          # agora (recente)
        ]
        
        rate_limiter._cleanup_old_records(identifier, current_time)
        
        # Apenas registros da última hora devem permanecer
        remaining_records = rate_limiter.memory_storage[identifier]
        assert len(remaining_records) == 3
        assert current_time - 7200 not in remaining_records
    
    def test_check_rate_limit_free_tier(self, rate_limiter):
        """Testa verificação de rate limit para tier free"""
        result = rate_limiter.check_rate_limit("192.168.1.1")
        
        assert result.allowed is True
        assert result.remaining >= 0
        assert result.reset_time > int(time.time())
    
    def test_check_rate_limit_basic_tier(self, rate_limiter):
        """Testa verificação de rate limit para tier basic"""
        result = rate_limiter.check_rate_limit("192.168.1.1", user_id="user123")
        
        assert result.allowed is True
        assert result.remaining >= 0
        assert result.reset_time > int(time.time())
    
    def test_check_rate_limit_premium_tier(self, rate_limiter):
        """Testa verificação de rate limit para tier premium"""
        result = rate_limiter.check_rate_limit("192.168.1.1", api_key="premium_key_123")
        
        assert result.allowed is True
        assert result.remaining >= 0
        assert result.reset_time > int(time.time())
    
    def test_check_rate_limit_enterprise_tier(self, rate_limiter):
        """Testa verificação de rate limit para tier enterprise"""
        result = rate_limiter.check_rate_limit("192.168.1.1", api_key="enterprise_key_123")
        
        assert result.allowed is True
        assert result.remaining >= 0
        assert result.reset_time > int(time.time())
    
    def test_check_rate_limit_with_endpoint_id(self, rate_limiter):
        """Testa verificação de rate limit com endpoint_id"""
        result = rate_limiter.check_rate_limit(
            "192.168.1.1",
            api_key="basic_key_123",
            endpoint_id="webhook_123"
        )
        
        assert result.allowed is True
        assert result.remaining >= 0
        assert result.reset_time > int(time.time())
    
    def test_get_rate_limit_info_free_tier(self, rate_limiter):
        """Testa obtenção de informações de rate limit para tier free"""
        info = rate_limiter.get_rate_limit_info("192.168.1.1")
        
        assert info["client_tier"] == "free"
        assert "limits" in info
        assert "requests_per_hour" in info["limits"]
        assert "requests_per_minute" in info["limits"]
        assert "burst_limit" in info["limits"]
        assert info["window_size"] == 3600
    
    def test_get_rate_limit_info_enterprise_tier(self, rate_limiter):
        """Testa obtenção de informações de rate limit para tier enterprise"""
        info = rate_limiter.get_rate_limit_info("192.168.1.1", api_key="enterprise_key_123")
        
        assert info["client_tier"] == "enterprise"
        assert info["limits"]["requests_per_hour"] == 100000
        assert info["limits"]["requests_per_minute"] == 10000
        assert info["limits"]["burst_limit"] == 1000
    
    def test_reset_rate_limit_memory(self, rate_limiter):
        """Testa reset de rate limit em memória"""
        identifier = "webhook:ip:192.168.1.1"
        rate_limiter.memory_storage[identifier] = [int(time.time())]
        
        result = rate_limiter.reset_rate_limit("192.168.1.1")
        
        assert result is True
        assert identifier not in rate_limiter.memory_storage
    
    def test_reset_rate_limit_with_endpoint_id(self, rate_limiter):
        """Testa reset de rate limit com endpoint_id"""
        result = rate_limiter.reset_rate_limit(
            "192.168.1.1",
            api_key="test_key",
            endpoint_id="webhook_123"
        )
        
        assert result is True
    
    def test_get_statistics(self, rate_limiter):
        """Testa obtenção de estatísticas"""
        stats = rate_limiter.get_statistics()
        
        assert stats["storage_type"] == "memory"
        assert "client_configs" in stats
        assert "free" in stats["client_configs"]
        assert "basic" in stats["client_configs"]
        assert "premium" in stats["client_configs"]
        assert "enterprise" in stats["client_configs"]
        assert "memory_entries" in stats
        assert stats["memory_entries"] == 0


class TestWebhookRateLimiterRedis:
    """Testes para WebhookRateLimiter com Redis"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock do Redis para testes"""
        mock_redis = Mock()
        mock_redis.ping.return_value = True
        return mock_redis
    
    @pytest.fixture
    def rate_limiter_with_redis(self, mock_redis):
        """Instância do WebhookRateLimiter com Redis mockado"""
        with patch('backend.app.utils.webhook_rate_limiter.redis') as mock_redis_module:
            mock_redis_module.from_url.return_value = mock_redis
            
            return WebhookRateLimiter(redis_url="redis://localhost:6379")
    
    def test_redis_rate_limit_allowed(self, rate_limiter_with_redis, mock_redis):
        """Testa verificação de rate limit no Redis - permitido"""
        # Mock das respostas do Redis
        mock_pipeline = Mock()
        mock_pipeline.execute.return_value = [b"5", 1800, b"2", 30, b"1", 1]  # Contadores baixos
        mock_redis.pipeline.return_value = mock_pipeline
        
        current_time = int(time.time())
        identifier = "test_identifier"
        config = RateLimitConfig(
            requests_per_hour=100,
            requests_per_minute=10,
            burst_limit=5
        )
        
        result = rate_limiter_with_redis._check_redis_rate_limit(identifier, config, current_time)
        
        assert result.allowed is True
        assert result.remaining >= 0
        assert result.reset_time > current_time
    
    def test_redis_rate_limit_hourly_exceeded(self, rate_limiter_with_redis, mock_redis):
        """Testa verificação de rate limit no Redis - limite horário excedido"""
        # Mock das respostas do Redis
        mock_pipeline = Mock()
        mock_pipeline.execute.return_value = [b"100", 1800, b"2", 30, b"1", 1]  # Limite horário excedido
        mock_redis.pipeline.return_value = mock_pipeline
        
        current_time = int(time.time())
        identifier = "test_identifier"
        config = RateLimitConfig(
            requests_per_hour=100,
            requests_per_minute=10,
            burst_limit=5
        )
        
        result = rate_limiter_with_redis._check_redis_rate_limit(identifier, config, current_time)
        
        assert result.allowed is False
        assert result.remaining == 0
        assert "Hourly limit exceeded" in result.reason
    
    def test_redis_rate_limit_minute_exceeded(self, rate_limiter_with_redis, mock_redis):
        """Testa verificação de rate limit no Redis - limite por minuto excedido"""
        # Mock das respostas do Redis
        mock_pipeline = Mock()
        mock_pipeline.execute.return_value = [b"5", 1800, b"10", 30, b"1", 1]  # Limite por minuto excedido
        mock_redis.pipeline.return_value = mock_pipeline
        
        current_time = int(time.time())
        identifier = "test_identifier"
        config = RateLimitConfig(
            requests_per_hour=100,
            requests_per_minute=10,
            burst_limit=5
        )
        
        result = rate_limiter_with_redis._check_redis_rate_limit(identifier, config, current_time)
        
        assert result.allowed is False
        assert result.remaining == 0
        assert "Minute limit exceeded" in result.reason
    
    def test_redis_rate_limit_burst_exceeded(self, rate_limiter_with_redis, mock_redis):
        """Testa verificação de rate limit no Redis - limite de burst excedido"""
        # Mock das respostas do Redis
        mock_pipeline = Mock()
        mock_pipeline.execute.return_value = [b"5", 1800, b"2", 30, b"5", 1]  # Limite de burst excedido
        mock_redis.pipeline.return_value = mock_pipeline
        
        current_time = int(time.time())
        identifier = "test_identifier"
        config = RateLimitConfig(
            requests_per_hour=100,
            requests_per_minute=10,
            burst_limit=5
        )
        
        result = rate_limiter_with_redis._check_redis_rate_limit(identifier, config, current_time)
        
        assert result.allowed is False
        assert result.remaining == 0
        assert "Burst limit exceeded" in result.reason
    
    def test_redis_rate_limit_fallback_to_memory(self, rate_limiter_with_redis, mock_redis):
        """Testa fallback para memória quando Redis falha"""
        # Mock de erro no Redis
        mock_redis.pipeline.side_effect = Exception("Redis error")
        
        current_time = int(time.time())
        identifier = "test_identifier"
        config = RateLimitConfig(
            requests_per_hour=100,
            requests_per_minute=10,
            burst_limit=5
        )
        
        result = rate_limiter_with_redis._check_redis_rate_limit(identifier, config, current_time)
        
        # Deve fazer fallback para memória
        assert result.allowed is True
        assert result.remaining >= 0
    
    def test_reset_rate_limit_redis(self, rate_limiter_with_redis, mock_redis):
        """Testa reset de rate limit no Redis"""
        # Mock das chaves do Redis
        mock_redis.keys.return_value = ["key1", "key2", "key3"]
        mock_redis.delete.return_value = 3
        
        result = rate_limiter_with_redis.reset_rate_limit("192.168.1.1", api_key="test_key")
        
        assert result is True
        mock_redis.keys.assert_called_once()
        mock_redis.delete.assert_called_once_with("key1", "key2", "key3")
    
    def test_get_statistics_with_redis(self, rate_limiter_with_redis):
        """Testa obtenção de estatísticas com Redis"""
        stats = rate_limiter_with_redis.get_statistics()
        
        assert stats["storage_type"] == "redis"
        assert "client_configs" in stats
        assert "memory_entries" not in stats


class TestWebhookRateLimiterIntegration:
    """Testes de integração para WebhookRateLimiter"""
    
    @pytest.fixture
    def rate_limiter(self):
        """Instância do WebhookRateLimiter para testes"""
        return WebhookRateLimiter()
    
    def test_complex_rate_limiting_scenario(self, rate_limiter):
        """Testa cenário complexo de rate limiting"""
        # Simular múltiplas requisições
        results = []
        for i in range(15):  # Exceder limite por minuto do tier free (10)
            result = rate_limiter.check_rate_limit("192.168.1.1")
            results.append(result)
        
        # As primeiras 10 devem ser permitidas
        for i in range(10):
            assert results[i].allowed is True
        
        # As próximas devem ser bloqueadas
        for i in range(10, 15):
            assert results[i].allowed is False
            assert "Minute limit exceeded" in results[i].reason
    
    def test_rate_limiting_different_tiers(self, rate_limiter):
        """Testa rate limiting para diferentes tiers"""
        # Tier free
        free_result = rate_limiter.check_rate_limit("192.168.1.1")
        free_info = rate_limiter.get_rate_limit_info("192.168.1.1")
        
        # Tier basic
        basic_result = rate_limiter.check_rate_limit("192.168.1.2", user_id="user123")
        basic_info = rate_limiter.get_rate_limit_info("192.168.1.2", user_id="user123")
        
        # Tier premium
        premium_result = rate_limiter.check_rate_limit("192.168.1.3", api_key="premium_key_123")
        premium_info = rate_limiter.get_rate_limit_info("192.168.1.3", api_key="premium_key_123")
        
        # Verificar que todos foram permitidos
        assert free_result.allowed is True
        assert basic_result.allowed is True
        assert premium_result.allowed is True
        
        # Verificar que os limites são diferentes
        assert free_info["limits"]["requests_per_hour"] < basic_info["limits"]["requests_per_hour"]
        assert basic_info["limits"]["requests_per_hour"] < premium_info["limits"]["requests_per_hour"]
    
    def test_rate_limiting_with_reset(self, rate_limiter):
        """Testa rate limiting com reset"""
        # Fazer algumas requisições
        for i in range(5):
            rate_limiter.check_rate_limit("192.168.1.1")
        
        # Resetar rate limit
        reset_result = rate_limiter.reset_rate_limit("192.168.1.1")
        assert reset_result is True
        
        # Verificar que pode fazer mais requisições
        result = rate_limiter.check_rate_limit("192.168.1.1")
        assert result.allowed is True


class TestWebhookRateLimiterErrorHandling:
    """Testes de tratamento de erros para WebhookRateLimiter"""
    
    @pytest.fixture
    def rate_limiter(self):
        """Instância do WebhookRateLimiter para testes"""
        return WebhookRateLimiter()
    
    def test_check_rate_limit_with_exception(self, rate_limiter):
        """Testa verificação de rate limit com exceção"""
        # Mock de exceção no _get_client_tier
        with patch.object(rate_limiter, '_get_client_tier', side_effect=Exception("Test error")):
            result = rate_limiter.check_rate_limit("192.168.1.1")
            
            # Deve permitir a requisição em caso de erro
            assert result.allowed is True
            assert result.remaining == 1000
    
    def test_memory_rate_limit_with_exception(self, rate_limiter):
        """Testa rate limit em memória com exceção"""
        # Mock de exceção no _cleanup_old_records
        with patch.object(rate_limiter, '_cleanup_old_records', side_effect=Exception("Test error")):
            current_time = int(time.time())
            identifier = "test_identifier"
            config = RateLimitConfig(
                requests_per_hour=100,
                requests_per_minute=10,
                burst_limit=5
            )
            
            result = rate_limiter._check_memory_rate_limit(identifier, config, current_time)
            
            # Deve permitir a requisição em caso de erro
            assert result.allowed is True
            assert result.remaining == 99


class TestWebhookRateLimiterPerformance:
    """Testes de performance para WebhookRateLimiter"""
    
    @pytest.fixture
    def rate_limiter(self):
        """Instância do WebhookRateLimiter para testes"""
        return WebhookRateLimiter()
    
    def test_multiple_rate_limit_checks_performance(self, rate_limiter):
        """Testa performance de múltiplas verificações de rate limit"""
        import time
        
        start_time = time.time()
        
        # Fazer múltiplas verificações
        for i in range(1000):
            rate_limiter.check_rate_limit(f"192.168.1.{i % 256}")
        
        end_time = time.time()
        
        # Verificar performance (deve ser rápido)
        assert end_time - start_time < 5.0  # Menos de 5 segundos para 1000 verificações
    
    def test_memory_usage_with_many_identifiers(self, rate_limiter):
        """Testa uso de memória com muitos identificadores"""
        # Criar muitos identificadores
        for i in range(1000):
            rate_limiter.check_rate_limit(f"192.168.1.{i % 256}")
        
        # Verificar que não há vazamento de memória
        stats = rate_limiter.get_statistics()
        assert stats["memory_entries"] <= 1000  # Máximo 1000 entradas


if __name__ == "__main__":
    pytest.main([__file__]) 