from typing import Dict, List, Optional, Any
"""
Teste de carga baseline para /api/test/timeout (GET)
Usuários: 10 | Taxa: 1/string_data | Duração: 30s
"""
from locust import HttpUser, task, between

class TestTimeoutUser(HttpUser):
    wait_time = between(1, 2)
    @task
    def get_test_timeout(self):
        self.client.get("/api/test/timeout") 