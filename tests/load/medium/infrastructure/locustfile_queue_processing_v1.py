"""
locustfile_queue_processing_v1.py
Teste de carga para os endpoints de filas de processamento

Prompt: CHECKLIST_TESTES_CARGA_CRITICIDADE.md - Nível Médio
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Tracing ID: LOAD_QUEUE_PROCESSING_20250127_001

Endpoints testados:
- POST /api/queue/tasks - Submissão de tarefas
- GET /api/queue/status - Status das filas
- GET /api/queue/metrics - Métricas de processamento
- POST /api/queue/batch - Submissão em lote
- GET /api/queue/backlog - Análise de backlog
- DELETE /api/queue/clear - Limpeza de filas

Cenários testados:
- Carga normal em filas
- Submissão de tarefas
- Processamento de lotes
- Análise de backlog
- Performance sob carga
- Stress em filas
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
QUEUE_TEST_CONFIG = {
    'task_types': [
        'keyword_analysis', 'trend_analysis', 'competitor_analysis',
        'report_generation', 'data_export', 'email_notification',
        'webhook_delivery', 'cache_warming', 'backup_creation',
        'log_processing', 'metrics_calculation', 'audit_analysis'
    ],
    'priorities': ['low', 'medium', 'high', 'critical'],
    'batch_sizes': [10, 25, 50, 100],
    'task_data': {
        'keyword_analysis': {
            'keywords': ['marketing digital', 'seo', 'google ads'],
            'depth': random.randint(1, 5),
            'include_competitors': True
        },
        'trend_analysis': {
            'category': random.choice(['tecnologia', 'saude', 'educacao']),
            'timeframe': random.choice(['7d', '30d', '90d']),
            'include_forecast': True
        },
        'report_generation': {
            'report_type': random.choice(['executive', 'detailed', 'technical']),
            'format': random.choice(['pdf', 'excel', 'json']),
            'include_charts': True
        }
    }
}

class QueueProcessingLoadTestUser(HttpUser):
    """
    Usuário de teste para carga em filas de processamento
    """
    
    wait_time = between(2, 5)
    weight = 8
    
    def on_start(self):
        """Inicialização do usuário"""
        self.tracing_id = f"QUEUE_LOAD_{int(time.time())}_{random.randint(1000, 9999)}"
        self.session_data = {
            'user_id': f"user_{random.randint(1000, 9999)}",
            'session_id': f"session_{random.randint(10000, 99999)}",
            'tasks_submitted': 0,
            'batches_submitted': 0,
            'total_requests': 0
        }
        
        # Headers padrão
        self.headers = {
            'Content-Type': 'application/json',
            'X-Tracing-ID': self.tracing_id,
            'X-User-ID': self.session_data['user_id'],
            'X-Session-ID': self.session_data['session_id']
        }
        
        print(f"[{self.tracing_id}] Usuário de filas iniciado")
    
    def on_stop(self):
        """Finalização do usuário"""
        print(f"[{self.tracing_id}] Usuário finalizado - "
              f"Total: {self.session_data['total_requests']}, "
              f"Tarefas: {self.session_data['tasks_submitted']}, "
              f"Lotes: {self.session_data['batches_submitted']}")
    
    @task(4)
    def test_queue_task_submission(self):
        """Teste de submissão de tarefas"""
        task_type = random.choice(QUEUE_TEST_CONFIG['task_types'])
        priority = random.choice(QUEUE_TEST_CONFIG['priorities'])
        
        # Gerar dados da tarefa
        task_data = QUEUE_TEST_CONFIG['task_data'].get(task_type, {})
        if not task_data:
            task_data = {
                'parameters': {'test': True},
                'metadata': {'source': 'load_test'}
            }
        
        payload = {
            'task_id': str(uuid.uuid4()),
            'task_type': task_type,
            'priority': priority,
            'data': task_data,
            'user_id': self.session_data['user_id'],
            'scheduled_at': datetime.now().isoformat(),
            'timeout': random.randint(300, 1800),  # 5-30 minutos
            'retries': random.randint(0, 3)
        }
        
        with self.client.post(
            "/api/queue/tasks",
            json=payload,
            headers=self.headers,
            name="/api/queue/tasks [POST]",
            catch_response=True
        ) as response:
            self.session_data['total_requests'] += 1
            
            if response.status_code == 202:
                try:
                    data = response.json()
                    
                    # Validar resposta de submissão
                    if 'task_id' in data and 'status' in data:
                        self.session_data['tasks_submitted'] += 1
                        response.success()
                    else:
                        response.failure("Resposta de submissão inválida")
                        
                except json.JSONDecodeError:
                    response.failure("Resposta não é JSON válido")
                    
            elif response.status_code == 429:
                response.success()  # Rate limiting é esperado
            else:
                response.failure(f"Status code inesperado: {response.status_code}")
    
    @task(2)
    def test_queue_status_get(self):
        """Teste de status das filas"""
        with self.client.get(
            "/api/queue/status",
            headers=self.headers,
            name="/api/queue/status [GET]",
            catch_response=True
        ) as response:
            self.session_data['total_requests'] += 1
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Validar estrutura de status
                    required_fields = ['total_tasks', 'pending_tasks', 'processing_tasks', 'completed_tasks']
                    if all(field in data for field in required_fields):
                        response.success()
                    else:
                        response.failure("Campos de status ausentes")
                        
                except json.JSONDecodeError:
                    response.failure("Resposta não é JSON válido")
            else:
                response.failure(f"Status code inesperado: {response.status_code}")
    
    @task(2)
    def test_queue_metrics_get(self):
        """Teste de métricas de processamento"""
        with self.client.get(
            "/api/queue/metrics",
            headers=self.headers,
            name="/api/queue/metrics [GET]",
            catch_response=True
        ) as response:
            self.session_data['total_requests'] += 1
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Validar métricas essenciais
                    required_metrics = ['throughput', 'avg_processing_time', 'error_rate', 'queue_depth']
                    if all(metric in data for metric in required_metrics):
                        response.success()
                    else:
                        response.failure("Métricas essenciais ausentes")
                        
                except json.JSONDecodeError:
                    response.failure("Resposta não é JSON válido")
            else:
                response.failure(f"Status code inesperado: {response.status_code}")
    
    @task(1)
    def test_queue_batch_submission(self):
        """Teste de submissão em lote"""
        batch_size = random.choice(QUEUE_TEST_CONFIG['batch_sizes'])
        task_type = random.choice(QUEUE_TEST_CONFIG['task_types'])
        
        # Gerar lote de tarefas
        tasks = []
        for i in range(batch_size):
            task_data = QUEUE_TEST_CONFIG['task_data'].get(task_type, {})
            if not task_data:
                task_data = {
                    'parameters': {'batch_index': i, 'test': True},
                    'metadata': {'source': 'load_test_batch'}
                }
            
            task = {
                'task_id': str(uuid.uuid4()),
                'task_type': task_type,
                'priority': random.choice(QUEUE_TEST_CONFIG['priorities']),
                'data': task_data,
                'user_id': self.session_data['user_id']
            }
            tasks.append(task)
        
        payload = {
            'batch_id': str(uuid.uuid4()),
            'tasks': tasks,
            'priority': random.choice(QUEUE_TEST_CONFIG['priorities']),
            'user_id': self.session_data['user_id'],
            'metadata': {
                'source': 'load_test',
                'batch_size': batch_size,
                'created_at': datetime.now().isoformat()
            }
        }
        
        with self.client.post(
            "/api/queue/batch",
            json=payload,
            headers=self.headers,
            name="/api/queue/batch [POST]",
            catch_response=True
        ) as response:
            self.session_data['total_requests'] += 1
            
            if response.status_code == 202:
                try:
                    data = response.json()
                    
                    # Validar resposta de lote
                    if 'batch_id' in data and 'tasks_submitted' in data:
                        self.session_data['batches_submitted'] += 1
                        response.success()
                    else:
                        response.failure("Resposta de lote inválida")
                        
                except json.JSONDecodeError:
                    response.failure("Resposta não é JSON válido")
                    
            elif response.status_code == 429:
                response.success()  # Rate limiting é esperado
            else:
                response.failure(f"Status code inesperado: {response.status_code}")
    
    @task(1)
    def test_queue_backlog_get(self):
        """Teste de análise de backlog"""
        with self.client.get(
            "/api/queue/backlog",
            headers=self.headers,
            name="/api/queue/backlog [GET]",
            catch_response=True
        ) as response:
            self.session_data['total_requests'] += 1
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Validar estrutura de backlog
                    if 'backlog_size' in data and 'oldest_task' in data:
                        response.success()
                    else:
                        response.failure("Estrutura de backlog inválida")
                        
                except json.JSONDecodeError:
                    response.failure("Resposta não é JSON válido")
            else:
                response.failure(f"Status code inesperado: {response.status_code}")

class QueueStressTestUser(HttpUser):
    """
    Usuário de teste para stress em filas de processamento
    """
    
    wait_time = between(0.5, 1.0)  # Mais rápido para stress
    weight = 4
    
    def on_start(self):
        """Inicialização do usuário de stress"""
        self.tracing_id = f"QUEUE_STRESS_{int(time.time())}_{random.randint(1000, 9999)}"
        self.headers = {
            'Content-Type': 'application/json',
            'X-Tracing-ID': self.tracing_id,
            'X-User-ID': f"stress_user_{random.randint(1000, 9999)}"
        }
        
        print(f"[{self.tracing_id}] Usuário de stress de filas iniciado")
    
    @task(6)
    def stress_queue_task_submission(self):
        """Stress test para submissão de tarefas"""
        task_type = random.choice(QUEUE_TEST_CONFIG['task_types'])
        
        payload = {
            'task_id': str(uuid.uuid4()),
            'task_type': task_type,
            'priority': 'low',
            'data': {'stress_test': True, 'timestamp': time.time()},
            'user_id': f"stress_user_{random.randint(1000, 9999)}",
            'timeout': 60,
            'retries': 0
        }
        
        with self.client.post(
            "/api/queue/tasks",
            json=payload,
            headers=self.headers,
            name="/api/queue/tasks [STRESS]",
            catch_response=True
        ) as response:
            if response.status_code in [202, 429]:
                response.success()
            else:
                response.failure(f"Status code inesperado: {response.status_code}")
    
    @task(2)
    def stress_queue_status(self):
        """Stress test para status das filas"""
        with self.client.get(
            "/api/queue/status",
            headers=self.headers,
            name="/api/queue/status [STRESS]",
            catch_response=True
        ) as response:
            if response.status_code == 200:
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
    print(f"🚀 Iniciando teste de carga de filas - {datetime.now()}")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Listener para fim do teste"""
    print(f"🏁 Finalizando teste de carga de filas - {datetime.now()}")
    
    # Estatísticas finais
    stats = environment.stats
    print(f"📊 Estatísticas finais:")
    print(f"   - Total de requests: {stats.total.num_requests}")
    print(f"   - Requests/s: {stats.total.current_rps}")
    print(f"   - Tempo médio: {stats.total.avg_response_time:.2f}ms")
    print(f"   - Taxa de erro: {stats.total.fail_ratio:.2%}") 