"""
Implementação de análise de hashtags para o TikTok.
"""
from typing import Dict, List, Optional, Set
from datetime import datetime
from shared.logger import logger

class AnalisadorHashtags:
    """Analisador de hashtags do TikTok."""
    
    def __init__(self):
        """Inicializa o analisador de hashtags."""
        self.hashtags = {}
        self.categorias = {}
        
    async def registrar_hashtag(
        self,
        hashtag: str,
        total_videos: int,
        total_views: int,
        categorias: List[str],
        relacionadas: List[str]
    ) -> None:
        """
        Registra uma hashtag para análise.
        
        Args:
            hashtag: Nome da hashtag
            total_videos: Total de vídeos
            total_views: Total de visualizações
            categorias: Lista de categorias
            relacionadas: Lista de hashtags relacionadas
        """
        if hashtag not in self.hashtags:
            self.hashtags[hashtag] = []
            
        registro = {
            "timestamp": datetime.utcnow(),
            "total_videos": total_videos,
            "total_views": total_views,
            "categorias": categorias,
            "relacionadas": relacionadas
        }
        
        self.hashtags[hashtag].append(registro)
        
        # Atualiza contadores por categoria
        for categoria in categorias:
            if categoria not in self.categorias:
                self.categorias[categoria] = {
                    "total_hashtags": 0,
                    "total_videos": 0,
                    "total_views": 0
                }
            self.categorias[categoria]["total_hashtags"] += 1
            self.categorias[categoria]["total_videos"] += total_videos
            self.categorias[categoria]["total_views"] += total_views
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "registro_hashtag",
            "status": "success",
            "source": "hashtags.analyzer",
            "details": {
                "hashtag": hashtag,
                "total_videos": total_videos,
                "categorias": categorias
            }
        })
        
    async def analisar_hashtag(
        self,
        hashtag: str,
        min_views: int = 100000
    ) -> Dict:
        """
        Analisa métricas de uma hashtag.
        
        Args:
            hashtag: Nome da hashtag
            min_views: Mínimo de views para ser relevante
            
        Returns:
            Dicionário com métricas da hashtag
        """
        try:
            if hashtag not in self.hashtags:
                return self._metricas_vazias()
                
            registros = self.hashtags[hashtag]
            if not registros:
                return self._metricas_vazias()
                
            ultimo = registros[-1]
            
            # Calcula taxa de engajamento
            engagement = (
                ultimo["total_views"] /
                max(1, ultimo["total_videos"])
            )
            
            # Calcula crescimento
            if len(registros) >= 2:
                primeiro = registros[0]
                crescimento_videos = (
                    (ultimo["total_videos"] - primeiro["total_videos"]) /
                    max(1, primeiro["total_videos"]) * 100
                )
                crescimento_views = (
                    (ultimo["total_views"] - primeiro["total_views"]) /
                    max(1, primeiro["total_views"]) * 100
                )
            else:
                crescimento_videos = 0
                crescimento_views = 0
                
            # Determina relevância
            is_relevante = ultimo["total_views"] >= min_views
            
            resultado = {
                "total_videos": ultimo["total_videos"],
                "total_views": ultimo["total_views"],
                "engagement": engagement,
                "crescimento_videos": crescimento_videos,
                "crescimento_views": crescimento_views,
                "is_relevante": is_relevante,
                "categorias": ultimo["categorias"],
                "relacionadas": ultimo["relacionadas"],
                "ultima_atualizacao": ultimo["timestamp"].isoformat()
            }
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "analise_hashtag",
                "status": "success",
                "source": "hashtags.analyzer",
                "details": {
                    "hashtag": hashtag,
                    "resultado": resultado
                }
            })
            
            return resultado
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_analise_hashtag",
                "status": "error",
                "source": "hashtags.analyzer",
                "details": {
                    "erro": str(e),
                    "hashtag": hashtag
                }
            })
            return self._metricas_vazias()
            
    async def analisar_categorias(self) -> Dict:
        """
        Analisa métricas por categoria.
        
        Returns:
            Dicionário com métricas por categoria
        """
        try:
            resultados = {}
            for categoria, metricas in self.categorias.items():
                # Calcula médias
                media_videos = (
                    metricas["total_videos"] /
                    max(1, metricas["total_hashtags"])
                )
                media_views = (
                    metricas["total_views"] /
                    max(1, metricas["total_hashtags"])
                )
                
                resultados[categoria] = {
                    "total_hashtags": metricas["total_hashtags"],
                    "total_videos": metricas["total_videos"],
                    "total_views": metricas["total_views"],
                    "media_videos": media_videos,
                    "media_views": media_views
                }
                
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "analise_categorias",
                "status": "success",
                "source": "hashtags.analyzer",
                "details": {
                    "total_categorias": len(resultados)
                }
            })
            
            return resultados
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_analise_categorias",
                "status": "error",
                "source": "hashtags.analyzer",
                "details": {"erro": str(e)}
            })
            return {}
            
    async def analisar_relacionamentos(
        self,
        min_ocorrencias: int = 2
    ) -> Dict[str, Set[str]]:
        """
        Analisa relacionamentos entre hashtags.
        
        Args:
            min_ocorrencias: Mínimo de ocorrências para considerar relacionamento
            
        Returns:
            Dicionário com hashtags relacionadas por hashtag
        """
        try:
            # Conta ocorrências de relacionamentos
            contagem = {}
            for hashtag, registros in self.hashtags.items():
                if not registros:
                    continue
                    
                ultimo = registros[-1]
                for relacionada in ultimo["relacionadas"]:
                    par = tuple(sorted([hashtag, relacionada]))
                    contagem[par] = contagem.get(par, 0) + 1
                    
            # Filtra relacionamentos relevantes
            relacionamentos = {}
            for (h1, h2), ocorrencias in contagem.items():
                if ocorrencias >= min_ocorrencias:
                    if h1 not in relacionamentos:
                        relacionamentos[h1] = set()
                    if h2 not in relacionamentos:
                        relacionamentos[h2] = set()
                        
                    relacionamentos[h1].add(h2)
                    relacionamentos[h2].add(h1)
                    
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "analise_relacionamentos",
                "status": "success",
                "source": "hashtags.analyzer",
                "details": {
                    "total_hashtags": len(relacionamentos),
                    "min_ocorrencias": min_ocorrencias
                }
            })
            
            return relacionamentos
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_analise_relacionamentos",
                "status": "error",
                "source": "hashtags.analyzer",
                "details": {"erro": str(e)}
            })
            return {}
            
    def _metricas_vazias(self) -> Dict:
        """Retorna dicionário padrão para hashtag sem dados."""
        return {
            "total_videos": 0,
            "total_views": 0,
            "engagement": 0.0,
            "crescimento_videos": 0.0,
            "crescimento_views": 0.0,
            "is_relevante": False,
            "categorias": [],
            "relacionadas": [],
            "ultima_atualizacao": datetime.utcnow().isoformat()
        } 