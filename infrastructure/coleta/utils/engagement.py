"""
Implementação de análise de métricas de engajamento para os coletores.
"""
from typing import Dict, List, Optional
from datetime import datetime
import numpy as np
from shared.logger import logger

class AnalisadorEngajamento:
    """Analisador de métricas de engajamento."""
    
    def __init__(self):
        """Inicializa o analisador de engajamento."""
        self.metricas = {}
        
    async def registrar_metricas(
        self,
        item_id: str,
        metricas: Dict[str, float],
        tipo: str,
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        Registra métricas de engajamento de um item.
        
        Args:
            item_id: Identificador do item
            metricas: Dicionário com métricas
            tipo: Tipo do item (post, video, etc)
            timestamp: Momento do registro
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
            
        if item_id not in self.metricas:
            self.metricas[item_id] = []
            
        registro = {
            "timestamp": timestamp,
            "tipo": tipo,
            **metricas
        }
        
        self.metricas[item_id].append(registro)
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "registro_metricas_engajamento",
            "status": "success",
            "source": "engagement.analyzer",
            "details": {
                "item_id": item_id,
                "tipo": tipo,
                "metricas": metricas
            }
        })
        
    async def calcular_engajamento(
        self,
        item_id: str,
        metrica_base: str = "impressoes"
    ) -> Dict:
        """
        Calcula taxa de engajamento de um item.
        
        Args:
            item_id: Identificador do item
            metrica_base: Métrica base para cálculo
            
        Returns:
            Dicionário com taxas de engajamento
        """
        try:
            if item_id not in self.metricas:
                return self._engajamento_vazio()
                
            registros = self.metricas[item_id]
            if not registros:
                return self._engajamento_vazio()
                
            ultimo_registro = registros[-1]
            metricas = {
                key: value for key, value in ultimo_registro.items()
                if isinstance(value, (int, float))
            }
            
            if metrica_base not in metricas:
                return self._engajamento_vazio()
                
            base = float(metricas[metrica_base])
            if base == 0:
                return self._engajamento_vazio()
                
            taxas = {}
            for metrica, valor in metricas.items():
                if metrica != metrica_base:
                    taxa = (float(valor) / base) * 100
                    taxas[f"taxa_{metrica}"] = taxa
                    
            resultado = {
                "metricas_brutas": metricas,
                "taxas_engajamento": taxas,
                "tipo": ultimo_registro["tipo"],
                "ultima_atualizacao": ultimo_registro["timestamp"].isoformat()
            }
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "calculo_engajamento",
                "status": "success",
                "source": "engagement.analyzer",
                "details": {
                    "item_id": item_id,
                    "metrica_base": metrica_base,
                    "resultado": resultado
                }
            })
            
            return resultado
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_calculo_engajamento",
                "status": "error",
                "source": "engagement.analyzer",
                "details": {
                    "erro": str(e),
                    "item_id": item_id
                }
            })
            return self._engajamento_vazio()
            
    async def comparar_engajamento(
        self,
        items: List[str],
        metrica: str
    ) -> Dict:
        """
        Compara engajamento entre múltiplos items.
        
        Args:
            items: Lista de IDs dos items
            metrica: Métrica para comparação
            
        Returns:
            Dicionário com análise comparativa
        """
        try:
            valores = []
            for item_id in items:
                if item_id in self.metricas:
                    registros = self.metricas[item_id]
                    if registros:
                        ultimo = registros[-1]
                        if metrica in ultimo:
                            valores.append({
                                "item_id": item_id,
                                "valor": float(ultimo[metrica]),
                                "tipo": ultimo["tipo"]
                            })
                            
            if not valores:
                return {
                    "total_items": 0,
                    "media": 0.0,
                    "mediana": 0.0,
                    "ranking": []
                }
                
            # Ordena por valor da métrica
            valores.sort(key=lambda value: value["valor"], reverse=True)
            
            # Calcula estatísticas
            valores_numericos = [value["valor"] for value in valores]
            resultado = {
                "total_items": len(valores),
                "media": float(np.mean(valores_numericos)),
                "mediana": float(np.median(valores_numericos)),
                "ranking": valores
            }
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "comparacao_engajamento",
                "status": "success",
                "source": "engagement.analyzer",
                "details": {
                    "total_items": len(items),
                    "metrica": metrica,
                    "resultado": resultado
                }
            })
            
            return resultado
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_comparacao_engajamento",
                "status": "error",
                "source": "engagement.analyzer",
                "details": {
                    "erro": str(e),
                    "metrica": metrica
                }
            })
            return {
                "total_items": 0,
                "media": 0.0,
                "mediana": 0.0,
                "ranking": []
            }
            
    def _engajamento_vazio(self) -> Dict:
        """Retorna dicionário padrão para item sem métricas."""
        return {
            "metricas_brutas": {},
            "taxas_engajamento": {},
            "tipo": "desconhecido",
            "ultima_atualizacao": datetime.utcnow().isoformat()
        } 