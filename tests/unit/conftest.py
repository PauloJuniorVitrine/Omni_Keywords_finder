import os
import sys
import pytest
from unittest.mock import MagicMock, AsyncMock
from typing import Dict, List, Optional, Any
from domain.models import Keyword, Cluster, IntencaoBusca
from datetime import datetime

# Adiciona o diretório raiz do projeto ao PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

@pytest.fixture
def keywords_reais():
    """Lista de keywords reais do domínio para uso em múltiplos testes."""
    return [
        Keyword(termo="marketing digital", volume_busca=1200, cpc=2.5, concorrencia=0.7, intencao=IntencaoBusca.COMERCIAL, fonte="google_ads", data_coleta=datetime.utcnow()),
        Keyword(termo="como criar blog wordpress", volume_busca=900, cpc=1.8, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL, fonte="google_ads", data_coleta=datetime.utcnow()),
        Keyword(termo="ferramentas de automação", volume_busca=700, cpc=3.2, concorrencia=0.8, intencao=IntencaoBusca.TRANSACIONAL, fonte="google_ads", data_coleta=datetime.utcnow())
    ]

@pytest.fixture
def clusters_reais(keywords_reais):
    """Clusters reais de keywords para uso em testes."""
    return [
        Cluster(
            id="cluster1",
            keywords=keywords_reais,
            similaridade_media=0.82,
            fase_funil="descoberta",
            categoria="Marketing",
            blog_dominio="meublog.com",
            data_criacao=datetime.utcnow(),
            status_geracao="pendente"
        )
    ]

@pytest.fixture
def config_sistema():
    """Configuração de sistema para testes."""
    return {
        "env": "test",
        "feature_flags": {"ab_testing": True, "monitoramento": True},
        "max_keywords": 1000,
        "timeout": 30
    }

@pytest.fixture
def usuario_teste():
    """Usuário de teste padrão."""
    return {
        "id": "user_001",
        "nome": "Usuário Teste",
        "email": "teste@exemplo.com",
        "roles": ["admin", "analista"]
    } 