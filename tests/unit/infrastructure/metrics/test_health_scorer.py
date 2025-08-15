"""
Testes unitários para HealthScorer
Tracing ID: METRICS-001
Prompt: INTEGRATION_EXTERNAL_CHECKLIST_V2.md
Ruleset: enterprise_control_layer.yaml
Data/Hora: 2024-12-20 02:00:00 UTC

Testes unitários abrangentes para o sistema de score de saúde das integrações.
"""

import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Optional
from datetime import datetime, timedelta

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

from infrastructure.metrics.health_scorer import (
    HealthScorer,
    HealthMetric,
    IntegrationHealth,
    SystemHealth,
    HealthStatus,
    MetricType
)


class TestHealthMetric:
    """Testes para HealthMetric"""
    
    def test_health_metric_creation(self):
        """Testa criação de métrica de saúde"""
        metric = HealthMetric(
            metric_type=MetricType.SUCCESS_RATE,
            value=95.5,
            weight=0.3,
            threshold={"excellent": 99.0, "good": 95.0, "warning": 90.0, "critical": 80.0},
            status=HealthStatus.GOOD,
            timestamp=datetime.now(),
            description="Taxa de sucesso da API"
        )
        
        assert metric.metric_type == MetricType.SUCCESS_RATE
        assert metric.value == 95.5
        assert metric.weight == 0.3
        assert metric.status == HealthStatus.GOOD
        assert metric.description == "Taxa de sucesso da API"
    
    def test_success_rate_score_calculation(self):
        """Testa cálculo de score para taxa de sucesso"""
        metric = HealthMetric(
            metric_type=MetricType.SUCCESS_RATE,
            value=99.5,
            weight=0.3,
            threshold={"excellent": 99.0, "good": 95.0, "warning": 90.0, "critical": 80.0},
            status=HealthStatus.EXCELLENT,
            timestamp=datetime.now()
        )
        
        score = metric.calculate_score()
        assert score == 100.0
    
    def test_success_rate_score_good(self):
        """Testa score de taxa de sucesso boa"""
        metric = HealthMetric(
            metric_type=MetricType.SUCCESS_RATE,
            value=97.0,
            weight=0.3,
            threshold={"excellent": 99.0, "good": 95.0, "warning": 90.0, "critical": 80.0},
            status=HealthStatus.GOOD,
            timestamp=datetime.now()
        )
        
        score = metric.calculate_score()
        assert score == 80.0
    
    def test_success_rate_score_warning(self):
        """Testa score de taxa de sucesso com warning"""
        metric = HealthMetric(
            metric_type=MetricType.SUCCESS_RATE,
            value=92.0,
            weight=0.3,
            threshold={"excellent": 99.0, "good": 95.0, "warning": 90.0, "critical": 80.0},
            status=HealthStatus.WARNING,
            timestamp=datetime.now()
        )
        
        score = metric.calculate_score()
        assert score == 60.0
    
    def test_success_rate_score_critical(self):
        """Testa score de taxa de sucesso crítica"""
        metric = HealthMetric(
            metric_type=MetricType.SUCCESS_RATE,
            value=75.0,
            weight=0.3,
            threshold={"excellent": 99.0, "good": 95.0, "warning": 90.0, "critical": 80.0},
            status=HealthStatus.CRITICAL,
            timestamp=datetime.now()
        )
        
        score = metric.calculate_score()
        assert score == 0.0
    
    def test_latency_score_calculation(self):
        """Testa cálculo de score para latência"""
        metric = HealthMetric(
            metric_type=MetricType.LATENCY,
            value=50,
            weight=0.25,
            threshold={"excellent": 100, "good": 500, "warning": 1000, "critical": 2000},
            status=HealthStatus.EXCELLENT,
            timestamp=datetime.now()
        )
        
        score = metric.calculate_score()
        assert score == 100.0
    
    def test_latency_score_good(self):
        """Testa score de latência boa"""
        metric = HealthMetric(
            metric_type=MetricType.LATENCY,
            value=300,
            weight=0.25,
            threshold={"excellent": 100, "good": 500, "warning": 1000, "critical": 2000},
            status=HealthStatus.GOOD,
            timestamp=datetime.now()
        )
        
        score = metric.calculate_score()
        assert score == 80.0
    
    def test_fallback_score_calculation(self):
        """Testa cálculo de score para fallbacks"""
        metric = HealthMetric(
            metric_type=MetricType.FALLBACKS,
            value=2,
            weight=0.2,
            threshold={"excellent": 1, "good": 5, "warning": 10, "critical": 20},
            status=HealthStatus.GOOD,
            timestamp=datetime.now()
        )
        
        score = metric.calculate_score()
        assert score == 80.0
    
    def test_error_rate_score_calculation(self):
        """Testa cálculo de score para taxa de erro"""
        metric = HealthMetric(
            metric_type=MetricType.ERROR_RATE,
            value=2.0,
            weight=0.15,
            threshold={"excellent": 1.0, "good": 5.0, "warning": 10.0, "critical": 20.0},
            status=HealthStatus.GOOD,
            timestamp=datetime.now()
        )
        
        score = metric.calculate_score()
        assert score == 80.0


class TestHealthScorer:
    """Testes para HealthScorer"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.config = {
            "thresholds": {
                "success_rate": {"excellent": 99.0, "good": 95.0},
                "latency": {"excellent": 100, "good": 500}
            },
            "metric_weights": {
                "success_rate": 0.4,
                "latency": 0.3,
                "fallbacks": 0.2,
                "error_rate": 0.1
            }
        }
        self.scorer = HealthScorer(self.config)
    
    def test_scorer_initialization(self):
        """Testa inicialização do health scorer"""
        scorer = HealthScorer()
        
        assert scorer.default_thresholds is not None
        assert scorer.metric_weights is not None
        assert scorer.cache_ttl == 300
    
    def test_scorer_initialization_with_config(self):
        """Testa inicialização com configuração"""
        scorer = HealthScorer(self.config)
        
        # Verificar se thresholds foram sobrescritos
        assert scorer.default_thresholds[MetricType.SUCCESS_RATE]["excellent"] == 99.0
        assert scorer.default_thresholds[MetricType.LATENCY]["excellent"] == 100
        
        # Verificar se weights foram configurados
        assert scorer.metric_weights[MetricType.SUCCESS_RATE] == 0.4
        assert scorer.metric_weights[MetricType.LATENCY] == 0.3
    
    def test_calculate_success_rate_perfect(self):
        """Testa cálculo de taxa de sucesso perfeita"""
        success_rate = self.scorer.calculate_success_rate(100, 100)
        assert success_rate == 100.0
    
    def test_calculate_success_rate_partial(self):
        """Testa cálculo de taxa de sucesso parcial"""
        success_rate = self.scorer.calculate_success_rate(100, 95)
        assert success_rate == 95.0
    
    def test_calculate_success_rate_zero_requests(self):
        """Testa cálculo de taxa de sucesso com zero requisições"""
        success_rate = self.scorer.calculate_success_rate(0, 0)
        assert success_rate == 100.0
    
    def test_calculate_latency_score(self):
        """Testa cálculo de score de latência"""
        latencies = [50, 100, 150, 200, 250]
        score = self.scorer.calculate_latency_score(latencies)
        
        # Score deve ser baseado no P95
        assert score > 0
        assert score <= 100
    
    def test_calculate_latency_score_empty(self):
        """Testa cálculo de score de latência com lista vazia"""
        score = self.scorer.calculate_latency_score([])
        assert score == 100.0
    
    def test_calculate_fallback_score(self):
        """Testa cálculo de score de fallback"""
        score = self.scorer.calculate_fallback_score(100, 5)
        assert score == 80.0  # 5% fallback rate = good
    
    def test_calculate_fallback_score_no_fallbacks(self):
        """Testa cálculo de score de fallback sem fallbacks"""
        score = self.scorer.calculate_fallback_score(100, 0)
        assert score == 100.0
    
    def test_calculate_error_rate(self):
        """Testa cálculo de taxa de erro"""
        error_rate = self.scorer.calculate_error_rate(100, 5)
        assert error_rate == 5.0
    
    def test_calculate_error_rate_zero_requests(self):
        """Testa cálculo de taxa de erro com zero requisições"""
        error_rate = self.scorer.calculate_error_rate(0, 0)
        assert error_rate == 0.0
    
    def test_calculate_throughput(self):
        """Testa cálculo de throughput"""
        now = datetime.now()
        requests = [
            now - timedelta(minutes=30),
            now - timedelta(minutes=20),
            now - timedelta(minutes=10),
            now - timedelta(minutes=5)
        ]
        
        throughput = self.scorer.calculate_throughput(requests, window_minutes=60)
        assert throughput > 0
    
    def test_calculate_throughput_empty(self):
        """Testa cálculo de throughput com lista vazia"""
        throughput = self.scorer.calculate_throughput([])
        assert throughput == 0.0
    
    def test_calculate_availability(self):
        """Testa cálculo de disponibilidade"""
        availability = self.scorer.calculate_availability(95, 100)
        assert availability == 95.0
    
    def test_calculate_availability_perfect(self):
        """Testa cálculo de disponibilidade perfeita"""
        availability = self.scorer.calculate_availability(100, 100)
        assert availability == 100.0
    
    def test_calculate_availability_zero_total(self):
        """Testa cálculo de disponibilidade com tempo total zero"""
        availability = self.scorer.calculate_availability(0, 0)
        assert availability == 100.0
    
    def test_create_health_metric(self):
        """Testa criação de métrica de saúde"""
        metric = self.scorer.create_health_metric(
            MetricType.SUCCESS_RATE,
            value=95.5,
            weight=0.3
        )
        
        assert metric.metric_type == MetricType.SUCCESS_RATE
        assert metric.value == 95.5
        assert metric.weight == 0.3
        assert metric.status == HealthStatus.GOOD
    
    def test_create_health_metric_custom_thresholds(self):
        """Testa criação de métrica com thresholds customizados"""
        custom_thresholds = {"excellent": 98.0, "good": 90.0, "warning": 80.0, "critical": 70.0}
        
        metric = self.scorer.create_health_metric(
            MetricType.SUCCESS_RATE,
            value=95.0,
            custom_thresholds=custom_thresholds
        )
        
        assert metric.threshold == custom_thresholds
        assert metric.status == HealthStatus.GOOD
    
    def test_calculate_integration_health(self):
        """Testa cálculo de saúde de integração"""
        metrics_data = {
            "success_rate": {"value": 98.5},
            "latency": {"value": 150},
            "fallbacks": {"value": 3},
            "error_rate": {"value": 1.5}
        }
        
        health = self.scorer.calculate_integration_health("test_api", metrics_data)
        
        assert health.integration_name == "test_api"
        assert health.overall_score > 0
        assert health.status in [HealthStatus.EXCELLENT, HealthStatus.GOOD, HealthStatus.WARNING, HealthStatus.CRITICAL]
        assert len(health.metrics) == 4
    
    def test_calculate_integration_health_unknown_metric(self):
        """Testa cálculo com métrica desconhecida"""
        metrics_data = {
            "success_rate": {"value": 98.5},
            "unknown_metric": {"value": 100}  # Métrica desconhecida
        }
        
        health = self.scorer.calculate_integration_health("test_api", metrics_data)
        
        # Deve ignorar métrica desconhecida
        assert len(health.metrics) == 1
        assert MetricType.SUCCESS_RATE in health.metrics
    
    def test_generate_recommendations(self):
        """Testa geração de recomendações"""
        metrics = {
            MetricType.SUCCESS_RATE: HealthMetric(
                metric_type=MetricType.SUCCESS_RATE,
                value=75.0,
                weight=0.3,
                threshold={"excellent": 99.0, "good": 95.0, "warning": 90.0, "critical": 80.0},
                status=HealthStatus.CRITICAL,
                timestamp=datetime.now()
            )
        }
        
        recommendations = self.scorer._generate_recommendations(metrics, 50.0)
        
        assert len(recommendations) > 0
        assert any("Investigar causas" in rec for rec in recommendations)
    
    def test_generate_alerts(self):
        """Testa geração de alertas"""
        metrics = {
            MetricType.SUCCESS_RATE: HealthMetric(
                metric_type=MetricType.SUCCESS_RATE,
                value=75.0,
                weight=0.3,
                threshold={"excellent": 99.0, "good": 95.0, "warning": 90.0, "critical": 80.0},
                status=HealthStatus.CRITICAL,
                timestamp=datetime.now()
            )
        }
        
        alerts = self.scorer._generate_alerts(metrics, HealthStatus.CRITICAL)
        
        assert len(alerts) > 0
        assert any("ALERTA" in alert for alert in alerts)
    
    def test_calculate_trend_improving(self):
        """Testa cálculo de tendência melhorando"""
        # Simular dados históricos com melhoria
        self.scorer.historical_data["test_api"] = deque([
            {"score": 50.0, "timestamp": datetime.now() - timedelta(hours=2)},
            {"score": 60.0, "timestamp": datetime.now() - timedelta(hours=1)},
            {"score": 80.0, "timestamp": datetime.now()}
        ])
        
        trend = self.scorer._calculate_trend("test_api", 80.0)
        assert trend == "improving"
    
    def test_calculate_trend_degrading(self):
        """Testa cálculo de tendência degradando"""
        # Simular dados históricos com degradação
        self.scorer.historical_data["test_api"] = deque([
            {"score": 90.0, "timestamp": datetime.now() - timedelta(hours=2)},
            {"score": 80.0, "timestamp": datetime.now() - timedelta(hours=1)},
            {"score": 60.0, "timestamp": datetime.now()}
        ])
        
        trend = self.scorer._calculate_trend("test_api", 60.0)
        assert trend == "degrading"
    
    def test_calculate_trend_stable(self):
        """Testa cálculo de tendência estável"""
        # Simular dados históricos estáveis
        self.scorer.historical_data["test_api"] = deque([
            {"score": 80.0, "timestamp": datetime.now() - timedelta(hours=2)},
            {"score": 82.0, "timestamp": datetime.now() - timedelta(hours=1)},
            {"score": 81.0, "timestamp": datetime.now()}
        ])
        
        trend = self.scorer._calculate_trend("test_api", 81.0)
        assert trend == "stable"
    
    def test_calculate_system_health(self):
        """Testa cálculo de saúde do sistema"""
        # Criar integrações de teste
        integration1 = IntegrationHealth(
            integration_name="api1",
            overall_score=95.0,
            status=HealthStatus.EXCELLENT,
            metrics={},
            last_updated=datetime.now()
        )
        
        integration2 = IntegrationHealth(
            integration_name="api2",
            overall_score=85.0,
            status=HealthStatus.GOOD,
            metrics={},
            last_updated=datetime.now()
        )
        
        integrations = {"api1": integration1, "api2": integration2}
        
        system_health = self.scorer.calculate_system_health(integrations)
        
        assert system_health.overall_score == 90.0
        assert system_health.total_integrations == 2
        assert system_health.healthy_integrations == 2
        assert system_health.critical_integrations == 0
    
    def test_calculate_system_health_empty(self):
        """Testa cálculo de saúde do sistema vazio"""
        system_health = self.scorer.calculate_system_health({})
        
        assert system_health.overall_score == 0.0
        assert system_health.status == HealthStatus.UNKNOWN
        assert system_health.total_integrations == 0
    
    def test_calculate_system_health_with_critical(self):
        """Testa cálculo de saúde do sistema com integração crítica"""
        integration1 = IntegrationHealth(
            integration_name="api1",
            overall_score=95.0,
            status=HealthStatus.EXCELLENT,
            metrics={},
            last_updated=datetime.now()
        )
        
        integration2 = IntegrationHealth(
            integration_name="api2",
            overall_score=30.0,
            status=HealthStatus.CRITICAL,
            metrics={},
            last_updated=datetime.now()
        )
        
        integrations = {"api1": integration1, "api2": integration2}
        
        system_health = self.scorer.calculate_system_health(integrations)
        
        assert system_health.critical_integrations == 1
        assert system_health.status == HealthStatus.WARNING
    
    def test_get_cached_health(self):
        """Testa obtenção de saúde em cache"""
        # Adicionar ao cache
        health = IntegrationHealth(
            integration_name="test_api",
            overall_score=90.0,
            status=HealthStatus.GOOD,
            metrics={},
            last_updated=datetime.now()
        )
        
        self.scorer.health_cache["test_api"] = {
            "health": health,
            "timestamp": datetime.now()
        }
        
        cached_health = self.scorer.get_cached_health("test_api")
        assert cached_health == health
    
    def test_get_cached_health_expired(self):
        """Testa obtenção de saúde em cache expirado"""
        # Adicionar ao cache com timestamp antigo
        health = IntegrationHealth(
            integration_name="test_api",
            overall_score=90.0,
            status=HealthStatus.GOOD,
            metrics={},
            last_updated=datetime.now()
        )
        
        self.scorer.health_cache["test_api"] = {
            "health": health,
            "timestamp": datetime.now() - timedelta(minutes=10)
        }
        
        cached_health = self.scorer.get_cached_health("test_api")
        assert cached_health is None
    
    def test_clear_cache(self):
        """Testa limpeza de cache"""
        # Adicionar dados ao cache
        self.scorer.health_cache["api1"] = {"health": None, "timestamp": datetime.now()}
        self.scorer.health_cache["api2"] = {"health": None, "timestamp": datetime.now()}
        
        # Limpar cache específico
        self.scorer.clear_cache("api1")
        assert "api1" not in self.scorer.health_cache
        assert "api2" in self.scorer.health_cache
        
        # Limpar todo o cache
        self.scorer.clear_cache()
        assert len(self.scorer.health_cache) == 0
    
    def test_get_historical_data(self):
        """Testa obtenção de dados históricos"""
        # Adicionar dados históricos
        self.scorer.historical_data["test_api"].append({
            "score": 90.0,
            "timestamp": datetime.now() - timedelta(hours=1)
        })
        
        self.scorer.historical_data["test_api"].append({
            "score": 95.0,
            "timestamp": datetime.now()
        })
        
        historical = self.scorer.get_historical_data("test_api", hours=2)
        assert len(historical) == 2
    
    def test_get_historical_data_filtered(self):
        """Testa obtenção de dados históricos filtrados"""
        # Adicionar dados históricos antigos
        self.scorer.historical_data["test_api"].append({
            "score": 90.0,
            "timestamp": datetime.now() - timedelta(hours=3)
        })
        
        # Adicionar dados recentes
        self.scorer.historical_data["test_api"].append({
            "score": 95.0,
            "timestamp": datetime.now()
        })
        
        # Buscar apenas dados das últimas 2 horas
        historical = self.scorer.get_historical_data("test_api", hours=2)
        assert len(historical) == 1
    
    def test_generate_health_report(self):
        """Testa geração de relatório de saúde"""
        # Criar integração de teste
        integration = IntegrationHealth(
            integration_name="test_api",
            overall_score=90.0,
            status=HealthStatus.GOOD,
            metrics={},
            last_updated=datetime.now(),
            recommendations=["Test recommendation"],
            alerts=["Test alert"]
        )
        
        system_health = SystemHealth(
            overall_score=90.0,
            status=HealthStatus.GOOD,
            integrations={"test_api": integration},
            total_integrations=1,
            healthy_integrations=1,
            warning_integrations=0,
            critical_integrations=0,
            last_updated=datetime.now(),
            recommendations=["System recommendation"],
            alerts=["System alert"]
        )
        
        report = self.scorer.generate_health_report(system_health)
        
        assert "tracing_id" in report
        assert report["tracing_id"] == "METRICS-001"
        assert "system_overview" in report
        assert "integrations" in report
        assert "test_api" in report["integrations"]


class TestConvenienceFunctions:
    """Testes para funções de conveniência"""
    
    def test_create_health_scorer(self):
        """Testa função de conveniência create_health_scorer"""
        config = {"test": "config"}
        scorer = create_health_scorer(config)
        
        assert isinstance(scorer, HealthScorer)
        assert scorer.config == config
    
    def test_calculate_integration_health_score(self):
        """Testa função de conveniência calculate_integration_health_score"""
        metrics_data = {
            "success_rate": {"value": 98.5},
            "latency": {"value": 150}
        }
        
        health = calculate_integration_health_score("test_api", metrics_data)
        
        assert isinstance(health, IntegrationHealth)
        assert health.integration_name == "test_api"
        assert health.overall_score > 0
    
    def test_generate_system_health_report(self):
        """Testa função de conveniência generate_system_health_report"""
        integration = IntegrationHealth(
            integration_name="test_api",
            overall_score=90.0,
            status=HealthStatus.GOOD,
            metrics={},
            last_updated=datetime.now()
        )
        
        integrations = {"test_api": integration}
        report = generate_system_health_report(integrations)
        
        assert "tracing_id" in report
        assert "system_overview" in report
        assert "integrations" in report


class TestErrorHandling:
    """Testes para tratamento de erros"""
    
    def test_calculate_integration_health_invalid_metric_type(self):
        """Testa cálculo com tipo de métrica inválido"""
        metrics_data = {
            "invalid_metric": {"value": 100}
        }
        
        health = self.scorer.calculate_integration_health("test_api", metrics_data)
        
        # Deve ignorar métrica inválida
        assert len(health.metrics) == 0
        assert health.overall_score == 0.0
    
    def test_calculate_integration_health_missing_value(self):
        """Testa cálculo com valor ausente"""
        metrics_data = {
            "success_rate": {}  # Sem valor
        }
        
        health = self.scorer.calculate_integration_health("test_api", metrics_data)
        
        # Deve usar valor padrão
        assert len(health.metrics) == 1
        assert health.metrics[MetricType.SUCCESS_RATE].value == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-value"]) 