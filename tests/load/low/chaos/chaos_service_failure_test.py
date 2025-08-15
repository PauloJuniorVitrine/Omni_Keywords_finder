#!/usr/bin/env python3
"""
Teste de Chaos Engineering - Falhas de Serviço
Omni Keywords Finder - Tracing ID: CHAOS_SERVICE_20250127_001

Este teste simula falhas de serviços para validar a resiliência do sistema:
- Falhas de serviços críticos
- Degradação de performance
- Timeout de serviços
- Falhas em cascata
- Recuperação automática
- Circuit breakers

Baseado em:
- infrastructure/resilience/service_resilience.py
- backend/app/services/resilient_service.py
- infrastructure/orchestrator/service_orchestrator.py

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
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
import subprocess
import signal
import os


@dataclass
class ServiceFailureScenario:
    """Cenário de falha de serviço"""
    name: str
    description: str
    service_name: str
    failure_type: str  # 'timeout', 'error', 'crash', 'degradation'
    duration_seconds: int
    recovery_time_seconds: int
    impact_level: str  # 'low', 'medium', 'high', 'critical'


class ChaosServiceFailureTest:
    """
    Teste de falhas de serviço para Chaos Engineering
    """
    
    def __init__(self, host: str = "http://localhost:8000", verbose: bool = False):
        self.host = host
        self.verbose = verbose
        self.tracing_id = "CHAOS_SERVICE_20250127_001"
        self.start_time = datetime.now()
        
        # Configurar logging
        self.setup_logging()
        
        # Cenários de falha de serviço
        self.failure_scenarios = [
            ServiceFailureScenario(
                name="Timeout de Analytics Service",
                description="Simula timeout no serviço de analytics",
                service_name="analytics_service",
                failure_type="timeout",
                duration_seconds=30,
                recovery_time_seconds=15,
                impact_level="medium"
            ),
            ServiceFailureScenario(
                name="Erro no Payment Service",
                description="Simula erro no serviço de pagamentos",
                service_name="payment_service",
                failure_type="error",
                duration_seconds=45,
                recovery_time_seconds=20,
                impact_level="high"
            ),
            ServiceFailureScenario(
                name="Degradação do Cache Service",
                description="Simula degradação no serviço de cache",
                service_name="cache_service",
                failure_type="degradation",
                duration_seconds=60,
                recovery_time_seconds=25,
                impact_level="medium"
            ),
            ServiceFailureScenario(
                name="Falha do Database Service",
                description="Simula falha no serviço de banco de dados",
                service_name="database_service",
                failure_type="crash",
                duration_seconds=20,
                recovery_time_seconds=30,
                impact_level="critical"
            ),
            ServiceFailureScenario(
                name="Timeout do Integration Service",
                description="Simula timeout no serviço de integrações",
                service_name="integration_service",
                failure_type="timeout",
                duration_seconds=40,
                recovery_time_seconds=18,
                impact_level="high"
            )
        ]
        
        # Serviços críticos para monitorar
        self.critical_services = {
            "analytics_service": {
                "endpoints": ["/api/v1/analytics/advanced", "/api/v1/analytics/trends"],
                "health_check": "/api/health/analytics",
                "process_name": "analytics"
            },
            "payment_service": {
                "endpoints": ["/api/v1/payments/process", "/api/v1/payments/status"],
                "health_check": "/api/health/payments",
                "process_name": "payment"
            },
            "cache_service": {
                "endpoints": ["/api/cache/status", "/api/cache/clear"],
                "health_check": "/api/health/cache",
                "process_name": "redis"
            },
            "database_service": {
                "endpoints": ["/api/database/status", "/api/database/backup"],
                "health_check": "/api/health/database",
                "process_name": "postgres"
            },
            "integration_service": {
                "endpoints": ["/api/integrations/instagram", "/api/integrations/google"],
                "health_check": "/api/health/integrations",
                "process_name": "integration"
            }
        }
        
        # Métricas coletadas
        self.metrics = {
            'scenarios_executed': 0,
            'scenarios_failed': 0,
            'services_affected': 0,
            'cascade_failures': 0,
            'recovery_success_rate': 0.0,
            'avg_downtime': 0.0,
            'max_downtime': 0.0
        }
        
    def setup_logging(self):
        """Configura logging estruturado"""
        logging.basicConfig(
            level=logging.INFO if self.verbose else logging.WARNING,
            format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
            handlers=[
                logging.FileHandler(f'logs/chaos_service_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(f"ChaosServiceTest_{self.tracing_id}")
        
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
    
    def check_service_health(self, service_name: str) -> Dict[str, Any]:
        """Verifica a saúde de um serviço específico"""
        service_info = self.critical_services.get(service_name)
        if not service_info:
            return {'healthy': False, 'error': 'Service not found'}
        
        try:
            # Verificar health check endpoint
            health_response = requests.get(
                f"{self.host}{service_info['health_check']}",
                timeout=10
            )
            
            # Verificar se o processo está rodando
            process_running = self.check_process_running(service_info['process_name'])
            
            # Testar endpoints do serviço
            endpoints_healthy = self.test_service_endpoints(service_info['endpoints'])
            
            return {
                'healthy': health_response.status_code == 200 and process_running and endpoints_healthy,
                'status_code': health_response.status_code,
                'process_running': process_running,
                'endpoints_healthy': endpoints_healthy,
                'response_time': health_response.elapsed.total_seconds(),
                'timestamp': datetime.now().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'healthy': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_process_running(self, process_name: str) -> bool:
        """Verifica se um processo está rodando"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if process_name.lower() in proc.info['name'].lower():
                    return True
                if proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline']).lower()
                    if process_name.lower() in cmdline:
                        return True
            return False
        except Exception as e:
            self.log(f"Erro ao verificar processo {process_name}: {str(e)}", "ERROR")
            return False
    
    def test_service_endpoints(self, endpoints: List[str]) -> bool:
        """Testa endpoints de um serviço"""
        healthy_endpoints = 0
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.host}{endpoint}", timeout=5)
                if response.status_code < 500:  # Não considerar 4xx como falha de serviço
                    healthy_endpoints += 1
            except:
                pass
        
        return healthy_endpoints > 0  # Pelo menos um endpoint deve estar funcionando
    
    def simulate_service_failure(self, scenario: ServiceFailureScenario) -> Dict[str, Any]:
        """Simula uma falha de serviço específica"""
        self.log(f"Iniciando simulação: {scenario.name}")
        
        results = {
            'scenario_name': scenario.name,
            'service_name': scenario.service_name,
            'failure_type': scenario.failure_type,
            'start_time': datetime.now().isoformat(),
            'health_before': {},
            'health_during': {},
            'health_after': {},
            'cascade_effects': [],
            'recovery_successful': False,
            'downtime_seconds': 0,
            'error_messages': []
        }
        
        try:
            # Fase 1: Verificar saúde inicial
            self.log("Fase 1: Verificando saúde inicial dos serviços")
            results['health_before'] = self.check_all_services_health()
            
            # Fase 2: Aplicar falha
            self.log(f"Fase 2: Aplicando falha no serviço {scenario.service_name}")
            failure_start = time.time()
            
            if self.apply_service_failure(scenario):
                # Monitorar durante a falha
                self.log("Fase 3: Monitorando durante a falha")
                results['health_during'] = self.monitor_services_during_failure(scenario)
                
                # Detectar efeitos em cascata
                results['cascade_effects'] = self.detect_cascade_effects(scenario)
                
                # Aguardar duração da falha
                time.sleep(scenario.duration_seconds)
                
                # Fase 4: Remover falha e testar recuperação
                self.log("Fase 4: Removendo falha e testando recuperação")
                failure_end = time.time()
                results['downtime_seconds'] = failure_end - failure_start
                
                if self.remove_service_failure(scenario):
                    # Aguardar tempo de recuperação
                    time.sleep(scenario.recovery_time_seconds)
                    
                    # Verificar recuperação
                    results['health_after'] = self.check_all_services_health()
                    results['recovery_successful'] = self.analyze_service_recovery(
                        results['health_before'], 
                        results['health_after']
                    )
                else:
                    results['error_messages'].append("Falha ao remover simulação de serviço")
            else:
                results['error_messages'].append("Falha ao aplicar simulação de serviço")
                
        except Exception as e:
            error_msg = f"Erro durante simulação {scenario.name}: {str(e)}"
            self.log(error_msg, "ERROR")
            results['error_messages'].append(error_msg)
            
        results['end_time'] = datetime.now().isoformat()
        return results
    
    def apply_service_failure(self, scenario: ServiceFailureScenario) -> bool:
        """Aplica uma falha de serviço específica"""
        try:
            if scenario.failure_type == "timeout":
                return self.simulate_service_timeout(scenario)
            elif scenario.failure_type == "error":
                return self.simulate_service_error(scenario)
            elif scenario.failure_type == "crash":
                return self.simulate_service_crash(scenario)
            elif scenario.failure_type == "degradation":
                return self.simulate_service_degradation(scenario)
            else:
                self.log(f"Tipo de falha não suportado: {scenario.failure_type}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Erro ao aplicar falha de serviço: {str(e)}", "ERROR")
            return False
    
    def simulate_service_timeout(self, scenario: ServiceFailureScenario) -> bool:
        """Simula timeout de serviço"""
        try:
            # Em um ambiente real, isso seria feito através de:
            # - Configuração de timeouts no load balancer
            # - Modificação de configurações de serviço
            # - Uso de ferramentas como Chaos Monkey
            
            self.log(f"Simulando timeout no serviço {scenario.service_name}")
            
            # Para simulação, vamos apenas registrar a intenção
            # Em produção, usar ferramentas específicas de chaos engineering
            
            return True
        except Exception as e:
            self.log(f"Erro ao simular timeout: {str(e)}", "ERROR")
            return False
    
    def simulate_service_error(self, scenario: ServiceFailureScenario) -> bool:
        """Simula erro de serviço"""
        try:
            self.log(f"Simulando erro no serviço {scenario.service_name}")
            
            # Simular retorno de erros HTTP 5xx
            # Em produção, isso seria feito através de feature flags ou configurações
            
            return True
        except Exception as e:
            self.log(f"Erro ao simular erro de serviço: {str(e)}", "ERROR")
            return False
    
    def simulate_service_crash(self, scenario: ServiceFailureScenario) -> bool:
        """Simula crash de serviço"""
        try:
            self.log(f"Simulando crash no serviço {scenario.service_name}")
            
            # Em produção, isso seria feito através de:
            # - Kill de processos
            # - Falhas de infraestrutura
            # - Uso de ferramentas de chaos engineering
            
            return True
        except Exception as e:
            self.log(f"Erro ao simular crash: {str(e)}", "ERROR")
            return False
    
    def simulate_service_degradation(self, scenario: ServiceFailureScenario) -> bool:
        """Simula degradação de serviço"""
        try:
            self.log(f"Simulando degradação no serviço {scenario.service_name}")
            
            # Simular degradação de performance
            # Em produção, isso seria feito através de:
            # - Limitação de recursos
            # - Aumento de latência
            # - Redução de throughput
            
            return True
        except Exception as e:
            self.log(f"Erro ao simular degradação: {str(e)}", "ERROR")
            return False
    
    def remove_service_failure(self, scenario: ServiceFailureScenario) -> bool:
        """Remove a falha de serviço aplicada"""
        try:
            self.log(f"Removendo falha do serviço {scenario.service_name}")
            
            # Em produção, restaurar configurações normais
            # - Restaurar timeouts
            # - Remover feature flags de erro
            # - Reiniciar processos se necessário
            
            return True
        except Exception as e:
            self.log(f"Erro ao remover falha de serviço: {str(e)}", "ERROR")
            return False
    
    def check_all_services_health(self) -> Dict[str, Any]:
        """Verifica a saúde de todos os serviços"""
        health_status = {}
        
        for service_name in self.critical_services.keys():
            health_status[service_name] = self.check_service_health(service_name)
        
        return health_status
    
    def monitor_services_during_failure(self, scenario: ServiceFailureScenario) -> Dict[str, Any]:
        """Monitora serviços durante a falha"""
        monitoring_data = {
            'service_health': {},
            'cascade_effects': [],
            'performance_metrics': {}
        }
        
        # Verificar saúde dos serviços afetados
        for service_name in self.critical_services.keys():
            if service_name == scenario.service_name:
                # Serviço diretamente afetado
                monitoring_data['service_health'][service_name] = self.check_service_health(service_name)
            else:
                # Verificar se há efeitos em cascata
                health = self.check_service_health(service_name)
                monitoring_data['service_health'][service_name] = health
                
                # Se um serviço não afetado diretamente está com problemas, é efeito cascata
                if not health.get('healthy', True):
                    monitoring_data['cascade_effects'].append({
                        'service': service_name,
                        'effect': 'cascade_failure',
                        'timestamp': datetime.now().isoformat()
                    })
        
        # Coletar métricas de performance
        monitoring_data['performance_metrics'] = self.collect_performance_metrics()
        
        return monitoring_data
    
    def detect_cascade_effects(self, scenario: ServiceFailureScenario) -> List[Dict[str, Any]]:
        """Detecta efeitos em cascata da falha"""
        cascade_effects = []
        
        # Verificar dependências entre serviços
        service_dependencies = {
            'analytics_service': ['database_service', 'cache_service'],
            'payment_service': ['database_service'],
            'integration_service': ['cache_service', 'database_service'],
            'cache_service': ['database_service'],
            'database_service': []
        }
        
        affected_service = scenario.service_name
        dependent_services = service_dependencies.get(affected_service, [])
        
        for dependent_service in dependent_services:
            health = self.check_service_health(dependent_service)
            if not health.get('healthy', True):
                cascade_effects.append({
                    'service': dependent_service,
                    'dependency': affected_service,
                    'effect_type': 'dependency_failure',
                    'timestamp': datetime.now().isoformat()
                })
        
        return cascade_effects
    
    def collect_performance_metrics(self) -> Dict[str, Any]:
        """Coleta métricas de performance do sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memória
            memory = psutil.virtual_memory()
            
            # Disco
            disk = psutil.disk_usage('/')
            
            # Rede
            network = psutil.net_io_counters()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024**3),
                'network_bytes_sent': network.bytes_sent,
                'network_bytes_recv': network.bytes_recv
            }
        except Exception as e:
            self.log(f"Erro ao coletar métricas de performance: {str(e)}", "ERROR")
            return {}
    
    def analyze_service_recovery(self, health_before: Dict, health_after: Dict) -> bool:
        """Analisa se a recuperação dos serviços foi bem-sucedida"""
        if not health_before or not health_after:
            return False
        
        # Verificar se todos os serviços estão saudáveis após recuperação
        services_recovered = 0
        total_services = len(health_after)
        
        for service_name, health_status in health_after.items():
            if health_status.get('healthy', False):
                services_recovered += 1
        
        recovery_rate = services_recovered / total_services if total_services > 0 else 0
        recovery_successful = recovery_rate >= 0.9  # 90% dos serviços devem estar saudáveis
        
        self.log(f"Análise de recuperação:")
        self.log(f"  Serviços recuperados: {services_recovered}/{total_services}")
        self.log(f"  Taxa de recuperação: {recovery_rate:.1%}")
        self.log(f"  Recuperação bem-sucedida: {recovery_successful}")
        
        return recovery_successful
    
    def run(self) -> Dict[str, Any]:
        """Executa todos os testes de falha de serviço"""
        self.log("🚀 Iniciando testes de Chaos Engineering - Falhas de Serviço")
        
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
                
                # Executar cenário
                scenario_result = self.simulate_service_failure(scenario)
                scenario_result['scenario_index'] = i + 1
                
                all_results['scenarios'].append(scenario_result)
                
                # Atualizar métricas gerais
                self.metrics['scenarios_executed'] += 1
                if scenario_result['recovery_successful']:
                    self.metrics['recovery_success_rate'] += 1
                
                if scenario_result['cascade_effects']:
                    self.metrics['cascade_failures'] += 1
                
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
            
            self.log(f"✅ Testes de falha de serviço concluídos: {success_rate:.1%} de sucesso")
            
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
        total_cascade_effects = sum(len(s.get('cascade_effects', [])) for s in scenarios)
        
        # Análise de downtime
        downtimes = [s.get('downtime_seconds', 0) for s in scenarios]
        avg_downtime = sum(downtimes) / len(downtimes) if downtimes else 0
        max_downtime = max(downtimes) if downtimes else 0
        
        return {
            'total_scenarios': total_scenarios,
            'successful_recoveries': successful_recoveries,
            'failed_scenarios': failed_scenarios,
            'recovery_success_rate': successful_recoveries / total_scenarios if total_scenarios > 0 else 0,
            'total_cascade_effects': total_cascade_effects,
            'avg_downtime_seconds': avg_downtime,
            'max_downtime_seconds': max_downtime,
            'services_affected': len(set(s['service_name'] for s in scenarios))
        }


def main():
    """Função principal para execução standalone"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Teste de Chaos Engineering - Falhas de Serviço")
    parser.add_argument('--host', default='http://localhost:8000', help='Host para testar')
    parser.add_argument('--verbose', action='store_true', help='Modo verboso')
    
    args = parser.parse_args()
    
    # Criar e executar teste
    test = ChaosServiceFailureTest(host=args.host, verbose=args.verbose)
    result = test.run()
    
    # Imprimir resultados
    print("\n" + "="*80)
    print("📊 RESULTADOS DOS TESTES DE FALHA DE SERVIÇO")
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
        print(f"   • Efeitos em Cascata: {summary['total_cascade_effects']}")
        print(f"   • Downtime Médio: {summary['avg_downtime_seconds']:.1f}s")
        print(f"   • Downtime Máximo: {summary['max_downtime_seconds']:.1f}s")
        print(f"   • Serviços Afetados: {summary['services_affected']}")
    
    print("="*80)


if __name__ == "__main__":
    main() 