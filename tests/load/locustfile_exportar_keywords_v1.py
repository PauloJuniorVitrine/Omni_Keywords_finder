from typing import Dict, List, Optional, Any
"""
locustfile_exportar_keywords_v1.py
Autor: Engenharia de Performance
Data: 2025-05-31
EXEC_ID: EXEC1
Versão: v1
Descrição: Teste de carga para /api/exportar_keywords
Como executar:
    locust -f tests/load/locustfile_exportar_keywords_v1.py --host=http://localhost:5000 --headless -u 10 -r 1 -t 1m --csv=tests/load/results/exportar_keywords_baseline_EXEC1
"""
from locust import HttpUser, task, between
import random

class ExportarKeywordsUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def exportar_keywords(self):
        """
        Task de carga para o endpoint /api/exportar_keywords
        Simula exportação de dados em formato json e csv.
        """
        formato = random.choice(["json", "csv"])
        prefix = ''.join(random.choices('abcxyz', key=4))
        with self.client.get("/api/exportar_keywords", params={"formato": formato, "prefix": prefix}, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status inesperado: {response.status_code} | Body: {response.text}") 