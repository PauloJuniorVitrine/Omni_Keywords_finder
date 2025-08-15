"""
Módulo: compliance_report_v1
Geração automática de relatório de conformidade do sistema.
"""
import json
from datetime import datetime
from typing import Dict, Any, List
from backend.app.services.auditoria_v1 import consultar_logs

COMPLIANCE_REPORT_PATH = 'logs/compliance_report.json'

def gerar_relatorio_conformidade(metricas: Dict[str, Any], cobertura: Dict[str, Any], falhas: List[str]) -> str:
    """
    Gera relatório de conformidade (JSON) com status, métricas, logs, falhas, cobertura.
    """
    logs = consultar_logs()
    relatorio = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'status': 'ok' if not falhas else 'falha',
        'metricas': metricas,
        'cobertura': cobertura,
        'falhas': falhas,
        'logs': logs[-50:]  # últimos 50 logs
    }
    with open(COMPLIANCE_REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)
    return COMPLIANCE_REPORT_PATH 