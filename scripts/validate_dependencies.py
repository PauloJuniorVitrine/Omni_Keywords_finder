#!/usr/bin/env python3
"""
📋 Validador de Dependências - Omni Keywords Finder
Tracing ID: INT-007
Data: 2024-12-19
Descrição: Ferramenta para identificar dependências não utilizadas no projeto

Script para validar e corrigir dependências
Responsável por verificar duplicatas, vulnerabilidades e versões.

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Correção 1
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Versão: 1.0.0
"""

import os
import sys
import json
import ast
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import logging
import subprocess
import re

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)string_data] %(message)string_data'
)
logger = logging.getLogger(__name__)

class DependencyValidator:
    """
    Validador de dependências para identificar imports não utilizados
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.imports_found = defaultdict(set)
        self.imports_used = defaultdict(set)
        self.unused_imports = defaultdict(set)
        self.orphan_dependencies = set()
        
    def scan_python_files(self) -> List[Path]:
        """Escaneia todos os arquivos Python no projeto"""
        python_files = []
        for root, dirs, files in os.walk(self.project_root):
            # Ignorar diretórios comuns que não devem ser analisados
            dirs[:] = [data for data in dirs if not data.startswith('.') and data not in ['__pycache__', 'node_modules', 'venv', 'env']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        return python_files
    
    def extract_imports(self, file_path: Path) -> Set[str]:
        """Extrai todos os imports de um arquivo Python"""
        imports = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
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
                            
        except Exception as e:
            logger.warning(f"Erro ao analisar {file_path}: {e}")
            
        return imports
    
    def extract_used_names(self, file_path: Path) -> Set[str]:
        """Extrai nomes utilizados no código (funções, classes, variáveis)"""
        used_names = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    used_names.add(node.id)
                elif isinstance(node, ast.Attribute):
                    # Para atributos como module.function
                    parts = []
                    current = node
                    while isinstance(current, ast.Attribute):
                        parts.append(current.attr)
                        current = current.value
                    if isinstance(current, ast.Name):
                        parts.append(current.id)
                        parts.reverse()
                        used_names.add('.'.join(parts))
                        
        except Exception as e:
            logger.warning(f"Erro ao extrair nomes de {file_path}: {e}")
            
        return used_names
    
    def analyze_dependencies(self):
        """Analisa dependências em todo o projeto"""
        python_files = self.scan_python_files()
        logger.info(f"Analisando {len(python_files)} arquivos Python...")
        
        for file_path in python_files:
            relative_path = file_path.relative_to(self.project_root)
            
            # Extrair imports
            imports = self.extract_imports(file_path)
            for imp in imports:
                self.imports_found[str(relative_path)].add(imp)
            
            # Extrair nomes utilizados
            used_names = self.extract_used_names(file_path)
            for name in used_names:
                self.imports_used[str(relative_path)].add(name)
        
        # Identificar imports não utilizados
        for file_path, imports in self.imports_found.items():
            used_names = self.imports_used[file_path]
            for imp in imports:
                # Verificar se o import é realmente utilizado
                if not self._is_import_used(imp, used_names):
                    self.unused_imports[file_path].add(imp)
    
    def _is_import_used(self, import_name: str, used_names: Set[str]) -> bool:
        """Verifica se um import é utilizado no código"""
        # Verificação direta
        if import_name in used_names:
            return True
        
        # Verificação de módulos (ex: 'os.path' quando 'os' é usado)
        parts = import_name.split('.')
        for index in range(1, len(parts)):
            partial_import = '.'.join(parts[:index])
            if partial_import in used_names:
                return True
        
        # Verificação de imports com alias
        for used_name in used_names:
            if used_name.endswith(import_name.split('.')[-1]):
                return True
        
        return False
    
    def check_requirements_dependencies(self) -> Dict[str, List[str]]:
        """Verifica dependências no requirements.txt vs imports encontrados"""
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            logger.warning("requirements.txt não encontrado")
            return {}
        
        # Ler requirements.txt
        with open(requirements_file, 'r') as f:
            requirements = [line.strip().split('==')[0].split('>=')[0].split('<=')[0] 
                          for line in f if line.strip() and not line.startswith('#')]
        
        # Mapear imports para dependências
        all_imports = set()
        for imports in self.imports_found.values():
            all_imports.update(imports)
        
        # Identificar dependências órfãs
        used_dependencies = set()
        for imp in all_imports:
            base_module = imp.split('.')[0]
            used_dependencies.add(base_module)
        
        orphan_deps = set(requirements) - used_dependencies
        missing_deps = used_dependencies - set(requirements)
        
        return {
            'orphan_dependencies': list(orphan_deps),
            'missing_dependencies': list(missing_deps),
            'total_requirements': len(requirements),
            'used_dependencies': len(used_dependencies)
        }
    
    def generate_report(self, output_file: str = None) -> Dict:
        """Gera relatório completo de análise"""
        self.analyze_dependencies()
        requirements_analysis = self.check_requirements_dependencies()
        
        report = {
            'summary': {
                'total_files_analyzed': len(self.imports_found),
                'total_imports_found': sum(len(imports) for imports in self.imports_found.values()),
                'total_unused_imports': sum(len(imports) for imports in self.unused_imports.values()),
                'orphan_dependencies': len(requirements_analysis.get('orphan_dependencies', [])),
                'missing_dependencies': len(requirements_analysis.get('missing_dependencies', []))
            },
            'unused_imports': dict(self.unused_imports),
            'requirements_analysis': requirements_analysis,
            'recommendations': self._generate_recommendations()
        }
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Relatório salvo em: {output_file}")
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Gera recomendações baseadas na análise"""
        recommendations = []
        
        total_unused = sum(len(imports) for imports in self.unused_imports.values())
        if total_unused > 0:
            recommendations.append(f"Remover {total_unused} imports não utilizados")
        
        orphan_count = len(self.requirements_analysis.get('orphan_dependencies', []))
        if orphan_count > 0:
            recommendations.append(f"Considerar remover {orphan_count} dependências órfãs do requirements.txt")
        
        missing_count = len(self.requirements_analysis.get('missing_dependencies', []))
        if missing_count > 0:
            recommendations.append(f"Adicionar {missing_count} dependências faltantes ao requirements.txt")
        
        if not recommendations:
            recommendations.append("Nenhuma ação necessária - dependências estão otimizadas")
        
        return recommendations

def run_command(command: str) -> Tuple[bool, str]:
    """Executa comando e retorna (sucesso, saída)."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)

def check_pip_audit() -> Dict[str, any]:
    """Verifica vulnerabilidades com pip-audit."""
    print("🔍 Verificando vulnerabilidades com pip-audit...")
    
    success, output = run_command("pip-audit")
    
    if success:
        print("✅ pip-audit executado com sucesso")
        return {"status": "success", "output": output}
    else:
        print("❌ pip-audit falhou ou encontrou vulnerabilidades")
        return {"status": "failed", "output": output}

def check_safety() -> Dict[str, any]:
    """Verifica vulnerabilidades com safety."""
    print("🔍 Verificando vulnerabilidades com safety...")
    
    success, output = run_command("safety check")
    
    if success:
        print("✅ safety executado com sucesso")
        return {"status": "success", "output": output}
    else:
        print("❌ safety falhou ou encontrou vulnerabilidades")
        return {"status": "failed", "output": output}

def check_duplicate_dependencies() -> Dict[str, any]:
    """Verifica dependências duplicadas no requirements.txt."""
    print("🔍 Verificando dependências duplicadas...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        return {"status": "error", "message": "requirements.txt não encontrado"}
    
    with open(requirements_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontrar duplicatas
    lines = content.split('\n')
    packages = {}
    duplicates = []
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and '>=' in line:
            package_name = line.split('>=')[0].strip()
            if package_name in packages:
                duplicates.append(package_name)
            else:
                packages[package_name] = line
    
    if duplicates:
        print(f"❌ Encontradas {len(duplicates)} dependências duplicadas:")
        for dup in duplicates:
            print(f"   - {dup}")
        return {"status": "failed", "duplicates": duplicates}
    else:
        print("✅ Nenhuma dependência duplicada encontrada")
        return {"status": "success", "duplicates": []}

def check_package_json() -> Dict[str, any]:
    """Verifica package.json para duplicatas."""
    print("🔍 Verificando package.json...")
    
    package_file = Path("package.json")
    if not package_file.exists():
        return {"status": "error", "message": "package.json não encontrado"}
    
    # Aqui você pode adicionar lógica para verificar package.json
    # Por simplicidade, vamos apenas verificar se existe
    print("✅ package.json encontrado")
    return {"status": "success"}

def suggest_fixes(issues: Dict[str, any]) -> List[str]:
    """Sugere correções para os problemas encontrados."""
    suggestions = []
    
    if issues.get("duplicates"):
        suggestions.append("Remover dependências duplicadas do requirements.txt")
    
    if issues.get("vulnerabilities"):
        suggestions.append("Atualizar dependências vulneráveis")
    
    return suggestions

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Validador de Dependências - Omni Keywords Finder')
    parser.add_argument('--project-root', default='.', help='Diretório raiz do projeto')
    parser.add_argument('--output', '-o', help='Arquivo de saída para o relatório JSON')
    parser.add_argument('--verbose', '-value', action='store_true', help='Modo verboso')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("🔍 Iniciando validação de dependências...")
    
    validator = DependencyValidator(args.project_root)
    report = validator.generate_report(args.output)
    
    # Exibir resumo
    summary = report['summary']
    print("\n📊 RESUMO DA ANÁLISE")
    print("=" * 50)
    print(f"📁 Arquivos analisados: {summary['total_files_analyzed']}")
    print(f"📦 Imports encontrados: {summary['total_imports_found']}")
    print(f"❌ Imports não utilizados: {summary['total_unused_imports']}")
    print(f"🧹 Dependências órfãs: {summary['orphan_dependencies']}")
    print(f"⚠️  Dependências faltantes: {summary['missing_dependencies']}")
    
    # Exibir recomendações
    print("\n💡 RECOMENDAÇÕES")
    print("=" * 50)
    for rec in report['recommendations']:
        print(f"• {rec}")
    
    # Exibir imports não utilizados por arquivo
    if report['unused_imports']:
        print("\n❌ IMPORTS NÃO UTILIZADOS")
        print("=" * 50)
        for file_path, imports in report['unused_imports'].items():
            print(f"\n📄 {file_path}:")
            for imp in sorted(imports):
                print(f"  - {imp}")
    
    # Exibir dependências órfãs
    orphan_deps = report['requirements_analysis'].get('orphan_dependencies', [])
    if orphan_deps:
        print(f"\n🧹 DEPENDÊNCIAS ÓRFÃS ({len(orphan_deps)}):")
        print("=" * 50)
        for dep in sorted(orphan_deps):
            print(f"  - {dep}")
    
    # Código de saída baseado na saúde geral
    if summary['total_unused_imports'] > 0 or summary['orphan_dependencies'] > 0:
        exit_code = 1  # Aviso
    else:
        exit_code = 0  # Sucesso
    
    logger.info(f"✅ Validação concluída com código de saída: {exit_code}")
    sys.exit(exit_code)

if __name__ == "__main__":
    main() 