"""
Handler de machine learning adaptativo para o pipeline de processamento.
Responsável por sugerir, filtrar e treinar modelos de ML para keywords.
"""
from typing import List, Optional
from domain.models import Keyword
from infrastructure.ml.ml_adaptativo import MLAdaptativo
from opentelemetry import trace, metrics

tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

class MLHandler:
    def __init__(self, ml_adaptativo: Optional[MLAdaptativo] = None):
        self.ml_adaptativo = ml_adaptativo

    def handle(self, keywords: List[Keyword], contexto: dict) -> List[Keyword]:
        with tracer.start_as_current_span("ml_keywords") as span:
            if not self.ml_adaptativo or not keywords:
                return keywords
            keywords_dict = [key.to_dict() for key in keywords]
            historico_feedback = contexto.get("historico_feedback")
            if historico_feedback is not None:
                self.ml_adaptativo.treinar_incremental(historico_feedback)
            sugeridos = self.ml_adaptativo.sugerir(keywords_dict)
            filtrados = self.ml_adaptativo.bloquear_repetidos(sugeridos, historico_feedback or [])
            keywords_final = [Keyword(**key) for key in filtrados]
            span.set_attribute("total_ml", len(keywords_final))
            meter.create_counter("ml_keywords").add(len(keywords_final))
            # Auditoria pode ser chamada aqui se necessário
            return keywords_final 