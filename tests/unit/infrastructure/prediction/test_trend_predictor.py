from typing import Dict, List, Optional, Any
"""
🧪 Testes Unitários - Sistema de Predição de Tendências
📊 Testes para TrendPredictor, TimeSeriesAnalyzer e AlertSystem
🔄 Versão: 1.0
📅 Data: 2024-12-19
👤 Autor: Paulo Júnior
🔗 Tracing ID: PREDICTION_20241219_004
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from infrastructure.prediction.trend_predictor import (
    TrendPredictor, TrendPrediction, TrendDirection, ConfidenceLevel,
    predict_keyword_trends
)
from infrastructure.prediction.time_series_analyzer import (
    TimeSeriesAnalyzer, SeasonalityPattern, TrendAnalysis,
    analyze_keyword_timeseries
)
from infrastructure.prediction.alert_system import (
    AlertSystem, Alert, AlertRule, AlertType, AlertSeverity, AlertStatus,
    create_alert_system
)


class TestTrendPredictor:
    """Testes para TrendPredictor"""
    
    @pytest.fixture
    def sample_data(self):
        """Dados de exemplo para testes"""
        dates = pd.date_range(start='2024-01-01', end='2024-12-01', freq='D')
        keywords = ['python', 'javascript', 'machine learning']
        
        data = []
        for date in dates:
            for keyword in keywords:
                # Simula dados com tendência e sazonalidade
                base_value = 100
                trend = (date - dates[0]).days * 0.1
                seasonal = 10 * np.sin(2 * np.pi * date.dayofyear / 365)
                noise = np.random.normal(0, 5)
                
                value = base_value + trend + seasonal + noise
                data.append({
                    'date': date,
                    'keyword': keyword,
                    'value': max(0, value)
                })
        
        return pd.DataFrame(data)
    
    @pytest.fixture
    def predictor(self):
        """Instância do TrendPredictor para testes"""
        config = {
            'min_data_points': 10,
            'prediction_horizon': 7,
            'confidence_threshold': 0.5,
            'alert_thresholds': {
                'high_rise': 0.2,
                'high_fall': -0.2,
                'moderate_rise': 0.1,
                'moderate_fall': -0.1
            }
        }
        return TrendPredictor(config)
    
    def test_init(self, predictor):
        """Testa inicialização do TrendPredictor"""
        assert predictor is not None
        assert predictor.config['min_data_points'] == 10
        assert predictor.config['prediction_horizon'] == 7
        assert len(predictor.predictions_cache) == 0
        assert len(predictor.alerts_history) == 0
    
    def test_default_config(self):
        """Testa configuração padrão"""
        predictor = TrendPredictor()
        assert predictor.config['min_data_points'] == 30
        assert predictor.config['prediction_horizon'] == 30
        assert predictor.config['confidence_threshold'] == 0.6
    
    def test_prepare_data(self, predictor, sample_data):
        """Testa preparação de dados"""
        prepared_data = predictor.prepare_data(sample_data)
        
        assert len(prepared_data) > 0
        assert 'day_of_week' in prepared_data.columns
        assert 'month' in prepared_data.columns
        assert 'quarter' in prepared_data.columns
        assert 'year' in prepared_data.columns
        assert 'is_weekend' in prepared_data.columns
        assert 'value_ma_7' in prepared_data.columns
        assert 'value_ma_30' in prepared_data.columns
        assert 'value_std_7' in prepared_data.columns
        
        # Verifica se não há valores nulos
        assert prepared_data['value'].notna().all()
    
    def test_prepare_data_insufficient_columns(self, predictor):
        """Testa preparação com colunas insuficientes"""
        invalid_data = pd.DataFrame({
            'date': ['2024-01-01'],
            'value': [100]
        })
        
        with pytest.raises(ValueError):
            predictor.prepare_data(invalid_data)
    
    def test_prepare_data_with_outliers(self, predictor):
        """Testa preparação com outliers"""
        data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=50),
            'keyword': ['test'] * 50,
            'value': [100] * 49 + [1000]  # Outlier no final
        })
        
        prepared_data = predictor.prepare_data(data)
        
        # Verifica se outlier foi removido
        assert len(prepared_data) < len(data)
        assert prepared_data['value'].max() < 1000
    
    @patch('infrastructure.prediction.trend_predictor.PROPHET_AVAILABLE', True)
    @patch('infrastructure.prediction.trend_predictor.Prophet')
    def test_train_prophet_model(self, mock_prophet, predictor, sample_data):
        """Testa treinamento do modelo Prophet"""
        # Mock do Prophet
        mock_model = Mock()
        mock_prophet.return_value = mock_model
        
        keyword_data = sample_data[sample_data['keyword'] == 'python']
        model = predictor.train_prophet_model(keyword_data, 'python')
        
        assert model is not None
        mock_model.fit.assert_called_once()
    
    @patch('infrastructure.prediction.trend_predictor.PROPHET_AVAILABLE', False)
    def test_train_prophet_model_unavailable(self, predictor, sample_data):
        """Testa quando Prophet não está disponível"""
        keyword_data = sample_data[sample_data['keyword'] == 'python']
        model = predictor.train_prophet_model(keyword_data, 'python')
        
        assert model is None
    
    def test_train_ml_model(self, predictor, sample_data):
        """Testa treinamento do modelo ML"""
        keyword_data = sample_data[sample_data['keyword'] == 'python']
        model = predictor.train_ml_model(keyword_data, 'python')
        
        assert model is not None
        assert 'python' in predictor.model_performance
        assert 'mae' in predictor.model_performance['python']
        assert 'r2' in predictor.model_performance['python']
    
    def test_train_ml_model_insufficient_data(self, predictor):
        """Testa treinamento com dados insuficientes"""
        data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=5),
            'keyword': ['test'] * 5,
            'value': [100, 110, 120, 130, 140]
        })
        
        model = predictor.train_ml_model(data, 'test')
        assert model is None
    
    def test_predict_trend(self, predictor, sample_data):
        """Testa predição de tendência"""
        keyword_data = sample_data[sample_data['keyword'] == 'python']
        prediction = predictor.predict_trend(keyword_data, 'python', '7d')
        
        assert prediction is not None
        assert isinstance(prediction, TrendPrediction)
        assert prediction.keyword == 'python'
        assert prediction.timeframe == '7d'
        assert prediction.current_value > 0
        assert prediction.predicted_value > 0
        assert 0 <= prediction.confidence <= 1
        assert prediction.direction in TrendDirection
        assert prediction.confidence_level in ConfidenceLevel
    
    def test_predict_trend_insufficient_data(self, predictor):
        """Testa predição com dados insuficientes"""
        data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=5),
            'keyword': ['test'] * 5,
            'value': [100, 110, 120, 130, 140]
        })
        
        prediction = predictor.predict_trend(data, 'test', '7d')
        assert prediction is None
    
    def test_calculate_confidence(self, predictor):
        """Testa cálculo de confiança"""
        data = pd.DataFrame({
            'value': [100, 110, 120, 130, 140, 150, 160, 170, 180, 190]
        })
        
        predictions = [200, 210]
        weights = [0.6, 0.4]
        
        confidence = predictor._calculate_confidence(data, predictions, weights)
        
        assert 0 <= confidence <= 1
    
    def test_determine_direction(self, predictor):
        """Testa determinação de direção"""
        # Tendência de alta
        direction = predictor._determine_direction(100, 120, 0.8)
        assert direction == TrendDirection.RISING
        
        # Tendência de baixa
        direction = predictor._determine_direction(100, 80, 0.8)
        assert direction == TrendDirection.FALLING
        
        # Estável
        direction = predictor._determine_direction(100, 102, 0.8)
        assert direction == TrendDirection.STABLE
        
        # Volátil (baixa confiança)
        direction = predictor._determine_direction(100, 120, 0.2)
        assert direction == TrendDirection.VOLATILE
    
    def test_determine_confidence_level(self, predictor):
        """Testa determinação de nível de confiança"""
        level = predictor._determine_confidence_level(0.9)
        assert level == ConfidenceLevel.HIGH
        
        level = predictor._determine_confidence_level(0.7)
        assert level == ConfidenceLevel.MEDIUM
        
        level = predictor._determine_confidence_level(0.4)
        assert level == ConfidenceLevel.LOW
    
    def test_analyze_factors(self, predictor):
        """Testa análise de fatores"""
        data = pd.DataFrame({
            'day_of_week': [0, 1, 2, 3, 4, 5, 6] * 10,
            'month': [1] * 70,
            'quarter': [1] * 70,
            'year': [2024] * 70,
            'is_weekend': [0, 0, 0, 0, 0, 1, 1] * 10,
            'value_ma_7': [100] * 70,
            'value_ma_30': [100] * 70,
            'value_std_7': [5] * 70,
            'value': [100 + np.random.normal(0, 5) for _ in range(70)]
        })
        
        factors = predictor._analyze_factors(data, 110)
        
        assert isinstance(factors, dict)
        assert 'weekly_seasonality' in factors
        assert 'monthly_seasonality' in factors
        assert 'volatility' in factors
    
    def test_generate_alerts(self, predictor):
        """Testa geração de alertas"""
        predictions = [
            TrendPrediction(
                keyword='python',
                current_value=100,
                predicted_value=150,  # 50% de aumento
                confidence=0.8,
                direction=TrendDirection.RISING,
                confidence_level=ConfidenceLevel.HIGH,
                timeframe='30d'
            ),
            TrendPrediction(
                keyword='javascript',
                current_value=100,
                predicted_value=50,  # 50% de queda
                confidence=0.8,
                direction=TrendDirection.FALLING,
                confidence_level=ConfidenceLevel.HIGH,
                timeframe='30d'
            )
        ]
        
        alerts = predictor.generate_alerts(predictions)
        
        assert len(alerts) > 0
        assert all(alert.keyword in ['python', 'javascript'] for alert in alerts)
    
    def test_get_performance_metrics(self, predictor):
        """Testa obtenção de métricas de performance"""
        # Adiciona dados de teste
        predictor.model_performance['test'] = {'mae': 0.1, 'r2': 0.8}
        predictor.predictions_cache['test_7d'] = {
            'prediction': Mock(confidence=0.8),
            'timestamp': datetime.now()
        }
        
        metrics = predictor.get_performance_metrics()
        
        assert 'model_performance' in metrics
        assert 'total_predictions' in metrics
        assert 'total_alerts' in metrics
        assert 'average_confidence' in metrics
    
    def test_save_load_model(self, predictor, tmp_path):
        """Testa salvamento e carregamento de modelo"""
        # Adiciona dados de teste
        predictor.model_performance['test'] = {'mae': 0.1, 'r2': 0.8}
        
        filepath = tmp_path / "test_model.pkl"
        
        # Salva
        predictor.save_model(str(filepath))
        assert filepath.exists()
        
        # Carrega em nova instância
        new_predictor = TrendPredictor()
        new_predictor.load_model(str(filepath))
        
        assert 'test' in new_predictor.model_performance
        assert new_predictor.model_performance['test']['mae'] == 0.1


class TestTimeSeriesAnalyzer:
    """Testes para TimeSeriesAnalyzer"""
    
    @pytest.fixture
    def sample_series(self):
        """Série temporal de exemplo"""
        dates = pd.date_range(start='2024-01-01', end='2024-12-01', freq='D')
        
        # Série com tendência e sazonalidade
        trend = np.linspace(100, 200, len(dates))
        seasonal = 20 * np.sin(2 * np.pi * np.arange(len(dates)) / 365)
        noise = np.random.normal(0, 5, len(dates))
        
        values = trend + seasonal + noise
        return pd.Series(values, index=dates, name='test_series')
    
    @pytest.fixture
    def analyzer(self):
        """Instância do TimeSeriesAnalyzer para testes"""
        config = {
            'min_periods': {'daily': 7, 'weekly': 28, 'monthly': 90},
            'seasonality_threshold': 0.2,
            'trend_threshold': 0.05,
            'anomaly_threshold': 1.5
        }
        return TimeSeriesAnalyzer(config)
    
    def test_init(self, analyzer):
        """Testa inicialização do TimeSeriesAnalyzer"""
        assert analyzer is not None
        assert analyzer.config['seasonality_threshold'] == 0.2
        assert len(analyzer.analysis_cache) == 0
    
    def test_default_config(self):
        """Testa configuração padrão"""
        analyzer = TimeSeriesAnalyzer()
        assert analyzer.config['seasonality_threshold'] == 0.3
        assert analyzer.config['trend_threshold'] == 0.1
        assert analyzer.config['anomaly_threshold'] == 2.0
    
    def test_analyze_series(self, analyzer, sample_series):
        """Testa análise completa de série"""
        analysis = analyzer.analyze_series(sample_series, 'test')
        
        assert 'basic_stats' in analysis
        assert 'stationarity' in analysis
        assert 'seasonality' in analysis
        assert 'trend' in analysis
        assert 'anomalies' in analysis
        assert 'correlation' in analysis
        assert 'metadata' in analysis
        
        # Verifica cache
        assert len(analyzer.analysis_cache) > 0
    
    def test_analyze_series_short(self, analyzer):
        """Testa análise de série muito curta"""
        short_series = pd.Series([1, 2, 3, 4, 5])
        analysis = analyzer.analyze_series(short_series, 'short')
        
        assert analysis == {}
    
    def test_basic_statistics(self, analyzer, sample_series):
        """Testa estatísticas básicas"""
        stats = analyzer._basic_statistics(sample_series)
        
        assert 'mean' in stats
        assert 'median' in stats
        assert 'std' in stats
        assert 'min' in stats
        assert 'max' in stats
        assert 'skewness' in stats
        assert 'kurtosis' in stats
        assert 'cv' in stats
        assert 'iqr' in stats
        
        assert stats['mean'] > 0
        assert stats['std'] > 0
    
    @patch('infrastructure.prediction.time_series_analyzer.STATSMODELS_AVAILABLE', True)
    @patch('infrastructure.prediction.time_series_analyzer.adfuller')
    @patch('infrastructure.prediction.time_series_analyzer.kpss')
    def test_test_stationarity(self, mock_kpss, mock_adfuller, analyzer, sample_series):
        """Testa teste de estacionariedade"""
        # Mock dos testes
        mock_adfuller.return_value = (0.5, 0.01, 0, {'1%': -3.5, '5%': -2.9, '10%': -2.6}, 100)
        mock_kpss.return_value = (0.3, 0.1, 0, {'1%': 0.7, '5%': 0.5, '10%': 0.3})
        
        result = analyzer._test_stationarity(sample_series)
        
        assert 'adf' in result
        assert 'kpss' in result
        assert 'conclusion' in result
        assert result['adf']['is_stationary'] == True
        assert result['kpss']['is_stationary'] == True
    
    @patch('infrastructure.prediction.time_series_analyzer.STATSMODELS_AVAILABLE', False)
    def test_test_stationarity_unavailable(self, analyzer, sample_series):
        """Testa quando statsmodels não está disponível"""
        result = analyzer._test_stationarity(sample_series)
        assert result['available'] == False
    
    def test_detect_seasonality(self, analyzer, sample_series):
        """Testa detecção de sazonalidade"""
        patterns = analyzer._detect_seasonality(sample_series)
        
        assert isinstance(patterns, list)
        
        if patterns:
            pattern = patterns[0]
            assert isinstance(pattern, SeasonalityPattern)
            assert pattern.type in SeasonalityType
            assert 0 <= pattern.strength <= 1
            assert pattern.period > 0
            assert 0 <= pattern.confidence <= 1
    
    def test_analyze_trend(self, analyzer, sample_series):
        """Testa análise de tendência"""
        trend = analyzer._analyze_trend(sample_series)
        
        assert isinstance(trend, TrendAnalysis)
        assert trend.type in TrendType
        assert isinstance(trend.slope, float)
        assert 0 <= trend.strength <= 1
        assert 0 <= trend.confidence <= 1
        assert isinstance(trend.changepoints, list)
    
    def test_detect_changepoints(self, analyzer, sample_series):
        """Testa detecção de changepoints"""
        changepoints = analyzer._detect_changepoints(sample_series)
        
        assert isinstance(changepoints, list)
        assert all(isinstance(cp, datetime) for cp in changepoints)
    
    @patch('infrastructure.prediction.time_series_analyzer.STATSMODELS_AVAILABLE', True)
    @patch('infrastructure.prediction.time_series_analyzer.seasonal_decompose')
    def test_decompose_series(self, mock_decompose, analyzer, sample_series):
        """Testa decomposição de série"""
        # Mock da decomposição
        mock_result = Mock()
        mock_result.trend = sample_series
        mock_result.seasonal = sample_series * 0.1
        mock_result.resid = sample_series * 0.05
        mock_decompose.return_value = mock_result
        
        decomposition = analyzer._decompose_series(sample_series)
        
        assert decomposition is not None
        assert isinstance(decomposition, TimeSeriesDecomposition)
        assert len(decomposition.trend) == len(sample_series)
        assert len(decomposition.seasonal) == len(sample_series)
        assert len(decomposition.residual) == len(sample_series)
    
    @patch('infrastructure.prediction.time_series_analyzer.STATSMODELS_AVAILABLE', False)
    def test_decompose_series_unavailable(self, analyzer, sample_series):
        """Testa quando statsmodels não está disponível"""
        decomposition = analyzer._decompose_series(sample_series)
        assert decomposition is None
    
    def test_detect_anomalies(self, analyzer, sample_series):
        """Testa detecção de anomalias"""
        anomalies = analyzer._detect_anomalies(sample_series)
        
        assert isinstance(anomalies, AnomalyDetection)
        assert isinstance(anomalies.anomalies, list)
        assert isinstance(anomalies.scores, list)
        assert isinstance(anomalies.threshold, float)
        assert isinstance(anomalies.method, str)
    
    def test_analyze_correlation(self, analyzer, sample_series):
        """Testa análise de correlação"""
        correlations = analyzer._analyze_correlation(sample_series)
        
        assert isinstance(correlations, dict)
        assert all(isinstance(value, float) for value in correlations.values())
    
    def test_get_summary_report(self, analyzer, sample_series):
        """Testa geração de relatório resumido"""
        analysis = analyzer.analyze_series(sample_series, 'test')
        report = analyzer.get_summary_report(analysis)
        
        assert isinstance(report, str)
        assert 'RELATÓRIO DE ANÁLISE TEMPORAL' in report
        assert 'test' in report


class TestAlertSystem:
    """Testes para AlertSystem"""
    
    @pytest.fixture
    def alert_system(self):
        """Instância do AlertSystem para testes"""
        config = {
            'alert_retention_days': 30,
            'max_active_alerts': 100,
            'default_cooldown_minutes': 15,
            'thresholds': {
                'trend_change': {
                    'critical': 0.3,
                    'high': 0.2,
                    'medium': 0.1,
                    'low': 0.05
                }
            }
        }
        return AlertSystem(config)
    
    @pytest.fixture
    def sample_predictions(self):
        """Predições de exemplo para testes"""
        return [
            {
                'keyword': 'python',
                'current_value': 100,
                'predicted_value': 150,  # 50% de aumento
                'confidence': 0.8,
                'timeframe': '30d',
                'metadata': {
                    'anomaly_score': 2.5,
                    'volatility': 1.8,
                    'historical_volatility': 1.0
                }
            },
            {
                'keyword': 'javascript',
                'current_value': 100,
                'predicted_value': 50,  # 50% de queda
                'confidence': 0.7,
                'timeframe': '30d',
                'metadata': {
                    'anomaly_score': 1.5,
                    'volatility': 0.8,
                    'historical_volatility': 1.0
                }
            }
        ]
    
    def test_init(self, alert_system):
        """Testa inicialização do AlertSystem"""
        assert alert_system is not None
        assert alert_system.config['alert_retention_days'] == 30
        assert alert_system.config['max_active_alerts'] == 100
        assert len(alert_system.alert_rules) > 0
        assert len(alert_system.alerts) == 0
    
    def test_default_config(self):
        """Testa configuração padrão"""
        alert_system = AlertSystem()
        assert alert_system.config['alert_retention_days'] == 90
        assert alert_system.config['max_active_alerts'] == 1000
        assert alert_system.config['default_cooldown_minutes'] == 30
    
    def test_add_alert_rule(self, alert_system):
        """Testa adição de regra de alerta"""
        rule = AlertRule(
            name='Test Rule',
            alert_type=AlertType.TREND_CHANGE,
            severity=AlertSeverity.HIGH,
            conditions={'change_percentage': 0.2},
            actions=['email']
        )
        
        initial_count = len(alert_system.alert_rules)
        alert_system.add_alert_rule(rule)
        
        assert len(alert_system.alert_rules) == initial_count + 1
        assert any(r.name == 'Test Rule' for r in alert_system.alert_rules)
    
    def test_add_alert_rule_invalid(self, alert_system):
        """Testa adição de regra inválida"""
        rule = AlertRule(
            name='',  # Nome vazio
            alert_type=AlertType.TREND_CHANGE,
            severity=AlertSeverity.HIGH,
            conditions={},  # Condições vazias
            actions=['email']
        )
        
        with pytest.raises(ValueError):
            alert_system.add_alert_rule(rule)
    
    def test_remove_alert_rule(self, alert_system):
        """Testa remoção de regra de alerta"""
        rule_name = alert_system.alert_rules[0].name
        initial_count = len(alert_system.alert_rules)
        
        alert_system.remove_alert_rule(rule_name)
        
        assert len(alert_system.alert_rules) == initial_count - 1
        assert not any(r.name == rule_name for r in alert_system.alert_rules)
    
    def test_remove_alert_rule_not_found(self, alert_system):
        """Testa remoção de regra inexistente"""
        initial_count = len(alert_system.alert_rules)
        alert_system.remove_alert_rule('NonExistentRule')
        
        assert len(alert_system.alert_rules) == initial_count
    
    @pytest.mark.asyncio
    async def test_evaluate_predictions(self, alert_system, sample_predictions):
        """Testa avaliação de predições"""
        alerts = await alert_system.evaluate_predictions(sample_predictions)
        
        assert isinstance(alerts, list)
        assert len(alerts) > 0
        
        for alert in alerts:
            assert isinstance(alert, Alert)
            assert alert.keyword in ['python', 'javascript']
            assert alert.status == AlertStatus.ACTIVE
            assert alert.timestamp is not None
    
    def test_evaluate_trend_change(self, alert_system):
        """Testa avaliação de mudança de tendência"""
        rule = AlertRule(
            name='Trend Test',
            alert_type=AlertType.TREND_CHANGE,
            severity=AlertSeverity.CRITICAL,
            conditions={'change_percentage': 0.3, 'confidence_min': 0.7},
            actions=['email']
        )
        
        prediction = {
            'keyword': 'python',
            'current_value': 100,
            'predicted_value': 150,  # 50% de aumento
            'confidence': 0.8,
            'timeframe': '30d'
        }
        
        alert = alert_system._evaluate_trend_change(rule, prediction)
        
        assert alert is not None
        assert alert.rule_name == 'Trend Test'
        assert alert.alert_type == AlertType.TREND_CHANGE
        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.keyword == 'python'
    
    def test_evaluate_threshold_breach(self, alert_system):
        """Testa avaliação de violação de threshold"""
        rule = AlertRule(
            name='Threshold Test',
            alert_type=AlertType.THRESHOLD_BREACH,
            severity=AlertSeverity.HIGH,
            conditions={
                'threshold_type': 'absolute',
                'threshold_value': 120,
                'direction': 'above'
            },
            actions=['email']
        )
        
        prediction = {
            'keyword': 'python',
            'current_value': 150,  # Acima do threshold
            'predicted_value': 160,
            'confidence': 0.8
        }
        
        alert = alert_system._evaluate_threshold_breach(rule, prediction)
        
        assert alert is not None
        assert alert.rule_name == 'Threshold Test'
        assert alert.alert_type == AlertType.THRESHOLD_BREACH
    
    def test_evaluate_anomaly(self, alert_system):
        """Testa avaliação de anomalia"""
        rule = AlertRule(
            name='Anomaly Test',
            alert_type=AlertType.ANOMALY_DETECTED,
            severity=AlertSeverity.MEDIUM,
            conditions={'anomaly_score_threshold': 2.0, 'confidence_min': 0.6},
            actions=['email']
        )
        
        prediction = {
            'keyword': 'python',
            'current_value': 100,
            'predicted_value': 110,
            'confidence': 0.7,
            'metadata': {'anomaly_score': 2.5}
        }
        
        alert = alert_system._evaluate_anomaly(rule, prediction)
        
        assert alert is not None
        assert alert.rule_name == 'Anomaly Test'
        assert alert.alert_type == AlertType.ANOMALY_DETECTED
    
    def test_evaluate_volatility(self, alert_system):
        """Testa avaliação de volatilidade"""
        rule = AlertRule(
            name='Volatility Test',
            alert_type=AlertType.VOLATILITY_SPIKE,
            severity=AlertSeverity.HIGH,
            conditions={'volatility_threshold': 1.5},
            actions=['email']
        )
        
        prediction = {
            'keyword': 'python',
            'current_value': 100,
            'predicted_value': 110,
            'confidence': 0.7,
            'metadata': {
                'volatility': 2.0,
                'historical_volatility': 1.0
            }
        }
        
        alert = alert_system._evaluate_volatility(rule, prediction)
        
        assert alert is not None
        assert alert.rule_name == 'Volatility Test'
        assert alert.alert_type == AlertType.VOLATILITY_SPIKE
    
    def test_is_in_cooldown(self, alert_system):
        """Testa verificação de cooldown"""
        keyword = 'python'
        
        # Não está em cooldown inicialmente
        assert not alert_system._is_in_cooldown(keyword)
        
        # Adiciona timestamp de cooldown
        alert_system.cooldown_timestamps[keyword] = datetime.now()
        
        # Está em cooldown
        assert alert_system._is_in_cooldown(keyword)
    
    def test_generate_alert_id(self, alert_system):
        """Testa geração de ID de alerta"""
        alert_id = alert_system._generate_alert_id()
        
        assert isinstance(alert_id, str)
        assert alert_id.startswith('alert_')
        assert len(alert_id) > 10
    
    def test_acknowledge_alert(self, alert_system):
        """Testa reconhecimento de alerta"""
        # Cria alerta de teste
        alert = Alert(
            id='test_alert',
            rule_name='Test Rule',
            alert_type=AlertType.TREND_CHANGE,
            severity=AlertSeverity.HIGH,
            message='Test alert',
            keyword='python',
            current_value=100,
            threshold_value=120,
            confidence=0.8,
            timestamp=datetime.now()
        )
        
        alert_system.alerts.append(alert)
        
        # Reconhece alerta
        alert_system.acknowledge_alert('test_alert', 'test_user')
        
        assert alert.status == AlertStatus.ACKNOWLEDGED
        assert alert.acknowledged_by == 'test_user'
        assert alert.acknowledged_at is not None
    
    def test_resolve_alert(self, alert_system):
        """Testa resolução de alerta"""
        # Cria alerta de teste
        alert = Alert(
            id='test_alert',
            rule_name='Test Rule',
            alert_type=AlertType.TREND_CHANGE,
            severity=AlertSeverity.HIGH,
            message='Test alert',
            keyword='python',
            current_value=100,
            threshold_value=120,
            confidence=0.8,
            timestamp=datetime.now()
        )
        
        alert_system.alerts.append(alert)
        initial_active_count = len(alert_system.alerts)
        
        # Resolve alerta
        alert_system.resolve_alert('test_alert', 'test_user')
        
        assert len(alert_system.alerts) == initial_active_count - 1
        assert len(alert_system.alert_history) == 1
        assert alert_system.alert_history[0].status == AlertStatus.RESOLVED
        assert alert_system.alert_history[0].resolved_at is not None
    
    def test_get_active_alerts(self, alert_system):
        """Testa obtenção de alertas ativos"""
        # Cria alertas de teste
        alert1 = Alert(
            id='alert1',
            rule_name='Rule1',
            alert_type=AlertType.TREND_CHANGE,
            severity=AlertSeverity.HIGH,
            message='Alert 1',
            keyword='python',
            current_value=100,
            threshold_value=120,
            confidence=0.8,
            timestamp=datetime.now()
        )
        
        alert2 = Alert(
            id='alert2',
            rule_name='Rule2',
            alert_type=AlertType.ANOMALY_DETECTED,
            severity=AlertSeverity.MEDIUM,
            message='Alert 2',
            keyword='javascript',
            current_value=100,
            threshold_value=120,
            confidence=0.8,
            timestamp=datetime.now()
        )
        
        alert_system.alerts.extend([alert1, alert2])
        
        # Testa filtros
        high_severity = alert_system.get_active_alerts({'severity': AlertSeverity.HIGH})
        assert len(high_severity) == 1
        assert high_severity[0].id == 'alert1'
        
        python_alerts = alert_system.get_active_alerts({'keyword': 'python'})
        assert len(python_alerts) == 1
        assert python_alerts[0].id == 'alert1'
    
    def test_get_alert_statistics(self, alert_system):
        """Testa obtenção de estatísticas"""
        # Adiciona alertas de teste
        alert1 = Alert(
            id='alert1',
            rule_name='Rule1',
            alert_type=AlertType.TREND_CHANGE,
            severity=AlertSeverity.HIGH,
            message='Alert 1',
            keyword='python',
            current_value=100,
            threshold_value=120,
            confidence=0.8,
            timestamp=datetime.now()
        )
        
        alert_system.alerts.append(alert1)
        
        stats = alert_system.get_alert_statistics()
        
        assert 'total_alerts' in stats
        assert 'active_alerts' in stats
        assert 'resolved_alerts' in stats
        assert 'severity_distribution' in stats
        assert 'type_distribution' in stats
        assert 'status_distribution' in stats
        assert stats['active_alerts'] == 1
    
    def test_export_alerts(self, alert_system, tmp_path):
        """Testa exportação de alertas"""
        # Cria alerta de teste
        alert = Alert(
            id='test_alert',
            rule_name='Test Rule',
            alert_type=AlertType.TREND_CHANGE,
            severity=AlertSeverity.HIGH,
            message='Test alert',
            keyword='python',
            current_value=100,
            threshold_value=120,
            confidence=0.8,
            timestamp=datetime.now()
        )
        
        alert_system.alerts.append(alert)
        
        # Exporta JSON
        json_file = tmp_path / "alerts.json"
        alert_system.export_alerts(str(json_file), 'json')
        assert json_file.exists()
        
        # Exporta CSV
        csv_file = tmp_path / "alerts.csv"
        alert_system.export_alerts(str(csv_file), 'csv')
        assert csv_file.exists()


# Testes de integração
class TestPredictionIntegration:
    """Testes de integração entre componentes"""
    
    @pytest.fixture
    def sample_data(self):
        """Dados de exemplo para testes de integração"""
        dates = pd.date_range(start='2024-01-01', end='2024-12-01', freq='D')
        keywords = ['python', 'javascript']
        
        data = []
        for date in dates:
            for keyword in keywords:
                base_value = 100
                trend = (date - dates[0]).days * 0.1
                seasonal = 10 * np.sin(2 * np.pi * date.dayofyear / 365)
                noise = np.random.normal(0, 5)
                
                value = base_value + trend + seasonal + noise
                data.append({
                    'date': date,
                    'keyword': keyword,
                    'value': max(0, value)
                })
        
        return pd.DataFrame(data)
    
    def test_predict_keyword_trends_integration(self, sample_data):
        """Testa integração da função de conveniência"""
        keywords = ['python', 'javascript']
        
        predictions = predict_keyword_trends(sample_data, keywords, '30d')
        
        assert isinstance(predictions, dict)
        assert len(predictions) > 0
        
        for keyword, prediction in predictions.items():
            assert keyword in keywords
            assert isinstance(prediction, TrendPrediction)
            assert prediction.keyword == keyword
            assert prediction.timeframe == '30d'
    
    def test_analyze_keyword_timeseries_integration(self, sample_data):
        """Testa integração da análise de série temporal"""
        keyword = 'python'
        
        analysis = analyze_keyword_timeseries(sample_data, keyword)
        
        assert isinstance(analysis, dict)
        assert 'basic_stats' in analysis
        assert 'trend' in analysis
        assert 'seasonality' in analysis
    
    def test_create_alert_system_integration(self):
        """Testa integração da criação do sistema de alertas"""
        config = {'max_active_alerts': 50}
        
        alert_system = create_alert_system(config)
        
        assert isinstance(alert_system, AlertSystem)
        assert alert_system.config['max_active_alerts'] == 50


if __name__ == '__main__':
    pytest.main([__file__, '-value']) 