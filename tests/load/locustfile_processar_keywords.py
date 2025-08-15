from locust import HttpUser, task, between
import random
import string
from typing import Dict, List, Optional, Any

class ProcessarKeywordsUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def processar_keywords(self):
        """
        Task de carga para o endpoint /api/processar_keywords
        Envia payloads variados simulando uso real.
        """
        payload = {
            "keywords": [
                {
                    "termo": ''.join(random.choices(string.ascii_lowercase, key=8)),
                    "volume_busca": random.randint(10, 10000),
                    "cpc": round(random.uniform(0.1, 10.0), 2),
                    "concorrencia": round(random.uniform(0, 1), 2)
                }
                for _ in range(random.randint(5, 20))
            ]
        }
        with self.client.post("/api/processar_keywords", json=payload, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status inesperado: {response.status_code} | Body: {response.text}") 