#!/usr/bin/env python3
"""
Testes Unitários - Credential Encryption Service
===============================================

Tracing ID: TEST_CREDENTIAL_ENCRYPTION_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Testes para: backend/app/services/credential_encryption.py
Prompt: CHECKLIST_TESTES_UNITARIOS.md - Item 5.1
Ruleset: enterprise_control_layer.yaml
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import base64
from datetime import datetime

from backend.app.services.credential_encryption import CredentialEncryptionService


class TestCredentialEncryptionService:
    @pytest.fixture
    def master_key(self):
        return "test_master_key_32_chars_long_12345"

    @pytest.fixture
    def encryption_service(self, master_key):
        return CredentialEncryptionService(master_key)

    def test_initialization_with_master_key(self, master_key):
        """Testa inicialização com chave mestra fornecida."""
        service = CredentialEncryptionService(master_key)
        assert service.master_key == master_key
        assert service.algorithm.__name__ == "AES"
        assert service.key_size == 256
        assert service.kdf_iterations == 100000
        assert service.salt_size == 32
        assert service.nonce_size == 12
        assert service.encryption_count == 0
        assert service.decryption_count == 0
        assert service.error_count == 0

    def test_initialization_with_env_variable(self):
        """Testa inicialização com variável de ambiente."""
        env_key = "env_master_key_32_chars_long_12345"
        with patch.dict(os.environ, {'CREDENTIAL_MASTER_KEY': env_key}):
            service = CredentialEncryptionService()
            assert service.master_key == env_key

    def test_initialization_without_master_key(self):
        """Testa inicialização sem chave mestra."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="CREDENTIAL_MASTER_KEY deve ser fornecida"):
                CredentialEncryptionService()

    def test_derive_key(self, encryption_service):
        """Testa derivação de chave com PBKDF2."""
        salt = b"test_salt_32_bytes_long_123456789"
        key = encryption_service._derive_key(salt)
        
        assert len(key) == 32  # 256 bits
        assert isinstance(key, bytes)
        assert key != encryption_service.master_key.encode()

    def test_encrypt_credential_success(self, encryption_service):
        """Testa criptografia bem-sucedida de credencial."""
        credential = "test_api_key_12345"
        context = "openai"
        
        encrypted = encryption_service.encrypt_credential(credential, context)
        
        assert isinstance(encrypted, str)
        assert len(encrypted) > 0
        assert encrypted != credential
        assert encryption_service.encryption_count == 1

    def test_encrypt_credential_empty_string(self, encryption_service):
        """Testa criptografia com string vazia."""
        with pytest.raises(ValueError, match="Credencial não pode ser vazia"):
            encryption_service.encrypt_credential("", "test")

    def test_encrypt_credential_whitespace_only(self, encryption_service):
        """Testa criptografia com apenas espaços em branco."""
        with pytest.raises(ValueError, match="Credencial não pode ser vazia"):
            encryption_service.encrypt_credential("   ", "test")

    def test_encrypt_credential_none(self, encryption_service):
        """Testa criptografia com None."""
        with pytest.raises(ValueError, match="Credencial não pode ser vazia"):
            encryption_service.encrypt_credential(None, "test")

    def test_decrypt_credential_success(self, encryption_service):
        """Testa descriptografia bem-sucedida de credencial."""
        original_credential = "test_api_key_12345"
        context = "google"
        
        encrypted = encryption_service.encrypt_credential(original_credential, context)
        decrypted = encryption_service.decrypt_credential(encrypted, context)
        
        assert decrypted == original_credential
        assert encryption_service.decryption_count == 1

    def test_decrypt_credential_empty_string(self, encryption_service):
        """Testa descriptografia com string vazia."""
        with pytest.raises(ValueError, match="Credencial criptografada não pode ser vazia"):
            encryption_service.decrypt_credential("", "test")

    def test_decrypt_credential_invalid_payload(self, encryption_service):
        """Testa descriptografia com payload inválido."""
        with pytest.raises(ValueError, match="Payload criptografado inválido"):
            encryption_service.decrypt_credential("invalid_base64", "test")

    def test_decrypt_credential_corrupted_data(self, encryption_service):
        """Testa descriptografia com dados corrompidos."""
        # Criar dados corrompidos
        corrupted_data = base64.urlsafe_b64encode(b"corrupted_data").decode('ascii')
        
        with pytest.raises(Exception):
            encryption_service.decrypt_credential(corrupted_data, "test")

    def test_encrypt_decrypt_roundtrip(self, encryption_service):
        """Testa ciclo completo de criptografia e descriptografia."""
        test_credentials = [
            "simple_key",
            "complex_api_key_with_special_chars_!@#$%^&*()",
            "very_long_credential_" + "x" * 100,
            "unicode_credential_测试_тест_テスト",
            "credential_with_newlines\nand\t tabs"
        ]
        
        for credential in test_credentials:
            encrypted = encryption_service.encrypt_credential(credential, "roundtrip_test")
            decrypted = encryption_service.decrypt_credential(encrypted, "roundtrip_test")
            assert decrypted == credential

    def test_encrypt_credentials_batch_success(self, encryption_service):
        """Testa criptografia em lote bem-sucedida."""
        credentials = {
            "openai_key": "sk-test-openai-key-12345",
            "google_key": "google-api-key-67890",
            "aws_key": "AKIAWSACCESSKEY123"
        }
        context = "batch_test"
        
        encrypted_batch = encryption_service.encrypt_credentials_batch(credentials, context)
        
        assert len(encrypted_batch) == 3
        assert "openai_key" in encrypted_batch
        assert "google_key" in encrypted_batch
        assert "aws_key" in encrypted_batch
        
        # Verificar que todas foram criptografadas
        for name, encrypted in encrypted_batch.items():
            assert encrypted != credentials[name]
            assert isinstance(encrypted, str)
            assert len(encrypted) > 0

    def test_encrypt_credentials_batch_with_errors(self, encryption_service):
        """Testa criptografia em lote com alguns erros."""
        credentials = {
            "valid_key": "valid_credential",
            "empty_key": "",
            "valid_key2": "another_valid_credential"
        }
        context = "batch_error_test"
        
        encrypted_batch = encryption_service.encrypt_credentials_batch(credentials, context)
        
        # Deve continuar processando mesmo com erros
        assert len(encrypted_batch) == 2
        assert "valid_key" in encrypted_batch
        assert "valid_key2" in encrypted_batch
        assert "empty_key" not in encrypted_batch

    def test_decrypt_credentials_batch_success(self, encryption_service):
        """Testa descriptografia em lote bem-sucedida."""
        original_credentials = {
            "openai_key": "sk-test-openai-key-12345",
            "google_key": "google-api-key-67890"
        }
        context = "batch_decrypt_test"
        
        # Criptografar primeiro
        encrypted_batch = encryption_service.encrypt_credentials_batch(original_credentials, context)
        
        # Descriptografar
        decrypted_batch = encryption_service.decrypt_credentials_batch(encrypted_batch, context)
        
        assert len(decrypted_batch) == 2
        assert decrypted_batch["openai_key"] == original_credentials["openai_key"]
        assert decrypted_batch["google_key"] == original_credentials["google_key"]

    def test_decrypt_credentials_batch_with_errors(self, encryption_service):
        """Testa descriptografia em lote com alguns erros."""
        # Criar um lote com dados válidos e inválidos
        encrypted_credentials = {
            "valid_key": encryption_service.encrypt_credential("valid_credential", "test"),
            "invalid_key": "invalid_encrypted_data",
            "valid_key2": encryption_service.encrypt_credential("another_valid", "test")
        }
        context = "batch_decrypt_error_test"
        
        decrypted_batch = encryption_service.decrypt_credentials_batch(encrypted_credentials, context)
        
        # Deve continuar processando mesmo com erros
        assert len(decrypted_batch) == 2
        assert "valid_key" in decrypted_batch
        assert "valid_key2" in decrypted_batch
        assert "invalid_key" not in decrypted_batch

    def test_get_security_metrics(self, encryption_service):
        """Testa obtenção de métricas de segurança."""
        # Realizar algumas operações
        encryption_service.encrypt_credential("test1", "metrics_test")
        encryption_service.encrypt_credential("test2", "metrics_test")
        encryption_service.decrypt_credential(
            encryption_service.encrypt_credential("test3", "metrics_test"),
            "metrics_test"
        )
        
        metrics = encryption_service.get_security_metrics()
        
        assert metrics["encryption_count"] == 3
        assert metrics["decryption_count"] == 1
        assert metrics["error_count"] == 0
        assert metrics["algorithm"] == "AES-256-GCM"
        assert metrics["key_size"] == 256
        assert metrics["kdf_iterations"] == 100000
        assert metrics["salt_size"] == 32
        assert metrics["nonce_size"] == 12

    def test_is_healthy_success(self, encryption_service):
        """Testa health check bem-sucedido."""
        assert encryption_service.is_healthy() is True

    def test_is_healthy_failure(self, encryption_service):
        """Testa health check com falha."""
        # Simular falha na criptografia
        with patch.object(encryption_service, 'encrypt_credential', side_effect=Exception("Crypto error")):
            assert encryption_service.is_healthy() is False

    def test_different_contexts_produce_different_encryptions(self, encryption_service):
        """Testa que contextos diferentes produzem criptografias diferentes."""
        credential = "same_credential"
        
        encrypted1 = encryption_service.encrypt_credential(credential, "context1")
        encrypted2 = encryption_service.encrypt_credential(credential, "context2")
        
        # Devem ser diferentes devido ao salt/nonce únicos
        assert encrypted1 != encrypted2
        
        # Mas ambas devem descriptografar corretamente
        decrypted1 = encryption_service.decrypt_credential(encrypted1, "context1")
        decrypted2 = encryption_service.decrypt_credential(encrypted2, "context2")
        
        assert decrypted1 == credential
        assert decrypted2 == credential

    def test_same_credential_different_encryptions(self, encryption_service):
        """Testa que a mesma credencial produz criptografias diferentes."""
        credential = "test_credential"
        context = "same_context"
        
        encrypted1 = encryption_service.encrypt_credential(credential, context)
        encrypted2 = encryption_service.encrypt_credential(credential, context)
        
        # Devem ser diferentes devido ao salt/nonce únicos
        assert encrypted1 != encrypted2
        
        # Mas ambas devem descriptografar corretamente
        decrypted1 = encryption_service.decrypt_credential(encrypted1, context)
        decrypted2 = encryption_service.decrypt_credential(encrypted2, context)
        
        assert decrypted1 == credential
        assert decrypted2 == credential

    def test_error_count_increment(self, encryption_service):
        """Testa incremento do contador de erros."""
        initial_error_count = encryption_service.error_count
        
        # Forçar um erro
        with pytest.raises(ValueError):
            encryption_service.encrypt_credential("", "error_test")
        
        assert encryption_service.error_count == initial_error_count + 1

    def test_encryption_count_increment(self, encryption_service):
        """Testa incremento do contador de criptografias."""
        initial_count = encryption_service.encryption_count
        
        encryption_service.encrypt_credential("test", "count_test")
        
        assert encryption_service.encryption_count == initial_count + 1

    def test_decryption_count_increment(self, encryption_service):
        """Testa incremento do contador de descriptografias."""
        initial_count = encryption_service.decryption_count
        
        encrypted = encryption_service.encrypt_credential("test", "count_test")
        encryption_service.decrypt_credential(encrypted, "count_test")
        
        assert encryption_service.decryption_count == initial_count + 1

    def test_large_credential_encryption(self, encryption_service):
        """Testa criptografia de credencial grande."""
        large_credential = "x" * 10000  # 10KB
        
        encrypted = encryption_service.encrypt_credential(large_credential, "large_test")
        decrypted = encryption_service.decrypt_credential(encrypted, "large_test")
        
        assert decrypted == large_credential

    def test_special_characters_in_credential(self, encryption_service):
        """Testa criptografia com caracteres especiais."""
        special_credential = "!@#$%^&*()_+-=[]{}|;':\",./<>?`~"
        
        encrypted = encryption_service.encrypt_credential(special_credential, "special_test")
        decrypted = encryption_service.decrypt_credential(encrypted, "special_test")
        
        assert decrypted == special_credential

    def test_unicode_credential_encryption(self, encryption_service):
        """Testa criptografia com caracteres Unicode."""
        unicode_credential = "测试_тест_テスト_한글_العربية"
        
        encrypted = encryption_service.encrypt_credential(unicode_credential, "unicode_test")
        decrypted = encryption_service.decrypt_credential(encrypted, "unicode_test")
        
        assert decrypted == unicode_credential

    def test_empty_batch_operations(self, encryption_service):
        """Testa operações em lote com dicionário vazio."""
        empty_credentials = {}
        
        encrypted_batch = encryption_service.encrypt_credentials_batch(empty_credentials, "empty_test")
        decrypted_batch = encryption_service.decrypt_credentials_batch(encrypted_batch, "empty_test")
        
        assert encrypted_batch == {}
        assert decrypted_batch == {}

    def test_batch_with_mixed_valid_invalid(self, encryption_service):
        """Testa lote com mistura de credenciais válidas e inválidas."""
        mixed_credentials = {
            "valid1": "valid_credential_1",
            "empty": "",
            "valid2": "valid_credential_2",
            "whitespace": "   ",
            "valid3": "valid_credential_3"
        }
        
        encrypted_batch = encryption_service.encrypt_credentials_batch(mixed_credentials, "mixed_test")
        
        # Deve processar apenas as válidas
        assert len(encrypted_batch) == 3
        assert "valid1" in encrypted_batch
        assert "valid2" in encrypted_batch
        assert "valid3" in encrypted_batch
        assert "empty" not in encrypted_batch
        assert "whitespace" not in encrypted_batch


if __name__ == "__main__":
    pytest.main([__file__]) 