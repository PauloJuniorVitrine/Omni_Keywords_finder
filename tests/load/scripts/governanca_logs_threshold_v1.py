from typing import Dict, List, Optional, Any
"""
Teste de carga threshold para /api/governanca/logs (GET)
Usuários: 100 | Taxa: 10/string_data | Duração: 1min
"""
from locust import HttpUser, task, between

class GovernancaLogsUser(HttpUser):
    wait_time = between(0.1, 0.2)
    @task
    def get_logs(self):
        headers = {"Authorization": "Bearer token_valido"}
        params = {"event": "validacao_keywords"}
        self.client.get("/api/governanca/logs", headers=headers, params=params) 