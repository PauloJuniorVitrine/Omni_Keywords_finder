"""
Testes unitários para Execuções Agendadas API
Sistema: Omni Keywords Finder
Módulo: APIs Auxiliares e Utilitárias
Fase: 20.5
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
import json
from datetime import datetime, timedelta

# Mock do módulo principal
mock_execucoes_agendadas_module = Mock()
mock_execucoes_agendadas_module.router = Mock()

class TestExecucoesAgendadasAPI:
    """Testes para API de Execuções Agendadas"""
    
    def setup_method(self):
        """Configuração inicial para cada teste"""
        self.mock_execucoes_service = Mock()
        self.mock_auth_service = Mock()
        self.mock_logger = Mock()
        
        # Mock das dependências
        with patch('app.api.execucoes_agendadas_api.get_execucoes_service', return_value=self.mock_execucoes_service), \
             patch('app.api.execucoes_agendadas_api.get_auth_service', return_value=self.mock_auth_service), \
             patch('app.api.execucoes_agendadas_api.get_logger', return_value=self.mock_logger):
            
            # Importação do módulo após mock
            from app.api.execucoes_agendadas_api import router
            self.client = TestClient(router)
    
    def test_schedule_execution_success(self):
        """Teste de sucesso para agendamento de execução"""
        # Arrange
        execution_data = {
            "user_id": 1,
            "keywords": ["teste", "palavra-chave"],
            "scheduled_time": "2025-01-28T10:00:00",
            "frequency": "daily"
        }
        scheduled_execution = {"id": 1, **execution_data, "status": "scheduled", "created_at": "2025-01-27T10:00:00"}
        self.mock_execucoes_service.agendar_execucao.return_value = scheduled_execution
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/execucoes-agendadas/schedule", json=execution_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 201
        assert response.json() == scheduled_execution
        self.mock_execucoes_service.agendar_execucao.assert_called_once_with(execution_data)
        self.mock_logger.info.assert_called()
    
    def test_schedule_execution_unauthorized(self):
        """Teste de erro de autorização"""
        # Arrange
        self.mock_auth_service.validar_token.side_effect = HTTPException(status_code=401)
        
        # Act
        response = self.client.post("/execucoes-agendadas/schedule", json={}, headers={"Authorization": "Bearer invalid"})
        
        # Assert
        assert response.status_code == 401
        self.mock_logger.warning.assert_called()
    
    def test_schedule_execution_service_error(self):
        """Teste de erro do serviço"""
        # Arrange
        execution_data = {"user_id": 1, "keywords": ["teste"], "scheduled_time": "2025-01-28T10:00:00"}
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_execucoes_service.agendar_execucao.side_effect = Exception("Erro interno")
        
        # Act
        response = self.client.post("/execucoes-agendadas/schedule", json=execution_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 500
        self.mock_logger.error.assert_called()
    
    def test_schedule_execution_validation_error(self):
        """Teste de erro de validação no agendamento"""
        # Arrange
        execution_data = {"user_id": 1}  # Dados incompletos
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/execucoes-agendadas/schedule", json=execution_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 422
        self.mock_logger.warning.assert_called()
    
    def test_get_scheduled_executions_success(self):
        """Teste de sucesso para listagem de execuções agendadas"""
        # Arrange
        mock_executions = [
            {"id": 1, "user_id": 1, "keywords": ["teste"], "scheduled_time": "2025-01-28T10:00:00", "status": "scheduled"},
            {"id": 2, "user_id": 1, "keywords": ["palavra"], "scheduled_time": "2025-01-29T10:00:00", "status": "completed"}
        ]
        self.mock_execucoes_service.listar_execucoes_agendadas.return_value = mock_executions
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/execucoes-agendadas/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_executions
        self.mock_execucoes_service.listar_execucoes_agendadas.assert_called_once()
    
    def test_get_execution_by_id_success(self):
        """Teste de sucesso para busca de execução por ID"""
        # Arrange
        execution_id = 1
        mock_execution = {"id": execution_id, "user_id": 1, "keywords": ["teste"], "scheduled_time": "2025-01-28T10:00:00", "status": "scheduled"}
        self.mock_execucoes_service.buscar_execucao_por_id.return_value = mock_execution
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/execucoes-agendadas/{execution_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_execution
        self.mock_execucoes_service.buscar_execucao_por_id.assert_called_once_with(execution_id)
    
    def test_get_execution_by_id_not_found(self):
        """Teste de execução não encontrada"""
        # Arrange
        execution_id = 999
        self.mock_execucoes_service.buscar_execucao_por_id.return_value = None
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/execucoes-agendadas/{execution_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_update_execution_success(self):
        """Teste de sucesso para atualização de execução"""
        # Arrange
        execution_id = 1
        execution_data = {"scheduled_time": "2025-01-29T10:00:00", "frequency": "weekly"}
        updated_execution = {"id": execution_id, "user_id": 1, "keywords": ["teste"], **execution_data, "status": "scheduled"}
        self.mock_execucoes_service.atualizar_execucao.return_value = updated_execution
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.put(f"/execucoes-agendadas/{execution_id}", json=execution_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == updated_execution
        self.mock_execucoes_service.atualizar_execucao.assert_called_once_with(execution_id, execution_data)
    
    def test_cancel_execution_success(self):
        """Teste de sucesso para cancelamento de execução"""
        # Arrange
        execution_id = 1
        self.mock_execucoes_service.cancelar_execucao.return_value = True
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.delete(f"/execucoes-agendadas/{execution_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 204
        self.mock_execucoes_service.cancelar_execucao.assert_called_once_with(execution_id)
    
    def test_cancel_execution_not_found(self):
        """Teste de cancelamento de execução inexistente"""
        # Arrange
        execution_id = 999
        self.mock_execucoes_service.cancelar_execucao.return_value = False
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.delete(f"/execucoes-agendadas/{execution_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_get_executions_by_user_success(self):
        """Teste de sucesso para execuções por usuário"""
        # Arrange
        user_id = 1
        mock_executions = [
            {"id": 1, "user_id": user_id, "keywords": ["teste"], "scheduled_time": "2025-01-28T10:00:00", "status": "scheduled"},
            {"id": 2, "user_id": user_id, "keywords": ["palavra"], "scheduled_time": "2025-01-29T10:00:00", "status": "completed"}
        ]
        self.mock_execucoes_service.obter_execucoes_usuario.return_value = mock_executions
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/execucoes-agendadas/user/{user_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_executions
        self.mock_execucoes_service.obter_execucoes_usuario.assert_called_once_with(user_id)
    
    def test_get_executions_by_status_success(self):
        """Teste de sucesso para execuções por status"""
        # Arrange
        status = "scheduled"
        mock_executions = [
            {"id": 1, "user_id": 1, "keywords": ["teste"], "scheduled_time": "2025-01-28T10:00:00", "status": status}
        ]
        self.mock_execucoes_service.obter_execucoes_por_status.return_value = mock_executions
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/execucoes-agendadas/status/{status}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_executions
        self.mock_execucoes_service.obter_execucoes_por_status.assert_called_once_with(status)
    
    def test_get_executions_stats_success(self):
        """Teste de sucesso para estatísticas de execuções"""
        # Arrange
        mock_stats = {"total": 50, "scheduled": 20, "running": 5, "completed": 20, "failed": 5}
        self.mock_execucoes_service.obter_estatisticas.return_value = mock_stats
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/execucoes-agendadas/stats", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_stats
        self.mock_execucoes_service.obter_estatisticas.assert_called_once()
    
    def test_pause_execution_success(self):
        """Teste de sucesso para pausar execução"""
        # Arrange
        execution_id = 1
        mock_result = {"id": execution_id, "status": "paused", "paused_at": "2025-01-27T10:00:00"}
        self.mock_execucoes_service.pausar_execucao.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.patch(f"/execucoes-agendadas/{execution_id}/pause", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_result
        self.mock_execucoes_service.pausar_execucao.assert_called_once_with(execution_id)
    
    def test_resume_execution_success(self):
        """Teste de sucesso para retomar execução"""
        # Arrange
        execution_id = 1
        mock_result = {"id": execution_id, "status": "scheduled", "resumed_at": "2025-01-27T10:00:00"}
        self.mock_execucoes_service.retomar_execucao.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.patch(f"/execucoes-agendadas/{execution_id}/resume", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_result
        self.mock_execucoes_service.retomar_execucao.assert_called_once_with(execution_id)
    
    def test_execute_now_success(self):
        """Teste de sucesso para execução imediata"""
        # Arrange
        execution_id = 1
        mock_result = {"id": execution_id, "status": "running", "started_at": "2025-01-27T10:00:00"}
        self.mock_execucoes_service.executar_agora.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post(f"/execucoes-agendadas/{execution_id}/execute", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_result
        self.mock_execucoes_service.executar_agora.assert_called_once_with(execution_id)
    
    def test_get_execution_history_success(self):
        """Teste de sucesso para histórico de execução"""
        # Arrange
        execution_id = 1
        mock_history = [
            {"id": 1, "execution_id": execution_id, "status": "started", "timestamp": "2025-01-27T10:00:00"},
            {"id": 2, "execution_id": execution_id, "status": "completed", "timestamp": "2025-01-27T10:05:00"}
        ]
        self.mock_execucoes_service.obter_historico.return_value = mock_history
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/execucoes-agendadas/{execution_id}/history", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_history
        self.mock_execucoes_service.obter_historico.assert_called_once_with(execution_id)
    
    def test_rate_limiting_exceeded(self):
        """Teste de rate limiting excedido"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_execucoes_service.agendar_execucao.side_effect = HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Act
        response = self.client.post("/execucoes-agendadas/schedule", json={"user_id": 1, "keywords": ["teste"]}, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 429
        self.mock_logger.warning.assert_called()
    
    def test_internal_server_error(self):
        """Teste de erro interno do servidor"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_execucoes_service.agendar_execucao.side_effect = Exception("Erro interno")
        
        # Act
        response = self.client.post("/execucoes-agendadas/schedule", json={"user_id": 1, "keywords": ["teste"]}, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 500
        self.mock_logger.error.assert_called()
    
    def test_missing_authorization_header(self):
        """Teste de header de autorização ausente"""
        # Act
        response = self.client.post("/execucoes-agendadas/schedule", json={"user_id": 1, "keywords": ["teste"]})
        
        # Assert
        assert response.status_code == 401
        self.mock_logger.warning.assert_called()
    
    def test_invalid_json_payload(self):
        """Teste de payload JSON inválido"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/execucoes-agendadas/schedule", data="invalid json", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 422
        self.mock_logger.warning.assert_called()
    
    def test_logging_metadata(self):
        """Teste de metadados de logging"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_execucoes_service.agendar_execucao.return_value = {"id": 1, "status": "scheduled"}
        
        # Act
        response = self.client.post("/execucoes-agendadas/schedule", json={"user_id": 1, "keywords": ["teste"]}, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 201
        # Verifica se o logger foi chamado com metadados apropriados
        self.mock_logger.info.assert_called()
        call_args = self.mock_logger.info.call_args[0][0]
        assert "execucao" in call_args.lower()
    
    def test_performance_metrics(self):
        """Teste de métricas de performance"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_execucoes_service.agendar_execucao.return_value = {"id": 1, "status": "scheduled"}
        
        # Act
        start_time = datetime.now()
        response = self.client.post("/execucoes-agendadas/schedule", json={"user_id": 1, "keywords": ["teste"]}, headers={"Authorization": "Bearer token"})
        end_time = datetime.now()
        
        # Assert
        assert response.status_code == 201
        # Verifica se a resposta foi rápida (menos de 1 segundo)
        assert (end_time - start_time).total_seconds() < 1.0 