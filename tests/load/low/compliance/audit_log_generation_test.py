"""
Teste de Carga para Geração de Logs de Auditoria
Tracing ID: AUDIT_LOG_GENERATION_001
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
class AuditLogTestConfig:
    """Configuração para testes de carga em logs de auditoria"""
    base_url: str = "http://localhost:8000"
    concurrent_users: int = 35
    test_duration: int = 360  # 6 minutos
    audit_events: List[str] = None
    
    def __post_init__(self):
        if self.audit_events is None:
            self.audit_events = [
                "user_login",
                "user_logout",
                "data_access",
                "data_modification",
                "permission_change",
                "system_config_change",
                "security_event",
                "compliance_check"
            ]

@dataclass
class AuditLogTestResult:
    """Resultado de teste de logs de auditoria"""
    event_type: str
    response_time: float
    status_code: int
    success: bool
    timestamp: datetime
    user_id: int
    log_id: Optional[str] = None
    event_severity: Optional[str] = None
    error_message: Optional[str] = None

class AuditLogLoadTester:
    """Testador de carga para logs de auditoria"""
    
    def __init__(self, config: AuditLogTestConfig):
        self.config = config
        self.results: List[AuditLogTestResult] = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def _authenticate_user(self, user_id: int) -> bool:
        """Autenticar usuário para operações de auditoria"""
        try:
            auth_data = {
                "username": f"audit_user_{user_id}",
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
    
    def _generate_audit_log(self, event_type: str, user_id: int) -> AuditLogTestResult:
        """Gerar log de auditoria"""
        start_time = time.time()
        
        try:
            # Autenticar usuário
            if not self._authenticate_user(user_id):
                return AuditLogTestResult(
                    event_type=event_type,
                    response_time=time.time() - start_time,
                    status_code=401,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    error_message="Falha na autenticação"
                )
            
            # Dados do evento de auditoria
            audit_data = {
                "event_type": event_type,
                "user_id": user_id,
                "request_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "severity": "medium",
                "source_ip": "192.168.1.100",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "metadata": {
                    "session_id": str(uuid.uuid4()),
                    "request_path": f"/api/v1/audit/{event_type}",
                    "http_method": "POST"
                }
            }
            
            # Fazer requisição para gerar log
            response = self.session.post(
                f"{self.config.base_url}/api/v1/audit/log",
                json=audit_data,
                timeout=30
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                log_id = response_data.get('log_id')
                event_severity = response_data.get('severity')
                
                return AuditLogTestResult(
                    event_type=event_type,
                    response_time=response_time,
                    status_code=response.status_code,
                    success=True,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    log_id=log_id,
                    event_severity=event_severity
                )
            else:
                return AuditLogTestResult(
                    event_type=event_type,
                    response_time=response_time,
                    status_code=response.status_code,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    error_message=response.text
                )
            
        except requests.exceptions.Timeout:
            return AuditLogTestResult(
                event_type=event_type,
                response_time=time.time() - start_time,
                status_code=408,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message="Timeout na geração do log"
            )
            
        except Exception as e:
            return AuditLogTestResult(
                event_type=event_type,
                response_time=time.time() - start_time,
                status_code=500,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message=str(e)
            )
    
    def _user_workload(self, user_id: int) -> List[AuditLogTestResult]:
        """Simular carga de trabalho de um usuário"""
        user_results = []
        
        # Gerar logs de auditoria para diferentes eventos
        for event_type in self.config.audit_events:
            result = self._generate_audit_log(event_type, user_id)
            user_results.append(result)
            
            # Pausa entre eventos
            time.sleep(1)
            
        return user_results
    
    def run_load_test(self) -> Dict[str, Any]:
        """Executar teste de carga completo"""
        logger.info(f"Iniciando teste de carga para logs de auditoria com {self.config.concurrent_users} usuários")
        
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
                    logger.info(f"Usuário {user_id} completou geração de logs de auditoria")
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
        
        # Separar resultados por tipo de evento
        event_results = {}
        for result in self.results:
            if result.event_type not in event_results:
                event_results[result.event_type] = []
            event_results[result.event_type].append(result)
        
        # Calcular métricas por tipo de evento
        event_metrics = {}
        for event_type, results in event_results.items():
            response_times = [r.response_time for r in results]
            success_count = sum(1 for r in results if r.success)
            total_count = len(results)
            
            event_metrics[event_type] = {
                "total_requests": total_count,
                "successful_requests": success_count,
                "success_rate": (success_count / total_count) * 100 if total_count > 0 else 0,
                "avg_response_time": statistics.mean(response_times) if response_times else 0,
                "min_response_time": min(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0,
                "p95_response_time": statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times) if response_times else 0
            }
        
        # Métricas gerais
        all_response_times = [r.response_time for r in self.results]
        all_successful = sum(1 for r in self.results if r.success)
        total_requests = len(self.results)
        
        return {
            "test_configuration": {
                "concurrent_users": self.config.concurrent_users,
                "test_duration": total_duration,
                "total_requests": total_requests,
                "audit_events": self.config.audit_events
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
                "logs_generated_per_second": all_successful / total_duration if total_duration > 0 else 0
            },
            "event_metrics": event_metrics,
            "errors": [
                {
                    "event_type": r.event_type,
                    "status_code": r.status_code,
                    "error_message": r.error_message,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in self.results if not r.success
            ]
        }

def run_audit_log_load_test(
    base_url: str = "http://localhost:8000",
    concurrent_users: int = 35,
    test_duration: int = 360
) -> Dict[str, Any]:
    """Função principal para executar teste de carga em logs de auditoria"""
    
    config = AuditLogTestConfig(
        base_url=base_url,
        concurrent_users=concurrent_users,
        test_duration=test_duration
    )
    
    tester = AuditLogLoadTester(config)
    results = tester.run_load_test()
    
    # Log dos resultados
    logger.info("=== RESULTADOS DO TESTE DE CARGA EM LOGS DE AUDITORIA ===")
    logger.info(f"Total de requisições: {results['overall_metrics']['total_requests']}")
    logger.info(f"Taxa de sucesso: {results['overall_metrics']['success_rate']:.2f}%")
    logger.info(f"Tempo médio de resposta: {results['overall_metrics']['avg_response_time']:.3f}s")
    logger.info(f"P95 tempo de resposta: {results['overall_metrics']['p95_response_time']:.3f}s")
    logger.info(f"Requisições por segundo: {results['overall_metrics']['requests_per_second']:.2f}")
    logger.info(f"Logs gerados por segundo: {results['overall_metrics']['logs_generated_per_second']:.2f}")
    
    return results

if __name__ == "__main__":
    # Executar teste de carga
    results = run_audit_log_load_test(
        base_url="http://localhost:8000",
        concurrent_users=35,
        test_duration=360
    )
    
    # Salvar resultados em arquivo
    with open("audit_log_load_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("Teste de carga em logs de auditoria concluído. Resultados salvos em audit_log_load_test_results.json") 