import pytest
from unittest.mock import MagicMock, patch
from myapp.api.advanced_metrics import AdvancedMetricsAPI, CustomMetricsManager, AggregationEngine, AlertManager

@pytest.fixture
def advanced_metrics_api():
    return AdvancedMetricsAPI()

@pytest.fixture
def sample_metrics_data():
    return [
        {'timestamp': '2024-01-01T10:00:00Z', 'user_id': 'user1', 'action': 'login', 'duration': 2.5},
        {'timestamp': '2024-01-01T10:01:00Z', 'user_id': 'user2', 'action': 'search', 'duration': 1.8},
        {'timestamp': '2024-01-01T10:02:00Z', 'user_id': 'user1', 'action': 'purchase', 'duration': 15.2},
        {'timestamp': '2024-01-01T10:03:00Z', 'user_id': 'user3', 'action': 'login', 'duration': 3.1},
        {'timestamp': '2024-01-01T10:04:00Z', 'user_id': 'user2', 'action': 'purchase', 'duration': 12.8}
    ]

# 1. Teste de métricas customizadas
def test_custom_metrics(advanced_metrics_api, sample_metrics_data):
    metrics_manager = CustomMetricsManager()
    
    # Criar métrica customizada
    custom_metric = {
        'name': 'user_engagement_score',
        'formula': 'avg(duration) * log(count(actions))',
        'description': 'Engagement score based on session duration and action count'
    }
    
    created_metric = metrics_manager.create_custom_metric(custom_metric)
    assert created_metric['name'] == 'user_engagement_score'
    assert created_metric['id'] is not None
    assert created_metric['formula'] == 'avg(duration) * log(count(actions))'
    
    # Calcular métrica customizada
    calculation_result = metrics_manager.calculate_custom_metric(created_metric['id'], sample_metrics_data)
    assert 'value' in calculation_result
    assert 'timestamp' in calculation_result
    assert calculation_result['metric_id'] == created_metric['id']

# 2. Teste de agregação avançada
def test_advanced_aggregation(advanced_metrics_api, sample_metrics_data):
    aggregation_engine = AggregationEngine()
    
    # Agregação por janela de tempo
    time_window_agg = aggregation_engine.aggregate_by_time_window(
        sample_metrics_data, 
        'duration', 
        window_size='5min'
    )
    assert len(time_window_agg) > 0
    assert all('window_start' in agg for agg in time_window_agg)
    assert all('avg_duration' in agg for agg in time_window_agg)
    
    # Agregação por percentil
    percentile_agg = aggregation_engine.aggregate_by_percentile(
        sample_metrics_data, 
        'duration', 
        percentiles=[25, 50, 75, 95]
    )
    assert 'p25' in percentile_agg
    assert 'p50' in percentile_agg
    assert 'p75' in percentile_agg
    assert 'p95' in percentile_agg
    
    # Agregação por grupo
    group_agg = aggregation_engine.aggregate_by_group(
        sample_metrics_data, 
        'action', 
        'duration'
    )
    assert 'login' in group_agg
    assert 'search' in group_agg
    assert 'purchase' in group_agg

# 3. Teste de alertas
def test_alert_management(advanced_metrics_api, sample_metrics_data):
    alert_manager = AlertManager()
    
    # Criar alerta
    alert_config = {
        'name': 'high_duration_alert',
        'condition': 'duration > 10',
        'threshold': 10,
        'severity': 'warning',
        'notification_channels': ['email', 'slack']
    }
    
    created_alert = alert_manager.create_alert(alert_config)
    assert created_alert['name'] == 'high_duration_alert'
    assert created_alert['id'] is not None
    assert created_alert['severity'] == 'warning'
    
    # Verificar alertas
    alert_check = alert_manager.check_alerts(sample_metrics_data)
    assert 'triggered_alerts' in alert_check
    assert 'alert_count' in alert_check
    
    # Processar alertas
    if alert_check['alert_count'] > 0:
        alert_processing = alert_manager.process_alerts(alert_check['triggered_alerts'])
        assert 'sent_notifications' in alert_processing
        assert 'failed_notifications' in alert_processing

# 4. Teste de dashboards
def test_dashboard_management(advanced_metrics_api, sample_metrics_data):
    metrics_manager = CustomMetricsManager()
    
    # Criar dashboard
    dashboard_config = {
        'name': 'User Analytics Dashboard',
        'description': 'Comprehensive user analytics dashboard',
        'widgets': [
            {'type': 'line_chart', 'metric': 'user_engagement_score', 'title': 'Engagement Trend'},
            {'type': 'bar_chart', 'metric': 'action_distribution', 'title': 'Action Distribution'},
            {'type': 'gauge', 'metric': 'avg_duration', 'title': 'Average Duration'}
        ]
    }
    
    created_dashboard = metrics_manager.create_dashboard(dashboard_config)
    assert created_dashboard['name'] == 'User Analytics Dashboard'
    assert created_dashboard['id'] is not None
    assert len(created_dashboard['widgets']) == 3
    
    # Gerar dados do dashboard
    dashboard_data = metrics_manager.generate_dashboard_data(created_dashboard['id'], sample_metrics_data)
    assert 'widgets_data' in dashboard_data
    assert 'last_updated' in dashboard_data
    assert len(dashboard_data['widgets_data']) == 3

# 5. Teste de casos edge
def test_edge_cases(advanced_metrics_api):
    metrics_manager = CustomMetricsManager()
    
    # Teste com métrica vazia
    empty_metric = {}
    with pytest.raises(ValueError):
        metrics_manager.create_custom_metric(empty_metric)
    
    # Teste com fórmula inválida
    invalid_metric = {
        'name': 'test',
        'formula': 'invalid_formula()',
        'description': 'Test'
    }
    with pytest.raises(ValueError):
        metrics_manager.create_custom_metric(invalid_metric)
    
    # Teste com dados insuficientes
    insufficient_data = [{'timestamp': '2024-01-01T10:00:00Z'}]
    with pytest.raises(ValueError):
        metrics_manager.calculate_custom_metric('metric_id', insufficient_data)

# 6. Teste de performance
def test_metrics_performance(advanced_metrics_api, sample_metrics_data, benchmark):
    aggregation_engine = AggregationEngine()
    
    def aggregate_operation():
        return aggregation_engine.aggregate_by_time_window(sample_metrics_data, 'duration', '5min')
    
    benchmark(aggregate_operation)

# 7. Teste de integração
def test_integration_with_monitoring_system(advanced_metrics_api, sample_metrics_data):
    metrics_manager = CustomMetricsManager()
    
    # Integração com sistema de monitoramento
    with patch('myapp.monitoring.MonitoringSystem') as mock_monitoring:
        mock_monitoring.return_value.collect_metrics.return_value = sample_metrics_data
        
        result = metrics_manager.collect_and_process_metrics('user_engagement_score')
        assert len(result['data']) == 5

# 8. Teste de configuração
def test_configuration_management(advanced_metrics_api):
    # Configurar limites de métricas
    limits_config = advanced_metrics_api.configure_metric_limits({
        'max_custom_metrics': 100,
        'max_aggregation_period': '30d',
        'max_alert_thresholds': 50
    })
    assert limits_config['max_custom_metrics'] == 100
    
    # Configurar retenção de dados
    retention_config = advanced_metrics_api.configure_data_retention({
        'raw_metrics_days': 90,
        'aggregated_metrics_days': 365,
        'alert_history_days': 180
    })
    assert retention_config['raw_metrics_days'] == 90

# 9. Teste de logs
def test_logging_functionality(advanced_metrics_api, sample_metrics_data, caplog):
    metrics_manager = CustomMetricsManager()
    
    with caplog.at_level('INFO'):
        metrics_manager.calculate_custom_metric('test_metric_id', sample_metrics_data)
    
    assert any('Custom metric calculated' in m for m in caplog.messages)
    assert any('test_metric_id' in m for m in caplog.messages)
    
    # Verificar logs de erro
    with caplog.at_level('ERROR'):
        try:
            metrics_manager.calculate_custom_metric('invalid_id', [])
        except:
            pass
    
    assert any('Failed to calculate metric' in m for m in caplog.messages)

# 10. Teste de relatórios
def test_report_generation(advanced_metrics_api, sample_metrics_data):
    metrics_manager = CustomMetricsManager()
    
    # Gerar relatório de métricas
    metrics_report = metrics_manager.generate_metrics_report('2024-01-01', '2024-01-31')
    assert 'summary' in metrics_report
    assert 'custom_metrics' in metrics_report
    assert 'performance_analysis' in metrics_report
    assert 'recommendations' in metrics_report
    
    # Gerar relatório de alertas
    alert_report = metrics_manager.generate_alert_report('2024-01-01', '2024-01-31')
    assert 'alert_summary' in alert_report
    assert 'triggered_alerts' in alert_report
    assert 'response_times' in alert_report 