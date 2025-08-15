"""
🧪 Testes de Integração para Endpoints de Credenciais
🎯 Objetivo: Validar comportamento completo dos endpoints de credenciais
📅 Criado: 2025-01-27
🔄 Versão: 1.0
📐 CoCoT: Integration Testing Patterns, API Testing Best Practices
🌲 ToT: Unit vs Integration vs E2E - Integration para validar fluxos completos
♻️ ReAct: Simulação: Cobertura 95%, tempo <30s, validação de cenários reais

Tracing ID: INTEGRATION_CREDENTIALS_001
Ruleset: enterprise_control_layer.yaml
"""

import pytest
import asyncio
import json
import tempfile
import os
from datetime import datetime, timezone
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException, status

# Importar aplicação e endpoints
from backend.app.main import app
from backend.app.api.credential_validation import router as validation_router
from backend.app.api.credentials_config import router as config_router
from backend.app.api.credentials_status import router as status_router

# Importar modelos e serviços
from backend.app.services.credential_encryption import CredentialEncryptionService
from backend.app.services.credential_rate_limiter import CredentialRateLimiter
from backend.app.services.credential_audit import CredentialAudit

# Configurar cliente de teste
client = TestClient(app)


class TestCredentialValidationEndpoints:
    """Testes de integração para endpoints de validação de credenciais."""
    
    @pytest.fixture
    def mock_auth_token(self):
        """Token de autenticação mock."""
        return "Bearer test_token_123"
    
    @pytest.fixture
    def valid_openai_request(self):
        """Request válido para OpenAI."""
        return {
            "provider": "openai",
            "credential_type": "api_key",
            "credential_value": "sk-proj-1234567890abcdefghijklmnopqrstuvwxyz",
            "context": "test_validation"
        }
    
    @pytest.fixture
    def valid_google_request(self):
        """Request válido para Google."""
        return {
            "provider": "google",
            "credential_type": "api_key",
            "credential_value": "AIzaSyC1234567890abcdefghijklmnopqrstuvwxyz",
            "context": "test_validation"
        }
    
    @pytest.fixture
    def invalid_request(self):
        """Request inválido."""
        return {
            "provider": "invalid_provider",
            "credential_type": "api_key",
            "credential_value": "",
            "context": "test_validation"
        }
    
    @pytest.mark.asyncio
    async def test_validate_credential_success_openai(self, mock_auth_token, valid_openai_request):
        """Testa validação bem-sucedida de credencial OpenAI."""
        with patch('backend.app.api.credential_validation.verify_authentication', return_value="test_user_123"), \
             patch('backend.app.api.credential_validation._validate_credential_internal', return_value=True), \
             patch('backend.app.api.credential_validation.get_rate_limiter') as mock_rate_limiter, \
             patch('backend.app.api.credential_validation.get_encryption_service') as mock_encryption:
            
            # Configurar mocks
            mock_rate_limiter.return_value.check_rate_limit.return_value = Mock(
                allowed=True,
                remaining=4,
                reset_time=datetime.now().timestamp() + 60
            )
            mock_encryption.return_value.encrypt_credential.return_value = "encrypted_key_123"
            
            # Fazer requisição
            response = client.post(
                "/api/credentials/validate",
                json=valid_openai_request,
                headers={"Authorization": mock_auth_token}
            )
            
            # Validar resposta
            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is True
            assert data["provider"] == "openai"
            assert data["credential_type"] == "api_key"
            assert data["message"] == "Credencial válida"
            assert data["details"]["encrypted"] is True
            assert "validation_time" in data
            assert "rate_limit_info" in data
    
    @pytest.mark.asyncio
    async def test_validate_credential_success_google(self, mock_auth_token, valid_google_request):
        """Testa validação bem-sucedida de credencial Google."""
        with patch('backend.app.api.credential_validation.verify_authentication', return_value="test_user_123"), \
             patch('backend.app.api.credential_validation._validate_credential_internal', return_value=True), \
             patch('backend.app.api.credential_validation.get_rate_limiter') as mock_rate_limiter, \
             patch('backend.app.api.credential_validation.get_encryption_service') as mock_encryption:
            
            # Configurar mocks
            mock_rate_limiter.return_value.check_rate_limit.return_value = Mock(
                allowed=True,
                remaining=4,
                reset_time=datetime.now().timestamp() + 60
            )
            mock_encryption.return_value.encrypt_credential.return_value = "encrypted_key_123"
            
            # Fazer requisição
            response = client.post(
                "/api/credentials/validate",
                json=valid_google_request,
                headers={"Authorization": mock_auth_token}
            )
            
            # Validar resposta
            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is True
            assert data["provider"] == "google"
            assert data["credential_type"] == "api_key"
            assert data["message"] == "Credencial válida"
    
    @pytest.mark.asyncio
    async def test_validate_credential_invalid(self, mock_auth_token, invalid_request):
        """Testa validação de credencial inválida."""
        with patch('backend.app.api.credential_validation.verify_authentication', return_value="test_user_123"), \
             patch('backend.app.api.credential_validation._validate_credential_internal', return_value=False), \
             patch('backend.app.api.credential_validation.get_rate_limiter') as mock_rate_limiter, \
             patch('backend.app.api.credential_validation.get_encryption_service') as mock_encryption:
            
            # Configurar mocks
            mock_rate_limiter.return_value.check_rate_limit.return_value = Mock(
                allowed=True,
                remaining=4,
                reset_time=datetime.now().timestamp() + 60
            )
            mock_encryption.return_value.encrypt_credential.return_value = None
            
            # Fazer requisição
            response = client.post(
                "/api/credentials/validate",
                json=invalid_request,
                headers={"Authorization": mock_auth_token}
            )
            
            # Validar resposta
            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is False
            assert data["message"] == "Credencial inválida"
            assert data["details"]["encrypted"] is False
    
    @pytest.mark.asyncio
    async def test_validate_credential_rate_limit_exceeded(self, mock_auth_token, valid_openai_request):
        """Testa rate limiting na validação de credenciais."""
        with patch('backend.app.api.credential_validation.verify_authentication', return_value="test_user_123"), \
             patch('backend.app.api.credential_validation.get_rate_limiter') as mock_rate_limiter:
            
            # Configurar mock para rate limit excedido
            mock_rate_limiter.return_value.check_rate_limit.return_value = Mock(
                allowed=False,
                reason="Rate limit exceeded",
                retry_after=60
            )
            
            # Fazer requisição
            response = client.post(
                "/api/credentials/validate",
                json=valid_openai_request,
                headers={"Authorization": mock_auth_token}
            )
            
            # Validar resposta
            assert response.status_code == 429
            data = response.json()
            assert "Rate limit excedido" in data["detail"]["message"]
            assert data["detail"]["retry_after"] == 60
    
    @pytest.mark.asyncio
    async def test_validate_credential_unauthorized(self, valid_openai_request):
        """Testa validação sem autenticação."""
        # Fazer requisição sem token
        response = client.post(
            "/api/credentials/validate",
            json=valid_openai_request
        )
        
        # Validar resposta
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_validate_credential_internal_error(self, mock_auth_token, valid_openai_request):
        """Testa erro interno na validação."""
        with patch('backend.app.api.credential_validation.verify_authentication', return_value="test_user_123"), \
             patch('backend.app.api.credential_validation._validate_credential_internal', side_effect=Exception("Internal error")), \
             patch('backend.app.api.credential_validation.get_rate_limiter') as mock_rate_limiter:
            
            # Configurar mocks
            mock_rate_limiter.return_value.check_rate_limit.return_value = Mock(
                allowed=True,
                remaining=4,
                reset_time=datetime.now().timestamp() + 60
            )
            
            # Fazer requisição
            response = client.post(
                "/api/credentials/validate",
                json=valid_openai_request,
                headers={"Authorization": mock_auth_token}
            )
            
            # Validar resposta
            assert response.status_code == 500
            data = response.json()
            assert "Erro interno na validação" in data["detail"]["message"]


class TestCredentialConfigEndpoints:
    """Testes de integração para endpoints de configuração de credenciais."""
    
    @pytest.fixture
    def mock_auth_user(self):
        """Usuário autenticado mock."""
        return {"id": "test_user_123", "email": "test@example.com"}
    
    @pytest.fixture
    def valid_config_data(self):
        """Dados de configuração válidos."""
        return {
            "ai": {
                "openai": {
                    "apiKey": "sk-proj-1234567890abcdefghijklmnopqrstuvwxyz",
                    "enabled": True,
                    "model": "gpt-4",
                    "maxTokens": 4096,
                    "temperature": 0.7
                },
                "google": {
                    "apiKey": "AIzaSyC1234567890abcdefghijklmnopqrstuvwxyz",
                    "enabled": True,
                    "model": "gemini-pro",
                    "maxTokens": 4096,
                    "temperature": 0.7
                }
            },
            "social": {
                "instagram": {
                    "username": "test_user",
                    "password": "test_password",
                    "sessionId": "test_session"
                }
            },
            "analytics": {
                "google_analytics": {
                    "clientId": "test_client_id",
                    "clientSecret": "test_client_secret"
                }
            }
        }
    
    @pytest.fixture
    def temp_config_file(self):
        """Arquivo de configuração temporário."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({}, f)
            temp_file = f.name
        
        yield temp_file
        
        # Limpar arquivo
        if os.path.exists(temp_file):
            os.unlink(temp_file)
    
    @pytest.mark.asyncio
    async def test_get_config_success(self, mock_auth_user, temp_config_file):
        """Testa obtenção de configuração com sucesso."""
        with patch('backend.app.api.credentials_config.get_current_user', return_value=mock_auth_user), \
             patch('backend.app.api.credentials_config.CONFIG_FILE', temp_config_file), \
             patch('backend.app.api.credentials_config.audit_service') as mock_audit:
            
            # Configurar mock de auditoria
            mock_audit.log_config_access.return_value = None
            
            # Fazer requisição
            response = client.get("/api/credentials/config")
            
            # Validar resposta
            assert response.status_code == 200
            data = response.json()
            assert "config" in data
            assert "lastUpdated" in data
            assert "isValid" in data
            assert "validationErrors" in data
    
    @pytest.mark.asyncio
    async def test_update_config_success(self, mock_auth_user, valid_config_data, temp_config_file):
        """Testa atualização de configuração com sucesso."""
        with patch('backend.app.api.credentials_config.get_current_user', return_value=mock_auth_user), \
             patch('backend.app.api.credentials_config.CONFIG_FILE', temp_config_file), \
             patch('backend.app.api.credentials_config.encryption_service') as mock_encryption, \
             patch('backend.app.api.credentials_config.audit_service') as mock_audit:
            
            # Configurar mocks
            mock_encryption.encrypt.return_value = "encrypted_value"
            mock_audit.log_config_access.return_value = None
            
            # Dados da requisição
            request_data = {
                "config": valid_config_data,
                "validateOnUpdate": True
            }
            
            # Fazer requisição
            response = client.put(
                "/api/credentials/config",
                json=request_data
            )
            
            # Validar resposta
            assert response.status_code == 200
            data = response.json()
            assert "config" in data
            assert "lastUpdated" in data
            assert "isValid" in data
            assert "validationErrors" in data
    
    @pytest.mark.asyncio
    async def test_update_config_encryption(self, mock_auth_user, valid_config_data, temp_config_file):
        """Testa criptografia automática na atualização."""
        with patch('backend.app.api.credentials_config.get_current_user', return_value=mock_auth_user), \
             patch('backend.app.api.credentials_config.CONFIG_FILE', temp_config_file), \
             patch('backend.app.api.credentials_config.encryption_service') as mock_encryption, \
             patch('backend.app.api.credentials_config.audit_service') as mock_audit:
            
            # Configurar mock de criptografia
            mock_encryption.encrypt.return_value = "encrypted_value"
            mock_audit.log_config_access.return_value = None
            
            # Dados da requisição
            request_data = {
                "config": valid_config_data,
                "validateOnUpdate": False
            }
            
            # Fazer requisição
            response = client.put(
                "/api/credentials/config",
                json=request_data
            )
            
            # Validar resposta
            assert response.status_code == 200
            
            # Verificar se criptografia foi chamada
            assert mock_encryption.encrypt.called
    
    @pytest.mark.asyncio
    async def test_validate_config_endpoint(self, mock_auth_user, temp_config_file):
        """Testa endpoint de validação de configuração."""
        with patch('backend.app.api.credentials_config.get_current_user', return_value=mock_auth_user), \
             patch('backend.app.api.credentials_config.CONFIG_FILE', temp_config_file), \
             patch('backend.app.api.credentials_config.audit_service') as mock_audit:
            
            # Configurar mock de auditoria
            mock_audit.log_config_access.return_value = None
            
            # Fazer requisição
            response = client.post("/api/credentials/config/validate")
            
            # Validar resposta
            assert response.status_code == 200
            data = response.json()
            assert "isValid" in data
            assert "errors" in data
            assert "validatedAt" in data
    
    @pytest.mark.asyncio
    async def test_update_config_validation_error(self, mock_auth_user, temp_config_file):
        """Testa erro de validação na atualização."""
        with patch('backend.app.api.credentials_config.get_current_user', return_value=mock_auth_user), \
             patch('backend.app.api.credentials_config.CONFIG_FILE', temp_config_file), \
             patch('backend.app.api.credentials_config.validate_config', return_value=(False, ["Erro de validação"])), \
             patch('backend.app.api.credentials_config.audit_service') as mock_audit:
            
            # Configurar mock de auditoria
            mock_audit.log_config_access.return_value = None
            
            # Dados da requisição inválida
            invalid_data = {
                "config": {
                    "ai": {
                        "openai": {
                            "apiKey": "",  # API key vazia
                            "enabled": True
                        }
                    }
                },
                "validateOnUpdate": True
            }
            
            # Fazer requisição
            response = client.put(
                "/api/credentials/config",
                json=invalid_data
            )
            
            # Validar resposta
            assert response.status_code == 400
            data = response.json()
            assert "Erro de validação" in str(data["detail"])
    
    @pytest.mark.asyncio
    async def test_get_config_backup_success(self, mock_auth_user, temp_config_file):
        """Testa obtenção de backup de configuração com sucesso."""
        with patch('backend.app.api.credentials_config.get_current_user', return_value=mock_auth_user), \
             patch('backend.app.api.credentials_config.CONFIG_FILE', temp_config_file), \
             patch('backend.app.api.credentials_config.audit_service') as mock_audit, \
             patch('os.path.exists', return_value=True), \
             patch('builtins.open', create=True) as mock_open:
            
            # Configurar mock de arquivo
            mock_file = Mock()
            mock_file.read.return_value = '{"test": "data"}'
            mock_open.return_value.__enter__.return_value = mock_file
            
            # Configurar mock de auditoria
            mock_audit.log_config_access.return_value = None
            
            # Fazer requisição
            response = client.get("/api/credentials/config/backup")
            
            # Validar resposta
            assert response.status_code == 200
            data = response.json()
            assert "backup_files" in data
            assert "latest_backup" in data
            assert "backup_count" in data
    
    @pytest.mark.asyncio
    async def test_get_config_backup_no_backups(self, mock_auth_user, temp_config_file):
        """Testa obtenção de backup quando não há backups."""
        with patch('backend.app.api.credentials_config.get_current_user', return_value=mock_auth_user), \
             patch('backend.app.api.credentials_config.CONFIG_FILE', temp_config_file), \
             patch('backend.app.api.credentials_config.audit_service') as mock_audit, \
             patch('os.path.exists', return_value=False):
            
            # Configurar mock de auditoria
            mock_audit.log_config_access.return_value = None
            
            # Fazer requisição
            response = client.get("/api/credentials/config/backup")
            
            # Validar resposta
            assert response.status_code == 200
            data = response.json()
            assert data["backup_count"] == 0
            assert data["backup_files"] == []


class TestCredentialStatusEndpoints:
    """Testes de integração para endpoints de status de credenciais."""
    
    @pytest.fixture
    def mock_auth_user(self):
        """Usuário autenticado mock."""
        return Mock(id="test_user_123", email="test@example.com")
    
    @pytest.mark.asyncio
    async def test_get_credentials_status_success(self, mock_auth_user):
        """Testa obtenção de status geral das credenciais."""
        with patch('backend.app.api.credentials_status.get_current_user', return_value=mock_auth_user), \
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
            
            # Fazer requisição
            response = client.get("/api/credentials/status")
            
            # Validar resposta
            assert response.status_code == 200
            data = response.json()
            assert "timestamp" in data
            assert "user_id" in data
            assert "system_health" in data
            assert "credentials_status" in data
            assert "rate_limiting" in data
            assert "audit_statistics" in data
    
    @pytest.mark.asyncio
    async def test_get_provider_status_success(self, mock_auth_user):
        """Testa obtenção de status de provedor específico."""
        with patch('backend.app.api.credentials_status.get_current_user', return_value=mock_auth_user), \
             patch('backend.app.api.credentials_status._get_provider_status') as mock_provider_status, \
             patch('backend.app.api.credentials_status.audit_service') as mock_audit:
            
            # Configurar mocks
            mock_provider_status.return_value = {
                "status": "healthy",
                "last_check": "2024-01-27T10:00:00Z",
                "rate_limit_remaining": 95
            }
            mock_audit.get_audit_events.return_value = [
                Mock(
                    timestamp="2024-01-27T10:00:00Z",
                    event_type="validation_success",
                    severity="info",
                    details={"provider": "openai"}
                )
            ]
            
            # Fazer requisição
            response = client.get("/api/credentials/status/openai")
            
            # Validar resposta
            assert response.status_code == 200
            data = response.json()
            assert data["provider"] == "openai"
            assert "timestamp" in data
            assert "user_id" in data
            assert "status" in data
            assert "recent_events" in data
            assert "health_score" in data
    
    @pytest.mark.asyncio
    async def test_get_provider_status_not_found(self, mock_auth_user):
        """Testa obtenção de status de provedor inexistente."""
        with patch('backend.app.api.credentials_status.get_current_user', return_value=mock_auth_user), \
             patch('backend.app.api.credentials_status._get_provider_status', return_value=None), \
             patch('backend.app.api.credentials_status.audit_service') as mock_audit:
            
            # Configurar mock de auditoria
            mock_audit.log_event.return_value = None
            
            # Fazer requisição
            response = client.get("/api/credentials/status/invalid_provider")
            
            # Validar resposta
            assert response.status_code == 404
            data = response.json()
            assert "não encontrado" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_get_system_health_success(self, mock_auth_user):
        """Testa obtenção de saúde do sistema."""
        with patch('backend.app.api.credentials_status.get_current_user', return_value=mock_auth_user), \
             patch('backend.app.api.credentials_status._get_system_health') as mock_system_health, \
             patch('backend.app.api.credentials_status.audit_service') as mock_audit:
            
            # Configurar mock
            mock_system_health.return_value = Mock(
                overall_health="healthy",
                encryption_status="operational",
                rate_limiting_status="normal",
                audit_status="active"
            )
            mock_audit.log_event.return_value = None
            
            # Fazer requisição
            response = client.get("/api/credentials/health")
            
            # Validar resposta
            assert response.status_code == 200
            data = response.json()
            assert "overall_health" in data
            assert "encryption_status" in data
            assert "rate_limiting_status" in data
            assert "audit_status" in data
    
    @pytest.mark.asyncio
    async def test_get_alerts_success(self, mock_auth_user):
        """Testa obtenção de alertas ativos."""
        with patch('backend.app.api.credentials_status.get_current_user', return_value=mock_auth_user), \
             patch('backend.app.api.credentials_status.audit_service') as mock_audit:
            
            # Configurar mock de auditoria
            mock_audit.get_audit_events.return_value = [
                Mock(
                    timestamp="2024-01-27T10:00:00Z",
                    event_type="validation_failed",
                    severity="error",
                    details={"provider": "openai", "reason": "Invalid API key"}
                )
            ]
            mock_audit.log_event.return_value = None
            
            # Fazer requisição
            response = client.get("/api/credentials/alerts")
            
            # Validar resposta
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            if data:  # Se há alertas
                alert = data[0]
                assert "timestamp" in alert
                assert "severity" in alert
                assert "message" in alert
                assert "provider" in alert
    
    @pytest.mark.asyncio
    async def test_get_alerts_with_severity_filter(self, mock_auth_user):
        """Testa obtenção de alertas filtrados por severidade."""
        with patch('backend.app.api.credentials_status.get_current_user', return_value=mock_auth_user), \
             patch('backend.app.api.credentials_status.audit_service') as mock_audit:
            
            # Configurar mock de auditoria
            mock_audit.get_audit_events.return_value = [
                Mock(
                    timestamp="2024-01-27T10:00:00Z",
                    event_type="validation_failed",
                    severity="error",
                    details={"provider": "openai", "reason": "Invalid API key"}
                )
            ]
            mock_audit.log_event.return_value = None
            
            # Fazer requisição com filtro
            response = client.get("/api/credentials/alerts?severity=error")
            
            # Validar resposta
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)


class TestCredentialHealthEndpoints:
    """Testes de integração para endpoints de health check."""
    
    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Testa health check bem-sucedido."""
        with patch('backend.app.api.credential_validation.get_encryption_service') as mock_encryption, \
             patch('backend.app.api.credential_validation.get_rate_limiter') as mock_rate_limiter:
            
            # Configurar mocks
            mock_encryption.return_value.is_healthy.return_value = True
            mock_rate_limiter.return_value.is_healthy.return_value = True
            
            # Fazer requisição
            response = client.get("/api/credentials/health")
            
            # Validar resposta
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "timestamp" in data
            assert "services" in data
            assert data["services"]["encryption"] == "operational"
            assert data["services"]["rate_limiting"] == "operational"
    
    @pytest.mark.asyncio
    async def test_health_check_service_unhealthy(self):
        """Testa health check com serviço não saudável."""
        with patch('backend.app.api.credential_validation.get_encryption_service') as mock_encryption, \
             patch('backend.app.api.credential_validation.get_rate_limiter') as mock_rate_limiter:
            
            # Configurar mocks
            mock_encryption.return_value.is_healthy.return_value = False
            mock_rate_limiter.return_value.is_healthy.return_value = True
            
            # Fazer requisição
            response = client.get("/api/credentials/health")
            
            # Validar resposta
            assert response.status_code == 503
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["services"]["encryption"] == "degraded"


class TestCredentialMetricsEndpoints:
    """Testes de integração para endpoints de métricas."""
    
    @pytest.fixture
    def mock_auth_token(self):
        """Token de autenticação mock."""
        return "Bearer test_token_123"
    
    @pytest.mark.asyncio
    async def test_get_credential_metrics_success(self, mock_auth_token):
        """Testa obtenção de métricas de credenciais."""
        with patch('backend.app.api.credential_validation.verify_authentication', return_value="test_user_123"), \
             patch('backend.app.api.credential_validation.get_rate_limiter') as mock_rate_limiter, \
             patch('backend.app.api.credential_validation.get_encryption_service') as mock_encryption:
            
            # Configurar mocks
            mock_rate_limiter.return_value.get_metrics.return_value = {
                "total_requests": 1000,
                "blocked_requests": 50,
                "anomaly_detections": 5,
                "active_providers": 8,
                "blocked_providers": 1
            }
            mock_encryption.return_value.get_metrics.return_value = {
                "encryption_operations": 500,
                "decryption_operations": 500,
                "errors": 0
            }
            
            # Fazer requisição
            response = client.get(
                "/api/credentials/metrics",
                headers={"Authorization": mock_auth_token}
            )
            
            # Validar resposta
            assert response.status_code == 200
            data = response.json()
            assert "total_requests" in data
            assert "blocked_requests" in data
            assert "anomaly_detections" in data
            assert "active_providers" in data
            assert "blocked_providers" in data
            assert "encryption_metrics" in data
            assert "rate_limit_metrics" in data
    
    @pytest.mark.asyncio
    async def test_reset_provider_rate_limit_success(self, mock_auth_token):
        """Testa reset de rate limit de provedor."""
        with patch('backend.app.api.credential_validation.verify_authentication', return_value="test_user_123"), \
             patch('backend.app.api.credential_validation.get_rate_limiter') as mock_rate_limiter:
            
            # Configurar mock
            mock_rate_limiter.return_value.reset_provider.return_value = True
            
            # Fazer requisição
            response = client.post(
                "/api/credentials/reset/openai",
                headers={"Authorization": mock_auth_token}
            )
            
            # Validar resposta
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Rate limit resetado com sucesso"
            assert data["provider"] == "openai"
            assert "reset_time" in data
    
    @pytest.mark.asyncio
    async def test_reset_provider_rate_limit_not_found(self, mock_auth_token):
        """Testa reset de rate limit de provedor inexistente."""
        with patch('backend.app.api.credential_validation.verify_authentication', return_value="test_user_123"), \
             patch('backend.app.api.credential_validation.get_rate_limiter') as mock_rate_limiter:
            
            # Configurar mock
            mock_rate_limiter.return_value.reset_provider.return_value = False
            
            # Fazer requisição
            response = client.post(
                "/api/credentials/reset/invalid_provider",
                headers={"Authorization": mock_auth_token}
            )
            
            # Validar resposta
            assert response.status_code == 404
            data = response.json()
            assert "não encontrado" in data["detail"]


class TestCredentialEndpointsIntegration:
    """Testes de integração completa dos endpoints de credenciais."""
    
    @pytest.fixture
    def mock_auth_token(self):
        """Token de autenticação mock."""
        return "Bearer test_token_123"
    
    @pytest.fixture
    def mock_auth_user(self):
        """Usuário autenticado mock."""
        return {"id": "test_user_123", "email": "test@example.com"}
    
    @pytest.mark.asyncio
    async def test_complete_credential_workflow(self, mock_auth_token, mock_auth_user):
        """Testa fluxo completo de credenciais: validação -> configuração -> status."""
        with patch('backend.app.api.credential_validation.verify_authentication', return_value="test_user_123"), \
             patch('backend.app.api.credential_validation._validate_credential_internal', return_value=True), \
             patch('backend.app.api.credential_validation.get_rate_limiter') as mock_rate_limiter, \
             patch('backend.app.api.credential_validation.get_encryption_service') as mock_encryption, \
             patch('backend.app.api.credentials_config.get_current_user', return_value=mock_auth_user), \
             patch('backend.app.api.credentials_config.CONFIG_FILE', tempfile.mktemp()), \
             patch('backend.app.api.credentials_config.audit_service') as mock_audit, \
             patch('backend.app.api.credentials_status.get_current_user', return_value=mock_auth_user), \
             patch('backend.app.api.credentials_status._get_provider_status') as mock_provider_status, \
             patch('backend.app.api.credentials_status._get_system_health') as mock_system_health:
            
            # Configurar mocks
            mock_rate_limiter.return_value.check_rate_limit.return_value = Mock(
                allowed=True,
                remaining=4,
                reset_time=datetime.now().timestamp() + 60
            )
            mock_encryption.return_value.encrypt_credential.return_value = "encrypted_key_123"
            mock_audit.log_config_access.return_value = None
            mock_provider_status.return_value = {"openai": {"status": "healthy"}}
            mock_system_health.return_value = Mock(
                overall_health="healthy",
                encryption_status="operational",
                rate_limiting_status="normal"
            )
            
            # 1. Validar credencial
            validation_request = {
                "provider": "openai",
                "credential_type": "api_key",
                "credential_value": "sk-proj-1234567890abcdefghijklmnopqrstuvwxyz",
                "context": "test_validation"
            }
            
            response = client.post(
                "/api/credentials/validate",
                json=validation_request,
                headers={"Authorization": mock_auth_token}
            )
            assert response.status_code == 200
            
            # 2. Obter configuração
            response = client.get("/api/credentials/config")
            assert response.status_code == 200
            
            # 3. Obter status
            response = client.get("/api/credentials/status")
            assert response.status_code == 200
            
            # 4. Obter métricas
            response = client.get(
                "/api/credentials/metrics",
                headers={"Authorization": mock_auth_token}
            )
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_error_handling_integration(self, mock_auth_token, mock_auth_user):
        """Testa tratamento de erros em cenários de integração."""
        with patch('backend.app.api.credential_validation.verify_authentication', return_value="test_user_123"), \
             patch('backend.app.api.credential_validation._validate_credential_internal', side_effect=Exception("Service unavailable")), \
             patch('backend.app.api.credential_validation.get_rate_limiter') as mock_rate_limiter, \
             patch('backend.app.api.credentials_config.get_current_user', return_value=mock_auth_user), \
             patch('backend.app.api.credentials_config.CONFIG_FILE', tempfile.mktemp()), \
             patch('backend.app.api.credentials_config.audit_service') as mock_audit:
            
            # Configurar mocks
            mock_rate_limiter.return_value.check_rate_limit.return_value = Mock(
                allowed=True,
                remaining=4,
                reset_time=datetime.now().timestamp() + 60
            )
            mock_audit.log_config_access.return_value = None
            
            # 1. Testar validação com erro
            validation_request = {
                "provider": "openai",
                "credential_type": "api_key",
                "credential_value": "invalid_key",
                "context": "test_validation"
            }
            
            response = client.post(
                "/api/credentials/validate",
                json=validation_request,
                headers={"Authorization": mock_auth_token}
            )
            assert response.status_code == 500
            
            # 2. Testar configuração com erro
            response = client.get("/api/credentials/config")
            assert response.status_code == 200  # Deve retornar configuração vazia
            
            # 3. Testar status com erro
            response = client.get("/api/credentials/status")
            assert response.status_code == 200  # Deve retornar status básico


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
        "markers", "integration: mark test as integration test"
    )


def pytest_collection_modifyitems(config, items):
    """Modifica itens de coleção para adicionar marcadores."""
    for item in items:
        if "test_credential_endpoints" in item.nodeid:
            item.add_marker(pytest.mark.integration)


@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Limpeza automática após cada teste."""
    yield
    # Limpeza específica se necessário
    pass 