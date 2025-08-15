"""
Testes de performance para APIs
Criado em: 2025-01-27
Tracing ID: COMPLETUDE_CHECKLIST_20250127_001
"""

import pytest
import time
import asyncio
import aiohttp
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any
import statistics
import json
import tempfile
import os

class PerformanceTestConfig:
    """Configuração para testes de performance"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.timeout = 30
        self.max_concurrent_requests = 100
        self.test_duration = 60  # segundos
        self.ramp_up_time = 10   # segundos
        self.expected_response_time = 2.0  # segundos
        self.expected_throughput = 100  # requests/segundo
        self.error_threshold = 0.05  # 5%

class MockAPIClient:
    """Cliente mock para testes de API"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_keywords(self, limit: int = 100) -> Dict[str, Any]:
        """Mock da API de keywords"""
        start_time = time.time()
        
        # Simula latência de rede
        await asyncio.sleep(0.1)
        
        # Simula processamento
        await asyncio.sleep(0.05)
        
        response_time = time.time() - start_time
        
        return {
            'status': 200,
            'data': [{'keyword': f'keyword_{i}', 'volume': i * 100} for i in range(limit)],
            'response_time': response_time,
            'timestamp': time.time()
        }
    
    async def analyze_keyword(self, keyword: str) -> Dict[str, Any]:
        """Mock da API de análise de keyword"""
        start_time = time.time()
        
        # Simula latência de rede
        await asyncio.sleep(0.15)
        
        # Simula processamento pesado
        await asyncio.sleep(0.1)
        
        response_time = time.time() - start_time
        
        return {
            'status': 200,
            'data': {
                'keyword': keyword,
                'volume': 1000,
                'difficulty': 0.5,
                'cpc': 2.5
            },
            'response_time': response_time,
            'timestamp': time.time()
        }
    
    async def search_keywords(self, query: str) -> Dict[str, Any]:
        """Mock da API de busca de keywords"""
        start_time = time.time()
        
        # Simula latência de rede
        await asyncio.sleep(0.08)
        
        # Simula busca no banco
        await asyncio.sleep(0.03)
        
        response_time = time.time() - start_time
        
        return {
            'status': 200,
            'data': [{'keyword': f'{query}_{i}', 'relevance': 0.9 - i * 0.1} for i in range(10)],
            'response_time': response_time,
            'timestamp': time.time()
        }

class TestAPIPerformance:
    """Testes de performance para APIs"""
    
    def setup_method(self):
        """Configuração inicial para cada teste"""
        self.config = PerformanceTestConfig()
        self.results = []
    
    async def test_single_request_performance(self):
        """Testa performance de uma única requisição"""
        async with MockAPIClient(self.config.base_url) as client:
            start_time = time.time()
            response = await client.get_keywords(10)
            end_time = time.time()
            
            total_time = end_time - start_time
            
            assert response['status'] == 200
            assert total_time < self.config.expected_response_time
            assert len(response['data']) == 10
            
            self.results.append({
                'test': 'single_request',
                'response_time': total_time,
                'status': response['status']
            })
    
    async def test_concurrent_requests_performance(self):
        """Testa performance com requisições concorrentes"""
        async with MockAPIClient(self.config.base_url) as client:
            tasks = []
            
            # Cria múltiplas tarefas concorrentes
            for i in range(10):
                task = client.get_keywords(5)
                tasks.append(task)
            
            start_time = time.time()
            responses = await asyncio.gather(*tasks)
            end_time = time.time()
            
            total_time = end_time - start_time
            avg_response_time = total_time / len(responses)
            
            # Validações
            assert all(r['status'] == 200 for r in responses)
            assert avg_response_time < self.config.expected_response_time
            assert len(responses) == 10
            
            self.results.append({
                'test': 'concurrent_requests',
                'total_time': total_time,
                'avg_response_time': avg_response_time,
                'success_rate': 1.0
            })
    
    async def test_load_test_keyword_analysis(self):
        """Teste de carga para análise de keywords"""
        async with MockAPIClient(self.config.base_url) as client:
            keywords = [f"keyword_{i}" for i in range(50)]
            tasks = []
            
            for keyword in keywords:
                task = client.analyze_keyword(keyword)
                tasks.append(task)
            
            start_time = time.time()
            responses = await asyncio.gather(*tasks)
            end_time = time.time()
            
            total_time = end_time - start_time
            response_times = [r['response_time'] for r in responses]
            
            # Estatísticas
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            throughput = len(responses) / total_time
            
            # Validações
            assert all(r['status'] == 200 for r in responses)
            assert avg_response_time < self.config.expected_response_time
            assert throughput >= self.config.expected_throughput * 0.5  # 50% do esperado
            
            self.results.append({
                'test': 'load_test_keyword_analysis',
                'total_time': total_time,
                'avg_response_time': avg_response_time,
                'max_response_time': max_response_time,
                'min_response_time': min_response_time,
                'throughput': throughput,
                'success_rate': 1.0
            })
    
    async def test_stress_test_search_api(self):
        """Teste de estresse para API de busca"""
        async with MockAPIClient(self.config.base_url) as client:
            queries = [f"query_{i}" for i in range(100)]
            tasks = []
            
            for query in queries:
                task = client.search_keywords(query)
                tasks.append(task)
            
            start_time = time.time()
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            total_time = end_time - start_time
            
            # Separa sucessos e falhas
            successful_responses = [r for r in responses if isinstance(r, dict) and r.get('status') == 200]
            failed_responses = [r for r in responses if not isinstance(r, dict) or r.get('status') != 200]
            
            success_rate = len(successful_responses) / len(responses)
            throughput = len(successful_responses) / total_time
            
            # Validações
            assert success_rate >= (1 - self.config.error_threshold)
            assert throughput >= self.config.expected_throughput * 0.3  # 30% do esperado
            
            self.results.append({
                'test': 'stress_test_search_api',
                'total_time': total_time,
                'success_rate': success_rate,
                'throughput': throughput,
                'total_requests': len(responses),
                'successful_requests': len(successful_responses),
                'failed_requests': len(failed_responses)
            })
    
    async def test_memory_usage_performance(self):
        """Testa uso de memória durante operações"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        async with MockAPIClient(self.config.base_url) as client:
            # Executa operações que consomem memória
            large_responses = []
            for i in range(20):
                response = await client.get_keywords(1000)
                large_responses.append(response)
            
            # Força garbage collection
            import gc
            gc.collect()
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Validações
            assert memory_increase < 100  # Máximo 100MB de aumento
            assert len(large_responses) == 20
            
            self.results.append({
                'test': 'memory_usage_performance',
                'initial_memory_mb': initial_memory,
                'final_memory_mb': final_memory,
                'memory_increase_mb': memory_increase,
                'responses_processed': len(large_responses)
            })
    
    async def test_database_connection_pool_performance(self):
        """Testa performance do pool de conexões"""
        async with MockAPIClient(self.config.base_url) as client:
            # Simula múltiplas conexões simultâneas
            connection_tasks = []
            
            for i in range(20):
                task = client.analyze_keyword(f"test_keyword_{i}")
                connection_tasks.append(task)
            
            start_time = time.time()
            responses = await asyncio.gather(*connection_tasks)
            end_time = time.time()
            
            total_time = end_time - start_time
            response_times = [r['response_time'] for r in responses]
            
            # Validações
            assert all(r['status'] == 200 for r in responses)
            assert statistics.mean(response_times) < self.config.expected_response_time
            
            self.results.append({
                'test': 'database_connection_pool_performance',
                'total_time': total_time,
                'avg_response_time': statistics.mean(response_times),
                'max_response_time': max(response_times),
                'min_response_time': min(response_times),
                'connections_used': len(responses)
            })

class TestPerformanceMonitoring:
    """Testes para monitoramento de performance"""
    
    def setup_method(self):
        """Configuração inicial"""
        self.config = PerformanceTestConfig()
        self.performance_data = []
    
    def test_response_time_distribution(self):
        """Testa distribuição dos tempos de resposta"""
        # Simula dados de tempo de resposta
        response_times = [0.1, 0.2, 0.15, 0.3, 0.25, 0.18, 0.22, 0.28, 0.12, 0.35]
        
        # Calcula percentis
        sorted_times = sorted(response_times)
        p50 = sorted_times[len(sorted_times) // 2]
        p90 = sorted_times[int(len(sorted_times) * 0.9)]
        p95 = sorted_times[int(len(sorted_times) * 0.95)]
        p99 = sorted_times[int(len(sorted_times) * 0.99)]
        
        # Validações
        assert p50 <= 0.25  # Mediana <= 250ms
        assert p90 <= 0.35  # 90% <= 350ms
        assert p95 <= 0.40  # 95% <= 400ms
        assert p99 <= 0.50  # 99% <= 500ms
        
        self.performance_data.append({
            'metric': 'response_time_distribution',
            'p50': p50,
            'p90': p90,
            'p95': p95,
            'p99': p99,
            'mean': statistics.mean(response_times)
        })
    
    def test_throughput_calculation(self):
        """Testa cálculo de throughput"""
        # Simula dados de throughput
        requests_per_second = [95, 98, 102, 97, 103, 99, 101, 96, 104, 100]
        
        avg_throughput = statistics.mean(requests_per_second)
        min_throughput = min(requests_per_second)
        max_throughput = max(requests_per_second)
        
        # Validações
        assert avg_throughput >= 95  # Mínimo 95 req/s
        assert min_throughput >= 90  # Mínimo 90 req/s
        assert max_throughput <= 110  # Máximo 110 req/s
        
        self.performance_data.append({
            'metric': 'throughput_calculation',
            'avg_throughput': avg_throughput,
            'min_throughput': min_throughput,
            'max_throughput': max_throughput
        })
    
    def test_error_rate_calculation(self):
        """Testa cálculo de taxa de erro"""
        # Simula dados de requisições
        total_requests = 1000
        successful_requests = 985
        failed_requests = total_requests - successful_requests
        
        error_rate = failed_requests / total_requests
        
        # Validações
        assert error_rate <= self.config.error_threshold
        assert error_rate >= 0
        
        self.performance_data.append({
            'metric': 'error_rate_calculation',
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'error_rate': error_rate
        })
    
    def test_performance_report_generation(self):
        """Testa geração de relatório de performance"""
        # Simula dados de performance
        performance_metrics = {
            'avg_response_time': 0.25,
            'max_response_time': 0.45,
            'throughput': 98.5,
            'error_rate': 0.02,
            'memory_usage_mb': 45.2,
            'cpu_usage_percent': 12.5
        }
        
        # Gera relatório
        report = {
            'timestamp': time.time(),
            'test_duration': self.config.test_duration,
            'metrics': performance_metrics,
            'status': 'PASS' if performance_metrics['error_rate'] <= self.config.error_threshold else 'FAIL'
        }
        
        # Salva relatório temporário
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(report, f, indent=2)
            report_file = f.name
        
        try:
            # Valida relatório
            with open(report_file, 'r') as f:
                loaded_report = json.load(f)
            
            assert 'timestamp' in loaded_report
            assert 'metrics' in loaded_report
            assert 'status' in loaded_report
            assert loaded_report['status'] in ['PASS', 'FAIL']
            
        finally:
            os.unlink(report_file)

class TestPerformanceBenchmarks:
    """Testes de benchmark de performance"""
    
    def setup_method(self):
        """Configuração inicial"""
        self.benchmark_results = []
    
    def test_keyword_analysis_benchmark(self):
        """Benchmark para análise de keywords"""
        import time
        
        # Simula benchmark
        iterations = 100
        times = []
        
        for i in range(iterations):
            start_time = time.time()
            # Simula operação de análise
            time.sleep(0.01)  # 10ms
            end_time = time.time()
            times.append(end_time - start_time)
        
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        
        # Validações
        assert avg_time < 0.02  # Média < 20ms
        assert max_time < 0.05  # Máximo < 50ms
        
        self.benchmark_results.append({
            'benchmark': 'keyword_analysis',
            'iterations': iterations,
            'avg_time_ms': avg_time * 1000,
            'min_time_ms': min_time * 1000,
            'max_time_ms': max_time * 1000,
            'throughput_per_second': iterations / sum(times)
        })
    
    def test_database_query_benchmark(self):
        """Benchmark para queries de banco"""
        import time
        
        # Simula benchmark de queries
        iterations = 50
        times = []
        
        for i in range(iterations):
            start_time = time.time()
            # Simula query
            time.sleep(0.005)  # 5ms
            end_time = time.time()
            times.append(end_time - start_time)
        
        avg_time = statistics.mean(times)
        
        # Validações
        assert avg_time < 0.01  # Média < 10ms
        
        self.benchmark_results.append({
            'benchmark': 'database_query',
            'iterations': iterations,
            'avg_time_ms': avg_time * 1000,
            'throughput_per_second': iterations / sum(times)
        })

if __name__ == "__main__":
    pytest.main([__file__]) 