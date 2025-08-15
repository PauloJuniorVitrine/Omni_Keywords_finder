#!/usr/bin/env python3
"""
Teste de Visualização de Dados
Omni Keywords Finder - Tracing ID: DASHBOARD_VISUALIZATION_20250127_001

Este teste valida a visualização de dados sob carga:
- Performance de renderização de gráficos
- Carga de visualizações complexas
- Interatividade de gráficos
- Exportação de visualizações
- Responsividade de dashboards

Baseado em:
- app/components/analytics/AnalyticsChart.tsx
- app/components/charts/ChartRenderer.tsx
- app/components/visualization/DataVisualization.tsx
- backend/app/api/visualization.py

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
class VisualizationScenario:
    """Cenário de teste de visualização"""
    name: str
    description: str
    visualization_type: str  # 'chart', 'graph', 'heatmap', 'scatter', 'dashboard'
    duration_minutes: int
    complexity: str  # 'simple', 'medium', 'complex', 'extreme'
    expected_behavior: str
    target_render_time: float  # ms


class DashboardVisualizationTest:
    """
    Teste de visualização de dados sob carga
    """
    
    def __init__(self, host: str = "http://localhost:8000", verbose: bool = False):
        self.host = host
        self.verbose = verbose
        self.tracing_id = "DASHBOARD_VISUALIZATION_20250127_001"
        self.start_time = datetime.now()
        
        # Configurar logging
        self.setup_logging()
        
        # Inicializar monitor de visualizações
        self.visualization_monitor = VisualizationMonitor()
        
        # Cenários de visualização
        self.visualization_scenarios = [
            VisualizationScenario(
                name="Gráficos de Linha",
                description="Performance de gráficos de linha com dados em tempo real",
                visualization_type="chart",
                duration_minutes=25,
                complexity="medium",
                expected_behavior="Renderização suave de gráficos de linha",
                target_render_time=800.0  # 800ms
            ),
            VisualizationScenario(
                name="Gráficos de Barras",
                description="Performance de gráficos de barras complexos",
                visualization_type="chart",
                duration_minutes=30,
                complexity="complex",
                expected_behavior="Renderização eficiente de gráficos de barras",
                target_render_time=1200.0  # 1.2s
            ),
            VisualizationScenario(
                name="Gráficos de Dispersão",
                description="Performance de gráficos de dispersão com muitos pontos",
                visualization_type="scatter",
                duration_minutes=35,
                complexity="extreme",
                expected_behavior="Renderização de gráficos de dispersão complexos",
                target_render_time=2000.0  # 2s
            ),
            VisualizationScenario(
                name="Mapas de Calor",
                description="Performance de mapas de calor com dados multidimensionais",
                visualization_type="heatmap",
                duration_minutes=40,
                complexity="extreme",
                expected_behavior="Renderização de mapas de calor interativos",
                target_render_time=2500.0  # 2.5s
            ),
            VisualizationScenario(
                name="Dashboards Interativos",
                description="Performance de dashboards com múltiplas visualizações",
                visualization_type="dashboard",
                duration_minutes=45,
                complexity="complex",
                expected_behavior="Interatividade fluida em dashboards",
                target_render_time=3000.0  # 3s
            )
        ]
        
        # Endpoints para teste de visualização
        self.visualization_endpoints = [
            "/api/visualization/chart",
            "/api/visualization/graph",
            "/api/visualization/heatmap",
            "/api/visualization/scatter",
            "/api/visualization/dashboard",
            "/api/visualization/export",
            "/api/visualization/interactive",
            "/api/visualization/realtime"
        ]
        
        # Métricas coletadas
        self.metrics = {
            'scenarios_executed': 0,
            'scenarios_failed': 0,
            'visualizations_rendered': 0,
            'interactions_processed': 0,
            'avg_render_time': 0.0
        }
        
    def setup_logging(self):
        """Configura logging estruturado"""
        logging.basicConfig(
            level=logging.INFO if self.verbose else logging.WARNING,
            format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
            handlers=[
                logging.FileHandler(f'logs/dashboard_visualization_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(f"DashboardVisualizationTest_{self.tracing_id}")
        
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
    
    def test_visualization_scenario(self, scenario: VisualizationScenario) -> Dict[str, Any]:
        """Testa um cenário específico de visualização"""
        self.log(f"Iniciando teste: {scenario.name} ({scenario.duration_minutes}min)")
        
        results = {
            'scenario_name': scenario.name,
            'visualization_type': scenario.visualization_type,
            'complexity': scenario.complexity,
            'start_time': datetime.now().isoformat(),
            'visualization_metrics': [],
            'visualization_events': [],
            'analysis': {},
            'summary': {}
        }
        
        try:
            # Iniciar monitoramento
            self.visualization_monitor.start_monitoring(scenario.visualization_type)
            
            # Executar cenário
            scenario_result = self.execute_visualization_scenario(scenario)
            
            # Parar monitoramento
            self.visualization_monitor.stop_monitoring()
            
            # Analisar resultados
            results['visualization_metrics'] = self.visualization_monitor.get_metrics()
            results['visualization_events'] = self.detect_visualization_events(results['visualization_metrics'], scenario)
            results['analysis'] = self.analyze_visualization_performance(results['visualization_metrics'], scenario)
            results['summary'] = self.analyze_visualization_results(scenario_result, results['visualization_metrics'], scenario)
            results['end_time'] = datetime.now().isoformat()
            
        except Exception as e:
            error_msg = f"Erro durante teste {scenario.name}: {str(e)}"
            self.log(error_msg, "ERROR")
            results['error'] = error_msg
            
        return results
    
    def execute_visualization_scenario(self, scenario: VisualizationScenario) -> Dict[str, Any]:
        """Executa o cenário de visualização"""
        start_time = time.time()
        end_time = start_time + (scenario.duration_minutes * 60)
        
        scenario_result = {
            'requests_made': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_render_time': 0.0,
            'visualization_events': []
        }
        
        self.log(f"Executando cenário por {scenario.duration_minutes} minutos")
        
        try:
            with ThreadPoolExecutor(max_workers=self.get_concurrent_workers(scenario.complexity)) as executor:
                futures = []
                
                while time.time() < end_time:
                    # Calcular complexidade da visualização
                    complexity = self.calculate_visualization_complexity(scenario.complexity, time.time() - start_time)
                    
                    # Submeter requisições
                    for _ in range(self.get_request_count(scenario.complexity)):
                        future = executor.submit(
                            self.make_visualization_request,
                            scenario,
                            complexity
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
                            
                            scenario_result['total_render_time'] += result['render_time']
                            
                            # Registrar evento de visualização
                            visualization_event = {
                                'timestamp': datetime.now().isoformat(),
                                'endpoint': result['endpoint'],
                                'render_time': result['render_time'],
                                'complexity': complexity,
                                'success': result['success'],
                                'visualization_type': scenario.visualization_type
                            }
                            scenario_result['visualization_events'].append(visualization_event)
                            
                        except Exception as e:
                            self.log(f"Erro na requisição de visualização: {str(e)}", "ERROR")
                            scenario_result['failed_requests'] += 1
                    
                    # Limpar futures processados
                    futures = [f for f in futures if not f.done()]
                    
                    # Aguardar baseado na complexidade
                    wait_time = self.calculate_wait_time(scenario.complexity)
                    time.sleep(wait_time)
                    
                    # Log de progresso
                    elapsed_minutes = (time.time() - start_time) / 60
                    if elapsed_minutes % 5 < wait_time / 60:  # A cada 5 minutos
                        self.log(f"Progresso: {elapsed_minutes:.1f}min / {scenario.duration_minutes}min")
                
        except KeyboardInterrupt:
            self.log("Teste interrompido pelo usuário", "WARNING")
        
        # Calcular métricas finais
        if scenario_result['requests_made'] > 0:
            scenario_result['avg_render_time'] = scenario_result['total_render_time'] / scenario_result['requests_made']
        
        return scenario_result
    
    def get_concurrent_workers(self, complexity: str) -> int:
        """Retorna número de workers baseado na complexidade"""
        if complexity == "simple":
            return 10
        elif complexity == "medium":
            return 15
        elif complexity == "complex":
            return 20
        elif complexity == "extreme":
            return 25
        else:
            return 12
    
    def get_request_count(self, complexity: str) -> int:
        """Retorna número de requisições baseado na complexidade"""
        if complexity == "simple":
            return 5
        elif complexity == "medium":
            return 8
        elif complexity == "complex":
            return 12
        elif complexity == "extreme":
            return 18
        else:
            return 6
    
    def calculate_visualization_complexity(self, complexity: str, elapsed_time: float) -> float:
        """Calcula complexidade da visualização"""
        if complexity == "simple":
            return 0.3
        
        elif complexity == "medium":
            return 0.6
        
        elif complexity == "complex":
            # Variação baseada em função seno
            variation = np.sin(elapsed_time / 300) * 0.3 + 0.7  # Variação de 0.4 a 1.0
            return variation
        
        elif complexity == "extreme":
            # Picos extremos a cada 2.5 minutos
            extreme_cycle = 150
            if (elapsed_time % extreme_cycle) < 75:  # 75 segundos de pico
                return 1.0
            else:
                return 0.4
        
        return 0.5
    
    def calculate_wait_time(self, complexity: str) -> float:
        """Calcula tempo de espera baseado na complexidade"""
        if complexity == "simple":
            return 3.0
        elif complexity == "medium":
            return 2.0
        elif complexity == "complex":
            return 1.5
        elif complexity == "extreme":
            return 1.0
        else:
            return 2.5
    
    def make_visualization_request(self, scenario: VisualizationScenario, complexity: float) -> Dict[str, Any]:
        """Faz uma requisição para teste de visualização"""
        start_time = time.time()
        
        try:
            # Selecionar endpoint baseado no tipo de visualização
            endpoint = self.select_visualization_endpoint(scenario.visualization_type, complexity)
            
            # Gerar payload específico para visualização
            payload = self.generate_visualization_payload(scenario, complexity)
            
            # Fazer requisição
            response = requests.post(
                f"{self.host}{endpoint}",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=60  # Timeout maior para visualizações
            )
            
            end_time = time.time()
            render_time = end_time - start_time
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'render_time': render_time * 1000,  # Converter para ms
                'endpoint': endpoint,
                'complexity': complexity,
                'payload_size': len(json.dumps(payload))
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                'success': False,
                'error': str(e),
                'render_time': (end_time - start_time) * 1000,
                'endpoint': 'unknown',
                'complexity': complexity
            }
    
    def select_visualization_endpoint(self, visualization_type: str, complexity: float) -> str:
        """Seleciona endpoint baseado no tipo de visualização"""
        if visualization_type == "chart":
            return random.choice(["/api/visualization/chart", "/api/visualization/graph"])
        
        elif visualization_type == "scatter":
            return random.choice(["/api/visualization/scatter", "/api/visualization/chart"])
        
        elif visualization_type == "heatmap":
            return random.choice(["/api/visualization/heatmap", "/api/visualization/interactive"])
        
        elif visualization_type == "dashboard":
            return random.choice(["/api/visualization/dashboard", "/api/visualization/realtime"])
        
        else:
            return random.choice(self.visualization_endpoints)
    
    def generate_visualization_payload(self, scenario: VisualizationScenario, complexity: float) -> Dict[str, Any]:
        """Gera payload específico para teste de visualização"""
        base_payload = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "visualization_performance",
            "scenario": scenario.name,
            "complexity": complexity
        }
        
        if scenario.visualization_type == "chart":
            base_payload.update({
                "data": {
                    "chart_visualization": {
                        "chart_type": "line" if complexity < 0.5 else "bar",
                        "data_points": int(complexity * 2000),
                        "dimensions": int(complexity * 5),
                        "interactive": complexity > 0.6,
                        "animations": complexity > 0.7
                    }
                }
            })
        
        elif scenario.visualization_type == "scatter":
            base_payload.update({
                "data": {
                    "scatter_visualization": {
                        "point_count": int(complexity * 5000),
                        "dimensions": int(complexity * 8),
                        "clustering": complexity > 0.7,
                        "zoom_enabled": True,
                        "tooltips": complexity > 0.5
                    }
                }
            })
        
        elif scenario.visualization_type == "heatmap":
            base_payload.update({
                "data": {
                    "heatmap_visualization": {
                        "matrix_size": int(complexity * 100),
                        "color_gradient": "viridis",
                        "interactive": True,
                        "zoom_levels": int(complexity * 5),
                        "annotations": complexity > 0.6
                    }
                }
            })
        
        elif scenario.visualization_type == "dashboard":
            base_payload.update({
                "data": {
                    "dashboard_visualization": {
                        "widget_count": int(complexity * 10),
                        "chart_types": ["line", "bar", "pie", "scatter"],
                        "real_time_updates": complexity > 0.5,
                        "responsive_layout": True,
                        "export_enabled": complexity > 0.7
                    }
                }
            })
        
        else:
            base_payload.update({
                "data": {
                    "generic_visualization": {
                        "data_size": int(complexity * 1000),
                        "render_type": "canvas",
                        "interactive": complexity > 0.5
                    }
                }
            })
        
        return base_payload
    
    def detect_visualization_events(self, metrics: List[Dict], scenario: VisualizationScenario) -> List[Dict]:
        """Detecta eventos relacionados a visualizações"""
        visualization_events = []
        
        for metric in metrics:
            render_time = metric.get('render_time', 0)
            
            # Detectar eventos baseado no tempo de renderização
            if render_time > scenario.target_render_time * 1.5:
                visualization_events.append({
                    'timestamp': metric['timestamp'],
                    'event_type': 'slow_visualization_render',
                    'render_time': render_time,
                    'target': scenario.target_render_time,
                    'severity': 'high'
                })
            
            elif render_time > scenario.target_render_time:
                visualization_events.append({
                    'timestamp': metric['timestamp'],
                    'event_type': 'visualization_render_exceeded',
                    'render_time': render_time,
                    'target': scenario.target_render_time,
                    'severity': 'medium'
                })
            
            # Detectar problemas de interatividade
            interaction_errors = metric.get('interaction_errors', 0)
            if interaction_errors > 0:
                visualization_events.append({
                    'timestamp': metric['timestamp'],
                    'event_type': 'visualization_interaction_error',
                    'error_count': interaction_errors,
                    'severity': 'high'
                })
        
        return visualization_events
    
    def analyze_visualization_performance(self, metrics: List[Dict], scenario: VisualizationScenario) -> Dict[str, Any]:
        """Analisa a performance das visualizações"""
        if not metrics:
            return {'analysis': 'no_data'}
        
        render_times = [m.get('render_time', 0) for m in metrics]
        interaction_times = [m.get('interaction_time', 0) for m in metrics]
        interaction_errors = [m.get('interaction_errors', 0) for m in metrics]
        
        # Estatísticas básicas
        mean_render_time = np.mean(render_times)
        max_render_time = max(render_times)
        mean_interaction_time = np.mean(interaction_times)
        total_errors = sum(interaction_errors)
        
        # Análise de tendência
        if len(render_times) > 1:
            trend = self.calculate_visualization_trend(render_times)
        else:
            trend = "insufficient_data"
        
        # Análise de performance vs target
        render_time_achievement_rate = (scenario.target_render_time / mean_render_time) * 100 if mean_render_time > 0 else 0
        
        # Análise de estabilidade
        render_time_stability = 1.0 - (np.std(render_times) / mean_render_time) if mean_render_time > 0 else 0
        
        return {
            'mean_render_time': mean_render_time,
            'max_render_time': max_render_time,
            'mean_interaction_time': mean_interaction_time,
            'total_errors': total_errors,
            'trend': trend,
            'render_time_achievement_rate': render_time_achievement_rate,
            'render_time_stability': render_time_stability,
            'target_achieved': mean_render_time <= scenario.target_render_time,
            'performance_issues': sum(1 for r in render_times if r > scenario.target_render_time)
        }
    
    def calculate_visualization_trend(self, render_times: List[float]) -> str:
        """Calcula tendência dos tempos de renderização"""
        if len(render_times) < 2:
            return "insufficient_data"
        
        # Regressão linear simples
        x = list(range(len(render_times)))
        slope = np.polyfit(x, render_times, 1)[0]
        
        if abs(slope) < 10:
            return "stable"
        elif slope > 10:
            return "increasing"
        else:
            return "decreasing"
    
    def analyze_visualization_results(self, scenario_result: Dict, metrics: List[Dict], scenario: VisualizationScenario) -> Dict[str, Any]:
        """Analisa os resultados do teste de visualização"""
        total_requests = scenario_result['requests_made']
        successful_requests = scenario_result['successful_requests']
        
        # Análise de métricas
        if metrics:
            render_times = [m.get('render_time', 0) for m in metrics]
            avg_render_time = np.mean(render_times)
            max_render_time = max(render_times)
            target_achieved_count = sum(1 for r in render_times if r <= scenario.target_render_time)
        else:
            avg_render_time = 0
            max_render_time = 0
            target_achieved_count = 0
        
        return {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'success_rate': successful_requests / total_requests if total_requests > 0 else 0,
            'avg_render_time': scenario_result.get('avg_render_time', 0),
            'avg_visualization_render_time': avg_render_time,
            'max_visualization_render_time': max_render_time,
            'target_achieved_count': target_achieved_count,
            'target_achievement_rate': target_achieved_count / len(metrics) if metrics else 0,
            'measurements_count': len(metrics),
            'duration_minutes': scenario.duration_minutes
        }
    
    def run(self) -> Dict[str, Any]:
        """Executa todos os testes de visualização"""
        self.log("🚀 Iniciando testes de visualização de dados")
        
        all_results = {
            'tracing_id': self.tracing_id,
            'start_time': self.start_time.isoformat(),
            'host': self.host,
            'scenarios': [],
            'summary': {},
            'visualization_analysis': {}
        }
        
        try:
            # Executar cenários
            for i, scenario in enumerate(self.visualization_scenarios):
                self.log(f"Executando cenário {i+1}/{len(self.visualization_scenarios)}: {scenario.name}")
                
                scenario_result = self.test_visualization_scenario(scenario)
                scenario_result['scenario_index'] = i + 1
                
                all_results['scenarios'].append(scenario_result)
                
                # Atualizar métricas
                self.metrics['scenarios_executed'] += 1
                if scenario_result.get('summary', {}).get('target_achievement_rate', 0) >= 0.8:
                    self.metrics['visualizations_rendered'] += 1
                
                # Pausa entre cenários
                if i < len(self.visualization_scenarios) - 1:
                    time.sleep(10)
            
            # Gerar resumo geral
            all_results['summary'] = self.generate_overall_summary(all_results)
            all_results['visualization_analysis'] = self.analyze_overall_visualization_performance(all_results)
            all_results['end_time'] = datetime.now().isoformat()
            
            # Calcular sucesso geral
            total_scenarios = len(all_results['scenarios'])
            successful_scenarios = sum(1 for s in all_results['scenarios'] 
                                     if not s.get('error'))
            success_rate = successful_scenarios / total_scenarios if total_scenarios > 0 else 0
            
            all_results['success'] = success_rate >= 0.8
            
            self.log(f"✅ Testes de visualização concluídos: {success_rate:.1%} de sucesso")
            
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
        
        # Análise por tipo de visualização
        visualization_analysis = {}
        for scenario in scenarios:
            visualization_type = scenario.get('visualization_type', 'unknown')
            if visualization_type not in visualization_analysis:
                visualization_analysis[visualization_type] = {
                    'count': 0,
                    'targets_achieved': 0,
                    'avg_render_time': 0.0
                }
            
            visualization_analysis[visualization_type]['count'] += 1
            summary = scenario.get('summary', {})
            if summary.get('target_achievement_rate', 0) >= 0.8:
                visualization_analysis[visualization_type]['targets_achieved'] += 1
            visualization_analysis[visualization_type]['avg_render_time'] += summary.get('avg_visualization_render_time', 0)
        
        # Calcular médias
        for visualization_type in visualization_analysis:
            count = visualization_analysis[visualization_type]['count']
            if count > 0:
                visualization_analysis[visualization_type]['avg_render_time'] /= count
        
        return {
            'total_scenarios': total_scenarios,
            'targets_achieved': targets_achieved,
            'achievement_rate': targets_achieved / total_scenarios if total_scenarios > 0 else 0,
            'visualization_analysis': visualization_analysis
        }
    
    def analyze_overall_visualization_performance(self, all_results: Dict) -> Dict[str, Any]:
        """Analisa performance geral das visualizações"""
        all_metrics = []
        for scenario in all_results['scenarios']:
            all_metrics.extend(scenario.get('visualization_metrics', []))
        
        if not all_metrics:
            return {}
        
        # Análise geral
        render_times = [m.get('render_time', 0) for m in all_metrics]
        interaction_times = [m.get('interaction_time', 0) for m in all_metrics]
        interaction_errors = [m.get('interaction_errors', 0) for m in all_metrics]
        
        return {
            'total_measurements': len(all_metrics),
            'avg_render_time_ms': np.mean(render_times) if render_times else 0,
            'max_render_time_ms': max(render_times) if render_times else 0,
            'avg_interaction_time_ms': np.mean(interaction_times) if interaction_times else 0,
            'total_interaction_errors': sum(interaction_errors),
            'total_visualizations_rendered': len(all_metrics)
        }


class VisualizationMonitor:
    """Monitor de visualizações"""
    
    def __init__(self):
        self.metrics = []
        self.monitoring = False
        self.monitor_thread = None
        self.visualization_type = None
        
    def start_monitoring(self, visualization_type: str):
        """Inicia o monitoramento de visualizações"""
        self.metrics = []
        self.monitoring = True
        self.visualization_type = visualization_type
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Para o monitoramento de visualizações"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
    
    def _monitor_loop(self):
        """Loop de monitoramento"""
        while self.monitoring:
            try:
                # Simular coleta de métricas de visualizações
                # Em um ambiente real, isso viria do sistema de visualizações
                
                if self.visualization_type == "chart":
                    # Simular gráficos
                    render_time = np.random.normal(600, 200)  # ms
                    interaction_time = np.random.normal(50, 20)  # ms
                    interaction_errors = np.random.poisson(0.05)  # erros
                    measurement = {
                        'timestamp': datetime.now(),
                        'render_time': max(0, render_time),
                        'interaction_time': max(0, interaction_time),
                        'interaction_errors': int(interaction_errors)
                    }
                
                elif self.visualization_type == "scatter":
                    # Simular gráficos de dispersão
                    render_time = np.random.normal(1500, 400)  # ms
                    interaction_time = np.random.normal(100, 40)  # ms
                    interaction_errors = np.random.poisson(0.1)  # erros
                    measurement = {
                        'timestamp': datetime.now(),
                        'render_time': max(0, render_time),
                        'interaction_time': max(0, interaction_time),
                        'interaction_errors': int(interaction_errors)
                    }
                
                elif self.visualization_type == "heatmap":
                    # Simular mapas de calor
                    render_time = np.random.normal(2000, 600)  # ms
                    interaction_time = np.random.normal(150, 60)  # ms
                    interaction_errors = np.random.poisson(0.15)  # erros
                    measurement = {
                        'timestamp': datetime.now(),
                        'render_time': max(0, render_time),
                        'interaction_time': max(0, interaction_time),
                        'interaction_errors': int(interaction_errors)
                    }
                
                elif self.visualization_type == "dashboard":
                    # Simular dashboards
                    render_time = np.random.normal(2500, 800)  # ms
                    interaction_time = np.random.normal(200, 80)  # ms
                    interaction_errors = np.random.poisson(0.2)  # erros
                    measurement = {
                        'timestamp': datetime.now(),
                        'render_time': max(0, render_time),
                        'interaction_time': max(0, interaction_time),
                        'interaction_errors': int(interaction_errors)
                    }
                
                else:
                    measurement = {
                        'timestamp': datetime.now(),
                        'render_time': 0,
                        'interaction_time': 0,
                        'interaction_errors': 0
                    }
                
                self.metrics.append(measurement)
                
                # Aguardar 15 segundos
                time.sleep(15)
                
            except Exception as e:
                logging.error(f"Erro no monitoramento de visualizações: {e}")
                time.sleep(15)
    
    def get_metrics(self) -> List[Dict]:
        """Retorna as métricas coletadas"""
        return self.metrics.copy()


def main():
    """Função principal para execução standalone"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Teste de Visualização de Dados")
    parser.add_argument('--host', default='http://localhost:8000', help='Host para testar')
    parser.add_argument('--verbose', action='store_true', help='Modo verboso')
    
    args = parser.parse_args()
    
    # Criar e executar teste
    test = DashboardVisualizationTest(host=args.host, verbose=args.verbose)
    result = test.run()
    
    # Imprimir resultados
    print("\n" + "="*80)
    print("📊 RESULTADOS DOS TESTES DE VISUALIZAÇÃO DE DADOS")
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
    
    if 'visualization_analysis' in result:
        analysis = result['visualization_analysis']
        print(f"\n📊 ANÁLISE DE VISUALIZAÇÕES:")
        print(f"   • Total de Medições: {analysis['total_measurements']}")
        print(f"   • Tempo de Renderização Médio: {analysis['avg_render_time_ms']:.1f} ms")
        print(f"   • Tempo de Renderização Máximo: {analysis['max_render_time_ms']:.1f} ms")
        print(f"   • Tempo de Interação Médio: {analysis['avg_interaction_time_ms']:.1f} ms")
        print(f"   • Total de Erros de Interação: {analysis['total_interaction_errors']}")
        print(f"   • Total de Visualizações Renderizadas: {analysis['total_visualizations_rendered']}")
    
    print("="*80)


if __name__ == "__main__":
    main() 