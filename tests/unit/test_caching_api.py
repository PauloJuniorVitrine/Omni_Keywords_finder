"""
Testes unitários para Caching API
Sistema: Omni Keywords Finder
Módulo: APIs Auxiliares e Utilitárias
Fase: 20.10
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
import json
from datetime import datetime, timedelta

# Mock do módulo principal
mock_caching_module = Mock()
mock_caching_module.router = Mock()

class TestCachingAPI:
    """Testes para API de Cache"""
    
    def setup_method(self):
        """Configuração inicial para cada teste"""
        self.mock_cache_service = Mock()
        self.mock_auth_service = Mock()
        self.mock_logger = Mock()
        
        # Mock das dependências
        with patch('app.api.caching_api.get_cache_service', return_value=self.mock_cache_service), \
             patch('app.api.caching_api.get_auth_service', return_value=self.mock_auth_service), \
             patch('app.api.caching_api.get_logger', return_value=self.mock_logger):
            
            # Importação do módulo após mock
            from app.api.caching_api import router
            self.client = TestClient(router)
    
    def test_get_cache_status_success(self):
        """Teste de sucesso para status do cache"""
        # Arrange
        mock_status = {
            "total_keys": 1500,
            "memory_usage": "256MB",
            "hit_rate": 0.85,
            "miss_rate": 0.15,
            "evictions": 25
        }
        self.mock_cache_service.obter_status.return_value = mock_status
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/caching/status", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_status
        self.mock_cache_service.obter_status.assert_called_once()
        self.mock_logger.info.assert_called()
    
    def test_get_cache_status_unauthorized(self):
        """Teste de erro de autorização"""
        # Arrange
        self.mock_auth_service.validar_token.side_effect = HTTPException(status_code=401)
        
        # Act
        response = self.client.get("/caching/status", headers={"Authorization": "Bearer invalid"})
        
        # Assert
        assert response.status_code == 401
        self.mock_logger.warning.assert_called()
    
    def test_get_cache_key_success(self):
        """Teste de sucesso para busca de chave no cache"""
        # Arrange
        key = "user:123:profile"
        mock_value = {"name": "João", "email": "joao@example.com", "preferences": {"theme": "dark"}}
        self.mock_cache_service.obter_chave.return_value = mock_value
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/caching/key/{key}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_value
        self.mock_cache_service.obter_chave.assert_called_once_with(key)
    
    def test_get_cache_key_not_found(self):
        """Teste de chave não encontrada no cache"""
        # Arrange
        key = "nonexistent:key"
        self.mock_cache_service.obter_chave.return_value = None
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/caching/key/{key}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_set_cache_key_success(self):
        """Teste de sucesso para definir chave no cache"""
        # Arrange
        key = "user:123:profile"
        value = {"name": "João", "email": "joao@example.com"}
        ttl = 3600  # 1 hora
        cache_data = {"key": key, "value": value, "ttl": ttl}
        self.mock_cache_service.definir_chave.return_value = True
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/caching/key", json=cache_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 201
        self.mock_cache_service.definir_chave.assert_called_once_with(key, value, ttl)
    
    def test_set_cache_key_validation_error(self):
        """Teste de erro de validação na definição de chave"""
        # Arrange
        cache_data = {"key": "", "value": None, "ttl": -1}  # Dados inválidos
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/caching/key", json=cache_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 422
        self.mock_logger.warning.assert_called()
    
    def test_delete_cache_key_success(self):
        """Teste de sucesso para exclusão de chave do cache"""
        # Arrange
        key = "user:123:profile"
        self.mock_cache_service.deletar_chave.return_value = True
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.delete(f"/caching/key/{key}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 204
        self.mock_cache_service.deletar_chave.assert_called_once_with(key)
    
    def test_delete_cache_key_not_found(self):
        """Teste de exclusão de chave inexistente"""
        # Arrange
        key = "nonexistent:key"
        self.mock_cache_service.deletar_chave.return_value = False
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.delete(f"/caching/key/{key}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_clear_cache_success(self):
        """Teste de sucesso para limpeza do cache"""
        # Arrange
        pattern = "user:*"  # Limpar apenas chaves de usuário
        mock_result = {"deleted_keys": 150, "pattern": pattern}
        self.mock_cache_service.limpar_cache.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.delete(f"/caching/clear?pattern={pattern}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_result
        self.mock_cache_service.limpar_cache.assert_called_once_with(pattern)
    
    def test_clear_all_cache_success(self):
        """Teste de sucesso para limpeza completa do cache"""
        # Arrange
        mock_result = {"deleted_keys": 1500, "pattern": "*"}
        self.mock_cache_service.limpar_cache.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.delete("/caching/clear", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_result
        self.mock_cache_service.limpar_cache.assert_called_once_with("*")
    
    def test_get_cache_keys_by_pattern_success(self):
        """Teste de sucesso para busca de chaves por padrão"""
        # Arrange
        pattern = "user:*"
        mock_keys = ["user:123:profile", "user:456:profile", "user:789:profile"]
        self.mock_cache_service.buscar_chaves.return_value = mock_keys
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/caching/keys?pattern={pattern}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_keys
        self.mock_cache_service.buscar_chaves.assert_called_once_with(pattern)
    
    def test_get_cache_keys_by_pattern_empty(self):
        """Teste de busca de chaves por padrão sem resultados"""
        # Arrange
        pattern = "nonexistent:*"
        self.mock_cache_service.buscar_chaves.return_value = []
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/caching/keys?pattern={pattern}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == []
        self.mock_cache_service.buscar_chaves.assert_called_once_with(pattern)
    
    def test_get_cache_ttl_success(self):
        """Teste de sucesso para obter TTL de chave"""
        # Arrange
        key = "user:123:profile"
        mock_ttl = {"key": key, "ttl": 1800, "expires_at": "2025-01-27T23:30:00Z"}
        self.mock_cache_service.obter_ttl.return_value = mock_ttl
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/caching/ttl/{key}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_ttl
        self.mock_cache_service.obter_ttl.assert_called_once_with(key)
    
    def test_get_cache_ttl_not_found(self):
        """Teste de TTL para chave inexistente"""
        # Arrange
        key = "nonexistent:key"
        self.mock_cache_service.obter_ttl.return_value = None
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get(f"/caching/ttl/{key}", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_extend_cache_ttl_success(self):
        """Teste de sucesso para estender TTL de chave"""
        # Arrange
        key = "user:123:profile"
        new_ttl = 7200  # 2 horas
        ttl_data = {"ttl": new_ttl}
        mock_result = {"key": key, "new_ttl": new_ttl, "success": True}
        self.mock_cache_service.estender_ttl.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.put(f"/caching/ttl/{key}", json=ttl_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_result
        self.mock_cache_service.estender_ttl.assert_called_once_with(key, new_ttl)
    
    def test_extend_cache_ttl_not_found(self):
        """Teste de extensão de TTL para chave inexistente"""
        # Arrange
        key = "nonexistent:key"
        new_ttl = 7200
        ttl_data = {"ttl": new_ttl}
        self.mock_cache_service.estender_ttl.return_value = None
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.put(f"/caching/ttl/{key}", json=ttl_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_get_cache_metrics_success(self):
        """Teste de sucesso para métricas do cache"""
        # Arrange
        mock_metrics = {
            "hit_rate": 0.85,
            "miss_rate": 0.15,
            "total_requests": 10000,
            "cache_size": "256MB",
            "keys_count": 1500,
            "evictions": 25,
            "avg_response_time": "2.5ms"
        }
        self.mock_cache_service.obter_metricas.return_value = mock_metrics
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/caching/metrics", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_metrics
        self.mock_cache_service.obter_metricas.assert_called_once()
    
    def test_warm_cache_success(self):
        """Teste de sucesso para aquecimento do cache"""
        # Arrange
        warm_data = {
            "patterns": ["user:*", "config:*"],
            "priority": "high"
        }
        mock_result = {"warmed_keys": 500, "patterns": ["user:*", "config:*"]}
        self.mock_cache_service.aquecer_cache.return_value = mock_result
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/caching/warm", json=warm_data, headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_result
        self.mock_cache_service.aquecer_cache.assert_called_once_with(warm_data["patterns"], warm_data["priority"])
    
    def test_get_cache_health_success(self):
        """Teste de sucesso para saúde do cache"""
        # Arrange
        mock_health = {
            "status": "healthy",
            "memory_usage": "75%",
            "connection_pool": "active",
            "last_check": "2025-01-27T22:30:00Z"
        }
        self.mock_cache_service.verificar_saude.return_value = mock_health
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/caching/health", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_health
        self.mock_cache_service.verificar_saude.assert_called_once()
    
    def test_get_cache_health_unhealthy(self):
        """Teste de saúde do cache com problemas"""
        # Arrange
        mock_health = {
            "status": "unhealthy",
            "memory_usage": "95%",
            "connection_pool": "overloaded",
            "last_check": "2025-01-27T22:30:00Z",
            "errors": ["Memory limit exceeded", "Connection pool exhausted"]
        }
        self.mock_cache_service.verificar_saude.return_value = mock_health
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.get("/caching/health", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_health
        self.mock_cache_service.verificar_saude.assert_called_once()
    
    def test_rate_limiting_exceeded(self):
        """Teste de rate limiting excedido"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_cache_service.obter_status.side_effect = HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Act
        response = self.client.get("/caching/status", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 429
        self.mock_logger.warning.assert_called()
    
    def test_internal_server_error(self):
        """Teste de erro interno do servidor"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_cache_service.obter_status.side_effect = Exception("Erro interno")
        
        # Act
        response = self.client.get("/caching/status", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 500
        self.mock_logger.error.assert_called()
    
    def test_missing_authorization_header(self):
        """Teste de header de autorização ausente"""
        # Act
        response = self.client.get("/caching/status")
        
        # Assert
        assert response.status_code == 401
        self.mock_logger.warning.assert_called()
    
    def test_invalid_json_payload(self):
        """Teste de payload JSON inválido"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        
        # Act
        response = self.client.post("/caching/key", data="invalid json", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 422
        self.mock_logger.warning.assert_called()
    
    def test_logging_metadata(self):
        """Teste de metadados de logging"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_cache_service.obter_status.return_value = {}
        
        # Act
        response = self.client.get("/caching/status", headers={"Authorization": "Bearer token"})
        
        # Assert
        assert response.status_code == 200
        # Verifica se o logger foi chamado com metadados apropriados
        self.mock_logger.info.assert_called()
        call_args = self.mock_logger.info.call_args[0][0]
        assert "caching" in call_args.lower()
    
    def test_performance_metrics(self):
        """Teste de métricas de performance"""
        # Arrange
        self.mock_auth_service.validar_token.return_value = {"user_id": 1}
        self.mock_cache_service.obter_status.return_value = {}
        
        # Act
        start_time = datetime.now()
        response = self.client.get("/caching/status", headers={"Authorization": "Bearer token"})
        end_time = datetime.now()
        
        # Assert
        assert response.status_code == 200
        # Verifica se a resposta foi rápida (menos de 1 segundo)
        assert (end_time - start_time).total_seconds() < 1.0 