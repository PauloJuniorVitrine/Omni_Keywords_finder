"""
Configurações compartilhadas para testes
Tracing ID: CONFTEST_001_20241227
"""

import pytest
import tempfile
import os
import sys
from unittest.mock import Mock, patch
from typing import Dict, Any

# Adicionar path do projeto
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

# Configurações globais para testes
pytest_plugins = []


@pytest.fixture(scope="session")
def test_config():
    """Configuração global para testes"""
    return {
        'test_mode': True,
        'log_level': 'DEBUG',
        'cache_enabled': False,
        'timeout_etapa': 30,
        'retry_attempts': 2
    }


@pytest.fixture(scope="session")
def temp_test_dir():
    """Diretório temporário para testes"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_google_api():
    """Mock para Google Keyword Planner API"""
    with patch('infrastructure.orchestrator.etapas.etapa_validacao.GoogleKeywordPlannerValidator') as mock:
        mock.return_value.validar.return_value = [
            {'keyword': 'teste1', 'volume': 1000, 'competition': 0.3, 'valid': True},
            {'keyword': 'teste2', 'volume': 800, 'competition': 0.5, 'valid': True}
        ]
        yield mock


@pytest.fixture
def mock_openai_api():
    """Mock para OpenAI API"""
    with patch('infrastructure.orchestrator.etapas.etapa_preenchimento.OpenAI') as mock:
        mock_client = Mock()
        mock_client.chat.completions.create.return_value.choices[0].message.content = "Conteúdo gerado"
        mock.return_value = mock_client
        yield mock


@pytest.fixture
def mock_coletor_keywords():
    """Mock para coletor de keywords"""
    with patch('infrastructure.orchestrator.etapas.etapa_coleta.ColetorKeywords') as mock:
        mock.return_value.coletar.return_value = [
            {'keyword': 'python tutorial', 'volume': 1000},
            {'keyword': 'javascript guide', 'volume': 800}
        ]
        yield mock


@pytest.fixture
def sample_keywords():
    """Dados de exemplo para keywords"""
    return [
        {'keyword': 'python tutorial', 'volume': 1000, 'competition': 0.3},
        {'keyword': 'javascript guide', 'volume': 800, 'competition': 0.5},
        {'keyword': 'machine learning', 'volume': 1200, 'competition': 0.7},
        {'keyword': 'data science', 'volume': 900, 'competition': 0.4}
    ]


@pytest.fixture
def sample_conteudos():
    """Dados de exemplo para conteúdos gerados"""
    return [
        {
            'keyword': 'python tutorial',
            'conteudo': 'Tutorial completo sobre Python com exemplos práticos.',
            'score_qualidade': 85
        },
        {
            'keyword': 'javascript guide',
            'conteudo': 'Guia completo sobre JavaScript para iniciantes.',
            'score_qualidade': 78
        }
    ]


@pytest.fixture
def orchestrator_config():
    """Configuração para testes do orquestrador"""
    return {
        'nicho': 'tecnologia',
        'max_keywords': 100,
        'timeout_etapa': 300,
        'retry_attempts': 3,
        'cache_enabled': True,
        'log_level': 'INFO',
        'circuit_breaker_enabled': True,
        'fallback_enabled': True
    }


@pytest.fixture
def mock_progress_tracker():
    """Mock para ProgressTracker"""
    with patch('infrastructure.orchestrator.progress_tracker.ProgressTracker') as mock:
        mock.return_value.obter_progresso.return_value = {
            'etapa_atual': 'coleta',
            'progresso': 25,
            'tempo_estimado': 120
        }
        mock.return_value.salvar_checkpoint.return_value = True
        mock.return_value.restaurar_checkpoint.return_value = {
            'etapa_atual': 'validacao',
            'progresso': 50,
            'dados_intermediarios': {'keywords': ['teste1', 'teste2']}
        }
        yield mock


@pytest.fixture
def mock_error_handler():
    """Mock para ErrorHandler"""
    with patch('infrastructure.orchestrator.error_handler.ErrorHandler') as mock:
        mock.return_value.tratar_erro.return_value = {
            'status': 'recuperado',
            'acao': 'retry',
            'tentativas': 1
        }
        mock.return_value.decidir_acao.return_value = 'retry'
        yield mock


@pytest.fixture
def mock_notification_system():
    """Mock para sistema de notificações"""
    with patch('infrastructure.orchestrator.notifications.NotificationSystem') as mock:
        mock.return_value.enviar_notificacao.return_value = True
        mock.return_value.enviar_alerta.return_value = True
        yield mock


@pytest.fixture
def mock_metrics_system():
    """Mock para sistema de métricas"""
    with patch('infrastructure.orchestrator.metrics.MetricsSystem') as mock:
        mock.return_value.registrar_metrica.return_value = True
        mock.return_value.obter_metricas.return_value = {
            'tempo_total': 300,
            'keywords_processadas': 150,
            'taxa_sucesso': 0.95
        }
        yield mock


@pytest.fixture
def mock_cache_system():
    """Mock para sistema de cache"""
    with patch('infrastructure.orchestrator.cache.CacheSystem') as mock:
        mock.return_value.obter.return_value = {
            'keywords': ['teste1', 'teste2'],
            'timestamp': '2024-12-27T10:00:00Z'
        }
        mock.return_value.salvar.return_value = True
        mock.return_value.invalidar.return_value = True
        yield mock


@pytest.fixture
def mock_validation_system():
    """Mock para sistema de validação"""
    with patch('infrastructure.orchestrator.validation.ValidationSystem') as mock:
        mock.return_value.validar_dados.return_value = True
        mock.return_value.validar_configuracao.return_value = True
        mock.return_value.validar_qualidade.return_value = True
        yield mock


@pytest.fixture
def sample_etapa_data():
    """Dados de exemplo para etapas"""
    return {
        'coleta': {
            'keywords': [
                {'keyword': 'python tutorial', 'volume': 1000},
                {'keyword': 'javascript guide', 'volume': 800}
            ]
        },
        'validacao': {
            'keywords_validas': [
                {'keyword': 'python tutorial', 'volume': 1000, 'valid': True},
                {'keyword': 'javascript guide', 'volume': 800, 'valid': True}
            ]
        },
        'processamento': {
            'keywords_processadas': [
                {'keyword': 'python tutorial', 'volume': 1000, 'score': 85},
                {'keyword': 'javascript guide', 'volume': 800, 'score': 75}
            ],
            'clusters': [
                {'nome': 'python', 'keywords': ['python tutorial']},
                {'nome': 'javascript', 'keywords': ['javascript guide']}
            ]
        },
        'preenchimento': {
            'conteudos_gerados': [
                {'keyword': 'python tutorial', 'conteudo': 'Tutorial completo sobre Python'},
                {'keyword': 'javascript guide', 'conteudo': 'Guia completo sobre JavaScript'}
            ]
        },
        'exportacao': {
            'arquivo_exportado': 'output/tecnologia.zip',
            'metadados': {
                'total_keywords': 2,
                'total_conteudos': 2,
                'tempo_processamento': 300
            }
        }
    }


@pytest.fixture
def mock_file_system():
    """Mock para operações de arquivo"""
    with patch('builtins.open', create=True) as mock_open, \
         patch('os.path.exists') as mock_exists, \
         patch('os.makedirs') as mock_makedirs:
        
        mock_exists.return_value = False
        mock_makedirs.return_value = None
        
        # Mock para operações de arquivo
        mock_file = Mock()
        mock_file.__enter__.return_value = mock_file
        mock_file.__exit__.return_value = None
        mock_file.write.return_value = None
        mock_file.read.return_value = '{"test": "data"}'
        mock_open.return_value = mock_file
        
        yield {
            'open': mock_open,
            'exists': mock_exists,
            'makedirs': mock_makedirs,
            'file': mock_file
        }


@pytest.fixture
def mock_zip_file():
    """Mock para operações de ZIP"""
    with patch('zipfile.ZipFile') as mock_zip:
        mock_zip_instance = Mock()
        mock_zip_instance.__enter__.return_value = mock_zip_instance
        mock_zip_instance.__exit__.return_value = None
        mock_zip_instance.writestr.return_value = None
        mock_zip.return_value = mock_zip_instance
        yield mock_zip


@pytest.fixture
def mock_time_sleep():
    """Mock para time.sleep para acelerar testes"""
    with patch('time.sleep') as mock_sleep:
        mock_sleep.return_value = None
        yield mock_sleep


@pytest.fixture
def mock_logging():
    """Mock para sistema de logging"""
    with patch('logging.getLogger') as mock_get_logger:
        mock_logger = Mock()
        mock_logger.info.return_value = None
        mock_logger.error.return_value = None
        mock_logger.warning.return_value = None
        mock_logger.debug.return_value = None
        mock_get_logger.return_value = mock_logger
        yield mock_logger


@pytest.fixture
def sample_error_scenarios():
    """Cenários de erro para testes"""
    return {
        'api_timeout': TimeoutError("API timeout"),
        'network_error': ConnectionError("Network connection failed"),
        'rate_limit': Exception("Rate limit exceeded"),
        'invalid_data': ValueError("Invalid data format"),
        'disk_full': OSError("No space left on device"),
        'permission_denied': PermissionError("Permission denied"),
        'resource_unavailable': ResourceWarning("Resource unavailable")
    }


@pytest.fixture
def mock_circuit_breaker():
    """Mock para circuit breaker"""
    with patch('infrastructure.orchestrator.error_handler.CircuitBreaker') as mock:
        mock.return_value.estado.return_value = 'closed'
        mock.return_value.pode_executar.return_value = True
        mock.return_value.registrar_sucesso.return_value = None
        mock.return_value.registrar_falha.return_value = None
        yield mock


@pytest.fixture
def performance_benchmarks():
    """Benchmarks de performance para testes"""
    return {
        'etapa_coleta': {'max_tempo': 30, 'max_memoria_mb': 100},
        'etapa_validacao': {'max_tempo': 60, 'max_memoria_mb': 150},
        'etapa_processamento': {'max_tempo': 45, 'max_memoria_mb': 200},
        'etapa_preenchimento': {'max_tempo': 120, 'max_memoria_mb': 300},
        'etapa_exportacao': {'max_tempo': 30, 'max_memoria_mb': 100},
        'fluxo_completo': {'max_tempo': 300, 'max_memoria_mb': 500}
    }


# Configurações específicas para diferentes tipos de teste
def pytest_configure(config):
    """Configuração do pytest"""
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "load: mark test as load test"
    )
    config.addinivalue_line(
        "markers", "resilience: mark test as resilience test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modifica itens de teste baseado em marcadores"""
    for item in items:
        if "test_load" in item.nodeid:
            item.add_marker(pytest.mark.load)
        elif "test_resilience" in item.nodeid:
            item.add_marker(pytest.mark.resilience)
        elif "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        else:
            item.add_marker(pytest.mark.unit)


# Hooks para limpeza
@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Limpeza automática após cada teste"""
    yield
    # Limpeza específica pode ser adicionada aqui
    import gc
    gc.collect() 