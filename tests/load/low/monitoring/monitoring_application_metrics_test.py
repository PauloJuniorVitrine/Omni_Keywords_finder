#!/usr/bin/env python3
"""
Teste de Métricas da Aplicação
Omni Keywords Finder - Tracing ID: MONITORING_APPLICATION_METRICS_20250127_001

Este teste valida as métricas da aplicação sob carga:
- Tempo de resposta
- Throughput
- Taxa de erro
- Métricas de negócio
- Performance de endpoints
- Métricas customizadas

Baseado em:
- backend/app/middleware/metrics_middleware.py
- backend/app/services/metrics_service.py
- backend/app/api/metrics.py

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
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np


@dataclass
class ApplicationMetricScenario:
    """Cenário de teste de métricas da aplicação"""
    name: str
    description: str
    metric_type: str  # 'response_time', 'throughput', 'error_rate', 'business', 'custom'
    duration_minutes: int
    load_pattern: str  # 'constant', 'burst', 'variable', 'stress'
    expected_behavior: str
    threshold_value: float


class MonitoringApplicationMetricsTest:
    """
    Teste de métricas da aplicação sob carga
    """
    
    def __init__(self, host: str = "http://localhost:8000", verbose: bool = False):
        self.host = host
        self.verbose = verbose
        self.tracing_id = "MONITORING_APPLICATION_METRICS_20250127_001"
        self.start_time = datetime.now()
        
        # Configurar logging
        self.setup_logging()
        
        # Inicializar monitor de métricas da aplicação
        self.app_metrics_monitor = ApplicationMetricsMonitor()
        
        # Cenários de métricas da aplicação
        self.application_metric_scenarios = [
            ApplicationMetricScenario(
                name="Tempo de Resposta",
                description="Monitoramento de tempo de resposta dos endpoints",
                metric_type="response_time",
                duration_minutes=25,
                load_pattern="variable",
                expected_behavior="Detecção de latência alta",
                threshold_value=2000.0  # 2 segundos
            ),
            ApplicationMetricScenario(
                name="Throughput",
                description="Monitoramento de requisições por segundo",
                metric_type="throughput",
                duration_minutes=30,
                load_pattern="burst",
                expected_behavior="Detecção de picos de throughput",
                threshold_value=100.0  # 100 req/s
            ),
            ApplicationMetricScenario(
                name="Taxa de Erro",
                description="Monitoramento de erros da aplicação",
                metric_type="error_rate",
                duration_minutes=20,
                load_pattern="stress",
                expected_behavior="Detecção de aumento de erros",
                threshold_value=5.0  # 5%
            ),
            ApplicationMetricScenario(
                name="Métricas de Negócio",
                description="Monitoramento de métricas de negócio",
                metric_type="business",
                duration_minutes=35,
                load_pattern="constant",
                expected_behavior="Validação de métricas de negócio",
                threshold_value=95.0  # 95% de sucesso
            ),
            ApplicationMetricScenario(
                name="Métricas Customizadas",
                description="Monitoramento de métricas customizadas",
                metric_type="custom",
                duration_minutes=40,
                load_pattern="variable",
                expected_behavior="Validação de métricas customizadas",
                threshold_value=80.0  # 80% de eficiência
            )
        ]
        
        # Endpoints para teste de métricas
        self.metric_endpoints = [
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
            'thresholds_exceeded': 0,
            'performance_issues': 0,
            'avg_metric_accuracy': 0.0
        }
        
    def setup_logging(self):
        """Configura logging estruturado"""
        logging.basicConfig(
            level=logging.INFO if self.verbose else logging.WARNING,
            format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
            handlers=[
                logging.FileHandler(f'logs/monitoring_application_metrics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(f"MonitoringApplicationMetricsTest_{self.tracing_id}")
        
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
    
    def test_application_metric_scenario(self, scenario: ApplicationMetricScenario) -> Dict[str, Any]:
        """Testa um cenário específico de métricas da aplicação"""
        self.log(f"Iniciando teste: {scenario.name} ({scenario.duration_minutes}min)")
        
        results = {
            'scenario_name': scenario.name,
            'metric_type': scenario.metric_type,
            'load_pattern': scenario.load_pattern,
            'start_time': datetime.now().isoformat(),
            'application_metrics': [],
            'performance_events': [],
            'threshold_events': [],
            'analysis': {},
            'summary': {}
        }
        
        try:
            # Iniciar monitoramento
            self.app_metrics_monitor.start_monitoring(scenario.metric_type)
            
            # Executar cenário
            scenario_result = self.execute_application_metric_scenario(scenario)
            
            # Parar monitoramento
            self.app_metrics_monitor.stop_monitoring()
            
            # Analisar resultados
            results['application_metrics'] = self.app_metrics_monitor.get_metrics()
            results['performance_events'] = self.detect_performance_events(results['application_metrics'], scenario)
            results['threshold_events'] = self.detect_threshold_events(results['application_metrics'], scenario)
            results['analysis'] = self.analyze_application_metrics(results['application_metrics'], scenario)
            results['summary'] = self.analyze_metric_results(scenario_result, results['application_metrics'], scenario)
            results['end_time'] = datetime.now().isoformat()
            
        except Exception as e:
            error_msg = f"Erro durante teste {scenario.name}: {str(e)}"
            self.log(error_msg, "ERROR")
            results['error'] = error_msg
            
        return results
    
    def execute_application_metric_scenario(self, scenario: ApplicationMetricScenario) -> Dict[str, Any]:
        """Executa o cenário de métricas da aplicação"""
        start_time = time.time()
        end_time = start_time + (scenario.duration_minutes * 60)
        
        scenario_result = {
            'requests_made': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_response_time': 0.0,
            'request_events': []
        }
        
        self.log(f"Executando cenário por {scenario.duration_minutes} minutos")
        
        try:
            with ThreadPoolExecutor(max_workers=self.get_concurrent_workers(scenario.load_pattern)) as executor:
                futures = []
                
                while time.time() < end_time:
                    # Calcular intensidade da carga
                    load_intensity = self.calculate_load_intensity(scenario.load_pattern, time.time() - start_time)
                    
                    # Submeter requisições
                    for _ in range(self.get_request_count(scenario.load_pattern)):
                        future = executor.submit(
                            self.make_metric_request,
                            scenario,
                            load_intensity
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
                            
                            # Registrar evento de requisição
                            request_event = {
                                'timestamp': datetime.now().isoformat(),
                                'endpoint': result['endpoint'],
                                'response_time': result['response_time'],
                                'status_code': result['status_code'],
                                'success': result['success'],
                                'load_intensity': load_intensity
                            }
                            scenario_result['request_events'].append(request_event)
                            
                        except Exception as e:
                            self.log(f"Erro na requisição de métrica: {str(e)}", "ERROR")
                            scenario_result['failed_requests'] += 1
                    
                    # Limpar futures processados
                    futures = [f for f in futures if not f.done()]
                    
                    # Aguardar baseado no padrão de carga
                    wait_time = self.calculate_wait_time(scenario.load_pattern)
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
            scenario_result['error_rate'] = scenario_result['failed_requests'] / scenario_result['requests_made'] * 100
        
        return scenario_result
    
    def get_concurrent_workers(self, load_pattern: str) -> int:
        """Retorna número de workers baseado no padrão de carga"""
        if load_pattern == "constant":
            return 10
        elif load_pattern == "burst":
            return 25
        elif load_pattern == "variable":
            return 15
        elif load_pattern == "stress":
            return 40
        else:
            return 10
    
    def get_request_count(self, load_pattern: str) -> int:
        """Retorna número de requisições baseado no padrão de carga"""
        if load_pattern == "constant":
            return 5
        elif load_pattern == "burst":
            return 15
        elif load_pattern == "variable":
            return 8
        elif load_pattern == "stress":
            return 20
        else:
            return 5
    
    def calculate_load_intensity(self, load_pattern: str, elapsed_time: float) -> float:
        """Calcula intensidade da carga baseada no padrão"""
        if load_pattern == "constant":
            return 0.7
        
        elif load_pattern == "burst":
            # Picos a cada 2 minutos
            burst_cycle = 120
            if (elapsed_time % burst_cycle) < 30:  # 30 segundos de pico
                return 1.0
            else:
                return 0.3
        
        elif load_pattern == "variable":
            # Variação baseada em função seno
            variation = np.sin(elapsed_time / 180) * 0.4 + 0.6  # Variação de 0.2 a 1.0
            return variation
        
        elif load_pattern == "stress":
            # Stress crescente
            return min(0.3 + (elapsed_time / 600), 1.0)  # Cresce até 1.0 em 10 minutos
        
        return 0.5
    
    def calculate_wait_time(self, load_pattern: str) -> float:
        """Calcula tempo de espera baseado no padrão de carga"""
        if load_pattern == "constant":
            return 3.0
        elif load_pattern == "burst":
            return 1.0
        elif load_pattern == "variable":
            return 2.0
        elif load_pattern == "stress":
            return 0.5
        else:
            return 3.0
    
    def make_metric_request(self, scenario: ApplicationMetricScenario, load_intensity: float) -> Dict[str, Any]:
        """Faz uma requisição para teste de métricas"""
        start_time = time.time()
        
        try:
            # Selecionar endpoint baseado no tipo de métrica
            endpoint = self.select_metric_endpoint(scenario.metric_type, load_intensity)
            
            # Gerar payload específico para métricas
            payload = self.generate_metric_payload(scenario, load_intensity)
            
            # Fazer requisição
            response = requests.post(
                f"{self.host}{endpoint}",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response_time': response_time * 1000,  # Converter para ms
                'endpoint': endpoint,
                'load_intensity': load_intensity,
                'payload_size': len(json.dumps(payload))
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                'success': False,
                'error': str(e),
                'response_time': (end_time - start_time) * 1000,
                'endpoint': 'unknown',
                'load_intensity': load_intensity
            }
    
    def select_metric_endpoint(self, metric_type: str, load_intensity: float) -> str:
        """Seleciona endpoint baseado no tipo de métrica"""
        if metric_type == "response_time":
            if load_intensity > 0.8:
                return random.choice(["/api/reports/generate", "/api/executions/create"])
            else:
                return random.choice(["/api/users/profile", "/api/categories/list"])
        
        elif metric_type == "throughput":
            return random.choice(["/api/v1/analytics/advanced", "/api/metrics/performance"])
        
        elif metric_type == "error_rate":
            # Endpoints que podem gerar erros
            return random.choice(["/api/reports/generate", "/api/executions/create"])
        
        elif metric_type == "business":
            return random.choice(["/api/business-metrics", "/api/v1/analytics/advanced"])
        
        elif metric_type == "custom":
            return random.choice(["/api/metrics/performance", "/api/audit/logs"])
        
        else:
            return random.choice(self.metric_endpoints)
    
    def generate_metric_payload(self, scenario: ApplicationMetricScenario, load_intensity: float) -> Dict[str, Any]:
        """Gera payload específico para teste de métricas"""
        base_payload = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "application_metrics",
            "scenario": scenario.name,
            "load_intensity": load_intensity
        }
        
        if scenario.metric_type == "response_time":
            base_payload.update({
                "data": {
                    "response_time_test": {
                        "complexity": "high" if load_intensity > 0.7 else "medium",
                        "data_size": int(load_intensity * 10000)
                    }
                }
            })
        
        elif scenario.metric_type == "throughput":
            base_payload.update({
                "data": {
                    "throughput_test": {
                        "request_count": int(load_intensity * 100),
                        "concurrent_operations": int(load_intensity * 10)
                    }
                }
            })
        
        elif scenario.metric_type == "error_rate":
            base_payload.update({
                "data": {
                    "error_rate_test": {
                        "force_errors": load_intensity > 0.8,
                        "invalid_data": load_intensity > 0.6
                    }
                }
            })
        
        elif scenario.metric_type == "business":
            base_payload.update({
                "data": {
                    "business_metrics": {
                        "analytics_period": "daily",
                        "include_trends": True,
                        "metrics_type": ["revenue", "users", "performance"]
                    }
                }
            })
        
        elif scenario.metric_type == "custom":
            base_payload.update({
                "data": {
                    "custom_metrics": {
                        "metric_name": "efficiency_score",
                        "calculation_type": "weighted_average",
                        "parameters": {"weight": load_intensity}
                    }
                }
            })
        
        return base_payload
    
    def detect_performance_events(self, metrics: List[Dict], scenario: ApplicationMetricScenario) -> List[Dict]:
        """Detecta eventos de performance"""
        performance_events = []
        
        for metric in metrics:
            metric_value = metric.get(scenario.metric_type, 0)
            
            # Detectar problemas de performance baseado no tipo
            if scenario.metric_type == "response_time" and metric_value > scenario.threshold_value:
                performance_events.append({
                    'timestamp': metric['timestamp'],
                    'event_type': 'high_latency',
                    'value': metric_value,
                    'threshold': scenario.threshold_value,
                    'severity': 'high' if metric_value > scenario.threshold_value * 1.5 else 'medium'
                })
            
            elif scenario.metric_type == "throughput" and metric_value > scenario.threshold_value:
                performance_events.append({
                    'timestamp': metric['timestamp'],
                    'event_type': 'high_throughput',
                    'value': metric_value,
                    'threshold': scenario.threshold_value,
                    'severity': 'high' if metric_value > scenario.threshold_value * 1.2 else 'medium'
                })
            
            elif scenario.metric_type == "error_rate" and metric_value > scenario.threshold_value:
                performance_events.append({
                    'timestamp': metric['timestamp'],
                    'event_type': 'high_error_rate',
                    'value': metric_value,
                    'threshold': scenario.threshold_value,
                    'severity': 'critical' if metric_value > scenario.threshold_value * 2 else 'high'
                })
        
        return performance_events
    
    def detect_threshold_events(self, metrics: List[Dict], scenario: ApplicationMetricScenario) -> List[Dict]:
        """Detecta eventos de threshold excedido"""
        threshold_events = []
        
        for metric in metrics:
            metric_value = metric.get(scenario.metric_type, 0)
            
            # Lógica específica por tipo de métrica
            if scenario.metric_type == "response_time":
                if metric_value > scenario.threshold_value:
                    threshold_events.append({
                        'timestamp': metric['timestamp'],
                        'metric_type': scenario.metric_type,
                        'value': metric_value,
                        'threshold': scenario.threshold_value,
                        'exceeded_by': metric_value - scenario.threshold_value
                    })
            
            elif scenario.metric_type == "throughput":
                if metric_value > scenario.threshold_value:
                    threshold_events.append({
                        'timestamp': metric['timestamp'],
                        'metric_type': scenario.metric_type,
                        'value': metric_value,
                        'threshold': scenario.threshold_value,
                        'exceeded_by': metric_value - scenario.threshold_value
                    })
            
            elif scenario.metric_type == "error_rate":
                if metric_value > scenario.threshold_value:
                    threshold_events.append({
                        'timestamp': metric['timestamp'],
                        'metric_type': scenario.metric_type,
                        'value': metric_value,
                        'threshold': scenario.threshold_value,
                        'exceeded_by': metric_value - scenario.threshold_value
                    })
            
            elif scenario.metric_type == "business":
                if metric_value < scenario.threshold_value:  # Para métricas de negócio, menor é pior
                    threshold_events.append({
                        'timestamp': metric['timestamp'],
                        'metric_type': scenario.metric_type,
                        'value': metric_value,
                        'threshold': scenario.threshold_value,
                        'exceeded_by': scenario.threshold_value - metric_value
                    })
            
            elif scenario.metric_type == "custom":
                if metric_value < scenario.threshold_value:
                    threshold_events.append({
                        'timestamp': metric['timestamp'],
                        'metric_type': scenario.metric_type,
                        'value': metric_value,
                        'threshold': scenario.threshold_value,
                        'exceeded_by': scenario.threshold_value - metric_value
                    })
        
        return threshold_events
    
    def analyze_application_metrics(self, metrics: List[Dict], scenario: ApplicationMetricScenario) -> Dict[str, Any]:
        """Analisa as métricas da aplicação"""
        if not metrics:
            return {'analysis': 'no_data'}
        
        metric_values = [m.get(scenario.metric_type, 0) for m in metrics]
        
        # Estatísticas básicas
        mean_value = np.mean(metric_values)
        max_value = max(metric_values)
        min_value = min(metric_values)
        std_value = np.std(metric_values)
        
        # Análise de tendência
        if len(metric_values) > 1:
            trend = self.calculate_metric_trend(metric_values)
        else:
            trend = "insufficient_data"
        
        # Análise de percentis
        percentiles = {
            'p50': np.percentile(metric_values, 50),
            'p90': np.percentile(metric_values, 90),
            'p95': np.percentile(metric_values, 95),
            'p99': np.percentile(metric_values, 99)
        }
        
        # Análise de estabilidade
        stability_score = 1.0 - (std_value / mean_value) if mean_value > 0 else 0
        
        return {
            'mean_value': mean_value,
            'max_value': max_value,
            'min_value': min_value,
            'std_value': std_value,
            'trend': trend,
            'percentiles': percentiles,
            'stability_score': stability_score,
            'threshold_exceeded_count': sum(1 for v in metric_values if v > scenario.threshold_value),
            'threshold_exceeded_rate': sum(1 for v in metric_values if v > scenario.threshold_value) / len(metric_values)
        }
    
    def calculate_metric_trend(self, values: List[float]) -> str:
        """Calcula tendência das métricas"""
        if len(values) < 2:
            return "insufficient_data"
        
        # Regressão linear simples
        x = list(range(len(values)))
        slope = np.polyfit(x, values, 1)[0]
        
        if abs(slope) < 0.1:
            return "stable"
        elif slope > 0.1:
            return "increasing"
        else:
            return "decreasing"
    
    def analyze_metric_results(self, scenario_result: Dict, metrics: List[Dict], scenario: ApplicationMetricScenario) -> Dict[str, Any]:
        """Analisa os resultados do teste de métricas"""
        total_requests = scenario_result['requests_made']
        successful_requests = scenario_result['successful_requests']
        
        # Análise de métricas
        if metrics:
            metric_values = [m.get(scenario.metric_type, 0) for m in metrics]
            avg_metric = np.mean(metric_values)
            max_metric = max(metric_values)
            threshold_exceeded_count = sum(1 for v in metric_values if v > scenario.threshold_value)
        else:
            avg_metric = 0
            max_metric = 0
            threshold_exceeded_count = 0
        
        return {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'success_rate': successful_requests / total_requests if total_requests > 0 else 0,
            'avg_response_time': scenario_result.get('avg_response_time', 0),
            'error_rate': scenario_result.get('error_rate', 0),
            'avg_metric_value': avg_metric,
            'max_metric_value': max_metric,
            'threshold_exceeded_count': threshold_exceeded_count,
            'threshold_exceeded_rate': threshold_exceeded_count / len(metrics) if metrics else 0,
            'measurements_count': len(metrics),
            'duration_minutes': scenario.duration_minutes
        }
    
    def run(self) -> Dict[str, Any]:
        """Executa todos os testes de métricas da aplicação"""
        self.log("🚀 Iniciando testes de métricas da aplicação")
        
        all_results = {
            'tracing_id': self.tracing_id,
            'start_time': self.start_time.isoformat(),
            'host': self.host,
            'scenarios': [],
            'summary': {},
            'application_analysis': {}
        }
        
        try:
            # Executar cenários
            for i, scenario in enumerate(self.application_metric_scenarios):
                self.log(f"Executando cenário {i+1}/{len(self.application_metric_scenarios)}: {scenario.name}")
                
                scenario_result = self.test_application_metric_scenario(scenario)
                scenario_result['scenario_index'] = i + 1
                
                all_results['scenarios'].append(scenario_result)
                
                # Atualizar métricas
                self.metrics['scenarios_executed'] += 1
                if scenario_result.get('summary', {}).get('threshold_exceeded_count', 0) > 0:
                    self.metrics['thresholds_exceeded'] += 1
                
                # Pausa entre cenários
                if i < len(self.application_metric_scenarios) - 1:
                    time.sleep(10)
            
            # Gerar resumo geral
            all_results['summary'] = self.generate_overall_summary(all_results)
            all_results['application_analysis'] = self.analyze_overall_application_metrics(all_results)
            all_results['end_time'] = datetime.now().isoformat()
            
            # Calcular sucesso geral
            total_scenarios = len(all_results['scenarios'])
            successful_scenarios = sum(1 for s in all_results['scenarios'] 
                                     if not s.get('error'))
            success_rate = successful_scenarios / total_scenarios if total_scenarios > 0 else 0
            
            all_results['success'] = success_rate >= 0.8
            
            self.log(f"✅ Testes de métricas da aplicação concluídos: {success_rate:.1%} de sucesso")
            
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
        thresholds_exceeded = sum(1 for s in scenarios 
                                if s.get('summary', {}).get('threshold_exceeded_count', 0) > 0)
        
        # Análise por tipo de métrica
        metric_analysis = {}
        for scenario in scenarios:
            metric_type = scenario.get('metric_type', 'unknown')
            if metric_type not in metric_analysis:
                metric_analysis[metric_type] = {
                    'count': 0,
                    'thresholds_exceeded': 0,
                    'avg_value': 0.0
                }
            
            metric_analysis[metric_type]['count'] += 1
            summary = scenario.get('summary', {})
            if summary.get('threshold_exceeded_count', 0) > 0:
                metric_analysis[metric_type]['thresholds_exceeded'] += 1
            metric_analysis[metric_type]['avg_value'] += summary.get('avg_metric_value', 0)
        
        # Calcular médias
        for metric_type in metric_analysis:
            count = metric_analysis[metric_type]['count']
            if count > 0:
                metric_analysis[metric_type]['avg_value'] /= count
        
        return {
            'total_scenarios': total_scenarios,
            'thresholds_exceeded': thresholds_exceeded,
            'exceeded_rate': thresholds_exceeded / total_scenarios if total_scenarios > 0 else 0,
            'metric_analysis': metric_analysis
        }
    
    def analyze_overall_application_metrics(self, all_results: Dict) -> Dict[str, Any]:
        """Analisa métricas gerais da aplicação"""
        all_metrics = []
        for scenario in all_results['scenarios']:
            all_metrics.extend(scenario.get('application_metrics', []))
        
        if not all_metrics:
            return {}
        
        # Análise geral
        response_times = [m.get('response_time', 0) for m in all_metrics]
        throughput_values = [m.get('throughput', 0) for m in all_metrics]
        error_rates = [m.get('error_rate', 0) for m in all_metrics]
        
        return {
            'total_measurements': len(all_metrics),
            'avg_response_time_ms': np.mean(response_times) if response_times else 0,
            'avg_throughput_rps': np.mean(throughput_values) if throughput_values else 0,
            'avg_error_rate_percent': np.mean(error_rates) if error_rates else 0,
            'max_response_time_ms': max(response_times) if response_times else 0,
            'max_throughput_rps': max(throughput_values) if throughput_values else 0,
            'max_error_rate_percent': max(error_rates) if error_rates else 0
        }


class ApplicationMetricsMonitor:
    """Monitor de métricas da aplicação"""
    
    def __init__(self):
        self.metrics = []
        self.monitoring = False
        self.monitor_thread = None
        self.metric_type = None
        
    def start_monitoring(self, metric_type: str):
        """Inicia o monitoramento de métricas"""
        self.metrics = []
        self.monitoring = True
        self.metric_type = metric_type
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Para o monitoramento de métricas"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
    
    def _monitor_loop(self):
        """Loop de monitoramento"""
        while self.monitoring:
            try:
                # Simular coleta de métricas da aplicação
                # Em um ambiente real, isso viria do sistema de métricas
                
                if self.metric_type == "response_time":
                    # Simular tempo de resposta
                    response_time = np.random.normal(500, 200)  # ms
                    measurement = {
                        'timestamp': datetime.now(),
                        'response_time': max(0, response_time)
                    }
                
                elif self.metric_type == "throughput":
                    # Simular throughput
                    throughput = np.random.normal(50, 20)  # req/s
                    measurement = {
                        'timestamp': datetime.now(),
                        'throughput': max(0, throughput)
                    }
                
                elif self.metric_type == "error_rate":
                    # Simular taxa de erro
                    error_rate = np.random.normal(2, 1)  # %
                    measurement = {
                        'timestamp': datetime.now(),
                        'error_rate': max(0, min(100, error_rate))
                    }
                
                elif self.metric_type == "business":
                    # Simular métricas de negócio
                    business_score = np.random.normal(90, 5)  # %
                    measurement = {
                        'timestamp': datetime.now(),
                        'business': max(0, min(100, business_score))
                    }
                
                elif self.metric_type == "custom":
                    # Simular métricas customizadas
                    custom_metric = np.random.normal(85, 10)  # %
                    measurement = {
                        'timestamp': datetime.now(),
                        'custom': max(0, min(100, custom_metric))
                    }
                
                else:
                    measurement = {
                        'timestamp': datetime.now(),
                        'unknown': 0
                    }
                
                self.metrics.append(measurement)
                
                # Aguardar 10 segundos
                time.sleep(10)
                
            except Exception as e:
                logging.error(f"Erro no monitoramento de métricas da aplicação: {e}")
                time.sleep(10)
    
    def get_metrics(self) -> List[Dict]:
        """Retorna as métricas coletadas"""
        return self.metrics.copy()


def main():
    """Função principal para execução standalone"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Teste de Métricas da Aplicação")
    parser.add_argument('--host', default='http://localhost:8000', help='Host para testar')
    parser.add_argument('--verbose', action='store_true', help='Modo verboso')
    
    args = parser.parse_args()
    
    # Criar e executar teste
    test = MonitoringApplicationMetricsTest(host=args.host, verbose=args.verbose)
    result = test.run()
    
    # Imprimir resultados
    print("\n" + "="*80)
    print("📊 RESULTADOS DOS TESTES DE MÉTRICAS DA APLICAÇÃO")
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
        print(f"   • Thresholds Excedidos: {summary['thresholds_exceeded']}")
        print(f"   • Taxa de Excesso: {summary['exceeded_rate']:.1%}")
    
    if 'application_analysis' in result:
        analysis = result['application_analysis']
        print(f"\n📱 ANÁLISE DA APLICAÇÃO:")
        print(f"   • Total de Medições: {analysis['total_measurements']}")
        print(f"   • Tempo de Resposta Médio: {analysis['avg_response_time_ms']:.1f} ms")
        print(f"   • Throughput Médio: {analysis['avg_throughput_rps']:.1f} req/s")
        print(f"   • Taxa de Erro Média: {analysis['avg_error_rate_percent']:.1f}%")
        print(f"   • Tempo de Resposta Máximo: {analysis['max_response_time_ms']:.1f} ms")
    
    print("="*80)


if __name__ == "__main__":
    main() 