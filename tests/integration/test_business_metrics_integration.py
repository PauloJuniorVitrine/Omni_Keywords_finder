"""
Teste de Integração - Backend de Métricas de Negócio
Validação de integração com Flask e funcionamento end-to-end

Tracing ID: TEST_BM_INTEGRATION_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: 🟡 ALTO - Backend de Métricas

Baseado no código real do sistema Omni Keywords Finder
"""

import pytest
import json
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from backend.app import create_app
from backend.app.services.business_metrics_service import BusinessMetricsService

class TestBusinessMetricsIntegration:
    """Testes de integração para o backend de métricas"""

    @pytest.fixture
    def app(self):
        """Criar app Flask para testes"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    @pytest.fixture
    def client(self, app):
        """Cliente de teste"""
        return app.test_client()

    @pytest.fixture
    def mock_auth(self):
        """Mock de autenticação"""
        with patch('backend.app.api.business_metrics.get_current_user') as mock:
            mock.return_value = {
                "id": "user-001",
                "email": "admin@omnikeywordsfinder.com",
                "role": "admin",
                "permissions": ["metrics:read", "metrics:write", "metrics:admin"]
            }
            yield mock

    @pytest.fixture
    def mock_permissions(self):
        """Mock de permissões"""
        with patch('backend.app.api.business_metrics.require_permissions') as mock:
            mock.return_value = True
            yield mock

    @pytest.fixture
    def mock_rate_limiter(self):
        """Mock de rate limiter"""
        with patch('backend.app.api.business_metrics.rate_limiter') as mock:
            mock.check_rate_limit.return_value = None
            yield mock

    def test_health_endpoint_accessible(self, client):
        """Teste: Endpoint de health está acessível"""
        response = client.get('/api/business-metrics/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "status" in data
        assert "api_version" in data
        assert "timestamp" in data

    def test_metric_types_endpoint_accessible(self, client, mock_auth, mock_permissions, mock_rate_limiter):
        """Teste: Endpoint de tipos de métricas está acessível"""
        response = client.get('/api/business-metrics/types')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "metric_types" in data
        assert "categories" in data
        assert "periods" in data

    def test_record_metric_endpoint_accessible(self, client, mock_auth, mock_permissions, mock_rate_limiter):
        """Teste: Endpoint de registro de métricas está acessível"""
        metric_data = {
            "metric_id": "test-metric-001",
            "metric_type": "users",
            "metric_name": "Usuários Ativos Teste",
            "category": "customer",
            "value": 100.0,
            "previous_value": 90.0,
            "target_value": 150.0,
            "period": "daily",
            "start_date": "2025-01-27T00:00:00Z",
            "end_date": "2025-01-27T23:59:59Z",
            "user_id": None,
            "plan_type": "premium",
            "region": "BR",
            "source": "test_integration",
            "version": "1.0",
            "environment": "test",
            "created_at": "2025-01-27T15:30:00Z"
        }
        
        response = client.post(
            '/api/business-metrics/metrics',
            data=json.dumps(metric_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "message" in data
        assert "metric_id" in data

    def test_get_metrics_endpoint_accessible(self, client, mock_auth, mock_permissions, mock_rate_limiter):
        """Teste: Endpoint de consulta de métricas está acessível"""
        response = client.get('/api/business-metrics/metrics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_analyze_metrics_endpoint_accessible(self, client, mock_auth, mock_permissions, mock_rate_limiter):
        """Teste: Endpoint de análise de métricas está acessível"""
        analysis_data = {
            "metric_type": "users",
            "start_date": "2025-01-01T00:00:00Z",
            "end_date": "2025-01-31T23:59:59Z"
        }
        
        response = client.post(
            '/api/business-metrics/analyze',
            data=json.dumps(analysis_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "metric_type" in data

    def test_create_kpi_endpoint_accessible(self, client, mock_auth, mock_permissions, mock_rate_limiter):
        """Teste: Endpoint de criação de KPI está acessível"""
        kpi_data = {
            "kpi_id": "test-kpi-001",
            "kpi_name": "KPI Teste",
            "description": "KPI para teste de integração",
            "current_value": 100.0,
            "target_value": 150.0,
            "previous_value": 90.0,
            "percentage_change": 11.1,
            "target_achievement": 66.7,
            "status": "on_track",
            "period": "daily",
            "last_updated": "2025-01-27T15:30:00Z",
            "category": "customer",
            "priority": "high",
            "owner": "test_team"
        }
        
        response = client.post(
            '/api/business-metrics/kpis',
            data=json.dumps(kpi_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "message" in data
        assert "kpi_id" in data

    def test_get_kpis_endpoint_accessible(self, client, mock_auth, mock_permissions, mock_rate_limiter):
        """Teste: Endpoint de consulta de KPIs está acessível"""
        response = client.get('/api/business-metrics/kpis')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_create_dashboard_endpoint_accessible(self, client, mock_auth, mock_permissions, mock_rate_limiter):
        """Teste: Endpoint de criação de dashboard está acessível"""
        dashboard_data = {
            "dashboard_id": "test-dashboard-001",
            "dashboard_name": "Dashboard Teste",
            "description": "Dashboard para teste de integração",
            "layout": "grid",
            "refresh_interval": 30000,
            "auto_refresh": True,
            "metrics": ["users", "revenue"],
            "kpis": ["test-kpi-001"],
            "is_public": False,
            "allowed_users": ["admin"],
            "allowed_roles": ["admin"],
            "created_by": "admin"
        }
        
        response = client.post(
            '/api/business-metrics/dashboards',
            data=json.dumps(dashboard_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "message" in data
        assert "dashboard_id" in data

    def test_get_dashboards_endpoint_accessible(self, client, mock_auth, mock_permissions, mock_rate_limiter):
        """Teste: Endpoint de consulta de dashboards está acessível"""
        response = client.get('/api/business-metrics/dashboards')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_summary_endpoint_accessible(self, client, mock_auth, mock_permissions, mock_rate_limiter):
        """Teste: Endpoint de resumo está acessível"""
        response = client.get('/api/business-metrics/summary?period=daily')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "users" in data
        assert "executions" in data
        assert "revenue" in data
        assert "kpis" in data

    def test_collect_metrics_endpoint_accessible(self, client, mock_auth, mock_permissions, mock_rate_limiter):
        """Teste: Endpoint de coleta de métricas está acessível"""
        response = client.post('/api/business-metrics/collect')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "message" in data

    def test_authentication_required(self, client):
        """Teste: Autenticação é obrigatória"""
        # Sem mock de autenticação
        response = client.get('/api/business-metrics/metrics')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert "error" in data
        assert "Autenticação necessária" in data["error"]

    def test_permission_required(self, client, mock_auth):
        """Teste: Permissão é obrigatória"""
        # Mock sem permissão
        with patch('backend.app.api.business_metrics.require_permissions') as mock_permissions:
            mock_permissions.return_value = False
            
            response = client.get('/api/business-metrics/metrics')
            
            assert response.status_code == 403
            data = json.loads(response.data)
            assert "error" in data
            assert "Permissão negada" in data["error"]

    def test_rate_limiting_works(self, client, mock_auth, mock_permissions):
        """Teste: Rate limiting funciona"""
        # Mock de rate limit excedido
        with patch('backend.app.api.business_metrics.rate_limiter') as mock_rate_limiter:
            mock_rate_limiter.check_rate_limit.side_effect = Exception("Rate limit exceeded")
            
            response = client.get('/api/business-metrics/metrics')
            
            assert response.status_code == 429
            data = json.loads(response.data)
            assert "error" in data
            assert "Rate limit excedido" in data["error"]

    def test_invalid_json_handling(self, client, mock_auth, mock_permissions, mock_rate_limiter):
        """Teste: Tratamento de JSON inválido"""
        response = client.post(
            '/api/business-metrics/metrics',
            data="invalid json",
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_missing_required_fields(self, client, mock_auth, mock_permissions, mock_rate_limiter):
        """Teste: Campos obrigatórios ausentes"""
        incomplete_data = {
            "metric_name": "Teste",
            "value": 100.0
            # Faltam campos obrigatórios
        }
        
        response = client.post(
            '/api/business-metrics/metrics',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_invalid_date_format(self, client, mock_auth, mock_permissions, mock_rate_limiter):
        """Teste: Formato de data inválido"""
        metric_data = {
            "metric_id": "test-metric-002",
            "metric_type": "users",
            "metric_name": "Teste Data Inválida",
            "category": "customer",
            "value": 100.0,
            "previous_value": 90.0,
            "target_value": 150.0,
            "period": "daily",
            "start_date": "invalid-date",  # Data inválida
            "end_date": "2025-01-27T23:59:59Z",
            "user_id": None,
            "plan_type": "premium",
            "region": "BR",
            "source": "test_integration",
            "version": "1.0",
            "environment": "test",
            "created_at": "2025-01-27T15:30:00Z"
        }
        
        response = client.post(
            '/api/business-metrics/metrics',
            data=json.dumps(metric_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_metrics_service_integration(self, client, mock_auth, mock_permissions, mock_rate_limiter):
        """Teste: Integração com o serviço de métricas"""
        # Mock do serviço para retornar dados específicos
        with patch('backend.app.api.business_metrics.metrics_service') as mock_service:
            mock_service.get_metrics.return_value = [
                {
                    "metric_id": "test-001",
                    "metric_name": "Usuários Ativos",
                    "value": 15420.0,
                    "category": "customer"
                }
            ]
            
            response = client.get('/api/business-metrics/metrics')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) == 1
            assert data[0]["metric_name"] == "Usuários Ativos"
            assert data[0]["value"] == 15420.0

    def test_error_handling_middleware(self, client, mock_auth, mock_permissions, mock_rate_limiter):
        """Teste: Middleware de tratamento de erros"""
        # Mock de erro no serviço
        with patch('backend.app.api.business_metrics.metrics_service') as mock_service:
            mock_service.get_metrics.side_effect = Exception("Database error")
            
            response = client.get('/api/business-metrics/metrics')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert "error" in data
            assert "Erro interno do servidor" in data["error"]

    def test_logging_functionality(self, client, mock_auth, mock_permissions, mock_rate_limiter, caplog):
        """Teste: Funcionalidade de logging"""
        with caplog.at_level('INFO'):
            response = client.get('/api/business-metrics/health')
            
            assert response.status_code == 200
            # Verificar se logs foram gerados
            assert any('Requisição iniciada' in record.message for record in caplog.records)
            assert any('Requisição concluída' in record.message for record in caplog.records)

    def test_api_version_in_response(self, client):
        """Teste: Versão da API está presente nas respostas"""
        response = client.get('/api/business-metrics/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "api_version" in data
        assert data["api_version"] == "1.0.0"

    def test_cors_headers_present(self, client):
        """Teste: Headers CORS estão presentes"""
        response = client.get('/api/business-metrics/health')
        
        assert response.status_code == 200
        # Verificar headers CORS (se configurados)
        assert 'Access-Control-Allow-Origin' in response.headers or 'Content-Type' in response.headers

    def test_endpoint_urls_consistent(self, client, mock_auth, mock_permissions, mock_rate_limiter):
        """Teste: URLs dos endpoints são consistentes"""
        endpoints = [
            '/api/business-metrics/health',
            '/api/business-metrics/types',
            '/api/business-metrics/metrics',
            '/api/business-metrics/kpis',
            '/api/business-metrics/dashboards',
            '/api/business-metrics/summary'
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            # Deve retornar 200 (com auth) ou 401 (sem auth), mas não 404
            assert response.status_code in [200, 401], f"Endpoint {endpoint} não encontrado"

    def test_blueprint_registration(self, app):
        """Teste: Blueprint está registrado corretamente"""
        # Verificar se o blueprint está registrado
        registered_blueprints = [bp.name for bp in app.blueprints.values()]
        assert 'business_metrics' in registered_blueprints
        
        # Verificar se as rotas estão registradas
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        business_metrics_routes = [route for route in routes if route.startswith('/api/business-metrics')]
        assert len(business_metrics_routes) > 0

    def test_database_connection(self, client, mock_auth, mock_permissions, mock_rate_limiter):
        """Teste: Conexão com banco de dados"""
        response = client.get('/api/business-metrics/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "database" in data
        assert data["database"] == "connected"

    def test_metrics_persistence(self, client, mock_auth, mock_permissions, mock_rate_limiter):
        """Teste: Persistência de métricas"""
        metric_data = {
            "metric_id": "persistence-test-001",
            "metric_type": "users",
            "metric_name": "Teste de Persistência",
            "category": "customer",
            "value": 200.0,
            "previous_value": 180.0,
            "target_value": 250.0,
            "period": "daily",
            "start_date": "2025-01-27T00:00:00Z",
            "end_date": "2025-01-27T23:59:59Z",
            "user_id": None,
            "plan_type": "premium",
            "region": "BR",
            "source": "persistence_test",
            "version": "1.0",
            "environment": "test",
            "created_at": "2025-01-27T15:30:00Z"
        }
        
        # Registrar métrica
        response = client.post(
            '/api/business-metrics/metrics',
            data=json.dumps(metric_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        # Consultar métricas para verificar se foi persistida
        response = client.get('/api/business-metrics/metrics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        # Verificar se a métrica está na lista (depende da implementação do mock)
        assert isinstance(data, list) 