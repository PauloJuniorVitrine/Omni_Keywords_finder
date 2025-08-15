"""
API para Sistema de Notificações Avançado

Endpoints para gerenciar notificações, templates, preferências de usuário
e integração com múltiplos canais de notificação.

Autor: Sistema de Notificações Avançado
Data: 2024-12-19
Ruleset: enterprise_control_layer.yaml
"""

from flask import Blueprint, request, jsonify, current_app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import uuid
from functools import wraps

# Importar sistema de notificações
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from infrastructure.notifications.advanced_notification_system import (
    AdvancedNotificationSystem,
    Notification,
    NotificationType,
    NotificationChannel,
    NotificationTemplate,
    UserPreferences,
    create_notification_system
)

# Blueprint para notificações avançadas
advanced_notifications_bp = Blueprint('advanced_notifications', __name__, url_prefix='/api/notifications')

# Sistema de notificações global
notification_system = None

def get_notification_system() -> AdvancedNotificationSystem:
    """Obtém instância do sistema de notificações"""
    global notification_system
    if notification_system is None:
        config = {
            'smtp_host': current_app.config.get('SMTP_HOST', 'localhost'),
            'smtp_port': current_app.config.get('SMTP_PORT', 587),
            'smtp_user': current_app.config.get('SMTP_USER'),
            'smtp_password': current_app.config.get('SMTP_PASSWORD'),
            'from_email': current_app.config.get('FROM_EMAIL', 'noreply@omnikeywords.com'),
            'slack_webhook_url': current_app.config.get('SLACK_WEBHOOK_URL'),
            'discord_webhook_url': current_app.config.get('DISCORD_WEBHOOK_URL'),
            'push_enabled': current_app.config.get('PUSH_ENABLED', False)
        }
        notification_system = create_notification_system(config)
    return notification_system

def require_auth(f):
    """Decorator para autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Implementar autenticação real aqui
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Token de autenticação necessário'}), 401
        
        # Validação básica - em produção usar JWT ou similar
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token inválido'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def get_user_id_from_request() -> str:
    """Extrai user_id do request"""
    # Em produção, extrair do token JWT
    return request.headers.get('X-User-ID', 'anonymous')

# Endpoints para notificações
@advanced_notifications_bp.route('', methods=['GET'])
@require_auth
def list_notifications():
    """Lista notificações do usuário"""
    try:
        user_id = get_user_id_from_request()
        system = get_notification_system()
        
        # Parâmetros de filtro
        notification_type = request.args.get('type')
        channel = request.args.get('channel')
        read_status = request.args.get('read', 'all')
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        
        # Em produção, buscar do banco de dados
        # Por enquanto, retornar lista vazia
        notifications = []
        
        # Aplicar filtros
        if notification_type:
            notifications = [n for n in notifications if n.notification_type.value == notification_type]
        
        if channel:
            notifications = [n for n in notifications if channel in [c.value for c in n.channels]]
        
        if read_status == 'read':
            notifications = [n for n in notifications if n.read_at]
        elif read_status == 'unread':
            notifications = [n for n in notifications if not n.read_at]
        
        # Paginação
        notifications = notifications[offset:offset + limit]
        
        return jsonify([{
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'type': n.notification_type.value,
            'channel': [c.value for c in n.channels],
            'priority': n.priority,
            'user_id': n.user_id,
            'template_id': n.template_id,
            'variables': n.variables,
            'created_at': n.created_at.isoformat() + 'Z',
            'sent_at': n.sent_at.isoformat() + 'Z' if n.sent_at else None,
            'read_at': n.read_at.isoformat() + 'Z' if n.read_at else None,
            'metadata': n.metadata
        } for n in notifications])
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar notificações: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@advanced_notifications_bp.route('', methods=['POST'])
@require_auth
def create_notification():
    """Cria nova notificação"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados JSON necessários'}), 400
        
        # Validação dos campos obrigatórios
        required_fields = ['title', 'message']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo obrigatório: {field}'}), 400
        
        # Criar notificação
        notification = Notification(
            id=str(uuid.uuid4()),
            title=data['title'],
            message=data['message'],
            notification_type=NotificationType(data.get('type', 'info')),
            user_id=data.get('user_id', get_user_id_from_request()),
            channels=[NotificationChannel(c) for c in data.get('channels', ['in_app'])],
            priority=data.get('priority', 1),
            template_id=data.get('template_id'),
            variables=data.get('variables'),
            created_at=datetime.utcnow(),
            metadata=data.get('metadata')
        )
        
        # Enviar notificação
        system = get_notification_system()
        success = system.send_notification(notification)
        
        if success:
            return jsonify({
                'id': notification.id,
                'message': 'Notificação criada com sucesso'
            }), 201
        else:
            return jsonify({'error': 'Erro ao enviar notificação'}), 500
            
    except ValueError as e:
        return jsonify({'error': f'Valor inválido: {str(e)}'}), 400
    except Exception as e:
        current_app.logger.error(f"Erro ao criar notificação: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@advanced_notifications_bp.route('/<notification_id>', methods=['GET'])
@require_auth
def get_notification(notification_id: str):
    """Obtém notificação específica"""
    try:
        user_id = get_user_id_from_request()
        
        # Em produção, buscar do banco de dados
        # Por enquanto, retornar erro 404
        return jsonify({'error': 'Notificação não encontrada'}), 404
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter notificação: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@advanced_notifications_bp.route('/<notification_id>/read', methods=['PATCH'])
@require_auth
def mark_as_read(notification_id: str):
    """Marca notificação como lida"""
    try:
        user_id = get_user_id_from_request()
        
        # Em produção, atualizar no banco de dados
        # Por enquanto, retornar sucesso
        return jsonify({'message': 'Notificação marcada como lida'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao marcar notificação como lida: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@advanced_notifications_bp.route('/<notification_id>', methods=['DELETE'])
@require_auth
def delete_notification(notification_id: str):
    """Exclui notificação"""
    try:
        user_id = get_user_id_from_request()
        
        # Em produção, excluir do banco de dados
        # Por enquanto, retornar sucesso
        return jsonify({'message': 'Notificação excluída'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao excluir notificação: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# Endpoints para preferências de usuário
@advanced_notifications_bp.route('/preferences/<user_id>', methods=['GET'])
@require_auth
def get_user_preferences(user_id: str):
    """Obtém preferências de notificação do usuário"""
    try:
        system = get_notification_system()
        preferences = system.get_user_preferences(user_id)
        
        return jsonify({
            'user_id': preferences.user_id,
            'email_enabled': preferences.email_enabled,
            'slack_enabled': preferences.slack_enabled,
            'discord_enabled': preferences.discord_enabled,
            'push_enabled': preferences.push_enabled,
            'in_app_enabled': preferences.in_app_enabled,
            'webhook_enabled': preferences.webhook_enabled,
            'webhook_url': preferences.webhook_url,
            'email_address': preferences.email_address,
            'slack_channel': preferences.slack_channel,
            'discord_webhook': preferences.discord_webhook,
            'notification_types': [t.value for t in preferences.notification_types] if preferences.notification_types else [],
            'quiet_hours_start': preferences.quiet_hours_start,
            'quiet_hours_end': preferences.quiet_hours_end,
            'timezone': preferences.timezone
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter preferências: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@advanced_notifications_bp.route('/preferences/<user_id>', methods=['PUT'])
@require_auth
def update_user_preferences(user_id: str):
    """Atualiza preferências de notificação do usuário"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados JSON necessários'}), 400
        
        system = get_notification_system()
        
        # Criar objeto de preferências
        preferences = UserPreferences(
            user_id=user_id,
            email_enabled=data.get('email_enabled', True),
            slack_enabled=data.get('slack_enabled', False),
            discord_enabled=data.get('discord_enabled', False),
            push_enabled=data.get('push_enabled', True),
            in_app_enabled=data.get('in_app_enabled', True),
            webhook_enabled=data.get('webhook_enabled', False),
            webhook_url=data.get('webhook_url'),
            email_address=data.get('email_address'),
            slack_channel=data.get('slack_channel'),
            discord_webhook=data.get('discord_webhook'),
            notification_types=[NotificationType(t) for t in data.get('notification_types', [])],
            quiet_hours_start=data.get('quiet_hours_start', '22:00'),
            quiet_hours_end=data.get('quiet_hours_end', '08:00'),
            timezone=data.get('timezone', 'UTC')
        )
        
        success = system.update_user_preferences(user_id, preferences)
        
        if success:
            return jsonify({'message': 'Preferências atualizadas com sucesso'}), 200
        else:
            return jsonify({'error': 'Erro ao atualizar preferências'}), 500
            
    except ValueError as e:
        return jsonify({'error': f'Valor inválido: {str(e)}'}), 400
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar preferências: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# Endpoints para templates
@advanced_notifications_bp.route('/templates', methods=['GET'])
@require_auth
def list_templates():
    """Lista templates de notificação"""
    try:
        system = get_notification_system()
        templates = system.list_templates()
        
        return jsonify([{
            'id': t.id,
            'name': t.name,
            'subject': t.subject,
            'body': t.body,
            'variables': t.variables,
            'channels': [c.value for c in t.channels],
            'created_at': t.created_at.isoformat() + 'Z',
            'updated_at': t.updated_at.isoformat() + 'Z'
        } for t in templates])
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar templates: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@advanced_notifications_bp.route('/templates', methods=['POST'])
@require_auth
def create_template():
    """Cria novo template de notificação"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados JSON necessários'}), 400
        
        # Validação dos campos obrigatórios
        required_fields = ['name', 'subject', 'body']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo obrigatório: {field}'}), 400
        
        # Criar template
        template = NotificationTemplate(
            id=str(uuid.uuid4()),
            name=data['name'],
            subject=data['subject'],
            body=data['body'],
            variables=data.get('variables', []),
            channels=[NotificationChannel(c) for c in data.get('channels', ['in_app'])],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Salvar template
        system = get_notification_system()
        success = system.create_template(template)
        
        if success:
            return jsonify({
                'id': template.id,
                'message': 'Template criado com sucesso'
            }), 201
        else:
            return jsonify({'error': 'Erro ao criar template'}), 500
            
    except ValueError as e:
        return jsonify({'error': f'Valor inválido: {str(e)}'}), 400
    except Exception as e:
        current_app.logger.error(f"Erro ao criar template: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@advanced_notifications_bp.route('/templates/<template_id>', methods=['GET'])
@require_auth
def get_template(template_id: str):
    """Obtém template específico"""
    try:
        system = get_notification_system()
        template = system.get_template(template_id)
        
        if not template:
            return jsonify({'error': 'Template não encontrado'}), 404
        
        return jsonify({
            'id': template.id,
            'name': template.name,
            'subject': template.subject,
            'body': template.body,
            'variables': template.variables,
            'channels': [c.value for c in template.channels],
            'created_at': template.created_at.isoformat() + 'Z',
            'updated_at': template.updated_at.isoformat() + 'Z'
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter template: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# Endpoints para estatísticas
@advanced_notifications_bp.route('/stats/<user_id>', methods=['GET'])
@require_auth
def get_notification_stats(user_id: str):
    """Obtém estatísticas de notificações do usuário"""
    try:
        days = int(request.args.get('days', 30))
        system = get_notification_system()
        stats = system.get_notification_stats(user_id, days)
        
        return jsonify(stats)
        
    except ValueError as e:
        return jsonify({'error': f'Valor inválido: {str(e)}'}), 400
    except Exception as e:
        current_app.logger.error(f"Erro ao obter estatísticas: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# Endpoints para testes
@advanced_notifications_bp.route('/test', methods=['POST'])
@require_auth
def test_notification():
    """Endpoint para testar notificações"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados JSON necessários'}), 400
        
        user_id = get_user_id_from_request()
        
        # Criar notificação de teste
        notification = Notification(
            id=str(uuid.uuid4()),
            title=data.get('title', 'Teste de Notificação'),
            message=data.get('message', 'Esta é uma notificação de teste'),
            notification_type=NotificationType(data.get('type', 'info')),
            user_id=user_id,
            channels=[NotificationChannel(c) for c in data.get('channels', ['in_app'])],
            priority=data.get('priority', 1),
            created_at=datetime.utcnow()
        )
        
        # Enviar notificação
        system = get_notification_system()
        success = system.send_notification(notification)
        
        if success:
            return jsonify({
                'id': notification.id,
                'message': 'Notificação de teste enviada com sucesso'
            }), 200
        else:
            return jsonify({'error': 'Erro ao enviar notificação de teste'}), 500
            
    except ValueError as e:
        return jsonify({'error': f'Valor inválido: {str(e)}'}), 400
    except Exception as e:
        current_app.logger.error(f"Erro ao enviar notificação de teste: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# Endpoints para WebSocket
@advanced_notifications_bp.route('/websocket/connect', methods=['POST'])
@require_auth
def websocket_connect():
    """Endpoint para conectar WebSocket"""
    try:
        user_id = get_user_id_from_request()
        
        # Em produção, gerar token de conexão WebSocket
        connection_token = str(uuid.uuid4())
        
        return jsonify({
            'connection_token': connection_token,
            'websocket_url': f'ws://localhost:8765?token={connection_token}'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao conectar WebSocket: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# Endpoints para configuração
@advanced_notifications_bp.route('/config', methods=['GET'])
@require_auth
def get_config():
    """Obtém configuração do sistema de notificações"""
    try:
        system = get_notification_system()
        
        return jsonify({
            'smtp_configured': bool(system.config.get('smtp_user')),
            'slack_configured': bool(system.config.get('slack_webhook_url')),
            'discord_configured': bool(system.config.get('discord_webhook_url')),
            'push_configured': bool(system.config.get('push_enabled')),
            'websocket_port': system.config.get('websocket_port', 8765)
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter configuração: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# Health check
@advanced_notifications_bp.route('/health', methods=['GET'])
def health_check():
    """Health check do sistema de notificações"""
    try:
        system = get_notification_system()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'version': '1.0.0'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro no health check: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500 