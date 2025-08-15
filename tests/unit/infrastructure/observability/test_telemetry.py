from typing import Dict, List, Optional, Any
"""
Testes Unitários - Sistema de Telemetria
Tracing ID: OBSERVABILITY_20241219_001
Data: 2024-12-19
Versão: 1.0

Testes para o sistema de telemetria centralizado com:
- Validação de inicialização
- Testes de métricas
- Testes de tracing
- Testes de logs estruturados
- Validação de configurações
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from contextlib import contextmanager

# Importar módulos de telemetria
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

from infrastructure.observability.telemetry import (
    TelemetryManager, 
    initialize_telemetry,
    get_telemetry_manager,
    traced_operation,
    monitored_metric
)


class TestTelemetryManager:
    """Testes para o gerenciador de telemetria."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.service_name = "test-service"
        self.telemetry_manager = TelemetryManager(self.service_name)
    
    def test_telemetry_manager_initialization(self):
        """Testa inicialização básica do gerenciador de telemetria."""
        # Arrange & Act
        manager = TelemetryManager("test-service")
        
        # Assert
        assert manager.service_name == "test-service"
        assert manager.tracer is None
        assert manager.meter is None
        assert manager.logger is None
        assert not manager._initialized
    
    def test_telemetry_manager_config_defaults(self):
        """Testa configurações padrão do gerenciador."""
        # Arrange & Act
        manager = TelemetryManager()
        
        # Assert
        assert manager.config["jaeger_endpoint"] == "http://localhost:14268/api/traces"
        assert manager.config["prometheus_port"] == 9090
        assert manager.config["sampling_rate"] == 0.1
        assert manager.config["log_level"] == "INFO"
        assert manager.config["environment"] == "development"
    
    @patch('infrastructure.observability.telemetry.Resource')
    @patch('infrastructure.observability.telemetry.TracerProvider')
    @patch('infrastructure.observability.telemetry.MeterProvider')
    @patch('infrastructure.observability.telemetry.start_http_server')
    def test_telemetry_initialization_success(self, mock_start_server, mock_meter_provider, 
                                            mock_tracer_provider, mock_resource):
        """Testa inicialização bem-sucedida da telemetria."""
        # Arrange
        mock_resource_instance = Mock()
        mock_resource.create.return_value = mock_resource_instance
        
        mock_tracer_provider_instance = Mock()
        mock_tracer_provider.return_value = mock_tracer_provider_instance
        
        mock_meter_provider_instance = Mock()
        mock_meter_provider.return_value = mock_meter_provider_instance
        
        # Act
        self.telemetry_manager.initialize()
        
        # Assert
        assert self.telemetry_manager._initialized is True
        mock_resource.create.assert_called_once()
        mock_tracer_provider.assert_called_once()
        mock_meter_provider.assert_called_once()
        mock_start_server.assert_called_once_with(9090)
    
    @patch('infrastructure.observability.telemetry.Resource')
    def test_telemetry_initialization_failure(self, mock_resource):
        """Testa falha na inicialização da telemetria."""
        # Arrange
        mock_resource.create.side_effect = Exception("Configuração inválida")
        
        # Act & Assert
        with pytest.raises(Exception, match="Configuração inválida"):
            self.telemetry_manager.initialize()
    
    def test_telemetry_initialization_idempotent(self):
        """Testa que inicialização é idempotente."""
        # Arrange
        with patch.object(self.telemetry_manager, '_setup_tracing') as mock_setup_tracing:
            with patch.object(self.telemetry_manager, '_setup_metrics') as mock_setup_metrics:
                with patch.object(self.telemetry_manager, '_setup_logging') as mock_setup_logging:
                    with patch.object(self.telemetry_manager, '_setup_auto_instrumentation') as mock_setup_auto:
                        
                        # Act - Primeira inicialização
                        self.telemetry_manager.initialize()
                        
                        # Act - Segunda inicialização
                        self.telemetry_manager.initialize()
                        
                        # Assert - Métodos chamados apenas uma vez
                        mock_setup_tracing.assert_called_once()
                        mock_setup_metrics.assert_called_once()
                        mock_setup_logging.assert_called_once()
                        mock_setup_auto.assert_called_once()
    
    @patch('infrastructure.observability.telemetry.trace')
    def test_trace_operation_context_manager(self, mock_trace):
        """Testa context manager para tracing de operações."""
        # Arrange
        mock_tracer = Mock()
        mock_span = Mock()
        mock_tracer.start_span.return_value = mock_span
        mock_trace.get_tracer.return_value = mock_tracer
        
        self.telemetry_manager.tracer = mock_tracer
        self.telemetry_manager._initialized = True
        
        # Act
        with self.telemetry_manager.trace_operation("test-operation", {"key": "value"}) as span:
            pass
        
        # Assert
        mock_tracer.start_span.assert_called_once_with("test-operation", attributes={"key": "value"})
        mock_span.end.assert_called_once()
    
    @patch('infrastructure.observability.telemetry.metrics')
    def test_record_metric_success(self, mock_metrics):
        """Testa registro bem-sucedido de métrica."""
        # Arrange
        mock_meter = Mock()
        mock_counter = Mock()
        mock_meter.create_counter.return_value = mock_counter
        mock_metrics.get_meter.return_value = mock_meter
        
        self.telemetry_manager.meter = mock_meter
        self.telemetry_manager._initialized = True
        
        # Act
        self.telemetry_manager.record_metric("test_metric", 42, {"label": "value"})
        
        # Assert
        mock_meter.create_counter.assert_called_once_with("test_metric")
        mock_counter.add.assert_called_once_with(42, {"label": "value"})
    
    @patch('infrastructure.observability.telemetry.metrics')
    def test_record_metric_failure_handling(self, mock_metrics):
        """Testa tratamento de erro no registro de métrica."""
        # Arrange
        mock_meter = Mock()
        mock_meter.create_counter.side_effect = Exception("Erro de métrica")
        mock_metrics.get_meter.return_value = mock_meter
        
        self.telemetry_manager.meter = mock_meter
        self.telemetry_manager._initialized = True
        
        with patch.object(self.telemetry_manager, 'logger') as mock_logger:
            # Act
            self.telemetry_manager.record_metric("test_metric", 42)
            
            # Assert
            mock_logger.error.assert_called_once()
    
    def test_log_event_with_extra_data(self):
        """Testa registro de evento com dados extras."""
        # Arrange
        mock_logger = Mock()
        self.telemetry_manager.logger = mock_logger
        self.telemetry_manager._initialized = True
        
        # Act
        self.telemetry_manager.log_event(
            "test_event", 
            "Test message", 
            {"extra_key": "extra_value"}
        )
        
        # Assert
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args
        assert "EVENT: test_event - Test message" in call_args[0][0]
        assert call_args[1]["extra"]["extra_key"] == "extra_value"


class TestTelemetryDecorators:
    """Testes para decoradores de telemetria."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.telemetry_manager = TelemetryManager("test-service")
    
    @patch('infrastructure.observability.telemetry.telemetry_manager')
    def test_traced_operation_decorator(self, mock_telemetry_manager):
        """Testa decorador de tracing de operações."""
        # Arrange
        mock_telemetry_manager.trace_operation.return_value.__enter__ = Mock()
        mock_telemetry_manager.trace_operation.return_value.__exit__ = Mock()
        
        @traced_operation("test-operation", {"decorator": "test"})
        def test_function():
            return "success"
        
        # Act
        result = test_function()
        
        # Assert
        assert result == "success"
        mock_telemetry_manager.trace_operation.assert_called_once_with("test-operation", {"decorator": "test"})
    
    @patch('infrastructure.observability.telemetry.telemetry_manager')
    @patch('infrastructure.observability.telemetry.time')
    def test_monitored_metric_decorator_success(self, mock_time, mock_telemetry_manager):
        """Testa decorador de métricas com sucesso."""
        # Arrange
        mock_time.time.side_effect = [100.0, 100.5]  # start_time, end_time
        
        @monitored_metric("test_metric", {"label": "value"})
        def test_function():
            return "success"
        
        # Act
        result = test_function()
        
        # Assert
        assert result == "success"
        assert mock_telemetry_manager.record_metric.call_count == 2  # success + duration
        mock_telemetry_manager.record_metric.assert_any_call("test_metric_success", 1, {"label": "value"})
        mock_telemetry_manager.record_metric.assert_any_call("test_metric_duration", 0.5, {"label": "value"})
    
    @patch('infrastructure.observability.telemetry.telemetry_manager')
    @patch('infrastructure.observability.telemetry.time')
    def test_monitored_metric_decorator_exception(self, mock_time, mock_telemetry_manager):
        """Testa decorador de métricas com exceção."""
        # Arrange
        mock_time.time.side_effect = [100.0, 100.5]  # start_time, end_time
        
        @monitored_metric("test_metric")
        def test_function():
            raise ValueError("Test error")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Test error"):
            test_function()
        
        # Assert
        assert mock_telemetry_manager.record_metric.call_count == 2  # error + duration
        mock_telemetry_manager.record_metric.assert_any_call("test_metric_error", 1, None)
        mock_telemetry_manager.record_metric.assert_any_call("test_metric_duration", 0.5, None)


class TestTelemetryIntegration:
    """Testes de integração para telemetria."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.telemetry_manager = TelemetryManager("integration-test")
    
    @patch('infrastructure.observability.telemetry.Resource')
    @patch('infrastructure.observability.telemetry.TracerProvider')
    @patch('infrastructure.observability.telemetry.MeterProvider')
    @patch('infrastructure.observability.telemetry.start_http_server')
    def test_full_telemetry_workflow(self, mock_start_server, mock_meter_provider, 
                                   mock_tracer_provider, mock_resource):
        """Testa workflow completo de telemetria."""
        # Arrange
        mock_resource_instance = Mock()
        mock_resource.create.return_value = mock_resource_instance
        
        mock_tracer_provider_instance = Mock()
        mock_tracer_provider.return_value = mock_tracer_provider_instance
        
        mock_meter_provider_instance = Mock()
        mock_meter_provider.return_value = mock_meter_provider_instance
        
        # Act
        self.telemetry_manager.initialize()
        
        # Simular operações
        with self.telemetry_manager.trace_operation("test-operation"):
            self.telemetry_manager.record_metric("test_counter", 1)
            self.telemetry_manager.log_event("test_event", "Test message")
        
        # Assert
        assert self.telemetry_manager._initialized is True
        mock_start_server.assert_called_once()
    
    def test_telemetry_without_opentelemetry(self):
        """Testa comportamento quando OpenTelemetry não está disponível."""
        # Arrange
        with patch('infrastructure.observability.telemetry.OPENTELEMETRY_AVAILABLE', False):
            manager = TelemetryManager("test-service")
            
            # Act
            manager.initialize()
            
            # Assert
            assert manager._initialized is False
            assert manager.tracer is None
            assert manager.meter is None


class TestTelemetryConfiguration:
    """Testes para configurações de telemetria."""
    
    def test_environment_variable_configuration(self):
        """Testa configuração via variáveis de ambiente."""
        # Arrange
        test_config = {
            "JAEGER_ENDPOINT": "http://test-jaeger:14268/api/traces",
            "PROMETHEUS_PORT": "9091",
            "SAMPLING_RATE": "0.5",
            "LOG_LEVEL": "DEBUG",
            "ENVIRONMENT": "production"
        }
        
        with patch.dict('os.environ', test_config):
            # Act
            manager = TelemetryManager()
            
            # Assert
            assert manager.config["jaeger_endpoint"] == "http://test-jaeger:14268/api/traces"
            assert manager.config["prometheus_port"] == 9091
            assert manager.config["sampling_rate"] == 0.5
            assert manager.config["log_level"] == "DEBUG"
            assert manager.config["environment"] == "production"
    
    def test_service_name_configuration(self):
        """Testa configuração de nome do serviço."""
        # Arrange & Act
        manager = TelemetryManager("custom-service-name")
        
        # Assert
        assert manager.service_name == "custom-service-name"


# Testes de performance e stress
class TestTelemetryPerformance:
    """Testes de performance para telemetria."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.telemetry_manager = TelemetryManager("performance-test")
    
    @patch('infrastructure.observability.telemetry.Resource')
    @patch('infrastructure.observability.telemetry.TracerProvider')
    @patch('infrastructure.observability.telemetry.MeterProvider')
    @patch('infrastructure.observability.telemetry.start_http_server')
    def test_telemetry_initialization_performance(self, mock_start_server, mock_meter_provider, 
                                                mock_tracer_provider, mock_resource):
        """Testa performance da inicialização."""
        # Arrange
        mock_resource_instance = Mock()
        mock_resource.create.return_value = mock_resource_instance
        
        mock_tracer_provider_instance = Mock()
        mock_tracer_provider.return_value = mock_tracer_provider_instance
        
        mock_meter_provider_instance = Mock()
        mock_meter_provider.return_value = mock_meter_provider_instance
        
        # Act
        start_time = time.time()
        self.telemetry_manager.initialize()
        end_time = time.time()
        
        # Assert
        initialization_time = end_time - start_time
        assert initialization_time < 1.0  # Deve inicializar em menos de 1 segundo
        assert self.telemetry_manager._initialized is True
    
    @patch('infrastructure.observability.telemetry.trace')
    def test_trace_operation_performance(self, mock_trace):
        """Testa performance de operações de tracing."""
        # Arrange
        mock_tracer = Mock()
        mock_span = Mock()
        mock_tracer.start_span.return_value = mock_span
        mock_trace.get_tracer.return_value = mock_tracer
        
        self.telemetry_manager.tracer = mock_tracer
        self.telemetry_manager._initialized = True
        
        # Act
        start_time = time.time()
        for index in range(100):  # 100 operações
            with self.telemetry_manager.trace_operation(f"operation-{index}"):
                pass
        end_time = time.time()
        
        # Assert
        total_time = end_time - start_time
        avg_time_per_operation = total_time / 100
        assert avg_time_per_operation < 0.001  # Menos de 1ms por operação
        assert mock_tracer.start_span.call_count == 100
        assert mock_span.end.call_count == 100


# Testes de segurança
class TestTelemetrySecurity:
    """Testes de segurança para telemetria."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.telemetry_manager = TelemetryManager("security-test")
    
    def test_sensitive_data_not_logged(self):
        """Testa que dados sensíveis não são logados."""
        # Arrange
        mock_logger = Mock()
        self.telemetry_manager.logger = mock_logger
        self.telemetry_manager._initialized = True
        
        sensitive_data = {
            "password": "secret123",
            "api_key": "sk-1234567890abcdef",
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        }
        
        # Act
        self.telemetry_manager.log_event("test_event", "Test message", sensitive_data)
        
        # Assert
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args
        log_data = call_args[1]["extra"]
        
        # Verificar que dados sensíveis não estão expostos
        assert "password" not in str(log_data)
        assert "api_key" not in str(log_data)
        assert "token" not in str(log_data)
    
    def test_telemetry_configuration_validation(self):
        """Testa validação de configurações de telemetria."""
        # Arrange & Act
        manager = TelemetryManager()
        
        # Assert
        assert isinstance(manager.config["sampling_rate"], float)
        assert 0.0 <= manager.config["sampling_rate"] <= 1.0
        assert isinstance(manager.config["prometheus_port"], int)
        assert 1024 <= manager.config["prometheus_port"] <= 65535


if __name__ == "__main__":
    pytest.main([__file__, "-value"]) 