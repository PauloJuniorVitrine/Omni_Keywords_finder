"""
Teste de Carga - RBAC Sob Carga
Baseado em: backend/app/api/rbac.py
Tracing ID: SECURITY_RBAC_LOAD_TEST_20250127_001
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

class SecurityRBACLoadTest:
    """
    Teste de carga para RBAC sob carga
    Baseado no código real: backend/app/api/rbac.py
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = {
            "rbac_checks": 0,
            "permission_granted": 0,
            "permission_denied": 0,
            "role_validation": 0,
            "response_times": [],
            "concurrent_checks": 0
        }
        
        # Endpoints RBAC baseados no código real
        self.rbac_endpoints = [
            "/api/rbac/usuarios",
            "/api/rbac/permissoes",
            "/api/rbac/papeis",
            "/api/rbac/audit"
        ]
        
        # Dados de teste baseados no sistema real
        self.test_users = [
            {"email": "admin@omnikeywords.com", "password": "admin_password_2025", "role": "admin"},
            {"email": "user1@omnikeywords.com", "password": "user_password_2025", "role": "user"},
            {"email": "user2@omnikeywords.com", "password": "user_password_2025", "role": "user"}
        ]
        
        # Permissões baseadas no código real
        self.permissions = [
            "users:read",
            "users:write", 
            "permissions:read",
            "permissions:write",
            "roles:read",
            "roles:write",
            "audit:read",
            "audit:write"
        ]
        
        logger.info("Teste de RBAC Sob Carga inicializado")

    def authenticate_user(self, user_data: Dict[str, str]) -> str:
        """Autentica usuário e retorna token"""
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

    def make_rbac_request(self, endpoint: str, token: str, user_role: str, request_id: int = 0) -> Dict[str, Any]:
        """
        Faz requisição RBAC e registra métricas
        Baseado em: backend/app/api/rbac.py
        """
        start_time = time.time()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Dados baseados em requisições RBAC reais
            if endpoint == "/api/rbac/usuarios":
                if request_id % 3 == 0:  # GET - Listar usuários
                    response = self.session.get(f"{self.base_url}{endpoint}", headers=headers, timeout=10)
                elif request_id % 3 == 1:  # POST - Criar usuário
                    user_data = {
                        "nome": f"Usuário Teste {request_id}",
                        "email": f"teste{request_id}@example.com",
                        "senha": "senha_teste_2025",
                        "role": "user"
                    }
                    response = self.session.post(f"{self.base_url}{endpoint}", json=user_data, headers=headers, timeout=10)
                else:  # PUT - Atualizar usuário
                    user_data = {
                        "nome": f"Usuário Atualizado {request_id}",
                        "role": "user"
                    }
                    response = self.session.put(f"{self.base_url}{endpoint}/1", json=user_data, headers=headers, timeout=10)
                    
            elif endpoint == "/api/rbac/permissoes":
                if request_id % 2 == 0:  # GET - Listar permissões
                    response = self.session.get(f"{self.base_url}{endpoint}", headers=headers, timeout=10)
                else:  # POST - Criar permissão
                    permission_data = {
                        "nome": f"permission_test_{request_id}",
                        "descricao": f"Permissão de teste {request_id}",
                        "recurso": "test_resource",
                        "acao": "read"
                    }
                    response = self.session.post(f"{self.base_url}{endpoint}", json=permission_data, headers=headers, timeout=10)
                    
            elif endpoint == "/api/rbac/papeis":
                if request_id % 2 == 0:  # GET - Listar papéis
                    response = self.session.get(f"{self.base_url}{endpoint}", headers=headers, timeout=10)
                else:  # POST - Criar papel
                    role_data = {
                        "nome": f"papel_teste_{request_id}",
                        "descricao": f"Papel de teste {request_id}",
                        "permissoes": ["users:read", "permissions:read"]
                    }
                    response = self.session.post(f"{self.base_url}{endpoint}", json=role_data, headers=headers, timeout=10)
                    
            elif endpoint == "/api/rbac/audit":
                # GET - Consultar logs de auditoria
                params = {
                    "data_inicio": "2025-01-01",
                    "data_fim": "2025-01-27",
                    "tipo": "rbac",
                    "limit": 50
                }
                response = self.session.get(f"{self.base_url}{endpoint}", params=params, headers=headers, timeout=10)
                
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
                "rbac_check": True,
                "permission_granted": response.status_code == 200,
                "permission_denied": response.status_code == 403,
                "unauthorized": response.status_code == 401
            }
            
            # Classificar resultado
            if response.status_code == 200:
                self.results["permission_granted"] += 1
                self.results["rbac_checks"] += 1
                
            elif response.status_code == 403:
                self.results["permission_denied"] += 1
                self.results["rbac_checks"] += 1
                logger.info(f"Permissão negada: {endpoint} - Role: {user_role}")
                
            elif response.status_code == 401:
                self.results["rbac_checks"] += 1
                logger.warning(f"Não autorizado: {endpoint} - Role: {user_role}")
                
            else:
                self.results["rbac_checks"] += 1
                logger.warning(f"Requisição RBAC falhou: {endpoint} - Status {response.status_code}")
            
            self.results["response_times"].append(duration)
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            self.results["rbac_checks"] += 1
            logger.error(f"Erro na requisição RBAC {endpoint}: {str(e)}")
            
            return {
                "endpoint": endpoint,
                "status_code": 0,
                "duration": duration,
                "user_role": user_role,
                "request_id": request_id,
                "rbac_check": True,
                "permission_granted": False,
                "permission_denied": False,
                "error": str(e)
            }

    def test_concurrent_rbac_checks(self, concurrent_users: int = 30, requests_per_user: int = 20) -> Dict[str, Any]:
        """
        Teste de verificações RBAC concorrentes
        Baseado em: backend/app/api/rbac.py
        """
        logger.info(f"Iniciando teste de verificações RBAC concorrentes: {concurrent_users} usuários, {requests_per_user} req/usuário")
        
        start_time = time.time()
        total_requests = concurrent_users * requests_per_user
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = []
            
            for user_id in range(concurrent_users):
                user_data = random.choice(self.test_users)
                
                for req_id in range(requests_per_user):
                    endpoint = random.choice(self.rbac_endpoints)
                    
                    future = executor.submit(
                        self._authenticate_and_rbac_request,
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
                    
                    if completed % 50 == 0:
                        logger.info(f"Progresso: {completed}/{total_requests} verificações RBAC completadas")
                        
                except Exception as e:
                    logger.error(f"Erro no teste: {str(e)}")
        
        return self.analyze_results("Verificações RBAC Concorrentes")

    def _authenticate_and_rbac_request(self, user_data: Dict[str, str], endpoint: str, request_id: int) -> Dict[str, Any]:
        """Autentica usuário e faz requisição RBAC"""
        # Autenticar
        token = self.authenticate_user(user_data)
        
        if not token:
            return {
                "endpoint": endpoint,
                "status_code": 401,
                "rbac_check": True,
                "permission_granted": False,
                "user_role": user_data["role"],
                "request_id": request_id,
                "error": "Falha na autenticação"
            }
        
        # Fazer requisição RBAC
        return self.make_rbac_request(endpoint, token, user_data["role"], request_id)

    def test_role_based_access_control(self) -> Dict[str, Any]:
        """
        Teste de controle de acesso baseado em roles
        Baseado em: backend/app/api/rbac.py
        """
        logger.info("Iniciando teste de controle de acesso baseado em roles")
        
        # Testar diferentes combinações de role/endpoint
        test_cases = [
            # (role, endpoint, método, deve_ter_acesso)
            ("admin", "/api/rbac/usuarios", "GET", True),
            ("admin", "/api/rbac/usuarios", "POST", True),
            ("admin", "/api/rbac/permissoes", "GET", True),
            ("admin", "/api/rbac/permissoes", "POST", True),
            ("admin", "/api/rbac/papeis", "GET", True),
            ("admin", "/api/rbac/papeis", "POST", True),
            ("admin", "/api/rbac/audit", "GET", True),
            ("user", "/api/rbac/usuarios", "GET", False),
            ("user", "/api/rbac/usuarios", "POST", False),
            ("user", "/api/rbac/permissoes", "GET", False),
            ("user", "/api/rbac/permissoes", "POST", False),
            ("user", "/api/rbac/papeis", "GET", False),
            ("user", "/api/rbac/papeis", "POST", False),
            ("user", "/api/rbac/audit", "GET", False),
        ]
        
        results = []
        
        for user_role, endpoint, method, should_have_access in test_cases:
            # Encontrar usuário com a role
            user_data = next((u for u in self.test_users if u["role"] == user_role), None)
            if not user_data:
                continue
            
            # Autenticar
            token = self.authenticate_user(user_data)
            if not token:
                continue
            
            # Fazer requisição RBAC
            result = self.make_rbac_request(endpoint, token, user_role, len(results))
            
            # Verificar se o resultado está correto
            access_granted = result["status_code"] == 200
            test_passed = access_granted == should_have_access
            
            results.append({
                "user_role": user_role,
                "endpoint": endpoint,
                "method": method,
                "should_have_access": should_have_access,
                "access_granted": access_granted,
                "test_passed": test_passed,
                "status_code": result["status_code"]
            })
        
        return {
            "test_type": "Controle de Acesso Baseado em Roles",
            "total_tests": len(results),
            "passed_tests": sum(1 for r in results if r["test_passed"]),
            "failed_tests": sum(1 for r in results if not r["test_passed"]),
            "success_rate": (sum(1 for r in results if r["test_passed"]) / len(results)) * 100 if results else 0,
            "details": results
        }

    def test_permission_validation_under_load(self, requests_per_second: int = 80, duration_seconds: int = 30) -> Dict[str, Any]:
        """
        Teste de validação de permissões sob carga
        Baseado em: backend/app/api/rbac.py
        """
        logger.info(f"Iniciando teste de validação de permissões: {requests_per_second} req/s por {duration_seconds}s")
        
        # Obter tokens válidos
        valid_tokens = []
        for user_data in self.test_users:
            token = self.authenticate_user(user_data)
            if token:
                valid_tokens.append({"token": token, "user": user_data})
        
        if not valid_tokens:
            logger.error("Não foi possível obter tokens válidos")
            return {"error": "Falha na obtenção de tokens"}
        
        total_requests = requests_per_second * duration_seconds
        delay = 1.0 / requests_per_second
        
        start_time = time.time()
        request_id = 0
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = []
            
            while time.time() - start_time < duration_seconds:
                endpoint = random.choice(self.rbac_endpoints)
                token_data = random.choice(valid_tokens)
                
                future = executor.submit(
                    self.make_rbac_request,
                    endpoint,
                    token_data["token"],
                    token_data["user"]["role"],
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
        
        return self.analyze_results("Validação de Permissões Sob Carga")

    def test_audit_log_generation(self) -> Dict[str, Any]:
        """
        Teste de geração de logs de auditoria RBAC
        Baseado em: backend/app/api/rbac.py
        """
        logger.info("Iniciando teste de geração de logs de auditoria RBAC")
        
        # Fazer várias operações RBAC para gerar logs
        operations = []
        
        for user_data in self.test_users:
            token = self.authenticate_user(user_data)
            if not token:
                continue
            
            # Fazer diferentes operações
            for endpoint in self.rbac_endpoints:
                result = self.make_rbac_request(endpoint, token, user_data["role"], len(operations))
                operations.append({
                    "user_role": user_data["role"],
                    "endpoint": endpoint,
                    "status_code": result["status_code"],
                    "timestamp": time.time()
                })
        
        # Consultar logs de auditoria
        admin_user = next((u for u in self.test_users if u["role"] == "admin"), None)
        if admin_user:
            token = self.authenticate_user(admin_user)
            if token:
                headers = {"Authorization": f"Bearer {token}"}
                
                try:
                    response = self.session.get(
                        f"{self.base_url}/api/rbac/audit",
                        headers=headers,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        audit_data = response.json()
                        return {
                            "test_type": "Geração de Logs de Auditoria RBAC",
                            "operations_performed": len(operations),
                            "audit_logs_retrieved": len(audit_data.get("logs", [])),
                            "audit_system_working": True,
                            "details": {
                                "operations": operations[:10],  # Primeiras 10 operações
                                "audit_logs_count": len(audit_data.get("logs", []))
                            }
                        }
                    else:
                        return {
                            "test_type": "Geração de Logs de Auditoria RBAC",
                            "operations_performed": len(operations),
                            "audit_system_working": False,
                            "error": f"Status code: {response.status_code}"
                        }
                        
                except Exception as e:
                    return {
                        "test_type": "Geração de Logs de Auditoria RBAC",
                        "operations_performed": len(operations),
                        "audit_system_working": False,
                        "error": str(e)
                    }
        
        return {
            "test_type": "Geração de Logs de Auditoria RBAC",
            "operations_performed": len(operations),
            "audit_system_working": False,
            "error": "Não foi possível autenticar usuário admin"
        }

    def analyze_results(self, test_name: str) -> Dict[str, Any]:
        """Analisa resultados do teste"""
        total_checks = self.results["rbac_checks"]
        
        if total_checks == 0:
            return {"error": "Nenhuma verificação RBAC foi feita"}
        
        avg_response_time = sum(self.results["response_times"]) / len(self.results["response_times"]) if self.results["response_times"] else 0
        
        return {
            "test_name": test_name,
            "total_rbac_checks": total_checks,
            "permission_granted": self.results["permission_granted"],
            "permission_denied": self.results["permission_denied"],
            "concurrent_checks": self.results["concurrent_checks"],
            "permission_grant_rate": (self.results["permission_granted"] / total_checks) * 100,
            "permission_deny_rate": (self.results["permission_denied"] / total_checks) * 100,
            "avg_response_time": avg_response_time
        }

    def run_complete_test_suite(self) -> Dict[str, Any]:
        """Executa suite completa de testes RBAC"""
        logger.info("Iniciando suite completa de testes RBAC sob carga")
        
        results = {
            "timestamp": time.time(),
            "tests": {}
        }
        
        # Teste 1: Verificações RBAC concorrentes
        results["tests"]["concurrent_rbac_checks"] = self.test_concurrent_rbac_checks()
        
        # Reset para próximo teste
        self.results = {
            "rbac_checks": 0,
            "permission_granted": 0,
            "permission_denied": 0,
            "role_validation": 0,
            "response_times": [],
            "concurrent_checks": 0
        }
        
        # Teste 2: Controle de acesso baseado em roles
        results["tests"]["role_based_access_control"] = self.test_role_based_access_control()
        
        # Reset para próximo teste
        self.results = {
            "rbac_checks": 0,
            "permission_granted": 0,
            "permission_denied": 0,
            "role_validation": 0,
            "response_times": [],
            "concurrent_checks": 0
        }
        
        # Teste 3: Validação de permissões sob carga
        results["tests"]["permission_validation"] = self.test_permission_validation_under_load()
        
        # Teste 4: Geração de logs de auditoria
        results["tests"]["audit_log_generation"] = self.test_audit_log_generation()
        
        logger.info("Suite completa de testes RBAC finalizada")
        return results

if __name__ == "__main__":
    # Executar testes
    test = SecurityRBACLoadTest()
    results = test.run_complete_test_suite()
    
    # Exibir resultados
    print("\n=== RESULTADOS DOS TESTES RBAC SOB CARGA ===")
    for test_name, test_result in results["tests"].items():
        print(f"\n{test_name.upper()}:")
        for key, value in test_result.items():
            print(f"  {key}: {value}") 