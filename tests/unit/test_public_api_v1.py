"""
Testes unitários para Public API V1
Sistema: Omni Keywords Finder
Módulo: APIs Auxiliares e Utilitárias
Fase: 20.6
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
import json
from datetime import datetime, timedelta

# Mock do módulo principal
mock_public_api_module = Mock()
mock_public_api_module.router = Mock()

class TestPublicAPIV1:
    """Testes para API Pública V1"""
    
    def setup_method(self):
        """Configuração inicial para cada teste"""
        self.mock_public_service = Mock()
        self.mock_auth_service = Mock()
        self.mock_logger = Mock()
        
        # Mock das dependências
        with patch('app.api.public_api_v1.get_public_service', return_value=self.mock_public_service), \
             patch('app.api.public_api_v1.get_auth_service', return_value=self.mock_auth_service), \
             patch('app.api.public_api_v1.get_logger', return_value=self.mock_logger):
            
            # Importação do módulo após mock
            from app.api.public_api_v1 import router
            self.client = TestClient(router)
    
    def test_health_check_success(self):
        """Teste de sucesso para health check"""
        # Arrange
        mock_health = {"status": "healthy", "timestamp": "2025-01-27T10:00:00", "version": "1.0.0"}
        self.mock_public_service.health_check.return_value = mock_health
        
        # Act
        response = self.client.get("/public/v1/health")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_health
        self.mock_public_service.health_check.assert_called_once()
    
    def test_health_check_service_error(self):
        """Teste de erro do serviço no health check"""
        # Arrange
        self.mock_public_service.health_check.side_effect = Exception("Erro interno")
        
        # Act
        response = self.client.get("/public/v1/health")
        
        # Assert
        assert response.status_code == 500
        self.mock_logger.error.assert_called()
    
    def test_get_keywords_success(self):
        """Teste de sucesso para busca de keywords públicas"""
        # Arrange
        query = "teste"
        mock_keywords = [
            {"keyword": "teste", "volume": 1000, "difficulty": "medium"},
            {"keyword": "teste online", "volume": 500, "difficulty": "easy"}
        ]
        self.mock_public_service.buscar_keywords.return_value = mock_keywords
        
        # Act
        response = self.client.get(f"/public/v1/keywords?q={query}")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_keywords
        self.mock_public_service.buscar_keywords.assert_called_once_with(query)
    
    def test_get_keywords_no_query(self):
        """Teste de busca de keywords sem query"""
        # Arrange
        mock_keywords = [
            {"keyword": "popular", "volume": 5000, "difficulty": "hard"},
            {"keyword": "trending", "volume": 3000, "difficulty": "medium"}
        ]
        self.mock_public_service.buscar_keywords.return_value = mock_keywords
        
        # Act
        response = self.client.get("/public/v1/keywords")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_keywords
        self.mock_public_service.buscar_keywords.assert_called_once_with("")
    
    def test_get_trending_keywords_success(self):
        """Teste de sucesso para keywords em tendência"""
        # Arrange
        mock_trending = [
            {"keyword": "tendência 1", "growth": 150, "volume": 2000},
            {"keyword": "tendência 2", "growth": 120, "volume": 1500}
        ]
        self.mock_public_service.obter_tendencias.return_value = mock_trending
        
        # Act
        response = self.client.get("/public/v1/keywords/trending")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_trending
        self.mock_public_service.obter_tendencias.assert_called_once()
    
    def test_get_keyword_suggestions_success(self):
        """Teste de sucesso para sugestões de keywords"""
        # Arrange
        query = "marketing"
        mock_suggestions = ["marketing digital", "marketing de conteúdo", "marketing de performance"]
        self.mock_public_service.obter_sugestoes.return_value = mock_suggestions
        
        # Act
        response = self.client.get(f"/public/v1/keywords/suggestions?q={query}")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_suggestions
        self.mock_public_service.obter_sugestoes.assert_called_once_with(query)
    
    def test_get_keyword_analytics_success(self):
        """Teste de sucesso para analytics de keyword"""
        # Arrange
        keyword = "teste"
        mock_analytics = {
            "keyword": keyword,
            "volume": 1000,
            "difficulty": "medium",
            "cpc": 2.50,
            "competition": 0.7
        }
        self.mock_public_service.obter_analytics.return_value = mock_analytics
        
        # Act
        response = self.client.get(f"/public/v1/keywords/{keyword}/analytics")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_analytics
        self.mock_public_service.obter_analytics.assert_called_once_with(keyword)
    
    def test_get_keyword_analytics_not_found(self):
        """Teste de analytics de keyword não encontrada"""
        # Arrange
        keyword = "keyword_inexistente"
        self.mock_public_service.obter_analytics.return_value = None
        
        # Act
        response = self.client.get(f"/public/v1/keywords/{keyword}/analytics")
        
        # Assert
        assert response.status_code == 404
        self.mock_logger.warning.assert_called()
    
    def test_get_related_keywords_success(self):
        """Teste de sucesso para keywords relacionadas"""
        # Arrange
        keyword = "marketing"
        mock_related = [
            {"keyword": "marketing digital", "relevance": 0.9},
            {"keyword": "marketing de conteúdo", "relevance": 0.8}
        ]
        self.mock_public_service.obter_relacionadas.return_value = mock_related
        
        # Act
        response = self.client.get(f"/public/v1/keywords/{keyword}/related")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_related
        self.mock_public_service.obter_relacionadas.assert_called_once_with(keyword)
    
    def test_get_keyword_volume_history_success(self):
        """Teste de sucesso para histórico de volume de keyword"""
        # Arrange
        keyword = "teste"
        mock_history = [
            {"date": "2025-01-20", "volume": 950},
            {"date": "2025-01-21", "volume": 1000},
            {"date": "2025-01-22", "volume": 1050}
        ]
        self.mock_public_service.obter_historico_volume.return_value = mock_history
        
        # Act
        response = self.client.get(f"/public/v1/keywords/{keyword}/volume-history")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_history
        self.mock_public_service.obter_historico_volume.assert_called_once_with(keyword)
    
    def test_get_keyword_competitors_success(self):
        """Teste de sucesso para competidores de keyword"""
        # Arrange
        keyword = "teste"
        mock_competitors = [
            {"domain": "competitor1.com", "position": 1, "traffic": 10000},
            {"domain": "competitor2.com", "position": 2, "traffic": 8000}
        ]
        self.mock_public_service.obter_competidores.return_value = mock_competitors
        
        # Act
        response = self.client.get(f"/public/v1/keywords/{keyword}/competitors")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_competitors
        self.mock_public_service.obter_competidores.assert_called_once_with(keyword)
    
    def test_get_keyword_questions_success(self):
        """Teste de sucesso para perguntas relacionadas à keyword"""
        # Arrange
        keyword = "marketing"
        mock_questions = [
            "O que é marketing digital?",
            "Como fazer marketing de conteúdo?",
            "Quais são as estratégias de marketing?"
        ]
        self.mock_public_service.obter_perguntas.return_value = mock_questions
        
        # Act
        response = self.client.get(f"/public/v1/keywords/{keyword}/questions")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_questions
        self.mock_public_service.obter_perguntas.assert_called_once_with(keyword)
    
    def test_get_keyword_content_ideas_success(self):
        """Teste de sucesso para ideias de conteúdo baseadas na keyword"""
        # Arrange
        keyword = "marketing digital"
        mock_ideas = [
            {"title": "Guia Completo de Marketing Digital", "type": "blog"},
            {"title": "10 Estratégias de Marketing Digital", "type": "video"}
        ]
        self.mock_public_service.obter_ideias_conteudo.return_value = mock_ideas
        
        # Act
        response = self.client.get(f"/public/v1/keywords/{keyword}/content-ideas")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_ideas
        self.mock_public_service.obter_ideias_conteudo.assert_called_once_with(keyword)
    
    def test_get_keyword_difficulty_analysis_success(self):
        """Teste de sucesso para análise de dificuldade da keyword"""
        # Arrange
        keyword = "teste"
        mock_analysis = {
            "keyword": keyword,
            "difficulty_score": 75,
            "factors": {
                "competition": "high",
                "domain_authority": "medium",
                "content_quality": "high"
            },
            "recommendations": ["Focar em conteúdo de qualidade", "Construir backlinks"]
        }
        self.mock_public_service.analisar_dificuldade.return_value = mock_analysis
        
        # Act
        response = self.client.get(f"/public/v1/keywords/{keyword}/difficulty-analysis")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_analysis
        self.mock_public_service.analisar_dificuldade.assert_called_once_with(keyword)
    
    def test_get_keyword_seasonality_success(self):
        """Teste de sucesso para sazonalidade da keyword"""
        # Arrange
        keyword = "presentes natal"
        mock_seasonality = [
            {"month": "dezembro", "volume": 5000, "trend": "peak"},
            {"month": "janeiro", "volume": 500, "trend": "low"}
        ]
        self.mock_public_service.obter_sazonalidade.return_value = mock_seasonality
        
        # Act
        response = self.client.get(f"/public/v1/keywords/{keyword}/seasonality")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_seasonality
        self.mock_public_service.obter_sazonalidade.assert_called_once_with(keyword)
    
    def test_get_keyword_local_data_success(self):
        """Teste de sucesso para dados locais da keyword"""
        # Arrange
        keyword = "restaurante"
        location = "São Paulo"
        mock_local_data = [
            {"keyword": f"{keyword} {location}", "volume": 2000, "local_competition": "high"},
            {"keyword": f"melhor {keyword} {location}", "volume": 1500, "local_competition": "medium"}
        ]
        self.mock_public_service.obter_dados_locais.return_value = mock_local_data
        
        # Act
        response = self.client.get(f"/public/v1/keywords/{keyword}/local?location={location}")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_local_data
        self.mock_public_service.obter_dados_locais.assert_called_once_with(keyword, location)
    
    def test_rate_limiting_exceeded(self):
        """Teste de rate limiting excedido"""
        # Arrange
        self.mock_public_service.buscar_keywords.side_effect = HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Act
        response = self.client.get("/public/v1/keywords?q=teste")
        
        # Assert
        assert response.status_code == 429
        self.mock_logger.warning.assert_called()
    
    def test_internal_server_error(self):
        """Teste de erro interno do servidor"""
        # Arrange
        self.mock_public_service.buscar_keywords.side_effect = Exception("Erro interno")
        
        # Act
        response = self.client.get("/public/v1/keywords?q=teste")
        
        # Assert
        assert response.status_code == 500
        self.mock_logger.error.assert_called()
    
    def test_logging_metadata(self):
        """Teste de metadados de logging"""
        # Arrange
        self.mock_public_service.buscar_keywords.return_value = []
        
        # Act
        response = self.client.get("/public/v1/keywords?q=teste")
        
        # Assert
        assert response.status_code == 200
        # Verifica se o logger foi chamado com metadados apropriados
        self.mock_logger.info.assert_called()
        call_args = self.mock_logger.info.call_args[0][0]
        assert "public" in call_args.lower()
    
    def test_performance_metrics(self):
        """Teste de métricas de performance"""
        # Arrange
        self.mock_public_service.buscar_keywords.return_value = []
        
        # Act
        start_time = datetime.now()
        response = self.client.get("/public/v1/keywords?q=teste")
        end_time = datetime.now()
        
        # Assert
        assert response.status_code == 200
        # Verifica se a resposta foi rápida (menos de 1 segundo)
        assert (end_time - start_time).total_seconds() < 1.0
    
    def test_cors_headers(self):
        """Teste de headers CORS"""
        # Arrange
        self.mock_public_service.health_check.return_value = {"status": "healthy"}
        
        # Act
        response = self.client.options("/public/v1/health")
        
        # Assert
        assert response.status_code == 200
        # Verifica se os headers CORS estão presentes
        assert "access-control-allow-origin" in response.headers
    
    def test_api_version_header(self):
        """Teste de header de versão da API"""
        # Arrange
        self.mock_public_service.health_check.return_value = {"status": "healthy"}
        
        # Act
        response = self.client.get("/public/v1/health")
        
        # Assert
        assert response.status_code == 200
        # Verifica se o header de versão está presente
        assert "x-api-version" in response.headers
        assert response.headers["x-api-version"] == "1.0.0" 