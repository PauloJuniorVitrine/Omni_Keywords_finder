from typing import Dict, List, Optional, Any
"""
Testes unitários para CustomFilters (custom_filters_v1.py)
"""
import pytest
from backend.app.services.custom_filters_v1 import CustomFilters

def test_aplicar_filtros_volume_minimo():
    """Testa filtro por volume mínimo de busca."""
    filtros = CustomFilters(
        idioma='pt-BR', 
        localizacao='BR', 
        volume_minimo=1000
    )
    palavras_chave = [
        {
            'termo': 'produto eletronico', 
            'idioma': 'pt-BR', 
            'localizacao': 'BR', 
            'volume': 1500,
            'cpc': 2.50,
            'concorrencia': 0.8
        },
        {
            'termo': 'consulta medica online', 
            'idioma': 'pt-BR', 
            'localizacao': 'BR', 
            'volume': 800,
            'cpc': 4.20,
            'concorrencia': 0.6
        },
        {
            'termo': 'curso de programacao', 
            'idioma': 'pt-BR', 
            'localizacao': 'BR', 
            'volume': 2500,
            'cpc': 3.10,
            'concorrencia': 0.7
        },
    ]
    resultado = filtros.aplicar(palavras_chave)
    
    # Verifica que apenas keywords com volume >= 1000 foram mantidas
    assert len(resultado) == 2
    assert resultado[0]['termo'] == 'produto eletronico'
    assert resultado[0]['volume'] == 1500
    assert resultado[1]['termo'] == 'curso de programacao'
    assert resultado[1]['volume'] == 2500

def test_aplicar_filtros_por_fonte():
    """Testa filtro por fonte de dados específica."""
    filtros = CustomFilters(
        idioma='pt-BR',
        localizacao='BR',
        outros={'fonte': 'google_ads'}
    )
    palavras_chave = [
        {
            'termo': 'marketing digital', 
            'idioma': 'pt-BR', 
            'localizacao': 'BR', 
            'volume': 2000, 
            'fonte': 'google_ads',
            'cpc': 1.80
        },
        {
            'termo': 'seo otimizacao', 
            'idioma': 'pt-BR', 
            'localizacao': 'BR', 
            'volume': 1800, 
            'fonte': 'google_trends',
            'cpc': 2.10
        },
    ]
    resultado = filtros.aplicar(palavras_chave)
    
    # Verifica que apenas keywords da fonte google_ads foram mantidas
    assert len(resultado) == 1
    assert resultado[0]['termo'] == 'marketing digital'
    assert resultado[0]['fonte'] == 'google_ads'
    assert resultado[0]['volume'] == 2000

def test_aplicar_filtros_lista_vazia():
    """Testa comportamento com lista vazia de keywords."""
    filtros = CustomFilters(
        idioma='pt-BR',
        localizacao='BR',
        volume_minimo=100
    )
    palavras_chave = []
    resultado = filtros.aplicar(palavras_chave)
    
    # Verifica que retorna lista vazia
    assert resultado == []
    assert len(resultado) == 0

def test_aplicar_filtros_multiplos_criterios():
    """Testa filtro combinando múltiplos critérios."""
    filtros = CustomFilters(
        idioma='pt-BR',
        localizacao='BR',
        volume_minimo=500,
        outros={'categoria': 'ecommerce'}
    )
    palavras_chave = [
        {
            'termo': 'loja virtual', 
            'idioma': 'pt-BR', 
            'localizacao': 'BR', 
            'volume': 1200,
            'categoria': 'ecommerce',
            'cpc': 2.80
        },
        {
            'termo': 'site institucional', 
            'idioma': 'pt-BR', 
            'localizacao': 'BR', 
            'volume': 800,
            'categoria': 'institucional',
            'cpc': 1.50
        },
        {
            'termo': 'ecommerce plataforma', 
            'idioma': 'pt-BR', 
            'localizacao': 'BR', 
            'volume': 300,
            'categoria': 'ecommerce',
            'cpc': 3.20
        },
    ]
    resultado = filtros.aplicar(palavras_chave)
    
    # Verifica que apenas keywords que atendem todos os critérios foram mantidas
    assert len(resultado) == 1
    assert resultado[0]['termo'] == 'loja virtual'
    assert resultado[0]['volume'] >= 500
    assert resultado[0]['categoria'] == 'ecommerce' 