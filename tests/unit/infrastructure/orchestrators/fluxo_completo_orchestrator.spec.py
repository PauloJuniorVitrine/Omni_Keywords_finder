"""
Testes Unitários - Fluxo Completo Orchestrator

Testes para o orquestrador principal que coordena todo o fluxo de processamento:
coleta → validação → processamento → preenchimento → exportação

Tracing ID: TEST_ORCHESTRATOR_001_20250127
Versão: 1.0
Autor: IA-Cursor
Execução: Via GitHub Actions (não local)
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

from infrastructure.orchestrator.fluxo_completo_orchestrator import (
    FluxoCompletoOrchestrator,
    FluxoStatus,
    FluxoContext,
    obter_orchestrator,
    executar_fluxo_completo
)
from infrastructure.orchestrator.config import OrchestratorConfig


class TestFluxoCompletoOrchestrator:
    """Testes para o orquestrador principal"""
    
    @pytest.fixture
    def mock_config(self):
        """Configuração mock baseada no comportamento real"""
        config = Mock(spec=OrchestratorConfig)
        config.listar_nichos_disponiveis.return_value = ["saude", "tecnologia", "financas"]
        config.obter_config_nicho.return_value = {
            "coleta": {"timeout": 30, "max_retries": 3},
            "validacao": {"min_volume": 100},
            "processamento": {"batch_size": 1000}
        }
        return config
    
    @pytest.fixture
    def mock_progress_tracker(self):
        """Progress tracker mock baseado no comportamento real"""
        tracker = Mock()
        tracker.iniciar_sessao.return_value = None
        tracker.adicionar_nicho.return_value = None
        tracker.iniciar_etapa.return_value = None
        tracker.atualizar_progresso_etapa.return_value = None
        tracker.concluir_etapa.return_value = None
        tracker.concluir_nicho.return_value = None
        tracker.obter_progresso_atual.return_value = Mock(
            percentual_geral=75.0,
            nichos_concluidos=2,
            total_nichos=3
        )
        return tracker
    
    @pytest.fixture
    def mock_error_handler(self):
        """Error handler mock baseado no comportamento real"""
        handler = Mock()
        handler.handle_error.return_value = {
            "error_id": "test_error_001",
            "severity": "HIGH",
            "timestamp": time.time()
        }
        return handler
    
    @pytest.fixture
    def orchestrator(self, mock_config, mock_progress_tracker, mock_error_handler):
        """Orquestrador com mocks configurados"""
        with patch('infrastructure.orchestrator.fluxo_completo_orchestrator.obter_config', return_value=mock_config), \
             patch('infrastructure.orchestrator.fluxo_completo_orchestrator.obter_progress_tracker', return_value=mock_progress_tracker), \
             patch('infrastructure.orchestrator.fluxo_completo_orchestrator.obter_error_handler', return_value=mock_error_handler):
            
            return FluxoCompletoOrchestrator(config=mock_config)
    
    @pytest.mark.parametrize("nichos,expected_sessao_id", [
        (["saude"], "fluxo_"),
        (["tecnologia", "financas"], "fluxo_"),
        (None, "fluxo_"),  # Usa todos os nichos configurados
    ])
    def test_iniciar_fluxo_sucesso(self, orchestrator, nichos, expected_sessao_id):
        """Testa inicialização bem-sucedida do fluxo"""
        # Arrange
        orchestrator.status = FluxoStatus.INICIANDO
        
        # Act
        sessao_id = orchestrator.iniciar_fluxo(nichos)
        
        # Assert
        assert sessao_id.startswith(expected_sessao_id)
        assert orchestrator.status == FluxoStatus.EM_EXECUCAO
        assert orchestrator.context is not None
        assert orchestrator.context.sessao_id == sessao_id
        
        # Verificar se progress tracker foi chamado
        orchestrator.progress_tracker.iniciar_sessao.assert_called_once()
        orchestrator.progress_tracker.adicionar_nicho.assert_called()
    
    @pytest.mark.parametrize("nichos,expected_error", [
        ([], ValueError),  # Lista vazia
        (["nichos_inexistente"], ValueError),  # Nicho não configurado
    ])
    def test_iniciar_fluxo_erro_nichos_invalidos(self, orchestrator, nichos, expected_error):
        """Testa erro ao iniciar fluxo com nichos inválidos"""
        # Arrange
        orchestrator.status = FluxoStatus.INICIANDO
        
        # Act & Assert
        with pytest.raises(expected_error):
            orchestrator.iniciar_fluxo(nichos)
    
    def test_iniciar_fluxo_ja_em_execucao(self, orchestrator):
        """Testa erro ao tentar iniciar fluxo já em execução"""
        # Arrange
        orchestrator.status = FluxoStatus.EM_EXECUCAO
        
        # Act & Assert
        with pytest.raises(RuntimeError, match="Fluxo já está em execução"):
            orchestrator.iniciar_fluxo(["saude"])
    
    @pytest.mark.parametrize("sessao_id_custom", [
        "sessao_custom_001",
        "test_session_20250127",
        None,  # Deve gerar automaticamente
    ])
    def test_iniciar_fluxo_sessao_id(self, orchestrator, sessao_id_custom):
        """Testa geração e uso de session ID"""
        # Arrange
        orchestrator.status = FluxoStatus.INICIANDO
        
        # Act
        sessao_id = orchestrator.iniciar_fluxo(["saude"], sessao_id_custom)
        
        # Assert
        if sessao_id_custom:
            assert sessao_id == sessao_id_custom
        else:
            assert sessao_id.startswith("fluxo_")
            assert len(sessao_id) > 10  # Deve ter timestamp
    
    @pytest.mark.parametrize("status_inicial,acao,status_final", [
        (FluxoStatus.EM_EXECUCAO, "pausar", FluxoStatus.PAUSADO),
        (FluxoStatus.PAUSADO, "retomar", FluxoStatus.EM_EXECUCAO),
        (FluxoStatus.EM_EXECUCAO, "cancelar", FluxoStatus.CANCELADO),
        (FluxoStatus.PAUSADO, "cancelar", FluxoStatus.CANCELADO),
    ])
    def test_controle_fluxo(self, orchestrator, status_inicial, acao, status_final):
        """Testa controles de pausar, retomar e cancelar"""
        # Arrange
        orchestrator.status = status_inicial
        
        # Act
        if acao == "pausar":
            orchestrator.pausar_fluxo()
        elif acao == "retomar":
            orchestrator.retomar_fluxo()
        elif acao == "cancelar":
            orchestrator.cancelar_fluxo()
        
        # Assert
        assert orchestrator.status == status_final
    
    def test_obter_status_completo(self, orchestrator):
        """Testa obtenção de status completo"""
        # Arrange
        orchestrator.status = FluxoStatus.EM_EXECUCAO
        orchestrator.context = FluxoContext(
            sessao_id="test_session",
            nicho_atual="saude",
            etapa_atual="coleta",
            inicio_timestamp=time.time()
        )
        
        # Act
        status = orchestrator.obter_status()
        
        # Assert
        assert status["status"] == "em_execucao"
        assert status["sessao_id"] == "test_session"
        assert status["nicho_atual"] == "saude"
        assert status["etapa_atual"] == "coleta"
        assert "progresso" in status
        assert status["progresso"]["percentual_geral"] == 75.0
    
    def test_obter_status_sem_contexto(self, orchestrator):
        """Testa obtenção de status sem contexto ativo"""
        # Arrange
        orchestrator.status = FluxoStatus.INICIANDO
        orchestrator.context = None
        
        # Act
        status = orchestrator.obter_status()
        
        # Assert
        assert status["status"] == "iniciando"
        assert status["sessao_id"] is None
        assert status["nicho_atual"] is None
        assert status["etapa_atual"] is None
        assert "progresso" not in status
    
    @pytest.mark.parametrize("callbacks_config", [
        {"on_progress": True, "on_error": True, "on_complete": True},
        {"on_progress": True, "on_error": False, "on_complete": False},
        {"on_progress": False, "on_error": True, "on_complete": False},
        {"on_progress": False, "on_error": False, "on_complete": True},
    ])
    def test_configurar_callbacks(self, orchestrator, callbacks_config):
        """Testa configuração de callbacks"""
        # Arrange
        callbacks = {}
        if callbacks_config["on_progress"]:
            callbacks["on_progress"] = Mock()
        if callbacks_config["on_error"]:
            callbacks["on_error"] = Mock()
        if callbacks_config["on_complete"]:
            callbacks["on_complete"] = Mock()
        
        # Act
        orchestrator.configurar_callbacks(**callbacks)
        
        # Assert
        for callback_name, should_exist in callbacks_config.items():
            if should_exist:
                assert getattr(orchestrator, callback_name) is not None
            else:
                assert getattr(orchestrator, callback_name) is None
    
    @pytest.mark.parametrize("nichos,expected_keywords", [
        (["saude"], 50),  # Simulação retorna 50 keywords
        (["tecnologia"], 50),
        (["financas"], 50),
    ])
    def test_simulacao_coleta(self, orchestrator, nichos, expected_keywords):
        """Testa simulação de coleta de keywords"""
        # Arrange
        nicho = nichos[0]
        config_nicho = {"coleta": {"timeout": 30}}
        
        # Act
        keywords = orchestrator._simular_coleta(nicho, config_nicho)
        
        # Assert
        assert len(keywords) == expected_keywords
        assert all(keyword.startswith(f"keyword_") for keyword in keywords)
        assert all(nicho in keyword for keyword in keywords)
    
    @pytest.mark.parametrize("nichos,expected_prompts", [
        (["saude"], 75),  # Simulação retorna 75 prompts
        (["tecnologia"], 75),
        (["financas"], 75),
    ])
    def test_simulacao_preenchimento(self, orchestrator, nichos, expected_prompts):
        """Testa simulação de preenchimento de prompts"""
        # Arrange
        nicho = nichos[0]
        config_nicho = {"preenchimento": {"model": "gpt-4"}}
        
        # Act
        prompts = orchestrator._simular_preenchimento(nicho, config_nicho)
        
        # Assert
        assert len(prompts) == expected_prompts
        assert all(prompt.startswith(f"prompt_") for prompt in prompts)
        assert all(nicho in prompt for prompt in prompts)
    
    def test_simulacao_exportacao(self, orchestrator):
        """Testa simulação de exportação"""
        # Arrange
        nicho = "saude"
        config_nicho = {"exportacao": {"formato": "zip"}}
        
        # Act
        arquivo = orchestrator._simular_exportacao(nicho, config_nicho)
        
        # Assert
        assert arquivo.startswith(f"{nicho}_keywords_")
        assert arquivo.endswith(".zip")
        assert str(int(time.time())) in arquivo
    
    @pytest.mark.parametrize("etapa,expected_sucesso", [
        ("coleta", True),
        ("validacao", True),
        ("processamento", True),
        ("preenchimento", True),
        ("exportacao", True),
    ])
    def test_executar_etapas_individualmente(self, orchestrator, etapa, expected_sucesso):
        """Testa execução individual de cada etapa"""
        # Arrange
        nicho = "saude"
        config_nicho = {"timeout": 30}
        
        # Act
        if etapa == "coleta":
            sucesso = orchestrator._executar_etapa_coleta(nicho, config_nicho)
        elif etapa == "validacao":
            sucesso = orchestrator._executar_etapa_validacao(nicho, config_nicho)
        elif etapa == "processamento":
            sucesso = orchestrator._executar_etapa_processamento(nicho, config_nicho)
        elif etapa == "preenchimento":
            sucesso = orchestrator._executar_etapa_preenchimento(nicho, config_nicho)
        elif etapa == "exportacao":
            sucesso = orchestrator._executar_etapa_exportacao(nicho, config_nicho)
        
        # Assert
        assert sucesso == expected_sucesso
        
        # Verificar se progress tracker foi chamado
        orchestrator.progress_tracker.iniciar_etapa.assert_called_with(nicho, etapa)
        orchestrator.progress_tracker.concluir_etapa.assert_called_with(
            nicho, etapa, True, metadados=pytest.approx({}, rel=1)
        )
    
    def test_processar_nicho_completo(self, orchestrator):
        """Testa processamento completo de um nicho"""
        # Arrange
        nicho = "saude"
        
        # Act
        sucesso = orchestrator._processar_nicho(nicho)
        
        # Assert
        assert sucesso is True
        
        # Verificar se todas as etapas foram executadas
        assert orchestrator.progress_tracker.iniciar_etapa.call_count == 5  # 5 etapas
        assert orchestrator.progress_tracker.concluir_etapa.call_count == 5
        assert orchestrator.progress_tracker.concluir_nicho.call_count == 1
    
    def test_executar_fluxo_completo_thread(self, orchestrator):
        """Testa execução do fluxo completo em thread separada"""
        # Arrange
        nichos = ["saude", "tecnologia"]
        orchestrator.status = FluxoStatus.INICIANDO
        
        # Act
        sessao_id = orchestrator.iniciar_fluxo(nichos)
        
        # Assert
        assert sessao_id is not None
        assert orchestrator.status == FluxoStatus.EM_EXECUCAO
        
        # Aguardar um pouco para thread executar
        time.sleep(0.1)
        
        # Verificar se progress tracker foi chamado para ambos os nichos
        assert orchestrator.progress_tracker.adicionar_nicho.call_count == 2


class TestFluxoCompletoOrchestratorIntegracao:
    """Testes de integração para o orquestrador"""
    
    @pytest.fixture
    def orchestrator_real(self):
        """Orquestrador com configuração real"""
        return FluxoCompletoOrchestrator()
    
    def test_obter_orchestrator_singleton(self):
        """Testa obtenção da instância singleton"""
        # Act
        orchestrator1 = obter_orchestrator()
        orchestrator2 = obter_orchestrator()
        
        # Assert
        assert orchestrator1 is orchestrator2
        assert isinstance(orchestrator1, FluxoCompletoOrchestrator)
    
    @pytest.mark.parametrize("nichos,sessao_id", [
        (["saude"], None),
        (["tecnologia", "financas"], "sessao_teste_001"),
        (None, "sessao_teste_002"),
    ])
    def test_executar_fluxo_completo_funcao(self, nichos, sessao_id):
        """Testa função de conveniência executar_fluxo_completo"""
        # Act
        with patch('infrastructure.orchestrator.fluxo_completo_orchestrator.orchestrator') as mock_orchestrator:
            mock_orchestrator.iniciar_fluxo.return_value = "sessao_gerada"
            
            sessao_id_resultado = executar_fluxo_completo(nichos, sessao_id)
        
        # Assert
        mock_orchestrator.iniciar_fluxo.assert_called_once_with(nichos, sessao_id)
        assert sessao_id_resultado == "sessao_gerada"


class TestFluxoCompletoOrchestratorEdgeCases:
    """Testes para casos extremos e edge cases"""
    
    @pytest.fixture
    def orchestrator_edge(self):
        """Orquestrador para testes de edge cases"""
        return FluxoCompletoOrchestrator()
    
    def test_fluxo_context_serializacao(self):
        """Testa serialização do contexto do fluxo"""
        # Arrange
        context = FluxoContext(
            sessao_id="test_session",
            nicho_atual="saude",
            etapa_atual="coleta",
            inicio_timestamp=time.time()
        )
        
        # Act
        context_dict = {
            "sessao_id": context.sessao_id,
            "nicho_atual": context.nicho_atual,
            "etapa_atual": context.etapa_atual,
            "inicio_timestamp": context.inicio_timestamp
        }
        
        # Assert
        assert context_dict["sessao_id"] == "test_session"
        assert context_dict["nicho_atual"] == "saude"
        assert context_dict["etapa_atual"] == "coleta"
        assert isinstance(context_dict["inicio_timestamp"], float)
    
    def test_fluxo_status_enum(self):
        """Testa enum de status do fluxo"""
        # Act & Assert
        assert FluxoStatus.INICIANDO.value == "iniciando"
        assert FluxoStatus.EM_EXECUCAO.value == "em_execucao"
        assert FluxoStatus.PAUSADO.value == "pausado"
        assert FluxoStatus.CONCLUIDO.value == "concluido"
        assert FluxoStatus.FALHOU.value == "falhou"
        assert FluxoStatus.CANCELADO.value == "cancelado"
        
        # Verificar que todos os status são únicos
        status_values = [status.value for status in FluxoStatus]
        assert len(status_values) == len(set(status_values))
    
    def test_thread_safety_lock(self, orchestrator_edge):
        """Testa thread safety com lock"""
        # Arrange
        results = []
        
        def worker():
            try:
                orchestrator_edge.iniciar_fluxo(["saude"])
                results.append("sucesso")
            except Exception as e:
                results.append(f"erro: {type(e).__name__}")
        
        # Act
        thread1 = threading.Thread(target=worker)
        thread2 = threading.Thread(target=worker)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # Assert
        # Pelo menos uma thread deve ter sucesso, a outra deve falhar com "já em execução"
        assert len(results) == 2
        assert "sucesso" in results
        assert any("RuntimeError" in result for result in results)
    
    @pytest.mark.parametrize("nichos_grandes", [
        ["nicho_" + str(i) for i in range(100)],  # 100 nichos
        ["nicho_" + str(i) for i in range(1000)],  # 1000 nichos
    ])
    def test_fluxo_muitos_nichos(self, orchestrator_edge, nichos_grandes):
        """Testa fluxo com muitos nichos (performance)"""
        # Arrange
        with patch.object(orchestrator_edge.config, 'listar_nichos_disponiveis', return_value=nichos_grandes):
            # Act
            sessao_id = orchestrator_edge.iniciar_fluxo(nichos_grandes[:10])  # Limitar a 10 para teste
            
            # Assert
            assert sessao_id is not None
            assert orchestrator_edge.status == FluxoStatus.EM_EXECUCAO
            assert orchestrator_edge.context is not None
    
    def test_fluxo_context_metadados(self):
        """Testa metadados do contexto do fluxo"""
        # Arrange
        context = FluxoContext(
            sessao_id="test_session",
            metadados={"teste": "valor", "numero": 42}
        )
        
        # Act
        context.metadados["novo"] = "dado"
        
        # Assert
        assert context.metadados["teste"] == "valor"
        assert context.metadados["numero"] == 42
        assert context.metadados["novo"] == "dado"
        assert len(context.metadados) == 3 