from typing import Dict, List, Optional, Any
#!/usr/bin/env python3
"""
🧪 Testes Unitários - IMP-012: Sistema de Cache Inteligente
🎯 Objetivo: Validar cache inteligente com hit rate > 90%
📅 Criado: 2024-12-27
🔄 Versão: 1.0
"""

import unittest
import time
import threading
import json
import pickle
import gzip
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Adicionar path para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from infrastructure.cache.intelligent_cache_imp012 import (
    IntelligentCacheSystem,
    CacheItem,
    CacheMetrics,
    AdaptiveTTLManager,
    L1Cache,
    L2Cache,
    CacheLevel,
    EvictionPolicy,
    cache_decorator
)


class TestCacheItem(unittest.TestCase):
    """Testes para CacheItem."""
    
    def setUp(self):
        """Configuração inicial."""
        self.item = CacheItem(
            key="test_key",
            value="test_value",
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            ttl=60
        )
    
    def test_is_expired_false(self):
        """Testa se item não expirou."""
        self.assertFalse(self.item.is_expired())
    
    def test_is_expired_true(self):
        """Testa se item expirou."""
        self.item.created_at = datetime.now() - timedelta(seconds=120)
        self.assertTrue(self.item.is_expired())
    
    def test_update_access(self):
        """Testa atualização de acesso."""
        old_access = self.item.last_accessed
        old_count = self.item.access_count
        
        time.sleep(0.1)  # Pequena pausa para garantir diferença
        self.item.update_access()
        
        self.assertGreater(self.item.last_accessed, old_access)
        self.assertEqual(self.item.access_count, old_count + 1)
    
    def test_calculate_size(self):
        """Testa cálculo de tamanho."""
        size = self.item.calculate_size()
        self.assertGreater(size, 0)
        self.assertEqual(self.item.size, size)
    
    def test_compress_decompress(self):
        """Testa compressão e descompressão."""
        # Criar dados grandes
        large_data = "value" * 10000
        self.item.value = large_data
        self.item.calculate_size()
        
        # Testar compressão
        compressed = self.item.compress()
        self.assertTrue(compressed)
        self.assertLess(self.item.compression_ratio, 1.0)
        
        # Testar descompressão
        decompressed = self.item.decompress()
        self.assertTrue(decompressed)
        self.assertEqual(self.item.value, large_data)


class TestCacheMetrics(unittest.TestCase):
    """Testes para CacheMetrics."""
    
    def setUp(self):
        """Configuração inicial."""
        self.metrics = CacheMetrics()
    
    def test_hit_rate_zero_requests(self):
        """Testa hit rate com zero requisições."""
        self.assertEqual(self.metrics.hit_rate, 0.0)
    
    def test_hit_rate_calculation(self):
        """Testa cálculo de hit rate."""
        self.metrics.total_requests = 100
        self.metrics.hits = 90
        self.metrics.misses = 10
        
        self.assertEqual(self.metrics.hit_rate, 0.9)
        self.assertEqual(self.metrics.miss_rate, 0.1)


class TestAdaptiveTTLManager(unittest.TestCase):
    """Testes para AdaptiveTTLManager."""
    
    def setUp(self):
        """Configuração inicial."""
        self.ttl_manager = AdaptiveTTLManager()
    
    def test_record_access(self):
        """Testa registro de acesso."""
        self.ttl_manager.record_access("test_key", 60, True)
        
        self.assertIn("test_key", self.ttl_manager.access_patterns)
        self.assertEqual(len(self.ttl_manager.access_patterns["test_key"]), 1)
    
    def test_calculate_optimal_ttl_no_patterns(self):
        """Testa cálculo de TTL sem padrões."""
        optimal_ttl = self.ttl_manager.calculate_optimal_ttl("test_key", 60)
        self.assertEqual(optimal_ttl, 60)
    
    def test_calculate_optimal_ttl_with_patterns(self):
        """Testa cálculo de TTL com padrões."""
        # Simular acessos frequentes
        for index in range(20):
            self.ttl_manager.record_access("test_key", 60, True)
        
        optimal_ttl = self.ttl_manager.calculate_optimal_ttl("test_key", 60)
        self.assertGreater(optimal_ttl, 60)  # Deve aumentar TTL


class TestL1Cache(unittest.TestCase):
    """Testes para L1Cache."""
    
    def setUp(self):
        """Configuração inicial."""
        self.cache = L1Cache(max_size=3, eviction_policy=EvictionPolicy.LRU)
    
    def test_set_and_get(self):
        """Testa set e get básico."""
        self.cache.set("key1", "value1", ttl=60)
        item = self.cache.get("key1")
        
        self.assertIsNotNone(item)
        self.assertEqual(item.value, "value1")
    
    def test_eviction_lru(self):
        """Testa evição LRU."""
        # Preencher cache
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.set("key3", "value3")
        
        # Acessar key1 para torná-la mais recente
        self.cache.get("key1")
        
        # Adicionar novo item (deve evictar key2)
        self.cache.set("key4", "value4")
        
        # Verificar que key2 foi removida
        self.assertIsNone(self.cache.get("key2"))
        self.assertIsNotNone(self.cache.get("key1"))
        self.assertIsNotNone(self.cache.get("key3"))
        self.assertIsNotNone(self.cache.get("key4"))
    
    def test_adaptive_eviction(self):
        """Testa evição adaptativa."""
        cache = L1Cache(max_size=3, eviction_policy=EvictionPolicy.ADAPTIVE)
        
        # Preencher cache
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        # Acessar key1 múltiplas vezes
        for _ in range(10):
            cache.get("key1")
        
        # Adicionar novo item (deve evictar key2 ou key3, não key1)
        cache.set("key4", "value4")
        
        # Verificar que key1 ainda existe
        self.assertIsNotNone(cache.get("key1"))
    
    def test_delete(self):
        """Testa remoção de item."""
        self.cache.set("key1", "value1")
        self.assertTrue(self.cache.delete("key1"))
        self.assertIsNone(self.cache.get("key1"))
    
    def test_clear(self):
        """Testa limpeza do cache."""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        self.cache.clear()
        
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNone(self.cache.get("key2"))


class TestL2Cache(unittest.TestCase):
    """Testes para L2Cache."""
    
    def setUp(self):
        """Configuração inicial."""
        self.cache = L2Cache()
    
    def test_set_and_get(self):
        """Testa set e get básico."""
        self.cache.set("key1", "value1", ttl=60)
        item = self.cache.get("key1")
        
        self.assertIsNotNone(item)
        self.assertEqual(item.value, "value1")
    
    def test_compression(self):
        """Testa compressão automática."""
        large_data = "value" * 10000
        self.cache.set("large_key", large_data, ttl=60)
        item = self.cache.get("large_key")
        
        self.assertIsNotNone(item)
        self.assertEqual(item.value, large_data)
        self.assertLess(item.compression_ratio, 1.0)
    
    def test_delete(self):
        """Testa remoção de item."""
        self.cache.set("key1", "value1")
        self.assertTrue(self.cache.delete("key1"))
        self.assertIsNone(self.cache.get("key1"))
    
    def test_clear(self):
        """Testa limpeza do cache."""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        self.cache.clear()
        
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNone(self.cache.get("key2"))


class TestIntelligentCacheSystem(unittest.TestCase):
    """Testes para IntelligentCacheSystem."""
    
    def setUp(self):
        """Configuração inicial."""
        self.cache_system = IntelligentCacheSystem(
            enable_l1=True,
            enable_l2=True,
            l1_max_size=100,
            enable_compression=True,
            enable_adaptive_ttl=True
        )
    
    def test_set_and_get(self):
        """Testa set e get básico."""
        self.cache_system.set("key1", "value1", ttl=60)
        value = self.cache_system.get("key1")
        
        self.assertEqual(value, "value1")
    
    def test_get_or_set(self):
        """Testa get_or_set."""
        def getter():
            return "computed_value"
        
        # Primeira chamada (miss)
        value1 = self.cache_system.get_or_set("key1", getter, ttl=60)
        self.assertEqual(value1, "computed_value")
        
        # Segunda chamada (hit)
        value2 = self.cache_system.get_or_set("key1", getter, ttl=60)
        self.assertEqual(value2, "computed_value")
    
    def test_hit_rate_optimization(self):
        """Testa otimização de hit rate."""
        def expensive_operation(key):
            time.sleep(0.01)  # Simular operação cara
            return f"result_{key}"
        
        # Simular padrão de acesso com alta reutilização
        keys = ["key1", "key2", "key3"]
        
        # Primeira rodada - todos miss
        for key in keys:
            self.cache_system.get_or_set(key, lambda key=key: expensive_operation(key), ttl=60)
        
        # Segunda rodada - todos hit
        for key in keys:
            self.cache_system.get_or_set(key, lambda key=key: expensive_operation(key), ttl=60)
        
        # Terceira rodada - todos hit
        for key in keys:
            self.cache_system.get_or_set(key, lambda key=key: expensive_operation(key), ttl=60)
        
        stats = self.cache_system.get_stats()
        hit_rate = stats['global_metrics']['hit_rate']
        
        # Hit rate deve ser > 90% após múltiplos acessos
        self.assertGreater(hit_rate, 0.9)
    
    def test_adaptive_ttl(self):
        """Testa TTL adaptativo."""
        # Simular acessos frequentes
        for index in range(20):
            self.cache_system.get_or_set("frequent_key", lambda: "value", ttl=60)
        
        # Verificar se TTL foi adaptado
        stats = self.cache_system.get_stats()
        ttl_adaptations = stats['global_metrics']['ttl_adaptations']
        
        self.assertGreater(ttl_adaptations, 0)
    
    def test_compression(self):
        """Testa compressão automática."""
        large_data = "value" * 10000
        self.cache_system.set("large_key", large_data, ttl=60)
        
        # Verificar se foi comprimido
        stats = self.cache_system.get_stats()
        compression_savings = stats['global_metrics']['compression_savings']
        
        self.assertGreater(compression_savings, 0)
    
    def test_cache_warming(self):
        """Testa cache warming."""
        def getter(key):
            return f"warmed_{key}"
        
        keys = ["key1", "key2", "key3"]
        self.cache_system.warm_cache(keys, getter, ttl=60)
        
        # Verificar se todos os itens estão no cache
        for key in keys:
            value = self.cache_system.get(key)
            self.assertEqual(value, f"warmed_{key}")
    
    def test_pattern_invalidation(self):
        """Testa invalidação por padrão."""
        # Adicionar itens
        self.cache_system.set("user_123_data", "value1")
        self.cache_system.set("user_123_config", "value2")
        self.cache_system.set("other_data", "value3")
        
        # Invalidar padrão
        self.cache_system.invalidate_pattern("user_123_*")
        
        # Verificar que itens do padrão foram removidos
        self.assertIsNone(self.cache_system.get("user_123_data"))
        self.assertIsNone(self.cache_system.get("user_123_config"))
        
        # Verificar que outros itens permanecem
        self.assertIsNotNone(self.cache_system.get("other_data"))
    
    def test_concurrent_access(self):
        """Testa acesso concorrente."""
        def worker(worker_id):
            for index in range(10):
                key = f"worker_{worker_id}_key_{index}"
                self.cache_system.get_or_set(key, lambda key=key: f"value_{key}", ttl=60)
        
        # Criar múltiplas threads
        threads = []
        for index in range(5):
            thread = threading.Thread(target=worker, args=(index,))
            threads.append(thread)
            thread.start()
        
        # Aguardar conclusão
        for thread in threads:
            thread.join()
        
        # Verificar que não houve erros
        stats = self.cache_system.get_stats()
        self.assertGreater(stats['global_metrics']['total_requests'], 0)
    
    def test_memory_management(self):
        """Testa gerenciamento de memória."""
        # Adicionar muitos itens pequenos
        for index in range(200):
            self.cache_system.set(f"key_{index}", f"value_{index}", ttl=60)
        
        # Verificar que cache não excedeu limite
        stats = self.cache_system.get_stats()
        l1_stats = stats.get('l1_cache', {})
        
        if l1_stats:
            self.assertLessEqual(l1_stats['size'], 100)  # max_size
    
    def test_ttl_expiration(self):
        """Testa expiração de TTL."""
        # Adicionar item com TTL curto
        self.cache_system.set("expire_key", "value", ttl=1)
        
        # Aguardar expiração
        time.sleep(2)
        
        # Verificar que item expirou
        value = self.cache_system.get("expire_key")
        self.assertIsNone(value)
    
    def test_get_stats(self):
        """Testa obtenção de estatísticas."""
        # Adicionar alguns itens
        self.cache_system.set("key1", "value1")
        self.cache_system.set("key2", "value2")
        self.cache_system.get("key1")
        self.cache_system.get("nonexistent")
        
        stats = self.cache_system.get_stats()
        
        # Verificar estrutura das estatísticas
        self.assertIn('global_metrics', stats)
        self.assertIn('l1_cache', stats)
        self.assertIn('l2_cache', stats)
        self.assertIn('access_patterns', stats)
        
        # Verificar métricas básicas
        global_metrics = stats['global_metrics']
        self.assertGreater(global_metrics['total_requests'], 0)
        self.assertGreaterEqual(global_metrics['hits'], 0)
        self.assertGreaterEqual(global_metrics['misses'], 0)


class TestCacheDecorator(unittest.TestCase):
    """Testes para decorator de cache."""
    
    def setUp(self):
        """Configuração inicial."""
        self.cache_system = IntelligentCacheSystem()
    
    def test_cache_decorator(self):
        """Testa decorator de cache."""
        call_count = 0
        
        @cache_decorator(ttl=60)
        def expensive_function(value, result):
            nonlocal call_count
            call_count += 1
            return value + result
        
        # Primeira chamada
        result1 = expensive_function(1, 2)
        self.assertEqual(result1, 3)
        self.assertEqual(call_count, 1)
        
        # Segunda chamada (deve usar cache)
        result2 = expensive_function(1, 2)
        self.assertEqual(result2, 3)
        self.assertEqual(call_count, 1)  # Não deve chamar função novamente
        
        # Chamada com parâmetros diferentes
        result3 = expensive_function(2, 3)
        self.assertEqual(result3, 5)
        self.assertEqual(call_count, 2)  # Deve chamar função novamente


class TestPerformanceBenchmarks(unittest.TestCase):
    """Testes de performance."""
    
    def setUp(self):
        """Configuração inicial."""
        self.cache_system = IntelligentCacheSystem(
            enable_l1=True,
            enable_l2=True,
            l1_max_size=1000,
            enable_compression=True,
            enable_adaptive_ttl=True
        )
    
    def test_high_frequency_access(self):
        """Testa acesso de alta frequência."""
        start_time = time.time()
        
        # Simular 1000 acessos
        for index in range(1000):
            key = f"key_{index % 100}"  # Reutilizar chaves
            self.cache_system.get_or_set(key, lambda key=key: f"value_{key}", ttl=60)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Verificar performance (deve ser rápido)
        self.assertLess(duration, 5.0)  # Máximo 5 segundos
        
        # Verificar hit rate alto
        stats = self.cache_system.get_stats()
        hit_rate = stats['global_metrics']['hit_rate']
        self.assertGreater(hit_rate, 0.8)  # Pelo menos 80% de hit rate
    
    def test_large_data_handling(self):
        """Testa manipulação de dados grandes."""
        large_data = "value" * 100000  # 100KB
        
        start_time = time.time()
        
        # Adicionar 10 itens grandes
        for index in range(10):
            self.cache_system.set(f"large_key_{index}", large_data, ttl=60)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Verificar que compressão funcionou
        stats = self.cache_system.get_stats()
        compression_savings = stats['global_metrics']['compression_savings']
        self.assertGreater(compression_savings, 0)
        
        # Verificar que operação foi rápida
        self.assertLess(duration, 2.0)  # Máximo 2 segundos


if __name__ == '__main__':
    # Executar testes
    unittest.main(verbosity=2) 