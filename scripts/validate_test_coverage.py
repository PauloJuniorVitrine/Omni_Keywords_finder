#!/usr/bin/env python3
"""
Script de Validação de Cobertura de Testes
Criado em: 2025-01-27
Tracing ID: COMPLETUDE_CHECKLIST_20250127_001
"""

import os
import sys
import json
import subprocess
import argparse
import tempfile
from typing import Dict, List, Any, Tuple
from pathlib import Path
import xml.etree.ElementTree as ET
import re
import statistics

class CoverageValidator:
    """Validador de cobertura de testes"""
    
    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.getcwd()
        self.coverage_threshold = 85.0  # 85% mínimo
        self.critical_modules = [
            'app/api',
            'app/services',
            'infrastructure',
            'shared'
        ]
        self.excluded_patterns = [
            '*/tests/*',
            '*/migrations/*',
            '*/__pycache__/*',
            '*.pyc',
            '*.pyo',
            '*.pyd',
            '*/venv/*',
            '*/env/*',
            '*/node_modules/*'
        ]
        self.coverage_data = {}
        self.validation_results = {}
    
    def run_coverage_analysis(self) -> Dict[str, Any]:
        """Executa análise de cobertura"""
        print("🔍 Executando análise de cobertura...")
        
        try:
            # Verifica se coverage está instalado
            subprocess.run([sys.executable, '-m', 'coverage', '--version'], 
                         check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Coverage não encontrado. Instalando...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'coverage'], 
                         check=True)
        
        # Limpa dados anteriores
        subprocess.run([sys.executable, '-m', 'coverage', 'erase'], 
                     cwd=self.project_root, check=True)
        
        # Executa testes com cobertura
        test_result = subprocess.run([
            sys.executable, '-m', 'coverage', 'run', '--source=.', 
            '-m', 'pytest', 'tests/', '--tb=short'
        ], cwd=self.project_root, capture_output=True, text=True)
        
        # Gera relatório XML
        xml_result = subprocess.run([
            sys.executable, '-m', 'coverage', 'xml', '-o', 'coverage.xml'
        ], cwd=self.project_root, capture_output=True, text=True)
        
        # Gera relatório HTML
        html_result = subprocess.run([
            sys.executable, '-m', 'coverage', 'html', '-d', 'htmlcov'
        ], cwd=self.project_root, capture_output=True, text=True)
        
        # Gera relatório JSON
        json_result = subprocess.run([
            sys.executable, '-m', 'coverage', 'json', '-o', 'coverage.json'
        ], cwd=self.project_root, capture_output=True, text=True)
        
        return {
            'test_exit_code': test_result.returncode,
            'xml_generated': xml_result.returncode == 0,
            'html_generated': html_result.returncode == 0,
            'json_generated': json_result.returncode == 0,
            'test_output': test_result.stdout,
            'test_errors': test_result.stderr
        }
    
    def parse_coverage_xml(self, xml_file: str = 'coverage.xml') -> Dict[str, Any]:
        """Parse arquivo XML de cobertura"""
        if not os.path.exists(xml_file):
            return {}
        
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            coverage_data = {
                'total_coverage': 0.0,
                'modules': {},
                'summary': {
                    'total_statements': 0,
                    'total_missing': 0,
                    'total_branches': 0,
                    'total_branch_missing': 0
                }
            }
            
            # Extrai cobertura total
            if root.get('line-rate'):
                coverage_data['total_coverage'] = float(root.get('line-rate')) * 100
            
            # Extrai dados por módulo
            for package in root.findall('.//package'):
                package_name = package.get('name', 'unknown')
                package_coverage = float(package.get('line-rate', 0)) * 100
                
                coverage_data['modules'][package_name] = {
                    'coverage': package_coverage,
                    'statements': int(package.get('statements', 0)),
                    'missing': int(package.get('missing', 0)),
                    'branches': int(package.get('branches', 0)),
                    'branch_missing': int(package.get('branch-missing', 0))
                }
                
                # Atualiza totais
                coverage_data['summary']['total_statements'] += int(package.get('statements', 0))
                coverage_data['summary']['total_missing'] += int(package.get('missing', 0))
                coverage_data['summary']['total_branches'] += int(package.get('branches', 0))
                coverage_data['summary']['total_branch_missing'] += int(package.get('branch-missing', 0))
            
            return coverage_data
            
        except Exception as e:
            print(f"❌ Erro ao parsear XML de cobertura: {e}")
            return {}
    
    def parse_coverage_json(self, json_file: str = 'coverage.json') -> Dict[str, Any]:
        """Parse arquivo JSON de cobertura"""
        if not os.path.exists(json_file):
            return {}
        
        try:
            with open(json_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Erro ao parsear JSON de cobertura: {e}")
            return {}
    
    def validate_coverage_thresholds(self, coverage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida thresholds de cobertura"""
        validation_results = {
            'overall_passed': False,
            'critical_modules_passed': False,
            'details': {},
            'recommendations': []
        }
        
        total_coverage = coverage_data.get('total_coverage', 0.0)
        
        # Valida cobertura total
        validation_results['overall_passed'] = total_coverage >= self.coverage_threshold
        validation_results['details']['total_coverage'] = {
            'value': total_coverage,
            'threshold': self.coverage_threshold,
            'passed': validation_results['overall_passed']
        }
        
        # Valida módulos críticos
        critical_modules_status = []
        for module in self.critical_modules:
            module_coverage = 0.0
            module_found = False
            
            for module_name, module_data in coverage_data.get('modules', {}).items():
                if module in module_name or module_name.startswith(module):
                    module_coverage = module_data.get('coverage', 0.0)
                    module_found = True
                    break
            
            module_passed = module_coverage >= self.coverage_threshold
            critical_modules_status.append(module_passed)
            
            validation_results['details'][module] = {
                'coverage': module_coverage,
                'threshold': self.coverage_threshold,
                'passed': module_passed,
                'found': module_found
            }
        
        validation_results['critical_modules_passed'] = all(critical_modules_status)
        
        # Gera recomendações
        if not validation_results['overall_passed']:
            validation_results['recommendations'].append(
                f"Cobertura total ({total_coverage:.1f}%) está abaixo do threshold ({self.coverage_threshold}%)"
            )
        
        for module, details in validation_results['details'].items():
            if module != 'total_coverage' and not details['passed']:
                validation_results['recommendations'].append(
                    f"Módulo '{module}' tem cobertura {details['coverage']:.1f}% (threshold: {self.coverage_threshold}%)"
                )
        
        return validation_results
    
    def analyze_uncovered_code(self, coverage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa código não coberto"""
        uncovered_analysis = {
            'uncovered_modules': [],
            'uncovered_functions': [],
            'risk_assessment': {},
            'priority_fixes': []
        }
        
        modules = coverage_data.get('modules', {})
        
        for module_name, module_data in modules.items():
            coverage = module_data.get('coverage', 0.0)
            missing = module_data.get('missing', 0)
            
            if coverage < self.coverage_threshold:
                uncovered_analysis['uncovered_modules'].append({
                    'module': module_name,
                    'coverage': coverage,
                    'missing_statements': missing,
                    'risk_level': 'high' if module_name in self.critical_modules else 'medium'
                })
        
        # Ordena por risco
        uncovered_analysis['uncovered_modules'].sort(
            key=lambda x: (x['risk_level'] == 'high', x['missing_statements']), 
            reverse=True
        )
        
        # Identifica prioridades
        for module in uncovered_analysis['uncovered_modules'][:5]:
            if module['risk_level'] == 'high':
                uncovered_analysis['priority_fixes'].append(
                    f"Adicionar testes para {module['module']} (cobertura: {module['coverage']:.1f}%)"
                )
        
        return uncovered_analysis
    
    def generate_coverage_report(self, coverage_data: Dict[str, Any], 
                               validation_results: Dict[str, Any],
                               uncovered_analysis: Dict[str, Any]) -> str:
        """Gera relatório de cobertura"""
        report = []
        report.append("# 📊 Relatório de Cobertura de Testes")
        report.append(f"**Data**: {self._get_timestamp()}")
        report.append(f"**Projeto**: {os.path.basename(self.project_root)}")
        report.append("")
        
        # Resumo executivo
        report.append("## 📋 Resumo Executivo")
        total_coverage = coverage_data.get('total_coverage', 0.0)
        overall_status = "✅ PASSOU" if validation_results['overall_passed'] else "❌ FALHOU"
        critical_status = "✅ PASSOU" if validation_results['critical_modules_passed'] else "❌ FALHOU"
        
        report.append(f"- **Cobertura Total**: {total_coverage:.1f}%")
        report.append(f"- **Status Geral**: {overall_status}")
        report.append(f"- **Módulos Críticos**: {critical_status}")
        report.append(f"- **Threshold**: {self.coverage_threshold}%")
        report.append("")
        
        # Detalhes por módulo
        report.append("## 📁 Cobertura por Módulo")
        report.append("| Módulo | Cobertura | Status |")
        report.append("|--------|-----------|--------|")
        
        for module, details in validation_results['details'].items():
            if module != 'total_coverage':
                status = "✅" if details['passed'] else "❌"
                report.append(f"| {module} | {details['coverage']:.1f}% | {status} |")
        
        report.append("")
        
        # Análise de código não coberto
        if uncovered_analysis['uncovered_modules']:
            report.append("## ⚠️ Módulos com Baixa Cobertura")
            report.append("| Módulo | Cobertura | Risco |")
            report.append("|--------|-----------|-------|")
            
            for module in uncovered_analysis['uncovered_modules'][:10]:
                risk_icon = "🔴" if module['risk_level'] == 'high' else "🟡"
                report.append(f"| {module['module']} | {module['coverage']:.1f}% | {risk_icon} |")
            
            report.append("")
        
        # Recomendações
        if validation_results['recommendations']:
            report.append("## 💡 Recomendações")
            for i, recommendation in enumerate(validation_results['recommendations'], 1):
                report.append(f"{i}. {recommendation}")
            report.append("")
        
        # Prioridades
        if uncovered_analysis['priority_fixes']:
            report.append("## 🎯 Prioridades de Correção")
            for i, priority in enumerate(uncovered_analysis['priority_fixes'], 1):
                report.append(f"{i}. {priority}")
            report.append("")
        
        # Estatísticas
        report.append("## 📈 Estatísticas")
        summary = coverage_data.get('summary', {})
        report.append(f"- **Total de Statements**: {summary.get('total_statements', 0)}")
        report.append(f"- **Statements Não Cobertos**: {summary.get('total_missing', 0)}")
        report.append(f"- **Total de Branches**: {summary.get('total_branches', 0)}")
        report.append(f"- **Branches Não Cobertos**: {summary.get('total_branch_missing', 0)}")
        report.append("")
        
        return "\n".join(report)
    
    def save_coverage_report(self, report: str, filename: str = None) -> str:
        """Salva relatório de cobertura"""
        if not filename:
            timestamp = self._get_timestamp().replace(':', '-').replace(' ', '_')
            filename = f"coverage_report_{timestamp}.md"
        
        filepath = os.path.join(self.project_root, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return filepath
    
    def _get_timestamp(self) -> str:
        """Obtém timestamp atual"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def run_full_validation(self) -> Dict[str, Any]:
        """Executa validação completa de cobertura"""
        print("🚀 Iniciando validação completa de cobertura...")
        
        # Executa análise de cobertura
        analysis_result = self.run_coverage_analysis()
        
        if analysis_result['test_exit_code'] != 0:
            print("⚠️ Testes falharam, mas continuando análise de cobertura...")
        
        # Parse dados de cobertura
        coverage_data = self.parse_coverage_xml()
        if not coverage_data:
            coverage_data = self.parse_coverage_json()
        
        if not coverage_data:
            print("❌ Não foi possível obter dados de cobertura")
            return {'error': 'Não foi possível obter dados de cobertura'}
        
        # Valida thresholds
        validation_results = self.validate_coverage_thresholds(coverage_data)
        
        # Analisa código não coberto
        uncovered_analysis = self.analyze_uncovered_code(coverage_data)
        
        # Gera relatório
        report = self.generate_coverage_report(coverage_data, validation_results, uncovered_analysis)
        
        # Salva relatório
        report_file = self.save_coverage_report(report)
        
        # Resultado final
        final_result = {
            'overall_passed': validation_results['overall_passed'],
            'critical_modules_passed': validation_results['critical_modules_passed'],
            'total_coverage': coverage_data.get('total_coverage', 0.0),
            'report_file': report_file,
            'validation_results': validation_results,
            'uncovered_analysis': uncovered_analysis,
            'analysis_result': analysis_result
        }
        
        # Exibe resultado
        print(f"\n📊 Resultado da Validação:")
        print(f"   Cobertura Total: {final_result['total_coverage']:.1f}%")
        print(f"   Status Geral: {'✅ PASSOU' if final_result['overall_passed'] else '❌ FALHOU'}")
        print(f"   Módulos Críticos: {'✅ PASSOU' if final_result['critical_modules_passed'] else '❌ FALHOU'}")
        print(f"   Relatório: {report_file}")
        
        return final_result

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Validador de Cobertura de Testes')
    parser.add_argument('--project-root', default=None, help='Diretório raiz do projeto')
    parser.add_argument('--threshold', type=float, default=85.0, help='Threshold de cobertura (default: 85%)')
    parser.add_argument('--output', default=None, help='Arquivo de saída do relatório')
    parser.add_argument('--json', action='store_true', help='Saída em formato JSON')
    
    args = parser.parse_args()
    
    # Configura validador
    validator = CoverageValidator(args.project_root)
    validator.coverage_threshold = args.threshold
    
    # Executa validação
    result = validator.run_full_validation()
    
    # Saída em JSON se solicitado
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        # Exibe recomendações se houver
        if 'validation_results' in result and result['validation_results']['recommendations']:
            print("\n💡 Recomendações:")
            for i, rec in enumerate(result['validation_results']['recommendations'], 1):
                print(f"   {i}. {rec}")
    
    # Retorna código de saída baseado no resultado
    sys.exit(0 if result.get('overall_passed', False) else 1)

if __name__ == "__main__":
    main() 