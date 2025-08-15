#!/usr/bin/env python3
"""
Script de Limpeza Automática - Omni Keywords Finder
Tracing ID: CLEANUP_20241219_001

Este script remove arquivos .bak e identifica dead code no projeto.
"""

import os
import re
import glob
import logging
from pathlib import Path
from typing import List, Dict, Tuple

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)string_data] [%(asctime)string_data] %(message)string_data',
    handlers=[
        logging.FileHandler('logs/limpeza_automatica.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LimpezaAutomatica:
    """Classe para limpeza automática do projeto."""
    
    def __init__(self, projeto_root: str = "."):
        self.projeto_root = Path(projeto_root)
        self.arquivos_removidos = []
        self.dead_code_identificado = []
        self.excluir_dirs = {'.venv', '__pycache__', '.git', 'node_modules', 'coverage', 'htmlcov'}
        
    def encontrar_arquivos_bak(self) -> List[Path]:
        """Encontra todos os arquivos .bak no projeto."""
        arquivos_bak = []
        
        for arquivo in self.projeto_root.rglob("*.bak"):
            # Verificar se não está em diretório excluído
            if not any(excluir in arquivo.parts for excluir in self.excluir_dirs):
                arquivos_bak.append(arquivo)
                
        return arquivos_bak
    
    def remover_arquivos_bak(self, arquivos: List[Path]) -> int:
        """Remove arquivos .bak especificados."""
        removidos = 0
        
        for arquivo in arquivos:
            try:
                arquivo.unlink()
                self.arquivos_removidos.append(str(arquivo))
                logger.info(f"✅ Arquivo .bak removido: {arquivo}")
                removidos += 1
            except Exception as e:
                logger.error(f"❌ Erro ao remover {arquivo}: {e}")
                
        return removidos
    
    def identificar_dead_code(self) -> Dict[str, List[str]]:
        """Identifica possíveis dead code no projeto."""
        dead_code = {
            'comentarios_extensos': [],
            'imports_comentados': [],
            'funcoes_comentadas': [],
            'classes_comentadas': []
        }
        
        # Padrões para identificar dead code
        padroes = {
            'comentarios_extensos': r'#.*\n#.*\n#.*\n#.*\n#.*',
            'imports_comentados': r'#\string_data*(?:from|import)\string_data+',
            'funcoes_comentadas': r'#\string_data*def\string_data+\w+',
            'classes_comentadas': r'#\string_data*class\string_data+\w+'
        }
        
        for arquivo in self.projeto_root.rglob("*.py"):
            # Pular diretórios excluídos
            if any(excluir in arquivo.parts for excluir in self.excluir_dirs):
                continue
                
            try:
                conteudo = arquivo.read_text(encoding='utf-8')
                
                for tipo, padrao in padroes.items():
                    matches = re.finditer(padrao, conteudo, re.MULTILINE)
                    for match in matches:
                        linha = conteudo.count('\n', 0, match.start()) + 1
                        dead_code[tipo].append(f"{arquivo}:{linha} - {match.group()}")
                        
            except Exception as e:
                logger.warning(f"⚠️ Erro ao analisar {arquivo}: {e}")
                
        return dead_code
    
    def validar_dependencias(self) -> bool:
        """Valida se não há dependências quebradas após limpeza."""
        try:
            # Tentar importar módulos principais
            import sys
            sys.path.insert(0, str(self.projeto_root))
            
            # Testar imports críticos
            imports_criticos = [
                'infrastructure.processamento.processador_keywords',
                'backend.app.services.execucao_service',
                'shared.utils.normalizador_central'
            ]
            
            for modulo in imports_criticos:
                try:
                    __import__(modulo)
                    logger.info(f"✅ Import válido: {modulo}")
                except ImportError as e:
                    logger.error(f"❌ Import quebrado: {modulo} - {e}")
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na validação de dependências: {e}")
            return False
    
    def gerar_relatorio(self) -> str:
        """Gera relatório da limpeza realizada."""
        relatorio = f"""
# 📋 RELATÓRIO DE LIMPEZA AUTOMÁTICA
Tracing ID: CLEANUP_20241219_001
Data: {os.popen('date').read().strip()}

## 📁 Arquivos .bak Removidos ({len(self.arquivos_removidos)})
"""
        
        for arquivo in self.arquivos_removidos:
            relatorio += f"- {arquivo}\n"
            
        relatorio += f"""
## 🧹 Dead Code Identificado
"""
        
        for tipo, itens in self.dead_code_identificado.items():
            if itens:
                relatorio += f"\n### {tipo.title()} ({len(itens)})\n"
                for item in itens[:10]:  # Limitar a 10 itens por tipo
                    relatorio += f"- {item}\n"
                if len(itens) > 10:
                    relatorio += f"- ... e mais {len(itens) - 10} itens\n"
                    
        return relatorio
    
    def executar_limpeza(self) -> bool:
        """Executa a limpeza completa do projeto."""
        logger.info("🚀 Iniciando limpeza automática...")
        
        # 1. Encontrar arquivos .bak
        arquivos_bak = self.encontrar_arquivos_bak()
        logger.info(f"📁 Encontrados {len(arquivos_bak)} arquivos .bak")
        
        # 2. Remover arquivos .bak
        if arquivos_bak:
            removidos = self.remover_arquivos_bak(arquivos_bak)
            logger.info(f"🗑️ Removidos {removidos} arquivos .bak")
        else:
            logger.info("✅ Nenhum arquivo .bak encontrado")
            
        # 3. Identificar dead code
        self.dead_code_identificado = self.identificar_dead_code()
        total_dead_code = sum(len(itens) for itens in self.dead_code_identificado.values())
        logger.info(f"🔍 Identificados {total_dead_code} possíveis dead code")
        
        # 4. Validar dependências
        dependencias_ok = self.validar_dependencias()
        if dependencias_ok:
            logger.info("✅ Validação de dependências: OK")
        else:
            logger.error("❌ Validação de dependências: FALHOU")
            return False
            
        # 5. Gerar relatório
        relatorio = self.gerar_relatorio()
        relatorio_path = self.projeto_root / "logs" / "relatorio_limpeza.md"
        relatorio_path.parent.mkdir(exist_ok=True)
        relatorio_path.write_text(relatorio, encoding='utf-8')
        
        logger.info(f"📄 Relatório salvo em: {relatorio_path}")
        logger.info("🎉 Limpeza automática concluída com sucesso!")
        
        return True

def main():
    """Função principal."""
    limpeza = LimpezaAutomatica()
    sucesso = limpeza.executar_limpeza()
    
    if sucesso:
        print("\n✅ Limpeza concluída com sucesso!")
        print("📄 Verifique o relatório em: logs/relatorio_limpeza.md")
    else:
        print("\n❌ Limpeza falhou. Verifique os logs.")
        return 1
        
    return 0

if __name__ == "__main__":
    exit(main()) 