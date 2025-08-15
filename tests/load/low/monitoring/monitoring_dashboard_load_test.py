"""
Teste de Carga para Dashboards de Monitoramento
Tracing ID: MONITORING_DASHBOARD_LOAD_001
Data: 2025-01-27
Baseado em: infrastructure/monitoring/dashboards.py
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

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class DashboardLoadTestConfig:
    """Configuração para testes de carga em dashboards"""
    base_url: str = "http://localhost:8000"
    concurrent_users: int = 50
    test_duration: int = 300  # 5 minutos
    ramp_up_time: int = 60    # 1 minuto
    dashboard_endpoints: List[str] = None
    
    def __post_init__(self):
        if self.dashboard_endpoints is None:
            self.dashboard_endpoints = [
                "/api/v1/dashboards/overview",
                "/api/v1/dashboards/performance",
                "/api/v1/dashboards/analytics",
                "/api/v1/dashboards/security",
                "/api/v1/dashboards/business",
                "/api/v1/dashboards/system"
            ]

@dataclass
class DashboardLoadTestResult:
    """Resultado de teste de carga em dashboard"""
    endpoint: str
    response_time: float
    status_code: int
    success: bool
    timestamp: datetime
    user_id: int
    error_message: Optional[str] = None

class DashboardLoadTester:
    """Testador de carga para dashboards de monitoramento"""
    
    def __init__(self, config: DashboardLoadTestConfig):
        self.config = config
        self.results: List[DashboardLoadTestResult] = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def _authenticate_user(self, user_id: int) -> bool:
        """Autenticar usuário para acesso aos dashboards"""
        try:
            auth_data = {
                "username": f"test_user_{user_id}",
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
    
    def _load_dashboard(self, endpoint: str, user_id: int) -> DashboardLoadTestResult:
        """Carregar dashboard específico"""
        start_time = time.time()
        
        try:
            # Autenticar usuário
            if not self._authenticate_user(user_id):
                return DashboardLoadTestResult(
                    endpoint=endpoint,
                    response_time=time.time() - start_time,
                    status_code=401,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    error_message="Falha na autenticação"
                )
            
            # Fazer requisição para o dashboard
            response = self.session.get(
                f"{self.config.base_url}{endpoint}",
                timeout=30,
                params={
                    'time_range': '1h',
                    'refresh': 'true',
                    'user_id': user_id
                }
            )
            
            response_time = time.time() - start_time
            
            return DashboardLoadTestResult(
                endpoint=endpoint,
                response_time=response_time,
                status_code=response.status_code,
                success=response.status_code == 200,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message=None if response.status_code == 200 else response.text
            )
            
        except requests.exceptions.Timeout:
            return DashboardLoadTestResult(
                endpoint=endpoint,
                response_time=time.time() - start_time,
                status_code=408,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message="Timeout na requisição"
            )
            
        except Exception as e:
            return DashboardLoadTestResult(
                endpoint=endpoint,
                response_time=time.time() - start_time,
                status_code=500,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message=str(e)
            )
    
    def _user_workload(self, user_id: int) -> List[DashboardLoadTestResult]:
        """Simular carga de trabalho de um usuário"""
        user_results = []
        
        # Simular navegação entre dashboards
        for endpoint in self.config.dashboard_endpoints:
            result = self._load_dashboard(endpoint, user_id)
            user_results.append(result)
            
            # Pausa entre requisições para simular comportamento real
            time.sleep(2)
            
        return user_results
    
    def run_load_test(self) -> Dict[str, Any]:
        """Executar teste de carga completo"""
        logger.info(f"Iniciando teste de carga para dashboards com {self.config.concurrent_users} usuários")
        
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
                    logger.info(f"Usuário {user_id} completou carga de trabalho")
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
        
        # Separar resultados por endpoint
        endpoint_results = {}
        for result in self.results:
            if result.endpoint not in endpoint_results:
                endpoint_results[result.endpoint] = []
            endpoint_results[result.endpoint].append(result)
        
        # Calcular métricas por endpoint
        endpoint_metrics = {}
        for endpoint, results in endpoint_results.items():
            response_times = [r.response_time for r in results]
            success_count = sum(1 for r in results if r.success)
            total_count = len(results)
            
            endpoint_metrics[endpoint] = {
                "total_requests": total_count,
                "successful_requests": success_count,
                "success_rate": (success_count / total_count) * 100 if total_count > 0 else 0,
                "avg_response_time": statistics.mean(response_times) if response_times else 0,
                "min_response_time": min(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0,
                "p95_response_time": statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times) if response_times else 0,
                "p99_response_time": statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else max(response_times) if response_times else 0
            }
        
        # Métricas gerais
        all_response_times = [r.response_time for r in self.results]
        all_successful = sum(1 for r in self.results if r.success)
        total_requests = len(self.results)
        
        return {
            "test_configuration": {
                "concurrent_users": self.config.concurrent_users,
                "test_duration": total_duration,
                "total_requests": total_requests
            },
            "overall_metrics": {
                "total_requests": total_requests,
                "successful_requests": all_successful,
                "success_rate": (all_successful / total_requests) * 100 if total_requests > 0 else 0,
                "avg_response_time": statistics.mean(all_response_times) if all_response_times else 0,
                "min_response_time": min(all_response_times) if all_response_times else 0,
                "max_response_time": max(all_response_times) if all_response_times else 0,
                "p95_response_time": statistics.quantiles(all_response_times, n=20)[18] if len(all_response_times) >= 20 else max(all_response_times) if all_response_times else 0,
                "p99_response_time": statistics.quantiles(all_response_times, n=100)[98] if len(all_response_times) >= 100 else max(all_response_times) if all_response_times else 0,
                "requests_per_second": total_requests / total_duration if total_duration > 0 else 0
            },
            "endpoint_metrics": endpoint_metrics,
            "errors": [
                {
                    "endpoint": r.endpoint,
                    "status_code": r.status_code,
                    "error_message": r.error_message,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in self.results if not r.success
            ]
        }

def run_dashboard_load_test(
    base_url: str = "http://localhost:8000",
    concurrent_users: int = 50,
    test_duration: int = 300
) -> Dict[str, Any]:
    """Função principal para executar teste de carga em dashboards"""
    
    config = DashboardLoadTestConfig(
        base_url=base_url,
        concurrent_users=concurrent_users,
        test_duration=test_duration
    )
    
    tester = DashboardLoadTester(config)
    results = tester.run_load_test()
    
    # Log dos resultados
    logger.info("=== RESULTADOS DO TESTE DE CARGA EM DASHBOARDS ===")
    logger.info(f"Total de requisições: {results['overall_metrics']['total_requests']}")
    logger.info(f"Taxa de sucesso: {results['overall_metrics']['success_rate']:.2f}%")
    logger.info(f"Tempo médio de resposta: {results['overall_metrics']['avg_response_time']:.3f}s")
    logger.info(f"P95 tempo de resposta: {results['overall_metrics']['p95_response_time']:.3f}s")
    logger.info(f"Requisições por segundo: {results['overall_metrics']['requests_per_second']:.2f}")
    
    return results

if __name__ == "__main__":
    # Executar teste de carga
    results = run_dashboard_load_test(
        base_url="http://localhost:8000",
        concurrent_users=50,
        test_duration=300
    )
    
    # Salvar resultados em arquivo
    with open("dashboard_load_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("Teste de carga em dashboards concluído. Resultados salvos em dashboard_load_test_results.json") 