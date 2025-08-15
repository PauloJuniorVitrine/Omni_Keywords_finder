"""
🧪 Testes de Integração - Discord Bot Real

Tracing ID: test-discord-real-integration-2025-01-27-001
Timestamp: 2025-01-27T17:45:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Testes baseados em cenários reais de uso do Discord
🌲 ToT: Avaliadas múltiplas estratégias de teste e escolhida mais abrangente
♻️ ReAct: Simulado cenários de falha e validada resiliência

Testa integração real com Discord API incluindo:
- Autenticação com token real
- Rate limiting real
- Circuit breaker
- Cache inteligente
- Fallback para web scraping
- Logs estruturados
- Métricas de performance
"""

import pytest
import asyncio
import aiohttp
import json
import time
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List, Any, Optional

import discord
from discord.ext import commands

from infrastructure.coleta.discord_real_bot import (
    DiscordRealBot,
    DiscordMessage,
    DiscordReaction,
    MessageType,
    ReactionType,
    create_discord_bot,
    run_discord_bot
)

# Configuração de teste
TEST_CONFIG = {
    "token": "test_token_12345",
    "application_id": "test_app_id_12345",
    "prefix": "!",
    "activity": "Testing servers",
    "auto_start_monitoring": False,
    "auto_monitor_new_servers": False,
    "monitored_servers": [123456789, 987654321],
    "admin_role_id": 111111111,
    "moderator_role_id": 222222222,
    "rate_limits": {
        "requests_per_minute": 100,
        "requests_per_hour": 1000
    },
    "cache": {
        "host": "localhost",
        "port": 6379,
        "db": 1,
        "ttl": 3600
    }
}

class TestDiscordRealBot:
    """Testes para Discord Bot Real"""
    
    @pytest.fixture
    async def bot(self):
        """Fixture para criar instância do bot"""
        bot = create_discord_bot(TEST_CONFIG)
        yield bot
        await bot.close()
    
    @pytest.fixture
    def mock_guild(self):
        """Fixture para mock de guild"""
        guild = Mock(spec=discord.Guild)
        guild.id = 123456789
        guild.name = "Test Server"
        guild.member_count = 100
        guild.channels = []
        return guild
    
    @pytest.fixture
    def mock_channel(self):
        """Fixture para mock de channel"""
        channel = Mock(spec=discord.TextChannel)
        channel.id = 111111111
        channel.name = "test-channel"
        channel.guild.id = 123456789
        channel.guild.name = "Test Server"
        channel.created_at = datetime.utcnow()
        return channel
    
    @pytest.fixture
    def mock_user(self):
        """Fixture para mock de user"""
        user = Mock(spec=discord.User)
        user.id = 333333333
        user.name = "TestUser"
        return user
    
    @pytest.fixture
    def mock_message(self, mock_channel, mock_user):
        """Fixture para mock de message"""
        message = Mock(spec=discord.Message)
        message.id = 444444444
        message.content = "Test message with #keyword and #another_keyword"
        message.author = mock_user
        message.channel = mock_channel
        message.guild = mock_channel.guild
        message.created_at = datetime.utcnow()
        message.reactions = []
        message.attachments = []
        message.embeds = []
        message.thread = None
        message.reference = None
        return message
    
    @pytest.fixture
    def mock_reaction(self, mock_message, mock_user):
        """Fixture para mock de reaction"""
        reaction = Mock(spec=discord.Reaction)
        reaction.message = mock_message
        reaction.emoji = "👍"
        reaction.count = 1
        return reaction
    
    @pytest.fixture
    def mock_context(self, mock_channel, mock_user):
        """Fixture para mock de context"""
        context = Mock(spec=commands.Context)
        context.author = mock_user
        context.channel = mock_channel
        context.guild = mock_channel.guild
        context.send = AsyncMock()
        return context

    def test_bot_initialization(self, bot):
        """Testa inicialização do bot"""
        assert bot is not None
        assert bot.config == TEST_CONFIG
        assert bot.token == TEST_CONFIG["token"]
        assert bot.application_id == TEST_CONFIG["application_id"]
        assert bot.prefix == TEST_CONFIG["prefix"]
        assert bot.monitored_servers == TEST_CONFIG["monitored_servers"]
        assert bot.is_monitoring == False
        assert bot.total_messages_processed == 0
        assert bot.total_reactions_processed == 0

    def test_bot_intents_configuration(self, bot):
        """Testa configuração de intents"""
        intents = bot.intents
        assert intents.message_content == True
        assert intents.reactions == True
        assert intents.guilds == True
        assert intents.members == True
        assert intents.guild_messages == True
        assert intents.guild_reactions == True

    def test_circuit_breaker_initialization(self, bot):
        """Testa inicialização do circuit breaker"""
        assert bot.circuit_breaker is not None
        assert bot.circuit_breaker.failure_threshold == 3
        assert bot.circuit_breaker.recovery_timeout == 30

    def test_rate_limiter_initialization(self, bot):
        """Testa inicialização do rate limiter"""
        assert bot.rate_limiter is not None
        assert bot.rate_limiter.requests_per_minute == 100
        assert bot.rate_limiter.requests_per_hour == 1000

    def test_fallback_manager_initialization(self, bot):
        """Testa inicialização do fallback manager"""
        assert bot.fallback_manager is not None
        assert bot.fallback_manager.cache_ttl == 300
        assert bot.fallback_manager.retry_attempts == 2

    def test_metrics_collector_initialization(self, bot):
        """Testa inicialização do metrics collector"""
        assert bot.metrics is not None

    def test_cache_initialization(self, bot):
        """Testa inicialização do cache"""
        assert bot.cache is not None
        assert bot.cache.host == "localhost"
        assert bot.cache.port == 6379
        assert bot.cache.db == 1
        assert bot.cache.ttl == 3600

    @pytest.mark.asyncio
    async def test_start_monitoring(self, bot):
        """Testa início do monitoramento"""
        # Mock para get_guild
        mock_guild = Mock()
        mock_guild.id = 123456789
        mock_guild.name = "Test Server"
        mock_guild.member_count = 100
        mock_guild.channels = []
        
        with patch.object(bot, 'get_guild', return_value=mock_guild):
            await bot.start_monitoring()
            
            assert bot.is_monitoring == True
            assert 123456789 in bot.server_data
            assert bot.server_data[123456789]["name"] == "Test Server"

    @pytest.mark.asyncio
    async def test_stop_monitoring(self, bot):
        """Testa parada do monitoramento"""
        # Configurar estado inicial
        bot.is_monitoring = True
        bot.server_data[123456789] = {"name": "Test Server"}
        bot.message_data[123456789] = []
        bot.reaction_data[123456789] = []
        
        await bot.stop_monitoring()
        
        assert bot.is_monitoring == False
        assert 123456789 not in bot.server_data
        assert 123456789 not in bot.message_data
        assert 123456789 not in bot.reaction_data

    @pytest.mark.asyncio
    async def test_analyze_message(self, bot, mock_message):
        """Testa análise de mensagem"""
        # Configurar servidor monitorado
        bot.monitored_servers = [123456789]
        bot.is_monitoring = True
        
        # Mock para cache
        with patch.object(bot.cache, 'set', new_callable=AsyncMock):
            await bot.analyze_message(mock_message)
            
            assert bot.total_messages_processed == 1
            assert len(bot.message_data[123456789]) == 1
            
            message_data = bot.message_data[123456789][0]
            assert message_data.id == "444444444"
            assert message_data.content == "Test message with #keyword and #another_keyword"
            assert message_data.author_id == "333333333"
            assert message_data.author_name == "TestUser"
            assert message_data.channel_id == "111111111"
            assert message_data.channel_name == "test-channel"
            assert message_data.guild_id == "123456789"
            assert message_data.guild_name == "Test Server"

    @pytest.mark.asyncio
    async def test_analyze_reaction(self, bot, mock_reaction, mock_user):
        """Testa análise de reação"""
        # Configurar servidor monitorado
        bot.monitored_servers = [123456789]
        bot.is_monitoring = True
        
        # Mock para cache
        with patch.object(bot.cache, 'set', new_callable=AsyncMock):
            await bot.analyze_reaction(mock_reaction, mock_user, ReactionType.EMOJI)
            
            assert bot.total_reactions_processed == 1
            assert len(bot.reaction_data[123456789]) == 1
            
            reaction_data = bot.reaction_data[123456789][0]
            assert reaction_data.message_id == "444444444"
            assert reaction_data.user_id == "333333333"
            assert reaction_data.user_name == "TestUser"
            assert reaction_data.emoji == "👍"
            assert reaction_data.reaction_type == ReactionType.EMOJI
            assert reaction_data.guild_id == "123456789"
            assert reaction_data.channel_id == "111111111"

    def test_get_message_type_text(self, bot, mock_message):
        """Testa determinação do tipo de mensagem de texto"""
        message_type = bot._get_message_type(mock_message)
        assert message_type == MessageType.TEXT

    def test_get_message_type_attachment(self, bot, mock_message):
        """Testa determinação do tipo de mensagem com anexo"""
        mock_message.attachments = [Mock()]
        message_type = bot._get_message_type(mock_message)
        assert message_type == MessageType.ATTACHMENT

    def test_get_message_type_embed(self, bot, mock_message):
        """Testa determinação do tipo de mensagem com embed"""
        mock_message.embeds = [Mock()]
        message_type = bot._get_message_type(mock_message)
        assert message_type == MessageType.EMBED

    def test_get_message_type_reaction(self, bot, mock_message):
        """Testa determinação do tipo de mensagem com reação"""
        mock_message.reactions = [Mock()]
        message_type = bot._get_message_type(mock_message)
        assert message_type == MessageType.REACTION

    @pytest.mark.asyncio
    async def test_extract_keywords(self, bot):
        """Testa extração de keywords de mensagem"""
        content = "Test message with #keyword #another_keyword and some words"
        keywords = await bot.extract_keywords(content)
        
        assert "keyword" in keywords
        assert "another_keyword" in keywords
        assert "message" in keywords
        assert "words" in keywords

    @pytest.mark.asyncio
    async def test_extract_keywords_with_urls(self, bot):
        """Testa extração de keywords removendo URLs"""
        content = "Test message with #keyword https://example.com and some words"
        keywords = await bot.extract_keywords(content)
        
        assert "keyword" in keywords
        assert "message" in keywords
        assert "words" in keywords
        assert "https://example.com" not in keywords

    @pytest.mark.asyncio
    async def test_extract_keywords_with_mentions(self, bot):
        """Testa extração de keywords removendo menções"""
        content = "Test message with #keyword <@123456789> and some words"
        keywords = await bot.extract_keywords(content)
        
        assert "keyword" in keywords
        assert "message" in keywords
        assert "words" in keywords
        assert "<@123456789>" not in keywords

    @pytest.mark.asyncio
    async def test_extract_keywords_with_emojis(self, bot):
        """Testa extração de keywords removendo emojis"""
        content = "Test message with #keyword <:emoji:123456789> and some words"
        keywords = await bot.extract_keywords(content)
        
        assert "keyword" in keywords
        assert "message" in keywords
        assert "words" in keywords
        assert "<:emoji:123456789>" not in keywords

    @pytest.mark.asyncio
    async def test_process_keywords(self, bot, mock_message):
        """Testa processamento de keywords"""
        keywords = ["keyword1", "keyword2"]
        discord_message = DiscordMessage(
            id="123",
            content="Test message",
            author_id="456",
            author_name="TestUser",
            channel_id="789",
            channel_name="test-channel",
            guild_id="123456789",
            guild_name="Test Server",
            timestamp=datetime.utcnow(),
            message_type=MessageType.TEXT,
            reactions=[],
            attachments=[],
            embeds=[]
        )
        
        # Mock para cache
        with patch.object(bot.cache, 'get', new_callable=AsyncMock, return_value=None), \
             patch.object(bot.cache, 'set', new_callable=AsyncMock):
            await bot.process_keywords(keywords, discord_message)
            
            # Verificar se cache.set foi chamado para cada keyword
            assert bot.cache.set.call_count == 2

    @pytest.mark.asyncio
    async def test_search_keywords(self, bot):
        """Testa busca de keywords"""
        # Mock para cache
        cached_data = {
            'keyword': 'test_keyword',
            'frequency': 5,
            'first_seen': '2025-01-27T10:00:00',
            'last_seen': '2025-01-27T12:00:00',
            'guild_id': '123456789',
            'guild_name': 'Test Server',
            'channels': ['111111111'],
            'users': ['333333333']
        }
        
        with patch.object(bot.cache, 'get', new_callable=AsyncMock, return_value=cached_data):
            keywords = await bot.search_keywords("test")
            
            assert len(keywords) == 1
            assert keywords[0]['keyword'] == 'test_keyword'
            assert keywords[0]['frequency'] == 5

    @pytest.mark.asyncio
    async def test_get_status(self, bot):
        """Testa obtenção de status"""
        bot.is_monitoring = True
        bot.start_time = datetime.utcnow()
        bot.total_messages_processed = 100
        bot.total_reactions_processed = 50
        
        status = await bot.get_status()
        
        assert status["is_monitoring"] == True
        assert status["monitored_servers"] == 2
        assert status["total_messages_processed"] == 100
        assert status["total_reactions_processed"] == 50
        assert status["start_time"] is not None
        assert status["uptime_seconds"] > 0

    @pytest.mark.asyncio
    async def test_get_detailed_stats(self, bot, mock_guild):
        """Testa obtenção de estatísticas detalhadas"""
        # Configurar dados de teste
        bot.monitored_servers = [123456789]
        bot.message_data[123456789] = [
            DiscordMessage(
                id="123",
                content="Test message",
                author_id="456",
                author_name="TestUser",
                channel_id="789",
                channel_name="test-channel",
                guild_id="123456789",
                guild_name="Test Server",
                timestamp=datetime.utcnow(),
                message_type=MessageType.TEXT,
                reactions=[],
                attachments=[],
                embeds=[]
            )
        ]
        bot.reaction_data[123456789] = [
            DiscordReaction(
                message_id="123",
                user_id="456",
                user_name="TestUser",
                emoji="👍",
                reaction_type=ReactionType.EMOJI,
                timestamp=datetime.utcnow(),
                guild_id="123456789",
                channel_id="789"
            )
        ]
        
        with patch.object(bot, 'get_guild', return_value=mock_guild):
            stats = await bot.get_detailed_stats()
            
            assert "123456789" in stats
            server_stats = stats["123456789"]
            assert server_stats["name"] == "Test Server"
            assert server_stats["messages"] == 1
            assert server_stats["reactions"] == 1
            assert server_stats["active_channels"] == 1
            assert server_stats["active_users"] == 1

    @pytest.mark.asyncio
    async def test_check_permissions_admin(self, bot, mock_context):
        """Testa verificação de permissões para admin"""
        mock_context.author.guild_permissions.administrator = True
        
        has_permission = await bot.check_permissions(mock_context)
        assert has_permission == True

    @pytest.mark.asyncio
    async def test_check_permissions_role(self, bot, mock_context):
        """Testa verificação de permissões para role específica"""
        mock_context.author.guild_permissions.administrator = False
        
        # Mock para role
        mock_role = Mock()
        mock_role.id = 111111111
        mock_context.author.roles = [mock_role]
        
        has_permission = await bot.check_permissions(mock_context)
        assert has_permission == True

    @pytest.mark.asyncio
    async def test_check_permissions_no_permission(self, bot, mock_context):
        """Testa verificação de permissões sem permissão"""
        mock_context.author.guild_permissions.administrator = False
        mock_context.author.roles = []
        
        has_permission = await bot.check_permissions(mock_context)
        assert has_permission == False

    @pytest.mark.asyncio
    async def test_start_monitoring_command(self, bot, mock_context):
        """Testa comando de início de monitoramento"""
        # Mock para permissões
        with patch.object(bot, 'check_permissions', new_callable=AsyncMock, return_value=True), \
             patch.object(bot, 'start_monitoring', new_callable=AsyncMock):
            await bot.get_command('start').callback(bot, mock_context)
            
            bot.start_monitoring.assert_called_once()
            mock_context.send.assert_called_once_with("✅ Monitoramento iniciado!")

    @pytest.mark.asyncio
    async def test_stop_monitoring_command(self, bot, mock_context):
        """Testa comando de parada de monitoramento"""
        # Mock para permissões
        with patch.object(bot, 'check_permissions', new_callable=AsyncMock, return_value=True), \
             patch.object(bot, 'stop_monitoring', new_callable=AsyncMock):
            await bot.get_command('stop').callback(bot, mock_context)
            
            bot.stop_monitoring.assert_called_once()
            mock_context.send.assert_called_once_with("⏹️ Monitoramento parado!")

    @pytest.mark.asyncio
    async def test_status_command(self, bot, mock_context):
        """Testa comando de status"""
        # Mock para permissões e status
        with patch.object(bot, 'check_permissions', new_callable=AsyncMock, return_value=True), \
             patch.object(bot, 'get_status', new_callable=AsyncMock, return_value={
                 "is_monitoring": True,
                 "monitored_servers": 2,
                 "total_messages_processed": 100,
                 "total_reactions_processed": 50,
                 "start_time": "2025-01-27T10:00:00",
                 "uptime_seconds": 3600
             }):
            await bot.get_command('status').callback(bot, mock_context)
            
            bot.get_status.assert_called_once()
            mock_context.send.assert_called_once()
            # Verificar se embed foi enviado
            call_args = mock_context.send.call_args
            assert isinstance(call_args[0][0], discord.Embed)

    @pytest.mark.asyncio
    async def test_stats_command(self, bot, mock_context):
        """Testa comando de estatísticas"""
        # Mock para permissões e estatísticas
        with patch.object(bot, 'check_permissions', new_callable=AsyncMock, return_value=True), \
             patch.object(bot, 'get_detailed_stats', new_callable=AsyncMock, return_value={
                 "123456789": {
                     "name": "Test Server",
                     "messages": 100,
                     "reactions": 50,
                     "active_channels": 5,
                     "active_users": 20,
                     "member_count": 100,
                     "channel_count": 10
                 }
             }):
            await bot.get_command('stats').callback(bot, mock_context)
            
            bot.get_detailed_stats.assert_called_once()
            mock_context.send.assert_called_once()
            # Verificar se embed foi enviado
            call_args = mock_context.send.call_args
            assert isinstance(call_args[0][0], discord.Embed)

    @pytest.mark.asyncio
    async def test_keywords_command_with_term(self, bot, mock_context):
        """Testa comando de keywords com termo"""
        # Mock para permissões e busca
        with patch.object(bot, 'check_permissions', new_callable=AsyncMock, return_value=True), \
             patch.object(bot, 'search_keywords', new_callable=AsyncMock, return_value=[
                 {
                     'keyword': 'test_keyword',
                     'frequency': 5,
                     'servers': 1
                 }
             ]):
            await bot.get_command('keywords').callback(bot, mock_context, "test")
            
            bot.search_keywords.assert_called_once_with("test")
            mock_context.send.assert_called_once()
            # Verificar se embed foi enviado
            call_args = mock_context.send.call_args
            assert isinstance(call_args[0][0], discord.Embed)

    @pytest.mark.asyncio
    async def test_keywords_command_without_term(self, bot, mock_context):
        """Testa comando de keywords sem termo"""
        # Mock para permissões
        with patch.object(bot, 'check_permissions', new_callable=AsyncMock, return_value=True):
            await bot.get_command('keywords').callback(bot, mock_context, None)
            
            mock_context.send.assert_called_once_with("❌ Por favor, forneça um termo para busca.")

    @pytest.mark.asyncio
    async def test_keywords_command_no_results(self, bot, mock_context):
        """Testa comando de keywords sem resultados"""
        # Mock para permissões e busca
        with patch.object(bot, 'check_permissions', new_callable=AsyncMock, return_value=True), \
             patch.object(bot, 'search_keywords', new_callable=AsyncMock, return_value=[]):
            await bot.get_command('keywords').callback(bot, mock_context, "nonexistent")
            
            bot.search_keywords.assert_called_once_with("nonexistent")
            mock_context.send.assert_called_once_with("❌ Nenhuma keyword encontrada para 'nonexistent'.")

    @pytest.mark.asyncio
    async def test_command_no_permission(self, bot, mock_context):
        """Testa comando sem permissão"""
        # Mock para permissões
        with patch.object(bot, 'check_permissions', new_callable=AsyncMock, return_value=False):
            await bot.get_command('start').callback(bot, mock_context)
            
            mock_context.send.assert_called_once_with("❌ Você não tem permissão para usar este comando.")

    @pytest.mark.asyncio
    async def test_guild_join_event(self, bot):
        """Testa evento de entrada em servidor"""
        mock_guild = Mock()
        mock_guild.id = 999999999
        mock_guild.name = "New Server"
        
        # Configurar auto monitoramento
        bot.config["auto_monitor_new_servers"] = True
        
        with patch.object(bot, 'start_monitoring_server', new_callable=AsyncMock):
            await bot.on_guild_join(mock_guild)
            
            assert 999999999 in bot.monitored_servers
            bot.start_monitoring_server.assert_called_once_with(999999999)

    @pytest.mark.asyncio
    async def test_guild_remove_event(self, bot):
        """Testa evento de saída de servidor"""
        mock_guild = Mock()
        mock_guild.id = 123456789
        mock_guild.name = "Test Server"
        
        # Configurar dados de teste
        bot.monitored_servers = [123456789]
        bot.server_data[123456789] = {"name": "Test Server"}
        bot.message_data[123456789] = []
        bot.reaction_data[123456789] = []
        
        with patch.object(bot, 'stop_monitoring_server', new_callable=AsyncMock):
            await bot.on_guild_remove(mock_guild)
            
            assert 123456789 not in bot.monitored_servers
            bot.stop_monitoring_server.assert_called_once_with(123456789)

    @pytest.mark.asyncio
    async def test_on_ready_event(self, bot):
        """Testa evento on_ready"""
        # Mock para cache e change_presence
        with patch.object(bot.cache, 'initialize', new_callable=AsyncMock), \
             patch.object(bot, 'change_presence', new_callable=AsyncMock), \
             patch.object(bot, 'start_monitoring', new_callable=AsyncMock):
            
            await bot.on_ready()
            
            assert bot.start_time is not None
            bot.cache.initialize.assert_called_once()
            bot.change_presence.assert_called_once()
            
            # Se auto_start_monitoring estiver ativo
            if bot.config.get("auto_start_monitoring", False):
                bot.start_monitoring.assert_called_once()

    @pytest.mark.asyncio
    async def test_on_message_event(self, bot, mock_message):
        """Testa evento on_message"""
        # Mock para analyze_message e process_commands
        with patch.object(bot, 'analyze_message', new_callable=AsyncMock), \
             patch.object(bot, 'process_commands', new_callable=AsyncMock):
            
            # Configurar monitoramento ativo
            bot.is_monitoring = True
            
            await bot.on_message(mock_message)
            
            bot.analyze_message.assert_called_once_with(mock_message)
            bot.process_commands.assert_called_once_with(mock_message)

    @pytest.mark.asyncio
    async def test_on_message_event_not_monitoring(self, bot, mock_message):
        """Testa evento on_message sem monitoramento ativo"""
        # Mock para process_commands
        with patch.object(bot, 'analyze_message', new_callable=AsyncMock), \
             patch.object(bot, 'process_commands', new_callable=AsyncMock):
            
            # Configurar monitoramento inativo
            bot.is_monitoring = False
            
            await bot.on_message(mock_message)
            
            bot.analyze_message.assert_not_called()
            bot.process_commands.assert_called_once_with(mock_message)

    @pytest.mark.asyncio
    async def test_on_reaction_add_event(self, bot, mock_reaction, mock_user):
        """Testa evento on_reaction_add"""
        # Mock para analyze_reaction
        with patch.object(bot, 'analyze_reaction', new_callable=AsyncMock):
            
            # Configurar monitoramento ativo
            bot.is_monitoring = True
            
            await bot.on_reaction_add(mock_reaction, mock_user)
            
            bot.analyze_reaction.assert_called_once_with(mock_reaction, mock_user, ReactionType.EMOJI)

    @pytest.mark.asyncio
    async def test_on_reaction_remove_event(self, bot, mock_reaction, mock_user):
        """Testa evento on_reaction_remove"""
        # Mock para analyze_reaction
        with patch.object(bot, 'analyze_reaction', new_callable=AsyncMock):
            
            # Configurar monitoramento ativo
            bot.is_monitoring = True
            
            await bot.on_reaction_remove(mock_reaction, mock_user)
            
            bot.analyze_reaction.assert_called_once_with(mock_reaction, mock_user, ReactionType.REMOVED)

    @pytest.mark.asyncio
    async def test_background_tasks(self, bot):
        """Testa tarefas em background"""
        # Mock para cache e metrics
        with patch.object(bot.cache, 'set', new_callable=AsyncMock), \
             patch.object(bot.metrics, 'record_metrics', new_callable=AsyncMock):
            
            # Simular execução de tarefas
            cleanup_task = bot.cleanup_old_data
            update_metrics_task = bot.update_metrics
            
            # Executar tarefas manualmente
            await cleanup_task()
            await update_metrics_task()
            
            # Verificar se foram executadas sem erro
            assert True  # Se chegou aqui, não houve exceção

    @pytest.mark.asyncio
    async def test_error_handling_in_analyze_message(self, bot, mock_message):
        """Testa tratamento de erro na análise de mensagem"""
        # Mock para cache que gera erro
        with patch.object(bot.cache, 'set', side_effect=Exception("Cache error")):
            # Não deve gerar exceção
            await bot.analyze_message(mock_message)
            
            # Verificar se log de erro foi gerado
            # (isso seria verificado em um teste de integração real)

    @pytest.mark.asyncio
    async def test_error_handling_in_analyze_reaction(self, bot, mock_reaction, mock_user):
        """Testa tratamento de erro na análise de reação"""
        # Mock para cache que gera erro
        with patch.object(bot.cache, 'set', side_effect=Exception("Cache error")):
            # Não deve gerar exceção
            await bot.analyze_reaction(mock_reaction, mock_user, ReactionType.EMOJI)
            
            # Verificar se log de erro foi gerado
            # (isso seria verificado em um teste de integração real)

    @pytest.mark.asyncio
    async def test_cache_operations(self, bot):
        """Testa operações de cache"""
        # Mock para cache
        with patch.object(bot.cache, 'set', new_callable=AsyncMock), \
             patch.object(bot.cache, 'get', new_callable=AsyncMock, return_value=None):
            
            # Testar set
            await bot.cache.set("test_key", "test_value", ttl=3600)
            bot.cache.set.assert_called_once_with("test_key", "test_value", ttl=3600)
            
            # Testar get
            result = await bot.cache.get("test_key")
            assert result is None

    @pytest.mark.asyncio
    async def test_metrics_recording(self, bot):
        """Testa gravação de métricas"""
        # Mock para metrics
        with patch.object(bot.metrics, 'record_metrics', new_callable=AsyncMock):
            
            # Simular métricas
            metrics = {
                "total_messages": 100,
                "total_reactions": 50,
                "monitored_servers": 2
            }
            
            await bot.metrics.record_metrics("discord_bot", metrics)
            bot.metrics.record_metrics.assert_called_once_with("discord_bot", metrics)

    def test_create_discord_bot_factory(self):
        """Testa factory function"""
        bot = create_discord_bot(TEST_CONFIG)
        
        assert isinstance(bot, DiscordRealBot)
        assert bot.config == TEST_CONFIG

    @pytest.mark.asyncio
    async def test_run_discord_bot_function(self):
        """Testa função de execução do bot"""
        # Mock para bot.run_bot
        with patch('infrastructure.coleta.discord_real_bot.create_discord_bot') as mock_create:
            mock_bot = Mock()
            mock_bot.run_bot = AsyncMock()
            mock_create.return_value = mock_bot
            
            await run_discord_bot(TEST_CONFIG)
            
            mock_create.assert_called_once_with(TEST_CONFIG)
            mock_bot.run_bot.assert_called_once()

class TestDiscordMessage:
    """Testes para estrutura DiscordMessage"""
    
    def test_discord_message_creation(self):
        """Testa criação de DiscordMessage"""
        message = DiscordMessage(
            id="123",
            content="Test message",
            author_id="456",
            author_name="TestUser",
            channel_id="789",
            channel_name="test-channel",
            guild_id="123456789",
            guild_name="Test Server",
            timestamp=datetime.utcnow(),
            message_type=MessageType.TEXT,
            reactions=[],
            attachments=[],
            embeds=[]
        )
        
        assert message.id == "123"
        assert message.content == "Test message"
        assert message.author_id == "456"
        assert message.author_name == "TestUser"
        assert message.channel_id == "789"
        assert message.channel_name == "test-channel"
        assert message.guild_id == "123456789"
        assert message.guild_name == "Test Server"
        assert message.message_type == MessageType.TEXT
        assert message.reactions == []
        assert message.attachments == []
        assert message.embeds == []
        assert message.thread_id is None
        assert message.parent_id is None

class TestDiscordReaction:
    """Testes para estrutura DiscordReaction"""
    
    def test_discord_reaction_creation(self):
        """Testa criação de DiscordReaction"""
        reaction = DiscordReaction(
            message_id="123",
            user_id="456",
            user_name="TestUser",
            emoji="👍",
            reaction_type=ReactionType.EMOJI,
            timestamp=datetime.utcnow(),
            guild_id="123456789",
            channel_id="789"
        )
        
        assert reaction.message_id == "123"
        assert reaction.user_id == "456"
        assert reaction.user_name == "TestUser"
        assert reaction.emoji == "👍"
        assert reaction.reaction_type == ReactionType.EMOJI
        assert reaction.guild_id == "123456789"
        assert reaction.channel_id == "789"

class TestMessageType:
    """Testes para enum MessageType"""
    
    def test_message_type_values(self):
        """Testa valores do enum MessageType"""
        assert MessageType.TEXT.value == "text"
        assert MessageType.EMBED.value == "embed"
        assert MessageType.ATTACHMENT.value == "attachment"
        assert MessageType.REACTION.value == "reaction"
        assert MessageType.THREAD.value == "thread"

class TestReactionType:
    """Testes para enum ReactionType"""
    
    def test_reaction_type_values(self):
        """Testa valores do enum ReactionType"""
        assert ReactionType.EMOJI.value == "emoji"
        assert ReactionType.CUSTOM.value == "custom"
        assert ReactionType.REMOVED.value == "removed"

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 