"""
Testes Unitários - Etapa Processamento

Testes para a etapa de processamento e enriquecimento de keywords.

Tracing ID: TEST_ETAPA_PROCESSAMENTO_001_20250127
Versão: 1.0
Autor: IA-Cursor
Execução: Via GitHub Actions (não local)
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Dict, Any

from infrastructure.orchestrator.etapas.etapa_processamento import (
    EtapaProcessamento,
    ProcessamentoResult
)
from domain.models import Keyword


class TestEtapaProcessamento:
    """Testes para a etapa de processamento"""
    
    @pytest.fixture
    def config_processamento(self):
        """Configuração mock baseada no comportamento real"""
        return {
            'usar_ml': True,
            'batch_size': 1000,
            'timeout_processamento': 30,
            'max_retries': 3
        }
    
    @pytest.fixture
    def etapa_processamento(self, config_processamento):
        """Etapa de processamento com mocks configurados"""
        with patch('infrastructure.orchestrator.etapas.etapa_processamento.MLProcessor'), \
             patch('infrastructure.orchestrator.etapas.etapa_processamento.NormalizadorKeywords'), \
             patch('infrastructure.orchestrator.etapas.etapa_processamento.EnriquecidorKeywords'), \
             patch('infrastructure.orchestrator.etapas.etapa_processamento.ValidadorKeywords'):
            return EtapaProcessamento(config_processamento)
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("keywords_coletadas,expected_processadas", [
        (["python tutorial", "javascript guide"], 2),
        (["python", "java", "c++"], 3),
        ([], 0),
    ])
    async def test_executar_processamento_sucesso(self, etapa_processamento, keywords_coletadas, expected_processadas):
        """Testa execução bem-sucedida do processamento"""
        # Act
        resultado = await etapa_processamento.executar(keywords_coletadas, "tecnologia")
        
        # Assert
        assert isinstance(resultado, ProcessamentoResult)
        assert resultado.total_keywords >= expected_processadas
        assert len(resultado.keywords_processadas) >= expected_processadas
        assert resultado.tempo_execucao > 0
        assert resultado.metricas_processamento['taxa_aprovacao'] > 0
        assert resultado.metadados['nicho'] == "tecnologia"
    
    def test_converter_para_keywords(self, etapa_processamento):
        """Testa conversão de strings para objetos Keyword"""
        # Arrange
        keywords_strings = ["python tutorial", "javascript guide"]
        
        # Act
        keywords = etapa_processamento._converter_para_keywords(keywords_strings)
        
        # Assert
        assert len(keywords) == 2
        assert all(isinstance(kw, Keyword) for kw in keywords)
        assert keywords[0].termo == "python tutorial"
        assert keywords[1].termo == "javascript guide"
    
    def test_obter_status(self, etapa_processamento):
        """Testa obtenção de status da etapa"""
        # Act
        status = etapa_processamento.obter_status()
        
        # Assert
        assert "ml_processor_ativo" in status
        assert "normalizador_ativo" in status
        assert "enriquecidor_ativo" in status
        assert "validador_ativo" in status
        assert "configuracao" in status 