"""
Testes Unitários para Cohort Analyzer
====================================

Testes abrangentes para o analisador de coortes:
- Criação de coortes
- Análise de coortes
- Comparação de coortes
- Análise de comportamento
- Métricas de retenção

Author: Paulo Júnior
Date: 2024-12-19
Tracing ID: ANALYTICS_TEST_003
"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

from infrastructure.analytics.avancado.cohort_analyzer import (
    CohortAnalyzer,
    CohortAnalysis,
    CohortComparison,
    CohortPeriod,
    CohortEvent,
    CohortDefinition
)


class TestCohortAnalyzer:
    """Testes para o analisador de coortes"""
    
    @pytest.fixture
    def analyzer(self):
        """Analisador de teste"""
        return CohortAnalyzer(db_url="sqlite:///:memory:")
    
    @pytest.fixture
    def sample_cohort_data(self):
        """Dados de coorte de exemplo"""
        return {
            "name": "Test Cohort",
            "description": "Test cohort for analysis",
            "cohort_period": CohortPeriod.WEEK,
            "trigger_event": "user_signup",
            "filters": {"country": "BR"},
            "created_by": "test_user"
        }
    
    def test_analyzer_initialization(self, analyzer):
        """Testa inicialização do analisador"""
        assert analyzer.engine is not None
        assert analyzer.Session is not None
    
    def test_create_cohort_success(self, analyzer, sample_cohort_data):
        """Testa criação bem-sucedida de coorte"""
        cohort_id = analyzer.create_cohort(
            name=sample_cohort_data["name"],
            description=sample_cohort_data["description"],
            cohort_period=sample_cohort_data["cohort_period"],
            trigger_event=sample_cohort_data["trigger_event"],
            filters=sample_cohort_data["filters"],
            created_by=sample_cohort_data["created_by"]
        )
        
        assert cohort_id is not None
        assert cohort_id.startswith("cohort_")
        
        # Verificar se foi salva no banco
        session = analyzer.Session()
        try:
            cohort_def = session.query(CohortDefinition).filter_by(id=cohort_id).first()
            assert cohort_def is not None
            assert cohort_def.name == sample_cohort_data["name"]
            assert cohort_def.description == sample_cohort_data["description"]
            assert cohort_def.cohort_period == sample_cohort_data["cohort_period"].value
            assert cohort_def.trigger_event == sample_cohort_data["trigger_event"]
            assert cohort_def.filters == sample_cohort_data["filters"]
            assert cohort_def.created_by == sample_cohort_data["created_by"]
        finally:
            session.close()
    
    def test_create_cohort_with_error(self, analyzer):
        """Testa criação de coorte com erro"""
        # Mock para simular erro no banco
        with patch.object(analyzer, 'Session') as mock_session:
            mock_session_instance = Mock()
            mock_session_instance.add.side_effect = Exception("Database error")
            mock_session.return_value = mock_session_instance
            
            with pytest.raises(Exception, match="Database error"):
                analyzer.create_cohort(
                    name="Test",
                    description="Test",
                    cohort_period=CohortPeriod.WEEK,
                    trigger_event="test"
                )
    
    def test_track_cohort_event_success(self, analyzer):
        """Testa rastreamento bem-sucedido de evento de coorte"""
        cohort_date = datetime.utcnow()
        event_date = cohort_date + timedelta(days=5)
        data = {"revenue": 100.0, "product": "test"}
        
        event_id = analyzer.track_cohort_event(
            user_id="test_user",
            cohort_date=cohort_date,
            event_type="purchase",
            event_date=event_date,
            data=data
        )
        
        assert event_id is not None
        assert event_id.startswith("event_")
        
        # Verificar se foi salvo no banco
        session = analyzer.Session()
        try:
            event = session.query(CohortEvent).filter_by(id=event_id).first()
            assert event is not None
            assert event.user_id == "test_user"
            assert event.cohort_date == cohort_date
            assert event.event_type == "purchase"
            assert event.event_date == event_date
            assert event.data == data
            assert event.period_number == 5  # 5 dias após a coorte
        finally:
            session.close()
    
    def test_analyze_cohort_success(self, analyzer):
        """Testa análise bem-sucedida de coorte"""
        # Criar coorte e eventos de teste
        cohort_id = analyzer.create_cohort(
            name="Test Cohort",
            description="Test",
            cohort_period=CohortPeriod.WEEK,
            trigger_event="signup"
        )
        
        # Adicionar eventos de teste
        cohort_date = datetime.utcnow()
        for index in range(10):  # 10 usuários
            for day in range(7):  # 7 dias
                analyzer.track_cohort_event(
                    user_id=f"user_{index}",
                    cohort_date=cohort_date,
                    event_type="activity",
                    event_date=cohort_date + timedelta(days=day),
                    data={"revenue": 10.0 * (day + 1)}
                )
        
        # Analisar coorte
        analysis = analyzer.analyze_cohort(cohort_id, max_periods=7)
        
        assert analysis is not None
        assert analysis.cohort_id == cohort_id
        assert analysis.cohort_size == 10
        assert len(analysis.retention_curve) == 7
        assert len(analysis.revenue_curve) == 7
        assert len(analysis.ltv_curve) == 7
        assert analysis.churn_rate >= 0
        assert analysis.avg_lifetime >= 0
        assert analysis.total_revenue > 0
    
    def test_analyze_cohort_not_found(self, analyzer):
        """Testa análise de coorte inexistente"""
        analysis = analyzer.analyze_cohort("nonexistent_cohort")
        assert analysis is None
    
    def test_analyze_cohort_no_events(self, analyzer):
        """Testa análise de coorte sem eventos"""
        cohort_id = analyzer.create_cohort(
            name="Empty Cohort",
            description="Test",
            cohort_period=CohortPeriod.WEEK,
            trigger_event="signup"
        )
        
        analysis = analyzer.analyze_cohort(cohort_id)
        assert analysis is None
    
    def test_calculate_churn_rate(self, analyzer):
        """Testa cálculo de taxa de churn"""
        # Curva de retenção de exemplo
        retention_curve = [100, 80, 60, 40, 30, 25, 20]  # 100% -> 20%
        
        churn_rate = analyzer._calculate_churn_rate(retention_curve)
        
        assert isinstance(churn_rate, float)
        assert churn_rate >= 0
        assert churn_rate <= 100
        
        # Churn rate deve ser aproximadamente 80% (100 - média da retenção)
        expected_churn = 100 - np.mean(retention_curve[1:])  # Exclui período 0
        assert abs(churn_rate - expected_churn) < 1.0
    
    def test_calculate_avg_lifetime(self, analyzer):
        """Testa cálculo de tempo médio de vida"""
        # Curva de retenção de exemplo
        retention_curve = [100, 80, 60, 40, 30, 25, 20]
        
        avg_lifetime = analyzer._calculate_avg_lifetime(retention_curve)
        
        assert isinstance(avg_lifetime, float)
        assert avg_lifetime >= 0
        
        # Tempo médio deve ser a soma das taxas de retenção dividida por 100
        expected_lifetime = sum(retention_curve) / 100
        assert abs(avg_lifetime - expected_lifetime) < 0.1
    
    def test_analyze_cohorts_by_period(self, analyzer):
        """Testa análise de múltiplas coortes por período"""
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
        
        # Criar coortes de teste
        for index in range(3):
            cohort_date = start_date + timedelta(weeks=index)
            cohort_id = analyzer.create_cohort(
                name=f"Cohort {index}",
                description="Test",
                cohort_period=CohortPeriod.WEEK,
                trigger_event="signup"
            )
            
            # Adicionar eventos
            for user in range(5):
                analyzer.track_cohort_event(
                    user_id=f"user_{index}_{user}",
                    cohort_date=cohort_date,
                    event_type="activity",
                    event_date=cohort_date + timedelta(days=user),
                    data={"revenue": 10.0}
                )
        
        # Analisar coortes
        analyses = analyzer.analyze_cohorts_by_period(
            start_date, end_date, CohortPeriod.WEEK
        )
        
        assert len(analyses) > 0
        assert all(isinstance(analysis, CohortAnalysis) for analysis in analyses)
    
    def test_compare_cohorts(self, analyzer):
        """Testa comparação de coortes"""
        # Criar duas coortes
        cohort_1_id = analyzer.create_cohort(
            name="Cohort 1",
            description="Test",
            cohort_period=CohortPeriod.WEEK,
            trigger_event="signup"
        )
        
        cohort_2_id = analyzer.create_cohort(
            name="Cohort 2",
            description="Test",
            cohort_period=CohortPeriod.WEEK,
            trigger_event="signup"
        )
        
        # Adicionar eventos diferentes para cada coorte
        cohort_1_date = datetime.utcnow() - timedelta(weeks=2)
        cohort_2_date = datetime.utcnow() - timedelta(weeks=1)
        
        # Coorte 1: 10 usuários, retenção baixa
        for index in range(10):
            for day in range(3):  # Só 3 dias de atividade
                analyzer.track_cohort_event(
                    user_id=f"user_1_{index}",
                    cohort_date=cohort_1_date,
                    event_type="activity",
                    event_date=cohort_1_date + timedelta(days=day),
                    data={"revenue": 5.0}
                )
        
        # Coorte 2: 10 usuários, retenção alta
        for index in range(10):
            for day in range(7):  # 7 dias de atividade
                analyzer.track_cohort_event(
                    user_id=f"user_2_{index}",
                    cohort_date=cohort_2_date,
                    event_type="activity",
                    event_date=cohort_2_date + timedelta(days=day),
                    data={"revenue": 15.0}
                )
        
        # Analisar coortes
        analysis_1 = analyzer.analyze_cohort(cohort_1_id)
        analysis_2 = analyzer.analyze_cohort(cohort_2_id)
        
        # Comparar
        comparison = analyzer.compare_cohorts(analysis_1, analysis_2)
        
        assert comparison is not None
        assert comparison.cohort_1 == analysis_1
        assert comparison.cohort_2 == analysis_2
        assert len(comparison.retention_diff) > 0
        assert len(comparison.revenue_diff) > 0
        assert len(comparison.ltv_diff) > 0
        assert comparison.significance is not None
    
    def test_analyze_cohort_behavior(self, analyzer):
        """Testa análise de comportamento da coorte"""
        # Criar coorte e eventos
        cohort_date = datetime.utcnow()
        cohort_id = f"cohort_{int(cohort_date.timestamp())}"
        
        # Adicionar eventos variados
        for index in range(5):
            analyzer.track_cohort_event(
                user_id=f"user_{index}",
                cohort_date=cohort_date,
                event_type="page_view",
                event_date=cohort_date + timedelta(hours=index),
                data={"page": "home"}
            )
            
            analyzer.track_cohort_event(
                user_id=f"user_{index}",
                cohort_date=cohort_date,
                event_type="purchase",
                event_date=cohort_date + timedelta(hours=index+1),
                data={"revenue": 50.0}
            )
        
        # Analisar comportamento
        behavior = analyzer.analyze_cohort_behavior(cohort_id)
        
        assert behavior is not None
        assert "total_events" in behavior
        assert "unique_users" in behavior
        assert "event_types" in behavior
        assert "activity_pattern" in behavior
        assert "engagement_metrics" in behavior
        
        assert behavior["total_events"] == 10  # 5 page_views + 5 purchases
        assert behavior["unique_users"] == 5
        assert behavior["event_types"]["page_view"] == 5
        assert behavior["event_types"]["purchase"] == 5
    
    def test_calculate_significance(self, analyzer):
        """Testa cálculo de significância estatística"""
        # Criar duas análises de coorte diferentes
        analysis_1 = CohortAnalysis(
            cohort_id="cohort_1",
            cohort_date=datetime.utcnow(),
            cohort_size=100,
            retention_curve=[100, 80, 60, 40, 30],
            revenue_curve=[0, 10, 15, 20, 25],
            ltv_curve=[0, 10, 25, 45, 70],
            churn_rate=70.0,
            avg_lifetime=3.0,
            total_revenue=70.0
        )
        
        analysis_2 = CohortAnalysis(
            cohort_id="cohort_2",
            cohort_date=datetime.utcnow(),
            cohort_size=100,
            retention_curve=[100, 90, 85, 80, 75],
            revenue_curve=[0, 15, 20, 25, 30],
            ltv_curve=[0, 15, 35, 60, 90],
            churn_rate=25.0,
            avg_lifetime=4.2,
            total_revenue=90.0
        )
        
        significance = analyzer._calculate_significance(analysis_1, analysis_2)
        
        assert significance is not None
        assert "retention_significance" in significance
        assert "revenue_significance" in significance
        assert "ltv_significance" in significance
        assert "overall_significance" in significance
        
        # Verificar que a significância está entre 0 e 1
        for key, value in significance.items():
            assert 0 <= value <= 1


class TestCohortAnalysis:
    """Testes para a classe CohortAnalysis"""
    
    def test_cohort_analysis_creation(self):
        """Testa criação de análise de coorte"""
        analysis = CohortAnalysis(
            cohort_id="test_cohort",
            cohort_date=datetime.utcnow(),
            cohort_size=100,
            retention_curve=[100, 80, 60, 40, 30],
            revenue_curve=[0, 10, 15, 20, 25],
            ltv_curve=[0, 10, 25, 45, 70],
            churn_rate=70.0,
            avg_lifetime=3.0,
            total_revenue=70.0
        )
        
        assert analysis.cohort_id == "test_cohort"
        assert analysis.cohort_size == 100
        assert len(analysis.retention_curve) == 5
        assert len(analysis.revenue_curve) == 5
        assert len(analysis.ltv_curve) == 5
        assert analysis.churn_rate == 70.0
        assert analysis.avg_lifetime == 3.0
        assert analysis.total_revenue == 70.0
        assert analysis.segment == "all"  # valor padrão
    
    def test_cohort_analysis_with_segment(self):
        """Testa criação de análise de coorte com segmento"""
        analysis = CohortAnalysis(
            cohort_id="test_cohort",
            cohort_date=datetime.utcnow(),
            cohort_size=100,
            retention_curve=[100, 80, 60],
            revenue_curve=[0, 10, 15],
            ltv_curve=[0, 10, 25],
            churn_rate=40.0,
            avg_lifetime=2.4,
            total_revenue=25.0,
            segment="premium"
        )
        
        assert analysis.segment == "premium"


class TestCohortComparison:
    """Testes para a classe CohortComparison"""
    
    def test_cohort_comparison_creation(self):
        """Testa criação de comparação de coortes"""
        analysis_1 = CohortAnalysis(
            cohort_id="cohort_1",
            cohort_date=datetime.utcnow(),
            cohort_size=100,
            retention_curve=[100, 80, 60],
            revenue_curve=[0, 10, 15],
            ltv_curve=[0, 10, 25],
            churn_rate=40.0,
            avg_lifetime=2.4,
            total_revenue=25.0
        )
        
        analysis_2 = CohortAnalysis(
            cohort_id="cohort_2",
            cohort_date=datetime.utcnow(),
            cohort_size=100,
            retention_curve=[100, 90, 85],
            revenue_curve=[0, 15, 20],
            ltv_curve=[0, 15, 35],
            churn_rate=15.0,
            avg_lifetime=2.75,
            total_revenue=35.0
        )
        
        comparison = CohortComparison(
            cohort_1=analysis_1,
            cohort_2=analysis_2,
            retention_diff=[0, 10, 25],
            revenue_diff=[0, 5, 5],
            ltv_diff=[0, 5, 10],
            significance={"overall_significance": 0.05}
        )
        
        assert comparison.cohort_1 == analysis_1
        assert comparison.cohort_2 == analysis_2
        assert len(comparison.retention_diff) == 3
        assert len(comparison.revenue_diff) == 3
        assert len(comparison.ltv_diff) == 3
        assert comparison.significance["overall_significance"] == 0.05


class TestCohortPeriod:
    """Testes para o enum CohortPeriod"""
    
    def test_cohort_period_values(self):
        """Testa valores do enum CohortPeriod"""
        assert CohortPeriod.DAY.value == "day"
        assert CohortPeriod.WEEK.value == "week"
        assert CohortPeriod.MONTH.value == "month"
        assert CohortPeriod.QUARTER.value == "quarter"
        assert CohortPeriod.YEAR.value == "year"
    
    def test_cohort_period_comparison(self):
        """Testa comparação de períodos de coorte"""
        assert CohortPeriod.DAY != CohortPeriod.WEEK
        assert CohortPeriod.DAY == CohortPeriod.DAY


class TestCohortEvent:
    """Testes para a classe CohortEvent"""
    
    def test_cohort_event_creation(self):
        """Testa criação de evento de coorte"""
        event = CohortEvent(
            id="test_event",
            user_id="test_user",
            cohort_date=datetime.utcnow(),
            event_type="purchase",
            event_date=datetime.utcnow() + timedelta(days=1),
            period_number=1,
            data={"revenue": 100.0},
            metadata={"source": "web"}
        )
        
        assert event.id == "test_event"
        assert event.user_id == "test_user"
        assert event.event_type == "purchase"
        assert event.period_number == 1
        assert event.data == {"revenue": 100.0}
        assert event.metadata == {"source": "web"}


class TestCohortDefinition:
    """Testes para a classe CohortDefinition"""
    
    def test_cohort_definition_creation(self):
        """Testa criação de definição de coorte"""
        definition = CohortDefinition(
            id="test_cohort",
            name="Test Cohort",
            description="Test cohort definition",
            cohort_period="week",
            trigger_event="signup",
            filters={"country": "BR"},
            created_by="test_user"
        )
        
        assert definition.id == "test_cohort"
        assert definition.name == "Test Cohort"
        assert definition.description == "Test cohort definition"
        assert definition.cohort_period == "week"
        assert definition.trigger_event == "signup"
        assert definition.filters == {"country": "BR"}
        assert definition.created_by == "test_user" 