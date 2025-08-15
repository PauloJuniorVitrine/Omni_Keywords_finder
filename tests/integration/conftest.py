# 🧪 Configuração de Testes de Integração - Omni Keywords Finder
# 📅 Semana 7-8: Integration & E2E (Meta: 98% cobertura)
# 🎯 Tracing ID: TESTES_98_COBERTURA_001_20250127
# 📝 Prompt: Configurar ambiente de testes de integração
# 🔧 Ruleset: enterprise_control_layer.yaml

"""
Configuração de Testes de Integração
====================================

Este módulo configura o ambiente para testes de integração:
- Fixtures compartilhadas
- Configurações de banco de teste
- Mocks globais
- Configurações de ambiente
- Utilitários de teste

Cobertura Alvo: 98% (Semana 7-8)
"""

import pytest
import asyncio
import tempfile
import os
import json
from typing import Dict, Any, List, Optional
from unittest.mock import patch, MagicMock, AsyncMock
import httpx
from datetime import datetime, timedelta

# Importações do sistema
from backend.app.main import app
from backend.app.database.connection import DatabaseConnection
from backend.app.services.keyword_service import KeywordService
from backend.app.services.analysis_service import AnalysisService
from backend.app.services.user_service import UserService


@pytest.fixture(scope="session")
def event_loop():
    """Cria loop de eventos para testes assíncronos."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_database():
    """Cria banco de dados temporário para testes de integração."""
    # Criar arquivo temporário
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    db_path = temp_db.name
    temp_db.close()
    
    # Configurar conexão de teste
    connection = DatabaseConnection(f"sqlite:///{db_path}")
    
    yield connection
    
    # Limpeza
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture(scope="session")
def test_app():
    """Configura aplicação de teste."""
    # Configurar variáveis de ambiente para teste
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = "sqlite:///test.db"
    
    # Configurar app para teste
    app.config.update({
        "TESTING": True,
        "DATABASE_URL": "sqlite:///test.db"
    })
    
    return app


@pytest.fixture
async def http_client():
    """Cliente HTTP para testes de integração."""
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_keyword_data():
    """Dados de exemplo para keywords."""
    return [
        {
            "keyword": "python programming",
            "language": "pt-BR",
            "region": "BR",
            "volume": 1000,
            "difficulty": "medium"
        },
        {
            "keyword": "machine learning",
            "language": "pt-BR",
            "region": "BR",
            "volume": 800,
            "difficulty": "high"
        },
        {
            "keyword": "data science",
            "language": "pt-BR",
            "region": "BR",
            "volume": 600,
            "difficulty": "medium"
        }
    ]


@pytest.fixture
def sample_user_data():
    """Dados de exemplo para usuários."""
    return {
        "username": "test_user_integration",
        "email": "integration@test.com",
        "password": "secure_password_123",
        "role": "user"
    }


@pytest.fixture
def sample_analysis_data():
    """Dados de exemplo para análises."""
    return {
        "keywords": ["python", "machine learning", "data science"],
        "analysis_type": "comprehensive",
        "include_competitors": True,
        "include_trends": True,
        "language": "pt-BR",
        "region": "BR"
    }


@pytest.fixture
def mock_external_api():
    """Mock para APIs externas."""
    with patch('httpx.AsyncClient.get') as mock_get:
        # Mock de resposta padrão
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "data": "mocked_response"
        }
        mock_get.return_value = mock_response
        
        yield mock_get


@pytest.fixture
def mock_database_operations():
    """Mock para operações de banco de dados."""
    with patch.object(DatabaseConnection, 'execute_query') as mock_execute:
        with patch.object(DatabaseConnection, 'execute_transaction') as mock_transaction:
            
            # Mock de queries
            mock_execute.return_value = [
                {"id": 1, "keyword": "python", "volume": 1000},
                {"id": 2, "keyword": "machine learning", "volume": 800}
            ]
            
            # Mock de transações
            mock_transaction.return_value = True
            
            yield {
                "execute": mock_execute,
                "transaction": mock_transaction
            }


@pytest.fixture
def mock_keyword_service():
    """Mock para serviço de keywords."""
    with patch.object(KeywordService, 'process_keywords') as mock_process:
        with patch.object(KeywordService, 'get_keywords') as mock_get:
            with patch.object(KeywordService, 'save_keywords') as mock_save:
                
                # Mock de processamento
                mock_process.return_value = [
                    {"id": 1, "keyword": "python", "volume": 1000, "difficulty": "medium"},
                    {"id": 2, "keyword": "machine learning", "volume": 800, "difficulty": "high"}
                ]
                
                # Mock de recuperação
                mock_get.return_value = [
                    {"id": 1, "keyword": "python", "volume": 1000, "difficulty": "medium"},
                    {"id": 2, "keyword": "machine learning", "volume": 800, "difficulty": "high"}
                ]
                
                # Mock de salvamento
                mock_save.return_value = [1, 2]
                
                yield {
                    "process": mock_process,
                    "get": mock_get,
                    "save": mock_save
                }


@pytest.fixture
def mock_analysis_service():
    """Mock para serviço de análise."""
    with patch.object(AnalysisService, 'analyze_keywords') as mock_analyze:
        with patch.object(AnalysisService, 'create_analysis') as mock_create:
            with patch.object(AnalysisService, 'get_analysis_by_id') as mock_get:
                
                # Mock de análise
                mock_analyze.return_value = {
                    "analysis_id": "anal_001",
                    "keywords_analyzed": 3,
                    "total_volume": 2400,
                    "avg_difficulty": "medium",
                    "recommendations": [
                        "Focar em 'python' para volume alto",
                        "Considerar 'data science' para menor competição"
                    ]
                }
                
                # Mock de criação
                mock_create.return_value = {
                    "id": 1,
                    "analysis_type": "comprehensive",
                    "status": "completed",
                    "created_at": datetime.now().isoformat()
                }
                
                # Mock de recuperação
                mock_get.return_value = {
                    "id": 1,
                    "analysis_type": "comprehensive",
                    "status": "completed",
                    "created_at": datetime.now().isoformat()
                }
                
                yield {
                    "analyze": mock_analyze,
                    "create": mock_create,
                    "get": mock_get
                }


@pytest.fixture
def mock_user_service():
    """Mock para serviço de usuários."""
    with patch.object(UserService, 'create_user') as mock_create:
        with patch.object(UserService, 'authenticate_user') as mock_auth:
            with patch.object(UserService, 'get_user_by_id') as mock_get:
                
                # Mock de criação
                mock_create.return_value = {
                    "id": 1,
                    "username": "test_user",
                    "email": "test@example.com",
                    "role": "user"
                }
                
                # Mock de autenticação
                mock_auth.return_value = {
                    "user_id": 1,
                    "access_token": "valid_token_123",
                    "refresh_token": "refresh_token_123"
                }
                
                # Mock de recuperação
                mock_get.return_value = {
                    "id": 1,
                    "username": "test_user",
                    "email": "test@example.com",
                    "role": "user"
                }
                
                yield {
                    "create": mock_create,
                    "authenticate": mock_auth,
                    "get": mock_get
                }


@pytest.fixture
def test_headers():
    """Headers de teste com autenticação."""
    return {
        "Authorization": "Bearer test_token_123",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


@pytest.fixture
def mock_rate_limiter():
    """Mock para sistema de rate limiting."""
    with patch('backend.app.middleware.rate_limit.check_rate_limit') as mock_check:
        mock_check.return_value = True  # Sempre permite
        yield mock_check


@pytest.fixture
def mock_cache():
    """Mock para sistema de cache."""
    with patch('backend.app.services.cache_service.get') as mock_get:
        with patch('backend.app.services.cache_service.set') as mock_set:
            with patch('backend.app.services.cache_service.delete') as mock_delete:
                
                # Mock de cache miss
                mock_get.return_value = None
                mock_set.return_value = True
                mock_delete.return_value = True
                
                yield {
                    "get": mock_get,
                    "set": mock_set,
                    "delete": mock_delete
                }


@pytest.fixture
def mock_logging():
    """Mock para sistema de logging."""
    with patch('backend.app.services.logging_service.log_info') as mock_info:
        with patch('backend.app.services.logging_service.log_error') as mock_error:
            with patch('backend.app.services.logging_service.log_warning') as mock_warning:
                
                # Mocks de logging
                mock_info.return_value = None
                mock_error.return_value = None
                mock_warning.return_value = None
                
                yield {
                    "info": mock_info,
                    "error": mock_error,
                    "warning": mock_warning
                }


@pytest.fixture
def mock_metrics():
    """Mock para sistema de métricas."""
    with patch('backend.app.services.metrics_service.increment') as mock_increment:
        with patch('backend.app.services.metrics_service.timing') as mock_timing:
            with patch('backend.app.services.metrics_service.gauge') as mock_gauge:
                
                # Mocks de métricas
                mock_increment.return_value = None
                mock_timing.return_value = None
                mock_gauge.return_value = None
                
                yield {
                    "increment": mock_increment,
                    "timing": mock_timing,
                    "gauge": mock_gauge
                }


@pytest.fixture
def mock_notifications():
    """Mock para sistema de notificações."""
    with patch('backend.app.services.notification_service.send') as mock_send:
        with patch('backend.app.services.notification_service.send_bulk') as mock_bulk:
            
            # Mocks de notificações
            mock_send.return_value = True
            mock_bulk.return_value = [True, True, True]
            
            yield {
                "send": mock_send,
                "bulk": mock_bulk
            }


@pytest.fixture
def mock_file_storage():
    """Mock para sistema de armazenamento de arquivos."""
    with patch('backend.app.services.storage_service.upload') as mock_upload:
        with patch('backend.app.services.storage_service.download') as mock_download:
            with patch('backend.app.services.storage_service.delete') as mock_delete:
                
                # Mocks de storage
                mock_upload.return_value = "https://storage.example.com/file.pdf"
                mock_download.return_value = b"file_content"
                mock_delete.return_value = True
                
                yield {
                    "upload": mock_upload,
                    "download": mock_download,
                    "delete": mock_delete
                }


@pytest.fixture
def integration_test_config():
    """Configuração para testes de integração."""
    return {
        "base_url": "http://localhost:8000",
        "timeout": 30.0,
        "max_retries": 3,
        "retry_delay": 1.0,
        "test_data_size": "medium",  # small, medium, large
        "enable_mocks": True,
        "enable_external_calls": False
    }


@pytest.fixture
def test_environment():
    """Configura ambiente de teste."""
    # Configurar variáveis de ambiente
    env_vars = {
        "TESTING": "true",
        "ENVIRONMENT": "test",
        "LOG_LEVEL": "DEBUG",
        "DATABASE_URL": "sqlite:///test_integration.db",
        "REDIS_URL": "redis://localhost:6379/1",
        "API_TIMEOUT": "30",
        "MAX_CONNECTIONS": "100"
    }
    
    # Aplicar variáveis
    for key, value in env_vars.items():
        os.environ[key] = value
    
    yield env_vars
    
    # Limpeza (opcional)
    for key in env_vars:
        if key in os.environ:
            del os.environ[key]


@pytest.fixture
def cleanup_test_data():
    """Fixture para limpeza de dados de teste."""
    # Lista de dados a serem limpos
    test_data = []
    
    yield test_data
    
    # Limpeza após teste
    for data in test_data:
        if hasattr(data, 'cleanup'):
            data.cleanup()


# Configurações globais para testes de integração
pytest_plugins = [
    "tests.integration.fixtures.database",
    "tests.integration.fixtures.external_services",
    "tests.integration.fixtures.test_data"
]

# Configuração pytest para testes de integração
pytestmark = pytest.mark.integration
pytestmark = pytest.mark.asyncio 