"""
Testes unitários para Clusters API
Sistema: Omni Keywords Finder
Módulo: APIs Auxiliares e Utilitárias
Fase: 20.7
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
import json
from datetime import datetime, timedelta

# Mock do módulo principal
mock_clusters_module = Mock()
mock_clusters_module.router = Mock()

class TestClustersAPI:
    """Testes para API de Clusters"""
    
    def setup_method(self):
        """Configuração inicial para cada teste"""
        self.mock_clusters_service = Mock()
        self.mock_auth_service = Mock()
        self.mock_logger = Mock()
        
        # Mock das dependências
        with patch('app.api.clusters_api.get_clusters_service', return_value=self.mock_clusters_service), \
             patch('app.api.clusters_api.get_auth_service', return_value=self.mock_auth_service), \
             patch('app.api.clusters_api.get_logger', return_value=self.mock_logger):
            
            # Importação do módulo após mock
            from app.api.clusters_api import router
            self.client = TestClient(router)
    
    def test_get_clusters_success(self):
        """Teste de sucesso para listagem de clusters"""
        # Arrange
        mock_clusters = [
            {"id": 1, "name": "Cluster Marketing", "keywords_count": 150, "status": "active"},
            {"id": 2, "name": "Cluster Tecnologia", "keywords_count": 200, "status": "active"}
        ]
        self.mock_clusters_service.listar_clusters.return_value = mock_clusters
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/clusters/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_clusters
        self.mock_clusters_service.listar_clusters.assert_called_once()
        self.mock_logger.info.assert_called()
    
    def test_get_clusters_unauthorized(self):
        """Teste de erro de autorização"""
        # Arrange
        self.mock_auth_service.validar_token.side_effect = HTTPException(status_code=401)
        
        # Act
        response = self.client.get("/clusters/", headers={"Authorization": "Bearer invalid"})
        
        # Assert
        assert response.status_code == 401
        self.mock_logger.warning.assert_called()
    
    def test_get_clusters_service_error(self):
        """Teste de erro do serviço"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_clusters_service.listar_clusters.side_effect = Exception("Erro interno")
        
        # Act
        response = self.client.get("/clusters/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 500
        self.mock_logger.error.assert_called()
    
    def test_get_cluster_by_id_success(self):
        """Teste de sucesso para busca de cluster por ID"""
        # Arrange
        cluster_id = 1
        mock_cluster = {"id": cluster_id, "name": "Cluster Marketing", "keywords_count": 150, "status": "active"}
        self.mock_clusters_service.buscar_cluster_por_id.return_value = mock_cluster
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/clusters/{cluster_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_cluster
        self.mock_clusters_service.buscar_cluster_por_id.assert_called_once_with(cluster_id)
    
    def test_get_cluster_by_id_not_found(self):
        """Teste de cluster não encontrado"""
        # Arrange
        cluster_id = 999
        self.mock_clusters_service.buscar_cluster_por_id.return_value = None
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/clusters/{cluster_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_create_cluster_success(self):
        """Teste de sucesso para criação de cluster"""
        # Arrange
        cluster_data = {"name": "Novo Cluster", "description": "Descrição do cluster"}
        created_cluster = {"id": 3, **cluster_data, "keywords_count": 0, "status": "active"}
        self.mock_clusters_service.criar_cluster.return_value = created_cluster
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/clusters/", json=cluster_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 201
        assert response.json() == created_cluster
        self.mock_clusters_service.criar_cluster.assert_called_once_with(cluster_data)
    
    def test_create_cluster_validation_error(self):
        """Teste de erro de validação na criação"""
        # Arrange
        cluster_data = {"name": ""}  # Nome vazio
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/clusters/", json=cluster_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 422
        self.mock_logger.warning.assert_called()
    
    def test_update_cluster_success(self):
        """Teste de sucesso para atualização de cluster"""
        # Arrange
        cluster_id = 1
        cluster_data = {"name": "Cluster Atualizado", "description": "Nova descrição"}
        updated_cluster = {"id": cluster_id, **cluster_data, "keywords_count": 150, "status": "active"}
        self.mock_clusters_service.atualizar_cluster.return_value = updated_cluster
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.put(f"/clusters/{cluster_id}", json=cluster_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == updated_cluster
        self.mock_clusters_service.atualizar_cluster.assert_called_once_with(cluster_id, cluster_data)
    
    def test_update_cluster_not_found(self):
        """Teste de atualização de cluster inexistente"""
        # Arrange
        cluster_id = 999
        cluster_data = {"name": "Cluster Atualizado"}
        self.mock_clusters_service.atualizar_cluster.return_value = None
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.put(f"/clusters/{cluster_id}", json=cluster_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_delete_cluster_success(self):
        """Teste de sucesso para exclusão de cluster"""
        # Arrange
        cluster_id = 1
        self.mock_clusters_service.deletar_cluster.return_value = True
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.delete(f"/clusters/{cluster_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 204
        self.mock_clusters_service.deletar_cluster.assert_called_once_with(cluster_id)
    
    def test_delete_cluster_not_found(self):
        """Teste de exclusão de cluster inexistente"""
        # Arrange
        cluster_id = 999
        self.mock_clusters_service.deletar_cluster.return_value = False
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.delete(f"/clusters/{cluster_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_add_keywords_to_cluster_success(self):
        """Teste de sucesso para adicionar keywords ao cluster"""
        # Arrange
        cluster_id = 1
        keywords_data = {"keywords": ["keyword1", "keyword2", "keyword3"]}
        mock_result = {"added": 3, "total": 153}
        self.mock_clusters_service.adicionar_keywords.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post(f"/clusters/{cluster_id}/keywords", json=keywords_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_result
        self.mock_clusters_service.adicionar_keywords.assert_called_once_with(cluster_id, keywords_data["keywords"])
    
    def test_remove_keywords_from_cluster_success(self):
        """Teste de sucesso para remover keywords do cluster"""
        # Arrange
        cluster_id = 1
        keywords_data = {"keywords": ["keyword1", "keyword2"]}
        mock_result = {"removed": 2, "total": 148}
        self.mock_clusters_service.remover_keywords.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.delete(f"/clusters/{cluster_id}/keywords", json=keywords_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_result
        self.mock_clusters_service.remover_keywords.assert_called_once_with(cluster_id, keywords_data["keywords"])
    
    def test_get_cluster_keywords_success(self):
        """Teste de sucesso para listar keywords do cluster"""
        # Arrange
        cluster_id = 1
        mock_keywords = [
            {"keyword": "marketing digital", "volume": 1000, "difficulty": "medium"},
            {"keyword": "marketing de conteúdo", "volume": 800, "difficulty": "easy"}
        ]
        self.mock_clusters_service.obter_keywords_cluster.return_value = mock_keywords
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/clusters/{cluster_id}/keywords", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_keywords
        self.mock_clusters_service.obter_keywords_cluster.assert_called_once_with(cluster_id)
    
    def test_analyze_cluster_success(self):
        """Teste de sucesso para análise do cluster"""
        # Arrange
        cluster_id = 1
        mock_analysis = {
            "cluster_id": cluster_id,
            "total_keywords": 150,
            "avg_volume": 1200,
            "avg_difficulty": "medium",
            "top_keywords": ["keyword1", "keyword2", "keyword3"],
            "recommendations": ["Adicionar mais keywords de baixa dificuldade", "Focar em volume médio"]
        }
        self.mock_clusters_service.analisar_cluster.return_value = mock_analysis
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/clusters/{cluster_id}/analyze", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_analysis
        self.mock_clusters_service.analisar_cluster.assert_called_once_with(cluster_id)
    
    def test_export_cluster_success(self):
        """Teste de sucesso para exportação do cluster"""
        # Arrange
        cluster_id = 1
        format_type = "csv"
        mock_export_data = "keyword,volume,difficulty\nmarketing digital,1000,medium\nmarketing de conteúdo,800,easy"
        self.mock_clusters_service.exportar_cluster.return_value = mock_export_data
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/clusters/{cluster_id}/export?format={format_type}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.content == mock_export_data.encode()
        self.mock_clusters_service.exportar_cluster.assert_called_once_with(cluster_id, format_type)
    
    def test_duplicate_cluster_success(self):
        """Teste de sucesso para duplicação de cluster"""
        # Arrange
        cluster_id = 1
        duplicate_data = {"name": "Cluster Duplicado", "include_keywords": True}
        duplicated_cluster = {"id": 4, "name": "Cluster Duplicado", "keywords_count": 150, "status": "active"}
        self.mock_clusters_service.duplicar_cluster.return_value = duplicated_cluster
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post(f"/clusters/{cluster_id}/duplicate", json=duplicate_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 201
        assert response.json() == duplicated_cluster
        self.mock_clusters_service.duplicar_cluster.assert_called_once_with(cluster_id, duplicate_data)
    
    def test_get_cluster_stats_success(self):
        """Teste de sucesso para estatísticas do cluster"""
        # Arrange
        cluster_id = 1
        mock_stats = {
            "total_keywords": 150,
            "avg_volume": 1200,
            "avg_difficulty": "medium",
            "volume_distribution": {"low": 30, "medium": 80, "high": 40},
            "difficulty_distribution": {"easy": 50, "medium": 70, "hard": 30}
        }
        self.mock_clusters_service.obter_estatisticas.return_value = mock_stats
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/clusters/{cluster_id}/stats", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_stats
        self.mock_clusters_service.obter_estatisticas.assert_called_once_with(cluster_id)
    
    def test_rate_limiting_exceeded(self):
        """Teste de rate limiting excedido"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_clusters_service.listar_clusters.side_effect = HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Act
        response = self.client.get("/clusters/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 429
        self.mock_logger.warning.assert_called()
    
    def test_internal_server_error(self):
        """Teste de erro interno do servidor"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_clusters_service.listar_clusters.side_effect = Exception("Erro interno")
        
        # Act
        response = self.client.get("/clusters/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 500
        self.mock_logger.error.assert_called()
    
    def test_missing_authorization_header(self):
        """Teste de header de autorização ausente"""
        # Act
        response = self.client.get("/clusters/")
        
        # Assert
        assert response.status_code == 401
        self.mock_logger.warning.assert_called()
    
    def test_invalid_json_payload(self):
        """Teste de payload JSON inválido"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/clusters/", data="invalid json", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 422
        self.mock_logger.warning.assert_called()
    
    def test_logging_metadata(self):
        """Teste de metadados de logging"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_clusters_service.listar_clusters.return_value = []
        
        # Act
        response = self.client.get("/clusters/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        # Verifica se o logger foi chamado com metadados apropriados
        self.mock_logger.info.assert_called()
        call_args = self.mock_logger.info.call_args[0][0]
        assert "clusters" in call_args.lower()
    
    def test_performance_metrics(self):
        """Teste de métricas de performance"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_clusters_service.listar_clusters.return_value = []
        
        # Act
        start_time = datetime.now()
        response = self.client.get("/clusters/", headers={"Authorization": "Bearer token"})
        end_time = datetime.now()
        
        # Assert
        assert response.status_code == 200
        # Verifica se a resposta foi rápida (menos de 1 segundo)
        assert (end_time - start_time).total_seconds() < 1.0 