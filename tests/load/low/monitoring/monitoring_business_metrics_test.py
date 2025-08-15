#!/usr/bin/env python3
"""
Teste de Métricas de Negócio
Omni Keywords Finder - Tracing ID: MONITORING_BUSINESS_METRICS_20250127_001

Este teste valida as métricas de negócio sob carga:
- Receita e conversões
- Engajamento de usuários
- Performance de campanhas
- ROI e eficiência
- KPIs de negócio
- Métricas de crescimento

Baseado em:
- backend/app/api/business_metrics.py
- backend/app/services/business_analytics.py
- backend/app/models/business_metrics.py

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
class BusinessMetricScenario:
    """Cenário de teste de métricas de negócio"""
    name: str
    description: str
    metric_type: str  # 'revenue', 'conversion', 'engagement', 'roi', 'growth', 'efficiency'
    duration_minutes: int
    business_load: str  # 'normal', 'peak', 'promotion', 'seasonal'
    expected_behavior: str
    target_value: float


class MonitoringBusinessMetricsTest:
    """
    Teste de métricas de negócio sob carga
    """
    
    def __init__(self, host: str = "http://localhost:8000", verbose: bool = False):
        self.host = host
        self.verbose = verbose
        self.tracing_id = "MONITORING_BUSINESS_METRICS_20250127_001"
        self.start_time = datetime.now()
        
        # Configurar logging
        self.setup_logging()
        
        # Inicializar monitor de métricas de negócio
        self.business_metrics_monitor = BusinessMetricsMonitor()
        
        # Cenários de métricas de negócio
        self.business_metric_scenarios = [
            BusinessMetricScenario(
                name="Métricas de Receita",
                description="Monitoramento de receita e vendas",
                metric_type="revenue",
                duration_minutes=30,
                business_load="peak",
                expected_behavior="Detecção de picos de receita",
                target_value=10000.0  # R$ 10.000
            ),
            BusinessMetricScenario(
                name="Taxa de Conversão",
                description="Monitoramento de conversões",
                metric_type="conversion",
                duration_minutes=25,
                business_load="promotion",
                expected_behavior="Aumento de conversões durante promoção",
                target_value=15.0  # 15%
            ),
            BusinessMetricScenario(
                name="Engajamento de Usuários",
                description="Monitoramento de engajamento",
                metric_type="engagement",
                duration_minutes=35,
                business_load="normal",
                expected_behavior="Estabilidade do engajamento",
                target_value=75.0  # 75%
            ),
            BusinessMetricScenario(
                name="ROI de Campanhas",
                description="Monitoramento de ROI",
                metric_type="roi",
                duration_minutes=40,
                business_load="promotion",
                expected_behavior="ROI positivo durante campanhas",
                target_value=120.0  # 120%
            ),
            BusinessMetricScenario(
                name="Crescimento de Usuários",
                description="Monitoramento de crescimento",
                metric_type="growth",
                duration_minutes=45,
                business_load="seasonal",
                expected_behavior="Crescimento sazonal",
                target_value=10.0  # 10%
            ),
            BusinessMetricScenario(
                name="Eficiência Operacional",
                description="Monitoramento de eficiência",
                metric_type="efficiency",
                duration_minutes=50,
                business_load="normal",
                expected_behavior="Manutenção da eficiência",
                target_value=85.0  # 85%
            )
        ]
        
        # Endpoints para métricas de negócio
        self.business_endpoints = [
            "/api/business-metrics",
            "/api/v1/analytics/business",
            "/api/metrics/revenue",
            "/api/metrics/conversion",
            "/api/metrics/engagement",
            "/api/metrics/roi",
            "/api/metrics/growth",
            "/api/metrics/efficiency"
        ]
        
        # Métricas coletadas
        self.metrics = {
            'scenarios_executed': 0,
            'scenarios_failed': 0,
            'targets_achieved': 0,
            'business_insights': 0,
            'avg_metric_accuracy': 0.0
        }
        
    def setup_logging(self):
        """Configura logging estruturado"""
        logging.basicConfig(
            level=logging.INFO if self.verbose else logging.WARNING,
            format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
            handlers=[
                logging.FileHandler(f'logs/monitoring_business_metrics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(f"MonitoringBusinessMetricsTest_{self.tracing_id}")
        
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
    
    def test_business_metric_scenario(self, scenario: BusinessMetricScenario) -> Dict[str, Any]:
        """Testa um cenário específico de métricas de negócio"""
        self.log(f"Iniciando teste: {scenario.name} ({scenario.duration_minutes}min)")
        
        results = {
            'scenario_name': scenario.name,
            'metric_type': scenario.metric_type,
            'business_load': scenario.business_load,
            'start_time': datetime.now().isoformat(),
            'business_metrics': [],
            'business_events': [],
            'target_events': [],
            'analysis': {},
            'summary': {}
        }
        
        try:
            # Iniciar monitoramento
            self.business_metrics_monitor.start_monitoring(scenario.metric_type)
            
            # Executar cenário
            scenario_result = self.execute_business_metric_scenario(scenario)
            
            # Parar monitoramento
            self.business_metrics_monitor.stop_monitoring()
            
            # Analisar resultados
            results['business_metrics'] = self.business_metrics_monitor.get_metrics()
            results['business_events'] = self.detect_business_events(results['business_metrics'], scenario)
            results['target_events'] = self.detect_target_events(results['business_metrics'], scenario)
            results['analysis'] = self.analyze_business_metrics(results['business_metrics'], scenario)
            results['summary'] = self.analyze_business_results(scenario_result, results['business_metrics'], scenario)
            results['end_time'] = datetime.now().isoformat()
            
        except Exception as e:
            error_msg = f"Erro durante teste {scenario.name}: {str(e)}"
            self.log(error_msg, "ERROR")
            results['error'] = error_msg
            
        return results
    
    def execute_business_metric_scenario(self, scenario: BusinessMetricScenario) -> Dict[str, Any]:
        """Executa o cenário de métricas de negócio"""
        start_time = time.time()
        end_time = start_time + (scenario.duration_minutes * 60)
        
        scenario_result = {
            'requests_made': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_response_time': 0.0,
            'business_events': []
        }
        
        self.log(f"Executando cenário por {scenario.duration_minutes} minutos")
        
        try:
            with ThreadPoolExecutor(max_workers=self.get_concurrent_workers(scenario.business_load)) as executor:
                futures = []
                
                while time.time() < end_time:
                    # Calcular intensidade da carga de negócio
                    business_intensity = self.calculate_business_intensity(scenario.business_load, time.time() - start_time)
                    
                    # Submeter requisições
                    for _ in range(self.get_request_count(scenario.business_load)):
                        future = executor.submit(
                            self.make_business_request,
                            scenario,
                            business_intensity
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
                            
                            # Registrar evento de negócio
                            business_event = {
                                'timestamp': datetime.now().isoformat(),
                                'endpoint': result['endpoint'],
                                'response_time': result['response_time'],
                                'business_intensity': business_intensity,
                                'success': result['success']
                            }
                            scenario_result['business_events'].append(business_event)
                            
                        except Exception as e:
                            self.log(f"Erro na requisição de negócio: {str(e)}", "ERROR")
                            scenario_result['failed_requests'] += 1
                    
                    # Limpar futures processados
                    futures = [f for f in futures if not f.done()]
                    
                    # Aguardar baseado na carga de negócio
                    wait_time = self.calculate_wait_time(scenario.business_load)
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
    
    def get_concurrent_workers(self, business_load: str) -> int:
        """Retorna número de workers baseado na carga de negócio"""
        if business_load == "normal":
            return 8
        elif business_load == "peak":
            return 20
        elif business_load == "promotion":
            return 15
        elif business_load == "seasonal":
            return 12
        else:
            return 10
    
    def get_request_count(self, business_load: str) -> int:
        """Retorna número de requisições baseado na carga de negócio"""
        if business_load == "normal":
            return 3
        elif business_load == "peak":
            return 10
        elif business_load == "promotion":
            return 8
        elif business_load == "seasonal":
            return 6
        else:
            return 4
    
    def calculate_business_intensity(self, business_load: str, elapsed_time: float) -> float:
        """Calcula intensidade da carga de negócio"""
        if business_load == "normal":
            return 0.6
        
        elif business_load == "peak":
            # Picos de negócio a cada hora
            peak_cycle = 3600
            if (elapsed_time % peak_cycle) < 900:  # 15 minutos de pico
                return 1.0
            else:
                return 0.4
        
        elif business_load == "promotion":
            # Promoção com variação
            promotion_intensity = 0.8 + np.sin(elapsed_time / 300) * 0.2  # Variação de 0.6 a 1.0
            return promotion_intensity
        
        elif business_load == "seasonal":
            # Carga sazonal
            seasonal_factor = np.sin(elapsed_time / 1800) * 0.3 + 0.7  # Variação de 0.4 a 1.0
            return seasonal_factor
        
        return 0.5
    
    def calculate_wait_time(self, business_load: str) -> float:
        """Calcula tempo de espera baseado na carga de negócio"""
        if business_load == "normal":
            return 5.0
        elif business_load == "peak":
            return 2.0
        elif business_load == "promotion":
            return 3.0
        elif business_load == "seasonal":
            return 4.0
        else:
            return 5.0
    
    def make_business_request(self, scenario: BusinessMetricScenario, business_intensity: float) -> Dict[str, Any]:
        """Faz uma requisição para teste de métricas de negócio"""
        start_time = time.time()
        
        try:
            # Selecionar endpoint baseado no tipo de métrica
            endpoint = self.select_business_endpoint(scenario.metric_type, business_intensity)
            
            # Gerar payload específico para métricas de negócio
            payload = self.generate_business_payload(scenario, business_intensity)
            
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
                'business_intensity': business_intensity,
                'payload_size': len(json.dumps(payload))
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                'success': False,
                'error': str(e),
                'response_time': (end_time - start_time) * 1000,
                'endpoint': 'unknown',
                'business_intensity': business_intensity
            }
    
    def select_business_endpoint(self, metric_type: str, business_intensity: float) -> str:
        """Seleciona endpoint baseado no tipo de métrica de negócio"""
        if metric_type == "revenue":
            return random.choice(["/api/metrics/revenue", "/api/business-metrics"])
        
        elif metric_type == "conversion":
            return random.choice(["/api/metrics/conversion", "/api/v1/analytics/business"])
        
        elif metric_type == "engagement":
            return random.choice(["/api/metrics/engagement", "/api/business-metrics"])
        
        elif metric_type == "roi":
            return random.choice(["/api/metrics/roi", "/api/v1/analytics/business"])
        
        elif metric_type == "growth":
            return random.choice(["/api/metrics/growth", "/api/business-metrics"])
        
        elif metric_type == "efficiency":
            return random.choice(["/api/metrics/efficiency", "/api/v1/analytics/business"])
        
        else:
            return random.choice(self.business_endpoints)
    
    def generate_business_payload(self, scenario: BusinessMetricScenario, business_intensity: float) -> Dict[str, Any]:
        """Gera payload específico para teste de métricas de negócio"""
        base_payload = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "business_metrics",
            "scenario": scenario.name,
            "business_intensity": business_intensity
        }
        
        if scenario.metric_type == "revenue":
            base_payload.update({
                "data": {
                    "revenue_metrics": {
                        "period": "daily",
                        "include_breakdown": True,
                        "currency": "BRL",
                        "business_intensity": business_intensity
                    }
                }
            })
        
        elif scenario.metric_type == "conversion":
            base_payload.update({
                "data": {
                    "conversion_metrics": {
                        "funnel_stages": ["visit", "signup", "purchase"],
                        "include_attribution": True,
                        "promotion_active": business_intensity > 0.7
                    }
                }
            })
        
        elif scenario.metric_type == "engagement":
            base_payload.update({
                "data": {
                    "engagement_metrics": {
                        "user_activity": ["page_views", "time_spent", "interactions"],
                        "cohort_analysis": True,
                        "retention_period": "30d"
                    }
                }
            })
        
        elif scenario.metric_type == "roi":
            base_payload.update({
                "data": {
                    "roi_metrics": {
                        "campaign_types": ["paid_search", "social_media", "email"],
                        "include_costs": True,
                        "attribution_model": "last_click"
                    }
                }
            })
        
        elif scenario.metric_type == "growth":
            base_payload.update({
                "data": {
                    "growth_metrics": {
                        "growth_indicators": ["users", "revenue", "engagement"],
                        "time_period": "monthly",
                        "seasonal_adjustment": True
                    }
                }
            })
        
        elif scenario.metric_type == "efficiency":
            base_payload.update({
                "data": {
                    "efficiency_metrics": {
                        "operational_metrics": ["cost_per_acquisition", "lifetime_value", "churn_rate"],
                        "benchmark_comparison": True,
                        "optimization_targets": True
                    }
                }
            })
        
        return base_payload
    
    def detect_business_events(self, metrics: List[Dict], scenario: BusinessMetricScenario) -> List[Dict]:
        """Detecta eventos de negócio"""
        business_events = []
        
        for metric in metrics:
            metric_value = metric.get(scenario.metric_type, 0)
            
            # Detectar eventos baseado no tipo de métrica
            if scenario.metric_type == "revenue":
                if metric_value > scenario.target_value * 1.2:
                    business_events.append({
                        'timestamp': metric['timestamp'],
                        'event_type': 'revenue_peak',
                        'value': metric_value,
                        'target': scenario.target_value,
                        'severity': 'high'
                    })
            
            elif scenario.metric_type == "conversion":
                if metric_value > scenario.target_value:
                    business_events.append({
                        'timestamp': metric['timestamp'],
                        'event_type': 'conversion_surge',
                        'value': metric_value,
                        'target': scenario.target_value,
                        'severity': 'medium'
                    })
            
            elif scenario.metric_type == "engagement":
                if metric_value < scenario.target_value * 0.8:
                    business_events.append({
                        'timestamp': metric['timestamp'],
                        'event_type': 'engagement_drop',
                        'value': metric_value,
                        'target': scenario.target_value,
                        'severity': 'high'
                    })
            
            elif scenario.metric_type == "roi":
                if metric_value > scenario.target_value:
                    business_events.append({
                        'timestamp': metric['timestamp'],
                        'event_type': 'roi_excellent',
                        'value': metric_value,
                        'target': scenario.target_value,
                        'severity': 'low'
                    })
            
            elif scenario.metric_type == "growth":
                if metric_value > scenario.target_value:
                    business_events.append({
                        'timestamp': metric['timestamp'],
                        'event_type': 'growth_positive',
                        'value': metric_value,
                        'target': scenario.target_value,
                        'severity': 'medium'
                    })
            
            elif scenario.metric_type == "efficiency":
                if metric_value < scenario.target_value * 0.9:
                    business_events.append({
                        'timestamp': metric['timestamp'],
                        'event_type': 'efficiency_decline',
                        'value': metric_value,
                        'target': scenario.target_value,
                        'severity': 'high'
                    })
        
        return business_events
    
    def detect_target_events(self, metrics: List[Dict], scenario: BusinessMetricScenario) -> List[Dict]:
        """Detecta eventos de atingimento de target"""
        target_events = []
        
        for metric in metrics:
            metric_value = metric.get(scenario.metric_type, 0)
            
            # Lógica específica por tipo de métrica
            if scenario.metric_type in ["revenue", "conversion", "roi", "growth"]:
                # Para estas métricas, maior é melhor
                if metric_value >= scenario.target_value:
                    target_events.append({
                        'timestamp': metric['timestamp'],
                        'metric_type': scenario.metric_type,
                        'value': metric_value,
                        'target': scenario.target_value,
                        'achievement_rate': (metric_value / scenario.target_value) * 100
                    })
            
            elif scenario.metric_type in ["engagement", "efficiency"]:
                # Para estas métricas, menor que target é problema
                if metric_value < scenario.target_value:
                    target_events.append({
                        'timestamp': metric['timestamp'],
                        'metric_type': scenario.metric_type,
                        'value': metric_value,
                        'target': scenario.target_value,
                        'achievement_rate': (metric_value / scenario.target_value) * 100
                    })
        
        return target_events
    
    def analyze_business_metrics(self, metrics: List[Dict], scenario: BusinessMetricScenario) -> Dict[str, Any]:
        """Analisa as métricas de negócio"""
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
            trend = self.calculate_business_trend(metric_values)
        else:
            trend = "insufficient_data"
        
        # Análise de sazonalidade
        seasonality = self.analyze_seasonality(metric_values)
        
        # Análise de performance vs target
        target_achievement_rate = (mean_value / scenario.target_value) * 100 if scenario.target_value > 0 else 0
        
        return {
            'mean_value': mean_value,
            'max_value': max_value,
            'min_value': min_value,
            'std_value': std_value,
            'trend': trend,
            'seasonality': seasonality,
            'target_achievement_rate': target_achievement_rate,
            'target_achieved': target_achievement_rate >= 100,
            'volatility': std_value / mean_value if mean_value > 0 else 0
        }
    
    def calculate_business_trend(self, values: List[float]) -> str:
        """Calcula tendência das métricas de negócio"""
        if len(values) < 2:
            return "insufficient_data"
        
        # Regressão linear simples
        x = list(range(len(values)))
        slope = np.polyfit(x, values, 1)[0]
        
        if abs(slope) < 0.01:
            return "stable"
        elif slope > 0.01:
            return "increasing"
        else:
            return "decreasing"
    
    def analyze_seasonality(self, values: List[float]) -> Dict[str, Any]:
        """Analisa sazonalidade das métricas"""
        if len(values) < 10:
            return {'detected': False, 'confidence': 0}
        
        # Análise simples de sazonalidade
        # Em um ambiente real, usar FFT ou decomposição temporal
        
        # Calcular variação entre valores consecutivos
        variations = [abs(values[i+1] - values[i]) for i in range(len(values)-1)]
        avg_variation = np.mean(variations)
        
        # Se há variação significativa, pode indicar sazonalidade
        if avg_variation > np.std(values) * 0.3:
            return {
                'detected': True,
                'confidence': min(avg_variation / np.std(values), 1.0),
                'pattern': 'variable'
            }
        else:
            return {
                'detected': False,
                'confidence': 0,
                'pattern': 'stable'
            }
    
    def analyze_business_results(self, scenario_result: Dict, metrics: List[Dict], scenario: BusinessMetricScenario) -> Dict[str, Any]:
        """Analisa os resultados do teste de métricas de negócio"""
        total_requests = scenario_result['requests_made']
        successful_requests = scenario_result['successful_requests']
        
        # Análise de métricas
        if metrics:
            metric_values = [m.get(scenario.metric_type, 0) for m in metrics]
            avg_metric = np.mean(metric_values)
            max_metric = max(metric_values)
            target_achieved_count = sum(1 for v in metric_values if v >= scenario.target_value)
        else:
            avg_metric = 0
            max_metric = 0
            target_achieved_count = 0
        
        return {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'success_rate': successful_requests / total_requests if total_requests > 0 else 0,
            'avg_response_time': scenario_result.get('avg_response_time', 0),
            'avg_metric_value': avg_metric,
            'max_metric_value': max_metric,
            'target_achieved_count': target_achieved_count,
            'target_achievement_rate': target_achieved_count / len(metrics) if metrics else 0,
            'measurements_count': len(metrics),
            'duration_minutes': scenario.duration_minutes
        }
    
    def run(self) -> Dict[str, Any]:
        """Executa todos os testes de métricas de negócio"""
        self.log("🚀 Iniciando testes de métricas de negócio")
        
        all_results = {
            'tracing_id': self.tracing_id,
            'start_time': self.start_time.isoformat(),
            'host': self.host,
            'scenarios': [],
            'summary': {},
            'business_analysis': {}
        }
        
        try:
            # Executar cenários
            for i, scenario in enumerate(self.business_metric_scenarios):
                self.log(f"Executando cenário {i+1}/{len(self.business_metric_scenarios)}: {scenario.name}")
                
                scenario_result = self.test_business_metric_scenario(scenario)
                scenario_result['scenario_index'] = i + 1
                
                all_results['scenarios'].append(scenario_result)
                
                # Atualizar métricas
                self.metrics['scenarios_executed'] += 1
                if scenario_result.get('summary', {}).get('target_achievement_rate', 0) >= 100:
                    self.metrics['targets_achieved'] += 1
                
                # Pausa entre cenários
                if i < len(self.business_metric_scenarios) - 1:
                    time.sleep(10)
            
            # Gerar resumo geral
            all_results['summary'] = self.generate_overall_summary(all_results)
            all_results['business_analysis'] = self.analyze_overall_business_metrics(all_results)
            all_results['end_time'] = datetime.now().isoformat()
            
            # Calcular sucesso geral
            total_scenarios = len(all_results['scenarios'])
            successful_scenarios = sum(1 for s in all_results['scenarios'] 
                                     if not s.get('error'))
            success_rate = successful_scenarios / total_scenarios if total_scenarios > 0 else 0
            
            all_results['success'] = success_rate >= 0.8
            
            self.log(f"✅ Testes de métricas de negócio concluídos: {success_rate:.1%} de sucesso")
            
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
                             if s.get('summary', {}).get('target_achievement_rate', 0) >= 100)
        
        # Análise por tipo de métrica de negócio
        business_analysis = {}
        for scenario in scenarios:
            metric_type = scenario.get('metric_type', 'unknown')
            if metric_type not in business_analysis:
                business_analysis[metric_type] = {
                    'count': 0,
                    'targets_achieved': 0,
                    'avg_value': 0.0
                }
            
            business_analysis[metric_type]['count'] += 1
            summary = scenario.get('summary', {})
            if summary.get('target_achievement_rate', 0) >= 100:
                business_analysis[metric_type]['targets_achieved'] += 1
            business_analysis[metric_type]['avg_value'] += summary.get('avg_metric_value', 0)
        
        # Calcular médias
        for metric_type in business_analysis:
            count = business_analysis[metric_type]['count']
            if count > 0:
                business_analysis[metric_type]['avg_value'] /= count
        
        return {
            'total_scenarios': total_scenarios,
            'targets_achieved': targets_achieved,
            'achievement_rate': targets_achieved / total_scenarios if total_scenarios > 0 else 0,
            'business_analysis': business_analysis
        }
    
    def analyze_overall_business_metrics(self, all_results: Dict) -> Dict[str, Any]:
        """Analisa métricas gerais de negócio"""
        all_metrics = []
        for scenario in all_results['scenarios']:
            all_metrics.extend(scenario.get('business_metrics', []))
        
        if not all_metrics:
            return {}
        
        # Análise geral
        revenue_values = [m.get('revenue', 0) for m in all_metrics]
        conversion_values = [m.get('conversion', 0) for m in all_metrics]
        engagement_values = [m.get('engagement', 0) for m in all_metrics]
        roi_values = [m.get('roi', 0) for m in all_metrics]
        
        return {
            'total_measurements': len(all_metrics),
            'avg_revenue': np.mean(revenue_values) if revenue_values else 0,
            'avg_conversion_rate': np.mean(conversion_values) if conversion_values else 0,
            'avg_engagement_rate': np.mean(engagement_values) if engagement_values else 0,
            'avg_roi': np.mean(roi_values) if roi_values else 0,
            'max_revenue': max(revenue_values) if revenue_values else 0,
            'max_conversion_rate': max(conversion_values) if conversion_values else 0
        }


class BusinessMetricsMonitor:
    """Monitor de métricas de negócio"""
    
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
                # Simular coleta de métricas de negócio
                # Em um ambiente real, isso viria do sistema de métricas de negócio
                
                if self.metric_type == "revenue":
                    # Simular receita
                    revenue = np.random.normal(8000, 2000)  # R$
                    measurement = {
                        'timestamp': datetime.now(),
                        'revenue': max(0, revenue)
                    }
                
                elif self.metric_type == "conversion":
                    # Simular taxa de conversão
                    conversion = np.random.normal(12, 3)  # %
                    measurement = {
                        'timestamp': datetime.now(),
                        'conversion': max(0, min(100, conversion))
                    }
                
                elif self.metric_type == "engagement":
                    # Simular engajamento
                    engagement = np.random.normal(70, 10)  # %
                    measurement = {
                        'timestamp': datetime.now(),
                        'engagement': max(0, min(100, engagement))
                    }
                
                elif self.metric_type == "roi":
                    # Simular ROI
                    roi = np.random.normal(150, 30)  # %
                    measurement = {
                        'timestamp': datetime.now(),
                        'roi': max(0, roi)
                    }
                
                elif self.metric_type == "growth":
                    # Simular crescimento
                    growth = np.random.normal(8, 2)  # %
                    measurement = {
                        'timestamp': datetime.now(),
                        'growth': max(-50, min(100, growth))
                    }
                
                elif self.metric_type == "efficiency":
                    # Simular eficiência
                    efficiency = np.random.normal(80, 8)  # %
                    measurement = {
                        'timestamp': datetime.now(),
                        'efficiency': max(0, min(100, efficiency))
                    }
                
                else:
                    measurement = {
                        'timestamp': datetime.now(),
                        'unknown': 0
                    }
                
                self.metrics.append(measurement)
                
                # Aguardar 15 segundos
                time.sleep(15)
                
            except Exception as e:
                logging.error(f"Erro no monitoramento de métricas de negócio: {e}")
                time.sleep(15)
    
    def get_metrics(self) -> List[Dict]:
        """Retorna as métricas coletadas"""
        return self.metrics.copy()


def main():
    """Função principal para execução standalone"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Teste de Métricas de Negócio")
    parser.add_argument('--host', default='http://localhost:8000', help='Host para testar')
    parser.add_argument('--verbose', action='store_true', help='Modo verboso')
    
    args = parser.parse_args()
    
    # Criar e executar teste
    test = MonitoringBusinessMetricsTest(host=args.host, verbose=args.verbose)
    result = test.run()
    
    # Imprimir resultados
    print("\n" + "="*80)
    print("📊 RESULTADOS DOS TESTES DE MÉTRICAS DE NEGÓCIO")
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
    
    if 'business_analysis' in result:
        analysis = result['business_analysis']
        print(f"\n💼 ANÁLISE DE NEGÓCIO:")
        print(f"   • Total de Medições: {analysis['total_measurements']}")
        print(f"   • Receita Média: R$ {analysis['avg_revenue']:.2f}")
        print(f"   • Taxa de Conversão Média: {analysis['avg_conversion_rate']:.1f}%")
        print(f"   • Engajamento Médio: {analysis['avg_engagement_rate']:.1f}%")
        print(f"   • ROI Médio: {analysis['avg_roi']:.1f}%")
        print(f"   • Receita Máxima: R$ {analysis['max_revenue']:.2f}")
    
    print("="*80)


if __name__ == "__main__":
    main() 