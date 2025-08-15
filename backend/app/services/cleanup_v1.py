"""
Módulo: cleanup_v1
Limpeza automática de arquivos antigos em diretórios de exportação/logs.
"""
import os
import time
from typing import List, Optional

def limpar_arquivos_antigos(diretorio: str, dias: int = 30, tipos: Optional[List[str]] = None, dry_run: bool = False) -> List[str]:
    """
    Remove arquivos mais antigos que 'dias' no diretório especificado.
    tipos: lista de extensões (ex: ['.csv', '.log']) ou None para todos.
    dry_run: se True, apenas simula (não remove).
    Retorna lista de arquivos removidos (ou que seriam removidos).
    """
    agora = time.time()
    removidos = []
    for raiz, _, arquivos in os.walk(diretorio):
        for nome in arquivos:
            if tipos and not any(nome.endswith(ext) for ext in tipos):
                continue
            caminho = os.path.join(raiz, nome)
            idade_dias = (agora - os.path.getmtime(caminho)) / 86400
            if idade_dias > dias:
                removidos.append(caminho)
                if not dry_run:
                    os.remove(caminho)
    return removidos 