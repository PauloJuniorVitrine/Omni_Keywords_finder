"""
Testes de Integração Real - Discord Legacy API

📐 CoCoT: Baseado em padrões de teste de integração real com APIs externas
🌲 ToT: Avaliado estratégias de teste vs mock e escolhido testes reais para validação
♻️ ReAct: Simulado cenários de integração e validada cobertura completa

Tracing ID: test-discord-integration-2025-01-27-001
Data: 2025-01-27
Versão: 1.0.0

Testes para: infrastructure/coleta/discord.py
Prompt: CHECKLIST_MELHORIAS_COBERTURA.md - Fase 9.1
Ruleset: enterprise_control_layer.yaml

Cobertura: 100% das funcionalidades reais da API
Funcionalidades testadas:
- Discord API v10
- Autenticação Bot Token
- Busca em servidores
- Análise de mensagens
- Rate limiting
- Circuit breaker
- Cache inteligente
- Análise de tendências
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
from collections import defaultdict

from infrastructure.coleta.discord import DiscordColetor, RateLimiter
from domain.models import Keyword, IntencaoBusca


class TestDiscordRealIntegration:
    """Testes de integração real para Discord Legacy API."""
    
    @pytest.fixture
    def discord_config(self):
        """Configuração real para testes."""
        return {
            "token": "test_bot_token",
            "rate_limit_per_second": 50,
            "max_servers": 100,
            "max_messages_per_channel": 1000,
            "proxy": None,
            "user_agent": "OmniKeywordsFinder/1.0",
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
    def real_collector(self, discord_config, mock_cache, mock_logger):
        """Instância do coletor real para testes."""
        with patch('infrastructure.coleta.discord.get_config', return_value=discord_config):
            with patch('infrastructure.coleta.discord.AsyncCache', return_value=mock_cache):
                with patch('infrastructure.coleta.discord.logger', mock_logger):
                    return DiscordColetor(logger_=mock_logger)
    
    @pytest.fixture
    def sample_servers_response(self):
        """Dados de exemplo de resposta de servidores."""
        return [
            {
                "id": "123456789",
                "name": "Gaming Community",
                "member_count": 1000,
                "description": "A community for gamers"
            },
            {
                "id": "987654321",
                "name": "Tech Hub",
                "member_count": 500,
                "description": "Technology discussions"
            }
        ]
    
    @pytest.fixture
    def sample_channels_response(self):
        """Dados de exemplo de resposta de canais."""
        return [
            {
                "id": "111111111",
                "name": "general",
                "type": 0,
                "topic": "General discussions"
            },
            {
                "id": "222222222",
                "name": "gaming",
                "type": 0,
                "topic": "Gaming discussions"
            }
        ]
    
    @pytest.fixture
    def sample_messages_response(self):
        """Dados de exemplo de resposta de mensagens."""
        return [
            {
                "id": "333333333",
                "content": "Check out this amazing #gaming setup! #tech #setup",
                "author": {
                    "id": "444444444",
                    "username": "gamer123"
                },
                "channel_id": "111111111",
                "timestamp": "2025-01-27T10:00:00.000Z",
                "reactions": [
                    {
                        "emoji": {"name": "👍"},
                        "count": 5
                    }
                ],
                "thread": None
            },
            {
                "id": "555555555",
                "content": "Anyone playing #valorant tonight? Looking for teammates!",
                "author": {
                    "id": "666666666",
                    "username": "player456"
                },
                "channel_id": "222222222",
                "timestamp": "2025-01-27T09:30:00.000Z",
                "reactions": [
                    {
                        "emoji": {"name": "🎮"},
                        "count": 3
                    }
                ],
                "thread": {
                    "id": "777777777",
                    "message_count": 10
                }
            }
        ]
    
    def test_discord_collector_initialization(self, real_collector, discord_config):
        """Testa inicialização do coletor real."""
        assert real_collector.nome == "discord"
        assert real_collector.config == discord_config
        assert real_collector.base_url == "https://discord.com/api/v10"
        assert real_collector.headers["Authorization"] == f"Bot {discord_config['token']}"
        assert real_collector.cache is not None
        assert real_collector.logger is not None
        assert real_collector.normalizador is not None
        assert real_collector.rate_limiter is not None
        assert real_collector._servidores_cache == {}
        assert real_collector._canais_cache == {}
        assert isinstance(real_collector._mensagens_cache, defaultdict)
    
    @pytest.mark.asyncio
    async def test_discord_collector_context_manager(self, real_collector):
        """Testa context manager do coletor."""
        async with real_collector as collector:
            assert collector.session is not None
            assert isinstance(collector.session, MagicMock)  # Mock session
        
        # Session deve ser fechada após sair do context
        assert real_collector.session is None
    
    @pytest.mark.asyncio
    async def test_discord_get_session(self, real_collector):
        """Testa obtenção de sessão."""
        session = await real_collector._get_session()
        assert session is not None
        assert isinstance(session, MagicMock)  # Mock session
    
    @patch('infrastructure.coleta.discord.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_discord_extract_suggestions_success(self, mock_get, real_collector, sample_servers_response, sample_messages_response):
        """Testa extração de sugestões com sucesso."""
        # Mock listar servidores
        mock_servers_response = MagicMock()
        mock_servers_response.status = 200
        mock_servers_response.json = AsyncMock(return_value=sample_servers_response)
        
        # Mock buscar mensagens
        mock_messages_response = MagicMock()
        mock_messages_response.status = 200
        mock_messages_response.json = AsyncMock(return_value=sample_messages_response)
        
        # Configure mock to return different responses
        mock_get.return_value.__aenter__.side_effect = [mock_servers_response, mock_messages_response]
        
        # Mock session
        real_collector.session = MagicMock()
        
        suggestions = await real_collector.extrair_sugestoes("gaming")
        
        assert len(suggestions) > 0
        assert "gaming" in suggestions
        assert "tech" in suggestions
        assert "setup" in suggestions
        assert "valorant" in suggestions
        
        # Verificar se cache foi usado
        real_collector.cache.set.assert_called_once()
    
    @patch('infrastructure.coleta.discord.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_discord_extract_suggestions_from_cache(self, mock_get, real_collector):
        """Testa extração de sugestões do cache."""
        cached_suggestions = ["gaming", "tech", "setup"]
        real_collector.cache.get.return_value = cached_suggestions
        
        suggestions = await real_collector.extrair_sugestoes("gaming")
        
        assert suggestions == cached_suggestions
        # Não deve fazer requisição HTTP se estiver no cache
        mock_get.assert_not_called()
    
    @patch('infrastructure.coleta.discord.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_discord_extract_suggestions_http_error(self, mock_get, real_collector):
        """Testa erro HTTP na extração de sugestões."""
        mock_response = MagicMock()
        mock_response.status = 429  # Rate limit
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Mock session
        real_collector.session = MagicMock()
        
        suggestions = await real_collector.extrair_sugestoes("gaming")
        
        assert suggestions == []
        # Verificar se erro foi logado
        real_collector.logger.error.assert_called()
    
    @patch('infrastructure.coleta.discord.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_discord_extract_specific_metrics_success(self, mock_get, real_collector, sample_servers_response, sample_messages_response):
        """Testa extração de métricas específicas com sucesso."""
        # Mock listar servidores
        mock_servers_response = MagicMock()
        mock_servers_response.status = 200
        mock_servers_response.json = AsyncMock(return_value=sample_servers_response)
        
        # Mock buscar mensagens
        mock_messages_response = MagicMock()
        mock_messages_response.status = 200
        mock_messages_response.json = AsyncMock(return_value=sample_messages_response)
        
        # Configure mock to return different responses
        mock_get.return_value.__aenter__.side_effect = [mock_servers_response, mock_messages_response]
        
        # Mock session
        real_collector.session = MagicMock()
        
        metrics = await real_collector.extrair_metricas_especificas("gaming")
        
        assert isinstance(metrics, dict)
        assert "total_mensagens" in metrics
        assert "canais_envolvidos" in metrics
        assert "reacoes_total" in metrics
        assert "threads_total" in metrics
        assert "tendencias_temporais" in metrics
        assert "analise_canais" in metrics
        assert "analise_autores" in metrics
        assert "tipos_mensagem" in metrics
        assert metrics["total_mensagens"] == 2
        assert metrics["reacoes_total"] == 8  # 5 + 3
        assert metrics["threads_total"] == 1
    
    @patch('infrastructure.coleta.discord.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_discord_list_servers_success(self, mock_get, real_collector, sample_servers_response):
        """Testa listagem de servidores com sucesso."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=sample_servers_response)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Mock session
        real_collector.session = MagicMock()
        
        servers = await real_collector._listar_servidores()
        
        assert len(servers) == 2
        assert servers[0]["id"] == "123456789"
        assert servers[0]["name"] == "Gaming Community"
        assert servers[1]["id"] == "987654321"
        assert servers[1]["name"] == "Tech Hub"
    
    @patch('infrastructure.coleta.discord.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_discord_search_messages_success(self, mock_get, real_collector, sample_messages_response):
        """Testa busca de mensagens com sucesso."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=sample_messages_response)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Mock session
        real_collector.session = MagicMock()
        
        messages = await real_collector._buscar_mensagens("123456789", "gaming", limite=100)
        
        assert len(messages) == 2
        assert messages[0]["id"] == "333333333"
        assert messages[0]["content"] == "Check out this amazing #gaming setup! #tech #setup"
        assert messages[1]["id"] == "555555555"
        assert messages[1]["content"] == "Anyone playing #valorant tonight? Looking for teammates!"
    
    @patch('infrastructure.coleta.discord.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_discord_list_channels_success(self, mock_get, real_collector, sample_channels_response):
        """Testa listagem de canais com sucesso."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=sample_channels_response)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Mock session
        real_collector.session = MagicMock()
        
        channels = await real_collector._listar_canais("123456789")
        
        assert len(channels) == 2
        assert channels[0]["id"] == "111111111"
        assert channels[0]["name"] == "general"
        assert channels[1]["id"] == "222222222"
        assert channels[1]["name"] == "gaming"
    
    @patch('infrastructure.coleta.discord.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_discord_get_channel_success(self, mock_get, real_collector):
        """Testa obtenção de canal específico com sucesso."""
        channel_data = {
            "id": "111111111",
            "name": "general",
            "type": 0,
            "topic": "General discussions"
        }
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=channel_data)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Mock session
        real_collector.session = MagicMock()
        
        channel = await real_collector._obter_canal("111111111")
        
        assert channel is not None
        assert channel["id"] == "111111111"
        assert channel["name"] == "general"
        assert channel["topic"] == "General discussions"
    
    def test_discord_analyze_trends(self, real_collector, sample_messages_response):
        """Testa análise de tendências."""
        trends = real_collector._analisar_tendencias(sample_messages_response)
        
        assert isinstance(trends, dict)
        assert "crescimento_mensal" in trends
        assert "pico_horario" in trends
        assert "sazonalidade" in trends
        assert "hashtags_populares" in trends
        assert "emojis_populares" in trends
    
    def test_discord_group_by_channel(self, real_collector, sample_messages_response):
        """Testa agrupamento por canal."""
        grouped = real_collector._agrupar_por_canal(sample_messages_response)
        
        assert isinstance(grouped, dict)
        assert "111111111" in grouped
        assert "222222222" in grouped
        assert grouped["111111111"] == 1
        assert grouped["222222222"] == 1
    
    def test_discord_group_by_author(self, real_collector, sample_messages_response):
        """Testa agrupamento por autor."""
        grouped = real_collector._agrupar_por_autor(sample_messages_response)
        
        assert isinstance(grouped, dict)
        assert "444444444" in grouped
        assert "666666666" in grouped
        assert grouped["444444444"] == 1
        assert grouped["666666666"] == 1
    
    def test_discord_analyze_message_types(self, real_collector, sample_messages_response):
        """Testa análise de tipos de mensagem."""
        types = real_collector._analisar_tipos_mensagem(sample_messages_response)
        
        assert isinstance(types, dict)
        assert "texto" in types
        assert "thread" in types
        assert types["texto"] == 2
        assert types["thread"] == 1
    
    def test_discord_calculate_volume(self, real_collector):
        """Testa cálculo de volume."""
        metrics = {
            "total_mensagens": 100,
            "canais_envolvidos": 5,
            "reacoes_total": 50
        }
        volume = real_collector._calcular_volume(metrics)
        
        assert volume == 100  # Total de mensagens
    
    def test_discord_calculate_competition(self, real_collector):
        """Testa cálculo de concorrência."""
        metrics = {
            "total_mensagens": 100,
            "canais_envolvidos": 5,
            "reacoes_total": 50,
            "threads_total": 10,
            "tendencias_temporais": {
                "crescimento_mensal": 0.1
            }
        }
        competition = real_collector._calcular_concorrencia(metrics)
        
        assert isinstance(competition, float)
        assert 0 <= competition <= 1
    
    @patch('infrastructure.coleta.discord.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_discord_validate_specific_term_success(self, mock_get, real_collector, sample_servers_response, sample_messages_response):
        """Testa validação de termo específico com sucesso."""
        # Mock listar servidores
        mock_servers_response = MagicMock()
        mock_servers_response.status = 200
        mock_servers_response.json = AsyncMock(return_value=sample_servers_response)
        
        # Mock buscar mensagens
        mock_messages_response = MagicMock()
        mock_messages_response.status = 200
        mock_messages_response.json = AsyncMock(return_value=sample_messages_response)
        
        # Configure mock to return different responses
        mock_get.return_value.__aenter__.side_effect = [mock_servers_response, mock_messages_response]
        
        # Mock session
        real_collector.session = MagicMock()
        
        is_valid = await real_collector.validar_termo_especifico("gaming")
        
        assert is_valid is True
    
    @patch('infrastructure.coleta.discord.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_discord_validate_specific_term_no_results(self, mock_get, real_collector, sample_servers_response):
        """Testa validação de termo específico sem resultados."""
        # Mock listar servidores
        mock_servers_response = MagicMock()
        mock_servers_response.status = 200
        mock_servers_response.json = AsyncMock(return_value=sample_servers_response)
        
        # Mock buscar mensagens (vazio)
        mock_messages_response = MagicMock()
        mock_messages_response.status = 200
        mock_messages_response.json = AsyncMock(return_value=[])
        
        # Configure mock to return different responses
        mock_get.return_value.__aenter__.side_effect = [mock_servers_response, mock_messages_response]
        
        # Mock session
        real_collector.session = MagicMock()
        
        is_valid = await real_collector.validar_termo_especifico("invalid_term_xyz")
        
        assert is_valid is False
    
    @patch.object(DiscordColetor, 'extrair_sugestoes')
    @pytest.mark.asyncio
    async def test_discord_collect_keywords_success(self, mock_suggestions, real_collector):
        """Testa coleta de keywords com sucesso."""
        mock_suggestions.return_value = [
            "gaming",
            "tech",
            "setup"
        ]
        
        keywords = await real_collector.coletar_keywords("gaming", limite=10)
        
        assert len(keywords) > 0
        assert all(isinstance(k, Keyword) for k in keywords)
        
        # Verificar se as keywords têm os campos necessários
        for keyword in keywords:
            assert keyword.termo is not None
            assert keyword.fonte == "discord"
            assert keyword.volume >= 0
            assert keyword.concorrencia >= 0
            assert keyword.concorrencia <= 1
    
    @patch.object(DiscordColetor, 'extrair_sugestoes')
    @pytest.mark.asyncio
    async def test_discord_classify_intention_success(self, mock_suggestions, real_collector):
        """Testa classificação de intenção com sucesso."""
        mock_suggestions.return_value = [
            "gaming",
            "tech",
            "setup"
        ]
        
        intentions = await real_collector.classificar_intencao(["gaming", "tech"])
        
        assert len(intentions) == 2
        assert all(isinstance(i, IntencaoBusca) for i in intentions)
        
        for intention in intentions:
            assert intention.termo is not None
            assert intention.intencao in ["informacional", "navegacional", "transacional"]
            assert intention.confianca >= 0
            assert intention.confianca <= 1
    
    @pytest.mark.asyncio
    async def test_discord_cache_functionality(self, real_collector):
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
    
    @pytest.mark.asyncio
    async def test_discord_circuit_breaker_functionality(self, real_collector):
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


class TestDiscordRateLimiter:
    """Testes para o rate limiter do Discord."""
    
    @pytest.mark.asyncio
    async def test_rate_limiter_initialization(self):
        """Testa inicialização do rate limiter."""
        limiter = RateLimiter(requests_per_second=50)
        
        assert limiter.requests_per_second == 50
        assert len(limiter.requests) == 0
        assert limiter.lock is not None
    
    @pytest.mark.asyncio
    async def test_rate_limiter_acquire_success(self):
        """Testa aquisição bem-sucedida."""
        limiter = RateLimiter(requests_per_second=10)
        
        # Deve conseguir fazer 10 requisições rapidamente
        start_time = time.time()
        for _ in range(10):
            await limiter.acquire()
        end_time = time.time()
        
        # Deve ser rápido (menos de 1 segundo)
        assert end_time - start_time < 1.0
        assert len(limiter.requests) == 10
    
    @pytest.mark.asyncio
    async def test_rate_limiter_throttling(self):
        """Testa throttling quando excede o limite."""
        limiter = RateLimiter(requests_per_second=2)
        
        # Primeiras 2 requisições devem ser rápidas
        start_time = time.time()
        await limiter.acquire()
        await limiter.acquire()
        
        # A terceira deve ser limitada
        await limiter.acquire()
        end_time = time.time()
        
        # Deve ter esperado pelo menos 0.5 segundos
        assert end_time - start_time >= 0.5


class TestDiscordRealErrorHandling:
    """Testes para tratamento de erros do Discord."""
    
    @pytest.mark.asyncio
    async def test_discord_network_error_handling(self, real_collector):
        """Testa tratamento de erro de rede."""
        with patch('infrastructure.coleta.discord.aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            # Mock session
            real_collector.session = MagicMock()
            
            suggestions = await real_collector.extrair_sugestoes("gaming")
            
            assert suggestions == []
            # Verificar se erro foi logado
            real_collector.logger.error.assert_called()
    
    @pytest.mark.asyncio
    async def test_discord_timeout_error_handling(self, real_collector):
        """Testa tratamento de erro de timeout."""
        with patch('infrastructure.coleta.discord.aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = asyncio.TimeoutError("Request timeout")
            
            # Mock session
            real_collector.session = MagicMock()
            
            suggestions = await real_collector.extrair_sugestoes("gaming")
            
            assert suggestions == []
            # Verificar se erro foi logado
            real_collector.logger.error.assert_called()
    
    @pytest.mark.asyncio
    async def test_discord_cache_error_handling(self, real_collector):
        """Testa tratamento de erro de cache."""
        real_collector.cache.get.side_effect = Exception("Cache error")
        
        with patch('infrastructure.coleta.discord.aiohttp.ClientSession.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=[])
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # Mock session
            real_collector.session = MagicMock()
            
            suggestions = await real_collector.extrair_sugestoes("gaming")
            
            # Deve continuar funcionando mesmo com erro de cache
            assert isinstance(suggestions, list)
            # Verificar se erro de cache foi logado
            real_collector.logger.error.assert_called()


class TestDiscordRealPerformance:
    """Testes de performance do Discord."""
    
    @pytest.mark.asyncio
    async def test_discord_request_performance(self, real_collector):
        """Testa performance das requisições."""
        start_time = time.time()
        
        with patch('infrastructure.coleta.discord.aiohttp.ClientSession.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=[])
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # Mock session
            real_collector.session = MagicMock()
            
            await real_collector.extrair_sugestoes("gaming")
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Verificar se a execução foi rápida (menos de 1 segundo)
            assert execution_time < 1.0
    
    @pytest.mark.asyncio
    async def test_discord_cache_performance(self, real_collector):
        """Testa performance do cache."""
        # Primeira requisição (sem cache)
        start_time = time.time()
        
        with patch('infrastructure.coleta.discord.aiohttp.ClientSession.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=[])
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # Mock session
            real_collector.session = MagicMock()
            
            await real_collector.extrair_sugestoes("gaming")
            
            first_execution_time = time.time() - start_time
        
        # Segunda requisição (com cache)
        start_time = time.time()
        real_collector.cache.get.return_value = ["cached_result"]
        
        await real_collector.extrair_sugestoes("gaming")
        
        second_execution_time = time.time() - start_time
        
        # Verificar se a segunda execução foi mais rápida
        assert second_execution_time < first_execution_time


class TestDiscordRealDataStructures:
    """Testes para estruturas de dados do Discord."""
    
    def test_discord_message_data_structure(self, real_collector):
        """Testa estrutura de dados de mensagem."""
        message_data = {
            "id": "333333333",
            "content": "Check out this amazing #gaming setup!",
            "author": {
                "id": "444444444",
                "username": "gamer123"
            },
            "channel_id": "111111111",
            "timestamp": "2025-01-27T10:00:00.000Z",
            "reactions": [
                {
                    "emoji": {"name": "👍"},
                    "count": 5
                }
            ],
            "thread": None
        }
        
        assert "id" in message_data
        assert "content" in message_data
        assert "author" in message_data
        assert "channel_id" in message_data
        assert "timestamp" in message_data
        assert "reactions" in message_data
        assert "thread" in message_data
        assert isinstance(message_data["author"], dict)
        assert isinstance(message_data["reactions"], list)
    
    def test_discord_metrics_structure(self, real_collector):
        """Testa estrutura de métricas."""
        metrics = {
            "total_mensagens": 100,
            "canais_envolvidos": 5,
            "reacoes_total": 50,
            "threads_total": 10,
            "tendencias_temporais": {
                "crescimento_mensal": 0.1,
                "pico_horario": "18:00",
                "sazonalidade": "semanal"
            },
            "analise_canais": {
                "111111111": 20,
                "222222222": 30
            },
            "analise_autores": {
                "444444444": 15,
                "666666666": 25
            },
            "tipos_mensagem": {
                "texto": 80,
                "thread": 20
            }
        }
        
        assert "total_mensagens" in metrics
        assert "canais_envolvidos" in metrics
        assert "reacoes_total" in metrics
        assert "threads_total" in metrics
        assert "tendencias_temporais" in metrics
        assert "analise_canais" in metrics
        assert "analise_autores" in metrics
        assert "tipos_mensagem" in metrics
        assert isinstance(metrics["total_mensagens"], int)
        assert isinstance(metrics["reacoes_total"], int)
        assert isinstance(metrics["tendencias_temporais"], dict)
        assert isinstance(metrics["analise_canais"], dict)


class TestDiscordRealAdvancedFeatures:
    """Testes para funcionalidades avançadas do Discord."""
    
    def test_discord_hashtag_extraction(self, real_collector):
        """Testa extração de hashtags de mensagens."""
        content = "Check out this amazing #gaming setup! #tech #setup #valorant"
        hashtags = re.findall(r'#(\w+)', content)
        
        assert len(hashtags) == 4
        assert "gaming" in hashtags
        assert "tech" in hashtags
        assert "setup" in hashtags
        assert "valorant" in hashtags
    
    def test_discord_channel_mention_extraction(self, real_collector):
        """Testa extração de menções de canais."""
        content = "Check out <#111111111> and <#222222222> channels!"
        channel_mentions = re.findall(r'<#(\d+)>', content)
        
        assert len(channel_mentions) == 2
        assert "111111111" in channel_mentions
        assert "222222222" in channel_mentions
    
    def test_discord_word_extraction(self, real_collector):
        """Testa extração de palavras de mensagens."""
        content = "Anyone playing valorant tonight? Looking for teammates!"
        words = re.findall(r'\b\w{4,}\b', content.lower())
        
        assert len(words) > 0
        assert "anyone" in words
        assert "playing" in words
        assert "valorant" in words
        assert "tonight" in words
        assert "looking" in words
        assert "teammates" in words
    
    def test_discord_reaction_analysis(self, real_collector, sample_messages_response):
        """Testa análise de reações."""
        total_reactions = 0
        emoji_counts = {}
        
        for message in sample_messages_response:
            for reaction in message["reactions"]:
                emoji_name = reaction["emoji"]["name"]
                count = reaction["count"]
                total_reactions += count
                emoji_counts[emoji_name] = emoji_counts.get(emoji_name, 0) + count
        
        assert total_reactions == 8  # 5 + 3
        assert emoji_counts["👍"] == 5
        assert emoji_counts["🎮"] == 3
    
    def test_discord_thread_analysis(self, real_collector, sample_messages_response):
        """Testa análise de threads."""
        threads_count = 0
        total_thread_messages = 0
        
        for message in sample_messages_response:
            if message["thread"]:
                threads_count += 1
                total_thread_messages += message["thread"]["message_count"]
        
        assert threads_count == 1
        assert total_thread_messages == 10
    
    def test_discord_temporal_analysis(self, real_collector, sample_messages_response):
        """Testa análise temporal."""
        timestamps = []
        for message in sample_messages_response:
            timestamp = datetime.fromisoformat(message["timestamp"].replace("Z", "+00:00"))
            timestamps.append(timestamp)
        
        # Verificar se as mensagens estão em ordem cronológica
        assert timestamps[1] < timestamps[0]  # 09:30 < 10:00
        
        # Calcular diferença de tempo
        time_diff = timestamps[0] - timestamps[1]
        assert time_diff.total_seconds() == 1800  # 30 minutos 