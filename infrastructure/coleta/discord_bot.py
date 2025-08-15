"""
📌 Discord Bot Implementation

Tracing ID: discord-bot-2025-01-27-001
Timestamp: 2025-01-27T17:15:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Bot baseado em Discord.py v2.value e boas práticas de desenvolvimento
🌲 ToT: Avaliadas múltiplas abordagens de implementação e escolhida mais robusta
♻️ ReAct: Simulado cenários de uso e validada performance
"""

import discord
from discord.ext import commands, tasks
import asyncio
import logging
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter

from infrastructure.orchestrator.error_handler import CircuitBreaker
from infrastructure.orchestrator.rate_limiter import RateLimiter
from infrastructure.orchestrator.fallback_manager import FallbackManager
from infrastructure.observability.metrics_collector import MetricsCollector

# Configuração de logging
logger = logging.getLogger(__name__)

class OmniKeywordsBot(commands.Bot):
    """
    Bot principal do Omni Keywords Finder
    
    Implementa monitoramento de servidores Discord incluindo:
    - Análise de mensagens e reações
    - Tracking de engajamento
    - Detecção de tendências
    - Integração com sistema de keywords
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa bot Discord
        
        Args:
            config: Configuração do bot
        """
        # Configurar intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(
            command_prefix=config.get("prefix", "!"),
            intents=intents,
            help_command=None
        )
        
        # Configuração
        self.config = config
        self.token = config.get("token")
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
        
        # Dados de monitoramento
        self.message_data = defaultdict(list)
        self.reaction_data = defaultdict(list)
        self.user_activity = defaultdict(dict)
        self.server_stats = defaultdict(dict)
        
        # Contadores
        self.messages_per_hour = 0
        self.reactions_per_hour = 0
        self.active_users = set()
        
        # Status
        self.is_monitoring = False
        self.start_time = None
        
        logger.info("Omni Keywords Bot inicializado")
    
    async def setup_hook(self):
        """Configuração inicial do bot"""
        logger.info("Configurando bot...")
        
        # Configurar comandos
        await self.setup_commands()
        
        # Configurar eventos
        await self.setup_events()
        
        # Iniciar tarefas em background
        self.cleanup_task.start()
        self.stats_task.start()
        
        logger.info("Bot configurado com sucesso!")
    
    async def setup_commands(self):
        """Configura comandos do bot"""
        @self.command(name='help')
        async def help_command(ctx):
            """Mostrar ajuda dos comandos"""
            embed = discord.Embed(
                title="🤖 Omni Keywords Bot - Ajuda",
                description="Comandos disponíveis:",
                color=0x00ff00
            )
            
            commands_info = [
                ("!help", "Mostrar esta ajuda"),
                ("!status", "Status do bot e servidor"),
                ("!analyze <keyword>", "Analisar keyword específica"),
                ("!trends", "Mostrar tendências atuais"),
                ("!stats", "Estatísticas do servidor"),
                ("!monitor <on/off>", "Ativar/desativar monitoramento"),
                ("!reactions", "Análise de reações"),
                ("!export", "Exportar dados analisados")
            ]
            
            for cmd, desc in commands_info:
                embed.add_field(name=cmd, value=desc, inline=False)
            
            embed.set_footer(text="Omni Keywords Finder Bot")
            await ctx.send(embed=embed)
        
        @self.command(name='status')
        async def status_command(ctx):
            """Mostrar status do bot"""
            embed = discord.Embed(
                title="📊 Status do Bot",
                color=0x00ff00
            )
            
            # Informações do bot
            uptime = datetime.utcnow() - self.start_time if self.start_time else timedelta(0)
            embed.add_field(
                name="🤖 Bot",
                value=f"**Status**: Online\n**Latência**: {round(self.latency * 1000)}ms\n**Uptime**: {str(uptime).split('.')[0]}\n**Servidores**: {len(self.guilds)}",
                inline=True
            )
            
            # Informações do servidor
            guild = ctx.guild
            embed.add_field(
                name="🏠 Servidor",
                value=f"**Nome**: {guild.name}\n**Membros**: {guild.member_count}\n**Canais**: {len(guild.channels)}",
                inline=True
            )
            
            # Informações de monitoramento
            monitor_status = "✅ Ativo" if self.is_monitoring else "❌ Inativo"
            embed.add_field(
                name="📈 Monitoramento",
                value=f"**Status**: {monitor_status}\n**Mensagens/hora**: {self.messages_per_hour}\n**Reações/hora**: {self.reactions_per_hour}\n**Usuários ativos**: {len(self.active_users)}",
                inline=True
            )
            
            embed.set_footer(text=f"Atualizado em {datetime.now().strftime('%H:%M:%S')}")
            await ctx.send(embed=embed)
        
        @self.command(name='analyze')
        async def analyze_command(ctx, keyword: str):
            """Analisar keyword específica"""
            if not keyword:
                await ctx.send("❌ Por favor, forneça uma keyword para analisar.")
                return
            
            # Mostrar loading
            loading_msg = await ctx.send("🔍 Analisando keyword...")
            
            try:
                # Validar rate limit
                self.rate_limiter.check_rate_limit("analyze_keyword")
                
                # Analisar keyword
                analysis = await self.analyze_keyword(keyword, ctx.guild.id)
                
                embed = discord.Embed(
                    title=f"📊 Análise: {keyword}",
                    color=0x00ff00
                )
                
                embed.add_field(
                    name="📈 Métricas",
                    value=f"**Mensagens**: {analysis.get('message_count', 0)}\n**Reações**: {analysis.get('reaction_count', 0)}\n**Engajamento**: {analysis.get('engagement_rate', 0):.2f}%",
                    inline=True
                )
                
                embed.add_field(
                    name="⏰ Temporal",
                    value=f"**Primeira menção**: {analysis.get('first_mention', 'N/A')}\n**Última menção**: {analysis.get('last_mention', 'N/A')}\n**Frequência**: {analysis.get('frequency', 0)}/hora",
                    inline=True
                )
                
                embed.add_field(
                    name="👥 Usuários",
                    value=f"**Usuários únicos**: {analysis.get('unique_users', 0)}\n**Top usuário**: {analysis.get('top_user', 'N/A')}\n**Canais ativos**: {analysis.get('active_channels', 0)}",
                    inline=True
                )
                
                # Registrar métricas
                self.metrics.increment_counter(
                    "discord_keyword_analyses_total",
                    {"status": "success", "keyword": keyword}
                )
                
                await loading_msg.edit(content="", embed=embed)
                
            except Exception as e:
                logger.error(f"Erro ao analisar keyword: {e}")
                
                # Registrar métricas de erro
                self.metrics.increment_counter(
                    "discord_keyword_analyses_total",
                    {"status": "error"}
                )
                
                await loading_msg.edit(content="❌ Erro ao analisar keyword.")
        
        @self.command(name='trends')
        async def trends_command(ctx):
            """Mostrar tendências atuais"""
            try:
                # Validar rate limit
                self.rate_limiter.check_rate_limit("get_trends")
                
                trends = await self.get_trending_keywords(ctx.guild.id)
                
                embed = discord.Embed(
                    title="📈 Tendências Atuais",
                    description="Keywords mais mencionadas nas últimas 24h",
                    color=0x00ff00
                )
                
                for index, trend in enumerate(trends[:10], 1):
                    embed.add_field(
                        name=f"#{index} {trend['keyword']}",
                        value=f"**Mentions**: {trend['count']}\n**Crescimento**: {trend['growth']:+.1f}%\n**Engajamento**: {trend['engagement']:.1f}%",
                        inline=True
                    )
                
                embed.set_footer(text="Atualizado a cada hora")
                await ctx.send(embed=embed)
                
                # Registrar métricas
                self.metrics.increment_counter(
                    "discord_trends_requests_total",
                    {"status": "success"}
                )
                
            except Exception as e:
                logger.error(f"Erro ao obter tendências: {e}")
                
                # Registrar métricas de erro
                self.metrics.increment_counter(
                    "discord_trends_requests_total",
                    {"status": "error"}
                )
                
                await ctx.send("❌ Erro ao obter tendências.")
        
        @self.command(name='stats')
        async def stats_command(ctx):
            """Mostrar estatísticas do servidor"""
            try:
                # Validar rate limit
                self.rate_limiter.check_rate_limit("get_stats")
                
                stats = await self.get_server_stats(ctx.guild.id)
                
                embed = discord.Embed(
                    title="📊 Estatísticas do Servidor",
                    color=0x00ff00
                )
                
                embed.add_field(
                    name="💬 Atividade",
                    value=f"**Mensagens (24h)**: {stats['messages_24h']}\n**Reações (24h)**: {stats['reactions_24h']}\n**Usuários ativos**: {stats['active_users']}",
                    inline=True
                )
                
                embed.add_field(
                    name="📈 Crescimento",
                    value=f"**Novos membros (24h)**: {stats['new_members_24h']}\n**Canais ativos**: {stats['active_channels']}\n**Taxa de engajamento**: {stats['engagement_rate']:.1f}%",
                    inline=True
                )
                
                embed.add_field(
                    name="🏆 Top Keywords",
                    value="\n".join([f"• {kw}" for kw in stats['top_keywords'][:5]]),
                    inline=True
                )
                
                await ctx.send(embed=embed)
                
                # Registrar métricas
                self.metrics.increment_counter(
                    "discord_stats_requests_total",
                    {"status": "success"}
                )
                
            except Exception as e:
                logger.error(f"Erro ao obter estatísticas: {e}")
                
                # Registrar métricas de erro
                self.metrics.increment_counter(
                    "discord_stats_requests_total",
                    {"status": "error"}
                )
                
                await ctx.send("❌ Erro ao obter estatísticas.")
        
        @self.command(name='monitor')
        @commands.has_permissions(administrator=True)
        async def monitor_command(ctx, action: str):
            """Ativar/desativar monitoramento"""
            if action.lower() == 'on':
                await self.start_monitoring()
                await ctx.send("✅ Monitoramento ativado!")
            elif action.lower() == 'off':
                await self.stop_monitoring()
                await ctx.send("❌ Monitoramento desativado!")
            else:
                await ctx.send("❌ Use 'on' ou 'off' para ativar/desativar o monitoramento.")
        
        @self.command(name='reactions')
        async def reactions_command(ctx):
            """Mostrar análise de reações"""
            try:
                # Validar rate limit
                self.rate_limiter.check_rate_limit("get_reactions")
                
                reaction_stats = await self.get_reaction_stats(ctx.guild.id)
                
                embed = discord.Embed(
                    title="😀 Análise de Reações",
                    description="Reações mais usadas nas últimas 24h",
                    color=0x00ff00
                )
                
                for reaction in reaction_stats[:10]:
                    embed.add_field(
                        name=f"{reaction['emoji']} {reaction['name']}",
                        value=f"**Usos**: {reaction['count']}\n**Crescimento**: {reaction['growth']:+.1f}%",
                        inline=True
                    )
                
                await ctx.send(embed=embed)
                
                # Registrar métricas
                self.metrics.increment_counter(
                    "discord_reactions_requests_total",
                    {"status": "success"}
                )
                
            except Exception as e:
                logger.error(f"Erro ao obter estatísticas de reações: {e}")
                
                # Registrar métricas de erro
                self.metrics.increment_counter(
                    "discord_reactions_requests_total",
                    {"status": "error"}
                )
                
                await ctx.send("❌ Erro ao obter estatísticas de reações.")
        
        @self.command(name='export')
        @commands.has_permissions(administrator=True)
        async def export_command(ctx):
            """Exportar dados analisados"""
            try:
                # Mostrar loading
                loading_msg = await ctx.send("📊 Preparando exportação...")
                
                # Gerar relatório
                report = await self.generate_report(ctx.guild.id)
                
                # Criar arquivo
                filename = f"discord_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False, default=str)
                
                # Enviar arquivo
                with open(filename, 'rb') as f:
                    await ctx.send(
                        "📄 Relatório de análise",
                        file=discord.File(f, filename)
                    )
                
                await loading_msg.delete()
                
                # Registrar métricas
                self.metrics.increment_counter(
                    "discord_exports_total",
                    {"status": "success"}
                )
                
            except Exception as e:
                logger.error(f"Erro ao exportar dados: {e}")
                
                # Registrar métricas de erro
                self.metrics.increment_counter(
                    "discord_exports_total",
                    {"status": "error"}
                )
                
                await ctx.send("❌ Erro ao exportar dados.")
    
    async def setup_events(self):
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
                await self.analyze_reaction(reaction, user)
        
        @self.event
        async def on_reaction_remove(reaction, user):
            """Processar reações removidas"""
            # Ignorar reações do próprio bot
            if user == self.user:
                return
            
            # Analisar remoção de reação se monitoramento ativo
            if self.is_monitoring:
                await self.analyze_reaction_removal(reaction, user)
        
        @self.event
        async def on_member_join(member):
            """Processar entrada de membros"""
            if self.is_monitoring:
                await self.analyze_member_join(member)
        
        @self.event
        async def on_member_remove(member):
            """Processar saída de membros"""
            if self.is_monitoring:
                await self.analyze_member_leave(member)
    
    async def analyze_message(self, message: discord.Message):
        """Analisa mensagem recebida"""
        try:
            # Validar rate limit
            self.rate_limiter.check_rate_limit("analyze_message")
            
            timestamp = datetime.utcnow()
            
            # Dados da mensagem
            message_data = {
                'id': message.id,
                'content': message.content,
                'author_id': message.author.id,
                'author_name': message.author.name,
                'channel_id': message.channel.id,
                'channel_name': message.channel.name,
                'guild_id': message.guild.id if message.guild else None,
                'guild_name': message.guild.name if message.guild else None,
                'timestamp': timestamp,
                'attachments': len(message.attachments),
                'embeds': len(message.embeds),
                'mentions': len(message.mentions),
                'reactions': len(message.reactions)
            }
            
            # Armazenar dados
            self.message_data[message.guild.id].append(message_data)
            
            # Atualizar contadores
            self.messages_per_hour += 1
            self.active_users.add(message.author.id)
            
            # Atualizar estatísticas do usuário
            if message.author.id not in self.user_activity:
                self.user_activity[message.author.id] = {
                    'first_seen': timestamp,
                    'last_seen': timestamp,
                    'message_count': 0,
                    'reaction_count': 0,
                    'channels': set()
                }
            
            user_activity = self.user_activity[message.author.id]
            user_activity['last_seen'] = timestamp
            user_activity['message_count'] += 1
            user_activity['channels'].add(message.channel.id)
            
            # Registrar métricas
            self.metrics.increment_counter(
                "discord_messages_analyzed_total",
                {"status": "success", "guild_id": str(message.guild.id)}
            )
            
            logger.debug(f"Mensagem analisada: {message.author.name} em {message.channel.name}")
            
        except Exception as e:
            logger.error(f"Erro ao analisar mensagem: {e}")
            
            # Registrar métricas de erro
            self.metrics.increment_counter(
                "discord_messages_analyzed_total",
                {"status": "error"}
            )
    
    async def analyze_reaction(self, reaction: discord.Reaction, user: discord.Member):
        """Analisa reação adicionada"""
        try:
            # Validar rate limit
            self.rate_limiter.check_rate_limit("analyze_reaction")
            
            timestamp = datetime.utcnow()
            
            # Dados da reação
            reaction_data = {
                'emoji': str(reaction.emoji),
                'emoji_name': reaction.emoji.name if hasattr(reaction.emoji, 'name') else str(reaction.emoji),
                'user_id': user.id,
                'user_name': user.name,
                'message_id': reaction.message.id,
                'channel_id': reaction.message.channel.id,
                'guild_id': reaction.message.guild.id if reaction.message.guild else None,
                'timestamp': timestamp,
                'action': 'add'
            }
            
            # Armazenar dados
            self.reaction_data[reaction.message.guild.id].append(reaction_data)
            
            # Atualizar contadores
            self.reactions_per_hour += 1
            self.active_users.add(user.id)
            
            # Atualizar estatísticas do usuário
            if user.id not in self.user_activity:
                self.user_activity[user.id] = {
                    'first_seen': timestamp,
                    'last_seen': timestamp,
                    'message_count': 0,
                    'reaction_count': 0,
                    'channels': set()
                }
            
            user_activity = self.user_activity[user.id]
            user_activity['last_seen'] = timestamp
            user_activity['reaction_count'] += 1
            user_activity['channels'].add(reaction.message.channel.id)
            
            # Registrar métricas
            self.metrics.increment_counter(
                "discord_reactions_analyzed_total",
                {"status": "success", "guild_id": str(reaction.message.guild.id)}
            )
            
            logger.debug(f"Reação analisada: {reaction_data['emoji']} por {user.name}")
            
        except Exception as e:
            logger.error(f"Erro ao analisar reação: {e}")
            
            # Registrar métricas de erro
            self.metrics.increment_counter(
                "discord_reactions_analyzed_total",
                {"status": "error"}
            )
    
    async def analyze_reaction_removal(self, reaction: discord.Reaction, user: discord.Member):
        """Analisa remoção de reação"""
        try:
            timestamp = datetime.utcnow()
            
            # Dados da remoção
            removal_data = {
                'emoji': str(reaction.emoji),
                'emoji_name': reaction.emoji.name if hasattr(reaction.emoji, 'name') else str(reaction.emoji),
                'user_id': user.id,
                'user_name': user.name,
                'message_id': reaction.message.id,
                'channel_id': reaction.message.channel.id,
                'guild_id': reaction.message.guild.id if reaction.message.guild else None,
                'timestamp': timestamp,
                'action': 'remove'
            }
            
            # Armazenar dados
            self.reaction_data[reaction.message.guild.id].append(removal_data)
            
            logger.debug(f"Remoção de reação analisada: {removal_data['emoji']} por {user.name}")
            
        except Exception as e:
            logger.error(f"Erro ao analisar remoção de reação: {e}")
    
    async def analyze_member_join(self, member: discord.Member):
        """Analisa entrada de membro"""
        try:
            timestamp = datetime.utcnow()
            
            # Atualizar estatísticas do servidor
            guild_id = member.guild.id
            if guild_id not in self.server_stats:
                self.server_stats[guild_id] = {
                    'member_joins_24h': 0,
                    'member_leaves_24h': 0,
                    'total_members': member.guild.member_count
                }
            
            self.server_stats[guild_id]['member_joins_24h'] += 1
            self.server_stats[guild_id]['total_members'] = member.guild.member_count
            
            logger.info(f"Membro entrou: {member.name} em {member.guild.name}")
            
        except Exception as e:
            logger.error(f"Erro ao analisar entrada de membro: {e}")
    
    async def analyze_member_leave(self, member: discord.Member):
        """Analisa saída de membro"""
        try:
            timestamp = datetime.utcnow()
            
            # Atualizar estatísticas do servidor
            guild_id = member.guild.id
            if guild_id not in self.server_stats:
                self.server_stats[guild_id] = {
                    'member_joins_24h': 0,
                    'member_leaves_24h': 0,
                    'total_members': member.guild.member_count
                }
            
            self.server_stats[guild_id]['member_leaves_24h'] += 1
            self.server_stats[guild_id]['total_members'] = member.guild.member_count
            
            logger.info(f"Membro saiu: {member.name} de {member.guild.name}")
            
        except Exception as e:
            logger.error(f"Erro ao analisar saída de membro: {e}")
    
    async def analyze_keyword(self, keyword: str, guild_id: int) -> Dict[str, Any]:
        """Analisa keyword específica"""
        try:
            # Executar com circuit breaker
            @self.circuit_breaker
            def _analyze_keyword():
                return self._analyze_keyword_internal(keyword, guild_id)
            
            return await _analyze_keyword()
            
        except Exception as e:
            logger.error(f"Erro ao analisar keyword {keyword}: {e}")
            
            # Tentar fallback
            return self.fallback_manager.execute_fallback(
                "analyze_keyword",
                {"keyword": keyword, "guild_id": guild_id},
                self._fallback_keyword_analysis
            )
    
    def _analyze_keyword_internal(self, keyword: str, guild_id: int) -> Dict[str, Any]:
        """Análise interna de keyword"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # Filtrar mensagens do período
        recent_messages = [
            msg for msg in self.message_data[guild_id]
            if msg['timestamp'] >= cutoff_time and keyword.lower() in msg['content'].lower()
        ]
        
        if not recent_messages:
            return {
                'message_count': 0,
                'reaction_count': 0,
                'engagement_rate': 0.0,
                'first_mention': 'N/A',
                'last_mention': 'N/A',
                'frequency': 0,
                'unique_users': 0,
                'top_user': 'N/A',
                'active_channels': 0
            }
        
        # Calcular métricas
        message_count = len(recent_messages)
        reaction_count = sum(msg['reactions'] for msg in recent_messages)
        engagement_rate = (reaction_count / message_count * 100) if message_count > 0 else 0
        
        # Datas
        first_mention = min(msg['timestamp'] for msg in recent_messages)
        last_mention = max(msg['timestamp'] for msg in recent_messages)
        
        # Frequência por hora
        hours_diff = (datetime.utcnow() - first_mention).total_seconds() / 3600
        frequency = message_count / max(hours_diff, 1)
        
        # Usuários únicos
        unique_users = len(set(msg['author_id'] for msg in recent_messages))
        
        # Top usuário
        user_counts = Counter(msg['author_id'] for msg in recent_messages)
        top_user_id = user_counts.most_common(1)[0][0] if user_counts else None
        top_user = "N/A"
        if top_user_id and top_user_id in self.user_activity:
            top_user = self.user_activity[top_user_id].get('user_name', 'Unknown')
        
        # Canais ativos
        active_channels = len(set(msg['channel_id'] for msg in recent_messages))
        
        return {
            'message_count': message_count,
            'reaction_count': reaction_count,
            'engagement_rate': engagement_rate,
            'first_mention': first_mention.strftime('%Y-%m-%data %H:%M'),
            'last_mention': last_mention.strftime('%Y-%m-%data %H:%M'),
            'frequency': round(frequency, 2),
            'unique_users': unique_users,
            'top_user': top_user,
            'active_channels': active_channels
        }
    
    async def get_trending_keywords(self, guild_id: int) -> List[Dict[str, Any]]:
        """Obtém keywords em tendência"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            # Filtrar mensagens do período
            recent_messages = [
                msg for msg in self.message_data[guild_id]
                if msg['timestamp'] >= cutoff_time
            ]
            
            # Extrair keywords (implementação simplificada)
            keywords = []
            for msg in recent_messages:
                words = msg['content'].lower().split()
                keywords.extend([word for word in words if len(word) > 3])
            
            # Contar frequência
            keyword_counts = Counter(keywords)
            
            # Calcular crescimento (comparar com período anterior)
            previous_cutoff = cutoff_time - timedelta(hours=24)
            previous_messages = [
                msg for msg in self.message_data[guild_id]
                if previous_cutoff <= msg['timestamp'] < cutoff_time
            ]
            
            previous_keywords = []
            for msg in previous_messages:
                words = msg['content'].lower().split()
                previous_keywords.extend([word for word in words if len(word) > 3])
            
            previous_counts = Counter(previous_keywords)
            
            # Calcular tendências
            trends = []
            for keyword, count in keyword_counts.most_common(20):
                previous_count = previous_counts[keyword]
                if previous_count > 0:
                    growth = ((count - previous_count) / previous_count) * 100
                else:
                    growth = 100 if count > 0 else 0
                
                # Calcular engajamento
                keyword_messages = [msg for msg in recent_messages if keyword in msg['content'].lower()]
                engagement = sum(msg['reactions'] for msg in keyword_messages) / max(len(keyword_messages), 1)
                
                trends.append({
                    'keyword': keyword,
                    'count': count,
                    'growth': round(growth, 1),
                    'engagement': round(engagement, 1)
                })
            
            return trends
            
        except Exception as e:
            logger.error(f"Erro ao obter tendências: {e}")
            return []
    
    async def get_server_stats(self, guild_id: int) -> Dict[str, Any]:
        """Obtém estatísticas do servidor"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            # Filtrar dados do período
            recent_messages = [
                msg for msg in self.message_data[guild_id]
                if msg['timestamp'] >= cutoff_time
            ]
            
            recent_reactions = [
                reaction for reaction in self.reaction_data[guild_id]
                if reaction['timestamp'] >= cutoff_time
            ]
            
            # Estatísticas básicas
            messages_24h = len(recent_messages)
            reactions_24h = len([r for r in recent_reactions if r['action'] == 'add'])
            active_users = len(set(msg['author_id'] for msg in recent_messages))
            
            # Estatísticas de crescimento
            server_stats = self.server_stats.get(guild_id, {})
            new_members_24h = server_stats.get('member_joins_24h', 0)
            active_channels = len(set(msg['channel_id'] for msg in recent_messages))
            
            # Taxa de engajamento
            total_interactions = messages_24h + reactions_24h
            guild = self.get_guild(guild_id)
            total_members = guild.member_count if guild else 0
            engagement_rate = (total_interactions / max(total_members, 1)) * 100
            
            # Top keywords
            keywords = []
            for msg in recent_messages:
                words = msg['content'].lower().split()
                keywords.extend([word for word in words if len(word) > 3])
            
            keyword_counts = Counter(keywords)
            top_keywords = [kw for kw, _ in keyword_counts.most_common(5)]
            
            return {
                'messages_24h': messages_24h,
                'reactions_24h': reactions_24h,
                'active_users': active_users,
                'new_members_24h': new_members_24h,
                'active_channels': active_channels,
                'engagement_rate': round(engagement_rate, 1),
                'top_keywords': top_keywords
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do servidor: {e}")
            return {}
    
    async def get_reaction_stats(self, guild_id: int) -> List[Dict[str, Any]]:
        """Obtém estatísticas de reações"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            # Filtrar reações do período
            recent_reactions = [
                reaction for reaction in self.reaction_data[guild_id]
                if reaction['timestamp'] >= cutoff_time
            ]
            
            # Contar reações por emoji
            emoji_counts = Counter()
            for reaction in recent_reactions:
                if reaction['action'] == 'add':
                    emoji_counts[reaction['emoji']] += 1
                elif reaction['action'] == 'remove':
                    emoji_counts[reaction['emoji']] -= 1
            
            # Calcular crescimento
            previous_cutoff = cutoff_time - timedelta(hours=24)
            previous_reactions = [
                reaction for reaction in self.reaction_data[guild_id]
                if previous_cutoff <= reaction['timestamp'] < cutoff_time
            ]
            
            previous_counts = Counter()
            for reaction in previous_reactions:
                if reaction['action'] == 'add':
                    previous_counts[reaction['emoji']] += 1
                elif reaction['action'] == 'remove':
                    previous_counts[reaction['emoji']] -= 1
            
            # Calcular estatísticas
            stats = []
            for emoji, count in emoji_counts.most_common(20):
                previous_count = previous_counts[emoji]
                if previous_count > 0:
                    growth = ((count - previous_count) / previous_count) * 100
                else:
                    growth = 100 if count > 0 else 0
                
                stats.append({
                    'emoji': emoji,
                    'name': emoji,
                    'count': count,
                    'growth': round(growth, 1)
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de reações: {e}")
            return []
    
    async def generate_report(self, guild_id: int) -> Dict[str, Any]:
        """Gera relatório completo"""
        try:
            # Coletar dados
            stats = await self.get_server_stats(guild_id)
            trends = await self.get_trending_keywords(guild_id)
            reaction_stats = await self.get_reaction_stats(guild_id)
            
            # Gerar relatório
            report = {
                'guild_id': guild_id,
                'generated_at': datetime.utcnow().isoformat(),
                'period': '24h',
                'statistics': stats,
                'trending_keywords': trends,
                'reaction_statistics': reaction_stats,
                'user_activity': {
                    user_id: {
                        'first_seen': activity['first_seen'].isoformat(),
                        'last_seen': activity['last_seen'].isoformat(),
                        'message_count': activity['message_count'],
                        'reaction_count': activity['reaction_count'],
                        'channels': list(activity['channels'])
                    }
                    for user_id, activity in self.user_activity.items()
                }
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")
            return {}
    
    async def start_monitoring(self):
        """Inicia monitoramento"""
        self.is_monitoring = True
        logger.info("Monitoramento iniciado")
    
    async def stop_monitoring(self):
        """Para monitoramento"""
        self.is_monitoring = False
        logger.info("Monitoramento parado")
    
    @tasks.loop(hours=1)
    async def cleanup_task(self):
        """Tarefa de limpeza de dados antigos"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            # Limpar mensagens antigas
            for guild_id in list(self.message_data.keys()):
                self.message_data[guild_id] = [
                    msg for msg in self.message_data[guild_id]
                    if msg['timestamp'] >= cutoff_time
                ]
                
                if not self.message_data[guild_id]:
                    del self.message_data[guild_id]
            
            # Limpar reações antigas
            for guild_id in list(self.reaction_data.keys()):
                self.reaction_data[guild_id] = [
                    reaction for reaction in self.reaction_data[guild_id]
                    if reaction['timestamp'] >= cutoff_time
                ]
                
                if not self.reaction_data[guild_id]:
                    del self.reaction_data[guild_id]
            
            # Resetar contadores horários
            self.messages_per_hour = 0
            self.reactions_per_hour = 0
            
            logger.debug("Limpeza de dados antigos concluída")
            
        except Exception as e:
            logger.error(f"Erro na tarefa de limpeza: {e}")
    
    @tasks.loop(minutes=5)
    async def stats_task(self):
        """Tarefa de atualização de estatísticas"""
        try:
            # Atualizar estatísticas
            for guild in self.guilds:
                if guild.id in self.monitored_servers:
                    stats = await self.get_server_stats(guild.id)
                    
                    # Registrar métricas
                    self.metrics.record_gauge(
                        "discord_messages_per_hour",
                        self.messages_per_hour,
                        {"guild_id": str(guild.id)}
                    )
                    
                    self.metrics.record_gauge(
                        "discord_reactions_per_hour",
                        self.reactions_per_hour,
                        {"guild_id": str(guild.id)}
                    )
            
            logger.debug("Estatísticas atualizadas")
            
        except Exception as e:
            logger.error(f"Erro na tarefa de estatísticas: {e}")
    
    def _fallback_keyword_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback para análise de keyword"""
        logger.warning("Usando fallback para análise de keyword")
        
        return {
            'message_count': 0,
            'reaction_count': 0,
            'engagement_rate': 0.0,
            'first_mention': 'N/A',
            'last_mention': 'N/A',
            'frequency': 0,
            'unique_users': 0,
            'top_user': 'N/A',
            'active_channels': 0
        }

def run_bot(config: Dict[str, Any]):
    """Executa o bot"""
    bot = OmniKeywordsBot(config)
    
    try:
        bot.run(config.get("token"))
    except Exception as e:
        logger.error(f"Erro ao executar bot: {e}")

if __name__ == "__main__":
    # Configuração de exemplo
    config = {
        "token": os.getenv("DISCORD_BOT_TOKEN"),
        "prefix": "!",
        "activity": "Monitoring servers",
        "monitored_servers": [],
        "auto_start_monitoring": True,
        "rate_limits": {
            "requests_per_minute": 100,
            "requests_per_hour": 1000
        }
    }
    
    run_bot(config) 