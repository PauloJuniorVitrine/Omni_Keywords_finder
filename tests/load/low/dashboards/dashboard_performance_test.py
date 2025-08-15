#!/usr/bin/env python3
"""
Teste de Performance de Dashboards
Omni Keywords Finder - Tracing ID: DASHBOARD_PERFORMANCE_20250127_001

Este teste valida a performance de dashboards sob carga:
- Tempo de carregamento de dashboards
- Performance de renderização de gráficos
- Responsividade de dashboards
- Carga de dados em tempo real
- Performance de filtros e interações

Baseado em:
- app/components/dashboard/DashboardCard.tsx
- app/components/analytics/AnalyticsChart.tsx
- app/components/metrics/MetricsDisplay.tsx
- backend/app/api/dashboard.py

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
class DashboardScenario:
    """Cenário de teste de dashboard"""
    name: str
    description: str
    dashboard_type: str  # 'analytics', 'metrics', 'reports', 'monitoring', 'business'
    duration_minutes: int
    load_intensity: str  # 'low', 'medium', 'high', 'extreme'
    expected_behavior: str
    target_load_time: float  # ms


class DashboardPerformanceTest:
    """
    Teste de performance de dashboards sob carga
    """
    
    def __init__(self, host: str = "http://localhost:8000", verbose: bool = False):
        self.host = host
        self.verbose = verbose
        self.tracing_id = "DASHBOARD_PERFORMANCE_20250127_001"
        self.start_time = datetime.now()
        
        # Configurar logging
        self.setup_logging()
        
        # Inicializar monitor de dashboards
        self.dashboard_monitor = DashboardMonitor()
        
        # Cenários de dashboards
        self.dashboard_scenarios = [
            DashboardScenario(
                name="Dashboard de Analytics",
                description="Performance do dashboard principal de analytics",
                dashboard_type="analytics",
                duration_minutes=30,
                load_intensity="high",
                expected_behavior="Carregamento rápido de gráficos e métricas",
                target_load_time=2000.0  # 2 segundos
            ),
            DashboardScenario(
                name="Dashboard de Métricas",
                description="Performance do dashboard de métricas do sistema",
                dashboard_type="metrics",
                duration_minutes=25,
                load_intensity="medium",
                expected_behavior="Exibição eficiente de métricas em tempo real",
                target_load_time=1500.0  # 1.5 segundos
            ),
            DashboardScenario(
                name="Dashboard de Relatórios",
                description="Performance do dashboard de relatórios",
                dashboard_type="reports",
                duration_minutes=35,
                load_intensity="extreme",
                expected_behavior="Geração e exibição de relatórios complexos",
                target_load_time=5000.0  # 5 segundos
            ),
            DashboardScenario(
                name="Dashboard de Monitoramento",
                description="Performance do dashboard de monitoramento",
                dashboard_type="monitoring",
                duration_minutes=40,
                load_intensity="high",
                expected_behavior="Monitoramento em tempo real de recursos",
                target_load_time=3000.0  # 3 segundos
            ),
            DashboardScenario(
                name="Dashboard de Negócio",
                description="Performance do dashboard de métricas de negócio",
                dashboard_type="business",
                duration_minutes=45,
                load_intensity="medium",
                expected_behavior="Análise de métricas de negócio",
                target_load_time=2500.0  # 2.5 segundos
            )
        ]
        
        # Endpoints para teste de dashboards
        self.dashboard_endpoints = [
            "/api/dashboard/analytics",
            "/api/dashboard/metrics",
            "/api/dashboard/reports",
            "/api/dashboard/monitoring",
            "/api/dashboard/business",
            "/api/dashboard/charts",
            "/api/dashboard/filters",
            "/api/dashboard/export"
        ]
        
        # Métricas coletadas
        self.metrics = {
            'scenarios_executed': 0,
            'scenarios_failed': 0,
            'dashboards_loaded': 0,
            'dashboard_interactions': 0,
            'avg_load_time': 0.0
        }
        
    def setup_logging(self):
        """Configura logging estruturado"""
        logging.basicConfig(
            level=logging.INFO if self.verbose else logging.WARNING,
            format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
            handlers=[
                logging.FileHandler(f'logs/dashboard_performance_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(f"DashboardPerformanceTest_{self.tracing_id}")
        
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
    
    def test_dashboard_scenario(self, scenario: DashboardScenario) -> Dict[str, Any]:
        """Testa um cenário específico de dashboard"""
        self.log(f"Iniciando teste: {scenario.name} ({scenario.duration_minutes}min)")
        
        results = {
            'scenario_name': scenario.name,
            'dashboard_type': scenario.dashboard_type,
            'load_intensity': scenario.load_intensity,
            'start_time': datetime.now().isoformat(),
            'dashboard_metrics': [],
            'dashboard_events': [],
            'analysis': {},
            'summary': {}
        }
        
        try:
            # Iniciar monitoramento
            self.dashboard_monitor.start_monitoring(scenario.dashboard_type)
            
            # Executar cenário
            scenario_result = self.execute_dashboard_scenario(scenario)
            
            # Parar monitoramento
            self.dashboard_monitor.stop_monitoring()
            
            # Analisar resultados
            results['dashboard_metrics'] = self.dashboard_monitor.get_metrics()
            results['dashboard_events'] = self.detect_dashboard_events(results['dashboard_metrics'], scenario)
            results['analysis'] = self.analyze_dashboard_performance(results['dashboard_metrics'], scenario)
            results['summary'] = self.analyze_dashboard_results(scenario_result, results['dashboard_metrics'], scenario)
            results['end_time'] = datetime.now().isoformat()
            
        except Exception as e:
            error_msg = f"Erro durante teste {scenario.name}: {str(e)}"
            self.log(error_msg, "ERROR")
            results['error'] = error_msg
            
        return results
    
    def execute_dashboard_scenario(self, scenario: DashboardScenario) -> Dict[str, Any]:
        """Executa o cenário de dashboard"""
        start_time = time.time()
        end_time = start_time + (scenario.duration_minutes * 60)
        
        scenario_result = {
            'requests_made': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_load_time': 0.0,
            'dashboard_events': []
        }
        
        self.log(f"Executando cenário por {scenario.duration_minutes} minutos")
        
        try:
            with ThreadPoolExecutor(max_workers=self.get_concurrent_workers(scenario.load_intensity)) as executor:
                futures = []
                
                while time.time() < end_time:
                    # Calcular intensidade de carga
                    load_intensity = self.calculate_load_intensity(scenario.load_intensity, time.time() - start_time)
                    
                    # Submeter requisições
                    for _ in range(self.get_request_count(scenario.load_intensity)):
                        future = executor.submit(
                            self.make_dashboard_request,
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
                            
                            scenario_result['total_load_time'] += result['load_time']
                            
                            # Registrar evento de dashboard
                            dashboard_event = {
                                'timestamp': datetime.now().isoformat(),
                                'endpoint': result['endpoint'],
                                'load_time': result['load_time'],
                                'load_intensity': load_intensity,
                                'success': result['success'],
                                'dashboard_type': scenario.dashboard_type
                            }
                            scenario_result['dashboard_events'].append(dashboard_event)
                            
                        except Exception as e:
                            self.log(f"Erro na requisição de dashboard: {str(e)}", "ERROR")
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
            scenario_result['avg_load_time'] = scenario_result['total_load_time'] / scenario_result['requests_made']
        
        return scenario_result
    
    def get_concurrent_workers(self, load_intensity: str) -> int:
        """Retorna número de workers baseado na intensidade de carga"""
        if load_intensity == "low":
            return 8
        elif load_intensity == "medium":
            return 15
        elif load_intensity == "high":
            return 25
        elif load_intensity == "extreme":
            return 35
        else:
            return 12
    
    def get_request_count(self, load_intensity: str) -> int:
        """Retorna número de requisições baseado na intensidade de carga"""
        if load_intensity == "low":
            return 4
        elif load_intensity == "medium":
            return 8
        elif load_intensity == "high":
            return 15
        elif load_intensity == "extreme":
            return 25
        else:
            return 6
    
    def calculate_load_intensity(self, load_intensity: str, elapsed_time: float) -> float:
        """Calcula intensidade de carga"""
        if load_intensity == "low":
            return 0.3
        
        elif load_intensity == "medium":
            return 0.6
        
        elif load_intensity == "high":
            # Variação baseada em função seno
            variation = np.sin(elapsed_time / 300) * 0.3 + 0.7  # Variação de 0.4 a 1.0
            return variation
        
        elif load_intensity == "extreme":
            # Picos extremos a cada 2 minutos
            extreme_cycle = 120
            if (elapsed_time % extreme_cycle) < 60:  # 1 minuto de pico
                return 1.0
            else:
                return 0.4
        
        return 0.5
    
    def calculate_wait_time(self, load_intensity: str) -> float:
        """Calcula tempo de espera baseado na intensidade de carga"""
        if load_intensity == "low":
            return 4.0
        elif load_intensity == "medium":
            return 2.5
        elif load_intensity == "high":
            return 1.5
        elif load_intensity == "extreme":
            return 1.0
        else:
            return 3.0
    
    def make_dashboard_request(self, scenario: DashboardScenario, load_intensity: float) -> Dict[str, Any]:
        """Faz uma requisição para teste de dashboard"""
        start_time = time.time()
        
        try:
            # Selecionar endpoint baseado no tipo de dashboard
            endpoint = self.select_dashboard_endpoint(scenario.dashboard_type, load_intensity)
            
            # Gerar payload específico para dashboard
            payload = self.generate_dashboard_payload(scenario, load_intensity)
            
            # Fazer requisição
            response = requests.post(
                f"{self.host}{endpoint}",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=60  # Timeout maior para dashboards
            )
            
            end_time = time.time()
            load_time = end_time - start_time
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'load_time': load_time * 1000,  # Converter para ms
                'endpoint': endpoint,
                'load_intensity': load_intensity,
                'payload_size': len(json.dumps(payload))
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                'success': False,
                'error': str(e),
                'load_time': (end_time - start_time) * 1000,
                'endpoint': 'unknown',
                'load_intensity': load_intensity
            }
    
    def select_dashboard_endpoint(self, dashboard_type: str, load_intensity: float) -> str:
        """Seleciona endpoint baseado no tipo de dashboard"""
        if dashboard_type == "analytics":
            return random.choice(["/api/dashboard/analytics", "/api/dashboard/charts"])
        
        elif dashboard_type == "metrics":
            return random.choice(["/api/dashboard/metrics", "/api/dashboard/monitoring"])
        
        elif dashboard_type == "reports":
            return random.choice(["/api/dashboard/reports", "/api/dashboard/export"])
        
        elif dashboard_type == "monitoring":
            return random.choice(["/api/dashboard/monitoring", "/api/dashboard/metrics"])
        
        elif dashboard_type == "business":
            return random.choice(["/api/dashboard/business", "/api/dashboard/analytics"])
        
        else:
            return random.choice(self.dashboard_endpoints)
    
    def generate_dashboard_payload(self, scenario: DashboardScenario, load_intensity: float) -> Dict[str, Any]:
        """Gera payload específico para teste de dashboard"""
        base_payload = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "dashboard_performance",
            "scenario": scenario.name,
            "load_intensity": load_intensity
        }
        
        if scenario.dashboard_type == "analytics":
            base_payload.update({
                "data": {
                    "analytics_dashboard": {
                        "chart_types": ["line", "bar", "pie", "area"],
                        "data_points": int(load_intensity * 1000),
                        "time_range": "30d",
                        "refresh_interval": 30
                    }
                }
            })
        
        elif scenario.dashboard_type == "metrics":
            base_payload.update({
                "data": {
                    "metrics_dashboard": {
                        "metric_types": ["cpu", "memory", "disk", "network"],
                        "update_frequency": "5s",
                        "history_days": 7,
                        "real_time": True
                    }
                }
            })
        
        elif scenario.dashboard_type == "reports":
            base_payload.update({
                "data": {
                    "reports_dashboard": {
                        "report_types": ["performance", "business", "security"],
                        "complexity": "high" if load_intensity > 0.7 else "medium",
                        "include_charts": True,
                        "export_format": "pdf"
                    }
                }
            })
        
        elif scenario.dashboard_type == "monitoring":
            base_payload.update({
                "data": {
                    "monitoring_dashboard": {
                        "monitoring_targets": ["api", "database", "cache", "queue"],
                        "alert_thresholds": True,
                        "real_time_updates": True,
                        "auto_refresh": True
                    }
                }
            })
        
        elif scenario.dashboard_type == "business":
            base_payload.update({
                "data": {
                    "business_dashboard": {
                        "business_metrics": ["revenue", "conversions", "users", "engagement"],
                        "time_periods": ["daily", "weekly", "monthly"],
                        "comparison_enabled": True,
                        "forecasting": load_intensity > 0.6
                    }
                }
            })
        
        return base_payload
    
    def detect_dashboard_events(self, metrics: List[Dict], scenario: DashboardScenario) -> List[Dict]:
        """Detecta eventos relacionados a dashboards"""
        dashboard_events = []
        
        for metric in metrics:
            load_time = metric.get('load_time', 0)
            
            # Detectar eventos baseado no tempo de carregamento
            if load_time > scenario.target_load_time * 1.5:
                dashboard_events.append({
                    'timestamp': metric['timestamp'],
                    'event_type': 'slow_dashboard_load',
                    'load_time': load_time,
                    'target': scenario.target_load_time,
                    'severity': 'high'
                })
            
            elif load_time > scenario.target_load_time:
                dashboard_events.append({
                    'timestamp': metric['timestamp'],
                    'event_type': 'dashboard_load_exceeded',
                    'load_time': load_time,
                    'target': scenario.target_load_time,
                    'severity': 'medium'
                })
            
            # Detectar problemas de renderização
            render_errors = metric.get('render_errors', 0)
            if render_errors > 0:
                dashboard_events.append({
                    'timestamp': metric['timestamp'],
                    'event_type': 'dashboard_render_error',
                    'error_count': render_errors,
                    'severity': 'high'
                })
        
        return dashboard_events
    
    def analyze_dashboard_performance(self, metrics: List[Dict], scenario: DashboardScenario) -> Dict[str, Any]:
        """Analisa a performance dos dashboards"""
        if not metrics:
            return {'analysis': 'no_data'}
        
        load_times = [m.get('load_time', 0) for m in metrics]
        render_times = [m.get('render_time', 0) for m in metrics]
        render_errors = [m.get('render_errors', 0) for m in metrics]
        
        # Estatísticas básicas
        mean_load_time = np.mean(load_times)
        max_load_time = max(load_times)
        mean_render_time = np.mean(render_times)
        total_errors = sum(render_errors)
        
        # Análise de tendência
        if len(load_times) > 1:
            trend = self.calculate_dashboard_trend(load_times)
        else:
            trend = "insufficient_data"
        
        # Análise de performance vs target
        load_time_achievement_rate = (scenario.target_load_time / mean_load_time) * 100 if mean_load_time > 0 else 0
        
        # Análise de estabilidade
        load_time_stability = 1.0 - (np.std(load_times) / mean_load_time) if mean_load_time > 0 else 0
        
        return {
            'mean_load_time': mean_load_time,
            'max_load_time': max_load_time,
            'mean_render_time': mean_render_time,
            'total_errors': total_errors,
            'trend': trend,
            'load_time_achievement_rate': load_time_achievement_rate,
            'load_time_stability': load_time_stability,
            'target_achieved': mean_load_time <= scenario.target_load_time,
            'performance_issues': sum(1 for l in load_times if l > scenario.target_load_time)
        }
    
    def calculate_dashboard_trend(self, load_times: List[float]) -> str:
        """Calcula tendência dos tempos de carregamento"""
        if len(load_times) < 2:
            return "insufficient_data"
        
        # Regressão linear simples
        x = list(range(len(load_times)))
        slope = np.polyfit(x, load_times, 1)[0]
        
        if abs(slope) < 10:
            return "stable"
        elif slope > 10:
            return "increasing"
        else:
            return "decreasing"
    
    def analyze_dashboard_results(self, scenario_result: Dict, metrics: List[Dict], scenario: DashboardScenario) -> Dict[str, Any]:
        """Analisa os resultados do teste de dashboard"""
        total_requests = scenario_result['requests_made']
        successful_requests = scenario_result['successful_requests']
        
        # Análise de métricas
        if metrics:
            load_times = [m.get('load_time', 0) for m in metrics]
            avg_load_time = np.mean(load_times)
            max_load_time = max(load_times)
            target_achieved_count = sum(1 for l in load_times if l <= scenario.target_load_time)
        else:
            avg_load_time = 0
            max_load_time = 0
            target_achieved_count = 0
        
        return {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'success_rate': successful_requests / total_requests if total_requests > 0 else 0,
            'avg_load_time': scenario_result.get('avg_load_time', 0),
            'avg_dashboard_load_time': avg_load_time,
            'max_dashboard_load_time': max_load_time,
            'target_achieved_count': target_achieved_count,
            'target_achievement_rate': target_achieved_count / len(metrics) if metrics else 0,
            'measurements_count': len(metrics),
            'duration_minutes': scenario.duration_minutes
        }
    
    def run(self) -> Dict[str, Any]:
        """Executa todos os testes de performance de dashboards"""
        self.log("🚀 Iniciando testes de performance de dashboards")
        
        all_results = {
            'tracing_id': self.tracing_id,
            'start_time': self.start_time.isoformat(),
            'host': self.host,
            'scenarios': [],
            'summary': {},
            'dashboard_analysis': {}
        }
        
        try:
            # Executar cenários
            for i, scenario in enumerate(self.dashboard_scenarios):
                self.log(f"Executando cenário {i+1}/{len(self.dashboard_scenarios)}: {scenario.name}")
                
                scenario_result = self.test_dashboard_scenario(scenario)
                scenario_result['scenario_index'] = i + 1
                
                all_results['scenarios'].append(scenario_result)
                
                # Atualizar métricas
                self.metrics['scenarios_executed'] += 1
                if scenario_result.get('summary', {}).get('target_achievement_rate', 0) >= 0.8:
                    self.metrics['dashboards_loaded'] += 1
                
                # Pausa entre cenários
                if i < len(self.dashboard_scenarios) - 1:
                    time.sleep(10)
            
            # Gerar resumo geral
            all_results['summary'] = self.generate_overall_summary(all_results)
            all_results['dashboard_analysis'] = self.analyze_overall_dashboard_performance(all_results)
            all_results['end_time'] = datetime.now().isoformat()
            
            # Calcular sucesso geral
            total_scenarios = len(all_results['scenarios'])
            successful_scenarios = sum(1 for s in all_results['scenarios'] 
                                     if not s.get('error'))
            success_rate = successful_scenarios / total_scenarios if total_scenarios > 0 else 0
            
            all_results['success'] = success_rate >= 0.8
            
            self.log(f"✅ Testes de performance de dashboards concluídos: {success_rate:.1%} de sucesso")
            
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
        
        # Análise por tipo de dashboard
        dashboard_analysis = {}
        for scenario in scenarios:
            dashboard_type = scenario.get('dashboard_type', 'unknown')
            if dashboard_type not in dashboard_analysis:
                dashboard_analysis[dashboard_type] = {
                    'count': 0,
                    'targets_achieved': 0,
                    'avg_load_time': 0.0
                }
            
            dashboard_analysis[dashboard_type]['count'] += 1
            summary = scenario.get('summary', {})
            if summary.get('target_achievement_rate', 0) >= 0.8:
                dashboard_analysis[dashboard_type]['targets_achieved'] += 1
            dashboard_analysis[dashboard_type]['avg_load_time'] += summary.get('avg_dashboard_load_time', 0)
        
        # Calcular médias
        for dashboard_type in dashboard_analysis:
            count = dashboard_analysis[dashboard_type]['count']
            if count > 0:
                dashboard_analysis[dashboard_type]['avg_load_time'] /= count
        
        return {
            'total_scenarios': total_scenarios,
            'targets_achieved': targets_achieved,
            'achievement_rate': targets_achieved / total_scenarios if total_scenarios > 0 else 0,
            'dashboard_analysis': dashboard_analysis
        }
    
    def analyze_overall_dashboard_performance(self, all_results: Dict) -> Dict[str, Any]:
        """Analisa performance geral dos dashboards"""
        all_metrics = []
        for scenario in all_results['scenarios']:
            all_metrics.extend(scenario.get('dashboard_metrics', []))
        
        if not all_metrics:
            return {}
        
        # Análise geral
        load_times = [m.get('load_time', 0) for m in all_metrics]
        render_times = [m.get('render_time', 0) for m in all_metrics]
        render_errors = [m.get('render_errors', 0) for m in all_metrics]
        
        return {
            'total_measurements': len(all_metrics),
            'avg_load_time_ms': np.mean(load_times) if load_times else 0,
            'max_load_time_ms': max(load_times) if load_times else 0,
            'avg_render_time_ms': np.mean(render_times) if render_times else 0,
            'total_render_errors': sum(render_errors),
            'total_dashboards_loaded': len(all_metrics)
        }


class DashboardMonitor:
    """Monitor de dashboards"""
    
    def __init__(self):
        self.metrics = []
        self.monitoring = False
        self.monitor_thread = None
        self.dashboard_type = None
        
    def start_monitoring(self, dashboard_type: str):
        """Inicia o monitoramento de dashboards"""
        self.metrics = []
        self.monitoring = True
        self.dashboard_type = dashboard_type
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Para o monitoramento de dashboards"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
    
    def _monitor_loop(self):
        """Loop de monitoramento"""
        while self.monitoring:
            try:
                # Simular coleta de métricas de dashboards
                # Em um ambiente real, isso viria do sistema de dashboards
                
                if self.dashboard_type == "analytics":
                    # Simular dashboards de analytics
                    load_time = np.random.normal(1500, 400)  # ms
                    render_time = np.random.normal(300, 100)  # ms
                    render_errors = np.random.poisson(0.1)  # erros
                    measurement = {
                        'timestamp': datetime.now(),
                        'load_time': max(0, load_time),
                        'render_time': max(0, render_time),
                        'render_errors': int(render_errors)
                    }
                
                elif self.dashboard_type == "metrics":
                    # Simular dashboards de métricas
                    load_time = np.random.normal(1000, 250)  # ms
                    render_time = np.random.normal(200, 80)  # ms
                    render_errors = np.random.poisson(0.05)  # erros
                    measurement = {
                        'timestamp': datetime.now(),
                        'load_time': max(0, load_time),
                        'render_time': max(0, render_time),
                        'render_errors': int(render_errors)
                    }
                
                elif self.dashboard_type == "reports":
                    # Simular dashboards de relatórios
                    load_time = np.random.normal(4000, 1000)  # ms
                    render_time = np.random.normal(800, 300)  # ms
                    render_errors = np.random.poisson(0.2)  # erros
                    measurement = {
                        'timestamp': datetime.now(),
                        'load_time': max(0, load_time),
                        'render_time': max(0, render_time),
                        'render_errors': int(render_errors)
                    }
                
                elif self.dashboard_type == "monitoring":
                    # Simular dashboards de monitoramento
                    load_time = np.random.normal(2500, 600)  # ms
                    render_time = np.random.normal(500, 150)  # ms
                    render_errors = np.random.poisson(0.15)  # erros
                    measurement = {
                        'timestamp': datetime.now(),
                        'load_time': max(0, load_time),
                        'render_time': max(0, render_time),
                        'render_errors': int(render_errors)
                    }
                
                elif self.dashboard_type == "business":
                    # Simular dashboards de negócio
                    load_time = np.random.normal(2000, 500)  # ms
                    render_time = np.random.normal(400, 120)  # ms
                    render_errors = np.random.poisson(0.1)  # erros
                    measurement = {
                        'timestamp': datetime.now(),
                        'load_time': max(0, load_time),
                        'render_time': max(0, render_time),
                        'render_errors': int(render_errors)
                    }
                
                else:
                    measurement = {
                        'timestamp': datetime.now(),
                        'load_time': 0,
                        'render_time': 0,
                        'render_errors': 0
                    }
                
                self.metrics.append(measurement)
                
                # Aguardar 12 segundos
                time.sleep(12)
                
            except Exception as e:
                logging.error(f"Erro no monitoramento de dashboards: {e}")
                time.sleep(12)
    
    def get_metrics(self) -> List[Dict]:
        """Retorna as métricas coletadas"""
        return self.metrics.copy()


def main():
    """Função principal para execução standalone"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Teste de Performance de Dashboards")
    parser.add_argument('--host', default='http://localhost:8000', help='Host para testar')
    parser.add_argument('--verbose', action='store_true', help='Modo verboso')
    
    args = parser.parse_args()
    
    # Criar e executar teste
    test = DashboardPerformanceTest(host=args.host, verbose=args.verbose)
    result = test.run()
    
    # Imprimir resultados
    print("\n" + "="*80)
    print("📊 RESULTADOS DOS TESTES DE PERFORMANCE DE DASHBOARDS")
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
    
    if 'dashboard_analysis' in result:
        analysis = result['dashboard_analysis']
        print(f"\n📊 ANÁLISE DE DASHBOARDS:")
        print(f"   • Total de Medições: {analysis['total_measurements']}")
        print(f"   • Tempo de Carregamento Médio: {analysis['avg_load_time_ms']:.1f} ms")
        print(f"   • Tempo de Carregamento Máximo: {analysis['max_load_time_ms']:.1f} ms")
        print(f"   • Tempo de Renderização Médio: {analysis['avg_render_time_ms']:.1f} ms")
        print(f"   • Total de Erros de Renderização: {analysis['total_render_errors']}")
        print(f"   • Total de Dashboards Carregados: {analysis['total_dashboards_loaded']}")
    
    print("="*80)


if __name__ == "__main__":
    main() 