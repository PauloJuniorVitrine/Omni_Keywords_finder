#!/usr/bin/env python3
"""
Script de Validação de Dependências - IMP-003
=============================================

Tracing ID: IMP003_DEPENDENCY_VALIDATION_20241227
Data/Hora: 2024-12-27 22:35:00 UTC
Versão: 1.0

Este script valida que não há quebras de dependência após a limpeza de dead code.
"""

import os
import sys
import ast
import logging
from pathlib import Path
from typing import List, Dict, Set, Tuple
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)string_data] [%(levelname)string_data] %(message)string_data',
    handlers=[
        logging.FileHandler('logs/validacao_dependencias_imp003.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class DependencyValidator:
    """Classe para validação de dependências após limpeza."""
    
    def __init__(self, projeto_root: str = "."):
        self.projeto_root = Path(projeto_root)
        self.imports_encontrados = {}
        self.funcoes_encontradas = {}
        self.classes_encontradas = {}
        self.erros_validacao = []
        self.warnings = []
        
        # Diretórios a excluir da análise
        self.excluir_dirs = {
            '.venv', '__pycache__', '.git', 'node_modules', 
            'coverage', 'htmlcov', 'backup_sistema_antigo_20241227'
        }
    
    def analisar_arquivo_python(self, arquivo: Path) -> Dict:
        """Analisa um arquivo Python para extrair imports, funções e classes."""
        resultado = {
            'imports': [],
            'funcoes': [],
            'classes': [],
            'erros': []
        }
        
        try:
            with open(arquivo, 'r', encoding='utf-8', errors='ignore') as f:
                conteudo = f.read()
            
            # Parse do AST
            tree = ast.parse(conteudo)
            
            # Extrair imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        resultado['imports'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        resultado['imports'].append(f"{module}.{alias.name}")
                elif isinstance(node, ast.FunctionDef):
                    resultado['funcoes'].append(node.name)
                elif isinstance(node, ast.ClassDef):
                    resultado['classes'].append(node.name)
                    
        except Exception as e:
            resultado['erros'].append(str(e))
            logger.warning(f"Erro ao analisar {arquivo}: {e}")
        
        return resultado
    
    def verificar_imports_utilizados(self, arquivo: Path, imports: List[str]) -> List[str]:
        """Verifica se os imports são realmente utilizados no arquivo."""
        imports_nao_utilizados = []
        
        try:
            with open(arquivo, 'r', encoding='utf-8', errors='ignore') as f:
                conteudo = f.read()
            
            for import_name in imports:
                # Verificar se o import é usado no código (análise básica)
                nome_base = import_name.split('.')[-1]
                if nome_base not in conteudo.replace(f'import {import_name}', '').replace(f'from {import_name}', ''):
                    imports_nao_utilizados.append(import_name)
                    
        except Exception as e:
            logger.warning(f"Erro ao verificar imports em {arquivo}: {e}")
        
        return imports_nao_utilizados
    
    def verificar_dependencias_cruzadas(self) -> Dict:
        """Verifica dependências cruzadas entre módulos."""
        dependencias = {}
        
        # Analisar todos os arquivos Python
        for arquivo in self.projeto_root.rglob("*.py"):
            if not any(excluir in arquivo.parts for excluir in self.excluir_dirs):
                rel_path = arquivo.relative_to(self.projeto_root)
                modulo = str(rel_path).replace('\\', '.').replace('/', '.').replace('.py', '')
                
                analise = self.analisar_arquivo_python(arquivo)
                dependencias[modulo] = {
                    'imports': analise['imports'],
                    'funcoes': analise['funcoes'],
                    'classes': analise['classes'],
                    'erros': analise['erros']
                }
        
        return dependencias
    
    def validar_imports_internos(self, dependencias: Dict) -> List[Dict]:
        """Valida se os imports internos existem."""
        problemas = []
        
        for modulo, info in dependencias.items():
            for import_name in info['imports']:
                # Verificar apenas imports internos (que começam com o nome do projeto)
                if import_name.startswith(('infrastructure', 'backend', 'shared', 'tests')):
                    # Verificar se o módulo existe
                    modulo_path = self.projeto_root / import_name.replace('.', '/') / '__init__.py'
                    if not modulo_path.exists():
                        # Tentar como arquivo .py
                        modulo_path = self.projeto_root / f"{import_name.replace('.', '/')}.py"
                        if not modulo_path.exists():
                            problemas.append({
                                'modulo': modulo,
                                'import_problema': import_name,
                                'tipo': 'import_inexistente'
                            })
        
        return problemas
    
    def executar_validacao(self) -> Dict:
        """Executa a validação completa de dependências."""
        logger.info("🔍 Iniciando validação de dependências - IMP-003...")
        
        # 1. Analisar dependências
        dependencias = self.verificar_dependencias_cruzadas()
        logger.info(f"📊 Analisados {len(dependencias)} módulos")
        
        # 2. Validar imports internos
        problemas_imports = self.validar_imports_internos(dependencias)
        logger.info(f"⚠️ Encontrados {len(problemas_imports)} problemas de imports")
        
        # 3. Verificar imports não utilizados
        imports_nao_utilizados = []
        for modulo, info in dependencias.items():
            arquivo_path = self.projeto_root / modulo.replace('.', '/') / '__init__.py'
            if not arquivo_path.exists():
                arquivo_path = self.projeto_root / f"{modulo.replace('.', '/')}.py"
            
            if arquivo_path.exists():
                nao_utilizados = self.verificar_imports_utilizados(arquivo_path, info['imports'])
                if nao_utilizados:
                    imports_nao_utilizados.extend([{
                        'modulo': modulo,
                        'imports': nao_utilizados
                    }])
        
        logger.info(f"📦 Encontrados {len(imports_nao_utilizados)} módulos com imports não utilizados")
        
        # 4. Gerar relatório
        relatorio = {
            'timestamp': datetime.now().isoformat(),
            'tracing_id': 'IMP003_DEPENDENCY_VALIDATION_20241227',
            'total_modulos_analisados': len(dependencias),
            'problemas_imports': problemas_imports,
            'total_problemas_imports': len(problemas_imports),
            'imports_nao_utilizados': imports_nao_utilizados,
            'total_imports_nao_utilizados': len(imports_nao_utilizados),
            'dependencias': dependencias,
            'status': 'OK' if len(problemas_imports) == 0 else 'PROBLEMAS_ENCONTRADOS'
        }
        
        # 5. Salvar relatório
        self.salvar_relatorio(relatorio)
        
        logger.info(f"✅ Validação de dependências concluída!")
        logger.info(f"📊 Status: {relatorio['status']}")
        logger.info(f"   - Módulos analisados: {len(dependencias)}")
        logger.info(f"   - Problemas de imports: {len(problemas_imports)}")
        logger.info(f"   - Imports não utilizados: {len(imports_nao_utilizados)}")
        
        return relatorio
    
    def salvar_relatorio(self, relatorio: Dict):
        """Salva o relatório de validação."""
        relatorio_path = self.projeto_root / "logs" / "relatorio_validacao_dependencias_imp003.json"
        relatorio_path.parent.mkdir(exist_ok=True)
        
        import json
        with open(relatorio_path, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Relatório salvo em: {relatorio_path}")

def main():
    """Função principal."""
    print("🔍 VALIDAÇÃO DE DEPENDÊNCIAS - IMP-003")
    print("=" * 50)
    
    # Executar validação
    validador = DependencyValidator()
    relatorio = validador.executar_validacao()
    
    # Exibir resultados
    print(f"\n📊 RESULTADOS VALIDAÇÃO IMP-003:")
    print(f"   📁 Módulos analisados: {relatorio['total_modulos_analisados']}")
    print(f"   ⚠️ Problemas de imports: {relatorio['total_problemas_imports']}")
    print(f"   📦 Imports não utilizados: {relatorio['total_imports_nao_utilizados']}")
    print(f"   🎯 Status: {relatorio['status']}")
    
    if relatorio['problemas_imports']:
        print("\n❌ Problemas de imports encontrados:")
        for problema in relatorio['problemas_imports'][:10]:  # Mostrar apenas os primeiros 10
            print(f"   - {problema['modulo']}: {problema['import_problema']}")
        
        if len(relatorio['problemas_imports']) > 10:
            print(f"   ... e mais {len(relatorio['problemas_imports']) - 10} problemas")
    
    if relatorio['imports_nao_utilizados']:
        print("\n📦 Módulos com imports não utilizados:")
        for item in relatorio['imports_nao_utilizados'][:10]:  # Mostrar apenas os primeiros 10
            print(f"   - {item['modulo']}: {', '.join(item['imports'])}")
        
        if len(relatorio['imports_nao_utilizados']) > 10:
            print(f"   ... e mais {len(relatorio['imports_nao_utilizados']) - 10} módulos")
    
    print(f"\n📄 Relatório completo salvo em: logs/relatorio_validacao_dependencias_imp003.json")
    
    if relatorio['status'] == 'OK':
        print("\n🎯 IMP-003: Validação de Dependências - APROVADA!")
    else:
        print("\n⚠️ IMP-003: Validação de Dependências - PROBLEMAS ENCONTRADOS!")

if __name__ == "__main__":
    main() 