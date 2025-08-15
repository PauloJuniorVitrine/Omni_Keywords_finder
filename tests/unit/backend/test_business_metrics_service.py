"""
Testes unitários para BusinessMetricsService
⚠️ CRIAR MAS NÃO EXECUTAR - Executar apenas na Fase 6.5

Prompt: CHECKLIST_TESTES_UNITARIOS.md - Item 1.3
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Versão: 1.0.0
"""

import pytest
import tempfile
import os
import json
import sqlite3
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

from backend.app.services.business_metrics_service import (
    BusinessMetricsService,
    MetricCalculation
)
from backend.app.schemas.business_metrics_schemas import (
    BusinessMetric,
    MetricFilterSchema,
    MetricAnalysisSchema,
    KPISchema,
    DashboardSchema,
    MetricType,
    MetricPeriod,
    MetricCategory
)

class TestBusinessMetricsService:
    """Testes para BusinessMetricsService baseados no código real."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Fixture para banco de dados temporário."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            temp_path = f.name
        
        yield temp_path
        
        # Limpeza
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def service(self, temp_db_path):
        """Fixture para serviço com banco temporário."""
        return BusinessMetricsService(temp_db_path)
    
    @pytest.fixture
    def sample_metric(self):
        """Fixture para métrica real."""
        return BusinessMetric(
            metric_id="metric_123",
            metric_type="revenue",
            metric_name="Receita Mensal",
            category="financial",
            value=15000.0,
            previous_value=12000.0,
            target_value=20000.0,
            period="monthly",
            start_date=datetime.now(timezone.utc) - timedelta(days=30),
            end_date=datetime.now(timezone.utc),
            user_id="user_123",
            plan_type="premium",
            region="brasil",
            source="api",
            version="1.0",
            environment="production"
        )
    
    @pytest.fixture
    def sample_kpi(self):
        """Fixture para KPI real."""
        return KPISchema(
            kpi_id="kpi_123",
            kpi_name="Taxa de Conversão",
            description="Taxa de conversão de leads em clientes",
            current_value=15.5,
            target_value=20.0,
            previous_value=12.0,
            percentage_change=29.17,
            target_achievement=77.5,
            status="warning",
            period="monthly",
            last_updated=datetime.now(timezone.utc),
            category="customer",
            priority="high",
            owner="marketing_team"
        )
    
    @pytest.fixture
    def sample_dashboard(self):
        """Fixture para dashboard real."""
        return DashboardSchema(
            dashboard_id="dashboard_123",
            dashboard_name="Dashboard Executivo",
            description="Visão geral das métricas de negócio",
            layout={"widgets": [{"type": "chart", "position": "top"}]},
            refresh_interval=300,
            auto_refresh=True,
            metrics=["metric_123", "metric_456"],
            kpis=["kpi_123"],
            is_public=False,
            allowed_users=["user_123", "user_456"],
            allowed_roles=["admin", "manager"],
            created_by="user_123"
        )
    
    def test_init_service(self, temp_db_path):
        """Testa inicialização do serviço."""
        service = BusinessMetricsService(temp_db_path)
        
        assert service.db_path == temp_db_path
        assert service.db is not None
        assert service.logger is not None
        
        # Verificar se banco foi criado
        assert os.path.exists(temp_db_path)
    
    def test_setup_database_creates_tables(self, temp_db_path):
        """Testa criação das tabelas no banco de dados."""
        service = BusinessMetricsService(temp_db_path)
        
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        # Verificar se tabelas existem
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'business_metrics' in tables
        assert 'kpis' in tables
        assert 'dashboards' in tables
        
        # Verificar se índices existem
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in cursor.fetchall()]
        
        assert 'idx_metric_type' in indexes
        assert 'idx_category' in indexes
        assert 'idx_period' in indexes
        assert 'idx_user_id' in indexes
        assert 'idx_plan_type' in indexes
        assert 'idx_start_date' in indexes
        assert 'idx_end_date' in indexes
        
        conn.close()
    
    def test_record_metric_sucesso(self, service, sample_metric):
        """Testa registro de métrica com sucesso."""
        metric_id = service.record_metric(sample_metric)
        
        assert metric_id == "metric_123"
        
        # Verificar se foi salva no banco
        cursor = service.db.cursor()
        cursor.execute("SELECT metric_id, metric_name, value FROM business_metrics WHERE metric_id = ?", (metric_id,))
        row = cursor.fetchone()
        
        assert row is not None
        assert row[0] == "metric_123"
        assert row[1] == "Receita Mensal"
        assert row[2] == 15000.0
    
    def test_record_metric_com_dados_completos(self, service):
        """Testa registro de métrica com dados completos."""
        metric = BusinessMetric(
            metric_id="metric_completo",
            metric_type="users",
            metric_name="Usuários Ativos",
            category="customer",
            value=1250,
            previous_value=1100,
            target_value=1500,
            period="daily",
            start_date=datetime.now(timezone.utc) - timedelta(days=1),
            end_date=datetime.now(timezone.utc),
            user_id="user_456",
            plan_type="basic",
            region="brasil",
            source="analytics",
            version="1.0",
            environment="production"
        )
        
        metric_id = service.record_metric(metric)
        
        # Verificar dados salvos
        cursor = service.db.cursor()
        cursor.execute("SELECT * FROM business_metrics WHERE metric_id = ?", (metric_id,))
        row = cursor.fetchone()
        
        assert row is not None
        assert row[1] == "users"  # metric_type
        assert row[2] == "Usuários Ativos"  # metric_name
        assert row[3] == "customer"  # category
        assert row[4] == 1250  # value
        assert row[5] == 1100  # previous_value
        assert row[6] == 1500  # target_value
        assert row[7] == "daily"  # period
        assert row[10] == "user_456"  # user_id
        assert row[11] == "basic"  # plan_type
        assert row[12] == "brasil"  # region
        assert row[13] == "analytics"  # source
    
    def test_get_metrics_sem_filtros(self, service, sample_metric):
        """Testa obtenção de métricas sem filtros."""
        # Registrar métrica
        service.record_metric(sample_metric)
        
        # Obter métricas
        filters = MetricFilterSchema()
        metrics = service.get_metrics(filters)
        
        assert len(metrics) == 1
        metric = metrics[0]
        assert metric['metric_id'] == "metric_123"
        assert metric['metric_name'] == "Receita Mensal"
        assert metric['value'] == 15000.0
        assert metric['category'] == "financial"
    
    def test_get_metrics_com_filtros(self, service, sample_metric):
        """Testa obtenção de métricas com filtros."""
        # Registrar métrica
        service.record_metric(sample_metric)
        
        # Criar segunda métrica
        metric2 = BusinessMetric(
            metric_id="metric_456",
            metric_type="executions",
            metric_name="Execuções Diárias",
            category="operational",
            value=500,
            period="daily",
            start_date=datetime.now(timezone.utc) - timedelta(days=1),
            end_date=datetime.now(timezone.utc),
            user_id="user_789",
            plan_type="free",
            region="brasil"
        )
        service.record_metric(metric2)
        
        # Filtrar por tipo
        filters = MetricFilterSchema(metric_types=["revenue"])
        metrics = service.get_metrics(filters)
        assert len(metrics) == 1
        assert metrics[0]['metric_type'] == "revenue"
        
        # Filtrar por categoria
        filters = MetricFilterSchema(categories=["operational"])
        metrics = service.get_metrics(filters)
        assert len(metrics) == 1
        assert metrics[0]['category'] == "operational"
        
        # Filtrar por usuário
        filters = MetricFilterSchema(user_id="user_123")
        metrics = service.get_metrics(filters)
        assert len(metrics) == 1
        assert metrics[0]['user_id'] == "user_123"
        
        # Filtrar por plano
        filters = MetricFilterSchema(plan_type="premium")
        metrics = service.get_metrics(filters)
        assert len(metrics) == 1
        assert metrics[0]['plan_type'] == "premium"
    
    def test_get_metrics_com_paginacao(self, service):
        """Testa obtenção de métricas com paginação."""
        # Criar múltiplas métricas
        for i in range(5):
            metric = BusinessMetric(
                metric_id=f"metric_{i}",
                metric_type="revenue",
                metric_name=f"Receita {i}",
                category="financial",
                value=1000 + i * 100,
                period="daily",
                start_date=datetime.now(timezone.utc) - timedelta(days=i),
                end_date=datetime.now(timezone.utc) - timedelta(days=i-1) if i > 0 else datetime.now(timezone.utc)
            )
            service.record_metric(metric)
        
        # Testar limite
        filters = MetricFilterSchema(limit=3)
        metrics = service.get_metrics(filters)
        assert len(metrics) == 3
        
        # Testar offset
        filters = MetricFilterSchema(limit=2, offset=2)
        metrics = service.get_metrics(filters)
        assert len(metrics) == 2
    
    def test_analyze_metrics_com_dados(self, service, sample_metric):
        """Testa análise de métricas com dados."""
        # Registrar métrica
        service.record_metric(sample_metric)
        
        # Criar métricas adicionais para análise
        for i in range(4):
            metric = BusinessMetric(
                metric_id=f"metric_analise_{i}",
                metric_type="revenue",
                metric_name=f"Receita {i}",
                category="financial",
                value=10000 + i * 1000,
                period="monthly",
                start_date=datetime.now(timezone.utc) - timedelta(days=30*(i+1)),
                end_date=datetime.now(timezone.utc) - timedelta(days=30*i) if i > 0 else datetime.now(timezone.utc),
                plan_type="premium" if i % 2 == 0 else "basic",
                region="brasil"
            )
            service.record_metric(metric)
        
        # Analisar métricas
        start_date = datetime.now(timezone.utc) - timedelta(days=120)
        end_date = datetime.now(timezone.utc)
        
        analysis = service.analyze_metrics("revenue", start_date, end_date)
        
        assert analysis.analysis_id is not None
        assert analysis.metric_type == "revenue"
        assert analysis.period_start == start_date
        assert analysis.period_end == end_date
        assert analysis.total_records == 5
        assert analysis.average_value > 0
        assert analysis.min_value > 0
        assert analysis.max_value > 0
        assert analysis.median_value > 0
        assert analysis.growth_rate is not None
        assert analysis.trend_direction in ["up", "down", "stable", "volatile"]
        assert analysis.trend_strength in ["strong", "moderate", "weak", "none"]
        assert len(analysis.insights) > 0
        assert len(analysis.recommendations) > 0
        assert isinstance(analysis.by_plan_type, dict)
        assert isinstance(analysis.by_region, dict)
    
    def test_analyze_metrics_sem_dados(self, service):
        """Testa análise de métricas sem dados."""
        start_date = datetime.now(timezone.utc) - timedelta(days=30)
        end_date = datetime.now(timezone.utc)
        
        analysis = service.analyze_metrics("revenue", start_date, end_date)
        
        assert analysis.analysis_id is not None
        assert analysis.metric_type == "revenue"
        assert analysis.total_records == 0
        assert analysis.average_value == 0.0
        assert analysis.min_value == 0.0
        assert analysis.max_value == 0.0
        assert analysis.median_value == 0.0
        assert analysis.growth_rate == 0.0
        assert analysis.trend_direction == "stable"
        assert analysis.trend_strength == "none"
        assert "Nenhum dado disponível" in analysis.insights[0]
        assert "Coletar mais dados" in analysis.recommendations[0]
    
    def test_calculate_growth_rate(self, service):
        """Testa cálculo de taxa de crescimento."""
        # Criar métricas com crescimento
        metrics = [
            {
                'start_date': '2025-01-01T00:00:00',
                'value': 1000.0
            },
            {
                'start_date': '2025-01-02T00:00:00',
                'value': 1200.0
            },
            {
                'start_date': '2025-01-03T00:00:00',
                'value': 1500.0
            }
        ]
        
        growth_rate = service._calculate_growth_rate(metrics)
        assert growth_rate == 50.0  # (1500 - 1000) / 1000 * 100
    
    def test_calculate_growth_rate_declinio(self, service):
        """Testa cálculo de taxa de crescimento com declínio."""
        metrics = [
            {
                'start_date': '2025-01-01T00:00:00',
                'value': 2000.0
            },
            {
                'start_date': '2025-01-02T00:00:00',
                'value': 1500.0
            }
        ]
        
        growth_rate = service._calculate_growth_rate(metrics)
        assert growth_rate == -25.0  # (1500 - 2000) / 2000 * 100
    
    def test_determine_trend_direction(self, service):
        """Testa determinação da direção da tendência."""
        # Tendência crescente
        values_up = [100, 120, 150, 180, 200]
        direction = service._determine_trend_direction(values_up)
        assert direction == "up"
        
        # Tendência decrescente
        values_down = [200, 180, 150, 120, 100]
        direction = service._determine_trend_direction(values_down)
        assert direction == "down"
        
        # Tendência estável
        values_stable = [100, 102, 98, 101, 99]
        direction = service._determine_trend_direction(values_stable)
        assert direction == "stable"
    
    def test_determine_trend_strength(self, service):
        """Testa determinação da força da tendência."""
        # Tendência forte (baixa variação)
        values_strong = [100, 101, 99, 100, 101]
        strength = service._determine_trend_strength(values_strong)
        assert strength == "strong"
        
        # Tendência moderada
        values_moderate = [100, 110, 90, 105, 95]
        strength = service._determine_trend_strength(values_moderate)
        assert strength == "moderate"
        
        # Tendência fraca (alta variação)
        values_weak = [100, 150, 50, 200, 25]
        strength = service._determine_trend_strength(values_weak)
        assert strength == "weak"
    
    def test_calculate_correlation(self, service):
        """Testa cálculo de correlação."""
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]  # Correlação perfeita positiva
        
        correlation = service._calculate_correlation(x, y)
        assert correlation == pytest.approx(1.0, abs=0.01)
        
        # Correlação negativa
        y_neg = [10, 8, 6, 4, 2]
        correlation = service._calculate_correlation(x, y_neg)
        assert correlation == pytest.approx(-1.0, abs=0.01)
    
    def test_analyze_by_segment(self, service):
        """Testa análise por segmento."""
        metrics = [
            {'plan_type': 'premium', 'value': 1000.0},
            {'plan_type': 'premium', 'value': 1200.0},
            {'plan_type': 'basic', 'value': 500.0},
            {'plan_type': 'basic', 'value': 600.0},
            {'plan_type': 'free', 'value': 100.0}
        ]
        
        by_plan = service._analyze_by_segment(metrics, 'plan_type')
        
        assert by_plan['premium'] == 1100.0  # (1000 + 1200) / 2
        assert by_plan['basic'] == 550.0  # (500 + 600) / 2
        assert by_plan['free'] == 100.0
    
    def test_generate_insights(self, service):
        """Testa geração de insights."""
        metrics = [{'value': 1000.0} for _ in range(50)]
        values = [1000.0 for _ in range(50)]
        
        # Crescimento forte
        insights = service._generate_insights(metrics, values, 25.0, "up")
        assert any("Crescimento forte" in insight for insight in insights)
        assert any("Tendência de crescimento" in insight for insight in insights)
        
        # Volume significativo
        insights = service._generate_insights(metrics, values, 5.0, "stable")
        assert any("Volume significativo" in insight for insight in insights)
    
    def test_generate_recommendations(self, service):
        """Testa geração de recomendações."""
        metrics = [{'value': 1000.0} for _ in range(10)]
        values = [1000.0 for _ in range(10)]
        
        # Declínio significativo
        recommendations = service._generate_recommendations(metrics, values, -15.0, "down")
        assert any("Investigar causas do declínio" in rec for rec in recommendations)
        
        # Crescimento anômalo
        recommendations = service._generate_recommendations(metrics, values, 60.0, "up")
        assert any("Avaliar se o crescimento é sustentável" in rec for rec in recommendations)
        
        # Volume baixo
        recommendations = service._generate_recommendations(metrics, values, 5.0, "stable")
        assert any("Aumentar frequência de coleta" in rec for rec in recommendations)
    
    def test_generate_alerts(self, service):
        """Testa geração de alertas."""
        metrics = [{'value': 1000.0} for _ in range(10)]
        values = [1000.0 for _ in range(10)]
        
        # Declínio crítico
        alerts = service._generate_alerts(metrics, values, -35.0, "down")
        assert any("ALERTA: Declínio crítico" in alert for alert in alerts)
        
        # Crescimento anômalo
        alerts = service._generate_alerts(metrics, values, 150.0, "up")
        assert any("ALERTA: Crescimento anômalo" in alert for alert in alerts)
    
    def test_create_kpi_sucesso(self, service, sample_kpi):
        """Testa criação de KPI com sucesso."""
        kpi_id = service.create_kpi(sample_kpi)
        
        assert kpi_id == "kpi_123"
        
        # Verificar se foi salvo no banco
        cursor = service.db.cursor()
        cursor.execute("SELECT kpi_id, kpi_name, current_value FROM kpis WHERE kpi_id = ?", (kpi_id,))
        row = cursor.fetchone()
        
        assert row is not None
        assert row[0] == "kpi_123"
        assert row[1] == "Taxa de Conversão"
        assert row[2] == 15.5
    
    def test_get_kpis(self, service, sample_kpi):
        """Testa obtenção de KPIs."""
        # Criar KPI
        service.create_kpi(sample_kpi)
        
        # Obter KPIs
        kpis = service.get_kpis()
        
        assert len(kpis) == 1
        kpi = kpis[0]
        assert kpi['kpi_id'] == "kpi_123"
        assert kpi['kpi_name'] == "Taxa de Conversão"
        assert kpi['current_value'] == 15.5
        assert kpi['target_value'] == 20.0
        assert kpi['status'] == "warning"
        assert kpi['priority'] == "high"
    
    def test_update_kpi(self, service, sample_kpi):
        """Testa atualização de KPI."""
        # Criar KPI
        service.create_kpi(sample_kpi)
        
        # Atualizar KPI
        updates = {
            'current_value': 18.0,
            'percentage_change': 50.0,
            'target_achievement': 90.0,
            'status': 'success'
        }
        
        sucesso = service.update_kpi("kpi_123", updates)
        assert sucesso is True
        
        # Verificar atualização
        kpis = service.get_kpis()
        kpi = kpis[0]
        assert kpi['current_value'] == 18.0
        assert kpi['percentage_change'] == 50.0
        assert kpi['target_achievement'] == 90.0
        assert kpi['status'] == "success"
    
    def test_update_kpi_inexistente(self, service):
        """Testa atualização de KPI inexistente."""
        updates = {'current_value': 20.0}
        sucesso = service.update_kpi("kpi_inexistente", updates)
        assert sucesso is False
    
    def test_create_dashboard_sucesso(self, service, sample_dashboard):
        """Testa criação de dashboard com sucesso."""
        dashboard_id = service.create_dashboard(sample_dashboard)
        
        assert dashboard_id == "dashboard_123"
        
        # Verificar se foi salvo no banco
        cursor = service.db.cursor()
        cursor.execute("SELECT dashboard_id, dashboard_name FROM dashboards WHERE dashboard_id = ?", (dashboard_id,))
        row = cursor.fetchone()
        
        assert row is not None
        assert row[0] == "dashboard_123"
        assert row[1] == "Dashboard Executivo"
    
    def test_get_dashboards_publicos(self, service, sample_dashboard):
        """Testa obtenção de dashboards públicos."""
        # Criar dashboard público
        sample_dashboard.is_public = True
        service.create_dashboard(sample_dashboard)
        
        # Obter dashboards
        dashboards = service.get_dashboards()
        
        assert len(dashboards) == 1
        dashboard = dashboards[0]
        assert dashboard['dashboard_id'] == "dashboard_123"
        assert dashboard['dashboard_name'] == "Dashboard Executivo"
        assert dashboard['is_public'] is True
        assert dashboard['refresh_interval'] == 300
        assert dashboard['auto_refresh'] is True
    
    def test_get_dashboards_por_usuario(self, service, sample_dashboard):
        """Testa obtenção de dashboards por usuário."""
        # Criar dashboard privado
        sample_dashboard.is_public = False
        sample_dashboard.allowed_users = ["user_123", "user_456"]
        service.create_dashboard(sample_dashboard)
        
        # Obter dashboards para usuário permitido
        dashboards = service.get_dashboards("user_123")
        assert len(dashboards) == 1
        
        # Obter dashboards para usuário não permitido
        dashboards = service.get_dashboards("user_999")
        assert len(dashboards) == 0
    
    def test_close_connection(self, service):
        """Testa fechamento da conexão."""
        service.close()
        
        # Tentar executar query após fechar
        with pytest.raises(Exception):
            cursor = service.db.cursor()
            cursor.execute("SELECT 1") 