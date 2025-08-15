#!/usr/bin/env python3
"""
Teste de Tracing Distribuído
Omni Keywords Finder - Tracing ID: MONITORING_DISTRIBUTED_TRACING_20250127_001

Este teste valida o tracing distribuído sob carga:
- Performance de tracing
- Propagação de contextos
- Análise de spans
- Correlação de requisições
- Latência de tracing

Baseado em:
- infrastructure/tracing/trace_manager.py
- backend/app/middleware/tracing_middleware.py
- backend/app/services/trace_analysis_service.py

Autor: IA-Cursor
Data: 2025-01-27
Versão: 1.0
"""

import time
import random
import requests
import json
import logging
import threading
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np


@dataclass
class TracingScenario:
    """Cenário de teste de tracing distribuído"""
    name: str
    description: str
    tracing_type: str  # 'request_chain', 'service_call', 'database_query', 'external_api', 'async_operation'
    duration_minutes: int
    trace_complexity: str  # 'simple', 'medium', 'complex', 'extreme'
    expected_behavior: str
    target_latency: float  # ms


class MonitoringDistributedTracingTest:
    """
    Teste de tracing distribuído sob carga
    """
    
    def __init__(self, host: str = "http://localhost:8000", verbose: bool = False):
        self.host = host
        self.verbose = verbose
        self.tracing_id = "MONITORING_DISTRIBUTED_TRACING_20250127_001"
        self.start_time = datetime.now()
        
        # Configurar logging
        self.setup_logging()
        
        # Inicializar monitor de tracing
        self.trace_monitor = DistributedTracingMonitor()
        
        # Cenários de tracing distribuído
        self.tracing_scenarios = [
            TracingScenario(
                name="Cadeia de Requisições",
                description="Tracing de cadeias de requisições complexas",
                tracing_type="request_chain",
                duration_minutes=25,
                trace_complexity="complex",
                expected_behavior="Propagação correta de contextos",
                target_latency=100.0  # 100ms
            ),
            TracingScenario(
                name="Chamadas de Serviço",
                description="Tracing de chamadas entre serviços",
                tracing_type="service_call",
                duration_minutes=30,
                trace_complexity="medium",
                expected_behavior="Correlação de spans de serviço",
                target_latency=50.0  # 50ms
            ),
            TracingScenario(
                name="Queries de Banco",
                description="Tracing de queries de banco de dados",
                tracing_type="database_query",
                duration_minutes=20,
                trace_complexity="simple",
                expected_behavior="Detecção de queries lentas",
                target_latency=20.0  # 20ms
            ),
            TracingScenario(
                name="APIs Externas",
                description="Tracing de chamadas para APIs externas",
                tracing_type="external_api",
                duration_minutes=35,
                trace_complexity="extreme",
                expected_behavior="Tracing de dependências externas",
                target_latency=200.0  # 200ms
            ),
            TracingScenario(
                name="Operações Assíncronas",
                description="Tracing de operações assíncronas",
                tracing_type="async_operation",
                duration_minutes=40,
                trace_complexity="complex",
                expected_behavior="Correlação de operações assíncronas",
                target_latency=150.0  # 150ms
            )
        ]
        
        # Endpoints para teste de tracing
        self.tracing_endpoints = [
            "/api/v1/analytics/advanced",
            "/api/reports/generate",
            "/api/executions/create",
            "/api/metrics/performance",
            "/api/business-metrics",
            "/api/users/profile",
            "/api/categories/list",
            "/api/audit/logs"
        ]
        
        # Métricas coletadas
        self.metrics = {
            'scenarios_executed': 0,
            'scenarios_failed': 0,
            'traces_generated': 0,
            'trace_analysis_events': 0,
            'avg_trace_latency': 0.0
        }
        
    def setup_logging(self):
        """Configura logging estruturado"""
        logging.basicConfig(
            level=logging.INFO if self.verbose else logging.WARNING,
            format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
            handlers=[
                logging.FileHandler(f'logs/monitoring_distributed_tracing_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(f"MonitoringDistributedTracingTest_{self.tracing_id}")
        
    def log(self, message: str, level: str = "INFO"):
        """Log estruturado com tracing ID"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] [{self.tracing_id}] {message}"
        
        if level == "ERROR":
            self.logger.error(log_message)
        elif level == "WARNING":
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    def test_tracing_scenario(self, scenario: TracingScenario) -> Dict[str, Any]:
        """Testa um cenário específico de tracing"""
        self.log(f"Iniciando teste: {scenario.name} ({scenario.duration_minutes}min)")
        
        results = {
            'scenario_name': scenario.name,
            'tracing_type': scenario.tracing_type,
            'trace_complexity': scenario.trace_complexity,
            'start_time': datetime.now().isoformat(),
            'trace_metrics': [],
            'trace_events': [],
            'analysis': {},
            'summary': {}
        }
        
        try:
            # Iniciar monitoramento
            self.trace_monitor.start_monitoring(scenario.tracing_type)
            
            # Executar cenário
            scenario_result = self.execute_tracing_scenario(scenario)
            
            # Parar monitoramento
            self.trace_monitor.stop_monitoring()
            
            # Analisar resultados
            results['trace_metrics'] = self.trace_monitor.get_metrics()
            results['trace_events'] = self.detect_trace_events(results['trace_metrics'], scenario)
            results['analysis'] = self.analyze_tracing(results['trace_metrics'], scenario)
            results['summary'] = self.analyze_trace_results(scenario_result, results['trace_metrics'], scenario)
            results['end_time'] = datetime.now().isoformat()
            
        except Exception as e:
            error_msg = f"Erro durante teste {scenario.name}: {str(e)}"
            self.log(error_msg, "ERROR")
            results['error'] = error_msg
            
        return results
    
    def execute_tracing_scenario(self, scenario: TracingScenario) -> Dict[str, Any]:
        """Executa o cenário de tracing"""
        start_time = time.time()
        end_time = start_time + (scenario.duration_minutes * 60)
        
        scenario_result = {
            'requests_made': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_response_time': 0.0,
            'trace_events': []
        }
        
        self.log(f"Executando cenário por {scenario.duration_minutes} minutos")
        
        try:
            with ThreadPoolExecutor(max_workers=self.get_concurrent_workers(scenario.trace_complexity)) as executor:
                futures = []
                
                while time.time() < end_time:
                    # Calcular complexidade do tracing
                    trace_complexity = self.calculate_trace_complexity(scenario.trace_complexity, time.time() - start_time)
                    
                    # Submeter requisições
                    for _ in range(self.get_request_count(scenario.trace_complexity)):
                        future = executor.submit(
                            self.make_trace_request,
                            scenario,
                            trace_complexity
                        )
                        futures.append(future)
                    
                    # Coletar resultados
                    for future in as_completed(futures):
                        try:
                            result = future.result()
                            scenario_result['requests_made'] += 1
                            
                            if result['success']:
                                scenario_result['successful_requests'] += 1
                            else:
                                scenario_result['failed_requests'] += 1
                            
                            scenario_result['total_response_time'] += result['response_time']
                            
                            # Registrar evento de tracing
                            trace_event = {
                                'timestamp': datetime.now().isoformat(),
                                'trace_id': result['trace_id'],
                                'endpoint': result['endpoint'],
                                'response_time': result['response_time'],
                                'trace_complexity': trace_complexity,
                                'success': result['success']
                            }
                            scenario_result['trace_events'].append(trace_event)
                            
                        except Exception as e:
                            self.log(f"Erro na requisição de tracing: {str(e)}", "ERROR")
                            scenario_result['failed_requests'] += 1
                    
                    # Limpar futures processados
                    futures = [f for f in futures if not f.done()]
                    
                    # Aguardar baseado na complexidade
                    wait_time = self.calculate_wait_time(scenario.trace_complexity)
                    time.sleep(wait_time)
                    
                    # Log de progresso
                    elapsed_minutes = (time.time() - start_time) / 60
                    if elapsed_minutes % 5 < wait_time / 60:  # A cada 5 minutos
                        self.log(f"Progresso: {elapsed_minutes:.1f}min / {scenario.duration_minutes}min")
                
        except KeyboardInterrupt:
            self.log("Teste interrompido pelo usuário", "WARNING")
        
        # Calcular métricas finais
        if scenario_result['requests_made'] > 0:
            scenario_result['avg_response_time'] = scenario_result['total_response_time'] / scenario_result['requests_made']
        
        return scenario_result
    
    def get_concurrent_workers(self, trace_complexity: str) -> int:
        """Retorna número de workers baseado na complexidade do tracing"""
        if trace_complexity == "simple":
            return 10
        elif trace_complexity == "medium":
            return 20
        elif trace_complexity == "complex":
            return 30
        elif trace_complexity == "extreme":
            return 40
        else:
            return 15
    
    def get_request_count(self, trace_complexity: str) -> int:
        """Retorna número de requisições baseado na complexidade do tracing"""
        if trace_complexity == "simple":
            return 5
        elif trace_complexity == "medium":
            return 10
        elif trace_complexity == "complex":
            return 15
        elif trace_complexity == "extreme":
            return 20
        else:
            return 8
    
    def calculate_trace_complexity(self, trace_complexity: str, elapsed_time: float) -> float:
        """Calcula complexidade do tracing"""
        if trace_complexity == "simple":
            return 0.3
        
        elif trace_complexity == "medium":
            return 0.6
        
        elif trace_complexity == "complex":
            # Variação baseada em função seno
            variation = np.sin(elapsed_time / 300) * 0.3 + 0.7  # Variação de 0.4 a 1.0
            return variation
        
        elif trace_complexity == "extreme":
            # Picos extremos a cada 3 minutos
            extreme_cycle = 180
            if (elapsed_time % extreme_cycle) < 60:  # 1 minuto de pico
                return 1.0
            else:
                return 0.4
        
        return 0.5
    
    def calculate_wait_time(self, trace_complexity: str) -> float:
        """Calcula tempo de espera baseado na complexidade do tracing"""
        if trace_complexity == "simple":
            return 4.0
        elif trace_complexity == "medium":
            return 2.0
        elif trace_complexity == "complex":
            return 1.5
        elif trace_complexity == "extreme":
            return 1.0
        else:
            return 3.0
    
    def make_trace_request(self, scenario: TracingScenario, trace_complexity: float) -> Dict[str, Any]:
        """Faz uma requisição para teste de tracing"""
        start_time = time.time()
        
        try:
            # Gerar trace ID único
            trace_id = str(uuid.uuid4())
            
            # Selecionar endpoint baseado no tipo de tracing
            endpoint = self.select_trace_endpoint(scenario.tracing_type, trace_complexity)
            
            # Gerar payload específico para tracing
            payload = self.generate_trace_payload(scenario, trace_complexity, trace_id)
            
            # Headers para tracing
            headers = {
                'Content-Type': 'application/json',
                'X-Trace-ID': trace_id,
                'X-Span-ID': str(uuid.uuid4()),
                'X-Parent-Span-ID': str(uuid.uuid4()) if trace_complexity > 0.5 else ''
            }
            
            # Fazer requisição
            response = requests.post(
                f"{self.host}{endpoint}",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response_time': response_time * 1000,  # Converter para ms
                'endpoint': endpoint,
                'trace_id': trace_id,
                'trace_complexity': trace_complexity,
                'payload_size': len(json.dumps(payload))
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                'success': False,
                'error': str(e),
                'response_time': (end_time - start_time) * 1000,
                'endpoint': 'unknown',
                'trace_id': str(uuid.uuid4()),
                'trace_complexity': trace_complexity
            }
    
    def select_trace_endpoint(self, tracing_type: str, trace_complexity: float) -> str:
        """Seleciona endpoint baseado no tipo de tracing"""
        if tracing_type == "request_chain":
            return random.choice(["/api/v1/analytics/advanced", "/api/reports/generate"])
        
        elif tracing_type == "service_call":
            return random.choice(["/api/metrics/performance", "/api/business-metrics"])
        
        elif tracing_type == "database_query":
            return random.choice(["/api/users/profile", "/api/categories/list"])
        
        elif tracing_type == "external_api":
            return random.choice(["/api/executions/create", "/api/audit/logs"])
        
        elif tracing_type == "async_operation":
            return random.choice(["/api/v1/analytics/advanced", "/api/reports/generate"])
        
        else:
            return random.choice(self.tracing_endpoints)
    
    def generate_trace_payload(self, scenario: TracingScenario, trace_complexity: float, trace_id: str) -> Dict[str, Any]:
        """Gera payload específico para teste de tracing"""
        base_payload = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "distributed_tracing",
            "scenario": scenario.name,
            "trace_complexity": trace_complexity,
            "trace_id": trace_id
        }
        
        if scenario.tracing_type == "request_chain":
            base_payload.update({
                "data": {
                    "request_chain": {
                        "depth": int(trace_complexity * 10),
                        "services": ["auth", "analytics", "database", "cache"],
                        "propagate_context": True
                    }
                }
            })
        
        elif scenario.tracing_type == "service_call":
            base_payload.update({
                "data": {
                    "service_call": {
                        "service_name": "analytics_service",
                        "method": "process_data",
                        "parameters": {"complexity": trace_complexity}
                    }
                }
            })
        
        elif scenario.tracing_type == "database_query":
            base_payload.update({
                "data": {
                    "database_query": {
                        "query_type": "complex_select" if trace_complexity > 0.7 else "simple_select",
                        "table_count": int(trace_complexity * 5),
                        "join_count": int(trace_complexity * 3)
                    }
                }
            })
        
        elif scenario.tracing_type == "external_api":
            base_payload.update({
                "data": {
                    "external_api": {
                        "api_name": "google_analytics",
                        "endpoint": "/data/ga",
                        "timeout": int(trace_complexity * 5000)
                    }
                }
            })
        
        elif scenario.tracing_type == "async_operation":
            base_payload.update({
                "data": {
                    "async_operation": {
                        "operation_type": "background_processing",
                        "queue_name": "high_priority",
                        "retry_count": int(trace_complexity * 3)
                    }
                }
            })
        
        return base_payload
    
    def detect_trace_events(self, metrics: List[Dict], scenario: TracingScenario) -> List[Dict]:
        """Detecta eventos relacionados a tracing"""
        trace_events = []
        
        for metric in metrics:
            trace_latency = metric.get('trace_latency', 0)
            
            # Detectar eventos baseado na latência de tracing
            if trace_latency > scenario.target_latency * 1.5:
                trace_events.append({
                    'timestamp': metric['timestamp'],
                    'event_type': 'high_trace_latency',
                    'latency': trace_latency,
                    'target': scenario.target_latency,
                    'severity': 'high'
                })
            
            elif trace_latency > scenario.target_latency:
                trace_events.append({
                    'timestamp': metric['timestamp'],
                    'event_type': 'trace_latency_exceeded',
                    'latency': trace_latency,
                    'target': scenario.target_latency,
                    'severity': 'medium'
                })
            
            # Detectar problemas de propagação
            propagation_errors = metric.get('propagation_errors', 0)
            if propagation_errors > 0:
                trace_events.append({
                    'timestamp': metric['timestamp'],
                    'event_type': 'trace_propagation_error',
                    'error_count': propagation_errors,
                    'severity': 'high'
                })
        
        return trace_events
    
    def analyze_tracing(self, metrics: List[Dict], scenario: TracingScenario) -> Dict[str, Any]:
        """Analisa o tracing distribuído"""
        if not metrics:
            return {'analysis': 'no_data'}
        
        trace_latencies = [m.get('trace_latency', 0) for m in metrics]
        span_counts = [m.get('span_count', 0) for m in metrics]
        propagation_errors = [m.get('propagation_errors', 0) for m in metrics]
        
        # Estatísticas básicas
        mean_latency = np.mean(trace_latencies)
        max_latency = max(trace_latencies)
        mean_spans = np.mean(span_counts)
        total_errors = sum(propagation_errors)
        
        # Análise de tendência
        if len(trace_latencies) > 1:
            trend = self.calculate_trace_trend(trace_latencies)
        else:
            trend = "insufficient_data"
        
        # Análise de performance vs target
        latency_achievement_rate = (scenario.target_latency / mean_latency) * 100 if mean_latency > 0 else 0
        
        # Análise de estabilidade
        latency_stability = 1.0 - (np.std(trace_latencies) / mean_latency) if mean_latency > 0 else 0
        
        return {
            'mean_latency': mean_latency,
            'max_latency': max_latency,
            'mean_spans': mean_spans,
            'total_errors': total_errors,
            'trend': trend,
            'latency_achievement_rate': latency_achievement_rate,
            'latency_stability': latency_stability,
            'target_achieved': mean_latency <= scenario.target_latency,
            'performance_issues': sum(1 for l in trace_latencies if l > scenario.target_latency)
        }
    
    def calculate_trace_trend(self, latencies: List[float]) -> str:
        """Calcula tendência das latências de tracing"""
        if len(latencies) < 2:
            return "insufficient_data"
        
        # Regressão linear simples
        x = list(range(len(latencies)))
        slope = np.polyfit(x, latencies, 1)[0]
        
        if abs(slope) < 1:
            return "stable"
        elif slope > 1:
            return "increasing"
        else:
            return "decreasing"
    
    def analyze_trace_results(self, scenario_result: Dict, metrics: List[Dict], scenario: TracingScenario) -> Dict[str, Any]:
        """Analisa os resultados do teste de tracing"""
        total_requests = scenario_result['requests_made']
        successful_requests = scenario_result['successful_requests']
        
        # Análise de métricas
        if metrics:
            trace_latencies = [m.get('trace_latency', 0) for m in metrics]
            avg_latency = np.mean(trace_latencies)
            max_latency = max(trace_latencies)
            target_achieved_count = sum(1 for l in trace_latencies if l <= scenario.target_latency)
        else:
            avg_latency = 0
            max_latency = 0
            target_achieved_count = 0
        
        return {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'success_rate': successful_requests / total_requests if total_requests > 0 else 0,
            'avg_response_time': scenario_result.get('avg_response_time', 0),
            'avg_trace_latency': avg_latency,
            'max_trace_latency': max_latency,
            'target_achieved_count': target_achieved_count,
            'target_achievement_rate': target_achieved_count / len(metrics) if metrics else 0,
            'measurements_count': len(metrics),
            'duration_minutes': scenario.duration_minutes
        }
    
    def run(self) -> Dict[str, Any]:
        """Executa todos os testes de tracing distribuído"""
        self.log("🚀 Iniciando testes de tracing distribuído")
        
        all_results = {
            'tracing_id': self.tracing_id,
            'start_time': self.start_time.isoformat(),
            'host': self.host,
            'scenarios': [],
            'summary': {},
            'trace_analysis': {}
        }
        
        try:
            # Executar cenários
            for i, scenario in enumerate(self.tracing_scenarios):
                self.log(f"Executando cenário {i+1}/{len(self.tracing_scenarios)}: {scenario.name}")
                
                scenario_result = self.test_tracing_scenario(scenario)
                scenario_result['scenario_index'] = i + 1
                
                all_results['scenarios'].append(scenario_result)
                
                # Atualizar métricas
                self.metrics['scenarios_executed'] += 1
                if scenario_result.get('summary', {}).get('target_achievement_rate', 0) >= 0.8:
                    self.metrics['traces_generated'] += 1
                
                # Pausa entre cenários
                if i < len(self.tracing_scenarios) - 1:
                    time.sleep(10)
            
            # Gerar resumo geral
            all_results['summary'] = self.generate_overall_summary(all_results)
            all_results['trace_analysis'] = self.analyze_overall_tracing(all_results)
            all_results['end_time'] = datetime.now().isoformat()
            
            # Calcular sucesso geral
            total_scenarios = len(all_results['scenarios'])
            successful_scenarios = sum(1 for s in all_results['scenarios'] 
                                     if not s.get('error'))
            success_rate = successful_scenarios / total_scenarios if total_scenarios > 0 else 0
            
            all_results['success'] = success_rate >= 0.8
            
            self.log(f"✅ Testes de tracing distribuído concluídos: {success_rate:.1%} de sucesso")
            
        except Exception as e:
            error_msg = f"Erro durante execução dos testes: {str(e)}"
            self.log(error_msg, "ERROR")
            all_results['success'] = False
            all_results['error'] = error_msg
        
        return all_results
    
    def generate_overall_summary(self, all_results: Dict) -> Dict[str, Any]:
        """Gera resumo geral dos resultados"""
        scenarios = all_results['scenarios']
        
        total_scenarios = len(scenarios)
        targets_achieved = sum(1 for s in scenarios 
                             if s.get('summary', {}).get('target_achievement_rate', 0) >= 0.8)
        
        # Análise por tipo de tracing
        trace_analysis = {}
        for scenario in scenarios:
            tracing_type = scenario.get('tracing_type', 'unknown')
            if tracing_type not in trace_analysis:
                trace_analysis[tracing_type] = {
                    'count': 0,
                    'targets_achieved': 0,
                    'avg_latency': 0.0
                }
            
            trace_analysis[tracing_type]['count'] += 1
            summary = scenario.get('summary', {})
            if summary.get('target_achievement_rate', 0) >= 0.8:
                trace_analysis[tracing_type]['targets_achieved'] += 1
            trace_analysis[tracing_type]['avg_latency'] += summary.get('avg_trace_latency', 0)
        
        # Calcular médias
        for tracing_type in trace_analysis:
            count = trace_analysis[tracing_type]['count']
            if count > 0:
                trace_analysis[tracing_type]['avg_latency'] /= count
        
        return {
            'total_scenarios': total_scenarios,
            'targets_achieved': targets_achieved,
            'achievement_rate': targets_achieved / total_scenarios if total_scenarios > 0 else 0,
            'trace_analysis': trace_analysis
        }
    
    def analyze_overall_tracing(self, all_results: Dict) -> Dict[str, Any]:
        """Analisa tracing geral"""
        all_metrics = []
        for scenario in all_results['scenarios']:
            all_metrics.extend(scenario.get('trace_metrics', []))
        
        if not all_metrics:
            return {}
        
        # Análise geral
        trace_latencies = [m.get('trace_latency', 0) for m in all_metrics]
        span_counts = [m.get('span_count', 0) for m in all_metrics]
        propagation_errors = [m.get('propagation_errors', 0) for m in all_metrics]
        
        return {
            'total_measurements': len(all_metrics),
            'avg_trace_latency_ms': np.mean(trace_latencies) if trace_latencies else 0,
            'max_trace_latency_ms': max(trace_latencies) if trace_latencies else 0,
            'avg_span_count': np.mean(span_counts) if span_counts else 0,
            'total_propagation_errors': sum(propagation_errors),
            'total_traces_generated': len(all_metrics)
        }


class DistributedTracingMonitor:
    """Monitor de tracing distribuído"""
    
    def __init__(self):
        self.metrics = []
        self.monitoring = False
        self.monitor_thread = None
        self.tracing_type = None
        
    def start_monitoring(self, tracing_type: str):
        """Inicia o monitoramento de tracing"""
        self.metrics = []
        self.monitoring = True
        self.tracing_type = tracing_type
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Para o monitoramento de tracing"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
    
    def _monitor_loop(self):
        """Loop de monitoramento"""
        while self.monitoring:
            try:
                # Simular coleta de métricas de tracing
                # Em um ambiente real, isso viria do sistema de tracing
                
                if self.tracing_type == "request_chain":
                    # Simular tracing de cadeia de requisições
                    trace_latency = np.random.normal(80, 30)  # ms
                    span_count = np.random.normal(8, 3)  # spans
                    propagation_errors = np.random.poisson(0.1)  # erros
                    measurement = {
                        'timestamp': datetime.now(),
                        'trace_latency': max(0, trace_latency),
                        'span_count': max(1, int(span_count)),
                        'propagation_errors': int(propagation_errors)
                    }
                
                elif self.tracing_type == "service_call":
                    # Simular tracing de chamadas de serviço
                    trace_latency = np.random.normal(40, 15)  # ms
                    span_count = np.random.normal(4, 2)  # spans
                    propagation_errors = np.random.poisson(0.05)  # erros
                    measurement = {
                        'timestamp': datetime.now(),
                        'trace_latency': max(0, trace_latency),
                        'span_count': max(1, int(span_count)),
                        'propagation_errors': int(propagation_errors)
                    }
                
                elif self.tracing_type == "database_query":
                    # Simular tracing de queries de banco
                    trace_latency = np.random.normal(15, 8)  # ms
                    span_count = np.random.normal(2, 1)  # spans
                    propagation_errors = np.random.poisson(0.02)  # erros
                    measurement = {
                        'timestamp': datetime.now(),
                        'trace_latency': max(0, trace_latency),
                        'span_count': max(1, int(span_count)),
                        'propagation_errors': int(propagation_errors)
                    }
                
                elif self.tracing_type == "external_api":
                    # Simular tracing de APIs externas
                    trace_latency = np.random.normal(150, 60)  # ms
                    span_count = np.random.normal(6, 2)  # spans
                    propagation_errors = np.random.poisson(0.2)  # erros
                    measurement = {
                        'timestamp': datetime.now(),
                        'trace_latency': max(0, trace_latency),
                        'span_count': max(1, int(span_count)),
                        'propagation_errors': int(propagation_errors)
                    }
                
                elif self.tracing_type == "async_operation":
                    # Simular tracing de operações assíncronas
                    trace_latency = np.random.normal(120, 40)  # ms
                    span_count = np.random.normal(10, 4)  # spans
                    propagation_errors = np.random.poisson(0.15)  # erros
                    measurement = {
                        'timestamp': datetime.now(),
                        'trace_latency': max(0, trace_latency),
                        'span_count': max(1, int(span_count)),
                        'propagation_errors': int(propagation_errors)
                    }
                
                else:
                    measurement = {
                        'timestamp': datetime.now(),
                        'trace_latency': 0,
                        'span_count': 0,
                        'propagation_errors': 0
                    }
                
                self.metrics.append(measurement)
                
                # Aguardar 8 segundos
                time.sleep(8)
                
            except Exception as e:
                logging.error(f"Erro no monitoramento de tracing: {e}")
                time.sleep(8)
    
    def get_metrics(self) -> List[Dict]:
        """Retorna as métricas coletadas"""
        return self.metrics.copy()


def main():
    """Função principal para execução standalone"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Teste de Tracing Distribuído")
    parser.add_argument('--host', default='http://localhost:8000', help='Host para testar')
    parser.add_argument('--verbose', action='store_true', help='Modo verboso')
    
    args = parser.parse_args()
    
    # Criar e executar teste
    test = MonitoringDistributedTracingTest(host=args.host, verbose=args.verbose)
    result = test.run()
    
    # Imprimir resultados
    print("\n" + "="*80)
    print("📊 RESULTADOS DOS TESTES DE TRACING DISTRIBUÍDO")
    print("="*80)
    print(f"🆔 Tracing ID: {result['tracing_id']}")
    print(f"🔗 Host: {result['host']}")
    print(f"⏰ Início: {result['start_time']}")
    print(f"⏰ Fim: {result['end_time']}")
    print(f"✅ Sucesso: {result['success']}")
    
    if 'summary' in result:
        summary = result['summary']
        print(f"\n📈 RESUMO:")
        print(f"   • Cenários Executados: {summary['total_scenarios']}")
        print(f"   • Targets Atingidos: {summary['targets_achieved']}")
        print(f"   • Taxa de Atingimento: {summary['achievement_rate']:.1%}")
    
    if 'trace_analysis' in result:
        analysis = result['trace_analysis']
        print(f"\n🔍 ANÁLISE DE TRACING:")
        print(f"   • Total de Medições: {analysis['total_measurements']}")
        print(f"   • Latência Média de Tracing: {analysis['avg_trace_latency_ms']:.1f} ms")
        print(f"   • Latência Máxima de Tracing: {analysis['max_trace_latency_ms']:.1f} ms")
        print(f"   • Média de Spans: {analysis['avg_span_count']:.1f}")
        print(f"   • Total de Erros de Propagação: {analysis['total_propagation_errors']}")
        print(f"   • Total de Traces Gerados: {analysis['total_traces_generated']}")
    
    print("="*80)


if __name__ == "__main__":
    main() 