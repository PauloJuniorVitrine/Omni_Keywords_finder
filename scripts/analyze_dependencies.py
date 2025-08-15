from typing import Dict, List, Optional, Any
#!/usr/bin/env python3
"""
Script de Análise de Dependências - Omni Keywords Finder
Tracing ID: ANALYZE_DEPS_001_20241227
"""

import os
import ast
import json
import datetime
from pathlib import Path
from collections import defaultdict

class DependencyAnalyzer:
    def __init__(self):
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.dependencies = defaultdict(set)
        self.functions = defaultdict(list)
        self.classes = defaultdict(list)
        self.imports = defaultdict(list)
        self.critical_points = []
        
    def analyze_python_file(self, file_path):
        """Analisa um arquivo Python e extrai dependências"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Analisar imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.imports[file_path].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        self.imports[file_path].append(f"{module}.{alias.name}")
                
                # Analisar definições de funções
                elif isinstance(node, ast.FunctionDef):
                    self.functions[file_path].append({
                        "name": node.name,
                        "lineno": node.lineno,
                        "args": [arg.arg for arg in node.args.args]
                    })
                
                # Analisar definições de classes
                elif isinstance(node, ast.ClassDef):
                    self.classes[file_path].append({
                        "name": node.name,
                        "lineno": node.lineno,
                        "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    })
                    
        except Exception as e:
            print(f"Erro ao analisar {file_path}: {e}")
    
    def find_critical_dependencies(self):
        """Identifica dependências críticas"""
        critical_modules = [
            "infrastructure.processamento.processador_keywords",
            "infrastructure.validacao.google_keyword_planner_validator",
            "infrastructure.cache.cache_inteligente_cauda_longa",
            "infrastructure.monitoring.performance_cauda_longa"
        ]
        
        for file_path, imports in self.imports.items():
            for imp in imports:
                for critical in critical_modules:
                    if critical in imp:
                        self.critical_points.append({
                            "file": file_path,
                            "import": imp,
                            "critical_module": critical,
                            "risk": "HIGH"
                        })
    
    def analyze_directory(self, directory):
        """Analisa um diretório recursivamente"""
        print(f"🔍 Analisando diretório: {directory}")
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self.analyze_python_file(file_path)
    
    def generate_report(self):
        """Gera relatório de dependências"""
        print(f"📊 GERANDO RELATÓRIO DE DEPENDÊNCIAS")
        
        # Encontrar dependências críticas
        self.find_critical_dependencies()
        
        report = {
            "timestamp": self.timestamp,
            "sistema": "Omni Keywords Finder",
            "tipo": "Análise de Dependências",
            "estatisticas": {
                "total_arquivos": len(self.imports),
                "total_funcoes": sum(len(funcs) for funcs in self.functions.values()),
                "total_classes": sum(len(classes) for classes in self.classes.values()),
                "total_imports": sum(len(imps) for imps in self.imports.values()),
                "pontos_criticos": len(self.critical_points)
            },
            "dependencias_criticas": self.critical_points,
            "imports_por_arquivo": dict(self.imports),
            "funcoes_por_arquivo": dict(self.functions),
            "classes_por_arquivo": dict(self.classes)
        }
        
        # Salvar relatório
        report_file = f"dependencias_analise_{self.timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Relatório salvo em: {report_file}")
        print(f"📊 Estatísticas:")
        print(f"   - Arquivos analisados: {report['estatisticas']['total_arquivos']}")
        print(f"   - Funções encontradas: {report['estatisticas']['total_funcoes']}")
        print(f"   - Classes encontradas: {report['estatisticas']['total_classes']}")
        print(f"   - Imports encontrados: {report['estatisticas']['total_imports']}")
        print(f"   - Pontos críticos: {report['estatisticas']['pontos_criticos']}")
        
        if self.critical_points:
            print(f"\n🚨 PONTOS CRÍTICOS IDENTIFICADOS:")
            for point in self.critical_points:
                print(f"   - {point['file']} importa {point['import']}")
        
        return report

def main():
    analyzer = DependencyAnalyzer()
    
    # Diretórios críticos para análise
    diretorios_criticos = [
        "infrastructure",
        "backend",
        "scripts"
    ]
    
    for diretorio in diretorios_criticos:
        if os.path.exists(diretorio):
            analyzer.analyze_directory(diretorio)
    
    # Gerar relatório
    report = analyzer.generate_report()
    
    print(f"\n🎯 ANÁLISE CONCLUÍDA!")
    print(f"📁 Relatório: dependencias_analise_{analyzer.timestamp}.json")

if __name__ == "__main__":
    main() 