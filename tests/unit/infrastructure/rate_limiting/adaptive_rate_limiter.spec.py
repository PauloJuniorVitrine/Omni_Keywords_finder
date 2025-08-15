from typing import Dict, List, Optional, Any
"""
Testes unitários para AdaptiveRateLimiter
⚠️ CRIAR MAS NÃO EXECUTAR - Executar apenas na Fase 6.5

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Fase 2.3
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Versão: 1.0.0
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from infrastructure.rate_limiting.adaptive_rate_limiter import (
    AdaptiveRateLimiter,
    RateLimitConfig,
    RateLimitMetrics,
    SystemLoad,
    RateLimitAlgorithm,
    TokenBucketRateLimiter,
    LeakyBucketRateLimiter,
    SlidingWindowRateLimiter
)

class TestAdaptiveRateLimiter:
    """Testes para AdaptiveRateLimiter."""
    
    @pytest.fixture
    def rate_limiter(self):
        """Fixture para rate limiter."""
        config = RateLimitConfig(
            initial_rate=10,
            min_rate=5,
            max_rate=50,
            burst_size=20,
            window_size=60,
            adaptation_factor=0.1
        )
        return AdaptiveRateLimiter(config)
    
    @pytest.fixture
    def mock_load_callback(self):
        """Fixture para callback de carga."""
        return Mock(return_value=0.5)
    
    @pytest.fixture
    def mock_adaptation_callback(self):
        """Fixture para callback de adaptação."""
        return Mock()
    
    def test_init(self, rate_limiter):
        """Testa inicialização do rate limiter."""
        assert rate_limiter.current_rate == 10
        assert rate_limiter.tokens == 20
        assert rate_limiter.config.initial_rate == 10
        assert rate_limiter.config.min_rate == 5
        assert rate_limiter.config.max_rate == 50
        assert isinstance(rate_limiter.request_history, list)
        assert isinstance(rate_limiter.response_times, list)
        assert isinstance(rate_limiter.error_history, list)
    
    @pytest.mark.asyncio
    async def test_allow_request_success(self, rate_limiter):
        """Testa requisição permitida com sucesso."""
        result = await rate_limiter.allow_request("client1", "medium", timeout=1.0)
        
        assert result is True
        assert rate_limiter.tokens == 19  # Um token usado
        assert rate_limiter.metrics['allowed_requests'] == 1
        assert rate_limiter.metrics['blocked_requests'] == 0
    
    @pytest.mark.asyncio
    async def test_allow_request_no_tokens(self, rate_limiter):
        """Testa requisição quando não há tokens."""
        # Usar todos os tokens
        for _ in range(20):
            await rate_limiter.allow_request("client1")
        
        # Próxima requisição deve ser bloqueada
        result = await rate_limiter.allow_request("client1")
        
        assert result is False
        assert rate_limiter.metrics['blocked_requests'] == 1
    
    @pytest.mark.asyncio
    async def test_allow_request_high_priority(self, rate_limiter):
        """Testa requisição de alta prioridade."""
        # Usar todos os tokens
        for _ in range(20):
            await rate_limiter.allow_request("client1")
        
        # Requisição de alta prioridade deve usar burst
        result = await rate_limiter.allow_request("client1", priority="high")
        
        assert result is True
        assert rate_limiter.config.burst_size == 19  # Burst usado
    
    @pytest.mark.asyncio
    async def test_allow_request_with_queue(self, rate_limiter):
        """Testa requisição com fila de espera."""
        # Usar todos os tokens
        for _ in range(20):
            await rate_limiter.allow_request("client1")
        
        # Requisição com timeout deve esperar na fila
        result = await rate_limiter.allow_request("client1", timeout=0.1)
        
        # Deve ser bloqueada após timeout
        assert result is False
    
    @pytest.mark.asyncio
    async def test_token_refill(self, rate_limiter):
        """Testa reabastecimento de tokens."""
        # Usar alguns tokens
        for _ in range(5):
            await rate_limiter.allow_request("client1")
        
        initial_tokens = rate_limiter.tokens
        
        # Aguardar reabastecimento
        await asyncio.sleep(0.2)
        
        # Forçar reabastecimento
        rate_limiter._refill_tokens()
        
        # Tokens devem ter aumentado
        assert rate_limiter.tokens > initial_tokens
    
    def test_record_request(self, rate_limiter):
        """Testa registro de requisição."""
        start_time = time.time()
        
        rate_limiter._record_request(start_time, True)
        
        assert len(rate_limiter.request_history) == 1
        assert rate_limiter.request_history[0]['allowed'] is True
        assert rate_limiter.request_history[0]['duration'] >= 0
    
    def test_record_response_time(self, rate_limiter):
        """Testa registro de tempo de resposta."""
        rate_limiter.record_response_time(0.5)
        
        assert len(rate_limiter.response_times) == 1
        assert rate_limiter.response_times[0] == 0.5
    
    def test_record_error(self, rate_limiter):
        """Testa registro de erro."""
        rate_limiter.record_error("Test error")
        
        assert len(rate_limiter.error_history) == 1
        assert rate_limiter.error_history[0]['error'] == "Test error"
    
    def test_adapt_rate(self, rate_limiter, mock_load_callback, mock_adaptation_callback):
        """Testa adaptação de taxa."""
        rate_limiter.set_load_monitor_callback(mock_load_callback)
        rate_limiter.set_adaptation_callback(mock_adaptation_callback)
        
        # Adicionar alguns dados de teste
        rate_limiter.record_response_time(0.1)
        rate_limiter.record_response_time(0.2)
        rate_limiter.record_error("error1")
        
        initial_rate = rate_limiter.current_rate
        
        rate_limiter.adapt_rate()
        
        # Verificar se callback foi chamado
        mock_load_callback.assert_called_once()
        mock_adaptation_callback.assert_called_once()
        
        # Verificar se métricas foram atualizadas
        assert rate_limiter.metrics['adaptation_count'] == 1
        assert rate_limiter.metrics['last_adaptation'] is not None
    
    def test_get_system_load_with_callback(self, rate_limiter, mock_load_callback):
        """Testa obtenção de carga do sistema com callback."""
        rate_limiter.set_load_monitor_callback(mock_load_callback)
        
        load = rate_limiter._get_system_load()
        
        assert load == 0.5
        mock_load_callback.assert_called_once()
    
    def test_get_system_load_without_callback(self, rate_limiter):
        """Testa obtenção de carga do sistema sem callback."""
        # Adicionar algumas requisições recentes
        for _ in range(10):
            rate_limiter._record_request(time.time(), True)
        
        load = rate_limiter._get_system_load()
        
        assert 0.0 <= load <= 1.0
    
    def test_calculate_avg_response_time(self, rate_limiter):
        """Testa cálculo de tempo médio de resposta."""
        # Sem dados
        avg_time = rate_limiter._calculate_avg_response_time()
        assert avg_time == 0.0
        
        # Com dados
        rate_limiter.record_response_time(0.1)
        rate_limiter.record_response_time(0.2)
        rate_limiter.record_response_time(0.3)
        
        avg_time = rate_limiter._calculate_avg_response_time()
        assert avg_time == 0.2
    
    def test_calculate_error_rate(self, rate_limiter):
        """Testa cálculo de taxa de erro."""
        # Sem dados
        error_rate = rate_limiter._calculate_error_rate()
        assert error_rate == 0.0
        
        # Com dados
        rate_limiter._record_request(time.time(), True)
        rate_limiter._record_request(time.time(), True)
        rate_limiter.record_error("error1")
        
        error_rate = rate_limiter._calculate_error_rate()
        assert error_rate == 0.5  # 1 erro em 2 requisições
    
    def test_calculate_adaptive_rate(self, rate_limiter):
        """Testa cálculo de taxa adaptativa."""
        # Testar com diferentes cenários
        rate1 = rate_limiter._calculate_adaptive_rate(0.2, 0.1, 0.05)  # Baixa carga
        rate2 = rate_limiter._calculate_adaptive_rate(0.8, 0.5, 0.2)  # Alta carga
        
        # Taxa deve ser maior com baixa carga
        assert rate1 > rate2
        
        # Verificar limites
        assert rate_limiter.config.min_rate <= rate1 <= rate_limiter.config.max_rate
        assert rate_limiter.config.min_rate <= rate2 <= rate_limiter.config.max_rate
    
    def test_get_metrics(self, rate_limiter):
        """Testa obtenção de métricas."""
        # Adicionar alguns dados
        rate_limiter.metrics['allowed_requests'] = 10
        rate_limiter.metrics['blocked_requests'] = 2
        rate_limiter.record_response_time(0.1)
        rate_limiter.record_error("error1")
        
        metrics = rate_limiter.get_metrics()
        
        assert isinstance(metrics, RateLimitMetrics)
        assert metrics.current_rate == 10
        assert metrics.allowed_requests == 10
        assert metrics.blocked_requests == 2
        assert metrics.adaptation_count == 0
        assert isinstance(metrics.last_adaptation, datetime)
        assert metrics.avg_response_time == 0.1
        assert metrics.error_rate > 0
    
    def test_get_system_load_level(self, rate_limiter):
        """Testa obtenção de nível de carga do sistema."""
        # Mock de carga baixa
        with patch.object(rate_limiter, '_get_system_load', return_value=0.2):
            load_level = rate_limiter.get_system_load_level()
            assert load_level == SystemLoad.LOW
        
        # Mock de carga crítica
        with patch.object(rate_limiter, '_get_system_load', return_value=0.98):
            load_level = rate_limiter.get_system_load_level()
            assert load_level == SystemLoad.CRITICAL
    
    def test_reset_metrics(self, rate_limiter):
        """Testa reset de métricas."""
        # Adicionar alguns dados
        rate_limiter.metrics['allowed_requests'] = 10
        rate_limiter.metrics['blocked_requests'] = 5
        rate_limiter.record_response_time(0.1)
        rate_limiter.record_error("error1")
        
        rate_limiter.reset_metrics()
        
        assert rate_limiter.metrics['allowed_requests'] == 0
        assert rate_limiter.metrics['blocked_requests'] == 0
        assert len(rate_limiter.request_history) == 0
        assert len(rate_limiter.response_times) == 0
        assert len(rate_limiter.error_history) == 0

class TestTokenBucketRateLimiter:
    """Testes para TokenBucketRateLimiter."""
    
    @pytest.fixture
    def token_bucket(self):
        """Fixture para token bucket."""
        return TokenBucketRateLimiter(rate=10, capacity=20)
    
    def test_init(self, token_bucket):
        """Testa inicialização do token bucket."""
        assert token_bucket.rate == 10
        assert token_bucket.capacity == 20
        assert token_bucket.tokens == 20
    
    def test_allow_request_with_tokens(self, token_bucket):
        """Testa requisição com tokens disponíveis."""
        result = token_bucket.allow_request()
        
        assert result is True
        assert token_bucket.tokens == 19
    
    def test_allow_request_no_tokens(self, token_bucket):
        """Testa requisição sem tokens."""
        # Usar todos os tokens
        for _ in range(20):
            token_bucket.allow_request()
        
        # Próxima requisição deve ser bloqueada
        result = token_bucket.allow_request()
        
        assert result is False
        assert token_bucket.tokens == 0
    
    def test_token_refill(self, token_bucket):
        """Testa reabastecimento de tokens."""
        # Usar alguns tokens
        for _ in range(5):
            token_bucket.allow_request()
        
        initial_tokens = token_bucket.tokens
        
        # Aguardar reabastecimento
        time.sleep(0.2)
        token_bucket._refill_tokens()
        
        # Tokens devem ter aumentado
        assert token_bucket.tokens > initial_tokens
    
    def test_token_refill_capacity_limit(self, token_bucket):
        """Testa limite de capacidade no reabastecimento."""
        # Usar alguns tokens
        token_bucket.allow_request()
        
        # Aguardar muito tempo
        time.sleep(1.0)
        token_bucket._refill_tokens()
        
        # Tokens não devem exceder capacidade
        assert token_bucket.tokens <= token_bucket.capacity

class TestLeakyBucketRateLimiter:
    """Testes para LeakyBucketRateLimiter."""
    
    @pytest.fixture
    def leaky_bucket(self):
        """Fixture para leaky bucket."""
        return LeakyBucketRateLimiter(rate=5, capacity=10)
    
    def test_init(self, leaky_bucket):
        """Testa inicialização do leaky bucket."""
        assert leaky_bucket.rate == 5
        assert leaky_bucket.capacity == 10
        assert len(leaky_bucket.queue) == 0
    
    def test_allow_request_with_capacity(self, leaky_bucket):
        """Testa requisição com capacidade disponível."""
        result = leaky_bucket.allow_request()
        
        assert result is True
        assert len(leaky_bucket.queue) == 1
    
    def test_allow_request_no_capacity(self, leaky_bucket):
        """Testa requisição sem capacidade."""
        # Preencher bucket
        for _ in range(10):
            leaky_bucket.allow_request()
        
        # Próxima requisição deve ser bloqueada
        result = leaky_bucket.allow_request()
        
        assert result is False
        assert len(leaky_bucket.queue) == 10
    
    def test_token_leak(self, leaky_bucket):
        """Testa vazamento de tokens."""
        # Adicionar alguns tokens
        for _ in range(5):
            leaky_bucket.allow_request()
        
        initial_size = len(leaky_bucket.queue)
        
        # Aguardar vazamento
        time.sleep(0.2)
        leaky_bucket._leak_tokens()
        
        # Tamanho deve ter diminuído
        assert len(leaky_bucket.queue) < initial_size

class TestSlidingWindowRateLimiter:
    """Testes para SlidingWindowRateLimiter."""
    
    @pytest.fixture
    def sliding_window(self):
        """Fixture para sliding window."""
        return SlidingWindowRateLimiter(rate=5, window_size=10)
    
    def test_init(self, sliding_window):
        """Testa inicialização do sliding window."""
        assert sliding_window.rate == 5
        assert sliding_window.window_size == 10
        assert len(sliding_window.requests) == 0
    
    def test_allow_request_within_rate(self, sliding_window):
        """Testa requisição dentro da taxa."""
        for index in range(5):
            result = sliding_window.allow_request()
            assert result is True
            assert len(sliding_window.requests) == index + 1
    
    def test_allow_request_exceed_rate(self, sliding_window):
        """Testa requisição excedendo a taxa."""
        # Usar toda a taxa
        for _ in range(5):
            sliding_window.allow_request()
        
        # Próxima requisição deve ser bloqueada
        result = sliding_window.allow_request()
        
        assert result is False
        assert len(sliding_window.requests) == 5
    
    def test_window_sliding(self, sliding_window):
        """Testa deslizamento da janela."""
        # Adicionar requisições antigas
        old_time = time.time() - 15  # Mais antiga que window_size
        sliding_window.requests.extend([old_time, old_time, old_time])
        
        # Adicionar requisições recentes
        for _ in range(3):
            sliding_window.allow_request()
        
        # Requisições antigas devem ter sido removidas
        assert len(sliding_window.requests) == 3

class TestRateLimitConfig:
    """Testes para RateLimitConfig."""
    
    def test_default_config(self):
        """Testa configuração padrão."""
        config = RateLimitConfig()
        
        assert config.initial_rate == 100
        assert config.min_rate == 10
        assert config.max_rate == 1000
        assert config.burst_size == 50
        assert config.window_size == 60
        assert config.adaptation_factor == 0.1
        assert isinstance(config.load_thresholds, dict)
    
    def test_custom_config(self):
        """Testa configuração customizada."""
        config = RateLimitConfig(
            initial_rate=50,
            min_rate=5,
            max_rate=200,
            burst_size=25,
            window_size=30,
            adaptation_factor=0.2
        )
        
        assert config.initial_rate == 50
        assert config.min_rate == 5
        assert config.max_rate == 200
        assert config.burst_size == 25
        assert config.window_size == 30
        assert config.adaptation_factor == 0.2

class TestRateLimitMetrics:
    """Testes para RateLimitMetrics."""
    
    def test_rate_limit_metrics_creation(self):
        """Testa criação de métricas."""
        metrics = RateLimitMetrics(
            current_rate=10,
            allowed_requests=100,
            blocked_requests=5,
            system_load=0.5,
            adaptation_count=2,
            last_adaptation=datetime.utcnow(),
            avg_response_time=0.1,
            error_rate=0.05
        )
        
        assert metrics.current_rate == 10
        assert metrics.allowed_requests == 100
        assert metrics.blocked_requests == 5
        assert metrics.system_load == 0.5
        assert metrics.adaptation_count == 2
        assert metrics.avg_response_time == 0.1
        assert metrics.error_rate == 0.05

class TestEnums:
    """Testes para enums."""
    
    def test_system_load_enum(self):
        """Testa enum SystemLoad."""
        assert SystemLoad.LOW.value == "low"
        assert SystemLoad.MEDIUM.value == "medium"
        assert SystemLoad.HIGH.value == "high"
        assert SystemLoad.CRITICAL.value == "critical"
    
    def test_rate_limit_algorithm_enum(self):
        """Testa enum RateLimitAlgorithm."""
        assert RateLimitAlgorithm.TOKEN_BUCKET.value == "token_bucket"
        assert RateLimitAlgorithm.LEAKY_BUCKET.value == "leaky_bucket"
        assert RateLimitAlgorithm.SLIDING_WINDOW.value == "sliding_window"
        assert RateLimitAlgorithm.ADAPTIVE.value == "adaptive" 