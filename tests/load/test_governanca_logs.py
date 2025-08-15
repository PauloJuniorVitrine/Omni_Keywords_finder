from typing import Dict, List, Optional, Any
"""
Teste de carga para o endpoint /governanca/logs.
Cenários positivos e negativos, logging estruturado, parametrização de host e versionamento de logs.
"""
import os
from locust import HttpUser, task, between, events
import random, json, time
from tests.load.utils.logging import log_request

class GovernancaLogsUser(HttpUser):
    wait_time = between(1, 2)
    host = os.environ.get("LOCUST_HOST", "http://127.0.0.1:5000/api")

    @task(2)
    def consultar_logs(self):
        with self.client.get("/governanca/logs", catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Status: {resp.status_code}")

    @task(1)
    def consultar_logs_filtro(self):
        event = random.choice(["validacao_keywords", "evento_inexistente", "", None])
        params = f"?event={event}" if event else ""
        with self.client.get(f"/governanca/logs{params}", catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Status: {resp.status_code}")

    @task(1)
    def consultar_logs_invalido(self):
        # Parâmetro inválido
        with self.client.get("/governanca/logs?event=@@@@", catch_response=True) as resp:
            if resp.status_code in (400, 422):
                resp.success()
            else:
                resp.failure(f"Esperado 400/422, obtido {resp.status_code}")

@events.request.add_listener
def _log_request(**kwargs):
    log_request(log_prefix="governanca_logs", **kwargs) 