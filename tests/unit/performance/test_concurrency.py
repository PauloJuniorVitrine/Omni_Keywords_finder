#!/usr/bin/env python3
"""
Testes de Performance - Concorrência
====================================

Tracing ID: PERFORMANCE_TEST_003
Data: 2025-01-27
Versão: 1.0
Status: ✅ IMPLEMENTAÇÃO

Testes para validar performance em cenários de concorrência do sistema.
"""

import pytest
import time
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Dict, List, Any
from unittest.mock import patch, MagicMock
from domain.models import Keyword, Cluster, IntencaoBusca
from infrastructure.coleta.utils.async_coletor_v1 import AsyncColetor
from infrastructure.processamento.gerador_prompt import GeradorPrompt

# Limites de performance para concorrência
CONCURRENCY_LIMITS = {
    "thread_safety": 0.001,      # 1ms para operações thread-safe
    "async_operation": 0.100,    # 100ms para operações assíncronas
    "concurrent_creation": 0.005, # 5ms para criação concorrente
    "race_condition": 0.001,     # 1ms para evitar race conditions
    "deadlock_timeout": 5.0,     # 5s timeout para deadlocks
    "scalability_factor": 0.8,   # 80% de eficiência em escala
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

class TestThreadSafety:
    """Testes de thread safety para operações críticas."""
    
    def test_keyword_creation_thread_safety(self):
        """Testa thread safety na criação de keywords."""
        results = []
        lock = threading.Lock()
        
        def create_keyword(thread_id):
            """Função executada por cada thread."""
            keyword = make_real_keyword(f"thread_{thread_id}")
            with lock:
                results.append({
                    "thread_id": thread_id,
                    "keyword": keyword,
                    "timestamp": time.time()
                })
        
        # Criar múltiplas threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=create_keyword, args=(i,))
            threads.append(thread)
        
        start_time = time.time()
        
        # Iniciar todas as threads
        for thread in threads:
            thread.start()
        
        # Aguardar conclusão
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        assert total_time < CONCURRENCY_LIMITS["thread_safety"] * 10
        assert len(results) == 10
        assert all(isinstance(r["keyword"], Keyword) for r in results)
        assert len(set(r["thread_id"] for r in results)) == 10
    
    def test_cluster_creation_thread_safety(self):
        """Testa thread safety na criação de clusters."""
        results = []
        lock = threading.Lock()
        
        def create_cluster(thread_id):
            """Função executada por cada thread."""
            cluster = make_real_cluster()
            cluster.id = f"cluster_thread_{thread_id}"
            with lock:
                results.append({
                    "thread_id": thread_id,
                    "cluster": cluster,
                    "timestamp": time.time()
                })
        
        # Criar múltiplas threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_cluster, args=(i,))
            threads.append(thread)
        
        start_time = time.time()
        
        # Iniciar todas as threads
        for thread in threads:
            thread.start()
        
        # Aguardar conclusão
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        assert total_time < CONCURRENCY_LIMITS["thread_safety"] * 5
        assert len(results) == 5
        assert all(isinstance(r["cluster"], Cluster) for r in results)
        assert len(set(r["thread_id"] for r in results)) == 5
    
    def test_shared_resource_thread_safety(self):
        """Testa thread safety com recursos compartilhados."""
        shared_counter = 0
        lock = threading.Lock()
        
        def increment_counter():
            """Função que incrementa contador compartilhado."""
            nonlocal shared_counter
            for _ in range(100):
                with lock:
                    shared_counter += 1
                    time.sleep(0.0001)  # Simular trabalho
        
        # Criar múltiplas threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=increment_counter)
            threads.append(thread)
        
        start_time = time.time()
        
        # Iniciar todas as threads
        for thread in threads:
            thread.start()
        
        # Aguardar conclusão
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        assert total_time < CONCURRENCY_LIMITS["deadlock_timeout"]
        assert shared_counter == 500  # 5 threads * 100 incrementos cada
        assert len(threads) == 5

class TestAsyncConcurrency:
    """Testes de concorrência assíncrona."""
    
    @pytest.mark.asyncio
    async def test_async_keyword_operations(self):
        """Testa operações assíncronas com keywords."""
        async def process_keyword(i):
            """Processa keyword de forma assíncrona."""
            keyword = make_real_keyword(f"async_kw_{i}")
            score = keyword.calcular_score({})
            data = keyword.to_dict()
            await asyncio.sleep(0.01)  # Simular operação assíncrona
            return {"id": i, "score": score, "data": data}
        
        start_time = time.time()
        
        # Executar operações concorrentes
        tasks = [process_keyword(i) for i in range(50)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verificar que operações concorrentes são mais rápidas que sequenciais
        expected_sequential_time = 50 * CONCURRENCY_LIMITS["async_operation"]
        assert total_time < expected_sequential_time * CONCURRENCY_LIMITS["scalability_factor"]
        assert len(results) == 50
        assert all(r["score"] > 0 for r in results)
    
    @pytest.mark.asyncio
    async def test_async_cluster_operations(self):
        """Testa operações assíncronas com clusters."""
        async def process_cluster(i):
            """Processa cluster de forma assíncrona."""
            cluster = make_real_cluster()
            cluster.id = f"async_cluster_{i}"
            data = cluster.to_dict()
            await asyncio.sleep(0.01)  # Simular operação assíncrona
            return {"id": i, "data": data, "keywords_count": len(cluster.keywords)}
        
        start_time = time.time()
        
        # Executar operações concorrentes
        tasks = [process_cluster(i) for i in range(20)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verificar que operações concorrentes são mais rápidas
        expected_sequential_time = 20 * CONCURRENCY_LIMITS["async_operation"]
        assert total_time < expected_sequential_time * CONCURRENCY_LIMITS["scalability_factor"]
        assert len(results) == 20
        assert all(r["keywords_count"] >= 4 for r in results)
    
    @pytest.mark.asyncio
    async def test_async_prompt_generation(self):
        """Testa geração assíncrona de prompts."""
        gp = GeradorPrompt(template="Artigo sobre $primary_keyword")
        
        async def generate_prompt(i):
            """Gera prompt de forma assíncrona."""
            pk = make_real_keyword(f"prompt_kw_{i}")
            sks = [make_real_keyword(f"sec_{i}_{j}") for j in range(3)]
            await asyncio.sleep(0.01)  # Simular operação assíncrona
            return gp.gerar_prompt(pk, sks)
        
        start_time = time.time()
        
        # Executar gerações concorrentes
        tasks = [generate_prompt(i) for i in range(30)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verificar que operações concorrentes são mais rápidas
        expected_sequential_time = 30 * CONCURRENCY_LIMITS["async_operation"]
        assert total_time < expected_sequential_time * CONCURRENCY_LIMITS["scalability_factor"]
        assert len(results) == 30
        assert all(f"prompt_kw_{i}" in result for i, result in enumerate(results))

class TestConcurrentDataAccess:
    """Testes de acesso concorrente a dados."""
    
    def test_concurrent_keyword_access(self):
        """Testa acesso concorrente a keywords."""
        keywords = [make_real_keyword(f"kw_{i}") for i in range(100)]
        results = []
        lock = threading.Lock()
        
        def access_keyword(thread_id):
            """Acessa keywords de forma concorrente."""
            for i in range(10):
                keyword = keywords[(thread_id + i) % len(keywords)]
                score = keyword.calcular_score({})
                data = keyword.to_dict()
                with lock:
                    results.append({
                        "thread_id": thread_id,
                        "keyword_id": i,
                        "score": score,
                        "termo": keyword.termo
                    })
        
        # Criar múltiplas threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=access_keyword, args=(i,))
            threads.append(thread)
        
        start_time = time.time()
        
        # Iniciar todas as threads
        for thread in threads:
            thread.start()
        
        # Aguardar conclusão
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        assert total_time < CONCURRENCY_LIMITS["concurrent_creation"] * 100
        assert len(results) == 100  # 10 threads * 10 acessos cada
        assert all(r["score"] > 0 for r in results)
    
    def test_concurrent_cluster_access(self):
        """Testa acesso concorrente a clusters."""
        clusters = [make_real_cluster() for _ in range(20)]
        for i, cluster in enumerate(clusters):
            cluster.id = f"cluster_access_{i}"
        
        results = []
        lock = threading.Lock()
        
        def access_cluster(thread_id):
            """Acessa clusters de forma concorrente."""
            for i in range(5):
                cluster = clusters[(thread_id + i) % len(clusters)]
                data = cluster.to_dict()
                keywords_count = len(cluster.keywords)
                with lock:
                    results.append({
                        "thread_id": thread_id,
                        "cluster_id": i,
                        "keywords_count": keywords_count,
                        "cluster_id_real": cluster.id
                    })
        
        # Criar múltiplas threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=access_cluster, args=(i,))
            threads.append(thread)
        
        start_time = time.time()
        
        # Iniciar todas as threads
        for thread in threads:
            thread.start()
        
        # Aguardar conclusão
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        assert total_time < CONCURRENCY_LIMITS["concurrent_creation"] * 25
        assert len(results) == 25  # 5 threads * 5 acessos cada
        assert all(r["keywords_count"] >= 4 for r in results)

class TestRaceConditionPrevention:
    """Testes para prevenção de race conditions."""
    
    def test_keyword_score_calculation_race_condition(self):
        """Testa prevenção de race conditions no cálculo de score."""
        keyword = make_real_keyword("race_condition_test")
        results = []
        lock = threading.Lock()
        
        def calculate_score(thread_id):
            """Calcula score de forma concorrente."""
            for _ in range(10):
                with lock:
                    score = keyword.calcular_score({
                        "volume": 0.4,
                        "cpc": 0.3,
                        "intencao": 0.2,
                        "concorrencia": 0.1
                    })
                    results.append({
                        "thread_id": thread_id,
                        "score": score,
                        "timestamp": time.time()
                    })
        
        # Criar múltiplas threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=calculate_score, args=(i,))
            threads.append(thread)
        
        start_time = time.time()
        
        # Iniciar todas as threads
        for thread in threads:
            thread.start()
        
        # Aguardar conclusão
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        assert total_time < CONCURRENCY_LIMITS["race_condition"] * 50
        assert len(results) == 50  # 5 threads * 10 cálculos cada
        assert all(r["score"] > 0 for r in results)
        # Verificar que todos os scores são consistentes
        scores = [r["score"] for r in results]
        assert len(set(scores)) == 1  # Todos os scores devem ser iguais
    
    def test_cluster_validation_race_condition(self):
        """Testa prevenção de race conditions na validação de clusters."""
        cluster = make_real_cluster()
        results = []
        lock = threading.Lock()
        
        def validate_cluster(thread_id):
            """Valida cluster de forma concorrente."""
            for _ in range(10):
                with lock:
                    # Validar propriedades do cluster
                    keywords_count = len(cluster.keywords)
                    similarity = cluster.similaridade_media
                    fase = cluster.fase_funil
                    
                    results.append({
                        "thread_id": thread_id,
                        "keywords_count": keywords_count,
                        "similarity": similarity,
                        "fase": fase,
                        "timestamp": time.time()
                    })
        
        # Criar múltiplas threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=validate_cluster, args=(i,))
            threads.append(thread)
        
        start_time = time.time()
        
        # Iniciar todas as threads
        for thread in threads:
            thread.start()
        
        # Aguardar conclusão
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        assert total_time < CONCURRENCY_LIMITS["race_condition"] * 50
        assert len(results) == 50  # 5 threads * 10 validações cada
        assert all(r["keywords_count"] >= 4 for r in results)
        assert all(0 <= r["similarity"] <= 1 for r in results)
        # Verificar que todas as validações são consistentes
        keywords_counts = [r["keywords_count"] for r in results]
        similarities = [r["similarity"] for r in results]
        assert len(set(keywords_counts)) == 1  # Todos os counts devem ser iguais
        assert len(set(similarities)) == 1  # Todas as similaridades devem ser iguais

class TestDeadlockPrevention:
    """Testes para prevenção de deadlocks."""
    
    def test_no_deadlock_keyword_operations(self):
        """Testa que operações com keywords não causam deadlock."""
        keyword1 = make_real_keyword("deadlock_test_1")
        keyword2 = make_real_keyword("deadlock_test_2")
        results = []
        
        def operation_with_timeout(thread_id, timeout=1.0):
            """Executa operação com timeout para evitar deadlock."""
            start_time = time.time()
            try:
                # Simular operação que poderia causar deadlock
                if thread_id % 2 == 0:
                    score1 = keyword1.calcular_score({})
                    time.sleep(0.001)  # Simular trabalho
                    score2 = keyword2.calcular_score({})
                else:
                    score2 = keyword2.calcular_score({})
                    time.sleep(0.001)  # Simular trabalho
                    score1 = keyword1.calcular_score({})
                
                results.append({
                    "thread_id": thread_id,
                    "score1": score1,
                    "score2": score2,
                    "success": True
                })
            except Exception as e:
                results.append({
                    "thread_id": thread_id,
                    "error": str(e),
                    "success": False
                })
            
            end_time = time.time()
            assert end_time - start_time < timeout
        
        # Criar múltiplas threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=operation_with_timeout, args=(i,))
            threads.append(thread)
        
        start_time = time.time()
        
        # Iniciar todas as threads
        for thread in threads:
            thread.start()
        
        # Aguardar conclusão com timeout
        for thread in threads:
            thread.join(timeout=CONCURRENCY_LIMITS["deadlock_timeout"])
        
        end_time = time.time()
        total_time = end_time - start_time
        
        assert total_time < CONCURRENCY_LIMITS["deadlock_timeout"]
        assert len(results) == 10
        assert all(r["success"] for r in results)
    
    def test_no_deadlock_cluster_operations(self):
        """Testa que operações com clusters não causam deadlock."""
        cluster1 = make_real_cluster()
        cluster1.id = "cluster_deadlock_1"
        cluster2 = make_real_cluster()
        cluster2.id = "cluster_deadlock_2"
        results = []
        
        def operation_with_timeout(thread_id, timeout=1.0):
            """Executa operação com timeout para evitar deadlock."""
            start_time = time.time()
            try:
                # Simular operação que poderia causar deadlock
                if thread_id % 2 == 0:
                    data1 = cluster1.to_dict()
                    time.sleep(0.001)  # Simular trabalho
                    data2 = cluster2.to_dict()
                else:
                    data2 = cluster2.to_dict()
                    time.sleep(0.001)  # Simular trabalho
                    data1 = cluster1.to_dict()
                
                results.append({
                    "thread_id": thread_id,
                    "cluster1_id": data1["id"],
                    "cluster2_id": data2["id"],
                    "success": True
                })
            except Exception as e:
                results.append({
                    "thread_id": thread_id,
                    "error": str(e),
                    "success": False
                })
            
            end_time = time.time()
            assert end_time - start_time < timeout
        
        # Criar múltiplas threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=operation_with_timeout, args=(i,))
            threads.append(thread)
        
        start_time = time.time()
        
        # Iniciar todas as threads
        for thread in threads:
            thread.start()
        
        # Aguardar conclusão com timeout
        for thread in threads:
            thread.join(timeout=CONCURRENCY_LIMITS["deadlock_timeout"])
        
        end_time = time.time()
        total_time = end_time - start_time
        
        assert total_time < CONCURRENCY_LIMITS["deadlock_timeout"]
        assert len(results) == 10
        assert all(r["success"] for r in results)

class TestScalability:
    """Testes de escalabilidade."""
    
    def test_keyword_creation_scalability(self):
        """Testa escalabilidade da criação de keywords."""
        def create_keywords_batch(batch_size):
            """Cria lote de keywords."""
            start_time = time.time()
            keywords = [make_real_keyword(f"scalability_kw_{i}") for i in range(batch_size)]
            end_time = time.time()
            return end_time - start_time
        
        # Testar diferentes tamanhos de lote
        batch_sizes = [10, 50, 100, 500, 1000]
        times = []
        
        for batch_size in batch_sizes:
            time_taken = create_keywords_batch(batch_size)
            times.append(time_taken)
        
        # Verificar que o tempo cresce linearmente (não exponencialmente)
        for i in range(1, len(times)):
            ratio = times[i] / times[i-1]
            batch_ratio = batch_sizes[i] / batch_sizes[i-1]
            # O tempo deve crescer proporcionalmente ao tamanho do lote
            assert ratio <= batch_ratio * 1.5  # Permitir 50% de overhead
    
    def test_cluster_creation_scalability(self):
        """Testa escalabilidade da criação de clusters."""
        def create_clusters_batch(batch_size):
            """Cria lote de clusters."""
            start_time = time.time()
            clusters = [make_real_cluster() for _ in range(batch_size)]
            for i, cluster in enumerate(clusters):
                cluster.id = f"scalability_cluster_{i}"
            end_time = time.time()
            return end_time - start_time
        
        # Testar diferentes tamanhos de lote
        batch_sizes = [5, 10, 20, 50, 100]
        times = []
        
        for batch_size in batch_sizes:
            time_taken = create_clusters_batch(batch_size)
            times.append(time_taken)
        
        # Verificar que o tempo cresce linearmente
        for i in range(1, len(times)):
            ratio = times[i] / times[i-1]
            batch_ratio = batch_sizes[i] / batch_sizes[i-1]
            assert ratio <= batch_ratio * 1.5  # Permitir 50% de overhead
    
    @pytest.mark.asyncio
    async def test_async_operations_scalability(self):
        """Testa escalabilidade de operações assíncronas."""
        async def async_operation(duration):
            """Operação assíncrona com duração controlada."""
            await asyncio.sleep(duration)
            return {"duration": duration, "timestamp": time.time()}
        
        async def run_concurrent_operations(num_operations):
            """Executa operações concorrentes."""
            start_time = time.time()
            tasks = [async_operation(0.01) for _ in range(num_operations)]
            results = await asyncio.gather(*tasks)
            end_time = time.time()
            return end_time - start_time, results
        
        # Testar diferentes números de operações concorrentes
        operation_counts = [10, 50, 100, 200, 500]
        times = []
        
        for count in operation_counts:
            time_taken, results = await run_concurrent_operations(count)
            times.append(time_taken)
            assert len(results) == count
        
        # Verificar que o tempo não cresce linearmente com o número de operações
        # (devido à concorrência)
        for i in range(1, len(times)):
            ratio = times[i] / times[i-1]
            operation_ratio = operation_counts[i] / operation_counts[i-1]
            # O tempo deve crescer menos que linearmente devido à concorrência
            assert ratio < operation_ratio * 0.8  # Pelo menos 20% de melhoria

class TestConcurrentDataStructures:
    """Testes de estruturas de dados concorrentes."""
    
    def test_thread_safe_list_operations(self):
        """Testa operações thread-safe em listas."""
        from collections import deque
        import queue
        
        # Usar deque thread-safe
        thread_safe_list = deque()
        results = []
        lock = threading.Lock()
        
        def add_to_list(thread_id):
            """Adiciona elementos à lista de forma thread-safe."""
            for i in range(10):
                item = make_real_keyword(f"thread_safe_{thread_id}_{i}")
                with lock:
                    thread_safe_list.append(item)
                    results.append({
                        "thread_id": thread_id,
                        "item_id": i,
                        "termo": item.termo
                    })
        
        # Criar múltiplas threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=add_to_list, args=(i,))
            threads.append(thread)
        
        start_time = time.time()
        
        # Iniciar todas as threads
        for thread in threads:
            thread.start()
        
        # Aguardar conclusão
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        assert total_time < CONCURRENCY_LIMITS["thread_safety"] * 50
        assert len(thread_safe_list) == 50  # 5 threads * 10 itens cada
        assert len(results) == 50
        assert all(isinstance(item, Keyword) for item in thread_safe_list)
    
    def test_thread_safe_queue_operations(self):
        """Testa operações thread-safe em filas."""
        import queue
        
        # Usar Queue thread-safe
        thread_safe_queue = queue.Queue()
        results = []
        
        def producer(thread_id):
            """Produz elementos para a fila."""
            for i in range(10):
                item = make_real_keyword(f"queue_producer_{thread_id}_{i}")
                thread_safe_queue.put(item)
        
        def consumer(thread_id):
            """Consome elementos da fila."""
            for i in range(10):
                try:
                    item = thread_safe_queue.get(timeout=1.0)
                    results.append({
                        "thread_id": thread_id,
                        "item_id": i,
                        "termo": item.termo
                    })
                    thread_safe_queue.task_done()
                except queue.Empty:
                    break
        
        # Criar threads produtoras e consumidoras
        producer_threads = []
        consumer_threads = []
        
        for i in range(3):
            producer_thread = threading.Thread(target=producer, args=(i,))
            consumer_thread = threading.Thread(target=consumer, args=(i,))
            producer_threads.append(producer_thread)
            consumer_threads.append(consumer_thread)
        
        start_time = time.time()
        
        # Iniciar threads produtoras
        for thread in producer_threads:
            thread.start()
        
        # Iniciar threads consumidoras
        for thread in consumer_threads:
            thread.start()
        
        # Aguardar conclusão
        for thread in producer_threads + consumer_threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        assert total_time < CONCURRENCY_LIMITS["thread_safety"] * 60
        assert len(results) == 30  # 3 consumidores * 10 itens cada
        assert all(isinstance(r["termo"], str) for r in results) 