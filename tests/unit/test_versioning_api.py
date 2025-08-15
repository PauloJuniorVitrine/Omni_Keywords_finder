"""
Testes unitários para Versioning API
Sistema: Omni Keywords Finder
Módulo: APIs Auxiliares e Utilitárias
Fase: 20.9
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
import json
from datetime import datetime, timedelta

# Mock do módulo principal
mock_versioning_module = Mock()
mock_versioning_module.router = Mock()

class TestVersioningAPI:
    """Testes para API de Versionamento"""
    
    def setup_method(self):
        """Configuração inicial para cada teste"""
        self.mock_versioning_service = Mock()
        self.mock_auth_service = Mock()
        self.mock_logger = Mock()
        
        # Mock das dependências
        with patch('app.api.versioning_api.get_versioning_service', return_value=self.mock_versioning_service), \
             patch('app.api.versioning_api.get_auth_service', return_value=self.mock_auth_service), \
             patch('app.api.versioning_api.get_logger', return_value=self.mock_logger):
            
            # Importação do módulo após mock
            from app.api.versioning_api import router
            self.client = TestClient(router)
    
    def test_get_versions_success(self):
        """Teste de sucesso para listagem de versões"""
        # Arrange
        mock_versions = [
            {"version": "1.0.0", "release_date": "2025-01-01", "status": "stable"},
            {"version": "1.1.0", "release_date": "2025-01-15", "status": "stable"},
            {"version": "1.2.0", "release_date": "2025-01-27", "status": "beta"}
        ]
        self.mock_versioning_service.listar_versoes.return_value = mock_versions
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/versioning/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_versions
        self.mock_versioning_service.listar_versoes.assert_called_once()
        self.mock_logger.info.assert_called()
    
    def test_get_versions_unauthorized(self):
        """Teste de erro de autorização"""
        # Arrange
        self.mock_auth_service.validar_token.side_effect = HTTPException(status_code=401)
        
        # Act
        response = self.client.get("/versioning/", headers={"Authorization": "Bearer invalid"})
        
        # Assert
        assert response.status_code == 401
        self.mock_logger.warning.assert_called()
    
    def test_get_versions_service_error(self):
        """Teste de erro do serviço"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_versioning_service.listar_versoes.side_effect = Exception("Erro interno")
        
        # Act
        response = self.client.get("/versioning/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 500
        self.mock_logger.error.assert_called()
    
    def test_get_version_by_id_success(self):
        """Teste de sucesso para busca de versão por ID"""
        # Arrange
        version_id = "1.2.0"
        mock_version = {"version": version_id, "release_date": "2025-01-27", "status": "beta", "changelog": "Nova funcionalidade"}
        self.mock_versioning_service.buscar_versao_por_id.return_value = mock_version
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/versioning/{version_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_version
        self.mock_versioning_service.buscar_versao_por_id.assert_called_once_with(version_id)
    
    def test_get_version_by_id_not_found(self):
        """Teste de versão não encontrada"""
        # Arrange
        version_id = "999.999.999"
        self.mock_versioning_service.buscar_versao_por_id.return_value = None
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/versioning/{version_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_create_version_success(self):
        """Teste de sucesso para criação de versão"""
        # Arrange
        version_data = {"version": "1.3.0", "changelog": "Correções de bugs", "status": "alpha"}
        created_version = {"version": "1.3.0", "release_date": "2025-01-27", "changelog": "Correções de bugs", "status": "alpha"}
        self.mock_versioning_service.criar_versao.return_value = created_version
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/versioning/", json=version_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 201
        assert response.json() == created_version
        self.mock_versioning_service.criar_versao.assert_called_once_with(version_data)
    
    def test_create_version_validation_error(self):
        """Teste de erro de validação na criação"""
        # Arrange
        version_data = {"version": "invalid", "changelog": ""}  # Versão inválida
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/versioning/", json=version_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 422
        self.mock_logger.warning.assert_called()
    
    def test_update_version_success(self):
        """Teste de sucesso para atualização de versão"""
        # Arrange
        version_id = "1.2.0"
        version_data = {"status": "stable", "changelog": "Versão estável"}
        updated_version = {"version": version_id, "release_date": "2025-01-27", "status": "stable", "changelog": "Versão estável"}
        self.mock_versioning_service.atualizar_versao.return_value = updated_version
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.put(f"/versioning/{version_id}", json=version_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == updated_version
        self.mock_versioning_service.atualizar_versao.assert_called_once_with(version_id, version_data)
    
    def test_update_version_not_found(self):
        """Teste de atualização de versão inexistente"""
        # Arrange
        version_id = "999.999.999"
        version_data = {"status": "stable"}
        self.mock_versioning_service.atualizar_versao.return_value = None
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.put(f"/versioning/{version_id}", json=version_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_delete_version_success(self):
        """Teste de sucesso para exclusão de versão"""
        # Arrange
        version_id = "1.0.0"
        self.mock_versioning_service.deletar_versao.return_value = True
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.delete(f"/versioning/{version_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 204
        self.mock_versioning_service.deletar_versao.assert_called_once_with(version_id)
    
    def test_delete_version_not_found(self):
        """Teste de exclusão de versão inexistente"""
        # Arrange
        version_id = "999.999.999"
        self.mock_versioning_service.deletar_versao.return_value = False
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.delete(f"/versioning/{version_id}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_get_current_version_success(self):
        """Teste de sucesso para versão atual"""
        # Arrange
        mock_current = {"version": "1.2.0", "release_date": "2025-01-27", "status": "stable"}
        self.mock_versioning_service.obter_versao_atual.return_value = mock_current
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/versioning/current", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_current
        self.mock_versioning_service.obter_versao_atual.assert_called_once()
    
    def test_get_latest_version_success(self):
        """Teste de sucesso para versão mais recente"""
        # Arrange
        mock_latest = {"version": "1.3.0", "release_date": "2025-01-28", "status": "alpha"}
        self.mock_versioning_service.obter_versao_mais_recente.return_value = mock_latest
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/versioning/latest", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_latest
        self.mock_versioning_service.obter_versao_mais_recente.assert_called_once()
    
    def test_get_version_changelog_success(self):
        """Teste de sucesso para changelog da versão"""
        # Arrange
        version_id = "1.2.0"
        mock_changelog = {
            "version": version_id,
            "changes": [
                {"type": "feature", "description": "Nova funcionalidade"},
                {"type": "fix", "description": "Correção de bug"}
            ]
        }
        self.mock_versioning_service.obter_changelog.return_value = mock_changelog
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/versioning/{version_id}/changelog", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_changelog
        self.mock_versioning_service.obter_changelog.assert_called_once_with(version_id)
    
    def test_compare_versions_success(self):
        """Teste de sucesso para comparação de versões"""
        # Arrange
        version1 = "1.1.0"
        version2 = "1.2.0"
        mock_comparison = {
            "version1": version1,
            "version2": version2,
            "differences": [
                {"type": "feature", "description": "Nova funcionalidade adicionada"},
                {"type": "fix", "description": "Bug corrigido"}
            ]
        }
        self.mock_versioning_service.comparar_versoes.return_value = mock_comparison
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/versioning/compare?version1={version1}&version2={version2}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_comparison
        self.mock_versioning_service.comparar_versoes.assert_called_once_with(version1, version2)
    
    def test_get_version_stats_success(self):
        """Teste de sucesso para estatísticas de versões"""
        # Arrange
        mock_stats = {
            "total_versions": 10,
            "stable_versions": 7,
            "beta_versions": 2,
            "alpha_versions": 1,
            "latest_release": "2025-01-27"
        }
        self.mock_versioning_service.obter_estatisticas.return_value = mock_stats
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/versioning/stats", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_stats
        self.mock_versioning_service.obter_estatisticas.assert_called_once()
    
    def test_validate_version_format_success(self):
        """Teste de sucesso para validação de formato de versão"""
        # Arrange
        version = "1.2.3"
        mock_validation = {"valid": True, "format": "semantic", "suggestions": []}
        self.mock_versioning_service.validar_formato_versao.return_value = mock_validation
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/versioning/validate-format", json={"version": version}, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_validation
        self.mock_versioning_service.validar_formato_versao.assert_called_once_with(version)
    
    def test_validate_version_format_invalid(self):
        """Teste de validação de formato de versão inválido"""
        # Arrange
        version = "invalid_version"
        mock_validation = {"valid": False, "format": "unknown", "suggestions": ["1.0.0", "1.0.1"]}
        self.mock_versioning_service.validar_formato_versao.return_value = mock_validation
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/versioning/validate-format", json={"version": version}, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_validation
        self.mock_versioning_service.validar_formato_versao.assert_called_once_with(version)
    
    def test_rate_limiting_exceeded(self):
        """Teste de rate limiting excedido"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_versioning_service.listar_versoes.side_effect = HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Act
        response = self.client.get("/versioning/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 429
        self.mock_logger.warning.assert_called()
    
    def test_internal_server_error(self):
        """Teste de erro interno do servidor"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_versioning_service.listar_versoes.side_effect = Exception("Erro interno")
        
        # Act
        response = self.client.get("/versioning/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 500
        self.mock_logger.error.assert_called()
    
    def test_missing_authorization_header(self):
        """Teste de header de autorização ausente"""
        # Act
        response = self.client.get("/versioning/")
        
        # Assert
        assert response.status_code == 401
        self.mock_logger.warning.assert_called()
    
    def test_invalid_json_payload(self):
        """Teste de payload JSON inválido"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/versioning/", data="invalid json", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 422
        self.mock_logger.warning.assert_called()
    
    def test_logging_metadata(self):
        """Teste de metadados de logging"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_versioning_service.listar_versoes.return_value = []
        
        # Act
        response = self.client.get("/versioning/", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        # Verifica se o logger foi chamado com metadados apropriados
        self.mock_logger.info.assert_called()
        call_args = self.mock_logger.info.call_args[0][0]
        assert "versioning" in call_args.lower()
    
    def test_performance_metrics(self):
        """Teste de métricas de performance"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_versioning_service.listar_versoes.return_value = []
        
        # Act
        start_time = datetime.now()
        response = self.client.get("/versioning/", headers={"Authorization": "Bearer token"})
        end_time = datetime.now()
        
        # Assert
        assert response.status_code == 200
        # Verifica se a resposta foi rápida (menos de 1 segundo)
        assert (end_time - start_time).total_seconds() < 1.0 