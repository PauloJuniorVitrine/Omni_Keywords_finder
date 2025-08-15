"""
Exemplo Prático - Sistema de Notificações Avançado
==================================================

Demonstração completa do uso do sistema de notificações avançado
com múltiplos canais, templates e cenários reais.

Tracing ID: NOTIF_20241219_001
Autor: Sistema de Notificações Avançado
Data: 2024-12-19
Versão: 1.0.0
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importa classes do sistema de notificações
from infrastructure.notifications.avancado.notification_manager import (
    NotificationManager,
    Notification,
    NotificationType,
    NotificationChannel,
    NotificationPriority,
    NotificationTemplate,
    NotificationPreferences,
    create_notification
)


class NotificationSystemExample:
    """Exemplo prático do sistema de notificações."""
    
    def __init__(self):
        """Inicializa o exemplo."""
        self.redis_client = None  # Simulado para o exemplo
        self.config = self._get_config()
        self.notification_manager = NotificationManager(self.redis_client, self.config)
        
        # Inicializa templates e configurações
        self._setup_templates()
        self._setup_user_preferences()
    
    def _get_config(self) -> Dict[str, Any]:
        """Retorna configuração para o exemplo."""
        return {
            "smtp": {
                "server": "smtp.gmail.com",
                "port": 587,
                "username": "user@gmail.com",
                "password": "app_password",
                "use_tls": True,
                "from_email": "noreply@omnikeywords.com",
                "from_name": "Omni Keywords Finder"
            },
            "slack": {
                "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
                "channel": "#notifications"
            },
            "sms": {
                "api_key": "your_sms_api_key",
                "api_secret": "your_sms_api_secret"
            }
        }
    
    def _setup_templates(self):
        """Configura templates de notificação."""
        
        # Template para execução concluída
        execucao_success = NotificationTemplate(
            name="execucao_sucesso",
            subject="✅ Execução {{execucao_id}} concluída com sucesso!",
            content="""
            <h2>Execução Concluída</h2>
            <p>Olá <strong>{{user_name}}</strong>,</p>
            <p>A execução <strong>{{execucao_id}}</strong> foi concluída com sucesso!</p>
            
            <h3>📊 Resultados:</h3>
            <ul>
                <li><strong>Keywords encontradas:</strong> {{keywords_count}}</li>
                <li><strong>Tempo de execução:</strong> {{tempo_execucao}}</li>
                <li><strong>Blog analisado:</strong> {{blog_url}}</li>
                <li><strong>Data de início:</strong> {{data_inicio}}</li>
                <li><strong>Data de conclusão:</strong> {{data_conclusao}}</li>
            </ul>
            
            <p><a href="{{dashboard_url}}" style="background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Ver no Dashboard</a></p>
            
            <p>Obrigado por usar o Omni Keywords Finder!</p>
            """,
            variables=["user_name", "execucao_id", "keywords_count", "tempo_execucao", "blog_url", "data_inicio", "data_conclusao", "dashboard_url"],
            channel=NotificationChannel.EMAIL
        )
        
        # Template para erro na execução
        execucao_error = NotificationTemplate(
            name="execucao_erro",
            subject="❌ Erro na execução {{execucao_id}}",
            content="""
            <h2>Erro na Execução</h2>
            <p>Olá <strong>{{user_name}}</strong>,</p>
            <p>A execução <strong>{{execucao_id}}</strong> falhou.</p>
            
            <h3>🚨 Detalhes do Erro:</h3>
            <div style="background: #ffebee; padding: 15px; border-left: 4px solid #f44336;">
                <strong>Erro:</strong> {{error_message}}<br>
                <strong>Código:</strong> {{error_code}}<br>
                <strong>Timestamp:</strong> {{timestamp}}
            </div>
            
            <h3>🔧 Ações Recomendadas:</h3>
            <ul>
                <li>Verifique se a URL do blog está acessível</li>
                <li>Confirme se o site não está bloqueando requisições</li>
                <li>Tente executar novamente em alguns minutos</li>
                <li>Entre em contato com o suporte se o problema persistir</li>
            </ul>
            
            <p><a href="{{dashboard_url}}" style="background: #f44336; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Ver no Dashboard</a></p>
            """,
            variables=["user_name", "execucao_id", "error_message", "error_code", "timestamp", "dashboard_url"],
            channel=NotificationChannel.EMAIL
        )
        
        # Template para relatório semanal
        relatorio_semanal = NotificationTemplate(
            name="relatorio_semanal",
            subject="📊 Relatório Semanal - {{periodo}}",
            content="""
            <h2>Relatório Semanal</h2>
            <p>Olá <strong>{{user_name}}</strong>,</p>
            <p>Aqui está seu relatório semanal de atividades:</p>
            
            <h3>📈 Estatísticas Gerais:</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div style="background: #e8f5e8; padding: 15px; border-radius: 5px;">
                    <strong>Execuções realizadas:</strong><br>
                    <span style="font-size: 24px; color: #4CAF50;">{{execucoes_count}}</span>
                </div>
                <div style="background: #e8f5e8; padding: 15px; border-radius: 5px;">
                    <strong>Keywords encontradas:</strong><br>
                    <span style="font-size: 24px; color: #4CAF50;">{{keywords_total}}</span>
                </div>
                <div style="background: #e8f5e8; padding: 15px; border-radius: 5px;">
                    <strong>Tempo total:</strong><br>
                    <span style="font-size: 24px; color: #4CAF50;">{{tempo_total}}</span>
                </div>
                <div style="background: #e8f5e8; padding: 15px; border-radius: 5px;">
                    <strong>Taxa de sucesso:</strong><br>
                    <span style="font-size: 24px; color: #4CAF50;">{{taxa_sucesso}}%</span>
                </div>
            </div>
            
            <h3>🏆 Top Keywords da Semana:</h3>
            <ol>
                {% for keyword in top_keywords %}
                <li><strong>{{keyword.termo}}</strong> - {{keyword.volume}} buscas/mês</li>
                {% endfor %}
            </ol>
            
            <h3>📊 Performance:</h3>
            <ul>
                <li><strong>Tempo médio por execução:</strong> {{tempo_medio}}</li>
                <li><strong>Execuções com erro:</strong> {{execucoes_erro}}</li>
                <li><strong>Blogs mais analisados:</strong> {{blogs_populares}}</li>
            </ul>
            
            <p><a href="{{dashboard_url}}" style="background: #2196F3; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Ver Dashboard Completo</a></p>
            """,
            variables=["user_name", "periodo", "execucoes_count", "keywords_total", "tempo_total", "taxa_sucesso", "top_keywords", "tempo_medio", "execucoes_erro", "blogs_populares", "dashboard_url"],
            channel=NotificationChannel.EMAIL
        )
        
        # Template para alerta de sistema
        sistema_alerta = NotificationTemplate(
            name="sistema_alerta",
            subject="🚨 Alerta do Sistema - {{alerta_titulo}}",
            content="""
            <h2>Alerta do Sistema</h2>
            <p><strong>{{alerta_titulo}}</strong></p>
            
            <div style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107;">
                <p><strong>Descrição:</strong> {{alerta_mensagem}}</p>
                <p><strong>Severidade:</strong> {{severidade}}</p>
                <p><strong>Componente:</strong> {{componente}}</p>
                <p><strong>Timestamp:</strong> {{timestamp}}</p>
            </div>
            
            <h3>🔧 Ações Automáticas:</h3>
            <ul>
                {% for acao in acoes_automaticas %}
                <li>{{acao}}</li>
                {% endfor %}
            </ul>
            
            <h3>👥 Equipe Notificada:</h3>
            <ul>
                {% for membro in equipe %}
                <li>{{membro.nome}} ({{membro.cargo}})</li>
                {% endfor %}
            </ul>
            
            <p><a href="{{dashboard_url}}" style="background: #ffc107; color: black; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Ver Dashboard</a></p>
            """,
            variables=["alerta_titulo", "alerta_mensagem", "severidade", "componente", "timestamp", "acoes_automaticas", "equipe", "dashboard_url"],
            channel=NotificationChannel.EMAIL
        )
        
        # Adiciona templates
        self.notification_manager.create_template(execucao_success)
        self.notification_manager.create_template(execucao_error)
        self.notification_manager.create_template(relatorio_semanal)
        self.notification_manager.create_template(sistema_alerta)
        
        logger.info("Templates configurados com sucesso")
    
    def _setup_user_preferences(self):
        """Configura preferências de usuário."""
        
        # Preferências para usuário padrão
        default_preferences = NotificationPreferences(
            user_id="user_default",
            channels={
                NotificationChannel.WEBSOCKET: True,
                NotificationChannel.EMAIL: True,
                NotificationChannel.SLACK: False,
                NotificationChannel.SMS: False
            },
            types={
                NotificationType.INFO: True,
                NotificationType.SUCCESS: True,
                NotificationType.WARNING: True,
                NotificationType.ERROR: True,
                NotificationType.CRITICAL: True
            },
            quiet_hours={"start": "22:00", "end": "08:00"},
            frequency_limit=20
        )
        
        # Preferências para usuário premium
        premium_preferences = NotificationPreferences(
            user_id="user_premium",
            channels={
                NotificationChannel.WEBSOCKET: True,
                NotificationChannel.EMAIL: True,
                NotificationChannel.SLACK: True,
                NotificationChannel.SMS: True
            },
            types={
                NotificationType.INFO: True,
                NotificationType.SUCCESS: True,
                NotificationType.WARNING: True,
                NotificationType.ERROR: True,
                NotificationType.CRITICAL: True
            },
            quiet_hours={"start": "23:00", "end": "07:00"},
            frequency_limit=50
        )
        
        # Preferências para usuário noturno
        night_preferences = NotificationPreferences(
            user_id="user_night",
            channels={
                NotificationChannel.WEBSOCKET: True,
                NotificationChannel.EMAIL: False,
                NotificationChannel.SLACK: True,
                NotificationChannel.SMS: True
            },
            types={
                NotificationType.INFO: False,
                NotificationType.SUCCESS: True,
                NotificationType.WARNING: True,
                NotificationType.ERROR: True,
                NotificationType.CRITICAL: True
            },
            quiet_hours={},  # Sem horário silencioso
            frequency_limit=30
        )
        
        # Adiciona preferências
        self.notification_manager.preferences["user_default"] = default_preferences
        self.notification_manager.preferences["user_premium"] = premium_preferences
        self.notification_manager.preferences["user_night"] = night_preferences
        
        logger.info("Preferências de usuário configuradas")
    
    async def exemplo_execucao_sucesso(self):
        """Exemplo de notificação de execução bem-sucedida."""
        logger.info("=== Exemplo: Execução Bem-sucedida ===")
        
        # Dados da execução
        execucao_data = {
            "user_name": "João Silva",
            "execucao_id": "EXEC_20241219_001",
            "keywords_count": "1,247",
            "tempo_execucao": "3m 45s",
            "blog_url": "https://exemplo.com/blog",
            "data_inicio": "2024-12-19 14:30:00",
            "data_conclusao": "2024-12-19 14:33:45",
            "dashboard_url": "https://dashboard.omnikeywords.com/execucoes/EXEC_20241219_001"
        }
        
        # Cria notificação usando template
        notification = self.notification_manager.render_template("execucao_sucesso", execucao_data)
        notification.user_id = "user_premium"
        notification.channels = [NotificationChannel.WEBSOCKET, NotificationChannel.EMAIL, NotificationChannel.SLACK]
        notification.type = NotificationType.SUCCESS
        notification.priority = NotificationPriority.NORMAL
        
        # Envia notificação
        result = await self.notification_manager.send_notification(notification)
        
        if result:
            logger.info("✅ Notificação de execução bem-sucedida enviada!")
        else:
            logger.error("❌ Falha ao enviar notificação de execução")
    
    async def exemplo_execucao_erro(self):
        """Exemplo de notificação de erro na execução."""
        logger.info("=== Exemplo: Erro na Execução ===")
        
        # Dados do erro
        error_data = {
            "user_name": "Maria Santos",
            "execucao_id": "EXEC_20241219_002",
            "error_message": "Timeout ao acessar o blog. O site pode estar sobrecarregado ou inacessível.",
            "error_code": "TIMEOUT_001",
            "timestamp": datetime.now().strftime("%Y-%m-%data %H:%M:%S"),
            "dashboard_url": "https://dashboard.omnikeywords.com/execucoes/EXEC_20241219_002"
        }
        
        # Cria notificação usando template
        notification = self.notification_manager.render_template("execucao_erro", error_data)
        notification.user_id = "user_default"
        notification.channels = [NotificationChannel.WEBSOCKET, NotificationChannel.EMAIL]
        notification.type = NotificationType.ERROR
        notification.priority = NotificationPriority.HIGH
        
        # Envia notificação
        result = await self.notification_manager.send_notification(notification)
        
        if result:
            logger.info("✅ Notificação de erro enviada!")
        else:
            logger.error("❌ Falha ao enviar notificação de erro")
    
    async def exemplo_relatorio_semanal(self):
        """Exemplo de notificação de relatório semanal."""
        logger.info("=== Exemplo: Relatório Semanal ===")
        
        # Dados do relatório
        relatorio_data = {
            "user_name": "Carlos Oliveira",
            "periodo": "13-19 Dezembro 2024",
            "execucoes_count": "15",
            "keywords_total": "18,432",
            "tempo_total": "2h 15m",
            "taxa_sucesso": "93.3",
            "top_keywords": [
                {"termo": "marketing digital", "volume": "12,500"},
                {"termo": "seo otimização", "volume": "8,900"},
                {"termo": "conteúdo marketing", "volume": "7,200"},
                {"termo": "google ads", "volume": "6,800"},
                {"termo": "redes sociais", "volume": "5,400"}
            ],
            "tempo_medio": "9m 12s",
            "execucoes_erro": "1",
            "blogs_populares": "techblog.com, marketingpro.com, seoexpert.com",
            "dashboard_url": "https://dashboard.omnikeywords.com/relatorios/semanal"
        }
        
        # Cria notificação usando template
        notification = self.notification_manager.render_template("relatorio_semanal", relatorio_data)
        notification.user_id = "user_premium"
        notification.channels = [NotificationChannel.EMAIL, NotificationChannel.SLACK]
        notification.type = NotificationType.INFO
        notification.priority = NotificationPriority.NORMAL
        
        # Envia notificação
        result = await self.notification_manager.send_notification(notification)
        
        if result:
            logger.info("✅ Relatório semanal enviado!")
        else:
            logger.error("❌ Falha ao enviar relatório semanal")
    
    async def exemplo_sistema_alerta(self):
        """Exemplo de notificação de alerta do sistema."""
        logger.info("=== Exemplo: Alerta do Sistema ===")
        
        # Dados do alerta
        alerta_data = {
            "alerta_titulo": "Alta Utilização de CPU",
            "alerta_mensagem": "O servidor de processamento está com utilização de CPU acima de 90% há mais de 10 minutos.",
            "severidade": "MÉDIA",
            "componente": "Processamento de Keywords",
            "timestamp": datetime.now().strftime("%Y-%m-%data %H:%M:%S"),
            "acoes_automaticas": [
                "Escalado automaticamente para 2 instâncias adicionais",
                "Redistribuído carga entre servidores",
                "Notificado equipe de infraestrutura"
            ],
            "equipe": [
                {"nome": "Ana Silva", "cargo": "DevOps Engineer"},
                {"nome": "Pedro Costa", "cargo": "System Administrator"},
                {"nome": "Lucas Santos", "cargo": "Tech Lead"}
            ],
            "dashboard_url": "https://dashboard.omnikeywords.com/monitoramento"
        }
        
        # Cria notificação usando template
        notification = self.notification_manager.render_template("sistema_alerta", alerta_data)
        notification.user_id = "user_night"
        notification.channels = [NotificationChannel.WEBSOCKET, NotificationChannel.SLACK, NotificationChannel.SMS]
        notification.type = NotificationType.WARNING
        notification.priority = NotificationPriority.HIGH
        
        # Envia notificação
        result = await self.notification_manager.send_notification(notification)
        
        if result:
            logger.info("✅ Alerta do sistema enviado!")
        else:
            logger.error("❌ Falha ao enviar alerta do sistema")
    
    async def exemplo_notificacao_simples(self):
        """Exemplo de notificação simples sem template."""
        logger.info("=== Exemplo: Notificação Simples ===")
        
        # Cria notificação simples
        notification = create_notification(
            user_id="user_default",
            subject="Bem-vindo ao Omni Keywords Finder!",
            content="Sua conta foi ativada com sucesso. Comece a usar nossa plataforma para encontrar as melhores keywords para seu negócio.",
            notification_type=NotificationType.SUCCESS,
            priority=NotificationPriority.NORMAL,
            channels=[NotificationChannel.WEBSOCKET, NotificationChannel.EMAIL]
        )
        
        # Envia notificação
        result = await self.notification_manager.send_notification(notification)
        
        if result:
            logger.info("✅ Notificação simples enviada!")
        else:
            logger.error("❌ Falha ao enviar notificação simples")
    
    async def exemplo_rate_limiting(self):
        """Exemplo de rate limiting."""
        logger.info("=== Exemplo: Rate Limiting ===")
        
        # Tenta enviar múltiplas notificações rapidamente
        for index in range(25):
            notification = create_notification(
                user_id="user_default",
                subject=f"Teste Rate Limit {index+1}",
                content=f"Esta é a notificação de teste número {index+1}",
                channels=[NotificationChannel.WEBSOCKET]
            )
            
            result = await self.notification_manager.send_notification(notification)
            
            if result:
                logger.info(f"✅ Notificação {index+1} enviada")
            else:
                logger.warning(f"⚠️ Notificação {index+1} bloqueada por rate limit")
                break
    
    async def exemplo_metricas(self):
        """Exemplo de obtenção de métricas."""
        logger.info("=== Exemplo: Métricas do Sistema ===")
        
        # Obtém métricas
        metrics = self.notification_manager.get_metrics()
        
        logger.info("📊 Métricas do Sistema de Notificações:")
        for key, value in metrics.items():
            logger.info(f"  {key}: {value}")
    
    async def executar_exemplos(self):
        """Executa todos os exemplos."""
        logger.info("🚀 Iniciando exemplos do Sistema de Notificações Avançado")
        logger.info("=" * 60)
        
        try:
            # Executa exemplos
            await self.exemplo_notificacao_simples()
            await asyncio.sleep(1)
            
            await self.exemplo_execucao_sucesso()
            await asyncio.sleep(1)
            
            await self.exemplo_execucao_erro()
            await asyncio.sleep(1)
            
            await self.exemplo_relatorio_semanal()
            await asyncio.sleep(1)
            
            await self.exemplo_sistema_alerta()
            await asyncio.sleep(1)
            
            await self.exemplo_rate_limiting()
            await asyncio.sleep(1)
            
            await self.exemplo_metricas()
            
            logger.info("=" * 60)
            logger.info("✅ Todos os exemplos executados com sucesso!")
            
        except Exception as e:
            logger.error(f"❌ Erro durante execução dos exemplos: {e}")


async def main():
    """Função principal."""
    example = NotificationSystemExample()
    await example.executar_exemplos()


if __name__ == "__main__":
    asyncio.run(main()) 