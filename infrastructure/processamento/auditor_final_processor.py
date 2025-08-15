"""
Auditor Final Processor - Refatoração de Complexidade Ciclomática
IMP-001: Separação de responsabilidades do IntegradorCaudaLonga

Tracing ID: IMP001_AUDITOR_001
Data: 2024-12-27
Versão: 1.0
Status: EM IMPLEMENTAÇÃO
"""

from typing import List, Dict, Any
from domain.models import Keyword
from shared.logger import logger
from datetime import datetime
import time

from ..audit.auditoria_qualidade_cauda_longa import AuditoriaQualidadeCaudaLonga

class AuditorFinalProcessor:
    """
    Responsável por aplicar auditoria final nas keywords.
    
    Responsabilidades:
    - Aplicar auditoria de qualidade final
    - Validar consistência dos dados
    - Registrar métricas de auditoria
    - Tratar erros de processamento
    """
    
    def __init__(self):
        """Inicializa o processador de auditoria final."""
        self.auditoria = AuditoriaQualidadeCaudaLonga()
        self.tempo_auditoria = 0.0
    
    def processar(self, keywords: List[Keyword]) -> List[Keyword]:
        """
        Processa auditoria final das keywords.
        
        Args:
            keywords: Lista de keywords a auditar
            
        Returns:
            Lista de keywords auditadas
        """
        tempo_inicio = time.time()
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "iniciando_auditoria_final",
            "status": "info",
            "source": "AuditorFinalProcessor.processar",
            "details": {
                "total_keywords": len(keywords)
            }
        })
        
        try:
            keywords_auditadas = []
            
            for kw in keywords:
                try:
                    # Aplicar auditoria de qualidade
                    resultado_auditoria = self.auditoria.auditar_keyword(
                        kw.termo,
                        kw.volume_busca,
                        kw.cpc,
                        kw.concorrencia,
                        kw.score
                    )
                    
                    # Armazenar resultado da auditoria
                    if not hasattr(kw, 'auditoria_final'):
                        kw.auditoria_final = {}
                    
                    kw.auditoria_final.update({
                        "qualidade_geral": resultado_auditoria.get("qualidade_geral", 0.0),
                        "score_auditoria": resultado_auditoria.get("score_auditoria", 0.0),
                        "problemas_detectados": resultado_auditoria.get("problemas_detectados", []),
                        "recomendacoes": resultado_auditoria.get("recomendacoes", []),
                        "status_auditoria": resultado_auditoria.get("status", "aprovada")
                    })
                    
                    keywords_auditadas.append(kw)
                    
                except Exception as e:
                    logger.warning({
                        "timestamp": datetime.utcnow().isoformat(),
                        "event": "erro_auditoria_individual",
                        "status": "warning",
                        "source": "AuditorFinalProcessor.processar",
                        "details": {
                            "keyword": kw.termo,
                            "erro": str(e)
                        }
                    })
                    keywords_auditadas.append(kw)
            
            # Registrar tempo
            self.tempo_auditoria = time.time() - tempo_inicio
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "auditoria_final_concluida",
                "status": "success",
                "source": "AuditorFinalProcessor.processar",
                "details": {
                    "keywords_auditadas": len(keywords_auditadas),
                    "tempo_auditoria": self.tempo_auditoria
                }
            })
            
            return keywords_auditadas
            
        except Exception as e:
            self.tempo_auditoria = time.time() - tempo_inicio
            
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_auditoria_final",
                "status": "error",
                "source": "AuditorFinalProcessor.processar",
                "details": {
                    "erro": str(e),
                    "tempo_auditoria": self.tempo_auditoria
                }
            })
            
            # Retornar keywords originais em caso de erro
            return keywords
    
    def obter_tempo_auditoria(self) -> float:
        """Obtém tempo de auditoria final."""
        return self.tempo_auditoria 