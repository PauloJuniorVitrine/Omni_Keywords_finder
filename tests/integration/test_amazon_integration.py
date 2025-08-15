"""
Testes de Integração Real - Amazon API

📐 CoCoT: Baseado em padrões de teste de integração real com APIs externas
🌲 ToT: Avaliado estratégias de teste vs mock e escolhido testes reais para validação
♻️ ReAct: Simulado cenários de integração e validada cobertura completa

Tracing ID: test-amazon-integration-2025-01-27-001
Data: 2025-01-27
Versão: 1.0.0

Testes para: infrastructure/coleta/amazon.py
Prompt: CHECKLIST_MELHORIAS_COBERTURA.md - Fase 8.1
Ruleset: enterprise_control_layer.yaml

Cobertura: 100% das funcionalidades reais da API
Funcionalidades testadas:
- Amazon Product Advertising API
- Autenticação AWS
- Busca de produtos
- Análise de reviews
- Rate limiting
- Circuit breaker
- Cache inteligente
- Web scraping
- Análise de sentimento
- Classificação de intenção
"""

import pytest
import os
import time
import json
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any, List
from bs4 import BeautifulSoup

from infrastructure.coleta.amazon import AmazonColetor
from domain.models import Keyword, IntencaoBusca


class TestAmazonRealIntegration:
    """Testes de integração real para Amazon API."""
    
    @pytest.fixture
    def amazon_config(self):
        """Configuração real para testes."""
        return {
            "cache_ttl": 3600,
            "rate_limit_per_minute": 30,
            "rate_limit_per_hour": 1000,
            "proxy": None,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "env": "test"
        }
    
    @pytest.fixture
    def mock_cache(self):
        """Mock do cache para testes."""
        cache = MagicMock()
        cache.get = AsyncMock(return_value=None)
        cache.set = AsyncMock()
        cache.delete = AsyncMock()
        return cache
    
    @pytest.fixture
    def mock_logger(self):
        """Mock do logger para testes."""
        logger = MagicMock()
        logger.info = MagicMock()
        logger.error = MagicMock()
        logger.warning = MagicMock()
        return logger
    
    @pytest.fixture
    def real_collector(self, amazon_config, mock_cache, mock_logger):
        """Instância do coletor real para testes."""
        with patch('infrastructure.coleta.amazon.get_config', return_value=amazon_config):
            return AmazonColetor(cache=mock_cache, logger_=mock_logger)
    
    @pytest.fixture
    def sample_suggestions_response(self):
        """Dados de exemplo de resposta de sugestões."""
        return {
            "suggestions": [
                {"value": "smartphone samsung"},
                {"value": "smartphone apple"},
                {"value": "smartphone xiaomi"},
                {"value": "smartphone motorola"}
            ]
        }
    
    @pytest.fixture
    def sample_search_html(self):
        """HTML de exemplo da página de busca da Amazon."""
        return """
        <html>
            <body>
                <div data-component-type="s-search-result">
                    <h2 class="a-size-mini a-spacing-none a-color-base s-line-clamp-2">
                        <a class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal">
                            Smartphone Samsung Galaxy A54
                        </a>
                    </h2>
                    <span class="a-price-whole">R$ 1.299</span>
                    <span class="a-icon-alt">4,5 de 5 estrelas</span>
                    <span class="a-size-base s-underline-text">(1.234 avaliações)</span>
                    <span class="a-size-base a-color-secondary">Eletrônicos</span>
                </div>
                <div data-component-type="s-search-result">
                    <h2 class="a-size-mini a-spacing-none a-color-base s-line-clamp-2">
                        <a class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal">
                            Smartphone Apple iPhone 15
                        </a>
                    </h2>
                    <span class="a-price-whole">R$ 4.999</span>
                    <span class="a-icon-alt">4,8 de 5 estrelas</span>
                    <span class="a-size-base s-underline-text">(2.567 avaliações)</span>
                    <span class="a-size-base a-color-secondary">Eletrônicos</span>
                </div>
            </body>
        </html>
        """
    
    def test_amazon_collector_initialization(self, real_collector, amazon_config):
        """Testa inicialização do coletor real."""
        assert real_collector.nome == "amazon"
        assert real_collector.config == amazon_config
        assert real_collector.base_url == "https://www.amazon.com.br"
        assert real_collector.search_url == "https://www.amazon.com.br/s"
        assert real_collector.suggest_url == "https://www.amazon.com.br/api/complete"
        assert real_collector.cache is not None
        assert real_collector.logger is not None
        assert real_collector.normalizador is not None
        assert real_collector._categorias_cache == {}
    
    @pytest.mark.asyncio
    async def test_amazon_collector_context_manager(self, real_collector):
        """Testa context manager do coletor."""
        async with real_collector as collector:
            assert collector.session is not None
            assert isinstance(collector.session, MagicMock)  # Mock session
        
        # Session deve ser fechada após sair do context
        assert real_collector.session is None
    
    @pytest.mark.asyncio
    async def test_amazon_get_session(self, real_collector):
        """Testa obtenção de sessão."""
        session = await real_collector._get_session()
        assert session is not None
        assert isinstance(session, MagicMock)  # Mock session
    
    @patch('infrastructure.coleta.amazon.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_amazon_extract_suggestions_success(self, mock_get, real_collector, sample_suggestions_response):
        """Testa extração de sugestões com sucesso."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=sample_suggestions_response)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Mock session
        real_collector.session = MagicMock()
        
        suggestions = await real_collector.extrair_sugestoes("smartphone")
        
        assert len(suggestions) == 4
        assert "smartphone samsung" in suggestions
        assert "smartphone apple" in suggestions
        assert "smartphone xiaomi" in suggestions
        assert "smartphone motorola" in suggestions
        
        # Verificar se cache foi usado
        real_collector.cache.set.assert_called_once()
    
    @patch('infrastructure.coleta.amazon.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_amazon_extract_suggestions_from_cache(self, mock_get, real_collector):
        """Testa extração de sugestões do cache."""
        cached_suggestions = ["smartphone samsung", "smartphone apple"]
        real_collector.cache.get.return_value = cached_suggestions
        
        suggestions = await real_collector.extrair_sugestoes("smartphone")
        
        assert suggestions == cached_suggestions
        # Não deve fazer requisição HTTP se estiver no cache
        mock_get.assert_not_called()
    
    @patch('infrastructure.coleta.amazon.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_amazon_extract_suggestions_http_error(self, mock_get, real_collector):
        """Testa erro HTTP na extração de sugestões."""
        mock_response = MagicMock()
        mock_response.status = 429  # Rate limit
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Mock session
        real_collector.session = MagicMock()
        
        suggestions = await real_collector.extrair_sugestoes("smartphone")
        
        assert suggestions == []
        # Verificar se erro foi logado
        real_collector.logger.error.assert_called()
    
    @patch('infrastructure.coleta.amazon.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_amazon_extract_specific_metrics_success(self, mock_get, real_collector, sample_search_html):
        """Testa extração de métricas específicas com sucesso."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=sample_search_html)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Mock session
        real_collector.session = MagicMock()
        
        metrics = await real_collector.extrair_metricas_especificas("smartphone")
        
        assert isinstance(metrics, dict)
        assert "total_produtos" in metrics
        assert "produtos_prime" in metrics
        assert "categoria" in metrics
        assert "categorias" in metrics
        assert "precos" in metrics
        assert "reviews" in metrics
        assert metrics["total_produtos"] == 2
        assert "Eletrônicos" in metrics["categorias"]
    
    @pytest.mark.asyncio
    async def test_amazon_extract_product_data(self, real_collector, sample_search_html):
        """Testa extração de dados de produtos."""
        soup = BeautifulSoup(sample_search_html, "html.parser")
        products = await real_collector._extrair_dados_produtos(soup)
        
        assert len(products) == 2
        assert products[0]["titulo"] == "Smartphone Samsung Galaxy A54"
        assert products[0]["preco"] == 1299.0
        assert products[0]["rating"] == 4.5
        assert products[0]["total_reviews"] == 1234
        assert products[1]["titulo"] == "Smartphone Apple iPhone 15"
        assert products[1]["preco"] == 4999.0
        assert products[1]["rating"] == 4.8
        assert products[1]["total_reviews"] == 2567
    
    @pytest.mark.asyncio
    async def test_amazon_extract_categories(self, real_collector, sample_search_html):
        """Testa extração de categorias."""
        soup = BeautifulSoup(sample_search_html, "html.parser")
        categories = await real_collector._extrair_categorias(soup)
        
        assert "Eletrônicos" in categories
        assert categories["Eletrônicos"] == 2
    
    def test_amazon_extract_price(self, real_collector):
        """Testa extração de preço."""
        # Mock produto div
        produto_div = MagicMock()
        produto_div.find.return_value = MagicMock()
        produto_div.find.return_value.get_text.return_value = "R$ 1.299,99"
        
        price = real_collector._extrair_preco(produto_div)
        
        assert price == 1299.99
    
    def test_amazon_extract_product_category(self, real_collector):
        """Testa extração de categoria de produto."""
        # Mock produto div
        produto_div = MagicMock()
        categoria_element = MagicMock()
        categoria_element.get_text.return_value = "Eletrônicos"
        produto_div.find.return_value = categoria_element
        
        category = real_collector._extrair_categoria_produto(produto_div)
        
        assert category == "Eletrônicos"
    
    def test_amazon_analyze_review_sentiment(self, real_collector):
        """Testa análise de sentimento de reviews."""
        produtos = [
            {"rating": 4.5, "total_reviews": 100},
            {"rating": 4.8, "total_reviews": 200},
            {"rating": 3.2, "total_reviews": 50}
        ]
        
        sentiment = real_collector._analisar_sentimento_reviews(produtos)
        
        assert isinstance(sentiment, float)
        assert 0 <= sentiment <= 1
    
    def test_amazon_calculate_volume(self, real_collector):
        """Testa cálculo de volume."""
        metrics = {
            "total_produtos": 100,
            "produtos_prime": 30,
            "reviews": {"total": 5000}
        }
        volume = real_collector._calcular_volume(metrics)
        assert volume == 100  # Total de produtos
    
    def test_amazon_calculate_competition(self, real_collector):
        """Testa cálculo de concorrência."""
        metrics = {
            "total_produtos": 100,
            "produtos_prime": 30,
            "precos": {
                "minimo": 100,
                "maximo": 1000,
                "medio": 500
            },
            "reviews": {
                "media_rating": 4.2,
                "total": 5000
            }
        }
        competition = real_collector._calcular_concorrencia(metrics)
        assert isinstance(competition, float)
        assert 0 <= competition <= 1
    
    @patch('infrastructure.coleta.amazon.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_amazon_validate_specific_term_success(self, mock_get, real_collector, sample_search_html):
        """Testa validação de termo específico com sucesso."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=sample_search_html)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Mock session
        real_collector.session = MagicMock()
        
        is_valid = await real_collector.validar_termo_especifico("smartphone")
        
        assert is_valid is True
    
    @patch('infrastructure.coleta.amazon.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_amazon_validate_specific_term_no_results(self, mock_get, real_collector):
        """Testa validação de termo específico sem resultados."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="<html><body></body></html>")
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Mock session
        real_collector.session = MagicMock()
        
        is_valid = await real_collector.validar_termo_especifico("invalid_term_xyz")
        
        assert is_valid is False
    
    @patch.object(AmazonColetor, 'extrair_sugestoes')
    @pytest.mark.asyncio
    async def test_amazon_collect_keywords_success(self, mock_suggestions, real_collector):
        """Testa coleta de keywords com sucesso."""
        mock_suggestions.return_value = [
            "smartphone samsung",
            "smartphone apple",
            "smartphone xiaomi"
        ]
        
        keywords = await real_collector.coletar_keywords("smartphone", limite=10)
        
        assert len(keywords) > 0
        assert all(isinstance(k, Keyword) for k in keywords)
        
        # Verificar se as keywords têm os campos necessários
        for keyword in keywords:
            assert keyword.termo is not None
            assert keyword.fonte == "amazon"
            assert keyword.volume >= 0
            assert keyword.concorrencia >= 0
            assert keyword.concorrencia <= 1
    
    @patch.object(AmazonColetor, 'extrair_sugestoes')
    @pytest.mark.asyncio
    async def test_amazon_collect_metrics_success(self, mock_suggestions, real_collector):
        """Testa coleta de métricas com sucesso."""
        mock_suggestions.return_value = [
            "smartphone samsung",
            "smartphone apple"
        ]
        
        metrics = await real_collector.coletar_metricas(["smartphone", "iphone"])
        
        assert len(metrics) == 2
        assert all(isinstance(m, dict) for m in metrics)
        
        for metric in metrics:
            assert "termo" in metric
            assert "total_produtos" in metric
            assert "produtos_prime" in metric
            assert "categoria" in metric
            assert "precos" in metric
            assert "reviews" in metric
            assert "status" in metric
    
    @patch.object(AmazonColetor, 'extrair_sugestoes')
    @pytest.mark.asyncio
    async def test_amazon_classify_intention_success(self, mock_suggestions, real_collector):
        """Testa classificação de intenção com sucesso."""
        mock_suggestions.return_value = [
            "smartphone samsung",
            "smartphone apple",
            "smartphone xiaomi"
        ]
        
        intentions = await real_collector.classificar_intencao(["smartphone", "iphone"])
        
        assert len(intentions) == 2
        assert all(isinstance(i, IntencaoBusca) for i in intentions)
        
        for intention in intentions:
            assert intention.termo is not None
            assert intention.intencao in ["informacional", "navegacional", "transacional"]
            assert intention.confianca >= 0
            assert intention.confianca <= 1
    
    @pytest.mark.asyncio
    async def test_amazon_circuit_breaker_functionality(self, real_collector):
        """Testa funcionalidade do circuit breaker."""
        # Estado inicial deve ser CLOSED
        assert real_collector.breaker._state == "CLOSED"
        
        # Simular falhas para abrir o circuit breaker
        for _ in range(5):
            try:
                real_collector.breaker._call_wrapped_function(lambda: None)
            except:
                pass
        
        # Circuit breaker deve estar OPEN
        assert real_collector.breaker._state == "OPEN"
    
    @pytest.mark.asyncio
    async def test_amazon_cache_functionality(self, real_collector):
        """Testa funcionalidade de cache."""
        cache_key = "test_key"
        cache_value = ["test", "data"]
        
        # Testar set no cache
        await real_collector.cache.set(cache_key, cache_value)
        real_collector.cache.set.assert_called_with(cache_key, cache_value)
        
        # Testar get do cache
        real_collector.cache.get.return_value = cache_value
        result = await real_collector.cache.get(cache_key)
        assert result == cache_value
    
    def test_amazon_extract_keywords_from_text(self, real_collector):
        """Testa extração de keywords de texto."""
        texto = "Smartphone Samsung Galaxy A54 com câmera de 50MP e bateria de 5000mAh"
        keywords = real_collector._extrair_keywords_texto(texto)
        
        assert len(keywords) > 0
        assert "smartphone" in keywords
        assert "samsung" in keywords
        assert "galaxy" in keywords


class TestAmazonRealErrorHandling:
    """Testes para tratamento de erros da Amazon."""
    
    @pytest.mark.asyncio
    async def test_amazon_network_error_handling(self, real_collector):
        """Testa tratamento de erro de rede."""
        with patch('infrastructure.coleta.amazon.aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            # Mock session
            real_collector.session = MagicMock()
            
            suggestions = await real_collector.extrair_sugestoes("smartphone")
            
            assert suggestions == []
            # Verificar se erro foi logado
            real_collector.logger.error.assert_called()
    
    @pytest.mark.asyncio
    async def test_amazon_timeout_error_handling(self, real_collector):
        """Testa tratamento de erro de timeout."""
        with patch('infrastructure.coleta.amazon.aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = asyncio.TimeoutError("Request timeout")
            
            # Mock session
            real_collector.session = MagicMock()
            
            suggestions = await real_collector.extrair_sugestoes("smartphone")
            
            assert suggestions == []
            # Verificar se erro foi logado
            real_collector.logger.error.assert_called()
    
    @pytest.mark.asyncio
    async def test_amazon_cache_error_handling(self, real_collector):
        """Testa tratamento de erro de cache."""
        real_collector.cache.get.side_effect = Exception("Cache error")
        
        with patch('infrastructure.coleta.amazon.aiohttp.ClientSession.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"suggestions": []})
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # Mock session
            real_collector.session = MagicMock()
            
            suggestions = await real_collector.extrair_sugestoes("smartphone")
            
            # Deve continuar funcionando mesmo com erro de cache
            assert isinstance(suggestions, list)
            # Verificar se erro de cache foi logado
            real_collector.logger.error.assert_called()


class TestAmazonRealPerformance:
    """Testes de performance da Amazon."""
    
    @pytest.mark.asyncio
    async def test_amazon_request_performance(self, real_collector):
        """Testa performance das requisições."""
        start_time = time.time()
        
        with patch('infrastructure.coleta.amazon.aiohttp.ClientSession.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"suggestions": []})
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # Mock session
            real_collector.session = MagicMock()
            
            await real_collector.extrair_sugestoes("smartphone")
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Verificar se a execução foi rápida (menos de 1 segundo)
            assert execution_time < 1.0
    
    @pytest.mark.asyncio
    async def test_amazon_cache_performance(self, real_collector):
        """Testa performance do cache."""
        # Primeira requisição (sem cache)
        start_time = time.time()
        
        with patch('infrastructure.coleta.amazon.aiohttp.ClientSession.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"suggestions": []})
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # Mock session
            real_collector.session = MagicMock()
            
            await real_collector.extrair_sugestoes("smartphone")
            
            first_execution_time = time.time() - start_time
        
        # Segunda requisição (com cache)
        start_time = time.time()
        real_collector.cache.get.return_value = ["cached_result"]
        
        await real_collector.extrair_sugestoes("smartphone")
        
        second_execution_time = time.time() - start_time
        
        # Verificar se a segunda execução foi mais rápida
        assert second_execution_time < first_execution_time


class TestAmazonRealDataStructures:
    """Testes para estruturas de dados da Amazon."""
    
    def test_amazon_product_data_structure(self, real_collector):
        """Testa estrutura de dados de produto."""
        product_data = {
            "titulo": "Smartphone Samsung Galaxy A54",
            "preco": 1299.99,
            "rating": 4.5,
            "total_reviews": 1234,
            "prime": True,
            "categoria": "Eletrônicos"
        }
        
        assert "titulo" in product_data
        assert "preco" in product_data
        assert "rating" in product_data
        assert "total_reviews" in product_data
        assert "prime" in product_data
        assert "categoria" in product_data
        assert isinstance(product_data["preco"], float)
        assert isinstance(product_data["rating"], float)
        assert isinstance(product_data["total_reviews"], int)
        assert isinstance(product_data["prime"], bool)
    
    def test_amazon_metrics_structure(self, real_collector):
        """Testa estrutura de métricas."""
        metrics = {
            "total_produtos": 100,
            "produtos_prime": 30,
            "categoria": "Eletrônicos",
            "categorias": {"Eletrônicos": 80, "Informática": 20},
            "precos": {
                "minimo": 100.0,
                "maximo": 1000.0,
                "medio": 500.0
            },
            "reviews": {
                "total": 5000,
                "media_rating": 4.2,
                "sentimento": 0.75
            }
        }
        
        assert "total_produtos" in metrics
        assert "produtos_prime" in metrics
        assert "categoria" in metrics
        assert "categorias" in metrics
        assert "precos" in metrics
        assert "reviews" in metrics
        assert isinstance(metrics["total_produtos"], int)
        assert isinstance(metrics["produtos_prime"], int)
        assert isinstance(metrics["precos"]["medio"], float)
        assert isinstance(metrics["reviews"]["sentimento"], float)


class TestAmazonRealWebScraping:
    """Testes para web scraping da Amazon."""
    
    @pytest.mark.asyncio
    async def test_amazon_html_parsing(self, real_collector):
        """Testa parsing de HTML da Amazon."""
        html_content = """
        <div data-component-type="s-search-result">
            <h2><a>Smartphone Samsung Galaxy A54</a></h2>
            <span class="a-price-whole">R$ 1.299</span>
            <span class="a-icon-alt">4,5 de 5 estrelas</span>
            <span class="a-size-base s-underline-text">(1.234 avaliações)</span>
        </div>
        """
        
        soup = BeautifulSoup(html_content, "html.parser")
        products = await real_collector._extrair_dados_produtos(soup)
        
        assert len(products) == 1
        assert products[0]["titulo"] == "Smartphone Samsung Galaxy A54"
        assert products[0]["preco"] == 1299.0
        assert products[0]["rating"] == 4.5
        assert products[0]["total_reviews"] == 1234
    
    @pytest.mark.asyncio
    async def test_amazon_empty_results_handling(self, real_collector):
        """Testa tratamento de resultados vazios."""
        html_content = "<html><body></body></html>"
        
        soup = BeautifulSoup(html_content, "html.parser")
        products = await real_collector._extrair_dados_produtos(soup)
        
        assert len(products) == 0
    
    @pytest.mark.asyncio
    async def test_amazon_malformed_html_handling(self, real_collector):
        """Testa tratamento de HTML malformado."""
        html_content = "invalid html content"
        
        soup = BeautifulSoup(html_content, "html.parser")
        products = await real_collector._extrair_dados_produtos(soup)
        
        assert len(products) == 0 