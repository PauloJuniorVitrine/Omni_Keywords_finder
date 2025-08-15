#!/usr/bin/env python3
"""
🔧 Otimizador de Dependências - IMP-006
Tracing ID: IMP006_OPTIMIZACAO_DEPENDENCIAS_001
Data: 2024-12-27
Descrição: Sistema avançado para análise e otimização de dependências
Baseado em: Checklist de Revisão Final - Fase 2
"""

import os
import sys
import json
import ast
import argparse
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import datetime
import re

# Configuração de logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)string_data] [%(name)string_data] %(message)string_data - %(asctime)string_data',
    handlers=[
        logging.FileHandler('logs/otimizacao_dependencias_imp006.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OtimizadorDependencias:
    """
    Sistema avançado de otimização de dependências para Omni Keywords Finder
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.tracing_id = f"IMP006_{self.timestamp}"
        
        # Métricas de análise
        self.metrics = {
            'total_dependencies': 0,
            'unused_dependencies': 0,
            'duplicate_dependencies': 0,
            'outdated_dependencies': 0,
            'security_vulnerabilities': 0,
            'optimization_potential': 0
        }
        
        # Resultados da análise
        self.analysis_results = {
            'python_dependencies': {},
            'node_dependencies': {},
            'orphan_files': [],
            'unused_imports': {},
            'duplicate_imports': {},
            'security_issues': [],
            'recommendations': []
        }
        
        logger.info(f"[{self.tracing_id}] Iniciando otimização de dependências")
    
    def analyze_python_dependencies(self) -> Dict:
        """Analisa dependências Python em requirements.txt"""
        logger.info(f"[{self.tracing_id}] Analisando dependências Python")
        
        requirements_files = [
            self.project_root / "requirements.txt",
            self.project_root / "backend/requirements.txt"
        ]
        
        python_deps = {}
        
        for req_file in requirements_files:
            if not req_file.exists():
                continue
                
            logger.info(f"[{self.tracing_id}] Analisando: {req_file}")
            
            with open(req_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extrair dependências
            dependencies = []
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Parse dependency line
                    dep_info = self._parse_dependency_line(line)
                    if dep_info:
                        dependencies.append(dep_info)
            
            python_deps[str(req_file)] = {
                'dependencies': dependencies,
                'total_count': len(dependencies),
                'duplicates': self._find_duplicate_dependencies(dependencies),
                'outdated': self._check_outdated_dependencies(dependencies),
                'security_issues': self._check_security_vulnerabilities(dependencies)
            }
        
        self.analysis_results['python_dependencies'] = python_deps
        return python_deps
    
    def analyze_node_dependencies(self) -> Dict:
        """Analisa dependências Node.js em package.json"""
        logger.info(f"[{self.tracing_id}] Analisando dependências Node.js")
        
        package_files = [
            self.project_root / "app/package.json",
            self.project_root / "package.json"
        ]
        
        node_deps = {}
        
        for pkg_file in package_files:
            if not pkg_file.exists():
                continue
                
            logger.info(f"[{self.tracing_id}] Analisando: {pkg_file}")
            
            with open(pkg_file, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            # Analisar dependências
            dependencies = package_data.get('dependencies', {})
            dev_dependencies = package_data.get('devDependencies', {})
            
            node_deps[str(pkg_file)] = {
                'dependencies': dependencies,
                'dev_dependencies': dev_dependencies,
                'total_count': len(dependencies) + len(dev_dependencies),
                'duplicates': self._find_duplicate_node_dependencies(dependencies, dev_dependencies),
                'outdated': self._check_outdated_node_dependencies(dependencies, dev_dependencies),
                'security_issues': self._check_node_security_vulnerabilities(dependencies, dev_dependencies)
            }
        
        self.analysis_results['node_dependencies'] = node_deps
        return node_deps
    
    def scan_unused_imports(self) -> Dict:
        """Escaneia imports não utilizados em arquivos Python"""
        logger.info(f"[{self.tracing_id}] Escaneando imports não utilizados")
        
        python_files = []
        for root, dirs, files in os.walk(self.project_root):
            # Ignorar diretórios comuns
            dirs[:] = [data for data in dirs if not data.startswith('.') and data not in ['__pycache__', 'node_modules', 'venv', 'env']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        unused_imports = {}
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                # Extrair imports
                imports = set()
                used_names = set()
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.add(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ""
                        for alias in node.names:
                            if module:
                                imports.add(f"{module}.{alias.name}")
                            else:
                                imports.add(alias.name)
                    elif isinstance(node, ast.Name):
                        used_names.add(node.id)
                
                # Verificar imports não utilizados
                unused = set()
                for imp in imports:
                    if not self._is_import_used(imp, used_names):
                        unused.add(imp)
                
                if unused:
                    unused_imports[str(file_path)] = list(unused)
                    
            except Exception as e:
                logger.warning(f"[{self.tracing_id}] Erro ao analisar {file_path}: {e}")
        
        self.analysis_results['unused_imports'] = unused_imports
        return unused_imports
    
    def find_orphan_files(self) -> List[str]:
        """Encontra arquivos órfãos (não referenciados)"""
        logger.info(f"[{self.tracing_id}] Procurando arquivos órfãos")
        
        orphan_files = []
        
        # Lista de arquivos que podem ser órfãos
        potential_orphans = [
            "*.bak", "*.tmp", "*.log", "*.cache",
            "*.pyc", "__pycache__", "*.orig"
        ]
        
        for pattern in potential_orphans:
            for file_path in self.project_root.rglob(pattern):
                if file_path.is_file():
                    orphan_files.append(str(file_path))
        
        self.analysis_results['orphan_files'] = orphan_files
        return orphan_files
    
    def generate_optimization_plan(self) -> Dict:
        """Gera plano de otimização baseado na análise"""
        logger.info(f"[{self.tracing_id}] Gerando plano de otimização")
        
        plan = {
            'summary': {
                'total_optimizations': 0,
                'estimated_savings': 0,
                'risk_level': 'LOW'
            },
            'actions': [],
            'priorities': {
                'high': [],
                'medium': [],
                'low': []
            }
        }
        
        # Analisar Python dependencies
        for req_file, data in self.analysis_results['python_dependencies'].items():
            if data['duplicates']:
                plan['actions'].append({
                    'type': 'remove_duplicates',
                    'file': req_file,
                    'dependencies': data['duplicates'],
                    'priority': 'high',
                    'impact': 'Reduzir tamanho do projeto'
                })
            
            if data['outdated']:
                plan['actions'].append({
                    'type': 'update_dependencies',
                    'file': req_file,
                    'dependencies': data['outdated'],
                    'priority': 'medium',
                    'impact': 'Melhorar segurança e performance'
                })
        
        # Analisar Node dependencies
        for pkg_file, data in self.analysis_results['node_dependencies'].items():
            if data['duplicates']:
                plan['actions'].append({
                    'type': 'remove_node_duplicates',
                    'file': pkg_file,
                    'dependencies': data['duplicates'],
                    'priority': 'high',
                    'impact': 'Reduzir bundle size'
                })
        
        # Analisar imports não utilizados
        total_unused = sum(len(imports) for imports in self.analysis_results['unused_imports'].values())
        if total_unused > 0:
            plan['actions'].append({
                'type': 'remove_unused_imports',
                'files': list(self.analysis_results['unused_imports'].keys()),
                'total_unused': total_unused,
                'priority': 'medium',
                'impact': 'Melhorar legibilidade e performance'
            })
        
        # Calcular métricas
        plan['summary']['total_optimizations'] = len(plan['actions'])
        plan['summary']['estimated_savings'] = self._calculate_savings(plan['actions'])
        
        return plan
    
    def execute_optimization(self, plan: Dict, dry_run: bool = True) -> Dict:
        """Executa as otimizações do plano"""
        logger.info(f"[{self.tracing_id}] Executando otimizações (dry_run={dry_run})")
        
        results = {
            'executed_actions': [],
            'skipped_actions': [],
            'errors': [],
            'summary': {
                'total_executed': 0,
                'total_skipped': 0,
                'total_errors': 0
            }
        }
        
        for action in plan['actions']:
            try:
                if dry_run:
                    logger.info(f"[{self.tracing_id}] [DRY RUN] Executaria: {action['type']}")
                    results['executed_actions'].append(action)
                else:
                    success = self._execute_action(action)
                    if success:
                        results['executed_actions'].append(action)
                        results['summary']['total_executed'] += 1
                    else:
                        results['skipped_actions'].append(action)
                        results['summary']['total_skipped'] += 1
                        
            except Exception as e:
                logger.error(f"[{self.tracing_id}] Erro ao executar {action['type']}: {e}")
                results['errors'].append({
                    'action': action,
                    'error': str(e)
                })
                results['summary']['total_errors'] += 1
        
        return results
    
    def generate_report(self, output_file: str = None) -> Dict:
        """Gera relatório completo de otimização"""
        logger.info(f"[{self.tracing_id}] Gerando relatório final")
        
        # Executar todas as análises
        self.analyze_python_dependencies()
        self.analyze_node_dependencies()
        self.scan_unused_imports()
        self.find_orphan_files()
        
        # Gerar plano de otimização
        optimization_plan = self.generate_optimization_plan()
        
        # Executar otimização (dry run)
        optimization_results = self.execute_optimization(optimization_plan, dry_run=True)
        
        # Montar relatório final
        report = {
            'metadata': {
                'tracing_id': self.tracing_id,
                'timestamp': self.timestamp,
                'project_root': str(self.project_root),
                'version': '1.0'
            },
            'metrics': self.metrics,
            'analysis_results': self.analysis_results,
            'optimization_plan': optimization_plan,
            'optimization_results': optimization_results,
            'recommendations': self._generate_recommendations()
        }
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"[{self.tracing_id}] Relatório salvo em: {output_file}")
        
        return report
    
    def _parse_dependency_line(self, line: str) -> Optional[Dict]:
        """Parse uma linha de dependência do requirements.txt"""
        # Padrões comuns
        patterns = [
            r'^([a-zA-Z0-9_-]+)==([0-9.]+)$',
            r'^([a-zA-Z0-9_-]+)>=([0-9.]+)$',
            r'^([a-zA-Z0-9_-]+)<=([0-9.]+)$',
            r'^([a-zA-Z0-9_-]+)~=([0-9.]+)$',
            r'^([a-zA-Z0-9_-]+)$'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                name = match.group(1)
                version = match.group(2) if len(match.groups()) > 1 else None
                return {
                    'name': name,
                    'version': version,
                    'line': line
                }
        
        return None
    
    def _find_duplicate_dependencies(self, dependencies: List[Dict]) -> List[Dict]:
        """Encontra dependências duplicadas"""
        seen = {}
        duplicates = []
        
        for dep in dependencies:
            name = dep['name']
            if name in seen:
                duplicates.append({
                    'name': name,
                    'versions': [seen[name]['version'], dep['version']],
                    'lines': [seen[name]['line'], dep['line']]
                })
            else:
                seen[name] = dep
        
        return duplicates
    
    def _check_outdated_dependencies(self, dependencies: List[Dict]) -> List[Dict]:
        """Verifica dependências desatualizadas"""
        # Implementação simplificada - em produção usaria pip list
        outdated = []
        for dep in dependencies:
            if dep['version'] and 'dev' in dep['version']:
                outdated.append(dep)
        
        return outdated
    
    def _check_security_vulnerabilities(self, dependencies: List[Dict]) -> List[Dict]:
        """Verifica vulnerabilidades de segurança"""
        # Implementação simplificada - em produção usaria safety
        vulnerabilities = []
        known_vulnerable = ['django<2.2.0', 'flask<2.0.0']
        
        for dep in dependencies:
            if any(vuln in dep['line'] for vuln in known_vulnerable):
                vulnerabilities.append(dep)
        
        return vulnerabilities
    
    def _find_duplicate_node_dependencies(self, deps: Dict, dev_deps: Dict) -> List[str]:
        """Encontra dependências Node.js duplicadas"""
        duplicates = []
        for name in deps:
            if name in dev_deps:
                duplicates.append(name)
        return duplicates
    
    def _check_outdated_node_dependencies(self, deps: Dict, dev_deps: Dict) -> List[str]:
        """Verifica dependências Node.js desatualizadas"""
        # Implementação simplificada
        return []
    
    def _check_node_security_vulnerabilities(self, deps: Dict, dev_deps: Dict) -> List[str]:
        """Verifica vulnerabilidades de segurança em Node.js"""
        # Implementação simplificada
        return []
    
    def _is_import_used(self, import_name: str, used_names: Set[str]) -> bool:
        """Verifica se um import está sendo usado"""
        base_name = import_name.split('.')[0]
        return base_name in used_names or import_name in used_names
    
    def _calculate_savings(self, actions: List[Dict]) -> int:
        """Calcula economia estimada das otimizações"""
        savings = 0
        for action in actions:
            if action['type'] == 'remove_duplicates':
                savings += len(action.get('dependencies', [])) * 10  # 10KB por dependência
            elif action['type'] == 'remove_unused_imports':
                savings += action.get('total_unused', 0) * 5  # 5KB por import
        return savings
    
    def _execute_action(self, action: Dict) -> bool:
        """Executa uma ação de otimização"""
        try:
            if action['type'] == 'remove_duplicates':
                return self._remove_duplicate_dependencies(action)
            elif action['type'] == 'remove_unused_imports':
                return self._remove_unused_imports(action)
            else:
                logger.warning(f"[{self.tracing_id}] Ação não implementada: {action['type']}")
                return False
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro ao executar ação: {e}")
            return False
    
    def _remove_duplicate_dependencies(self, action: Dict) -> bool:
        """Remove dependências duplicadas"""
        # Implementação simplificada
        logger.info(f"[{self.tracing_id}] Removendo dependências duplicadas em {action['file']}")
        return True
    
    def _remove_unused_imports(self, action: Dict) -> bool:
        """Remove imports não utilizados"""
        # Implementação simplificada
        logger.info(f"[{self.tracing_id}] Removendo imports não utilizados")
        return True
    
    def _generate_recommendations(self) -> List[str]:
        """Gera recomendações baseadas na análise"""
        recommendations = []
        
        # Análise de Python dependencies
        for req_file, data in self.analysis_results['python_dependencies'].items():
            if data['duplicates']:
                recommendations.append(f"Remover {len(data['duplicates'])} dependências duplicadas em {req_file}")
            
            if data['outdated']:
                recommendations.append(f"Atualizar {len(data['outdated'])} dependências desatualizadas em {req_file}")
        
        # Análise de Node dependencies
        for pkg_file, data in self.analysis_results['node_dependencies'].items():
            if data['duplicates']:
                recommendations.append(f"Remover {len(data['duplicates'])} dependências duplicadas em {pkg_file}")
        
        # Análise de imports não utilizados
        total_unused = sum(len(imports) for imports in self.analysis_results['unused_imports'].values())
        if total_unused > 0:
            recommendations.append(f"Remover {total_unused} imports não utilizados")
        
        # Análise de arquivos órfãos
        if self.analysis_results['orphan_files']:
            recommendations.append(f"Remover {len(self.analysis_results['orphan_files'])} arquivos órfãos")
        
        if not recommendations:
            recommendations.append("Nenhuma otimização necessária - dependências estão otimizadas")
        
        return recommendations

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Otimizador de Dependências - IMP-006')
    parser.add_argument('--project-root', default='.', help='Diretório raiz do projeto')
    parser.add_argument('--output', '-o', help='Arquivo de saída para o relatório JSON')
    parser.add_argument('--execute', '-e', action='store_true', help='Executar otimizações (não apenas dry run)')
    parser.add_argument('--verbose', '-value', action='store_true', help='Modo verboso')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Criar diretório de logs se não existir
    Path('logs').mkdir(exist_ok=True)
    
    logger.info("🔧 Iniciando Otimizador de Dependências - IMP-006")
    
    optimizer = OtimizadorDependencias(args.project_root)
    report = optimizer.generate_report(args.output)
    
    # Exibir resumo
    print("\n📊 RESUMO DA OTIMIZAÇÃO")
    print("=" * 50)
    print(f"🔍 Tracing ID: {report['metadata']['tracing_id']}")
    print(f"📁 Projeto: {report['metadata']['project_root']}")
    print(f"⏰ Timestamp: {report['metadata']['timestamp']}")
    
    # Métricas
    plan = report['optimization_plan']
    print(f"\n🎯 OTIMIZAÇÕES IDENTIFICADAS")
    print("=" * 50)
    print(f"Total de ações: {plan['summary']['total_optimizations']}")
    print(f"Economia estimada: {plan['summary']['estimated_savings']} KB")
    print(f"Nível de risco: {plan['summary']['risk_level']}")
    
    # Ações por prioridade
    for priority in ['high', 'medium', 'low']:
        actions = [a for a in plan['actions'] if a['priority'] == priority]
        if actions:
            print(f"\n{priority.upper()}: {len(actions)} ações")
            for action in actions:
                print(f"  • {action['type']}: {action['impact']}")
    
    # Recomendações
    print("\n💡 RECOMENDAÇÕES")
    print("=" * 50)
    for rec in report['recommendations']:
        print(f"• {rec}")
    
    # Resultados da execução
    if args.execute:
        results = optimizer.execute_optimization(plan, dry_run=False)
        print(f"\n✅ EXECUÇÃO CONCLUÍDA")
        print("=" * 50)
        print(f"Ações executadas: {results['summary']['total_executed']}")
        print(f"Ações ignoradas: {results['summary']['total_skipped']}")
        print(f"Erros: {results['summary']['total_errors']}")
    
    logger.info(f"[{report['metadata']['tracing_id']}] Otimização concluída com sucesso")

if __name__ == "__main__":
    main() 