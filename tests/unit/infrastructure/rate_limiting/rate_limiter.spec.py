from typing import Dict, List, Optional, Any
"""
Testes unitários para o sistema de rate limiting inteligente.
Cobre detecção de padrões, rate limiting adaptativo e middleware.
"""
import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from infrastructure.security.rate_limiting import (
    AdaptiveRateLimiter,
    PatternDetector,
    RequestInfo,
    RateLimitConfig,
    RateLimitStrategy,
    ThreatLevel
)

class TestRateLimitConfig:
    """Testes para configuração de rate limiting."""
    
    def test_default_config(self):
        """Testa configurações padrão."""
        config = RateLimitConfig()
        
        assert config.requests_per_minute == 60
        assert config.requests_per_hour == 1000
        assert config.requests_per_day == 10000
        assert config.burst_limit == 10
        assert config.adaptive_enabled is True
        assert config.anomaly_threshold == 2.0
    
    def test_custom_config(self):
        """Testa configuração customizada."""
        config = RateLimitConfig(
            requests_per_minute=30,
            burst_limit=5,
            adaptive_enabled=False
        )
        
        assert config.requests_per_minute == 30
        assert config.burst_limit == 5
        assert config.adaptive_enabled is False

class TestRequestInfo:
    """Testes para informações de requisição."""
    
    def test_request_info_creation(self):
        """Testa criação de RequestInfo."""
        request = RequestInfo(
            timestamp=time.time(),
            ip="192.168.1.1",
            user_agent="Mozilla/5.0",
            endpoint="/api/test",
            method="GET",
            response_time=0.1,
            status_code=200,
            payload_size=1024
        )
        
        assert request.ip == "192.168.1.1"
        assert request.user_agent == "Mozilla/5.0"
        assert request.endpoint == "/api/test"
        assert request.method == "GET"
        assert request.status_code == 200
        assert request.payload_size == 1024

class TestPatternDetector:
    """Testes para detector de padrões."""
    
    @pytest.fixture
    def detector(self):
        """Fixture para detector de padrões."""
        return PatternDetector()
    
    @pytest.fixture
    def sample_requests(self):
        """Fixture para requisições de exemplo."""
        base_time = time.time()
        requests = []
        
        # Requisições normais
        for index in range(10):
            requests.append(RequestInfo(
                timestamp=base_time + index * 2,  # 2 segundos entre requisições
                ip="192.168.1.1",
                user_agent="Mozilla/5.0",
                endpoint="/api/test",
                method="GET",
                response_time=0.1 + (index * 0.01),
                status_code=200,
                payload_size=100 + index
            ))
        
        return requests
    
    def test_add_request(self, detector, sample_requests):
        """Testa adição de requisições."""
        for request in sample_requests:
            score = detector.add_request(request)
            assert 0.0 <= score <= 1.0
    
    def test_analyze_frequency_normal(self, detector, sample_requests):
        """Testa análise de frequência normal."""
        for request in sample_requests:
            detector.add_request(request)
        
        # Requisições normais devem ter score baixo
        recent_requests = list(detector.patterns["192.168.1.1:/api/test"])[-10:]
        score = detector._analyze_frequency(recent_requests)
        assert score < 0.5  # Score baixo para padrão normal
    
    def test_analyze_frequency_bot_like(self, detector):
        """Testa análise de frequência bot-like."""
        base_time = time.time()
        
        # Requisições muito regulares (bot-like)
        for index in range(20):
            request = RequestInfo(
                timestamp=base_time + index * 1.0,  # Exatamente 1 segundo
                ip="192.168.1.2",
                user_agent="Bot/1.0",
                endpoint="/api/test",
                method="GET",
                response_time=0.1,
                status_code=200,
                payload_size=100
            )
            detector.add_request(request)
        
        recent_requests = list(detector.patterns["192.168.1.2:/api/test"])[-10:]
        score = detector._analyze_frequency(recent_requests)
        assert score > 0.5  # Score alto para padrão suspeito
    
    def test_analyze_time_pattern_normal(self, detector, sample_requests):
        """Testa análise de padrão temporal normal."""
        for request in sample_requests:
            detector.add_request(request)
        
        recent_requests = list(detector.patterns["192.168.1.1:/api/test"])[-10:]
        score = detector._analyze_time_pattern(recent_requests)
        assert score < 0.3  # Score baixo para horários normais
    
    def test_analyze_time_pattern_suspicious(self, detector):
        """Testa análise de padrão temporal suspeito."""
        base_time = time.time()
        
        # Requisições em horários suspeitos (2-6 AM)
        suspicious_hour = 3  # 3 AM
        dt = datetime.fromtimestamp(base_time)
        dt = dt.replace(hour=suspicious_hour, minute=0, second=0, microsecond=0)
        base_time = dt.timestamp()
        
        for index in range(10):
            request = RequestInfo(
                timestamp=base_time + index * 60,  # 1 minuto entre requisições
                ip="192.168.1.3",
                user_agent="Mozilla/5.0",
                endpoint="/api/test",
                method="GET",
                response_time=0.1,
                status_code=200,
                payload_size=100
            )
            detector.add_request(request)
        
        recent_requests = list(detector.patterns["192.168.1.3:/api/test"])[-10:]
        score = detector._analyze_time_pattern(recent_requests)
        assert score > 0.5  # Score alto para horários suspeitos
    
    def test_analyze_payload_pattern_identical(self, detector):
        """Testa análise de payload idêntico."""
        base_time = time.time()
        
        # Payloads idênticos (suspeito)
        for index in range(10):
            request = RequestInfo(
                timestamp=base_time + index,
                ip="192.168.1.4",
                user_agent="Mozilla/5.0",
                endpoint="/api/test",
                method="POST",
                response_time=0.1,
                status_code=200,
                payload_size=1024  # Mesmo tamanho
            )
            detector.add_request(request)
        
        recent_requests = list(detector.patterns["192.168.1.4:/api/test"])[-10:]
        score = detector._analyze_payload_pattern(recent_requests)
        assert score > 0.8  # Score muito alto para payloads idênticos
    
    def test_analyze_user_agent_pattern_suspicious(self, detector):
        """Testa análise de user agent suspeito."""
        base_time = time.time()
        
        # User agents suspeitos
        suspicious_agents = ["Bot/1.0", "Crawler/2.0", "", "python-requests/2.25.1"]
        
        for index, agent in enumerate(suspicious_agents * 3):  # Repete 3 vezes
            request = RequestInfo(
                timestamp=base_time + index,
                ip="192.168.1.5",
                user_agent=agent,
                endpoint="/api/test",
                method="GET",
                response_time=0.1,
                status_code=200,
                payload_size=100
            )
            detector.add_request(request)
        
        recent_requests = list(detector.patterns["192.168.1.5:/api/test"])[-10:]
        score = detector._analyze_user_agent_pattern(recent_requests)
        assert score > 0.5  # Score alto para user agents suspeitos
    
    def test_analyze_response_pattern_errors(self, detector):
        """Testa análise de padrão de resposta com erros."""
        base_time = time.time()
        
        # Muitas requisições com erro
        for index in range(10):
            status_code = 500 if index % 2 == 0 else 200  # Alterna entre erro e sucesso
            request = RequestInfo(
                timestamp=base_time + index,
                ip="192.168.1.6",
                user_agent="Mozilla/5.0",
                endpoint="/api/test",
                method="GET",
                response_time=0.1,
                status_code=status_code,
                payload_size=100
            )
            detector.add_request(request)
        
        recent_requests = list(detector.patterns["192.168.1.6:/api/test"])[-10:]
        score = detector._analyze_response_pattern(recent_requests)
        assert score > 0.4  # Score alto para muitos erros
    
    def test_get_threat_level(self, detector, sample_requests):
        """Testa obtenção de nível de ameaça."""
        for request in sample_requests:
            detector.add_request(request)
        
        # Requisições normais devem ter nível baixo
        threat_level = detector.get_threat_level("192.168.1.1", "/api/test")
        assert threat_level in [ThreatLevel.LOW, ThreatLevel.MEDIUM]

class TestAdaptiveRateLimiter:
    """Testes para rate limiter adaptativo."""
    
    @pytest.fixture
    def rate_limiter(self):
        """Fixture para rate limiter."""
        config = RateLimitConfig(
            requests_per_minute=10,  # Limite baixo para testes
            burst_limit=5,
            cooldown_period=60
        )
        return AdaptiveRateLimiter(config)
    
    @pytest.fixture
    def mock_cache(self):
        """Mock do cache."""
        mock_cache = AsyncMock()
        mock_cache.get.return_value = {}
        mock_cache.set.return_value = True
        return mock_cache
    
    @pytest.mark.asyncio
    async def test_process_request_normal(self, rate_limiter, mock_cache):
        """Testa processamento de requisição normal."""
        with patch('infrastructure.security.rate_limiting.get_cache', return_value=mock_cache):
            request = RequestInfo(
                timestamp=time.time(),
                ip="192.168.1.1",
                user_agent="Mozilla/5.0",
                endpoint="/api/test",
                method="GET",
                response_time=0.1,
                status_code=200,
                payload_size=100
            )
            
            allowed, info = await rate_limiter.process_request(request)
            
            assert allowed is True
            assert 'remaining' in info
            assert 'threat_level' in info
            assert 'anomaly_score' in info
    
    @pytest.mark.asyncio
    async def test_process_request_rate_limited(self, rate_limiter, mock_cache):
        """Testa rate limiting de requisições."""
        with patch('infrastructure.security.rate_limiting.get_cache', return_value=mock_cache):
            # Simula muitas requisições
            for index in range(15):  # Mais que o limite
                request = RequestInfo(
                    timestamp=time.time() + index,
                    ip="192.168.1.2",
                    user_agent="Mozilla/5.0",
                    endpoint="/api/test",
                    method="GET",
                    response_time=0.1,
                    status_code=200,
                    payload_size=100
                )
                
                allowed, info = await rate_limiter.process_request(request)
                
                if index >= 10:  # Após o limite
                    assert allowed is False
                    assert 'remaining' in info
                    assert info['remaining'] == 0
    
    @pytest.mark.asyncio
    async def test_process_request_blacklisted(self, rate_limiter):
        """Testa bloqueio de IP na blacklist."""
        rate_limiter.config.blacklist_ips = ["192.168.1.3"]
        
        request = RequestInfo(
            timestamp=time.time(),
            ip="192.168.1.3",
            user_agent="Mozilla/5.0",
            endpoint="/api/test",
            method="GET",
            response_time=0.1,
            status_code=200,
            payload_size=100
        )
        
        allowed, info = await rate_limiter.process_request(request)
        
        assert allowed is False
        assert info['blocked'] is True
        assert info['reason'] == 'blacklisted'
    
    @pytest.mark.asyncio
    async def test_process_request_whitelisted(self, rate_limiter):
        """Testa bypass de IP na whitelist."""
        rate_limiter.config.whitelist_ips = ["192.168.1.4"]
        
        request = RequestInfo(
            timestamp=time.time(),
            ip="192.168.1.4",
            user_agent="Mozilla/5.0",
            endpoint="/api/test",
            method="GET",
            response_time=0.1,
            status_code=200,
            payload_size=100
        )
        
        allowed, info = await rate_limiter.process_request(request)
        
        assert allowed is True
        assert info['whitelisted'] is True
    
    @pytest.mark.asyncio
    async def test_process_request_critical_threat(self, rate_limiter, mock_cache):
        """Testa bloqueio por ameaça crítica."""
        with patch('infrastructure.security.rate_limiting.get_cache', return_value=mock_cache):
            # Simula padrão muito suspeito
            base_time = time.time()
            
            for index in range(50):  # Muitas requisições muito rápidas
                request = RequestInfo(
                    timestamp=base_time + index * 0.1,  # 0.1 segundo entre requisições
                    ip="192.168.1.5",
                    user_agent="Bot/1.0",
                    endpoint="/api/test",
                    method="GET",
                    response_time=0.01,  # Muito rápido
                    status_code=200,
                    payload_size=1024  # Payload idêntico
                )
                
                allowed, info = await rate_limiter.process_request(request)
                
                if index > 20:  # Após detectar padrão suspeito
                    if not allowed:
                        assert info['blocked'] is True
                        assert info['reason'] == 'critical_threat'
                        break
    
    def test_get_metrics(self, rate_limiter):
        """Testa obtenção de métricas."""
        # Simula algumas operações
        rate_limiter.metrics['total_requests'] = 100
        rate_limiter.metrics['blocked_requests'] = 5
        rate_limiter.metrics['rate_limited_requests'] = 10
        rate_limiter.metrics['anomalies_detected'] = 3
        rate_limiter.metrics['alerts_sent'] = 2
        
        metrics = rate_limiter.get_metrics()
        
        assert metrics['total_requests'] == 100
        assert metrics['block_rate'] == 5.0  # 5%
        assert metrics['rate_limit_rate'] == 10.0  # 10%
        assert metrics['anomaly_rate'] == 3.0  # 3%
        assert metrics['alert_rate'] == 2.0  # 2%
    
    @pytest.mark.asyncio
    async def test_health_check(self, rate_limiter, mock_cache):
        """Testa verificação de saúde."""
        with patch('infrastructure.security.rate_limiting.get_cache', return_value=mock_cache):
            health = await rate_limiter.health_check()
            
            assert health['rate_limiter_healthy'] is True
            assert 'metrics' in health
            assert 'blocked_ips_count' in health

@pytest.mark.asyncio
async def test_rate_limiter_integration():
    """Teste de integração do rate limiter."""
    # Testa fluxo completo
    config = RateLimitConfig(
        requests_per_minute=5,
        burst_limit=3,
        adaptive_enabled=True
    )
    
    rate_limiter = AdaptiveRateLimiter(config)
    
    # Simula requisições normais
    for index in range(3):
        request = RequestInfo(
            timestamp=time.time() + index,
            ip="192.168.1.10",
            user_agent="Mozilla/5.0",
            endpoint="/api/test",
            method="GET",
            response_time=0.1,
            status_code=200,
            payload_size=100
        )
        
        allowed, info = await rate_limiter.process_request(request)
        assert allowed is True
    
    # Simula requisição que excede o limite
    request = RequestInfo(
        timestamp=time.time() + 10,
        ip="192.168.1.10",
        user_agent="Mozilla/5.0",
        endpoint="/api/test",
        method="GET",
        response_time=0.1,
        status_code=200,
        payload_size=100
    )
    
    allowed, info = await rate_limiter.process_request(request)
    assert allowed is False  # Deve ser bloqueada
    
    # Verifica métricas
    metrics = rate_limiter.get_metrics()
    assert metrics['total_requests'] == 4
    assert metrics['rate_limited_requests'] == 1 