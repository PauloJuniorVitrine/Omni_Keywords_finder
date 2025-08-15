"""
Testes Unitários - Middleware de Validação
Testa validação global, rate limiting e sanitização

Prompt: Implementação de testes para middleware de validação
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, request, jsonify
from werkzeug.exceptions import RequestEntityTooLarge, BadRequest

# Importar middleware
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.middleware.validation_middleware import ValidationMiddleware, validate_input
from app.schemas.auth import LoginRequest

class TestValidationMiddleware:
    """Testes para o middleware de validação"""
    
    @pytest.fixture
    def app(self):
        """Cria aplicação Flask para testes"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['REDIS_HOST'] = 'localhost'
        app.config['REDIS_PORT'] = 6379
        
        # Registrar rota de teste
        @app.route('/test', methods=['POST'])
        def test_route():
            return jsonify({'status': 'success'})
        
        @app.route('/auth/login', methods=['POST'])
        def auth_route():
            return jsonify({'status': 'authenticated'})
        
        @app.route('/execucao/create', methods=['POST'])
        def execucao_route():
            return jsonify({'status': 'execution_created'})
        
        return app
    
    @pytest.fixture
    def middleware(self, app):
        """Cria instância do middleware"""
        with patch('redis.Redis'):
            middleware = ValidationMiddleware(app)
            return middleware
    
    def test_middleware_initialization(self, app):
        """Testa inicialização do middleware"""
        with patch('redis.Redis') as mock_redis:
            middleware = ValidationMiddleware(app)
            
            assert middleware.app == app
            assert middleware.rate_limits is not None
            assert 'auth' in middleware.rate_limits
            assert 'execucao' in middleware.rate_limits
    
    def test_validate_payload_size_success(self, app, middleware):
        """Testa validação de tamanho de payload - sucesso"""
        with app.test_request_context('/test', method='POST', 
                                    data=json.dumps({'test': 'data'}),
                                    content_type='application/json'):
            # Simular content_length pequeno
            request.content_length = 100
            
            # Não deve levantar exceção
            middleware.validate_payload_size()
    
    def test_validate_payload_size_too_large(self, app, middleware):
        """Testa validação de tamanho de payload - muito grande"""
        with app.test_request_context('/test', method='POST', 
                                    data=json.dumps({'test': 'data'}),
                                    content_type='application/json'):
            # Simular content_length muito grande
            request.content_length = 200000  # 200KB
            
            with pytest.raises(RequestEntityTooLarge):
                middleware.validate_payload_size()
    
    def test_validate_headers_success(self, app, middleware):
        """Testa validação de headers - sucesso"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Test)',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        with app.test_request_context('/test', method='POST', 
                                    headers=headers,
                                    data=json.dumps({'test': 'data'})):
            # Não deve levantar exceção
            middleware.validate_headers()
    
    def test_validate_headers_missing(self, app, middleware):
        """Testa validação de headers - ausente"""
        with app.test_request_context('/test', method='POST', 
                                    data=json.dumps({'test': 'data'})):
            with pytest.raises(BadRequest) as exc_info:
                middleware.validate_headers()
            
            assert 'Header obrigatório ausente' in str(exc_info.value)
    
    def test_validate_headers_invalid_content_type(self, app, middleware):
        """Testa validação de headers - Content-Type inválido"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Test)',
            'Accept': 'application/json',
            'Content-Type': 'text/plain'
        }
        
        with app.test_request_context('/test', method='POST', 
                                    headers=headers,
                                    data='test data'):
            with pytest.raises(BadRequest) as exc_info:
                middleware.validate_headers()
            
            assert 'Header inválido' in str(exc_info.value)
    
    def test_sanitize_input_json(self, app, middleware):
        """Testa sanitização de entrada JSON"""
        malicious_data = {
            'username': '<script>alert("xss")</script>',
            'email': 'test@example.com',
            'message': 'Hello & welcome <b>user</b>'
        }
        
        with app.test_request_context('/test', method='POST', 
                                    data=json.dumps(malicious_data),
                                    content_type='application/json'):
            middleware.sanitize_input()
            
            # Verificar se dados foram sanitizados
            sanitized_data = request.get_json()
            assert '&lt;script&gt;alert("xss")&lt;/script&gt;' in sanitized_data['username']
            assert '&amp;' in sanitized_data['message']
    
    def test_sanitize_string(self, middleware):
        """Testa sanitização de string"""
        malicious_string = '<script>alert("xss")</script> & "quotes"'
        sanitized = middleware.sanitize_string(malicious_string)
        
        assert '<script>' not in sanitized
        assert '&lt;script&gt;' in sanitized
        assert '&amp;' in sanitized
        assert '&quot;' in sanitized
    
    def test_sanitize_dict(self, middleware):
        """Testa sanitização de dicionário"""
        data = {
            'name': '<b>John</b>',
            'nested': {
                'description': 'Hello & world'
            },
            'list': ['<script>', 'normal text']
        }
        
        sanitized = middleware.sanitize_dict(data)
        
        assert '&lt;b&gt;John&lt;/b&gt;' in sanitized['name']
        assert '&amp;' in sanitized['nested']['description']
        assert '&lt;script&gt;' in sanitized['list'][0]
        assert 'normal text' == sanitized['list'][1]
    
    def test_generate_request_id(self, middleware):
        """Testa geração de ID de requisição"""
        request_id = middleware.generate_request_id()
        
        assert isinstance(request_id, str)
        assert '-' in request_id
        assert len(request_id) > 10
    
    def test_get_client_id_user(self, app, middleware):
        """Testa obtenção de ID do cliente - usuário autenticado"""
        with app.test_request_context('/test'):
            # Simular usuário autenticado
            g.user = Mock()
            g.user.id = 123
            
            client_id = middleware.get_client_id()
            assert client_id == 'user:123'
    
    def test_get_client_id_ip(self, app, middleware):
        """Testa obtenção de ID do cliente - IP"""
        with app.test_request_context('/test'):
            # Simular IP
            request.remote_addr = '192.168.1.1'
            
            client_id = middleware.get_client_id()
            assert client_id == 'ip:192.168.1.1'
    
    def test_handle_payload_too_large(self, middleware):
        """Testa handler para payload muito grande"""
        error = RequestEntityTooLarge("Payload too large")
        response = middleware.handle_payload_too_large(error)
        
        assert response.status_code == 413
        data = json.loads(response.get_data())
        assert 'Payload too large' in data['error']
    
    def test_handle_bad_request(self, middleware):
        """Testa handler para requisição malformada"""
        error = BadRequest("Invalid header")
        response = middleware.handle_bad_request(error)
        
        assert response.status_code == 400
        data = json.loads(response.get_data())
        assert 'Bad request' in data['error']
    
    def test_after_request_headers(self, app, middleware):
        """Testa headers adicionados após requisição"""
        with app.test_request_context('/test'):
            response = app.make_response(jsonify({'test': 'data'}))
            
            # Simular informações de rate limit
            g.rate_limit_info = {
                'limit': 100,
                'remaining': 95,
                'reset': int(time.time()) + 60
            }
            
            modified_response = middleware.after_request(response)
            
            # Verificar headers de segurança
            assert modified_response.headers['X-Content-Type-Options'] == 'nosniff'
            assert modified_response.headers['X-Frame-Options'] == 'DENY'
            assert modified_response.headers['X-XSS-Protection'] == '1; mode=block'
            
            # Verificar headers de rate limit
            assert 'X-RateLimit-Limit' in modified_response.headers
            assert 'X-RateLimit-Remaining' in modified_response.headers
            assert 'X-RateLimit-Reset' in modified_response.headers

class TestPasswordStrengthValidator:
    """Testes para o validador de força de senha"""
    
    @pytest.fixture
    def validator(self):
        """Cria instância do validador"""
        from app.security.password_strength import PasswordStrengthValidator
        return PasswordStrengthValidator()
    
    def test_validate_password_empty(self, validator):
        """Testa validação de senha vazia"""
        result = validator.validate_password("")
        
        assert not result.is_valid
        assert result.strength.value == "very_weak"
        assert result.score == 0
        assert "Senha é obrigatória" in result.feedback[0]
    
    def test_validate_password_too_short(self, validator):
        """Testa validação de senha muito curta"""
        result = validator.validate_password("abc")
        
        assert not result.is_valid
        assert "pelo menos 8 caracteres" in result.feedback[0]
    
    def test_validate_password_common(self, validator):
        """Testa validação de senha comum"""
        result = validator.validate_password("password")
        
        assert not result.is_valid
        assert "muito comum" in result.feedback[0]
        assert "senha_comum" in result.common_patterns
    
    def test_validate_password_strong(self, validator):
        """Testa validação de senha forte"""
        result = validator.validate_password("MyStr0ng!P@ssw0rd")
        
        assert result.is_valid
        assert result.strength.value in ["strong", "very_strong"]
        assert result.score >= 60
    
    def test_validate_password_with_username(self, validator):
        """Testa validação de senha com username"""
        result = validator.validate_password("john123", username="john")
        
        assert not result.is_valid
        assert "não deve conter o nome de usuário" in result.feedback[0]
    
    def test_validate_password_with_email(self, validator):
        """Testa validação de senha com email"""
        result = validator.validate_password("test123", email="test@example.com")
        
        assert not result.is_valid
        assert "não deve conter partes do email" in result.feedback[0]
    
    def test_generate_strong_password(self, validator):
        """Testa geração de senha forte"""
        password = validator.generate_strong_password(16)
        
        assert len(password) == 16
        assert re.search(r'[a-z]', password)  # minúscula
        assert re.search(r'[A-Z]', password)  # maiúscula
        assert re.search(r'\d', password)     # número
        assert re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password)  # especial
    
    def test_get_strength_description(self, validator):
        """Testa descrição da força da senha"""
        from app.security.password_strength import PasswordStrength
        
        description = validator.get_strength_description(PasswordStrength.STRONG)
        assert "Forte" in description

class TestValidateInputDecorator:
    """Testes para o decorator de validação de entrada"""
    
    @pytest.fixture
    def app(self):
        """Cria aplicação Flask para testes"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app
    
    def test_validate_input_success(self, app):
        """Testa decorator de validação - sucesso"""
        @app.route('/test', methods=['POST'])
        @validate_input(LoginRequest)
        def test_route():
            return jsonify({'status': 'success'})
        
        with app.test_client() as client:
            data = {
                'username': 'testuser',
                'senha': 'TestPass123!'
            }
            
            response = client.post('/test', 
                                 data=json.dumps(data),
                                 content_type='application/json')
            
            assert response.status_code == 200
            assert json.loads(response.get_data())['status'] == 'success'
    
    def test_validate_input_failure(self, app):
        """Testa decorator de validação - falha"""
        @app.route('/test', methods=['POST'])
        @validate_input(LoginRequest)
        def test_route():
            return jsonify({'status': 'success'})
        
        with app.test_client() as client:
            data = {
                'username': '',  # Inválido
                'senha': '123'   # Muito curta
            }
            
            response = client.post('/test', 
                                 data=json.dumps(data),
                                 content_type='application/json')
            
            assert response.status_code == 422
            data = json.loads(response.get_data())
            assert 'Validation error' in data['error']

if __name__ == '__main__':
    pytest.main([__file__]) 