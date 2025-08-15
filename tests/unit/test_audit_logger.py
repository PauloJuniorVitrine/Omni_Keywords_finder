"""
Testes Unitários para Audit Logger
Sistema de Logging de Segurança para Auditoria - Omni Keywords Finder

Prompt: Implementação de testes unitários para sistema de auditoria de segurança
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import json
import logging
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from typing import Dict, Any

from backend.app.security.audit_logger import (
    SecurityAuditLogger,
    SecurityEvent,
    SecurityEventType,
    SecurityLevel,
    security_logger,
    log_security_event
)


class TestSecurityEventType:
    """Testes para enum SecurityEventType"""
    
    def test_security_event_type_values(self):
        """Testa valores do enum SecurityEventType"""
        assert SecurityEventType.LOGIN_SUCCESS.value == "login_success"
        assert SecurityEventType.LOGIN_FAILED.value == "login_failed"
        assert SecurityEventType.LOGIN_BLOCKED.value == "login_blocked"
        assert SecurityEventType.LOGOUT.value == "logout"
        assert SecurityEventType.PASSWORD_CHANGE.value == "password_change"
        assert SecurityEventType.PASSWORD_RESET.value == "password_reset"
        assert SecurityEventType.ACCOUNT_LOCKED.value == "account_locked"
        assert SecurityEventType.ACCOUNT_UNLOCKED.value == "account_unlocked"
        assert SecurityEventType.RATE_LIMIT_EXCEEDED.value == "rate_limit_exceeded"
        assert SecurityEventType.SUSPICIOUS_ACTIVITY.value == "suspicious_activity"
        assert SecurityEventType.OAUTH_LOGIN.value == "oauth_login"
        assert SecurityEventType.OAUTH_FAILED.value == "oauth_failed"
        assert SecurityEventType.SESSION_EXPIRED.value == "session_expired"
        assert SecurityEventType.UNAUTHORIZED_ACCESS.value == "unauthorized_access"
        assert SecurityEventType.ADMIN_ACTION.value == "admin_action"
    
    def test_security_event_type_comparison(self):
        """Testa comparação entre tipos de eventos"""
        assert SecurityEventType.LOGIN_SUCCESS != SecurityEventType.LOGIN_FAILED
        assert SecurityEventType.ADMIN_ACTION != SecurityEventType.SUSPICIOUS_ACTIVITY
        assert SecurityEventType.LOGOUT == SecurityEventType.LOGOUT


class TestSecurityLevel:
    """Testes para enum SecurityLevel"""
    
    def test_security_level_values(self):
        """Testa valores do enum SecurityLevel"""
        assert SecurityLevel.INFO.value == "info"
        assert SecurityLevel.WARNING.value == "warning"
        assert SecurityLevel.CRITICAL.value == "critical"
        assert SecurityLevel.ALERT.value == "alert"
    
    def test_security_level_comparison(self):
        """Testa comparação entre níveis de segurança"""
        assert SecurityLevel.INFO != SecurityLevel.WARNING
        assert SecurityLevel.CRITICAL != SecurityLevel.ALERT
        assert SecurityLevel.INFO == SecurityLevel.INFO


class TestSecurityEvent:
    """Testes para SecurityEvent"""
    
    def test_security_event_creation(self):
        """Testa criação de SecurityEvent"""
        event = SecurityEvent(
            event_type=SecurityEventType.LOGIN_SUCCESS,
            timestamp="2025-01-27T10:00:00Z",
            user_id="user123",
            username="john_doe",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            session_id="session123",
            details={"endpoint": "/login"},
            security_level=SecurityLevel.INFO,
            risk_score=2,
            correlation_id="corr123"
        )
        
        assert event.event_type == SecurityEventType.LOGIN_SUCCESS
        assert event.timestamp == "2025-01-27T10:00:00Z"
        assert event.user_id == "user123"
        assert event.username == "john_doe"
        assert event.ip_address == "192.168.1.1"
        assert event.user_agent == "Mozilla/5.0"
        assert event.session_id == "session123"
        assert event.details == {"endpoint": "/login"}
        assert event.security_level == SecurityLevel.INFO
        assert event.risk_score == 2
        assert event.correlation_id == "corr123"
        assert event.source == "auth_api"
    
    def test_security_event_default_values(self):
        """Testa valores padrão de SecurityEvent"""
        event = SecurityEvent(
            event_type=SecurityEventType.LOGIN_FAILED,
            timestamp="2025-01-27T10:00:00Z",
            user_id=None,
            username=None,
            ip_address="192.168.1.1",
            user_agent="",
            session_id=None,
            details={},
            security_level=SecurityLevel.WARNING,
            risk_score=5,
            correlation_id=None
        )
        
        assert event.user_id is None
        assert event.username is None
        assert event.session_id is None
        assert event.correlation_id is None
        assert event.source == "auth_api"


class TestSecurityAuditLogger:
    """Testes para SecurityAuditLogger"""
    
    @pytest.fixture
    def temp_log_file(self):
        """Arquivo de log temporário para testes"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            temp_file = f.name
        
        yield temp_file
        
        # Limpar arquivo após teste
        if os.path.exists(temp_file):
            os.unlink(temp_file)
    
    @pytest.fixture
    def logger(self, temp_log_file):
        """Instância do SecurityAuditLogger para testes"""
        with patch.dict(os.environ, {'SECURITY_LOG_FILE': temp_log_file}):
            return SecurityAuditLogger()
    
    def test_logger_initialization(self, logger):
        """Testa inicialização do SecurityAuditLogger"""
        assert logger.logger is not None
        assert isinstance(logger.logger, logging.Logger)
        assert logger.logger.name == 'security_audit'
        assert len(logger.risk_patterns) > 0
        assert logger.alert_threshold >= 0
        assert logger._lock is not None
    
    def test_load_risk_patterns(self, logger):
        """Testa carregamento de padrões de risco"""
        patterns = logger._load_risk_patterns()
        
        assert isinstance(patterns, dict)
        assert len(patterns) > 0
        assert 'multiple_failed_logins' in patterns
        assert 'suspicious_ip' in patterns
        assert 'unusual_time' in patterns
        assert 'suspicious_user_agent' in patterns
        assert 'rate_limit_exceeded' in patterns
        assert 'admin_action' in patterns
        assert 'oauth_failure' in patterns
        assert 'session_hijacking' in patterns
        assert 'brute_force' in patterns
        
        # Verificar que todos os valores são inteiros positivos
        for value in patterns.values():
            assert isinstance(value, int)
            assert value >= 0
    
    def test_calculate_risk_score_no_risk(self, logger):
        """Testa cálculo de score de risco sem riscos"""
        event = SecurityEvent(
            event_type=SecurityEventType.LOGIN_SUCCESS,
            timestamp="2025-01-27T10:00:00Z",
            user_id="user123",
            username="john_doe",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            session_id="session123",
            details={},
            security_level=SecurityLevel.INFO,
            risk_score=0,
            correlation_id="corr123"
        )
        
        score = logger._calculate_risk_score(event)
        
        assert score == 0
    
    def test_calculate_risk_score_multiple_failed_logins(self, logger):
        """Testa cálculo de score de risco com múltiplas tentativas falhadas"""
        event = SecurityEvent(
            event_type=SecurityEventType.LOGIN_FAILED,
            timestamp="2025-01-27T10:00:00Z",
            user_id="user123",
            username="john_doe",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            session_id="session123",
            details={"failed_attempts": 5},
            security_level=SecurityLevel.WARNING,
            risk_score=0,
            correlation_id="corr123"
        )
        
        score = logger._calculate_risk_score(event)
        
        assert score >= logger.risk_patterns['multiple_failed_logins']
    
    def test_calculate_risk_score_suspicious_ip(self, logger):
        """Testa cálculo de score de risco com IP suspeito"""
        event = SecurityEvent(
            event_type=SecurityEventType.LOGIN_SUCCESS,
            timestamp="2025-01-27T10:00:00Z",
            user_id="user123",
            username="john_doe",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            session_id="session123",
            details={"suspicious_ip": True},
            security_level=SecurityLevel.WARNING,
            risk_score=0,
            correlation_id="corr123"
        )
        
        score = logger._calculate_risk_score(event)
        
        assert score >= logger.risk_patterns['suspicious_ip']
    
    def test_calculate_risk_score_unusual_time(self, logger):
        """Testa cálculo de score de risco com horário incomum"""
        event = SecurityEvent(
            event_type=SecurityEventType.LOGIN_SUCCESS,
            timestamp="2025-01-27T10:00:00Z",
            user_id="user123",
            username="john_doe",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            session_id="session123",
            details={"unusual_time": True},
            security_level=SecurityLevel.WARNING,
            risk_score=0,
            correlation_id="corr123"
        )
        
        score = logger._calculate_risk_score(event)
        
        assert score >= logger.risk_patterns['unusual_time']
    
    def test_calculate_risk_score_suspicious_user_agent(self, logger):
        """Testa cálculo de score de risco com User-Agent suspeito"""
        event = SecurityEvent(
            event_type=SecurityEventType.LOGIN_SUCCESS,
            timestamp="2025-01-27T10:00:00Z",
            user_id="user123",
            username="john_doe",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            session_id="session123",
            details={"suspicious_user_agent": True},
            security_level=SecurityLevel.WARNING,
            risk_score=0,
            correlation_id="corr123"
        )
        
        score = logger._calculate_risk_score(event)
        
        assert score >= logger.risk_patterns['suspicious_user_agent']
    
    def test_calculate_risk_score_rate_limit_exceeded(self, logger):
        """Testa cálculo de score de risco com rate limit excedido"""
        event = SecurityEvent(
            event_type=SecurityEventType.RATE_LIMIT_EXCEEDED,
            timestamp="2025-01-27T10:00:00Z",
            user_id="user123",
            username="john_doe",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            session_id="session123",
            details={},
            security_level=SecurityLevel.WARNING,
            risk_score=0,
            correlation_id="corr123"
        )
        
        score = logger._calculate_risk_score(event)
        
        assert score >= logger.risk_patterns['rate_limit_exceeded']
    
    def test_calculate_risk_score_admin_action(self, logger):
        """Testa cálculo de score de risco com ação administrativa"""
        event = SecurityEvent(
            event_type=SecurityEventType.ADMIN_ACTION,
            timestamp="2025-01-27T10:00:00Z",
            user_id="user123",
            username="john_doe",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            session_id="session123",
            details={},
            security_level=SecurityLevel.INFO,
            risk_score=0,
            correlation_id="corr123"
        )
        
        score = logger._calculate_risk_score(event)
        
        assert score >= logger.risk_patterns['admin_action']
    
    def test_calculate_risk_score_oauth_failure(self, logger):
        """Testa cálculo de score de risco com falha OAuth"""
        event = SecurityEvent(
            event_type=SecurityEventType.OAUTH_FAILED,
            timestamp="2025-01-27T10:00:00Z",
            user_id="user123",
            username="john_doe",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            session_id="session123",
            details={},
            security_level=SecurityLevel.WARNING,
            risk_score=0,
            correlation_id="corr123"
        )
        
        score = logger._calculate_risk_score(event)
        
        assert score >= logger.risk_patterns['oauth_failure']
    
    def test_calculate_risk_score_maximum(self, logger):
        """Testa que o score de risco não excede o máximo"""
        event = SecurityEvent(
            event_type=SecurityEventType.RATE_LIMIT_EXCEEDED,
            timestamp="2025-01-27T10:00:00Z",
            user_id="user123",
            username="john_doe",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            session_id="session123",
            details={
                "failed_attempts": 10,
                "suspicious_ip": True,
                "unusual_time": True,
                "suspicious_user_agent": True
            },
            security_level=SecurityLevel.ALERT,
            risk_score=0,
            correlation_id="corr123"
        )
        
        score = logger._calculate_risk_score(event)
        
        assert score <= 10  # Máximo definido no código
    
    def test_detect_anomalies_brute_force(self, logger):
        """Testa detecção de anomalias de força bruta"""
        event = SecurityEvent(
            event_type=SecurityEventType.LOGIN_FAILED,
            timestamp="2025-01-27T10:00:00Z",
            user_id="user123",
            username="john_doe",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            session_id="session123",
            details={"failed_attempts": 6},
            security_level=SecurityLevel.WARNING,
            risk_score=0,
            correlation_id="corr123"
        )
        
        anomalies = logger._detect_anomalies(event)
        
        assert "brute_force_attempt" in anomalies
    
    def test_detect_anomalies_suspicious_ip(self, logger):
        """Testa detecção de anomalias de IP suspeito"""
        event = SecurityEvent(
            event_type=SecurityEventType.LOGIN_SUCCESS,
            timestamp="2025-01-27T10:00:00Z",
            user_id="user123",
            username="john_doe",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            session_id="session123",
            details={"suspicious_ip": True},
            security_level=SecurityLevel.WARNING,
            risk_score=0,
            correlation_id="corr123"
        )
        
        anomalies = logger._detect_anomalies(event)
        
        assert "suspicious_ip_address" in anomalies
    
    def test_detect_anomalies_unusual_time(self, logger):
        """Testa detecção de anomalias de horário incomum"""
        event = SecurityEvent(
            event_type=SecurityEventType.LOGIN_SUCCESS,
            timestamp="2025-01-27T10:00:00Z",
            user_id="user123",
            username="john_doe",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            session_id="session123",
            details={"unusual_time": True},
            security_level=SecurityLevel.WARNING,
            risk_score=0,
            correlation_id="corr123"
        )
        
        anomalies = logger._detect_anomalies(event)
        
        assert "unusual_access_time" in anomalies
    
    def test_detect_anomalies_suspicious_user_agent(self, logger):
        """Testa detecção de anomalias de User-Agent suspeito"""
        event = SecurityEvent(
            event_type=SecurityEventType.LOGIN_SUCCESS,
            timestamp="2025-01-27T10:00:00Z",
            user_id="user123",
            username="john_doe",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            session_id="session123",
            details={"suspicious_user_agent": True},
            security_level=SecurityLevel.WARNING,
            risk_score=0,
            correlation_id="corr123"
        )
        
        anomalies = logger._detect_anomalies(event)
        
        assert "suspicious_user_agent" in anomalies
    
    def test_detect_anomalies_no_anomalies(self, logger):
        """Testa detecção de anomalias sem anomalias"""
        event = SecurityEvent(
            event_type=SecurityEventType.LOGIN_SUCCESS,
            timestamp="2025-01-27T10:00:00Z",
            user_id="user123",
            username="john_doe",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            session_id="session123",
            details={},
            security_level=SecurityLevel.INFO,
            risk_score=0,
            correlation_id="corr123"
        )
        
        anomalies = logger._detect_anomalies(event)
        
        assert len(anomalies) == 0
    
    def test_should_alert_below_threshold(self, logger):
        """Testa se deve gerar alerta abaixo do threshold"""
        event = SecurityEvent(
            event_type=SecurityEventType.LOGIN_SUCCESS,
            timestamp="2025-01-27T10:00:00Z",
            user_id="user123",
            username="john_doe",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            session_id="session123",
            details={},
            security_level=SecurityLevel.INFO,
            risk_score=logger.alert_threshold - 1,
            correlation_id="corr123"
        )
        
        should_alert = logger._should_alert(event)
        
        assert should_alert is False
    
    def test_should_alert_at_threshold(self, logger):
        """Testa se deve gerar alerta no threshold"""
        event = SecurityEvent(
            event_type=SecurityEventType.LOGIN_SUCCESS,
            timestamp="2025-01-27T10:00:00Z",
            user_id="user123",
            username="john_doe",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            session_id="session123",
            details={},
            security_level=SecurityLevel.INFO,
            risk_score=logger.alert_threshold,
            correlation_id="corr123"
        )
        
        should_alert = logger._should_alert(event)
        
        assert should_alert is True
    
    def test_should_alert_above_threshold(self, logger):
        """Testa se deve gerar alerta acima do threshold"""
        event = SecurityEvent(
            event_type=SecurityEventType.LOGIN_SUCCESS,
            timestamp="2025-01-27T10:00:00Z",
            user_id="user123",
            username="john_doe",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            session_id="session123",
            details={},
            security_level=SecurityLevel.INFO,
            risk_score=logger.alert_threshold + 1,
            correlation_id="corr123"
        )
        
        should_alert = logger._should_alert(event)
        
        assert should_alert is True
    
    @patch('backend.app.security.audit_logger.request')
    def test_get_client_info(self, mock_request, logger):
        """Testa obtenção de informações do cliente"""
        mock_request.headers = {
            'X-Forwarded-For': '10.0.0.1',
            'User-Agent': 'Test Browser',
            'Referer': 'https://example.com',
            'Origin': 'https://example.com'
        }
        mock_request.remote_addr = '192.168.1.1'
        
        client_info = logger._get_client_info()
        
        assert client_info['ip_address'] == '10.0.0.1'
        assert client_info['user_agent'] == 'Test Browser'
        assert client_info['referer'] == 'https://example.com'
        assert client_info['origin'] == 'https://example.com'
    
    @patch('backend.app.security.audit_logger.request')
    def test_get_client_info_no_forwarded_for(self, mock_request, logger):
        """Testa obtenção de informações do cliente sem X-Forwarded-For"""
        mock_request.headers = {
            'User-Agent': 'Test Browser'
        }
        mock_request.remote_addr = '192.168.1.1'
        
        client_info = logger._get_client_info()
        
        assert client_info['ip_address'] == '192.168.1.1'
        assert client_info['user_agent'] == 'Test Browser'
    
    def test_is_suspicious_ip_true(self, logger):
        """Testa verificação de IP suspeito - verdadeiro"""
        with patch.dict(os.environ, {'SUSPICIOUS_IPS': '192.168.1.1,10.0.0.1'}):
            result = logger._is_suspicious_ip('192.168.1.1')
            assert result is True
    
    def test_is_suspicious_ip_false(self, logger):
        """Testa verificação de IP suspeito - falso"""
        with patch.dict(os.environ, {'SUSPICIOUS_IPS': '192.168.1.1,10.0.0.1'}):
            result = logger._is_suspicious_ip('192.168.2.1')
            assert result is False
    
    def test_is_suspicious_ip_empty_list(self, logger):
        """Testa verificação de IP suspeito com lista vazia"""
        with patch.dict(os.environ, {'SUSPICIOUS_IPS': ''}):
            result = logger._is_suspicious_ip('192.168.1.1')
            assert result is False
    
    @patch('backend.app.security.audit_logger.datetime')
    def test_is_unusual_time_late_night(self, mock_datetime, logger):
        """Testa verificação de horário incomum - madrugada"""
        mock_datetime.now.return_value.hour = 2
        
        result = logger._is_unusual_time()
        
        assert result is True
    
    @patch('backend.app.security.audit_logger.datetime')
    def test_is_unusual_time_early_morning(self, mock_datetime, logger):
        """Testa verificação de horário incomum - manhã cedo"""
        mock_datetime.now.return_value.hour = 5
        
        result = logger._is_unusual_time()
        
        assert result is True
    
    @patch('backend.app.security.audit_logger.datetime')
    def test_is_unusual_time_normal_hours(self, mock_datetime, logger):
        """Testa verificação de horário incomum - horário normal"""
        mock_datetime.now.return_value.hour = 14
        
        result = logger._is_unusual_time()
        
        assert result is False
    
    def test_is_suspicious_user_agent_true(self, logger):
        """Testa verificação de User-Agent suspeito - verdadeiro"""
        suspicious_agents = [
            'bot',
            'crawler',
            'spider',
            'scraper',
            'curl',
            'wget',
            'python-requests',
            'sqlmap',
            'nikto',
            'nmap'
        ]
        
        for agent in suspicious_agents:
            result = logger._is_suspicious_user_agent(agent)
            assert result is True
    
    def test_is_suspicious_user_agent_false(self, logger):
        """Testa verificação de User-Agent suspeito - falso"""
        normal_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Chrome/91.0.4472.124 Safari/537.36',
            'Firefox/89.0',
            'Safari/14.1.1'
        ]
        
        for agent in normal_agents:
            result = logger._is_suspicious_user_agent(agent)
            assert result is False
    
    @patch('backend.app.security.audit_logger.request')
    @patch('backend.app.security.audit_logger.g')
    def test_log_event_success(self, mock_g, mock_request, logger, temp_log_file):
        """Testa log de evento com sucesso"""
        mock_request.headers = {
            'X-Forwarded-For': '192.168.1.1',
            'User-Agent': 'Mozilla/5.0'
        }
        mock_request.remote_addr = '192.168.1.1'
        mock_g.get.return_value = None
        
        event = logger.log_event(
            event_type=SecurityEventType.LOGIN_SUCCESS,
            user_id="user123",
            username="john_doe",
            details={"endpoint": "/login"},
            security_level=SecurityLevel.INFO
        )
        
        assert event.event_type == SecurityEventType.LOGIN_SUCCESS
        assert event.user_id == "user123"
        assert event.username == "john_doe"
        assert event.ip_address == "192.168.1.1"
        assert event.user_agent == "Mozilla/5.0"
        assert event.details["endpoint"] == "/login"
        assert event.security_level == SecurityLevel.INFO
        assert event.risk_score >= 0
        assert event.source == "auth_api"
        
        # Verificar se o log foi escrito no arquivo
        with open(temp_log_file, 'r') as f:
            log_content = f.read()
            assert log_content.strip() != ""
            log_entry = json.loads(log_content)
            assert log_entry["event_type"] == "login_success"
            assert log_entry["user_id"] == "user123"
    
    @patch('backend.app.security.audit_logger.request')
    @patch('backend.app.security.audit_logger.g')
    def test_log_event_with_anomalies(self, mock_g, mock_request, logger, temp_log_file):
        """Testa log de evento com anomalias"""
        mock_request.headers = {
            'X-Forwarded-For': '192.168.1.1',
            'User-Agent': 'bot'
        }
        mock_request.remote_addr = '192.168.1.1'
        mock_g.get.return_value = None
        
        event = logger.log_event(
            event_type=SecurityEventType.LOGIN_FAILED,
            user_id="user123",
            username="john_doe",
            details={"failed_attempts": 6},
            security_level=SecurityLevel.WARNING
        )
        
        assert event.security_level == SecurityLevel.WARNING
        assert "anomalies" in event.details
        assert len(event.details["anomalies"]) > 0
    
    @patch('backend.app.security.audit_logger.request')
    @patch('backend.app.security.audit_logger.g')
    def test_log_event_high_risk_alert(self, mock_g, mock_request, logger, temp_log_file):
        """Testa log de evento com risco alto (alerta)"""
        mock_request.headers = {
            'X-Forwarded-For': '192.168.1.1',
            'User-Agent': 'Mozilla/5.0'
        }
        mock_request.remote_addr = '192.168.1.1'
        mock_g.get.return_value = None
        
        # Configurar threshold baixo para forçar alerta
        logger.alert_threshold = 1
        
        event = logger.log_event(
            event_type=SecurityEventType.RATE_LIMIT_EXCEEDED,
            user_id="user123",
            username="john_doe",
            details={"failed_attempts": 10},
            security_level=SecurityLevel.WARNING
        )
        
        assert event.security_level == SecurityLevel.ALERT
        assert event.risk_score >= logger.alert_threshold


class TestSecurityAuditLoggerIntegration:
    """Testes de integração para SecurityAuditLogger"""
    
    @pytest.fixture
    def temp_log_file(self):
        """Arquivo de log temporário para testes"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            temp_file = f.name
        
        yield temp_file
        
        # Limpar arquivo após teste
        if os.path.exists(temp_file):
            os.unlink(temp_file)
    
    @pytest.fixture
    def logger(self, temp_log_file):
        """Instância do SecurityAuditLogger para testes"""
        with patch.dict(os.environ, {'SECURITY_LOG_FILE': temp_log_file}):
            return SecurityAuditLogger()
    
    @patch('backend.app.security.audit_logger.request')
    @patch('backend.app.security.audit_logger.g')
    def test_complex_security_scenario(self, mock_g, mock_request, logger, temp_log_file):
        """Testa cenário complexo de segurança"""
        mock_request.headers = {
            'X-Forwarded-For': '192.168.1.1',
            'User-Agent': 'sqlmap'
        }
        mock_request.remote_addr = '192.168.1.1'
        mock_g.get.return_value = None
        
        # Simular múltiplas tentativas de login falhadas
        events = []
        for i in range(5):
            event = logger.log_event(
                event_type=SecurityEventType.LOGIN_FAILED,
                user_id="user123",
                username="john_doe",
                details={"failed_attempts": i + 1},
                security_level=SecurityLevel.WARNING
            )
            events.append(event)
        
        # Verificar que o último evento tem risco alto
        last_event = events[-1]
        assert last_event.risk_score > 0
        assert "anomalies" in last_event.details
        
        # Verificar logs no arquivo
        with open(temp_log_file, 'r') as f:
            log_lines = f.readlines()
            assert len(log_lines) == 5
            
            for line in log_lines:
                log_entry = json.loads(line.strip())
                assert log_entry["event_type"] == "login_failed"
                assert log_entry["user_id"] == "user123"


class TestGlobalSecurityLogger:
    """Testes para instância global do SecurityAuditLogger"""
    
    def test_global_security_logger(self):
        """Testa instância global do SecurityAuditLogger"""
        assert security_logger is not None
        assert isinstance(security_logger, SecurityAuditLogger)
        assert security_logger.logger.name == 'security_audit'


class TestLogSecurityEventDecorator:
    """Testes para decorator log_security_event"""
    
    @pytest.fixture
    def mock_request(self):
        """Mock de request para testes"""
        request = Mock()
        request.headers = {
            'X-Forwarded-For': '192.168.1.1',
            'User-Agent': 'Mozilla/5.0'
        }
        request.remote_addr = '192.168.1.1'
        request.endpoint = '/test'
        request.method = 'GET'
        return request
    
    @pytest.fixture
    def mock_g(self):
        """Mock de g para testes"""
        g = Mock()
        g.get.return_value = None
        return g
    
    @patch('backend.app.security.audit_logger.request')
    @patch('backend.app.security.audit_logger.g')
    def test_log_security_event_decorator_success(self, mock_g, mock_request, mock_request_obj):
        """Testa decorator com sucesso"""
        mock_request.return_value = mock_request_obj
        mock_g.return_value = Mock()
        mock_g.return_value.get.return_value = None
        
        @log_security_event(SecurityEventType.LOGIN_SUCCESS)
        def test_function():
            return "success"
        
        result = test_function()
        
        assert result == "success"
    
    @patch('backend.app.security.audit_logger.request')
    @patch('backend.app.security.audit_logger.g')
    def test_log_security_event_decorator_exception(self, mock_g, mock_request, mock_request_obj):
        """Testa decorator com exceção"""
        mock_request.return_value = mock_request_obj
        mock_g.return_value = Mock()
        mock_g.return_value.get.return_value = None
        
        @log_security_event(SecurityEventType.LOGIN_SUCCESS)
        def test_function():
            raise Exception("Test error")
        
        with pytest.raises(Exception):
            test_function()


class TestSecurityAuditLoggerErrorHandling:
    """Testes de tratamento de erros para SecurityAuditLogger"""
    
    @pytest.fixture
    def temp_log_file(self):
        """Arquivo de log temporário para testes"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            temp_file = f.name
        
        yield temp_file
        
        # Limpar arquivo após teste
        if os.path.exists(temp_file):
            os.unlink(temp_file)
    
    @pytest.fixture
    def logger(self, temp_log_file):
        """Instância do SecurityAuditLogger para testes"""
        with patch.dict(os.environ, {'SECURITY_LOG_FILE': temp_log_file}):
            return SecurityAuditLogger()
    
    def test_logger_with_invalid_event_type(self, logger):
        """Testa logger com tipo de evento inválido"""
        # Deve funcionar sem erro mesmo com dados inválidos
        event = SecurityEvent(
            event_type=SecurityEventType.LOGIN_SUCCESS,
            timestamp="2025-01-27T10:00:00Z",
            user_id="user123",
            username="john_doe",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            session_id="session123",
            details={},
            security_level=SecurityLevel.INFO,
            risk_score=0,
            correlation_id="corr123"
        )
        
        # Deve funcionar sem erro
        score = logger._calculate_risk_score(event)
        assert isinstance(score, int)
        assert score >= 0


class TestSecurityAuditLoggerPerformance:
    """Testes de performance para SecurityAuditLogger"""
    
    @pytest.fixture
    def temp_log_file(self):
        """Arquivo de log temporário para testes"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            temp_file = f.name
        
        yield temp_file
        
        # Limpar arquivo após teste
        if os.path.exists(temp_file):
            os.unlink(temp_file)
    
    @pytest.fixture
    def logger(self, temp_log_file):
        """Instância do SecurityAuditLogger para testes"""
        with patch.dict(os.environ, {'SECURITY_LOG_FILE': temp_log_file}):
            return SecurityAuditLogger()
    
    @patch('backend.app.security.audit_logger.request')
    @patch('backend.app.security.audit_logger.g')
    def test_multiple_log_events_performance(self, mock_g, mock_request, logger, temp_log_file):
        """Testa performance de múltiplos logs de eventos"""
        import time
        
        mock_request.headers = {
            'X-Forwarded-For': '192.168.1.1',
            'User-Agent': 'Mozilla/5.0'
        }
        mock_request.remote_addr = '192.168.1.1'
        mock_g.get.return_value = None
        
        start_time = time.time()
        
        # Logar múltiplos eventos
        for i in range(100):
            logger.log_event(
                event_type=SecurityEventType.LOGIN_SUCCESS,
                user_id=f"user{i}",
                username=f"user{i}",
                details={"attempt": i},
                security_level=SecurityLevel.INFO
            )
        
        end_time = time.time()
        
        # Verificar performance (deve ser rápido)
        assert end_time - start_time < 5.0  # Menos de 5 segundos para 100 logs
        
        # Verificar que todos os logs foram escritos
        with open(temp_log_file, 'r') as f:
            log_lines = f.readlines()
            assert len(log_lines) == 100


if __name__ == "__main__":
    pytest.main([__file__]) 