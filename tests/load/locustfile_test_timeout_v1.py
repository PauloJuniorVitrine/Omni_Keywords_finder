from typing import Dict, List, Optional, Any
"""
locustfile_test_timeout_v1.py
Autor: Engenharia de Performance
Data: 2025-05-31
EXEC_ID: EXEC1
Versão: v1
Descrição: Teste de carga para /api/test/timeout
Como executar:
    locust -f tests/load/locustfile_test_timeout_v1.py --host=http://localhost:5000 --headless -u 10 -r 1 -t 1m --csv=tests/load/results/test_timeout_baseline_EXEC1
"""
from locust import HttpUser, task, between
import requests

class TestTimeoutUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def test_timeout(self):
        """
        Task de carga para o endpoint /api/test/timeout
        Simula requisições que forçam timeout no backend.
        """
        try:
            with self.client.get("/api/test/timeout", timeout=5, catch_response=True) as response:
                if response.status_code in (200, 408, 504, 503, 502):
                    response.success()
                else:
                    response.failure(f"Status inesperado: {response.status_code} | Body: {response.text}")
        except requests.exceptions.ReadTimeout:
            print("[INFO] Timeout esperado capturado.")
            # Considera sucesso pois o objetivo é forçar timeout
        except Exception as e:
            print(f"[ERRO] Exceção inesperada: {e}") 