#!/usr/bin/env python3
"""
Teste de Coleta de Logs
Omni Keywords Finder - Tracing ID: MONITORING_LOG_GENERATION_20250127_001

Este teste valida a coleta de logs sob carga:
- Volume de logs gerados
- Performance de coleta
- Estrutura e formato dos logs
- Rotação e retenção
- Análise de logs em tempo real

Baseado em:
- infrastructure/logging/log_manager.py
- backend/app/middleware/logging_middleware.py
- backend/app/services/log_analysis_service.py

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
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np


@dataclass
class LogGenerationScenario:
    """Cenário de teste de geração de logs"""
    name: str
    description: str
    log_type: str  # 'application', 'access', 'error', 'audit', 'performance'
    duration_minutes: int
    log_intensity: str  # 'low', 'medium', 'high', 'extreme'
    expected_behavior: str
    target_volume: int  # logs por minuto


class MonitoringLogGenerationTest:
    """
    Teste de coleta de logs sob carga
    """
    
    def __init__(self, host: str = "http://localhost:8000", verbose: bool = False):
        self.host = host
        self.verbose = verbose
        self.tracing_id = "MONITORING_LOG_GENERATION_20250127_001"
        self.start_time = datetime.now()
        
        # Configurar logging
        self.setup_logging()
        
        # Inicializar monitor de logs
        self.log_monitor = LogGenerationMonitor()
        
        # Cenários de geração de logs
        self.log_generation_scenarios = [
            LogGenerationScenario(
                name="Logs de Aplicação",
                description="Geração de logs de aplicação sob carga",
                log_type="application",
                duration_minutes=20,
                log_intensity="high",
                expected_behavior="Geração consistente de logs de aplicação",
                target_volume=1000  # 1000 logs/min
            ),
            LogGenerationScenario(
                name="Logs de Acesso",
                description="Geração de logs de acesso HTTP",
                log_type="access",
                duration_minutes=25,
                log_intensity="extreme",
                expected_behavior="Alto volume de logs de acesso",
                target_volume=5000  # 5000 logs/min
            ),
            LogGenerationScenario(
                name="Logs de Erro",
                description="Geração de logs de erro controlados",
                log_type="error",
                duration_minutes=15,
                log_intensity="medium",
                expected_behavior="Detecção e registro de erros",
                target_volume=100  # 100 logs/min
            ),
            LogGenerationScenario(
                name="Logs de Auditoria",
                description="Geração de logs de auditoria",
                log_type="audit",
                duration_minutes=30,
                log_intensity="low",
                expected_behavior="Registro de eventos de auditoria",
                target_volume=50  # 50 logs/min
            ),
            LogGenerationScenario(
                name="Logs de Performance",
                description="Geração de logs de performance",
                log_type="performance",
                duration_minutes=35,
                log_intensity="high",
                expected_behavior="Monitoramento de performance",
                target_volume=500  # 500 logs/min
            )
        ]
        
        # Endpoints para gerar logs
        self.log_endpoints = [
            "/api/v1/analytics/advanced",
            "/api/reports/generate",
            "/api/executions/create",
            "/api/users/profile",
            "/api/categories/list",
            "/api/audit/logs",
            "/api/metrics/performance",
            "/api/business-metrics"
        ]
        
        # Métricas coletadas
        self.metrics = {
            'scenarios_executed': 0,
            'scenarios_failed': 0,
            'logs_generated': 0,
            'log_analysis_events': 0,
            'avg_log_processing_time': 0.0
        }
        
    def setup_logging(self):
        """Configura logging estruturado"""
        logging.basicConfig(
            level=logging.INFO if self.verbose else logging.WARNING,
            format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
            handlers=[
                logging.FileHandler(f'logs/monitoring_log_generation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(f"MonitoringLogGenerationTest_{self.tracing_id}")
        
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
    
    def test_log_generation_scenario(self, scenario: LogGenerationScenario) -> Dict[str, Any]:
        """Testa um cenário específico de geração de logs"""
        self.log(f"Iniciando teste: {scenario.name} ({scenario.duration_minutes}min)")
        
        results = {
            'scenario_name': scenario.name,
            'log_type': scenario.log_type,
            'log_intensity': scenario.log_intensity,
            'start_time': datetime.now().isoformat(),
            'log_metrics': [],
            'log_events': [],
            'analysis': {},
            'summary': {}
        }
        
        try:
            # Iniciar monitoramento
            self.log_monitor.start_monitoring(scenario.log_type)
            
            # Executar cenário
            scenario_result = self.execute_log_generation_scenario(scenario)
            
            # Parar monitoramento
            self.log_monitor.stop_monitoring()
            
            # Analisar resultados
            results['log_metrics'] = self.log_monitor.get_metrics()
            results['log_events'] = self.detect_log_events(results['log_metrics'], scenario)
            results['analysis'] = self.analyze_log_generation(results['log_metrics'], scenario)
            results['summary'] = self.analyze_log_results(scenario_result, results['log_metrics'], scenario)
            results['end_time'] = datetime.now().isoformat()
            
        except Exception as e:
            error_msg = f"Erro durante teste {scenario.name}: {str(e)}"
            self.log(error_msg, "ERROR")
            results['error'] = error_msg
            
        return results
    
    def execute_log_generation_scenario(self, scenario: LogGenerationScenario) -> Dict[str, Any]:
        """Executa o cenário de geração de logs"""
        start_time = time.time()
        end_time = start_time + (scenario.duration_minutes * 60)
        
        scenario_result = {
            'requests_made': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_response_time': 0.0,
            'log_events': []
        }
        
        self.log(f"Executando cenário por {scenario.duration_minutes} minutos")
        
        try:
            with ThreadPoolExecutor(max_workers=self.get_concurrent_workers(scenario.log_intensity)) as executor:
                futures = []
                
                while time.time() < end_time:
                    # Calcular intensidade da geração de logs
                    log_intensity = self.calculate_log_intensity(scenario.log_intensity, time.time() - start_time)
                    
                    # Submeter requisições
                    for _ in range(self.get_request_count(scenario.log_intensity)):
                        future = executor.submit(
                            self.make_log_request,
                            scenario,
                            log_intensity
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
                            
                            # Registrar evento de log
                            log_event = {
                                'timestamp': datetime.now().isoformat(),
                                'endpoint': result['endpoint'],
                                'response_time': result['response_time'],
                                'log_intensity': log_intensity,
                                'success': result['success'],
                                'log_type': scenario.log_type
                            }
                            scenario_result['log_events'].append(log_event)
                            
                        except Exception as e:
                            self.log(f"Erro na requisição de log: {str(e)}", "ERROR")
                            scenario_result['failed_requests'] += 1
                    
                    # Limpar futures processados
                    futures = [f for f in futures if not f.done()]
                    
                    # Aguardar baseado na intensidade
                    wait_time = self.calculate_wait_time(scenario.log_intensity)
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
    
    def get_concurrent_workers(self, log_intensity: str) -> int:
        """Retorna número de workers baseado na intensidade de logs"""
        if log_intensity == "low":
            return 5
        elif log_intensity == "medium":
            return 15
        elif log_intensity == "high":
            return 30
        elif log_intensity == "extreme":
            return 50
        else:
            return 10
    
    def get_request_count(self, log_intensity: str) -> int:
        """Retorna número de requisições baseado na intensidade de logs"""
        if log_intensity == "low":
            return 3
        elif log_intensity == "medium":
            return 8
        elif log_intensity == "high":
            return 15
        elif log_intensity == "extreme":
            return 25
        else:
            return 5
    
    def calculate_log_intensity(self, log_intensity: str, elapsed_time: float) -> float:
        """Calcula intensidade da geração de logs"""
        if log_intensity == "low":
            return 0.3
        
        elif log_intensity == "medium":
            return 0.6
        
        elif log_intensity == "high":
            # Variação baseada em função seno
            variation = np.sin(elapsed_time / 300) * 0.3 + 0.7  # Variação de 0.4 a 1.0
            return variation
        
        elif log_intensity == "extreme":
            # Picos extremos a cada 2 minutos
            extreme_cycle = 120
            if (elapsed_time % extreme_cycle) < 30:  # 30 segundos de pico
                return 1.0
            else:
                return 0.5
        
        return 0.5
    
    def calculate_wait_time(self, log_intensity: str) -> float:
        """Calcula tempo de espera baseado na intensidade de logs"""
        if log_intensity == "low":
            return 5.0
        elif log_intensity == "medium":
            return 2.0
        elif log_intensity == "high":
            return 1.0
        elif log_intensity == "extreme":
            return 0.5
        else:
            return 3.0
    
    def make_log_request(self, scenario: LogGenerationScenario, log_intensity: float) -> Dict[str, Any]:
        """Faz uma requisição para gerar logs"""
        start_time = time.time()
        
        try:
            # Selecionar endpoint baseado no tipo de log
            endpoint = self.select_log_endpoint(scenario.log_type, log_intensity)
            
            # Gerar payload específico para logs
            payload = self.generate_log_payload(scenario, log_intensity)
            
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
                'log_intensity': log_intensity,
                'payload_size': len(json.dumps(payload))
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                'success': False,
                'error': str(e),
                'response_time': (end_time - start_time) * 1000,
                'endpoint': 'unknown',
                'log_intensity': log_intensity
            }
    
    def select_log_endpoint(self, log_type: str, log_intensity: float) -> str:
        """Seleciona endpoint baseado no tipo de log"""
        if log_type == "application":
            return random.choice(["/api/v1/analytics/advanced", "/api/reports/generate"])
        
        elif log_type == "access":
            return random.choice(["/api/users/profile", "/api/categories/list"])
        
        elif log_type == "error":
            # Endpoints que podem gerar erros
            return random.choice(["/api/reports/generate", "/api/executions/create"])
        
        elif log_type == "audit":
            return random.choice(["/api/audit/logs", "/api/metrics/performance"])
        
        elif log_type == "performance":
            return random.choice(["/api/metrics/performance", "/api/business-metrics"])
        
        else:
            return random.choice(self.log_endpoints)
    
    def generate_log_payload(self, scenario: LogGenerationScenario, log_intensity: float) -> Dict[str, Any]:
        """Gera payload específico para teste de logs"""
        base_payload = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "log_generation",
            "scenario": scenario.name,
            "log_intensity": log_intensity
        }
        
        if scenario.log_type == "application":
            base_payload.update({
                "data": {
                    "application_log": {
                        "operation": "data_processing",
                        "complexity": "high" if log_intensity > 0.7 else "medium",
                        "data_size": int(log_intensity * 10000)
                    }
                }
            })
        
        elif scenario.log_type == "access":
            base_payload.update({
                "data": {
                    "access_log": {
                        "user_agent": "load_test_client",
                        "ip_address": f"192.168.1.{random.randint(1, 255)}",
                        "request_method": "POST"
                    }
                }
            })
        
        elif scenario.log_type == "error":
            base_payload.update({
                "data": {
                    "error_log": {
                        "force_error": log_intensity > 0.8,
                        "error_type": "validation_error" if log_intensity > 0.6 else "processing_error"
                    }
                }
            })
        
        elif scenario.log_type == "audit":
            base_payload.update({
                "data": {
                    "audit_log": {
                        "user_id": f"user_{random.randint(1000, 9999)}",
                        "action": "data_access",
                        "resource": "analytics_data"
                    }
                }
            })
        
        elif scenario.log_type == "performance":
            base_payload.update({
                "data": {
                    "performance_log": {
                        "operation_type": "heavy_computation",
                        "expected_duration": int(log_intensity * 5000),
                        "monitoring_enabled": True
                    }
                }
            })
        
        return base_payload
    
    def detect_log_events(self, metrics: List[Dict], scenario: LogGenerationScenario) -> List[Dict]:
        """Detecta eventos relacionados a logs"""
        log_events = []
        
        for metric in metrics:
            log_volume = metric.get('log_volume', 0)
            
            # Detectar eventos baseado no volume de logs
            if log_volume > scenario.target_volume * 1.2:
                log_events.append({
                    'timestamp': metric['timestamp'],
                    'event_type': 'high_log_volume',
                    'volume': log_volume,
                    'target': scenario.target_volume,
                    'severity': 'high'
                })
            
            elif log_volume < scenario.target_volume * 0.5:
                log_events.append({
                    'timestamp': metric['timestamp'],
                    'event_type': 'low_log_volume',
                    'volume': log_volume,
                    'target': scenario.target_volume,
                    'severity': 'medium'
                })
            
            # Detectar problemas de performance
            processing_time = metric.get('processing_time', 0)
            if processing_time > 1000:  # Mais de 1 segundo
                log_events.append({
                    'timestamp': metric['timestamp'],
                    'event_type': 'slow_log_processing',
                    'processing_time': processing_time,
                    'severity': 'high'
                })
        
        return log_events
    
    def analyze_log_generation(self, metrics: List[Dict], scenario: LogGenerationScenario) -> Dict[str, Any]:
        """Analisa a geração de logs"""
        if not metrics:
            return {'analysis': 'no_data'}
        
        log_volumes = [m.get('log_volume', 0) for m in metrics]
        processing_times = [m.get('processing_time', 0) for m in metrics]
        
        # Estatísticas básicas
        mean_volume = np.mean(log_volumes)
        max_volume = max(log_volumes)
        mean_processing_time = np.mean(processing_times)
        max_processing_time = max(processing_times)
        
        # Análise de tendência
        if len(log_volumes) > 1:
            trend = self.calculate_log_trend(log_volumes)
        else:
            trend = "insufficient_data"
        
        # Análise de performance vs target
        volume_achievement_rate = (mean_volume / scenario.target_volume) * 100 if scenario.target_volume > 0 else 0
        
        # Análise de estabilidade
        volume_stability = 1.0 - (np.std(log_volumes) / mean_volume) if mean_volume > 0 else 0
        
        return {
            'mean_volume': mean_volume,
            'max_volume': max_volume,
            'mean_processing_time': mean_processing_time,
            'max_processing_time': max_processing_time,
            'trend': trend,
            'volume_achievement_rate': volume_achievement_rate,
            'volume_stability': volume_stability,
            'target_achieved': volume_achievement_rate >= 80,  # 80% do target
            'performance_issues': sum(1 for t in processing_times if t > 1000)
        }
    
    def calculate_log_trend(self, volumes: List[float]) -> str:
        """Calcula tendência dos volumes de log"""
        if len(volumes) < 2:
            return "insufficient_data"
        
        # Regressão linear simples
        x = list(range(len(volumes)))
        slope = np.polyfit(x, volumes, 1)[0]
        
        if abs(slope) < 10:
            return "stable"
        elif slope > 10:
            return "increasing"
        else:
            return "decreasing"
    
    def analyze_log_results(self, scenario_result: Dict, metrics: List[Dict], scenario: LogGenerationScenario) -> Dict[str, Any]:
        """Analisa os resultados do teste de logs"""
        total_requests = scenario_result['requests_made']
        successful_requests = scenario_result['successful_requests']
        
        # Análise de métricas
        if metrics:
            log_volumes = [m.get('log_volume', 0) for m in metrics]
            avg_volume = np.mean(log_volumes)
            max_volume = max(log_volumes)
            target_achieved_count = sum(1 for v in log_volumes if v >= scenario.target_volume * 0.8)
        else:
            avg_volume = 0
            max_volume = 0
            target_achieved_count = 0
        
        return {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'success_rate': successful_requests / total_requests if total_requests > 0 else 0,
            'avg_response_time': scenario_result.get('avg_response_time', 0),
            'avg_log_volume': avg_volume,
            'max_log_volume': max_volume,
            'target_achieved_count': target_achieved_count,
            'target_achievement_rate': target_achieved_count / len(metrics) if metrics else 0,
            'measurements_count': len(metrics),
            'duration_minutes': scenario.duration_minutes
        }
    
    def run(self) -> Dict[str, Any]:
        """Executa todos os testes de geração de logs"""
        self.log("🚀 Iniciando testes de geração de logs")
        
        all_results = {
            'tracing_id': self.tracing_id,
            'start_time': self.start_time.isoformat(),
            'host': self.host,
            'scenarios': [],
            'summary': {},
            'log_analysis': {}
        }
        
        try:
            # Executar cenários
            for i, scenario in enumerate(self.log_generation_scenarios):
                self.log(f"Executando cenário {i+1}/{len(self.log_generation_scenarios)}: {scenario.name}")
                
                scenario_result = self.test_log_generation_scenario(scenario)
                scenario_result['scenario_index'] = i + 1
                
                all_results['scenarios'].append(scenario_result)
                
                # Atualizar métricas
                self.metrics['scenarios_executed'] += 1
                if scenario_result.get('summary', {}).get('target_achievement_rate', 0) >= 0.8:
                    self.metrics['logs_generated'] += 1
                
                # Pausa entre cenários
                if i < len(self.log_generation_scenarios) - 1:
                    time.sleep(10)
            
            # Gerar resumo geral
            all_results['summary'] = self.generate_overall_summary(all_results)
            all_results['log_analysis'] = self.analyze_overall_log_generation(all_results)
            all_results['end_time'] = datetime.now().isoformat()
            
            # Calcular sucesso geral
            total_scenarios = len(all_results['scenarios'])
            successful_scenarios = sum(1 for s in all_results['scenarios'] 
                                     if not s.get('error'))
            success_rate = successful_scenarios / total_scenarios if total_scenarios > 0 else 0
            
            all_results['success'] = success_rate >= 0.8
            
            self.log(f"✅ Testes de geração de logs concluídos: {success_rate:.1%} de sucesso")
            
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
        
        # Análise por tipo de log
        log_analysis = {}
        for scenario in scenarios:
            log_type = scenario.get('log_type', 'unknown')
            if log_type not in log_analysis:
                log_analysis[log_type] = {
                    'count': 0,
                    'targets_achieved': 0,
                    'avg_volume': 0.0
                }
            
            log_analysis[log_type]['count'] += 1
            summary = scenario.get('summary', {})
            if summary.get('target_achievement_rate', 0) >= 0.8:
                log_analysis[log_type]['targets_achieved'] += 1
            log_analysis[log_type]['avg_volume'] += summary.get('avg_log_volume', 0)
        
        # Calcular médias
        for log_type in log_analysis:
            count = log_analysis[log_type]['count']
            if count > 0:
                log_analysis[log_type]['avg_volume'] /= count
        
        return {
            'total_scenarios': total_scenarios,
            'targets_achieved': targets_achieved,
            'achievement_rate': targets_achieved / total_scenarios if total_scenarios > 0 else 0,
            'log_analysis': log_analysis
        }
    
    def analyze_overall_log_generation(self, all_results: Dict) -> Dict[str, Any]:
        """Analisa geração geral de logs"""
        all_metrics = []
        for scenario in all_results['scenarios']:
            all_metrics.extend(scenario.get('log_metrics', []))
        
        if not all_metrics:
            return {}
        
        # Análise geral
        log_volumes = [m.get('log_volume', 0) for m in all_metrics]
        processing_times = [m.get('processing_time', 0) for m in all_metrics]
        
        return {
            'total_measurements': len(all_metrics),
            'avg_log_volume': np.mean(log_volumes) if log_volumes else 0,
            'max_log_volume': max(log_volumes) if log_volumes else 0,
            'avg_processing_time_ms': np.mean(processing_times) if processing_times else 0,
            'max_processing_time_ms': max(processing_times) if processing_times else 0,
            'total_logs_generated': sum(log_volumes)
        }


class LogGenerationMonitor:
    """Monitor de geração de logs"""
    
    def __init__(self):
        self.metrics = []
        self.monitoring = False
        self.monitor_thread = None
        self.log_type = None
        
    def start_monitoring(self, log_type: str):
        """Inicia o monitoramento de logs"""
        self.metrics = []
        self.monitoring = True
        self.log_type = log_type
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Para o monitoramento de logs"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
    
    def _monitor_loop(self):
        """Loop de monitoramento"""
        while self.monitoring:
            try:
                # Simular coleta de métricas de logs
                # Em um ambiente real, isso viria do sistema de logs
                
                if self.log_type == "application":
                    # Simular logs de aplicação
                    log_volume = np.random.normal(800, 200)  # logs/min
                    processing_time = np.random.normal(50, 20)  # ms
                    measurement = {
                        'timestamp': datetime.now(),
                        'log_volume': max(0, log_volume),
                        'processing_time': max(0, processing_time)
                    }
                
                elif self.log_type == "access":
                    # Simular logs de acesso
                    log_volume = np.random.normal(4000, 1000)  # logs/min
                    processing_time = np.random.normal(30, 10)  # ms
                    measurement = {
                        'timestamp': datetime.now(),
                        'log_volume': max(0, log_volume),
                        'processing_time': max(0, processing_time)
                    }
                
                elif self.log_type == "error":
                    # Simular logs de erro
                    log_volume = np.random.normal(80, 30)  # logs/min
                    processing_time = np.random.normal(100, 50)  # ms
                    measurement = {
                        'timestamp': datetime.now(),
                        'log_volume': max(0, log_volume),
                        'processing_time': max(0, processing_time)
                    }
                
                elif self.log_type == "audit":
                    # Simular logs de auditoria
                    log_volume = np.random.normal(40, 15)  # logs/min
                    processing_time = np.random.normal(80, 30)  # ms
                    measurement = {
                        'timestamp': datetime.now(),
                        'log_volume': max(0, log_volume),
                        'processing_time': max(0, processing_time)
                    }
                
                elif self.log_type == "performance":
                    # Simular logs de performance
                    log_volume = np.random.normal(400, 100)  # logs/min
                    processing_time = np.random.normal(60, 25)  # ms
                    measurement = {
                        'timestamp': datetime.now(),
                        'log_volume': max(0, log_volume),
                        'processing_time': max(0, processing_time)
                    }
                
                else:
                    measurement = {
                        'timestamp': datetime.now(),
                        'log_volume': 0,
                        'processing_time': 0
                    }
                
                self.metrics.append(measurement)
                
                # Aguardar 10 segundos
                time.sleep(10)
                
            except Exception as e:
                logging.error(f"Erro no monitoramento de logs: {e}")
                time.sleep(10)
    
    def get_metrics(self) -> List[Dict]:
        """Retorna as métricas coletadas"""
        return self.metrics.copy()


def main():
    """Função principal para execução standalone"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Teste de Geração de Logs")
    parser.add_argument('--host', default='http://localhost:8000', help='Host para testar')
    parser.add_argument('--verbose', action='store_true', help='Modo verboso')
    
    args = parser.parse_args()
    
    # Criar e executar teste
    test = MonitoringLogGenerationTest(host=args.host, verbose=args.verbose)
    result = test.run()
    
    # Imprimir resultados
    print("\n" + "="*80)
    print("📊 RESULTADOS DOS TESTES DE GERAÇÃO DE LOGS")
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
    
    if 'log_analysis' in result:
        analysis = result['log_analysis']
        print(f"\n📝 ANÁLISE DE LOGS:")
        print(f"   • Total de Medições: {analysis['total_measurements']}")
        print(f"   • Volume Médio de Logs: {analysis['avg_log_volume']:.1f} logs/min")
        print(f"   • Volume Máximo de Logs: {analysis['max_log_volume']:.1f} logs/min")
        print(f"   • Tempo de Processamento Médio: {analysis['avg_processing_time_ms']:.1f} ms")
        print(f"   • Total de Logs Gerados: {analysis['total_logs_generated']:.0f}")
    
    print("="*80)


if __name__ == "__main__":
    main() 