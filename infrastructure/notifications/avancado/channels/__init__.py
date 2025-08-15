from typing import Dict, List, Optional, Any
"""
Canais de Notificação - Omni Keywords Finder
============================================

Este módulo contém os diferentes canais de notificação disponíveis:
- WebSocket (tempo real)
- Email (SMTP)
- Slack (webhook)
- SMS (simulado)

Tracing ID: NOTIF_20241219_001
Autor: Sistema de Notificações Avançado
Data: 2024-12-19
Versão: 1.0.0
"""

from .websocket_channel import WebSocketChannel
from .email_channel import EmailChannel
from .slack_channel import SlackChannel
from .sms_channel import SMSChannel

__all__ = [
    'WebSocketChannel',
    'EmailChannel', 
    'SlackChannel',
    'SMSChannel'
] 