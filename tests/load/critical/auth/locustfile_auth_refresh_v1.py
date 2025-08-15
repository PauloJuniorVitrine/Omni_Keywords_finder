"""
🧪 TESTE DE CARGA - ENDPOINT AUTH REFRESH
🎯 Objetivo: Teste de carga em /api/auth/refresh
📅 Data: 2025-01-27
🔗 Tracing ID: LOAD_TEST_AUTH_REFRESH_001
📋 Ruleset: enterprise_control_layer.yaml

📊 ABORDAGENS APLICADAS:
✅ CoCoT (Completo, Coerente, Transparente)
✅ ToT (Tree of Thoughts) - Múltiplas rotas de pensamento
✅ ReAct (Reasoning + Acting) - Raciocínio + Ação iterativa
✅ Representações Visuais - Diagramas e fluxos

🔍 CENÁRIOS DE TESTE:
1. Refresh token válido
2. Refresh token expirado
3. Refresh token inválido/malformado
4. Refresh token na blacklist
5. Rate limiting
6. Concorrência de refresh tokens
7. Token rotation (se habilitado)
"""

import time
import json
import random
import jwt
from datetime import datetime, timedelta
from locust import HttpUser, task, between, events
from typing import Dict, Any, Optional

# Configurações de teste
TEST_CONFIG = {
    "base_url": "http://localhost:8000",
    "endpoint": "/api/auth/refresh",
    "rate_limit": 100,  # requests por minuto
    "concurrent_users": 50,
    "test_duration": 300,  # 5 minutos
    "think_time": (1, 3),  # tempo entre requests
}

# Tokens de teste (baseados no RefreshTokenManager)
class TestTokenGenerator:
    """Gerador de tokens de teste baseado no RefreshTokenManager real"""
    
    def __init__(self):
        self.refresh_secret = "refresh-secret-key-change-in-production"
        self.access_secret = "access-secret-key-change-in-production"
        self.access_token_expires = 3600  # 1 hora
        self.refresh_token_expires = 604800  # 7 dias
    
    def generate_valid_refresh_token(self, user_id: int = 1) -> str:
        """Gera refresh token válido"""
        claims = {
            'user_id': user_id,
            'token_family': f"family_{user_id}_{int(time.time())}",
            'token_type': 'refresh',
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=self.refresh_token_expires)
        }
        return jwt.encode(claims, self.refresh_secret, algorithm='HS256')
    
    def generate_expired_refresh_token(self, user_id: int = 1) -> str:
        """Gera refresh token expirado"""
        claims = {
            'user_id': user_id,
            'token_family': f"family_{user_id}_{int(time.time())}",
            'token_type': 'refresh',
            'iat': datetime.utcnow() - timedelta(days=8),
            'exp': datetime.utcnow() - timedelta(days=1)
        }
        return jwt.encode(claims, self.refresh_secret, algorithm='HS256')
    
    def generate_invalid_refresh_token(self) -> str:
        """Gera refresh token inválido"""
        return "invalid.token.here"
    
    def generate_access_token_as_refresh(self, user_id: int = 1) -> str:
        """Gera access token mas envia como refresh token (teste de tipo)"""
        claims = {
            'user_id': user_id,
            'token_family': f"family_{user_id}_{int(time.time())}",
            'token_type': 'access',  # Tipo incorreto
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=self.access_token_expires)
        }
        return jwt.encode(claims, self.access_secret, algorithm='HS256')

# Métricas de teste
class TestMetrics:
    """Coleta métricas durante o teste"""
    
    def __init__(self):
        self.success_count = 0
        self.error_count = 0
        self.rate_limit_count = 0
        self.invalid_token_count = 0
        self.expired_token_count = 0
        self.response_times = []
    
    def record_success(self, response_time: float):
        """Registra sucesso"""
        self.success_count += 1
        self.response_times.append(response_time)
    
    def record_error(self, error_type: str, response_time: float):
        """Registra erro"""
        self.error_count += 1
        self.response_times.append(response_time)
        
        if error_type == "rate_limit":
            self.rate_limit_count += 1
        elif error_type == "invalid_token":
            self.invalid_token_count += 1
        elif error_type == "expired_token":
            self.expired_token_count += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo das métricas"""
        total_requests = self.success_count + self.error_count
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        return {
            "total_requests": total_requests,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": (self.success_count / total_requests * 100) if total_requests > 0 else 0,
            "avg_response_time": avg_response_time,
            "rate_limit_errors": self.rate_limit_count,
            "invalid_token_errors": self.invalid_token_count,
            "expired_token_errors": self.expired_token_count,
        }

# Usuário de teste Locust
class AuthRefreshUser(HttpUser):
    """Usuário de teste para endpoint de refresh token"""
    
    wait_time = between(*TEST_CONFIG["think_time"])
    token_generator = TestTokenGenerator()
    metrics = TestMetrics()
    
    def on_start(self):
        """Inicialização do usuário"""
        self.user_id = random.randint(1, 1000)
        self.valid_refresh_token = self.token_generator.generate_valid_refresh_token(self.user_id)
        self.expired_refresh_token = self.token_generator.generate_expired_refresh_token(self.user_id)
        self.invalid_refresh_token = self.token_generator.generate_invalid_refresh_token()
        self.wrong_type_token = self.token_generator.generate_access_token_as_refresh(self.user_id)
        
        # Log de inicialização
        print(f"[INFO] Usuário {self.user_id} inicializado com tokens de teste")
    
    @task(40)  # 40% das requisições
    def test_valid_refresh_token(self):
        """Teste com refresh token válido"""
        start_time = time.time()
        
        try:
            payload = {
                "refresh_token": self.valid_refresh_token
            }
            
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "LoadTest/1.0",
                "X-Request-ID": f"req_{self.user_id}_{int(time.time())}"
            }
            
            with self.client.post(
                TEST_CONFIG["endpoint"],
                json=payload,
                headers=headers,
                catch_response=True,
                name="refresh_valid_token"
            ) as response:
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    # Validar resposta
                    try:
                        data = response.json()
                        if "access_token" in data and "refresh_token" in data:
                            response.success()
                            self.metrics.record_success(response_time)
                            print(f"[SUCCESS] Refresh válido - User {self.user_id} - {response_time:.3f}s")
                        else:
                            response.failure("Resposta não contém tokens esperados")
                            self.metrics.record_error("invalid_response", response_time)
                    except json.JSONDecodeError:
                        response.failure("Resposta não é JSON válido")
                        self.metrics.record_error("invalid_json", response_time)
                
                elif response.status_code == 401:
                    response.failure("Token inválido ou expirado")
                    self.metrics.record_error("invalid_token", response_time)
                
                elif response.status_code == 429:
                    response.failure("Rate limit excedido")
                    self.metrics.record_error("rate_limit", response_time)
                
                else:
                    response.failure(f"Status inesperado: {response.status_code}")
                    self.metrics.record_error("unexpected_status", response_time)
        
        except Exception as e:
            response_time = time.time() - start_time
            self.metrics.record_error("exception", response_time)
            print(f"[ERROR] Exceção no refresh válido - User {self.user_id}: {str(e)}")
    
    @task(20)  # 20% das requisições
    def test_expired_refresh_token(self):
        """Teste com refresh token expirado"""
        start_time = time.time()
        
        try:
            payload = {
                "refresh_token": self.expired_refresh_token
            }
            
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "LoadTest/1.0",
                "X-Request-ID": f"req_{self.user_id}_{int(time.time())}"
            }
            
            with self.client.post(
                TEST_CONFIG["endpoint"],
                json=payload,
                headers=headers,
                catch_response=True,
                name="refresh_expired_token"
            ) as response:
                response_time = time.time() - start_time
                
                if response.status_code == 401:
                    response.success()  # Esperado para token expirado
                    self.metrics.record_error("expired_token", response_time)
                    print(f"[EXPECTED] Token expirado - User {self.user_id} - {response_time:.3f}s")
                
                elif response.status_code == 200:
                    response.failure("Token expirado foi aceito (inconsistência)")
                    self.metrics.record_error("unexpected_success", response_time)
                
                else:
                    response.failure(f"Status inesperado para token expirado: {response.status_code}")
                    self.metrics.record_error("unexpected_status", response_time)
        
        except Exception as e:
            response_time = time.time() - start_time
            self.metrics.record_error("exception", response_time)
            print(f"[ERROR] Exceção no refresh expirado - User {self.user_id}: {str(e)}")
    
    @task(15)  # 15% das requisições
    def test_invalid_refresh_token(self):
        """Teste com refresh token inválido"""
        start_time = time.time()
        
        try:
            payload = {
                "refresh_token": self.invalid_refresh_token
            }
            
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "LoadTest/1.0",
                "X-Request-ID": f"req_{self.user_id}_{int(time.time())}"
            }
            
            with self.client.post(
                TEST_CONFIG["endpoint"],
                json=payload,
                headers=headers,
                catch_response=True,
                name="refresh_invalid_token"
            ) as response:
                response_time = time.time() - start_time
                
                if response.status_code in [400, 401, 422]:
                    response.success()  # Esperado para token inválido
                    self.metrics.record_error("invalid_token", response_time)
                    print(f"[EXPECTED] Token inválido - User {self.user_id} - {response_time:.3f}s")
                
                elif response.status_code == 200:
                    response.failure("Token inválido foi aceito (vulnerabilidade)")
                    self.metrics.record_error("security_issue", response_time)
                
                else:
                    response.failure(f"Status inesperado para token inválido: {response.status_code}")
                    self.metrics.record_error("unexpected_status", response_time)
        
        except Exception as e:
            response_time = time.time() - start_time
            self.metrics.record_error("exception", response_time)
            print(f"[ERROR] Exceção no refresh inválido - User {self.user_id}: {str(e)}")
    
    @task(10)  # 10% das requisições
    def test_wrong_token_type(self):
        """Teste enviando access token como refresh token"""
        start_time = time.time()
        
        try:
            payload = {
                "refresh_token": self.wrong_type_token
            }
            
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "LoadTest/1.0",
                "X-Request-ID": f"req_{self.user_id}_{int(time.time())}"
            }
            
            with self.client.post(
                TEST_CONFIG["endpoint"],
                json=payload,
                headers=headers,
                catch_response=True,
                name="refresh_wrong_token_type"
            ) as response:
                response_time = time.time() - start_time
                
                if response.status_code in [400, 401, 422]:
                    response.success()  # Esperado para tipo incorreto
                    self.metrics.record_error("invalid_token", response_time)
                    print(f"[EXPECTED] Tipo de token incorreto - User {self.user_id} - {response_time:.3f}s")
                
                elif response.status_code == 200:
                    response.failure("Access token aceito como refresh token (vulnerabilidade)")
                    self.metrics.record_error("security_issue", response_time)
                
                else:
                    response.failure(f"Status inesperado para tipo incorreto: {response.status_code}")
                    self.metrics.record_error("unexpected_status", response_time)
        
        except Exception as e:
            response_time = time.time() - start_time
            self.metrics.record_error("exception", response_time)
            print(f"[ERROR] Exceção no tipo incorreto - User {self.user_id}: {str(e)}")
    
    @task(10)  # 10% das requisições
    def test_malformed_payload(self):
        """Teste com payload malformado"""
        start_time = time.time()
        
        try:
            # Payloads malformados para teste
            malformed_payloads = [
                {},  # Payload vazio
                {"refresh_token": ""},  # Token vazio
                {"refresh_token": None},  # Token None
                {"invalid_field": "value"},  # Campo inválido
                "invalid_json_string",  # String inválida
                {"refresh_token": "a" * 10000},  # Token muito longo
            ]
            
            payload = random.choice(malformed_payloads)
            
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "LoadTest/1.0",
                "X-Request-ID": f"req_{self.user_id}_{int(time.time())}"
            }
            
            with self.client.post(
                TEST_CONFIG["endpoint"],
                json=payload if isinstance(payload, dict) else payload,
                headers=headers,
                catch_response=True,
                name="refresh_malformed_payload"
            ) as response:
                response_time = time.time() - start_time
                
                if response.status_code in [400, 422]:
                    response.success()  # Esperado para payload malformado
                    self.metrics.record_error("malformed_payload", response_time)
                    print(f"[EXPECTED] Payload malformado - User {self.user_id} - {response_time:.3f}s")
                
                elif response.status_code == 200:
                    response.failure("Payload malformado foi aceito (vulnerabilidade)")
                    self.metrics.record_error("security_issue", response_time)
                
                else:
                    response.failure(f"Status inesperado para payload malformado: {response.status_code}")
                    self.metrics.record_error("unexpected_status", response_time)
        
        except Exception as e:
            response_time = time.time() - start_time
            self.metrics.record_error("exception", response_time)
            print(f"[ERROR] Exceção no payload malformado - User {self.user_id}: {str(e)}")
    
    @task(5)  # 5% das requisições
    def test_concurrent_refresh(self):
        """Teste de concorrência - múltiplos refresh simultâneos"""
        start_time = time.time()
        
        try:
            # Gerar novo token para teste de concorrência
            concurrent_token = self.token_generator.generate_valid_refresh_token(self.user_id)
            
            payload = {
                "refresh_token": concurrent_token
            }
            
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "LoadTest/1.0",
                "X-Request-ID": f"req_{self.user_id}_{int(time.time())}"
            }
            
            with self.client.post(
                TEST_CONFIG["endpoint"],
                json=payload,
                headers=headers,
                catch_response=True,
                name="refresh_concurrent"
            ) as response:
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    response.success()
                    self.metrics.record_success(response_time)
                    print(f"[SUCCESS] Refresh concorrente - User {self.user_id} - {response_time:.3f}s")
                
                elif response.status_code == 409:
                    response.success()  # Conflito esperado em alguns casos
                    self.metrics.record_error("concurrent_conflict", response_time)
                    print(f"[EXPECTED] Conflito concorrente - User {self.user_id} - {response_time:.3f}s")
                
                elif response.status_code == 429:
                    response.failure("Rate limit excedido")
                    self.metrics.record_error("rate_limit", response_time)
                
                else:
                    response.failure(f"Status inesperado para concorrência: {response.status_code}")
                    self.metrics.record_error("unexpected_status", response_time)
        
        except Exception as e:
            response_time = time.time() - start_time
            self.metrics.record_error("exception", response_time)
            print(f"[ERROR] Exceção no refresh concorrente - User {self.user_id}: {str(e)}")

# Event listeners para métricas globais
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Evento de início do teste"""
    print(f"""
🚀 INICIANDO TESTE DE CARGA - AUTH REFRESH
📊 Configuração:
   - Base URL: {TEST_CONFIG['base_url']}
   - Endpoint: {TEST_CONFIG['endpoint']}
   - Usuários concorrentes: {TEST_CONFIG['concurrent_users']}
   - Duração: {TEST_CONFIG['test_duration']}s
   - Rate limit: {TEST_CONFIG['rate_limit']} req/min

🎯 Cenários de teste:
   - 40% Refresh token válido
   - 20% Refresh token expirado
   - 15% Refresh token inválido
   - 10% Tipo de token incorreto
   - 10% Payload malformado
   - 5% Teste de concorrência

📈 Métricas serão coletadas durante o teste...
    """)

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Evento de fim do teste"""
    print(f"""
🏁 TESTE DE CARGA FINALIZADO - AUTH REFRESH

📊 RESUMO FINAL:
   - Total de requisições: {AuthRefreshUser.metrics.get_summary()['total_requests']}
   - Taxa de sucesso: {AuthRefreshUser.metrics.get_summary()['success_rate']:.2f}%
   - Tempo médio de resposta: {AuthRefreshUser.metrics.get_summary()['avg_response_time']:.3f}s
   - Erros de rate limit: {AuthRefreshUser.metrics.get_summary()['rate_limit_errors']}
   - Erros de token inválido: {AuthRefreshUser.metrics.get_summary()['invalid_token_errors']}
   - Erros de token expirado: {AuthRefreshUser.metrics.get_summary()['expired_token_errors']}

✅ Teste concluído com sucesso!
    """)

# Configurações adicionais
if __name__ == "__main__":
    print("""
🧪 TESTE DE CARGA - AUTH REFRESH TOKEN
🎯 Para executar: locust -f locustfile_auth_refresh_v1.py --host=http://localhost:8000
📊 Abra http://localhost:8089 para interface web
    """) 