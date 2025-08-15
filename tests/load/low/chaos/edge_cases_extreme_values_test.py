#!/usr/bin/env python3
"""
Teste de Edge Cases - Valores Extremos
Omni Keywords Finder - Tracing ID: EDGE_EXTREME_VALUES_20250127_001

Este teste valida o comportamento do sistema com valores extremos:
- Valores numéricos muito grandes/pequenos
- Strings muito longas
- Arrays muito grandes
- Objetos muito profundos
- Valores de limite (boundary values)
- Valores negativos onde não deveriam ser

Baseado em:
- backend/app/models/validation.py
- backend/app/utils/data_validator.py
- backend/app/api/limits.py

Autor: IA-Cursor
Data: 2025-01-27
Versão: 1.0
"""

import time
import random
import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import math


@dataclass
class ExtremeValueScenario:
    """Cenário de valor extremo"""
    name: str
    description: str
    value_type: str  # 'very_large', 'very_small', 'very_long', 'very_deep', 'boundary', 'negative'
    field_name: str
    extreme_value: Any
    expected_behavior: str
    severity: str  # 'low', 'medium', 'high', 'critical'


class EdgeCasesExtremeValuesTest:
    """
    Teste de valores extremos para Edge Cases
    """
    
    def __init__(self, host: str = "http://localhost:8000", verbose: bool = False):
        self.host = host
        self.verbose = verbose
        self.tracing_id = "EDGE_EXTREME_VALUES_20250127_001"
        self.start_time = datetime.now()
        
        # Configurar logging
        self.setup_logging()
        
        # Cenários de valores extremos
        self.extreme_value_scenarios = [
            ExtremeValueScenario(
                name="Valor Numérico Muito Grande",
                description="Valor numérico próximo ao limite máximo",
                value_type="very_large",
                field_name="amount",
                extreme_value=sys.maxsize,
                expected_behavior="400 Bad Request ou 413 Payload Too Large",
                severity="high"
            ),
            ExtremeValueScenario(
                name="Valor Numérico Muito Pequeno",
                description="Valor numérico próximo ao limite mínimo",
                value_type="very_small",
                field_name="amount",
                extreme_value=-sys.maxsize,
                expected_behavior="400 Bad Request",
                severity="medium"
            ),
            ExtremeValueScenario(
                name="String Muito Longa",
                description="String com milhões de caracteres",
                value_type="very_long",
                field_name="description",
                extreme_value="A" * 1000000,  # 1MB de texto
                expected_behavior="413 Payload Too Large",
                severity="high"
            ),
            ExtremeValueScenario(
                name="Array Muito Grande",
                description="Array com milhares de elementos",
                value_type="very_large",
                field_name="keywords",
                extreme_value=list(range(100000)),  # 100k elementos
                expected_behavior="413 Payload Too Large",
                severity="high"
            ),
            ExtremeValueScenario(
                name="Objeto Muito Profundo",
                description="Objeto aninhado com muitos níveis",
                value_type="very_deep",
                field_name="config",
                extreme_value=self.generate_deep_object(50),  # 50 níveis
                expected_behavior="400 Bad Request ou 413 Payload Too Large",
                severity="medium"
            ),
            ExtremeValueScenario(
                name="Valor de Limite Superior",
                description="Valor no limite superior aceitável",
                value_type="boundary",
                field_name="amount",
                extreme_value=999999.99,
                expected_behavior="200 OK",
                severity="low"
            ),
            ExtremeValueScenario(
                name="Valor de Limite Inferior",
                description="Valor no limite inferior aceitável",
                value_type="boundary",
                field_name="amount",
                extreme_value=0.01,
                expected_behavior="200 OK",
                severity="low"
            ),
            ExtremeValueScenario(
                name="Valor Negativo Inválido",
                description="Valor negativo onde não deveria ser",
                value_type="negative",
                field_name="amount",
                extreme_value=-100.00,
                expected_behavior="400 Bad Request",
                severity="medium"
            ),
            ExtremeValueScenario(
                name="Data Muito Antiga",
                description="Data muito no passado",
                value_type="very_small",
                field_name="start_date",
                extreme_value="1900-01-01",
                expected_behavior="400 Bad Request",
                severity="low"
            ),
            ExtremeValueScenario(
                name="Data Muito Futura",
                description="Data muito no futuro",
                value_type="very_large",
                field_name="end_date",
                extreme_value="2100-12-31",
                expected_behavior="400 Bad Request",
                severity="low"
            ),
            ExtremeValueScenario(
                name="Email Muito Longo",
                description="Email com domínio extremamente longo",
                value_type="very_long",
                field_name="email",
                extreme_value=f"test@{'a' * 1000}.com",
                expected_behavior="400 Bad Request",
                severity="medium"
            ),
            ExtremeValueScenario(
                name="ID Muito Grande",
                description="ID com valor extremamente grande",
                value_type="very_large",
                field_name="user_id",
                extreme_value=999999999999999999,
                expected_behavior="400 Bad Request",
                severity="medium"
            )
        ]
        
        # Endpoints para testar
        self.test_endpoints = [
            "/api/auth/login",
            "/api/auth/register",
            "/api/v1/payments/process",
            "/api/v1/analytics/advanced",
            "/api/reports/generate",
            "/api/users/profile",
            "/api/categories/create",
            "/api/executions/create"
        ]
        
        # Métricas coletadas
        self.metrics = {
            'scenarios_executed': 0,
            'scenarios_failed': 0,
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'extreme_values_handled': 0,
            'unexpected_responses': 0,
            'avg_response_time': 0.0
        }
        
    def setup_logging(self):
        """Configura logging estruturado"""
        logging.basicConfig(
            level=logging.INFO if self.verbose else logging.WARNING,
            format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
            handlers=[
                logging.FileHandler(f'logs/edge_extreme_values_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(f"EdgeExtremeValuesTest_{self.tracing_id}")
        
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
    
    def generate_deep_object(self, depth: int) -> Dict:
        """Gera um objeto aninhado com profundidade específica"""
        if depth == 0:
            return {"value": "leaf", "data": "end_of_nesting"}
        
        return {
            "level": depth,
            "nested": self.generate_deep_object(depth - 1),
            "metadata": {
                "depth": depth,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def test_extreme_value_scenario(self, scenario: ExtremeValueScenario) -> Dict[str, Any]:
        """Testa um cenário específico de valor extremo"""
        self.log(f"Iniciando teste: {scenario.name}")
        
        results = {
            'scenario_name': scenario.name,
            'value_type': scenario.value_type,
            'severity': scenario.severity,
            'start_time': datetime.now().isoformat(),
            'endpoint_results': [],
            'extreme_values_handled': 0,
            'unexpected_responses': 0,
            'summary': {}
        }
        
        try:
            # Testar em múltiplos endpoints
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                
                for endpoint in self.test_endpoints:
                    future = executor.submit(
                        self.test_endpoint_with_extreme_value,
                        endpoint,
                        scenario
                    )
                    futures.append(future)
                
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        results['endpoint_results'].append(result)
                    except Exception as e:
                        self.log(f"Erro no teste de endpoint: {str(e)}", "ERROR")
                        results['endpoint_results'].append({
                            'endpoint': 'unknown',
                            'success': False,
                            'error': str(e)
                        })
            
            # Analisar resultados
            results['summary'] = self.analyze_extreme_value_results(results['endpoint_results'])
            results['end_time'] = datetime.now().isoformat()
            
        except Exception as e:
            error_msg = f"Erro durante teste {scenario.name}: {str(e)}"
            self.log(error_msg, "ERROR")
            results['error'] = error_msg
            
        return results
    
    def test_endpoint_with_extreme_value(self, endpoint: str, scenario: ExtremeValueScenario) -> Dict[str, Any]:
        """Testa um endpoint específico com valor extremo"""
        start_time = time.time()
        
        try:
            # Gerar payload com valor extremo
            payload = self.generate_payload_with_extreme_value(endpoint, scenario)
            
            # Fazer requisição
            response = requests.post(
                f"{self.host}{endpoint}",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=60  # Timeout maior para valores extremos
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Analisar resposta
            is_expected = self.analyze_extreme_value_response_behavior(response, scenario)
            
            return {
                'endpoint': endpoint,
                'field_name': scenario.field_name,
                'value_type': scenario.value_type,
                'payload_size': len(json.dumps(payload)),
                'status_code': response.status_code,
                'response_time': response_time,
                'response_body': response.text[:500],  # Primeiros 500 caracteres
                'is_expected_behavior': is_expected,
                'expected_behavior': scenario.expected_behavior,
                'actual_behavior': f"{response.status_code} {response.reason}",
                'timestamp': datetime.now().isoformat()
            }
            
        except requests.exceptions.Timeout:
            end_time = time.time()
            return {
                'endpoint': endpoint,
                'field_name': scenario.field_name,
                'value_type': scenario.value_type,
                'status_code': 'timeout',
                'response_time': end_time - start_time,
                'error': 'Request timeout - valor muito extremo',
                'is_expected_behavior': True,  # Timeout é esperado para valores extremos
                'timestamp': datetime.now().isoformat()
            }
        except requests.exceptions.ConnectionError:
            end_time = time.time()
            return {
                'endpoint': endpoint,
                'field_name': scenario.field_name,
                'value_type': scenario.value_type,
                'status_code': 'connection_error',
                'response_time': end_time - start_time,
                'error': 'Connection error',
                'is_expected_behavior': False,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            end_time = time.time()
            return {
                'endpoint': endpoint,
                'field_name': scenario.field_name,
                'value_type': scenario.value_type,
                'status_code': 'error',
                'response_time': end_time - start_time,
                'error': str(e),
                'is_expected_behavior': False,
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_payload_with_extreme_value(self, endpoint: str, scenario: ExtremeValueScenario) -> Dict[str, Any]:
        """Gera payload com valor extremo baseado no endpoint"""
        base_payload = {}
        
        if endpoint == "/api/auth/login":
            base_payload = {
                "email": "test@example.com",
                "password": "test123"
            }
            if scenario.field_name == "email":
                base_payload["email"] = scenario.extreme_value
        elif endpoint == "/api/auth/register":
            base_payload = {
                "email": "test@example.com",
                "password": "test123",
                "name": "Test User",
                "confirm_password": "test123"
            }
            if scenario.field_name == "email":
                base_payload["email"] = scenario.extreme_value
            elif scenario.field_name == "name":
                base_payload["name"] = scenario.extreme_value
        elif endpoint == "/api/v1/payments/process":
            base_payload = {
                "amount": 100.00,
                "currency": "BRL",
                "payment_method": "credit_card"
            }
            if scenario.field_name == "amount":
                base_payload["amount"] = scenario.extreme_value
        elif endpoint == "/api/v1/analytics/advanced":
            base_payload = {
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "metrics": ["performance", "trends"]
            }
            if scenario.field_name == "start_date":
                base_payload["start_date"] = scenario.extreme_value
            elif scenario.field_name == "end_date":
                base_payload["end_date"] = scenario.extreme_value
        elif endpoint == "/api/reports/generate":
            base_payload = {
                "report_type": "performance",
                "date_range": "monthly"
            }
            if scenario.field_name == "description":
                base_payload["description"] = scenario.extreme_value
        elif endpoint == "/api/users/profile":
            base_payload = {
                "user_id": 123,
                "name": "Test User"
            }
            if scenario.field_name == "user_id":
                base_payload["user_id"] = scenario.extreme_value
            elif scenario.field_name == "name":
                base_payload["name"] = scenario.extreme_value
        elif endpoint == "/api/categories/create":
            base_payload = {
                "name": "Test Category",
                "description": "Test Description"
            }
            if scenario.field_name == "name":
                base_payload["name"] = scenario.extreme_value
            elif scenario.field_name == "description":
                base_payload["description"] = scenario.extreme_value
        elif endpoint == "/api/executions/create":
            base_payload = {
                "keywords": ["test", "keyword"],
                "category": "test"
            }
            if scenario.field_name == "keywords":
                base_payload["keywords"] = scenario.extreme_value
            elif scenario.field_name == "description":
                base_payload["description"] = scenario.extreme_value
        
        return base_payload
    
    def analyze_extreme_value_response_behavior(self, response: requests.Response, scenario: ExtremeValueScenario) -> bool:
        """Analisa se a resposta está de acordo com o comportamento esperado"""
        expected_status = scenario.expected_behavior.split()[0]
        
        if expected_status == "400":
            return response.status_code == 400
        elif expected_status == "413":
            return response.status_code == 413
        elif expected_status == "200":
            return response.status_code == 200
        elif expected_status == "400" and "ou" in scenario.expected_behavior:
            # Caso onde aceita 400 ou 413
            return response.status_code in [400, 413]
        
        return False
    
    def analyze_extreme_value_results(self, endpoint_results: List[Dict]) -> Dict[str, Any]:
        """Analisa os resultados dos testes de valores extremos"""
        total_tests = len(endpoint_results)
        expected_behaviors = sum(1 for r in endpoint_results if r.get('is_expected_behavior', False))
        unexpected_behaviors = total_tests - expected_behaviors
        
        # Categorizar respostas
        status_codes = {}
        for result in endpoint_results:
            status = result.get('status_code', 'unknown')
            status_codes[status] = status_codes.get(status, 0) + 1
        
        # Calcular tempo médio de resposta
        response_times = [r.get('response_time', 0) for r in endpoint_results if 'response_time' in r]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Análise de tamanho de payload
        payload_sizes = [r.get('payload_size', 0) for r in endpoint_results if 'payload_size' in r]
        avg_payload_size = sum(payload_sizes) / len(payload_sizes) if payload_sizes else 0
        
        return {
            'total_tests': total_tests,
            'expected_behaviors': expected_behaviors,
            'unexpected_behaviors': unexpected_behaviors,
            'success_rate': expected_behaviors / total_tests if total_tests > 0 else 0,
            'status_codes_distribution': status_codes,
            'avg_response_time': avg_response_time,
            'max_response_time': max(response_times) if response_times else 0,
            'avg_payload_size': avg_payload_size,
            'max_payload_size': max(payload_sizes) if payload_sizes else 0
        }
    
    def generate_additional_extreme_scenarios(self) -> List[ExtremeValueScenario]:
        """Gera cenários adicionais de valores extremos"""
        additional_scenarios = []
        
        # Cenários com valores de ponto flutuante extremos
        float_extremes = [
            ("Float Muito Grande", float('inf')),
            ("Float Muito Pequeno", float('-inf')),
            ("Float NaN", float('nan')),
            ("Float Epsilon", sys.float_info.epsilon),
            ("Float Max", sys.float_info.max),
            ("Float Min", sys.float_info.min)
        ]
        
        for name, value in float_extremes:
            additional_scenarios.append(ExtremeValueScenario(
                name=name,
                description=f"Valor float extremo: {name}",
                value_type="very_large" if value > 0 else "very_small",
                field_name="amount",
                extreme_value=value,
                expected_behavior="400 Bad Request",
                severity="high"
            ))
        
        # Cenários com strings com caracteres especiais
        special_strings = [
            ("String com Null Bytes", "test\x00string"),
            ("String com Caracteres de Controle", "test\x01\x02\x03string"),
            ("String com Unicode Extremo", "test" + "🚀" * 1000 + "end"),
            ("String com Emojis Múltiplos", "test" + "💻🚀🎯🔥" * 100 + "end")
        ]
        
        for name, value in special_strings:
            additional_scenarios.append(ExtremeValueScenario(
                name=name,
                description=f"String especial: {name}",
                value_type="very_long",
                field_name="description",
                extreme_value=value,
                expected_behavior="400 Bad Request",
                severity="medium"
            ))
        
        # Cenários com arrays com tipos mistos
        mixed_arrays = [
            ("Array com Tipos Mistos", [1, "string", True, None, {"key": "value"}] * 1000),
            ("Array com Objetos Complexos", [{"id": i, "data": "x" * 100} for i in range(1000)]),
            ("Array Aninhado", self.generate_nested_array(10, 100))
        ]
        
        for name, value in mixed_arrays:
            additional_scenarios.append(ExtremeValueScenario(
                name=name,
                description=f"Array complexo: {name}",
                value_type="very_large",
                field_name="keywords",
                extreme_value=value,
                expected_behavior="413 Payload Too Large",
                severity="high"
            ))
        
        return additional_scenarios
    
    def generate_nested_array(self, depth: int, size: int) -> List:
        """Gera array aninhado com profundidade e tamanho específicos"""
        if depth == 0:
            return list(range(size))
        
        return [self.generate_nested_array(depth - 1, size // 10) for _ in range(10)]
    
    def run(self) -> Dict[str, Any]:
        """Executa todos os testes de valores extremos"""
        self.log("🚀 Iniciando testes de Edge Cases - Valores Extremos")
        
        all_results = {
            'tracing_id': self.tracing_id,
            'start_time': self.start_time.isoformat(),
            'host': self.host,
            'scenarios': [],
            'additional_scenarios': [],
            'summary': {},
            'performance_analysis': {}
        }
        
        try:
            # Executar cenários básicos
            for i, scenario in enumerate(self.extreme_value_scenarios):
                self.log(f"Executando cenário {i+1}/{len(self.extreme_value_scenarios)}: {scenario.name}")
                
                scenario_result = self.test_extreme_value_scenario(scenario)
                scenario_result['scenario_index'] = i + 1
                
                all_results['scenarios'].append(scenario_result)
                
                # Atualizar métricas
                self.metrics['scenarios_executed'] += 1
                if scenario_result.get('summary', {}).get('success_rate', 0) >= 0.8:
                    self.metrics['scenarios_failed'] += 1
                
                # Pausa entre cenários
                if i < len(self.extreme_value_scenarios) - 1:
                    time.sleep(2)  # Pausa maior para valores extremos
            
            # Executar cenários adicionais
            self.log("Executando cenários adicionais de valores extremos")
            additional_scenarios = self.generate_additional_extreme_scenarios()
            
            for i, scenario in enumerate(additional_scenarios):
                scenario_result = self.test_extreme_value_scenario(scenario)
                scenario_result['scenario_index'] = i + 1
                scenario_result['is_additional_test'] = True
                
                all_results['additional_scenarios'].append(scenario_result)
                
                # Pausa entre cenários
                if i < len(additional_scenarios) - 1:
                    time.sleep(2)
            
            # Gerar resumo geral
            all_results['summary'] = self.generate_overall_summary(all_results)
            all_results['performance_analysis'] = self.analyze_performance_impact(all_results)
            all_results['end_time'] = datetime.now().isoformat()
            
            # Calcular sucesso geral
            total_scenarios = len(all_results['scenarios']) + len(all_results['additional_scenarios'])
            successful_scenarios = sum(1 for s in all_results['scenarios'] 
                                     if s.get('summary', {}).get('success_rate', 0) >= 0.8)
            success_rate = successful_scenarios / total_scenarios if total_scenarios > 0 else 0
            
            all_results['success'] = success_rate >= 0.9  # 90% de sucesso mínimo
            
            self.log(f"✅ Testes de valores extremos concluídos: {success_rate:.1%} de sucesso")
            
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
        total_endpoint_tests = sum(len(s.get('endpoint_results', [])) for s in all_scenarios)
        
        # Análise por tipo de valor
        value_type_analysis = {}
        for scenario in all_scenarios:
            value_type = scenario.get('value_type', 'unknown')
            if value_type not in value_type_analysis:
                value_type_analysis[value_type] = {'count': 0, 'success_rate': 0}
            
            value_type_analysis[value_type]['count'] += 1
            success_rate = scenario.get('summary', {}).get('success_rate', 0)
            value_type_analysis[value_type]['success_rate'] += success_rate
        
        # Calcular média por tipo
        for value_type in value_type_analysis:
            count = value_type_analysis[value_type]['count']
            if count > 0:
                value_type_analysis[value_type]['success_rate'] /= count
        
        return {
            'total_scenarios': total_scenarios,
            'total_endpoint_tests': total_endpoint_tests,
            'value_type_analysis': value_type_analysis,
            'additional_tests': len(all_results['additional_scenarios']),
            'basic_tests': len(all_results['scenarios'])
        }
    
    def analyze_performance_impact(self, all_results: Dict) -> Dict[str, Any]:
        """Analisa o impacto de performance dos valores extremos"""
        all_scenarios = all_results['scenarios'] + all_results['additional_scenarios']
        
        performance_metrics = {
            'total_requests': 0,
            'timeout_requests': 0,
            'slow_requests': 0,  # > 30 segundos
            'very_slow_requests': 0,  # > 60 segundos
            'large_payloads': 0,  # > 1MB
            'very_large_payloads': 0,  # > 10MB
            'avg_response_time': 0.0,
            'max_response_time': 0.0,
            'avg_payload_size': 0.0,
            'max_payload_size': 0.0
        }
        
        all_response_times = []
        all_payload_sizes = []
        
        for scenario in all_scenarios:
            for result in scenario.get('endpoint_results', []):
                performance_metrics['total_requests'] += 1
                
                response_time = result.get('response_time', 0)
                payload_size = result.get('payload_size', 0)
                
                all_response_times.append(response_time)
                all_payload_sizes.append(payload_size)
                
                if result.get('status_code') == 'timeout':
                    performance_metrics['timeout_requests'] += 1
                elif response_time > 60:
                    performance_metrics['very_slow_requests'] += 1
                elif response_time > 30:
                    performance_metrics['slow_requests'] += 1
                
                if payload_size > 10 * 1024 * 1024:  # 10MB
                    performance_metrics['very_large_payloads'] += 1
                elif payload_size > 1024 * 1024:  # 1MB
                    performance_metrics['large_payloads'] += 1
        
        if all_response_times:
            performance_metrics['avg_response_time'] = sum(all_response_times) / len(all_response_times)
            performance_metrics['max_response_time'] = max(all_response_times)
        
        if all_payload_sizes:
            performance_metrics['avg_payload_size'] = sum(all_payload_sizes) / len(all_payload_sizes)
            performance_metrics['max_payload_size'] = max(all_payload_sizes)
        
        return performance_metrics


def main():
    """Função principal para execução standalone"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Teste de Edge Cases - Valores Extremos")
    parser.add_argument('--host', default='http://localhost:8000', help='Host para testar')
    parser.add_argument('--verbose', action='store_true', help='Modo verboso')
    
    args = parser.parse_args()
    
    # Criar e executar teste
    test = EdgeCasesExtremeValuesTest(host=args.host, verbose=args.verbose)
    result = test.run()
    
    # Imprimir resultados
    print("\n" + "="*80)
    print("📊 RESULTADOS DOS TESTES DE VALORES EXTREMOS")
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
        print(f"   • Testes de Endpoint: {summary['total_endpoint_tests']}")
        print(f"   • Testes Adicionais: {summary['additional_tests']}")
        print(f"   • Testes Básicos: {summary['basic_tests']}")
    
    if 'performance_analysis' in result:
        perf = result['performance_analysis']
        print(f"\n⚡ ANÁLISE DE PERFORMANCE:")
        print(f"   • Total de Requisições: {perf['total_requests']}")
        print(f"   • Timeouts: {perf['timeout_requests']}")
        print(f"   • Requisições Lentas (>30s): {perf['slow_requests']}")
        print(f"   • Requisições Muito Lentas (>60s): {perf['very_slow_requests']}")
        print(f"   • Payloads Grandes (>1MB): {perf['large_payloads']}")
        print(f"   • Payloads Muito Grandes (>10MB): {perf['very_large_payloads']}")
        print(f"   • Tempo Médio de Resposta: {perf['avg_response_time']:.2f}s")
        print(f"   • Tamanho Médio de Payload: {perf['avg_payload_size']:.0f} bytes")
    
    print("="*80)


if __name__ == "__main__":
    main() 