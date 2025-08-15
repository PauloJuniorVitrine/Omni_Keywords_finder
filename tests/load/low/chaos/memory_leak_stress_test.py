#!/usr/bin/env python3
"""
Teste de Memory Leaks - Stress de Memória
Omni Keywords Finder - Tracing ID: MEMORY_LEAK_STRESS_20250127_001

Este teste aplica stress extremo na memória para detectar vazamentos:
- Carga máxima de memória
- Testes de limite de memória
- Análise de comportamento sob stress
- Validação de recuperação
- Detecção de falhas de memória

Baseado em:
- backend/app/services/stress_service.py
- backend/app/middleware/memory_limits.py
- backend/app/utils/memory_stress.py

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


@dataclass
class MemoryStressScenario:
    """Cenário de teste de stress de memória"""
    name: str
    description: str
    stress_type: str  # 'gradual', 'sudden', 'cyclic', 'extreme'
    duration_minutes: int
    memory_target_mb: float
    concurrent_requests: int
    expected_behavior: str
    severity: str  # 'low', 'medium', 'high', 'critical'


class MemoryLeakStressTest:
    """
    Teste de stress de memória para detectar vazamentos
    """
    
    def __init__(self, host: str = "http://localhost:8000", verbose: bool = False):
        self.host = host
        self.verbose = verbose
        self.tracing_id = "MEMORY_LEAK_STRESS_20250127_001"
        self.start_time = datetime.now()
        
        # Configurar logging
        self.setup_logging()
        
        # Inicializar monitor de stress
        self.stress_monitor = MemoryStressMonitor()
        
        # Cenários de stress de memória
        self.memory_stress_scenarios = [
            MemoryStressScenario(
                name="Stress Gradual",
                description="Aumento gradual da carga de memória",
                stress_type="gradual",
                duration_minutes=30,
                memory_target_mb=500.0,
                concurrent_requests=10,
                expected_behavior="Crescimento controlado de memória",
                severity="medium"
            ),
            MemoryStressScenario(
                name="Stress Súbito",
                description="Carga súbita e intensa de memória",
                stress_type="sudden",
                duration_minutes=15,
                memory_target_mb=800.0,
                concurrent_requests=50,
                expected_behavior="Pico de memória seguido de recuperação",
                severity="high"
            ),
            MemoryStressScenario(
                name="Stress Cíclico",
                description="Ciclos de stress e recuperação",
                stress_type="cyclic",
                duration_minutes=45,
                memory_target_mb=600.0,
                concurrent_requests=25,
                expected_behavior="Ciclos de crescimento e recuperação",
                severity="medium"
            ),
            MemoryStressScenario(
                name="Stress Extremo",
                description="Stress máximo até o limite",
                stress_type="extreme",
                duration_minutes=20,
                memory_target_mb=1000.0,
                concurrent_requests=100,
                expected_behavior="Limite de memória respeitado",
                severity="critical"
            )
        ]
        
        # Endpoints para stress de memória
        self.stress_endpoints = [
            "/api/v1/analytics/advanced",
            "/api/reports/generate",
            "/api/executions/create",
            "/api/metrics/performance",
            "/api/audit/logs",
            "/api/users/profile"
        ]
        
        # Métricas coletadas
        self.metrics = {
            'scenarios_executed': 0,
            'scenarios_failed': 0,
            'total_requests': 0,
            'memory_targets_reached': 0,
            'system_crashes': 0,
            'recovery_successful': 0,
            'avg_memory_peak': 0.0
        }
        
    def setup_logging(self):
        """Configura logging estruturado"""
        logging.basicConfig(
            level=logging.INFO if self.verbose else logging.WARNING,
            format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
            handlers=[
                logging.FileHandler(f'logs/memory_leak_stress_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(f"MemoryLeakStressTest_{self.tracing_id}")
        
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
    
    def test_memory_stress_scenario(self, scenario: MemoryStressScenario) -> Dict[str, Any]:
        """Testa um cenário específico de stress de memória"""
        self.log(f"Iniciando teste de stress: {scenario.name} ({scenario.duration_minutes}min)")
        
        results = {
            'scenario_name': scenario.name,
            'stress_type': scenario.stress_type,
            'severity': scenario.severity,
            'start_time': datetime.now().isoformat(),
            'memory_measurements': [],
            'stress_events': [],
            'recovery_analysis': {},
            'stress_analysis': {},
            'summary': {}
        }
        
        try:
            # Iniciar monitoramento
            self.stress_monitor.start_monitoring()
            
            # Executar cenário de stress
            scenario_result = self.execute_memory_stress_scenario(scenario)
            
            # Parar monitoramento
            self.stress_monitor.stop_monitoring()
            
            # Analisar resultados
            results['memory_measurements'] = self.stress_monitor.get_measurements()
            results['stress_events'] = scenario_result['stress_events']
            results['recovery_analysis'] = self.analyze_memory_recovery(results['memory_measurements'])
            results['stress_analysis'] = self.analyze_stress_behavior(results['memory_measurements'], scenario)
            results['summary'] = self.analyze_stress_results(scenario_result, results['memory_measurements'], scenario)
            results['end_time'] = datetime.now().isoformat()
            
        except Exception as e:
            error_msg = f"Erro durante teste {scenario.name}: {str(e)}"
            self.log(error_msg, "ERROR")
            results['error'] = error_msg
            
        return results
    
    def execute_memory_stress_scenario(self, scenario: MemoryStressScenario) -> Dict[str, Any]:
        """Executa o cenário de stress de memória"""
        start_time = time.time()
        end_time = start_time + (scenario.duration_minutes * 60)
        
        scenario_result = {
            'requests_made': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_response_time': 0.0,
            'stress_events': [],
            'memory_target_reached': False,
            'system_crashed': False,
            'peak_memory_mb': 0.0
        }
        
        self.log(f"Executando stress por {scenario.duration_minutes} minutos")
        
        try:
            with ThreadPoolExecutor(max_workers=scenario.concurrent_requests) as executor:
                futures = []
                
                while time.time() < end_time:
                    # Determinar intensidade do stress baseado no tipo
                    stress_intensity = self.calculate_stress_intensity(scenario, time.time() - start_time)
                    
                    # Submeter requisições concorrentes
                    for _ in range(scenario.concurrent_requests):
                        future = executor.submit(
                            self.make_stress_request,
                            scenario,
                            stress_intensity
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
                            
                            # Registrar evento de stress
                            stress_event = {
                                'timestamp': datetime.now().isoformat(),
                                'memory_usage_mb': result.get('memory_usage', 0),
                                'stress_intensity': stress_intensity,
                                'response_time': result['response_time'],
                                'success': result['success']
                            }
                            scenario_result['stress_events'].append(stress_event)
                            
                            # Atualizar pico de memória
                            current_memory = result.get('memory_usage', 0)
                            if current_memory > scenario_result['peak_memory_mb']:
                                scenario_result['peak_memory_mb'] = current_memory
                            
                            # Verificar se atingiu target
                            if current_memory >= scenario.memory_target_mb:
                                scenario_result['memory_target_reached'] = True
                                self.log(f"🎯 Target de memória atingido: {current_memory:.1f} MB", "WARNING")
                            
                            # Verificar se sistema crashou
                            if current_memory > 2000:  # 2GB threshold
                                scenario_result['system_crashed'] = True
                                self.log(f"💥 Sistema pode ter crashado: {current_memory:.1f} MB", "ERROR")
                                break
                            
                        except Exception as e:
                            self.log(f"Erro na requisição de stress: {str(e)}", "ERROR")
                            scenario_result['failed_requests'] += 1
                    
                    # Limpar futures processados
                    futures = [f for f in futures if not f.done()]
                    
                    # Aguardar baseado no tipo de stress
                    wait_time = self.calculate_stress_wait_time(scenario, stress_intensity)
                    time.sleep(wait_time)
                    
                    # Log de progresso
                    elapsed_minutes = (time.time() - start_time) / 60
                    if elapsed_minutes % 5 < wait_time / 60:  # A cada 5 minutos
                        self.log(f"Progresso: {elapsed_minutes:.1f}min / {scenario.duration_minutes}min")
                
        except KeyboardInterrupt:
            self.log("Teste de stress interrompido pelo usuário", "WARNING")
        
        # Calcular métricas finais
        if scenario_result['requests_made'] > 0:
            scenario_result['avg_response_time'] = scenario_result['total_response_time'] / scenario_result['requests_made']
        
        return scenario_result
    
    def calculate_stress_intensity(self, scenario: MemoryStressScenario, elapsed_time: float) -> float:
        """Calcula a intensidade do stress baseado no tempo decorrido"""
        max_intensity = 1.0
        
        if scenario.stress_type == "gradual":
            # Aumento gradual linear
            progress = elapsed_time / (scenario.duration_minutes * 60)
            return min(progress, max_intensity)
        
        elif scenario.stress_type == "sudden":
            # Stress súbito no início
            if elapsed_time < 60:  # Primeiro minuto
                return max_intensity
            else:
                return 0.3  # Manter stress baixo
        
        elif scenario.stress_type == "cyclic":
            # Ciclos de stress
            cycle_duration = 300  # 5 minutos por ciclo
            cycle_progress = (elapsed_time % cycle_duration) / cycle_duration
            if cycle_progress < 0.5:
                return max_intensity  # Primeira metade do ciclo: stress alto
            else:
                return 0.2  # Segunda metade: stress baixo
        
        elif scenario.stress_type == "extreme":
            # Stress extremo constante
            return max_intensity
        
        return 0.5
    
    def calculate_stress_wait_time(self, scenario: MemoryStressScenario, intensity: float) -> float:
        """Calcula o tempo de espera entre requisições de stress"""
        base_wait = 1.0  # 1 segundo base
        
        if scenario.stress_type == "gradual":
            return base_wait / (intensity + 0.1)  # Menor espera com maior intensidade
        
        elif scenario.stress_type == "sudden":
            return base_wait / 10  # Muito rápido
        
        elif scenario.stress_type == "cyclic":
            return base_wait / (intensity * 5 + 0.1)
        
        elif scenario.stress_type == "extreme":
            return base_wait / 20  # Extremamente rápido
        
        return base_wait
    
    def make_stress_request(self, scenario: MemoryStressScenario, intensity: float) -> Dict[str, Any]:
        """Faz uma requisição de stress"""
        start_time = time.time()
        
        try:
            # Selecionar endpoint baseado na intensidade
            endpoint = self.select_stress_endpoint(intensity)
            
            # Gerar payload de stress
            payload = self.generate_stress_payload(scenario, intensity)
            
            # Fazer requisição
            response = requests.post(
                f"{self.host}{endpoint}",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
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
                'intensity': intensity,
                'payload_size': len(json.dumps(payload))
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                'success': False,
                'error': str(e),
                'response_time': end_time - start_time,
                'endpoint': 'unknown',
                'memory_usage': 0,
                'intensity': intensity
            }
    
    def select_stress_endpoint(self, intensity: float) -> str:
        """Seleciona endpoint baseado na intensidade do stress"""
        if intensity > 0.8:
            # Stress alto: endpoints pesados
            return random.choice(["/api/reports/generate", "/api/executions/create"])
        elif intensity > 0.5:
            # Stress médio: endpoints moderados
            return random.choice(["/api/v1/analytics/advanced", "/api/metrics/performance"])
        else:
            # Stress baixo: endpoints leves
            return random.choice(["/api/users/profile", "/api/audit/logs"])
    
    def generate_stress_payload(self, scenario: MemoryStressScenario, intensity: float) -> Dict[str, Any]:
        """Gera payload específico para stress de memória"""
        base_payload = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "memory_stress",
            "scenario": scenario.name,
            "intensity": intensity
        }
        
        # Calcular tamanho do payload baseado na intensidade
        payload_size = int(intensity * 10000)  # 0 a 10k elementos
        
        if scenario.stress_type == "gradual":
            base_payload.update({
                "data": {
                    "gradual_stress": {
                        "array_size": payload_size,
                        "complexity": "increasing",
                        "depth": int(intensity * 10)
                    }
                }
            })
        elif scenario.stress_type == "sudden":
            base_payload.update({
                "data": {
                    "sudden_stress": {
                        "large_objects": [{"id": i, "data": "x" * 1000} for i in range(payload_size)],
                        "immediate_load": True
                    }
                }
            })
        elif scenario.stress_type == "cyclic":
            base_payload.update({
                "data": {
                    "cyclic_stress": {
                        "cycle_number": int(time.time() / 300),  # Ciclo a cada 5 min
                        "cycle_intensity": intensity,
                        "data_batch": list(range(payload_size))
                    }
                }
            })
        elif scenario.stress_type == "extreme":
            base_payload.update({
                "data": {
                    "extreme_stress": {
                        "max_complexity": True,
                        "deep_nesting": {"level": int(intensity * 20)},
                        "large_arrays": [list(range(payload_size)) for _ in range(10)],
                        "memory_intensive": True
                    }
                }
            })
        
        return base_payload
    
    def analyze_memory_recovery(self, measurements: List[Dict]) -> Dict[str, Any]:
        """Analisa a recuperação da memória após stress"""
        if len(measurements) < 10:
            return {'recovery_score': 0, 'recovery_time_seconds': 0}
        
        memory_values = [m['memory_mb'] for m in measurements]
        timestamps = [m['timestamp'] for m in measurements]
        
        # Encontrar pico de memória
        peak_index = memory_values.index(max(memory_values))
        peak_memory = memory_values[peak_index]
        peak_time = timestamps[peak_index]
        
        # Analisar recuperação após o pico
        if peak_index < len(memory_values) - 1:
            post_peak_values = memory_values[peak_index:]
            post_peak_times = timestamps[peak_index:]
            
            # Calcular tempo de recuperação
            recovery_threshold = peak_memory * 0.8  # 80% do pico
            recovery_time = 0
            
            for i, memory in enumerate(post_peak_values):
                if memory <= recovery_threshold:
                    recovery_time = (post_peak_times[i] - peak_time).total_seconds()
                    break
            
            # Calcular score de recuperação
            final_memory = memory_values[-1]
            recovery_score = 1.0 - (final_memory / peak_memory) if peak_memory > 0 else 0
            
        else:
            recovery_time = 0
            recovery_score = 0
        
        return {
            'peak_memory_mb': peak_memory,
            'peak_time': peak_time.isoformat(),
            'recovery_time_seconds': recovery_time,
            'recovery_score': recovery_score,
            'final_memory_mb': memory_values[-1] if memory_values else 0,
            'recovery_successful': recovery_score > 0.5
        }
    
    def analyze_stress_behavior(self, measurements: List[Dict], scenario: MemoryStressScenario) -> Dict[str, Any]:
        """Analisa o comportamento durante o stress"""
        if len(measurements) < 5:
            return {'stress_pattern': 'insufficient_data', 'stability_score': 0}
        
        memory_values = [m['memory_mb'] for m in measurements]
        
        # Análise de padrão de stress
        if scenario.stress_type == "gradual":
            # Verificar crescimento gradual
            growth_rate = (memory_values[-1] - memory_values[0]) / len(memory_values)
            pattern = 'gradual_growth' if growth_rate > 0.1 else 'stable'
        
        elif scenario.stress_type == "sudden":
            # Verificar pico súbito
            max_growth = max(memory_values[i+1] - memory_values[i] for i in range(len(memory_values)-1))
            pattern = 'sudden_spike' if max_growth > 50 else 'gradual'
        
        elif scenario.stress_type == "cyclic":
            # Verificar padrão cíclico
            if len(memory_values) >= 10:
                # Análise de variância
                variance = np.var(memory_values)
                pattern = 'cyclic' if variance > 100 else 'stable'
            else:
                pattern = 'insufficient_data'
        
        elif scenario.stress_type == "extreme":
            # Verificar stress extremo
            max_memory = max(memory_values)
            pattern = 'extreme_stress' if max_memory > scenario.memory_target_mb else 'controlled'
        
        else:
            pattern = 'unknown'
        
        # Calcular score de estabilidade
        if len(memory_values) > 1:
            stability_score = 1.0 - (np.std(memory_values) / np.mean(memory_values)) if np.mean(memory_values) > 0 else 0
        else:
            stability_score = 0
        
        return {
            'stress_pattern': pattern,
            'stability_score': stability_score,
            'max_memory_mb': max(memory_values) if memory_values else 0,
            'memory_volatility': np.std(memory_values) if len(memory_values) > 1 else 0
        }
    
    def analyze_stress_results(self, scenario_result: Dict, measurements: List[Dict], scenario: MemoryStressScenario) -> Dict[str, Any]:
        """Analisa os resultados do teste de stress"""
        total_requests = scenario_result['requests_made']
        successful_requests = scenario_result['successful_requests']
        
        # Análise de memória
        if measurements:
            initial_memory = measurements[0]['memory_mb']
            final_memory = measurements[-1]['memory_mb']
            memory_growth = final_memory - initial_memory
            peak_memory = scenario_result.get('peak_memory_mb', 0)
        else:
            memory_growth = 0
            peak_memory = 0
        
        # Análise de recuperação
        recovery_analysis = self.analyze_memory_recovery(measurements)
        stress_analysis = self.analyze_stress_behavior(measurements, scenario)
        
        return {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'success_rate': successful_requests / total_requests if total_requests > 0 else 0,
            'avg_response_time': scenario_result.get('avg_response_time', 0),
            'memory_growth_mb': memory_growth,
            'peak_memory_mb': peak_memory,
            'memory_target_reached': scenario_result.get('memory_target_reached', False),
            'system_crashed': scenario_result.get('system_crashed', False),
            'recovery_successful': recovery_analysis.get('recovery_successful', False),
            'stress_pattern': stress_analysis.get('stress_pattern', 'unknown'),
            'measurements_count': len(measurements),
            'duration_minutes': scenario.duration_minutes
        }
    
    def run(self) -> Dict[str, Any]:
        """Executa todos os testes de stress de memória"""
        self.log("🚀 Iniciando testes de stress de memória")
        
        all_results = {
            'tracing_id': self.tracing_id,
            'start_time': self.start_time.isoformat(),
            'host': self.host,
            'scenarios': [],
            'summary': {},
            'stress_analysis': {}
        }
        
        try:
            # Executar cenários
            for i, scenario in enumerate(self.memory_stress_scenarios):
                self.log(f"Executando cenário {i+1}/{len(self.memory_stress_scenarios)}: {scenario.name}")
                
                scenario_result = self.test_memory_stress_scenario(scenario)
                scenario_result['scenario_index'] = i + 1
                
                all_results['scenarios'].append(scenario_result)
                
                # Atualizar métricas
                self.metrics['scenarios_executed'] += 1
                if scenario_result.get('summary', {}).get('memory_target_reached', False):
                    self.metrics['memory_targets_reached'] += 1
                if scenario_result.get('summary', {}).get('system_crashed', False):
                    self.metrics['system_crashes'] += 1
                if scenario_result.get('summary', {}).get('recovery_successful', False):
                    self.metrics['recovery_successful'] += 1
                
                # Pausa entre cenários
                if i < len(self.memory_stress_scenarios) - 1:
                    time.sleep(10)  # Pausa para estabilizar
            
            # Gerar resumo geral
            all_results['summary'] = self.generate_overall_summary(all_results)
            all_results['stress_analysis'] = self.analyze_overall_stress(all_results)
            all_results['end_time'] = datetime.now().isoformat()
            
            # Calcular sucesso geral
            total_scenarios = len(all_results['scenarios'])
            successful_scenarios = sum(1 for s in all_results['scenarios'] 
                                     if not s.get('error'))
            success_rate = successful_scenarios / total_scenarios if total_scenarios > 0 else 0
            
            all_results['success'] = success_rate >= 0.8  # 80% de sucesso mínimo
            
            self.log(f"✅ Testes de stress concluídos: {success_rate:.1%} de sucesso")
            
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
        targets_reached = sum(1 for s in scenarios 
                            if s.get('summary', {}).get('memory_target_reached', False))
        system_crashes = sum(1 for s in scenarios 
                           if s.get('summary', {}).get('system_crashed', False))
        recovery_successful = sum(1 for s in scenarios 
                                if s.get('summary', {}).get('recovery_successful', False))
        
        # Análise por tipo de stress
        stress_type_analysis = {}
        for scenario in scenarios:
            stress_type = scenario.get('stress_type', 'unknown')
            if stress_type not in stress_type_analysis:
                stress_type_analysis[stress_type] = {
                    'count': 0, 
                    'targets_reached': 0,
                    'crashes': 0,
                    'recovery_successful': 0
                }
            
            stress_type_analysis[stress_type]['count'] += 1
            if scenario.get('summary', {}).get('memory_target_reached', False):
                stress_type_analysis[stress_type]['targets_reached'] += 1
            if scenario.get('summary', {}).get('system_crashed', False):
                stress_type_analysis[stress_type]['crashes'] += 1
            if scenario.get('summary', {}).get('recovery_successful', False):
                stress_type_analysis[stress_type]['recovery_successful'] += 1
        
        return {
            'total_scenarios': total_scenarios,
            'targets_reached': targets_reached,
            'system_crashes': system_crashes,
            'recovery_successful': recovery_successful,
            'target_reached_rate': targets_reached / total_scenarios if total_scenarios > 0 else 0,
            'crash_rate': system_crashes / total_scenarios if total_scenarios > 0 else 0,
            'recovery_rate': recovery_successful / total_scenarios if total_scenarios > 0 else 0,
            'stress_type_analysis': stress_type_analysis
        }
    
    def analyze_overall_stress(self, all_results: Dict) -> Dict[str, Any]:
        """Analisa o stress geral aplicado"""
        all_measurements = []
        for scenario in all_results['scenarios']:
            all_measurements.extend(scenario.get('memory_measurements', []))
        
        if not all_measurements:
            return {}
        
        memory_values = [m['memory_mb'] for m in all_measurements]
        
        return {
            'total_measurements': len(all_measurements),
            'max_memory_usage_mb': max(memory_values) if memory_values else 0,
            'avg_memory_usage_mb': sum(memory_values) / len(memory_values) if memory_values else 0,
            'memory_volatility': np.std(memory_values) if len(memory_values) > 1 else 0,
            'stress_intensity_score': self.calculate_stress_intensity_score(all_results)
        }
    
    def calculate_stress_intensity_score(self, all_results: Dict) -> float:
        """Calcula score de intensidade do stress"""
        scenarios = all_results['scenarios']
        if not scenarios:
            return 0.0
        
        total_score = 0.0
        for scenario in scenarios:
            summary = scenario.get('summary', {})
            
            # Pontos por target atingido
            if summary.get('memory_target_reached', False):
                total_score += 0.3
            
            # Pontos por crash do sistema
            if summary.get('system_crashed', False):
                total_score += 0.5
            
            # Pontos por recuperação bem-sucedida
            if summary.get('recovery_successful', False):
                total_score += 0.2
        
        return min(total_score / len(scenarios), 1.0)


class MemoryStressMonitor:
    """Monitor de memória para testes de stress"""
    
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
                    'cpu_percent': process.cpu_percent(),
                    'memory_percent': process.memory_percent()
                }
                
                self.measurements.append(measurement)
                
                # Aguardar 2 segundos (mais frequente para stress)
                time.sleep(2)
                
            except Exception as e:
                logging.error(f"Erro no monitoramento de stress: {e}")
                time.sleep(2)
    
    def get_measurements(self) -> List[Dict]:
        """Retorna as medições coletadas"""
        return self.measurements.copy()


def main():
    """Função principal para execução standalone"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Teste de Memory Leaks - Stress")
    parser.add_argument('--host', default='http://localhost:8000', help='Host para testar')
    parser.add_argument('--verbose', action='store_true', help='Modo verboso')
    
    args = parser.parse_args()
    
    # Criar e executar teste
    test = MemoryLeakStressTest(host=args.host, verbose=args.verbose)
    result = test.run()
    
    # Imprimir resultados
    print("\n" + "="*80)
    print("📊 RESULTADOS DOS TESTES DE STRESS DE MEMÓRIA")
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
        print(f"   • Targets Atingidos: {summary['targets_reached']}")
        print(f"   • Crashes do Sistema: {summary['system_crashes']}")
        print(f"   • Recuperações Bem-sucedidas: {summary['recovery_successful']}")
        print(f"   • Taxa de Target: {summary['target_reached_rate']:.1%}")
        print(f"   • Taxa de Crash: {summary['crash_rate']:.1%}")
    
    if 'stress_analysis' in result:
        analysis = result['stress_analysis']
        print(f"\n💥 ANÁLISE DE STRESS:")
        print(f"   • Total de Medições: {analysis['total_measurements']}")
        print(f"   • Pico de Memória: {analysis['max_memory_usage_mb']:.1f} MB")
        print(f"   • Memória Média: {analysis['avg_memory_usage_mb']:.1f} MB")
        print(f"   • Score de Intensidade: {analysis['stress_intensity_score']:.2f}")
    
    print("="*80)


if __name__ == "__main__":
    main() 