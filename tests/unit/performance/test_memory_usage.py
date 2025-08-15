#!/usr/bin/env python3
"""
Testes de Performance - Uso de Memória
======================================

Tracing ID: PERFORMANCE_TEST_002
Data: 2025-01-27
Versão: 1.0
Status: ✅ IMPLEMENTAÇÃO

Testes para validar eficiência de memória de operações críticas do sistema.
"""

import pytest
import time
import sys
import gc
import psutil
import os
from typing import Dict, List, Any
from unittest.mock import patch, MagicMock
from domain.models import Keyword, Cluster, IntencaoBusca
from infrastructure.coleta.utils.async_coletor_v1 import AsyncColetor
from infrastructure.processamento.gerador_prompt import GeradorPrompt

# Limites de memória baseados em requisitos reais do sistema
MEMORY_LIMITS = {
    "keyword_object": 1024,      # 1KB por keyword
    "cluster_object": 10240,     # 10KB por cluster
    "prompt_object": 2048,       # 2KB por prompt
    "cache_entry": 512,          # 512B por entrada de cache
    "bulk_operation": 1048576,   # 1MB para operações em lote
    "memory_leak_threshold": 0.1, # 10% de crescimento máximo
}

def make_real_keyword(termo: str = "marketing digital") -> Keyword:
    """Cria keyword real baseada em dados do sistema."""
    return Keyword(
        termo=termo,
        volume_busca=1200,
        cpc=2.5,
        concorrencia=0.7,
        intencao=IntencaoBusca.COMERCIAL,
        score=0.85,
        justificativa="Score calculado baseado em volume e CPC",
        fonte="google_ads",
        data_coleta=time.time(),
        ordem_no_cluster=1,
        fase_funil="consideração",
        nome_artigo="Artigo sobre marketing digital"
    )

def make_real_cluster() -> Cluster:
    """Cria cluster real baseado em dados do sistema."""
    keywords = [
        make_real_keyword("marketing digital"),
        make_real_keyword("seo avançado"),
        make_real_keyword("redes sociais"),
        make_real_keyword("email marketing"),
        make_real_keyword("analytics"),
        make_real_keyword("conversão")
    ]
    
    return Cluster(
        id="cluster_marketing_001",
        keywords=keywords,
        similaridade_media=0.85,
        fase_funil="consideração",
        categoria="marketing",
        blog_dominio="meublog.com",
        data_criacao=time.time(),
        status_geracao="concluida",
        prompt_gerado="Prompt real gerado para cluster de marketing"
    )

def get_memory_usage():
    """Obtém uso de memória atual do processo."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss

def measure_object_memory(obj):
    """Mede memória usada por um objeto."""
    return sys.getsizeof(obj)

class TestMemoryEfficiencyKeywords:
    """Testes de eficiência de memória para Keywords."""
    
    def test_keyword_object_memory_footprint(self):
        """Testa footprint de memória de objetos Keyword."""
        keyword = make_real_keyword("teste memória")
        
        memory_used = measure_object_memory(keyword)
        assert memory_used < MEMORY_LIMITS["keyword_object"]
        
        # Verificar que objeto é válido
        assert keyword.termo == "teste memória"
        assert keyword.volume_busca == 1200
        assert keyword.cpc == 2.5
    
    def test_keyword_list_memory_efficiency(self):
        """Testa eficiência de memória com listas de keywords."""
        initial_memory = get_memory_usage()
        
        # Criar lista de keywords
        keywords = [make_real_keyword(f"kw_{i}") for i in range(1000)]
        
        final_memory = get_memory_usage()
        memory_increase = final_memory - initial_memory
        memory_per_keyword = memory_increase / 1000
        
        assert memory_per_keyword < MEMORY_LIMITS["keyword_object"]
        assert len(keywords) == 1000
        assert all(isinstance(k, Keyword) for k in keywords)
    
    def test_keyword_serialization_memory(self):
        """Testa uso de memória na serialização de keywords."""
        keyword = make_real_keyword("serialização memória")
        
        # Medir memória antes da serialização
        initial_memory = get_memory_usage()
        
        # Serializar
        data = keyword.to_dict()
        
        # Medir memória após serialização
        final_memory = get_memory_usage()
        memory_used = final_memory - initial_memory
        
        assert memory_used < MEMORY_LIMITS["keyword_object"]
        assert isinstance(data, dict)
        assert data["termo"] == "serialização memória"
    
    def test_keyword_deserialization_memory(self):
        """Testa uso de memória na deserialização de keywords."""
        keyword = make_real_keyword("deserialização memória")
        data = keyword.to_dict()
        
        # Medir memória antes da deserialização
        initial_memory = get_memory_usage()
        
        # Deserializar
        keyword2 = Keyword.from_dict(data)
        
        # Medir memória após deserialização
        final_memory = get_memory_usage()
        memory_used = final_memory - initial_memory
        
        assert memory_used < MEMORY_LIMITS["keyword_object"]
        assert keyword == keyword2

class TestMemoryEfficiencyClusters:
    """Testes de eficiência de memória para Clusters."""
    
    def test_cluster_object_memory_footprint(self):
        """Testa footprint de memória de objetos Cluster."""
        cluster = make_real_cluster()
        
        memory_used = measure_object_memory(cluster)
        assert memory_used < MEMORY_LIMITS["cluster_object"]
        
        # Verificar que objeto é válido
        assert cluster.id == "cluster_marketing_001"
        assert len(cluster.keywords) == 6
        assert cluster.similaridade_media == 0.85
    
    def test_cluster_list_memory_efficiency(self):
        """Testa eficiência de memória com listas de clusters."""
        initial_memory = get_memory_usage()
        
        # Criar lista de clusters
        clusters = [make_real_cluster() for _ in range(100)]
        for i, cluster in enumerate(clusters):
            cluster.id = f"cluster_mem_{i}"
        
        final_memory = get_memory_usage()
        memory_increase = final_memory - initial_memory
        memory_per_cluster = memory_increase / 100
        
        assert memory_per_cluster < MEMORY_LIMITS["cluster_object"]
        assert len(clusters) == 100
        assert all(isinstance(c, Cluster) for c in clusters)
    
    def test_cluster_serialization_memory(self):
        """Testa uso de memória na serialização de clusters."""
        cluster = make_real_cluster()
        
        # Medir memória antes da serialização
        initial_memory = get_memory_usage()
        
        # Serializar
        data = cluster.to_dict()
        
        # Medir memória após serialização
        final_memory = get_memory_usage()
        memory_used = final_memory - initial_memory
        
        assert memory_used < MEMORY_LIMITS["cluster_object"]
        assert isinstance(data, dict)
        assert data["id"] == "cluster_marketing_001"
        assert len(data["keywords"]) == 6

class TestMemoryEfficiencyPromptGeneration:
    """Testes de eficiência de memória para geração de prompts."""
    
    def test_prompt_generation_memory_footprint(self):
        """Testa footprint de memória na geração de prompts."""
        gp = GeradorPrompt(template="Artigo sobre $primary_keyword")
        pk = make_real_keyword("marketing digital")
        sks = [make_real_keyword("seo"), make_real_keyword("redes sociais")]
        
        # Medir memória antes da geração
        initial_memory = get_memory_usage()
        
        # Gerar prompt
        prompt = gp.gerar_prompt(pk, sks)
        
        # Medir memória após geração
        final_memory = get_memory_usage()
        memory_used = final_memory - initial_memory
        
        assert memory_used < MEMORY_LIMITS["prompt_object"]
        assert "marketing digital" in prompt
        assert "seo" in prompt
        assert "redes sociais" in prompt
    
    def test_prompt_generation_bulk_memory(self):
        """Testa uso de memória em geração em lote de prompts."""
        gp = GeradorPrompt(template="Artigo sobre $primary_keyword")
        
        # Medir memória antes
        initial_memory = get_memory_usage()
        
        # Gerar múltiplos prompts
        prompts = []
        for i in range(100):
            pk = make_real_keyword(f"kw_{i}")
            sks = [make_real_keyword(f"sec_{i}_{j}") for j in range(3)]
            prompt = gp.gerar_prompt(pk, sks)
            prompts.append(prompt)
        
        # Medir memória após
        final_memory = get_memory_usage()
        memory_used = final_memory - initial_memory
        
        assert memory_used < MEMORY_LIMITS["bulk_operation"]
        assert len(prompts) == 100
        assert all(f"kw_{i}" in prompt for i, prompt in enumerate(prompts))

class TestMemoryEfficiencyCache:
    """Testes de eficiência de memória para operações de cache."""
    
    def test_cache_entry_memory_footprint(self):
        """Testa footprint de memória de entradas de cache."""
        class MockCache:
            def __init__(self):
                self.data = {}
            
            async def set(self, key, value):
                self.data[key] = value
            
            async def get(self, key):
                return self.data.get(key)
        
        cache = MockCache()
        
        # Medir memória antes
        initial_memory = get_memory_usage()
        
        # Adicionar entrada de cache
        cache.data["test_key"] = {"termo": "marketing", "volume": 100}
        
        # Medir memória após
        final_memory = get_memory_usage()
        memory_used = final_memory - initial_memory
        
        assert memory_used < MEMORY_LIMITS["cache_entry"]
        assert cache.data["test_key"]["termo"] == "marketing"
    
    def test_cache_bulk_operations_memory(self):
        """Testa uso de memória em operações em lote de cache."""
        class MockCache:
            def __init__(self):
                self.data = {}
            
            async def set(self, key, value):
                self.data[key] = value
        
        cache = MockCache()
        
        # Medir memória antes
        initial_memory = get_memory_usage()
        
        # Adicionar múltiplas entradas
        for i in range(1000):
            cache.data[f"key_{i}"] = {
                "termo": f"keyword_{i}",
                "volume": i * 10,
                "cpc": i * 0.1
            }
        
        # Medir memória após
        final_memory = get_memory_usage()
        memory_used = final_memory - initial_memory
        memory_per_entry = memory_used / 1000
        
        assert memory_per_entry < MEMORY_LIMITS["cache_entry"]
        assert len(cache.data) == 1000

class TestMemoryLeakDetection:
    """Testes para detecção de vazamentos de memória."""
    
    def test_keyword_creation_no_memory_leak(self):
        """Testa que criação de keywords não causa vazamento de memória."""
        initial_memory = get_memory_usage()
        
        # Criar e destruir keywords múltiplas vezes
        for _ in range(10):
            keywords = [make_real_keyword(f"kw_{i}") for i in range(100)]
            del keywords
            gc.collect()
        
        final_memory = get_memory_usage()
        memory_growth = (final_memory - initial_memory) / initial_memory
        
        assert memory_growth < MEMORY_LIMITS["memory_leak_threshold"]
    
    def test_cluster_creation_no_memory_leak(self):
        """Testa que criação de clusters não causa vazamento de memória."""
        initial_memory = get_memory_usage()
        
        # Criar e destruir clusters múltiplas vezes
        for _ in range(10):
            clusters = [make_real_cluster() for _ in range(10)]
            del clusters
            gc.collect()
        
        final_memory = get_memory_usage()
        memory_growth = (final_memory - initial_memory) / initial_memory
        
        assert memory_growth < MEMORY_LIMITS["memory_leak_threshold"]
    
    def test_prompt_generation_no_memory_leak(self):
        """Testa que geração de prompts não causa vazamento de memória."""
        gp = GeradorPrompt(template="Artigo sobre $primary_keyword")
        initial_memory = get_memory_usage()
        
        # Gerar e destruir prompts múltiplas vezes
        for _ in range(10):
            prompts = []
            for i in range(50):
                pk = make_real_keyword(f"kw_{i}")
                sks = [make_real_keyword(f"sec_{i}")]
                prompt = gp.gerar_prompt(pk, sks)
                prompts.append(prompt)
            del prompts
            gc.collect()
        
        final_memory = get_memory_usage()
        memory_growth = (final_memory - initial_memory) / initial_memory
        
        assert memory_growth < MEMORY_LIMITS["memory_leak_threshold"]

class TestMemoryEfficiencyAsyncOperations:
    """Testes de eficiência de memória para operações assíncronas."""
    
    @pytest.mark.asyncio
    async def test_async_collector_memory_efficiency(self):
        """Testa eficiência de memória do coletor assíncrono."""
        async def fonte_memoria(termo, **kwargs):
            return [{"termo": termo, "fonte": "memoria", "volume": 100}]
        
        coletor = AsyncColetor([fonte_memoria])
        
        # Medir memória antes
        initial_memory = get_memory_usage()
        
        # Executar coleta
        result = await coletor.coletar("teste memória")
        
        # Medir memória após
        final_memory = get_memory_usage()
        memory_used = final_memory - initial_memory
        
        assert memory_used < MEMORY_LIMITS["keyword_object"] * 10  # Múltiplas keywords
        assert len(result) == 1
        assert result[0]["termo"] == "teste memória"
    
    @pytest.mark.asyncio
    async def test_async_collector_bulk_memory(self):
        """Testa uso de memória em coleta em lote."""
        async def fonte_bulk(termo, **kwargs):
            return [{"termo": f"{termo}_{i}", "volume": 100 + i} for i in range(10)]
        
        coletor = AsyncColetor([fonte_bulk])
        
        # Medir memória antes
        initial_memory = get_memory_usage()
        
        # Executar múltiplas coletas
        results = []
        for i in range(10):
            result = await coletor.coletar(f"termo_{i}")
            results.append(result)
        
        # Medir memória após
        final_memory = get_memory_usage()
        memory_used = final_memory - initial_memory
        
        assert memory_used < MEMORY_LIMITS["bulk_operation"]
        assert len(results) == 10
        assert all(len(result) == 10 for result in results)

class TestMemoryEfficiencyBulkOperations:
    """Testes de eficiência de memória para operações em lote."""
    
    def test_bulk_keyword_processing_memory(self):
        """Testa uso de memória em processamento em lote de keywords."""
        initial_memory = get_memory_usage()
        
        # Processar muitas keywords
        keywords = [make_real_keyword(f"kw_{i}") for i in range(10000)]
        
        # Simular processamento
        processed = []
        for keyword in keywords:
            score = keyword.calcular_score({})
            data = keyword.to_dict()
            processed.append({
                "keyword": keyword,
                "score": score,
                "data": data
            })
        
        final_memory = get_memory_usage()
        memory_used = final_memory - initial_memory
        
        assert memory_used < MEMORY_LIMITS["bulk_operation"]
        assert len(processed) == 10000
        assert all(p["score"] > 0 for p in processed)
    
    def test_bulk_cluster_processing_memory(self):
        """Testa uso de memória em processamento em lote de clusters."""
        initial_memory = get_memory_usage()
        
        # Processar muitos clusters
        clusters = [make_real_cluster() for _ in range(1000)]
        for i, cluster in enumerate(clusters):
            cluster.id = f"cluster_bulk_{i}"
        
        # Simular processamento
        processed = []
        for cluster in clusters:
            data = cluster.to_dict()
            total_keywords = len(cluster.keywords)
            avg_similarity = cluster.similaridade_media
            processed.append({
                "cluster": cluster,
                "data": data,
                "total_keywords": total_keywords,
                "avg_similarity": avg_similarity
            })
        
        final_memory = get_memory_usage()
        memory_used = final_memory - initial_memory
        
        assert memory_used < MEMORY_LIMITS["bulk_operation"]
        assert len(processed) == 1000
        assert all(p["total_keywords"] >= 4 for p in processed)

class TestMemoryEfficiencyDataStructures:
    """Testes de eficiência de memória para estruturas de dados."""
    
    def test_dict_vs_list_memory_efficiency(self):
        """Testa eficiência de memória entre dict e list para keywords."""
        keywords_list = [make_real_keyword(f"kw_{i}") for i in range(100)]
        keywords_dict = {f"kw_{i}": make_real_keyword(f"kw_{i}") for i in range(100)}
        
        list_memory = measure_object_memory(keywords_list)
        dict_memory = measure_object_memory(keywords_dict)
        
        # Dict deve usar mais memória que list para o mesmo número de elementos
        assert dict_memory > list_memory
        assert len(keywords_list) == len(keywords_dict)
    
    def test_set_memory_efficiency(self):
        """Testa eficiência de memória de sets para termos únicos."""
        termos = [f"termo_{i % 50}" for i in range(100)]  # 50 termos únicos
        
        list_memory = measure_object_memory(termos)
        set_memory = measure_object_memory(set(termos))
        
        # Set deve usar menos memória para termos únicos
        assert set_memory < list_memory
        assert len(set(termos)) == 50
        assert len(termos) == 100
    
    def test_tuple_vs_list_memory_efficiency(self):
        """Testa eficiência de memória entre tuple e list."""
        keywords_list = [make_real_keyword(f"kw_{i}") for i in range(10)]
        keywords_tuple = tuple(keywords_list)
        
        list_memory = measure_object_memory(keywords_list)
        tuple_memory = measure_object_memory(keywords_tuple)
        
        # Tuple deve usar menos memória que list
        assert tuple_memory < list_memory
        assert len(keywords_list) == len(keywords_tuple)

class TestMemoryEfficiencyGarbageCollection:
    """Testes de eficiência de garbage collection."""
    
    def test_gc_effectiveness_keywords(self):
        """Testa efetividade do GC com keywords."""
        initial_memory = get_memory_usage()
        
        # Criar muitas keywords
        keywords = [make_real_keyword(f"kw_{i}") for i in range(10000)]
        
        # Forçar garbage collection
        del keywords
        gc.collect()
        
        final_memory = get_memory_usage()
        memory_recovered = initial_memory - final_memory
        
        # Deve haver recuperação significativa de memória
        assert memory_recovered > 0
        assert final_memory <= initial_memory
    
    def test_gc_effectiveness_clusters(self):
        """Testa efetividade do GC com clusters."""
        initial_memory = get_memory_usage()
        
        # Criar muitos clusters
        clusters = [make_real_cluster() for _ in range(1000)]
        
        # Forçar garbage collection
        del clusters
        gc.collect()
        
        final_memory = get_memory_usage()
        memory_recovered = initial_memory - final_memory
        
        # Deve haver recuperação significativa de memória
        assert memory_recovered > 0
        assert final_memory <= initial_memory
    
    def test_weak_references_memory_efficiency(self):
        """Testa eficiência de memória com weak references."""
        import weakref
        
        initial_memory = get_memory_usage()
        
        # Criar objetos com weak references
        keywords = [make_real_keyword(f"kw_{i}") for i in range(1000)]
        weak_refs = [weakref.ref(kw) for kw in keywords]
        
        # Remover referências fortes
        del keywords
        
        # Forçar garbage collection
        gc.collect()
        
        final_memory = get_memory_usage()
        memory_used = final_memory - initial_memory
        
        # Weak references devem usar menos memória
        assert memory_used < MEMORY_LIMITS["keyword_object"] * 100  # Apenas as weak refs
        assert all(ref() is None for ref in weak_refs)  # Objetos devem ser coletados 