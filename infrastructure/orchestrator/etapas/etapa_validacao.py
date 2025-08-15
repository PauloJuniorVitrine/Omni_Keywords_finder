"""
Etapa de Validação - Omni Keywords Finder

Responsável pela validação de keywords usando Google Keyword Planner
e outros validadores disponíveis.

Tracing ID: ETAPA_VALIDACAO_001_20241227
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

from infrastructure.validacao.google_keyword_planner_validator import GoogleKeywordPlannerValidator
from infrastructure.validacao.base_validator import BaseValidator
from domain.models import Keyword

logger = logging.getLogger(__name__)


@dataclass
class ValidacaoResult:
    """Resultado da etapa de validação."""
    keywords_validadas: List[Keyword]
    total_keywords: int
    tempo_execucao: float
    validadores_utilizados: List[str]
    metadados: Dict[str, Any]


class EtapaValidacao:
    """
    Etapa responsável pela validação de keywords.
    
    Integra com Google Keyword Planner e outros validadores
    para garantir qualidade e relevância das keywords.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa a etapa de validação.
        
        Args:
            config: Configurações da etapa de validação
        """
        self.config = config
        
        # Inicializar validadores disponíveis
        self.validadores = self._inicializar_validadores()
        
        logger.info("Etapa de validação inicializada")
    
    def _inicializar_validadores(self) -> Dict[str, BaseValidator]:
        """Inicializa todos os validadores disponíveis."""
        validadores = {}
        
        try:
            # Validador Google Keyword Planner
            if self.config.get('usar_google_keyword_planner', True):
                validadores['google_keyword_planner'] = GoogleKeywordPlannerValidator()
                logger.info("Validador Google Keyword Planner inicializado")
        except Exception as e:
            logger.warning(f"Erro ao inicializar Google Keyword Planner: {e}")
        
        # TODO: Adicionar outros validadores conforme necessário
        # validadores['bing_ads'] = BingAdsValidator()
        # validadores['facebook_ads'] = FacebookAdsValidator()
        
        logger.info(f"Total de validadores inicializados: {len(validadores)}")
        return validadores
    
    async def executar(self, keywords: List[str], nicho: str) -> ValidacaoResult:
        """
        Executa a etapa de validação para as keywords.
        
        Args:
            keywords: Lista de keywords para validar
            nicho: Nome do nicho
            
        Returns:
            ValidacaoResult com os dados validados
        """
        inicio_tempo = time.time()
        logger.info(f"Iniciando validação para nicho: {nicho} - {len(keywords)} keywords")
        
        try:
            # Executar validação real
            keywords_validadas = []
            validadores_utilizados = []
            
            # Validar com cada validador disponível
            for nome_validador, validador in self.validadores.items():
                try:
                    logger.info(f"Validando com {nome_validador} para nicho: {nicho}")
                    
                    # Aplicar rate limiting
                    self._aplicar_rate_limiting(nome_validador)
                    
                    # Executar validação
                    keywords_validadas_fonte = await validador.validar_keywords(
                        keywords=keywords,
                        config_validacao=self.config
                    )
                    
                    if keywords_validadas_fonte:
                        keywords_validadas.extend(keywords_validadas_fonte)
                        validadores_utilizados.append(nome_validador)
                        logger.info(f"Validadas {len(keywords_validadas_fonte)} keywords com {nome_validador}")
                    
                except Exception as e:
                    logger.error(f"Erro na validação com {nome_validador}: {e}")
                    continue
            
            # Remover duplicatas baseado no termo
            keywords_unicas = {}
            for kw in keywords_validadas:
                if hasattr(kw, 'termo'):
                    keywords_unicas[kw.termo] = kw
                else:
                    keywords_unicas[str(kw)] = kw
            
            keywords_validadas = list(keywords_unicas.values())
            
            # Aplicar filtros de qualidade
            keywords_validadas = self._aplicar_filtros_qualidade(keywords_validadas, nicho)
            
            tempo_execucao = time.time() - inicio_tempo
            
            resultado = ValidacaoResult(
                keywords_validadas=keywords_validadas,
                total_keywords=len(keywords_validadas),
                tempo_execucao=tempo_execucao,
                validadores_utilizados=validadores_utilizados,
                metadados={
                    'nicho': nicho,
                    'keywords_originais': len(keywords),
                    'config_utilizada': self.config
                }
            )
            
            logger.info(f"Validação concluída para nicho: {nicho} - {len(keywords_validadas)} keywords em {tempo_execucao:.2f}string_data")
            return resultado
            
        except Exception as e:
            logger.error(f"Erro na etapa de validação para nicho {nicho}: {e}")
            raise
    
    def _aplicar_rate_limiting(self, nome_validador: str):
        """Aplica rate limiting para evitar bloqueios."""
        delay = self.config.get('delay_entre_requests', 1.0)
        
        # Delay específico por validador
        delays_especificos = self.config.get('delays_por_validador', {})
        if nome_validador in delays_especificos:
            delay = delays_especificos[nome_validador]
        
        time.sleep(delay)
    
    def _aplicar_filtros_qualidade(self, keywords: List[Keyword], nicho: str) -> List[Keyword]:
        """Aplica filtros de qualidade nas keywords validadas."""
        keywords_filtradas = []
        
        for keyword in keywords:
            # Filtro de volume mínimo
            volume_minimo = self.config.get('min_search_volume', 100)
            if hasattr(keyword, 'volume_busca') and keyword.volume_busca < volume_minimo:
                continue
            
            # Filtro de concorrência máxima
            concorrencia_maxima = self.config.get('max_competition', 0.8)
            if hasattr(keyword, 'concorrencia') and keyword.concorrencia > concorrencia_maxima:
                continue
            
            # Filtro de CPC mínimo
            cpc_minimo = self.config.get('min_cpc', 0.1)
            if hasattr(keyword, 'cpc') and keyword.cpc < cpc_minimo:
                continue
            
            # Filtro de CPC máximo
            cpc_maximo = self.config.get('max_cpc', 10.0)
            if hasattr(keyword, 'cpc') and keyword.cpc > cpc_maximo:
                continue
            
            keywords_filtradas.append(keyword)
        
        logger.info(f"Filtros aplicados: {len(keywords)} -> {len(keywords_filtradas)} keywords")
        return keywords_filtradas
    
    def obter_status(self) -> Dict[str, Any]:
        """Obtém status da etapa de validação."""
        return {
            "validadores_ativos": len(self.validadores),
            "validadores_disponiveis": list(self.validadores.keys()),
            "configuracao": self.config
        } 