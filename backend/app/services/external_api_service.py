import requests
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import pybreaker
from typing import Dict, List, Optional, Any

breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=30)

@breaker
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), retry=retry_if_exception_type(requests.RequestException))
def fetch_external_data(endpoint: str, token: str) -> dict:
    """Consome API externa com timeout, retries e circuit breaker."""
    headers = {'Authorization': f'Bearer {token}'}
    try:
        resp = requests.get(endpoint, headers=headers, timeout=5)
        resp.raise_for_status()
        logging.info(f'API externa OK: {endpoint} status={resp.status_code}')
        return resp.json()
    except Exception as e:
        logging.error(f'Erro API externa: {endpoint} erro={e}')
        raise 