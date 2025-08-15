"""
Sistema de Notificações Avançado - Omni Keywords Finder

Funcionalidades:
- Notificações em tempo real
- Integração com email
- Webhooks para Slack/Discord
- Notificações push
- Sistema de templates
- Preferências de usuário

Autor: Sistema de Notificações Avançado
Data: 2024-12-19
Ruleset: enterprise_control_layer.yaml
"""

import os
import json
import smtplib
import requests
import asyncio
import websockets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import threading
import queue
from pathlib import Path

class NotificationType(Enum):
    """Tipos de notificação suportados"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    CRITICAL = "critical"

class NotificationChannel(Enum):
    """Canais de notificação disponíveis"""
    EMAIL = "email"
    SLACK = "slack"
    DISCORD = "discord"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"

@dataclass
class NotificationTemplate:
    """Template de notificação"""
    id: str
    name: str
    subject: str
    body: str
    variables: List[str]
    channels: List[NotificationChannel]
    created_at: datetime
    updated_at: datetime

@dataclass
class UserPreferences:
    """Preferências de notificação do usuário"""
    user_id: str
    email_enabled: bool = True
    slack_enabled: bool = False
    discord_enabled: bool = False
    push_enabled: bool = True
    in_app_enabled: bool = True
    webhook_enabled: bool = False
    webhook_url: Optional[str] = None
    email_address: Optional[str] = None
    slack_channel: Optional[str] = None
    discord_webhook: Optional[str] = None
    notification_types: List[NotificationType] = None
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "08:00"
    timezone: str = "UTC"

@dataclass
class Notification:
    """Estrutura de notificação"""
    id: str
    title: str
    message: str
    notification_type: NotificationType
    user_id: Optional[str] = None
    channels: List[NotificationChannel] = None
    template_id: Optional[str] = None
    variables: Dict[str, Any] = None
    priority: int = 1  # 1-5, onde 5 é mais crítico
    created_at: datetime = None
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None

class EmailNotifier:
    """Gerenciador de notificações por email"""
    
    def __init__(self, config: Dict[str, Any]):
        self.smtp_host = config.get('smtp_host', 'localhost')
        self.smtp_port = config.get('smtp_port', 587)
        self.smtp_user = config.get('smtp_user')
        self.smtp_password = config.get('smtp_password')
        self.from_email = config.get('from_email', 'noreply@omnikeywords.com')
        self.use_tls = config.get('use_tls', True)
        
    def send_notification(self, notification: Notification, user_prefs: UserPreferences) -> bool:
        """Envia notificação por email"""
        if not user_prefs.email_enabled or not user_prefs.email_address:
            return False
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = user_prefs.email_address
            msg['Subject'] = notification.title
            
            # Aplicar template se especificado
            body = self._apply_template(notification)
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
                
            logging.info(f"Email enviado para {user_prefs.email_address}: {notification.title}")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao enviar email: {str(e)}")
            return False
    
    def _apply_template(self, notification: Notification) -> str:
        """Aplica template HTML ao email"""
        template = f"""
        <html>
        <body>
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background-color: {self._get_color(notification.notification_type)}; padding: 20px; border-radius: 8px;">
                    <h2 style="color: white; margin: 0;">{notification.title}</h2>
                </div>
                <div style="padding: 20px; background-color: #f9f9f9;">
                    <p style="font-size: 16px; line-height: 1.6;">{notification.message}</p>
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                    <p style="font-size: 12px; color: #666;">
                        Enviado em: {notification.created_at.strftime('%data/%m/%Y %H:%M:%S')}
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        return template
    
    def _get_color(self, notification_type: NotificationType) -> str:
        """Retorna cor baseada no tipo de notificação"""
        colors = {
            NotificationType.INFO: "#4f8cff",
            NotificationType.WARNING: "#eab308",
            NotificationType.ERROR: "#ef4444",
            NotificationType.SUCCESS: "#10b981",
            NotificationType.CRITICAL: "#dc2626"
        }
        return colors.get(notification_type, "#4f8cff")

class SlackNotifier:
    """Gerenciador de notificações para Slack"""
    
    def __init__(self, config: Dict[str, Any]):
        self.webhook_url = config.get('slack_webhook_url')
        self.default_channel = config.get('slack_default_channel', '#general')
        
    def send_notification(self, notification: Notification, user_prefs: UserPreferences) -> bool:
        """Envia notificação para Slack"""
        if not user_prefs.slack_enabled or not self.webhook_url:
            return False
            
        try:
            channel = user_prefs.slack_channel or self.default_channel
            payload = {
                "channel": channel,
                "text": f"*{notification.title}*",
                "attachments": [{
                    "color": self._get_color(notification.notification_type),
                    "text": notification.message,
                    "fields": [
                        {
                            "title": "Tipo",
                            "value": notification.notification_type.value.upper(),
                            "short": True
                        },
                        {
                            "title": "Prioridade",
                            "value": str(notification.priority),
                            "short": True
                        }
                    ],
                    "footer": f"Omni Keywords Finder • {notification.created_at.strftime('%data/%m/%Y %H:%M')}"
                }]
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            logging.info(f"Slack notification enviada para {channel}: {notification.title}")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao enviar notificação Slack: {str(e)}")
            return False
    
    def _get_color(self, notification_type: NotificationType) -> str:
        """Retorna cor para Slack baseada no tipo"""
        colors = {
            NotificationType.INFO: "#4f8cff",
            NotificationType.WARNING: "#eab308",
            NotificationType.ERROR: "#ef4444",
            NotificationType.SUCCESS: "#10b981",
            NotificationType.CRITICAL: "#dc2626"
        }
        return colors.get(notification_type, "#4f8cff")

class DiscordNotifier:
    """Gerenciador de notificações para Discord"""
    
    def __init__(self, config: Dict[str, Any]):
        self.webhook_url = config.get('discord_webhook_url')
        
    def send_notification(self, notification: Notification, user_prefs: UserPreferences) -> bool:
        """Envia notificação para Discord"""
        if not user_prefs.discord_enabled or not user_prefs.discord_webhook:
            return False
            
        try:
            embed = {
                "title": notification.title,
                "description": notification.message,
                "color": self._get_color_int(notification.notification_type),
                "timestamp": notification.created_at.isoformat(),
                "footer": {
                    "text": "Omni Keywords Finder"
                },
                "fields": [
                    {
                        "name": "Tipo",
                        "value": notification.notification_type.value.upper(),
                        "inline": True
                    },
                    {
                        "name": "Prioridade",
                        "value": str(notification.priority),
                        "inline": True
                    }
                ]
            }
            
            payload = {
                "embeds": [embed]
            }
            
            response = requests.post(user_prefs.discord_webhook, json=payload, timeout=10)
            response.raise_for_status()
            
            logging.info(f"Discord notification enviada: {notification.title}")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao enviar notificação Discord: {str(e)}")
            return False
    
    def _get_color_int(self, notification_type: NotificationType) -> int:
        """Retorna cor como inteiro para Discord"""
        colors = {
            NotificationType.INFO: 0x4f8cff,
            NotificationType.WARNING: 0xeab308,
            NotificationType.ERROR: 0xef4444,
            NotificationType.SUCCESS: 0x10b981,
            NotificationType.CRITICAL: 0xdc2626
        }
        return colors.get(notification_type, 0x4f8cff)

class PushNotifier:
    """Gerenciador de notificações push"""
    
    def __init__(self, config: Dict[str, Any]):
        self.push_enabled = config.get('push_enabled', False)
        
    def send_notification(self, notification: Notification, user_prefs: UserPreferences) -> bool:
        """Envia notificação push"""
        if not user_prefs.push_enabled or not self.push_enabled:
            return False
            
        try:
            # Implementação simulada - sem dependências externas
            logging.info(f"Push notification simulada: {notification.title}")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao enviar push notification: {str(e)}")
            return False

class WebhookNotifier:
    """Gerenciador de webhooks genéricos"""
    
    def send_notification(self, notification: Notification, user_prefs: UserPreferences) -> bool:
        """Envia notificação via webhook"""
        if not user_prefs.webhook_enabled or not user_prefs.webhook_url:
            return False
            
        try:
            payload = {
                "notification_id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "type": notification.notification_type.value,
                "priority": notification.priority,
                "user_id": notification.user_id,
                "created_at": notification.created_at.isoformat(),
                "metadata": notification.metadata or {}
            }
            
            response = requests.post(user_prefs.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            logging.info(f"Webhook notification enviada: {notification.title}")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao enviar webhook notification: {str(e)}")
            return False

class TemplateManager:
    """Gerenciador de templates de notificação"""
    
    def __init__(self, templates_dir: str = "templates/notifications"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.templates: Dict[str, NotificationTemplate] = {}
        self._load_templates()
    
    def _load_templates(self):
        """Carrega templates do sistema de arquivos"""
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    template = NotificationTemplate(
                        id=data['id'],
                        name=data['name'],
                        subject=data['subject'],
                        body=data['body'],
                        variables=data.get('variables', []),
                        channels=[NotificationChannel(c) for c in data.get('channels', [])],
                        created_at=datetime.fromisoformat(data['created_at']),
                        updated_at=datetime.fromisoformat(data['updated_at'])
                    )
                    self.templates[template.id] = template
            except Exception as e:
                logging.error(f"Erro ao carregar template {template_file}: {str(e)}")
    
    def get_template(self, template_id: str) -> Optional[NotificationTemplate]:
        """Retorna template por ID"""
        return self.templates.get(template_id)
    
    def create_template(self, template: NotificationTemplate) -> bool:
        """Cria novo template"""
        try:
            template_file = self.templates_dir / f"{template.id}.json"
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(template), f, indent=2, default=str)
            
            self.templates[template.id] = template
            return True
        except Exception as e:
            logging.error(f"Erro ao criar template: {str(e)}")
            return False
    
    def apply_template(self, template_id: str, variables: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Aplica template com variáveis"""
        template = self.get_template(template_id)
        if not template:
            return None
        
        try:
            subject = template.subject
            body = template.body
            
            for var_name, var_value in variables.items():
                placeholder = f"{{{{{var_name}}}}}"
                subject = subject.replace(placeholder, str(var_value))
                body = body.replace(placeholder, str(var_value))
            
            return {
                "subject": subject,
                "body": body
            }
        except Exception as e:
            logging.error(f"Erro ao aplicar template {template_id}: {str(e)}")
            return None

class AdvancedNotificationSystem:
    """Sistema principal de notificações avançado"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.notifiers = {
            NotificationChannel.EMAIL: EmailNotifier(config),
            NotificationChannel.SLACK: SlackNotifier(config),
            NotificationChannel.DISCORD: DiscordNotifier(config),
            NotificationChannel.PUSH: PushNotifier(config),
            NotificationChannel.WEBHOOK: WebhookNotifier()
        }
        
        self.template_manager = TemplateManager()
        self.user_preferences: Dict[str, UserPreferences] = {}
        self.notification_queue = queue.Queue()
        self.real_time_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        
        # Iniciar workers
        self._start_workers()
        self._load_user_preferences()
    
    def _start_workers(self):
        """Inicia workers para processamento assíncrono"""
        self.worker_thread = threading.Thread(target=self._notification_worker, daemon=True)
        self.worker_thread.start()
        
        # Iniciar servidor WebSocket para notificações em tempo real
        self.ws_thread = threading.Thread(target=self._start_websocket_server, daemon=True)
        self.ws_thread.start()
    
    def _notification_worker(self):
        """Worker para processar notificações em background"""
        while True:
            try:
                notification_data = self.notification_queue.get(timeout=1)
                self._process_notification(notification_data)
                self.notification_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Erro no worker de notificações: {str(e)}")
    
    def _process_notification(self, notification_data: Dict[str, Any]):
        """Processa notificação individual"""
        notification = Notification(**notification_data['notification'])
        user_prefs = notification_data.get('user_preferences')
        
        if not user_prefs:
            user_prefs = self.get_user_preferences(notification.user_id)
        
        # Verificar quiet hours
        if self._is_in_quiet_hours(user_prefs):
            logging.info(f"Notificação {notification.id} em quiet hours, aguardando...")
            return
        
        # Enviar para canais habilitados
        for channel in notification.channels or [NotificationChannel.IN_APP]:
            if channel == NotificationChannel.IN_APP:
                self._send_in_app_notification(notification)
            else:
                notifier = self.notifiers.get(channel)
                if notifier:
                    notifier.send_notification(notification, user_prefs)
        
        # Marcar como enviada
        notification.sent_at = datetime.utcnow()
    
    def _is_in_quiet_hours(self, user_prefs: UserPreferences) -> bool:
        """Verifica se está em período de quiet hours"""
        if not user_prefs.quiet_hours_start or not user_prefs.quiet_hours_end:
            return False
        
        now = datetime.now()
        start_time = datetime.strptime(user_prefs.quiet_hours_start, "%H:%M").time()
        end_time = datetime.strptime(user_prefs.quiet_hours_end, "%H:%M").time()
        current_time = now.time()
        
        if start_time <= end_time:
            return start_time <= current_time <= end_time
        else:  # Período atravessa meia-noite
            return current_time >= start_time or current_time <= end_time
    
    def _send_in_app_notification(self, notification: Notification):
        """Envia notificação in-app via WebSocket"""
        if notification.user_id in self.real_time_connections:
            try:
                asyncio.run(self._send_websocket_message(
                    notification.user_id,
                    asdict(notification)
                ))
            except Exception as e:
                logging.error(f"Erro ao enviar notificação in-app: {str(e)}")
    
    async def _send_websocket_message(self, user_id: str, message: Dict[str, Any]):
        """Envia mensagem via WebSocket"""
        if user_id in self.real_time_connections:
            websocket = self.real_time_connections[user_id]
            await websocket.send(json.dumps(message))
    
    def _start_websocket_server(self):
        """Inicia servidor WebSocket para notificações em tempo real"""
        async def websocket_handler(websocket, path):
            try:
                # Autenticar usuário (implementação básica)
                user_id = await websocket.recv()
                self.real_time_connections[user_id] = websocket
                
                try:
                    async for message in websocket:
                        # Processar mensagens do cliente se necessário
                        pass
                finally:
                    if user_id in self.real_time_connections:
                        del self.real_time_connections[user_id]
            except Exception as e:
                logging.error(f"Erro no WebSocket: {str(e)}")
        
        # Iniciar servidor WebSocket
        start_server = websockets.serve(websocket_handler, "localhost", 8765)
        asyncio.run(start_server)
    
    def send_notification(self, notification: Notification, user_id: Optional[str] = None) -> bool:
        """Envia notificação"""
        try:
            # Aplicar template se especificado
            if notification.template_id and notification.variables:
                template_result = self.template_manager.apply_template(
                    notification.template_id, 
                    notification.variables
                )
                if template_result:
                    notification.title = template_result["subject"]
                    notification.message = template_result["body"]
            
            # Definir timestamp se não especificado
            if not notification.created_at:
                notification.created_at = datetime.utcnow()
            
            # Obter preferências do usuário
            user_prefs = self.get_user_preferences(user_id or notification.user_id)
            
            # Adicionar à fila para processamento assíncrono
            self.notification_queue.put({
                'notification': asdict(notification),
                'user_preferences': user_prefs
            })
            
            logging.info(f"Notificação {notification.id} adicionada à fila")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao enviar notificação: {str(e)}")
            return False
    
    def get_user_preferences(self, user_id: str) -> UserPreferences:
        """Obtém preferências do usuário"""
        if user_id not in self.user_preferences:
            # Carregar do banco de dados ou criar padrão
            self.user_preferences[user_id] = UserPreferences(user_id=user_id)
        return self.user_preferences[user_id]
    
    def update_user_preferences(self, user_id: str, preferences: UserPreferences) -> bool:
        """Atualiza preferências do usuário"""
        try:
            self.user_preferences[user_id] = preferences
            # Salvar no banco de dados
            self._save_user_preferences()
            return True
        except Exception as e:
            logging.error(f"Erro ao atualizar preferências: {str(e)}")
            return False
    
    def _load_user_preferences(self):
        """Carrega preferências dos usuários"""
        # Implementar carregamento do banco de dados
        pass
    
    def _save_user_preferences(self):
        """Salva preferências dos usuários"""
        # Implementar salvamento no banco de dados
        pass
    
    def create_template(self, template: NotificationTemplate) -> bool:
        """Cria novo template"""
        return self.template_manager.create_template(template)
    
    def get_template(self, template_id: str) -> Optional[NotificationTemplate]:
        """Obtém template por ID"""
        return self.template_manager.get_template(template_id)
    
    def list_templates(self) -> List[NotificationTemplate]:
        """Lista todos os templates"""
        return list(self.template_manager.templates.values())
    
    def get_notification_stats(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Obtém estatísticas de notificações do usuário"""
        # Implementar consulta ao banco de dados
        return {
            "total_sent": 0,
            "by_type": {},
            "by_channel": {},
            "read_rate": 0.0
        }

# Configuração padrão
DEFAULT_CONFIG = {
    "smtp_host": "localhost",
    "smtp_port": 587,
    "smtp_user": "",
    "smtp_password": "",
    "from_email": "noreply@omnikeywords.com",
    "use_tls": True,
    "slack_webhook_url": "",
    "slack_default_channel": "#general",
    "discord_webhook_url": "",
    "push_enabled": False,
    "websocket_port": 8765
}

def create_notification_system(config: Optional[Dict[str, Any]] = None) -> AdvancedNotificationSystem:
    """Factory para criar sistema de notificações"""
    if config is None:
        config = DEFAULT_CONFIG
    
    return AdvancedNotificationSystem(config) 