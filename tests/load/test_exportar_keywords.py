from typing import Dict, List, Optional, Any
"""
Teste de carga para o endpoint /exportar_keywords.
Cenários positivos e negativos, logging estruturado, parametrização de host e versionamento de logs.
"""
import os
from locust import HttpUser, task, between, events
import random, json, time
from tests.load.utils.logging import log_request

class ExportarKeywordsUser(HttpUser):
    wait_time = between(1, 2)
    host = os.environ.get("LOCUST_HOST", "http://127.0.0.1:5000/api")

    @task(2)
    def exportar_keywords_json(self):
        prefix = f"test_kw_{random.randint(0,9999)}"
        with self.client.get(f"/exportar_keywords?formato=json&prefix={prefix}", catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Status: {resp.status_code}")

    @task(1)
    def exportar_keywords_csv(self):
        prefix = f"test_kw_{random.randint(0,9999)}"
        with self.client.get(f"/exportar_keywords?formato=csv&prefix={prefix}", catch_response=True) as resp:
            if resp.status_code == 200 and resp.headers.get("Content-Type", "").startswith("text/csv"):
                resp.success()
            else:
                resp.failure(f"Status: {resp.status_code}")

    @task(1)
    def exportar_keywords_invalido(self):
        # Formato inválido
        prefix = f"test_kw_{random.randint(0,9999)}"
        with self.client.get(f"/exportar_keywords?formato=xml&prefix={prefix}", catch_response=True) as resp:
            if resp.status_code == 400:
                resp.success()
            else:
                resp.failure(f"Esperado 400, obtido {resp.status_code}")

@events.request.add_listener
def _log_request(**kwargs):
    log_request(log_prefix="exportar_keywords", **kwargs) 