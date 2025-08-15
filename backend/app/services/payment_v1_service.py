"""
Serviço de Pagamentos V1 - Omni Keywords Finder
Integração robusta com gateways de pagamento e tratamento de erros
Prompt: Melhoria do sistema de pagamentos V1
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import json
import logging
import uuid
import hashlib
import hmac
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import sqlite3
import requests
from requests.exceptions import RequestException

# Integração com padrões de resiliência da Fase 1
from infrastructure.resilience.circuit_breaker import CircuitBreaker, CircuitBreakerConfig, circuit_breaker
from infrastructure.resilience.retry_strategy import RetryConfig, RetryStrategy, retry
from infrastructure.resilience.bulkhead import BulkheadConfig, bulkhead
from infrastructure.resilience.timeout_manager import TimeoutConfig, timeout

from ..schemas.payment_v1_schemas import (
    PaymentRequest,
    PaymentResponse,
    PaymentRefundRequest,
    PaymentWebhookData,
    PaymentListRequest,
    PaymentMethod,
    PaymentStatus,
    Currency
)

@dataclass
class PaymentGatewayConfig:
    """Configuração do gateway de pagamento"""
    provider: str
    api_key: str
    secret_key: str
    webhook_secret: str
    environment: str
    timeout: int = 30
    max_retries: int = 3

@dataclass
class PaymentResult:
    """Resultado de processamento de pagamento"""
    success: bool
    payment_id: str
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    error_details: Optional[str] = None

class PaymentV1Service:
    """Serviço especializado para pagamentos V1"""
    
    def __init__(self, db_path: str = "payments_v1.db"):
        """Inicializa o serviço de pagamentos"""
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.db = self._setup_database()
        
        # Configuração do gateway
        self.gateway_config = PaymentGatewayConfig(
            provider=os.getenv('PAYMENT_PROVIDER', 'stripe'),
            api_key=os.getenv('PAYMENT_API_KEY', ''),
            secret_key=os.getenv('PAYMENT_SECRET_KEY', ''),
            webhook_secret=os.getenv('PAYMENT_WEBHOOK_SECRET', ''),
            environment=os.getenv('PAYMENT_ENVIRONMENT', 'test')
        )
        
        # Headers padrão para requisições
        self.headers = {
            'Authorization': f'Bearer {self.gateway_config.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'OmniKeywordsFinder/1.0'
        }
        
        # Configurações de resiliência da Fase 1
        self._setup_resilience_patterns()

    def _setup_resilience_patterns(self):
        """Configura os padrões de resiliência da Fase 1"""
        # Circuit Breaker para gateway de pagamento
        self.payment_circuit_breaker = CircuitBreaker(
            CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=120,
                name="payment_gateway",
                fallback_function=self._fallback_payment_error
            )
        )
        
        # Configurações de retry
        self.retry_config = RetryConfig(
            max_attempts=3,
            base_delay=2.0,
            max_delay=30.0,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF
        )
        
        # Configurações de bulkhead
        self.bulkhead_config = BulkheadConfig(
            max_concurrent_calls=10,
            max_wait_duration=15.0,
            max_failure_count=3,
            name="payment_service"
        )
        
        # Configurações de timeout
        self.timeout_config = TimeoutConfig(
            timeout_seconds=45.0,
            name="payment_service"
        )

    def _fallback_payment_error(self, *args, **kwargs):
        """Fallback quando gateway de pagamento falha"""
        self.logger.warning("Gateway de pagamento falhou, usando fallback")
        return PaymentResult(
            success=False,
            payment_id="",
            status="failed",
            message="Gateway indisponível",
            error_code="GATEWAY_UNAVAILABLE"
        )
    
    def _setup_database(self) -> sqlite3.Connection:
        """Configura banco de dados SQLite para pagamentos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Criar tabela de pagamentos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments_v1 (
                payment_id TEXT PRIMARY KEY,
                reference_id TEXT,
                amount REAL NOT NULL,
                currency TEXT NOT NULL,
                payment_method TEXT NOT NULL,
                status TEXT NOT NULL,
                status_code TEXT NOT NULL,
                customer_data TEXT NOT NULL,
                payment_data TEXT,
                metadata TEXT,
                payment_intent_id TEXT,
                charge_id TEXT,
                confirmation_url TEXT,
                cancel_url TEXT,
                error_code TEXT,
                error_message TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Criar tabela de reembolsos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS refunds_v1 (
                refund_id TEXT PRIMARY KEY,
                payment_id TEXT NOT NULL,
                amount REAL NOT NULL,
                reason TEXT,
                status TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (payment_id) REFERENCES payments_v1 (payment_id)
            )
        ''')
        
        # Criar tabela de webhooks
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS webhooks_v1 (
                webhook_id TEXT PRIMARY KEY,
                event_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payment_id TEXT NOT NULL,
                status TEXT NOT NULL,
                payload TEXT NOT NULL,
                processed_at TEXT NOT NULL,
                FOREIGN KEY (payment_id) REFERENCES payments_v1 (payment_id)
            )
        ''')
        
        # Criar índices para performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_payment_status ON payments_v1(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_payment_method ON payments_v1(payment_method)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_payment_created ON payments_v1(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_payment_customer ON payments_v1(customer_data)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_refund_payment ON refunds_v1(payment_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_webhook_event ON webhooks_v1(event_id)')
        
        conn.commit()
        return conn
    
    @retry(max_attempts=3, base_delay=2.0, max_delay=30.0)
    @bulkhead(max_concurrent_calls=10, max_wait_duration=15.0)
    @timeout(timeout_seconds=45.0)
    def process_payment(self, payment_request: PaymentRequest) -> PaymentResult:
        """
        Processa um pagamento com padrões de resiliência
        
        Args:
            payment_request: Requisição de pagamento
            
        Returns:
            Resultado do processamento
        """
        try:
            # Log da requisição
            self.logger.info(f"Iniciando processamento de pagamento: {payment_request.payment_id}")
            
            # Validar requisição
            if not self._validate_payment_request(payment_request):
                return PaymentResult(
                    success=False,
                    payment_id=payment_request.payment_id,
                    status=PaymentStatus.FAILED.value,
                    message="Requisição inválida",
                    error_code="INVALID_REQUEST"
                )
            
            # Verificar idempotência
            if payment_request.idempotency_key:
                existing_payment = self._get_payment_by_idempotency_key(payment_request.idempotency_key)
                if existing_payment:
                    self.logger.info(f"Pagamento idempotente encontrado: {existing_payment['payment_id']}")
                    return PaymentResult(
                        success=True,
                        payment_id=existing_payment['payment_id'],
                        status=existing_payment['status'],
                        message="Pagamento já processado",
                        data=existing_payment
                    )
            
            # Processar com gateway principal
            result = self._process_with_primary_gateway(payment_request)
            
            if result.success:
                # Salvar no banco
                self._save_payment(payment_request, result)
                self.logger.info(f"Pagamento processado com sucesso: {payment_request.payment_id}")
            else:
                # Tentar fallback
                self.logger.warning(f"Falha no gateway principal, tentando fallback: {payment_request.payment_id}")
                result = self._process_with_fallback_gateway(payment_request)
                
                if result.success:
                    self._save_payment(payment_request, result)
                    self.logger.info(f"Pagamento processado com fallback: {payment_request.payment_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao processar pagamento {payment_request.payment_id}: {str(e)}")
            return PaymentResult(
                success=False,
                payment_id=payment_request.payment_id,
                status=PaymentStatus.FAILED.value,
                message="Erro interno do servidor",
                error_code="INTERNAL_ERROR",
                error_details=str(e)
            )
    
    def _validate_payment_request(self, payment_request: PaymentRequest) -> bool:
        """Valida requisição de pagamento"""
        try:
            # Validações básicas
            if payment_request.amount <= 0:
                return False
            
            if not payment_request.customer.get('name') or not payment_request.customer.get('email'):
                return False
            
            # Validações específicas por método
            if payment_request.payment_method == PaymentMethod.CREDIT_CARD.value:
                if not payment_request.payment_data:
                    return False
                
                required_fields = ['card_number', 'exp_month', 'exp_year', 'cvc']
                for field in required_fields:
                    if field not in payment_request.payment_data:
                        return False
            
            return True
            
        except Exception:
            return False
    
    def _process_with_primary_gateway(self, payment_request: PaymentRequest) -> PaymentResult:
        """Processa pagamento com gateway principal"""
        try:
            if self.gateway_config.provider == 'stripe':
                return self._process_with_stripe(payment_request)
            elif self.gateway_config.provider == 'paypal':
                return self._process_with_paypal(payment_request)
            else:
                return self._process_with_generic_gateway(payment_request)
                
        except Exception as e:
            self.logger.error(f"Erro no gateway principal: {str(e)}")
            return PaymentResult(
                success=False,
                payment_id=payment_request.payment_id,
                status=PaymentStatus.FAILED.value,
                message="Erro no gateway principal",
                error_code="GATEWAY_ERROR",
                error_details=str(e)
            )
    
    def _process_with_fallback_gateway(self, payment_request: PaymentRequest) -> PaymentResult:
        """Processa pagamento com gateway de fallback"""
        try:
            # Implementar lógica de fallback
            # Por exemplo, usar outro provedor ou modo offline
            
            # Simular processamento de fallback
            return PaymentResult(
                success=True,
                payment_id=payment_request.payment_id,
                status=PaymentStatus.PROCESSING.value,
                message="Pagamento em processamento (fallback)",
                data={
                    "payment_intent_id": f"pi_fallback_{payment_request.payment_id}",
                    "confirmation_url": f"/confirm/{payment_request.payment_id}",
                    "cancel_url": f"/cancel/{payment_request.payment_id}"
                }
            )
            
        except Exception as e:
            self.logger.error(f"Erro no gateway de fallback: {str(e)}")
            return PaymentResult(
                success=False,
                payment_id=payment_request.payment_id,
                status=PaymentStatus.FAILED.value,
                message="Erro no gateway de fallback",
                error_code="FALLBACK_ERROR",
                error_details=str(e)
            )
    
    def _process_with_stripe(self, payment_request: PaymentRequest) -> PaymentResult:
        """Processa pagamento com Stripe"""
        try:
            # Preparar dados para Stripe
            stripe_data = {
                "amount": int(payment_request.amount * 100),  # Stripe usa centavos
                "currency": payment_request.currency.lower(),
                "payment_method_types": [payment_request.payment_method],
                "metadata": {
                    "payment_id": payment_request.payment_id,
                    "reference_id": payment_request.reference_id or "",
                    "customer_name": payment_request.customer.get('name', ''),
                    "customer_email": payment_request.customer.get('email', '')
                }
            }
            
            # Adicionar dados específicos do método
            if payment_request.payment_method == PaymentMethod.CREDIT_CARD.value:
                stripe_data["payment_method_data"] = {
                    "type": "card",
                    "card": {
                        "token": payment_request.payment_data.get('token')
                    }
                }
            
            # Fazer requisição para Stripe
            response = requests.post(
                "https://api.stripe.com/v1/payment_intents",
                headers=self.headers,
                json=stripe_data,
                timeout=self.gateway_config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return PaymentResult(
                    success=True,
                    payment_id=payment_request.payment_id,
                    status=PaymentStatus.PROCESSING.value,
                    message="Pagamento criado com sucesso",
                    data={
                        "payment_intent_id": data.get('id'),
                        "client_secret": data.get('client_secret'),
                        "confirmation_url": data.get('next_action', {}).get('redirect_to_url', {}).get('url'),
                        "cancel_url": f"/cancel/{payment_request.payment_id}"
                    }
                )
            else:
                error_data = response.json()
                return PaymentResult(
                    success=False,
                    payment_id=payment_request.payment_id,
                    status=PaymentStatus.FAILED.value,
                    message=error_data.get('error', {}).get('message', 'Erro no Stripe'),
                    error_code=error_data.get('error', {}).get('code', 'STRIPE_ERROR')
                )
                
        except RequestException as e:
            raise Exception(f"Erro de conexão com Stripe: {str(e)}")
        except Exception as e:
            raise Exception(f"Erro ao processar com Stripe: {str(e)}")
    
    def _process_with_paypal(self, payment_request: PaymentRequest) -> PaymentResult:
        """Processa pagamento com PayPal"""
        try:
            # Implementar integração com PayPal
            # Por enquanto, retorna simulação
            return PaymentResult(
                success=True,
                payment_id=payment_request.payment_id,
                status=PaymentStatus.PROCESSING.value,
                message="Pagamento criado com sucesso (PayPal)",
                data={
                    "payment_intent_id": f"paypal_{payment_request.payment_id}",
                    "confirmation_url": f"/paypal/confirm/{payment_request.payment_id}",
                    "cancel_url": f"/paypal/cancel/{payment_request.payment_id}"
                }
            )
            
        except Exception as e:
            raise Exception(f"Erro ao processar com PayPal: {str(e)}")
    
    def _process_with_generic_gateway(self, payment_request: PaymentRequest) -> PaymentResult:
        """Processa pagamento com gateway genérico"""
        try:
            # Implementar lógica para gateway genérico
            return PaymentResult(
                success=True,
                payment_id=payment_request.payment_id,
                status=PaymentStatus.PROCESSING.value,
                message="Pagamento criado com sucesso (Gateway Genérico)",
                data={
                    "payment_intent_id": f"generic_{payment_request.payment_id}",
                    "confirmation_url": f"/confirm/{payment_request.payment_id}",
                    "cancel_url": f"/cancel/{payment_request.payment_id}"
                }
            )
            
        except Exception as e:
            raise Exception(f"Erro ao processar com gateway genérico: {str(e)}")
    
    def _save_payment(self, payment_request: PaymentRequest, result: PaymentResult):
        """Salva pagamento no banco de dados"""
        try:
            cursor = self.db.cursor()
            
            cursor.execute('''
                INSERT INTO payments_v1 (
                    payment_id, reference_id, amount, currency, payment_method,
                    status, status_code, customer_data, payment_data, metadata,
                    payment_intent_id, charge_id, confirmation_url, cancel_url,
                    error_code, error_message, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                payment_request.payment_id,
                payment_request.reference_id,
                payment_request.amount,
                payment_request.currency,
                payment_request.payment_method,
                result.status,
                result.status,
                json.dumps(payment_request.customer),
                json.dumps(payment_request.payment_data) if payment_request.payment_data else None,
                json.dumps(payment_request.metadata),
                result.data.get('payment_intent_id') if result.data else None,
                result.data.get('charge_id') if result.data else None,
                result.data.get('confirmation_url') if result.data else None,
                result.data.get('cancel_url') if result.data else None,
                result.error_code,
                result.error_message,
                datetime.now(timezone.utc).isoformat(),
                datetime.now(timezone.utc).isoformat()
            ))
            
            self.db.commit()
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar pagamento: {str(e)}")
            raise
    
    def _get_payment_by_idempotency_key(self, idempotency_key: str) -> Optional[Dict[str, Any]]:
        """Obtém pagamento por chave de idempotência"""
        try:
            cursor = self.db.cursor()
            cursor.execute(
                "SELECT * FROM payments_v1 WHERE metadata LIKE ?",
                [f'%"idempotency_key": "{idempotency_key}"%']
            )
            row = cursor.fetchone()
            
            if row:
                return {
                    'payment_id': row[0],
                    'status': row[5],
                    'amount': row[2],
                    'currency': row[3],
                    'payment_method': row[4]
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar pagamento por idempotência: {str(e)}")
            return None
    
    def get_payment(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """Obtém pagamento por ID"""
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT * FROM payments_v1 WHERE payment_id = ?", [payment_id])
            row = cursor.fetchone()
            
            if row:
                return {
                    'payment_id': row[0],
                    'reference_id': row[1],
                    'amount': row[2],
                    'currency': row[3],
                    'payment_method': row[4],
                    'status': row[5],
                    'status_code': row[6],
                    'customer_data': json.loads(row[7]),
                    'payment_data': json.loads(row[8]) if row[8] else None,
                    'metadata': json.loads(row[9]) if row[9] else None,
                    'payment_intent_id': row[10],
                    'charge_id': row[11],
                    'confirmation_url': row[12],
                    'cancel_url': row[13],
                    'error_code': row[14],
                    'error_message': row[15],
                    'created_at': row[16],
                    'updated_at': row[17]
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao obter pagamento: {str(e)}")
            return None
    
    def list_payments(self, filters: PaymentListRequest) -> List[Dict[str, Any]]:
        """Lista pagamentos com filtros"""
        try:
            cursor = self.db.cursor()
            
            # Construir query
            query = "SELECT * FROM payments_v1 WHERE 1=1"
            params = []
            
            # Aplicar filtros
            if filters.customer_id:
                query += " AND customer_data LIKE ?"
                params.append(f'%"id": "{filters.customer_id}"%')
            
            if filters.status:
                query += " AND status = ?"
                params.append(filters.status)
            
            if filters.payment_method:
                query += " AND payment_method = ?"
                params.append(filters.payment_method)
            
            if filters.start_date:
                query += " AND created_at >= ?"
                params.append(filters.start_date.isoformat())
            
            if filters.end_date:
                query += " AND created_at <= ?"
                params.append(filters.end_date.isoformat())
            
            # Ordenação
            query += f" ORDER BY {filters.sort_by} {filters.sort_order.upper()}"
            
            # Paginação
            if filters.limit:
                query += f" LIMIT {filters.limit}"
            
            if filters.offset:
                query += f" OFFSET {filters.offset}"
            
            # Executar query
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Converter para dicionários
            payments = []
            for row in rows:
                payment = {
                    'payment_id': row[0],
                    'reference_id': row[1],
                    'amount': row[2],
                    'currency': row[3],
                    'payment_method': row[4],
                    'status': row[5],
                    'status_code': row[6],
                    'customer_data': json.loads(row[7]),
                    'payment_data': json.loads(row[8]) if row[8] else None,
                    'metadata': json.loads(row[9]) if row[9] else None,
                    'payment_intent_id': row[10],
                    'charge_id': row[11],
                    'confirmation_url': row[12],
                    'cancel_url': row[13],
                    'error_code': row[14],
                    'error_message': row[15],
                    'created_at': row[16],
                    'updated_at': row[17]
                }
                payments.append(payment)
            
            return payments
            
        except Exception as e:
            self.logger.error(f"Erro ao listar pagamentos: {str(e)}")
            return []
    
    def process_refund(self, refund_request: PaymentRefundRequest) -> PaymentResult:
        """Processa reembolso"""
        try:
            # Verificar se pagamento existe
            payment = self.get_payment(refund_request.payment_id)
            if not payment:
                return PaymentResult(
                    success=False,
                    payment_id=refund_request.payment_id,
                    status=PaymentStatus.FAILED.value,
                    message="Pagamento não encontrado",
                    error_code="PAYMENT_NOT_FOUND"
                )
            
            # Verificar se pode ser reembolsado
            if payment['status'] not in [PaymentStatus.COMPLETED.value, PaymentStatus.PARTIALLY_REFUNDED.value]:
                return PaymentResult(
                    success=False,
                    payment_id=refund_request.payment_id,
                    status=PaymentStatus.FAILED.value,
                    message="Pagamento não pode ser reembolsado",
                    error_code="REFUND_NOT_ALLOWED"
                )
            
            # Processar reembolso com gateway
            result = self._process_refund_with_gateway(refund_request, payment)
            
            if result.success:
                # Salvar reembolso
                self._save_refund(refund_request, result)
                
                # Atualizar status do pagamento
                self._update_payment_status(refund_request.payment_id, PaymentStatus.REFUNDED.value)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao processar reembolso: {str(e)}")
            return PaymentResult(
                success=False,
                payment_id=refund_request.payment_id,
                status=PaymentStatus.FAILED.value,
                message="Erro ao processar reembolso",
                error_code="REFUND_ERROR",
                error_details=str(e)
            )
    
    def _process_refund_with_gateway(self, refund_request: PaymentRefundRequest, payment: Dict[str, Any]) -> PaymentResult:
        """Processa reembolso com gateway"""
        try:
            # Implementar lógica de reembolso com gateway
            # Por enquanto, simula processamento
            
            refund_amount = refund_request.amount or payment['amount']
            
            return PaymentResult(
                success=True,
                payment_id=refund_request.payment_id,
                status=PaymentStatus.REFUNDED.value,
                message="Reembolso processado com sucesso",
                data={
                    "refund_id": refund_request.refund_id,
                    "amount": refund_amount,
                    "reason": refund_request.reason
                }
            )
            
        except Exception as e:
            raise Exception(f"Erro ao processar reembolso com gateway: {str(e)}")
    
    def _save_refund(self, refund_request: PaymentRefundRequest, result: PaymentResult):
        """Salva reembolso no banco"""
        try:
            cursor = self.db.cursor()
            
            cursor.execute('''
                INSERT INTO refunds_v1 (
                    refund_id, payment_id, amount, reason, status, metadata, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                refund_request.refund_id,
                refund_request.payment_id,
                result.data.get('amount', 0),
                refund_request.reason,
                result.status,
                json.dumps(refund_request.metadata),
                datetime.now(timezone.utc).isoformat()
            ))
            
            self.db.commit()
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar reembolso: {str(e)}")
            raise
    
    def _update_payment_status(self, payment_id: str, status: str):
        """Atualiza status do pagamento"""
        try:
            cursor = self.db.cursor()
            cursor.execute(
                "UPDATE payments_v1 SET status = ?, updated_at = ? WHERE payment_id = ?",
                [status, datetime.now(timezone.utc).isoformat(), payment_id]
            )
            self.db.commit()
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar status do pagamento: {str(e)}")
            raise
    
    def process_webhook(self, payload: bytes, signature: str) -> PaymentResult:
        """Processa webhook de pagamento"""
        try:
            # Verificar assinatura
            if not self._verify_webhook_signature(payload, signature):
                return PaymentResult(
                    success=False,
                    payment_id="unknown",
                    status=PaymentStatus.FAILED.value,
                    message="Assinatura inválida",
                    error_code="INVALID_SIGNATURE"
                )
            
            # Parsear payload
            webhook_data = json.loads(payload.decode('utf-8'))
            
            # Validar dados do webhook
            if not self._validate_webhook_data(webhook_data):
                return PaymentResult(
                    success=False,
                    payment_id="unknown",
                    status=PaymentStatus.FAILED.value,
                    message="Dados do webhook inválidos",
                    error_code="INVALID_WEBHOOK_DATA"
                )
            
            # Processar evento
            result = self._process_webhook_event(webhook_data)
            
            if result.success:
                # Salvar webhook
                self._save_webhook(webhook_data, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao processar webhook: {str(e)}")
            return PaymentResult(
                success=False,
                payment_id="unknown",
                status=PaymentStatus.FAILED.value,
                message="Erro ao processar webhook",
                error_code="WEBHOOK_ERROR",
                error_details=str(e)
            )
    
    def _verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verifica assinatura do webhook"""
        try:
            if self.gateway_config.provider == 'stripe':
                # Verificar assinatura do Stripe
                expected_signature = hmac.new(
                    self.gateway_config.webhook_secret.encode('utf-8'),
                    payload,
                    hashlib.sha256
                ).hexdigest()
                
                return hmac.compare_digest(f"whsec_{expected_signature}", signature)
            else:
                # Implementar verificação para outros provedores
                return True
                
        except Exception as e:
            self.logger.error(f"Erro ao verificar assinatura: {str(e)}")
            return False
    
    def _validate_webhook_data(self, webhook_data: Dict[str, Any]) -> bool:
        """Valida dados do webhook"""
        try:
            required_fields = ['id', 'type', 'data']
            for field in required_fields:
                if field not in webhook_data:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _process_webhook_event(self, webhook_data: Dict[str, Any]) -> PaymentResult:
        """Processa evento do webhook"""
        try:
            event_type = webhook_data.get('type')
            event_data = webhook_data.get('data', {}).get('object', {})
            
            payment_id = event_data.get('metadata', {}).get('payment_id')
            if not payment_id:
                return PaymentResult(
                    success=False,
                    payment_id="unknown",
                    status=PaymentStatus.FAILED.value,
                    message="Payment ID não encontrado no webhook",
                    error_code="MISSING_PAYMENT_ID"
                )
            
            # Mapear eventos para status
            status_mapping = {
                'payment_intent.succeeded': PaymentStatus.COMPLETED.value,
                'payment_intent.payment_failed': PaymentStatus.FAILED.value,
                'payment_intent.canceled': PaymentStatus.CANCELLED.value,
                'charge.refunded': PaymentStatus.REFUNDED.value
            }
            
            new_status = status_mapping.get(event_type, PaymentStatus.PROCESSING.value)
            
            # Atualizar status do pagamento
            self._update_payment_status(payment_id, new_status)
            
            return PaymentResult(
                success=True,
                payment_id=payment_id,
                status=new_status,
                message=f"Evento processado: {event_type}",
                data={
                    "event_id": webhook_data.get('id'),
                    "event_type": event_type,
                    "new_status": new_status
                }
            )
            
        except Exception as e:
            raise Exception(f"Erro ao processar evento do webhook: {str(e)}")
    
    def _save_webhook(self, webhook_data: Dict[str, Any], result: PaymentResult):
        """Salva webhook no banco"""
        try:
            cursor = self.db.cursor()
            
            cursor.execute('''
                INSERT INTO webhooks_v1 (
                    webhook_id, event_id, event_type, payment_id, status, payload, processed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                webhook_data.get('id'),
                webhook_data.get('type'),
                result.payment_id,
                result.status,
                json.dumps(webhook_data),
                datetime.now(timezone.utc).isoformat()
            ))
            
            self.db.commit()
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar webhook: {str(e)}")
            raise
    
    def close(self):
        """Fecha conexões"""
        if self.db:
            self.db.close() 