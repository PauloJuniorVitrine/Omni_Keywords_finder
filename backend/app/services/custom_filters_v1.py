"""
Módulo: custom_filters_v1
Permite configuração e aplicação de filtros customizados para coleta de palavras-chave.
"""
from typing import List, Dict, Any

class CustomFilters:
    """
    Classe para definir e aplicar filtros customizados na coleta de palavras-chave.
    """
    def __init__(self, idioma: str = 'pt-BR', localizacao: str = 'BR', volume_minimo: int = 0, outros: Dict[str, Any] = None):
        self.idioma = idioma
        self.localizacao = localizacao
        self.volume_minimo = volume_minimo
        self.outros = outros or {}

    def aplicar(self, palavras_chave: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filtra a lista de palavras-chave conforme os parâmetros definidos.
        """
        filtradas = [
            p for p in palavras_chave
            if p.get('idioma', self.idioma) == self.idioma
            and p.get('localizacao', self.localizacao) == self.localizacao
            and p.get('volume', 0) >= self.volume_minimo
        ]
        # Aplicar outros filtros customizados se necessário
        for chave, valor in self.outros.items():
            filtradas = [p for p in filtradas if p.get(chave) == valor]
        return filtradas 