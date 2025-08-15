"""
Módulo: ranking_config_v1
Permite configuração dinâmica dos pesos de ranking para seleção de palavras-chave.
"""
from typing import List, Dict, Any

class RankingConfig:
    """
    Classe para definir e aplicar critérios de ranking customizados.
    """
    def __init__(self, pesos: Dict[str, float] = None):
        # Pesos padrão: volume, concorrencia, tendencia, intencao, ctr
        self.pesos = pesos or {
            'volume': 0.4,
            'concorrencia': 0.2,
            'tendencia': 0.2,
            'intencao': 0.1,
            'ctr': 0.1
        }

    def ranquear(self, palavras_chave: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Aplica o ranking customizado e retorna a lista ordenada.
        """
        def score(p):
            return sum([
                p.get('volume', 0) * self.pesos['volume'],
                (1 - p.get('concorrencia', 0)) * self.pesos['concorrencia'],
                p.get('tendencia', 0) * self.pesos['tendencia'],
                p.get('intencao', 0) * self.pesos['intencao'],
                p.get('ctr', 0) * self.pesos['ctr'],
            ])
        return sorted(palavras_chave, key=score, reverse=True) 