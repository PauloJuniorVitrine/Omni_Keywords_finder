from typing import Dict, List, Optional, Any
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 IMP012: Testes Unitários - Sistema de Penetration Testing
🎯 Objetivo: Validar funcionalidades do penetration tester
📅 Criado: 2025-01-27
🔄 Versão: 1.0
📋 Tracing ID: IMP012_TEST_001
"""

import unittest
import asyncio
import json
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from pathlib import Path

# Importar módulo a ser testado
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
from scripts.security.penetration_testing_imp012 import (
    PenetrationTester,
    Vulnerability,
    TestResult,
    VulnerabilitySeverity,
    TestCategory
)

class TestPenetrationTester(unittest.TestCase):
    """Testes para o sistema de penetration testing."""
    
    def setUp(self):
        """Configurar ambiente de teste."""
        self.target_url = "http://localhost:8000"
        self.config = {
            'timeout': 5,
            'max_retries': 1,
            'threads': 2,
            'delay_between_requests': 0.01,
            'follow_redirects': True,
            'verify_ssl': False
        }
        self.tester = PenetrationTester(self.target_url, self.config)
    
    def test_initialization(self):
        """Testar inicialização do penetration tester."""
        self.assertEqual(self.tester.target_url, self.target_url)
        self.assertEqual(self.tester.config['timeout'], 5)
        self.assertEqual(self.tester.config['threads'], 2)
        self.assertIsNotNone(self.tester.test_id)
        self.assertTrue(self.tester.test_id.startswith('PT_'))
    
    def test_default_config(self):
        """Testar configuração padrão."""
        tester = PenetrationTester("http://test.com")
        default_config = tester._default_config()
        
        self.assertIn('timeout', default_config)
        self.assertIn('threads', default_config)
        self.assertIn('delay_between_requests', default_config)
        self.assertIn('follow_redirects', default_config)
        self.assertIn('verify_ssl', default_config)
    
    def test_vulnerability_creation(self):
        """Testar criação de vulnerabilidade."""
        vuln = Vulnerability(
            id="TEST-001",
            title="Test Vulnerability",
            description="Test description",
            severity=VulnerabilitySeverity.HIGH,
            category=TestCategory.AUTHENTICATION,
            cvss_score=7.5,
            affected_endpoint="/api/test",
            payload="test_payload",
            remediation="Fix this"
        )
        
        self.assertEqual(vuln.id, "TEST-001")
        self.assertEqual(vuln.title, "Test Vulnerability")
        self.assertEqual(vuln.severity, VulnerabilitySeverity.HIGH)
        self.assertEqual(vuln.category, TestCategory.AUTHENTICATION)
        self.assertEqual(vuln.cvss_score, 7.5)
        self.assertIsNotNone(vuln.discovered_at)
        self.assertEqual(vuln.status, "open")
    
    def test_test_result_creation(self):
        """Testar criação de resultado de teste."""
        result = TestResult(
            test_name="Test Authentication",
            category=TestCategory.AUTHENTICATION,
            status="PASS",
            description="Test completed successfully",
            duration=1.5
        )
        
        self.assertEqual(result.test_name, "Test Authentication")
        self.assertEqual(result.category, TestCategory.AUTHENTICATION)
        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.duration, 1.5)
        self.assertIsNotNone(result.timestamp)
    
    @patch('scripts.security.penetration_testing_imp012.requests.Session')
    async def test_make_request(self, mock_session):
        """Testar método de requisição HTTP."""
        # Configurar mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_response.elapsed.total_seconds.return_value = 0.1
        mock_session.return_value.request.return_value = mock_response
        
        # Testar requisição
        response = await self.tester._make_request('GET', '/api/test')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "OK")
    
    def test_detect_sql_injection(self):
        """Testar detecção de SQL Injection."""
        # Mock de resposta com erro SQL
        mock_response = Mock()
        mock_response.text = "mysql_fetch_array() error"
        mock_response.elapsed.total_seconds.return_value = 0.1
        
        # Testar detecção
        result = self.tester._detect_sql_injection(mock_response, "test")
        self.assertTrue(result)
        
        # Testar resposta sem erro SQL
        mock_response.text = "OK"
        result = self.tester._detect_sql_injection(mock_response, "test")
        self.assertFalse(result)
        
        # Testar time-based injection
        mock_response.text = "OK"
        mock_response.elapsed.total_seconds.return_value = 6.0
        result = self.tester._detect_sql_injection(mock_response, "'; WAITFOR DELAY '00:00:05'--")
        self.assertTrue(result)
    
    def test_detect_xss(self):
        """Testar detecção de XSS."""
        # Mock de resposta com payload refletido
        mock_response = Mock()
        mock_response.text = "<script>alert('XSS')</script>"
        mock_response.headers = {}
        
        # Testar detecção
        result = self.tester._detect_xss(mock_response, "<script>alert('XSS')</script>")
        self.assertTrue(result)
        
        # Testar resposta sem payload
        mock_response.text = "OK"
        result = self.tester._detect_xss(mock_response, "<script>alert('XSS')</script>")
        self.assertFalse(result)
        
        # Testar header de proteção ausente
        mock_response.text = "OK"
        mock_response.headers = {}
        result = self.tester._detect_xss(mock_response, "test")
        self.assertTrue(result)  # Header X-XSS-Protection ausente
    
    def test_detect_authentication_vulnerability(self):
        """Testar detecção de vulnerabilidades de autenticação."""
        # Mock de resposta para weak password
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "token: abc123"
        
        # Testar weak password policy
        result = self.tester._detect_authentication_vulnerability(mock_response, "Weak Password Policy")
        self.assertTrue(result)
        
        # Testar account enumeration
        mock_response.text = "user exists"
        result = self.tester._detect_authentication_vulnerability(mock_response, "Account Enumeration")
        self.assertTrue(result)
        
        # Testar brute force protection
        mock_response.status_code = 200
        result = self.tester._detect_authentication_vulnerability(mock_response, "Brute Force Protection")
        self.assertTrue(result)  # Deveria ser bloqueado
    
    def test_calculate_security_score(self):
        """Testar cálculo de score de segurança."""
        # Score inicial deve ser 100
        score = self.tester._calculate_security_score()
        self.assertEqual(score, 100)
        
        # Adicionar vulnerabilidades e testar
        self.tester._add_vulnerability(
            title="Critical Test",
            description="Test",
            severity=VulnerabilitySeverity.CRITICAL,
            category=TestCategory.AUTHENTICATION,
            cvss_score=9.0
        )
        
        score = self.tester._calculate_security_score()
        self.assertEqual(score, 80)  # 100 - 20
        
        # Adicionar mais vulnerabilidades
        self.tester._add_vulnerability(
            title="High Test",
            description="Test",
            severity=VulnerabilitySeverity.HIGH,
            category=TestCategory.AUTHORIZATION,
            cvss_score=7.5
        )
        
        score = self.tester._calculate_security_score()
        self.assertEqual(score, 65)  # 80 - 15
    
    def test_generate_recommendations(self):
        """Testar geração de recomendações."""
        # Adicionar vulnerabilidade com remediação
        self.tester._add_vulnerability(
            title="Test Vulnerability",
            description="Test",
            severity=VulnerabilitySeverity.HIGH,
            category=TestCategory.AUTHENTICATION,
            cvss_score=7.5,
            remediation="Fix this issue"
        )
        
        recommendations = self.tester._generate_recommendations()
        
        self.assertIn("Test Vulnerability: Fix this issue", recommendations)
        self.assertIn("Implementar WAF (Web Application Firewall)", recommendations)
        self.assertIn("Configurar monitoramento de segurança em tempo real", recommendations)
    
    def test_add_vulnerability(self):
        """Testar adição de vulnerabilidade."""
        initial_count = len(self.tester.vulnerabilities)
        
        self.tester._add_vulnerability(
            title="Test Vulnerability",
            description="Test",
            severity=VulnerabilitySeverity.HIGH,
            category=TestCategory.AUTHENTICATION,
            cvss_score=7.5
        )
        
        self.assertEqual(len(self.tester.vulnerabilities), initial_count + 1)
        self.assertEqual(self.tester.vulnerabilities[-1].title, "Test Vulnerability")
    
    def test_add_result(self):
        """Testar adição de resultado de teste."""
        initial_count = len(self.tester.results)
        
        self.tester._add_result(
            test_name="Test",
            category=TestCategory.AUTHENTICATION,
            status="PASS",
            description="Test",
            duration=1.0
        )
        
        self.assertEqual(len(self.tester.results), initial_count + 1)
        self.assertEqual(self.tester.results[-1].test_name, "Test")
    
    def test_generate_report(self):
        """Testar geração de relatório."""
        # Adicionar alguns resultados e vulnerabilidades
        self.tester._add_result(
            test_name="Test 1",
            category=TestCategory.AUTHENTICATION,
            status="PASS",
            description="Test",
            duration=1.0
        )
        
        self.tester._add_result(
            test_name="Test 2",
            category=TestCategory.AUTHORIZATION,
            status="FAIL",
            description="Test",
            duration=2.0
        )
        
        self.tester._add_vulnerability(
            title="Test Vulnerability",
            description="Test",
            severity=VulnerabilitySeverity.HIGH,
            category=TestCategory.AUTHENTICATION,
            cvss_score=7.5
        )
        
        # Gerar relatório
        report = self.tester._generate_report(5.0)
        
        # Verificar estrutura do relatório
        self.assertIn('test_id', report)
        self.assertIn('target_url', report)
        self.assertIn('timestamp', report)
        self.assertIn('duration', report)
        self.assertIn('summary', report)
        self.assertIn('results', report)
        self.assertIn('vulnerabilities', report)
        self.assertIn('recommendations', report)
        
        # Verificar dados do resumo
        summary = report['summary']
        self.assertEqual(summary['total_tests'], 2)
        self.assertEqual(summary['passed_tests'], 1)
        self.assertEqual(summary['failed_tests'], 1)
        self.assertEqual(summary['total_vulnerabilities'], 1)
        self.assertEqual(summary['security_score'], 85)  # 100 - 15
    
    def test_save_report(self):
        """Testar salvamento de relatório."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Alterar diretório de trabalho
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Criar relatório de teste
                report = {
                    'test_id': 'TEST-001',
                    'target_url': 'http://test.com',
                    'timestamp': datetime.now().isoformat(),
                    'duration': 5.0,
                    'summary': {
                        'total_tests': 1,
                        'passed_tests': 1,
                        'failed_tests': 0,
                        'error_tests': 0,
                        'success_rate': 100.0,
                        'total_vulnerabilities': 0,
                        'vulnerabilities_by_severity': {},
                        'security_score': 100
                    },
                    'results': [],
                    'vulnerabilities': [],
                    'recommendations': [],
                    'metadata': {}
                }
                
                # Salvar relatório
                self.tester._save_report(report)
                
                # Verificar se arquivos foram criados
                self.assertTrue(os.path.exists('reports/security'))
                self.assertTrue(os.path.exists(f"reports/security/penetration_test_{report['test_id']}.json"))
                self.assertTrue(os.path.exists(f"reports/security/penetration_test_{report['test_id']}.html"))
                self.assertTrue(os.path.exists(f"reports/security/penetration_test_{report['test_id']}.md"))
                
            finally:
                os.chdir(original_cwd)
    
    def test_generate_html_report(self):
        """Testar geração de relatório HTML."""
        with tempfile.TemporaryDirectory() as temp_dir:
            report = {
                'test_id': 'TEST-001',
                'target_url': 'http://test.com',
                'timestamp': '2025-01-27T10:00:00',
                'duration': 5.0,
                'vulnerabilities': [
                    {
                        'title': 'Test Vulnerability',
                        'severity': 'high',
                        'cvss_score': 7.5,
                        'description': 'Test description',
                        'affected_endpoint': '/api/test',
                        'payload': 'test_payload',
                        'remediation': 'Fix this'
                    }
                ]
            }
            
            html_file = os.path.join(temp_dir, 'test_report.html')
            self.tester._generate_html_report(report, html_file)
            
            # Verificar se arquivo foi criado
            self.assertTrue(os.path.exists(html_file))
            
            # Verificar conteúdo
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('Test Vulnerability', content)
                self.assertIn('high', content)
                self.assertIn('7.5', content)
    
    def test_generate_markdown_report(self):
        """Testar geração de relatório Markdown."""
        with tempfile.TemporaryDirectory() as temp_dir:
            report = {
                'test_id': 'TEST-001',
                'target_url': 'http://test.com',
                'timestamp': '2025-01-27T10:00:00',
                'duration': 5.0,
                'summary': {
                    'security_score': 85
                },
                'vulnerabilities': [
                    {
                        'title': 'Test Vulnerability',
                        'severity': 'high',
                        'cvss_score': 7.5,
                        'description': 'Test description',
                        'affected_endpoint': '/api/test',
                        'payload': 'test_payload',
                        'remediation': 'Fix this'
                    }
                ],
                'recommendations': ['Fix this issue']
            }
            
            md_file = os.path.join(temp_dir, 'test_report.md')
            self.tester._generate_markdown_report(report, md_file)
            
            # Verificar se arquivo foi criado
            self.assertTrue(os.path.exists(md_file))
            
            # Verificar conteúdo
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('Test Vulnerability', content)
                self.assertIn('high', content)
                self.assertIn('7.5', content)
                self.assertIn('Fix this issue', content)

class TestVulnerabilitySeverity(unittest.TestCase):
    """Testes para enum de severidade de vulnerabilidades."""
    
    def test_severity_values(self):
        """Testar valores do enum de severidade."""
        self.assertEqual(VulnerabilitySeverity.CRITICAL.value, "critical")
        self.assertEqual(VulnerabilitySeverity.HIGH.value, "high")
        self.assertEqual(VulnerabilitySeverity.MEDIUM.value, "medium")
        self.assertEqual(VulnerabilitySeverity.LOW.value, "low")
        self.assertEqual(VulnerabilitySeverity.INFO.value, "info")

class TestTestCategory(unittest.TestCase):
    """Testes para enum de categorias de teste."""
    
    def test_category_values(self):
        """Testar valores do enum de categoria."""
        self.assertEqual(TestCategory.AUTHENTICATION.value, "authentication")
        self.assertEqual(TestCategory.AUTHORIZATION.value, "authorization")
        self.assertEqual(TestCategory.INPUT_VALIDATION.value, "input_validation")
        self.assertEqual(TestCategory.SESSION_MANAGEMENT.value, "session_management")
        self.assertEqual(TestCategory.CRYPTOGRAPHY.value, "cryptography")
        self.assertEqual(TestCategory.NETWORK_SECURITY.value, "network_security")
        self.assertEqual(TestCategory.API_SECURITY.value, "api_security")
        self.assertEqual(TestCategory.WEB_SECURITY.value, "web_security")
        self.assertEqual(TestCategory.INFRASTRUCTURE.value, "infrastructure")

def run_penetration_testing_tests():
    """Executar todos os testes de penetration testing."""
    print("🧪 IMP012: Executando Testes de Penetration Testing")
    print("="*60)
    
    # Criar suite de testes
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPenetrationTester)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestVulnerabilitySeverity))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTestCategory))
    
    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Gerar relatório
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    }
    
    # Salvar relatório
    with open('penetration_testing_test_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 Relatório de Testes de Penetration Testing:")
    print(f"   Total de testes: {report['total_tests']}")
    print(f"   Falhas: {report['failures']}")
    print(f"   Erros: {report['errors']}")
    print(f"   Taxa de sucesso: {report['success_rate']:.1f}%")
    
    if report['success_rate'] >= 95:
        print("\n🎉 Testes de penetration testing APROVADOS!")
        return True
    else:
        print("\n⚠️ Testes de penetration testing precisam de melhorias.")
        return False

if __name__ == "__main__":
    run_penetration_testing_tests() 