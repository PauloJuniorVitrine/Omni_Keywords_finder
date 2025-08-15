from typing import Dict, List, Optional, Any
"""
run_all_load_tests.py
Autor: Engenharia de Performance
Data: 2025-05-31
EXEC_ID: EXEC1
Descrição: Orquestração automatizada dos testes de carga para todos os fluxos críticos.
Como executar:
    python tests/load/run_all_load_tests.py
"""
import subprocess
import os
from datetime import datetime

# Parâmetros dos ciclos
CICLOS = [
    ("baseline", 10, 1, "1m"),
    ("threshold", 100, 10, "5m"),
    ("stress", 400, 40, "2m"),
]

# Locustfiles e fluxos (ajustado para nomes reais)
FLUXOS = [
    ("processar_keywords", "locustfile_processar_keywords_v1.py"),
    ("exportar_keywords", "locustfile_exportar_keywords_v1.py"),
    ("governanca_logs", "locustfile_governanca_logs_v1.py"),
    ("governanca_regras_upload", "locustfile_governanca_regras_upload_v1.py"),
    ("test_timeout", "locustfile_test_timeout_v1.py"),
    ("test_reset", "locustfile_test_reset_v1.py"),
    ("google_trends", "locustfile_google_trends_v1.py"),
]

RESULTS_DIR = "tests/load/results"
LOGS_DIR = "tests/load/logs"
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

for fluxo, locustfile in FLUXOS:
    for ciclo, usuarios, rate, duracao in CICLOS:
        print(f"Iniciando {fluxo} [{ciclo}] - Usuários: {usuarios}, Rate: {rate}/string_data, Duração: {duracao}")
        csv_path = os.path.join(RESULTS_DIR, f"{fluxo}_{ciclo}_EXEC1")
        log_path = os.path.join(LOGS_DIR, f"LOAD_LOG_{fluxo}_{ciclo}_EXEC1.md")
        cmd = [
            "python", "-m", "locust",
            "-f", f"tests/load/{locustfile}",
            "--host=http://localhost:5000",
            "--headless",
            f"-u", str(usuarios),
            f"-r", str(rate),
            f"-t", duracao,
            f"--csv={csv_path}"
        ]
        try:
            with open(log_path, "w") as logf:
                proc = subprocess.run(cmd, stdout=logf, stderr=subprocess.STDOUT, check=True)
            print(f"✅ {fluxo} [{ciclo}] concluído com sucesso.")
        except Exception as e:
            print(f"❌ {fluxo} [{ciclo}] erro de execução: {e}") 