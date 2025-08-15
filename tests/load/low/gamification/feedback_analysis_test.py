"""
Teste de Carga para Análise de Feedback - Gamificação
Tracing ID: FEEDBACK_ANALYSIS_001
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
class FeedbackAnalysisTestConfig:
    """Configuração para testes de carga em análise de feedback"""
    base_url: str = "http://localhost:8000"
    concurrent_users: int = 25
    test_duration: int = 120  # 2 minutos
    analysis_operations: List[str] = None
    
    def __post_init__(self):
        if self.analysis_operations is None:
            self.analysis_operations = [
                "analyze_sentiment",
                "categorize_feedback",
                "extract_keywords",
                "calculate_priority_score",
                "identify_trends",
                "generate_summary"
            ]

@dataclass
class FeedbackAnalysisTestResult:
    """Resultado de teste de análise de feedback"""
    operation: str
    response_time: float
    status_code: int
    success: bool
    timestamp: datetime
    user_id: int
    analysis_type: Optional[str] = None
    sentiment_score: Optional[float] = None
    category: Optional[str] = None
    keywords_count: Optional[int] = None
    priority_score: Optional[float] = None
    error_message: Optional[str] = None

class FeedbackAnalysisLoadTester:
    """Testador de carga para análise de feedback"""
    
    def __init__(self, config: FeedbackAnalysisTestConfig):
        self.config = config
        self.results: List[FeedbackAnalysisTestResult] = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def _authenticate_user(self, user_id: int) -> bool:
        """Autenticar usuário para operações de análise"""
        try:
            auth_data = {
                "username": f"analysis_user_{user_id}",
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
    
    def _analyze_feedback(self, analysis_type: str, user_id: int) -> FeedbackAnalysisTestResult:
        """Analisar feedback"""
        start_time = time.time()
        
        try:
            # Autenticar usuário
            if not self._authenticate_user(user_id):
                return FeedbackAnalysisTestResult(
                    operation="analyze_feedback",
                    response_time=time.time() - start_time,
                    status_code=401,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    analysis_type=analysis_type,
                    error_message="Falha na autenticação"
                )
            
            # Dados para análise
            analysis_data = {
                "user_id": user_id,
                "request_id": str(uuid.uuid4()),
                "analysis_type": analysis_type,
                "feedback_text": "O sistema está funcionando bem, mas gostaria de mais recursos de análise de palavras-chave",
                "feedback_metadata": {
                    "source": "load_test",
                    "timestamp": datetime.now().isoformat(),
                    "user_type": "test"
                },
                "analysis_options": {
                    "include_sentiment": True,
                    "extract_keywords": True,
                    "categorize": True,
                    "calculate_priority": True
                }
            }
            
            # Fazer requisição para análise
            response = self.session.post(
                f"{self.config.base_url}/api/feedback/analyze",
                json=analysis_data,
                timeout=45
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                sentiment_score = response_data.get('sentiment_score')
                category = response_data.get('category')
                keywords_count = len(response_data.get('keywords', []))
                priority_score = response_data.get('priority_score')
                
                return FeedbackAnalysisTestResult(
                    operation="analyze_feedback",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=True,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    analysis_type=analysis_type,
                    sentiment_score=sentiment_score,
                    category=category,
                    keywords_count=keywords_count,
                    priority_score=priority_score
                )
            else:
                return FeedbackAnalysisTestResult(
                    operation="analyze_feedback",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    analysis_type=analysis_type,
                    error_message=response.text
                )
            
        except requests.exceptions.Timeout:
            return FeedbackAnalysisTestResult(
                operation="analyze_feedback",
                response_time=time.time() - start_time,
                status_code=408,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                analysis_type=analysis_type,
                error_message="Timeout na análise de feedback"
            )
            
        except Exception as e:
            return FeedbackAnalysisTestResult(
                operation="analyze_feedback",
                response_time=time.time() - start_time,
                status_code=500,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                analysis_type=analysis_type,
                error_message=str(e)
            )
    
    def _user_workload(self, user_id: int) -> List[FeedbackAnalysisTestResult]:
        """Simular carga de trabalho de um usuário"""
        user_results = []
        
        # Executar diferentes tipos de análise
        for analysis_type in self.config.analysis_operations:
            result = self._analyze_feedback(analysis_type, user_id)
            user_results.append(result)
            
            # Pausa entre análises
            time.sleep(1)
            
        return user_results
    
    def run_load_test(self) -> Dict[str, Any]:
        """Executar teste de carga completo"""
        logger.info(f"Iniciando teste de carga para análise de feedback com {self.config.concurrent_users} usuários")
        
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
                    logger.info(f"Usuário {user_id} completou análises de feedback")
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
        
        # Separar resultados por tipo de análise
        analysis_type_results = {}
        for result in self.results:
            if result.analysis_type not in analysis_type_results:
                analysis_type_results[result.analysis_type] = []
            analysis_type_results[result.analysis_type].append(result)
        
        # Calcular métricas por tipo de análise
        analysis_type_metrics = {}
        for analysis_type, results in analysis_type_results.items():
            response_times = [r.response_time for r in results]
            success_count = sum(1 for r in results if r.success)
            total_count = len(results)
            sentiment_scores = [r.sentiment_score for r in results if r.sentiment_score]
            keywords_counts = [r.keywords_count for r in results if r.keywords_count]
            priority_scores = [r.priority_score for r in results if r.priority_score]
            
            analysis_type_metrics[analysis_type] = {
                "total_analyses": total_count,
                "successful_analyses": success_count,
                "success_rate": (success_count / total_count) * 100 if total_count > 0 else 0,
                "avg_response_time": statistics.mean(response_times) if response_times else 0,
                "min_response_time": min(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0,
                "p95_response_time": statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times) if response_times else 0,
                "avg_sentiment_score": statistics.mean(sentiment_scores) if sentiment_scores else 0,
                "avg_keywords_count": statistics.mean(keywords_counts) if keywords_counts else 0,
                "avg_priority_score": statistics.mean(priority_scores) if priority_scores else 0
            }
        
        # Métricas gerais
        all_response_times = [r.response_time for r in self.results]
        all_successful = sum(1 for r in self.results if r.success)
        total_analyses = len(self.results)
        all_sentiment_scores = [r.sentiment_score for r in self.results if r.sentiment_score]
        all_keywords_counts = [r.keywords_count for r in self.results if r.keywords_count]
        all_priority_scores = [r.priority_score for r in self.results if r.priority_score]
        
        return {
            "test_configuration": {
                "concurrent_users": self.config.concurrent_users,
                "test_duration": total_duration,
                "total_analyses": total_analyses,
                "analysis_operations": self.config.analysis_operations
            },
            "overall_metrics": {
                "total_analyses": total_analyses,
                "successful_analyses": all_successful,
                "success_rate": (all_successful / total_analyses) * 100 if total_analyses > 0 else 0,
                "avg_response_time": statistics.mean(all_response_times) if all_response_times else 0,
                "min_response_time": min(all_response_times) if all_response_times else 0,
                "max_response_time": max(all_response_times) if all_response_times else 0,
                "p95_response_time": statistics.quantiles(all_response_times, n=20)[18] if len(all_response_times) >= 20 else max(all_response_times) if all_response_times else 0,
                "analyses_per_second": total_analyses / total_duration if total_duration > 0 else 0,
                "avg_sentiment_score": statistics.mean(all_sentiment_scores) if all_sentiment_scores else 0,
                "avg_keywords_count": statistics.mean(all_keywords_counts) if all_keywords_counts else 0,
                "avg_priority_score": statistics.mean(all_priority_scores) if all_priority_scores else 0
            },
            "analysis_type_metrics": analysis_type_metrics,
            "errors": [
                {
                    "analysis_type": r.analysis_type,
                    "status_code": r.status_code,
                    "error_message": r.error_message,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in self.results if not r.success
            ]
        }

def run_feedback_analysis_load_test(
    base_url: str = "http://localhost:8000",
    concurrent_users: int = 25,
    test_duration: int = 120
) -> Dict[str, Any]:
    """Função principal para executar teste de carga em análise de feedback"""
    
    config = FeedbackAnalysisTestConfig(
        base_url=base_url,
        concurrent_users=concurrent_users,
        test_duration=test_duration
    )
    
    tester = FeedbackAnalysisLoadTester(config)
    results = tester.run_load_test()
    
    # Log dos resultados
    logger.info("=== RESULTADOS DO TESTE DE CARGA EM ANÁLISE DE FEEDBACK ===")
    logger.info(f"Total de análises: {results['overall_metrics']['total_analyses']}")
    logger.info(f"Taxa de sucesso: {results['overall_metrics']['success_rate']:.2f}%")
    logger.info(f"Tempo médio de resposta: {results['overall_metrics']['avg_response_time']:.3f}s")
    logger.info(f"P95 tempo de resposta: {results['overall_metrics']['p95_response_time']:.3f}s")
    logger.info(f"Análises por segundo: {results['overall_metrics']['analyses_per_second']:.2f}")
    logger.info(f"Score de sentimento médio: {results['overall_metrics']['avg_sentiment_score']:.3f}")
    logger.info(f"Palavras-chave médias: {results['overall_metrics']['avg_keywords_count']:.2f}")
    logger.info(f"Score de prioridade médio: {results['overall_metrics']['avg_priority_score']:.3f}")
    
    return results

if __name__ == "__main__":
    # Executar teste de carga
    results = run_feedback_analysis_load_test(
        base_url="http://localhost:8000",
        concurrent_users=25,
        test_duration=120
    )
    
    # Salvar resultados em arquivo
    with open("feedback_analysis_load_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("Teste de carga em análise de feedback concluído. Resultados salvos em feedback_analysis_load_test_results.json") 