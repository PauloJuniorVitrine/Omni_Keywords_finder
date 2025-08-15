"""
Testes Unitários para Refresh Token Manager
Gerenciador de Refresh Tokens - Omni Keywords Finder

Prompt: Implementação de testes unitários para gerenciador de refresh tokens
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import jwt
import uuid
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Optional, List

from backend.app.utils.refresh_token_manager import (
    RefreshTokenManager,
    TokenPair,
    TokenInfo,
    create_token_pair,
    refresh_access_token,
    revoke_token,
    revoke_all_user_tokens,
    validate_access_token
)


class TestTokenPair:
    """Testes para TokenPair"""
    
    def test_token_pair_creation(self):
        """Testa criação de TokenPair"""
        access_expires = datetime.utcnow() + timedelta(hours=1)
        refresh_expires = datetime.utcnow() + timedelta(days=7)
        
        token_pair = TokenPair(
            access_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            refresh_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            access_expires_at=access_expires,
            refresh_expires_at=refresh_expires,
            user_id=123,
            token_family="family-123"
        )
        
        assert token_pair.access_token.startswith("eyJ")
        assert token_pair.refresh_token.startswith("eyJ")
        assert token_pair.access_expires_at == access_expires
        assert token_pair.refresh_expires_at == refresh_expires
        assert token_pair.user_id == 123
        assert token_pair.token_family == "family-123"


class TestTokenInfo:
    """Testes para TokenInfo"""
    
    def test_token_info_creation(self):
        """Testa criação de TokenInfo"""
        created_at = datetime.utcnow()
        expires_at = created_at + timedelta(days=7)
        
        token_info = TokenInfo(
            user_id=123,
            token_family="family-123",
            created_at=created_at,
            expires_at=expires_at,
            is_revoked=False
        )
        
        assert token_info.user_id == 123
        assert token_info.token_family == "family-123"
        assert token_info.created_at == created_at
        assert token_info.expires_at == expires_at
        assert token_info.is_revoked is False
    
    def test_token_info_revoked(self):
        """Testa criação de TokenInfo revogado"""
        created_at = datetime.utcnow()
        expires_at = created_at + timedelta(days=7)
        
        token_info = TokenInfo(
            user_id=123,
            token_family="family-123",
            created_at=created_at,
            expires_at=expires_at,
            is_revoked=True
        )
        
        assert token_info.is_revoked is True


class TestRefreshTokenManager:
    """Testes para RefreshTokenManager"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock do Redis"""
        redis_mock = Mock()
        redis_mock.get.return_value = None
        redis_mock.setex.return_value = None
        redis_mock.delete.return_value = None
        redis_mock.exists.return_value = 0
        redis_mock.keys.return_value = []
        return redis_mock
    
    @pytest.fixture
    def token_manager(self, mock_redis):
        """Instância do RefreshTokenManager para testes"""
        with patch('backend.app.utils.refresh_token_manager.redis') as mock_redis_module:
            mock_redis_module.from_url.return_value = mock_redis
            
            with patch.dict('os.environ', {
                'JWT_REFRESH_SECRET_KEY': 'test-refresh-secret',
                'JWT_SECRET_KEY': 'test-access-secret',
                'JWT_ACCESS_TOKEN_EXPIRES': '3600',
                'JWT_REFRESH_TOKEN_EXPIRES': '604800',
                'MAX_REFRESH_TOKENS_PER_USER': '5',
                'ENABLE_TOKEN_ROTATION': 'true'
            }):
                return RefreshTokenManager()
    
    def test_token_manager_initialization(self, token_manager):
        """Testa inicialização do RefreshTokenManager"""
        assert token_manager.refresh_secret == "test-refresh-secret"
        assert token_manager.access_secret == "test-access-secret"
        assert token_manager.access_token_expires == 3600
        assert token_manager.refresh_token_expires == 604800
        assert token_manager.max_refresh_tokens_per_user == 5
        assert token_manager.enable_token_rotation is True
        assert token_manager.redis_client is not None
    
    def test_token_manager_initialization_no_redis(self):
        """Testa inicialização do RefreshTokenManager sem Redis"""
        with patch('backend.app.utils.refresh_token_manager.redis') as mock_redis_module:
            mock_redis_module.from_url.side_effect = Exception("Redis connection failed")
            
            with patch.dict('os.environ', {
                'JWT_REFRESH_SECRET_KEY': 'test-refresh-secret',
                'JWT_SECRET_KEY': 'test-access-secret',
                'JWT_ACCESS_TOKEN_EXPIRES': '3600',
                'JWT_REFRESH_TOKEN_EXPIRES': '604800',
                'MAX_REFRESH_TOKENS_PER_USER': '5',
                'ENABLE_TOKEN_ROTATION': 'true'
            }):
                manager = RefreshTokenManager()
                assert manager.redis_client is None
    
    def test_create_token_pair(self, token_manager, mock_redis):
        """Testa criação de par de tokens"""
        user_id = 123
        additional_claims = {"role": "admin", "permissions": ["read", "write"]}
        
        token_pair = token_manager.create_token_pair(user_id, additional_claims)
        
        assert isinstance(token_pair, TokenPair)
        assert token_pair.user_id == user_id
        assert token_pair.token_family is not None
        assert len(token_pair.token_family) > 0
        
        # Verificar se os tokens são JWT válidos
        assert token_pair.access_token.count('.') == 2  # JWT format
        assert token_pair.refresh_token.count('.') == 2  # JWT format
        
        # Verificar expiração
        assert token_pair.access_expires_at > datetime.utcnow()
        assert token_pair.refresh_expires_at > datetime.utcnow()
        assert token_pair.refresh_expires_at > token_pair.access_expires_at
        
        # Verificar se foi armazenado no Redis
        mock_redis.setex.assert_called()
    
    def test_create_token_pair_no_additional_claims(self, token_manager, mock_redis):
        """Testa criação de par de tokens sem claims adicionais"""
        user_id = 123
        
        token_pair = token_manager.create_token_pair(user_id)
        
        assert isinstance(token_pair, TokenPair)
        assert token_pair.user_id == user_id
        
        # Decodificar tokens para verificar claims
        access_payload = jwt.decode(token_pair.access_token, token_manager.access_secret, algorithms=['HS256'])
        refresh_payload = jwt.decode(token_pair.refresh_token, token_manager.refresh_secret, algorithms=['HS256'])
        
        assert access_payload['user_id'] == user_id
        assert access_payload['token_type'] == 'access'
        assert refresh_payload['user_id'] == user_id
        assert refresh_payload['token_type'] == 'refresh'
        assert access_payload['token_family'] == refresh_payload['token_family']
    
    def test_refresh_access_token_valid(self, token_manager, mock_redis):
        """Testa renovação de access token com refresh token válido"""
        # Criar par de tokens inicial
        user_id = 123
        token_pair = token_manager.create_token_pair(user_id)
        
        # Mock de token não na blacklist
        mock_redis.exists.return_value = 0
        
        # Renovar access token
        new_token_pair = token_manager.refresh_access_token(token_pair.refresh_token)
        
        assert new_token_pair is not None
        assert isinstance(new_token_pair, TokenPair)
        assert new_token_pair.user_id == user_id
        assert new_token_pair.token_family == token_pair.token_family
        
        # Verificar se o refresh token anterior foi invalidado (rotação)
        mock_redis.setex.assert_called()  # Adicionado à blacklist
    
    def test_refresh_access_token_invalid_type(self, token_manager):
        """Testa renovação com token de tipo inválido"""
        # Criar access token (não refresh token)
        user_id = 123
        token_pair = token_manager.create_token_pair(user_id)
        
        # Tentar renovar com access token
        result = token_manager.refresh_access_token(token_pair.access_token)
        
        assert result is None
    
    def test_refresh_access_token_expired(self, token_manager):
        """Testa renovação com refresh token expirado"""
        # Criar token com expiração no passado
        user_id = 123
        claims = {
            'user_id': user_id,
            'token_family': str(uuid.uuid4()),
            'token_type': 'refresh',
            'iat': datetime.utcnow() - timedelta(days=8),
            'exp': datetime.utcnow() - timedelta(days=1)  # Expirado
        }
        
        expired_token = jwt.encode(claims, token_manager.refresh_secret, algorithm='HS256')
        
        result = token_manager.refresh_access_token(expired_token)
        
        assert result is None
    
    def test_refresh_access_token_blacklisted(self, token_manager, mock_redis):
        """Testa renovação com refresh token na blacklist"""
        # Criar par de tokens
        user_id = 123
        token_pair = token_manager.create_token_pair(user_id)
        
        # Mock de token na blacklist
        mock_redis.exists.return_value = 1
        
        result = token_manager.refresh_access_token(token_pair.refresh_token)
        
        assert result is None
    
    def test_refresh_access_token_invalid_signature(self, token_manager):
        """Testa renovação com refresh token com assinatura inválida"""
        # Criar token com chave secreta diferente
        user_id = 123
        claims = {
            'user_id': user_id,
            'token_family': str(uuid.uuid4()),
            'token_type': 'refresh',
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(days=7)
        }
        
        invalid_token = jwt.encode(claims, "wrong-secret", algorithm='HS256')
        
        result = token_manager.refresh_access_token(invalid_token)
        
        assert result is None
    
    def test_revoke_token_access_token(self, token_manager, mock_redis):
        """Testa revogação de access token"""
        # Criar par de tokens
        user_id = 123
        token_pair = token_manager.create_token_pair(user_id)
        
        # Revogar access token
        result = token_manager.revoke_token(token_pair.access_token, user_id)
        
        assert result is True
        mock_redis.setex.assert_called()  # Adicionado à blacklist
    
    def test_revoke_token_refresh_token(self, token_manager, mock_redis):
        """Testa revogação de refresh token"""
        # Criar par de tokens
        user_id = 123
        token_pair = token_manager.create_token_pair(user_id)
        
        # Revogar refresh token
        result = token_manager.revoke_token(token_pair.refresh_token, user_id)
        
        assert result is True
        mock_redis.setex.assert_called()  # Adicionado à blacklist
    
    def test_revoke_token_invalid_token(self, token_manager):
        """Testa revogação de token inválido"""
        result = token_manager.revoke_token("invalid-token")
        
        assert result is False
    
    def test_revoke_token_wrong_user_id(self, token_manager):
        """Testa revogação de token com user_id incorreto"""
        # Criar par de tokens
        user_id = 123
        token_pair = token_manager.create_token_pair(user_id)
        
        # Tentar revogar com user_id incorreto
        result = token_manager.revoke_token(token_pair.access_token, user_id=999)
        
        assert result is False
    
    def test_revoke_all_user_tokens(self, token_manager, mock_redis):
        """Testa revogação de todos os tokens de um usuário"""
        user_id = 123
        
        # Mock de tokens existentes
        mock_redis.keys.return_value = [
            f"refresh_token:{user_id}:family1",
            f"refresh_token:{user_id}:family2"
        ]
        
        result = token_manager.revoke_all_user_tokens(user_id)
        
        assert result is True
        # Verificar se todos os tokens foram removidos
        assert mock_redis.delete.call_count == 2
        # Verificar se usuário foi adicionado à blacklist
        mock_redis.setex.assert_called()
    
    def test_revoke_all_user_tokens_no_redis(self):
        """Testa revogação de todos os tokens sem Redis"""
        with patch('backend.app.utils.refresh_token_manager.redis') as mock_redis_module:
            mock_redis_module.from_url.side_effect = Exception("Redis connection failed")
            
            with patch.dict('os.environ', {
                'JWT_REFRESH_SECRET_KEY': 'test-refresh-secret',
                'JWT_SECRET_KEY': 'test-access-secret',
                'JWT_ACCESS_TOKEN_EXPIRES': '3600',
                'JWT_REFRESH_TOKEN_EXPIRES': '604800',
                'MAX_REFRESH_TOKENS_PER_USER': '5',
                'ENABLE_TOKEN_ROTATION': 'true'
            }):
                manager = RefreshTokenManager()
                result = manager.revoke_all_user_tokens(123)
                assert result is False
    
    def test_validate_access_token_valid(self, token_manager, mock_redis):
        """Testa validação de access token válido"""
        # Criar par de tokens
        user_id = 123
        token_pair = token_manager.create_token_pair(user_id)
        
        # Mock de token não na blacklist
        mock_redis.exists.return_value = 0
        
        # Validar access token
        payload = token_manager.validate_access_token(token_pair.access_token)
        
        assert payload is not None
        assert payload['user_id'] == user_id
        assert payload['token_type'] == 'access'
        assert payload['token_family'] == token_pair.token_family
    
    def test_validate_access_token_blacklisted(self, token_manager, mock_redis):
        """Testa validação de access token na blacklist"""
        # Criar par de tokens
        user_id = 123
        token_pair = token_manager.create_token_pair(user_id)
        
        # Mock de token na blacklist
        mock_redis.exists.return_value = 1
        
        # Validar access token
        payload = token_manager.validate_access_token(token_pair.access_token)
        
        assert payload is None
    
    def test_validate_access_token_wrong_type(self, token_manager, mock_redis):
        """Testa validação de token com tipo incorreto"""
        # Criar par de tokens
        user_id = 123
        token_pair = token_manager.create_token_pair(user_id)
        
        # Mock de token não na blacklist
        mock_redis.exists.return_value = 0
        
        # Tentar validar refresh token como access token
        payload = token_manager.validate_access_token(token_pair.refresh_token)
        
        assert payload is None
    
    def test_validate_access_token_expired(self, token_manager, mock_redis):
        """Testa validação de access token expirado"""
        # Criar token com expiração no passado
        user_id = 123
        claims = {
            'user_id': user_id,
            'token_family': str(uuid.uuid4()),
            'token_type': 'access',
            'iat': datetime.utcnow() - timedelta(hours=2),
            'exp': datetime.utcnow() - timedelta(hours=1)  # Expirado
        }
        
        expired_token = jwt.encode(claims, token_manager.access_secret, algorithm='HS256')
        
        # Mock de token não na blacklist
        mock_redis.exists.return_value = 0
        
        payload = token_manager.validate_access_token(expired_token)
        
        assert payload is None
    
    def test_validate_access_token_invalid_signature(self, token_manager, mock_redis):
        """Testa validação de access token com assinatura inválida"""
        # Criar token com chave secreta diferente
        user_id = 123
        claims = {
            'user_id': user_id,
            'token_family': str(uuid.uuid4()),
            'token_type': 'access',
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=1)
        }
        
        invalid_token = jwt.encode(claims, "wrong-secret", algorithm='HS256')
        
        # Mock de token não na blacklist
        mock_redis.exists.return_value = 0
        
        payload = token_manager.validate_access_token(invalid_token)
        
        assert payload is None
    
    def test_store_refresh_token(self, token_manager, mock_redis):
        """Testa armazenamento de refresh token"""
        refresh_token = "test-refresh-token"
        user_id = 123
        token_family = "family-123"
        
        token_manager._store_refresh_token(refresh_token, user_id, token_family)
        
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert f"refresh_token:{user_id}:{token_family}" in call_args[0]
        assert call_args[0][1] == token_manager.refresh_token_expires
        assert call_args[0][2] == refresh_token
    
    def test_is_token_blacklisted(self, token_manager, mock_redis):
        """Testa verificação de token na blacklist"""
        token = "test-token"
        
        # Mock de token na blacklist
        mock_redis.exists.return_value = 1
        
        result = token_manager._is_token_blacklisted(token)
        
        assert result is True
        mock_redis.exists.assert_called_once()
    
    def test_is_token_not_blacklisted(self, token_manager, mock_redis):
        """Testa verificação de token não na blacklist"""
        token = "test-token"
        
        # Mock de token não na blacklist
        mock_redis.exists.return_value = 0
        
        result = token_manager._is_token_blacklisted(token)
        
        assert result is False
    
    def test_blacklist_token(self, token_manager, mock_redis):
        """Testa adição de token à blacklist"""
        token = "test-token"
        user_id = 123
        token_family = "family-123"
        
        result = token_manager._blacklist_token(token, user_id, token_family)
        
        assert result is True
        # Verificar se foi adicionado à blacklist
        mock_redis.setex.assert_called()
        # Verificar se foi removido da lista de tokens ativos
        mock_redis.delete.assert_called_once()
    
    def test_cleanup_old_tokens(self, token_manager, mock_redis):
        """Testa limpeza de tokens antigos"""
        user_id = 123
        
        # Mock de tokens existentes (mais que o limite)
        mock_redis.keys.return_value = [
            f"refresh_token:{user_id}:family1",
            f"refresh_token:{user_id}:family2",
            f"refresh_token:{user_id}:family3",
            f"refresh_token:{user_id}:family4",
            f"refresh_token:{user_id}:family5",
            f"refresh_token:{user_id}:family6"  # Excede limite de 5
        ]
        
        token_manager._cleanup_old_tokens(user_id)
        
        # Verificar se tokens antigos foram removidos
        assert mock_redis.delete.call_count > 0
    
    def test_get_user_active_tokens(self, token_manager, mock_redis):
        """Testa obtenção de tokens ativos do usuário"""
        user_id = 123
        
        # Mock de tokens existentes
        mock_redis.keys.return_value = [
            f"refresh_token:{user_id}:family1",
            f"refresh_token:{user_id}:family2"
        ]
        
        # Mock de tokens válidos
        valid_token = jwt.encode({
            'user_id': user_id,
            'token_family': 'family1',
            'token_type': 'refresh',
            'iat': datetime.utcnow().timestamp(),
            'exp': (datetime.utcnow() + timedelta(days=7)).timestamp()
        }, token_manager.refresh_secret, algorithm='HS256')
        
        mock_redis.get.side_effect = [valid_token, None]  # Um válido, um None
        
        tokens = token_manager.get_user_active_tokens(user_id)
        
        assert len(tokens) == 1
        assert tokens[0]['token_family'] == 'family1'
        assert tokens[0]['is_active'] is True
    
    def test_get_user_active_tokens_no_redis(self):
        """Testa obtenção de tokens ativos sem Redis"""
        with patch('backend.app.utils.refresh_token_manager.redis') as mock_redis_module:
            mock_redis_module.from_url.side_effect = Exception("Redis connection failed")
            
            with patch.dict('os.environ', {
                'JWT_REFRESH_SECRET_KEY': 'test-refresh-secret',
                'JWT_SECRET_KEY': 'test-access-secret',
                'JWT_ACCESS_TOKEN_EXPIRES': '3600',
                'JWT_REFRESH_TOKEN_EXPIRES': '604800',
                'MAX_REFRESH_TOKENS_PER_USER': '5',
                'ENABLE_TOKEN_ROTATION': 'true'
            }):
                manager = RefreshTokenManager()
                tokens = manager.get_user_active_tokens(123)
                assert tokens == []
    
    def test_get_blacklist_stats(self, token_manager, mock_redis):
        """Testa obtenção de estatísticas da blacklist"""
        # Mock de chaves na blacklist
        mock_redis.keys.side_effect = [
            ["blacklist:1", "blacklist:2", "blacklist:3"],  # Tokens blacklisted
            ["user_blacklist:1", "user_blacklist:2"]  # Usuários blacklisted
        ]
        
        stats = token_manager.get_blacklist_stats()
        
        assert stats['total_blacklisted_tokens'] == 3
        assert stats['total_blacklisted_users'] == 2
        assert stats['redis_available'] is True
    
    def test_get_blacklist_stats_no_redis(self):
        """Testa obtenção de estatísticas da blacklist sem Redis"""
        with patch('backend.app.utils.refresh_token_manager.redis') as mock_redis_module:
            mock_redis_module.from_url.side_effect = Exception("Redis connection failed")
            
            with patch.dict('os.environ', {
                'JWT_REFRESH_SECRET_KEY': 'test-refresh-secret',
                'JWT_SECRET_KEY': 'test-access-secret',
                'JWT_ACCESS_TOKEN_EXPIRES': '3600',
                'JWT_REFRESH_TOKEN_EXPIRES': '604800',
                'MAX_REFRESH_TOKENS_PER_USER': '5',
                'ENABLE_TOKEN_ROTATION': 'true'
            }):
                manager = RefreshTokenManager()
                stats = manager.get_blacklist_stats()
                assert stats['error'] == 'Redis não disponível'


class TestRefreshTokenManagerNoRedis:
    """Testes para RefreshTokenManager sem Redis"""
    
    @pytest.fixture
    def token_manager_no_redis(self):
        """Instância do RefreshTokenManager sem Redis"""
        with patch('backend.app.utils.refresh_token_manager.redis') as mock_redis_module:
            mock_redis_module.from_url.side_effect = Exception("Redis connection failed")
            
            with patch.dict('os.environ', {
                'JWT_REFRESH_SECRET_KEY': 'test-refresh-secret',
                'JWT_SECRET_KEY': 'test-access-secret',
                'JWT_ACCESS_TOKEN_EXPIRES': '3600',
                'JWT_REFRESH_TOKEN_EXPIRES': '604800',
                'MAX_REFRESH_TOKENS_PER_USER': '5',
                'ENABLE_TOKEN_ROTATION': 'true'
            }):
                return RefreshTokenManager()
    
    def test_create_token_pair_no_redis(self, token_manager_no_redis):
        """Testa criação de par de tokens sem Redis"""
        user_id = 123
        
        token_pair = token_manager_no_redis.create_token_pair(user_id)
        
        assert isinstance(token_pair, TokenPair)
        assert token_pair.user_id == user_id
        # Sem Redis, ainda deve funcionar mas não armazenar
    
    def test_refresh_access_token_no_redis(self, token_manager_no_redis):
        """Testa renovação de access token sem Redis"""
        # Criar par de tokens
        user_id = 123
        token_pair = token_manager_no_redis.create_token_pair(user_id)
        
        # Renovar access token
        new_token_pair = token_manager_no_redis.refresh_access_token(token_pair.refresh_token)
        
        assert new_token_pair is not None
        assert isinstance(new_token_pair, TokenPair)
        assert new_token_pair.user_id == user_id
    
    def test_validate_access_token_no_redis(self, token_manager_no_redis):
        """Testa validação de access token sem Redis"""
        # Criar par de tokens
        user_id = 123
        token_pair = token_manager_no_redis.create_token_pair(user_id)
        
        # Validar access token
        payload = token_manager_no_redis.validate_access_token(token_pair.access_token)
        
        assert payload is not None
        assert payload['user_id'] == user_id


class TestRefreshTokenManagerIntegration:
    """Testes de integração para RefreshTokenManager"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock do Redis"""
        redis_mock = Mock()
        redis_mock.get.return_value = None
        redis_mock.setex.return_value = None
        redis_mock.delete.return_value = None
        redis_mock.exists.return_value = 0
        redis_mock.keys.return_value = []
        return redis_mock
    
    @pytest.fixture
    def token_manager(self, mock_redis):
        """Instância do RefreshTokenManager para testes"""
        with patch('backend.app.utils.refresh_token_manager.redis') as mock_redis_module:
            mock_redis_module.from_url.return_value = mock_redis
            
            with patch.dict('os.environ', {
                'JWT_REFRESH_SECRET_KEY': 'test-refresh-secret',
                'JWT_SECRET_KEY': 'test-access-secret',
                'JWT_ACCESS_TOKEN_EXPIRES': '3600',
                'JWT_REFRESH_TOKEN_EXPIRES': '604800',
                'MAX_REFRESH_TOKENS_PER_USER': '5',
                'ENABLE_TOKEN_ROTATION': 'true'
            }):
                return RefreshTokenManager()
    
    def test_full_token_lifecycle(self, token_manager, mock_redis):
        """Testa ciclo completo de vida dos tokens"""
        user_id = 123
        
        # 1. Criar par de tokens
        token_pair = token_manager.create_token_pair(user_id)
        assert token_pair.user_id == user_id
        
        # 2. Validar access token
        payload = token_manager.validate_access_token(token_pair.access_token)
        assert payload is not None
        assert payload['user_id'] == user_id
        
        # 3. Renovar access token
        new_token_pair = token_manager.refresh_access_token(token_pair.refresh_token)
        assert new_token_pair is not None
        assert new_token_pair.user_id == user_id
        
        # 4. Verificar que refresh token anterior foi invalidado
        old_payload = token_manager.validate_access_token(token_pair.access_token)
        # O access token anterior ainda pode ser válido até expirar
        
        # 5. Revogar tokens
        result = token_manager.revoke_token(new_token_pair.access_token, user_id)
        assert result is True
        
        # 6. Verificar estatísticas
        stats = token_manager.get_blacklist_stats()
        assert 'total_blacklisted_tokens' in stats


class TestRefreshTokenManagerErrorHandling:
    """Testes de tratamento de erros para RefreshTokenManager"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock do Redis"""
        redis_mock = Mock()
        redis_mock.get.return_value = None
        redis_mock.setex.return_value = None
        redis_mock.delete.return_value = None
        redis_mock.exists.return_value = 0
        redis_mock.keys.return_value = []
        return redis_mock
    
    @pytest.fixture
    def token_manager(self, mock_redis):
        """Instância do RefreshTokenManager para testes"""
        with patch('backend.app.utils.refresh_token_manager.redis') as mock_redis_module:
            mock_redis_module.from_url.return_value = mock_redis
            
            with patch.dict('os.environ', {
                'JWT_REFRESH_SECRET_KEY': 'test-refresh-secret',
                'JWT_SECRET_KEY': 'test-access-secret',
                'JWT_ACCESS_TOKEN_EXPIRES': '3600',
                'JWT_REFRESH_TOKEN_EXPIRES': '604800',
                'MAX_REFRESH_TOKENS_PER_USER': '5',
                'ENABLE_TOKEN_ROTATION': 'true'
            }):
                return RefreshTokenManager()
    
    def test_redis_error_handling(self, token_manager, mock_redis):
        """Testa tratamento de erro do Redis"""
        # Simular erro do Redis
        mock_redis.setex.side_effect = Exception("Redis error")
        
        # Deve continuar funcionando sem quebrar
        token_pair = token_manager.create_token_pair(123)
        assert isinstance(token_pair, TokenPair)
    
    def test_jwt_error_handling(self, token_manager):
        """Testa tratamento de erro de JWT"""
        # Token malformado
        result = token_manager.refresh_access_token("invalid.jwt.token")
        assert result is None


class TestRefreshTokenManagerPerformance:
    """Testes de performance para RefreshTokenManager"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock do Redis"""
        redis_mock = Mock()
        redis_mock.get.return_value = None
        redis_mock.setex.return_value = None
        redis_mock.delete.return_value = None
        redis_mock.exists.return_value = 0
        redis_mock.keys.return_value = []
        return redis_mock
    
    @pytest.fixture
    def token_manager(self, mock_redis):
        """Instância do RefreshTokenManager para testes"""
        with patch('backend.app.utils.refresh_token_manager.redis') as mock_redis_module:
            mock_redis_module.from_url.return_value = mock_redis
            
            with patch.dict('os.environ', {
                'JWT_REFRESH_SECRET_KEY': 'test-refresh-secret',
                'JWT_SECRET_KEY': 'test-access-secret',
                'JWT_ACCESS_TOKEN_EXPIRES': '3600',
                'JWT_REFRESH_TOKEN_EXPIRES': '604800',
                'MAX_REFRESH_TOKENS_PER_USER': '5',
                'ENABLE_TOKEN_ROTATION': 'true'
            }):
                return RefreshTokenManager()
    
    def test_multiple_token_operations_performance(self, token_manager, mock_redis):
        """Testa performance de múltiplas operações de token"""
        import time
        
        start_time = time.time()
        
        # Executar múltiplas operações de token
        for i in range(10):
            # Criar par de tokens
            token_pair = token_manager.create_token_pair(i)
            
            # Validar access token
            payload = token_manager.validate_access_token(token_pair.access_token)
            
            # Renovar access token
            new_token_pair = token_manager.refresh_access_token(token_pair.refresh_token)
            
            assert payload is not None
            assert new_token_pair is not None
        
        end_time = time.time()
        
        # Verificar performance (deve ser rápido)
        assert end_time - start_time < 5.0  # Menos de 5 segundos para 10 operações


class TestRefreshTokenManagerFunctions:
    """Testes para funções de conveniência"""
    
    @pytest.fixture
    def mock_token_manager(self):
        """Mock do RefreshTokenManager"""
        return Mock()
    
    def test_create_token_pair_function(self, mock_token_manager):
        """Testa função create_token_pair"""
        with patch('backend.app.utils.refresh_token_manager.refresh_token_manager', mock_token_manager):
            create_token_pair(123, {"role": "admin"})
            
            mock_token_manager.create_token_pair.assert_called_once_with(123, {"role": "admin"})
    
    def test_refresh_access_token_function(self, mock_token_manager):
        """Testa função refresh_access_token"""
        with patch('backend.app.utils.refresh_token_manager.refresh_token_manager', mock_token_manager):
            refresh_access_token("refresh-token")
            
            mock_token_manager.refresh_access_token.assert_called_once_with("refresh-token")
    
    def test_revoke_token_function(self, mock_token_manager):
        """Testa função revoke_token"""
        with patch('backend.app.utils.refresh_token_manager.refresh_token_manager', mock_token_manager):
            revoke_token("token", 123)
            
            mock_token_manager.revoke_token.assert_called_once_with("token", 123)
    
    def test_revoke_all_user_tokens_function(self, mock_token_manager):
        """Testa função revoke_all_user_tokens"""
        with patch('backend.app.utils.refresh_token_manager.refresh_token_manager', mock_token_manager):
            revoke_all_user_tokens(123)
            
            mock_token_manager.revoke_all_user_tokens.assert_called_once_with(123)
    
    def test_validate_access_token_function(self, mock_token_manager):
        """Testa função validate_access_token"""
        with patch('backend.app.utils.refresh_token_manager.refresh_token_manager', mock_token_manager):
            validate_access_token("access-token")
            
            mock_token_manager.validate_access_token.assert_called_once_with("access-token")


if __name__ == "__main__":
    pytest.main([__file__]) 