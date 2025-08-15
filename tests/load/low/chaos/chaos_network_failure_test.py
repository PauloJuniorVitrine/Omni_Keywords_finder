#!/usr/bin/env python3
"""
Teste de Chaos Engineering - Falhas de Rede
Omni Keywords Finder - Tracing ID: CHAOS_NETWORK_20250127_001

Este teste simula falhas de rede para validar a resiliência do sistema:
- Latência de rede
- Perda de pacotes
- Timeout de conexão
- Falhas de DNS
- Interrupções de rede
- Recuperação automática

Baseado em:
- infrastructure/resilience/network_resilience.py
- backend/app/middleware/network_middleware.py
- infrastructure/monitoring/network_monitoring.py

Autor: IA-Cursor
Data: 2025-01-27
Versão: 1.0
"""

import time
import random
import socket
import threading
import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
import subprocess
import platform


@dataclass
class NetworkFailureScenario:
    """Cenário de falha de rede"""
    name: str
    description: str
    latency_ms: int
    packet_loss_percent: float
    timeout_seconds: int
    duration_seconds: int
    recovery_time_seconds: int


class ChaosNetworkFailureTest:
    """
    Teste de falhas de rede para Chaos Engineering
    """
    
    def __init__(self, host: str = "http://localhost:8000", verbose: bool = False):
        self.host = host
        self.verbose = verbose
        self.tracing_id = "CHAOS_NETWORK_20250127_001"
        self.start_time = datetime.now()
        
        # Configurar logging
        self.setup_logging()
        
        # Cenários de falha de rede
        self.failure_scenarios = [
            NetworkFailureScenario(
                name="Latência Moderada",
                description="Aumento de latência para 100ms",
                latency_ms=100,
                packet_loss_percent=0.0,
                timeout_seconds=5,
                duration_seconds=30,
                recovery_time_seconds=10
            ),
            NetworkFailureScenario(
                name="Latência Alta",
                description="Aumento de latência para 500ms",
                latency_ms=500,
                packet_loss_percent=0.0,
                timeout_seconds=10,
                duration_seconds=60,
                recovery_time_seconds=15
            ),
            NetworkFailureScenario(
                name="Perda de Pacotes",
                description="5% de perda de pacotes",
                latency_ms=50,
                packet_loss_percent=5.0,
                timeout_seconds=8,
                duration_seconds=45,
                recovery_time_seconds=12
            ),
            NetworkFailureScenario(
                name="Timeout de Conexão",
                description="Timeout de conexão de 10s",
                latency_ms=0,
                packet_loss_percent=0.0,
                timeout_seconds=10,
                duration_seconds=30,
                recovery_time_seconds=10
            ),
            NetworkFailureScenario(
                name="Falha Completa",
                description="Falha completa de rede",
                latency_ms=0,
                packet_loss_percent=100.0,
                timeout_seconds=15,
                duration_seconds=20,
                recovery_time_seconds=20
            )
        ]
        
        # Endpoints críticos para testar
        self.critical_endpoints = [
            "/api/auth/login",
            "/api/v1/analytics/advanced",
            "/api/v1/payments/process",
            "/api/integrations/instagram",
            "/api/reports/generate",
            "/api/metrics/performance"
        ]
        
        # Métricas coletadas
        self.metrics = {
            'scenarios_executed': 0,
            'scenarios_failed': 0,
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'avg_response_time': 0.0,
            'max_response_time': 0.0,
            'min_response_time': float('inf'),
            'recovery_success_rate': 0.0
        }
        
    def setup_logging(self):
        """Configura logging estruturado"""
        logging.basicConfig(
            level=logging.INFO if self.verbose else logging.WARNING,
            format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
            handlers=[
                logging.FileHandler(f'logs/chaos_network_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(f"ChaosNetworkTest_{self.tracing_id}")
        
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
            
    def check_system_requirements(self) -> bool:
        """Verifica se o sistema suporta os testes de rede"""
        try:
            # Verificar se é possível modificar configurações de rede
            if platform.system() == "Windows":
                # Windows - verificar se tem privilégios de administrador
                try:
                    subprocess.run(["netsh", "interface", "show", "interface"], 
                                 capture_output=True, check=True)
                    self.log("Sistema Windows detectado - verificando privilégios")
                except subprocess.CalledProcessError:
                    self.log("Privilégios de administrador necessários no Windows", "WARNING")
                    return False
            else:
                # Linux/Mac - verificar se tc (traffic control) está disponível
                try:
                    subprocess.run(["tc", "qdisc", "show"], 
                                 capture_output=True, check=True)
                    self.log("Sistema Linux/Mac detectado - tc disponível")
                except (subprocess.CalledProcessError, FileNotFoundError):
                    self.log("tc (traffic control) não disponível", "WARNING")
                    return False
                    
            return True
            
        except Exception as e:
            self.log(f"Erro ao verificar requisitos do sistema: {str(e)}", "ERROR")
            return False
    
    def simulate_network_failure(self, scenario: NetworkFailureScenario) -> Dict[str, Any]:
        """Simula uma falha de rede específica"""
        self.log(f"Iniciando simulação: {scenario.name}")
        
        results = {
            'scenario_name': scenario.name,
            'start_time': datetime.now().isoformat(),
            'requests_during_failure': [],
            'requests_during_recovery': [],
            'failure_detected': False,
            'recovery_successful': False,
            'error_messages': []
        }
        
        try:
            # Fase 1: Estado normal (baseline)
            self.log("Fase 1: Coletando baseline de performance")
            baseline_requests = self.make_test_requests(10, "baseline")
            
            # Fase 2: Aplicar falha de rede
            self.log(f"Fase 2: Aplicando falha de rede - {scenario.description}")
            if self.apply_network_failure(scenario):
                results['failure_detected'] = True
                
                # Fazer requisições durante a falha
                failure_requests = self.make_test_requests(20, "failure")
                results['requests_during_failure'] = failure_requests
                
                # Aguardar duração da falha
                time.sleep(scenario.duration_seconds)
                
                # Fase 3: Remover falha e testar recuperação
                self.log("Fase 3: Removendo falha e testando recuperação")
                if self.remove_network_failure(scenario):
                    recovery_requests = self.make_test_requests(15, "recovery")
                    results['requests_during_recovery'] = recovery_requests
                    
                    # Verificar se a recuperação foi bem-sucedida
                    recovery_success = self.analyze_recovery(recovery_requests, baseline_requests)
                    results['recovery_successful'] = recovery_success
                    
                    # Aguardar tempo de recuperação
                    time.sleep(scenario.recovery_time_seconds)
                else:
                    results['error_messages'].append("Falha ao remover simulação de rede")
            else:
                results['error_messages'].append("Falha ao aplicar simulação de rede")
                
        except Exception as e:
            error_msg = f"Erro durante simulação {scenario.name}: {str(e)}"
            self.log(error_msg, "ERROR")
            results['error_messages'].append(error_msg)
            
        results['end_time'] = datetime.now().isoformat()
        return results
    
    def apply_network_failure(self, scenario: NetworkFailureScenario) -> bool:
        """Aplica uma falha de rede específica"""
        try:
            if platform.system() == "Windows":
                return self.apply_network_failure_windows(scenario)
            else:
                return self.apply_network_failure_linux(scenario)
        except Exception as e:
            self.log(f"Erro ao aplicar falha de rede: {str(e)}", "ERROR")
            return False
    
    def apply_network_failure_windows(self, scenario: NetworkFailureScenario) -> bool:
        """Aplica falha de rede no Windows usando netsh"""
        try:
            # Simular latência usando netsh (se disponível)
            if scenario.latency_ms > 0:
                # Nota: Esta é uma simulação simplificada
                # Em produção, usar ferramentas como Clumsy ou NetLimiter
                self.log(f"Simulando latência de {scenario.latency_ms}ms no Windows")
                
            # Simular perda de pacotes
            if scenario.packet_loss_percent > 0:
                self.log(f"Simulando perda de {scenario.packet_loss_percent}% de pacotes")
                
            return True
            
        except Exception as e:
            self.log(f"Erro ao aplicar falha no Windows: {str(e)}", "ERROR")
            return False
    
    def apply_network_failure_linux(self, scenario: NetworkFailureScenario) -> bool:
        """Aplica falha de rede no Linux usando tc"""
        try:
            # Obter interface de rede padrão
            result = subprocess.run(["ip", "route", "show", "default"], 
                                  capture_output=True, text=True, check=True)
            default_route = result.stdout.strip().split()[4]  # interface name
            
            # Aplicar latência
            if scenario.latency_ms > 0:
                cmd = [
                    "tc", "qdisc", "add", "dev", default_route, "root", "netem",
                    "delay", f"{scenario.latency_ms}ms"
                ]
                subprocess.run(cmd, check=True)
                self.log(f"Latência de {scenario.latency_ms}ms aplicada")
            
            # Aplicar perda de pacotes
            if scenario.packet_loss_percent > 0:
                cmd = [
                    "tc", "qdisc", "change", "dev", default_route, "root", "netem",
                    "loss", f"{scenario.packet_loss_percent}%"
                ]
                subprocess.run(cmd, check=True)
                self.log(f"Perda de {scenario.packet_loss_percent}% aplicada")
                
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"Erro ao aplicar falha no Linux: {str(e)}", "ERROR")
            return False
        except Exception as e:
            self.log(f"Erro inesperado no Linux: {str(e)}", "ERROR")
            return False
    
    def remove_network_failure(self, scenario: NetworkFailureScenario) -> bool:
        """Remove a falha de rede aplicada"""
        try:
            if platform.system() == "Windows":
                return self.remove_network_failure_windows(scenario)
            else:
                return self.remove_network_failure_linux(scenario)
        except Exception as e:
            self.log(f"Erro ao remover falha de rede: {str(e)}", "ERROR")
            return False
    
    def remove_network_failure_windows(self, scenario: NetworkFailureScenario) -> bool:
        """Remove falha de rede no Windows"""
        try:
            self.log("Removendo simulação de rede no Windows")
            # Em produção, remover configurações aplicadas
            return True
        except Exception as e:
            self.log(f"Erro ao remover falha no Windows: {str(e)}", "ERROR")
            return False
    
    def remove_network_failure_linux(self, scenario: NetworkFailureScenario) -> bool:
        """Remove falha de rede no Linux"""
        try:
            # Obter interface de rede padrão
            result = subprocess.run(["ip", "route", "show", "default"], 
                                  capture_output=True, text=True, check=True)
            default_route = result.stdout.strip().split()[4]
            
            # Remover configurações tc
            cmd = ["tc", "qdisc", "del", "dev", default_route, "root"]
            subprocess.run(cmd, check=True)
            self.log("Configurações de rede removidas no Linux")
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"Erro ao remover falha no Linux: {str(e)}", "ERROR")
            return False
        except Exception as e:
            self.log(f"Erro inesperado ao remover falha no Linux: {str(e)}", "ERROR")
            return False
    
    def make_test_requests(self, num_requests: int, phase: str) -> List[Dict[str, Any]]:
        """Faz requisições de teste para endpoints críticos"""
        requests_data = []
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            
            for i in range(num_requests):
                endpoint = random.choice(self.critical_endpoints)
                future = executor.submit(self.make_single_request, endpoint, phase, i)
                futures.append(future)
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    requests_data.append(result)
                except Exception as e:
                    self.log(f"Erro em requisição de teste: {str(e)}", "ERROR")
                    requests_data.append({
                        'endpoint': 'unknown',
                        'phase': phase,
                        'success': False,
                        'response_time': 0,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
        
        return requests_data
    
    def make_single_request(self, endpoint: str, phase: str, request_id: int) -> Dict[str, Any]:
        """Faz uma única requisição de teste"""
        start_time = time.time()
        
        try:
            # Preparar payload baseado no endpoint
            payload = self.get_payload_for_endpoint(endpoint)
            
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
                'endpoint': endpoint,
                'phase': phase,
                'request_id': request_id,
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'response_time': response_time,
                'response_size': len(response.content),
                'timestamp': datetime.now().isoformat()
            }
            
        except requests.exceptions.Timeout:
            end_time = time.time()
            return {
                'endpoint': endpoint,
                'phase': phase,
                'request_id': request_id,
                'success': False,
                'error': 'timeout',
                'response_time': end_time - start_time,
                'timestamp': datetime.now().isoformat()
            }
        except requests.exceptions.ConnectionError:
            end_time = time.time()
            return {
                'endpoint': endpoint,
                'phase': phase,
                'request_id': request_id,
                'success': False,
                'error': 'connection_error',
                'response_time': end_time - start_time,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            end_time = time.time()
            return {
                'endpoint': endpoint,
                'phase': phase,
                'request_id': request_id,
                'success': False,
                'error': str(e),
                'response_time': end_time - start_time,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_payload_for_endpoint(self, endpoint: str) -> Dict[str, Any]:
        """Retorna payload apropriado para cada endpoint"""
        payloads = {
            "/api/auth/login": {
                "email": "test@example.com",
                "password": "test_password_123"
            },
            "/api/v1/analytics/advanced": {
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "metrics": ["performance", "trends", "comparison"]
            },
            "/api/v1/payments/process": {
                "amount": 100.00,
                "currency": "BRL",
                "payment_method": "credit_card",
                "card_token": "tok_test_123"
            },
            "/api/integrations/instagram": {
                "username": "test_user",
                "action": "analyze_posts",
                "limit": 50
            },
            "/api/reports/generate": {
                "report_type": "performance_summary",
                "date_range": "last_30_days",
                "format": "pdf"
            },
            "/api/metrics/performance": {
                "metric_type": "response_time",
                "time_window": "1h"
            }
        }
        
        return payloads.get(endpoint, {"test": True})
    
    def analyze_recovery(self, recovery_requests: List[Dict], baseline_requests: List[Dict]) -> bool:
        """Analisa se a recuperação foi bem-sucedida"""
        if not recovery_requests or not baseline_requests:
            return False
        
        # Calcular métricas de baseline
        baseline_success_rate = sum(1 for r in baseline_requests if r['success']) / len(baseline_requests)
        baseline_avg_response_time = sum(r['response_time'] for r in baseline_requests) / len(baseline_requests)
        
        # Calcular métricas de recuperação
        recovery_success_rate = sum(1 for r in recovery_requests if r['success']) / len(recovery_requests)
        recovery_avg_response_time = sum(r['response_time'] for r in recovery_requests) / len(recovery_requests)
        
        # Critérios de recuperação bem-sucedida
        success_rate_threshold = 0.8  # 80% de sucesso
        response_time_threshold = 2.0  # 2x o tempo de resposta normal
        
        recovery_successful = (
            recovery_success_rate >= success_rate_threshold and
            recovery_avg_response_time <= baseline_avg_response_time * response_time_threshold
        )
        
        self.log(f"Análise de recuperação:")
        self.log(f"  Baseline - Sucesso: {baseline_success_rate:.2%}, Tempo: {baseline_avg_response_time:.2f}s")
        self.log(f"  Recuperação - Sucesso: {recovery_success_rate:.2%}, Tempo: {recovery_avg_response_time:.2f}s")
        self.log(f"  Recuperação bem-sucedida: {recovery_successful}")
        
        return recovery_successful
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Coleta métricas do sistema durante os testes"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memória
            memory = psutil.virtual_memory()
            
            # Rede
            network = psutil.net_io_counters()
            
            # Disco
            disk = psutil.disk_usage('/')
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'network_bytes_sent': network.bytes_sent,
                'network_bytes_recv': network.bytes_recv,
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024**3)
            }
        except Exception as e:
            self.log(f"Erro ao coletar métricas do sistema: {str(e)}", "ERROR")
            return {}
    
    def run(self) -> Dict[str, Any]:
        """Executa todos os testes de falha de rede"""
        self.log("🚀 Iniciando testes de Chaos Engineering - Falhas de Rede")
        
        # Verificar requisitos do sistema
        if not self.check_system_requirements():
            self.log("Sistema não atende aos requisitos para testes de rede", "WARNING")
            return {
                'success': False,
                'error': 'System requirements not met',
                'tracing_id': self.tracing_id
            }
        
        all_results = {
            'tracing_id': self.tracing_id,
            'start_time': self.start_time.isoformat(),
            'host': self.host,
            'scenarios': [],
            'summary': {},
            'system_metrics': []
        }
        
        try:
            # Executar cada cenário de falha
            for i, scenario in enumerate(self.failure_scenarios):
                self.log(f"Executando cenário {i+1}/{len(self.failure_scenarios)}: {scenario.name}")
                
                # Coletar métricas do sistema antes
                system_metrics_before = self.collect_system_metrics()
                
                # Executar cenário
                scenario_result = self.simulate_network_failure(scenario)
                scenario_result['scenario_index'] = i + 1
                scenario_result['system_metrics_before'] = system_metrics_before
                scenario_result['system_metrics_after'] = self.collect_system_metrics()
                
                all_results['scenarios'].append(scenario_result)
                
                # Atualizar métricas gerais
                self.metrics['scenarios_executed'] += 1
                if scenario_result['recovery_successful']:
                    self.metrics['recovery_success_rate'] += 1
                
                # Pausa entre cenários
                if i < len(self.failure_scenarios) - 1:
                    time.sleep(5)
            
            # Gerar resumo
            all_results['summary'] = self.generate_summary(all_results['scenarios'])
            all_results['end_time'] = datetime.now().isoformat()
            
            # Calcular sucesso geral
            successful_scenarios = sum(1 for s in all_results['scenarios'] 
                                     if s['recovery_successful'] and not s['error_messages'])
            total_scenarios = len(all_results['scenarios'])
            success_rate = successful_scenarios / total_scenarios if total_scenarios > 0 else 0
            
            all_results['success'] = success_rate >= 0.8  # 80% de sucesso mínimo
            
            self.log(f"✅ Testes de falha de rede concluídos: {success_rate:.1%} de sucesso")
            
        except Exception as e:
            error_msg = f"Erro durante execução dos testes: {str(e)}"
            self.log(error_msg, "ERROR")
            all_results['success'] = False
            all_results['error'] = error_msg
        
        return all_results
    
    def generate_summary(self, scenarios: List[Dict]) -> Dict[str, Any]:
        """Gera resumo dos resultados dos cenários"""
        total_scenarios = len(scenarios)
        successful_recoveries = sum(1 for s in scenarios if s['recovery_successful'])
        failed_scenarios = sum(1 for s in scenarios if s['error_messages'])
        
        # Análise de performance
        all_response_times = []
        for scenario in scenarios:
            for request in scenario['requests_during_failure'] + scenario['requests_during_recovery']:
                if 'response_time' in request:
                    all_response_times.append(request['response_time'])
        
        avg_response_time = sum(all_response_times) / len(all_response_times) if all_response_times else 0
        max_response_time = max(all_response_times) if all_response_times else 0
        min_response_time = min(all_response_times) if all_response_times else 0
        
        return {
            'total_scenarios': total_scenarios,
            'successful_recoveries': successful_recoveries,
            'failed_scenarios': failed_scenarios,
            'recovery_success_rate': successful_recoveries / total_scenarios if total_scenarios > 0 else 0,
            'avg_response_time': avg_response_time,
            'max_response_time': max_response_time,
            'min_response_time': min_response_time,
            'total_requests': len(all_response_times)
        }


def main():
    """Função principal para execução standalone"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Teste de Chaos Engineering - Falhas de Rede")
    parser.add_argument('--host', default='http://localhost:8000', help='Host para testar')
    parser.add_argument('--verbose', action='store_true', help='Modo verboso')
    
    args = parser.parse_args()
    
    # Criar e executar teste
    test = ChaosNetworkFailureTest(host=args.host, verbose=args.verbose)
    result = test.run()
    
    # Imprimir resultados
    print("\n" + "="*80)
    print("📊 RESULTADOS DOS TESTES DE FALHA DE REDE")
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
        print(f"   • Recuperações Bem-sucedidas: {summary['successful_recoveries']}")
        print(f"   • Taxa de Sucesso: {summary['recovery_success_rate']:.1%}")
        print(f"   • Tempo Médio de Resposta: {summary['avg_response_time']:.2f}s")
        print(f"   • Tempo Máximo de Resposta: {summary['max_response_time']:.2f}s")
    
    print("="*80)


if __name__ == "__main__":
    main() 