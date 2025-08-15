from typing import Dict, List, Optional, Any
"""
Teste de carga stress para /api/exportar_keywords (GET)
Usuários: 400 | Taxa: 40/string_data | Duração: 30s
"""
from locust import HttpUser, task, between

class ExportarKeywordsUser(HttpUser):
    wait_time = between(0.01, 0.05)
    @task
    def get_exportar_keywords(self):
        params = {"formato": "json", "prefix": "python_"}
        self.client.get("/api/exportar_keywords", params=params) 