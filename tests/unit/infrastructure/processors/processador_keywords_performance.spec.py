"""
Testes de Performance para Processador Keywords
Tracing ID: PERFORMANCE_001_20250127
Data: 2025-01-27
Versão: 1.0
Status: ✅ IMPLEMENTADO

Testes de performance e otimização para o processador de keywords.
Cobre cenários de alta carga, benchmarks e métricas de performance.
"""

import pytest
import time
import threading
import asyncio
import psutil
import gc
from typing import List, Dict, Any
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from datetime import datetime

from domain.models import Keyword, IntencaoBusca
from infrastructure.processamento.processador_keywords import ProcessadorKeywords
from infrastructure.processamento.validador_keywords import ValidadorKeywords
from shared.logger import logger


class TestProcessadorKeywordsPerformance:
    """
    Testes de performance para ProcessadorKeywords.
    
    Cobre:
    - Performance com grandes volumes
    - Otimizações de memória
    - Concorrência e paralelismo
    - Benchmarks de operações
    - Métricas de throughput
    - Análise de gargalos
    """

    @pytest.fixture
    def processador_performance(self):
        """Processador configurado para testes de performance."""
        return ProcessadorKeywords(
            config={
                "batch_size": 1000,
                "max_workers": 4,
                "timeout": 30,
                "enable_cache": True,
                "cache_ttl": 3600,
                "enable_metrics": True
            }
        )

    @pytest.fixture
    def keywords_grande_volume(self):
        """Gera lista grande de keywords para testes."""
        keywords = []
        for i in range(10000):
            keyword = Keyword(
                termo=f"palavra chave teste {i}",
                volume_busca=100 + (i % 1000),
                cpc=1.0 + (i / 10000),
                concorrencia=0.1 + (i / 100000),
                intencao=IntencaoBusca.INFORMACIONAL,
                score=0.5 + (i / 20000),
                justificativa=f"Justificativa para keyword {i}",
                fonte="teste_performance",
                data_coleta=datetime.now()
            )
            keywords.append(keyword)
        return keywords

    @pytest.fixture
    def keywords_diversificadas(self):
        """Gera keywords com diferentes características."""
        keywords = []
        termos_base = [
            "python tutorial",
            "javascript guide",
            "machine learning",
            "web development",
            "data science",
            "artificial intelligence",
            "blockchain technology",
            "cloud computing",
            "cybersecurity",
            "mobile development"
        ]
        
        for i, termo_base in enumerate(termos_base):
            for j in range(100):  # 100 variações por termo base
                keyword = Keyword(
                    termo=f"{termo_base} {j}",
                    volume_busca=100 + (i * 10) + j,
                    cpc=1.0 + (i / 10) + (j / 100),
                    concorrencia=0.1 + (i / 100) + (j / 1000),
                    intencao=IntencaoBusca.INFORMACIONAL,
                    score=0.5 + (i / 20) + (j / 200),
                    justificativa=f"Justificativa para {termo_base} {j}",
                    fonte="teste_diversificado",
                    data_coleta=datetime.now()
                )
                keywords.append(keyword)
        return keywords

    # ==================== PERFORMANCE COM GRANDES VOLUMES ====================

    def test_performance_grande_volume(self, processador_performance, keywords_grande_volume):
        """Testa performance com grande volume de keywords."""
        # Medir uso de memória inicial
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Medir tempo de processamento
        start_time = time.time()
        
        resultado = processador_performance.processar_keywords(
            keywords_grande_volume,
            config={"batch_size": 1000, "max_workers": 4}
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Medir uso de memória final
        final_memory = process.memory_info().rss
        memory_usage = final_memory - initial_memory
        
        # Verificar performance
        assert processing_time < 30.0, f"Tempo de processamento muito alto: {processing_time:.2f}s"
        assert memory_usage < 500 * 1024 * 1024, f"Uso de memória muito alto: {memory_usage / 1024 / 1024:.2f}MB"
        
        # Verificar resultado
        assert len(resultado) == len(keywords_grande_volume)
        assert all(isinstance(kw, Keyword) for kw in resultado)
        
        # Calcular throughput
        throughput = len(keywords_grande_volume) / processing_time
        assert throughput > 100, f"Throughput muito baixo: {throughput:.2f} keywords/s"

    def test_performance_batch_processing(self, processador_performance, keywords_grande_volume):
        """Testa performance com diferentes tamanhos de batch."""
        batch_sizes = [100, 500, 1000, 2000, 5000]
        results = {}
        
        for batch_size in batch_sizes:
            start_time = time.time()
            
            resultado = processador_performance.processar_keywords(
                keywords_grande_volume[:1000],  # Usar apenas 1000 para teste
                config={"batch_size": batch_size, "max_workers": 4}
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            results[batch_size] = {
                "time": processing_time,
                "throughput": 1000 / processing_time,
                "memory": psutil.Process().memory_info().rss
            }
        
        # Verificar que batch_size maior não necessariamente é melhor
        assert results[1000]["throughput"] > results[100]["throughput"], "Batch maior deve ter melhor throughput"

    # ==================== OTIMIZAÇÕES DE MEMÓRIA ====================

    def test_memory_optimization(self, processador_performance, keywords_grande_volume):
        """Testa otimizações de memória."""
        import sys
        
        # Forçar garbage collection
        gc.collect()
        
        # Medir memória antes
        initial_memory = psutil.Process().memory_info().rss
        
        # Processar em lotes para testar liberação de memória
        batch_size = 1000
        total_processed = 0
        
        for i in range(0, len(keywords_grande_volume), batch_size):
            batch = keywords_grande_volume[i:i + batch_size]
            
            # Processar lote
            resultado = processador_performance.processar_keywords(batch)
            total_processed += len(resultado)
            
            # Forçar garbage collection após cada lote
            gc.collect()
            
            # Verificar que memória não cresce indefinidamente
            current_memory = psutil.Process().memory_info().rss
            memory_increase = current_memory - initial_memory
            
            # Aumento de memória deve ser controlado
            assert memory_increase < 100 * 1024 * 1024, f"Aumento de memória muito alto: {memory_increase / 1024 / 1024:.2f}MB"
        
        assert total_processed == len(keywords_grande_volume)

    def test_memory_leak_detection(self, processador_performance):
        """Testa detecção de vazamentos de memória."""
        import sys
        
        # Referências antes
        initial_refs = len(gc.get_objects())
        
        # Executar múltiplas operações
        for i in range(10):
            keywords = [
                Keyword(
                    termo=f"keyword_{i}_{j}",
                    volume_busca=100,
                    cpc=1.0,
                    concorrencia=0.5,
                    intencao=IntencaoBusca.INFORMACIONAL
                )
                for j in range(100)
            ]
            
            resultado = processador_performance.processar_keywords(keywords)
            
            # Forçar garbage collection
            gc.collect()
        
        # Referências depois
        final_refs = len(gc.get_objects())
        
        # Verificar que não houve vazamento significativo
        ref_increase = final_refs - initial_refs
        assert ref_increase < 1000, f"Aumento de referências muito alto: {ref_increase}"

    # ==================== CONCORRÊNCIA E PARALELISMO ====================

    def test_concurrent_processing(self, processador_performance, keywords_diversificadas):
        """Testa processamento concorrente."""
        def process_batch(batch):
            """Processa um lote de keywords."""
            return processador_performance.processar_keywords(batch)
        
        # Dividir keywords em lotes
        batch_size = 1000
        batches = [
            keywords_diversificadas[i:i + batch_size]
            for i in range(0, len(keywords_diversificadas), batch_size)
        ]
        
        # Processar em paralelo
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(process_batch, batch) for batch in batches]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        parallel_time = end_time - start_time
        
        # Processar sequencialmente para comparação
        start_time = time.time()
        sequential_results = []
        for batch in batches:
            sequential_results.append(processador_performance.processar_keywords(batch))
        end_time = time.time()
        sequential_time = end_time - start_time
        
        # Verificar que processamento paralelo é mais rápido
        assert parallel_time < sequential_time, f"Paralelo não foi mais rápido: {parallel_time:.2f}s vs {sequential_time:.2f}s"
        
        # Verificar resultados
        total_parallel = sum(len(result) for result in results)
        total_sequential = sum(len(result) for result in sequential_results)
        assert total_parallel == total_sequential

    def test_thread_safety(self, processador_performance):
        """Testa thread safety do processador."""
        results = []
        errors = []
        
        def worker(worker_id):
            """Worker para teste de thread safety."""
            try:
                keywords = [
                    Keyword(
                        termo=f"worker_{worker_id}_keyword_{i}",
                        volume_busca=100 + i,
                        cpc=1.0 + (i / 100),
                        concorrencia=0.1 + (i / 1000),
                        intencao=IntencaoBusca.INFORMACIONAL
                    )
                    for i in range(100)
                ]
                
                resultado = processador_performance.processar_keywords(keywords)
                results.append(len(resultado))
                
            except Exception as e:
                errors.append(e)
        
        # Criar múltiplas threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Aguardar conclusão
        for thread in threads:
            thread.join()
        
        # Verificar que não houve erros
        assert len(errors) == 0, f"Erros encontrados: {errors}"
        
        # Verificar que todas as threads processaram corretamente
        assert len(results) == 10
        assert all(result == 100 for result in results)

    # ==================== BENCHMARKS DE OPERAÇÕES ====================

    def test_benchmark_operations(self, processador_performance):
        """Executa benchmarks de operações básicas."""
        keywords = [
            Keyword(
                termo=f"benchmark_keyword_{i}",
                volume_busca=100,
                cpc=1.0,
                concorrencia=0.5,
                intencao=IntencaoBusca.INFORMACIONAL
            )
            for i in range(1000)
        ]
        
        # Benchmark de inicialização
        start_time = time.time()
        processador = ProcessadorKeywords()
        init_time = time.time() - start_time
        assert init_time < 1.0, f"Tempo de inicialização muito alto: {init_time:.3f}s"
        
        # Benchmark de processamento
        start_time = time.time()
        resultado = processador.processar_keywords(keywords)
        process_time = time.time() - start_time
        
        # Benchmark de validação
        validador = ValidadorKeywords()
        start_time = time.time()
        for keyword in keywords[:100]:  # Validar apenas 100 para benchmark
            validador.validar_keyword(keyword)
        validation_time = time.time() - start_time
        
        # Verificar performance
        assert process_time < 10.0, f"Tempo de processamento muito alto: {process_time:.2f}s"
        assert validation_time < 1.0, f"Tempo de validação muito alto: {validation_time:.3f}s"
        
        # Calcular métricas
        process_throughput = len(keywords) / process_time
        validation_throughput = 100 / validation_time
        
        assert process_throughput > 50, f"Throughput de processamento baixo: {process_throughput:.2f} keywords/s"
        assert validation_throughput > 50, f"Throughput de validação baixo: {validation_throughput:.2f} keywords/s"

    def test_benchmark_memory_operations(self, processador_performance):
        """Benchmark de operações de memória."""
        import sys
        
        # Medir criação de objetos
        start_time = time.time()
        keywords = []
        for i in range(10000):
            keyword = Keyword(
                termo=f"memory_keyword_{i}",
                volume_busca=100,
                cpc=1.0,
                concorrencia=0.5,
                intencao=IntencaoBusca.INFORMACIONAL
            )
            keywords.append(keyword)
        creation_time = time.time() - start_time
        
        # Medir processamento
        start_time = time.time()
        resultado = processador_performance.processar_keywords(keywords)
        process_time = time.time() - start_time
        
        # Medir limpeza
        start_time = time.time()
        del keywords
        del resultado
        gc.collect()
        cleanup_time = time.time() - start_time
        
        # Verificar performance
        assert creation_time < 5.0, f"Tempo de criação muito alto: {creation_time:.2f}s"
        assert process_time < 30.0, f"Tempo de processamento muito alto: {process_time:.2f}s"
        assert cleanup_time < 2.0, f"Tempo de limpeza muito alto: {cleanup_time:.2f}s"

    # ==================== MÉTRICAS DE THROUGHPUT ====================

    def test_throughput_metrics(self, processador_performance, keywords_diversificadas):
        """Testa métricas de throughput."""
        # Testar diferentes tamanhos de entrada
        input_sizes = [100, 500, 1000, 2000, 5000]
        throughput_results = {}
        
        for size in input_sizes:
            keywords_subset = keywords_diversificadas[:size]
            
            start_time = time.time()
            resultado = processador_performance.processar_keywords(keywords_subset)
            end_time = time.time()
            
            processing_time = end_time - start_time
            throughput = size / processing_time
            
            throughput_results[size] = {
                "time": processing_time,
                "throughput": throughput,
                "memory": psutil.Process().memory_info().rss
            }
        
        # Verificar que throughput aumenta com tamanho (economia de escala)
        assert throughput_results[1000]["throughput"] > throughput_results[100]["throughput"]
        assert throughput_results[5000]["throughput"] > throughput_results[1000]["throughput"]
        
        # Verificar que tempo é proporcional
        assert throughput_results[5000]["time"] < throughput_results[100]["time"] * 50

    def test_throughput_under_load(self, processador_performance):
        """Testa throughput sob carga."""
        # Simular carga de CPU
        def cpu_load():
            """Função que consome CPU."""
            for _ in range(1000000):
                _ = 1 + 1
        
        # Executar carga em background
        load_thread = threading.Thread(target=cpu_load)
        load_thread.start()
        
        try:
            # Testar processamento sob carga
            keywords = [
                Keyword(
                    termo=f"load_keyword_{i}",
                    volume_busca=100,
                    cpc=1.0,
                    concorrencia=0.5,
                    intencao=IntencaoBusca.INFORMACIONAL
                )
                for i in range(1000)
            ]
            
            start_time = time.time()
            resultado = processador_performance.processar_keywords(keywords)
            end_time = time.time()
            
            processing_time = end_time - start_time
            throughput = len(keywords) / processing_time
            
            # Deve manter performance razoável mesmo sob carga
            assert processing_time < 20.0, f"Tempo muito alto sob carga: {processing_time:.2f}s"
            assert throughput > 30, f"Throughput muito baixo sob carga: {throughput:.2f} keywords/s"
            
        finally:
            # Parar thread de carga
            load_thread.join(timeout=1)

    # ==================== ANÁLISE DE GARGALOS ====================

    def test_bottleneck_analysis(self, processador_performance, keywords_grande_volume):
        """Analisa gargalos no processamento."""
        import cProfile
        import pstats
        import io
        
        # Profiling do processamento
        pr = cProfile.Profile()
        pr.enable()
        
        resultado = processador_performance.processar_keywords(keywords_grande_volume[:1000])
        
        pr.disable()
        
        # Analisar resultados do profiling
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats(10)  # Top 10 funções
        
        profile_output = s.getvalue()
        
        # Verificar que não há gargalos óbvios
        assert "processar_keywords" in profile_output
        assert "validar_keyword" in profile_output
        
        # Verificar que tempo total é razoável
        total_time = sum(stat[3] for stat in ps.stats.values())
        assert total_time < 10.0, f"Tempo total de profiling muito alto: {total_time:.2f}s"

    def test_memory_bottleneck_analysis(self, processador_performance):
        """Analisa gargalos de memória."""
        import tracemalloc
        
        # Iniciar tracking de memória
        tracemalloc.start()
        
        # Processar keywords
        keywords = [
            Keyword(
                termo=f"memory_keyword_{i}",
                volume_busca=100,
                cpc=1.0,
                concorrencia=0.5,
                intencao=IntencaoBusca.INFORMACIONAL
            )
            for i in range(5000)
        ]
        
        snapshot1 = tracemalloc.take_snapshot()
        
        resultado = processador_performance.processar_keywords(keywords)
        
        snapshot2 = tracemalloc.take_snapshot()
        
        # Comparar snapshots
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        
        # Verificar que não há vazamentos significativos
        total_increase = sum(stat.size_diff for stat in top_stats if stat.size_diff > 0)
        assert total_increase < 10 * 1024 * 1024, f"Aumento de memória muito alto: {total_increase / 1024 / 1024:.2f}MB"
        
        tracemalloc.stop()

    # ==================== TESTES DE STRESS ====================

    def test_stress_test_continuous_processing(self, processador_performance):
        """Teste de stress com processamento contínuo."""
        start_time = time.time()
        total_processed = 0
        
        # Processar continuamente por 30 segundos
        while time.time() - start_time < 30:
            keywords = [
                Keyword(
                    termo=f"stress_keyword_{total_processed + i}",
                    volume_busca=100,
                    cpc=1.0,
                    concorrencia=0.5,
                    intencao=IntencaoBusca.INFORMACIONAL
                )
                for i in range(100)
            ]
            
            resultado = processador_performance.processar_keywords(keywords)
            total_processed += len(resultado)
        
        # Calcular throughput médio
        total_time = time.time() - start_time
        avg_throughput = total_processed / total_time
        
        # Verificar performance sustentada
        assert avg_throughput > 50, f"Throughput médio muito baixo: {avg_throughput:.2f} keywords/s"
        assert total_processed > 1000, f"Poucas keywords processadas: {total_processed}"

    def test_stress_test_memory_pressure(self, processador_performance):
        """Teste de stress com pressão de memória."""
        import random
        
        # Criar pressão de memória
        memory_pressure = []
        for i in range(1000):
            memory_pressure.append([random.random() for _ in range(1000)])
        
        try:
            # Processar keywords sob pressão de memória
            keywords = [
                Keyword(
                    termo=f"pressure_keyword_{i}",
                    volume_busca=100,
                    cpc=1.0,
                    concorrencia=0.5,
                    intencao=IntencaoBusca.INFORMACIONAL
                )
                for i in range(1000)
            ]
            
            start_time = time.time()
            resultado = processador_performance.processar_keywords(keywords)
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            # Deve manter performance mesmo sob pressão
            assert processing_time < 20.0, f"Tempo muito alto sob pressão: {processing_time:.2f}s"
            assert len(resultado) == 1000
            
        finally:
            # Liberar pressão de memória
            del memory_pressure
            gc.collect()

    # ==================== TESTES DE CONFIGURAÇÃO DE PERFORMANCE ====================

    @pytest.mark.parametrize("config", [
        # Configuração otimizada para velocidade
        {
            "batch_size": 2000,
            "max_workers": 8,
            "timeout": 60,
            "enable_cache": True,
            "cache_ttl": 7200,
            "enable_metrics": False
        },
        # Configuração otimizada para memória
        {
            "batch_size": 100,
            "max_workers": 2,
            "timeout": 10,
            "enable_cache": False,
            "enable_metrics": False
        },
        # Configuração balanceada
        {
            "batch_size": 1000,
            "max_workers": 4,
            "timeout": 30,
            "enable_cache": True,
            "cache_ttl": 3600,
            "enable_metrics": True
        }
    ])
    def test_performance_configurations(self, config, keywords_diversificadas):
        """Testa diferentes configurações de performance."""
        processador = ProcessadorKeywords(config=config)
        
        # Medir performance
        start_time = time.time()
        resultado = processador.processar_keywords(keywords_diversificadas[:1000])
        end_time = time.time()
        
        processing_time = end_time - start_time
        throughput = 1000 / processing_time
        
        # Verificar que configuração otimizada para velocidade é mais rápida
        if config["batch_size"] == 2000 and config["max_workers"] == 8:
            assert throughput > 100, f"Configuração rápida não atingiu throughput esperado: {throughput:.2f}"
        elif config["batch_size"] == 100 and config["max_workers"] == 2:
            assert throughput > 20, f"Configuração de memória não atingiu throughput mínimo: {throughput:.2f}"
        else:
            assert throughput > 50, f"Configuração balanceada não atingiu throughput esperado: {throughput:.2f}"

    # ==================== TESTES DE MONITORAMENTO ====================

    def test_performance_monitoring(self, processador_performance, keywords_diversificadas):
        """Testa monitoramento de performance."""
        # Simular monitoramento
        metrics = {
            "start_time": time.time(),
            "keywords_processed": 0,
            "errors": 0,
            "memory_usage": []
        }
        
        def monitor_callback(keywords_processed, errors):
            """Callback de monitoramento."""
            metrics["keywords_processed"] = keywords_processed
            metrics["errors"] = errors
            metrics["memory_usage"].append(psutil.Process().memory_info().rss)
        
        # Processar com monitoramento
        resultado = processador_performance.processar_keywords(
            keywords_diversificadas[:1000],
            callback_progresso=monitor_callback
        )
        
        metrics["end_time"] = time.time()
        metrics["total_time"] = metrics["end_time"] - metrics["start_time"]
        
        # Verificar métricas
        assert metrics["keywords_processed"] == 1000
        assert metrics["errors"] == 0
        assert metrics["total_time"] > 0
        assert len(metrics["memory_usage"]) > 0
        
        # Verificar que uso de memória é razoável
        max_memory = max(metrics["memory_usage"])
        assert max_memory < 500 * 1024 * 1024, f"Uso máximo de memória muito alto: {max_memory / 1024 / 1024:.2f}MB"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 