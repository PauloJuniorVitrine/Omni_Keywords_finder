from typing import Dict, List, Optional, Any
"""
locustfile_governanca_logs_v1.py
Autor: Engenharia de Performance
Data: 2025-05-31
EXEC_ID: EXEC1
Versão: v1
Descrição: Teste de carga para /api/governanca/logs
Como executar:
    locust -f tests/load/locustfile_governanca_logs_v1.py --host=http://localhost:5000 --headless -u 10 -r 1 -t 1m --csv=tests/load/results/governanca_logs_baseline_EXEC1
"""
from locust import HttpUser, task, between
import random

class GovernancaLogsUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def governanca_logs(self):
        """
        Task de carga para o endpoint /api/governanca/logs
        Simula busca filtrada e autenticação.
        """
        event = random.choice(["validacao_keywords", "evento_inexistente", "@@@@"])
        token = random.choice([
            "Bearer token_valido",
            "Bearer token_invalido",
            "",
            "Bearer ",
        ])
        with self.client.get("/api/governanca/logs", params={"event": event}, headers={"Authorization": "Bearer token_teste"}, catch_response=True) as response:
            if response.status_code in (200, 401, 400):
                response.success()
            else:
                response.failure(f"Status inesperado: {response.status_code} | Body: {response.text}") 