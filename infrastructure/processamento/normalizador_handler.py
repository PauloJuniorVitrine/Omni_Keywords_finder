"""
Handler de normalização de palavras-chave para o pipeline de processamento.
Responsável por padronizar termos, remover duplicatas e aplicar regras de case/acentuação.
"""
from typing import List, Set
from domain.models import Keyword
import re
import unicodedata
from opentelemetry import trace, metrics
from shared.logger import logger

tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

class NormalizadorHandler:
    """
    Handler para normalização de palavras-chave.
    Remove duplicatas, aplica lower/strip, remove acentos se configurado.
    """
    def __init__(self, remover_acentos: bool = False, case_sensitive: bool = False):
        self.remover_acentos = remover_acentos
        self.case_sensitive = case_sensitive

    def handle(self, keywords: List[Keyword], contexto: dict) -> List[Keyword]:
        """
        Normaliza lista de keywords, removendo duplicatas e aplicando regras de formatação.
        """
        with tracer.start_as_current_span("normalizacao_keywords") as span:
            termos_vistos: Set[str] = set()
            keywords_normalizadas: List[Keyword] = []
            for kw in keywords:
                if not kw.termo:
                    continue
                termo_norm = kw.termo.strip()
                termo_norm = re.sub(r'\string_data+', ' ', termo_norm)
                if not self.case_sensitive:
                    termo_norm = termo_norm.lower()
                if self.remover_acentos:
                    termo_norm = unicodedata.normalize('NFKD', termo_norm).encode('ASCII', 'ignore').decode('ASCII')
                if not termo_norm:
                    continue
                if termo_norm not in termos_vistos:
                    termos_vistos.add(termo_norm)
                    nova_kw = Keyword(
                        termo=termo_norm,
                        volume_busca=max(0, kw.volume_busca),
                        cpc=max(0, kw.cpc),
                        concorrencia=max(0, min(1, kw.concorrencia)),
                        intencao=kw.intencao,
                        score=kw.score,
                        justificativa=kw.justificativa,
                        fonte=kw.fonte,
                        data_coleta=kw.data_coleta
                    )
                    keywords_normalizadas.append(nova_kw)
            span.set_attribute("total_normalizadas", len(keywords_normalizadas))
            meter.create_counter("normalizacao_keywords").add(len(keywords_normalizadas))
            logger.info({
                "event": "normalizacao_keywords",
                "status": "audit",
                "details": {"total": len(keywords), "unicos": len(keywords_normalizadas)}
            })
            return keywords_normalizadas

def normalizar_keywords(*args, **kwargs):
    """Normaliza lista de palavras-chave (a ser implementado)."""
    pass 