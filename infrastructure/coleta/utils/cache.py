"""
Cache distribuído para coletores de keywords.
Utiliza o sistema de cache centralizado com Redis e fallback local.
"""
import asyncio
from typing import Any, Optional, Dict
from shared.cache import AsyncCache, get_cache, cached
from shared.logger import logger

class CacheDistribuido:
    """
    Cache distribuído especializado para coletores.
    Implementa cache de alta performance com TTL específico para keywords.
    """
    
    def __init__(self, namespace: str = "keywords", ttl_padrao: int = 86400):
        """
        Inicializa cache distribuído.
        
        Args:
            namespace: Namespace do cache
            ttl_padrao: TTL padrão em segundos (24h para keywords)
        """
        self.namespace = namespace
        self.ttl_padrao = ttl_padrao
        self._cache: Optional[AsyncCache] = None
    
    async def _get_cache(self) -> AsyncCache:
        """Obtém instância do cache."""
        if self._cache is None:
            self._cache = await get_cache(self.namespace)
        return self._cache
    
    async def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém valor do cache.
        
        Args:
            key: Chave do cache
            default: Valor padrão se não encontrado
            
        Returns:
            Valor do cache ou default
        """
        try:
            cache = await self._get_cache()
            return await cache.get(key, default)
        except Exception as e:
            logger.error({
                "event": "cache_get_error",
                "status": "error",
                "source": "CacheDistribuido.get",
                "details": {"key": key, "error": str(e)}
            })
            return default
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Define valor no cache.
        
        Args:
            key: Chave do cache
            value: Valor a ser armazenado
            ttl: Tempo de vida em segundos (None = TTL padrão)
            
        Returns:
            True se sucesso, False caso contrário
        """
        if ttl is None:
            ttl = self.ttl_padrao
        
        try:
            cache = await self._get_cache()
            return await cache.set(key, value, ttl)
        except Exception as e:
            logger.error({
                "event": "cache_set_error",
                "status": "error",
                "source": "CacheDistribuido.set",
                "details": {"key": key, "error": str(e)}
            })
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Remove valor do cache.
        
        Args:
            key: Chave do cache
            
        Returns:
            True se removido, False se não encontrado
        """
        try:
            cache = await self._get_cache()
            return await cache.delete(key)
        except Exception as e:
            logger.error({
                "event": "cache_delete_error",
                "status": "error",
                "source": "CacheDistribuido.delete",
                "details": {"key": key, "error": str(e)}
            })
            return False
    
    async def clear(self) -> bool:
        """
        Limpa todo o cache do namespace.
        
        Returns:
            True se sucesso
        """
        try:
            cache = await self._get_cache()
            return await cache.clear()
        except Exception as e:
            logger.error({
                "event": "cache_clear_error",
                "status": "error",
                "source": "CacheDistribuido.clear",
                "details": {"error": str(e)}
            })
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Obtém métricas do cache.
        
        Returns:
            Dicionário com métricas
        """
        try:
            if self._cache:
                return self._cache.get_metrics()
            return {"error": "Cache não inicializado"}
        except Exception as e:
            logger.error({
                "event": "cache_metrics_error",
                "status": "error",
                "source": "CacheDistribuido.get_metrics",
                "details": {"error": str(e)}
            })
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Verifica saúde do cache.
        
        Returns:
            Status de saúde
        """
        try:
            cache = await self._get_cache()
            return await cache.health_check()
        except Exception as e:
            logger.error({
                "event": "cache_health_check_error",
                "status": "error",
                "source": "CacheDistribuido.health_check",
                "details": {"error": str(e)}
            })
            return {"error": str(e), "overall_healthy": False}

# Decorator especializado para cache de keywords
def cached_keywords(ttl: Optional[int] = None):
    """
    Decorator para cache automático de funções de coleta de keywords.
    
    Args:
        ttl: Tempo de vida do cache (None = TTL padrão para keywords)
    """
    if ttl is None:
        ttl = 86400  # 24 horas para keywords
    
    return cached(ttl=ttl, key_prefix="keywords")

# Decorator para cache de métricas
def cached_metrics(ttl: Optional[int] = None):
    """
    Decorator para cache automático de métricas.
    
    Args:
        ttl: Tempo de vida do cache (None = TTL padrão para métricas)
    """
    if ttl is None:
        ttl = 43200  # 12 horas para métricas
    
    return cached(ttl=ttl, key_prefix="metrics")

# Decorator para cache de tendências
def cached_trends(ttl: Optional[int] = None):
    """
    Decorator para cache automático de tendências.
    
    Args:
        ttl: Tempo de vida do cache (None = TTL padrão para tendências)
    """
    if ttl is None:
        ttl = 21600  # 6 horas para tendências
    
    return cached(ttl=ttl, key_prefix="trends")

# Exemplo de uso dos decorators
@cached_keywords()
async def exemplo_coleta_keywords(termo: str) -> Dict[str, Any]:
    """
    Exemplo de função de coleta com cache automático.
    
    Args:
        termo: Termo para coleta
        
    Returns:
        Dados coletados
    """
    # Simula coleta demorada
    await asyncio.sleep(1)
    
    return {
        "termo": termo,
        "volume": 1000,
        "cpc": 1.5,
        "concorrencia": 0.7
    }

@cached_metrics()
async def exemplo_metricas(dominio: str) -> Dict[str, Any]:
    """
    Exemplo de função de métricas com cache automático.
    
    Args:
        dominio: Domínio para análise
        
    Returns:
        Métricas calculadas
    """
    # Simula cálculo de métricas
    await asyncio.sleep(0.5)
    
    return {
        "dominio": dominio,
        "score_medio": 0.85,
        "total_keywords": 150,
        "performance": "alta"
    } 