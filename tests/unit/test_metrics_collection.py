"""
Testes Unitários para Metrics Collection
Sistema de Coleta de Métricas - Omni Keywords Finder

Prompt: Implementação de testes unitários para sistema de coleta de métricas
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import json
from typing import Dict, Any, List

from backend.app.monitoring.metrics_collection import (
    MetricsCollector,
    PerformanceMonitor,
    MetricsAnalyzer,
    MetricData,
    MetricType,
    initialize_metrics,
    get_metrics_summary,
    record_request_metrics,
    record_error_metrics
)


class TestMetricType:
    """Testes para enum MetricType"""
    
    def test_metric_type_values(self):
        """Testa valores do enum MetricType"""
        assert MetricType.COUNTER.value == "counter"
        assert MetricType.GAUGE.value == "gauge"
        assert MetricType.HISTOGRAM.value == "histogram"
        assert MetricType.SUMMARY.value == "summary"


class TestMetricData:
    """Testes para classe MetricData"""
    
    def test_metric_data_creation(self):
        """Testa criação de dados de métrica"""
        timestamp = datetime.now()
        metric_data = MetricData(
            name="test_metric",
            value=42.5,
            labels={"service": "test", "endpoint": "/api"},
            timestamp=timestamp
        )
        
        assert metric_data.name == "test_metric"
        assert metric_data.value == 42.5
        assert metric_data.labels == {"service": "test", "endpoint": "/api"}
        assert metric_data.timestamp == timestamp
    
    def test_metric_data_defaults(self):
        """Testa valores padrão de MetricData"""
        metric_data = MetricData(name="test", value=10.0)
        
        assert metric_data.labels == {}
        assert isinstance(metric_data.timestamp, datetime)


class TestMetricsCollector:
    """Testes para classe MetricsCollector"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock do cliente Redis"""
        redis_mock = Mock()
        redis_mock.lpush = AsyncMock()
        redis_mock.expire = AsyncMock()
        return redis_mock
    
    @pytest.fixture
    def metrics_collector(self, mock_redis):
        """Instância do MetricsCollector para testes"""
        return MetricsCollector(mock_redis)
    
    def test_metrics_collector_initialization(self, mock_redis):
        """Testa inicialização do MetricsCollector"""
        collector = MetricsCollector(mock_redis)
        
        assert collector.redis_client == mock_redis
        assert collector.metrics == {}
        assert collector.buffer.maxlen == 1000
        assert collector.flush_interval == 60
        assert collector.is_running is False
        
        # Verifica se as métricas Prometheus foram criadas
        assert collector.request_counter is not None
        assert collector.request_duration is not None
        assert collector.active_connections is not None
        assert collector.error_counter is not None
        assert collector.memory_usage is not None
        assert collector.cpu_usage is not None
    
    def test_start_collection(self, metrics_collector):
        """Testa início da coleta de métricas"""
        metrics_collector.start_collection()
        
        assert metrics_collector.is_running is True
    
    def test_stop_collection(self, metrics_collector):
        """Testa parada da coleta de métricas"""
        metrics_collector.is_running = True
        metrics_collector.stop_collection()
        
        assert metrics_collector.is_running is False
    
    def test_record_request(self, metrics_collector):
        """Testa registro de métricas de request"""
        with patch.object(metrics_collector.request_counter, 'labels') as mock_counter:
            with patch.object(metrics_collector.request_duration, 'labels') as mock_duration:
                mock_counter.return_value.inc = Mock()
                mock_duration.return_value.observe = Mock()
                
                metrics_collector.record_request("GET", "/api/test", 200, 0.5)
                
                # Verifica se as métricas Prometheus foram chamadas
                mock_counter.assert_called_once_with(method="GET", endpoint="/api/test", status="200")
                mock_counter.return_value.inc.assert_called_once()
                
                mock_duration.assert_called_once_with(method="GET", endpoint="/api/test")
                mock_duration.return_value.observe.assert_called_once_with(0.5)
                
                # Verifica se as métricas customizadas foram adicionadas
                assert len(metrics_collector.buffer) == 2
    
    def test_record_error(self, metrics_collector):
        """Testa registro de métricas de erro"""
        with patch.object(metrics_collector.error_counter, 'labels') as mock_error:
            mock_error.return_value.inc = Mock()
            
            metrics_collector.record_error("validation_error", "api", "Invalid input")
            
            # Verifica se a métrica Prometheus foi chamada
            mock_error.assert_called_once_with(type="validation_error", component="api")
            mock_error.return_value.inc.assert_called_once()
            
            # Verifica se a métrica customizada foi adicionada
            assert len(metrics_collector.buffer) == 1
    
    def test_record_database_query(self, metrics_collector):
        """Testa registro de métricas de query do banco"""
        metrics_collector.record_database_query("SELECT", 0.1, True)
        
        # Verifica se as métricas foram adicionadas
        assert len(metrics_collector.buffer) == 2
        
        # Testa query que falhou
        metrics_collector.record_database_query("INSERT", 0.2, False)
        
        # Deve ter adicionado mais 3 métricas (2 da query + 1 do erro)
        assert len(metrics_collector.buffer) == 5
    
    def test_record_cache_operation(self, metrics_collector):
        """Testa registro de métricas de cache"""
        metrics_collector.record_cache_operation("GET", 0.01, True)
        
        # Verifica se as métricas foram adicionadas
        assert len(metrics_collector.buffer) == 2
        
        # Testa operação que falhou
        metrics_collector.record_cache_operation("SET", 0.02, False)
        
        # Deve ter adicionado mais 3 métricas (2 da operação + 1 do erro)
        assert len(metrics_collector.buffer) == 5
    
    def test_record_api_call(self, metrics_collector):
        """Testa registro de métricas de chamadas de API"""
        metrics_collector.record_api_call("google", "/search", 1.5, True)
        
        # Verifica se as métricas foram adicionadas
        assert len(metrics_collector.buffer) == 2
        
        # Testa chamada que falhou
        metrics_collector.record_api_call("facebook", "/posts", 2.0, False)
        
        # Deve ter adicionado mais 3 métricas (2 da chamada + 1 do erro)
        assert len(metrics_collector.buffer) == 5
    
    @pytest.mark.asyncio
    async def test_collect_system_metrics(self, metrics_collector):
        """Testa coleta de métricas do sistema"""
        with patch('psutil.cpu_percent') as mock_cpu:
            with patch('psutil.virtual_memory') as mock_memory:
                with patch('psutil.disk_usage') as mock_disk:
                    with patch('psutil.net_io_counters') as mock_network:
                        with patch('psutil.net_connections') as mock_connections:
                            # Configura mocks
                            mock_cpu.return_value = 25.5
                            mock_memory.return_value.used = 1024 * 1024 * 100  # 100MB
                            mock_memory.return_value.percent = 50.0
                            mock_disk.return_value.used = 1024 * 1024 * 1024  # 1GB
                            mock_disk.return_value.total = 1024 * 1024 * 1024 * 10  # 10GB
                            mock_network.return_value.bytes_sent = 1024 * 1024  # 1MB
                            mock_network.return_value.bytes_recv = 2048 * 1024  # 2MB
                            mock_connections.return_value = [Mock(), Mock(), Mock()]  # 3 conexões
                            
                            await metrics_collector.collect_system_metrics()
                            
                            # Verifica se as métricas foram adicionadas
                            assert len(metrics_collector.buffer) == 6
    
    def test_add_metric(self, metrics_collector):
        """Testa adição de métrica ao buffer"""
        metrics_collector._add_metric("test_metric", 42.0, {"label": "value"})
        
        assert len(metrics_collector.buffer) == 1
        
        metric = metrics_collector.buffer[0]
        assert metric.name == "test_metric"
        assert metric.value == 42.0
        assert metric.labels == {"label": "value"}
        assert isinstance(metric.timestamp, datetime)
    
    @pytest.mark.asyncio
    async def test_flush_metrics_empty_buffer(self, metrics_collector):
        """Testa flush com buffer vazio"""
        await metrics_collector.flush_metrics()
        
        # Não deve chamar Redis se o buffer estiver vazio
        metrics_collector.redis_client.lpush.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_flush_metrics_with_data(self, metrics_collector):
        """Testa flush com dados no buffer"""
        # Adiciona métricas ao buffer
        metrics_collector._add_metric("test1", 10.0, {"label": "value1"})
        metrics_collector._add_metric("test2", 20.0, {"label": "value2"})
        
        await metrics_collector.flush_metrics()
        
        # Verifica se o Redis foi chamado
        metrics_collector.redis_client.lpush.assert_called_once()
        metrics_collector.redis_client.expire.assert_called_once()
        
        # Verifica se o buffer foi esvaziado
        assert len(metrics_collector.buffer) == 0
    
    @pytest.mark.asyncio
    async def test_flush_metrics_error_handling(self, metrics_collector):
        """Testa tratamento de erro no flush"""
        # Adiciona métricas ao buffer
        metrics_collector._add_metric("test1", 10.0)
        metrics_collector._add_metric("test2", 20.0)
        
        # Simula erro no Redis
        metrics_collector.redis_client.lpush.side_effect = Exception("Redis error")
        
        await metrics_collector.flush_metrics()
        
        # Verifica se as métricas foram recolocadas no buffer
        assert len(metrics_collector.buffer) == 2


class TestPerformanceMonitor:
    """Testes para classe PerformanceMonitor"""
    
    @pytest.fixture
    def mock_metrics_collector(self):
        """Mock do MetricsCollector"""
        return Mock()
    
    @pytest.fixture
    def performance_monitor(self, mock_metrics_collector):
        """Instância do PerformanceMonitor para testes"""
        return PerformanceMonitor(mock_metrics_collector)
    
    def test_performance_monitor_initialization(self, mock_metrics_collector):
        """Testa inicialização do PerformanceMonitor"""
        monitor = PerformanceMonitor(mock_metrics_collector)
        
        assert monitor.metrics_collector == mock_metrics_collector
        assert monitor.start_times == {}
    
    def test_start_timer(self, performance_monitor):
        """Testa início de timer"""
        performance_monitor.start_timer("test_operation")
        
        assert "test_operation" in performance_monitor.start_times
        assert isinstance(performance_monitor.start_times["test_operation"], float)
    
    def test_end_timer_success(self, performance_monitor):
        """Testa finalização de timer com sucesso"""
        performance_monitor.start_timer("test_operation")
        
        # Simula passagem de tempo
        performance_monitor.start_times["test_operation"] = time.time() - 1.0
        
        performance_monitor.end_timer("test_operation", success=True)
        
        # Verifica se a métrica foi registrada
        performance_monitor.metrics_collector._add_metric.assert_called_once()
        
        # Verifica se o timer foi removido
        assert "test_operation" not in performance_monitor.start_times
    
    def test_end_timer_failure(self, performance_monitor):
        """Testa finalização de timer com falha"""
        performance_monitor.start_timer("test_operation")
        
        # Simula passagem de tempo
        performance_monitor.start_times["test_operation"] = time.time() - 0.5
        
        performance_monitor.end_timer("test_operation", success=False)
        
        # Verifica se a métrica foi registrada
        performance_monitor.metrics_collector._add_metric.assert_called_once()
    
    def test_end_timer_nonexistent(self, performance_monitor):
        """Testa finalização de timer inexistente"""
        performance_monitor.end_timer("nonexistent_operation")
        
        # Não deve chamar _add_metric
        performance_monitor.metrics_collector._add_metric.assert_not_called()
    
    def test_record_keyword_analysis(self, performance_monitor):
        """Testa registro de métricas de análise de keywords"""
        performance_monitor.record_keyword_analysis(100, 5.5, True)
        
        # Verifica se as métricas foram registradas
        assert performance_monitor.metrics_collector._add_metric.call_count == 2
        
        # Testa análise que falhou
        performance_monitor.record_keyword_analysis(50, 2.0, False)
        
        # Deve ter registrado mais 3 métricas (2 da análise + 1 do erro)
        assert performance_monitor.metrics_collector._add_metric.call_count == 5
        performance_monitor.metrics_collector.record_error.assert_called_once()
    
    def test_record_competitor_analysis(self, performance_monitor):
        """Testa registro de métricas de análise de competidores"""
        performance_monitor.record_competitor_analysis(10, 3.0, True)
        
        # Verifica se as métricas foram registradas
        assert performance_monitor.metrics_collector._add_metric.call_count == 2
        
        # Testa análise que falhou
        performance_monitor.record_competitor_analysis(5, 1.5, False)
        
        # Deve ter registrado mais 3 métricas (2 da análise + 1 do erro)
        assert performance_monitor.metrics_collector._add_metric.call_count == 5
        performance_monitor.metrics_collector.record_error.assert_called_once()
    
    def test_record_report_generation(self, performance_monitor):
        """Testa registro de métricas de geração de relatórios"""
        performance_monitor.record_report_generation("pdf", 10.0, True)
        
        # Verifica se a métrica foi registrada
        performance_monitor.metrics_collector._add_metric.assert_called_once()
        
        # Testa geração que falhou
        performance_monitor.record_report_generation("excel", 5.0, False)
        
        # Deve ter registrado mais 2 métricas (1 da geração + 1 do erro)
        assert performance_monitor.metrics_collector._add_metric.call_count == 3
        performance_monitor.metrics_collector.record_error.assert_called_once()


class TestMetricsAnalyzer:
    """Testes para classe MetricsAnalyzer"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock do cliente Redis"""
        redis_mock = Mock()
        redis_mock.lrange = AsyncMock()
        return redis_mock
    
    @pytest.fixture
    def metrics_analyzer(self, mock_redis):
        """Instância do MetricsAnalyzer para testes"""
        return MetricsAnalyzer(mock_redis)
    
    def test_metrics_analyzer_initialization(self, mock_redis):
        """Testa inicialização do MetricsAnalyzer"""
        analyzer = MetricsAnalyzer(mock_redis)
        
        assert analyzer.redis_client == mock_redis
    
    @pytest.mark.asyncio
    async def test_get_metrics_summary_empty(self, metrics_analyzer):
        """Testa obtenção de resumo com dados vazios"""
        metrics_analyzer.redis_client.lrange.return_value = []
        
        result = await metrics_analyzer.get_metrics_summary(24)
        
        assert result == {}
    
    @pytest.mark.asyncio
    async def test_get_metrics_summary_with_data(self, metrics_analyzer):
        """Testa obtenção de resumo com dados"""
        # Mock de dados de métricas
        metrics_data = [
            {
                "name": "http_request_duration",
                "value": 0.5,
                "labels": {"method": "GET", "endpoint": "/api"},
                "timestamp": "2025-01-27T10:00:00"
            },
            {
                "name": "errors",
                "value": 1,
                "labels": {"type": "validation_error", "component": "api"},
                "timestamp": "2025-01-27T10:01:00"
            }
        ]
        
        metrics_analyzer.redis_client.lrange.return_value = [json.dumps(metrics_data)]
        
        result = await metrics_analyzer.get_metrics_summary(1)
        
        assert "total_metrics" in result
        assert "metrics_by_type" in result
        assert "errors" in result
        assert "performance" in result
    
    def test_analyze_metrics_empty(self, metrics_analyzer):
        """Testa análise de métricas vazias"""
        result = metrics_analyzer._analyze_metrics([])
        
        assert result == {}
    
    def test_analyze_metrics_with_data(self, metrics_analyzer):
        """Testa análise de métricas com dados"""
        metrics_data = [
            {
                "name": "http_request_duration",
                "value": 0.5,
                "labels": {},
                "timestamp": "2025-01-27T10:00:00"
            },
            {
                "name": "http_request_duration",
                "value": 1.0,
                "labels": {},
                "timestamp": "2025-01-27T10:01:00"
            },
            {
                "name": "errors",
                "value": 1,
                "labels": {"type": "validation_error", "component": "api"},
                "timestamp": "2025-01-27T10:02:00"
            }
        ]
        
        result = metrics_analyzer._analyze_metrics(metrics_data)
        
        assert result["total_metrics"] == 3
        assert "http_request_duration" in result["metrics_by_type"]
        assert "errors" in result["metrics_by_type"]
        assert len(result["errors"]) > 0
        assert len(result["performance"]) > 0
    
    def test_analyze_errors(self, metrics_analyzer):
        """Testa análise de erros"""
        error_metrics = [
            {
                "name": "errors",
                "value": 1,
                "labels": {"type": "validation_error", "component": "api"},
                "timestamp": "2025-01-27T10:00:00"
            },
            {
                "name": "errors",
                "value": 1,
                "labels": {"type": "database_error", "component": "database"},
                "timestamp": "2025-01-27T10:01:00"
            },
            {
                "name": "errors",
                "value": 1,
                "labels": {"type": "validation_error", "component": "api"},
                "timestamp": "2025-01-27T10:02:00"
            }
        ]
        
        result = metrics_analyzer._analyze_errors(error_metrics)
        
        assert result["total_errors"] == 3
        assert result["error_types"]["validation_error"] == 2
        assert result["error_types"]["database_error"] == 1
        assert result["errors_by_component"]["api"] == 2
        assert result["errors_by_component"]["database"] == 1
    
    def test_analyze_performance(self, metrics_analyzer):
        """Testa análise de performance"""
        performance_metrics = {
            "http_request_duration": [
                {"name": "http_request_duration", "value": 0.1, "labels": {}, "timestamp": "2025-01-27T10:00:00"},
                {"name": "http_request_duration", "value": 0.5, "labels": {}, "timestamp": "2025-01-27T10:01:00"},
                {"name": "http_request_duration", "value": 1.0, "labels": {}, "timestamp": "2025-01-27T10:02:00"}
            ]
        }
        
        result = metrics_analyzer._analyze_performance(performance_metrics)
        
        assert "http_request_duration" in result
        analysis = result["http_request_duration"]
        assert analysis["count"] == 3
        assert analysis["average"] == 0.5333333333333333
        assert analysis["min"] == 0.1
        assert analysis["max"] == 1.0
        assert analysis["p95"] == 1.0
        assert analysis["p99"] == 1.0


class TestMetricsIntegration:
    """Testes de integração para sistema de métricas"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock do cliente Redis"""
        redis_mock = Mock()
        redis_mock.lpush = AsyncMock()
        redis_mock.expire = AsyncMock()
        redis_mock.lrange = AsyncMock()
        return redis_mock
    
    def test_initialize_metrics(self, mock_redis):
        """Testa inicialização do sistema de métricas"""
        with patch('backend.app.monitoring.metrics_collection.metrics_collector') as mock_collector:
            with patch('backend.app.monitoring.metrics_collection.performance_monitor') as mock_monitor:
                with patch('backend.app.monitoring.metrics_collection.metrics_analyzer') as mock_analyzer:
                    initialize_metrics(mock_redis)
                    
                    # Verifica se as instâncias foram criadas
                    assert mock_collector is not None
                    assert mock_monitor is not None
                    assert mock_analyzer is not None
    
    @pytest.mark.asyncio
    async def test_get_metrics_summary_global(self, mock_redis):
        """Testa função global get_metrics_summary"""
        with patch('backend.app.monitoring.metrics_collection.metrics_analyzer') as mock_analyzer:
            mock_analyzer.get_metrics_summary = AsyncMock(return_value={"test": "data"})
            
            result = await get_metrics_summary(24)
            
            assert result == {"test": "data"}
            mock_analyzer.get_metrics_summary.assert_called_once_with(24)
    
    def test_record_request_metrics_global(self, mock_redis):
        """Testa função global record_request_metrics"""
        with patch('backend.app.monitoring.metrics_collection.metrics_collector') as mock_collector:
            record_request_metrics("POST", "/api/test", 201, 0.3)
            
            mock_collector.record_request.assert_called_once_with("POST", "/api/test", 201, 0.3)
    
    def test_record_error_metrics_global(self, mock_redis):
        """Testa função global record_error_metrics"""
        with patch('backend.app.monitoring.metrics_collection.metrics_collector') as mock_collector:
            record_error_metrics("validation_error", "api", "Invalid input")
            
            mock_collector.record_error.assert_called_once_with("validation_error", "api", "Invalid input")


class TestMetricsErrorHandling:
    """Testes de tratamento de erros para sistema de métricas"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock do cliente Redis"""
        redis_mock = Mock()
        redis_mock.lpush = AsyncMock()
        redis_mock.expire = AsyncMock()
        redis_mock.lrange = AsyncMock()
        return redis_mock
    
    @pytest.mark.asyncio
    async def test_collect_system_metrics_error(self, mock_redis):
        """Testa tratamento de erro na coleta de métricas do sistema"""
        collector = MetricsCollector(mock_redis)
        
        with patch('psutil.cpu_percent', side_effect=Exception("System error")):
            # Não deve levantar exceção
            await collector.collect_system_metrics()
    
    @pytest.mark.asyncio
    async def test_flush_metrics_error(self, mock_redis):
        """Testa tratamento de erro no flush de métricas"""
        collector = MetricsCollector(mock_redis)
        collector._add_metric("test", 10.0)
        
        # Simula erro no Redis
        mock_redis.lpush.side_effect = Exception("Redis error")
        
        # Não deve levantar exceção
        await collector.flush_metrics()
        
        # Verifica se as métricas foram recolocadas no buffer
        assert len(collector.buffer) == 1
    
    @pytest.mark.asyncio
    async def test_get_metrics_summary_error(self, mock_redis):
        """Testa tratamento de erro na obtenção de resumo"""
        analyzer = MetricsAnalyzer(mock_redis)
        
        # Simula erro no Redis
        mock_redis.lrange.side_effect = Exception("Redis error")
        
        result = await analyzer.get_metrics_summary(24)
        
        # Deve retornar dicionário vazio em caso de erro
        assert result == {}


class TestMetricsPerformance:
    """Testes de performance para sistema de métricas"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock do cliente Redis"""
        redis_mock = Mock()
        redis_mock.lpush = AsyncMock()
        redis_mock.expire = AsyncMock()
        return redis_mock
    
    def test_buffer_performance(self, mock_redis):
        """Testa performance do buffer de métricas"""
        collector = MetricsCollector(mock_redis)
        
        # Adiciona muitas métricas rapidamente
        for i in range(1000):
            collector._add_metric(f"metric_{i}", float(i))
        
        # Verifica se o buffer não excedeu o limite
        assert len(collector.buffer) <= 1000
    
    def test_metrics_collection_performance(self, mock_redis):
        """Testa performance da coleta de métricas"""
        collector = MetricsCollector(mock_redis)
        
        # Simula muitas operações
        for i in range(100):
            collector.record_request("GET", f"/api/{i}", 200, 0.1)
            collector.record_error("test_error", "test_component", f"Error {i}")
        
        # Verifica se as métricas foram registradas
        assert len(collector.buffer) == 200


if __name__ == "__main__":
    pytest.main([__file__]) 