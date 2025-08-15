"""
Testes Unitários - Etapa Coleta

Testes para a etapa de coleta de keywords de múltiplas fontes.

Tracing ID: TEST_ETAPA_COLETA_001_20250127
Versão: 1.0
Autor: IA-Cursor
Execução: Via GitHub Actions (não local)
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Dict, Any

from infrastructure.orchestrator.etapas.etapa_coleta import (
    EtapaColeta,
    ColetaResult
)
from domain.models import Keyword


class TestEtapaColeta:
    """Testes para a etapa de coleta"""
    
    @pytest.fixture
    def config_coleta(self):
        """Configuração mock baseada no comportamento real"""
        return {
            'usar_google_keyword_planner': True,
            'usar_google_suggest': True,
            'usar_google_trends': True,
            'delay_entre_requests': 1.0,
            'delays_por_coletor': {
                'google_keyword_planner': 2.0,
                'google_suggest': 0.5,
                'google_trends': 1.5
            },
            'min_comprimento_keyword': 3,
            'keywords_semente': ['python tutorial', 'javascript guide']
        }
    
    @pytest.fixture
    def mock_coletores(self):
        """Coletores mock baseados no comportamento real"""
        coletores = {}
        
        # Mock Google Keyword Planner
        mock_google_planner = Mock()
        mock_google_planner.coletar_keywords = AsyncMock(return_value=[
            Keyword(termo="python tutorial", volume_busca=1000, cpc=1.5),
            Keyword(termo="python course", volume_busca=800, cpc=1.2)
        ])
        coletores['google_keyword_planner'] = mock_google_planner
        
        # Mock Google Suggest
        mock_google_suggest = Mock()
        mock_google_suggest.coletar_keywords = AsyncMock(return_value=[
            Keyword(termo="python tutorial", volume_busca=0, cpc=0.0),
            Keyword(termo="python for beginners", volume_busca=0, cpc=0.0)
        ])
        coletores['google_suggest'] = mock_google_suggest
        
        # Mock Google Trends
        mock_google_trends = Mock()
        mock_google_trends.coletar_keywords = AsyncMock(return_value=[
            Keyword(termo="python programming", volume_busca=0, cpc=0.0),
            Keyword(termo="python development", volume_busca=0, cpc=0.0)
        ])
        coletores['google_trends'] = mock_google_trends
        
        return coletores
    
    @pytest.fixture
    def etapa_coleta(self, config_coleta, mock_coletores):
        """Etapa de coleta com mocks configurados"""
        with patch('infrastructure.orchestrator.etapas.etapa_coleta.EtapaColeta._inicializar_coletores', return_value=mock_coletores):
            return EtapaColeta(config_coleta)
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("nicho,keywords_semente,expected_min_keywords", [
        ("tecnologia", None, 3),  # Usa keywords_semente do config
        ("saude", ["medicina natural"], 1),
        ("financas", ["investimentos"], 1),
        ("educacao", ["cursos online"], 1),
    ])
    async def test_executar_coleta_sucesso(self, etapa_coleta, nicho, keywords_semente, expected_min_keywords):
        """Testa execução bem-sucedida da coleta"""
        # Act
        resultado = await etapa_coleta.executar(nicho, keywords_semente)
        
        # Assert
        assert isinstance(resultado, ColetaResult)
        assert resultado.total_keywords >= expected_min_keywords
        assert len(resultado.keywords_coletadas) >= expected_min_keywords
        assert resultado.tempo_execucao > 0
        assert len(resultado.fontes_utilizadas) > 0
        assert resultado.metadados['nicho'] == nicho
        
        # Verificar se keywords são strings válidas
        for keyword in resultado.keywords_coletadas:
            assert isinstance(keyword, str)
            assert len(keyword.strip()) >= 3
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("nicho", [
        "tecnologia",
        "saude", 
        "financas",
        "educacao"
    ])
    async def test_executar_coleta_sem_keywords_semente(self, etapa_coleta, nicho):
        """Testa coleta sem keywords semente (usa config)"""
        # Act
        resultado = await etapa_coleta.executar(nicho)
        
        # Assert
        assert resultado.total_keywords > 0
        assert len(resultado.keywords_coletadas) > 0
        assert resultado.metadados['keywords_semente'] == ['python tutorial', 'javascript guide']
    
    @pytest.mark.asyncio
    async def test_executar_coleta_com_erro_coletor(self, etapa_coleta):
        """Testa coleta quando um coletor falha"""
        # Arrange
        etapa_coleta.coletores['google_keyword_planner'].coletar_keywords.side_effect = Exception("API Error")
        
        # Act
        resultado = await etapa_coleta.executar("tecnologia")
        
        # Assert
        assert resultado.total_keywords > 0  # Outros coletores ainda funcionam
        assert len(resultado.keywords_coletadas) > 0
        assert 'google_suggest' in resultado.fontes_utilizadas
        assert 'google_trends' in resultado.fontes_utilizadas
    
    @pytest.mark.parametrize("keywords,expected_filtradas", [
        (["python", "javascript", "java"], ["python", "javascript", "java"]),  # Todas válidas
        (["py", "js", "java"], ["java"]),  # py e js muito curtos
        (["python<script>", "javascript", "java"], ["javascript", "java"]),  # python<script> tem caracteres inválidos
        (["", "   ", "python"], ["python"]),  # Vazias ou só espaços
        (["a" * 1000, "python"], ["python"]),  # Muito longa
    ])
    def test_aplicar_filtros_qualidade(self, etapa_coleta, keywords, expected_filtradas):
        """Testa aplicação de filtros de qualidade"""
        # Act
        keywords_filtradas = etapa_coleta._aplicar_filtros_qualidade(keywords, "tecnologia")
        
        # Assert
        assert len(keywords_filtradas) == len(expected_filtradas)
        for keyword in keywords_filtradas:
            assert keyword in expected_filtradas
    
    @pytest.mark.parametrize("keyword,expected", [
        ("python tutorial", True),
        ("javascript guide", True),
        ("python<script>", False),
        ("javascript&", False),
        ("java'", False),
        ("c++", True),  # + é válido
        ("c#", True),   # # é válido
    ])
    def test_validar_caracteres_keyword(self, etapa_coleta, keyword, expected):
        """Testa validação de caracteres em keywords"""
        # Act
        resultado = etapa_coleta._validar_caracteres_keyword(keyword)
        
        # Assert
        assert resultado == expected
    
    @pytest.mark.parametrize("keyword,nicho,expected", [
        ("python tutorial", "tecnologia", True),
        ("medicina natural", "saude", True),
        ("investimentos", "financas", True),
        ("cursos online", "educacao", True),
        ("python tutorial", "saude", False),  # Não relevante para saúde
        ("medicina natural", "tecnologia", False),  # Não relevante para tecnologia
    ])
    def test_validar_relevancia_nicho(self, etapa_coleta, keyword, nicho, expected):
        """Testa validação de relevância para nicho"""
        # Act
        resultado = etapa_coleta._validar_relevancia_nicho(keyword, nicho)
        
        # Assert
        assert resultado == expected
    
    def test_aplicar_rate_limiting(self, etapa_coleta):
        """Testa aplicação de rate limiting"""
        # Arrange
        inicio = time.time()
        
        # Act
        etapa_coleta._aplicar_rate_limiting('google_keyword_planner')
        
        # Assert
        tempo_decorrido = time.time() - inicio
        assert tempo_decorrido >= 2.0  # Delay específico do Google Keyword Planner
    
    def test_obter_status(self, etapa_coleta):
        """Testa obtenção de status da etapa"""
        # Act
        status = etapa_coleta.obter_status()
        
        # Assert
        assert "coletores_ativos" in status
        assert "coletores_disponiveis" in status
        assert "configuracao" in status
        assert status["coletores_ativos"] == 3  # 3 coletores configurados
        assert len(status["coletores_disponiveis"]) == 3
    
    @pytest.mark.asyncio
    async def test_executar_coleta_todos_coletores_falham(self, etapa_coleta):
        """Testa cenário onde todos os coletores falham"""
        # Arrange
        for coletor in etapa_coleta.coletores.values():
            coletor.coletar_keywords.side_effect = Exception("All collectors failed")
        
        # Act
        resultado = await etapa_coleta.executar("tecnologia")
        
        # Assert
        assert resultado.total_keywords == 0
        assert len(resultado.keywords_coletadas) == 0
        assert len(resultado.fontes_utilizadas) == 0
        assert resultado.tempo_execucao > 0
    
    @pytest.mark.asyncio
    async def test_executar_coleta_remove_duplicatas(self, etapa_coleta):
        """Testa remoção de duplicatas na coleta"""
        # Arrange
        # Configurar coletores para retornar keywords duplicadas
        etapa_coleta.coletores['google_keyword_planner'].coletar_keywords.return_value = [
            Keyword(termo="python tutorial", volume_busca=1000, cpc=1.5),
            Keyword(termo="python tutorial", volume_busca=1000, cpc=1.5),  # Duplicata
        ]
        etapa_coleta.coletores['google_suggest'].coletar_keywords.return_value = [
            Keyword(termo="python tutorial", volume_busca=0, cpc=0.0),  # Duplicata
            Keyword(termo="python for beginners", volume_busca=0, cpc=0.0),
        ]
        
        # Act
        resultado = await etapa_coleta.executar("tecnologia")
        
        # Assert
        keywords_unicas = set(resultado.keywords_coletadas)
        assert len(keywords_unicas) == len(resultado.keywords_coletadas)  # Sem duplicatas
        assert "python tutorial" in resultado.keywords_coletadas
        assert "python for beginners" in resultado.keywords_coletadas
    
    @pytest.mark.asyncio
    async def test_executar_coleta_metadados_completos(self, etapa_coleta):
        """Testa se metadados estão completos no resultado"""
        # Act
        resultado = await etapa_coleta.executar("tecnologia", ["python"])
        
        # Assert
        assert "nicho" in resultado.metadados
        assert "keywords_semente" in resultado.metadados
        assert "config_utilizada" in resultado.metadados
        assert resultado.metadados["nicho"] == "tecnologia"
        assert resultado.metadados["keywords_semente"] == ["python"]
        assert resultado.metadados["config_utilizada"] == etapa_coleta.config


class TestEtapaColetaEdgeCases:
    """Testes para casos extremos da etapa de coleta"""
    
    @pytest.fixture
    def config_coleta_edge(self):
        """Configuração para testes de edge cases"""
        return {
            'usar_google_keyword_planner': False,
            'usar_google_suggest': False,
            'usar_google_trends': False,
            'min_comprimento_keyword': 1,
            'keywords_semente': []
        }
    
    @pytest.fixture
    def etapa_coleta_edge(self, config_coleta_edge):
        """Etapa de coleta para edge cases"""
        return EtapaColeta(config_coleta_edge)
    
    @pytest.mark.asyncio
    async def test_executar_coleta_sem_coletores(self, etapa_coleta_edge):
        """Testa coleta sem coletores configurados"""
        # Act
        resultado = await etapa_coleta_edge.executar("tecnologia")
        
        # Assert
        assert resultado.total_keywords == 0
        assert len(resultado.keywords_coletadas) == 0
        assert len(resultado.fontes_utilizadas) == 0
    
    @pytest.mark.parametrize("keyword_extrema", [
        "a" * 10000,  # Muito longa
        "",  # Vazia
        "   ",  # Só espaços
        "a",  # Muito curta
        "python<script>alert('xss')</script>",  # Caracteres perigosos
        "python\njavascript",  # Com quebra de linha
        "python\tjavascript",  # Com tab
    ])
    def test_filtros_qualidade_keywords_extremas(self, etapa_coleta_edge, keyword_extrema):
        """Testa filtros com keywords extremas"""
        # Act
        keywords_filtradas = etapa_coleta_edge._aplicar_filtros_qualidade([keyword_extrema], "tecnologia")
        
        # Assert
        assert len(keywords_filtradas) == 0  # Todas devem ser filtradas
    
    def test_validar_caracteres_keywords_extremas(self, etapa_coleta_edge):
        """Testa validação de caracteres com keywords extremas"""
        keywords_extremas = [
            "python<script>",
            "javascript&",
            "java'",
            "c++<",
            "c#>",
            "python\"",
            "javascript\\",
            "java/",
        ]
        
        for keyword in keywords_extremas:
            assert not etapa_coleta_edge._validar_caracteres_keyword(keyword)
    
    @pytest.mark.asyncio
    async def test_executar_coleta_nicho_vazio(self, etapa_coleta_edge):
        """Testa coleta com nicho vazio"""
        # Act
        resultado = await etapa_coleta_edge.executar("")
        
        # Assert
        assert resultado.total_keywords == 0
        assert resultado.metadados["nicho"] == ""
    
    @pytest.mark.asyncio
    async def test_executar_coleta_keywords_semente_vazias(self, etapa_coleta_edge):
        """Testa coleta com keywords semente vazias"""
        # Act
        resultado = await etapa_coleta_edge.executar("tecnologia", [])
        
        # Assert
        assert resultado.total_keywords == 0
        assert resultado.metadados["keywords_semente"] == []


class TestEtapaColetaPerformance:
    """Testes de performance para a etapa de coleta"""
    
    @pytest.fixture
    def config_coleta_perf(self):
        """Configuração para testes de performance"""
        return {
            'usar_google_keyword_planner': True,
            'usar_google_suggest': True,
            'usar_google_trends': True,
            'delay_entre_requests': 0.1,  # Delay baixo para testes
            'min_comprimento_keyword': 3,
            'keywords_semente': ['python']
        }
    
    @pytest.fixture
    def etapa_coleta_perf(self, config_coleta_perf):
        """Etapa de coleta para testes de performance"""
        with patch('infrastructure.orchestrator.etapas.etapa_coleta.EtapaColeta._inicializar_coletores') as mock_init:
            mock_init.return_value = {
                'google_keyword_planner': Mock(),
                'google_suggest': Mock(),
                'google_trends': Mock()
            }
            return EtapaColeta(config_coleta_perf)
    
    @pytest.mark.asyncio
    async def test_executar_coleta_tempo_resposta(self, etapa_coleta_perf):
        """Testa tempo de resposta da coleta"""
        # Arrange
        inicio = time.time()
        
        # Act
        resultado = await etapa_coleta_perf.executar("tecnologia")
        
        # Assert
        tempo_execucao = time.time() - inicio
        assert tempo_execucao < 5.0  # Deve ser rápido em testes
        assert resultado.tempo_execucao > 0
        assert resultado.tempo_execucao < 5.0
    
    @pytest.mark.asyncio
    async def test_executar_coleta_muitas_keywords_semente(self, etapa_coleta_perf):
        """Testa coleta com muitas keywords semente"""
        # Arrange
        keywords_semente = [f"keyword_{i}" for i in range(100)]
        
        # Act
        resultado = await etapa_coleta_perf.executar("tecnologia", keywords_semente)
        
        # Assert
        assert resultado.metadados["keywords_semente"] == keywords_semente
        assert resultado.tempo_execucao > 0 