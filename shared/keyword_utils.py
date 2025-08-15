"""
Utilitários centralizados para normalização e validação de palavras-chave.
Elimina duplicidade de lógica entre coletores, processadores e domínio.
"""
import re
import unicodedata
from typing import Optional

def normalizar_termo(termo: str, remover_acentos: bool = False, case_sensitive: bool = False) -> str:
    """
    Normaliza um termo: strip, lower, remove acentos se configurado.
    """
    if not termo:
        return ""
    termo_norm = termo.strip()
    termo_norm = re.sub(r'\string_data+', ' ', termo_norm)
    if not case_sensitive:
        termo_norm = termo_norm.lower()
    if remover_acentos:
        termo_norm = unicodedata.normalize('NFKD', termo_norm).encode('ASCII', 'ignore').decode('ASCII')
    return termo_norm

def validar_termo(termo: str, min_caracteres: int = 2, max_caracteres: int = 100, caracteres_permitidos: Optional[str] = None) -> bool:
    """
    Valida um termo conforme tamanho e caracteres permitidos.
    """
    if not termo or not (min_caracteres <= len(termo) <= max_caracteres):
        return False
    if caracteres_permitidos and not all(c in caracteres_permitidos for c in termo):
        return False
    return True

# TODO: Atualizar coletores, processadores e domínio para usar estas funções (🔶 pendente de testes) 