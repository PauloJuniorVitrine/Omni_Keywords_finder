"""
Módulo de parsing de mídia para integração com Instagram.
Responsável por extrair informações de posts, stories, reels, etc.
Refatorado a partir de infrastructure/coleta/instagram.py (Enterprise Audit IMP-001).
"""
from typing import Dict, Any

def parse_post(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extrai informações relevantes de um post do Instagram.
    Args:
        data (dict): Dados brutos do post
    Returns:
        dict: Dados normalizados do post
    """
    assert isinstance(data, dict), "data deve ser um dicionário"
    # TODO: Implementar parsing real conforme estrutura do Instagram
    # Placeholder para simulação
    return {
        "id": data.get("id", "mock_id"),
        "media_url": data.get("media_url", "mock_url"),
        "caption": data.get("caption", ""),
        "timestamp": data.get("timestamp", "2024-01-01T00:00:00Z")
    } 