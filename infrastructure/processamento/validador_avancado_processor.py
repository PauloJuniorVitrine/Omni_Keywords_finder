"""
Validador Avançado Processor - Refatoração de Complexidade Ciclomática
IMP-001: Separação de responsabilidades do IntegradorCaudaLonga

Tracing ID: IMP001_VALIDADOR_001
Data: 2024-12-27
Versão: 1.0
Status: EM IMPLEMENTAÇÃO
"""

from typing import List, Dict, Any
from domain.models import Keyword
from shared.logger import logger
from datetime import datetime
import time

from .validador_cauda_longa_avancado import ValidadorCaudaLongaAvancado

class ValidadorAvancadoProcessor:
    """
    Responsável por aplicar validação avançada nas keywords.
    
    Responsabilidades:
    - Aplicar validação avançada de cauda longa
    - Filtrar keywords baseado em critérios
    - Registrar métricas de validação
    - Tratar erros de processamento
    """
    
    def __init__(self):
        """Inicializa o processador de validação avançada."""
        self.validador = ValidadorCaudaLongaAvancado()
        self.tempo_validacao = 0.0
    
    def processar(
        self, 
        keywords: List[Keyword], 
        config: Dict[str, Any]
    ) -> List[Keyword]:
        """
        Processa validação avançada das keywords.
        
        Args:
            keywords: Lista de keywords a validar
            config: Configuração específica do nicho
            
        Returns:
            Lista de keywords validadas
        """
        tempo_inicio = time.time()
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "iniciando_validacao_avancada",
            "status": "info",
            "source": "ValidadorAvancadoProcessor.processar",
            "details": {
                "total_keywords": len(keywords),
                "config_keys": list(config.keys())
            }
        })
        
        try:
            keywords_validadas = []
            
            for kw in keywords:
                try:
                    # Aplicar validação avançada
                    resultado_validacao = self.validador.validar_keyword_avancada(
                        kw.termo,
                        kw.volume_busca,
                        kw.cpc,
                        kw.concorrencia,
                        kw.score,
                        config
                    )
                    
                    # Verificar se keyword foi aprovada
                    if resultado_validacao.get("aprovada", False):
                        # Armazenar detalhes da validação
                        if not hasattr(kw, 'validacao_avancada'):
                            kw.validacao_avancada = {}
                        
                        kw.validacao_avancada.update({
                            "aprovada": True,
                            "score_validacao": resultado_validacao.get("score_validacao", 0.0),
                            "criticos_atendidos": resultado_validacao.get("criticos_atendidos", []),
                            "justificativa": resultado_validacao.get("justificativa", "")
                        })
                        
                        keywords_validadas.append(kw)
                    else:
                        logger.info({
                            "timestamp": datetime.utcnow().isoformat(),
                            "event": "keyword_rejeitada_validacao",
                            "status": "info",
                            "source": "ValidadorAvancadoProcessor.processar",
                            "details": {
                                "keyword": kw.termo,
                                "motivo": resultado_validacao.get("justificativa", "Critérios não atendidos")
                            }
                        })
                    
                except Exception as e:
                    logger.warning({
                        "timestamp": datetime.utcnow().isoformat(),
                        "event": "erro_validacao_individual",
                        "status": "warning",
                        "source": "ValidadorAvancadoProcessor.processar",
                        "details": {
                            "keyword": kw.termo,
                            "erro": str(e)
                        }
                    })
                    # Em caso de erro, manter keyword para análise posterior
                    keywords_validadas.append(kw)
            
            # Registrar tempo
            self.tempo_validacao = time.time() - tempo_inicio
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "validacao_avancada_concluida",
                "status": "success",
                "source": "ValidadorAvancadoProcessor.processar",
                "details": {
                    "keywords_aprovadas": len(keywords_validadas),
                    "keywords_rejeitadas": len(keywords) - len(keywords_validadas),
                    "tempo_validacao": self.tempo_validacao
                }
            })
            
            return keywords_validadas
            
        except Exception as e:
            self.tempo_validacao = time.time() - tempo_inicio
            
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_validacao_avancada",
                "status": "error",
                "source": "ValidadorAvancadoProcessor.processar",
                "details": {
                    "erro": str(e),
                    "tempo_validacao": self.tempo_validacao
                }
            })
            
            # Retornar keywords originais em caso de erro
            return keywords
    
    def obter_tempo_validacao(self) -> float:
        """Obtém tempo de validação avançada."""
        return self.tempo_validacao 