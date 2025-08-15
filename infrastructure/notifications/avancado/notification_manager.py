"""
Sistema de Notificações Avançado - Omni Keywords Finder
=======================================================

Este módulo implementa um sistema de notificações enterprise com múltiplos canais,
templates personalizáveis, preferências por usuário e histórico completo.

Tracing ID: NOTIF_20241219_001
Autor: Sistema de Notificações Avançado
Data: 2024-12-19
Versão: 1.0.0

Características:
- Múltiplos canais (WebSocket, Email, Slack, SMS)
- Templates personalizáveis com variáveis
- Preferências por usuário
- Histórico completo de notificações
- Agendamento de notificações
- Integração com observabilidade
- Rate limiting e fallback inteligente
"""

import asyncio
import json
import logging
import smtplib
import ssl
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

import redis
import websockets
from dataclasses import dataclass, field
from jinja2 import Template

# Configuração de logging
logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Tipos de notificação suportados."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class NotificationChannel(Enum):
    """Canais de notificação disponíveis."""
    WEBSOCKET = "websocket"
    EMAIL = "email"
    SLACK = "slack"
    SMS = "sms"
    PUSH = "push"


class NotificationPriority(Enum):
    """Prioridades de notificação."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class NotificationTemplate:
    """Template de notificação com variáveis."""
    name: str
    subject: str
    content: str
    variables: List[str] = field(default_factory=list)
    channel: NotificationChannel = NotificationChannel.EMAIL
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class NotificationPreferences:
    """Preferências de notificação por usuário."""
    user_id: str
    channels: Dict[NotificationChannel, bool] = field(default_factory=dict)
    types: Dict[NotificationType, bool] = field(default_factory=dict)
    quiet_hours: Dict[str, str] = field(default_factory=dict)  # {"start": "22:00", "end": "08:00"}
    frequency_limit: int = 10  # Máximo de notificações por hora
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Notification:
    """Estrutura de uma notificação."""
    id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    type: NotificationType = NotificationType.INFO
    priority: NotificationPriority = NotificationPriority.NORMAL
    subject: str = ""
    content: str = ""
    channels: List[NotificationChannel] = field(default_factory=list)
    template_name: Optional[str] = None
    variables: Dict[str, Any] = field(default_factory=dict)
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    status: str = "pending"  # pending, sent, failed, cancelled
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class NotificationChannelProvider(ABC):
    """Interface base para provedores de canal de notificação."""
    
    @abstractmethod
    async def send(self, notification: Notification) -> bool:
        """Envia uma notificação através do canal."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Verifica se o canal está disponível."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Retorna o nome do canal."""
        pass


class WebSocketChannel(NotificationChannelProvider):
    """Canal de notificação via WebSocket para notificações em tempo real."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.channel_name = "notifications"
    
    async def send(self, notification: Notification) -> bool:
        """Envia notificação via WebSocket usando Redis pub/sub."""
        try:
            message = {
                "id": notification.id,
                "user_id": notification.user_id,
                "type": notification.type.value,
                "priority": notification.priority.value,
                "subject": notification.subject,
                "content": notification.content,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": notification.metadata
            }
            
            # Publica no canal específico do usuário
            user_channel = f"{self.channel_name}:{notification.user_id}"
            self.redis_client.publish(user_channel, json.dumps(message))
            
            logger.info(f"Notificação WebSocket enviada para usuário {notification.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação WebSocket: {e}")
            return False
    
    def is_available(self) -> bool:
        """Verifica se o Redis está disponível."""
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    def get_name(self) -> str:
        return "websocket"


class EmailChannel(NotificationChannelProvider):
    """Canal de notificação via Email."""
    
    def __init__(self, smtp_config: Dict[str, Any]):
        self.smtp_config = smtp_config
        self.smtp_server = smtp_config.get("server", "localhost")
        self.smtp_port = smtp_config.get("port", 587)
        self.username = smtp_config.get("username", "")
        self.password = smtp_config.get("password", "")
        self.use_tls = smtp_config.get("use_tls", True)
        self.from_email = smtp_config.get("from_email", "noreply@omnikeywords.com")
    
    async def send(self, notification: Notification) -> bool:
        """Envia notificação via email."""
        try:
            # Busca email do usuário (implementar conforme necessário)
            user_email = self._get_user_email(notification.user_id)
            if not user_email:
                logger.error(f"Email não encontrado para usuário {notification.user_id}")
                return False
            
            # Cria mensagem
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = user_email
            msg['Subject'] = notification.subject
            
            # Adiciona conteúdo
            msg.attach(MIMEText(notification.content, 'html'))
            
            # Envia email
            context = ssl.create_default_context() if self.use_tls else None
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls(context=context)
                if self.username and self.password:
                    server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Email enviado para {user_email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            return False
    
    def _get_user_email(self, user_id: str) -> Optional[str]:
        """Busca email do usuário (implementar conforme modelo de usuário)."""
        # TODO: Implementar busca no banco de dados
        return f"{user_id}@example.com"
    
    def is_available(self) -> bool:
        """Verifica se o servidor SMTP está disponível."""
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                return True
        except:
            return False
    
    def get_name(self) -> str:
        return "email"


class SlackChannel(NotificationChannelProvider):
    """Canal de notificação via Slack."""
    
    def __init__(self, webhook_url: str, channel: str = "#general"):
        self.webhook_url = webhook_url
        self.channel = channel
    
    async def send(self, notification: Notification) -> bool:
        """Envia notificação via Slack webhook."""
        try:
            import aiohttp
            
            # Prepara payload do Slack
            payload = {
                "channel": self.channel,
                "text": f"*{notification.subject}*\n{notification.content}",
                "username": "Omni Keywords Finder",
                "icon_emoji": ":robot_face:"
            }
            
            # Adiciona cor baseada no tipo
            color_map = {
                NotificationType.INFO: "#36a64f",
                NotificationType.SUCCESS: "#36a64f",
                NotificationType.WARNING: "#ff9500",
                NotificationType.ERROR: "#ff0000",
                NotificationType.CRITICAL: "#8b0000"
            }
            
            if notification.type in color_map:
                payload["attachments"] = [{
                    "color": color_map[notification.type],
                    "fields": [
                        {
                            "title": "Tipo",
                            "value": notification.type.value.upper(),
                            "short": True
                        },
                        {
                            "title": "Prioridade",
                            "value": notification.priority.value,
                            "short": True
                        }
                    ]
                }]
            
            # Envia via webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"Notificação Slack enviada para canal {self.channel}")
                        return True
                    else:
                        logger.error(f"Erro ao enviar para Slack: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Erro ao enviar notificação Slack: {e}")
            return False
    
    def is_available(self) -> bool:
        """Verifica se o webhook do Slack está configurado."""
        return bool(self.webhook_url)
    
    def get_name(self) -> str:
        return "slack"


class SMSChannel(NotificationChannelProvider):
    """Canal de notificação via SMS (simulado)."""
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
    
    async def send(self, notification: Notification) -> bool:
        """Envia notificação via SMS (simulado)."""
        try:
            # Simula envio de SMS
            phone = self._get_user_phone(notification.user_id)
            if not phone:
                logger.error(f"Telefone não encontrado para usuário {notification.user_id}")
                return False
            
            # Simula delay de envio
            await asyncio.sleep(0.1)
            
            logger.info(f"SMS simulado enviado para {phone}: {notification.content[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar SMS: {e}")
            return False
    
    def _get_user_phone(self, user_id: str) -> Optional[str]:
        """Busca telefone do usuário (implementar conforme modelo de usuário)."""
        # TODO: Implementar busca no banco de dados
        return "+5511999999999"
    
    def is_available(self) -> bool:
        """Verifica se as credenciais SMS estão configuradas."""
        return bool(self.api_key and self.api_secret)
    
    def get_name(self) -> str:
        return "sms"


class NotificationManager:
    """Gerenciador principal de notificações."""
    
    def __init__(self, redis_client: redis.Redis, config: Dict[str, Any]):
        self.redis_client = redis_client
        self.config = config
        
        # Inicializa canais
        self.channels: Dict[NotificationChannel, NotificationChannelProvider] = {}
        self._initialize_channels()
        
        # Cache de templates e preferências
        self.templates: Dict[str, NotificationTemplate] = {}
        self.preferences: Dict[str, NotificationPreferences] = {}
        
        # Histórico de notificações
        self.notification_history: List[Notification] = []
        
        # Rate limiting
        self.rate_limits: Dict[str, List[datetime]] = {}
        
        logger.info("Sistema de notificações avançado inicializado")
    
    def _initialize_channels(self):
        """Inicializa os canais de notificação configurados."""
        # WebSocket (sempre disponível se Redis estiver)
        if self.redis_client:
            self.channels[NotificationChannel.WEBSOCKET] = WebSocketChannel(self.redis_client)
        
        # Email
        smtp_config = self.config.get("smtp", {})
        if smtp_config:
            self.channels[NotificationChannel.EMAIL] = EmailChannel(smtp_config)
        
        # Slack
        slack_config = self.config.get("slack", {})
        if slack_config.get("webhook_url"):
            self.channels[NotificationChannel.SLACK] = SlackChannel(
                slack_config["webhook_url"],
                slack_config.get("channel", "#general")
            )
        
        # SMS
        sms_config = self.config.get("sms", {})
        if sms_config.get("api_key") and sms_config.get("api_secret"):
            self.channels[NotificationChannel.SMS] = SMSChannel(
                sms_config["api_key"],
                sms_config["api_secret"]
            )
        
        logger.info(f"Canais inicializados: {[c.get_name() for c in self.channels.values()]}")
    
    async def send_notification(self, notification: Notification) -> bool:
        """Envia uma notificação através dos canais configurados."""
        try:
            # Validações
            if not self._validate_notification(notification):
                return False
            
            # Verifica rate limiting
            if not self._check_rate_limit(notification.user_id):
                logger.warning(f"Rate limit excedido para usuário {notification.user_id}")
                return False
            
            # Verifica quiet hours
            if self._is_in_quiet_hours(notification.user_id):
                logger.info(f"Notificação agendada para fora do horário silencioso: {notification.user_id}")
                await self._schedule_notification(notification)
                return True
            
            # Obtém preferências do usuário
            preferences = self._get_user_preferences(notification.user_id)
            
            # Filtra canais baseado nas preferências
            available_channels = self._get_available_channels(preferences)
            
            if not available_channels:
                logger.warning(f"Nenhum canal disponível para usuário {notification.user_id}")
                return False
            
            # Envia para cada canal disponível
            success_count = 0
            for channel in available_channels:
                if channel in self.channels:
                    provider = self.channels[channel]
                    if provider.is_available():
                        if await provider.send(notification):
                            success_count += 1
                        else:
                            # Tenta fallback
                            await self._handle_channel_failure(notification, channel)
            
            # Atualiza status
            notification.status = "sent" if success_count > 0 else "failed"
            notification.sent_at = datetime.utcnow()
            
            # Salva no histórico
            self._save_to_history(notification)
            
            # Registra métricas
            self._record_metrics(notification, success_count)
            
            logger.info(f"Notificação enviada: {success_count}/{len(available_channels)} canais")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação: {e}")
            notification.status = "failed"
            return False
    
    def _validate_notification(self, notification: Notification) -> bool:
        """Valida uma notificação antes do envio."""
        if not notification.user_id:
            logger.error("User ID é obrigatório")
            return False
        
        if not notification.subject and not notification.content:
            logger.error("Subject ou content é obrigatório")
            return False
        
        if not notification.channels:
            logger.error("Pelo menos um canal deve ser especificado")
            return False
        
        return True
    
    def _check_rate_limit(self, user_id: str) -> bool:
        """Verifica rate limiting para o usuário."""
        now = datetime.utcnow()
        user_limits = self.rate_limits.get(user_id, [])
        
        # Remove timestamps antigos (mais de 1 hora)
        user_limits = [ts for ts in user_limits if now - ts < timedelta(hours=1)]
        
        # Verifica limite (10 notificações por hora por padrão)
        preferences = self._get_user_preferences(user_id)
        limit = preferences.frequency_limit if preferences else 10
        
        if len(user_limits) >= limit:
            return False
        
        # Adiciona timestamp atual
        user_limits.append(now)
        self.rate_limits[user_id] = user_limits
        
        return True
    
    def _is_in_quiet_hours(self, user_id: str) -> bool:
        """Verifica se está no horário silencioso do usuário."""
        preferences = self._get_user_preferences(user_id)
        if not preferences or not preferences.quiet_hours:
            return False
        
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        start_time = preferences.quiet_hours.get("start", "22:00")
        end_time = preferences.quiet_hours.get("end", "08:00")
        
        # Lógica simples para horário silencioso
        if start_time <= end_time:
            return start_time <= current_time <= end_time
        else:  # Horário silencioso cruza meia-noite
            return current_time >= start_time or current_time <= end_time
    
    async def _schedule_notification(self, notification: Notification):
        """Agenda notificação para horário fora do silencioso."""
        preferences = self._get_user_preferences(notification.user_id)
        if not preferences or not preferences.quiet_hours:
            return
        
        # Calcula próximo horário disponível
        end_time = preferences.quiet_hours.get("end", "08:00")
        hour, minute = map(int, end_time.split(":"))
        
        now = datetime.now()
        scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if scheduled_time <= now:
            scheduled_time += timedelta(days=1)
        
        notification.scheduled_at = scheduled_time
        notification.status = "scheduled"
        
        # Salva notificação agendada
        await self._save_scheduled_notification(notification)
        
        logger.info(f"Notificação agendada para {scheduled_time}")
    
    async def _save_scheduled_notification(self, notification: Notification):
        """Salva notificação agendada no Redis."""
        try:
            key = f"scheduled_notifications:{notification.id}"
            data = {
                "id": notification.id,
                "user_id": notification.user_id,
                "scheduled_at": notification.scheduled_at.isoformat(),
                "notification": notification.__dict__
            }
            self.redis_client.setex(key, 86400, json.dumps(data))  # 24 horas
        except Exception as e:
            logger.error(f"Erro ao salvar notificação agendada: {e}")
    
    def _get_user_preferences(self, user_id: str) -> Optional[NotificationPreferences]:
        """Obtém preferências do usuário (cache + banco)."""
        if user_id in self.preferences:
            return self.preferences[user_id]
        
        # TODO: Implementar busca no banco de dados
        # Por enquanto, retorna preferências padrão
        preferences = NotificationPreferences(
            user_id=user_id,
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
            }
        )
        
        self.preferences[user_id] = preferences
        return preferences
    
    def _get_available_channels(self, preferences: NotificationPreferences) -> List[NotificationChannel]:
        """Obtém canais disponíveis baseado nas preferências."""
        available = []
        for channel, enabled in preferences.channels.items():
            if enabled and channel in self.channels:
                provider = self.channels[channel]
                if provider.is_available():
                    available.append(channel)
        return available
    
    async def _handle_channel_failure(self, notification: Notification, channel: NotificationChannel):
        """Trata falha de canal específico."""
        logger.warning(f"Canal {channel.value} falhou para notificação {notification.id}")
        
        # Implementa fallback
        if channel == NotificationChannel.EMAIL:
            # Tenta WebSocket como fallback
            if NotificationChannel.WEBSOCKET in self.channels:
                await self.channels[NotificationChannel.WEBSOCKET].send(notification)
    
    def _save_to_history(self, notification: Notification):
        """Salva notificação no histórico."""
        self.notification_history.append(notification)
        
        # Mantém apenas últimas 1000 notificações
        if len(self.notification_history) > 1000:
            self.notification_history = self.notification_history[-1000:]
    
    def _record_metrics(self, notification: Notification, success_count: int):
        """Registra métricas de notificação."""
        try:
            # Incrementa contadores no Redis
            pipeline = self.redis_client.pipeline()
            
            # Total de notificações
            pipeline.incr("notifications:total")
            
            # Por tipo
            pipeline.incr(f"notifications:type:{notification.type.value}")
            
            # Por canal
            for channel in notification.channels:
                pipeline.incr(f"notifications:channel:{channel.value}")
            
            # Sucesso/falha
            if success_count > 0:
                pipeline.incr("notifications:success")
            else:
                pipeline.incr("notifications:failed")
            
            pipeline.execute()
            
        except Exception as e:
            logger.error(f"Erro ao registrar métricas: {e}")
    
    def create_template(self, template: NotificationTemplate) -> bool:
        """Cria um novo template de notificação."""
        try:
            self.templates[template.name] = template
            logger.info(f"Template criado: {template.name}")
            return True
        except Exception as e:
            logger.error(f"Erro ao criar template: {e}")
            return False
    
    def get_template(self, name: str) -> Optional[NotificationTemplate]:
        """Obtém um template por nome."""
        return self.templates.get(name)
    
    def render_template(self, template_name: str, variables: Dict[str, Any]) -> Optional[Notification]:
        """Renderiza um template com variáveis."""
        template = self.get_template(template_name)
        if not template:
            logger.error(f"Template não encontrado: {template_name}")
            return None
        
        try:
            # Renderiza subject e content
            subject_template = Template(template.subject)
            content_template = Template(template.content)
            
            subject = subject_template.render(**variables)
            content = content_template.render(**variables)
            
            # Cria notificação
            notification = Notification(
                type=NotificationType.INFO,
                subject=subject,
                content=content,
                channels=[template.channel],
                template_name=template_name,
                variables=variables
            )
            
            return notification
            
        except Exception as e:
            logger.error(f"Erro ao renderizar template {template_name}: {e}")
            return None
    
    def get_notification_history(self, user_id: str, limit: int = 50) -> List[Notification]:
        """Obtém histórico de notificações do usuário."""
        user_notifications = [
            n for n in self.notification_history 
            if n.user_id == user_id
        ]
        return user_notifications[-limit:]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtém métricas do sistema de notificações."""
        try:
            metrics = {}
            
            # Contadores do Redis
            for key in ["total", "success", "failed"]:
                value = self.redis_client.get(f"notifications:{key}")
                metrics[f"notifications_{key}"] = int(value) if value else 0
            
            # Por tipo
            for notification_type in NotificationType:
                value = self.redis_client.get(f"notifications:type:{notification_type.value}")
                metrics[f"notifications_type_{notification_type.value}"] = int(value) if value else 0
            
            # Por canal
            for channel in NotificationChannel:
                value = self.redis_client.get(f"notifications:channel:{channel.value}")
                metrics[f"notifications_channel_{channel.value}"] = int(value) if value else 0
            
            # Canais disponíveis
            metrics["channels_available"] = len([c for c in self.channels.values() if c.is_available()])
            metrics["channels_total"] = len(self.channels)
            
            # Templates
            metrics["templates_count"] = len(self.templates)
            
            # Histórico
            metrics["history_count"] = len(self.notification_history)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erro ao obter métricas: {e}")
            return {}


# Função de conveniência para criar notificação
def create_notification(
    user_id: str,
    subject: str,
    content: str,
    notification_type: NotificationType = NotificationType.INFO,
    priority: NotificationPriority = NotificationPriority.NORMAL,
    channels: List[NotificationChannel] = None,
    template_name: str = None,
    variables: Dict[str, Any] = None
) -> Notification:
    """Cria uma notificação com parâmetros padrão."""
    if channels is None:
        channels = [NotificationChannel.WEBSOCKET, NotificationChannel.EMAIL]
    
    return Notification(
        user_id=user_id,
        type=notification_type,
        priority=priority,
        subject=subject,
        content=content,
        channels=channels,
        template_name=template_name,
        variables=variables or {}
    )


# Exemplo de uso
if __name__ == "__main__":
    # Configuração de exemplo
    config = {
        "smtp": {
            "server": "smtp.gmail.com",
            "port": 587,
            "username": "user@gmail.com",
            "password": "password",
            "use_tls": True,
            "from_email": "noreply@omnikeywords.com"
        },
        "slack": {
            "webhook_url": "https://hooks.slack.com/services/...",
            "channel": "#notifications"
        },
        "sms": {
            "api_key": "your_api_key",
            "api_secret": "your_api_secret"
        }
    }
    
    # Inicializa Redis (simulado)
    redis_client = None
    
    # Cria gerenciador
    manager = NotificationManager(redis_client, config)
    
    # Cria template
    template = NotificationTemplate(
        name="execucao_concluida",
        subject="Execução {{execucao_id}} concluída",
        content="""
        <h2>Execução Concluída</h2>
        <p>A execução <strong>{{execucao_id}}</strong> foi concluída com sucesso.</p>
        <p><strong>Keywords encontradas:</strong> {{keywords_count}}</p>
        <p><strong>Tempo de execução:</strong> {{tempo_execucao}}</p>
        """,
        variables=["execucao_id", "keywords_count", "tempo_execucao"],
        channel=NotificationChannel.EMAIL
    )
    
    manager.create_template(template)
    
    print("Sistema de notificações avançado configurado com sucesso!") 