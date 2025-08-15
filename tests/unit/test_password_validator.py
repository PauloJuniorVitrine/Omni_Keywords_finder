"""
Testes Unitários para Password Strength Validator
Validador de Senha Robusto - Omni Keywords Finder

Prompt: Implementação de testes unitários para validador de senha
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import re
import hashlib
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List

from backend.app.utils.password_validator import (
    PasswordValidator,
    PasswordValidationResult,
    validate_password_strength,
    is_password_strong_enough,
    get_password_suggestions
)


class TestPasswordValidationResult:
    """Testes para PasswordValidationResult"""
    
    def test_password_validation_result_creation(self):
        """Testa criação de PasswordValidationResult"""
        result = PasswordValidationResult(
            is_valid=True,
            score=85,
            strength="very_strong",
            issues=[],
            suggestions=[]
        )
        
        assert result.is_valid is True
        assert result.score == 85
        assert result.strength == "very_strong"
        assert len(result.issues) == 0
        assert len(result.suggestions) == 0
    
    def test_password_validation_result_with_issues(self):
        """Testa criação de PasswordValidationResult com issues"""
        result = PasswordValidationResult(
            is_valid=False,
            score=30,
            strength="weak",
            issues=["Senha muito curta", "Falta caractere especial"],
            suggestions=["Adicione mais caracteres", "Use símbolos"]
        )
        
        assert result.is_valid is False
        assert result.score == 30
        assert result.strength == "weak"
        assert len(result.issues) == 2
        assert len(result.suggestions) == 2


class TestPasswordValidator:
    """Testes para PasswordValidator"""
    
    @pytest.fixture
    def password_validator(self):
        """Instância do PasswordValidator para testes"""
        return PasswordValidator()
    
    def test_password_validator_initialization(self, password_validator):
        """Testa inicialização do PasswordValidator"""
        assert password_validator.min_length == 8
        assert password_validator.max_length == 128
        assert password_validator.common_passwords_file == "common_passwords.txt"
        assert password_validator.pwned_api_url == "https://api.pwnedpasswords.com/range/"
        assert len(password_validator.common_passwords) > 0
        assert len(password_validator.patterns) == 7
    
    def test_load_common_passwords(self, password_validator):
        """Testa carregamento de senhas comuns"""
        common_passwords = password_validator._load_common_passwords()
        
        assert isinstance(common_passwords, set)
        assert len(common_passwords) > 0
        assert 'password' in common_passwords
        assert '123456' in common_passwords
        assert 'admin' in common_passwords
    
    def test_validate_password_empty(self, password_validator):
        """Testa validação de senha vazia"""
        result = password_validator.validate_password("")
        
        assert result.is_valid is False
        assert result.score == 0
        assert result.strength == "very_weak"
        assert "Senha não pode estar vazia" in result.issues
    
    def test_validate_password_none(self, password_validator):
        """Testa validação de senha None"""
        result = password_validator.validate_password(None)
        
        assert result.is_valid is False
        assert result.score == 0
        assert result.strength == "very_weak"
        assert "Senha não pode estar vazia" in result.issues
    
    def test_validate_password_too_short(self, password_validator):
        """Testa validação de senha muito curta"""
        result = password_validator.validate_password("abc123")
        
        assert result.is_valid is False
        assert result.score == 0
        assert result.strength == "very_weak"
        assert "Senha deve ter pelo menos 8 caracteres" in result.issues
    
    def test_validate_password_too_long(self, password_validator):
        """Testa validação de senha muito longa"""
        long_password = "a" * 129  # 129 caracteres
        result = password_validator.validate_password(long_password)
        
        assert result.is_valid is False
        assert result.score == 0
        assert result.strength == "very_weak"
        assert "Senha deve ter no máximo 128 caracteres" in result.issues
    
    def test_validate_password_common_password(self, password_validator):
        """Testa validação de senha comum"""
        result = password_validator.validate_password("password")
        
        assert result.is_valid is False
        assert result.score == 0
        assert result.strength == "very_weak"
        assert "Senha muito comum" in result.issues
    
    def test_validate_password_suspicious_chars(self, password_validator):
        """Testa validação de senha com caracteres suspeitos"""
        result = password_validator.validate_password("pass<script>word")
        
        assert result.is_valid is False
        assert result.score == 0
        assert result.strength == "very_weak"
        assert "Senha contém caracteres não permitidos" in result.issues
    
    def test_validate_password_keyboard_patterns(self, password_validator):
        """Testa validação de senha com padrões de teclado"""
        result = password_validator.validate_password("qwerty123")
        
        assert result.is_valid is False
        assert result.score == 0
        assert result.strength == "very_weak"
        assert "Senha contém padrões de teclado comuns" in result.issues
    
    def test_validate_password_consecutive_chars(self, password_validator):
        """Testa validação de senha com caracteres consecutivos"""
        result = password_validator.validate_password("passssword123")
        
        assert result.is_valid is False
        assert result.score == 0
        assert result.strength == "very_weak"
        assert "Senha contém caracteres consecutivos" in result.issues
    
    def test_validate_password_missing_uppercase(self, password_validator):
        """Testa validação de senha sem maiúsculas"""
        result = password_validator.validate_password("password123!")
        
        assert result.is_valid is False
        assert result.score == 0
        assert result.strength == "very_weak"
        assert "Senha deve conter pelo menos uma letra maiúscula" in result.issues
    
    def test_validate_password_missing_lowercase(self, password_validator):
        """Testa validação de senha sem minúsculas"""
        result = password_validator.validate_password("PASSWORD123!")
        
        assert result.is_valid is False
        assert result.score == 0
        assert result.strength == "very_weak"
        assert "Senha deve conter pelo menos uma letra minúscula" in result.issues
    
    def test_validate_password_missing_digit(self, password_validator):
        """Testa validação de senha sem números"""
        result = password_validator.validate_password("Password!")
        
        assert result.is_valid is False
        assert result.score == 0
        assert result.strength == "very_weak"
        assert "Senha deve conter pelo menos um número" in result.issues
    
    def test_validate_password_missing_special(self, password_validator):
        """Testa validação de senha sem caracteres especiais"""
        result = password_validator.validate_password("Password123")
        
        assert result.is_valid is False
        assert result.score == 0
        assert result.strength == "very_weak"
        assert "Senha deve conter pelo menos um caractere especial" in result.issues
    
    def test_validate_password_contains_username(self, password_validator):
        """Testa validação de senha que contém username"""
        result = password_validator.validate_password("johnpassword123!", username="john")
        
        assert result.is_valid is False
        assert result.score == 0
        assert result.strength == "very_weak"
        assert "Senha não deve conter o nome de usuário" in result.issues
    
    def test_validate_password_contains_email(self, password_validator):
        """Testa validação de senha que contém parte do email"""
        result = password_validator.validate_password("johnpassword123!", email="john@example.com")
        
        assert result.is_valid is False
        assert result.score == 0
        assert result.strength == "very_weak"
        assert "Senha não deve conter parte do email" in result.issues
    
    def test_validate_password_strong(self, password_validator):
        """Testa validação de senha forte"""
        result = password_validator.validate_password("MySecureP@ssw0rd!")
        
        assert result.is_valid is True
        assert result.score >= 60
        assert result.strength in ["strong", "very_strong"]
        assert len(result.issues) == 0
    
    def test_validate_password_very_strong(self, password_validator):
        """Testa validação de senha muito forte"""
        result = password_validator.validate_password("MyVerySecureP@ssw0rd2024!")
        
        assert result.is_valid is True
        assert result.score >= 80
        assert result.strength == "very_strong"
        assert len(result.issues) == 0
    
    def test_validate_password_medium_strength(self, password_validator):
        """Testa validação de senha de força média"""
        result = password_validator.validate_password("MyPassword123")
        
        assert result.is_valid is True
        assert 40 <= result.score < 60
        assert result.strength == "medium"
    
    def test_validate_password_weak(self, password_validator):
        """Testa validação de senha fraca"""
        result = password_validator.validate_password("mypassword")
        
        assert result.is_valid is False
        assert 20 <= result.score < 40
        assert result.strength == "weak"
    
    def test_validate_password_very_weak(self, password_validator):
        """Testa validação de senha muito fraca"""
        result = password_validator.validate_password("123")
        
        assert result.is_valid is False
        assert result.score < 20
        assert result.strength == "very_weak"
    
    def test_determine_strength(self, password_validator):
        """Testa determinação de força da senha"""
        assert password_validator._determine_strength(85) == "very_strong"
        assert password_validator._determine_strength(70) == "strong"
        assert password_validator._determine_strength(50) == "medium"
        assert password_validator._determine_strength(30) == "weak"
        assert password_validator._determine_strength(10) == "very_weak"
    
    @patch('backend.app.utils.password_validator.requests.get')
    def test_check_pwned_password_compromised(self, mock_get, password_validator):
        """Testa verificação de senha comprometida"""
        # Mock de senha comprometida
        password = "password123"
        password_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix = password_hash[:5]
        suffix = password_hash[5:]
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = f"{suffix}:5\n"  # Senha aparece 5 vezes
        mock_get.return_value = mock_response
        
        result = password_validator._check_pwned_password(password)
        
        assert result is True
        mock_get.assert_called_once_with(f"{password_validator.pwned_api_url}{prefix}", timeout=5)
    
    @patch('backend.app.utils.password_validator.requests.get')
    def test_check_pwned_password_not_compromised(self, mock_get, password_validator):
        """Testa verificação de senha não comprometida"""
        # Mock de senha não comprometida
        password = "MySecureP@ssw0rd2024!"
        password_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix = password_hash[:5]
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OTHER_HASH:1\n"  # Outra senha, não a nossa
        mock_get.return_value = mock_response
        
        result = password_validator._check_pwned_password(password)
        
        assert result is False
    
    @patch('backend.app.utils.password_validator.requests.get')
    def test_check_pwned_password_api_error(self, mock_get, password_validator):
        """Testa verificação de senha com erro na API"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        result = password_validator._check_pwned_password("password123")
        
        assert result is False
    
    @patch('backend.app.utils.password_validator.requests.get')
    def test_check_pwned_password_network_error(self, mock_get, password_validator):
        """Testa verificação de senha com erro de rede"""
        mock_get.side_effect = Exception("Network error")
        
        result = password_validator._check_pwned_password("password123")
        
        assert result is False
    
    def test_generate_password_suggestions(self, password_validator):
        """Testa geração de sugestões de senha"""
        suggestions = password_validator.generate_password_suggestions()
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert all(isinstance(suggestion, str) for suggestion in suggestions)
        assert "Use uma frase memorável" in suggestions[0]
    
    def test_validate_password_policy_valid(self, password_validator):
        """Testa validação de senha contra política válida"""
        password = "MySecureP@ssw0rd123!"
        policy = {
            'min_length': 8,
            'max_length': 128,
            'require_uppercase': True,
            'require_lowercase': True,
            'require_digit': True,
            'require_special': True,
            'forbid_common': True
        }
        
        is_valid, errors = password_validator.validate_password_policy(password, policy)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_password_policy_invalid(self, password_validator):
        """Testa validação de senha contra política inválida"""
        password = "weak"
        policy = {
            'min_length': 8,
            'require_uppercase': True,
            'require_digit': True
        }
        
        is_valid, errors = password_validator.validate_password_policy(password, policy)
        
        assert is_valid is False
        assert len(errors) > 0
        assert "Senha deve ter pelo menos 8 caracteres" in errors
        assert "Senha deve conter pelo menos uma letra maiúscula" in errors
        assert "Senha deve conter pelo menos um número" in errors
    
    def test_validate_password_policy_common_password(self, password_validator):
        """Testa validação de senha comum contra política"""
        password = "password"
        policy = {
            'min_length': 8,
            'forbid_common': True
        }
        
        is_valid, errors = password_validator.validate_password_policy(password, policy)
        
        assert is_valid is False
        assert "Senha muito comum" in errors


class TestPasswordValidatorIntegration:
    """Testes de integração para PasswordValidator"""
    
    @pytest.fixture
    def password_validator(self):
        """Instância do PasswordValidator para testes"""
        return PasswordValidator()
    
    @patch('backend.app.utils.password_validator.requests.get')
    def test_full_password_validation_workflow(self, mock_get, password_validator):
        """Testa workflow completo de validação de senha"""
        # Mock de senha não comprometida
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OTHER_HASH:1\n"
        mock_get.return_value = mock_response
        
        # Testar senha forte
        result = password_validator.validate_password(
            "MySecureP@ssw0rd2024!",
            username="john",
            email="john@example.com"
        )
        
        assert result.is_valid is True
        assert result.score >= 80
        assert result.strength == "very_strong"
        assert len(result.issues) == 0
        assert len(result.suggestions) == 0
        
        # Verificar se a API foi chamada
        mock_get.assert_called_once()
    
    def test_password_validation_with_personal_info(self, password_validator):
        """Testa validação de senha com informações pessoais"""
        # Senha contém username
        result = password_validator.validate_password(
            "johnpassword123!",
            username="john",
            email="john@example.com"
        )
        
        assert result.is_valid is False
        assert "Senha não deve conter o nome de usuário" in result.issues
        
        # Senha contém parte do email
        result = password_validator.validate_password(
            "johnpassword123!",
            username="admin",
            email="john@example.com"
        )
        
        assert result.is_valid is False
        assert "Senha não deve conter parte do email" in result.issues


class TestPasswordValidatorErrorHandling:
    """Testes de tratamento de erros para PasswordValidator"""
    
    @pytest.fixture
    def password_validator(self):
        """Instância do PasswordValidator para testes"""
        return PasswordValidator()
    
    def test_validate_password_with_special_characters(self, password_validator):
        """Testa validação de senha com caracteres especiais válidos"""
        result = password_validator.validate_password("MyP@ssw0rd!")
        
        assert result.is_valid is True
        assert result.score > 0
        assert "!" in result.suggestions or len(result.issues) == 0
    
    def test_validate_password_with_unicode(self, password_validator):
        """Testa validação de senha com caracteres Unicode"""
        result = password_validator.validate_password("MyP@ssw0rdçã")
        
        # Deve funcionar sem erro
        assert isinstance(result, PasswordValidationResult)
        assert hasattr(result, 'is_valid')
        assert hasattr(result, 'score')


class TestPasswordValidatorPerformance:
    """Testes de performance para PasswordValidator"""
    
    @pytest.fixture
    def password_validator(self):
        """Instância do PasswordValidator para testes"""
        return PasswordValidator()
    
    def test_multiple_password_validations_performance(self, password_validator):
        """Testa performance de múltiplas validações de senha"""
        import time
        
        passwords = [
            "weak",
            "password123",
            "MyPassword123",
            "MySecureP@ssw0rd123!",
            "MyVerySecureP@ssw0rd2024!",
            "qwerty123",
            "admin123",
            "test123",
            "user123",
            "pass123"
        ]
        
        start_time = time.time()
        
        results = []
        for password in passwords:
            result = password_validator.validate_password(password)
            results.append(result)
        
        end_time = time.time()
        
        # Verificar performance (deve ser rápido)
        assert end_time - start_time < 2.0  # Menos de 2 segundos para 10 validações
        assert len(results) == 10
        
        # Verificar que todos os resultados são válidos
        for result in results:
            assert isinstance(result, PasswordValidationResult)
            assert hasattr(result, 'is_valid')
            assert hasattr(result, 'score')
            assert hasattr(result, 'strength')


class TestPasswordValidatorFunctions:
    """Testes para funções de conveniência"""
    
    def test_validate_password_strength_function(self):
        """Testa função validate_password_strength"""
        result = validate_password_strength("MySecureP@ssw0rd123!")
        
        assert isinstance(result, PasswordValidationResult)
        assert result.is_valid is True
        assert result.score > 0
    
    def test_validate_password_strength_with_username_email(self):
        """Testa função validate_password_strength com username e email"""
        result = validate_password_strength(
            "MySecureP@ssw0rd123!",
            username="john",
            email="john@example.com"
        )
        
        assert isinstance(result, PasswordValidationResult)
        assert result.is_valid is True
    
    def test_is_password_strong_enough_true(self):
        """Testa função is_password_strong_enough com senha forte"""
        result = is_password_strong_enough("MySecureP@ssw0rd123!", min_score=60)
        
        assert result is True
    
    def test_is_password_strong_enough_false(self):
        """Testa função is_password_strong_enough com senha fraca"""
        result = is_password_strong_enough("weak", min_score=60)
        
        assert result is False
    
    def test_is_password_strong_enough_custom_score(self):
        """Testa função is_password_strong_enough com score customizado"""
        result = is_password_strong_enough("MyPassword123", min_score=80)
        
        # Depende da força real da senha
        assert isinstance(result, bool)
    
    def test_get_password_suggestions_function(self):
        """Testa função get_password_suggestions"""
        suggestions = get_password_suggestions()
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert all(isinstance(suggestion, str) for suggestion in suggestions)


class TestPasswordValidatorEdgeCases:
    """Testes de casos edge para PasswordValidator"""
    
    @pytest.fixture
    def password_validator(self):
        """Instância do PasswordValidator para testes"""
        return PasswordValidator()
    
    def test_validate_password_exactly_min_length(self, password_validator):
        """Testa validação de senha com exatamente o comprimento mínimo"""
        password = "Abc123!@"  # 8 caracteres
        result = password_validator.validate_password(password)
        
        assert result.is_valid is True
        assert result.score > 0
    
    def test_validate_password_exactly_max_length(self, password_validator):
        """Testa validação de senha com exatamente o comprimento máximo"""
        password = "A" * 128  # 128 caracteres
        result = password_validator.validate_password(password)
        
        assert result.is_valid is True
        assert result.score > 0
    
    def test_validate_password_with_spaces(self, password_validator):
        """Testa validação de senha com espaços"""
        result = password_validator.validate_password("My Password 123!")
        
        assert isinstance(result, PasswordValidationResult)
        assert hasattr(result, 'is_valid')
        assert hasattr(result, 'score')
    
    def test_validate_password_with_numbers_only(self, password_validator):
        """Testa validação de senha apenas com números"""
        result = password_validator.validate_password("123456789")
        
        assert result.is_valid is False
        assert result.score < 40
        assert result.strength in ["weak", "very_weak"]
    
    def test_validate_password_with_letters_only(self, password_validator):
        """Testa validação de senha apenas com letras"""
        result = password_validator.validate_password("MyPassword")
        
        assert result.is_valid is False
        assert result.score < 40
        assert result.strength in ["weak", "very_weak"]
    
    def test_validate_password_with_special_only(self, password_validator):
        """Testa validação de senha apenas com caracteres especiais"""
        result = password_validator.validate_password("!@#$%^&*()")
        
        assert result.is_valid is False
        assert result.score < 40
        assert result.strength in ["weak", "very_weak"]


if __name__ == "__main__":
    pytest.main([__file__]) 