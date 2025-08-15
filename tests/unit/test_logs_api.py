"""
Testes unitários para Logs API
Sistema: Omni Keywords Finder
Módulo: APIs Auxiliares e Utilitárias
Fase: 20.3
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
import json
from datetime import datetime, timedelta

# Mock do módulo principal
mock_logs_module = Mock()
mock_logs_module.router = Mock()

class TestLogsAPI:
    """Testes para API de Logs"""
    
    def setup_method(self):
        """Configuração inicial para cada teste"""
        self.mock_logs_service = Mock()
        self.mock_auth_service = Mock()
        self.mock_logger = Mock()
        
        # Mock das dependências
        with patch('app.api.logs_api.get_logs_service', return_value=self.mock_logs_service), \
             patch('app.api.logs_api.get_auth_service', return_value=self.mock_auth_service), \
             patch('app.api.logs_api.get_logger', return_value=self.mock_logger):
            
            # Importação do módulo após mock
            from app.api.logs_api import router
            self.client = TestClient(router)
    
    def test_get_logs_success(self):
        """Teste de sucesso para consulta de logs"""
        # Arrange
        mock_logs = [
            {"id": 1, "level": "INFO", "message": "Log de teste", "timestamp": "2025-01-27T10:00:00"},
            {"id": 2, "level": "ERROR", "message": "Erro de teste", "timestamp": "2025-01-27T10:01:00"}
        ]
        self.mock_logs_service.consultar_logs.return_value = mock_logs
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/logs/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_logs
        self.mock_logs_service.consultar_logs.assert_called_once()
        self.mock_logger.info.assert_called()
    
    def test_get_logs_unauthorized(self):
        """Teste de erro de autorização"""
        # Arrange
        self.mock_auth_service.validar_token.side_effect = HTTPException(status_code=401)
        
        # Act
        response = self.client.get("/logs/", headers={"Authorization": "Bearer invalid"})
        
        # Assert
        assert response.status_code == 401
        self.mock_logger.warning.assert_called()
    
    def test_get_logs_service_error(self):
        """Teste de erro do serviço"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_logs_service.consultar_logs.side_effect = Exception("Erro interno")
        
        # Act
        response = self.client.get("/logs/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 500
        self.mock_logger.error.assert_called()
    
    def test_get_logs_with_filters_success(self):
        """Teste de sucesso para consulta de logs com filtros"""
        # Arrange
        filters = {"level": "ERROR", "start_date": "2025-01-27", "end_date": "2025-01-28"}
        mock_logs = [{"id": 2, "level": "ERROR", "message": "Erro de teste", "timestamp": "2025-01-27T10:01:00"}]
        self.mock_logs_service.consultar_logs.return_value = mock_logs
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/logs/", params=filters, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_logs
        self.mock_logs_service.consultar_logs.assert_called_once_with(**filters)
    
    def test_get_log_by_id_success(self):
        """Teste de sucesso para busca de log por ID"""
        # Arrange
        log_id = 1
        mock_log = {"id": log_id, "level": "INFO", "message": "Log de teste", "timestamp": "2025-01-27T10:00:00"}
        self.mock_logs_service.buscar_log_por_id.return_value = mock_log
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/logs/{log_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_log
        self.mock_logs_service.buscar_log_por_id.assert_called_once_with(log_id)
    
    def test_get_log_by_id_not_found(self):
        """Teste de log não encontrado"""
        # Arrange
        log_id = 999
        self.mock_logs_service.buscar_log_por_id.return_value = None
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/logs/{log_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_create_log_success(self):
        """Teste de sucesso para criação de log"""
        # Arrange
        log_data = {"level": "INFO", "message": "Novo log", "module": "test"}
        created_log = {"id": 3, **log_data, "timestamp": "2025-01-27T10:00:00"}
        self.mock_logs_service.criar_log.return_value = created_log
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/logs/", json=log_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 201
        assert response.json() == created_log
        self.mock_logs_service.criar_log.assert_called_once_with(log_data)
    
    def test_create_log_validation_error(self):
        """Teste de erro de validação na criação"""
        # Arrange
        log_data = {"level": "INVALID", "message": ""}  # Level inválido e mensagem vazia
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/logs/", json=log_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 422
        self.mock_logger.warning.assert_called()
    
    def test_delete_log_success(self):
        """Teste de sucesso para exclusão de log"""
        # Arrange
        log_id = 1
        self.mock_logs_service.deletar_log.return_value = True
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.delete(f"/logs/{log_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 204
        self.mock_logs_service.deletar_log.assert_called_once_with(log_id)
    
    def test_delete_log_not_found(self):
        """Teste de exclusão de log inexistente"""
        # Arrange
        log_id = 999
        self.mock_logs_service.deletar_log.return_value = False
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.delete(f"/logs/{log_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_search_logs_success(self):
        """Teste de sucesso para busca de logs"""
        # Arrange
        query = "erro"
        mock_results = [{"id": 2, "level": "ERROR", "message": "Erro de teste", "timestamp": "2025-01-27T10:01:00"}]
        self.mock_logs_service.buscar_logs.return_value = mock_results
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/logs/search?q={query}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_results
        self.mock_logs_service.buscar_logs.assert_called_once_with(query)
    
    def test_get_logs_stats_success(self):
        """Teste de sucesso para estatísticas de logs"""
        # Arrange
        mock_stats = {"total": 1000, "info": 800, "warning": 150, "error": 50}
        self.mock_logs_service.obter_estatisticas.return_value = mock_stats
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/logs/stats", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_stats
        self.mock_logs_service.obter_estatisticas.assert_called_once()
    
    def test_export_logs_success(self):
        """Teste de sucesso para exportação de logs"""
        # Arrange
        format_type = "csv"
        mock_export_data = "id,level,message,timestamp\n1,INFO,Log de teste,2025-01-27T10:00:00"
        self.mock_logs_service.exportar_logs.return_value = mock_export_data
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/logs/export?format={format_type}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.content == mock_export_data.encode()
        self.mock_logs_service.exportar_logs.assert_called_once_with(format_type)
    
    def test_clear_logs_success(self):
        """Teste de sucesso para limpeza de logs"""
        # Arrange
        mock_result = {"deleted": 100, "remaining": 50}
        self.mock_logs_service.limpar_logs.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/logs/clear", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_result
        self.mock_logs_service.limpar_logs.assert_called_once()
    
    def test_get_logs_by_module_success(self):
        """Teste de sucesso para logs por módulo"""
        # Arrange
        module = "api"
        mock_logs = [{"id": 1, "level": "INFO", "message": "API log", "module": module}]
        self.mock_logs_service.obter_logs_por_modulo.return_value = mock_logs
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/logs/module/{module}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_logs
        self.mock_logs_service.obter_logs_por_modulo.assert_called_once_with(module)
    
    def test_get_logs_by_level_success(self):
        """Teste de sucesso para logs por nível"""
        # Arrange
        level = "ERROR"
        mock_logs = [{"id": 2, "level": level, "message": "Erro de teste"}]
        self.mock_logs_service.obter_logs_por_nivel.return_value = mock_logs
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/logs/level/{level}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_logs
        self.mock_logs_service.obter_logs_por_nivel.assert_called_once_with(level)
    
    def test_get_logs_timeline_success(self):
        """Teste de sucesso para timeline de logs"""
        # Arrange
        start_date = "2025-01-27"
        end_date = "2025-01-28"
        mock_timeline = [
            {"date": "2025-01-27", "count": 50},
            {"date": "2025-01-28", "count": 30}
        ]
        self.mock_logs_service.obter_timeline.return_value = mock_timeline
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/logs/timeline?start_date={start_date}&end_date={end_date}", 
                                 headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_timeline
        self.mock_logs_service.obter_timeline.assert_called_once_with(start_date, end_date)
    
    def test_get_logs_alerts_success(self):
        """Teste de sucesso para alertas de logs"""
        # Arrange
        mock_alerts = [
            {"id": 1, "type": "error_spike", "message": "Pico de erros detectado", "severity": "high"}
        ]
        self.mock_logs_service.obter_alertas.return_value = mock_alerts
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/logs/alerts", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_alerts
        self.mock_logs_service.obter_alertas.assert_called_once()
    
    def test_rate_limiting_exceeded(self):
        """Teste de rate limiting excedido"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_logs_service.consultar_logs.side_effect = HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Act
        response = self.client.get("/logs/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 429
        self.mock_logger.warning.assert_called()
    
    def test_internal_server_error(self):
        """Teste de erro interno do servidor"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_logs_service.consultar_logs.side_effect = Exception("Erro interno")
        
        # Act
        response = self.client.get("/logs/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 500
        self.mock_logger.error.assert_called()
    
    def test_missing_authorization_header(self):
        """Teste de header de autorização ausente"""
        # Act
        response = self.client.get("/logs/")
        
        # Assert
        assert response.status_code == 401
        self.mock_logger.warning.assert_called()
    
    def test_invalid_json_payload(self):
        """Teste de payload JSON inválido"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/logs/", data="invalid json", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 422
        self.mock_logger.warning.assert_called()
    
    def test_logging_metadata(self):
        """Teste de metadados de logging"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_logs_service.consultar_logs.return_value = []
        
        # Act
        response = self.client.get("/logs/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        # Verifica se o logger foi chamado com metadados apropriados
        self.mock_logger.info.assert_called()
        call_args = self.mock_logger.info.call_args[0][0]
        assert "logs" in call_args.lower()
    
    def test_performance_metrics(self):
        """Teste de métricas de performance"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_logs_service.consultar_logs.return_value = []
        
        # Act
        start_time = datetime.now()
        response = self.client.get("/logs/", headers={"Authorization": "Bearer token"})
        end_time = datetime.now()
        
        # Assert
        assert response.status_code == 200
        # Verifica se a resposta foi rápida (menos de 1 segundo)
        assert (end_time - start_time).total_seconds() < 1.0 