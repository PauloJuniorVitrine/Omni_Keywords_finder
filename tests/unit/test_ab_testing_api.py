import pytest
from unittest.mock import MagicMock, patch
from myapp.api.ab_testing import ABTestingAPI, ExperimentManager, TrafficDistributor, MetricsCollector

@pytest.fixture
def ab_testing_api():
    return ABTestingAPI()

@pytest.fixture
def sample_experiment():
    return {
        'name': 'button_color_test',
        'description': 'Test different button colors for conversion',
        'variants': [
            {'name': 'control', 'traffic_percentage': 50, 'config': {'color': 'blue'}},
            {'name': 'variant_a', 'traffic_percentage': 50, 'config': {'color': 'green'}}
        ],
        'metrics': ['click_rate', 'conversion_rate'],
        'duration_days': 14
    }

# 1. Teste de criação de experimentos
def test_experiment_creation(ab_testing_api, sample_experiment):
    experiment_manager = ExperimentManager()
    
    # Criar experimento
    experiment = experiment_manager.create_experiment(sample_experiment)
    assert experiment['name'] == 'button_color_test'
    assert experiment['id'] is not None
    assert experiment['status'] == 'draft'
    assert len(experiment['variants']) == 2
    
    # Verificar experimento criado
    created_experiment = experiment_manager.get_experiment(experiment['id'])
    assert created_experiment['description'] == 'Test different button colors for conversion'
    assert created_experiment['duration_days'] == 14

# 2. Teste de distribuição de tráfego
def test_traffic_distribution(ab_testing_api, sample_experiment):
    distributor = TrafficDistributor()
    experiment_manager = ExperimentManager()
    
    # Criar experimento primeiro
    experiment = experiment_manager.create_experiment(sample_experiment)
    
    # Distribuir tráfego
    for i in range(100):
        variant = distributor.assign_variant(experiment['id'], f'user_{i}')
        assert variant in ['control', 'variant_a']
    
    # Verificar distribuição
    distribution = distributor.get_traffic_distribution(experiment['id'])
    assert 'control' in distribution
    assert 'variant_a' in distribution
    assert sum(distribution.values()) == 100

# 3. Teste de coleta de métricas
def test_metrics_collection(ab_testing_api, sample_experiment):
    collector = MetricsCollector()
    experiment_manager = ExperimentManager()
    
    # Criar experimento
    experiment = experiment_manager.create_experiment(sample_experiment)
    
    # Coletar métricas
    metrics_data = {
        'user_id': 'user123',
        'variant': 'control',
        'event': 'button_click',
        'timestamp': '2024-01-01T10:00:00Z',
        'properties': {'page': 'homepage'}
    }
    
    collection_result = collector.collect_metric(experiment['id'], metrics_data)
    assert collection_result['collected'] is True
    assert collection_result['metric_id'] is not None
    
    # Obter métricas agregadas
    aggregated_metrics = collector.get_aggregated_metrics(experiment['id'])
    assert 'control' in aggregated_metrics
    assert 'variant_a' in aggregated_metrics
    assert 'click_rate' in aggregated_metrics['control']

# 4. Teste de análise de resultados
def test_results_analysis(ab_testing_api, sample_experiment):
    experiment_manager = ExperimentManager()
    
    # Criar experimento
    experiment = experiment_manager.create_experiment(sample_experiment)
    
    # Analisar resultados
    analysis_result = experiment_manager.analyze_results(experiment['id'])
    assert 'statistical_significance' in analysis_result
    assert 'winner' in analysis_result
    assert 'confidence_level' in analysis_result
    assert 'p_value' in analysis_result
    
    # Gerar relatório
    report = experiment_manager.generate_report(experiment['id'])
    assert 'summary' in report
    assert 'detailed_analysis' in report
    assert 'recommendations' in report

# 5. Teste de casos edge
def test_edge_cases(ab_testing_api):
    experiment_manager = ExperimentManager()
    
    # Teste com experimento vazio
    empty_experiment = {}
    with pytest.raises(ValueError):
        experiment_manager.create_experiment(empty_experiment)
    
    # Teste com porcentagens inválidas
    invalid_percentages = {
        'name': 'test',
        'variants': [
            {'name': 'control', 'traffic_percentage': 60},
            {'name': 'variant_a', 'traffic_percentage': 50}
        ]
    }
    with pytest.raises(ValueError):
        experiment_manager.create_experiment(invalid_percentages)
    
    # Teste com experimento inexistente
    with pytest.raises(Exception):
        experiment_manager.get_experiment('nonexistent_id')

# 6. Teste de performance
def test_ab_testing_performance(ab_testing_api, sample_experiment, benchmark):
    experiment_manager = ExperimentManager()
    
    def create_experiment_operation():
        return experiment_manager.create_experiment(sample_experiment)
    
    benchmark(create_experiment_operation)

# 7. Teste de integração
def test_integration_with_analytics_platform(ab_testing_api, sample_experiment):
    experiment_manager = ExperimentManager()
    
    # Integração com plataforma de analytics
    with patch('myapp.analytics.AnalyticsPlatform') as mock_analytics:
        mock_analytics.return_value.track_event.return_value = {'tracked': True}
        
        result = experiment_manager.track_experiment_event(sample_experiment['id'], 'user123', 'click')
        assert result['tracked'] is True

# 8. Teste de configuração
def test_configuration_management(ab_testing_api):
    # Configurar limites de experimentos
    limits_config = ab_testing_api.configure_experiment_limits({
        'max_active_experiments': 10,
        'max_variants_per_experiment': 5,
        'min_traffic_percentage': 5
    })
    assert limits_config['max_active_experiments'] == 10
    
    # Configurar notificações
    notification_config = ab_testing_api.configure_notifications({
        'experiment_started': True,
        'experiment_completed': True,
        'significant_results': True
    })
    assert notification_config['experiment_started'] is True

# 9. Teste de logs
def test_logging_functionality(ab_testing_api, sample_experiment, caplog):
    experiment_manager = ExperimentManager()
    
    with caplog.at_level('INFO'):
        experiment_manager.create_experiment(sample_experiment)
    
    assert any('Experiment created' in m for m in caplog.messages)
    assert any('button_color_test' in m for m in caplog.messages)
    
    # Verificar logs de erro
    with caplog.at_level('ERROR'):
        try:
            experiment_manager.create_experiment({})
        except:
            pass
    
    assert any('Invalid experiment data' in m for m in caplog.messages)

# 10. Teste de métricas
def test_metrics_monitoring(ab_testing_api, sample_experiment):
    experiment_manager = ExperimentManager()
    
    # Monitorar métricas de experimentos
    experiment_metrics = experiment_manager.monitor_experiment_metrics('2024-01-01', '2024-01-31')
    assert 'total_experiments' in experiment_metrics
    assert 'active_experiments' in experiment_metrics
    assert 'completed_experiments' in experiment_metrics
    assert 'avg_experiment_duration' in experiment_metrics
    
    # Monitorar performance do sistema
    system_metrics = experiment_manager.monitor_system_performance()
    assert 'traffic_distribution_time' in system_metrics
    assert 'metrics_collection_rate' in system_metrics
    assert 'analysis_processing_time' in system_metrics 