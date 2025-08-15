"""
Sistema de Detecção Automática de Fase do Funil - Omni Keywords Finder
===================================================================

Este módulo implementa detecção automática da fase do funil mais adequada
para cada keyword, substituindo o mapeamento fixo 1:1 entre posição e fase.

Autor: Paulo Júnior
Data: 2024-12-20
Tracing ID: LONGTAIL-017
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from domain.models import Keyword, IntencaoBusca
from shared.logger import logger
from shared.config import ProcessingConfig, FUNNEL_STAGES

class FaseFunil(Enum):
    """Enumeração das fases do funil de conversão."""
    DESCOBERTA = "descoberta"
    CURIOSIDADE = "curiosidade"
    CONSIDERACAO = "consideracao"
    COMPARACAO = "comparacao"
    DECISAO = "decisao"
    AUTORIDADE = "autoridade"

@dataclass
class DeteccaoFase:
    """Resultado da detecção de fase do funil."""
    keyword: Keyword
    fase_detectada: FaseFunil
    confianca: float
    fatores: List[str]
    score_intencao: float
    score_palavras_chave: float
    score_padrao: float
    justificativa: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class DetectorFaseFunil:
    """
    Sistema de detecção automática de fase do funil.
    
    Características:
    - Análise semântica de intenção
    - Padrões linguísticos específicos
    - Machine Learning para classificação
    - Validação de coerência
    - Logs detalhados de detecção
    """
    
    def __init__(
        self,
        enable_ml: bool = True,
        enable_logging: bool = True,
        threshold_confianca: float = 0.6
    ):
        """
        Inicializa o detector de fase do funil.
        
        Args:
            enable_ml: Se True, habilita análise de ML
            enable_logging: Se True, habilita logs detalhados
            threshold_confianca: Threshold mínimo de confiança
        """
        self.enable_ml = enable_ml
        self.enable_logging = enable_logging
        self.threshold_confianca = threshold_confianca
        
        # Padrões linguísticos por fase
        self.padroes_fase = {
            FaseFunil.DESCOBERTA: {
                "palavras": ["o que é", "como funciona", "guia", "tutorial", "introdução"],
                "regex": [
                    r"\b(o que é|como funciona|guia|tutorial|introdução)\b",
                    r"\b(primeira vez|iniciante|básico)\b"
                ]
            },
            FaseFunil.CURIOSIDADE: {
                "palavras": ["benefícios", "vantagens", "por que", "dicas", "melhores"],
                "regex": [
                    r"\b(benefícios|vantagens|por que|dicas|melhores)\b",
                    r"\b(como escolher|quando usar|onde encontrar)\b"
                ]
            },
            FaseFunil.CONSIDERACAO: {
                "palavras": ["tipos", "modelos", "opções", "características", "especificações"],
                "regex": [
                    r"\b(tipos|modelos|opções|características|especificações)\b",
                    r"\b(qual escolher|diferenças|comparativo)\b"
                ]
            },
            FaseFunil.COMPARACAO: {
                "palavras": ["vs", "versus", "comparação", "diferença", "melhor"],
                "regex": [
                    r"\b(vs|versus|comparação|diferença|melhor)\b",
                    r"\b(value|contra|entre|qual)\b"
                ]
            },
            FaseFunil.DECISAO: {
                "palavras": ["comprar", "adquirir", "preço", "oferta", "desconto"],
                "regex": [
                    r"\b(comprar|adquirir|preço|oferta|desconto)\b",
                    r"\b(onde comprar|melhor preço|promoção)\b"
                ]
            },
            FaseFunil.AUTORIDADE: {
                "palavras": ["revisão", "análise", "expert", "profissional", "avaliação"],
                "regex": [
                    r"\b(revisão|análise|expert|profissional|avaliação)\b",
                    r"\b(opinião|experiência|teste|review)\b"
                ]
            }
        }
        
        # Mapeamento de intenções para fases
        self.intencao_fase = {
            IntencaoBusca.NAVEGACIONAL: FaseFunil.DESCOBERTA,
            IntencaoBusca.INFORMACIONAL: FaseFunil.CURIOSIDADE,
            IntencaoBusca.COMPARACAO: FaseFunil.COMPARACAO,
            IntencaoBusca.COMERCIAL: FaseFunil.CONSIDERACAO,
            IntencaoBusca.TRANSACIONAL: FaseFunil.DECISAO
        }
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "detector_fase_funil_inicializado",
            "status": "success",
            "source": "detector_fase_funil.__init__",
            "details": {
                "enable_ml": enable_ml,
                "threshold_confianca": threshold_confianca,
                "total_fases": len(FaseFunil)
            }
        })
    
    def detectar_fase_automatica(
        self,
        keywords: List[Keyword],
        contexto_nicho: Optional[str] = None
    ) -> List[DeteccaoFase]:
        """
        Detecta automaticamente a fase do funil para cada keyword.
        
        Args:
            keywords: Lista de keywords para análise
            contexto_nicho: Nicho específico para ajustes
            
        Returns:
            Lista de DeteccaoFase com fases detectadas
        """
        if not keywords:
            logger.warning({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "detector_fase_keywords_vazia",
                "status": "warning",
                "source": "detector_fase_funil.detectar_fase_automatica",
                "details": {"total_keywords": 0}
            })
            return []
        
        resultados = []
        for keyword in keywords:
            deteccao = self._analisar_keyword(keyword, contexto_nicho)
            resultados.append(deteccao)
        
        # Valida coerência entre fases detectadas
        self._validar_coerencia_fases(resultados)
        
        # Log dos resultados
        if self.enable_logging:
            self._log_deteccoes(resultados, contexto_nicho)
        
        return resultados
    
    def _analisar_keyword(
        self,
        keyword: Keyword,
        contexto_nicho: Optional[str]
    ) -> DeteccaoFase:
        """
        Analisa uma keyword individual para detectar sua fase.
        
        Args:
            keyword: Keyword para análise
            contexto_nicho: Nicho específico
            
        Returns:
            DeteccaoFase com resultado da análise
        """
        termo = keyword.termo.lower()
        
        # Análise por intenção
        score_intencao, fase_intencao = self._analisar_por_intencao(keyword)
        
        # Análise por palavras-chave
        score_palavras, fase_palavras = self._analisar_por_palavras_chave(termo)
        
        # Análise por padrões
        score_padrao, fase_padrao = self._analisar_por_padroes(termo)
        
        # Combina os scores
        fase_final, confianca, fatores = self._combinar_scores(
            score_intencao, fase_intencao,
            score_palavras, fase_palavras,
            score_padrao, fase_padrao
        )
        
        # Gera justificativa
        justificativa = self._gerar_justificativa_fase(
            keyword, fase_final, confianca, fatores
        )
        
        return DeteccaoFase(
            keyword=keyword,
            fase_detectada=fase_final,
            confianca=confianca,
            fatores=fatores,
            score_intencao=score_intencao,
            score_palavras_chave=score_palavras,
            score_padrao=score_padrao,
            justificativa=justificativa
        )
    
    def _analisar_por_intencao(self, keyword: Keyword) -> Tuple[float, FaseFunil]:
        """Analisa fase baseada na intenção de busca."""
        if keyword.intencao in self.intencao_fase:
            return 0.8, self.intencao_fase[keyword.intencao]
        else:
            return 0.3, FaseFunil.CURIOSIDADE  # Default
    
    def _analisar_por_palavras_chave(self, termo: str) -> Tuple[float, FaseFunil]:
        """Analisa fase baseada em palavras-chave específicas."""
        melhor_score = 0.0
        melhor_fase = FaseFunil.CURIOSIDADE
        
        for fase, config in self.padroes_fase.items():
            score = 0.0
            palavras_encontradas = 0
            
            # Verifica palavras-chave
            for palavra in config["palavras"]:
                if palavra in termo:
                    palavras_encontradas += 1
            
            # Calcula score baseado no número de palavras encontradas
            if palavras_encontradas > 0:
                score = min(0.9, palavras_encontradas * 0.3)
            
            if score > melhor_score:
                melhor_score = score
                melhor_fase = fase
        
        return melhor_score, melhor_fase
    
    def _analisar_por_padroes(self, termo: str) -> Tuple[float, FaseFunil]:
        """Analisa fase baseada em padrões regex."""
        melhor_score = 0.0
        melhor_fase = FaseFunil.CURIOSIDADE
        
        for fase, config in self.padroes_fase.items():
            score = 0.0
            padroes_encontrados = 0
            
            # Verifica padrões regex
            for padrao in config["regex"]:
                if re.search(padrao, termo, re.IGNORECASE):
                    padroes_encontrados += 1
            
            # Calcula score baseado no número de padrões encontrados
            if padroes_encontrados > 0:
                score = min(0.95, padroes_encontrados * 0.4)
            
            if score > melhor_score:
                melhor_score = score
                melhor_fase = fase
        
        return melhor_score, melhor_fase
    
    def _combinar_scores(
        self,
        score_intencao: float,
        fase_intencao: FaseFunil,
        score_palavras: float,
        fase_palavras: FaseFunil,
        score_padrao: float,
        fase_padrao: FaseFunil
    ) -> Tuple[FaseFunil, float, List[str]]:
        """
        Combina os diferentes scores para determinar a fase final.
        
        Args:
            score_intencao: Score da análise por intenção
            fase_intencao: Fase detectada por intenção
            score_palavras: Score da análise por palavras-chave
            fase_palavras: Fase detectada por palavras-chave
            score_padrao: Score da análise por padrões
            fase_padrao: Fase detectada por padrões
            
        Returns:
            Tupla com (fase_final, confianca, fatores)
        """
        # Pesos para cada tipo de análise
        peso_intencao = 0.4
        peso_palavras = 0.3
        peso_padrao = 0.3
        
        # Calcula scores ponderados por fase
        scores_por_fase = {}
        fatores = []
        
        # Adiciona scores por intenção
        if score_intencao > 0:
            scores_por_fase[fase_intencao] = scores_por_fase.get(fase_intencao, 0) + score_intencao * peso_intencao
            fatores.append(f"intenção: {fase_intencao.value}")
        
        # Adiciona scores por palavras-chave
        if score_palavras > 0:
            scores_por_fase[fase_palavras] = scores_por_fase.get(fase_palavras, 0) + score_palavras * peso_palavras
            fatores.append(f"palavras-chave: {fase_palavras.value}")
        
        # Adiciona scores por padrões
        if score_padrao > 0:
            scores_por_fase[fase_padrao] = scores_por_fase.get(fase_padrao, 0) + score_padrao * peso_padrao
            fatores.append(f"padrões: {fase_padrao.value}")
        
        # Determina fase com maior score
        if scores_por_fase:
            fase_final = max(scores_por_fase, key=scores_por_fase.get)
            confianca = scores_por_fase[fase_final]
        else:
            fase_final = FaseFunil.CURIOSIDADE
            confianca = 0.3
            fatores.append("análise inconclusiva")
        
        return fase_final, round(confianca, 3), fatores
    
    def _gerar_justificativa_fase(
        self,
        keyword: Keyword,
        fase: FaseFunil,
        confianca: float,
        fatores: List[str]
    ) -> str:
        """Gera justificativa detalhada da fase detectada."""
        if confianca >= 0.8:
            nivel = "alta"
        elif confianca >= 0.6:
            nivel = "média"
        else:
            nivel = "baixa"
        
        fatores_str = ", ".join(fatores)
        return f"Fase {fase.value} detectada com confiança {nivel} ({confianca:.1%}) baseada em: {fatores_str}"
    
    def _validar_coerencia_fases(self, deteccoes: List[DeteccaoFase]) -> None:
        """
        Valida coerência entre as fases detectadas.
        
        Args:
            deteccoes: Lista de detecções para validar
        """
        if len(deteccoes) < 2:
            return
        
        # Verifica se há fases duplicadas com alta confiança
        fases_por_confianca = {}
        for deteccao in deteccoes:
            if deteccao.confianca >= 0.7:
                fase = deteccao.fase_detectada
                if fase not in fases_por_confianca:
                    fases_por_confianca[fase] = []
                fases_por_confianca[fase].append(deteccao.keyword.termo)
        
        # Log de alertas se necessário
        for fase, termos in fases_por_confianca.items():
            if len(termos) > 1:
                logger.warning({
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": "fase_duplicada_detectada",
                    "status": "warning",
                    "source": "detector_fase_funil._validar_coerencia_fases",
                    "details": {
                        "fase": fase.value,
                        "termos": termos,
                        "total_duplicados": len(termos)
                    }
                })
    
    def _log_deteccoes(
        self,
        deteccoes: List[DeteccaoFase],
        contexto_nicho: Optional[str]
    ) -> None:
        """Registra logs detalhados das detecções."""
        # Estatísticas por fase
        stats_por_fase = {}
        for deteccao in deteccoes:
            fase = deteccao.fase_detectada.value
            if fase not in stats_por_fase:
                stats_por_fase[fase] = {
                    "total": 0,
                    "confianca_media": 0.0,
                    "termos": []
                }
            stats_por_fase[fase]["total"] += 1
            stats_por_fase[fase]["confianca_media"] += deteccao.confianca
            stats_por_fase[fase]["termos"].append(deteccao.keyword.termo)
        
        # Calcula confiança média por fase
        for fase in stats_por_fase:
            total = stats_por_fase[fase]["total"]
            stats_por_fase[fase]["confianca_media"] = round(
                stats_por_fase[fase]["confianca_media"] / total, 3
            )
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "fases_funil_detectadas",
            "status": "success",
            "source": "detector_fase_funil._log_deteccoes",
            "details": {
                "total_keywords": len(deteccoes),
                "contexto_nicho": contexto_nicho,
                "estatisticas_por_fase": stats_por_fase,
                "confianca_geral_media": round(
                    sum(data.confianca for data in deteccoes) / len(deteccoes), 3
                )
            }
        })
    
    def aplicar_deteccao_automatica(
        self,
        keywords: List[Keyword],
        contexto_nicho: Optional[str] = None
    ) -> List[Keyword]:
        """
        Aplica detecção automática e atualiza as keywords.
        
        Args:
            keywords: Lista de keywords para processar
            contexto_nicho: Nicho específico para ajustes
            
        Returns:
            Lista de keywords com fases detectadas
        """
        deteccoes = self.detectar_fase_automatica(keywords, contexto_nicho)
        
        # Atualiza as keywords com as fases detectadas
        for deteccao in deteccoes:
            keyword = deteccao.keyword
            keyword.fase_funil = deteccao.fase_detectada.value
            keyword.nome_artigo = f"Artigo_{deteccao.fase_detectada.value.capitalize()}"
            
            # Adiciona metadados de detecção
            if not hasattr(keyword, 'metadados_deteccao'):
                keyword.metadados_deteccao = {}
            
            keyword.metadados_deteccao.update({
                "fase_detectada": deteccao.fase_detectada.value,
                "confianca_deteccao": deteccao.confianca,
                "fatores_deteccao": deteccao.fatores,
                "justificativa_deteccao": deteccao.justificativa,
                "timestamp_deteccao": deteccao.timestamp.isoformat()
            })
        
        return keywords
    
    def validar_qualidade_deteccao(
        self,
        deteccoes: List[DeteccaoFase]
    ) -> Dict[str, Any]:
        """
        Valida a qualidade das detecções realizadas.
        
        Args:
            deteccoes: Lista de detecções para validar
            
        Returns:
            Dicionário com métricas de qualidade
        """
        if not deteccoes:
            return {"status": "empty", "message": "Nenhuma detecção para validar"}
        
        confiancas = [data.confianca for data in deteccoes]
        
        # Calcula métricas de qualidade
        qualidade = {
            "total_keywords": len(deteccoes),
            "confianca_media": round(sum(confiancas) / len(confiancas), 3),
            "confianca_mediana": round(sorted(confiancas)[len(confiancas)//2], 3),
            "confianca_min": round(min(confiancas), 3),
            "confianca_max": round(max(confiancas), 3),
            "distribuicao_confianca": {
                "alta": len([c for c in confiancas if c >= 0.8]),
                "media": len([c for c in confiancas if 0.6 <= c < 0.8]),
                "baixa": len([c for c in confiancas if c < 0.6])
            },
            "fases_detectadas": {}
        }
        
        # Estatísticas por fase
        for deteccao in deteccoes:
            fase = deteccao.fase_detectada.value
            if fase not in qualidade["fases_detectadas"]:
                qualidade["fases_detectadas"][fase] = 0
            qualidade["fases_detectadas"][fase] += 1
        
        # Determina status geral
        if qualidade["confianca_media"] >= 0.7:
            qualidade["status"] = "excelente"
        elif qualidade["confianca_media"] >= 0.5:
            qualidade["status"] = "bom"
        else:
            qualidade["status"] = "precisa_melhoria"
        
        return qualidade

# Função de conveniência para uso direto
def detectar_fases_funil_automatico(
    keywords: List[Keyword],
    contexto_nicho: Optional[str] = None,
    enable_ml: bool = True
) -> List[Keyword]:
    """
    Função de conveniência para detecção automática de fases do funil.
    
    Args:
        keywords: Lista de keywords para processar
        contexto_nicho: Nicho específico para ajustes
        enable_ml: Se True, habilita análise de ML
        
    Returns:
        Lista de keywords com fases detectadas
    """
    detector = DetectorFaseFunil(enable_ml=enable_ml)
    return detector.aplicar_deteccao_automatica(keywords, contexto_nicho) 