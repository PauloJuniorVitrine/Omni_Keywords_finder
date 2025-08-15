"""
Teste Simples de Integração - Omni Keywords Finder

Teste básico para verificar se o sistema de integração funciona
sem dependências externas complexas.

Tracing ID: TEST_SIMPLE_INTEGRATION_001_20250127
"""

import pytest
import time
from unittest.mock import Mock, patch
from datetime import datetime

# Importar módulos reais para teste
from infrastructure.integration.integration_bridge import IntegrationBridge, IntegrationResult
from infrastructure.integration.flow_coordinator import FlowCoordinator, FlowResult
from infrastructure.integration.module_connector import ModuleConnector, ConnectionStatus


class TestSimpleIntegration:
    """Testes simples de integração."""
    
    def test_integration_bridge_creation(self):
        """Testa criação básica do IntegrationBridge."""
        bridge = IntegrationBridge()
        
        assert bridge is not None
        assert hasattr(bridge, 'tracing_id')
        assert hasattr(bridge, 'modules_initialized')
        assert hasattr(bridge, 'metrics')
        
        # Verificar que o tracing_id é gerado
        assert bridge.tracing_id is not None
        assert isinstance(bridge.tracing_id, str)
        assert len(bridge.tracing_id) > 0
    
    def test_flow_coordinator_creation(self):
        """Testa criação básica do FlowCoordinator."""
        coordinator = FlowCoordinator()
        
        assert coordinator is not None
        assert hasattr(coordinator, 'tracing_id')
        assert hasattr(coordinator, 'bridge')
        assert hasattr(coordinator, 'flow_history')
        
        # Verificar que o tracing_id é gerado
        assert coordinator.tracing_id is not None
        assert isinstance(coordinator.tracing_id, str)
        assert len(coordinator.tracing_id) > 0
    
    def test_module_connector_creation(self):
        """Testa criação básica do ModuleConnector."""
        connector = ModuleConnector()
        
        assert connector is not None
        assert hasattr(connector, 'connections')
        assert hasattr(connector, 'health_checks')
        
        # Verificar estruturas de dados
        assert isinstance(connector.connections, dict)
        assert isinstance(connector.health_checks, dict)
    
    def test_integration_result_creation(self):
        """Testa criação de IntegrationResult."""
        result = IntegrationResult(
            success=True,
            data={"test": "data"},
            error=None,
            execution_time=1.5,
            metadata={"source": "test"}
        )
        
        assert result.success is True
        assert result.data == {"test": "data"}
        assert result.error is None
        assert result.execution_time == 1.5
        assert result.metadata == {"source": "test"}
    
    def test_flow_result_creation(self):
        """Testa criação de FlowResult."""
        result = FlowResult(
            flow_id="test_flow",
            termo="teste",
            nicho="tech",
            success=True,
            steps={},
            total_time=2.0,
            keywords_coletadas=5,
            keywords_processadas=5,
            arquivos_gerados=2
        )
        
        assert result.flow_id == "test_flow"
        assert result.termo == "teste"
        assert result.nicho == "tech"
        assert result.success is True
        assert result.total_time == 2.0
        assert result.keywords_coletadas == 5
        assert result.keywords_processadas == 5
        assert result.arquivos_gerados == 2
    
    def test_bridge_status_check(self):
        """Testa verificação de status do bridge."""
        bridge = IntegrationBridge()
        
        status = bridge.get_module_status()
        
        assert isinstance(status, dict)
        assert "bridge_ready" in status
        assert "modules_initialized" in status
        assert "coletor_available" in status
        assert "processador_available" in status
        assert "exportador_available" in status
        assert "metrics" in status
    
    def test_coordinator_status_check(self):
        """Testa verificação de status do coordenador."""
        coordinator = FlowCoordinator()
        
        status = coordinator.get_flow_status()
        
        assert isinstance(status, dict)
        assert "total_flows" in status
        assert "successful_flows" in status
        assert "failed_flows" in status
        assert "last_flow_time" in status
    
    def test_connector_basic_operations(self):
        """Testa operações básicas do conector."""
        connector = ModuleConnector()
        
        # Testar conexão entre módulos
        result = connector.connect_modules("module1", "module2", "test_connection")
        
        assert result.success is True
        assert "module1" in connector.connections
        assert "module2" in connector.connections["module1"]
        
        # Testar verificação de saúde
        health = connector.check_connection_health("module1", "module2")
        
        assert isinstance(health, dict)
        assert "status" in health
        assert "last_check" in health
        
        # Testar obtenção de status
        status = connector.get_connection_status("module1", "module2")
        
        assert isinstance(status, ConnectionStatus)
        assert status in [ConnectionStatus.ACTIVE, ConnectionStatus.INACTIVE, ConnectionStatus.ERROR]
    
    def test_metrics_tracking(self):
        """Testa rastreamento de métricas."""
        bridge = IntegrationBridge()
        
        # Verificar métricas iniciais
        initial_metrics = bridge.metrics.copy()
        
        assert "total_integrations" in initial_metrics
        assert "successful_integrations" in initial_metrics
        assert "failed_integrations" in initial_metrics
        assert "last_error" in initial_metrics
        assert "last_success" in initial_metrics
        
        # Verificar valores iniciais
        assert initial_metrics["total_integrations"] == 0
        assert initial_metrics["successful_integrations"] == 0
        assert initial_metrics["failed_integrations"] == 0
    
    def test_tracing_id_uniqueness(self):
        """Testa que cada instância tem um tracing_id único."""
        bridge1 = IntegrationBridge()
        bridge2 = IntegrationBridge()
        coordinator1 = FlowCoordinator()
        coordinator2 = FlowCoordinator()
        
        # Verificar que todos têm tracing_ids
        assert bridge1.tracing_id is not None
        assert bridge2.tracing_id is not None
        assert coordinator1.tracing_id is not None
        assert coordinator2.tracing_id is not None
        
        # Verificar que são únicos
        tracing_ids = [
            bridge1.tracing_id,
            bridge2.tracing_id,
            coordinator1.tracing_id,
            coordinator2.tracing_id
        ]
        
        assert len(tracing_ids) == len(set(tracing_ids))
        
        # Verificar formato
        for tracing_id in tracing_ids:
            assert isinstance(tracing_id, str)
            assert len(tracing_id) > 0
    
    def test_error_handling_basic(self):
        """Testa tratamento básico de erros."""
        bridge = IntegrationBridge()
        
        # Verificar que o bridge não está pronto inicialmente
        assert bridge.is_ready() is False
        
        # Verificar que get_module_status funciona mesmo com erro
        status = bridge.get_module_status()
        assert isinstance(status, dict)
        assert status["bridge_ready"] is False
        assert status["modules_initialized"] is False
    
    def test_flow_history_tracking(self):
        """Testa rastreamento de histórico de fluxos."""
        coordinator = FlowCoordinator()
        
        # Verificar histórico inicial
        assert len(coordinator.flow_history) == 0
        
        # Verificar que get_flow_status funciona
        status = coordinator.get_flow_status()
        assert status["total_flows"] == 0
        assert status["successful_flows"] == 0
        assert status["failed_flows"] == 0
    
    def test_reset_functionality(self):
        """Testa funcionalidade de reset."""
        coordinator = FlowCoordinator()
        
        # Executar reset
        coordinator.reset_flow()
        
        # Verificar que o histórico está limpo
        assert len(coordinator.flow_history) == 0
        
        # Verificar que get_flow_status ainda funciona
        status = coordinator.get_flow_status()
        assert status["total_flows"] == 0


# Testes de integração básica
class TestBasicIntegration:
    """Testes de integração básica entre componentes."""
    
    def test_bridge_coordinator_integration(self):
        """Testa integração entre bridge e coordenador."""
        bridge = IntegrationBridge()
        coordinator = FlowCoordinator()
        
        # Verificar que o coordenador tem acesso ao bridge
        assert coordinator.bridge is not None
        assert isinstance(coordinator.bridge, IntegrationBridge)
        
        # Verificar que podem compartilhar informações
        bridge_status = bridge.get_module_status()
        coordinator_bridge_status = coordinator.get_bridge_status()
        
        assert bridge_status["bridge_ready"] == coordinator_bridge_status["bridge_ready"]
        assert bridge_status["modules_initialized"] == coordinator_bridge_status["modules_initialized"]
    
    def test_connector_integration(self):
        """Testa integração do conector com outros componentes."""
        connector = ModuleConnector()
        
        # Criar algumas conexões
        connector.connect_modules("coleta", "processamento", "data_flow")
        connector.connect_modules("processamento", "exportacao", "result_flow")
        
        # Verificar que as conexões foram criadas
        assert "coleta" in connector.connections
        assert "processamento" in connector.connections
        assert "exportacao" in connector.connections
        
        # Verificar que as conexões são bidirecionais
        assert "processamento" in connector.connections["coleta"]
        assert "exportacao" in connector.connections["processamento"]
    
    def test_metrics_integration(self):
        """Testa integração de métricas entre componentes."""
        bridge = IntegrationBridge()
        coordinator = FlowCoordinator()
        
        # Verificar que ambos têm sistemas de métricas
        bridge_metrics = bridge.metrics
        coordinator_status = coordinator.get_flow_status()
        
        assert isinstance(bridge_metrics, dict)
        assert isinstance(coordinator_status, dict)
        
        # Verificar que as métricas são consistentes
        assert "total_integrations" in bridge_metrics
        assert "total_flows" in coordinator_status


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
