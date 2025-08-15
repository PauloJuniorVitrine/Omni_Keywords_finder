"""
Testes Unitários - Etapa Validação

Testes para a etapa de validação de keywords com Google Keyword Planner.

Tracing ID: TEST_ETAPA_VALIDACAO_001_20250127
Versão: 1.0
Autor: IA-Cursor
Execução: Via GitHub Actions (não local)
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Dict, Any

from infrastructure.orchestrator.etapas.etapa_validacao import (
    EtapaValidacao,
    ValidacaoResult
)
from domain.models import Keyword


class TestEtapaValidacao:
    """Testes para a etapa de validação"""
    
    @pytest.fixture
    def config_validacao(self):
        """Configuração mock baseada no comportamento real"""
        return {
            'usar_google_keyword_planner': True,
            'min_volume_busca': 100,
            'max_cpc': 5.0,
            'min_concorrencia': 0.1,
            'max_concorrencia': 0.9,
            'timeout_validacao': 30,
            'max_retries': 3,
            'delay_entre_requests': 1.0
        }
    
    @pytest.fixture
    def mock_validadores(self):
        """Validadores mock baseados no comportamento real"""
        validadores = {}
        
        # Mock Google Keyword Planner Validator
        mock_google_planner = Mock()
        mock_google_planner.validar_keywords = AsyncMock(return_value={
            'keywords_validas': [
                Keyword(termo="python tutorial", volume_busca=1000, cpc=1.5, concorrencia=0.7),
                Keyword(termo="javascript guide", volume_busca=800, cpc=1.2, concorrencia=0.6)
            ],
            'keywords_rejeitadas': [
                Keyword(termo="low volume", volume_busca=50, cpc=0.5, concorrencia=0.3)
            ],
            'metricas': {
                'total_validadas': 2,
                'total_rejeitadas': 1,
                'taxa_aprovacao': 0.67
            }
        })
        validadores['google_keyword_planner'] = mock_google_planner
        
        return validadores
    
    @pytest.fixture
    def etapa_validacao(self, config_validacao, mock_validadores):
        """Etapa de validação com mocks configurados"""
        with patch('infrastructure.orchestrator.etapas.etapa_validacao.EtapaValidacao._inicializar_validadores', return_value=mock_validadores):
            return EtapaValidacao(config_validacao)
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("keywords_coletadas,expected_validas", [
        (["python tutorial", "javascript guide"], 2),
        (["low volume", "high volume"], 1),
        (["python", "java", "c++"], 3),
        ([], 0),
    ])
    async def test_executar_validacao_sucesso(self, etapa_validacao, keywords_coletadas, expected_validas):
        """Testa execução bem-sucedida da validação"""
        # Act
        resultado = await etapa_validacao.executar(keywords_coletadas, "tecnologia")
        
        # Assert
        assert isinstance(resultado, ValidacaoResult)
        assert resultado.total_keywords_validas >= expected_validas
        assert len(resultado.keywords_validadas) >= expected_validas
        assert resultado.tempo_execucao > 0
        assert resultado.metricas_validacao['taxa_aprovacao'] > 0
        assert resultado.metadados['nicho'] == "tecnologia"
        
        # Verificar se keywords validadas são objetos Keyword
        for keyword in resultado.keywords_validadas:
            assert isinstance(keyword, Keyword)
            assert keyword.volume_busca >= 100  # Min volume configurado
            assert keyword.cpc <= 5.0  # Max CPC configurado
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("nicho", [
        "tecnologia",
        "saude", 
        "financas",
        "educacao"
    ])
    async def test_executar_validacao_diferentes_nichos(self, etapa_validacao, nicho):
        """Testa validação para diferentes nichos"""
        # Arrange
        keywords_coletadas = ["python tutorial", "javascript guide"]
        
        # Act
        resultado = await etapa_validacao.executar(keywords_coletadas, nicho)
        
        # Assert
        assert resultado.total_keywords_validas > 0
        assert resultado.metadados['nicho'] == nicho
        assert resultado.metricas_validacao['total_validadas'] > 0
    
    @pytest.mark.asyncio
    async def test_executar_validacao_com_erro_validador(self, etapa_validacao):
        """Testa validação quando um validador falha"""
        # Arrange
        etapa_validacao.validadores['google_keyword_planner'].validar_keywords.side_effect = Exception("API Error")
        
        # Act
        resultado = await etapa_validacao.executar(["python tutorial"], "tecnologia")
        
        # Assert
        assert resultado.total_keywords_validas == 0
        assert len(resultado.keywords_validadas) == 0
        assert resultado.metricas_validacao['total_validadas'] == 0
        assert resultado.metricas_validacao['total_rejeitadas'] == 0
    
    @pytest.mark.parametrize("keyword,config,expected_valida", [
        (Keyword(termo="python", volume_busca=1000, cpc=1.5, concorrencia=0.7), {}, True),
        (Keyword(termo="python", volume_busca=50, cpc=1.5, concorrencia=0.7), {}, False),  # Volume baixo
        (Keyword(termo="python", volume_busca=1000, cpc=10.0, concorrencia=0.7), {}, False),  # CPC alto
        (Keyword(termo="python", volume_busca=1000, cpc=1.5, concorrencia=0.05), {}, False),  # Concorrência baixa
        (Keyword(termo="python", volume_busca=1000, cpc=1.5, concorrencia=0.95), {}, False),  # Concorrência alta
    ])
    def test_aplicar_criterios_validacao(self, etapa_validacao, keyword, config, expected_valida):
        """Testa aplicação de critérios de validação"""
        # Act
        valida = etapa_validacao._aplicar_criterios_validacao(keyword, config)
        
        # Assert
        assert valida == expected_valida
    
    @pytest.mark.parametrize("keywords,expected_filtradas", [
        ([
            Keyword(termo="python", volume_busca=1000, cpc=1.5, concorrencia=0.7),
            Keyword(termo="javascript", volume_busca=800, cpc=1.2, concorrencia=0.6)
        ], 2),  # Todas válidas
        ([
            Keyword(termo="python", volume_busca=50, cpc=1.5, concorrencia=0.7),
            Keyword(termo="javascript", volume_busca=800, cpc=1.2, concorrencia=0.6)
        ], 1),  # Uma inválida (volume baixo)
        ([
            Keyword(termo="python", volume_busca=1000, cpc=10.0, concorrencia=0.7),
            Keyword(termo="javascript", volume_busca=800, cpc=1.2, concorrencia=0.6)
        ], 1),  # Uma inválida (CPC alto)
    ])
    def test_filtrar_keywords_por_criterios(self, etapa_validacao, keywords, expected_filtradas):
        """Testa filtragem de keywords por critérios"""
        # Act
        keywords_filtradas = etapa_validacao._filtrar_keywords_por_criterios(keywords)
        
        # Assert
        assert len(keywords_filtradas) == expected_filtradas
    
    def test_calcular_metricas_validacao(self, etapa_validacao):
        """Testa cálculo de métricas de validação"""
        # Arrange
        keywords_validadas = [
            Keyword(termo="python", volume_busca=1000, cpc=1.5, concorrencia=0.7),
            Keyword(termo="javascript", volume_busca=800, cpc=1.2, concorrencia=0.6)
        ]
        keywords_rejeitadas = [
            Keyword(termo="low volume", volume_busca=50, cpc=0.5, concorrencia=0.3)
        ]
        tempo_execucao = 2.5
        
        # Act
        metricas = etapa_validacao._calcular_metricas_validacao(
            keywords_validadas, keywords_rejeitadas, tempo_execucao
        )
        
        # Assert
        assert metricas['total_validadas'] == 2
        assert metricas['total_rejeitadas'] == 1
        assert metricas['taxa_aprovacao'] == 2/3
        assert metricas['tempo_execucao'] == 2.5
        assert metricas['volume_medio'] == 900  # (1000 + 800) / 2
        assert metricas['cpc_medio'] == 1.35  # (1.5 + 1.2) / 2
        assert metricas['concorrencia_media'] == 0.65  # (0.7 + 0.6) / 2
    
    def test_obter_status(self, etapa_validacao):
        """Testa obtenção de status da etapa"""
        # Act
        status = etapa_validacao.obter_status()
        
        # Assert
        assert "validadores_ativos" in status
        assert "validadores_disponiveis" in status
        assert "configuracao" in status
        assert status["validadores_ativos"] == 1  # 1 validador configurado
        assert len(status["validadores_disponiveis"]) == 1
    
    @pytest.mark.asyncio
    async def test_executar_validacao_keywords_vazias(self, etapa_validacao):
        """Testa validação com lista de keywords vazia"""
        # Act
        resultado = await etapa_validacao.executar([], "tecnologia")
        
        # Assert
        assert resultado.total_keywords_validas == 0
        assert len(resultado.keywords_validadas) == 0
        assert resultado.metricas_validacao['total_validadas'] == 0
        assert resultado.metricas_validacao['total_rejeitadas'] == 0
        assert resultado.metricas_validacao['taxa_aprovacao'] == 0
    
    @pytest.mark.asyncio
    async def test_executar_validacao_metadados_completos(self, etapa_validacao):
        """Testa se metadados estão completos no resultado"""
        # Act
        resultado = await etapa_validacao.executar(["python tutorial"], "tecnologia")
        
        # Assert
        assert "nicho" in resultado.metadados
        assert "config_utilizada" in resultado.metadados
        assert resultado.metadados["nicho"] == "tecnologia"
        assert resultado.metadados["config_utilizada"] == etapa_validacao.config


class TestEtapaValidacaoEdgeCases:
    """Testes para casos extremos da etapa de validação"""
    
    @pytest.fixture
    def config_validacao_edge(self):
        """Configuração para testes de edge cases"""
        return {
            'usar_google_keyword_planner': False,
            'min_volume_busca': 0,
            'max_cpc': float('inf'),
            'min_concorrencia': 0,
            'max_concorrencia': 1,
            'timeout_validacao': 1,
            'max_retries': 1,
            'delay_entre_requests': 0.1
        }
    
    @pytest.fixture
    def etapa_validacao_edge(self, config_validacao_edge):
        """Etapa de validação para edge cases"""
        return EtapaValidacao(config_validacao_edge)
    
    @pytest.mark.asyncio
    async def test_executar_validacao_sem_validadores(self, etapa_validacao_edge):
        """Testa validação sem validadores configurados"""
        # Act
        resultado = await etapa_validacao_edge.executar(["python tutorial"], "tecnologia")
        
        # Assert
        assert resultado.total_keywords_validas == 0
        assert len(resultado.keywords_validadas) == 0
    
    @pytest.mark.parametrize("keyword_extrema", [
        Keyword(termo="", volume_busca=0, cpc=0, concorrencia=0),
        Keyword(termo="python", volume_busca=float('inf'), cpc=float('inf'), concorrencia=1),
        Keyword(termo="python", volume_busca=-1, cpc=-1, concorrencia=-1),
        Keyword(termo="python", volume_busca=1000, cpc=1.5, concorrencia=0.7),
    ])
    def test_criterios_validacao_keywords_extremas(self, etapa_validacao_edge, keyword_extrema):
        """Testa critérios com keywords extremas"""
        # Act
        valida = etapa_validacao_edge._aplicar_criterios_validacao(keyword_extrema, {})
        
        # Assert
        if keyword_extrema.termo == "python" and keyword_extrema.volume_busca == 1000:
            assert valida is True
        else:
            assert valida is False
    
    @pytest.mark.asyncio
    async def test_executar_validacao_nicho_vazio(self, etapa_validacao_edge):
        """Testa validação com nicho vazio"""
        # Act
        resultado = await etapa_validacao_edge.executar(["python tutorial"], "")
        
        # Assert
        assert resultado.metadados["nicho"] == ""
    
    def test_calcular_metricas_sem_keywords(self, etapa_validacao_edge):
        """Testa cálculo de métricas sem keywords"""
        # Act
        metricas = etapa_validacao_edge._calcular_metricas_validacao([], [], 0)
        
        # Assert
        assert metricas['total_validadas'] == 0
        assert metricas['total_rejeitadas'] == 0
        assert metricas['taxa_aprovacao'] == 0
        assert metricas['volume_medio'] == 0
        assert metricas['cpc_medio'] == 0
        assert metricas['concorrencia_media'] == 0


class TestEtapaValidacaoPerformance:
    """Testes de performance para a etapa de validação"""
    
    @pytest.fixture
    def config_validacao_perf(self):
        """Configuração para testes de performance"""
        return {
            'usar_google_keyword_planner': True,
            'min_volume_busca': 100,
            'max_cpc': 5.0,
            'min_concorrencia': 0.1,
            'max_concorrencia': 0.9,
            'timeout_validacao': 5,
            'max_retries': 1,
            'delay_entre_requests': 0.1
        }
    
    @pytest.fixture
    def etapa_validacao_perf(self, config_validacao_perf):
        """Etapa de validação para testes de performance"""
        with patch('infrastructure.orchestrator.etapas.etapa_validacao.EtapaValidacao._inicializar_validadores') as mock_init:
            mock_init.return_value = {
                'google_keyword_planner': Mock()
            }
            return EtapaValidacao(config_validacao_perf)
    
    @pytest.mark.asyncio
    async def test_executar_validacao_tempo_resposta(self, etapa_validacao_perf):
        """Testa tempo de resposta da validação"""
        # Arrange
        inicio = time.time()
        
        # Act
        resultado = await etapa_validacao_perf.executar(["python tutorial"], "tecnologia")
        
        # Assert
        tempo_execucao = time.time() - inicio
        assert tempo_execucao < 10.0  # Deve ser rápido em testes
        assert resultado.tempo_execucao > 0
        assert resultado.tempo_execucao < 10.0
    
    @pytest.mark.asyncio
    async def test_executar_validacao_muitas_keywords(self, etapa_validacao_perf):
        """Testa validação com muitas keywords"""
        # Arrange
        keywords_coletadas = [f"keyword_{i}" for i in range(100)]
        
        # Act
        resultado = await etapa_validacao_perf.executar(keywords_coletadas, "tecnologia")
        
        # Assert
        assert resultado.metadados["keywords_coletadas"] == keywords_coletadas
        assert resultado.tempo_execucao > 0
    
    def test_filtrar_keywords_por_criterios_performance(self, etapa_validacao_perf):
        """Testa performance da filtragem por critérios"""
        # Arrange
        keywords = [
            Keyword(termo=f"keyword_{i}", volume_busca=1000, cpc=1.5, concorrencia=0.7)
            for i in range(1000)
        ]
        
        # Act
        inicio = time.time()
        keywords_filtradas = etapa_validacao_perf._filtrar_keywords_por_criterios(keywords)
        tempo_execucao = time.time() - inicio
        
        # Assert
        assert tempo_execucao < 1.0  # Deve ser rápido
        assert len(keywords_filtradas) == 1000  # Todas devem passar


class TestEtapaValidacaoIntegracao:
    """Testes de integração para a etapa de validação"""
    
    @pytest.fixture
    def etapa_validacao_real(self):
        """Etapa de validação com configuração real"""
        return EtapaValidacao({})
    
    def test_inicializacao_validadores_real(self, etapa_validacao_real):
        """Testa inicialização real dos validadores"""
        # Act
        status = etapa_validacao_real.obter_status()
        
        # Assert
        assert "validadores_ativos" in status
        assert "validadores_disponiveis" in status
        assert "configuracao" in status
    
    @pytest.mark.parametrize("config_diferentes", [
        {'min_volume_busca': 50, 'max_cpc': 10.0},
        {'min_volume_busca': 1000, 'max_cpc': 1.0},
        {'min_concorrencia': 0.5, 'max_concorrencia': 0.8},
        {'timeout_validacao': 60, 'max_retries': 5},
    ])
    def test_validacao_com_configuracoes_diferentes(self, config_diferentes):
        """Testa validação com diferentes configurações"""
        # Arrange
        etapa = EtapaValidacao(config_diferentes)
        
        # Act
        status = etapa.obter_status()
        
        # Assert
        assert status["configuracao"] == config_diferentes 