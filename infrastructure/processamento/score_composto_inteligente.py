"""
Score Composto Inteligente - Omni Keywords Finder
Tracing ID: LONGTAIL-006
Data/Hora: 2024-12-20 17:05:00 UTC
Versão: 1.0
Status: IMPLEMENTADO

Sistema completo de score composto que combina múltiplos fatores para avaliar
a qualidade de keywords de cauda longa de forma inteligente e adaptativa.
"""

import json
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from enum import Enum

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TipoScore(Enum):
    """Tipos de score disponíveis."""
    COMPLEXIDADE = "complexidade"
    ESPECIFICIDADE = "especificidade"
    COMPETITIVO = "competitivo"
    TENDA = "tendencia"
    COMPOSTO = "composto"

@dataclass
class ScoreComponente:
    """Estrutura para score de componente individual."""
    tipo: TipoScore
    valor: float
    peso: float
    peso_normalizado: float
    descricao: str
    timestamp: datetime

@dataclass
class ScoreComposto:
    """Estrutura para score composto final."""
    keyword: str
    score_final: float
    componentes: Dict[str, ScoreComponente]
    classificacao: str
    confianca: float
    timestamp: datetime
    tracing_id: str
    metadados: Dict[str, Any]

class ScoreCompostoInteligente:
    """
    Sistema de score composto inteligente para keywords de cauda longa.
    
    Combina múltiplos fatores:
    - Score de complexidade (30%)
    - Score de especificidade (25%)
    - Score competitivo (25%)
    - Score de tendência (20%)
    
    Com ponderação inteligente baseada em contexto e nicho.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa o sistema de score composto.
        
        Args:
            config_path: Caminho para arquivo de configuração
        """
        self.tracing_id = f"LONGTAIL-006_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.config = self._carregar_configuracao(config_path)
        self.pesos_padrao = self._definir_pesos_padrao()
        self.classificacoes = self._definir_classificacoes()
        
        logger.info(f"[{self.tracing_id}] Sistema de score composto inicializado")
    
    def _carregar_configuracao(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Carrega configuração do sistema de score."""
        config_padrao = {
            "pesos_padrao": {
                "complexidade": 0.30,
                "especificidade": 0.25,
                "competitivo": 0.25,
                "tendencia": 0.20
            },
            "thresholds_classificacao": {
                "excelente": 0.85,
                "muito_bom": 0.75,
                "bom": 0.65,
                "regular": 0.50,
                "ruim": 0.0
            },
            "pesos_por_nicho": {
                "ecommerce": {
                    "complexidade": 0.25,
                    "especificidade": 0.30,
                    "competitivo": 0.30,
                    "tendencia": 0.15
                },
                "saude": {
                    "complexidade": 0.35,
                    "especificidade": 0.30,
                    "competitivo": 0.20,
                    "tendencia": 0.15
                },
                "tecnologia": {
                    "complexidade": 0.30,
                    "especificidade": 0.25,
                    "competitivo": 0.25,
                    "tendencia": 0.20
                },
                "educacao": {
                    "complexidade": 0.25,
                    "especificidade": 0.35,
                    "competitivo": 0.25,
                    "tendencia": 0.15
                },
                "financas": {
                    "complexidade": 0.30,
                    "especificidade": 0.25,
                    "competitivo": 0.30,
                    "tendencia": 0.15
                }
            },
            "fatores_ajuste": {
                "volume_busca": 0.1,
                "cpc": 0.1,
                "concorrencia": 0.1,
                "sazonalidade": 0.05
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
    
    def _definir_pesos_padrao(self) -> Dict[str, float]:
        """Define pesos padrão para os componentes do score."""
        return self.config["pesos_padrao"]
    
    def _definir_classificacoes(self) -> Dict[str, float]:
        """Define thresholds para classificações de qualidade."""
        return self.config["thresholds_classificacao"]
    
    def calcular_score_complexidade(self, keyword: str, dados_adicionais: Optional[Dict] = None) -> ScoreComponente:
        """
        Calcula score de complexidade da keyword.
        
        Fatores considerados:
        - Número de palavras
        - Comprimento das palavras
        - Estrutura gramatical
        - Presença de termos técnicos
        """
        try:
            palavras = keyword.lower().split()
            
            # Fator 1: Número de palavras (3-8 palavras é ideal)
            num_palavras = len(palavras)
            if num_palavras < 3:
                score_palavras = 0.3
            elif 3 <= num_palavras <= 8:
                score_palavras = 1.0
            else:
                score_palavras = max(0.5, 1.0 - (num_palavras - 8) * 0.1)
            
            # Fator 2: Comprimento médio das palavras
            comprimentos = [len(p) for p in palavras if len(p) > 2]
            if comprimentos:
                comp_medio = np.mean(comprimentos)
                score_comprimento = min(1.0, comp_medio / 8)
            else:
                score_comprimento = 0.5
            
            # Fator 3: Palavras longas (>6 caracteres)
            palavras_longas = [p for p in palavras if len(p) > 6]
            score_palavras_longas = min(1.0, len(palavras_longas) / 3)
            
            # Fator 4: Estrutura gramatical (presença de preposições, artigos)
            preposicoes = ['de', 'da', 'do', 'em', 'na', 'no', 'para', 'com', 'sem']
            artigos = ['o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas']
            estruturais = [p for p in palavras if p in preposicoes + artigos]
            score_estrutura = min(1.0, len(estruturais) / 4)
            
            # Cálculo final
            score_final = (
                score_palavras * 0.3 +
                score_comprimento * 0.25 +
                score_palavras_longas * 0.25 +
                score_estrutura * 0.2
            )
            
            return ScoreComponente(
                tipo=TipoScore.COMPLEXIDADE,
                valor=round(score_final, 3),
                peso=self.pesos_padrao["complexidade"],
                peso_normalizado=self.pesos_padrao["complexidade"],
                descricao=f"Complexidade baseada em {num_palavras} palavras, {len(palavras_longas)} longas",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro no cálculo de complexidade: {e}")
            return ScoreComponente(
                tipo=TipoScore.COMPLEXIDADE,
                valor=0.5,
                peso=self.pesos_padrao["complexidade"],
                peso_normalizado=self.pesos_padrao["complexidade"],
                descricao="Erro no cálculo - valor padrão",
                timestamp=datetime.now()
            )
    
    def calcular_score_especificidade(self, keyword: str, nicho: Optional[str] = None) -> ScoreComponente:
        """
        Calcula score de especificidade da keyword.
        
        Fatores considerados:
        - Palavras específicas do nicho
        - Termos técnicos
        - Modificadores específicos
        - Ausência de termos genéricos
        """
        try:
            palavras = keyword.lower().split()
            
            # Palavras específicas por nicho
            palavras_especificas_por_nicho = {
                "ecommerce": ["preço", "barato", "promoção", "desconto", "oferta", "comprar", "vender"],
                "saude": ["sintomas", "tratamento", "medicamento", "consulta", "exame", "diagnóstico"],
                "tecnologia": ["tutorial", "configuração", "otimização", "resolução", "problema", "solução"],
                "educacao": ["curso", "aprendizado", "estudo", "material", "exercício", "prática"],
                "financas": ["investimento", "economia", "poupança", "rendimento", "risco", "retorno"]
            }
            
            # Palavras genéricas a serem evitadas
            palavras_genericas = ["coisa", "item", "produto", "serviço", "informação", "dados"]
            
            # Cálculo de especificidade
            score_especificas = 0
            if nicho and nicho in palavras_especificas_por_nicho:
                palavras_especificas = palavras_especificas_por_nicho[nicho]
                encontradas = sum(1 for p in palavras if p in palavras_especificas)
                score_especificas = min(1.0, encontradas / 3)
            else:
                # Análise genérica de especificidade
                palavras_tecnicas = [p for p in palavras if len(p) > 6]
                score_especificas = min(1.0, len(palavras_tecnicas) / 3)
            
            # Penalização por palavras genéricas
            palavras_genericas_encontradas = sum(1 for p in palavras if p in palavras_genericas)
            penalizacao_genericas = max(0, palavras_genericas_encontradas * 0.2)
            
            # Score final
            score_final = max(0, score_especificas - penalizacao_genericas)
            
            return ScoreComponente(
                tipo=TipoScore.ESPECIFICIDADE,
                valor=round(score_final, 3),
                peso=self.pesos_padrao["especificidade"],
                peso_normalizado=self.pesos_padrao["especificidade"],
                descricao=f"Especificidade baseada em palavras técnicas e nicho {nicho or 'genérico'}",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro no cálculo de especificidade: {e}")
            return ScoreComponente(
                tipo=TipoScore.ESPECIFICIDADE,
                valor=0.5,
                peso=self.pesos_padrao["especificidade"],
                peso_normalizado=self.pesos_padrao["especificidade"],
                descricao="Erro no cálculo - valor padrão",
                timestamp=datetime.now()
            )
    
    def calcular_score_competitivo(self, dados_mercado: Dict[str, Any]) -> ScoreComponente:
        """
        Calcula score competitivo baseado em dados de mercado.
        
        Fatores considerados:
        - Volume de busca
        - CPC (Custo por Clique)
        - Nível de concorrência
        - Oportunidade de mercado
        """
        try:
            volume = dados_mercado.get('volume_busca', 0)
            cpc = dados_mercado.get('cpc', 0)
            concorrencia = dados_mercado.get('concorrencia', 0.5)
            
            # Normalização dos valores
            # Volume: 0-1000+ (ideal: 100-1000)
            if volume == 0:
                score_volume = 0
            elif 100 <= volume <= 1000:
                score_volume = 1.0
            elif volume < 100:
                score_volume = volume / 100
            else:
                score_volume = max(0.5, 1.0 - (volume - 1000) / 10000)
            
            # CPC: 0-10+ (ideal: 1-5)
            if cpc == 0:
                score_cpc = 0.5
            elif 1 <= cpc <= 5:
                score_cpc = 1.0
            elif cpc < 1:
                score_cpc = 0.7
            else:
                score_cpc = max(0.3, 1.0 - (cpc - 5) / 10)
            
            # Concorrência: 0-1 (menor é melhor)
            score_concorrencia = 1.0 - concorrencia
            
            # Cálculo final
            score_final = (
                score_volume * 0.4 +
                score_cpc * 0.4 +
                score_concorrencia * 0.2
            )
            
            return ScoreComponente(
                tipo=TipoScore.COMPETITIVO,
                valor=round(score_final, 3),
                peso=self.pesos_padrao["competitivo"],
                peso_normalizado=self.pesos_padrao["competitivo"],
                descricao=f"Competitivo: volume={volume}, cpc={cpc}, concorrência={concorrencia}",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro no cálculo competitivo: {e}")
            return ScoreComponente(
                tipo=TipoScore.COMPETITIVO,
                valor=0.5,
                peso=self.pesos_padrao["competitivo"],
                peso_normalizado=self.pesos_padrao["competitivo"],
                descricao="Erro no cálculo - valor padrão",
                timestamp=datetime.now()
            )
    
    def calcular_score_tendencia(self, dados_tendencia: Dict[str, Any]) -> ScoreComponente:
        """
        Calcula score de tendência baseado em dados temporais.
        
        Fatores considerados:
        - Crescimento de volume
        - Sazonalidade
        - Tendência de mercado
        - Novidade da keyword
        """
        try:
            crescimento_volume = dados_tendencia.get('crescimento_volume', 0)
            sazonalidade = dados_tendencia.get('sazonalidade', 0.5)
            tendencia_mercado = dados_tendencia.get('tendencia_mercado', 0.5)
            novidade = dados_tendencia.get('novidade', 0.5)
            
            # Score de crescimento (0-100%)
            score_crescimento = min(1.0, max(0, crescimento_volume / 100))
            
            # Score de sazonalidade (0-1, onde 1 é alta sazonalidade)
            score_sazonalidade = sazonalidade
            
            # Score de tendência de mercado (0-1)
            score_tendencia_mercado = tendencia_mercado
            
            # Score de novidade (0-1)
            score_novidade = novidade
            
            # Cálculo final (crescimento e novidade são mais importantes)
            score_final = (
                score_crescimento * 0.4 +
                score_novidade * 0.3 +
                score_tendencia_mercado * 0.2 +
                score_sazonalidade * 0.1
            )
            
            return ScoreComponente(
                tipo=TipoScore.TENDA,
                valor=round(score_final, 3),
                peso=self.pesos_padrao["tendencia"],
                peso_normalizado=self.pesos_padrao["tendencia"],
                descricao=f"Tendência: crescimento={crescimento_volume}%, novidade={novidade}",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro no cálculo de tendência: {e}")
            return ScoreComponente(
                tipo=TipoScore.TENDA,
                valor=0.5,
                peso=self.pesos_padrao["tendencia"],
                peso_normalizado=self.pesos_padrao["tendencia"],
                descricao="Erro no cálculo - valor padrão",
                timestamp=datetime.now()
            )
    
    def calcular_score_composto(
        self, 
        keyword: str, 
        dados_mercado: Optional[Dict[str, Any]] = None,
        dados_tendencia: Optional[Dict[str, Any]] = None,
        nicho: Optional[str] = None
    ) -> ScoreComposto:
        """
        Calcula score composto final combinando todos os componentes.
        
        Args:
            keyword: Keyword a ser analisada
            dados_mercado: Dados de mercado (volume, CPC, concorrência)
            dados_tendencia: Dados de tendência temporal
            nicho: Nicho de mercado
            
        Returns:
            ScoreComposto: Score composto final
        """
        try:
            logger.info(f"[{self.tracing_id}] Calculando score composto para: {keyword}")
            
            # Dados padrão se não fornecidos
            dados_mercado = dados_mercado or {
                'volume_busca': 500,
                'cpc': 2.5,
                'concorrencia': 0.6
            }
            
            dados_tendencia = dados_tendencia or {
                'crescimento_volume': 10,
                'sazonalidade': 0.3,
                'tendencia_mercado': 0.7,
                'novidade': 0.6
            }
            
            # Cálculo dos componentes
            score_complexidade = self.calcular_score_complexidade(keyword)
            score_especificidade = self.calcular_score_especificidade(keyword, nicho)
            score_competitivo = self.calcular_score_competitivo(dados_mercado)
            score_tendencia = self.calcular_score_tendencia(dados_tendencia)
            
            # Ajuste de pesos por nicho
            if nicho and nicho in self.config["pesos_por_nicho"]:
                pesos_nicho = self.config["pesos_por_nicho"][nicho]
                score_complexidade.peso_normalizado = pesos_nicho["complexidade"]
                score_especificidade.peso_normalizado = pesos_nicho["especificidade"]
                score_competitivo.peso_normalizado = pesos_nicho["competitivo"]
                score_tendencia.peso_normalizado = pesos_nicho["tendencia"]
            
            # Cálculo do score final
            score_final = (
                score_complexidade.valor * score_complexidade.peso_normalizado +
                score_especificidade.valor * score_especificidade.peso_normalizado +
                score_competitivo.valor * score_competitivo.peso_normalizado +
                score_tendencia.valor * score_tendencia.peso_normalizado
            )
            
            # Classificação
            classificacao = self._classificar_score(score_final)
            
            # Cálculo de confiança
            confianca = self._calcular_confianca([
                score_complexidade.valor,
                score_especificidade.valor,
                score_competitivo.valor,
                score_tendencia.valor
            ])
            
            # Metadados
            metadados = {
                "nicho": nicho,
                "dados_mercado": dados_mercado,
                "dados_tendencia": dados_tendencia,
                "pesos_utilizados": {
                    "complexidade": score_complexidade.peso_normalizado,
                    "especificidade": score_especificidade.peso_normalizado,
                    "competitivo": score_competitivo.peso_normalizado,
                    "tendencia": score_tendencia.peso_normalizado
                }
            }
            
            # Criação do resultado
            componentes = {
                "complexidade": score_complexidade,
                "especificidade": score_especificidade,
                "competitivo": score_competitivo,
                "tendencia": score_tendencia
            }
            
            resultado = ScoreComposto(
                keyword=keyword,
                score_final=round(score_final, 3),
                componentes=componentes,
                classificacao=classificacao,
                confianca=round(confianca, 3),
                timestamp=datetime.now(),
                tracing_id=self.tracing_id,
                metadados=metadados
            )
            
            logger.info(f"[{self.tracing_id}] Score composto calculado: {score_final:.3f} ({classificacao})")
            return resultado
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro no cálculo do score composto: {e}")
            raise
    
    def _classificar_score(self, score: float) -> str:
        """Classifica o score final em categorias de qualidade."""
        thresholds = self.classificacoes
        
        if score >= thresholds["excelente"]:
            return "excelente"
        elif score >= thresholds["muito_bom"]:
            return "muito_bom"
        elif score >= thresholds["bom"]:
            return "bom"
        elif score >= thresholds["regular"]:
            return "regular"
        else:
            return "ruim"
    
    def _calcular_confianca(self, scores: List[float]) -> float:
        """
        Calcula nível de confiança baseado na consistência dos scores.
        
        Quanto mais próximos os scores, maior a confiança.
        """
        if not scores:
            return 0.5
        
        # Desvio padrão normalizado
        desvio = np.std(scores)
        media = np.mean(scores)
        
        if media == 0:
            return 0.5
        
        # Coeficiente de variação
        cv = desvio / media
        
        # Confiança inversamente proporcional ao CV
        confianca = max(0.1, 1.0 - cv)
        
        return confianca
    
    def validar_keyword_score(self, keyword: str, score_minimo: float = 0.7) -> Dict[str, Any]:
        """
        Valida se uma keyword atende ao score mínimo.
        
        Args:
            keyword: Keyword a ser validada
            score_minimo: Score mínimo para aprovação
            
        Returns:
            Dict com resultado da validação
        """
        try:
            score_composto = self.calcular_score_composto(keyword)
            
            aprovada = score_composto.score_final >= score_minimo
            
            resultado = {
                "keyword": keyword,
                "aprovada": aprovada,
                "score_final": score_composto.score_final,
                "classificacao": score_composto.classificacao,
                "confianca": score_composto.confianca,
                "componentes": {
                    nome: {
                        "valor": comp.valor,
                        "peso": comp.peso_normalizado,
                        "descricao": comp.descricao
                    }
                    for nome, comp in score_composto.componentes.items()
                },
                "timestamp": score_composto.timestamp.isoformat(),
                "tracing_id": score_composto.tracing_id
            }
            
            logger.info(f"[{self.tracing_id}] Validação concluída - Aprovada: {aprovada}")
            return resultado
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro na validação: {e}")
            raise
    
    def gerar_relatorio_scores(self, keywords: List[str], dados_mercado: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Gera relatório de scores para múltiplas keywords.
        
        Args:
            keywords: Lista de keywords
            dados_mercado: Dados de mercado (opcional)
            
        Returns:
            Dict com relatório completo
        """
        try:
            logger.info(f"[{self.tracing_id}] Gerando relatório para {len(keywords)} keywords")
            
            scores = []
            aprovadas = 0
            classificacoes = {}
            
            for keyword in keywords:
                try:
                    score = self.calcular_score_composto(keyword, dados_mercado)
                    scores.append(score)
                    
                    if score.score_final >= 0.7:
                        aprovadas += 1
                    
                    if score.classificacao not in classificacoes:
                        classificacoes[score.classificacao] = 0
                    classificacoes[score.classificacao] += 1
                    
                except Exception as e:
                    logger.warning(f"[{self.tracing_id}] Erro ao analisar '{keyword}': {e}")
            
            # Estatísticas
            scores_finais = [string_data.score_final for string_data in scores]
            estatisticas = {
                "total_keywords": len(keywords),
                "analisadas_com_sucesso": len(scores),
                "aprovadas": aprovadas,
                "taxa_aprovacao": round(aprovadas / len(scores) * 100, 2) if scores else 0,
                "score_medio": round(np.mean(scores_finais), 3) if scores_finais else 0,
                "score_mediano": round(np.median(scores_finais), 3) if scores_finais else 0,
                "score_minimo": round(min(scores_finais), 3) if scores_finais else 0,
                "score_maximo": round(max(scores_finais), 3) if scores_finais else 0,
                "classificacoes": classificacoes
            }
            
            # Análise por componente
            analise_componentes = {}
            for nome_componente in ["complexidade", "especificidade", "competitivo", "tendencia"]:
                valores = [string_data.componentes[nome_componente].valor for string_data in scores]
                analise_componentes[nome_componente] = {
                    "media": round(np.mean(valores), 3),
                    "mediana": round(np.median(valores), 3),
                    "minimo": round(min(valores), 3),
                    "maximo": round(max(valores), 3)
                }
            
            relatorio = {
                "tracing_id": self.tracing_id,
                "timestamp": datetime.now().isoformat(),
                "estatisticas": estatisticas,
                "analise_componentes": analise_componentes,
                "scores_detalhados": [
                    {
                        "keyword": string_data.keyword,
                        "score_final": string_data.score_final,
                        "classificacao": string_data.classificacao,
                        "confianca": string_data.confianca,
                        "componentes": {
                            nome: comp.valor for nome, comp in string_data.componentes.items()
                        }
                    }
                    for string_data in scores
                ]
            }
            
            logger.info(f"[{self.tracing_id}] Relatório gerado com sucesso")
            return relatorio
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro ao gerar relatório: {e}")
            raise

# Funções de conveniência
def calcular_score_composto(
    keyword: str, 
    dados_mercado: Optional[Dict[str, Any]] = None,
    dados_tendencia: Optional[Dict[str, Any]] = None,
    nicho: Optional[str] = None,
    config_path: Optional[str] = None
) -> ScoreComposto:
    """
    Função de conveniência para cálculo rápido de score composto.
    
    Args:
        keyword: Keyword a ser analisada
        dados_mercado: Dados de mercado
        dados_tendencia: Dados de tendência
        nicho: Nicho de mercado
        config_path: Caminho para configuração
        
    Returns:
        ScoreComposto: Score composto calculado
    """
    sistema = ScoreCompostoInteligente(config_path)
    return sistema.calcular_score_composto(keyword, dados_mercado, dados_tendencia, nicho)

def validar_keyword_score(
    keyword: str, 
    score_minimo: float = 0.7,
    config_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Função de conveniência para validação rápida de keyword.
    
    Args:
        keyword: Keyword a ser validada
        score_minimo: Score mínimo para aprovação
        config_path: Caminho para configuração
        
    Returns:
        Dict: Resultado da validação
    """
    sistema = ScoreCompostoInteligente(config_path)
    return sistema.validar_keyword_score(keyword, score_minimo)

if __name__ == "__main__":
    # Teste básico do sistema de score composto
    sistema = ScoreCompostoInteligente()
    
    # Keywords de teste
    keywords_teste = [
        "melhor preço notebook gaming 2024",
        "como fazer backup automático windows 11",
        "sintomas de diabetes tipo 2 em adultos",
        "curso online marketing digital certificado",
        "investimento em criptomoedas para iniciantes"
    ]
    
    # Dados de mercado simulados
    dados_mercado = {
        'volume_busca': 500,
        'cpc': 2.5,
        'concorrencia': 0.6
    }
    
    print("=== TESTE DO SISTEMA DE SCORE COMPOSTO INTELIGENTE ===")
    for keyword in keywords_teste:
        resultado = sistema.validar_keyword_score(keyword)
        print(f"\nKeyword: {keyword}")
        print(f"Aprovada: {resultado['aprovada']}")
        print(f"Score Final: {resultado['score_final']}")
        print(f"Classificação: {resultado['classificacao']}")
        print(f"Confiança: {resultado['confianca']}")
        print("Componentes:")
        for nome, comp in resultado['componentes'].items():
            print(f"  {nome}: {comp['valor']} (peso: {comp['peso']})") 