"""
API de Pagamentos - Omni Keywords Finder
Integração real com Stripe para processamento seguro de pagamentos
Prompt: Implementação real de pagamentos
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import os
import logging
import hmac
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import Blueprint, request, jsonify, current_app
from backend.app.utils.log_event import log_event
from backend.app.utils.payment_logger import payment_security_logger
from backend.app.middleware.auth_middleware import auth_required
from backend.app.schemas.payment_schemas import (
    PaymentCreateSchema, PaymentUpdateSchema, PaymentFilterSchema, 
    PaymentResponseSchema, PaymentCardSchema, PixSchema, BoletoSchema
)
from infrastructure.security.ip_whitelist import is_ip_allowed

# Importar Stripe
try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    logging.warning("Stripe não disponível. Instale com: pip install stripe")

payments_bp = Blueprint('payments', __name__, url_prefix='/api/payments')

# Configurar Stripe
if STRIPE_AVAILABLE:
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    if not stripe.api_key:
        logging.error("STRIPE_SECRET_KEY não configurada")

class PaymentService:
    """Serviço para processamento de pagamentos"""
    
    def __init__(self):
        self.stripe_available = STRIPE_AVAILABLE and stripe.api_key is not None
    
    def create_payment_intent(self, amount: int, currency: str = 'brl', 
                            metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Cria um PaymentIntent no Stripe
        
        Args:
            amount: Valor em centavos
            currency: Moeda (padrão: brl)
            metadata: Metadados adicionais
            
        Returns:
            Dicionário com dados do PaymentIntent
        """
        if not self.stripe_available:
            raise Exception("Stripe não configurado")
        
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                metadata=metadata or {},
                automatic_payment_methods={
                    'enabled': True,
                }
            )
            
            log_event('info', 'Payment', 
                     detalhes=f'PaymentIntent criado: {payment_intent.id}, valor: {amount/100}')
            
            return {
                'id': payment_intent.id,
                'client_secret': payment_intent.client_secret,
                'amount': payment_intent.amount,
                'currency': payment_intent.currency,
                'status': payment_intent.status
            }
            
        except stripe.error.StripeError as e:
            log_event('erro', 'Payment', detalhes=f'Erro Stripe: {str(e)}')
            raise Exception(f"Erro no processamento de pagamento: {str(e)}")
    
    def retrieve_payment_intent(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Recupera um PaymentIntent do Stripe
        
        Args:
            payment_intent_id: ID do PaymentIntent
            
        Returns:
            Dados do PaymentIntent
        """
        if not self.stripe_available:
            raise Exception("Stripe não configurado")
        
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                'id': payment_intent.id,
                'amount': payment_intent.amount,
                'currency': payment_intent.currency,
                'status': payment_intent.status,
                'payment_method': payment_intent.payment_method,
                'created': payment_intent.created,
                'metadata': payment_intent.metadata
            }
            
        except stripe.error.StripeError as e:
            log_event('erro', 'Payment', detalhes=f'Erro ao recuperar PaymentIntent: {str(e)}')
            raise Exception(f"Erro ao recuperar pagamento: {str(e)}")
    
    def validate_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Valida assinatura do webhook do Stripe
        
        Args:
            payload: Corpo da requisição
            signature: Assinatura do header
            
        Returns:
            True se assinatura válida
        """
        webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        if not webhook_secret:
            logging.error("STRIPE_WEBHOOK_SECRET não configurada")
            return False
        
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            return True
        except ValueError as e:
            logging.error(f"Payload inválido: {e}")
            return False
        except stripe.error.SignatureVerificationError as e:
            logging.error(f"Assinatura inválida: {e}")
            return False

# Instância global do serviço
payment_service = PaymentService()

@payments_bp.route('/create', methods=['POST'])
@auth_required()
def create_payment():
    """
    Cria um pagamento real via Stripe com validação robusta.
    
    ---
    tags:
      - Pagamentos
    security:
      - Bearer: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/PaymentCreateSchema'
    responses:
      201:
        description: Pagamento criado com sucesso
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PaymentResponseSchema'
      400:
        description: Dados inválidos
      422:
        description: Erro de validação
      500:
        description: Erro interno
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'erro': 'Dados JSON obrigatórios'}), 400
        
        # Validar dados com Pydantic
        try:
            payment_schema = PaymentCreateSchema(**data)
        except Exception as validation_error:
            # Log de erro de validação
            user_id = getattr(request, 'user_id', 'anonymous')
            ip_address = request.remote_addr
            
            payment_security_logger.log_validation_error(
                user_id=user_id,
                error_type='schema_validation',
                field_name='payment_data',
                error_message=str(validation_error),
                ip_address=ip_address
            )
            
            log_event('warning', 'Payment', 
                     detalhes=f'Validação falhou: {str(validation_error)}')
            return jsonify({
                'erro': 'Dados inválidos',
                'detalhes': str(validation_error)
            }), 422
        
        # Adicionar metadados do usuário
        user_id = getattr(request, 'user_id', None)
        if user_id:
            payment_schema.metadata['user_id'] = user_id
            payment_schema.metadata['created_at'] = datetime.utcnow().isoformat()
        
        # Criar PaymentIntent
        payment_data = payment_service.create_payment_intent(
            amount=payment_schema.amount,
            currency=payment_schema.currency,
            metadata=payment_schema.metadata
        )
        
        # Log de segurança detalhado
        user_agent = request.headers.get('User-Agent', 'Unknown')
        ip_address = request.remote_addr
        
        payment_security_logger.log_payment_creation(
            payment_data=payment_data,
            user_id=user_id or 'anonymous',
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        log_event('info', 'Payment', 
                 detalhes=f'Pagamento criado para usuário {user_id}: {payment_data["id"]}')
        
        return jsonify({
            'status': 'success',
            'payment_intent': payment_data,
            'message': 'Pagamento criado com sucesso'
        }), 201
        
    except Exception as e:
        log_event('erro', 'Payment', detalhes=f'Erro ao criar pagamento: {str(e)}')
        return jsonify({
            'erro': 'Erro ao processar pagamento',
            'detalhes': str(e)
        }), 500

@payments_bp.route('/status/<payment_intent_id>', methods=['GET'])
@auth_required()
def get_payment_status(payment_intent_id: str):
    """
    Obtém status de um pagamento.
    
    ---
    tags:
      - Pagamentos
    security:
      - Bearer: []
    parameters:
      - name: payment_intent_id
        in: path
        required: true
        schema:
          type: string
        description: ID do PaymentIntent
    responses:
      200:
        description: Status do pagamento
      404:
        description: Pagamento não encontrado
    """
    try:
        payment_data = payment_service.retrieve_payment_intent(payment_intent_id)
        
        log_event('info', 'Payment', 
                 detalhes=f'Status consultado: {payment_intent_id}')
        
        return jsonify({
            'status': 'success',
            'payment': payment_data
        }), 200
        
    except Exception as e:
        log_event('erro', 'Payment', detalhes=f'Erro ao consultar status: {str(e)}')
        return jsonify({
            'erro': 'Erro ao consultar pagamento',
            'detalhes': str(e)
        }), 500

@payments_bp.route('/webhook', methods=['POST'])
def payment_webhook():
    """
    Webhook para receber notificações do Stripe.
    
    ---
    tags:
      - Pagamentos
    responses:
      200:
        description: Webhook processado
      400:
        description: Assinatura inválida
      403:
        description: IP não autorizado
    """
    try:
        # Validar IP
        allowed_ips = os.getenv('STRIPE_WEBHOOK_IPS', '').split(',')
        remote_ip = request.remote_addr
        if allowed_ips and remote_ip not in allowed_ips:
            log_event('warning', 'Payment', 
                     detalhes=f'Webhook IP não autorizado: {remote_ip}')
            return jsonify({'erro': 'IP não autorizado'}), 403
        
        # Obter payload e assinatura
        payload = request.data
        signature = request.headers.get('Stripe-Signature', '')
        
        if not signature:
            log_event('warning', 'Payment', detalhes='Webhook sem assinatura')
            return jsonify({'erro': 'Assinatura obrigatória'}), 400
        
        # Validar assinatura
        if not payment_service.validate_webhook_signature(payload, signature):
            log_event('warning', 'Payment', detalhes='Webhook com assinatura inválida')
            return jsonify({'erro': 'Assinatura inválida'}), 400
        
        # Processar evento
        event = json.loads(payload)
        event_type = event.get('type')
        event_id = event.get('id')
        
        # Log de webhook com detalhes de segurança
        payment_security_logger.log_webhook_event(
            event_type=event_type,
            event_id=event_id,
            payment_id=event.get('data', {}).get('object', {}).get('id', 'unknown'),
            ip_address=request.remote_addr,
            signature_valid=True
        )
        
        log_event('info', 'Payment', 
                 detalhes=f'Webhook processado: {event_type} - {event_id}')
        
        # Processar diferentes tipos de evento
        if event_type == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            payment_security_logger.log_payment_success(
                payment_id=payment_intent['id'],
                user_id=payment_intent.get('metadata', {}).get('user_id', 'unknown'),
                amount=payment_intent['amount'],
                currency=payment_intent['currency'],
                payment_method=payment_intent.get('payment_method', 'unknown')
            )
            log_event('success', 'Payment', 
                     detalhes=f'Pagamento confirmado: {payment_intent["id"]}')
            
        elif event_type == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            payment_security_logger.log_payment_failure(
                payment_id=payment_intent['id'],
                user_id=payment_intent.get('metadata', {}).get('user_id', 'unknown'),
                error_code='payment_failed',
                error_message='Pagamento falhou',
                payment_method=payment_intent.get('payment_method', 'unknown')
            )
            log_event('warning', 'Payment', 
                     detalhes=f'Pagamento falhou: {payment_intent["id"]}')
            
        elif event_type == 'charge.dispute.created':
            charge = event['data']['object']
            payment_security_logger.log_payment_dispute(
                payment_id=charge.get('payment_intent', 'unknown'),
                user_id=charge.get('metadata', {}).get('user_id', 'unknown'),
                dispute_reason=charge.get('dispute_reason', 'unknown'),
                dispute_amount=charge.get('amount', 0)
            )
            log_event('warning', 'Payment', 
                     detalhes=f'Disputa criada: {charge["id"]}')
        
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        log_event('erro', 'Payment', detalhes=f'Erro no webhook: {str(e)}')
        return jsonify({'erro': 'Erro interno'}), 500

@payments_bp.route('/list', methods=['GET'])
@auth_required()
def list_payments():
    """
    Lista pagamentos com filtros validados.
    
    ---
    tags:
      - Pagamentos
    security:
      - Bearer: []
    parameters:
      - name: status
        in: query
        schema:
          type: string
        description: Status do pagamento
      - name: payment_method
        in: query
        schema:
          type: string
        description: Método de pagamento
      - name: min_amount
        in: query
        schema:
          type: integer
        description: Valor mínimo
      - name: max_amount
        in: query
        schema:
          type: integer
        description: Valor máximo
      - name: limit
        in: query
        schema:
          type: integer
          default: 20
        description: Limite de resultados
      - name: offset
        in: query
        schema:
          type: integer
          default: 0
        description: Offset para paginação
    responses:
      200:
        description: Lista de pagamentos
      422:
        description: Filtros inválidos
    """
    try:
        # Obter parâmetros da query
        filters = {
            'status': request.args.get('status'),
            'payment_method': request.args.get('payment_method'),
            'min_amount': request.args.get('min_amount', type=int),
            'max_amount': request.args.get('max_amount', type=int),
            'limit': request.args.get('limit', 20, type=int),
            'offset': request.args.get('offset', 0, type=int)
        }
        
        # Validar filtros com Pydantic
        try:
            filter_schema = PaymentFilterSchema(**filters)
        except Exception as validation_error:
            log_event('warning', 'Payment', 
                     detalhes=f'Filtros inválidos: {str(validation_error)}')
            return jsonify({
                'erro': 'Filtros inválidos',
                'detalhes': str(validation_error)
            }), 422
        
        # TODO: Implementar busca real no banco de dados
        # Por enquanto, retorna lista simulada
        payments = [
            {
                'id': 'pi_test_123',
                'amount': 1000,
                'currency': 'brl',
                'status': 'succeeded',
                'payment_method': 'card',
                'created_at': datetime.utcnow().isoformat(),
                'description': 'Pagamento teste'
            }
        ]
        
        log_event('info', 'Payment', 
                 detalhes=f'Pagamentos listados com filtros: {filters}')
        
        return jsonify({
            'status': 'success',
            'payments': payments,
            'total': len(payments),
            'limit': filter_schema.limit,
            'offset': filter_schema.offset
        }), 200
        
    except Exception as e:
        log_event('erro', 'Payment', detalhes=f'Erro ao listar pagamentos: {str(e)}')
        return jsonify({
            'erro': 'Erro ao listar pagamentos',
            'detalhes': str(e)
        }), 500

@payments_bp.route('/config', methods=['GET'])
def get_payment_config():
    """
    Retorna configuração de pagamento para o frontend.
    
    ---
    tags:
      - Pagamentos
    responses:
      200:
        description: Configuração de pagamento
    """
    publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY', '')
    
    return jsonify({
        'stripe_publishable_key': publishable_key,
        'currency': 'brl',
        'supported_methods': ['card', 'pix', 'boleto']
    }), 200 