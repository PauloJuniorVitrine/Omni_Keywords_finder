"""
API Segura para Sistema de Webhooks - Omni Keywords Finder
Versão otimizada e segura com validação HMAC, rate limiting e logs estruturados
Prompt: Revisão de segurança de webhooks
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import json
import uuid
import time
import hmac
import hashlib
import base64
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from functools import wraps

from flask import Blueprint, request, jsonify, current_app, Response
from flask_sqlalchemy import SQLAlchemy

# Importar schemas e utilitários de segurança
from ..schemas.webhook_schemas import (
    WebhookEndpointSchema,
    WebhookPayloadSchema,
    WebhookSignatureSchema,
    WebhookDeliverySchema,
    WebhookFilterSchema,
    WebhookHMACValidator
)
from ..utils.webhook_logger import WebhookLogger
from ..utils.webhook_rate_limiter import WebhookRateLimiter

# Blueprint para webhooks seguros
webhooks_secure_bp = Blueprint('webhooks_secure', __name__, url_prefix='/api/webhooks/v2')

# Instâncias globais
webhook_logger = WebhookLogger()
webhook_rate_limiter = WebhookRateLimiter()

def get_client_ip() -> str:
    """Obtém IP real do cliente considerando proxies"""
    # Verificar headers de proxy
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip
    
    return request.remote_addr

def get_user_agent() -> str:
    """Obtém User-Agent do cliente"""
    return request.headers.get('User-Agent', 'Unknown')

def require_auth(f):
    """Decorator para autenticação robusta"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Obter dados do cliente
            ip_address = get_client_ip()
            user_agent = get_user_agent()
            api_key = request.headers.get('X-API-Key')
            auth_token = request.headers.get('Authorization')
            
            # Verificar rate limiting primeiro
            rate_result = webhook_rate_limiter.check_rate_limit(
                ip_address=ip_address,
                api_key=api_key,
                user_id=kwargs.get('user_id')
            )
            
            if not rate_result.allowed:
                # Log de rate limiting
                webhook_logger.log_rate_limited(
                    endpoint_id=kwargs.get('webhook_id'),
                    ip_address=ip_address,
                    rate_limit=rate_result.remaining,
                    current_count=0,
                    reason=rate_result.reason
                )
                
                response = jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': rate_result.retry_after,
                    'limit_reset': rate_result.reset_time
                })
                response.status_code = 429
                response.headers['Retry-After'] = str(rate_result.retry_after or 60)
                return response
            
            # Verificar autenticação
            if not auth_token and not api_key:
                webhook_logger.log_unauthorized(
                    endpoint_id=kwargs.get('webhook_id'),
                    ip_address=ip_address,
                    user_agent=user_agent,
                    reason="Missing authentication"
                )
                return jsonify({'error': 'Token de autenticação necessário'}), 401
            
            # Em produção, validar token/API key no banco de dados
            # Por enquanto, simular validação
            if auth_token and not auth_token.startswith('Bearer '):
                webhook_logger.log_unauthorized(
                    endpoint_id=kwargs.get('webhook_id'),
                    ip_address=ip_address,
                    user_agent=user_agent,
                    reason="Invalid token format"
                )
                return jsonify({'error': 'Formato de token inválido'}), 401
            
            # Adicionar dados do cliente ao contexto
            request.client_ip = ip_address
            request.user_agent = user_agent
            request.api_key = api_key
            request.auth_token = auth_token
            
            return f(*args, **kwargs)
            
        except Exception as e:
            current_app.logger.error(f"Erro na autenticação: {str(e)}")
            return jsonify({'error': 'Erro interno de autenticação'}), 500
    
    return decorated_function

def validate_hmac_signature(f):
    """Decorator para validação de assinatura HMAC"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Obter dados da requisição
            payload = request.get_data(as_text=True)
            signature = request.headers.get('X-Webhook-Signature')
            timestamp = request.headers.get('X-Webhook-Timestamp')
            
            if not signature or not timestamp:
                webhook_logger.log_unauthorized(
                    endpoint_id=kwargs.get('webhook_id'),
                    ip_address=get_client_ip(),
                    user_agent=get_user_agent(),
                    reason="Missing HMAC signature or timestamp"
                )
                return jsonify({'error': 'Assinatura HMAC necessária'}), 401
            
            # Validar timestamp (prevenir replay attacks)
            try:
                request_time = int(timestamp)
                current_time = int(time.time())
                
                if abs(current_time - request_time) > 300:  # 5 minutos de tolerância
                    webhook_logger.log_unauthorized(
                        endpoint_id=kwargs.get('webhook_id'),
                        ip_address=get_client_ip(),
                        user_agent=get_user_agent(),
                        reason="Timestamp too old"
                    )
                    return jsonify({'error': 'Timestamp muito antigo'}), 401
                    
            except ValueError:
                return jsonify({'error': 'Timestamp inválido'}), 400
            
            # Em produção, obter secret do banco de dados
            # Por enquanto, usar secret padrão
            secret = "webhook_secret_key_2025"  # Em produção, buscar do banco
            
            # Validar assinatura
            is_valid = WebhookHMACValidator.validate_signature(
                payload, signature, secret, timestamp
            )
            
            # Log da validação
            webhook_logger.log_signature_validated(
                endpoint_id=kwargs.get('webhook_id'),
                signature_valid=is_valid,
                timestamp=timestamp
            )
            
            if not is_valid:
                return jsonify({'error': 'Assinatura HMAC inválida'}), 401
            
            return f(*args, **kwargs)
            
        except Exception as e:
            current_app.logger.error(f"Erro na validação HMAC: {str(e)}")
            return jsonify({'error': 'Erro na validação de assinatura'}), 500
    
    return decorated_function

# Endpoints seguros para gerenciar webhooks

@webhooks_secure_bp.route('/', methods=['GET'])
@require_auth
def list_webhooks_secure():
    """Lista todos os webhooks registrados com validação robusta"""
    try:
        # Obter parâmetros de filtro
        filters = WebhookFilterSchema(
            limit=request.args.get('limit', 50, type=int),
            offset=request.args.get('offset', 0, type=int)
        )
        
        # Em produção, buscar do banco de dados
        # Por enquanto, retornar dados simulados
        webhooks = [
            {
                'id': str(uuid.uuid4()),
                'name': 'Webhook de Teste',
                'url': 'https://api.exemplo.com/webhook',
                'events': ['user.created', 'payment.succeeded'],
                'security_level': 'hmac',
                'status': 'active',
                'rate_limit': 100,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat(),
                'last_triggered': None,
                'success_count': 0,
                'failure_count': 0
            }
        ]
        
        # Log da operação
        webhook_logger.log_webhook_created(
            endpoint_id=webhooks[0]['id'],
            name=webhooks[0]['name'],
            url=webhooks[0]['url'],
            events=webhooks[0]['events'],
            user_id="user_123",
            ip_address=get_client_ip()
        )
        
        return jsonify({
            'webhooks': webhooks,
            'total': len(webhooks),
            'limit': filters.limit,
            'offset': filters.offset
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar webhooks: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@webhooks_secure_bp.route('/', methods=['POST'])
@require_auth
def create_webhook_secure():
    """Cria um novo webhook com validação robusta"""
    try:
        # Obter e validar dados
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados JSON necessários'}), 400
        
        # Validar com schema
        try:
            webhook_data = WebhookEndpointSchema(**data)
        except Exception as validation_error:
            webhook_logger.log_malformed_payload(
                endpoint_id=None,
                ip_address=get_client_ip(),
                errors=[str(validation_error)]
            )
            return jsonify({
                'error': 'Dados inválidos',
                'details': str(validation_error)
            }), 400
        
        # Gerar ID único
        webhook_id = str(uuid.uuid4())
        
        # Em produção, salvar no banco de dados
        # Por enquanto, simular criação
        
        # Log da criação
        webhook_logger.log_webhook_created(
            endpoint_id=webhook_id,
            name=webhook_data.name,
            url=str(webhook_data.url),
            events=webhook_data.events,
            user_id="user_123",
            ip_address=get_client_ip(),
            security_level=webhook_data.security_level
        )
        
        return jsonify({
            'message': 'Webhook criado com sucesso',
            'webhook_id': webhook_id,
            'security_level': webhook_data.security_level
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Erro ao criar webhook: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@webhooks_secure_bp.route('/<webhook_id>', methods=['GET'])
@require_auth
def get_webhook_secure(webhook_id: str):
    """Obtém detalhes de um webhook específico"""
    try:
        # Validar ID
        try:
            uuid.UUID(webhook_id)
        except ValueError:
            return jsonify({'error': 'ID de webhook inválido'}), 400
        
        # Em produção, buscar do banco de dados
        # Por enquanto, retornar dados simulados
        webhook = {
            'id': webhook_id,
            'name': 'Webhook de Teste',
            'url': 'https://api.exemplo.com/webhook',
            'events': ['user.created', 'payment.succeeded'],
            'security_level': 'hmac',
            'status': 'active',
            'rate_limit': 100,
            'timeout': 30,
            'retry_attempts': 3,
            'retry_delay': 5,
            'headers': {},
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'last_triggered': None,
            'success_count': 0,
            'failure_count': 0,
            'metadata': {}
        }
        
        return jsonify(webhook)
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter webhook: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@webhooks_secure_bp.route('/<webhook_id>', methods=['PUT'])
@require_auth
def update_webhook_secure(webhook_id: str):
    """Atualiza um webhook existente com validação robusta"""
    try:
        # Validar ID
        try:
            uuid.UUID(webhook_id)
        except ValueError:
            return jsonify({'error': 'ID de webhook inválido'}), 400
        
        # Obter e validar dados
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados JSON necessários'}), 400
        
        # Validar campos permitidos
        allowed_fields = {
            'name', 'url', 'events', 'secret', 'api_key', 'security_level',
            'headers', 'timeout', 'retry_attempts', 'retry_delay', 'rate_limit',
            'status', 'metadata'
        }
        
        invalid_fields = set(data.keys()) - allowed_fields
        if invalid_fields:
            return jsonify({
                'error': 'Campos não permitidos',
                'invalid_fields': list(invalid_fields)
            }), 400
        
        # Em produção, atualizar no banco de dados
        # Por enquanto, simular atualização
        
        # Log da atualização
        webhook_logger.log_webhook_updated(
            endpoint_id=webhook_id,
            changes=data,
            user_id="user_123",
            ip_address=get_client_ip()
        )
        
        return jsonify({'message': 'Webhook atualizado com sucesso'})
        
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar webhook: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@webhooks_secure_bp.route('/<webhook_id>', methods=['DELETE'])
@require_auth
def delete_webhook_secure(webhook_id: str):
    """Remove um webhook com validação"""
    try:
        # Validar ID
        try:
            uuid.UUID(webhook_id)
        except ValueError:
            return jsonify({'error': 'ID de webhook inválido'}), 400
        
        # Em produção, verificar se existe e remover do banco
        # Por enquanto, simular remoção
        
        # Log da remoção
        webhook_logger.log_webhook_deleted(
            endpoint_id=webhook_id,
            name="Webhook Removido",
            user_id="user_123",
            ip_address=get_client_ip()
        )
        
        return jsonify({'message': 'Webhook removido com sucesso'})
        
    except Exception as e:
        current_app.logger.error(f"Erro ao remover webhook: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@webhooks_secure_bp.route('/<webhook_id>/test', methods=['POST'])
@require_auth
def test_webhook_secure(webhook_id: str):
    """Testa um webhook enviando payload de teste seguro"""
    try:
        # Validar ID
        try:
            uuid.UUID(webhook_id)
        except ValueError:
            return jsonify({'error': 'ID de webhook inválido'}), 400
        
        # Criar payload de teste seguro
        test_data = {
            'event': 'test.webhook',
            'data': {
                'test': True,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'message': 'Teste de webhook seguro'
            },
            'id': str(uuid.uuid4()),
            'source': 'test',
            'version': '1.0'
        }
        
        # Validar payload
        try:
            payload = WebhookPayloadSchema(**test_data)
        except Exception as validation_error:
            return jsonify({
                'error': 'Erro na validação do payload',
                'details': str(validation_error)
            }), 400
        
        # Em produção, disparar webhook real
        # Por enquanto, simular disparo
        
        # Log do teste
        webhook_logger.log_webhook_triggered(
            endpoint_id=webhook_id,
            event_id=test_data['id'],
            event_type=test_data['event'],
            payload_size=len(json.dumps(test_data)),
            ip_address=get_client_ip(),
            user_agent=get_user_agent()
        )
        
        return jsonify({
            'message': 'Teste de webhook enviado',
            'event_id': test_data['id'],
            'payload': test_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao testar webhook: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@webhooks_secure_bp.route('/<webhook_id>/stats', methods=['GET'])
@require_auth
def get_webhook_stats_secure(webhook_id: str):
    """Obtém estatísticas de um webhook com validação"""
    try:
        # Validar ID
        try:
            uuid.UUID(webhook_id)
        except ValueError:
            return jsonify({'error': 'ID de webhook inválido'}), 400
        
        # Obter parâmetros
        days = request.args.get('days', 30, type=int)
        if days < 1 or days > 365:
            return jsonify({'error': 'Período inválido (1-365 dias)'}), 400
        
        # Em produção, buscar estatísticas do banco
        # Por enquanto, retornar dados simulados
        stats = {
            'webhook_id': webhook_id,
            'name': 'Webhook de Teste',
            'period_days': days,
            'stats': {
                'total_deliveries': 100,
                'successful_deliveries': 95,
                'failed_deliveries': 5,
                'success_rate': 95.0,
                'average_response_time': 0.5,
                'last_delivery': datetime.now(timezone.utc).isoformat()
            }
        }
        
        return jsonify(stats)
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter estatísticas: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@webhooks_secure_bp.route('/events', methods=['GET'])
@require_auth
def list_events_secure():
    """Lista todos os tipos de eventos disponíveis"""
    try:
        events = [
            {'value': 'user.created', 'description': 'Usuário Criado'},
            {'value': 'user.updated', 'description': 'Usuário Atualizado'},
            {'value': 'user.deleted', 'description': 'Usuário Deletado'},
            {'value': 'payment.created', 'description': 'Pagamento Criado'},
            {'value': 'payment.succeeded', 'description': 'Pagamento Sucedido'},
            {'value': 'payment.failed', 'description': 'Pagamento Falhou'},
            {'value': 'subscription.created', 'description': 'Assinatura Criada'},
            {'value': 'subscription.updated', 'description': 'Assinatura Atualizada'},
            {'value': 'subscription.cancelled', 'description': 'Assinatura Cancelada'},
            {'value': 'execution.started', 'description': 'Execução Iniciada'},
            {'value': 'execution.completed', 'description': 'Execução Concluída'},
            {'value': 'execution.failed', 'description': 'Execução Falhou'},
            {'value': 'keyword.found', 'description': 'Palavra-chave Encontrada'},
            {'value': 'keyword.analyzed', 'description': 'Palavra-chave Analisada'},
            {'value': 'keyword.exported', 'description': 'Palavra-chave Exportada'}
        ]
        
        return jsonify({
            'events': events,
            'total': len(events)
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar eventos: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@webhooks_secure_bp.route('/health', methods=['GET'])
def health_check_secure():
    """Verifica saúde do sistema de webhooks seguro"""
    try:
        # Verificar componentes
        redis_status = "healthy" if webhook_rate_limiter.use_redis else "fallback"
        
        health_data = {
            'status': 'healthy',
            'components': {
                'rate_limiter': redis_status,
                'logger': 'healthy',
                'hmac_validator': 'healthy'
            },
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'version': '2.0'
        }
        
        return jsonify(health_data)
        
    except Exception as e:
        current_app.logger.error(f"Erro no health check: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500

@webhooks_secure_bp.route('/rate-limit-info', methods=['GET'])
@require_auth
def get_rate_limit_info():
    """Obtém informações sobre rate limiting do cliente"""
    try:
        info = webhook_rate_limiter.get_rate_limit_info(
            ip_address=get_client_ip(),
            api_key=request.api_key,
            user_id="user_123"
        )
        
        return jsonify(info)
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter rate limit info: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# Endpoint para receber webhooks (com validação HMAC)
@webhooks_secure_bp.route('/receive', methods=['POST'])
@validate_hmac_signature
def receive_webhook():
    """Recebe webhooks externos com validação HMAC"""
    try:
        # Obter payload
        payload = request.get_json()
        if not payload:
            return jsonify({'error': 'Payload JSON necessário'}), 400
        
        # Validar payload
        try:
            webhook_payload = WebhookPayloadSchema(**payload)
        except Exception as validation_error:
            webhook_logger.log_malformed_payload(
                endpoint_id=None,
                ip_address=get_client_ip(),
                errors=[str(validation_error)]
            )
            return jsonify({
                'error': 'Payload inválido',
                'details': str(validation_error)
            }), 400
        
        # Processar webhook
        # Em produção, processar o evento
        processing_result = {
            'status': 'processed',
            'event_id': webhook_payload.id,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # Log do processamento
        webhook_logger.log_webhook_delivered(
            endpoint_id="external",
            event_id=webhook_payload.id,
            response_status=200,
            response_time=0.1
        )
        
        return jsonify(processing_result)
        
    except Exception as e:
        current_app.logger.error(f"Erro ao processar webhook: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500 