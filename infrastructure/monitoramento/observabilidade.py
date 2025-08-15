import logging
import uuid
from prometheus_client import Counter, Histogram
from typing import Dict, List, Optional, Any

# Métricas Prometheus
REQUEST_COUNT = Counter('app_request_count', 'Total de requisições', ['endpoint', 'status'])
REQUEST_FAILURES = Counter('app_request_failures', 'Total de falhas', ['endpoint'])
REQUEST_LATENCY = Histogram('app_request_latency_seconds', 'Latência das requisições', ['endpoint'])

def log_structured(message: str, extra: dict = None, level: str = 'info'):
    """Log estruturado com suporte a campos extras."""
    if extra is None:
        extra = {}
    log_msg = {'msg': message, **extra}
    getattr(logging, level)(log_msg)

def generate_trace_uuid() -> str:
    """Gera UUID de rastreio para requisições."""
    return str(uuid.uuid4()) 