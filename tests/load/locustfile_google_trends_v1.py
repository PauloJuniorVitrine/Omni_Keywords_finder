from typing import Dict, List, Optional, Any
"""
locustfile_google_trends_v1.py
Autor: Engenharia de Performance
Data: 2025-05-31
EXEC_ID: EXEC1
Versão: v1
Descrição: Teste de carga para /api/externo/google_trends
Como executar:
    locust -f tests/load/locustfile_google_trends_v1.py --host=http://localhost:5000 --headless -u 10 -r 1 -t 1m --csv=tests/load/results/google_trends_baseline_EXEC1
"""
from locust import HttpUser, task, between
import random

class GoogleTrendsUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def google_trends(self):
        """
        Task de carga para o endpoint /api/externo/google_trends
        Simula integração externa e fallback.
        """
        termo = ''.join(random.choices('abcxyz', key=6))
        simular = random.choice([None, "timeout", "erro_autenticacao", "resposta_invalida"])
        params = {"termo": termo}
        if simular:
            params["simular"] = simular
        with self.client.get("/api/externo/google_trends", params=params, catch_response=True) as response:
            if response.status_code in (200, 401, 502, 503, 408, 504):
                response.success()
            else:
                print(f"[ERRO] Status inesperado: {response.status_code} | Body: {response.text}")
                response.failure(f"Status inesperado: {response.status_code} | Body: {response.text}") 