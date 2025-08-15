#!/usr/bin/env python3
"""
Script de Limpeza de Arquivos .bak e Dead Code
==============================================

Tracing ID: CLEANUP_20241219_001
Data/Hora: 2024-12-19 10:45:00 UTC
Versão: 1.0

Este script remove arquivos de backup (.bak) e identifica dead code
no projeto Omni Keywords Finder.
"""

import os
import re
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)string_data] [%(levelname)string_data] %(message)string_data',
    handlers=[
        logging.FileHandler('logs/limpeza_arquivos_bak.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class LimpezaArquivosBak:
    """Classe para limpeza de arquivos .bak e dead code."""
    
    def __init__(self, projeto_root: str = "."):
        self.projeto_root = Path(projeto_root)
        self.arquivos_removidos = []
        self.dead_code_identificado = []
        self.erros = []
        
    def encontrar_arquivos_bak(self) -> List[Path]:
        """Encontra todos os arquivos .bak no projeto."""
        arquivos_bak = []
        
        # Padrões de arquivos de backup
        padroes_backup = [
            "*.bak*",
            "*~",
            "*.tmp",
            "*.old",
            "*.backup"
        ]
        
        for padrao in padroes_backup:
            for arquivo in self.projeto_root.rglob(padrao):
                # Excluir .venv e node_modules
                if ".venv" in str(arquivo) or "node_modules" in str(arquivo):
                    continue
                arquivos_bak.append(arquivo)
                
        return arquivos_bak
    
    def verificar_dead_code(self, arquivo: Path) -> List[Dict]:
        """Verifica se há dead code no arquivo."""
        dead_code = []
        
        if not arquivo.is_file() or arquivo.suffix not in ['.py', '.js', '.ts', '.tsx']:
            return dead_code
            
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
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
    
    def remover_arquivo_bak(self, arquivo: Path) -> bool:
        """Remove um arquivo de backup."""
        try:
            if arquivo.exists():
                arquivo.unlink()
                logger.info(f"✅ Arquivo removido: {arquivo}")
                self.arquivos_removidos.append(str(arquivo))
                return True
        except Exception as e:
            logger.error(f"❌ Erro ao remover {arquivo}: {e}")
            self.erros.append(f"Erro ao remover {arquivo}: {e}")
            return False
    
    def executar_limpeza(self) -> Dict:
        """Executa a limpeza completa."""
        logger.info("🚀 Iniciando limpeza de arquivos .bak e dead code...")
        
        # Encontrar arquivos .bak
        arquivos_bak = self.encontrar_arquivos_bak()
        logger.info(f"📁 Encontrados {len(arquivos_bak)} arquivos de backup")
        
        # Remover arquivos .bak
        for arquivo in arquivos_bak:
            self.remover_arquivo_bak(arquivo)
        
        # Verificar dead code nos arquivos principais
        logger.info("🔍 Verificando dead code...")
        arquivos_principais = [
            self.projeto_root / "infrastructure",
            self.projeto_root / "backend", 
            self.projeto_root / "shared",
            self.projeto_root / "tests"
        ]
        
        for diretorio in arquivos_principais:
            if diretorio.exists():
                for arquivo in diretorio.rglob("*"):
                    if arquivo.is_file():
                        dead_code = self.verificar_dead_code(arquivo)
                        if dead_code:
                            self.dead_code_identificado.extend(dead_code)
        
        # Gerar relatório
        relatorio = {
            'timestamp': datetime.now().isoformat(),
            'arquivos_removidos': self.arquivos_removidos,
            'total_arquivos_removidos': len(self.arquivos_removidos),
            'dead_code_identificado': self.dead_code_identificado,
            'total_dead_code': len(self.dead_code_identificado),
            'erros': self.erros,
            'total_erros': len(self.erros)
        }
        
        # Salvar relatório
        self.salvar_relatorio(relatorio)
        
        logger.info(f"✅ Limpeza concluída!")
        logger.info(f"📊 Resumo:")
        logger.info(f"   - Arquivos removidos: {len(self.arquivos_removidos)}")
        logger.info(f"   - Dead code identificado: {len(self.dead_code_identificado)}")
        logger.info(f"   - Erros: {len(self.erros)}")
        
        return relatorio
    
    def salvar_relatorio(self, relatorio: Dict):
        """Salva o relatório de limpeza."""
        relatorio_path = self.projeto_root / "logs" / "relatorio_limpeza.json"
        relatorio_path.parent.mkdir(exist_ok=True)
        
        import json
        with open(relatorio_path, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Relatório salvo em: {relatorio_path}")

def main():
    """Função principal."""
    print("🧹 LIMPEZA DE ARQUIVOS .BAK E DEAD CODE")
    print("=" * 50)
    
    # Executar limpeza
    limpeza = LimpezaArquivosBak()
    relatorio = limpeza.executar_limpeza()
    
    # Exibir resultados
    print("\n📊 RESULTADOS:")
    print(f"   ✅ Arquivos removidos: {relatorio['total_arquivos_removidos']}")
    print(f"   🔍 Dead code identificado: {relatorio['total_dead_code']}")
    print(f"   ❌ Erros: {relatorio['total_erros']}")
    
    if relatorio['arquivos_removidos']:
        print("\n🗑️ Arquivos removidos:")
        for arquivo in relatorio['arquivos_removidos']:
            print(f"   - {arquivo}")
    
    if relatorio['dead_code_identificado']:
        print("\n⚠️ Dead code identificado:")
        for item in relatorio['dead_code_identificado'][:10]:  # Mostrar apenas os primeiros 10
            print(f"   - {item['arquivo']}:{item['linha']} - {item['conteudo']}")
        
        if len(relatorio['dead_code_identificado']) > 10:
            print(f"   ... e mais {len(relatorio['dead_code_identificado']) - 10} itens")
    
    if relatorio['erros']:
        print("\n❌ Erros encontrados:")
        for erro in relatorio['erros']:
            print(f"   - {erro}")
    
    print(f"\n📄 Relatório completo salvo em: logs/relatorio_limpeza.json")

if __name__ == "__main__":
    main() 