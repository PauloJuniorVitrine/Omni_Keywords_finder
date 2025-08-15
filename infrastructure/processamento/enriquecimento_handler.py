"""
Handler de enriquecimento de palavras-chave para o pipeline de processamento.
Responsável por calcular score e justificativa para cada keyword, aplicando pesos e regras do contexto.
"""
from typing import List
from domain.models import Keyword
from opentelemetry import trace, metrics
from shared.logger import logger

tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

class EnriquecimentoHandler:
    """
    Handler para enriquecimento de palavras-chave.
    Calcula score e justificativa para cada keyword.
    """
    def handle(self, keywords: List[Keyword], contexto: dict) -> List[Keyword]:
        """
        Enriquecer keywords com score e justificativa, aplicando pesos do contexto.
        """
        with tracer.start_as_current_span("enriquecimento_keywords") as span:
            erros = []
            keywords_enriquecidas = []
            for kw in keywords:
                try:
                    kw.score = kw.calcular_score(contexto.get("pesos", {}))
                    kw.justificativa = f"Score calculado com pesos: {contexto.get('pesos', {})}"
                    keywords_enriquecidas.append(kw)
                except Exception as e:
                    logger.error({
                        "event": "erro_enriquecimento",
                        "status": "error",
                        "source": "enriquecimento_handler",
                        "details": {"termo": kw.termo, "erro": str(e)}
                    })
                    erros.append({"termo": kw.termo, "erro": str(e)})
            span.set_attribute("total_enriquecidas", len(keywords_enriquecidas))
            meter.create_counter("enriquecimento_keywords").add(len(keywords_enriquecidas))
            logger.info({
                "event": "enriquecimento_keywords",
                "status": "audit",
                "details": {"total": len(keywords), "enriquecidas": len(keywords_enriquecidas), "erros": erros}
            })
            return keywords_enriquecidas

def enriquecer_keywords(*args, **kwargs):
    """Enriquece lista de palavras-chave com dados externos (a ser implementado)."""
    pass 