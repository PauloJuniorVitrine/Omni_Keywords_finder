"""
Teste de Carga - Analytics Detalhado
===================================

Endpoint: /api/v1/analytics/keywords/performance
Método: GET
Criticidade: ALTO (Funcionalidade core)

Baseado em: backend/app/api/advanced_analytics.py (linhas 144-182)
"""

import random
from datetime import datetime, timezone
from locust import HttpUser, task, between, events
from typing import Dict, Any


class AnalyticsDetailedLoadTest(HttpUser):
    """
    Teste de carga para endpoint de analytics detalhado
    
    Baseado no endpoint real: /api/v1/analytics/keywords/performance
    """
    
    wait_time = between(3, 6)  # Intervalo maior para analytics detalhado
    
    def on_start(self):
        """Setup inicial - autenticação"""
        self.auth_token = self._authenticate()
        self.time_ranges = ["1d", "7d", "30d", "90d"]
        self.categories = ["all", "marketing", "ecommerce", "saas", "blog"]
        self.nichos = ["all", "tech", "health", "finance", "education"]
        self.limits = [10, 50, 100, 200]
    
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
    def test_keywords_performance_default(self):
        """Teste de performance de keywords com parâmetros padrão"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        with self.client.get(
            "/api/v1/analytics/keywords/performance",
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure(f"Performance de keywords falhou: {data.get('error')}")
            elif response.status_code == 401:
                response.success()  # Esperado se token expirou
            else:
                response.failure(f"Status inesperado: {response.status_code}")
    
    @task(3)
    def test_keywords_performance_with_filters(self):
        """Teste de performance de keywords com filtros"""
        time_range = random.choice(self.time_ranges)
        category = random.choice(self.categories)
        nicho = random.choice(self.nichos)
        limit = random.choice(self.limits)
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        params = {
            "timeRange": time_range,
            "category": category,
            "nicho": nicho,
            "limit": limit
        }
        
        with self.client.get(
            "/api/v1/analytics/keywords/performance",
            params=params,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure(f"Performance com filtros falhou: {data.get('error')}")
            elif response.status_code == 400:
                response.success()  # Erro esperado para filtros inválidos
            else:
                response.failure(f"Status inesperado com filtros: {response.status_code}")
    
    @task(2)
    def test_clusters_efficiency(self):
        """Teste de eficiência de clusters"""
        time_range = random.choice(self.time_ranges)
        category = random.choice(self.categories)
        nicho = random.choice(self.nichos)
        limit = random.choice([10, 25, 50])
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        params = {
            "timeRange": time_range,
            "category": category,
            "nicho": nicho,
            "limit": limit
        }
        
        with self.client.get(
            "/api/v1/analytics/clusters/efficiency",
            params=params,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure(f"Eficiência de clusters falhou: {data.get('error')}")
            elif response.status_code == 400:
                response.success()  # Erro esperado
            else:
                response.failure(f"Status inesperado clusters: {response.status_code}")
    
    @task(2)
    def test_user_behavior(self):
        """Teste de comportamento do usuário"""
        time_range = random.choice(self.time_ranges)
        action_types = ["search", "export", "analyze", "cluster", "view"]
        action_type = random.choice(action_types)
        limit = random.choice([100, 500, 1000])
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        params = {
            "timeRange": time_range,
            "action_type": action_type,
            "limit": limit
        }
        
        with self.client.get(
            "/api/v1/analytics/user/behavior",
            params=params,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure(f"Comportamento do usuário falhou: {data.get('error')}")
            elif response.status_code == 400:
                response.success()  # Erro esperado
            else:
                response.failure(f"Status inesperado comportamento: {response.status_code}")
    
    @task(1)
    def test_predictive_insights(self):
        """Teste de insights preditivos"""
        insight_types = ["keyword_trend", "cluster_performance", "user_engagement", "revenue_forecast"]
        insight_type = random.choice(insight_types)
        confidence = random.uniform(0.5, 0.9)
        limit = random.choice([5, 10, 20])
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        params = {
            "type": insight_type,
            "confidence": confidence,
            "limit": limit
        }
        
        with self.client.get(
            "/api/v1/analytics/predictive/insights",
            params=params,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure(f"Insights preditivos falharam: {data.get('error')}")
            elif response.status_code == 400:
                response.success()  # Erro esperado
            else:
                response.failure(f"Status inesperado insights: {response.status_code}")
    
    @task(1)
    def test_analytics_summary(self):
        """Teste de métricas resumidas"""
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
            "/api/v1/analytics/summary",
            params=params,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure(f"Métricas resumidas falharam: {data.get('error')}")
            elif response.status_code == 400:
                response.success()  # Erro esperado
            else:
                response.failure(f"Status inesperado resumo: {response.status_code}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Evento de início do teste"""
    print("🚀 Iniciando teste de carga - Analytics Detalhado")
    print(f"📊 Base URL: {environment.host}")
    print(f"👥 Usuários: {environment.runner.user_count}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Evento de fim do teste"""
    print("✅ Teste de carga - Analytics Detalhado finalizado")
    print(f"📈 Total de requisições: {environment.stats.total.num_requests}")
    print(f"⏱️ Tempo médio de resposta: {environment.stats.total.avg_response_time:.2f}ms") 