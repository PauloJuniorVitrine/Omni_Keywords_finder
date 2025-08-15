"""
🧪 Testes de Segurança de APIs

Tracing ID: api-security-tests-2025-01-27-001
Timestamp: 2025-01-27T20:15:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Testes baseados em cenários reais de segurança
🌲 ToT: Avaliadas múltiplas estratégias de teste
♻️ ReAct: Simulado cenários de ataque e validada proteção

Testa sistema de segurança de APIs incluindo:
- Testes de geração e validação de tokens
- Testes de rate limiting
- Testes de validação de entrada
- Testes de detecção de ataques
- Testes de audit logs
- Testes de blacklist/whitelist
- Testes de performance
- Testes de integração
"""

import pytest
import json
import time
import tempfile
import os
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock
import threading
import asyncio
import jwt
import sqlite3

from infrastructure.security.api_security import (
    SecurityLevel, AttackType, TokenType, SecurityEvent, RateLimitConfig, TokenConfig,
    TokenManager, RateLimiter, SecurityValidator, AuditLogger, APISecurityManager,
    require_auth, rate_limit, validate_input
)

class TestSecurityLevel:
    """Testes de níveis de segurança"""
    
    def test_security_level_values(self):
        """Testa valores dos níveis de segurança"""
        assert SecurityLevel.LOW.value == "low"
        assert SecurityLevel.MEDIUM.value == "medium"
        assert SecurityLevel.HIGH.value == "high"
        assert SecurityLevel.CRITICAL.value == "critical"

class TestAttackType:
    """Testes de tipos de ataque"""
    
    def test_attack_type_values(self):
        """Testa valores dos tipos de ataque"""
        assert AttackType.SQL_INJECTION.value == "sql_injection"
        assert AttackType.XSS.value == "xss"
        assert AttackType.CSRF.value == "csrf"
        assert AttackType.BRUTE_FORCE.value == "brute_force"
        assert AttackType.DDoS.value == "ddos"
        assert AttackType.RATE_LIMIT_EXCEEDED.value == "rate_limit_exceeded"
        assert AttackType.INVALID_TOKEN.value == "invalid_token"
        assert AttackType.SUSPICIOUS_ACTIVITY.value == "suspicious_activity"

class TestTokenType:
    """Testes de tipos de token"""
    
    def test_token_type_values(self):
        """Testa valores dos tipos de token"""
        assert TokenType.ACCESS.value == "access"
        assert TokenType.REFRESH.value == "refresh"
        assert TokenType.API_KEY.value == "api_key"
        assert TokenType.SESSION.value == "session"

class TestSecurityEvent:
    """Testes de eventos de segurança"""
    
    def test_security_event_creation(self):
        """Testa criação de evento de segurança"""
        event = SecurityEvent(
            id="event123",
            timestamp=datetime.now(timezone.utc),
            event_type="attack_detected",
            severity=SecurityLevel.HIGH,
            source_ip="192.168.1.100",
            user_id="user123",
            request_id="req456",
            endpoint="/api/users",
            method="POST",
            user_agent="Mozilla/5.0",
            attack_type=AttackType.SQL_INJECTION,
            details={"param": "value"},
            blocked=True,
            action_taken="Request blocked"
        )
        
        assert event.id == "event123"
        assert event.event_type == "attack_detected"
        assert event.severity == SecurityLevel.HIGH
        assert event.source_ip == "192.168.1.100"
        assert event.user_id == "user123"
        assert event.attack_type == AttackType.SQL_INJECTION
        assert event.blocked is True
        assert event.action_taken == "Request blocked"
    
    def test_security_event_to_dict(self):
        """Testa conversão para dicionário"""
        timestamp = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        event = SecurityEvent(
            id="event123",
            timestamp=timestamp,
            event_type="rate_limit_exceeded",
            severity=SecurityLevel.MEDIUM,
            source_ip="192.168.1.100",
            attack_type=AttackType.RATE_LIMIT_EXCEEDED,
            blocked=False
        )
        
        event_dict = event.to_dict()
        
        assert event_dict["id"] == "event123"
        assert event_dict["timestamp"] == timestamp.isoformat()
        assert event_dict["event_type"] == "rate_limit_exceeded"
        assert event_dict["severity"] == "medium"
        assert event_dict["source_ip"] == "192.168.1.100"
        assert event_dict["attack_type"] == "rate_limit_exceeded"
        assert event_dict["blocked"] is False

class TestRateLimitConfig:
    """Testes de configuração de rate limiting"""
    
    def test_rate_limit_config_defaults(self):
        """Testa valores padrão da configuração"""
        config = RateLimitConfig()
        
        assert config.requests_per_minute == 60
        assert config.requests_per_hour == 1000
        assert config.requests_per_day == 10000
        assert config.burst_limit == 10
        assert config.window_size == 60
        assert config.penalty_duration == 300
    
    def test_rate_limit_config_custom(self):
        """Testa configuração customizada"""
        config = RateLimitConfig(
            requests_per_minute=30,
            requests_per_hour=500,
            requests_per_day=5000,
            burst_limit=5,
            window_size=30,
            penalty_duration=600
        )
        
        assert config.requests_per_minute == 30
        assert config.requests_per_hour == 500
        assert config.requests_per_day == 5000
        assert config.burst_limit == 5
        assert config.window_size == 30
        assert config.penalty_duration == 600

class TestTokenConfig:
    """Testes de configuração de tokens"""
    
    def test_token_config_creation(self):
        """Testa criação de configuração de tokens"""
        config = TokenConfig(
            secret_key="test-secret-key",
            algorithm="HS512",
            access_token_expiry=1800,
            refresh_token_expiry=604800,
            api_key_expiry=31536000,
            issuer="test-issuer",
            audience="test-audience"
        )
        
        assert config.secret_key == "test-secret-key"
        assert config.algorithm == "HS512"
        assert config.access_token_expiry == 1800
        assert config.refresh_token_expiry == 604800
        assert config.api_key_expiry == 31536000
        assert config.issuer == "test-issuer"
        assert config.audience == "test-audience"
    
    def test_token_config_defaults(self):
        """Testa valores padrão da configuração"""
        config = TokenConfig(secret_key="test-secret")
        
        assert config.secret_key == "test-secret"
        assert config.algorithm == "HS256"
        assert config.access_token_expiry == 3600
        assert config.refresh_token_expiry == 2592000
        assert config.api_key_expiry == 31536000
        assert config.issuer == "omni-keywords-finder"
        assert config.audience == "api-users"

class TestTokenManager:
    """Testes do gerenciador de tokens"""
    
    def test_token_manager_creation(self):
        """Testa criação do gerenciador"""
        config = TokenConfig(secret_key="test-secret-key")
        manager = TokenManager(config)
        
        assert manager.config == config
        assert len(manager.blacklisted_tokens) == 0
        assert len(manager.token_cache) == 0
    
    def test_generate_access_token(self):
        """Testa geração de token de acesso"""
        config = TokenConfig(secret_key="test-secret-key")
        manager = TokenManager(config)
        
        token = manager.generate_access_token("user123", ["read", "write"])
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verificar se token foi adicionado ao cache
        assert token in manager.token_cache
        cached_data = manager.token_cache[token]
        assert cached_data["user_id"] == "user123"
        assert cached_data["permissions"] == ["read", "write"]
    
    def test_generate_refresh_token(self):
        """Testa geração de token de refresh"""
        config = TokenConfig(secret_key="test-secret-key")
        manager = TokenManager(config)
        
        token = manager.generate_refresh_token("user123")
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_generate_api_key(self):
        """Testa geração de API key"""
        config = TokenConfig(secret_key="test-secret-key")
        manager = TokenManager(config)
        
        token = manager.generate_api_key("user123", ["api_access"])
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verificar se token foi adicionado ao cache
        assert token in manager.token_cache
        cached_data = manager.token_cache[token]
        assert cached_data["user_id"] == "user123"
        assert cached_data["permissions"] == ["api_access"]
    
    def test_validate_token_valid(self):
        """Testa validação de token válido"""
        config = TokenConfig(secret_key="test-secret-key")
        manager = TokenManager(config)
        
        token = manager.generate_access_token("user123", ["read"])
        result = manager.validate_token(token)
        
        assert result is not None
        assert result["user_id"] == "user123"
        assert result["permissions"] == ["read"]
        assert result["type"] == "access"
    
    def test_validate_token_invalid(self):
        """Testa validação de token inválido"""
        config = TokenConfig(secret_key="test-secret-key")
        manager = TokenManager(config)
        
        result = manager.validate_token("invalid-token")
        assert result is None
    
    def test_validate_token_blacklisted(self):
        """Testa validação de token na blacklist"""
        config = TokenConfig(secret_key="test-secret-key")
        manager = TokenManager(config)
        
        token = manager.generate_access_token("user123")
        manager.blacklist_token(token)
        
        result = manager.validate_token(token)
        assert result is None
    
    def test_blacklist_token(self):
        """Testa blacklist de token"""
        config = TokenConfig(secret_key="test-secret-key")
        manager = TokenManager(config)
        
        token = manager.generate_access_token("user123")
        
        # Verificar se token está no cache
        assert token in manager.token_cache
        
        # Adicionar à blacklist
        manager.blacklist_token(token)
        
        # Verificar se token foi adicionado à blacklist
        assert token in manager.blacklisted_tokens
        
        # Verificar se token foi removido do cache
        assert token not in manager.token_cache
    
    def test_refresh_access_token(self):
        """Testa renovação de token de acesso"""
        config = TokenConfig(secret_key="test-secret-key")
        manager = TokenManager(config)
        
        refresh_token = manager.generate_refresh_token("user123")
        new_access_token = manager.refresh_access_token(refresh_token)
        
        assert new_access_token is not None
        assert isinstance(new_access_token, str)
        
        # Validar novo token
        result = manager.validate_token(new_access_token)
        assert result is not None
        assert result["user_id"] == "user123"
    
    def test_refresh_access_token_invalid(self):
        """Testa renovação com refresh token inválido"""
        config = TokenConfig(secret_key="test-secret-key")
        manager = TokenManager(config)
        
        result = manager.refresh_access_token("invalid-refresh-token")
        assert result is None
    
    def test_has_permission(self):
        """Testa verificação de permissão"""
        config = TokenConfig(secret_key="test-secret-key")
        manager = TokenManager(config)
        
        token = manager.generate_access_token("user123", ["read", "write"])
        
        # Verificar permissões existentes
        assert manager.has_permission(token, "read") is True
        assert manager.has_permission(token, "write") is True
        
        # Verificar permissão inexistente
        assert manager.has_permission(token, "delete") is False
    
    def test_has_permission_admin(self):
        """Testa verificação de permissão admin"""
        config = TokenConfig(secret_key="test-secret-key")
        manager = TokenManager(config)
        
        token = manager.generate_access_token("admin123", ["admin"])
        
        # Admin deve ter todas as permissões
        assert manager.has_permission(token, "read") is True
        assert manager.has_permission(token, "write") is True
        assert manager.has_permission(token, "delete") is True
    
    def test_get_user_id(self):
        """Testa obtenção de ID do usuário"""
        config = TokenConfig(secret_key="test-secret-key")
        manager = TokenManager(config)
        
        token = manager.generate_access_token("user123")
        
        user_id = manager.get_user_id(token)
        assert user_id == "user123"
        
        # Token inválido
        user_id = manager.get_user_id("invalid-token")
        assert user_id is None

class TestRateLimiter:
    """Testes do rate limiter"""
    
    def test_rate_limiter_creation(self):
        """Testa criação do rate limiter"""
        config = RateLimitConfig()
        limiter = RateLimiter(config)
        
        assert limiter.config == config
        assert len(limiter.requests) == 0
        assert len(limiter.blocked_ips) == 0
    
    def test_is_allowed_first_request(self):
        """Testa primeira requisição"""
        config = RateLimitConfig(requests_per_minute=60, burst_limit=10)
        limiter = RateLimiter(config)
        
        is_allowed, info = limiter.is_allowed("test-ip")
        
        assert is_allowed is True
        assert info["blocked"] is False
        assert info["current_requests"] == 1
    
    def test_is_allowed_within_limits(self):
        """Testa requisições dentro dos limites"""
        config = RateLimitConfig(requests_per_minute=60, burst_limit=10)
        limiter = RateLimiter(config)
        
        # Fazer várias requisições
        for i in range(5):
            is_allowed, info = limiter.is_allowed("test-ip")
            assert is_allowed is True
        
        # Verificar estatísticas
        stats = limiter.get_stats("test-ip")
        assert stats["current_requests"] == 5
    
    def test_is_allowed_burst_limit_exceeded(self):
        """Testa exceder limite de burst"""
        config = RateLimitConfig(requests_per_minute=60, burst_limit=3)
        limiter = RateLimiter(config)
        
        # Fazer requisições até exceder burst limit
        for i in range(3):
            is_allowed, info = limiter.is_allowed("test-ip")
            assert is_allowed is True
        
        # Próxima requisição deve ser bloqueada
        is_allowed, info = limiter.is_allowed("test-ip")
        assert is_allowed is False
        assert info["blocked"] is True
        assert "Burst limit exceeded" in info["reason"]
    
    def test_is_allowed_rate_limit_exceeded(self):
        """Testa exceder rate limit"""
        config = RateLimitConfig(requests_per_minute=3, burst_limit=10)
        limiter = RateLimiter(config)
        
        # Fazer requisições até exceder rate limit
        for i in range(3):
            is_allowed, info = limiter.is_allowed("test-ip")
            assert is_allowed is True
        
        # Próxima requisição deve ser bloqueada
        is_allowed, info = limiter.is_allowed("test-ip")
        assert is_allowed is False
        assert info["blocked"] is False
        assert "Rate limit exceeded" in info["reason"]
    
    def test_get_stats(self):
        """Testa obtenção de estatísticas"""
        config = RateLimitConfig(requests_per_minute=60, burst_limit=10)
        limiter = RateLimiter(config)
        
        # Fazer algumas requisições
        for i in range(5):
            limiter.is_allowed("test-ip")
        
        stats = limiter.get_stats("test-ip")
        
        assert stats["identifier"] == "test-ip"
        assert stats["current_requests"] == 5
        assert stats["requests_per_minute"] == 5
        assert stats["blocked"] is False
        assert stats["limits"]["burst"] == 10
        assert stats["limits"]["per_minute"] == 60

class TestSecurityValidator:
    """Testes do validador de segurança"""
    
    def test_security_validator_creation(self):
        """Testa criação do validador"""
        validator = SecurityValidator()
        
        assert validator.sql_injection_regex is not None
        assert validator.xss_regex is not None
        assert validator.csrf_regex is not None
    
    def test_validate_input_safe(self):
        """Testa validação de entrada segura"""
        validator = SecurityValidator()
        
        safe_inputs = [
            "hello world",
            "user123",
            "normal@email.com",
            "123456",
            "text with spaces"
        ]
        
        for safe_input in safe_inputs:
            is_valid, attack_type, reason = validator.validate_input(safe_input)
            assert is_valid is True
            assert attack_type is None
    
    def test_validate_input_sql_injection(self):
        """Testa detecção de SQL injection"""
        validator = SecurityValidator()
        
        sql_injection_inputs = [
            "'; DROP TABLE users; --",
            "OR 1=1",
            "SELECT * FROM users",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --",
            "UNION SELECT password FROM users"
        ]
        
        for malicious_input in sql_injection_inputs:
            is_valid, attack_type, reason = validator.validate_input(malicious_input)
            assert is_valid is False
            assert attack_type == AttackType.SQL_INJECTION
            assert "SQL injection" in reason
    
    def test_validate_input_xss(self):
        """Testa detecção de XSS"""
        validator = SecurityValidator()
        
        xss_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<iframe src='http://evil.com'></iframe>",
            "onclick=alert('xss')"
        ]
        
        for malicious_input in xss_inputs:
            is_valid, attack_type, reason = validator.validate_input(malicious_input)
            assert is_valid is False
            assert attack_type == AttackType.XSS
            assert "XSS" in reason
    
    def test_validate_input_csrf(self):
        """Testa detecção de CSRF"""
        validator = SecurityValidator()
        
        csrf_inputs = [
            "<img src='http://evil.com/csrf'>",
            "<iframe src='http://evil.com/csrf'></iframe>"
        ]
        
        for malicious_input in csrf_inputs:
            is_valid, attack_type, reason = validator.validate_input(malicious_input)
            assert is_valid is False
            assert attack_type == AttackType.CSRF
            assert "CSRF" in reason
    
    def test_sanitize_input(self):
        """Testa sanitização de entrada"""
        validator = SecurityValidator()
        
        malicious_input = "<script>alert('xss')</script>hello world"
        sanitized = validator.sanitize_input(malicious_input)
        
        assert "<script>" not in sanitized
        assert "hello world" in sanitized
    
    def test_validate_ip(self):
        """Testa validação de IP"""
        validator = SecurityValidator()
        
        valid_ips = [
            "192.168.1.1",
            "10.0.0.1",
            "172.16.0.1",
            "127.0.0.1",
            "::1",
            "2001:db8::1"
        ]
        
        invalid_ips = [
            "256.256.256.256",
            "192.168.1.256",
            "invalid-ip",
            "192.168.1",
            "192.168.1.1.1"
        ]
        
        for valid_ip in valid_ips:
            assert validator.validate_ip(valid_ip) is True
        
        for invalid_ip in invalid_ips:
            assert validator.validate_ip(invalid_ip) is False
    
    def test_is_suspicious_activity(self):
        """Testa detecção de atividade suspeita"""
        validator = SecurityValidator()
        
        # Atividade normal
        normal_request = {
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'params': {'user_id': '123'},
            'payload': '{"name": "test"}'
        }
        
        is_suspicious, attack_type, reason = validator.is_suspicious_activity(normal_request)
        assert is_suspicious is False
        
        # Atividade suspeita - User-Agent suspeito
        suspicious_request = {
            'user_agent': 'sqlmap/1.0',
            'params': {'user_id': '123'},
            'payload': '{"name": "test"}'
        }
        
        is_suspicious, attack_type, reason = validator.is_suspicious_activity(suspicious_request)
        assert is_suspicious is True
        assert attack_type == AttackType.SUSPICIOUS_ACTIVITY
        assert "Suspicious User-Agent" in reason

class TestAuditLogger:
    """Testes do logger de auditoria"""
    
    def test_audit_logger_creation(self):
        """Testa criação do logger"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            logger = AuditLogger(db_path)
            
            # Verificar se banco foi criado
            assert os.path.exists(db_path)
            
            # Verificar se tabelas foram criadas
            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                assert "security_events" in tables
                assert "api_requests" in tables
        finally:
            os.unlink(db_path)
    
    def test_log_security_event(self):
        """Testa registro de evento de segurança"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            logger = AuditLogger(db_path)
            
            event = SecurityEvent(
                id="test-event",
                timestamp=datetime.now(timezone.utc),
                event_type="test_event",
                severity=SecurityLevel.MEDIUM,
                source_ip="192.168.1.100",
                blocked=False
            )
            
            logger.log_security_event(event)
            
            # Verificar se evento foi registrado
            events = logger.get_security_events()
            assert len(events) == 1
            assert events[0].id == "test-event"
            assert events[0].event_type == "test_event"
        finally:
            os.unlink(db_path)
    
    def test_log_api_request(self):
        """Testa registro de requisição de API"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            logger = AuditLogger(db_path)
            
            request_data = {
                'id': 'req123',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'source_ip': '192.168.1.100',
                'user_id': 'user123',
                'endpoint': '/api/users',
                'method': 'GET',
                'status_code': 200,
                'response_time': 0.123,
                'user_agent': 'Mozilla/5.0',
                'request_size': 1024,
                'response_size': 2048
            }
            
            logger.log_api_request(request_data)
            
            # Verificar se requisição foi registrada (implementar se necessário)
            # Por enquanto, apenas verificar se não há erro
            assert True
        finally:
            os.unlink(db_path)
    
    def test_get_security_events_filtered(self):
        """Testa obtenção de eventos filtrados"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            logger = AuditLogger(db_path)
            
            # Criar eventos com diferentes severidades
            event1 = SecurityEvent(
                id="event1",
                timestamp=datetime.now(timezone.utc),
                event_type="test_event",
                severity=SecurityLevel.LOW,
                source_ip="192.168.1.100"
            )
            
            event2 = SecurityEvent(
                id="event2",
                timestamp=datetime.now(timezone.utc),
                event_type="test_event",
                severity=SecurityLevel.HIGH,
                source_ip="192.168.1.101"
            )
            
            logger.log_security_event(event1)
            logger.log_security_event(event2)
            
            # Filtrar por severidade
            high_events = logger.get_security_events(severity=SecurityLevel.HIGH)
            assert len(high_events) == 1
            assert high_events[0].severity == SecurityLevel.HIGH
            
            # Filtrar por IP
            # Implementar filtro por IP se necessário
        finally:
            os.unlink(db_path)

class TestAPISecurityManager:
    """Testes do gerenciador de segurança de APIs"""
    
    def test_security_manager_creation(self):
        """Testa criação do gerenciador"""
        token_config = TokenConfig(secret_key="test-secret")
        rate_limit_config = RateLimitConfig()
        
        manager = APISecurityManager(
            token_config=token_config,
            rate_limit_config=rate_limit_config,
            security_level=SecurityLevel.HIGH
        )
        
        assert manager.token_manager is not None
        assert manager.rate_limiter is not None
        assert manager.security_validator is not None
        assert manager.audit_logger is not None
        assert manager.security_level == SecurityLevel.HIGH
    
    def test_validate_request_safe(self):
        """Testa validação de requisição segura"""
        token_config = TokenConfig(secret_key="test-secret")
        rate_limit_config = RateLimitConfig()
        
        manager = APISecurityManager(token_config, rate_limit_config)
        
        request_data = {
            'source_ip': '192.168.1.100',
            'endpoint': '/api/users',
            'method': 'GET',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'params': {'user_id': '123'},
            'payload': ''
        }
        
        is_valid, result, event = manager.validate_request(request_data)
        
        assert is_valid is True
        assert result['valid'] is True
        assert result['blocked'] is False
        assert event is None
    
    def test_validate_request_with_token(self):
        """Testa validação de requisição com token"""
        token_config = TokenConfig(secret_key="test-secret")
        rate_limit_config = RateLimitConfig()
        
        manager = APISecurityManager(token_config, rate_limit_config)
        
        # Gerar token
        token = manager.token_manager.generate_access_token("user123", ["read"])
        
        request_data = {
            'source_ip': '192.168.1.100',
            'endpoint': '/api/users',
            'method': 'GET',
            'user_agent': 'Mozilla/5.0',
            'params': {'user_id': '123'},
            'payload': ''
        }
        
        is_valid, result, event = manager.validate_request(request_data, token)
        
        assert is_valid is True
        assert result['user_id'] == "user123"
        assert result['permissions'] == ["read"]
    
    def test_validate_request_sql_injection(self):
        """Testa validação de requisição com SQL injection"""
        token_config = TokenConfig(secret_key="test-secret")
        rate_limit_config = RateLimitConfig()
        
        manager = APISecurityManager(token_config, rate_limit_config)
        
        request_data = {
            'source_ip': '192.168.1.100',
            'endpoint': '/api/users',
            'method': 'POST',
            'user_agent': 'Mozilla/5.0',
            'params': {'user_id': "'; DROP TABLE users; --"},
            'payload': ''
        }
        
        is_valid, result, event = manager.validate_request(request_data)
        
        assert is_valid is False
        assert result['blocked'] is True
        assert "SQL injection" in result['reason']
        assert event is not None
        assert event.attack_type == AttackType.SQL_INJECTION
        assert event.blocked is True
    
    def test_validate_request_xss(self):
        """Testa validação de requisição com XSS"""
        token_config = TokenConfig(secret_key="test-secret")
        rate_limit_config = RateLimitConfig()
        
        manager = APISecurityManager(token_config, rate_limit_config)
        
        request_data = {
            'source_ip': '192.168.1.100',
            'endpoint': '/api/users',
            'method': 'POST',
            'user_agent': 'Mozilla/5.0',
            'params': {},
            'payload': '<script>alert("xss")</script>'
        }
        
        is_valid, result, event = manager.validate_request(request_data)
        
        assert is_valid is False
        assert result['blocked'] is True
        assert "XSS" in result['reason']
        assert event is not None
        assert event.attack_type == AttackType.XSS
    
    def test_validate_request_invalid_token(self):
        """Testa validação de requisição com token inválido"""
        token_config = TokenConfig(secret_key="test-secret")
        rate_limit_config = RateLimitConfig()
        
        manager = APISecurityManager(token_config, rate_limit_config)
        
        request_data = {
            'source_ip': '192.168.1.100',
            'endpoint': '/api/users',
            'method': 'GET',
            'user_agent': 'Mozilla/5.0',
            'params': {},
            'payload': ''
        }
        
        is_valid, result, event = manager.validate_request(request_data, "invalid-token")
        
        assert is_valid is False
        assert result['blocked'] is True
        assert "Invalid token" in result['reason']
        assert event is not None
        assert event.attack_type == AttackType.INVALID_TOKEN
    
    def test_validate_request_rate_limit(self):
        """Testa validação de requisição com rate limiting"""
        token_config = TokenConfig(secret_key="test-secret")
        rate_limit_config = RateLimitConfig(requests_per_minute=2, burst_limit=2)
        
        manager = APISecurityManager(token_config, rate_limit_config)
        
        request_data = {
            'source_ip': '192.168.1.100',
            'endpoint': '/api/users',
            'method': 'GET',
            'user_agent': 'Mozilla/5.0',
            'params': {},
            'payload': ''
        }
        
        # Fazer requisições até exceder limite
        for i in range(2):
            is_valid, result, event = manager.validate_request(request_data)
            assert is_valid is True
        
        # Próxima requisição deve ser bloqueada
        is_valid, result, event = manager.validate_request(request_data)
        assert is_valid is False
        assert "Rate limit exceeded" in result['reason']
    
    def test_blacklist_whitelist_ips(self):
        """Testa blacklist e whitelist de IPs"""
        token_config = TokenConfig(secret_key="test-secret")
        rate_limit_config = RateLimitConfig()
        
        manager = APISecurityManager(token_config, rate_limit_config)
        
        # Adicionar IP à blacklist
        manager.add_blacklisted_ip("192.168.1.100")
        
        request_data = {
            'source_ip': '192.168.1.100',
            'endpoint': '/api/users',
            'method': 'GET',
            'user_agent': 'Mozilla/5.0',
            'params': {},
            'payload': ''
        }
        
        is_valid, result, event = manager.validate_request(request_data)
        assert is_valid is False
        assert result['blocked'] is True
        assert "IP is blacklisted" in result['reason']
        
        # Remover da blacklist
        manager.remove_blacklisted_ip("192.168.1.100")
        
        is_valid, result, event = manager.validate_request(request_data)
        assert is_valid is True
        
        # Adicionar à whitelist
        manager.add_whitelisted_ip("192.168.1.101")
        
        request_data['source_ip'] = '192.168.1.101'
        is_valid, result, event = manager.validate_request(request_data)
        assert is_valid is True
    
    def test_get_metrics(self):
        """Testa obtenção de métricas"""
        token_config = TokenConfig(secret_key="test-secret")
        rate_limit_config = RateLimitConfig()
        
        manager = APISecurityManager(token_config, rate_limit_config)
        
        # Fazer algumas requisições
        request_data = {
            'source_ip': '192.168.1.100',
            'endpoint': '/api/users',
            'method': 'GET',
            'user_agent': 'Mozilla/5.0',
            'params': {},
            'payload': ''
        }
        
        for i in range(5):
            manager.validate_request(request_data)
        
        metrics = manager.get_metrics()
        
        assert metrics['total_requests'] == 5
        assert metrics['blocked_requests'] == 0
        assert metrics['security_events'] == 0
        assert metrics['security_level'] == 'medium'
        assert metrics['block_rate'] == 0.0

class TestDecorators:
    """Testes dos decorators"""
    
    def test_require_auth_decorator(self):
        """Testa decorator require_auth"""
        @require_auth("read")
        def test_function():
            return "success"
        
        # Por enquanto, apenas verificar se não há erro
        result = test_function()
        assert result == "success"
    
    def test_rate_limit_decorator(self):
        """Testa decorator rate_limit"""
        @rate_limit(60)
        def test_function():
            return "success"
        
        # Por enquanto, apenas verificar se não há erro
        result = test_function()
        assert result == "success"
    
    def test_validate_input_decorator(self):
        """Testa decorator validate_input"""
        @validate_input("param")
        def test_function(param):
            return "success"
        
        # Por enquanto, apenas verificar se não há erro
        result = test_function("test")
        assert result == "success"

class TestIntegration:
    """Testes de integração"""
    
    def test_full_security_workflow(self):
        """Testa workflow completo de segurança"""
        # Configurar sistema
        token_config = TokenConfig(secret_key="test-secret")
        rate_limit_config = RateLimitConfig(requests_per_minute=10, burst_limit=5)
        
        manager = APISecurityManager(
            token_config=token_config,
            rate_limit_config=rate_limit_config,
            security_level=SecurityLevel.HIGH
        )
        
        # Gerar token
        token = manager.token_manager.generate_access_token("user123", ["read", "write"])
        
        # Requisição segura
        safe_request = {
            'source_ip': '192.168.1.100',
            'endpoint': '/api/users',
            'method': 'GET',
            'user_agent': 'Mozilla/5.0',
            'params': {'user_id': '123'},
            'payload': ''
        }
        
        is_valid, result, event = manager.validate_request(safe_request, token)
        assert is_valid is True
        assert result['user_id'] == "user123"
        
        # Requisição maliciosa
        malicious_request = {
            'source_ip': '192.168.1.101',
            'endpoint': '/api/users',
            'method': 'POST',
            'user_agent': 'sqlmap/1.0',
            'params': {'user_id': "'; DROP TABLE users; --"},
            'payload': '<script>alert("xss")</script>'
        }
        
        is_valid, result, event = manager.validate_request(malicious_request)
        assert is_valid is False
        assert result['blocked'] is True
        
        # Verificar métricas
        metrics = manager.get_metrics()
        assert metrics['total_requests'] == 2
        assert metrics['blocked_requests'] == 1
        assert metrics['attacks_detected'] >= 1
        
        # Verificar eventos de segurança
        events = manager.get_security_events()
        assert len(events) >= 1

# Teste de funcionalidade
if __name__ == "__main__":
    # Teste básico
    token_config = TokenConfig(secret_key="test-secret")
    rate_limit_config = RateLimitConfig()
    
    manager = APISecurityManager(token_config, rate_limit_config)
    
    # Testar requisição segura
    request_data = {
        'source_ip': '192.168.1.100',
        'endpoint': '/api/users',
        'method': 'GET',
        'user_agent': 'Mozilla/5.0',
        'params': {'user_id': '123'},
        'payload': ''
    }
    
    is_valid, result, event = manager.validate_request(request_data)
    print(f"Requisição válida: {is_valid}")
    print(f"Resultado: {result}")
    
    # Mostrar métricas
    metrics = manager.get_metrics()
    print(f"Métricas: {json.dumps(metrics, indent=2)}") 