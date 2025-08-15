"""
Teste de Carga - Reembolso de Pagamentos
========================================

Endpoint: /api/v1/payments/{payment_id}/refund
Método: POST
Criticidade: CRÍTICA (Receita do sistema)

Baseado em: backend/app/api/payments_v1.py (linhas 219-285)
"""

import json
import random
from datetime import datetime, timezone
from locust import HttpUser, task, between, events
from typing import Dict, Any


class PaymentRefundLoadTest(HttpUser):
    """
    Teste de carga para endpoint de reembolso de pagamentos
    
    Baseado no endpoint real: /api/v1/payments/{payment_id}/refund
    """
    
    wait_time = between(1, 3)  # Intervalo entre requisições
    
    def on_start(self):
        """Setup inicial - autenticação"""
        self.auth_token = self._authenticate()
        self.payment_ids = self._get_available_payment_ids()
    
    def _authenticate(self) -> str:
        """Autenticação para obter token"""
        try:
            response = self.client.post("/api/auth/login", json={
                "email": "test@example.com",
                "password": "testpassword123"
            })
            
            if response.status_code == 200:
                data = response.json()
                return data.get("access_token", "")
            else:
                print(f"Falha na autenticação: {response.status_code}")
                return ""
                
        except Exception as e:
            print(f"Erro na autenticação: {str(e)}")
            return ""
    
    def _get_available_payment_ids(self) -> list:
        """Obtém IDs de pagamentos disponíveis para reembolso"""
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = self.client.get("/api/v1/payments/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                payments = data.get("payments", [])
                # Filtrar apenas pagamentos que podem ser reembolsados
                refundable_payments = [
                    p["id"] for p in payments 
                    if p.get("status") in ["completed", "succeeded"]
                ]
                return refundable_payments[:10]  # Limitar a 10 IDs
            else:
                print(f"Falha ao obter pagamentos: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Erro ao obter pagamentos: {str(e)}")
            return []
    
    @task(3)
    def test_refund_full_amount(self):
        """Teste de reembolso do valor total"""
        if not self.payment_ids:
            return
            
        payment_id = random.choice(self.payment_ids)
        
        # Payload baseado no modelo PaymentRefundRequest real
        payload = {
            "payment_id": payment_id,
            "refund_id": f"refund_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}",
            "amount": None,  # Reembolso total
            "reason": "customer_request",
            "description": "Reembolso solicitado pelo cliente"
        }
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        with self.client.post(
            f"/api/v1/payments/{payment_id}/refund",
            json=payload,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure(f"Reembolso falhou: {data.get('message')}")
            elif response.status_code == 400:
                # Erro esperado para alguns casos
                response.success()
            elif response.status_code == 404:
                response.success()  # Pagamento não encontrado é válido
            else:
                response.failure(f"Status inesperado: {response.status_code}")
    
    @task(2)
    def test_refund_partial_amount(self):
        """Teste de reembolso parcial"""
        if not self.payment_ids:
            return
            
        payment_id = random.choice(self.payment_ids)
        
        # Payload para reembolso parcial
        payload = {
            "payment_id": payment_id,
            "refund_id": f"refund_partial_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}",
            "amount": random.randint(1000, 5000),  # Valor parcial em centavos
            "reason": "partial_refund",
            "description": "Reembolso parcial por item cancelado"
        }
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        with self.client.post(
            f"/api/v1/payments/{payment_id}/refund",
            json=payload,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure(f"Reembolso parcial falhou: {data.get('message')}")
            elif response.status_code == 400:
                response.success()  # Erro esperado
            else:
                response.failure(f"Status inesperado: {response.status_code}")
    
    @task(1)
    def test_refund_invalid_payment(self):
        """Teste de reembolso com ID inválido"""
        invalid_payment_id = f"invalid_{random.randint(100000, 999999)}"
        
        payload = {
            "payment_id": invalid_payment_id,
            "refund_id": f"refund_invalid_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}",
            "amount": None,
            "reason": "test_invalid",
            "description": "Teste com ID inválido"
        }
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        with self.client.post(
            f"/api/v1/payments/{invalid_payment_id}/refund",
            json=payload,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 404:
                response.success()  # Esperado para ID inválido
            elif response.status_code == 400:
                response.success()  # Também válido
            else:
                response.failure(f"Status inesperado para ID inválido: {response.status_code}")
    
    @task(1)
    def test_refund_without_auth(self):
        """Teste de reembolso sem autenticação"""
        if not self.payment_ids:
            return
            
        payment_id = random.choice(self.payment_ids)
        
        payload = {
            "payment_id": payment_id,
            "refund_id": f"refund_noauth_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}",
            "amount": None,
            "reason": "test_no_auth",
            "description": "Teste sem autenticação"
        }
        
        headers = {"Content-Type": "application/json"}
        
        with self.client.post(
            f"/api/v1/payments/{payment_id}/refund",
            json=payload,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 401:
                response.success()  # Esperado sem autenticação
            else:
                response.failure(f"Status inesperado sem auth: {response.status_code}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Evento de início do teste"""
    print("🚀 Iniciando teste de carga - Reembolso de Pagamentos")
    print(f"📊 Base URL: {environment.host}")
    print(f"👥 Usuários: {environment.runner.user_count}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Evento de fim do teste"""
    print("✅ Teste de carga - Reembolso de Pagamentos finalizado")
    print(f"📈 Total de requisições: {environment.stats.total.num_requests}")
    print(f"⏱️ Tempo médio de resposta: {environment.stats.total.avg_response_time:.2f}ms") 