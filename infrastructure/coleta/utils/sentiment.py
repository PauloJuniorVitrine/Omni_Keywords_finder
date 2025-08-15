"""
Implementação de análise de sentimento para os coletores.
"""
from typing import Dict, List, Tuple
from textblob import TextBlob
from datetime import datetime
from shared.logger import logger

class AnalisadorSentimento:
    """Analisador de sentimento usando TextBlob."""
    
    def __init__(self):
        """Inicializa o analisador de sentimento."""
        self.total_analises = 0
        
    async def analisar_texto(self, texto: str) -> Dict:
        """
        Analisa o sentimento de um texto.
        
        Args:
            texto: Texto para análise
            
        Returns:
            Dicionário com polaridade e subjetividade
        """
        try:
            blob = TextBlob(texto)
            self.total_analises += 1
            
            resultado = {
                "polaridade": blob.sentiment.polarity,
                "subjetividade": blob.sentiment.subjectivity,
                "classificacao": self._classificar_polaridade(blob.sentiment.polarity)
            }
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "analise_sentimento",
                "status": "success",
                "source": "sentiment.analyzer",
                "details": {
                    "tamanho_texto": len(texto),
                    "resultado": resultado,
                    "total_analises": self.total_analises
                }
            })
            
            return resultado
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_analise_sentimento",
                "status": "error",
                "source": "sentiment.analyzer",
                "details": {"erro": str(e)}
            })
            return {
                "polaridade": 0.0,
                "subjetividade": 0.0,
                "classificacao": "neutro"
            }
            
    async def analisar_textos(self, textos: List[str]) -> List[Dict]:
        """
        Analisa o sentimento de múltiplos textos.
        
        Args:
            textos: Lista de textos para análise
            
        Returns:
            Lista de resultados de análise
        """
        return [await self.analisar_texto(texto) for texto in textos]
        
    async def analisar_comentarios(
        self,
        comentarios: List[Dict]
    ) -> List[Tuple[Dict, Dict]]:
        """
        Analisa sentimento de comentários com metadados.
        
        Args:
            comentarios: Lista de dicionários com texto e metadados
            
        Returns:
            Lista de tuplas (comentário original, análise)
        """
        resultados = []
        for comentario in comentarios:
            if "texto" in comentario:
                analise = await self.analisar_texto(comentario["texto"])
                resultados.append((comentario, analise))
        return resultados
        
    def _classificar_polaridade(self, polaridade: float) -> str:
        """
        Classifica a polaridade em categorias.
        
        Args:
            polaridade: Valor de polaridade (-1 a 1)
            
        Returns:
            Classificação textual do sentimento
        """
        if polaridade > 0.3:
            return "positivo"
        elif polaridade < -0.3:
            return "negativo"
        else:
            return "neutro" 