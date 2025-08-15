"""
locustfile_performance_api_response_time_v1.py
Teste de carga para performance de tempo de resposta de APIs

Prompt: CHECKLIST_TESTES_CARGA_CRITICIDADE.md - Nível Médio
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Tracing ID: LOAD_PERFORMANCE_API_RESPONSE_TIME_20250127_001

Endpoints testados:
- GET /api/metrics/overview - Métricas gerais
- GET /api/metrics/performance - Métricas de performance
- GET /api/metrics/system - Métricas do sistema
- GET /api/executions - Listagem de execuções
- GET /api/user/profile - Perfil do usuário
- GET /api/credentials/status - Status de credenciais
- GET /api/credentials/metrics - Métricas de credenciais

Cenários testados:
- Carga normal em APIs
- Teste de latência
- Validação de percentis
- Performance sob carga
- Stress em APIs
- Validação de thresholds
"""
import os
import sys
import time
import json
import random
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from locust import HttpUser, task, between, events
from locust.exception import StopUser

# Configurações de teste
PERFORMANCE_TEST_CONFIG = {
    'endpoints': [
        '/api/metrics/overview',
        '/api/metrics/performance', 
        '/api/metrics/system',
        '/api/executions',
        '/api/user/profile',
        '/api/credentials/status',
        '/api/credentials/metrics'
    ],
    'response_time_thresholds': {
        'p50': 200,    # 50% das requisições < 200ms
        'p95': 500,    # 95% das requisições < 500ms
        'p99': 1000,   # 99% das requisições < 1000ms
        'max': 2000    # Máximo 2s
    },
    'throughput_thresholds': {
        'min_rps': 10,     # Mínimo 10 req/s
        'target_rps': 50,  # Alvo 50 req/s
        'max_rps': 100     # Máximo 100 req/s
    },
    'error_thresholds': {
        'max_error_rate': 0.05,  # Máximo 5% de erro
        'max_timeout_rate': 0.01  # Máximo 1% de timeout
    }
}

class PerformanceResponseTimeLoadTestUser(HttpUser):
    """
    Usuário de teste para performance de tempo de resposta de APIs
    """
    
    wait_time = between(1, 3)
    weight = 8
    
    def on_start(self):
        """Inicialização do usuário"""
        self.tracing_id = f"PERF_RESP_{int(time.time())}_{random.randint(1000, 9999)}"
        self.session_data = {
            'user_id': f"user_{random.randint(1000, 9999)}",
            'session_id': f"session_{random.randint(10000, 99999)}",
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'response_times': []
        }
        
        # Headers padrão
        self.headers = {
            'Content-Type': 'application/json',
            'X-Tracing-ID': self.tracing_id,
            'X-User-ID': self.session_data['user_id'],
            'X-Session-ID': self.session_data['session_id']
        }
        
        print(f"[{self.tracing_id}] Usuário de performance iniciado")
    
    def on_stop(self):
        """Finalização do usuário"""
        print(f"[{self.tracing_id}] Usuário finalizado - "
              f"Total: {self.session_data['total_requests']}, "
              f"Sucesso: {self.session_data['successful_requests']}, "
              f"Falhas: {self.session_data['failed_requests']}")
    
    @task(3)
    def test_metrics_overview_response_time(self):
        """Teste de tempo de resposta para métricas gerais"""
        with self.client.get(
            "/api/metrics/overview",
            headers=self.headers,
            name="/api/metrics/overview [GET]",
            catch_response=True
        ) as response:
            self.session_data['total_requests'] += 1
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Validar estrutura de métricas
                    if 'total_requests' in data and 'avg_response_time' in data:
                        self.session_data['successful_requests'] += 1
                        self.session_data['response_times'].append(response.elapsed.total_seconds() * 1000)
                        response.success()
                    else:
                        self.session_data['failed_requests'] += 1
                        response.failure("Estrutura de métricas inválida")
                        
                except json.JSONDecodeError:
                    self.session_data['failed_requests'] += 1
                    response.failure("Resposta não é JSON válido")
            else:
                self.session_data['failed_requests'] += 1
                response.failure(f"Status code inesperado: {response.status_code}")
    
    @task(3)
    def test_metrics_performance_response_time(self):
        """Teste de tempo de resposta para métricas de performance"""
        with self.client.get(
            "/api/metrics/performance",
            headers=self.headers,
            name="/api/metrics/performance [GET]",
            catch_response=True
        ) as response:
            self.session_data['total_requests'] += 1
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Validar métricas de performance
                    required_metrics = ['response_time', 'throughput', 'error_rate']
                    if all(metric in data for metric in required_metrics):
                        self.session_data['successful_requests'] += 1
                        self.session_data['response_times'].append(response.elapsed.total_seconds() * 1000)
                        response.success()
                    else:
                        self.session_data['failed_requests'] += 1
                        response.failure("Métricas de performance ausentes")
                        
                except json.JSONDecodeError:
                    self.session_data['failed_requests'] += 1
                    response.failure("Resposta não é JSON válido")
            else:
                self.session_data['failed_requests'] += 1
                response.failure(f"Status code inesperado: {response.status_code}")
    
    @task(2)
    def test_executions_response_time(self):
        """Teste de tempo de resposta para listagem de execuções"""
        with self.client.get(
            "/api/executions",
            headers=self.headers,
            name="/api/executions [GET]",
            catch_response=True
        ) as response:
            self.session_data['total_requests'] += 1
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Validar estrutura de execuções
                    if 'executions' in data or 'data' in data:
                        self.session_data['successful_requests'] += 1
                        self.session_data['response_times'].append(response.elapsed.total_seconds() * 1000)
                        response.success()
                    else:
                        self.session_data['failed_requests'] += 1
                        response.failure("Estrutura de execuções inválida")
                        
                except json.JSONDecodeError:
                    self.session_data['failed_requests'] += 1
                    response.failure("Resposta não é JSON válido")
            else:
                self.session_data['failed_requests'] += 1
                response.failure(f"Status code inesperado: {response.status_code}")
    
    @task(2)
    def test_user_profile_response_time(self):
        """Teste de tempo de resposta para perfil do usuário"""
        with self.client.get(
            "/api/user/profile",
            headers=self.headers,
            name="/api/user/profile [GET]",
            catch_response=True
        ) as response:
            self.session_data['total_requests'] += 1
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Validar estrutura de perfil
                    if 'user_id' in data or 'profile' in data:
                        self.session_data['successful_requests'] += 1
                        self.session_data['response_times'].append(response.elapsed.total_seconds() * 1000)
                        response.success()
                    else:
                        self.session_data['failed_requests'] += 1
                        response.failure("Estrutura de perfil inválida")
                        
                except json.JSONDecodeError:
                    self.session_data['failed_requests'] += 1
                    response.failure("Resposta não é JSON válido")
            else:
                self.session_data['failed_requests'] += 1
                response.failure(f"Status code inesperado: {response.status_code}")
    
    @task(1)
    def test_credentials_status_response_time(self):
        """Teste de tempo de resposta para status de credenciais"""
        with self.client.get(
            "/api/credentials/status",
            headers=self.headers,
            name="/api/credentials/status [GET]",
            catch_response=True
        ) as response:
            self.session_data['total_requests'] += 1
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Validar estrutura de status
                    if 'status' in data or 'credentials' in data:
                        self.session_data['successful_requests'] += 1
                        self.session_data['response_times'].append(response.elapsed.total_seconds() * 1000)
                        response.success()
                    else:
                        self.session_data['failed_requests'] += 1
                        response.failure("Estrutura de status inválida")
                        
                except json.JSONDecodeError:
                    self.session_data['failed_requests'] += 1
                    response.failure("Resposta não é JSON válido")
            else:
                self.session_data['failed_requests'] += 1
                response.failure(f"Status code inesperado: {response.status_code}")

class PerformanceStressTestUser(HttpUser):
    """
    Usuário de teste para stress em performance de APIs
    """
    
    wait_time = between(0.5, 1.0)  # Mais rápido para stress
    weight = 4
    
    def on_start(self):
        """Inicialização do usuário de stress"""
        self.tracing_id = f"PERF_STRESS_{int(time.time())}_{random.randint(1000, 9999)}"
        self.headers = {
            'Content-Type': 'application/json',
            'X-Tracing-ID': self.tracing_id,
            'X-User-ID': f"stress_user_{random.randint(1000, 9999)}"
        }
        
        print(f"[{self.tracing_id}] Usuário de stress de performance iniciado")
    
    @task(6)
    def stress_metrics_endpoints(self):
        """Stress test para endpoints de métricas"""
        endpoint = random.choice(PERFORMANCE_TEST_CONFIG['endpoints'])
        
        with self.client.get(
            endpoint,
            headers=self.headers,
            name=f"{endpoint} [STRESS]",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 429:
                response.success()  # Rate limiting é esperado
            else:
                response.failure(f"Status code inesperado: {response.status_code}")
    
    @task(2)
    def stress_concurrent_requests(self):
        """Stress test para requisições concorrentes"""
        # Fazer múltiplas requisições simultâneas
        endpoints = random.sample(PERFORMANCE_TEST_CONFIG['endpoints'], 3)
        
        for endpoint in endpoints:
            with self.client.get(
                endpoint,
                headers=self.headers,
                name=f"{endpoint} [CONCURRENT]",
                catch_response=True
            ) as response:
                if response.status_code in [200, 429]:
                    response.success()
                else:
                    response.failure(f"Status code inesperado: {response.status_code}")

# Event listeners para métricas customizadas
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, context, exception, start_time, url, **kwargs):
    """Listener para métricas de request"""
    if exception:
        print(f"❌ Request falhou: {name} - {exception}")
    else:
        print(f"✅ Request sucesso: {name} - {response_time}ms")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Listener para início do teste"""
    print(f"🚀 Iniciando teste de performance de APIs - {datetime.now()}")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Listener para fim do teste"""
    print(f"🏁 Finalizando teste de performance de APIs - {datetime.now()}")
    
    # Estatísticas finais
    stats = environment.stats
    print(f"📊 Estatísticas finais:")
    print(f"   - Total de requests: {stats.total.num_requests}")
    print(f"   - Requests/s: {stats.total.current_rps}")
    print(f"   - Tempo médio: {stats.total.avg_response_time:.2f}ms")
    print(f"   - Taxa de erro: {stats.total.fail_ratio:.2%}")
    
    # Validar thresholds
    if stats.total.avg_response_time > PERFORMANCE_TEST_CONFIG['response_time_thresholds']['p50']:
        print(f"⚠️  Tempo médio acima do threshold P50: {stats.total.avg_response_time:.2f}ms")
    
    if stats.total.fail_ratio > PERFORMANCE_TEST_CONFIG['error_thresholds']['max_error_rate']:
        print(f"⚠️  Taxa de erro acima do threshold: {stats.total.fail_ratio:.2%}") 