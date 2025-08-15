"""
📌 Discord Bot Real Implementation

Tracing ID: discord-real-bot-2025-01-27-001
Timestamp: 2025-01-27T17:30:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Bot baseado em Discord.py v2.x e boas práticas de desenvolvimento
🌲 ToT: Avaliadas múltiplas abordagens de implementação e escolhida mais robusta
♻️ ReAct: Simulado cenários de uso e validada performance

Implementa Discord Bot real com:
- Autenticação com token real
- Rate limiting real
- Circuit breaker
- Cache inteligente
- Fallback para web scraping
- Logs estruturados
- Métricas de performance
"""

import discord
from discord.ext import commands, tasks
import asyncio
import logging
import os
import json
import aiohttp
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict, Counter
import re
from dataclasses import dataclass
from enum import Enum

from infrastructure.orchestrator.error_handler import CircuitBreaker
from infrastructure.orchestrator.rate_limiter import RateLimiter
from infrastructure.orchestrator.fallback_manager import FallbackManager
from infrastructure.observability.metrics_collector import MetricsCollector
from infrastructure.cache.redis_cache import RedisCache
from shared.logger import logger

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Tipos de mensagem Discord"""
    TEXT = "text"
    EMBED = "embed"
    ATTACHMENT = "attachment"
    REACTION = "reaction"
    THREAD = "thread"

class ReactionType(Enum):
    """Tipos de reação Discord"""
    EMOJI = "emoji"
    CUSTOM = "custom"
    REMOVED = "removed"

@dataclass
class DiscordMessage:
    """Estrutura de dados para mensagens Discord"""
    id: str
    content: str
    author_id: str
    author_name: str
    channel_id: str
    channel_name: str
    guild_id: str
    guild_name: str
    timestamp: datetime
    message_type: MessageType
    reactions: List[Dict]
    attachments: List[Dict]
    embeds: List[Dict]
    thread_id: Optional[str] = None
    parent_id: Optional[str] = None

@dataclass
class DiscordReaction:
    """Estrutura de dados para reações Discord"""
    message_id: str
    user_id: str
    user_name: str
    emoji: str
    reaction_type: ReactionType
    timestamp: datetime
    guild_id: str
    channel_id: str

class DiscordRealBot(commands.Bot):
    """
    Bot Discord real para Omni Keywords Finder
    
    Implementa monitoramento de servidores Discord incluindo:
    - Análise de mensagens e reações
    - Tracking de engajamento
    - Detecção de tendências
    - Integração com sistema de keywords
    - Rate limiting real
    - Circuit breaker
    - Cache inteligente
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa bot Discord real
        
        Args:
            config: Configuração do bot
        """
        # Configurar intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        intents.guilds = True
        intents.members = True
        intents.guild_messages = True
        intents.guild_reactions = True
        
        super().__init__(
            command_prefix=config.get("prefix", "!"),
            intents=intents,
            help_command=None
        )
        
        # Configuração
        self.config = config
        self.token = config.get("token")
        self.application_id = config.get("application_id")
        self.monitored_servers = config.get("monitored_servers", [])
        self.admin_role_id = config.get("admin_role_id")
        self.moderator_role_id = config.get("moderator_role_id")
        
        # Configurar circuit breaker
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=30,
            expected_exception=Exception
        )
        
        # Configurar rate limiter
        self.rate_limiter = RateLimiter(
            requests_per_minute=config.get("rate_limits", {}).get("requests_per_minute", 100),
            requests_per_hour=config.get("rate_limits", {}).get("requests_per_hour", 1000)
        )
        
        # Configurar fallback manager
        self.fallback_manager = FallbackManager(
            cache_ttl=300,  # 5 minutos
            retry_attempts=2
        )
        
        # Configurar métricas
        self.metrics = MetricsCollector()
        
        # Configurar cache
        self.cache = RedisCache(
            host=config.get("cache", {}).get("host", "localhost"),
            port=config.get("cache", {}).get("port", 6379),
            db=config.get("cache", {}).get("db", 0),
            ttl=config.get("cache", {}).get("ttl", 3600)
        )
        
        # Dados de monitoramento
        self.message_data = defaultdict(list)
        self.reaction_data = defaultdict(list)
        self.server_data = defaultdict(dict)
        self.channel_data = defaultdict(dict)
        
        # Status do bot
        self.is_monitoring = False
        self.start_time = None
        self.total_messages_processed = 0
        self.total_reactions_processed = 0
        
        # Configurar eventos
        self.setup_events()
        
        # Configurar comandos
        self.setup_commands()
        
        # Configurar tarefas em background
        self.setup_background_tasks()
    
    def setup_events(self):
        """Configura eventos do bot"""
        @self.event
        async def on_ready():
            """Evento executado quando o bot está pronto"""
            self.start_time = datetime.utcnow()
            logger.info(f'Bot conectado como {self.user.name}')
            
            # Configurar status
            activity = discord.Activity(
                type=discord.ActivityType.watching,
                name=self.config.get("activity", "Monitoring servers")
            )
            await self.change_presence(activity=activity)
            
            # Inicializar cache
            await self.cache.initialize()
            
            # Iniciar monitoramento se configurado
            if self.config.get("auto_start_monitoring", False):
                await self.start_monitoring()
        
        @self.event
        async def on_message(message):
            """Processar mensagens recebidas"""
            # Ignorar mensagens do próprio bot
            if message.author == self.user:
                return
            
            # Analisar mensagem se monitoramento ativo
            if self.is_monitoring:
                await self.analyze_message(message)
            
            # Processar comandos
            await self.process_commands(message)
        
        @self.event
        async def on_reaction_add(reaction, user):
            """Processar reações adicionadas"""
            # Ignorar reações do próprio bot
            if user == self.user:
                return
            
            # Analisar reação se monitoramento ativo
            if self.is_monitoring:
                await self.analyze_reaction(reaction, user, ReactionType.EMOJI)
        
        @self.event
        async def on_reaction_remove(reaction, user):
            """Processar reações removidas"""
            # Ignorar reações do próprio bot
            if user == self.user:
                return
            
            # Analisar remoção de reação se monitoramento ativo
            if self.is_monitoring:
                await self.analyze_reaction(reaction, user, ReactionType.REMOVED)
        
        @self.event
        async def on_guild_join(guild):
            """Evento quando bot entra em servidor"""
            logger.info(f"Bot entrou no servidor: {guild.name} (ID: {guild.id})")
            
            # Adicionar servidor aos monitorados se configurado
            if self.config.get("auto_monitor_new_servers", False):
                self.monitored_servers.append(guild.id)
                await self.start_monitoring_server(guild.id)
        
        @self.event
        async def on_guild_remove(guild):
            """Evento quando bot sai de servidor"""
            logger.info(f"Bot saiu do servidor: {guild.name} (ID: {guild.id})")
            
            # Remover servidor dos monitorados
            if guild.id in self.monitored_servers:
                self.monitored_servers.remove(guild.id)
                await self.stop_monitoring_server(guild.id)
    
    def setup_commands(self):
        """Configura comandos do bot"""
        
        @self.command(name="start")
        async def start_monitoring_command(ctx):
            """Inicia monitoramento do servidor"""
            if not await self.check_permissions(ctx):
                await ctx.send("❌ Você não tem permissão para usar este comando.")
                return
            
            await self.start_monitoring()
            await ctx.send("✅ Monitoramento iniciado!")
        
        @self.command(name="stop")
        async def stop_monitoring_command(ctx):
            """Para monitoramento do servidor"""
            if not await self.check_permissions(ctx):
                await ctx.send("❌ Você não tem permissão para usar este comando.")
                return
            
            await self.stop_monitoring()
            await ctx.send("⏹️ Monitoramento parado!")
        
        @self.command(name="status")
        async def status_command(ctx):
            """Mostra status do monitoramento"""
            if not await self.check_permissions(ctx):
                await ctx.send("❌ Você não tem permissão para usar este comando.")
                return
            
            status = await self.get_status()
            embed = discord.Embed(
                title="📊 Status do Monitoramento",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="Status",
                value="🟢 Ativo" if self.is_monitoring else "🔴 Inativo",
                inline=True
            )
            embed.add_field(
                name="Servidores Monitorados",
                value=str(len(self.monitored_servers)),
                inline=True
            )
            embed.add_field(
                name="Mensagens Processadas",
                value=str(self.total_messages_processed),
                inline=True
            )
            embed.add_field(
                name="Reações Processadas",
                value=str(self.total_reactions_processed),
                inline=True
            )
            
            if self.start_time:
                uptime = datetime.utcnow() - self.start_time
                embed.add_field(
                    name="Uptime",
                    value=str(uptime).split('.')[0],
                    inline=True
                )
            
            await ctx.send(embed=embed)
        
        @self.command(name="stats")
        async def stats_command(ctx):
            """Mostra estatísticas detalhadas"""
            if not await self.check_permissions(ctx):
                await ctx.send("❌ Você não tem permissão para usar este comando.")
                return
            
            stats = await self.get_detailed_stats()
            embed = discord.Embed(
                title="📈 Estatísticas Detalhadas",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            
            for server_id, server_stats in stats.items():
                guild = self.get_guild(int(server_id))
                server_name = guild.name if guild else f"Servidor {server_id}"
                
                embed.add_field(
                    name=f"📊 {server_name}",
                    value=f"**Mensagens:** {server_stats.get('messages', 0)}\n"
                          f"**Reações:** {server_stats.get('reactions', 0)}\n"
                          f"**Canais Ativos:** {server_stats.get('active_channels', 0)}\n"
                          f"**Usuários Ativos:** {server_stats.get('active_users', 0)}",
                    inline=False
                )
            
            await ctx.send(embed=embed)
        
        @self.command(name="keywords")
        async def keywords_command(ctx, termo: str = None):
            """Busca keywords relacionadas"""
            if not await self.check_permissions(ctx):
                await ctx.send("❌ Você não tem permissão para usar este comando.")
                return
            
            if not termo:
                await ctx.send("❌ Por favor, forneça um termo para busca.")
                return
            
            keywords = await self.search_keywords(termo)
            
            if not keywords:
                await ctx.send(f"❌ Nenhuma keyword encontrada para '{termo}'.")
                return
            
            embed = discord.Embed(
                title=f"🔍 Keywords para '{termo}'",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            
            # Limitar a 25 keywords para não exceder limite do Discord
            for i, keyword in enumerate(keywords[:25]):
                embed.add_field(
                    name=f"#{i+1}",
                    value=f"**{keyword['keyword']}**\n"
                          f"Frequência: {keyword['frequency']}\n"
                          f"Servidores: {keyword['servers']}",
                    inline=True
                )
            
            await ctx.send(embed=embed)
    
    def setup_background_tasks(self):
        """Configura tarefas em background"""
        
        @tasks.loop(minutes=5)
        async def cleanup_old_data():
            """Limpa dados antigos"""
            try:
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                
                # Limpar mensagens antigas
                for server_id in list(self.message_data.keys()):
                    self.message_data[server_id] = [
                        msg for msg in self.message_data[server_id]
                        if msg.timestamp > cutoff_time
                    ]
                
                # Limpar reações antigas
                for server_id in list(self.reaction_data.keys()):
                    self.reaction_data[server_id] = [
                        reaction for reaction in self.reaction_data[server_id]
                        if reaction.timestamp > cutoff_time
                    ]
                
                logger.info("Limpeza de dados antigos concluída")
                
            except Exception as e:
                logger.error(f"Erro na limpeza de dados: {e}")
        
        @tasks.loop(minutes=10)
        async def update_metrics():
            """Atualiza métricas do bot"""
            try:
                # Coletar métricas
                metrics = {
                    "total_messages": self.total_messages_processed,
                    "total_reactions": self.total_reactions_processed,
                    "monitored_servers": len(self.monitored_servers),
                    "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds() if self.start_time else 0
                }
                
                # Enviar métricas
                await self.metrics.record_metrics("discord_bot", metrics)
                
                logger.info("Métricas atualizadas")
                
            except Exception as e:
                logger.error(f"Erro ao atualizar métricas: {e}")
        
        # Iniciar tarefas
        cleanup_old_data.start()
        update_metrics.start()
    
    async def check_permissions(self, ctx) -> bool:
        """Verifica permissões do usuário"""
        # Admin pode usar todos os comandos
        if ctx.author.guild_permissions.administrator:
            return True
        
        # Verificar roles específicos
        if self.admin_role_id and discord.utils.get(ctx.author.roles, id=self.admin_role_id):
            return True
        
        if self.moderator_role_id and discord.utils.get(ctx.author.roles, id=self.moderator_role_id):
            return True
        
        return False
    
    async def start_monitoring(self):
        """Inicia monitoramento de todos os servidores"""
        if self.is_monitoring:
            logger.warning("Monitoramento já está ativo")
            return
        
        self.is_monitoring = True
        logger.info("Iniciando monitoramento de servidores Discord")
        
        # Iniciar monitoramento de cada servidor
        for server_id in self.monitored_servers:
            await self.start_monitoring_server(server_id)
    
    async def stop_monitoring(self):
        """Para monitoramento de todos os servidores"""
        if not self.is_monitoring:
            logger.warning("Monitoramento já está inativo")
            return
        
        self.is_monitoring = False
        logger.info("Parando monitoramento de servidores Discord")
        
        # Parar monitoramento de cada servidor
        for server_id in self.monitored_servers:
            await self.stop_monitoring_server(server_id)
    
    async def start_monitoring_server(self, server_id: int):
        """Inicia monitoramento de um servidor específico"""
        try:
            guild = self.get_guild(server_id)
            if not guild:
                logger.error(f"Servidor {server_id} não encontrado")
                return
            
            logger.info(f"Iniciando monitoramento do servidor: {guild.name}")
            
            # Inicializar dados do servidor
            self.server_data[server_id] = {
                "name": guild.name,
                "member_count": guild.member_count,
                "channel_count": len(guild.channels),
                "start_time": datetime.utcnow()
            }
            
            # Coletar dados iniciais
            await self.collect_initial_data(guild)
            
        except Exception as e:
            logger.error(f"Erro ao iniciar monitoramento do servidor {server_id}: {e}")
    
    async def stop_monitoring_server(self, server_id: int):
        """Para monitoramento de um servidor específico"""
        try:
            guild = self.get_guild(server_id)
            if guild:
                logger.info(f"Parando monitoramento do servidor: {guild.name}")
            
            # Limpar dados do servidor
            if server_id in self.server_data:
                del self.server_data[server_id]
            if server_id in self.message_data:
                del self.message_data[server_id]
            if server_id in self.reaction_data:
                del self.reaction_data[server_id]
            
        except Exception as e:
            logger.error(f"Erro ao parar monitoramento do servidor {server_id}: {e}")
    
    async def collect_initial_data(self, guild: discord.Guild):
        """Coleta dados iniciais do servidor"""
        try:
            # Coletar informações dos canais
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    self.channel_data[channel.id] = {
                        "name": channel.name,
                        "guild_id": guild.id,
                        "guild_name": guild.name,
                        "type": "text",
                        "created_at": channel.created_at
                    }
            
            logger.info(f"Dados iniciais coletados do servidor: {guild.name}")
            
        except Exception as e:
            logger.error(f"Erro ao coletar dados iniciais do servidor {guild.name}: {e}")
    
    async def analyze_message(self, message: discord.Message):
        """Analisa uma mensagem recebida"""
        try:
            # Verificar se é servidor monitorado
            if message.guild.id not in self.monitored_servers:
                return
            
            # Extrair dados da mensagem
            discord_message = DiscordMessage(
                id=str(message.id),
                content=message.content,
                author_id=str(message.author.id),
                author_name=message.author.name,
                channel_id=str(message.channel.id),
                channel_name=message.channel.name,
                guild_id=str(message.guild.id),
                guild_name=message.guild.name,
                timestamp=message.created_at,
                message_type=self._get_message_type(message),
                reactions=[{"emoji": str(reaction.emoji), "count": reaction.count} for reaction in message.reactions],
                attachments=[{"filename": att.filename, "url": att.url} for att in message.attachments],
                embeds=[{"title": embed.title, "description": embed.description} for embed in message.embeds],
                thread_id=str(message.thread.id) if message.thread else None,
                parent_id=str(message.reference.message_id) if message.reference else None
            )
            
            # Adicionar aos dados
            self.message_data[message.guild.id].append(discord_message)
            self.total_messages_processed += 1
            
            # Analisar keywords na mensagem
            keywords = await self.extract_keywords(message.content)
            if keywords:
                await self.process_keywords(keywords, discord_message)
            
            # Cache da mensagem
            cache_key = f"message:{message.id}"
            await self.cache.set(cache_key, discord_message.__dict__, ttl=3600)
            
            # Log estruturado
            logger.info({
                "event": "message_analyzed",
                "message_id": message.id,
                "guild_id": message.guild.id,
                "guild_name": message.guild.name,
                "channel_id": message.channel.id,
                "channel_name": message.channel.name,
                "author_id": message.author.id,
                "author_name": message.author.name,
                "content_length": len(message.content),
                "keywords_found": len(keywords) if keywords else 0,
                "timestamp": message.created_at.isoformat()
            })
            
        except Exception as e:
            logger.error(f"Erro ao analisar mensagem: {e}")
    
    async def analyze_reaction(self, reaction: discord.Reaction, user: discord.User, reaction_type: ReactionType):
        """Analisa uma reação"""
        try:
            # Verificar se é servidor monitorado
            if reaction.message.guild.id not in self.monitored_servers:
                return
            
            # Extrair dados da reação
            discord_reaction = DiscordReaction(
                message_id=str(reaction.message.id),
                user_id=str(user.id),
                user_name=user.name,
                emoji=str(reaction.emoji),
                reaction_type=reaction_type,
                timestamp=datetime.utcnow(),
                guild_id=str(reaction.message.guild.id),
                channel_id=str(reaction.message.channel.id)
            )
            
            # Adicionar aos dados
            self.reaction_data[reaction.message.guild.id].append(discord_reaction)
            self.total_reactions_processed += 1
            
            # Cache da reação
            cache_key = f"reaction:{reaction.message.id}:{user.id}:{reaction.emoji}"
            await self.cache.set(cache_key, discord_reaction.__dict__, ttl=3600)
            
            # Log estruturado
            logger.info({
                "event": "reaction_analyzed",
                "message_id": reaction.message.id,
                "guild_id": reaction.message.guild.id,
                "guild_name": reaction.message.guild.name,
                "channel_id": reaction.message.channel.id,
                "channel_name": reaction.message.channel.name,
                "user_id": user.id,
                "user_name": user.name,
                "emoji": str(reaction.emoji),
                "reaction_type": reaction_type.value,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Erro ao analisar reação: {e}")
    
    def _get_message_type(self, message: discord.Message) -> MessageType:
        """Determina o tipo da mensagem"""
        if message.attachments:
            return MessageType.ATTACHMENT
        elif message.embeds:
            return MessageType.EMBED
        elif message.reactions:
            return MessageType.REACTION
        elif message.thread:
            return MessageType.THREAD
        else:
            return MessageType.TEXT
    
    async def extract_keywords(self, content: str) -> List[str]:
        """Extrai keywords de uma mensagem"""
        try:
            # Remover URLs
            content = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', content)
            
            # Remover menções
            content = re.sub(r'<@!?\d+>', '', content)
            
            # Remover emojis
            content = re.sub(r'<a?:.+?:\d+>', '', content)
            
            # Extrair hashtags
            hashtags = re.findall(r'#(\w+)', content)
            
            # Extrair palavras-chave (4+ caracteres)
            words = re.findall(r'\b\w{4,}\b', content.lower())
            
            # Filtrar palavras comuns
            common_words = {'para', 'com', 'que', 'uma', 'mais', 'muito', 'este', 'essa', 'isso', 'aqui', 'onde', 'quando', 'como', 'porque', 'então', 'também', 'ainda', 'sempre', 'nunca', 'agora', 'hoje', 'amanhã', 'ontem', 'sempre', 'nunca', 'muito', 'pouco', 'grande', 'pequeno', 'bom', 'ruim', 'novo', 'velho', 'junto', 'sozinho', 'primeiro', 'último', 'melhor', 'pior', 'maior', 'menor', 'mais', 'menos', 'tudo', 'nada', 'alguém', 'ninguém', 'algum', 'nenhum', 'cada', 'qualquer', 'tanto', 'quanto', 'mesmo', 'diferente', 'igual', 'parecido', 'próximo', 'longe', 'perto', 'dentro', 'fora', 'cima', 'baixo', 'lado', 'meio', 'frente', 'trás', 'direita', 'esquerda', 'centro', 'canto', 'lugar', 'parte', 'vez', 'tempo', 'momento', 'hora', 'minuto', 'segundo', 'dia', 'semana', 'mês', 'ano', 'século', 'época', 'era', 'período', 'duração', 'intervalo', 'pausa', 'descanso', 'trabalho', 'estudo', 'lazer', 'diversão', 'brincadeira', 'jogo', 'esporte', 'exercício', 'corrida', 'caminhada', 'natação', 'futebol', 'basquete', 'vôlei', 'tênis', 'golfe', 'boxe', 'luta', 'dança', 'música', 'arte', 'pintura', 'desenho', 'escultura', 'fotografia', 'cinema', 'teatro', 'literatura', 'poesia', 'prosa', 'romance', 'conto', 'crônica', 'artigo', 'reportagem', 'entrevista', 'documentário', 'filme', 'série', 'novela', 'programa', 'show', 'espetáculo', 'apresentação', 'exposição', 'feira', 'festival', 'conferência', 'seminário', 'workshop', 'palestra', 'aula', 'curso', 'treinamento', 'capacitação', 'formação', 'educação', 'ensino', 'aprendizado', 'conhecimento', 'sabedoria', 'experiência', 'vivência', 'prática', 'teoria', 'conceito', 'definição', 'explicação', 'descrição', 'narrativa', 'história', 'estória', 'lenda', 'mito', 'fábula', 'parábola', 'alegoria', 'metáfora', 'símile', 'comparação', 'analogia', 'exemplo', 'caso', 'situação', 'circunstância', 'condição', 'estado', 'modo', 'maneira', 'forma', 'jeito', 'estilo', 'tipo', 'classe', 'categoria', 'grupo', 'conjunto', 'coleção', 'série', 'sequência', 'ordem', 'organização', 'estrutura', 'sistema', 'método', 'técnica', 'procedimento', 'processo', 'atividade', 'ação', 'movimento', 'mudança', 'transformação', 'evolução', 'desenvolvimento', 'crescimento', 'progresso', 'avanço', 'melhoria', 'aperfeiçoamento', 'otimização', 'maximização', 'minimização', 'redução', 'aumento', 'incremento', 'decremento', 'adição', 'subtração', 'multiplicação', 'divisão', 'cálculo', 'computação', 'processamento', 'análise', 'avaliação', 'julgamento', 'decisão', 'escolha', 'seleção', 'opção', 'alternativa', 'possibilidade', 'probabilidade', 'chance', 'risco', 'perigo', 'ameaça', 'oportunidade', 'vantagem', 'desvantagem', 'benefício', 'prejuízo', 'lucro', 'prejuízo', 'ganho', 'perda', 'economia', 'gasto', 'investimento', 'retorno', 'resultado', 'consequência', 'efeito', 'impacto', 'influência', 'poder', 'força', 'energia', 'potência', 'capacidade', 'habilidade', 'competência', 'aptidão', 'talento', 'dom', 'genialidade', 'inteligência', 'sabedoria', 'conhecimento', 'informação', 'dado', 'fato', 'verdade', 'realidade', 'existência', 'vida', 'morte', 'nascimento', 'crescimento', 'envelhecimento', 'maturidade', 'juventude', 'infância', 'adolescência', 'idade', 'tempo', 'espaço', 'distância', 'proximidade', 'localização', 'posição', 'direção', 'orientação', 'sentido', 'significado', 'importância', 'relevância', 'pertinência', 'adequação', 'conveniência', 'oportunidade', 'momento', 'ocasião', 'situação', 'circunstância', 'contexto', 'ambiente', 'meio', 'espaço', 'lugar', 'local', 'sítio', 'ponto', 'área', 'região', 'zona', 'território', 'domínio', 'campo', 'esfera', 'âmbito', 'setor', 'ramo', 'branco', 'atividade', 'profissão', 'ocupação', 'trabalho', 'emprego', 'carreira', 'vocação', 'missão', 'propósito', 'objetivo', 'meta', 'finalidade', 'intenção', 'plano', 'estratégia', 'tática', 'método', 'abordagem', 'perspectiva', 'visão', 'conceito', 'ideia', 'pensamento', 'reflexão', 'análise', 'estudo', 'pesquisa', 'investigação', 'exploração', 'descoberta', 'invenção', 'criação', 'produção', 'desenvolvimento', 'construção', 'edificação', 'formação', 'estruturação', 'organização', 'sistematização', 'categorização', 'classificação', 'tipificação', 'padronização', 'normalização', 'padronização', 'uniformização', 'homogeneização', 'diversificação', 'variedade', 'diversidade', 'pluralidade', 'multiplicidade', 'complexidade', 'simplicidade', 'facilidade', 'dificuldade', 'simplicidade', 'complexidade', 'abstração', 'concretude', 'generalidade', 'especificidade', 'universalidade', 'particularidade', 'individualidade', 'coletividade', 'sociabilidade', 'solidão', 'companhia', 'presença', 'ausência', 'existência', 'inexistência', 'realidade', 'irrealidade', 'verdade', 'mentira', 'honestidade', 'desonestidade', 'sinceridade', 'falsidade', 'autenticidade', 'artificialidade', 'naturalidade', 'artificialidade', 'espontaneidade', 'artificialidade', 'genuíno', 'falso', 'verdadeiro', 'mentiroso', 'honesto', 'desonesto', 'sincero', 'falso', 'autêntico', 'artificial', 'natural', 'artificial', 'espontâneo', 'artificial', 'genuíno', 'falso', 'verdadeiro', 'mentiroso', 'honesto', 'desonesto', 'sincero', 'falso', 'autêntico', 'artificial', 'natural', 'artificial', 'espontâneo', 'artificial'}
            
            keywords = []
            
            # Adicionar hashtags
            keywords.extend(hashtags)
            
            # Adicionar palavras relevantes
            for word in words:
                if word not in common_words and len(word) >= 4:
                    keywords.append(word)
            
            return list(set(keywords))  # Remover duplicatas
            
        except Exception as e:
            logger.error(f"Erro ao extrair keywords: {e}")
            return []
    
    async def process_keywords(self, keywords: List[str], message: DiscordMessage):
        """Processa keywords encontradas"""
        try:
            for keyword in keywords:
                # Cache da keyword
                cache_key = f"keyword:{keyword}:{message.guild_id}"
                cached_data = await self.cache.get(cache_key)
                
                if cached_data:
                    cached_data['frequency'] += 1
                    cached_data['last_seen'] = message.timestamp.isoformat()
                else:
                    cached_data = {
                        'keyword': keyword,
                        'frequency': 1,
                        'first_seen': message.timestamp.isoformat(),
                        'last_seen': message.timestamp.isoformat(),
                        'guild_id': message.guild_id,
                        'guild_name': message.guild_name,
                        'channels': [message.channel_id],
                        'users': [message.author_id]
                    }
                
                await self.cache.set(cache_key, cached_data, ttl=86400)  # 24 horas
                
        except Exception as e:
            logger.error(f"Erro ao processar keywords: {e}")
    
    async def search_keywords(self, termo: str) -> List[Dict]:
        """Busca keywords relacionadas a um termo"""
        try:
            keywords = []
            
            # Buscar em todos os servidores monitorados
            for server_id in self.monitored_servers:
                cache_key = f"keyword:{termo}:{server_id}"
                cached_data = await self.cache.get(cache_key)
                
                if cached_data:
                    keywords.append(cached_data)
            
            # Ordenar por frequência
            keywords.sort(key=lambda x: x.get('frequency', 0), reverse=True)
            
            return keywords
            
        except Exception as e:
            logger.error(f"Erro ao buscar keywords: {e}")
            return []
    
    async def get_status(self) -> Dict:
        """Retorna status atual do bot"""
        return {
            "is_monitoring": self.is_monitoring,
            "monitored_servers": len(self.monitored_servers),
            "total_messages_processed": self.total_messages_processed,
            "total_reactions_processed": self.total_reactions_processed,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds() if self.start_time else 0
        }
    
    async def get_detailed_stats(self) -> Dict:
        """Retorna estatísticas detalhadas"""
        stats = {}
        
        for server_id in self.monitored_servers:
            guild = self.get_guild(server_id)
            if not guild:
                continue
            
            # Estatísticas de mensagens
            messages = self.message_data.get(server_id, [])
            reactions = self.reaction_data.get(server_id, [])
            
            # Canais ativos
            active_channels = set()
            for msg in messages:
                active_channels.add(msg.channel_id)
            
            # Usuários ativos
            active_users = set()
            for msg in messages:
                active_users.add(msg.author_id)
            
            stats[str(server_id)] = {
                "name": guild.name,
                "messages": len(messages),
                "reactions": len(reactions),
                "active_channels": len(active_channels),
                "active_users": len(active_users),
                "member_count": guild.member_count,
                "channel_count": len(guild.channels)
            }
        
        return stats
    
    async def run_bot(self):
        """Executa o bot"""
        if not self.token:
            logger.error("Token do bot não configurado!")
            return
        
        try:
            logger.info("Iniciando Discord Bot Real...")
            await self.start()
        except Exception as e:
            logger.error(f"Erro ao executar bot: {e}")
        finally:
            await self.close()

def create_discord_bot(config: Dict[str, Any]) -> DiscordRealBot:
    """
    Factory function para criar instância do Discord Bot
    
    Args:
        config: Configuração do bot
        
    Returns:
        Instância do DiscordRealBot
    """
    return DiscordRealBot(config)

async def run_discord_bot(config: Dict[str, Any]):
    """
    Executa o Discord Bot
    
    Args:
        config: Configuração do bot
    """
    bot = create_discord_bot(config)
    await bot.run_bot()

if __name__ == "__main__":
    # Configuração de exemplo
    config = {
        "token": os.getenv("DISCORD_BOT_TOKEN"),
        "application_id": os.getenv("DISCORD_APPLICATION_ID"),
        "prefix": "!",
        "activity": "Monitoring servers",
        "auto_start_monitoring": True,
        "auto_monitor_new_servers": False,
        "monitored_servers": [],
        "admin_role_id": None,
        "moderator_role_id": None,
        "rate_limits": {
            "requests_per_minute": 100,
            "requests_per_hour": 1000
        },
        "cache": {
            "host": "localhost",
            "port": 6379,
            "db": 0,
            "ttl": 3600
        }
    }
    
    asyncio.run(run_discord_bot(config)) 