from typing import Dict, List, Optional, Any
"""
locustfile_test_reset_v1.py
Autor: Engenharia de Performance
Data: 2025-05-31
EXEC_ID: EXEC1
Versão: v1
Descrição: Teste de carga para /api/test/reset
Como executar:
    locust -f tests/load/locustfile_test_reset_v1.py --host=http://localhost:5000 --headless -u 10 -r 1 -t 1m --csv=tests/load/results/test_reset_baseline_EXEC1
"""
from locust import HttpUser, task, between

class TestResetUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def test_reset(self):
        """
        Task de carga para o endpoint /api/test/reset
        Simula reset de ambiente para garantir idempotência dos testes.
        """
        with self.client.post("/api/test/reset", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status inesperado: {response.status_code} | Body: {response.text}") 