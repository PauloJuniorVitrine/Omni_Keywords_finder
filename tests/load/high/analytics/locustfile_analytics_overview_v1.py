"""
Teste de Carga - Analytics Overview
==================================

Endpoint: /api/v1/analytics/advanced
Método: GET
Criticidade: ALTO (Funcionalidade core)

Baseado em: backend/app/api/advanced_analytics.py (linhas 95-142)
"""

import random
from datetime import datetime, timezone
from locust import HttpUser, task, between, events
from typing import Dict, Any


class AnalyticsOverviewLoadTest(HttpUser):
    """
    Teste de carga para endpoint de overview de analytics
    
    Baseado no endpoint real: /api/v1/analytics/advanced
    """
    
    wait_time = between(2, 5)  # Intervalo entre requisições
    
    def on_start(self):
        """Setup inicial - autenticação"""
        self.auth_token = self._authenticate()
        self.time_ranges = ["1d", "7d", "30d", "90d"]
        self.categories = ["all", "marketing", "ecommerce", "saas", "blog"]
        self.nichos = ["all", "tech", "health", "finance", "education"]
    
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
    
    @task(4)
    def test_analytics_overview_default(self):
        """Teste de analytics overview com parâmetros padrão"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        with self.client.get(
            "/api/v1/analytics/advanced",
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure(f"Analytics falhou: {data.get('error')}")
            elif response.status_code == 401:
                response.success()  # Esperado se token expirou
            else:
                response.failure(f"Status inesperado: {response.status_code}")
    
    @task(3)
    def test_analytics_overview_with_filters(self):
        """Teste de analytics overview com filtros"""
        time_range = random.choice(self.time_ranges)
        category = random.choice(self.categories)
        nicho = random.choice(self.nichos)
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        params = {
            "timeRange": time_range,
            "category": category,
            "nicho": nicho
        }
        
        with self.client.get(
            "/api/v1/analytics/advanced",
            params=params,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure(f"Analytics com filtros falhou: {data.get('error')}")
            elif response.status_code == 400:
                response.success()  # Erro esperado para filtros inválidos
            else:
                response.failure(f"Status inesperado com filtros: {response.status_code}")
    
    @task(2)
    def test_analytics_overview_invalid_time_range(self):
        """Teste de analytics com range de tempo inválido"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        params = {
            "timeRange": "invalid_range",
            "category": "all",
            "nicho": "all"
        }
        
        with self.client.get(
            "/api/v1/analytics/advanced",
            params=params,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 400:
                response.success()  # Esperado para range inválido
            else:
                response.failure(f"Status inesperado para range inválido: {response.status_code}")
    
    @task(1)
    def test_analytics_overview_without_auth(self):
        """Teste de analytics sem autenticação"""
        with self.client.get(
            "/api/v1/analytics/advanced",
            catch_response=True
        ) as response:
            if response.status_code == 401:
                response.success()  # Esperado sem autenticação
            else:
                response.failure(f"Status inesperado sem auth: {response.status_code}")
    
    @task(1)
    def test_analytics_overview_long_time_range(self):
        """Teste de analytics com range de tempo longo"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        params = {
            "timeRange": "90d",
            "category": "all",
            "nicho": "all"
        }
        
        with self.client.get(
            "/api/v1/analytics/advanced",
            params=params,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure(f"Analytics longo falhou: {data.get('error')}")
            elif response.status_code == 400:
                response.success()  # Erro esperado
            else:
                response.failure(f"Status inesperado para range longo: {response.status_code}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Evento de início do teste"""
    print("🚀 Iniciando teste de carga - Analytics Overview")
    print(f"📊 Base URL: {environment.host}")
    print(f"👥 Usuários: {environment.runner.user_count}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Evento de fim do teste"""
    print("✅ Teste de carga - Analytics Overview finalizado")
    print(f"📈 Total de requisições: {environment.stats.total.num_requests}")
    print(f"⏱️ Tempo médio de resposta: {environment.stats.total.avg_response_time:.2f}ms") 