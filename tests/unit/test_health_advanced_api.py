import pytest
from unittest.mock import MagicMock, patch
from myapp.api.health_advanced import HealthAdvancedAPI, ComponentChecker, DependencyMonitor, HealthMetrics

@pytest.fixture
def health_api():
    return HealthAdvancedAPI()

@pytest.fixture
def sample_components():
    return [
        {'name': 'database', 'type': 'database', 'endpoint': 'postgresql://localhost:5432'},
        {'name': 'redis_cache', 'type': 'cache', 'endpoint': 'redis://localhost:6379'},
        {'name': 'api_gateway', 'type': 'service', 'endpoint': 'http://localhost:8000'},
        {'name': 'file_storage', 'type': 'storage', 'endpoint': 's3://bucket'}
    ]

# 1. Teste de health checks de componentes
def test_component_health_checks(health_api, sample_components):
    component_checker = ComponentChecker()
    
    # Verificar saúde de componentes individuais
    for component in sample_components:
        health_status = component_checker.check_component_health(component)
        assert health_status['component_name'] == component['name']
        assert health_status['status'] in ['healthy', 'warning', 'critical', 'unknown']
        assert 'response_time' in health_status
        assert 'last_check' in health_status
    
    # Verificar saúde de todos os componentes
    all_components_health = component_checker.check_all_components(sample_components)
    assert 'overall_status' in all_components_health
    assert 'healthy_components' in all_components_health
    assert 'problematic_components' in all_components_health
    assert 'total_components' in all_components_health

# 2. Teste de health checks de dependências
def test_dependency_health_checks(health_api, sample_components):
    dependency_monitor = DependencyMonitor()
    
    # Verificar dependências
    dependencies = [
        {'name': 'external_api', 'url': 'https://api.external.com/health'},
        {'name': 'payment_gateway', 'url': 'https://payments.gateway.com/status'},
        {'name': 'email_service', 'url': 'https://email.service.com/health'}
    ]
    
    dependency_health = dependency_monitor.check_dependencies(dependencies)
    assert len(dependency_health) == len(dependencies)
    assert all('status' in dep for dep in dependency_health)
    assert all('response_time' in dep for dep in dependency_health)
    
    # Verificar dependências críticas
    critical_deps = dependency_monitor.check_critical_dependencies(dependencies)
    assert 'critical_status' in critical_deps
    assert 'failed_dependencies' in critical_deps

# 3. Teste de métricas de saúde
def test_health_metrics(health_api, sample_components):
    health_metrics = HealthMetrics()
    
    # Coletar métricas de saúde
    metrics = health_metrics.collect_health_metrics(sample_components)
    assert 'uptime_percentage' in metrics
    assert 'avg_response_time' in metrics
    assert 'error_rate' in metrics
    assert 'availability_score' in metrics
    
    # Calcular score de saúde
    health_score = health_metrics.calculate_health_score(sample_components)
    assert 0 <= health_score <= 100
    assert 'score' in health_score
    assert 'factors' in health_score
    assert 'recommendations' in health_score
    
    # Gerar relatório de tendências
    trends = health_metrics.generate_health_trends('2024-01-01', '2024-01-31')
    assert 'trend_data' in trends
    assert 'improvements' in trends
    assert 'degradations' in trends

# 4. Teste de alertas
def test_health_alerts(health_api, sample_components):
    component_checker = ComponentChecker()
    
    # Configurar alertas
    alert_config = {
        'response_time_threshold': 1000,  # ms
        'error_rate_threshold': 0.05,     # 5%
        'uptime_threshold': 0.99          # 99%
    }
    
    # Verificar alertas
    alerts = component_checker.check_health_alerts(sample_components, alert_config)
    assert 'triggered_alerts' in alerts
    assert 'alert_count' in alerts
    assert 'severity_levels' in alerts
    
    # Processar alertas
    if alerts['alert_count'] > 0:
        alert_processing = component_checker.process_health_alerts(alerts['triggered_alerts'])
        assert 'notifications_sent' in alert_processing
        assert 'escalation_level' in alert_processing

# 5. Teste de casos edge
def test_edge_cases(health_api):
    component_checker = ComponentChecker()
    
    # Teste com componentes vazios
    empty_components = []
    health_status = component_checker.check_all_components(empty_components)
    assert health_status['total_components'] == 0
    assert health_status['overall_status'] == 'unknown'
    
    # Teste com endpoint inválido
    invalid_component = {'name': 'invalid', 'endpoint': 'invalid://endpoint'}
    with pytest.raises(Exception):
        component_checker.check_component_health(invalid_component)
    
    # Teste com timeout
    slow_component = {'name': 'slow_service', 'endpoint': 'http://slow.service.com'}
    with patch('requests.get') as mock_request:
        mock_request.side_effect = Exception('Timeout')
        health_status = component_checker.check_component_health(slow_component)
        assert health_status['status'] == 'critical'

# 6. Teste de performance
def test_health_performance(health_api, sample_components, benchmark):
    component_checker = ComponentChecker()
    
    def check_components_operation():
        return component_checker.check_all_components(sample_components)
    
    benchmark(check_components_operation)

# 7. Teste de integração
def test_integration_with_monitoring_system(health_api, sample_components):
    component_checker = ComponentChecker()
    
    # Integração com sistema de monitoramento
    with patch('myapp.monitoring.MonitoringSystem') as mock_monitoring:
        mock_monitoring.return_value.get_component_status.return_value = {
            'status': 'healthy', 'response_time': 100
        }
        
        result = component_checker.check_with_monitoring_system(sample_components[0])
        assert result['status'] == 'healthy'
        assert result['response_time'] == 100

# 8. Teste de configuração
def test_configuration_management(health_api):
    # Configurar thresholds de saúde
    thresholds_config = health_api.configure_health_thresholds({
        'response_time_warning': 500,
        'response_time_critical': 2000,
        'error_rate_warning': 0.01,
        'error_rate_critical': 0.10
    })
    assert thresholds_config['response_time_warning'] == 500
    
    # Configurar intervalos de verificação
    intervals_config = health_api.configure_check_intervals({
        'component_check_interval': 30,
        'dependency_check_interval': 60,
        'metrics_collection_interval': 300
    })
    assert intervals_config['component_check_interval'] == 30

# 9. Teste de logs
def test_logging_functionality(health_api, sample_components, caplog):
    component_checker = ComponentChecker()
    
    with caplog.at_level('INFO'):
        component_checker.check_all_components(sample_components)
    
    assert any('Health check completed' in m for m in caplog.messages)
    assert any('components' in m for m in caplog.messages)
    
    # Verificar logs de alerta
    with caplog.at_level('WARNING'):
        component_checker.check_health_alerts(sample_components, {})
    
    assert any('Health alert' in m for m in caplog.messages)

# 10. Teste de relatórios
def test_report_generation(health_api, sample_components):
    health_metrics = HealthMetrics()
    
    # Gerar relatório de saúde
    health_report = health_metrics.generate_health_report('2024-01-01', '2024-01-31')
    assert 'executive_summary' in health_report
    assert 'component_analysis' in health_report
    assert 'dependency_status' in health_report
    assert 'recommendations' in health_report
    
    # Gerar relatório de SLA
    sla_report = health_metrics.generate_sla_report('2024-01-01', '2024-01-31')
    assert 'sla_compliance' in sla_report
    assert 'uptime_percentage' in sla_report
    assert 'response_time_sla' in sla_report
    assert 'incident_summary' in sla_report 