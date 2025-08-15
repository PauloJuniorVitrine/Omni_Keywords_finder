"""
Testes Unitários para Funnel Analyzer
====================================

Testes abrangentes para o analisador de funis de conversão:
- Análise de funis
- Detecção de gargalos
- Análise por segmentos
- Predição de conversão
- Geração de recomendações

Author: Paulo Júnior
Date: 2024-12-19
Tracing ID: ANALYTICS_TEST_002
"""

import pytest
import math
import statistics
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

from infrastructure.analytics.avancado.funnel_analyzer import (
    FunnelAnalyzer,
    FunnelStep,
    FunnelStepType,
    FunnelAnalysis
)
from infrastructure.analytics.avancado.real_time_analytics import (
    RealTimeAnalytics,
    AnalyticsEvent,
    EventType
)


class TestFunnelAnalyzer:
    """Testes para o analisador de funis"""
    
    @pytest.fixture
    def analytics(self):
        """Sistema de analytics de teste"""
        return RealTimeAnalytics(enable_observability=False)
    
    @pytest.fixture
    def funnel_analyzer(self, analytics):
        """Analisador de funis de teste"""
        return FunnelAnalyzer(
            analytics=analytics,
            enable_ml=False,
            enable_observability=False
        )
    
    @pytest.fixture
    def sample_funnel_steps(self):
        """Passos de funil de exemplo"""
        return [
            FunnelStep(
                step_id="landing",
                step_name="Landing Page",
                step_type=FunnelStepType.PAGE_VIEW,
                required_properties={"page": "landing"},
                conversion_rate_target=100.0
            ),
            FunnelStep(
                step_id="signup",
                step_name="Sign Up",
                step_type=FunnelStepType.FORM_COMPLETE,
                required_properties={"form": "signup"},
                conversion_rate_target=25.0
            ),
            FunnelStep(
                step_id="purchase",
                step_name="Purchase",
                step_type=FunnelStepType.PURCHASE,
                required_properties={"status": "completed"},
                conversion_rate_target=5.0
            )
        ]
    
    @pytest.fixture
    def sample_events(self):
        """Eventos de exemplo"""
        base_time = datetime.utcnow()
        events = []
        
        # Eventos para landing page (1000 usuários)
        for index in range(1000):
            events.append(AnalyticsEvent(
                event_id=f"evt_landing_{index}",
                event_type=EventType.PAGE_VIEW,
                user_id=f"user_{index}",
                session_id=f"session_{index}",
                timestamp=base_time + timedelta(seconds=index),
                properties={"page": "landing"},
                metadata={"funnel_id": "test_funnel", "step_id": "landing"}
            ))
        
        # Eventos para signup (250 usuários - 25% conversão)
        for index in range(250):
            events.append(AnalyticsEvent(
                event_id=f"evt_signup_{index}",
                event_type=EventType.FORM_COMPLETE,
                user_id=f"user_{index}",
                session_id=f"session_{index}",
                timestamp=base_time + timedelta(seconds=index+60),
                properties={"form": "signup"},
                metadata={"funnel_id": "test_funnel", "step_id": "signup"}
            ))
        
        # Eventos para purchase (50 usuários - 5% conversão)
        for index in range(50):
            events.append(AnalyticsEvent(
                event_id=f"evt_purchase_{index}",
                event_type=EventType.PURCHASE,
                user_id=f"user_{index}",
                session_id=f"session_{index}",
                timestamp=base_time + timedelta(seconds=index+120),
                properties={"status": "completed"},
                metadata={"funnel_id": "test_funnel", "step_id": "purchase"}
            ))
        
        return events
    
    def test_funnel_analyzer_initialization(self, funnel_analyzer, analytics):
        """Testa inicialização do analisador de funis"""
        assert funnel_analyzer.analytics == analytics
        assert funnel_analyzer.enable_ml is False
        assert funnel_analyzer.enable_observability is False
        assert funnel_analyzer.funnel_cache == {}
        assert funnel_analyzer.conversion_model is None
        assert funnel_analyzer.bottleneck_model is None
    
    def test_analyze_funnel_success(self, funnel_analyzer, sample_funnel_steps, sample_events):
        """Testa análise bem-sucedida de funil"""
        # Mock da configuração do funil
        funnel_config = {
            "funnel_id": "test_funnel",
            "funnel_name": "Test Funnel",
            "steps": sample_funnel_steps,
            "created_at": datetime.utcnow()
        }
        
        with patch.object(funnel_analyzer, '_get_funnel_config') as mock_config:
            with patch.object(funnel_analyzer, '_collect_funnel_events') as mock_events:
                mock_config.return_value = funnel_config
                mock_events.return_value = sample_events
                
                analysis = funnel_analyzer.analyze_funnel(
                    funnel_id="test_funnel",
                    time_range=timedelta(days=7)
                )
        
        assert analysis.funnel_id == "test_funnel"
        assert analysis.funnel_name == "Test Funnel"
        assert len(analysis.steps) == 3
        assert analysis.total_conversions == 50
        assert analysis.overall_conversion_rate == 5.0  # 50/1000 * 100
        assert len(analysis.step_analysis) == 3
        assert len(analysis.bottlenecks) > 0
        assert len(analysis.recommendations) > 0
        assert analysis.generated_at is not None
    
    def test_analyze_funnel_not_found(self, funnel_analyzer):
        """Testa análise de funil inexistente"""
        with patch.object(funnel_analyzer, '_get_funnel_config') as mock_config:
            mock_config.return_value = None
            
            with pytest.raises(ValueError, match="Funil test_funnel não encontrado"):
                funnel_analyzer.analyze_funnel("test_funnel")
    
    def test_analyze_funnel_steps(self, funnel_analyzer, sample_funnel_steps, sample_events):
        """Testa análise de passos do funil"""
        step_analysis = funnel_analyzer._analyze_funnel_steps(sample_funnel_steps, sample_events)
        
        assert len(step_analysis) == 3
        
        # Verificar análise do primeiro passo (landing)
        landing_analysis = step_analysis["landing"]
        assert landing_analysis["step_name"] == "Landing Page"
        assert landing_analysis["conversions"] == 1000
        assert landing_analysis["unique_users"] == 1000
        assert landing_analysis["conversion_rate"] == 100.0
        
        # Verificar análise do segundo passo (signup)
        signup_analysis = step_analysis["signup"]
        assert signup_analysis["step_name"] == "Sign Up"
        assert signup_analysis["conversions"] == 250
        assert signup_analysis["unique_users"] == 250
        assert signup_analysis["conversion_rate"] == 25.0  # 250/1000 * 100
        
        # Verificar análise do terceiro passo (purchase)
        purchase_analysis = step_analysis["purchase"]
        assert purchase_analysis["step_name"] == "Purchase"
        assert purchase_analysis["conversions"] == 50
        assert purchase_analysis["unique_users"] == 50
        assert purchase_analysis["conversion_rate"] == 20.0  # 50/250 * 100
    
    def test_detect_bottlenecks(self, funnel_analyzer, sample_funnel_steps):
        """Testa detecção de gargalos"""
        step_analysis = {
            "landing": {
                "step_name": "Landing Page",
                "conversions": 1000,
                "conversion_rate": 100.0,
                "target_conversion_rate": 100.0,
                "performance_gap": 0.0
            },
            "signup": {
                "step_name": "Sign Up",
                "conversions": 200,
                "conversion_rate": 20.0,
                "target_conversion_rate": 25.0,
                "performance_gap": -5.0
            },
            "purchase": {
                "step_name": "Purchase",
                "conversions": 30,
                "conversion_rate": 15.0,
                "target_conversion_rate": 5.0,
                "performance_gap": 10.0
            }
        }
        
        bottlenecks = funnel_analyzer._detect_bottlenecks(sample_funnel_steps, step_analysis)
        
        assert len(bottlenecks) > 0
        
        # Verificar se o gargalo do signup foi detectado
        signup_bottleneck = next((b for b in bottlenecks if b["step_id"] == "signup"), None)
        assert signup_bottleneck is not None
        assert signup_bottleneck["severity"] == "high"
        assert "conversion rate" in signup_bottleneck["description"].lower()
    
    def test_generate_recommendations(self, funnel_analyzer, sample_funnel_steps):
        """Testa geração de recomendações"""
        step_analysis = {
            "landing": {
                "step_name": "Landing Page",
                "conversions": 1000,
                "conversion_rate": 100.0,
                "target_conversion_rate": 100.0,
                "performance_gap": 0.0
            },
            "signup": {
                "step_name": "Sign Up",
                "conversions": 200,
                "conversion_rate": 20.0,
                "target_conversion_rate": 25.0,
                "performance_gap": -5.0
            }
        }
        
        bottlenecks = [
            {
                "step_id": "signup",
                "severity": "high",
                "description": "Low conversion rate",
                "impact": "high"
            }
        ]
        
        recommendations = funnel_analyzer._generate_recommendations(
            sample_funnel_steps, step_analysis, bottlenecks
        )
        
        assert len(recommendations) > 0
        assert all(isinstance(rec, str) for rec in recommendations)
        
        # Verificar se há recomendações para o gargalo
        signup_recommendations = [rec for rec in recommendations if "signup" in rec.lower()]
        assert len(signup_recommendations) > 0
    
    def test_analyze_segments(self, funnel_analyzer, sample_funnel_steps, sample_events):
        """Testa análise por segmentos"""
        segments = ["new_users", "returning_users"]
        
        segment_analysis = funnel_analyzer._analyze_segments(
            sample_funnel_steps, sample_events, segments
        )
        
        assert len(segment_analysis) == 2
        assert "new_users" in segment_analysis
        assert "returning_users" in segment_analysis
        
        # Verificar estrutura da análise por segmento
        for segment, analysis in segment_analysis.items():
            assert "conversion_rates" in analysis
            assert "total_conversions" in analysis
            assert "performance_comparison" in analysis
    
    def test_predict_conversion_rate(self, funnel_analyzer, sample_funnel_steps):
        """Testa predição de taxa de conversão"""
        step_analysis = {
            "landing": {
                "conversions": 1000,
                "conversion_rate": 100.0,
                "avg_time_seconds": 30
            },
            "signup": {
                "conversions": 250,
                "conversion_rate": 25.0,
                "avg_time_seconds": 120
            },
            "purchase": {
                "conversions": 50,
                "conversion_rate": 20.0,
                "avg_time_seconds": 300
            }
        }
        
        predicted_rate = funnel_analyzer._predict_conversion_rate(sample_funnel_steps, step_analysis)
        
        assert isinstance(predicted_rate, float)
        assert 0 <= predicted_rate <= 100
    
    def test_get_funnel_config(self, funnel_analyzer):
        """Testa obtenção de configuração de funil"""
        config = funnel_analyzer._get_funnel_config("ecommerce_funnel")
        
        assert config is not None
        assert config["funnel_id"] == "ecommerce_funnel"
        assert config["funnel_name"] == "E-commerce Funnel"
        assert len(config["steps"]) == 4
    
    def test_get_funnel_config_not_found(self, funnel_analyzer):
        """Testa obtenção de configuração de funil inexistente"""
        config = funnel_analyzer._get_funnel_config("nonexistent_funnel")
        assert config is None
    
    def test_collect_funnel_events(self, funnel_analyzer, sample_funnel_steps):
        """Testa coleta de eventos do funil"""
        events = funnel_analyzer._collect_funnel_events(
            "test_funnel", sample_funnel_steps, timedelta(days=7)
        )
        
        assert len(events) > 0
        assert all(isinstance(event, AnalyticsEvent) for event in events)
        
        # Verificar se há eventos para cada passo
        step_ids = set(event.metadata.get("step_id") for event in events)
        expected_step_ids = {step.step_id for step in sample_funnel_steps}
        assert step_ids == expected_step_ids
    
    def test_map_step_type_to_event_type(self, funnel_analyzer):
        """Testa mapeamento de tipos de passo para tipos de evento"""
        # Testar mapeamentos
        assert funnel_analyzer._map_step_type_to_event_type(FunnelStepType.PAGE_VIEW) == EventType.PAGE_VIEW
        assert funnel_analyzer._map_step_type_to_event_type(FunnelStepType.CLICK) == EventType.CLICK
        assert funnel_analyzer._map_step_type_to_event_type(FunnelStepType.FORM_COMPLETE) == EventType.FORM_COMPLETE
        assert funnel_analyzer._map_step_type_to_event_type(FunnelStepType.PURCHASE) == EventType.PURCHASE
        assert funnel_analyzer._map_step_type_to_event_type(FunnelStepType.CUSTOM) == EventType.CUSTOM
    
    def test_calculate_step_performance_score(self, funnel_analyzer):
        """Testa cálculo de score de performance do passo"""
        step_analysis = {
            "conversion_rate": 25.0,
            "target_conversion_rate": 30.0,
            "avg_time_seconds": 120
        }
        
        score = funnel_analyzer._calculate_step_performance_score(step_analysis)
        
        assert isinstance(score, float)
        assert 0 <= score <= 100
    
    def test_identify_optimization_opportunities(self, funnel_analyzer, sample_funnel_steps):
        """Testa identificação de oportunidades de otimização"""
        step_analysis = {
            "landing": {
                "conversion_rate": 100.0,
                "target_conversion_rate": 100.0,
                "performance_gap": 0.0
            },
            "signup": {
                "conversion_rate": 20.0,
                "target_conversion_rate": 25.0,
                "performance_gap": -5.0
            }
        }
        
        opportunities = funnel_analyzer._identify_optimization_opportunities(
            sample_funnel_steps, step_analysis
        )
        
        assert len(opportunities) > 0
        assert all(isinstance(opp, dict) for opp in opportunities)
        
        # Verificar se há oportunidades para o passo com gap negativo
        signup_opportunities = [opp for opp in opportunities if opp.get("step_id") == "signup"]
        assert len(signup_opportunities) > 0
    
    def test_analyze_funnel_with_ml_enabled(self, analytics):
        """Testa análise de funil com ML habilitado"""
        funnel_analyzer = FunnelAnalyzer(
            analytics=analytics,
            enable_ml=True,
            enable_observability=False
        )
        
        # Verificar se modelos ML foram inicializados
        assert funnel_analyzer.conversion_model is not None
        assert funnel_analyzer.bottleneck_model is not None
    
    def test_analyze_funnel_with_observability_enabled(self, analytics):
        """Testa análise de funil com observabilidade habilitada"""
        with patch('infrastructure.observability.telemetry.TelemetryManager') as mock_telemetry:
            with patch('infrastructure.observability.metrics.MetricsManager') as mock_metrics:
                mock_telemetry.return_value = Mock()
                mock_metrics.return_value = Mock()
                
                funnel_analyzer = FunnelAnalyzer(
                    analytics=analytics,
                    enable_ml=False,
                    enable_observability=True
                )
                
                assert funnel_analyzer.telemetry is not None
                assert funnel_analyzer.metrics is not None
    
    def test_record_funnel_metrics(self, funnel_analyzer, sample_funnel_steps, sample_events):
        """Testa registro de métricas do funil"""
        # Mock da análise
        analysis = FunnelAnalysis(
            funnel_id="test_funnel",
            funnel_name="Test Funnel",
            steps=sample_funnel_steps,
            analysis_period=timedelta(days=7),
            total_conversions=50,
            overall_conversion_rate=5.0,
            step_analysis={},
            bottlenecks=[],
            recommendations=[],
            segment_analysis={},
            predicted_conversion_rate=5.5,
            generated_at=datetime.utcnow()
        )
        
        with patch.object(funnel_analyzer, 'metrics') as mock_metrics:
            mock_metrics.record_gauge = Mock()
            mock_metrics.increment_counter = Mock()
            
            funnel_analyzer._record_funnel_metrics(analysis)
            
            # Verificar se métricas foram registradas
            mock_metrics.record_gauge.assert_called()
            mock_metrics.increment_counter.assert_called()


class TestFunnelStep:
    """Testes para a classe FunnelStep"""
    
    def test_funnel_step_creation(self):
        """Testa criação de passo do funil"""
        step = FunnelStep(
            step_id="test_step",
            step_name="Test Step",
            step_type=FunnelStepType.PAGE_VIEW,
            required_properties={"page": "test"},
            conversion_rate_target=25.0
        )
        
        assert step.step_id == "test_step"
        assert step.step_name == "Test Step"
        assert step.step_type == FunnelStepType.PAGE_VIEW
        assert step.required_properties == {"page": "test"}
        assert step.conversion_rate_target == 25.0
    
    def test_funnel_step_default_values(self):
        """Testa valores padrão do passo do funil"""
        step = FunnelStep(
            step_id="test_step",
            step_name="Test Step",
            step_type=FunnelStepType.CLICK
        )
        
        assert step.required_properties == {}
        assert step.conversion_rate_target == 0.0


class TestFunnelStepType:
    """Testes para o enum FunnelStepType"""
    
    def test_funnel_step_type_values(self):
        """Testa valores do enum FunnelStepType"""
        assert FunnelStepType.PAGE_VIEW.value == "page_view"
        assert FunnelStepType.CLICK.value == "click"
        assert FunnelStepType.FORM_START.value == "form_start"
        assert FunnelStepType.FORM_COMPLETE.value == "form_complete"
        assert FunnelStepType.PURCHASE.value == "purchase"
        assert FunnelStepType.CUSTOM.value == "custom"
    
    def test_funnel_step_type_comparison(self):
        """Testa comparação de tipos de passo"""
        assert FunnelStepType.PAGE_VIEW != FunnelStepType.CLICK
        assert FunnelStepType.PAGE_VIEW == FunnelStepType.PAGE_VIEW


class TestFunnelAnalysis:
    """Testes para a classe FunnelAnalysis"""
    
    def test_funnel_analysis_creation(self, sample_funnel_steps):
        """Testa criação de análise de funil"""
        analysis = FunnelAnalysis(
            funnel_id="test_funnel",
            funnel_name="Test Funnel",
            steps=sample_funnel_steps,
            analysis_period=timedelta(days=7),
            total_conversions=50,
            overall_conversion_rate=5.0,
            step_analysis={},
            bottlenecks=[],
            recommendations=[],
            segment_analysis={},
            predicted_conversion_rate=5.5,
            generated_at=datetime.utcnow()
        )
        
        assert analysis.funnel_id == "test_funnel"
        assert analysis.funnel_name == "Test Funnel"
        assert len(analysis.steps) == 3
        assert analysis.total_conversions == 50
        assert analysis.overall_conversion_rate == 5.0
        assert analysis.predicted_conversion_rate == 5.5
        assert analysis.generated_at is not None 