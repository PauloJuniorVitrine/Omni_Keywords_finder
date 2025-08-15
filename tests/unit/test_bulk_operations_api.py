"""
Testes unitários para Bulk Operations API
Sistema: Omni Keywords Finder
Módulo: APIs Auxiliares e Utilitárias
Fase: 20.8
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
import json
from datetime import datetime, timedelta

# Mock do módulo principal
mock_bulk_operations_module = Mock()
mock_bulk_operations_module.router = Mock()

class TestBulkOperationsAPI:
    """Testes para API de Operações em Lote"""
    
    def setup_method(self):
        """Configuração inicial para cada teste"""
        self.mock_bulk_service = Mock()
        self.mock_auth_service = Mock()
        self.mock_logger = Mock()
        
        # Mock das dependências
        with patch('app.api.bulk_operations_api.get_bulk_service', return_value=self.mock_bulk_service), \
             patch('app.api.bulk_operations_api.get_auth_service', return_value=self.mock_auth_service), \
             patch('app.api.bulk_operations_api.get_logger', return_value=self.mock_logger):
            
            # Importação do módulo após mock
            from app.api.bulk_operations_api import router
            self.client = TestClient(router)
    
    def test_bulk_keywords_import_success(self):
        """Teste de sucesso para importação em lote de keywords"""
        # Arrange
        bulk_data = {
            "keywords": ["keyword1", "keyword2", "keyword3"],
            "cluster_id": 1,
            "options": {"validate": True, "skip_duplicates": True}
        }
        mock_result = {"imported": 3, "skipped": 0, "errors": 0, "total": 3}
        self.mock_bulk_service.importar_keywords_lote.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/bulk/keywords/import", json=bulk_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_result
        self.mock_bulk_service.importar_keywords_lote.assert_called_once_with(bulk_data)
        self.mock_logger.info.assert_called()
    
    def test_bulk_keywords_import_unauthorized(self):
        """Teste de erro de autorização"""
        # Arrange
        self.mock_auth_service.validar_token.side_effect = HTTPException(status_code=401)
        
        # Act
        response = self.client.post("/bulk/keywords/import", json={}, headers={"Authorization": "Bearer invalid"})
        
        # Assert
        assert response.status_code == 401
        self.mock_logger.warning.assert_called()
    
    def test_bulk_keywords_import_service_error(self):
        """Teste de erro do serviço"""
        # Arrange
        bulk_data = {"keywords": ["keyword1", "keyword2"]}
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_bulk_service.importar_keywords_lote.side_effect = Exception("Erro interno")
        
        # Act
        response = self.client.post("/bulk/keywords/import", json=bulk_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 500
        self.mock_logger.error.assert_called()
    
    def test_bulk_keywords_import_validation_error(self):
        """Teste de erro de validação na importação"""
        # Arrange
        bulk_data = {"keywords": []}  # Lista vazia
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/bulk/keywords/import", json=bulk_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 422
        self.mock_logger.warning.assert_called()
    
    def test_bulk_keywords_export_success(self):
        """Teste de sucesso para exportação em lote de keywords"""
        # Arrange
        export_data = {
            "cluster_ids": [1, 2, 3],
            "format": "csv",
            "filters": {"status": "active"}
        }
        mock_export_data = "keyword,volume,difficulty\nkeyword1,1000,medium\nkeyword2,800,easy"
        self.mock_bulk_service.exportar_keywords_lote.return_value = mock_export_data
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/bulk/keywords/export", json=export_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.content == mock_export_data.encode()
        self.mock_bulk_service.exportar_keywords_lote.assert_called_once_with(export_data)
    
    def test_bulk_keywords_update_success(self):
        """Teste de sucesso para atualização em lote de keywords"""
        # Arrange
        update_data = {
            "keyword_ids": [1, 2, 3],
            "updates": {"status": "inactive", "priority": "low"}
        }
        mock_result = {"updated": 3, "errors": 0, "total": 3}
        self.mock_bulk_service.atualizar_keywords_lote.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.put("/bulk/keywords/update", json=update_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_result
        self.mock_bulk_service.atualizar_keywords_lote.assert_called_once_with(update_data)
    
    def test_bulk_keywords_delete_success(self):
        """Teste de sucesso para exclusão em lote de keywords"""
        # Arrange
        delete_data = {"keyword_ids": [1, 2, 3]}
        mock_result = {"deleted": 3, "errors": 0, "total": 3}
        self.mock_bulk_service.deletar_keywords_lote.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.delete("/bulk/keywords/delete", json=delete_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_result
        self.mock_bulk_service.deletar_keywords_lote.assert_called_once_with(delete_data)
    
    def test_bulk_clusters_operations_success(self):
        """Teste de sucesso para operações em lote de clusters"""
        # Arrange
        operations_data = {
            "operations": [
                {"action": "create", "data": {"name": "Cluster 1"}},
                {"action": "update", "id": 1, "data": {"name": "Cluster Atualizado"}},
                {"action": "delete", "id": 2}
            ]
        }
        mock_result = {"success": 3, "errors": 0, "total": 3}
        self.mock_bulk_service.operacoes_clusters_lote.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/bulk/clusters/operations", json=operations_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_result
        self.mock_bulk_service.operacoes_clusters_lote.assert_called_once_with(operations_data)
    
    def test_bulk_analytics_success(self):
        """Teste de sucesso para analytics em lote"""
        # Arrange
        analytics_data = {
            "keyword_ids": [1, 2, 3, 4, 5],
            "metrics": ["volume", "difficulty", "cpc"]
        }
        mock_analytics = [
            {"keyword_id": 1, "volume": 1000, "difficulty": "medium", "cpc": 2.50},
            {"keyword_id": 2, "volume": 800, "difficulty": "easy", "cpc": 1.80}
        ]
        self.mock_bulk_service.analytics_lote.return_value = mock_analytics
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/bulk/analytics", json=analytics_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_analytics
        self.mock_bulk_service.analytics_lote.assert_called_once_with(analytics_data)
    
    def test_bulk_validation_success(self):
        """Teste de sucesso para validação em lote"""
        # Arrange
        validation_data = {
            "keywords": ["keyword1", "keyword2", "invalid_keyword_123"],
            "rules": ["length", "characters", "format"]
        }
        mock_validation = {
            "valid": ["keyword1", "keyword2"],
            "invalid": ["invalid_keyword_123"],
            "errors": {"invalid_keyword_123": "Formato inválido"}
        }
        self.mock_bulk_service.validar_lote.return_value = mock_validation
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/bulk/validation", json=validation_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_validation
        self.mock_bulk_service.validar_lote.assert_called_once_with(validation_data)
    
    def test_bulk_processing_status_success(self):
        """Teste de sucesso para status de processamento em lote"""
        # Arrange
        job_id = "bulk_job_123"
        mock_status = {
            "job_id": job_id,
            "status": "processing",
            "progress": 75,
            "total": 100,
            "completed": 75,
            "errors": 2
        }
        self.mock_bulk_service.obter_status_processamento.return_value = mock_status
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/bulk/status/{job_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_status
        self.mock_bulk_service.obter_status_processamento.assert_called_once_with(job_id)
    
    def test_bulk_processing_cancel_success(self):
        """Teste de sucesso para cancelamento de processamento em lote"""
        # Arrange
        job_id = "bulk_job_123"
        mock_result = {"job_id": job_id, "status": "cancelled", "cancelled_at": "2025-01-27T10:00:00"}
        self.mock_bulk_service.cancelar_processamento.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post(f"/bulk/cancel/{job_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_result
        self.mock_bulk_service.cancelar_processamento.assert_called_once_with(job_id)
    
    def test_bulk_processing_history_success(self):
        """Teste de sucesso para histórico de processamentos em lote"""
        # Arrange
        mock_history = [
            {"job_id": "bulk_job_1", "type": "import", "status": "completed", "created_at": "2025-01-27T09:00:00"},
            {"job_id": "bulk_job_2", "type": "export", "status": "processing", "created_at": "2025-01-27T10:00:00"}
        ]
        self.mock_bulk_service.obter_historico_processamentos.return_value = mock_history
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/bulk/history", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_history
        self.mock_bulk_service.obter_historico_processamentos.assert_called_once()
    
    def test_bulk_processing_retry_success(self):
        """Teste de sucesso para retry de processamento em lote"""
        # Arrange
        job_id = "bulk_job_123"
        mock_result = {"job_id": f"{job_id}_retry", "status": "queued", "retry_count": 1}
        self.mock_bulk_service.repetir_processamento.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post(f"/bulk/retry/{job_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_result
        self.mock_bulk_service.repetir_processamento.assert_called_once_with(job_id)
    
    def test_bulk_processing_cleanup_success(self):
        """Teste de sucesso para limpeza de processamentos em lote"""
        # Arrange
        cleanup_data = {"older_than_days": 30, "status": ["completed", "failed"]}
        mock_result = {"cleaned": 50, "remaining": 10}
        self.mock_bulk_service.limpar_processamentos.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/bulk/cleanup", json=cleanup_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_result
        self.mock_bulk_service.limpar_processamentos.assert_called_once_with(cleanup_data)
    
    def test_rate_limiting_exceeded(self):
        """Teste de rate limiting excedido"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_bulk_service.importar_keywords_lote.side_effect = HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Act
        response = self.client.post("/bulk/keywords/import", json={"keywords": ["test"]}, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 429
        self.mock_logger.warning.assert_called()
    
    def test_internal_server_error(self):
        """Teste de erro interno do servidor"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_bulk_service.importar_keywords_lote.side_effect = Exception("Erro interno")
        
        # Act
        response = self.client.post("/bulk/keywords/import", json={"keywords": ["test"]}, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 500
        self.mock_logger.error.assert_called()
    
    def test_missing_authorization_header(self):
        """Teste de header de autorização ausente"""
        # Act
        response = self.client.post("/bulk/keywords/import", json={"keywords": ["test"]})
        
        # Assert
        assert response.status_code == 401
        self.mock_logger.warning.assert_called()
    
    def test_invalid_json_payload(self):
        """Teste de payload JSON inválido"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/bulk/keywords/import", data="invalid json", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 422
        self.mock_logger.warning.assert_called()
    
    def test_logging_metadata(self):
        """Teste de metadados de logging"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_bulk_service.importar_keywords_lote.return_value = {"imported": 1, "total": 1}
        
        # Act
        response = self.client.post("/bulk/keywords/import", json={"keywords": ["test"]}, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        # Verifica se o logger foi chamado com metadados apropriados
        self.mock_logger.info.assert_called()
        call_args = self.mock_logger.info.call_args[0][0]
        assert "bulk" in call_args.lower()
    
    def test_performance_metrics(self):
        """Teste de métricas de performance"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_bulk_service.importar_keywords_lote.return_value = {"imported": 1, "total": 1}
        
        # Act
        start_time = datetime.now()
        response = self.client.post("/bulk/keywords/import", json={"keywords": ["test"]}, headers={"Authorization": "Bearer token"})
        end_time = datetime.now()
        
        # Assert
        assert response.status_code == 200
        # Verifica se a resposta foi rápida (menos de 1 segundo)
        assert (end_time - start_time).total_seconds() < 1.0 