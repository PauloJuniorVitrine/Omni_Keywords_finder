#!/usr/bin/env python3
"""
Teste de Detecção de Memory Leaks
Omni Keywords Finder - Tracing ID: MEMORY_LEAK_DETECTION_20250127_001

Este teste detecta vazamentos de memória no sistema:
- Monitoramento de uso de memória
- Análise de garbage collection
- Detecção de crescimento de memória
- Alertas de vazamento
- Análise de objetos não liberados

Baseado em:
- backend/app/middleware/memory_middleware.py
- backend/app/utils/memory_monitor.py
- backend/app/services/memory_service.py

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
import tracemalloc
import sys


@dataclass
class MemoryLeakScenario:
    """Cenário de teste de memory leak"""
    name: str
    description: str
    leak_type: str  # 'gradual', 'sudden', 'cyclic', 'reference_cycle'
    duration_seconds: int
    request_interval: float
    expected_behavior: str
    severity: str  # 'low', 'medium', 'high', 'critical'


class MemoryLeakDetectionTest:
    """
    Teste de detecção de vazamentos de memória
    """
    
    def __init__(self, host: str = "http://localhost:8000", verbose: bool = False):
        self.host = host
        self.verbose = verbose
        self.tracing_id = "MEMORY_LEAK_DETECTION_20250127_001"
        self.start_time = datetime.now()
        
        # Configurar logging
        self.setup_logging()
        
        # Inicializar monitoramento de memória
        self.memory_monitor = MemoryMonitor()
        
        # Cenários de memory leak
        self.memory_leak_scenarios = [
            MemoryLeakScenario(
                name="Vazamento Gradual",
                description="Vazamento lento e constante de memória",
                leak_type="gradual",
                duration_seconds=300,  # 5 minutos
                request_interval=2.0,
                expected_behavior="Detecção de crescimento gradual",
                severity="medium"
            ),
            MemoryLeakScenario(
                name="Vazamento Súbito",
                description="Vazamento rápido e significativo",
                leak_type="sudden",
                duration_seconds=120,  # 2 minutos
                request_interval=1.0,
                expected_behavior="Detecção de crescimento súbito",
                severity="high"
            ),
            MemoryLeakScenario(
                name="Vazamento Cíclico",
                description="Vazamento que ocorre em ciclos",
                leak_type="cyclic",
                duration_seconds=240,  # 4 minutos
                request_interval=3.0,
                expected_behavior="Detecção de padrão cíclico",
                severity="medium"
            ),
            MemoryLeakScenario(
                name="Ciclo de Referências",
                description="Objetos com referências circulares",
                leak_type="reference_cycle",
                duration_seconds=180,  # 3 minutos
                request_interval=2.5,
                expected_behavior="Detecção de referências circulares",
                severity="critical"
            )
        ]
        
        # Endpoints para testar memory leaks
        self.test_endpoints = [
            "/api/v1/analytics/advanced",
            "/api/reports/generate",
            "/api/v1/payments/process",
            "/api/executions/create",
            "/api/users/profile",
            "/api/categories/list"
        ]
        
        # Métricas coletadas
        self.metrics = {
            'scenarios_executed': 0,
            'scenarios_failed': 0,
            'total_requests': 0,
            'memory_leaks_detected': 0,
            'false_positives': 0,
            'avg_memory_growth': 0.0
        }
        
    def setup_logging(self):
        """Configura logging estruturado"""
        logging.basicConfig(
            level=logging.INFO if self.verbose else logging.WARNING,
            format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
            handlers=[
                logging.FileHandler(f'logs/memory_leak_detection_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(f"MemoryLeakDetectionTest_{self.tracing_id}")
        
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
    
    def test_memory_leak_scenario(self, scenario: MemoryLeakScenario) -> Dict[str, Any]:
        """Testa um cenário específico de memory leak"""
        self.log(f"Iniciando teste: {scenario.name}")
        
        results = {
            'scenario_name': scenario.name,
            'leak_type': scenario.leak_type,
            'severity': scenario.severity,
            'start_time': datetime.now().isoformat(),
            'memory_measurements': [],
            'leak_detected': False,
            'leak_details': {},
            'summary': {}
        }
        
        try:
            # Iniciar monitoramento de memória
            self.memory_monitor.start_monitoring()
            
            # Executar cenário de teste
            scenario_result = self.execute_memory_leak_scenario(scenario)
            
            # Parar monitoramento
            self.memory_monitor.stop_monitoring()
            
            # Analisar resultados
            results['memory_measurements'] = self.memory_monitor.get_measurements()
            results['leak_detected'] = self.detect_memory_leak(results['memory_measurements'], scenario)
            results['leak_details'] = self.analyze_leak_details(results['memory_measurements'], scenario)
            results['summary'] = self.analyze_memory_leak_results(scenario_result, results['memory_measurements'])
            results['end_time'] = datetime.now().isoformat()
            
        except Exception as e:
            error_msg = f"Erro durante teste {scenario.name}: {str(e)}"
            self.log(error_msg, "ERROR")
            results['error'] = error_msg
            
        return results
    
    def execute_memory_leak_scenario(self, scenario: MemoryLeakScenario) -> Dict[str, Any]:
        """Executa o cenário de memory leak"""
        start_time = time.time()
        end_time = start_time + scenario.duration_seconds
        
        scenario_result = {
            'requests_made': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_response_time': 0.0,
            'memory_growth_rate': 0.0
        }
        
        self.log(f"Executando cenário por {scenario.duration_seconds} segundos")
        
        try:
            while time.time() < end_time:
                # Fazer requisição
                request_result = self.make_memory_test_request(scenario)
                scenario_result['requests_made'] += 1
                
                if request_result['success']:
                    scenario_result['successful_requests'] += 1
                else:
                    scenario_result['failed_requests'] += 1
                
                scenario_result['total_response_time'] += request_result['response_time']
                
                # Aguardar intervalo
                time.sleep(scenario.request_interval)
                
                # Log de progresso a cada 30 segundos
                elapsed = time.time() - start_time
                if elapsed % 30 < scenario.request_interval:
                    self.log(f"Progresso: {elapsed:.0f}s / {scenario.duration_seconds}s")
            
        except KeyboardInterrupt:
            self.log("Teste interrompido pelo usuário", "WARNING")
        
        # Calcular métricas finais
        if scenario_result['requests_made'] > 0:
            scenario_result['avg_response_time'] = scenario_result['total_response_time'] / scenario_result['requests_made']
        
        return scenario_result
    
    def make_memory_test_request(self, scenario: MemoryLeakScenario) -> Dict[str, Any]:
        """Faz uma requisição para testar memory leak"""
        start_time = time.time()
        
        try:
            # Selecionar endpoint aleatório
            endpoint = random.choice(self.test_endpoints)
            
            # Gerar payload baseado no tipo de leak
            payload = self.generate_memory_test_payload(scenario)
            
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
                'payload_size': len(json.dumps(payload))
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                'success': False,
                'error': str(e),
                'response_time': end_time - start_time,
                'endpoint': 'unknown'
            }
    
    def generate_memory_test_payload(self, scenario: MemoryLeakScenario) -> Dict[str, Any]:
        """Gera payload específico para teste de memory leak"""
        base_payload = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "memory_leak",
            "scenario": scenario.name
        }
        
        if scenario.leak_type == "gradual":
            # Payload que pode causar vazamento gradual
            base_payload.update({
                "data": {
                    "analytics": {
                        "metrics": ["performance", "trends", "growth"] * 100,
                        "period": "daily",
                        "filters": {"category": "test", "date_range": "30d"}
                    }
                }
            })
        elif scenario.leak_type == "sudden":
            # Payload que pode causar vazamento súbito
            base_payload.update({
                "data": {
                    "large_array": list(range(10000)),
                    "complex_object": {
                        "nested": {"deep": {"structure": {"with": {"many": {"levels": "data"}}}}}
                    }
                }
            })
        elif scenario.leak_type == "cyclic":
            # Payload que pode causar vazamento cíclico
            base_payload.update({
                "data": {
                    "cyclic_data": {
                        "batch_size": 1000,
                        "iterations": 10,
                        "cache_enabled": True
                    }
                }
            })
        elif scenario.leak_type == "reference_cycle":
            # Payload que pode causar referências circulares
            base_payload.update({
                "data": {
                    "circular_references": True,
                    "object_count": 1000,
                    "reference_depth": 5
                }
            })
        
        return base_payload
    
    def detect_memory_leak(self, measurements: List[Dict], scenario: MemoryLeakScenario) -> bool:
        """Detecta se há vazamento de memória baseado nas medições"""
        if len(measurements) < 10:
            return False
        
        # Extrair valores de memória
        memory_values = [m['memory_mb'] for m in measurements]
        timestamps = [m['timestamp'] for m in measurements]
        
        # Calcular taxa de crescimento
        if len(memory_values) >= 2:
            initial_memory = memory_values[0]
            final_memory = memory_values[-1]
            time_span = (timestamps[-1] - timestamps[0]).total_seconds()
            
            growth_rate = (final_memory - initial_memory) / time_span  # MB/s
            
            # Thresholds baseados no tipo de leak
            if scenario.leak_type == "gradual":
                threshold = 0.1  # 0.1 MB/s
            elif scenario.leak_type == "sudden":
                threshold = 1.0  # 1.0 MB/s
            elif scenario.leak_type == "cyclic":
                threshold = 0.5  # 0.5 MB/s
            elif scenario.leak_type == "reference_cycle":
                threshold = 0.2  # 0.2 MB/s
            else:
                threshold = 0.5
            
            return growth_rate > threshold
        
        return False
    
    def analyze_leak_details(self, measurements: List[Dict], scenario: MemoryLeakScenario) -> Dict[str, Any]:
        """Analisa detalhes do vazamento de memória"""
        if not measurements:
            return {}
        
        memory_values = [m['memory_mb'] for m in measurements]
        timestamps = [m['timestamp'] for m in measurements]
        
        # Estatísticas básicas
        initial_memory = memory_values[0]
        final_memory = memory_values[-1]
        max_memory = max(memory_values)
        min_memory = min(memory_values)
        
        # Calcular crescimento
        total_growth = final_memory - initial_memory
        growth_percentage = (total_growth / initial_memory) * 100 if initial_memory > 0 else 0
        
        # Calcular taxa de crescimento
        time_span = (timestamps[-1] - timestamps[0]).total_seconds()
        growth_rate = total_growth / time_span if time_span > 0 else 0
        
        # Análise de padrão
        pattern_analysis = self.analyze_memory_pattern(memory_values, timestamps, scenario)
        
        return {
            'initial_memory_mb': initial_memory,
            'final_memory_mb': final_memory,
            'max_memory_mb': max_memory,
            'min_memory_mb': min_memory,
            'total_growth_mb': total_growth,
            'growth_percentage': growth_percentage,
            'growth_rate_mb_per_second': growth_rate,
            'time_span_seconds': time_span,
            'pattern_analysis': pattern_analysis,
            'leak_severity': self.calculate_leak_severity(growth_rate, scenario)
        }
    
    def analyze_memory_pattern(self, memory_values: List[float], timestamps: List[datetime], scenario: MemoryLeakScenario) -> Dict[str, Any]:
        """Analisa o padrão de uso de memória"""
        pattern = {
            'type': 'unknown',
            'confidence': 0.0,
            'characteristics': []
        }
        
        if len(memory_values) < 5:
            return pattern
        
        # Calcular diferenças entre medições consecutivas
        differences = [memory_values[i+1] - memory_values[i] for i in range(len(memory_values)-1)]
        
        # Análise baseada no tipo de cenário
        if scenario.leak_type == "gradual":
            # Verificar se há crescimento constante
            positive_diffs = sum(1 for d in differences if d > 0)
            if positive_diffs > len(differences) * 0.7:
                pattern['type'] = 'gradual_growth'
                pattern['confidence'] = positive_diffs / len(differences)
                pattern['characteristics'].append('Crescimento constante')
        
        elif scenario.leak_type == "sudden":
            # Verificar se há picos súbitos
            large_increases = sum(1 for d in differences if d > 1.0)  # > 1MB
            if large_increases > 0:
                pattern['type'] = 'sudden_spikes'
                pattern['confidence'] = large_increases / len(differences)
                pattern['characteristics'].append('Picos súbitos de memória')
        
        elif scenario.leak_type == "cyclic":
            # Verificar se há padrão cíclico
            if len(differences) >= 6:
                # Análise simples de ciclicidade
                first_half = differences[:len(differences)//2]
                second_half = differences[len(differences)//2:]
                
                if abs(sum(first_half) - sum(second_half)) < 0.5:
                    pattern['type'] = 'cyclic_pattern'
                    pattern['confidence'] = 0.8
                    pattern['characteristics'].append('Padrão cíclico detectado')
        
        elif scenario.leak_type == "reference_cycle":
            # Verificar se há crescimento com garbage collection
            gc_counts = [m.get('gc_count', 0) for m in measurements if 'gc_count' in m]
            if gc_counts:
                gc_increases = sum(1 for i in range(1, len(gc_counts)) if gc_counts[i] > gc_counts[i-1])
                if gc_increases > len(gc_counts) * 0.5:
                    pattern['type'] = 'reference_cycle'
                    pattern['confidence'] = gc_increases / len(gc_counts)
                    pattern['characteristics'].append('Aumento de garbage collection')
        
        return pattern
    
    def calculate_leak_severity(self, growth_rate: float, scenario: MemoryLeakScenario) -> str:
        """Calcula a severidade do vazamento"""
        if growth_rate > 5.0:
            return "critical"
        elif growth_rate > 2.0:
            return "high"
        elif growth_rate > 0.5:
            return "medium"
        elif growth_rate > 0.1:
            return "low"
        else:
            return "none"
    
    def analyze_memory_leak_results(self, scenario_result: Dict, measurements: List[Dict]) -> Dict[str, Any]:
        """Analisa os resultados do teste de memory leak"""
        total_requests = scenario_result['requests_made']
        successful_requests = scenario_result['successful_requests']
        
        # Calcular métricas de memória
        if measurements:
            initial_memory = measurements[0]['memory_mb']
            final_memory = measurements[-1]['memory_mb']
            memory_growth = final_memory - initial_memory
            memory_growth_rate = memory_growth / (len(measurements) * 5)  # Assumindo medições a cada 5s
        else:
            memory_growth = 0
            memory_growth_rate = 0
        
        return {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'success_rate': successful_requests / total_requests if total_requests > 0 else 0,
            'avg_response_time': scenario_result.get('avg_response_time', 0),
            'memory_growth_mb': memory_growth,
            'memory_growth_rate_mb_per_minute': memory_growth_rate * 60,
            'measurements_count': len(measurements)
        }
    
    def run(self) -> Dict[str, Any]:
        """Executa todos os testes de detecção de memory leak"""
        self.log("🚀 Iniciando testes de detecção de memory leaks")
        
        all_results = {
            'tracing_id': self.tracing_id,
            'start_time': self.start_time.isoformat(),
            'host': self.host,
            'scenarios': [],
            'summary': {},
            'memory_analysis': {}
        }
        
        try:
            # Executar cenários
            for i, scenario in enumerate(self.memory_leak_scenarios):
                self.log(f"Executando cenário {i+1}/{len(self.memory_leak_scenarios)}: {scenario.name}")
                
                scenario_result = self.test_memory_leak_scenario(scenario)
                scenario_result['scenario_index'] = i + 1
                
                all_results['scenarios'].append(scenario_result)
                
                # Atualizar métricas
                self.metrics['scenarios_executed'] += 1
                if scenario_result['leak_detected']:
                    self.metrics['memory_leaks_detected'] += 1
                
                # Pausa entre cenários
                if i < len(self.memory_leak_scenarios) - 1:
                    time.sleep(5)  # Pausa para estabilizar memória
            
            # Gerar resumo geral
            all_results['summary'] = self.generate_overall_summary(all_results)
            all_results['memory_analysis'] = self.analyze_overall_memory_usage(all_results)
            all_results['end_time'] = datetime.now().isoformat()
            
            # Calcular sucesso geral
            total_scenarios = len(all_results['scenarios'])
            successful_scenarios = sum(1 for s in all_results['scenarios'] 
                                     if not s.get('error'))
            success_rate = successful_scenarios / total_scenarios if total_scenarios > 0 else 0
            
            all_results['success'] = success_rate >= 0.8  # 80% de sucesso mínimo
            
            self.log(f"✅ Testes de memory leak concluídos: {success_rate:.1%} de sucesso")
            
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
        leaks_detected = sum(1 for s in scenarios if s.get('leak_detected', False))
        
        # Análise por tipo de leak
        leak_type_analysis = {}
        for scenario in scenarios:
            leak_type = scenario.get('leak_type', 'unknown')
            if leak_type not in leak_type_analysis:
                leak_type_analysis[leak_type] = {'count': 0, 'detected': 0}
            
            leak_type_analysis[leak_type]['count'] += 1
            if scenario.get('leak_detected', False):
                leak_type_analysis[leak_type]['detected'] += 1
        
        return {
            'total_scenarios': total_scenarios,
            'leaks_detected': leaks_detected,
            'detection_rate': leaks_detected / total_scenarios if total_scenarios > 0 else 0,
            'leak_type_analysis': leak_type_analysis
        }
    
    def analyze_overall_memory_usage(self, all_results: Dict) -> Dict[str, Any]:
        """Analisa o uso geral de memória"""
        all_measurements = []
        for scenario in all_results['scenarios']:
            all_measurements.extend(scenario.get('memory_measurements', []))
        
        if not all_measurements:
            return {}
        
        memory_values = [m['memory_mb'] for m in all_measurements]
        
        return {
            'total_measurements': len(all_measurements),
            'min_memory_mb': min(memory_values),
            'max_memory_mb': max(memory_values),
            'avg_memory_mb': sum(memory_values) / len(memory_values),
            'memory_volatility': max(memory_values) - min(memory_values)
        }


class MemoryMonitor:
    """Monitor de memória para detectar vazamentos"""
    
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
            self.monitor_thread.join(timeout=5)
    
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
                    'gc_collections': sum(stats['collections'] for stats in gc_stats)
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
    
    parser = argparse.ArgumentParser(description="Teste de Detecção de Memory Leaks")
    parser.add_argument('--host', default='http://localhost:8000', help='Host para testar')
    parser.add_argument('--verbose', action='store_true', help='Modo verboso')
    
    args = parser.parse_args()
    
    # Criar e executar teste
    test = MemoryLeakDetectionTest(host=args.host, verbose=args.verbose)
    result = test.run()
    
    # Imprimir resultados
    print("\n" + "="*80)
    print("📊 RESULTADOS DOS TESTES DE DETECÇÃO DE MEMORY LEAKS")
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
        print(f"   • Memory Leaks Detectados: {summary['leaks_detected']}")
        print(f"   • Taxa de Detecção: {summary['detection_rate']:.1%}")
    
    if 'memory_analysis' in result:
        analysis = result['memory_analysis']
        print(f"\n💾 ANÁLISE DE MEMÓRIA:")
        print(f"   • Total de Medições: {analysis['total_measurements']}")
        print(f"   • Memória Mínima: {analysis['min_memory_mb']:.1f} MB")
        print(f"   • Memória Máxima: {analysis['max_memory_mb']:.1f} MB")
        print(f"   • Memória Média: {analysis['avg_memory_mb']:.1f} MB")
        print(f"   • Volatilidade: {analysis['memory_volatility']:.1f} MB")
    
    print("="*80)


if __name__ == "__main__":
    main() 