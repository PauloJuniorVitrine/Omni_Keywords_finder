"""
Aplicador ML Processor - Refatoração de Complexidade Ciclomática
IMP-001: Separação de responsabilidades do IntegradorCaudaLonga

Tracing ID: IMP001_ML_001
Data: 2024-12-27
Versão: 1.0
Status: EM IMPLEMENTAÇÃO
"""

from typing import List, Dict, Any
from domain.models import Keyword
from shared.logger import logger
from datetime import datetime
import time

from ..ml.ajuste_automatico_cauda_longa import AjusteAutomaticoCaudaLonga

class AplicadorMLProcessor:
    """
    Responsável por aplicar ajustes de ML nas keywords.
    
    Responsabilidades:
    - Aplicar ajustes automáticos de ML
    - Otimizar scores baseado em aprendizado
    - Registrar métricas de ML
    - Tratar erros de processamento
    """
    
    def __init__(self):
        """Inicializa o processador de ML."""
        self.ml_ajuste = AjusteAutomaticoCaudaLonga()
        self.tempo_ml = 0.0
    
    def processar(self, keywords: List[Keyword]) -> List[Keyword]:
        """
        Processa ajustes de ML nas keywords.
        
        Args:
            keywords: Lista de keywords a processar
            
        Returns:
            Lista de keywords com ajustes de ML aplicados
        """
        tempo_inicio = time.time()
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "iniciando_ajuste_ml",
            "status": "info",
            "source": "AplicadorMLProcessor.processar",
            "details": {
                "total_keywords": len(keywords)
            }
        })
        
        try:
            keywords_ml = []
            
            for kw in keywords:
                try:
                    # Aplicar ajuste de ML
                    ajuste_ml = self.ml_ajuste.aplicar_ajuste_automatico(
                        kw.termo,
                        kw.volume_busca,
                        kw.cpc,
                        kw.concorrencia,
                        kw.score
                    )
                    
                    # Aplicar ajustes se disponíveis
                    if ajuste_ml.get("ajuste_aplicado", False):
                        # Armazenar ajustes em atributo dinâmico
                        if not hasattr(kw, 'ajuste_ml'):
                            kw.ajuste_ml = {}
                        
                        kw.ajuste_ml.update({
                            "ajuste_aplicado": True,
                            "score_original": kw.score,
                            "score_ajustado": ajuste_ml.get("score_ajustado", kw.score),
                            "fator_ajuste": ajuste_ml.get("fator_ajuste", 1.0),
                            "justificativa_ajuste": ajuste_ml.get("justificativa", "")
                        })
                        
                        # Atualizar score se ajuste foi aplicado
                        kw.score = ajuste_ml.get("score_ajustado", kw.score)
                    
                    keywords_ml.append(kw)
                    
                except Exception as e:
                    logger.warning({
                        "timestamp": datetime.utcnow().isoformat(),
                        "event": "erro_ajuste_ml_individual",
                        "status": "warning",
                        "source": "AplicadorMLProcessor.processar",
                        "details": {
                            "keyword": kw.termo,
                            "erro": str(e)
                        }
                    })
                    keywords_ml.append(kw)
            
            # Registrar tempo
            self.tempo_ml = time.time() - tempo_inicio
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "ajuste_ml_concluido",
                "status": "success",
                "source": "AplicadorMLProcessor.processar",
                "details": {
                    "keywords_processadas": len(keywords_ml),
                    "tempo_ml": self.tempo_ml
                }
            })
            
            return keywords_ml
            
        except Exception as e:
            self.tempo_ml = time.time() - tempo_inicio
            
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_ajuste_ml",
                "status": "error",
                "source": "AplicadorMLProcessor.processar",
                "details": {
                    "erro": str(e),
                    "tempo_ml": self.tempo_ml
                }
            })
            
            # Retornar keywords originais em caso de erro
            return keywords
    
    def obter_tempo_ml(self) -> float:
        """Obtém tempo de processamento de ML."""
        return self.tempo_ml 