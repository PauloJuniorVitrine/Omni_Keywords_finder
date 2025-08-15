"""
Testes Unitários para Business Metrics Service
Serviço de Métricas de Negócio - Omni Keywords Finder

Prompt: Implementação de testes unitários para serviço de métricas de negócio
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import json
import tempfile
import os
import statistics
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

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


class TestMetricCalculation:
    """Testes para MetricCalculation"""
    
    def test_metric_calculation_creation(self):
        """Testa criação de cálculo de métrica"""
        calculation = MetricCalculation(
            value=100.0,
            previous_value=80.0,
            change_percentage=25.0,
            trend_direction="up",
            trend_strength="strong"
        )
        
        assert calculation.value == 100.0
        assert calculation.previous_value == 80.0
        assert calculation.change_percentage == 25.0
        assert calculation.trend_direction == "up"
        assert calculation.trend_strength == "strong"


class TestBusinessMetricsService:
    """Testes para BusinessMetricsService"""
    
    @pytest.fixture
    def temp_db_path(self):
        """Cria caminho temporário para banco de dados"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        yield db_path
        # Limpar após teste
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def business_metrics_service(self, temp_db_path):
        """Instância do BusinessMetricsService para testes"""
        service = BusinessMetricsService(db_path=temp_db_path)
        yield service
        service.close()
    
    @pytest.fixture
    def sample_metric(self):
        """Métrica de exemplo para testes"""
        return BusinessMetric(
            metric_id="test_metric_123",
            metric_type=MetricType.REVENUE.value,
            metric_name="Receita Mensal",
            category=MetricCategory.FINANCIAL.value,
            value=10000.0,
            previous_value=8000.0,
            target_value=12000.0,
            period=MetricPeriod.MONTHLY.value,
            start_date=datetime.now(timezone.utc) - timedelta(days=30),
            end_date=datetime.now(timezone.utc),
            user_id="user_123",
            plan_type="premium",
            region="BR",
            source="payment_gateway",
            version="1.0",
            environment="production",
            created_at=datetime.now(timezone.utc)
        )
    
    def test_business_metrics_service_initialization(self, temp_db_path):
        """Testa inicialização do BusinessMetricsService"""
        service = BusinessMetricsService(db_path=temp_db_path)
        
        assert service.db_path == temp_db_path
        assert service.db is not None
        
        service.close()
    
    def test_record_metric_success(self, business_metrics_service, sample_metric):
        """Testa registro de métrica com sucesso"""
        metric_id = business_metrics_service.record_metric(sample_metric)
        
        assert metric_id == "test_metric_123"
        
        # Verificar se foi salva no banco
        cursor = business_metrics_service.db.cursor()
        cursor.execute("SELECT * FROM business_metrics WHERE metric_id = ?", [metric_id])
        row = cursor.fetchone()
        
        assert row is not None
        assert row[0] == "test_metric_123"
        assert row[1] == MetricType.REVENUE.value
        assert row[2] == "Receita Mensal"
        assert row[4] == 10000.0
    
    def test_record_metric_error(self, business_metrics_service):
        """Testa registro de métrica com erro"""
        # Métrica inválida (sem metric_id)
        invalid_metric = BusinessMetric(
            metric_id="",  # ID vazio
            metric_type=MetricType.REVENUE.value,
            metric_name="Receita Mensal",
            category=MetricCategory.FINANCIAL.value,
            value=10000.0,
            previous_value=8000.0,
            target_value=12000.0,
            period=MetricPeriod.MONTHLY.value,
            start_date=datetime.now(timezone.utc) - timedelta(days=30),
            end_date=datetime.now(timezone.utc),
            user_id="user_123",
            plan_type="premium",
            region="BR",
            source="payment_gateway",
            version="1.0",
            environment="production",
            created_at=datetime.now(timezone.utc)
        )
        
        with pytest.raises(Exception):
            business_metrics_service.record_metric(invalid_metric)
    
    def test_get_metrics_empty(self, business_metrics_service):
        """Testa obtenção de métricas vazia"""
        filters = MetricFilterSchema()
        metrics = business_metrics_service.get_metrics(filters)
        
        assert metrics == []
    
    def test_get_metrics_with_filters(self, business_metrics_service, sample_metric):
        """Testa obtenção de métricas com filtros"""
        # Registrar métrica
        business_metrics_service.record_metric(sample_metric)
        
        # Filtrar por tipo
        filters = MetricFilterSchema(metric_types=[MetricType.REVENUE.value])
        metrics = business_metrics_service.get_metrics(filters)
        
        assert len(metrics) == 1
        assert metrics[0]["metric_id"] == "test_metric_123"
        assert metrics[0]["metric_type"] == MetricType.REVENUE.value
    
    def test_get_metrics_with_date_filters(self, business_metrics_service, sample_metric):
        """Testa obtenção de métricas com filtros de data"""
        # Registrar métrica
        business_metrics_service.record_metric(sample_metric)
        
        # Filtrar por data
        start_date = datetime.now(timezone.utc) - timedelta(days=60)
        end_date = datetime.now(timezone.utc)
        filters = MetricFilterSchema(start_date=start_date, end_date=end_date)
        metrics = business_metrics_service.get_metrics(filters)
        
        assert len(metrics) == 1
        assert metrics[0]["metric_id"] == "test_metric_123"
    
    def test_analyze_metrics_empty(self, business_metrics_service):
        """Testa análise de métricas vazia"""
        start_date = datetime.now(timezone.utc) - timedelta(days=30)
        end_date = datetime.now(timezone.utc)
        
        analysis = business_metrics_service.analyze_metrics(
            MetricType.REVENUE.value,
            start_date,
            end_date
        )
        
        assert analysis.total_records == 0
        assert analysis.average_value == 0.0
        assert analysis.growth_rate == 0.0
        assert analysis.trend_direction == "stable"
        assert analysis.trend_strength == "none"
        assert "Nenhum dado disponível" in analysis.insights[0]
    
    def test_analyze_metrics_with_data(self, business_metrics_service, sample_metric):
        """Testa análise de métricas com dados"""
        # Registrar métrica
        business_metrics_service.record_metric(sample_metric)
        
        start_date = datetime.now(timezone.utc) - timedelta(days=30)
        end_date = datetime.now(timezone.utc)
        
        analysis = business_metrics_service.analyze_metrics(
            MetricType.REVENUE.value,
            start_date,
            end_date
        )
        
        assert analysis.total_records == 1
        assert analysis.average_value == 10000.0
        assert analysis.min_value == 10000.0
        assert analysis.max_value == 10000.0
        assert analysis.metric_type == MetricType.REVENUE.value
        assert len(analysis.insights) > 0
        assert len(analysis.recommendations) > 0
    
    def test_calculate_growth_rate_positive(self, business_metrics_service):
        """Testa cálculo de taxa de crescimento positiva"""
        metrics = [
            {"start_date": "2025-01-01", "value": 100.0},
            {"start_date": "2025-01-02", "value": 120.0}
        ]
        
        growth_rate = business_metrics_service._calculate_growth_rate(metrics)
        
        assert growth_rate == 20.0  # (120-100)/100 * 100
    
    def test_calculate_growth_rate_negative(self, business_metrics_service):
        """Testa cálculo de taxa de crescimento negativa"""
        metrics = [
            {"start_date": "2025-01-01", "value": 100.0},
            {"start_date": "2025-01-02", "value": 80.0}
        ]
        
        growth_rate = business_metrics_service._calculate_growth_rate(metrics)
        
        assert growth_rate == -20.0  # (80-100)/100 * 100
    
    def test_calculate_growth_rate_zero_initial(self, business_metrics_service):
        """Testa cálculo de taxa de crescimento com valor inicial zero"""
        metrics = [
            {"start_date": "2025-01-01", "value": 0.0},
            {"start_date": "2025-01-02", "value": 100.0}
        ]
        
        growth_rate = business_metrics_service._calculate_growth_rate(metrics)
        
        assert growth_rate == 0.0  # Divisão por zero
    
    def test_determine_trend_direction_up(self, business_metrics_service):
        """Testa determinação de tendência crescente"""
        values = [10.0, 20.0, 30.0, 40.0, 50.0]  # Tendência crescente forte
        
        direction = business_metrics_service._determine_trend_direction(values)
        
        assert direction == "up"
    
    def test_determine_trend_direction_down(self, business_metrics_service):
        """Testa determinação de tendência decrescente"""
        values = [50.0, 40.0, 30.0, 20.0, 10.0]  # Tendência decrescente forte
        
        direction = business_metrics_service._determine_trend_direction(values)
        
        assert direction == "down"
    
    def test_determine_trend_direction_stable(self, business_metrics_service):
        """Testa determinação de tendência estável"""
        values = [10.0, 11.0, 9.0, 10.5, 9.5]  # Tendência estável
        
        direction = business_metrics_service._determine_trend_direction(values)
        
        assert direction == "stable"
    
    def test_determine_trend_strength_strong(self, business_metrics_service):
        """Testa determinação de força de tendência forte"""
        values = [100.0, 101.0, 99.0, 100.5, 99.5]  # Baixa variação
        
        strength = business_metrics_service._determine_trend_strength(values)
        
        assert strength == "strong"
    
    def test_determine_trend_strength_moderate(self, business_metrics_service):
        """Testa determinação de força de tendência moderada"""
        values = [100.0, 110.0, 90.0, 105.0, 95.0]  # Variação moderada
        
        strength = business_metrics_service._determine_trend_strength(values)
        
        assert strength == "moderate"
    
    def test_determine_trend_strength_weak(self, business_metrics_service):
        """Testa determinação de força de tendência fraca"""
        values = [100.0, 150.0, 50.0, 200.0, 25.0]  # Alta variação
        
        strength = business_metrics_service._determine_trend_strength(values)
        
        assert strength == "weak"
    
    def test_calculate_correlation_positive(self, business_metrics_service):
        """Testa cálculo de correlação positiva"""
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]  # Correlação perfeita positiva
        
        correlation = business_metrics_service._calculate_correlation(x, y)
        
        assert correlation == 1.0
    
    def test_calculate_correlation_negative(self, business_metrics_service):
        """Testa cálculo de correlação negativa"""
        x = [1, 2, 3, 4, 5]
        y = [10, 8, 6, 4, 2]  # Correlação perfeita negativa
        
        correlation = business_metrics_service._calculate_correlation(x, y)
        
        assert correlation == -1.0
    
    def test_calculate_correlation_zero(self, business_metrics_service):
        """Testa cálculo de correlação zero"""
        x = [1, 2, 3, 4, 5]
        y = [5, 5, 5, 5, 5]  # Sem correlação
        
        correlation = business_metrics_service._calculate_correlation(x, y)
        
        assert correlation == 0.0
    
    def test_analyze_by_segment(self, business_metrics_service):
        """Testa análise por segmento"""
        metrics = [
            {"plan_type": "premium", "value": 100.0},
            {"plan_type": "premium", "value": 200.0},
            {"plan_type": "basic", "value": 50.0},
            {"plan_type": "basic", "value": 75.0}
        ]
        
        result = business_metrics_service._analyze_by_segment(metrics, "plan_type")
        
        assert result["premium"] == 150.0  # (100+200)/2
        assert result["basic"] == 62.5     # (50+75)/2
    
    def test_generate_insights_strong_growth(self, business_metrics_service):
        """Testa geração de insights com crescimento forte"""
        metrics = [{"value": 100.0}]
        values = [100.0]
        growth_rate = 25.0
        trend_direction = "up"
        
        insights = business_metrics_service._generate_insights(metrics, values, growth_rate, trend_direction)
        
        assert any("Crescimento forte" in insight for insight in insights)
        assert any("Tendência de crescimento" in insight for insight in insights)
    
    def test_generate_insights_decline(self, business_metrics_service):
        """Testa geração de insights com declínio"""
        metrics = [{"value": 100.0}]
        values = [100.0]
        growth_rate = -25.0
        trend_direction = "down"
        
        insights = business_metrics_service._generate_insights(metrics, values, growth_rate, trend_direction)
        
        assert any("Declínio significativo" in insight for insight in insights)
        assert any("Tendência de declínio" in insight for insight in insights)
    
    def test_generate_recommendations_decline(self, business_metrics_service):
        """Testa geração de recomendações para declínio"""
        metrics = [{"value": 100.0}]
        values = [100.0]
        growth_rate = -15.0
        trend_direction = "down"
        
        recommendations = business_metrics_service._generate_recommendations(metrics, values, growth_rate, trend_direction)
        
        assert any("Investigar causas" in rec for rec in recommendations)
    
    def test_generate_recommendations_strong_growth(self, business_metrics_service):
        """Testa geração de recomendações para crescimento forte"""
        metrics = [{"value": 100.0}]
        values = [100.0]
        growth_rate = 60.0
        trend_direction = "up"
        
        recommendations = business_metrics_service._generate_recommendations(metrics, values, growth_rate, trend_direction)
        
        assert any("Avaliar se o crescimento" in rec for rec in recommendations)
    
    def test_generate_alerts_critical_decline(self, business_metrics_service):
        """Testa geração de alertas para declínio crítico"""
        metrics = [{"value": 100.0}]
        values = [100.0]
        growth_rate = -35.0
        trend_direction = "down"
        
        alerts = business_metrics_service._generate_alerts(metrics, values, growth_rate, trend_direction)
        
        assert any("ALERTA: Declínio crítico" in alert for alert in alerts)
    
    def test_generate_alerts_anomalous_growth(self, business_metrics_service):
        """Testa geração de alertas para crescimento anômalo"""
        metrics = [{"value": 100.0}]
        values = [100.0]
        growth_rate = 150.0
        trend_direction = "up"
        
        alerts = business_metrics_service._generate_alerts(metrics, values, growth_rate, trend_direction)
        
        assert any("ALERTA: Crescimento anômalo" in alert for alert in alerts)
    
    def test_create_kpi_success(self, business_metrics_service):
        """Testa criação de KPI com sucesso"""
        kpi = KPISchema(
            kpi_id="test_kpi_123",
            kpi_name="Taxa de Conversão",
            description="Taxa de conversão de leads em clientes",
            current_value=15.5,
            target_value=20.0,
            previous_value=12.0,
            percentage_change=29.2,
            target_achievement=77.5,
            status="on_track",
            period=MetricPeriod.MONTHLY.value,
            last_updated=datetime.now(timezone.utc),
            category=MetricCategory.SALES.value,
            priority="high",
            owner="sales_team"
        )
        
        kpi_id = business_metrics_service.create_kpi(kpi)
        
        assert kpi_id == "test_kpi_123"
        
        # Verificar se foi salvo no banco
        cursor = business_metrics_service.db.cursor()
        cursor.execute("SELECT * FROM kpis WHERE kpi_id = ?", [kpi_id])
        row = cursor.fetchone()
        
        assert row is not None
        assert row[0] == "test_kpi_123"
        assert row[1] == "Taxa de Conversão"
        assert row[3] == 15.5
    
    def test_get_kpis_empty(self, business_metrics_service):
        """Testa obtenção de KPIs vazia"""
        kpis = business_metrics_service.get_kpis()
        
        assert kpis == []
    
    def test_get_kpis_with_data(self, business_metrics_service):
        """Testa obtenção de KPIs com dados"""
        # Criar KPI
        kpi = KPISchema(
            kpi_id="test_kpi_123",
            kpi_name="Taxa de Conversão",
            description="Taxa de conversão de leads em clientes",
            current_value=15.5,
            target_value=20.0,
            previous_value=12.0,
            percentage_change=29.2,
            target_achievement=77.5,
            status="on_track",
            period=MetricPeriod.MONTHLY.value,
            last_updated=datetime.now(timezone.utc),
            category=MetricCategory.SALES.value,
            priority="high",
            owner="sales_team"
        )
        
        business_metrics_service.create_kpi(kpi)
        
        # Obter KPIs
        kpis = business_metrics_service.get_kpis()
        
        assert len(kpis) == 1
        assert kpis[0]["kpi_id"] == "test_kpi_123"
        assert kpis[0]["kpi_name"] == "Taxa de Conversão"
    
    def test_update_kpi_success(self, business_metrics_service):
        """Testa atualização de KPI com sucesso"""
        # Criar KPI
        kpi = KPISchema(
            kpi_id="test_kpi_123",
            kpi_name="Taxa de Conversão",
            description="Taxa de conversão de leads em clientes",
            current_value=15.5,
            target_value=20.0,
            previous_value=12.0,
            percentage_change=29.2,
            target_achievement=77.5,
            status="on_track",
            period=MetricPeriod.MONTHLY.value,
            last_updated=datetime.now(timezone.utc),
            category=MetricCategory.SALES.value,
            priority="high",
            owner="sales_team"
        )
        
        business_metrics_service.create_kpi(kpi)
        
        # Atualizar KPI
        updates = {"current_value": 18.0, "status": "exceeding"}
        success = business_metrics_service.update_kpi("test_kpi_123", updates)
        
        assert success is True
        
        # Verificar se foi atualizado
        kpis = business_metrics_service.get_kpis()
        assert kpis[0]["current_value"] == 18.0
        assert kpis[0]["status"] == "exceeding"
    
    def test_update_kpi_not_found(self, business_metrics_service):
        """Testa atualização de KPI não encontrado"""
        updates = {"current_value": 18.0}
        success = business_metrics_service.update_kpi("nonexistent_kpi", updates)
        
        assert success is False
    
    def test_create_dashboard_success(self, business_metrics_service):
        """Testa criação de dashboard com sucesso"""
        dashboard = DashboardSchema(
            dashboard_id="test_dashboard_123",
            dashboard_name="Dashboard de Vendas",
            description="Dashboard para acompanhamento de vendas",
            layout={"widgets": [{"type": "chart", "position": "top"}]},
            refresh_interval=300,
            auto_refresh=True,
            metrics=["revenue", "conversion_rate"],
            kpis=["kpi_1", "kpi_2"],
            is_public=True,
            allowed_users=["user_1", "user_2"],
            allowed_roles=["admin", "manager"],
            created_by="admin",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        dashboard_id = business_metrics_service.create_dashboard(dashboard)
        
        assert dashboard_id == "test_dashboard_123"
        
        # Verificar se foi salvo no banco
        cursor = business_metrics_service.db.cursor()
        cursor.execute("SELECT * FROM dashboards WHERE dashboard_id = ?", [dashboard_id])
        row = cursor.fetchone()
        
        assert row is not None
        assert row[0] == "test_dashboard_123"
        assert row[1] == "Dashboard de Vendas"
    
    def test_get_dashboards_empty(self, business_metrics_service):
        """Testa obtenção de dashboards vazia"""
        dashboards = business_metrics_service.get_dashboards()
        
        assert dashboards == []
    
    def test_get_dashboards_with_data(self, business_metrics_service):
        """Testa obtenção de dashboards com dados"""
        # Criar dashboard
        dashboard = DashboardSchema(
            dashboard_id="test_dashboard_123",
            dashboard_name="Dashboard de Vendas",
            description="Dashboard para acompanhamento de vendas",
            layout={"widgets": [{"type": "chart", "position": "top"}]},
            refresh_interval=300,
            auto_refresh=True,
            metrics=["revenue", "conversion_rate"],
            kpis=["kpi_1", "kpi_2"],
            is_public=True,
            allowed_users=["user_1", "user_2"],
            allowed_roles=["admin", "manager"],
            created_by="admin",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        business_metrics_service.create_dashboard(dashboard)
        
        # Obter dashboards
        dashboards = business_metrics_service.get_dashboards()
        
        assert len(dashboards) == 1
        assert dashboards[0]["dashboard_id"] == "test_dashboard_123"
        assert dashboards[0]["dashboard_name"] == "Dashboard de Vendas"


class TestBusinessMetricsServiceIntegration:
    """Testes de integração para BusinessMetricsService"""
    
    @pytest.fixture
    def temp_db_path(self):
        """Cria caminho temporário para banco de dados"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        yield db_path
        # Limpar após teste
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def business_metrics_service(self, temp_db_path):
        """Instância do BusinessMetricsService para testes"""
        service = BusinessMetricsService(db_path=temp_db_path)
        yield service
        service.close()
    
    def test_full_metrics_workflow(self, business_metrics_service):
        """Testa fluxo completo de métricas"""
        # Criar métricas
        metrics = []
        for i in range(5):
            metric = BusinessMetric(
                metric_id=f"metric_{i}",
                metric_type=MetricType.REVENUE.value,
                metric_name=f"Receita {i}",
                category=MetricCategory.FINANCIAL.value,
                value=1000.0 + (i * 100),
                previous_value=900.0 + (i * 100),
                target_value=1200.0 + (i * 100),
                period=MetricPeriod.MONTHLY.value,
                start_date=datetime.now(timezone.utc) - timedelta(days=30),
                end_date=datetime.now(timezone.utc),
                user_id=f"user_{i}",
                plan_type="premium" if i % 2 == 0 else "basic",
                region="BR",
                source="payment_gateway",
                version="1.0",
                environment="production",
                created_at=datetime.now(timezone.utc)
            )
            business_metrics_service.record_metric(metric)
            metrics.append(metric)
        
        # Obter métricas
        filters = MetricFilterSchema(metric_types=[MetricType.REVENUE.value])
        retrieved_metrics = business_metrics_service.get_metrics(filters)
        
        assert len(retrieved_metrics) == 5
        
        # Analisar métricas
        start_date = datetime.now(timezone.utc) - timedelta(days=30)
        end_date = datetime.now(timezone.utc)
        
        analysis = business_metrics_service.analyze_metrics(
            MetricType.REVENUE.value,
            start_date,
            end_date
        )
        
        assert analysis.total_records == 5
        assert analysis.average_value == 1200.0  # (1000+1100+1200+1300+1400)/5
        assert len(analysis.insights) > 0
        assert len(analysis.recommendations) > 0
        assert len(analysis.by_plan_type) == 2  # premium e basic


class TestBusinessMetricsServiceErrorHandling:
    """Testes de tratamento de erros para BusinessMetricsService"""
    
    @pytest.fixture
    def temp_db_path(self):
        """Cria caminho temporário para banco de dados"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        yield db_path
        # Limpar após teste
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def business_metrics_service(self, temp_db_path):
        """Instância do BusinessMetricsService para testes"""
        service = BusinessMetricsService(db_path=temp_db_path)
        yield service
        service.close()
    
    def test_database_error_handling(self, business_metrics_service):
        """Testa tratamento de erro de banco de dados"""
        # Fechar conexão para simular erro
        business_metrics_service.db.close()
        
        metric = BusinessMetric(
            metric_id="test_metric_123",
            metric_type=MetricType.REVENUE.value,
            metric_name="Receita Mensal",
            category=MetricCategory.FINANCIAL.value,
            value=10000.0,
            previous_value=8000.0,
            target_value=12000.0,
            period=MetricPeriod.MONTHLY.value,
            start_date=datetime.now(timezone.utc) - timedelta(days=30),
            end_date=datetime.now(timezone.utc),
            user_id="user_123",
            plan_type="premium",
            region="BR",
            source="payment_gateway",
            version="1.0",
            environment="production",
            created_at=datetime.now(timezone.utc)
        )
        
        # Deve levantar exceção ao tentar salvar
        with pytest.raises(Exception):
            business_metrics_service.record_metric(metric)


class TestBusinessMetricsServicePerformance:
    """Testes de performance para BusinessMetricsService"""
    
    @pytest.fixture
    def temp_db_path(self):
        """Cria caminho temporário para banco de dados"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        yield db_path
        # Limpar após teste
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def business_metrics_service(self, temp_db_path):
        """Instância do BusinessMetricsService para testes"""
        service = BusinessMetricsService(db_path=temp_db_path)
        yield service
        service.close()
    
    def test_multiple_metrics_performance(self, business_metrics_service):
        """Testa performance de múltiplas métricas"""
        import time
        
        start_time = time.time()
        
        # Criar múltiplas métricas
        for i in range(100):
            metric = BusinessMetric(
                metric_id=f"metric_{i}",
                metric_type=MetricType.REVENUE.value,
                metric_name=f"Receita {i}",
                category=MetricCategory.FINANCIAL.value,
                value=1000.0 + i,
                previous_value=900.0 + i,
                target_value=1200.0 + i,
                period=MetricPeriod.MONTHLY.value,
                start_date=datetime.now(timezone.utc) - timedelta(days=30),
                end_date=datetime.now(timezone.utc),
                user_id=f"user_{i}",
                plan_type="premium" if i % 2 == 0 else "basic",
                region="BR",
                source="payment_gateway",
                version="1.0",
                environment="production",
                created_at=datetime.now(timezone.utc)
            )
            
            business_metrics_service.record_metric(metric)
        
        end_time = time.time()
        
        # Verificar se todas foram salvas
        filters = MetricFilterSchema()
        metrics = business_metrics_service.get_metrics(filters)
        assert len(metrics) == 100
        
        # Verificar performance (deve ser rápido)
        assert end_time - start_time < 10.0  # Menos de 10 segundos para 100 métricas


if __name__ == "__main__":
    pytest.main([__file__]) 