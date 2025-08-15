"""
Testes Unitários para Business Metrics Models
Business Metrics Models - Modelos de métricas de negócio para tracking de ROI, conversões e insights

Prompt: Implementação de testes unitários para Business Metrics Models
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Fase: Criação sem execução - Testes baseados em código real
Tracing ID: BUSINESS_METRICS_TESTS_001_20250127
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, date, timedelta
from typing import Dict, Any, List, Optional

from backend.app.models.business_metrics import (
    KeywordMetrics,
    CategoryROI,
    ConversionTracking,
    RankingHistory,
    PredictiveInsights,
    BusinessReport
)


class TestKeywordMetrics:
    """Testes para KeywordMetrics"""
    
    @pytest.fixture
    def sample_keyword_data(self):
        """Dados de exemplo para KeywordMetrics"""
        return {
            'keyword': 'omni keywords finder',
            'categoria_id': 1,
            'search_volume': 1000,
            'search_volume_change': 15.5,
            'current_ranking': 5,
            'previous_ranking': 8,
            'ranking_improvement': 37.5,
            'click_through_rate': 3.2,
            'conversion_rate': 2.1,
            'cost_per_click': 1.50,
            'cost_per_conversion': 71.43,
            'revenue_generated': 1500.0,
            'cost_incurred': 500.0,
            'roi_percentage': 200.0,
            'profit_margin': 66.67,
            'impressions': 5000,
            'clicks': 160,
            'conversions': 33
        }
    
    @pytest.fixture
    def keyword_metrics_instance(self, sample_keyword_data):
        """Instância de KeywordMetrics para testes"""
        return KeywordMetrics(**sample_keyword_data)
    
    def test_initialization(self, sample_keyword_data):
        """Testa inicialização básica de KeywordMetrics"""
        instance = KeywordMetrics(**sample_keyword_data)
        
        assert instance.keyword == 'omni keywords finder'
        assert instance.categoria_id == 1
        assert instance.search_volume == 1000
        assert instance.search_volume_change == 15.5
        assert instance.current_ranking == 5
        assert instance.previous_ranking == 8
        assert instance.ranking_improvement == 37.5
        assert instance.click_through_rate == 3.2
        assert instance.conversion_rate == 2.1
        assert instance.cost_per_click == 1.50
        assert instance.cost_per_conversion == 71.43
        assert instance.revenue_generated == 1500.0
        assert instance.cost_incurred == 500.0
        assert instance.roi_percentage == 200.0
        assert instance.profit_margin == 66.67
        assert instance.impressions == 5000
        assert instance.clicks == 160
        assert instance.conversions == 33
    
    def test_validation_required_fields(self):
        """Testa validação de campos obrigatórios"""
        # Teste sem keyword (campo obrigatório)
        with pytest.raises(Exception):
            KeywordMetrics(categoria_id=1)
        
        # Teste sem categoria_id (campo obrigatório)
        with pytest.raises(Exception):
            KeywordMetrics(keyword='test')
    
    def test_timestamps_auto_generation(self, sample_keyword_data):
        """Testa geração automática de timestamps"""
        instance = KeywordMetrics(**sample_keyword_data)
        
        assert instance.data_coleta is not None
        assert instance.data_atualizacao is not None
        assert isinstance(instance.data_coleta, datetime)
        assert isinstance(instance.data_atualizacao, datetime)
    
    def test_roi_calculation(self, sample_keyword_data):
        """Testa cálculo de ROI"""
        instance = KeywordMetrics(**sample_keyword_data)
        
        # ROI = (revenue - cost) / cost * 100
        expected_roi = (1500.0 - 500.0) / 500.0 * 100
        assert instance.roi_percentage == expected_roi
    
    def test_ranking_improvement_calculation(self, sample_keyword_data):
        """Testa cálculo de melhoria de ranking"""
        instance = KeywordMetrics(**sample_keyword_data)
        
        # Melhoria = (previous - current) / previous * 100
        expected_improvement = (8 - 5) / 8 * 100
        assert instance.ranking_improvement == expected_improvement
    
    def test_repr_method(self, keyword_metrics_instance):
        """Testa método __repr__"""
        repr_str = repr(keyword_metrics_instance)
        assert 'KeywordMetrics' in repr_str
        assert 'omni keywords finder' in repr_str
        assert '200.0%' in repr_str
    
    def test_edge_cases(self):
        """Testa casos extremos"""
        # Teste com valores zero
        zero_data = {
            'keyword': 'test zero',
            'categoria_id': 1,
            'search_volume': 0,
            'current_ranking': 1,
            'previous_ranking': 1
        }
        instance = KeywordMetrics(**zero_data)
        assert instance.search_volume == 0
        assert instance.current_ranking == 1
        
        # Teste com valores negativos
        negative_data = {
            'keyword': 'test negative',
            'categoria_id': 1,
            'search_volume_change': -10.5,
            'current_ranking': 10,
            'previous_ranking': 5
        }
        instance = KeywordMetrics(**negative_data)
        assert instance.search_volume_change == -10.5


class TestCategoryROI:
    """Testes para CategoryROI"""
    
    @pytest.fixture
    def sample_category_roi_data(self):
        """Dados de exemplo para CategoryROI"""
        return {
            'categoria_id': 1,
            'total_revenue': 50000.0,
            'total_cost': 15000.0,
            'total_roi': 35000.0,
            'roi_percentage': 233.33,
            'total_keywords': 100,
            'active_keywords': 85,
            'avg_ranking': 7.5,
            'avg_conversion_rate': 2.8,
            'periodo_inicio': date(2024, 1, 1),
            'periodo_fim': date(2024, 1, 31)
        }
    
    @pytest.fixture
    def category_roi_instance(self, sample_category_roi_data):
        """Instância de CategoryROI para testes"""
        return CategoryROI(**sample_category_roi_data)
    
    def test_initialization(self, sample_category_roi_data):
        """Testa inicialização básica de CategoryROI"""
        instance = CategoryROI(**sample_category_roi_data)
        
        assert instance.categoria_id == 1
        assert instance.total_revenue == 50000.0
        assert instance.total_cost == 15000.0
        assert instance.total_roi == 35000.0
        assert instance.roi_percentage == 233.33
        assert instance.total_keywords == 100
        assert instance.active_keywords == 85
        assert instance.avg_ranking == 7.5
        assert instance.avg_conversion_rate == 2.8
        assert instance.periodo_inicio == date(2024, 1, 1)
        assert instance.periodo_fim == date(2024, 1, 31)
    
    def test_default_values(self):
        """Testa valores padrão"""
        instance = CategoryROI(
            categoria_id=1,
            periodo_inicio=date(2024, 1, 1),
            periodo_fim=date(2024, 1, 31)
        )
        
        assert instance.total_revenue == 0.0
        assert instance.total_cost == 0.0
        assert instance.total_roi == 0.0
        assert instance.roi_percentage == 0.0
        assert instance.total_keywords == 0
        assert instance.active_keywords == 0
    
    def test_period_validation(self):
        """Testa validação de período"""
        # Teste com período inválido (fim antes do início)
        with pytest.raises(Exception):
            CategoryROI(
                categoria_id=1,
                periodo_inicio=date(2024, 1, 31),
                periodo_fim=date(2024, 1, 1)
            )
    
    def test_roi_calculation_consistency(self, sample_category_roi_data):
        """Testa consistência do cálculo de ROI"""
        instance = CategoryROI(**sample_category_roi_data)
        
        # Verifica se total_roi = total_revenue - total_cost
        expected_total_roi = 50000.0 - 15000.0
        assert instance.total_roi == expected_total_roi
        
        # Verifica se roi_percentage = (total_roi / total_cost) * 100
        expected_roi_percentage = (35000.0 / 15000.0) * 100
        assert abs(instance.roi_percentage - expected_roi_percentage) < 0.01
    
    def test_active_keywords_validation(self, sample_category_roi_data):
        """Testa validação de keywords ativas"""
        data = sample_category_roi_data.copy()
        data['active_keywords'] = 150  # Mais que total_keywords
        
        with pytest.raises(Exception):
            CategoryROI(**data)
    
    def test_repr_method(self, category_roi_instance):
        """Testa método __repr__"""
        repr_str = repr(category_roi_instance)
        assert 'CategoryROI' in repr_str
        assert '1' in repr_str
        assert '233.33%' in repr_str


class TestConversionTracking:
    """Testes para ConversionTracking"""
    
    @pytest.fixture
    def sample_conversion_data(self):
        """Dados de exemplo para ConversionTracking"""
        return {
            'keyword': 'omni keywords finder',
            'categoria_id': 1,
            'conversion_id': 'conv_001_20240127',
            'conversion_type': 'sale',
            'conversion_value': 299.99,
            'conversion_currency': 'BRL',
            'user_id': 'user_123',
            'session_id': 'sess_456',
            'source': 'organic',
            'medium': 'organic',
            'campaign': 'omni_keywords_2024'
        }
    
    @pytest.fixture
    def conversion_instance(self, sample_conversion_data):
        """Instância de ConversionTracking para testes"""
        return ConversionTracking(**sample_conversion_data)
    
    def test_initialization(self, sample_conversion_data):
        """Testa inicialização básica de ConversionTracking"""
        instance = ConversionTracking(**sample_conversion_data)
        
        assert instance.keyword == 'omni keywords finder'
        assert instance.categoria_id == 1
        assert instance.conversion_id == 'conv_001_20240127'
        assert instance.conversion_type == 'sale'
        assert instance.conversion_value == 299.99
        assert instance.conversion_currency == 'BRL'
        assert instance.user_id == 'user_123'
        assert instance.session_id == 'sess_456'
        assert instance.source == 'organic'
        assert instance.medium == 'organic'
        assert instance.campaign == 'omni_keywords_2024'
    
    def test_conversion_type_validation(self):
        """Testa validação de tipos de conversão"""
        valid_types = ['sale', 'lead', 'signup']
        
        for conv_type in valid_types:
            instance = ConversionTracking(
                keyword='test',
                categoria_id=1,
                conversion_id='test_001',
                conversion_type=conv_type,
                conversion_value=100.0
            )
            assert instance.conversion_type == conv_type
    
    def test_conversion_value_validation(self):
        """Testa validação de valor de conversão"""
        # Teste com valor negativo
        with pytest.raises(Exception):
            ConversionTracking(
                keyword='test',
                categoria_id=1,
                conversion_id='test_001',
                conversion_type='sale',
                conversion_value=-100.0
            )
        
        # Teste com valor zero
        with pytest.raises(Exception):
            ConversionTracking(
                keyword='test',
                categoria_id=1,
                conversion_id='test_001',
                conversion_type='sale',
                conversion_value=0.0
            )
    
    def test_currency_validation(self):
        """Testa validação de moeda"""
        # Teste com moeda inválida
        with pytest.raises(Exception):
            ConversionTracking(
                keyword='test',
                categoria_id=1,
                conversion_id='test_001',
                conversion_type='sale',
                conversion_value=100.0,
                conversion_currency='INVALID'
            )
    
    def test_unique_conversion_id(self, sample_conversion_data):
        """Testa unicidade do conversion_id"""
        instance1 = ConversionTracking(**sample_conversion_data)
        
        # Tentativa de criar com mesmo ID deve falhar
        with pytest.raises(Exception):
            ConversionTracking(**sample_conversion_data)
    
    def test_timestamps_auto_generation(self, sample_conversion_data):
        """Testa geração automática de timestamps"""
        instance = ConversionTracking(**sample_conversion_data)
        
        assert instance.data_conversao is not None
        assert instance.data_criacao is not None
        assert isinstance(instance.data_conversao, datetime)
        assert isinstance(instance.data_criacao, datetime)
    
    def test_repr_method(self, conversion_instance):
        """Testa método __repr__"""
        repr_str = repr(conversion_instance)
        assert 'ConversionTracking' in repr_str
        assert 'omni keywords finder' in repr_str
        assert '299.99' in repr_str


class TestRankingHistory:
    """Testes para RankingHistory"""
    
    @pytest.fixture
    def sample_ranking_data(self):
        """Dados de exemplo para RankingHistory"""
        return {
            'keyword': 'omni keywords finder',
            'categoria_id': 1,
            'ranking_position': 5,
            'search_engine': 'google',
            'device_type': 'desktop',
            'search_volume': 1000,
            'click_through_rate': 3.2,
            'data_ranking': date(2024, 1, 27)
        }
    
    @pytest.fixture
    def ranking_instance(self, sample_ranking_data):
        """Instância de RankingHistory para testes"""
        return RankingHistory(**sample_ranking_data)
    
    def test_initialization(self, sample_ranking_data):
        """Testa inicialização básica de RankingHistory"""
        instance = RankingHistory(**sample_ranking_data)
        
        assert instance.keyword == 'omni keywords finder'
        assert instance.categoria_id == 1
        assert instance.ranking_position == 5
        assert instance.search_engine == 'google'
        assert instance.device_type == 'desktop'
        assert instance.search_volume == 1000
        assert instance.click_through_rate == 3.2
        assert instance.data_ranking == date(2024, 1, 27)
    
    def test_default_values(self):
        """Testa valores padrão"""
        instance = RankingHistory(
            keyword='test',
            categoria_id=1,
            ranking_position=10,
            data_ranking=date(2024, 1, 27)
        )
        
        assert instance.search_engine == 'google'
        assert instance.device_type == 'desktop'
    
    def test_ranking_position_validation(self):
        """Testa validação de posição de ranking"""
        # Teste com posição zero
        with pytest.raises(Exception):
            RankingHistory(
                keyword='test',
                categoria_id=1,
                ranking_position=0,
                data_ranking=date(2024, 1, 27)
            )
        
        # Teste com posição negativa
        with pytest.raises(Exception):
            RankingHistory(
                keyword='test',
                categoria_id=1,
                ranking_position=-1,
                data_ranking=date(2024, 1, 27)
            )
    
    def test_device_type_validation(self):
        """Testa validação de tipo de dispositivo"""
        valid_devices = ['desktop', 'mobile', 'tablet']
        
        for device in valid_devices:
            instance = RankingHistory(
                keyword='test',
                categoria_id=1,
                ranking_position=10,
                device_type=device,
                data_ranking=date(2024, 1, 27)
            )
            assert instance.device_type == device
    
    def test_search_engine_validation(self):
        """Testa validação de motor de busca"""
        valid_engines = ['google', 'bing', 'yahoo']
        
        for engine in valid_engines:
            instance = RankingHistory(
                keyword='test',
                categoria_id=1,
                ranking_position=10,
                search_engine=engine,
                data_ranking=date(2024, 1, 27)
            )
            assert instance.search_engine == engine
    
    def test_repr_method(self, ranking_instance):
        """Testa método __repr__"""
        repr_str = repr(ranking_instance)
        assert 'RankingHistory' in repr_str
        assert 'omni keywords finder' in repr_str
        assert '5' in repr_str


class TestPredictiveInsights:
    """Testes para PredictiveInsights"""
    
    @pytest.fixture
    def sample_predictive_data(self):
        """Dados de exemplo para PredictiveInsights"""
        return {
            'keyword': 'omni keywords finder',
            'categoria_id': 1,
            'predicted_ranking_30d': 3,
            'predicted_ranking_60d': 2,
            'predicted_ranking_90d': 1,
            'predicted_search_volume_30d': 1200,
            'predicted_search_volume_60d': 1400,
            'predicted_search_volume_90d': 1600,
            'predicted_conversion_rate_30d': 2.5,
            'predicted_conversion_rate_60d': 2.8,
            'predicted_conversion_rate_90d': 3.0,
            'confidence_score': 0.85,
            'model_version': 'v2.1.0',
            'recommendations': {
                'action': 'increase_content',
                'priority': 'high',
                'estimated_impact': '15% improvement'
            },
            'risk_score': 0.15
        }
    
    @pytest.fixture
    def predictive_instance(self, sample_predictive_data):
        """Instância de PredictiveInsights para testes"""
        return PredictiveInsights(**sample_predictive_data)
    
    def test_initialization(self, sample_predictive_data):
        """Testa inicialização básica de PredictiveInsights"""
        instance = PredictiveInsights(**sample_predictive_data)
        
        assert instance.keyword == 'omni keywords finder'
        assert instance.categoria_id == 1
        assert instance.predicted_ranking_30d == 3
        assert instance.predicted_ranking_60d == 2
        assert instance.predicted_ranking_90d == 1
        assert instance.predicted_search_volume_30d == 1200
        assert instance.predicted_search_volume_60d == 1400
        assert instance.predicted_search_volume_90d == 1600
        assert instance.predicted_conversion_rate_30d == 2.5
        assert instance.predicted_conversion_rate_60d == 2.8
        assert instance.predicted_conversion_rate_90d == 3.0
        assert instance.confidence_score == 0.85
        assert instance.model_version == 'v2.1.0'
        assert instance.risk_score == 0.15
    
    def test_confidence_score_validation(self):
        """Testa validação de score de confiança"""
        # Teste com score válido
        instance = PredictiveInsights(
            keyword='test',
            categoria_id=1,
            confidence_score=0.75
        )
        assert instance.confidence_score == 0.75
        
        # Teste com score fora do range
        with pytest.raises(Exception):
            PredictiveInsights(
                keyword='test',
                categoria_id=1,
                confidence_score=1.5
            )
        
        with pytest.raises(Exception):
            PredictiveInsights(
                keyword='test',
                categoria_id=1,
                confidence_score=-0.1
            )
    
    def test_risk_score_validation(self):
        """Testa validação de score de risco"""
        # Teste com score válido
        instance = PredictiveInsights(
            keyword='test',
            categoria_id=1,
            risk_score=0.25
        )
        assert instance.risk_score == 0.25
        
        # Teste com score fora do range
        with pytest.raises(Exception):
            PredictiveInsights(
                keyword='test',
                categoria_id=1,
                risk_score=1.5
            )
    
    def test_recommendations_json_storage(self, sample_predictive_data):
        """Testa armazenamento de recomendações em JSON"""
        instance = PredictiveInsights(**sample_predictive_data)
        
        assert instance.recommendations is not None
        assert isinstance(instance.recommendations, dict)
        assert instance.recommendations['action'] == 'increase_content'
        assert instance.recommendations['priority'] == 'high'
        assert instance.recommendations['estimated_impact'] == '15% improvement'
    
    def test_prediction_trends(self, sample_predictive_data):
        """Testa tendências das previsões"""
        instance = PredictiveInsights(**sample_predictive_data)
        
        # Verifica se rankings melhoram ao longo do tempo
        assert instance.predicted_ranking_30d > instance.predicted_ranking_60d
        assert instance.predicted_ranking_60d > instance.predicted_ranking_90d
        
        # Verifica se volumes aumentam ao longo do tempo
        assert instance.predicted_search_volume_30d < instance.predicted_search_volume_60d
        assert instance.predicted_search_volume_60d < instance.predicted_search_volume_90d
        
        # Verifica se taxas de conversão aumentam ao longo do tempo
        assert instance.predicted_conversion_rate_30d < instance.predicted_conversion_rate_60d
        assert instance.predicted_conversion_rate_60d < instance.predicted_conversion_rate_90d
    
    def test_repr_method(self, predictive_instance):
        """Testa método __repr__"""
        repr_str = repr(predictive_instance)
        assert 'PredictiveInsights' in repr_str
        assert 'omni keywords finder' in repr_str


class TestBusinessReport:
    """Testes para BusinessReport"""
    
    @pytest.fixture
    def sample_report_data(self):
        """Dados de exemplo para BusinessReport"""
        return {
            'report_type': 'monthly',
            'report_period': '2024-01',
            'report_data': {
                'keywords_analyzed': 150,
                'top_performers': ['omni keywords', 'keyword finder', 'seo tools'],
                'improvements': {
                    'avg_ranking': 15.5,
                    'conversion_rate': 2.8,
                    'roi': 180.0
                }
            },
            'summary': 'Relatório mensal de performance de keywords',
            'total_revenue': 75000.0,
            'total_cost': 25000.0,
            'total_roi': 50000.0,
            'total_conversions': 1250,
            'avg_conversion_rate': 2.8,
            'status': 'generated',
            'recipients': ['admin@omni.com', 'manager@omni.com']
        }
    
    @pytest.fixture
    def report_instance(self, sample_report_data):
        """Instância de BusinessReport para testes"""
        return BusinessReport(**sample_report_data)
    
    def test_initialization(self, sample_report_data):
        """Testa inicialização básica de BusinessReport"""
        instance = BusinessReport(**sample_report_data)
        
        assert instance.report_type == 'monthly'
        assert instance.report_period == '2024-01'
        assert instance.summary == 'Relatório mensal de performance de keywords'
        assert instance.total_revenue == 75000.0
        assert instance.total_cost == 25000.0
        assert instance.total_roi == 50000.0
        assert instance.total_conversions == 1250
        assert instance.avg_conversion_rate == 2.8
        assert instance.status == 'generated'
    
    def test_report_type_validation(self):
        """Testa validação de tipo de relatório"""
        valid_types = ['daily', 'weekly', 'monthly', 'quarterly']
        
        for report_type in valid_types:
            instance = BusinessReport(
                report_type=report_type,
                report_period='2024-01',
                report_data={}
            )
            assert instance.report_type == report_type
    
    def test_status_validation(self):
        """Testa validação de status"""
        valid_statuses = ['generated', 'sent', 'archived']
        
        for status in valid_statuses:
            instance = BusinessReport(
                report_type='monthly',
                report_period='2024-01',
                report_data={},
                status=status
            )
            assert instance.status == status
    
    def test_default_values(self):
        """Testa valores padrão"""
        instance = BusinessReport(
            report_type='monthly',
            report_period='2024-01',
            report_data={}
        )
        
        assert instance.total_revenue == 0.0
        assert instance.total_cost == 0.0
        assert instance.total_roi == 0.0
        assert instance.total_conversions == 0
        assert instance.avg_conversion_rate == 0.0
        assert instance.status == 'generated'
    
    def test_report_data_json_storage(self, sample_report_data):
        """Testa armazenamento de dados do relatório em JSON"""
        instance = BusinessReport(**sample_report_data)
        
        assert instance.report_data is not None
        assert isinstance(instance.report_data, dict)
        assert instance.report_data['keywords_analyzed'] == 150
        assert 'omni keywords' in instance.report_data['top_performers']
        assert instance.report_data['improvements']['avg_ranking'] == 15.5
    
    def test_recipients_json_storage(self, sample_report_data):
        """Testa armazenamento de destinatários em JSON"""
        instance = BusinessReport(**sample_report_data)
        
        assert instance.recipients is not None
        assert isinstance(instance.recipients, list)
        assert 'admin@omni.com' in instance.recipients
        assert 'manager@omni.com' in instance.recipients
    
    def test_roi_calculation_consistency(self, sample_report_data):
        """Testa consistência do cálculo de ROI"""
        instance = BusinessReport(**sample_report_data)
        
        # Verifica se total_roi = total_revenue - total_cost
        expected_total_roi = 75000.0 - 25000.0
        assert instance.total_roi == expected_total_roi
    
    def test_timestamps_auto_generation(self, sample_report_data):
        """Testa geração automática de timestamps"""
        instance = BusinessReport(**sample_report_data)
        
        assert instance.data_geracao is not None
        assert isinstance(instance.data_geracao, datetime)
        assert instance.data_envio is None  # Deve ser None inicialmente
    
    def test_repr_method(self, report_instance):
        """Testa método __repr__"""
        repr_str = repr(report_instance)
        assert 'BusinessReport' in repr_str
        assert 'monthly' in repr_str
        assert '2024-01' in repr_str


class TestBusinessMetricsIntegration:
    """Testes de integração para Business Metrics Models"""
    
    def test_keyword_metrics_to_category_roi_relationship(self):
        """Testa relacionamento entre KeywordMetrics e CategoryROI"""
        # Simula criação de métricas de keywords
        keyword_metrics = KeywordMetrics(
            keyword='test keyword',
            categoria_id=1,
            revenue_generated=1000.0,
            cost_incurred=300.0
        )
        
        # Simula cálculo de ROI da categoria
        category_roi = CategoryROI(
            categoria_id=1,
            total_revenue=1000.0,
            total_cost=300.0,
            total_roi=700.0,
            roi_percentage=233.33,
            periodo_inicio=date(2024, 1, 1),
            periodo_fim=date(2024, 1, 31)
        )
        
        assert keyword_metrics.categoria_id == category_roi.categoria_id
        assert keyword_metrics.revenue_generated == category_roi.total_revenue
        assert keyword_metrics.cost_incurred == category_roi.total_cost
    
    def test_conversion_tracking_to_keyword_metrics_relationship(self):
        """Testa relacionamento entre ConversionTracking e KeywordMetrics"""
        # Simula tracking de conversão
        conversion = ConversionTracking(
            keyword='test keyword',
            categoria_id=1,
            conversion_id='conv_001',
            conversion_type='sale',
            conversion_value=299.99
        )
        
        # Simula métricas da keyword
        keyword_metrics = KeywordMetrics(
            keyword='test keyword',
            categoria_id=1,
            conversions=1,
            revenue_generated=299.99
        )
        
        assert conversion.keyword == keyword_metrics.keyword
        assert conversion.categoria_id == keyword_metrics.categoria_id
        assert conversion.conversion_value == keyword_metrics.revenue_generated


class TestBusinessMetricsErrorHandling:
    """Testes de tratamento de erro para Business Metrics Models"""
    
    def test_invalid_roi_calculation(self):
        """Testa cálculo de ROI com valores inválidos"""
        # Teste com custo zero
        with pytest.raises(ZeroDivisionError):
            keyword_metrics = KeywordMetrics(
                keyword='test',
                categoria_id=1,
                revenue_generated=1000.0,
                cost_incurred=0.0
            )
            # Tentativa de calcular ROI com custo zero
    
    def test_invalid_ranking_improvement(self):
        """Testa cálculo de melhoria de ranking com valores inválidos"""
        # Teste com ranking anterior zero
        with pytest.raises(ZeroDivisionError):
            keyword_metrics = KeywordMetrics(
                keyword='test',
                categoria_id=1,
                current_ranking=5,
                previous_ranking=0
            )
            # Tentativa de calcular melhoria com ranking anterior zero
    
    def test_invalid_conversion_data(self):
        """Testa dados de conversão inválidos"""
        # Teste com valor de conversão negativo
        with pytest.raises(ValueError):
            ConversionTracking(
                keyword='test',
                categoria_id=1,
                conversion_id='conv_001',
                conversion_type='sale',
                conversion_value=-100.0
            )


class TestBusinessMetricsPerformance:
    """Testes de performance para Business Metrics Models"""
    
    def test_large_dataset_handling(self):
        """Testa manipulação de grandes volumes de dados"""
        # Simula criação de múltiplas instâncias
        keyword_metrics_list = []
        
        for i in range(1000):
            metrics = KeywordMetrics(
                keyword=f'keyword_{i}',
                categoria_id=1,
                search_volume=1000 + i,
                current_ranking=10 + (i % 20)
            )
            keyword_metrics_list.append(metrics)
        
        assert len(keyword_metrics_list) == 1000
        
        # Verifica se todas as instâncias foram criadas corretamente
        for i, metrics in enumerate(keyword_metrics_list):
            assert metrics.keyword == f'keyword_{i}'
            assert metrics.search_volume == 1000 + i
    
    def test_json_serialization_performance(self):
        """Testa performance de serialização JSON"""
        # Teste com dados complexos
        complex_data = {
            'keywords_analyzed': 1000,
            'top_performers': [f'keyword_{i}' for i in range(100)],
            'improvements': {
                'avg_ranking': 15.5,
                'conversion_rate': 2.8,
                'roi': 180.0,
                'detailed_metrics': {
                    'organic_traffic': 50000,
                    'paid_traffic': 25000,
                    'conversions': 1500
                }
            }
        }
        
        report = BusinessReport(
            report_type='monthly',
            report_period='2024-01',
            report_data=complex_data
        )
        
        # Verifica se a serialização funciona corretamente
        assert report.report_data == complex_data
        assert len(report.report_data['top_performers']) == 100 