"""
Módulo: keyword_classification_rules_v1
Permite definir e aplicar regras customizadas para classificar palavras-chave como primárias ou secundárias.
"""
from typing import List, Dict, Any, Callable

class KeywordClassifier:
    """
    Classe para classificar palavras-chave em primárias e secundárias conforme regras customizadas.
    """
    def __init__(self, regra: Callable[[Dict[str, Any]], str]):
        """
        regra: função que recebe uma palavra-chave (dict) e retorna 'primaria', 'secundaria' ou None.
        """
        self.regra = regra

    def classificar(self, palavras_chave: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retorna dict com listas de 'primarias' e 'secundarias'.
        """
        primarias, secundarias = [], []
        for p in palavras_chave:
            tipo = self.regra(p)
            if tipo == 'primaria':
                primarias.append(p)
            elif tipo == 'secundaria':
                secundarias.append(p)
        return {'primarias': primarias, 'secundarias': secundarias}

# Exemplos de regras

def regra_por_volume(p: Dict[str, Any], limiar: int = 1000) -> str:
    if p.get('volume', 0) >= limiar:
        return 'primaria'
    return 'secundaria'

def regra_por_intencao(p: Dict[str, Any], limiar: float = 0.7) -> str:
    if p.get('intencao', 0) >= limiar:
        return 'primaria'
    return 'secundaria' 