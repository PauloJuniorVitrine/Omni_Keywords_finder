from typing import Dict, List, Optional, Any
"""
Teste de carga stress para /api/governanca/regras/upload (POST)
Usuários: 400 | Taxa: 40/string_data | Duração: 30s
"""
from locust import HttpUser, task, between

class GovernancaRegrasUploadUser(HttpUser):
    wait_time = between(0.01, 0.05)
    @task
    def post_upload_regras(self):
        payload = {
            "score_minimo": 0.7,
            "blacklist": ["kw_banida1", "kw_banida2"],
            "whitelist": ["kw_livre1", "kw_livre2"]
        }
        headers = {"Content-Type": "application/json"}
        self.client.post("/api/governanca/regras/upload", json=payload, headers=headers) 