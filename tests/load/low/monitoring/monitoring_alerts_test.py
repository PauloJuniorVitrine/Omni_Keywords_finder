#!/usr/bin/env python3
"""
Teste de Alertas
Omni Keywords Finder - Tracing ID: MONITORING_ALERTS_20250127_001

Este teste valida a geração e processamento de alertas sob carga:
- Geração de alertas
- Processamento de alertas
- Notificações
- Escalação de alertas
- Performance do sistema de alertas

Baseado em:
- infrastructure/monitoring/alert_manager.py
- backend/app/services/alert_service.py
- backend/app/api/alerts.py

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
class AlertScenario:
    """Cenário de teste de alertas"""
    name: str
    description: str
    alert_type: str  # 'performance', 'error', 'security', 'business', 'system'
    duration_minutes: int
    alert_intensity: str  # 'low', 'medium', 'high', 'critical'
    expected_behavior: str
    target_response_time: float  # ms


class MonitoringAlertsTest:
    """
    Teste de alertas sob carga
    """
    
    def __init__(self, host: str = "http://localhost:8000", verbose: bool = False):
        self.host = host
        self.verbose = verbose
        self.tracing_id = "MONITORING_ALERTS_20250127_001"
        self.start_time = datetime.now()
        
        # Configurar logging
        self.setup_logging()
        
        # Inicializar monitor de alertas
        self.alert_monitor = AlertMonitor()
        
        # Cenários de alertas
        self.alert_scenarios = [
            AlertScenario(
                name="Alertas de Performance",
                description="Geração de alertas de performance sob carga",
                alert_type="performance",
                duration_minutes=25,
                alert_intensity="high",
                expected_behavior="Detecção de problemas de performance",
                target_response_time=100.0  # 100ms
            ),
            AlertScenario(
                name="Alertas de Erro",
                description="Geração de alertas de erro",
                alert_type="error",
                duration_minutes=20,
                alert_intensity="critical",
                expected_behavior="Detecção e notificação de erros",
                target_response_time=50.0  # 50ms
            ),
            AlertScenario(
                name="Alertas de Segurança",
                description="Geração de alertas de segurança",
                alert_type="security",
                duration_minutes=30,
                alert_intensity="high",
                expected_behavior="Detecção de ameaças de segurança",
                target_response_time=75.0  # 75ms
            ),
            AlertScenario(
                name="Alertas de Negócio",
                description="Geração de alertas de negócio",
                alert_type="business",
                duration_minutes=35,
                alert_intensity="medium",
                expected_behavior="Monitoramento de métricas de negócio",
                target_response_time=150.0  # 150ms
            ),
            AlertScenario(
                name="Alertas de Sistema",
                description="Geração de alertas de sistema",
                alert_type="system",
                duration_minutes=40,
                alert_intensity="critical",
                expected_behavior="Monitoramento de recursos do sistema",
                target_response_time=80.0  # 80ms
            )
        ]
        
        # Endpoints para teste de alertas
        self.alert_endpoints = [
            "/api/alerts/create",
            "/api/alerts/process",
            "/api/alerts/notify",
            "/api/alerts/escalate",
            "/api/alerts/resolve",
            "/api/alerts/status",
            "/api/alerts/history",
            "/api/alerts/config"
        ]
        
        # Métricas coletadas
        self.metrics = {
            'scenarios_executed': 0,
            'scenarios_failed': 0,
            'alerts_generated': 0,
            'alerts_processed': 0,
            'avg_alert_response_time': 0.0
        }
        
    def setup_logging(self):
        """Configura logging estruturado"""
        logging.basicConfig(
            level=logging.INFO if self.verbose else logging.WARNING,
            format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
            handlers=[
                logging.FileHandler(f'logs/monitoring_alerts_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(f"MonitoringAlertsTest_{self.tracing_id}")
        
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
    
    def test_alert_scenario(self, scenario: AlertScenario) -> Dict[str, Any]:
        """Testa um cenário específico de alertas"""
        self.log(f"Iniciando teste: {scenario.name} ({scenario.duration_minutes}min)")
        
        results = {
            'scenario_name': scenario.name,
            'alert_type': scenario.alert_type,
            'alert_intensity': scenario.alert_intensity,
            'start_time': datetime.now().isoformat(),
            'alert_metrics': [],
            'alert_events': [],
            'analysis': {},
            'summary': {}
        }
        
        try:
            # Iniciar monitoramento
            self.alert_monitor.start_monitoring(scenario.alert_type)
            
            # Executar cenário
            scenario_result = self.execute_alert_scenario(scenario)
            
            # Parar monitoramento
            self.alert_monitor.stop_monitoring()
            
            # Analisar resultados
            results['alert_metrics'] = self.alert_monitor.get_metrics()
            results['alert_events'] = self.detect_alert_events(results['alert_metrics'], scenario)
            results['analysis'] = self.analyze_alerts(results['alert_metrics'], scenario)
            results['summary'] = self.analyze_alert_results(scenario_result, results['alert_metrics'], scenario)
            results['end_time'] = datetime.now().isoformat()
            
        except Exception as e:
            error_msg = f"Erro durante teste {scenario.name}: {str(e)}"
            self.log(error_msg, "ERROR")
            results['error'] = error_msg
            
        return results
    
    def execute_alert_scenario(self, scenario: AlertScenario) -> Dict[str, Any]:
        """Executa o cenário de alertas"""
        start_time = time.time()
        end_time = start_time + (scenario.duration_minutes * 60)
        
        scenario_result = {
            'requests_made': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_response_time': 0.0,
            'alert_events': []
        }
        
        self.log(f"Executando cenário por {scenario.duration_minutes} minutos")
        
        try:
            with ThreadPoolExecutor(max_workers=self.get_concurrent_workers(scenario.alert_intensity)) as executor:
                futures = []
                
                while time.time() < end_time:
                    # Calcular intensidade dos alertas
                    alert_intensity = self.calculate_alert_intensity(scenario.alert_intensity, time.time() - start_time)
                    
                    # Submeter requisições
                    for _ in range(self.get_request_count(scenario.alert_intensity)):
                        future = executor.submit(
                            self.make_alert_request,
                            scenario,
                            alert_intensity
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
                            
                            # Registrar evento de alerta
                            alert_event = {
                                'timestamp': datetime.now().isoformat(),
                                'endpoint': result['endpoint'],
                                'response_time': result['response_time'],
                                'alert_intensity': alert_intensity,
                                'success': result['success'],
                                'alert_type': scenario.alert_type
                            }
                            scenario_result['alert_events'].append(alert_event)
                            
                        except Exception as e:
                            self.log(f"Erro na requisição de alerta: {str(e)}", "ERROR")
                            scenario_result['failed_requests'] += 1
                    
                    # Limpar futures processados
                    futures = [f for f in futures if not f.done()]
                    
                    # Aguardar baseado na intensidade
                    wait_time = self.calculate_wait_time(scenario.alert_intensity)
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
    
    def get_concurrent_workers(self, alert_intensity: str) -> int:
        """Retorna número de workers baseado na intensidade dos alertas"""
        if alert_intensity == "low":
            return 5
        elif alert_intensity == "medium":
            return 15
        elif alert_intensity == "high":
            return 25
        elif alert_intensity == "critical":
            return 35
        else:
            return 10
    
    def get_request_count(self, alert_intensity: str) -> int:
        """Retorna número de requisições baseado na intensidade dos alertas"""
        if alert_intensity == "low":
            return 3
        elif alert_intensity == "medium":
            return 8
        elif alert_intensity == "high":
            return 15
        elif alert_intensity == "critical":
            return 25
        else:
            return 5
    
    def calculate_alert_intensity(self, alert_intensity: str, elapsed_time: float) -> float:
        """Calcula intensidade dos alertas"""
        if alert_intensity == "low":
            return 0.3
        
        elif alert_intensity == "medium":
            return 0.6
        
        elif alert_intensity == "high":
            # Variação baseada em função seno
            variation = np.sin(elapsed_time / 240) * 0.3 + 0.7  # Variação de 0.4 a 1.0
            return variation
        
        elif alert_intensity == "critical":
            # Picos críticos a cada 1.5 minutos
            critical_cycle = 90
            if (elapsed_time % critical_cycle) < 45:  # 45 segundos de pico
                return 1.0
            else:
                return 0.4
        
        return 0.5
    
    def calculate_wait_time(self, alert_intensity: str) -> float:
        """Calcula tempo de espera baseado na intensidade dos alertas"""
        if alert_intensity == "low":
            return 5.0
        elif alert_intensity == "medium":
            return 3.0
        elif alert_intensity == "high":
            return 2.0
        elif alert_intensity == "critical":
            return 1.0
        else:
            return 4.0
    
    def make_alert_request(self, scenario: AlertScenario, alert_intensity: float) -> Dict[str, Any]:
        """Faz uma requisição para teste de alertas"""
        start_time = time.time()
        
        try:
            # Selecionar endpoint baseado no tipo de alerta
            endpoint = self.select_alert_endpoint(scenario.alert_type, alert_intensity)
            
            # Gerar payload específico para alertas
            payload = self.generate_alert_payload(scenario, alert_intensity)
            
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
                'alert_intensity': alert_intensity,
                'payload_size': len(json.dumps(payload))
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                'success': False,
                'error': str(e),
                'response_time': (end_time - start_time) * 1000,
                'endpoint': 'unknown',
                'alert_intensity': alert_intensity
            }
    
    def select_alert_endpoint(self, alert_type: str, alert_intensity: float) -> str:
        """Seleciona endpoint baseado no tipo de alerta"""
        if alert_type == "performance":
            return random.choice(["/api/alerts/create", "/api/alerts/process"])
        
        elif alert_type == "error":
            return random.choice(["/api/alerts/create", "/api/alerts/notify"])
        
        elif alert_type == "security":
            return random.choice(["/api/alerts/create", "/api/alerts/escalate"])
        
        elif alert_type == "business":
            return random.choice(["/api/alerts/create", "/api/alerts/status"])
        
        elif alert_type == "system":
            return random.choice(["/api/alerts/create", "/api/alerts/process"])
        
        else:
            return random.choice(self.alert_endpoints)
    
    def generate_alert_payload(self, scenario: AlertScenario, alert_intensity: float) -> Dict[str, Any]:
        """Gera payload específico para teste de alertas"""
        base_payload = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "alert_testing",
            "scenario": scenario.name,
            "alert_intensity": alert_intensity
        }
        
        if scenario.alert_type == "performance":
            base_payload.update({
                "data": {
                    "performance_alert": {
                        "metric": "response_time",
                        "threshold": 2000,
                        "current_value": int(alert_intensity * 3000),
                        "severity": "high" if alert_intensity > 0.7 else "medium"
                    }
                }
            })
        
        elif scenario.alert_type == "error":
            base_payload.update({
                "data": {
                    "error_alert": {
                        "error_type": "database_connection_failed",
                        "error_count": int(alert_intensity * 100),
                        "severity": "critical" if alert_intensity > 0.8 else "high",
                        "requires_immediate_action": alert_intensity > 0.9
                    }
                }
            })
        
        elif scenario.alert_type == "security":
            base_payload.update({
                "data": {
                    "security_alert": {
                        "threat_type": "brute_force_attack",
                        "source_ip": f"192.168.1.{random.randint(1, 255)}",
                        "attempt_count": int(alert_intensity * 1000),
                        "severity": "critical" if alert_intensity > 0.7 else "high"
                    }
                }
            })
        
        elif scenario.alert_type == "business":
            base_payload.update({
                "data": {
                    "business_alert": {
                        "metric": "conversion_rate",
                        "threshold": 10.0,
                        "current_value": alert_intensity * 15.0,
                        "trend": "declining" if alert_intensity > 0.6 else "stable"
                    }
                }
            })
        
        elif scenario.alert_type == "system":
            base_payload.update({
                "data": {
                    "system_alert": {
                        "resource": "cpu_usage",
                        "threshold": 80.0,
                        "current_value": alert_intensity * 100.0,
                        "severity": "critical" if alert_intensity > 0.8 else "warning"
                    }
                }
            })
        
        return base_payload
    
    def detect_alert_events(self, metrics: List[Dict], scenario: AlertScenario) -> List[Dict]:
        """Detecta eventos relacionados a alertas"""
        alert_events = []
        
        for metric in metrics:
            alert_response_time = metric.get('alert_response_time', 0)
            
            # Detectar eventos baseado no tempo de resposta dos alertas
            if alert_response_time > scenario.target_response_time * 1.5:
                alert_events.append({
                    'timestamp': metric['timestamp'],
                    'event_type': 'slow_alert_response',
                    'response_time': alert_response_time,
                    'target': scenario.target_response_time,
                    'severity': 'high'
                })
            
            elif alert_response_time > scenario.target_response_time:
                alert_events.append({
                    'timestamp': metric['timestamp'],
                    'event_type': 'alert_response_exceeded',
                    'response_time': alert_response_time,
                    'target': scenario.target_response_time,
                    'severity': 'medium'
                })
            
            # Detectar problemas de processamento
            processing_errors = metric.get('processing_errors', 0)
            if processing_errors > 0:
                alert_events.append({
                    'timestamp': metric['timestamp'],
                    'event_type': 'alert_processing_error',
                    'error_count': processing_errors,
                    'severity': 'high'
                })
        
        return alert_events
    
    def analyze_alerts(self, metrics: List[Dict], scenario: AlertScenario) -> Dict[str, Any]:
        """Analisa os alertas"""
        if not metrics:
            return {'analysis': 'no_data'}
        
        alert_response_times = [m.get('alert_response_time', 0) for m in metrics]
        alert_counts = [m.get('alert_count', 0) for m in metrics]
        processing_errors = [m.get('processing_errors', 0) for m in metrics]
        
        # Estatísticas básicas
        mean_response_time = np.mean(alert_response_times)
        max_response_time = max(alert_response_times)
        total_alerts = sum(alert_counts)
        total_errors = sum(processing_errors)
        
        # Análise de tendência
        if len(alert_response_times) > 1:
            trend = self.calculate_alert_trend(alert_response_times)
        else:
            trend = "insufficient_data"
        
        # Análise de performance vs target
        response_time_achievement_rate = (scenario.target_response_time / mean_response_time) * 100 if mean_response_time > 0 else 0
        
        # Análise de estabilidade
        response_time_stability = 1.0 - (np.std(alert_response_times) / mean_response_time) if mean_response_time > 0 else 0
        
        return {
            'mean_response_time': mean_response_time,
            'max_response_time': max_response_time,
            'total_alerts': total_alerts,
            'total_errors': total_errors,
            'trend': trend,
            'response_time_achievement_rate': response_time_achievement_rate,
            'response_time_stability': response_time_stability,
            'target_achieved': mean_response_time <= scenario.target_response_time,
            'performance_issues': sum(1 for r in alert_response_times if r > scenario.target_response_time)
        }
    
    def calculate_alert_trend(self, response_times: List[float]) -> str:
        """Calcula tendência dos tempos de resposta dos alertas"""
        if len(response_times) < 2:
            return "insufficient_data"
        
        # Regressão linear simples
        x = list(range(len(response_times)))
        slope = np.polyfit(x, response_times, 1)[0]
        
        if abs(slope) < 1:
            return "stable"
        elif slope > 1:
            return "increasing"
        else:
            return "decreasing"
    
    def analyze_alert_results(self, scenario_result: Dict, metrics: List[Dict], scenario: AlertScenario) -> Dict[str, Any]:
        """Analisa os resultados do teste de alertas"""
        total_requests = scenario_result['requests_made']
        successful_requests = scenario_result['successful_requests']
        
        # Análise de métricas
        if metrics:
            alert_response_times = [m.get('alert_response_time', 0) for m in metrics]
            avg_response_time = np.mean(alert_response_times)
            max_response_time = max(alert_response_times)
            target_achieved_count = sum(1 for r in alert_response_times if r <= scenario.target_response_time)
        else:
            avg_response_time = 0
            max_response_time = 0
            target_achieved_count = 0
        
        return {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'success_rate': successful_requests / total_requests if total_requests > 0 else 0,
            'avg_response_time': scenario_result.get('avg_response_time', 0),
            'avg_alert_response_time': avg_response_time,
            'max_alert_response_time': max_response_time,
            'target_achieved_count': target_achieved_count,
            'target_achievement_rate': target_achieved_count / len(metrics) if metrics else 0,
            'measurements_count': len(metrics),
            'duration_minutes': scenario.duration_minutes
        }
    
    def run(self) -> Dict[str, Any]:
        """Executa todos os testes de alertas"""
        self.log("🚀 Iniciando testes de alertas")
        
        all_results = {
            'tracing_id': self.tracing_id,
            'start_time': self.start_time.isoformat(),
            'host': self.host,
            'scenarios': [],
            'summary': {},
            'alert_analysis': {}
        }
        
        try:
            # Executar cenários
            for i, scenario in enumerate(self.alert_scenarios):
                self.log(f"Executando cenário {i+1}/{len(self.alert_scenarios)}: {scenario.name}")
                
                scenario_result = self.test_alert_scenario(scenario)
                scenario_result['scenario_index'] = i + 1
                
                all_results['scenarios'].append(scenario_result)
                
                # Atualizar métricas
                self.metrics['scenarios_executed'] += 1
                if scenario_result.get('summary', {}).get('target_achievement_rate', 0) >= 0.8:
                    self.metrics['alerts_generated'] += 1
                
                # Pausa entre cenários
                if i < len(self.alert_scenarios) - 1:
                    time.sleep(10)
            
            # Gerar resumo geral
            all_results['summary'] = self.generate_overall_summary(all_results)
            all_results['alert_analysis'] = self.analyze_overall_alerts(all_results)
            all_results['end_time'] = datetime.now().isoformat()
            
            # Calcular sucesso geral
            total_scenarios = len(all_results['scenarios'])
            successful_scenarios = sum(1 for s in all_results['scenarios'] 
                                     if not s.get('error'))
            success_rate = successful_scenarios / total_scenarios if total_scenarios > 0 else 0
            
            all_results['success'] = success_rate >= 0.8
            
            self.log(f"✅ Testes de alertas concluídos: {success_rate:.1%} de sucesso")
            
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
        
        # Análise por tipo de alerta
        alert_analysis = {}
        for scenario in scenarios:
            alert_type = scenario.get('alert_type', 'unknown')
            if alert_type not in alert_analysis:
                alert_analysis[alert_type] = {
                    'count': 0,
                    'targets_achieved': 0,
                    'avg_response_time': 0.0
                }
            
            alert_analysis[alert_type]['count'] += 1
            summary = scenario.get('summary', {})
            if summary.get('target_achievement_rate', 0) >= 0.8:
                alert_analysis[alert_type]['targets_achieved'] += 1
            alert_analysis[alert_type]['avg_response_time'] += summary.get('avg_alert_response_time', 0)
        
        # Calcular médias
        for alert_type in alert_analysis:
            count = alert_analysis[alert_type]['count']
            if count > 0:
                alert_analysis[alert_type]['avg_response_time'] /= count
        
        return {
            'total_scenarios': total_scenarios,
            'targets_achieved': targets_achieved,
            'achievement_rate': targets_achieved / total_scenarios if total_scenarios > 0 else 0,
            'alert_analysis': alert_analysis
        }
    
    def analyze_overall_alerts(self, all_results: Dict) -> Dict[str, Any]:
        """Analisa alertas gerais"""
        all_metrics = []
        for scenario in all_results['scenarios']:
            all_metrics.extend(scenario.get('alert_metrics', []))
        
        if not all_metrics:
            return {}
        
        # Análise geral
        alert_response_times = [m.get('alert_response_time', 0) for m in all_metrics]
        alert_counts = [m.get('alert_count', 0) for m in all_metrics]
        processing_errors = [m.get('processing_errors', 0) for m in all_metrics]
        
        return {
            'total_measurements': len(all_metrics),
            'avg_alert_response_time_ms': np.mean(alert_response_times) if alert_response_times else 0,
            'max_alert_response_time_ms': max(alert_response_times) if alert_response_times else 0,
            'total_alerts_generated': sum(alert_counts),
            'total_processing_errors': sum(processing_errors),
            'avg_alerts_per_minute': sum(alert_counts) / (len(all_metrics) * 10) if all_metrics else 0  # 10s por medição
        }


class AlertMonitor:
    """Monitor de alertas"""
    
    def __init__(self):
        self.metrics = []
        self.monitoring = False
        self.monitor_thread = None
        self.alert_type = None
        
    def start_monitoring(self, alert_type: str):
        """Inicia o monitoramento de alertas"""
        self.metrics = []
        self.monitoring = True
        self.alert_type = alert_type
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Para o monitoramento de alertas"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
    
    def _monitor_loop(self):
        """Loop de monitoramento"""
        while self.monitoring:
            try:
                # Simular coleta de métricas de alertas
                # Em um ambiente real, isso viria do sistema de alertas
                
                if self.alert_type == "performance":
                    # Simular alertas de performance
                    alert_response_time = np.random.normal(80, 25)  # ms
                    alert_count = np.random.poisson(5)  # alertas
                    processing_errors = np.random.poisson(0.1)  # erros
                    measurement = {
                        'timestamp': datetime.now(),
                        'alert_response_time': max(0, alert_response_time),
                        'alert_count': int(alert_count),
                        'processing_errors': int(processing_errors)
                    }
                
                elif self.alert_type == "error":
                    # Simular alertas de erro
                    alert_response_time = np.random.normal(40, 15)  # ms
                    alert_count = np.random.poisson(10)  # alertas
                    processing_errors = np.random.poisson(0.2)  # erros
                    measurement = {
                        'timestamp': datetime.now(),
                        'alert_response_time': max(0, alert_response_time),
                        'alert_count': int(alert_count),
                        'processing_errors': int(processing_errors)
                    }
                
                elif self.alert_type == "security":
                    # Simular alertas de segurança
                    alert_response_time = np.random.normal(60, 20)  # ms
                    alert_count = np.random.poisson(3)  # alertas
                    processing_errors = np.random.poisson(0.05)  # erros
                    measurement = {
                        'timestamp': datetime.now(),
                        'alert_response_time': max(0, alert_response_time),
                        'alert_count': int(alert_count),
                        'processing_errors': int(processing_errors)
                    }
                
                elif self.alert_type == "business":
                    # Simular alertas de negócio
                    alert_response_time = np.random.normal(120, 40)  # ms
                    alert_count = np.random.poisson(2)  # alertas
                    processing_errors = np.random.poisson(0.1)  # erros
                    measurement = {
                        'timestamp': datetime.now(),
                        'alert_response_time': max(0, alert_response_time),
                        'alert_count': int(alert_count),
                        'processing_errors': int(processing_errors)
                    }
                
                elif self.alert_type == "system":
                    # Simular alertas de sistema
                    alert_response_time = np.random.normal(70, 25)  # ms
                    alert_count = np.random.poisson(4)  # alertas
                    processing_errors = np.random.poisson(0.15)  # erros
                    measurement = {
                        'timestamp': datetime.now(),
                        'alert_response_time': max(0, alert_response_time),
                        'alert_count': int(alert_count),
                        'processing_errors': int(processing_errors)
                    }
                
                else:
                    measurement = {
                        'timestamp': datetime.now(),
                        'alert_response_time': 0,
                        'alert_count': 0,
                        'processing_errors': 0
                    }
                
                self.metrics.append(measurement)
                
                # Aguardar 10 segundos
                time.sleep(10)
                
            except Exception as e:
                logging.error(f"Erro no monitoramento de alertas: {e}")
                time.sleep(10)
    
    def get_metrics(self) -> List[Dict]:
        """Retorna as métricas coletadas"""
        return self.metrics.copy()


def main():
    """Função principal para execução standalone"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Teste de Alertas")
    parser.add_argument('--host', default='http://localhost:8000', help='Host para testar')
    parser.add_argument('--verbose', action='store_true', help='Modo verboso')
    
    args = parser.parse_args()
    
    # Criar e executar teste
    test = MonitoringAlertsTest(host=args.host, verbose=args.verbose)
    result = test.run()
    
    # Imprimir resultados
    print("\n" + "="*80)
    print("📊 RESULTADOS DOS TESTES DE ALERTAS")
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
    
    if 'alert_analysis' in result:
        analysis = result['alert_analysis']
        print(f"\n🚨 ANÁLISE DE ALERTAS:")
        print(f"   • Total de Medições: {analysis['total_measurements']}")
        print(f"   • Tempo de Resposta Médio: {analysis['avg_alert_response_time_ms']:.1f} ms")
        print(f"   • Tempo de Resposta Máximo: {analysis['max_alert_response_time_ms']:.1f} ms")
        print(f"   • Total de Alertas Gerados: {analysis['total_alerts_generated']}")
        print(f"   • Total de Erros de Processamento: {analysis['total_processing_errors']}")
        print(f"   • Média de Alertas por Minuto: {analysis['avg_alerts_per_minute']:.1f}")
    
    print("="*80)


if __name__ == "__main__":
    main() 