"""
Teste de Carga para Privacidade - Compliance
Tracing ID: COMPLIANCE_PRIVACY_001
Data: 2025-01-27
Baseado em: infrastructure/compliance/privacy_compliance.py
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
class PrivacyTestConfig:
    """Configuração para testes de carga em privacidade"""
    base_url: str = "http://localhost:8000"
    concurrent_users: int = 30
    test_duration: int = 480  # 8 minutos
    privacy_operations: List[str] = None
    data_categories: List[str] = None
    
    def __post_init__(self):
        if self.privacy_operations is None:
            self.privacy_operations = [
                "data_anonymization",
                "data_encryption", 
                "consent_management",
                "data_export",
                "data_deletion",
                "privacy_audit"
            ]
        
        if self.data_categories is None:
            self.data_categories = [
                "personal_data",
                "sensitive_data",
                "financial_data",
                "health_data",
                "location_data",
                "behavioral_data"
            ]

@dataclass
class PrivacyTestResult:
    """Resultado de teste de privacidade"""
    operation: str
    data_category: str
    response_time: float
    status_code: int
    success: bool
    timestamp: datetime
    user_id: int
    data_size: Optional[int] = None
    record_count: Optional[int] = None
    error_message: Optional[str] = None

class PrivacyLoadTester:
    """Testador de carga para privacidade"""
    
    def __init__(self, config: PrivacyTestConfig):
        self.config = config
        self.results: List[PrivacyTestResult] = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def _authenticate_user(self, user_id: int) -> bool:
        """Autenticar usuário para operações de privacidade"""
        try:
            auth_data = {
                "username": f"privacy_user_{user_id}",
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
    
    def _anonymize_data(self, data_category: str, user_id: int) -> PrivacyTestResult:
        """Anonimizar dados"""
        start_time = time.time()
        
        try:
            # Autenticar usuário
            if not self._authenticate_user(user_id):
                return PrivacyTestResult(
                    operation="data_anonymization",
                    data_category=data_category,
                    response_time=time.time() - start_time,
                    status_code=401,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    error_message="Falha na autenticação"
                )
            
            # Dados da anonimização
            anonymize_data = {
                "data_category": data_category,
                "user_id": user_id,
                "request_id": str(uuid.uuid4()),
                "anonymization_level": "high",
                "preserve_analytics": True
            }
            
            # Fazer requisição para anonimizar
            response = self.session.post(
                f"{self.config.base_url}/api/v1/privacy/anonymize",
                json=anonymize_data,
                timeout=90
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                data_size = response_data.get('anonymized_data_size', 0)
                record_count = response_data.get('anonymized_records', 0)
                
                return PrivacyTestResult(
                    operation="data_anonymization",
                    data_category=data_category,
                    response_time=response_time,
                    status_code=response.status_code,
                    success=True,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    data_size=data_size,
                    record_count=record_count
                )
            else:
                return PrivacyTestResult(
                    operation="data_anonymization",
                    data_category=data_category,
                    response_time=response_time,
                    status_code=response.status_code,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    error_message=response.text
                )
            
        except requests.exceptions.Timeout:
            return PrivacyTestResult(
                operation="data_anonymization",
                data_category=data_category,
                response_time=time.time() - start_time,
                status_code=408,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message="Timeout na anonimização"
            )
            
        except Exception as e:
            return PrivacyTestResult(
                operation="data_anonymization",
                data_category=data_category,
                response_time=time.time() - start_time,
                status_code=500,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message=str(e)
            )
    
    def _manage_consent(self, data_category: str, user_id: int) -> PrivacyTestResult:
        """Gerenciar consentimento"""
        start_time = time.time()
        
        try:
            consent_data = {
                "data_category": data_category,
                "user_id": user_id,
                "request_id": str(uuid.uuid4()),
                "consent_type": "explicit",
                "consent_status": "granted",
                "purpose": "analytics"
            }
            
            response = self.session.post(
                f"{self.config.base_url}/api/v1/privacy/consent",
                json=consent_data,
                timeout=30
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                record_count = response_data.get('consent_records', 0)
                
                return PrivacyTestResult(
                    operation="consent_management",
                    data_category=data_category,
                    response_time=response_time,
                    status_code=response.status_code,
                    success=True,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    record_count=record_count
                )
            else:
                return PrivacyTestResult(
                    operation="consent_management",
                    data_category=data_category,
                    response_time=response_time,
                    status_code=response.status_code,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    error_message=response.text
                )
                
        except Exception as e:
            return PrivacyTestResult(
                operation="consent_management",
                data_category=data_category,
                response_time=time.time() - start_time,
                status_code=500,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message=str(e)
            )
    
    def _export_user_data(self, data_category: str, user_id: int) -> PrivacyTestResult:
        """Exportar dados do usuário"""
        start_time = time.time()
        
        try:
            export_data = {
                "data_category": data_category,
                "user_id": user_id,
                "request_id": str(uuid.uuid4()),
                "format": "json",
                "include_metadata": True
            }
            
            response = self.session.post(
                f"{self.config.base_url}/api/v1/privacy/export",
                json=export_data,
                timeout=120
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                data_size = response_data.get('export_size', 0)
                record_count = response_data.get('export_records', 0)
                
                return PrivacyTestResult(
                    operation="data_export",
                    data_category=data_category,
                    response_time=response_time,
                    status_code=response.status_code,
                    success=True,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    data_size=data_size,
                    record_count=record_count
                )
            else:
                return PrivacyTestResult(
                    operation="data_export",
                    data_category=data_category,
                    response_time=response_time,
                    status_code=response.status_code,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    error_message=response.text
                )
                
        except Exception as e:
            return PrivacyTestResult(
                operation="data_export",
                data_category=data_category,
                response_time=time.time() - start_time,
                status_code=500,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message=str(e)
            )
    
    def _delete_user_data(self, data_category: str, user_id: int) -> PrivacyTestResult:
        """Deletar dados do usuário"""
        start_time = time.time()
        
        try:
            delete_data = {
                "data_category": data_category,
                "user_id": user_id,
                "request_id": str(uuid.uuid4()),
                "deletion_type": "permanent",
                "confirmation": True
            }
            
            response = self.session.post(
                f"{self.config.base_url}/api/v1/privacy/delete",
                json=delete_data,
                timeout=90
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                data_size = response_data.get('deleted_data_size', 0)
                record_count = response_data.get('deleted_records', 0)
                
                return PrivacyTestResult(
                    operation="data_deletion",
                    data_category=data_category,
                    response_time=response_time,
                    status_code=response.status_code,
                    success=True,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    data_size=data_size,
                    record_count=record_count
                )
            else:
                return PrivacyTestResult(
                    operation="data_deletion",
                    data_category=data_category,
                    response_time=response_time,
                    status_code=response.status_code,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    error_message=response.text
                )
                
        except Exception as e:
            return PrivacyTestResult(
                operation="data_deletion",
                data_category=data_category,
                response_time=time.time() - start_time,
                status_code=500,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message=str(e)
            )
    
    def _user_workload(self, user_id: int) -> List[PrivacyTestResult]:
        """Simular carga de trabalho de um usuário"""
        user_results = []
        
        # Executar operações de privacidade
        for data_category in self.config.data_categories:
            # Anonimizar dados
            anonymize_result = self._anonymize_data(data_category, user_id)
            user_results.append(anonymize_result)
            
            # Gerenciar consentimento
            consent_result = self._manage_consent(data_category, user_id)
            user_results.append(consent_result)
            
            # Exportar dados
            export_result = self._export_user_data(data_category, user_id)
            user_results.append(export_result)
            
            # Deletar dados (apenas para alguns usuários para simular cenário real)
            if user_id % 3 == 0:  # 1/3 dos usuários
                delete_result = self._delete_user_data(data_category, user_id)
                user_results.append(delete_result)
            
            # Pausa entre operações
            time.sleep(2)
            
        return user_results
    
    def run_load_test(self) -> Dict[str, Any]:
        """Executar teste de carga completo"""
        logger.info(f"Iniciando teste de carga para privacidade com {self.config.concurrent_users} usuários")
        
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
                    logger.info(f"Usuário {user_id} completou operações de privacidade")
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
        
        # Separar resultados por categoria de dados
        category_results = {}
        for result in self.results:
            if result.data_category not in category_results:
                category_results[result.data_category] = []
            category_results[result.data_category].append(result)
        
        # Calcular métricas por operação
        operation_metrics = {}
        for operation, results in operation_results.items():
            response_times = [r.response_time for r in results]
            success_count = sum(1 for r in results if r.success)
            total_count = len(results)
            data_sizes = [r.data_size for r in results if r.data_size]
            record_counts = [r.record_count for r in results if r.record_count]
            
            operation_metrics[operation] = {
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
        
        # Calcular métricas por categoria
        category_metrics = {}
        for category, results in category_results.items():
            response_times = [r.response_time for r in results]
            success_count = sum(1 for r in results if r.success)
            total_count = len(results)
            
            category_metrics[category] = {
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
                "privacy_operations": self.config.privacy_operations,
                "data_categories": self.config.data_categories
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
            "operation_metrics": operation_metrics,
            "category_metrics": category_metrics,
            "errors": [
                {
                    "operation": r.operation,
                    "data_category": r.data_category,
                    "status_code": r.status_code,
                    "error_message": r.error_message,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in self.results if not r.success
            ]
        }

def run_privacy_load_test(
    base_url: str = "http://localhost:8000",
    concurrent_users: int = 30,
    test_duration: int = 480
) -> Dict[str, Any]:
    """Função principal para executar teste de carga em privacidade"""
    
    config = PrivacyTestConfig(
        base_url=base_url,
        concurrent_users=concurrent_users,
        test_duration=test_duration
    )
    
    tester = PrivacyLoadTester(config)
    results = tester.run_load_test()
    
    # Log dos resultados
    logger.info("=== RESULTADOS DO TESTE DE CARGA EM PRIVACIDADE ===")
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
    results = run_privacy_load_test(
        base_url="http://localhost:8000",
        concurrent_users=30,
        test_duration=480
    )
    
    # Salvar resultados em arquivo
    with open("privacy_load_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("Teste de carga em privacidade concluído. Resultados salvos em privacy_load_test_results.json") 