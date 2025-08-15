"""
locustfile_performance_api_throughput_v1.py
Teste de carga para performance de throughput de APIs

Prompt: CHECKLIST_TESTES_CARGA_CRITICIDADE.md - Nível Médio
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Tracing ID: LOAD_PERFORMANCE_API_THROUGHPUT_20250127_001

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
- Teste de throughput
- Validação de RPS
- Performance sob carga
- Stress em APIs
- Validação de limites
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
THROUGHPUT_TEST_CONFIG = {
    'endpoints': [
        '/api/metrics/overview',
        '/api/metrics/performance', 
        '/api/metrics/system',
        '/api/executions',
        '/api/user/profile',
        '/api/credentials/status',
        '/api/credentials/metrics'
    ],
    'throughput_targets': {
        'min_rps': 10,     # Mínimo 10 req/s
        'target_rps': 50,  # Alvo 50 req/s
        'max_rps': 100,    # Máximo 100 req/s
        'burst_rps': 200   # Pico 200 req/s
    },
    'concurrency_levels': {
        'low': 10,         # Baixa concorrência
        'medium': 50,      # Média concorrência
        'high': 100,       # Alta concorrência
        'extreme': 200     # Concorrência extrema
    },
    'test_durations': {
        'short': '1m',     # Teste curto
        'medium': '5m',    # Teste médio
        'long': '15m'      # Teste longo
    }
}

class PerformanceThroughputLoadTestUser(HttpUser):
    """
    Usuário de teste para performance de throughput de APIs
    """
    
    wait_time = between(0.5, 2.0)  # Mais rápido para throughput
    weight = 8
    
    def on_start(self):
        """Inicialização do usuário"""
        self.tracing_id = f"PERF_THROUGHPUT_{int(time.time())}_{random.randint(1000, 9999)}"
        self.session_data = {
            'user_id': f"user_{random.randint(1000, 9999)}",
            'session_id': f"session_{random.randint(10000, 99999)}",
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'start_time': time.time()
        }
        
        # Headers padrão
        self.headers = {
            'Content-Type': 'application/json',
            'X-Tracing-ID': self.tracing_id,
            'X-User-ID': self.session_data['user_id'],
            'X-Session-ID': self.session_data['session_id']
        }
        
        print(f"[{self.tracing_id}] Usuário de throughput iniciado")
    
    def on_stop(self):
        """Finalização do usuário"""
        end_time = time.time()
        duration = end_time - self.session_data['start_time']
        rps = self.session_data['total_requests'] / duration if duration > 0 else 0
        
        print(f"[{self.tracing_id}] Usuário finalizado - "
              f"Total: {self.session_data['total_requests']}, "
              f"Sucesso: {self.session_data['successful_requests']}, "
              f"Falhas: {self.session_data['failed_requests']}, "
              f"RPS: {rps:.2f}")
    
    @task(4)
    def test_metrics_overview_throughput(self):
        """Teste de throughput para métricas gerais"""
        with self.client.get(
            "/api/metrics/overview",
            headers=self.headers,
            name="/api/metrics/overview [THROUGHPUT]",
            catch_response=True
        ) as response:
            self.session_data['total_requests'] += 1
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Validar estrutura de métricas
                    if 'total_requests' in data and 'avg_response_time' in data:
                        self.session_data['successful_requests'] += 1
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
    
    @task(4)
    def test_metrics_performance_throughput(self):
        """Teste de throughput para métricas de performance"""
        with self.client.get(
            "/api/metrics/performance",
            headers=self.headers,
            name="/api/metrics/performance [THROUGHPUT]",
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
    
    @task(3)
    def test_executions_throughput(self):
        """Teste de throughput para listagem de execuções"""
        with self.client.get(
            "/api/executions",
            headers=self.headers,
            name="/api/executions [THROUGHPUT]",
            catch_response=True
        ) as response:
            self.session_data['total_requests'] += 1
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Validar estrutura de execuções
                    if 'executions' in data or 'data' in data:
                        self.session_data['successful_requests'] += 1
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
    def test_user_profile_throughput(self):
        """Teste de throughput para perfil do usuário"""
        with self.client.get(
            "/api/user/profile",
            headers=self.headers,
            name="/api/user/profile [THROUGHPUT]",
            catch_response=True
        ) as response:
            self.session_data['total_requests'] += 1
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Validar estrutura de perfil
                    if 'user_id' in data or 'profile' in data:
                        self.session_data['successful_requests'] += 1
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
    def test_credentials_status_throughput(self):
        """Teste de throughput para status de credenciais"""
        with self.client.get(
            "/api/credentials/status",
            headers=self.headers,
            name="/api/credentials/status [THROUGHPUT]",
            catch_response=True
        ) as response:
            self.session_data['total_requests'] += 1
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Validar estrutura de status
                    if 'status' in data or 'credentials' in data:
                        self.session_data['successful_requests'] += 1
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

class PerformanceBurstTestUser(HttpUser):
    """
    Usuário de teste para burst de throughput
    """
    
    wait_time = between(0.1, 0.5)  # Muito rápido para burst
    weight = 4
    
    def on_start(self):
        """Inicialização do usuário de burst"""
        self.tracing_id = f"PERF_BURST_{int(time.time())}_{random.randint(1000, 9999)}"
        self.headers = {
            'Content-Type': 'application/json',
            'X-Tracing-ID': self.tracing_id,
            'X-User-ID': f"burst_user_{random.randint(1000, 9999)}"
        }
        
        print(f"[{self.tracing_id}] Usuário de burst iniciado")
    
    @task(8)
    def burst_metrics_endpoints(self):
        """Burst test para endpoints de métricas"""
        endpoint = random.choice(THROUGHPUT_TEST_CONFIG['endpoints'])
        
        with self.client.get(
            endpoint,
            headers=self.headers,
            name=f"{endpoint} [BURST]",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 429:
                response.success()  # Rate limiting é esperado
            else:
                response.failure(f"Status code inesperado: {response.status_code}")
    
    @task(2)
    def burst_concurrent_requests(self):
        """Burst test para requisições concorrentes"""
        # Fazer múltiplas requisições simultâneas
        endpoints = random.sample(THROUGHPUT_TEST_CONFIG['endpoints'], 5)
        
        for endpoint in endpoints:
            with self.client.get(
                endpoint,
                headers=self.headers,
                name=f"{endpoint} [CONCURRENT_BURST]",
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
    print(f"🚀 Iniciando teste de throughput de APIs - {datetime.now()}")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Listener para fim do teste"""
    print(f"🏁 Finalizando teste de throughput de APIs - {datetime.now()}")
    
    # Estatísticas finais
    stats = environment.stats
    print(f"📊 Estatísticas finais:")
    print(f"   - Total de requests: {stats.total.num_requests}")
    print(f"   - Requests/s: {stats.total.current_rps}")
    print(f"   - Tempo médio: {stats.total.avg_response_time:.2f}ms")
    print(f"   - Taxa de erro: {stats.total.fail_ratio:.2%}")
    
    # Validar throughput
    if stats.total.current_rps < THROUGHPUT_TEST_CONFIG['throughput_targets']['min_rps']:
        print(f"⚠️  Throughput abaixo do mínimo: {stats.total.current_rps:.2f} RPS")
    
    if stats.total.current_rps > THROUGHPUT_TEST_CONFIG['throughput_targets']['max_rps']:
        print(f"⚠️  Throughput acima do máximo: {stats.total.current_rps:.2f} RPS") 