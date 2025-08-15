"""
Testes Unitários para Two Factor Auth
Sistema de Autenticação de Dois Fatores - Omni Keywords Finder

Prompt: Implementação de testes unitários para sistema de autenticação 2FA
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import pyotp
import hashlib
import json
import base64
import secrets
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

from backend.app.utils.two_factor_auth import (
    TwoFactorAuth,
    TwoFactorSetup,
    TwoFactorVerification,
    setup_2fa,
    verify_2fa,
    generate_qr_code,
    get_remaining_backup_codes,
    regenerate_backup_codes,
    disable_2fa
)


class TestTwoFactorSetup:
    """Testes para TwoFactorSetup"""
    
    def test_two_factor_setup_creation(self):
        """Testa criação de TwoFactorSetup"""
        setup = TwoFactorSetup(
            secret_key="JBSWY3DPEHPK3PXP",
            qr_code_url="otpauth://totp/OmniKeywordsFinder:user@example.com?secret=JBSWY3DPEHPK3PXP&issuer=OmniKeywordsFinder",
            backup_codes=["ABC12345", "DEF67890", "GHI11111"],
            setup_complete=False
        )
        
        assert setup.secret_key == "JBSWY3DPEHPK3PXP"
        assert "otpauth://totp/" in setup.qr_code_url
        assert len(setup.backup_codes) == 3
        assert setup.setup_complete is False
    
    def test_two_factor_setup_complete(self):
        """Testa criação de TwoFactorSetup completo"""
        setup = TwoFactorSetup(
            secret_key="JBSWY3DPEHPK3PXP",
            qr_code_url="otpauth://totp/OmniKeywordsFinder:user@example.com?secret=JBSWY3DPEHPK3PXP&issuer=OmniKeywordsFinder",
            backup_codes=["ABC12345", "DEF67890"],
            setup_complete=True
        )
        
        assert setup.setup_complete is True
        assert len(setup.backup_codes) == 2


class TestTwoFactorVerification:
    """Testes para TwoFactorVerification"""
    
    def test_two_factor_verification_success(self):
        """Testa criação de TwoFactorVerification com sucesso"""
        verification = TwoFactorVerification(
            is_valid=True,
            is_backup_code=False,
            remaining_attempts=5,
            message="Código 2FA válido."
        )
        
        assert verification.is_valid is True
        assert verification.is_backup_code is False
        assert verification.remaining_attempts == 5
        assert verification.message == "Código 2FA válido."
    
    def test_two_factor_verification_backup_code(self):
        """Testa criação de TwoFactorVerification com backup code"""
        verification = TwoFactorVerification(
            is_valid=True,
            is_backup_code=True,
            remaining_attempts=5,
            message="Backup code usado com sucesso."
        )
        
        assert verification.is_valid is True
        assert verification.is_backup_code is True
        assert verification.remaining_attempts == 5
    
    def test_two_factor_verification_failure(self):
        """Testa criação de TwoFactorVerification com falha"""
        verification = TwoFactorVerification(
            is_valid=False,
            is_backup_code=False,
            remaining_attempts=2,
            message="Código 2FA inválido. Tentativas restantes: 2"
        )
        
        assert verification.is_valid is False
        assert verification.is_backup_code is False
        assert verification.remaining_attempts == 2
    
    def test_two_factor_verification_locked(self):
        """Testa criação de TwoFactorVerification com usuário bloqueado"""
        verification = TwoFactorVerification(
            is_valid=False,
            is_backup_code=False,
            remaining_attempts=0,
            message="Muitas tentativas incorretas. Conta bloqueada por 15 minutos."
        )
        
        assert verification.is_valid is False
        assert verification.remaining_attempts == 0
        assert "bloqueada" in verification.message


class TestTwoFactorAuth:
    """Testes para TwoFactorAuth"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock do Redis"""
        redis_mock = Mock()
        redis_mock.get.return_value = None
        redis_mock.setex.return_value = None
        redis_mock.delete.return_value = None
        redis_mock.exists.return_value = 0
        redis_mock.ttl.return_value = 0
        return redis_mock
    
    @pytest.fixture
    def two_factor_auth(self, mock_redis):
        """Instância do TwoFactorAuth para testes"""
        with patch('backend.app.utils.two_factor_auth.redis') as mock_redis_module:
            mock_redis_module.from_url.return_value = mock_redis
            
            with patch.dict('os.environ', {
                '2FA_ISSUER_NAME': 'Test App',
                '2FA_BACKUP_CODES_COUNT': '5',
                '2FA_BACKUP_CODE_LENGTH': '8',
                '2FA_MAX_ATTEMPTS': '3',
                '2FA_LOCKOUT_DURATION': '900'
            }):
                return TwoFactorAuth()
    
    def test_two_factor_auth_initialization(self, two_factor_auth):
        """Testa inicialização do TwoFactorAuth"""
        assert two_factor_auth.issuer_name == "Test App"
        assert two_factor_auth.backup_codes_count == 5
        assert two_factor_auth.backup_code_length == 8
        assert two_factor_auth.max_attempts == 3
        assert two_factor_auth.lockout_duration == 900
        assert two_factor_auth.redis_client is not None
    
    def test_two_factor_auth_initialization_no_redis(self):
        """Testa inicialização do TwoFactorAuth sem Redis"""
        with patch('backend.app.utils.two_factor_auth.redis') as mock_redis_module:
            mock_redis_module.from_url.side_effect = Exception("Redis connection failed")
            
            with patch.dict('os.environ', {
                '2FA_ISSUER_NAME': 'Test App',
                '2FA_BACKUP_CODES_COUNT': '5',
                '2FA_BACKUP_CODE_LENGTH': '8',
                '2FA_MAX_ATTEMPTS': '3',
                '2FA_LOCKOUT_DURATION': '900'
            }):
                auth = TwoFactorAuth()
                assert auth.redis_client is None
    
    def test_generate_secret_key(self, two_factor_auth):
        """Testa geração de chave secreta"""
        user_id = 123
        email = "user@example.com"
        
        secret_key = two_factor_auth.generate_secret_key(user_id, email)
        
        assert isinstance(secret_key, str)
        assert len(secret_key) > 0
        # Verificar se é base32 válido
        assert all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567' for c in secret_key)
    
    def test_generate_secret_key_different_users(self, two_factor_auth):
        """Testa geração de chaves secretas diferentes para usuários diferentes"""
        secret_key1 = two_factor_auth.generate_secret_key(1, "user1@example.com")
        secret_key2 = two_factor_auth.generate_secret_key(2, "user2@example.com")
        
        assert secret_key1 != secret_key2
    
    def test_setup_2fa(self, two_factor_auth):
        """Testa configuração de 2FA"""
        user_id = 123
        email = "user@example.com"
        username = "testuser"
        
        setup = two_factor_auth.setup_2fa(user_id, email, username)
        
        assert isinstance(setup, TwoFactorSetup)
        assert setup.secret_key is not None
        assert len(setup.secret_key) > 0
        assert "otpauth://totp/" in setup.qr_code_url
        assert email in setup.qr_code_url
        assert len(setup.backup_codes) == 5
        assert all(len(code) == 8 for code in setup.backup_codes)
        assert setup.setup_complete is False
    
    def test_verify_totp_valid_code(self, two_factor_auth, mock_redis):
        """Testa verificação de código TOTP válido"""
        # Gerar chave secreta e código TOTP válido
        secret_key = two_factor_auth.generate_secret_key(123, "user@example.com")
        totp = pyotp.TOTP(secret_key)
        valid_code = totp.now()
        
        # Mock de usuário não bloqueado
        mock_redis.exists.return_value = 0
        
        verification = two_factor_auth.verify_totp(secret_key, valid_code, 123)
        
        assert verification.is_valid is True
        assert verification.is_backup_code is False
        assert verification.remaining_attempts == 3
        assert "válido" in verification.message
    
    def test_verify_totp_invalid_code(self, two_factor_auth, mock_redis):
        """Testa verificação de código TOTP inválido"""
        secret_key = two_factor_auth.generate_secret_key(123, "user@example.com")
        invalid_code = "123456"
        
        # Mock de usuário não bloqueado
        mock_redis.exists.return_value = 0
        mock_redis.get.return_value = "1"  # 1 tentativa anterior
        
        verification = two_factor_auth.verify_totp(secret_key, invalid_code, 123)
        
        assert verification.is_valid is False
        assert verification.is_backup_code is False
        assert verification.remaining_attempts == 1
        assert "inválido" in verification.message
    
    def test_verify_totp_user_locked(self, two_factor_auth, mock_redis):
        """Testa verificação com usuário bloqueado"""
        secret_key = two_factor_auth.generate_secret_key(123, "user@example.com")
        code = "123456"
        
        # Mock de usuário bloqueado
        mock_redis.exists.return_value = 1
        mock_redis.ttl.return_value = 600  # 10 minutos restantes
        
        verification = two_factor_auth.verify_totp(secret_key, code, 123)
        
        assert verification.is_valid is False
        assert verification.remaining_attempts == 0
        assert "bloqueada" in verification.message
        assert "10" in verification.message
    
    def test_verify_totp_max_attempts_exceeded(self, two_factor_auth, mock_redis):
        """Testa verificação com máximo de tentativas excedido"""
        secret_key = two_factor_auth.generate_secret_key(123, "user@example.com")
        invalid_code = "123456"
        
        # Mock de usuário não bloqueado mas com tentativas esgotadas
        mock_redis.exists.return_value = 0
        mock_redis.get.return_value = "3"  # 3 tentativas (máximo)
        
        verification = two_factor_auth.verify_totp(secret_key, invalid_code, 123)
        
        assert verification.is_valid is False
        assert verification.remaining_attempts == 0
        assert "bloqueada" in verification.message
    
    def test_verify_totp_backup_code(self, two_factor_auth, mock_redis):
        """Testa verificação de backup code"""
        secret_key = two_factor_auth.generate_secret_key(123, "user@example.com")
        backup_code = "ABC12345"
        
        # Mock de backup code válido
        mock_redis.exists.return_value = 0
        mock_redis.get.return_value = json.dumps([
            hashlib.sha256(backup_code.encode()).hexdigest()
        ])
        
        verification = two_factor_auth.verify_totp(secret_key, backup_code, 123)
        
        assert verification.is_valid is True
        assert verification.is_backup_code is True
        assert verification.remaining_attempts == 3
        assert "Backup code" in verification.message
    
    def test_generate_qr_code(self, two_factor_auth):
        """Testa geração de QR code"""
        qr_code_url = "otpauth://totp/TestApp:user@example.com?secret=JBSWY3DPEHPK3PXP&issuer=TestApp"
        
        qr_code_base64 = two_factor_auth.generate_qr_code(qr_code_url)
        
        assert isinstance(qr_code_base64, str)
        assert qr_code_base64.startswith("data:image/png;base64,")
        assert len(qr_code_base64) > 100  # Deve ter conteúdo base64
    
    def test_generate_qr_code_error(self, two_factor_auth):
        """Testa geração de QR code com erro"""
        invalid_url = ""  # URL inválida
        
        qr_code_base64 = two_factor_auth.generate_qr_code(invalid_url)
        
        assert qr_code_base64 == ""
    
    def test_generate_qr_code_url(self, two_factor_auth):
        """Testa geração de URL para QR code"""
        secret_key = "JBSWY3DPEHPK3PXP"
        email = "user@example.com"
        username = "testuser"
        
        qr_code_url = two_factor_auth._generate_qr_code_url(secret_key, email, username)
        
        assert "otpauth://totp/" in qr_code_url
        assert email in qr_code_url
        assert "Test App" in qr_code_url  # issuer_name
        assert secret_key in qr_code_url
    
    def test_generate_backup_codes(self, two_factor_auth):
        """Testa geração de códigos de backup"""
        backup_codes = two_factor_auth._generate_backup_codes()
        
        assert len(backup_codes) == 5
        assert all(len(code) == 8 for code in backup_codes)
        assert all(code.isalnum() for code in backup_codes)
        # Verificar se são únicos
        assert len(set(backup_codes)) == 5
    
    def test_store_backup_codes(self, two_factor_auth, mock_redis):
        """Testa armazenamento de códigos de backup"""
        user_id = 123
        backup_codes = ["ABC12345", "DEF67890", "GHI11111"]
        
        two_factor_auth._store_backup_codes(user_id, backup_codes)
        
        # Verificar se foi chamado com a chave correta
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert "2fa_backup_codes:123" in call_args[0]
        assert call_args[0][1] == 86400 * 30  # 30 dias
        
        # Verificar se os códigos foram hasheados
        stored_data = json.loads(call_args[0][2])
        assert len(stored_data) == 3
        assert all(len(hash_code) == 64 for hash_code in stored_data)  # SHA256 hash length
    
    def test_is_backup_code_valid(self, two_factor_auth, mock_redis):
        """Testa verificação de backup code válido"""
        user_id = 123
        backup_code = "ABC12345"
        code_hash = hashlib.sha256(backup_code.encode()).hexdigest()
        
        # Mock de backup codes armazenados
        mock_redis.get.return_value = json.dumps([code_hash])
        
        result = two_factor_auth._is_backup_code(backup_code, user_id)
        
        assert result is True
        mock_redis.get.assert_called_with("2fa_backup_codes:123")
    
    def test_is_backup_code_invalid(self, two_factor_auth, mock_redis):
        """Testa verificação de backup code inválido"""
        user_id = 123
        backup_code = "ABC12345"
        
        # Mock de backup codes armazenados (diferente)
        mock_redis.get.return_value = json.dumps([
            hashlib.sha256("DIFFERENT".encode()).hexdigest()
        ])
        
        result = two_factor_auth._is_backup_code(backup_code, user_id)
        
        assert result is False
    
    def test_is_backup_code_no_stored_codes(self, two_factor_auth, mock_redis):
        """Testa verificação de backup code sem códigos armazenados"""
        user_id = 123
        backup_code = "ABC12345"
        
        # Mock de nenhum backup code armazenado
        mock_redis.get.return_value = None
        
        result = two_factor_auth._is_backup_code(backup_code, user_id)
        
        assert result is False
    
    def test_use_backup_code(self, two_factor_auth, mock_redis):
        """Testa uso de backup code"""
        user_id = 123
        backup_code = "ABC12345"
        code_hash = hashlib.sha256(backup_code.encode()).hexdigest()
        
        # Mock de backup codes armazenados
        mock_redis.get.return_value = json.dumps([code_hash, "OTHER_HASH"])
        
        two_factor_auth._use_backup_code(backup_code, user_id)
        
        # Verificar se foi atualizado sem o código usado
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        stored_data = json.loads(call_args[0][2])
        assert len(stored_data) == 1
        assert code_hash not in stored_data
        assert "OTHER_HASH" in stored_data
    
    def test_is_user_locked(self, two_factor_auth, mock_redis):
        """Testa verificação de usuário bloqueado"""
        user_id = 123
        
        # Mock de usuário bloqueado
        mock_redis.exists.return_value = 1
        
        result = two_factor_auth._is_user_locked(user_id)
        
        assert result is True
        mock_redis.exists.assert_called_with("2fa_lockout:123")
    
    def test_is_user_not_locked(self, two_factor_auth, mock_redis):
        """Testa verificação de usuário não bloqueado"""
        user_id = 123
        
        # Mock de usuário não bloqueado
        mock_redis.exists.return_value = 0
        
        result = two_factor_auth._is_user_locked(user_id)
        
        assert result is False
    
    def test_lock_user(self, two_factor_auth, mock_redis):
        """Testa bloqueio de usuário"""
        user_id = 123
        
        with patch('backend.app.utils.two_factor_auth.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2025, 1, 27, 12, 0, 0)
            
            two_factor_auth._lock_user(user_id)
        
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert "2fa_lockout:123" in call_args[0]
        assert call_args[0][1] == 900  # lockout_duration
    
    def test_get_lockout_remaining_time(self, two_factor_auth, mock_redis):
        """Testa obtenção de tempo restante de bloqueio"""
        user_id = 123
        
        # Mock de 10 minutos restantes
        mock_redis.ttl.return_value = 600
        
        remaining_time = two_factor_auth._get_lockout_remaining_time(user_id)
        
        assert remaining_time == 10
        mock_redis.ttl.assert_called_with("2fa_lockout:123")
    
    def test_increment_attempts(self, two_factor_auth, mock_redis):
        """Testa incremento de tentativas"""
        user_id = 123
        
        # Mock de 1 tentativa anterior
        mock_redis.get.return_value = "1"
        
        remaining_attempts = two_factor_auth._increment_attempts(user_id)
        
        assert remaining_attempts == 1  # 3 - 2 = 1
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert "2fa_attempts:123" in call_args[0]
        assert call_args[0][1] == 3600  # 1 hora
        assert call_args[0][2] == "2"  # 1 + 1 = 2
    
    def test_increment_attempts_first_attempt(self, two_factor_auth, mock_redis):
        """Testa incremento de tentativas na primeira tentativa"""
        user_id = 123
        
        # Mock de nenhuma tentativa anterior
        mock_redis.get.return_value = None
        
        remaining_attempts = two_factor_auth._increment_attempts(user_id)
        
        assert remaining_attempts == 2  # 3 - 1 = 2
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][2] == "1"  # Primeira tentativa
    
    def test_reset_attempts(self, two_factor_auth, mock_redis):
        """Testa reset de tentativas"""
        user_id = 123
        
        two_factor_auth._reset_attempts(user_id)
        
        mock_redis.delete.assert_called_with("2fa_attempts:123")
    
    def test_get_remaining_backup_codes(self, two_factor_auth, mock_redis):
        """Testa obtenção de backup codes restantes"""
        user_id = 123
        
        # Mock de 3 backup codes armazenados
        mock_redis.get.return_value = json.dumps(["hash1", "hash2", "hash3"])
        
        remaining_count = two_factor_auth.get_remaining_backup_codes(user_id)
        
        assert remaining_count == 3
        mock_redis.get.assert_called_with("2fa_backup_codes:123")
    
    def test_get_remaining_backup_codes_none(self, two_factor_auth, mock_redis):
        """Testa obtenção de backup codes restantes quando não há nenhum"""
        user_id = 123
        
        # Mock de nenhum backup code armazenado
        mock_redis.get.return_value = None
        
        remaining_count = two_factor_auth.get_remaining_backup_codes(user_id)
        
        assert remaining_count == 0
    
    def test_regenerate_backup_codes(self, two_factor_auth, mock_redis):
        """Testa regeneração de backup codes"""
        user_id = 123
        
        new_codes = two_factor_auth.regenerate_backup_codes(user_id)
        
        assert len(new_codes) == 5
        assert all(len(code) == 8 for code in new_codes)
        # Verificar se foram armazenados
        mock_redis.setex.assert_called_once()
    
    def test_disable_2fa(self, two_factor_auth, mock_redis):
        """Testa desabilitação de 2FA"""
        user_id = 123
        
        two_factor_auth.disable_2fa(user_id)
        
        # Verificar se todas as chaves foram removidas
        assert mock_redis.delete.call_count == 3
        delete_calls = [call[0][0] for call in mock_redis.delete.call_args_list]
        assert "2fa_backup_codes:123" in delete_calls
        assert "2fa_attempts:123" in delete_calls
        assert "2fa_lockout:123" in delete_calls


class TestTwoFactorAuthNoRedis:
    """Testes para TwoFactorAuth sem Redis"""
    
    @pytest.fixture
    def two_factor_auth_no_redis(self):
        """Instância do TwoFactorAuth sem Redis"""
        with patch('backend.app.utils.two_factor_auth.redis') as mock_redis_module:
            mock_redis_module.from_url.side_effect = Exception("Redis connection failed")
            
            with patch.dict('os.environ', {
                '2FA_ISSUER_NAME': 'Test App',
                '2FA_BACKUP_CODES_COUNT': '5',
                '2FA_BACKUP_CODE_LENGTH': '8',
                '2FA_MAX_ATTEMPTS': '3',
                '2FA_LOCKOUT_DURATION': '900'
            }):
                return TwoFactorAuth()
    
    def test_verify_totp_no_redis(self, two_factor_auth_no_redis):
        """Testa verificação TOTP sem Redis"""
        secret_key = two_factor_auth_no_redis.generate_secret_key(123, "user@example.com")
        totp = pyotp.TOTP(secret_key)
        valid_code = totp.now()
        
        verification = two_factor_auth_no_redis.verify_totp(secret_key, valid_code, 123)
        
        assert verification.is_valid is True
        assert verification.remaining_attempts == 3
    
    def test_backup_code_no_redis(self, two_factor_auth_no_redis):
        """Testa backup code sem Redis"""
        secret_key = two_factor_auth_no_redis.generate_secret_key(123, "user@example.com")
        backup_code = "ABC12345"
        
        verification = two_factor_auth_no_redis.verify_totp(secret_key, backup_code, 123)
        
        # Sem Redis, backup codes não funcionam
        assert verification.is_valid is False
    
    def test_get_remaining_backup_codes_no_redis(self, two_factor_auth_no_redis):
        """Testa obtenção de backup codes restantes sem Redis"""
        remaining_count = two_factor_auth_no_redis.get_remaining_backup_codes(123)
        
        assert remaining_count == 0


class TestTwoFactorAuthIntegration:
    """Testes de integração para TwoFactorAuth"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock do Redis"""
        redis_mock = Mock()
        redis_mock.get.return_value = None
        redis_mock.setex.return_value = None
        redis_mock.delete.return_value = None
        redis_mock.exists.return_value = 0
        redis_mock.ttl.return_value = 0
        return redis_mock
    
    @pytest.fixture
    def two_factor_auth(self, mock_redis):
        """Instância do TwoFactorAuth para testes"""
        with patch('backend.app.utils.two_factor_auth.redis') as mock_redis_module:
            mock_redis_module.from_url.return_value = mock_redis
            
            with patch.dict('os.environ', {
                '2FA_ISSUER_NAME': 'Test App',
                '2FA_BACKUP_CODES_COUNT': '5',
                '2FA_BACKUP_CODE_LENGTH': '8',
                '2FA_MAX_ATTEMPTS': '3',
                '2FA_LOCKOUT_DURATION': '900'
            }):
                return TwoFactorAuth()
    
    def test_full_2fa_workflow(self, two_factor_auth, mock_redis):
        """Testa workflow completo de 2FA"""
        user_id = 123
        email = "user@example.com"
        username = "testuser"
        
        # 1. Configurar 2FA
        setup = two_factor_auth.setup_2fa(user_id, email, username)
        assert setup.secret_key is not None
        assert len(setup.backup_codes) == 5
        
        # 2. Verificar código TOTP válido
        totp = pyotp.TOTP(setup.secret_key)
        valid_code = totp.now()
        
        verification = two_factor_auth.verify_totp(setup.secret_key, valid_code, user_id)
        assert verification.is_valid is True
        
        # 3. Verificar backup code
        backup_code = setup.backup_codes[0]
        mock_redis.get.return_value = json.dumps([
            hashlib.sha256(backup_code.encode()).hexdigest()
        ])
        
        verification = two_factor_auth.verify_totp(setup.secret_key, backup_code, user_id)
        assert verification.is_valid is True
        assert verification.is_backup_code is True
        
        # 4. Verificar backup codes restantes
        remaining_count = two_factor_auth.get_remaining_backup_codes(user_id)
        assert remaining_count == 4  # Um foi usado
        
        # 5. Regenerar backup codes
        new_codes = two_factor_auth.regenerate_backup_codes(user_id)
        assert len(new_codes) == 5
        
        # 6. Desabilitar 2FA
        two_factor_auth.disable_2fa(user_id)
        assert mock_redis.delete.call_count == 3


class TestTwoFactorAuthErrorHandling:
    """Testes de tratamento de erros para TwoFactorAuth"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock do Redis"""
        redis_mock = Mock()
        redis_mock.get.return_value = None
        redis_mock.setex.return_value = None
        redis_mock.delete.return_value = None
        redis_mock.exists.return_value = 0
        redis_mock.ttl.return_value = 0
        return redis_mock
    
    @pytest.fixture
    def two_factor_auth(self, mock_redis):
        """Instância do TwoFactorAuth para testes"""
        with patch('backend.app.utils.two_factor_auth.redis') as mock_redis_module:
            mock_redis_module.from_url.return_value = mock_redis
            
            with patch.dict('os.environ', {
                '2FA_ISSUER_NAME': 'Test App',
                '2FA_BACKUP_CODES_COUNT': '5',
                '2FA_BACKUP_CODE_LENGTH': '8',
                '2FA_MAX_ATTEMPTS': '3',
                '2FA_LOCKOUT_DURATION': '900'
            }):
                return TwoFactorAuth()
    
    def test_redis_error_handling(self, two_factor_auth, mock_redis):
        """Testa tratamento de erro do Redis"""
        # Simular erro do Redis
        mock_redis.get.side_effect = Exception("Redis error")
        
        # Deve continuar funcionando sem quebrar
        remaining_count = two_factor_auth.get_remaining_backup_codes(123)
        assert remaining_count == 0
    
    def test_json_error_handling(self, two_factor_auth, mock_redis):
        """Testa tratamento de erro de JSON"""
        # Simular JSON inválido
        mock_redis.get.return_value = "invalid json"
        
        # Deve continuar funcionando sem quebrar
        remaining_count = two_factor_auth.get_remaining_backup_codes(123)
        assert remaining_count == 0


class TestTwoFactorAuthPerformance:
    """Testes de performance para TwoFactorAuth"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock do Redis"""
        redis_mock = Mock()
        redis_mock.get.return_value = None
        redis_mock.setex.return_value = None
        redis_mock.delete.return_value = None
        redis_mock.exists.return_value = 0
        redis_mock.ttl.return_value = 0
        return redis_mock
    
    @pytest.fixture
    def two_factor_auth(self, mock_redis):
        """Instância do TwoFactorAuth para testes"""
        with patch('backend.app.utils.two_factor_auth.redis') as mock_redis_module:
            mock_redis_module.from_url.return_value = mock_redis
            
            with patch.dict('os.environ', {
                '2FA_ISSUER_NAME': 'Test App',
                '2FA_BACKUP_CODES_COUNT': '5',
                '2FA_BACKUP_CODE_LENGTH': '8',
                '2FA_MAX_ATTEMPTS': '3',
                '2FA_LOCKOUT_DURATION': '900'
            }):
                return TwoFactorAuth()
    
    def test_multiple_2fa_operations_performance(self, two_factor_auth, mock_redis):
        """Testa performance de múltiplas operações 2FA"""
        import time
        
        start_time = time.time()
        
        # Executar múltiplas operações 2FA
        for i in range(10):
            # Setup 2FA
            setup = two_factor_auth.setup_2fa(i, f"user{i}@example.com", f"user{i}")
            
            # Verificar código
            totp = pyotp.TOTP(setup.secret_key)
            code = totp.now()
            verification = two_factor_auth.verify_totp(setup.secret_key, code, i)
            
            # Gerar QR code
            qr_code = two_factor_auth.generate_qr_code(setup.qr_code_url)
            
            assert verification.is_valid is True
            assert len(qr_code) > 0
        
        end_time = time.time()
        
        # Verificar performance (deve ser rápido)
        assert end_time - start_time < 5.0  # Menos de 5 segundos para 10 operações


class TestTwoFactorAuthFunctions:
    """Testes para funções de conveniência"""
    
    @pytest.fixture
    def mock_two_factor_auth(self):
        """Mock do TwoFactorAuth"""
        return Mock()
    
    def test_setup_2fa_function(self, mock_two_factor_auth):
        """Testa função setup_2fa"""
        with patch('backend.app.utils.two_factor_auth.two_factor_auth', mock_two_factor_auth):
            setup_2fa(123, "user@example.com", "testuser")
            
            mock_two_factor_auth.setup_2fa.assert_called_once_with(123, "user@example.com", "testuser")
    
    def test_verify_2fa_function(self, mock_two_factor_auth):
        """Testa função verify_2fa"""
        with patch('backend.app.utils.two_factor_auth.two_factor_auth', mock_two_factor_auth):
            verify_2fa("secret", "123456", 123)
            
            mock_two_factor_auth.verify_totp.assert_called_once_with("secret", "123456", 123)
    
    def test_generate_qr_code_function(self, mock_two_factor_auth):
        """Testa função generate_qr_code"""
        with patch('backend.app.utils.two_factor_auth.two_factor_auth', mock_two_factor_auth):
            generate_qr_code("otpauth://...")
            
            mock_two_factor_auth.generate_qr_code.assert_called_once_with("otpauth://...")
    
    def test_get_remaining_backup_codes_function(self, mock_two_factor_auth):
        """Testa função get_remaining_backup_codes"""
        with patch('backend.app.utils.two_factor_auth.two_factor_auth', mock_two_factor_auth):
            get_remaining_backup_codes(123)
            
            mock_two_factor_auth.get_remaining_backup_codes.assert_called_once_with(123)
    
    def test_regenerate_backup_codes_function(self, mock_two_factor_auth):
        """Testa função regenerate_backup_codes"""
        with patch('backend.app.utils.two_factor_auth.two_factor_auth', mock_two_factor_auth):
            regenerate_backup_codes(123)
            
            mock_two_factor_auth.regenerate_backup_codes.assert_called_once_with(123)
    
    def test_disable_2fa_function(self, mock_two_factor_auth):
        """Testa função disable_2fa"""
        with patch('backend.app.utils.two_factor_auth.two_factor_auth', mock_two_factor_auth):
            disable_2fa(123)
            
            mock_two_factor_auth.disable_2fa.assert_called_once_with(123)


if __name__ == "__main__":
    pytest.main([__file__]) 