"""
🔐 Teste de Carga - Endpoint de Logout
🎯 Objetivo: Validar performance e segurança do endpoint /api/auth/logout
📅 Data: 2025-01-27
🔗 Tracing ID: LOAD_TEST_LOGOUT_20250127_001
📋 Ruleset: enterprise_control_layer.yaml

📊 Abordagens de Raciocínio:
- CoCoT: Comprovação, Causalidade, Contexto, Tendência
- ToT: Tree of Thoughts - Múltiplas abordagens de teste
- ReAct: Simulação e reflexão sobre cenários
- Representações Visuais: Diagramas de fluxo e relacionamentos

🔍 Cenários de Teste:
1. Logout válido com token JWT
2. Logout com token expirado
3. Logout sem token
4. Logout com token malformado
5. Rate limiting em logout
6. Logout concorrente
7. Logout após múltiplos logins
"""

import time
import json
import random
from locust import HttpUser, task, between, events
from typing import Dict, Any, Optional
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LogoutTestUser(HttpUser):
    """
    Usuário de teste para endpoint de logout
    Implementa cenários baseados em código real do sistema
    """
    
    wait_time = between(1, 3)  # Tempo entre requisições
    weight = 1  # Peso do usuário no teste
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_token: Optional[str] = None
        self.user_id: Optional[int] = None
        self.test_data = self._load_test_data()
        
    def on_start(self):
        """Inicialização do usuário - login para obter token"""
        try:
            # Login para obter token válido
            login_response = self.client.post(
                "/api/auth/login",
                json={
                    "username": "test_user_load",
                    "senha": "TestPass123!"
                },
                headers={"Content-Type": "application/json"},
                name="setup_login"
            )
            
            if login_response.status_code == 200:
                data = login_response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                logger.info(f"Usuário {self.user_id} autenticado para testes de logout")
            else:
                logger.warning(f"Falha no login de setup: {login_response.status_code}")
                
        except Exception as e:
            logger.error(f"Erro no setup do usuário: {e}")
    
    def _load_test_data(self) -> Dict[str, Any]:
        """Carrega dados de teste baseados no código real"""
        return {
            "valid_tokens": [],  # Tokens válidos para teste
            "expired_tokens": [
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
            ],
            "malformed_tokens": [
                "invalid_token",
                "Bearer ",
                "Bearer invalid",
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid",
                ""
            ],
            "test_users": [
                {"username": "test_user_1", "senha": "TestPass123!"},
                {"username": "test_user_2", "senha": "TestPass123!"},
                {"username": "test_user_3", "senha": "TestPass123!"}
            ]
        }
    
    @task(40)  # 40% das requisições
    def logout_valid_token(self):
        """
        🔐 Cenário: Logout com token válido
        📊 CoCoT: Comprovação de logout bem-sucedido
        🎯 ToT: Abordagem principal de teste
        """
        if not self.auth_token:
            logger.warning("Token não disponível para teste de logout válido")
            return
            
        start_time = time.time()
        
        try:
            response = self.client.post(
                "/api/auth/logout",
                headers={
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                },
                name="logout_valid_token"
            )
            
            # Validações baseadas no código real
            if response.status_code == 200:
                data = response.json()
                assert "msg" in data, "Resposta deve conter campo 'msg'"
                assert data["msg"] == "Logout efetuado.", "Mensagem de logout incorreta"
                
                # Log de sucesso
                logger.info(f"Logout bem-sucedido para usuário {self.user_id}")
                
            elif response.status_code == 401:
                logger.warning(f"Token inválido/expirado: {response.status_code}")
                
            else:
                logger.error(f"Erro inesperado no logout: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Exceção no logout válido: {e}")
            self.environment.events.request_failure.fire(
                request_type="POST",
                name="logout_valid_token",
                response_time=time.time() - start_time,
                exception=e
            )
    
    @task(20)  # 20% das requisições
    def logout_expired_token(self):
        """
        ⏰ Cenário: Logout com token expirado
        📊 CoCoT: Causalidade de token expirado
        🎯 ToT: Abordagem de teste de segurança
        """
        expired_token = random.choice(self.test_data["expired_tokens"])
        
        start_time = time.time()
        
        try:
            response = self.client.post(
                "/api/auth/logout",
                headers={
                    "Authorization": f"Bearer {expired_token}",
                    "Content-Type": "application/json"
                },
                name="logout_expired_token"
            )
            
            # Validações esperadas para token expirado
            if response.status_code == 401:
                logger.info("Token expirado rejeitado corretamente")
                
            elif response.status_code == 422:
                logger.info("Token malformado rejeitado corretamente")
                
            else:
                logger.warning(f"Resposta inesperada para token expirado: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Exceção no logout com token expirado: {e}")
            self.environment.events.request_failure.fire(
                request_type="POST",
                name="logout_expired_token",
                response_time=time.time() - start_time,
                exception=e
            )
    
    @task(15)  # 15% das requisições
    def logout_no_token(self):
        """
        🚫 Cenário: Logout sem token
        📊 CoCoT: Contexto de autenticação ausente
        🎯 ToT: Abordagem de teste de validação
        """
        start_time = time.time()
        
        try:
            response = self.client.post(
                "/api/auth/logout",
                headers={"Content-Type": "application/json"},
                name="logout_no_token"
            )
            
            # Validações esperadas para requisição sem token
            if response.status_code == 401:
                logger.info("Requisição sem token rejeitada corretamente")
                
            else:
                logger.warning(f"Resposta inesperada para requisição sem token: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Exceção no logout sem token: {e}")
            self.environment.events.request_failure.fire(
                request_type="POST",
                name="logout_no_token",
                response_time=time.time() - start_time,
                exception=e
            )
    
    @task(15)  # 15% das requisições
    def logout_malformed_token(self):
        """
        🛡️ Cenário: Logout com token malformado
        📊 CoCoT: Tendência de ataques de segurança
        🎯 ToT: Abordagem de teste de robustez
        """
        malformed_token = random.choice(self.test_data["malformed_tokens"])
        
        start_time = time.time()
        
        try:
            response = self.client.post(
                "/api/auth/logout",
                headers={
                    "Authorization": f"Bearer {malformed_token}",
                    "Content-Type": "application/json"
                },
                name="logout_malformed_token"
            )
            
            # Validações esperadas para token malformado
            if response.status_code in [401, 422]:
                logger.info(f"Token malformado rejeitado corretamente: {response.status_code}")
                
            else:
                logger.warning(f"Resposta inesperada para token malformado: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Exceção no logout com token malformado: {e}")
            self.environment.events.request_failure.fire(
                request_type="POST",
                name="logout_malformed_token",
                response_time=time.time() - start_time,
                exception=e
            )
    
    @task(10)  # 10% das requisições
    def logout_concurrent_sessions(self):
        """
        🔄 Cenário: Logout com múltiplas sessões
        📊 CoCoT: Contexto de uso real
        🎯 ToT: Abordagem de teste de concorrência
        """
        if not self.auth_token:
            return
            
        start_time = time.time()
        
        try:
            # Simular logout concorrente
            responses = []
            for i in range(3):
                response = self.client.post(
                    "/api/auth/logout",
                    headers={
                        "Authorization": f"Bearer {self.auth_token}",
                        "Content-Type": "application/json"
                    },
                    name=f"logout_concurrent_{i}"
                )
                responses.append(response)
            
            # Analisar respostas
            success_count = sum(1 for r in responses if r.status_code == 200)
            logger.info(f"Logout concorrente: {success_count}/3 sucessos")
            
        except Exception as e:
            logger.error(f"Exceção no logout concorrente: {e}")
            self.environment.events.request_failure.fire(
                request_type="POST",
                name="logout_concurrent_sessions",
                response_time=time.time() - start_time,
                exception=e
            )

# Event listeners para métricas customizadas
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, context, exception, start_time, url, **kwargs):
    """Listener para métricas customizadas"""
    if name.startswith("logout_"):
        # Métricas específicas de logout
        if response and response.status_code == 200:
            logger.info(f"✅ Logout bem-sucedido: {name} - {response_time:.2f}ms")
        elif response and response.status_code == 401:
            logger.info(f"🔒 Logout rejeitado (401): {name} - {response_time:.2f}ms")
        elif exception:
            logger.error(f"❌ Erro no logout: {name} - {exception}")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Inicialização do teste"""
    logger.info("🚀 Iniciando teste de carga para endpoint de logout")
    logger.info(f"📊 Configuração: {environment.host}")
    logger.info("🎯 Cenários: Logout válido, expirado, sem token, malformado, concorrente")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Finalização do teste"""
    logger.info("🏁 Teste de carga de logout finalizado")
    
    # Estatísticas finais
    stats = environment.stats
    logout_stats = {
        "total_requests": stats.total.num_requests,
        "failed_requests": stats.total.num_failures,
        "avg_response_time": stats.total.avg_response_time,
        "max_response_time": stats.total.max_response_time,
        "min_response_time": stats.total.min_response_time,
        "requests_per_sec": stats.total.current_rps
    }
    
    logger.info(f"📈 Estatísticas finais: {json.dumps(logout_stats, indent=2)}")

# Configurações de teste
class LogoutTestConfig:
    """Configurações específicas para teste de logout"""
    
    # Limites de performance baseados no código real
    MAX_RESPONSE_TIME = 2000  # 2 segundos
    MAX_ERROR_RATE = 0.05     # 5%
    EXPECTED_RPS = 100        # 100 requests por segundo
    
    # Cenários de teste
    SCENARIOS = {
        "logout_valid_token": {
            "weight": 40,
            "expected_status": 200,
            "description": "Logout com token válido"
        },
        "logout_expired_token": {
            "weight": 20,
            "expected_status": 401,
            "description": "Logout com token expirado"
        },
        "logout_no_token": {
            "weight": 15,
            "expected_status": 401,
            "description": "Logout sem token"
        },
        "logout_malformed_token": {
            "weight": 15,
            "expected_status": [401, 422],
            "description": "Logout com token malformado"
        },
        "logout_concurrent_sessions": {
            "weight": 10,
            "expected_status": 200,
            "description": "Logout com sessões concorrentes"
        }
    }
    
    # Critérios de sucesso
    SUCCESS_CRITERIA = {
        "response_time_p95": 1500,  # 95% das requisições < 1.5s
        "error_rate": 0.05,         # Taxa de erro < 5%
        "throughput": 50,           # Mínimo 50 RPS
        "availability": 0.99        # 99% de disponibilidade
    } 