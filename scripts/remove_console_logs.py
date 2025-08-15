#!/usr/bin/env python3
"""
Script para remover console.log de produção
Responsável por limpar logs de debug do frontend.

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Correção 2
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Versão: 1.0.0
"""

import os
import re
import glob
from pathlib import Path
from typing import List, Tuple

def find_tsx_files(directory: str = "app") -> List[str]:
    """Encontra todos os arquivos .tsx no diretório."""
    pattern = os.path.join(directory, "**/*.tsx")
    return glob.glob(pattern, recursive=True)

def remove_console_logs(file_path: str) -> Tuple[bool, int]:
    """
    Remove console.log de um arquivo TSX.
    
    Args:
        file_path: Caminho do arquivo
        
    Returns:
        (modificado, quantidade_removidos)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Padrões para remover console.log
        patterns = [
            # console.log simples
            r'console\.log\([^)]*\);',
            # console.log com template strings
            r'console\.log\(`[^`]*`\);',
            # console.log com múltiplos argumentos
            r'console\.log\([^)]*\);',
            # console.log com comentários
            r'console\.log\([^)]*\);.*?//.*?',
        ]
        
        removed_count = 0
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            if matches:
                # Comentar em vez de remover (mais seguro)
                content = re.sub(
                    pattern,
                    lambda m: f"// {m.group(0)} // Removido para produção",
                    content,
                    flags=re.MULTILINE | re.DOTALL
                )
                removed_count += len(matches)
        
        # Se houve mudanças, salvar arquivo
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, removed_count
        
        return False, 0
        
    except Exception as e:
        print(f"Erro processando {file_path}: {e}")
        return False, 0

def main():
    """Função principal."""
    print("🔧 Removendo console.log de produção...")
    
    # Encontrar arquivos TSX
    tsx_files = find_tsx_files()
    print(f"📁 Encontrados {len(tsx_files)} arquivos TSX")
    
    total_modified = 0
    total_removed = 0
    
    for file_path in tsx_files:
        modified, removed = remove_console_logs(file_path)
        if modified:
            total_modified += 1
            total_removed += removed
            print(f"✅ {file_path}: {removed} console.log removidos")
    
    print(f"\n📊 Resumo:")
    print(f"   Arquivos modificados: {total_modified}")
    print(f"   Console.log removidos: {total_removed}")
    print(f"   Arquivos processados: {len(tsx_files)}")
    
    if total_removed > 0:
        print(f"\n🎉 Limpeza concluída com sucesso!")
    else:
        print(f"\nℹ️  Nenhum console.log encontrado para remover.")

if __name__ == "__main__":
    main() 