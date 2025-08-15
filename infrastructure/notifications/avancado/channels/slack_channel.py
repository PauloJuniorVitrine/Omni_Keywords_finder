"""
Canal Slack para Notificações
=============================

Implementa notificações via Slack com suporte a webhooks,
mensagens ricas, canais múltiplos e integração avançada.

Tracing ID: NOTIF_20241219_001
Autor: Sistema de Notificações Avançado
Data: 2024-12-19
Versão: 1.0.0
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SlackMessageType(Enum):
    """Tipos de mensagem Slack."""
    SIMPLE = "simple"
    RICH = "rich"
    INTERACTIVE = "interactive"


@dataclass
class SlackConfig:
    """Configuração Slack."""
    webhook_url: str
    channel: str = "#general"
    username: str = "Omni Keywords Finder"
    icon_emoji: str = ":robot_face:"
    icon_url: str = ""
    link_names: bool = True


@dataclass
class SlackAttachment:
    """Anexo para mensagem Slack."""
    title: str = ""
    text: str = ""
    color: str = "#36a64f"
    fields: List[Dict[str, Any]] = None
    footer: str = ""
    footer_icon: str = ""
    ts: int = None
    
    def __post_init__(self):
        if self.fields is None:
            self.fields = []
        if self.ts is None:
            self.ts = int(datetime.utcnow().timestamp())


class SlackChannel:
    """Canal de notificação via Slack."""
    
    def __init__(self, webhook_url: str, channel: str = "#general"):
        self.config = SlackConfig(webhook_url=webhook_url, channel=channel)
        self.message_templates = {}
        self.channel_mappings = {}  # Mapeia tipos de notificação para canais
        
        # Inicializa templates padrão
        self._initialize_default_templates()
    
    def _initialize_default_templates(self):
        """Inicializa templates de mensagem Slack padrão."""
        
        # Template para execução concluída
        execucao_success = {
            "text": "✅ Execução concluída com sucesso!",
            "attachments": [{
                "color": "#36a64f",
                "title": "Execução {{execucao_id}}",
                "fields": [
                    {"title": "Status", "value": "✅ Sucesso", "short": True},
                    {"title": "Keywords", "value": "{{keywords_count}}", "short": True},
                    {"title": "Tempo", "value": "{{tempo_execucao}}", "short": True},
                    {"title": "Blog", "value": "{{blog_url}}", "short": True}
                ],
                "footer": "Omni Keywords Finder",
                "footer_icon": ":chart_with_upwards_trend:"
            }]
        }
        
        # Template para erro
        execucao_error = {
            "text": "❌ Erro na execução!",
            "attachments": [{
                "color": "#f44336",
                "title": "Execução {{execucao_id}}",
                "fields": [
                    {"title": "Status", "value": "❌ Erro", "short": True},
                    {"title": "Erro", "value": "{{error_message}}", "short": False}
                ],
                "footer": "Omni Keywords Finder",
                "footer_icon": ":warning:"
            }]
        }
        
        # Template para relatório
        relatorio = {
            "text": "📊 Relatório de atividades",
            "attachments": [{
                "color": "#2196F3",
                "title": "Relatório {{periodo}}",
                "fields": [
                    {"title": "Execuções", "value": "{{execucoes_count}}", "short": True},
                    {"title": "Keywords", "value": "{{keywords_total}}", "short": True},
                    {"title": "Taxa Sucesso", "value": "{{taxa_sucesso}}%", "short": True},
                    {"title": "Tempo Total", "value": "{{tempo_total}}", "short": True}
                ],
                "footer": "Omni Keywords Finder",
                "footer_icon": ":bar_chart:"
            }]
        }
        
        # Template para alerta de sistema
        sistema_alerta = {
            "text": "🚨 Alerta do Sistema",
            "attachments": [{
                "color": "#ff9500",
                "title": "{{alerta_titulo}}",
                "text": "{{alerta_mensagem}}",
                "fields": [
                    {"title": "Severidade", "value": "{{severidade}}", "short": True},
                    {"title": "Componente", "value": "{{componente}}", "short": True}
                ],
                "footer": "Omni Keywords Finder",
                "footer_icon": ":warning:"
            }]
        }
        
        self.message_templates = {
            "execucao_success": execucao_success,
            "execucao_error": execucao_error,
            "relatorio": relatorio,
            "sistema_alerta": sistema_alerta
        }
    
    async def send(self, notification) -> bool:
        """Envia notificação via Slack webhook."""
        try:
            # Determina canal baseado no tipo de notificação
            channel = self._get_channel_for_notification(notification)
            
            # Prepara payload
            payload = self._prepare_payload(notification, channel)
            
            # Envia via webhook
            success = await self._send_webhook(payload)
            
            if success:
                logger.info(f"Notificação Slack enviada para canal {channel}")
                return True
            else:
                logger.error(f"Falha ao enviar para Slack: canal {channel}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao enviar notificação Slack: {e}")
            return False
    
    def _get_channel_for_notification(self, notification) -> str:
        """Determina canal apropriado para a notificação."""
        # Mapeamento baseado no tipo de notificação
        channel_mapping = {
            "execucao_success": "#execucoes",
            "execucao_error": "#erros",
            "relatorio": "#relatorios",
            "sistema_alerta": "#alertas"
        }
        
        # Verifica se há mapeamento específico
        if notification.template_name in channel_mapping:
            return channel_mapping[notification.template_name]
        
        # Verifica se há mapeamento por tipo
        type_mapping = {
            "info": "#info",
            "success": "#success",
            "warning": "#warnings",
            "error": "#errors",
            "critical": "#critical"
        }
        
        if notification.type.value in type_mapping:
            return type_mapping[notification.type.value]
        
        # Canal padrão
        return self.config.channel
    
    def _prepare_payload(self, notification, channel: str) -> Dict[str, Any]:
        """Prepara payload para Slack."""
        payload = {
            "channel": channel,
            "username": self.config.username,
            "icon_emoji": self.config.icon_emoji,
            "link_names": self.config.link_names
        }
        
        # Se tem template, usa ele
        if notification.template_name and notification.template_name in self.message_templates:
            template = self.message_templates[notification.template_name]
            payload.update(template)
            
            # Renderiza variáveis no template
            payload = self._render_template_variables(payload, notification.variables)
        else:
            # Mensagem simples
            payload["text"] = f"*{notification.subject}*\n{notification.content}"
            
            # Adiciona cor baseada no tipo
            color_map = {
                "info": "#36a64f",
                "success": "#36a64f",
                "warning": "#ff9500",
                "error": "#f44336",
                "critical": "#8b0000"
            }
            
            if notification.type.value in color_map:
                payload["attachments"] = [{
                    "color": color_map[notification.type.value],
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
                    ],
                    "footer": "Omni Keywords Finder",
                    "ts": int(datetime.utcnow().timestamp())
                }]
        
        return payload
    
    def _render_template_variables(self, payload: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """Renderiza variáveis no template."""
        import re
        
        def replace_variables(text: str) -> str:
            """Substitui variáveis no texto."""
            for key, value in variables.items():
                placeholder = f"{{{{{key}}}}}"
                text = text.replace(placeholder, str(value))
            return text
        
        # Renderiza texto principal
        if "text" in payload:
            payload["text"] = replace_variables(payload["text"])
        
        # Renderiza attachments
        if "attachments" in payload:
            for attachment in payload["attachments"]:
                if "title" in attachment:
                    attachment["title"] = replace_variables(attachment["title"])
                if "text" in attachment:
                    attachment["text"] = replace_variables(attachment["text"])
                if "footer" in attachment:
                    attachment["footer"] = replace_variables(attachment["footer"])
                
                # Renderiza fields
                if "fields" in attachment:
                    for field in attachment["fields"]:
                        if "title" in field:
                            field["title"] = replace_variables(field["title"])
                        if "value" in field:
                            field["value"] = replace_variables(field["value"])
        
        return payload
    
    async def _send_webhook(self, payload: Dict[str, Any]) -> bool:
        """Envia payload via webhook."""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.webhook_url,
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                ) as response:
                    if response.status == 200:
                        return True
                    else:
                        logger.error(f"Slack webhook retornou status {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Erro ao enviar webhook Slack: {e}")
            return False
    
    def is_available(self) -> bool:
        """Verifica se o webhook do Slack está configurado."""
        return bool(self.config.webhook_url and self.config.webhook_url.startswith("https://hooks.slack.com/"))
    
    def get_name(self) -> str:
        return "slack"
    
    def add_template(self, name: str, template: Dict[str, Any]):
        """Adiciona novo template de mensagem."""
        self.message_templates[name] = template
        logger.info(f"Template Slack adicionado: {name}")
    
    def set_channel_mapping(self, notification_type: str, channel: str):
        """Define mapeamento de tipo de notificação para canal."""
        self.channel_mappings[notification_type] = channel
        logger.info(f"Mapeamento de canal definido: {notification_type} -> {channel}")
    
    def send_rich_message(self, channel: str, title: str, text: str, color: str = "#36a64f", fields: List[Dict] = None):
        """Envia mensagem rica para canal específico."""
        payload = {
            "channel": channel,
            "username": self.config.username,
            "icon_emoji": self.config.icon_emoji,
            "attachments": [{
                "color": color,
                "title": title,
                "text": text,
                "fields": fields or [],
                "footer": "Omni Keywords Finder",
                "ts": int(datetime.utcnow().timestamp())
            }]
        }
        
        return asyncio.create_task(self._send_webhook(payload))
    
    def send_interactive_message(self, channel: str, text: str, actions: List[Dict]):
        """Envia mensagem interativa com botões."""
        payload = {
            "channel": channel,
            "username": self.config.username,
            "icon_emoji": self.config.icon_emoji,
            "attachments": [{
                "text": text,
                "callback_id": "notification_actions",
                "actions": actions
            }]
        }
        
        return asyncio.create_task(self._send_webhook(payload))
    
    def get_templates(self) -> List[str]:
        """Retorna lista de templates disponíveis."""
        return list(self.message_templates.keys())
    
    def get_channels(self) -> List[str]:
        """Retorna lista de canais configurados."""
        channels = set([self.config.channel])
        channels.update(self.channel_mappings.values())
        return list(channels) 