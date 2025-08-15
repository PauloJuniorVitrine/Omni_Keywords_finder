"""
Testes Unitários - Rate Limits Auditor

Tracing ID: FF-003-TEST
Data/Hora: 2024-12-20 00:08:00 UTC
Versão: 1.0
Status: Implementação Inicial

Testes unitários para o sistema de auditoria de rate limits.
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Importar módulos a serem testados
from scripts.audit.rate_limit_auditor import (
    RateLimitAuditor,
    RateLimitConfig,
    RateLimitUsage,
    RateLimitViolation,
    RateLimitType,
    RateLimitStatus,
    IntegrationType,
    get_rate_limit_auditor,
    check_rate_limit,
    simulate_throttling
)

class TestRateLimitType:
    """Testes para enum RateLimitType"""
    
    def test_rate_limit_type_values(self):
        """Testa valores do enum RateLimitType"""
        assert RateLimitType.REQUESTS_PER_SECOND.value == "requests_per_second"
        assert RateLimitType.REQUESTS_PER_MINUTE.value == "requests_per_minute"
        assert RateLimitType.REQUESTS_PER_HOUR.value == "requests_per_hour"
        assert RateLimitType.REQUESTS_PER_DAY.value == "requests_per_day"
        assert RateLimitType.BANDWIDTH_PER_SECOND.value == "bandwidth_per_second"
        assert RateLimitType.CONCURRENT_CONNECTIONS.value == "concurrent_connections"

class TestRateLimitStatus:
    """Testes para enum RateLimitStatus"""
    
    def test_rate_limit_status_values(self):
        """Testa valores do enum RateLimitStatus"""
        assert RateLimitStatus.NORMAL.value == "normal"
        assert RateLimitStatus.APPROACHING.value == "approaching"
        assert RateLimitStatus.THROTTLED.value == "throttled"
        assert RateLimitStatus.EXCEEDED.value == "exceeded"
        assert RateLimitStatus.BLOCKED.value == "blocked"

class TestIntegrationType:
    """Testes para enum IntegrationType"""
    
    def test_integration_type_values(self):
        """Testa valores do enum IntegrationType"""
        assert IntegrationType.GOOGLE_TRENDS.value == "google_trends"
        assert IntegrationType.GOOGLE_SEARCH_CONSOLE.value == "google_search_console"
        assert IntegrationType.SEMRUSH.value == "semrush"
        assert IntegrationType.WEBHOOK.value == "webhook"
        assert IntegrationType.PAYMENT_GATEWAY.value == "payment_gateway"

class TestRateLimitConfig:
    """Testes para RateLimitConfig"""
    
    def test_rate_limit_config_creation(self):
        """Testa criação de RateLimitConfig"""
        config = RateLimitConfig(
            integration_type=IntegrationType.GOOGLE_TRENDS,
            rate_limit_type=RateLimitType.REQUESTS_PER_MINUTE,
            limit_value=100
        )
        
        assert config.integration_type == IntegrationType.GOOGLE_TRENDS
        assert config.rate_limit_type == RateLimitType.REQUESTS_PER_MINUTE
        assert config.limit_value == 100
        assert config.window_seconds == 60
        assert config.burst_limit is None
        assert config.soft_limit_percentage == 0.8
        assert config.hard_limit_percentage == 1.0
        assert config.retry_after_seconds == 60
        assert config.penalty_seconds == 300
        assert config.created_at is not None
        assert config.updated_at is not None

    def test_rate_limit_config_with_custom_values(self):
        """Testa criação com valores customizados"""
        config = RateLimitConfig(
            integration_type=IntegrationType.SEMRUSH,
            rate_limit_type=RateLimitType.REQUESTS_PER_DAY,
            limit_value=5000,
            window_seconds=86400,
            burst_limit=6000,
            soft_limit_percentage=0.9,
            hard_limit_percentage=1.0,
            retry_after_seconds=7200,
            penalty_seconds=3600,
            metadata={"owner": "api-team", "priority": "high"}
        )
        
        assert config.integration_type == IntegrationType.SEMRUSH
        assert config.rate_limit_type == RateLimitType.REQUESTS_PER_DAY
        assert config.limit_value == 5000
        assert config.window_seconds == 86400
        assert config.burst_limit == 6000
        assert config.soft_limit_percentage == 0.9
        assert config.hard_limit_percentage == 1.0
        assert config.retry_after_seconds == 7200
        assert config.penalty_seconds == 3600
        assert config.metadata["owner"] == "api-team"

class TestRateLimitUsage:
    """Testes para RateLimitUsage"""
    
    def test_rate_limit_usage_creation(self):
        """Testa criação de RateLimitUsage"""
        now = datetime.utcnow()
        usage = RateLimitUsage(
            integration_type=IntegrationType.GOOGLE_TRENDS,
            rate_limit_type=RateLimitType.REQUESTS_PER_MINUTE,
            current_usage=50,
            limit_value=100,
            window_start=now,
            window_end=now + timedelta(minutes=1),
            usage_percentage=0.5,
            status=RateLimitStatus.NORMAL,
            last_request_time=now
        )
        
        assert usage.integration_type == IntegrationType.GOOGLE_TRENDS
        assert usage.rate_limit_type == RateLimitType.REQUESTS_PER_MINUTE
        assert usage.current_usage == 50
        assert usage.limit_value == 100
        assert usage.usage_percentage == 0.5
        assert usage.status == RateLimitStatus.NORMAL
        assert usage.throttled_requests == 0
        assert usage.blocked_requests == 0
        assert usage.retry_after is None

    def test_rate_limit_usage_with_violations(self):
        """Testa criação com violações"""
        now = datetime.utcnow()
        usage = RateLimitUsage(
            integration_type=IntegrationType.WEBHOOK,
            rate_limit_type=RateLimitType.REQUESTS_PER_SECOND,
            current_usage=15,
            limit_value=10,
            window_start=now,
            window_end=now + timedelta(seconds=1),
            usage_percentage=1.5,
            status=RateLimitStatus.EXCEEDED,
            last_request_time=now,
            throttled_requests=5,
            blocked_requests=3,
            retry_after=now + timedelta(seconds=30)
        )
        
        assert usage.current_usage == 15
        assert usage.limit_value == 10
        assert usage.usage_percentage == 1.5
        assert usage.status == RateLimitStatus.EXCEEDED
        assert usage.throttled_requests == 5
        assert usage.blocked_requests == 3
        assert usage.retry_after is not None

class TestRateLimitViolation:
    """Testes para RateLimitViolation"""
    
    def test_rate_limit_violation_creation(self):
        """Testa criação de RateLimitViolation"""
        now = datetime.utcnow()
        violation = RateLimitViolation(
            integration_type=IntegrationType.GOOGLE_TRENDS,
            rate_limit_type=RateLimitType.REQUESTS_PER_MINUTE,
            violation_time=now,
            limit_value=100,
            actual_usage=120,
            violation_percentage=120.0,
            penalty_applied=True,
            retry_after=now + timedelta(minutes=1),
            metadata={"window_start": now.isoformat()}
        )
        
        assert violation.integration_type == IntegrationType.GOOGLE_TRENDS
        assert violation.rate_limit_type == RateLimitType.REQUESTS_PER_MINUTE
        assert violation.limit_value == 100
        assert violation.actual_usage == 120
        assert violation.violation_percentage == 120.0
        assert violation.penalty_applied is True
        assert violation.retry_after is not None
        assert violation.metadata["window_start"] == now.isoformat()

class TestRateLimitAuditor:
    """Testes para RateLimitAuditor"""
    
    @pytest.fixture
    def auditor(self):
        """Fixture para instância de auditor"""
        return RateLimitAuditor()
    
    def test_initialization(self, auditor):
        """Testa inicialização do auditor"""
        assert len(auditor.rate_limits) > 0
        assert len(auditor.current_usage) == 0
        assert len(auditor.violations) == 0
        assert len(auditor.alerts) == 0

    def test_initialize_default_limits(self, auditor):
        """Testa inicialização dos rate limits padrão"""
        # Verificar se Google Trends tem rate limits
        google_trends_key = "google_trends_requests_per_minute"
        assert google_trends_key in auditor.rate_limits
        
        config = auditor.rate_limits[google_trends_key]
        assert config.integration_type == IntegrationType.GOOGLE_TRENDS
        assert config.rate_limit_type == RateLimitType.REQUESTS_PER_MINUTE
        assert config.limit_value == 100
        assert config.window_seconds == 60
        
        # Verificar se SEMRUSH tem rate limits
        semrush_key = "semrush_requests_per_minute"
        assert semrush_key in auditor.rate_limits
        
        config = auditor.rate_limits[semrush_key]
        assert config.integration_type == IntegrationType.SEMRUSH
        assert config.limit_value == 30

    def test_check_rate_limit_normal(self, auditor):
        """Testa verificação de rate limit normal"""
        # Primeira verificação deve ser permitida
        result = auditor.check_rate_limit(IntegrationType.GOOGLE_TRENDS)
        assert result is True
        
        # Verificar se uso foi registrado
        key = "google_trends_requests_per_minute"
        usage = auditor.current_usage.get(key)
        assert usage is not None
        assert usage.current_usage == 1
        assert usage.status == RateLimitStatus.NORMAL

    def test_check_rate_limit_approaching(self, auditor):
        """Testa verificação de rate limit aproximando do limite"""
        # Configurar uso próximo do limite
        key = "google_trends_requests_per_minute"
        config = auditor.rate_limits[key]
        
        # Simular 80 requisições (80% do limite)
        for index in range(80):
            auditor.check_rate_limit(IntegrationType.GOOGLE_TRENDS)
        
        usage = auditor.current_usage[key]
        assert usage.current_usage == 80
        assert usage.status == RateLimitStatus.APPROACHING

    def test_check_rate_limit_exceeded(self, auditor):
        """Testa verificação de rate limit excedido"""
        # Configurar uso no limite
        key = "google_trends_requests_per_minute"
        config = auditor.rate_limits[key]
        
        # Simular 100 requisições (100% do limite)
        for index in range(100):
            result = auditor.check_rate_limit(IntegrationType.GOOGLE_TRENDS)
            if index < 99:  # As primeiras 99 devem ser permitidas
                assert result is True
        
        # A 100ª deve ser bloqueada
        result = auditor.check_rate_limit(IntegrationType.GOOGLE_TRENDS)
        assert result is False
        
        usage = auditor.current_usage[key]
        assert usage.status == RateLimitStatus.EXCEEDED
        assert usage.retry_after is not None

    def test_check_rate_limit_retry_after(self, auditor):
        """Testa verificação após período de retry"""
        # Exceder limite
        for index in range(101):
            auditor.check_rate_limit(IntegrationType.GOOGLE_TRENDS)
        
        key = "google_trends_requests_per_minute"
        usage = auditor.current_usage[key]
        assert usage.status == RateLimitStatus.EXCEEDED
        
        # Tentar novamente (deve ser bloqueado)
        result = auditor.check_rate_limit(IntegrationType.GOOGLE_TRENDS)
        assert result is False
        
        # Simular passagem do tempo de retry
        usage.retry_after = datetime.utcnow() - timedelta(seconds=1)
        
        # Agora deve ser permitido
        result = auditor.check_rate_limit(IntegrationType.GOOGLE_TRENDS)
        assert result is True
        assert usage.status == RateLimitStatus.NORMAL

    def test_check_rate_limit_unconfigured(self, auditor):
        """Testa verificação de rate limit não configurado"""
        # Tentar verificar integração não configurada
        result = auditor.check_rate_limit(IntegrationType.ANALYTICS)
        assert result is True  # Deve permitir se não configurado

    def test_simulate_throttling(self, auditor):
        """Testa simulação de throttling"""
        # Simular 50 requisições
        result = auditor.simulate_throttling(
            IntegrationType.GOOGLE_TRENDS,
            RateLimitType.REQUESTS_PER_MINUTE,
            50
        )
        
        assert result["integration_type"] == "google_trends"
        assert result["rate_limit_type"] == "requests_per_minute"
        assert result["requests_count"] == 50
        assert result["allowed_requests"] == 50  # Todas devem ser permitidas
        assert result["blocked_requests"] == 0
        assert result["simulation_time"] > 0
        assert result["requests_per_second"] > 0

    def test_simulate_throttling_exceed_limit(self, auditor):
        """Testa simulação de throttling excedendo limite"""
        # Simular 150 requisições (mais que o limite de 100)
        result = auditor.simulate_throttling(
            IntegrationType.GOOGLE_TRENDS,
            RateLimitType.REQUESTS_PER_MINUTE,
            150
        )
        
        assert result["integration_type"] == "google_trends"
        assert result["requests_count"] == 150
        assert result["allowed_requests"] == 100  # Apenas 100 devem ser permitidas
        assert result["blocked_requests"] == 50   # 50 devem ser bloqueadas
        assert result["violations"] > 0

    def test_get_rate_limit_config(self, auditor):
        """Testa obtenção de configuração de rate limit"""
        config = auditor.get_rate_limit_config(
            IntegrationType.GOOGLE_TRENDS,
            RateLimitType.REQUESTS_PER_MINUTE
        )
        
        assert config is not None
        assert config.integration_type == IntegrationType.GOOGLE_TRENDS
        assert config.rate_limit_type == RateLimitType.REQUESTS_PER_MINUTE
        assert config.limit_value == 100
        
        # Teste com configuração inexistente
        config = auditor.get_rate_limit_config(
            IntegrationType.ANALYTICS,
            RateLimitType.REQUESTS_PER_MINUTE
        )
        assert config is None

    def test_get_current_usage(self, auditor):
        """Testa obtenção de uso atual"""
        # Fazer algumas requisições
        for index in range(10):
            auditor.check_rate_limit(IntegrationType.GOOGLE_TRENDS)
        
        usage = auditor.get_current_usage(
            IntegrationType.GOOGLE_TRENDS,
            RateLimitType.REQUESTS_PER_MINUTE
        )
        
        assert usage is not None
        assert usage.current_usage == 10
        assert usage.integration_type == IntegrationType.GOOGLE_TRENDS
        
        # Teste com uso inexistente
        usage = auditor.get_current_usage(
            IntegrationType.ANALYTICS,
            RateLimitType.REQUESTS_PER_MINUTE
        )
        assert usage is None

    def test_get_all_usage(self, auditor):
        """Testa obtenção de todos os usos"""
        # Fazer requisições em diferentes integrações
        auditor.check_rate_limit(IntegrationType.GOOGLE_TRENDS)
        auditor.check_rate_limit(IntegrationType.SEMRUSH)
        
        all_usage = auditor.get_all_usage()
        
        assert len(all_usage) == 2
        assert "google_trends_requests_per_minute" in all_usage
        assert "semrush_requests_per_minute" in all_usage

    def test_get_violations(self, auditor):
        """Testa obtenção de violações"""
        # Criar algumas violações
        for index in range(110):  # Exceder limite
            auditor.check_rate_limit(IntegrationType.GOOGLE_TRENDS)
        
        violations = auditor.get_violations()
        assert len(violations) > 0
        
        # Filtrar por integração
        google_violations = auditor.get_violations(IntegrationType.GOOGLE_TRENDS)
        assert len(google_violations) > 0
        
        # Filtrar por período
        violations_24h = auditor.get_violations(days=1)
        assert len(violations_24h) > 0

    def test_get_alerts(self, auditor):
        """Testa obtenção de alertas"""
        # Criar alguns alertas
        for index in range(85):  # Aproximar do limite (80%)
            auditor.check_rate_limit(IntegrationType.GOOGLE_TRENDS)
        
        alerts = auditor.get_alerts()
        assert len(alerts) > 0
        
        # Filtrar por período
        alerts_1h = auditor.get_alerts(hours=1)
        assert len(alerts_1h) > 0

    def test_update_rate_limit_config(self, auditor):
        """Testa atualização de configuração de rate limit"""
        # Obter configuração original
        config = auditor.get_rate_limit_config(
            IntegrationType.GOOGLE_TRENDS,
            RateLimitType.REQUESTS_PER_MINUTE
        )
        original_limit = config.limit_value
        
        # Atualizar configuração
        updates = {"limit_value": original_limit + 50}
        result = auditor.update_rate_limit_config(
            IntegrationType.GOOGLE_TRENDS,
            RateLimitType.REQUESTS_PER_MINUTE,
            updates
        )
        
        assert result is True
        
        # Verificar se foi atualizada
        updated_config = auditor.get_rate_limit_config(
            IntegrationType.GOOGLE_TRENDS,
            RateLimitType.REQUESTS_PER_MINUTE
        )
        assert updated_config.limit_value == original_limit + 50

    def test_update_rate_limit_config_invalid(self, auditor):
        """Testa atualização de configuração inválida"""
        # Tentar atualizar configuração inexistente
        result = auditor.update_rate_limit_config(
            IntegrationType.ANALYTICS,
            RateLimitType.REQUESTS_PER_MINUTE,
            {"limit_value": 100}
        )
        assert result is False

    def test_get_compliance_report(self, auditor):
        """Testa geração de relatório de compliance"""
        # Criar alguns dados de uso
        for index in range(10):
            auditor.check_rate_limit(IntegrationType.GOOGLE_TRENDS)
            auditor.check_rate_limit(IntegrationType.SEMRUSH)
        
        report = auditor.get_compliance_report()
        
        assert "timestamp" in report
        assert "summary" in report
        assert "integrations" in report
        
        summary = report["summary"]
        assert summary["total_integrations"] > 0
        assert summary["total_rate_limits"] > 0
        
        integrations = report["integrations"]
        assert "google_trends" in integrations
        assert "semrush" in integrations

    def test_get_performance_metrics(self, auditor):
        """Testa obtenção de métricas de performance"""
        # Criar alguns dados de uso
        for index in range(10):
            auditor.check_rate_limit(IntegrationType.GOOGLE_TRENDS)
        
        metrics = auditor.get_performance_metrics()
        
        assert "timestamp" in metrics
        assert "rate_limits" in metrics
        assert "summary" in metrics
        
        summary = metrics["summary"]
        assert summary["total_rate_limits"] > 0
        assert summary["active_usage"] > 0
        
        rate_limits = metrics["rate_limits"]
        assert "google_trends_requests_per_minute" in rate_limits

    def test_get_health_status(self, auditor):
        """Testa obtenção de status de saúde"""
        status = auditor.get_health_status()
        
        assert "status" in status
        assert "total_rate_limits" in status
        assert "active_usage" in status
        assert "recent_violations_1h" in status
        assert "recent_alerts_1h" in status
        assert "timestamp" in status

    def test_record_violation(self, auditor):
        """Testa registro de violação"""
        # Configurar uso
        key = "google_trends_requests_per_minute"
        config = auditor.rate_limits[key]
        
        usage = RateLimitUsage(
            integration_type=IntegrationType.GOOGLE_TRENDS,
            rate_limit_type=RateLimitType.REQUESTS_PER_MINUTE,
            current_usage=120,
            limit_value=100,
            window_start=datetime.utcnow(),
            window_end=datetime.utcnow() + timedelta(minutes=1),
            usage_percentage=1.2,
            status=RateLimitStatus.EXCEEDED,
            last_request_time=datetime.utcnow()
        )
        
        # Registrar violação
        auditor._record_violation(
            IntegrationType.GOOGLE_TRENDS,
            RateLimitType.REQUESTS_PER_MINUTE,
            usage,
            config
        )
        
        assert len(auditor.violations) == 1
        violation = auditor.violations[0]
        assert violation.integration_type == IntegrationType.GOOGLE_TRENDS
        assert violation.actual_usage == 120
        assert violation.violation_percentage == 120.0

    def test_generate_alert(self, auditor):
        """Testa geração de alerta"""
        key = "google_trends_requests_per_minute"
        usage = RateLimitUsage(
            integration_type=IntegrationType.GOOGLE_TRENDS,
            rate_limit_type=RateLimitType.REQUESTS_PER_MINUTE,
            current_usage=90,
            limit_value=100,
            window_start=datetime.utcnow(),
            window_end=datetime.utcnow() + timedelta(minutes=1),
            usage_percentage=0.9,
            status=RateLimitStatus.APPROACHING,
            last_request_time=datetime.utcnow()
        )
        
        # Gerar alerta
        auditor._generate_alert(key, usage, "approaching_limit")
        
        assert len(auditor.alerts) == 1
        alert = auditor.alerts[0]
        assert alert["key"] == key
        assert alert["alert_type"] == "approaching_limit"
        assert alert["current_usage"] == 90
        assert alert["limit_value"] == 100

class TestGlobalFunctions:
    """Testes para funções globais"""
    
    @patch('scripts.audit.rate_limit_auditor._rate_limit_auditor')
    def test_get_rate_limit_auditor(self, mock_global_auditor):
        """Testa obtenção de instância global"""
        # Simular instância global
        mock_global_auditor.return_value = Mock()
        
        result = get_rate_limit_auditor()
        assert result is not None

    @patch('scripts.audit.rate_limit_auditor.get_rate_limit_auditor')
    def test_check_rate_limit(self, mock_get_auditor):
        """Testa função de conveniência check_rate_limit"""
        mock_auditor = Mock()
        mock_get_auditor.return_value = mock_auditor
        mock_auditor.check_rate_limit.return_value = True
        
        result = check_rate_limit("google_trends", "requests_per_minute")
        
        assert result is True
        mock_auditor.check_rate_limit.assert_called_once()

    @patch('scripts.audit.rate_limit_auditor.get_rate_limit_auditor')
    def test_simulate_throttling(self, mock_get_auditor):
        """Testa função de conveniência simulate_throttling"""
        mock_auditor = Mock()
        mock_get_auditor.return_value = mock_auditor
        mock_auditor.simulate_throttling.return_value = {
            "integration_type": "google_trends",
            "allowed_requests": 50,
            "blocked_requests": 0
        }
        
        result = simulate_throttling("google_trends", "requests_per_minute", 50)
        
        assert result["integration_type"] == "google_trends"
        assert result["allowed_requests"] == 50
        mock_auditor.simulate_throttling.assert_called_once()

class TestErrorHandling:
    """Testes para tratamento de erros"""
    
    def test_check_rate_limit_with_exception(self, auditor):
        """Testa tratamento de exceção em check_rate_limit"""
        # Simular exceção
        with patch.object(auditor, 'rate_limits', side_effect=Exception("Test error")):
            result = auditor.check_rate_limit(IntegrationType.GOOGLE_TRENDS)
            assert result is True  # Deve permitir em caso de erro

    def test_simulate_throttling_with_exception(self, auditor):
        """Testa tratamento de exceção em simulate_throttling"""
        # Simular exceção
        with patch.object(auditor, 'check_rate_limit', side_effect=Exception("Test error")):
            result = auditor.simulate_throttling(IntegrationType.GOOGLE_TRENDS)
            assert "error" in result

    def test_health_status_with_exception(self, auditor):
        """Testa tratamento de exceção em get_health_status"""
        # Simular exceção
        with patch.object(auditor, 'violations', side_effect=Exception("Test error")):
            status = auditor.get_health_status()
            assert status["status"] == "unhealthy"
            assert "error" in status

class TestIntegrationScenarios:
    """Testes para cenários de integração"""
    
    def test_google_trends_scenario(self, auditor):
        """Testa cenário completo para Google Trends"""
        # Simular uso normal
        for index in range(50):
            result = auditor.check_rate_limit(IntegrationType.GOOGLE_TRENDS)
            assert result is True
        
        usage = auditor.get_current_usage(IntegrationType.GOOGLE_TRENDS)
        assert usage.current_usage == 50
        assert usage.status == RateLimitStatus.NORMAL
        
        # Simular uso próximo do limite
        for index in range(30):
            result = auditor.check_rate_limit(IntegrationType.GOOGLE_TRENDS)
            assert result is True
        
        usage = auditor.get_current_usage(IntegrationType.GOOGLE_TRENDS)
        assert usage.current_usage == 80
        assert usage.status == RateLimitStatus.APPROACHING
        
        # Verificar alertas
        alerts = auditor.get_alerts()
        assert len(alerts) > 0

    def test_semrush_scenario(self, auditor):
        """Testa cenário completo para SEMRUSH"""
        # SEMRUSH tem limite de 30 por minuto
        for index in range(30):
            result = auditor.check_rate_limit(IntegrationType.SEMRUSH)
            assert result is True
        
        # A 31ª deve ser bloqueada
        result = auditor.check_rate_limit(IntegrationType.SEMRUSH)
        assert result is False
        
        usage = auditor.get_current_usage(IntegrationType.SEMRUSH)
        assert usage.status == RateLimitStatus.EXCEEDED
        
        # Verificar violações
        violations = auditor.get_violations(IntegrationType.SEMRUSH)
        assert len(violations) > 0

    def test_webhook_scenario(self, auditor):
        """Testa cenário completo para Webhook"""
        # Webhook tem limite de 10 por segundo
        for index in range(10):
            result = auditor.check_rate_limit(IntegrationType.WEBHOOK, RateLimitType.REQUESTS_PER_SECOND)
            assert result is True
        
        # A 11ª deve ser bloqueada
        result = auditor.check_rate_limit(IntegrationType.WEBHOOK, RateLimitType.REQUESTS_PER_SECOND)
        assert result is False
        
        # Simular throttling
        simulation = auditor.simulate_throttling(IntegrationType.WEBHOOK, RateLimitType.REQUESTS_PER_SECOND, 20)
        assert simulation["allowed_requests"] == 10
        assert simulation["blocked_requests"] == 10 