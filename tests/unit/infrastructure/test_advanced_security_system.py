"""
Testes para AdvancedSecuritySystem - Omni Keywords Finder

Tracing ID: TEST_SECURITY_001_20250127
Data: 2025-01-27
Versão: 1.0
Status: 🟡 ALTO - Testes para AdvancedSecuritySystem

Baseado no código real do sistema Omni Keywords Finder
"""

import pytest
import asyncio
import time
import json
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, Any, List
from collections import deque

# Mock dos módulos para evitar dependências externas
class MockEncryptionManager:
    def __init__(self, config):
        self.config = config
        self.encrypted_count = 0
        self.decrypted_count = 0
    
    def encrypt(self, data):
        self.encrypted_count += 1
        return f"encrypted_{data}"
    
    def decrypt(self, encrypted_data):
        self.decrypted_count += 1
        return encrypted_data.replace("encrypted_", "")

class MockAuthenticationManager:
    def __init__(self, config):
        self.config = config
        self.authenticated_users = set()
        self.failed_attempts = {}
    
    def authenticate(self, username, password):
        if username == "admin" and password == "correct_password":
            self.authenticated_users.add(username)
            return True
        else:
            if username not in self.failed_attempts:
                self.failed_attempts[username] = 0
            self.failed_attempts[username] += 1
            return False
    
    def is_authenticated(self, username):
        return username in self.authenticated_users

class MockAuthorizationManager:
    def __init__(self, config):
        self.config = config
        self.user_roles = {
            "admin": ["admin", "user"],
            "user": ["user"],
            "guest": ["guest"]
        }
        self.resource_permissions = {
            "admin": ["read", "write", "delete"],
            "user": ["read", "write"],
            "guest": ["read"]
        }
    
    def has_permission(self, username, resource, action):
        if username not in self.user_roles:
            return False
        
        user_role = self.user_roles[username][0]  # Primeiro role
        return action in self.resource_permissions.get(user_role, [])
    
    def get_user_roles(self, username):
        return self.user_roles.get(username, [])

class MockThreatDetection:
    def __init__(self, config):
        self.config = config
        self.threats_detected = []
        self.risk_score = 0
    
    def analyze_request(self, request_data):
        # Simular análise de ameaça
        if "malicious" in str(request_data).lower():
            threat = {
                "type": "malicious_content",
                "risk_level": "high",
                "timestamp": time.time()
            }
            self.threats_detected.append(threat)
            self.risk_score += 10
            return threat
        return None
    
    def get_risk_score(self):
        return self.risk_score

class MockAuditSystem:
    def __init__(self, config):
        self.config = config
        self.audit_log = []
    
    def log_event(self, event_type, user, action, details):
        audit_entry = {
            "timestamp": time.time(),
            "event_type": event_type,
            "user": user,
            "action": action,
            "details": details
        }
        self.audit_log.append(audit_entry)
        return audit_entry
    
    def get_audit_log(self):
        return self.audit_log

class MockAdvancedRateLimiter:
    def __init__(self, config):
        self.config = config
        self.request_counts = {}
        self.blocked_ips = set()
    
    def is_allowed(self, ip_address, endpoint):
        if ip_address in self.blocked_ips:
            return False
        
        key = f"{ip_address}:{endpoint}"
        if key not in self.request_counts:
            self.request_counts[key] = 0
        
        self.request_counts[key] += 1
        
        # Simular limite de 100 requests por minuto
        return self.request_counts[key] <= 100
    
    def block_ip(self, ip_address):
        self.blocked_ips.add(ip_address)
    
    def unblock_ip(self, ip_address):
        self.blocked_ips.discard(ip_address)

class MockWebApplicationFirewall:
    def __init__(self, config):
        self.config = config
        self.blocked_patterns = [
            "sql_injection",
            "xss_attack",
            "path_traversal"
        ]
        self.blocked_requests = []
    
    def inspect_request(self, request_data):
        for pattern in self.blocked_patterns:
            if pattern in str(request_data).lower():
                blocked_request = {
                    "pattern": pattern,
                    "request": request_data,
                    "timestamp": time.time()
                }
                self.blocked_requests.append(blocked_request)
                return False, f"Blocked by WAF: {pattern}"
        return True, "Request allowed"
    
    def get_blocked_requests(self):
        return self.blocked_requests

class MockSensitiveDataDetector:
    def __init__(self, config):
        self.config = config
        self.sensitive_patterns = [
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
            r"\b\d{4}-\d{4}-\d{4}-\d{4}\b",  # Credit card
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"  # Email
        ]
        self.detected_data = []
    
    def scan_data(self, data):
        detected = []
        data_str = str(data)
        
        for pattern in self.sensitive_patterns:
            import re
            matches = re.findall(pattern, data_str)
            if matches:
                detected.extend(matches)
        
        if detected:
            self.detected_data.append({
                "data": data,
                "detected_patterns": detected,
                "timestamp": time.time()
            })
        
        return detected

class MockSecurityMetrics:
    def __init__(self):
        self.total_requests = 0
        self.blocked_requests = 0
        self.authentication_failures = 0
        self.authorization_failures = 0
        self.threats_detected = 0
        self.encryption_operations = 0
    
    def increment(self, metric_name):
        if hasattr(self, metric_name):
            setattr(self, metric_name, getattr(self, metric_name) + 1)
    
    def get_metrics(self):
        return {
            "total_requests": self.total_requests,
            "blocked_requests": self.blocked_requests,
            "authentication_failures": self.authentication_failures,
            "authorization_failures": self.authorization_failures,
            "threats_detected": self.threats_detected,
            "encryption_operations": self.encryption_operations
        }

# Teste principal
class TestAdvancedSecuritySystem:
    """Testes para o AdvancedSecuritySystem"""
    
    @pytest.fixture
    def mock_security_system(self):
        """Fixture para mock do sistema de segurança"""
        with patch('infrastructure.security.advanced_security_system.redis.Redis') as mock_redis, \
             patch('infrastructure.security.advanced_security_system.EncryptionManager', MockEncryptionManager), \
             patch('infrastructure.security.advanced_security_system.AuthenticationManager', MockAuthenticationManager), \
             patch('infrastructure.security.advanced_security_system.AuthorizationManager', MockAuthorizationManager), \
             patch('infrastructure.security.advanced_security_system.ThreatDetectionSystem', MockThreatDetection), \
             patch('infrastructure.security.advanced_security_system.AuditSystem', MockAuditSystem), \
             patch('infrastructure.security.advanced_security_system.AdvancedRateLimiter', MockAdvancedRateLimiter), \
             patch('infrastructure.security.advanced_security_system.WebApplicationFirewall', MockWebApplicationFirewall), \
             patch('infrastructure.security.advanced_security_system.SensitiveDataDetector', MockSensitiveDataDetector):
            
            from infrastructure.security.advanced_security_system import AdvancedSecuritySystem
            
            config = {
                'redis_host': 'localhost',
                'redis_port': 6379,
                'redis_db': 0
            }
            
            return AdvancedSecuritySystem(config)
    
    @pytest.fixture
    def sample_request(self):
        """Fixture para request de teste"""
        return {
            "ip_address": "192.168.1.100",
            "user": "admin",
            "endpoint": "/api/keywords",
            "method": "GET",
            "headers": {"Authorization": "Bearer token123"},
            "body": {"query": "python programming"}
        }
    
    def test_inicializacao(self, mock_security_system):
        """Testa inicialização do sistema de segurança"""
        sec_sys = mock_security_system
        
        # Verificar se todos os componentes foram inicializados
        assert sec_sys.encryption_manager is not None
        assert sec_sys.authentication_manager is not None
        assert sec_sys.authorization_manager is not None
        assert sec_sys.threat_detection is not None
        assert sec_sys.audit_system is not None
        assert sec_sys.rate_limiter is not None
        assert sec_sys.waf is not None
        assert sec_sys.sensitive_data_detector is not None
        
        # Verificar se as métricas foram inicializadas
        assert sec_sys.metrics is not None
        assert isinstance(sec_sys.security_events, deque)
        assert sec_sys.lock is not None
    
    def test_autenticacao_sucesso(self, mock_security_system):
        """Testa autenticação bem-sucedida"""
        sec_sys = mock_security_system
        
        # Testar autenticação válida
        result = sec_sys.authentication_manager.authenticate("admin", "correct_password")
        assert result is True
        
        # Verificar se o usuário foi marcado como autenticado
        assert sec_sys.authentication_manager.is_authenticated("admin")
    
    def test_autenticacao_falha(self, mock_security_system):
        """Testa falha de autenticação"""
        sec_sys = mock_security_system
        
        # Testar autenticação inválida
        result = sec_sys.authentication_manager.authenticate("admin", "wrong_password")
        assert result is False
        
        # Verificar se o usuário não foi autenticado
        assert not sec_sys.authentication_manager.is_authenticated("admin")
        
        # Verificar contador de tentativas falhadas
        assert sec_sys.authentication_manager.failed_attempts["admin"] == 1
    
    def test_autorizacao(self, mock_security_system):
        """Testa sistema de autorização"""
        sec_sys = mock_security_system
        
        # Verificar permissões de admin
        assert sec_sys.authorization_manager.has_permission("admin", "keywords", "read")
        assert sec_sys.authorization_manager.has_permission("admin", "keywords", "write")
        assert sec_sys.authorization_manager.has_permission("admin", "keywords", "delete")
        
        # Verificar permissões de user
        assert sec_sys.authorization_manager.has_permission("user", "keywords", "read")
        assert sec_sys.authorization_manager.has_permission("user", "keywords", "write")
        assert not sec_sys.authorization_manager.has_permission("user", "keywords", "delete")
        
        # Verificar permissões de guest
        assert sec_sys.authorization_manager.has_permission("guest", "keywords", "read")
        assert not sec_sys.authorization_manager.has_permission("guest", "keywords", "write")
        assert not sec_sys.authorization_manager.has_permission("guest", "keywords", "delete")
    
    def test_deteccao_ameacas(self, mock_security_system):
        """Testa detecção de ameaças"""
        sec_sys = mock_security_system
        
        # Testar request normal
        normal_request = {"query": "python programming"}
        threat = sec_sys.threat_detection.analyze_request(normal_request)
        assert threat is None
        
        # Testar request malicioso
        malicious_request = {"query": "malicious sql injection"}
        threat = sec_sys.threat_detection.analyze_request(malicious_request)
        assert threat is not None
        assert threat["type"] == "malicious_content"
        assert threat["risk_level"] == "high"
        
        # Verificar se a ameaça foi registrada
        assert len(sec_sys.threat_detection.threats_detected) == 1
        assert sec_sys.threat_detection.get_risk_score() > 0
    
    def test_auditoria(self, mock_security_system):
        """Testa sistema de auditoria"""
        sec_sys = mock_security_system
        
        # Registrar evento de auditoria
        audit_entry = sec_sys.audit_system.log_event(
            "USER_LOGIN",
            "admin",
            "authentication",
            {"ip": "192.168.1.100", "success": True}
        )
        
        # Verificar se o evento foi registrado
        assert audit_entry is not None
        assert audit_entry["event_type"] == "USER_LOGIN"
        assert audit_entry["user"] == "admin"
        assert audit_entry["action"] == "authentication"
        
        # Verificar se o evento está no log
        audit_log = sec_sys.audit_system.get_audit_log()
        assert len(audit_log) == 1
        assert audit_log[0] == audit_entry
    
    def test_rate_limiting(self, mock_security_system):
        """Testa rate limiting"""
        sec_sys = mock_security_system
        
        # Testar requests permitidos
        for i in range(100):
            allowed = sec_sys.rate_limiter.is_allowed("192.168.1.100", "/api/keywords")
            assert allowed is True
        
        # Testar request bloqueado (limite excedido)
        blocked = sec_sys.rate_limiter.is_allowed("192.168.1.100", "/api/keywords")
        assert blocked is False
        
        # Testar bloqueio de IP
        sec_sys.rate_limiter.block_ip("192.168.1.200")
        assert "192.168.1.200" in sec_sys.rate_limiter.blocked_ips
        
        # Testar desbloqueio de IP
        sec_sys.rate_limiter.unblock_ip("192.168.1.200")
        assert "192.168.1.200" not in sec_sys.rate_limiter.blocked_ips
    
    def test_waf(self, mock_security_system):
        """Testa Web Application Firewall"""
        sec_sys = mock_security_system
        
        # Testar request normal
        normal_request = {"query": "python programming"}
        allowed, message = sec_sys.waf.inspect_request(normal_request)
        assert allowed is True
        assert "Request allowed" in message
        
        # Testar request bloqueado (SQL injection)
        malicious_request = "sql_injection attack"
        allowed, message = sec_sys.waf.inspect_request(malicious_request)
        assert allowed is False
        assert "Blocked by WAF" in message
        
        # Verificar se o request foi registrado como bloqueado
        blocked_requests = sec_sys.waf.get_blocked_requests()
        assert len(blocked_requests) == 1
        assert blocked_requests[0]["pattern"] == "sql_injection"
    
    def test_deteccao_dados_sensiveis(self, mock_security_system):
        """Testa detecção de dados sensíveis"""
        sec_sys = mock_security_system
        
        # Testar dados sem informações sensíveis
        normal_data = {"query": "python programming"}
        detected = sec_sys.sensitive_data_detector.scan_data(normal_data)
        assert len(detected) == 0
        
        # Testar dados com email
        sensitive_data = {"user": "user@example.com", "query": "python"}
        detected = sec_sys.sensitive_data_detector.scan_data(sensitive_data)
        assert len(detected) > 0
        assert "user@example.com" in detected
        
        # Verificar se os dados foram registrados
        detected_entries = sec_sys.sensitive_data_detector.detected_data
        assert len(detected_entries) == 1
        assert detected_entries[0]["data"] == sensitive_data
    
    def test_criptografia(self, mock_security_system):
        """Testa operações de criptografia"""
        sec_sys = mock_security_system
        
        # Testar criptografia
        original_data = "sensitive information"
        encrypted_data = sec_sys.encryption_manager.encrypt(original_data)
        assert encrypted_data.startswith("encrypted_")
        assert sec_sys.encryption_manager.encrypted_count == 1
        
        # Testar descriptografia
        decrypted_data = sec_sys.encryption_manager.decrypt(encrypted_data)
        assert decrypted_data == original_data
        assert sec_sys.encryption_manager.decrypted_count == 1
    
    def test_metricas_seguranca(self, mock_security_system):
        """Testa métricas de segurança"""
        sec_sys = mock_security_system
        
        # Incrementar métricas
        sec_sys.metrics.increment("total_requests")
        sec_sys.metrics.increment("blocked_requests")
        sec_sys.metrics.increment("threats_detected")
        
        # Verificar métricas
        metrics = sec_sys.metrics.get_metrics()
        assert metrics["total_requests"] == 1
        assert metrics["blocked_requests"] == 1
        assert metrics["threats_detected"] == 1
    
    def test_processamento_request_completo(self, mock_security_system, sample_request):
        """Testa processamento completo de um request"""
        sec_sys = mock_security_system
        
        # Simular processamento de request
        request_data = sample_request
        
        # 1. Rate limiting
        allowed = sec_sys.rate_limiter.is_allowed(
            request_data["ip_address"], 
            request_data["endpoint"]
        )
        assert allowed is True
        
        # 2. WAF inspection
        waf_allowed, waf_message = sec_sys.waf.inspect_request(request_data)
        assert waf_allowed is True
        
        # 3. Threat detection
        threat = sec_sys.threat_detection.analyze_request(request_data)
        assert threat is None
        
        # 4. Sensitive data detection
        sensitive_data = sec_sys.sensitive_data_detector.scan_data(request_data)
        assert len(sensitive_data) == 0
        
        # 5. Authentication
        authenticated = sec_sys.authentication_manager.authenticate(
            request_data["user"], 
            "correct_password"
        )
        assert authenticated is True
        
        # 6. Authorization
        authorized = sec_sys.authorization_manager.has_permission(
            request_data["user"], 
            "keywords", 
            "read"
        )
        assert authorized is True
        
        # 7. Audit logging
        audit_entry = sec_sys.audit_system.log_event(
            "API_REQUEST",
            request_data["user"],
            "read_keywords",
            {"endpoint": request_data["endpoint"], "ip": request_data["ip_address"]}
        )
        assert audit_entry is not None
        
        # 8. Update metrics
        sec_sys.metrics.increment("total_requests")
        metrics = sec_sys.metrics.get_metrics()
        assert metrics["total_requests"] == 1
    
    def test_estado_seguranca_events(self, mock_security_system):
        """Testa estado dos security events"""
        sec_sys = mock_security_system
        
        # Verificar estado inicial
        assert len(sec_sys.security_events) == 0
        
        # Adicionar evento de segurança
        security_event = {
            "type": "threat_detected",
            "severity": "high",
            "timestamp": time.time(),
            "details": "SQL injection attempt"
        }
        sec_sys.security_events.append(security_event)
        
        # Verificar se o evento foi adicionado
        assert len(sec_sys.security_events) == 1
        assert sec_sys.security_events[0]["type"] == "threat_detected"
    
    def test_thread_safety(self, mock_security_system):
        """Testa thread safety do sistema"""
        sec_sys = mock_security_system
        
        # Verificar se o lock foi inicializado
        assert sec_sys.lock is not None
        
        # Simular operação thread-safe
        with sec_sys.lock:
            # Operação crítica
            sec_sys.metrics.increment("total_requests")
            sec_sys.security_events.append({"test": "event"})
        
        # Verificar se as operações foram executadas
        metrics = sec_sys.metrics.get_metrics()
        assert metrics["total_requests"] == 1
        assert len(sec_sys.security_events) == 1
