"""
Módulo: ranking_explain_v1
Gera relatório detalhado explicando o score de cada palavra-chave.
"""
from typing import List, Dict, Any
from backend.app.services.ranking_config_v1 import RankingConfig

class RankingExplain:
    """
    Classe para gerar explicação detalhada do ranking de palavras-chave.
    """
    def __init__(self, ranking_config: RankingConfig):
        self.ranking_config = ranking_config

    def explicar(self, palavras_chave: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Retorna lista de dicts com score e detalhamento dos critérios para cada palavra-chave.
        """
        explicacoes = []
        for p in palavras_chave:
            detalhes = {
                'termo': p.get('termo'),
                'score': 0,
                'detalhes': {}
            }
            score = 0
            for crit, peso in self.ranking_config.pesos.items():
                valor = p.get(crit, 0)
                if crit == 'concorrencia':
                    valor = 1 - valor
                detalhes['detalhes'][crit] = {'valor': valor, 'peso': peso, 'parcial': valor * peso}
                score += valor * peso
            detalhes['score'] = score
            explicacoes.append(detalhes)
        return explicacoes 