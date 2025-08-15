"""
Testes Unitários: CredentialValidator
Testa funcionalidades do validador de credenciais

Prompt: CredentialValidator como Validador
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-27
Versão: 1.0.0
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import List

from backend.app.api.credential_validation import (
    _validate_credential_internal,
    validate_credential,
    CredentialValidationRequest,
    CredentialValidationResponse
)
from backend.app.services.credential_encryption import CredentialEncryptionService
from backend.app.services.credential_rate_limiter import CredentialRateLimiter

class TestCredentialValidator:
    """Testes para CredentialValidator."""
    
    @pytest.fixture
    def encryption_service(self):
        """Serviço de criptografia para testes."""
        return CredentialEncryptionService()
    
    @pytest.fixture
    def rate_limiter(self):
        """Rate limiter para testes."""
        return CredentialRateLimiter()
    
    @pytest.fixture
    def valid_openai_key(self):
        """Chave OpenAI válida para testes."""
        return "sk-proj-1234567890abcdefghijklmnopqrstuvwxyz"
    
    @pytest.fixture
    def valid_deepseek_key(self):
        """Chave DeepSeek válida para testes."""
        return "sk-1234567890abcdefghijklmnopqrstuvwxyz"
    
    @pytest.fixture
    def valid_claude_key(self):
        """Chave Claude válida para testes."""
        return "sk-ant-api03-1234567890abcdefghijklmnopqrstuvwxyz"
    
    @pytest.fixture
    def valid_gemini_key(self):
        """Chave Gemini válida para testes."""
        return "AIzaSyB1234567890abcdefghijklmnopqrstuvwxyz"
    
    @pytest.fixture
    def valid_google_key(self):
        """Chave Google válida para testes."""
        return "AIzaSyB1234567890abcdefghijklmnopqrstuvwxyz"
    
    @pytest.mark.asyncio
    async def test_validate_openai_key_valid(self, valid_openai_key):
        """Testa validação de chave OpenAI válida."""
        result = await _validate_credential_internal(
            "openai",
            "api_key",
            valid_openai_key
        )
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_openai_key_invalid_format(self):
        """Testa validação de chave OpenAI com formato inválido."""
        invalid_key = "invalid-key-format"
        result = await _validate_credential_internal(
            "openai",
            "api_key",
            invalid_key
        )
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_openai_key_too_short(self):
        """Testa validação de chave OpenAI muito curta."""
        short_key = "sk-123"
        result = await _validate_credential_internal(
            "openai",
            "api_key",
            short_key
        )
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_deepseek_key_valid(self, valid_deepseek_key):
        """Testa validação de chave DeepSeek válida."""
        result = await _validate_credential_internal(
            "deepseek",
            "api_key",
            valid_deepseek_key
        )
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_deepseek_key_invalid_format(self):
        """Testa validação de chave DeepSeek com formato inválido."""
        invalid_key = "invalid-key-format"
        result = await _validate_credential_internal(
            "deepseek",
            "api_key",
            invalid_key
        )
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_claude_key_valid(self, valid_claude_key):
        """Testa validação de chave Claude válida."""
        result = await _validate_credential_internal(
            "claude",
            "api_key",
            valid_claude_key
        )
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_claude_key_invalid_format(self):
        """Testa validação de chave Claude com formato inválido."""
        invalid_key = "sk-1234567890abcdefghijklmnopqrstuvwxyz"
        result = await _validate_credential_internal(
            "claude",
            "api_key",
            invalid_key
        )
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_gemini_key_valid(self, valid_gemini_key):
        """Testa validação de chave Gemini válida."""
        result = await _validate_credential_internal(
            "gemini",
            "api_key",
            valid_gemini_key
        )
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_gemini_key_too_short(self):
        """Testa validação de chave Gemini muito curta."""
        short_key = "AIzaSyB123"
        result = await _validate_credential_internal(
            "gemini",
            "api_key",
            short_key
        )
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_google_key_valid(self, valid_google_key):
        """Testa validação de chave Google válida."""
        result = await _validate_credential_internal(
            "google",
            "api_key",
            valid_google_key
        )
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_google_key_too_short(self):
        """Testa validação de chave Google muito curta."""
        short_key = "AIzaSyB123"
        result = await _validate_credential_internal(
            "google",
            "api_key",
            short_key
        )
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_empty_credential(self):
        """Testa validação de credencial vazia."""
        result = await _validate_credential_internal(
            "openai",
            "api_key",
            ""
        )
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_none_credential(self):
        """Testa validação de credencial None."""
        result = await _validate_credential_internal(
            "openai",
            "api_key",
            None
        )
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_whitespace_credential(self):
        """Testa validação de credencial com apenas espaços."""
        result = await _validate_credential_internal(
            "openai",
            "api_key",
            "   "
        )
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_unknown_provider(self):
        """Testa validação de provider desconhecido."""
        result = await _validate_credential_internal(
            "unknown_provider",
            "api_key",
            "some-key"
        )
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_with_context(self):
        """Testa validação com contexto adicional."""
        result = await _validate_credential_internal(
            "openai",
            "api_key",
            "sk-proj-1234567890abcdefghijklmnopqrstuvwxyz",
            context="test_context"
        )
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_case_insensitive_provider(self, valid_openai_key):
        """Testa validação com provider em maiúsculas."""
        result = await _validate_credential_internal(
            "OPENAI",
            "api_key",
            valid_openai_key
        )
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_case_insensitive_deepseek(self, valid_deepseek_key):
        """Testa validação DeepSeek com provider em maiúsculas."""
        result = await _validate_credential_internal(
            "DEEPSEEK",
            "api_key",
            valid_deepseek_key
        )
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_case_insensitive_claude(self, valid_claude_key):
        """Testa validação Claude com provider em maiúsculas."""
        result = await _validate_credential_internal(
            "CLAUDE",
            "api_key",
            valid_claude_key
        )
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_case_insensitive_gemini(self, valid_gemini_key):
        """Testa validação Gemini com provider em maiúsculas."""
        result = await _validate_credential_internal(
            "GEMINI",
            "api_key",
            valid_gemini_key
        )
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_case_insensitive_google(self, valid_google_key):
        """Testa validação Google com provider em maiúsculas."""
        result = await _validate_credential_internal(
            "GOOGLE",
            "api_key",
            valid_google_key
        )
        assert result is True


class TestCredentialValidationEndpoint:
    """Testes para endpoint de validação de credenciais."""
    
    @pytest.fixture
    def mock_request(self):
        """Mock de request para testes."""
        request = Mock()
        request.client.host = "127.0.0.1"
        return request
    
    @pytest.fixture
    def mock_user(self):
        """Mock de usuário para testes."""
        return {"id": "test_user_123", "email": "test@example.com"}
    
    @pytest.fixture
    def valid_validation_request(self):
        """Request de validação válido."""
        return CredentialValidationRequest(
            provider="openai",
            credential_type="api_key",
            credential_value="sk-proj-1234567890abcdefghijklmnopqrstuvwxyz",
            context="test_context"
        )
    
    @pytest.mark.asyncio
    async def test_validate_credential_success(self, mock_request, mock_user, valid_validation_request):
        """Testa validação de credencial com sucesso."""
        with patch('backend.app.api.credential_validation._validate_credential_internal', return_value=True), \
             patch('backend.app.api.credential_validation.encryption_service') as mock_encryption, \
             patch('backend.app.api.credential_validation.rate_limiter') as mock_rate_limiter:
            
            mock_encryption.encrypt_credential.return_value = "encrypted_key"
            mock_rate_limiter.check_rate_limit.return_value = Mock(remaining=4, reset_time=time.time() + 60)
            
            response = await validate_credential(
                valid_validation_request,
                mock_request,
                mock_user["id"]
            )
            
            assert isinstance(response, CredentialValidationResponse)
            assert response.valid is True
            assert response.provider == "openai"
            assert response.credential_type == "api_key"
            assert response.message == "Credencial válida"
            assert response.details["encrypted"] is True
    
    @pytest.mark.asyncio
    async def test_validate_credential_failure(self, mock_request, mock_user, valid_validation_request):
        """Testa validação de credencial com falha."""
        with patch('backend.app.api.credential_validation._validate_credential_internal', return_value=False), \
             patch('backend.app.api.credential_validation.rate_limiter') as mock_rate_limiter:
            
            mock_rate_limiter.check_rate_limit.return_value = Mock(remaining=4, reset_time=time.time() + 60)
            
            response = await validate_credential(
                valid_validation_request,
                mock_request,
                mock_user["id"]
            )
            
            assert isinstance(response, CredentialValidationResponse)
            assert response.valid is False
            assert response.message == "Credencial inválida"
            assert response.details["encrypted"] is False
    
    @pytest.mark.asyncio
    async def test_validate_credential_rate_limit_exceeded(self, mock_request, mock_user, valid_validation_request):
        """Testa validação quando rate limit é excedido."""
        with patch('backend.app.api.credential_validation.rate_limiter') as mock_rate_limiter:
            mock_rate_limiter.check_rate_limit.side_effect = Exception("Rate limit exceeded")
            
            with pytest.raises(Exception, match="Rate limit exceeded"):
                await validate_credential(
                    valid_validation_request,
                    mock_request,
                    mock_user["id"]
                )
    
    @pytest.mark.asyncio
    async def test_validate_credential_encryption_error(self, mock_request, mock_user, valid_validation_request):
        """Testa validação quando há erro na criptografia."""
        with patch('backend.app.api.credential_validation._validate_credential_internal', return_value=True), \
             patch('backend.app.api.credential_validation.encryption_service') as mock_encryption, \
             patch('backend.app.api.credential_validation.rate_limiter') as mock_rate_limiter:
            
            mock_encryption.encrypt_credential.side_effect = Exception("Encryption error")
            mock_rate_limiter.check_rate_limit.return_value = Mock(remaining=4, reset_time=time.time() + 60)
            
            response = await validate_credential(
                valid_validation_request,
                mock_request,
                mock_user["id"]
            )
            
            assert response.valid is True
            assert response.details["encrypted"] is False


class TestCredentialValidationEdgeCases:
    """Testes para casos extremos de validação."""
    
    @pytest.mark.asyncio
    async def test_validate_very_long_credential(self):
        """Testa validação de credencial muito longa."""
        long_key = "sk-proj-" + "a" * 1000
        result = await _validate_credential_internal(
            "openai",
            "api_key",
            long_key
        )
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_credential_with_special_characters(self):
        """Testa validação de credencial com caracteres especiais."""
        special_key = "sk-proj-1234567890!@#$%^&*()_+-=[]{}|;:,.<>?"
        result = await _validate_credential_internal(
            "openai",
            "api_key",
            special_key
        )
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_credential_with_unicode(self):
        """Testa validação de credencial com caracteres Unicode."""
        unicode_key = "sk-proj-1234567890áéíóúñç"
        result = await _validate_credential_internal(
            "openai",
            "api_key",
            unicode_key
        )
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_credential_with_newlines(self):
        """Testa validação de credencial com quebras de linha."""
        multiline_key = "sk-proj-1234567890\nabcdefghijklmnopqrstuvwxyz"
        result = await _validate_credential_internal(
            "openai",
            "api_key",
            multiline_key
        )
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_credential_with_tabs(self):
        """Testa validação de credencial com tabs."""
        tabbed_key = "sk-proj-1234567890\tabcdefghijklmnopqrstuvwxyz"
        result = await _validate_credential_internal(
            "openai",
            "api_key",
            tabbed_key
        )
        assert result is True


class TestCredentialValidationPerformance:
    """Testes de performance para validação de credenciais."""
    
    @pytest.mark.asyncio
    async def test_validation_performance_single(self):
        """Testa performance de validação única."""
        start_time = time.time()
        
        result = await _validate_credential_internal(
            "openai",
            "api_key",
            "sk-proj-1234567890abcdefghijklmnopqrstuvwxyz"
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert result is True
        assert execution_time < 0.1  # Deve ser muito rápido
    
    @pytest.mark.asyncio
    async def test_validation_performance_multiple(self):
        """Testa performance de múltiplas validações."""
        providers = ["openai", "deepseek", "claude", "gemini", "google"]
        keys = [
            "sk-proj-1234567890abcdefghijklmnopqrstuvwxyz",
            "sk-1234567890abcdefghijklmnopqrstuvwxyz",
            "sk-ant-api03-1234567890abcdefghijklmnopqrstuvwxyz",
            "AIzaSyB1234567890abcdefghijklmnopqrstuvwxyz",
            "AIzaSyB1234567890abcdefghijklmnopqrstuvwxyz"
        ]
        
        start_time = time.time()
        
        results = []
        for provider, key in zip(providers, keys):
            result = await _validate_credential_internal(
                provider,
                "api_key",
                key
            )
            results.append(result)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert all(results) is True
        assert execution_time < 0.5  # Deve ser rápido mesmo com múltiplas validações


class TestCredentialValidationSecurity:
    """Testes de segurança para validação de credenciais."""
    
    @pytest.mark.asyncio
    async def test_validate_sql_injection_attempt(self):
        """Testa tentativa de SQL injection."""
        sql_injection_key = "sk-proj-1234567890'; DROP TABLE users; --"
        result = await _validate_credential_internal(
            "openai",
            "api_key",
            sql_injection_key
        )
        assert result is True  # Deve aceitar a chave, mas não executar SQL
    
    @pytest.mark.asyncio
    async def test_validate_xss_attempt(self):
        """Testa tentativa de XSS."""
        xss_key = "sk-proj-1234567890<script>alert('xss')</script>"
        result = await _validate_credential_internal(
            "openai",
            "api_key",
            xss_key
        )
        assert result is True  # Deve aceitar a chave, mas não executar script
    
    @pytest.mark.asyncio
    async def test_validate_command_injection_attempt(self):
        """Testa tentativa de command injection."""
        command_injection_key = "sk-proj-1234567890; rm -rf /;"
        result = await _validate_credential_internal(
            "openai",
            "api_key",
            command_injection_key
        )
        assert result is True  # Deve aceitar a chave, mas não executar comandos
    
    @pytest.mark.asyncio
    async def test_validate_path_traversal_attempt(self):
        """Testa tentativa de path traversal."""
        path_traversal_key = "sk-proj-1234567890../../../etc/passwd"
        result = await _validate_credential_internal(
            "openai",
            "api_key",
            path_traversal_key
        )
        assert result is True  # Deve aceitar a chave, mas não acessar arquivos


if __name__ == "__main__":
    pytest.main([__file__, "-value"]) 