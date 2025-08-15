"""
Testes unitários para LoteExecucaoService
⚠️ CRIAR MAS NÃO EXECUTAR - Executar apenas na Fase 6.5

Prompt: CHECKLIST_TESTES_UNITARIOS.md - Item 1.2
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Versão: 1.0.0
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor

from backend.app.services.lote_execucao_service import (
    LoteExecucaoService,
    LoteConfig,
    ExecucaoItem,
    LoteResultado,
    LoteStatus,
    ExecucaoStatus,
    init_lote_service,
    get_lote_service
)

class TestLoteExecucaoService:
    """Testes para LoteExecucaoService baseados no código real."""
    
    @pytest.fixture
    def service(self):
        """Fixture para serviço de lote."""
        config = {'max_workers': 5}
        return LoteExecucaoService(config)
    
    @pytest.fixture
    def sample_config(self):
        """Fixture para configuração de lote real."""
        return LoteConfig(
            max_concurrent=3,
            timeout_por_execucao=300,
            retry_delay=60,
            max_retries=3,
            priority=5
        )
    
    @pytest.fixture
    def sample_execucoes(self):
        """Fixture para execuções reais."""
        return [
            {
                'categoria_id': 1,
                'palavras_chave': ["seo", "ads", "social media"],
                'cluster': "marketing_digital"
            },
            {
                'categoria_id': 2,
                'palavras_chave': ["email marketing", "automacao"],
                'cluster': "email_marketing"
            },
            {
                'categoria_id': 3,
                'palavras_chave': ["content marketing", "blog"],
                'cluster': "content_marketing"
            }
        ]
    
    def test_init_service(self, service):
        """Testa inicialização do serviço."""
        assert service.config == {'max_workers': 5}
        assert isinstance(service.lotes_ativos, dict)
        assert service.running is True
        assert service.processing_thread is not None
        assert service.on_lote_complete is None
        assert service.on_execucao_complete is None
        assert service.on_error is None
        
        # Verificar estatísticas iniciais
        assert service.stats['lotes_processados'] == 0
        assert service.stats['execucoes_processadas'] == 0
        assert service.stats['tempo_total_processamento'] == 0.0
        assert service.stats['taxa_sucesso_geral'] == 0.0
    
    def test_start_stop_processing(self, service):
        """Testa início e parada do processamento."""
        # Verificar que está rodando
        assert service.running is True
        assert service.processing_thread is not None
        assert service.processing_thread.is_alive()
        
        # Parar processamento
        service.stop_processing()
        assert service.running is False
    
    def test_criar_lote_sucesso(self, service, sample_config, sample_execucoes):
        """Testa criação de lote com sucesso."""
        user_id = "user_123"
        
        lote_id = service.criar_lote(
            execucoes=sample_execucoes,
            config=sample_config,
            user_id=user_id
        )
        
        assert lote_id is not None
        assert lote_id in service.lotes_ativos
        
        lote_info = service.lotes_ativos[lote_id]
        assert lote_info['status'] == LoteStatus.PENDENTE
        assert lote_info['user_id'] == user_id
        assert lote_info['config'] == sample_config
        assert len(lote_info['execucoes']) == 3
        assert lote_info['progresso'] == 0
        assert lote_info['resultado'] is None
    
    def test_criar_lote_com_execucoes_especificas(self, service, sample_config, sample_execucoes):
        """Testa criação de lote com execuções específicas."""
        user_id = "user_456"
        
        lote_id = service.criar_lote(
            execucoes=sample_execucoes,
            config=sample_config,
            user_id=user_id
        )
        
        lote_info = service.lotes_ativos[lote_id]
        
        # Verificar primeira execução
        execucao1 = lote_info['execucoes'][0]
        assert execucao1.categoria_id == 1
        assert execucao1.palavras_chave == ["seo", "ads", "social media"]
        assert execucao1.cluster == "marketing_digital"
        assert execucao1.status == ExecucaoStatus.PENDENTE
        assert execucao1.max_tentativas == 3
        
        # Verificar segunda execução
        execucao2 = lote_info['execucoes'][1]
        assert execucao2.categoria_id == 2
        assert execucao2.palavras_chave == ["email marketing", "automacao"]
        assert execucao2.cluster == "email_marketing"
    
    def test_criar_lote_sem_config(self, service, sample_execucoes):
        """Testa criação de lote sem configuração específica."""
        user_id = "user_default"
        
        lote_id = service.criar_lote(
            execucoes=sample_execucoes,
            user_id=user_id
        )
        
        lote_info = service.lotes_ativos[lote_id]
        assert lote_info['config'] is not None
        assert lote_info['config'].max_concurrent == 5  # Valor padrão
        assert lote_info['config'].timeout_por_execucao == 300  # Valor padrão
        assert lote_info['config'].max_retries == 3  # Valor padrão
    
    def test_obter_status_lote_existente(self, service, sample_config, sample_execucoes):
        """Testa obtenção de status de lote existente."""
        user_id = "user_status"
        
        lote_id = service.criar_lote(
            execucoes=sample_execucoes,
            config=sample_config,
            user_id=user_id
        )
        
        status = service.obter_status_lote(lote_id)
        
        assert status is not None
        assert status['lote_id'] == lote_id
        assert status['status'] == "pendente"
        assert status['progresso'] == 0
        assert status['total_execucoes'] == 3
        assert status['execucoes_concluidas'] == 0
        assert status['execucoes_falharam'] == 0
        assert status['execucoes_em_execucao'] == 0
        assert status['execucoes_pendentes'] == 3
        assert status['taxa_sucesso'] == 0
        assert status['criado_em'] is not None
        assert status['inicio_processamento'] is None
        assert status['fim_processamento'] is None
        assert status['resultado'] is None
    
    def test_obter_status_lote_inexistente(self, service):
        """Testa obtenção de status de lote inexistente."""
        status = service.obter_status_lote("lote_inexistente")
        assert status is None
    
    def test_cancelar_lote_pendente(self, service, sample_config, sample_execucoes):
        """Testa cancelamento de lote pendente."""
        user_id = "user_cancel"
        
        lote_id = service.criar_lote(
            execucoes=sample_execucoes,
            config=sample_config,
            user_id=user_id
        )
        
        # Verificar que está pendente
        lote_info = service.lotes_ativos[lote_id]
        assert lote_info['status'] == LoteStatus.PENDENTE
        
        # Cancelar
        sucesso = service.cancelar_lote(lote_id)
        assert sucesso is True
        
        # Verificar que foi cancelado
        lote_info = service.lotes_ativos[lote_id]
        assert lote_info['status'] == LoteStatus.CANCELADO
        assert lote_info['fim_processamento'] is not None
        
        # Verificar que execuções foram canceladas
        for execucao in lote_info['execucoes']:
            assert execucao.status == ExecucaoStatus.CANCELADA
    
    def test_cancelar_lote_inexistente(self, service):
        """Testa cancelamento de lote inexistente."""
        sucesso = service.cancelar_lote("lote_inexistente")
        assert sucesso is False
    
    def test_cancelar_lote_ja_concluido(self, service, sample_config, sample_execucoes):
        """Testa cancelamento de lote já concluído."""
        user_id = "user_cancel_concluido"
        
        lote_id = service.criar_lote(
            execucoes=sample_execucoes,
            config=sample_config,
            user_id=user_id
        )
        
        # Simular lote concluído
        lote_info = service.lotes_ativos[lote_id]
        lote_info['status'] = LoteStatus.CONCLUIDO
        
        # Tentar cancelar
        sucesso = service.cancelar_lote(lote_id)
        assert sucesso is False
    
    def test_pausar_lote_em_execucao(self, service, sample_config, sample_execucoes):
        """Testa pausa de lote em execução."""
        user_id = "user_pause"
        
        lote_id = service.criar_lote(
            execucoes=sample_execucoes,
            config=sample_config,
            user_id=user_id
        )
        
        # Simular lote em execução
        lote_info = service.lotes_ativos[lote_id]
        lote_info['status'] = LoteStatus.EM_EXECUCAO
        
        # Pausar
        sucesso = service.pausar_lote(lote_id)
        assert sucesso is True
        
        # Verificar que foi pausado
        lote_info = service.lotes_ativos[lote_id]
        assert lote_info['status'] == LoteStatus.PAUSADO
    
    def test_pausar_lote_nao_em_execucao(self, service, sample_config, sample_execucoes):
        """Testa pausa de lote não em execução."""
        user_id = "user_pause_erro"
        
        lote_id = service.criar_lote(
            execucoes=sample_execucoes,
            config=sample_config,
            user_id=user_id
        )
        
        # Tentar pausar lote pendente
        sucesso = service.pausar_lote(lote_id)
        assert sucesso is False
    
    def test_retomar_lote_pausado(self, service, sample_config, sample_execucoes):
        """Testa retomada de lote pausado."""
        user_id = "user_resume"
        
        lote_id = service.criar_lote(
            execucoes=sample_execucoes,
            config=sample_config,
            user_id=user_id
        )
        
        # Simular lote pausado
        lote_info = service.lotes_ativos[lote_id]
        lote_info['status'] = LoteStatus.PAUSADO
        
        # Retomar
        sucesso = service.retomar_lote(lote_id)
        assert sucesso is True
        
        # Verificar que foi retomado
        lote_info = service.lotes_ativos[lote_id]
        assert lote_info['status'] == LoteStatus.EM_EXECUCAO
    
    def test_retomar_lote_nao_pausado(self, service, sample_config, sample_execucoes):
        """Testa retomada de lote não pausado."""
        user_id = "user_resume_erro"
        
        lote_id = service.criar_lote(
            execucoes=sample_execucoes,
            config=sample_config,
            user_id=user_id
        )
        
        # Tentar retomar lote pendente
        sucesso = service.retomar_lote(lote_id)
        assert sucesso is False
    
    def test_listar_lotes_vazio(self, service):
        """Testa listagem de lotes quando não há nenhum."""
        lotes = service.listar_lotes()
        assert lotes == []
    
    def test_listar_lotes_com_filtros(self, service, sample_config, sample_execucoes):
        """Testa listagem de lotes com filtros."""
        user_id_1 = "user_111"
        user_id_2 = "user_222"
        
        # Criar lotes para diferentes usuários
        lote_id_1 = service.criar_lote(
            execucoes=sample_execucoes,
            config=sample_config,
            user_id=user_id_1
        )
        
        lote_id_2 = service.criar_lote(
            execucoes=sample_execucoes,
            config=sample_config,
            user_id=user_id_2
        )
        
        # Listar todos
        todos = service.listar_lotes()
        assert len(todos) == 2
        
        # Filtrar por usuário
        do_usuario_1 = service.listar_lotes(user_id=user_id_1)
        assert len(do_usuario_1) == 1
        assert do_usuario_1[0]['lote_id'] == lote_id_1
        
        # Filtrar por status
        pendentes = service.listar_lotes(status=LoteStatus.PENDENTE)
        assert len(pendentes) == 2
        assert all(l['status'] == 'pendente' for l in pendentes)
    
    def test_obter_estatisticas_vazio(self, service):
        """Testa obtenção de estatísticas quando não há lotes."""
        stats = service.obter_estatisticas()
        
        assert stats['lotes_ativos'] == 0
        assert stats['lotes_processados'] == 0
        assert stats['execucoes_processadas'] == 0
        assert stats['tempo_total_processamento'] == 0.0
        assert stats['taxa_sucesso_geral'] == 0.0
        assert 'status_por_lote' in stats
    
    def test_obter_estatisticas_com_lotes(self, service, sample_config, sample_execucoes):
        """Testa obtenção de estatísticas com lotes."""
        user_id = "user_stats"
        
        # Criar lote
        lote_id = service.criar_lote(
            execucoes=sample_execucoes,
            config=sample_config,
            user_id=user_id
        )
        
        # Simular algumas estatísticas
        service.stats['lotes_processados'] = 5
        service.stats['execucoes_processadas'] = 15
        service.stats['tempo_total_processamento'] = 120.5
        service.stats['taxa_sucesso_geral'] = 0.8
        
        stats = service.obter_estatisticas()
        
        assert stats['lotes_ativos'] == 1
        assert stats['lotes_processados'] == 5
        assert stats['execucoes_processadas'] == 15
        assert stats['tempo_total_processamento'] == 120.5
        assert stats['taxa_sucesso_geral'] == 0.8
        assert stats['status_por_lote']['pendente'] == 1
    
    def test_limpar_lotes_antigos(self, service, sample_config, sample_execucoes):
        """Testa limpeza de lotes antigos."""
        user_id = "user_cleanup"
        
        # Criar lote
        lote_id = service.criar_lote(
            execucoes=sample_execucoes,
            config=sample_config,
            user_id=user_id
        )
        
        # Verificar que lote existe
        assert lote_id in service.lotes_ativos
        
        # Simular lote antigo (8 dias atrás)
        lote_info = service.lotes_ativos[lote_id]
        lote_info['criado_em'] = datetime.now(timezone.utc) - timedelta(days=8)
        
        # Limpar lotes antigos (padrão 7 dias)
        service.limpar_lotes_antigos()
        
        # Verificar que lote foi removido
        assert lote_id not in service.lotes_ativos
    
    def test_simular_execucao(self, service):
        """Testa simulação de execução."""
        execucao = ExecucaoItem(
            id="test_exec_123",
            categoria_id=1,
            palavras_chave=["seo", "ads"],
            cluster="marketing_digital"
        )
        
        resultado = service._simular_execucao(execucao)
        
        assert resultado is not None
        assert resultado['palavras_chave_processadas'] == 2
        assert resultado['resultados_encontrados'] == 20
        assert resultado['tempo_processamento'] == 2.0
        assert resultado['cluster_usado'] == "marketing_digital"
        assert resultado['status'] == "sucesso"
    
    def test_processar_resultado_execucao(self, service):
        """Testa processamento de resultado de execução."""
        execucao = ExecucaoItem(
            id="test_exec_456",
            categoria_id=2,
            palavras_chave=["email marketing"],
            cluster="email_marketing"
        )
        
        resultado = {
            'palavras_chave_processadas': 1,
            'resultados_encontrados': 10,
            'tempo_processamento': 1.5,
            'cluster_usado': "email_marketing",
            'status': "sucesso"
        }
        
        # Mock do callback
        mock_callback = Mock()
        service.on_execucao_complete = mock_callback
        
        service._processar_resultado_execucao(execucao, resultado)
        
        assert execucao.resultado == resultado
        assert service.stats['execucoes_processadas'] == 1
        mock_callback.assert_called_once_with(execucao, resultado)
    
    def test_processar_erro_execucao(self, service):
        """Testa processamento de erro de execução."""
        execucao = ExecucaoItem(
            id="test_exec_789",
            categoria_id=3,
            palavras_chave=["content marketing"],
            cluster="content_marketing"
        )
        
        erro = "Erro de conexão com API"
        
        # Mock do callback
        mock_callback = Mock()
        service.on_error = mock_callback
        
        service._processar_erro_execucao(execucao, erro)
        
        assert execucao.erro == erro
        mock_callback.assert_called_once()
    
    def test_atualizar_progresso_lote(self, service, sample_config, sample_execucoes):
        """Testa atualização de progresso do lote."""
        user_id = "user_progress"
        
        lote_id = service.criar_lote(
            execucoes=sample_execucoes,
            config=sample_config,
            user_id=user_id
        )
        
        lote_info = service.lotes_ativos[lote_id]
        
        # Verificar progresso inicial
        assert lote_info['progresso'] == 0
        
        # Simular algumas execuções concluídas
        lote_info['execucoes'][0].status = ExecucaoStatus.CONCLUIDA
        lote_info['execucoes'][1].status = ExecucaoStatus.FALHOU
        
        service._atualizar_progresso_lote(lote_info)
        
        # Verificar progresso atualizado (2 de 3 = 66.67%)
        assert lote_info['progresso'] == pytest.approx(66.67, rel=0.01)
    
    def test_finalizar_lote_sucesso(self, service, sample_config, sample_execucoes):
        """Testa finalização de lote com sucesso."""
        user_id = "user_finalize"
        
        lote_id = service.criar_lote(
            execucoes=sample_execucoes,
            config=sample_config,
            user_id=user_id
        )
        
        lote_info = service.lotes_ativos[lote_id]
        
        # Simular execuções
        lote_info['inicio_processamento'] = datetime.now(timezone.utc) - timedelta(minutes=5)
        lote_info['execucoes'][0].status = ExecucaoStatus.CONCLUIDA
        lote_info['execucoes'][1].status = ExecucaoStatus.CONCLUIDA
        lote_info['execucoes'][2].status = ExecucaoStatus.FALHOU
        
        # Mock do callback
        mock_callback = Mock()
        service.on_lote_complete = mock_callback
        
        service._finalizar_lote(lote_info)
        
        # Verificar que lote foi finalizado
        assert lote_info['status'] == LoteStatus.CONCLUIDO  # Taxa sucesso > 50%
        assert lote_info['fim_processamento'] is not None
        assert lote_info['resultado'] is not None
        
        # Verificar resultado
        resultado = lote_info['resultado']
        assert resultado['lote_id'] == lote_id
        assert resultado['total_execucoes'] == 3
        assert resultado['execucoes_concluidas'] == 2
        assert resultado['execucoes_falharam'] == 1
        assert resultado['execucoes_canceladas'] == 0
        assert resultado['taxa_sucesso'] == pytest.approx(0.67, rel=0.01)
        
        # Verificar callback
        mock_callback.assert_called_once()
    
    def test_finalizar_lote_falha(self, service, sample_config, sample_execucoes):
        """Testa finalização de lote com falha."""
        user_id = "user_finalize_fail"
        
        lote_id = service.criar_lote(
            execucoes=sample_execucoes,
            config=sample_config,
            user_id=user_id
        )
        
        lote_info = service.lotes_ativos[lote_id]
        
        # Simular execuções com maioria falhando
        lote_info['inicio_processamento'] = datetime.now(timezone.utc) - timedelta(minutes=5)
        lote_info['execucoes'][0].status = ExecucaoStatus.FALHOU
        lote_info['execucoes'][1].status = ExecucaoStatus.FALHOU
        lote_info['execucoes'][2].status = ExecucaoStatus.CONCLUIDA
        
        service._finalizar_lote(lote_info)
        
        # Verificar que lote foi marcado como falhou (taxa sucesso < 50%)
        assert lote_info['status'] == LoteStatus.FALHOU
    
    def test_executar_item_sucesso(self, service, sample_config):
        """Testa execução de item individual com sucesso."""
        execucao = ExecucaoItem(
            id="test_item_123",
            categoria_id=1,
            palavras_chave=["seo", "ads"],
            cluster="marketing_digital"
        )
        
        resultado = service._executar_item(execucao, sample_config)
        
        assert resultado is not None
        assert execucao.status == ExecucaoStatus.CONCLUIDA
        assert execucao.resultado == resultado
        assert execucao.tempo_inicio is not None
        assert execucao.tempo_fim is not None
        assert execucao.tentativas == 0
        assert execucao.erro is None
    
    def test_executar_item_com_retry(self, service, sample_config):
        """Testa execução de item com retry."""
        execucao = ExecucaoItem(
            id="test_item_retry",
            categoria_id=2,
            palavras_chave=["email marketing"],
            cluster="email_marketing",
            max_tentativas=2
        )
        
        # Mock para simular falha na primeira tentativa
        with patch.object(service, '_simular_execucao', side_effect=[Exception("Erro temporário"), {"status": "sucesso"}]):
            try:
                service._executar_item(execucao, sample_config)
            except Exception:
                pass
            
            # Segunda tentativa
            resultado = service._executar_item(execucao, sample_config)
            
            assert resultado is not None
            assert execucao.status == ExecucaoStatus.CONCLUIDA
            assert execucao.tentativas == 1
    
    def test_executar_item_max_retries_exceeded(self, service, sample_config):
        """Testa execução de item que excede máximo de tentativas."""
        execucao = ExecucaoItem(
            id="test_item_max_retries",
            categoria_id=3,
            palavras_chave=["content marketing"],
            cluster="content_marketing",
            max_tentativas=2
        )
        
        # Mock para simular falha persistente
        with patch.object(service, '_simular_execucao', side_effect=Exception("Erro persistente")):
            # Primeira tentativa
            try:
                service._executar_item(execucao, sample_config)
            except Exception:
                pass
            
            # Segunda tentativa (última)
            try:
                service._executar_item(execucao, sample_config)
            except Exception:
                pass
            
            assert execucao.status == ExecucaoStatus.FALHOU
            assert execucao.tentativas == 2
            assert execucao.erro == "Erro persistente"
    
    def test_init_lote_service_global(self):
        """Testa inicialização do serviço global."""
        config = {'max_workers': 8}
        
        service = init_lote_service(config)
        
        assert service is not None
        assert isinstance(service, LoteExecucaoService)
        assert service.config == config
    
    def test_get_lote_service_global(self):
        """Testa obtenção do serviço global."""
        config = {'max_workers': 6}
        init_lote_service(config)
        
        service = get_lote_service()
        
        assert service is not None
        assert isinstance(service, LoteExecucaoService)
        assert service.config == config 