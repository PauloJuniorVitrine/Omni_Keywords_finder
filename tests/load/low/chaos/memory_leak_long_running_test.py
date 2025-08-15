#!/usr/bin/env python3
"""
Teste de Memory Leaks - Longa Duração
Omni Keywords Finder - Tracing ID: MEMORY_LEAK_LONG_RUNNING_20250127_001

Este teste detecta vazamentos de memória em testes de longa duração:
- Monitoramento contínuo por horas
- Análise de tendências de memória
- Detecção de crescimento lento
- Análise de estabilidade
- Validação de recuperação

Baseado em:
- backend/app/services/long_running_service.py
- backend/app/middleware/memory_middleware.py
- backend/app/utils/memory_analyzer.py

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
import gc
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
from scipy import stats


@dataclass
class LongRunningScenario:
    """Cenário de teste de longa duração"""
    name: str
    description: str
    duration_hours: float
    request_pattern: str  # 'constant', 'burst', 'variable', 'stress'
    memory_threshold_mb: float
    expected_behavior: str
    severity: str  # 'low', 'medium', 'high', 'critical'


class MemoryLeakLongRunningTest:
    """
    Teste de memory leaks de longa duração
    """
    
    def __init__(self, host: str = "http://localhost:8000", verbose: bool = False):
        self.host = host
        self.verbose = verbose
        self.tracing_id = "MEMORY_LEAK_LONG_RUNNING_20250127_001"
        self.start_time = datetime.now()
        
        # Configurar logging
        self.setup_logging()
        
        # Inicializar monitor de memória
        self.memory_monitor = LongRunningMemoryMonitor()
        
        # Cenários de longa duração
        self.long_running_scenarios = [
            LongRunningScenario(
                name="Teste Constante",
                description="Requisições constantes por 2 horas",
                duration_hours=2.0,
                request_pattern="constant",
                memory_threshold_mb=100.0,
                expected_behavior="Estabilidade de memória",
                severity="medium"
            ),
            LongRunningScenario(
                name="Teste com Picos",
                description="Requisições com picos de carga por 3 horas",
                duration_hours=3.0,
                request_pattern="burst",
                memory_threshold_mb=150.0,
                expected_behavior="Recuperação após picos",
                severity="high"
            ),
            LongRunningScenario(
                name="Teste Variável",
                description="Carga variável por 4 horas",
                duration_hours=4.0,
                request_pattern="variable",
                memory_threshold_mb=200.0,
                expected_behavior="Adaptação à carga variável",
                severity="medium"
            ),
            LongRunningScenario(
                name="Teste de Stress",
                description="Stress contínuo por 1 hora",
                duration_hours=1.0,
                request_pattern="stress",
                memory_threshold_mb=300.0,
                expected_behavior="Limite de memória respeitado",
                severity="critical"
            )
        ]
        
        # Endpoints para testes de longa duração
        self.test_endpoints = [
            "/api/v1/analytics/advanced",
            "/api/reports/generate",
            "/api/v1/payments/process",
            "/api/executions/create",
            "/api/users/profile",
            "/api/categories/list",
            "/api/metrics/performance",
            "/api/audit/logs"
        ]
        
        # Métricas coletadas
        self.metrics = {
            'scenarios_executed': 0,
            'scenarios_failed': 0,
            'total_requests': 0,
            'memory_threshold_exceeded': 0,
            'stability_periods': 0,
            'avg_memory_growth_rate': 0.0
        }
        
    def setup_logging(self):
        """Configura logging estruturado"""
        logging.basicConfig(
            level=logging.INFO if self.verbose else logging.WARNING,
            format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
            handlers=[
                logging.FileHandler(f'logs/memory_leak_long_running_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(f"MemoryLeakLongRunningTest_{self.tracing_id}")
        
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
    
    def test_long_running_scenario(self, scenario: LongRunningScenario) -> Dict[str, Any]:
        """Testa um cenário específico de longa duração"""
        self.log(f"Iniciando teste de longa duração: {scenario.name} ({scenario.duration_hours}h)")
        
        results = {
            'scenario_name': scenario.name,
            'request_pattern': scenario.request_pattern,
            'severity': scenario.severity,
            'start_time': datetime.now().isoformat(),
            'memory_measurements': [],
            'request_metrics': [],
            'stability_analysis': {},
            'trend_analysis': {},
            'summary': {}
        }
        
        try:
            # Iniciar monitoramento
            self.memory_monitor.start_monitoring()
            
            # Executar cenário
            scenario_result = self.execute_long_running_scenario(scenario)
            
            # Parar monitoramento
            self.memory_monitor.stop_monitoring()
            
            # Analisar resultados
            results['memory_measurements'] = self.memory_monitor.get_measurements()
            results['request_metrics'] = scenario_result['request_metrics']
            results['stability_analysis'] = self.analyze_memory_stability(results['memory_measurements'])
            results['trend_analysis'] = self.analyze_memory_trends(results['memory_measurements'])
            results['summary'] = self.analyze_long_running_results(scenario_result, results['memory_measurements'], scenario)
            results['end_time'] = datetime.now().isoformat()
            
        except Exception as e:
            error_msg = f"Erro durante teste {scenario.name}: {str(e)}"
            self.log(error_msg, "ERROR")
            results['error'] = error_msg
            
        return results
    
    def execute_long_running_scenario(self, scenario: LongRunningScenario) -> Dict[str, Any]:
        """Executa o cenário de longa duração"""
        start_time = time.time()
        end_time = start_time + (scenario.duration_hours * 3600)
        
        scenario_result = {
            'requests_made': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_response_time': 0.0,
            'request_metrics': [],
            'memory_threshold_exceeded': False
        }
        
        self.log(f"Executando cenário por {scenario.duration_hours} horas")
        
        try:
            while time.time() < end_time:
                # Determinar intervalo baseado no padrão
                interval = self.calculate_request_interval(scenario, time.time() - start_time)
                
                # Fazer requisição
                request_result = self.make_long_running_request(scenario)
                scenario_result['requests_made'] += 1
                
                if request_result['success']:
                    scenario_result['successful_requests'] += 1
                else:
                    scenario_result['failed_requests'] += 1
                
                scenario_result['total_response_time'] += request_result['response_time']
                
                # Adicionar métricas da requisição
                request_metric = {
                    'timestamp': datetime.now().isoformat(),
                    'request_number': scenario_result['requests_made'],
                    'success': request_result['success'],
                    'response_time': request_result['response_time'],
                    'memory_usage_mb': request_result.get('memory_usage', 0),
                    'elapsed_time_hours': (time.time() - start_time) / 3600
                }
                scenario_result['request_metrics'].append(request_metric)
                
                # Verificar threshold de memória
                if request_result.get('memory_usage', 0) > scenario.memory_threshold_mb:
                    scenario_result['memory_threshold_exceeded'] = True
                    self.log(f"⚠️ Threshold de memória excedido: {request_result.get('memory_usage', 0):.1f} MB", "WARNING")
                
                # Log de progresso a cada 30 minutos
                elapsed_hours = (time.time() - start_time) / 3600
                if elapsed_hours % 0.5 < interval / 3600:  # A cada 30 minutos
                    self.log(f"Progresso: {elapsed_hours:.1f}h / {scenario.duration_hours}h")
                
                # Aguardar intervalo
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.log("Teste interrompido pelo usuário", "WARNING")
        
        # Calcular métricas finais
        if scenario_result['requests_made'] > 0:
            scenario_result['avg_response_time'] = scenario_result['total_response_time'] / scenario_result['requests_made']
        
        return scenario_result
    
    def calculate_request_interval(self, scenario: LongRunningScenario, elapsed_time: float) -> float:
        """Calcula o intervalo entre requisições baseado no padrão"""
        base_interval = 10.0  # 10 segundos base
        
        if scenario.request_pattern == "constant":
            return base_interval
        
        elif scenario.request_pattern == "burst":
            # Picos a cada 30 minutos
            burst_cycle = 1800  # 30 minutos
            if (elapsed_time % burst_cycle) < 300:  # 5 minutos de pico
                return base_interval / 5  # 5x mais rápido durante picos
            else:
                return base_interval * 2  # 2x mais lento fora dos picos
        
        elif scenario.request_pattern == "variable":
            # Variação baseada em função seno
            variation = np.sin(elapsed_time / 1800) * 0.5 + 1  # Variação de 0.5x a 1.5x
            return base_interval / variation
        
        elif scenario.request_pattern == "stress":
            # Stress contínuo
            return base_interval / 10  # 10x mais rápido
        
        return base_interval
    
    def make_long_running_request(self, scenario: LongRunningScenario) -> Dict[str, Any]:
        """Faz uma requisição para teste de longa duração"""
        start_time = time.time()
        
        try:
            # Selecionar endpoint baseado no padrão
            endpoint = self.select_endpoint_for_pattern(scenario.request_pattern)
            
            # Gerar payload específico para longa duração
            payload = self.generate_long_running_payload(scenario)
            
            # Fazer requisição
            response = requests.post(
                f"{self.host}{endpoint}",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=60  # Timeout maior para testes de longa duração
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Obter uso atual de memória
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response_time': response_time,
                'endpoint': endpoint,
                'memory_usage': memory_usage,
                'payload_size': len(json.dumps(payload))
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                'success': False,
                'error': str(e),
                'response_time': end_time - start_time,
                'endpoint': 'unknown',
                'memory_usage': 0
            }
    
    def select_endpoint_for_pattern(self, pattern: str) -> str:
        """Seleciona endpoint baseado no padrão de teste"""
        if pattern == "constant":
            return random.choice(["/api/v1/analytics/advanced", "/api/users/profile"])
        elif pattern == "burst":
            return random.choice(["/api/reports/generate", "/api/v1/payments/process"])
        elif pattern == "variable":
            return random.choice(self.test_endpoints)
        elif pattern == "stress":
            return random.choice(["/api/executions/create", "/api/metrics/performance"])
        else:
            return random.choice(self.test_endpoints)
    
    def generate_long_running_payload(self, scenario: LongRunningScenario) -> Dict[str, Any]:
        """Gera payload específico para teste de longa duração"""
        base_payload = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "long_running",
            "scenario": scenario.name,
            "duration_hours": scenario.duration_hours
        }
        
        if scenario.request_pattern == "constant":
            base_payload.update({
                "data": {
                    "analytics": {
                        "metrics": ["performance", "trends"],
                        "period": "daily",
                        "filters": {"category": "test"}
                    }
                }
            })
        elif scenario.request_pattern == "burst":
            base_payload.update({
                "data": {
                    "report": {
                        "type": "comprehensive",
                        "include_charts": True,
                        "include_metrics": True
                    }
                }
            })
        elif scenario.request_pattern == "variable":
            base_payload.update({
                "data": {
                    "variable_load": {
                        "intensity": random.randint(1, 10),
                        "complexity": random.choice(["low", "medium", "high"])
                    }
                }
            })
        elif scenario.request_pattern == "stress":
            base_payload.update({
                "data": {
                    "stress_test": {
                        "concurrent_operations": random.randint(10, 100),
                        "data_size": random.randint(1000, 10000),
                        "complexity_level": "high"
                    }
                }
            })
        
        return base_payload
    
    def analyze_memory_stability(self, measurements: List[Dict]) -> Dict[str, Any]:
        """Analisa a estabilidade da memória ao longo do tempo"""
        if len(measurements) < 10:
            return {'stability_score': 0, 'stable_periods': 0}
        
        memory_values = [m['memory_mb'] for m in measurements]
        
        # Calcular variação
        mean_memory = np.mean(memory_values)
        std_memory = np.std(memory_values)
        coefficient_of_variation = std_memory / mean_memory if mean_memory > 0 else 0
        
        # Identificar períodos estáveis
        stable_periods = 0
        stability_threshold = 0.1  # 10% de variação
        
        for i in range(len(memory_values) - 1):
            variation = abs(memory_values[i+1] - memory_values[i]) / memory_values[i] if memory_values[i] > 0 else 0
            if variation < stability_threshold:
                stable_periods += 1
        
        stability_score = stable_periods / (len(memory_values) - 1) if len(memory_values) > 1 else 0
        
        return {
            'stability_score': stability_score,
            'stable_periods': stable_periods,
            'coefficient_of_variation': coefficient_of_variation,
            'mean_memory_mb': mean_memory,
            'std_memory_mb': std_memory,
            'is_stable': stability_score > 0.7
        }
    
    def analyze_memory_trends(self, measurements: List[Dict]) -> Dict[str, Any]:
        """Analisa tendências de memória ao longo do tempo"""
        if len(measurements) < 5:
            return {'trend': 'insufficient_data', 'slope': 0, 'r_squared': 0}
        
        memory_values = [m['memory_mb'] for m in measurements]
        time_points = list(range(len(memory_values)))
        
        # Regressão linear
        slope, intercept, r_value, p_value, std_err = stats.linregress(time_points, memory_values)
        r_squared = r_value ** 2
        
        # Determinar tipo de tendência
        if abs(slope) < 0.1:
            trend = 'stable'
        elif slope > 0.1:
            trend = 'increasing'
        else:
            trend = 'decreasing'
        
        # Calcular taxa de crescimento por hora
        growth_rate_per_hour = slope * 3600 / 5  # Assumindo medições a cada 5 segundos
        
        return {
            'trend': trend,
            'slope': slope,
            'r_squared': r_squared,
            'p_value': p_value,
            'growth_rate_mb_per_hour': growth_rate_per_hour,
            'is_significant': p_value < 0.05
        }
    
    def analyze_long_running_results(self, scenario_result: Dict, measurements: List[Dict], scenario: LongRunningScenario) -> Dict[str, Any]:
        """Analisa os resultados do teste de longa duração"""
        total_requests = scenario_result['requests_made']
        successful_requests = scenario_result['successful_requests']
        
        # Análise de memória
        if measurements:
            initial_memory = measurements[0]['memory_mb']
            final_memory = measurements[-1]['memory_mb']
            memory_growth = final_memory - initial_memory
            memory_growth_rate = memory_growth / scenario.duration_hours
        else:
            memory_growth = 0
            memory_growth_rate = 0
        
        # Análise de estabilidade
        stability_analysis = self.analyze_memory_stability(measurements)
        trend_analysis = self.analyze_memory_trends(measurements)
        
        return {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'success_rate': successful_requests / total_requests if total_requests > 0 else 0,
            'avg_response_time': scenario_result.get('avg_response_time', 0),
            'memory_growth_mb': memory_growth,
            'memory_growth_rate_mb_per_hour': memory_growth_rate,
            'memory_threshold_exceeded': scenario_result.get('memory_threshold_exceeded', False),
            'stability_score': stability_analysis.get('stability_score', 0),
            'trend_type': trend_analysis.get('trend', 'unknown'),
            'measurements_count': len(measurements),
            'duration_hours': scenario.duration_hours
        }
    
    def run(self) -> Dict[str, Any]:
        """Executa todos os testes de longa duração"""
        self.log("🚀 Iniciando testes de memory leaks de longa duração")
        
        all_results = {
            'tracing_id': self.tracing_id,
            'start_time': self.start_time.isoformat(),
            'host': self.host,
            'scenarios': [],
            'summary': {},
            'long_term_analysis': {}
        }
        
        try:
            # Executar cenários
            for i, scenario in enumerate(self.long_running_scenarios):
                self.log(f"Executando cenário {i+1}/{len(self.long_running_scenarios)}: {scenario.name}")
                
                scenario_result = self.test_long_running_scenario(scenario)
                scenario_result['scenario_index'] = i + 1
                
                all_results['scenarios'].append(scenario_result)
                
                # Atualizar métricas
                self.metrics['scenarios_executed'] += 1
                if scenario_result.get('summary', {}).get('memory_threshold_exceeded', False):
                    self.metrics['memory_threshold_exceeded'] += 1
                
                # Pausa entre cenários
                if i < len(self.long_running_scenarios) - 1:
                    time.sleep(10)  # Pausa para estabilizar
            
            # Gerar resumo geral
            all_results['summary'] = self.generate_overall_summary(all_results)
            all_results['long_term_analysis'] = self.analyze_long_term_patterns(all_results)
            all_results['end_time'] = datetime.now().isoformat()
            
            # Calcular sucesso geral
            total_scenarios = len(all_results['scenarios'])
            successful_scenarios = sum(1 for s in all_results['scenarios'] 
                                     if not s.get('error'))
            success_rate = successful_scenarios / total_scenarios if total_scenarios > 0 else 0
            
            all_results['success'] = success_rate >= 0.8  # 80% de sucesso mínimo
            
            self.log(f"✅ Testes de longa duração concluídos: {success_rate:.1%} de sucesso")
            
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
        threshold_exceeded = sum(1 for s in scenarios 
                               if s.get('summary', {}).get('memory_threshold_exceeded', False))
        
        # Análise por padrão de requisição
        pattern_analysis = {}
        for scenario in scenarios:
            pattern = scenario.get('request_pattern', 'unknown')
            if pattern not in pattern_analysis:
                pattern_analysis[pattern] = {'count': 0, 'threshold_exceeded': 0}
            
            pattern_analysis[pattern]['count'] += 1
            if scenario.get('summary', {}).get('memory_threshold_exceeded', False):
                pattern_analysis[pattern]['threshold_exceeded'] += 1
        
        return {
            'total_scenarios': total_scenarios,
            'threshold_exceeded': threshold_exceeded,
            'exceeded_rate': threshold_exceeded / total_scenarios if total_scenarios > 0 else 0,
            'pattern_analysis': pattern_analysis
        }
    
    def analyze_long_term_patterns(self, all_results: Dict) -> Dict[str, Any]:
        """Analisa padrões de longo prazo"""
        all_measurements = []
        for scenario in all_results['scenarios']:
            all_measurements.extend(scenario.get('memory_measurements', []))
        
        if not all_measurements:
            return {}
        
        memory_values = [m['memory_mb'] for m in all_measurements]
        timestamps = [m['timestamp'] for m in all_measurements]
        
        # Análise de correlação temporal
        time_points = [(ts - timestamps[0]).total_seconds() for ts in timestamps]
        
        if len(time_points) > 1:
            correlation = np.corrcoef(time_points, memory_values)[0, 1]
        else:
            correlation = 0
        
        return {
            'total_measurements': len(all_measurements),
            'total_duration_hours': (timestamps[-1] - timestamps[0]).total_seconds() / 3600 if timestamps else 0,
            'memory_correlation_with_time': correlation,
            'memory_volatility': np.std(memory_values) if len(memory_values) > 1 else 0,
            'peak_memory_usage_mb': max(memory_values) if memory_values else 0
        }


class LongRunningMemoryMonitor:
    """Monitor de memória para testes de longa duração"""
    
    def __init__(self):
        self.measurements = []
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Inicia o monitoramento de memória"""
        self.measurements = []
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Para o monitoramento de memória"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
    
    def _monitor_loop(self):
        """Loop de monitoramento"""
        while self.monitoring:
            try:
                # Obter uso de memória do processo
                process = psutil.Process()
                memory_info = process.memory_info()
                
                # Obter estatísticas de garbage collection
                gc_stats = gc.get_stats()
                
                measurement = {
                    'timestamp': datetime.now(),
                    'memory_mb': memory_info.rss / 1024 / 1024,  # Convert to MB
                    'virtual_memory_mb': memory_info.vms / 1024 / 1024,
                    'gc_count': len(gc_stats),
                    'gc_collections': sum(stats['collections'] for stats in gc_stats),
                    'cpu_percent': process.cpu_percent()
                }
                
                self.measurements.append(measurement)
                
                # Aguardar 5 segundos
                time.sleep(5)
                
            except Exception as e:
                logging.error(f"Erro no monitoramento de memória: {e}")
                time.sleep(5)
    
    def get_measurements(self) -> List[Dict]:
        """Retorna as medições coletadas"""
        return self.measurements.copy()


def main():
    """Função principal para execução standalone"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Teste de Memory Leaks - Longa Duração")
    parser.add_argument('--host', default='http://localhost:8000', help='Host para testar')
    parser.add_argument('--verbose', action='store_true', help='Modo verboso')
    
    args = parser.parse_args()
    
    # Criar e executar teste
    test = MemoryLeakLongRunningTest(host=args.host, verbose=args.verbose)
    result = test.run()
    
    # Imprimir resultados
    print("\n" + "="*80)
    print("📊 RESULTADOS DOS TESTES DE MEMORY LEAKS - LONGA DURAÇÃO")
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
        print(f"   • Thresholds Excedidos: {summary['threshold_exceeded']}")
        print(f"   • Taxa de Excesso: {summary['exceeded_rate']:.1%}")
    
    if 'long_term_analysis' in result:
        analysis = result['long_term_analysis']
        print(f"\n⏰ ANÁLISE DE LONGO PRAZO:")
        print(f"   • Total de Medições: {analysis['total_measurements']}")
        print(f"   • Duração Total: {analysis['total_duration_hours']:.1f} horas")
        print(f"   • Correlação com Tempo: {analysis['memory_correlation_with_time']:.3f}")
        print(f"   • Pico de Memória: {analysis['peak_memory_usage_mb']:.1f} MB")
    
    print("="*80)


if __name__ == "__main__":
    main() 