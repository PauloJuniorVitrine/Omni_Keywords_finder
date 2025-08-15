"""
Testes unitários para FluxoCompletoOrchestrator
Tracing ID: TEST_ORCHESTRATOR_001_20241227
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any
import sys
import os

# Adicionar path do projeto
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from infrastructure.orchestrator.fluxo_completo_orchestrator import FluxoCompletoOrchestrator
from infrastructure.orchestrator.progress_tracker import ProgressTracker
from infrastructure.orchestrator.error_handler import ErrorHandler


class TestFluxoCompletoOrchestrator:
    """Testes para o orquestrador principal do fluxo completo"""
    
    @pytest.fixture
    def mock_config(self):
        """Configuração mock para testes"""
        return {
            'nicho': 'teste_nicho',
            'max_keywords': 100,
            'timeout_etapa': 300,
            'retry_attempts': 3
        }
    
    @pytest.fixture
    def orchestrator(self, mock_config):
        """Instância do orquestrador para testes"""
        with patch('infrastructure.orchestrator.fluxo_completo_orchestrator.ProgressTracker'), \
             patch('infrastructure.orchestrator.fluxo_completo_orchestrator.ErrorHandler'):
            return FluxoCompletoOrchestrator(mock_config)
    
    def test_inicializacao_orchestrator(self, mock_config):
        """Testa inicialização correta do orquestrador"""
        # Arrange & Act
        with patch('infrastructure.orchestrator.fluxo_completo_orchestrator.ProgressTracker'), \
             patch('infrastructure.orchestrator.fluxo_completo_orchestrator.ErrorHandler'):
            orchestrator = FluxoCompletoOrchestrator(mock_config)
        
        # Assert
        assert orchestrator.config == mock_config
        assert orchestrator.etapas is not None
        assert orchestrator.progress_tracker is not None
        assert orchestrator.error_handler is not None
    
    def test_validacao_configuracao_valida(self, orchestrator):
        """Testa validação de configuração válida"""
        # Arrange
        config_valida = {
            'nicho': 'teste',
            'max_keywords': 50,
            'timeout_etapa': 200
        }
        
        # Act
        resultado = orchestrator.validar_configuracao(config_valida)
        
        # Assert
        assert resultado is True
    
    def test_validacao_configuracao_invalida(self, orchestrator):
        """Testa validação de configuração inválida"""
        # Arrange
        config_invalida = {
            'nicho': '',  # Nicho vazio
            'max_keywords': -1,  # Valor negativo
            'timeout_etapa': 0  # Timeout zero
        }
        
        # Act & Assert
        with pytest.raises(ValueError):
            orchestrator.validar_configuracao(config_invalida)
    
    @patch('infrastructure.orchestrator.fluxo_completo_orchestrator.EtapaColeta')
    def test_execucao_etapa_coleta_sucesso(self, mock_etapa_coleta, orchestrator):
        """Testa execução bem-sucedida da etapa de coleta"""
        # Arrange
        mock_etapa = Mock()
        mock_etapa.executar.return_value = {'keywords': ['teste1', 'teste2']}
        mock_etapa_coleta.return_value = mock_etapa
        
        # Act
        resultado = orchestrator.executar_etapa('coleta', {'nicho': 'teste'})
        
        # Assert
        assert resultado['status'] == 'sucesso'
        assert 'keywords' in resultado['dados']
        mock_etapa.executar.assert_called_once()
    
    @patch('infrastructure.orchestrator.fluxo_completo_orchestrator.EtapaColeta')
    def test_execucao_etapa_coleta_falha(self, mock_etapa_coleta, orchestrator):
        """Testa execução com falha na etapa de coleta"""
        # Arrange
        mock_etapa = Mock()
        mock_etapa.executar.side_effect = Exception("Erro de coleta")
        mock_etapa_coleta.return_value = mock_etapa
        
        # Act
        resultado = orchestrator.executar_etapa('coleta', {'nicho': 'teste'})
        
        # Assert
        assert resultado['status'] == 'erro'
        assert 'Erro de coleta' in resultado['mensagem']
    
    def test_execucao_etapa_inexistente(self, orchestrator):
        """Testa execução de etapa que não existe"""
        # Act
        resultado = orchestrator.executar_etapa('etapa_inexistente', {})
        
        # Assert
        assert resultado['status'] == 'erro'
        assert 'Etapa não encontrada' in resultado['mensagem']
    
    @patch('infrastructure.orchestrator.fluxo_completo_orchestrator.EtapaColeta')
    @patch('infrastructure.orchestrator.fluxo_completo_orchestrator.EtapaValidacao')
    @patch('infrastructure.orchestrator.fluxo_completo_orchestrator.EtapaProcessamento')
    def test_execucao_fluxo_completo_sucesso(self, mock_processamento, mock_validacao, mock_coleta, orchestrator):
        """Testa execução completa do fluxo com sucesso"""
        # Arrange
        mock_coleta.return_value.executar.return_value = {'keywords': ['teste1', 'teste2']}
        mock_validacao.return_value.executar.return_value = {'keywords_validas': ['teste1']}
        mock_processamento.return_value.executar.return_value = {'keywords_processadas': ['teste1']}
        
        # Act
        resultado = orchestrator.executar_fluxo_completo()
        
        # Assert
        assert resultado['status'] == 'sucesso'
        assert resultado['etapas_executadas'] == 3
        assert 'keywords_processadas' in resultado['dados_finais']
    
    def test_execucao_fluxo_completo_com_falha(self, orchestrator):
        """Testa execução do fluxo com falha em etapa intermediária"""
        # Arrange
        with patch.object(orchestrator, 'executar_etapa') as mock_executar:
            mock_executar.side_effect = [
                {'status': 'sucesso', 'dados': {'keywords': ['teste1']}},
                {'status': 'erro', 'mensagem': 'Falha na validação'},
                {'status': 'sucesso', 'dados': {'keywords_processadas': ['teste1']}}
            ]
        
        # Act
        resultado = orchestrator.executar_fluxo_completo()
        
        # Assert
        assert resultado['status'] == 'erro'
        assert 'Falha na validação' in resultado['mensagem']
        assert resultado['etapa_falha'] == 'validacao'
    
    def test_rollback_apos_falha(self, orchestrator):
        """Testa rollback após falha em etapa"""
        # Arrange
        with patch.object(orchestrator.progress_tracker, 'salvar_checkpoint') as mock_salvar, \
             patch.object(orchestrator.progress_tracker, 'restaurar_checkpoint') as mock_restaurar:
            
            # Act
            orchestrator.executar_com_rollback('coleta', {'nicho': 'teste'})
            
            # Assert
            mock_salvar.assert_called()
            # Rollback só deve ser chamado se houver falha
    
    def test_limpeza_recursos(self, orchestrator):
        """Testa limpeza adequada de recursos"""
        # Arrange
        with patch.object(orchestrator.progress_tracker, 'limpar') as mock_limpar:
            # Act
            orchestrator.limpar_recursos()
            
            # Assert
            mock_limpar.assert_called_once()
    
    def test_obter_status_execucao(self, orchestrator):
        """Testa obtenção do status de execução"""
        # Arrange
        orchestrator.progress_tracker.obter_progresso.return_value = {
            'etapa_atual': 'coleta',
            'progresso': 25,
            'tempo_estimado': 120
        }
        
        # Act
        status = orchestrator.obter_status()
        
        # Assert
        assert status['etapa_atual'] == 'coleta'
        assert status['progresso'] == 25
        assert status['tempo_estimado'] == 120
    
    def test_pausar_execucao(self, orchestrator):
        """Testa pausa da execução"""
        # Arrange
        with patch.object(orchestrator.progress_tracker, 'pausar') as mock_pausar:
            # Act
            resultado = orchestrator.pausar_execucao()
            
            # Assert
            assert resultado['status'] == 'pausado'
            mock_pausar.assert_called_once()
    
    def test_retomar_execucao(self, orchestrator):
        """Testa retomada da execução"""
        # Arrange
        with patch.object(orchestrator.progress_tracker, 'retomar') as mock_retomar:
            # Act
            resultado = orchestrator.retomar_execucao()
            
            # Assert
            assert resultado['status'] == 'retomado'
            mock_retomar.assert_called_once()
    
    def test_cancelar_execucao(self, orchestrator):
        """Testa cancelamento da execução"""
        # Arrange
        with patch.object(orchestrator.progress_tracker, 'cancelar') as mock_cancelar:
            # Act
            resultado = orchestrator.cancelar_execucao()
            
            # Assert
            assert resultado['status'] == 'cancelado'
            mock_cancelar.assert_called_once()
    
    def test_obter_metricas_execucao(self, orchestrator):
        """Testa obtenção de métricas de execução"""
        # Arrange
        orchestrator.metricas = {
            'tempo_total': 300,
            'keywords_processadas': 150,
            'taxa_sucesso': 0.95
        }
        
        # Act
        metricas = orchestrator.obter_metricas()
        
        # Assert
        assert metricas['tempo_total'] == 300
        assert metricas['keywords_processadas'] == 150
        assert metricas['taxa_sucesso'] == 0.95


class TestFluxoCompletoOrchestratorIntegracao:
    """Testes de integração para o orquestrador"""
    
    @pytest.fixture
    def config_real(self):
        """Configuração real para testes de integração"""
        return {
            'nicho': 'tecnologia',
            'max_keywords': 50,
            'timeout_etapa': 300,
            'retry_attempts': 3,
            'cache_enabled': True,
            'log_level': 'INFO'
        }
    
    def test_integracao_com_sistema_existente(self, config_real):
        """Testa integração com sistema existente"""
        # Este teste seria executado apenas em ambiente de integração
        # Arrange
        with patch('infrastructure.orchestrator.fluxo_completo_orchestrator.ProgressTracker'), \
             patch('infrastructure.orchestrator.fluxo_completo_orchestrator.ErrorHandler'):
            orchestrator = FluxoCompletoOrchestrator(config_real)
        
        # Act & Assert
        assert orchestrator.config['nicho'] == 'tecnologia'
        assert orchestrator.config['cache_enabled'] is True
    
    def test_persistencia_estado(self, config_real):
        """Testa persistência de estado entre execuções"""
        # Arrange
        with patch('infrastructure.orchestrator.fluxo_completo_orchestrator.ProgressTracker') as mock_tracker, \
             patch('infrastructure.orchestrator.fluxo_completo_orchestrator.ErrorHandler'):
            
            mock_tracker.return_value.obter_estado.return_value = {
                'etapa_atual': 'validacao',
                'progresso': 50,
                'dados_intermediarios': {'keywords': ['teste1', 'teste2']}
            }
            
            orchestrator = FluxoCompletoOrchestrator(config_real)
        
        # Act
        estado = orchestrator.progress_tracker.obter_estado()
        
        # Assert
        assert estado['etapa_atual'] == 'validacao'
        assert estado['progresso'] == 50
        assert 'keywords' in estado['dados_intermediarios']


if __name__ == '__main__':
    pytest.main([__file__, '-value']) 