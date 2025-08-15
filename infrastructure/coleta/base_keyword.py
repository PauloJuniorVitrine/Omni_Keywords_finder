"""
Classes base para implementação de coletores de palavras-chave.
"""
from abc import abstractmethod
from typing import List, Dict, Optional, Any
from infrastructure.coleta.base import ColetorBase
from domain.models import Keyword, IntencaoBusca
from shared.config import (
    CACHE_CONFIG,
    COLETA_CONFIG,
    VALIDACAO_CONFIG
)
from infrastructure.coleta.utils.cache import CacheDistribuido
from shared.logger import logger
import json
import asyncio
from datetime import datetime, timedelta

# 🎯 FASE 4 - INTEGRAÇÃO COM OBSERVABILIDADE
from infrastructure.observability.trace_decorator import trace_function
from infrastructure.observability.anomaly_detection import AnomalyDetector
from infrastructure.observability.predictive_monitoring import PredictiveMonitor

class KeywordColetorBase(ColetorBase):
    """Classe base para coletores especializados em palavras-chave."""

    def __init__(self, nome: str, config: Dict):
        """Inicializa o coletor com configurações específicas para keywords."""
        super().__init__(nome, config)
        
        # Configurações de coleta
        self.rate_limit = COLETA_CONFIG["limite_requisicoes_minuto"]
        self.proxy_enabled = COLETA_CONFIG["proxy_enabled"]
        self.user_agent = COLETA_CONFIG["user_agent"]
        self.proxy_config = COLETA_CONFIG["proxy_config"] if self.proxy_enabled else None
        
        # Configurações de validação
        self.min_volume = VALIDACAO_CONFIG["min_volume"]
        self.max_volume = VALIDACAO_CONFIG["max_volume"]
        self.min_concorrencia = VALIDACAO_CONFIG["min_concorrencia"]
        self.max_concorrencia = VALIDACAO_CONFIG["max_concorrencia"]
        self.min_caracteres = VALIDACAO_CONFIG["min_caracteres"]
        self.max_caracteres = VALIDACAO_CONFIG["max_caracteres"]
        self.caracteres_permitidos = VALIDACAO_CONFIG["caracteres_permitidos"]
        
        # Configuração de cache
        self.cache = CacheDistribuido(
            namespace=CACHE_CONFIG["namespaces"][nome],
            ttl_padrao=CACHE_CONFIG["ttl_padrao"]
        )

    @abstractmethod
    async def extrair_sugestoes(self, termo: str) -> List[str]:
        """
        Extrai sugestões de palavras-chave relacionadas ao termo.
        
        Args:
            termo: Termo base para busca de sugestões
            
        Returns:
            Lista de strings com sugestões relacionadas
        """
        pass

    @abstractmethod
    async def extrair_metricas_especificas(self, termo: str) -> Dict:
        """
        Extrai métricas específicas da fonte para o termo.
        
        Args:
            termo: Termo para extrair métricas
            
        Returns:
            Dicionário com métricas específicas da fonte
        """
        pass

    async def validar_termo_especifico(self, termo: str) -> bool:
        """
        Validação específica do coletor além das validações base.
        
        Args:
            termo: Termo a ser validado
            
        Returns:
            True se válido para este coletor específico
        """
        return True

    async def validar_termo(self, termo: str) -> bool:
        """
        Valida um termo antes da coleta.
        
        Args:
            termo: Termo a ser validado
            
        Returns:
            True se o termo é válido
        """
        try:
            # Valida tamanho
            if not self.min_caracteres <= len(termo) <= self.max_caracteres:
                self.registrar_erro(
                    "Termo com tamanho inválido",
                    {
                        "termo": termo,
                        "tamanho": len(termo),
                        "min": self.min_caracteres,
                        "max": self.max_caracteres
                    }
                )
                return False
                
            # Valida caracteres
            if not all(c in self.caracteres_permitidos for c in termo):
                self.registrar_erro(
                    "Termo contém caracteres inválidos",
                    {"termo": termo}
                )
                return False
                
            # Validação específica do coletor
            if not await self.validar_termo_especifico(termo):
                return False
                
            return True
            
        except Exception as e:
            self.registrar_erro(
                "Erro ao validar termo",
                {"erro": str(e), "termo": termo}
            )
            return False

    @trace_function()
    async def coletar_keywords(self, termos: List[str]) -> List[Keyword]:
        """
        Coleta keywords para uma lista de termos.
        
        Args:
            termos: Lista de termos para coleta
            
        Returns:
            Lista de objetos Keyword
        """
        try:
            if isinstance(termos, str):
                termos = [termos]
            elif isinstance(termos, list):
                termos = [t for sub in termos for t in (sub if isinstance(sub, list) else [sub])]

            # Valida termos de entrada
            termos_validos = []
            for termo in termos:
                if not isinstance(termo, str):
                    self.registrar_erro(
                        "Termo inválido: não é string",
                        {"termo": termo, "tipo": str(type(termo))}
                    )
                    continue
                if await self.validar_termo(termo):
                    termos_validos.append(termo)
            
            # Coleta métricas para cada termo
            keywords = []
            for termo in termos_validos:
                try:
                    # Verifica cache
                    cache_key = f"keyword:{termo}"
                    cached = await self.cache.get(cache_key)
                    if cached:
                        keyword = Keyword(**cached)
                        keywords.append(keyword)
                        continue
                    
                    # Coleta métricas específicas
                    metricas = await self.extrair_metricas_especificas(termo)
                    
                    # Valida métricas
                    intencao = metricas["intencao"]
                    if isinstance(intencao, str):
                        try:
                            intencao = IntencaoBusca(intencao)
                        except Exception:
                            intencao = IntencaoBusca.INFORMACIONAL
                    if self._validar_metricas(metricas):
                        keyword = Keyword(
                            termo=termo,
                            fonte=self.nome,
                            volume_busca=metricas["volume"],
                            cpc=metricas["cpc"],
                            concorrencia=metricas["concorrencia"],
                            intencao=intencao,
                            metadados=metricas.get("metadados", {})
                        )
                        
                        # Salva no cache
                        await self.cache.set(
                            cache_key,
                            keyword.dict(),
                            ttl=CACHE_CONFIG["ttl_keywords"]
                        )
                        
                        keywords.append(keyword)
                        
                except Exception as e:
                    self.registrar_erro(
                        "Erro ao coletar keyword",
                        {"erro": str(e), "termo": termo}
                    )
                    continue
                
                # Respeita rate limit
                await asyncio.sleep(60 / self.rate_limit)

                logger.error({
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": "debug_termo_coleta",
                    "status": "debug",
                    "source": f"coletor.{self.nome}",
                    "termo": termo,
                    "tipo": str(type(termo))
                })
            
            self.registrar_sucesso("coleta_keywords", {
                "total_termos": len(termos),
                "termos_validos": len(termos_validos),
                "keywords_coletadas": len(keywords)
            })
            
            return keywords
            
        except Exception as e:
            self.registrar_erro(
                "Erro ao coletar keywords",
                {"erro": str(e)}
            )
            return []

    def _validar_metricas(self, metricas: Dict) -> bool:
        """
        Valida as métricas coletadas.
        
        Args:
            metricas: Dicionário com métricas
            
        Returns:
            True se métricas são válidas
        """
        return True

    def registrar_erro(self, mensagem: str, detalhes: Dict[str, Any]) -> None:
        """
        Registra um erro ocorrido durante a coleta e adiciona à lista self.erros.
        """
        self.erros.append(mensagem)
        logger.error({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "erro_coletor",
            "status": "error",
            "source": f"coletor.{self.nome}",
            "message": mensagem,
            "details": detalhes or {}
        })

    def registrar_sucesso(self, evento: str, detalhes: Dict[str, Any]) -> None:
        """
        Registra um evento de sucesso do coletor.
        
        Args:
            evento: Nome do evento
            detalhes: Detalhes adicionais
        """
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": evento,
            "status": "success", 
            "source": f"coletor.{self.nome}",
            "details": detalhes
        })

    def obter_data_atual(self):
        """Retorna a data/hora atual em UTC para uso em data_coleta."""
        return datetime.utcnow()

    def calcular_relevancia(self, *args, **kwargs) -> float:
        """Stub de cálculo de relevância. Deve ser implementado conforme a fonte."""
        return 1.0 