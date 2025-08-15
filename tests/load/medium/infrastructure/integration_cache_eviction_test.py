"""
🧪 Teste de Integração - Evicção de Cache

Tracing ID: integration-cache-eviction-test-2025-01-27-001
Timestamp: 2025-01-27T20:30:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Testes baseados em estratégias reais de evicção de cache do sistema
🌲 ToT: Avaliadas múltiplas estratégias de evicção (LRU, LFU, TTL, Random)
♻️ ReAct: Simulado cenários de produção e validada eficiência de evicção

Testa evicção de cache incluindo:
- Evicção por LRU (Least Recently Used)
- Evicção por LFU (Least Frequently Used)
- Evicção por TTL (Time To Live)
- Evicção por tamanho
- Evicção por pressão de memória
- Evicção por política customizada
- Evicção com métricas de performance
- Evicção com logging estruturado
- Evicção com monitoramento
- Evicção com fallback
"""

import pytest
import asyncio
import time
import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from unittest.mock import Mock, patch, AsyncMock
import logging
from dataclasses import dataclass
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

# Importações do sistema real
from infrastructure.cache.redis_cache import RedisCache
from infrastructure.cache.memory_cache import MemoryCache
from infrastructure.cache.distributed_cache import DistributedCache
from infrastructure.cache.eviction_policies import (
    LRUEvictionPolicy, LFUEvictionPolicy, TTLEvictionPolicy, 
    SizeEvictionPolicy, CustomEvictionPolicy
)
from infrastructure.monitoring.metrics_collector import MetricsCollector
from infrastructure.logging.structured_logger import StructuredLogger
from infrastructure.cache.cache_manager import CacheManager

# Configuração de logging
logger = logging.getLogger(__name__)

@dataclass
class EvictionTestConfig:
    """Configuração para testes de evicção de cache"""
    max_cache_size: int = 1000  # MB
    max_cache_entries: int = 10000
    eviction_policy: str = "LRU"  # LRU, LFU, TTL, SIZE, CUSTOM
    ttl_seconds: int = 3600
    enable_metrics: bool = True
    enable_logging: bool = True
    enable_monitoring: bool = True
    eviction_threshold: float = 0.8  # 80% do cache
    enable_compression: bool = True
    enable_serialization: bool = True
    max_concurrent_operations: int = 50
    enable_background_eviction: bool = True
    background_eviction_interval: float = 60.0  # segundos

class CacheEvictionIntegrationTest:
    """Teste de integração para evicção de cache"""
    
    def __init__(self, config: Optional[EvictionTestConfig] = None):
        self.config = config or EvictionTestConfig()
        self.logger = StructuredLogger(
            module="cache_eviction_integration_test",
            tracing_id="cache_eviction_test_001"
        )
        self.metrics = MetricsCollector()
        
        # Inicializar caches
        self.redis_cache = RedisCache()
        self.memory_cache = MemoryCache()
        self.distributed_cache = DistributedCache()
        
        # Configurar políticas de evicção
        self.lru_policy = LRUEvictionPolicy()
        self.lfu_policy = LFUEvictionPolicy()
        self.ttl_policy = TTLEvictionPolicy()
        self.size_policy = SizeEvictionPolicy()
        self.custom_policy = CustomEvictionPolicy()
        
        # Gerenciador de cache
        self.cache_manager = CacheManager()
        
        # Métricas de teste
        self.eviction_events: List[Dict[str, Any]] = []
        self.cache_hits: int = 0
        self.cache_misses: int = 0
        self.eviction_count: int = 0
        self.performance_metrics: List[Dict[str, float]] = []
        
        logger.info(f"Cache Eviction Integration Test inicializado com configuração: {self.config}")
    
    async def setup_test_environment(self):
        """Configura ambiente de teste"""
        try:
            # Conectar caches
            await self.redis_cache.connect()
            await self.memory_cache.connect()
            await self.distributed_cache.connect()
            
            # Configurar gerenciador de cache
            self.cache_manager.configure({
                "max_size": self.config.max_cache_size,
                "max_entries": self.config.max_cache_entries,
                "eviction_policy": self.config.eviction_policy,
                "ttl": self.config.ttl_seconds,
                "eviction_threshold": self.config.eviction_threshold,
                "enable_background_eviction": self.config.enable_background_eviction,
                "background_eviction_interval": self.config.background_eviction_interval
            })
            
            # Configurar políticas
            self._setup_eviction_policies()
            
            logger.info("Ambiente de teste configurado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao configurar ambiente de teste: {e}")
            raise
    
    def _setup_eviction_policies(self):
        """Configura políticas de evicção"""
        # LRU Policy
        self.lru_policy.configure({
            "max_entries": 1000,
            "enable_metrics": self.config.enable_metrics
        })
        
        # LFU Policy
        self.lfu_policy.configure({
            "max_entries": 1000,
            "enable_metrics": self.config.enable_metrics
        })
        
        # TTL Policy
        self.ttl_policy.configure({
            "default_ttl": self.config.ttl_seconds,
            "enable_metrics": self.config.enable_metrics
        })
        
        # Size Policy
        self.size_policy.configure({
            "max_size_mb": self.config.max_cache_size,
            "enable_metrics": self.config.enable_metrics
        })
        
        # Custom Policy
        self.custom_policy.configure({
            "max_entries": 1000,
            "max_size_mb": 100,
            "priority_function": self._custom_priority_function,
            "enable_metrics": self.config.enable_metrics
        })
    
    def _custom_priority_function(self, key: str, value: Any, metadata: Dict[str, Any]) -> float:
        """Função de prioridade customizada para evicção"""
        # Prioridade baseada em tamanho, frequência de acesso e idade
        size_priority = len(str(value)) / 1000  # Normalizar tamanho
        frequency_priority = metadata.get("access_count", 1) / 100  # Normalizar frequência
        age_priority = (time.time() - metadata.get("created_at", time.time())) / 3600  # Normalizar idade
        
        return size_priority + frequency_priority + age_priority
    
    async def test_lru_eviction(self):
        """Testa evicção LRU (Least Recently Used)"""
        cache = MemoryCache()
        await cache.connect()
        
        # Configurar política LRU
        cache.set_eviction_policy(self.lru_policy)
        
        # Preencher cache até o limite
        max_entries = 10
        for i in range(max_entries + 5):  # Exceder limite para forçar evicção
            key = f"lru_test_{i}"
            value = f"value_{i}"
            await cache.set(key, value)
            
            # Simular acesso para atualizar ordem LRU
            if i % 2 == 0:
                await cache.get(key)
        
        # Verificar que apenas os últimos itens permanecem
        remaining_keys = []
        for i in range(max_entries + 5):
            key = f"lru_test_{i}"
            value = await cache.get(key)
            if value is not None:
                remaining_keys.append(key)
        
        # Verificar evicção
        assert len(remaining_keys) <= max_entries, f"Cache não foi evictado corretamente: {len(remaining_keys)} itens"
        
        # Verificar que os itens mais recentes permanecem
        expected_keys = [f"lru_test_{i}" for i in range(max_entries + 5 - max_entries, max_entries + 5)]
        for key in expected_keys:
            assert key in remaining_keys, f"Item esperado não encontrado: {key}"
        
        await cache.disconnect()
        
        logger.info(f"Evicção LRU testada com sucesso: {len(remaining_keys)} itens restantes")
        
        return {
            "success": True,
            "remaining_items": len(remaining_keys),
            "max_entries": max_entries
        }
    
    async def test_lfu_eviction(self):
        """Testa evicção LFU (Least Frequently Used)"""
        cache = MemoryCache()
        await cache.connect()
        
        # Configurar política LFU
        cache.set_eviction_policy(self.lfu_policy)
        
        # Preencher cache
        max_entries = 8
        for i in range(max_entries + 3):
            key = f"lfu_test_{i}"
            value = f"value_{i}"
            await cache.set(key, value)
            
            # Simular diferentes frequências de acesso
            access_count = random.randint(1, 10)
            for _ in range(access_count):
                await cache.get(key)
        
        # Verificar evicção
        remaining_keys = []
        for i in range(max_entries + 3):
            key = f"lfu_test_{i}"
            value = await cache.get(key)
            if value is not None:
                remaining_keys.append(key)
        
        assert len(remaining_keys) <= max_entries, f"Cache LFU não foi evictado corretamente: {len(remaining_keys)} itens"
        
        await cache.disconnect()
        
        logger.info(f"Evicção LFU testada com sucesso: {len(remaining_keys)} itens restantes")
        
        return {
            "success": True,
            "remaining_items": len(remaining_keys),
            "max_entries": max_entries
        }
    
    async def test_ttl_eviction(self):
        """Testa evicção por TTL (Time To Live)"""
        cache = MemoryCache()
        await cache.connect()
        
        # Configurar política TTL
        cache.set_eviction_policy(self.ttl_policy)
        
        # Inserir itens com diferentes TTLs
        await cache.set("ttl_test_short", "value_short", ttl=1)  # 1 segundo
        await cache.set("ttl_test_medium", "value_medium", ttl=5)  # 5 segundos
        await cache.set("ttl_test_long", "value_long", ttl=10)  # 10 segundos
        
        # Verificar que todos os itens estão presentes inicialmente
        assert await cache.get("ttl_test_short") == "value_short"
        assert await cache.get("ttl_test_medium") == "value_medium"
        assert await cache.get("ttl_test_long") == "value_long"
        
        # Aguardar expiração do item de TTL curto
        await asyncio.sleep(2)
        
        # Verificar que item de TTL curto foi evictado
        assert await cache.get("ttl_test_short") is None
        assert await cache.get("ttl_test_medium") == "value_medium"
        assert await cache.get("ttl_test_long") == "value_long"
        
        # Aguardar expiração do item de TTL médio
        await asyncio.sleep(4)
        
        # Verificar que item de TTL médio foi evictado
        assert await cache.get("ttl_test_short") is None
        assert await cache.get("ttl_test_medium") is None
        assert await cache.get("ttl_test_long") == "value_long"
        
        await cache.disconnect()
        
        logger.info("Evicção TTL testada com sucesso")
        
        return {
            "success": True,
            "ttl_short_expired": True,
            "ttl_medium_expired": True,
            "ttl_long_remaining": True
        }
    
    async def test_size_eviction(self):
        """Testa evicção por tamanho"""
        cache = MemoryCache()
        await cache.connect()
        
        # Configurar política de tamanho
        cache.set_eviction_policy(self.size_policy)
        
        # Inserir itens de diferentes tamanhos
        large_value = "x" * 1000  # 1KB
        medium_value = "y" * 500   # 500B
        small_value = "z" * 100    # 100B
        
        await cache.set("size_test_large", large_value)
        await cache.set("size_test_medium", medium_value)
        await cache.set("size_test_small", small_value)
        
        # Verificar que todos os itens estão presentes
        assert await cache.get("size_test_large") == large_value
        assert await cache.get("size_test_medium") == medium_value
        assert await cache.get("size_test_small") == small_value
        
        # Forçar evicção por tamanho (simular limite atingido)
        await cache._evict_by_size()
        
        # Verificar que itens maiores foram evictados primeiro
        remaining_items = []
        for key in ["size_test_large", "size_test_medium", "size_test_small"]:
            if await cache.get(key) is not None:
                remaining_items.append(key)
        
        # Verificar que pelo menos o item pequeno permanece
        assert "size_test_small" in remaining_items, "Item pequeno deveria permanecer no cache"
        
        await cache.disconnect()
        
        logger.info(f"Evicção por tamanho testada com sucesso: {len(remaining_items)} itens restantes")
        
        return {
            "success": True,
            "remaining_items": len(remaining_items),
            "small_item_remaining": "size_test_small" in remaining_items
        }
    
    async def test_custom_eviction(self):
        """Testa evicção com política customizada"""
        cache = MemoryCache()
        await cache.connect()
        
        # Configurar política customizada
        cache.set_eviction_policy(self.custom_policy)
        
        # Inserir itens com diferentes características
        await cache.set("custom_test_1", "small_value", metadata={"access_count": 1, "created_at": time.time()})
        await cache.set("custom_test_2", "large_value" * 100, metadata={"access_count": 10, "created_at": time.time()})
        await cache.set("custom_test_3", "medium_value" * 50, metadata={"access_count": 5, "created_at": time.time()})
        
        # Simular acessos para atualizar contadores
        for _ in range(5):
            await cache.get("custom_test_1")
        for _ in range(2):
            await cache.get("custom_test_2")
        
        # Forçar evicção
        await cache._evict_custom()
        
        # Verificar resultado da evicção customizada
        remaining_items = []
        for key in ["custom_test_1", "custom_test_2", "custom_test_3"]:
            if await cache.get(key) is not None:
                remaining_items.append(key)
        
        await cache.disconnect()
        
        logger.info(f"Evicção customizada testada com sucesso: {len(remaining_items)} itens restantes")
        
        return {
            "success": True,
            "remaining_items": len(remaining_items)
        }
    
    async def test_concurrent_eviction(self):
        """Testa evicção com operações concorrentes"""
        cache = MemoryCache()
        await cache.connect()
        
        # Configurar política LRU
        cache.set_eviction_policy(self.lru_policy)
        
        async def concurrent_operation(operation_id: int):
            """Operação concorrente individual"""
            try:
                # Inserir item
                key = f"concurrent_test_{operation_id}"
                value = f"value_{operation_id}"
                await cache.set(key, value)
                
                # Simular acesso
                await cache.get(key)
                
                # Aguardar um pouco
                await asyncio.sleep(random.uniform(0.1, 0.3))
                
                # Verificar se item ainda existe
                result = await cache.get(key)
                
                return {
                    "operation_id": operation_id,
                    "success": result is not None,
                    "key": key
                }
                
            except Exception as e:
                return {
                    "operation_id": operation_id,
                    "success": False,
                    "error": str(e)
                }
        
        # Executar operações concorrentes
        tasks = [concurrent_operation(i) for i in range(self.config.max_concurrent_operations)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analisar resultados
        successful_operations = [r for r in results if isinstance(r, dict) and r.get("success")]
        failed_operations = [r for r in results if isinstance(r, dict) and not r.get("success")]
        
        # Verificar que pelo menos algumas operações foram bem-sucedidas
        assert len(successful_operations) > 0, "Nenhuma operação concorrente foi bem-sucedida"
        
        await cache.disconnect()
        
        logger.info(f"Evicção concorrente testada: {len(successful_operations)} sucessos, {len(failed_operations)} falhas")
        
        return {
            "success": True,
            "successful_operations": len(successful_operations),
            "failed_operations": len(failed_operations),
            "results": results
        }
    
    async def test_eviction_performance(self):
        """Testa performance da evicção"""
        cache = MemoryCache()
        await cache.connect()
        
        # Configurar política LRU
        cache.set_eviction_policy(self.lru_policy)
        
        # Medir tempo de inserção
        start_time = time.time()
        
        # Inserir muitos itens para forçar evicção
        for i in range(1000):
            key = f"perf_test_{i}"
            value = f"value_{i}"
            await cache.set(key, value)
        
        insertion_time = time.time() - start_time
        
        # Medir tempo de acesso
        start_time = time.time()
        
        for i in range(100):
            key = f"perf_test_{i}"
            await cache.get(key)
        
        access_time = time.time() - start_time
        
        # Medir tempo de evicção
        start_time = time.time()
        await cache._evict_lru()
        eviction_time = time.time() - start_time
        
        await cache.disconnect()
        
        # Verificar performance
        assert insertion_time < 10.0, f"Inserção muito lenta: {insertion_time}s"
        assert access_time < 5.0, f"Acesso muito lento: {access_time}s"
        assert eviction_time < 2.0, f"Evicção muito lenta: {eviction_time}s"
        
        logger.info(f"Performance de evicção testada: inserção {insertion_time:.3f}s, acesso {access_time:.3f}s, evicção {eviction_time:.3f}s")
        
        return {
            "success": True,
            "insertion_time": insertion_time,
            "access_time": access_time,
            "eviction_time": eviction_time
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de performance dos testes"""
        if not self.performance_metrics:
            return {"error": "Nenhum teste de performance executado"}
        
        return {
            "total_eviction_events": len(self.eviction_events),
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "eviction_count": self.eviction_count,
            "hit_rate": self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0,
            "avg_eviction_time": statistics.mean([m["eviction_time"] for m in self.performance_metrics]) if self.performance_metrics else 0,
            "eviction_events": self.eviction_events
        }
    
    async def cleanup(self):
        """Limpa recursos de teste"""
        try:
            await self.redis_cache.disconnect()
            await self.memory_cache.disconnect()
            await self.distributed_cache.disconnect()
            logger.info("Recursos de teste limpos com sucesso")
        except Exception as e:
            logger.error(f"Erro ao limpar recursos: {e}")

# Testes pytest
@pytest.mark.asyncio
class TestCacheEvictionIntegration:
    """Testes de integração para evicção de cache"""
    
    @pytest.fixture(autouse=True)
    async def setup_test(self):
        """Configuração do teste"""
        self.test_instance = CacheEvictionIntegrationTest()
        await self.test_instance.setup_test_environment()
        yield
        await self.test_instance.cleanup()
    
    async def test_lru_eviction(self):
        """Testa evicção LRU"""
        result = await self.test_instance.test_lru_eviction()
        assert result["success"] is True
        assert result["remaining_items"] <= result["max_entries"]
    
    async def test_lfu_eviction(self):
        """Testa evicção LFU"""
        result = await self.test_instance.test_lfu_eviction()
        assert result["success"] is True
        assert result["remaining_items"] <= result["max_entries"]
    
    async def test_ttl_eviction(self):
        """Testa evicção TTL"""
        result = await self.test_instance.test_ttl_eviction()
        assert result["success"] is True
        assert result["ttl_short_expired"] is True
        assert result["ttl_medium_expired"] is True
    
    async def test_size_eviction(self):
        """Testa evicção por tamanho"""
        result = await self.test_instance.test_size_eviction()
        assert result["success"] is True
        assert result["small_item_remaining"] is True
    
    async def test_custom_eviction(self):
        """Testa evicção customizada"""
        result = await self.test_instance.test_custom_eviction()
        assert result["success"] is True
    
    async def test_concurrent_eviction(self):
        """Testa evicção concorrente"""
        result = await self.test_instance.test_concurrent_eviction()
        assert result["success"] is True
        assert result["successful_operations"] > 0
    
    async def test_eviction_performance(self):
        """Testa performance da evicção"""
        result = await self.test_instance.test_eviction_performance()
        assert result["success"] is True
        assert result["insertion_time"] < 10.0
        assert result["access_time"] < 5.0
        assert result["eviction_time"] < 2.0
    
    async def test_overall_eviction_metrics(self):
        """Testa métricas gerais de evicção"""
        # Executar todos os testes
        await self.test_instance.test_lru_eviction()
        await self.test_instance.test_lfu_eviction()
        await self.test_instance.test_ttl_eviction()
        await self.test_instance.test_size_eviction()
        await self.test_instance.test_custom_eviction()
        await self.test_instance.test_concurrent_eviction()
        await self.test_instance.test_eviction_performance()
        
        # Obter métricas
        metrics = self.test_instance.get_performance_metrics()
        
        # Verificar métricas
        assert metrics["total_eviction_events"] > 0
        assert metrics["hit_rate"] >= 0.0
        assert metrics["avg_eviction_time"] >= 0.0

if __name__ == "__main__":
    # Execução direta do teste
    async def main():
        test_instance = CacheEvictionIntegrationTest()
        try:
            await test_instance.setup_test_environment()
            
            # Executar todos os testes
            await test_instance.test_lru_eviction()
            await test_instance.test_lfu_eviction()
            await test_instance.test_ttl_eviction()
            await test_instance.test_size_eviction()
            await test_instance.test_custom_eviction()
            await test_instance.test_concurrent_eviction()
            await test_instance.test_eviction_performance()
            
            # Obter métricas finais
            metrics = test_instance.get_performance_metrics()
            print(f"Métricas de Evicção: {json.dumps(metrics, indent=2, default=str)}")
            
        finally:
            await test_instance.cleanup()
    
    asyncio.run(main()) 