"""
Teste de Carga para Sistema de Ranking - Gamificação
Tracing ID: GAMIFICATION_LEADERBOARD_001
Data: 2025-01-27
Baseado em: infrastructure/gamification/leaderboards.py
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
class LeaderboardTestConfig:
    """Configuração para testes de carga em ranking"""
    base_url: str = "http://localhost:8000"
    concurrent_users: int = 35
    test_duration: int = 240  # 4 minutos
    leaderboard_operations: List[str] = None
    
    def __post_init__(self):
        if self.leaderboard_operations is None:
            self.leaderboard_operations = [
                "view_global_leaderboard",
                "view_category_leaderboard",
                "view_user_ranking",
                "update_score",
                "view_achievements_leaderboard",
                "view_weekly_leaderboard"
            ]

@dataclass
class LeaderboardTestResult:
    """Resultado de teste de ranking"""
    operation: str
    response_time: float
    status_code: int
    success: bool
    timestamp: datetime
    user_id: int
    leaderboard_type: Optional[str] = None
    user_rank: Optional[int] = None
    total_participants: Optional[int] = None
    error_message: Optional[str] = None

class LeaderboardLoadTester:
    """Testador de carga para ranking"""
    
    def __init__(self, config: LeaderboardTestConfig):
        self.config = config
        self.results: List[LeaderboardTestResult] = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def _authenticate_user(self, user_id: int) -> bool:
        """Autenticar usuário para operações de ranking"""
        try:
            auth_data = {
                "username": f"leaderboard_user_{user_id}",
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
    
    def _run_leaderboard_operation(self, operation: str, user_id: int) -> LeaderboardTestResult:
        """Executar operação de ranking"""
        start_time = time.time()
        
        try:
            # Autenticar usuário
            if not self._authenticate_user(user_id):
                return LeaderboardTestResult(
                    operation=operation,
                    response_time=time.time() - start_time,
                    status_code=401,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    error_message="Falha na autenticação"
                )
            
            # Dados da operação de ranking
            leaderboard_data = {
                "operation": operation,
                "user_id": user_id,
                "request_id": str(uuid.uuid4()),
                "leaderboard_type": "global",
                "category": "keyword_analysis",
                "score": 1500
            }
            
            # Fazer requisição para operação de ranking
            response = self.session.post(
                f"{self.config.base_url}/api/v1/gamification/leaderboard/process",
                json=leaderboard_data,
                timeout=25
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                leaderboard_type = response_data.get('leaderboard_type')
                user_rank = response_data.get('user_rank')
                total_participants = response_data.get('total_participants')
                
                return LeaderboardTestResult(
                    operation=operation,
                    response_time=response_time,
                    status_code=response.status_code,
                    success=True,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    leaderboard_type=leaderboard_type,
                    user_rank=user_rank,
                    total_participants=total_participants
                )
            else:
                return LeaderboardTestResult(
                    operation=operation,
                    response_time=response_time,
                    status_code=response.status_code,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    error_message=response.text
                )
            
        except requests.exceptions.Timeout:
            return LeaderboardTestResult(
                operation=operation,
                response_time=time.time() - start_time,
                status_code=408,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message="Timeout na operação de ranking"
            )
            
        except Exception as e:
            return LeaderboardTestResult(
                operation=operation,
                response_time=time.time() - start_time,
                status_code=500,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message=str(e)
            )
    
    def _user_workload(self, user_id: int) -> List[LeaderboardTestResult]:
        """Simular carga de trabalho de um usuário"""
        user_results = []
        
        # Executar operações de ranking
        for operation in self.config.leaderboard_operations:
            result = self._run_leaderboard_operation(operation, user_id)
            user_results.append(result)
            
            # Pausa entre operações
            time.sleep(1)
            
        return user_results
    
    def run_load_test(self) -> Dict[str, Any]:
        """Executar teste de carga completo"""
        logger.info(f"Iniciando teste de carga para ranking com {self.config.concurrent_users} usuários")
        
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
                    logger.info(f"Usuário {user_id} completou operações de ranking")
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
            user_ranks = [r.user_rank for r in results if r.user_rank]
            total_participants = [r.total_participants for r in results if r.total_participants]
            
            operation_metrics[operation] = {
                "total_requests": total_count,
                "successful_requests": success_count,
                "success_rate": (success_count / total_count) * 100 if total_count > 0 else 0,
                "avg_response_time": statistics.mean(response_times) if response_times else 0,
                "min_response_time": min(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0,
                "p95_response_time": statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times) if response_times else 0,
                "avg_user_rank": statistics.mean(user_ranks) if user_ranks else 0,
                "avg_participants": statistics.mean(total_participants) if total_participants else 0
            }
        
        # Métricas gerais
        all_response_times = [r.response_time for r in self.results]
        all_successful = sum(1 for r in self.results if r.success)
        total_requests = len(self.results)
        all_user_ranks = [r.user_rank for r in self.results if r.user_rank]
        all_participants = [r.total_participants for r in self.results if r.total_participants]
        
        return {
            "test_configuration": {
                "concurrent_users": self.config.concurrent_users,
                "test_duration": total_duration,
                "total_requests": total_requests,
                "leaderboard_operations": self.config.leaderboard_operations
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
                "avg_user_rank": statistics.mean(all_user_ranks) if all_user_ranks else 0,
                "avg_participants": statistics.mean(all_participants) if all_participants else 0
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

def run_leaderboard_load_test(
    base_url: str = "http://localhost:8000",
    concurrent_users: int = 35,
    test_duration: int = 240
) -> Dict[str, Any]:
    """Função principal para executar teste de carga em ranking"""
    
    config = LeaderboardTestConfig(
        base_url=base_url,
        concurrent_users=concurrent_users,
        test_duration=test_duration
    )
    
    tester = LeaderboardLoadTester(config)
    results = tester.run_load_test()
    
    # Log dos resultados
    logger.info("=== RESULTADOS DO TESTE DE CARGA EM RANKING ===")
    logger.info(f"Total de requisições: {results['overall_metrics']['total_requests']}")
    logger.info(f"Taxa de sucesso: {results['overall_metrics']['success_rate']:.2f}%")
    logger.info(f"Tempo médio de resposta: {results['overall_metrics']['avg_response_time']:.3f}s")
    logger.info(f"P95 tempo de resposta: {results['overall_metrics']['p95_response_time']:.3f}s")
    logger.info(f"Requisições por segundo: {results['overall_metrics']['requests_per_second']:.2f}")
    logger.info(f"Ranking médio: {results['overall_metrics']['avg_user_rank']:.2f}")
    logger.info(f"Participantes médios: {results['overall_metrics']['avg_participants']:.2f}")
    
    return results

if __name__ == "__main__":
    # Executar teste de carga
    results = run_leaderboard_load_test(
        base_url="http://localhost:8000",
        concurrent_users=35,
        test_duration=240
    )
    
    # Salvar resultados em arquivo
    with open("leaderboard_load_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("Teste de carga em ranking concluído. Resultados salvos em leaderboard_load_test_results.json") 