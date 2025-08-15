"""
Handler de limpeza de palavras-chave para o pipeline de processamento.
Responsável por filtrar e limpar keywords inválidas ou inconsistentes.
"""
from typing import List
from domain.models import Keyword
from opentelemetry import trace, metrics
from shared.logger import logger
from datetime import datetime
from infrastructure.processamento.validador_keywords import ValidadorKeywords

tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

class LimpezaHandler:
    """
    Handler para limpeza de palavras-chave.
    Remove keywords inválidas conforme regras do validador.
    """
    def handle(self, keywords: List[Keyword], contexto: dict) -> List[Keyword]:
        """
        Filtra keywords inválidas usando o validador configurado.
        """
        with tracer.start_as_current_span("limpeza_keywords") as span:
            keywords_limpas = []
            validador: ValidadorKeywords = contexto.get("validador") or ValidadorKeywords()
            for kw in keywords:
                try:
                    valido, _ = validador.validar_keyword(kw)
                    if valido and (kw.volume_busca >= 0 and kw.cpc >= 0 and 0 <= kw.concorrencia <= 1):
                        keywords_limpas.append(kw)
                except Exception as e:
                    logger.error({
                        "timestamp": datetime.utcnow().isoformat(),
                        "event": "erro_limpeza_keyword",
                        "status": "error",
                        "source": "limpeza_handler",
                        "details": {"termo": kw.termo, "erro": str(e)}
                    })
            span.set_attribute("total_limpas", len(keywords_limpas))
            meter.create_counter("limpeza_keywords").add(len(keywords_limpas))
            logger.info({
                "event": "limpeza_keywords",
                "status": "audit",
                "details": {"antes": len(keywords), "depois": len(keywords_limpas)}
            })
            return keywords_limpas 