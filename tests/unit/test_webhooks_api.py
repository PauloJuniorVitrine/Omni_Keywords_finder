"""
Testes unitários para Webhooks API
Sistema: Omni Keywords Finder
Módulo: APIs Auxiliares e Utilitárias
Fase: 20.12
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
import json
from datetime import datetime, timedelta

# Mock do módulo principal
mock_webhooks_module = Mock()
mock_webhooks_module.router = Mock()

class TestWebhooksAPI:
    """Testes para API de Webhooks"""
    
    def setup_method(self):
        """Configuração inicial para cada teste"""
        self.mock_webhook_service = Mock()
        self.mock_auth_service = Mock()
        self.mock_logger = Mock()
        
        # Mock das dependências
        with patch('app.api.webhooks_api.get_webhook_service', return_value=self.mock_webhook_service), \
             patch('app.api.webhooks_api.get_auth_service', return_value=self.mock_auth_service), \
             patch('app.api.webhooks_api.get_logger', return_value=self.mock_logger):
            
            # Importação do módulo após mock
            from app.api.webhooks_api import router
            self.client = TestClient(router)
    
    def test_get_webhooks_success(self):
        """Teste de sucesso para listagem de webhooks"""
        # Arrange
        mock_webhooks = [
            {"id": 1, "url": "https://api.example.com/webhook1", "events": ["keyword.found"], "status": "active"},
            {"id": 2, "url": "https://api.example.com/webhook2", "events": ["analysis.complete"], "status": "active"},
            {"id": 3, "url": "https://api.example.com/webhook3", "events": ["error.occurred"], "status": "inactive"}
        ]
        self.mock_webhook_service.listar_webhooks.return_value = mock_webhooks
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/webhooks/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_webhooks
        self.mock_webhook_service.listar_webhooks.assert_called_once()
        self.mock_logger.info.assert_called()
    
    def test_get_webhooks_unauthorized(self):
        """Teste de erro de autorização"""
        # Arrange
        self.mock_auth_service.validar_token.side_effect = HTTPException(status_code=401)
        
        # Act
        response = self.client.get("/webhooks/", headers={"Authorization": "Bearer invalid"})
        
        # Assert
        assert response.status_code == 401
        self.mock_logger.warning.assert_called()
    
    def test_get_webhook_by_id_success(self):
        """Teste de sucesso para busca de webhook por ID"""
        # Arrange
        webhook_id = 1
        mock_webhook = {
            "id": webhook_id,
            "url": "https://api.example.com/webhook1",
            "events": ["keyword.found", "analysis.complete"],
            "status": "active",
            "created_at": "2025-01-27T22:00:00Z",
            "last_triggered": "2025-01-27T22:30:00Z"
        }
        self.mock_webhook_service.buscar_webhook_por_id.return_value = mock_webhook
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/webhooks/{webhook_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_webhook
        self.mock_webhook_service.buscar_webhook_por_id.assert_called_once_with(webhook_id)
    
    def test_get_webhook_by_id_not_found(self):
        """Teste de webhook não encontrado"""
        # Arrange
        webhook_id = 999
        self.mock_webhook_service.buscar_webhook_por_id.return_value = None
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/webhooks/{webhook_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_create_webhook_success(self):
        """Teste de sucesso para criação de webhook"""
        # Arrange
        webhook_data = {
            "url": "https://api.example.com/new-webhook",
            "events": ["keyword.found", "analysis.complete"],
            "secret": "webhook_secret_123"
        }
        created_webhook = {
            "id": 4,
            "url": "https://api.example.com/new-webhook",
            "events": ["keyword.found", "analysis.complete"],
            "status": "active",
            "created_at": "2025-01-27T22:30:00Z"
        }
        self.mock_webhook_service.criar_webhook.return_value = created_webhook
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/webhooks/", json=webhook_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 201
        assert response.json() == created_webhook
        self.mock_webhook_service.criar_webhook.assert_called_once_with(webhook_data)
    
    def test_create_webhook_validation_error(self):
        """Teste de erro de validação na criação"""
        # Arrange
        webhook_data = {"url": "invalid-url", "events": []}  # Dados inválidos
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/webhooks/", json=webhook_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 422
        self.mock_logger.warning.assert_called()
    
    def test_update_webhook_success(self):
        """Teste de sucesso para atualização de webhook"""
        # Arrange
        webhook_id = 1
        webhook_data = {"events": ["keyword.found", "analysis.complete", "error.occurred"], "status": "inactive"}
        updated_webhook = {
            "id": webhook_id,
            "url": "https://api.example.com/webhook1",
            "events": ["keyword.found", "analysis.complete", "error.occurred"],
            "status": "inactive",
            "updated_at": "2025-01-27T22:30:00Z"
        }
        self.mock_webhook_service.atualizar_webhook.return_value = updated_webhook
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.put(f"/webhooks/{webhook_id}", json=webhook_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == updated_webhook
        self.mock_webhook_service.atualizar_webhook.assert_called_once_with(webhook_id, webhook_data)
    
    def test_update_webhook_not_found(self):
        """Teste de atualização de webhook inexistente"""
        # Arrange
        webhook_id = 999
        webhook_data = {"status": "inactive"}
        self.mock_webhook_service.atualizar_webhook.return_value = None
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.put(f"/webhooks/{webhook_id}", json=webhook_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_delete_webhook_success(self):
        """Teste de sucesso para exclusão de webhook"""
        # Arrange
        webhook_id = 1
        self.mock_webhook_service.deletar_webhook.return_value = True
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.delete(f"/webhooks/{webhook_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 204
        self.mock_webhook_service.deletar_webhook.assert_called_once_with(webhook_id)
    
    def test_delete_webhook_not_found(self):
        """Teste de exclusão de webhook inexistente"""
        # Arrange
        webhook_id = 999
        self.mock_webhook_service.deletar_webhook.return_value = False
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.delete(f"/webhooks/{webhook_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_test_webhook_success(self):
        """Teste de sucesso para teste de webhook"""
        # Arrange
        webhook_id = 1
        test_data = {"message": "Test webhook", "timestamp": "2025-01-27T22:30:00Z"}
        mock_result = {
            "webhook_id": webhook_id,
            "test_sent": True,
            "response_status": 200,
            "response_time": "150ms",
            "timestamp": "2025-01-27T22:30:00Z"
        }
        self.mock_webhook_service.testar_webhook.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post(f"/webhooks/{webhook_id}/test", json=test_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_result
        self.mock_webhook_service.testar_webhook.assert_called_once_with(webhook_id, test_data)
    
    def test_test_webhook_not_found(self):
        """Teste de teste de webhook inexistente"""
        # Arrange
        webhook_id = 999
        test_data = {"message": "Test"}
        self.mock_webhook_service.testar_webhook.return_value = None
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post(f"/webhooks/{webhook_id}/test", json=test_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_get_webhook_events_success(self):
        """Teste de sucesso para listagem de eventos de webhook"""
        # Arrange
        webhook_id = 1
        mock_events = [
            {"id": 1, "event_type": "keyword.found", "payload": {"keyword": "test"}, "sent_at": "2025-01-27T22:00:00Z", "status": "success"},
            {"id": 2, "event_type": "analysis.complete", "payload": {"analysis_id": 123}, "sent_at": "2025-01-27T22:15:00Z", "status": "success"},
            {"id": 3, "event_type": "error.occurred", "payload": {"error": "timeout"}, "sent_at": "2025-01-27T22:30:00Z", "status": "failed"}
        ]
        self.mock_webhook_service.obter_eventos.return_value = mock_events
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/webhooks/{webhook_id}/events", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_events
        self.mock_webhook_service.obter_eventos.assert_called_once_with(webhook_id)
    
    def test_get_webhook_events_not_found(self):
        """Teste de eventos para webhook inexistente"""
        # Arrange
        webhook_id = 999
        self.mock_webhook_service.obter_eventos.return_value = []
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/webhooks/{webhook_id}/events", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == []
        self.mock_webhook_service.obter_eventos.assert_called_once_with(webhook_id)
    
    def test_retry_webhook_event_success(self):
        """Teste de sucesso para retry de evento de webhook"""
        # Arrange
        webhook_id = 1
        event_id = 3
        mock_result = {
            "webhook_id": webhook_id,
            "event_id": event_id,
            "retry_sent": True,
            "response_status": 200,
            "response_time": "120ms",
            "timestamp": "2025-01-27T22:35:00Z"
        }
        self.mock_webhook_service.reenviar_evento.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post(f"/webhooks/{webhook_id}/events/{event_id}/retry", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_result
        self.mock_webhook_service.reenviar_evento.assert_called_once_with(webhook_id, event_id)
    
    def test_retry_webhook_event_not_found(self):
        """Teste de retry de evento inexistente"""
        # Arrange
        webhook_id = 1
        event_id = 999
        self.mock_webhook_service.reenviar_evento.return_value = None
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post(f"/webhooks/{webhook_id}/events/{event_id}/retry", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_get_webhook_stats_success(self):
        """Teste de sucesso para estatísticas de webhook"""
        # Arrange
        webhook_id = 1
        mock_stats = {
            "webhook_id": webhook_id,
            "total_events": 150,
            "successful_events": 140,
            "failed_events": 10,
            "success_rate": 0.93,
            "avg_response_time": "180ms",
            "last_triggered": "2025-01-27T22:30:00Z"
        }
        self.mock_webhook_service.obter_estatisticas.return_value = mock_stats
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/webhooks/{webhook_id}/stats", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_stats
        self.mock_webhook_service.obter_estatisticas.assert_called_once_with(webhook_id)
    
    def test_get_webhook_stats_not_found(self):
        """Teste de estatísticas para webhook inexistente"""
        # Arrange
        webhook_id = 999
        self.mock_webhook_service.obter_estatisticas.return_value = None
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/webhooks/{webhook_id}/stats", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_get_available_events_success(self):
        """Teste de sucesso para listagem de eventos disponíveis"""
        # Arrange
        mock_events = [
            {"name": "keyword.found", "description": "Triggered when a keyword is found", "payload_schema": {"keyword": "string", "url": "string"}},
            {"name": "analysis.complete", "description": "Triggered when analysis is completed", "payload_schema": {"analysis_id": "integer", "results": "object"}},
            {"name": "error.occurred", "description": "Triggered when an error occurs", "payload_schema": {"error": "string", "details": "object"}}
        ]
        self.mock_webhook_service.obter_eventos_disponiveis.return_value = mock_events
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/webhooks/events", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_events
        self.mock_webhook_service.obter_eventos_disponiveis.assert_called_once()
    
    def test_validate_webhook_url_success(self):
        """Teste de sucesso para validação de URL de webhook"""
        # Arrange
        url_data = {"url": "https://api.example.com/webhook"}
        mock_validation = {
            "url": "https://api.example.com/webhook",
            "valid": True,
            "response_time": "120ms",
            "status_code": 200
        }
        self.mock_webhook_service.validar_url.return_value = mock_validation
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/webhooks/validate-url", json=url_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_validation
        self.mock_webhook_service.validar_url.assert_called_once_with(url_data["url"])
    
    def test_validate_webhook_url_invalid(self):
        """Teste de validação de URL inválida"""
        # Arrange
        url_data = {"url": "invalid-url"}
        mock_validation = {
            "url": "invalid-url",
            "valid": False,
            "error": "Invalid URL format"
        }
        self.mock_webhook_service.validar_url.return_value = mock_validation
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/webhooks/validate-url", json=url_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_validation
        self.mock_webhook_service.validar_url.assert_called_once_with(url_data["url"])
    
    def test_rate_limiting_exceeded(self):
        """Teste de rate limiting excedido"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_webhook_service.listar_webhooks.side_effect = HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Act
        response = self.client.get("/webhooks/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 429
        self.mock_logger.warning.assert_called()
    
    def test_internal_server_error(self):
        """Teste de erro interno do servidor"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_webhook_service.listar_webhooks.side_effect = Exception("Erro interno")
        
        # Act
        response = self.client.get("/webhooks/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 500
        self.mock_logger.error.assert_called()
    
    def test_missing_authorization_header(self):
        """Teste de header de autorização ausente"""
        # Act
        response = self.client.get("/webhooks/")
        
        # Assert
        assert response.status_code == 401
        self.mock_logger.warning.assert_called()
    
    def test_invalid_json_payload(self):
        """Teste de payload JSON inválido"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/webhooks/", data="invalid json", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 422
        self.mock_logger.warning.assert_called()
    
    def test_logging_metadata(self):
        """Teste de metadados de logging"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_webhook_service.listar_webhooks.return_value = []
        
        # Act
        response = self.client.get("/webhooks/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        # Verifica se o logger foi chamado com metadados apropriados
        self.mock_logger.info.assert_called()
        call_args = self.mock_logger.info.call_args[0][0]
        assert "webhooks" in call_args.lower()
    
    def test_performance_metrics(self):
        """Teste de métricas de performance"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_webhook_service.listar_webhooks.return_value = []
        
        # Act
        start_time = datetime.now()
        response = self.client.get("/webhooks/", headers={"Authorization": "Bearer token"})
        end_time = datetime.now()
        
        # Assert
        assert response.status_code == 200
        # Verifica se a resposta foi rápida (menos de 1 segundo)
        assert (end_time - start_time).total_seconds() < 1.0 