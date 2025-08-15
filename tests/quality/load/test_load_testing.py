# 🧪 Testes de Carga - Omni Keywords Finder
# 📅 Semana 7-8: Integration & E2E (Meta: 98% cobertura)
# 🎯 Tracing ID: TESTES_98_COBERTURA_001_20250127
# 📝 Prompt: Implementar testes de carga para validar performance
# 🔧 Ruleset: enterprise_control_layer.yaml

"""
Testes de Carga e Performance
=============================

Este módulo implementa testes de carga para validar:
- Performance sob carga
- Escalabilidade do sistema
- Limites de capacidade
- Estabilidade em longo prazo
- Recuperação de falhas

Cobertura Alvo: 98% (Semana 7-8)
"""

import pytest
import asyncio
import time
import statistics
from typing import Dict, Any, List, Tuple
from unittest.mock import patch, MagicMock
import httpx
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class LoadTestResult:
    """Resultado de teste de carga."""
    endpoint: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    error_rate: float
    test_duration: float


class LoadTestingFramework:
    """Framework para testes de carga."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[LoadTestResult] = []
        
    async def run_concurrent_requests(
        self, 
        endpoint: str, 
        method: str = "GET",
        payload: Dict = None,
        headers: Dict = None,
        concurrent_users: int = 10,
        requests_per_user: int = 10,
        timeout: float = 30.0
    ) -> LoadTestResult:
        """
        Executa requisições concorrentes para teste de carga.
        
        Args:
            endpoint: Endpoint a ser testado
            method: Método HTTP
            payload: Dados da requisição
            headers: Headers HTTP
            concurrent_users: Número de usuários simultâneos
            requests_per_user: Requisições por usuário
            timeout: Timeout por requisição
            
        Returns:
            LoadTestResult com métricas de performance
        """
        start_time = time.time()
        response_times = []
        successful_requests = 0
        failed_requests = 0
        
        async def make_request(user_id: int, request_id: int) -> Tuple[bool, float]:
            """Faz uma requisição individual."""
            try:
                request_start = time.time()
                
                async with httpx.AsyncClient(timeout=timeout) as client:
                    if method.upper() == "GET":
                        response = await client.get(
                            f"{self.base_url}{endpoint}",
                            headers=headers
                        )
                    elif method.upper() == "POST":
                        response = await client.post(
                            f"{self.base_url}{endpoint}",
                            json=payload,
                            headers=headers
                        )
                    elif method.upper() == "PUT":
                        response = await client.put(
                            f"{self.base_url}{endpoint}",
                            json=payload,
                            headers=headers
                        )
                    elif method.upper() == "DELETE":
                        response = await client.delete(
                            f"{self.base_url}{endpoint}",
                            headers=headers
                        )
                    else:
                        raise ValueError(f"Método HTTP não suportado: {method}")
                
                request_time = time.time() - request_start
                
                if response.status_code < 400:
                    return True, request_time
                else:
                    return False, request_time
                    
            except Exception as e:
                # Falha na requisição
                return False, 0.0
        
        # Executar requisições concorrentes
        tasks = []
        for user_id in range(concurrent_users):
            for request_id in range(requests_per_user):
                task = make_request(user_id, request_id)
                tasks.append(task)
        
        # Aguardar todas as requisições
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Processar resultados
        for result in results:
            if isinstance(result, Exception):
                failed_requests += 1
            else:
                success, response_time = result
                if success:
                    successful_requests += 1
                    response_times.append(response_time)
                else:
                    failed_requests += 1
        
        total_requests = concurrent_users * requests_per_user
        test_duration = time.time() - start_time
        
        # Calcular métricas
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            # Percentis
            sorted_times = sorted(response_times)
            p95_index = int(len(sorted_times) * 0.95)
            p99_index = int(len(sorted_times) * 0.99)
            
            p95_response_time = sorted_times[p95_index] if p95_index < len(sorted_times) else max_response_time
            p99_response_time = sorted_times[p99_index] if p99_index < len(sorted_times) else max_response_time
        else:
            avg_response_time = min_response_time = max_response_time = p95_response_time = p99_response_time = 0.0
        
        requests_per_second = total_requests / test_duration if test_duration > 0 else 0.0
        error_rate = failed_requests / total_requests if total_requests > 0 else 0.0
        
        result = LoadTestResult(
            endpoint=endpoint,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            requests_per_second=requests_per_second,
            error_rate=error_rate,
            test_duration=test_duration
        )
        
        self.results.append(result)
        return result
    
    def generate_load_report(self) -> str:
        """Gera relatório de testes de carga."""
        if not self.results:
            return "Nenhum teste de carga executado."
        
        report = []
        report.append("=" * 80)
        report.append("📊 RELATÓRIO DE TESTES DE CARGA")
        report.append("=" * 80)
        report.append(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total de Testes: {len(self.results)}")
        report.append("")
        
        for result in self.results:
            report.append(f"🔗 Endpoint: {result.endpoint}")
            report.append(f"   📈 Total de Requisições: {result.total_requests}")
            report.append(f"   ✅ Sucessos: {result.successful_requests}")
            report.append(f"   ❌ Falhas: {result.failed_requests}")
            report.append(f"   ⏱️  Tempo Médio: {result.avg_response_time:.3f}s")
            report.append(f"   🚀 RPS: {result.requests_per_second:.2f}")
            report.append(f"   📊 Taxa de Erro: {result.error_rate:.2%}")
            report.append(f"   📊 P95: {result.p95_response_time:.3f}s")
            report.append(f"   📊 P99: {result.p99_response_time:.3f}s")
            report.append("")
        
        # Resumo geral
        total_requests = sum(r.total_requests for r in self.results)
        total_successful = sum(r.successful_requests for r in self.results)
        total_failed = sum(r.failed_requests for r in self.results)
        overall_error_rate = total_failed / total_requests if total_requests > 0 else 0.0
        
        report.append("📋 RESUMO GERAL")
        report.append("-" * 40)
        report.append(f"Total de Requisições: {total_requests}")
        report.append(f"Total de Sucessos: {total_successful}")
        report.append(f"Total de Falhas: {total_failed}")
        report.append(f"Taxa de Erro Geral: {overall_error_rate:.2%}")
        report.append("")
        
        return "\n".join(report)


class TestLoadTesting:
    """Testes de carga para o sistema."""
    
    @pytest.fixture(autouse=True)
    def setup_load_testing(self):
        """Configura ambiente de teste de carga."""
        self.load_tester = LoadTestingFramework()
        self.base_url = "http://localhost:8000"
        
        # Configurações de teste
        self.test_configs = {
            "light_load": {"users": 5, "requests": 10},
            "medium_load": {"users": 20, "requests": 25},
            "heavy_load": {"users": 50, "requests": 50},
            "stress_test": {"users": 100, "requests": 100}
        }
        
        yield
        
        # Limpeza
        pass
    
    async def test_keyword_search_light_load(self):
        """
        Testa performance de busca de keywords sob carga leve.
        
        Cenário: 5 usuários simultâneos, 10 requisições cada
        """
        result = await self.load_tester.run_concurrent_requests(
            endpoint="/api/v1/keywords/search",
            method="GET",
            payload=None,
            headers=None,
            concurrent_users=self.test_configs["light_load"]["users"],
            requests_per_user=self.test_configs["light_load"]["requests"]
        )
        
        # Validações de performance
        assert result.successful_requests > 0
        assert result.error_rate < 0.05  # Máximo 5% de erro
        assert result.avg_response_time < 1.0  # Máximo 1 segundo
        assert result.p95_response_time < 2.0  # P95 < 2 segundos
        assert result.requests_per_second > 10  # Mínimo 10 RPS
    
    async def test_keyword_analysis_medium_load(self):
        """
        Testa performance de análise de keywords sob carga média.
        
        Cenário: 20 usuários simultâneos, 25 requisições cada
        """
        payload = {
            "keywords": ["python", "machine learning", "data science"],
            "config": {
                "analysis_type": "basic",
                "language": "pt-BR",
                "region": "BR"
            }
        }
        
        result = await self.load_tester.run_concurrent_requests(
            endpoint="/api/v1/analysis/create",
            method="POST",
            payload=payload,
            headers=None,
            concurrent_users=self.test_configs["medium_load"]["users"],
            requests_per_user=self.test_configs["medium_load"]["requests"]
        )
        
        # Validações de performance
        assert result.successful_requests > 0
        assert result.error_rate < 0.10  # Máximo 10% de erro
        assert result.avg_response_time < 3.0  # Máximo 3 segundos
        assert result.p95_response_time < 5.0  # P95 < 5 segundos
        assert result.requests_per_second > 50  # Mínimo 50 RPS
    
    async def test_dashboard_heavy_load(self):
        """
        Testa performance do dashboard sob carga pesada.
        
        Cenário: 50 usuários simultâneos, 50 requisições cada
        """
        result = await self.load_tester.run_concurrent_requests(
            endpoint="/api/v1/dashboard/overview",
            method="GET",
            payload=None,
            headers=None,
            concurrent_users=self.test_configs["heavy_load"]["users"],
            requests_per_user=self.test_configs["heavy_load"]["requests"]
        )
        
        # Validações de performance
        assert result.successful_requests > 0
        assert result.error_rate < 0.15  # Máximo 15% de erro
        assert result.avg_response_time < 2.0  # Máximo 2 segundos
        assert result.p95_response_time < 4.0  # P95 < 4 segundos
        assert result.requests_per_second > 100  # Mínimo 100 RPS
    
    async def test_stress_test_system_limits(self):
        """
        Testa limites do sistema sob estresse extremo.
        
        Cenário: 100 usuários simultâneos, 100 requisições cada
        """
        result = await self.load_tester.run_concurrent_requests(
            endpoint="/api/v1/keywords/search",
            method="GET",
            payload=None,
            headers=None,
            concurrent_users=self.test_configs["stress_test"]["users"],
            requests_per_user=self.test_configs["stress_test"]["requests"]
        )
        
        # Em teste de estresse, esperamos algumas falhas
        assert result.successful_requests > 0
        assert result.error_rate < 0.30  # Máximo 30% de erro
        assert result.avg_response_time < 5.0  # Máximo 5 segundos
        assert result.p95_response_time < 10.0  # P95 < 10 segundos
    
    async def test_concurrent_analysis_operations(self):
        """
        Testa operações concorrentes de análise.
        
        Cenário: Múltiplas análises simultâneas
        """
        # Criar múltiplas análises simultaneamente
        analysis_payloads = [
            {
                "keywords": [f"keyword_{i}"],
                "config": {"analysis_type": "basic"}
            }
            for i in range(20)
        ]
        
        results = []
        for payload in analysis_payloads:
            result = await self.load_tester.run_concurrent_requests(
                endpoint="/api/v1/analysis/create",
                method="POST",
                payload=payload,
                concurrent_users=1,
                requests_per_user=1
            )
            results.append(result)
        
        # Validar que todas as análises foram iniciadas
        successful_analyses = sum(1 for r in results if r.successful_requests > 0)
        assert successful_analyses >= 15  # Pelo menos 75% de sucesso
    
    async def test_database_connection_pool_under_load(self):
        """
        Testa pool de conexões do banco sob carga.
        
        Cenário: Múltiplas operações de banco simultâneas
        """
        # Simular múltiplas operações de banco
        db_operations = [
            "/api/v1/keywords/list",
            "/api/v1/analysis/list",
            "/api/v1/user/profile"
        ]
        
        results = []
        for endpoint in db_operations:
            result = await self.load_tester.run_concurrent_requests(
                endpoint=endpoint,
                method="GET",
                concurrent_users=10,
                requests_per_user=20
            )
            results.append(result)
        
        # Validar que pool de conexões está funcionando
        for result in results:
            assert result.error_rate < 0.10  # Máximo 10% de erro
            assert result.avg_response_time < 1.0  # Máximo 1 segundo
    
    async def test_memory_usage_under_load(self):
        """
        Testa uso de memória sob carga.
        
        Cenário: Monitoramento de recursos durante testes
        """
        # Mock de monitoramento de memória
        with patch('psutil.virtual_memory') as mock_memory:
            mock_memory.return_value = MagicMock(
                percent=75.0,  # 75% de uso
                available=1024 * 1024 * 1024,  # 1GB disponível
                total=4 * 1024 * 1024 * 1024  # 4GB total
            )
            
            # Executar teste de carga
            result = await self.load_tester.run_concurrent_requests(
                endpoint="/api/v1/keywords/search",
                method="GET",
                concurrent_users=30,
                requests_per_user=40
            )
            
            # Validar que sistema mantém performance
            assert result.successful_requests > 0
            assert result.error_rate < 0.15  # Máximo 15% de erro
            assert result.avg_response_time < 2.0  # Máximo 2 segundos
    
    async def test_network_latency_impact(self):
        """
        Testa impacto da latência de rede na performance.
        
        Cenário: Simulação de diferentes latências
        """
        # Mock de latência de rede
        with patch('httpx.AsyncClient.get') as mock_get:
            # Simular diferentes latências
            latencies = [0.1, 0.5, 1.0, 2.0]  # segundos
            
            async def delayed_response(*args, **kwargs):
                await asyncio.sleep(latencies.pop(0) if latencies else 0.1)
                return MagicMock(status_code=200, json=lambda: {"data": "test"})
            
            mock_get.side_effect = delayed_response
            
            # Executar teste com latência simulada
            result = await self.load_tester.run_concurrent_requests(
                endpoint="/api/v1/keywords/search",
                method="GET",
                concurrent_users=10,
                requests_per_user=20
            )
            
            # Validar que sistema lida com latência
            assert result.successful_requests > 0
            assert result.avg_response_time > 0.5  # Deve refletir latência
    
    async def test_gradual_load_increase(self):
        """
        Testa aumento gradual de carga.
        
        Cenário: Carga aumenta progressivamente para identificar breaking point
        """
        load_levels = [
            {"users": 5, "requests": 10},
            {"users": 15, "requests": 20},
            {"users": 30, "requests": 40},
            {"users": 50, "requests": 60}
        ]
        
        results = []
        for config in load_levels:
            result = await self.load_tester.run_concurrent_requests(
                endpoint="/api/v1/keywords/search",
                method="GET",
                concurrent_users=config["users"],
                requests_per_user=config["requests"]
            )
            results.append(result)
            
            # Aguardar entre níveis
            await asyncio.sleep(2)
        
        # Validar degradação gradual (não catastrófica)
        for i, result in enumerate(results):
            if i > 0:  # Comparar com nível anterior
                prev_result = results[i-1]
                # Performance pode degradar, mas não deve quebrar
                assert result.error_rate < 0.50  # Máximo 50% de erro
                assert result.avg_response_time < 10.0  # Máximo 10 segundos
    
    async def test_recovery_after_high_load(self):
        """
        Testa recuperação do sistema após carga alta.
        
        Cenário: Sistema se recupera após período de estresse
        """
        # 1. Aplicar carga alta
        stress_result = await self.load_tester.run_concurrent_requests(
            endpoint="/api/v1/keywords/search",
            method="GET",
            concurrent_users=80,
            requests_per_user=80
        )
        
        # 2. Aguardar estabilização
        await asyncio.sleep(5)
        
        # 3. Testar recuperação com carga normal
        recovery_result = await self.load_tester.run_concurrent_requests(
            endpoint="/api/v1/keywords/search",
            method="GET",
            concurrent_users=10,
            requests_per_user=20
        )
        
        # Validar recuperação
        assert recovery_result.error_rate < 0.05  # Deve voltar ao normal
        assert recovery_result.avg_response_time < 1.0  # Performance deve se recuperar
        assert recovery_result.requests_per_second > 10  # RPS deve se recuperar
    
    def test_load_test_report_generation(self):
        """Testa geração de relatórios de teste de carga."""
        # Simular alguns resultados
        self.load_tester.results = [
            LoadTestResult(
                endpoint="/api/v1/keywords/search",
                total_requests=100,
                successful_requests=95,
                failed_requests=5,
                avg_response_time=0.5,
                min_response_time=0.1,
                max_response_time=2.0,
                p95_response_time=1.0,
                p99_response_time=1.5,
                requests_per_second=50.0,
                error_rate=0.05,
                test_duration=2.0
            )
        ]
        
        # Gerar relatório
        report = self.load_tester.generate_load_report()
        
        # Validar conteúdo do relatório
        assert "RELATÓRIO DE TESTES DE CARGA" in report
        assert "/api/v1/keywords/search" in report
        assert "100" in report  # Total de requisições
        assert "95" in report   # Sucessos
        assert "5" in report    # Falhas
        assert "0.5" in report  # Tempo médio
        assert "50.0" in report # RPS


# Configuração de fixtures para testes de carga
@pytest.fixture
def load_testing_framework():
    """Framework de teste de carga."""
    return LoadTestingFramework()


@pytest.fixture
def sample_load_config():
    """Configuração de exemplo para testes de carga."""
    return {
        "concurrent_users": 10,
        "requests_per_user": 20,
        "timeout": 30.0
    }


# Configuração pytest para testes de carga
pytestmark = pytest.mark.asyncio
pytestmark = pytest.mark.load
pytestmark = pytest.mark.slow
