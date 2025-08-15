#!/usr/bin/env python3
"""
Testes Unitários - Credential Rate Limiter
=========================================

Tracing ID: TEST_CREDENTIAL_RATE_LIMITER_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Testes para: backend/app/services/credential_rate_limiter.py
Prompt: CHECKLIST_TESTES_UNITARIOS.md - Item 5.2
Ruleset: enterprise_control_layer.yaml
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import time
import threading
from datetime import datetime, timedelta

from backend.app.services.credential_rate_limiter import (
    CredentialRateLimiter, TokenBucket, RateLimitConfig, RateLimitResult,
    RateLimitStrategy
)


class TestCredentialRateLimiter:
    @pytest.fixture
    def rate_limit_config(self):
        return RateLimitConfig(
            max_requests=5,
            window_seconds=60,
            strategy=RateLimitStrategy.TOKEN_BUCKET,
            burst_limit=2,
            cooldown_seconds=300
        )

    @pytest.fixture
    def rate_limiter(self, rate_limit_config):
        return CredentialRateLimiter(rate_limit_config)

    def test_rate_limit_strategy_enum(self):
        """Testa enum RateLimitStrategy."""
        assert RateLimitStrategy.TOKEN_BUCKET.value == "token_bucket"
        assert RateLimitStrategy.LEAKY_BUCKET.value == "leaky_bucket"
        assert RateLimitStrategy.FIXED_WINDOW.value == "fixed_window"
        assert RateLimitStrategy.SLIDING_WINDOW.value == "sliding_window"

    def test_rate_limit_config_dataclass(self):
        """Testa criação de objeto RateLimitConfig."""
        config = RateLimitConfig(
            max_requests=10,
            window_seconds=120,
            strategy=RateLimitStrategy.LEAKY_BUCKET,
            burst_limit=3,
            cooldown_seconds=600
        )
        assert config.max_requests == 10
        assert config.window_seconds == 120
        assert config.strategy == RateLimitStrategy.LEAKY_BUCKET
        assert config.burst_limit == 3
        assert config.cooldown_seconds == 600

    def test_rate_limit_result_dataclass(self):
        """Testa criação de objeto RateLimitResult."""
        result = RateLimitResult(
            allowed=True,
            remaining=3,
            reset_time=time.time() + 30,
            retry_after=30,
            reason="Rate limit OK"
        )
        assert result.allowed is True
        assert result.remaining == 3
        assert result.retry_after == 30
        assert result.reason == "Rate limit OK"

    def test_token_bucket_initialization(self):
        """Testa inicialização do TokenBucket."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        assert bucket.capacity == 10
        assert bucket.refill_rate == 1.0
        assert bucket.tokens == 10
        assert bucket.last_refill > 0

    def test_token_bucket_consume_success(self):
        """Testa consumo bem-sucedido de tokens."""
        bucket = TokenBucket(capacity=5, refill_rate=1.0)
        
        # Consumir 3 tokens
        assert bucket.consume(3) is True
        assert bucket.get_remaining() == 2

    def test_token_bucket_consume_failure(self):
        """Testa falha no consumo de tokens."""
        bucket = TokenBucket(capacity=5, refill_rate=1.0)
        
        # Consumir mais tokens que disponíveis
        assert bucket.consume(7) is False
        assert bucket.get_remaining() == 5

    def test_token_bucket_refill(self):
        """Testa reabastecimento do bucket."""
        bucket = TokenBucket(capacity=5, refill_rate=1.0)
        
        # Consumir todos os tokens
        bucket.consume(5)
        assert bucket.get_remaining() == 0
        
        # Aguardar 2 segundos para reabastecimento
        time.sleep(2)
        
        # Verificar se tokens foram reabastecidos
        remaining = bucket.get_remaining()
        assert remaining > 0
        assert remaining <= 2  # Máximo 2 tokens em 2 segundos

    def test_token_bucket_get_reset_time(self):
        """Testa cálculo do tempo de reset."""
        bucket = TokenBucket(capacity=5, refill_rate=1.0)
        
        # Com bucket cheio
        assert bucket.get_reset_time() == 0
        
        # Com bucket vazio
        bucket.consume(5)
        reset_time = bucket.get_reset_time()
        assert reset_time > 0
        assert reset_time <= 5  # Tempo para reabastecer 5 tokens

    def test_credential_rate_limiter_initialization(self, rate_limit_config):
        """Testa inicialização do CredentialRateLimiter."""
        limiter = CredentialRateLimiter(rate_limit_config)
        assert limiter.config == rate_limit_config
        assert len(limiter.buckets) == 0
        assert len(limiter.blocked_providers) == 0
        assert limiter.total_requests == 0
        assert limiter.blocked_requests == 0
        assert limiter.anomaly_detections == 0

    def test_credential_rate_limiter_default_config(self):
        """Testa inicialização com configuração padrão."""
        limiter = CredentialRateLimiter()
        assert limiter.config.max_requests == 5
        assert limiter.config.window_seconds == 60
        assert limiter.config.strategy == RateLimitStrategy.TOKEN_BUCKET

    def test_get_or_create_bucket(self, rate_limiter):
        """Testa obtenção ou criação de bucket."""
        provider = "test_provider"
        
        # Primeira vez deve criar o bucket
        bucket1 = rate_limiter._get_or_create_bucket(provider)
        assert provider in rate_limiter.buckets
        assert bucket1.capacity == 5
        
        # Segunda vez deve retornar o mesmo bucket
        bucket2 = rate_limiter._get_or_create_bucket(provider)
        assert bucket1 is bucket2

    def test_is_provider_blocked_false(self, rate_limiter):
        """Testa verificação de provider não bloqueado."""
        assert rate_limiter.is_provider_blocked("test_provider") is False

    def test_is_provider_blocked_true(self, rate_limiter):
        """Testa verificação de provider bloqueado."""
        provider = "test_provider"
        rate_limiter.blocked_providers[provider] = time.time() + 60
        
        assert rate_limiter.is_provider_blocked(provider) is True

    def test_is_provider_blocked_expired(self, rate_limiter):
        """Testa verificação de provider com bloqueio expirado."""
        provider = "test_provider"
        rate_limiter.blocked_providers[provider] = time.time() - 60
        
        assert rate_limiter.is_provider_blocked(provider) is False
        assert provider not in rate_limiter.blocked_providers

    def test_check_rate_limit_success(self, rate_limiter):
        """Testa verificação de rate limit bem-sucedida."""
        provider = "test_provider"
        client_ip = "192.168.1.1"
        
        result = rate_limiter.check_rate_limit(provider, client_ip)
        
        assert result.allowed is True
        assert result.remaining >= 0
        assert result.reset_time > time.time()
        assert result.retry_after is None
        assert result.reason is None
        assert rate_limiter.total_requests == 1

    def test_check_rate_limit_exceeded(self, rate_limiter):
        """Testa rate limit excedido."""
        provider = "test_provider"
        
        # Consumir todos os tokens
        for _ in range(6):  # Mais que o limite de 5
            result = rate_limiter.check_rate_limit(provider)
        
        # Última requisição deve ser bloqueada
        assert result.allowed is False
        assert result.remaining == 0
        assert result.retry_after is not None
        assert result.reason == "Rate limit excedido"
        assert rate_limiter.blocked_requests > 0

    def test_check_rate_limit_provider_blocked(self, rate_limiter):
        """Testa rate limit com provider bloqueado."""
        provider = "test_provider"
        rate_limiter.blocked_providers[provider] = time.time() + 60
        
        result = rate_limiter.check_rate_limit(provider)
        
        assert result.allowed is False
        assert result.remaining == 0
        assert result.retry_after == 300  # cooldown_seconds
        assert result.reason == "Provider bloqueado por rate limit"

    def test_record_request(self, rate_limiter):
        """Testa registro de requisição no histórico."""
        provider = "test_provider"
        client_ip = "192.168.1.1"
        
        rate_limiter._record_request(provider, client_ip)
        
        assert provider in rate_limiter.request_history
        assert len(rate_limiter.request_history[provider]) == 1
        
        request_info = rate_limiter.request_history[provider][0]
        assert request_info["provider"] == provider
        assert request_info["client_ip"] == client_ip
        assert "timestamp" in request_info

    def test_check_anomaly_and_block_normal(self, rate_limiter):
        """Testa verificação de anomalia com comportamento normal."""
        provider = "test_provider"
        
        # Adicionar algumas requisições normais
        for _ in range(3):
            rate_limiter._record_request(provider)
        
        rate_limiter._check_anomaly_and_block(provider)
        
        assert provider not in rate_limiter.blocked_providers
        assert rate_limiter.anomaly_detections == 0

    def test_check_anomaly_and_block_anomaly(self, rate_limiter):
        """Testa detecção e bloqueio por anomalia."""
        provider = "test_provider"
        
        # Adicionar muitas requisições rapidamente (mais que burst_limit * 2)
        for _ in range(10):  # burst_limit = 2, então 10 > 4
            rate_limiter._record_request(provider)
        
        rate_limiter._check_anomaly_and_block(provider)
        
        assert provider in rate_limiter.blocked_providers
        assert rate_limiter.anomaly_detections == 1

    def test_get_provider_status_new_provider(self, rate_limiter):
        """Testa status de provider novo."""
        provider = "new_provider"
        status = rate_limiter.get_provider_status(provider)
        
        assert status["provider"] == provider
        assert status["is_blocked"] is False
        assert status["remaining_requests"] == 5  # max_requests
        assert status["max_requests"] == 5
        assert status["reset_time_seconds"] == 0
        assert status["window_seconds"] == 60

    def test_get_provider_status_existing_provider(self, rate_limiter):
        """Testa status de provider existente."""
        provider = "existing_provider"
        
        # Fazer uma requisição para criar o bucket
        rate_limiter.check_rate_limit(provider)
        
        status = rate_limiter.get_provider_status(provider)
        
        assert status["provider"] == provider
        assert status["is_blocked"] is False
        assert status["remaining_requests"] == 4  # 5 - 1
        assert status["max_requests"] == 5

    def test_get_provider_status_blocked_provider(self, rate_limiter):
        """Testa status de provider bloqueado."""
        provider = "blocked_provider"
        rate_limiter.blocked_providers[provider] = time.time() + 60
        
        status = rate_limiter.get_provider_status(provider)
        
        assert status["provider"] == provider
        assert status["is_blocked"] is True

    def test_reset_provider_success(self, rate_limiter):
        """Testa reset bem-sucedido de provider."""
        provider = "test_provider"
        
        # Criar dados do provider
        rate_limiter.check_rate_limit(provider)
        rate_limiter.blocked_providers[provider] = time.time() + 60
        rate_limiter._record_request(provider)
        
        # Resetar
        result = rate_limiter.reset_provider(provider)
        
        assert result is True
        assert provider not in rate_limiter.buckets
        assert provider not in rate_limiter.blocked_providers
        assert len(rate_limiter.request_history[provider]) == 0

    def test_reset_provider_nonexistent(self, rate_limiter):
        """Testa reset de provider inexistente."""
        provider = "nonexistent_provider"
        
        result = rate_limiter.reset_provider(provider)
        
        assert result is True

    def test_get_metrics(self, rate_limiter):
        """Testa obtenção de métricas."""
        # Realizar algumas operações
        rate_limiter.check_rate_limit("provider1")
        rate_limiter.check_rate_limit("provider2")
        
        metrics = rate_limiter.get_metrics()
        
        assert metrics["total_requests"] == 2
        assert metrics["blocked_requests"] == 0
        assert metrics["anomaly_detections"] == 0
        assert metrics["active_providers"] == 2
        assert metrics["blocked_providers"] == 0
        assert metrics["config"]["max_requests"] == 5
        assert metrics["config"]["window_seconds"] == 60
        assert metrics["config"]["strategy"] == "token_bucket"

    def test_is_healthy_success(self, rate_limiter):
        """Testa health check bem-sucedido."""
        assert rate_limiter.is_healthy() is True

    def test_is_healthy_failure(self, rate_limiter):
        """Testa health check com falha."""
        # Simular falha no check_rate_limit
        with patch.object(rate_limiter, 'check_rate_limit', side_effect=Exception("Test error")):
            assert rate_limiter.is_healthy() is False

    def test_thread_safety(self, rate_limiter):
        """Testa thread safety do rate limiter."""
        provider = "thread_test_provider"
        results = []
        
        def make_request():
            result = rate_limiter.check_rate_limit(provider)
            results.append(result.allowed)
        
        # Criar múltiplas threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Aguardar todas as threads
        for thread in threads:
            thread.join()
        
        # Verificar que não houve race conditions
        assert len(results) == 10
        assert sum(results) <= 5  # Máximo 5 requisições permitidas

    def test_token_bucket_thread_safety(self):
        """Testa thread safety do TokenBucket."""
        bucket = TokenBucket(capacity=5, refill_rate=1.0)
        results = []
        
        def consume_token():
            result = bucket.consume(1)
            results.append(result)
        
        # Criar múltiplas threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=consume_token)
            threads.append(thread)
            thread.start()
        
        # Aguardar todas as threads
        for thread in threads:
            thread.join()
        
        # Verificar que apenas 5 tokens foram consumidos
        assert len(results) == 10
        assert sum(results) == 5  # Apenas 5 devem ter sucesso

    def test_rate_limit_with_different_providers(self, rate_limiter):
        """Testa rate limiting com providers diferentes."""
        provider1 = "provider1"
        provider2 = "provider2"
        
        # Consumir tokens do provider1
        for _ in range(3):
            result1 = rate_limiter.check_rate_limit(provider1)
            assert result1.allowed is True
        
        # Provider2 deve ter tokens completos
        result2 = rate_limiter.check_rate_limit(provider2)
        assert result2.allowed is True
        assert result2.remaining == 4  # 5 - 1

    def test_rate_limit_refill_over_time(self, rate_limiter):
        """Testa reabastecimento de tokens ao longo do tempo."""
        provider = "refill_test_provider"
        
        # Consumir todos os tokens
        for _ in range(5):
            rate_limiter.check_rate_limit(provider)
        
        # Última requisição deve ser bloqueada
        result = rate_limiter.check_rate_limit(provider)
        assert result.allowed is False
        
        # Aguardar um pouco para reabastecimento
        time.sleep(1)
        
        # Deve ter alguns tokens disponíveis
        result = rate_limiter.check_rate_limit(provider)
        assert result.allowed is True

    def test_anomaly_detection_with_client_ip(self, rate_limiter):
        """Testa detecção de anomalia com IP do cliente."""
        provider = "anomaly_test_provider"
        client_ip = "192.168.1.100"
        
        # Adicionar muitas requisições rapidamente
        for _ in range(10):
            rate_limiter._record_request(provider, client_ip)
        
        rate_limiter._check_anomaly_and_block(provider, client_ip)
        
        assert provider in rate_limiter.blocked_providers
        assert rate_limiter.anomaly_detections == 1

    def test_request_history_limit(self, rate_limiter):
        """Testa limite do histórico de requisições."""
        provider = "history_test_provider"
        
        # Adicionar mais requisições que o limite (100)
        for i in range(150):
            rate_limiter._record_request(provider)
        
        # Verificar que o histórico não excedeu o limite
        assert len(rate_limiter.request_history[provider]) <= 100

    def test_edge_cases(self, rate_limiter):
        """Testa casos edge."""
        # Teste com provider vazio
        result = rate_limiter.check_rate_limit("")
        assert result.allowed is True
        
        # Teste com provider None
        result = rate_limiter.check_rate_limit(None)
        assert result.allowed is True
        
        # Teste com client_ip None
        result = rate_limiter.check_rate_limit("test", None)
        assert result.allowed is True

    def test_metrics_after_blocked_requests(self, rate_limiter):
        """Testa métricas após requisições bloqueadas."""
        provider = "metrics_test_provider"
        
        # Fazer requisições até exceder o limite
        for _ in range(10):
            rate_limiter.check_rate_limit(provider)
        
        metrics = rate_limiter.get_metrics()
        
        assert metrics["total_requests"] == 10
        assert metrics["blocked_requests"] > 0
        assert metrics["active_providers"] == 1


if __name__ == "__main__":
    pytest.main([__file__]) 