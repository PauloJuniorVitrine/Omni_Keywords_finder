from typing import Dict, List, Optional, Any
"""
Teste de carga threshold para /api/externo/google_trends (GET)
Usuários: 100 | Taxa: 10/string_data | Duração: 1min
"""
from locust import HttpUser, task, between

class GoogleTrendsUser(HttpUser):
    wait_time = between(0.1, 0.2)
    @task
    def get_google_trends(self):
        params = {"termo": "python carga"}
        self.client.get("/api/externo/google_trends", params=params) 