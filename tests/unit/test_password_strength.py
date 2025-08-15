"""
Testes Unitários para Password Strength
Validador de Força de Senha - Omni Keywords Finder

Prompt: Implementação de testes unitários para validador de força de senha
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import re
import hashlib
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List

from backend.app.security.password_strength import (
    PasswordStrengthValidator,
    PasswordValidationResult,
    PasswordStrength,
    password_validator
)


class TestPasswordStrength:
    """Testes para enum PasswordStrength"""
    
    def test_password_strength_values(self):
        """Testa valores do enum PasswordStrength"""
        assert PasswordStrength.VERY_WEAK.value == "very_weak"
        assert PasswordStrength.WEAK.value == "weak"
        assert PasswordStrength.MEDIUM.value == "medium"
        assert PasswordStrength.STRONG.value == "strong"
        assert PasswordStrength.VERY_STRONG.value == "very_strong"
    
    def test_password_strength_comparison(self):
        """Testa comparação entre níveis de força"""
        assert PasswordStrength.VERY_WEAK != PasswordStrength.WEAK
        assert PasswordStrength.STRONG != PasswordStrength.VERY_STRONG
        assert PasswordStrength.MEDIUM == PasswordStrength.MEDIUM


class TestPasswordValidationResult:
    """Testes para PasswordValidationResult"""
    
    def test_password_validation_result_creation(self):
        """Testa criação de PasswordValidationResult"""
        result = PasswordValidationResult(
            is_valid=True,
            strength=PasswordStrength.VERY_STRONG,
            score=95,
            feedback=[],
            suggestions=[],
            breaches_found=0,
            common_patterns=[]
        )
        
        assert result.is_valid is True
        assert result.strength == PasswordStrength.VERY_STRONG
        assert result.score == 95
        assert len(result.feedback) == 0
        assert len(result.suggestions) == 0
        assert result.breaches_found == 0
        assert len(result.common_patterns) == 0
    
    def test_password_validation_result_with_issues(self):
        """Testa criação de PasswordValidationResult com problemas"""
        result = PasswordValidationResult(
            is_valid=False,
            strength=PasswordStrength.WEAK,
            score=25,
            feedback=["Senha muito curta", "Falta caractere especial"],
            suggestions=["Adicione mais caracteres", "Use símbolos"],
            breaches_found=1,
            common_patterns=["senha_comum"]
        )
        
        assert result.is_valid is False
        assert result.strength == PasswordStrength.WEAK
        assert result.score == 25
        assert len(result.feedback) == 2
        assert len(result.suggestions) == 2
        assert result.breaches_found == 1
        assert len(result.common_patterns) == 1


class TestPasswordStrengthValidator:
    """Testes para PasswordStrengthValidator"""
    
    @pytest.fixture
    def validator(self):
        """Instância do PasswordStrengthValidator para testes"""
        return PasswordStrengthValidator()
    
    def test_validator_initialization(self, validator):
        """Testa inicialização do PasswordStrengthValidator"""
        assert validator.min_length == 8
        assert validator.max_length == 128
        assert validator.require_uppercase is True
        assert validator.require_lowercase is True
        assert validator.require_digits is True
        assert validator.require_special is True
        assert len(validator.common_passwords) > 0
        assert len(validator.common_patterns) > 0
        assert len(validator.special_chars) > 0
    
    def test_load_common_passwords(self, validator):
        """Testa carregamento de senhas comuns"""
        common_passwords = validator._load_common_passwords()
        
        assert isinstance(common_passwords, set)
        assert len(common_passwords) > 0
        assert 'password' in common_passwords
        assert '123456' in common_passwords
        assert 'admin' in common_passwords
    
    def test_validate_password_empty(self, validator):
        """Testa validação de senha vazia"""
        result = validator.validate_password("")
        
        assert result.is_valid is False
        assert result.strength == PasswordStrength.VERY_WEAK
        assert result.score == 0
        assert "Senha é obrigatória" in result.feedback
        assert len(result.suggestions) > 0
    
    def test_validate_password_none(self, validator):
        """Testa validação de senha None"""
        result = validator.validate_password(None)
        
        assert result.is_valid is False
        assert result.strength == PasswordStrength.VERY_WEAK
        assert result.score == 0
        assert "Senha é obrigatória" in result.feedback
    
    def test_validate_password_too_short(self, validator):
        """Testa validação de senha muito curta"""
        result = validator.validate_password("abc123")
        
        assert result.is_valid is False
        assert result.strength == PasswordStrength.VERY_WEAK
        assert result.score < 0
        assert "Senha deve ter pelo menos 8 caracteres" in result.feedback
    
    def test_validate_password_too_long(self, validator):
        """Testa validação de senha muito longa"""
        long_password = "a" * 129  # 129 caracteres
        result = validator.validate_password(long_password)
        
        assert result.is_valid is False
        assert result.strength == PasswordStrength.VERY_WEAK
        assert result.score < 0
        assert "Senha deve ter no máximo 128 caracteres" in result.feedback
    
    def test_validate_password_common_password(self, validator):
        """Testa validação de senha comum"""
        result = validator.validate_password("password")
        
        assert result.is_valid is False
        assert result.strength == PasswordStrength.VERY_WEAK
        assert result.score < 0
        assert "Senha muito comum" in result.feedback
        assert "senha_comum" in result.common_patterns
    
    def test_validate_password_strong(self, validator):
        """Testa validação de senha forte"""
        result = validator.validate_password("MySecureP@ssw0rd123!")
        
        assert result.is_valid is True
        assert result.strength in [PasswordStrength.STRONG, PasswordStrength.VERY_STRONG]
        assert result.score >= 60
        assert len(result.feedback) == 0 or all("Evite" not in f for f in result.feedback)
    
    def test_validate_password_very_strong(self, validator):
        """Testa validação de senha muito forte"""
        result = validator.validate_password("MyVerySecureP@ssw0rd2024!")
        
        assert result.is_valid is True
        assert result.strength == PasswordStrength.VERY_STRONG
        assert result.score >= 80
        assert len(result.feedback) == 0 or all("Evite" not in f for f in result.feedback)
    
    def test_validate_password_medium(self, validator):
        """Testa validação de senha de força média"""
        result = validator.validate_password("MyPassword123")
        
        assert result.is_valid is True
        assert result.strength == PasswordStrength.MEDIUM
        assert 40 <= result.score < 60
    
    def test_validate_password_weak(self, validator):
        """Testa validação de senha fraca"""
        result = validator.validate_password("mypassword")
        
        assert result.is_valid is False
        assert result.strength == PasswordStrength.WEAK
        assert 20 <= result.score < 40
    
    def test_validate_password_very_weak(self, validator):
        """Testa validação de senha muito fraca"""
        result = validator.validate_password("123")
        
        assert result.is_valid is False
        assert result.strength == PasswordStrength.VERY_WEAK
        assert result.score < 20
    
    def test_validate_length_short(self, validator):
        """Testa validação de comprimento curto"""
        feedback = []
        suggestions = []
        
        score = validator._validate_length("abc", feedback, suggestions)
        
        assert score == -20
        assert "Senha deve ter pelo menos 8 caracteres" in feedback
        assert len(suggestions) > 0
    
    def test_validate_length_long(self, validator):
        """Testa validação de comprimento longo"""
        feedback = []
        suggestions = []
        long_password = "a" * 129
        
        score = validator._validate_length(long_password, feedback, suggestions)
        
        assert score == -10
        assert "Senha deve ter no máximo 128 caracteres" in feedback
    
    def test_validate_length_good(self, validator):
        """Testa validação de comprimento adequado"""
        feedback = []
        suggestions = []
        
        # Testar diferentes comprimentos
        score_8 = validator._validate_length("abcdefgh", feedback, suggestions)
        assert score_8 == 10
        
        feedback.clear()
        suggestions.clear()
        
        score_12 = validator._validate_length("abcdefghijkl", feedback, suggestions)
        assert score_12 == 20
    
    def test_validate_complexity_missing_uppercase(self, validator):
        """Testa validação de complexidade sem maiúsculas"""
        feedback = []
        suggestions = []
        
        score = validator._validate_complexity("password123!", feedback, suggestions)
        
        assert score < 0
        assert "Senha deve conter pelo menos uma letra maiúscula" in feedback
    
    def test_validate_complexity_missing_lowercase(self, validator):
        """Testa validação de complexidade sem minúsculas"""
        feedback = []
        suggestions = []
        
        score = validator._validate_complexity("PASSWORD123!", feedback, suggestions)
        
        assert score < 0
        assert "Senha deve conter pelo menos uma letra minúscula" in feedback
    
    def test_validate_complexity_missing_digits(self, validator):
        """Testa validação de complexidade sem números"""
        feedback = []
        suggestions = []
        
        score = validator._validate_complexity("Password!", feedback, suggestions)
        
        assert score < 0
        assert "Senha deve conter pelo menos um número" in feedback
    
    def test_validate_complexity_missing_special(self, validator):
        """Testa validação de complexidade sem caracteres especiais"""
        feedback = []
        suggestions = []
        
        score = validator._validate_complexity("Password123", feedback, suggestions)
        
        assert score < 0
        assert "Senha deve conter pelo menos um caractere especial" in feedback
    
    def test_validate_complexity_complete(self, validator):
        """Testa validação de complexidade completa"""
        feedback = []
        suggestions = []
        
        score = validator._validate_complexity("MyPassword123!", feedback, suggestions)
        
        assert score >= 25  # 5+5+5+10 = 25
        assert len(feedback) == 0
    
    def test_validate_common_passwords_common(self, validator):
        """Testa validação de senhas comuns"""
        feedback = []
        suggestions = []
        common_patterns = []
        
        score = validator._validate_common_passwords("password", feedback, suggestions, common_patterns)
        
        assert score == -30
        assert "Senha muito comum" in feedback
        assert "senha_comum" in common_patterns
    
    def test_validate_common_passwords_variation(self, validator):
        """Testa validação de variações de senhas comuns"""
        feedback = []
        suggestions = []
        common_patterns = []
        
        score = validator._validate_common_passwords("password123", feedback, suggestions, common_patterns)
        
        assert score == -20
        assert "Senha similar a senhas comuns" in feedback
        assert "variacao_comum" in common_patterns
    
    def test_validate_common_passwords_unique(self, validator):
        """Testa validação de senha única"""
        feedback = []
        suggestions = []
        common_patterns = []
        
        score = validator._validate_common_passwords("MyUniquePassword2024!", feedback, suggestions, common_patterns)
        
        assert score == 10
        assert len(feedback) == 0
        assert len(common_patterns) == 0
    
    def test_validate_patterns_sequences(self, validator):
        """Testa validação de padrões com sequências"""
        feedback = []
        suggestions = []
        common_patterns = []
        
        score = validator._validate_patterns("password123", feedback, suggestions, common_patterns)
        
        assert score < 0
        assert "sequência numérica" in ' '.join(feedback).lower()
        assert "sequencia_numerica" in common_patterns
    
    def test_validate_patterns_repetitions(self, validator):
        """Testa validação de padrões com repetições"""
        feedback = []
        suggestions = []
        common_patterns = []
        
        score = validator._validate_patterns("passssword", feedback, suggestions, common_patterns)
        
        assert score < 0
        assert "caracteres repetidos" in ' '.join(feedback).lower()
        assert "caracteres_repetidos" in common_patterns
    
    def test_validate_patterns_keyboard(self, validator):
        """Testa validação de padrões de teclado"""
        feedback = []
        suggestions = []
        common_patterns = []
        
        score = validator._validate_patterns("qwerty123", feedback, suggestions, common_patterns)
        
        assert score < 0
        assert "padrões do teclado" in ' '.join(feedback).lower()
        assert "padrao_teclado" in common_patterns
    
    def test_validate_context_username(self, validator):
        """Testa validação de contexto com username"""
        feedback = []
        suggestions = []
        
        score = validator._validate_context("johnpassword123!", "john", None, feedback, suggestions)
        
        assert score == -25
        assert "Senha não deve conter o nome de usuário" in feedback
    
    def test_validate_context_email(self, validator):
        """Testa validação de contexto com email"""
        feedback = []
        suggestions = []
        
        score = validator._validate_context("johnpassword123!", None, "john@example.com", feedback, suggestions)
        
        assert score == -20
        assert "Senha não deve conter partes do email" in feedback
    
    def test_validate_context_clean(self, validator):
        """Testa validação de contexto limpo"""
        feedback = []
        suggestions = []
        
        score = validator._validate_context("MySecurePassword123!", "john", "john@example.com", feedback, suggestions)
        
        assert score == 0
        assert len(feedback) == 0
    
    def test_validate_repetitions_excessive(self, validator):
        """Testa validação de repetições excessivas"""
        feedback = []
        suggestions = []
        
        score = validator._validate_repetitions("aaaaaaa", feedback, suggestions)
        
        assert score < 0
        assert "Muitos caracteres repetidos" in feedback
    
    def test_validate_repetitions_patterns(self, validator):
        """Testa validação de repetições de padrões"""
        feedback = []
        suggestions = []
        
        score = validator._validate_repetitions("abcabc", feedback, suggestions)
        
        assert score < 0
        assert "Padrões repetidos detectados" in feedback
    
    def test_validate_sequences_alphabetic(self, validator):
        """Testa validação de sequências alfabéticas"""
        feedback = []
        suggestions = []
        
        score = validator._validate_sequences("passwordabc", feedback, suggestions)
        
        assert score < 0
        assert "sequências alfabéticas" in ' '.join(feedback).lower()
    
    def test_validate_sequences_numeric_reverse(self, validator):
        """Testa validação de sequências numéricas reversas"""
        feedback = []
        suggestions = []
        
        score = validator._validate_sequences("password987", feedback, suggestions)
        
        assert score < 0
        assert "sequências numéricas reversas" in ' '.join(feedback).lower()
    
    def test_check_breaches_compromised(self, validator):
        """Testa verificação de senhas comprometidas"""
        feedback = []
        suggestions = []
        
        score = validator._check_breaches("password", feedback, suggestions)
        
        assert score == -50
        assert "Esta senha foi encontrada em vazamentos de dados" in feedback
    
    def test_check_breaches_safe(self, validator):
        """Testa verificação de senhas seguras"""
        feedback = []
        suggestions = []
        
        score = validator._check_breaches("MySecurePassword2024!", feedback, suggestions)
        
        assert score == 10
        assert len(feedback) == 0
    
    def test_determine_strength(self, validator):
        """Testa determinação de força da senha"""
        assert validator._determine_strength(85) == PasswordStrength.VERY_STRONG
        assert validator._determine_strength(70) == PasswordStrength.STRONG
        assert validator._determine_strength(50) == PasswordStrength.MEDIUM
        assert validator._determine_strength(30) == PasswordStrength.WEAK
        assert validator._determine_strength(10) == PasswordStrength.VERY_WEAK
    
    def test_is_valid_password_valid(self, validator):
        """Testa verificação de senha válida"""
        feedback = []
        is_valid = validator._is_valid_password(60, feedback)
        
        assert is_valid is True
    
    def test_is_valid_password_invalid_score(self, validator):
        """Testa verificação de senha inválida por score"""
        feedback = []
        is_valid = validator._is_valid_password(30, feedback)
        
        assert is_valid is False
    
    def test_is_valid_password_critical_feedback(self, validator):
        """Testa verificação de senha inválida por feedback crítico"""
        feedback = ["Senha muito comum - escolha algo mais único"]
        is_valid = validator._is_valid_password(60, feedback)
        
        assert is_valid is False
    
    def test_generate_strong_password(self, validator):
        """Testa geração de senha forte"""
        password = validator.generate_strong_password(16)
        
        assert len(password) == 16
        assert re.search(r'[a-z]', password)  # minúscula
        assert re.search(r'[A-Z]', password)  # maiúscula
        assert re.search(r'\d', password)     # número
        assert re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password)  # especial
    
    def test_generate_strong_password_minimum_length(self, validator):
        """Testa geração de senha forte com comprimento mínimo"""
        password = validator.generate_strong_password(4)  # Muito curto
        
        assert len(password) == 8  # Deve usar o mínimo
        assert re.search(r'[a-z]', password)
        assert re.search(r'[A-Z]', password)
        assert re.search(r'\d', password)
        assert re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password)
    
    def test_get_strength_description(self, validator):
        """Testa obtenção de descrição de força"""
        descriptions = {
            PasswordStrength.VERY_WEAK: "Muito fraca - deve ser alterada imediatamente",
            PasswordStrength.WEAK: "Fraca - precisa de melhorias",
            PasswordStrength.MEDIUM: "Média - aceitável mas pode ser melhorada",
            PasswordStrength.STRONG: "Forte - boa segurança",
            PasswordStrength.VERY_STRONG: "Muito forte - excelente segurança"
        }
        
        for strength, expected_desc in descriptions.items():
            desc = validator.get_strength_description(strength)
            assert desc == expected_desc


class TestPasswordStrengthValidatorIntegration:
    """Testes de integração para PasswordStrengthValidator"""
    
    @pytest.fixture
    def validator(self):
        """Instância do PasswordStrengthValidator para testes"""
        return PasswordStrengthValidator()
    
    def test_full_password_validation_workflow(self, validator):
        """Testa workflow completo de validação de senha"""
        # Testar senha forte
        result = validator.validate_password(
            "MySecureP@ssw0rd2024!",
            username="john",
            email="john@example.com"
        )
        
        assert result.is_valid is True
        assert result.strength in [PasswordStrength.STRONG, PasswordStrength.VERY_STRONG]
        assert result.score >= 60
        assert result.breaches_found == 0
        assert len(result.common_patterns) == 0
    
    def test_password_validation_with_personal_info(self, validator):
        """Testa validação de senha com informações pessoais"""
        # Senha contém username
        result = validator.validate_password(
            "johnpassword123!",
            username="john",
            email="john@example.com"
        )
        
        assert result.is_valid is False
        assert "Senha não deve conter o nome de usuário" in result.feedback
        
        # Senha contém parte do email
        result = validator.validate_password(
            "johnpassword123!",
            username="admin",
            email="john@example.com"
        )
        
        assert result.is_valid is False
        assert "Senha não deve conter partes do email" in result.feedback


class TestPasswordStrengthValidatorErrorHandling:
    """Testes de tratamento de erros para PasswordStrengthValidator"""
    
    @pytest.fixture
    def validator(self):
        """Instância do PasswordStrengthValidator para testes"""
        return PasswordStrengthValidator()
    
    def test_validate_password_with_special_characters(self, validator):
        """Testa validação de senha com caracteres especiais válidos"""
        result = validator.validate_password("MyP@ssw0rd!")
        
        assert isinstance(result, PasswordValidationResult)
        assert hasattr(result, 'is_valid')
        assert hasattr(result, 'score')
        assert hasattr(result, 'strength')
    
    def test_validate_password_with_unicode(self, validator):
        """Testa validação de senha com caracteres Unicode"""
        result = validator.validate_password("MyP@ssw0rdçã")
        
        # Deve funcionar sem erro
        assert isinstance(result, PasswordValidationResult)
        assert hasattr(result, 'is_valid')
        assert hasattr(result, 'score')


class TestPasswordStrengthValidatorPerformance:
    """Testes de performance para PasswordStrengthValidator"""
    
    @pytest.fixture
    def validator(self):
        """Instância do PasswordStrengthValidator para testes"""
        return PasswordStrengthValidator()
    
    def test_multiple_password_validations_performance(self, validator):
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
            result = validator.validate_password(password)
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


class TestPasswordStrengthValidatorGlobal:
    """Testes para instância global do PasswordStrengthValidator"""
    
    def test_global_password_validator(self):
        """Testa instância global do validador"""
        result = password_validator.validate_password("MySecureP@ssw0rd123!")
        
        assert isinstance(result, PasswordValidationResult)
        assert result.is_valid is True
        assert result.strength in [PasswordStrength.STRONG, PasswordStrength.VERY_STRONG]
        assert result.score >= 60
    
    def test_global_password_generator(self):
        """Testa gerador de senha da instância global"""
        password = password_validator.generate_strong_password(16)
        
        assert len(password) == 16
        assert re.search(r'[a-z]', password)
        assert re.search(r'[A-Z]', password)
        assert re.search(r'\d', password)
        assert re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password)


class TestPasswordStrengthValidatorEdgeCases:
    """Testes de casos edge para PasswordStrengthValidator"""
    
    @pytest.fixture
    def validator(self):
        """Instância do PasswordStrengthValidator para testes"""
        return PasswordStrengthValidator()
    
    def test_validate_password_exactly_min_length(self, validator):
        """Testa validação de senha com exatamente o comprimento mínimo"""
        password = "Abc123!@"  # 8 caracteres
        result = validator.validate_password(password)
        
        assert result.is_valid is True
        assert result.score > 0
    
    def test_validate_password_exactly_max_length(self, validator):
        """Testa validação de senha com exatamente o comprimento máximo"""
        password = "A" * 128  # 128 caracteres
        result = validator.validate_password(password)
        
        assert result.is_valid is True
        assert result.score > 0
    
    def test_validate_password_with_spaces(self, validator):
        """Testa validação de senha com espaços"""
        result = validator.validate_password("My Password 123!")
        
        assert isinstance(result, PasswordValidationResult)
        assert hasattr(result, 'is_valid')
        assert hasattr(result, 'score')
        assert hasattr(result, 'strength')
    
    def test_validate_password_with_numbers_only(self, validator):
        """Testa validação de senha apenas com números"""
        result = validator.validate_password("123456789")
        
        assert result.is_valid is False
        assert result.score < 40
        assert result.strength in [PasswordStrength.WEAK, PasswordStrength.VERY_WEAK]
    
    def test_validate_password_with_letters_only(self, validator):
        """Testa validação de senha apenas com letras"""
        result = validator.validate_password("MyPassword")
        
        assert result.is_valid is False
        assert result.score < 40
        assert result.strength in [PasswordStrength.WEAK, PasswordStrength.VERY_WEAK]
    
    def test_validate_password_with_special_only(self, validator):
        """Testa validação de senha apenas com caracteres especiais"""
        result = validator.validate_password("!@#$%^&*()")
        
        assert result.is_valid is False
        assert result.score < 40
        assert result.strength in [PasswordStrength.WEAK, PasswordStrength.VERY_WEAK]


if __name__ == "__main__":
    pytest.main([__file__]) 