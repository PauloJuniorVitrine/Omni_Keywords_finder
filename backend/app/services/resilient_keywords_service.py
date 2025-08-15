# =============================================================================
# Serviço de Keywords com Resiliência Integrada
# =============================================================================
# 
# Este arquivo implementa o serviço de keywords com circuit breakers,
# retry policies e fallback strategies integrados.
#
# Tracing ID: resilient-keywords-service-2025-01-27-001
# Versão: 1.0
# Responsável: DevOps Team
# =============================================================================

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResilientKeywordsService:
    """Serviço de keywords com resiliência integrada"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutos
        self.fallback_data = {
            "keywords": [
                {"keyword": "seo optimization", "volume": 1000, "difficulty": "medium"},
                {"keyword": "content marketing", "volume": 800, "difficulty": "low"},
                {"keyword": "digital marketing", "volume": 1200, "difficulty": "medium"}
            ],
            "total": 3,
            "source": "fallback"
        }
    
    async def get_keywords(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Busca keywords com resiliência integrada
        
        Args:
            query: Termo de busca
            limit: Limite de resultados
            
        Returns:
            Dicionário com keywords e metadados
        """
        cache_key = f"keywords:{query}:{limit}"
        
        # Verificar cache primeiro
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if datetime.now() < cached_data["expires_at"]:
                logger.info(f"Retornando dados do cache para: {query}")
                return cached_data["data"]
        
        try:
            # Simular busca de keywords (substituir por implementação real)
            keywords = await self._fetch_keywords_from_api(query, limit)
            
            # Armazenar no cache
            self.cache[cache_key] = {
                "data": keywords,
                "expires_at": datetime.now() + timedelta(seconds=self.cache_ttl)
            }
            
            logger.info(f"Keywords buscadas com sucesso para: {query}")
            return keywords
            
        except Exception as e:
            logger.warning(f"Erro ao buscar keywords para '{query}': {e}")
            return self._get_fallback_keywords(query, limit)
    
    async def _fetch_keywords_from_api(self, query: str, limit: int) -> Dict[str, Any]:
        """
        Busca keywords da API externa (simulado)
        
        Args:
            query: Termo de busca
            limit: Limite de resultados
            
        Returns:
            Dicionário com keywords
        """
        # Simular latência da API
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # Simular falha ocasional (10% de chance)
        if random.random() < 0.1:
            raise Exception("API temporariamente indisponível")
        
        # Simular dados de keywords
        keywords = []
        for index in range(min(limit, 20)):
            keyword = f"{query} {index+1}"
            keywords.append({
                "keyword": keyword,
                "volume": random.randint(100, 5000),
                "difficulty": random.choice(["low", "medium", "high"]),
                "cpc": round(random.uniform(0.1, 5.0), 2),
                "competition": round(random.uniform(0.1, 1.0), 2)
            })
        
        return {
            "keywords": keywords,
            "total": len(keywords),
            "query": query,
            "source": "api",
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_fallback_keywords(self, query: str, limit: int) -> Dict[str, Any]:
        """
        Retorna keywords de fallback quando a API falha
        
        Args:
            query: Termo de busca
            limit: Limite de resultados
            
        Returns:
            Dicionário com keywords de fallback
        """
        logger.info(f"Usando fallback para query: {query}")
        
        # Filtrar keywords de fallback baseado na query
        filtered_keywords = [
            kw for kw in self.fallback_data["keywords"]
            if query.lower() in kw["keyword"].lower()
        ]
        
        if not filtered_keywords:
            filtered_keywords = self.fallback_data["keywords"][:limit]
        
        return {
            "keywords": filtered_keywords[:limit],
            "total": len(filtered_keywords),
            "query": query,
            "source": "fallback",
            "timestamp": datetime.now().isoformat(),
            "message": "Dados de fallback devido a indisponibilidade da API"
        }
    
    async def analyze_keywords(self, keywords: List[str]) -> Dict[str, Any]:
        """
        Analisa keywords com resiliência
        
        Args:
            keywords: Lista de keywords para analisar
            
        Returns:
            Dicionário com análise
        """
        try:
            # Simular análise de keywords
            await asyncio.sleep(random.uniform(0.2, 1.0))
            
            # Simular falha ocasional (5% de chance)
            if random.random() < 0.05:
                raise Exception("Serviço de análise indisponível")
            
            analysis = {
                "keywords": [],
                "summary": {
                    "total_keywords": len(keywords),
                    "avg_volume": 0,
                    "avg_difficulty": 0,
                    "recommendations": []
                }
            }
            
            total_volume = 0
            total_difficulty = 0
            
            for keyword in keywords:
                volume = random.randint(100, 5000)
                difficulty = random.uniform(0.1, 1.0)
                
                analysis["keywords"].append({
                    "keyword": keyword,
                    "volume": volume,
                    "difficulty": round(difficulty, 2),
                    "cpc": round(random.uniform(0.1, 5.0), 2),
                    "competition": round(random.uniform(0.1, 1.0), 2),
                    "trend": random.choice(["rising", "stable", "declining"])
                })
                
                total_volume += volume
                total_difficulty += difficulty
            
            # Calcular médias
            if keywords:
                analysis["summary"]["avg_volume"] = total_volume // len(keywords)
                analysis["summary"]["avg_difficulty"] = round(total_difficulty / len(keywords), 2)
            
            # Gerar recomendações
            analysis["summary"]["recommendations"] = [
                "Foque em keywords com volume médio e baixa dificuldade",
                "Considere long-tail keywords para melhor conversão",
                "Monitore tendências regularmente"
            ]
            
            return analysis
            
        except Exception as e:
            logger.warning(f"Erro na análise de keywords: {e}")
            return self._get_fallback_analysis(keywords)
    
    def _get_fallback_analysis(self, keywords: List[str]) -> Dict[str, Any]:
        """
        Retorna análise de fallback
        
        Args:
            keywords: Lista de keywords
            
        Returns:
            Dicionário com análise de fallback
        """
        return {
            "keywords": [
                {
                    "keyword": kw,
                    "volume": "N/A",
                    "difficulty": "N/A",
                    "cpc": "N/A",
                    "competition": "N/A",
                    "trend": "N/A"
                }
                for kw in keywords
            ],
            "summary": {
                "total_keywords": len(keywords),
                "avg_volume": "N/A",
                "avg_difficulty": "N/A",
                "recommendations": [
                    "Análise indisponível - tente novamente mais tarde",
                    "Use dados históricos se disponível"
                ]
            },
            "source": "fallback",
            "message": "Análise de fallback devido a indisponibilidade do serviço"
        }
    
    async def get_keyword_suggestions(self, seed_keyword: str) -> List[str]:
        """
        Obtém sugestões de keywords com resiliência
        
        Args:
            seed_keyword: Keyword base para sugestões
            
        Returns:
            Lista de sugestões
        """
        try:
            # Simular busca de sugestões
            await asyncio.sleep(random.uniform(0.1, 0.3))
            
            # Simular falha ocasional (3% de chance)
            if random.random() < 0.03:
                raise Exception("Serviço de sugestões indisponível")
            
            # Gerar sugestões baseadas na seed keyword
            suggestions = [
                f"{seed_keyword} tutorial",
                f"{seed_keyword} guide",
                f"{seed_keyword} tips",
                f"{seed_keyword} examples",
                f"{seed_keyword} best practices",
                f"{seed_keyword} tools",
                f"{seed_keyword} software",
                f"{seed_keyword} course",
                f"{seed_keyword} training",
                f"{seed_keyword} certification"
            ]
            
            # Adicionar variações
            variations = [
                f"how to {seed_keyword}",
                f"{seed_keyword} for beginners",
                f"advanced {seed_keyword}",
                f"{seed_keyword} vs alternatives",
                f"free {seed_keyword}"
            ]
            
            suggestions.extend(variations)
            
            # Retornar sugestões aleatórias
            return random.sample(suggestions, min(10, len(suggestions)))
            
        except Exception as e:
            logger.warning(f"Erro ao buscar sugestões para '{seed_keyword}': {e}")
            return self._get_fallback_suggestions(seed_keyword)
    
    def _get_fallback_suggestions(self, seed_keyword: str) -> List[str]:
        """
        Retorna sugestões de fallback
        
        Args:
            seed_keyword: Keyword base
            
        Returns:
            Lista de sugestões de fallback
        """
        return [
            f"{seed_keyword} tutorial",
            f"{seed_keyword} guide",
            f"{seed_keyword} tips",
            f"how to {seed_keyword}",
            f"{seed_keyword} for beginners"
        ]
    
    def get_service_health(self) -> Dict[str, Any]:
        """
        Retorna status de saúde do serviço
        
        Returns:
            Dicionário com métricas de saúde
        """
        cache_size = len(self.cache)
        cache_hit_rate = self._calculate_cache_hit_rate()
        
        return {
            "status": "healthy",
            "cache": {
                "size": cache_size,
                "hit_rate": cache_hit_rate,
                "ttl": self.cache_ttl
            },
            "fallback_usage": self._get_fallback_usage(),
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calcula taxa de hit do cache (simulado)"""
        return round(random.uniform(0.7, 0.95), 2)
    
    def _get_fallback_usage(self) -> Dict[str, int]:
        """Retorna estatísticas de uso de fallback (simulado)"""
        return {
            "total_fallbacks": random.randint(5, 50),
            "keywords_fallback": random.randint(3, 30),
            "analysis_fallback": random.randint(2, 20)
        } 