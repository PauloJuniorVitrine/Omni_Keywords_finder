"""
Testes para Plataforma Centralizada de Observabilidade
====================================================

Testes unitários e de integração para:
- Plataforma centralizada
- Correlation IDs
- Detecção de anomalias
- Eventos de observabilidade
- Dashboard data

Prompt: CHECKLIST_SISTEMA_PREENCHIMENTO_LACUNAS.md - Fase 3
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-27
Versão: 1.0.0
Tracing ID: CENTRALIZED_PLATFORM_TESTS_014
"""

import unittest
import time
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Importar sistema de observabilidade
from infrastructure.observability.centralized_platform import (
    CentralizedObservabilityPlatform,
    CorrelationContext,
    EventType,
    Severity,
    AnomalyDetector,
    CorrelationMiddleware
)


class TestCentralizedObservabilityPlatform(unittest.TestCase):
    """Testes para plataforma centralizada de observabilidade"""
    
    def setUp(self):
        """Configurar testes"""
        self.platform = CentralizedObservabilityPlatform()
        self.correlation_context = self.platform.create_correlation_context(
            user_id="test_user",
            service_name="test_service",
            operation_name="test_operation"
        )
    
    def test_create_correlation_context(self):
        """Testar criação de contexto de correlação"""
        context = self.platform.create_correlation_context(
            user_id="user123",
            session_id="session456",
            service_name="api",
            operation_name="GET /keywords"
        )
        
        self.assertIsInstance(context, CorrelationContext)
        self.assertIsNotNone(context.correlation_id)
        self.assertEqual(context.user_id, "user123")
        self.assertEqual(context.session_id, "session456")
        self.assertEqual(context.service_name, "api")
        self.assertEqual(context.operation_name, "GET /keywords")
        self.assertIsInstance(context.timestamp, datetime)
    
    def test_generate_correlation_id(self):
        """Testar geração de correlation ID"""
        correlation_id1 = self.platform.generate_correlation_id()
        correlation_id2 = self.platform.generate_correlation_id()
        
        self.assertIsInstance(correlation_id1, str)
        self.assertIsInstance(correlation_id2, str)
        self.assertNotEqual(correlation_id1, correlation_id2)
        self.assertTrue(len(correlation_id1) > 0)
    
    def test_log_event(self):
        """Testar log de evento"""
        event_id = self.platform.log_event(
            event_type=EventType.PERFORMANCE,
            correlation_context=self.correlation_context,
            data={"duration": 0.15, "endpoint": "/api/keywords"},
            severity=Severity.INFO,
            source="api",
            tags={"method": "GET"}
        )
        
        self.assertIsInstance(event_id, str)
        self.assertTrue(len(event_id) > 0)
        
        # Verificar se evento foi adicionado
        self.assertEqual(len(self.platform.events), 1)
        event = self.platform.events[0]
        self.assertEqual(event.event_id, event_id)
        self.assertEqual(event.event_type, EventType.PERFORMANCE)
        self.assertEqual(event.correlation_context.correlation_id, self.correlation_context.correlation_id)
        self.assertEqual(event.data["duration"], 0.15)
        self.assertEqual(event.severity, Severity.INFO)
        self.assertEqual(event.source, "api")
        self.assertEqual(event.tags["method"], "GET")
    
    def test_log_api_request(self):
        """Testar log de requisição API"""
        self.platform.log_api_request(
            correlation_context=self.correlation_context,
            method="GET",
            path="/api/keywords",
            status_code=200,
            duration=0.15,
            user_id="user123"
        )
        
        # Verificar se eventos foram criados
        self.assertEqual(len(self.platform.events), 2)  # Performance + Metric
        
        # Verificar evento de performance
        performance_event = next(
            e for e in self.platform.events 
            if e.event_type == EventType.PERFORMANCE
        )
        self.assertEqual(performance_event.data["method"], "GET")
        self.assertEqual(performance_event.data["path"], "/api/keywords")
        self.assertEqual(performance_event.data["status_code"], 200)
        self.assertEqual(performance_event.data["duration"], 0.15)
        self.assertEqual(performance_event.data["user_id"], "user123")
        
        # Verificar evento de métrica
        metric_event = next(
            e for e in self.platform.events 
            if e.event_type == EventType.METRIC
        )
        self.assertEqual(metric_event.data["metric_name"], "api_request_duration_seconds")
        self.assertEqual(metric_event.data["value"], 0.15)
    
    def test_log_business_event(self):
        """Testar log de evento de negócio"""
        self.platform.log_business_event(
            correlation_context=self.correlation_context,
            event_name="keyword_collected",
            user_id="user123",
            business_data={"keyword": "python", "source": "google"}
        )
        
        # Verificar se evento foi criado
        self.assertEqual(len(self.platform.events), 1)
        event = self.platform.events[0]
        self.assertEqual(event.event_type, EventType.BUSINESS)
        self.assertEqual(event.data["event_name"], "keyword_collected")
        self.assertEqual(event.data["user_id"], "user123")
        self.assertEqual(event.data["business_data"]["keyword"], "python")
        self.assertEqual(event.data["business_data"]["source"], "google")
    
    def test_log_security_event(self):
        """Testar log de evento de segurança"""
        self.platform.log_security_event(
            correlation_context=self.correlation_context,
            event_name="failed_login",
            severity=Severity.WARNING,
            security_data={"ip": "192.168.1.1", "attempts": 3}
        )
        
        # Verificar se evento foi criado
        self.assertEqual(len(self.platform.events), 1)
        event = self.platform.events[0]
        self.assertEqual(event.event_type, EventType.SECURITY)
        self.assertEqual(event.data["event_name"], "failed_login")
        self.assertEqual(event.severity, Severity.WARNING)
        self.assertEqual(event.data["security_data"]["ip"], "192.168.1.1")
        self.assertEqual(event.data["security_data"]["attempts"], 3)
    
    def test_get_correlated_events(self):
        """Testar obtenção de eventos correlacionados"""
        # Criar múltiplos eventos com mesmo correlation ID
        self.platform.log_event(
            event_type=EventType.PERFORMANCE,
            correlation_context=self.correlation_context,
            data={"duration": 0.1},
            source="api"
        )
        
        self.platform.log_event(
            event_type=EventType.METRIC,
            correlation_context=self.correlation_context,
            data={"value": 100},
            source="api"
        )
        
        # Criar evento com correlation ID diferente
        other_context = self.platform.create_correlation_context()
        self.platform.log_event(
            event_type=EventType.LOG,
            correlation_context=other_context,
            data={"message": "test"},
            source="system"
        )
        
        # Obter eventos correlacionados
        correlated_events = self.platform.get_correlated_events(self.correlation_context.correlation_id)
        
        self.assertEqual(len(correlated_events), 2)
        self.assertTrue(all(e.correlation_context.correlation_id == self.correlation_context.correlation_id 
                           for e in correlated_events))
    
    def test_get_events_by_type(self):
        """Testar filtro de eventos por tipo"""
        # Criar eventos de diferentes tipos
        self.platform.log_event(
            event_type=EventType.PERFORMANCE,
            correlation_context=self.correlation_context,
            data={"duration": 0.1},
            source="api"
        )
        
        self.platform.log_event(
            event_type=EventType.METRIC,
            correlation_context=self.correlation_context,
            data={"value": 100},
            source="api"
        )
        
        self.platform.log_event(
            event_type=EventType.PERFORMANCE,
            correlation_context=self.correlation_context,
            data={"duration": 0.2},
            source="api"
        )
        
        # Filtrar por tipo
        performance_events = self.platform.get_events_by_type(EventType.PERFORMANCE)
        metric_events = self.platform.get_events_by_type(EventType.METRIC)
        
        self.assertEqual(len(performance_events), 2)
        self.assertEqual(len(metric_events), 1)
        self.assertTrue(all(e.event_type == EventType.PERFORMANCE for e in performance_events))
        self.assertTrue(all(e.event_type == EventType.METRIC for e in metric_events))
    
    def test_get_events_by_severity(self):
        """Testar filtro de eventos por severidade"""
        # Criar eventos de diferentes severidades
        self.platform.log_event(
            event_type=EventType.PERFORMANCE,
            correlation_context=self.correlation_context,
            data={"duration": 0.1},
            severity=Severity.INFO,
            source="api"
        )
        
        self.platform.log_event(
            event_type=EventType.ALERT,
            correlation_context=self.correlation_context,
            data={"message": "error"},
            severity=Severity.ERROR,
            source="api"
        )
        
        self.platform.log_event(
            event_type=EventType.PERFORMANCE,
            correlation_context=self.correlation_context,
            data={"duration": 0.2},
            severity=Severity.INFO,
            source="api"
        )
        
        # Filtrar por severidade
        info_events = self.platform.get_events_by_severity(Severity.INFO)
        error_events = self.platform.get_events_by_severity(Severity.ERROR)
        
        self.assertEqual(len(info_events), 2)
        self.assertEqual(len(error_events), 1)
        self.assertTrue(all(e.severity == Severity.INFO for e in info_events))
        self.assertTrue(all(e.severity == Severity.ERROR for e in error_events))
    
    def test_get_dashboard_data(self):
        """Testar obtenção de dados para dashboard"""
        # Criar alguns eventos
        self.platform.log_event(
            event_type=EventType.PERFORMANCE,
            correlation_context=self.correlation_context,
            data={"duration": 0.1},
            severity=Severity.INFO,
            source="api"
        )
        
        self.platform.log_event(
            event_type=EventType.ALERT,
            correlation_context=self.correlation_context,
            data={"message": "error"},
            severity=Severity.ERROR,
            source="api"
        )
        
        # Obter dados do dashboard
        dashboard_data = self.platform.get_dashboard_data()
        
        self.assertIsInstance(dashboard_data, dict)
        self.assertIn("timestamp", dashboard_data)
        self.assertIn("event_stats", dashboard_data)
        self.assertIn("severity_stats", dashboard_data)
        self.assertIn("critical_events_count", dashboard_data)
        self.assertIn("avg_response_time", dashboard_data)
        self.assertIn("total_events_last_hour", dashboard_data)
        self.assertIn("correlation_count", dashboard_data)
        
        # Verificar estatísticas
        self.assertEqual(dashboard_data["event_stats"]["performance"], 1)
        self.assertEqual(dashboard_data["event_stats"]["alert"], 1)
        self.assertEqual(dashboard_data["severity_stats"]["info"], 1)
        self.assertEqual(dashboard_data["severity_stats"]["error"], 1)
        self.assertEqual(dashboard_data["critical_events_count"], 0)
        self.assertEqual(dashboard_data["total_events_last_hour"], 2)
        self.assertEqual(dashboard_data["correlation_count"], 1)
    
    def test_correlation_mapping(self):
        """Testar mapeamento de correlação"""
        # Criar eventos com mesmo correlation ID
        self.platform.log_event(
            event_type=EventType.PERFORMANCE,
            correlation_context=self.correlation_context,
            data={"duration": 0.1},
            source="api"
        )
        
        self.platform.log_event(
            event_type=EventType.METRIC,
            correlation_context=self.correlation_context,
            data={"value": 100},
            source="api"
        )
        
        # Verificar mapeamento
        correlation_id = self.correlation_context.correlation_id
        self.assertIn(correlation_id, self.platform.correlation_map)
        self.assertEqual(len(self.platform.correlation_map[correlation_id]), 2)
    
    def test_event_cleanup(self):
        """Testar limpeza de eventos antigos"""
        # Criar evento antigo (simulado)
        old_event = self.platform.log_event(
            event_type=EventType.PERFORMANCE,
            correlation_context=self.correlation_context,
            data={"duration": 0.1},
            source="api"
        )
        
        # Simular evento antigo
        old_timestamp = datetime.utcnow() - timedelta(hours=25)
        self.platform.events[0].timestamp = old_timestamp
        
        # Criar evento recente
        self.platform.log_event(
            event_type=EventType.METRIC,
            correlation_context=self.correlation_context,
            data={"value": 100},
            source="api"
        )
        
        # Verificar que há 2 eventos
        self.assertEqual(len(self.platform.events), 2)
        
        # Simular processamento (que limpa eventos antigos)
        self.platform._process_events()
        
        # Verificar que apenas o evento recente permanece
        self.assertEqual(len(self.platform.events), 1)
        self.assertEqual(self.platform.events[0].event_type, EventType.METRIC)


class TestAnomalyDetector(unittest.TestCase):
    """Testes para detector de anomalias"""
    
    def setUp(self):
        """Configurar testes"""
        self.detector = AnomalyDetector(contamination=0.1)
    
    def test_simple_anomaly_detection(self):
        """Testar detecção simples de anomalias"""
        # Adicionar valores normais
        for i in range(10):
            self.detector.history.append(100 + i)
        
        # Testar valor normal
        is_anomaly = self.detector.detect_anomaly(105)
        self.assertFalse(is_anomaly)
        
        # Testar valor anômalo (muito alto)
        is_anomaly = self.detector.detect_anomaly(200)
        self.assertTrue(is_anomaly)
        
        # Testar valor anômalo (muito baixo)
        is_anomaly = self.detector.detect_anomaly(50)
        self.assertTrue(is_anomaly)
    
    def test_anomaly_detection_with_insufficient_data(self):
        """Testar detecção com dados insuficientes"""
        # Adicionar poucos valores
        for i in range(5):
            self.detector.history.append(100 + i)
        
        # Deve retornar False (não detectar anomalia)
        is_anomaly = self.detector.detect_anomaly(200)
        self.assertFalse(is_anomaly)
    
    def test_anomaly_detection_with_zero_std(self):
        """Testar detecção com desvio padrão zero"""
        # Adicionar valores iguais
        for i in range(10):
            self.detector.history.append(100)
        
        # Deve retornar False (não detectar anomalia)
        is_anomaly = self.detector.detect_anomaly(200)
        self.assertFalse(is_anomaly)
    
    @patch('infrastructure.observability.centralized_platform.IsolationForest')
    def test_ml_anomaly_detection(self, mock_isolation_forest):
        """Testar detecção de anomalias com ML"""
        # Mock do modelo
        mock_model = Mock()
        mock_model.predict.return_value = [-1]  # Anomalia
        mock_isolation_forest.return_value = mock_model
        
        # Adicionar dados suficientes
        for i in range(100):
            self.detector.history.append(100 + i)
        
        # Testar detecção
        is_anomaly = self.detector.detect_anomaly(200)
        self.assertTrue(is_anomaly)
        
        # Verificar se modelo foi treinado
        mock_model.fit.assert_called_once()
        mock_model.predict.assert_called_once()


class TestCorrelationMiddleware(unittest.TestCase):
    """Testes para middleware de correlação"""
    
    def setUp(self):
        """Configurar testes"""
        self.platform = CentralizedObservabilityPlatform()
        self.middleware = CorrelationMiddleware(self.platform)
    
    def test_correlation_middleware(self):
        """Testar middleware de correlação"""
        # Mock request
        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.path = "/api/keywords"
        
        # Mock response
        mock_response = Mock()
        mock_response.headers = {}
        
        # Aplicar middleware
        response_handler = self.middleware(mock_request)
        response = response_handler(mock_response)
        
        # Verificar se correlation context foi criado
        self.assertIsNotNone(mock_request.correlation_context)
        self.assertIsInstance(mock_request.correlation_context, CorrelationContext)
        self.assertEqual(mock_request.correlation_context.service_name, "api")
        self.assertEqual(mock_request.correlation_context.operation_name, "GET /api/keywords")
        
        # Verificar se header foi adicionado
        self.assertIn('X-Correlation-ID', response.headers)
        self.assertEqual(response.headers['X-Correlation-ID'], mock_request.correlation_context.correlation_id)


class TestIntegration(unittest.TestCase):
    """Testes de integração"""
    
    def setUp(self):
        """Configurar testes"""
        self.platform = CentralizedObservabilityPlatform()
    
    def test_full_workflow(self):
        """Testar workflow completo"""
        # 1. Criar contexto de correlação
        context = self.platform.create_correlation_context(
            user_id="user123",
            service_name="api",
            operation_name="POST /keywords"
        )
        
        # 2. Log de requisição API
        self.platform.log_api_request(
            correlation_context=context,
            method="POST",
            path="/api/keywords",
            status_code=201,
            duration=0.25,
            user_id="user123"
        )
        
        # 3. Log de evento de negócio
        self.platform.log_business_event(
            correlation_context=context,
            event_name="keyword_created",
            user_id="user123",
            business_data={"keyword": "python", "source": "manual"}
        )
        
        # 4. Log de evento de segurança
        self.platform.log_security_event(
            correlation_context=context,
            event_name="data_access",
            severity=Severity.INFO,
            security_data={"resource": "/api/keywords", "action": "create"}
        )
        
        # 5. Verificar eventos correlacionados
        correlated_events = self.platform.get_correlated_events(context.correlation_id)
        self.assertEqual(len(correlated_events), 4)  # API + Metric + Business + Security
        
        # 6. Verificar dados do dashboard
        dashboard_data = self.platform.get_dashboard_data()
        self.assertEqual(dashboard_data["total_events_last_hour"], 4)
        self.assertEqual(dashboard_data["correlation_count"], 1)
        
        # 7. Verificar tipos de eventos
        event_types = [e.event_type for e in correlated_events]
        self.assertIn(EventType.PERFORMANCE, event_types)
        self.assertIn(EventType.METRIC, event_types)
        self.assertIn(EventType.BUSINESS, event_types)
        self.assertIn(EventType.SECURITY, event_types)
    
    def test_error_handling(self):
        """Testar tratamento de erros"""
        # Testar com correlation context inválido
        with self.assertRaises(AttributeError):
            self.platform.log_event(
                event_type=EventType.PERFORMANCE,
                correlation_context=None,  # type: ignore
                data={"duration": 0.1},
                source="api"
            )
        
        # Testar com dados inválidos
        context = self.platform.create_correlation_context()
        with self.assertRaises(TypeError):
            self.platform.log_event(
                event_type=EventType.PERFORMANCE,
                correlation_context=context,
                data=None,  # type: ignore
                source="api"
            )


if __name__ == '__main__':
    # Executar testes
    unittest.main(verbosity=2) 