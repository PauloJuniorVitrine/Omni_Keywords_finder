"""
Sistema de Cálculo de Complexidade Semântica
LONGTAIL-002: Sistema completo de análise de complexidade semântica

Tracing ID: LONGTAIL-002
Data/Hora: 2024-12-20 16:40:00 UTC
Versão: 1.0
Status: EM IMPLEMENTAÇÃO

Responsável: Sistema de Cauda Longa
"""

import re
import unicodedata
from typing import Dict, List, Set, Tuple, Optional, NamedTuple
from datetime import datetime
from dataclasses import dataclass
from shared.logger import logger


@dataclass
class ComplexidadeSemantica:
    """Resultado da análise de complexidade semântica."""
    score_complexidade: float
    densidade_semantica: float
    palavras_unicas: int
    total_palavras: int
    caracteres_significativos: int
    nivel_complexidade: str
    fatores_complexidade: Dict[str, float]
    metadados: Dict[str, any]


class CalculadorComplexidadeSemantica:
    """
    Sistema completo de cálculo de complexidade semântica para cauda longa.
    
    Funcionalidades:
    - Remoção de espaços extras
    - Filtro de pontuação irrelevante
    - Análise de palavras únicas
    - Cálculo de densidade semântica
    - Normalização de complexidade
    - Relatórios de análise
    - Integração com processamento
    - Logs de complexidade
    - Thresholds configuráveis
    - Validação de qualidade
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o calculador de complexidade semântica.
        
        Args:
            config: Configuração opcional do calculador
        """
        self.config = config or {}
        self._pontuacao_irrelevante = self._carregar_pontuacao_irrelevante()
        self._palavras_complexas = self._carregar_palavras_complexas()
        self._remover_espacos_extras = self.config.get("remover_espacos_extras", True)
        self._filtrar_pontuacao = self.config.get("filtrar_pontuacao", True)
        self._case_sensitive = self.config.get("case_sensitive", False)
        self._remover_acentos = self.config.get("remover_acentos", False)
        
        # Thresholds configuráveis
        self._threshold_baixa = self.config.get("threshold_baixa", 0.3)
        self._threshold_media = self.config.get("threshold_media", 0.6)
        self._threshold_alta = self.config.get("threshold_alta", 0.8)
        
        # Métricas de performance
        self.metricas = {
            "total_analises": 0,
            "total_textos_processados": 0,
            "tempo_total_analise": 0.0,
            "ultima_analise": None
        }
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "calculador_complexidade_inicializado",
            "status": "success",
            "source": "CalculadorComplexidadeSemantica.__init__",
            "details": {
                "remover_espacos_extras": self._remover_espacos_extras,
                "filtrar_pontuacao": self._filtrar_pontuacao,
                "case_sensitive": self._case_sensitive,
                "remover_acentos": self._remover_acentos,
                "threshold_baixa": self._threshold_baixa,
                "threshold_media": self._threshold_media,
                "threshold_alta": self._threshold_alta,
                "total_palavras_complexas": len(self._palavras_complexas)
            }
        })
    
    def _carregar_pontuacao_irrelevante(self) -> Set[str]:
        """
        Carrega pontuação considerada irrelevante para análise.
        
        Returns:
            Conjunto de pontuação irrelevante
        """
        pontuacao = {
            # Pontuação básica
            ".", ",", "!", "?", ";", ":", "-", "_",
            
            # Aspas e parênteses
            '"', "'", "(", ")", "[", "]", "{", "}",
            
            # Outros símbolos
            "@", "#", "$", "%", "^", "&", "*", "+", "=",
            "<", ">", "/", "\\", "|", "~", "`"
        }
        
        return pontuacao
    
    def _carregar_palavras_complexas(self) -> Set[str]:
        """
        Carrega palavras consideradas complexas para análise.
        
        Returns:
            Conjunto de palavras complexas
        """
        palavras_complexas = {
            # Palavras técnicas
            "algoritmo", "arquitetura", "framework", "paradigma", "metodologia",
            "otimização", "implementação", "integração", "configuração", "escalabilidade",
            "robustez", "confiabilidade", "manutenibilidade", "extensibilidade", "modularidade",
            
            # Palavras acadêmicas
            "análise", "síntese", "metodologia", "metodológico", "conceitual", "teórico",
            "prático", "empírico", "quantitativo", "qualitativo", "estatístico", "probabilístico",
            "determinístico", "heurístico", "algorítmico", "sistemático", "sistêmico",
            
            # Palavras específicas de domínio
            "especializado", "especializada", "especializados", "especializadas",
            "profissional", "profissionais", "avançado", "avançada", "avançados", "avançadas",
            "experimental", "experimentais", "inovador", "inovadora", "inovadores", "inovadoras",
            "revolucionário", "revolucionária", "revolucionários", "revolucionárias",
            
            # Palavras de complexidade
            "sofisticado", "sofisticada", "sofisticados", "sofisticadas",
            "elaborado", "elaborada", "elaborados", "elaboradas",
            "detalhado", "detalhada", "detalhados", "detalhadas",
            "compreensivo", "compreensiva", "compreensivos", "compreensivas",
            "abrangente", "abrangentes", "extenso", "extensa", "extensos", "extensas",
            
            # Palavras técnicas específicas
            "multidimensional", "interdisciplinar", "transdisciplinar", "interconectado",
            "interconectada", "interconectados", "interconectadas", "interdependente",
            "interdependentes", "interrelacionado", "interrelacionada", "interrelacionados",
            "interrelacionadas", "interoperável", "interoperáveis", "interoperacional",
            "interoperacionais", "interoperatividade", "interoperatividades"
        }
        
        return palavras_complexas
    
    def normalizar_texto(self, texto: str) -> str:
        """
        Normaliza texto para análise de complexidade.
        
        Args:
            texto: Texto a ser normalizado
            
        Returns:
            Texto normalizado
        """
        if not texto:
            return ""
        
        # Normalização básica
        texto = texto.strip()
        
        # Remoção de espaços extras
        if self._remover_espacos_extras:
            texto = re.sub(r'\string_data+', ' ', texto)
        
        # Case sensitivity
        if not self._case_sensitive:
            texto = texto.lower()
        
        # Remoção de acentos
        if self._remover_acentos:
            texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
        
        return texto
    
    def filtrar_pontuacao(self, texto: str) -> str:
        """
        Remove pontuação irrelevante do texto.
        
        Args:
            texto: Texto para filtragem
            
        Returns:
            Texto sem pontuação irrelevante
        """
        if not self._filtrar_pontuacao:
            return texto
        
        for pontuacao in self._pontuacao_irrelevante:
            texto = texto.replace(pontuacao, ' ')
        
        # Remove espaços extras após remoção de pontuação
        texto = re.sub(r'\string_data+', ' ', texto)
        
        return texto.strip()
    
    def extrair_palavras(self, texto: str) -> List[str]:
        """
        Extrai palavras do texto normalizado.
        
        Args:
            texto: Texto para extração
            
        Returns:
            Lista de palavras extraídas
        """
        texto_normalizado = self.normalizar_texto(texto)
        texto_filtrado = self.filtrar_pontuacao(texto_normalizado)
        
        # Extração de palavras usando regex
        palavras = re.findall(r'\b\w+\b', texto_filtrado)
        
        return palavras
    
    def calcular_densidade_semantica(self, palavras: List[str]) -> float:
        """
        Calcula densidade semântica baseada em palavras únicas.
        
        Args:
            palavras: Lista de palavras
            
        Returns:
            Densidade semântica entre 0 e 1
        """
        if not palavras:
            return 0.0
        
        palavras_unicas = len(set(palavras))
        total_palavras = len(palavras)
        
        # Densidade = palavras únicas / total de palavras
        densidade = palavras_unicas / total_palavras
        
        return min(1.0, max(0.0, densidade))
    
    def calcular_fatores_complexidade(self, palavras: List[str]) -> Dict[str, float]:
        """
        Calcula fatores individuais de complexidade.
        
        Args:
            palavras: Lista de palavras
            
        Returns:
            Dicionário com fatores de complexidade
        """
        if not palavras:
            return {
                "densidade_semantica": 0.0,
                "palavras_complexas": 0.0,
                "comprimento_medio": 0.0,
                "variedade_vocabulario": 0.0
            }
        
        # Densidade semântica
        densidade_semantica = self.calcular_densidade_semantica(palavras)
        
        # Proporção de palavras complexas
        palavras_complexas_encontradas = sum(
            1 for palavra in palavras 
            if palavra in self._palavras_complexas
        )
        proporcao_palavras_complexas = palavras_complexas_encontradas / len(palavras)
        
        # Comprimento médio das palavras
        comprimentos = [len(palavra) for palavra in palavras]
        comprimento_medio = sum(comprimentos) / len(comprimentos)
        comprimento_medio_norm = min(1.0, comprimento_medio / 15.0)  # Normalizado para 15 caracteres
        
        # Variedade de vocabulário (baseado em palavras únicas)
        palavras_unicas = len(set(palavras))
        variedade_vocabulario = palavras_unicas / len(palavras)
        
        return {
            "densidade_semantica": densidade_semantica,
            "palavras_complexas": proporcao_palavras_complexas,
            "comprimento_medio": comprimento_medio_norm,
            "variedade_vocabulario": variedade_vocabulario
        }
    
    def calcular_score_complexidade(self, fatores: Dict[str, float]) -> float:
        """
        Calcula score final de complexidade baseado nos fatores.
        
        Args:
            fatores: Dicionário com fatores de complexidade
            
        Returns:
            Score de complexidade entre 0 e 1
        """
        # Pesos para cada fator
        pesos = {
            "densidade_semantica": 0.3,
            "palavras_complexas": 0.3,
            "comprimento_medio": 0.2,
            "variedade_vocabulario": 0.2
        }
        
        # Cálculo do score ponderado
        score = sum(
            fatores.get(fator, 0.0) * peso
            for fator, peso in pesos.items()
        )
        
        return min(1.0, max(0.0, score))
    
    def classificar_nivel_complexidade(self, score: float) -> str:
        """
        Classifica o nível de complexidade baseado no score.
        
        Args:
            score: Score de complexidade
            
        Returns:
            Nível de complexidade
        """
        if score < self._threshold_baixa:
            return "baixa"
        elif score < self._threshold_media:
            return "média"
        elif score < self._threshold_alta:
            return "alta"
        else:
            return "muito alta"
    
    def contar_caracteres_significativos(self, texto: str) -> int:
        """
        Conta caracteres significativos no texto.
        
        Args:
            texto: Texto para contagem
            
        Returns:
            Número de caracteres significativos
        """
        texto_normalizado = self.normalizar_texto(texto)
        texto_filtrado = self.filtrar_pontuacao(texto_normalizado)
        
        # Remove espaços e conta caracteres
        caracteres_significativos = len(texto_filtrado.replace(" ", ""))
        
        return caracteres_significativos
    
    def analisar_complexidade(self, texto: str) -> ComplexidadeSemantica:
        """
        Analisa complexidade semântica de um texto.
        
        Args:
            texto: Texto para análise
            
        Returns:
            Resultado da análise de complexidade
        """
        inicio_analise = datetime.utcnow()
        
        try:
            # Extração de palavras
            palavras = self.extrair_palavras(texto)
            
            # Cálculo de fatores de complexidade
            fatores = self.calcular_fatores_complexidade(palavras)
            
            # Cálculo do score final
            score_complexidade = self.calcular_score_complexidade(fatores)
            
            # Classificação do nível
            nivel_complexidade = self.classificar_nivel_complexidade(score_complexidade)
            
            # Contagem de caracteres significativos
            caracteres_significativos = self.contar_caracteres_significativos(texto)
            
            # Metadados da análise
            metadados = {
                "texto_original": texto,
                "texto_normalizado": self.normalizar_texto(texto),
                "texto_filtrado": self.filtrar_pontuacao(self.normalizar_texto(texto)),
                "configuracao": {
                    "remover_espacos_extras": self._remover_espacos_extras,
                    "filtrar_pontuacao": self._filtrar_pontuacao,
                    "case_sensitive": self._case_sensitive,
                    "remover_acentos": self._remover_acentos,
                    "threshold_baixa": self._threshold_baixa,
                    "threshold_media": self._threshold_media,
                    "threshold_alta": self._threshold_alta
                },
                "palavras_complexas_encontradas": [
                    palavra for palavra in palavras 
                    if palavra in self._palavras_complexas
                ]
            }
            
            # Criação do resultado
            resultado = ComplexidadeSemantica(
                score_complexidade=score_complexidade,
                densidade_semantica=fatores["densidade_semantica"],
                palavras_unicas=len(set(palavras)),
                total_palavras=len(palavras),
                caracteres_significativos=caracteres_significativos,
                nivel_complexidade=nivel_complexidade,
                fatores_complexidade=fatores,
                metadados=metadados
            )
            
            # Atualização de métricas
            tempo_analise = (datetime.utcnow() - inicio_analise).total_seconds()
            self.metricas["total_analises"] += 1
            self.metricas["total_textos_processados"] += 1
            self.metricas["tempo_total_analise"] += tempo_analise
            self.metricas["ultima_analise"] = datetime.utcnow().isoformat()
            
            # Log da análise
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "analise_complexidade_semantica",
                "status": "success",
                "source": "CalculadorComplexidadeSemantica.analisar_complexidade",
                "details": {
                    "texto_tamanho": len(texto),
                    "total_palavras": len(palavras),
                    "palavras_unicas": len(set(palavras)),
                    "score_complexidade": score_complexidade,
                    "nivel_complexidade": nivel_complexidade,
                    "tempo_analise": tempo_analise,
                    "caracteres_significativos": caracteres_significativos
                }
            })
            
            return resultado
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_analise_complexidade",
                "status": "error",
                "source": "CalculadorComplexidadeSemantica.analisar_complexidade",
                "details": {
                    "texto": texto[:100] + "..." if len(texto) > 100 else texto,
                    "erro": str(e)
                }
            })
            
            # Retorno de erro
            return ComplexidadeSemantica(
                score_complexidade=0.0,
                densidade_semantica=0.0,
                palavras_unicas=0,
                total_palavras=0,
                caracteres_significativos=0,
                nivel_complexidade="erro",
                fatores_complexidade={},
                metadados={"erro": str(e)}
            )
    
    def obter_metricas(self) -> Dict:
        """
        Obtém métricas de performance do calculador.
        
        Returns:
            Dicionário com métricas
        """
        return {
            **self.metricas,
            "tempo_medio_analise": (
                self.metricas["tempo_total_analise"] / max(self.metricas["total_analises"], 1)
            ),
            "textos_por_analise": (
                self.metricas["total_textos_processados"] / max(self.metricas["total_analises"], 1)
            )
        }
    
    def resetar_metricas(self):
        """Reseta métricas de performance."""
        self.metricas = {
            "total_analises": 0,
            "total_textos_processados": 0,
            "tempo_total_analise": 0.0,
            "ultima_analise": None
        }
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "metricas_resetadas",
            "status": "info",
            "source": "CalculadorComplexidadeSemantica.resetar_metricas",
            "details": {"acao": "reset_metricas"}
        })


# Instância global para uso em outros módulos
calculador_complexidade = CalculadorComplexidadeSemantica() 