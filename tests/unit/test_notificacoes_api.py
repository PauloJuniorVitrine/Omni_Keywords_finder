"""
Testes unitários para Notificações API
Sistema: Omni Keywords Finder
Módulo: APIs Auxiliares e Utilitárias
Fase: 20.4
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
import json
from datetime import datetime, timedelta

# Mock do módulo principal
mock_notificacoes_module = Mock()
mock_notificacoes_module.router = Mock()

class TestNotificacoesAPI:
    """Testes para API de Notificações"""
    
    def setup_method(self):
        """Configuração inicial para cada teste"""
        self.mock_notificacoes_service = Mock()
        self.mock_auth_service = Mock()
        self.mock_logger = Mock()
        
        # Mock das dependências
        with patch('app.api.notificacoes_api.get_notificacoes_service', return_value=self.mock_notificacoes_service), \
             patch('app.api.notificacoes_api.get_auth_service', return_value=self.mock_auth_service), \
             patch('app.api.notificacoes_api.get_logger', return_value=self.mock_logger):
            
            # Importação do módulo após mock
            from app.api.notificacoes_api import router
            self.client = TestClient(router)
    
    def test_send_notification_success(self):
        """Teste de sucesso para envio de notificação"""
        # Arrange
        notification_data = {
            "user_id": 1,
            "type": "email",
            "subject": "Teste",
            "message": "Mensagem de teste"
        }
        sent_notification = {"id": 1, **notification_data, "status": "sent", "sent_at": "2025-01-27T10:00:00"}
        self.mock_notificacoes_service.enviar_notificacao.return_value = sent_notification
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/notificacoes/send", json=notification_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == sent_notification
        self.mock_notificacoes_service.enviar_notificacao.assert_called_once_with(notification_data)
        self.mock_logger.info.assert_called()
    
    def test_send_notification_unauthorized(self):
        """Teste de erro de autorização"""
        # Arrange
        self.mock_auth_service.validar_token.side_effect = HTTPException(status_code=401)
        
        # Act
        response = self.client.post("/notificacoes/send", json={}, headers={"Authorization": "Bearer invalid"})
        
        # Assert
        assert response.status_code == 401
        self.mock_logger.warning.assert_called()
    
    def test_send_notification_service_error(self):
        """Teste de erro do serviço"""
        # Arrange
        notification_data = {"user_id": 1, "type": "email", "message": "Teste"}
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_notificacoes_service.enviar_notificacao.side_effect = Exception("Erro interno")
        
        # Act
        response = self.client.post("/notificacoes/send", json=notification_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 500
        self.mock_logger.error.assert_called()
    
    def test_send_notification_validation_error(self):
        """Teste de erro de validação no envio"""
        # Arrange
        notification_data = {"user_id": 1}  # Dados incompletos
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/notificacoes/send", json=notification_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 422
        self.mock_logger.warning.assert_called()
    
    def test_get_notifications_success(self):
        """Teste de sucesso para listagem de notificações"""
        # Arrange
        mock_notifications = [
            {"id": 1, "user_id": 1, "type": "email", "subject": "Teste 1", "status": "sent"},
            {"id": 2, "user_id": 1, "type": "sms", "subject": "Teste 2", "status": "pending"}
        ]
        self.mock_notificacoes_service.listar_notificacoes.return_value = mock_notifications
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/notificacoes/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_notifications
        self.mock_notificacoes_service.listar_notificacoes.assert_called_once()
    
    def test_get_notification_by_id_success(self):
        """Teste de sucesso para busca de notificação por ID"""
        # Arrange
        notification_id = 1
        mock_notification = {"id": notification_id, "user_id": 1, "type": "email", "subject": "Teste", "status": "sent"}
        self.mock_notificacoes_service.buscar_notificacao_por_id.return_value = mock_notification
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/notificacoes/{notification_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_notification
        self.mock_notificacoes_service.buscar_notificacao_por_id.assert_called_once_with(notification_id)
    
    def test_get_notification_by_id_not_found(self):
        """Teste de notificação não encontrada"""
        # Arrange
        notification_id = 999
        self.mock_notificacoes_service.buscar_notificacao_por_id.return_value = None
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/notificacoes/{notification_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_update_notification_success(self):
        """Teste de sucesso para atualização de notificação"""
        # Arrange
        notification_id = 1
        notification_data = {"status": "read"}
        updated_notification = {"id": notification_id, "user_id": 1, "type": "email", "subject": "Teste", "status": "read"}
        self.mock_notificacoes_service.atualizar_notificacao.return_value = updated_notification
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.put(f"/notificacoes/{notification_id}", json=notification_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == updated_notification
        self.mock_notificacoes_service.atualizar_notificacao.assert_called_once_with(notification_id, notification_data)
    
    def test_delete_notification_success(self):
        """Teste de sucesso para exclusão de notificação"""
        # Arrange
        notification_id = 1
        self.mock_notificacoes_service.deletar_notificacao.return_value = True
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.delete(f"/notificacoes/{notification_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 204
        self.mock_notificacoes_service.deletar_notificacao.assert_called_once_with(notification_id)
    
    def test_send_bulk_notifications_success(self):
        """Teste de sucesso para envio em lote de notificações"""
        # Arrange
        notifications_data = [
            {"user_id": 1, "type": "email", "subject": "Teste 1", "message": "Mensagem 1"},
            {"user_id": 2, "type": "sms", "subject": "Teste 2", "message": "Mensagem 2"}
        ]
        mock_result = {"enviadas": 2, "erros": 0, "total": 2}
        self.mock_notificacoes_service.enviar_notificacoes_lote.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/notificacoes/bulk", json=notifications_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_result
        self.mock_notificacoes_service.enviar_notificacoes_lote.assert_called_once_with(notifications_data)
    
    def test_get_notifications_by_user_success(self):
        """Teste de sucesso para notificações por usuário"""
        # Arrange
        user_id = 1
        mock_notifications = [
            {"id": 1, "user_id": user_id, "type": "email", "subject": "Teste 1", "status": "sent"},
            {"id": 2, "user_id": user_id, "type": "sms", "subject": "Teste 2", "status": "pending"}
        ]
        self.mock_notificacoes_service.obter_notificacoes_usuario.return_value = mock_notifications
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/notificacoes/user/{user_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_notifications
        self.mock_notificacoes_service.obter_notificacoes_usuario.assert_called_once_with(user_id)
    
    def test_get_notifications_by_type_success(self):
        """Teste de sucesso para notificações por tipo"""
        # Arrange
        notification_type = "email"
        mock_notifications = [
            {"id": 1, "user_id": 1, "type": notification_type, "subject": "Teste 1", "status": "sent"}
        ]
        self.mock_notificacoes_service.obter_notificacoes_por_tipo.return_value = mock_notifications
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/notificacoes/type/{notification_type}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_notifications
        self.mock_notificacoes_service.obter_notificacoes_por_tipo.assert_called_once_with(notification_type)
    
    def test_get_notifications_stats_success(self):
        """Teste de sucesso para estatísticas de notificações"""
        # Arrange
        mock_stats = {"total": 100, "enviadas": 80, "pendentes": 15, "erros": 5}
        self.mock_notificacoes_service.obter_estatisticas.return_value = mock_stats
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/notificacoes/stats", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_stats
        self.mock_notificacoes_service.obter_estatisticas.assert_called_once()
    
    def test_mark_notification_as_read_success(self):
        """Teste de sucesso para marcar notificação como lida"""
        # Arrange
        notification_id = 1
        mock_result = {"id": notification_id, "status": "read", "read_at": "2025-01-27T10:00:00"}
        self.mock_notificacoes_service.marcar_como_lida.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.patch(f"/notificacoes/{notification_id}/read", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_result
        self.mock_notificacoes_service.marcar_como_lida.assert_called_once_with(notification_id)
    
    def test_mark_all_notifications_as_read_success(self):
        """Teste de sucesso para marcar todas as notificações como lidas"""
        # Arrange
        user_id = 1
        mock_result = {"marcadas": 5, "total": 5}
        self.mock_notificacoes_service.marcar_todas_como_lidas.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.patch(f"/notificacoes/user/{user_id}/read-all", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_result
        self.mock_notificacoes_service.marcar_todas_como_lidas.assert_called_once_with(user_id)
    
    def test_get_notification_templates_success(self):
        """Teste de sucesso para templates de notificação"""
        # Arrange
        mock_templates = [
            {"id": 1, "name": "welcome", "subject": "Bem-vindo", "body": "Olá {name}!"},
            {"id": 2, "name": "alert", "subject": "Alerta", "body": "Atenção: {message}"}
        ]
        self.mock_notificacoes_service.obter_templates.return_value = mock_templates
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/notificacoes/templates", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_templates
        self.mock_notificacoes_service.obter_templates.assert_called_once()
    
    def test_send_template_notification_success(self):
        """Teste de sucesso para envio de notificação com template"""
        # Arrange
        template_data = {
            "user_id": 1,
            "template_name": "welcome",
            "variables": {"name": "João"}
        }
        sent_notification = {"id": 1, "user_id": 1, "template": "welcome", "status": "sent"}
        self.mock_notificacoes_service.enviar_template.return_value = sent_notification
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/notificacoes/template", json=template_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == sent_notification
        self.mock_notificacoes_service.enviar_template.assert_called_once_with(template_data)
    
    def test_rate_limiting_exceeded(self):
        """Teste de rate limiting excedido"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_notificacoes_service.enviar_notificacao.side_effect = HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Act
        response = self.client.post("/notificacoes/send", json={"user_id": 1, "message": "test"}, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 429
        self.mock_logger.warning.assert_called()
    
    def test_internal_server_error(self):
        """Teste de erro interno do servidor"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_notificacoes_service.enviar_notificacao.side_effect = Exception("Erro interno")
        
        # Act
        response = self.client.post("/notificacoes/send", json={"user_id": 1, "message": "test"}, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 500
        self.mock_logger.error.assert_called()
    
    def test_missing_authorization_header(self):
        """Teste de header de autorização ausente"""
        # Act
        response = self.client.post("/notificacoes/send", json={"user_id": 1, "message": "test"})
        
        # Assert
        assert response.status_code == 401
        self.mock_logger.warning.assert_called()
    
    def test_invalid_json_payload(self):
        """Teste de payload JSON inválido"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/notificacoes/send", data="invalid json", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 422
        self.mock_logger.warning.assert_called()
    
    def test_logging_metadata(self):
        """Teste de metadados de logging"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_notificacoes_service.enviar_notificacao.return_value = {"id": 1, "status": "sent"}
        
        # Act
        response = self.client.post("/notificacoes/send", json={"user_id": 1, "message": "test"}, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        # Verifica se o logger foi chamado com metadados apropriados
        self.mock_logger.info.assert_called()
        call_args = self.mock_logger.info.call_args[0][0]
        assert "notificacao" in call_args.lower()
    
    def test_performance_metrics(self):
        """Teste de métricas de performance"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_notificacoes_service.enviar_notificacao.return_value = {"id": 1, "status": "sent"}
        
        # Act
        start_time = datetime.now()
        response = self.client.post("/notificacoes/send", json={"user_id": 1, "message": "test"}, headers={"Authorization": "Bearer token"})
        end_time = datetime.now()
        
        # Assert
        assert response.status_code == 200
        # Verifica se a resposta foi rápida (menos de 1 segundo)
        assert (end_time - start_time).total_seconds() < 1.0 