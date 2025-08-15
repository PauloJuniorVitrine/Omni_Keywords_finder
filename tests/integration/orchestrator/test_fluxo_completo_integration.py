"""
Testes de Integração - Fluxo Completo do Orquestrador

Testa o fluxo completo de processamento de keywords através do orquestrador:
- Coleta de keywords
- Validação
- Processamento
- Preenchimento
- Exportação

Tracing ID: TEST_INTEGRATION_001_20241227
Versão: 2.0
Autor: IA-Cursor
Status: ✅ ATUALIZADO PARA NOVA ARQUITETURA
"""

import pytest
import asyncio
import time
from typing import List, Dict, Any
from unittest.mock import Mock, patch, AsyncMock

from infrastructure.orchestrator.fluxo_completo_orchestrator import FluxoCompletoOrchestrator
from infrastructure.orchestrator.config import OrchestratorConfig, NichoConfig, NichoType
from domain.models import Keyword


class TestFluxoCompletoOrchestrator:
    """Testes para o fluxo completo do orquestrador."""
    
    @pytest.fixture
    def config_orchestrator(self):
        """Configuração de teste para o orquestrador."""
        config = OrchestratorConfig(
            modo_debug=True,
            log_level="DEBUG",
            max_nichos_concorrentes=1,
            timeout_total_minutos=5,
            persistir_progresso=False,
            notificar_progresso=False,
            notificar_erros=False,
            notificar_conclusao=False,
            coletar_metricas=False
        )
        
        # Adicionar nicho de teste
        nicho_config = NichoConfig(
            nome="Teste Tecnologia",
            tipo=NichoType.TECNOLOGIA,
            keywords_semente=["python", "programação", "desenvolvimento"],
            categorias=["programação", "tecnologia", "software"]
        )
        config.adicionar_nicho("teste_tecnologia", nicho_config)
        
        return config
    
    @pytest.fixture
    def orchestrator(self, config_orchestrator):
        """Instância do orquestrador para testes."""
        return FluxoCompletoOrchestrator(config_orchestrator)
    
    @pytest.fixture
    def keywords_mock(self):
        """Keywords mock para testes."""
        return [
            Keyword(
                termo="python programação",
                volume_busca=1000,
                cpc=2.5,
                concorrencia=0.6,
                intencao="informacional",
                score=0.8,
                justificativa="Keyword relevante para tecnologia",
                fonte="google_suggest",
                data_coleta=None
            ),
            Keyword(
                termo="desenvolvimento web",
                volume_busca=2000,
                cpc=3.0,
                concorrencia=0.7,
                intencao="comercial",
                score=0.9,
                justificativa="Keyword de alto volume",
                fonte="google_keyword_planner",
                data_coleta=None
            ),
            Keyword(
                termo="curso python online",
                volume_busca=500,
                cpc=1.5,
                concorrencia=0.4,
                intencao="transacional",
                score=0.7,
                justificativa="Keyword de cauda longa",
                fonte="amazon",
                data_coleta=None
            )
        ]
    
    @pytest.mark.asyncio
    async def test_inicializacao_orchestrator(self, config_orchestrator):
        """Testa inicialização do orquestrador."""
        orchestrator = FluxoCompletoOrchestrator(config_orchestrator)
        
        assert orchestrator.config == config_orchestrator
        assert orchestrator.progress_tracker is not None
        assert orchestrator.error_handler is not None
        assert len(orchestrator.etapas) == 5  # coleta, validação, processamento, preenchimento, exportação
    
    @pytest.mark.asyncio
    async def test_execucao_fluxo_completo(self, orchestrator, keywords_mock):
        """Testa execução do fluxo completo."""
        # Mock das etapas para evitar chamadas reais
        with patch.object(orchestrator.etapas['coleta'], 'executar') as mock_coleta, \
             patch.object(orchestrator.etapas['validacao'], 'executar') as mock_validacao, \
             patch.object(orchestrator.etapas['processamento'], 'executar') as mock_processamento, \
             patch.object(orchestrator.etapas['preenchimento'], 'executar') as mock_preenchimento, \
             patch.object(orchestrator.etapas['exportacao'], 'executar') as mock_exportacao:
            
            # Configurar mocks
            mock_coleta.return_value = type('obj', (object,), {
                'keywords_coletadas': ["python", "programação", "desenvolvimento"],
                'total_keywords': 3,
                'tempo_execucao': 1.0,
                'fontes_utilizadas': ['google_suggest'],
                'metadados': {}
            })
            
            mock_validacao.return_value = type('obj', (object,), {
                'keywords_aprovadas': keywords_mock,
                'total_keywords': 3,
                'tempo_execucao': 0.5,
                'metricas_validacao': {},
                'metadados': {}
            })
            
            mock_processamento.return_value = type('obj', (object,), {
                'keywords_processadas': keywords_mock,
                'total_keywords': 3,
                'tempo_execucao': 1.5,
                'metricas_processamento': {},
                'metadados': {}
            })
            
            mock_preenchimento.return_value = type('obj', (object,), {
                'prompts_gerados': ["prompt1", "prompt2", "prompt3"],
                'total_prompts': 3,
                'tempo_execucao': 2.0,
                'metricas_preenchimento': {},
                'metadados': {}
            })
            
            mock_exportacao.return_value = type('obj', (object,), {
                'arquivo_gerado': "teste_tecnologia.zip",
                'tamanho_arquivo': 1024,
                'tempo_execucao': 0.5,
                'metricas_exportacao': {},
                'metadados': {}
            })
            
            # Executar fluxo completo
            resultado = await orchestrator.executar_fluxo_completo("teste_tecnologia")
            
            # Verificar que todas as etapas foram chamadas
            mock_coleta.assert_called_once()
            mock_validacao.assert_called_once()
            mock_processamento.assert_called_once()
            mock_preenchimento.assert_called_once()
            mock_exportacao.assert_called_once()
            
            # Verificar resultado
            assert resultado is not None
            assert resultado['status'] == 'concluido'
            assert resultado['nicho'] == 'teste_tecnologia'
            assert 'metricas' in resultado
            assert 'tempo_total' in resultado
    
    @pytest.mark.asyncio
    async def test_execucao_com_erro_etapa(self, orchestrator):
        """Testa execução com erro em uma etapa."""
        # Mock da etapa de coleta para simular erro
        with patch.object(orchestrator.etapas['coleta'], 'executar') as mock_coleta:
            mock_coleta.side_effect = Exception("Erro simulado na coleta")
            
            # Executar fluxo completo
            resultado = await orchestrator.executar_fluxo_completo("teste_tecnologia")
            
            # Verificar que o erro foi tratado
            assert resultado is not None
            assert resultado['status'] == 'erro'
            assert 'erro' in resultado
            assert 'Erro simulado na coleta' in str(resultado['erro'])
    
    @pytest.mark.asyncio
    async def test_execucao_timeout(self, orchestrator):
        """Testa execução com timeout."""
        # Mock da etapa de coleta para simular timeout
        with patch.object(orchestrator.etapas['coleta'], 'executar') as mock_coleta:
            async def slow_execution(*args, **kwargs):
                await asyncio.sleep(10)  # Simular execução lenta
                return type('obj', (object,), {
                    'keywords_coletadas': [],
                    'total_keywords': 0,
                    'tempo_execucao': 10.0,
                    'fontes_utilizadas': [],
                    'metadados': {}
                })
            
            mock_coleta.side_effect = slow_execution
            
            # Executar com timeout curto
            orchestrator.config.timeout_total_minutos = 0.1  # 6 segundos
            
            resultado = await orchestrator.executar_fluxo_completo("teste_tecnologia")
            
            # Verificar que o timeout foi detectado
            assert resultado is not None
            assert resultado['status'] == 'timeout'
    
    @pytest.mark.asyncio
    async def test_progress_tracking(self, orchestrator):
        """Testa rastreamento de progresso."""
        # Mock das etapas
        with patch.object(orchestrator.etapas['coleta'], 'executar') as mock_coleta, \
             patch.object(orchestrator.etapas['validacao'], 'executar') as mock_validacao:
            
            # Configurar mocks
            mock_coleta.return_value = type('obj', (object,), {
                'keywords_coletadas': ["python"],
                'total_keywords': 1,
                'tempo_execucao': 1.0,
                'fontes_utilizadas': ['google_suggest'],
                'metadados': {}
            })
            
            mock_validacao.side_effect = Exception("Erro na validação")
            
            # Executar fluxo
            resultado = await orchestrator.executar_fluxo_completo("teste_tecnologia")
            
            # Verificar progresso
            progresso = orchestrator.progress_tracker.obter_progresso("teste_tecnologia")
            assert progresso is not None
            assert progresso['etapa_atual'] == 'validacao'
            assert progresso['status'] == 'erro'
    
    @pytest.mark.asyncio
    async def test_error_handling(self, orchestrator):
        """Testa tratamento de erros."""
        # Mock da etapa de coleta para simular erro
        with patch.object(orchestrator.etapas['coleta'], 'executar') as mock_coleta:
            mock_coleta.side_effect = Exception("Erro crítico")
            
            # Executar fluxo
            resultado = await orchestrator.executar_fluxo_completo("teste_tecnologia")
            
            # Verificar que o erro foi registrado
            erros = orchestrator.error_handler.obter_erros("teste_tecnologia")
            assert len(erros) > 0
            assert any("Erro crítico" in str(erro) for erro in erros)
    
    @pytest.mark.asyncio
    async def test_metricas_execucao(self, orchestrator, keywords_mock):
        """Testa coleta de métricas durante execução."""
        # Mock das etapas
        with patch.object(orchestrator.etapas['coleta'], 'executar') as mock_coleta, \
             patch.object(orchestrator.etapas['validacao'], 'executar') as mock_validacao, \
             patch.object(orchestrator.etapas['processamento'], 'executar') as mock_processamento, \
             patch.object(orchestrator.etapas['preenchimento'], 'executar') as mock_preenchimento, \
             patch.object(orchestrator.etapas['exportacao'], 'executar') as mock_exportacao:
            
            # Configurar mocks com métricas
            mock_coleta.return_value = type('obj', (object,), {
                'keywords_coletadas': ["python"],
                'total_keywords': 1,
                'tempo_execucao': 1.0,
                'fontes_utilizadas': ['google_suggest'],
                'metadados': {'coleta_metricas': 'teste'}
            })
            
            mock_validacao.return_value = type('obj', (object,), {
                'keywords_aprovadas': keywords_mock,
                'total_keywords': 3,
                'tempo_execucao': 0.5,
                'metricas_validacao': {'taxa_aprovacao': 0.8},
                'metadados': {}
            })
            
            mock_processamento.return_value = type('obj', (object,), {
                'keywords_processadas': keywords_mock,
                'total_keywords': 3,
                'tempo_execucao': 1.5,
                'metricas_processamento': {'score_medio': 0.8},
                'metadados': {}
            })
            
            mock_preenchimento.return_value = type('obj', (object,), {
                'prompts_gerados': ["prompt1"],
                'total_prompts': 1,
                'tempo_execucao': 2.0,
                'metricas_preenchimento': {'qualidade_media': 0.9},
                'metadados': {}
            })
            
            mock_exportacao.return_value = type('obj', (object,), {
                'arquivo_gerado': "teste.zip",
                'tamanho_arquivo': 1024,
                'tempo_execucao': 0.5,
                'metricas_exportacao': {'tamanho_mb': 1.0},
                'metadados': {}
            })
            
            # Executar fluxo
            resultado = await orchestrator.executar_fluxo_completo("teste_tecnologia")
            
            # Verificar métricas
            assert 'metricas' in resultado
            metricas = resultado['metricas']
            assert 'coleta' in metricas
            assert 'validacao' in metricas
            assert 'processamento' in metricas
            assert 'preenchimento' in metricas
            assert 'exportacao' in metricas
            assert 'tempo_total' in resultado
    
    @pytest.mark.asyncio
    async def test_execucao_multiplos_nichos(self, config_orchestrator):
        """Testa execução de múltiplos nichos."""
        # Adicionar segundo nicho
        nicho_config2 = NichoConfig(
            nome="Teste Finanças",
            tipo=NichoType.FINANCAS,
            keywords_semente=["investimentos", "economia"],
            categorias=["investimentos", "economia"]
        )
        config_orchestrator.adicionar_nicho("teste_financas", nicho_config2)
        
        orchestrator = FluxoCompletoOrchestrator(config_orchestrator)
        
        # Mock das etapas
        with patch.object(orchestrator.etapas['coleta'], 'executar') as mock_coleta, \
             patch.object(orchestrator.etapas['validacao'], 'executar') as mock_validacao, \
             patch.object(orchestrator.etapas['processamento'], 'executar') as mock_processamento, \
             patch.object(orchestrator.etapas['preenchimento'], 'executar') as mock_preenchimento, \
             patch.object(orchestrator.etapas['exportacao'], 'executar') as mock_exportacao:
            
            # Configurar mocks
            mock_return = type('obj', (object,), {
                'keywords_coletadas': ["teste"],
                'total_keywords': 1,
                'tempo_execucao': 1.0,
                'fontes_utilizadas': ['teste'],
                'metadados': {}
            })
            
            mock_coleta.return_value = mock_return
            mock_validacao.return_value = type('obj', (object,), {
                'keywords_aprovadas': [],
                'total_keywords': 0,
                'tempo_execucao': 0.5,
                'metricas_validacao': {},
                'metadados': {}
            })
            mock_processamento.return_value = type('obj', (object,), {
                'keywords_processadas': [],
                'total_keywords': 0,
                'tempo_execucao': 1.5,
                'metricas_processamento': {},
                'metadados': {}
            })
            mock_preenchimento.return_value = type('obj', (object,), {
                'prompts_gerados': [],
                'total_prompts': 0,
                'tempo_execucao': 2.0,
                'metricas_preenchimento': {},
                'metadados': {}
            })
            mock_exportacao.return_value = type('obj', (object,), {
                'arquivo_gerado': "teste.zip",
                'tamanho_arquivo': 1024,
                'tempo_execucao': 0.5,
                'metricas_exportacao': {},
                'metadados': {}
            })
            
            # Executar múltiplos nichos
            nichos = ["teste_tecnologia", "teste_financas"]
            resultados = await orchestrator.executar_multiplos_nichos(nichos)
            
            # Verificar resultados
            assert len(resultados) == 2
            assert all(resultado['status'] == 'concluido' for resultado in resultados.values())
            assert mock_coleta.call_count == 2  # Chamado para cada nicho


if __name__ == "__main__":
    pytest.main([__file__, "-value"]) 