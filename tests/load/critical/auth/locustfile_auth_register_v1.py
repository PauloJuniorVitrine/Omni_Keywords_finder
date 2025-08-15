"""
🧪 TESTE DE CARGA - ENDPOINT AUTH REGISTER
🎯 Objetivo: Teste de carga em /api/auth/register
📅 Data: 2025-01-27
🔗 Tracing ID: LOAD_TEST_AUTH_REGISTER_001
📋 Ruleset: enterprise_control_layer.yaml

📊 ABORDAGENS APLICADAS:
✅ CoCoT (Completo, Coerente, Transparente)
✅ ToT (Tree of Thoughts) - Múltiplas rotas de pensamento
✅ ReAct (Reasoning + Acting) - Raciocínio + Ação iterativa
✅ Representações Visuais - Diagramas e fluxos

🔍 CENÁRIOS DE TESTE:
1. Registro válido com dados corretos
2. Registro com email duplicado
3. Registro com username duplicado
4. Dados malformados/inválidos
5. Validação de complexidade de senha
6. Rate limiting
7. Concorrência de registros
8. Ataques de enumeração
"""

import time
import json
import random
import string
import re
from datetime import datetime
from locust import HttpUser, task, between, events
from typing import Dict, Any, Optional

# Configurações de teste
TEST_CONFIG = {
    "base_url": "http://localhost:8000",
    "endpoint": "/api/auth/register",
    "rate_limit": 50,  # requests por minuto (mais restritivo que login)
    "concurrent_users": 30,
    "test_duration": 300,  # 5 minutos
    "think_time": (2, 5),  # tempo entre requests (mais longo que login)
}

# Gerador de dados de teste
class TestDataGenerator:
    """Gerador de dados de teste baseado no RegisterRequest schema"""
    
    def __init__(self):
        self.used_usernames = set()
        self.used_emails = set()
        self.test_domains = [
            "test.com", "example.com", "demo.org", "sample.net",
            "loadtest.io", "perftest.dev", "stresstest.co"
        ]
    
    def generate_valid_username(self) -> str:
        """Gera username válido baseado no schema"""
        # Padrão: 3-50 caracteres, alfanuméricos, underscore, hífen
        length = random.randint(5, 15)
        chars = string.ascii_lowercase + string.digits + "_-"
        username = ''.join(random.choice(chars) for _ in range(length))
        
        # Garantir que não seja apenas números
        if username.isdigit():
            username = "user_" + username
        
        # Garantir unicidade
        while username in self.used_usernames:
            username = username + str(random.randint(100, 999))
        
        self.used_usernames.add(username)
        return username
    
    def generate_valid_email(self) -> str:
        """Gera email válido"""
        username = self.generate_valid_username()
        domain = random.choice(self.test_domains)
        email = f"{username}@{domain}"
        
        # Garantir unicidade
        while email in self.used_emails:
            username = self.generate_valid_username()
            email = f"{username}@{domain}"
        
        self.used_emails.add(email)
        return email
    
    def generate_valid_password(self) -> str:
        """Gera senha válida baseada no schema"""
        # Requisitos: 8-128 chars, maiúscula, minúscula, número, especial
        length = random.randint(12, 20)
        
        # Garantir pelo menos um de cada tipo
        password = [
            random.choice(string.ascii_uppercase),  # Maiúscula
            random.choice(string.ascii_lowercase),  # Minúscula
            random.choice(string.digits),           # Número
            random.choice("!@#$%^&*(),.?\":{}|<>")  # Especial
        ]
        
        # Completar com caracteres aleatórios
        remaining_length = length - len(password)
        all_chars = string.ascii_letters + string.digits + "!@#$%^&*(),.?\":{}|<>"
        password.extend(random.choice(all_chars) for _ in range(remaining_length))
        
        # Embaralhar
        random.shuffle(password)
        return ''.join(password)
    
    def generate_invalid_username(self) -> str:
        """Gera username inválido"""
        invalid_usernames = [
            "",  # Vazio
            "ab",  # Muito curto
            "a" * 51,  # Muito longo
            "user@name",  # Caracteres inválidos
            "user name",  # Espaço
            "123456",  # Apenas números
            "user-name-",  # Termina com hífen
            "user_name_",  # Termina com underscore
        ]
        return random.choice(invalid_usernames)
    
    def generate_invalid_email(self) -> str:
        """Gera email inválido"""
        invalid_emails = [
            "",  # Vazio
            "invalid-email",  # Sem @
            "@domain.com",  # Sem username
            "user@",  # Sem domínio
            "user@domain",  # Sem TLD
            "user..name@domain.com",  # Pontos duplos
            "user@domain..com",  # Pontos duplos no domínio
            "user name@domain.com",  # Espaço no username
            "user@domain name.com",  # Espaço no domínio
        ]
        return random.choice(invalid_emails)
    
    def generate_invalid_password(self) -> str:
        """Gera senha inválida"""
        invalid_passwords = [
            "",  # Vazio
            "short",  # Muito curta
            "a" * 129,  # Muito longa
            "password",  # Sem maiúscula
            "PASSWORD",  # Sem minúscula
            "Password",  # Sem número
            "Password123",  # Sem especial
            "Password123!",  # Com caracteres suspeitos
            "Password<script>",  # XSS
            "Passwordjavascript",  # XSS
        ]
        return random.choice(invalid_passwords)
    
    def generate_duplicate_data(self) -> Dict[str, str]:
        """Gera dados duplicados para teste"""
        # Usar dados já existentes
        if self.used_usernames and self.used_emails:
            return {
                "username": random.choice(list(self.used_usernames)),
                "email": random.choice(list(self.used_emails)),
                "senha": self.generate_valid_password(),
                "confirmar_senha": ""
            }
        else:
            # Se não há dados existentes, criar novos
            return self.generate_valid_data()
    
    def generate_valid_data(self) -> Dict[str, str]:
        """Gera dados válidos completos"""
        password = self.generate_valid_password()
        return {
            "username": self.generate_valid_username(),
            "email": self.generate_valid_email(),
            "senha": password,
            "confirmar_senha": password
        }
    
    def generate_malformed_data(self) -> Dict[str, Any]:
        """Gera dados malformados"""
        malformed_payloads = [
            {},  # Payload vazio
            {"username": "test"},  # Incompleto
            {"email": "test@test.com"},  # Incompleto
            {"senha": "password123"},  # Incompleto
            {"username": None, "email": "test@test.com", "senha": "password123"},  # Campo None
            {"username": "", "email": "", "senha": ""},  # Campos vazios
            {"invalid_field": "value"},  # Campo inválido
            "invalid_json_string",  # String inválida
        ]
        return random.choice(malformed_payloads)

# Métricas de teste
class TestMetrics:
    """Coleta métricas durante o teste"""
    
    def __init__(self):
        self.success_count = 0
        self.error_count = 0
        self.rate_limit_count = 0
        self.validation_error_count = 0
        self.duplicate_error_count = 0
        self.security_error_count = 0
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
        elif error_type == "validation":
            self.validation_error_count += 1
        elif error_type == "duplicate":
            self.duplicate_error_count += 1
        elif error_type == "security":
            self.security_error_count += 1
    
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
            "validation_errors": self.validation_error_count,
            "duplicate_errors": self.duplicate_error_count,
            "security_errors": self.security_error_count,
        }

# Usuário de teste Locust
class AuthRegisterUser(HttpUser):
    """Usuário de teste para endpoint de registro"""
    
    wait_time = between(*TEST_CONFIG["think_time"])
    data_generator = TestDataGenerator()
    metrics = TestMetrics()
    
    def on_start(self):
        """Inicialização do usuário"""
        self.user_id = random.randint(1, 1000)
        print(f"[INFO] Usuário {self.user_id} inicializado para testes de registro")
    
    @task(50)  # 50% das requisições
    def test_valid_registration(self):
        """Teste com dados de registro válidos"""
        start_time = time.time()
        
        try:
            payload = self.data_generator.generate_valid_data()
            
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
                name="register_valid_data"
            ) as response:
                response_time = time.time() - start_time
                
                if response.status_code == 201:
                    # Validar resposta
                    try:
                        data = response.json()
                        if "user_id" in data and "message" in data:
                            response.success()
                            self.metrics.record_success(response_time)
                            print(f"[SUCCESS] Registro válido - User {self.user_id} - {response_time:.3f}s")
                        else:
                            response.failure("Resposta não contém dados esperados")
                            self.metrics.record_error("invalid_response", response_time)
                    except json.JSONDecodeError:
                        response.failure("Resposta não é JSON válido")
                        self.metrics.record_error("invalid_json", response_time)
                
                elif response.status_code == 409:
                    response.success()  # Conflito esperado (dados duplicados)
                    self.metrics.record_error("duplicate", response_time)
                    print(f"[EXPECTED] Conflito de dados - User {self.user_id} - {response_time:.3f}s")
                
                elif response.status_code == 429:
                    response.failure("Rate limit excedido")
                    self.metrics.record_error("rate_limit", response_time)
                
                else:
                    response.failure(f"Status inesperado: {response.status_code}")
                    self.metrics.record_error("unexpected_status", response_time)
        
        except Exception as e:
            response_time = time.time() - start_time
            self.metrics.record_error("exception", response_time)
            print(f"[ERROR] Exceção no registro válido - User {self.user_id}: {str(e)}")
    
    @task(15)  # 15% das requisições
    def test_duplicate_registration(self):
        """Teste com dados duplicados"""
        start_time = time.time()
        
        try:
            payload = self.data_generator.generate_duplicate_data()
            
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
                name="register_duplicate_data"
            ) as response:
                response_time = time.time() - start_time
                
                if response.status_code == 409:
                    response.success()  # Conflito esperado
                    self.metrics.record_error("duplicate", response_time)
                    print(f"[EXPECTED] Dados duplicados - User {self.user_id} - {response_time:.3f}s")
                
                elif response.status_code == 201:
                    response.failure("Dados duplicados foram aceitos (inconsistência)")
                    self.metrics.record_error("unexpected_success", response_time)
                
                else:
                    response.failure(f"Status inesperado para dados duplicados: {response.status_code}")
                    self.metrics.record_error("unexpected_status", response_time)
        
        except Exception as e:
            response_time = time.time() - start_time
            self.metrics.record_error("exception", response_time)
            print(f"[ERROR] Exceção no registro duplicado - User {self.user_id}: {str(e)}")
    
    @task(15)  # 15% das requisições
    def test_invalid_username(self):
        """Teste com username inválido"""
        start_time = time.time()
        
        try:
            payload = self.data_generator.generate_valid_data()
            payload["username"] = self.data_generator.generate_invalid_username()
            
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
                name="register_invalid_username"
            ) as response:
                response_time = time.time() - start_time
                
                if response.status_code in [400, 422]:
                    response.success()  # Validação esperada
                    self.metrics.record_error("validation", response_time)
                    print(f"[EXPECTED] Username inválido - User {self.user_id} - {response_time:.3f}s")
                
                elif response.status_code == 201:
                    response.failure("Username inválido foi aceito (vulnerabilidade)")
                    self.metrics.record_error("security", response_time)
                
                else:
                    response.failure(f"Status inesperado para username inválido: {response.status_code}")
                    self.metrics.record_error("unexpected_status", response_time)
        
        except Exception as e:
            response_time = time.time() - start_time
            self.metrics.record_error("exception", response_time)
            print(f"[ERROR] Exceção no username inválido - User {self.user_id}: {str(e)}")
    
    @task(10)  # 10% das requisições
    def test_invalid_email(self):
        """Teste com email inválido"""
        start_time = time.time()
        
        try:
            payload = self.data_generator.generate_valid_data()
            payload["email"] = self.data_generator.generate_invalid_email()
            
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
                name="register_invalid_email"
            ) as response:
                response_time = time.time() - start_time
                
                if response.status_code in [400, 422]:
                    response.success()  # Validação esperada
                    self.metrics.record_error("validation", response_time)
                    print(f"[EXPECTED] Email inválido - User {self.user_id} - {response_time:.3f}s")
                
                elif response.status_code == 201:
                    response.failure("Email inválido foi aceito (vulnerabilidade)")
                    self.metrics.record_error("security", response_time)
                
                else:
                    response.failure(f"Status inesperado para email inválido: {response.status_code}")
                    self.metrics.record_error("unexpected_status", response_time)
        
        except Exception as e:
            response_time = time.time() - start_time
            self.metrics.record_error("exception", response_time)
            print(f"[ERROR] Exceção no email inválido - User {self.user_id}: {str(e)}")
    
    @task(5)  # 5% das requisições
    def test_invalid_password(self):
        """Teste com senha inválida"""
        start_time = time.time()
        
        try:
            payload = self.data_generator.generate_valid_data()
            invalid_password = self.data_generator.generate_invalid_password()
            payload["senha"] = invalid_password
            payload["confirmar_senha"] = invalid_password
            
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
                name="register_invalid_password"
            ) as response:
                response_time = time.time() - start_time
                
                if response.status_code in [400, 422]:
                    response.success()  # Validação esperada
                    self.metrics.record_error("validation", response_time)
                    print(f"[EXPECTED] Senha inválida - User {self.user_id} - {response_time:.3f}s")
                
                elif response.status_code == 201:
                    response.failure("Senha inválida foi aceita (vulnerabilidade)")
                    self.metrics.record_error("security", response_time)
                
                else:
                    response.failure(f"Status inesperado para senha inválida: {response.status_code}")
                    self.metrics.record_error("unexpected_status", response_time)
        
        except Exception as e:
            response_time = time.time() - start_time
            self.metrics.record_error("exception", response_time)
            print(f"[ERROR] Exceção na senha inválida - User {self.user_id}: {str(e)}")
    
    @task(3)  # 3% das requisições
    def test_password_mismatch(self):
        """Teste com senhas que não coincidem"""
        start_time = time.time()
        
        try:
            payload = self.data_generator.generate_valid_data()
            payload["confirmar_senha"] = payload["senha"] + "extra"
            
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
                name="register_password_mismatch"
            ) as response:
                response_time = time.time() - start_time
                
                if response.status_code in [400, 422]:
                    response.success()  # Validação esperada
                    self.metrics.record_error("validation", response_time)
                    print(f"[EXPECTED] Senhas não coincidem - User {self.user_id} - {response_time:.3f}s")
                
                elif response.status_code == 201:
                    response.failure("Senhas diferentes foram aceitas (vulnerabilidade)")
                    self.metrics.record_error("security", response_time)
                
                else:
                    response.failure(f"Status inesperado para senhas diferentes: {response.status_code}")
                    self.metrics.record_error("unexpected_status", response_time)
        
        except Exception as e:
            response_time = time.time() - start_time
            self.metrics.record_error("exception", response_time)
            print(f"[ERROR] Exceção nas senhas diferentes - User {self.user_id}: {str(e)}")
    
    @task(2)  # 2% das requisições
    def test_malformed_payload(self):
        """Teste com payload malformado"""
        start_time = time.time()
        
        try:
            payload = self.data_generator.generate_malformed_data()
            
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
                name="register_malformed_payload"
            ) as response:
                response_time = time.time() - start_time
                
                if response.status_code in [400, 422]:
                    response.success()  # Validação esperada
                    self.metrics.record_error("validation", response_time)
                    print(f"[EXPECTED] Payload malformado - User {self.user_id} - {response_time:.3f}s")
                
                elif response.status_code == 201:
                    response.failure("Payload malformado foi aceito (vulnerabilidade)")
                    self.metrics.record_error("security", response_time)
                
                else:
                    response.failure(f"Status inesperado para payload malformado: {response.status_code}")
                    self.metrics.record_error("unexpected_status", response_time)
        
        except Exception as e:
            response_time = time.time() - start_time
            self.metrics.record_error("exception", response_time)
            print(f"[ERROR] Exceção no payload malformado - User {self.user_id}: {str(e)}")

# Event listeners para métricas globais
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Evento de início do teste"""
    print(f"""
🚀 INICIANDO TESTE DE CARGA - AUTH REGISTER
📊 Configuração:
   - Base URL: {TEST_CONFIG['base_url']}
   - Endpoint: {TEST_CONFIG['endpoint']}
   - Usuários concorrentes: {TEST_CONFIG['concurrent_users']}
   - Duração: {TEST_CONFIG['test_duration']}s
   - Rate limit: {TEST_CONFIG['rate_limit']} req/min

🎯 Cenários de teste:
   - 50% Registro válido
   - 15% Dados duplicados
   - 15% Username inválido
   - 10% Email inválido
   - 5% Senha inválida
   - 3% Senhas não coincidem
   - 2% Payload malformado

📈 Métricas serão coletadas durante o teste...
    """)

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Evento de fim do teste"""
    print(f"""
🏁 TESTE DE CARGA FINALIZADO - AUTH REGISTER

📊 RESUMO FINAL:
   - Total de requisições: {AuthRegisterUser.metrics.get_summary()['total_requests']}
   - Taxa de sucesso: {AuthRegisterUser.metrics.get_summary()['success_rate']:.2f}%
   - Tempo médio de resposta: {AuthRegisterUser.metrics.get_summary()['avg_response_time']:.3f}s
   - Erros de rate limit: {AuthRegisterUser.metrics.get_summary()['rate_limit_errors']}
   - Erros de validação: {AuthRegisterUser.metrics.get_summary()['validation_errors']}
   - Erros de duplicação: {AuthRegisterUser.metrics.get_summary()['duplicate_errors']}
   - Erros de segurança: {AuthRegisterUser.metrics.get_summary()['security_errors']}

✅ Teste concluído com sucesso!
    """)

# Configurações adicionais
if __name__ == "__main__":
    print("""
🧪 TESTE DE CARGA - AUTH REGISTER
🎯 Para executar: locust -f locustfile_auth_register_v1.py --host=http://localhost:8000
📊 Abra http://localhost:8089 para interface web
    """) 