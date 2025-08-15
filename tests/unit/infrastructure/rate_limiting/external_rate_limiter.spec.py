"""
Testes Unitários para Rate Limiter Externo - Omni Keywords Finder
Testes abrangentes para rate limiting de APIs externas
Prompt: Rate limiting para consumo externo
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import time
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from app.utils.external_rate_limiter import (
    ExternalRateLimiter,
    external_rate_limit,
    external_get_rate_limit,
    external_post_rate_limit
)

class TestExternalRateLimiter:
    """Testes para o rate limiter externo"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.rate_limiter = ExternalRateLimiter()
        self.mock_request = Mock()
        self.mock_request.remote_addr = "192.168.1.1"
        self.mock_request.headers = {
            'User-Agent': 'TestAgent/1.0',
            'X-Forwarded-For': '10.0.0.1'
        }
    
    def test_init_default_config(self):
        """Testa inicialização com configurações padrão"""
        assert self.rate_limiter.default_limits['get']['requests'] == 60
        assert self.rate_limiter.default_limits['post']['requests'] == 30
        assert self.rate_limiter.default_limits['put']['requests'] == 20
        assert self.rate_limiter.default_limits['delete']['requests'] == 10
        assert self.rate_limiter.default_limits['patch']['requests'] == 20
    
    def test_client_limits_config(self):
        """Testa configurações de limites por tipo de cliente"""
        assert self.rate_limiter.client_limits['free']['multiplier'] == 0.5
        assert self.rate_limiter.client_limits['basic']['multiplier'] == 1.0
        assert self.rate_limiter.client_limits['premium']['multiplier'] == 2.0
        assert self.rate_limiter.client_limits['enterprise']['multiplier'] == 5.0
    
    def test_get_client_identifier_basic(self):
        """Testa obtenção de identificador básico do cliente"""
        identifier = self.rate_limiter.get_client_identifier(self.mock_request)
        assert len(identifier) == 16
        assert isinstance(identifier, str)
    
    def test_get_client_identifier_with_api_key(self):
        """Testa obtenção de identificador com API key"""
        self.mock_request.headers['X-API-Key'] = 'sk_test_123456789'
        identifier = self.rate_limiter.get_client_identifier(self.mock_request)
        assert len(identifier) == 16
        assert isinstance(identifier, str)
    
    def test_get_client_identifier_with_bearer_token(self):
        """Testa obtenção de identificador com Bearer token"""
        self.mock_request.headers['Authorization'] = 'Bearer sk_test_123456789'
        identifier = self.rate_limiter.get_client_identifier(self.mock_request)
        assert len(identifier) == 16
        assert isinstance(identifier, str)
    
    def test_get_client_type_header(self):
        """Testa determinação de tipo de cliente por header"""
        self.mock_request.headers['X-Client-Type'] = 'premium'
        client_type = self.rate_limiter.get_client_type(self.mock_request)
        assert client_type == 'premium'
    
    def test_get_client_type_enterprise_api_key(self):
        """Testa determinação de tipo de cliente por API key enterprise"""
        self.mock_request.headers['X-API-Key'] = 'sk_enterprise_123456789'
        client_type = self.rate_limiter.get_client_type(self.mock_request)
        assert client_type == 'enterprise'
    
    def test_get_client_type_premium_api_key(self):
        """Testa determinação de tipo de cliente por API key premium"""
        self.mock_request.headers['X-API-Key'] = 'sk_premium_123456789'
        client_type = self.rate_limiter.get_client_type(self.mock_request)
        assert client_type == 'premium'
    
    def test_get_client_type_basic_api_key(self):
        """Testa determinação de tipo de cliente por API key basic"""
        self.mock_request.headers['X-API-Key'] = 'sk_basic_123456789'
        client_type = self.rate_limiter.get_client_type(self.mock_request)
        assert client_type == 'basic'
    
    def test_get_client_type_free_default(self):
        """Testa determinação de tipo de cliente free por padrão"""
        client_type = self.rate_limiter.get_client_type(self.mock_request)
        assert client_type == 'free'
    
    def test_get_rate_limit_config_free_get(self):
        """Testa configuração de rate limit para cliente free com GET"""
        config = self.rate_limiter.get_rate_limit_config('get', 'free')
        assert config['requests'] == 30  # 60 * 0.5
        assert config['window'] == 60
    
    def test_get_rate_limit_config_basic_post(self):
        """Testa configuração de rate limit para cliente basic com POST"""
        config = self.rate_limiter.get_rate_limit_config('post', 'basic')
        assert config['requests'] == 30  # 30 * 1.0
        assert config['window'] == 60
    
    def test_get_rate_limit_config_premium_put(self):
        """Testa configuração de rate limit para cliente premium com PUT"""
        config = self.rate_limiter.get_rate_limit_config('put', 'premium')
        assert config['requests'] == 40  # 20 * 2.0
        assert config['window'] == 60
    
    def test_get_rate_limit_config_enterprise_delete(self):
        """Testa configuração de rate limit para cliente enterprise com DELETE"""
        config = self.rate_limiter.get_rate_limit_config('delete', 'enterprise')
        assert config['requests'] == 50  # 10 * 5.0
        assert config['window'] == 60
    
    def test_get_rate_limit_config_unknown_method(self):
        """Testa configuração de rate limit para método desconhecido"""
        config = self.rate_limiter.get_rate_limit_config('unknown', 'basic')
        assert config['requests'] == 60  # Usa GET como padrão
        assert config['window'] == 60
    
    def test_get_rate_limit_config_unknown_client_type(self):
        """Testa configuração de rate limit para tipo de cliente desconhecido"""
        config = self.rate_limiter.get_rate_limit_config('get', 'unknown')
        assert config['requests'] == 60  # Usa multiplier 1.0 como padrão
        assert config['window'] == 60

class TestExternalRateLimiterWithRedis:
    """Testes para rate limiter com Redis"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.rate_limiter = ExternalRateLimiter()
        self.mock_request = Mock()
        self.mock_request.remote_addr = "192.168.1.1"
        self.mock_request.headers = {
            'User-Agent': 'TestAgent/1.0'
        }
    
    @patch('app.utils.external_rate_limiter.redis.Redis')
    def test_check_rate_limit_with_redis_success(self, mock_redis):
        """Testa verificação de rate limit com Redis - sucesso"""
        # Mock do Redis
        mock_redis_instance = Mock()
        mock_redis_instance.incr.return_value = 1
        mock_redis_instance.expire.return_value = True
        mock_redis.return_value = mock_redis_instance
        
        # Mock da conexão
        self.rate_limiter.redis_client = mock_redis_instance
        
        client_id = self.rate_limiter.get_client_identifier(self.mock_request)
        allowed, rate_info = self.rate_limiter.check_rate_limit(client_id, 'get', 'basic')
        
        assert allowed is True
        assert rate_info['remaining'] == 59  # 60 - 1
        assert 'reset_time' in rate_info
        assert rate_info['limit'] == 60
        assert rate_info['window'] == 60
        assert rate_info['client_type'] == 'basic'
    
    @patch('app.utils.external_rate_limiter.redis.Redis')
    def test_check_rate_limit_with_redis_exceeded(self, mock_redis):
        """Testa verificação de rate limit com Redis - limite excedido"""
        # Mock do Redis
        mock_redis_instance = Mock()
        mock_redis_instance.incr.return_value = 61  # Excede o limite de 60
        mock_redis_instance.expire.return_value = True
        mock_redis.return_value = mock_redis_instance
        
        # Mock da conexão
        self.rate_limiter.redis_client = mock_redis_instance
        
        client_id = self.rate_limiter.get_client_identifier(self.mock_request)
        allowed, rate_info = self.rate_limiter.check_rate_limit(client_id, 'get', 'basic')
        
        assert allowed is False
        assert rate_info['remaining'] == 0
        assert 'retry_after' in rate_info
        assert rate_info['limit'] == 60
        assert rate_info['window'] == 60
        assert rate_info['client_type'] == 'basic'
        assert rate_info['current_count'] == 61
    
    @patch('app.utils.external_rate_limiter.redis.Redis')
    def test_check_rate_limit_with_redis_error(self, mock_redis):
        """Testa verificação de rate limit com Redis - erro"""
        # Mock do Redis com erro
        mock_redis_instance = Mock()
        mock_redis_instance.incr.side_effect = Exception("Redis error")
        mock_redis.return_value = mock_redis_instance
        
        # Mock da conexão
        self.rate_limiter.redis_client = mock_redis_instance
        
        client_id = self.rate_limiter.get_client_identifier(self.mock_request)
        allowed, rate_info = self.rate_limiter.check_rate_limit(client_id, 'get', 'basic')
        
        # Deve permitir em caso de erro (fallback)
        assert allowed is True
        assert rate_info['remaining'] == 60
        assert 'reset_time' in rate_info
    
    def test_check_rate_limit_without_redis(self):
        """Testa verificação de rate limit sem Redis"""
        # Sem Redis
        self.rate_limiter.redis_client = None
        
        client_id = self.rate_limiter.get_client_identifier(self.mock_request)
        allowed, rate_info = self.rate_limiter.check_rate_limit(client_id, 'get', 'basic')
        
        # Deve permitir sem Redis (fallback)
        assert allowed is True
        assert rate_info['remaining'] == 60
        assert 'reset_time' in rate_info
        assert rate_info['limit'] == 60
        assert rate_info['window'] == 60
        assert rate_info['client_type'] == 'basic'

class TestExternalRateLimiterLogging:
    """Testes para logging do rate limiter"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.rate_limiter = ExternalRateLimiter()
        self.mock_request = Mock()
        self.mock_request.remote_addr = "192.168.1.1"
        self.mock_request.headers = {
            'User-Agent': 'TestAgent/1.0'
        }
    
    @patch('app.utils.external_rate_limiter.security_logger')
    @patch('app.utils.external_rate_limiter.logger')
    def test_log_rate_limit_exceeded(self, mock_logger, mock_security_logger):
        """Testa logging de rate limit excedido"""
        with patch('app.utils.external_rate_limiter.request', self.mock_request):
            self.rate_limiter._log_rate_limit_exceeded(
                key="test_key",
                method="get",
                client_type="basic",
                config={'requests': 60, 'window': 60},
                current_count=61
            )
            
            # Verifica se o security logger foi chamado
            mock_security_logger.log_security_event.assert_called_once()
            call_args = mock_security_logger.log_security_event.call_args
            assert call_args[1]['event_type'] == 'rate_limit_exceeded'
            assert call_args[1]['severity'] == 'warning'
            
            # Verifica se o logger foi chamado
            mock_logger.warning.assert_called_once()
            log_message = mock_logger.warning.call_args[0][0]
            assert "Rate limit excedido" in log_message
            assert "test_key" in log_message
            assert "get" in log_message
            assert "basic" in log_message

class TestExternalRateLimiterStats:
    """Testes para estatísticas do rate limiter"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.rate_limiter = ExternalRateLimiter()
    
    @patch('app.utils.external_rate_limiter.redis.Redis')
    def test_get_rate_limit_stats_success(self, mock_redis):
        """Testa obtenção de estatísticas de rate limit"""
        # Mock do Redis
        mock_redis_instance = Mock()
        mock_redis_instance.keys.return_value = [
            'external_rate_limit:test_key:get:1640995200',
            'external_rate_limit:test_key:post:1640995200'
        ]
        mock_redis_instance.get.side_effect = ['10', '5']
        mock_redis.return_value = mock_redis_instance
        
        # Mock da conexão
        self.rate_limiter.redis_client = mock_redis_instance
        
        stats = self.rate_limiter.get_rate_limit_stats('test_key')
        
        assert 'get' in stats
        assert 'post' in stats
        assert stats['get']['current_count'] == 10
        assert stats['post']['current_count'] == 5
        assert len(stats['get']['windows']) == 1
        assert len(stats['post']['windows']) == 1
    
    @patch('app.utils.external_rate_limiter.redis.Redis')
    def test_get_rate_limit_stats_specific_method(self, mock_redis):
        """Testa obtenção de estatísticas para método específico"""
        # Mock do Redis
        mock_redis_instance = Mock()
        mock_redis_instance.keys.return_value = [
            'external_rate_limit:test_key:get:1640995200'
        ]
        mock_redis_instance.get.return_value = '10'
        mock_redis.return_value = mock_redis_instance
        
        # Mock da conexão
        self.rate_limiter.redis_client = mock_redis_instance
        
        stats = self.rate_limiter.get_rate_limit_stats('test_key', method='get')
        
        assert 'get' in stats
        assert 'post' not in stats
        assert stats['get']['current_count'] == 10
    
    def test_get_rate_limit_stats_without_redis(self):
        """Testa obtenção de estatísticas sem Redis"""
        # Sem Redis
        self.rate_limiter.redis_client = None
        
        stats = self.rate_limiter.get_rate_limit_stats('test_key')
        
        assert stats == {"error": "Redis não disponível"}
    
    @patch('app.utils.external_rate_limiter.redis.Redis')
    def test_get_rate_limit_stats_redis_error(self, mock_redis):
        """Testa obtenção de estatísticas com erro no Redis"""
        # Mock do Redis com erro
        mock_redis_instance = Mock()
        mock_redis_instance.keys.side_effect = Exception("Redis error")
        mock_redis.return_value = mock_redis_instance
        
        # Mock da conexão
        self.rate_limiter.redis_client = mock_redis_instance
        
        stats = self.rate_limiter.get_rate_limit_stats('test_key')
        
        assert "error" in stats
        assert "Redis error" in stats["error"]

class TestExternalRateLimitDecorators:
    """Testes para decorators de rate limiting"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.mock_request = Mock()
        self.mock_request.remote_addr = "192.168.1.1"
        self.mock_request.method = "GET"
        self.mock_request.headers = {
            'User-Agent': 'TestAgent/1.0'
        }
    
    @patch('app.utils.external_rate_limiter.request')
    @patch('app.utils.external_rate_limiter.jsonify')
    def test_external_rate_limit_decorator_success(self, mock_jsonify, mock_request):
        """Testa decorator de rate limiting - sucesso"""
        mock_request.remote_addr = "192.168.1.1"
        mock_request.method = "GET"
        mock_request.headers = {'User-Agent': 'TestAgent/1.0'}
        
        # Mock do rate limiter
        with patch('app.utils.external_rate_limiter.ExternalRateLimiter') as mock_limiter_class:
            mock_limiter = Mock()
            mock_limiter.get_client_identifier.return_value = "test_client"
            mock_limiter.get_client_type.return_value = "basic"
            mock_limiter.check_rate_limit.return_value = (True, {
                'remaining': 59,
                'reset_time': 1640995260,
                'limit': 60,
                'window': 60,
                'client_type': 'basic'
            })
            mock_limiter_class.return_value = mock_limiter
            
            # Função de teste
            @external_rate_limit()
            def test_function():
                return "success", 200
            
            # Mock da resposta
            mock_response = Mock()
            mock_response.headers = {}
            mock_jsonify.return_value = mock_response
            
            # Executar função
            result = test_function()
            
            # Verificar se rate limiter foi chamado
            mock_limiter.get_client_identifier.assert_called_once()
            mock_limiter.get_client_type.assert_called_once()
            mock_limiter.check_rate_limit.assert_called_once()
    
    @patch('app.utils.external_rate_limiter.request')
    @patch('app.utils.external_rate_limiter.jsonify')
    def test_external_rate_limit_decorator_exceeded(self, mock_jsonify, mock_request):
        """Testa decorator de rate limiting - limite excedido"""
        mock_request.remote_addr = "192.168.1.1"
        mock_request.method = "GET"
        mock_request.headers = {'User-Agent': 'TestAgent/1.0'}
        
        # Mock do rate limiter
        with patch('app.utils.external_rate_limiter.ExternalRateLimiter') as mock_limiter_class:
            mock_limiter = Mock()
            mock_limiter.get_client_identifier.return_value = "test_client"
            mock_limiter.get_client_type.return_value = "basic"
            mock_limiter.check_rate_limit.return_value = (False, {
                'remaining': 0,
                'reset_time': 1640995260,
                'retry_after': 60,
                'limit': 60,
                'window': 60,
                'client_type': 'basic'
            })
            mock_limiter_class.return_value = mock_limiter
            
            # Função de teste
            @external_rate_limit()
            def test_function():
                return "success", 200
            
            # Mock da resposta
            mock_response = Mock()
            mock_response.headers = {}
            mock_jsonify.return_value = mock_response
            
            # Executar função
            result = test_function()
            
            # Verificar se retornou 429
            assert result[1] == 429
            assert "Rate limit exceeded" in result[0].json['error']
    
    def test_external_get_rate_limit_decorator(self):
        """Testa decorator específico para GET"""
        @external_get_rate_limit
        def test_get_function():
            return "success", 200
        
        # Verificar se o decorator foi aplicado
        assert hasattr(test_get_function, '__wrapped__')
    
    def test_external_post_rate_limit_decorator(self):
        """Testa decorator específico para POST"""
        @external_post_rate_limit
        def test_post_function():
            return "success", 200
        
        # Verificar se o decorator foi aplicado
        assert hasattr(test_post_function, '__wrapped__')

class TestExternalRateLimiterEdgeCases:
    """Testes de casos extremos para rate limiter"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.rate_limiter = ExternalRateLimiter()
    
    def test_get_client_identifier_empty_headers(self):
        """Testa identificador com headers vazios"""
        mock_request = Mock()
        mock_request.remote_addr = "192.168.1.1"
        mock_request.headers = {}
        
        identifier = self.rate_limiter.get_client_identifier(mock_request)
        assert len(identifier) == 16
        assert isinstance(identifier, str)
    
    def test_get_client_identifier_none_values(self):
        """Testa identificador com valores None"""
        mock_request = Mock()
        mock_request.remote_addr = None
        mock_request.headers = {
            'User-Agent': None,
            'X-API-Key': None
        }
        
        identifier = self.rate_limiter.get_client_identifier(mock_request)
        assert len(identifier) == 16
        assert isinstance(identifier, str)
    
    def test_get_client_type_invalid_header(self):
        """Testa tipo de cliente com header inválido"""
        mock_request = Mock()
        mock_request.headers = {'X-Client-Type': 'invalid_type'}
        
        client_type = self.rate_limiter.get_client_type(mock_request)
        assert client_type == 'free'  # Deve retornar free como padrão
    
    def test_get_rate_limit_config_edge_multipliers(self):
        """Testa configuração com multiplicadores extremos"""
        # Teste com multiplicador muito alto
        config = self.rate_limiter.get_rate_limit_config('get', 'enterprise')
        assert config['requests'] == 300  # 60 * 5.0
        assert config['window'] == 60
        
        # Teste com multiplicador baixo
        config = self.rate_limiter.get_rate_limit_config('get', 'free')
        assert config['requests'] == 30  # 60 * 0.5
        assert config['window'] == 60
    
    def test_get_rate_limit_config_case_insensitive(self):
        """Testa configuração case insensitive"""
        # Método em maiúsculo
        config = self.rate_limiter.get_rate_limit_config('GET', 'BASIC')
        assert config['requests'] == 60
        assert config['window'] == 60
        
        # Método em minúsculo
        config = self.rate_limiter.get_rate_limit_config('get', 'basic')
        assert config['requests'] == 60
        assert config['window'] == 60

if __name__ == "__main__":
    pytest.main([__file__]) 