"""
Teste de Carga - Rate Limiting
Baseado em: backend/app/middleware/rate_limiting.py
Tracing ID: SECURITY_RATE_LIMITING_LOAD_TEST_20250127_001
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

class SecurityRateLimitingLoadTest:
    """
    Teste de carga para validação de rate limiting
    Baseado no código real: backend/app/middleware/rate_limiting.py
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = {
            "rate_limit_hits": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "rate_limit_headers": []
        }
        
        # Configuração baseada no código real
        self.endpoints_to_test = [
            "/api/auth/login",
            "/api/rbac/usuarios",
            "/api/v1/payments/process",
            "/api/analytics/overview"
        ]
        
        # Dados de teste baseados no sistema real
        self.test_credentials = {
            "email": "admin@omnikeywords.com",
            "password": "admin_password_2025"
        }
        
        logger.info("Teste de Rate Limiting inicializado")

    def get_auth_token(self) -> str:
        """Obtém token de autenticação"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json=self.test_credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                token_data = response.json()
                return token_data.get("access_token", "")
            else:
                logger.error(f"Falha na autenticação: {response.status_code}")
                return ""
                
        except Exception as e:
            logger.error(f"Erro durante autenticação: {str(e)}")
            return ""

    def make_request(self, endpoint: str, token: str = "", request_id: int = 0) -> Dict[str, Any]:
        """
        Faz uma requisição e registra métricas
        Baseado em: backend/app/middleware/rate_limiting.py linha 100-150
        """
        start_time = time.time()
        
        try:
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            
            # Dados baseados em requisições reais
            if endpoint == "/api/auth/login":
                data = {
                    "email": f"user{request_id}@test.com",
                    "password": "test_password_2025"
                }
                response = self.session.post(f"{self.base_url}{endpoint}", json=data, headers=headers, timeout=10)
                
            elif endpoint == "/api/rbac/usuarios":
                response = self.session.get(f"{self.base_url}{endpoint}", headers=headers, timeout=10)
                
            elif endpoint == "/api/v1/payments/process":
                payment_data = {
                    "payment_id": f"pay_test_{request_id}",
                    "amount": random.choice([1000, 2500, 5000]),
                    "currency": "BRL",
                    "payment_method": "credit_card",
                    "payment_method_data": {
                        "card_number": "4242424242424242",
                        "exp_month": "12",
                        "exp_year": "2025",
                        "cvc": "123"
                    }
                }
                response = self.session.post(f"{self.base_url}{endpoint}", json=payment_data, headers=headers, timeout=10)
                
            elif endpoint == "/api/analytics/overview":
                response = self.session.get(f"{self.base_url}{endpoint}", headers=headers, timeout=10)
                
            else:
                response = self.session.get(f"{self.base_url}{endpoint}", headers=headers, timeout=10)
            
            duration = time.time() - start_time
            
            # Registrar métricas baseadas no código real
            result = {
                "endpoint": endpoint,
                "status_code": response.status_code,
                "duration": duration,
                "request_id": request_id,
                "rate_limited": response.status_code == 429,
                "headers": dict(response.headers)
            }
            
            # Verificar headers de rate limiting (baseado no código real)
            if "X-RateLimit-Remaining" in response.headers:
                result["rate_limit_remaining"] = response.headers["X-RateLimit-Remaining"]
                result["rate_limit_reset"] = response.headers.get("X-RateLimit-Reset")
                result["retry_after"] = response.headers.get("Retry-After")
                
                self.results["rate_limit_headers"].append({
                    "remaining": response.headers["X-RateLimit-Remaining"],
                    "reset": response.headers.get("X-RateLimit-Reset"),
                    "retry_after": response.headers.get("Retry-After")
                })
            
            # Classificar resultado
            if response.status_code == 429:
                self.results["rate_limit_hits"] += 1
                logger.info(f"Rate limit atingido: {endpoint} - Request {request_id}")
                
            elif response.status_code == 200:
                self.results["successful_requests"] += 1
                
            else:
                self.results["failed_requests"] += 1
                logger.warning(f"Requisição falhou: {endpoint} - Status {response.status_code}")
            
            self.results["response_times"].append(duration)
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            self.results["failed_requests"] += 1
            logger.error(f"Erro na requisição {endpoint}: {str(e)}")
            
            return {
                "endpoint": endpoint,
                "status_code": 0,
                "duration": duration,
                "request_id": request_id,
                "rate_limited": False,
                "error": str(e)
            }

    def test_rate_limiting_by_ip(self, requests_per_second: int = 50, duration_seconds: int = 30) -> Dict[str, Any]:
        """
        Teste de rate limiting por IP
        Baseado em: backend/app/middleware/rate_limiting.py linha 80-90
        """
        logger.info(f"Iniciando teste de rate limiting por IP: {requests_per_second} req/s por {duration_seconds}s")
        
        total_requests = requests_per_second * duration_seconds
        delay = 1.0 / requests_per_second
        
        start_time = time.time()
        request_id = 0
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            
            while time.time() - start_time < duration_seconds:
                endpoint = random.choice(self.endpoints_to_test)
                
                future = executor.submit(self.make_request, endpoint, "", request_id)
                futures.append(future)
                
                request_id += 1
                time.sleep(delay)
            
            # Aguardar conclusão
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Erro no teste: {str(e)}")
        
        return self.analyze_results("Rate Limiting por IP")

    def test_rate_limiting_by_user(self, requests_per_second: int = 30, duration_seconds: int = 30) -> Dict[str, Any]:
        """
        Teste de rate limiting por usuário
        Baseado em: backend/app/middleware/rate_limiting.py linha 80-90
        """
        logger.info(f"Iniciando teste de rate limiting por usuário: {requests_per_second} req/s por {duration_seconds}s")
        
        # Obter token de autenticação
        token = self.get_auth_token()
        if not token:
            logger.error("Não foi possível obter token de autenticação")
            return {"error": "Falha na autenticação"}
        
        total_requests = requests_per_second * duration_seconds
        delay = 1.0 / requests_per_second
        
        start_time = time.time()
        request_id = 0
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            
            while time.time() - start_time < duration_seconds:
                endpoint = random.choice(self.endpoints_to_test)
                
                future = executor.submit(self.make_request, endpoint, token, request_id)
                futures.append(future)
                
                request_id += 1
                time.sleep(delay)
            
            # Aguardar conclusão
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Erro no teste: {str(e)}")
        
        return self.analyze_results("Rate Limiting por Usuário")

    def test_rate_limiting_bypass_attempts(self) -> Dict[str, Any]:
        """
        Teste de tentativas de bypass do rate limiting
        Baseado em: backend/app/middleware/rate_limiting.py linha 100-150
        """
        logger.info("Iniciando teste de tentativas de bypass do rate limiting")
        
        bypass_attempts = [
            # Tentativa 1: Múltiplos IPs
            {"method": "multiple_ips", "description": "Requisições de múltiplos IPs"},
            
            # Tentativa 2: Headers falsificados
            {"method": "fake_headers", "description": "Headers de rate limit falsificados"},
            
            # Tentativa 3: Requisições muito rápidas
            {"method": "rapid_requests", "description": "Requisições em alta velocidade"},
            
            # Tentativa 4: Diferentes User-Agents
            {"method": "different_user_agents", "description": "Diferentes User-Agents"}
        ]
        
        results = {}
        
        for attempt in bypass_attempts:
            logger.info(f"Testando bypass: {attempt['description']}")
            
            if attempt["method"] == "multiple_ips":
                results["multiple_ips"] = self._test_multiple_ips_bypass()
                
            elif attempt["method"] == "fake_headers":
                results["fake_headers"] = self._test_fake_headers_bypass()
                
            elif attempt["method"] == "rapid_requests":
                results["rapid_requests"] = self._test_rapid_requests_bypass()
                
            elif attempt["method"] == "different_user_agents":
                results["different_user_agents"] = self._test_user_agent_bypass()
        
        return {
            "test_type": "Rate Limiting Bypass Attempts",
            "bypass_attempts": results,
            "summary": self._analyze_bypass_results(results)
        }

    def _test_multiple_ips_bypass(self) -> Dict[str, Any]:
        """Testa bypass usando múltiplos IPs"""
        try:
            # Simular requisições de diferentes IPs
            fake_ips = ["192.168.1.1", "192.168.1.2", "192.168.1.3", "10.0.0.1", "10.0.0.2"]
            
            results = []
            for i, ip in enumerate(fake_ips):
                headers = {"X-Forwarded-For": ip, "X-Real-IP": ip}
                
                response = self.session.get(
                    f"{self.base_url}/api/rbac/usuarios",
                    headers=headers,
                    timeout=5
                )
                
                results.append({
                    "ip": ip,
                    "status_code": response.status_code,
                    "rate_limited": response.status_code == 429
                })
            
            return {
                "attempts": len(results),
                "rate_limited_count": sum(1 for r in results if r["rate_limited"]),
                "bypass_successful": any(not r["rate_limited"] for r in results),
                "details": results
            }
            
        except Exception as e:
            return {"error": str(e)}

    def _test_fake_headers_bypass(self) -> Dict[str, Any]:
        """Testa bypass usando headers falsificados"""
        try:
            # Headers falsificados baseados no código real
            fake_headers = {
                "X-RateLimit-Remaining": "100",
                "X-RateLimit-Reset": str(int(time.time()) + 3600),
                "Retry-After": "0"
            }
            
            results = []
            for i in range(10):
                response = self.session.get(
                    f"{self.base_url}/api/rbac/usuarios",
                    headers=fake_headers,
                    timeout=5
                )
                
                results.append({
                    "attempt": i + 1,
                    "status_code": response.status_code,
                    "rate_limited": response.status_code == 429,
                    "fake_headers_ignored": response.status_code == 429
                })
            
            return {
                "attempts": len(results),
                "rate_limited_count": sum(1 for r in results if r["rate_limited"]),
                "fake_headers_ignored": all(r["fake_headers_ignored"] for r in results),
                "details": results
            }
            
        except Exception as e:
            return {"error": str(e)}

    def _test_rapid_requests_bypass(self) -> Dict[str, Any]:
        """Testa bypass usando requisições muito rápidas"""
        try:
            results = []
            start_time = time.time()
            
            # Fazer 100 requisições muito rápidas
            for i in range(100):
                response = self.session.get(
                    f"{self.base_url}/api/rbac/usuarios",
                    timeout=1
                )
                
                results.append({
                    "attempt": i + 1,
                    "status_code": response.status_code,
                    "rate_limited": response.status_code == 429,
                    "timestamp": time.time() - start_time
                })
                
                # Mínimo delay para não sobrecarregar
                time.sleep(0.01)
            
            return {
                "attempts": len(results),
                "rate_limited_count": sum(1 for r in results if r["rate_limited"]),
                "bypass_successful": any(not r["rate_limited"] for r in results[-10:]),  # Últimas 10 requisições
                "duration": time.time() - start_time,
                "details": results[-10:]  # Apenas as últimas 10
            }
            
        except Exception as e:
            return {"error": str(e)}

    def _test_user_agent_bypass(self) -> Dict[str, Any]:
        """Testa bypass usando diferentes User-Agents"""
        try:
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                "PostmanRuntime/7.32.3",
                "curl/7.88.1"
            ]
            
            results = []
            for i, user_agent in enumerate(user_agents):
                headers = {"User-Agent": user_agent}
                
                response = self.session.get(
                    f"{self.base_url}/api/rbac/usuarios",
                    headers=headers,
                    timeout=5
                )
                
                results.append({
                    "user_agent": user_agent,
                    "status_code": response.status_code,
                    "rate_limited": response.status_code == 429
                })
            
            return {
                "attempts": len(results),
                "rate_limited_count": sum(1 for r in results if r["rate_limited"]),
                "bypass_successful": any(not r["rate_limited"] for r in results),
                "details": results
            }
            
        except Exception as e:
            return {"error": str(e)}

    def analyze_results(self, test_name: str) -> Dict[str, Any]:
        """Analisa resultados do teste"""
        total_requests = (self.results["rate_limit_hits"] + 
                         self.results["successful_requests"] + 
                         self.results["failed_requests"])
        
        if total_requests == 0:
            return {"error": "Nenhuma requisição foi feita"}
        
        avg_response_time = sum(self.results["response_times"]) / len(self.results["response_times"]) if self.results["response_times"] else 0
        
        return {
            "test_name": test_name,
            "total_requests": total_requests,
            "rate_limit_hits": self.results["rate_limit_hits"],
            "successful_requests": self.results["successful_requests"],
            "failed_requests": self.results["failed_requests"],
            "rate_limit_percentage": (self.results["rate_limit_hits"] / total_requests) * 100,
            "success_percentage": (self.results["successful_requests"] / total_requests) * 100,
            "avg_response_time": avg_response_time,
            "rate_limit_headers_analyzed": len(self.results["rate_limit_headers"])
        }

    def _analyze_bypass_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa resultados dos testes de bypass"""
        total_bypass_attempts = len(results)
        successful_bypasses = sum(1 for r in results.values() if isinstance(r, dict) and r.get("bypass_successful", False))
        
        return {
            "total_bypass_attempts": total_bypass_attempts,
            "successful_bypasses": successful_bypasses,
            "bypass_success_rate": (successful_bypasses / total_bypass_attempts) * 100 if total_bypass_attempts > 0 else 0,
            "security_level": "HIGH" if successful_bypasses == 0 else "MEDIUM" if successful_bypasses <= 2 else "LOW"
        }

    def run_complete_test_suite(self) -> Dict[str, Any]:
        """Executa suite completa de testes de rate limiting"""
        logger.info("Iniciando suite completa de testes de rate limiting")
        
        results = {
            "timestamp": time.time(),
            "tests": {}
        }
        
        # Teste 1: Rate limiting por IP
        results["tests"]["rate_limiting_by_ip"] = self.test_rate_limiting_by_ip()
        
        # Reset para próximo teste
        self.results = {
            "rate_limit_hits": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "rate_limit_headers": []
        }
        
        # Teste 2: Rate limiting por usuário
        results["tests"]["rate_limiting_by_user"] = self.test_rate_limiting_by_user()
        
        # Reset para próximo teste
        self.results = {
            "rate_limit_hits": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "rate_limit_headers": []
        }
        
        # Teste 3: Tentativas de bypass
        results["tests"]["bypass_attempts"] = self.test_rate_limiting_bypass_attempts()
        
        logger.info("Suite completa de testes de rate limiting finalizada")
        return results

if __name__ == "__main__":
    # Executar testes
    test = SecurityRateLimitingLoadTest()
    results = test.run_complete_test_suite()
    
    # Exibir resultados
    print("\n=== RESULTADOS DOS TESTES DE RATE LIMITING ===")
    for test_name, test_result in results["tests"].items():
        print(f"\n{test_name.upper()}:")
        for key, value in test_result.items():
            print(f"  {key}: {value}") 