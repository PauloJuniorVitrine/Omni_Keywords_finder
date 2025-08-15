#!/usr/bin/env python3
"""
Script de Validação de Qualidade - CI/CD Pipeline
Tracing ID: CI_QUALITY_20241219_001

Este script valida a qualidade do código antes do deploy.
"""

import os
import sys
import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)string_data] [%(asctime)string_data] %(message)string_data'
)
logger = logging.getLogger(__name__)

class QualityValidator:
    """Validador de qualidade para CI/CD."""
    
    def __init__(self):
        self.project_root = Path(".")
        self.results = {
            'coverage': 0.0,
            'complexity': 'A',
            'maintainability': 'A',
            'security_score': 0,
            'test_count': 0,
            'errors': [],
            'warnings': []
        }
        
    def check_test_coverage(self) -> bool:
        """Verifica cobertura de testes."""
        try:
            logger.info("📊 Verificando cobertura de testes...")
            
            # Executar pytest com cobertura
            result = subprocess.run([
                'pytest', '--cov=./', '--cov-report=json', '--cov-report=term-missing'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode != 0:
                self.results['errors'].append("Testes falharam")
                return False
                
            # Parse coverage report
            coverage_file = self.project_root / "coverage.json"
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                    total_coverage = coverage_data.get('totals', {}).get('percent_covered', 0)
                    self.results['coverage'] = total_coverage
                    
                    if total_coverage < 85:
                        self.results['warnings'].append(f"Cobertura baixa: {total_coverage:.1f}%")
                        return False
                        
            logger.info(f"✅ Cobertura de testes: {self.results['coverage']:.1f}%")
            return True
            
        except Exception as e:
            self.results['errors'].append(f"Erro ao verificar cobertura: {e}")
            return False
            
    def check_code_complexity(self) -> bool:
        """Verifica complexidade ciclomática."""
        try:
            logger.info("🧠 Verificando complexidade ciclomática...")
            
            # Executar radon para análise de complexidade
            result = subprocess.run([
                'radon', 'cc', 'infrastructure/', 'backend/', 'shared/', '-a', '-counter'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                complexity_data = json.loads(result.stdout)
                
                # Analisar complexidade
                high_complexity = 0
                for file_path, functions in complexity_data.items():
                    for func_name, metrics in functions.items():
                        if metrics.get('complexity', 0) > 10:
                            high_complexity += 1
                            self.results['warnings'].append(
                                f"Função complexa: {file_path}:{func_name}"
                            )
                            
                if high_complexity > 5:
                    self.results['complexity'] = 'C'
                    self.results['warnings'].append("Muitas funções complexas")
                    return False
                    
            logger.info("✅ Complexidade ciclomática: OK")
            return True
            
        except Exception as e:
            self.results['errors'].append(f"Erro ao verificar complexidade: {e}")
            return False
            
    def check_maintainability(self) -> bool:
        """Verifica índice de manutenibilidade."""
        try:
            logger.info("🔧 Verificando índice de manutenibilidade...")
            
            # Executar radon para análise de manutenibilidade
            result = subprocess.run([
                'radon', 'mi', 'infrastructure/', 'backend/', 'shared/', '-counter'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                mi_data = json.loads(result.stdout)
                
                # Calcular média do índice de manutenibilidade
                total_mi = 0
                file_count = 0
                
                for file_path, mi_score in mi_data.items():
                    if isinstance(mi_score, (int, float)):
                        total_mi += mi_score
                        file_count += 1
                        
                if file_count > 0:
                    avg_mi = total_mi / file_count
                    if avg_mi < 65:
                        self.results['maintainability'] = 'C'
                        self.results['warnings'].append(f"Índice de manutenibilidade baixo: {avg_mi:.1f}")
                        return False
                        
            logger.info("✅ Índice de manutenibilidade: OK")
            return True
            
        except Exception as e:
            self.results['errors'].append(f"Erro ao verificar manutenibilidade: {e}")
            return False
            
    def check_security(self) -> bool:
        """Verifica segurança do código."""
        try:
            logger.info("🔒 Verificando segurança...")
            
            # Executar bandit para análise de segurança
            result = subprocess.run([
                'bandit', '-r', 'infrastructure/', 'backend/', 'shared/', '-f', 'json'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                security_data = json.loads(result.stdout)
                
                # Contar vulnerabilidades por severidade
                high_issues = len([index for index in security_data.get('results', []) 
                                 if index.get('issue_severity') == 'HIGH'])
                medium_issues = len([index for index in security_data.get('results', []) 
                                   if index.get('issue_severity') == 'MEDIUM'])
                                   
                if high_issues > 0:
                    self.results['errors'].append(f"Vulnerabilidades críticas encontradas: {high_issues}")
                    return False
                    
                if medium_issues > 10:
                    self.results['warnings'].append(f"Muitas vulnerabilidades médias: {medium_issues}")
                    
                self.results['security_score'] = 100 - (high_issues * 20) - (medium_issues * 5)
                
            logger.info(f"✅ Score de segurança: {self.results['security_score']}/100")
            return True
            
        except Exception as e:
            self.results['errors'].append(f"Erro ao verificar segurança: {e}")
            return False
            
    def check_dependencies(self) -> bool:
        """Verifica dependências vulneráveis."""
        try:
            logger.info("📦 Verificando dependências...")
            
            # Executar safety check
            result = subprocess.run([
                'safety', 'check', '--json'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                deps_data = json.loads(result.stdout)
                
                # Verificar vulnerabilidades críticas
                critical_vulns = [value for value in deps_data if value.get('severity') == 'CRITICAL']
                high_vulns = [value for value in deps_data if value.get('severity') == 'HIGH']
                
                if critical_vulns:
                    self.results['errors'].append(f"Dependências críticas vulneráveis: {len(critical_vulns)}")
                    return False
                    
                if high_vulns:
                    self.results['warnings'].append(f"Dependências altamente vulneráveis: {len(high_vulns)}")
                    
            logger.info("✅ Dependências: OK")
            return True
            
        except Exception as e:
            self.results['errors'].append(f"Erro ao verificar dependências: {e}")
            return False
            
    def check_documentation(self) -> bool:
        """Verifica documentação."""
        try:
            logger.info("📚 Verificando documentação...")
            
            # Verificar arquivos de documentação obrigatórios
            required_docs = [
                'README.md',
                'CHANGELOG.md',
                'docs/RELATORIO_QUALIDADE_FINAL.md',
                'docs/PLANO_EXECUCAO_TESTES.md'
            ]
            
            missing_docs = []
            for doc in required_docs:
                if not (self.project_root / doc).exists():
                    missing_docs.append(doc)
                    
            if missing_docs:
                self.results['warnings'].append(f"Documentação faltando: {', '.join(missing_docs)}")
                
            # Verificar docstrings em arquivos Python
            python_files = list(self.project_root.rglob("*.py"))
            files_without_docstrings = 0
            
            for py_file in python_files:
                if any(exclude in str(py_file) for exclude in ['.venv', '__pycache__', '.git']):
                    continue
                    
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if '"""' not in content and "'''" not in content:
                        files_without_docstrings += 1
                        
            if files_without_docstrings > 10:
                self.results['warnings'].append(f"Muitos arquivos sem docstrings: {files_without_docstrings}")
                
            logger.info("✅ Documentação: OK")
            return True
            
        except Exception as e:
            self.results['errors'].append(f"Erro ao verificar documentação: {e}")
            return False
            
    def generate_report(self) -> str:
        """Gera relatório de qualidade."""
        report = f"""
# 📊 RELATÓRIO DE QUALIDADE - CI/CD
Tracing ID: CI_QUALITY_20241219_001

## 📈 Métricas
- **Cobertura de Testes**: {self.results['coverage']:.1f}%
- **Complexidade**: {self.results['complexity']}
- **Manutenibilidade**: {self.results['maintainability']}
- **Score de Segurança**: {self.results['security_score']}/100

## ❌ Erros ({len(self.results['errors'])})
"""
        
        for error in self.results['errors']:
            report += f"- {error}\n"
            
        report += f"""
## ⚠️ Avisos ({len(self.results['warnings'])})
"""
        
        for warning in self.results['warnings']:
            report += f"- {warning}\n"
            
        return report
        
    def validate_all(self) -> bool:
        """Executa todas as validações."""
        logger.info("🚀 Iniciando validação de qualidade...")
        
        checks = [
            self.check_test_coverage,
            self.check_code_complexity,
            self.check_maintainability,
            self.check_security,
            self.check_dependencies,
            self.check_documentation
        ]
        
        all_passed = True
        for check in checks:
            if not check():
                all_passed = False
                
        # Gerar relatório
        report = self.generate_report()
        report_path = self.project_root / "logs" / "quality_report.md"
        report_path.parent.mkdir(exist_ok=True)
        report_path.write_text(report, encoding='utf-8')
        
        logger.info(f"📄 Relatório salvo em: {report_path}")
        
        if all_passed:
            logger.info("✅ Todas as validações passaram!")
        else:
            logger.error("❌ Algumas validações falharam!")
            
        return all_passed

def main():
    """Função principal."""
    validator = QualityValidator()
    success = validator.validate_all()
    
    if not success:
        sys.exit(1)
        
    return 0

if __name__ == "__main__":
    exit(main()) 