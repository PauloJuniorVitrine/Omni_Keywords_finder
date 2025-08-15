#!/usr/bin/env python3
"""
Teste de Edge Cases - Requisições Malformadas
Omni Keywords Finder - Tracing ID: EDGE_MALFORMED_REQUESTS_20250127_001

Este teste valida o comportamento do sistema com requisições malformadas:
- Headers inválidos
- Content-Type incorreto
- Método HTTP incorreto
- URL malformada
- Parâmetros de query inválidos
- Payload JSON inválido

Baseado em:
- backend/app/middleware/request_middleware.py
- backend/app/api/error_handlers.py
- backend/app/utils/request_validator.py

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
import urllib.parse


@dataclass
class MalformedRequestScenario:
    """Cenário de requisição malformada"""
    name: str
    description: str
    request_type: str  # 'invalid_headers', 'wrong_content_type', 'wrong_method', 'malformed_url', 'invalid_query', 'invalid_json'
    method: str
    url: str
    headers: Dict[str, str]
    data: Any
    expected_behavior: str
    severity: str  # 'low', 'medium', 'high', 'critical'


class EdgeCasesMalformedRequestsTest:
    """
    Teste de requisições malformadas para Edge Cases
    """
    
    def __init__(self, host: str = "http://localhost:8000", verbose: bool = False):
        self.host = host
        self.verbose = verbose
        self.tracing_id = "EDGE_MALFORMED_REQUESTS_20250127_001"
        self.start_time = datetime.now()
        
        # Configurar logging
        self.setup_logging()
        
        # Cenários de requisições malformadas
        self.malformed_request_scenarios = [
            MalformedRequestScenario(
                name="Content-Type Inválido",
                description="Requisição com Content-Type incorreto",
                request_type="wrong_content_type",
                method="POST",
                url="/api/auth/login",
                headers={"Content-Type": "text/plain"},
                data="email=test@example.com&password=test123",
                expected_behavior="400 Bad Request",
                severity="medium"
            ),
            MalformedRequestScenario(
                name="Método HTTP Incorreto",
                description="Usar GET em endpoint que requer POST",
                request_type="wrong_method",
                method="GET",
                url="/api/auth/login",
                headers={"Content-Type": "application/json"},
                data={"email": "test@example.com", "password": "test123"},
                expected_behavior="405 Method Not Allowed",
                severity="medium"
            ),
            MalformedRequestScenario(
                name="Headers Ausentes",
                description="Requisição sem headers obrigatórios",
                request_type="invalid_headers",
                method="POST",
                url="/api/v1/payments/process",
                headers={},
                data={"amount": 100.00, "currency": "BRL"},
                expected_behavior="400 Bad Request",
                severity="high"
            ),
            MalformedRequestScenario(
                name="URL Malformada",
                description="URL com caracteres especiais não codificados",
                request_type="malformed_url",
                method="GET",
                url="/api/search?query=test data with spaces&category=test category",
                headers={"Content-Type": "application/json"},
                data=None,
                expected_behavior="400 Bad Request ou 404 Not Found",
                severity="low"
            ),
            MalformedRequestScenario(
                name="JSON Inválido",
                description="Payload JSON com sintaxe incorreta",
                request_type="invalid_json",
                method="POST",
                url="/api/auth/login",
                headers={"Content-Type": "application/json"},
                data='{"email": "test@example.com", "password": "test123",}',
                expected_behavior="400 Bad Request",
                severity="high"
            ),
            MalformedRequestScenario(
                name="Query Parameters Inválidos",
                description="Parâmetros de query com valores incorretos",
                request_type="invalid_query",
                method="GET",
                url="/api/analytics?start_date=invalid-date&end_date=2024-13-45",
                headers={"Content-Type": "application/json"},
                data=None,
                expected_behavior="400 Bad Request",
                severity="medium"
            ),
            MalformedRequestScenario(
                name="Headers Muito Grandes",
                description="Headers com valores extremamente grandes",
                request_type="invalid_headers",
                method="POST",
                url="/api/auth/login",
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "A" * 10000,
                    "X-Custom-Header": "B" * 5000
                },
                data={"email": "test@example.com", "password": "test123"},
                expected_behavior="400 Bad Request ou 431 Request Header Fields Too Large",
                severity="medium"
            ),
            MalformedRequestScenario(
                name="Método HTTP Desconhecido",
                description="Usar método HTTP não padrão",
                request_type="wrong_method",
                method="INVALID_METHOD",
                url="/api/auth/login",
                headers={"Content-Type": "application/json"},
                data={"email": "test@example.com", "password": "test123"},
                expected_behavior="405 Method Not Allowed",
                severity="low"
            ),
            MalformedRequestScenario(
                name="URL com Caracteres Especiais",
                description="URL com caracteres Unicode e especiais",
                request_type="malformed_url",
                method="GET",
                url="/api/search?query=测试&category=тест&special=!@#$%^&*()",
                headers={"Content-Type": "application/json"},
                data=None,
                expected_behavior="400 Bad Request ou 404 Not Found",
                severity="low"
            ),
            MalformedRequestScenario(
                name="Content-Type Múltiplo",
                description="Múltiplos Content-Type headers",
                request_type="invalid_headers",
                method="POST",
                url="/api/auth/login",
                headers={
                    "Content-Type": "application/json",
                    "Content-Type": "text/plain"
                },
                data={"email": "test@example.com", "password": "test123"},
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
            "/api/categories/list",
            "/api/executions/status"
        ]
        
        # Métricas coletadas
        self.metrics = {
            'scenarios_executed': 0,
            'scenarios_failed': 0,
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'malformed_requests_handled': 0,
            'unexpected_responses': 0,
            'avg_response_time': 0.0
        }
        
    def setup_logging(self):
        """Configura logging estruturado"""
        logging.basicConfig(
            level=logging.INFO if self.verbose else logging.WARNING,
            format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
            handlers=[
                logging.FileHandler(f'logs/edge_malformed_requests_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(f"EdgeMalformedRequestsTest_{self.tracing_id}")
        
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
    
    def test_malformed_request_scenario(self, scenario: MalformedRequestScenario) -> Dict[str, Any]:
        """Testa um cenário específico de requisição malformada"""
        self.log(f"Iniciando teste: {scenario.name}")
        
        results = {
            'scenario_name': scenario.name,
            'request_type': scenario.request_type,
            'severity': scenario.severity,
            'start_time': datetime.now().isoformat(),
            'endpoint_results': [],
            'malformed_requests_handled': 0,
            'unexpected_responses': 0,
            'summary': {}
        }
        
        try:
            # Testar em múltiplos endpoints
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                
                for endpoint in self.test_endpoints:
                    future = executor.submit(
                        self.test_endpoint_with_malformed_request,
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
            results['summary'] = self.analyze_malformed_request_results(results['endpoint_results'])
            results['end_time'] = datetime.now().isoformat()
            
        except Exception as e:
            error_msg = f"Erro durante teste {scenario.name}: {str(e)}"
            self.log(error_msg, "ERROR")
            results['error'] = error_msg
            
        return results
    
    def test_endpoint_with_malformed_request(self, endpoint: str, scenario: MalformedRequestScenario) -> Dict[str, Any]:
        """Testa um endpoint específico com requisição malformada"""
        start_time = time.time()
        
        try:
            # Adaptar URL do cenário para o endpoint
            test_url = f"{self.host}{endpoint}"
            if scenario.request_type == "malformed_url":
                test_url = f"{self.host}{scenario.url}"
            elif scenario.request_type == "invalid_query":
                test_url = f"{self.host}{endpoint}{scenario.url.split('?')[1]}"
            
            # Preparar dados
            if scenario.request_type == "invalid_json":
                data = scenario.data
            elif scenario.request_type == "wrong_content_type" and scenario.headers.get("Content-Type") == "text/plain":
                data = scenario.data
            else:
                data = json.dumps(scenario.data) if scenario.data else None
            
            # Fazer requisição
            response = requests.request(
                method=scenario.method,
                url=test_url,
                headers=scenario.headers,
                data=data,
                timeout=30
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Analisar resposta
            is_expected = self.analyze_malformed_response_behavior(response, scenario)
            
            return {
                'endpoint': endpoint,
                'method': scenario.method,
                'url': test_url,
                'headers': scenario.headers,
                'data': str(data)[:200] if data else None,  # Primeiros 200 caracteres
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
                'method': scenario.method,
                'url': test_url,
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
                'method': scenario.method,
                'url': test_url,
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
                'method': scenario.method,
                'url': test_url,
                'status_code': 'error',
                'response_time': end_time - start_time,
                'error': str(e),
                'is_expected_behavior': False,
                'timestamp': datetime.now().isoformat()
            }
    
    def analyze_malformed_response_behavior(self, response: requests.Response, scenario: MalformedRequestScenario) -> bool:
        """Analisa se a resposta está de acordo com o comportamento esperado"""
        expected_status = scenario.expected_behavior.split()[0]
        
        if expected_status == "400":
            return response.status_code == 400
        elif expected_status == "405":
            return response.status_code == 405
        elif expected_status == "404":
            return response.status_code == 404
        elif expected_status == "431":
            return response.status_code == 431
        elif expected_status == "400" and "ou" in scenario.expected_behavior:
            # Caso onde aceita 400 ou 404
            return response.status_code in [400, 404]
        elif expected_status == "400" and "ou" in scenario.expected_behavior and "431" in scenario.expected_behavior:
            # Caso onde aceita 400 ou 431
            return response.status_code in [400, 431]
        
        return False
    
    def analyze_malformed_request_results(self, endpoint_results: List[Dict]) -> Dict[str, Any]:
        """Analisa os resultados dos testes de requisições malformadas"""
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
    
    def generate_additional_malformed_scenarios(self) -> List[MalformedRequestScenario]:
        """Gera cenários adicionais de requisições malformadas"""
        additional_scenarios = []
        
        # Cenários com headers de segurança inválidos
        security_headers_scenarios = [
            ("Authorization Inválido", {"Authorization": "invalid_token"}),
            ("X-API-Key Inválido", {"X-API-Key": "invalid_key"}),
            ("User-Agent Malicioso", {"User-Agent": "malicious_bot/1.0"}),
            ("Referer Inválido", {"Referer": "http://malicious-site.com"}),
        ]
        
        for name, headers in security_headers_scenarios:
            additional_scenarios.append(MalformedRequestScenario(
                name=name,
                description=f"Headers de segurança inválidos: {name}",
                request_type="invalid_headers",
                method="POST",
                url="/api/auth/login",
                headers=headers,
                data={"email": "test@example.com", "password": "test123"},
                expected_behavior="401 Unauthorized ou 400 Bad Request",
                severity="high"
            ))
        
        # Cenários com métodos HTTP não padrão
        non_standard_methods = ["PATCH", "OPTIONS", "HEAD", "TRACE", "CONNECT"]
        
        for method in non_standard_methods:
            additional_scenarios.append(MalformedRequestScenario(
                name=f"Método {method}",
                description=f"Usar método HTTP {method}",
                request_type="wrong_method",
                method=method,
                url="/api/auth/login",
                headers={"Content-Type": "application/json"},
                data={"email": "test@example.com", "password": "test123"},
                expected_behavior="405 Method Not Allowed",
                severity="low"
            ))
        
        # Cenários com URLs malformadas
        malformed_urls = [
            ("URL com Espaços", "/api/search?query=test data"),
            ("URL com Caracteres Especiais", "/api/search?query=test&data=value"),
            ("URL Muito Longa", "/api/search?" + "&".join([f"param{i}=value{i}" for i in range(100)])),
            ("URL com Encoding Inválido", "/api/search?query=%invalid%encoding"),
        ]
        
        for name, url in malformed_urls:
            additional_scenarios.append(MalformedRequestScenario(
                name=name,
                description=f"URL malformada: {name}",
                request_type="malformed_url",
                method="GET",
                url=url,
                headers={"Content-Type": "application/json"},
                data=None,
                expected_behavior="400 Bad Request ou 404 Not Found",
                severity="medium"
            ))
        
        return additional_scenarios
    
    def run(self) -> Dict[str, Any]:
        """Executa todos os testes de requisições malformadas"""
        self.log("🚀 Iniciando testes de Edge Cases - Requisições Malformadas")
        
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
            for i, scenario in enumerate(self.malformed_request_scenarios):
                self.log(f"Executando cenário {i+1}/{len(self.malformed_request_scenarios)}: {scenario.name}")
                
                scenario_result = self.test_malformed_request_scenario(scenario)
                scenario_result['scenario_index'] = i + 1
                
                all_results['scenarios'].append(scenario_result)
                
                # Atualizar métricas
                self.metrics['scenarios_executed'] += 1
                if scenario_result.get('summary', {}).get('success_rate', 0) >= 0.8:
                    self.metrics['scenarios_failed'] += 1
                
                # Pausa entre cenários
                if i < len(self.malformed_request_scenarios) - 1:
                    time.sleep(1)
            
            # Executar cenários adicionais
            self.log("Executando cenários adicionais de requisições malformadas")
            additional_scenarios = self.generate_additional_malformed_scenarios()
            
            for i, scenario in enumerate(additional_scenarios):
                scenario_result = self.test_malformed_request_scenario(scenario)
                scenario_result['scenario_index'] = i + 1
                scenario_result['is_additional_test'] = True
                
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
            
            self.log(f"✅ Testes de requisições malformadas concluídos: {success_rate:.1%} de sucesso")
            
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
        
        # Análise por tipo de requisição
        request_type_analysis = {}
        for scenario in all_scenarios:
            request_type = scenario.get('request_type', 'unknown')
            if request_type not in request_type_analysis:
                request_type_analysis[request_type] = {'count': 0, 'success_rate': 0}
            
            request_type_analysis[request_type]['count'] += 1
            success_rate = scenario.get('summary', {}).get('success_rate', 0)
            request_type_analysis[request_type]['success_rate'] += success_rate
        
        # Calcular média por tipo
        for request_type in request_type_analysis:
            count = request_type_analysis[request_type]['count']
            if count > 0:
                request_type_analysis[request_type]['success_rate'] /= count
        
        return {
            'total_scenarios': total_scenarios,
            'total_endpoint_tests': total_endpoint_tests,
            'request_type_analysis': request_type_analysis,
            'additional_tests': len(all_results['additional_scenarios']),
            'basic_tests': len(all_results['scenarios'])
        }
    
    def analyze_security_vulnerabilities(self, all_results: Dict) -> Dict[str, Any]:
        """Analisa vulnerabilidades de segurança encontradas"""
        security_scenarios = [s for s in all_results['additional_scenarios'] 
                            if 'security' in s.get('scenario_name', '').lower()]
        
        vulnerabilities = {
            'security_header_attempts': 0,
            'non_standard_method_attempts': 0,
            'malformed_url_attempts': 0,
            'successful_attacks': 0,
            'blocked_attacks': 0
        }
        
        for scenario in security_scenarios:
            scenario_name = scenario.get('scenario_name', '')
            
            if 'Authorization' in scenario_name or 'API-Key' in scenario_name:
                vulnerabilities['security_header_attempts'] += 1
            elif 'Método' in scenario_name:
                vulnerabilities['non_standard_method_attempts'] += 1
            elif 'URL' in scenario_name:
                vulnerabilities['malformed_url_attempts'] += 1
            
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
    
    parser = argparse.ArgumentParser(description="Teste de Edge Cases - Requisições Malformadas")
    parser.add_argument('--host', default='http://localhost:8000', help='Host para testar')
    parser.add_argument('--verbose', action='store_true', help='Modo verboso')
    
    args = parser.parse_args()
    
    # Criar e executar teste
    test = EdgeCasesMalformedRequestsTest(host=args.host, verbose=args.verbose)
    result = test.run()
    
    # Imprimir resultados
    print("\n" + "="*80)
    print("📊 RESULTADOS DOS TESTES DE REQUISIÇÕES MALFORMADAS")
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
    
    if 'security_analysis' in result:
        security = result['security_analysis']
        print(f"\n🔒 ANÁLISE DE SEGURANÇA:")
        print(f"   • Tentativas de Headers de Segurança: {security['security_header_attempts']}")
        print(f"   • Métodos Não Padrão: {security['non_standard_method_attempts']}")
        print(f"   • URLs Malformadas: {security['malformed_url_attempts']}")
        print(f"   • Ataques Bloqueados: {security['blocked_attacks']}")
        print(f"   • Ataques Bem-sucedidos: {security['successful_attacks']}")
    
    print("="*80)


if __name__ == "__main__":
    main() 