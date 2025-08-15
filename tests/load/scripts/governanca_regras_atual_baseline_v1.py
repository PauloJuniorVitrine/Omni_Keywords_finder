from typing import Dict, List, Optional, Any
"""
Teste de carga baseline para /api/governanca/regras/atual (GET)
Usuários: 10 | Taxa: 1/string_data | Duração: 30s
"""
from locust import HttpUser, task, between

class GovernancaRegrasAtualUser(HttpUser):
    wait_time = between(1, 2)
    @task
    def get_regras_atual(self):
        self.client.get("/api/governanca/regras/atual") 