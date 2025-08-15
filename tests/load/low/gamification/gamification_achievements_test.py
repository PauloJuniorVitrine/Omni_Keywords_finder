"""
Teste de Carga para Sistema de Conquistas - Gamificação
Tracing ID: GAMIFICATION_ACHIEVEMENTS_001
Data: 2025-01-27
Baseado em: infrastructure/gamification/badges_system.py
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
class AchievementsTestConfig:
    """Configuração para testes de carga em conquistas"""
    base_url: str = "http://localhost:8000"
    concurrent_users: int = 40
    test_duration: int = 300  # 5 minutos
    achievement_operations: List[str] = None
    
    def __post_init__(self):
        if self.achievement_operations is None:
            self.achievement_operations = [
                "unlock_achievement",
                "view_achievements",
                "check_progress",
                "claim_reward",
                "view_leaderboard",
                "compare_achievements"
            ]

@dataclass
class AchievementsTestResult:
    """Resultado de teste de conquistas"""
    operation: str
    response_time: float
    status_code: int
    success: bool
    timestamp: datetime
    user_id: int
    achievement_id: Optional[str] = None
    progress_percentage: Optional[float] = None
    error_message: Optional[str] = None

class AchievementsLoadTester:
    """Testador de carga para conquistas"""
    
    def __init__(self, config: AchievementsTestConfig):
        self.config = config
        self.results: List[AchievementsTestResult] = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def _authenticate_user(self, user_id: int) -> bool:
        """Autenticar usuário para operações de conquistas"""
        try:
            auth_data = {
                "username": f"achievement_user_{user_id}",
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
    
    def _run_achievement_operation(self, operation: str, user_id: int) -> AchievementsTestResult:
        """Executar operação de conquista"""
        start_time = time.time()
        
        try:
            # Autenticar usuário
            if not self._authenticate_user(user_id):
                return AchievementsTestResult(
                    operation=operation,
                    response_time=time.time() - start_time,
                    status_code=401,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    error_message="Falha na autenticação"
                )
            
            # Dados da operação de conquista
            achievement_data = {
                "operation": operation,
                "user_id": user_id,
                "request_id": str(uuid.uuid4()),
                "achievement_type": "keyword_master",
                "progress_value": 75
            }
            
            # Fazer requisição para operação de conquista
            response = self.session.post(
                f"{self.config.base_url}/api/v1/gamification/achievements/process",
                json=achievement_data,
                timeout=30
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                achievement_id = response_data.get('achievement_id')
                progress_percentage = response_data.get('progress_percentage', 0.0)
                
                return AchievementsTestResult(
                    operation=operation,
                    response_time=response_time,
                    status_code=response.status_code,
                    success=True,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    achievement_id=achievement_id,
                    progress_percentage=progress_percentage
                )
            else:
                return AchievementsTestResult(
                    operation=operation,
                    response_time=response_time,
                    status_code=response.status_code,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    error_message=response.text
                )
            
        except requests.exceptions.Timeout:
            return AchievementsTestResult(
                operation=operation,
                response_time=time.time() - start_time,
                status_code=408,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message="Timeout na operação de conquista"
            )
            
        except Exception as e:
            return AchievementsTestResult(
                operation=operation,
                response_time=time.time() - start_time,
                status_code=500,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message=str(e)
            )
    
    def _user_workload(self, user_id: int) -> List[AchievementsTestResult]:
        """Simular carga de trabalho de um usuário"""
        user_results = []
        
        # Executar operações de conquistas
        for operation in self.config.achievement_operations:
            result = self._run_achievement_operation(operation, user_id)
            user_results.append(result)
            
            # Pausa entre operações
            time.sleep(1)
            
        return user_results
    
    def run_load_test(self) -> Dict[str, Any]:
        """Executar teste de carga completo"""
        logger.info(f"Iniciando teste de carga para conquistas com {self.config.concurrent_users} usuários")
        
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
                    logger.info(f"Usuário {user_id} completou operações de conquistas")
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
            progress_percentages = [r.progress_percentage for r in results if r.progress_percentage]
            
            operation_metrics[operation] = {
                "total_requests": total_count,
                "successful_requests": success_count,
                "success_rate": (success_count / total_count) * 100 if total_count > 0 else 0,
                "avg_response_time": statistics.mean(response_times) if response_times else 0,
                "min_response_time": min(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0,
                "p95_response_time": statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times) if response_times else 0,
                "avg_progress": statistics.mean(progress_percentages) if progress_percentages else 0
            }
        
        # Métricas gerais
        all_response_times = [r.response_time for r in self.results]
        all_successful = sum(1 for r in self.results if r.success)
        total_requests = len(self.results)
        all_progress = [r.progress_percentage for r in self.results if r.progress_percentage]
        
        return {
            "test_configuration": {
                "concurrent_users": self.config.concurrent_users,
                "test_duration": total_duration,
                "total_requests": total_requests,
                "achievement_operations": self.config.achievement_operations
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
                "avg_progress": statistics.mean(all_progress) if all_progress else 0
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

def run_achievements_load_test(
    base_url: str = "http://localhost:8000",
    concurrent_users: int = 40,
    test_duration: int = 300
) -> Dict[str, Any]:
    """Função principal para executar teste de carga em conquistas"""
    
    config = AchievementsTestConfig(
        base_url=base_url,
        concurrent_users=concurrent_users,
        test_duration=test_duration
    )
    
    tester = AchievementsLoadTester(config)
    results = tester.run_load_test()
    
    # Log dos resultados
    logger.info("=== RESULTADOS DO TESTE DE CARGA EM CONQUISTAS ===")
    logger.info(f"Total de requisições: {results['overall_metrics']['total_requests']}")
    logger.info(f"Taxa de sucesso: {results['overall_metrics']['success_rate']:.2f}%")
    logger.info(f"Tempo médio de resposta: {results['overall_metrics']['avg_response_time']:.3f}s")
    logger.info(f"P95 tempo de resposta: {results['overall_metrics']['p95_response_time']:.3f}s")
    logger.info(f"Requisições por segundo: {results['overall_metrics']['requests_per_second']:.2f}")
    logger.info(f"Progresso médio: {results['overall_metrics']['avg_progress']:.2f}%")
    
    return results

if __name__ == "__main__":
    # Executar teste de carga
    results = run_achievements_load_test(
        base_url="http://localhost:8000",
        concurrent_users=40,
        test_duration=300
    )
    
    # Salvar resultados em arquivo
    with open("achievements_load_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("Teste de carga em conquistas concluído. Resultados salvos em achievements_load_test_results.json") 