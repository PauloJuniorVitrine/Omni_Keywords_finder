"""
Módulo: async_coletor_v1
Coleta assíncrona e paralela de palavras-chave de múltiplas fontes.
Integração com cache e logging estruturado.
"""
import asyncio
from typing import List, Dict, Callable, Any
import logging

class AsyncColetor:
    def __init__(self, fontes: List[Callable[..., Any]], cache=None, logger=None):
        """
        fontes: lista de funções async de coleta (ex: google, trends, amazon...)
        cache: objeto de cache (opcional)
        logger: logger estruturado (opcional)
        """
        self.fontes = fontes
        self.cache = cache
        self.logger = logger or logging.getLogger("async_coletor")

    async def coletar(self, termo: str, filtros: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Coleta palavras-chave de todas as fontes em paralelo, aplicando filtros.
        Usa cache se disponível.
        """
        resultados = []
        filtros = filtros or {}
        cache_key = f"keywords:{termo}:{str(filtros)}"
        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached:
                self.logger.info({"event": "cache_hit", "termo": termo, "filtros": filtros})
                return cached
        tasks = [fonte(termo, **filtros) for fonte in self.fontes]
        try:
            resultados = await asyncio.gather(*tasks, return_exceptions=True)
            # Filtrar exceções e logar falhas
            final = []
            for idx, r in enumerate(resultados):
                if isinstance(r, Exception):
                    self.logger.error({"event": "coleta_falha", "fonte": self.fontes[idx].__name__, "erro": str(r)})
                else:
                    final.extend(r)
            if self.cache:
                await self.cache.set(cache_key, final)
            self.logger.info({"event": "coleta_sucesso", "termo": termo, "total": len(final)})
            return final
        except Exception as e:
            self.logger.error({"event": "coleta_erro_geral", "termo": termo, "erro": str(e)})
            return [] 