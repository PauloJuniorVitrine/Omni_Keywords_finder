#!/usr/bin/env python3
"""
Teste de Edge Cases - Acesso Concorrente
Omni Keywords Finder - Tracing ID: EDGE_CONCURRENT_ACCESS_20250127_001

Este teste valida o comportamento do sistema com acesso concorrente:
- Múltiplas requisições simultâneas
- Race conditions
- Deadlocks
- Contenção de recursos
- Sincronização de dados
- Locks e semáforos

Baseado em:
- backend/app/middleware/concurrency_middleware.py
- backend/app/services/concurrent_service.py
- backend/app/utils/lock_manager.py

Autor: IA-Cursor
Data: 2025-01-27
Versão: 1.0
"""

import time
import random
import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import queue
import asyncio


@dataclass
class ConcurrentAccessScenario:
    """Cenário de acesso concorrente"""
    name: str
    description: str
    concurrency_type: str  # 'read_write', 'write_write', 'read_read', 'mixed', 'resource_contention'
    num_threads: int
    endpoint: str
    payload: Dict[str, Any]
    expected_behavior: str
    severity: str  # 'low', 'medium', 'high', 'critical'


class EdgeCasesConcurrentAccessTest:
    """
    Teste de acesso concorrente para Edge Cases
    """
    
    def __init__(self, host: str = "http://localhost:8000", verbose: bool = False):
        self.host = host
        self.verbose = verbose
        self.tracing_id = "EDGE_CONCURRENT_ACCESS_20250127_001"
        self.start_time = datetime.now()
        
        # Configurar logging
        self.setup_logging()
        
        # Cenários de acesso concorrente
        self.concurrent_access_scenarios = [
            ConcurrentAccessScenario(
                name="Leitura Concorrente",
                description="Múltiplas leituras simultâneas do mesmo recurso",
                concurrency_type="read_read",
                num_threads=50,
                endpoint="/api/users/profile",
                payload={"user_id": 123},
                expected_behavior="200 OK para todas as requisições",
                severity="low"
            ),
            ConcurrentAccessScenario(
                name="Escrita Concorrente",
                description="Múltiplas escritas simultâneas no mesmo recurso",
                concurrency_type="write_write",
                num_threads=20,
                endpoint="/api/users/profile",
                payload={"user_id": 123, "name": "Updated User"},
                expected_behavior="200 OK com possível sobrescrita",
                severity="high"
            ),
            ConcurrentAccessScenario(
                name="Leitura e Escrita Concorrente",
                description="Leituras e escritas simultâneas no mesmo recurso",
                concurrency_type="read_write",
                num_threads=30,
                endpoint="/api/users/profile",
                payload={"user_id": 123, "name": "Concurrent User"},
                expected_behavior="200 OK com possível inconsistência",
                severity="critical"
            ),
            ConcurrentAccessScenario(
                name="Contenção de Recursos",
                description="Acesso concorrente a recursos limitados",
                concurrency_type="resource_contention",
                num_threads=100,
                endpoint="/api/v1/payments/process",
                payload={"amount": 100.00, "currency": "BRL"},
                expected_behavior="429 Too Many Requests ou 503 Service Unavailable",
                severity="high"
            ),
            ConcurrentAccessScenario(
                name="Operações Mistas",
                description="Mistura de operações diferentes simultâneas",
                concurrency_type="mixed",
                num_threads=40,
                endpoint="/api/v1/analytics/advanced",
                payload={"start_date": "2024-01-01", "end_date": "2024-12-31"},
                expected_behavior="200 OK com possível degradação",
                severity="medium"
            ),
            ConcurrentAccessScenario(
                name="Acesso a Dados Compartilhados",
                description="Acesso concorrente a dados compartilhados",
                concurrency_type="read_write",
                num_threads=25,
                endpoint="/api/categories/list",
                payload={"category_id": 1},
                expected_behavior="200 OK com possível inconsistência",
                severity="medium"
            ),
            ConcurrentAccessScenario(
                name="Operações de Transação",
                description="Transações concorrentes no banco de dados",
                concurrency_type="write_write",
                num_threads=15,
                endpoint="/api/v1/payments/process",
                payload={"amount": 50.00, "currency": "BRL", "transaction_id": "TXN123"},
                expected_behavior="200 OK ou 409 Conflict",
                severity="critical"
            ),
            ConcurrentAccessScenario(
                name="Cache Concorrente",
                description="Acesso concorrente ao sistema de cache",
                concurrency_type="read_read",
                num_threads=60,
                endpoint="/api/v1/analytics/trends",
                payload={"period": "daily"},
                expected_behavior="200 OK com possível cache miss",
                severity="low"
            ),
            ConcurrentAccessScenario(
                name="Fila de Processamento",
                description="Envio concorrente para filas de processamento",
                concurrency_type="write_write",
                num_threads=35,
                endpoint="/api/executions/create",
                payload={"keywords": ["test", "concurrent"], "category": "test"},
                expected_behavior="200 OK com possível acúmulo",
                severity="medium"
            ),
            ConcurrentAccessScenario(
                name="Sessões Concorrentes",
                description="Múltiplas sessões simultâneas do mesmo usuário",
                concurrency_type="mixed",
                num_threads=45,
                endpoint="/api/auth/login",
                payload={"email": "test@example.com", "password": "test123"},
                expected_behavior="200 OK com possível invalidação",
                severity="high"
            )
        ]
        
        # Endpoints para testes de concorrência
        self.concurrent_endpoints = [
            "/api/users/profile",
            "/api/v1/payments/process",
            "/api/v1/analytics/advanced",
            "/api/categories/list",
            "/api/executions/create",
            "/api/auth/login",
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
            'concurrent_requests_handled': 0,
            'race_conditions_detected': 0,
            'deadlocks_detected': 0,
            'avg_response_time': 0.0
        }
        
        # Lock para sincronização
        self.lock = threading.Lock()
        self.results_queue = queue.Queue()
        
    def setup_logging(self):
        """Configura logging estruturado"""
        logging.basicConfig(
            level=logging.INFO if self.verbose else logging.WARNING,
            format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
            handlers=[
                logging.FileHandler(f'logs/edge_concurrent_access_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(f"EdgeConcurrentAccessTest_{self.tracing_id}")
        
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
    
    def test_concurrent_access_scenario(self, scenario: ConcurrentAccessScenario) -> Dict[str, Any]:
        """Testa um cenário específico de acesso concorrente"""
        self.log(f"Iniciando teste: {scenario.name} com {scenario.num_threads} threads")
        
        results = {
            'scenario_name': scenario.name,
            'concurrency_type': scenario.concurrency_type,
            'severity': scenario.severity,
            'num_threads': scenario.num_threads,
            'start_time': datetime.now().isoformat(),
            'thread_results': [],
            'race_conditions': [],
            'deadlocks': [],
            'summary': {}
        }
        
        try:
            # Executar threads concorrentes
            with ThreadPoolExecutor(max_workers=scenario.num_threads) as executor:
                futures = []
                
                for i in range(scenario.num_threads):
                    future = executor.submit(
                        self.execute_concurrent_request,
                        scenario,
                        i
                    )
                    futures.append(future)
                
                # Coletar resultados
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        results['thread_results'].append(result)
                    except Exception as e:
                        self.log(f"Erro no thread: {str(e)}", "ERROR")
                        results['thread_results'].append({
                            'thread_id': 'unknown',
                            'success': False,
                            'error': str(e)
                        })
            
            # Analisar resultados para detectar problemas de concorrência
            results['race_conditions'] = self.detect_race_conditions(results['thread_results'])
            results['deadlocks'] = self.detect_deadlocks(results['thread_results'])
            results['summary'] = self.analyze_concurrent_access_results(results['thread_results'])
            results['end_time'] = datetime.now().isoformat()
            
        except Exception as e:
            error_msg = f"Erro durante teste {scenario.name}: {str(e)}"
            self.log(error_msg, "ERROR")
            results['error'] = error_msg
            
        return results
    
    def execute_concurrent_request(self, scenario: ConcurrentAccessScenario, thread_id: int) -> Dict[str, Any]:
        """Executa uma requisição concorrente"""
        start_time = time.time()
        thread_tracing_id = f"{self.tracing_id}_T{thread_id:03d}"
        
        try:
            # Adicionar identificador único ao payload
            payload = scenario.payload.copy()
            if isinstance(payload, dict):
                payload['thread_id'] = thread_id
                payload['timestamp'] = datetime.now().isoformat()
                payload['tracing_id'] = thread_tracing_id
            
            # Fazer requisição
            response = requests.post(
                f"{self.host}{scenario.endpoint}",
                json=payload,
                headers={
                    'Content-Type': 'application/json',
                    'X-Thread-ID': str(thread_id),
                    'X-Tracing-ID': thread_tracing_id
                },
                timeout=30
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Analisar resposta
            is_expected = self.analyze_concurrent_response_behavior(response, scenario)
            
            return {
                'thread_id': thread_id,
                'tracing_id': thread_tracing_id,
                'endpoint': scenario.endpoint,
                'payload': payload,
                'status_code': response.status_code,
                'response_time': response_time,
                'response_body': response.text[:200],  # Primeiros 200 caracteres
                'is_expected_behavior': is_expected,
                'expected_behavior': scenario.expected_behavior,
                'actual_behavior': f"{response.status_code} {response.reason}",
                'timestamp': datetime.now().isoformat(),
                'start_time': start_time,
                'end_time': end_time
            }
            
        except requests.exceptions.Timeout:
            end_time = time.time()
            return {
                'thread_id': thread_id,
                'tracing_id': thread_tracing_id,
                'endpoint': scenario.endpoint,
                'status_code': 'timeout',
                'response_time': end_time - start_time,
                'error': 'Request timeout',
                'is_expected_behavior': False,
                'timestamp': datetime.now().isoformat(),
                'start_time': start_time,
                'end_time': end_time
            }
        except requests.exceptions.ConnectionError:
            end_time = time.time()
            return {
                'thread_id': thread_id,
                'tracing_id': thread_tracing_id,
                'endpoint': scenario.endpoint,
                'status_code': 'connection_error',
                'response_time': end_time - start_time,
                'error': 'Connection error',
                'is_expected_behavior': False,
                'timestamp': datetime.now().isoformat(),
                'start_time': start_time,
                'end_time': end_time
            }
        except Exception as e:
            end_time = time.time()
            return {
                'thread_id': thread_id,
                'tracing_id': thread_tracing_id,
                'endpoint': scenario.endpoint,
                'status_code': 'error',
                'response_time': end_time - start_time,
                'error': str(e),
                'is_expected_behavior': False,
                'timestamp': datetime.now().isoformat(),
                'start_time': start_time,
                'end_time': end_time
            }
    
    def analyze_concurrent_response_behavior(self, response: requests.Response, scenario: ConcurrentAccessScenario) -> bool:
        """Analisa se a resposta está de acordo com o comportamento esperado"""
        expected_status = scenario.expected_behavior.split()[0]
        
        if expected_status == "200":
            return response.status_code == 200
        elif expected_status == "429":
            return response.status_code == 429
        elif expected_status == "503":
            return response.status_code == 503
        elif expected_status == "409":
            return response.status_code == 409
        elif expected_status == "200" and "ou" in scenario.expected_behavior:
            # Caso onde aceita 200 ou 409
            return response.status_code in [200, 409]
        elif expected_status == "429" and "ou" in scenario.expected_behavior:
            # Caso onde aceita 429 ou 503
            return response.status_code in [429, 503]
        
        return False
    
    def detect_race_conditions(self, thread_results: List[Dict]) -> List[Dict]:
        """Detecta possíveis race conditions"""
        race_conditions = []
        
        # Agrupar resultados por endpoint
        endpoint_results = {}
        for result in thread_results:
            endpoint = result.get('endpoint', 'unknown')
            if endpoint not in endpoint_results:
                endpoint_results[endpoint] = []
            endpoint_results[endpoint].append(result)
        
        # Analisar cada endpoint para race conditions
        for endpoint, results in endpoint_results.items():
            if len(results) < 2:
                continue
            
            # Verificar se há respostas inconsistentes para o mesmo recurso
            status_codes = [r.get('status_code') for r in results]
            unique_status_codes = set(status_codes)
            
            if len(unique_status_codes) > 1 and 'error' not in unique_status_codes:
                race_conditions.append({
                    'endpoint': endpoint,
                    'type': 'inconsistent_responses',
                    'status_codes': list(unique_status_codes),
                    'thread_count': len(results),
                    'description': 'Respostas inconsistentes para o mesmo recurso'
                })
            
            # Verificar se há respostas com dados diferentes para o mesmo recurso
            response_bodies = [r.get('response_body', '') for r in results if r.get('status_code') == 200]
            unique_bodies = set(response_bodies)
            
            if len(unique_bodies) > 1:
                race_conditions.append({
                    'endpoint': endpoint,
                    'type': 'inconsistent_data',
                    'unique_responses': len(unique_bodies),
                    'thread_count': len(results),
                    'description': 'Dados inconsistentes retornados para o mesmo recurso'
                })
        
        return race_conditions
    
    def detect_deadlocks(self, thread_results: List[Dict]) -> List[Dict]:
        """Detecta possíveis deadlocks"""
        deadlocks = []
        
        # Verificar se há threads que não retornaram (timeout)
        timeout_threads = [r for r in thread_results if r.get('status_code') == 'timeout']
        
        if len(timeout_threads) > 0:
            deadlocks.append({
                'type': 'timeout_deadlock',
                'timeout_threads': len(timeout_threads),
                'total_threads': len(thread_results),
                'description': f'{len(timeout_threads)} threads não retornaram (possível deadlock)'
            })
        
        # Verificar se há threads com tempo de resposta muito alto
        high_response_times = [r for r in thread_results 
                             if r.get('response_time', 0) > 25]  # > 25 segundos
        
        if len(high_response_times) > len(thread_results) * 0.5:  # Mais de 50% dos threads
            deadlocks.append({
                'type': 'performance_deadlock',
                'slow_threads': len(high_response_times),
                'total_threads': len(thread_results),
                'description': f'{len(high_response_times)} threads com resposta muito lenta'
            })
        
        return deadlocks
    
    def analyze_concurrent_access_results(self, thread_results: List[Dict]) -> Dict[str, Any]:
        """Analisa os resultados dos testes de acesso concorrente"""
        total_threads = len(thread_results)
        successful_threads = sum(1 for r in thread_results if r.get('is_expected_behavior', False))
        failed_threads = total_threads - successful_threads
        
        # Categorizar respostas
        status_codes = {}
        for result in thread_results:
            status = result.get('status_code', 'unknown')
            status_codes[status] = status_codes.get(status, 0) + 1
        
        # Calcular tempo médio de resposta
        response_times = [r.get('response_time', 0) for r in thread_results if 'response_time' in r]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Análise de throughput
        if response_times:
            min_time = min(response_times)
            max_time = max(response_times)
            throughput = total_threads / max_time if max_time > 0 else 0
        else:
            min_time = max_time = throughput = 0
        
        return {
            'total_threads': total_threads,
            'successful_threads': successful_threads,
            'failed_threads': failed_threads,
            'success_rate': successful_threads / total_threads if total_threads > 0 else 0,
            'status_codes_distribution': status_codes,
            'avg_response_time': avg_response_time,
            'min_response_time': min_time,
            'max_response_time': max_time,
            'throughput': throughput
        }
    
    def generate_additional_concurrent_scenarios(self) -> List[ConcurrentAccessScenario]:
        """Gera cenários adicionais de acesso concorrente"""
        additional_scenarios = []
        
        # Cenários com diferentes níveis de concorrência
        concurrency_levels = [
            ("Baixa Concorrência", 10),
            ("Média Concorrência", 50),
            ("Alta Concorrência", 100),
            ("Extrema Concorrência", 200)
        ]
        
        for name, num_threads in concurrency_levels:
            additional_scenarios.append(ConcurrentAccessScenario(
                name=f"Teste de {name}",
                description=f"Teste com {num_threads} threads simultâneos",
                concurrency_type="mixed",
                num_threads=num_threads,
                endpoint="/api/v1/analytics/advanced",
                payload={"start_date": "2024-01-01", "end_date": "2024-12-31"},
                expected_behavior="200 OK com possível degradação",
                severity="medium"
            ))
        
        # Cenários de stress test
        stress_scenarios = [
            ("Stress Test - Pagamentos", "/api/v1/payments/process", {"amount": 100.00, "currency": "BRL"}),
            ("Stress Test - Analytics", "/api/v1/analytics/trends", {"period": "daily"}),
            ("Stress Test - Relatórios", "/api/reports/generate", {"report_type": "performance"}),
            ("Stress Test - Execuções", "/api/executions/create", {"keywords": ["stress", "test"], "category": "test"})
        ]
        
        for name, endpoint, payload in stress_scenarios:
            additional_scenarios.append(ConcurrentAccessScenario(
                name=name,
                description=f"Stress test com 150 threads em {endpoint}",
                concurrency_type="resource_contention",
                num_threads=150,
                endpoint=endpoint,
                payload=payload,
                expected_behavior="429 Too Many Requests ou degradação",
                severity="high"
            ))
        
        return additional_scenarios
    
    def run(self) -> Dict[str, Any]:
        """Executa todos os testes de acesso concorrente"""
        self.log("🚀 Iniciando testes de Edge Cases - Acesso Concorrente")
        
        all_results = {
            'tracing_id': self.tracing_id,
            'start_time': self.start_time.isoformat(),
            'host': self.host,
            'scenarios': [],
            'additional_scenarios': [],
            'summary': {},
            'concurrency_analysis': {}
        }
        
        try:
            # Executar cenários básicos
            for i, scenario in enumerate(self.concurrent_access_scenarios):
                self.log(f"Executando cenário {i+1}/{len(self.concurrent_access_scenarios)}: {scenario.name}")
                
                scenario_result = self.test_concurrent_access_scenario(scenario)
                scenario_result['scenario_index'] = i + 1
                
                all_results['scenarios'].append(scenario_result)
                
                # Atualizar métricas
                self.metrics['scenarios_executed'] += 1
                if scenario_result.get('summary', {}).get('success_rate', 0) >= 0.8:
                    self.metrics['scenarios_failed'] += 1
                
                # Pausa entre cenários
                if i < len(self.concurrent_access_scenarios) - 1:
                    time.sleep(3)  # Pausa maior para testes de concorrência
            
            # Executar cenários adicionais
            self.log("Executando cenários adicionais de acesso concorrente")
            additional_scenarios = self.generate_additional_concurrent_scenarios()
            
            for i, scenario in enumerate(additional_scenarios):
                scenario_result = self.test_concurrent_access_scenario(scenario)
                scenario_result['scenario_index'] = i + 1
                scenario_result['is_additional_test'] = True
                
                all_results['additional_scenarios'].append(scenario_result)
                
                # Pausa entre cenários
                if i < len(additional_scenarios) - 1:
                    time.sleep(3)
            
            # Gerar resumo geral
            all_results['summary'] = self.generate_overall_summary(all_results)
            all_results['concurrency_analysis'] = self.analyze_concurrency_issues(all_results)
            all_results['end_time'] = datetime.now().isoformat()
            
            # Calcular sucesso geral
            total_scenarios = len(all_results['scenarios']) + len(all_results['additional_scenarios'])
            successful_scenarios = sum(1 for s in all_results['scenarios'] 
                                     if s.get('summary', {}).get('success_rate', 0) >= 0.8)
            success_rate = successful_scenarios / total_scenarios if total_scenarios > 0 else 0
            
            all_results['success'] = success_rate >= 0.9  # 90% de sucesso mínimo
            
            self.log(f"✅ Testes de acesso concorrente concluídos: {success_rate:.1%} de sucesso")
            
        except Exception as e:
            error_msg = f"Erro durante execução dos testes: {str(e)}"
            self.log(error_msg, "ERROR")
            all_results['success'] = False
            all_results['error'] = error_msg
        
        return all_results
    
    def generate_overall_summary(self, all_results: Dict) -> Dict[str, Any]:
        """Gera resumo geral dos resultados"""
        all_scenarios = all_results['scenarios'] + all_results['additional_scenarios']
        
        total_scenarios = len(all_scenarios)
        total_threads = sum(s.get('num_threads', 0) for s in all_scenarios)
        
        # Análise por tipo de concorrência
        concurrency_type_analysis = {}
        for scenario in all_scenarios:
            concurrency_type = scenario.get('concurrency_type', 'unknown')
            if concurrency_type not in concurrency_type_analysis:
                concurrency_type_analysis[concurrency_type] = {'count': 0, 'success_rate': 0}
            
            concurrency_type_analysis[concurrency_type]['count'] += 1
            success_rate = scenario.get('summary', {}).get('success_rate', 0)
            concurrency_type_analysis[concurrency_type]['success_rate'] += success_rate
        
        # Calcular média por tipo
        for concurrency_type in concurrency_type_analysis:
            count = concurrency_type_analysis[concurrency_type]['count']
            if count > 0:
                concurrency_type_analysis[concurrency_type]['success_rate'] /= count
        
        return {
            'total_scenarios': total_scenarios,
            'total_threads': total_threads,
            'concurrency_type_analysis': concurrency_type_analysis,
            'additional_tests': len(all_results['additional_scenarios']),
            'basic_tests': len(all_results['scenarios'])
        }
    
    def analyze_concurrency_issues(self, all_results: Dict) -> Dict[str, Any]:
        """Analisa problemas de concorrência encontrados"""
        all_scenarios = all_results['scenarios'] + all_results['additional_scenarios']
        
        concurrency_issues = {
            'total_race_conditions': 0,
            'total_deadlocks': 0,
            'scenarios_with_issues': 0,
            'critical_issues': 0,
            'performance_degradation': 0,
            'resource_contention': 0
        }
        
        for scenario in all_scenarios:
            race_conditions = scenario.get('race_conditions', [])
            deadlocks = scenario.get('deadlocks', [])
            
            concurrency_issues['total_race_conditions'] += len(race_conditions)
            concurrency_issues['total_deadlocks'] += len(deadlocks)
            
            if race_conditions or deadlocks:
                concurrency_issues['scenarios_with_issues'] += 1
            
            # Verificar se há problemas críticos
            if scenario.get('severity') == 'critical' and (race_conditions or deadlocks):
                concurrency_issues['critical_issues'] += 1
            
            # Verificar degradação de performance
            summary = scenario.get('summary', {})
            if summary.get('avg_response_time', 0) > 10:  # > 10 segundos
                concurrency_issues['performance_degradation'] += 1
            
            # Verificar contenção de recursos
            if scenario.get('concurrency_type') == 'resource_contention':
                concurrency_issues['resource_contention'] += 1
        
        return concurrency_issues


def main():
    """Função principal para execução standalone"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Teste de Edge Cases - Acesso Concorrente")
    parser.add_argument('--host', default='http://localhost:8000', help='Host para testar')
    parser.add_argument('--verbose', action='store_true', help='Modo verboso')
    
    args = parser.parse_args()
    
    # Criar e executar teste
    test = EdgeCasesConcurrentAccessTest(host=args.host, verbose=args.verbose)
    result = test.run()
    
    # Imprimir resultados
    print("\n" + "="*80)
    print("📊 RESULTADOS DOS TESTES DE ACESSO CONCORRENTE")
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
        print(f"   • Total de Threads: {summary['total_threads']}")
        print(f"   • Testes Adicionais: {summary['additional_tests']}")
        print(f"   • Testes Básicos: {summary['basic_tests']}")
    
    if 'concurrency_analysis' in result:
        analysis = result['concurrency_analysis']
        print(f"\n🔍 ANÁLISE DE CONCORRÊNCIA:")
        print(f"   • Race Conditions Detectadas: {analysis['total_race_conditions']}")
        print(f"   • Deadlocks Detectados: {analysis['total_deadlocks']}")
        print(f"   • Cenários com Problemas: {analysis['scenarios_with_issues']}")
        print(f"   • Problemas Críticos: {analysis['critical_issues']}")
        print(f"   • Degradação de Performance: {analysis['performance_degradation']}")
        print(f"   • Contenção de Recursos: {analysis['resource_contention']}")
    
    print("="*80)


if __name__ == "__main__":
    main() 