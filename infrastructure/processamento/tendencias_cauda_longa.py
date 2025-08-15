"""
Sistema de Tendências para Cauda Longa - Omni Keywords Finder
Tracing ID: LONGTAIL-009
Data/Hora: 2024-12-20 17:20:00 UTC
Versão: 1.0
Status: IMPLEMENTADO

Sistema completo de análise de tendências que detecta padrões temporais,
tendências emergentes e sazonalidade em keywords de cauda longa.
"""

import json
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
from collections import defaultdict, Counter
import re

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TipoTendencia(Enum):
    """Tipos de tendência."""
    CRESCENTE = "crescente"
    DECRESCENTE = "decrescente"
    ESTAVEL = "estavel"
    SAZONAL = "sazonal"
    EMERGENTE = "emergente"
    DECLINANTE = "declinante"

class CategoriaTendencia(Enum):
    """Categorias de tendência."""
    VOLUME_BUSCA = "volume_busca"
    CPC = "cpc"
    CONCORRENCIA = "concorrencia"
    SAZONALIDADE = "sazonalidade"
    NOVIDADE = "novidade"
    COMPOSTA = "composta"

@dataclass
class DadosTemporais:
    """Estrutura para dados temporais."""
    data: datetime
    volume_busca: int
    cpc: float
    concorrencia: float
    posicao_serp: Optional[int]
    cliques: Optional[int]
    impressoes: Optional[int]

@dataclass
class AnaliseTendencia:
    """Estrutura para análise de tendência."""
    keyword: str
    tipo_tendencia: TipoTendencia
    categoria: CategoriaTendencia
    score_tendencia: float
    periodo_analise: str
    dados_temporais: List[DadosTemporais]
    padrao_detectado: str
    confianca: float
    predicao_proximo_mes: Optional[Dict[str, Any]]
    timestamp: datetime
    tracing_id: str

@dataclass
class TendenciaEmergente:
    """Estrutura para tendência emergente."""
    keyword: str
    score_emergencia: float
    taxa_crescimento: float
    volume_atual: int
    volume_anterior: int
    fatores_emergencia: List[str]
    nicho_relacionado: str
    timestamp_deteccao: datetime
    confianca: float

class SistemaTendenciasCaudaLonga:
    """
    Sistema de análise de tendências para cauda longa.
    
    Características:
    - Análise temporal de keywords
    - Detecção de tendências emergentes
    - Score de tendência
    - Relatórios de tendências
    - Alertas de novas tendências
    - Integração com coleta
    - Logs de tendências
    - Configuração de alertas
    - Análise de sazonalidade
    - Predição de tendências
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa o sistema de tendências.
        
        Args:
            config_path: Caminho para arquivo de configuração
        """
        self.tracing_id = f"LONGTAIL-009_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.config = self._carregar_configuracao(config_path)
        self.dados_historicos = defaultdict(list)
        self.tendencias_emergentes = []
        self.alertas_configurados = []
        
        logger.info(f"[{self.tracing_id}] Sistema de tendências inicializado")
    
    def _carregar_configuracao(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Carrega configuração do sistema de tendências."""
        config_padrao = {
            "periodos_analise": {
                "curto_prazo": 30,  # dias
                "medio_prazo": 90,
                "longo_prazo": 365
            },
            "thresholds_tendencia": {
                "crescimento_significativo": 0.2,  # 20%
                "declinio_significativo": -0.15,   # -15%
                "estabilidade": 0.05,              # ±5%
                "emergencia": 0.5                  # 50% crescimento
            },
            "pesos_analise": {
                "volume_busca": 0.4,
                "cpc": 0.2,
                "concorrencia": 0.2,
                "sazonalidade": 0.2
            },
            "configuracao_alertas": {
                "tendencia_emergente": True,
                "declinio_significativo": True,
                "sazonalidade_detectada": True,
                "volume_anomalo": True
            },
            "configuracao_predicao": {
                "horizonte_predicao": 30,  # dias
                "confianca_minima": 0.7,
                "metodo_predicao": "regressao_linear"
            }
        }
        
        if config_path:
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_custom = json.load(f)
                    config_padrao.update(config_custom)
            except Exception as e:
                logger.warning(f"[{self.tracing_id}] Erro ao carregar config: {e}")
        
        return config_padrao
    
    def adicionar_dados_temporais(
        self, 
        keyword: str, 
        dados: Union[DadosTemporais, Dict[str, Any]]
    ) -> bool:
        """
        Adiciona dados temporais para análise de tendência.
        
        Args:
            keyword: Keyword relacionada
            dados: Dados temporais
            
        Returns:
            bool: True se adicionado com sucesso
        """
        try:
            if isinstance(dados, dict):
                # Converter dict para DadosTemporais
                dados_temporais = DadosTemporais(
                    data=datetime.fromisoformat(dados["data"]) if isinstance(dados["data"], str) else dados["data"],
                    volume_busca=dados.get("volume_busca", 0),
                    cpc=dados.get("cpc", 0.0),
                    concorrencia=dados.get("concorrencia", 0.0),
                    posicao_serp=dados.get("posicao_serp"),
                    cliques=dados.get("cliques"),
                    impressoes=dados.get("impressoes")
                )
            else:
                dados_temporais = dados
            
            # Adicionar à lista histórica
            self.dados_historicos[keyword].append(dados_temporais)
            
            # Ordenar por data
            self.dados_historicos[keyword].sort(key=lambda value: value.data)
            
            logger.info(f"[{self.tracing_id}] Dados temporais adicionados para: {keyword}")
            return True
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro ao adicionar dados temporais: {e}")
            return False
    
    def analisar_tendencia(
        self, 
        keyword: str, 
        periodo: str = "medio_prazo"
    ) -> Optional[AnaliseTendencia]:
        """
        Analisa tendência de uma keyword específica.
        
        Args:
            keyword: Keyword a ser analisada
            periodo: Período de análise (curto_prazo, medio_prazo, longo_prazo)
            
        Returns:
            AnaliseTendencia: Análise de tendência
        """
        try:
            if keyword not in self.dados_historicos:
                logger.warning(f"[{self.tracing_id}] Sem dados históricos para: {keyword}")
                return None
            
            dados = self.dados_historicos[keyword]
            if len(dados) < 2:
                logger.warning(f"[{self.tracing_id}] Dados insuficientes para análise: {keyword}")
                return None
            
            # Filtrar dados por período
            dias_periodo = self.config["periodos_analise"][periodo]
            data_limite = datetime.now() - timedelta(days=dias_periodo)
            dados_filtrados = [data for data in dados if data.data >= data_limite]
            
            if len(dados_filtrados) < 2:
                logger.warning(f"[{self.tracing_id}] Dados insuficientes no período: {keyword}")
                return None
            
            # Análise de tendência
            tipo_tendencia = self._detectar_tipo_tendencia(dados_filtrados)
            score_tendencia = self._calcular_score_tendencia(dados_filtrados)
            padrao_detectado = self._identificar_padrao(dados_filtrados)
            confianca = self._calcular_confianca_tendencia(dados_filtrados)
            
            # Predição para próximo mês
            predicao = self._predizer_proximo_mes(dados_filtrados)
            
            # Criação da análise
            analise = AnaliseTendencia(
                keyword=keyword,
                tipo_tendencia=tipo_tendencia,
                categoria=CategoriaTendencia.COMPOSTA,
                score_tendencia=score_tendencia,
                periodo_analise=periodo,
                dados_temporais=dados_filtrados,
                padrao_detectado=padrao_detectado,
                confianca=confianca,
                predicao_proximo_mes=predicao,
                timestamp=datetime.now(),
                tracing_id=self.tracing_id
            )
            
            logger.info(f"[{self.tracing_id}] Análise de tendência concluída: {keyword} - {tipo_tendencia.value}")
            return analise
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro na análise de tendência: {e}")
            return None
    
    def _detectar_tipo_tendencia(self, dados: List[DadosTemporais]) -> TipoTendencia:
        """Detecta o tipo de tendência baseado nos dados."""
        try:
            if len(dados) < 2:
                return TipoTendencia.ESTAVEL
            
            # Calcular taxas de crescimento
            volumes = [data.volume_busca for data in dados]
            cpcs = [data.cpc for data in dados]
            
            # Taxa de crescimento do volume
            if volumes[0] > 0:
                taxa_volume = (volumes[-1] - volumes[0]) / volumes[0]
            else:
                taxa_volume = 0
            
            # Taxa de crescimento do CPC
            if cpcs[0] > 0:
                taxa_cpc = (cpcs[-1] - cpcs[0]) / cpcs[0]
            else:
                taxa_cpc = 0
            
            # Análise de sazonalidade
            sazonal = self._detectar_sazonalidade(dados)
            
            # Determinação do tipo
            thresholds = self.config["thresholds_tendencia"]
            
            if sazonal:
                return TipoTendencia.SAZONAL
            elif taxa_volume >= thresholds["emergencia"]:
                return TipoTendencia.EMERGENTE
            elif taxa_volume >= thresholds["crescimento_significativo"]:
                return TipoTendencia.CRESCENTE
            elif taxa_volume <= thresholds["declinio_significativo"]:
                return TipoTendencia.DECLINANTE
            elif abs(taxa_volume) <= thresholds["estabilidade"]:
                return TipoTendencia.ESTAVEL
            else:
                return TipoTendencia.DECRESCENTE
                
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro na detecção de tipo de tendência: {e}")
            return TipoTendencia.ESTAVEL
    
    def _calcular_score_tendencia(self, dados: List[DadosTemporais]) -> float:
        """Calcula score de tendência baseado em múltiplos fatores."""
        try:
            if len(dados) < 2:
                return 0.5
            
            pesos = self.config["pesos_analise"]
            scores = {}
            
            # Score de volume de busca
            volumes = [data.volume_busca for data in dados]
            if volumes[0] > 0:
                taxa_volume = (volumes[-1] - volumes[0]) / volumes[0]
                scores["volume_busca"] = min(1.0, max(0, 0.5 + taxa_volume))
            else:
                scores["volume_busca"] = 0.5
            
            # Score de CPC
            cpcs = [data.cpc for data in dados]
            if cpcs[0] > 0:
                taxa_cpc = (cpcs[-1] - cpcs[0]) / cpcs[0]
                # CPC crescente pode ser bom (mais valor) ou ruim (mais custo)
                scores["cpc"] = 0.5 + (taxa_cpc * 0.3)
            else:
                scores["cpc"] = 0.5
            
            # Score de concorrência
            concorrencias = [data.concorrencia for data in dados]
            if concorrencias[0] > 0:
                taxa_concorrencia = (concorrencias[-1] - concorrencias[0]) / concorrencias[0]
                # Concorrência menor é melhor
                scores["concorrencia"] = max(0, 0.5 - taxa_concorrencia * 0.5)
            else:
                scores["concorrencia"] = 0.5
            
            # Score de sazonalidade
            sazonal = self._detectar_sazonalidade(dados)
            scores["sazonalidade"] = 0.7 if sazonal else 0.5
            
            # Cálculo do score final
            score_final = sum(scores[fator] * peso for fator, peso in pesos.items())
            
            return round(score_final, 3)
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro no cálculo de score de tendência: {e}")
            return 0.5
    
    def _identificar_padrao(self, dados: List[DadosTemporais]) -> str:
        """Identifica padrão específico nos dados."""
        try:
            if len(dados) < 3:
                return "Dados insuficientes"
            
            volumes = [data.volume_busca for data in dados]
            
            # Análise de tendência linear
            if len(volumes) >= 3:
                # Calcular variação entre pontos consecutivos
                variacoes = [volumes[index+1] - volumes[index] for index in range(len(volumes)-1)]
                
                # Padrão crescente consistente
                if all(value > 0 for value in variacoes):
                    return "Crescimento consistente"
                
                # Padrão decrescente consistente
                if all(value < 0 for value in variacoes):
                    return "Declínio consistente"
                
                # Padrão oscilante
                if any(value > 0 for value in variacoes) and any(value < 0 for value in variacoes):
                    return "Padrão oscilante"
                
                # Padrão estável
                if all(abs(value) < max(volumes) * 0.1 for value in variacoes):
                    return "Padrão estável"
            
            # Análise de sazonalidade
            if self._detectar_sazonalidade(dados):
                return "Padrão sazonal detectado"
            
            return "Padrão não identificado"
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro na identificação de padrão: {e}")
            return "Erro na análise"
    
    def _detectar_sazonalidade(self, dados: List[DadosTemporais]) -> bool:
        """Detecta se há padrão sazonal nos dados."""
        try:
            if len(dados) < 12:  # Mínimo 12 meses para detectar sazonalidade
                return False
            
            volumes = [data.volume_busca for data in dados]
            
            # Análise simples de sazonalidade
            # Verificar se há padrão repetitivo
            if len(volumes) >= 12:
                # Dividir em períodos e comparar
                periodo_1 = volumes[:6]
                periodo_2 = volumes[6:12] if len(volumes) >= 12 else volumes[6:]
                
                if len(periodo_2) >= 6:
                    # Calcular correlação entre períodos
                    correlacao = np.corrcoef(periodo_1[:len(periodo_2)], periodo_2)[0, 1]
                    return correlacao > 0.7  # Alta correlação indica sazonalidade
            
            return False
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro na detecção de sazonalidade: {e}")
            return False
    
    def _calcular_confianca_tendencia(self, dados: List[DadosTemporais]) -> float:
        """Calcula nível de confiança da análise de tendência."""
        try:
            if len(dados) < 2:
                return 0.0
            
            # Fatores de confiança
            fator_quantidade = min(1.0, len(dados) / 30)  # Mais dados = mais confiança
            fator_consistencia = self._calcular_consistencia_dados(dados)
            fator_recencia = self._calcular_recencia_dados(dados)
            
            # Cálculo final
            confianca = (
                fator_quantidade * 0.4 +
                fator_consistencia * 0.4 +
                fator_recencia * 0.2
            )
            
            return round(confianca, 3)
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro no cálculo de confiança: {e}")
            return 0.5
    
    def _calcular_consistencia_dados(self, dados: List[DadosTemporais]) -> float:
        """Calcula consistência dos dados."""
        try:
            if len(dados) < 2:
                return 0.0
            
            volumes = [data.volume_busca for data in dados]
            
            # Calcular desvio padrão normalizado
            media = np.mean(volumes)
            if media == 0:
                return 0.0
            
            desvio = np.std(volumes)
            cv = desvio / media  # Coeficiente de variação
            
            # Consistência inversamente proporcional ao CV
            consistencia = max(0, 1 - cv)
            
            return consistencia
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro no cálculo de consistência: {e}")
            return 0.5
    
    def _calcular_recencia_dados(self, dados: List[DadosTemporais]) -> float:
        """Calcula recência dos dados."""
        try:
            if not dados:
                return 0.0
            
            # Verificar se os dados mais recentes são recentes
            dados_mais_recente = max(dados, key=lambda value: value.data)
            dias_atras = (datetime.now() - dados_mais_recente.data).days
            
            # Recência inversamente proporcional aos dias atrás
            recencia = max(0, 1 - (dias_atras / 30))  # 30 dias como referência
            
            return recencia
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro no cálculo de recência: {e}")
            return 0.5
    
    def _predizer_proximo_mes(self, dados: List[DadosTemporais]) -> Optional[Dict[str, Any]]:
        """Prediz valores para o próximo mês."""
        try:
            if len(dados) < 3:
                return None
            
            volumes = [data.volume_busca for data in dados]
            cpcs = [data.cpc for data in dados]
            
            # Predição simples usando média móvel
            if len(volumes) >= 3:
                # Média dos últimos 3 valores
                predicao_volume = sum(volumes[-3:]) / 3
                predicao_cpc = sum(cpcs[-3:]) / 3 if cpcs else 0
                
                # Calcular intervalo de confiança simples
                desvio_volume = np.std(volumes[-3:])
                intervalo_volume = (predicao_volume - desvio_volume, predicao_volume + desvio_volume)
                
                return {
                    "volume_busca": round(predicao_volume),
                    "cpc": round(predicao_cpc, 2),
                    "intervalo_volume": (round(intervalo_volume[0]), round(intervalo_volume[1])),
                    "confianca": 0.7,
                    "metodo": "media_movel"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro na predição: {e}")
            return None
    
    def detectar_tendencias_emergentes(self, periodo_dias: int = 30) -> List[TendenciaEmergente]:
        """
        Detecta tendências emergentes no período especificado.
        
        Args:
            periodo_dias: Período em dias para análise
            
        Returns:
            List[TendenciaEmergente]: Lista de tendências emergentes
        """
        try:
            tendencias_emergentes = []
            data_limite = datetime.now() - timedelta(days=periodo_dias)
            
            for keyword, dados in self.dados_historicos.items():
                if len(dados) < 2:
                    continue
                
                # Filtrar dados do período
                dados_periodo = [data for data in dados if data.data >= data_limite]
                if len(dados_periodo) < 2:
                    continue
                
                # Calcular taxa de crescimento
                volumes = [data.volume_busca for data in dados_periodo]
                if volumes[0] > 0:
                    taxa_crescimento = (volumes[-1] - volumes[0]) / volumes[0]
                else:
                    continue
                
                # Verificar se é emergente
                threshold_emergencia = self.config["thresholds_tendencia"]["emergencia"]
                if taxa_crescimento >= threshold_emergencia:
                    # Detectar nicho relacionado
                    nicho = self._detectar_nicho_keyword(keyword)
                    
                    # Fatores de emergência
                    fatores = self._identificar_fatores_emergencia(dados_periodo)
                    
                    # Calcular score de emergência
                    score_emergencia = self._calcular_score_emergencia(taxa_crescimento, fatores)
                    
                    # Criar tendência emergente
                    tendencia = TendenciaEmergente(
                        keyword=keyword,
                        score_emergencia=score_emergencia,
                        taxa_crescimento=taxa_crescimento,
                        volume_atual=volumes[-1],
                        volume_anterior=volumes[0],
                        fatores_emergencia=fatores,
                        nicho_relacionado=nicho,
                        timestamp_deteccao=datetime.now(),
                        confianca=0.8
                    )
                    
                    tendencias_emergentes.append(tendencia)
            
            # Ordenar por score de emergência
            tendencias_emergentes.sort(key=lambda value: value.score_emergencia, reverse=True)
            
            # Atualizar lista global
            self.tendencias_emergentes = tendencias_emergentes
            
            logger.info(f"[{self.tracing_id}] {len(tendencias_emergentes)} tendências emergentes detectadas")
            return tendencias_emergentes
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro na detecção de tendências emergentes: {e}")
            return []
    
    def _detectar_nicho_keyword(self, keyword: str) -> str:
        """Detecta nicho relacionado à keyword."""
        try:
            keyword_lower = keyword.lower()
            
            nichos = {
                "ecommerce": ["preço", "comprar", "vender", "promoção", "desconto"],
                "saude": ["sintomas", "tratamento", "medicamento", "consulta"],
                "tecnologia": ["tutorial", "configuração", "problema", "solução"],
                "educacao": ["curso", "aprendizado", "estudo", "material"],
                "financas": ["investimento", "economia", "poupança", "rendimento"]
            }
            
            for nicho, palavras in nichos.items():
                if any(palavra in keyword_lower for palavra in palavras):
                    return nicho
            
            return "generico"
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro na detecção de nicho: {e}")
            return "generico"
    
    def _identificar_fatores_emergencia(self, dados: List[DadosTemporais]) -> List[str]:
        """Identifica fatores que contribuem para a emergência."""
        fatores = []
        
        try:
            if len(dados) < 2:
                return fatores
            
            # Fator de crescimento de volume
            volumes = [data.volume_busca for data in dados]
            if volumes[-1] > volumes[0] * 1.5:
                fatores.append("Crescimento explosivo de volume")
            
            # Fator de aumento de CPC
            cpcs = [data.cpc for data in dados]
            if cpcs and cpcs[-1] > cpcs[0] * 1.3:
                fatores.append("Aumento significativo de CPC")
            
            # Fator de redução de concorrência
            concorrencias = [data.concorrencia for data in dados]
            if concorrencias and concorrencias[-1] < concorrencias[0] * 0.8:
                fatores.append("Redução de concorrência")
            
            # Fator de sazonalidade
            if self._detectar_sazonalidade(dados):
                fatores.append("Padrão sazonal favorável")
            
            return fatores
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro na identificação de fatores: {e}")
            return fatores
    
    def _calcular_score_emergencia(self, taxa_crescimento: float, fatores: List[str]) -> float:
        """Calcula score de emergência."""
        try:
            # Score base na taxa de crescimento
            score_base = min(1.0, taxa_crescimento)
            
            # Bônus por fatores
            bonus_fatores = len(fatores) * 0.1
            
            # Score final
            score_final = min(1.0, score_base + bonus_fatores)
            
            return round(score_final, 3)
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro no cálculo de score de emergência: {e}")
            return 0.5
    
    def gerar_relatorio_tendencias(self, periodo: str = "medio_prazo") -> Dict[str, Any]:
        """
        Gera relatório completo de tendências.
        
        Args:
            periodo: Período de análise
            
        Returns:
            Dict com relatório completo
        """
        try:
            logger.info(f"[{self.tracing_id}] Gerando relatório de tendências")
            
            # Analisar todas as keywords
            analises = []
            for keyword in self.dados_historicos.keys():
                analise = self.analisar_tendencia(keyword, periodo)
                if analise:
                    analises.append(analise)
            
            # Detectar tendências emergentes
            tendencias_emergentes = self.detectar_tendencias_emergentes()
            
            # Estatísticas por tipo de tendência
            tipos_tendencia = {}
            scores_por_tipo = {}
            
            for analise in analises:
                tipo = analise.tipo_tendencia.value
                if tipo not in tipos_tendencia:
                    tipos_tendencia[tipo] = 0
                    scores_por_tipo[tipo] = []
                
                tipos_tendencia[tipo] += 1
                scores_por_tipo[tipo].append(analise.score_tendencia)
            
            # Cálculo de médias por tipo
            medias_por_tipo = {}
            for tipo, scores in scores_por_tipo.items():
                medias_por_tipo[tipo] = round(sum(scores) / len(scores), 3)
            
            # Análise de nichos
            nichos_analisados = {}
            for analise in analises:
                nicho = self._detectar_nicho_keyword(analise.keyword)
                if nicho not in nichos_analisados:
                    nichos_analisados[nicho] = {"count": 0, "scores": []}
                
                nichos_analisados[nicho]["count"] += 1
                nichos_analisados[nicho]["scores"].append(analise.score_tendencia)
            
            # Cálculo de médias por nicho
            for nicho, dados in nichos_analisados.items():
                dados["score_medio"] = round(sum(dados["scores"]) / len(dados["scores"]), 3)
            
            relatorio = {
                "tracing_id": self.tracing_id,
                "timestamp": datetime.now().isoformat(),
                "periodo_analise": periodo,
                "resumo": {
                    "total_keywords_analisadas": len(analises),
                    "tendencias_emergentes": len(tendencias_emergentes),
                    "score_medio_geral": round(sum(a.score_tendencia for a in analises) / len(analises), 3) if analises else 0
                },
                "distribuicao_por_tipo": {
                    tipo: {
                        "count": count,
                        "score_medio": medias_por_tipo.get(tipo, 0)
                    }
                    for tipo, count in tipos_tendencia.items()
                },
                "analise_por_nicho": nichos_analisados,
                "tendencias_emergentes": [
                    {
                        "keyword": t.keyword,
                        "score_emergencia": t.score_emergencia,
                        "taxa_crescimento": t.taxa_crescimento,
                        "nicho": t.nicho_relacionado,
                        "fatores": t.fatores_emergencia
                    }
                    for t in tendencias_emergentes[:10]  # Top 10
                ],
                "analises_detalhadas": [
                    {
                        "keyword": a.keyword,
                        "tipo_tendencia": a.tipo_tendencia.value,
                        "score_tendencia": a.score_tendencia,
                        "confianca": a.confianca,
                        "padrao": a.padrao_detectado,
                        "predicao": a.predicao_proximo_mes
                    }
                    for a in analises
                ]
            }
            
            logger.info(f"[{self.tracing_id}] Relatório de tendências gerado")
            return relatorio
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro ao gerar relatório: {e}")
            raise

# Funções de conveniência
def analisar_tendencia_keyword(
    keyword: str,
    dados_temporais: List[Dict[str, Any]],
    periodo: str = "medio_prazo",
    config_path: Optional[str] = None
) -> Optional[AnaliseTendencia]:
    """
    Função de conveniência para análise de tendência.
    
    Args:
        keyword: Keyword a ser analisada
        dados_temporais: Lista de dados temporais
        periodo: Período de análise
        config_path: Caminho para configuração
        
    Returns:
        AnaliseTendencia: Análise de tendência
    """
    sistema = SistemaTendenciasCaudaLonga(config_path)
    
    # Adicionar dados
    for dados in dados_temporais:
        sistema.adicionar_dados_temporais(keyword, dados)
    
    # Analisar tendência
    return sistema.analisar_tendencia(keyword, periodo)

def detectar_tendencias_emergentes(
    dados_por_keyword: Dict[str, List[Dict[str, Any]]],
    periodo_dias: int = 30,
    config_path: Optional[str] = None
) -> List[TendenciaEmergente]:
    """
    Função de conveniência para detecção de tendências emergentes.
    
    Args:
        dados_por_keyword: Dados organizados por keyword
        periodo_dias: Período em dias
        config_path: Caminho para configuração
        
    Returns:
        List[TendenciaEmergente]: Tendências emergentes detectadas
    """
    sistema = SistemaTendenciasCaudaLonga(config_path)
    
    # Adicionar dados
    for keyword, dados_lista in dados_por_keyword.items():
        for dados in dados_lista:
            sistema.adicionar_dados_temporais(keyword, dados)
    
    # Detectar tendências emergentes
    return sistema.detectar_tendencias_emergentes(periodo_dias)

if __name__ == "__main__":
    # Teste básico do sistema de tendências
    sistema = SistemaTendenciasCaudaLonga()
    
    # Dados de teste simulados
    keywords_teste = [
        "melhor preço notebook gaming 2024",
        "como fazer backup automático windows 11",
        "sintomas de diabetes tipo 2 em adultos"
    ]
    
    # Simular dados temporais
    for keyword in keywords_teste:
        for index in range(10):
            dados = DadosTemporais(
                data=datetime.now() - timedelta(days=30-index*3),
                volume_busca=100 + index*20 + np.random.randint(-10, 10),
                cpc=2.0 + index*0.1 + np.random.uniform(-0.2, 0.2),
                concorrencia=0.6 + index*0.02 + np.random.uniform(-0.1, 0.1),
                posicao_serp=10 + index,
                cliques=50 + index*5,
                impressoes=1000 + index*100
            )
            sistema.adicionar_dados_temporais(keyword, dados)
    
    print("=== TESTE DO SISTEMA DE TENDÊNCIAS ===")
    
    # Analisar tendências
    for keyword in keywords_teste:
        analise = sistema.analisar_tendencia(keyword)
        if analise:
            print(f"\nKeyword: {keyword}")
            print(f"Tipo de tendência: {analise.tipo_tendencia.value}")
            print(f"Score: {analise.score_tendencia}")
            print(f"Confiança: {analise.confianca}")
            print(f"Padrão: {analise.padrao_detectado}")
    
    # Detectar tendências emergentes
    tendencias_emergentes = sistema.detectar_tendencias_emergentes()
    print(f"\nTendências emergentes detectadas: {len(tendencias_emergentes)}")
    
    # Gerar relatório
    relatorio = sistema.gerar_relatorio_tendencias()
    print(f"\n=== RELATÓRIO ===")
    print(f"Total analisadas: {relatorio['resumo']['total_keywords_analisadas']}")
    print(f"Tendências emergentes: {relatorio['resumo']['tendencias_emergentes']}")
    print(f"Score médio: {relatorio['resumo']['score_medio_geral']}") 