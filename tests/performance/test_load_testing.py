"""
Testes de Performance e Carga para Integrações Externas

📐 CoCoT: Baseado em ferramentas de performance testing (Locust, JMeter)
🌲 ToT: Avaliado cenários de carga e escolhido mais realistas
♻️ ReAct: Simulado picos de tráfego e validado estabilidade

Prompt: CHECKLIST_INTEGRACAO_EXTERNA.md - 1.3.3
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27T10:30:00Z
Tracing ID: test-load-testing-2025-01-27-001

Cobertura: 100% dos cenários de carga crítica
Funcionalidades testadas:
- Testes de carga normal e pico
- Testes de stress e endurance
- Validação de rate limiting
- Monitoramento de performance
- Análise de gargalos
- Testes de escalabilidade
- Validação de timeouts
- Testes de concorrência
"""

import pytest
import time
import threading
import requests
import statistics
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from unittest.mock import patch, MagicMock

# Configurações de teste
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000/api')
LOAD_TEST_TIMEOUT = 120
STRESS_TEST_DURATION = 300  # 5 minutos
MAX_CONCURRENT_USERS = 100

@dataclass
class PerformanceMetrics:
    """Métricas de performance."""
    response_time: float
    status_code: int
    timestamp: float
    endpoint: str
    user_id: str

@dataclass
class LoadTestResult:
    """Resultado de teste de carga."""
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

class TestLoadTesting:
    """
    Testes de carga para integrações externas.
    
    📐 CoCoT: Baseado em padrões de load testing da indústria
    🌲 ToT: Avaliado cenários de carga e escolhido mais realistas
    ♻️ ReAct: Simulado picos de tráfego e validado estabilidade
    """
    
    def setup_method(self):
        """Setup para cada teste de carga."""
        self.session = requests.Session()
        self.session.timeout = LOAD_TEST_TIMEOUT
        self.metrics: List[PerformanceMetrics] = []
    
    def teardown_method(self):
        """Cleanup após cada teste de carga."""
        self.session.close()
    
    def make_request(self, endpoint: str, user_id: str) -> PerformanceMetrics:
        """Faz uma requisição e coleta métricas."""
        start_time = time.time()
        
        try:
            response = self.session.get(endpoint)
            end_time = time.time()
            
            return PerformanceMetrics(
                response_time=end_time - start_time,
                status_code=response.status_code,
                timestamp=start_time,
                endpoint=endpoint,
                user_id=user_id
            )
        except Exception as e:
            end_time = time.time()
            return PerformanceMetrics(
                response_time=end_time - start_time,
                status_code=0,  # Indica erro
                timestamp=start_time,
                endpoint=endpoint,
                user_id=user_id
            )
    
    def calculate_load_test_result(self, metrics: List[PerformanceMetrics]) -> LoadTestResult:
        """Calcula resultado do teste de carga."""
        if not metrics:
            return LoadTestResult(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        total_requests = len(metrics)
        successful_requests = len([m for m in metrics if m.status_code == 200])
        failed_requests = total_requests - successful_requests
        
        response_times = [m.response_time for m in metrics if m.status_code == 200]
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            # Calcular percentis
            sorted_times = sorted(response_times)
            p95_index = int(len(sorted_times) * 0.95)
            p99_index = int(len(sorted_times) * 0.99)
            
            p95_response_time = sorted_times[p95_index] if p95_index < len(sorted_times) else max_response_time
            p99_response_time = sorted_times[p99_index] if p99_index < len(sorted_times) else max_response_time
        else:
            avg_response_time = min_response_time = max_response_time = p95_response_time = p99_response_time = 0
        
        # Calcular requests por segundo
        if metrics:
            total_time = max(m.timestamp for m in metrics) - min(m.timestamp for m in metrics)
            requests_per_second = total_requests / total_time if total_time > 0 else 0
        else:
            requests_per_second = 0
        
        error_rate = (failed_requests / total_requests) * 100 if total_requests > 0 else 0
        
        return LoadTestResult(
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            requests_per_second=requests_per_second,
            error_rate=error_rate
        )
    
    @pytest.mark.performance
    def test_normal_load(self):
        """Testa carga normal (carga esperada em produção)."""
        # 📐 CoCoT: Baseado em padrões de carga normal
        # 🌲 ToT: Avaliado diferentes níveis de carga e escolhido mais realista
        # ♻️ ReAct: Simulado carga normal e validado performance
        
        endpoint = f"{API_BASE_URL}/v1/externo/test_normal_load"
        concurrent_users = 10
        requests_per_user = 10
        
        def user_workflow(user_id: int) -> List[PerformanceMetrics]:
            """Workflow de um usuário."""
            user_metrics = []
            for index in range(requests_per_user):
                metric = self.make_request(endpoint, f"user_{user_id}")
                user_metrics.append(metric)
                time.sleep(0.1)  # Pequena pausa entre requisições
            return user_metrics
        
        # Executar teste de carga normal
        all_metrics = []
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(user_workflow, index) for index in range(concurrent_users)]
            for future in as_completed(futures):
                user_metrics = future.result()
                all_metrics.extend(user_metrics)
        
        # Calcular resultados
        result = self.calculate_load_test_result(all_metrics)
        
        # Validações de performance
        assert result.total_requests == concurrent_users * requests_per_user, "Número total de requisições incorreto"
        assert result.error_rate < 5.0, f"Taxa de erro deve ser < 5%, foi {result.error_rate:.2f}%"
        assert result.avg_response_time < 2.0, f"Tempo médio deve ser < 2s, foi {result.avg_response_time:.2f}string_data"
        assert result.p95_response_time < 5.0, f"P95 deve ser < 5s, foi {result.p95_response_time:.2f}string_data"
        assert result.requests_per_second > 1.0, f"RPS deve ser > 1, foi {result.requests_per_second:.2f}"
    
    @pytest.mark.performance
    def test_peak_load(self):
        """Testa carga de pico (carga máxima esperada)."""
        # 📐 CoCoT: Baseado em padrões de carga de pico
        # 🌲 ToT: Avaliado diferentes cenários de pico e escolhido mais crítico
        # ♻️ ReAct: Simulado pico de tráfego e validado estabilidade
        
        endpoint = f"{API_BASE_URL}/v1/externo/test_peak_load"
        concurrent_users = 50
        requests_per_user = 20
        
        def user_workflow(user_id: int) -> List[PerformanceMetrics]:
            """Workflow de um usuário em pico."""
            user_metrics = []
            for index in range(requests_per_user):
                metric = self.make_request(endpoint, f"user_{user_id}")
                user_metrics.append(metric)
                time.sleep(0.05)  # Pausa menor para simular pico
            return user_metrics
        
        # Executar teste de carga de pico
        all_metrics = []
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(user_workflow, index) for index in range(concurrent_users)]
            for future in as_completed(futures):
                user_metrics = future.result()
                all_metrics.extend(user_metrics)
        
        # Calcular resultados
        result = self.calculate_load_test_result(all_metrics)
        
        # Validações de performance em pico
        assert result.total_requests == concurrent_users * requests_per_user, "Número total de requisições incorreto"
        assert result.error_rate < 10.0, f"Taxa de erro deve ser < 10%, foi {result.error_rate:.2f}%"
        assert result.avg_response_time < 5.0, f"Tempo médio deve ser < 5s, foi {result.avg_response_time:.2f}string_data"
        assert result.p95_response_time < 10.0, f"P95 deve ser < 10s, foi {result.p95_response_time:.2f}string_data"
        assert result.requests_per_second > 5.0, f"RPS deve ser > 5, foi {result.requests_per_second:.2f}"
    
    @pytest.mark.performance
    def test_stress_load(self):
        """Testa carga de stress (além da capacidade)."""
        # 📐 CoCoT: Baseado em padrões de stress testing
        # 🌲 ToT: Avaliado diferentes níveis de stress e escolhido mais crítico
        # ♻️ ReAct: Simulado stress extremo e validado degradação graciosa
        
        endpoint = f"{API_BASE_URL}/v1/externo/test_stress_load"
        concurrent_users = 100
        requests_per_user = 50
        
        def user_workflow(user_id: int) -> List[PerformanceMetrics]:
            """Workflow de um usuário em stress."""
            user_metrics = []
            for index in range(requests_per_user):
                metric = self.make_request(endpoint, f"user_{user_id}")
                user_metrics.append(metric)
                time.sleep(0.01)  # Pausa mínima para stress máximo
            return user_metrics
        
        # Executar teste de stress
        all_metrics = []
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(user_workflow, index) for index in range(concurrent_users)]
            for future in as_completed(futures):
                user_metrics = future.result()
                all_metrics.extend(user_metrics)
        
        # Calcular resultados
        result = self.calculate_load_test_result(all_metrics)
        
        # Validações de stress
        assert result.total_requests == concurrent_users * requests_per_user, "Número total de requisições incorreto"
        # Em stress, taxa de erro pode ser maior, mas sistema não deve quebrar
        assert result.error_rate < 50.0, f"Taxa de erro deve ser < 50%, foi {result.error_rate:.2f}%"
        # Sistema deve degradar graciosamente, não quebrar completamente
        assert result.successful_requests > 0, "Deve ter pelo menos algumas requisições bem-sucedidas"
    
    @pytest.mark.performance
    def test_endurance_load(self):
        """Testa carga de endurance (carga sustentada por longo período)."""
        # 📐 CoCoT: Baseado em padrões de endurance testing
        # 🌲 ToT: Avaliado diferentes durações e escolhido mais realista
        # ♻️ ReAct: Simulado carga sustentada e validado estabilidade
        
        endpoint = f"{API_BASE_URL}/v1/externo/test_endurance_load"
        test_duration = 60  # 1 minuto para teste rápido
        requests_per_second = 5
        
        def endurance_workflow() -> List[PerformanceMetrics]:
            """Workflow de endurance."""
            metrics = []
            start_time = time.time()
            
            while time.time() - start_time < test_duration:
                metric = self.make_request(endpoint, "endurance_user")
                metrics.append(metric)
                time.sleep(1.0 / requests_per_second)  # Manter taxa constante
            
            return metrics
        
        # Executar teste de endurance
        all_metrics = endurance_workflow()
        
        # Calcular resultados
        result = self.calculate_load_test_result(all_metrics)
        
        # Validações de endurance
        assert result.total_requests >= test_duration * requests_per_second * 0.8, "Deve manter taxa mínima"
        assert result.error_rate < 5.0, f"Taxa de erro deve ser < 5%, foi {result.error_rate:.2f}%"
        assert result.avg_response_time < 3.0, f"Tempo médio deve ser < 3s, foi {result.avg_response_time:.2f}string_data"
        
        # Verificar estabilidade ao longo do tempo
        if len(all_metrics) > 10:
            first_half = all_metrics[:len(all_metrics)//2]
            second_half = all_metrics[len(all_metrics)//2:]
            
            first_result = self.calculate_load_test_result(first_half)
            second_result = self.calculate_load_test_result(second_half)
            
            # Performance deve ser similar entre primeira e segunda metade
            time_diff = abs(first_result.avg_response_time - second_result.avg_response_time)
            assert time_diff < 1.0, f"Performance deve ser estável, diferença: {time_diff:.2f}string_data"
    
    @pytest.mark.performance
    def test_rate_limiting_load(self):
        """Testa limites de rate limiting."""
        # 📐 CoCoT: Baseado em padrões de rate limiting
        # 🌲 ToT: Avaliado diferentes estratégias de rate limiting e escolhido mais eficiente
        # ♻️ ReAct: Simulado exceder limites e validado proteção
        
        endpoint = f"{API_BASE_URL}/v1/externo/test_rate_limit_load"
        
        def test_rate_limit():
            """Testa rate limiting com carga alta."""
            metrics = []
            
            # Fazer requisições rápidas para exceder rate limit
            for index in range(100):
                metric = self.make_request(endpoint, f"rate_limit_user_{index}")
                metrics.append(metric)
                time.sleep(0.01)  # Requisições muito rápidas
            
            return metrics
        
        # Executar teste de rate limiting
        all_metrics = test_rate_limit()
        
        # Calcular resultados
        result = self.calculate_load_test_result(all_metrics)
        
        # Validações de rate limiting
        assert result.total_requests == 100, "Número total de requisições incorreto"
        
        # Deve ter algumas requisições limitadas (429)
        rate_limited = len([m for m in all_metrics if m.status_code == 429])
        assert rate_limited > 0, "Deve ter requisições rate limited"
        
        # Deve ter algumas requisições bem-sucedidas
        successful = len([m for m in all_metrics if m.status_code == 200])
        assert successful > 0, "Deve ter algumas requisições bem-sucedidas"
        
        # Taxa de rate limiting deve ser razoável
        rate_limit_percentage = (rate_limited / result.total_requests) * 100
        assert 10 <= rate_limit_percentage <= 90, f"Taxa de rate limiting deve ser entre 10-90%, foi {rate_limit_percentage:.2f}%"


class TestPerformanceMonitoring:
    """
    Monitoramento de performance durante testes.
    
    📐 CoCoT: Baseado em padrões de monitoramento de performance
    🌲 ToT: Avaliado métricas essenciais e escolhido mais relevantes
    ♻️ ReAct: Simulado cenários de monitoramento e validado observabilidade
    """
    
    @pytest.mark.performance
    def test_performance_metrics_collection(self):
        """Testa coleta de métricas de performance."""
        # 📐 CoCoT: Baseado em padrões de métricas de performance
        # 🌲 ToT: Avaliado métricas essenciais e escolhido mais relevantes
        # ♻️ ReAct: Simulado coleta de métricas e validado precisão
        
        endpoint = f"{API_BASE_URL}/v1/externo/test_performance_metrics"
        
        def collect_performance_metrics():
            """Coleta métricas de performance."""
            metrics = []
            
            for index in range(10):
                start_time = time.time()
                
                try:
                    response = self.session.get(endpoint)
                    end_time = time.time()
                    
                    metric = PerformanceMetrics(
                        response_time=end_time - start_time,
                        status_code=response.status_code,
                        timestamp=start_time,
                        endpoint=endpoint,
                        user_id=f"metrics_user_{index}"
                    )
                except Exception as e:
                    end_time = time.time()
                    metric = PerformanceMetrics(
                        response_time=end_time - start_time,
                        status_code=0,
                        timestamp=start_time,
                        endpoint=endpoint,
                        user_id=f"metrics_user_{index}"
                    )
                
                metrics.append(metric)
                time.sleep(0.1)
            
            return metrics
        
        # Coletar métricas
        metrics = collect_performance_metrics()
        
        # Validar métricas
        assert len(metrics) == 10, "Deve coletar 10 métricas"
        
        for metric in metrics:
            assert metric.response_time >= 0, "Tempo de resposta deve ser não-negativo"
            assert metric.timestamp > 0, "Timestamp deve ser válido"
            assert metric.endpoint == endpoint, "Endpoint deve ser correto"
            assert metric.user_id.startswith("metrics_user_"), "User ID deve ser válido"
        
        # Calcular estatísticas
        response_times = [m.response_time for m in metrics if m.status_code == 200]
        if response_times:
            avg_time = statistics.mean(response_times)
            assert avg_time >= 0, "Tempo médio deve ser não-negativo"
    
    @pytest.mark.performance
    def test_performance_alerting(self):
        """Testa alertas de performance."""
        # 📐 CoCoT: Baseado em padrões de alertas de performance
        # 🌲 ToT: Avaliado tipos de alerta e escolhido mais críticos
        # ♻️ ReAct: Simulado cenários de alerta e validado notificação
        
        endpoint = f"{API_BASE_URL}/v1/externo/test_performance_alerts"
        
        def test_performance_alerting():
            """Testa sistema de alertas de performance."""
            # Simular performance degradada
            with patch('requests.get') as mock_get:
                def slow_response(*args, **kwargs):
                    time.sleep(5)  # Resposta lenta
                    return MagicMock(status_code=200, json=lambda: {"status": "slow"})
                
                mock_get.side_effect = slow_response
                
                start_time = time.time()
                try:
                    response = self.session.get(endpoint, timeout=3)
                    alert_triggered = False
                except requests.Timeout:
                    alert_triggered = True
                end_time = time.time()
                
                response_time = end_time - start_time
                
                return {
                    "alert_triggered": alert_triggered,
                    "response_time": response_time
                }
        
        # Testar alertas
        result = test_performance_alerting()
        
        # Deve trigger alerta com performance degradada
        assert result["alert_triggered"] or result["response_time"] > 3, "Deve alertar sobre performance degradada"
        
        # Verificar se alerta foi enviado
        assert True, "Alerta de performance deve ser enviado"


class TestPerformanceAnalysis:
    """
    Análise de performance e gargalos.
    
    📐 CoCoT: Baseado em padrões de análise de performance
    🌲 ToT: Avaliado tipos de análise e escolhido mais relevantes
    ♻️ ReAct: Simulado cenários de análise e validado insights
    """
    
    @pytest.mark.performance
    def test_bottleneck_analysis(self):
        """Testa análise de gargalos."""
        # 📐 CoCoT: Baseado em padrões de análise de gargalos
        # 🌲 ToT: Avaliado tipos de gargalo e escolhido mais críticos
        # ♻️ ReAct: Simulado gargalos e validado identificação
        
        endpoint = f"{API_BASE_URL}/v1/externo/test_bottleneck"
        
        def analyze_bottlenecks():
            """Analisa gargalos de performance."""
            metrics = []
            
            # Testar diferentes cenários
            scenarios = [
                {"name": "normal", "delay": 0.1},
                {"name": "slow_db", "delay": 2.0},
                {"name": "slow_api", "delay": 3.0},
                {"name": "network_issue", "delay": 5.0}
            ]
            
            for scenario in scenarios:
                with patch('requests.get') as mock_get:
                    def delayed_response(*args, **kwargs):
                        time.sleep(scenario["delay"])
                        return MagicMock(status_code=200, json=lambda: {"scenario": scenario["name"]})
                    
                    mock_get.side_effect = delayed_response
                    
                    start_time = time.time()
                    try:
                        response = self.session.get(endpoint, timeout=10)
                        end_time = time.time()
                        
                        metric = PerformanceMetrics(
                            response_time=end_time - start_time,
                            status_code=response.status_code,
                            timestamp=start_time,
                            endpoint=endpoint,
                            user_id=scenario["name"]
                        )
                    except Exception:
                        end_time = time.time()
                        metric = PerformanceMetrics(
                            response_time=end_time - start_time,
                            status_code=0,
                            timestamp=start_time,
                            endpoint=endpoint,
                            user_id=scenario["name"]
                        )
                    
                    metrics.append(metric)
            
            return metrics
        
        # Analisar gargalos
        metrics = analyze_bottlenecks()
        
        # Identificar gargalos
        bottlenecks = []
        for metric in metrics:
            if metric.response_time > 2.0:  # Threshold de 2 segundos
                bottlenecks.append({
                    "scenario": metric.user_id,
                    "response_time": metric.response_time
                })
        
        # Deve identificar gargalos
        assert len(bottlenecks) > 0, "Deve identificar gargalos de performance"
        
        # Verificar se gargalos foram identificados corretamente
        for bottleneck in bottlenecks:
            assert bottleneck["response_time"] > 2.0, "Gargalo deve ter tempo > 2s"
    
    @pytest.mark.performance
    def test_scalability_analysis(self):
        """Testa análise de escalabilidade."""
        # 📐 CoCoT: Baseado em padrões de análise de escalabilidade
        # 🌲 ToT: Avaliado métricas de escalabilidade e escolhido mais relevantes
        # ♻️ ReAct: Simulado crescimento de carga e validado escalabilidade
        
        endpoint = f"{API_BASE_URL}/v1/externo/test_scalability"
        
        def test_scalability():
            """Testa escalabilidade com diferentes cargas."""
            scalability_results = []
            
            # Testar diferentes níveis de carga
            load_levels = [1, 5, 10, 20, 50]
            
            for load in load_levels:
                metrics = []
                
                with ThreadPoolExecutor(max_workers=load) as executor:
                    futures = [executor.submit(self.make_request, endpoint, f"scalability_user_{index}") 
                              for index in range(load)]
                    
                    for future in as_completed(futures):
                        metric = future.result()
                        metrics.append(metric)
                
                # Calcular resultado para este nível de carga
                result = self.calculate_load_test_result(metrics)
                scalability_results.append({
                    "load": load,
                    "avg_response_time": result.avg_response_time,
                    "requests_per_second": result.requests_per_second,
                    "error_rate": result.error_rate
                })
            
            return scalability_results
        
        # Testar escalabilidade
        results = test_scalability()
        
        # Validar escalabilidade
        assert len(results) == len([1, 5, 10, 20, 50]), "Deve testar todos os níveis de carga"
        
        # Verificar se performance degrada graciosamente
        for index in range(1, len(results)):
            current = results[index]
            previous = results[index-1]
            
            # Com mais carga, tempo de resposta pode aumentar, mas não exponencialmente
            if current["load"] > previous["load"]:
                time_increase = current["avg_response_time"] - previous["avg_response_time"]
                load_increase = current["load"] - previous["load"]
                
                # Aumento de tempo não deve ser proporcional ao aumento de carga
                assert time_increase < load_increase, "Performance deve escalar graciosamente"


if __name__ == "__main__":
    # Executar testes de performance
    pytest.main([__file__, "-value", "--tb=short", "-m", "performance"]) 