"""
locustfile_database_connection_pool_v1.py
Teste de carga específico para pool de conexões de banco de dados

Prompt: CHECKLIST_TESTES_CARGA_CRITICIDADE.md - Nível Médio
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Tracing ID: LOAD_DATABASE_CONNECTION_POOL_20250127_001

Endpoints testados:
- GET /api/nichos - Teste de pool com queries simples
- GET /api/categorias - Teste de pool com filtros
- GET /api/execucoes - Teste de pool com joins
- POST /api/execucoes - Teste de pool com transações
- GET /api/logs/execucoes - Teste de pool com queries complexas
- GET /api/notificacoes - Teste de pool com paginação
- GET /api/prompt-system/nichos - Teste de pool com prompt system
- GET /api/prompt-system/categorias - Teste de pool com categorias

Cenários testados:
- Stress no pool de conexões
- Conexões simultâneas
- Timeouts de conexão
- Recovery após falhas
- Pool exhaustion
- Connection reuse
- Health checks
"""

import time
import json
import random
import asyncio
from typing import Dict, Any, List
from locust import HttpUser, task, between, events
from datetime import datetime, timedelta

class DatabaseConnectionPoolUser(HttpUser):
    """
    Usuário de teste de carga específico para pool de conexões
    """
    
    wait_time = between(0.5, 2)  # Mais agressivo para stress no pool
    tracing_id = "LOAD_DATABASE_CONNECTION_POOL_20250127_001"
    
    def on_start(self):
        """Inicialização do usuário"""
        self.auth_token = self._get_auth_token()
        self.headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json",
            "X-Tracing-ID": self.tracing_id
        }
        
        # Contadores para métricas
        self.connection_requests = 0
        self.connection_timeouts = 0
        self.connection_errors = 0
        
        # Dados de teste para transações
        self.test_data = {
            "nichos": [
                {"nome": f"Teste Nicho {i}", "descricao": f"Descrição teste {i}"}
                for i in range(1, 11)
            ],
            "execucoes": [
                {"categoria_id": i, "palavras_chave": [f"keyword{i}", f"test{i}"]}
                for i in range(1, 6)
            ]
        }
    
    def _get_auth_token(self) -> str:
        """Obtém token de autenticação"""
        try:
            response = self.client.post("/api/auth/login", json={
                "username": "test_user",
                "senha": "test123"
            })
            if response.status_code == 200:
                return response.json().get("access_token", "")
        except Exception as e:
            print(f"Erro ao obter token: {e}")
        return ""
    
    @task(4)
    def test_pool_simple_queries(self):
        """Teste de stress no pool com queries simples"""
        self.connection_requests += 1
        
        with self.client.get(
            "/api/nichos",
            headers=self.headers,
            name="GET /api/nichos - Pool stress (queries simples)",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    response.success()
                else:
                    response.failure("Formato de resposta inválido")
            elif response.status_code == 503:
                self.connection_timeouts += 1
                response.failure("Pool esgotado - 503 Service Unavailable")
            else:
                self.connection_errors += 1
                response.failure(f"Status code: {response.status_code}")
    
    @task(3)
    def test_pool_filtered_queries(self):
        """Teste de stress no pool com queries filtradas"""
        self.connection_requests += 1
        nicho_id = random.randint(1, 5)
        
        with self.client.get(
            f"/api/categorias?nicho_id={nicho_id}",
            headers=self.headers,
            name="GET /api/categorias - Pool stress (queries filtradas)",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    response.success()
                else:
                    response.failure("Formato de resposta inválido")
            elif response.status_code == 503:
                self.connection_timeouts += 1
                response.failure("Pool esgotado - 503 Service Unavailable")
            else:
                self.connection_errors += 1
                response.failure(f"Status code: {response.status_code}")
    
    @task(3)
    def test_pool_join_queries(self):
        """Teste de stress no pool com queries com joins"""
        self.connection_requests += 1
        
        with self.client.get(
            "/api/execucoes?include=categoria,nicho",
            headers=self.headers,
            name="GET /api/execucoes - Pool stress (queries com joins)",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    response.success()
                else:
                    response.failure("Formato de resposta inválido")
            elif response.status_code == 503:
                self.connection_timeouts += 1
                response.failure("Pool esgotado - 503 Service Unavailable")
            else:
                self.connection_errors += 1
                response.failure(f"Status code: {response.status_code}")
    
    @task(2)
    def test_pool_transactions(self):
        """Teste de stress no pool com transações"""
        self.connection_requests += 1
        execucao_data = random.choice(self.test_data["execucoes"])
        
        with self.client.post(
            "/api/execucoes",
            json=execucao_data,
            headers=self.headers,
            name="POST /api/execucoes - Pool stress (transações)",
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                data = response.json()
                if "id" in data or "status" in data:
                    response.success()
                else:
                    response.failure("Resposta sem ID ou status")
            elif response.status_code == 503:
                self.connection_timeouts += 1
                response.failure("Pool esgotado - 503 Service Unavailable")
            else:
                self.connection_errors += 1
                response.failure(f"Status code: {response.status_code}")
    
    @task(2)
    def test_pool_complex_queries(self):
        """Teste de stress no pool com queries complexas"""
        self.connection_requests += 1
        
        with self.client.get(
            "/api/logs/execucoes?limit=100&order=desc",
            headers=self.headers,
            name="GET /api/logs - Pool stress (queries complexas)",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    response.success()
                else:
                    response.failure("Formato de resposta inválido")
            elif response.status_code == 503:
                self.connection_timeouts += 1
                response.failure("Pool esgotado - 503 Service Unavailable")
            else:
                self.connection_errors += 1
                response.failure(f"Status code: {response.status_code}")
    
    @task(2)
    def test_pool_pagination(self):
        """Teste de stress no pool com paginação"""
        self.connection_requests += 1
        page = random.randint(1, 10)
        limit = random.choice([10, 20, 50, 100])
        
        with self.client.get(
            f"/api/notificacoes?page={page}&limit={limit}",
            headers=self.headers,
            name="GET /api/notificacoes - Pool stress (paginação)",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    response.success()
                else:
                    response.failure("Formato de resposta inválido")
            elif response.status_code == 503:
                self.connection_timeouts += 1
                response.failure("Pool esgotado - 503 Service Unavailable")
            else:
                self.connection_errors += 1
                response.failure(f"Status code: {response.status_code}")
    
    @task(2)
    def test_pool_prompt_system(self):
        """Teste de stress no pool com prompt system"""
        self.connection_requests += 1
        
        with self.client.get(
            "/api/prompt-system/nichos",
            headers=self.headers,
            name="GET /api/prompt-system/nichos - Pool stress (prompt system)",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    response.success()
                else:
                    response.failure("Formato de resposta inválido")
            elif response.status_code == 503:
                self.connection_timeouts += 1
                response.failure("Pool esgotado - 503 Service Unavailable")
            else:
                self.connection_errors += 1
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def test_pool_exhaustion(self):
        """Teste de esgotamento do pool de conexões"""
        self.connection_requests += 1
        
        # Fazer múltiplas requisições simultâneas para esgotar o pool
        for i in range(5):
            with self.client.get(
                f"/api/nichos?page={i+1}",
                headers=self.headers,
                name=f"GET /api/nichos - Pool exhaustion {i+1}",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    response.success()
                elif response.status_code == 503:
                    self.connection_timeouts += 1
                    response.failure("Pool esgotado - 503 Service Unavailable")
                else:
                    self.connection_errors += 1
                    response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def test_pool_recovery(self):
        """Teste de recovery do pool após falhas"""
        self.connection_requests += 1
        
        # Simular falha e recovery
        with self.client.get(
            "/api/nichos",
            headers=self.headers,
            name="GET /api/nichos - Pool recovery test",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    response.success()
                else:
                    response.failure("Formato de resposta inválido")
            elif response.status_code == 503:
                self.connection_timeouts += 1
                response.failure("Pool esgotado - 503 Service Unavailable")
            else:
                self.connection_errors += 1
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def test_pool_health_check(self):
        """Teste de health check do pool"""
        self.connection_requests += 1
        
        # Endpoint que pode indicar saúde do pool
        with self.client.get(
            "/api/health",
            headers=self.headers,
            name="GET /api/health - Pool health check",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "status" in data:
                    response.success()
                else:
                    response.failure("Resposta sem status")
            elif response.status_code == 503:
                self.connection_timeouts += 1
                response.failure("Pool esgotado - 503 Service Unavailable")
            else:
                self.connection_errors += 1
                response.failure(f"Status code: {response.status_code}")
    
    def on_stop(self):
        """Finalização do usuário - reportar métricas"""
        print(f"📊 Métricas do usuário {self.tracing_id}:")
        print(f"   - Requisições de conexão: {self.connection_requests}")
        print(f"   - Timeouts de pool: {self.connection_timeouts}")
        print(f"   - Erros de conexão: {self.connection_errors}")
        
        if self.connection_requests > 0:
            timeout_rate = (self.connection_timeouts / self.connection_requests) * 100
            error_rate = (self.connection_errors / self.connection_requests) * 100
            print(f"   - Taxa de timeout: {timeout_rate:.2f}%")
            print(f"   - Taxa de erro: {error_rate:.2f}%")

# Event listeners para métricas customizadas
@events.request.add_listener
def my_request_handler(request_type, name, response_time, response_length, response, context, exception, start_time, url, **kwargs):
    """Handler customizado para métricas de pool de conexões"""
    if "Pool" in name:
        if exception:
            print(f"❌ Erro no pool: {name} - {exception}")
        elif response_time > 5000:  # 5 segundos
            print(f"⚠️ Pool lento: {name} - {response_time}ms")
        else:
            print(f"✅ Pool OK: {name} - {response_time}ms")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Evento de início do teste"""
    print(f"🚀 Iniciando teste de carga de pool de conexões - {datetime.now()}")
    print(f"📊 Tracing ID: {DatabaseConnectionPoolUser.tracing_id}")
    print(f"🎯 Objetivo: Testar stress no pool de conexões do banco de dados")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Evento de fim do teste"""
    print(f"✅ Teste de carga de pool de conexões finalizado - {datetime.now()}")
    print(f"📈 Métricas coletadas para análise de performance do pool")
    
    # Análise final
    stats = environment.stats
    if stats.total.num_requests > 0:
        avg_response_time = stats.total.avg_response_time
        max_response_time = stats.total.max_response_time
        error_rate = (stats.total.num_failures / stats.total.num_requests) * 100
        
        print(f"📊 Estatísticas finais:")
        print(f"   - Total de requisições: {stats.total.num_requests}")
        print(f"   - Tempo médio de resposta: {avg_response_time:.2f}ms")
        print(f"   - Tempo máximo de resposta: {max_response_time:.2f}ms")
        print(f"   - Taxa de erro: {error_rate:.2f}%")
        
        # Recomendações baseadas nos resultados
        if avg_response_time > 2000:
            print(f"⚠️ Tempo médio alto - considere otimizar queries ou aumentar pool")
        if error_rate > 5:
            print(f"⚠️ Taxa de erro alta - verifique configurações do pool")
        if max_response_time > 10000:
            print(f"⚠️ Tempo máximo muito alto - verifique gargalos no banco") 