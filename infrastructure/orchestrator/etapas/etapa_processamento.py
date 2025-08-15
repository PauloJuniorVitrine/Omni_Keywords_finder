"""
Etapa de Processamento - Omni Keywords Finder

Responsável pelo processamento e enriquecimento de keywords:
- Normalização
- Limpeza
- Enriquecimento com ML
- Validação
- Score e ranking

Tracing ID: ETAPA_PROCESSAMENTO_001_20241227
Versão: 2.0
Autor: IA-Cursor
Status: ✅ ADAPTADO PARA NOVA ARQUITETURA
"""

import time
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path
import sys

# Adicionar caminho para importar módulos do projeto
sys.path.append(str(Path(__file__).parent.parent.parent))

from domain.models import Keyword
from infrastructure.processamento.ml_processor import MLProcessor
from infrastructure.processamento.normalizador_keywords import NormalizadorKeywords
from infrastructure.processamento.enriquecidor_keywords import EnriquecidorKeywords
from infrastructure.processamento.validador_keywords import ValidadorKeywords

logger = logging.getLogger(__name__)


@dataclass
class ProcessamentoResult:
    """Resultado da etapa de processamento."""
    keywords_processadas: List[Keyword]
    total_keywords: int
    tempo_execucao: float
    metricas_processamento: Dict[str, Any]
    metadados: Dict[str, Any]


class EtapaProcessamento:
    """
    Etapa responsável pelo processamento e enriquecimento de keywords.
    
    Integra com ML Processor e outros componentes de processamento
    para otimizar e enriquecer as keywords coletadas.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa a etapa de processamento.
        
        Args:
            config: Configurações da etapa de processamento
        """
        self.config = config
        
        # Inicializar componentes de processamento
        self.ml_processor = MLProcessor()
        self.normalizador = NormalizadorKeywords()
        self.enriquecidor = EnriquecidorKeywords()
        self.validador = ValidadorKeywords()
        
        logger.info("Etapa de processamento inicializada")
    
    async def executar(self, keywords_coletadas: List[str], nicho: str) -> ProcessamentoResult:
        """
        Executa a etapa de processamento para as keywords coletadas.
        
        Args:
            keywords_coletadas: Lista de keywords coletadas
            nicho: Nome do nicho
            
        Returns:
            ProcessamentoResult com os dados processados
        """
        inicio_tempo = time.time()
        logger.info(f"Iniciando processamento para nicho: {nicho} - {len(keywords_coletadas)} keywords")
        
        try:
            # Converter strings para objetos Keyword
            keywords_objetos = self._converter_para_keywords(keywords_coletadas)
            
            # 1. Normalização
            logger.info("Executando normalização...")
            keywords_normalizadas = self.normalizador.normalizar_lista(keywords_objetos)
            logger.info(f"Normalização concluída: {len(keywords_normalizadas)} keywords")
            
            # 2. Validação básica
            logger.info("Executando validação...")
            keywords_validadas = self._validar_keywords(keywords_normalizadas)
            logger.info(f"Validação concluída: {len(keywords_validadas)} keywords")
            
            # 3. Enriquecimento
            logger.info("Executando enriquecimento...")
            keywords_enriquecidas = self.enriquecidor.enriquecer_keywords(keywords_validadas)
            logger.info(f"Enriquecimento concluído: {len(keywords_enriquecidas)} keywords")
            
            # 4. Processamento ML (se habilitado)
            if self.config.get('usar_ml', True):
                logger.info("Executando processamento ML...")
                keywords_ml = self.ml_processor.processar_keywords(
                    keywords_enriquecidas,
                    contexto={'nicho': nicho}
                )
                logger.info(f"Processamento ML concluído: {len(keywords_ml)} keywords")
            else:
                keywords_ml = keywords_enriquecidas
            
            # 5. Aplicar filtros finais
            keywords_finais = self._aplicar_filtros_finais(keywords_ml, nicho)
            
            tempo_execucao = time.time() - inicio_tempo
            
            # Calcular métricas
            metricas = self._calcular_metricas_processamento(
                len(keywords_coletadas),
                len(keywords_finais),
                tempo_execucao
            )
            
            resultado = ProcessamentoResult(
                keywords_processadas=keywords_finais,
                total_keywords=len(keywords_finais),
                tempo_execucao=tempo_execucao,
                metricas_processamento=metricas,
                metadados={
                    'nicho': nicho,
                    'keywords_iniciais': len(keywords_coletadas),
                    'taxa_aprovacao': len(keywords_finais) / len(keywords_coletadas) if keywords_coletadas else 0,
                    'config_utilizada': self.config
                }
            )
            
            logger.info(f"Processamento concluído para nicho: {nicho} - {len(keywords_finais)} keywords em {tempo_execucao:.2f}string_data")
            return resultado
            
        except Exception as e:
            logger.error(f"Erro na etapa de processamento para nicho {nicho}: {e}")
            raise
    
    def _converter_para_keywords(self, keywords_strings: List[str]) -> List[Keyword]:
        """Converte lista de strings para objetos Keyword."""
        keywords = []
        for termo in keywords_strings:
            try:
                keyword = Keyword(
                    termo=termo,
                    volume_busca=0,  # Será preenchido pelo enriquecimento
                    cpc=0.0,
                    concorrencia=0.0,
                    intencao="informacional",
                    score=0.0,
                    justificativa="",
                    fonte="coleta",
                    data_coleta=None
                )
                keywords.append(keyword)
            except Exception as e:
                logger.warning(f"Erro ao converter keyword '{termo}': {e}")
                continue
        
        return keywords
    
    def _validar_keywords(self, keywords: List[Keyword]) -> List[Keyword]:
        """Valida keywords usando o validador."""
        keywords_validas = []
        
        for keyword in keywords:
            try:
                valido, _ = self.validador.validar_keyword(keyword)
                if valido:
                    keywords_validas.append(keyword)
            except Exception as e:
                logger.warning(f"Erro ao validar keyword '{keyword.termo}': {e}")
                continue
        
        return keywords_validas
    
    def _aplicar_filtros_finais(self, keywords: List[Keyword], nicho: str) -> List[Keyword]:
        """Aplica filtros finais nas keywords processadas."""
        keywords_filtradas = []
        
        for keyword in keywords:
            # Filtro de score mínimo
            score_minimo = self.config.get('score_minimo', 0.0)
            if keyword.score < score_minimo:
                continue
            
            # Filtro de volume mínimo
            volume_minimo = self.config.get('volume_minimo', 0)
            if keyword.volume_busca < volume_minimo:
                continue
            
            # Filtro de CPC máximo
            cpc_maximo = self.config.get('cpc_maximo', float('inf'))
            if keyword.cpc > cpc_maximo:
                continue
            
            # Filtro de concorrência máxima
            concorrencia_maxima = self.config.get('concorrencia_maxima', 1.0)
            if keyword.concorrencia > concorrencia_maxima:
                continue
            
            keywords_filtradas.append(keyword)
        
        logger.info(f"Filtros finais aplicados: {len(keywords)} -> {len(keywords_filtradas)} keywords")
        return keywords_filtradas
    
    def _calcular_metricas_processamento(self, total_inicial: int, total_final: int, tempo_execucao: float) -> Dict[str, Any]:
        """Calcula métricas do processamento."""
        return {
            'total_inicial': total_inicial,
            'total_final': total_final,
            'taxa_aprovacao': total_final / total_inicial if total_inicial > 0 else 0.0,
            'tempo_execucao': tempo_execucao,
            'keywords_por_segundo': total_final / tempo_execucao if tempo_execucao > 0 else 0.0
        }
    
    def obter_status(self) -> Dict[str, Any]:
        """Obtém status da etapa de processamento."""
        return {
            "ml_processor_ativo": self.config.get('usar_ml', True),
            "normalizador_ativo": True,
            "enriquecidor_ativo": True,
            "validador_ativo": True,
            "configuracao": self.config
        } 