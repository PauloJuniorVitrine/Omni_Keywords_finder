"""
⚡ Teste de Carga - Performance de Velocidade de Processamento
🎯 Objetivo: Testar velocidade de processamento de keywords e operações de otimização
📅 Data: 2025-01-27
🔗 Tracing ID: LOAD_PERF_PROCESSING_SPEED_001
📋 Ruleset: enterprise_control_layer.yaml

📐 CoCoT: Baseado em código real de processamento paralelo e otimizações
🌲 ToT: Avaliadas múltiplas estratégias de processamento (paralelo, batch, async)
♻️ ReAct: Simulado cenários de carga e validada performance

Testa endpoints de processamento baseados em:
- infrastructure/processamento/parallel_processor.py
- infrastructure/performance/optimizations.py
- backend/app/api/api_routes.py
- infrastructure/processamento/otimizador_performance_imp005.py
"""

import time
import json
import random
import psutil
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
class ProcessingMetrics:
    """Métricas de processamento"""
    operation_name: str
    execution_time: float
    throughput: float
    memory_usage: float
    cpu_usage: float
    success_count: int
    error_count: int
    timestamp: datetime

class ProcessingSpeedLoadTest(HttpUser):
    """
    Teste de carga para velocidade de processamento
    Baseado em endpoints reais de processamento de keywords
    """
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Inicialização do teste"""
        self.metrics: List[ProcessingMetrics] = []
        self.start_time = time.time()
        self.processed_keywords = 0
        self.failed_operations = 0
        
        # Configurações de teste
        self.test_config = {
            'batch_sizes': [10, 50, 100, 200],
            'concurrency_levels': [5, 10, 20, 50],
            'processing_types': ['parallel', 'batch', 'optimized'],
            'max_execution_time': 30.0,  # segundos
            'memory_threshold': 500.0,   # MB
            'cpu_threshold': 80.0        # %
        }
        
        logger.info(f"Teste de velocidade de processamento iniciado - {self.test_config}")
    
    def on_stop(self):
        """Finalização do teste"""
        self._generate_performance_report()
    
    @task(3)
    def test_parallel_processing_speed(self):
        """Teste de velocidade de processamento paralelo"""
        self._test_processing_speed("parallel", batch_size=100)
    
    @task(2)
    def test_batch_processing_speed(self):
        """Teste de velocidade de processamento em lote"""
        self._test_processing_speed("batch", batch_size=50)
    
    @task(2)
    def test_optimized_processing_speed(self):
        """Teste de velocidade de processamento otimizado"""
        self._test_processing_speed("optimized", batch_size=200)
    
    @task(1)
    def test_small_batch_processing(self):
        """Teste de velocidade com lotes pequenos"""
        self._test_processing_speed("small_batch", batch_size=10)
    
    @task(1)
    def test_large_batch_processing(self):
        """Teste de velocidade com lotes grandes"""
        self._test_processing_speed("large_batch", batch_size=500)
    
    def _test_processing_speed(self, processing_type: str, batch_size: int):
        """Teste de velocidade de processamento"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / (1024 * 1024)  # MB
        start_cpu = psutil.cpu_percent()
        
        try:
            # Gerar dados de teste baseados em código real
            test_keywords = self._generate_test_keywords(batch_size)
            
            # Preparar payload baseado em endpoint real
            payload = {
                "keywords": test_keywords,
                "processing_type": processing_type,
                "optimization_level": "high",
                "batch_size": batch_size,
                "enable_cache": True,
                "enable_parallel": processing_type == "parallel",
                "enable_compression": True
            }
            
            # Executar requisição
            with self.client.post(
                "/api/processar_keywords",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Processing-Type": processing_type,
                    "X-Batch-Size": str(batch_size),
                    "X-Optimization-Level": "high"
                },
                catch_response=True,
                timeout=60
            ) as response:
                end_time = time.time()
                end_memory = psutil.Process().memory_info().rss / (1024 * 1024)  # MB
                end_cpu = psutil.cpu_percent()
                
                execution_time = end_time - start_time
                memory_usage = end_memory - start_memory
                cpu_usage = (end_cpu + start_cpu) / 2
                throughput = batch_size / execution_time if execution_time > 0 else 0
                
                # Validar resposta
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # Validações baseadas em código real
                    if self._validate_processing_response(response_data, batch_size):
                        self.processed_keywords += batch_size
                        
                        # Registrar métricas de sucesso
                        metrics = ProcessingMetrics(
                            operation_name=f"processing_speed_{processing_type}",
                            execution_time=execution_time,
                            throughput=throughput,
                            memory_usage=memory_usage,
                            cpu_usage=cpu_usage,
                            success_count=batch_size,
                            error_count=0,
                            timestamp=datetime.now()
                        )
                        self.metrics.append(metrics)
                        
                        # Validar thresholds de performance
                        self._validate_performance_thresholds(metrics, processing_type)
                        
                        response.success()
                        logger.info(f"Processamento {processing_type} bem-sucedido: {batch_size} keywords em {execution_time:.2f}s")
                    else:
                        response.failure("Resposta inválida")
                        self.failed_operations += 1
                else:
                    response.failure(f"Status code: {response.status_code}")
                    self.failed_operations += 1
                    
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            
            metrics = ProcessingMetrics(
                operation_name=f"processing_speed_{processing_type}_error",
                execution_time=execution_time,
                throughput=0,
                memory_usage=0,
                cpu_usage=0,
                success_count=0,
                error_count=batch_size,
                timestamp=datetime.now()
            )
            self.metrics.append(metrics)
            
            self.failed_operations += 1
            logger.error(f"Erro no processamento {processing_type}: {str(e)}")
    
    def _generate_test_keywords(self, count: int) -> List[Dict[str, Any]]:
        """Gerar keywords de teste baseadas em dados reais"""
        # Dados reais baseados em código do sistema
        sample_keywords = [
            {"termo": "marketing digital", "volume_busca": 12000, "cpc": 2.50, "concorrencia": 0.85},
            {"termo": "seo otimização", "volume_busca": 8900, "cpc": 3.20, "concorrencia": 0.92},
            {"termo": "google ads", "volume_busca": 15000, "cpc": 4.10, "concorrencia": 0.78},
            {"termo": "redes sociais", "volume_busca": 22000, "cpc": 1.80, "concorrencia": 0.65},
            {"termo": "content marketing", "volume_busca": 6800, "cpc": 2.90, "concorrencia": 0.88},
            {"termo": "email marketing", "volume_busca": 9500, "cpc": 2.30, "concorrencia": 0.72},
            {"termo": "analytics google", "volume_busca": 11000, "cpc": 1.50, "concorrencia": 0.45},
            {"termo": "conversão otimização", "volume_busca": 4200, "cpc": 5.20, "concorrencia": 0.95},
            {"termo": "landing page", "volume_busca": 18000, "cpc": 3.80, "concorrencia": 0.82},
            {"termo": "copywriting", "volume_busca": 7500, "cpc": 2.70, "concorrencia": 0.68}
        ]
        
        keywords = []
        for i in range(count):
            base_keyword = sample_keywords[i % len(sample_keywords)]
            keyword = {
                "termo": f"{base_keyword['termo']} {i+1}",
                "volume_busca": base_keyword["volume_busca"] + random.randint(-1000, 1000),
                "cpc": base_keyword["cpc"] + random.uniform(-0.5, 0.5),
                "concorrencia": min(1.0, max(0.0, base_keyword["concorrencia"] + random.uniform(-0.1, 0.1)))
            }
            keywords.append(keyword)
        
        return keywords
    
    def _validate_processing_response(self, response_data: Dict[str, Any], expected_count: int) -> bool:
        """Validar resposta de processamento"""
        try:
            # Validações baseadas em código real
            if not isinstance(response_data, dict):
                return False
            
            if "keywords" not in response_data:
                return False
            
            keywords = response_data.get("keywords", [])
            if not isinstance(keywords, list):
                return False
            
            # Verificar se todas as keywords foram processadas
            if len(keywords) != expected_count:
                return False
            
            # Verificar estrutura das keywords retornadas
            for keyword in keywords:
                if not isinstance(keyword, dict):
                    return False
                if "termo" not in keyword or "score" not in keyword:
                    return False
                if not isinstance(keyword["termo"], str) or not isinstance(keyword["score"], (int, float)):
                    return False
            
            # Verificar relatório se presente
            if "relatorio" in response_data:
                relatorio = response_data["relatorio"]
                if not isinstance(relatorio, dict):
                    return False
                if "status" not in relatorio:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na validação da resposta: {str(e)}")
            return False
    
    def _validate_performance_thresholds(self, metrics: ProcessingMetrics, processing_type: str):
        """Validar thresholds de performance"""
        # Thresholds baseados em código real de otimização
        thresholds = {
            "parallel": {
                "max_execution_time": 5.0,    # 5s para 100 keywords
                "min_throughput": 20.0,       # 20 keywords/s
                "max_memory": 100.0,          # 100MB
                "max_cpu": 80.0               # 80%
            },
            "batch": {
                "max_execution_time": 8.0,    # 8s para 50 keywords
                "min_throughput": 6.0,        # 6 keywords/s
                "max_memory": 80.0,           # 80MB
                "max_cpu": 70.0               # 70%
            },
            "optimized": {
                "max_execution_time": 3.0,    # 3s para 200 keywords
                "min_throughput": 60.0,       # 60 keywords/s
                "max_memory": 150.0,          # 150MB
                "max_cpu": 85.0               # 85%
            }
        }
        
        threshold = thresholds.get(processing_type, thresholds["optimized"])
        
        # Validar thresholds
        if metrics.execution_time > threshold["max_execution_time"]:
            logger.warning(f"Tempo de execução alto: {metrics.execution_time:.2f}s > {threshold['max_execution_time']}s")
        
        if metrics.throughput < threshold["min_throughput"]:
            logger.warning(f"Throughput baixo: {metrics.throughput:.2f} < {threshold['min_throughput']}")
        
        if metrics.memory_usage > threshold["max_memory"]:
            logger.warning(f"Uso de memória alto: {metrics.memory_usage:.2f}MB > {threshold['max_memory']}MB")
        
        if metrics.cpu_usage > threshold["max_cpu"]:
            logger.warning(f"Uso de CPU alto: {metrics.cpu_usage:.2f}% > {threshold['max_cpu']}%")
    
    def _generate_performance_report(self):
        """Gerar relatório de performance"""
        if not self.metrics:
            return
        
        # Calcular estatísticas
        execution_times = [m.execution_time for m in self.metrics]
        throughputs = [m.throughput for m in self.metrics if m.throughput > 0]
        memory_usages = [m.memory_usage for m in self.metrics]
        cpu_usages = [m.cpu_usage for m in self.metrics]
        
        total_success = sum(m.success_count for m in self.metrics)
        total_errors = sum(m.error_count for m in self.metrics)
        
        report = {
            "test_name": "Processing Speed Load Test",
            "timestamp": datetime.now().isoformat(),
            "total_operations": len(self.metrics),
            "total_keywords_processed": total_success,
            "total_errors": total_errors,
            "success_rate": (total_success / (total_success + total_errors)) * 100 if (total_success + total_errors) > 0 else 0,
            "performance_metrics": {
                "execution_time": {
                    "mean": statistics.mean(execution_times) if execution_times else 0,
                    "median": statistics.median(execution_times) if execution_times else 0,
                    "min": min(execution_times) if execution_times else 0,
                    "max": max(execution_times) if execution_times else 0,
                    "p95": statistics.quantiles(execution_times, n=20)[18] if len(execution_times) >= 20 else max(execution_times) if execution_times else 0
                },
                "throughput": {
                    "mean": statistics.mean(throughputs) if throughputs else 0,
                    "median": statistics.median(throughputs) if throughputs else 0,
                    "min": min(throughputs) if throughputs else 0,
                    "max": max(throughputs) if throughputs else 0
                },
                "memory_usage": {
                    "mean": statistics.mean(memory_usages) if memory_usages else 0,
                    "max": max(memory_usages) if memory_usages else 0
                },
                "cpu_usage": {
                    "mean": statistics.mean(cpu_usages) if cpu_usages else 0,
                    "max": max(cpu_usages) if cpu_usages else 0
                }
            },
            "test_config": self.test_config
        }
        
        # Salvar relatório
        try:
            with open(f"test-results/processing_speed_report_{int(time.time())}.json", "w") as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Relatório de performance salvo: processing_speed_report_{int(time.time())}.json")
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {str(e)}")

# Event listeners para métricas globais
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Evento de início do teste"""
    logger.info("Teste de velocidade de processamento iniciado")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Evento de fim do teste"""
    logger.info("Teste de velocidade de processamento finalizado") 