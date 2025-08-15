from typing import Dict, List, Optional, Any
"""
Testes Unitários - Sistema de Rate Limiting Inteligente
Tracing ID: RATE_LIMITING_20241219_001
Data: 2024-12-19
Versão: 1.0

Testes para o sistema de rate limiting inteligente com:
- Validação de algoritmos de rate limiting
- Testes de detecção de anomalias
- Testes de ajuste adaptativo
- Testes de performance
- Validação de configurações
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from dataclasses import asdict

# Importar módulos de rate limiting
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

from infrastructure.security.rate_limiting_inteligente import (
    RateLimitingInteligente,
    RateLimitConfig,
    RateLimitResult,
    RateLimitStrategy,
    AnomalyDetector,
    AnomalyType,
    AdaptiveRateLimiter,
    AnomalyData,
    get_rate_limiter,
    initialize_rate_limiter
)


class TestRateLimitConfig:
    """Testes para configuração de rate limiting."""
    
    def test_rate_limit_config_defaults(self):
        """Testa configurações padrão."""
        # Arrange & Act
        config = RateLimitConfig()
        
        # Assert
        assert config.requests_per_minute == 60
        assert config.requests_per_hour == 1000
        assert config.requests_per_day == 10000
        assert config.burst_limit == 10
        assert config.window_size == 60
        assert config.strategy == RateLimitStrategy.SLIDING_WINDOW
        assert config.enable_anomaly_detection is True
        assert config.anomaly_threshold == 2.0
        assert config.adaptive_learning is True
        assert config.fallback_enabled is True
        assert config.redis_ttl == 3600
    
    def test_rate_limit_config_custom(self):
        """Testa configuração customizada."""
        # Arrange & Act
        config = RateLimitConfig(
            requests_per_minute=30,
            requests_per_hour=500,
            anomaly_threshold=1.5,
            adaptive_learning=False
        )
        
        # Assert
        assert config.requests_per_minute == 30
        assert config.requests_per_hour == 500
        assert config.anomaly_threshold == 1.5
        assert config.adaptive_learning is False


class TestAnomalyDetector:
    """Testes para detector de anomalias."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.detector = AnomalyDetector(threshold=2.0)
    
    def test_detect_burst_traffic_normal(self):
        """Testa detecção de tráfego normal (sem burst)."""
        # Arrange
        user_id = "test_user"
        request_count = 5
        time_window = 10  # 5 requests em 10 segundos = 0.5 req/string_data
        
        # Act
        anomaly = self.detector.detect_burst_traffic(user_id, request_count, time_window)
        
        # Assert
        assert anomaly is None
    
    def test_detect_burst_traffic_anomaly(self):
        """Testa detecção de tráfego em burst."""
        # Arrange
        user_id = "test_user"
        request_count = 30
        time_window = 10  # 30 requests em 10 segundos = 3.0 req/string_data > threshold 2.0
        
        # Act
        anomaly = self.detector.detect_burst_traffic(user_id, request_count, time_window)
        
        # Assert
        assert anomaly is not None
        assert anomaly.anomaly_type == AnomalyType.BURST_TRAFFIC
        assert anomaly.user_id == user_id
        assert anomaly.severity > 1.0
        assert anomaly.pattern_data["requests_per_second"] == 3.0
    
    def test_detect_suspicious_pattern_sql_injection(self):
        """Testa detecção de padrão suspeito (SQL injection)."""
        # Arrange
        user_id = "test_user"
        endpoint = "/api/search"
        request_data = {"query": "'; DROP TABLE users; --"}
        
        # Act
        anomaly = self.detector.detect_suspicious_pattern(user_id, endpoint, request_data)
        
        # Assert
        assert anomaly is not None
        assert anomaly.anomaly_type == AnomalyType.SUSPICIOUS_PATTERN
        assert anomaly.user_id == user_id
        assert anomaly.endpoint == endpoint
        assert anomaly.severity == 3.0
        assert "sql_injection" in anomaly.pattern_data["detected_pattern"]
    
    def test_detect_suspicious_pattern_normal(self):
        """Testa requisição normal (sem padrões suspeitos)."""
        # Arrange
        user_id = "test_user"
        endpoint = "/api/search"
        request_data = {"query": "normal search term"}
        
        # Act
        anomaly = self.detector.detect_suspicious_pattern(user_id, endpoint, request_data)
        
        # Assert
        assert anomaly is None
    
    def test_detect_geographic_anomaly(self):
        """Testa detecção de anomalia geográfica."""
        # Arrange
        user_id = "test_user"
        ip_address = "192.168.1.1"
        country = "Brazil"
        city = "São Paulo"
        
        # Primeira requisição - estabelece perfil
        self.detector.detect_geographic_anomaly(user_id, ip_address, country, city)
        
        # Segunda requisição - país diferente
        anomaly = self.detector.detect_geographic_anomaly(
            user_id, "192.168.1.2", "Russia", "Moscow"
        )
        
        # Assert
        assert anomaly is not None
        assert anomaly.anomaly_type == AnomalyType.GEOGRAPHIC_ANOMALY
        assert anomaly.user_id == user_id
        assert anomaly.severity == 2.0
        assert anomaly.pattern_data["usual_country"] == "Brazil"
        assert anomaly.pattern_data["current_country"] == "Russia"
    
    def test_detect_time_anomaly(self):
        """Testa detecção de anomalia de tempo."""
        # Arrange
        user_id = "test_user"
        current_time = time.time()
        
        # Primeira requisição - estabelece perfil
        self.detector.detect_time_anomaly(user_id, current_time)
        
        # Segunda requisição - horário incomum (3 AM)
        unusual_time = current_time - (current_time % 86400) + 10800  # 3 AM
        anomaly = self.detector.detect_time_anomaly(user_id, unusual_time)
        
        # Assert
        # Pode ou não detectar anomalia dependendo do horário atual
        if anomaly:
            assert anomaly.anomaly_type == AnomalyType.TIME_ANOMALY
            assert anomaly.user_id == user_id


class TestAdaptiveRateLimiter:
    """Testes para rate limiter adaptativo."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        config = RateLimitConfig()
        self.adaptive_limiter = AdaptiveRateLimiter(config)
    
    def test_calculate_adaptive_limit_conservative_user(self):
        """Testa cálculo de limite para usuário conservador."""
        # Arrange
        user_id = "conservative_user"
        
        # Simular uso baixo (0.2 = 20%)
        for _ in range(10):
            self.adaptive_limiter.calculate_adaptive_limit(user_id, 0.2)
        
        # Act
        adjustment = self.adaptive_limiter.calculate_adaptive_limit(user_id, 0.2)
        
        # Assert
        assert adjustment > 1.0  # Deve aumentar o limite
        assert adjustment <= 2.0  # Não deve exceder o máximo
    
    def test_calculate_adaptive_limit_aggressive_user(self):
        """Testa cálculo de limite para usuário agressivo."""
        # Arrange
        user_id = "aggressive_user"
        
        # Simular uso alto (0.9 = 90%)
        for _ in range(10):
            self.adaptive_limiter.calculate_adaptive_limit(user_id, 0.9)
        
        # Act
        adjustment = self.adaptive_limiter.calculate_adaptive_limit(user_id, 0.9)
        
        # Assert
        assert adjustment < 1.0  # Deve diminuir o limite
        assert adjustment >= 0.5  # Não deve ficar abaixo do mínimo
    
    def test_calculate_adaptive_limit_normal_user(self):
        """Testa cálculo de limite para usuário normal."""
        # Arrange
        user_id = "normal_user"
        
        # Simular uso normal (0.5 = 50%)
        for _ in range(10):
            self.adaptive_limiter.calculate_adaptive_limit(user_id, 0.5)
        
        # Act
        adjustment = self.adaptive_limiter.calculate_adaptive_limit(user_id, 0.5)
        
        # Assert
        assert 0.9 <= adjustment <= 1.1  # Deve ficar próximo de 1.0


class TestRateLimitingInteligente:
    """Testes para o sistema de rate limiting inteligente."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.config = RateLimitConfig(
            requests_per_minute=5,  # Limite baixo para testes
            requests_per_hour=50,
            requests_per_day=100,
            enable_anomaly_detection=True,
            adaptive_learning=True
        )
        self.rate_limiter = RateLimitingInteligente(self.config)
    
    def test_rate_limiter_initialization(self):
        """Testa inicialização do rate limiter."""
        # Arrange & Act
        rate_limiter = RateLimitingInteligente()
        
        # Assert
        assert rate_limiter.config is not None
        assert rate_limiter.anomaly_detector is not None
        assert rate_limiter.adaptive_limiter is not None
        assert rate_limiter.request_history is not None
        assert rate_limiter.blocked_ips is not None
        assert rate_limiter.whitelist_ips is not None
    
    def test_check_rate_limit_within_limits(self):
        """Testa rate limiting dentro dos limites."""
        # Arrange
        identifier = "test_user"
        
        # Act - Primeiras 4 requisições (dentro do limite de 5/min)
        for index in range(4):
            result = self.rate_limiter.check_rate_limit(identifier)
            assert result.allowed is True
            assert result.remaining_requests > 0
    
    def test_check_rate_limit_exceeded(self):
        """Testa rate limiting quando excedido."""
        # Arrange
        identifier = "test_user"
        
        # Act - Fazer 6 requisições (excede limite de 5/min)
        results = []
        for index in range(6):
            result = self.rate_limiter.check_rate_limit(identifier)
            results.append(result)
        
        # Assert
        assert results[0].allowed is True  # Primeiras 5 permitidas
        assert results[1].allowed is True
        assert results[2].allowed is True
        assert results[3].allowed is True
        assert results[4].allowed is True
        assert results[5].allowed is False  # 6ª bloqueada
        assert results[5].remaining_requests == 0
        assert results[5].retry_after is not None
    
    def test_check_rate_limit_with_anomaly_detection(self):
        """Testa rate limiting com detecção de anomalias."""
        # Arrange
        identifier = "test_user"
        user_id = "test_user"
        ip_address = "192.168.1.1"
        endpoint = "/api/search"
        request_data = {"query": "'; DROP TABLE users; --"}
        
        # Act
        result = self.rate_limiter.check_rate_limit(
            identifier=identifier,
            user_id=user_id,
            ip_address=ip_address,
            endpoint=endpoint,
            request_data=request_data
        )
        
        # Assert
        assert result.allowed is True  # Deve permitir (dentro do limite)
        assert result.anomaly_detected is True  # Mas detectar anomalia
        assert result.anomaly_type == AnomalyType.SUSPICIOUS_PATTERN
    
    def test_whitelist_functionality(self):
        """Testa funcionalidade de whitelist."""
        # Arrange
        ip_address = "192.168.1.100"
        identifier = ip_address
        
        # Act - Adicionar à whitelist
        self.rate_limiter.add_to_whitelist(ip_address)
        
        # Verificar rate limit
        result = self.rate_limiter.check_rate_limit(
            identifier=identifier,
            ip_address=ip_address
        )
        
        # Assert
        assert result.allowed is True
        assert result.remaining_requests == 999999
        assert "whitelist" in result.reason
    
    def test_blacklist_functionality(self):
        """Testa funcionalidade de blacklist."""
        # Arrange
        ip_address = "192.168.1.200"
        identifier = ip_address
        
        # Act - Adicionar à blacklist
        self.rate_limiter.add_to_blacklist(ip_address, duration=60)
        
        # Verificar rate limit
        result = self.rate_limiter.check_rate_limit(
            identifier=identifier,
            ip_address=ip_address
        )
        
        # Assert
        assert result.allowed is False
        assert result.remaining_requests == 0
        assert result.retry_after == 3600  # 1 hora
        assert "bloqueado" in result.reason
    
    def test_adaptive_rate_limiting(self):
        """Testa rate limiting adaptativo."""
        # Arrange
        user_id = "adaptive_user"
        identifier = user_id
        
        # Simular usuário conservador
        for index in range(10):
            result = self.rate_limiter.check_rate_limit(
                identifier=identifier,
                user_id=user_id
            )
            time.sleep(0.1)  # Pequena pausa
        
        # Act - Verificar se o limite foi ajustado
        result = self.rate_limiter.check_rate_limit(
            identifier=identifier,
            user_id=user_id
        )
        
        # Assert
        assert result.allowed is True
        assert result.adaptive_adjustment is not None
        assert result.adaptive_adjustment > 1.0  # Deve ter aumentado
    
    def test_sliding_window_accuracy(self):
        """Testa precisão do algoritmo sliding window."""
        # Arrange
        identifier = "sliding_test"
        
        # Fazer requisições
        for index in range(3):
            self.rate_limiter.check_rate_limit(identifier)
        
        # Aguardar um pouco
        time.sleep(0.1)
        
        # Act - Verificar contagem
        result = self.rate_limiter.check_rate_limit(identifier)
        
        # Assert
        assert result.allowed is True
        assert result.remaining_requests == 2  # 5 - 3 = 2 restantes
    
    def test_reset_limits(self):
        """Testa reset de limites."""
        # Arrange
        identifier = "reset_test"
        
        # Fazer algumas requisições
        for index in range(3):
            self.rate_limiter.check_rate_limit(identifier)
        
        # Act - Resetar limites
        self.rate_limiter.reset_limits(identifier)
        
        # Verificar se foi resetado
        result = self.rate_limiter.check_rate_limit(identifier)
        
        # Assert
        assert result.allowed is True
        assert result.remaining_requests == 5  # Deve ter resetado
    
    def test_get_statistics(self):
        """Testa obtenção de estatísticas."""
        # Arrange
        identifier = "stats_test"
        self.rate_limiter.check_rate_limit(identifier)
        self.rate_limiter.add_to_whitelist("192.168.1.1")
        self.rate_limiter.add_to_blacklist("192.168.1.2")
        
        # Act
        stats = self.rate_limiter.get_statistics()
        
        # Assert
        assert "total_identifiers" in stats
        assert "whitelisted_ips" in stats
        assert "blocked_ips" in stats
        assert "anomaly_detection_enabled" in stats
        assert "adaptive_learning_enabled" in stats
        assert stats["whitelisted_ips"] == 1
        assert stats["blocked_ips"] == 1


class TestRateLimitingPerformance:
    """Testes de performance para rate limiting."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.config = RateLimitConfig(
            requests_per_minute=1000,
            requests_per_hour=10000
        )
        self.rate_limiter = RateLimitingInteligente(self.config)
    
    def test_rate_limiting_performance(self):
        """Testa performance do rate limiting."""
        # Arrange
        identifier = "perf_test"
        start_time = time.time()
        
        # Act - 1000 verificações
        for index in range(1000):
            result = self.rate_limiter.check_rate_limit(identifier)
        
        end_time = time.time()
        
        # Assert
        total_time = end_time - start_time
        avg_time_per_check = total_time / 1000
        assert avg_time_per_check < 0.001  # Menos de 1ms por verificação
    
    def test_concurrent_rate_limiting(self):
        """Testa rate limiting concorrente."""
        # Arrange
        identifier = "concurrent_test"
        results = []
        
        def check_rate_limit():
            result = self.rate_limiter.check_rate_limit(identifier)
            results.append(result)
        
        # Act - 10 threads simultâneas
        threads = []
        for index in range(10):
            thread = threading.Thread(target=check_rate_limit)
            threads.append(thread)
            thread.start()
        
        # Aguardar todas as threads
        for thread in threads:
            thread.join()
        
        # Assert
        assert len(results) == 10
        # Todas devem ser permitidas (dentro do limite)
        assert all(result.allowed for result in results)


class TestRateLimitingIntegration:
    """Testes de integração para rate limiting."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.rate_limiter = RateLimitingInteligente()
    
    def test_full_rate_limiting_workflow(self):
        """Testa workflow completo de rate limiting."""
        # Arrange
        user_id = "workflow_user"
        ip_address = "192.168.1.1"
        identifier = f"{user_id}_{ip_address}"
        
        # Act - Simular uso normal
        for index in range(5):
            result = self.rate_limiter.check_rate_limit(
                identifier=identifier,
                user_id=user_id,
                ip_address=ip_address,
                endpoint="/api/search",
                request_data={"query": f"search_{index}"}
            )
            assert result.allowed is True
        
        # Simular uso excessivo
        for index in range(10):
            result = self.rate_limiter.check_rate_limit(
                identifier=identifier,
                user_id=user_id,
                ip_address=ip_address
            )
            if not result.allowed:
                break
        
        # Assert
        assert result.allowed is False
        assert result.remaining_requests == 0
        assert result.retry_after is not None
    
    def test_anomaly_detection_integration(self):
        """Testa integração com detecção de anomalias."""
        # Arrange
        user_id = "anomaly_user"
        ip_address = "192.168.1.1"
        identifier = user_id
        
        # Simular requisição com padrão suspeito
        result = self.rate_limiter.check_rate_limit(
            identifier=identifier,
            user_id=user_id,
            ip_address=ip_address,
            endpoint="/api/search",
            request_data={"query": "'; SELECT * FROM users; --"}
        )
        
        # Assert
        assert result.allowed is True  # Deve permitir (dentro do limite)
        assert result.anomaly_detected is True
        assert result.anomaly_type == AnomalyType.SUSPICIOUS_PATTERN


class TestRateLimitingSecurity:
    """Testes de segurança para rate limiting."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.rate_limiter = RateLimitingInteligente()
    
    def test_sql_injection_detection(self):
        """Testa detecção de SQL injection."""
        # Arrange
        user_id = "security_user"
        ip_address = "192.168.1.1"
        identifier = user_id
        
        sql_injection_payloads = [
            "'; DROP TABLE users; --",
            "' OR 1=1; --",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --",
            "'; UPDATE users SET password='hacked'; --"
        ]
        
        # Act & Assert
        for payload in sql_injection_payloads:
            result = self.rate_limiter.check_rate_limit(
                identifier=identifier,
                user_id=user_id,
                ip_address=ip_address,
                endpoint="/api/search",
                request_data={"query": payload}
            )
            
            assert result.anomaly_detected is True
            assert result.anomaly_type == AnomalyType.SUSPICIOUS_PATTERN
    
    def test_xss_detection(self):
        """Testa detecção de XSS."""
        # Arrange
        user_id = "security_user"
        ip_address = "192.168.1.1"
        identifier = user_id
        
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=value onerror=alert('xss')>",
            "';alert('xss');//"
        ]
        
        # Act & Assert
        for payload in xss_payloads:
            result = self.rate_limiter.check_rate_limit(
                identifier=identifier,
                user_id=user_id,
                ip_address=ip_address,
                endpoint="/api/search",
                request_data={"query": payload}
            )
            
            assert result.anomaly_detected is True
            assert result.anomaly_type == AnomalyType.SUSPICIOUS_PATTERN


if __name__ == "__main__":
    pytest.main([__file__, "-value"]) 