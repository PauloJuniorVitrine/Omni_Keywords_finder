"""
⚡ Teste de Carga - Performance de Uso de CPU
🎯 Objetivo: Testar uso de CPU em operações de processamento e otimizações
📅 Data: 2025-01-27
🔗 Tracing ID: LOAD_PERF_CPU_USAGE_001
📋 Ruleset: enterprise_control_layer.yaml

📐 CoCoT: Baseado em código real de otimizações de CPU e processamento
🌲 ToT: Avaliadas múltiplas estratégias de otimização de CPU
♻️ ReAct: Simulado cenários de carga e validada utilização de CPU

Testa endpoints baseados em:
- infrastructure/performance/optimizations.py
- infrastructure/processamento/parallel_processor.py
- infrastructure/performance/performance_monitor.py
- backend/app/api/advanced_metrics.py
"""

import time
import json
import random
import psutil
import threading
import multiprocessing
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import statistics

from locust import HttpUser, task, between, events
from locust.exception import StopUser

# Configuração de logging
import logging
logger = logging.getLogger(__name__)

@dataclass
class CPUMetrics:
    """Métricas de uso de CPU"""
    operation_name: str
    cpu_before: float
    cpu_after: float
    cpu_peak: float
    cpu_average: float
    cpu_percentile_95: float
    cpu_percentile_99: float
    execution_time: float
    thread_count: int
    process_count: int
    success_count: int
    error_count: int
    timestamp: datetime

class CPUUsageLoadTest(HttpUser):
    """
    Teste de carga para uso de CPU
    Baseado em endpoints reais de processamento e otimizações
    """
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Inicialização do teste"""
        self.metrics: List[CPUMetrics] = []
        self.start_time = time.time()
        self.cpu_peak = 0
        self.cpu_samples = []
        
        # Configurações de teste baseadas em código real
        self.test_config = {
            'cpu_thresholds': {
                'warning': 70.0,     # %
                'critical': 85.0,    # %
                'max_peak': 95.0     # %
            },
            'concurrency_levels': [5, 10, 20, 50, 100],
            'batch_sizes': [50, 100, 200, 500],
            'operation_types': ['cpu_intensive', 'io_intensive', 'mixed_operations', 'parallel_processing'],
            'cpu_monitoring': True,
            'thread_monitoring': True,
            'process_monitoring': True
        }
        
        # Iniciar monitoramento de CPU
        if self.test_config['cpu_monitoring']:
            self._start_cpu_monitoring()
        
        logger.info(f"Teste de uso de CPU iniciado - {self.test_config}")
    
    def on_stop(self):
        """Finalização do teste"""
        if self.test_config['cpu_monitoring']:
            self._stop_cpu_monitoring()
        self._generate_cpu_report()
    
    @task(3)
    def test_cpu_intensive_operations(self):
        """Teste de operações intensivas de CPU"""
        self._test_cpu_usage("cpu_intensive", batch_size=100)
    
    @task(2)
    def test_io_intensive_operations(self):
        """Teste de operações intensivas de I/O"""
        self._test_cpu_usage("io_intensive", batch_size=200)
    
    @task(2)
    def test_mixed_operations(self):
        """Teste de operações mistas"""
        self._test_cpu_usage("mixed_operations", batch_size=150)
    
    @task(2)
    def test_parallel_processing(self):
        """Teste de processamento paralelo"""
        self._test_cpu_usage("parallel_processing", batch_size=300)
    
    @task(1)
    def test_cpu_stress(self):
        """Teste de estresse de CPU"""
        self._test_cpu_stress()
    
    def _test_cpu_usage(self, operation_type: str, batch_size: int):
        """Teste de uso de CPU"""
        # Coletar métricas iniciais
        cpu_before = self._get_cpu_usage()
        thread_count_before = threading.active_count()
        process_count_before = len(psutil.pids())
        start_time = time.time()
        
        # Iniciar coleta de amostras de CPU
        cpu_samples = []
        monitoring_thread = None
        
        if self.test_config['cpu_monitoring']:
            monitoring_thread = threading.Thread(
                target=self._collect_cpu_samples,
                args=(cpu_samples,),
                daemon=True
            )
            monitoring_thread.start()
        
        try:
            # Gerar dados de teste
            test_data = self._generate_test_data(batch_size, operation_type)
            
            # Preparar payload baseado em operação
            if operation_type == "cpu_intensive":
                payload = self._prepare_cpu_intensive_payload(test_data)
                endpoint = "/api/processar_keywords"
            elif operation_type == "io_intensive":
                payload = self._prepare_io_intensive_payload(test_data)
                endpoint = "/api/cache/operations"
            elif operation_type == "mixed_operations":
                payload = self._prepare_mixed_payload(test_data)
                endpoint = "/api/advanced_metrics"
            else:
                payload = self._prepare_parallel_payload(test_data)
                endpoint = "/api/processar_keywords"
            
            # Executar requisição
            with self.client.post(
                endpoint,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Operation-Type": operation_type,
                    "X-Batch-Size": str(batch_size),
                    "X-CPU-Monitoring": "true",
                    "X-Concurrency-Level": str(random.choice(self.test_config['concurrency_levels']))
                },
                catch_response=True,
                timeout=120
            ) as response:
                end_time = time.time()
                cpu_after = self._get_cpu_usage()
                thread_count_after = threading.active_count()
                process_count_after = len(psutil.pids())
                
                execution_time = end_time - start_time
                thread_count = thread_count_after - thread_count_before
                process_count = process_count_after - process_count_before
                
                # Calcular estatísticas de CPU
                if cpu_samples:
                    cpu_average = statistics.mean(cpu_samples)
                    cpu_peak = max(cpu_samples)
                    cpu_p95 = statistics.quantiles(cpu_samples, n=20)[18] if len(cpu_samples) >= 20 else max(cpu_samples)
                    cpu_p99 = statistics.quantiles(cpu_samples, n=100)[98] if len(cpu_samples) >= 100 else max(cpu_samples)
                else:
                    cpu_average = (cpu_before + cpu_after) / 2
                    cpu_peak = max(cpu_before, cpu_after)
                    cpu_p95 = cpu_peak
                    cpu_p99 = cpu_peak
                
                # Atualizar pico global
                if cpu_peak > self.cpu_peak:
                    self.cpu_peak = cpu_peak
                
                # Validar resposta
                if response.status_code == 200:
                    response_data = response.json()
                    
                    if self._validate_cpu_response(response_data, operation_type):
                        # Registrar métricas de sucesso
                        metrics = CPUMetrics(
                            operation_name=f"cpu_usage_{operation_type}",
                            cpu_before=cpu_before,
                            cpu_after=cpu_after,
                            cpu_peak=cpu_peak,
                            cpu_average=cpu_average,
                            cpu_percentile_95=cpu_p95,
                            cpu_percentile_99=cpu_p99,
                            execution_time=execution_time,
                            thread_count=thread_count,
                            process_count=process_count,
                            success_count=batch_size,
                            error_count=0,
                            timestamp=datetime.now()
                        )
                        self.metrics.append(metrics)
                        
                        # Validar thresholds de CPU
                        self._validate_cpu_thresholds(metrics, operation_type)
                        
                        response.success()
                        logger.info(f"Operação {operation_type} bem-sucedida: {batch_size} itens, CPU: {cpu_average:.2f}%")
                    else:
                        response.failure("Resposta inválida")
                else:
                    response.failure(f"Status code: {response.status_code}")
                    
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            cpu_after = self._get_cpu_usage()
            
            metrics = CPUMetrics(
                operation_name=f"cpu_usage_{operation_type}_error",
                cpu_before=cpu_before,
                cpu_after=cpu_after,
                cpu_peak=cpu_after,
                cpu_average=cpu_after,
                cpu_percentile_95=cpu_after,
                cpu_percentile_99=cpu_after,
                execution_time=execution_time,
                thread_count=0,
                process_count=0,
                success_count=0,
                error_count=batch_size,
                timestamp=datetime.now()
            )
            self.metrics.append(metrics)
            
            logger.error(f"Erro na operação {operation_type}: {str(e)}")
        
        finally:
            # Parar monitoramento se necessário
            if monitoring_thread and monitoring_thread.is_alive():
                monitoring_thread.join(timeout=1)
    
    def _test_cpu_stress(self):
        """Teste de estresse de CPU"""
        logger.info("Iniciando teste de estresse de CPU")
        
        # Executar operações que consomem muita CPU
        for i in range(5):
            cpu_before = self._get_cpu_usage()
            start_time = time.time()
            
            # Simular carga de CPU
            self._simulate_cpu_load()
            
            cpu_after = self._get_cpu_usage()
            execution_time = time.time() - start_time
            
            logger.info(f"Estresse {i+1}: CPU {cpu_before:.2f}% -> {cpu_after:.2f}% em {execution_time:.2f}s")
            
            # Aguardar entre testes
            time.sleep(2)
    
    def _get_cpu_usage(self) -> float:
        """Obter uso de CPU atual"""
        try:
            return psutil.cpu_percent(interval=1)
        except Exception as e:
            logger.error(f"Erro ao obter uso de CPU: {str(e)}")
            return 0.0
    
    def _collect_cpu_samples(self, samples: List[float], duration: float = 30):
        """Coletar amostras de CPU durante execução"""
        start_time = time.time()
        while time.time() - start_time < duration:
            try:
                cpu_usage = psutil.cpu_percent(interval=0.1)
                samples.append(cpu_usage)
                time.sleep(0.1)
            except Exception as e:
                logger.debug(f"Erro ao coletar amostra de CPU: {str(e)}")
                break
    
    def _generate_test_data(self, count: int, operation_type: str) -> List[Dict[str, Any]]:
        """Gerar dados de teste baseados no tipo de operação"""
        if operation_type == "cpu_intensive":
            return self._generate_cpu_intensive_data(count)
        elif operation_type == "io_intensive":
            return self._generate_io_intensive_data(count)
        elif operation_type == "mixed_operations":
            return self._generate_mixed_data(count)
        else:
            return self._generate_parallel_data(count)
    
    def _generate_cpu_intensive_data(self, count: int) -> List[Dict[str, Any]]:
        """Gerar dados para operações intensivas de CPU"""
        data = []
        for i in range(count):
            # Dados que requerem processamento intensivo
            item = {
                "id": f"cpu_intensive_{i}",
                "complex_calculation": {
                    "iterations": random.randint(1000, 10000),
                    "precision": random.randint(10, 100),
                    "algorithm": random.choice(["monte_carlo", "fourier", "matrix_mult", "sorting"])
                },
                "data_processing": {
                    "size": random.randint(10000, 100000),
                    "compression_level": random.randint(1, 9),
                    "encryption": random.choice([True, False])
                },
                "ml_operations": {
                    "model_type": random.choice(["neural_network", "random_forest", "svm", "clustering"]),
                    "features": random.randint(100, 1000),
                    "iterations": random.randint(100, 1000)
                }
            }
            data.append(item)
        return data
    
    def _generate_io_intensive_data(self, count: int) -> List[Dict[str, Any]]:
        """Gerar dados para operações intensivas de I/O"""
        data = []
        for i in range(count):
            # Dados que requerem muitas operações de I/O
            item = {
                "id": f"io_intensive_{i}",
                "file_operations": {
                    "read_files": random.randint(10, 100),
                    "write_files": random.randint(5, 50),
                    "file_size": random.randint(1024, 102400)  # 1KB - 100KB
                },
                "network_operations": {
                    "api_calls": random.randint(20, 200),
                    "data_transfer": random.randint(1000, 10000),
                    "timeout": random.randint(5, 30)
                },
                "database_operations": {
                    "queries": random.randint(50, 500),
                    "batch_size": random.randint(100, 1000),
                    "transactions": random.randint(10, 100)
                }
            }
            data.append(item)
        return data
    
    def _generate_mixed_data(self, count: int) -> List[Dict[str, Any]]:
        """Gerar dados para operações mistas"""
        data = []
        for i in range(count):
            # Dados que combinam CPU e I/O
            item = {
                "id": f"mixed_{i}",
                "operation_type": random.choice(["cpu_heavy", "io_heavy", "balanced"]),
                "cpu_operations": {
                    "calculations": random.randint(100, 1000),
                    "processing_time": random.uniform(0.1, 2.0)
                },
                "io_operations": {
                    "file_access": random.randint(5, 50),
                    "network_calls": random.randint(10, 100)
                },
                "memory_operations": {
                    "allocation_size": random.randint(1024, 102400),
                    "cache_operations": random.randint(20, 200)
                }
            }
            data.append(item)
        return data
    
    def _generate_parallel_data(self, count: int) -> List[Dict[str, Any]]:
        """Gerar dados para processamento paralelo"""
        data = []
        for i in range(count):
            # Dados otimizados para processamento paralelo
            item = {
                "id": f"parallel_{i}",
                "parallel_config": {
                    "workers": random.randint(2, 16),
                    "chunk_size": random.randint(10, 100),
                    "priority": random.choice(["low", "medium", "high"])
                },
                "workload": {
                    "type": random.choice(["embeddings", "clustering", "analysis", "export"]),
                    "complexity": random.choice(["simple", "medium", "complex"]),
                    "estimated_time": random.uniform(0.5, 10.0)
                },
                "optimization": {
                    "cache_enabled": random.choice([True, False]),
                    "compression_enabled": random.choice([True, False]),
                    "async_processing": random.choice([True, False])
                }
            }
            data.append(item)
        return data
    
    def _prepare_cpu_intensive_payload(self, test_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Preparar payload para operações intensivas de CPU"""
        return {
            "operations": test_data,
            "cpu_config": {
                "max_workers": multiprocessing.cpu_count(),
                "enable_optimization": True,
                "enable_parallel": True,
                "cpu_priority": "high"
            },
            "processing": {
                "algorithm": "intensive",
                "iterations": 1000,
                "precision": 50
            },
            "monitoring": {
                "track_cpu": True,
                "track_memory": True,
                "track_performance": True
            }
        }
    
    def _prepare_io_intensive_payload(self, test_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Preparar payload para operações intensivas de I/O"""
        return {
            "operations": test_data,
            "io_config": {
                "enable_async": True,
                "enable_buffering": True,
                "enable_compression": True,
                "max_concurrent_io": 50
            },
            "cache_config": {
                "enable_cache": True,
                "cache_size": 1000,
                "ttl": 3600
            },
            "monitoring": {
                "track_io": True,
                "track_latency": True,
                "track_throughput": True
            }
        }
    
    def _prepare_mixed_payload(self, test_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Preparar payload para operações mistas"""
        return {
            "operations": test_data,
            "config": {
                "enable_balanced_processing": True,
                "enable_adaptive_optimization": True,
                "enable_resource_monitoring": True
            },
            "optimization": {
                "cpu_optimization": True,
                "io_optimization": True,
                "memory_optimization": True
            },
            "monitoring": {
                "track_all_metrics": True,
                "enable_alerting": True,
                "enable_reporting": True
            }
        }
    
    def _prepare_parallel_payload(self, test_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Preparar payload para processamento paralelo"""
        return {
            "operations": test_data,
            "parallel_config": {
                "workers": multiprocessing.cpu_count(),
                "chunk_size": 100,
                "enable_load_balancing": True,
                "enable_fault_tolerance": True
            },
            "optimization": {
                "enable_work_stealing": True,
                "enable_dynamic_scaling": True,
                "enable_performance_tuning": True
            },
            "monitoring": {
                "track_parallel_metrics": True,
                "track_worker_performance": True,
                "track_load_distribution": True
            }
        }
    
    def _validate_cpu_response(self, response_data: Dict[str, Any], operation_type: str) -> bool:
        """Validar resposta considerando uso de CPU"""
        try:
            if not isinstance(response_data, dict):
                return False
            
            # Validações específicas por tipo de operação
            if operation_type == "cpu_intensive":
                return "results" in response_data or "processing_stats" in response_data
            elif operation_type == "io_intensive":
                return "cache_stats" in response_data or "io_stats" in response_data
            elif operation_type == "mixed_operations":
                return "metrics" in response_data or "performance_stats" in response_data
            else:
                return "parallel_results" in response_data or "worker_stats" in response_data
            
        except Exception as e:
            logger.error(f"Erro na validação da resposta: {str(e)}")
            return False
    
    def _validate_cpu_thresholds(self, metrics: CPUMetrics, operation_type: str):
        """Validar thresholds de CPU"""
        thresholds = self.test_config['cpu_thresholds']
        
        # Validar uso médio de CPU
        if metrics.cpu_average > thresholds['warning']:
            logger.warning(f"Uso médio de CPU alto: {metrics.cpu_average:.2f}% > {thresholds['warning']}%")
        
        if metrics.cpu_average > thresholds['critical']:
            logger.error(f"Uso médio de CPU crítico: {metrics.cpu_average:.2f}% > {thresholds['critical']}%")
        
        # Validar pico de CPU
        if metrics.cpu_peak > thresholds['max_peak']:
            logger.error(f"Pico de CPU muito alto: {metrics.cpu_peak:.2f}% > {thresholds['max_peak']}%")
        
        # Validar percentil 95
        if metrics.cpu_percentile_95 > thresholds['critical']:
            logger.warning(f"CPU P95 alto: {metrics.cpu_percentile_95:.2f}% > {thresholds['critical']}%")
        
        # Validar número de threads
        if metrics.thread_count > 100:
            logger.warning(f"Muitas threads criadas: {metrics.thread_count}")
    
    def _simulate_cpu_load(self):
        """Simular carga de CPU"""
        try:
            # Operações que consomem CPU
            for i in range(1000000):
                _ = i * i + i / 2
            
            # Pequena pausa
            time.sleep(0.1)
            
        except Exception as e:
            logger.debug(f"Erro na simulação de carga: {str(e)}")
    
    def _generate_cpu_report(self):
        """Gerar relatório de uso de CPU"""
        if not self.metrics:
            return
        
        # Calcular estatísticas
        cpu_averages = [m.cpu_average for m in self.metrics]
        cpu_peaks = [m.cpu_peak for m in self.metrics]
        cpu_p95s = [m.cpu_percentile_95 for m in self.metrics]
        execution_times = [m.execution_time for m in self.metrics]
        thread_counts = [m.thread_count for m in self.metrics]
        
        total_success = sum(m.success_count for m in self.metrics)
        total_errors = sum(m.error_count for m in self.metrics)
        
        # Análise de tendência de CPU
        cpu_trend = self._analyze_cpu_trend()
        
        report = {
            "test_name": "CPU Usage Load Test",
            "timestamp": datetime.now().isoformat(),
            "total_operations": len(self.metrics),
            "total_items_processed": total_success,
            "total_errors": total_errors,
            "success_rate": (total_success / (total_success + total_errors)) * 100 if (total_success + total_errors) > 0 else 0,
            "cpu_metrics": {
                "cpu_average": {
                    "mean": statistics.mean(cpu_averages) if cpu_averages else 0,
                    "median": statistics.median(cpu_averages) if cpu_averages else 0,
                    "min": min(cpu_averages) if cpu_averages else 0,
                    "max": max(cpu_averages) if cpu_averages else 0,
                    "p95": statistics.quantiles(cpu_averages, n=20)[18] if len(cpu_averages) >= 20 else max(cpu_averages) if cpu_averages else 0
                },
                "cpu_peak": {
                    "mean": statistics.mean(cpu_peaks) if cpu_peaks else 0,
                    "max": max(cpu_peaks) if cpu_peaks else 0
                },
                "cpu_percentile_95": {
                    "mean": statistics.mean(cpu_p95s) if cpu_p95s else 0,
                    "max": max(cpu_p95s) if cpu_p95s else 0
                }
            },
            "performance_metrics": {
                "execution_time": {
                    "mean": statistics.mean(execution_times) if execution_times else 0,
                    "max": max(execution_times) if execution_times else 0
                },
                "thread_count": {
                    "mean": statistics.mean(thread_counts) if thread_counts else 0,
                    "max": max(thread_counts) if thread_counts else 0
                }
            },
            "cpu_trend_analysis": cpu_trend,
            "test_config": self.test_config
        }
        
        # Salvar relatório
        try:
            with open(f"test-results/cpu_usage_report_{int(time.time())}.json", "w") as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Relatório de uso de CPU salvo: cpu_usage_report_{int(time.time())}.json")
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {str(e)}")
    
    def _analyze_cpu_trend(self) -> Dict[str, Any]:
        """Analisar tendência de uso de CPU"""
        if len(self.metrics) < 5:
            return {"insufficient_data": True}
        
        # Calcular tendência linear
        x_values = list(range(len(self.metrics)))
        y_values = [m.cpu_average for m in self.metrics]
        
        try:
            # Calcular correlação
            correlation = statistics.correlation(x_values, y_values) if len(x_values) > 1 else 0
            
            # Calcular slope (tendência)
            if len(x_values) > 1:
                slope = (y_values[-1] - y_values[0]) / (x_values[-1] - x_values[0])
            else:
                slope = 0
            
            # Determinar se há tendência de aumento
            cpu_increasing = correlation > 0.5 and slope > 0.5  # Aumento consistente > 0.5% por operação
            
            return {
                "correlation": correlation,
                "slope": slope,
                "cpu_increasing": cpu_increasing,
                "trend_strength": "strong" if abs(correlation) > 0.8 else "moderate" if abs(correlation) > 0.5 else "weak",
                "recommendation": "Investigar aumento de CPU" if cpu_increasing else "Uso de CPU estável"
            }
            
        except Exception as e:
            return {"error": str(e)}

# Event listeners para métricas globais
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Evento de início do teste"""
    logger.info("Teste de uso de CPU iniciado")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Evento de fim do teste"""
    logger.info("Teste de uso de CPU finalizado") 