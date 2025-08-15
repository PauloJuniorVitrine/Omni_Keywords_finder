from typing import Dict, List, Optional, Any
"""
Teste de carga baseline para /api/governanca/logs (GET)
Usuários: 10 | Taxa: 1/string_data | Duração: 30s
"""
from locust import HttpUser, task, between

class GovernancaLogsUser(HttpUser):
    wait_time = between(1, 2)
    @task
    def get_logs(self):
        headers = {"Authorization": "Bearer token_valido"}
        params = {"event": "validacao_keywords"}
        self.client.get("/api/governanca/logs", headers=headers, params=params) 