"""
⚡ Teste de Carga - Performance de Uso de Memória
🎯 Objetivo: Testar uso de memória em operações de processamento e cache
📅 Data: 2025-01-27
🔗 Tracing ID: LOAD_PERF_MEMORY_USAGE_001
📋 Ruleset: enterprise_control_layer.yaml

📐 CoCoT: Baseado em código real de gerenciamento de memória e cache
🌲 ToT: Avaliadas múltiplas estratégias de otimização de memória
♻️ ReAct: Simulado cenários de carga e validada gestão de memória

Testa endpoints baseados em:
- infrastructure/performance/memory_management.py
- infrastructure/cache/intelligent_cache.py
- infrastructure/processamento/parallel_processor.py
- backend/app/api/advanced_metrics.py
"""

import time
import json
import random
import psutil
import gc
import tracemalloc
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
class MemoryMetrics:
    """Métricas de uso de memória"""
    operation_name: str
    memory_before: float
    memory_after: float
    memory_peak: float
    memory_increase: float
    memory_percent: float
    gc_collections: int
    execution_time: float
    success_count: int
    error_count: int
    timestamp: datetime

class MemoryUsageLoadTest(HttpUser):
    """
    Teste de carga para uso de memória
    Baseado em endpoints reais de processamento e cache
    """
    
    wait_time = between(2, 5)
    
    def on_start(self):
        """Inicialização do teste"""
        self.metrics: List[MemoryMetrics] = []
        self.start_time = time.time()
        self.memory_peak = 0
        self.gc_collections_before = gc.get_count()
        
        # Configurações de teste baseadas em código real
        self.test_config = {
            'memory_thresholds': {
                'warning': 200.0,    # MB
                'critical': 500.0,   # MB
                'max_peak': 800.0    # MB
            },
            'cache_sizes': [100, 500, 1000, 2000],
            'batch_sizes': [50, 100, 200, 500],
            'operation_types': ['cache_operations', 'processing_operations', 'mixed_operations'],
            'gc_monitoring': True,
            'memory_profiling': True
        }
        
        # Iniciar profiling de memória
        if self.test_config['memory_profiling']:
            tracemalloc.start()
        
        logger.info(f"Teste de uso de memória iniciado - {self.test_config}")
    
    def on_stop(self):
        """Finalização do teste"""
        if self.test_config['memory_profiling']:
            tracemalloc.stop()
        self._generate_memory_report()
    
    @task(3)
    def test_cache_memory_usage(self):
        """Teste de uso de memória em operações de cache"""
        self._test_memory_usage("cache_operations", batch_size=100)
    
    @task(2)
    def test_processing_memory_usage(self):
        """Teste de uso de memória em processamento"""
        self._test_memory_usage("processing_operations", batch_size=200)
    
    @task(2)
    def test_mixed_memory_usage(self):
        """Teste de uso de memória em operações mistas"""
        self._test_memory_usage("mixed_operations", batch_size=150)
    
    @task(1)
    def test_large_batch_memory_usage(self):
        """Teste de uso de memória com lotes grandes"""
        self._test_memory_usage("large_batch", batch_size=500)
    
    @task(1)
    def test_memory_leak_detection(self):
        """Teste de detecção de vazamento de memória"""
        self._test_memory_leak_detection()
    
    def _test_memory_usage(self, operation_type: str, batch_size: int):
        """Teste de uso de memória"""
        # Coletar métricas iniciais
        memory_before = self._get_memory_usage()
        gc_collections_before = gc.get_count()
        start_time = time.time()
        
        try:
            # Forçar garbage collection antes do teste
            if self.test_config['gc_monitoring']:
                gc.collect()
            
            # Gerar dados de teste
            test_data = self._generate_test_data(batch_size, operation_type)
            
            # Preparar payload baseado em operação
            if operation_type == "cache_operations":
                payload = self._prepare_cache_payload(test_data)
                endpoint = "/api/cache/operations"
            elif operation_type == "processing_operations":
                payload = self._prepare_processing_payload(test_data)
                endpoint = "/api/processar_keywords"
            elif operation_type == "mixed_operations":
                payload = self._prepare_mixed_payload(test_data)
                endpoint = "/api/advanced_metrics"
            else:
                payload = self._prepare_large_batch_payload(test_data)
                endpoint = "/api/processar_keywords"
            
            # Executar requisição
            with self.client.post(
                endpoint,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Operation-Type": operation_type,
                    "X-Batch-Size": str(batch_size),
                    "X-Memory-Monitoring": "true"
                },
                catch_response=True,
                timeout=120
            ) as response:
                end_time = time.time()
                memory_after = self._get_memory_usage()
                gc_collections_after = gc.get_count()
                
                execution_time = end_time - start_time
                memory_increase = memory_after - memory_before
                memory_percent = (memory_after / psutil.virtual_memory().total) * 100
                gc_collections = sum(gc_collections_after) - sum(gc_collections_before)
                
                # Atualizar pico de memória
                if memory_after > self.memory_peak:
                    self.memory_peak = memory_after
                
                # Validar resposta
                if response.status_code == 200:
                    response_data = response.json()
                    
                    if self._validate_memory_response(response_data, operation_type):
                        # Registrar métricas de sucesso
                        metrics = MemoryMetrics(
                            operation_name=f"memory_usage_{operation_type}",
                            memory_before=memory_before,
                            memory_after=memory_after,
                            memory_peak=self.memory_peak,
                            memory_increase=memory_increase,
                            memory_percent=memory_percent,
                            gc_collections=gc_collections,
                            execution_time=execution_time,
                            success_count=batch_size,
                            error_count=0,
                            timestamp=datetime.now()
                        )
                        self.metrics.append(metrics)
                        
                        # Validar thresholds de memória
                        self._validate_memory_thresholds(metrics, operation_type)
                        
                        response.success()
                        logger.info(f"Operação {operation_type} bem-sucedida: {batch_size} itens, memória: {memory_increase:.2f}MB")
                    else:
                        response.failure("Resposta inválida")
                else:
                    response.failure(f"Status code: {response.status_code}")
                    
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            memory_after = self._get_memory_usage()
            
            metrics = MemoryMetrics(
                operation_name=f"memory_usage_{operation_type}_error",
                memory_before=memory_before,
                memory_after=memory_after,
                memory_peak=self.memory_peak,
                memory_increase=memory_after - memory_before,
                memory_percent=(memory_after / psutil.virtual_memory().total) * 100,
                gc_collections=0,
                execution_time=execution_time,
                success_count=0,
                error_count=batch_size,
                timestamp=datetime.now()
            )
            self.metrics.append(metrics)
            
            logger.error(f"Erro na operação {operation_type}: {str(e)}")
    
    def _test_memory_leak_detection(self):
        """Teste de detecção de vazamento de memória"""
        logger.info("Iniciando teste de detecção de vazamento de memória")
        
        # Executar operações repetitivas
        for i in range(10):
            memory_before = self._get_memory_usage()
            
            # Executar operação que pode causar vazamento
            self._execute_potential_memory_leak_operation()
            
            memory_after = self._get_memory_usage()
            memory_increase = memory_after - memory_before
            
            # Forçar garbage collection
            gc.collect()
            memory_after_gc = self._get_memory_usage()
            
            # Verificar se há vazamento
            if memory_after_gc > memory_before + 10:  # 10MB de tolerância
                logger.warning(f"Possível vazamento de memória detectado na iteração {i+1}: {memory_after_gc - memory_before:.2f}MB")
            
            time.sleep(1)
    
    def _get_memory_usage(self) -> float:
        """Obter uso de memória atual em MB"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            return memory_info.rss / (1024 * 1024)  # MB
        except Exception as e:
            logger.error(f"Erro ao obter uso de memória: {str(e)}")
            return 0.0
    
    def _generate_test_data(self, count: int, operation_type: str) -> List[Dict[str, Any]]:
        """Gerar dados de teste baseados no tipo de operação"""
        if operation_type == "cache_operations":
            return self._generate_cache_test_data(count)
        elif operation_type == "processing_operations":
            return self._generate_processing_test_data(count)
        elif operation_type == "mixed_operations":
            return self._generate_mixed_test_data(count)
        else:
            return self._generate_large_batch_test_data(count)
    
    def _generate_cache_test_data(self, count: int) -> List[Dict[str, Any]]:
        """Gerar dados de teste para cache"""
        cache_operations = []
        for i in range(count):
            operation = {
                "operation": random.choice(["get", "set", "delete", "update"]),
                "key": f"test_key_{i}_{random.randint(1000, 9999)}",
                "value": {
                    "data": f"test_value_{i}",
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {
                        "size": random.randint(100, 10000),
                        "type": random.choice(["string", "object", "array"]),
                        "compressed": random.choice([True, False])
                    }
                },
                "ttl": random.randint(60, 3600),
                "priority": random.choice(["low", "medium", "high"])
            }
            cache_operations.append(operation)
        return cache_operations
    
    def _generate_processing_test_data(self, count: int) -> List[Dict[str, Any]]:
        """Gerar dados de teste para processamento"""
        keywords = []
        for i in range(count):
            keyword = {
                "termo": f"keyword_test_{i}_{random.randint(1000, 9999)}",
                "volume_busca": random.randint(1000, 50000),
                "cpc": random.uniform(0.5, 10.0),
                "concorrencia": random.uniform(0.1, 1.0),
                "metadata": {
                    "language": random.choice(["pt-BR", "en-US", "es-ES"]),
                    "category": random.choice(["marketing", "technology", "health", "finance"]),
                    "complexity": random.choice(["low", "medium", "high"])
                }
            }
            keywords.append(keyword)
        return keywords
    
    def _generate_mixed_test_data(self, count: int) -> List[Dict[str, Any]]:
        """Gerar dados de teste mistos"""
        mixed_data = []
        for i in range(count):
            data_type = random.choice(["cache", "processing", "metrics"])
            
            if data_type == "cache":
                data = {
                    "type": "cache",
                    "operation": "set",
                    "key": f"mixed_key_{i}",
                    "value": {"data": f"mixed_value_{i}"}
                }
            elif data_type == "processing":
                data = {
                    "type": "processing",
                    "keyword": f"mixed_keyword_{i}",
                    "volume": random.randint(1000, 20000)
                }
            else:
                data = {
                    "type": "metrics",
                    "metric_name": f"mixed_metric_{i}",
                    "value": random.uniform(0, 100)
                }
            
            mixed_data.append(data)
        return mixed_data
    
    def _generate_large_batch_test_data(self, count: int) -> List[Dict[str, Any]]:
        """Gerar dados de teste para lotes grandes"""
        large_data = []
        for i in range(count):
            # Dados maiores para testar limites de memória
            data = {
                "id": f"large_batch_{i}",
                "content": "x" * random.randint(1000, 10000),  # Conteúdo grande
                "metadata": {
                    "size": random.randint(10000, 100000),
                    "complexity": "high",
                    "compression_ratio": random.uniform(0.1, 0.9)
                },
                "nested_data": {
                    "level1": {
                        "level2": {
                            "level3": [random.randint(1, 1000) for _ in range(100)]
                        }
                    }
                }
            }
            large_data.append(data)
        return large_data
    
    def _prepare_cache_payload(self, test_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Preparar payload para operações de cache"""
        return {
            "operations": test_data,
            "cache_config": {
                "enable_compression": True,
                "enable_eviction": True,
                "max_size": 1000,
                "ttl_default": 3600
            },
            "monitoring": {
                "track_memory": True,
                "track_hit_rate": True,
                "track_evictions": True
            }
        }
    
    def _prepare_processing_payload(self, test_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Preparar payload para processamento"""
        return {
            "keywords": test_data,
            "processing_config": {
                "enable_parallel": True,
                "enable_cache": True,
                "enable_compression": True,
                "batch_size": len(test_data),
                "memory_limit": 500  # MB
            },
            "optimization": {
                "level": "high",
                "memory_management": True,
                "gc_optimization": True
            }
        }
    
    def _prepare_mixed_payload(self, test_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Preparar payload para operações mistas"""
        return {
            "operations": test_data,
            "config": {
                "enable_memory_monitoring": True,
                "enable_gc_monitoring": True,
                "enable_performance_tracking": True
            },
            "metrics": {
                "memory_usage": True,
                "cache_performance": True,
                "processing_speed": True
            }
        }
    
    def _prepare_large_batch_payload(self, test_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Preparar payload para lotes grandes"""
        return {
            "data": test_data,
            "batch_config": {
                "size": len(test_data),
                "memory_limit": 1000,  # MB
                "enable_streaming": True,
                "enable_compression": True
            },
            "monitoring": {
                "memory_tracking": True,
                "gc_monitoring": True,
                "performance_tracking": True
            }
        }
    
    def _validate_memory_response(self, response_data: Dict[str, Any], operation_type: str) -> bool:
        """Validar resposta considerando uso de memória"""
        try:
            if not isinstance(response_data, dict):
                return False
            
            # Validações específicas por tipo de operação
            if operation_type == "cache_operations":
                return "cache_stats" in response_data or "operations" in response_data
            elif operation_type == "processing_operations":
                return "keywords" in response_data or "results" in response_data
            elif operation_type == "mixed_operations":
                return "metrics" in response_data or "summary" in response_data
            else:
                return "data" in response_data or "results" in response_data
            
        except Exception as e:
            logger.error(f"Erro na validação da resposta: {str(e)}")
            return False
    
    def _validate_memory_thresholds(self, metrics: MemoryMetrics, operation_type: str):
        """Validar thresholds de memória"""
        thresholds = self.test_config['memory_thresholds']
        
        # Validar aumento de memória
        if metrics.memory_increase > thresholds['warning']:
            logger.warning(f"Aumento de memória alto: {metrics.memory_increase:.2f}MB > {thresholds['warning']}MB")
        
        if metrics.memory_increase > thresholds['critical']:
            logger.error(f"Aumento de memória crítico: {metrics.memory_increase:.2f}MB > {thresholds['critical']}MB")
        
        # Validar pico de memória
        if metrics.memory_peak > thresholds['max_peak']:
            logger.error(f"Pico de memória muito alto: {metrics.memory_peak:.2f}MB > {thresholds['max_peak']}MB")
        
        # Validar percentual de memória
        if metrics.memory_percent > 80:
            logger.warning(f"Uso de memória alto: {metrics.memory_percent:.2f}%")
    
    def _execute_potential_memory_leak_operation(self):
        """Executar operação que pode causar vazamento de memória"""
        try:
            # Simular operação que pode causar vazamento
            large_data = []
            for i in range(1000):
                large_data.append({
                    "id": i,
                    "data": "x" * 1000,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Fazer requisição que pode não liberar memória adequadamente
            self.client.post(
                "/api/processar_keywords",
                json={"keywords": large_data},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
        except Exception as e:
            logger.debug(f"Operação de vazamento simulada: {str(e)}")
    
    def _generate_memory_report(self):
        """Gerar relatório de uso de memória"""
        if not self.metrics:
            return
        
        # Calcular estatísticas
        memory_increases = [m.memory_increase for m in self.metrics]
        memory_peaks = [m.memory_peak for m in self.metrics]
        memory_percents = [m.memory_percent for m in self.metrics]
        execution_times = [m.execution_time for m in self.metrics]
        
        total_success = sum(m.success_count for m in self.metrics)
        total_errors = sum(m.error_count for m in self.metrics)
        
        # Análise de vazamento de memória
        memory_trend = self._analyze_memory_trend()
        
        report = {
            "test_name": "Memory Usage Load Test",
            "timestamp": datetime.now().isoformat(),
            "total_operations": len(self.metrics),
            "total_items_processed": total_success,
            "total_errors": total_errors,
            "success_rate": (total_success / (total_success + total_errors)) * 100 if (total_success + total_errors) > 0 else 0,
            "memory_metrics": {
                "memory_increase": {
                    "mean": statistics.mean(memory_increases) if memory_increases else 0,
                    "median": statistics.median(memory_increases) if memory_increases else 0,
                    "min": min(memory_increases) if memory_increases else 0,
                    "max": max(memory_increases) if memory_increases else 0,
                    "p95": statistics.quantiles(memory_increases, n=20)[18] if len(memory_increases) >= 20 else max(memory_increases) if memory_increases else 0
                },
                "memory_peak": {
                    "mean": statistics.mean(memory_peaks) if memory_peaks else 0,
                    "max": max(memory_peaks) if memory_peaks else 0
                },
                "memory_percent": {
                    "mean": statistics.mean(memory_percents) if memory_percents else 0,
                    "max": max(memory_percents) if memory_percents else 0
                }
            },
            "performance_metrics": {
                "execution_time": {
                    "mean": statistics.mean(execution_times) if execution_times else 0,
                    "max": max(execution_times) if execution_times else 0
                }
            },
            "memory_leak_analysis": memory_trend,
            "test_config": self.test_config
        }
        
        # Salvar relatório
        try:
            with open(f"test-results/memory_usage_report_{int(time.time())}.json", "w") as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Relatório de uso de memória salvo: memory_usage_report_{int(time.time())}.json")
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {str(e)}")
    
    def _analyze_memory_trend(self) -> Dict[str, Any]:
        """Analisar tendência de uso de memória para detectar vazamentos"""
        if len(self.metrics) < 5:
            return {"insufficient_data": True}
        
        # Calcular tendência linear
        x_values = list(range(len(self.metrics)))
        y_values = [m.memory_after for m in self.metrics]
        
        try:
            # Calcular correlação
            correlation = statistics.correlation(x_values, y_values) if len(x_values) > 1 else 0
            
            # Calcular slope (tendência)
            if len(x_values) > 1:
                slope = (y_values[-1] - y_values[0]) / (x_values[-1] - x_values[0])
            else:
                slope = 0
            
            # Determinar se há vazamento
            memory_leak_detected = correlation > 0.7 and slope > 1.0  # Aumento consistente > 1MB por operação
            
            return {
                "correlation": correlation,
                "slope": slope,
                "memory_leak_detected": memory_leak_detected,
                "trend_strength": "strong" if abs(correlation) > 0.8 else "moderate" if abs(correlation) > 0.5 else "weak",
                "recommendation": "Investigar vazamento de memória" if memory_leak_detected else "Uso de memória estável"
            }
            
        except Exception as e:
            return {"error": str(e)}

# Event listeners para métricas globais
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Evento de início do teste"""
    logger.info("Teste de uso de memória iniciado")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Evento de fim do teste"""
    logger.info("Teste de uso de memória finalizado") 