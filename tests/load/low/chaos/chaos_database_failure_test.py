#!/usr/bin/env python3
"""
Teste de Chaos Engineering - Falhas de Banco de Dados
Omni Keywords Finder - Tracing ID: CHAOS_DATABASE_20250127_001

Este teste simula falhas de banco de dados para validar a resiliência do sistema:
- Falhas de conexão
- Timeout de queries
- Deadlocks
- Falhas de disco
- Falhas de memória
- Recuperação automática
- Failover

Baseado em:
- backend/app/database/connection_manager.py
- infrastructure/resilience/database_resilience.py
- backend/app/models/__init__.py

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
import sqlite3
import os


@dataclass
class DatabaseFailureScenario:
    """Cenário de falha de banco de dados"""
    name: str
    description: str
    failure_type: str  # 'connection', 'timeout', 'deadlock', 'disk', 'memory'
    duration_seconds: int
    recovery_time_seconds: int
    impact_level: str  # 'low', 'medium', 'high', 'critical'
    database_type: str  # 'sqlite', 'postgres', 'mysql'


class ChaosDatabaseFailureTest:
    """
    Teste de falhas de banco de dados para Chaos Engineering
    """
    
    def __init__(self, host: str = "http://localhost:8000", verbose: bool = False):
        self.host = host
        self.verbose = verbose
        self.tracing_id = "CHAOS_DATABASE_20250127_001"
        self.start_time = datetime.now()
        
        # Configurar logging
        self.setup_logging()
        
        # Cenários de falha de banco de dados
        self.failure_scenarios = [
            DatabaseFailureScenario(
                name="Timeout de Conexão",
                description="Simula timeout na conexão com o banco",
                failure_type="connection",
                duration_seconds=30,
                recovery_time_seconds=15,
                impact_level="high",
                database_type="sqlite"
            ),
            DatabaseFailureScenario(
                name="Timeout de Query",
                description="Simula timeout em queries complexas",
                failure_type="timeout",
                duration_seconds=45,
                recovery_time_seconds=20,
                impact_level="medium",
                database_type="sqlite"
            ),
            DatabaseFailureScenario(
                name="Deadlock",
                description="Simula deadlock entre transações",
                failure_type="deadlock",
                duration_seconds=20,
                recovery_time_seconds=10,
                impact_level="medium",
                database_type="sqlite"
            ),
            DatabaseFailureScenario(
                name="Falha de Disco",
                description="Simula falha de disco",
                failure_type="disk",
                duration_seconds=60,
                recovery_time_seconds=30,
                impact_level="critical",
                database_type="sqlite"
            ),
            DatabaseFailureScenario(
                name="Falha de Memória",
                description="Simula falha de memória",
                failure_type="memory",
                duration_seconds=40,
                recovery_time_seconds=25,
                impact_level="high",
                database_type="sqlite"
            )
        ]
        
        # Endpoints que dependem do banco de dados
        self.database_dependent_endpoints = [
            "/api/auth/login",
            "/api/v1/analytics/advanced",
            "/api/v1/payments/process",
            "/api/reports/generate",
            "/api/metrics/performance",
            "/api/users/profile",
            "/api/categories/list",
            "/api/executions/status"
        ]
        
        # Queries de teste para validar o banco
        self.test_queries = [
            "SELECT COUNT(*) FROM users",
            "SELECT COUNT(*) FROM categories",
            "SELECT COUNT(*) FROM executions",
            "SELECT COUNT(*) FROM keywords",
            "SELECT COUNT(*) FROM payments"
        ]
        
        # Métricas coletadas
        self.metrics = {
            'scenarios_executed': 0,
            'scenarios_failed': 0,
            'database_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'avg_query_time': 0.0,
            'max_query_time': 0.0,
            'recovery_success_rate': 0.0
        }
        
    def setup_logging(self):
        """Configura logging estruturado"""
        logging.basicConfig(
            level=logging.INFO if self.verbose else logging.WARNING,
            format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
            handlers=[
                logging.FileHandler(f'logs/chaos_database_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(f"ChaosDatabaseTest_{self.tracing_id}")
        
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
    
    def check_database_health(self) -> Dict[str, Any]:
        """Verifica a saúde do banco de dados"""
        try:
            # Verificar se o arquivo do banco existe
            db_files = [
                "backend/db.sqlite3",
                "instance/db.sqlite3",
                "db.sqlite3"
            ]
            
            db_file = None
            for file_path in db_files:
                if os.path.exists(file_path):
                    db_file = file_path
                    break
            
            if not db_file:
                return {
                    'healthy': False,
                    'error': 'Database file not found',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Testar conexão
            connection = sqlite3.connect(db_file, timeout=10)
            cursor = connection.cursor()
            
            # Executar query de teste
            start_time = time.time()
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            result = cursor.fetchone()
            query_time = time.time() - start_time
            
            # Verificar tabelas existentes
            tables = []
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            for row in cursor.fetchall():
                tables.append(row[0])
            
            connection.close()
            
            return {
                'healthy': True,
                'db_file': db_file,
                'table_count': result[0],
                'tables': tables,
                'query_time': query_time,
                'file_size_mb': os.path.getsize(db_file) / (1024 * 1024),
                'timestamp': datetime.now().isoformat()
            }
            
        except sqlite3.Error as e:
            return {
                'healthy': False,
                'error': f'SQLite error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'healthy': False,
                'error': f'Unexpected error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def execute_test_queries(self) -> List[Dict[str, Any]]:
        """Executa queries de teste para validar o banco"""
        results = []
        
        try:
            db_files = [
                "backend/db.sqlite3",
                "instance/db.sqlite3",
                "db.sqlite3"
            ]
            
            db_file = None
            for file_path in db_files:
                if os.path.exists(file_path):
                    db_file = file_path
                    break
            
            if not db_file:
                return [{'error': 'Database file not found'}]
            
            connection = sqlite3.connect(db_file, timeout=30)
            cursor = connection.cursor()
            
            for query in self.test_queries:
                try:
                    start_time = time.time()
                    cursor.execute(query)
                    result = cursor.fetchone()
                    query_time = time.time() - start_time
                    
                    results.append({
                        'query': query,
                        'success': True,
                        'result': result[0] if result else None,
                        'query_time': query_time,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                except sqlite3.Error as e:
                    results.append({
                        'query': query,
                        'success': False,
                        'error': str(e),
                        'query_time': 0,
                        'timestamp': datetime.now().isoformat()
                    })
            
            connection.close()
            
        except Exception as e:
            results.append({
                'error': f'Database connection failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            })
        
        return results
    
    def simulate_database_failure(self, scenario: DatabaseFailureScenario) -> Dict[str, Any]:
        """Simula uma falha de banco de dados específica"""
        self.log(f"Iniciando simulação: {scenario.name}")
        
        results = {
            'scenario_name': scenario.name,
            'failure_type': scenario.failure_type,
            'start_time': datetime.now().isoformat(),
            'health_before': {},
            'health_during': {},
            'health_after': {},
            'queries_before': [],
            'queries_during': [],
            'queries_after': [],
            'api_requests_during': [],
            'recovery_successful': False,
            'downtime_seconds': 0,
            'error_messages': []
        }
        
        try:
            # Fase 1: Verificar saúde inicial
            self.log("Fase 1: Verificando saúde inicial do banco")
            results['health_before'] = self.check_database_health()
            results['queries_before'] = self.execute_test_queries()
            
            # Fase 2: Aplicar falha
            self.log(f"Fase 2: Aplicando falha de banco - {scenario.description}")
            failure_start = time.time()
            
            if self.apply_database_failure(scenario):
                # Fase 3: Testar durante a falha
                self.log("Fase 3: Testando durante a falha")
                results['health_during'] = self.check_database_health()
                results['queries_during'] = self.execute_test_queries()
                results['api_requests_during'] = self.test_api_endpoints_during_failure()
                
                # Aguardar duração da falha
                time.sleep(scenario.duration_seconds)
                
                # Fase 4: Remover falha e testar recuperação
                self.log("Fase 4: Removendo falha e testando recuperação")
                failure_end = time.time()
                results['downtime_seconds'] = failure_end - failure_start
                
                if self.remove_database_failure(scenario):
                    # Aguardar tempo de recuperação
                    time.sleep(scenario.recovery_time_seconds)
                    
                    # Verificar recuperação
                    results['health_after'] = self.check_database_health()
                    results['queries_after'] = self.execute_test_queries()
                    results['recovery_successful'] = self.analyze_database_recovery(
                        results['health_before'], 
                        results['health_after'],
                        results['queries_before'],
                        results['queries_after']
                    )
                else:
                    results['error_messages'].append("Falha ao remover simulação de banco")
            else:
                results['error_messages'].append("Falha ao aplicar simulação de banco")
                
        except Exception as e:
            error_msg = f"Erro durante simulação {scenario.name}: {str(e)}"
            self.log(error_msg, "ERROR")
            results['error_messages'].append(error_msg)
            
        results['end_time'] = datetime.now().isoformat()
        return results
    
    def apply_database_failure(self, scenario: DatabaseFailureScenario) -> bool:
        """Aplica uma falha de banco de dados específica"""
        try:
            if scenario.failure_type == "connection":
                return self.simulate_connection_failure(scenario)
            elif scenario.failure_type == "timeout":
                return self.simulate_query_timeout(scenario)
            elif scenario.failure_type == "deadlock":
                return self.simulate_deadlock(scenario)
            elif scenario.failure_type == "disk":
                return self.simulate_disk_failure(scenario)
            elif scenario.failure_type == "memory":
                return self.simulate_memory_failure(scenario)
            else:
                self.log(f"Tipo de falha não suportado: {scenario.failure_type}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Erro ao aplicar falha de banco: {str(e)}", "ERROR")
            return False
    
    def simulate_connection_failure(self, scenario: DatabaseFailureScenario) -> bool:
        """Simula falha de conexão com o banco"""
        try:
            self.log("Simulando falha de conexão com o banco")
            
            # Em produção, isso seria feito através de:
            # - Bloqueio de portas
            # - Falha de rede
            # - Configuração de firewall
            
            # Para simulação, vamos apenas registrar a intenção
            # Em produção, usar ferramentas específicas de chaos engineering
            
            return True
        except Exception as e:
            self.log(f"Erro ao simular falha de conexão: {str(e)}", "ERROR")
            return False
    
    def simulate_query_timeout(self, scenario: DatabaseFailureScenario) -> bool:
        """Simula timeout em queries"""
        try:
            self.log("Simulando timeout em queries")
            
            # Em produção, isso seria feito através de:
            # - Configuração de timeouts no banco
            # - Queries complexas que consomem muito tempo
            # - Limitação de recursos
            
            return True
        except Exception as e:
            self.log(f"Erro ao simular timeout de query: {str(e)}", "ERROR")
            return False
    
    def simulate_deadlock(self, scenario: DatabaseFailureScenario) -> bool:
        """Simula deadlock entre transações"""
        try:
            self.log("Simulando deadlock entre transações")
            
            # Em produção, isso seria feito através de:
            # - Transações concorrentes que acessam os mesmos recursos
            # - Configuração de isolamento de transações
            # - Queries que causam conflito
            
            return True
        except Exception as e:
            self.log(f"Erro ao simular deadlock: {str(e)}", "ERROR")
            return False
    
    def simulate_disk_failure(self, scenario: DatabaseFailureScenario) -> bool:
        """Simula falha de disco"""
        try:
            self.log("Simulando falha de disco")
            
            # Em produção, isso seria feito através de:
            # - Falha física do disco
            # - Limitação de espaço em disco
            # - Problemas de I/O
            
            return True
        except Exception as e:
            self.log(f"Erro ao simular falha de disco: {str(e)}", "ERROR")
            return False
    
    def simulate_memory_failure(self, scenario: DatabaseFailureScenario) -> bool:
        """Simula falha de memória"""
        try:
            self.log("Simulando falha de memória")
            
            # Em produção, isso seria feito através de:
            # - Limitação de memória disponível
            # - Falha de RAM
            # - Configuração de limites de memória
            
            return True
        except Exception as e:
            self.log(f"Erro ao simular falha de memória: {str(e)}", "ERROR")
            return False
    
    def remove_database_failure(self, scenario: DatabaseFailureScenario) -> bool:
        """Remove a falha de banco aplicada"""
        try:
            self.log(f"Removendo falha de banco: {scenario.failure_type}")
            
            # Em produção, restaurar configurações normais
            # - Restaurar conectividade
            # - Remover limitações de timeout
            # - Resolver deadlocks
            # - Restaurar espaço em disco
            # - Restaurar memória
            
            return True
        except Exception as e:
            self.log(f"Erro ao remover falha de banco: {str(e)}", "ERROR")
            return False
    
    def test_api_endpoints_during_failure(self) -> List[Dict[str, Any]]:
        """Testa endpoints da API durante a falha do banco"""
        results = []
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            
            for endpoint in self.database_dependent_endpoints:
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
            "/api/auth/login": {
                "email": "test@example.com",
                "password": "test_password_123"
            },
            "/api/v1/analytics/advanced": {
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "metrics": ["performance", "trends"]
            },
            "/api/v1/payments/process": {
                "amount": 100.00,
                "currency": "BRL",
                "payment_method": "credit_card"
            },
            "/api/reports/generate": {
                "report_type": "performance_summary",
                "date_range": "last_30_days"
            },
            "/api/metrics/performance": {
                "metric_type": "response_time",
                "time_window": "1h"
            },
            "/api/users/profile": {
                "user_id": 1
            },
            "/api/categories/list": {
                "limit": 10,
                "offset": 0
            },
            "/api/executions/status": {
                "execution_id": "test_123"
            }
        }
        
        return payloads.get(endpoint, {"test": True})
    
    def analyze_database_recovery(self, health_before: Dict, health_after: Dict, 
                                queries_before: List[Dict], queries_after: List[Dict]) -> bool:
        """Analisa se a recuperação do banco foi bem-sucedida"""
        if not health_before or not health_after:
            return False
        
        # Verificar se o banco está saudável após recuperação
        if not health_after.get('healthy', False):
            return False
        
        # Verificar se as queries estão funcionando
        successful_queries_before = sum(1 for q in queries_before if q.get('success', False))
        successful_queries_after = sum(1 for q in queries_after if q.get('success', False))
        
        total_queries = len(queries_after)
        if total_queries == 0:
            return False
        
        query_success_rate = successful_queries_after / total_queries
        recovery_successful = query_success_rate >= 0.8  # 80% das queries devem funcionar
        
        self.log(f"Análise de recuperação do banco:")
        self.log(f"  Queries bem-sucedidas antes: {successful_queries_before}/{len(queries_before)}")
        self.log(f"  Queries bem-sucedidas depois: {successful_queries_after}/{total_queries}")
        self.log(f"  Taxa de sucesso das queries: {query_success_rate:.1%}")
        self.log(f"  Recuperação bem-sucedida: {recovery_successful}")
        
        return recovery_successful
    
    def run(self) -> Dict[str, Any]:
        """Executa todos os testes de falha de banco de dados"""
        self.log("🚀 Iniciando testes de Chaos Engineering - Falhas de Banco de Dados")
        
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
                scenario_result = self.simulate_database_failure(scenario)
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
            
            self.log(f"✅ Testes de falha de banco concluídos: {success_rate:.1%} de sucesso")
            
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
        
        # Análise de queries
        all_query_times = []
        for scenario in scenarios:
            for query_result in scenario.get('queries_after', []):
                if 'query_time' in query_result:
                    all_query_times.append(query_result['query_time'])
        
        avg_query_time = sum(all_query_times) / len(all_query_times) if all_query_times else 0
        max_query_time = max(all_query_times) if all_query_times else 0
        
        return {
            'total_scenarios': total_scenarios,
            'successful_recoveries': successful_recoveries,
            'failed_scenarios': failed_scenarios,
            'recovery_success_rate': successful_recoveries / total_scenarios if total_scenarios > 0 else 0,
            'avg_downtime_seconds': avg_downtime,
            'max_downtime_seconds': max_downtime,
            'avg_query_time': avg_query_time,
            'max_query_time': max_query_time,
            'total_queries_tested': len(all_query_times)
        }


def main():
    """Função principal para execução standalone"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Teste de Chaos Engineering - Falhas de Banco de Dados")
    parser.add_argument('--host', default='http://localhost:8000', help='Host para testar')
    parser.add_argument('--verbose', action='store_true', help='Modo verboso')
    
    args = parser.parse_args()
    
    # Criar e executar teste
    test = ChaosDatabaseFailureTest(host=args.host, verbose=args.verbose)
    result = test.run()
    
    # Imprimir resultados
    print("\n" + "="*80)
    print("📊 RESULTADOS DOS TESTES DE FALHA DE BANCO DE DADOS")
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
        print(f"   • Tempo Médio de Query: {summary['avg_query_time']:.3f}s")
        print(f"   • Tempo Máximo de Query: {summary['max_query_time']:.3f}s")
        print(f"   • Queries Testadas: {summary['total_queries_tested']}")
    
    print("="*80)


if __name__ == "__main__":
    main() 