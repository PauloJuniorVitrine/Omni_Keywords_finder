"""
Teste de Carga para Retenção de Dados - Compliance
Tracing ID: COMPLIANCE_DATA_RETENTION_001
Data: 2025-01-27
Baseado em: infrastructure/compliance/, backend/app/api/auditoria.py
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
class DataRetentionTestConfig:
    """Configuração para testes de carga em retenção de dados"""
    base_url: str = "http://localhost:8000"
    concurrent_users: int = 25
    test_duration: int = 600  # 10 minutos
    data_types: List[str] = None
    retention_policies: List[str] = None
    
    def __post_init__(self):
        if self.data_types is None:
            self.data_types = [
                "user_data",
                "transaction_data", 
                "log_data",
                "analytics_data",
                "audit_data",
                "backup_data"
            ]
        
        if self.retention_policies is None:
            self.retention_policies = ["30d", "90d", "1y", "7y", "permanent"]

@dataclass
class DataRetentionTestResult:
    """Resultado de teste de retenção de dados"""
    data_type: str
    retention_policy: str
    operation: str
    response_time: float
    status_code: int
    success: bool
    timestamp: datetime
    user_id: int
    data_size: Optional[int] = None
    record_count: Optional[int] = None
    error_message: Optional[str] = None

class DataRetentionLoadTester:
    """Testador de carga para retenção de dados"""
    
    def __init__(self, config: DataRetentionTestConfig):
        self.config = config
        self.results: List[DataRetentionTestResult] = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def _authenticate_user(self, user_id: int) -> bool:
        """Autenticar usuário para operações de compliance"""
        try:
            auth_data = {
                "username": f"compliance_user_{user_id}",
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
    
    def _apply_retention_policy(self, data_type: str, retention_policy: str, user_id: int) -> DataRetentionTestResult:
        """Aplicar política de retenção"""
        start_time = time.time()
        
        try:
            # Autenticar usuário
            if not self._authenticate_user(user_id):
                return DataRetentionTestResult(
                    data_type=data_type,
                    retention_policy=retention_policy,
                    operation="apply_policy",
                    response_time=time.time() - start_time,
                    status_code=401,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    error_message="Falha na autenticação"
                )
            
            # Dados da política de retenção
            policy_data = {
                "data_type": data_type,
                "retention_policy": retention_policy,
                "action": "apply",
                "user_id": user_id,
                "request_id": str(uuid.uuid4()),
                "metadata": {
                    "compliance_standard": "GDPR",
                    "data_classification": "personal",
                    "retention_reason": "legal_requirement"
                }
            }
            
            # Fazer requisição para aplicar política
            response = self.session.post(
                f"{self.config.base_url}/api/v1/compliance/retention/apply",
                json=policy_data,
                timeout=60
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                data_size = response_data.get('affected_data_size', 0)
                record_count = response_data.get('affected_records', 0)
                
                return DataRetentionTestResult(
                    data_type=data_type,
                    retention_policy=retention_policy,
                    operation="apply_policy",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=True,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    data_size=data_size,
                    record_count=record_count
                )
            else:
                return DataRetentionTestResult(
                    data_type=data_type,
                    retention_policy=retention_policy,
                    operation="apply_policy",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    error_message=response.text
                )
            
        except requests.exceptions.Timeout:
            return DataRetentionTestResult(
                data_type=data_type,
                retention_policy=retention_policy,
                operation="apply_policy",
                response_time=time.time() - start_time,
                status_code=408,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message="Timeout na aplicação da política"
            )
            
        except Exception as e:
            return DataRetentionTestResult(
                data_type=data_type,
                retention_policy=retention_policy,
                operation="apply_policy",
                response_time=time.time() - start_time,
                status_code=500,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message=str(e)
            )
    
    def _check_retention_status(self, data_type: str, user_id: int) -> DataRetentionTestResult:
        """Verificar status de retenção"""
        start_time = time.time()
        
        try:
            response = self.session.get(
                f"{self.config.base_url}/api/v1/compliance/retention/status",
                params={
                    "data_type": data_type,
                    "user_id": user_id
                },
                timeout=30
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                data_size = response_data.get('total_data_size', 0)
                record_count = response_data.get('total_records', 0)
                
                return DataRetentionTestResult(
                    data_type=data_type,
                    retention_policy="status_check",
                    operation="check_status",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=True,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    data_size=data_size,
                    record_count=record_count
                )
            else:
                return DataRetentionTestResult(
                    data_type=data_type,
                    retention_policy="status_check",
                    operation="check_status",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    error_message=response.text
                )
                
        except Exception as e:
            return DataRetentionTestResult(
                data_type=data_type,
                retention_policy="status_check",
                operation="check_status",
                response_time=time.time() - start_time,
                status_code=500,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message=str(e)
            )
    
    def _purge_expired_data(self, data_type: str, user_id: int) -> DataRetentionTestResult:
        """Purge de dados expirados"""
        start_time = time.time()
        
        try:
            purge_data = {
                "data_type": data_type,
                "user_id": user_id,
                "request_id": str(uuid.uuid4()),
                "dry_run": False
            }
            
            response = self.session.post(
                f"{self.config.base_url}/api/v1/compliance/retention/purge",
                json=purge_data,
                timeout=120  # 2 minutos para purge
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                data_size = response_data.get('purged_data_size', 0)
                record_count = response_data.get('purged_records', 0)
                
                return DataRetentionTestResult(
                    data_type=data_type,
                    retention_policy="purge",
                    operation="purge_data",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=True,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    data_size=data_size,
                    record_count=record_count
                )
            else:
                return DataRetentionTestResult(
                    data_type=data_type,
                    retention_policy="purge",
                    operation="purge_data",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    error_message=response.text
                )
                
        except Exception as e:
            return DataRetentionTestResult(
                data_type=data_type,
                retention_policy="purge",
                operation="purge_data",
                response_time=time.time() - start_time,
                status_code=500,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message=str(e)
            )
    
    def _user_workload(self, user_id: int) -> List[DataRetentionTestResult]:
        """Simular carga de trabalho de um usuário"""
        user_results = []
        
        # Aplicar políticas de retenção
        for data_type in self.config.data_types:
            for retention_policy in self.config.retention_policies:
                # Aplicar política
                result = self._apply_retention_policy(data_type, retention_policy, user_id)
                user_results.append(result)
                
                # Verificar status
                status_result = self._check_retention_status(data_type, user_id)
                user_results.append(status_result)
                
                # Pausa entre operações
                time.sleep(2)
            
            # Purge de dados expirados
            purge_result = self._purge_expired_data(data_type, user_id)
            user_results.append(purge_result)
            
            time.sleep(3)
            
        return user_results
    
    def run_load_test(self) -> Dict[str, Any]:
        """Executar teste de carga completo"""
        logger.info(f"Iniciando teste de carga para retenção de dados com {self.config.concurrent_users} usuários")
        
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
                    logger.info(f"Usuário {user_id} completou operações de retenção")
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
        
        # Separar resultados por tipo de dados
        data_type_results = {}
        for result in self.results:
            if result.data_type not in data_type_results:
                data_type_results[result.data_type] = []
            data_type_results[result.data_type].append(result)
        
        # Separar resultados por operação
        operation_results = {}
        for result in self.results:
            if result.operation not in operation_results:
                operation_results[result.operation] = []
            operation_results[result.operation].append(result)
        
        # Calcular métricas por tipo de dados
        data_type_metrics = {}
        for data_type, results in data_type_results.items():
            response_times = [r.response_time for r in results]
            success_count = sum(1 for r in results if r.success)
            total_count = len(results)
            data_sizes = [r.data_size for r in results if r.data_size]
            record_counts = [r.record_count for r in results if r.record_count]
            
            data_type_metrics[data_type] = {
                "total_requests": total_count,
                "successful_requests": success_count,
                "success_rate": (success_count / total_count) * 100 if total_count > 0 else 0,
                "avg_response_time": statistics.mean(response_times) if response_times else 0,
                "min_response_time": min(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0,
                "p95_response_time": statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times) if response_times else 0,
                "avg_data_size": statistics.mean(data_sizes) if data_sizes else 0,
                "avg_record_count": statistics.mean(record_counts) if record_counts else 0
            }
        
        # Calcular métricas por operação
        operation_metrics = {}
        for operation, results in operation_results.items():
            response_times = [r.response_time for r in results]
            success_count = sum(1 for r in results if r.success)
            total_count = len(results)
            
            operation_metrics[operation] = {
                "total_requests": total_count,
                "successful_requests": success_count,
                "success_rate": (success_count / total_count) * 100 if total_count > 0 else 0,
                "avg_response_time": statistics.mean(response_times) if response_times else 0,
                "min_response_time": min(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0
            }
        
        # Métricas gerais
        all_response_times = [r.response_time for r in self.results]
        all_successful = sum(1 for r in self.results if r.success)
        total_requests = len(self.results)
        all_data_sizes = [r.data_size for r in self.results if r.data_size]
        all_record_counts = [r.record_count for r in self.results if r.record_count]
        
        return {
            "test_configuration": {
                "concurrent_users": self.config.concurrent_users,
                "test_duration": total_duration,
                "total_requests": total_requests,
                "data_types": self.config.data_types,
                "retention_policies": self.config.retention_policies
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
                "avg_data_size": statistics.mean(all_data_sizes) if all_data_sizes else 0,
                "total_data_processed": sum(all_data_sizes) if all_data_sizes else 0,
                "avg_record_count": statistics.mean(all_record_counts) if all_record_counts else 0,
                "total_records_processed": sum(all_record_counts) if all_record_counts else 0
            },
            "data_type_metrics": data_type_metrics,
            "operation_metrics": operation_metrics,
            "errors": [
                {
                    "data_type": r.data_type,
                    "retention_policy": r.retention_policy,
                    "operation": r.operation,
                    "status_code": r.status_code,
                    "error_message": r.error_message,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in self.results if not r.success
            ]
        }

def run_data_retention_load_test(
    base_url: str = "http://localhost:8000",
    concurrent_users: int = 25,
    test_duration: int = 600
) -> Dict[str, Any]:
    """Função principal para executar teste de carga em retenção de dados"""
    
    config = DataRetentionTestConfig(
        base_url=base_url,
        concurrent_users=concurrent_users,
        test_duration=test_duration
    )
    
    tester = DataRetentionLoadTester(config)
    results = tester.run_load_test()
    
    # Log dos resultados
    logger.info("=== RESULTADOS DO TESTE DE CARGA EM RETENÇÃO DE DADOS ===")
    logger.info(f"Total de requisições: {results['overall_metrics']['total_requests']}")
    logger.info(f"Taxa de sucesso: {results['overall_metrics']['success_rate']:.2f}%")
    logger.info(f"Tempo médio de resposta: {results['overall_metrics']['avg_response_time']:.3f}s")
    logger.info(f"P95 tempo de resposta: {results['overall_metrics']['p95_response_time']:.3f}s")
    logger.info(f"Requisições por segundo: {results['overall_metrics']['requests_per_second']:.2f}")
    logger.info(f"Dados processados: {results['overall_metrics']['total_data_processed']} bytes")
    logger.info(f"Registros processados: {results['overall_metrics']['total_records_processed']}")
    
    return results

if __name__ == "__main__":
    # Executar teste de carga
    results = run_data_retention_load_test(
        base_url="http://localhost:8000",
        concurrent_users=25,
        test_duration=600
    )
    
    # Salvar resultados em arquivo
    with open("data_retention_load_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("Teste de carga em retenção de dados concluído. Resultados salvos em data_retention_load_test_results.json") 