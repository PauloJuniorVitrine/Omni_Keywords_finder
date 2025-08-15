"""
Sistema de Score Competitivo Adaptativo
LONGTAIL-003: Sistema completo de score competitivo adaptativo

Tracing ID: LONGTAIL-003
Data/Hora: 2024-12-20 16:45:00 UTC
Versão: 1.0
Status: EM IMPLEMENTAÇÃO

Responsável: Sistema de Cauda Longa
"""

import math
from typing import Dict, List, Optional, Tuple, NamedTuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from shared.logger import logger


class NivelCompetitividade(Enum):
    """Níveis de competitividade."""
    BAIXA = "baixa"
    MEDIA = "média"
    ALTA = "alta"
    MUITO_ALTA = "muito alta"


@dataclass
class ScoreCompetitivo:
    """Resultado do cálculo de score competitivo."""
    score_final: float
    nivel_competitividade: NivelCompetitividade
    volume_normalizado: float
    cpc_normalizado: float
    concorrencia_normalizada: float
    fatores_competitivos: Dict[str, float]
    metadados: Dict[str, any]


class CalculadorScoreCompetitivo:
    """
    Sistema completo de score competitivo adaptativo para cauda longa.
    
    Funcionalidades:
    - Normalização de volume de busca
    - Normalização de CPC
    - Concorrência adaptativa por nicho
    - Fórmula: Score = (Volume * 0.4) + (CPC * 0.3) + (1 - Concorrência * 0.3)
    - Classificação automática de competitividade
    - Priorização por score
    - Relatórios de competitividade
    - Thresholds dinâmicos
    - Integração com cobertura
    - Logs de análise competitiva
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o calculador de score competitivo.
        
        Args:
            config: Configuração opcional do calculador
        """
        self.config = config or {}
        
        # Pesos da fórmula
        self._peso_volume = self.config.get("peso_volume", 0.4)
        self._peso_cpc = self.config.get("peso_cpc", 0.3)
        self._peso_concorrencia = self.config.get("peso_concorrencia", 0.3)
        
        # Thresholds de normalização
        self._max_volume = self.config.get("max_volume", 100000)
        self._max_cpc = self.config.get("max_cpc", 50.0)
        self._max_concorrencia = self.config.get("max_concorrencia", 1.0)
        
        # Thresholds de competitividade
        self._threshold_baixa = self.config.get("threshold_baixa", 0.3)
        self._threshold_media = self.config.get("threshold_media", 0.6)
        self._threshold_alta = self.config.get("threshold_alta", 0.8)
        
        # Configurações por nicho
        self._configuracoes_nicho = self._carregar_configuracoes_nicho()
        
        # Métricas de performance
        self.metricas = {
            "total_calculos": 0,
            "total_keywords_processadas": 0,
            "tempo_total_calculo": 0.0,
            "ultimo_calculo": None
        }
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "calculador_score_competitivo_inicializado",
            "status": "success",
            "source": "CalculadorScoreCompetitivo.__init__",
            "details": {
                "peso_volume": self._peso_volume,
                "peso_cpc": self._peso_cpc,
                "peso_concorrencia": self._peso_concorrencia,
                "max_volume": self._max_volume,
                "max_cpc": self._max_cpc,
                "max_concorrencia": self._max_concorrencia,
                "threshold_baixa": self._threshold_baixa,
                "threshold_media": self._threshold_media,
                "threshold_alta": self._threshold_alta,
                "nichos_configurados": len(self._configuracoes_nicho)
            }
        })
    
    def _carregar_configuracoes_nicho(self) -> Dict[str, Dict]:
        """
        Carrega configurações específicas por nicho.
        
        Returns:
            Dicionário com configurações por nicho
        """
        configuracoes = {
            "e-commerce": {
                "peso_volume": 0.5,
                "peso_cpc": 0.3,
                "peso_concorrencia": 0.2,
                "max_volume": 50000,
                "max_cpc": 30.0,
                "max_concorrencia": 0.9,
                "threshold_baixa": 0.4,
                "threshold_media": 0.7,
                "threshold_alta": 0.85
            },
            "saude": {
                "peso_volume": 0.3,
                "peso_cpc": 0.4,
                "peso_concorrencia": 0.3,
                "max_volume": 20000,
                "max_cpc": 40.0,
                "max_concorrencia": 0.8,
                "threshold_baixa": 0.3,
                "threshold_media": 0.6,
                "threshold_alta": 0.8
            },
            "tecnologia": {
                "peso_volume": 0.4,
                "peso_cpc": 0.3,
                "peso_concorrencia": 0.3,
                "max_volume": 80000,
                "max_cpc": 35.0,
                "max_concorrencia": 0.95,
                "threshold_baixa": 0.35,
                "threshold_media": 0.65,
                "threshold_alta": 0.85
            },
            "educacao": {
                "peso_volume": 0.4,
                "peso_cpc": 0.2,
                "peso_concorrencia": 0.4,
                "max_volume": 30000,
                "max_cpc": 25.0,
                "max_concorrencia": 0.7,
                "threshold_baixa": 0.3,
                "threshold_media": 0.6,
                "threshold_alta": 0.8
            },
            "financas": {
                "peso_volume": 0.3,
                "peso_cpc": 0.5,
                "peso_concorrencia": 0.2,
                "max_volume": 15000,
                "max_cpc": 60.0,
                "max_concorrencia": 0.9,
                "threshold_baixa": 0.25,
                "threshold_media": 0.55,
                "threshold_alta": 0.8
            }
        }
        
        return configuracoes
    
    def detectar_nicho(self, keyword: str, metadados: Optional[Dict] = None) -> str:
        """
        Detecta o nicho da keyword baseado em palavras-chave.
        
        Args:
            keyword: Keyword para análise
            metadados: Metadados adicionais
            
        Returns:
            Nicho detectado
        """
        keyword_lower = keyword.lower()
        
        # Palavras-chave por nicho
        nichos = {
            "e-commerce": ["comprar", "venda", "loja", "produto", "preço", "oferta", "desconto", "frete"],
            "saude": ["saúde", "médico", "tratamento", "sintomas", "doença", "cura", "medicamento", "consulta"],
            "tecnologia": ["software", "app", "programa", "tecnologia", "digital", "online", "internet", "computador"],
            "educacao": ["curso", "estudar", "aprender", "ensino", "educação", "faculdade", "universidade", "professor"],
            "financas": ["investimento", "dinheiro", "banco", "crédito", "financiamento", "economia", "lucro", "renda"]
        }
        
        # Contagem de palavras por nicho
        scores_nicho = {}
        for nicho, palavras_chave in nichos.items():
            score = sum(1 for palavra in palavras_chave if palavra in keyword_lower)
            scores_nicho[nicho] = score
        
        # Retorna nicho com maior score
        nicho_detectado = max(scores_nicho.items(), key=lambda value: value[1])[0]
        
        # Se nenhuma palavra-chave foi encontrada, usa configuração padrão
        if scores_nicho[nicho_detectado] == 0:
            return "padrao"
        
        return nicho_detectado
    
    def obter_configuracao_nicho(self, nicho: str) -> Dict:
        """
        Obtém configuração específica para o nicho.
        
        Args:
            nicho: Nicho para configuração
            
        Returns:
            Configuração do nicho
        """
        return self._configuracoes_nicho.get(nicho, {
            "peso_volume": self._peso_volume,
            "peso_cpc": self._peso_cpc,
            "peso_concorrencia": self._peso_concorrencia,
            "max_volume": self._max_volume,
            "max_cpc": self._max_cpc,
            "max_concorrencia": self._max_concorrencia,
            "threshold_baixa": self._threshold_baixa,
            "threshold_media": self._threshold_media,
            "threshold_alta": self._threshold_alta
        })
    
    def normalizar_volume(self, volume: int, max_volume: int) -> float:
        """
        Normaliza volume de busca para escala 0-1.
        
        Args:
            volume: Volume de busca
            max_volume: Volume máximo para normalização
            
        Returns:
            Volume normalizado entre 0 e 1
        """
        if volume <= 0:
            return 0.0
        
        # Usa logaritmo para suavizar distribuição
        volume_log = math.log(volume + 1)
        max_volume_log = math.log(max_volume + 1)
        
        return min(1.0, volume_log / max_volume_log)
    
    def normalizar_cpc(self, cpc: float, max_cpc: float) -> float:
        """
        Normaliza CPC para escala 0-1.
        
        Args:
            cpc: CPC
            max_cpc: CPC máximo para normalização
            
        Returns:
            CPC normalizado entre 0 e 1
        """
        if cpc <= 0:
            return 0.0
        
        # Normalização linear com limite superior
        return min(1.0, cpc / max_cpc)
    
    def normalizar_concorrencia(self, concorrencia: float, max_concorrencia: float) -> float:
        """
        Normaliza concorrência para escala 0-1.
        
        Args:
            concorrencia: Concorrência
            max_concorrencia: Concorrência máxima para normalização
            
        Returns:
            Concorrência normalizada entre 0 e 1
        """
        if concorrencia <= 0:
            return 0.0
        
        # Normalização linear com limite superior
        return min(1.0, concorrencia / max_concorrencia)
    
    def calcular_fatores_competitivos(
        self, 
        volume: int, 
        cpc: float, 
        concorrencia: float, 
        config_nicho: Dict
    ) -> Dict[str, float]:
        """
        Calcula fatores competitivos individuais.
        
        Args:
            volume: Volume de busca
            cpc: CPC
            concorrencia: Concorrência
            config_nicho: Configuração do nicho
            
        Returns:
            Dicionário com fatores competitivos
        """
        # Normalizações
        volume_norm = self.normalizar_volume(volume, config_nicho["max_volume"])
        cpc_norm = self.normalizar_cpc(cpc, config_nicho["max_cpc"])
        concorrencia_norm = self.normalizar_concorrencia(concorrencia, config_nicho["max_concorrencia"])
        
        # Fator de concorrência invertido (menor concorrência = melhor)
        concorrencia_invertida = 1 - concorrencia_norm
        
        return {
            "volume_normalizado": volume_norm,
            "cpc_normalizado": cpc_norm,
            "concorrencia_normalizada": concorrencia_norm,
            "concorrencia_invertida": concorrencia_invertida
        }
    
    def calcular_score_competitivo(
        self, 
        fatores: Dict[str, float], 
        config_nicho: Dict
    ) -> float:
        """
        Calcula score competitivo final.
        
        Args:
            fatores: Fatores competitivos
            config_nicho: Configuração do nicho
            
        Returns:
            Score competitivo entre 0 e 1
        """
        # Aplica pesos específicos do nicho
        score = (
            fatores["volume_normalizado"] * config_nicho["peso_volume"] +
            fatores["cpc_normalizado"] * config_nicho["peso_cpc"] +
            fatores["concorrencia_invertida"] * config_nicho["peso_concorrencia"]
        )
        
        return min(1.0, max(0.0, score))
    
    def classificar_competitividade(self, score: float, config_nicho: Dict) -> NivelCompetitividade:
        """
        Classifica o nível de competitividade baseado no score.
        
        Args:
            score: Score competitivo
            config_nicho: Configuração do nicho
            
        Returns:
            Nível de competitividade
        """
        if score < config_nicho["threshold_baixa"]:
            return NivelCompetitividade.BAIXA
        elif score < config_nicho["threshold_media"]:
            return NivelCompetitividade.MEDIA
        elif score < config_nicho["threshold_alta"]:
            return NivelCompetitividade.ALTA
        else:
            return NivelCompetitividade.MUITO_ALTA
    
    def calcular_score(
        self, 
        keyword: str, 
        volume: int, 
        cpc: float, 
        concorrencia: float,
        metadados: Optional[Dict] = None
    ) -> ScoreCompetitivo:
        """
        Calcula score competitivo completo para uma keyword.
        
        Args:
            keyword: Keyword para análise
            volume: Volume de busca
            cpc: CPC
            concorrencia: Concorrência
            metadados: Metadados adicionais
            
        Returns:
            Resultado do score competitivo
        """
        inicio_calculo = datetime.utcnow()
        
        try:
            # Detecção de nicho
            nicho = self.detectar_nicho(keyword, metadados)
            config_nicho = self.obter_configuracao_nicho(nicho)
            
            # Cálculo de fatores competitivos
            fatores = self.calcular_fatores_competitivos(volume, cpc, concorrencia, config_nicho)
            
            # Cálculo do score final
            score_final = self.calcular_score_competitivo(fatores, config_nicho)
            
            # Classificação de competitividade
            nivel_competitividade = self.classificar_competitividade(score_final, config_nicho)
            
            # Metadados do cálculo
            metadados_calculo = {
                "keyword": keyword,
                "nicho_detectado": nicho,
                "configuracao_nicho": config_nicho,
                "valores_originais": {
                    "volume": volume,
                    "cpc": cpc,
                    "concorrencia": concorrencia
                },
                "metadados_entrada": metadados or {}
            }
            
            # Criação do resultado
            resultado = ScoreCompetitivo(
                score_final=score_final,
                nivel_competitividade=nivel_competitividade,
                volume_normalizado=fatores["volume_normalizado"],
                cpc_normalizado=fatores["cpc_normalizado"],
                concorrencia_normalizada=fatores["concorrencia_normalizada"],
                fatores_competitivos=fatores,
                metadados=metadados_calculo
            )
            
            # Atualização de métricas
            tempo_calculo = (datetime.utcnow() - inicio_calculo).total_seconds()
            self.metricas["total_calculos"] += 1
            self.metricas["total_keywords_processadas"] += 1
            self.metricas["tempo_total_calculo"] += tempo_calculo
            self.metricas["ultimo_calculo"] = datetime.utcnow().isoformat()
            
            # Log do cálculo
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "calculo_score_competitivo",
                "status": "success",
                "source": "CalculadorScoreCompetitivo.calcular_score",
                "details": {
                    "keyword": keyword,
                    "nicho": nicho,
                    "volume": volume,
                    "cpc": cpc,
                    "concorrencia": concorrencia,
                    "score_final": score_final,
                    "nivel_competitividade": nivel_competitividade.value,
                    "tempo_calculo": tempo_calculo
                }
            })
            
            return resultado
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_calculo_score_competitivo",
                "status": "error",
                "source": "CalculadorScoreCompetitivo.calcular_score",
                "details": {
                    "keyword": keyword,
                    "volume": volume,
                    "cpc": cpc,
                    "concorrencia": concorrencia,
                    "erro": str(e)
                }
            })
            
            # Retorno de erro
            return ScoreCompetitivo(
                score_final=0.0,
                nivel_competitividade=NivelCompetitividade.BAIXA,
                volume_normalizado=0.0,
                cpc_normalizado=0.0,
                concorrencia_normalizada=0.0,
                fatores_competitivos={},
                metadados={"erro": str(e)}
            )
    
    def priorizar_keywords(self, keywords_scores: List[ScoreCompetitivo]) -> List[ScoreCompetitivo]:
        """
        Prioriza keywords baseado no score competitivo.
        
        Args:
            keywords_scores: Lista de scores competitivos
            
        Returns:
            Lista priorizada de scores
        """
        # Ordena por score decrescente
        keywords_priorizadas = sorted(
            keywords_scores, 
            key=lambda value: value.score_final, 
            reverse=True
        )
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "priorizacao_keywords",
            "status": "success",
            "source": "CalculadorScoreCompetitivo.priorizar_keywords",
            "details": {
                "total_keywords": len(keywords_priorizadas),
                "score_maximo": keywords_priorizadas[0].score_final if keywords_priorizadas else 0.0,
                "score_minimo": keywords_priorizadas[-1].score_final if keywords_priorizadas else 0.0
            }
        })
        
        return keywords_priorizadas
    
    def gerar_relatorio_competitividade(self, keywords_scores: List[ScoreCompetitivo]) -> Dict:
        """
        Gera relatório de competitividade.
        
        Args:
            keywords_scores: Lista de scores competitivos
            
        Returns:
            Relatório de competitividade
        """
        if not keywords_scores:
            return {"erro": "Nenhuma keyword para análise"}
        
        # Estatísticas básicas
        scores = [ks.score_final for ks in keywords_scores]
        volumes = [ks.volume_normalizado for ks in keywords_scores]
        cpcs = [ks.cpc_normalizado for ks in keywords_scores]
        concorrencias = [ks.concorrencia_normalizada for ks in keywords_scores]
        
        # Contagem por nível
        niveis = {}
        for nivel in NivelCompetitividade:
            niveis[nivel.value] = sum(1 for ks in keywords_scores if ks.nivel_competitividade == nivel)
        
        # Nichos detectados
        nichos = {}
        for ks in keywords_scores:
            nicho = ks.metadados.get("nicho_detectado", "desconhecido")
            nichos[nicho] = nichos.get(nicho, 0) + 1
        
        relatorio = {
            "estatisticas_gerais": {
                "total_keywords": len(keywords_scores),
                "score_medio": sum(scores) / len(scores),
                "score_maximo": max(scores),
                "score_minimo": min(scores),
                "volume_medio": sum(volumes) / len(volumes),
                "cpc_medio": sum(cpcs) / len(cpcs),
                "concorrencia_media": sum(concorrencias) / len(concorrencias)
            },
            "distribuicao_niveis": niveis,
            "distribuicao_nichos": nichos,
            "top_keywords": [
                {
                    "keyword": ks.metadados.get("keyword", "desconhecida"),
                    "score": ks.score_final,
                    "nivel": ks.nivel_competitividade.value,
                    "nicho": ks.metadados.get("nicho_detectado", "desconhecido")
                }
                for ks in sorted(keywords_scores, key=lambda value: value.score_final, reverse=True)[:10]
            ]
        }
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "relatorio_competitividade_gerado",
            "status": "success",
            "source": "CalculadorScoreCompetitivo.gerar_relatorio_competitividade",
            "details": {
                "total_keywords": len(keywords_scores),
                "score_medio": relatorio["estatisticas_gerais"]["score_medio"]
            }
        })
        
        return relatorio
    
    def obter_metricas(self) -> Dict:
        """
        Obtém métricas de performance do calculador.
        
        Returns:
            Dicionário com métricas
        """
        return {
            **self.metricas,
            "tempo_medio_calculo": (
                self.metricas["tempo_total_calculo"] / max(self.metricas["total_calculos"], 1)
            ),
            "keywords_por_calculo": (
                self.metricas["total_keywords_processadas"] / max(self.metricas["total_calculos"], 1)
            )
        }
    
    def resetar_metricas(self):
        """Reseta métricas de performance."""
        self.metricas = {
            "total_calculos": 0,
            "total_keywords_processadas": 0,
            "tempo_total_calculo": 0.0,
            "ultimo_calculo": None
        }
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "metricas_resetadas",
            "status": "info",
            "source": "CalculadorScoreCompetitivo.resetar_metricas",
            "details": {"acao": "reset_metricas"}
        })


# Instância global para uso em outros módulos
calculador_score_competitivo = CalculadorScoreCompetitivo() 