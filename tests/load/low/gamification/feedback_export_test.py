"""
Teste de Carga para Exportação de Feedback - Gamificação
Tracing ID: FEEDBACK_EXPORT_001
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
class FeedbackExportTestConfig:
    """Configuração para testes de carga em exportação de feedback"""
    base_url: str = "http://localhost:8000"
    concurrent_users: int = 20
    test_duration: int = 90  # 1.5 minutos
    export_formats: List[str] = None
    
    def __post_init__(self):
        if self.export_formats is None:
            self.export_formats = [
                "json",
                "csv",
                "excel",
                "pdf",
                "xml"
            ]

@dataclass
class FeedbackExportTestResult:
    """Resultado de teste de exportação de feedback"""
    operation: str
    response_time: float
    status_code: int
    success: bool
    timestamp: datetime
    user_id: int
    export_format: Optional[str] = None
    file_size_bytes: Optional[int] = None
    records_count: Optional[int] = None
    download_url: Optional[str] = None
    error_message: Optional[str] = None

class FeedbackExportLoadTester:
    """Testador de carga para exportação de feedback"""
    
    def __init__(self, config: FeedbackExportTestConfig):
        self.config = config
        self.results: List[FeedbackExportTestResult] = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def _authenticate_user(self, user_id: int) -> bool:
        """Autenticar usuário para operações de exportação"""
        try:
            auth_data = {
                "username": f"export_user_{user_id}",
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
    
    def _export_feedback(self, export_format: str, user_id: int) -> FeedbackExportTestResult:
        """Exportar feedback"""
        start_time = time.time()
        
        try:
            # Autenticar usuário
            if not self._authenticate_user(user_id):
                return FeedbackExportTestResult(
                    operation="export_feedback",
                    response_time=time.time() - start_time,
                    status_code=401,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    export_format=export_format,
                    error_message="Falha na autenticação"
                )
            
            # Dados para exportação
            export_data = {
                "user_id": user_id,
                "request_id": str(uuid.uuid4()),
                "export_format": export_format,
                "filters": {
                    "date_from": (datetime.now() - timedelta(days=30)).isoformat(),
                    "date_to": datetime.now().isoformat(),
                    "feedback_types": ["bug_report", "feature_request", "general_feedback"],
                    "priority_levels": ["low", "medium", "high"]
                },
                "options": {
                    "include_metadata": True,
                    "include_analysis": True,
                    "compress": False
                }
            }
            
            # Fazer requisição para exportação
            response = self.session.post(
                f"{self.config.base_url}/api/feedback/export",
                json=export_data,
                timeout=60
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                file_size_bytes = response_data.get('file_size_bytes')
                records_count = response_data.get('records_count')
                download_url = response_data.get('download_url')
                
                return FeedbackExportTestResult(
                    operation="export_feedback",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=True,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    export_format=export_format,
                    file_size_bytes=file_size_bytes,
                    records_count=records_count,
                    download_url=download_url
                )
            else:
                return FeedbackExportTestResult(
                    operation="export_feedback",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    export_format=export_format,
                    error_message=response.text
                )
            
        except requests.exceptions.Timeout:
            return FeedbackExportTestResult(
                operation="export_feedback",
                response_time=time.time() - start_time,
                status_code=408,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                export_format=export_format,
                error_message="Timeout na exportação de feedback"
            )
            
        except Exception as e:
            return FeedbackExportTestResult(
                operation="export_feedback",
                response_time=time.time() - start_time,
                status_code=500,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                export_format=export_format,
                error_message=str(e)
            )
    
    def _user_workload(self, user_id: int) -> List[FeedbackExportTestResult]:
        """Simular carga de trabalho de um usuário"""
        user_results = []
        
        # Exportar em diferentes formatos
        for export_format in self.config.export_formats:
            result = self._export_feedback(export_format, user_id)
            user_results.append(result)
            
            # Pausa entre exportações
            time.sleep(2)
            
        return user_results
    
    def run_load_test(self) -> Dict[str, Any]:
        """Executar teste de carga completo"""
        logger.info(f"Iniciando teste de carga para exportação de feedback com {self.config.concurrent_users} usuários")
        
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
                    logger.info(f"Usuário {user_id} completou exportações de feedback")
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
        
        # Separar resultados por formato de exportação
        export_format_results = {}
        for result in self.results:
            if result.export_format not in export_format_results:
                export_format_results[result.export_format] = []
            export_format_results[result.export_format].append(result)
        
        # Calcular métricas por formato de exportação
        export_format_metrics = {}
        for export_format, results in export_format_results.items():
            response_times = [r.response_time for r in results]
            success_count = sum(1 for r in results if r.success)
            total_count = len(results)
            file_sizes = [r.file_size_bytes for r in results if r.file_size_bytes]
            records_counts = [r.records_count for r in results if r.records_count]
            
            export_format_metrics[export_format] = {
                "total_exports": total_count,
                "successful_exports": success_count,
                "success_rate": (success_count / total_count) * 100 if total_count > 0 else 0,
                "avg_response_time": statistics.mean(response_times) if response_times else 0,
                "min_response_time": min(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0,
                "p95_response_time": statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times) if response_times else 0,
                "avg_file_size_mb": statistics.mean(file_sizes) / (1024 * 1024) if file_sizes else 0,
                "avg_records_count": statistics.mean(records_counts) if records_counts else 0
            }
        
        # Métricas gerais
        all_response_times = [r.response_time for r in self.results]
        all_successful = sum(1 for r in self.results if r.success)
        total_exports = len(self.results)
        all_file_sizes = [r.file_size_bytes for r in self.results if r.file_size_bytes]
        all_records_counts = [r.records_count for r in self.results if r.records_count]
        
        return {
            "test_configuration": {
                "concurrent_users": self.config.concurrent_users,
                "test_duration": total_duration,
                "total_exports": total_exports,
                "export_formats": self.config.export_formats
            },
            "overall_metrics": {
                "total_exports": total_exports,
                "successful_exports": all_successful,
                "success_rate": (all_successful / total_exports) * 100 if total_exports > 0 else 0,
                "avg_response_time": statistics.mean(all_response_times) if all_response_times else 0,
                "min_response_time": min(all_response_times) if all_response_times else 0,
                "max_response_time": max(all_response_times) if all_response_times else 0,
                "p95_response_time": statistics.quantiles(all_response_times, n=20)[18] if len(all_response_times) >= 20 else max(all_response_times) if all_response_times else 0,
                "exports_per_second": total_exports / total_duration if total_duration > 0 else 0,
                "avg_file_size_mb": statistics.mean(all_file_sizes) / (1024 * 1024) if all_file_sizes else 0,
                "avg_records_count": statistics.mean(all_records_counts) if all_records_counts else 0
            },
            "export_format_metrics": export_format_metrics,
            "errors": [
                {
                    "export_format": r.export_format,
                    "status_code": r.status_code,
                    "error_message": r.error_message,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in self.results if not r.success
            ]
        }

def run_feedback_export_load_test(
    base_url: str = "http://localhost:8000",
    concurrent_users: int = 20,
    test_duration: int = 90
) -> Dict[str, Any]:
    """Função principal para executar teste de carga em exportação de feedback"""
    
    config = FeedbackExportTestConfig(
        base_url=base_url,
        concurrent_users=concurrent_users,
        test_duration=test_duration
    )
    
    tester = FeedbackExportLoadTester(config)
    results = tester.run_load_test()
    
    # Log dos resultados
    logger.info("=== RESULTADOS DO TESTE DE CARGA EM EXPORTAÇÃO DE FEEDBACK ===")
    logger.info(f"Total de exportações: {results['overall_metrics']['total_exports']}")
    logger.info(f"Taxa de sucesso: {results['overall_metrics']['success_rate']:.2f}%")
    logger.info(f"Tempo médio de resposta: {results['overall_metrics']['avg_response_time']:.3f}s")
    logger.info(f"P95 tempo de resposta: {results['overall_metrics']['p95_response_time']:.3f}s")
    logger.info(f"Exportações por segundo: {results['overall_metrics']['exports_per_second']:.2f}")
    logger.info(f"Tamanho médio do arquivo: {results['overall_metrics']['avg_file_size_mb']:.2f} MB")
    logger.info(f"Registros médios: {results['overall_metrics']['avg_records_count']:.2f}")
    
    return results

if __name__ == "__main__":
    # Executar teste de carga
    results = run_feedback_export_load_test(
        base_url="http://localhost:8000",
        concurrent_users=20,
        test_duration=90
    )
    
    # Salvar resultados em arquivo
    with open("feedback_export_load_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("Teste de carga em exportação de feedback concluído. Resultados salvos em feedback_export_load_test_results.json") 