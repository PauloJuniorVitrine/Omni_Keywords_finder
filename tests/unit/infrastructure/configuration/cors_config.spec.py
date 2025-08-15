from typing import Dict, List, Optional, Any
"""
Teste unitário para configuração CORS segura
Tracing ID: FIXTYPE-002
"""

import pytest
import os
from unittest.mock import patch
from backend.app.main import app, get_cors_origins


class TestCORSConfiguration:
    """Testes para configuração CORS segura"""

    def test_cors_origins_development(self):
        """Testa origens CORS em ambiente de desenvolvimento"""
        with patch.dict(os.environ, {'FLASK_ENV': 'development'}):
            origins = get_cors_origins()
            
            expected_origins = [
                'http://localhost:3000',
                'http://localhost:3001',
                'http://127.0.0.1:3000',
                'http://127.0.0.1:3001'
            ]
            
            assert origins == expected_origins
            assert len(origins) == 4

    def test_cors_origins_staging(self):
        """Testa origens CORS em ambiente de staging"""
        with patch.dict(os.environ, {'FLASK_ENV': 'staging'}):
            origins = get_cors_origins()
            
            expected_origins = [
                'https://staging.omni-keywords-finder.com',
                'https://test.omni-keywords-finder.com'
            ]
            
            assert origins == expected_origins
            assert len(origins) == 2

    def test_cors_origins_production(self):
        """Testa origens CORS em ambiente de produção"""
        with patch.dict(os.environ, {'FLASK_ENV': 'production'}):
            origins = get_cors_origins()
            
            expected_origins = [
                'https://omni-keywords-finder.com',
                'https://www.omni-keywords-finder.com',
                'https://app.omni-keywords-finder.com'
            ]
            
            assert origins == expected_origins
            assert len(origins) == 3

    def test_cors_origins_default_development(self):
        """Testa que o padrão é desenvolvimento quando FLASK_ENV não está definido"""
        with patch.dict(os.environ, {}, clear=True):
            origins = get_cors_origins()
            
            # Deve retornar origens de desenvolvimento
            assert 'http://localhost:3000' in origins
            assert 'http://localhost:3001' in origins

    def test_cors_configuration_applied(self):
        """Testa se a configuração CORS foi aplicada ao app Flask"""
        with app.test_client() as client:
            # Verifica se o app tem configuração CORS
            assert hasattr(app, 'extensions')
            assert 'cors' in app.extensions

    def test_cors_headers_present(self):
        """Testa se headers CORS estão presentes nas respostas"""
        with app.test_client() as client:
            response = client.options('/')
            
            # Verifica headers CORS básicos
            assert 'Access-Control-Allow-Origin' in response.headers
            assert 'Access-Control-Allow-Methods' in response.headers
            assert 'Access-Control-Allow-Headers' in response.headers

    def test_cors_credentials_support(self):
        """Testa se suporte a credentials está habilitado"""
        with app.test_client() as client:
            response = client.options('/')
            
            # Verifica se credentials estão habilitados
            assert 'Access-Control-Allow-Credentials' in response.headers
            assert response.headers['Access-Control-Allow-Credentials'] == 'true'

    def test_cors_max_age_set(self):
        """Testa se max-age está configurado"""
        with app.test_client() as client:
            response = client.options('/')
            
            # Verifica se max-age está presente
            assert 'Access-Control-Max-Age' in response.headers
            assert response.headers['Access-Control-Max-Age'] == '3600'


if __name__ == '__main__':
    pytest.main([__file__]) 