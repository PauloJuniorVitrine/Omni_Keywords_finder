from typing import Dict, List, Optional, Any
"""
Testes para validação da refatoração do ExecucaoService.
Testa se os serviços especializados estão sendo usados corretamente.

Prompt: CHECKLIST_SEGUNDA_REVISAO.md - IMP-002
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-19
Versão: 1.0.0
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from backend.app.services.execucao_service import ExecucaoService
from backend.app.services.lote_execucao_service import LoteExecucaoService
from backend.app.services.agendamento_service import AgendamentoService
from backend.app.services.validacao_execucao_service import ValidacaoExecucaoService
from backend.app.services.prompt_service import PromptService


class TestExecucaoServiceRefatorado:
    """Testes para validação da refatoração do ExecucaoService."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.service = ExecucaoService()
    
    def test_inicializacao_servicos_especializados(self):
        """Testa se os serviços especializados são inicializados corretamente."""
        assert isinstance(self.service.lote_service, LoteExecucaoService)
        assert isinstance(self.service.agendamento_service, AgendamentoService)
        assert isinstance(self.service.validacao_service, ValidacaoExecucaoService)
        assert isinstance(self.service.prompt_service, PromptService)
    
    @patch('backend.app.services.execucao_service.ValidacaoExecucaoService.validar_lote_completo')
    @patch('backend.app.services.execucao_service.LoteExecucaoService.processar_lote')
    def test_processar_lote_execucoes_delega_para_servicos(self, mock_processar_lote, mock_validar_lote):
        """Testa se o processamento de lote delega para serviços especializados."""
        # Mock da validação
        dados_validos = [
            {'categoria_id': 1, 'palavras_chave': ['teste'], 'cluster': 'teste'}
        ]
        mock_validar_lote.return_value = (True, [], dados_validos)
        
        # Mock do processamento
        resultado_esperado = {
            'id_lote': '20241219T120000',
            'resultados': [{'execucao_id': 1, 'status': 'ok'}],
            'tempo_total': 1.5,
            'qtd_executada': 1,
            'log_path': 'logs/exec_trace/test.log'
        }
        mock_processar_lote.return_value = resultado_esperado
        
        # Executar teste
        dados = [{'categoria_id': 1, 'palavras_chave': ['teste'], 'cluster': 'teste'}]
        resultado = self.service.processar_lote_execucoes(dados)
        
        # Verificações
        mock_validar_lote.assert_called_once_with(dados)
        mock_processar_lote.assert_called_once_with(dados_validos)
        assert resultado == resultado_esperado
    
    @patch('backend.app.services.execucao_service.ValidacaoExecucaoService.validar_lote_completo')
    def test_processar_lote_execucoes_validacao_falha(self, mock_validar_lote):
        """Testa comportamento quando validação falha."""
        # Mock da validação falhando
        erros = ['categoria_id é obrigatório']
        mock_validar_lote.return_value = (False, erros, [])
        
        # Executar teste
        dados = [{'palavras_chave': ['teste']}]  # Sem categoria_id
        resultado = self.service.processar_lote_execucoes(dados)
        
        # Verificações
        assert resultado['erros_validacao'] == erros
        assert resultado['qtd_executada'] == 0
        assert resultado['tempo_total'] == 0.0
    
    @patch('backend.app.services.execucao_service.AgendamentoService.processar_agendamentos')
    def test_processar_execucoes_agendadas_delega_para_servico(self, mock_processar_agendamentos):
        """Testa se o processamento de agendamentos delega para serviço especializado."""
        # Mock do processamento
        resultado_esperado = {
            'total_processadas': 2,
            'logs_execucao': [{'agendamento_id': 1, 'status': 'ok'}],
            'log_path': 'logs/exec_trace/agendadas.log',
            'timestamp': '2024-12-19T12:00:00'
        }
        mock_processar_agendamentos.return_value = resultado_esperado
        
        # Executar teste
        resultado = self.service.processar_execucoes_agendadas()
        
        # Verificações
        mock_processar_agendamentos.assert_called_once()
        assert resultado == resultado_esperado
    
    @patch('backend.app.services.execucao_service.AgendamentoService.processar_agendamentos')
    def test_processar_execucoes_agendadas_sem_pendencias(self, mock_processar_agendamentos):
        """Testa comportamento quando não há agendamentos pendentes."""
        # Mock sem pendências
        mock_processar_agendamentos.return_value = None
        
        # Executar teste
        resultado = self.service.processar_execucoes_agendadas()
        
        # Verificações
        assert resultado is None
    
    @patch('backend.app.services.execucao_service.ValidacaoExecucaoService.validar_execucao_completa')
    @patch('backend.app.services.execucao_service.PromptService.processar_prompt_completo')
    @patch('backend.app.services.execucao_service.db')
    def test_executar_prompt_individual_sucesso(self, mock_db, mock_processar_prompt, mock_validar):
        """Testa execução individual bem-sucedida."""
        # Mock da validação
        categoria_mock = Mock()
        categoria_mock.nome = 'Teste'
        categoria_mock.cluster = 'cluster_teste'
        categoria_mock.prompt_path = '/path/to/prompt.txt'
        
        dados_validados = {
            'categoria_id': 1,
            'palavras_chave': ['teste'],
            'cluster': 'cluster_teste',
            'categoria': categoria_mock,
            'prompt_path': '/path/to/prompt.txt'
        }
        mock_validar.return_value = (True, None, dados_validados)
        
        # Mock do processamento de prompt
        mock_processar_prompt.return_value = (True, None, 'prompt preenchido')
        
        # Mock do banco de dados
        execucao_mock = Mock()
        execucao_mock.id = 1
        execucao_mock.tempo_real = 0.5
        
        # Executar teste
        resultado = self.service.executar_prompt_individual(
            categoria_id=1,
            palavras_chave=['teste'],
            cluster='cluster_teste'
        )
        
        # Verificações
        mock_validar.assert_called_once()
        mock_processar_prompt.assert_called_once()
        assert resultado['execucao_id'] == 1
        assert resultado['status'] == 'ok'
    
    @patch('backend.app.services.execucao_service.ValidacaoExecucaoService.validar_execucao_completa')
    def test_executar_prompt_individual_validacao_falha(self, mock_validar):
        """Testa execução individual com falha na validação."""
        # Mock da validação falhando
        mock_validar.return_value = (False, 'Categoria não encontrada', {})
        
        # Executar teste
        resultado = self.service.executar_prompt_individual(
            categoria_id=999,
            palavras_chave=['teste']
        )
        
        # Verificações
        assert 'erro' in resultado
        assert resultado['erro'] == 'Categoria não encontrada'
    
    @patch('backend.app.services.execucao_service.ValidacaoExecucaoService.validar_execucao_completa')
    @patch('backend.app.services.execucao_service.ValidacaoExecucaoService.validar_data_agendamento')
    @patch('backend.app.services.execucao_service.AgendamentoService.agendar_execucao')
    def test_agendar_execucao_sucesso(self, mock_agendar, mock_validar_data, mock_validar):
        """Testa agendamento bem-sucedido."""
        # Mock da validação
        categoria_mock = Mock()
        categoria_mock.nome = 'Teste'
        categoria_mock.cluster = 'cluster_teste'
        categoria_mock.prompt_path = '/path/to/prompt.txt'
        
        dados_validados = {
            'categoria_id': 1,
            'palavras_chave': ['teste'],
            'cluster': 'cluster_teste',
            'categoria': categoria_mock,
            'prompt_path': '/path/to/prompt.txt'
        }
        mock_validar.return_value = (True, None, dados_validados)
        
        # Mock da validação de data
        data_futura = datetime.utcnow() + timedelta(hours=1)
        mock_validar_data.return_value = (True, None, data_futura.isoformat())
        
        # Mock do agendamento
        resultado_agendamento = {
            'agendamento_id': 1,
            'status': 'agendado',
            'data_agendada': data_futura.isoformat()
        }
        mock_agendar.return_value = resultado_agendamento
        
        # Executar teste
        resultado = self.service.agendar_execucao(
            categoria_id=1,
            palavras_chave=['teste'],
            cluster='cluster_teste',
            data_agendada=data_futura,
            usuario='teste'
        )
        
        # Verificações
        mock_validar.assert_called_once()
        mock_validar_data.assert_called_once()
        mock_agendar.assert_called_once()
        assert resultado == resultado_agendamento
    
    @patch('backend.app.services.execucao_service.PromptService.obter_estatisticas_cache')
    def test_obter_estatisticas_servicos(self, mock_estatisticas):
        """Testa obtenção de estatísticas dos serviços."""
        # Mock das estatísticas
        stats_prompt = {
            'cache_enabled': True,
            'tamanho_atual': 5,
            'tamanho_maximo': 100,
            'taxa_ocupacao': 0.05
        }
        mock_estatisticas.return_value = stats_prompt
        
        # Executar teste
        resultado = self.service.obter_estatisticas_servicos()
        
        # Verificações
        assert 'prompt_service' in resultado
        assert resultado['prompt_service'] == stats_prompt
        assert 'servicos_ativos' in resultado
        assert 'LoteExecucaoService' in resultado['servicos_ativos']
        assert 'AgendamentoService' in resultado['servicos_ativos']
        assert 'ValidacaoExecucaoService' in resultado['servicos_ativos']
        assert 'PromptService' in resultado['servicos_ativos']
    
    def test_compatibilidade_api_existente(self):
        """Testa se as funções de compatibilidade estão disponíveis."""
        from backend.app.services.execucao_service import processar_lote_execucoes, processar_execucoes_agendadas
        
        # Verificar se as funções existem
        assert callable(processar_lote_execucoes)
        assert callable(processar_execucoes_agendadas)
        
        # Verificar se delegam para o serviço
        with patch('backend.app.services.execucao_service._execucao_service') as mock_service:
            mock_service.processar_lote_execucoes.return_value = {'teste': 'ok'}
            mock_service.processar_execucoes_agendadas.return_value = {'teste': 'ok'}
            
            dados = [{'categoria_id': 1, 'palavras_chave': ['teste']}]
            resultado_lote = processar_lote_execucoes(dados)
            resultado_agendadas = processar_execucoes_agendadas()
            
            assert resultado_lote == {'teste': 'ok'}
            assert resultado_agendadas == {'teste': 'ok'} 