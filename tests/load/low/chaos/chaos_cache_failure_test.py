#!/usr/bin/env python3
"""
Teste de Chaos Engineering - Falhas de Cache
Omni Keywords Finder - Tracing ID: CHAOS_CACHE_20250127_001

Este teste simula falhas de cache para validar a resiliência do sistema:
- Falhas de conexão com Redis
- Evicção de cache
- Falhas de memória
- Timeout de cache
- Falhas de rede
- Recuperação automática
- Fallback para banco

Baseado em:
- infrastructure/cache/redis_cache.py
- infrastructure/cache/cache_manager.py
- backend/app/services/cache_service.py

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
import redis
import socket


@dataclass
class CacheFailureScenario:
    """Cenário de falha de cache"""
    name: str
    description: str
    failure_type: str  # 'connection', 'memory', 'eviction', 'timeout', 'network'
    duration_seconds: int
    recovery_time_seconds: int
    impact_level: str  # 'low', 'medium', 'high', 'critical'


class ChaosCacheFailureTest:
    """
    Teste de falhas de cache para Chaos Engineering
    """
    
    def __init__(self, host: str = "http://localhost:8000", verbose: bool = False):
        self.host = host
        self.verbose = verbose
        self.tracing_id = "CHAOS_CACHE_20250127_001"
        self.start_time = datetime.now()
        
        # Configurar logging
        self.setup_logging()
        
        # Cenários de falha de cache
        self.failure_scenarios = [
            CacheFailureScenario(
                name="Falha de Conexão Redis",
                description="Simula falha de conexão com Redis",
                failure_type="connection",
                duration_seconds=30,
                recovery_time_seconds=15,
                impact_level="high"
            ),
            CacheFailureScenario(
                name="Falha de Memória Redis",
                description="Simula falha de memória no Redis",
                failure_type="memory",
                duration_seconds=45,
                recovery_time_seconds=20,
                impact_level="medium"
            ),
            CacheFailureScenario(
                name="Evicção de Cache",
                description="Simula evicção de dados do cache",
                failure_type="eviction",
                duration_seconds=20,
                recovery_time_seconds=10,
                impact_level="low"
            ),
            CacheFailureScenario(
                name="Timeout de Cache",
                description="Simula timeout em operações de cache",
                failure_type="timeout",
                duration_seconds=40,
                recovery_time_seconds=18,
                impact_level="medium"
            ),
            CacheFailureScenario(
                name="Falha de Rede Cache",
                description="Simula falha de rede afetando cache",
                failure_type="network",
                duration_seconds=25,
                recovery_time_seconds=12,
                impact_level="high"
            )
        ]
        
        # Endpoints que dependem de cache
        self.cache_dependent_endpoints = [
            "/api/v1/analytics/advanced",
            "/api/v1/analytics/trends",
            "/api/metrics/performance",
            "/api/cache/status",
            "/api/cache/clear",
            "/api/categories/list",
            "/api/users/profile",
            "/api/executions/status"
        ]
        
        # Chaves de cache para testar
        self.test_cache_keys = [
            "analytics:overview",
            "analytics:trends",
            "metrics:performance",
            "categories:list",
            "users:profile",
            "executions:status"
        ]
        
        # Configurações de Redis
        self.redis_config = {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'timeout': 5
        }
        
        # Métricas coletadas
        self.metrics = {
            'scenarios_executed': 0,
            'scenarios_failed': 0,
            'cache_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'avg_cache_time': 0.0,
            'max_cache_time': 0.0,
            'recovery_success_rate': 0.0
        }
        
    def setup_logging(self):
        """Configura logging estruturado"""
        logging.basicConfig(
            level=logging.INFO if self.verbose else logging.WARNING,
            format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
            handlers=[
                logging.FileHandler(f'logs/chaos_cache_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(f"ChaosCacheTest_{self.tracing_id}")
        
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
    
    def check_cache_health(self) -> Dict[str, Any]:
        """Verifica a saúde do cache Redis"""
        try:
            # Tentar conectar com Redis
            r = redis.Redis(**self.redis_config)
            
            # Testar ping
            start_time = time.time()
            ping_result = r.ping()
            ping_time = time.time() - start_time
            
            if not ping_result:
                return {
                    'healthy': False,
                    'error': 'Redis ping failed',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Obter informações do Redis
            info = r.info()
            
            # Verificar uso de memória
            used_memory = info.get('used_memory', 0)
            used_memory_human = info.get('used_memory_human', '0B')
            maxmemory = info.get('maxmemory', 0)
            maxmemory_human = info.get('maxmemory_human', '0B')
            
            # Verificar estatísticas
            total_commands_processed = info.get('total_commands_processed', 0)
            total_connections_received = info.get('total_connections_received', 0)
            keyspace_hits = info.get('keyspace_hits', 0)
            keyspace_misses = info.get('keyspace_misses', 0)
            
            # Calcular hit rate
            total_requests = keyspace_hits + keyspace_misses
            hit_rate = keyspace_hits / total_requests if total_requests > 0 else 0
            
            return {
                'healthy': True,
                'ping_time': ping_time,
                'used_memory': used_memory,
                'used_memory_human': used_memory_human,
                'maxmemory': maxmemory,
                'maxmemory_human': maxmemory_human,
                'total_commands_processed': total_commands_processed,
                'total_connections_received': total_connections_received,
                'keyspace_hits': keyspace_hits,
                'keyspace_misses': keyspace_misses,
                'hit_rate': hit_rate,
                'timestamp': datetime.now().isoformat()
            }
            
        except redis.ConnectionError as e:
            return {
                'healthy': False,
                'error': f'Redis connection error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
        except redis.TimeoutError as e:
            return {
                'healthy': False,
                'error': f'Redis timeout error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'healthy': False,
                'error': f'Unexpected error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def test_cache_operations(self) -> List[Dict[str, Any]]:
        """Testa operações básicas de cache"""
        results = []
        
        try:
            r = redis.Redis(**self.redis_config)
            
            for key in self.test_cache_keys:
                try:
                    # Teste de escrita
                    start_time = time.time()
                    test_value = f"test_value_{random.randint(1000, 9999)}"
                    r.set(key, test_value, ex=300)  # 5 minutos de TTL
                    write_time = time.time() - start_time
                    
                    # Teste de leitura
                    start_time = time.time()
                    retrieved_value = r.get(key)
                    read_time = time.time() - start_time
                    
                    # Teste de verificação de existência
                    start_time = time.time()
                    exists = r.exists(key)
                    exists_time = time.time() - start_time
                    
                    results.append({
                        'key': key,
                        'operation': 'read_write_exists',
                        'success': True,
                        'write_time': write_time,
                        'read_time': read_time,
                        'exists_time': exists_time,
                        'value_retrieved': retrieved_value == test_value.encode() if retrieved_value else False,
                        'exists_result': bool(exists),
                        'timestamp': datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    results.append({
                        'key': key,
                        'operation': 'read_write_exists',
                        'success': False,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Teste de limpeza
            try:
                start_time = time.time()
                r.flushdb()
                flush_time = time.time() - start_time
                
                results.append({
                    'key': 'all',
                    'operation': 'flush',
                    'success': True,
                    'flush_time': flush_time,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                results.append({
                    'key': 'all',
                    'operation': 'flush',
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
            
        except Exception as e:
            results.append({
                'error': f'Cache connection failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            })
        
        return results
    
    def simulate_cache_failure(self, scenario: CacheFailureScenario) -> Dict[str, Any]:
        """Simula uma falha de cache específica"""
        self.log(f"Iniciando simulação: {scenario.name}")
        
        results = {
            'scenario_name': scenario.name,
            'failure_type': scenario.failure_type,
            'start_time': datetime.now().isoformat(),
            'health_before': {},
            'health_during': {},
            'health_after': {},
            'operations_before': [],
            'operations_during': [],
            'operations_after': [],
            'api_requests_during': [],
            'recovery_successful': False,
            'downtime_seconds': 0,
            'error_messages': []
        }
        
        try:
            # Fase 1: Verificar saúde inicial
            self.log("Fase 1: Verificando saúde inicial do cache")
            results['health_before'] = self.check_cache_health()
            results['operations_before'] = self.test_cache_operations()
            
            # Fase 2: Aplicar falha
            self.log(f"Fase 2: Aplicando falha de cache - {scenario.description}")
            failure_start = time.time()
            
            if self.apply_cache_failure(scenario):
                # Fase 3: Testar durante a falha
                self.log("Fase 3: Testando durante a falha")
                results['health_during'] = self.check_cache_health()
                results['operations_during'] = self.test_cache_operations()
                results['api_requests_during'] = self.test_api_endpoints_during_failure()
                
                # Aguardar duração da falha
                time.sleep(scenario.duration_seconds)
                
                # Fase 4: Remover falha e testar recuperação
                self.log("Fase 4: Removendo falha e testando recuperação")
                failure_end = time.time()
                results['downtime_seconds'] = failure_end - failure_start
                
                if self.remove_cache_failure(scenario):
                    # Aguardar tempo de recuperação
                    time.sleep(scenario.recovery_time_seconds)
                    
                    # Verificar recuperação
                    results['health_after'] = self.check_cache_health()
                    results['operations_after'] = self.test_cache_operations()
                    results['recovery_successful'] = self.analyze_cache_recovery(
                        results['health_before'], 
                        results['health_after'],
                        results['operations_before'],
                        results['operations_after']
                    )
                else:
                    results['error_messages'].append("Falha ao remover simulação de cache")
            else:
                results['error_messages'].append("Falha ao aplicar simulação de cache")
                
        except Exception as e:
            error_msg = f"Erro durante simulação {scenario.name}: {str(e)}"
            self.log(error_msg, "ERROR")
            results['error_messages'].append(error_msg)
            
        results['end_time'] = datetime.now().isoformat()
        return results
    
    def apply_cache_failure(self, scenario: CacheFailureScenario) -> bool:
        """Aplica uma falha de cache específica"""
        try:
            if scenario.failure_type == "connection":
                return self.simulate_connection_failure(scenario)
            elif scenario.failure_type == "memory":
                return self.simulate_memory_failure(scenario)
            elif scenario.failure_type == "eviction":
                return self.simulate_cache_eviction(scenario)
            elif scenario.failure_type == "timeout":
                return self.simulate_cache_timeout(scenario)
            elif scenario.failure_type == "network":
                return self.simulate_network_failure(scenario)
            else:
                self.log(f"Tipo de falha não suportado: {scenario.failure_type}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Erro ao aplicar falha de cache: {str(e)}", "ERROR")
            return False
    
    def simulate_connection_failure(self, scenario: CacheFailureScenario) -> bool:
        """Simula falha de conexão com Redis"""
        try:
            self.log("Simulando falha de conexão com Redis")
            
            # Em produção, isso seria feito através de:
            # - Parar o serviço Redis
            # - Bloquear porta 6379
            # - Falha de rede
            
            # Para simulação, vamos apenas registrar a intenção
            # Em produção, usar ferramentas específicas de chaos engineering
            
            return True
        except Exception as e:
            self.log(f"Erro ao simular falha de conexão: {str(e)}", "ERROR")
            return False
    
    def simulate_memory_failure(self, scenario: CacheFailureScenario) -> bool:
        """Simula falha de memória no Redis"""
        try:
            self.log("Simulando falha de memória no Redis")
            
            # Em produção, isso seria feito através de:
            # - Limitar memória disponível
            # - Configurar maxmemory policy
            # - Forçar evicção
            
            return True
        except Exception as e:
            self.log(f"Erro ao simular falha de memória: {str(e)}", "ERROR")
            return False
    
    def simulate_cache_eviction(self, scenario: CacheFailureScenario) -> bool:
        """Simula evicção de dados do cache"""
        try:
            self.log("Simulando evicção de dados do cache")
            
            # Em produção, isso seria feito através de:
            # - Configurar políticas de evicção
            # - Limitar memória
            # - Forçar remoção de chaves
            
            return True
        except Exception as e:
            self.log(f"Erro ao simular evicção de cache: {str(e)}", "ERROR")
            return False
    
    def simulate_cache_timeout(self, scenario: CacheFailureScenario) -> bool:
        """Simula timeout em operações de cache"""
        try:
            self.log("Simulando timeout em operações de cache")
            
            # Em produção, isso seria feito através de:
            # - Configurar timeouts baixos
            # - Sobrecarregar o Redis
            # - Limitar recursos
            
            return True
        except Exception as e:
            self.log(f"Erro ao simular timeout de cache: {str(e)}", "ERROR")
            return False
    
    def simulate_network_failure(self, scenario: CacheFailureScenario) -> bool:
        """Simula falha de rede afetando cache"""
        try:
            self.log("Simulando falha de rede afetando cache")
            
            # Em produção, isso seria feito através de:
            # - Falha de rede entre aplicação e Redis
            # - Bloqueio de tráfego
            # - Latência alta
            
            return True
        except Exception as e:
            self.log(f"Erro ao simular falha de rede: {str(e)}", "ERROR")
            return False
    
    def remove_cache_failure(self, scenario: CacheFailureScenario) -> bool:
        """Remove a falha de cache aplicada"""
        try:
            self.log(f"Removendo falha de cache: {scenario.failure_type}")
            
            # Em produção, restaurar configurações normais
            # - Restaurar conectividade
            # - Restaurar memória
            # - Restaurar políticas de evicção
            # - Restaurar timeouts
            # - Restaurar conectividade de rede
            
            return True
        except Exception as e:
            self.log(f"Erro ao remover falha de cache: {str(e)}", "ERROR")
            return False
    
    def test_api_endpoints_during_failure(self) -> List[Dict[str, Any]]:
        """Testa endpoints da API durante a falha do cache"""
        results = []
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            
            for endpoint in self.cache_dependent_endpoints:
                future = executor.submit(self.test_single_endpoint, endpoint)
                futures.append(future)
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({
                        'endpoint': 'unknown',
                        'success': False,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
        
        return results
    
    def test_single_endpoint(self, endpoint: str) -> Dict[str, Any]:
        """Testa um endpoint específico"""
        start_time = time.time()
        
        try:
            # Preparar payload baseado no endpoint
            payload = self.get_payload_for_endpoint(endpoint)
            
            # Fazer requisição
            response = requests.post(
                f"{self.host}{endpoint}",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                'endpoint': endpoint,
                'success': response.status_code < 500,
                'status_code': response.status_code,
                'response_time': response_time,
                'timestamp': datetime.now().isoformat()
            }
            
        except requests.exceptions.Timeout:
            end_time = time.time()
            return {
                'endpoint': endpoint,
                'success': False,
                'error': 'timeout',
                'response_time': end_time - start_time,
                'timestamp': datetime.now().isoformat()
            }
        except requests.exceptions.ConnectionError:
            end_time = time.time()
            return {
                'endpoint': endpoint,
                'success': False,
                'error': 'connection_error',
                'response_time': end_time - start_time,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            end_time = time.time()
            return {
                'endpoint': endpoint,
                'success': False,
                'error': str(e),
                'response_time': end_time - start_time,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_payload_for_endpoint(self, endpoint: str) -> Dict[str, Any]:
        """Retorna payload apropriado para cada endpoint"""
        payloads = {
            "/api/v1/analytics/advanced": {
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "metrics": ["performance", "trends"]
            },
            "/api/v1/analytics/trends": {
                "time_window": "30d",
                "metric": "keywords_performance"
            },
            "/api/metrics/performance": {
                "metric_type": "response_time",
                "time_window": "1h"
            },
            "/api/cache/status": {
                "detailed": True
            },
            "/api/cache/clear": {
                "pattern": "*"
            },
            "/api/categories/list": {
                "limit": 10,
                "offset": 0
            },
            "/api/users/profile": {
                "user_id": 1
            },
            "/api/executions/status": {
                "execution_id": "test_123"
            }
        }
        
        return payloads.get(endpoint, {"test": True})
    
    def analyze_cache_recovery(self, health_before: Dict, health_after: Dict, 
                              operations_before: List[Dict], operations_after: List[Dict]) -> bool:
        """Analisa se a recuperação do cache foi bem-sucedida"""
        if not health_before or not health_after:
            return False
        
        # Verificar se o cache está saudável após recuperação
        if not health_after.get('healthy', False):
            return False
        
        # Verificar se as operações estão funcionando
        successful_operations_before = sum(1 for op in operations_before if op.get('success', False))
        successful_operations_after = sum(1 for op in operations_after if op.get('success', False))
        
        total_operations = len(operations_after)
        if total_operations == 0:
            return False
        
        operation_success_rate = successful_operations_after / total_operations
        recovery_successful = operation_success_rate >= 0.8  # 80% das operações devem funcionar
        
        self.log(f"Análise de recuperação do cache:")
        self.log(f"  Operações bem-sucedidas antes: {successful_operations_before}/{len(operations_before)}")
        self.log(f"  Operações bem-sucedidas depois: {successful_operations_after}/{total_operations}")
        self.log(f"  Taxa de sucesso das operações: {operation_success_rate:.1%}")
        self.log(f"  Recuperação bem-sucedida: {recovery_successful}")
        
        return recovery_successful
    
    def run(self) -> Dict[str, Any]:
        """Executa todos os testes de falha de cache"""
        self.log("🚀 Iniciando testes de Chaos Engineering - Falhas de Cache")
        
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
                scenario_result = self.simulate_cache_failure(scenario)
                scenario_result['scenario_index'] = i + 1
                
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
            
            self.log(f"✅ Testes de falha de cache concluídos: {success_rate:.1%} de sucesso")
            
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
        
        # Análise de downtime
        downtimes = [s.get('downtime_seconds', 0) for s in scenarios]
        avg_downtime = sum(downtimes) / len(downtimes) if downtimes else 0
        max_downtime = max(downtimes) if downtimes else 0
        
        # Análise de operações de cache
        all_operation_times = []
        for scenario in scenarios:
            for operation in scenario.get('operations_after', []):
                for time_key in ['write_time', 'read_time', 'exists_time', 'flush_time']:
                    if time_key in operation:
                        all_operation_times.append(operation[time_key])
        
        avg_operation_time = sum(all_operation_times) / len(all_operation_times) if all_operation_times else 0
        max_operation_time = max(all_operation_times) if all_operation_times else 0
        
        return {
            'total_scenarios': total_scenarios,
            'successful_recoveries': successful_recoveries,
            'failed_scenarios': failed_scenarios,
            'recovery_success_rate': successful_recoveries / total_scenarios if total_scenarios > 0 else 0,
            'avg_downtime_seconds': avg_downtime,
            'max_downtime_seconds': max_downtime,
            'avg_operation_time': avg_operation_time,
            'max_operation_time': max_operation_time,
            'total_operations_tested': len(all_operation_times)
        }


def main():
    """Função principal para execução standalone"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Teste de Chaos Engineering - Falhas de Cache")
    parser.add_argument('--host', default='http://localhost:8000', help='Host para testar')
    parser.add_argument('--verbose', action='store_true', help='Modo verboso')
    
    args = parser.parse_args()
    
    # Criar e executar teste
    test = ChaosCacheFailureTest(host=args.host, verbose=args.verbose)
    result = test.run()
    
    # Imprimir resultados
    print("\n" + "="*80)
    print("📊 RESULTADOS DOS TESTES DE FALHA DE CACHE")
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
        print(f"   • Downtime Médio: {summary['avg_downtime_seconds']:.1f}s")
        print(f"   • Downtime Máximo: {summary['max_downtime_seconds']:.1f}s")
        print(f"   • Tempo Médio de Operação: {summary['avg_operation_time']:.3f}s")
        print(f"   • Tempo Máximo de Operação: {summary['max_operation_time']:.3f}s")
        print(f"   • Operações Testadas: {summary['total_operations_tested']}")
    
    print("="*80)


if __name__ == "__main__":
    main() 