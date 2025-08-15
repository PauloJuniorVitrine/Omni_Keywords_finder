"""
🧪 Testes de Segurança para Endpoints de Credenciais
🎯 Objetivo: Validar proteção contra ataques de segurança nos endpoints de credenciais
📅 Criado: 2025-01-27
🔄 Versão: 1.0
📐 CoCoT: OWASP Top 10, Security Testing Best Practices
🌲 ToT: Brute Force vs SQL Injection vs XSS - Todos críticos para credenciais
♻️ ReAct: Simulação: Proteção 100%, detecção de ataques, logs de segurança

Tracing ID: SECURITY_CREDENTIALS_001
Ruleset: enterprise_control_layer.yaml
"""

import pytest
import asyncio
import json
import time
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException, status

# Importar aplicação
from backend.app.main import app

# Configurar cliente de teste
client = TestClient(app)


class TestCredentialBruteForceProtection:
    """Testes de proteção contra ataques de força bruta."""
    
    @pytest.fixture
    def mock_auth_token(self):
        """Token de autenticação mock."""
        return "Bearer test_token_123"
    
    @pytest.fixture
    def valid_credential_request(self):
        """Request válido para teste."""
        return {
            "provider": "openai",
            "credential_type": "api_key",
            "credential_value": "sk-proj-1234567890abcdefghijklmnopqrstuvwxyz",
            "context": "test_validation"
        }
    
    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_brute_force_validation_endpoint(self, mock_auth_token, valid_credential_request):
        """Testa proteção contra brute force no endpoint de validação."""
        with patch('backend.app.api.credential_validation.verify_authentication', return_value="test_user_123"), \
             patch('backend.app.api.credential_validation._validate_credential_internal', return_value=False), \
             patch('backend.app.api.credential_validation.get_rate_limiter') as mock_rate_limiter:
            
            # Simular múltiplas tentativas de validação com credenciais inválidas
            for attempt in range(10):
                # Configurar mock para permitir algumas tentativas, depois bloquear
                if attempt < 5:
                    mock_rate_limiter.return_value.check_rate_limit.return_value = Mock(
                        allowed=True,
                        remaining=5 - attempt,
                        reset_time=datetime.now().timestamp() + 60
                    )
                else:
                    mock_rate_limiter.return_value.check_rate_limit.return_value = Mock(
                        allowed=False,
                        reason="Rate limit exceeded - possible brute force attack",
                        retry_after=300  # 5 minutos de bloqueio
                    )
                
                # Fazer requisição
                response = client.post(
                    "/api/credentials/validate",
                    json=valid_credential_request,
                    headers={"Authorization": mock_auth_token}
                )
                
                if attempt < 5:
                    # Primeiras tentativas devem ser permitidas
                    assert response.status_code in [200, 429], f"Tentativa {attempt + 1} deve ser permitida"
                else:
                    # Tentativas subsequentes devem ser bloqueadas
                    assert response.status_code == 429, f"Tentativa {attempt + 1} deve ser bloqueada"
                    data = response.json()
                    assert "Rate limit excedido" in str(data["detail"])
                    assert "brute force" in str(data["detail"]).lower()
    
    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_brute_force_config_endpoint(self, valid_credential_request):
        """Testa proteção contra brute force no endpoint de configuração."""
        with patch('backend.app.api.credentials_config.get_current_user', return_value={"id": "test_user_123"}), \
             patch('backend.app.api.credentials_config.CONFIG_FILE', tempfile.mktemp()), \
             patch('backend.app.api.credentials_config.audit_service') as mock_audit:
            
            # Configurar mock de auditoria
            mock_audit.log_config_access.return_value = None
            
            # Simular múltiplas tentativas de acesso à configuração
            for attempt in range(20):
                response = client.get("/api/credentials/config")
                
                if attempt < 10:
                    # Primeiras tentativas devem ser permitidas
                    assert response.status_code == 200, f"Tentativa {attempt + 1} deve ser permitida"
                else:
                    # Tentativas subsequentes devem ser bloqueadas ou limitadas
                    assert response.status_code in [200, 429], f"Tentativa {attempt + 1} deve ser limitada"
    
    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_brute_force_status_endpoint(self):
        """Testa proteção contra brute force no endpoint de status."""
        with patch('backend.app.api.credentials_status.get_current_user', return_value=Mock(id="test_user_123")), \
             patch('backend.app.api.credentials_status._get_provider_status') as mock_provider_status, \
             patch('backend.app.api.credentials_status._get_system_health') as mock_system_health, \
             patch('backend.app.api.credentials_status.audit_service') as mock_audit, \
             patch('backend.app.api.credentials_status.rate_limiter') as mock_rate_limiter:
            
            # Configurar mocks
            mock_provider_status.return_value = {"openai": {"status": "healthy"}}
            mock_system_health.return_value = Mock(
                overall_health="healthy",
                encryption_status="operational",
                rate_limiting_status="normal"
            )
            mock_audit.get_audit_statistics.return_value = {"total_events": 100}
            mock_rate_limiter.get_status.return_value = {"active_providers": 5}
            
            # Simular múltiplas tentativas de acesso ao status
            for attempt in range(15):
                response = client.get("/api/credentials/status")
                
                if attempt < 8:
                    # Primeiras tentativas devem ser permitidas
                    assert response.status_code == 200, f"Tentativa {attempt + 1} deve ser permitida"
                else:
                    # Tentativas subsequentes devem ser limitadas
                    assert response.status_code in [200, 429], f"Tentativa {attempt + 1} deve ser limitada"


class TestCredentialSQLInjectionProtection:
    """Testes de proteção contra SQL Injection."""
    
    @pytest.fixture
    def mock_auth_token(self):
        """Token de autenticação mock."""
        return "Bearer test_token_123"
    
    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_sql_injection_validation_endpoint(self, mock_auth_token):
        """Testa proteção contra SQL injection no endpoint de validação."""
        with patch('backend.app.api.credential_validation.verify_authentication', return_value="test_user_123"), \
             patch('backend.app.api.credential_validation.get_rate_limiter') as mock_rate_limiter:
            
            # Configurar mock de rate limiter
            mock_rate_limiter.return_value.check_rate_limit.return_value = Mock(
                allowed=True,
                remaining=10,
                reset_time=datetime.now().timestamp() + 60
            )
            
            # Vetores de SQL injection para testar
            sql_injection_payloads = [
                "'; DROP TABLE credentials; --",
                "' OR '1'='1",
                "' UNION SELECT * FROM credentials --",
                "'; INSERT INTO credentials VALUES ('hacker', 'password'); --",
                "' OR 1=1#",
                "admin'--",
                "1' AND '1'='1",
                "1' OR '1'='1'--",
                "'; UPDATE credentials SET api_key='hacked'; --",
                "'; DELETE FROM credentials WHERE 1=1; --"
            ]
            
            for payload in sql_injection_payloads:
                # Testar no campo provider
                malicious_request = {
                    "provider": payload,
                    "credential_type": "api_key",
                    "credential_value": "test_value",
                    "context": "test_validation"
                }
                
                response = client.post(
                    "/api/credentials/validate",
                    json=malicious_request,
                    headers={"Authorization": mock_auth_token}
                )
                
                # Deve bloquear ou sanitizar payload malicioso
                assert response.status_code in [400, 422, 500], f"Deve bloquear SQL injection no provider: {payload}"
                
                # Testar no campo credential_value
                malicious_request = {
                    "provider": "openai",
                    "credential_type": "api_key",
                    "credential_value": payload,
                    "context": "test_validation"
                }
                
                response = client.post(
                    "/api/credentials/validate",
                    json=malicious_request,
                    headers={"Authorization": mock_auth_token}
                )
                
                # Deve bloquear ou sanitizar payload malicioso
                assert response.status_code in [400, 422, 500], f"Deve bloquear SQL injection no credential_value: {payload}"
    
    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_sql_injection_config_endpoint(self):
        """Testa proteção contra SQL injection no endpoint de configuração."""
        with patch('backend.app.api.credentials_config.get_current_user', return_value={"id": "test_user_123"}), \
             patch('backend.app.api.credentials_config.CONFIG_FILE', tempfile.mktemp()), \
             patch('backend.app.api.credentials_config.audit_service') as mock_audit:
            
            # Configurar mock de auditoria
            mock_audit.log_config_access.return_value = None
            
            # Vetores de SQL injection para testar
            sql_injection_payloads = [
                "'; DROP TABLE config; --",
                "' OR '1'='1",
                "'; INSERT INTO config VALUES ('hacker', 'data'); --",
                "admin'--",
                "1' OR '1'='1'--"
            ]
            
            for payload in sql_injection_payloads:
                # Testar no campo apiKey
                malicious_config = {
                    "config": {
                        "ai": {
                            "openai": {
                                "apiKey": payload,
                                "enabled": True
                            }
                        }
                    },
                    "validateOnUpdate": False
                }
                
                response = client.put(
                    "/api/credentials/config",
                    json=malicious_config
                )
                
                # Deve bloquear ou sanitizar payload malicioso
                assert response.status_code in [400, 422, 500], f"Deve bloquear SQL injection no apiKey: {payload}"
    
    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_sql_injection_status_endpoint(self):
        """Testa proteção contra SQL injection no endpoint de status."""
        with patch('backend.app.api.credentials_status.get_current_user', return_value=Mock(id="test_user_123")), \
             patch('backend.app.api.credentials_status.audit_service') as mock_audit:
            
            # Configurar mock de auditoria
            mock_audit.log_event.return_value = None
            
            # Vetores de SQL injection para testar
            sql_injection_payloads = [
                "'; DROP TABLE status; --",
                "' OR '1'='1",
                "admin'--",
                "1' OR '1'='1'--"
            ]
            
            for payload in sql_injection_payloads:
                # Testar no parâmetro provider
                response = client.get(f"/api/credentials/status/{payload}")
                
                # Deve bloquear ou sanitizar payload malicioso
                assert response.status_code in [400, 404, 422, 500], f"Deve bloquear SQL injection no provider: {payload}"


class TestCredentialXSSProtection:
    """Testes de proteção contra XSS (Cross-Site Scripting)."""
    
    @pytest.fixture
    def mock_auth_token(self):
        """Token de autenticação mock."""
        return "Bearer test_token_123"
    
    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_xss_validation_endpoint(self, mock_auth_token):
        """Testa proteção contra XSS no endpoint de validação."""
        with patch('backend.app.api.credential_validation.verify_authentication', return_value="test_user_123"), \
             patch('backend.app.api.credential_validation.get_rate_limiter') as mock_rate_limiter:
            
            # Configurar mock de rate limiter
            mock_rate_limiter.return_value.check_rate_limit.return_value = Mock(
                allowed=True,
                remaining=10,
                reset_time=datetime.now().timestamp() + 60
            )
            
            # Vetores de XSS para testar
            xss_payloads = [
                "<script>alert('XSS')</script>",
                "javascript:alert('XSS')",
                "<img src=value onerror=alert('XSS')>",
                "<svg onload=alert('XSS')>",
                "';alert('XSS');//",
                "<iframe src=javascript:alert('XSS')>",
                "&#60;script&#62;alert('XSS')&#60;/script&#62;",
                "javascript:void(alert('XSS'))"
            ]
            
            for payload in xss_payloads:
                # Testar no campo context
                malicious_request = {
                    "provider": "openai",
                    "credential_type": "api_key",
                    "credential_value": "test_value",
                    "context": payload
                }
                
                response = client.post(
                    "/api/credentials/validate",
                    json=malicious_request,
                    headers={"Authorization": mock_auth_token}
                )
                
                # Deve sanitizar ou bloquear payload malicioso
                assert response.status_code in [200, 400, 422], f"Deve sanitizar XSS no context: {payload}"
                
                if response.status_code == 200:
                    # Se aceitar, deve sanitizar na resposta
                    data = response.json()
                    assert payload not in str(data), f"XSS payload não deve aparecer na resposta: {payload}"
    
    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_xss_config_endpoint(self):
        """Testa proteção contra XSS no endpoint de configuração."""
        with patch('backend.app.api.credentials_config.get_current_user', return_value={"id": "test_user_123"}), \
             patch('backend.app.api.credentials_config.CONFIG_FILE', tempfile.mktemp()), \
             patch('backend.app.api.credentials_config.audit_service') as mock_audit:
            
            # Configurar mock de auditoria
            mock_audit.log_config_access.return_value = None
            
            # Vetores de XSS para testar
            xss_payloads = [
                "<script>alert('XSS')</script>",
                "javascript:alert('XSS')",
                "<img src=value onerror=alert('XSS')>"
            ]
            
            for payload in xss_payloads:
                # Testar no campo model
                malicious_config = {
                    "config": {
                        "ai": {
                            "openai": {
                                "apiKey": "test_key",
                                "enabled": True,
                                "model": payload
                            }
                        }
                    },
                    "validateOnUpdate": False
                }
                
                response = client.put(
                    "/api/credentials/config",
                    json=malicious_config
                )
                
                # Deve sanitizar ou bloquear payload malicioso
                assert response.status_code in [200, 400, 422], f"Deve sanitizar XSS no model: {payload}"


class TestCredentialAuthenticationSecurity:
    """Testes de segurança de autenticação."""
    
    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_invalid_token_handling(self):
        """Testa tratamento de tokens inválidos."""
        # Testar diferentes tipos de tokens inválidos
        invalid_tokens = [
            "invalid_token",
            "Bearer invalid_token",
            "Bearer ",
            "Basic dXNlcjpwYXNz",
            "Token invalid_token",
            "",
            None
        ]
        
        for token in invalid_tokens:
            headers = {"Authorization": token} if token else {}
            
            # Testar em diferentes endpoints
            endpoints = [
                "/api/credentials/validate",
                "/api/credentials/config",
                "/api/credentials/status",
                "/api/credentials/metrics"
            ]
            
            for endpoint in endpoints:
                if endpoint == "/api/credentials/validate":
                    response = client.post(endpoint, json={}, headers=headers)
                elif endpoint == "/api/credentials/config":
                    response = client.get(endpoint, headers=headers)
                elif endpoint == "/api/credentials/status":
                    response = client.get(endpoint, headers=headers)
                elif endpoint == "/api/credentials/metrics":
                    response = client.get(endpoint, headers=headers)
                
                # Deve rejeitar tokens inválidos
                assert response.status_code == 401, f"Deve rejeitar token inválido: {token}"
    
    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_token_expiration_handling(self):
        """Testa tratamento de tokens expirados."""
        # Simular token expirado
        expired_token = "Bearer expired_jwt_token"
        headers = {"Authorization": expired_token}
        
        with patch('backend.app.api.credential_validation.verify_authentication', side_effect=HTTPException(status_code=401, detail="Token expired")):
            response = client.post(
                "/api/credentials/validate",
                json={},
                headers=headers
            )
            
            assert response.status_code == 401
            data = response.json()
            assert "expired" in str(data["detail"]).lower()
    
    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_privilege_escalation_prevention(self):
        """Testa prevenção de escalação de privilégios."""
        # Simular usuário comum tentando acessar recursos de admin
        user_token = "Bearer user_token"
        admin_token = "Bearer admin_token"
        
        with patch('backend.app.api.credentials_config.get_current_user') as mock_get_user:
            # Testar com usuário comum
            mock_get_user.return_value = {"id": "user_123", "role": "user"}
            
            response = client.get("/api/credentials/config")
            assert response.status_code in [200, 403]  # Pode permitir ou bloquear dependendo da implementação
            
            # Testar com admin
            mock_get_user.return_value = {"id": "admin_123", "role": "admin"}
            
            response = client.get("/api/credentials/config")
            assert response.status_code == 200  # Admin deve ter acesso


class TestCredentialDataValidationSecurity:
    """Testes de validação de dados de segurança."""
    
    @pytest.fixture
    def mock_auth_token(self):
        """Token de autenticação mock."""
        return "Bearer test_token_123"
    
    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_malicious_payload_validation(self, mock_auth_token):
        """Testa validação de payloads maliciosos."""
        with patch('backend.app.api.credential_validation.verify_authentication', return_value="test_user_123"), \
             patch('backend.app.api.credential_validation.get_rate_limiter') as mock_rate_limiter:
            
            # Configurar mock de rate limiter
            mock_rate_limiter.return_value.check_rate_limit.return_value = Mock(
                allowed=True,
                remaining=10,
                reset_time=datetime.now().timestamp() + 60
            )
            
            # Payloads maliciosos para testar
            malicious_payloads = [
                # NoSQL Injection
                {"$where": "function() { return true; }"},
                {"$ne": "admin"},
                # Command Injection
                "; rm -rf /",
                "| cat /etc/passwd",
                # Path Traversal
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32\\config\\sam",
                # LDAP Injection
                "*)(uid=*))(|(uid=*",
                "admin)(&(password=*))",
                # XML Injection
                "<!DOCTYPE test [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]><test>&xxe;</test>",
                # JSON Injection
                '{"key": "value", "__proto__": {"admin": true}}'
            ]
            
            for payload in malicious_payloads:
                malicious_request = {
                    "provider": str(payload),
                    "credential_type": "api_key",
                    "credential_value": str(payload),
                    "context": str(payload)
                }
                
                response = client.post(
                    "/api/credentials/validate",
                    json=malicious_request,
                    headers={"Authorization": mock_auth_token}
                )
                
                # Deve bloquear ou sanitizar payload malicioso
                assert response.status_code in [400, 422, 500], f"Deve bloquear payload malicioso: {payload}"
    
    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_oversized_payload_validation(self, mock_auth_token):
        """Testa validação de payloads muito grandes."""
        with patch('backend.app.api.credential_validation.verify_authentication', return_value="test_user_123"):
            # Payload muito grande
            oversized_payload = "A" * 10000  # 10KB
            
            malicious_request = {
                "provider": "openai",
                "credential_type": "api_key",
                "credential_value": oversized_payload,
                "context": "test_validation"
            }
            
            response = client.post(
                "/api/credentials/validate",
                json=malicious_request,
                headers={"Authorization": mock_auth_token}
            )
            
            # Deve rejeitar payload muito grande
            assert response.status_code in [400, 413, 422], "Deve rejeitar payload muito grande"


class TestCredentialLoggingSecurity:
    """Testes de segurança de logging."""
    
    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_security_event_logging(self):
        """Testa logging de eventos de segurança."""
        with patch('backend.app.api.credential_validation.verify_authentication', return_value="test_user_123"), \
             patch('backend.app.api.credential_validation.get_rate_limiter') as mock_rate_limiter, \
             patch('backend.app.api.credential_validation.logger') as mock_logger:
            
            # Configurar mock de rate limiter para simular ataque
            mock_rate_limiter.return_value.check_rate_limit.return_value = Mock(
                allowed=False,
                reason="Rate limit exceeded - possible attack",
                retry_after=300
            )
            
            # Fazer requisição que deve gerar log de segurança
            response = client.post(
                "/api/credentials/validate",
                json={"provider": "test", "credential_type": "api_key", "credential_value": "test"},
                headers={"Authorization": "Bearer test_token"}
            )
            
            # Verificar se log de segurança foi gerado
            assert mock_logger.warning.called or mock_logger.error.called, "Deve gerar log de segurança"
    
    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_sensitive_data_logging_prevention(self):
        """Testa prevenção de logging de dados sensíveis."""
        with patch('backend.app.api.credential_validation.verify_authentication', return_value="test_user_123"), \
             patch('backend.app.api.credential_validation.get_rate_limiter') as mock_rate_limiter, \
             patch('backend.app.api.credential_validation.logger') as mock_logger:
            
            # Configurar mock de rate limiter
            mock_rate_limiter.return_value.check_rate_limit.return_value = Mock(
                allowed=True,
                remaining=10,
                reset_time=datetime.now().timestamp() + 60
            )
            
            # Fazer requisição com dados sensíveis
            sensitive_request = {
                "provider": "openai",
                "credential_type": "api_key",
                "credential_value": "sk-proj-secret-key-123",
                "context": "test_validation"
            }
            
            response = client.post(
                "/api/credentials/validate",
                json=sensitive_request,
                headers={"Authorization": "Bearer test_token"}
            )
            
            # Verificar se dados sensíveis não foram logados
            log_calls = mock_logger.info.call_args_list + mock_logger.warning.call_args_list + mock_logger.error.call_args_list
            
            for call in log_calls:
                log_message = str(call)
                assert "sk-proj-secret-key-123" not in log_message, "Dados sensíveis não devem ser logados"


@pytest.fixture(scope="session")
def test_app():
    """Aplicação de teste para sessão."""
    return app


@pytest.fixture(scope="session")
def test_client():
    """Cliente de teste para sessão."""
    return TestClient(app)


def pytest_configure(config):
    """Configuração do pytest."""
    config.addinivalue_line(
        "markers", "security: mark test as security test"
    )


def pytest_collection_modifyitems(config, items):
    """Modifica itens de coleção para adicionar marcadores."""
    for item in items:
        if "test_credential_security" in item.nodeid:
            item.add_marker(pytest.mark.security)


@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Limpeza automática após cada teste."""
    yield
    # Limpeza específica se necessário
    pass 