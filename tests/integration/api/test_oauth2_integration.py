import pytest
from flask import Flask
from backend.app.api.auth import auth_bp, init_jwt, init_oauth
from backend.app.models import db as _db
from backend.app.models.user import User
from flask_jwt_extended import decode_token
from unittest.mock import patch
from typing import Dict, List, Optional, Any

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
    _db.init_app(app)
    with app.app_context():
        _db.create_all()
        init_jwt(app)
        init_oauth(app)
        app.register_blueprint(auth_bp)
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

@patch('backend.app.api.auth.oauth')
def test_oauth2_login_redirect(mock_oauth, client):
    mock_client = mock_oauth.create_client.return_value
    mock_client.authorize_redirect.return_value = 'redirect-url'
    response = client.get('/api/auth/oauth2/login/google')
    assert response.status_code == 200 or response.status_code == 302

@patch('backend.app.api.auth.oauth')
def test_oauth2_callback_success_google(mock_oauth, client):
    mock_client = mock_oauth.create_client.return_value
    mock_client.authorize_access_token.return_value = {'sub': '123', 'email': 'user@example.com', 'name': 'Test User'}
    mock_client.parse_id_token.return_value = {'sub': '123', 'email': 'user@example.com', 'name': 'Test User'}
    response = client.get('/api/auth/oauth2/callback/google')
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    token_data = decode_token(data['access_token'])
    assert 'user_id' in data
    assert data['provider'] == 'google'

@patch('backend.app.api.auth.oauth')
def test_oauth2_callback_success_github(mock_oauth, client):
    mock_client = mock_oauth.create_client.return_value
    mock_client.authorize_access_token.return_value = {'access_token': 'token'}
    mock_client.get.return_value.json.return_value = {'id': 456, 'email': 'git@example.com', 'login': 'gituser'}
    response = client.get('/api/auth/oauth2/callback/github')
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert data['provider'] == 'github'

@patch('backend.app.api.auth.oauth')
def test_oauth2_callback_invalid_provider(mock_oauth, client):
    response = client.get('/api/auth/oauth2/callback/invalid')
    assert response.status_code == 400
    data = response.get_json()
    assert 'erro' in data

@patch('backend.app.api.auth.oauth')
def test_oauth2_callback_token_expired(mock_oauth, client):
    mock_client = mock_oauth.create_client.return_value
    mock_client.authorize_access_token.side_effect = Exception('Token expirado')
    response = client.get('/api/auth/oauth2/callback/google')
    assert response.status_code == 500 or response.status_code == 400 