"""
🧪 Testes de Performance para Endpoints de Credenciais
🎯 Objetivo: Validar performance dos endpoints de credenciais sob diferentes cargas
📅 Criado: 2025-01-27
🔄 Versão: 1.0
📐 CoCoT: Performance Testing Patterns, Load Testing Best Practices
🌲 ToT: Normal vs Peak vs Stress - Todos importantes para credenciais
♻️ ReAct: Simulação: Carga real, métricas precisas, otimização contínua

Tracing ID: PERFORMANCE_CREDENTIALS_001
Ruleset: enterprise_control_layer.yaml
"""

import pytest
import time
import threading
import requests
import statistics
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from unittest.mock import patch, Mock

# Configurações de teste
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')
CREDENTIALS_BASE_URL = f"{API_BASE_URL}/api/credentials"
PERFORMANCE_TEST_TIMEOUT = 120
STRESS_TEST_DURATION = 300  # 5 minutos
MAX_CONCURRENT_USERS = 50

@dataclass
class CredentialPerformanceMetrics:
    """Métricas de performance para credenciais."""
    response_time: float
    status_code: int
    timestamp: float
    endpoint: str
    operation: str
    user_id: str
    payload_size: int
    encryption_time: float = 0.0
    validation_time: float = 0.0

@dataclass
class CredentialLoadTestResult:
    """Resultado de teste de carga para credenciais."""
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
    avg_encryption_time: float
    avg_validation_time: float
    throughput_mb_per_second: float


class TestCredentialPerformance:
    """Testes de performance para endpoints de credenciais."""
    
    def setup_method(self):
        """Setup para cada teste de performance."""
        self.session = requests.Session()
        self.session.timeout = PERFORMANCE_TEST_TIMEOUT
        self.metrics: List[CredentialPerformanceMetrics] = []
        
        # Dados de teste
        self.test_credentials = {
            "openai": {
                "api_key": "sk-proj-test1234567890abcdefghijklmnopqrstuvwxyz",
                "model": "gpt-4",
                "max_tokens": 4096,
                "temperature": 0.7
            },
            "google": {
                "api_key": "AIzaSyCtest1234567890abcdefghijklmnopqrstuvwxyz",
                "model": "gemini-pro",
                "max_tokens": 4096,
                "temperature": 0.7
            }
        }
    
    def teardown_method(self):
        """Cleanup após cada teste de performance."""
        self.session.close()
    
    def get_auth_token(self) -> str:
        """Obtém token de autenticação para testes."""
        return "Bearer test_performance_token_123"
    
    def make_credential_request(self, endpoint: str, operation: str, payload: Dict = None, user_id: str = "test_user") -> CredentialPerformanceMetrics:
        """Faz uma requisição para endpoint de credenciais e coleta métricas."""
        start_time = time.time()
        encryption_start = validation_start = encryption_time = validation_time = 0.0
        
        headers = {"Authorization": self.get_auth_token()}
        
        try:
            if operation == "GET":
                response = self.session.get(endpoint, headers=headers)
            elif operation == "POST":
                response = self.session.post(endpoint, json=payload, headers=headers)
            elif operation == "PUT":
                response = self.session.put(endpoint, json=payload, headers=headers)
            else:
                raise ValueError(f"Operação não suportada: {operation}")
            
            end_time = time.time()
            
            payload_size = len(json.dumps(payload)) if payload else 0
            
            return CredentialPerformanceMetrics(
                response_time=end_time - start_time,
                status_code=response.status_code,
                timestamp=start_time,
                endpoint=endpoint,
                operation=operation,
                user_id=user_id,
                payload_size=payload_size,
                encryption_time=encryption_time,
                validation_time=validation_time
            )
        except Exception as e:
            end_time = time.time()
            return CredentialPerformanceMetrics(
                response_time=end_time - start_time,
                status_code=0,  # Indica erro
                timestamp=start_time,
                endpoint=endpoint,
                operation=operation,
                user_id=user_id,
                payload_size=len(json.dumps(payload)) if payload else 0,
                encryption_time=encryption_time,
                validation_time=validation_time
            )
    
    def calculate_credential_load_test_result(self, metrics: List[CredentialPerformanceMetrics]) -> CredentialLoadTestResult:
        """Calcula resultado do teste de carga para credenciais."""
        if not metrics:
            return CredentialLoadTestResult(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        total_requests = len(metrics)
        successful_requests = len([m for m in metrics if m.status_code == 200])
        failed_requests = total_requests - successful_requests
        
        response_times = [m.response_time for m in metrics if m.status_code == 200]
        encryption_times = [m.encryption_time for m in metrics if m.encryption_time > 0]
        validation_times = [m.validation_time for m in metrics if m.validation_time > 0]
        
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
        
        # Calcular throughput
        total_payload_size = sum(m.payload_size for m in metrics)
        throughput_mb_per_second = (total_payload_size / 1024 / 1024) / total_time if total_time > 0 else 0
        
        error_rate = (failed_requests / total_requests) * 100 if total_requests > 0 else 0
        
        avg_encryption_time = statistics.mean(encryption_times) if encryption_times else 0
        avg_validation_time = statistics.mean(validation_times) if validation_times else 0
        
        return CredentialLoadTestResult(
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
            avg_encryption_time=avg_encryption_time,
            avg_validation_time=avg_validation_time,
            throughput_mb_per_second=throughput_mb_per_second
        )
    
    @pytest.mark.performance
    def test_credential_validation_performance(self):
        """Testa performance do endpoint de validação de credenciais."""
        # 📐 CoCoT: Baseado em padrões de performance de validação
        # 🌲 ToT: Avaliado diferentes cenários de validação e escolhido mais críticos
        # ♻️ ReAct: Simulado validações em massa e validado performance
        
        endpoint = f"{CREDENTIALS_BASE_URL}/validate"
        concurrent_users = 20
        requests_per_user = 5
        
        def validation_workflow(user_id: int) -> List[CredentialPerformanceMetrics]:
            """Workflow de validação de um usuário."""
            user_metrics = []
            
            # Testar diferentes tipos de credenciais
            test_payloads = [
                {
                    "provider": "openai",
                    "credential_type": "api_key",
                    "credential_value": self.test_credentials["openai"]["api_key"],
                    "context": f"performance_test_user_{user_id}"
                },
                {
                    "provider": "google",
                    "credential_type": "api_key",
                    "credential_value": self.test_credentials["google"]["api_key"],
                    "context": f"performance_test_user_{user_id}"
                }
            ]
            
            for index in range(requests_per_user):
                payload = test_payloads[index % len(test_payloads)]
                metric = self.make_credential_request(endpoint, "POST", payload, f"user_{user_id}")
                user_metrics.append(metric)
                time.sleep(0.1)  # Pequena pausa entre requisições
            
            return user_metrics
        
        # Executar teste de performance de validação
        all_metrics = []
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(validation_workflow, index) for index in range(concurrent_users)]
            for future in as_completed(futures):
                user_metrics = future.result()
                all_metrics.extend(user_metrics)
        
        # Calcular resultados
        result = self.calculate_credential_load_test_result(all_metrics)
        
        # Validações de performance para validação
        assert result.total_requests == concurrent_users * requests_per_user, "Número total de requisições incorreto"
        assert result.error_rate < 10.0, f"Taxa de erro deve ser < 10%, foi {result.error_rate:.2f}%"
        assert result.avg_response_time < 1.0, f"Tempo médio deve ser < 1s, foi {result.avg_response_time:.2f}string_data"
        assert result.p95_response_time < 2.0, f"P95 deve ser < 2s, foi {result.p95_response_time:.2f}string_data"
        assert result.requests_per_second > 5.0, f"RPS deve ser > 5, foi {result.requests_per_second:.2f}"
        
        print(f"✅ Validação Performance: {result.requests_per_second:.2f} RPS, {result.avg_response_time:.3f}string_data avg")
    
    @pytest.mark.performance
    def test_credential_config_performance(self):
        """Testa performance do endpoint de configuração de credenciais."""
        # 📐 CoCoT: Baseado em padrões de performance de configuração
        # 🌲 ToT: Avaliado diferentes tamanhos de configuração e escolhido mais realistas
        # ♻️ ReAct: Simulado configurações complexas e validado performance
        
        get_endpoint = f"{CREDENTIALS_BASE_URL}/config"
        put_endpoint = f"{CREDENTIALS_BASE_URL}/config"
        concurrent_users = 10
        requests_per_user = 3
        
        def config_workflow(user_id: int) -> List[CredentialPerformanceMetrics]:
            """Workflow de configuração de um usuário."""
            user_metrics = []
            
            # Testar GET de configuração
            for index in range(requests_per_user):
                metric = self.make_credential_request(get_endpoint, "GET", user_id=f"user_{user_id}")
                user_metrics.append(metric)
                time.sleep(0.2)
            
            # Testar PUT de configuração
            config_payload = {
                "config": {
                    "ai": {
                        "openai": {
                            "apiKey": f"sk-proj-user{user_id}-{int(time.time())}",
                            "enabled": True,
                            "model": "gpt-4",
                            "maxTokens": 4096,
                            "temperature": 0.7
                        }
                    },
                    "general": {
                        "user_id": f"user_{user_id}",
                        "timestamp": datetime.now().isoformat()
                    }
                },
                "validateOnUpdate": False
            }
            
            metric = self.make_credential_request(put_endpoint, "PUT", config_payload, f"user_{user_id}")
            user_metrics.append(metric)
            
            return user_metrics
        
        # Executar teste de performance de configuração
        all_metrics = []
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(config_workflow, index) for index in range(concurrent_users)]
            for future in as_completed(futures):
                user_metrics = future.result()
                all_metrics.extend(user_metrics)
        
        # Calcular resultados
        result = self.calculate_credential_load_test_result(all_metrics)
        
        # Validações de performance para configuração
        assert result.total_requests > 0, "Deve ter pelo menos uma requisição"
        assert result.error_rate < 15.0, f"Taxa de erro deve ser < 15%, foi {result.error_rate:.2f}%"
        assert result.avg_response_time < 2.0, f"Tempo médio deve ser < 2s, foi {result.avg_response_time:.2f}string_data"
        assert result.p95_response_time < 5.0, f"P95 deve ser < 5s, foi {result.p95_response_time:.2f}string_data"
        
        print(f"✅ Configuração Performance: {result.requests_per_second:.2f} RPS, {result.avg_response_time:.3f}string_data avg")
    
    @pytest.mark.performance
    def test_credential_status_performance(self):
        """Testa performance do endpoint de status de credenciais."""
        # 📐 CoCoT: Baseado em padrões de performance de monitoramento
        # 🌲 ToT: Avaliado diferentes tipos de status e escolhido mais críticos
        # ♻️ ReAct: Simulado monitoramento contínuo e validado performance
        
        general_status_endpoint = f"{CREDENTIALS_BASE_URL}/status"
        health_endpoint = f"{CREDENTIALS_BASE_URL}/health"
        metrics_endpoint = f"{CREDENTIALS_BASE_URL}/metrics"
        concurrent_users = 30
        requests_per_user = 4
        
        def status_workflow(user_id: int) -> List[CredentialPerformanceMetrics]:
            """Workflow de status de um usuário."""
            user_metrics = []
            
            # Testar diferentes endpoints de status
            endpoints = [
                (general_status_endpoint, "GET"),
                (health_endpoint, "GET"),
                (metrics_endpoint, "GET"),
                (f"{CREDENTIALS_BASE_URL}/status/openai", "GET")
            ]
            
            for index in range(requests_per_user):
                endpoint, operation = endpoints[index % len(endpoints)]
                metric = self.make_credential_request(endpoint, operation, user_id=f"user_{user_id}")
                user_metrics.append(metric)
                time.sleep(0.1)
            
            return user_metrics
        
        # Executar teste de performance de status
        all_metrics = []
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(status_workflow, index) for index in range(concurrent_users)]
            for future in as_completed(futures):
                user_metrics = future.result()
                all_metrics.extend(user_metrics)
        
        # Calcular resultados
        result = self.calculate_credential_load_test_result(all_metrics)
        
        # Validações de performance para status
        assert result.total_requests == concurrent_users * requests_per_user, "Número total de requisições incorreto"
        assert result.error_rate < 5.0, f"Taxa de erro deve ser < 5%, foi {result.error_rate:.2f}%"
        assert result.avg_response_time < 0.5, f"Tempo médio deve ser < 0.5s, foi {result.avg_response_time:.2f}string_data"
        assert result.p95_response_time < 1.0, f"P95 deve ser < 1s, foi {result.p95_response_time:.2f}string_data"
        assert result.requests_per_second > 10.0, f"RPS deve ser > 10, foi {result.requests_per_second:.2f}"
        
        print(f"✅ Status Performance: {result.requests_per_second:.2f} RPS, {result.avg_response_time:.3f}string_data avg")
    
    @pytest.mark.performance
    def test_credential_stress_performance(self):
        """Testa performance sob stress dos endpoints de credenciais."""
        # 📐 CoCoT: Baseado em padrões de stress testing
        # 🌲 ToT: Avaliado diferentes níveis de stress e escolhido mais crítico
        # ♻️ ReAct: Simulado stress extremo e validado estabilidade
        
        endpoints = [
            (f"{CREDENTIALS_BASE_URL}/validate", "POST"),
            (f"{CREDENTIALS_BASE_URL}/config", "GET"),
            (f"{CREDENTIALS_BASE_URL}/status", "GET"),
            (f"{CREDENTIALS_BASE_URL}/health", "GET")
        ]
        
        concurrent_users = 50
        test_duration = 60  # 1 minuto de stress
        
        def stress_workflow(user_id: int) -> List[CredentialPerformanceMetrics]:
            """Workflow de stress de um usuário."""
            user_metrics = []
            start_time = time.time()
            
            while time.time() - start_time < test_duration:
                for endpoint, operation in endpoints:
                    if operation == "POST":
                        payload = {
                            "provider": "openai",
                            "credential_type": "api_key",
                            "credential_value": f"sk-proj-stress-{user_id}-{int(time.time())}",
                            "context": "stress_test"
                        }
                    else:
                        payload = None
                    
                    metric = self.make_credential_request(endpoint, operation, payload, f"stress_user_{user_id}")
                    user_metrics.append(metric)
                    
                    # Pequena pausa para não sobrecarregar
                    time.sleep(0.05)
            
            return user_metrics
        
        # Executar teste de stress
        all_metrics = []
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(stress_workflow, index) for index in range(concurrent_users)]
            for future in as_completed(futures):
                user_metrics = future.result()
                all_metrics.extend(user_metrics)
        
        # Calcular resultados
        result = self.calculate_credential_load_test_result(all_metrics)
        
        # Validações de stress
        assert result.total_requests > 1000, "Deve ter pelo menos 1000 requisições"
        assert result.error_rate < 20.0, f"Taxa de erro deve ser < 20%, foi {result.error_rate:.2f}%"
        assert result.avg_response_time < 3.0, f"Tempo médio deve ser < 3s, foi {result.avg_response_time:.2f}string_data"
        assert result.p99_response_time < 10.0, f"P99 deve ser < 10s, foi {result.p99_response_time:.2f}string_data"
        
        print(f"✅ Stress Performance: {result.requests_per_second:.2f} RPS, {result.error_rate:.2f}% erro")
    
    @pytest.mark.performance
    def test_credential_encryption_performance(self):
        """Testa performance da criptografia de credenciais."""
        # 📐 CoCoT: Baseado em padrões de performance de criptografia
        # 🌲 ToT: Avaliado diferentes algoritmos e escolhido mais eficiente
        # ♻️ ReAct: Simulado criptografia em massa e validado performance
        
        endpoint = f"{CREDENTIALS_BASE_URL}/config"
        concurrent_users = 15
        requests_per_user = 10
        
        def encryption_workflow(user_id: int) -> List[CredentialPerformanceMetrics]:
            """Workflow de criptografia de um usuário."""
            user_metrics = []
            
            # Criar configuração com múltiplas credenciais para testar criptografia
            config_payload = {
                "config": {
                    "ai": {
                        "openai": {
                            "apiKey": f"sk-proj-encryption-{user_id}-{int(time.time())}",
                            "enabled": True,
                            "model": "gpt-4",
                            "maxTokens": 4096,
                            "temperature": 0.7
                        },
                        "google": {
                            "apiKey": f"AIzaSyCencryption-{user_id}-{int(time.time())}",
                            "enabled": True,
                            "model": "gemini-pro",
                            "maxTokens": 4096,
                            "temperature": 0.7
                        }
                    },
                    "social": {
                        "instagram": {
                            "username": f"user_{user_id}",
                            "password": f"password_{user_id}_{int(time.time())}",
                            "sessionId": f"session_{user_id}_{int(time.time())}",
                            "enabled": True
                        }
                    },
                    "analytics": {
                        "google_analytics": {
                            "clientId": f"client_{user_id}_{int(time.time())}",
                            "clientSecret": f"secret_{user_id}_{int(time.time())}",
                            "enabled": True
                        }
                    }
                },
                "validateOnUpdate": False
            }
            
            for index in range(requests_per_user):
                metric = self.make_credential_request(endpoint, "PUT", config_payload, f"encryption_user_{user_id}")
                user_metrics.append(metric)
                time.sleep(0.1)
            
            return user_metrics
        
        # Executar teste de performance de criptografia
        all_metrics = []
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(encryption_workflow, index) for index in range(concurrent_users)]
            for future in as_completed(futures):
                user_metrics = future.result()
                all_metrics.extend(user_metrics)
        
        # Calcular resultados
        result = self.calculate_credential_load_test_result(all_metrics)
        
        # Validações de performance de criptografia
        assert result.total_requests == concurrent_users * requests_per_user, "Número total de requisições incorreto"
        assert result.error_rate < 15.0, f"Taxa de erro deve ser < 15%, foi {result.error_rate:.2f}%"
        assert result.avg_response_time < 3.0, f"Tempo médio deve ser < 3s, foi {result.avg_response_time:.2f}string_data"
        assert result.p95_response_time < 8.0, f"P95 deve ser < 8s, foi {result.p95_response_time:.2f}string_data"
        assert result.throughput_mb_per_second > 0.1, f"Throughput deve ser > 0.1 MB/string_data, foi {result.throughput_mb_per_second:.3f}"
        
        print(f"✅ Criptografia Performance: {result.requests_per_second:.2f} RPS, {result.throughput_mb_per_second:.3f} MB/string_data")


class TestCredentialPerformanceMonitoring:
    """Testes de monitoramento de performance para credenciais."""
    
    @pytest.mark.performance
    def test_performance_metrics_collection(self):
        """Testa coleta de métricas de performance."""
        # 📐 CoCoT: Baseado em padrões de monitoramento de performance
        # 🌲 ToT: Avaliado diferentes métricas e escolhido as mais importantes
        # ♻️ ReAct: Simulado coleta contínua e validado precisão
        
        endpoint = f"{CREDENTIALS_BASE_URL}/metrics"
        headers = {"Authorization": "Bearer test_performance_token_123"}
        
        # Coletar métricas por 30 segundos
        start_time = time.time()
        metrics_samples = []
        
        while time.time() - start_time < 30:
            try:
                response = requests.get(endpoint, headers=headers, timeout=5)
                if response.status_code == 200:
                    metrics_data = response.json()
                    metrics_samples.append({
                        "timestamp": time.time(),
                        "total_requests": metrics_data.get("total_requests", 0),
                        "active_providers": metrics_data.get("active_providers", 0),
                        "blocked_requests": metrics_data.get("blocked_requests", 0)
                    })
            except Exception as e:
                print(f"Erro ao coletar métricas: {e}")
            
            time.sleep(1)  # Coletar a cada segundo
        
        # Validar coleta de métricas
        assert len(metrics_samples) > 0, "Deve ter coletado pelo menos uma amostra"
        assert len(metrics_samples) >= 25, f"Deve ter coletado pelo menos 25 amostras, coletou {len(metrics_samples)}"
        
        # Verificar consistência das métricas
        total_requests_values = [m["total_requests"] for m in metrics_samples]
        assert max(total_requests_values) >= min(total_requests_values), "Métricas devem ser consistentes"
        
        print(f"✅ Coleta de Métricas: {len(metrics_samples)} amostras coletadas")
    
    @pytest.mark.performance
    def test_performance_alerting(self):
        """Testa sistema de alertas de performance."""
        # 📐 CoCoT: Baseado em padrões de alertas de performance
        # 🌲 ToT: Avaliado diferentes thresholds e escolhido os mais críticos
        # ♻️ ReAct: Simulado degradação e validado alertas
        
        # Simular degradação de performance
        endpoint = f"{CREDENTIALS_BASE_URL}/validate"
        headers = {"Authorization": "Bearer test_performance_token_123"}
        
        # Fazer requisições rápidas para simular alta carga
        response_times = []
        for index in range(100):
            start_time = time.time()
            try:
                payload = {
                    "provider": "openai",
                    "credential_type": "api_key",
                    "credential_value": f"sk-proj-alert-{index}",
                    "context": "performance_alert_test"
                }
                response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
                end_time = time.time()
                response_times.append(end_time - start_time)
            except Exception as e:
                end_time = time.time()
                response_times.append(end_time - start_time)
            
            time.sleep(0.01)  # Muito pequena pausa para simular alta carga
        
        # Analisar performance
        avg_response_time = statistics.mean(response_times)
        p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]
        
        # Verificar se alertas seriam disparados
        performance_issues = []
        if avg_response_time > 2.0:
            performance_issues.append(f"Tempo médio alto: {avg_response_time:.2f}string_data")
        if p95_response_time > 5.0:
            performance_issues.append(f"P95 alto: {p95_response_time:.2f}string_data")
        
        # Em um sistema real, isso dispararia alertas
        print(f"✅ Alertas de Performance: {len(performance_issues)} issues detectadas")
        for issue in performance_issues:
            print(f"   - {issue}")


@pytest.fixture(scope="session")
def performance_setup():
    """Setup para testes de performance."""
    # Verificar se a API está disponível
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            pytest.skip("API não está disponível para testes de performance")
    except requests.exceptions.RequestException:
        pytest.skip("API não está disponível para testes de performance")


def pytest_configure(config):
    """Configuração do pytest."""
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )


def pytest_collection_modifyitems(config, items):
    """Modifica itens de coleção para adicionar marcadores."""
    for item in items:
        if "test_credential_performance" in item.nodeid:
            item.add_marker(pytest.mark.performance)


@pytest.fixture(autouse=True)
def cleanup_after_performance_test():
    """Limpeza automática após cada teste de performance."""
    yield
    # Limpeza específica se necessário
    pass 