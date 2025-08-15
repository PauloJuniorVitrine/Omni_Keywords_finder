"""
Módulo: auditoria_v1
Logging de auditoria para ações críticas do sistema.
"""
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

AUDIT_LOG_PATH = 'logs/auditoria.log'

def registrar_log(tipo_operacao: str, entidade: str, usuario: str, detalhes: str, id_referencia: Optional[str] = None):
    """
    Registra log de auditoria em JSON.
    """
    log = {
        'tipo_operacao': tipo_operacao,
        'entidade': entidade,
        'id_referencia': id_referencia,
        'usuario': usuario,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'detalhes': detalhes
    }
    os.makedirs(os.path.dirname(AUDIT_LOG_PATH), exist_ok=True)
    with open(AUDIT_LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log, ensure_ascii=False) + '\n')


def consultar_logs(tipo_operacao: Optional[str] = None, entidade: Optional[str] = None, usuario: Optional[str] = None, data_inicio: Optional[str] = None, data_fim: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Consulta logs de auditoria por filtros.
    """
    if not os.path.exists(AUDIT_LOG_PATH):
        return []
    resultados = []
    with open(AUDIT_LOG_PATH, 'r', encoding='utf-8') as f:
        for linha in f:
            log = json.loads(linha)
            if tipo_operacao and log['tipo_operacao'] != tipo_operacao:
                continue
            if entidade and log['entidade'] != entidade:
                continue
            if usuario and log['usuario'] != usuario:
                continue
            if data_inicio and log['timestamp'] < data_inicio:
                continue
            if data_fim and log['timestamp'] > data_fim:
                continue
            resultados.append(log)
    return resultados 