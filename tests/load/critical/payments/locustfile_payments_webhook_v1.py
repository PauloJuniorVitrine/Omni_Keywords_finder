"""
Teste de Carga - Webhooks de Pagamento
Endpoint: /api/v1/payments/webhook (POST)
Baseado em: backend/app/api/payments_v1.py linha 286-338
Tracing ID: PAYMENTS_WEBHOOK_LOAD_TEST_20250127_001
Data: 2025-01-27
"""

from locust import HttpUser, task, between
import json
import logging
import random
import hmac
import hashlib

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PaymentsWebhookLoadTest(HttpUser):
    """
    Teste de carga para endpoint de webhooks de pagamento
    Baseado no código real: backend/app/api/payments_v1.py
    """
    
    wait_time = between(2, 5)  # Intervalo para webhooks
    
    def on_start(self):
        """Setup inicial - configuração de webhooks"""
        # Configuração baseada no código real
        self.webhook_secret = "whsec_test_webhook_secret_2025"
        self.stripe_signature = "t=1234567890,v1=test_signature"
        
        logger.info("Configuração de webhooks inicializada")

    def generate_stripe_signature(self, payload: str, secret: str, timestamp: str) -> str:
        """
        Gera assinatura Stripe para webhook
        Baseado no código real de validação
        """
        try:
            signed_payload = f"{timestamp}.{payload}"
            signature = hmac.new(
                secret.encode('utf-8'),
                signed_payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            return f"t={timestamp},v1={signature}"
        except Exception as e:
            logger.error(f"Erro ao gerar assinatura: {str(e)}")
            return ""

    @task(4)
    def process_stripe_webhook_success(self):
        """
        Teste de webhook Stripe de sucesso
        Baseado em: backend/app/api/payments_v1.py linha 286-338
        """
        try:
            # Dados baseados em webhooks reais do Stripe
            webhook_data = {
                "id": f"evt_{random.randint(1000000000000000, 9999999999999999)}",
                "object": "event",
                "api_version": "2023-10-16",
                "created": 1706371200,
                "data": {
                    "object": {
                        "id": f"pi_{random.randint(1000000000000000, 9999999999999999)}",
                        "object": "payment_intent",
                        "amount": random.choice([1000, 2500, 5000, 10000]),
                        "currency": "brl",
                        "status": "succeeded",
                        "payment_method": "pm_card_visa",
                        "customer": f"cus_{random.randint(1000000000000000, 9999999999999999)}",
                        "metadata": {
                            "order_id": f"order_{random.randint(1000, 9999)}",
                            "product": "Premium Plan"
                        }
                    }
                },
                "livemode": False,
                "pending_webhooks": 1,
                "request": {
                    "id": f"req_{random.randint(1000000000000000, 9999999999999999)}",
                    "idempotency_key": None
                },
                "type": "payment_intent.succeeded"
            }
            
            # Gerar assinatura
            payload = json.dumps(webhook_data)
            timestamp = str(int(webhook_data["created"]))
            signature = self.generate_stripe_signature(payload, self.webhook_secret, timestamp)
            
            headers = {
                "Content-Type": "application/json",
                "Stripe-Signature": signature
            }
            
            response = self.client.post(
                "/api/v1/payments/webhook",
                headers=headers,
                data=payload,
                name="Payments - Webhook Stripe (Sucesso)"
            )
            
            # Validações baseadas no código real
            if response.status_code == 200:
                result = response.json()
                assert "success" in result, "Campo 'success' ausente na resposta"
                assert "message" in result, "Campo 'message' ausente na resposta"
                
                logger.info(f"Webhook Stripe processado com sucesso: {webhook_data['id']}")
                
            elif response.status_code == 400:
                error_data = response.json()
                logger.warning(f"Webhook Stripe rejeitado: {error_data.get('detail', 'Erro desconhecido')}")
                
            elif response.status_code == 401:
                logger.warning("Webhook Stripe não autorizado - assinatura inválida")
                
            else:
                logger.error(f"Erro inesperado no webhook: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Erro durante processamento de webhook Stripe: {str(e)}")

    @task(2)
    def process_stripe_webhook_failure(self):
        """
        Teste de webhook Stripe de falha
        Baseado em: backend/app/api/payments_v1.py linha 286-338
        """
        try:
            # Dados de webhook de falha
            webhook_data = {
                "id": f"evt_{random.randint(1000000000000000, 9999999999999999)}",
                "object": "event",
                "api_version": "2023-10-16",
                "created": 1706371200,
                "data": {
                    "object": {
                        "id": f"pi_{random.randint(1000000000000000, 9999999999999999)}",
                        "object": "payment_intent",
                        "amount": 5000,
                        "currency": "brl",
                        "status": "payment_failed",
                        "last_payment_error": {
                            "type": "card_error",
                            "code": "card_declined",
                            "message": "Your card was declined."
                        },
                        "metadata": {
                            "order_id": f"order_{random.randint(1000, 9999)}",
                            "product": "Basic Plan"
                        }
                    }
                },
                "livemode": False,
                "pending_webhooks": 1,
                "request": {
                    "id": f"req_{random.randint(1000000000000000, 9999999999999999)}",
                    "idempotency_key": None
                },
                "type": "payment_intent.payment_failed"
            }
            
            # Gerar assinatura
            payload = json.dumps(webhook_data)
            timestamp = str(int(webhook_data["created"]))
            signature = self.generate_stripe_signature(payload, self.webhook_secret, timestamp)
            
            headers = {
                "Content-Type": "application/json",
                "Stripe-Signature": signature
            }
            
            response = self.client.post(
                "/api/v1/payments/webhook",
                headers=headers,
                data=payload,
                name="Payments - Webhook Stripe (Falha)"
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Webhook Stripe de falha processado: {webhook_data['id']}")
                
            elif response.status_code == 400:
                error_data = response.json()
                logger.warning(f"Webhook Stripe de falha rejeitado: {error_data.get('detail', 'Erro desconhecido')}")
                
        except Exception as e:
            logger.error(f"Erro durante processamento de webhook de falha: {str(e)}")

    @task(2)
    def process_paypal_webhook(self):
        """
        Teste de webhook PayPal
        Baseado em: backend/app/api/payments_v1.py linha 286-338
        """
        try:
            # Dados baseados em webhooks reais do PayPal
            webhook_data = {
                "id": f"WH-{random.randint(1000000000000000, 9999999999999999)}",
                "event_type": "PAYMENT.CAPTURE.COMPLETED",
                "create_time": "2025-01-27T18:00:00.000Z",
                "resource_type": "capture",
                "resource": {
                    "id": f"CAPTURE-{random.randint(1000000000000000, 9999999999999999)}",
                    "status": "COMPLETED",
                    "amount": {
                        "currency_code": "BRL",
                        "value": str(random.choice([10.00, 25.00, 50.00, 100.00]))
                    },
                    "custom_id": f"order_{random.randint(1000, 9999)}"
                },
                "links": [
                    {
                        "href": "https://api.paypal.com/v1/notifications/webhooks-events/WH-123456789",
                        "rel": "self",
                        "method": "GET"
                    }
                ]
            }
            
            # Assinatura PayPal (simulada)
            paypal_signature = "PAYPAL-SIGNATURE-TEST-2025"
            
            headers = {
                "Content-Type": "application/json",
                "Paypal-Signature": paypal_signature
            }
            
            response = self.client.post(
                "/api/v1/payments/webhook",
                headers=headers,
                json=webhook_data,
                name="Payments - Webhook PayPal"
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Webhook PayPal processado com sucesso: {webhook_data['id']}")
                
            elif response.status_code == 400:
                error_data = response.json()
                logger.warning(f"Webhook PayPal rejeitado: {error_data.get('detail', 'Erro desconhecido')}")
                
        except Exception as e:
            logger.error(f"Erro durante processamento de webhook PayPal: {str(e)}")

    @task(1)
    def process_webhook_invalid_signature(self):
        """
        Teste de webhook com assinatura inválida
        Baseado em: backend/app/api/payments_v1.py linha 286-338
        """
        try:
            # Dados de webhook válidos
            webhook_data = {
                "id": f"evt_{random.randint(1000000000000000, 9999999999999999)}",
                "object": "event",
                "type": "payment_intent.succeeded",
                "data": {
                    "object": {
                        "id": f"pi_{random.randint(1000000000000000, 9999999999999999)}",
                        "status": "succeeded"
                    }
                }
            }
            
            # Assinatura inválida
            invalid_signature = "t=1234567890,v1=invalid_signature"
            
            headers = {
                "Content-Type": "application/json",
                "Stripe-Signature": invalid_signature
            }
            
            response = self.client.post(
                "/api/v1/payments/webhook",
                headers=headers,
                json=webhook_data,
                name="Payments - Webhook (Assinatura Inválida)"
            )
            
            # Deve retornar 401 para assinatura inválida
            if response.status_code == 401:
                logger.info("Webhook rejeitado por assinatura inválida (esperado)")
                
            elif response.status_code == 400:
                error_data = response.json()
                logger.info(f"Webhook rejeitado: {error_data.get('detail', 'Erro de validação')}")
                
            else:
                logger.warning(f"Resposta inesperada para assinatura inválida: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Erro durante teste de assinatura inválida: {str(e)}")

    @task(1)
    def process_webhook_malformed_data(self):
        """
        Teste de webhook com dados malformados
        Baseado em: backend/app/api/payments_v1.py linha 286-338
        """
        try:
            # Dados malformados
            malformed_data = {
                "invalid_field": "invalid_value",
                "missing_required_fields": True
            }
            
            headers = {
                "Content-Type": "application/json",
                "Stripe-Signature": "t=1234567890,v1=test_signature"
            }
            
            response = self.client.post(
                "/api/v1/payments/webhook",
                headers=headers,
                json=malformed_data,
                name="Payments - Webhook (Dados Malformados)"
            )
            
            # Deve retornar 400 para dados malformados
            if response.status_code == 400:
                error_data = response.json()
                logger.info(f"Webhook rejeitado por dados malformados: {error_data.get('detail', 'Erro de validação')}")
                
            elif response.status_code == 422:
                error_data = response.json()
                logger.info(f"Validação Pydantic rejeitou dados malformados: {error_data}")
                
            else:
                logger.warning(f"Resposta inesperada para dados malformados: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Erro durante teste de dados malformados: {str(e)}")

    def on_stop(self):
        """Cleanup ao finalizar"""
        logger.info("Teste de carga Payments Webhook finalizado") 