"""
Teste de Carga - Exportação de Analytics
========================================

Endpoint: /api/v1/analytics/export
Método: POST
Criticidade: ALTO (Funcionalidade core)

Baseado em: backend/app/api/advanced_analytics.py (linhas 325-405)
"""

import json
import random
from datetime import datetime, timezone
from locust import HttpUser, task, between, events
from typing import Dict, Any


class AnalyticsExportLoadTest(HttpUser):
    """
    Teste de carga para endpoint de exportação de analytics
    
    Baseado no endpoint real: /api/v1/analytics/export
    """
    
    wait_time = between(5, 10)  # Intervalo maior para exportação
    
    def on_start(self):
        """Setup inicial - autenticação"""
        self.auth_token = self._authenticate()
        self.time_ranges = ["1d", "7d", "30d", "90d"]
        self.categories = ["all", "marketing", "ecommerce", "saas", "blog"]
        self.nichos = ["all", "tech", "health", "finance", "education"]
        self.formats = ["csv", "json", "excel", "pdf"]
        self.metrics = ["performance", "efficiency", "behavior"]
    
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
    
    @task(3)
    def test_export_csv(self):
        """Teste de exportação CSV"""
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "format": "csv",
            "timeRange": random.choice(self.time_ranges),
            "category": random.choice(self.categories),
            "nicho": random.choice(self.nichos),
            "metrics": random.sample(self.metrics, random.randint(1, 3))
        }
        
        with self.client.post(
            "/api/v1/analytics/export",
            json=payload,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure(f"Exportação CSV falhou: {data.get('error')}")
            elif response.status_code == 400:
                response.success()  # Erro esperado para parâmetros inválidos
            else:
                response.failure(f"Status inesperado CSV: {response.status_code}")
    
    @task(2)
    def test_export_json(self):
        """Teste de exportação JSON"""
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "format": "json",
            "timeRange": random.choice(self.time_ranges),
            "category": random.choice(self.categories),
            "nicho": random.choice(self.nichos),
            "metrics": ["performance", "efficiency"]
        }
        
        with self.client.post(
            "/api/v1/analytics/export",
            json=payload,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure(f"Exportação JSON falhou: {data.get('error')}")
            elif response.status_code == 400:
                response.success()  # Erro esperado
            else:
                response.failure(f"Status inesperado JSON: {response.status_code}")
    
    @task(2)
    def test_export_excel(self):
        """Teste de exportação Excel"""
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "format": "excel",
            "timeRange": random.choice(self.time_ranges),
            "category": random.choice(self.categories),
            "nicho": random.choice(self.nichos),
            "metrics": ["performance", "efficiency", "behavior"]
        }
        
        with self.client.post(
            "/api/v1/analytics/export",
            json=payload,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure(f"Exportação Excel falhou: {data.get('error')}")
            elif response.status_code == 400:
                response.success()  # Erro esperado
            else:
                response.failure(f"Status inesperado Excel: {response.status_code}")
    
    @task(1)
    def test_export_pdf(self):
        """Teste de exportação PDF"""
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "format": "pdf",
            "timeRange": random.choice(self.time_ranges),
            "category": random.choice(self.categories),
            "nicho": random.choice(self.nichos),
            "metrics": ["performance"]
        }
        
        with self.client.post(
            "/api/v1/analytics/export",
            json=payload,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure(f"Exportação PDF falhou: {data.get('error')}")
            elif response.status_code == 400:
                response.success()  # Erro esperado
            else:
                response.failure(f"Status inesperado PDF: {response.status_code}")
    
    @task(1)
    def test_export_invalid_format(self):
        """Teste de exportação com formato inválido"""
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "format": "invalid_format",
            "timeRange": "7d",
            "category": "all",
            "nicho": "all",
            "metrics": ["performance"]
        }
        
        with self.client.post(
            "/api/v1/analytics/export",
            json=payload,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 400:
                response.success()  # Esperado para formato inválido
            else:
                response.failure(f"Status inesperado formato inválido: {response.status_code}")
    
    @task(1)
    def test_export_without_auth(self):
        """Teste de exportação sem autenticação"""
        payload = {
            "format": "csv",
            "timeRange": "7d",
            "category": "all",
            "nicho": "all",
            "metrics": ["performance"]
        }
        
        headers = {"Content-Type": "application/json"}
        
        with self.client.post(
            "/api/v1/analytics/export",
            json=payload,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 401:
                response.success()  # Esperado sem autenticação
            else:
                response.failure(f"Status inesperado sem auth: {response.status_code}")
    
    @task(1)
    def test_export_large_dataset(self):
        """Teste de exportação com dataset grande"""
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "format": "csv",
            "timeRange": "90d",
            "category": "all",
            "nicho": "all",
            "metrics": ["performance", "efficiency", "behavior"]
        }
        
        with self.client.post(
            "/api/v1/analytics/export",
            json=payload,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure(f"Exportação grande falhou: {data.get('error')}")
            elif response.status_code in [400, 413]:
                response.success()  # Erro esperado para dataset muito grande
            else:
                response.failure(f"Status inesperado dataset grande: {response.status_code}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Evento de início do teste"""
    print("🚀 Iniciando teste de carga - Exportação de Analytics")
    print(f"📊 Base URL: {environment.host}")
    print(f"👥 Usuários: {environment.runner.user_count}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Evento de fim do teste"""
    print("✅ Teste de carga - Exportação de Analytics finalizado")
    print(f"📈 Total de requisições: {environment.stats.total.num_requests}")
    print(f"⏱️ Tempo médio de resposta: {environment.stats.total.avg_response_time:.2f}ms") 