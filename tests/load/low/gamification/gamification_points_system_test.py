"""
Teste de Carga para Sistema de Pontos - Gamificação
Tracing ID: GAMIFICATION_POINTS_SYSTEM_001
Data: 2025-01-27
Baseado em: infrastructure/gamification/points_system.py
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
class PointsSystemTestConfig:
    """Configuração para testes de carga em sistema de pontos"""
    base_url: str = "http://localhost:8000"
    concurrent_users: int = 45
    test_duration: int = 360  # 6 minutos
    points_operations: List[str] = None
    
    def __post_init__(self):
        if self.points_operations is None:
            self.points_operations = [
                "earn_points",
                "spend_points",
                "check_balance",
                "view_history",
                "transfer_points",
                "redeem_rewards"
            ]

@dataclass
class PointsSystemTestResult:
    """Resultado de teste de sistema de pontos"""
    operation: str
    response_time: float
    status_code: int
    success: bool
    timestamp: datetime
    user_id: int
    points_amount: Optional[int] = None
    balance_after: Optional[int] = None
    error_message: Optional[str] = None

class PointsSystemLoadTester:
    """Testador de carga para sistema de pontos"""
    
    def __init__(self, config: PointsSystemTestConfig):
        self.config = config
        self.results: List[PointsSystemTestResult] = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def _authenticate_user(self, user_id: int) -> bool:
        """Autenticar usuário para operações de pontos"""
        try:
            auth_data = {
                "username": f"points_user_{user_id}",
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
    
    def _earn_points(self, user_id: int) -> PointsSystemTestResult:
        """Ganhar pontos"""
        start_time = time.time()
        
        try:
            # Autenticar usuário
            if not self._authenticate_user(user_id):
                return PointsSystemTestResult(
                    operation="earn_points",
                    response_time=time.time() - start_time,
                    status_code=401,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    error_message="Falha na autenticação"
                )
            
            # Dados para ganhar pontos
            earn_data = {
                "user_id": user_id,
                "request_id": str(uuid.uuid4()),
                "activity_type": "keyword_analysis",
                "points_amount": 50,
                "description": "Análise de palavras-chave concluída"
            }
            
            # Fazer requisição para ganhar pontos
            response = self.session.post(
                f"{self.config.base_url}/api/v1/gamification/points/earn",
                json=earn_data,
                timeout=30
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                points_amount = response_data.get('points_earned', 0)
                balance_after = response_data.get('new_balance', 0)
                
                return PointsSystemTestResult(
                    operation="earn_points",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=True,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    points_amount=points_amount,
                    balance_after=balance_after
                )
            else:
                return PointsSystemTestResult(
                    operation="earn_points",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    error_message=response.text
                )
            
        except requests.exceptions.Timeout:
            return PointsSystemTestResult(
                operation="earn_points",
                response_time=time.time() - start_time,
                status_code=408,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message="Timeout ao ganhar pontos"
            )
            
        except Exception as e:
            return PointsSystemTestResult(
                operation="earn_points",
                response_time=time.time() - start_time,
                status_code=500,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message=str(e)
            )
    
    def _spend_points(self, user_id: int) -> PointsSystemTestResult:
        """Gastar pontos"""
        start_time = time.time()
        
        try:
            spend_data = {
                "user_id": user_id,
                "request_id": str(uuid.uuid4()),
                "activity_type": "premium_feature",
                "points_amount": 25,
                "description": "Acesso a recurso premium"
            }
            
            response = self.session.post(
                f"{self.config.base_url}/api/v1/gamification/points/spend",
                json=spend_data,
                timeout=30
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                points_amount = response_data.get('points_spent', 0)
                balance_after = response_data.get('new_balance', 0)
                
                return PointsSystemTestResult(
                    operation="spend_points",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=True,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    points_amount=points_amount,
                    balance_after=balance_after
                )
            else:
                return PointsSystemTestResult(
                    operation="spend_points",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    error_message=response.text
                )
                
        except Exception as e:
            return PointsSystemTestResult(
                operation="spend_points",
                response_time=time.time() - start_time,
                status_code=500,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message=str(e)
            )
    
    def _check_balance(self, user_id: int) -> PointsSystemTestResult:
        """Verificar saldo de pontos"""
        start_time = time.time()
        
        try:
            response = self.session.get(
                f"{self.config.base_url}/api/v1/gamification/points/balance",
                params={"user_id": user_id},
                timeout=20
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                balance_after = response_data.get('current_balance', 0)
                
                return PointsSystemTestResult(
                    operation="check_balance",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=True,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    balance_after=balance_after
                )
            else:
                return PointsSystemTestResult(
                    operation="check_balance",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    error_message=response.text
                )
                
        except Exception as e:
            return PointsSystemTestResult(
                operation="check_balance",
                response_time=time.time() - start_time,
                status_code=500,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message=str(e)
            )
    
    def _view_history(self, user_id: int) -> PointsSystemTestResult:
        """Visualizar histórico de pontos"""
        start_time = time.time()
        
        try:
            response = self.session.get(
                f"{self.config.base_url}/api/v1/gamification/points/history",
                params={
                    "user_id": user_id,
                    "limit": 20,
                    "offset": 0
                },
                timeout=30
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                points_amount = len(response_data.get('transactions', []))
                
                return PointsSystemTestResult(
                    operation="view_history",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=True,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    points_amount=points_amount
                )
            else:
                return PointsSystemTestResult(
                    operation="view_history",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    error_message=response.text
                )
                
        except Exception as e:
            return PointsSystemTestResult(
                operation="view_history",
                response_time=time.time() - start_time,
                status_code=500,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message=str(e)
            )
    
    def _transfer_points(self, user_id: int) -> PointsSystemTestResult:
        """Transferir pontos"""
        start_time = time.time()
        
        try:
            transfer_data = {
                "from_user_id": user_id,
                "to_user_id": user_id + 1000,  # Usuário diferente
                "request_id": str(uuid.uuid4()),
                "points_amount": 10,
                "description": "Transferência de pontos"
            }
            
            response = self.session.post(
                f"{self.config.base_url}/api/v1/gamification/points/transfer",
                json=transfer_data,
                timeout=40
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                points_amount = response_data.get('points_transferred', 0)
                balance_after = response_data.get('sender_balance', 0)
                
                return PointsSystemTestResult(
                    operation="transfer_points",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=True,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    points_amount=points_amount,
                    balance_after=balance_after
                )
            else:
                return PointsSystemTestResult(
                    operation="transfer_points",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    error_message=response.text
                )
                
        except Exception as e:
            return PointsSystemTestResult(
                operation="transfer_points",
                response_time=time.time() - start_time,
                status_code=500,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message=str(e)
            )
    
    def _redeem_rewards(self, user_id: int) -> PointsSystemTestResult:
        """Resgatar recompensas"""
        start_time = time.time()
        
        try:
            redeem_data = {
                "user_id": user_id,
                "request_id": str(uuid.uuid4()),
                "reward_id": "premium_analysis",
                "points_cost": 100,
                "description": "Resgate de análise premium"
            }
            
            response = self.session.post(
                f"{self.config.base_url}/api/v1/gamification/points/redeem",
                json=redeem_data,
                timeout=35
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                points_amount = response_data.get('points_spent', 0)
                balance_after = response_data.get('new_balance', 0)
                
                return PointsSystemTestResult(
                    operation="redeem_rewards",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=True,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    points_amount=points_amount,
                    balance_after=balance_after
                )
            else:
                return PointsSystemTestResult(
                    operation="redeem_rewards",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    error_message=response.text
                )
                
        except Exception as e:
            return PointsSystemTestResult(
                operation="redeem_rewards",
                response_time=time.time() - start_time,
                status_code=500,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message=str(e)
            )
    
    def _run_points_operation(self, operation: str, user_id: int) -> PointsSystemTestResult:
        """Executar operação de pontos"""
        if operation == "earn_points":
            return self._earn_points(user_id)
        elif operation == "spend_points":
            return self._spend_points(user_id)
        elif operation == "check_balance":
            return self._check_balance(user_id)
        elif operation == "view_history":
            return self._view_history(user_id)
        elif operation == "transfer_points":
            return self._transfer_points(user_id)
        elif operation == "redeem_rewards":
            return self._redeem_rewards(user_id)
        else:
            return PointsSystemTestResult(
                operation=operation,
                response_time=0,
                status_code=400,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message="Operação não suportada"
            )
    
    def _user_workload(self, user_id: int) -> List[PointsSystemTestResult]:
        """Simular carga de trabalho de um usuário"""
        user_results = []
        
        # Executar operações de pontos
        for operation in self.config.points_operations:
            result = self._run_points_operation(operation, user_id)
            user_results.append(result)
            
            # Pausa entre operações
            time.sleep(1)
            
        return user_results
    
    def run_load_test(self) -> Dict[str, Any]:
        """Executar teste de carga completo"""
        logger.info(f"Iniciando teste de carga para sistema de pontos com {self.config.concurrent_users} usuários")
        
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
                    logger.info(f"Usuário {user_id} completou operações de pontos")
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
            points_amounts = [r.points_amount for r in results if r.points_amount]
            balances = [r.balance_after for r in results if r.balance_after]
            
            operation_metrics[operation] = {
                "total_requests": total_count,
                "successful_requests": success_count,
                "success_rate": (success_count / total_count) * 100 if total_count > 0 else 0,
                "avg_response_time": statistics.mean(response_times) if response_times else 0,
                "min_response_time": min(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0,
                "p95_response_time": statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times) if response_times else 0,
                "avg_points_amount": statistics.mean(points_amounts) if points_amounts else 0,
                "avg_balance": statistics.mean(balances) if balances else 0
            }
        
        # Métricas gerais
        all_response_times = [r.response_time for r in self.results]
        all_successful = sum(1 for r in self.results if r.success)
        total_requests = len(self.results)
        all_points_amounts = [r.points_amount for r in self.results if r.points_amount]
        all_balances = [r.balance_after for r in self.results if r.balance_after]
        
        return {
            "test_configuration": {
                "concurrent_users": self.config.concurrent_users,
                "test_duration": total_duration,
                "total_requests": total_requests,
                "points_operations": self.config.points_operations
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
                "total_points_processed": sum(all_points_amounts) if all_points_amounts else 0,
                "avg_balance": statistics.mean(all_balances) if all_balances else 0
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

def run_points_system_load_test(
    base_url: str = "http://localhost:8000",
    concurrent_users: int = 45,
    test_duration: int = 360
) -> Dict[str, Any]:
    """Função principal para executar teste de carga em sistema de pontos"""
    
    config = PointsSystemTestConfig(
        base_url=base_url,
        concurrent_users=concurrent_users,
        test_duration=test_duration
    )
    
    tester = PointsSystemLoadTester(config)
    results = tester.run_load_test()
    
    # Log dos resultados
    logger.info("=== RESULTADOS DO TESTE DE CARGA EM SISTEMA DE PONTOS ===")
    logger.info(f"Total de requisições: {results['overall_metrics']['total_requests']}")
    logger.info(f"Taxa de sucesso: {results['overall_metrics']['success_rate']:.2f}%")
    logger.info(f"Tempo médio de resposta: {results['overall_metrics']['avg_response_time']:.3f}s")
    logger.info(f"P95 tempo de resposta: {results['overall_metrics']['p95_response_time']:.3f}s")
    logger.info(f"Requisições por segundo: {results['overall_metrics']['requests_per_second']:.2f}")
    logger.info(f"Total de pontos processados: {results['overall_metrics']['total_points_processed']}")
    logger.info(f"Saldo médio: {results['overall_metrics']['avg_balance']:.2f}")
    
    return results

if __name__ == "__main__":
    # Executar teste de carga
    results = run_points_system_load_test(
        base_url="http://localhost:8000",
        concurrent_users=45,
        test_duration=360
    )
    
    # Salvar resultados em arquivo
    with open("points_system_load_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("Teste de carga em sistema de pontos concluído. Resultados salvos em points_system_load_test_results.json") 