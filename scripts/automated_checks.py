#!/usr/bin/env python3
"""
Script de Automação de Verificações - Omni Keywords Finder
Tracing ID: AUTOMATED_CHECKS_20250127_001
Data: 2025-01-27
"""

import os
import sys
import json
import yaml
import subprocess
import logging
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automated_checks.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class CheckResult:
    """Resultado de uma verificação."""
    name: str
    status: str  # 'PASS', 'FAIL', 'WARNING', 'SKIP'
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    duration: float

class AutomatedChecks:
    """Sistema de verificações automatizadas."""
    
    def __init__(self, config_path: str = "config/automated_checks.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.results: List[CheckResult] = []
        self.start_time = datetime.now()
        
        # Criar diretório de logs se não existir
        Path("logs").mkdir(exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega configuração do arquivo YAML."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Arquivo de configuração não encontrado: {self.config_path}")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Retorna configuração padrão."""
        return {
            'checks': {
                'security': {
                    'enabled': True,
                    'vulnerability_scan': True,
                    'dependency_check': True,
                    'secret_scan': True
                },
                'quality': {
                    'enabled': True,
                    'linting': True,
                    'test_coverage': True,
                    'code_complexity': True
                },
                'compliance': {
                    'enabled': True,
                    'gdpr_check': True,
                    'lgpd_check': True,
                    'license_check': True
                },
                'performance': {
                    'enabled': True,
                    'load_test': False,
                    'memory_check': True,
                    'response_time': True
                }
            },
            'thresholds': {
                'test_coverage': 85,
                'code_complexity': 10,
                'security_score': 90,
                'performance_score': 80
            }
        }
    
    def run_all_checks(self) -> List[CheckResult]:
        """Executa todas as verificações configuradas."""
        logger.info("Iniciando verificações automatizadas...")
        
        checks_config = self.config.get('checks', {})
        
        # Verificações de Segurança
        if checks_config.get('security', {}).get('enabled', True):
            self._run_security_checks(checks_config['security'])
        
        # Verificações de Qualidade
        if checks_config.get('quality', {}).get('enabled', True):
            self._run_quality_checks(checks_config['quality'])
        
        # Verificações de Compliance
        if checks_config.get('compliance', {}).get('enabled', True):
            self._run_compliance_checks(checks_config['compliance'])
        
        # Verificações de Performance
        if checks_config.get('performance', {}).get('enabled', True):
            self._run_performance_checks(checks_config['performance'])
        
        self._generate_report()
        return self.results
    
    def _run_security_checks(self, config: Dict[str, Any]) -> None:
        """Executa verificações de segurança."""
        logger.info("Executando verificações de segurança...")
        
        if config.get('vulnerability_scan', True):
            self._check_vulnerabilities()
        
        if config.get('dependency_check', True):
            self._check_dependencies()
        
        if config.get('secret_scan', True):
            self._check_secrets()
    
    def _run_quality_checks(self, config: Dict[str, Any]) -> None:
        """Executa verificações de qualidade."""
        logger.info("Executando verificações de qualidade...")
        
        if config.get('linting', True):
            self._check_linting()
        
        if config.get('test_coverage', True):
            self._check_test_coverage()
        
        if config.get('code_complexity', True):
            self._check_code_complexity()
    
    def _run_compliance_checks(self, config: Dict[str, Any]) -> None:
        """Executa verificações de compliance."""
        logger.info("Executando verificações de compliance...")
        
        if config.get('gdpr_check', True):
            self._check_gdpr_compliance()
        
        if config.get('lgpd_check', True):
            self._check_lgpd_compliance()
        
        if config.get('license_check', True):
            self._check_licenses()
    
    def _run_performance_checks(self, config: Dict[str, Any]) -> None:
        """Executa verificações de performance."""
        logger.info("Executando verificações de performance...")
        
        if config.get('memory_check', True):
            self._check_memory_usage()
        
        if config.get('response_time', True):
            self._check_response_time()
        
        if config.get('load_test', False):
            self._run_load_test()
    
    def _check_vulnerabilities(self) -> None:
        """Verifica vulnerabilidades de segurança."""
        start_time = datetime.now()
        
        try:
            # Verificar vulnerabilidades com bandit
            result = subprocess.run(
                ['bandit', '-r', 'app/', '-f', 'json'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            if result.returncode == 0:
                self.results.append(CheckResult(
                    name="Vulnerability Scan",
                    status="PASS",
                    message="Nenhuma vulnerabilidade crítica encontrada",
                    details={'output': result.stdout},
                    timestamp=datetime.now(),
                    duration=duration
                ))
            else:
                # Analisar saída do bandit
                try:
                    output = json.loads(result.stdout)
                    issues = output.get('results', [])
                    critical_issues = [i for i in issues if i.get('issue_severity') == 'HIGH']
                    
                    if critical_issues:
                        self.results.append(CheckResult(
                            name="Vulnerability Scan",
                            status="FAIL",
                            message=f"Encontradas {len(critical_issues)} vulnerabilidades críticas",
                            details={'issues': critical_issues},
                            timestamp=datetime.now(),
                            duration=duration
                        ))
                    else:
                        self.results.append(CheckResult(
                            name="Vulnerability Scan",
                            status="WARNING",
                            message=f"Encontradas {len(issues)} vulnerabilidades de baixo/médio risco",
                            details={'issues': issues},
                            timestamp=datetime.now(),
                            duration=duration
                        ))
                except json.JSONDecodeError:
                    self.results.append(CheckResult(
                        name="Vulnerability Scan",
                        status="FAIL",
                        message="Erro ao analisar saída do bandit",
                        details={'error': result.stderr},
                        timestamp=datetime.now(),
                        duration=duration
                    ))
        
        except subprocess.TimeoutExpired:
            self.results.append(CheckResult(
                name="Vulnerability Scan",
                status="FAIL",
                message="Timeout na verificação de vulnerabilidades",
                details={'error': 'Timeout after 5 minutes'},
                timestamp=datetime.now(),
                duration=300
            ))
        except Exception as e:
            self.results.append(CheckResult(
                name="Vulnerability Scan",
                status="FAIL",
                message=f"Erro na verificação de vulnerabilidades: {e}",
                details={'error': str(e)},
                timestamp=datetime.now(),
                duration=(datetime.now() - start_time).total_seconds()
            ))
    
    def _check_dependencies(self) -> None:
        """Verifica dependências vulneráveis."""
        start_time = datetime.now()
        
        try:
            # Verificar dependências com safety
            result = subprocess.run(
                ['safety', 'check', '--json'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            if result.returncode == 0:
                self.results.append(CheckResult(
                    name="Dependency Check",
                    status="PASS",
                    message="Nenhuma dependência vulnerável encontrada",
                    details={'output': result.stdout},
                    timestamp=datetime.now(),
                    duration=duration
                ))
            else:
                try:
                    output = json.loads(result.stdout)
                    vulnerabilities = output.get('vulnerabilities', [])
                    
                    self.results.append(CheckResult(
                        name="Dependency Check",
                        status="FAIL",
                        message=f"Encontradas {len(vulnerabilities)} dependências vulneráveis",
                        details={'vulnerabilities': vulnerabilities},
                        timestamp=datetime.now(),
                        duration=duration
                    ))
                except json.JSONDecodeError:
                    self.results.append(CheckResult(
                        name="Dependency Check",
                        status="FAIL",
                        message="Erro ao analisar dependências",
                        details={'error': result.stderr},
                        timestamp=datetime.now(),
                        duration=duration
                    ))
        
        except Exception as e:
            self.results.append(CheckResult(
                name="Dependency Check",
                status="FAIL",
                message=f"Erro na verificação de dependências: {e}",
                details={'error': str(e)},
                timestamp=datetime.now(),
                duration=(datetime.now() - start_time).total_seconds()
            ))
    
    def _check_secrets(self) -> None:
        """Verifica vazamento de secrets no código."""
        start_time = datetime.now()
        
        try:
            # Padrões de secrets para verificar
            secret_patterns = [
                r'password["\s]*[:=]["\s]*["\']?[^"\'\s]+["\']?',
                r'api[_-]?key["\s]*[:=]["\s]*["\']?[a-zA-Z0-9]{20,}["\']?',
                r'token["\s]*[:=]["\s]*["\']?[a-zA-Z0-9]{20,}["\']?',
                r'secret["\s]*[:=]["\s]*["\']?[a-zA-Z0-9]{20,}["\']?',
                r'AKIA[0-9A-Z]{16}',
                r'AIza[0-9A-Za-z-_]{35}'
            ]
            
            found_secrets = []
            
            # Verificar arquivos Python
            for root, dirs, files in os.walk('app/'):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                for pattern in secret_patterns:
                                    import re
                                    matches = re.findall(pattern, content, re.IGNORECASE)
                                    if matches:
                                        found_secrets.append({
                                            'file': file_path,
                                            'pattern': pattern,
                                            'matches': matches
                                        })
                        except Exception as e:
                            logger.warning(f"Erro ao ler arquivo {file_path}: {e}")
            
            duration = (datetime.now() - start_time).total_seconds()
            
            if not found_secrets:
                self.results.append(CheckResult(
                    name="Secret Scan",
                    status="PASS",
                    message="Nenhum secret encontrado no código",
                    details={'files_scanned': len([f for f in Path('app/').rglob('*.py')])},
                    timestamp=datetime.now(),
                    duration=duration
                ))
            else:
                self.results.append(CheckResult(
                    name="Secret Scan",
                    status="FAIL",
                    message=f"Encontrados {len(found_secrets)} possíveis secrets no código",
                    details={'secrets': found_secrets},
                    timestamp=datetime.now(),
                    duration=duration
                ))
        
        except Exception as e:
            self.results.append(CheckResult(
                name="Secret Scan",
                status="FAIL",
                message=f"Erro na verificação de secrets: {e}",
                details={'error': str(e)},
                timestamp=datetime.now(),
                duration=(datetime.now() - start_time).total_seconds()
            ))
    
    def _check_linting(self) -> None:
        """Verifica qualidade do código com linters."""
        start_time = datetime.now()
        
        try:
            # Verificar com flake8
            result = subprocess.run(
                ['flake8', 'app/', '--max-line-length=88', '--count'],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            if result.returncode == 0:
                self.results.append(CheckResult(
                    name="Code Linting",
                    status="PASS",
                    message="Código passa na verificação de estilo",
                    details={'output': result.stdout},
                    timestamp=datetime.now(),
                    duration=duration
                ))
            else:
                issues = result.stdout.strip().split('\n')[-1] if result.stdout else 'Unknown'
                self.results.append(CheckResult(
                    name="Code Linting",
                    status="FAIL",
                    message=f"Encontrados {issues} problemas de estilo",
                    details={'output': result.stdout, 'errors': result.stderr},
                    timestamp=datetime.now(),
                    duration=duration
                ))
        
        except Exception as e:
            self.results.append(CheckResult(
                name="Code Linting",
                status="FAIL",
                message=f"Erro na verificação de estilo: {e}",
                details={'error': str(e)},
                timestamp=datetime.now(),
                duration=(datetime.now() - start_time).total_seconds()
            ))
    
    def _check_test_coverage(self) -> None:
        """Verifica cobertura de testes."""
        start_time = datetime.now()
        
        try:
            # Executar testes com cobertura
            result = subprocess.run(
                ['pytest', 'tests/', '--cov=app', '--cov-report=json'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            if result.returncode == 0:
                # Analisar relatório de cobertura
                try:
                    with open('.coverage', 'r') as f:
                        coverage_data = json.load(f)
                    
                    total_coverage = coverage_data.get('totals', {}).get('percent_covered', 0)
                    threshold = self.config.get('thresholds', {}).get('test_coverage', 85)
                    
                    if total_coverage >= threshold:
                        self.results.append(CheckResult(
                            name="Test Coverage",
                            status="PASS",
                            message=f"Cobertura de testes: {total_coverage:.1f}% (mínimo: {threshold}%)",
                            details={'coverage': total_coverage, 'threshold': threshold},
                            timestamp=datetime.now(),
                            duration=duration
                        ))
                    else:
                        self.results.append(CheckResult(
                            name="Test Coverage",
                            status="FAIL",
                            message=f"Cobertura de testes insuficiente: {total_coverage:.1f}% (mínimo: {threshold}%)",
                            details={'coverage': total_coverage, 'threshold': threshold},
                            timestamp=datetime.now(),
                            duration=duration
                        ))
                except Exception as e:
                    self.results.append(CheckResult(
                        name="Test Coverage",
                        status="WARNING",
                        message="Testes passaram mas não foi possível analisar cobertura",
                        details={'error': str(e)},
                        timestamp=datetime.now(),
                        duration=duration
                    ))
            else:
                self.results.append(CheckResult(
                    name="Test Coverage",
                    status="FAIL",
                    message="Testes falharam",
                    details={'output': result.stdout, 'errors': result.stderr},
                    timestamp=datetime.now(),
                    duration=duration
                ))
        
        except Exception as e:
            self.results.append(CheckResult(
                name="Test Coverage",
                status="FAIL",
                message=f"Erro na verificação de cobertura: {e}",
                details={'error': str(e)},
                timestamp=datetime.now(),
                duration=(datetime.now() - start_time).total_seconds()
            ))
    
    def _check_code_complexity(self) -> None:
        """Verifica complexidade do código."""
        start_time = datetime.now()
        
        try:
            # Verificar complexidade com radon
            result = subprocess.run(
                ['radon', 'cc', 'app/', '-a', '-j'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            if result.returncode == 0:
                try:
                    complexity_data = json.loads(result.stdout)
                    threshold = self.config.get('thresholds', {}).get('code_complexity', 10)
                    
                    high_complexity = []
                    for file_path, functions in complexity_data.items():
                        for func_name, complexity in functions.items():
                            if complexity > threshold:
                                high_complexity.append({
                                    'file': file_path,
                                    'function': func_name,
                                    'complexity': complexity
                                })
                    
                    if not high_complexity:
                        self.results.append(CheckResult(
                            name="Code Complexity",
                            status="PASS",
                            message=f"Complexidade do código está dentro do limite ({threshold})",
                            details={'max_complexity': threshold},
                            timestamp=datetime.now(),
                            duration=duration
                        ))
                    else:
                        self.results.append(CheckResult(
                            name="Code Complexity",
                            status="WARNING",
                            message=f"Encontradas {len(high_complexity)} funções com alta complexidade",
                            details={'high_complexity': high_complexity, 'threshold': threshold},
                            timestamp=datetime.now(),
                            duration=duration
                        ))
                except json.JSONDecodeError:
                    self.results.append(CheckResult(
                        name="Code Complexity",
                        status="WARNING",
                        message="Não foi possível analisar complexidade do código",
                        details={'error': 'JSON decode error'},
                        timestamp=datetime.now(),
                        duration=duration
                    ))
            else:
                self.results.append(CheckResult(
                    name="Code Complexity",
                    status="FAIL",
                    message="Erro na análise de complexidade",
                    details={'error': result.stderr},
                    timestamp=datetime.now(),
                    duration=duration
                ))
        
        except Exception as e:
            self.results.append(CheckResult(
                name="Code Complexity",
                status="FAIL",
                message=f"Erro na verificação de complexidade: {e}",
                details={'error': str(e)},
                timestamp=datetime.now(),
                duration=(datetime.now() - start_time).total_seconds()
            ))
    
    def _check_gdpr_compliance(self) -> None:
        """Verifica compliance com GDPR."""
        start_time = datetime.now()
        
        try:
            # Verificar se há políticas de privacidade
            privacy_files = [
                'docs/privacy_policy.md',
                'docs/gdpr_compliance.md',
                'app/templates/privacy_policy.html'
            ]
            
            missing_files = []
            for file_path in privacy_files:
                if not os.path.exists(file_path):
                    missing_files.append(file_path)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            if not missing_files:
                self.results.append(CheckResult(
                    name="GDPR Compliance",
                    status="PASS",
                    message="Documentação de privacidade encontrada",
                    details={'files_checked': privacy_files},
                    timestamp=datetime.now(),
                    duration=duration
                ))
            else:
                self.results.append(CheckResult(
                    name="GDPR Compliance",
                    status="WARNING",
                    message=f"Faltam {len(missing_files)} arquivos de documentação de privacidade",
                    details={'missing_files': missing_files},
                    timestamp=datetime.now(),
                    duration=duration
                ))
        
        except Exception as e:
            self.results.append(CheckResult(
                name="GDPR Compliance",
                status="FAIL",
                message=f"Erro na verificação GDPR: {e}",
                details={'error': str(e)},
                timestamp=datetime.now(),
                duration=(datetime.now() - start_time).total_seconds()
            ))
    
    def _check_lgpd_compliance(self) -> None:
        """Verifica compliance com LGPD."""
        start_time = datetime.now()
        
        try:
            # Verificar se há políticas de privacidade em português
            lgpd_files = [
                'docs/lgpd_compliance.md',
                'docs/politica_privacidade.md',
                'app/templates/politica_privacidade.html'
            ]
            
            missing_files = []
            for file_path in lgpd_files:
                if not os.path.exists(file_path):
                    missing_files.append(file_path)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            if not missing_files:
                self.results.append(CheckResult(
                    name="LGPD Compliance",
                    status="PASS",
                    message="Documentação LGPD encontrada",
                    details={'files_checked': lgpd_files},
                    timestamp=datetime.now(),
                    duration=duration
                ))
            else:
                self.results.append(CheckResult(
                    name="LGPD Compliance",
                    status="WARNING",
                    message=f"Faltam {len(missing_files)} arquivos de documentação LGPD",
                    details={'missing_files': missing_files},
                    timestamp=datetime.now(),
                    duration=duration
                ))
        
        except Exception as e:
            self.results.append(CheckResult(
                name="LGPD Compliance",
                status="FAIL",
                message=f"Erro na verificação LGPD: {e}",
                details={'error': str(e)},
                timestamp=datetime.now(),
                duration=(datetime.now() - start_time).total_seconds()
            ))
    
    def _check_licenses(self) -> None:
        """Verifica licenças de dependências."""
        start_time = datetime.now()
        
        try:
            # Verificar se há arquivo de licenças
            license_files = [
                'LICENSE',
                'LICENSE.txt',
                'license.txt',
                'docs/licenses.md'
            ]
            
            found_license = None
            for file_path in license_files:
                if os.path.exists(file_path):
                    found_license = file_path
                    break
            
            duration = (datetime.now() - start_time).total_seconds()
            
            if found_license:
                self.results.append(CheckResult(
                    name="License Check",
                    status="PASS",
                    message=f"Arquivo de licença encontrado: {found_license}",
                    details={'license_file': found_license},
                    timestamp=datetime.now(),
                    duration=duration
                ))
            else:
                self.results.append(CheckResult(
                    name="License Check",
                    status="WARNING",
                    message="Nenhum arquivo de licença encontrado",
                    details={'checked_files': license_files},
                    timestamp=datetime.now(),
                    duration=duration
                ))
        
        except Exception as e:
            self.results.append(CheckResult(
                name="License Check",
                status="FAIL",
                message=f"Erro na verificação de licenças: {e}",
                details={'error': str(e)},
                timestamp=datetime.now(),
                duration=(datetime.now() - start_time).total_seconds()
            ))
    
    def _check_memory_usage(self) -> None:
        """Verifica uso de memória."""
        start_time = datetime.now()
        
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            duration = (datetime.now() - start_time).total_seconds()
            
            if memory_percent < 80:
                self.results.append(CheckResult(
                    name="Memory Usage",
                    status="PASS",
                    message=f"Uso de memória: {memory_percent:.1f}%",
                    details={'memory_percent': memory_percent, 'available_gb': memory.available / (1024**3)},
                    timestamp=datetime.now(),
                    duration=duration
                ))
            else:
                self.results.append(CheckResult(
                    name="Memory Usage",
                    status="WARNING",
                    message=f"Uso de memória alto: {memory_percent:.1f}%",
                    details={'memory_percent': memory_percent, 'available_gb': memory.available / (1024**3)},
                    timestamp=datetime.now(),
                    duration=duration
                ))
        
        except Exception as e:
            self.results.append(CheckResult(
                name="Memory Usage",
                status="SKIP",
                message=f"Não foi possível verificar uso de memória: {e}",
                details={'error': str(e)},
                timestamp=datetime.now(),
                duration=(datetime.now() - start_time).total_seconds()
            ))
    
    def _check_response_time(self) -> None:
        """Verifica tempo de resposta da aplicação."""
        start_time = datetime.now()
        
        try:
            import requests
            
            # Tentar fazer uma requisição para a aplicação
            response = requests.get('http://localhost:8000/health', timeout=10)
            response_time = response.elapsed.total_seconds()
            
            duration = (datetime.now() - start_time).total_seconds()
            
            if response_time < 2.0:
                self.results.append(CheckResult(
                    name="Response Time",
                    status="PASS",
                    message=f"Tempo de resposta: {response_time:.3f}s",
                    details={'response_time': response_time, 'status_code': response.status_code},
                    timestamp=datetime.now(),
                    duration=duration
                ))
            else:
                self.results.append(CheckResult(
                    name="Response Time",
                    status="WARNING",
                    message=f"Tempo de resposta lento: {response_time:.3f}s",
                    details={'response_time': response_time, 'status_code': response.status_code},
                    timestamp=datetime.now(),
                    duration=duration
                ))
        
        except Exception as e:
            self.results.append(CheckResult(
                name="Response Time",
                status="SKIP",
                message=f"Não foi possível verificar tempo de resposta: {e}",
                details={'error': str(e)},
                timestamp=datetime.now(),
                duration=(datetime.now() - start_time).total_seconds()
            ))
    
    def _run_load_test(self) -> None:
        """Executa teste de carga."""
        start_time = datetime.now()
        
        try:
            # Implementar teste de carga básico
            import requests
            import threading
            import time
            
            def make_request():
                try:
                    response = requests.get('http://localhost:8000/health', timeout=5)
                    return response.status_code == 200
                except:
                    return False
            
            # Simular 10 requisições simultâneas
            threads = []
            results = []
            
            for i in range(10):
                thread = threading.Thread(target=lambda: results.append(make_request()))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            success_rate = sum(results) / len(results) * 100
            
            duration = (datetime.now() - start_time).total_seconds()
            
            if success_rate >= 90:
                self.results.append(CheckResult(
                    name="Load Test",
                    status="PASS",
                    message=f"Taxa de sucesso: {success_rate:.1f}%",
                    details={'success_rate': success_rate, 'total_requests': len(results)},
                    timestamp=datetime.now(),
                    duration=duration
                ))
            else:
                self.results.append(CheckResult(
                    name="Load Test",
                    status="FAIL",
                    message=f"Taxa de sucesso baixa: {success_rate:.1f}%",
                    details={'success_rate': success_rate, 'total_requests': len(results)},
                    timestamp=datetime.now(),
                    duration=duration
                ))
        
        except Exception as e:
            self.results.append(CheckResult(
                name="Load Test",
                status="SKIP",
                message=f"Não foi possível executar teste de carga: {e}",
                details={'error': str(e)},
                timestamp=datetime.now(),
                duration=(datetime.now() - start_time).total_seconds()
            ))
    
    def _generate_report(self) -> None:
        """Gera relatório das verificações."""
        total_checks = len(self.results)
        passed_checks = len([r for r in self.results if r.status == 'PASS'])
        failed_checks = len([r for r in self.results if r.status == 'FAIL'])
        warning_checks = len([r for r in self.results if r.status == 'WARNING'])
        skipped_checks = len([r for r in self.results if r.status == 'SKIP'])
        
        total_duration = (datetime.now() - self.start_time).total_seconds()
        
        report = {
            'summary': {
                'total_checks': total_checks,
                'passed': passed_checks,
                'failed': failed_checks,
                'warnings': warning_checks,
                'skipped': skipped_checks,
                'success_rate': (passed_checks / total_checks * 100) if total_checks > 0 else 0,
                'total_duration': total_duration,
                'timestamp': datetime.now().isoformat()
            },
            'results': [
                {
                    'name': r.name,
                    'status': r.status,
                    'message': r.message,
                    'details': r.details,
                    'timestamp': r.timestamp.isoformat(),
                    'duration': r.duration
                }
                for r in self.results
            ]
        }
        
        # Salvar relatório
        report_path = f"logs/automated_checks_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Log do resumo
        logger.info(f"Verificações concluídas: {passed_checks}/{total_checks} passaram")
        logger.info(f"Relatório salvo em: {report_path}")
        
        if failed_checks > 0:
            logger.error(f"{failed_checks} verificações falharam")
            sys.exit(1)

def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description='Executa verificações automatizadas')
    parser.add_argument('--config', '-c', default='config/automated_checks.yaml',
                       help='Caminho para arquivo de configuração')
    parser.add_argument('--output', '-o', default='logs/',
                       help='Diretório para salvar relatórios')
    
    args = parser.parse_args()
    
    # Criar diretório de saída se não existir
    Path(args.output).mkdir(parents=True, exist_ok=True)
    
    # Executar verificações
    checker = AutomatedChecks(args.config)
    results = checker.run_all_checks()
    
    # Exibir resumo
    print("\n" + "="*60)
    print("RELATÓRIO DE VERIFICAÇÕES AUTOMATIZADAS")
    print("="*60)
    
    for result in results:
        status_icon = {
            'PASS': '✅',
            'FAIL': '❌',
            'WARNING': '⚠️',
            'SKIP': '⏭️'
        }.get(result.status, '❓')
        
        print(f"{status_icon} {result.name}: {result.message}")
    
    print("\n" + "="*60)
    print("Verificações concluídas!")

if __name__ == "__main__":
    main() 