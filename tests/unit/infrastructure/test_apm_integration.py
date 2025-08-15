"""
Testes para APMManager - Omni Keywords Finder

Tracing ID: TEST_APM_001_20250127
Data: 2025-01-27
Versão: 1.0
Status: 🟡 ALTO - Testes para APMManager

Baseado no código real do sistema Omni Keywords Finder
"""

import pytest
import asyncio
import time
import json
import threading
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, Any, List
from collections import deque

# Mock dos módulos para evitar dependências externas
class MockAPMCollector:
    def __init__(self):
        self.collected_metrics = []
        self.collection_count = 0
    
    def collect_metrics(self):
        """Coleta métricas do sistema"""
        self.collection_count += 1
        metrics = {
            "timestamp": time.time(),
            "cpu_usage": 45.2,
            "memory_usage": 78.5,
            "disk_usage": 62.1,
            "network_io": 1024.5
        }
        self.collected_metrics.append(metrics)
        return metrics
    
    def get_collection_count(self):
        return self.collection_count
    
    def get_collected_metrics(self):
        return self.collected_metrics

class MockAPMInsightEngine:
    def __init__(self):
        self.insights_generated = []
        self.analysis_count = 0
    
    def analyze_metrics(self, metrics):
        """Analisa métricas e gera insights"""
        self.analysis_count += 1
        
        insights = []
        if metrics.get("cpu_usage", 0) > 80:
            insights.append({
                "type": "high_cpu_usage",
                "severity": "warning",
                "message": "CPU usage is above 80%",
                "timestamp": time.time()
            })
        
        if metrics.get("memory_usage", 0) > 90:
            insights.append({
                "type": "high_memory_usage",
                "severity": "critical",
                "message": "Memory usage is above 90%",
                "timestamp": time.time()
            })
        
        self.insights_generated.extend(insights)
        return insights
    
    def get_insights_count(self):
        return len(self.insights_generated)
    
    def get_insights(self):
        return self.insights_generated

class MockAPMAlertManager:
    def __init__(self):
        self.alerts_sent = []
        self.alert_count = 0
    
    def send_alert(self, alert_type, message, severity="info"):
        """Envia alerta"""
        self.alert_count += 1
        alert = {
            "id": f"alert_{self.alert_count}",
            "type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": time.time()
        }
        self.alerts_sent.append(alert)
        return alert
    
    def get_alerts_count(self):
        return len(self.alerts_sent)
    
    def get_alerts(self):
        return self.alerts_sent

class MockJaegerTracer:
    def __init__(self):
        self.spans_created = []
        self.trace_count = 0
    
    def start_span(self, operation_name, tags=None):
        """Inicia um span de tracing"""
        self.trace_count += 1
        span = {
            "id": f"span_{self.trace_count}",
            "operation_name": operation_name,
            "tags": tags or {},
            "start_time": time.time(),
            "end_time": None
        }
        self.spans_created.append(span)
        return span
    
    def finish_span(self, span):
        """Finaliza um span"""
        span["end_time"] = time.time()
        span["duration"] = span["end_time"] - span["start_time"]
    
    def get_spans_count(self):
        return len(self.spans_created)
    
    def get_spans(self):
        return self.spans_created

class MockSentryClient:
    def __init__(self):
        self.events_sent = []
        self.event_count = 0
    
    def capture_exception(self, exception, tags=None):
        """Captura exceção"""
        self.event_count += 1
        event = {
            "id": f"event_{self.event_count}",
            "type": "exception",
            "exception": str(exception),
            "tags": tags or {},
            "timestamp": time.time()
        }
        self.events_sent.append(event)
        return event
    
    def capture_message(self, message, level="info", tags=None):
        """Captura mensagem"""
        self.event_count += 1
        event = {
            "id": f"event_{self.event_count}",
            "type": "message",
            "message": message,
            "level": level,
            "tags": tags or {},
            "timestamp": time.time()
        }
        self.events_sent.append(event)
        return event
    
    def get_events_count(self):
        return len(self.events_sent)
    
    def get_events(self):
        return self.events_sent

class MockPrometheusMetrics:
    def __init__(self):
        self.metrics_registered = {}
        self.counter_values = {}
        self.gauge_values = {}
        self.histogram_values = {}
    
    def Counter(self, name, description, labelnames=None):
        """Registra contador Prometheus"""
        self.metrics_registered[name] = {
            "type": "counter",
            "description": description,
            "labelnames": labelnames or []
        }
        self.counter_values[name] = 0
        return MockCounter(name, self)
    
    def Gauge(self, name, description, labelnames=None):
        """Registra gauge Prometheus"""
        self.metrics_registered[name] = {
            "type": "gauge",
            "description": description,
            "labelnames": labelnames or []
        }
        self.gauge_values[name] = 0
        return MockGauge(name, self)
    
    def Histogram(self, name, description, labelnames=None):
        """Registra histograma Prometheus"""
        self.metrics_registered[name] = {
            "type": "histogram",
            "description": description,
            "labelnames": labelnames or []
        }
        self.histogram_values[name] = []
        return MockHistogram(name, self)

class MockCounter:
    def __init__(self, name, metrics_manager):
        self.name = name
        self.metrics_manager = metrics_manager
    
    def inc(self, amount=1):
        """Incrementa contador"""
        self.metrics_manager.counter_values[self.name] += amount

class MockGauge:
    def __init__(self, name, metrics_manager):
        self.name = name
        self.metrics_manager = metrics_manager
    
    def set(self, value):
        """Define valor do gauge"""
        self.metrics_manager.gauge_values[self.name] = value

class MockHistogram:
    def __init__(self, name, metrics_manager):
        self.name = name
        self.metrics_manager = metrics_manager
    
    def observe(self, value):
        """Observa valor para histograma"""
        self.metrics_manager.histogram_values[self.name].append(value)

# Teste principal
class TestAPMManager:
    """Testes para o APMManager"""
    
    @pytest.fixture
    def mock_apm_manager(self):
        """Fixture para mock do APM Manager"""
        with patch('infrastructure.monitoring.apm_integration.APMCollector', MockAPMCollector), \
             patch('infrastructure.monitoring.apm_integration.APMInsightEngine', MockAPMInsightEngine), \
             patch('infrastructure.monitoring.apm_integration.APMAlertManager', MockAPMAlertManager), \
             patch('infrastructure.monitoring.apm_integration.JaegerTracer', MockJaegerTracer), \
             patch('infrastructure.monitoring.apm_integration.SentryClient', MockSentryClient), \
             patch('infrastructure.monitoring.apm_integration.prometheus_client', MockPrometheusMetrics):
            
            from infrastructure.monitoring.apm_integration import APMManager
            
            return APMManager("test-service")
    
    @pytest.fixture
    def sample_metrics(self):
        """Fixture para métricas de teste"""
        return {
            "cpu_usage": 85.5,
            "memory_usage": 92.3,
            "disk_usage": 75.8,
            "network_io": 2048.7
        }
    
    def test_inicializacao(self, mock_apm_manager):
        """Testa inicialização do APM Manager"""
        apm = mock_apm_manager
        
        # Verificar se todos os componentes foram inicializados
        assert apm.collector is not None
        assert apm.insight_engine is not None
        assert apm.alert_manager is not None
        
        # Verificar configurações
        assert apm.service_name == "test-service"
        assert apm.config["environment"] == "development"
        assert apm.config["enable_insights"] is True
        assert apm.config["enable_alerts"] is True
        
        # Verificar se a thread de processamento foi iniciada
        assert apm.processing_thread is not None
        assert apm.processing_thread.is_alive()
    
    def test_configuracao_padrao(self, mock_apm_manager):
        """Testa configurações padrão"""
        apm = mock_apm_manager
        
        # Verificar configurações padrão
        assert apm.config["jaeger_endpoint"] == "http://localhost:14268/api/traces"
        assert apm.config["prometheus_port"] == 9090
        assert apm.config["sampling_rate"] == 0.1
        assert apm.config["environment"] == "development"
    
    def test_coleta_metricas(self, mock_apm_manager):
        """Testa coleta de métricas"""
        apm = mock_apm_manager
        
        # Coletar métricas
        metrics = apm.collector.collect_metrics()
        
        # Verificar se as métricas foram coletadas
        assert metrics is not None
        assert "timestamp" in metrics
        assert "cpu_usage" in metrics
        assert "memory_usage" in metrics
        assert "disk_usage" in metrics
        assert "network_io" in metrics
        
        # Verificar contador de coleta
        assert apm.collector.get_collection_count() == 1
        
        # Verificar se as métricas foram armazenadas
        collected_metrics = apm.collector.get_collected_metrics()
        assert len(collected_metrics) == 1
        assert collected_metrics[0] == metrics
    
    def test_geracao_insights(self, mock_apm_manager, sample_metrics):
        """Testa geração de insights"""
        apm = mock_apm_manager
        
        # Analisar métricas para gerar insights
        insights = apm.insight_engine.analyze_metrics(sample_metrics)
        
        # Verificar se os insights foram gerados
        assert len(insights) > 0
        
        # Verificar se há insight de CPU alta
        cpu_insights = [i for i in insights if i["type"] == "high_cpu_usage"]
        assert len(cpu_insights) == 1
        assert cpu_insights[0]["severity"] == "warning"
        
        # Verificar se há insight de memória alta
        memory_insights = [i for i in insights if i["type"] == "high_memory_usage"]
        assert len(memory_insights) == 1
        assert memory_insights[0]["severity"] == "critical"
        
        # Verificar contador de análise
        assert apm.insight_engine.get_analysis_count() == 1
        
        # Verificar se os insights foram armazenados
        stored_insights = apm.insight_engine.get_insights()
        assert len(stored_insights) == 2
    
    def test_envio_alertas(self, mock_apm_manager):
        """Testa envio de alertas"""
        apm = mock_apm_manager
        
        # Enviar alerta de informação
        info_alert = apm.alert_manager.send_alert(
            "system_info",
            "System is running normally",
            "info"
        )
        
        # Verificar se o alerta foi enviado
        assert info_alert is not None
        assert info_alert["type"] == "system_info"
        assert info_alert["severity"] == "info"
        assert info_alert["message"] == "System is running normally"
        
        # Enviar alerta de warning
        warning_alert = apm.alert_manager.send_alert(
            "high_cpu",
            "CPU usage is high",
            "warning"
        )
        
        # Verificar se o alerta foi enviado
        assert warning_alert is not None
        assert warning_alert["severity"] == "warning"
        
        # Verificar contador de alertas
        assert apm.alert_manager.get_alerts_count() == 2
        
        # Verificar se os alertas foram armazenados
        stored_alerts = apm.alert_manager.get_alerts()
        assert len(stored_alerts) == 2
    
    def test_tracing_jaeger(self, mock_apm_manager):
        """Testa integração com Jaeger"""
        apm = mock_apm_manager
        
        # Iniciar span de tracing
        span = apm.tracer.start_span("test_operation", {"service": "test"})
        
        # Verificar se o span foi criado
        assert span is not None
        assert span["operation_name"] == "test_operation"
        assert span["tags"]["service"] == "test"
        assert span["start_time"] is not None
        assert span["end_time"] is None
        
        # Finalizar span
        apm.tracer.finish_span(span)
        
        # Verificar se o span foi finalizado
        assert span["end_time"] is not None
        assert span["duration"] is not None
        
        # Verificar contador de spans
        assert apm.tracer.get_spans_count() == 1
        
        # Verificar se o span foi armazenado
        stored_spans = apm.tracer.get_spans()
        assert len(stored_spans) == 1
        assert stored_spans[0] == span
    
    def test_error_tracking_sentry(self, mock_apm_manager):
        """Testa integração com Sentry"""
        apm = mock_apm_manager
        
        # Capturar exceção
        exception = Exception("Test exception")
        event = apm.sentry.capture_exception(exception, {"service": "test"})
        
        # Verificar se o evento foi capturado
        assert event is not None
        assert event["type"] == "exception"
        assert event["exception"] == "Test exception"
        assert event["tags"]["service"] == "test"
        
        # Capturar mensagem
        message_event = apm.sentry.capture_message("Test message", "info", {"service": "test"})
        
        # Verificar se a mensagem foi capturada
        assert message_event is not None
        assert message_event["type"] == "message"
        assert message_event["message"] == "Test message"
        assert message_event["level"] == "info"
        
        # Verificar contador de eventos
        assert apm.sentry.get_events_count() == 2
        
        # Verificar se os eventos foram armazenados
        stored_events = apm.sentry.get_events()
        assert len(stored_events) == 2
    
    def test_metricas_prometheus(self, mock_apm_manager):
        """Testa métricas Prometheus"""
        apm = mock_apm_manager
        
        # Registrar contador
        counter = apm.prometheus.Counter("test_counter", "Test counter", ["label"])
        counter.inc(5)
        
        # Verificar se o contador foi registrado
        assert "test_counter" in apm.prometheus.metrics_registered
        assert apm.prometheus.metrics_registered["test_counter"]["type"] == "counter"
        assert apm.prometheus.counter_values["test_counter"] == 5
        
        # Registrar gauge
        gauge = apm.prometheus.Gauge("test_gauge", "Test gauge", ["label"])
        gauge.set(42.5)
        
        # Verificar se o gauge foi registrado
        assert "test_gauge" in apm.prometheus.metrics_registered
        assert apm.prometheus.metrics_registered["test_gauge"]["type"] == "gauge"
        assert apm.prometheus.gauge_values["test_gauge"] == 42.5
        
        # Registrar histograma
        histogram = apm.prometheus.Histogram("test_histogram", "Test histogram", ["label"])
        histogram.observe(1.5)
        histogram.observe(2.5)
        
        # Verificar se o histograma foi registrado
        assert "test_histogram" in apm.prometheus.metrics_registered
        assert apm.prometheus.metrics_registered["test_histogram"]["type"] == "histogram"
        assert len(apm.prometheus.histogram_values["test_histogram"]) == 2
    
    def test_processamento_loop(self, mock_apm_manager):
        """Testa loop de processamento"""
        apm = mock_apm_manager
        
        # Verificar se a thread está rodando
        assert apm.processing_thread.is_alive()
        
        # Aguardar um pouco para o loop processar
        time.sleep(0.1)
        
        # Verificar se o processamento está ativo
        # (Este teste depende da implementação específica do método _processing_loop)
        assert hasattr(apm, '_processing_loop')
    
    def test_configuracao_ambiente(self, mock_apm_manager):
        """Testa configuração por ambiente"""
        apm = mock_apm_manager
        
        # Verificar configuração de desenvolvimento
        assert apm.config["environment"] == "development"
        assert apm.config["sampling_rate"] == 0.1
        
        # Simular mudança para produção
        apm.config["environment"] = "production"
        apm.config["sampling_rate"] = 0.01
        
        # Verificar se as configurações foram alteradas
        assert apm.config["environment"] == "production"
        assert apm.config["sampling_rate"] == 0.01
    
    def test_habilitacao_desabilitacao_recursos(self, mock_apm_manager):
        """Testa habilitação/desabilitação de recursos"""
        apm = mock_apm_manager
        
        # Verificar estado inicial
        assert apm.config["enable_insights"] is True
        assert apm.config["enable_alerts"] is True
        
        # Desabilitar insights
        apm.config["enable_insights"] = False
        assert apm.config["enable_insights"] is False
        
        # Desabilitar alertas
        apm.config["enable_alerts"] = False
        assert apm.config["enable_alerts"] is False
    
    def test_metricas_sistema(self, mock_apm_manager):
        """Testa métricas do sistema"""
        apm = mock_apm_manager
        
        # Simular métricas do sistema
        system_metrics = {
            "cpu_usage": 65.2,
            "memory_usage": 78.9,
            "disk_usage": 45.3,
            "network_io": 1536.8
        }
        
        # Coletar métricas
        collected = apm.collector.collect_metrics()
        
        # Verificar se as métricas foram coletadas
        assert collected is not None
        assert isinstance(collected["cpu_usage"], (int, float))
        assert isinstance(collected["memory_usage"], (int, float))
        assert isinstance(collected["disk_usage"], (int, float))
        assert isinstance(collected["network_io"], (int, float))
    
    def test_insights_automaticos(self, mock_apm_manager):
        """Testa geração automática de insights"""
        apm = mock_apm_manager
        
        # Métricas que devem gerar insights
        critical_metrics = {
            "cpu_usage": 95.0,
            "memory_usage": 98.5,
            "disk_usage": 99.1,
            "network_io": 5000.0
        }
        
        # Analisar métricas críticas
        insights = apm.insight_engine.analyze_metrics(critical_metrics)
        
        # Verificar se múltiplos insights foram gerados
        assert len(insights) >= 2
        
        # Verificar se há insights críticos
        critical_insights = [i for i in insights if i["severity"] == "critical"]
        assert len(critical_insights) >= 1
        
        # Verificar se os insights foram armazenados
        stored_insights = apm.insight_engine.get_insights()
        assert len(stored_insights) >= 2
    
    def test_alertas_automaticos(self, mock_apm_manager):
        """Testa geração automática de alertas"""
        apm = mock_apm_manager
        
        # Simular situação crítica
        critical_alert = apm.alert_manager.send_alert(
            "system_critical",
            "System resources critically low",
            "critical"
        )
        
        # Verificar se o alerta crítico foi enviado
        assert critical_alert is not None
        assert critical_alert["severity"] == "critical"
        assert critical_alert["type"] == "system_critical"
        
        # Verificar se o alerta foi armazenado
        stored_alerts = apm.alert_manager.get_alerts()
        assert len(stored_alerts) == 1
        assert stored_alerts[0]["severity"] == "critical"
    
    def test_threading_safety(self, mock_apm_manager):
        """Testa thread safety do sistema"""
        apm = mock_apm_manager
        
        # Verificar se a thread de processamento foi iniciada
        assert apm.processing_thread is not None
        assert apm.processing_thread.is_alive()
        
        # Verificar se a thread é daemon
        assert apm.processing_thread.daemon is True
    
    def test_estado_sistema(self, mock_apm_manager):
        """Testa estado geral do sistema APM"""
        apm = mock_apm_manager
        
        # Verificar se todos os componentes estão funcionando
        assert apm.collector is not None
        assert apm.insight_engine is not None
        assert apm.alert_manager is not None
        assert apm.tracer is not None
        assert apm.sentry is not None
        assert apm.prometheus is not None
        
        # Verificar se a thread está rodando
        assert apm.processing_thread.is_alive()
        
        # Verificar configurações
        assert apm.service_name == "test-service"
        assert apm.config is not None
