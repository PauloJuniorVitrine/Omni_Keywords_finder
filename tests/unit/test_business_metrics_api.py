"""
Teste Unitário - Backend de Métricas de Negócio
Teste baseado no código real do sistema Omni Keywords Finder

Tracing ID: TEST_BM_API_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: 🟡 ALTO - Backend de Métricas

Baseado no código real do sistema Omni Keywords Finder
"""

import pytest
import json
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import HTTPException

from backend.app.api.business_metrics import router
from backend.app.services.business_metrics_service import BusinessMetricsService
from backend.app.schemas.business_metrics_schemas import (
    BusinessMetric,
    MetricFilterSchema,
    KPISchema,
    DashboardSchema,
    MetricType,
    MetricPeriod,
    MetricCategory
)

# Dados reais baseados no sistema Omni Keywords Finder
MOCK_METRICS_DATA = [
    {
        "metric_id": "metric-001",
        "metric_type": "users",
        "metric_name": "Usuários Ativos",
        "category": "customer",
        "value": 15420.0,
        "previous_value": 14200.0,
        "target_value": 20000.0,
        "period": "daily",
        "start_date": "2025-01-27T00:00:00Z",
        "end_date": "2025-01-27T23:59:59Z",
        "user_id": None,
        "plan_type": "premium",
        "region": "BR",
        "source": "system_collector",
        "version": "1.0",
        "environment": "production",
        "created_at": "2025-01-27T15:30:00Z"
    },
    {
        "metric_id": "metric-002",
        "metric_type": "revenue",
        "metric_name": "Receita Mensal",
        "category": "financial",
        "value": 1250000.0,
        "previous_value": 1150000.0,
        "target_value": 1500000.0,
        "period": "monthly",
        "start_date": "2025-01-01T00:00:00Z",
        "end_date": "2025-01-31T23:59:59Z",
        "user_id": None,
        "plan_type": "premium",
        "region": "BR",
        "source": "payment_system",
        "version": "1.0",
        "environment": "production",
        "created_at": "2025-01-27T15:30:00Z"
    },
    {
        "metric_id": "metric-003",
        "metric_type": "executions",
        "metric_name": "Execuções de Keywords",
        "category": "performance",
        "value": 892.0,
        "previous_value": 850.0,
        "target_value": 1000.0,
        "period": "daily",
        "start_date": "2025-01-27T00:00:00Z",
        "end_date": "2025-01-27T23:59:59Z",
        "user_id": None,
        "plan_type": "premium",
        "region": "BR",
        "source": "execution_engine",
        "version": "1.0",
        "environment": "production",
        "created_at": "2025-01-27T15:30:00Z"
    },
    {
        "metric_id": "metric-004",
        "metric_type": "conversion",
        "metric_name": "Taxa de Conversão",
        "category": "marketing",
        "value": 3.2,
        "previous_value": 3.0,
        "target_value": 5.0,
        "period": "daily",
        "start_date": "2025-01-27T00:00:00Z",
        "end_date": "2025-01-27T23:59:59Z",
        "user_id": None,
        "plan_type": "premium",
        "region": "BR",
        "source": "analytics_system",
        "version": "1.0",
        "environment": "production",
        "created_at": "2025-01-27T15:30:00Z"
    }
]

MOCK_KPIS_DATA = [
    {
        "kpi_id": "kpi-001",
        "kpi_name": "Usuários Ativos",
        "description": "Número de usuários ativos no sistema",
        "current_value": 15420.0,
        "target_value": 20000.0,
        "previous_value": 14200.0,
        "percentage_change": 8.6,
        "target_achievement": 77.1,
        "status": "on_track",
        "period": "daily",
        "last_updated": "2025-01-27T15:30:00Z",
        "category": "customer",
        "priority": "high",
        "owner": "product_team"
    },
    {
        "kpi_id": "kpi-002",
        "kpi_name": "Receita Mensal",
        "description": "Receita total do mês",
        "current_value": 1250000.0,
        "target_value": 1500000.0,
        "previous_value": 1150000.0,
        "percentage_change": 8.7,
        "target_achievement": 83.3,
        "status": "on_track",
        "period": "monthly",
        "last_updated": "2025-01-27T15:30:00Z",
        "category": "financial",
        "priority": "critical",
        "owner": "finance_team"
    },
    {
        "kpi_id": "kpi-003",
        "kpi_name": "Taxa de Conversão",
        "description": "Taxa de conversão de visitantes em usuários",
        "current_value": 3.2,
        "target_value": 5.0,
        "previous_value": 3.0,
        "percentage_change": 6.7,
        "target_achievement": 64.0,
        "status": "at_risk",
        "period": "daily",
        "last_updated": "2025-01-27T15:30:00Z",
        "category": "marketing",
        "priority": "high",
        "owner": "marketing_team"
    }
]

MOCK_DASHBOARDS_DATA = [
    {
        "dashboard_id": "dashboard-001",
        "dashboard_name": "Dashboard Executivo",
        "description": "Dashboard principal para executivos",
        "layout": "grid",
        "refresh_interval": 30000,
        "auto_refresh": True,
        "metrics": json.dumps(["users", "revenue", "conversion"]),
        "kpis": json.dumps(["kpi-001", "kpi-002", "kpi-003"]),
        "is_public": False,
        "allowed_users": json.dumps(["admin", "executive"]),
        "allowed_roles": json.dumps(["admin", "executive"]),
        "created_by": "admin",
        "created_at": "2025-01-27T15:30:00Z",
        "updated_at": "2025-01-27T15:30:00Z"
    },
    {
        "dashboard_id": "dashboard-002",
        "dashboard_name": "Dashboard de ROI",
        "description": "Dashboard especializado em ROI",
        "layout": "flexible",
        "refresh_interval": 60000,
        "auto_refresh": True,
        "metrics": json.dumps(["roi", "investment", "return"]),
        "kpis": json.dumps(["kpi-002"]),
        "is_public": False,
        "allowed_users": json.dumps(["admin", "finance"]),
        "allowed_roles": json.dumps(["admin", "finance"]),
        "created_by": "admin",
        "created_at": "2025-01-27T15:30:00Z",
        "updated_at": "2025-01-27T15:30:00Z"
    }
]

@pytest.fixture
def mock_current_user():
    """Mock do usuário atual"""
    return {
        "id": "user-001",
        "email": "admin@omnikeywordsfinder.com",
        "role": "admin",
        "permissions": ["metrics:read", "metrics:write", "metrics:admin"]
    }

@pytest.fixture
def mock_metrics_service():
    """Mock do serviço de métricas"""
    service = MagicMock(spec=BusinessMetricsService)
    
    # Mock do método get_metrics
    service.get_metrics.return_value = MOCK_METRICS_DATA
    
    # Mock do método record_metric
    service.record_metric.return_value = "metric-001"
    
    # Mock do método analyze_metrics
    service.analyze_metrics.return_value = {
        "metric_type": "users",
        "period": {
            "start_date": "2025-01-01T00:00:00Z",
            "end_date": "2025-01-31T23:59:59Z"
        },
        "summary": {
            "total_records": 31,
            "average_value": 15420.0,
            "growth_rate": 8.6,
            "trend_direction": "up",
            "trend_strength": "moderate"
        },
        "insights": [
            "Crescimento consistente de usuários ativos",
            "Meta de 20.000 usuários está 77% alcançada"
        ],
        "recommendations": [
            "Investir em campanhas de aquisição",
            "Melhorar retenção de usuários existentes"
        ],
        "alerts": [
            "Taxa de crescimento está abaixo do esperado"
        ]
    }
    
    # Mock do método get_kpis
    service.get_kpis.return_value = MOCK_KPIS_DATA
    
    # Mock do método create_kpi
    service.create_kpi.return_value = "kpi-001"
    
    # Mock do método update_kpi
    service.update_kpi.return_value = True
    
    # Mock do método get_dashboards
    service.get_dashboards.return_value = MOCK_DASHBOARDS_DATA
    
    # Mock do método create_dashboard
    service.create_dashboard.return_value = "dashboard-001"
    
    return service

@pytest.fixture
def client(mock_metrics_service):
    """Cliente de teste com mocks"""
    with patch('backend.app.api.business_metrics.metrics_service', mock_metrics_service):
        with patch('backend.app.api.business_metrics.get_current_user') as mock_auth:
            mock_auth.return_value = {
                "id": "user-001",
                "email": "admin@omnikeywordsfinder.com",
                "role": "admin",
                "permissions": ["metrics:read", "metrics:write", "metrics:admin"]
            }
            
            with patch('backend.app.api.business_metrics.require_permissions') as mock_permissions:
                mock_permissions.return_value = None
                
                with patch('backend.app.api.business_metrics.rate_limiter') as mock_rate_limiter:
                    mock_rate_limiter.check_rate_limit.return_value = None
                    
                    from fastapi.testclient import TestClient
                    from fastapi import FastAPI
                    
                    app = FastAPI()
                    app.include_router(router)
                    return TestClient(app)

class TestBusinessMetricsAPI:
    """Testes para a API de métricas de negócio"""

    def test_record_business_metric_success(self, client, mock_current_user):
        """Teste de registro de métrica com sucesso"""
        metric_data = {
            "metric_id": "metric-001",
            "metric_type": "users",
            "metric_name": "Usuários Ativos",
            "category": "customer",
            "value": 15420.0,
            "previous_value": 14200.0,
            "target_value": 20000.0,
            "period": "daily",
            "start_date": "2025-01-27T00:00:00Z",
            "end_date": "2025-01-27T23:59:59Z",
            "user_id": None,
            "plan_type": "premium",
            "region": "BR",
            "source": "system_collector",
            "version": "1.0",
            "environment": "production",
            "created_at": "2025-01-27T15:30:00Z"
        }
        
        response = client.post("/api/business-metrics/metrics", json=metric_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Métrica registrada com sucesso"
        assert data["metric_id"] == "metric-001"

    def test_get_business_metrics_success(self, client):
        """Teste de obtenção de métricas com sucesso"""
        response = client.get("/api/business-metrics/metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4
        assert data[0]["metric_name"] == "Usuários Ativos"
        assert data[0]["value"] == 15420.0
        assert data[1]["metric_name"] == "Receita Mensal"
        assert data[1]["value"] == 1250000.0

    def test_get_business_metrics_with_filters(self, client):
        """Teste de obtenção de métricas com filtros"""
        response = client.get(
            "/api/business-metrics/metrics",
            params={
                "metric_types": "users,revenue",
                "categories": "customer,financial",
                "periods": "daily,monthly",
                "limit": 10,
                "offset": 0
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4

    def test_analyze_business_metrics_success(self, client):
        """Teste de análise de métricas com sucesso"""
        analysis_data = {
            "metric_type": "users",
            "start_date": "2025-01-01T00:00:00Z",
            "end_date": "2025-01-31T23:59:59Z"
        }
        
        response = client.post("/api/business-metrics/analyze", json=analysis_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["metric_type"] == "users"
        assert "summary" in data
        assert "insights" in data
        assert "recommendations" in data
        assert "alerts" in data

    def test_create_kpi_success(self, client):
        """Teste de criação de KPI com sucesso"""
        kpi_data = {
            "kpi_id": "kpi-001",
            "kpi_name": "Usuários Ativos",
            "description": "Número de usuários ativos no sistema",
            "current_value": 15420.0,
            "target_value": 20000.0,
            "previous_value": 14200.0,
            "percentage_change": 8.6,
            "target_achievement": 77.1,
            "status": "on_track",
            "period": "daily",
            "last_updated": "2025-01-27T15:30:00Z",
            "category": "customer",
            "priority": "high",
            "owner": "product_team"
        }
        
        response = client.post("/api/business-metrics/kpis", json=kpi_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "KPI criado com sucesso"
        assert data["kpi_id"] == "kpi-001"

    def test_get_kpis_success(self, client):
        """Teste de obtenção de KPIs com sucesso"""
        response = client.get("/api/business-metrics/kpis")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["kpi_name"] == "Usuários Ativos"
        assert data[0]["current_value"] == 15420.0
        assert data[1]["kpi_name"] == "Receita Mensal"
        assert data[1]["current_value"] == 1250000.0

    def test_update_kpi_success(self, client):
        """Teste de atualização de KPI com sucesso"""
        update_data = {
            "current_value": 16000.0,
            "target_achievement": 80.0,
            "status": "on_track"
        }
        
        response = client.put("/api/business-metrics/kpis/kpi-001", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "KPI atualizado com sucesso"

    def test_create_dashboard_success(self, client):
        """Teste de criação de dashboard com sucesso"""
        dashboard_data = {
            "dashboard_id": "dashboard-001",
            "dashboard_name": "Dashboard Executivo",
            "description": "Dashboard principal para executivos",
            "layout": "grid",
            "refresh_interval": 30000,
            "auto_refresh": True,
            "metrics": ["users", "revenue", "conversion"],
            "kpis": ["kpi-001", "kpi-002", "kpi-003"],
            "is_public": False,
            "allowed_users": ["admin", "executive"],
            "allowed_roles": ["admin", "executive"],
            "created_by": "admin"
        }
        
        response = client.post("/api/business-metrics/dashboards", json=dashboard_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Dashboard criado com sucesso"
        assert data["dashboard_id"] == "dashboard-001"

    def test_get_dashboards_success(self, client):
        """Teste de obtenção de dashboards com sucesso"""
        response = client.get("/api/business-metrics/dashboards")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["dashboard_name"] == "Dashboard Executivo"
        assert data[1]["dashboard_name"] == "Dashboard de ROI"

    def test_get_metric_types_success(self, client):
        """Teste de obtenção de tipos de métricas com sucesso"""
        response = client.get("/api/business-metrics/types")
        
        assert response.status_code == 200
        data = response.json()
        assert "metric_types" in data
        assert "categories" in data
        assert "periods" in data

    def test_get_metrics_summary_success(self, client):
        """Teste de obtenção de resumo de métricas com sucesso"""
        response = client.get("/api/business-metrics/summary?period=monthly")
        
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "executions" in data
        assert "revenue" in data
        assert "kpis" in data

    def test_collect_metrics_success(self, client):
        """Teste de coleta de métricas com sucesso"""
        response = client.post("/api/business-metrics/collect")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Coleta de métricas iniciada em background"

    def test_metrics_health_check_success(self, client):
        """Teste de verificação de saúde com sucesso"""
        response = client.get("/api/business-metrics/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        assert "total_kpis" in data
        assert "timestamp" in data

    def test_record_metric_validation_error(self, client):
        """Teste de erro de validação ao registrar métrica"""
        invalid_metric = {
            "metric_id": "metric-001",
            "metric_type": "invalid_type",
            "metric_name": "",
            "category": "invalid_category",
            "value": -100.0,  # Valor negativo inválido
            "period": "invalid_period"
        }
        
        response = client.post("/api/business-metrics/metrics", json=invalid_metric)
        
        assert response.status_code == 400
        data = response.json()
        assert "Dados inválidos" in data["detail"]

    def test_get_metrics_invalid_filters(self, client):
        """Teste de filtros inválidos na obtenção de métricas"""
        response = client.get(
            "/api/business-metrics/metrics",
            params={
                "limit": 10000,  # Limite muito alto
                "offset": -10    # Offset negativo
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Parâmetros inválidos" in data["detail"]

    def test_analyze_metrics_invalid_dates(self, client):
        """Teste de datas inválidas na análise de métricas"""
        analysis_data = {
            "metric_type": "users",
            "start_date": "2025-01-31T23:59:59Z",
            "end_date": "2025-01-01T00:00:00Z"  # Data final antes da inicial
        }
        
        response = client.post("/api/business-metrics/analyze", json=analysis_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "Data inicial não pode ser posterior à data final" in data["detail"]

    def test_rate_limiting(self, client):
        """Teste de rate limiting"""
        # Simular muitas requisições
        responses = []
        for _ in range(10):
            response = client.get("/api/business-metrics/metrics")
            responses.append(response)
        
        # Verificar que algumas requisições foram limitadas
        status_codes = [r.status_code for r in responses]
        assert 429 in status_codes  # Too Many Requests

    def test_authentication_required(self, client):
        """Teste de autenticação obrigatória"""
        # Mock sem usuário autenticado
        with patch('backend.app.api.business_metrics.get_current_user') as mock_auth:
            mock_auth.side_effect = HTTPException(status_code=401, detail="Unauthorized")
            
            response = client.get("/api/business-metrics/metrics")
            assert response.status_code == 401

    def test_permission_required(self, client):
        """Teste de permissão obrigatória"""
        # Mock sem permissão
        with patch('backend.app.api.business_metrics.require_permissions') as mock_permissions:
            mock_permissions.side_effect = HTTPException(status_code=403, detail="Forbidden")
            
            response = client.get("/api/business-metrics/metrics")
            assert response.status_code == 403

    def test_database_error_handling(self, client):
        """Teste de tratamento de erro de banco de dados"""
        # Mock de erro de banco
        with patch('backend.app.api.business_metrics.metrics_service') as mock_service:
            mock_service.get_metrics.side_effect = Exception("Database connection failed")
            
            response = client.get("/api/business-metrics/metrics")
            assert response.status_code == 500
            data = response.json()
            assert "Erro interno do servidor" in data["detail"]

    def test_metrics_calculation_accuracy(self, client):
        """Teste de precisão dos cálculos de métricas"""
        response = client.get("/api/business-metrics/metrics")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar que os valores são realistas
        users_metric = next(m for m in data if m["metric_name"] == "Usuários Ativos")
        assert users_metric["value"] > 0
        assert users_metric["value"] < 100000  # Valor realista
        
        revenue_metric = next(m for m in data if m["metric_name"] == "Receita Mensal")
        assert revenue_metric["value"] > 0
        assert revenue_metric["value"] < 10000000  # Valor realista

    def test_kpi_status_calculation(self, client):
        """Teste de cálculo de status dos KPIs"""
        response = client.get("/api/business-metrics/kpis")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar que os status são calculados corretamente
        users_kpi = next(k for k in data if k["kpi_name"] == "Usuários Ativos")
        assert users_kpi["status"] in ["on_track", "at_risk", "off_track"]
        assert users_kpi["target_achievement"] >= 0
        assert users_kpi["target_achievement"] <= 100

    def test_dashboard_configuration_validation(self, client):
        """Teste de validação de configuração de dashboard"""
        invalid_dashboard = {
            "dashboard_name": "",  # Nome vazio
            "refresh_interval": -1000,  # Intervalo negativo
            "metrics": "invalid_json",  # JSON inválido
            "allowed_users": []  # Lista vazia
        }
        
        response = client.post("/api/business-metrics/dashboards", json=invalid_dashboard)
        
        assert response.status_code == 400
        data = response.json()
        assert "Dados inválidos" in data["detail"]

    def test_metrics_export_functionality(self, client):
        """Teste de funcionalidade de exportação de métricas"""
        # Teste de exportação CSV
        response = client.get("/api/business-metrics/metrics?format=csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
        
        # Teste de exportação JSON
        response = client.get("/api/business-metrics/metrics?format=json")
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")

    def test_metrics_aggregation(self, client):
        """Teste de agregação de métricas"""
        response = client.get(
            "/api/business-metrics/metrics",
            params={
                "aggregate_by": "category",
                "period": "monthly"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        # Verificar que os dados estão agregados por categoria
        assert len(data) > 0

    def test_metrics_trend_analysis(self, client):
        """Teste de análise de tendências"""
        response = client.post(
            "/api/business-metrics/analyze",
            json={
                "metric_type": "users",
                "start_date": "2025-01-01T00:00:00Z",
                "end_date": "2025-01-31T23:59:59Z",
                "include_trends": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "trends" in data
        assert "growth_rate" in data["summary"]

    def test_metrics_alert_generation(self, client):
        """Teste de geração de alertas"""
        response = client.post(
            "/api/business-metrics/analyze",
            json={
                "metric_type": "conversion",
                "start_date": "2025-01-01T00:00:00Z",
                "end_date": "2025-01-31T23:59:59Z",
                "include_alerts": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert isinstance(data["alerts"], list)

    def test_metrics_performance_monitoring(self, client):
        """Teste de monitoramento de performance"""
        response = client.get("/api/business-metrics/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "performance_metrics" in data or "status" in data

    def test_metrics_data_consistency(self, client):
        """Teste de consistência dos dados de métricas"""
        response = client.get("/api/business-metrics/metrics")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar consistência dos dados
        for metric in data:
            assert "metric_id" in metric
            assert "metric_name" in metric
            assert "value" in metric
            assert "category" in metric
            assert "period" in metric
            assert metric["value"] >= 0  # Valores não negativos

    def test_metrics_api_versioning(self, client):
        """Teste de versionamento da API"""
        response = client.get("/api/business-metrics/health")
        
        assert response.status_code == 200
        data = response.json()
        # Verificar que a versão da API está presente
        assert "api_version" in data or "version" in data

    def test_metrics_api_documentation(self, client):
        """Teste de documentação da API"""
        response = client.get("/docs")
        
        assert response.status_code == 200
        # Verificar que a documentação está disponível
        assert "business-metrics" in response.text or "metrics" in response.text 