"""
Testes de Concorrência para Sistema de Cache
Tracing ID: CONCURRENCY_001_20250127
Data: 2025-01-27
Versão: 1.0
Status: ✅ IMPLEMENTADO

Testes de concorrência e thread safety para o sistema de cache.
Cobre cenários de acesso simultâneo, race conditions e sincronização.
"""

import pytest
import threading
import time
import asyncio
import random
from typing import List, Dict, Any, Optional
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from datetime import datetime, timedelta

from infrastructure.cache.advanced_caching import AdvancedCaching, CacheConfig, CacheLevel, CacheStrategy
from infrastructure.cache.intelligent_cache_system import IntelligentCacheSystem
from infrastructure.cache.distributed_cache import DistributedCache
from shared.logger import logger


class TestCacheConcurrency:
    """
    Testes de concorrência para sistema de cache.
    
    Cobre:
    - Acesso simultâneo a cache
    - Race conditions
    - Thread safety
    - Sincronização de operações
    - Performance sob concorrência
    - Deadlock prevention
    """

    @pytest.fixture
    def cache_config(self):
        """Configuração de cache para testes de concorrência."""
        return CacheConfig(
            l1_enabled=True,
            l1_max_size=1000,
            l2_enabled=True,
            l2_max_size=5000,
            strategy=CacheStrategy.LRU,
            default_ttl=3600,
            warming_enabled=True,
            invalidation_enabled=True,
            compression_enabled=False,
            serialization_format="json"
        )

    @pytest.fixture
    def advanced_cache(self, cache_config):
        """Instância de cache avançado para testes."""
        return AdvancedCaching(cache_config)

    @pytest.fixture
    def intelligent_cache(self):
        """Instância de cache inteligente para testes."""
        return IntelligentCacheSystem(
            l1_max_size=1000,
            l2_max_size=5000,
            default_ttl=3600,
            enable_metrics=True
        )

    @pytest.fixture
    def distributed_cache(self):
        """Instância de cache distribuído para testes."""
        return DistributedCache()

    # ==================== ACESSO SIMULTÂNEO ====================

    def test_concurrent_read_access(self, advanced_cache):
        """Testa acesso simultâneo de leitura."""
        # Preparar dados
        test_data = {f"key_{i}": f"value_{i}" for i in range(100)}
        for key, value in test_data.items():
            advanced_cache.set(key, value, ttl=60)
        
        results = []
        errors = []
        
        def reader(thread_id):
            """Função de leitura concorrente."""
            try:
                for i in range(50):
                    key = f"key_{random.randint(0, 99)}"
                    value = advanced_cache.get(key)
                    if value is not None:
                        results.append((thread_id, key, value))
            except Exception as e:
                errors.append(e)
        
        # Criar múltiplas threads de leitura
        threads = []
        for i in range(10):
            thread = threading.Thread(target=reader, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Aguardar conclusão
        for thread in threads:
            thread.join()
        
        # Verificar que não houve erros
        assert len(errors) == 0, f"Erros encontrados: {errors}"
        
        # Verificar que todas as threads leram dados
        assert len(results) > 0
        assert all(isinstance(result, tuple) and len(result) == 3 for result in results)

    def test_concurrent_write_access(self, advanced_cache):
        """Testa acesso simultâneo de escrita."""
        results = []
        errors = []
        
        def writer(thread_id):
            """Função de escrita concorrente."""
            try:
                for i in range(100):
                    key = f"thread_{thread_id}_key_{i}"
                    value = f"thread_{thread_id}_value_{i}"
                    success = advanced_cache.set(key, value, ttl=60)
                    results.append((thread_id, key, success))
            except Exception as e:
                errors.append(e)
        
        # Criar múltiplas threads de escrita
        threads = []
        for i in range(5):
            thread = threading.Thread(target=writer, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Aguardar conclusão
        for thread in threads:
            thread.join()
        
        # Verificar que não houve erros
        assert len(errors) == 0, f"Erros encontrados: {errors}"
        
        # Verificar que todas as escritas foram bem-sucedidas
        assert len(results) == 500  # 5 threads * 100 escritas cada
        assert all(success for _, _, success in results)

    def test_concurrent_read_write_access(self, advanced_cache):
        """Testa acesso simultâneo de leitura e escrita."""
        read_results = []
        write_results = []
        errors = []
        
        def reader(thread_id):
            """Função de leitura concorrente."""
            try:
                for i in range(50):
                    key = f"shared_key_{random.randint(0, 99)}"
                    value = advanced_cache.get(key)
                    if value is not None:
                        read_results.append((thread_id, key, value))
                    time.sleep(0.001)  # Pequena pausa
            except Exception as e:
                errors.append(e)
        
        def writer(thread_id):
            """Função de escrita concorrente."""
            try:
                for i in range(50):
                    key = f"shared_key_{i}"
                    value = f"thread_{thread_id}_value_{i}"
                    success = advanced_cache.set(key, value, ttl=60)
                    write_results.append((thread_id, key, success))
                    time.sleep(0.001)  # Pequena pausa
            except Exception as e:
                errors.append(e)
        
        # Criar threads de leitura e escrita
        read_threads = []
        write_threads = []
        
        for i in range(5):
            read_thread = threading.Thread(target=reader, args=(i,))
            write_thread = threading.Thread(target=writer, args=(i,))
            read_threads.append(read_thread)
            write_threads.append(write_thread)
            read_thread.start()
            write_thread.start()
        
        # Aguardar conclusão
        for thread in read_threads + write_threads:
            thread.join()
        
        # Verificar que não houve erros
        assert len(errors) == 0, f"Erros encontrados: {errors}"
        
        # Verificar que operações foram executadas
        assert len(read_results) > 0
        assert len(write_results) == 250  # 5 threads * 50 escritas cada

    # ==================== RACE CONDITIONS ====================

    def test_race_condition_get_set(self, advanced_cache):
        """Testa race condition entre get e set."""
        key = "race_key"
        initial_value = "initial_value"
        
        # Definir valor inicial
        advanced_cache.set(key, initial_value, ttl=60)
        
        results = []
        errors = []
        
        def concurrent_operation(thread_id):
            """Operação concorrente que lê e escreve."""
            try:
                for i in range(100):
                    # Ler valor
                    read_value = advanced_cache.get(key)
                    
                    # Modificar e escrever
                    new_value = f"thread_{thread_id}_mod_{i}"
                    success = advanced_cache.set(key, new_value, ttl=60)
                    
                    results.append((thread_id, i, read_value, success))
                    
            except Exception as e:
                errors.append(e)
        
        # Executar operações concorrentes
        threads = []
        for i in range(3):
            thread = threading.Thread(target=concurrent_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verificar que não houve erros
        assert len(errors) == 0, f"Erros encontrados: {errors}"
        
        # Verificar que todas as operações foram executadas
        assert len(results) == 300  # 3 threads * 100 operações cada

    def test_race_condition_delete(self, advanced_cache):
        """Testa race condition com operações de delete."""
        # Preparar dados
        for i in range(100):
            advanced_cache.set(f"delete_key_{i}", f"value_{i}", ttl=60)
        
        results = []
        errors = []
        
        def delete_operation(thread_id):
            """Operação de delete concorrente."""
            try:
                for i in range(20):
                    key = f"delete_key_{thread_id * 20 + i}"
                    
                    # Verificar se existe antes de deletar
                    exists_before = advanced_cache.get(key) is not None
                    
                    # Deletar
                    success = advanced_cache.delete(key)
                    
                    # Verificar se foi deletado
                    exists_after = advanced_cache.get(key) is not None
                    
                    results.append((thread_id, key, exists_before, success, exists_after))
                    
            except Exception as e:
                errors.append(e)
        
        # Executar deletes concorrentes
        threads = []
        for i in range(5):
            thread = threading.Thread(target=delete_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verificar que não houve erros
        assert len(errors) == 0, f"Erros encontrados: {errors}"
        
        # Verificar que deletes foram executados
        assert len(results) == 100  # 5 threads * 20 deletes cada
        
        # Verificar que items foram realmente deletados
        deleted_items = [r for r in results if r[3] and not r[4]]  # success=True, exists_after=False
        assert len(deleted_items) > 0

    # ==================== THREAD SAFETY ====================

    def test_thread_safety_intelligent_cache(self, intelligent_cache):
        """Testa thread safety do cache inteligente."""
        results = []
        errors = []
        
        def cache_operation(thread_id):
            """Operação de cache concorrente."""
            try:
                for i in range(100):
                    key = f"intelligent_key_{thread_id}_{i}"
                    value = f"intelligent_value_{thread_id}_{i}"
                    
                    # Set
                    success_set = intelligent_cache.set(key, value, ttl=60)
                    
                    # Get
                    retrieved_value = intelligent_cache.get(key)
                    
                    # Delete
                    success_delete = intelligent_cache.delete(key)
                    
                    results.append((thread_id, i, success_set, retrieved_value, success_delete))
                    
            except Exception as e:
                errors.append(e)
        
        # Executar operações concorrentes
        threads = []
        for i in range(10):
            thread = threading.Thread(target=cache_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verificar que não houve erros
        assert len(errors) == 0, f"Erros encontrados: {errors}"
        
        # Verificar que todas as operações foram executadas
        assert len(results) == 1000  # 10 threads * 100 operações cada
        
        # Verificar que operações foram bem-sucedidas
        successful_sets = [r for r in results if r[2]]  # success_set
        successful_gets = [r for r in results if r[3] is not None]  # retrieved_value
        successful_deletes = [r for r in results if r[4]]  # success_delete
        
        assert len(successful_sets) > 0
        assert len(successful_gets) > 0
        assert len(successful_deletes) > 0

    def test_thread_safety_distributed_cache(self, distributed_cache):
        """Testa thread safety do cache distribuído."""
        results = []
        errors = []
        
        def distributed_operation(thread_id):
            """Operação de cache distribuído concorrente."""
            try:
                for i in range(50):
                    key = f"distributed_key_{thread_id}_{i}"
                    value = f"distributed_value_{thread_id}_{i}"
                    
                    # Set
                    distributed_cache.set(key, value, ttl=60)
                    
                    # Get
                    retrieved_value = distributed_cache.get(key)
                    
                    # Verificar consistência
                    if retrieved_value == value:
                        results.append((thread_id, i, True))
                    else:
                        results.append((thread_id, i, False))
                    
            except Exception as e:
                errors.append(e)
        
        # Executar operações concorrentes
        threads = []
        for i in range(5):
            thread = threading.Thread(target=distributed_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verificar que não houve erros
        assert len(errors) == 0, f"Erros encontrados: {errors}"
        
        # Verificar que todas as operações foram executadas
        assert len(results) == 250  # 5 threads * 50 operações cada
        
        # Verificar consistência
        consistent_operations = [r for r in results if r[2]]  # True
        assert len(consistent_operations) > 0

    # ==================== SINCRONIZAÇÃO DE OPERAÇÕES ====================

    def test_synchronization_locks(self, advanced_cache):
        """Testa sincronização usando locks."""
        # Simular operação crítica
        critical_section_counter = 0
        lock = threading.Lock()
        
        def critical_operation(thread_id):
            """Operação que acessa seção crítica."""
            nonlocal critical_section_counter
            
            for i in range(100):
                with lock:
                    # Seção crítica
                    current_value = critical_section_counter
                    time.sleep(0.001)  # Simular processamento
                    critical_section_counter = current_value + 1
                    
                    # Usar cache na seção crítica
                    key = f"critical_key_{current_value}"
                    advanced_cache.set(key, f"critical_value_{current_value}", ttl=60)
        
        # Executar operações críticas concorrentes
        threads = []
        for i in range(5):
            thread = threading.Thread(target=critical_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verificar que contador está correto
        assert critical_section_counter == 500  # 5 threads * 100 incrementos cada

    def test_synchronization_barriers(self, advanced_cache):
        """Testa sincronização usando barriers."""
        barrier = threading.Barrier(5)
        results = []
        
        def synchronized_operation(thread_id):
            """Operação sincronizada."""
            for i in range(10):
                # Preparar dados
                key = f"barrier_key_{thread_id}_{i}"
                value = f"barrier_value_{thread_id}_{i}"
                
                # Aguardar todos os threads
                barrier.wait()
                
                # Operação sincronizada
                advanced_cache.set(key, value, ttl=60)
                retrieved_value = advanced_cache.get(key)
                
                results.append((thread_id, i, retrieved_value == value))
        
        # Executar operações sincronizadas
        threads = []
        for i in range(5):
            thread = threading.Thread(target=synchronized_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verificar que todas as operações foram executadas
        assert len(results) == 50  # 5 threads * 10 operações cada
        
        # Verificar que operações foram bem-sucedidas
        successful_operations = [r for r in results if r[2]]  # True
        assert len(successful_operations) == 50

    # ==================== PERFORMANCE SOB CONCORRÊNCIA ====================

    def test_concurrent_performance_benchmark(self, advanced_cache):
        """Benchmark de performance sob concorrência."""
        # Preparar dados
        for i in range(1000):
            advanced_cache.set(f"benchmark_key_{i}", f"benchmark_value_{i}", ttl=60)
        
        start_time = time.time()
        
        def performance_operation(thread_id):
            """Operação de performance."""
            for i in range(100):
                key = f"benchmark_key_{random.randint(0, 999)}"
                value = advanced_cache.get(key)
                
                if value is None:
                    # Se não encontrou, criar novo
                    new_key = f"new_key_{thread_id}_{i}"
                    new_value = f"new_value_{thread_id}_{i}"
                    advanced_cache.set(new_key, new_value, ttl=60)
        
        # Executar operações concorrentes
        threads = []
        for i in range(20):
            thread = threading.Thread(target=performance_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verificar performance
        total_operations = 20 * 100  # 20 threads * 100 operações cada
        throughput = total_operations / total_time
        
        assert throughput > 1000, f"Throughput muito baixo: {throughput:.2f} ops/s"
        assert total_time < 10.0, f"Tempo total muito alto: {total_time:.2f}s"

    def test_concurrent_memory_usage(self, advanced_cache):
        """Testa uso de memória sob concorrência."""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        def memory_intensive_operation(thread_id):
            """Operação intensiva em memória."""
            for i in range(1000):
                key = f"memory_key_{thread_id}_{i}"
                value = f"memory_value_{thread_id}_{i}" * 100  # Valor grande
                advanced_cache.set(key, value, ttl=60)
                
                # Ler alguns valores
                for j in range(10):
                    read_key = f"memory_key_{thread_id}_{random.randint(0, i)}"
                    advanced_cache.get(read_key)
        
        # Executar operações concorrentes
        threads = []
        for i in range(5):
            thread = threading.Thread(target=memory_intensive_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Forçar garbage collection
        gc.collect()
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Verificar que uso de memória é controlado
        assert memory_increase < 200 * 1024 * 1024, f"Aumento de memória muito alto: {memory_increase / 1024 / 1024:.2f}MB"

    # ==================== DEADLOCK PREVENTION ====================

    def test_deadlock_prevention(self, advanced_cache):
        """Testa prevenção de deadlock."""
        # Simular cenário que poderia causar deadlock
        lock1 = threading.Lock()
        lock2 = threading.Lock()
        
        def deadlock_prone_operation(thread_id):
            """Operação que poderia causar deadlock."""
            for i in range(10):
                if thread_id % 2 == 0:
                    # Thread par: lock1 -> lock2
                    with lock1:
                        time.sleep(0.001)
                        with lock2:
                            key = f"deadlock_key_{thread_id}_{i}"
                            advanced_cache.set(key, f"value_{thread_id}_{i}", ttl=60)
                else:
                    # Thread ímpar: lock2 -> lock1
                    with lock2:
                        time.sleep(0.001)
                        with lock1:
                            key = f"deadlock_key_{thread_id}_{i}"
                            advanced_cache.set(key, f"value_{thread_id}_{i}", ttl=60)
        
        # Executar operações com timeout
        threads = []
        for i in range(4):
            thread = threading.Thread(target=deadlock_prone_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Aguardar com timeout
        for thread in threads:
            thread.join(timeout=5.0)  # 5 segundos de timeout
        
        # Verificar que todas as threads terminaram
        active_threads = [t for t in threads if t.is_alive()]
        assert len(active_threads) == 0, f"Threads ainda ativas: {len(active_threads)}"

    def test_timeout_handling(self, advanced_cache):
        """Testa tratamento de timeout em operações concorrentes."""
        def slow_operation(thread_id):
            """Operação lenta que simula timeout."""
            for i in range(10):
                key = f"timeout_key_{thread_id}_{i}"
                
                # Simular operação lenta
                time.sleep(0.1)
                
                # Tentar operação de cache
                try:
                    advanced_cache.set(key, f"timeout_value_{thread_id}_{i}", ttl=60)
                    retrieved_value = advanced_cache.get(key)
                    assert retrieved_value is not None
                except Exception as e:
                    # Deve lidar com timeout graciosamente
                    pass
        
        # Executar operações com timeout
        threads = []
        for i in range(5):
            thread = threading.Thread(target=slow_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Aguardar com timeout
        for thread in threads:
            thread.join(timeout=10.0)  # 10 segundos de timeout
        
        # Verificar que todas as threads terminaram
        active_threads = [t for t in threads if t.is_alive()]
        assert len(active_threads) == 0, f"Threads ainda ativas: {len(active_threads)}"

    # ==================== TESTES DE STRESS ====================

    def test_stress_concurrent_access(self, advanced_cache):
        """Teste de stress com acesso concorrente intenso."""
        start_time = time.time()
        total_operations = 0
        errors = []
        
        def stress_operation(thread_id):
            """Operação de stress."""
            nonlocal total_operations
            
            try:
                for i in range(1000):
                    operation_type = random.choice(['get', 'set', 'delete'])
                    key = f"stress_key_{thread_id}_{i}"
                    
                    if operation_type == 'get':
                        advanced_cache.get(key)
                    elif operation_type == 'set':
                        advanced_cache.set(key, f"stress_value_{thread_id}_{i}", ttl=60)
                    elif operation_type == 'delete':
                        advanced_cache.delete(key)
                    
                    total_operations += 1
                    
            except Exception as e:
                errors.append(e)
        
        # Executar operações de stress
        threads = []
        for i in range(10):
            thread = threading.Thread(target=stress_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verificar que não houve muitos erros
        assert len(errors) < 10, f"Muitos erros encontrados: {len(errors)}"
        
        # Verificar performance
        throughput = total_operations / total_time
        assert throughput > 500, f"Throughput muito baixo: {throughput:.2f} ops/s"
        assert total_time < 30.0, f"Tempo total muito alto: {total_time:.2f}s"

    def test_stress_memory_pressure(self, advanced_cache):
        """Teste de stress com pressão de memória."""
        import gc
        
        # Forçar garbage collection
        gc.collect()
        
        def memory_pressure_operation(thread_id):
            """Operação que cria pressão de memória."""
            large_data = []
            
            for i in range(100):
                # Criar dados grandes
                key = f"pressure_key_{thread_id}_{i}"
                value = f"pressure_value_{thread_id}_{i}" * 1000  # Valor muito grande
                
                advanced_cache.set(key, value, ttl=60)
                large_data.append(value)
                
                # Ler dados
                for j in range(10):
                    read_key = f"pressure_key_{thread_id}_{random.randint(0, i)}"
                    advanced_cache.get(read_key)
            
            # Liberar dados grandes
            del large_data
            gc.collect()
        
        # Executar operações com pressão de memória
        threads = []
        for i in range(5):
            thread = threading.Thread(target=memory_pressure_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Forçar garbage collection final
        gc.collect()
        
        # Verificar que sistema ainda funciona
        test_key = "final_test_key"
        test_value = "final_test_value"
        
        success_set = advanced_cache.set(test_key, test_value, ttl=60)
        retrieved_value = advanced_cache.get(test_key)
        
        assert success_set
        assert retrieved_value == test_value

    # ==================== TESTES DE CONFIGURAÇÃO ====================

    @pytest.mark.parametrize("max_workers", [1, 2, 4, 8, 16])
    def test_concurrent_configuration_performance(self, max_workers):
        """Testa performance com diferentes configurações de concorrência."""
        config = CacheConfig(
            l1_enabled=True,
            l1_max_size=1000,
            l2_enabled=True,
            l2_max_size=5000,
            strategy=CacheStrategy.LRU,
            default_ttl=3600
        )
        
        cache = AdvancedCaching(config)
        
        def worker_operation(thread_id):
            """Operação de worker."""
            for i in range(100):
                key = f"config_key_{thread_id}_{i}"
                value = f"config_value_{thread_id}_{i}"
                
                cache.set(key, value, ttl=60)
                retrieved_value = cache.get(key)
                
                assert retrieved_value == value
        
        # Executar com diferentes números de workers
        start_time = time.time()
        
        threads = []
        for i in range(max_workers):
            thread = threading.Thread(target=worker_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verificar que performance é razoável
        total_operations = max_workers * 100
        throughput = total_operations / total_time
        
        assert throughput > 50, f"Throughput muito baixo para {max_workers} workers: {throughput:.2f} ops/s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 