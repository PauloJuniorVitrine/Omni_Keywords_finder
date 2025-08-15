"""
Testes de Integração - Integration Bridge

Baseado no código real do sistema Omni Keywords Finder
para garantir que os testes sejam representativos.

Tracing ID: TEST_INTEGRATION_BRIDGE_001_20250127
"""

import pytest
import time
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime

# Importar módulos reais para teste
from infrastructure.integration.integration_bridge import IntegrationBridge, IntegrationResult
from infrastructure.integration.flow_coordinator import FlowCoordinator, FlowResult, FlowStep
from infrastructure.integration.module_connector import ModuleConnector, ConnectionStatus

# Importar mocks
from tests.mocks.mock_modules import (
    MockGoogleKeywordPlanner, MockGoogleSuggest, MockGoogleTrends,
    MockProcessadorOrquestrador, MockExportadorKeywords
)
from tests.mocks.mock_data import (
    MOCK_KEYWORDS, MOCK_COLETA_RESULT, MOCK_PROCESSAMENTO_RESULT,
    MOCK_EXPORTACAO_RESULT, MOCK_METRICS
)


class TestIntegrationBridge:
    """Testes para IntegrationBridge baseados no código real."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste."""
        # Mock dos módulos externos
        with patch('infrastructure.integration.integration_bridge.GoogleKeywordPlannerColetor', MockGoogleKeywordPlanner), \
             patch('infrastructure.integration.integration_bridge.GoogleSuggestColetor', MockGoogleSuggest), \
             patch('infrastructure.integration.integration_bridge.GoogleTrendsColetor', MockGoogleTrends), \
             patch('infrastructure.integration.integration_bridge.ProcessadorOrquestrador', MockProcessadorOrquestrador), \
             patch('infrastructure.integration.integration_bridge.ExportadorKeywords', MockExportadorKeywords):
            
            self.bridge = IntegrationBridge()
            yield
            # Cleanup se necessário
    
    def test_bridge_initialization(self):
        """Testa inicialização do bridge."""
        assert self.bridge is not None
        assert hasattr(self.bridge, 'tracing_id')
        assert hasattr(self.bridge, 'modules_initialized')
        assert hasattr(self.bridge, 'coletor')
        assert hasattr(self.bridge, 'processador')
        assert hasattr(self.bridge, 'exportador')
    
    def test_bridge_ready_status(self):
        """Testa status de prontidão do bridge."""
        # Mock para simular módulos inicializados
        self.bridge.modules_initialized = True
        self.bridge.coletor = {"base": Mock(), "google_planner": Mock()}
        self.bridge.processador = Mock()
        self.bridge.exportador = Mock()
        
        assert self.bridge.is_ready() is True
    
    def test_bridge_not_ready_status(self):
        """Testa status quando bridge não está pronto."""
        self.bridge.modules_initialized = False
        assert self.bridge.is_ready() is False
    
    def test_get_module_status(self):
        """Testa obtenção de status dos módulos."""
        status = self.bridge.get_module_status()
        
        assert isinstance(status, dict)
        assert "bridge_ready" in status
        assert "modules_initialized" in status
        assert "coletor_available" in status
        assert "processador_available" in status
        assert "exportador_available" in status
        assert "metrics" in status
    
    def test_execute_coleta_success(self):
        """Testa execução bem-sucedida de coleta."""
        # Mock para simular módulos prontos
        self.bridge.modules_initialized = True
        self.bridge.coletor = {"google_trends": MockGoogleTrends()}
        
        resultado = self.bridge.execute_coleta("teste", "tech")
        
        assert isinstance(resultado, IntegrationResult)
        assert resultado.success is True
        assert resultado.data is not None
        assert resultado.error is None
        assert resultado.execution_time >= 0
    
    def test_execute_coleta_bridge_not_ready(self):
        """Testa execução de coleta quando bridge não está pronto."""
        self.bridge.modules_initialized = False
        
        resultado = self.bridge.execute_coleta("teste", "tech")
        
        assert isinstance(resultado, IntegrationResult)
        assert resultado.success is False
        assert "Bridge não está pronto" in resultado.error
    
    def test_execute_processamento_success(self):
        """Testa execução bem-sucedida de processamento."""
        # Mock para simular módulos prontos
        self.bridge.modules_initialized = True
        self.bridge.processador = MockProcessadorOrquestrador()
        
        keywords = ["keyword1", "keyword2"]
        resultado = self.bridge.execute_processamento(keywords, "tech")
        
        assert isinstance(resultado, IntegrationResult)
        assert resultado.success is True
        assert resultado.data is not None
        assert resultado.error is None
        assert resultado.execution_time >= 0
    
    def test_execute_processamento_bridge_not_ready(self):
        """Testa execução de processamento quando bridge não está pronto."""
        self.bridge.modules_initialized = False
        
        keywords = ["keyword1", "keyword2"]
        resultado = self.bridge.execute_processamento(keywords, "tech")
        
        assert isinstance(resultado, IntegrationResult)
        assert resultado.success is False
        assert "Bridge não está pronto" in resultado.error
    
    def test_execute_exportacao_success(self):
        """Testa execução bem-sucedida de exportação."""
        # Mock para simular módulos prontos
        self.bridge.modules_initialized = True
        self.bridge.exportador = MockExportadorKeywords()
        
        keywords = ["keyword1", "keyword2"]
        resultado = self.bridge.execute_exportacao(keywords, "tech")
        
        assert isinstance(resultado, IntegrationResult)
        assert resultado.success is True
        assert resultado.data is not None
        assert resultado.error is None
        assert resultado.execution_time >= 0
    
    def test_execute_exportacao_bridge_not_ready(self):
        """Testa execução de exportação quando bridge não está pronto."""
        self.bridge.modules_initialized = False
        
        keywords = ["keyword1", "keyword2"]
        resultado = self.bridge.execute_exportacao(keywords, "tech")
        
        assert isinstance(resultado, IntegrationResult)
        assert resultado.success is False
        assert "Bridge não está pronto" in resultado.error
    
    def test_execute_fluxo_completo_success(self):
        """Testa execução bem-sucedida do fluxo completo."""
        # Mock para simular módulos prontos
        self.bridge.modules_initialized = True
        self.bridge.coletor = {"google_trends": MockGoogleTrends()}
        self.bridge.processador = MockProcessadorOrquestrador()
        self.bridge.exportador = MockExportadorKeywords()
        
        resultado = self.bridge.execute_fluxo_completo("teste", "tech")
        
        assert isinstance(resultado, dict)
        assert "tempo_total" in resultado
        assert "keywords_coletadas" in resultado
        assert "keywords_processadas" in resultado
        assert "arquivos_gerados" in resultado
        assert resultado["tempo_total"] >= 0
    
    def test_execute_fluxo_completo_bridge_not_ready(self):
        """Testa execução do fluxo completo quando bridge não está pronto."""
        self.bridge.modules_initialized = False
        
        resultado = self.bridge.execute_fluxo_completo("teste", "tech")
        
        assert isinstance(resultado, dict)
        assert "error" in resultado
        assert "Bridge não está pronto" in resultado["error"]
    
    def test_metrics_tracking(self):
        """Testa rastreamento de métricas."""
        # Simular algumas execuções
        self.bridge.modules_initialized = True
        self.bridge.coletor = {"google_trends": MockGoogleTrends()}
        
        # Executar coleta algumas vezes
        for i in range(3):
            self.bridge.execute_coleta(f"termo{i}", "tech")
        
        metrics = self.bridge.metrics
        assert metrics["total_integrations"] >= 3
        assert "last_success" in metrics
        assert metrics["successful_integrations"] >= 0
    
    def test_error_handling(self):
        """Testa tratamento de erros."""
        # Mock para simular erro
        with patch.object(self.bridge, '_initialize_modules', side_effect=Exception("Test error")):
            bridge_with_error = IntegrationBridge()
            
            assert bridge_with_error.modules_initialized is False
            assert bridge_with_error.is_ready() is False
    
    def test_tracing_id_generation(self):
        """Testa geração de tracing ID."""
        assert self.bridge.tracing_id is not None
        assert isinstance(self.bridge.tracing_id, str)
        assert len(self.bridge.tracing_id) > 0
        assert self.bridge.tracing_id.startswith("BRIDGE_")


class TestFlowCoordinator:
    """Testes para FlowCoordinator baseados no código real."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste."""
        with patch('infrastructure.integration.integration_bridge.GoogleKeywordPlannerColetor', MockGoogleKeywordPlanner), \
             patch('infrastructure.integration.integration_bridge.GoogleSuggestColetor', MockGoogleSuggest), \
             patch('infrastructure.integration.integration_bridge.GoogleTrendsColetor', MockGoogleTrends), \
             patch('infrastructure.integration.integration_bridge.ProcessadorOrquestrador', MockProcessadorOrquestrador), \
             patch('infrastructure.integration.integration_bridge.ExportadorKeywords', MockExportadorKeywords):
            
            self.coordinator = FlowCoordinator()
            yield
    
    def test_coordinator_initialization(self):
        """Testa inicialização do coordenador."""
        assert self.coordinator is not None
        assert hasattr(self.coordinator, 'tracing_id')
        assert hasattr(self.coordinator, 'bridge')
        assert hasattr(self.coordinator, 'flow_history')
    
    def test_execute_complete_flow_success(self):
        """Testa execução bem-sucedida do fluxo completo."""
        # Mock para simular bridge pronto
        self.coordinator.bridge.modules_initialized = True
        self.coordinator.bridge.coletor = {"google_trends": MockGoogleTrends()}
        self.coordinator.bridge.processador = MockProcessadorOrquestrador()
        self.coordinator.bridge.exportador = MockExportadorKeywords()
        
        resultado = self.coordinator.execute_complete_flow("teste", "tech")
        
        assert isinstance(resultado, FlowResult)
        assert resultado.success is True
        assert resultado.flow_id is not None
        assert resultado.termo == "teste"
        assert resultado.nicho == "tech"
        assert resultado.total_time >= 0
        assert resultado.keywords_coletadas > 0
        assert resultado.keywords_processadas > 0
        assert resultado.arquivos_gerados > 0
    
    def test_execute_complete_flow_bridge_not_ready(self):
        """Testa execução do fluxo quando bridge não está pronto."""
        self.coordinator.bridge.modules_initialized = False
        
        resultado = self.coordinator.execute_complete_flow("teste", "tech")
        
        assert isinstance(resultado, FlowResult)
        assert resultado.success is False
        assert resultado.error is not None
    
    def test_flow_steps_execution(self):
        """Testa execução de cada etapa do fluxo."""
        # Mock para simular bridge pronto
        self.coordinator.bridge.modules_initialized = True
        self.coordinator.bridge.coletor = {"google_trends": MockGoogleTrends()}
        self.coordinator.bridge.processador = MockProcessadorOrquestrador()
        self.coordinator.bridge.exportador = MockExportadorKeywords()
        
        # Executar fluxo
        resultado = self.coordinator.execute_complete_flow("teste", "tech")
        
        # Verificar etapas
        assert "coleta" in resultado.steps
        assert "processamento" in resultado.steps
        assert "exportacao" in resultado.steps
        
        # Verificar status das etapas
        for step_name, step in resultado.steps.items():
            assert step.status == "completed"
            assert step.start_time > 0
            assert step.end_time > 0
            assert step.result is not None
    
    def test_flow_history_tracking(self):
        """Testa rastreamento do histórico de fluxos."""
        # Executar alguns fluxos
        self.coordinator.bridge.modules_initialized = True
        self.coordinator.bridge.coletor = {"google_trends": MockGoogleTrends()}
        self.coordinator.bridge.processador = MockProcessadorOrquestrador()
        self.coordinator.bridge.exportador = MockExportadorKeywords()
        
        for i in range(2):
            self.coordinator.execute_complete_flow(f"termo{i}", "tech")
        
        assert len(self.coordinator.flow_history) >= 2
    
    def test_get_flow_status(self):
        """Testa obtenção de status do fluxo."""
        status = self.coordinator.get_flow_status()
        
        assert isinstance(status, dict)
        assert "total_flows" in status
        assert "successful_flows" in status
        assert "failed_flows" in status
        assert "last_flow_time" in status
    
    def test_get_bridge_status(self):
        """Testa obtenção de status do bridge."""
        status = self.coordinator.get_bridge_status()
        
        assert isinstance(status, dict)
        assert "bridge_ready" in status
        assert "modules_initialized" in status
    
    def test_reset_flow(self):
        """Testa reset do fluxo."""
        # Executar um fluxo primeiro
        self.coordinator.bridge.modules_initialized = True
        self.coordinator.bridge.coletor = {"google_trends": MockGoogleTrends()}
        self.coordinator.bridge.processador = MockProcessadorOrquestrador()
        self.coordinator.bridge.exportador = MockExportadorKeywords()
        
        self.coordinator.execute_complete_flow("teste", "tech")
        
        # Reset
        self.coordinator.reset_flow()
        
        assert len(self.coordinator.flow_history) == 0


class TestModuleConnector:
    """Testes para ModuleConnector baseados no código real."""
    
    def test_connector_initialization(self):
        """Testa inicialização do conector."""
        connector = ModuleConnector()
        
        assert connector is not None
        assert hasattr(connector, 'connections')
        assert hasattr(connector, 'health_checks')
    
    def test_connect_modules(self):
        """Testa conexão entre módulos."""
        connector = ModuleConnector()
        
        # Mock de módulos
        module1 = Mock()
        module2 = Mock()
        
        result = connector.connect_modules("module1", "module2", "test_connection")
        
        assert result.success is True
        assert "module1" in connector.connections
        assert "module2" in connector.connections["module1"]
    
    def test_check_connection_health(self):
        """Testa verificação de saúde da conexão."""
        connector = ModuleConnector()
        
        # Criar conexão
        connector.connect_modules("module1", "module2", "test_connection")
        
        health = connector.check_connection_health("module1", "module2")
        
        assert isinstance(health, dict)
        assert "status" in health
        assert "last_check" in health
    
    def test_get_connection_status(self):
        """Testa obtenção de status da conexão."""
        connector = ModuleConnector()
        
        # Criar conexão
        connector.connect_modules("module1", "module2", "test_connection")
        
        status = connector.get_connection_status("module1", "module2")
        
        assert isinstance(status, ConnectionStatus)
        assert status in [ConnectionStatus.ACTIVE, ConnectionStatus.INACTIVE, ConnectionStatus.ERROR]


# Testes de integração end-to-end
class TestIntegrationEndToEnd:
    """Testes de integração end-to-end baseados no código real."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste."""
        with patch('infrastructure.integration.integration_bridge.GoogleKeywordPlannerColetor', MockGoogleKeywordPlanner), \
             patch('infrastructure.integration.integration_bridge.GoogleSuggestColetor', MockGoogleSuggest), \
             patch('infrastructure.integration.integration_bridge.GoogleTrendsColetor', MockGoogleTrends), \
             patch('infrastructure.integration.integration_bridge.ProcessadorOrquestrador', MockProcessadorOrquestrador), \
             patch('infrastructure.integration.integration_bridge.ExportadorKeywords', MockExportadorKeywords):
            
            self.bridge = IntegrationBridge()
            self.coordinator = FlowCoordinator()
            yield
    
    def test_complete_integration_flow(self):
        """Testa fluxo completo de integração."""
        # Configurar bridge
        self.bridge.modules_initialized = True
        self.bridge.coletor = {"google_trends": MockGoogleTrends()}
        self.bridge.processador = MockProcessadorOrquestrador()
        self.bridge.exportador = MockExportadorKeywords()
        
        # Executar fluxo completo
        resultado = self.coordinator.execute_complete_flow("teste", "tech")
        
        # Verificações
        assert resultado.success is True
        assert resultado.keywords_coletadas > 0
        assert resultado.keywords_processadas > 0
        assert resultado.arquivos_gerados > 0
        assert resultado.total_time >= 0
        
        # Verificar que cada etapa foi executada
        assert "coleta" in resultado.steps
        assert "processamento" in resultado.steps
        assert "exportacao" in resultado.steps
        
        # Verificar dados de cada etapa
        coleta_step = resultado.steps["coleta"]
        assert coleta_step.status == "completed"
        assert len(coleta_step.result) > 0
        
        processamento_step = resultado.steps["processamento"]
        assert processamento_step.status == "completed"
        assert "keywords" in processamento_step.result
        
        exportacao_step = resultado.steps["exportacao"]
        assert exportacao_step.status == "completed"
        assert "arquivos" in exportacao_step.result
    
    def test_error_propagation(self):
        """Testa propagação de erros através do fluxo."""
        # Mock para simular erro em uma etapa
        with patch.object(self.bridge, 'execute_coleta', side_effect=Exception("Coleta failed")):
            resultado = self.coordinator.execute_complete_flow("teste", "tech")
            
            assert resultado.success is False
            assert resultado.error is not None
            assert "Coleta failed" in resultado.error
    
    def test_metrics_accumulation(self):
        """Testa acumulação de métricas durante o fluxo."""
        # Configurar bridge
        self.bridge.modules_initialized = True
        self.bridge.coletor = {"google_trends": MockGoogleTrends()}
        self.bridge.processador = MockProcessadorOrquestrador()
        self.bridge.exportador = MockExportadorKeywords()
        
        # Executar fluxo
        self.coordinator.execute_complete_flow("teste", "tech")
        
        # Verificar métricas
        metrics = self.bridge.metrics
        assert metrics["total_integrations"] > 0
        assert metrics["successful_integrations"] > 0
        assert "last_success" in metrics
