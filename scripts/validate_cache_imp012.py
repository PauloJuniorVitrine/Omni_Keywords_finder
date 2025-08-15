#!/usr/bin/env python3
"""
🚀 Script de Validação - IMP-012: Sistema de Cache Inteligente
🎯 Objetivo: Validar cache inteligente com hit rate > 90%
📅 Criado: 2024-12-27
🔄 Versão: 1.0
"""

import sys
import os
import time
import json
import threading
import subprocess
from datetime import datetime
from typing import Dict, List, Any

# Adicionar path para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

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


class CacheValidator:
    """Validador do sistema de cache inteligente."""
    
    def __init__(self):
        """Inicializa o validador."""
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests_passed': 0,
            'tests_failed': 0,
            'total_tests': 0,
            'hit_rate_achieved': 0.0,
            'performance_metrics': {},
            'validation_status': 'PENDING'
        }
        
        # Inicializar sistema de cache
        self.cache_system = IntelligentCacheSystem(
            enable_l1=True,
            enable_l2=True,
            l1_max_size=1000,
            enable_compression=True,
            enable_adaptive_ttl=True
        )
    
    def run_unit_tests(self) -> bool:
        """Executa testes unitários."""
        print("🧪 Executando testes unitários...")
        
        try:
            # Executar testes via subprocess
            result = subprocess.run([
                sys.executable, '-m', 'unittest', 
                'tests.unit.test_intelligent_cache_imp012',
                '-value'
            ], capture_output=True, text=True, cwd=os.path.join(os.path.dirname(__file__), '..'))
            
            if result.returncode == 0:
                print("✅ Testes unitários passaram!")
                self.results['tests_passed'] += 1
                return True
            else:
                print(f"❌ Testes unitários falharam:\n{result.stdout}\n{result.stderr}")
                self.results['tests_failed'] += 1
                return False
                
        except Exception as e:
            print(f"❌ Erro ao executar testes unitários: {e}")
            self.results['tests_failed'] += 1
            return False
    
    def test_hit_rate_optimization(self) -> bool:
        """Testa otimização de hit rate."""
        print("🎯 Testando otimização de hit rate...")
        
        def expensive_operation(key: str) -> str:
            time.sleep(0.01)  # Simular operação cara
            return f"result_{key}"
        
        # Simular padrão de acesso com alta reutilização
        keys = [f"key_{index}" for index in range(50)]
        
        # Primeira rodada - todos miss
        print("  📥 Primeira rodada (misses)...")
        for key in keys:
            self.cache_system.get_or_set(key, lambda key=key: expensive_operation(key), ttl=60)
        
        # Segunda rodada - todos hit
        print("  📤 Segunda rodada (hits)...")
        for key in keys:
            self.cache_system.get_or_set(key, lambda key=key: expensive_operation(key), ttl=60)
        
        # Terceira rodada - todos hit
        print("  📤 Terceira rodada (hits)...")
        for key in keys:
            self.cache_system.get_or_set(key, lambda key=key: expensive_operation(key), ttl=60)
        
        # Obter estatísticas
        stats = self.cache_system.get_stats()
        hit_rate = stats['global_metrics']['hit_rate']
        
        print(f"  📊 Hit rate alcançado: {hit_rate:.2%}")
        
        # Validar hit rate > 90%
        if hit_rate > 0.9:
            print("✅ Hit rate > 90% alcançado!")
            self.results['hit_rate_achieved'] = hit_rate
            self.results['tests_passed'] += 1
            return True
        else:
            print(f"❌ Hit rate insuficiente: {hit_rate:.2%} (meta: >90%)")
            self.results['tests_failed'] += 1
            return False
    
    def test_adaptive_ttl(self) -> bool:
        """Testa TTL adaptativo."""
        print("🔄 Testando TTL adaptativo...")
        
        # Simular acessos frequentes
        for index in range(30):
            self.cache_system.get_or_set("frequent_key", lambda: "value", ttl=60)
        
        # Verificar se TTL foi adaptado
        stats = self.cache_system.get_stats()
        ttl_adaptations = stats['global_metrics']['ttl_adaptations']
        
        if ttl_adaptations > 0:
            print(f"✅ TTL adaptativo funcionando: {ttl_adaptations} adaptações")
            self.results['tests_passed'] += 1
            return True
        else:
            print("❌ TTL adaptativo não funcionou")
            self.results['tests_failed'] += 1
            return False
    
    def test_compression(self) -> bool:
        """Testa compressão automática."""
        print("🗜️ Testando compressão automática...")
        
        # Criar dados grandes
        large_data = "value" * 100000  # 100KB
        self.cache_system.set("large_key", large_data, ttl=60)
        
        # Verificar se foi comprimido
        stats = self.cache_system.get_stats()
        compression_savings = stats['global_metrics']['compression_savings']
        
        if compression_savings > 0:
            print(f"✅ Compressão funcionando: {compression_savings:.2%} de economia")
            self.results['tests_passed'] += 1
            return True
        else:
            print("❌ Compressão não funcionou")
            self.results['tests_failed'] += 1
            return False
    
    def test_cache_warming(self) -> bool:
        """Testa cache warming."""
        print("🔥 Testando cache warming...")
        
        def getter(key: str) -> str:
            return f"warmed_{key}"
        
        keys = [f"warm_key_{index}" for index in range(10)]
        self.cache_system.warm_cache(keys, getter, ttl=60)
        
        # Verificar se todos os itens estão no cache
        all_cached = True
        for key in keys:
            value = self.cache_system.get(key)
            if value != f"warmed_{key}":
                all_cached = False
                break
        
        if all_cached:
            print("✅ Cache warming funcionando!")
            self.results['tests_passed'] += 1
            return True
        else:
            print("❌ Cache warming falhou")
            self.results['tests_failed'] += 1
            return False
    
    def test_pattern_invalidation(self) -> bool:
        """Testa invalidação por padrão."""
        print("🗑️ Testando invalidação por padrão...")
        
        # Adicionar itens
        self.cache_system.set("user_123_data", "value1")
        self.cache_system.set("user_123_config", "value2")
        self.cache_system.set("other_data", "value3")
        
        # Invalidar padrão
        self.cache_system.invalidate_pattern("user_123_*")
        
        # Verificar que itens do padrão foram removidos
        user_data = self.cache_system.get("user_123_data")
        user_config = self.cache_system.get("user_123_config")
        other_data = self.cache_system.get("other_data")
        
        if user_data is None and user_config is None and other_data is not None:
            print("✅ Invalidação por padrão funcionando!")
            self.results['tests_passed'] += 1
            return True
        else:
            print("❌ Invalidação por padrão falhou")
            self.results['tests_failed'] += 1
            return False
    
    def test_concurrent_access(self) -> bool:
        """Testa acesso concorrente."""
        print("🔄 Testando acesso concorrente...")
        
        def worker(worker_id: int):
            for index in range(20):
                key = f"worker_{worker_id}_key_{index}"
                self.cache_system.get_or_set(key, lambda key=key: f"value_{key}", ttl=60)
        
        # Criar múltiplas threads
        threads = []
        for index in range(10):
            thread = threading.Thread(target=worker, args=(index,))
            threads.append(thread)
            thread.start()
        
        # Aguardar conclusão
        for thread in threads:
            thread.join()
        
        # Verificar que não houve erros
        stats = self.cache_system.get_stats()
        total_requests = stats['global_metrics']['total_requests']
        
        if total_requests > 0:
            print(f"✅ Acesso concorrente funcionando: {total_requests} requisições")
            self.results['tests_passed'] += 1
            return True
        else:
            print("❌ Acesso concorrente falhou")
            self.results['tests_failed'] += 1
            return False
    
    def test_performance_benchmarks(self) -> bool:
        """Testa benchmarks de performance."""
        print("⚡ Testando benchmarks de performance...")
        
        start_time = time.time()
        
        # Simular 2000 acessos
        for index in range(2000):
            key = f"perf_key_{index % 100}"  # Reutilizar chaves
            self.cache_system.get_or_set(key, lambda key=key: f"value_{key}", ttl=60)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Verificar performance (deve ser rápido)
        if duration < 10.0:  # Máximo 10 segundos
            print(f"✅ Performance OK: {duration:.2f}string_data para 2000 acessos")
            
            # Verificar hit rate alto
            stats = self.cache_system.get_stats()
            hit_rate = stats['global_metrics']['hit_rate']
            
            if hit_rate > 0.8:  # Pelo menos 80% de hit rate
                print(f"✅ Hit rate alto: {hit_rate:.2%}")
                self.results['performance_metrics'] = {
                    'duration_seconds': duration,
                    'hit_rate': hit_rate,
                    'requests_per_second': 2000 / duration
                }
                self.results['tests_passed'] += 1
                return True
            else:
                print(f"❌ Hit rate baixo: {hit_rate:.2%}")
                self.results['tests_failed'] += 1
                return False
        else:
            print(f"❌ Performance lenta: {duration:.2f}string_data")
            self.results['tests_failed'] += 1
            return False
    
    def test_memory_management(self) -> bool:
        """Testa gerenciamento de memória."""
        print("💾 Testando gerenciamento de memória...")
        
        # Adicionar muitos itens pequenos
        for index in range(2000):
            self.cache_system.set(f"mem_key_{index}", f"value_{index}", ttl=60)
        
        # Verificar que cache não excedeu limite
        stats = self.cache_system.get_stats()
        l1_stats = stats.get('l1_cache', {})
        
        if l1_stats:
            size = l1_stats.get('size', 0)
            max_size = l1_stats.get('max_size', 1000)
            
            if size <= max_size:
                print(f"✅ Gerenciamento de memória OK: {size}/{max_size} itens")
                self.results['tests_passed'] += 1
                return True
            else:
                print(f"❌ Cache excedeu limite: {size}/{max_size}")
                self.results['tests_failed'] += 1
                return False
        else:
            print("❌ Estatísticas L1 não disponíveis")
            self.results['tests_failed'] += 1
            return False
    
    def test_cache_decorator(self) -> bool:
        """Testa decorator de cache."""
        print("🎭 Testando decorator de cache...")
        
        call_count = 0
        
        @cache_decorator(ttl=60)
        def expensive_function(value: int, result: int) -> int:
            nonlocal call_count
            call_count += 1
            time.sleep(0.01)  # Simular operação cara
            return value + result
        
        # Primeira chamada
        result1 = expensive_function(1, 2)
        
        # Segunda chamada (deve usar cache)
        result2 = expensive_function(1, 2)
        
        # Terceira chamada (deve usar cache)
        result3 = expensive_function(1, 2)
        
        if result1 == result2 == result3 == 3 and call_count == 1:
            print("✅ Decorator de cache funcionando!")
            self.results['tests_passed'] += 1
            return True
        else:
            print(f"❌ Decorator de cache falhou: call_count={call_count}")
            self.results['tests_failed'] += 1
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Executa todos os testes."""
        print("🚀 Iniciando validação do sistema de cache inteligente...")
        print("=" * 60)
        
        tests = [
            ("Testes Unitários", self.run_unit_tests),
            ("Hit Rate Optimization", self.test_hit_rate_optimization),
            ("TTL Adaptativo", self.test_adaptive_ttl),
            ("Compressão", self.test_compression),
            ("Cache Warming", self.test_cache_warming),
            ("Invalidação por Padrão", self.test_pattern_invalidation),
            ("Acesso Concorrente", self.test_concurrent_access),
            ("Benchmarks de Performance", self.test_performance_benchmarks),
            ("Gerenciamento de Memória", self.test_memory_management),
            ("Decorator de Cache", self.test_cache_decorator)
        ]
        
        self.results['total_tests'] = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n📋 {test_name}")
            print("-" * 40)
            
            try:
                success = test_func()
                if success:
                    print(f"✅ {test_name}: PASSOU")
                else:
                    print(f"❌ {test_name}: FALHOU")
            except Exception as e:
                print(f"❌ {test_name}: ERRO - {e}")
                self.results['tests_failed'] += 1
        
        # Calcular status final
        success_rate = self.results['tests_passed'] / self.results['total_tests']
        
        if success_rate >= 0.9 and self.results['hit_rate_achieved'] > 0.9:
            self.results['validation_status'] = 'PASSED'
            print(f"\n🎉 VALIDAÇÃO PASSOU!")
        else:
            self.results['validation_status'] = 'FAILED'
            print(f"\n❌ VALIDAÇÃO FALHOU!")
        
        print(f"📊 Resultados:")
        print(f"   Testes passados: {self.results['tests_passed']}/{self.results['total_tests']}")
        print(f"   Taxa de sucesso: {success_rate:.2%}")
        print(f"   Hit rate alcançado: {self.results['hit_rate_achieved']:.2%}")
        print(f"   Status: {self.results['validation_status']}")
        
        return self.results
    
    def save_results(self, filename: str = "cache_validation_results.json"):
        """Salva resultados da validação."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n💾 Resultados salvos em: {filename}")


def main():
    """Função principal."""
    print("🚀 IMP-012: Validação do Sistema de Cache Inteligente")
    print("=" * 60)
    
    validator = CacheValidator()
    results = validator.run_all_tests()
    
    # Salvar resultados
    validator.save_results()
    
    # Retornar código de saída
    if results['validation_status'] == 'PASSED':
        print("\n✅ IMP-012: VALIDAÇÃO CONCLUÍDA COM SUCESSO!")
        return 0
    else:
        print("\n❌ IMP-012: VALIDAÇÃO FALHOU!")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code) 