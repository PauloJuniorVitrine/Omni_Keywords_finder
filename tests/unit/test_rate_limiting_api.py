"""
Testes unitários para Rate Limiting API
Sistema: Omni Keywords Finder
Módulo: APIs Auxiliares e Utilitárias
Fase: 20.11
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
import json
from datetime import datetime, timedelta

# Mock do módulo principal
mock_rate_limiting_module = Mock()
mock_rate_limiting_module.router = Mock()

class TestRateLimitingAPI:
    """Testes para API de Rate Limiting"""
    
    def setup_method(self):
        """Configuração inicial para cada teste"""
        self.mock_rate_limiter_service = Mock()
        self.mock_auth_service = Mock()
        self.mock_logger = Mock()
        
        # Mock das dependências
        with patch('app.api.rate_limiting_api.get_rate_limiter_service', return_value=self.mock_rate_limiter_service), \
             patch('app.api.rate_limiting_api.get_auth_service', return_value=self.mock_auth_service), \
             patch('app.api.rate_limiting_api.get_logger', return_value=self.mock_logger):
            
            # Importação do módulo após mock
            from app.api.rate_limiting_api import router
            self.client = TestClient(router)
    
    def test_get_rate_limit_status_success(self):
        """Teste de sucesso para status do rate limiting"""
        # Arrange
        mock_status = {
            "total_requests": 1500,
            "allowed_requests": 1200,
            "blocked_requests": 300,
            "current_rate": 25,
            "limit_rate": 100
        }
        self.mock_rate_limiter_service.obter_status.return_value = mock_status
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/rate-limiting/status", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_status
        self.mock_rate_limiter_service.obter_status.assert_called_once()
        self.mock_logger.info.assert_called()
    
    def test_get_rate_limit_status_unauthorized(self):
        """Teste de erro de autorização"""
        # Arrange
        self.mock_auth_service.validar_token.side_effect = HTTPException(status_code=401)
        
        # Act
        response = self.client.get("/rate-limiting/status", headers={"Authorization": "Bearer invalid"})
        
        # Assert
        assert response.status_code == 401
        self.mock_logger.warning.assert_called()
    
    def test_get_client_rate_limit_success(self):
        """Teste de sucesso para rate limit de cliente específico"""
        # Arrange
        client_id = "user:123"
        mock_limit = {
            "client_id": client_id,
            "current_requests": 45,
            "max_requests": 100,
            "window_seconds": 3600,
            "remaining_requests": 55,
            "reset_time": "2025-01-27T23:30:00Z"
        }
        self.mock_rate_limiter_service.obter_limite_cliente.return_value = mock_limit
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/rate-limiting/client/{client_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_limit
        self.mock_rate_limiter_service.obter_limite_cliente.assert_called_once_with(client_id)
    
    def test_get_client_rate_limit_not_found(self):
        """Teste de cliente não encontrado"""
        # Arrange
        client_id = "nonexistent:client"
        self.mock_rate_limiter_service.obter_limite_cliente.return_value = None
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/rate-limiting/client/{client_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_set_client_rate_limit_success(self):
        """Teste de sucesso para definir rate limit de cliente"""
        # Arrange
        client_id = "user:123"
        limit_data = {"max_requests": 200, "window_seconds": 3600}
        mock_result = {
            "client_id": client_id,
            "max_requests": 200,
            "window_seconds": 3600,
            "success": True
        }
        self.mock_rate_limiter_service.definir_limite_cliente.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post(f"/rate-limiting/client/{client_id}", json=limit_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 201
        assert response.json() == mock_result
        self.mock_rate_limiter_service.definir_limite_cliente.assert_called_once_with(client_id, limit_data)
    
    def test_set_client_rate_limit_validation_error(self):
        """Teste de erro de validação na definição de limite"""
        # Arrange
        client_id = "user:123"
        limit_data = {"max_requests": -1, "window_seconds": 0}  # Dados inválidos
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post(f"/rate-limiting/client/{client_id}", json=limit_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 422
        self.mock_logger.warning.assert_called()
    
    def test_delete_client_rate_limit_success(self):
        """Teste de sucesso para remoção de rate limit de cliente"""
        # Arrange
        client_id = "user:123"
        self.mock_rate_limiter_service.remover_limite_cliente.return_value = True
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.delete(f"/rate-limiting/client/{client_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 204
        self.mock_rate_limiter_service.remover_limite_cliente.assert_called_once_with(client_id)
    
    def test_delete_client_rate_limit_not_found(self):
        """Teste de remoção de limite de cliente inexistente"""
        # Arrange
        client_id = "nonexistent:client"
        self.mock_rate_limiter_service.remover_limite_cliente.return_value = False
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.delete(f"/rate-limiting/client/{client_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_get_global_rate_limit_success(self):
        """Teste de sucesso para rate limit global"""
        # Arrange
        mock_global_limit = {
            "max_requests_per_minute": 1000,
            "max_requests_per_hour": 50000,
            "max_requests_per_day": 1000000,
            "current_requests_per_minute": 150,
            "current_requests_per_hour": 2500,
            "current_requests_per_day": 45000
        }
        self.mock_rate_limiter_service.obter_limite_global.return_value = mock_global_limit
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/rate-limiting/global", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_global_limit
        self.mock_rate_limiter_service.obter_limite_global.assert_called_once()
    
    def test_set_global_rate_limit_success(self):
        """Teste de sucesso para definir rate limit global"""
        # Arrange
        global_limit_data = {
            "max_requests_per_minute": 1200,
            "max_requests_per_hour": 60000,
            "max_requests_per_day": 1200000
        }
        mock_result = {
            "success": True,
            "new_limits": global_limit_data
        }
        self.mock_rate_limiter_service.definir_limite_global.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/rate-limiting/global", json=global_limit_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 201
        assert response.json() == mock_result
        self.mock_rate_limiter_service.definir_limite_global.assert_called_once_with(global_limit_data)
    
    def test_get_blocked_clients_success(self):
        """Teste de sucesso para listar clientes bloqueados"""
        # Arrange
        mock_blocked = [
            {"client_id": "user:123", "blocked_until": "2025-01-27T23:30:00Z", "reason": "Rate limit exceeded"},
            {"client_id": "ip:192.168.1.100", "blocked_until": "2025-01-27T23:45:00Z", "reason": "Suspicious activity"}
        ]
        self.mock_rate_limiter_service.obter_clientes_bloqueados.return_value = mock_blocked
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/rate-limiting/blocked", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_blocked
        self.mock_rate_limiter_service.obter_clientes_bloqueados.assert_called_once()
    
    def test_unblock_client_success(self):
        """Teste de sucesso para desbloquear cliente"""
        # Arrange
        client_id = "user:123"
        mock_result = {"client_id": client_id, "unblocked": True, "timestamp": "2025-01-27T22:30:00Z"}
        self.mock_rate_limiter_service.desbloquear_cliente.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post(f"/rate-limiting/unblock/{client_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_result
        self.mock_rate_limiter_service.desbloquear_cliente.assert_called_once_with(client_id)
    
    def test_unblock_client_not_found(self):
        """Teste de desbloqueio de cliente não bloqueado"""
        # Arrange
        client_id = "user:123"
        self.mock_rate_limiter_service.desbloquear_cliente.return_value = None
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post(f"/rate-limiting/unblock/{client_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_get_rate_limit_metrics_success(self):
        """Teste de sucesso para métricas de rate limiting"""
        # Arrange
        mock_metrics = {
            "total_requests": 15000,
            "allowed_requests": 12000,
            "blocked_requests": 3000,
            "block_rate": 0.20,
            "avg_response_time": "15ms",
            "peak_requests_per_minute": 250,
            "unique_clients": 500
        }
        self.mock_rate_limiter_service.obter_metricas.return_value = mock_metrics
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/rate-limiting/metrics", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_metrics
        self.mock_rate_limiter_service.obter_metricas.assert_called_once()
    
    def test_get_rate_limit_history_success(self):
        """Teste de sucesso para histórico de rate limiting"""
        # Arrange
        client_id = "user:123"
        mock_history = [
            {"timestamp": "2025-01-27T22:00:00Z", "action": "request", "result": "allowed"},
            {"timestamp": "2025-01-27T22:01:00Z", "action": "request", "result": "blocked"},
            {"timestamp": "2025-01-27T22:02:00Z", "action": "unblock", "result": "success"}
        ]
        self.mock_rate_limiter_service.obter_historico.return_value = mock_history
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/rate-limiting/history/{client_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_history
        self.mock_rate_limiter_service.obter_historico.assert_called_once_with(client_id)
    
    def test_get_rate_limit_history_not_found(self):
        """Teste de histórico para cliente inexistente"""
        # Arrange
        client_id = "nonexistent:client"
        self.mock_rate_limiter_service.obter_historico.return_value = []
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/rate-limiting/history/{client_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == []
        self.mock_rate_limiter_service.obter_historico.assert_called_once_with(client_id)
    
    def test_whitelist_client_success(self):
        """Teste de sucesso para adicionar cliente à whitelist"""
        # Arrange
        client_id = "user:123"
        whitelist_data = {"reason": "VIP user", "expires_at": "2025-12-31T23:59:59Z"}
        mock_result = {"client_id": client_id, "whitelisted": True, "reason": "VIP user"}
        self.mock_rate_limiter_service.adicionar_whitelist.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post(f"/rate-limiting/whitelist/{client_id}", json=whitelist_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 201
        assert response.json() == mock_result
        self.mock_rate_limiter_service.adicionar_whitelist.assert_called_once_with(client_id, whitelist_data)
    
    def test_remove_from_whitelist_success(self):
        """Teste de sucesso para remover cliente da whitelist"""
        # Arrange
        client_id = "user:123"
        mock_result = {"client_id": client_id, "removed_from_whitelist": True}
        self.mock_rate_limiter_service.remover_whitelist.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.delete(f"/rate-limiting/whitelist/{client_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_result
        self.mock_rate_limiter_service.remover_whitelist.assert_called_once_with(client_id)
    
    def test_get_whitelist_success(self):
        """Teste de sucesso para listar clientes na whitelist"""
        # Arrange
        mock_whitelist = [
            {"client_id": "user:123", "reason": "VIP user", "added_at": "2025-01-01T00:00:00Z"},
            {"client_id": "ip:192.168.1.1", "reason": "Internal network", "added_at": "2025-01-01T00:00:00Z"}
        ]
        self.mock_rate_limiter_service.obter_whitelist.return_value = mock_whitelist
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/rate-limiting/whitelist", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_whitelist
        self.mock_rate_limiter_service.obter_whitelist.assert_called_once()
    
    def test_blacklist_client_success(self):
        """Teste de sucesso para adicionar cliente à blacklist"""
        # Arrange
        client_id = "user:123"
        blacklist_data = {"reason": "Abusive behavior", "duration_hours": 24}
        mock_result = {"client_id": client_id, "blacklisted": True, "reason": "Abusive behavior"}
        self.mock_rate_limiter_service.adicionar_blacklist.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post(f"/rate-limiting/blacklist/{client_id}", json=blacklist_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 201
        assert response.json() == mock_result
        self.mock_rate_limiter_service.adicionar_blacklist.assert_called_once_with(client_id, blacklist_data)
    
    def test_remove_from_blacklist_success(self):
        """Teste de sucesso para remover cliente da blacklist"""
        # Arrange
        client_id = "user:123"
        mock_result = {"client_id": client_id, "removed_from_blacklist": True}
        self.mock_rate_limiter_service.remover_blacklist.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.delete(f"/rate-limiting/blacklist/{client_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_result
        self.mock_rate_limiter_service.remover_blacklist.assert_called_once_with(client_id)
    
    def test_get_blacklist_success(self):
        """Teste de sucesso para listar clientes na blacklist"""
        # Arrange
        mock_blacklist = [
            {"client_id": "user:123", "reason": "Abusive behavior", "added_at": "2025-01-27T22:00:00Z"},
            {"client_id": "ip:192.168.1.100", "reason": "Suspicious activity", "added_at": "2025-01-27T21:00:00Z"}
        ]
        self.mock_rate_limiter_service.obter_blacklist.return_value = mock_blacklist
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/rate-limiting/blacklist", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_blacklist
        self.mock_rate_limiter_service.obter_blacklist.assert_called_once()
    
    def test_rate_limiting_exceeded(self):
        """Teste de rate limiting excedido"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_rate_limiter_service.obter_status.side_effect = HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Act
        response = self.client.get("/rate-limiting/status", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 429
        self.mock_logger.warning.assert_called()
    
    def test_internal_server_error(self):
        """Teste de erro interno do servidor"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_rate_limiter_service.obter_status.side_effect = Exception("Erro interno")
        
        # Act
        response = self.client.get("/rate-limiting/status", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 500
        self.mock_logger.error.assert_called()
    
    def test_missing_authorization_header(self):
        """Teste de header de autorização ausente"""
        # Act
        response = self.client.get("/rate-limiting/status")
        
        # Assert
        assert response.status_code == 401
        self.mock_logger.warning.assert_called()
    
    def test_invalid_json_payload(self):
        """Teste de payload JSON inválido"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/rate-limiting/client/user:123", data="invalid json", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 422
        self.mock_logger.warning.assert_called()
    
    def test_logging_metadata(self):
        """Teste de metadados de logging"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_rate_limiter_service.obter_status.return_value = {}
        
        # Act
        response = self.client.get("/rate-limiting/status", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        # Verifica se o logger foi chamado com metadados apropriados
        self.mock_logger.info.assert_called()
        call_args = self.mock_logger.info.call_args[0][0]
        assert "rate limiting" in call_args.lower()
    
    def test_performance_metrics(self):
        """Teste de métricas de performance"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_rate_limiter_service.obter_status.return_value = {}
        
        # Act
        start_time = datetime.now()
        response = self.client.get("/rate-limiting/status", headers={"Authorization": "Bearer token"})
        end_time = datetime.now()
        
        # Assert
        assert response.status_code == 200
        # Verifica se a resposta foi rápida (menos de 1 segundo)
        assert (end_time - start_time).total_seconds() < 1.0 