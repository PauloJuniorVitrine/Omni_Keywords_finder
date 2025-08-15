# 📌 Discord Bot Setup Guide

**Tracing ID**: `discord-setup-2025-01-27-001`  
**Timestamp**: 2025-01-27T17:00:00Z  
**Versão**: 1.0  
**Status**: 🚀 **IMPLEMENTAÇÃO**

---

## 📋 **RESUMO EXECUTIVO**

### **Objetivo**
Configurar e implementar Discord Bot para integração com o sistema Omni Keywords Finder, permitindo monitoramento de servidores, análise de mensagens e tracking de reações.

### **Funcionalidades Principais**
- Monitoramento de servidores Discord
- Análise de mensagens e reações
- Tracking de engajamento
- Integração com sistema de keywords
- Alertas e notificações

### **Requisitos Técnicos**
- Python 3.8+
- Discord.py library
- Tokens de API Discord
- Permissões adequadas no servidor

---

## 🧭 **METODOLOGIAS DE RACIOCÍNIO OBRIGATÓRIAS**

### **📐 CoCoT (Comprovação, Causalidade, Contexto, Tendência)**

#### **Comprovação**
- Baseado em documentação oficial do Discord Developer Portal
- Seguindo boas práticas de segurança para bots
- Validado com exemplos reais de implementação

#### **Causalidade**
- Cada configuração tem propósito específico
- Permissões são justificadas por funcionalidade
- Integração segue padrões estabelecidos

#### **Contexto**
- Alinhado com objetivos do sistema Omni Keywords Finder
- Considera restrições de rate limiting do Discord
- Adaptado para ambiente de produção

#### **Tendência**
- Usando Discord.py v2.x (versão mais recente)
- Implementando features modernas do Discord
- Preparado para futuras atualizações da API

### **🌲 ToT (Tree of Thought)**

#### **Múltiplas Abordagens**
- Avaliação de diferentes tipos de bot (User Bot vs Application Bot)
- Comparação de estratégias de monitoramento
- Análise de trade-offs entre funcionalidades

#### **Avaliação de Caminhos**
- Escolha da abordagem mais segura e eficiente
- Balanceamento entre funcionalidade e performance
- Consideração de limitações da API

### **♻️ ReAct – Simulação e Reflexão**

#### **Simulação de Impacto**
- Teste de funcionalidades em ambiente de desenvolvimento
- Validação de rate limits e performance
- Verificação de segurança e privacidade

---

## 🚀 **FASE 1: SETUP DO DISCORD DEVELOPER PORTAL**

### **1.1 Criar Aplicação Discord**

#### **Passo 1: Acessar Discord Developer Portal**
1. Acesse: https://discord.com/developers/applications
2. Faça login com sua conta Discord
3. Clique em "New Application"

#### **Passo 2: Configurar Aplicação**
```yaml
Nome da Aplicação: Omni Keywords Finder Bot
Descrição: Bot para análise de keywords e monitoramento de servidores
Icone: [Upload ícone personalizado]
```

#### **Passo 3: Obter Credenciais**
- **Application ID**: Copie o ID da aplicação
- **Public Key**: Mantenha para validação de webhooks
- **Bot Token**: Será gerado na próxima etapa

### **1.2 Configurar Bot**

#### **Passo 1: Criar Bot**
1. No menu lateral, clique em "Bot"
2. Clique em "Add Bot"
3. Confirme a criação

#### **Passo 2: Configurar Bot**
```yaml
Username: Omni Keywords Bot
Avatar: [Upload avatar personalizado]
Public Bot: ✅ Habilitado
Require OAuth2 Code Grant: ❌ Desabilitado
```

#### **Passo 3: Configurar Permissões**
```yaml
# Permissões Essenciais
Read Messages/View Channels: ✅
Send Messages: ✅
Read Message History: ✅
Add Reactions: ✅
Use External Emojis: ✅
Attach Files: ✅
Embed Links: ✅

# Permissões de Monitoramento
View Server Insights: ✅
View Audit Log: ✅

# Permissões de Moderação (Opcional)
Manage Messages: ❌
Kick Members: ❌
Ban Members: ❌
```

### **1.3 Configurar OAuth2**

#### **Passo 1: Configurar Scopes**
```yaml
Scopes:
  - bot
  - applications.commands
```

#### **Passo 2: Configurar Permissões**
```yaml
Bot Permissions:
  - Read Messages/View Channels
  - Send Messages
  - Read Message History
  - Add Reactions
  - Use External Emojis
  - Attach Files
  - Embed Links
  - View Server Insights
  - View Audit Log
```

#### **Passo 3: Gerar URL de Convite**
```yaml
URL de Convite: https://discord.com/api/oauth2/authorize?client_id=YOUR_APP_ID&permissions=PERMISSION_BITS&scope=bot%20applications.commands
```

---

## 🔧 **FASE 2: CONFIGURAÇÃO DO AMBIENTE**

### **2.1 Instalar Dependências**

#### **Requirements**
```txt
discord.py>=2.3.0
aiohttp>=3.8.0
python-dotenv>=1.0.0
asyncio-mqtt>=0.11.0
```

#### **Comando de Instalação**
```bash
pip install discord.py aiohttp python-dotenv asyncio-mqtt
```

### **2.2 Configurar Variáveis de Ambiente**

#### **Arquivo .env**
```env
# Discord Bot Configuration
DISCORD_BOT_TOKEN=your_bot_token_here
DISCORD_APPLICATION_ID=your_application_id_here
DISCORD_PUBLIC_KEY=your_public_key_here

# Bot Configuration
BOT_PREFIX=!
BOT_STATUS=Analyzing keywords...
BOT_ACTIVITY=Monitoring servers

# Server Configuration
MONITORED_SERVERS=server_id_1,server_id_2
ADMIN_ROLE_ID=admin_role_id
MODERATOR_ROLE_ID=moderator_role_id

# Database Configuration
DATABASE_URL=sqlite:///discord_bot.db

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/discord_bot.log

# Rate Limiting
MAX_MESSAGES_PER_MINUTE=100
MAX_REACTIONS_PER_MINUTE=50
```

### **2.3 Configurar Estrutura de Pastas**

#### **Estrutura de Diretórios**
```
infrastructure/coleta/discord/
├── __init__.py
├── discord_bot.py
├── discord_reaction_analyzer.py
├── discord_message_analyzer.py
├── discord_server_monitor.py
├── discord_commands.py
├── discord_events.py
└── discord_utils.py
```

---

## 🤖 **FASE 3: IMPLEMENTAÇÃO DO BOT**

### **3.1 Configuração Básica do Bot**

#### **Arquivo: discord_bot.py**
```python
"""
Discord Bot Implementation

Tracing ID: discord-bot-2025-01-27-001
Timestamp: 2025-01-27T17:00:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO
"""

import discord
from discord.ext import commands
import asyncio
import logging
import os
from dotenv import load_dotenv

from .discord_commands import setup_commands
from .discord_events import setup_events
from .discord_server_monitor import ServerMonitor
from .discord_reaction_analyzer import ReactionAnalyzer
from .discord_message_analyzer import MessageAnalyzer

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OmniKeywordsBot(commands.Bot):
    """
    Bot principal do Omni Keywords Finder
    """
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(
            command_prefix=os.getenv('BOT_PREFIX', '!'),
            intents=intents,
            help_command=None
        )
        
        # Inicializar componentes
        self.server_monitor = ServerMonitor(self)
        self.reaction_analyzer = ReactionAnalyzer(self)
        self.message_analyzer = MessageAnalyzer(self)
        
        # Configurar eventos e comandos
        setup_events(self)
        setup_commands(self)
    
    async def setup_hook(self):
        """Configuração inicial do bot"""
        logger.info("Configurando bot...")
        
        # Inicializar componentes
        await self.server_monitor.initialize()
        await self.reaction_analyzer.initialize()
        await self.message_analyzer.initialize()
        
        logger.info("Bot configurado com sucesso!")
    
    async def on_ready(self):
        """Evento executado quando o bot está pronto"""
        logger.info(f'Bot conectado como {self.user.name}')
        
        # Configurar status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=os.getenv('BOT_ACTIVITY', 'Monitoring servers')
        )
        await self.change_presence(activity=activity)
        
        # Iniciar monitoramento
        await self.server_monitor.start_monitoring()
    
    async def on_message(self, message):
        """Processar mensagens recebidas"""
        # Ignorar mensagens do próprio bot
        if message.author == self.user:
            return
        
        # Analisar mensagem
        await self.message_analyzer.analyze_message(message)
        
        # Processar comandos
        await self.process_commands(message)
    
    async def on_reaction_add(self, reaction, user):
        """Processar reações adicionadas"""
        # Ignorar reações do próprio bot
        if user == self.user:
            return
        
        # Analisar reação
        await self.reaction_analyzer.analyze_reaction(reaction, user)
    
    async def on_reaction_remove(self, reaction, user):
        """Processar reações removidas"""
        # Ignorar reações do próprio bot
        if user == self.user:
            return
        
        # Analisar remoção de reação
        await self.reaction_analyzer.analyze_reaction_removal(reaction, user)

def run_bot():
    """Executar o bot"""
    load_dotenv()
    
    bot = OmniKeywordsBot()
    token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not token:
        logger.error("Token do bot não configurado!")
        return
    
    try:
        bot.run(token)
    except Exception as e:
        logger.error(f"Erro ao executar bot: {e}")

if __name__ == "__main__":
    run_bot()
```

### **3.2 Implementar Comandos**

#### **Arquivo: discord_commands.py**
```python
"""
Comandos do Discord Bot

Tracing ID: discord-commands-2025-01-27-001
Timestamp: 2025-01-27T17:00:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO
"""

import discord
from discord.ext import commands
import logging
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def setup_commands(bot):
    """Configurar comandos do bot"""
    
    @bot.command(name='help')
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
    
    @bot.command(name='status')
    async def status_command(ctx):
        """Mostrar status do bot"""
        embed = discord.Embed(
            title="📊 Status do Bot",
            color=0x00ff00
        )
        
        # Informações do bot
        embed.add_field(
            name="🤖 Bot",
            value=f"**Status**: Online\n**Latência**: {round(bot.latency * 1000)}ms\n**Servidores**: {len(bot.guilds)}",
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
        monitor_status = "✅ Ativo" if bot.server_monitor.is_monitoring else "❌ Inativo"
        embed.add_field(
            name="📈 Monitoramento",
            value=f"**Status**: {monitor_status}\n**Mensagens/hora**: {bot.message_analyzer.messages_per_hour}\n**Reações/hora**: {bot.reaction_analyzer.reactions_per_hour}",
            inline=True
        )
        
        embed.set_footer(text=f"Atualizado em {datetime.now().strftime('%H:%M:%S')}")
        await ctx.send(embed=embed)
    
    @bot.command(name='analyze')
    async def analyze_command(ctx, keyword: str):
        """Analisar keyword específica"""
        if not keyword:
            await ctx.send("❌ Por favor, forneça uma keyword para analisar.")
            return
        
        # Mostrar loading
        loading_msg = await ctx.send("🔍 Analisando keyword...")
        
        try:
            # Analisar keyword
            analysis = await bot.message_analyzer.analyze_keyword(keyword)
            
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
            
            await loading_msg.edit(content="", embed=embed)
            
        except Exception as e:
            logger.error(f"Erro ao analisar keyword: {e}")
            await loading_msg.edit(content="❌ Erro ao analisar keyword.")
    
    @bot.command(name='trends')
    async def trends_command(ctx):
        """Mostrar tendências atuais"""
        try:
            trends = await bot.message_analyzer.get_trending_keywords()
            
            embed = discord.Embed(
                title="📈 Tendências Atuais",
                description="Keywords mais mencionadas nas últimas 24h",
                color=0x00ff00
            )
            
            for i, trend in enumerate(trends[:10], 1):
                embed.add_field(
                    name=f"#{i} {trend['keyword']}",
                    value=f"**Mentions**: {trend['count']}\n**Crescimento**: {trend['growth']:+.1f}%\n**Engajamento**: {trend['engagement']:.1f}%",
                    inline=True
                )
            
            embed.set_footer(text="Atualizado a cada hora")
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro ao obter tendências: {e}")
            await ctx.send("❌ Erro ao obter tendências.")
    
    @bot.command(name='stats')
    async def stats_command(ctx):
        """Mostrar estatísticas do servidor"""
        try:
            stats = await bot.server_monitor.get_server_stats()
            
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
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            await ctx.send("❌ Erro ao obter estatísticas.")
    
    @bot.command(name='monitor')
    @commands.has_permissions(administrator=True)
    async def monitor_command(ctx, action: str):
        """Ativar/desativar monitoramento"""
        if action.lower() == 'on':
            await bot.server_monitor.start_monitoring()
            await ctx.send("✅ Monitoramento ativado!")
        elif action.lower() == 'off':
            await bot.server_monitor.stop_monitoring()
            await ctx.send("❌ Monitoramento desativado!")
        else:
            await ctx.send("❌ Use 'on' ou 'off' para ativar/desativar o monitoramento.")
    
    @bot.command(name='reactions')
    async def reactions_command(ctx):
        """Mostrar análise de reações"""
        try:
            reaction_stats = await bot.reaction_analyzer.get_reaction_stats()
            
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
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de reações: {e}")
            await ctx.send("❌ Erro ao obter estatísticas de reações.")
    
    @bot.command(name='export')
    @commands.has_permissions(administrator=True)
    async def export_command(ctx):
        """Exportar dados analisados"""
        try:
            # Mostrar loading
            loading_msg = await ctx.send("📊 Preparando exportação...")
            
            # Gerar relatório
            report = await bot.server_monitor.generate_report()
            
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
            
        except Exception as e:
            logger.error(f"Erro ao exportar dados: {e}")
            await ctx.send("❌ Erro ao exportar dados.")
```

### **3.3 Implementar Análise de Reações**

#### **Arquivo: discord_reaction_analyzer.py**
```python
"""
Analisador de Reações Discord

Tracing ID: discord-reactions-2025-01-27-001
Timestamp: 2025-01-27T17:00:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO
"""

import discord
import logging
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class ReactionAnalyzer:
    """
    Analisador de reações Discord
    
    Implementa análise avançada de reações incluindo:
    - Tracking de reações por emoji
    - Análise de padrões temporais
    - Detecção de tendências
    - Métricas de engajamento
    """
    
    def __init__(self, bot):
        """Inicializa analisador de reações"""
        self.bot = bot
        self.reaction_data = defaultdict(list)
        self.reaction_stats = defaultdict(int)
        self.reactions_per_hour = 0
        self.last_hour_reactions = 0
        self.hourly_stats = defaultdict(int)
        
        # Configurações
        self.track_emojis = True
        self.track_users = True
        self.track_timing = True
        self.max_history_hours = 24
        
        logger.info("ReactionAnalyzer inicializado")
    
    async def initialize(self):
        """Inicialização assíncrona"""
        logger.info("Inicializando ReactionAnalyzer...")
        
        # Carregar dados históricos se disponível
        await self.load_historical_data()
        
        logger.info("ReactionAnalyzer inicializado com sucesso!")
    
    async def analyze_reaction(self, reaction: discord.Reaction, user: discord.Member):
        """Analisa reação adicionada"""
        try:
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
            
            # Atualizar estatísticas
            self.reaction_stats[reaction_data['emoji']] += 1
            self.reactions_per_hour += 1
            self.hourly_stats[timestamp.hour] += 1
            
            # Limpar dados antigos
            await self.cleanup_old_data()
            
            # Log da reação
            logger.debug(f"Reação adicionada: {reaction_data['emoji']} por {user.name}")
            
        except Exception as e:
            logger.error(f"Erro ao analisar reação: {e}")
    
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
            
            # Atualizar estatísticas
            self.reaction_stats[removal_data['emoji']] -= 1
            self.reactions_per_hour -= 1
            
            logger.debug(f"Reação removida: {removal_data['emoji']} por {user.name}")
            
        except Exception as e:
            logger.error(f"Erro ao analisar remoção de reação: {e}")
    
    async def get_reaction_stats(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Obtém estatísticas de reações"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Filtrar reações do período
            recent_reactions = []
            for guild_reactions in self.reaction_data.values():
                for reaction in guild_reactions:
                    if reaction['timestamp'] >= cutoff_time:
                        recent_reactions.append(reaction)
            
            # Contar reações por emoji
            emoji_counts = Counter()
            for reaction in recent_reactions:
                if reaction['action'] == 'add':
                    emoji_counts[reaction['emoji']] += 1
                elif reaction['action'] == 'remove':
                    emoji_counts[reaction['emoji']] -= 1
            
            # Calcular crescimento
            previous_cutoff = cutoff_time - timedelta(hours=hours)
            previous_reactions = []
            for guild_reactions in self.reaction_data.values():
                for reaction in guild_reactions:
                    if previous_cutoff <= reaction['timestamp'] < cutoff_time:
                        previous_reactions.append(reaction)
            
            previous_counts = Counter()
            for reaction in previous_reactions:
                if reaction['action'] == 'add':
                    previous_counts[reaction['emoji']] += 1
                elif reaction['action'] == 'remove':
                    previous_counts[reaction['emoji']] -= 1
            
            # Calcular crescimento percentual
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
                    'growth': growth
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de reações: {e}")
            return []
    
    async def get_user_reaction_stats(self, user_id: int, hours: int = 24) -> Dict[str, Any]:
        """Obtém estatísticas de reações de um usuário"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            user_reactions = []
            for guild_reactions in self.reaction_data.values():
                for reaction in guild_reactions:
                    if (reaction['user_id'] == user_id and 
                        reaction['timestamp'] >= cutoff_time):
                        user_reactions.append(reaction)
            
            # Estatísticas do usuário
            stats = {
                'total_reactions': len([r for r in user_reactions if r['action'] == 'add']),
                'total_removals': len([r for r in user_reactions if r['action'] == 'remove']),
                'favorite_emojis': Counter(),
                'active_hours': Counter(),
                'active_channels': set()
            }
            
            for reaction in user_reactions:
                if reaction['action'] == 'add':
                    stats['favorite_emojis'][reaction['emoji']] += 1
                stats['active_hours'][reaction['timestamp'].hour] += 1
                stats['active_channels'].add(reaction['channel_id'])
            
            # Converter para lista
            stats['favorite_emojis'] = dict(stats['favorite_emojis'].most_common(5))
            stats['active_hours'] = dict(stats['active_hours'])
            stats['active_channels'] = len(stats['active_channels'])
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do usuário: {e}")
            return {}
    
    async def get_temporal_patterns(self, hours: int = 24) -> Dict[str, Any]:
        """Obtém padrões temporais de reações"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Filtrar reações do período
            recent_reactions = []
            for guild_reactions in self.reaction_data.values():
                for reaction in guild_reactions:
                    if reaction['timestamp'] >= cutoff_time:
                        recent_reactions.append(reaction)
            
            # Padrões por hora
            hourly_patterns = defaultdict(int)
            for reaction in recent_reactions:
                if reaction['action'] == 'add':
                    hourly_patterns[reaction['timestamp'].hour] += 1
            
            # Padrões por dia da semana
            daily_patterns = defaultdict(int)
            for reaction in recent_reactions:
                if reaction['action'] == 'add':
                    daily_patterns[reaction['timestamp'].weekday()] += 1
            
            # Encontrar picos de atividade
            peak_hour = max(hourly_patterns.items(), key=lambda x: x[1])[0] if hourly_patterns else 0
            peak_day = max(daily_patterns.items(), key=lambda x: x[1])[0] if daily_patterns else 0
            
            return {
                'hourly_patterns': dict(hourly_patterns),
                'daily_patterns': dict(daily_patterns),
                'peak_hour': peak_hour,
                'peak_day': peak_day,
                'total_reactions': sum(hourly_patterns.values())
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter padrões temporais: {e}")
            return {}
    
    async def detect_reaction_trends(self) -> List[Dict[str, Any]]:
        """Detecta tendências em reações"""
        try:
            # Comparar períodos
            current_stats = await self.get_reaction_stats(6)  # Últimas 6 horas
            previous_stats = await self.get_reaction_stats(12)  # 6-12 horas atrás
            
            trends = []
            
            for current in current_stats:
                emoji = current['emoji']
                current_count = current['count']
                
                # Encontrar estatísticas anteriores
                previous_count = 0
                for prev in previous_stats:
                    if prev['emoji'] == emoji:
                        previous_count = prev['count']
                        break
                
                # Calcular tendência
                if previous_count > 0:
                    growth_rate = ((current_count - previous_count) / previous_count) * 100
                else:
                    growth_rate = 100 if current_count > 0 else 0
                
                # Classificar tendência
                if growth_rate > 50:
                    trend_type = "🔥 Crescendo Rapidamente"
                elif growth_rate > 20:
                    trend_type = "📈 Crescendo"
                elif growth_rate > -20:
                    trend_type = "➡️ Estável"
                else:
                    trend_type = "📉 Declinando"
                
                trends.append({
                    'emoji': emoji,
                    'name': emoji,
                    'current_count': current_count,
                    'previous_count': previous_count,
                    'growth_rate': growth_rate,
                    'trend_type': trend_type
                })
            
            # Ordenar por taxa de crescimento
            trends.sort(key=lambda x: x['growth_rate'], reverse=True)
            
            return trends[:10]  # Top 10 tendências
            
        except Exception as e:
            logger.error(f"Erro ao detectar tendências: {e}")
            return []
    
    async def cleanup_old_data(self):
        """Remove dados antigos"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=self.max_history_hours)
            
            for guild_id in list(self.reaction_data.keys()):
                self.reaction_data[guild_id] = [
                    reaction for reaction in self.reaction_data[guild_id]
                    if reaction['timestamp'] >= cutoff_time
                ]
                
                # Remover guilds vazios
                if not self.reaction_data[guild_id]:
                    del self.reaction_data[guild_id]
            
        except Exception as e:
            logger.error(f"Erro ao limpar dados antigos: {e}")
    
    async def load_historical_data(self):
        """Carrega dados históricos"""
        # Implementar carregamento de dados históricos se necessário
        pass
    
    async def save_data(self):
        """Salva dados em arquivo"""
        # Implementar salvamento de dados se necessário
        pass
```

---

## 📊 **FASE 4: TESTES E VALIDAÇÃO**

### **4.1 Testes de Funcionalidade**

#### **Testes Básicos**
```python
# Testar conexão do bot
# Testar comandos básicos
# Testar análise de reações
# Testar monitoramento de servidor
```

### **4.2 Testes de Performance**

#### **Testes de Carga**
```python
# Testar com múltiplas reações simultâneas
# Testar com alto volume de mensagens
# Testar rate limiting
```

### **4.3 Testes de Segurança**

#### **Validação de Permissões**
```python
# Verificar permissões mínimas necessárias
# Testar acesso restrito
# Validar proteção de dados
```

---

## 🔧 **FASE 5: DEPLOYMENT E MONITORAMENTO**

### **5.1 Configuração de Produção**

#### **Variáveis de Ambiente**
```env
# Produção
DISCORD_BOT_TOKEN=production_token_here
LOG_LEVEL=WARNING
DATABASE_URL=postgresql://user:pass@host:port/db
```

### **5.2 Monitoramento**

#### **Métricas a Monitorar**
- Latência do bot
- Taxa de reações por hora
- Uso de memória
- Erros de API
- Disponibilidade

### **5.3 Backup e Recuperação**

#### **Estratégia de Backup**
- Backup diário dos dados
- Configuração versionada
- Plano de recuperação

---

## 📝 **NOTAS DE IMPLEMENTAÇÃO**

### **Considerações de Segurança**
- Token do bot deve ser mantido seguro
- Permissões mínimas necessárias
- Logs não devem conter dados sensíveis
- Rate limiting para evitar spam

### **Considerações de Performance**
- Cache de dados frequentes
- Limpeza periódica de dados antigos
- Otimização de queries
- Monitoramento de recursos

### **Considerações de Privacidade**
- Respeitar configurações de privacidade do servidor
- Não coletar dados pessoais desnecessários
- Permitir opt-out de monitoramento
- Conformidade com GDPR

---

## 🔄 **ATUALIZAÇÕES E MANUTENÇÃO**

### **Atualizações Regulares**
- Manter Discord.py atualizado
- Monitorar mudanças na API Discord
- Atualizar dependências de segurança
- Revisar permissões periodicamente

### **Manutenção**
- Limpeza de logs antigos
- Otimização de performance
- Correção de bugs
- Melhorias de funcionalidade

---

**Documento criado em**: 2025-01-27T17:00:00Z  
**Próxima revisão**: Após implementação completa  
**Responsável**: Equipe de Desenvolvimento  
**Versão**: 1.0 