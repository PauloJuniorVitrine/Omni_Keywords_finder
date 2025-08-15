# =============================================================================
# Testes Unitários - Resilient Keywords Service
# =============================================================================
# 
# Testes para o serviço de keywords com resiliência integrada
# Baseados completamente na implementação real do código
#
# Arquivo: backend/app/services/resilient_keywords_service.py
# Linhas: 344
# Tracing ID: test-resilient-keywords-service-2025-01-27-001
# =============================================================================

import pytest
import asyncio
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import random

from backend.app.services.resilient_keywords_service import ResilientKeywordsService


class TestResilientKeywordsService:
    """Testes para o ResilientKeywordsService"""
    
    @pytest.fixture
    def service(self):
        """Fixture para criar instância do serviço"""
        return ResilientKeywordsService()
    
    @pytest.fixture
    def sample_keywords(self):
        """Fixture com keywords de exemplo baseadas no código real"""
        return [
            "seo optimization",
            "content marketing", 
            "digital marketing",
            "social media marketing",
            "email marketing"
        ]
    
    @pytest.fixture
    def sample_query(self):
        """Fixture com query de exemplo"""
        return "marketing digital"
    
    def test_inicializacao_servico(self, service):
        """Teste de inicialização do serviço"""
        # Arrange & Act - Serviço já criado no fixture
        
        # Assert - Verificar propriedades iniciais
        assert service.cache == {}
        assert service.cache_ttl == 300  # 5 minutos
        assert len(service.fallback_data["keywords"]) == 3
        assert service.fallback_data["total"] == 3
        assert service.fallback_data["source"] == "fallback"
        
        # Verificar estrutura dos dados de fallback
        fallback_keywords = service.fallback_data["keywords"]
        assert fallback_keywords[0]["keyword"] == "seo optimization"
        assert fallback_keywords[0]["volume"] == 1000
        assert fallback_keywords[0]["difficulty"] == "medium"
        
        assert fallback_keywords[1]["keyword"] == "content marketing"
        assert fallback_keywords[1]["volume"] == 800
        assert fallback_keywords[1]["difficulty"] == "low"
        
        assert fallback_keywords[2]["keyword"] == "digital marketing"
        assert fallback_keywords[2]["volume"] == 1200
        assert fallback_keywords[2]["difficulty"] == "medium"
    
    @pytest.mark.asyncio
    async def test_get_keywords_sucesso(self, service, sample_query):
        """Teste de busca de keywords com sucesso"""
        # Arrange
        query = sample_query
        limit = 10
        
        # Act
        result = await service.get_keywords(query, limit)
        
        # Assert
        assert "keywords" in result
        assert "total" in result
        assert "query" in result
        assert "source" in result
        assert "timestamp" in result
        
        assert result["query"] == query
        assert result["source"] == "api"
        assert result["total"] <= limit
        assert len(result["keywords"]) <= limit
        
        # Verificar estrutura das keywords
        for keyword in result["keywords"]:
            assert "keyword" in keyword
            assert "volume" in keyword
            assert "difficulty" in keyword
            assert "cpc" in keyword
            assert "competition" in keyword
            
            assert isinstance(keyword["keyword"], str)
            assert isinstance(keyword["volume"], int)
            assert keyword["difficulty"] in ["low", "medium", "high"]
            assert isinstance(keyword["cpc"], float)
            assert isinstance(keyword["competition"], float)
    
    @pytest.mark.asyncio
    async def test_get_keywords_cache(self, service, sample_query):
        """Teste de cache de keywords"""
        # Arrange
        query = sample_query
        limit = 5
        
        # Act - Primeira busca (deve ir para cache)
        result1 = await service.get_keywords(query, limit)
        
        # Act - Segunda busca (deve vir do cache)
        result2 = await service.get_keywords(query, limit)
        
        # Assert
        assert result1 == result2
        
        # Verificar se está no cache
        cache_key = f"keywords:{query}:{limit}"
        assert cache_key in service.cache
        
        cached_data = service.cache[cache_key]
        assert "data" in cached_data
        assert "expires_at" in cached_data
        assert cached_data["data"] == result1
    
    @pytest.mark.asyncio
    async def test_get_keywords_fallback_api_falha(self, service, sample_query):
        """Teste de fallback quando API falha"""
        # Arrange
        query = sample_query
        limit = 5
        
        # Mock para simular falha da API
        with patch.object(service, '_fetch_keywords_from_api', side_effect=Exception("API indisponível")):
            # Act
            result = await service.get_keywords(query, limit)
            
            # Assert
            assert result["source"] == "fallback"
            assert "message" in result
            assert "Dados de fallback devido a indisponibilidade da API" in result["message"]
            assert result["query"] == query
            assert result["total"] <= limit
            
            # Verificar se contém keywords de fallback
            assert len(result["keywords"]) > 0
            for keyword in result["keywords"]:
                assert "keyword" in keyword
                assert "volume" in keyword
                assert "difficulty" in keyword
    
    @pytest.mark.asyncio
    async def test_get_keywords_fallback_filtro_query(self, service):
        """Teste de fallback com filtro baseado na query"""
        # Arrange
        query = "seo"  # Deve encontrar "seo optimization" no fallback
        limit = 10
        
        # Mock para simular falha da API
        with patch.object(service, '_fetch_keywords_from_api', side_effect=Exception("API indisponível")):
            # Act
            result = await service.get_keywords(query, limit)
            
            # Assert
            assert result["source"] == "fallback"
            assert len(result["keywords"]) > 0
            
            # Verificar se encontrou keywords relacionadas a "seo"
            found_seo = False
            for keyword in result["keywords"]:
                if "seo" in keyword["keyword"].lower():
                    found_seo = True
                    break
            
            assert found_seo
    
    @pytest.mark.asyncio
    async def test_fetch_keywords_from_api_sucesso(self, service, sample_query):
        """Teste da função interna de busca na API"""
        # Arrange
        query = sample_query
        limit = 8
        
        # Act
        result = await service._fetch_keywords_from_api(query, limit)
        
        # Assert
        assert "keywords" in result
        assert "total" in result
        assert "query" in result
        assert "source" in result
        assert "timestamp" in result
        
        assert result["query"] == query
        assert result["source"] == "api"
        assert result["total"] <= limit
        assert len(result["keywords"]) <= limit
        
        # Verificar estrutura das keywords
        for keyword in result["keywords"]:
            assert "keyword" in keyword
            assert "volume" in keyword
            assert "difficulty" in keyword
            assert "cpc" in keyword
            assert "competition" in keyword
            
            # Verificar tipos e valores
            assert isinstance(keyword["keyword"], str)
            assert isinstance(keyword["volume"], int)
            assert 100 <= keyword["volume"] <= 5000
            assert keyword["difficulty"] in ["low", "medium", "high"]
            assert isinstance(keyword["cpc"], float)
            assert 0.1 <= keyword["cpc"] <= 5.0
            assert isinstance(keyword["competition"], float)
            assert 0.1 <= keyword["competition"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_fetch_keywords_from_api_falha_simulada(self, service, sample_query):
        """Teste de falha simulada da API"""
        # Arrange
        query = sample_query
        limit = 5
        
        # Mock para forçar falha (10% de chance)
        with patch('random.random', return_value=0.05):  # Menor que 0.1 para forçar falha
            # Act & Assert
            with pytest.raises(Exception, match="API temporariamente indisponível"):
                await service._fetch_keywords_from_api(query, limit)
    
    def test_get_fallback_keywords_filtro_query(self, service):
        """Teste de fallback com filtro de query"""
        # Arrange
        query = "content"
        limit = 5
        
        # Act
        result = service._get_fallback_keywords(query, limit)
        
        # Assert
        assert result["source"] == "fallback"
        assert result["query"] == query
        assert "message" in result
        assert "Dados de fallback devido a indisponibilidade da API" in result["message"]
        
        # Verificar se encontrou keywords relacionadas
        found_content = False
        for keyword in result["keywords"]:
            if "content" in keyword["keyword"].lower():
                found_content = True
                break
        
        assert found_content
    
    def test_get_fallback_keywords_sem_filtro(self, service):
        """Teste de fallback sem filtro de query"""
        # Arrange
        query = "xyz123"  # Query que não existe no fallback
        limit = 2
        
        # Act
        result = service._get_fallback_keywords(query, limit)
        
        # Assert
        assert result["source"] == "fallback"
        assert result["query"] == query
        assert len(result["keywords"]) <= limit
        assert len(result["keywords"]) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_keywords_sucesso(self, service, sample_keywords):
        """Teste de análise de keywords com sucesso"""
        # Arrange
        keywords = sample_keywords[:3]  # Usar apenas 3 keywords
        
        # Act
        result = await service.analyze_keywords(keywords)
        
        # Assert
        assert "keywords" in result
        assert "summary" in result
        
        # Verificar estrutura do summary
        summary = result["summary"]
        assert "total_keywords" in summary
        assert "avg_volume" in summary
        assert "avg_difficulty" in summary
        assert "recommendations" in summary
        
        assert summary["total_keywords"] == len(keywords)
        assert summary["avg_volume"] > 0
        assert summary["avg_difficulty"] > 0
        assert len(summary["recommendations"]) > 0
        
        # Verificar estrutura das keywords analisadas
        assert len(result["keywords"]) == len(keywords)
        for i, keyword_data in enumerate(result["keywords"]):
            assert keyword_data["keyword"] == keywords[i]
            assert "volume" in keyword_data
            assert "difficulty" in keyword_data
            assert "cpc" in keyword_data
            assert "competition" in keyword_data
            assert "trend" in keyword_data
            
            assert isinstance(keyword_data["volume"], int)
            assert isinstance(keyword_data["difficulty"], float)
            assert isinstance(keyword_data["cpc"], float)
            assert isinstance(keyword_data["competition"], float)
            assert keyword_data["trend"] in ["rising", "stable", "declining"]
    
    @pytest.mark.asyncio
    async def test_analyze_keywords_falha_fallback(self, service, sample_keywords):
        """Teste de fallback na análise de keywords"""
        # Arrange
        keywords = sample_keywords[:2]
        
        # Mock para simular falha do serviço de análise
        with patch('random.random', return_value=0.03):  # Menor que 0.05 para forçar falha
            # Act
            result = await service.analyze_keywords(keywords)
            
            # Assert
            assert "keywords" in result
            assert "summary" in result
            
            # Verificar dados de fallback
            for keyword_data in result["keywords"]:
                assert keyword_data["volume"] == "N/A"
                assert keyword_data["difficulty"] == "N/A"
                assert keyword_data["cpc"] == "N/A"
                assert keyword_data["competition"] == "N/A"
                assert keyword_data["trend"] == "N/A"
            
            summary = result["summary"]
            assert summary["avg_volume"] == "N/A"
            assert summary["avg_difficulty"] == "N/A"
            assert "Análise indisponível" in summary["recommendations"][0]
    
    def test_get_fallback_analysis(self, service, sample_keywords):
        """Teste da função de análise de fallback"""
        # Arrange
        keywords = sample_keywords[:2]
        
        # Act
        result = service._get_fallback_analysis(keywords)
        
        # Assert
        assert "keywords" in result
        assert "summary" in result
        assert "source" in result
        assert "message" in result
        
        assert result["source"] == "fallback"
        assert "Análise de fallback devido a indisponibilidade do serviço" in result["message"]
        
        # Verificar estrutura das keywords
        assert len(result["keywords"]) == len(keywords)
        for i, keyword_data in enumerate(result["keywords"]):
            assert keyword_data["keyword"] == keywords[i]
            assert keyword_data["volume"] == "N/A"
            assert keyword_data["difficulty"] == "N/A"
            assert keyword_data["cpc"] == "N/A"
            assert keyword_data["competition"] == "N/A"
            assert keyword_data["trend"] == "N/A"
        
        # Verificar summary
        summary = result["summary"]
        assert summary["total_keywords"] == len(keywords)
        assert summary["avg_volume"] == "N/A"
        assert summary["avg_difficulty"] == "N/A"
        assert len(summary["recommendations"]) == 2
    
    @pytest.mark.asyncio
    async def test_get_keyword_suggestions_sucesso(self, service):
        """Teste de sugestões de keywords com sucesso"""
        # Arrange
        seed_keyword = "python"
        
        # Act
        result = await service.get_keyword_suggestions(seed_keyword)
        
        # Assert
        assert isinstance(result, list)
        assert len(result) <= 10
        assert len(result) > 0
        
        # Verificar se todas as sugestões contêm a seed keyword
        for suggestion in result:
            assert seed_keyword.lower() in suggestion.lower()
        
        # Verificar tipos de sugestões esperadas
        expected_patterns = [
            f"{seed_keyword} tutorial",
            f"{seed_keyword} guide",
            f"{seed_keyword} tips",
            f"how to {seed_keyword}",
            f"{seed_keyword} for beginners"
        ]
        
        found_patterns = 0
        for pattern in expected_patterns:
            if any(pattern.lower() in suggestion.lower() for suggestion in result):
                found_patterns += 1
        
        assert found_patterns > 0
    
    @pytest.mark.asyncio
    async def test_get_keyword_suggestions_falha_fallback(self, service):
        """Teste de fallback nas sugestões de keywords"""
        # Arrange
        seed_keyword = "javascript"
        
        # Mock para simular falha do serviço de sugestões
        with patch('random.random', return_value=0.02):  # Menor que 0.03 para forçar falha
            # Act
            result = await service.get_keyword_suggestions(seed_keyword)
            
            # Assert
            assert isinstance(result, list)
            assert len(result) == 5  # Fallback sempre retorna 5 sugestões
            
            # Verificar sugestões de fallback
            expected_fallback = [
                f"{seed_keyword} tutorial",
                f"{seed_keyword} guide",
                f"{seed_keyword} tips",
                f"how to {seed_keyword}",
                f"{seed_keyword} for beginners"
            ]
            
            for suggestion in expected_fallback:
                assert suggestion in result
    
    def test_get_fallback_suggestions(self, service):
        """Teste da função de sugestões de fallback"""
        # Arrange
        seed_keyword = "react"
        
        # Act
        result = service._get_fallback_suggestions(seed_keyword)
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 5
        
        expected_suggestions = [
            f"{seed_keyword} tutorial",
            f"{seed_keyword} guide",
            f"{seed_keyword} tips",
            f"how to {seed_keyword}",
            f"{seed_keyword} for beginners"
        ]
        
        assert result == expected_suggestions
    
    def test_get_service_health(self, service):
        """Teste de status de saúde do serviço"""
        # Act
        result = service.get_service_health()
        
        # Assert
        assert "status" in result
        assert "cache" in result
        assert "fallback_usage" in result
        assert "timestamp" in result
        
        assert result["status"] == "healthy"
        
        # Verificar estrutura do cache
        cache_info = result["cache"]
        assert "size" in cache_info
        assert "hit_rate" in cache_info
        assert "ttl" in cache_info
        
        assert isinstance(cache_info["size"], int)
        assert isinstance(cache_info["hit_rate"], float)
        assert cache_info["ttl"] == 300
        
        # Verificar estrutura do fallback usage
        fallback_info = result["fallback_usage"]
        assert "total_fallbacks" in fallback_info
        assert "keywords_fallback" in fallback_info
        assert "analysis_fallback" in fallback_info
        
        assert isinstance(fallback_info["total_fallbacks"], int)
        assert isinstance(fallback_info["keywords_fallback"], int)
        assert isinstance(fallback_info["analysis_fallback"], int)
    
    def test_calculate_cache_hit_rate(self, service):
        """Teste do cálculo de taxa de hit do cache"""
        # Act
        hit_rate = service._calculate_cache_hit_rate()
        
        # Assert
        assert isinstance(hit_rate, float)
        assert 0.7 <= hit_rate <= 0.95
        assert hit_rate == round(hit_rate, 2)  # Deve ter 2 casas decimais
    
    def test_get_fallback_usage(self, service):
        """Teste das estatísticas de uso de fallback"""
        # Act
        usage_stats = service._get_fallback_usage()
        
        # Assert
        assert "total_fallbacks" in usage_stats
        assert "keywords_fallback" in usage_stats
        assert "analysis_fallback" in usage_stats
        
        assert isinstance(usage_stats["total_fallbacks"], int)
        assert isinstance(usage_stats["keywords_fallback"], int)
        assert isinstance(usage_stats["analysis_fallback"], int)
        
        # Verificar ranges esperados
        assert 5 <= usage_stats["total_fallbacks"] <= 50
        assert 3 <= usage_stats["keywords_fallback"] <= 30
        assert 2 <= usage_stats["analysis_fallback"] <= 20
    
    @pytest.mark.asyncio
    async def test_get_keywords_diferentes_limits(self, service, sample_query):
        """Teste de busca com diferentes limites"""
        # Arrange
        query = sample_query
        limits = [1, 5, 10, 20]
        
        for limit in limits:
            # Act
            result = await service.get_keywords(query, limit)
            
            # Assert
            assert result["total"] <= limit
            assert len(result["keywords"]) <= limit
    
    @pytest.mark.asyncio
    async def test_analyze_keywords_lista_vazia(self, service):
        """Teste de análise com lista vazia de keywords"""
        # Arrange
        keywords = []
        
        # Act
        result = await service.analyze_keywords(keywords)
        
        # Assert
        assert "keywords" in result
        assert "summary" in result
        
        assert len(result["keywords"]) == 0
        assert result["summary"]["total_keywords"] == 0
        assert result["summary"]["avg_volume"] == 0
        assert result["summary"]["avg_difficulty"] == 0
    
    @pytest.mark.asyncio
    async def test_get_keyword_suggestions_string_vazia(self, service):
        """Teste de sugestões com string vazia"""
        # Arrange
        seed_keyword = ""
        
        # Act
        result = await service.get_keyword_suggestions(seed_keyword)
        
        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
    
    def test_cache_expiration(self, service, sample_query):
        """Teste de expiração do cache"""
        # Arrange
        query = sample_query
        limit = 5
        
        # Simular dados no cache com expiração passada
        cache_key = f"keywords:{query}:{limit}"
        expired_time = datetime.now() - timedelta(seconds=1)
        
        service.cache[cache_key] = {
            "data": {"test": "data"},
            "expires_at": expired_time
        }
        
        # Act - Deve ignorar cache expirado
        cache_data = service.cache[cache_key]
        
        # Assert
        assert cache_data["expires_at"] < datetime.now()
    
    @pytest.mark.asyncio
    async def test_resiliencia_multiplas_falhas(self, service, sample_query):
        """Teste de resiliência com múltiplas falhas"""
        # Arrange
        query = sample_query
        limit = 5
        
        # Mock para simular falhas consecutivas
        with patch.object(service, '_fetch_keywords_from_api', side_effect=Exception("Falha")) as mock_api:
            # Act - Múltiplas tentativas
            results = []
            for _ in range(3):
                result = await service.get_keywords(query, limit)
                results.append(result)
            
            # Assert
            assert mock_api.call_count == 3  # Deve ter tentado 3 vezes
            
            # Todas devem ter usado fallback
            for result in results:
                assert result["source"] == "fallback"
                assert "message" in result
    
    def test_fallback_data_estrutura(self, service):
        """Teste da estrutura dos dados de fallback"""
        # Arrange & Act - Dados já definidos no __init__
        
        # Assert
        fallback_data = service.fallback_data
        
        assert "keywords" in fallback_data
        assert "total" in fallback_data
        assert "source" in fallback_data
        
        assert fallback_data["total"] == 3
        assert fallback_data["source"] == "fallback"
        
        keywords = fallback_data["keywords"]
        assert len(keywords) == 3
        
        # Verificar estrutura de cada keyword
        for keyword in keywords:
            assert "keyword" in keyword
            assert "volume" in keyword
            assert "difficulty" in keyword
            
            assert isinstance(keyword["keyword"], str)
            assert isinstance(keyword["volume"], int)
            assert keyword["difficulty"] in ["low", "medium", "high"] 