"""
Teste de Carga - Autenticação Sob Carga
Baseado em: backend/app/middleware/auth_middleware.py
Tracing ID: SECURITY_AUTH_LOAD_TEST_20250127_001
Data: 2025-01-27
"""

import time
import logging
import random
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityAuthLoadTest:
    """
    Teste de carga para autenticação sob carga
    Baseado no código real: backend/app/middleware/auth_middleware.py
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = {
            "auth_success": 0,
            "auth_failed": 0,
            "token_expired": 0,
            "invalid_token": 0,
            "permission_denied": 0,
            "response_times": [],
            "concurrent_sessions": 0
        }
        
        # Endpoints baseados no código real
        self.protected_endpoints = [
            "/api/nichos",
            "/api/categorias", 
            "/api/execucoes",
            "/api/payments",
            "/api/analytics",
            "/api/credentials"
        ]
        
        # Dados de teste baseados no sistema real
        self.test_users = [
            {"email": "admin@omnikeywords.com", "password": "admin_password_2025", "role": "admin"},
            {"email": "user1@omnikeywords.com", "password": "user_password_2025", "role": "user"},
            {"email": "user2@omnikeywords.com", "password": "user_password_2025", "role": "user"}
        ]
        
        logger.info("Teste de Autenticação Sob Carga inicializado")

    def authenticate_user(self, user_data: Dict[str, str]) -> str:
        """
        Autentica usuário e retorna token
        Baseado em: backend/app/middleware/auth_middleware.py linha 50-80
        """
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"email": user_data["email"], "password": user_data["password"]},
                timeout=10
            )
            
            if response.status_code == 200:
                token_data = response.json()
                return token_data.get("access_token", "")
            else:
                logger.warning(f"Falha na autenticação de {user_data['email']}: {response.status_code}")
                return ""
                
        except Exception as e:
            logger.error(f"Erro durante autenticação de {user_data['email']}: {str(e)}")
            return ""

    def make_authenticated_request(self, endpoint: str, token: str, user_role: str, request_id: int = 0) -> Dict[str, Any]:
        """
        Faz requisição autenticada e registra métricas
        Baseado em: backend/app/middleware/auth_middleware.py linha 100-150
        """
        start_time = time.time()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Dados baseados em requisições reais
            if endpoint == "/api/nichos":
                if request_id % 2 == 0:  # GET
                    response = self.session.get(f"{self.base_url}{endpoint}", headers=headers, timeout=10)
                else:  # POST
                    nicho_data = {
                        "nome": f"Nicho Teste {request_id}",
                        "descricao": f"Descrição do nicho {request_id}",
                        "categoria": "tecnologia"
                    }
                    response = self.session.post(f"{self.base_url}{endpoint}", json=nicho_data, headers=headers, timeout=10)
                    
            elif endpoint == "/api/categorias":
                response = self.session.get(f"{self.base_url}{endpoint}", headers=headers, timeout=10)
                
            elif endpoint == "/api/execucoes":
                if request_id % 3 == 0:  # GET
                    response = self.session.get(f"{self.base_url}{endpoint}", headers=headers, timeout=10)
                else:  # POST
                    execucao_data = {
                        "nome": f"Execução Teste {request_id}",
                        "tipo": "keyword_research",
                        "parametros": {"keywords": ["teste", "palavra"]}
                    }
                    response = self.session.post(f"{self.base_url}{endpoint}", json=execucao_data, headers=headers, timeout=10)
                    
            elif endpoint == "/api/payments":
                response = self.session.get(f"{self.base_url}{endpoint}", headers=headers, timeout=10)
                
            elif endpoint == "/api/analytics":
                response = self.session.get(f"{self.base_url}{endpoint}/overview", headers=headers, timeout=10)
                
            elif endpoint == "/api/credentials":
                response = self.session.get(f"{self.base_url}{endpoint}", headers=headers, timeout=10)
                
            else:
                response = self.session.get(f"{self.base_url}{endpoint}", headers=headers, timeout=10)
            
            duration = time.time() - start_time
            
            # Registrar métricas baseadas no código real
            result = {
                "endpoint": endpoint,
                "status_code": response.status_code,
                "duration": duration,
                "user_role": user_role,
                "request_id": request_id,
                "auth_success": response.status_code == 200,
                "auth_failed": response.status_code == 401,
                "permission_denied": response.status_code == 403
            }
            
            # Classificar resultado
            if response.status_code == 200:
                self.results["auth_success"] += 1
                
            elif response.status_code == 401:
                self.results["auth_failed"] += 1
                error_data = response.json() if response.content else {}
                if "expired" in str(error_data).lower():
                    self.results["token_expired"] += 1
                else:
                    self.results["invalid_token"] += 1
                    
            elif response.status_code == 403:
                self.results["permission_denied"] += 1
                logger.info(f"Permissão negada: {endpoint} - Role: {user_role}")
                
            else:
                self.results["auth_failed"] += 1
                logger.warning(f"Requisição falhou: {endpoint} - Status {response.status_code}")
            
            self.results["response_times"].append(duration)
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            self.results["auth_failed"] += 1
            logger.error(f"Erro na requisição {endpoint}: {str(e)}")
            
            return {
                "endpoint": endpoint,
                "status_code": 0,
                "duration": duration,
                "user_role": user_role,
                "request_id": request_id,
                "auth_success": False,
                "auth_failed": True,
                "error": str(e)
            }

    def test_concurrent_authentication(self, concurrent_users: int = 50, requests_per_user: int = 10) -> Dict[str, Any]:
        """
        Teste de autenticação concorrente
        Baseado em: backend/app/middleware/auth_middleware.py linha 100-150
        """
        logger.info(f"Iniciando teste de autenticação concorrente: {concurrent_users} usuários, {requests_per_user} req/usuário")
        
        start_time = time.time()
        total_requests = concurrent_users * requests_per_user
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = []
            
            for user_id in range(concurrent_users):
                user_data = random.choice(self.test_users)
                
                for req_id in range(requests_per_user):
                    endpoint = random.choice(self.protected_endpoints)
                    
                    future = executor.submit(
                        self._authenticate_and_request,
                        user_data,
                        endpoint,
                        req_id
                    )
                    futures.append(future)
            
            # Aguardar conclusão
            completed = 0
            for future in as_completed(futures):
                try:
                    future.result()
                    completed += 1
                    
                    if completed % 10 == 0:
                        logger.info(f"Progresso: {completed}/{total_requests} requisições completadas")
                        
                except Exception as e:
                    logger.error(f"Erro no teste: {str(e)}")
        
        return self.analyze_results("Autenticação Concorrente")

    def _authenticate_and_request(self, user_data: Dict[str, str], endpoint: str, request_id: int) -> Dict[str, Any]:
        """Autentica usuário e faz requisição"""
        # Autenticar
        token = self.authenticate_user(user_data)
        
        if not token:
            return {
                "endpoint": endpoint,
                "status_code": 401,
                "auth_success": False,
                "user_role": user_data["role"],
                "request_id": request_id,
                "error": "Falha na autenticação"
            }
        
        # Fazer requisição autenticada
        return self.make_authenticated_request(endpoint, token, user_data["role"], request_id)

    def test_session_management(self, session_count: int = 100) -> Dict[str, Any]:
        """
        Teste de gerenciamento de sessões
        Baseado em: backend/app/middleware/auth_middleware.py linha 200-220
        """
        logger.info(f"Iniciando teste de gerenciamento de sessões: {session_count} sessões")
        
        sessions = []
        start_time = time.time()
        
        # Criar múltiplas sessões
        for i in range(session_count):
            user_data = random.choice(self.test_users)
            token = self.authenticate_user(user_data)
            
            if token:
                sessions.append({
                    "user": user_data,
                    "token": token,
                    "created_at": time.time()
                })
        
        self.results["concurrent_sessions"] = len(sessions)
        
        # Testar requisições com diferentes sessões
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = []
            
            for i, session in enumerate(sessions):
                endpoint = random.choice(self.protected_endpoints)
                
                future = executor.submit(
                    self.make_authenticated_request,
                    endpoint,
                    session["token"],
                    session["user"]["role"],
                    i
                )
                futures.append(future)
            
            # Aguardar conclusão
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Erro no teste de sessão: {str(e)}")
        
        return self.analyze_results("Gerenciamento de Sessões")

    def test_token_validation_under_load(self, requests_per_second: int = 100, duration_seconds: int = 30) -> Dict[str, Any]:
        """
        Teste de validação de tokens sob carga
        Baseado em: backend/app/middleware/auth_middleware.py linha 100-150
        """
        logger.info(f"Iniciando teste de validação de tokens: {requests_per_second} req/s por {duration_seconds}s")
        
        # Obter tokens válidos
        valid_tokens = []
        for user_data in self.test_users:
            token = self.authenticate_user(user_data)
            if token:
                valid_tokens.append({"token": token, "user": user_data})
        
        if not valid_tokens:
            logger.error("Não foi possível obter tokens válidos")
            return {"error": "Falha na obtenção de tokens"}
        
        # Tokens inválidos para teste
        invalid_tokens = [
            "invalid_token_1",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid",
            "expired_token_test",
            ""
        ]
        
        total_requests = requests_per_second * duration_seconds
        delay = 1.0 / requests_per_second
        
        start_time = time.time()
        request_id = 0
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = []
            
            while time.time() - start_time < duration_seconds:
                endpoint = random.choice(self.protected_endpoints)
                
                # Alternar entre tokens válidos e inválidos
                if request_id % 4 == 0:  # 25% tokens inválidos
                    token_data = random.choice(invalid_tokens)
                    if isinstance(token_data, dict):
                        token = token_data["token"]
                        user_role = token_data["user"]["role"]
                    else:
                        token = token_data
                        user_role = "unknown"
                else:
                    token_data = random.choice(valid_tokens)
                    token = token_data["token"]
                    user_role = token_data["user"]["role"]
                
                future = executor.submit(
                    self.make_authenticated_request,
                    endpoint,
                    token,
                    user_role,
                    request_id
                )
                futures.append(future)
                
                request_id += 1
                time.sleep(delay)
            
            # Aguardar conclusão
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Erro no teste: {str(e)}")
        
        return self.analyze_results("Validação de Tokens Sob Carga")

    def test_permission_validation(self) -> Dict[str, Any]:
        """
        Teste de validação de permissões
        Baseado em: backend/app/middleware/auth_middleware.py linha 60-90
        """
        logger.info("Iniciando teste de validação de permissões")
        
        # Testar diferentes combinações de usuário/endpoint
        test_cases = [
            # (usuário, endpoint, deve_ter_acesso)
            ("admin", "/api/credentials", True),
            ("user", "/api/credentials", False),
            ("admin", "/api/analytics", True),
            ("user", "/api/analytics", False),
            ("admin", "/api/execucoes", True),
            ("user", "/api/execucoes", True),  # Usuários podem acessar execuções
            ("admin", "/api/nichos", True),
            ("user", "/api/nichos", True),     # Usuários podem acessar nichos
        ]
        
        results = []
        
        for user_role, endpoint, should_have_access in test_cases:
            # Encontrar usuário com a role
            user_data = next((u for u in self.test_users if u["role"] == user_role), None)
            if not user_data:
                continue
            
            # Autenticar
            token = self.authenticate_user(user_data)
            if not token:
                continue
            
            # Fazer requisição
            result = self.make_authenticated_request(endpoint, token, user_role, len(results))
            
            # Verificar se o resultado está correto
            access_granted = result["status_code"] == 200
            test_passed = access_granted == should_have_access
            
            results.append({
                "user_role": user_role,
                "endpoint": endpoint,
                "should_have_access": should_have_access,
                "access_granted": access_granted,
                "test_passed": test_passed,
                "status_code": result["status_code"]
            })
        
        return {
            "test_type": "Validação de Permissões",
            "total_tests": len(results),
            "passed_tests": sum(1 for r in results if r["test_passed"]),
            "failed_tests": sum(1 for r in results if not r["test_passed"]),
            "success_rate": (sum(1 for r in results if r["test_passed"]) / len(results)) * 100 if results else 0,
            "details": results
        }

    def analyze_results(self, test_name: str) -> Dict[str, Any]:
        """Analisa resultados do teste"""
        total_requests = (self.results["auth_success"] + 
                         self.results["auth_failed"])
        
        if total_requests == 0:
            return {"error": "Nenhuma requisição foi feita"}
        
        avg_response_time = sum(self.results["response_times"]) / len(self.results["response_times"]) if self.results["response_times"] else 0
        
        return {
            "test_name": test_name,
            "total_requests": total_requests,
            "auth_success": self.results["auth_success"],
            "auth_failed": self.results["auth_failed"],
            "token_expired": self.results["token_expired"],
            "invalid_token": self.results["invalid_token"],
            "permission_denied": self.results["permission_denied"],
            "concurrent_sessions": self.results["concurrent_sessions"],
            "auth_success_rate": (self.results["auth_success"] / total_requests) * 100,
            "avg_response_time": avg_response_time
        }

    def run_complete_test_suite(self) -> Dict[str, Any]:
        """Executa suite completa de testes de autenticação"""
        logger.info("Iniciando suite completa de testes de autenticação sob carga")
        
        results = {
            "timestamp": time.time(),
            "tests": {}
        }
        
        # Teste 1: Autenticação concorrente
        results["tests"]["concurrent_authentication"] = self.test_concurrent_authentication()
        
        # Reset para próximo teste
        self.results = {
            "auth_success": 0,
            "auth_failed": 0,
            "token_expired": 0,
            "invalid_token": 0,
            "permission_denied": 0,
            "response_times": [],
            "concurrent_sessions": 0
        }
        
        # Teste 2: Gerenciamento de sessões
        results["tests"]["session_management"] = self.test_session_management()
        
        # Reset para próximo teste
        self.results = {
            "auth_success": 0,
            "auth_failed": 0,
            "token_expired": 0,
            "invalid_token": 0,
            "permission_denied": 0,
            "response_times": [],
            "concurrent_sessions": 0
        }
        
        # Teste 3: Validação de tokens sob carga
        results["tests"]["token_validation"] = self.test_token_validation_under_load()
        
        # Teste 4: Validação de permissões
        results["tests"]["permission_validation"] = self.test_permission_validation()
        
        logger.info("Suite completa de testes de autenticação finalizada")
        return results

if __name__ == "__main__":
    # Executar testes
    test = SecurityAuthLoadTest()
    results = test.run_complete_test_suite()
    
    # Exibir resultados
    print("\n=== RESULTADOS DOS TESTES DE AUTENTICAÇÃO SOB CARGA ===")
    for test_name, test_result in results["tests"].items():
        print(f"\n{test_name.upper()}:")
        for key, value in test_result.items():
            print(f"  {key}: {value}") 