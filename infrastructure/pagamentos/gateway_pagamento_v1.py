from typing import Dict, List, Optional, Any
"""
Gateway de pagamento (v1)
- Integração com Stripe/PayPal
- Retries com backoff exponencial
- Fallback para fila de compensação
- Logging estruturado
"""
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError

logger = logging.getLogger("pagamentos")

class PagamentoGatewayV1:
    """
    Gateway para integração de pagamentos com robustez e logging.
    """
    def __init__(self, provider: str, api_key: str):
        self.provider = provider
        self.api_key = api_key

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def processar_pagamento(self, valor: float, moeda: str, dados_cliente: dict) -> dict:
        try:
            # Aqui seria chamada real ao SDK do Stripe/PayPal
            logger.info({
                "uuid": "auto-gerado",
                "provider": self.provider,
                "valor": valor,
                "moeda": moeda
            })
            # Simulação de resposta
            return {"status": "sucesso", "valor": valor, "moeda": moeda}
        except Exception as e:
            logger.error({
                "uuid": "auto-gerado",
                "provider": self.provider,
                "erro": str(e)
            })
            raise

    def processar_com_fallback(self, valor: float, moeda: str, dados_cliente: dict) -> dict:
        try:
            return self.processar_pagamento(valor, moeda, dados_cliente)
        except RetryError:
            logger.warning({
                "uuid": "auto-gerado",
                "provider": self.provider,
                "fallback": True
            })
            # Aqui seria enviada para fila de compensação
            return {"erro": "Falha no pagamento, fallback ativado."} 