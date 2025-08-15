"""
Testes Unitários - Etapa Preenchimento

Testes para a etapa de preenchimento de prompts.

Tracing ID: TEST_ETAPA_PREENCHIMENTO_001_20250127
Versão: 1.0
Autor: IA-Cursor
Execução: Via GitHub Actions (não local)
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Dict, Any

from infrastructure.orchestrator.etapas.etapa_preenchimento import (
    EtapaPreenchimento,
    PreenchimentoResult
)
from domain.models import Keyword, IntencaoBusca


class TestEtapaPreenchimento:
    """Testes para a etapa de preenchimento"""
    
    @pytest.fixture
    def config_preenchimento(self):
        """Configuração mock baseada no comportamento real"""
        return {
            'model': 'gpt-4',
            'max_tokens': 2000,
            'temperature': 0.7,
            'timeout_preenchimento': 30,
            'max_retries': 3
        }
    
    @pytest.fixture
    def etapa_preenchimento(self, config_preenchimento):
        """Etapa de preenchimento com mocks configurados"""
        with patch('infrastructure.orchestrator.etapas.etapa_preenchimento.GeradorPrompt'), \
             patch('infrastructure.orchestrator.etapas.etapa_preenchimento.PromptTemplate'):
            return EtapaPreenchimento(config_preenchimento)
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("keywords_processadas,expected_prompts", [
        ([Keyword(termo="python tutorial", volume_busca=1000, cpc=1.5, concorrencia=0.7, intencao=IntencaoBusca.INFORMACIONAL)], 1),
        ([Keyword(termo="python", volume_busca=800, cpc=1.2, concorrencia=0.6, intencao=IntencaoBusca.INFORMACIONAL), Keyword(termo="javascript", volume_busca=600, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL)], 2),
        ([], 0),
    ])
    async def test_executar_preenchimento_sucesso(self, etapa_preenchimento, keywords_processadas, expected_prompts):
        """Testa execução bem-sucedida do preenchimento"""
        # Act
        resultado = await etapa_preenchimento.executar(keywords_processadas, "tecnologia")
        
        # Assert
        assert isinstance(resultado, PreenchimentoResult)
        assert resultado.total_prompts >= expected_prompts
        assert len(resultado.prompts_gerados) >= expected_prompts
        assert resultado.tempo_execucao > 0
        assert resultado.metadados['nicho'] == "tecnologia"
    
    def test_obter_status(self, etapa_preenchimento):
        """Testa obtenção de status da etapa"""
        # Act
        status = etapa_preenchimento.obter_status()
        
        # Assert
        assert "model" in status
        assert "configuracao" in status
        assert status["model"] == "gpt-4" 