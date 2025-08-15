"""
locustfile_database_load_v1.py
Teste de carga para os endpoints de banco de dados

Prompt: CHECKLIST_TESTES_CARGA_CRITICIDADE.md - Nível Médio
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Tracing ID: LOAD_DATABASE_20250127_001

Endpoints testados:
- GET /api/nichos - Listagem de nichos com paginação
- GET /api/categorias - Listagem de categorias com filtros
- GET /api/execucoes - Listagem de execuções com joins
- POST /api/execucoes - Criação de execuções (transação)
- GET /api/logs - Consulta de logs com filtros complexos
- GET /api/notificacoes - Listagem de notificações
- POST /api/prompt-system/nichos - Criação de nichos (transação)
- GET /api/prompt-system/nichos - Listagem de nichos
- POST /api/prompt-system/categorias - Criação de categorias (transação)
- GET /api/prompt-system/categorias - Listagem de categorias

Cenários testados:
- Carga em pool de conexões
- Queries complexas com joins
- Transações concorrentes
- Paginação e filtros
- Consultas de logs
- Operações CRUD
"""

import time
import json
import random
from typing import Dict, Any, List
from locust import HttpUser, task, between, events
from datetime import datetime, timedelta

class DatabaseLoadUser(HttpUser):
    """
    Usuário de teste de carga para endpoints de banco de dados
    """
    
    wait_time = between(1, 3)
    tracing_id = "LOAD_DATABASE_20250127_001"
    
    def on_start(self):
        """Inicialização do usuário"""
        self.auth_token = self._get_auth_token()
        self.headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json",
            "X-Tracing-ID": self.tracing_id
        }
        
        # Dados de teste baseados no código real
        self.test_nichos = [
            {"nome": "Marketing Digital", "descricao": "Nicho de marketing digital"},
            {"nome": "E-commerce", "descricao": "Nicho de e-commerce"},
            {"nome": "Saúde", "descricao": "Nicho de saúde e bem-estar"},
            {"nome": "Educação", "descricao": "Nicho de educação online"},
            {"nome": "Tecnologia", "descricao": "Nicho de tecnologia"}
        ]
        
        self.test_categorias = [
            {"nome": "SEO", "perfil_cliente": "Empresas que buscam visibilidade"},
            {"nome": "Google Ads", "perfil_cliente": "Empresas com orçamento para ads"},
            {"nome": "Redes Sociais", "perfil_cliente": "Empresas focadas em social media"},
            {"nome": "Content Marketing", "perfil_cliente": "Empresas que produzem conteúdo"},
            {"nome": "Email Marketing", "perfil_cliente": "Empresas com base de leads"}
        ]
        
        self.test_execucoes = [
            {"categoria_id": 1, "palavras_chave": ["seo", "otimização", "google"]},
            {"categoria_id": 2, "palavras_chave": ["google ads", "anúncios", "ppc"]},
            {"categoria_id": 3, "palavras_chave": ["instagram", "facebook", "social media"]},
            {"categoria_id": 4, "palavras_chave": ["content marketing", "blog", "artigos"]},
            {"categoria_id": 5, "palavras_chave": ["email marketing", "newsletter", "automação"]}
        ]
    
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
    
    @task(3)
    def test_list_nichos(self):
        """Teste de carga em listagem de nichos com paginação"""
        with self.client.get(
            "/api/nichos",
            headers=self.headers,
            name="GET /api/nichos - Listagem com paginação",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    response.success()
                else:
                    response.failure("Resposta vazia ou formato inválido")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(3)
    def test_list_categorias(self):
        """Teste de carga em listagem de categorias com filtros"""
        nicho_id = random.randint(1, 5)
        with self.client.get(
            f"/api/categorias?nicho_id={nicho_id}",
            headers=self.headers,
            name="GET /api/categorias - Listagem com filtros",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    response.success()
                else:
                    response.failure("Formato de resposta inválido")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(2)
    def test_list_execucoes(self):
        """Teste de carga em listagem de execuções com joins"""
        with self.client.get(
            "/api/execucoes",
            headers=self.headers,
            name="GET /api/execucoes - Listagem com joins",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    response.success()
                else:
                    response.failure("Formato de resposta inválido")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def test_create_execucao(self):
        """Teste de carga em criação de execuções (transação)"""
        execucao_data = random.choice(self.test_execucoes)
        with self.client.post(
            "/api/execucoes",
            json=execucao_data,
            headers=self.headers,
            name="POST /api/execucoes - Criação (transação)",
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                data = response.json()
                if "id" in data or "status" in data:
                    response.success()
                else:
                    response.failure("Resposta sem ID ou status")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(2)
    def test_list_logs(self):
        """Teste de carga em consulta de logs com filtros complexos"""
        with self.client.get(
            "/api/logs/execucoes",
            headers=self.headers,
            name="GET /api/logs - Consulta com filtros",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    response.success()
                else:
                    response.failure("Formato de resposta inválido")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(2)
    def test_list_notificacoes(self):
        """Teste de carga em listagem de notificações"""
        with self.client.get(
            "/api/notificacoes",
            headers=self.headers,
            name="GET /api/notificacoes - Listagem",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    response.success()
                else:
                    response.failure("Formato de resposta inválido")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def test_create_nicho(self):
        """Teste de carga em criação de nichos (transação)"""
        nicho_data = random.choice(self.test_nichos)
        with self.client.post(
            "/api/prompt-system/nichos",
            json=nicho_data,
            headers=self.headers,
            name="POST /api/prompt-system/nichos - Criação (transação)",
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                data = response.json()
                if "id" in data or "nome" in data:
                    response.success()
                else:
                    response.failure("Resposta sem ID ou nome")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(2)
    def test_list_prompt_nichos(self):
        """Teste de carga em listagem de nichos do prompt system"""
        with self.client.get(
            "/api/prompt-system/nichos",
            headers=self.headers,
            name="GET /api/prompt-system/nichos - Listagem",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    response.success()
                else:
                    response.failure("Formato de resposta inválido")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def test_create_categoria(self):
        """Teste de carga em criação de categorias (transação)"""
        categoria_data = random.choice(self.test_categorias)
        categoria_data["nicho_id"] = random.randint(1, 5)
        categoria_data["cluster"] = "cluster_teste"
        categoria_data["prompt_path"] = "/prompts/teste.txt"
        
        with self.client.post(
            "/api/prompt-system/categorias",
            json=categoria_data,
            headers=self.headers,
            name="POST /api/prompt-system/categorias - Criação (transação)",
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                data = response.json()
                if "id" in data or "nome" in data:
                    response.success()
                else:
                    response.failure("Resposta sem ID ou nome")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(2)
    def test_list_prompt_categorias(self):
        """Teste de carga em listagem de categorias do prompt system"""
        with self.client.get(
            "/api/prompt-system/categorias",
            headers=self.headers,
            name="GET /api/prompt-system/categorias - Listagem",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    response.success()
                else:
                    response.failure("Formato de resposta inválido")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def test_complex_query_with_joins(self):
        """Teste de carga em query complexa com joins"""
        # Simula query complexa com múltiplos joins
        with self.client.get(
            "/api/execucoes?include=categoria,nicho&limit=50",
            headers=self.headers,
            name="GET /api/execucoes - Query complexa com joins",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    response.success()
                else:
                    response.failure("Formato de resposta inválido")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def test_pagination_stress(self):
        """Teste de carga em paginação com diferentes páginas"""
        page = random.randint(1, 10)
        limit = random.choice([10, 20, 50, 100])
        
        with self.client.get(
            f"/api/nichos?page={page}&limit={limit}",
            headers=self.headers,
            name="GET /api/nichos - Paginação stress",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    response.success()
                else:
                    response.failure("Formato de resposta inválido")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def test_concurrent_transactions(self):
        """Teste de carga em transações concorrentes"""
        # Simula múltiplas operações concorrentes
        operations = [
            ("GET", "/api/nichos"),
            ("GET", "/api/categorias"),
            ("GET", "/api/execucoes"),
            ("GET", "/api/logs/execucoes")
        ]
        
        for method, endpoint in operations:
            with self.client.request(
                method,
                endpoint,
                headers=self.headers,
                name=f"{method} {endpoint} - Transação concorrente",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Status code: {response.status_code}")

# Event listeners para métricas customizadas
@events.request.add_listener
def my_request_handler(request_type, name, response_time, response_length, response, context, exception, start_time, url, **kwargs):
    """Handler customizado para métricas de banco de dados"""
    if exception:
        print(f"Erro na requisição {name}: {exception}")
    else:
        print(f"Requisição {name} completada em {response_time}ms")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Evento de início do teste"""
    print(f"🚀 Iniciando teste de carga de banco de dados - {datetime.now()}")
    print(f"📊 Tracing ID: {DatabaseLoadUser.tracing_id}")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Evento de fim do teste"""
    print(f"✅ Teste de carga de banco de dados finalizado - {datetime.now()}")
    print(f"📈 Métricas coletadas para análise de performance") 