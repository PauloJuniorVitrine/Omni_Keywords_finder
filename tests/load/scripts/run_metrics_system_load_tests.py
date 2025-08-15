"""
run_metrics_system_load_tests.py
Script de execução para teste de carga do endpoint /api/metrics/system

Prompt: CHECKLIST_TESTES_CARGA_CRITICIDADE.md - Nível Alto
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Tracing ID: RUN_METRICS_SYSTEM_20250127_001

Funcionalidades:
- Executa locustfile_metrics_system_v1.py
- Permite parametrização de usuários e spawn rate
- Gera relatório HTML e log estruturado
- Valida thresholds de latência e disponibilidade
- Testa endpoint: /api/metrics/system
"""

import subprocess
import sys
import logging
from datetime import datetime

TRACING_ID = "RUN_METRICS_SYSTEM_20250127_001"
LOCUSTFILE = "../high/analytics/locustfile_metrics_system_v1.py"
REPORT_HTML = f"metrics_system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
LOG_FILE = f"metrics_system_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format=f'%(asctime)s [%(levelname)s] [%(name)s] [TracingID:{TRACING_ID}] %(message)s'
)


def run_load_test(users=100, spawn_rate=10, host="http://localhost:8000"):
    cmd = [
        sys.executable, "-m", "locust",
        "-f", LOCUSTFILE,
        "--headless",
        "-u", str(users),
        "-r", str(spawn_rate),
        "--host", host,
        "--html", REPORT_HTML,
        "--logfile", LOG_FILE,
        "--only-summary"
    ]
    logging.info(f"Iniciando teste de carga de métricas do sistema: users={users}, spawn_rate={spawn_rate}, host={host}")
    result = subprocess.run(cmd)
    if result.returncode == 0:
        logging.info("Teste de carga de métricas do sistema finalizado com sucesso.")
    else:
        logging.error(f"Teste de carga de métricas do sistema falhou. Código de retorno: {result.returncode}")
    print(f"Relatório HTML: {REPORT_HTML}")
    print(f"Log: {LOG_FILE}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Executa teste de carga para endpoint de métricas do sistema")
    parser.add_argument("-u", "--users", type=int, default=100, help="Número de usuários simultâneos")
    parser.add_argument("-r", "--spawn-rate", type=int, default=10, help="Taxa de spawn de usuários por segundo")
    parser.add_argument("--host", type=str, default="http://localhost:8000", help="Host alvo da API")
    args = parser.parse_args()
    run_load_test(users=args.users, spawn_rate=args.spawn_rate, host=args.host) 