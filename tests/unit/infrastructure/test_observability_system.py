"""
Testes unitários para Sistema de Observabilidade

📐 CoCoT: Baseado em algoritmos de observabilidade distribuída
🌲 ToT: Avaliado métodos de monitoramento e escolhido mais preciso
♻️ ReAct: Simulado coleta de dados e validado precisão

Prompt: CHECKLIST_TESTES_UNITARIOS.md - Item 7.1
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27T10:30:00Z
Tracing ID: test-observability-system-2025-01-27-001

Testes baseados COMPLETAMENTE no código real:
- Sistema de telemetria centralizado
- Métricas customizadas
- Tracing distribuído
- Payload/headers logging
- Anonimização de dados sensíveis
- Cache e performance
- Casos edge
"""

import pytest
import json
import time
import re
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from contextlib import contextmanager

from infrastructure.observability.telemetry import (
    TelemetryManager,
    PayloadLogger,
    get_telemetry_manager,
    initialize_telemetry,
    traced_operation,
    monitored_metric
)

from infrastructure.observability.metrics import (
    MetricsManager,
    get_metrics_manager,
    initialize_metrics,
    record_http_request,
    record_error,
    record_keyword_processed,
    record_cache_hit,
    record_cache_miss
)

from infrastructure.observability.opentelemetry_config import (
    OpenTelemetryConfig,
    initialize_observability
)


class TestPayloadLogger:
    """Testes para PayloadLogger."""
    
    @pytest.fixture
    def payload_logger(self):
        """Fixture para criar PayloadLogger."""
        return PayloadLogger()
    
    @pytest.fixture
    def sample_sensitive_data(self):
        """Fixture com dados sensíveis de exemplo."""
        return {
            'password': 'mypassword123',
            'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9',
            'api_key': 'sk-1234567890abcdef',
            'cpf': '123.456.789-00',
            'email': 'user@example.com',
            'phone': '(11) 99999-9999',
            'credit_card': '1234-5678-9012-3456'
        }
    
    def test_payload_logger_initialization(self, payload_logger):
        """Teste de inicialização do PayloadLogger."""
        assert payload_logger.config['log_payloads'] is True
        assert payload_logger.config['log_headers'] is True
        assert payload_logger.config['anonymize_sensitive'] is True
        assert payload_logger.config['max_payload_size'] == 10240
        assert payload_logger.config['max_header_size'] == 2048
        assert len(payload_logger.sensitive_patterns) > 0
        assert len(payload_logger.sensitive_headers) > 0

    def test_anonymize_sensitive_data_password(self, payload_logger):
        """Teste de anonimização de senha."""
        data = '{"user": "test", "password": "secret123"}'
        anonymized = payload_logger.anonymize_sensitive_data(data)
        assert 'password="[REDACTED]"' in anonymized
        assert 'secret123' not in anonymized

    def test_anonymize_sensitive_data_token(self, payload_logger):
        """Teste de anonimização de token."""
        data = '{"auth": {"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"}}'
        anonymized = payload_logger.anonymize_sensitive_data(data)
        assert 'token="[REDACTED]"' in anonymized
        assert 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9' not in anonymized

    def test_anonymize_sensitive_data_bearer_token(self, payload_logger):
        """Teste de anonimização de bearer token."""
        data = 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
        anonymized = payload_logger.anonymize_sensitive_data(data)
        assert 'Bearer [REDACTED]' in anonymized
        assert 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9' not in anonymized

    def test_anonymize_sensitive_data_cpf(self, payload_logger):
        """Teste de anonimização de CPF."""
        data = '{"user": {"cpf": "123.456.789-00"}}'
        anonymized = payload_logger.anonymize_sensitive_data(data)
        assert '[DOCUMENT_REDACTED]' in anonymized
        assert '123.456.789-00' not in anonymized

    def test_anonymize_sensitive_data_email(self, payload_logger):
        """Teste de anonimização de email."""
        data = '{"user": {"email": "user@example.com"}}'
        anonymized = payload_logger.anonymize_sensitive_data(data)
        assert '[REDACTED]@example.com' in anonymized
        assert 'user@example.com' not in anonymized

    def test_anonymize_sensitive_data_phone(self, payload_logger):
        """Teste de anonimização de telefone."""
        data = '{"user": {"phone": "(11) 99999-9999"}}'
        anonymized = payload_logger.anonymize_sensitive_data(data)
        assert '[PHONE_REDACTED]' in anonymized
        assert '(11) 99999-9999' not in anonymized

    def test_anonymize_sensitive_data_credit_card(self, payload_logger):
        """Teste de anonimização de cartão de crédito."""
        data = '{"payment": {"card": "1234-5678-9012-3456"}}'
        anonymized = payload_logger.anonymize_sensitive_data(data)
        assert '****-****-****-3456' in anonymized
        assert '1234-5678-9012-3456' not in anonymized

    def test_anonymize_headers(self, payload_logger):
        """Teste de anonimização de headers."""
        headers = {
            'authorization': 'Bearer token123',
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0'
        }
        anonymized = payload_logger.anonymize_headers(headers)
        assert anonymized['authorization'] == '[REDACTED]'
        assert anonymized['content-type'] == 'application/json'
        assert anonymized['user-agent'] == 'Mozilla/5.0'

    def test_truncate_data(self, payload_logger):
        """Teste de truncamento de dados."""
        large_data = "x" * 15000  # 15KB
        truncated = payload_logger.truncate_data(large_data, 10240)  # 10KB
        assert len(truncated.encode('utf-8')) <= 10240
        assert '[TRUNCATED]' in truncated

    def test_log_payload_dict(self, payload_logger):
        """Teste de logging de payload como dicionário."""
        payload = {"user": "test", "action": "login"}
        with patch('logging.info') as mock_log:
            payload_logger.log_payload(payload)
            mock_log.assert_called_once()

    def test_log_payload_bytes(self, payload_logger):
        """Teste de logging de payload como bytes."""
        payload = b'{"user": "test", "action": "login"}'
        with patch('logging.info') as mock_log:
            payload_logger.log_payload(payload)
            mock_log.assert_called_once()

    def test_log_headers(self, payload_logger):
        """Teste de logging de headers."""
        headers = {"content-type": "application/json", "user-agent": "test"}
        with patch('logging.info') as mock_log:
            payload_logger.log_headers(headers)
            mock_log.assert_called_once()

    def test_log_http_request(self, payload_logger):
        """Teste de logging de requisição HTTP."""
        with patch.object(payload_logger, 'log_headers') as mock_headers:
            with patch.object(payload_logger, 'log_payload') as mock_payload:
                payload_logger.log_http_request(
                    method="POST",
                    url="/api/login",
                    headers={"content-type": "application/json"},
                    payload={"user": "test", "password": "secret"}
                )
                mock_headers.assert_called_once()
                mock_payload.assert_called_once()

    def test_log_http_response(self, payload_logger):
        """Teste de logging de resposta HTTP."""
        with patch.object(payload_logger, 'log_headers') as mock_headers:
            with patch.object(payload_logger, 'log_payload') as mock_payload:
                payload_logger.log_http_response(
                    status_code=200,
                    headers={"content-type": "application/json"},
                    payload={"status": "success"}
                )
                mock_headers.assert_called_once()
                mock_payload.assert_called_once()


class TestTelemetryManager:
    """Testes para TelemetryManager."""
    
    @pytest.fixture
    def telemetry_manager(self):
        """Fixture para criar TelemetryManager."""
        return TelemetryManager("test-service")
    
    @pytest.fixture
    def initialized_telemetry_manager(self):
        """Fixture para TelemetryManager inicializado."""
        manager = TelemetryManager("test-service")
        with patch('opentelemetry.sdk.trace.TracerProvider'):
            with patch('opentelemetry.sdk.metrics.MeterProvider'):
                with patch('prometheus_client.start_http_server'):
                    manager.initialize()
        return manager

    def test_telemetry_manager_initialization(self, telemetry_manager):
        """Teste de inicialização do TelemetryManager."""
        assert telemetry_manager.service_name == "test-service"
        assert telemetry_manager.tracer is None
        assert telemetry_manager.meter is None
        assert telemetry_manager._initialized is False
        assert isinstance(telemetry_manager.payload_logger, PayloadLogger)
        assert telemetry_manager.config["jaeger_endpoint"] == "http://localhost:14268/api/traces"
        assert telemetry_manager.config["prometheus_port"] == 9090
        assert telemetry_manager.config["sampling_rate"] == 0.1

    def test_telemetry_manager_initialize(self, telemetry_manager):
        """Teste de inicialização completa do TelemetryManager."""
        with patch('opentelemetry.sdk.trace.TracerProvider') as mock_tracer_provider:
            with patch('opentelemetry.sdk.metrics.MeterProvider') as mock_meter_provider:
                with patch('prometheus_client.start_http_server') as mock_prometheus:
                    with patch('opentelemetry.instrumentation.flask.FlaskInstrumentor') as mock_flask:
                        with patch('opentelemetry.instrumentation.requests.RequestsInstrumentor') as mock_requests:
                            with patch('opentelemetry.instrumentation.sqlalchemy.SQLAlchemyInstrumentor') as mock_sqlalchemy:
                                telemetry_manager.initialize()
                                
                                assert telemetry_manager._initialized is True
                                mock_tracer_provider.assert_called_once()
                                mock_meter_provider.assert_called_once()
                                mock_prometheus.assert_called_once()

    def test_trace_operation_context_manager(self, initialized_telemetry_manager):
        """Teste do context manager de tracing."""
        with patch.object(initialized_telemetry_manager.tracer, 'start_span') as mock_start_span:
            mock_span = Mock()
            mock_start_span.return_value = mock_span
            
            with initialized_telemetry_manager.trace_operation("test_operation", {"key": "value"}):
                pass
            
            mock_start_span.assert_called_once_with("test_operation", attributes={"key": "value"})
            mock_span.end.assert_called_once()

    def test_trace_operation_with_exception(self, initialized_telemetry_manager):
        """Teste do context manager de tracing com exceção."""
        with patch.object(initialized_telemetry_manager.tracer, 'start_span') as mock_start_span:
            mock_span = Mock()
            mock_start_span.return_value = mock_span
            
            with pytest.raises(ValueError):
                with initialized_telemetry_manager.trace_operation("test_operation"):
                    raise ValueError("Test error")
            
            mock_span.record_exception.assert_called_once()
            mock_span.set_status.assert_called_once()

    def test_record_metric(self, initialized_telemetry_manager):
        """Teste de registro de métrica."""
        with patch.object(initialized_telemetry_manager.meter, 'create_counter') as mock_create_counter:
            mock_counter = Mock()
            mock_create_counter.return_value = mock_counter
            
            initialized_telemetry_manager.record_metric("test_metric", 1, {"label": "value"})
            
            mock_create_counter.assert_called_once_with("test_metric")
            mock_counter.add.assert_called_once_with(1, {"label": "value"})

    def test_log_event(self, initialized_telemetry_manager):
        """Teste de logging de evento."""
        with patch.object(initialized_telemetry_manager.logger, 'info') as mock_info:
            initialized_telemetry_manager.log_event(
                "test_event",
                "Test message",
                {"extra": "data"}
            )
            
            mock_info.assert_called_once()
            call_args = mock_info.call_args[0][0]
            assert "EVENT: test_event - Test message" in call_args

    def test_get_telemetry_manager(self):
        """Teste da função get_telemetry_manager."""
        manager = get_telemetry_manager()
        assert isinstance(manager, TelemetryManager)

    def test_initialize_telemetry(self):
        """Teste da função initialize_telemetry."""
        with patch('infrastructure.observability.telemetry.TelemetryManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            
            result = initialize_telemetry("test-service")
            
            mock_manager_class.assert_called_once_with("test-service")
            mock_manager.initialize.assert_called_once()
            assert result == mock_manager

    def test_traced_operation_decorator(self):
        """Teste do decorador traced_operation."""
        with patch('infrastructure.observability.telemetry.telemetry_manager') as mock_manager:
            mock_manager.trace_operation.return_value.__enter__ = Mock()
            mock_manager.trace_operation.return_value.__exit__ = Mock()
            
            @traced_operation("test_operation", {"key": "value"})
            def test_function():
                return "success"
            
            result = test_function()
            
            assert result == "success"
            mock_manager.trace_operation.assert_called_once_with("test_operation", {"key": "value"})

    def test_monitored_metric_decorator_success(self):
        """Teste do decorador monitored_metric com sucesso."""
        with patch('infrastructure.observability.telemetry.telemetry_manager') as mock_manager:
            with patch('time.time') as mock_time:
                mock_time.side_effect = [100.0, 100.5]  # start_time, end_time
                
                @monitored_metric("test_metric", {"label": "value"})
                def test_function():
                    return "success"
                
                result = test_function()
                
                assert result == "success"
                assert mock_manager.record_metric.call_count == 2
                mock_manager.record_metric.assert_any_call("test_metric_success", 1, {"label": "value"})
                mock_manager.record_metric.assert_any_call("test_metric_duration", 0.5, {"label": "value"})

    def test_monitored_metric_decorator_error(self):
        """Teste do decorador monitored_metric com erro."""
        with patch('infrastructure.observability.telemetry.telemetry_manager') as mock_manager:
            with patch('time.time') as mock_time:
                mock_time.side_effect = [100.0, 100.5]  # start_time, end_time
                
                @monitored_metric("test_metric", {"label": "value"})
                def test_function():
                    raise ValueError("Test error")
                
                with pytest.raises(ValueError):
                    test_function()
                
                assert mock_manager.record_metric.call_count == 2
                mock_manager.record_metric.assert_any_call("test_metric_error", 1, {"label": "value"})
                mock_manager.record_metric.assert_any_call("test_metric_duration", 0.5, {"label": "value"})


class TestMetricsManager:
    """Testes para MetricsManager."""
    
    @pytest.fixture
    def metrics_manager(self):
        """Fixture para criar MetricsManager."""
        return MetricsManager("test-service")
    
    @pytest.fixture
    def initialized_metrics_manager(self):
        """Fixture para MetricsManager inicializado."""
        manager = MetricsManager("test-service")
        with patch('prometheus_client.start_http_server'):
            with patch('prometheus_client.Counter'):
                with patch('prometheus_client.Gauge'):
                    with patch('prometheus_client.Histogram'):
                        manager._setup_metrics()
        return manager

    def test_metrics_manager_initialization(self, metrics_manager):
        """Teste de inicialização do MetricsManager."""
        assert metrics_manager.service_name == "test-service"
        assert metrics_manager._initialized is False
        assert metrics_manager.config["prometheus_port"] == 9090
        assert metrics_manager.config["metrics_prefix"] == "omni_keywords_finder"
        assert metrics_manager.config["environment"] == "development"
        assert metrics_manager.config["enable_default_metrics"] is True

    def test_record_http_request(self, initialized_metrics_manager):
        """Teste de registro de requisição HTTP."""
        with patch.object(initialized_metrics_manager.metrics["http_requests_total"], 'inc') as mock_inc:
            with patch.object(initialized_metrics_manager.metrics["http_request_duration_seconds"], 'observe') as mock_observe:
                initialized_metrics_manager.record_http_request("POST", "/api/test", 200, 0.5)
                
                mock_inc.assert_called_once_with(method="POST", endpoint="/api/test", status_code=200)
                mock_observe.assert_called_once_with(0.5, method="POST", endpoint="/api/test")

    def test_record_error(self, initialized_metrics_manager):
        """Teste de registro de erro."""
        with patch.object(initialized_metrics_manager.metrics["errors_total"], 'inc') as mock_inc:
            initialized_metrics_manager.record_error("ValueError", "test-service", "Test error message")
            
            mock_inc.assert_called_once_with(error_type="ValueError", service="test-service")

    def test_record_keyword_processed(self, initialized_metrics_manager):
        """Teste de registro de keyword processada."""
        with patch.object(initialized_metrics_manager.metrics["keywords_processed_total"], 'inc') as mock_inc:
            initialized_metrics_manager.record_keyword_processed("google", "success", "marketing", 5)
            
            mock_inc.assert_called_once_with(source="google", status="success", niche="marketing")

    def test_record_keyword_processing_duration(self, initialized_metrics_manager):
        """Teste de registro de duração de processamento de keyword."""
        with patch.object(initialized_metrics_manager.metrics["keywords_processing_duration_seconds"], 'observe') as mock_observe:
            initialized_metrics_manager.record_keyword_processing_duration("google", "marketing", 1.5)
            
            mock_observe.assert_called_once_with(1.5, source="google", niche="marketing")

    def test_record_cache_hit(self, initialized_metrics_manager):
        """Teste de registro de cache hit."""
        with patch.object(initialized_metrics_manager.metrics["cache_hits_total"], 'inc') as mock_inc:
            initialized_metrics_manager.record_cache_hit("redis", "keyword:*")
            
            mock_inc.assert_called_once_with(cache_type="redis", key_pattern="keyword:*")

    def test_record_cache_miss(self, initialized_metrics_manager):
        """Teste de registro de cache miss."""
        with patch.object(initialized_metrics_manager.metrics["cache_misses_total"], 'inc') as mock_inc:
            initialized_metrics_manager.record_cache_miss("redis", "keyword:*")
            
            mock_inc.assert_called_once_with(cache_type="redis", key_pattern="keyword:*")

    def test_record_execution(self, initialized_metrics_manager):
        """Teste de registro de execução."""
        with patch.object(initialized_metrics_manager.metrics["executions_total"], 'inc') as mock_inc:
            with patch.object(initialized_metrics_manager.metrics["execution_duration_seconds"], 'observe') as mock_observe:
                initialized_metrics_manager.record_execution("batch", "success", 10.5)
                
                mock_inc.assert_called_once_with(execution_type="batch", status="success")
                mock_observe.assert_called_once_with(10.5, execution_type="batch")

    def test_record_external_api_call(self, initialized_metrics_manager):
        """Teste de registro de chamada para API externa."""
        with patch.object(initialized_metrics_manager.metrics["external_api_calls_total"], 'inc') as mock_inc:
            with patch.object(initialized_metrics_manager.metrics["external_api_duration_seconds"], 'observe') as mock_observe:
                initialized_metrics_manager.record_external_api_call("google", "/search", "success", 2.5)
                
                mock_inc.assert_called_once_with(api_name="google", endpoint="/search", status="success")
                mock_observe.assert_called_once_with(2.5, api_name="google", endpoint="/search")

    def test_set_memory_usage(self, initialized_metrics_manager):
        """Teste de definição de uso de memória."""
        with patch.object(initialized_metrics_manager.metrics["memory_usage_bytes"], 'set') as mock_set:
            initialized_metrics_manager.set_memory_usage("test-service", 1024000)
            
            mock_set.assert_called_once_with(1024000, service="test-service")

    def test_set_cpu_usage(self, initialized_metrics_manager):
        """Teste de definição de uso de CPU."""
        with patch.object(initialized_metrics_manager.metrics["cpu_usage_percent"], 'set') as mock_set:
            initialized_metrics_manager.set_cpu_usage("test-service", 75.5)
            
            mock_set.assert_called_once_with(75.5, service="test-service")

    def test_set_active_connections(self, initialized_metrics_manager):
        """Teste de definição de conexões ativas."""
        with patch.object(initialized_metrics_manager.metrics["active_connections"], 'set') as mock_set:
            initialized_metrics_manager.set_active_connections("database", 10)
            
            mock_set.assert_called_once_with(10, connection_type="database")

    def test_get_metrics_manager(self):
        """Teste da função get_metrics_manager."""
        manager = get_metrics_manager()
        assert isinstance(manager, MetricsManager)

    def test_initialize_metrics(self):
        """Teste da função initialize_metrics."""
        with patch('infrastructure.observability.metrics.MetricsManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            
            result = initialize_metrics("test-service")
            
            mock_manager_class.assert_called_once_with("test-service")
            assert result == mock_manager

    def test_record_http_request_function(self):
        """Teste da função record_http_request."""
        with patch('infrastructure.observability.metrics.get_metrics_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_get_manager.return_value = mock_manager
            
            record_http_request("GET", "/api/test", 200, 0.3)
            
            mock_manager.record_http_request.assert_called_once_with("GET", "/api/test", 200, 0.3)

    def test_record_error_function(self):
        """Teste da função record_error."""
        with patch('infrastructure.observability.metrics.get_metrics_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_get_manager.return_value = mock_manager
            
            record_error("ValueError", "test-service", "Test error")
            
            mock_manager.record_error.assert_called_once_with("ValueError", "test-service", "Test error")

    def test_record_keyword_processed_function(self):
        """Teste da função record_keyword_processed."""
        with patch('infrastructure.observability.metrics.get_metrics_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_get_manager.return_value = mock_manager
            
            record_keyword_processed("google", "success", "marketing", 3)
            
            mock_manager.record_keyword_processed.assert_called_once_with("google", "success", "marketing", 3)

    def test_record_cache_hit_function(self):
        """Teste da função record_cache_hit."""
        with patch('infrastructure.observability.metrics.get_metrics_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_get_manager.return_value = mock_manager
            
            record_cache_hit("redis", "keyword:*")
            
            mock_manager.record_cache_hit.assert_called_once_with("redis", "keyword:*")

    def test_record_cache_miss_function(self):
        """Teste da função record_cache_miss."""
        with patch('infrastructure.observability.metrics.get_metrics_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_get_manager.return_value = mock_manager
            
            record_cache_miss("redis", "keyword:*")
            
            mock_manager.record_cache_miss.assert_called_once_with("redis", "keyword:*")


class TestOpenTelemetryConfig:
    """Testes para OpenTelemetryConfig."""
    
    @pytest.fixture
    def ot_config(self):
        """Fixture para criar OpenTelemetryConfig."""
        return OpenTelemetryConfig("development")
    
    @pytest.fixture
    def initialized_ot_config(self):
        """Fixture para OpenTelemetryConfig inicializado."""
        config = OpenTelemetryConfig("development")
        with patch('opentelemetry.sdk.trace.TracerProvider'):
            with patch('opentelemetry.sdk.metrics.MeterProvider'):
                config.setup_tracing()
                config.setup_metrics()
        return config

    def test_opentelemetry_config_initialization(self, ot_config):
        """Teste de inicialização do OpenTelemetryConfig."""
        assert ot_config.environment == "development"
        assert ot_config.service_name == "omni-keywords-finder"
        assert ot_config.sampling_rate == 1.0  # 100% para development
        assert "console" in ot_config.exporters
        assert "console_metrics" in ot_config.exporters

    def test_get_sampling_rate(self, ot_config):
        """Teste de obtenção de taxa de sampling."""
        assert ot_config._get_sampling_rate() == 1.0  # development
        
        staging_config = OpenTelemetryConfig("staging")
        assert staging_config._get_sampling_rate() == 0.5  # staging
        
        production_config = OpenTelemetryConfig("production")
        assert production_config._get_sampling_rate() == 0.1  # production

    def test_configure_exporters(self, ot_config):
        """Teste de configuração de exportadores."""
        exporters = ot_config._configure_exporters()
        assert "console" in exporters
        assert "console_metrics" in exporters

    def test_setup_tracing(self, ot_config):
        """Teste de configuração de tracing."""
        with patch('opentelemetry.sdk.trace.TracerProvider') as mock_tracer_provider:
            with patch('opentelemetry.sdk.trace.export.BatchSpanProcessor'):
                with patch('opentelemetry.trace.set_tracer_provider'):
                    with patch('opentelemetry.trace.get_tracer'):
                        ot_config.setup_tracing()
                        assert ot_config.tracer_provider is not None

    def test_setup_metrics(self, ot_config):
        """Teste de configuração de métricas."""
        with patch('opentelemetry.sdk.metrics.MeterProvider') as mock_meter_provider:
            with patch('opentelemetry.sdk.metrics.export.PeriodicExportingMetricReader'):
                with patch('opentelemetry.metrics.set_meter_provider'):
                    with patch('opentelemetry.metrics.get_meter'):
                        ot_config.setup_metrics()
                        assert ot_config.meter_provider is not None

    def test_create_custom_metrics(self, initialized_ot_config):
        """Teste de criação de métricas customizadas."""
        with patch.object(initialized_ot_config.meter, 'create_counter') as mock_counter:
            with patch.object(initialized_ot_config.meter, 'create_histogram') as mock_histogram:
                with patch.object(initialized_ot_config.meter, 'create_up_down_counter') as mock_up_down_counter:
                    initialized_ot_config._create_custom_metrics()
                    
                    # Verificar se as métricas foram criadas
                    assert mock_counter.call_count >= 4  # api_request, business_operation, cache_hit, cache_miss
                    assert mock_histogram.call_count >= 1  # api_duration
                    assert mock_up_down_counter.call_count >= 1  # active_connections

    def test_trace_operation_context_manager(self, initialized_ot_config):
        """Teste do context manager de tracing."""
        with patch.object(initialized_ot_config.tracer, 'start_span') as mock_start_span:
            mock_span = Mock()
            mock_start_span.return_value = mock_span
            
            with initialized_ot_config.trace_operation("test_operation", {"key": "value"}):
                pass
            
            mock_start_span.assert_called_once_with("test_operation", kind=Mock(), attributes={"key": "value"})
            mock_span.set_status.assert_called_once()
            mock_span.end.assert_called_once()

    def test_record_api_request(self, initialized_ot_config):
        """Teste de registro de requisição de API."""
        with patch.object(initialized_ot_config.api_request_counter, 'add') as mock_add:
            with patch.object(initialized_ot_config.api_duration_histogram, 'record') as mock_record:
                initialized_ot_config.record_api_request("POST", "/api/test", 200, 0.5)
                
                mock_add.assert_called_once_with(1, {
                    "endpoint": "/api/test",
                    "method": "POST",
                    "status_code": "200"
                })
                mock_record.assert_called_once_with(0.5, {
                    "endpoint": "/api/test",
                    "method": "POST"
                })

    def test_record_business_operation(self, initialized_ot_config):
        """Teste de registro de operação de negócio."""
        with patch.object(initialized_ot_config.business_operation_counter, 'add') as mock_add:
            initialized_ot_config.record_business_operation("keyword_processing", "success")
            
            mock_add.assert_called_once_with(1, {
                "operation": "keyword_processing",
                "status": "success"
            })

    def test_record_cache_operation(self, initialized_ot_config):
        """Teste de registro de operação de cache."""
        with patch.object(initialized_ot_config.cache_hit_counter, 'add') as mock_hit_add:
            with patch.object(initialized_ot_config.cache_miss_counter, 'add') as mock_miss_add:
                # Teste de cache hit
                initialized_ot_config.record_cache_operation("keyword_cache", True)
                mock_hit_add.assert_called_once_with(1, {"operation": "keyword_cache"})
                
                # Teste de cache miss
                initialized_ot_config.record_cache_operation("keyword_cache", False)
                mock_miss_add.assert_called_once_with(1, {"operation": "keyword_cache"})

    def test_update_active_connections(self, initialized_ot_config):
        """Teste de atualização de conexões ativas."""
        with patch.object(initialized_ot_config.active_connections_counter, 'add') as mock_add:
            initialized_ot_config.update_active_connections(5)
            
            mock_add.assert_called_once_with(5)

    def test_shutdown(self, initialized_ot_config):
        """Teste de shutdown do OpenTelemetry."""
        with patch.object(initialized_ot_config.tracer_provider, 'shutdown') as mock_tracer_shutdown:
            with patch.object(initialized_ot_config.meter_provider, 'shutdown') as mock_meter_shutdown:
                initialized_ot_config.shutdown()
                
                mock_tracer_shutdown.assert_called_once()
                mock_meter_shutdown.assert_called_once()

    def test_initialize_observability(self):
        """Teste da função initialize_observability."""
        with patch('infrastructure.observability.opentelemetry_config.OpenTelemetryConfig') as mock_config_class:
            mock_config = Mock()
            mock_config_class.return_value = mock_config
            
            result = initialize_observability("development")
            
            mock_config_class.assert_called_once_with("development")
            mock_config.setup_tracing.assert_called_once()
            mock_config.setup_metrics.assert_called_once()
            assert result == mock_config 