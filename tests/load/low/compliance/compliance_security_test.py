"""
Teste de Carga para Segurança - Compliance
Tracing ID: COMPLIANCE_SECURITY_001
Data: 2025-01-27
Baseado em: backend/app/api/auditoria.py
"""

import time
import json
import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
import statistics
import uuid

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SecurityTestConfig:
    """Configuração para testes de carga em segurança"""
    base_url: str = "http://localhost:8000"
    concurrent_users: int = 20
    test_duration: int = 400  # 6.7 minutos
    security_operations: List[str] = None
    
    def __post_init__(self):
        if self.security_operations is None:
            self.security_operations = [
                "security_scan",
                "vulnerability_assessment", 
                "penetration_test",
                "access_control_audit",
                "encryption_validation",
                "security_compliance_check"
            ]

@dataclass
class SecurityTestResult:
    """Resultado de teste de segurança"""
    operation: str
    response_time: float
    status_code: int
    success: bool
    timestamp: datetime
    user_id: int
    security_score: Optional[float] = None
    vulnerabilities_found: Optional[int] = None
    error_message: Optional[str] = None

class SecurityLoadTester:
    """Testador de carga para segurança"""
    
    def __init__(self, config: SecurityTestConfig):
        self.config = config
        self.results: List[SecurityTestResult] = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def _authenticate_user(self, user_id: int) -> bool:
        """Autenticar usuário para operações de segurança"""
        try:
            auth_data = {
                "username": f"security_user_{user_id}",
                "password": "test_password_123"
            }
            
            response = self.session.post(
                f"{self.config.base_url}/api/auth/login",
                json=auth_data,
                timeout=10
            )
            
            if response.status_code == 200:
                token = response.json().get('access_token')
                if token:
                    self.session.headers.update({
                        'Authorization': f'Bearer {token}'
                    })
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Erro na autenticação do usuário {user_id}: {e}")
            return False
    
    def _run_security_operation(self, operation: str, user_id: int) -> SecurityTestResult:
        """Executar operação de segurança"""
        start_time = time.time()
        
        try:
            # Autenticar usuário
            if not self._authenticate_user(user_id):
                return SecurityTestResult(
                    operation=operation,
                    response_time=time.time() - start_time,
                    status_code=401,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    error_message="Falha na autenticação"
                )
            
            # Dados da operação de segurança
            security_data = {
                "operation": operation,
                "user_id": user_id,
                "request_id": str(uuid.uuid4()),
                "scan_depth": "comprehensive",
                "include_remediation": True
            }
            
            # Fazer requisição para operação de segurança
            response = self.session.post(
                f"{self.config.base_url}/api/v1/security/compliance/scan",
                json=security_data,
                timeout=120
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                security_score = response_data.get('security_score', 0.0)
                vulnerabilities_found = response_data.get('vulnerabilities_count', 0)
                
                return SecurityTestResult(
                    operation=operation,
                    response_time=response_time,
                    status_code=response.status_code,
                    success=True,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    security_score=security_score,
                    vulnerabilities_found=vulnerabilities_found
                )
            else:
                return SecurityTestResult(
                    operation=operation,
                    response_time=response_time,
                    status_code=response.status_code,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    error_message=response.text
                )
            
        except requests.exceptions.Timeout:
            return SecurityTestResult(
                operation=operation,
                response_time=time.time() - start_time,
                status_code=408,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message="Timeout na operação de segurança"
            )
            
        except Exception as e:
            return SecurityTestResult(
                operation=operation,
                response_time=time.time() - start_time,
                status_code=500,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message=str(e)
            )
    
    def _user_workload(self, user_id: int) -> List[SecurityTestResult]:
        """Simular carga de trabalho de um usuário"""
        user_results = []
        
        # Executar operações de segurança
        for operation in self.config.security_operations:
            result = self._run_security_operation(operation, user_id)
            user_results.append(result)
            
            # Pausa entre operações
            time.sleep(3)
            
        return user_results
    
    def run_load_test(self) -> Dict[str, Any]:
        """Executar teste de carga completo"""
        logger.info(f"Iniciando teste de carga para segurança com {self.config.concurrent_users} usuários")
        
        start_time = time.time()
        
        # Executar carga de usuários concorrentes
        with ThreadPoolExecutor(max_workers=self.config.concurrent_users) as executor:
            # Submeter tarefas para todos os usuários
            future_to_user = {
                executor.submit(self._user_workload, user_id): user_id 
                for user_id in range(1, self.config.concurrent_users + 1)
            }
            
            # Coletar resultados
            for future in as_completed(future_to_user):
                user_id = future_to_user[future]
                try:
                    user_results = future.result()
                    self.results.extend(user_results)
                    logger.info(f"Usuário {user_id} completou operações de segurança")
                except Exception as e:
                    logger.error(f"Erro no usuário {user_id}: {e}")
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Analisar resultados
        return self._analyze_results(total_duration)
    
    def _analyze_results(self, total_duration: float) -> Dict[str, Any]:
        """Analisar resultados do teste de carga"""
        if not self.results:
            return {"error": "Nenhum resultado coletado"}
        
        # Separar resultados por operação
        operation_results = {}
        for result in self.results:
            if result.operation not in operation_results:
                operation_results[result.operation] = []
            operation_results[result.operation].append(result)
        
        # Calcular métricas por operação
        operation_metrics = {}
        for operation, results in operation_results.items():
            response_times = [r.response_time for r in results]
            success_count = sum(1 for r in results if r.success)
            total_count = len(results)
            security_scores = [r.security_score for r in results if r.security_score]
            vulnerabilities = [r.vulnerabilities_found for r in results if r.vulnerabilities_found]
            
            operation_metrics[operation] = {
                "total_requests": total_count,
                "successful_requests": success_count,
                "success_rate": (success_count / total_count) * 100 if total_count > 0 else 0,
                "avg_response_time": statistics.mean(response_times) if response_times else 0,
                "min_response_time": min(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0,
                "p95_response_time": statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times) if response_times else 0,
                "avg_security_score": statistics.mean(security_scores) if security_scores else 0,
                "avg_vulnerabilities": statistics.mean(vulnerabilities) if vulnerabilities else 0
            }
        
        # Métricas gerais
        all_response_times = [r.response_time for r in self.results]
        all_successful = sum(1 for r in self.results if r.success)
        total_requests = len(self.results)
        all_security_scores = [r.security_score for r in self.results if r.security_score]
        all_vulnerabilities = [r.vulnerabilities_found for r in self.results if r.vulnerabilities_found]
        
        return {
            "test_configuration": {
                "concurrent_users": self.config.concurrent_users,
                "test_duration": total_duration,
                "total_requests": total_requests,
                "security_operations": self.config.security_operations
            },
            "overall_metrics": {
                "total_requests": total_requests,
                "successful_requests": all_successful,
                "success_rate": (all_successful / total_requests) * 100 if total_requests > 0 else 0,
                "avg_response_time": statistics.mean(all_response_times) if all_response_times else 0,
                "min_response_time": min(all_response_times) if all_response_times else 0,
                "max_response_time": max(all_response_times) if all_response_times else 0,
                "p95_response_time": statistics.quantiles(all_response_times, n=20)[18] if len(all_response_times) >= 20 else max(all_response_times) if all_response_times else 0,
                "requests_per_second": total_requests / total_duration if total_duration > 0 else 0,
                "avg_security_score": statistics.mean(all_security_scores) if all_security_scores else 0,
                "total_vulnerabilities_found": sum(all_vulnerabilities) if all_vulnerabilities else 0
            },
            "operation_metrics": operation_metrics,
            "errors": [
                {
                    "operation": r.operation,
                    "status_code": r.status_code,
                    "error_message": r.error_message,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in self.results if not r.success
            ]
        }

def run_security_load_test(
    base_url: str = "http://localhost:8000",
    concurrent_users: int = 20,
    test_duration: int = 400
) -> Dict[str, Any]:
    """Função principal para executar teste de carga em segurança"""
    
    config = SecurityTestConfig(
        base_url=base_url,
        concurrent_users=concurrent_users,
        test_duration=test_duration
    )
    
    tester = SecurityLoadTester(config)
    results = tester.run_load_test()
    
    # Log dos resultados
    logger.info("=== RESULTADOS DO TESTE DE CARGA EM SEGURANÇA ===")
    logger.info(f"Total de requisições: {results['overall_metrics']['total_requests']}")
    logger.info(f"Taxa de sucesso: {results['overall_metrics']['success_rate']:.2f}%")
    logger.info(f"Tempo médio de resposta: {results['overall_metrics']['avg_response_time']:.3f}s")
    logger.info(f"P95 tempo de resposta: {results['overall_metrics']['p95_response_time']:.3f}s")
    logger.info(f"Requisições por segundo: {results['overall_metrics']['requests_per_second']:.2f}")
    logger.info(f"Score médio de segurança: {results['overall_metrics']['avg_security_score']:.2f}")
    logger.info(f"Total de vulnerabilidades encontradas: {results['overall_metrics']['total_vulnerabilities_found']}")
    
    return results

if __name__ == "__main__":
    # Executar teste de carga
    results = run_security_load_test(
        base_url="http://localhost:8000",
        concurrent_users=20,
        test_duration=400
    )
    
    # Salvar resultados em arquivo
    with open("security_load_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("Teste de carga em segurança concluído. Resultados salvos em security_load_test_results.json") 