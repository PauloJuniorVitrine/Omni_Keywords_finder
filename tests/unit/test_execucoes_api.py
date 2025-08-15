import pytest
from unittest.mock import MagicMock, patch
from myapp.api.execucoes import ExecucoesAPI, ExecutionManager, ExecutionMonitor, ResultProcessor

@pytest.fixture
def execucoes_api():
    return ExecucoesAPI()

@pytest.fixture
def sample_execution():
    return {
        'name': 'keyword_analysis',
        'parameters': {
            'keywords': ['python', 'javascript'],
            'max_results': 100,
            'language': 'pt-BR'
        },
        'priority': 'normal',
        'timeout': 300
    }

# 1. Teste de criação de execuções
def test_execution_creation(execucoes_api, sample_execution):
    execution_manager = ExecutionManager()
    
    # Criar execução
    execution = execution_manager.create_execution(sample_execution)
    assert execution['name'] == 'keyword_analysis'
    assert execution['id'] is not None
    assert execution['status'] == 'pending'
    assert execution['created_at'] is not None
    
    # Verificar execução criada
    created_execution = execution_manager.get_execution(execution['id'])
    assert created_execution['parameters']['keywords'] == ['python', 'javascript']
    assert created_execution['priority'] == 'normal'

# 2. Teste de monitoramento
def test_execution_monitoring(execucoes_api, sample_execution):
    monitor = ExecutionMonitor()
    execution_manager = ExecutionManager()
    
    # Criar execução primeiro
    execution = execution_manager.create_execution(sample_execution)
    
    # Monitorar status
    status = monitor.get_execution_status(execution['id'])
    assert status in ['pending', 'running', 'completed', 'failed', 'cancelled']
    
    # Monitorar progresso
    progress = monitor.get_execution_progress(execution['id'])
    assert 'percentage' in progress
    assert 'current_step' in progress
    assert 'estimated_completion' in progress
    
    # Monitorar recursos
    resources = monitor.get_resource_usage(execution['id'])
    assert 'cpu_usage' in resources
    assert 'memory_usage' in resources
    assert 'disk_usage' in resources

# 3. Teste de cancelamento
def test_execution_cancellation(execucoes_api, sample_execution):
    execution_manager = ExecutionManager()
    
    # Criar execução
    execution = execution_manager.create_execution(sample_execution)
    
    # Cancelar execução
    cancellation_result = execution_manager.cancel_execution(execution['id'])
    assert cancellation_result['cancelled'] is True
    assert cancellation_result['cancelled_at'] is not None
    
    # Verificar status após cancelamento
    status = execution_manager.get_execution_status(execution['id'])
    assert status == 'cancelled'

# 4. Teste de resultados
def test_execution_results(execucoes_api, sample_execution):
    result_processor = ResultProcessor()
    execution_manager = ExecutionManager()
    
    # Criar execução
    execution = execution_manager.create_execution(sample_execution)
    
    # Simular resultados
    mock_results = {
        'keywords': ['python', 'javascript'],
        'analysis_results': [
            {'keyword': 'python', 'volume': 1000, 'difficulty': 'medium'},
            {'keyword': 'javascript', 'volume': 800, 'difficulty': 'easy'}
        ],
        'summary': {'total_keywords': 2, 'avg_volume': 900}
    }
    
    # Processar resultados
    processed_results = result_processor.process_results(execution['id'], mock_results)
    assert processed_results['processed'] is True
    assert processed_results['results_count'] == 2
    assert 'summary' in processed_results
    
    # Obter resultados
    results = result_processor.get_results(execution['id'])
    assert results['keywords'] == ['python', 'javascript']
    assert len(results['analysis_results']) == 2

# 5. Teste de casos edge
def test_edge_cases(execucoes_api):
    execution_manager = ExecutionManager()
    
    # Teste com execução vazia
    empty_execution = {}
    with pytest.raises(ValueError):
        execution_manager.create_execution(empty_execution)
    
    # Teste com timeout inválido
    invalid_timeout = {
        'name': 'test',
        'parameters': {},
        'timeout': -1
    }
    with pytest.raises(ValueError):
        execution_manager.create_execution(invalid_timeout)
    
    # Teste com execução inexistente
    with pytest.raises(Exception):
        execution_manager.get_execution('nonexistent_id')

# 6. Teste de performance
def test_execution_performance(execucoes_api, sample_execution, benchmark):
    execution_manager = ExecutionManager()
    
    def create_execution_operation():
        return execution_manager.create_execution(sample_execution)
    
    benchmark(create_execution_operation)

# 7. Teste de integração
def test_integration_with_workflow_engine(execucoes_api, sample_execution):
    execution_manager = ExecutionManager()
    
    # Integração com engine de workflow
    with patch('myapp.workflow.WorkflowEngine') as mock_workflow:
        mock_workflow.return_value.start_execution.return_value = {'workflow_id': 'wf_123'}
        
        result = execution_manager.start_execution_with_workflow(sample_execution)
        assert result['workflow_id'] == 'wf_123'

# 8. Teste de configuração
def test_configuration_management(execucoes_api):
    # Configurar limites de execução
    limits_config = execucoes_api.configure_execution_limits({
        'max_concurrent_executions': 10,
        'max_execution_time': 3600,
        'max_memory_usage': '2GB'
    })
    assert limits_config['max_concurrent_executions'] == 10
    
    # Configurar notificações
    notification_config = execucoes_api.configure_notifications({
        'email_notifications': True,
        'webhook_notifications': False,
        'slack_notifications': True
    })
    assert notification_config['email_notifications'] is True

# 9. Teste de logs
def test_logging_functionality(execucoes_api, sample_execution, caplog):
    execution_manager = ExecutionManager()
    
    with caplog.at_level('INFO'):
        execution_manager.create_execution(sample_execution)
    
    assert any('Execution created' in m for m in caplog.messages)
    assert any('keyword_analysis' in m for m in caplog.messages)
    
    # Verificar logs de erro
    with caplog.at_level('ERROR'):
        try:
            execution_manager.create_execution({})
        except:
            pass
    
    assert any('Invalid execution data' in m for m in caplog.messages)

# 10. Teste de métricas
def test_metrics_monitoring(execucoes_api, sample_execution):
    execution_manager = ExecutionManager()
    
    # Monitorar métricas de execução
    execution_metrics = execution_manager.monitor_execution_metrics('2024-01-01', '2024-01-31')
    assert 'total_executions' in execution_metrics
    assert 'success_rate' in execution_metrics
    assert 'avg_execution_time' in execution_metrics
    assert 'failed_executions' in execution_metrics
    
    # Monitorar performance do sistema
    system_metrics = execution_manager.monitor_system_performance()
    assert 'active_executions' in system_metrics
    assert 'queue_size' in system_metrics
    assert 'resource_utilization' in system_metrics 