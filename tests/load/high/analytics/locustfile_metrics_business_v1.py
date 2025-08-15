"""
locustfile_metrics_business_v1.py
Teste de carga para os endpoints de métricas de negócio

Prompt: CHECKLIST_TESTES_CARGA_CRITICIDADE.md - Nível Alto
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Tracing ID: LOAD_METRICS_BUSINESS_20250127_001

Endpoints testados:
- GET /api/business-metrics/metrics - Consulta métricas com filtros
- GET /api/business-metrics/summary - Resumo das métricas principais
- GET /api/business-metrics/kpis - KPIs
- GET /api/business-metrics/dashboards - Dashboards
- POST /api/business-metrics/analyze - Análise de métricas

Cenários:
- Consulta GET concorrente aos endpoints de métricas de negócio
- Validação de latência, throughput, disponibilidade e integridade dos dados
- Simulação de picos e stress
- Análise de resposta e métricas de negócio
"""

from locust import HttpUser, TaskSet, task, between, events
import time
import random
import json
from datetime import datetime, timedelta

ENDPOINTS = {
    "metrics": "/api/business-metrics/metrics",
    "summary": "/api/business-metrics/summary", 
    "kpis": "/api/business-metrics/kpis",
    "dashboards": "/api/business-metrics/dashboards",
    "analyze": "/api/business-metrics/analyze"
}
TRACING_ID = "LOAD_METRICS_BUSINESS_20250127_001"

class MetricsBusinessTasks(TaskSet):
    def on_start(self):
        self.headers = {
            "Content-Type": "application/json",
            "Tracing-ID": TRACING_ID
        }
        # Se necessário, autentique aqui
        # self.token = self.login_and_get_token()
        # self.headers["Authorization"] = f"Bearer {self.token}"

    @task(4)
    def get_business_metrics(self):
        """Consulta métricas de negócio com filtros"""
        start = time.time()
        params = {
            "metric_types": random.choice(["users,revenue", "executions,keywords", "conversions"]),
            "periods": random.choice(["daily", "weekly", "monthly"]),
            "limit": random.choice([10, 50, 100])
        }
        with self.client.get(ENDPOINTS["metrics"], headers=self.headers, params=params, name="GET /api/business-metrics/metrics", catch_response=True) as response:
            elapsed = time.time() - start
            try:
                assert response.status_code == 200, f"Status code {response.status_code}"
                data = response.json()
                # Validação de integridade mínima
                assert isinstance(data, list), "Resposta deve ser uma lista"
                # Validação de latência
                assert elapsed < 2.0, f"Latência alta: {elapsed:.2f}s"
                response.success()
            except Exception as e:
                response.failure(str(e))

    @task(3)
    def get_metrics_summary(self):
        """Consulta resumo das métricas principais"""
        start = time.time()
        params = {"period": random.choice(["daily", "weekly", "monthly"])}
        with self.client.get(ENDPOINTS["summary"], headers=self.headers, params=params, name="GET /api/business-metrics/summary", catch_response=True) as response:
            elapsed = time.time() - start
            try:
                assert response.status_code == 200, f"Status code {response.status_code}"
                data = response.json()
                # Validação de integridade mínima
                assert "users" in data or "revenue" in data or "executions" in data, "Chaves de resumo ausentes"
                # Validação de latência
                assert elapsed < 1.5, f"Latência alta: {elapsed:.2f}s"
                response.success()
            except Exception as e:
                response.failure(str(e))

    @task(2)
    def get_kpis(self):
        """Consulta KPIs"""
        start = time.time()
        with self.client.get(ENDPOINTS["kpis"], headers=self.headers, name="GET /api/business-metrics/kpis", catch_response=True) as response:
            elapsed = time.time() - start
            try:
                assert response.status_code == 200, f"Status code {response.status_code}"
                data = response.json()
                # Validação de integridade mínima
                assert isinstance(data, list), "Resposta deve ser uma lista"
                # Validação de latência
                assert elapsed < 1.5, f"Latência alta: {elapsed:.2f}s"
                response.success()
            except Exception as e:
                response.failure(str(e))

    @task(1)
    def get_dashboards(self):
        """Consulta dashboards"""
        start = time.time()
        with self.client.get(ENDPOINTS["dashboards"], headers=self.headers, name="GET /api/business-metrics/dashboards", catch_response=True) as response:
            elapsed = time.time() - start
            try:
                assert response.status_code == 200, f"Status code {response.status_code}"
                data = response.json()
                # Validação de integridade mínima
                assert isinstance(data, list), "Resposta deve ser uma lista"
                # Validação de latência
                assert elapsed < 2.0, f"Latência alta: {elapsed:.2f}s"
                response.success()
            except Exception as e:
                response.failure(str(e))

    @task(1)
    def analyze_business_metrics(self):
        """Análise de métricas de negócio"""
        start = time.time()
        payload = {
            "metric_type": random.choice(["users", "revenue", "executions"]),
            "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "end_date": datetime.now().isoformat()
        }
        with self.client.post(ENDPOINTS["analyze"], headers=self.headers, json=payload, name="POST /api/business-metrics/analyze", catch_response=True) as response:
            elapsed = time.time() - start
            try:
                assert response.status_code == 200, f"Status code {response.status_code}"
                data = response.json()
                # Validação de integridade mínima
                assert "analysis" in data or "insights" in data, "Chaves de análise ausentes"
                # Validação de latência
                assert elapsed < 3.0, f"Latência alta: {elapsed:.2f}s"
                response.success()
            except Exception as e:
                response.failure(str(e))

class WebsiteUser(HttpUser):
    tasks = [MetricsBusinessTasks]
    wait_time = between(1.0, 3.0)
    host = "http://localhost:8000"  # Ajuste conforme ambiente 