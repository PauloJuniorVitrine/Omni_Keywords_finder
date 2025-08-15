import pytest
from unittest.mock import MagicMock, patch
from myapp.api.advanced_analytics import AdvancedAnalyticsAPI, DataAnalyzer, PredictionEngine, ReportGenerator

@pytest.fixture
def analytics_api():
    return AdvancedAnalyticsAPI()

@pytest.fixture
def sample_data():
    return [
        {'date': '2024-01-01', 'revenue': 1000, 'users': 50, 'conversion_rate': 0.05},
        {'date': '2024-01-02', 'revenue': 1200, 'users': 60, 'conversion_rate': 0.06},
        {'date': '2024-01-03', 'revenue': 800, 'users': 40, 'conversion_rate': 0.04},
        {'date': '2024-01-04', 'revenue': 1500, 'users': 75, 'conversion_rate': 0.08},
        {'date': '2024-01-05', 'revenue': 1100, 'users': 55, 'conversion_rate': 0.05}
    ]

# 1. Teste de análise de dados
def test_data_analysis(analytics_api, sample_data):
    analyzer = DataAnalyzer()
    
    # Análise estatística básica
    basic_stats = analyzer.calculate_basic_statistics(sample_data, 'revenue')
    assert basic_stats['mean'] == 1120
    assert basic_stats['median'] == 1100
    assert basic_stats['std_dev'] > 0
    assert 'min' in basic_stats
    assert 'max' in basic_stats
    
    # Análise de tendências
    trend_analysis = analyzer.analyze_trends(sample_data, 'revenue')
    assert 'trend_direction' in trend_analysis
    assert 'trend_strength' in trend_analysis
    assert 'seasonality' in trend_analysis
    
    # Análise de correlação
    correlation_analysis = analyzer.analyze_correlations(sample_data, ['revenue', 'users', 'conversion_rate'])
    assert 'revenue_users' in correlation_analysis
    assert 'revenue_conversion_rate' in correlation_analysis
    assert all(-1 <= corr <= 1 for corr in correlation_analysis.values())

# 2. Teste de predições
def test_predictions(analytics_api, sample_data):
    predictor = PredictionEngine()
    
    # Predição de séries temporais
    time_series_prediction = predictor.predict_time_series(sample_data, 'revenue', periods=3)
    assert len(time_series_prediction['predictions']) == 3
    assert 'confidence_intervals' in time_series_prediction
    assert 'model_accuracy' in time_series_prediction
    
    # Predição de classificação
    classification_data = [
        {'features': [1, 2, 3], 'target': 0},
        {'features': [4, 5, 6], 'target': 1},
        {'features': [7, 8, 9], 'target': 0}
    ]
    classification_prediction = predictor.predict_classification(classification_data, [2, 3, 4])
    assert 'predicted_class' in classification_prediction
    assert 'confidence' in classification_prediction
    
    # Predição de regressão
    regression_prediction = predictor.predict_regression(sample_data, 'revenue', ['users', 'conversion_rate'])
    assert 'predicted_value' in regression_prediction
    assert 'r_squared' in regression_prediction

# 3. Teste de relatórios
def test_report_generation(analytics_api, sample_data):
    generator = ReportGenerator()
    
    # Gerar relatório executivo
    executive_report = generator.generate_executive_report(sample_data)
    assert 'summary' in executive_report
    assert 'key_insights' in executive_report
    assert 'recommendations' in executive_report
    assert 'visualizations' in executive_report
    
    # Gerar relatório técnico
    technical_report = generator.generate_technical_report(sample_data)
    assert 'methodology' in technical_report
    assert 'statistical_analysis' in technical_report
    assert 'model_performance' in technical_report
    assert 'data_quality' in technical_report
    
    # Gerar dashboard
    dashboard = generator.generate_dashboard(sample_data)
    assert 'metrics' in dashboard
    assert 'charts' in dashboard
    assert 'filters' in dashboard

# 4. Teste de exportação
def test_data_export(analytics_api, sample_data):
    generator = ReportGenerator()
    
    # Exportar para CSV
    csv_data = generator.export_to_csv(sample_data)
    assert 'date,revenue,users,conversion_rate' in csv_data
    assert '2024-01-01,1000,50,0.05' in csv_data
    
    # Exportar para JSON
    json_data = generator.export_to_json(sample_data)
    assert isinstance(json_data, dict)
    assert 'data' in json_data
    assert 'metadata' in json_data
    
    # Exportar para Excel com múltiplas abas
    excel_data = generator.export_to_excel(sample_data)
    assert excel_data['format'] == 'excel'
    assert 'sheets' in excel_data
    assert len(excel_data['sheets']) > 1

# 5. Teste de casos edge
def test_edge_cases(analytics_api):
    analyzer = DataAnalyzer()
    
    # Teste com dados vazios
    empty_data = []
    with pytest.raises(ValueError):
        analyzer.calculate_basic_statistics(empty_data, 'revenue')
    
    # Teste com dados insuficientes
    insufficient_data = [{'revenue': 100}]
    with pytest.raises(ValueError):
        analyzer.analyze_trends(insufficient_data, 'revenue')
    
    # Teste com dados nulos
    null_data = [{'revenue': None, 'users': 50}]
    with pytest.raises(ValueError):
        analyzer.calculate_basic_statistics(null_data, 'revenue')

# 6. Teste de performance
def test_analytics_performance(analytics_api, sample_data, benchmark):
    analyzer = DataAnalyzer()
    
    def analyze_data_operation():
        return analyzer.calculate_basic_statistics(sample_data, 'revenue')
    
    benchmark(analyze_data_operation)

# 7. Teste de integração
def test_integration_with_ml_models(analytics_api, sample_data):
    predictor = PredictionEngine()
    
    # Integração com modelo de ML
    with patch('myapp.ml.ModelManager') as mock_ml:
        mock_ml.return_value.predict.return_value = {'prediction': 1200, 'confidence': 0.85}
        
        result = predictor.predict_with_ml_model(sample_data, 'revenue')
        assert result['prediction'] == 1200
        assert result['confidence'] == 0.85

# 8. Teste de configuração
def test_configuration_management(analytics_api):
    # Configurar algoritmos de análise
    algorithm_config = analytics_api.configure_algorithms({
        'time_series': 'arima',
        'classification': 'random_forest',
        'regression': 'linear_regression'
    })
    assert algorithm_config['time_series'] == 'arima'
    
    # Configurar parâmetros de modelo
    model_config = analytics_api.configure_model_parameters({
        'prediction_horizon': 30,
        'confidence_level': 0.95,
        'min_data_points': 10
    })
    assert model_config['prediction_horizon'] == 30

# 9. Teste de logs
def test_logging_functionality(analytics_api, sample_data, caplog):
    analyzer = DataAnalyzer()
    
    with caplog.at_level('INFO'):
        analyzer.calculate_basic_statistics(sample_data, 'revenue')
    
    assert any('Analysis completed' in m for m in caplog.messages)
    assert any('revenue' in m for m in caplog.messages)
    
    # Verificar logs de erro
    with caplog.at_level('ERROR'):
        try:
            analyzer.calculate_basic_statistics([], 'revenue')
        except:
            pass
    
    assert any('Insufficient data' in m for m in caplog.messages)

# 10. Teste de métricas
def test_metrics_monitoring(analytics_api, sample_data):
    analyzer = DataAnalyzer()
    
    # Monitorar performance das análises
    analysis_metrics = analyzer.monitor_analysis_performance('2024-01-01', '2024-01-31')
    assert 'total_analyses' in analysis_metrics
    assert 'avg_processing_time' in analysis_metrics
    assert 'accuracy_scores' in analysis_metrics
    assert 'model_performance' in analysis_metrics
    
    # Monitorar qualidade dos dados
    data_quality_metrics = analyzer.monitor_data_quality(sample_data)
    assert 'completeness' in data_quality_metrics
    assert 'accuracy' in data_quality_metrics
    assert 'consistency' in data_quality_metrics
    assert 'timeliness' in data_quality_metrics 