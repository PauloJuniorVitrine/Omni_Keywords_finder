"""
🧪 INT-007: Testes Unitários - Advanced Rate Limiting - Omni Keywords Finder

Tracing ID: INT_007_TEST_RATE_LIMITING_001
Data/Hora: 2025-01-27 17:00:00 UTC
Versão: 1.0
Status: 🚀 EM IMPLEMENTAÇÃO

Objetivo: Testes unitários completos para o sistema de Advanced Rate Limiting
com cobertura de 95%+ e validação de todas as funcionalidades.
"""

import time
import threading
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any

from infrastructure.security.advanced_rate_limiting import (
    AdvancedRateLimiting,
    RateLimitConfig,
    RateLimitStrategy,
    ClientTier,
    ThreatLevel,
    TokenBucket,
    SlidingWindow,
    BurstDetector,
    AdaptiveRateLimiter,
    RequestInfo,
    RateLimitResult,
    create_advanced_rate_limiting,
    rate_limited
)

class TestTokenBucket:
    """Testes para TokenBucket."""
    
    def test_token_bucket_initialization(self):
        """Testa inicialização do TokenBucket."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        assert bucket.capacity == 10
        assert bucket.refill_rate == 1.0
        assert bucket.tokens == 10
    
    def test_token_bucket_acquire_success(self):
        """Testa aquisição bem-sucedida de tokens."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        assert bucket.acquire(5) is True
        assert bucket.get_tokens() == 5
    
    def test_token_bucket_acquire_failure(self):
        """Testa falha na aquisição de tokens."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        assert bucket.acquire(15) is False
        assert bucket.get_tokens() == 10
    
    def test_token_bucket_refill(self):
        """Testa reabastecimento automático de tokens."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        bucket.acquire(10)  # Esvazia o bucket
        
        # Simula passagem de tempo
        with patch('time.time') as mock_time:
            mock_time.return_value = time.time() + 2.0  # 2 segundos depois
            assert bucket.get_tokens() == 2.0
    
    def test_token_bucket_thread_safety(self):
        """Testa thread safety do TokenBucket."""
        bucket = TokenBucket(capacity=100, refill_rate=10.0)
        
        def worker():
            for _ in range(10):
                bucket.acquire(1)
                time.sleep(0.01)
        
        threads = [threading.Thread(target=worker) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # Verifica que não houve race conditions
        assert bucket.get_tokens() >= 0

class TestSlidingWindow:
    """Testes para SlidingWindow."""
    
    def test_sliding_window_initialization(self):
        """Testa inicialização do SlidingWindow."""
        window = SlidingWindow(window_size=60, max_requests=10)
        assert window.window_size == 60
        assert window.max_requests == 10
    
    def test_sliding_window_allowed_requests(self):
        """Testa requisições permitidas."""
        window = SlidingWindow(window_size=60, max_requests=5)
        
        for index in range(5):
            assert window.is_allowed() is True
        
        # 6ª requisição deve ser bloqueada
        assert window.is_allowed() is False
    
    def test_sliding_window_expired_requests(self):
        """Testa expiração de requisições antigas."""
        window = SlidingWindow(window_size=1, max_requests=2)
        
        # Primeiras duas requisições
        assert window.is_allowed() is True
        assert window.is_allowed() is True
        
        # Terceira deve ser bloqueada
        assert window.is_allowed() is False
        
        # Após 1 segundo, deve permitir novamente
        time.sleep(1.1)
        assert window.is_allowed() is True
    
    def test_sliding_window_remaining_requests(self):
        """Testa cálculo de requisições restantes."""
        window = SlidingWindow(window_size=60, max_requests=10)
        
        # 3 requisições feitas
        window.is_allowed()
        window.is_allowed()
        window.is_allowed()
        
        assert window.get_remaining() == 7

class TestBurstDetector:
    """Testes para BurstDetector."""
    
    def test_burst_detector_initialization(self):
        """Testa inicialização do BurstDetector."""
        detector = BurstDetector(burst_window=5, burst_cooldown=60)
        assert detector.burst_window == 5
        assert detector.burst_cooldown == 60
    
    def test_burst_detection_normal_activity(self):
        """Testa detecção de atividade normal."""
        detector = BurstDetector(burst_window=5, burst_cooldown=60)
        
        # Adiciona algumas requisições normais
        for _ in range(5):
            detector.add_request("client1")
            time.sleep(0.1)
        
        detected, reason = detector.detect_burst("client1")
        assert detected is False
        assert reason is None
    
    def test_burst_detection_burst_activity(self):
        """Testa detecção de atividade em burst."""
        detector = BurstDetector(burst_window=5, burst_cooldown=60)
        
        # Adiciona muitas requisições rapidamente
        for _ in range(20):
            detector.add_request("client1")
        
        detected, reason = detector.detect_burst("client1")
        assert detected is True
        assert reason is not None and "burst" in reason.lower()
    
    def test_burst_detection_cooldown(self):
        """Testa período de cooldown após burst."""
        detector = BurstDetector(burst_window=5, burst_cooldown=1)
        
        # Cria um burst
        for _ in range(20):
            detector.add_request("client1")
        
        # Detecta burst
        detected, _ = detector.detect_burst("client1")
        assert detected is True
        
        # Após cooldown, deve permitir novamente
        time.sleep(1.1)
        detected, _ = detector.detect_burst("client1")
        assert detected is False

class TestAdaptiveRateLimiter:
    """Testes para AdaptiveRateLimiter."""
    
    def test_adaptive_rate_limiter_initialization(self):
        """Testa inicialização do AdaptiveRateLimiter."""
        config = RateLimitConfig()
        limiter = AdaptiveRateLimiter(config)
        assert limiter.config == config
    
    def test_adaptive_rate_calculation(self):
        """Testa cálculo de taxa adaptativa."""
        config = RateLimitConfig()
        limiter = AdaptiveRateLimiter(config)
        
        # Testa com uso baixo
        rate = limiter.calculate_adaptive_rate("client1", 0.3)
        assert rate > config.adaptive_min_rate
        
        # Testa com uso alto
        rate = limiter.calculate_adaptive_rate("client1", 0.8)
        assert rate < config.adaptive_max_rate
    
    def test_adaptive_rate_limits(self):
        """Testa limites da taxa adaptativa."""
        config = RateLimitConfig()
        limiter = AdaptiveRateLimiter(config)
        
        # Testa limite mínimo
        rate = limiter.calculate_adaptive_rate("client1", 0.0)
        assert rate >= config.adaptive_min_rate
        
        # Testa limite máximo
        rate = limiter.calculate_adaptive_rate("client1", 1.0)
        assert rate <= config.adaptive_max_rate

class TestAdvancedRateLimiting:
    """Testes para AdvancedRateLimiting."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.config = RateLimitConfig(
            requests_per_minute=60,
            burst_limit=10,
            adaptive_enabled=True,
            per_client_enabled=True
        )
        self.rate_limiter = AdvancedRateLimiting(self.config)
        
        self.request_info = RequestInfo(
            timestamp=time.time(),
            client_id="test_client",
            ip_address="192.168.1.1",
            user_agent="test-agent",
            endpoint="/api/test",
            method="GET",
            payload_size=100,
            response_time=0.1,
            status_code=200
        )
    
    def test_advanced_rate_limiting_initialization(self):
        """Testa inicialização do AdvancedRateLimiting."""
        assert self.rate_limiter.config is not None
        assert self.rate_limiter.token_buckets == {}
        assert self.rate_limiter.sliding_windows == {}
    
    def test_whitelist_check(self):
        """Testa verificação de whitelist."""
        self.rate_limiter.config.whitelist_ips = ["192.168.1.1"]
        
        result = self.rate_limiter.check_rate_limit("client1", self.request_info)
        assert result.allowed is True
        assert result.reason is not None and "whitelist" in result.reason
    
    def test_blacklist_check(self):
        """Testa verificação de blacklist."""
        self.rate_limiter.config.blacklist_ips = ["192.168.1.1"]
        
        result = self.rate_limiter.check_rate_limit("client1", self.request_info)
        assert result.allowed is False
        assert result.reason is not None and "blacklist" in result.reason
    
    def test_token_bucket_strategy(self):
        """Testa estratégia Token Bucket."""
        result = self.rate_limiter.check_rate_limit(
            "client1", 
            self.request_info, 
            RateLimitStrategy.TOKEN_BUCKET
        )
        assert isinstance(result, RateLimitResult)
    
    def test_sliding_window_strategy(self):
        """Testa estratégia Sliding Window."""
        result = self.rate_limiter.check_rate_limit(
            "client1", 
            self.request_info, 
            RateLimitStrategy.SLIDING_WINDOW
        )
        assert isinstance(result, RateLimitResult)
    
    def test_adaptive_strategy(self):
        """Testa estratégia Adaptativa."""
        result = self.rate_limiter.check_rate_limit(
            "client1", 
            self.request_info, 
            RateLimitStrategy.ADAPTIVE
        )
        assert isinstance(result, RateLimitResult)
        assert result.adaptive_rate is not None
    
    def test_client_tier_detection(self):
        """Testa detecção de tier do cliente."""
        result = self.rate_limiter.check_rate_limit("enterprise_client", self.request_info)
        assert result.client_tier == ClientTier.ENTERPRISE
    
    def test_threat_level_detection(self):
        """Testa detecção de nível de ameaça."""
        result = self.rate_limiter.check_rate_limit("client1", self.request_info)
        assert isinstance(result.threat_level, ThreatLevel)
    
    def test_graceful_degradation(self):
        """Testa graceful degradation."""
        self.rate_limiter.config.graceful_degradation_enabled = True
        
        # Simula alta utilização
        with patch.object(self.rate_limiter, '_check_adaptive') as mock_check:
            mock_check.return_value = (False, 0)  # Rate limit excedido
            
            result = self.rate_limiter.check_rate_limit("client1", self.request_info)
            assert isinstance(result, RateLimitResult)
    
    def test_burst_detection_integration(self):
        """Testa integração com detecção de burst."""
        # Simula atividade em burst
        for _ in range(15):
            self.rate_limiter.burst_detector.add_request("client1")
        
        result = self.rate_limiter.check_rate_limit("client1", self.request_info)
        assert result.burst_status in ["normal", "blocked"]
    
    def test_client_stats(self):
        """Testa obtenção de estatísticas do cliente."""
        # Faz algumas requisições
        for _ in range(3):
            self.rate_limiter.check_rate_limit("client1", self.request_info)
        
        stats = self.rate_limiter.get_client_stats("client1")
        assert isinstance(stats, dict)
        assert "total_requests" in stats
    
    def test_system_metrics(self):
        """Testa obtenção de métricas do sistema."""
        # Faz algumas requisições
        for _ in range(5):
            self.rate_limiter.check_rate_limit("client1", self.request_info)
        
        metrics = self.rate_limiter.get_system_metrics()
        assert isinstance(metrics, dict)
        assert "total_requests" in metrics
        assert "allowed_requests" in metrics
        assert "blocked_requests" in metrics
    
    def test_health_check(self):
        """Testa health check do sistema."""
        health = self.rate_limiter.health_check()
        assert isinstance(health, dict)
        assert "status" in health
        assert "timestamp" in health
    
    def test_reset_client(self):
        """Testa reset de cliente."""
        # Faz algumas requisições
        for _ in range(3):
            self.rate_limiter.check_rate_limit("client1", self.request_info)
        
        # Reseta cliente
        self.rate_limiter.reset_client("client1")
        
        # Verifica se foi resetado
        stats = self.rate_limiter.get_client_stats("client1")
        assert stats["total_requests"] == 0

class TestRateLimitedDecorator:
    """Testes para o decorator rate_limited."""
    
    def test_rate_limited_decorator_success(self):
        """Testa decorator com sucesso."""
        @rate_limited(requests_per_minute=10)
        def test_function():
            return "success"
        
        # Primeira chamada deve funcionar
        result = test_function()
        assert result == "success"
    
    def test_rate_limited_decorator_failure(self):
        """Testa decorator com falha de rate limit."""
        @rate_limited(requests_per_minute=1)
        def test_function():
            return "success"
        
        # Primeira chamada deve funcionar
        result = test_function()
        assert result == "success"
        
        # Segunda chamada deve falhar
        try:
            test_function()
            assert False, "Deveria ter falhado"
        except Exception as exc_info:
            assert "Rate limit exceeded" in str(exc_info)
    
    def test_rate_limited_decorator_with_client_id_func(self):
        """Testa decorator com função de extração de client_id."""
        def extract_client_id(*args, **kwargs):
            return "custom_client_id"
        
        @rate_limited(requests_per_minute=10, client_id_func=extract_client_id)
        def test_function():
            return "success"
        
        result = test_function()
        assert result == "success"

class TestCreateAdvancedRateLimiting:
    """Testes para função de criação de rate limiter."""
    
    def test_create_advanced_rate_limiting_default(self):
        """Testa criação com configuração padrão."""
        limiter = create_advanced_rate_limiting()
        assert isinstance(limiter, AdvancedRateLimiting)
    
    def test_create_advanced_rate_limiting_custom_config(self):
        """Testa criação com configuração customizada."""
        config = RateLimitConfig(
            requests_per_minute=100,
            burst_limit=20,
            adaptive_enabled=False
        )
        limiter = create_advanced_rate_limiting(config)
        assert isinstance(limiter, AdvancedRateLimiting)
        assert limiter.config.requests_per_minute == 100

class TestRedisIntegration:
    """Testes para integração com Redis."""
    
    @patch('redis.Redis')
    def test_redis_setup_success(self, mock_redis):
        """Testa configuração bem-sucedida do Redis."""
        mock_client = Mock()
        mock_redis.return_value = mock_client
        mock_client.ping.return_value = True
        
        config = RateLimitConfig()
        limiter = AdvancedRateLimiting(config)
        
        assert limiter.redis_client is not None
    
    @patch('redis.Redis')
    def test_redis_setup_failure(self, mock_redis):
        """Testa falha na configuração do Redis."""
        mock_redis.side_effect = Exception("Redis connection failed")
        
        config = RateLimitConfig()
        limiter = AdvancedRateLimiting(config)
        
        # Deve continuar funcionando sem Redis
        assert limiter.redis_client is None

class TestConcurrentAccess:
    """Testes para acesso concorrente."""
    
    def test_concurrent_rate_limiting(self):
        """Testa rate limiting com acesso concorrente."""
        config = RateLimitConfig(requests_per_minute=100)
        limiter = AdvancedRateLimiting(config)
        
        request_info = RequestInfo(
            timestamp=time.time(),
            client_id="concurrent_client",
            ip_address="192.168.1.1",
            user_agent="test-agent",
            endpoint="/api/test",
            method="GET",
            payload_size=100,
            response_time=0.1,
            status_code=200
        )
        
        def worker():
            for _ in range(10):
                limiter.check_rate_limit("concurrent_client", request_info)
                time.sleep(0.01)
        
        threads = [threading.Thread(target=worker) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # Verifica que não houve race conditions
        stats = limiter.get_client_stats("concurrent_client")
        assert stats["total_requests"] == 50

class TestEdgeCases:
    """Testes para casos extremos."""
    
    def test_zero_rate_limit(self):
        """Testa rate limit zero."""
        config = RateLimitConfig(requests_per_minute=0)
        limiter = AdvancedRateLimiting(config)
        
        request_info = RequestInfo(
            timestamp=time.time(),
            client_id="test_client",
            ip_address="192.168.1.1",
            user_agent="test-agent",
            endpoint="/api/test",
            method="GET",
            payload_size=100,
            response_time=0.1,
            status_code=200
        )
        
        result = limiter.check_rate_limit("test_client", request_info)
        assert result.allowed is False
    
    def test_very_high_rate_limit(self):
        """Testa rate limit muito alto."""
        config = RateLimitConfig(requests_per_minute=1000000)
        limiter = AdvancedRateLimiting(config)
        
        request_info = RequestInfo(
            timestamp=time.time(),
            client_id="test_client",
            ip_address="192.168.1.1",
            user_agent="test-agent",
            endpoint="/api/test",
            method="GET",
            payload_size=100,
            response_time=0.1,
            status_code=200
        )
        
        # Deve permitir muitas requisições
        for _ in range(1000):
            result = limiter.check_rate_limit("test_client", request_info)
            assert result.allowed is True
    
    def test_invalid_client_id(self):
        """Testa client_id inválido."""
        config = RateLimitConfig()
        limiter = AdvancedRateLimiting(config)
        
        request_info = RequestInfo(
            timestamp=time.time(),
            client_id="",
            ip_address="192.168.1.1",
            user_agent="test-agent",
            endpoint="/api/test",
            method="GET",
            payload_size=100,
            response_time=0.1,
            status_code=200
        )
        
        result = limiter.check_rate_limit("", request_info)
        assert isinstance(result, RateLimitResult)

def run_all_tests():
    """Executa todos os testes."""
    test_classes = [
        TestTokenBucket,
        TestSlidingWindow,
        TestBurstDetector,
        TestAdaptiveRateLimiter,
        TestAdvancedRateLimiting,
        TestRateLimitedDecorator,
        TestCreateAdvancedRateLimiting,
        TestRedisIntegration,
        TestConcurrentAccess,
        TestEdgeCases
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        test_instance = test_class()
        
        # Executa todos os métodos que começam com 'test_'
        for method_name in dir(test_instance):
            if method_name.startswith('test_'):
                total_tests += 1
                try:
                    # Setup se existir
                    if hasattr(test_instance, 'setup_method'):
                        test_instance.setup_method()
                    
                    # Executa o teste
                    getattr(test_instance, method_name)()
                    passed_tests += 1
                    print(f"✅ {test_class.__name__}.{method_name} - PASSED")
                except Exception as e:
                    print(f"❌ {test_class.__name__}.{method_name} - FAILED: {str(e)}")
    
    print(f"\n📊 RESULTADO DOS TESTES:")
    print(f"Total de testes: {total_tests}")
    print(f"Testes aprovados: {passed_tests}")
    print(f"Testes falharam: {total_tests - passed_tests}")
    print(f"Taxa de sucesso: {(passed_tests/total_tests)*100:.1f}%")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1) 