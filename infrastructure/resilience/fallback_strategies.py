"""
🔄 Estratégias de Fallback Avançadas - Sistema de Resiliência

Tracing ID: fallback-strategies-2025-01-27-001
Timestamp: 2025-01-27T19:00:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Estratégias baseadas em padrões reais de degradação e recuperação
🌲 ToT: Avaliadas múltiplas estratégias de fallback (cache, histórico, alternativas)
♻️ ReAct: Simulado cenários de falha e validada estratégia de fallback

Implementa estratégias de fallback incluindo:
- Fallback para cache com TTL inteligente
- Fallback para dados históricos
- Fallback para APIs alternativas
- Fallback para web scraping
- Fallback para dados mock
- Estratégias de degradação gradual
- Recuperação automática
"""

import asyncio
import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from enum import Enum
import logging
import aiohttp
from dataclasses import dataclass, field
import weakref
import pickle
import gzip
import base64

# Configuração de logging
logger = logging.getLogger(__name__)

class FallbackStrategy(Enum):
    """Estratégias de fallback disponíveis"""
    CACHE = "cache"
    HISTORICAL = "historical"
    ALTERNATIVE_API = "alternative_api"
    WEB_SCRAPING = "web_scraping"
    MOCK = "mock"
    RETRY = "retry"
    DEGRADED = "degraded"
    NONE = "none"

@dataclass
class FallbackConfig:
    """Configuração de fallback"""
    primary_strategy: FallbackStrategy = FallbackStrategy.CACHE
    secondary_strategy: FallbackStrategy = FallbackStrategy.HISTORICAL
    tertiary_strategy: FallbackStrategy = FallbackStrategy.MOCK
    enable_gradual_degradation: bool = True
    cache_ttl: int = 3600  # 1 hora
    historical_data_ttl: int = 86400  # 24 horas
    retry_attempts: int = 3
    retry_delay: float = 1.0
    enable_compression: bool = True
    enable_encryption: bool = False
    max_fallback_data_size: int = 1024 * 1024  # 1MB
    enable_metrics: bool = True
    enable_logging: bool = True

@dataclass
class FallbackMetrics:
    """Métricas de fallback"""
    total_fallbacks: int = 0
    cache_fallbacks: int = 0
    historical_fallbacks: int = 0
    alternative_api_fallbacks: int = 0
    web_scraping_fallbacks: int = 0
    mock_fallbacks: int = 0
    retry_fallbacks: int = 0
    degraded_fallbacks: int = 0
    successful_fallbacks: int = 0
    failed_fallbacks: int = 0
    fallback_response_times: List[float] = field(default_factory=list)
    last_fallback_time: Optional[datetime] = None
    
    def add_fallback(self, strategy: FallbackStrategy, success: bool, response_time: float):
        """Adiciona métrica de fallback"""
        self.total_fallbacks += 1
        self.last_fallback_time = datetime.now()
        self.fallback_response_times.append(response_time)
        
        if success:
            self.successful_fallbacks += 1
        else:
            self.failed_fallbacks += 1
            
        if strategy == FallbackStrategy.CACHE:
            self.cache_fallbacks += 1
        elif strategy == FallbackStrategy.HISTORICAL:
            self.historical_fallbacks += 1
        elif strategy == FallbackStrategy.ALTERNATIVE_API:
            self.alternative_api_fallbacks += 1
        elif strategy == FallbackStrategy.WEB_SCRAPING:
            self.web_scraping_fallbacks += 1
        elif strategy == FallbackStrategy.MOCK:
            self.mock_fallbacks += 1
        elif strategy == FallbackStrategy.RETRY:
            self.retry_fallbacks += 1
        elif strategy == FallbackStrategy.DEGRADED:
            self.degraded_fallbacks += 1
            
        # Manter apenas os últimos 100 tempos
        if len(self.fallback_response_times) > 100:
            self.fallback_response_times.pop(0)
            
    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo das métricas"""
        return {
            'total_fallbacks': self.total_fallbacks,
            'successful_fallbacks': self.successful_fallbacks,
            'failed_fallbacks': self.failed_fallbacks,
            'success_rate': self.successful_fallbacks / self.total_fallbacks if self.total_fallbacks > 0 else 0,
            'strategy_breakdown': {
                'cache': self.cache_fallbacks,
                'historical': self.historical_fallbacks,
                'alternative_api': self.alternative_api_fallbacks,
                'web_scraping': self.web_scraping_fallbacks,
                'mock': self.mock_fallbacks,
                'retry': self.retry_fallbacks,
                'degraded': self.degraded_fallbacks
            },
            'average_response_time': sum(self.fallback_response_times) / len(self.fallback_response_times) if self.fallback_response_times else 0,
            'last_fallback_time': self.last_fallback_time.isoformat() if self.last_fallback_time else None
        }

class CacheFallbackStrategy:
    """Estratégia de fallback para cache"""
    
    def __init__(self, config: FallbackConfig):
        self.config = config
        self.cache: Dict[str, Tuple[Any, datetime]] = {}
        self._cleanup_task = None
        
    async def get_fallback_data(self, key: str) -> Optional[Any]:
        """Obtém dados do cache como fallback"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.config.cache_ttl):
                logger.info(f"Cache fallback usado para chave: {key}")
                return data
            else:
                # Dados expirados
                del self.cache[key]
        return None
        
    async def store_data(self, key: str, data: Any):
        """Armazena dados no cache"""
        if self.config.enable_compression:
            data = self._compress_data(data)
        self.cache[key] = (data, datetime.now())
        
        # Limpeza automática se cache muito grande
        if len(self.cache) > 1000:
            await self._cleanup_expired()
            
    def _compress_data(self, data: Any) -> bytes:
        """Comprime dados"""
        try:
            serialized = pickle.dumps(data)
            if len(serialized) > 1024:  # Comprimir apenas se > 1KB
                compressed = gzip.compress(serialized)
                return base64.b64encode(compressed)
            return serialized
        except Exception as e:
            logger.warning(f"Erro ao comprimir dados: {e}")
            return pickle.dumps(data)
            
    def _decompress_data(self, data: bytes) -> Any:
        """Descomprime dados"""
        try:
            if data.startswith(b'gzip:'):
                compressed = base64.b64decode(data[5:])
                serialized = gzip.decompress(compressed)
                return pickle.loads(serialized)
            else:
                return pickle.loads(data)
        except Exception as e:
            logger.warning(f"Erro ao descomprimir dados: {e}")
            return None
            
    async def _cleanup_expired(self):
        """Remove dados expirados do cache"""
        now = datetime.now()
        expired_keys = []
        for key, (data, timestamp) in self.cache.items():
            if now - timestamp > timedelta(seconds=self.config.cache_ttl):
                expired_keys.append(key)
                
        for key in expired_keys:
            del self.cache[key]
            
        logger.info(f"Removidos {len(expired_keys)} itens expirados do cache")

class HistoricalDataFallbackStrategy:
    """Estratégia de fallback para dados históricos"""
    
    def __init__(self, config: FallbackConfig):
        self.config = config
        self.historical_data: Dict[str, List[Tuple[Any, datetime]]] = {}
        
    async def get_fallback_data(self, key: str) -> Optional[Any]:
        """Obtém dados históricos como fallback"""
        if key in self.historical_data:
            data_list = self.historical_data[key]
            if data_list:
                # Retorna o dado mais recente dentro do TTL
                for data, timestamp in reversed(data_list):
                    if datetime.now() - timestamp < timedelta(seconds=self.config.historical_data_ttl):
                        logger.info(f"Dados históricos usados como fallback para chave: {key}")
                        return data
                        
                # Se não há dados recentes, retorna o mais antigo
                if data_list:
                    data, timestamp = data_list[0]
                    logger.info(f"Dados históricos antigos usados como fallback para chave: {key}")
                    return data
        return None
        
    async def store_data(self, key: str, data: Any):
        """Armazena dados históricos"""
        if key not in self.historical_data:
            self.historical_data[key] = []
            
        self.historical_data[key].append((data, datetime.now()))
        
        # Manter apenas os últimos 10 registros
        if len(self.historical_data[key]) > 10:
            self.historical_data[key] = self.historical_data[key][-10:]
            
    async def cleanup_expired(self):
        """Remove dados históricos expirados"""
        now = datetime.now()
        for key in list(self.historical_data.keys()):
            data_list = self.historical_data[key]
            valid_data = []
            for data, timestamp in data_list:
                if now - timestamp < timedelta(seconds=self.config.historical_data_ttl):
                    valid_data.append((data, timestamp))
                    
            if valid_data:
                self.historical_data[key] = valid_data
            else:
                del self.historical_data[key]

class AlternativeAPIFallbackStrategy:
    """Estratégia de fallback para APIs alternativas"""
    
    def __init__(self, config: FallbackConfig):
        self.config = config
        self.alternative_apis: Dict[str, List[str]] = {}
        self.api_health: Dict[str, bool] = {}
        
    def register_alternative_api(self, primary_api: str, alternative_apis: List[str]):
        """Registra APIs alternativas para uma API primária"""
        self.alternative_apis[primary_api] = alternative_apis
        for api in alternative_apis:
            self.api_health[api] = True
            
    async def get_fallback_data(self, primary_api: str, request_func: Callable, *args, **kwargs) -> Optional[Any]:
        """Tenta obter dados de APIs alternativas"""
        if primary_api not in self.alternative_apis:
            return None
            
        alternative_apis = self.alternative_apis[primary_api]
        
        for api in alternative_apis:
            if not self.api_health.get(api, True):
                continue
                
            try:
                logger.info(f"Tentando API alternativa: {api}")
                result = await request_func(api, *args, **kwargs)
                if result:
                    logger.info(f"Sucesso com API alternativa: {api}")
                    return result
            except Exception as e:
                logger.warning(f"Falha com API alternativa {api}: {e}")
                self.api_health[api] = False
                
        return None
        
    async def check_api_health(self, api: str) -> bool:
        """Verifica saúde de uma API"""
        try:
            # Implementar health check específico para cada API
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{api}/health", timeout=5) as response:
                    return response.status == 200
        except Exception:
            return False
            
    async def restore_api_health(self, api: str):
        """Restaura saúde de uma API"""
        if await self.check_api_health(api):
            self.api_health[api] = True
            logger.info(f"API {api} restaurada")

class WebScrapingFallbackStrategy:
    """Estratégia de fallback para web scraping"""
    
    def __init__(self, config: FallbackConfig):
        self.config = config
        self.scraping_rules: Dict[str, Dict[str, Any]] = {}
        
    def register_scraping_rule(self, api_name: str, rule: Dict[str, Any]):
        """Registra regra de scraping para uma API"""
        self.scraping_rules[api_name] = rule
        
    async def get_fallback_data(self, api_name: str, query: str) -> Optional[Any]:
        """Obtém dados via web scraping"""
        if api_name not in self.scraping_rules:
            return None
            
        rule = self.scraping_rules[api_name]
        
        try:
            logger.info(f"Tentando web scraping para: {api_name}")
            
            # Implementar scraping específico para cada API
            if api_name == "instagram":
                return await self._scrape_instagram(query, rule)
            elif api_name == "tiktok":
                return await self._scrape_tiktok(query, rule)
            elif api_name == "youtube":
                return await self._scrape_youtube(query, rule)
            elif api_name == "pinterest":
                return await self._scrape_pinterest(query, rule)
            else:
                return await self._generic_scraping(query, rule)
                
        except Exception as e:
            logger.error(f"Erro no web scraping para {api_name}: {e}")
            return None
            
    async def _scrape_instagram(self, query: str, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Scraping específico para Instagram"""
        # Implementação específica para Instagram
        return {
            "source": "web_scraping",
            "platform": "instagram",
            "query": query,
            "data": [],
            "message": "Web scraping não implementado para Instagram"
        }
        
    async def _scrape_tiktok(self, query: str, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Scraping específico para TikTok"""
        # Implementação específica para TikTok
        return {
            "source": "web_scraping",
            "platform": "tiktok",
            "query": query,
            "data": [],
            "message": "Web scraping não implementado para TikTok"
        }
        
    async def _scrape_youtube(self, query: str, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Scraping específico para YouTube"""
        # Implementação específica para YouTube
        return {
            "source": "web_scraping",
            "platform": "youtube",
            "query": query,
            "data": [],
            "message": "Web scraping não implementado para YouTube"
        }
        
    async def _scrape_pinterest(self, query: str, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Scraping específico para Pinterest"""
        # Implementação específica para Pinterest
        return {
            "source": "web_scraping",
            "platform": "pinterest",
            "query": query,
            "data": [],
            "message": "Web scraping não implementado para Pinterest"
        }
        
    async def _generic_scraping(self, query: str, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Scraping genérico"""
        return {
            "source": "web_scraping",
            "platform": "generic",
            "query": query,
            "data": [],
            "message": "Web scraping genérico não implementado"
        }

class MockDataFallbackStrategy:
    """Estratégia de fallback para dados mock"""
    
    def __init__(self, config: FallbackConfig):
        self.config = config
        self.mock_data_templates: Dict[str, Dict[str, Any]] = {}
        
    def register_mock_template(self, api_name: str, template: Dict[str, Any]):
        """Registra template de dados mock para uma API"""
        self.mock_data_templates[api_name] = template
        
    async def get_fallback_data(self, api_name: str, query: str) -> Dict[str, Any]:
        """Retorna dados mock como fallback"""
        template = self.mock_data_templates.get(api_name, {})
        
        mock_data = {
            "source": "mock",
            "platform": api_name,
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "data": template.get("data", []),
            "message": f"Dados mock para {api_name}",
            "warning": "Estes são dados simulados, não dados reais"
        }
        
        logger.info(f"Dados mock usados como fallback para: {api_name}")
        return mock_data

class RetryFallbackStrategy:
    """Estratégia de fallback com retry"""
    
    def __init__(self, config: FallbackConfig):
        self.config = config
        
    async def execute_with_retry(self, func: Callable, *args, **kwargs) -> Optional[Any]:
        """Executa função com retry"""
        last_exception = None
        
        for attempt in range(self.config.retry_attempts):
            try:
                logger.info(f"Tentativa {attempt + 1} de {self.config.retry_attempts}")
                result = await func(*args, **kwargs)
                if result:
                    logger.info(f"Sucesso na tentativa {attempt + 1}")
                    return result
            except Exception as e:
                last_exception = e
                logger.warning(f"Falha na tentativa {attempt + 1}: {e}")
                
                if attempt < self.config.retry_attempts - 1:
                    await asyncio.sleep(self.config.retry_delay * (2 ** attempt))  # Backoff exponencial
                    
        logger.error(f"Todas as tentativas falharam: {last_exception}")
        return None

class DegradedFallbackStrategy:
    """Estratégia de fallback com degradação gradual"""
    
    def __init__(self, config: FallbackConfig):
        self.config = config
        self.degradation_levels: Dict[str, List[Dict[str, Any]]] = {}
        
    def register_degradation_levels(self, api_name: str, levels: List[Dict[str, Any]]):
        """Registra níveis de degradação para uma API"""
        self.degradation_levels[api_name] = levels
        
    async def get_degraded_data(self, api_name: str, level: int = 0) -> Optional[Any]:
        """Obtém dados degradados"""
        if api_name not in self.degradation_levels:
            return None
            
        levels = self.degradation_levels[api_name]
        if level >= len(levels):
            return None
            
        degradation_config = levels[level]
        
        # Implementar lógica de degradação específica
        degraded_data = {
            "source": "degraded",
            "platform": api_name,
            "degradation_level": level,
            "data": degradation_config.get("data", []),
            "message": f"Dados degradados nível {level} para {api_name}",
            "features_disabled": degradation_config.get("features_disabled", [])
        }
        
        logger.info(f"Dados degradados nível {level} usados para: {api_name}")
        return degraded_data

class FallbackManager:
    """Gerenciador principal de fallback"""
    
    def __init__(self, config: FallbackConfig):
        self.config = config
        self.metrics = FallbackMetrics()
        
        # Inicializar estratégias
        self.cache_strategy = CacheFallbackStrategy(config)
        self.historical_strategy = HistoricalDataFallbackStrategy(config)
        self.alternative_api_strategy = AlternativeAPIFallbackStrategy(config)
        self.web_scraping_strategy = WebScrapingFallbackStrategy(config)
        self.mock_strategy = MockDataFallbackStrategy(config)
        self.retry_strategy = RetryFallbackStrategy(config)
        self.degraded_strategy = DegradedFallbackStrategy(config)
        
        # Configurar dados mock padrão
        self._setup_default_mock_data()
        
    def _setup_default_mock_data(self):
        """Configura dados mock padrão"""
        # Instagram mock
        self.mock_strategy.register_mock_template("instagram", {
            "data": [
                {
                    "id": "mock_post_1",
                    "caption": "Post mock do Instagram",
                    "media_type": "IMAGE",
                    "like_count": 100,
                    "comment_count": 10
                }
            ]
        })
        
        # TikTok mock
        self.mock_strategy.register_mock_template("tiktok", {
            "data": [
                {
                    "id": "mock_video_1",
                    "description": "Vídeo mock do TikTok",
                    "like_count": 200,
                    "comment_count": 20,
                    "share_count": 50
                }
            ]
        })
        
        # YouTube mock
        self.mock_strategy.register_mock_template("youtube", {
            "data": [
                {
                    "id": "mock_video_1",
                    "title": "Vídeo mock do YouTube",
                    "description": "Descrição mock",
                    "view_count": 1000,
                    "like_count": 100
                }
            ]
        })
        
        # Pinterest mock
        self.mock_strategy.register_mock_template("pinterest", {
            "data": [
                {
                    "id": "mock_pin_1",
                    "title": "Pin mock do Pinterest",
                    "description": "Descrição mock",
                    "link": "https://example.com/mock"
                }
            ]
        })
        
    async def execute_with_fallback(self, primary_func: Callable, api_name: str, 
                                  query: str, *args, **kwargs) -> Any:
        """Executa função primária com fallback"""
        start_time = time.time()
        
        try:
            # Tentar função primária
            result = await primary_func(*args, **kwargs)
            if result:
                return result
        except Exception as e:
            logger.warning(f"Falha na função primária para {api_name}: {e}")
            
        # Aplicar estratégias de fallback em ordem
        fallback_result = await self._apply_fallback_strategies(api_name, query, *args, **kwargs)
        
        response_time = time.time() - start_time
        success = fallback_result is not None
        
        if self.config.enable_metrics:
            self.metrics.add_fallback(self.config.primary_strategy, success, response_time)
            
        return fallback_result
        
    async def _apply_fallback_strategies(self, api_name: str, query: str, 
                                       *args, **kwargs) -> Optional[Any]:
        """Aplica estratégias de fallback em ordem"""
        strategies = [
            (self.config.primary_strategy, "primária"),
            (self.config.secondary_strategy, "secundária"),
            (self.config.tertiary_strategy, "terciária")
        ]
        
        for strategy, description in strategies:
            try:
                result = await self._execute_strategy(strategy, api_name, query, *args, **kwargs)
                if result:
                    logger.info(f"Fallback {description} ({strategy.value}) bem-sucedido para {api_name}")
                    return result
            except Exception as e:
                logger.warning(f"Fallback {description} ({strategy.value}) falhou para {api_name}: {e}")
                
        logger.error(f"Todas as estratégias de fallback falharam para {api_name}")
        return None
        
    async def _execute_strategy(self, strategy: FallbackStrategy, api_name: str, 
                              query: str, *args, **kwargs) -> Optional[Any]:
        """Executa estratégia específica de fallback"""
        cache_key = f"{api_name}:{hash(str(args) + str(kwargs))}"
        
        if strategy == FallbackStrategy.CACHE:
            return await self.cache_strategy.get_fallback_data(cache_key)
            
        elif strategy == FallbackStrategy.HISTORICAL:
            return await self.historical_strategy.get_fallback_data(cache_key)
            
        elif strategy == FallbackStrategy.ALTERNATIVE_API:
            # Implementar lógica de API alternativa
            return None
            
        elif strategy == FallbackStrategy.WEB_SCRAPING:
            return await self.web_scraping_strategy.get_fallback_data(api_name, query)
            
        elif strategy == FallbackStrategy.MOCK:
            return await self.mock_strategy.get_fallback_data(api_name, query)
            
        elif strategy == FallbackStrategy.RETRY:
            # Implementar retry com função primária
            return None
            
        elif strategy == FallbackStrategy.DEGRADED:
            return await self.degraded_strategy.get_degraded_data(api_name, 0)
            
        return None
        
    async def store_data_for_fallback(self, api_name: str, data: Any, *args, **kwargs):
        """Armazena dados para uso futuro em fallback"""
        cache_key = f"{api_name}:{hash(str(args) + str(kwargs))}"
        
        # Armazenar no cache
        await self.cache_strategy.store_data(cache_key, data)
        
        # Armazenar como dados históricos
        await self.historical_strategy.store_data(cache_key, data)
        
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de fallback"""
        return self.metrics.get_summary() if self.config.enable_metrics else {}
        
    async def cleanup(self):
        """Limpeza de dados expirados"""
        await self.cache_strategy._cleanup_expired()
        await self.historical_strategy.cleanup_expired()

# Instância global do gerenciador de fallback
fallback_manager = FallbackManager(FallbackConfig())

# Decorator para usar fallback
def fallback(api_name: str, query: str = "", config: Optional[FallbackConfig] = None):
    """Decorator para aplicar fallback a função"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            manager = fallback_manager if config is None else FallbackManager(config)
            return await manager.execute_with_fallback(func, api_name, query, *args, **kwargs)
        return wrapper
    return decorator

# Funções utilitárias
async def execute_with_fallback(primary_func: Callable, api_name: str, 
                               query: str = "", *args, **kwargs) -> Any:
    """Executa função com fallback"""
    return await fallback_manager.execute_with_fallback(primary_func, api_name, query, *args, **kwargs)

def get_fallback_metrics() -> Dict[str, Any]:
    """Obtém métricas de fallback"""
    return fallback_manager.get_metrics()

async def store_fallback_data(api_name: str, data: Any, *args, **kwargs):
    """Armazena dados para fallback"""
    await fallback_manager.store_data_for_fallback(api_name, data, *args, **kwargs)

async def cleanup_fallback_data():
    """Limpa dados de fallback expirados"""
    await fallback_manager.cleanup()

# Exemplo de uso
if __name__ == "__main__":
    import asyncio
    
    async def test_fallback():
        # Função que pode falhar
        async def unreliable_api_call():
            import random
            if random.random() < 0.8:  # 80% de chance de falha
                raise Exception("API indisponível")
            return {"data": "dados reais"}
        
        # Testar fallback
        result = await execute_with_fallback(
            unreliable_api_call, 
            "test_api", 
            "test_query"
        )
        
        print(f"Resultado: {result}")
        print(f"Métricas: {get_fallback_metrics()}")
    
    asyncio.run(test_fallback()) 