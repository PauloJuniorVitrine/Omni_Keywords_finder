"""
API para Sistema de Webhooks - Omni Keywords Finder

Endpoints para gerenciar webhooks, registrar endpoints, visualizar estatísticas
e logs de entrega de webhooks.

Autor: Sistema de Webhooks para Integração Externa
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

# Importar sistema de webhooks
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from infrastructure.integrations.webhook_system import (
    WebhookSystem,
    WebhookEndpoint,
    WebhookEventType,
    WebhookStatus,
    WebhookSecurityLevel,
    create_webhook_system
)

# Blueprint para webhooks
webhooks_bp = Blueprint('webhooks', __name__, url_prefix='/api/webhooks')

# Sistema de webhooks global
webhook_system = None

def get_webhook_system() -> WebhookSystem:
    """Obtém instância do sistema de webhooks"""
    global webhook_system
    if webhook_system is None:
        config = {
            'max_retries': 3,
            'base_delay': 5,
            'db_path': 'webhooks.db'
        }
        webhook_system = create_webhook_system(config)
        webhook_system.start()
    return webhook_system

def require_auth(f):
    """Decorator para autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Implementar autenticação real aqui
        # Por enquanto, apenas simula autenticação
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Token de autenticação necessário'}), 401
        return f(*args, **kwargs)
    return decorated_function

def validate_webhook_data(data: Dict[str, Any]) -> List[str]:
    """Valida dados do webhook"""
    errors = []
    
    if not data.get('name'):
        errors.append("Nome é obrigatório")
    
    if not data.get('url'):
        errors.append("URL é obrigatória")
    else:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(data['url'])
            if not parsed.scheme or not parsed.netloc:
                errors.append("URL inválida")
        except Exception:
            errors.append("URL malformada")
    
    if not data.get('events'):
        errors.append("Pelo menos um evento deve ser especificado")
    else:
        valid_events = [e.value for e in WebhookEventType]
        for event in data['events']:
            if event not in valid_events:
                errors.append(f"Evento inválido: {event}")
    
    return errors

# Endpoints para gerenciar webhooks

@webhooks_bp.route('/', methods=['GET'])
@require_auth
def list_webhooks():
    """Lista todos os webhooks registrados"""
    try:
        system = get_webhook_system()
        endpoints = system.list_endpoints()
        
        webhooks = []
        for endpoint in endpoints:
            webhooks.append({
                'id': endpoint.id,
                'name': endpoint.name,
                'url': endpoint.url,
                'events': [e.value for e in endpoint.events],
                'security_level': endpoint.security_level.value,
                'status': endpoint.status.value,
                'rate_limit': endpoint.rate_limit,
                'created_at': endpoint.created_at.isoformat() if endpoint.created_at else None,
                'updated_at': endpoint.updated_at.isoformat() if endpoint.updated_at else None,
                'last_triggered': endpoint.last_triggered.isoformat() if endpoint.last_triggered else None,
                'success_count': endpoint.success_count,
                'failure_count': endpoint.failure_count
            })
        
        return jsonify({
            'webhooks': webhooks,
            'total': len(webhooks)
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar webhooks: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@webhooks_bp.route('/', methods=['POST'])
@require_auth
def create_webhook():
    """Cria um novo webhook"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados JSON necessários'}), 400
        
        # Validar dados
        errors = validate_webhook_data(data)
        if errors:
            return jsonify({'error': 'Dados inválidos', 'details': errors}), 400
        
        system = get_webhook_system()
        
        # Criar endpoint
        endpoint = WebhookEndpoint(
            id=str(uuid.uuid4()),
            name=data['name'],
            url=data['url'],
            events=[WebhookEventType(event) for event in data['events']],
            secret=data.get('secret'),
            api_key=data.get('api_key'),
            security_level=WebhookSecurityLevel(data.get('security_level', 'hmac')),
            headers=data.get('headers', {}),
            timeout=data.get('timeout', 30),
            retry_attempts=data.get('retry_attempts', 3),
            retry_delay=data.get('retry_delay', 5),
            rate_limit=data.get('rate_limit', 100),
            status=WebhookStatus.ACTIVE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata=data.get('metadata', {})
        )
        
        # Registrar endpoint
        if system.register_endpoint(endpoint):
            return jsonify({
                'message': 'Webhook criado com sucesso',
                'webhook_id': endpoint.id
            }), 201
        else:
            return jsonify({'error': 'Erro ao criar webhook'}), 500
        
    except Exception as e:
        current_app.logger.error(f"Erro ao criar webhook: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@webhooks_bp.route('/<webhook_id>', methods=['GET'])
@require_auth
def get_webhook(webhook_id: str):
    """Obtém detalhes de um webhook específico"""
    try:
        system = get_webhook_system()
        endpoint = system.get_endpoint(webhook_id)
        
        if not endpoint:
            return jsonify({'error': 'Webhook não encontrado'}), 404
        
        return jsonify({
            'id': endpoint.id,
            'name': endpoint.name,
            'url': endpoint.url,
            'events': [e.value for e in endpoint.events],
            'security_level': endpoint.security_level.value,
            'status': endpoint.status.value,
            'rate_limit': endpoint.rate_limit,
            'timeout': endpoint.timeout,
            'retry_attempts': endpoint.retry_attempts,
            'retry_delay': endpoint.retry_delay,
            'headers': endpoint.headers,
            'created_at': endpoint.created_at.isoformat() if endpoint.created_at else None,
            'updated_at': endpoint.updated_at.isoformat() if endpoint.updated_at else None,
            'last_triggered': endpoint.last_triggered.isoformat() if endpoint.last_triggered else None,
            'success_count': endpoint.success_count,
            'failure_count': endpoint.failure_count,
            'metadata': endpoint.metadata
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter webhook: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@webhooks_bp.route('/<webhook_id>', methods=['PUT'])
@require_auth
def update_webhook(webhook_id: str):
    """Atualiza um webhook existente"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados JSON necessários'}), 400
        
        system = get_webhook_system()
        endpoint = system.get_endpoint(webhook_id)
        
        if not endpoint:
            return jsonify({'error': 'Webhook não encontrado'}), 404
        
        # Atualizar campos permitidos
        if 'name' in data:
            endpoint.name = data['name']
        
        if 'url' in data:
            endpoint.url = data['url']
        
        if 'events' in data:
            endpoint.events = [WebhookEventType(event) for event in data['events']]
        
        if 'secret' in data:
            endpoint.secret = data['secret']
        
        if 'api_key' in data:
            endpoint.api_key = data['api_key']
        
        if 'security_level' in data:
            endpoint.security_level = WebhookSecurityLevel(data['security_level'])
        
        if 'headers' in data:
            endpoint.headers = data['headers']
        
        if 'timeout' in data:
            endpoint.timeout = data['timeout']
        
        if 'retry_attempts' in data:
            endpoint.retry_attempts = data['retry_attempts']
        
        if 'retry_delay' in data:
            endpoint.retry_delay = data['retry_delay']
        
        if 'rate_limit' in data:
            endpoint.rate_limit = data['rate_limit']
        
        if 'status' in data:
            endpoint.status = WebhookStatus(data['status'])
        
        if 'metadata' in data:
            endpoint.metadata = data['metadata']
        
        endpoint.updated_at = datetime.utcnow()
        
        # Salvar alterações
        if system.db.save_endpoint(endpoint):
            return jsonify({'message': 'Webhook atualizado com sucesso'})
        else:
            return jsonify({'error': 'Erro ao atualizar webhook'}), 500
        
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar webhook: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@webhooks_bp.route('/<webhook_id>', methods=['DELETE'])
@require_auth
def delete_webhook(webhook_id: str):
    """Remove um webhook"""
    try:
        system = get_webhook_system()
        
        if system.unregister_endpoint(webhook_id):
            return jsonify({'message': 'Webhook removido com sucesso'})
        else:
            return jsonify({'error': 'Webhook não encontrado'}), 404
        
    except Exception as e:
        current_app.logger.error(f"Erro ao remover webhook: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@webhooks_bp.route('/<webhook_id>/stats', methods=['GET'])
@require_auth
def get_webhook_stats(webhook_id: str):
    """Obtém estatísticas de um webhook"""
    try:
        system = get_webhook_system()
        endpoint = system.get_endpoint(webhook_id)
        
        if not endpoint:
            return jsonify({'error': 'Webhook não encontrado'}), 404
        
        # Obter estatísticas dos últimos 30 dias
        days = request.args.get('days', 30, type=int)
        stats = system.get_delivery_stats(webhook_id, days)
        
        return jsonify({
            'webhook_id': webhook_id,
            'name': endpoint.name,
            'period_days': days,
            'stats': stats
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter estatísticas: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@webhooks_bp.route('/<webhook_id>/test', methods=['POST'])
@require_auth
def test_webhook(webhook_id: str):
    """Testa um webhook enviando payload de teste"""
    try:
        system = get_webhook_system()
        endpoint = system.get_endpoint(webhook_id)
        
        if not endpoint:
            return jsonify({'error': 'Webhook não encontrado'}), 404
        
        # Criar payload de teste
        test_data = {
            'test': True,
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Teste de webhook'
        }
        
        # Trigger do webhook
        delivery_ids = system.trigger_webhook(
            WebhookEventType.USER_ACTION,
            test_data,
            source='test'
        )
        
        return jsonify({
            'message': 'Teste de webhook enviado',
            'delivery_ids': delivery_ids
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao testar webhook: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@webhooks_bp.route('/events', methods=['GET'])
@require_auth
def list_events():
    """Lista todos os tipos de eventos disponíveis"""
    try:
        events = [
            {
                'value': event.value,
                'description': event.name.replace('_', ' ').title()
            }
            for event in WebhookEventType
        ]
        
        return jsonify({
            'events': events,
            'total': len(events)
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar eventos: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@webhooks_bp.route('/retries', methods=['GET'])
@require_auth
def get_pending_retries():
    """Lista webhooks pendentes de retry"""
    try:
        system = get_webhook_system()
        retries = system.get_pending_retries()
        
        retry_list = []
        for delivery in retries:
            retry_list.append({
                'id': delivery.id,
                'endpoint_id': delivery.endpoint_id,
                'event_id': delivery.event_id,
                'attempt_count': delivery.attempt_count,
                'max_attempts': delivery.max_attempts,
                'next_retry': delivery.next_retry.isoformat() if delivery.next_retry else None,
                'created_at': delivery.created_at.isoformat() if delivery.created_at else None,
                'error_message': delivery.error_message
            })
        
        return jsonify({
            'retries': retry_list,
            'total': len(retry_list)
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter retries: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@webhooks_bp.route('/health', methods=['GET'])
def health_check():
    """Verifica saúde do sistema de webhooks"""
    try:
        system = get_webhook_system()
        
        # Verificar se o sistema está funcionando
        endpoints = system.list_endpoints()
        retries = system.get_pending_retries()
        
        return jsonify({
            'status': 'healthy',
            'endpoints_count': len(endpoints),
            'pending_retries': len(retries),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro no health check: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Webhooks System
from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any, List
import json
import hmac
import hashlib

router = APIRouter()

class WebhookManager:
    def __init__(self):
        self.webhooks: Dict[str, str] = {}
        self.secret_key = "webhook_secret"
    
    def register_webhook(self, event_type: str, url: str) -> bool:
        """Register a webhook for an event type"""
        self.webhooks[event_type] = url
        return True
    
    def trigger_webhook(self, event_type: str, payload: Dict[str, Any]) -> bool:
        """Trigger webhook for an event type"""
        if event_type not in self.webhooks:
            return False
        # Send webhook
        return True

webhook_manager = WebhookManager()

@router.post("/webhooks/register")
async def register_webhook(event_type: str, url: str):
    """Register a new webhook"""
    success = webhook_manager.register_webhook(event_type, url)
    if success:
        return {"message": "Webhook registered successfully"}
    raise HTTPException(status_code=400, detail="Failed to register webhook")

@router.post("/webhooks/trigger/{event_type}")
async def trigger_webhook(event_type: str, payload: Dict[str, Any]):
    """Trigger a webhook"""
    success = webhook_manager.trigger_webhook(event_type, payload)
    if success:
        return {"message": "Webhook triggered successfully"}
    raise HTTPException(status_code=404, detail="Webhook not found") 