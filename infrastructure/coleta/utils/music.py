"""
Implementação de análise de músicas para o TikTok.
"""
from typing import Dict, List, Optional
from datetime import datetime
from shared.logger import logger

class AnalisadorMusica:
    """Analisador de músicas do TikTok."""
    
    def __init__(self):
        """Inicializa o analisador de músicas."""
        self.musicas = {}
        
    async def registrar_musica(
        self,
        musica_id: str,
        titulo: str,
        artista: str,
        duracao: int,
        total_videos: int,
        total_views: int
    ) -> None:
        """
        Registra uma música para análise.
        
        Args:
            musica_id: ID da música
            titulo: Título da música
            artista: Nome do artista
            duracao: Duração em segundos
            total_videos: Total de vídeos usando a música
            total_views: Total de visualizações
        """
        if musica_id not in self.musicas:
            self.musicas[musica_id] = []
            
        registro = {
            "timestamp": datetime.utcnow(),
            "titulo": titulo,
            "artista": artista,
            "duracao": duracao,
            "total_videos": total_videos,
            "total_views": total_views
        }
        
        self.musicas[musica_id].append(registro)
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "registro_musica",
            "status": "success",
            "source": "music.analyzer",
            "details": {
                "musica_id": musica_id,
                "titulo": titulo,
                "artista": artista,
                "total_videos": total_videos
            }
        })
        
    async def analisar_popularidade(
        self,
        musica_id: str,
        min_videos: int = 1000
    ) -> Dict:
        """
        Analisa popularidade de uma música.
        
        Args:
            musica_id: ID da música
            min_videos: Mínimo de vídeos para ser considerada popular
            
        Returns:
            Dicionário com métricas de popularidade
        """
        try:
            if musica_id not in self.musicas:
                return self._popularidade_vazia()
                
            registros = self.musicas[musica_id]
            if not registros:
                return self._popularidade_vazia()
                
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
            else:
                crescimento_videos = 0
                
            # Determina popularidade
            is_popular = (
                ultimo["total_videos"] >= min_videos and
                engagement > 1000  # Média de 1000 views por vídeo
            )
            
            resultado = {
                "titulo": ultimo["titulo"],
                "artista": ultimo["artista"],
                "total_videos": ultimo["total_videos"],
                "total_views": ultimo["total_views"],
                "engagement": engagement,
                "crescimento_videos": crescimento_videos,
                "is_popular": is_popular,
                "duracao": ultimo["duracao"],
                "ultima_atualizacao": ultimo["timestamp"].isoformat()
            }
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "analise_popularidade_musica",
                "status": "success",
                "source": "music.analyzer",
                "details": {
                    "musica_id": musica_id,
                    "resultado": resultado
                }
            })
            
            return resultado
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_analise_popularidade_musica",
                "status": "error",
                "source": "music.analyzer",
                "details": {
                    "erro": str(e),
                    "musica_id": musica_id
                }
            })
            return self._popularidade_vazia()
            
    async def analisar_tendencias(
        self,
        musicas: List[str],
        min_crescimento: float = 50.0
    ) -> Dict:
        """
        Analisa tendências entre múltiplas músicas.
        
        Args:
            musicas: Lista de IDs de músicas
            min_crescimento: Crescimento mínimo para ser tendência
            
        Returns:
            Dicionário com análise de tendências
        """
        try:
            resultados = []
            for musica_id in musicas:
                popularidade = await self.analisar_popularidade(musica_id)
                if popularidade["crescimento_videos"] >= min_crescimento:
                    resultados.append({
                        "musica_id": musica_id,
                        **popularidade
                    })
                    
            # Ordena por crescimento
            resultados.sort(
                key=lambda value: value["crescimento_videos"],
                reverse=True
            )
            
            # Calcula médias
            if resultados:
                media_videos = sum(
                    r["total_videos"] for r in resultados
                ) / len(resultados)
                
                media_views = sum(
                    r["total_views"] for r in resultados
                ) / len(resultados)
                
                media_engagement = sum(
                    r["engagement"] for r in resultados
                ) / len(resultados)
            else:
                media_videos = 0
                media_views = 0
                media_engagement = 0
                
            resultado = {
                "total_musicas": len(resultados),
                "musicas_tendencia": resultados[:5],  # Top 5
                "media_videos": media_videos,
                "media_views": media_views,
                "media_engagement": media_engagement
            }
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "analise_tendencias_musicas",
                "status": "success",
                "source": "music.analyzer",
                "details": {
                    "total_musicas": len(musicas),
                    "musicas_tendencia": len(resultados)
                }
            })
            
            return resultado
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_analise_tendencias_musicas",
                "status": "error",
                "source": "music.analyzer",
                "details": {"erro": str(e)}
            })
            return {
                "total_musicas": 0,
                "musicas_tendencia": [],
                "media_videos": 0,
                "media_views": 0,
                "media_engagement": 0
            }
            
    def _popularidade_vazia(self) -> Dict:
        """Retorna dicionário padrão para música sem dados."""
        return {
            "titulo": "",
            "artista": "",
            "total_videos": 0,
            "total_views": 0,
            "engagement": 0.0,
            "crescimento_videos": 0.0,
            "is_popular": False,
            "duracao": 0,
            "ultima_atualizacao": datetime.utcnow().isoformat()
        } 