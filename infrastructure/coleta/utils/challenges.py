"""
Implementação de análise de desafios (challenges) para o TikTok.
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from shared.logger import logger

class AnalisadorDesafios:
    """Analisador de desafios do TikTok."""
    
    def __init__(self):
        """Inicializa o analisador de desafios."""
        self.desafios = {}
        
    async def registrar_desafio(
        self,
        desafio_id: str,
        nome: str,
        descricao: str,
        total_videos: int,
        total_views: int,
        hashtags: List[str],
        criador: Optional[str] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None
    ) -> None:
        """
        Registra um desafio para análise.
        
        Args:
            desafio_id: ID do desafio
            nome: Nome do desafio
            descricao: Descrição do desafio
            total_videos: Total de vídeos
            total_views: Total de visualizações
            hashtags: Lista de hashtags associadas
            criador: Nome do criador (opcional)
            data_inicio: Data de início (opcional)
            data_fim: Data de fim (opcional)
        """
        if desafio_id not in self.desafios:
            self.desafios[desafio_id] = []
            
        registro = {
            "timestamp": datetime.utcnow(),
            "nome": nome,
            "descricao": descricao,
            "total_videos": total_videos,
            "total_views": total_views,
            "hashtags": hashtags,
            "criador": criador,
            "data_inicio": data_inicio.isoformat() if data_inicio else None,
            "data_fim": data_fim.isoformat() if data_fim else None
        }
        
        self.desafios[desafio_id].append(registro)
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "registro_desafio",
            "status": "success",
            "source": "challenges.analyzer",
            "details": {
                "desafio_id": desafio_id,
                "nome": nome,
                "total_videos": total_videos
            }
        })
        
    async def analisar_desafio(
        self,
        desafio_id: str,
        min_views: int = 1000000
    ) -> Dict:
        """
        Analisa métricas de um desafio.
        
        Args:
            desafio_id: ID do desafio
            min_views: Mínimo de views para ser viral
            
        Returns:
            Dicionário com métricas do desafio
        """
        try:
            if desafio_id not in self.desafios:
                return self._metricas_vazias()
                
            registros = self.desafios[desafio_id]
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
                
            # Determina viralidade
            is_viral = ultimo["total_views"] >= min_views
            
            # Calcula duração
            duracao = None
            if ultimo["data_inicio"] and ultimo["data_fim"]:
                inicio = datetime.fromisoformat(ultimo["data_inicio"])
                fim = datetime.fromisoformat(ultimo["data_fim"])
                duracao = (fim - inicio).days
                
            resultado = {
                "nome": ultimo["nome"],
                "descricao": ultimo["descricao"],
                "total_videos": ultimo["total_videos"],
                "total_views": ultimo["total_views"],
                "engagement": engagement,
                "crescimento_videos": crescimento_videos,
                "crescimento_views": crescimento_views,
                "is_viral": is_viral,
                "hashtags": ultimo["hashtags"],
                "criador": ultimo["criador"],
                "data_inicio": ultimo["data_inicio"],
                "data_fim": ultimo["data_fim"],
                "duracao_dias": duracao,
                "ultima_atualizacao": ultimo["timestamp"].isoformat()
            }
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "analise_desafio",
                "status": "success",
                "source": "challenges.analyzer",
                "details": {
                    "desafio_id": desafio_id,
                    "resultado": resultado
                }
            })
            
            return resultado
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_analise_desafio",
                "status": "error",
                "source": "challenges.analyzer",
                "details": {
                    "erro": str(e),
                    "desafio_id": desafio_id
                }
            })
            return self._metricas_vazias()
            
    async def analisar_tendencias(
        self,
        min_crescimento: float = 100.0,
        periodo_dias: int = 7
    ) -> Dict:
        """
        Analisa tendências entre desafios.
        
        Args:
            min_crescimento: Crescimento mínimo para ser tendência
            periodo_dias: Período em dias para análise
            
        Returns:
            Dicionário com análise de tendências
        """
        try:
            data_corte = datetime.utcnow() - timedelta(days=periodo_dias)
            resultados = []
            
            for desafio_id in self.desafios:
                metricas = await self.analisar_desafio(desafio_id)
                
                # Verifica se é tendência
                if (
                    metricas["crescimento_views"] >= min_crescimento and
                    metricas["data_inicio"] and
                    datetime.fromisoformat(metricas["data_inicio"]) >= data_corte
                ):
                    resultados.append({
                        "desafio_id": desafio_id,
                        **metricas
                    })
                    
            # Ordena por crescimento
            resultados.sort(
                key=lambda value: value["crescimento_views"],
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
                
                media_duracao = sum(
                    r["duracao_dias"] for r in resultados
                    if r["duracao_dias"] is not None
                ) / len([r for r in resultados if r["duracao_dias"] is not None])
            else:
                media_videos = 0
                media_views = 0
                media_engagement = 0
                media_duracao = 0
                
            resultado = {
                "total_desafios": len(resultados),
                "desafios_tendencia": resultados[:5],  # Top 5
                "media_videos": media_videos,
                "media_views": media_views,
                "media_engagement": media_engagement,
                "media_duracao_dias": media_duracao,
                "periodo_analise": {
                    "inicio": data_corte.isoformat(),
                    "fim": datetime.utcnow().isoformat()
                }
            }
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "analise_tendencias_desafios",
                "status": "success",
                "source": "challenges.analyzer",
                "details": {
                    "total_desafios": len(resultados),
                    "periodo_dias": periodo_dias
                }
            })
            
            return resultado
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_analise_tendencias_desafios",
                "status": "error",
                "source": "challenges.analyzer",
                "details": {"erro": str(e)}
            })
            return {
                "total_desafios": 0,
                "desafios_tendencia": [],
                "media_videos": 0,
                "media_views": 0,
                "media_engagement": 0,
                "media_duracao_dias": 0,
                "periodo_analise": {
                    "inicio": data_corte.isoformat(),
                    "fim": datetime.utcnow().isoformat()
                }
            }
            
    def _metricas_vazias(self) -> Dict:
        """Retorna dicionário padrão para desafio sem dados."""
        return {
            "nome": "",
            "descricao": "",
            "total_videos": 0,
            "total_views": 0,
            "engagement": 0.0,
            "crescimento_videos": 0.0,
            "crescimento_views": 0.0,
            "is_viral": False,
            "hashtags": [],
            "criador": None,
            "data_inicio": None,
            "data_fim": None,
            "duracao_dias": None,
            "ultima_atualizacao": datetime.utcnow().isoformat()
        } 