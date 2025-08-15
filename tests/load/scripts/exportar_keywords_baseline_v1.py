from typing import Dict, List, Optional, Any
"""
Teste de carga baseline para /api/exportar_keywords (GET)
Usuários: 10 | Taxa: 1/string_data | Duração: 30s
"""
from locust import HttpUser, task, between

class ExportarKeywordsUser(HttpUser):
    wait_time = between(1, 2)
    @task
    def get_exportar_keywords(self):
        params = {"formato": "json", "prefix": "python_"}
        self.client.get("/api/exportar_keywords", params=params) 