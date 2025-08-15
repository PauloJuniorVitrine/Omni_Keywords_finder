from typing import Dict, List, Optional, Any
#!/usr/bin/env python3
"""
🧪 TESTES UNITÁRIOS - CONFIGURAÇÃO CORS

Tracing ID: TEST_CORS_CONFIG_2025_001
Data/Hora: 2025-01-27 19:00:00 UTC
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

Testes para configuração CORS e headers de segurança.
"""

import unittest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock
from datetime import datetime

# Adicionar backend ao path
import sys
sys.path.append('backend')

# Importar módulos CORS
from app.middleware.cors_middleware import (
    get_cors_config, 
    is_valid_origin, 
    validate_origin_middleware,
    cors_protected,
    generate_request_id,
    log_cors_violation
)

from app.middleware.security_headers import (
    get_security_config,
    add_security_headers,
    validate_request_headers,
    log_suspicious_header
)

class TestCORSConfig(unittest.TestCase):
    """Testes para configuração CORS"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Criar diretórios necessários
        os.makedirs('data/cors', exist_ok=True)
        os.makedirs('logs/cors', exist_ok=True)
    
    def tearDown(self):
        """Limpeza após cada teste"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_get_cors_config_development(self):
        """Testa configuração CORS para desenvolvimento"""
        with patch.dict(os.environ, {'FLASK_ENV': 'development'}):
            config = get_cors_config()
            
            self.assertIn('http://localhost:3000', config['origins'])
            self.assertIn('http://localhost:3001', config['origins'])
            self.assertIn('http://localhost:5173', config['origins'])  # Vite
            self.assertFalse(config['strict_origin_validation'])
            self.assertFalse(config['log_violations'])
    
    def test_get_cors_config_staging(self):
        """Testa configuração CORS para staging"""
        with patch.dict(os.environ, {'FLASK_ENV': 'staging'}):
            config = get_cors_config()
            
            self.assertIn('https://staging.omni-keywords-finder.com', config['origins'])
            self.assertIn('http://localhost:3000', config['origins'])  # Para testes
            self.assertTrue(config['strict_origin_validation'])
            self.assertTrue(config['log_violations'])
    
    def test_get_cors_config_production(self):
        """Testa configuração CORS para produção"""
        with patch.dict(os.environ, {'FLASK_ENV': 'production'}):
            config = get_cors_config()
            
            self.assertIn('https://omni-keywords-finder.com', config['origins'])
            self.assertNotIn('http://localhost', str(config['origins']))  # Não deve ter localhost
            self.assertTrue(config['strict_origin_validation'])
            self.assertTrue(config['log_violations'])
    
    def test_is_valid_origin_exact_match(self):
        """Testa validação de origem com match exato"""
        config = get_cors_config()
        
        # Testa match exato
        self.assertTrue(is_valid_origin('http://localhost:3000', config))
        self.assertFalse(is_valid_origin('http://malicious.com', config))
    
    def test_is_valid_origin_pattern_match(self):
        """Testa validação de origem com padrão (desenvolvimento)"""
        with patch.dict(os.environ, {'FLASK_ENV': 'development'}):
            config = get_cors_config()
            
            # Em desenvolvimento, permite localhost com qualquer porta
            self.assertTrue(is_valid_origin('http://localhost:8080', config))
            self.assertTrue(is_valid_origin('http://127.0.0.1:9999', config))
            self.assertFalse(is_valid_origin('http://malicious.com:3000', config))
    
    def test_is_valid_origin_strict_mode(self):
        """Testa validação de origem em modo estrito"""
        with patch.dict(os.environ, {'FLASK_ENV': 'production'}):
            config = get_cors_config()
            
            # Em produção, apenas origens exatas
            self.assertTrue(is_valid_origin('https://omni-keywords-finder.com', config))
            self.assertFalse(is_valid_origin('http://localhost:3000', config))
            self.assertFalse(is_valid_origin('https://malicious.com', config))
    
    def test_generate_request_id(self):
        """Testa geração de Request ID"""
        request_id1 = generate_request_id()
        request_id2 = generate_request_id()
        
        self.assertIsInstance(request_id1, str)
        self.assertIsInstance(request_id2, str)
        self.assertNotEqual(request_id1, request_id2)
        self.assertTrue(len(request_id1) > 0)

class TestCORSMiddleware(unittest.TestCase):
    """Testes para middleware CORS"""
    
    def setUp(self):
        """Configuração inicial"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        os.makedirs('data/cors', exist_ok=True)
        os.makedirs('logs/cors', exist_ok=True)
    
    def tearDown(self):
        """Limpeza"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('app.middleware.cors_middleware.log_cors_violation')
    def test_validate_origin_middleware_valid_origin(self, mock_log):
        """Testa middleware com origem válida"""
        with patch.dict(os.environ, {'FLASK_ENV': 'development'}):
            from flask import Flask, request
            
            app = Flask(__name__)
            
            @app.route('/test')
            @validate_origin_middleware()
            def test_endpoint():
                return {'status': 'ok'}
            
            with app.test_client() as client:
                response = client.get('/test', headers={'Origin': 'http://localhost:3000'})
                
                self.assertEqual(response.status_code, 200)
                self.assertIn('Access-Control-Allow-Origin', response.headers)
                self.assertEqual(response.headers['Access-Control-Allow-Origin'], 'http://localhost:3000')
                mock_log.assert_not_called()
    
    @patch('app.middleware.cors_middleware.log_cors_violation')
    def test_validate_origin_middleware_invalid_origin(self, mock_log):
        """Testa middleware com origem inválida"""
        with patch.dict(os.environ, {'FLASK_ENV': 'production'}):
            from flask import Flask, request
            
            app = Flask(__name__)
            
            @app.route('/test')
            @validate_origin_middleware()
            def test_endpoint():
                return {'status': 'ok'}
            
            with app.test_client() as client:
                response = client.get('/test', headers={'Origin': 'http://malicious.com'})
                
                self.assertEqual(response.status_code, 403)
                self.assertIn('error', response.get_json())
                mock_log.assert_called_once()
    
    def test_cors_protected_options(self):
        """Testa decorator cors_protected com requisição OPTIONS"""
        with patch.dict(os.environ, {'FLASK_ENV': 'development'}):
            from flask import Flask, request
            
            app = Flask(__name__)
            
            @app.route('/test', methods=['GET', 'OPTIONS'])
            @cors_protected
            def test_endpoint():
                return {'status': 'ok'}
            
            with app.test_client() as client:
                response = client.options('/test', headers={'Origin': 'http://localhost:3000'})
                
                self.assertEqual(response.status_code, 200)
                self.assertIn('Access-Control-Allow-Origin', response.headers)
                self.assertIn('Access-Control-Allow-Methods', response.headers)
                self.assertIn('Access-Control-Allow-Headers', response.headers)

class TestSecurityHeaders(unittest.TestCase):
    """Testes para headers de segurança"""
    
    def setUp(self):
        """Configuração inicial"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        os.makedirs('data/security', exist_ok=True)
        os.makedirs('logs/security', exist_ok=True)
    
    def tearDown(self):
        """Limpeza"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_get_security_config_development(self):
        """Testa configuração de segurança para desenvolvimento"""
        with patch.dict(os.environ, {'FLASK_ENV': 'development'}):
            config = get_security_config()
            
            self.assertIsNone(config['strict_transport_security'])  # Não usar HSTS
            self.assertEqual(config['x_frame_options'], 'SAMEORIGIN')  # Mais permissivo
            self.assertIsNone(config['cross_origin_embedder_policy'])  # Desabilitado
    
    def test_get_security_config_production(self):
        """Testa configuração de segurança para produção"""
        with patch.dict(os.environ, {'FLASK_ENV': 'production'}):
            config = get_security_config()
            
            self.assertIsNotNone(config['strict_transport_security'])
            self.assertEqual(config['x_frame_options'], 'DENY')
            self.assertIsNotNone(config['cross_origin_embedder_policy'])
            self.assertIn('preload', config['strict_transport_security'])
    
    def test_add_security_headers(self):
        """Testa adição de headers de segurança"""
        from flask import Response
        
        response = Response('test')
        config = get_security_config()
        
        # Mock do g.request_id
        with patch('app.middleware.security_headers.g') as mock_g:
            mock_g.request_id = 'test-request-id'
            
            enhanced_response = add_security_headers(response)
            
            # Verifica headers básicos
            self.assertIn('X-Content-Type-Options', enhanced_response.headers)
            self.assertIn('X-Frame-Options', enhanced_response.headers)
            self.assertIn('X-XSS-Protection', enhanced_response.headers)
            self.assertIn('Referrer-Policy', enhanced_response.headers)
            self.assertIn('X-Request-ID', enhanced_response.headers)
            self.assertEqual(enhanced_response.headers['X-Request-ID'], 'test-request-id')
    
    @patch('app.middleware.security_headers.log_suspicious_header')
    def test_validate_request_headers_normal(self, mock_log):
        """Testa validação de headers com requisição normal"""
        from flask import Flask, request
        
        app = Flask(__name__)
        
        with app.test_request_context('/', headers={'User-Agent': 'Mozilla/5.0'}):
            validate_request_headers()
            mock_log.assert_not_called()
    
    @patch('app.middleware.security_headers.log_suspicious_header')
    def test_validate_request_headers_suspicious(self, mock_log):
        """Testa validação de headers com headers suspeitos"""
        from flask import Flask, request
        
        app = Flask(__name__)
        
        with app.test_request_context('/', headers={
            'User-Agent': 'A' * 600,  # User-Agent muito longo
            'X-Forwarded-For': '192.168.1.1'  # Header suspeito
        }):
            validate_request_headers()
            self.assertEqual(mock_log.call_count, 2)  # 2 headers suspeitos

class TestCORSIntegration(unittest.TestCase):
    """Testes de integração CORS"""
    
    def setUp(self):
        """Configuração inicial"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        os.makedirs('data/integration', exist_ok=True)
        os.makedirs('logs/integration', exist_ok=True)
    
    def tearDown(self):
        """Limpeza"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_full_cors_workflow(self):
        """Testa workflow completo de CORS"""
        with patch.dict(os.environ, {'FLASK_ENV': 'development'}):
            from flask import Flask, request
            
            app = Flask(__name__)
            
            # Aplica middleware CORS
            from app.middleware.cors_middleware import init_cors_middleware
            from app.middleware.security_headers import init_security_headers
            
            app = init_cors_middleware(app)
            app = init_security_headers(app)
            
            @app.route('/api/test')
            def test_endpoint():
                return {'status': 'ok', 'data': 'test'}
            
            with app.test_client() as client:
                # Testa requisição normal
                response = client.get('/api/test', headers={
                    'Origin': 'http://localhost:3000',
                    'X-Request-ID': 'test-id'
                })
                
                self.assertEqual(response.status_code, 200)
                self.assertIn('Access-Control-Allow-Origin', response.headers)
                self.assertIn('X-Content-Type-Options', response.headers)
                self.assertIn('X-Request-ID', response.headers)
                
                # Testa preflight OPTIONS
                response = client.options('/api/test', headers={
                    'Origin': 'http://localhost:3000',
                    'Access-Control-Request-Method': 'POST',
                    'Access-Control-Request-Headers': 'Content-Type'
                })
                
                self.assertEqual(response.status_code, 200)
                self.assertIn('Access-Control-Allow-Origin', response.headers)
                self.assertIn('Access-Control-Allow-Methods', response.headers)
    
    def test_cors_error_handling(self):
        """Testa tratamento de erros CORS"""
        with patch.dict(os.environ, {'FLASK_ENV': 'production'}):
            from flask import Flask, request
            
            app = Flask(__name__)
            
            from app.middleware.cors_middleware import init_cors_middleware
            app = init_cors_middleware(app)
            
            @app.route('/api/test')
            def test_endpoint():
                return {'status': 'ok'}
            
            with app.test_client() as client:
                # Testa origem não permitida em produção
                response = client.get('/api/test', headers={
                    'Origin': 'http://localhost:3000'
                })
                
                # Em produção, localhost não é permitido
                self.assertEqual(response.status_code, 403)
                self.assertIn('error', response.get_json())

if __name__ == '__main__':
    unittest.main() 