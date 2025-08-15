"""
locustfile_metrics_system_v1.py
Teste de carga para o endpoint /api/metrics/system

Prompt: CHECKLIST_TESTES_CARGA_CRITICIDADE.md - Nível Alto
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Tracing ID: LOAD_METRICS_SYSTEM_20250127_001

Cenários:
- Consulta GET concorrente ao endpoint de métricas do sistema
- Validação de latência, throughput, disponibilidade e integridade dos dados
- Simulação de picos e stress
- Análise de resposta e métricas do sistema (CPU, memória, disco, rede)
"""

from locust import HttpUser, TaskSet, task, between, events
import time
import random
import json

ENDPOINT = "/api/metrics/system"
TRACING_ID = "LOAD_METRICS_SYSTEM_20250127_001"

class MetricsSystemTasks(TaskSet):
    def on_start(self):
        self.headers = {
            "Content-Type": "application/json",
            "Tracing-ID": TRACING_ID
        }
        # Se necessário, autentique aqui
        # self.token = self.login_and_get_token()
        # self.headers["Authorization"] = f"Bearer {self.token}"

    @task(5)
    def get_system_metrics(self):
        """Consulta métricas do sistema"""
        start = time.time()
        with self.client.get(ENDPOINT, headers=self.headers, name="GET /api/metrics/system", catch_response=True) as response:
            elapsed = time.time() - start
            try:
                assert response.status_code == 200, f"Status code {response.status_code}"
                data = response.json()
                # Validação de integridade mínima
                assert "cpu" in data or "memory" in data or "disk" in data, "Chaves de métricas do sistema ausentes"
                # Validação de latência
                assert elapsed < 1.5, f"Latência alta: {elapsed:.2f}s"
                response.success()
            except Exception as e:
                response.failure(str(e))

    @task(2)
    def get_system_metrics_stress(self):
        """Consulta métricas do sistema com stress (múltiplas requisições concorrentes)"""
        start = time.time()
        # Simular múltiplas requisições concorrentes
        for i in range(random.randint(1, 3)):
            with self.client.get(ENDPOINT, headers=self.headers, name="GET /api/metrics/system (stress)", catch_response=True) as response:
                elapsed = time.time() - start
                try:
                    assert response.status_code == 200, f"Status code {response.status_code}"
                    data = response.json()
                    assert "cpu" in data or "memory" in data or "disk" in data, "Chaves de métricas do sistema ausentes"
                    assert elapsed < 2.0, f"Latência alta: {elapsed:.2f}s"
                    response.success()
                except Exception as e:
                    response.failure(str(e))

    @task(1)
    def get_system_metrics_continuous(self):
        """Consulta contínua de métricas do sistema"""
        start = time.time()
        # Simular consulta contínua (múltiplas requisições em sequência)
        for i in range(3):
            with self.client.get(ENDPOINT, headers=self.headers, name="GET /api/metrics/system (continuous)", catch_response=True) as response:
                elapsed = time.time() - start
                try:
                    assert response.status_code == 200, f"Status code {response.status_code}"
                    data = response.json()
                    assert "cpu" in data or "memory" in data or "disk" in data, "Chaves de métricas do sistema ausentes"
                    assert elapsed < 3.0, f"Latência alta: {elapsed:.2f}s"
                    response.success()
                except Exception as e:
                    response.failure(str(e))

class WebsiteUser(HttpUser):
    tasks = [MetricsSystemTasks]
    wait_time = between(0.5, 2.0)
    host = "http://localhost:8000"  # Ajuste conforme ambiente 