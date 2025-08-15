"""
Handler de validação de palavras-chave para o pipeline de processamento.
Responsável por validar keywords segundo regras e versionamento.
"""
from typing import List, Optional
from domain.models import Keyword
from infrastructure.processamento.validador_keywords import ValidadorKeywords
from opentelemetry import trace, metrics
from shared.logger import logger
import uuid
from datetime import datetime

tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

class ValidacaoHandler:
    """
    Handler para validação de palavras-chave.
    Aplica regras de negócio e filtros avançados.
    """
    def __init__(self, validador: ValidadorKeywords, regras: Optional[dict] = None):
        self.validador = validador
        self.regras = regras or {}
        self.versao_regras = None

    def handle(self, keywords: List[Keyword], contexto: dict) -> List[Keyword]:
        """
        Valida lista de keywords usando o validador e regras configuradas.
        """
        with tracer.start_as_current_span("validacao_keywords") as span:
            keywords_validas, relatorio = self.validador.validar_lista(keywords, relatorio=True)
            span.set_attribute("total_validas", len(keywords_validas))
            meter.create_counter("validacao_keywords").add(len(keywords_validas))
            logger.info({
                "event": "validacao_keywords",
                "status": "audit",
                "details": {"total": len(keywords), "validas": len(keywords_validas), "versao_regras": self.versao_regras, "relatorio": relatorio}
            })
            return keywords_validas 