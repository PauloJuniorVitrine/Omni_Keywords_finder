from typing import Dict, List, Optional, Any
"""
Testes Unitários para Analytics em Tempo Real
============================================

Testes abrangentes para o sistema de analytics em tempo real.

Autor: Paulo Júnior
Data: 2024-12-19
Tracing ID: ANALYTICS_RT_TEST_001
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from infrastructure.analytics.avancado.real_time_analytics import (
    RealTimeAnalytics, EventProcessor, MetricsAggregator, AlertManager,
    DashboardManager, RealTimeEvent, RealTimeMetric, EventType, MetricType
)


class TestEventProcessor:
    """Testes para EventProcessor"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.processor = EventProcessor()
    
    def test_process_page_view_event(self):
        """Testa processamento de evento de visualização de página"""
        event = RealTimeEvent(
            event_id="test-123",
            event_type=EventType.PAGE_VIEW,
            user_id="user-123",
            session_id="session-123",
            timestamp=datetime.utcnow(),
            data={"page": "/home", "time_on_page": 120}
        )
        
        metrics = self.processor.process_event(event)
        
        assert len(metrics) >= 2  # Pelo menos page_views e unique_users
        assert any(m.metric_name == "page_views" for m in metrics)
        assert any(m.metric_name == "unique_users" for m in metrics)
    
    def test_process_conversion_event(self):
        """Testa processamento de evento de conversão"""
        event = RealTimeEvent(
            event_id="test-123",
            event_type=EventType.CONVERSION,
            user_id="user-123",
            session_id="session-123",
            timestamp=datetime.utcnow(),
            data={"type": "purchase", "revenue": 100.0}
        )
        
        metrics = self.processor.process_event(event)
        
        assert len(metrics) >= 3  # conversions, revenue, conversion_rate
        assert any(m.metric_name == "conversions" for m in metrics)
        assert any(m.metric_name == "revenue" for m in metrics)
    
    def test_process_search_event(self):
        """Testa processamento de evento de busca"""
        event = RealTimeEvent(
            event_id="test-123",
            event_type=EventType.SEARCH,
            user_id="user-123",
            session_id="session-123",
            timestamp=datetime.utcnow(),
            data={"query": "keywords", "results_count": 50}
        )
        
        metrics = self.processor.process_event(event)
        
        assert len(metrics) >= 2  # searches e search_results
        assert any(m.metric_name == "searches" for m in metrics)
        assert any(m.metric_name == "search_results" for m in metrics)
    
    def test_process_performance_event(self):
        """Testa processamento de evento de performance"""
        event = RealTimeEvent(
            event_id="test-123",
            event_type=EventType.PERFORMANCE,
            user_id="user-123",
            session_id="session-123",
            timestamp=datetime.utcnow(),
            data={"page": "/home", "load_time": 2500, "api_response_time": 150}
        )
        
        metrics = self.processor.process_event(event)
        
        assert len(metrics) >= 2  # page_load_time e api_response_time
        assert any(m.metric_name == "page_load_time" for m in metrics)
        assert any(m.metric_name == "api_response_time" for m in metrics)


class TestMetricsAggregator:
    """Testes para MetricsAggregator"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.aggregator = MetricsAggregator()
    
    def test_add_counter_metric(self):
        """Testa adição de métrica do tipo counter"""
        metric = RealTimeMetric(
            metric_name="page_views",
            metric_type=MetricType.COUNTER,
            value=1,
            timestamp=datetime.utcnow(),
            labels={"page": "/home"}
        )
        
        self.aggregator.add_metric(metric)
        
        result = self.aggregator.get_metric("page_views", {"page": "/home"})
        assert result is not None
        assert result["value"] == 1
        assert result["count"] == 1
    
    def test_add_gauge_metric(self):
        """Testa adição de métrica do tipo gauge"""
        metric = RealTimeMetric(
            metric_name="active_users",
            metric_type=MetricType.GAUGE,
            value=100,
            timestamp=datetime.utcnow(),
            labels={"segment": "premium"}
        )
        
        self.aggregator.add_metric(metric)
        
        result = self.aggregator.get_metric("active_users", {"segment": "premium"})
        assert result is not None
        assert result["value"] == 100
    
    def test_add_histogram_metric(self):
        """Testa adição de métrica do tipo histogram"""
        # Adiciona múltiplas métricas para histograma
        for index in range(5):
            metric = RealTimeMetric(
                metric_name="load_time",
                metric_type=MetricType.HISTOGRAM,
                value=100 + index * 50,
                timestamp=datetime.utcnow(),
                labels={"page": "/home"}
            )
            self.aggregator.add_metric(metric)
        
        result = self.aggregator.get_metric("load_time", {"page": "/home"})
        assert result is not None
        assert "min" in result
        assert "max" in result
        assert "mean" in result
        assert "median" in result
        assert result["count"] == 5
    
    def test_metric_expiration(self):
        """Testa expiração de métricas antigas"""
        # Adiciona métrica antiga
        old_metric = RealTimeMetric(
            metric_name="test_metric",
            metric_type=MetricType.COUNTER,
            value=1,
            timestamp=datetime.utcnow() - timedelta(seconds=400),  # Mais antiga que window_size
            labels={}
        )
        
        self.aggregator.add_metric(old_metric)
        
        # Adiciona métrica recente
        new_metric = RealTimeMetric(
            metric_name="test_metric",
            metric_type=MetricType.COUNTER,
            value=1,
            timestamp=datetime.utcnow(),
            labels={}
        )
        
        self.aggregator.add_metric(new_metric)
        
        result = self.aggregator.get_metric("test_metric")
        assert result is not None
        assert result["value"] == 1  # Apenas a métrica recente


class TestAlertManager:
    """Testes para AlertManager"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.mock_notification_manager = Mock()
        self.alert_manager = AlertManager(self.mock_notification_manager)
    
    def test_set_threshold(self):
        """Testa definição de threshold"""
        self.alert_manager.set_threshold(
            "error_rate", ">", 10, "Taxa de erro alta", "critical"
        )
        
        assert "error_rate" in self.alert_manager.thresholds
        threshold = self.alert_manager.thresholds["error_rate"]
        assert threshold["operator"] == ">"
        assert threshold["value"] == 10
        assert threshold["alert_message"] == "Taxa de erro alta"
        assert threshold["severity"] == "critical"
    
    def test_check_thresholds_triggered(self):
        """Testa verificação de thresholds com alerta disparado"""
        self.alert_manager.set_threshold("error_rate", ">", 5, "Taxa de erro alta")
        
        metrics = {
            "error_rate_page_home": {"value": 10}
        }
        
        self.alert_manager.check_thresholds(metrics)
        
        # Verifica se notificação foi enviada
        self.mock_notification_manager.send_notification.assert_called_once()
    
    def test_check_thresholds_not_triggered(self):
        """Testa verificação de thresholds sem alerta"""
        self.alert_manager.set_threshold("error_rate", ">", 10, "Taxa de erro alta")
        
        metrics = {
            "error_rate_page_home": {"value": 5}
        }
        
        self.alert_manager.check_thresholds(metrics)
        
        # Verifica se notificação não foi enviada
        self.mock_notification_manager.send_notification.assert_not_called()
    
    def test_evaluate_threshold_operators(self):
        """Testa diferentes operadores de threshold"""
        # Testa operador >
        assert self.alert_manager._evaluate_threshold(10, ">", 5) is True
        assert self.alert_manager._evaluate_threshold(3, ">", 5) is False
        
        # Testa operador >=
        assert self.alert_manager._evaluate_threshold(5, ">=", 5) is True
        assert self.alert_manager._evaluate_threshold(3, ">=", 5) is False
        
        # Testa operador <
        assert self.alert_manager._evaluate_threshold(3, "<", 5) is True
        assert self.alert_manager._evaluate_threshold(10, "<", 5) is False
        
        # Testa operador <=
        assert self.alert_manager._evaluate_threshold(5, "<=", 5) is True
        assert self.alert_manager._evaluate_threshold(10, "<=", 5) is False
        
        # Testa operador ==
        assert self.alert_manager._evaluate_threshold(5, "==", 5) is True
        assert self.alert_manager._evaluate_threshold(10, "==", 5) is False
        
        # Testa operador !=
        assert self.alert_manager._evaluate_threshold(10, "!=", 5) is True
        assert self.alert_manager._evaluate_threshold(5, "!=", 5) is False


class TestDashboardManager:
    """Testes para DashboardManager"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_url = f"sqlite:///{self.temp_db.name}"
        self.dashboard_manager = DashboardManager(self.db_url)
    
    def teardown_method(self):
        """Cleanup após cada teste"""
        self.temp_db.close()
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_create_dashboard(self):
        """Testa criação de dashboard"""
        name = "Test Dashboard"
        description = "Dashboard de teste"
        config = {"refresh_interval": 30}
        widgets = [
            {"id": "widget1", "type": "metric", "title": "Test Widget"}
        ]
        
        dashboard_id = self.dashboard_manager.create_dashboard(
            name, description, config, widgets, is_public=True
        )
        
        assert dashboard_id is not None
        assert len(dashboard_id) > 0
    
    def test_get_dashboard(self):
        """Testa obtenção de dashboard"""
        # Cria dashboard
        name = "Test Dashboard"
        description = "Dashboard de teste"
        config = {"refresh_interval": 30}
        widgets = [{"id": "widget1", "type": "metric"}]
        
        dashboard_id = self.dashboard_manager.create_dashboard(
            name, description, config, widgets
        )
        
        # Obtém dashboard
        dashboard = self.dashboard_manager.get_dashboard(dashboard_id)
        
        assert dashboard is not None
        assert dashboard["name"] == name
        assert dashboard["description"] == description
        assert dashboard["config"] == config
        assert dashboard["widgets"] == widgets
    
    def test_update_dashboard(self):
        """Testa atualização de dashboard"""
        # Cria dashboard
        dashboard_id = self.dashboard_manager.create_dashboard(
            "Test Dashboard", "Description", {}, []
        )
        
        # Atualiza dashboard
        success = self.dashboard_manager.update_dashboard(
            dashboard_id, name="Updated Dashboard", description="Updated Description"
        )
        
        assert success is True
        
        # Verifica atualização
        dashboard = self.dashboard_manager.get_dashboard(dashboard_id)
        assert dashboard["name"] == "Updated Dashboard"
        assert dashboard["description"] == "Updated Description"
    
    def test_list_dashboards(self):
        """Testa listagem de dashboards"""
        # Cria alguns dashboards
        self.dashboard_manager.create_dashboard("Dashboard 1", "Desc 1", {}, [], is_public=True)
        self.dashboard_manager.create_dashboard("Dashboard 2", "Desc 2", {}, [], is_public=False)
        
        # Lista dashboards públicos
        public_dashboards = self.dashboard_manager.list_dashboards()
        assert len(public_dashboards) >= 1
        
        # Lista dashboards por usuário
        user_dashboards = self.dashboard_manager.list_dashboards("user-123")
        assert len(user_dashboards) >= 1


class TestRealTimeAnalytics:
    """Testes para RealTimeAnalytics"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_url = f"sqlite:///{self.temp_db.name}"
        self.analytics = RealTimeAnalytics(self.db_url)
    
    def teardown_method(self):
        """Cleanup após cada teste"""
        self.temp_db.close()
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_track_event(self):
        """Testa rastreamento de evento"""
        event_id = self.analytics.track_event(
            EventType.PAGE_VIEW,
            "user-123",
            "session-123",
            {"page": "/home", "time_on_page": 120}
        )
        
        assert event_id is not None
        assert len(event_id) > 0
    
    def test_get_metrics(self):
        """Testa obtenção de métricas"""
        # Rastreia alguns eventos
        self.analytics.track_event(
            EventType.PAGE_VIEW,
            "user-123",
            "session-123",
            {"page": "/home"}
        )
        
        self.analytics.track_event(
            EventType.CONVERSION,
            "user-123",
            "session-123",
            {"type": "purchase", "revenue": 100}
        )
        
        # Obtém métricas
        metrics = self.analytics.get_metrics()
        assert isinstance(metrics, dict)
        assert len(metrics) > 0
    
    def test_get_metrics_by_name(self):
        """Testa obtenção de métricas por nome"""
        # Rastreia evento
        self.analytics.track_event(
            EventType.PAGE_VIEW,
            "user-123",
            "session-123",
            {"page": "/home"}
        )
        
        # Obtém métricas de page_views
        page_view_metrics = self.analytics.get_metrics("page_views")
        assert isinstance(page_view_metrics, dict)
    
    def test_create_dashboard(self):
        """Testa criação de dashboard"""
        dashboard_id = self.analytics.dashboard_manager.create_dashboard(
            "Test Dashboard",
            "Dashboard de teste",
            {"refresh_interval": 30},
            [{"id": "widget1", "type": "metric"}]
        )
        
        assert dashboard_id is not None
    
    def test_get_dashboard_data(self):
        """Testa obtenção de dados do dashboard"""
        # Cria dashboard
        dashboard_id = self.analytics.dashboard_manager.create_dashboard(
            "Test Dashboard",
            "Dashboard de teste",
            {"refresh_interval": 30},
            [
                {
                    "id": "widget1",
                    "type": "metric",
                    "config": {"metric_name": "page_views"}
                }
            ]
        )
        
        # Obtém dados do dashboard
        dashboard_data = self.analytics.get_dashboard_data(dashboard_id)
        
        assert dashboard_data is not None
        assert "dashboard" in dashboard_data
        assert "widgets_data" in dashboard_data
    
    def test_process_widget_metric(self):
        """Testa processamento de widget de métrica"""
        # Rastreia evento para gerar métrica
        self.analytics.track_event(
            EventType.PAGE_VIEW,
            "user-123",
            "session-123",
            {"page": "/home"}
        )
        
        # Processa widget de métrica
        widget_config = {"metric_name": "page_views"}
        widget_data = self.analytics._process_widget({
            "type": "metric",
            "config": widget_config
        })
        
        assert "value" in widget_data
        assert "trend" in widget_data
        assert "last_updated" in widget_data
    
    def test_process_widget_chart(self):
        """Testa processamento de widget de gráfico"""
        widget_config = {
            "metric_name": "page_views",
            "chart_type": "line",
            "time_range": 3600
        }
        
        widget_data = self.analytics._process_widget({
            "type": "chart",
            "config": widget_config
        })
        
        assert "chart_type" in widget_data
        assert "data" in widget_data
        assert "config" in widget_data
    
    def test_process_widget_table(self):
        """Testa processamento de widget de tabela"""
        # Rastreia eventos para gerar dados
        self.analytics.track_event(
            EventType.PAGE_VIEW,
            "user-123",
            "session-123",
            {"page": "/home"}
        )
        
        widget_config = {
            "metrics": ["page_views"],
            "limit": 10
        }
        
        widget_data = self.analytics._process_widget({
            "type": "table",
            "config": widget_config
        })
        
        assert "data" in widget_data
        assert "columns" in widget_data


class TestHelperFunctions:
    """Testes para funções helper"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_url = f"sqlite:///{self.temp_db.name}"
        self.analytics = RealTimeAnalytics(self.db_url)
    
    def teardown_method(self):
        """Cleanup após cada teste"""
        self.temp_db.close()
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_track_event_helper(self):
        """Testa função helper track_event"""
        from infrastructure.analytics.avancado.real_time_analytics import track_event
        
        event_id = track_event(
            "page_view",
            "user-123",
            "session-123",
            {"page": "/home"}
        )
        
        assert event_id is not None
    
    def test_get_metrics_helper(self):
        """Testa função helper get_metrics"""
        from infrastructure.analytics.avancado.real_time_analytics import get_metrics
        
        # Rastreia evento
        self.analytics.track_event(
            EventType.PAGE_VIEW,
            "user-123",
            "session-123",
            {"page": "/home"}
        )
        
        # Obtém métricas
        metrics = get_metrics()
        assert isinstance(metrics, dict)
    
    def test_create_dashboard_helper(self):
        """Testa função helper create_dashboard"""
        from infrastructure.analytics.avancado.real_time_analytics import create_dashboard
        
        widgets = [
            {"id": "widget1", "type": "metric", "title": "Test Widget"}
        ]
        
        dashboard_id = create_dashboard(
            "Test Dashboard",
            "Dashboard de teste",
            widgets,
            is_public=True
        )
        
        assert dashboard_id is not None


class TestErrorHandling:
    """Testes para tratamento de erros"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_url = f"sqlite:///{self.temp_db.name}"
        self.analytics = RealTimeAnalytics(self.db_url)
    
    def teardown_method(self):
        """Cleanup após cada teste"""
        self.temp_db.close()
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_invalid_event_type(self):
        """Testa comportamento com tipo de evento inválido"""
        from infrastructure.analytics.avancado.real_time_analytics import track_event
        
        event_id = track_event(
            "invalid_event_type",
            "user-123",
            "session-123",
            {"page": "/home"}
        )
        
        assert event_id is None
    
    def test_database_connection_error(self):
        """Testa comportamento com erro de conexão"""
        # Cria analytics com URL inválida
        invalid_analytics = RealTimeAnalytics("sqlite:///invalid/path.db")
        
        # Deve lançar exceção
        with pytest.raises(Exception):
            invalid_analytics.track_event(
                EventType.PAGE_VIEW,
                "user-123",
                "session-123",
                {"page": "/home"}
            )
    
    def test_empty_metrics(self):
        """Testa comportamento com métricas vazias"""
        metrics = self.analytics.get_metrics()
        assert isinstance(metrics, dict)
        assert len(metrics) == 0


class TestPerformance:
    """Testes de performance"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_url = f"sqlite:///{self.temp_db.name}"
        self.analytics = RealTimeAnalytics(self.db_url)
    
    def teardown_method(self):
        """Cleanup após cada teste"""
        self.temp_db.close()
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_bulk_event_tracking(self):
        """Testa rastreamento de eventos em massa"""
        start_time = datetime.utcnow()
        
        # Rastreia 1000 eventos
        for index in range(1000):
            self.analytics.track_event(
                EventType.PAGE_VIEW,
                f"user-{index}",
                f"session-{index}",
                {"page": f"/page-{index}"}
            )
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        # Deve ser rápido (menos de 5 segundos)
        assert duration < 5.0
    
    def test_metrics_aggregation_performance(self):
        """Testa performance da agregação de métricas"""
        # Adiciona muitas métricas
        start_time = datetime.utcnow()
        
        for index in range(1000):
            metric = RealTimeMetric(
                metric_name="test_metric",
                metric_type=MetricType.COUNTER,
                value=1,
                timestamp=datetime.utcnow(),
                labels={"label": f"value-{index}"}
            )
            self.analytics.metrics_aggregator.add_metric(metric)
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        # Deve ser rápido (menos de 1 segundo)
        assert duration < 1.0
        
        # Testa obtenção de métricas
        metrics = self.analytics.get_metrics()
        assert len(metrics) > 0


if __name__ == "__main__":
    pytest.main([__file__]) 