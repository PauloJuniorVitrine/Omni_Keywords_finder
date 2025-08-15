"""
Teste de Carga para Exportação de Métricas de Monitoramento
Tracing ID: MONITORING_EXPORT_METRICS_001
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
class MetricsExportTestConfig:
    """Configuração para testes de carga em exportação de métricas"""
    base_url: str = "http://localhost:8000"
    concurrent_users: int = 40
    test_duration: int = 480  # 8 minutos
    metric_types: List[str] = None
    export_formats: List[str] = None
    time_ranges: List[str] = None
    
    def __post_init__(self):
        if self.metric_types is None:
            self.metric_types = [
                "system_metrics",
                "application_metrics", 
                "business_metrics",
                "performance_metrics",
                "security_metrics",
                "user_metrics"
            ]
        
        if self.export_formats is None:
            self.export_formats = ["json", "csv", "excel", "prometheus", "influxdb"]
            
        if self.time_ranges is None:
            self.time_ranges = ["1h", "6h", "24h", "7d", "30d"]

@dataclass
class MetricsExportTestResult:
    """Resultado de teste de exportação de métricas"""
    metric_type: str
    export_format: str
    time_range: str
    response_time: float
    status_code: int
    success: bool
    timestamp: datetime
    user_id: int
    export_id: Optional[str] = None
    data_size: Optional[int] = None
    record_count: Optional[int] = None
    error_message: Optional[str] = None

class MetricsExportLoadTester:
    """Testador de carga para exportação de métricas"""
    
    def __init__(self, config: MetricsExportTestConfig):
        self.config = config
        self.results: List[MetricsExportTestResult] = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def _authenticate_user(self, user_id: int) -> bool:
        """Autenticar usuário para exportação de métricas"""
        try:
            auth_data = {
                "username": f"metrics_user_{user_id}",
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
    
    def _export_metrics(self, metric_type: str, export_format: str, time_range: str, user_id: int) -> MetricsExportTestResult:
        """Exportar métricas específicas"""
        start_time = time.time()
        
        try:
            # Autenticar usuário
            if not self._authenticate_user(user_id):
                return MetricsExportTestResult(
                    metric_type=metric_type,
                    export_format=export_format,
                    time_range=time_range,
                    response_time=time.time() - start_time,
                    status_code=401,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    error_message="Falha na autenticação"
                )
            
            # Calcular range de tempo
            end_time = datetime.now()
            if time_range == "1h":
                start_time_range = end_time - timedelta(hours=1)
            elif time_range == "6h":
                start_time_range = end_time - timedelta(hours=6)
            elif time_range == "24h":
                start_time_range = end_time - timedelta(days=1)
            elif time_range == "7d":
                start_time_range = end_time - timedelta(days=7)
            elif time_range == "30d":
                start_time_range = end_time - timedelta(days=30)
            else:
                start_time_range = end_time - timedelta(hours=1)
            
            # Dados da exportação
            export_data = {
                "metric_type": metric_type,
                "format": export_format,
                "time_range": {
                    "start": start_time_range.isoformat(),
                    "end": end_time.isoformat()
                },
                "filters": {
                    "include_metadata": True,
                    "include_timestamps": True,
                    "aggregation": "auto"
                },
                "user_id": user_id,
                "request_id": str(uuid.uuid4())
            }
            
            # Fazer requisição para exportar métricas
            response = self.session.post(
                f"{self.config.base_url}/api/v1/metrics/export",
                json=export_data,
                timeout=90  # 1.5 minutos para exportação
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                export_id = response_data.get('export_id')
                data_size = response_data.get('data_size', 0)
                record_count = response_data.get('record_count', 0)
                
                return MetricsExportTestResult(
                    metric_type=metric_type,
                    export_format=export_format,
                    time_range=time_range,
                    response_time=response_time,
                    status_code=response.status_code,
                    success=True,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    export_id=export_id,
                    data_size=data_size,
                    record_count=record_count
                )
            else:
                return MetricsExportTestResult(
                    metric_type=metric_type,
                    export_format=export_format,
                    time_range=time_range,
                    response_time=response_time,
                    status_code=response.status_code,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    error_message=response.text
                )
            
        except requests.exceptions.Timeout:
            return MetricsExportTestResult(
                metric_type=metric_type,
                export_format=export_format,
                time_range=time_range,
                response_time=time.time() - start_time,
                status_code=408,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message="Timeout na exportação"
            )
            
        except Exception as e:
            return MetricsExportTestResult(
                metric_type=metric_type,
                export_format=export_format,
                time_range=time_range,
                response_time=time.time() - start_time,
                status_code=500,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                error_message=str(e)
            )
    
    def _download_export(self, export_id: str, export_format: str, user_id: int) -> MetricsExportTestResult:
        """Download de exportação de métricas"""
        start_time = time.time()
        
        try:
            response = self.session.get(
                f"{self.config.base_url}/api/v1/metrics/export/download/{export_id}",
                params={"format": export_format},
                timeout=60,
                stream=True
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                # Calcular tamanho dos dados
                data_size = len(response.content) if hasattr(response, 'content') else 0
                
                return MetricsExportTestResult(
                    metric_type="download",
                    export_format=export_format,
                    time_range="download",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=True,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    export_id=export_id,
                    data_size=data_size
                )
            else:
                return MetricsExportTestResult(
                    metric_type="download",
                    export_format=export_format,
                    time_range="download",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    export_id=export_id,
                    error_message=response.text
                )
                
        except Exception as e:
            return MetricsExportTestResult(
                metric_type="download",
                export_format=export_format,
                time_range="download",
                response_time=time.time() - start_time,
                status_code=500,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                export_id=export_id,
                error_message=str(e)
            )
    
    def _user_workload(self, user_id: int) -> List[MetricsExportTestResult]:
        """Simular carga de trabalho de um usuário"""
        user_results = []
        
        # Exportar diferentes tipos de métricas
        for metric_type in self.config.metric_types:
            for export_format in self.config.export_formats:
                for time_range in self.config.time_ranges:
                    # Exportar métricas
                    result = self._export_metrics(metric_type, export_format, time_range, user_id)
                    user_results.append(result)
                    
                    # Se exportou com sucesso, fazer download
                    if result.success and result.export_id:
                        download_result = self._download_export(result.export_id, export_format, user_id)
                        user_results.append(download_result)
                    
                    # Pausa entre requisições
                    time.sleep(3)
            
        return user_results
    
    def run_load_test(self) -> Dict[str, Any]:
        """Executar teste de carga completo"""
        logger.info(f"Iniciando teste de carga para exportação de métricas com {self.config.concurrent_users} usuários")
        
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
                    logger.info(f"Usuário {user_id} completou exportação de métricas")
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
        
        # Separar resultados por tipo de métrica
        metric_type_results = {}
        for result in self.results:
            if result.metric_type not in metric_type_results:
                metric_type_results[result.metric_type] = []
            metric_type_results[result.metric_type].append(result)
        
        # Separar resultados por formato
        format_results = {}
        for result in self.results:
            if result.export_format not in format_results:
                format_results[result.export_format] = []
            format_results[result.export_format].append(result)
        
        # Separar resultados por range de tempo
        time_range_results = {}
        for result in self.results:
            if result.time_range not in time_range_results:
                time_range_results[result.time_range] = []
            time_range_results[result.time_range].append(result)
        
        # Calcular métricas por tipo de métrica
        metric_type_metrics = {}
        for metric_type, results in metric_type_results.items():
            response_times = [r.response_time for r in results]
            success_count = sum(1 for r in results if r.success)
            total_count = len(results)
            data_sizes = [r.data_size for r in results if r.data_size]
            record_counts = [r.record_count for r in results if r.record_count]
            
            metric_type_metrics[metric_type] = {
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
        
        # Calcular métricas por formato
        format_metrics = {}
        for export_format, results in format_results.items():
            response_times = [r.response_time for r in results]
            success_count = sum(1 for r in results if r.success)
            total_count = len(results)
            
            format_metrics[export_format] = {
                "total_requests": total_count,
                "successful_requests": success_count,
                "success_rate": (success_count / total_count) * 100 if total_count > 0 else 0,
                "avg_response_time": statistics.mean(response_times) if response_times else 0,
                "min_response_time": min(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0
            }
        
        # Calcular métricas por range de tempo
        time_range_metrics = {}
        for time_range, results in time_range_results.items():
            response_times = [r.response_time for r in results]
            success_count = sum(1 for r in results if r.success)
            total_count = len(results)
            
            time_range_metrics[time_range] = {
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
                "metric_types": self.config.metric_types,
                "export_formats": self.config.export_formats,
                "time_ranges": self.config.time_ranges
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
                "total_data_exported": sum(all_data_sizes) if all_data_sizes else 0,
                "avg_record_count": statistics.mean(all_record_counts) if all_record_counts else 0,
                "total_records_exported": sum(all_record_counts) if all_record_counts else 0
            },
            "metric_type_metrics": metric_type_metrics,
            "format_metrics": format_metrics,
            "time_range_metrics": time_range_metrics,
            "errors": [
                {
                    "metric_type": r.metric_type,
                    "export_format": r.export_format,
                    "time_range": r.time_range,
                    "status_code": r.status_code,
                    "error_message": r.error_message,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in self.results if not r.success
            ]
        }

def run_metrics_export_load_test(
    base_url: str = "http://localhost:8000",
    concurrent_users: int = 40,
    test_duration: int = 480
) -> Dict[str, Any]:
    """Função principal para executar teste de carga em exportação de métricas"""
    
    config = MetricsExportTestConfig(
        base_url=base_url,
        concurrent_users=concurrent_users,
        test_duration=test_duration
    )
    
    tester = MetricsExportLoadTester(config)
    results = tester.run_load_test()
    
    # Log dos resultados
    logger.info("=== RESULTADOS DO TESTE DE CARGA EM EXPORTAÇÃO DE MÉTRICAS ===")
    logger.info(f"Total de requisições: {results['overall_metrics']['total_requests']}")
    logger.info(f"Taxa de sucesso: {results['overall_metrics']['success_rate']:.2f}%")
    logger.info(f"Tempo médio de resposta: {results['overall_metrics']['avg_response_time']:.3f}s")
    logger.info(f"P95 tempo de resposta: {results['overall_metrics']['p95_response_time']:.3f}s")
    logger.info(f"Requisições por segundo: {results['overall_metrics']['requests_per_second']:.2f}")
    logger.info(f"Dados exportados: {results['overall_metrics']['total_data_exported']} bytes")
    logger.info(f"Registros exportados: {results['overall_metrics']['total_records_exported']}")
    
    return results

if __name__ == "__main__":
    # Executar teste de carga
    results = run_metrics_export_load_test(
        base_url="http://localhost:8000",
        concurrent_users=40,
        test_duration=480
    )
    
    # Salvar resultados em arquivo
    with open("metrics_export_load_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("Teste de carga em exportação de métricas concluído. Resultados salvos em metrics_export_load_test_results.json") 