#!/usr/bin/env python3
"""
Teste de Métricas do Sistema
Omni Keywords Finder - Tracing ID: MONITORING_SYSTEM_METRICS_20250127_001

Este teste valida as métricas do sistema sob carga:
- CPU, Memória, Disco, Rede
- Métricas de processo
- Métricas de sistema operacional
- Alertas e thresholds
- Coleta e armazenamento de métricas

Baseado em:
- infrastructure/monitoring/system_metrics.py
- backend/app/middleware/metrics_middleware.py
- backend/app/services/metrics_service.py

Autor: IA-Cursor
Data: 2025-01-27
Versão: 1.0
"""

import time
import random
import requests
import json
import logging
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np


@dataclass
class SystemMetricScenario:
    """Cenário de teste de métricas do sistema"""
    name: str
    description: str
    metric_type: str  # 'cpu', 'memory', 'disk', 'network', 'process'
    duration_minutes: int
    load_intensity: str  # 'low', 'medium', 'high', 'extreme'
    expected_behavior: str
    threshold_value: float


class MonitoringSystemMetricsTest:
    """
    Teste de métricas do sistema sob carga
    """
    
    def __init__(self, host: str = "http://localhost:8000", verbose: bool = False):
        self.host = host
        self.verbose = verbose
        self.tracing_id = "MONITORING_SYSTEM_METRICS_20250127_001"
        self.start_time = datetime.now()
        
        # Configurar logging
        self.setup_logging()
        
        # Inicializar monitor de métricas
        self.metrics_monitor = SystemMetricsMonitor()
        
        # Cenários de métricas do sistema
        self.system_metric_scenarios = [
            SystemMetricScenario(
                name="Métricas de CPU",
                description="Monitoramento de uso de CPU sob carga",
                metric_type="cpu",
                duration_minutes=30,
                load_intensity="high",
                expected_behavior="Detecção de picos de CPU",
                threshold_value=80.0
            ),
            SystemMetricScenario(
                name="Métricas de Memória",
                description="Monitoramento de uso de memória",
                metric_type="memory",
                duration_minutes=30,
                load_intensity="high",
                expected_behavior="Detecção de crescimento de memória",
                threshold_value=85.0
            ),
            SystemMetricScenario(
                name="Métricas de Disco",
                description="Monitoramento de I/O de disco",
                metric_type="disk",
                duration_minutes=20,
                load_intensity="medium",
                expected_behavior="Detecção de alta atividade de disco",
                threshold_value=70.0
            ),
            SystemMetricScenario(
                name="Métricas de Rede",
                description="Monitoramento de tráfego de rede",
                metric_type="network",
                duration_minutes=25,
                load_intensity="high",
                expected_behavior="Detecção de alto tráfego de rede",
                threshold_value=75.0
            ),
            SystemMetricScenario(
                name="Métricas de Processo",
                description="Monitoramento de recursos do processo",
                metric_type="process",
                duration_minutes=35,
                load_intensity="extreme",
                expected_behavior="Detecção de anomalias no processo",
                threshold_value=90.0
            )
        ]
        
        # Endpoints para gerar carga
        self.load_endpoints = [
            "/api/v1/analytics/advanced",
            "/api/reports/generate",
            "/api/executions/create",
            "/api/metrics/performance",
            "/api/audit/logs"
        ]
        
        # Métricas coletadas
        self.metrics = {
            'scenarios_executed': 0,
            'scenarios_failed': 0,
            'thresholds_exceeded': 0,
            'alerts_generated': 0,
            'avg_metric_accuracy': 0.0
        }
        
    def setup_logging(self):
        """Configura logging estruturado"""
        logging.basicConfig(
            level=logging.INFO if self.verbose else logging.WARNING,
            format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
            handlers=[
                logging.FileHandler(f'logs/monitoring_system_metrics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(f"MonitoringSystemMetricsTest_{self.tracing_id}")
        
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
    
    def test_system_metric_scenario(self, scenario: SystemMetricScenario) -> Dict[str, Any]:
        """Testa um cenário específico de métricas do sistema"""
        self.log(f"Iniciando teste: {scenario.name} ({scenario.duration_minutes}min)")
        
        results = {
            'scenario_name': scenario.name,
            'metric_type': scenario.metric_type,
            'load_intensity': scenario.load_intensity,
            'start_time': datetime.now().isoformat(),
            'system_metrics': [],
            'threshold_events': [],
            'alert_events': [],
            'analysis': {},
            'summary': {}
        }
        
        try:
            # Iniciar monitoramento
            self.metrics_monitor.start_monitoring(scenario.metric_type)
            
            # Executar cenário
            scenario_result = self.execute_system_metric_scenario(scenario)
            
            # Parar monitoramento
            self.metrics_monitor.stop_monitoring()
            
            # Analisar resultados
            results['system_metrics'] = self.metrics_monitor.get_metrics()
            results['threshold_events'] = self.detect_threshold_events(results['system_metrics'], scenario)
            results['alert_events'] = self.generate_alert_events(results['threshold_events'], scenario)
            results['analysis'] = self.analyze_system_metrics(results['system_metrics'], scenario)
            results['summary'] = self.analyze_metric_results(scenario_result, results['system_metrics'], scenario)
            results['end_time'] = datetime.now().isoformat()
            
        except Exception as e:
            error_msg = f"Erro durante teste {scenario.name}: {str(e)}"
            self.log(error_msg, "ERROR")
            results['error'] = error_msg
            
        return results
    
    def execute_system_metric_scenario(self, scenario: SystemMetricScenario) -> Dict[str, Any]:
        """Executa o cenário de métricas do sistema"""
        start_time = time.time()
        end_time = start_time + (scenario.duration_minutes * 60)
        
        scenario_result = {
            'requests_made': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_response_time': 0.0,
            'load_events': []
        }
        
        self.log(f"Executando cenário por {scenario.duration_minutes} minutos")
        
        try:
            with ThreadPoolExecutor(max_workers=self.get_concurrent_workers(scenario.load_intensity)) as executor:
                futures = []
                
                while time.time() < end_time:
                    # Gerar carga baseada na intensidade
                    load_intensity = self.calculate_load_intensity(scenario.load_intensity, time.time() - start_time)
                    
                    # Submeter requisições
                    for _ in range(self.get_request_count(scenario.load_intensity)):
                        future = executor.submit(
                            self.make_load_request,
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
                            
                            # Registrar evento de carga
                            load_event = {
                                'timestamp': datetime.now().isoformat(),
                                'load_intensity': load_intensity,
                                'response_time': result['response_time'],
                                'success': result['success']
                            }
                            scenario_result['load_events'].append(load_event)
                            
                        except Exception as e:
                            self.log(f"Erro na requisição de carga: {str(e)}", "ERROR")
                            scenario_result['failed_requests'] += 1
                    
                    # Limpar futures processados
                    futures = [f for f in futures if not f.done()]
                    
                    # Aguardar baseado na intensidade
                    wait_time = self.calculate_wait_time(scenario.load_intensity)
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
    
    def get_concurrent_workers(self, load_intensity: str) -> int:
        """Retorna número de workers baseado na intensidade"""
        if load_intensity == "low":
            return 5
        elif load_intensity == "medium":
            return 15
        elif load_intensity == "high":
            return 30
        elif load_intensity == "extreme":
            return 50
        else:
            return 10
    
    def get_request_count(self, load_intensity: str) -> int:
        """Retorna número de requisições baseado na intensidade"""
        if load_intensity == "low":
            return 3
        elif load_intensity == "medium":
            return 8
        elif load_intensity == "high":
            return 15
        elif load_intensity == "extreme":
            return 25
        else:
            return 5
    
    def calculate_load_intensity(self, load_intensity: str, elapsed_time: float) -> float:
        """Calcula intensidade da carga baseada no tempo"""
        base_intensity = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.8,
            "extreme": 1.0
        }.get(load_intensity, 0.5)
        
        # Variação temporal
        variation = np.sin(elapsed_time / 300) * 0.2 + 1  # Variação de ±20%
        return min(base_intensity * variation, 1.0)
    
    def calculate_wait_time(self, load_intensity: str) -> float:
        """Calcula tempo de espera baseado na intensidade"""
        if load_intensity == "low":
            return 5.0
        elif load_intensity == "medium":
            return 2.0
        elif load_intensity == "high":
            return 1.0
        elif load_intensity == "extreme":
            return 0.5
        else:
            return 3.0
    
    def make_load_request(self, scenario: SystemMetricScenario, load_intensity: float) -> Dict[str, Any]:
        """Faz uma requisição para gerar carga"""
        start_time = time.time()
        
        try:
            # Selecionar endpoint baseado na intensidade
            endpoint = self.select_load_endpoint(load_intensity)
            
            # Gerar payload baseado no tipo de métrica
            payload = self.generate_metric_load_payload(scenario, load_intensity)
            
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
                'response_time': response_time,
                'endpoint': endpoint,
                'load_intensity': load_intensity
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                'success': False,
                'error': str(e),
                'response_time': end_time - start_time,
                'endpoint': 'unknown',
                'load_intensity': load_intensity
            }
    
    def select_load_endpoint(self, load_intensity: float) -> str:
        """Seleciona endpoint baseado na intensidade da carga"""
        if load_intensity > 0.8:
            return random.choice(["/api/reports/generate", "/api/executions/create"])
        elif load_intensity > 0.5:
            return random.choice(["/api/v1/analytics/advanced", "/api/metrics/performance"])
        else:
            return random.choice(["/api/audit/logs", "/api/users/profile"])
    
    def generate_metric_load_payload(self, scenario: SystemMetricScenario, load_intensity: float) -> Dict[str, Any]:
        """Gera payload específico para teste de métricas"""
        base_payload = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "system_metrics",
            "scenario": scenario.name,
            "load_intensity": load_intensity
        }
        
        if scenario.metric_type == "cpu":
            base_payload.update({
                "data": {
                    "cpu_intensive": {
                        "iterations": int(load_intensity * 10000),
                        "complexity": "high"
                    }
                }
            })
        elif scenario.metric_type == "memory":
            base_payload.update({
                "data": {
                    "memory_intensive": {
                        "array_size": int(load_intensity * 100000),
                        "object_count": int(load_intensity * 1000)
                    }
                }
            })
        elif scenario.metric_type == "disk":
            base_payload.update({
                "data": {
                    "disk_intensive": {
                        "file_operations": int(load_intensity * 100),
                        "data_size": int(load_intensity * 10000)
                    }
                }
            })
        elif scenario.metric_type == "network":
            base_payload.update({
                "data": {
                    "network_intensive": {
                        "request_count": int(load_intensity * 50),
                        "data_transfer": int(load_intensity * 1000000)
                    }
                }
            })
        elif scenario.metric_type == "process":
            base_payload.update({
                "data": {
                    "process_intensive": {
                        "threads": int(load_intensity * 10),
                        "memory_allocation": int(load_intensity * 100000)
                    }
                }
            })
        
        return base_payload
    
    def detect_threshold_events(self, metrics: List[Dict], scenario: SystemMetricScenario) -> List[Dict]:
        """Detecta eventos de threshold excedido"""
        threshold_events = []
        
        for metric in metrics:
            metric_value = metric.get(scenario.metric_type, 0)
            if metric_value > scenario.threshold_value:
                threshold_event = {
                    'timestamp': metric['timestamp'],
                    'metric_type': scenario.metric_type,
                    'value': metric_value,
                    'threshold': scenario.threshold_value,
                    'exceeded_by': metric_value - scenario.threshold_value
                }
                threshold_events.append(threshold_event)
        
        return threshold_events
    
    def generate_alert_events(self, threshold_events: List[Dict], scenario: SystemMetricScenario) -> List[Dict]:
        """Gera eventos de alerta baseados nos thresholds"""
        alert_events = []
        
        for event in threshold_events:
            alert_event = {
                'timestamp': event['timestamp'],
                'alert_type': f"{scenario.metric_type}_threshold_exceeded",
                'severity': self.calculate_alert_severity(event['exceeded_by']),
                'message': f"Threshold de {scenario.metric_type} excedido: {event['value']:.1f} > {event['threshold']:.1f}",
                'metric_value': event['value'],
                'threshold_value': event['threshold']
            }
            alert_events.append(alert_event)
        
        return alert_events
    
    def calculate_alert_severity(self, exceeded_by: float) -> str:
        """Calcula severidade do alerta"""
        if exceeded_by > 50:
            return "critical"
        elif exceeded_by > 20:
            return "high"
        elif exceeded_by > 10:
            return "medium"
        else:
            return "low"
    
    def analyze_system_metrics(self, metrics: List[Dict], scenario: SystemMetricScenario) -> Dict[str, Any]:
        """Analisa as métricas do sistema"""
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
        
        # Análise de picos
        peaks = self.detect_metric_peaks(metric_values, scenario.threshold_value)
        
        return {
            'mean_value': mean_value,
            'max_value': max_value,
            'min_value': min_value,
            'std_value': std_value,
            'trend': trend,
            'peak_count': len(peaks),
            'threshold_exceeded_count': sum(1 for v in metric_values if v > scenario.threshold_value),
            'stability_score': 1.0 - (std_value / mean_value) if mean_value > 0 else 0
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
    
    def detect_metric_peaks(self, values: List[float], threshold: float) -> List[int]:
        """Detecta picos nas métricas"""
        peaks = []
        
        for i in range(1, len(values) - 1):
            if values[i] > threshold and values[i] > values[i-1] and values[i] > values[i+1]:
                peaks.append(i)
        
        return peaks
    
    def analyze_metric_results(self, scenario_result: Dict, metrics: List[Dict], scenario: SystemMetricScenario) -> Dict[str, Any]:
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
            'avg_metric_value': avg_metric,
            'max_metric_value': max_metric,
            'threshold_exceeded_count': threshold_exceeded_count,
            'threshold_exceeded_rate': threshold_exceeded_count / len(metrics) if metrics else 0,
            'measurements_count': len(metrics),
            'duration_minutes': scenario.duration_minutes
        }
    
    def run(self) -> Dict[str, Any]:
        """Executa todos os testes de métricas do sistema"""
        self.log("🚀 Iniciando testes de métricas do sistema")
        
        all_results = {
            'tracing_id': self.tracing_id,
            'start_time': self.start_time.isoformat(),
            'host': self.host,
            'scenarios': [],
            'summary': {},
            'system_analysis': {}
        }
        
        try:
            # Executar cenários
            for i, scenario in enumerate(self.system_metric_scenarios):
                self.log(f"Executando cenário {i+1}/{len(self.system_metric_scenarios)}: {scenario.name}")
                
                scenario_result = self.test_system_metric_scenario(scenario)
                scenario_result['scenario_index'] = i + 1
                
                all_results['scenarios'].append(scenario_result)
                
                # Atualizar métricas
                self.metrics['scenarios_executed'] += 1
                if scenario_result.get('summary', {}).get('threshold_exceeded_count', 0) > 0:
                    self.metrics['thresholds_exceeded'] += 1
                
                # Pausa entre cenários
                if i < len(self.system_metric_scenarios) - 1:
                    time.sleep(10)
            
            # Gerar resumo geral
            all_results['summary'] = self.generate_overall_summary(all_results)
            all_results['system_analysis'] = self.analyze_overall_system_metrics(all_results)
            all_results['end_time'] = datetime.now().isoformat()
            
            # Calcular sucesso geral
            total_scenarios = len(all_results['scenarios'])
            successful_scenarios = sum(1 for s in all_results['scenarios'] 
                                     if not s.get('error'))
            success_rate = successful_scenarios / total_scenarios if total_scenarios > 0 else 0
            
            all_results['success'] = success_rate >= 0.8
            
            self.log(f"✅ Testes de métricas do sistema concluídos: {success_rate:.1%} de sucesso")
            
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
    
    def analyze_overall_system_metrics(self, all_results: Dict) -> Dict[str, Any]:
        """Analisa métricas gerais do sistema"""
        all_metrics = []
        for scenario in all_results['scenarios']:
            all_metrics.extend(scenario.get('system_metrics', []))
        
        if not all_metrics:
            return {}
        
        # Análise geral
        cpu_values = [m.get('cpu', 0) for m in all_metrics]
        memory_values = [m.get('memory', 0) for m in all_metrics]
        disk_values = [m.get('disk', 0) for m in all_metrics]
        network_values = [m.get('network', 0) for m in all_metrics]
        
        return {
            'total_measurements': len(all_metrics),
            'avg_cpu_usage': np.mean(cpu_values) if cpu_values else 0,
            'avg_memory_usage': np.mean(memory_values) if memory_values else 0,
            'avg_disk_usage': np.mean(disk_values) if disk_values else 0,
            'avg_network_usage': np.mean(network_values) if network_values else 0,
            'max_cpu_usage': max(cpu_values) if cpu_values else 0,
            'max_memory_usage': max(memory_values) if memory_values else 0
        }


class SystemMetricsMonitor:
    """Monitor de métricas do sistema"""
    
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
                # Obter métricas do sistema
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                network = psutil.net_io_counters()
                
                # Obter métricas do processo
                process = psutil.Process()
                process_memory = process.memory_info()
                process_cpu = process.cpu_percent()
                
                measurement = {
                    'timestamp': datetime.now(),
                    'cpu': cpu_percent,
                    'memory': memory.percent,
                    'disk': disk.percent,
                    'network_bytes_sent': network.bytes_sent,
                    'network_bytes_recv': network.bytes_recv,
                    'process_cpu': process_cpu,
                    'process_memory_mb': process_memory.rss / 1024 / 1024
                }
                
                self.metrics.append(measurement)
                
                # Aguardar 5 segundos
                time.sleep(5)
                
            except Exception as e:
                logging.error(f"Erro no monitoramento de métricas: {e}")
                time.sleep(5)
    
    def get_metrics(self) -> List[Dict]:
        """Retorna as métricas coletadas"""
        return self.metrics.copy()


def main():
    """Função principal para execução standalone"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Teste de Métricas do Sistema")
    parser.add_argument('--host', default='http://localhost:8000', help='Host para testar')
    parser.add_argument('--verbose', action='store_true', help='Modo verboso')
    
    args = parser.parse_args()
    
    # Criar e executar teste
    test = MonitoringSystemMetricsTest(host=args.host, verbose=args.verbose)
    result = test.run()
    
    # Imprimir resultados
    print("\n" + "="*80)
    print("📊 RESULTADOS DOS TESTES DE MÉTRICAS DO SISTEMA")
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
    
    if 'system_analysis' in result:
        analysis = result['system_analysis']
        print(f"\n💻 ANÁLISE DO SISTEMA:")
        print(f"   • Total de Medições: {analysis['total_measurements']}")
        print(f"   • CPU Médio: {analysis['avg_cpu_usage']:.1f}%")
        print(f"   • Memória Média: {analysis['avg_memory_usage']:.1f}%")
        print(f"   • Disco Médio: {analysis['avg_disk_usage']:.1f}%")
        print(f"   • CPU Máximo: {analysis['max_cpu_usage']:.1f}%")
        print(f"   • Memória Máxima: {analysis['max_memory_usage']:.1f}%")
    
    print("="*80)


if __name__ == "__main__":
    main() 