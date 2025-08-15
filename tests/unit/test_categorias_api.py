"""
Testes unitários para Categorias API
Sistema: Omni Keywords Finder
Módulo: APIs Auxiliares e Utilitárias
Fase: 20.2
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
import json
from datetime import datetime, timedelta

# Mock do módulo principal
mock_categorias_module = Mock()
mock_categorias_module.router = Mock()

class TestCategoriasAPI:
    """Testes para API de Categorias"""
    
    def setup_method(self):
        """Configuração inicial para cada teste"""
        self.mock_categorias_service = Mock()
        self.mock_auth_service = Mock()
        self.mock_logger = Mock()
        
        # Mock das dependências
        with patch('app.api.categorias_api.get_categorias_service', return_value=self.mock_categorias_service), \
             patch('app.api.categorias_api.get_auth_service', return_value=self.mock_auth_service), \
             patch('app.api.categorias_api.get_logger', return_value=self.mock_logger):
            
            # Importação do módulo após mock
            from app.api.categorias_api import router
            self.client = TestClient(router)
    
    def test_get_categorias_success(self):
        """Teste de sucesso para listagem de categorias"""
        # Arrange
        mock_categorias = [
            {"id": 1, "nome": "Marketing Digital", "descricao": "Estratégias de marketing"},
            {"id": 2, "nome": "Tecnologia", "descricao": "Inovação tecnológica"}
        ]
        self.mock_categorias_service.listar_categorias.return_value = mock_categorias
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/categorias/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_categorias
        self.mock_categorias_service.listar_categorias.assert_called_once()
        self.mock_logger.info.assert_called()
    
    def test_get_categorias_unauthorized(self):
        """Teste de erro de autorização"""
        # Arrange
        self.mock_auth_service.validar_token.side_effect = HTTPException(status_code=401)
        
        # Act
        response = self.client.get("/categorias/", headers={"Authorization": "Bearer invalid"})
        
        # Assert
        assert response.status_code == 401
        self.mock_logger.warning.assert_called()
    
    def test_get_categorias_service_error(self):
        """Teste de erro do serviço"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_categorias_service.listar_categorias.side_effect = Exception("Erro interno")
        
        # Act
        response = self.client.get("/categorias/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 500
        self.mock_logger.error.assert_called()
    
    def test_get_categoria_by_id_success(self):
        """Teste de sucesso para busca de categoria por ID"""
        # Arrange
        categoria_id = 1
        mock_categoria = {"id": categoria_id, "nome": "Marketing Digital", "descricao": "Estratégias de marketing"}
        self.mock_categorias_service.buscar_categoria_por_id.return_value = mock_categoria
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/categorias/{categoria_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_categoria
        self.mock_categorias_service.buscar_categoria_por_id.assert_called_once_with(categoria_id)
    
    def test_get_categoria_by_id_not_found(self):
        """Teste de categoria não encontrada"""
        # Arrange
        categoria_id = 999
        self.mock_categorias_service.buscar_categoria_por_id.return_value = None
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/categorias/{categoria_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_create_categoria_success(self):
        """Teste de sucesso para criação de categoria"""
        # Arrange
        categoria_data = {"nome": "Nova Categoria", "descricao": "Descrição da categoria"}
        created_categoria = {"id": 3, **categoria_data}
        self.mock_categorias_service.criar_categoria.return_value = created_categoria
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/categorias/", json=categoria_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 201
        assert response.json() == created_categoria
        self.mock_categorias_service.criar_categoria.assert_called_once_with(categoria_data)
    
    def test_create_categoria_validation_error(self):
        """Teste de erro de validação na criação"""
        # Arrange
        categoria_data = {"nome": ""}  # Nome vazio
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/categorias/", json=categoria_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 422
        self.mock_logger.warning.assert_called()
    
    def test_update_categoria_success(self):
        """Teste de sucesso para atualização de categoria"""
        # Arrange
        categoria_id = 1
        categoria_data = {"nome": "Categoria Atualizada", "descricao": "Nova descrição"}
        updated_categoria = {"id": categoria_id, **categoria_data}
        self.mock_categorias_service.atualizar_categoria.return_value = updated_categoria
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.put(f"/categorias/{categoria_id}", json=categoria_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == updated_categoria
        self.mock_categorias_service.atualizar_categoria.assert_called_once_with(categoria_id, categoria_data)
    
    def test_update_categoria_not_found(self):
        """Teste de atualização de categoria inexistente"""
        # Arrange
        categoria_id = 999
        categoria_data = {"nome": "Categoria Atualizada"}
        self.mock_categorias_service.atualizar_categoria.return_value = None
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.put(f"/categorias/{categoria_id}", json=categoria_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_delete_categoria_success(self):
        """Teste de sucesso para exclusão de categoria"""
        # Arrange
        categoria_id = 1
        self.mock_categorias_service.deletar_categoria.return_value = True
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.delete(f"/categorias/{categoria_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 204
        self.mock_categorias_service.deletar_categoria.assert_called_once_with(categoria_id)
    
    def test_delete_categoria_not_found(self):
        """Teste de exclusão de categoria inexistente"""
        # Arrange
        categoria_id = 999
        self.mock_categorias_service.deletar_categoria.return_value = False
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.delete(f"/categorias/{categoria_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_search_categorias_success(self):
        """Teste de sucesso para busca de categorias"""
        # Arrange
        query = "marketing"
        mock_results = [{"id": 1, "nome": "Marketing Digital", "descricao": "Estratégias de marketing"}]
        self.mock_categorias_service.buscar_categorias.return_value = mock_results
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/categorias/search?q={query}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_results
        self.mock_categorias_service.buscar_categorias.assert_called_once_with(query)
    
    def test_get_categorias_stats_success(self):
        """Teste de sucesso para estatísticas de categorias"""
        # Arrange
        mock_stats = {"total": 15, "ativas": 12, "inativas": 3}
        self.mock_categorias_service.obter_estatisticas.return_value = mock_stats
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/categorias/stats", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_stats
        self.mock_categorias_service.obter_estatisticas.assert_called_once()
    
    def test_export_categorias_success(self):
        """Teste de sucesso para exportação de categorias"""
        # Arrange
        format_type = "csv"
        mock_export_data = "id,nome,descricao\n1,Marketing Digital,Estratégias de marketing"
        self.mock_categorias_service.exportar_categorias.return_value = mock_export_data
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/categorias/export?format={format_type}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.content == mock_export_data.encode()
        self.mock_categorias_service.exportar_categorias.assert_called_once_with(format_type)
    
    def test_import_categorias_success(self):
        """Teste de sucesso para importação de categorias"""
        # Arrange
        import_data = [{"nome": "Nova Categoria", "descricao": "Descrição"}]
        mock_result = {"importadas": 1, "erros": 0}
        self.mock_categorias_service.importar_categorias.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/categorias/import", json=import_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_result
        self.mock_categorias_service.importar_categorias.assert_called_once_with(import_data)
    
    def test_bulk_operations_success(self):
        """Teste de sucesso para operações em lote"""
        # Arrange
        operations = [
            {"action": "create", "data": {"nome": "Categoria 1"}},
            {"action": "update", "id": 1, "data": {"nome": "Categoria Atualizada"}}
        ]
        mock_result = {"sucessos": 2, "erros": 0}
        self.mock_categorias_service.operacoes_lote.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/categorias/bulk", json=operations, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_result
        self.mock_categorias_service.operacoes_lote.assert_called_once_with(operations)
    
    def test_get_categoria_analytics_success(self):
        """Teste de sucesso para analytics de categorias"""
        # Arrange
        categoria_id = 1
        mock_analytics = {"keywords_count": 200, "avg_volume": 8000, "trend": "up"}
        self.mock_categorias_service.obter_analytics.return_value = mock_analytics
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/categorias/{categoria_id}/analytics", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_analytics
        self.mock_categorias_service.obter_analytics.assert_called_once_with(categoria_id)
    
    def test_validate_categoria_name_success(self):
        """Teste de sucesso para validação de nome de categoria"""
        # Arrange
        nome = "Marketing Digital"
        mock_validation = {"valid": True, "suggestions": []}
        self.mock_categorias_service.validar_nome.return_value = mock_validation
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/categorias/validate-name", json={"nome": nome}, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_validation
        self.mock_categorias_service.validar_nome.assert_called_once_with(nome)
    
    def test_get_categoria_suggestions_success(self):
        """Teste de sucesso para sugestões de categorias"""
        # Arrange
        query = "mark"
        mock_suggestions = ["Marketing Digital", "Marketing de Conteúdo", "Marketing de Performance"]
        self.mock_categorias_service.obter_sugestoes.return_value = mock_suggestions
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/categorias/suggestions?q={query}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_suggestions
        self.mock_categorias_service.obter_sugestoes.assert_called_once_with(query)
    
    def test_rate_limiting_exceeded(self):
        """Teste de rate limiting excedido"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_categorias_service.listar_categorias.side_effect = HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Act
        response = self.client.get("/categorias/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 429
        self.mock_logger.warning.assert_called()
    
    def test_internal_server_error(self):
        """Teste de erro interno do servidor"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_categorias_service.listar_categorias.side_effect = Exception("Erro interno")
        
        # Act
        response = self.client.get("/categorias/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 500
        self.mock_logger.error.assert_called()
    
    def test_missing_authorization_header(self):
        """Teste de header de autorização ausente"""
        # Act
        response = self.client.get("/categorias/")
        
        # Assert
        assert response.status_code == 401
        self.mock_logger.warning.assert_called()
    
    def test_invalid_json_payload(self):
        """Teste de payload JSON inválido"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/categorias/", data="invalid json", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 422
        self.mock_logger.warning.assert_called()
    
    def test_logging_metadata(self):
        """Teste de metadados de logging"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_categorias_service.listar_categorias.return_value = []
        
        # Act
        response = self.client.get("/categorias/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        # Verifica se o logger foi chamado com metadados apropriados
        self.mock_logger.info.assert_called()
        call_args = self.mock_logger.info.call_args[0][0]
        assert "categorias" in call_args.lower()
    
    def test_performance_metrics(self):
        """Teste de métricas de performance"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_categorias_service.listar_categorias.return_value = []
        
        # Act
        start_time = datetime.now()
        response = self.client.get("/categorias/", headers={"Authorization": "Bearer token"})
        end_time = datetime.now()
        
        # Assert
        assert response.status_code == 200
        # Verifica se a resposta foi rápida (menos de 1 segundo)
        assert (end_time - start_time).total_seconds() < 1.0 