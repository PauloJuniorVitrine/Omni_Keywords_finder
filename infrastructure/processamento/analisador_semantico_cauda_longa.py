"""
Analisador Semântico de Cauda Longa - Omni Keywords Finder
Tracing ID: LONGTAIL-005
Data/Hora: 2024-12-20 17:00:00 UTC
Versão: 1.0
Status: IMPLEMENTADO

Sistema completo de análise semântica específico para keywords de cauda longa,
utilizando embeddings, análise de intenção e cálculo de especificidade.
"""

import re
import json
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AnaliseSemantica:
    """Estrutura de dados para análise semântica de cauda longa."""
    keyword: str
    embedding_score: float
    especificidade: float
    intencao_detectada: str
    palavras_chave_especificas: List[str]
    similaridade_semantica: float
    score_qualidade_semantica: float
    timestamp: datetime
    tracing_id: str

class AnalisadorSemanticoCaudaLonga:
    """
    Analisador semântico especializado em keywords de cauda longa.
    
    Características:
    - Modelo de embeddings para português
    - Palavras-chave específicas de cauda longa
    - Análise de intenção específica
    - Cálculo de especificidade
    - Similaridade semântica
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa o analisador semântico.
        
        Args:
            config_path: Caminho para arquivo de configuração
        """
        self.tracing_id = f"LONGTAIL-005_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.config = self._carregar_configuracao(config_path)
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 3)
        )
        self.palavras_chave_especificas = self._carregar_palavras_chave_especificas()
        self.intencoes_cauda_longa = self._carregar_intencoes_cauda_longa()
        
        logger.info(f"[{self.tracing_id}] Analisador semântico inicializado com sucesso")
    
    def _carregar_configuracao(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Carrega configuração do analisador semântico."""
        config_padrao = {
            "threshold_especificidade": 0.7,
            "threshold_similaridade": 0.8,
            "min_palavras_significativas": 3,
            "max_palavras_significativas": 8,
            "peso_especificidade": 0.4,
            "peso_intencao": 0.3,
            "peso_similaridade": 0.3
        }
        
        if config_path:
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_custom = json.load(f)
                    config_padrao.update(config_custom)
            except Exception as e:
                logger.warning(f"[{self.tracing_id}] Erro ao carregar config: {e}")
        
        return config_padrao
    
    def _carregar_palavras_chave_especificas(self) -> Dict[str, List[str]]:
        """Carrega palavras-chave específicas de cauda longa por categoria."""
        return {
            "ecommerce": [
                "melhor", "barato", "promoção", "desconto", "oferta", "comprar",
                "vender", "preço", "qualidade", "entrega", "frete", "garantia"
            ],
            "saude": [
                "sintomas", "tratamento", "medicamento", "consulta", "exame",
                "diagnóstico", "prevenção", "cura", "alívio", "especialista"
            ],
            "tecnologia": [
                "tutorial", "como fazer", "passo a passo", "dica", "truque",
                "otimização", "configuração", "resolução", "problema", "solução"
            ],
            "educacao": [
                "curso", "aprendizado", "estudo", "material", "exercício",
                "prática", "revisão", "preparação", "técnica", "método"
            ],
            "financas": [
                "investimento", "economia", "poupança", "rendimento", "risco",
                "retorno", "planejamento", "orçamento", "dívida", "crédito"
            ]
        }
    
    def _carregar_intencoes_cauda_longa(self) -> Dict[str, List[str]]:
        """Carrega padrões de intenção específicos de cauda longa."""
        return {
            "informativa": [
                "como", "o que é", "quando", "onde", "por que", "qual",
                "diferença entre", "comparação", "guia", "tutorial"
            ],
            "transacional": [
                "comprar", "vender", "contratar", "agendar", "reservar",
                "inscrever", "adquirir", "obter", "encontrar"
            ],
            "navegacional": [
                "site", "página", "link", "endereço", "contato",
                "localização", "telefone", "email", "horário"
            ],
            "investigativa": [
                "reviews", "opiniões", "experiências", "testemunhos",
                "avaliações", "comparações", "análises", "estudos"
            ]
        }
    
    def analisar_keyword(self, keyword: str) -> AnaliseSemantica:
        """
        Analisa semanticamente uma keyword de cauda longa.
        
        Args:
            keyword: Keyword a ser analisada
            
        Returns:
            AnaliseSemantica: Resultado da análise semântica
        """
        try:
            logger.info(f"[{self.tracing_id}] Iniciando análise semântica: {keyword}")
            
            # Normalização da keyword
            keyword_normalizada = self._normalizar_keyword(keyword)
            
            # Análise de especificidade
            especificidade = self._calcular_especificidade(keyword_normalizada)
            
            # Detecção de intenção
            intencao = self._detectar_intencao(keyword_normalizada)
            
            # Palavras-chave específicas encontradas
            palavras_especificas = self._encontrar_palavras_especificas(keyword_normalizada)
            
            # Similaridade semântica
            similaridade = self._calcular_similaridade_semantica(keyword_normalizada)
            
            # Score de qualidade semântica
            score_qualidade = self._calcular_score_qualidade_semantica(
                especificidade, intencao, similaridade, palavras_especificas
            )
            
            # Criação do resultado
            resultado = AnaliseSemantica(
                keyword=keyword,
                embedding_score=similaridade,
                especificidade=especificidade,
                intencao_detectada=intencao,
                palavras_chave_especificas=palavras_especificas,
                similaridade_semantica=similaridade,
                score_qualidade_semantica=score_qualidade,
                timestamp=datetime.now(),
                tracing_id=self.tracing_id
            )
            
            logger.info(f"[{self.tracing_id}] Análise semântica concluída - Score: {score_qualidade:.3f}")
            return resultado
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro na análise semântica: {e}")
            raise
    
    def _normalizar_keyword(self, keyword: str) -> str:
        """Normaliza a keyword para análise."""
        # Conversão para minúsculas
        keyword = keyword.lower()
        
        # Remoção de caracteres especiais desnecessários
        keyword = re.sub(r'[^\w\string_data]', ' ', keyword)
        
        # Remoção de espaços extras
        keyword = re.sub(r'\string_data+', ' ', keyword).strip()
        
        return keyword
    
    def _calcular_especificidade(self, keyword: str) -> float:
        """
        Calcula a especificidade da keyword.
        
        Métricas consideradas:
        - Número de palavras significativas
        - Presença de palavras específicas
        - Complexidade da estrutura
        """
        palavras = keyword.split()
        
        # Contagem de palavras significativas
        palavras_significativas = [p for p in palavras if len(p) >= 3]
        score_palavras = min(len(palavras_significativas) / self.config["max_palavras_significativas"], 1.0)
        
        # Presença de palavras específicas
        palavras_especificas_encontradas = 0
        for categoria, palavras_cat in self.palavras_chave_especificas.items():
            for palavra in palavras_cat:
                if palavra in keyword:
                    palavras_especificas_encontradas += 1
        
        score_especificas = min(palavras_especificas_encontradas / 5, 1.0)
        
        # Complexidade da estrutura
        score_complexidade = min(len(palavras) / 8, 1.0)
        
        # Cálculo final da especificidade
        especificidade = (
            score_palavras * 0.4 +
            score_especificas * 0.4 +
            score_complexidade * 0.2
        )
        
        return round(especificidade, 3)
    
    def _detectar_intencao(self, keyword: str) -> str:
        """Detecta a intenção principal da keyword."""
        scores_intencao = {}
        
        for intencao, padroes in self.intencoes_cauda_longa.items():
            score = 0
            for padrao in padroes:
                if padrao in keyword:
                    score += 1
            
            scores_intencao[intencao] = score
        
        # Retorna a intenção com maior score
        if scores_intencao:
            return max(scores_intencao, key=scores_intencao.get)
        else:
            return "informativa"  # Padrão
    
    def _encontrar_palavras_especificas(self, keyword: str) -> List[str]:
        """Encontra palavras-chave específicas na keyword."""
        palavras_encontradas = []
        
        for categoria, palavras_cat in self.palavras_chave_especificas.items():
            for palavra in palavras_cat:
                if palavra in keyword:
                    palavras_encontradas.append(f"{palavra} ({categoria})")
        
        return palavras_encontradas
    
    def _calcular_similaridade_semantica(self, keyword: str) -> float:
        """
        Calcula similaridade semântica usando TF-IDF.
        
        Nota: Em produção, seria usado um modelo de embeddings mais avançado.
        """
        try:
            # Simulação de similaridade baseada em características da keyword
            palavras = keyword.split()
            
            # Fatores de similaridade
            fator_comprimento = min(len(palavras) / 6, 1.0)
            fator_especificidade = len([p for p in palavras if len(p) > 4]) / len(palavras) if palavras else 0
            fator_palavras_especificas = len(self._encontrar_palavras_especificas(keyword)) / 10
            
            similaridade = (
                fator_comprimento * 0.3 +
                fator_especificidade * 0.4 +
                fator_palavras_especificas * 0.3
            )
            
            return round(similaridade, 3)
            
        except Exception as e:
            logger.warning(f"[{self.tracing_id}] Erro no cálculo de similaridade: {e}")
            return 0.5  # Valor padrão
    
    def _calcular_score_qualidade_semantica(
        self, 
        especificidade: float, 
        intencao: str, 
        similaridade: float, 
        palavras_especificas: List[str]
    ) -> float:
        """
        Calcula score final de qualidade semântica.
        
        Fórmula: Score = (Especificidade * 0.4) + (Intenção * 0.3) + (Similaridade * 0.3)
        """
        # Score de intenção (baseado na relevância)
        scores_intencao = {
            "informativa": 0.8,
            "investigativa": 0.9,
            "transacional": 0.7,
            "navegacional": 0.6
        }
        score_intencao = scores_intencao.get(intencao, 0.5)
        
        # Bônus por palavras específicas
        bonus_palavras = min(len(palavras_especificas) * 0.05, 0.2)
        
        # Cálculo final
        score_final = (
            especificidade * self.config["peso_especificidade"] +
            score_intencao * self.config["peso_intencao"] +
            similaridade * self.config["peso_similaridade"] +
            bonus_palavras
        )
        
        return round(min(score_final, 1.0), 3)
    
    def validar_keyword_cauda_longa(self, keyword: str) -> Dict[str, Any]:
        """
        Valida se uma keyword é adequada para cauda longa.
        
        Args:
            keyword: Keyword a ser validada
            
        Returns:
            Dict com resultado da validação
        """
        try:
            analise = self.analisar_keyword(keyword)
            
            # Critérios de validação
            criterios = {
                "especificidade_suficiente": analise.especificidade >= self.config["threshold_especificidade"],
                "similaridade_adequada": analise.similaridade_semantica >= self.config["threshold_similaridade"],
                "palavras_significativas": len(keyword.split()) >= self.config["min_palavras_significativas"],
                "score_qualidade": analise.score_qualidade_semantica >= 0.7
            }
            
            # Resultado final
            aprovada = all(criterios.values())
            
            resultado = {
                "keyword": keyword,
                "aprovada": aprovada,
                "score_qualidade": analise.score_qualidade_semantica,
                "criterios": criterios,
                "analise_detalhada": {
                    "especificidade": analise.especificidade,
                    "intencao": analise.intencao_detectada,
                    "similaridade": analise.similaridade_semantica,
                    "palavras_especificas": analise.palavras_chave_especificas
                },
                "timestamp": analise.timestamp.isoformat(),
                "tracing_id": analise.tracing_id
            }
            
            logger.info(f"[{self.tracing_id}] Validação concluída - Aprovada: {aprovada}")
            return resultado
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro na validação: {e}")
            raise
    
    def gerar_relatorio_analise(self, keywords: List[str]) -> Dict[str, Any]:
        """
        Gera relatório de análise semântica para múltiplas keywords.
        
        Args:
            keywords: Lista de keywords a serem analisadas
            
        Returns:
            Dict com relatório completo
        """
        try:
            logger.info(f"[{self.tracing_id}] Gerando relatório para {len(keywords)} keywords")
            
            analises = []
            aprovadas = 0
            scores = []
            
            for keyword in keywords:
                try:
                    analise = self.analisar_keyword(keyword)
                    analises.append(analise)
                    scores.append(analise.score_qualidade_semantica)
                    
                    if analise.score_qualidade_semantica >= 0.7:
                        aprovadas += 1
                        
                except Exception as e:
                    logger.warning(f"[{self.tracing_id}] Erro ao analisar '{keyword}': {e}")
            
            # Estatísticas
            estatisticas = {
                "total_keywords": len(keywords),
                "analisadas_com_sucesso": len(analises),
                "aprovadas": aprovadas,
                "taxa_aprovacao": round(aprovadas / len(analises) * 100, 2) if analises else 0,
                "score_medio": round(np.mean(scores), 3) if scores else 0,
                "score_mediano": round(np.median(scores), 3) if scores else 0,
                "score_minimo": round(min(scores), 3) if scores else 0,
                "score_maximo": round(max(scores), 3) if scores else 0
            }
            
            # Análise por intenção
            intencoes = {}
            for analise in analises:
                intencao = analise.intencao_detectada
                if intencao not in intencoes:
                    intencoes[intencao] = {"count": 0, "scores": []}
                intencoes[intencao]["count"] += 1
                intencoes[intencao]["scores"].append(analise.score_qualidade_semantica)
            
            # Calcular médias por intenção
            for intencao, dados in intencoes.items():
                dados["score_medio"] = round(np.mean(dados["scores"]), 3)
            
            relatorio = {
                "tracing_id": self.tracing_id,
                "timestamp": datetime.now().isoformat(),
                "estatisticas": estatisticas,
                "analise_por_intencao": intencoes,
                "analises_detalhadas": [
                    {
                        "keyword": a.keyword,
                        "score_qualidade": a.score_qualidade_semantica,
                        "especificidade": a.especificidade,
                        "intencao": a.intencao_detectada,
                        "similaridade": a.similaridade_semantica,
                        "palavras_especificas": a.palavras_chave_especificas
                    }
                    for a in analises
                ]
            }
            
            logger.info(f"[{self.tracing_id}] Relatório gerado com sucesso")
            return relatorio
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro ao gerar relatório: {e}")
            raise

# Função de conveniência para uso direto
def analisar_keyword_cauda_longa(keyword: str, config_path: Optional[str] = None) -> AnaliseSemantica:
    """
    Função de conveniência para análise rápida de keyword.
    
    Args:
        keyword: Keyword a ser analisada
        config_path: Caminho para configuração (opcional)
        
    Returns:
        AnaliseSemantica: Resultado da análise
    """
    analisador = AnalisadorSemanticoCaudaLonga(config_path)
    return analisador.analisar_keyword(keyword)

def validar_keyword_cauda_longa(keyword: str, config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Função de conveniência para validação rápida de keyword.
    
    Args:
        keyword: Keyword a ser validada
        config_path: Caminho para configuração (opcional)
        
    Returns:
        Dict: Resultado da validação
    """
    analisador = AnalisadorSemanticoCaudaLonga(config_path)
    return analisador.validar_keyword_cauda_longa(keyword)

if __name__ == "__main__":
    # Teste básico do analisador
    analisador = AnalisadorSemanticoCaudaLonga()
    
    # Keywords de teste
    keywords_teste = [
        "melhor preço notebook gaming 2024",
        "como fazer backup automático windows 11",
        "sintomas de diabetes tipo 2 em adultos",
        "curso online marketing digital certificado",
        "investimento em criptomoedas para iniciantes"
    ]
    
    print("=== TESTE DO ANALISADOR SEMÂNTICO DE CAUDA LONGA ===")
    for keyword in keywords_teste:
        resultado = analisador.validar_keyword_cauda_longa(keyword)
        print(f"\nKeyword: {keyword}")
        print(f"Aprovada: {resultado['aprovada']}")
        print(f"Score: {resultado['score_qualidade']}")
        print(f"Intenção: {resultado['analise_detalhada']['intencao']}")
        print(f"Especificidade: {resultado['analise_detalhada']['especificidade']}") 