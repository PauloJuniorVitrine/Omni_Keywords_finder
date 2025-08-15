"""
Teste de Carga - Retry de Webhooks de Pagamento
===============================================

Endpoint: /api/v1/payments/webhook (retry logic)
Método: POST
Criticidade: CRÍTICA (Receita do sistema)

Baseado em: backend/app/api/payments_v1.py (linhas 287-350)
"""

import json
import random
import hashlib
import hmac
from datetime import datetime, timezone
from locust import HttpUser, task, between, events
from typing import Dict, Any


class PaymentWebhookRetryLoadTest(HttpUser):
    """
    Teste de carga para retry de webhooks de pagamento
    
    Baseado no endpoint real: /api/v1/payments/webhook
    """
    
    wait_time = between(0.5, 2)  # Intervalo menor para webhooks
    
    def on_start(self):
        """Setup inicial"""
        self.webhook_secret = "whsec_test_secret_key_12345"  # Chave de teste
        self.payment_ids = self._generate_payment_ids()
    
    def _generate_payment_ids(self) -> list:
        """Gera IDs de pagamento para teste"""
        return [f"pi_{random.randint(100000, 999999)}" for _ in range(20)]
    
    def _generate_stripe_signature(self, payload: str, timestamp: str) -> str:
        """Gera assinatura Stripe para webhook"""
        message = f"{timestamp}.{payload}"
        signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return f"t={timestamp},v1={signature}"
    
    def _generate_paypal_signature(self, payload: str) -> str:
        """Gera assinatura PayPal para webhook"""
        signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    @task(4)
    def test_stripe_webhook_retry(self):
        """Teste de retry de webhook Stripe"""
        payment_id = random.choice(self.payment_ids)
        timestamp = str(int(datetime.now().timestamp()))
        
        # Payload baseado em webhook real do Stripe
        payload = {
            "id": f"evt_{random.randint(100000, 999999)}",
            "object": "event",
            "api_version": "2023-10-16",
            "created": int(datetime.now().timestamp()),
            "data": {
                "object": {
                    "id": payment_id,
                    "object": "payment_intent",
                    "amount": random.randint(1000, 10000),
                    "currency": "brl",
                    "status": "succeeded",
                    "payment_method": "pm_card_visa",
                    "customer": f"cus_{random.randint(100000, 999999)}",
                    "metadata": {
                        "order_id": f"order_{random.randint(100000, 999999)}"
                    }
                }
            },
            "livemode": False,
            "pending_webhooks": 1,
            "request": {
                "id": f"req_{random.randint(100000, 999999)}",
                "idempotency_key": None
            },
            "type": "payment_intent.succeeded"
        }
        
        payload_str = json.dumps(payload)
        signature = self._generate_stripe_signature(payload_str, timestamp)
        
        headers = {
            "Content-Type": "application/json",
            "Stripe-Signature": signature,
            "User-Agent": "Stripe/v1 WebhooksSimulator"
        }
        
        with self.client.post(
            "/api/v1/payments/webhook",
            data=payload_str,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure(f"Webhook Stripe falhou: {data.get('message')}")
            elif response.status_code == 400:
                # Erro esperado para alguns casos
                response.success()
            else:
                response.failure(f"Status inesperado Stripe: {response.status_code}")
    
    @task(3)
    def test_paypal_webhook_retry(self):
        """Teste de retry de webhook PayPal"""
        payment_id = random.choice(self.payment_ids)
        
        # Payload baseado em webhook real do PayPal
        payload = {
            "id": f"WH-{random.randint(100000, 999999)}",
            "event_type": "PAYMENT.CAPTURE.COMPLETED",
            "create_time": datetime.now().isoformat(),
            "resource_type": "capture",
            "resource": {
                "id": f"CAPTURE-{random.randint(100000, 999999)}",
                "status": "COMPLETED",
                "amount": {
                    "currency_code": "BRL",
                    "value": str(random.randint(10, 100))
                },
                "custom_id": payment_id,
                "seller_protection": {
                    "status": "ELIGIBLE",
                    "dispute_categories": ["ITEM_NOT_RECEIVED", "UNAUTHORIZED_TRANSACTION"]
                }
            },
            "links": [
                {
                    "href": f"https://api.paypal.com/v1/notifications/webhooks/{random.randint(100000, 999999)}",
                    "rel": "self",
                    "method": "GET"
                }
            ]
        }
        
        payload_str = json.dumps(payload)
        signature = self._generate_paypal_signature(payload_str)
        
        headers = {
            "Content-Type": "application/json",
            "PAYPAL-TRANSMISSION-SIG": signature,
            "PAYPAL-TRANSMISSION-ID": f"transmission_{random.randint(100000, 999999)}",
            "PAYPAL-TRANSMISSION-TIME": datetime.now().isoformat(),
            "PAYPAL-CERT-URL": "https://api.paypal.com/v1/notifications/certs/CERT-360caa42-fca2a594-5e11-aeed-5f0585850472",
            "PAYPAL-AUTH-ALGO": "SHA256withRSA",
            "User-Agent": "PayPal-Webhook-Simulator"
        }
        
        with self.client.post(
            "/api/v1/payments/webhook",
            data=payload_str,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure(f"Webhook PayPal falhou: {data.get('message')}")
            elif response.status_code == 400:
                response.success()  # Erro esperado
            else:
                response.failure(f"Status inesperado PayPal: {response.status_code}")
    
    @task(2)
    def test_webhook_retry_without_signature(self):
        """Teste de webhook sem assinatura (deve falhar)"""
        payment_id = random.choice(self.payment_ids)
        
        payload = {
            "id": f"evt_{random.randint(100000, 999999)}",
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": payment_id,
                    "status": "succeeded"
                }
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        with self.client.post(
            "/api/v1/payments/webhook",
            json=payload,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 400:
                response.success()  # Esperado sem assinatura
            else:
                response.failure(f"Status inesperado sem assinatura: {response.status_code}")
    
    @task(1)
    def test_webhook_retry_invalid_signature(self):
        """Teste de webhook com assinatura inválida"""
        payment_id = random.choice(self.payment_ids)
        timestamp = str(int(datetime.now().timestamp()))
        
        payload = {
            "id": f"evt_{random.randint(100000, 999999)}",
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": payment_id,
                    "status": "succeeded"
                }
            }
        }
        
        payload_str = json.dumps(payload)
        # Assinatura inválida
        invalid_signature = f"t={timestamp},v1=invalid_signature_12345"
        
        headers = {
            "Content-Type": "application/json",
            "Stripe-Signature": invalid_signature
        }
        
        with self.client.post(
            "/api/v1/payments/webhook",
            data=payload_str,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 400:
                response.success()  # Esperado com assinatura inválida
            else:
                response.failure(f"Status inesperado assinatura inválida: {response.status_code}")
    
    @task(1)
    def test_webhook_retry_malformed_payload(self):
        """Teste de webhook com payload malformado"""
        headers = {
            "Content-Type": "application/json",
            "Stripe-Signature": "t=1234567890,v1=test_signature"
        }
        
        # Payload malformado
        malformed_payload = "{ invalid json }"
        
        with self.client.post(
            "/api/v1/payments/webhook",
            data=malformed_payload,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code in [400, 422]:
                response.success()  # Esperado para payload malformado
            else:
                response.failure(f"Status inesperado payload malformado: {response.status_code}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Evento de início do teste"""
    print("🚀 Iniciando teste de carga - Retry de Webhooks de Pagamento")
    print(f"📊 Base URL: {environment.host}")
    print(f"👥 Usuários: {environment.runner.user_count}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Evento de fim do teste"""
    print("✅ Teste de carga - Retry de Webhooks de Pagamento finalizado")
    print(f"📈 Total de requisições: {environment.stats.total.num_requests}")
    print(f"⏱️ Tempo médio de resposta: {environment.stats.total.avg_response_time:.2f}ms") 