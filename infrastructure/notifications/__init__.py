from typing import Dict, List, Optional, Any
"""
Módulo de Notificações Avançado

Este módulo fornece funcionalidades completas de notificações para o sistema
Omni Keywords Finder, incluindo notificações em tempo real, email, Slack,
Discord, push notifications e webhooks.

Funcionalidades:
- Notificações em tempo real via WebSocket
- Integração com email (SMTP)
- Webhooks para Slack/Discord
- Notificações push
- Sistema de templates personalizáveis
- Preferências de usuário configuráveis
- Quiet hours e agendamento

Autor: Sistema de Notificações Avançado
Data: 2024-12-19
Ruleset: enterprise_control_layer.yaml
"""

from .advanced_notification_system import (
    AdvancedNotificationSystem,
    Notification,
    NotificationType,
    NotificationChannel,
    NotificationTemplate,
    UserPreferences,
    EmailNotifier,
    SlackNotifier,
    DiscordNotifier,
    PushNotifier,
    WebhookNotifier,
    TemplateManager,
    create_notification_system
)

__all__ = [
    'AdvancedNotificationSystem',
    'Notification',
    'NotificationType',
    'NotificationChannel',
    'NotificationTemplate',
    'UserPreferences',
    'EmailNotifier',
    'SlackNotifier',
    'DiscordNotifier',
    'PushNotifier',
    'WebhookNotifier',
    'TemplateManager',
    'create_notification_system'
] 