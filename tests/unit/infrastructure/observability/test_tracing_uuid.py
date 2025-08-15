from typing import Dict, List, Optional, Any
"""
Testes Unitários para Sistema de Tracing com UUID Único - Omni Keywords Finder

Testes abrangentes para validação do sistema de tracing com UUID único:
- Geração de UUID único por integração
- Propagação cross-service
- Integração com OpenTelemetry
- Logging estruturado com UUID
- Dashboard de rastreabilidade
- Context managers para integrações

Autor: Sistema de Testes de Observabilidade
Data: 2024-12-19
Ruleset: enterprise_control_layer.yaml
Tracing ID: TEST_TRACING_UUID_001
"""

import pytest
import tempfile
import os
import json
import time
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Importar o módulo a ser testado
import sys
sys.path.append('infrastructure/observability')
from tracing import (
    DistributedTracing, IntegrationType, IntegrationTrace,
    traced_integration, get_tracing, initialize_tracing
)

class TestDistributedTracing:
    """Testes para o sistema de tracing com UUID único"""
    
    @pytest.fixture
    def tracing(self):
        """Fixture para criar sistema de tracing de teste"""
        return DistributedTracing("test-service")
    
    @pytest.fixture
    def temp_dir(self):
        """Fixture para criar diretório temporário"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_tracing_initialization(self, tracing):
        """Teste de inicialização do sistema de tracing"""
        assert tracing is not None
        assert tracing.service_name == "test-service"
        assert tracing.config is not None
        assert "sampling_rate" in tracing.config
        assert "enable_uuid_propagation" in tracing.config
        assert "uuid_header_name" in tracing.config
    
    def test_generate_integration_uuid(self, tracing):
        """Teste de geração de UUID único para integração"""
        # Gerar UUIDs para diferentes integrações
        uuid1 = tracing.generate_integration_uuid(
            IntegrationType.WEBHOOK, "test_operation"
        )
        uuid2 = tracing.generate_integration_uuid(
            IntegrationType.API_CALL, "test_operation"
        )
        uuid3 = tracing.generate_integration_uuid(
            IntegrationType.WEBHOOK, "different_operation"
        )
        
        # Verificar que UUIDs são únicos
        assert uuid1 != uuid2
        assert uuid1 != uuid3
        assert uuid2 != uuid3
        
        # Verificar formato do UUID
        assert len(uuid1) > 0
        assert "-" in uuid1
        
        # Verificar que UUIDs são consistentes para mesma entrada
        uuid1_again = tracing.generate_integration_uuid(
            IntegrationType.WEBHOOK, "test_operation"
        )
        assert uuid1 == uuid1_again
    
    def test_start_integration_trace(self, tracing):
        """Teste de início de trace de integração"""
        # Iniciar trace
        integration_uuid = tracing.start_integration_trace(
            IntegrationType.WEBHOOK,
            "test_operation",
            metadata={"test_key": "test_value"}
        )
        
        # Verificar que UUID foi gerado
        assert integration_uuid is not None
        assert len(integration_uuid) > 0
        
        # Verificar que trace está ativo
        assert integration_uuid in tracing.active_integrations
        
        # Verificar dados do trace
        trace = tracing.active_integrations[integration_uuid]
        assert trace.integration_type == IntegrationType.WEBHOOK
        assert trace.operation_name == "test_operation"
        assert trace.service_name == "test-service"
        assert trace.status == "pending"
        assert trace.start_time is not None
        assert trace.end_time is None
        assert trace.metadata["test_key"] == "test_value"
    
    def test_end_integration_trace(self, tracing):
        """Teste de finalização de trace de integração"""
        # Iniciar trace
        integration_uuid = tracing.start_integration_trace(
            IntegrationType.API_CALL,
            "test_operation"
        )
        
        # Aguardar um pouco para ter duração
        time.sleep(0.1)
        
        # Finalizar trace com sucesso
        tracing.end_integration_trace(integration_uuid, status="success")
        
        # Verificar que trace não está mais ativo
        assert integration_uuid not in tracing.active_integrations
        
        # Verificar que trace está no histórico
        assert len(tracing.integration_history) == 1
        
        # Verificar dados do trace finalizado
        trace = tracing.integration_history[0]
        assert trace.integration_uuid == integration_uuid
        assert trace.status == "success"
        assert trace.end_time is not None
        assert trace.duration is not None
        assert trace.duration > 0
    
    def test_end_integration_trace_with_error(self, tracing):
        """Teste de finalização de trace com erro"""
        # Iniciar trace
        integration_uuid = tracing.start_integration_trace(
            IntegrationType.EXTERNAL_SERVICE,
            "test_operation"
        )
        
        # Finalizar trace com erro
        error_message = "Connection timeout"
        tracing.end_integration_trace(
            integration_uuid, 
            status="error", 
            error_message=error_message
        )
        
        # Verificar dados do trace com erro
        trace = tracing.integration_history[0]
        assert trace.status == "error"
        assert trace.error_message == error_message
    
    def test_integration_span_context_manager(self, tracing):
        """Teste do context manager para spans de integração"""
        # Usar context manager
        with tracing.integration_span(
            IntegrationType.WEBHOOK,
            "test_operation",
            metadata={"test": "value"}
        ) as integration_uuid:
            # Verificar que UUID foi retornado
            assert integration_uuid is not None
            
            # Verificar que trace está ativo durante execução
            assert integration_uuid in tracing.active_integrations
        
        # Verificar que trace foi finalizado automaticamente
        assert integration_uuid not in tracing.active_integrations
        assert len(tracing.integration_history) == 1
        
        # Verificar que trace foi marcado como sucesso
        trace = tracing.integration_history[0]
        assert trace.status == "success"
    
    def test_integration_span_context_manager_with_exception(self, tracing):
        """Teste do context manager com exceção"""
        # Usar context manager que gera exceção
        with pytest.raises(ValueError):
            with tracing.integration_span(
                IntegrationType.API_CALL,
                "test_operation"
            ) as integration_uuid:
                # Verificar que UUID foi retornado
                assert integration_uuid is not None
                
                # Gerar exceção
                raise ValueError("Test error")
        
        # Verificar que trace foi finalizado com erro
        assert len(tracing.integration_history) == 1
        trace = tracing.integration_history[0]
        assert trace.status == "error"
        assert "Test error" in trace.error_message
    
    def test_inject_integration_context(self, tracing):
        """Teste de injeção de contexto de integração"""
        # Preparar headers
        headers = {"Content-Type": "application/json"}
        integration_uuid = "test-uuid-123"
        
        # Injeta contexto
        result_headers = tracing.inject_integration_context(headers, integration_uuid)
        
        # Verificar que UUID foi adicionado
        assert tracing.config["uuid_header_name"] in result_headers
        assert result_headers[tracing.config["uuid_header_name"]] == integration_uuid
        
        # Verificar que headers originais foram preservados
        assert "Content-Type" in result_headers
        assert result_headers["Content-Type"] == "application/json"
    
    def test_extract_integration_context(self, tracing):
        """Teste de extração de contexto de integração"""
        # Preparar headers com contexto
        integration_uuid = "test-uuid-456"
        headers = {
            "Content-Type": "application/json",
            tracing.config["uuid_header_name"]: integration_uuid
        }
        
        # Extrair contexto
        extracted_uuid = tracing.extract_integration_context(headers)
        
        # Verificar que UUID foi extraído
        assert extracted_uuid == integration_uuid
    
    def test_extract_integration_context_missing(self, tracing):
        """Teste de extração de contexto quando não presente"""
        # Preparar headers sem contexto
        headers = {"Content-Type": "application/json"}
        
        # Extrair contexto
        extracted_uuid = tracing.extract_integration_context(headers)
        
        # Verificar que None foi retornado
        assert extracted_uuid is None
    
    def test_get_integration_trace(self, tracing):
        """Teste de obtenção de trace de integração"""
        # Iniciar trace
        integration_uuid = tracing.start_integration_trace(
            IntegrationType.DATABASE,
            "test_operation"
        )
        
        # Obter trace ativo
        active_trace = tracing.get_integration_trace(integration_uuid)
        assert active_trace is not None
        assert active_trace.integration_uuid == integration_uuid
        
        # Finalizar trace
        tracing.end_integration_trace(integration_uuid)
        
        # Obter trace do histórico
        history_trace = tracing.get_integration_trace(integration_uuid)
        assert history_trace is not None
        assert history_trace.integration_uuid == integration_uuid
        assert history_trace.status == "success"
    
    def test_get_integration_trace_not_found(self, tracing):
        """Teste de obtenção de trace inexistente"""
        # Tentar obter trace que não existe
        trace = tracing.get_integration_trace("non-existent-uuid")
        assert trace is None
    
    def test_get_integration_statistics(self, tracing):
        """Teste de obtenção de estatísticas de integração"""
        # Criar múltiplos traces
        for index in range(3):
            integration_uuid = tracing.start_integration_trace(
                IntegrationType.WEBHOOK,
                f"operation_{index}"
            )
            tracing.end_integration_trace(integration_uuid, status="success")
        
        # Criar trace com erro
        error_uuid = tracing.start_integration_trace(
            IntegrationType.API_CALL,
            "error_operation"
        )
        tracing.end_integration_trace(error_uuid, status="error")
        
        # Obter estatísticas
        stats = tracing.get_integration_statistics()
        
        # Verificar estatísticas básicas
        assert stats["active_integrations"] == 0
        assert stats["total_integrations"] == 4
        assert stats["service_name"] == "test-service"
        
        # Verificar estatísticas por tipo
        assert "webhook" in stats["type_statistics"]
        assert "api_call" in stats["type_statistics"]
        
        webhook_stats = stats["type_statistics"]["webhook"]
        assert webhook_stats["total"] == 3
        assert webhook_stats["success"] == 3
        assert webhook_stats["error"] == 0
        assert webhook_stats["success_rate"] == 100.0
        
        api_call_stats = stats["type_statistics"]["api_call"]
        assert api_call_stats["total"] == 1
        assert api_call_stats["success"] == 0
        assert api_call_stats["error"] == 1
        assert api_call_stats["success_rate"] == 0.0
    
    def test_export_integration_traces(self, tracing):
        """Teste de exportação de traces de integração"""
        # Criar alguns traces
        for index in range(2):
            integration_uuid = tracing.start_integration_trace(
                IntegrationType.WEBHOOK,
                f"operation_{index}"
            )
            tracing.end_integration_trace(integration_uuid)
        
        # Exportar em formato JSON
        export_data = tracing.export_integration_traces("json")
        
        # Verificar que é JSON válido
        try:
            data = json.loads(export_data)
        except json.JSONDecodeError:
            pytest.fail("Export data is not valid JSON")
        
        # Verificar estrutura dos dados
        assert "service_name" in data
        assert "export_timestamp" in data
        assert "active_integrations" in data
        assert "integration_history" in data
        assert "statistics" in data
        
        # Verificar dados específicos
        assert data["service_name"] == "test-service"
        assert len(data["integration_history"]) == 2
    
    def test_integration_history_limit(self, tracing):
        """Teste de limite do histórico de integrações"""
        # Configurar limite baixo para teste
        original_limit = tracing.config["max_integration_history"]
        tracing.config["max_integration_history"] = 3
        
        try:
            # Criar mais traces que o limite
            for index in range(5):
                integration_uuid = tracing.start_integration_trace(
                    IntegrationType.WEBHOOK,
                    f"operation_{index}"
                )
                tracing.end_integration_trace(integration_uuid)
            
            # Verificar que apenas os últimos traces foram mantidos
            assert len(tracing.integration_history) == 3
            
            # Verificar que os últimos traces são os mais recentes
            last_trace = tracing.integration_history[-1]
            assert "operation_4" in last_trace.operation_name
            
        finally:
            # Restaurar limite original
            tracing.config["max_integration_history"] = original_limit
    
    def test_parent_child_trace_relationship(self, tracing):
        """Teste de relacionamento pai-filho entre traces"""
        # Criar trace pai
        parent_uuid = tracing.start_integration_trace(
            IntegrationType.WEBHOOK,
            "parent_operation"
        )
        
        # Criar trace filho
        child_uuid = tracing.start_integration_trace(
            IntegrationType.API_CALL,
            "child_operation",
            parent_trace_id=parent_uuid
        )
        
        # Finalizar traces
        tracing.end_integration_trace(child_uuid)
        tracing.end_integration_trace(parent_uuid)
        
        # Verificar relacionamento
        child_trace = tracing.get_integration_trace(child_uuid)
        assert child_trace.parent_trace_id == parent_uuid
        
        parent_trace = tracing.get_integration_trace(parent_uuid)
        assert child_uuid in parent_trace.child_traces
    
    def test_traced_integration_decorator(self):
        """Teste do decorador traced_integration"""
        # Função de teste
        @traced_integration(IntegrationType.WEBHOOK, "decorated_operation")
        def test_function():
            return "success"
        
        # Executar função
        result = test_function()
        assert result == "success"
        
        # Verificar que trace foi criado
        tracing = get_tracing()
        assert len(tracing.integration_history) == 1
        
        trace = tracing.integration_history[0]
        assert trace.operation_name == "decorated_operation"
        assert trace.status == "success"
    
    def test_traced_integration_decorator_with_exception(self):
        """Teste do decorador traced_integration com exceção"""
        # Função de teste que gera exceção
        @traced_integration(IntegrationType.API_CALL, "error_operation")
        def error_function():
            raise ValueError("Test error")
        
        # Executar função
        with pytest.raises(ValueError):
            error_function()
        
        # Verificar que trace foi criado com erro
        tracing = get_tracing()
        assert len(tracing.integration_history) == 1
        
        trace = tracing.integration_history[0]
        assert trace.operation_name == "error_operation"
        assert trace.status == "error"
        assert "Test error" in trace.error_message
    
    def test_get_tracing_function(self):
        """Teste da função get_tracing"""
        # Obter instância global
        tracing = get_tracing()
        
        # Verificar que é uma instância válida
        assert isinstance(tracing, DistributedTracing)
        assert tracing.service_name == "omni-keywords-finder"
    
    def test_initialize_tracing_function(self):
        """Teste da função initialize_tracing"""
        # Inicializar com nome customizado
        tracing = initialize_tracing("custom-service")
        
        # Verificar que é uma instância válida
        assert isinstance(tracing, DistributedTracing)
        assert tracing.service_name == "custom-service"
    
    def test_integration_types_enum(self):
        """Teste dos tipos de integração"""
        # Verificar todos os tipos disponíveis
        expected_types = [
            "webhook", "api_call", "database", "external_service",
            "internal_service", "background_job", "scheduled_task"
        ]
        
        for expected_type in expected_types:
            assert hasattr(IntegrationType, expected_type.upper())
            enum_value = getattr(IntegrationType, expected_type.upper())
            assert enum_value.value == expected_type
    
    def test_integration_trace_dataclass(self):
        """Teste da dataclass IntegrationTrace"""
        # Criar trace
        trace = IntegrationTrace(
            integration_uuid="test-uuid",
            integration_type=IntegrationType.WEBHOOK,
            service_name="test-service",
            operation_name="test-operation",
            start_time=datetime.now()
        )
        
        # Verificar atributos
        assert trace.integration_uuid == "test-uuid"
        assert trace.integration_type == IntegrationType.WEBHOOK
        assert trace.service_name == "test-service"
        assert trace.operation_name == "test-operation"
        assert trace.status == "pending"
        assert trace.metadata == {}
        assert trace.child_traces == []

if __name__ == "__main__":
    pytest.main([__file__]) 