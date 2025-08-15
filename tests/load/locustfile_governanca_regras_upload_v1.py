from typing import Dict, List, Optional, Any
"""
locustfile_governanca_regras_upload_v1.py
Autor: Engenharia de Performance
Data: 2025-05-31
EXEC_ID: EXEC1
Versão: v1
Descrição: Teste de carga para /api/governanca/regras/upload
Como executar:
    locust -f tests/load/locustfile_governanca_regras_upload_v1.py --host=http://localhost:5000 --headless -u 10 -r 1 -t 1m --csv=tests/load/results/governanca_regras_upload_baseline_EXEC1
"""
from locust import HttpUser, task, between
import io
import random

class GovernancaRegrasUploadUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def upload_regras(self):
        """
        Task de carga para o endpoint /api/governanca/regras/upload
        Simula upload de arquivo YAML.
        """
        yaml_content = f"""
score_minimo: {round(random.uniform(0.1, 1.0), 2)}
blacklist:
  - kw_banida
whitelist:
  - kw_livre
"""
        files = {"file": ("regras.yaml", io.BytesIO(yaml_content.encode()), "application/value-yaml")}
        with self.client.post("/api/governanca/regras/upload", files=files, catch_response=True) as response:
            if response.status_code in (200, 201, 422, 400):
                response.success()
            else:
                response.failure(f"Status inesperado: {response.status_code} | Body: {response.text}") 