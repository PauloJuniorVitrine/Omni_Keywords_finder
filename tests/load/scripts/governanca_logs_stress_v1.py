from typing import Dict, List, Optional, Any
"""
Teste de carga stress para /api/governanca/logs (GET)
Usuários: 400 | Taxa: 40/string_data | Duração: 30s
"""
from locust import HttpUser, task, between

class GovernancaLogsUser(HttpUser):
    wait_time = between(0.01, 0.05)
    @task
    def get_logs(self):
        headers = {"Authorization": "Bearer token_valido"}
        params = {"event": "validacao_keywords"}
        self.client.get("/api/governanca/logs", headers=headers, params=params) 