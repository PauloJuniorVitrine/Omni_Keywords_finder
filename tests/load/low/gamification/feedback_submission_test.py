"""
Teste de Carga para Submissão de Feedback - Gamificação
Tracing ID: FEEDBACK_SUBMISSION_001
Data: 2025-01-27
Baseado em: backend/app/api/feedback.py
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
class FeedbackSubmissionTestConfig:
    """Configuração para testes de carga em submissão de feedback"""
    base_url: str = "http://localhost:8000"
    concurrent_users: int = 30
    test_duration: int = 180  # 3 minutos
    feedback_types: List[str] = None
    
    def __post_init__(self):
        if self.feedback_types is None:
            self.feedback_types = [
                "bug_report",
                "feature_request",
                "general_feedback",
                "performance_issue",
                "usability_feedback",
                "suggestion"
            ]

@dataclass
class FeedbackSubmissionTestResult:
    """Resultado de teste de submissão de feedback"""
    operation: str
    response_time: float
    status_code: int
    success: bool
    timestamp: datetime
    user_id: int
    feedback_id: Optional[str] = None
    feedback_type: Optional[str] = None
    priority: Optional[str] = None
    error_message: Optional[str] = None

class FeedbackSubmissionLoadTester:
    """Testador de carga para submissão de feedback"""
    
    def __init__(self, config: FeedbackSubmissionTestConfig):
        self.config = config
        self.results: List[FeedbackSubmissionTestResult] = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def _authenticate_user(self, user_id: int) -> bool:
        """Autenticar usuário para operações de feedback"""
        try:
            auth_data = {
                "username": f"feedback_user_{user_id}",
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
    
    def _submit_feedback(self, feedback_type: str, user_id: int) -> FeedbackSubmissionTestResult:
        """Submeter feedback"""
        start_time = time.time()
        
        try:
            # Autenticar usuário
            if not self._authenticate_user(user_id):
                return FeedbackSubmissionTestResult(
                    operation="submit_feedback",
                    response_time=time.time() - start_time,
                    status_code=401,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    feedback_type=feedback_type,
                    error_message="Falha na autenticação"
                )
            
            # Dados do feedback
            feedback_data = {
                "user_id": user_id,
                "request_id": str(uuid.uuid4()),
                "feedback_type": feedback_type,
                "title": f"Feedback de teste - {feedback_type}",
                "description": f"Este é um feedback de teste para {feedback_type} gerado automaticamente",
                "priority": "medium",
                "category": "system",
                "tags": ["test", "automated", feedback_type],
                "metadata": {
                    "source": "load_test",
                    "test_user": True,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            # Fazer requisição para submeter feedback
            response = self.session.post(
                f"{self.config.base_url}/api/feedback/submit",
                json=feedback_data,
                timeout=30
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                feedback_id = response_data.get('feedback_id')
                priority = response_data.get('priority')
                
                return FeedbackSubmissionTestResult(
                    operation="submit_feedback",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=True,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    feedback_id=feedback_id,
                    feedback_type=feedback_type,
                    priority=priority
                )
            else:
                return FeedbackSubmissionTestResult(
                    operation="submit_feedback",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    feedback_type=feedback_type,
                    error_message=response.text
                )
            
        except requests.exceptions.Timeout:
            return FeedbackSubmissionTestResult(
                operation="submit_feedback",
                response_time=time.time() - start_time,
                status_code=408,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                feedback_type=feedback_type,
                error_message="Timeout ao submeter feedback"
            )
            
        except Exception as e:
            return FeedbackSubmissionTestResult(
                operation="submit_feedback",
                response_time=time.time() - start_time,
                status_code=500,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                feedback_type=feedback_type,
                error_message=str(e)
            )
    
    def _user_workload(self, user_id: int) -> List[FeedbackSubmissionTestResult]:
        """Simular carga de trabalho de um usuário"""
        user_results = []
        
        # Submeter diferentes tipos de feedback
        for feedback_type in self.config.feedback_types:
            result = self._submit_feedback(feedback_type, user_id)
            user_results.append(result)
            
            # Pausa entre submissões
            time.sleep(1)
            
        return user_results
    
    def run_load_test(self) -> Dict[str, Any]:
        """Executar teste de carga completo"""
        logger.info(f"Iniciando teste de carga para submissão de feedback com {self.config.concurrent_users} usuários")
        
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
                    logger.info(f"Usuário {user_id} completou submissões de feedback")
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
        
        # Separar resultados por tipo de feedback
        feedback_type_results = {}
        for result in self.results:
            if result.feedback_type not in feedback_type_results:
                feedback_type_results[result.feedback_type] = []
            feedback_type_results[result.feedback_type].append(result)
        
        # Calcular métricas por tipo de feedback
        feedback_type_metrics = {}
        for feedback_type, results in feedback_type_results.items():
            response_times = [r.response_time for r in results]
            success_count = sum(1 for r in results if r.success)
            total_count = len(results)
            priorities = [r.priority for r in results if r.priority]
            
            feedback_type_metrics[feedback_type] = {
                "total_submissions": total_count,
                "successful_submissions": success_count,
                "success_rate": (success_count / total_count) * 100 if total_count > 0 else 0,
                "avg_response_time": statistics.mean(response_times) if response_times else 0,
                "min_response_time": min(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0,
                "p95_response_time": statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times) if response_times else 0,
                "most_common_priority": max(set(priorities), key=priorities.count) if priorities else None
            }
        
        # Métricas gerais
        all_response_times = [r.response_time for r in self.results]
        all_successful = sum(1 for r in self.results if r.success)
        total_submissions = len(self.results)
        all_priorities = [r.priority for r in self.results if r.priority]
        
        return {
            "test_configuration": {
                "concurrent_users": self.config.concurrent_users,
                "test_duration": total_duration,
                "total_submissions": total_submissions,
                "feedback_types": self.config.feedback_types
            },
            "overall_metrics": {
                "total_submissions": total_submissions,
                "successful_submissions": all_successful,
                "success_rate": (all_successful / total_submissions) * 100 if total_submissions > 0 else 0,
                "avg_response_time": statistics.mean(all_response_times) if all_response_times else 0,
                "min_response_time": min(all_response_times) if all_response_times else 0,
                "max_response_time": max(all_response_times) if all_response_times else 0,
                "p95_response_time": statistics.quantiles(all_response_times, n=20)[18] if len(all_response_times) >= 20 else max(all_response_times) if all_response_times else 0,
                "submissions_per_second": total_submissions / total_duration if total_duration > 0 else 0,
                "most_common_priority": max(set(all_priorities), key=all_priorities.count) if all_priorities else None
            },
            "feedback_type_metrics": feedback_type_metrics,
            "errors": [
                {
                    "feedback_type": r.feedback_type,
                    "status_code": r.status_code,
                    "error_message": r.error_message,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in self.results if not r.success
            ]
        }

def run_feedback_submission_load_test(
    base_url: str = "http://localhost:8000",
    concurrent_users: int = 30,
    test_duration: int = 180
) -> Dict[str, Any]:
    """Função principal para executar teste de carga em submissão de feedback"""
    
    config = FeedbackSubmissionTestConfig(
        base_url=base_url,
        concurrent_users=concurrent_users,
        test_duration=test_duration
    )
    
    tester = FeedbackSubmissionLoadTester(config)
    results = tester.run_load_test()
    
    # Log dos resultados
    logger.info("=== RESULTADOS DO TESTE DE CARGA EM SUBMISSÃO DE FEEDBACK ===")
    logger.info(f"Total de submissões: {results['overall_metrics']['total_submissions']}")
    logger.info(f"Taxa de sucesso: {results['overall_metrics']['success_rate']:.2f}%")
    logger.info(f"Tempo médio de resposta: {results['overall_metrics']['avg_response_time']:.3f}s")
    logger.info(f"P95 tempo de resposta: {results['overall_metrics']['p95_response_time']:.3f}s")
    logger.info(f"Submissões por segundo: {results['overall_metrics']['submissions_per_second']:.2f}")
    logger.info(f"Prioridade mais comum: {results['overall_metrics']['most_common_priority']}")
    
    return results

if __name__ == "__main__":
    # Executar teste de carga
    results = run_feedback_submission_load_test(
        base_url="http://localhost:8000",
        concurrent_users=30,
        test_duration=180
    )
    
    # Salvar resultados em arquivo
    with open("feedback_submission_load_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("Teste de carga em submissão de feedback concluído. Resultados salvos em feedback_submission_load_test_results.json") 