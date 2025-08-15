from typing import Dict, List, Optional, Any
"""
Teste de carga stress para /api/processar_keywords (POST)
Usuários: 400 | Taxa: 40/string_data | Duração: 30s
"""
from locust import HttpUser, task, between

class ProcessarKeywordsUser(HttpUser):
    wait_time = between(0.01, 0.05)
    @task
    def post_keywords(self):
        payload = {
            "keywords": [
                {"termo": "python carga", "volume_busca": 100, "cpc": 1.2, "concorrencia": 0.3, "intencao": "informacional"},
                {"termo": "pytest carga", "volume_busca": 80, "cpc": 0.9, "concorrencia": 0.2, "intencao": "informacional"}
            ]
        }
        self.client.post("/api/processar_keywords", json=payload) 