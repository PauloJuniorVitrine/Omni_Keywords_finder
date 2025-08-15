from typing import Dict, List, Optional, Any
"""
Testes Unitários - Orquestrador (Fase 1: Fundação Crítica)

Testes para validar a implementação dos componentes críticos:
- FluxoCompletoOrchestrator
- ProgressTracker  
- ErrorHandler
- Configurações

Tracing ID: TEST_ORCHESTRATOR_001_20241227
Versão: 1.0
Autor: IA-Cursor
"""

import pytest
import time
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from infrastructure.orchestrator.fluxo_completo_orchestrator import (
    FluxoCompletoOrchestrator,
    FluxoStatus,
    FluxoContext,
    obter_orchestrator,
    executar_fluxo_completo
)
from infrastructure.orchestrator.progress_tracker import (
    ProgressTracker,
    SessaoProgress,
    NichoProgress,
    EtapaProgress,
    EtapaStatus,
    EtapaType,
    obter_progress_tracker
)
from infrastructure.orchestrator.error_handler import (
    ErrorHandler,
    ErrorType,
    ErrorSeverity,
    CircuitBreakerState,
    obter_error_handler,
    with_error_handling,
    with_circuit_breaker_and_retry
)
from infrastructure.orchestrator.config import (
    OrchestratorConfig,
    NichoConfig,
    NichoType,
    ColetaConfig,
    ValidacaoConfig,
    ProcessamentoConfig,
    PreenchimentoConfig,
    ExportacaoConfig,
    obter_config
)


class TestFluxoCompletoOrchestrator:
    """Testes para o orquestrador principal."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.config = OrchestratorConfig()
        self.orchestrator = FluxoCompletoOrchestrator(self.config)
    
    def test_inicializacao(self):
        """Testa inicialização do orquestrador."""
        assert self.orchestrator.status == FluxoStatus.INICIANDO
        assert self.orchestrator.context is None
        assert self.orchestrator.config == self.config
        assert self.orchestrator.progress_tracker is not None
        assert self.orchestrator.error_handler is not None
    
    def test_iniciar_fluxo_sucesso(self):
        """Testa início bem-sucedido do fluxo."""
        nichos = ["saude", "financas"]
        sessao_id = self.orchestrator.iniciar_fluxo(nichos)
        
        assert sessao_id is not None
        assert len(sessao_id) > 0
        assert self.orchestrator.status == FluxoStatus.EM_EXECUCAO
    
    def test_iniciar_fluxo_sem_nichos(self):
        """Testa erro ao iniciar fluxo sem nichos."""
        with pytest.raises(ValueError, match="Nenhum nicho especificado"):
            self.orchestrator.iniciar_fluxo([])
    
    def test_iniciar_fluxo_ja_em_execucao(self):
        """Testa erro ao tentar iniciar fluxo já em execução."""
        nichos = ["saude"]
        self.orchestrator.iniciar_fluxo(nichos)
        
        with pytest.raises(RuntimeError, match="Fluxo já está em execução"):
            self.orchestrator.iniciar_fluxo(nichos)
    
    def test_pausar_retomar_fluxo(self):
        """Testa pausar e retomar fluxo."""
        nichos = ["saude"]
        self.orchestrator.iniciar_fluxo(nichos)
        
        self.orchestrator.pausar_fluxo()
        assert self.orchestrator.status == FluxoStatus.PAUSADO
        
        self.orchestrator.retomar_fluxo()
        assert self.orchestrator.status == FluxoStatus.EM_EXECUCAO
    
    def test_cancelar_fluxo(self):
        """Testa cancelamento do fluxo."""
        nichos = ["saude"]
        self.orchestrator.iniciar_fluxo(nichos)
        
        self.orchestrator.cancelar_fluxo()
        assert self.orchestrator.status == FluxoStatus.CANCELADO
    
    def test_obter_status(self):
        """Testa obtenção do status do fluxo."""
        nichos = ["saude"]
        sessao_id = self.orchestrator.iniciar_fluxo(nichos)
        
        status = self.orchestrator.obter_status()
        
        assert "status" in status
        assert "sessao_id" in status
        assert "nichos" in status
        assert status["sessao_id"] == sessao_id
    
    def test_configurar_callbacks(self):
        """Testa configuração de callbacks."""
        on_progress = Mock()
        on_error = Mock()
        on_complete = Mock()
        
        self.orchestrator.configurar_callbacks(
            on_progress=on_progress,
            on_error=on_error,
            on_complete=on_complete
        )
        
        assert self.orchestrator.on_progress == on_progress
        assert self.orchestrator.on_error == on_error
        assert self.orchestrator.on_complete == on_complete


class TestProgressTracker:
    """Testes para o sistema de progress tracking."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.temp_dir = tempfile.mkdtemp()
        self.tracker = ProgressTracker(diretorio_persistencia=self.temp_dir)
    
    def teardown_method(self):
        """Cleanup após cada teste."""
        shutil.rmtree(self.temp_dir)
    
    def test_inicializacao(self):
        """Testa inicialização do progress tracker."""
        assert self.tracker.diretorio_persistencia == self.temp_dir
        assert self.tracker.sessao_atual is None
        assert self.tracker.lock is not None
    
    def test_iniciar_sessao(self):
        """Testa início de nova sessão."""
        config = {"nichos": ["saude"], "config": {}}
        sessao = self.tracker.iniciar_sessao("test_session", config)
        
        assert sessao.sessao_id == "test_session"
        assert sessao.config == config
        assert self.tracker.sessao_atual == sessao
    
    def test_adicionar_nicho(self):
        """Testa adição de nicho à sessão."""
        self.tracker.iniciar_sessao("test_session", {})
        nicho = self.tracker.adicionar_nicho("saude")
        
        assert nicho.nome_nicho == "saude"
        assert nicho.status == EtapaStatus.PENDENTE
        assert len(nicho.etapas) == 5  # 5 etapas padrão
    
    def test_iniciar_etapa(self):
        """Testa início de etapa."""
        self.tracker.iniciar_sessao("test_session", {})
        self.tracker.adicionar_nicho("saude")
        
        etapa = self.tracker.iniciar_etapa("saude", "coleta")
        
        assert etapa.status == EtapaStatus.EM_EXECUCAO
        assert etapa.inicio_timestamp is not None
    
    def test_atualizar_progresso_etapa(self):
        """Testa atualização de progresso de etapa."""
        self.tracker.iniciar_sessao("test_session", {})
        self.tracker.adicionar_nicho("saude")
        self.tracker.iniciar_etapa("saude", "coleta")
        
        etapa = self.tracker.atualizar_progresso_etapa(
            "saude", "coleta", 50, 100, "Processando..."
        )
        
        assert etapa.progresso_atual == 50
        assert etapa.total_itens == 100
        assert etapa.percentual == 50.0
        assert etapa.mensagem == "Processando..."
    
    def test_concluir_etapa(self):
        """Testa conclusão de etapa."""
        self.tracker.iniciar_sessao("test_session", {})
        self.tracker.adicionar_nicho("saude")
        self.tracker.iniciar_etapa("saude", "coleta")
        
        etapa = self.tracker.concluir_etapa("saude", "coleta", True)
        
        assert etapa.status == EtapaStatus.CONCLUIDA
        assert etapa.fim_timestamp is not None
    
    def test_concluir_etapa_com_erro(self):
        """Testa conclusão de etapa com erro."""
        self.tracker.iniciar_sessao("test_session", {})
        self.tracker.adicionar_nicho("saude")
        self.tracker.iniciar_etapa("saude", "coleta")
        
        etapa = self.tracker.concluir_etapa(
            "saude", "coleta", False, "Erro de API"
        )
        
        assert etapa.status == EtapaStatus.FALHOU
        assert etapa.erro == "Erro de API"
    
    def test_concluir_nicho(self):
        """Testa conclusão de nicho."""
        self.tracker.iniciar_sessao("test_session", {})
        nicho = self.tracker.adicionar_nicho("saude")
        
        nicho_concluido = self.tracker.concluir_nicho("saude", True)
        
        assert nicho_concluido.status == EtapaStatus.CONCLUIDA
        assert nicho_concluido.fim_timestamp is not None
    
    def test_concluir_sessao(self):
        """Testa conclusão de sessão."""
        sessao = self.tracker.iniciar_sessao("test_session", {})
        
        sessao_concluida = self.tracker.concluir_sessao(True)
        
        assert sessao_concluida.fim_timestamp is not None
        assert self.tracker.sessao_atual is None
    
    def test_carregar_sessao(self):
        """Testa carregamento de sessão persistida."""
        self.tracker.iniciar_sessao("test_session", {})
        self.tracker.adicionar_nicho("saude")
        self.tracker._persistir_sessao()
        
        # Criar novo tracker e carregar sessão
        novo_tracker = ProgressTracker(diretorio_persistencia=self.temp_dir)
        sessao_carregada = novo_tracker.carregar_sessao("test_session")
        
        assert sessao_carregada is not None
        assert sessao_carregada.sessao_id == "test_session"
        assert "saude" in sessao_carregada.nichos
    
    def test_limpar_sessoes_antigas(self):
        """Testa limpeza de sessões antigas."""
        self.tracker.iniciar_sessao("test_session", {})
        self.tracker._persistir_sessao()
        
        # Simular sessão antiga
        arquivo_sessao = Path(self.temp_dir) / "test_session.json"
        arquivo_sessao.touch()
        
        self.tracker.limpar_sessoes_antigas(dias=0)  # Limpar todas
        
        assert not arquivo_sessao.exists()


class TestErrorHandler:
    """Testes para o sistema de tratamento de erros."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.error_handler = ErrorHandler()
    
    def test_inicializacao(self):
        """Testa inicialização do error handler."""
        assert self.error_handler.circuit_breakers == {}
        assert self.error_handler.error_history == {}
        assert self.error_handler.lock is not None
    
    def test_register_circuit_breaker(self):
        """Testa registro de circuit breaker."""
        circuit_breaker = self.error_handler.register_circuit_breaker(
            "test_api", threshold=3, timeout_seconds=30
        )
        
        assert circuit_breaker.name == "test_api"
        assert circuit_breaker.threshold == 3
        assert circuit_breaker.timeout_seconds == 30
        assert circuit_breaker.state == "CLOSED"
        assert "test_api" in self.error_handler.circuit_breakers
    
    def test_circuit_breaker_should_allow_request(self):
        """Testa lógica do circuit breaker."""
        circuit_breaker = self.error_handler.register_circuit_breaker("test_api")
        
        # Estado CLOSED deve permitir requisições
        assert circuit_breaker.should_allow_request() is True
        
        # Simular falhas para abrir circuit breaker
        for _ in range(5):
            circuit_breaker.on_failure()
        
        # Estado OPEN não deve permitir requisições
        assert circuit_breaker.should_allow_request() is False
    
    def test_circuit_breaker_half_open(self):
        """Testa transição para estado HALF_OPEN."""
        circuit_breaker = self.error_handler.register_circuit_breaker(
            "test_api", threshold=1, timeout_seconds=1
        )
        
        # Falhar uma vez para abrir
        circuit_breaker.on_failure()
        assert circuit_breaker.state == "OPEN"
        
        # Aguardar timeout
        time.sleep(1.1)
        
        # Deve permitir uma requisição (HALF_OPEN)
        assert circuit_breaker.should_allow_request() is True
        assert circuit_breaker.state == "HALF_OPEN"
    
    def test_circuit_breaker_success_recovery(self):
        """Testa recuperação do circuit breaker com sucessos."""
        circuit_breaker = self.error_handler.register_circuit_breaker(
            "test_api", threshold=1, timeout_seconds=1
        )
        
        # Falhar para abrir
        circuit_breaker.on_failure()
        time.sleep(1.1)  # Aguardar timeout
        
        # Sucessos devem fechar o circuit breaker
        for _ in range(2):
            circuit_breaker.on_success()
        
        assert circuit_breaker.state == "CLOSED"
    
    def test_with_circuit_breaker_decorator(self):
        """Testa decorator de circuit breaker."""
        @self.error_handler.with_circuit_breaker("test_api", threshold=1)
        def test_function():
            raise Exception("Test error")
        
        # Primeira chamada deve falhar
        with pytest.raises(Exception):
            test_function()
        
        # Segunda chamada deve ser bloqueada pelo circuit breaker
        with pytest.raises(Exception, match="Circuit breaker 'test_api' está aberto"):
            test_function()
    
    def test_with_retry_decorator(self):
        """Testa decorator de retry."""
        call_count = 0
        
        @self.error_handler.with_retry(max_retries=3, base_delay=0.1)
        def test_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary error")
            return "success"
        
        result = test_function()
        
        assert result == "success"
        assert call_count == 3
    
    def test_handle_error(self):
        """Testa tratamento de erro."""
        error = Exception("Test error")
        error_info = self.error_handler.handle_error(
            error, ErrorType.NETWORK, ErrorSeverity.HIGH, {"context": "test"}
        )
        
        assert error_info.error_type == ErrorType.NETWORK
        assert error_info.severity == ErrorSeverity.HIGH
        assert error_info.message == "Test error"
        assert error_info.context == {"context": "test"}
    
    def test_classify_error(self):
        """Testa classificação automática de erros."""
        # Erro de rede
        network_error = ConnectionError("Connection failed")
        error_type, severity = self.error_handler.classify_error(network_error)
        assert error_type == ErrorType.NETWORK
        assert severity == ErrorSeverity.HIGH
        
        # Erro de validação
        validation_error = ValueError("Invalid input")
        error_type, severity = self.error_handler.classify_error(validation_error)
        assert error_type == ErrorType.VALIDATION
        assert severity == ErrorSeverity.MEDIUM
    
    def test_safe_execute(self):
        """Testa execução segura de função."""
        def success_function():
            return "success"
        
        def failing_function():
            raise Exception("Test error")
        
        # Função que sucede
        result = self.error_handler.safe_execute(success_function)
        assert result == "success"
        
        # Função que falha
        with pytest.raises(Exception):
            self.error_handler.safe_execute(failing_function)
    
    def test_get_error_stats(self):
        """Testa obtenção de estatísticas de erro."""
        error = Exception("Test error")
        self.error_handler.handle_error(error, ErrorType.NETWORK, ErrorSeverity.HIGH)
        
        stats = self.error_handler.get_error_stats()
        
        assert "total_errors" in stats
        assert "errors_by_type" in stats
        assert "errors_by_severity" in stats
        assert stats["total_errors"] > 0


class TestOrchestratorConfig:
    """Testes para as configurações do orquestrador."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.config = OrchestratorConfig()
    
    def test_inicializacao(self):
        """Testa inicialização das configurações."""
        assert self.config.tracing_id == "ORCHESTRATOR_001_20241227"
        assert self.config.modo_debug is False
        assert self.config.log_level == "INFO"
        assert self.config.max_nichos_concorrentes == 1
        assert len(self.config.nichos) > 0
    
    def test_carregar_configuracoes_padrao(self):
        """Testa carregamento de configurações padrão."""
        config = OrchestratorConfig()
        
        assert "saude" in config.nichos
        assert "financas" in config.nichos
        assert "tecnologia" in config.nichos
        
        nicho_saude = config.nichos["saude"]
        assert nicho_saude.nome == "Saúde e Bem-estar"
        assert nicho_saude.tipo == NichoType.SAUDE
        assert len(nicho_saude.keywords_semente) > 0
    
    def test_obter_config_nicho(self):
        """Testa obtenção de configuração de nicho."""
        config_nicho = self.config.obter_config_nicho("saude")
        
        assert config_nicho.nome == "Saúde e Bem-estar"
        assert config_nicho.tipo == NichoType.SAUDE
    
    def test_obter_config_nicho_inexistente(self):
        """Testa erro ao obter nicho inexistente."""
        with pytest.raises(ValueError, match="Nicho 'inexistente' não encontrado"):
            self.config.obter_config_nicho("inexistente")
    
    def test_listar_nichos_disponiveis(self):
        """Testa listagem de nichos disponíveis."""
        nichos = self.config.listar_nichos_disponiveis()
        
        assert "saude" in nichos
        assert "financas" in nichos
        assert "tecnologia" in nichos
    
    def test_adicionar_nicho(self):
        """Testa adição de novo nicho."""
        novo_nicho = NichoConfig(
            nome="Teste",
            tipo=NichoType.EDUCACAO,
            keywords_semente=["teste", "educação"]
        )
        
        self.config.adicionar_nicho("teste", novo_nicho)
        
        assert "teste" in self.config.nichos
        assert self.config.nichos["teste"] == novo_nicho
    
    def test_remover_nicho(self):
        """Testa remoção de nicho."""
        self.config.remover_nicho("saude")
        
        assert "saude" not in self.config.nichos
    
    def test_validacao_configuracoes(self):
        """Testa validação de configurações."""
        # Configuração válida
        config_valida = OrchestratorConfig()
        assert config_valida.nichos is not None
        
        # Configuração inválida (sem nichos)
        config_invalida = OrchestratorConfig()
        config_invalida.nichos = {}
        
        with pytest.raises(ValueError, match="Pelo menos um nicho deve ser configurado"):
            config_invalida._validar_configuracoes()


class TestIntegration:
    """Testes de integração entre componentes."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.config = OrchestratorConfig()
        self.orchestrator = FluxoCompletoOrchestrator(self.config)
        self.progress_tracker = obter_progress_tracker()
        self.error_handler = obter_error_handler()
    
    def test_integracao_orchestrator_progress_tracker(self):
        """Testa integração entre orquestrador e progress tracker."""
        nichos = ["saude"]
        sessao_id = self.orchestrator.iniciar_fluxo(nichos)
        
        # Verificar se progress tracker foi atualizado
        progress = self.progress_tracker.obter_progresso_atual()
        assert progress is not None
        assert progress.sessao_id == sessao_id
        assert "saude" in progress.nichos
    
    def test_integracao_error_handler_circuit_breaker(self):
        """Testa integração do error handler com circuit breaker."""
        # Registrar circuit breaker
        circuit_breaker = self.error_handler.register_circuit_breaker("test_api")
        
        # Simular falhas
        for _ in range(5):
            circuit_breaker.on_failure()
        
        # Verificar se circuit breaker está aberto
        assert circuit_breaker.state == "OPEN"
        assert circuit_breaker.should_allow_request() is False
    
    def test_fluxo_completo_simulado(self):
        """Testa fluxo completo simulado."""
        nichos = ["saude"]
        
        # Configurar callbacks para monitorar progresso
        progress_calls = []
        error_calls = []
        complete_calls = []
        
        def on_progress(nicho, etapa, progresso):
            progress_calls.append((nicho, etapa, progresso))
        
        def on_error(nicho, erro):
            error_calls.append((nicho, erro))
        
        def on_complete():
            complete_calls.append(True)
        
        self.orchestrator.configurar_callbacks(
            on_progress=on_progress,
            on_error=on_error,
            on_complete=on_complete
        )
        
        # Executar fluxo
        sessao_id = self.orchestrator.iniciar_fluxo(nichos)
        
        # Aguardar conclusão (simulado)
        time.sleep(0.1)
        
        # Verificar se callbacks foram chamados
        assert len(progress_calls) > 0
        assert len(complete_calls) > 0 or len(error_calls) > 0


class TestUtils:
    """Testes para funções utilitárias."""
    
    def test_obter_orchestrator(self):
        """Testa função utilitária para obter orquestrador."""
        orchestrator = obter_orchestrator()
        
        assert isinstance(orchestrator, FluxoCompletoOrchestrator)
        assert orchestrator.config is not None
    
    def test_obter_progress_tracker(self):
        """Testa função utilitária para obter progress tracker."""
        tracker = obter_progress_tracker()
        
        assert isinstance(tracker, ProgressTracker)
    
    def test_obter_error_handler(self):
        """Testa função utilitária para obter error handler."""
        handler = obter_error_handler()
        
        assert isinstance(handler, ErrorHandler)
    
    def test_obter_config(self):
        """Testa função utilitária para obter configuração."""
        config = obter_config()
        
        assert isinstance(config, OrchestratorConfig)
        assert len(config.nichos) > 0
    
    def test_executar_fluxo_completo(self):
        """Testa função utilitária para executar fluxo completo."""
        nichos = ["saude"]
        sessao_id = executar_fluxo_completo(nichos)
        
        assert sessao_id is not None
        assert len(sessao_id) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-value"]) 