"""
Etapa de Coleta - Omni Keywords Finder

Responsável pela coleta de keywords de todas as fontes disponíveis:
- Google Keyword Planner
- Google Suggest
- Google Trends
- Google PAA
- Amazon
- Reddit
- Pinterest
- YouTube
- TikTok
- Instagram
- Discord
- GSC

Tracing ID: ETAPA_COLETA_001_20241227
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

from infrastructure.coleta.base_keyword import KeywordColetorBase
from infrastructure.coleta.amazon import AmazonColetor
from infrastructure.coleta.google_suggest import GoogleSuggestColetor
from infrastructure.coleta.google_trends import GoogleTrendsColetor
from infrastructure.coleta.google_paa import GooglePAAColetor
from infrastructure.coleta.google_keyword_planner import GoogleKeywordPlannerColetor
from infrastructure.coleta.reddit import RedditColetor
from infrastructure.coleta.pinterest import PinterestColetor
from infrastructure.coleta.youtube import YouTubeColetor
from infrastructure.coleta.tiktok import TikTokColetor
from infrastructure.coleta.instagram import InstagramColetor
from infrastructure.coleta.discord import DiscordColetor
from infrastructure.coleta.gsc import GSCColetor

logger = logging.getLogger(__name__)


@dataclass
class ColetaResult:
    """Resultado da etapa de coleta."""
    keywords_coletadas: List[str]
    total_keywords: int
    tempo_execucao: float
    fontes_utilizadas: List[str]
    metadados: Dict[str, Any]


class EtapaColeta:
    """
    Etapa responsável pela coleta de keywords de múltiplas fontes.
    
    Integra com todos os coletores disponíveis e aplica rate limiting
    inteligente para evitar bloqueios.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa a etapa de coleta.
        
        Args:
            config: Configurações da etapa de coleta
        """
        self.config = config
        
        # Inicializar coletores disponíveis
        self.coletores = self._inicializar_coletores()
        
        logger.info("Etapa de coleta inicializada")
    
    def _inicializar_coletores(self) -> Dict[str, KeywordColetorBase]:
        """Inicializa todos os coletores disponíveis."""
        coletores = {}
        
        try:
            # Google Keyword Planner
            if self.config.get('usar_google_keyword_planner', True):
                coletores['google_keyword_planner'] = GoogleKeywordPlannerColetor()
                logger.info("Coletor Google Keyword Planner inicializado")
        except Exception as e:
            logger.warning(f"Erro ao inicializar coletor Google Keyword Planner: {e}")
        
        try:
            # Google Suggest
            if self.config.get('usar_google_suggest', True):
                coletores['google_suggest'] = GoogleSuggestColetor()
                logger.info("Coletor Google Suggest inicializado")
        except Exception as e:
            logger.warning(f"Erro ao inicializar coletor Google Suggest: {e}")
        
        try:
            # Google Trends
            if self.config.get('usar_google_trends', True):
                coletores['google_trends'] = GoogleTrendsColetor()
                logger.info("Coletor Google Trends inicializado")
        except Exception as e:
            logger.warning(f"Erro ao inicializar coletor Google Trends: {e}")
        
        try:
            # Google PAA
            if self.config.get('usar_google_paa', True):
                coletores['google_paa'] = GooglePAAColetor()
                logger.info("Coletor Google PAA inicializado")
        except Exception as e:
            logger.warning(f"Erro ao inicializar coletor Google PAA: {e}")
        
        try:
            # Amazon
            if self.config.get('usar_amazon', True):
                coletores['amazon'] = AmazonColetor()
                logger.info("Coletor Amazon inicializado")
        except Exception as e:
            logger.warning(f"Erro ao inicializar coletor Amazon: {e}")
        
        try:
            # Reddit
            if self.config.get('usar_reddit', True):
                coletores['reddit'] = RedditColetor()
                logger.info("Coletor Reddit inicializado")
        except Exception as e:
            logger.warning(f"Erro ao inicializar coletor Reddit: {e}")
        
        try:
            # Pinterest
            if self.config.get('usar_pinterest', True):
                coletores['pinterest'] = PinterestColetor()
                logger.info("Coletor Pinterest inicializado")
        except Exception as e:
            logger.warning(f"Erro ao inicializar coletor Pinterest: {e}")
        
        try:
            # YouTube
            if self.config.get('usar_youtube', True):
                coletores['youtube'] = YouTubeColetor()
                logger.info("Coletor YouTube inicializado")
        except Exception as e:
            logger.warning(f"Erro ao inicializar coletor YouTube: {e}")
        
        try:
            # TikTok
            if self.config.get('usar_tiktok', True):
                coletores['tiktok'] = TikTokColetor()
                logger.info("Coletor TikTok inicializado")
        except Exception as e:
            logger.warning(f"Erro ao inicializar coletor TikTok: {e}")
        
        try:
            # Instagram
            if self.config.get('usar_instagram', True):
                coletores['instagram'] = InstagramColetor()
                logger.info("Coletor Instagram inicializado")
        except Exception as e:
            logger.warning(f"Erro ao inicializar coletor Instagram: {e}")
        
        try:
            # Discord
            if self.config.get('usar_discord', True):
                coletores['discord'] = DiscordColetor()
                logger.info("Coletor Discord inicializado")
        except Exception as e:
            logger.warning(f"Erro ao inicializar coletor Discord: {e}")
        
        try:
            # GSC
            if self.config.get('usar_gsc', True):
                coletores['gsc'] = GSCColetor()
                logger.info("Coletor GSC inicializado")
        except Exception as e:
            logger.warning(f"Erro ao inicializar coletor GSC: {e}")
        
        logger.info(f"Total de coletores inicializados: {len(coletores)}")
        return coletores
    
    async def executar(self, nicho: str, keywords_semente: Optional[List[str]] = None) -> ColetaResult:
        """
        Executa a etapa de coleta para um nicho específico.
        
        Args:
            nicho: Nome do nicho
            keywords_semente: Keywords iniciais para expandir
            
        Returns:
            ColetaResult com os dados coletados
        """
        inicio_tempo = time.time()
        logger.info(f"Iniciando coleta para nicho: {nicho}")
        
        try:
            # Executar coleta real
            keywords_coletadas = []
            fontes_utilizadas = []
            
            # Usar keywords semente se fornecidas
            if keywords_semente is None:
                keywords_semente = self.config.get('keywords_semente', []) or []
            
            # Coletar de cada fonte disponível
            for nome_coletor, coletor in self.coletores.items():
                try:
                    logger.info(f"Coletando de {nome_coletor} para nicho: {nicho}")
                    
                    # Aplicar rate limiting
                    self._aplicar_rate_limiting(nome_coletor)
                    
                    # Executar coleta - usar método correto do coletor
                    keywords_fonte = await coletor.coletar_keywords(keywords_semente or [])
                    
                    if keywords_fonte:
                        # Extrair termos das keywords
                        termos_fonte = [kw.termo for kw in keywords_fonte if hasattr(kw, 'termo')]
                        keywords_coletadas.extend(termos_fonte)
                        fontes_utilizadas.append(nome_coletor)
                        logger.info(f"Coletadas {len(termos_fonte)} keywords de {nome_coletor}")
                    
                except Exception as e:
                    logger.error(f"Erro na coleta de {nome_coletor}: {e}")
                    continue
            
            # Remover duplicatas
            keywords_coletadas = list(set(keywords_coletadas))
            
            # Aplicar filtros de qualidade
            keywords_coletadas = self._aplicar_filtros_qualidade(keywords_coletadas, nicho)
            
            tempo_execucao = time.time() - inicio_tempo
            
            resultado = ColetaResult(
                keywords_coletadas=keywords_coletadas,
                total_keywords=len(keywords_coletadas),
                tempo_execucao=tempo_execucao,
                fontes_utilizadas=fontes_utilizadas,
                metadados={
                    'nicho': nicho,
                    'keywords_semente': keywords_semente,
                    'config_utilizada': self.config
                }
            )
            
            logger.info(f"Coleta concluída para nicho: {nicho} - {len(keywords_coletadas)} keywords em {tempo_execucao:.2f}string_data")
            return resultado
            
        except Exception as e:
            logger.error(f"Erro na etapa de coleta para nicho {nicho}: {e}")
            raise
    
    def _aplicar_rate_limiting(self, nome_coletor: str):
        """Aplica rate limiting para evitar bloqueios."""
        delay = self.config.get('delay_entre_requests', 1.0)
        
        # Delay específico por coletor
        delays_especificos = self.config.get('delays_por_coletor', {})
        if nome_coletor in delays_especificos:
            delay = delays_especificos[nome_coletor]
        
        time.sleep(delay)
    
    def _aplicar_filtros_qualidade(self, keywords: List[str], nicho: str) -> List[str]:
        """Aplica filtros de qualidade nas keywords coletadas."""
        keywords_filtradas = []
        
        for keyword in keywords:
            # Filtro de comprimento mínimo
            if len(keyword.strip()) < self.config.get('min_comprimento_keyword', 3):
                continue
            
            # Filtro de caracteres válidos
            if not self._validar_caracteres_keyword(keyword):
                continue
            
            # Filtro de relevância para o nicho
            if not self._validar_relevancia_nicho(keyword, nicho):
                continue
            
            keywords_filtradas.append(keyword.strip())
        
        logger.info(f"Filtros aplicados: {len(keywords)} -> {len(keywords_filtradas)} keywords")
        return keywords_filtradas
    
    def obter_status(self) -> Dict[str, Any]:
        """Obtém status da etapa de coleta."""
        return {
            "coletores_ativos": len(self.coletores),
            "coletores_disponiveis": list(self.coletores.keys()),
            "configuracao": self.config
        }
    
    def _validar_caracteres_keyword(self, keyword: str) -> bool:
        """Valida se a keyword contém apenas caracteres válidos."""
        caracteres_invalidos = ['<', '>', '&', '"', "'", '\\', '/']
        return not any(c in keyword for c in caracteres_invalidos)
    
    def _validar_relevancia_nicho(self, keyword: str, nicho: str) -> bool:
        """Valida se a keyword é relevante para o nicho."""
        # Implementação básica - pode ser expandida
        keyword_lower = keyword.lower()
        nicho_lower = nicho.lower()
        
        # Verificar se palavras do nicho estão na keyword
        palavras_nicho = nicho_lower.split()
        return any(palavra in keyword_lower for palavra in palavras_nicho) 