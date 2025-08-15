import pytest
from unittest.mock import MagicMock, patch
from myapp.api.auditoria import AuditoriaAPI, EventLogger, LogSearcher, ComplianceChecker

@pytest.fixture
def auditoria_api():
    return AuditoriaAPI()

@pytest.fixture
def sample_event():
    return {
        'user_id': 'user123',
        'action': 'login',
        'timestamp': '2024-01-01T10:00:00Z',
        'ip_address': '192.168.1.1',
        'user_agent': 'Mozilla/5.0',
        'details': {'success': True}
    }

# 1. Teste de logging de eventos
def test_event_logging(auditoria_api, sample_event):
    logger = EventLogger()
    
    # Logar evento
    log_result = logger.log_event(sample_event)
    assert log_result['logged'] is True
    assert log_result['event_id'] is not None
    assert log_result['timestamp'] is not None
    
    # Verificar evento logado
    logged_event = logger.get_event(log_result['event_id'])
    assert logged_event['user_id'] == 'user123'
    assert logged_event['action'] == 'login'

# 2. Teste de busca de logs
def test_log_search(auditoria_api, sample_event):
    searcher = LogSearcher()
    
    # Buscar por usuário
    user_logs = searcher.search_by_user('user123')
    assert len(user_logs) > 0
    assert all(log['user_id'] == 'user123' for log in user_logs)
    
    # Buscar por ação
    action_logs = searcher.search_by_action('login')
    assert len(action_logs) > 0
    assert all(log['action'] == 'login' for log in action_logs)
    
    # Buscar por período
    period_logs = searcher.search_by_period('2024-01-01', '2024-01-02')
    assert len(period_logs) > 0
    assert all('2024-01-01' in log['timestamp'] for log in period_logs)

# 3. Teste de relatórios
def test_report_generation(auditoria_api, sample_event):
    logger = EventLogger()
    
    # Gerar relatório de atividades
    activity_report = logger.generate_activity_report('2024-01-01', '2024-01-31')
    assert 'total_events' in activity_report
    assert 'user_activities' in activity_report
    assert 'action_summary' in activity_report
    
    # Gerar relatório de segurança
    security_report = logger.generate_security_report('2024-01-01', '2024-01-31')
    assert 'failed_logins' in security_report
    assert 'suspicious_activities' in security_report
    assert 'ip_analysis' in security_report

# 4. Teste de compliance
def test_compliance_checking(auditoria_api, sample_event):
    compliance = ComplianceChecker()
    
    # Verificar compliance GDPR
    gdpr_compliance = compliance.check_gdpr_compliance()
    assert gdpr_compliance['compliant'] in [True, False]
    assert 'data_retention' in gdpr_compliance
    assert 'user_consent' in gdpr_compliance
    
    # Verificar compliance SOX
    sox_compliance = compliance.check_sox_compliance()
    assert sox_compliance['compliant'] in [True, False]
    assert 'access_controls' in sox_compliance
    assert 'audit_trail' in sox_compliance

# 5. Teste de casos edge
def test_edge_cases(auditoria_api):
    logger = EventLogger()
    
    # Teste com evento vazio
    empty_event = {}
    with pytest.raises(ValueError):
        logger.log_event(empty_event)
    
    # Teste com timestamp inválido
    invalid_event = {
        'user_id': 'user123',
        'action': 'login',
        'timestamp': 'invalid_timestamp'
    }
    with pytest.raises(ValueError):
        logger.log_event(invalid_event)
    
    # Teste com busca sem resultados
    searcher = LogSearcher()
    no_results = searcher.search_by_user('nonexistent_user')
    assert len(no_results) == 0

# 6. Teste de performance
def test_auditoria_performance(auditoria_api, sample_event, benchmark):
    logger = EventLogger()
    
    def log_event_operation():
        return logger.log_event(sample_event)
    
    benchmark(log_event_operation)

# 7. Teste de integração
def test_integration_with_database(auditoria_api, sample_event):
    logger = EventLogger()
    
    # Integração com banco de dados
    with patch('myapp.database.AuditDatabase') as mock_db:
        mock_db.return_value.insert_event.return_value = {'id': 'event_123'}
        
        result = logger.log_event_to_database(sample_event)
        assert result['id'] == 'event_123'

# 8. Teste de configuração
def test_configuration_management(auditoria_api):
    # Configurar retenção de logs
    retention_config = auditoria_api.configure_log_retention({
        'audit_logs_days': 365,
        'security_logs_days': 730,
        'performance_logs_days': 90
    })
    assert retention_config['audit_logs_days'] == 365
    
    # Configurar níveis de log
    log_levels = auditoria_api.configure_log_levels({
        'audit': 'INFO',
        'security': 'WARNING',
        'performance': 'DEBUG'
    })
    assert log_levels['audit'] == 'INFO'

# 9. Teste de logs
def test_logging_functionality(auditoria_api, sample_event, caplog):
    logger = EventLogger()
    
    with caplog.at_level('INFO'):
        logger.log_event(sample_event)
    
    assert any('Event logged' in m for m in caplog.messages)
    assert any('user123' in m for m in caplog.messages)
    
    # Verificar logs de erro
    with caplog.at_level('ERROR'):
        try:
            logger.log_event({})
        except:
            pass
    
    assert any('Invalid event data' in m for m in caplog.messages)

# 10. Teste de métricas
def test_metrics_monitoring(auditoria_api, sample_event):
    logger = EventLogger()
    
    # Monitorar volume de logs
    volume_metrics = logger.monitor_log_volume('2024-01-01', '2024-01-31')
    assert 'total_events' in volume_metrics
    assert 'events_per_day' in volume_metrics
    assert 'peak_hours' in volume_metrics
    
    # Monitorar performance do sistema
    performance_metrics = logger.monitor_system_performance()
    assert 'log_processing_time' in performance_metrics
    assert 'storage_usage' in performance_metrics
    assert 'query_performance' in performance_metrics 