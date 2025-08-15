"""
Testes unitários para Nichos API
Sistema: Omni Keywords Finder
Módulo: APIs Auxiliares e Utilitárias
Fase: 20.1
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
import json
from datetime import datetime, timedelta

# Mock do módulo principal
mock_nichos_module = Mock()
mock_nichos_module.router = Mock()

class TestNichosAPI:
    """Testes para API de Nichos"""
    
    def setup_method(self):
        """Configuração inicial para cada teste"""
        self.mock_nichos_service = Mock()
        self.mock_auth_service = Mock()
        self.mock_logger = Mock()
        
        # Mock das dependências
        with patch('app.api.nichos_api.get_nichos_service', return_value=self.mock_nichos_service), \
             patch('app.api.nichos_api.get_auth_service', return_value=self.mock_auth_service), \
             patch('app.api.nichos_api.get_logger', return_value=self.mock_logger):
            
            # Importação do módulo após mock
            from app.api.nichos_api import router
            self.client = TestClient(router)
    
    def test_get_nichos_success(self):
        """Teste de sucesso para listagem de nichos"""
        # Arrange
        mock_nichos = [
            {"id": 1, "nome": "E-commerce", "descricao": "Vendas online"},
            {"id": 2, "nome": "Saúde", "descricao": "Área médica"}
        ]
        self.mock_nichos_service.listar_nichos.return_value = mock_nichos
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/nichos/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_nichos
        self.mock_nichos_service.listar_nichos.assert_called_once()
        self.mock_logger.info.assert_called()
    
    def test_get_nichos_unauthorized(self):
        """Teste de erro de autorização"""
        # Arrange
        self.mock_auth_service.validar_token.side_effect = HTTPException(status_code=401)
        
        # Act
        response = self.client.get("/nichos/", headers={"Authorization": "Bearer invalid"})
        
        # Assert
        assert response.status_code == 401
        self.mock_logger.warning.assert_called()
    
    def test_get_nichos_service_error(self):
        """Teste de erro do serviço"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_nichos_service.listar_nichos.side_effect = Exception("Erro interno")
        
        # Act
        response = self.client.get("/nichos/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 500
        self.mock_logger.error.assert_called()
    
    def test_get_nicho_by_id_success(self):
        """Teste de sucesso para busca de nicho por ID"""
        # Arrange
        nicho_id = 1
        mock_nicho = {"id": nicho_id, "nome": "E-commerce", "descricao": "Vendas online"}
        self.mock_nichos_service.buscar_nicho_por_id.return_value = mock_nicho
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/nichos/{nicho_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_nicho
        self.mock_nichos_service.buscar_nicho_por_id.assert_called_once_with(nicho_id)
    
    def test_get_nicho_by_id_not_found(self):
        """Teste de nicho não encontrado"""
        # Arrange
        nicho_id = 999
        self.mock_nichos_service.buscar_nicho_por_id.return_value = None
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/nichos/{nicho_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_create_nicho_success(self):
        """Teste de sucesso para criação de nicho"""
        # Arrange
        nicho_data = {"nome": "Novo Nicho", "descricao": "Descrição do nicho"}
        created_nicho = {"id": 3, **nicho_data}
        self.mock_nichos_service.criar_nicho.return_value = created_nicho
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/nichos/", json=nicho_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 201
        assert response.json() == created_nicho
        self.mock_nichos_service.criar_nicho.assert_called_once_with(nicho_data)
    
    def test_create_nicho_validation_error(self):
        """Teste de erro de validação na criação"""
        # Arrange
        nicho_data = {"nome": ""}  # Nome vazio
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/nichos/", json=nicho_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 422
        self.mock_logger.warning.assert_called()
    
    def test_update_nicho_success(self):
        """Teste de sucesso para atualização de nicho"""
        # Arrange
        nicho_id = 1
        nicho_data = {"nome": "Nichos Atualizado", "descricao": "Nova descrição"}
        updated_nicho = {"id": nicho_id, **nicho_data}
        self.mock_nichos_service.atualizar_nicho.return_value = updated_nicho
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.put(f"/nichos/{nicho_id}", json=nicho_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == updated_nicho
        self.mock_nichos_service.atualizar_nicho.assert_called_once_with(nicho_id, nicho_data)
    
    def test_update_nicho_not_found(self):
        """Teste de atualização de nicho inexistente"""
        # Arrange
        nicho_id = 999
        nicho_data = {"nome": "Nichos Atualizado"}
        self.mock_nichos_service.atualizar_nicho.return_value = None
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.put(f"/nichos/{nicho_id}", json=nicho_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_delete_nicho_success(self):
        """Teste de sucesso para exclusão de nicho"""
        # Arrange
        nicho_id = 1
        self.mock_nichos_service.deletar_nicho.return_value = True
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.delete(f"/nichos/{nicho_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 204
        self.mock_nichos_service.deletar_nicho.assert_called_once_with(nicho_id)
    
    def test_delete_nicho_not_found(self):
        """Teste de exclusão de nicho inexistente"""
        # Arrange
        nicho_id = 999
        self.mock_nichos_service.deletar_nicho.return_value = False
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.delete(f"/nichos/{nicho_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_search_nichos_success(self):
        """Teste de sucesso para busca de nichos"""
        # Arrange
        query = "e-commerce"
        mock_results = [{"id": 1, "nome": "E-commerce", "descricao": "Vendas online"}]
        self.mock_nichos_service.buscar_nichos.return_value = mock_results
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/nichos/search?q={query}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_results
        self.mock_nichos_service.buscar_nichos.assert_called_once_with(query)
    
    def test_get_nichos_stats_success(self):
        """Teste de sucesso para estatísticas de nichos"""
        # Arrange
        mock_stats = {"total": 10, "ativos": 8, "inativos": 2}
        self.mock_nichos_service.obter_estatisticas.return_value = mock_stats
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/nichos/stats", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_stats
        self.mock_nichos_service.obter_estatisticas.assert_called_once()
    
    def test_export_nichos_success(self):
        """Teste de sucesso para exportação de nichos"""
        # Arrange
        format_type = "csv"
        mock_export_data = "id,nome,descricao\n1,E-commerce,Vendas online"
        self.mock_nichos_service.exportar_nichos.return_value = mock_export_data
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/nichos/export?format={format_type}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.content == mock_export_data.encode()
        self.mock_nichos_service.exportar_nichos.assert_called_once_with(format_type)
    
    def test_import_nichos_success(self):
        """Teste de sucesso para importação de nichos"""
        # Arrange
        import_data = [{"nome": "Novo Nicho", "descricao": "Descrição"}]
        mock_result = {"importados": 1, "erros": 0}
        self.mock_nichos_service.importar_nichos.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/nichos/import", json=import_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_result
        self.mock_nichos_service.importar_nichos.assert_called_once_with(import_data)
    
    def test_bulk_operations_success(self):
        """Teste de sucesso para operações em lote"""
        # Arrange
        operations = [
            {"action": "create", "data": {"nome": "Nichos 1"}},
            {"action": "update", "id": 1, "data": {"nome": "Nichos Atualizado"}}
        ]
        mock_result = {"sucessos": 2, "erros": 0}
        self.mock_nichos_service.operacoes_lote.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/nichos/bulk", json=operations, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_result
        self.mock_nichos_service.operacoes_lote.assert_called_once_with(operations)
    
    def test_get_nicho_analytics_success(self):
        """Teste de sucesso para analytics de nichos"""
        # Arrange
        nicho_id = 1
        mock_analytics = {"keywords_count": 150, "avg_volume": 5000, "trend": "up"}
        self.mock_nichos_service.obter_analytics.return_value = mock_analytics
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/nichos/{nicho_id}/analytics", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_analytics
        self.mock_nichos_service.obter_analytics.assert_called_once_with(nicho_id)
    
    def test_validate_nicho_name_success(self):
        """Teste de sucesso para validação de nome de nicho"""
        # Arrange
        nome = "E-commerce"
        mock_validation = {"valid": True, "suggestions": []}
        self.mock_nichos_service.validar_nome.return_value = mock_validation
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/nichos/validate-name", json={"nome": nome}, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_validation
        self.mock_nichos_service.validar_nome.assert_called_once_with(nome)
    
    def test_get_nicho_suggestions_success(self):
        """Teste de sucesso para sugestões de nichos"""
        # Arrange
        query = "e-com"
        mock_suggestions = ["E-commerce", "E-commerce B2B", "E-commerce Mobile"]
        self.mock_nichos_service.obter_sugestoes.return_value = mock_suggestions
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/nichos/suggestions?q={query}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_suggestions
        self.mock_nichos_service.obter_sugestoes.assert_called_once_with(query)
    
    def test_rate_limiting_exceeded(self):
        """Teste de rate limiting excedido"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_nichos_service.listar_nichos.side_effect = HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Act
        response = self.client.get("/nichos/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 429
        self.mock_logger.warning.assert_called()
    
    def test_internal_server_error(self):
        """Teste de erro interno do servidor"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_nichos_service.listar_nichos.side_effect = Exception("Erro interno")
        
        # Act
        response = self.client.get("/nichos/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 500
        self.mock_logger.error.assert_called()
    
    def test_missing_authorization_header(self):
        """Teste de header de autorização ausente"""
        # Act
        response = self.client.get("/nichos/")
        
        # Assert
        assert response.status_code == 401
        self.mock_logger.warning.assert_called()
    
    def test_invalid_json_payload(self):
        """Teste de payload JSON inválido"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/nichos/", data="invalid json", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 422
        self.mock_logger.warning.assert_called()
    
    def test_logging_metadata(self):
        """Teste de metadados de logging"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_nichos_service.listar_nichos.return_value = []
        
        # Act
        response = self.client.get("/nichos/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        # Verifica se o logger foi chamado com metadados apropriados
        self.mock_logger.info.assert_called()
        call_args = self.mock_logger.info.call_args[0][0]
        assert "nichos" in call_args.lower()
    
    def test_performance_metrics(self):
        """Teste de métricas de performance"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_nichos_service.listar_nichos.return_value = []
        
        # Act
        start_time = datetime.now()
        response = self.client.get("/nichos/", headers={"Authorization": "Bearer token"})
        end_time = datetime.now()
        
        # Assert
        assert response.status_code == 200
        # Verifica se a resposta foi rápida (menos de 1 segundo)
        assert (end_time - start_time).total_seconds() < 1.0 