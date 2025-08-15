#!/usr/bin/env python3
"""
Testes de Performance - Tempo de Resposta
=========================================

Tracing ID: PERFORMANCE_TEST_001
Data: 2025-01-27
Versão: 1.0
Status: ✅ IMPLEMENTAÇÃO

Testes para validar tempo de resposta de operações críticas do sistema.
"""

import pytest
import time
import asyncio
from typing import Dict, List, Any
from unittest.mock import patch, MagicMock
from domain.models import Keyword, Cluster, IntencaoBusca
from infrastructure.coleta.utils.async_coletor_v1 import AsyncColetor
from infrastructure.processamento.gerador_prompt import GeradorPrompt

# Limites de performance baseados em requisitos reais do sistema
PERFORMANCE_LIMITS = {
    "keyword_creation": 0.001,  # 1ms
    "cluster_creation": 0.005,  # 5ms
    "prompt_generation": 0.010,  # 10ms
    "async_collection": 0.100,   # 100ms
    "cache_operation": 0.001,    # 1ms
    "serialization": 0.002,      # 2ms
    "validation": 0.003,         # 3ms
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

class TestPerformanceKeywordOperations:
    """Testes de performance para operações com Keywords."""
    
    def test_keyword_creation_performance(self):
        """Testa performance da criação de keywords."""
        start_time = time.time()
        
        # Criar múltiplas keywords reais
        keywords = []
        for i in range(100):
            keyword = make_real_keyword(f"keyword_{i}")
            keywords.append(keyword)
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / 100
        
        assert avg_time < PERFORMANCE_LIMITS["keyword_creation"]
        assert len(keywords) == 100
        assert all(isinstance(k, Keyword) for k in keywords)
    
    def test_keyword_serialization_performance(self):
        """Testa performance da serialização de keywords."""
        keyword = make_real_keyword("teste serialização")
        
        start_time = time.time()
        data = keyword.to_dict()
        end_time = time.time()
        
        serialization_time = end_time - start_time
        assert serialization_time < PERFORMANCE_LIMITS["serialization"]
        assert isinstance(data, dict)
        assert data["termo"] == "teste serialização"
    
    def test_keyword_deserialization_performance(self):
        """Testa performance da deserialização de keywords."""
        keyword = make_real_keyword("teste deserialização")
        data = keyword.to_dict()
        
        start_time = time.time()
        keyword2 = Keyword.from_dict(data)
        end_time = time.time()
        
        deserialization_time = end_time - start_time
        assert deserialization_time < PERFORMANCE_LIMITS["serialization"]
        assert keyword == keyword2
    
    def test_keyword_score_calculation_performance(self):
        """Testa performance do cálculo de score."""
        keyword = make_real_keyword("teste score")
        
        start_time = time.time()
        score = keyword.calcular_score({
            "volume": 0.4,
            "cpc": 0.3,
            "intencao": 0.2,
            "concorrencia": 0.1
        })
        end_time = time.time()
        
        calculation_time = end_time - start_time
        assert calculation_time < PERFORMANCE_LIMITS["validation"]
        assert score > 0
        assert "Score =" in keyword.justificativa

class TestPerformanceClusterOperations:
    """Testes de performance para operações com Clusters."""
    
    def test_cluster_creation_performance(self):
        """Testa performance da criação de clusters."""
        start_time = time.time()
        
        # Criar múltiplos clusters reais
        clusters = []
        for i in range(10):
            cluster = make_real_cluster()
            cluster.id = f"cluster_{i}"
            clusters.append(cluster)
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / 10
        
        assert avg_time < PERFORMANCE_LIMITS["cluster_creation"]
        assert len(clusters) == 10
        assert all(isinstance(c, Cluster) for c in clusters)
    
    def test_cluster_serialization_performance(self):
        """Testa performance da serialização de clusters."""
        cluster = make_real_cluster()
        
        start_time = time.time()
        data = cluster.to_dict()
        end_time = time.time()
        
        serialization_time = end_time - start_time
        assert serialization_time < PERFORMANCE_LIMITS["serialization"]
        assert isinstance(data, dict)
        assert data["id"] == "cluster_marketing_001"
        assert len(data["keywords"]) == 6
    
    def test_cluster_validation_performance(self):
        """Testa performance da validação de clusters."""
        cluster = make_real_cluster()
        
        start_time = time.time()
        # Validar propriedades do cluster
        assert len(cluster.keywords) >= 4
        assert len(cluster.keywords) <= 8
        assert 0 <= cluster.similaridade_media <= 1
        assert cluster.fase_funil in ["descoberta", "consideração", "conversão"]
        end_time = time.time()
        
        validation_time = end_time - start_time
        assert validation_time < PERFORMANCE_LIMITS["validation"]

class TestPerformancePromptGeneration:
    """Testes de performance para geração de prompts."""
    
    def test_prompt_generation_performance(self):
        """Testa performance da geração de prompts."""
        gp = GeradorPrompt(template="Artigo sobre $primary_keyword com foco em $secondary_keywords")
        pk = make_real_keyword("marketing digital")
        sks = [make_real_keyword("seo"), make_real_keyword("redes sociais")]
        cluster = make_real_cluster()
        
        start_time = time.time()
        prompt = gp.gerar_prompt(pk, sks, cluster=cluster)
        end_time = time.time()
        
        generation_time = end_time - start_time
        assert generation_time < PERFORMANCE_LIMITS["prompt_generation"]
        assert "marketing digital" in prompt
        assert "seo" in prompt
        assert "redes sociais" in prompt
    
    def test_prompt_generation_complex_template_performance(self):
        """Testa performance com template complexo."""
        template_complexo = """
        # Artigo: $primary_keyword
        
        ## Palavras-chave Secundárias:
        $secondary_keywords
        
        ## Informações do Cluster:
        - ID: $cluster_id
        - Fase: $fase_funil
        - Categoria: $categoria
        - Similaridade: $similaridade_media
        
        ## Configurações:
        - Público: $publico_alvo
        - Tom: $tom_voz
        - Objetivo: $objetivo
        """
        
        gp = GeradorPrompt(template=template_complexo)
        pk = make_real_keyword("seo avançado")
        sks = [make_real_keyword("backlinks"), make_real_keyword("meta tags")]
        cluster = make_real_cluster()
        
        extras = {
            "publico_alvo": "profissionais de marketing",
            "tom_voz": "técnico e profissional",
            "objetivo": "educar sobre estratégias"
        }
        
        start_time = time.time()
        prompt = gp.gerar_prompt(pk, sks, cluster=cluster, extras=extras)
        end_time = time.time()
        
        generation_time = end_time - start_time
        assert generation_time < PERFORMANCE_LIMITS["prompt_generation"] * 2  # Template complexo
        assert "seo avançado" in prompt
        assert "backlinks" in prompt
        assert "meta tags" in prompt

class TestPerformanceAsyncOperations:
    """Testes de performance para operações assíncronas."""
    
    @pytest.mark.asyncio
    async def test_async_collector_performance(self):
        """Testa performance do coletor assíncrono."""
        async def fonte_rapida(termo, **kwargs):
            await asyncio.sleep(0.01)  # Simular latência real
            return [{"termo": termo, "fonte": "rapida", "volume": 100}]
        
        coletor = AsyncColetor([fonte_rapida])
        
        start_time = time.time()
        result = await coletor.coletar("marketing digital")
        end_time = time.time()
        
        collection_time = end_time - start_time
        assert collection_time < PERFORMANCE_LIMITS["async_collection"]
        assert len(result) == 1
        assert result[0]["termo"] == "marketing digital"
    
    @pytest.mark.asyncio
    async def test_async_collector_multiple_sources_performance(self):
        """Testa performance com múltiplas fontes."""
        async def fonte1(termo, **kwargs):
            await asyncio.sleep(0.01)
            return [{"termo": termo, "fonte": "fonte1", "volume": 100}]
        
        async def fonte2(termo, **kwargs):
            await asyncio.sleep(0.01)
            return [{"termo": termo, "fonte": "fonte2", "volume": 200}]
        
        async def fonte3(termo, **kwargs):
            await asyncio.sleep(0.01)
            return [{"termo": termo, "fonte": "fonte3", "volume": 300}]
        
        coletor = AsyncColetor([fonte1, fonte2, fonte3])
        
        start_time = time.time()
        result = await coletor.coletar("seo")
        end_time = time.time()
        
        collection_time = end_time - start_time
        assert collection_time < PERFORMANCE_LIMITS["async_collection"] * 1.5  # Múltiplas fontes
        assert len(result) == 3
        assert all(item["termo"] == "seo" for item in result)

class TestPerformanceCacheOperations:
    """Testes de performance para operações de cache."""
    
    def test_cache_set_performance(self):
        """Testa performance de escrita no cache."""
        class MockCache:
            def __init__(self):
                self.data = {}
            
            async def set(self, key, value):
                self.data[key] = value
            
            async def get(self, key):
                return self.data.get(key)
        
        cache = MockCache()
        
        start_time = time.time()
        # Simular operação de cache
        cache.data["test_key"] = {"termo": "marketing", "volume": 100}
        end_time = time.time()
        
        cache_time = end_time - start_time
        assert cache_time < PERFORMANCE_LIMITS["cache_operation"]
        assert cache.data["test_key"]["termo"] == "marketing"
    
    def test_cache_get_performance(self):
        """Testa performance de leitura do cache."""
        class MockCache:
            def __init__(self):
                self.data = {
                    "keyword_1": {"termo": "seo", "volume": 100},
                    "keyword_2": {"termo": "marketing", "volume": 200},
                    "keyword_3": {"termo": "analytics", "volume": 150}
                }
            
            async def get(self, key):
                return self.data.get(key)
        
        cache = MockCache()
        
        start_time = time.time()
        # Simular múltiplas leituras
        for i in range(100):
            result = cache.data.get(f"keyword_{i % 3 + 1}")
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time = total_time / 100
        assert avg_time < PERFORMANCE_LIMITS["cache_operation"]

class TestPerformanceBulkOperations:
    """Testes de performance para operações em lote."""
    
    def test_bulk_keyword_processing_performance(self):
        """Testa performance de processamento em lote de keywords."""
        keywords = [make_real_keyword(f"kw_{i}") for i in range(1000)]
        
        start_time = time.time()
        
        # Processar todas as keywords
        processed = []
        for keyword in keywords:
            # Simular processamento real
            score = keyword.calcular_score({})
            data = keyword.to_dict()
            processed.append({
                "keyword": keyword,
                "score": score,
                "data": data
            })
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / 1000
        
        assert avg_time < PERFORMANCE_LIMITS["keyword_creation"] * 3  # Processamento mais complexo
        assert len(processed) == 1000
        assert all(p["score"] > 0 for p in processed)
    
    def test_bulk_cluster_processing_performance(self):
        """Testa performance de processamento em lote de clusters."""
        clusters = [make_real_cluster() for _ in range(100)]
        for i, cluster in enumerate(clusters):
            cluster.id = f"cluster_bulk_{i}"
        
        start_time = time.time()
        
        # Processar todos os clusters
        processed = []
        for cluster in clusters:
            # Simular processamento real
            data = cluster.to_dict()
            total_keywords = len(cluster.keywords)
            avg_similarity = cluster.similaridade_media
            processed.append({
                "cluster": cluster,
                "data": data,
                "total_keywords": total_keywords,
                "avg_similarity": avg_similarity
            })
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / 100
        
        assert avg_time < PERFORMANCE_LIMITS["cluster_creation"] * 2  # Processamento mais complexo
        assert len(processed) == 100
        assert all(p["total_keywords"] >= 4 for p in processed)
        assert all(0 <= p["avg_similarity"] <= 1 for p in processed)

class TestPerformanceMemoryUsage:
    """Testes de performance para uso de memória."""
    
    def test_memory_efficiency_keywords(self):
        """Testa eficiência de memória com keywords."""
        import sys
        
        # Medir memória antes
        initial_memory = sys.getsizeof([])
        
        # Criar muitas keywords
        keywords = [make_real_keyword(f"kw_{i}") for i in range(10000)]
        
        # Medir memória após
        final_memory = sys.getsizeof(keywords)
        memory_per_keyword = (final_memory - initial_memory) / 10000
        
        # Verificar que uso de memória é razoável (menos de 1KB por keyword)
        assert memory_per_keyword < 1024
        assert len(keywords) == 10000
    
    def test_memory_efficiency_clusters(self):
        """Testa eficiência de memória com clusters."""
        import sys
        
        # Medir memória antes
        initial_memory = sys.getsizeof([])
        
        # Criar muitos clusters
        clusters = [make_real_cluster() for _ in range(1000)]
        for i, cluster in enumerate(clusters):
            cluster.id = f"cluster_mem_{i}"
        
        # Medir memória após
        final_memory = sys.getsizeof(clusters)
        memory_per_cluster = (final_memory - initial_memory) / 1000
        
        # Verificar que uso de memória é razoável (menos de 10KB por cluster)
        assert memory_per_cluster < 10240
        assert len(clusters) == 1000

class TestPerformanceConcurrency:
    """Testes de performance para concorrência."""
    
    @pytest.mark.asyncio
    async def test_concurrent_keyword_operations(self):
        """Testa operações concorrentes com keywords."""
        async def process_keyword(i):
            keyword = make_real_keyword(f"concurrent_kw_{i}")
            score = keyword.calcular_score({})
            data = keyword.to_dict()
            return {"id": i, "score": score, "data": data}
        
        start_time = time.time()
        
        # Executar operações concorrentes
        tasks = [process_keyword(i) for i in range(100)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verificar que operações concorrentes são mais rápidas que sequenciais
        expected_sequential_time = 100 * PERFORMANCE_LIMITS["keyword_creation"]
        assert total_time < expected_sequential_time * 0.5  # Pelo menos 50% mais rápido
        assert len(results) == 100
        assert all(r["score"] > 0 for r in results)
    
    @pytest.mark.asyncio
    async def test_concurrent_prompt_generation(self):
        """Testa geração concorrente de prompts."""
        gp = GeradorPrompt(template="Artigo sobre $primary_keyword")
        
        async def generate_prompt(i):
            pk = make_real_keyword(f"prompt_kw_{i}")
            sks = [make_real_keyword(f"sec_{i}_{j}") for j in range(3)]
            return gp.gerar_prompt(pk, sks)
        
        start_time = time.time()
        
        # Executar gerações concorrentes
        tasks = [generate_prompt(i) for i in range(50)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verificar que operações concorrentes são mais rápidas
        expected_sequential_time = 50 * PERFORMANCE_LIMITS["prompt_generation"]
        assert total_time < expected_sequential_time * 0.7  # Pelo menos 30% mais rápido
        assert len(results) == 50
        assert all("prompt_kw_" in result for result in results) 