#!/usr/bin/env python3
"""
Teste de Edge Cases - Dados Inválidos
Omni Keywords Finder - Tracing ID: EDGE_INVALID_DATA_20250127_001

Este teste valida o comportamento do sistema com dados inválidos:
- Dados malformados
- Tipos de dados incorretos
- Valores nulos/vazios
- Dados muito grandes
- Caracteres especiais
- Validação de entrada

Baseado em:
- backend/app/api/validation.py
- backend/app/middleware/validation_middleware.py
- backend/app/models/validation.py

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
import string


@dataclass
class InvalidDataScenario:
    """Cenário de dados inválidos"""
    name: str
    description: str
    data_type: str  # 'malformed', 'wrong_type', 'null_empty', 'too_large', 'special_chars'
    payload: Dict[str, Any]
    expected_behavior: str
    severity: str  # 'low', 'medium', 'high', 'critical'


class EdgeCasesInvalidDataTest:
    """
    Teste de dados inválidos para Edge Cases
    """
    
    def __init__(self, host: str = "http://localhost:8000", verbose: bool = False):
        self.host = host
        self.verbose = verbose
        self.tracing_id = "EDGE_INVALID_DATA_20250127_001"
        self.start_time = datetime.now()
        
        # Configurar logging
        self.setup_logging()
        
        # Cenários de dados inválidos
        self.invalid_data_scenarios = [
            InvalidDataScenario(
                name="Email Inválido",
                description="Email com formato incorreto",
                data_type="malformed",
                payload={
                    "email": "invalid_email_format",
                    "password": "test_password_123"
                },
                expected_behavior="400 Bad Request",
                severity="medium"
            ),
            InvalidDataScenario(
                name="Senha Vazia",
                description="Senha com valor vazio",
                data_type="null_empty",
                payload={
                    "email": "test@example.com",
                    "password": ""
                },
                expected_behavior="400 Bad Request",
                severity="medium"
            ),
            InvalidDataScenario(
                name="Valor Numérico como String",
                description="Campo numérico recebendo string",
                data_type="wrong_type",
                payload={
                    "amount": "not_a_number",
                    "currency": "BRL",
                    "payment_method": "credit_card"
                },
                expected_behavior="400 Bad Request",
                severity="high"
            ),
            InvalidDataScenario(
                name="Data Muito Grande",
                description="Campo com valor extremamente grande",
                data_type="too_large",
                payload={
                    "description": "A" * 10000,  # 10KB de texto
                    "category": "test"
                },
                expected_behavior="400 Bad Request ou 413 Payload Too Large",
                severity="medium"
            ),
            InvalidDataScenario(
                name="Caracteres Especiais",
                description="Dados com caracteres especiais e Unicode",
                data_type="special_chars",
                payload={
                    "name": "Teste com ç, ã, é, ñ, 🚀, 💻, 测试, тест",
                    "description": "Dados com emojis e caracteres especiais: !@#$%^&*()_+-=[]{}|;':\",./<>?"
                },
                expected_behavior="200 OK ou 400 Bad Request",
                severity="low"
            ),
            InvalidDataScenario(
                name="Campo Nulo",
                description="Campo obrigatório com valor null",
                data_type="null_empty",
                payload={
                    "email": None,
                    "password": "test_password_123"
                },
                expected_behavior="400 Bad Request",
                severity="high"
            ),
            InvalidDataScenario(
                name="JSON Malformado",
                description="Payload JSON com sintaxe incorreta",
                data_type="malformed",
                payload={
                    "data": "invalid json: { missing quotes, unclosed brackets ["
                },
                expected_behavior="400 Bad Request",
                severity="critical"
            ),
            InvalidDataScenario(
                name="Array Vazio",
                description="Array obrigatório vazio",
                data_type="null_empty",
                payload={
                    "keywords": [],
                    "category": "test"
                },
                expected_behavior="400 Bad Request",
                severity="medium"
            ),
            InvalidDataScenario(
                name="Valor Negativo",
                description="Campo numérico com valor negativo",
                data_type="wrong_type",
                payload={
                    "amount": -100.00,
                    "currency": "BRL"
                },
                expected_behavior="400 Bad Request",
                severity="medium"
            ),
            InvalidDataScenario(
                name="Data Futura",
                description="Data com valor futuro inválido",
                data_type="wrong_type",
                payload={
                    "start_date": "2030-01-01",
                    "end_date": "2030-12-31"
                },
                expected_behavior="400 Bad Request",
                severity="low"
            )
        ]
        
        # Endpoints para testar com dados inválidos
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
            'validation_errors': 0,
            'unexpected_responses': 0,
            'avg_response_time': 0.0
        }
        
    def setup_logging(self):
        """Configura logging estruturado"""
        logging.basicConfig(
            level=logging.INFO if self.verbose else logging.WARNING,
            format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
            handlers=[
                logging.FileHandler(f'logs/edge_invalid_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(f"EdgeInvalidDataTest_{self.tracing_id}")
        
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
    
    def generate_invalid_payload(self, scenario: InvalidDataScenario, endpoint: str) -> Dict[str, Any]:
        """Gera payload inválido baseado no endpoint e cenário"""
        base_payload = scenario.payload.copy()
        
        # Adaptar payload para endpoint específico
        if endpoint == "/api/auth/login":
            return {
                "email": base_payload.get("email", "invalid@test"),
                "password": base_payload.get("password", "")
            }
        elif endpoint == "/api/auth/register":
            return {
                "email": base_payload.get("email", "invalid@test"),
                "password": base_payload.get("password", ""),
                "name": base_payload.get("name", ""),
                "confirm_password": base_payload.get("password", "")
            }
        elif endpoint == "/api/v1/payments/process":
            return {
                "amount": base_payload.get("amount", "invalid"),
                "currency": base_payload.get("currency", ""),
                "payment_method": base_payload.get("payment_method", None)
            }
        elif endpoint == "/api/v1/analytics/advanced":
            return {
                "start_date": base_payload.get("start_date", "invalid-date"),
                "end_date": base_payload.get("end_date", "invalid-date"),
                "metrics": base_payload.get("keywords", [])
            }
        elif endpoint == "/api/reports/generate":
            return {
                "report_type": base_payload.get("description", ""),
                "date_range": base_payload.get("category", None)
            }
        elif endpoint == "/api/users/profile":
            return {
                "user_id": base_payload.get("amount", "invalid"),
                "name": base_payload.get("name", "")
            }
        elif endpoint == "/api/categories/create":
            return {
                "name": base_payload.get("name", ""),
                "description": base_payload.get("description", "")
            }
        elif endpoint == "/api/executions/create":
            return {
                "keywords": base_payload.get("keywords", []),
                "category": base_payload.get("category", None)
            }
        
        return base_payload
    
    def test_invalid_data_scenario(self, scenario: InvalidDataScenario) -> Dict[str, Any]:
        """Testa um cenário específico de dados inválidos"""
        self.log(f"Iniciando teste: {scenario.name}")
        
        results = {
            'scenario_name': scenario.name,
            'data_type': scenario.data_type,
            'severity': scenario.severity,
            'start_time': datetime.now().isoformat(),
            'endpoint_results': [],
            'validation_errors': [],
            'unexpected_responses': [],
            'summary': {}
        }
        
        try:
            # Testar em múltiplos endpoints
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                
                for endpoint in self.test_endpoints:
                    future = executor.submit(
                        self.test_endpoint_with_invalid_data,
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
            results['summary'] = self.analyze_invalid_data_results(results['endpoint_results'])
            results['end_time'] = datetime.now().isoformat()
            
        except Exception as e:
            error_msg = f"Erro durante teste {scenario.name}: {str(e)}"
            self.log(error_msg, "ERROR")
            results['error'] = error_msg
            
        return results
    
    def test_endpoint_with_invalid_data(self, endpoint: str, scenario: InvalidDataScenario) -> Dict[str, Any]:
        """Testa um endpoint específico com dados inválidos"""
        start_time = time.time()
        
        try:
            # Gerar payload inválido para o endpoint
            invalid_payload = self.generate_invalid_payload(scenario, endpoint)
            
            # Fazer requisição
            response = requests.post(
                f"{self.host}{endpoint}",
                json=invalid_payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Analisar resposta
            is_expected = self.analyze_response_behavior(response, scenario)
            
            return {
                'endpoint': endpoint,
                'payload': invalid_payload,
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
                'payload': invalid_payload,
                'status_code': 'timeout',
                'response_time': end_time - start_time,
                'error': 'Request timeout',
                'is_expected_behavior': False,
                'timestamp': datetime.now().isoformat()
            }
        except requests.exceptions.ConnectionError:
            end_time = time.time()
            return {
                'endpoint': endpoint,
                'payload': invalid_payload,
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
                'payload': invalid_payload,
                'status_code': 'error',
                'response_time': end_time - start_time,
                'error': str(e),
                'is_expected_behavior': False,
                'timestamp': datetime.now().isoformat()
            }
    
    def analyze_response_behavior(self, response: requests.Response, scenario: InvalidDataScenario) -> bool:
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
        elif expected_status == "200" and "ou" in scenario.expected_behavior:
            # Caso onde aceita 200 ou 400
            return response.status_code in [200, 400]
        
        return False
    
    def analyze_invalid_data_results(self, endpoint_results: List[Dict]) -> Dict[str, Any]:
        """Analisa os resultados dos testes de dados inválidos"""
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
        
        return {
            'total_tests': total_tests,
            'expected_behaviors': expected_behaviors,
            'unexpected_behaviors': unexpected_behaviors,
            'success_rate': expected_behaviors / total_tests if total_tests > 0 else 0,
            'status_codes_distribution': status_codes,
            'avg_response_time': avg_response_time,
            'max_response_time': max(response_times) if response_times else 0
        }
    
    def generate_additional_invalid_scenarios(self) -> List[InvalidDataScenario]:
        """Gera cenários adicionais de dados inválidos dinamicamente"""
        additional_scenarios = []
        
        # Cenários com SQL Injection
        sql_injection_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --"
        ]
        
        for i, payload in enumerate(sql_injection_payloads):
            additional_scenarios.append(InvalidDataScenario(
                name=f"SQL Injection {i+1}",
                description=f"Tentativa de SQL injection: {payload[:20]}...",
                data_type="malformed",
                payload={"search_term": payload},
                expected_behavior="400 Bad Request",
                severity="critical"
            ))
        
        # Cenários com XSS
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>"
        ]
        
        for i, payload in enumerate(xss_payloads):
            additional_scenarios.append(InvalidDataScenario(
                name=f"XSS Attack {i+1}",
                description=f"Tentativa de XSS: {payload[:20]}...",
                data_type="malformed",
                payload={"comment": payload},
                expected_behavior="400 Bad Request",
                severity="critical"
            ))
        
        # Cenários com dados muito grandes
        large_data_scenarios = [
            ("String Gigante", "A" * 1000000),  # 1MB
            ("Array Gigante", list(range(100000))),  # 100k elementos
            ("Objeto Profundo", self.generate_deep_object(20))  # 20 níveis
        ]
        
        for name, data in large_data_scenarios:
            additional_scenarios.append(InvalidDataScenario(
                name=name,
                description=f"Dados extremamente grandes: {type(data).__name__}",
                data_type="too_large",
                payload={"data": data},
                expected_behavior="413 Payload Too Large",
                severity="high"
            ))
        
        return additional_scenarios
    
    def generate_deep_object(self, depth: int) -> Dict:
        """Gera um objeto aninhado com profundidade específica"""
        if depth == 0:
            return {"value": "leaf"}
        
        return {
            "level": depth,
            "nested": self.generate_deep_object(depth - 1)
        }
    
    def run(self) -> Dict[str, Any]:
        """Executa todos os testes de dados inválidos"""
        self.log("🚀 Iniciando testes de Edge Cases - Dados Inválidos")
        
        all_results = {
            'tracing_id': self.tracing_id,
            'start_time': self.start_time.isoformat(),
            'host': self.host,
            'scenarios': [],
            'additional_scenarios': [],
            'summary': {},
            'security_analysis': {}
        }
        
        try:
            # Executar cenários básicos
            for i, scenario in enumerate(self.invalid_data_scenarios):
                self.log(f"Executando cenário {i+1}/{len(self.invalid_data_scenarios)}: {scenario.name}")
                
                scenario_result = self.test_invalid_data_scenario(scenario)
                scenario_result['scenario_index'] = i + 1
                
                all_results['scenarios'].append(scenario_result)
                
                # Atualizar métricas
                self.metrics['scenarios_executed'] += 1
                if scenario_result.get('summary', {}).get('success_rate', 0) >= 0.8:
                    self.metrics['scenarios_failed'] += 1
                
                # Pausa entre cenários
                if i < len(self.invalid_data_scenarios) - 1:
                    time.sleep(1)
            
            # Executar cenários adicionais de segurança
            self.log("Executando cenários adicionais de segurança")
            additional_scenarios = self.generate_additional_invalid_scenarios()
            
            for i, scenario in enumerate(additional_scenarios):
                scenario_result = self.test_invalid_data_scenario(scenario)
                scenario_result['scenario_index'] = i + 1
                scenario_result['is_security_test'] = True
                
                all_results['additional_scenarios'].append(scenario_result)
                
                # Pausa entre cenários
                if i < len(additional_scenarios) - 1:
                    time.sleep(1)
            
            # Gerar resumo geral
            all_results['summary'] = self.generate_overall_summary(all_results)
            all_results['security_analysis'] = self.analyze_security_vulnerabilities(all_results)
            all_results['end_time'] = datetime.now().isoformat()
            
            # Calcular sucesso geral
            total_scenarios = len(all_results['scenarios']) + len(all_results['additional_scenarios'])
            successful_scenarios = sum(1 for s in all_results['scenarios'] 
                                     if s.get('summary', {}).get('success_rate', 0) >= 0.8)
            success_rate = successful_scenarios / total_scenarios if total_scenarios > 0 else 0
            
            all_results['success'] = success_rate >= 0.9  # 90% de sucesso mínimo
            
            self.log(f"✅ Testes de dados inválidos concluídos: {success_rate:.1%} de sucesso")
            
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
        
        # Análise por tipo de dados
        data_type_analysis = {}
        for scenario in all_scenarios:
            data_type = scenario.get('data_type', 'unknown')
            if data_type not in data_type_analysis:
                data_type_analysis[data_type] = {'count': 0, 'success_rate': 0}
            
            data_type_analysis[data_type]['count'] += 1
            success_rate = scenario.get('summary', {}).get('success_rate', 0)
            data_type_analysis[data_type]['success_rate'] += success_rate
        
        # Calcular média por tipo
        for data_type in data_type_analysis:
            count = data_type_analysis[data_type]['count']
            if count > 0:
                data_type_analysis[data_type]['success_rate'] /= count
        
        return {
            'total_scenarios': total_scenarios,
            'total_endpoint_tests': total_endpoint_tests,
            'data_type_analysis': data_type_analysis,
            'security_tests': len(all_results['additional_scenarios']),
            'basic_tests': len(all_results['scenarios'])
        }
    
    def analyze_security_vulnerabilities(self, all_results: Dict) -> Dict[str, Any]:
        """Analisa vulnerabilidades de segurança encontradas"""
        security_scenarios = all_results['additional_scenarios']
        
        vulnerabilities = {
            'sql_injection_attempts': 0,
            'xss_attempts': 0,
            'large_payload_attempts': 0,
            'successful_attacks': 0,
            'blocked_attacks': 0
        }
        
        for scenario in security_scenarios:
            scenario_name = scenario.get('scenario_name', '')
            
            if 'SQL Injection' in scenario_name:
                vulnerabilities['sql_injection_attempts'] += 1
            elif 'XSS' in scenario_name:
                vulnerabilities['xss_attempts'] += 1
            elif 'Gigante' in scenario_name:
                vulnerabilities['large_payload_attempts'] += 1
            
            # Verificar se o ataque foi bloqueado
            success_rate = scenario.get('summary', {}).get('success_rate', 0)
            if success_rate >= 0.8:  # 80% dos endpoints bloquearam
                vulnerabilities['blocked_attacks'] += 1
            else:
                vulnerabilities['successful_attacks'] += 1
        
        return vulnerabilities


def main():
    """Função principal para execução standalone"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Teste de Edge Cases - Dados Inválidos")
    parser.add_argument('--host', default='http://localhost:8000', help='Host para testar')
    parser.add_argument('--verbose', action='store_true', help='Modo verboso')
    
    args = parser.parse_args()
    
    # Criar e executar teste
    test = EdgeCasesInvalidDataTest(host=args.host, verbose=args.verbose)
    result = test.run()
    
    # Imprimir resultados
    print("\n" + "="*80)
    print("📊 RESULTADOS DOS TESTES DE DADOS INVÁLIDOS")
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
        print(f"   • Testes de Segurança: {summary['security_tests']}")
        print(f"   • Testes Básicos: {summary['basic_tests']}")
    
    if 'security_analysis' in result:
        security = result['security_analysis']
        print(f"\n🔒 ANÁLISE DE SEGURANÇA:")
        print(f"   • Tentativas SQL Injection: {security['sql_injection_attempts']}")
        print(f"   • Tentativas XSS: {security['xss_attempts']}")
        print(f"   • Payloads Grandes: {security['large_payload_attempts']}")
        print(f"   • Ataques Bloqueados: {security['blocked_attacks']}")
        print(f"   • Ataques Bem-sucedidos: {security['successful_attacks']}")
    
    print("="*80)


if __name__ == "__main__":
    main() 