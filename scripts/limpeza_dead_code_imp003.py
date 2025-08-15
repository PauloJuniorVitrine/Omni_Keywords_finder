#!/usr/bin/env python3
"""
Script de Limpeza de Dead Code - IMP-003
========================================

Tracing ID: IMP003_DEAD_CODE_CLEANUP_20241227
Data/Hora: 2024-12-27 22:30:00 UTC
Versão: 1.0

Este script implementa a melhoria IMP-003: Limpeza Completa de Dead Code
no projeto Omni Keywords Finder.
"""

import os
import re
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Set
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)string_data] [%(levelname)string_data] %(message)string_data',
    handlers=[
        logging.FileHandler('logs/limpeza_dead_code_imp003.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class DeadCodeCleaner:
    """Classe para limpeza de dead code e arquivos desnecessários."""
    
    def __init__(self, projeto_root: str = "."):
        self.projeto_root = Path(projeto_root)
        self.arquivos_removidos = []
        self.dead_code_identificado = []
        self.imports_nao_utilizados = []
        self.erros = []
        
        # Diretórios a excluir da análise
        self.excluir_dirs = {
            '.venv', '__pycache__', '.git', 'node_modules', 
            'coverage', 'htmlcov', 'backup_sistema_antigo_20241227'
        }
        
    def encontrar_arquivos_backup(self) -> List[Path]:
        """Encontra todos os arquivos de backup no projeto."""
        arquivos_backup = []
        
        # Padrões de arquivos de backup
        padroes_backup = [
            "*.bak*",
            "*~",
            "*.tmp",
            "*.old",
            "*.backup",
            "*_backup*",
            "*_old*"
        ]
        
        for padrao in padroes_backup:
            for arquivo in self.projeto_root.rglob(padrao):
                # Excluir diretórios especiais
                if not any(excluir in arquivo.parts for excluir in self.excluir_dirs):
                    arquivos_backup.append(arquivo)
                
        return arquivos_backup
    
    def verificar_dead_code(self, arquivo: Path) -> List[Dict]:
        """Verifica se há dead code no arquivo."""
        dead_code = []
        
        if not arquivo.is_file() or arquivo.suffix not in ['.py', '.js', '.ts', '.tsx']:
            return dead_code
            
        try:
            with open(arquivo, 'r', encoding='utf-8', errors='ignore') as f:
                conteudo = f.read()
                linhas = conteudo.split('\n')
                
            # Padrões de dead code
            padroes_dead_code = [
                r'^\string_data*# TODO.*$',
                r'^\string_data*# FIXME.*$', 
                r'^\string_data*# HACK.*$',
                r'^\string_data*# XXX.*$',
                r'^\string_data*# DEPRECATED.*$',
                r'^\string_data*# REMOVE.*$',
                r'^\string_data*// TODO.*$',
                r'^\string_data*// FIXME.*$',
                r'^\string_data*// HACK.*$',
                r'^\string_data*// XXX.*$',
                r'^\string_data*// DEPRECATED.*$',
                r'^\string_data*// REMOVE.*$'
            ]
            
            for index, linha in enumerate(linhas, 1):
                for padrao in padroes_dead_code:
                    if re.match(padrao, linha):
                        dead_code.append({
                            'linha': index,
                            'conteudo': linha.strip(),
                            'arquivo': str(arquivo)
                        })
                        
        except Exception as e:
            logger.warning(f"Erro ao verificar dead code em {arquivo}: {e}")
            
        return dead_code
    
    def verificar_imports_nao_utilizados(self, arquivo: Path) -> List[Dict]:
        """Verifica imports não utilizados em arquivos Python."""
        imports_nao_utilizados = []
        
        if not arquivo.is_file() or arquivo.suffix != '.py':
            return imports_nao_utilizados
            
        try:
            with open(arquivo, 'r', encoding='utf-8', errors='ignore') as f:
                conteudo = f.read()
                
            # Padrões de imports
            padroes_import = [
                r'^import\string_data+(\w+)',
                r'^from\string_data+(\w+)\string_data+import',
                r'^from\string_data+(\w+\.\w+)\string_data+import'
            ]
            
            imports_encontrados = []
            for padrao in padroes_import:
                matches = re.finditer(padrao, conteudo, re.MULTILINE)
                for match in matches:
                    imports_encontrados.append(match.group(1))
            
            # Verificar se os imports são utilizados (análise básica)
            for import_name in imports_encontrados:
                # Verificar se o import é usado no código
                if import_name not in conteudo.replace(f'import {import_name}', '').replace(f'from {import_name}', ''):
                    imports_nao_utilizados.append({
                        'import': import_name,
                        'arquivo': str(arquivo)
                    })
                        
        except Exception as e:
            logger.warning(f"Erro ao verificar imports em {arquivo}: {e}")
            
        return imports_nao_utilizados
    
    def remover_arquivo_backup(self, arquivo: Path) -> bool:
        """Remove um arquivo de backup."""
        try:
            if arquivo.exists():
                arquivo.unlink()
                logger.info(f"✅ Arquivo de backup removido: {arquivo}")
                self.arquivos_removidos.append(str(arquivo))
                return True
        except Exception as e:
            logger.error(f"❌ Erro ao remover {arquivo}: {e}")
            self.erros.append(f"Erro ao remover {arquivo}: {e}")
            return False
    
    def executar_limpeza(self) -> Dict:
        """Executa a limpeza completa."""
        logger.info("🚀 Iniciando limpeza de dead code - IMP-003...")
        
        # 1. Encontrar e remover arquivos de backup
        arquivos_backup = self.encontrar_arquivos_backup()
        logger.info(f"📁 Encontrados {len(arquivos_backup)} arquivos de backup")
        
        for arquivo in arquivos_backup:
            self.remover_arquivo_backup(arquivo)
        
        # 2. Verificar dead code nos arquivos principais
        logger.info("🔍 Verificando dead code...")
        diretorios_principais = [
            "infrastructure",
            "backend", 
            "shared",
            "tests",
            "scripts"
        ]
        
        for diretorio in diretorios_principais:
            dir_path = self.projeto_root / diretorio
            if dir_path.exists():
                for arquivo in dir_path.rglob("*"):
                    if arquivo.is_file() and not any(excluir in arquivo.parts for excluir in self.excluir_dirs):
                        # Verificar dead code
                        dead_code = self.verificar_dead_code(arquivo)
                        if dead_code:
                            self.dead_code_identificado.extend(dead_code)
                        
                        # Verificar imports não utilizados
                        imports_nao_utilizados = self.verificar_imports_nao_utilizados(arquivo)
                        if imports_nao_utilizados:
                            self.imports_nao_utilizados.extend(imports_nao_utilizados)
        
        # 3. Gerar relatório
        relatorio = {
            'timestamp': datetime.now().isoformat(),
            'tracing_id': 'IMP003_DEAD_CODE_CLEANUP_20241227',
            'arquivos_removidos': self.arquivos_removidos,
            'total_arquivos_removidos': len(self.arquivos_removidos),
            'dead_code_identificado': self.dead_code_identificado,
            'total_dead_code': len(self.dead_code_identificado),
            'imports_nao_utilizados': self.imports_nao_utilizados,
            'total_imports_nao_utilizados': len(self.imports_nao_utilizados),
            'erros': self.erros,
            'total_erros': len(self.erros)
        }
        
        # 4. Salvar relatório
        self.salvar_relatorio(relatorio)
        
        logger.info(f"✅ Limpeza IMP-003 concluída!")
        logger.info(f"📊 Resumo:")
        logger.info(f"   - Arquivos de backup removidos: {len(self.arquivos_removidos)}")
        logger.info(f"   - Dead code identificado: {len(self.dead_code_identificado)}")
        logger.info(f"   - Imports não utilizados: {len(self.imports_nao_utilizados)}")
        logger.info(f"   - Erros: {len(self.erros)}")
        
        return relatorio
    
    def salvar_relatorio(self, relatorio: Dict):
        """Salva o relatório de limpeza."""
        relatorio_path = self.projeto_root / "logs" / "relatorio_limpeza_imp003.json"
        relatorio_path.parent.mkdir(exist_ok=True)
        
        import json
        with open(relatorio_path, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Relatório salvo em: {relatorio_path}")

def main():
    """Função principal."""
    print("🧹 LIMPEZA DE DEAD CODE - IMP-003")
    print("=" * 50)
    
    # Executar limpeza
    limpeza = DeadCodeCleaner()
    relatorio = limpeza.executar_limpeza()
    
    # Exibir resultados
    print("\n📊 RESULTADOS IMP-003:")
    print(f"   ✅ Arquivos de backup removidos: {relatorio['total_arquivos_removidos']}")
    print(f"   🔍 Dead code identificado: {relatorio['total_dead_code']}")
    print(f"   📦 Imports não utilizados: {relatorio['total_imports_nao_utilizados']}")
    print(f"   ❌ Erros: {relatorio['total_erros']}")
    
    if relatorio['arquivos_removidos']:
        print("\n🗑️ Arquivos de backup removidos:")
        for arquivo in relatorio['arquivos_removidos']:
            print(f"   - {arquivo}")
    
    if relatorio['dead_code_identificado']:
        print("\n⚠️ Dead code identificado:")
        for item in relatorio['dead_code_identificado'][:10]:  # Mostrar apenas os primeiros 10
            print(f"   - {item['arquivo']}:{item['linha']} - {item['conteudo']}")
        
        if len(relatorio['dead_code_identificado']) > 10:
            print(f"   ... e mais {len(relatorio['dead_code_identificado']) - 10} itens")
    
    if relatorio['imports_nao_utilizados']:
        print("\n📦 Imports não utilizados:")
        for item in relatorio['imports_nao_utilizados'][:10]:  # Mostrar apenas os primeiros 10
            print(f"   - {item['arquivo']}: {item['import']}")
        
        if len(relatorio['imports_nao_utilizados']) > 10:
            print(f"   ... e mais {len(relatorio['imports_nao_utilizados']) - 10} itens")
    
    if relatorio['erros']:
        print("\n❌ Erros encontrados:")
        for erro in relatorio['erros']:
            print(f"   - {erro}")
    
    print(f"\n📄 Relatório completo salvo em: logs/relatorio_limpeza_imp003.json")
    print("\n🎯 IMP-003: Limpeza de Dead Code - CONCLUÍDA!")

if __name__ == "__main__":
    main() 