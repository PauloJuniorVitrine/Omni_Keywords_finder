"""
Testes Unitários - Etapa Exportação

Testes para a etapa de exportação de arquivos.

Tracing ID: TEST_ETAPA_EXPORTACAO_001_20250127
Versão: 1.0
Autor: IA-Cursor
Execução: Via GitHub Actions (não local)
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Dict, Any

from infrastructure.orchestrator.etapas.etapa_exportacao import (
    EtapaExportacao,
    ExportacaoResult
)
from domain.models import Keyword, IntencaoBusca


class TestEtapaExportacao:
    """Testes para a etapa de exportação"""
    
    @pytest.fixture
    def config_exportacao(self):
        """Configuração mock baseada no comportamento real"""
        return {
            'formato': 'zip',
            'diretorio_saida': './output',
            'timeout_exportacao': 30,
            'max_retries': 3
        }
    
    @pytest.fixture
    def etapa_exportacao(self, config_exportacao):
        """Etapa de exportação com mocks configurados"""
        with patch('infrastructure.orchestrator.etapas.etapa_exportacao.ExportadorKeywords'), \
             patch('infrastructure.orchestrator.etapas.etapa_exportacao.pathlib.Path'):
            return EtapaExportacao(config_exportacao)
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("prompts_gerados,expected_arquivos", [
        (["prompt1", "prompt2"], 1),
        (["prompt1"], 1),
        ([], 0),
    ])
    async def test_executar_exportacao_sucesso(self, etapa_exportacao, prompts_gerados, expected_arquivos):
        """Testa execução bem-sucedida da exportação"""
        # Act
        resultado = await etapa_exportacao.executar(prompts_gerados, "tecnologia")
        
        # Assert
        assert isinstance(resultado, ExportacaoResult)
        assert resultado.total_arquivos >= expected_arquivos
        assert len(resultado.arquivos_gerados) >= expected_arquivos
        assert resultado.tempo_execucao > 0
        assert resultado.metadados['nicho'] == "tecnologia"
    
    def test_obter_status(self, etapa_exportacao):
        """Testa obtenção de status da etapa"""
        # Act
        status = etapa_exportacao.obter_status()
        
        # Assert
        assert "formato" in status
        assert "configuracao" in status
        assert status["formato"] == "zip" 