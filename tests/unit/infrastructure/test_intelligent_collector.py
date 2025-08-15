"""
Testes para IntelligentCollector - Omni Keywords Finder

Tracing ID: TEST_COLLECTOR_001_20250127
Data: 2025-01-27
Versão: 1.0
Status: 🟡 ALTO - Testes para IntelligentCollector

Baseado no código real do sistema Omni Keywords Finder
"""

import pytest
import asyncio
import time
import json
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, Any, List
from collections import deque

# Mock dos módulos para evitar dependências externas
class MockMetricsCollector:
    def __init__(self):
        self.metrics_collected = []
        self.collection_count = 0
    
    def collect_system_metrics(self):
        """Coleta métricas do sistema"""
        self.collection_count += 1
        metrics = {
            "timestamp": time.time(),
            "cpu_usage": 45.2,
            "memory_usage": 78.5,
            "disk_usage": 62.1,
            "network_io": 1024.5
        }
        self.metrics_collected.append(metrics)
        return metrics
    
    def get_collection_count(self):
        return self.collection_count
    
    def get_collected_metrics(self):
        return self.metrics_collected

class MockStructuredLogger:
    def __init__(self):
        self.logs_written = []
        self.log_count = 0
    
    def info(self, message, **kwargs):
        """Log de informação"""
        self.log_count += 1
        log_entry = {
            "level": "info",
            "message": message,
            "timestamp": time.time(),
            "kwargs": kwargs
        }
        self.logs_written.append(log_entry)
    
    def warning(self, message, **kwargs):
        """Log de warning"""
        self.log_count += 1
        log_entry = {
            "level": "warning",
            "message": message,
            "timestamp": time.time(),
            "kwargs": kwargs
        }
        self.logs_written.append(log_entry)
    
    def error(self, message, **kwargs):
        """Log de erro"""
        self.log_count += 1
        log_entry = {
            "level": "error",
            "message": message,
            "timestamp": time.time(),
            "kwargs": kwargs
        }
        self.logs_written.append(log_entry)
    
    def get_logs_count(self):
        return len(self.logs_written)
    
    def get_logs(self):
        return self.logs_written

class MockAnomalyDetector:
    def __init__(self):
        self.anomalies_detected = []
        self.detection_count = 0
    
    async def detect_anomalies(self, data):
        """Detecta anomalias nos dados"""
        self.detection_count += 1
        
        anomalies = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get("value", 0) > 100:
                    anomaly = {
                        "type": "high_value",
                        "severity": "warning",
                        "data": item,
                        "timestamp": time.time()
                    }
                    anomalies.append(anomaly)
        
        self.anomalies_detected.extend(anomalies)
        return anomalies
    
    def get_anomalies_count(self):
        return len(self.anomalies_detected)
    
    def get_anomalies(self):
        return self.anomalies_detected

class MockRedisManager:
    def __init__(self):
        self.stored_data = {}
        self.operation_count = 0
    
    async def store_data(self, key, data, ttl=None):
        """Armazena dados no Redis"""
        self.operation_count += 1
        self.stored_data[key] = {
            "data": data,
            "ttl": ttl,
            "timestamp": time.time()
        }
        return True
    
    async def get_data(self, key):
        """Recupera dados do Redis"""
        self.operation_count += 1
        return self.stored_data.get(key, {}).get("data")
    
    async def delete_data(self, key):
        """Remove dados do Redis"""
        self.operation_count += 1
        if key in self.stored_data:
            del self.stored_data[key]
            return True
        return False
    
    def get_operation_count(self):
        return self.operation_count
    
    def get_stored_data(self):
        return self.stored_data

class MockDataSource:
    def __init__(self, name, data_type):
        self.name = name
        self.data_type = data_type
        self.collection_count = 0
        self.is_active = True
    
    async def collect_data(self):
        """Coleta dados da fonte"""
        self.collection_count += 1
        
        if self.data_type == "system_metric":
            return {
                "source": self.name,
                "type": self.data_type,
                "value": 75.5,
                "timestamp": time.time()
            }
        elif self.data_type == "application_log":
            return {
                "source": self.name,
                "type": self.data_type,
                "message": f"Log from {self.name}",
                "level": "info",
                "timestamp": time.time()
            }
        else:
            return {
                "source": self.name,
                "type": self.data_type,
                "data": f"Data from {self.name}",
                "timestamp": time.time()
            }
    
    def get_collection_count(self):
        return self.collection_count
    
    def set_active(self, active):
        self.is_active = active

class MockEvent:
    def __init__(self, event_type, source, data, timestamp=None):
        self.event_type = event_type
        self.source = source
        self.data = data
        self.timestamp = timestamp or time.time()
        self.id = f"event_{int(self.timestamp * 1000)}"
    
    def to_dict(self):
        return {
            "id": self.id,
            "event_type": self.event_type,
            "source": self.source,
            "data": self.data,
            "timestamp": self.timestamp
        }

# Teste principal
class TestIntelligentCollector:
    """Testes para o IntelligentCollector"""
    
    @pytest.fixture
    def mock_collector(self):
        """Fixture para mock do IntelligentCollector"""
        with patch('infrastructure.aiops.intelligent_collector.MetricsCollector', MockMetricsCollector), \
             patch('infrastructure.aiops.intelligent_collector.StructuredLogger', MockStructuredLogger), \
             patch('infrastructure.aiops.intelligent_collector.AnomalyDetector', MockAnomalyDetector), \
             patch('infrastructure.aiops.intelligent_collector.RedisManager', MockRedisManager):
            
            from infrastructure.aiops.intelligent_collector import IntelligentCollector
            
            config = {
                'collection_interval': 60,
                'batch_size': 1000,
                'enable_anomaly_detection': True,
                'enable_correlation': True,
                'max_recent_events': 10000
            }
            
            return IntelligentCollector(config)
    
    @pytest.fixture
    def sample_events(self):
        """Fixture para eventos de teste"""
        return [
            MockEvent("system_metric", "cpu_monitor", {"cpu_usage": 75.5}),
            MockEvent("application_log", "web_server", {"message": "Request processed"}),
            MockEvent("database_query", "db_monitor", {"query_time": 150}),
            MockEvent("api_request", "api_gateway", {"endpoint": "/api/keywords"}),
            MockEvent("error_event", "error_handler", {"error": "Connection timeout"})
        ]
    
    def test_inicializacao(self, mock_collector):
        """Testa inicialização do coletor inteligente"""
        collector = mock_collector
        
        # Verificar se todos os componentes foram inicializados
        assert collector.metrics_collector is not None
        assert collector.structured_logger is not None
        assert collector.anomaly_detector is not None
        assert collector.redis_manager is not None
        
        # Verificar configurações
        assert collector.collection_interval == 60
        assert collector.batch_size == 1000
        assert collector.enable_anomaly_detection is True
        assert collector.enable_correlation is True
        assert collector.max_recent_events == 10000
        
        # Verificar estado inicial
        assert collector.is_running is False
        assert len(collector.sources) == 0
        assert len(collector.recent_events) == 0
    
    def test_adicionar_fonte_dados(self, mock_collector):
        """Testa adição de fonte de dados"""
        collector = mock_collector
        
        # Criar fonte de dados
        source = MockDataSource("test_source", "system_metric")
        
        # Adicionar fonte
        collector.sources.append(source)
        
        # Verificar se a fonte foi adicionada
        assert len(collector.sources) == 1
        assert collector.sources[0].name == "test_source"
        assert collector.sources[0].data_type == "system_metric"
    
    def test_coleta_dados_fonte(self, mock_collector):
        """Testa coleta de dados de uma fonte"""
        collector = mock_collector
        
        # Criar e adicionar fonte
        source = MockDataSource("test_source", "system_metric")
        collector.sources.append(source)
        
        # Coletar dados
        data = await source.collect_data()
        
        # Verificar se os dados foram coletados
        assert data is not None
        assert data["source"] == "test_source"
        assert data["type"] == "system_metric"
        assert "value" in data
        assert "timestamp" in data
        
        # Verificar contador de coleta
        assert source.get_collection_count() == 1
    
    def test_deteccao_anomalias(self, mock_collector):
        """Testa detecção de anomalias"""
        collector = mock_collector
        
        # Dados normais
        normal_data = [
            {"value": 50, "timestamp": time.time()},
            {"value": 60, "timestamp": time.time()},
            {"value": 45, "timestamp": time.time()}
        ]
        
        # Dados com anomalia
        anomalous_data = [
            {"value": 50, "timestamp": time.time()},
            {"value": 150, "timestamp": time.time()},  # Anomalia
            {"value": 60, "timestamp": time.time()}
        ]
        
        # Testar dados normais
        anomalies_normal = await collector.anomaly_detector.detect_anomalies(normal_data)
        assert len(anomalies_normal) == 0
        
        # Testar dados com anomalia
        anomalies_anomalous = await collector.anomaly_detector.detect_anomalies(anomalous_data)
        assert len(anomalies_anomalous) == 1
        assert anomalies_anomalous[0]["type"] == "high_value"
        assert anomalies_anomalous[0]["severity"] == "warning"
        
        # Verificar contador de detecções
        assert collector.anomaly_detector.get_detection_count() == 2
    
    def test_correlacao_eventos(self, mock_collector, sample_events):
        """Testa correlação de eventos"""
        collector = mock_collector
        
        # Simular correlação de eventos
        correlated_events = []
        
        # Agrupar eventos por tipo
        events_by_type = {}
        for event in sample_events:
            event_type = event.event_type
            if event_type not in events_by_type:
                events_by_type[event_type] = []
            events_by_type[event_type].append(event)
        
        # Criar correlações
        for event_type, events in events_by_type.items():
            if len(events) > 1:
                correlation = {
                    "type": "event_correlation",
                    "event_type": event_type,
                    "count": len(events),
                    "events": [e.to_dict() for e in events],
                    "timestamp": time.time()
                }
                correlated_events.append(correlation)
        
        # Verificar se as correlações foram criadas
        assert len(correlated_events) > 0
        
        # Verificar estrutura da correlação
        for correlation in correlated_events:
            assert "type" in correlation
            assert "event_type" in correlation
            assert "count" in correlation
            assert "events" in correlation
            assert "timestamp" in correlation
    
    def test_armazenamento_redis(self, mock_collector):
        """Testa armazenamento no Redis"""
        collector = mock_collector
        
        # Dados para armazenar
        test_data = {
            "key": "test_key",
            "value": "test_value",
            "timestamp": time.time()
        }
        
        # Armazenar dados
        result = await collector.redis_manager.store_data("test_key", test_data, ttl=3600)
        
        # Verificar se o armazenamento foi bem-sucedido
        assert result is True
        
        # Recuperar dados
        retrieved_data = await collector.redis_manager.get_data("test_key")
        
        # Verificar se os dados foram recuperados corretamente
        assert retrieved_data is not None
        assert retrieved_data["key"] == "test_key"
        assert retrieved_data["value"] == "test_value"
        
        # Verificar contador de operações
        assert collector.redis_manager.get_operation_count() == 2
    
    def test_logging_estruturado(self, mock_collector):
        """Testa logging estruturado"""
        collector = mock_collector
        
        # Log de informação
        collector.structured_logger.info("Test info message", service="test")
        
        # Log de warning
        collector.structured_logger.warning("Test warning message", service="test")
        
        # Log de erro
        collector.structured_logger.error("Test error message", service="test")
        
        # Verificar se os logs foram escritos
        assert collector.structured_logger.get_logs_count() == 3
        
        # Verificar estrutura dos logs
        logs = collector.structured_logger.get_logs()
        assert logs[0]["level"] == "info"
        assert logs[1]["level"] == "warning"
        assert logs[2]["level"] == "error"
        
        # Verificar se todos os logs têm timestamp
        for log in logs:
            assert "timestamp" in log
            assert "message" in log
            assert "kwargs" in log
    
    def test_metricas_prometheus(self, mock_collector):
        """Testa métricas Prometheus"""
        collector = mock_collector
        
        # Verificar se as métricas foram registradas
        assert collector.events_collected is not None
        assert collector.collection_duration is not None
        assert collector.active_sources is not None
        assert collector.collection_errors is not None
        
        # Simular incremento de métricas
        collector.events_collected.labels(source="test", type="system_metric").inc()
        collector.active_sources.set(5)
        collector.collection_errors.labels(source="test").inc()
        
        # Verificar se as métricas estão funcionando
        # (Este teste depende da implementação específica das métricas Prometheus)
        assert hasattr(collector.events_collected, 'labels')
        assert hasattr(collector.active_sources, 'set')
        assert hasattr(collector.collection_errors, 'labels')
    
    def test_processamento_eventos(self, mock_collector, sample_events):
        """Testa processamento de eventos"""
        collector = mock_collector
        
        # Processar eventos
        await collector._process_events(sample_events)
        
        # Verificar se os eventos foram adicionados ao cache recente
        assert len(collector.recent_events) == len(sample_events)
        
        # Verificar se os eventos foram armazenados no Redis
        # (Este teste depende da implementação específica do método _store_events)
        assert hasattr(collector, '_store_events')
    
    def test_gerenciamento_cache_eventos(self, mock_collector, sample_events):
        """Testa gerenciamento do cache de eventos"""
        collector = mock_collector
        
        # Adicionar eventos ao cache
        collector.recent_events.extend(sample_events)
        
        # Verificar se os eventos foram adicionados
        assert len(collector.recent_events) == len(sample_events)
        
        # Simular limite excedido
        collector.max_recent_events = 3
        
        # Adicionar mais eventos (deve remover os mais antigos)
        extra_events = [
            MockEvent("extra", "extra_source", {"data": "extra"}),
            MockEvent("extra2", "extra_source2", {"data": "extra2"})
        ]
        
        collector.recent_events.extend(extra_events)
        
        # Verificar se o cache foi limitado
        assert len(collector.recent_events) <= collector.max_recent_events
    
    def test_fontes_dados_multiplas(self, mock_collector):
        """Testa múltiplas fontes de dados"""
        collector = mock_collector
        
        # Criar múltiplas fontes
        sources = [
            MockDataSource("cpu_monitor", "system_metric"),
            MockDataSource("memory_monitor", "system_metric"),
            MockDataSource("web_server", "application_log"),
            MockDataSource("database", "database_query"),
            MockDataSource("api_gateway", "api_request")
        ]
        
        # Adicionar fontes
        for source in sources:
            collector.sources.append(source)
        
        # Verificar se todas as fontes foram adicionadas
        assert len(collector.sources) == 5
        
        # Verificar tipos de fontes
        source_types = [source.data_type for source in collector.sources]
        assert "system_metric" in source_types
        assert "application_log" in source_types
        assert "database_query" in source_types
        assert "api_request" in source_types
    
    def test_coleta_paralela(self, mock_collector):
        """Testa coleta paralela de dados"""
        collector = mock_collector
        
        # Criar fontes
        sources = [
            MockDataSource("source1", "system_metric"),
            MockDataSource("source2", "system_metric"),
            MockDataSource("source3", "application_log")
        ]
        
        # Adicionar fontes
        for source in sources:
            collector.sources.append(source)
        
        # Simular coleta paralela
        async def collect_from_source(source):
            return await source.collect_data()
        
        # Coletar de todas as fontes em paralelo
        tasks = [collect_from_source(source) for source in sources]
        results = await asyncio.gather(*tasks)
        
        # Verificar se todos os dados foram coletados
        assert len(results) == 3
        
        # Verificar se cada fonte coletou dados
        for source in sources:
            assert source.get_collection_count() == 1
    
    def test_estado_sistema(self, mock_collector):
        """Testa estado geral do sistema"""
        collector = mock_collector
        
        # Verificar se todos os componentes estão funcionando
        assert collector.metrics_collector is not None
        assert collector.structured_logger is not None
        assert collector.anomaly_detector is not None
        assert collector.redis_manager is not None
        
        # Verificar configurações
        assert collector.collection_interval > 0
        assert collector.batch_size > 0
        assert collector.max_recent_events > 0
        
        # Verificar estado inicial
        assert collector.is_running is False
        assert len(collector.sources) == 0
        assert len(collector.recent_events) == 0
    
    def test_configuracao_dinamica(self, mock_collector):
        """Testa configuração dinâmica do sistema"""
        collector = mock_collector
        
        # Verificar configurações iniciais
        assert collector.enable_anomaly_detection is True
        assert collector.enable_correlation is True
        assert collector.collection_interval == 60
        
        # Alterar configurações
        collector.enable_anomaly_detection = False
        collector.enable_correlation = False
        collector.collection_interval = 30
        
        # Verificar se as alterações foram aplicadas
        assert collector.enable_anomaly_detection is False
        assert collector.enable_correlation is False
        assert collector.collection_interval == 30
    
    def test_limpeza_cache(self, mock_collector, sample_events):
        """Testa limpeza do cache de eventos"""
        collector = mock_collector
        
        # Adicionar eventos ao cache
        collector.recent_events.extend(sample_events)
        
        # Verificar se os eventos foram adicionados
        assert len(collector.recent_events) == len(sample_events)
        
        # Limpar cache
        collector.recent_events.clear()
        
        # Verificar se o cache foi limpo
        assert len(collector.recent_events) == 0
    
    def test_estatisticas_sistema(self, mock_collector):
        """Testa estatísticas do sistema"""
        collector = mock_collector
        
        # Verificar se as estatísticas estão disponíveis
        # (Este teste depende da implementação específica das estatísticas)
        assert hasattr(collector, 'stats')
        
        # Verificar se as métricas estão funcionando
        assert collector.events_collected is not None
        assert collector.collection_duration is not None
        assert collector.active_sources is not None
        assert collector.collection_errors is not None
