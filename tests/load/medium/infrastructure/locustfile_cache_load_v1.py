"""
locustfile_cache_load_v1.py
Teste de carga para os endpoints de cache

Prompt: CHECKLIST_TESTES_CARGA_CRITICIDADE.md - Nível Médio
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Tracing ID: LOAD_CACHE_20250127_001

Endpoints testados:
- GET /api/cache/keywords - Busca de keywords no cache
- GET /api/cache/metrics - Métricas de cache
- GET /api/cache/trends - Tendências no cache
- POST /api/cache/warm - Cache warming
- DELETE /api/cache/invalidate - Invalidação de cache
- GET /api/cache/stats - Estatísticas de cache

Cenários testados:
- Carga normal no cache
- Cache miss scenarios
- Evicção de cache
- Cache warming
- Invalidação de cache
- Performance sob carga
"""
import os
import sys
import time
import json
import random
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from locust import HttpUser, task, between, events
from locust.exception import StopUser

# Configurações de teste
CACHE_TEST_CONFIG = {
    'keywords': [
        'marketing digital', 'seo', 'google ads', 'facebook ads', 'instagram marketing',
        'content marketing', 'email marketing', 'social media', 'analytics', 'conversion',
        'lead generation', 'branding', 'influencer marketing', 'video marketing', 'mobile marketing'
    ],
    'categories': [
        'tecnologia', 'saude', 'educacao', 'financas', 'entretenimento',
        'esportes', 'moda', 'automoveis', 'imoveis', 'viagem'
    ],
    'cache_patterns': [
        'keywords', 'metrics', 'trends', 'analytics', 'reports',
        'user_data', 'config', 'templates', 'logs', 'audit'
    ]
}

class CacheLoadTestUser(HttpUser):
    """
    Usuário de teste para carga no sistema de cache
    """
    
    wait_time = between(1, 3)
    weight = 10
    
    def on_start(self):
        """Inicialização do usuário"""
        self.tracing_id = f"CACHE_LOAD_{int(time.time())}_{random.randint(1000, 9999)}"
        self.session_data = {
            'user_id': f"user_{random.randint(1000, 9999)}",
            'session_id': f"session_{random.randint(10000, 99999)}",
            'cache_hits': 0,
            'cache_misses': 0,
            'total_requests': 0
        }
        
        # Headers padrão
        self.headers = {
            'Content-Type': 'application/json',
            'X-Tracing-ID': self.tracing_id,
            'X-User-ID': self.session_data['user_id'],
            'X-Session-ID': self.session_data['session_id']
        }
        
        print(f"[{self.tracing_id}] Usuário de cache iniciado")
    
    def on_stop(self):
        """Finalização do usuário"""
        print(f"[{self.tracing_id}] Usuário finalizado - "
              f"Total: {self.session_data['total_requests']}, "
              f"Hits: {self.session_data['cache_hits']}, "
              f"Misses: {self.session_data['cache_misses']}")
    
    @task(3)
    def test_cache_keywords_get(self):
        """Teste de busca de keywords no cache"""
        keyword = random.choice(CACHE_TEST_CONFIG['keywords'])
        cache_key = f"keywords:{keyword}"
        
        with self.client.get(
            f"/api/cache/keywords?q={keyword}",
            headers=self.headers,
            name="/api/cache/keywords [GET]",
            catch_response=True
        ) as response:
            self.session_data['total_requests'] += 1
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Validar estrutura da resposta
                    if 'data' in data and 'cached' in data:
                        if data['cached']:
                            self.session_data['cache_hits'] += 1
                            response.success()
                        else:
                            self.session_data['cache_misses'] += 1
                            response.success()
                    else:
                        response.failure("Estrutura de resposta inválida")
                        
                except json.JSONDecodeError:
                    response.failure("Resposta não é JSON válido")
                    
            elif response.status_code == 404:
                self.session_data['cache_misses'] += 1
                response.success()
            else:
                response.failure(f"Status code inesperado: {response.status_code}")
    
    @task(2)
    def test_cache_metrics_get(self):
        """Teste de métricas de cache"""
        with self.client.get(
            "/api/cache/metrics",
            headers=self.headers,
            name="/api/cache/metrics [GET]",
            catch_response=True
        ) as response:
            self.session_data['total_requests'] += 1
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Validar métricas essenciais
                    required_fields = ['hit_ratio', 'total_requests', 'cache_size', 'memory_usage']
                    if all(field in data for field in required_fields):
                        response.success()
                    else:
                        response.failure("Métricas essenciais ausentes")
                        
                except json.JSONDecodeError:
                    response.failure("Resposta não é JSON válido")
            else:
                response.failure(f"Status code inesperado: {response.status_code}")
    
    @task(2)
    def test_cache_trends_get(self):
        """Teste de tendências no cache"""
        category = random.choice(CACHE_TEST_CONFIG['categories'])
        
        with self.client.get(
            f"/api/cache/trends?category={category}",
            headers=self.headers,
            name="/api/cache/trends [GET]",
            catch_response=True
        ) as response:
            self.session_data['total_requests'] += 1
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Validar estrutura de tendências
                    if 'trends' in data and isinstance(data['trends'], list):
                        response.success()
                    else:
                        response.failure("Estrutura de tendências inválida")
                        
                except json.JSONDecodeError:
                    response.failure("Resposta não é JSON válido")
            else:
                response.failure(f"Status code inesperado: {response.status_code}")
    
    @task(1)
    def test_cache_warm_post(self):
        """Teste de cache warming"""
        pattern = random.choice(CACHE_TEST_CONFIG['cache_patterns'])
        
        payload = {
            'pattern': pattern,
            'priority': random.choice(['low', 'medium', 'high']),
            'batch_size': random.randint(10, 100)
        }
        
        with self.client.post(
            "/api/cache/warm",
            json=payload,
            headers=self.headers,
            name="/api/cache/warm [POST]",
            catch_response=True
        ) as response:
            self.session_data['total_requests'] += 1
            
            if response.status_code in [200, 202]:
                try:
                    data = response.json()
                    
                    # Validar resposta de warming
                    if 'status' in data and 'items_warmed' in data:
                        response.success()
                    else:
                        response.failure("Resposta de warming inválida")
                        
                except json.JSONDecodeError:
                    response.failure("Resposta não é JSON válido")
            else:
                response.failure(f"Status code inesperado: {response.status_code}")
    
    @task(1)
    def test_cache_invalidate_delete(self):
        """Teste de invalidação de cache"""
        pattern = random.choice(CACHE_TEST_CONFIG['cache_patterns'])
        
        with self.client.delete(
            f"/api/cache/invalidate?pattern={pattern}",
            headers=self.headers,
            name="/api/cache/invalidate [DELETE]",
            catch_response=True
        ) as response:
            self.session_data['total_requests'] += 1
            
            if response.status_code in [200, 204]:
                response.success()
            else:
                response.failure(f"Status code inesperado: {response.status_code}")
    
    @task(1)
    def test_cache_stats_get(self):
        """Teste de estatísticas de cache"""
        with self.client.get(
            "/api/cache/stats",
            headers=self.headers,
            name="/api/cache/stats [GET]",
            catch_response=True
        ) as response:
            self.session_data['total_requests'] += 1
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Validar estatísticas
                    required_stats = ['total_keys', 'memory_usage', 'hit_ratio', 'evictions']
                    if all(stat in data for stat in required_stats):
                        response.success()
                    else:
                        response.failure("Estatísticas essenciais ausentes")
                        
                except json.JSONDecodeError:
                    response.failure("Resposta não é JSON válido")
            else:
                response.failure(f"Status code inesperado: {response.status_code}")

class CacheStressTestUser(HttpUser):
    """
    Usuário de teste para stress no sistema de cache
    """
    
    wait_time = between(0.1, 0.5)  # Mais rápido para stress
    weight = 5
    
    def on_start(self):
        """Inicialização do usuário de stress"""
        self.tracing_id = f"CACHE_STRESS_{int(time.time())}_{random.randint(1000, 9999)}"
        self.headers = {
            'Content-Type': 'application/json',
            'X-Tracing-ID': self.tracing_id,
            'X-User-ID': f"stress_user_{random.randint(1000, 9999)}"
        }
        
        print(f"[{self.tracing_id}] Usuário de stress de cache iniciado")
    
    @task(5)
    def stress_cache_keywords(self):
        """Stress test para keywords no cache"""
        # Gerar keyword aleatória para maximizar cache misses
        keyword = f"stress_keyword_{random.randint(1, 10000)}"
        
        with self.client.get(
            f"/api/cache/keywords?q={keyword}",
            headers=self.headers,
            name="/api/cache/keywords [STRESS]",
            catch_response=True
        ) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Status code inesperado: {response.status_code}")
    
    @task(3)
    def stress_cache_metrics(self):
        """Stress test para métricas de cache"""
        with self.client.get(
            "/api/cache/metrics",
            headers=self.headers,
            name="/api/cache/metrics [STRESS]",
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
    print(f"🚀 Iniciando teste de carga de cache - {datetime.now()}")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Listener para fim do teste"""
    print(f"🏁 Finalizando teste de carga de cache - {datetime.now()}")
    
    # Estatísticas finais
    stats = environment.stats
    print(f"📊 Estatísticas finais:")
    print(f"   - Total de requests: {stats.total.num_requests}")
    print(f"   - Requests/s: {stats.total.current_rps}")
    print(f"   - Tempo médio: {stats.total.avg_response_time:.2f}ms")
    print(f"   - Taxa de erro: {stats.total.fail_ratio:.2%}") 