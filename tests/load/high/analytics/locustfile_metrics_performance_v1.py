"""
locustfile_metrics_performance_v1.py
Teste de carga para o endpoint /api/metrics/performance

Prompt: CHECKLIST_TESTES_CARGA_CRITICIDADE.md - Nível Alto
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Tracing ID: LOAD_METRICS_PERFORMANCE_20250127_001

Cenários:
- Consulta GET concorrente ao endpoint de métricas de performance
- Validação de latência, throughput, disponibilidade e integridade dos dados
- Simulação de picos e stress
- Análise de resposta e métricas Prometheus
"""

from locust import HttpUser, TaskSet, task, between, events
import time
import random
import json

ENDPOINT = "/api/metrics/performance"
TRACING_ID = "LOAD_METRICS_PERFORMANCE_20250127_001"

class MetricsPerformanceTasks(TaskSet):
    def on_start(self):
        self.headers = {
            "Content-Type": "application/json",
            "Tracing-ID": TRACING_ID
        }
        # Se necessário, autentique aqui
        # self.token = self.login_and_get_token()
        # self.headers["Authorization"] = f"Bearer {self.token}"

    @task(5)
    def get_performance_metrics(self):
        start = time.time()
        with self.client.get(ENDPOINT, headers=self.headers, name="GET /api/metrics/performance", catch_response=True) as response:
            elapsed = time.time() - start
            try:
                assert response.status_code == 200, f"Status code {response.status_code}"
                data = response.json()
                # Validação de integridade mínima
                assert "performance_metrics" in data or "system" in data, "Chave performance_metrics/system ausente"
                # Validação de latência
                assert elapsed < 2.0, f"Latência alta: {elapsed:.2f}s"
                response.success()
            except Exception as e:
                response.failure(str(e))

    @task(1)
    def get_performance_metrics_stress(self):
        # Simula consulta com parâmetros de stress (ex: minutos=180)
        params = {"minutes": random.choice([60, 120, 180])}
        start = time.time()
        with self.client.get(ENDPOINT, headers=self.headers, params=params, name="GET /api/metrics/performance?minutes", catch_response=True) as response:
            elapsed = time.time() - start
            try:
                assert response.status_code == 200, f"Status code {response.status_code}"
                data = response.json()
                assert "performance_metrics" in data or "system" in data, "Chave performance_metrics/system ausente"
                assert elapsed < 3.0, f"Latência alta: {elapsed:.2f}s"
                response.success()
            except Exception as e:
                response.failure(str(e))

class WebsiteUser(HttpUser):
    tasks = [MetricsPerformanceTasks]
    wait_time = between(0.5, 2.0)
    host = "http://localhost:8000"  # Ajuste conforme ambiente 