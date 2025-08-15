from typing import Dict, List, Optional, Any
"""
Teste de carga stress para /api/governanca/regras/atual (GET)
Usuários: 400 | Taxa: 40/string_data | Duração: 30s
"""
from locust import HttpUser, task, between

class GovernancaRegrasAtualUser(HttpUser):
    wait_time = between(0.01, 0.05)
    @task
    def get_regras_atual(self):
        self.client.get("/api/governanca/regras/atual") 