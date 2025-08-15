"""
Calculador de Scores Processor - Refatoração de Complexidade Ciclomática
IMP-001: Separação de responsabilidades do IntegradorCaudaLonga

Tracing ID: IMP001_SCORES_001
Data: 2024-12-27
Versão: 1.0
Status: EM IMPLEMENTAÇÃO
"""

from typing import List, Dict, Any
from domain.models import Keyword
from shared.logger import logger
from datetime import datetime
import time

from .complexidade_semantica import ComplexidadeSemantica
from .score_competitivo import ScoreCompetitivo
from .score_composto_inteligente import ScoreCompostoInteligente

class CalculadorScoresProcessor:
    """
    Responsável por calcular scores de keywords.
    
    Responsabilidades:
    - Calcular complexidade semântica
    - Calcular score competitivo
    - Calcular score composto inteligente
    - Registrar métricas de cálculo
    - Tratar erros de processamento
    """
    
    def __init__(self):
        """Inicializa o processador de cálculo de scores."""
        self.complexidade = ComplexidadeSemantica()
        self.score_competitivo = ScoreCompetitivo()
        self.score_composto = ScoreCompostoInteligente()
        self.tempo_calculo = 0.0
    
    def processar(self, keywords: List[Keyword]) -> List[Keyword]:
        """
        Processa cálculo de scores das keywords.
        
        Args:
            keywords: Lista de keywords a processar
            
        Returns:
            Lista de keywords com scores calculados
        """
        tempo_inicio = time.time()
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "iniciando_calculo_scores",
            "status": "info",
            "source": "CalculadorScoresProcessor.processar",
            "details": {
                "total_keywords": len(keywords)
            }
        })
        
        try:
            # 1. Calcular complexidade semântica
            keywords_complexidade = self._calcular_complexidade(keywords)
            
            # 2. Calcular score competitivo
            keywords_competitivas = self._calcular_score_competitivo(keywords_complexidade)
            
            # 3. Calcular score composto
            keywords_scores = self._calcular_score_composto(keywords_competitivas)
            
            # Registrar tempo
            self.tempo_calculo = time.time() - tempo_inicio
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "calculo_scores_concluido",
                "status": "success",
                "source": "CalculadorScoresProcessor.processar",
                "details": {
                    "keywords_processadas": len(keywords_scores),
                    "tempo_calculo": self.tempo_calculo
                }
            })
            
            return keywords_scores
            
        except Exception as e:
            self.tempo_calculo = time.time() - tempo_inicio
            
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_calculo_scores",
                "status": "error",
                "source": "CalculadorScoresProcessor.processar",
                "details": {
                    "erro": str(e),
                    "tempo_calculo": self.tempo_calculo
                }
            })
            
            # Retornar keywords originais em caso de erro
            return keywords
    
    def _calcular_complexidade(self, keywords: List[Keyword]) -> List[Keyword]:
        """Calcula complexidade semântica das keywords."""
        try:
            keywords_complexidade = []
            
            for kw in keywords:
                try:
                    # Calcular complexidade
                    complexidade = self.complexidade.calcular_complexidade(kw.termo)
                    
                    # Armazenar em atributo dinâmico
                    if not hasattr(kw, 'complexidade_semantica'):
                        kw.complexidade_semantica = complexidade
                    
                    keywords_complexidade.append(kw)
                    
                except Exception as e:
                    logger.warning({
                        "timestamp": datetime.utcnow().isoformat(),
                        "event": "erro_calculo_complexidade_individual",
                        "status": "warning",
                        "source": "CalculadorScoresProcessor._calcular_complexidade",
                        "details": {
                            "keyword": kw.termo,
                            "erro": str(e)
                        }
                    })
                    keywords_complexidade.append(kw)
            
            return keywords_complexidade
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_calculo_complexidade",
                "status": "error",
                "source": "CalculadorScoresProcessor._calcular_complexidade",
                "details": {"erro": str(e)}
            })
            return keywords
    
    def _calcular_score_competitivo(self, keywords: List[Keyword]) -> List[Keyword]:
        """Calcula score competitivo das keywords."""
        try:
            keywords_competitivas = []
            
            for kw in keywords:
                try:
                    # Calcular score competitivo
                    score_comp = self.score_competitivo.calcular_score_competitivo(
                        kw.termo,
                        kw.volume_busca,
                        kw.cpc,
                        kw.concorrencia
                    )
                    
                    # Armazenar em atributo dinâmico
                    if not hasattr(kw, 'score_competitivo'):
                        kw.score_competitivo = score_comp
                    
                    keywords_competitivas.append(kw)
                    
                except Exception as e:
                    logger.warning({
                        "timestamp": datetime.utcnow().isoformat(),
                        "event": "erro_calculo_competitivo_individual",
                        "status": "warning",
                        "source": "CalculadorScoresProcessor._calcular_score_competitivo",
                        "details": {
                            "keyword": kw.termo,
                            "erro": str(e)
                        }
                    })
                    keywords_competitivas.append(kw)
            
            return keywords_competitivas
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_calculo_competitivo",
                "status": "error",
                "source": "CalculadorScoresProcessor._calcular_score_competitivo",
                "details": {"erro": str(e)}
            })
            return keywords
    
    def _calcular_score_composto(self, keywords: List[Keyword]) -> List[Keyword]:
        """Calcula score composto inteligente das keywords."""
        try:
            keywords_scores = []
            
            for kw in keywords:
                try:
                    # Preparar dados para score composto
                    dados_keyword = {
                        "termo": kw.termo,
                        "volume_busca": kw.volume_busca,
                        "cpc": kw.cpc,
                        "concorrencia": kw.concorrencia,
                        "intencao": kw.intencao.value,
                        "complexidade": getattr(kw, 'complexidade_semantica', 0.0),
                        "score_competitivo": getattr(kw, 'score_competitivo', 0.0)
                    }
                    
                    # Calcular score composto
                    score_composto = self.score_composto.calcular_score_composto(dados_keyword)
                    
                    # Atualizar score principal da keyword
                    kw.score = score_composto.get("score_final", 0.0)
                    kw.justificativa = score_composto.get("justificativa", "")
                    
                    keywords_scores.append(kw)
                    
                except Exception as e:
                    logger.warning({
                        "timestamp": datetime.utcnow().isoformat(),
                        "event": "erro_calculo_composto_individual",
                        "status": "warning",
                        "source": "CalculadorScoresProcessor._calcular_score_composto",
                        "details": {
                            "keyword": kw.termo,
                            "erro": str(e)
                        }
                    })
                    keywords_scores.append(kw)
            
            return keywords_scores
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_calculo_composto",
                "status": "error",
                "source": "CalculadorScoresProcessor._calcular_score_composto",
                "details": {"erro": str(e)}
            })
            return keywords
    
    def obter_tempo_calculo(self) -> float:
        """Obtém tempo de cálculo de scores."""
        return self.tempo_calculo 