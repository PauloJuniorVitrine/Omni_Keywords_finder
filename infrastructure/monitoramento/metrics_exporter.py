from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from flask import Response, Blueprint
import time
from typing import Dict, List, Optional, Any

metrics_bp = Blueprint('metrics', __name__)

# Métricas customizadas
KEYWORDS_PROCESSADAS = Counter('keywords_processadas_total', 'Total de keywords processadas')
EXPORTACOES_REALIZADAS = Counter('exportacoes_realizadas_total', 'Total de exportações de keywords')
TEMPO_PROCESSAMENTO = Histogram('tempo_processamento_keywords_segundos', 'Tempo de processamento de keywords')
ERROS_PROCESSAMENTO = Counter('erros_processamento_total', 'Total de erros no processamento de keywords')

@metrics_bp.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

# Decorators utilitários para instrumentação

def track_keywords_processadas(func):
    def wrapper(*args, **kwargs):
        with TEMPO_PROCESSAMENTO.time():
            try:
                result = func(*args, **kwargs)
                if isinstance(result, list):
                    KEYWORDS_PROCESSADAS.inc(len(result))
                return result
            except Exception:
                ERROS_PROCESSAMENTO.inc()
                raise
    return wrapper

def track_exportacao(func):
    def wrapper(*args, **kwargs):
        EXPORTACOES_REALIZADAS.inc()
        return func(*args, **kwargs)
    return wrapper 