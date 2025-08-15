"""
Módulo: keyword_gap_suggestion_v1
Sugere preenchimento de lacunas e valida complementaridade semântica entre palavras-chave primárias e secundárias.
"""
from typing import List, Dict, Any
import difflib

class KeywordGapSuggester:
    """
    Classe para detectar lacunas e sugerir preenchimento inteligente.
    """
    def __init__(self, threshold: float = 0.6):
        self.threshold = threshold

    def detectar_lacunas(self, primarias: List[Dict[str, Any]], secundarias: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detecta se há ausência de primárias ou secundárias.
        """
        return {
            'falta_primaria': len(primarias) == 0,
            'falta_secundaria': len(secundarias) == 0
        }

    def sugerir_secundarias(self, primarias: List[Dict[str, Any]], candidatos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sugere secundárias relevantes para cada primária com base em similaridade textual.
        """
        sugestoes = []
        for p in primarias:
            termo_p = p.get('termo', '')
            similares = [c for c in candidatos if self.similaridade(termo_p, c.get('termo', '')) >= self.threshold]
            sugestoes.extend(similares)
        return sugestoes

    def validar_complementaridade(self, primaria: Dict[str, Any], secundaria: Dict[str, Any]) -> bool:
        """
        Valida se a secundária é semanticamente complementar à primária (similaridade textual simples).
        """
        return self.similaridade(primaria.get('termo', ''), secundaria.get('termo', '')) >= self.threshold

    def similaridade(self, a: str, b: str) -> float:
        """
        Similaridade simples baseada em SequenceMatcher (0 a 1).
        """
        return difflib.SequenceMatcher(None, a, b).ratio() 