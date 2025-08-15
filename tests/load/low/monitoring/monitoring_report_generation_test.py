"""
Teste de Carga para Geração de Relatórios de Monitoramento
Tracing ID: MONITORING_REPORT_GENERATION_001
Data: 2025-01-27
Baseado em: infrastructure/monitoring/
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
class ReportGenerationTestConfig:
    """Configuração para testes de carga em geração de relatórios"""
    base_url: str = "http://localhost:8000"
    concurrent_users: int = 30
    test_duration: int = 600  # 10 minutos
    report_types: List[str] = None
    report_formats: List[str] = None
    
    def __post_init__(self):
        if self.report_types is None:
            self.report_types = [
                "performance_summary",
                "security_audit",
                "business_metrics",
                "system_health",
                "user_activity",
                "error_analysis"
            ]
        
        if self.report_formats is None:
            self.report_formats = ["pdf", "excel", "json", "csv"]

@dataclass
class ReportGenerationTestResult:
    """Resultado de teste de geração de relatório"""
    report_type: str
    report_format: str
    response_time: float
    status_code: int
    success: bool
    timestamp: datetime
    user_id: int
    report_id: Optional[str] = None
    file_size: Optional[int] = None
    error_message: Optional[str] = None

class ReportGenerationLoadTester:
    """Testador de carga para geração de relatórios"""
    
    def __init__(self, config: ReportGenerationTestConfig):
        self.config = config
        self.results: List[ReportGenerationTestResult] = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def _authenticate_user(self, user_id: int) -> bool:
        """Autenticar usuário para geração de relatórios"""
        try:
            auth_data = {
                "username": f"report_user_{user_id}",
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
    
    def _generate_report(self, report_type: str, report_format: str, user_id: int) -> ReportGenerationTestResult:
        """Gerar relatório específico"""
        start_time = time.time()
        
        try:
            # Autenticar usuário
            if not self._authenticate_user(user_id):
                return ReportGenerationTestResult(
                    report_type=report_type,
                    report_format=report_format,
                    response_time=time.time() - start_time,
                    status_code=401,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    error_message="Falha na autenticação"
                )
            
            # Dados do relatório
            report_data = {
                "report_type": report_type,
                "format": report_format,
                "time_range": {
                    "start": (datetime.now() - timedelta(days=7)).isoformat(),
                    "end": datetime.now().isoformat()
                },
                "filters": {
                    "include_charts": True,
                    "include_tables": True,
                    "include_summary": True
                },
                "user_id": user_id,
                "request_id": str(uuid.uuid4())
            }
            
            # Fazer requisição para gerar relatório
            response = self.session.post(
                f"{self.config.base_url}/api/v1/reports/generate",
                json=report_data,
                timeout=120  # 2 minutos para geração
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                report_id = response_data.get('report_id')
                file_size = response_data.get('file_size', 0)
                
                return ReportGenerationTestResult(
                    report_type=report_type,
                    report_format=report_format,
                    response_time=response_time,
                    status_code=response.status_code,
                    success=True,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    report_id=report_id,
                    file_size=file_size
                )
            else:
                return ReportGenerationTestResult(
                    report_type=report_type,
                    report_format=report_format,
                    response_time=response_time,
                    status_code=response.status_code,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    error_message=response.text
                )
            
        except requests.exceptions.Timeout:
            return ReportGenerationTestResult(
                report_type=report_type,
                report_format=report_format,
                response_time=time.time() - start_time,
                status_code=408,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message="Timeout na geração do relatório"
            )
            
        except Exception as e:
            return ReportGenerationTestResult(
                report_type=report_type,
                report_format=report_format,
                response_time=time.time() - start_time,
                status_code=500,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message=str(e)
            )
    
    def _download_report(self, report_id: str, report_format: str, user_id: int) -> ReportGenerationTestResult:
        """Download de relatório gerado"""
        start_time = time.time()
        
        try:
            response = self.session.get(
                f"{self.config.base_url}/api/v1/reports/download/{report_id}",
                params={"format": report_format},
                timeout=60,
                stream=True
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                # Calcular tamanho do arquivo
                file_size = len(response.content) if hasattr(response, 'content') else 0
                
                return ReportGenerationTestResult(
                    report_type="download",
                    report_format=report_format,
                    response_time=response_time,
                    status_code=response.status_code,
                    success=True,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    report_id=report_id,
                    file_size=file_size
                )
            else:
                return ReportGenerationTestResult(
                    report_type="download",
                    report_format=report_format,
                    response_time=response_time,
                    status_code=response.status_code,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    report_id=report_id,
                    error_message=response.text
                )
                
        except Exception as e:
            return ReportGenerationTestResult(
                report_type="download",
                report_format=report_format,
                response_time=time.time() - start_time,
                status_code=500,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                report_id=report_id,
                error_message=str(e)
            )
    
    def _user_workload(self, user_id: int) -> List[ReportGenerationTestResult]:
        """Simular carga de trabalho de um usuário"""
        user_results = []
        
        # Gerar diferentes tipos de relatórios
        for report_type in self.config.report_types:
            for report_format in self.config.report_formats:
                # Gerar relatório
                result = self._generate_report(report_type, report_format, user_id)
                user_results.append(result)
                
                # Se gerou com sucesso, fazer download
                if result.success and result.report_id:
                    download_result = self._download_report(result.report_id, report_format, user_id)
                    user_results.append(download_result)
                
                # Pausa entre requisições
                time.sleep(5)
            
        return user_results
    
    def run_load_test(self) -> Dict[str, Any]:
        """Executar teste de carga completo"""
        logger.info(f"Iniciando teste de carga para geração de relatórios com {self.config.concurrent_users} usuários")
        
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
                    logger.info(f"Usuário {user_id} completou geração de relatórios")
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
        
        # Separar resultados por tipo de relatório
        report_type_results = {}
        for result in self.results:
            if result.report_type not in report_type_results:
                report_type_results[result.report_type] = []
            report_type_results[result.report_type].append(result)
        
        # Separar resultados por formato
        format_results = {}
        for result in self.results:
            if result.report_format not in format_results:
                format_results[result.report_format] = []
            format_results[result.report_format].append(result)
        
        # Calcular métricas por tipo de relatório
        report_type_metrics = {}
        for report_type, results in report_type_results.items():
            response_times = [r.response_time for r in results]
            success_count = sum(1 for r in results if r.success)
            total_count = len(results)
            file_sizes = [r.file_size for r in results if r.file_size]
            
            report_type_metrics[report_type] = {
                "total_requests": total_count,
                "successful_requests": success_count,
                "success_rate": (success_count / total_count) * 100 if total_count > 0 else 0,
                "avg_response_time": statistics.mean(response_times) if response_times else 0,
                "min_response_time": min(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0,
                "p95_response_time": statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times) if response_times else 0,
                "avg_file_size": statistics.mean(file_sizes) if file_sizes else 0
            }
        
        # Calcular métricas por formato
        format_metrics = {}
        for report_format, results in format_results.items():
            response_times = [r.response_time for r in results]
            success_count = sum(1 for r in results if r.success)
            total_count = len(results)
            
            format_metrics[report_format] = {
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
        all_file_sizes = [r.file_size for r in self.results if r.file_size]
        
        return {
            "test_configuration": {
                "concurrent_users": self.config.concurrent_users,
                "test_duration": total_duration,
                "total_requests": total_requests,
                "report_types": self.config.report_types,
                "report_formats": self.config.report_formats
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
                "avg_file_size": statistics.mean(all_file_sizes) if all_file_sizes else 0,
                "total_data_generated": sum(all_file_sizes) if all_file_sizes else 0
            },
            "report_type_metrics": report_type_metrics,
            "format_metrics": format_metrics,
            "errors": [
                {
                    "report_type": r.report_type,
                    "report_format": r.report_format,
                    "status_code": r.status_code,
                    "error_message": r.error_message,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in self.results if not r.success
            ]
        }

def run_report_generation_load_test(
    base_url: str = "http://localhost:8000",
    concurrent_users: int = 30,
    test_duration: int = 600
) -> Dict[str, Any]:
    """Função principal para executar teste de carga em geração de relatórios"""
    
    config = ReportGenerationTestConfig(
        base_url=base_url,
        concurrent_users=concurrent_users,
        test_duration=test_duration
    )
    
    tester = ReportGenerationLoadTester(config)
    results = tester.run_load_test()
    
    # Log dos resultados
    logger.info("=== RESULTADOS DO TESTE DE CARGA EM GERAÇÃO DE RELATÓRIOS ===")
    logger.info(f"Total de requisições: {results['overall_metrics']['total_requests']}")
    logger.info(f"Taxa de sucesso: {results['overall_metrics']['success_rate']:.2f}%")
    logger.info(f"Tempo médio de resposta: {results['overall_metrics']['avg_response_time']:.3f}s")
    logger.info(f"P95 tempo de resposta: {results['overall_metrics']['p95_response_time']:.3f}s")
    logger.info(f"Requisições por segundo: {results['overall_metrics']['requests_per_second']:.2f}")
    logger.info(f"Dados gerados: {results['overall_metrics']['total_data_generated']} bytes")
    
    return results

if __name__ == "__main__":
    # Executar teste de carga
    results = run_report_generation_load_test(
        base_url="http://localhost:8000",
        concurrent_users=30,
        test_duration=600
    )
    
    # Salvar resultados em arquivo
    with open("report_generation_load_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("Teste de carga em geração de relatórios concluído. Resultados salvos em report_generation_load_test_results.json") 