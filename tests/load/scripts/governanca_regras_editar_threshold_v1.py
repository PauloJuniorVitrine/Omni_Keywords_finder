from typing import Dict, List, Optional, Any
"""
Teste de carga threshold para /api/governanca/regras/editar (POST)
Usuários: 100 | Taxa: 10/string_data | Duração: 1min
"""
from locust import HttpUser, task, between

class GovernancaRegrasEditarUser(HttpUser):
    wait_time = between(0.1, 0.2)
    @task
    def post_editar_regras(self):
        payload = {
            "score_minimo": 0.7,
            "blacklist": ["kw_banida1", "kw_banida2"],
            "whitelist": ["kw_livre1", "kw_livre2"]
        }
        headers = {"Content-Type": "application/json"}
        self.client.post("/api/governanca/regras/editar", json=payload, headers=headers) 