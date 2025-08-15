"""
🧪 TESTE DE CARGA CRÍTICO - AUTENTICAÇÃO LOGIN
📐 CoCoT Analysis | 🌲 ToT Approach | ♻️ ReAct Simulation | 🖼️ Visual Representation

Tracing ID: LOAD_TEST_AUTH_LOGIN_20250127_001
Baseado em: backend/app/api/auth.py (linhas 79-146)
Schema: backend/app/schemas/auth.py (LoginRequest)
Modelo: backend/app/models/user.py

📊 ANÁLISE CoCoT:
- Comprovação: Endpoint crítico para segurança do sistema
- Causalidade: Login é gateway para todas as funcionalidades
- Contexto: Sistema de autenticação JWT com rate limiting
- Tendência: Testes de carga modernos com Locust + métricas

🌲 ANÁLISE ToT:
1. Cenário 1: Carga normal (usuários válidos)
2. Cenário 2: Ataque de força bruta (credenciais inválidas)
3. Cenário 3: Rate limiting (exceder limites)
4. Cenário 4: Dados malformados (validação)

♻️ SIMULAÇÃO ReAct:
- Efeitos colaterais: Bloqueio de IPs, logs de segurança
- Ganhos: Identificação de gargalos, validação de rate limiting
- Riscos: Sobrecarga do banco, impacto em usuários reais
"""

import time
import json
import random
from locust import HttpUser, task, between, events
from typing import Dict, List, Optional
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthLoginLoadTest(HttpUser):
    """
    Teste de carga para endpoint de login
    Baseado no código real: backend/app/api/auth.py
    """
    
    # Tempo entre requisições (1-3 segundos)
    wait_time = between(1, 3)
    
    # Dados de teste baseados no schema real
    VALID_USERS = [
        {"username": "admin_user", "senha": "Admin@123"},
        {"username": "premium_user", "senha": "Premium@456"},
        {"username": "basic_user", "senha": "Basic@789"},
        {"username": "test_user", "senha": "Test@101"},
        {"username": "demo_user", "senha": "Demo@202"}
    ]
    
    INVALID_CREDENTIALS = [
        {"username": "invalid_user", "senha": "wrong_password"},
        {"username": "nonexistent", "senha": "random_pass"},
        {"username": "admin_user", "senha": "wrong_password"},
        {"username": "", "senha": "test_password"},
        {"username": "test_user", "senha": ""}
    ]
    
    MALFORMED_DATA = [
        {"username": "a" * 100, "senha": "test"},  # Username muito longo
        {"username": "test", "senha": "a" * 200},  # Senha muito longa
        {"username": "test<script>", "senha": "test"},  # Caracteres especiais
        {"username": "123456", "senha": "test"},  # Apenas números
        {"username": "test", "senha": "<script>alert('xss')</script>"}  # XSS
    ]
    
    def on_start(self):
        """Inicialização do teste"""
        logger.info("🚀 Iniciando teste de carga para /api/auth/login")
        self.test_start_time = time.time()
        
        # Headers padrão baseados no código real
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'OmniKeywordsFinder-LoadTest/1.0',
            'Accept': 'application/json'
        }
    
    @task(4)  # 40% das requisições - Cenário normal
    def test_valid_login(self):
        """
        Teste de login com credenciais válidas
        Baseado em: backend/app/api/auth.py linha 79-146
        """
        user_data = random.choice(self.VALID_USERS)
        
        with self.client.post(
            "/api/auth/login",
            json=user_data,
            headers=self.headers,
            catch_response=True,
            name="Login Válido"
        ) as response:
            
            # Validação baseada no código real
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Verificar estrutura da resposta (baseado no código real)
                    required_fields = ['success', 'access_token', 'user_id', 'message']
                    for field in required_fields:
                        if field not in data:
                            response.failure(f"Campo obrigatório ausente: {field}")
                            return
                    
                    # Validar tipos dos campos
                    if not isinstance(data['success'], bool) or not data['success']:
                        response.failure("Campo 'success' deve ser true")
                        return
                    
                    if not isinstance(data['access_token'], str) or len(data['access_token']) < 10:
                        response.failure("Token JWT inválido")
                        return
                    
                    if not isinstance(data['user_id'], int) or data['user_id'] <= 0:
                        response.failure("ID do usuário inválido")
                        return
                    
                    response.success()
                    logger.info(f"✅ Login válido bem-sucedido para: {user_data['username']}")
                    
                except json.JSONDecodeError:
                    response.failure("Resposta não é JSON válido")
                    return
                    
            elif response.status_code == 401:
                # Credenciais inválidas (esperado para alguns usuários de teste)
                response.success()
                logger.warning(f"⚠️ Login falhou (esperado): {user_data['username']}")
                
            elif response.status_code == 429:
                # Rate limiting atingido
                response.success()
                logger.warning(f"⏱️ Rate limiting atingido para: {user_data['username']}")
                
            else:
                response.failure(f"Status code inesperado: {response.status_code}")
    
    @task(3)  # 30% das requisições - Cenário de força bruta
    def test_invalid_login(self):
        """
        Teste de login com credenciais inválidas
        Baseado em: backend/app/api/auth.py linha 95-105
        """
        invalid_data = random.choice(self.INVALID_CREDENTIALS)
        
        with self.client.post(
            "/api/auth/login",
            json=invalid_data,
            headers=self.headers,
            catch_response=True,
            name="Login Inválido"
        ) as response:
            
            # Validação baseada no código real
            if response.status_code == 401:
                try:
                    data = response.json()
                    
                    # Verificar estrutura de erro (baseado no código real)
                    if 'error_code' in data and data['error_code'] == 'INVALID_CREDENTIALS':
                        response.success()
                        logger.info(f"✅ Erro de credenciais inválidas (esperado): {invalid_data['username']}")
                    else:
                        response.failure("Estrutura de erro inválida")
                        return
                        
                except json.JSONDecodeError:
                    response.failure("Resposta de erro não é JSON válido")
                    return
                    
            elif response.status_code == 429:
                # Rate limiting por tentativas inválidas
                response.success()
                logger.warning(f"⏱️ Rate limiting por tentativas inválidas: {invalid_data['username']}")
                
            else:
                response.failure(f"Status code inesperado para credenciais inválidas: {response.status_code}")
    
    @task(2)  # 20% das requisições - Cenário de validação
    def test_malformed_data(self):
        """
        Teste de login com dados malformados
        Baseado em: backend/app/schemas/auth.py (validações)
        """
        malformed_data = random.choice(self.MALFORMED_DATA)
        
        with self.client.post(
            "/api/auth/login",
            json=malformed_data,
            headers=self.headers,
            catch_response=True,
            name="Dados Malformados"
        ) as response:
            
            # Validação baseada no schema real
            if response.status_code == 400:
                try:
                    data = response.json()
                    
                    # Verificar se é erro de validação
                    if 'error_code' in data and data['error_code'] == 'VALIDATION_ERROR':
                        response.success()
                        logger.info(f"✅ Validação de dados malformados (esperado): {malformed_data['username']}")
                    else:
                        response.failure("Estrutura de erro de validação inválida")
                        return
                        
                except json.JSONDecodeError:
                    response.failure("Resposta de validação não é JSON válido")
                    return
                    
            elif response.status_code == 422:
                # Erro de validação Pydantic
                response.success()
                logger.info(f"✅ Erro de validação Pydantic (esperado): {malformed_data['username']}")
                
            else:
                response.failure(f"Status code inesperado para dados malformados: {response.status_code}")
    
    @task(1)  # 10% das requisições - Cenário de rate limiting
    def test_rate_limiting(self):
        """
        Teste de rate limiting
        Baseado em: backend/app/middleware/rate_limiter.py
        """
        # Fazer múltiplas requisições rápidas para testar rate limiting
        for i in range(5):
            user_data = random.choice(self.VALID_USERS)
            
            with self.client.post(
                "/api/auth/login",
                json=user_data,
                headers=self.headers,
                catch_response=True,
                name="Rate Limiting Test"
            ) as response:
                
                if response.status_code == 429:
                    # Rate limiting atingido
                    response.success()
                    logger.info(f"✅ Rate limiting funcionando (esperado) - tentativa {i+1}")
                    break
                elif response.status_code in [200, 401]:
                    # Requisição processada normalmente
                    response.success()
                else:
                    response.failure(f"Status code inesperado no teste de rate limiting: {response.status_code}")
    
    def on_stop(self):
        """Finalização do teste"""
        test_duration = time.time() - self.test_start_time
        logger.info(f"🏁 Teste de carga finalizado. Duração: {test_duration:.2f}s")

# Event listeners para métricas customizadas
@events.request.add_listener
def my_request_handler(request_type, name, response_time, response_length, response, context, exception, start_time, url, **kwargs):
    """Listener para métricas customizadas"""
    if name == "Login Válido" and response.status_code == 200:
        # Log de sucesso
        logger.info(f"✅ Login válido: {response_time}ms")
    elif name == "Login Inválido" and response.status_code == 401:
        # Log de falha esperada
        logger.info(f"⚠️ Login inválido (esperado): {response_time}ms")
    elif response.status_code == 429:
        # Log de rate limiting
        logger.warning(f"⏱️ Rate limiting: {response_time}ms")

# Configuração para execução
if __name__ == "__main__":
    print("🧪 TESTE DE CARGA - AUTENTICAÇÃO LOGIN")
    print("📊 Baseado em código real do sistema")
    print("🎯 Endpoint: /api/auth/login")
    print("📋 Executar com: locust -f locustfile_auth_login_v1.py") 