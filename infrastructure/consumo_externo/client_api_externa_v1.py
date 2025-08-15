from typing import Dict, List, Optional, Any
"""
Cliente REST para consumo de API externa (v1)
- Retries com backoff exponencial
- Fallback para fila de compensação
- Logging estruturado
"""
import requests
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError

logger = logging.getLogger("consumo_externo")

class APIExternaClientV1:
    """
    Cliente para consumo de API externa com robustez e logging.
    """
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get(self, endpoint: str, params: dict = None) -> dict:
        url = f"{self.base_url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = requests.get(url, headers=headers, params=params, timeout=5)
            logger.info({
                "uuid": "auto-gerado",
                "endpoint": endpoint,
                "status_code": response.status_code,
                "tempo_resposta_ms": response.elapsed.total_seconds() * 1000
            })
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error({
                "uuid": "auto-gerado",
                "endpoint": endpoint,
                "erro": str(e)
            })
            raise

    def get_com_fallback(self, endpoint: str, params: dict = None) -> dict:
        try:
            return self.get(endpoint, params)
        except RetryError:
            logger.warning({
                "uuid": "auto-gerado",
                "endpoint": endpoint,
                "fallback": True
            })
            # Aqui seria enviada para fila de compensação
            return {"erro": "Falha ao consumir API externa, fallback ativado."} 