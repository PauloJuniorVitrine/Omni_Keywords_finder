"""
Sistema de Score Composto Inteligente para Ordenação - Omni Keywords Finder
=======================================================================

Este módulo implementa um sistema de score composto para ordenação inteligente
de keywords, substituindo a ordenação baseada apenas em volume de busca.

Fórmula: Score = (Volume * 0.3) + (CPC * 0.25) + (Intenção * 0.2) + (1-Concorrência * 0.15) + (Tendência * 0.1)

Autor: Paulo Júnior
Data: 2024-12-20
Tracing ID: LONGTAIL-016
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from domain.models import Keyword, IntencaoBusca
from shared.logger import logger
from shared.config import ProcessingConfig

@dataclass
class ScoreConfig:
    """Configuração dos pesos para cálculo do score composto."""
    peso_volume: float = 0.30
    peso_cpc: float = 0.25
    peso_intencao: float = 0.20
    peso_concorrencia: float = 0.15
    peso_tendencia: float = 0.10
    
    def __post_init__(self):
        """Valida se os pesos somam 1.0."""
        total = sum([
            self.peso_volume,
            self.peso_cpc,
            self.peso_intencao,
            self.peso_concorrencia,
            self.peso_tendencia
        ])
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Pesos devem somar 1.0, atual: {total}")

@dataclass
class ScoreResult:
    """Resultado do cálculo de score composto."""
    keyword: Keyword
    score_final: float
    score_volume: float
    score_cpc: float
    score_intencao: float
    score_concorrencia: float
    score_tendencia: float
    ranking: int
    justificativa: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class ScoreCompostoOrdenacao:
    """
    Sistema de score composto inteligente para ordenação de keywords.
    
    Características:
    - Score baseado em múltiplos fatores
    - Normalização inteligente de valores
    - Configuração flexível de pesos
    - Logs detalhados de cálculo
    - Validação de qualidade
    """
    
    def __init__(
        self,
        config: Optional[ScoreConfig] = None,
        enable_trend_analysis: bool = True,
        enable_logging: bool = True
    ):
        """
        Inicializa o sistema de score composto.
        
        Args:
            config: Configuração dos pesos (opcional)
            enable_trend_analysis: Se True, habilita análise de tendências
            enable_logging: Se True, habilita logs detalhados
        """
        self.config = config or ScoreConfig()
        self.enable_trend_analysis = enable_trend_analysis
        self.enable_logging = enable_logging
        
        # Mapeamento de intenções para scores
        self.intencao_scores = {
            IntencaoBusca.TRANSACIONAL: 1.0,    # Mais valiosa
            IntencaoBusca.COMERCIAL: 0.8,
            IntencaoBusca.COMPARACAO: 0.7,
            IntencaoBusca.INFORMACIONAL: 0.6,
            IntencaoBusca.NAVEGACIONAL: 0.4     # Menos valiosa
        }
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "score_composto_inicializado",
            "status": "success",
            "source": "score_composto_ordenacao.__init__",
            "details": {
                "config": {
                    "peso_volume": self.config.peso_volume,
                    "peso_cpc": self.config.peso_cpc,
                    "peso_intencao": self.config.peso_intencao,
                    "peso_concorrencia": self.config.peso_concorrencia,
                    "peso_tendencia": self.config.peso_tendencia
                },
                "enable_trend_analysis": enable_trend_analysis
            }
        })
    
    def calcular_score_composto(
        self,
        keywords: List[Keyword],
        contexto_nicho: Optional[str] = None,
        periodo_tendencia: int = 30
    ) -> List[ScoreResult]:
        """
        Calcula score composto para lista de keywords.
        
        Args:
            keywords: Lista de keywords para análise
            contexto_nicho: Nicho específico para ajustes
            periodo_tendencia: Período em dias para análise de tendência
            
        Returns:
            Lista de ScoreResult ordenada por score (maior primeiro)
        """
        if not keywords:
            logger.warning({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "score_composto_keywords_vazia",
                "status": "warning",
                "source": "score_composto_ordenacao.calcular_score_composto",
                "details": {"total_keywords": 0}
            })
            return []
        
        # Normaliza valores para cálculo
        volumes = [key.volume_busca for key in keywords]
        cpcs = [key.cpc for key in keywords]
        concorrencias = [key.concorrencia for key in keywords]
        
        # Calcula scores individuais
        scores_volume = self._normalizar_volume(volumes)
        scores_cpc = self._normalizar_cpc(cpcs)
        scores_intencao = self._calcular_score_intencao(keywords)
        scores_concorrencia = self._calcular_score_concorrencia(concorrencias)
        scores_tendencia = self._calcular_score_tendencia(keywords, periodo_tendencia)
        
        # Calcula scores compostos
        resultados = []
        for index, keyword in enumerate(keywords):
            score_final = (
                scores_volume[index] * self.config.peso_volume +
                scores_cpc[index] * self.config.peso_cpc +
                scores_intencao[index] * self.config.peso_intencao +
                scores_concorrencia[index] * self.config.peso_concorrencia +
                scores_tendencia[index] * self.config.peso_tendencia
            )
            
            justificativa = self._gerar_justificativa(
                keyword, scores_volume[index], scores_cpc[index], scores_intencao[index],
                scores_concorrencia[index], scores_tendencia[index], score_final
            )
            
            resultado = ScoreResult(
                keyword=keyword,
                score_final=round(score_final, 4),
                score_volume=round(scores_volume[index], 4),
                score_cpc=round(scores_cpc[index], 4),
                score_intencao=round(scores_intencao[index], 4),
                score_concorrencia=round(scores_concorrencias[index], 4),
                score_tendencia=round(scores_tendencia[index], 4),
                ranking=0,  # Será definido após ordenação
                justificativa=justificativa
            )
            resultados.append(resultado)
        
        # Ordena por score final (maior primeiro)
        resultados.sort(key=lambda value: value.score_final, reverse=True)
        
        # Atualiza rankings
        for index, resultado in enumerate(resultados):
            resultado.ranking = index + 1
        
        # Log dos resultados
        if self.enable_logging:
            self._log_resultados(resultados, contexto_nicho)
        
        return resultados
    
    def _normalizar_volume(self, volumes: List[int]) -> List[float]:
        """Normaliza volumes de busca para score 0-1."""
        if not volumes:
            return []
        
        max_volume = max(volumes) if max(volumes) > 0 else 1
        return [value / max_volume for value in volumes]
    
    def _normalizar_cpc(self, cpcs: List[float]) -> List[float]:
        """Normaliza CPCs para score 0-1."""
        if not cpcs:
            return []
        
        max_cpc = max(cpcs) if max(cpcs) > 0 else 1
        return [c / max_cpc for c in cpcs]
    
    def _calcular_score_intencao(self, keywords: List[Keyword]) -> List[float]:
        """Calcula scores baseados na intenção de busca."""
        scores = []
        for keyword in keywords:
            score = self.intencao_scores.get(keyword.intencao, 0.5)
            scores.append(score)
        return scores
    
    def _calcular_score_concorrencia(self, concorrencias: List[float]) -> List[float]:
        """Calcula scores baseados na concorrência (inverso)."""
        if not concorrencias:
            return []
        
        # Inverte a concorrência: menor concorrência = maior score
        return [1.0 - c for c in concorrencias]
    
    def _calcular_score_tendencia(
        self,
        keywords: List[Keyword],
        periodo_dias: int
    ) -> List[float]:
        """
        Calcula scores baseados em tendências (simulado).
        
        Em implementação real, isso seria baseado em dados históricos
        de volume de busca ao longo do tempo.
        """
        if not self.enable_trend_analysis:
            return [0.5] * len(keywords)  # Score neutro
        
        # Simulação de análise de tendência
        # Em produção, isso seria baseado em dados reais do Google Trends
        scores = []
        for keyword in keywords:
            # Simula tendência baseada em características da keyword
            if len(keyword.termo.split()) > 3:  # Long-tail
                score = 0.8  # Tendência crescente
            elif keyword.volume_busca > 1000:
                score = 0.6  # Estável
            else:
                score = 0.4  # Tendência decrescente
            scores.append(score)
        
        return scores
    
    def _gerar_justificativa(
        self,
        keyword: Keyword,
        score_volume: float,
        score_cpc: float,
        score_intencao: float,
        score_concorrencia: float,
        score_tendencia: float,
        score_final: float
    ) -> str:
        """Gera justificativa detalhada do score."""
        fatores = []
        
        if score_volume > 0.7:
            fatores.append("alto volume de busca")
        elif score_volume < 0.3:
            fatores.append("baixo volume de busca")
        
        if score_cpc > 0.7:
            fatores.append("alto CPC")
        elif score_cpc < 0.3:
            fatores.append("baixo CPC")
        
        if score_intencao > 0.8:
            fatores.append("intenção transacional")
        elif score_intencao < 0.5:
            fatores.append("intenção informacional")
        
        if score_concorrencia > 0.7:
            fatores.append("baixa concorrência")
        elif score_concorrencia < 0.3:
            fatores.append("alta concorrência")
        
        if score_tendencia > 0.7:
            fatores.append("tendência crescente")
        elif score_tendencia < 0.3:
            fatores.append("tendência decrescente")
        
        if not fatores:
            fatores.append("características equilibradas")
        
        return f"Score {score_final:.3f} baseado em: {', '.join(fatores)}"
    
    def _log_resultados(
        self,
        resultados: List[ScoreResult],
        contexto_nicho: Optional[str]
    ) -> None:
        """Registra logs detalhados dos resultados."""
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "score_composto_calculado",
            "status": "success",
            "source": "score_composto_ordenacao._log_resultados",
            "details": {
                "total_keywords": len(resultados),
                "contexto_nicho": contexto_nicho,
                "top_5_scores": [
                    {
                        "termo": r.keyword.termo,
                        "score_final": r.score_final,
                        "ranking": r.ranking,
                        "justificativa": r.justificativa
                    }
                    for r in resultados[:5]
                ],
                "score_medio": round(np.mean([r.score_final for r in resultados]), 4),
                "score_desvio": round(np.std([r.score_final for r in resultados]), 4)
            }
        })
    
    def aplicar_ordenacao_inteligente(
        self,
        keywords: List[Keyword],
        contexto_nicho: Optional[str] = None
    ) -> List[Keyword]:
        """
        Aplica ordenação inteligente baseada no score composto.
        
        Args:
            keywords: Lista de keywords para ordenar
            contexto_nicho: Nicho específico para ajustes
            
        Returns:
            Lista de keywords ordenada por score composto
        """
        resultados = self.calcular_score_composto(keywords, contexto_nicho)
        
        # Atualiza ordem_no_cluster baseado no ranking
        for resultado in resultados:
            resultado.keyword.ordem_no_cluster = resultado.ranking - 1
            resultado.keyword.nome_artigo = f"Artigo{resultado.ranking}"
        
        # Retorna keywords ordenadas
        return [r.keyword for r in resultados]
    
    def validar_qualidade_ordenacao(
        self,
        resultados: List[ScoreResult]
    ) -> Dict[str, Any]:
        """
        Valida a qualidade da ordenação gerada.
        
        Args:
            resultados: Lista de ScoreResult
            
        Returns:
            Dicionário com métricas de qualidade
        """
        if not resultados:
            return {"status": "empty", "message": "Nenhum resultado para validar"}
        
        scores = [r.score_final for r in resultados]
        
        # Calcula métricas de qualidade
        qualidade = {
            "total_keywords": len(resultados),
            "score_medio": round(np.mean(scores), 4),
            "score_mediana": round(np.median(scores), 4),
            "score_desvio": round(np.std(scores), 4),
            "score_min": round(min(scores), 4),
            "score_max": round(max(scores), 4),
            "distribuicao": {
                "excelente": len([string_data for string_data in scores if string_data >= 0.8]),
                "bom": len([string_data for string_data in scores if 0.6 <= string_data < 0.8]),
                "regular": len([string_data for string_data in scores if 0.4 <= string_data < 0.6]),
                "ruim": len([string_data for string_data in scores if string_data < 0.4])
            },
            "ranking_consistencia": self._validar_consistencia_ranking(resultados)
        }
        
        # Determina status geral
        if qualidade["score_medio"] >= 0.7:
            qualidade["status"] = "excelente"
        elif qualidade["score_medio"] >= 0.5:
            qualidade["status"] = "bom"
        else:
            qualidade["status"] = "precisa_melhoria"
        
        return qualidade
    
    def _validar_consistencia_ranking(self, resultados: List[ScoreResult]) -> Dict[str, Any]:
        """Valida consistência do ranking gerado."""
        if len(resultados) < 2:
            return {"status": "insuficiente", "message": "Poucos itens para análise"}
        
        # Verifica se rankings estão sequenciais
        rankings = [r.ranking for r in resultados]
        rankings_esperados = list(range(1, len(resultados) + 1))
        
        if rankings == rankings_esperados:
            return {"status": "consistente", "message": "Ranking sequencial correto"}
        else:
            return {
                "status": "inconsistente",
                "message": "Ranking não sequencial",
                "rankings_atuais": rankings,
                "rankings_esperados": rankings_esperados
            }

# Função de conveniência para uso direto
def ordenar_keywords_inteligente(
    keywords: List[Keyword],
    contexto_nicho: Optional[str] = None,
    config: Optional[ScoreConfig] = None
) -> List[Keyword]:
    """
    Função de conveniência para ordenação inteligente de keywords.
    
    Args:
        keywords: Lista de keywords para ordenar
        contexto_nicho: Nicho específico para ajustes
        config: Configuração personalizada (opcional)
        
    Returns:
        Lista de keywords ordenada por score composto
    """
    ordenador = ScoreCompostoOrdenacao(config=config)
    return ordenador.aplicar_ordenacao_inteligente(keywords, contexto_nicho) 