"""
Configuração pytest para testes do backend
Tracing ID: BACKEND_TESTS_001_20250127
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# Adicionar path do projeto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Importar aplicação
from backend.app.main import app as flask_app
from backend.app.models import db, Nicho, Categoria, Execucao, Log
from backend.app.config import Config

@pytest.fixture(scope="session")
def app():
    """Fixture para aplicação Flask de teste."""
    # Configurar para teste
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    # Inicializar extensões
    db.init_app(flask_app)
    JWTManager(flask_app)
    
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.drop_all()

@pytest.fixture(scope="function")
def client(app):
    """Fixture para cliente de teste."""
    return app.test_client()

@pytest.fixture(scope="function")
def db_session(app):
    """Fixture para sessão de banco de dados."""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        
        # Criar sessão
        session = db.create_scoped_session(
            options={"bind": connection, "binds": {}}
        )
        
        db.session = session
        
        yield session
        
        # Rollback
        transaction.rollback()
        connection.close()
        session.remove()

@pytest.fixture
def mock_google_api():
    """Mock para API do Google."""
    with patch('infrastructure.coleta.gsc.GoogleSearchConsole') as mock:
        mock.return_value.get_keywords.return_value = [
            {'keyword': 'test keyword 1', 'volume': 1000, 'competition': 'low'},
            {'keyword': 'test keyword 2', 'volume': 500, 'competition': 'medium'},
            {'keyword': 'test keyword 3', 'volume': 2000, 'competition': 'high'}
        ]
        yield mock

@pytest.fixture
def mock_openai_api():
    """Mock para API do OpenAI."""
    with patch('infrastructure.processamento.ml_processor.OpenAI') as mock:
        mock.return_value.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Generated content for test"))]
        )
        yield mock

@pytest.fixture
def sample_nichos(db_session):
    """Dados de exemplo para nichos."""
    nichos = [
        Nicho(nome="Marketing Digital", descricao="Estratégias de marketing online"),
        Nicho(nome="Tecnologia", descricao="Inovações tecnológicas"),
        Nicho(nome="Saúde", descricao="Bem-estar e qualidade de vida")
    ]
    
    for nicho in nichos:
        db_session.add(nicho)
    db_session.commit()
    
    return nichos

@pytest.fixture
def sample_categorias(db_session):
    """Dados de exemplo para categorias."""
    categorias = [
        Categoria(nome="SEO", descricao="Otimização para motores de busca"),
        Categoria(nome="Redes Sociais", descricao="Marketing em redes sociais"),
        Categoria(nome="Email Marketing", descricao="Estratégias de email")
    ]
    
    for categoria in categorias:
        db_session.add(categoria)
    db_session.commit()
    
    return categorias

@pytest.fixture
def sample_execucoes(db_session):
    """Dados de exemplo para execuções."""
    execucoes = [
        Execucao(
            nicho_id=1,
            status="concluido",
            total_keywords=100,
            keywords_processadas=95,
            keywords_validas=90
        ),
        Execucao(
            nicho_id=2,
            status="em_execucao",
            total_keywords=50,
            keywords_processadas=25,
            keywords_validas=20
        )
    ]
    
    for execucao in execucoes:
        db_session.add(execucao)
    db_session.commit()
    
    return execucoes

@pytest.fixture
def auth_headers():
    """Headers de autenticação para testes."""
    return {
        'Authorization': 'Bearer test-jwt-token',
        'Content-Type': 'application/json'
    }

@pytest.fixture
def test_config():
    """Configuração de teste."""
    return {
        'TESTING': True,
        'DATABASE_URL': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret-key',
        'LOG_LEVEL': 'DEBUG'
    }
