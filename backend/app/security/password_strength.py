"""
Validador de Força de Senha - Omni Keywords Finder
Implementa validação seguindo diretrizes NIST SP 800-63B

Prompt: Implementação de validador robusto de força de senha
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import re
import hashlib
import requests
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class PasswordStrength(Enum):
    """Níveis de força de senha"""
    VERY_WEAK = "very_weak"
    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"
    VERY_STRONG = "very_strong"

@dataclass
class PasswordValidationResult:
    """Resultado da validação de senha"""
    is_valid: bool
    strength: PasswordStrength
    score: int  # 0-100
    feedback: List[str]
    suggestions: List[str]
    breaches_found: int
    common_patterns: List[str]

class PasswordStrengthValidator:
    """Validador de força de senha seguindo NIST SP 800-63B"""
    
    def __init__(self):
        # Lista de senhas comuns (top 1000)
        self.common_passwords = self._load_common_passwords()
        
        # Padrões comuns a evitar
        self.common_patterns = [
            r'123456',
            r'password',
            r'qwerty',
            r'abc123',
            r'admin',
            r'letmein',
            r'welcome',
            r'monkey',
            r'dragon',
            r'master',
            r'football',
            r'baseball',
            r'starwars',
            r'harrypotter',
            r'superman',
            r'batman',
            r'spider',
            r'ironman',
            r'captain',
            r'thor'
        ]
        
        # Caracteres especiais permitidos
        self.special_chars = r'!@#$%^&*()_+-=[]{}|;:,.<>?'
        
        # Configurações NIST
        self.min_length = 8
        self.max_length = 128
        self.require_uppercase = True
        self.require_lowercase = True
        self.require_digits = True
        self.require_special = True
    
    def _load_common_passwords(self) -> set:
        """Carrega lista de senhas comuns"""
        # Em produção, carregar de arquivo ou API
        return {
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey',
            'dragon', 'master', 'football', 'baseball', 'starwars',
            'harrypotter', 'superman', 'batman', 'spider', 'ironman'
        }
    
    def validate_password(self, password: str, username: str = None, email: str = None) -> PasswordValidationResult:
        """Valida força da senha seguindo NIST SP 800-63B"""
        feedback = []
        suggestions = []
        score = 0
        breaches_found = 0
        common_patterns = []
        
        # Validações básicas
        if not password:
            return PasswordValidationResult(
                is_valid=False,
                strength=PasswordStrength.VERY_WEAK,
                score=0,
                feedback=['Senha é obrigatória'],
                suggestions=['Digite uma senha'],
                breaches_found=0,
                common_patterns=[]
            )
        
        # 1. Verificar comprimento
        length_score = self._validate_length(password, feedback, suggestions)
        score += length_score
        
        # 2. Verificar complexidade
        complexity_score = self._validate_complexity(password, feedback, suggestions)
        score += complexity_score
        
        # 3. Verificar senhas comuns
        common_score = self._validate_common_passwords(password, feedback, suggestions, common_patterns)
        score += common_score
        
        # 4. Verificar padrões comuns
        pattern_score = self._validate_patterns(password, feedback, suggestions, common_patterns)
        score += pattern_score
        
        # 5. Verificar contexto (username, email)
        context_score = self._validate_context(password, username, email, feedback, suggestions)
        score += context_score
        
        # 6. Verificar repetições
        repetition_score = self._validate_repetitions(password, feedback, suggestions)
        score += repetition_score
        
        # 7. Verificar sequências
        sequence_score = self._validate_sequences(password, feedback, suggestions)
        score += sequence_score
        
        # 8. Verificar vazamentos (simulado)
        breach_score = self._check_breaches(password, feedback, suggestions)
        score += breach_score
        breaches_found = 1 if breach_score < 0 else 0
        
        # Determinar força baseada no score
        strength = self._determine_strength(score)
        
        # Verificar se é válida
        is_valid = self._is_valid_password(score, feedback)
        
        return PasswordValidationResult(
            is_valid=is_valid,
            strength=strength,
            score=max(0, min(100, score)),
            feedback=feedback,
            suggestions=suggestions,
            breaches_found=breaches_found,
            common_patterns=common_patterns
        )
    
    def _validate_length(self, password: str, feedback: List[str], suggestions: List[str]) -> int:
        """Valida comprimento da senha"""
        length = len(password)
        score = 0
        
        if length < self.min_length:
            feedback.append(f'Senha deve ter pelo menos {self.min_length} caracteres')
            suggestions.append(f'Adicione mais {self.min_length - length} caracteres')
            return -20
        
        if length > self.max_length:
            feedback.append(f'Senha deve ter no máximo {self.max_length} caracteres')
            suggestions.append('Reduza o tamanho da senha')
            return -10
        
        # Pontuação por comprimento
        if length >= 12:
            score += 20
        elif length >= 10:
            score += 15
        elif length >= 8:
            score += 10
        
        return score
    
    def _validate_complexity(self, password: str, feedback: List[str], suggestions: List[str]) -> int:
        """Valida complexidade da senha"""
        score = 0
        
        # Verificar maiúsculas
        if re.search(r'[A-Z]', password):
            score += 5
        elif self.require_uppercase:
            feedback.append('Senha deve conter pelo menos uma letra maiúscula')
            suggestions.append('Adicione letras maiúsculas')
            score -= 10
        
        # Verificar minúsculas
        if re.search(r'[a-z]', password):
            score += 5
        elif self.require_lowercase:
            feedback.append('Senha deve conter pelo menos uma letra minúscula')
            suggestions.append('Adicione letras minúsculas')
            score -= 10
        
        # Verificar dígitos
        if re.search(r'\d', password):
            score += 5
        elif self.require_digits:
            feedback.append('Senha deve conter pelo menos um número')
            suggestions.append('Adicione números')
            score -= 10
        
        # Verificar caracteres especiais
        if re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            score += 10
        elif self.require_special:
            feedback.append('Senha deve conter pelo menos um caractere especial')
            suggestions.append('Adicione caracteres especiais (!@#$%^&*)')
            score -= 15
        
        return score
    
    def _validate_common_passwords(self, password: str, feedback: List[str], suggestions: List[str], common_patterns: List[str]) -> int:
        """Verifica se a senha é comum"""
        password_lower = password.lower()
        
        if password_lower in self.common_passwords:
            feedback.append('Senha muito comum - escolha algo mais único')
            suggestions.append('Use uma combinação única de palavras')
            common_patterns.append('senha_comum')
            return -30
        
        # Verificar variações comuns
        for common in self.common_passwords:
            if common in password_lower or password_lower in common:
                feedback.append('Senha similar a senhas comuns')
                suggestions.append('Evite variações de senhas populares')
                common_patterns.append('variacao_comum')
                return -20
        
        return 10
    
    def _validate_patterns(self, password: str, feedback: List[str], suggestions: List[str], common_patterns: List[str]) -> int:
        """Verifica padrões comuns"""
        score = 0
        
        # Verificar sequências numéricas
        if re.search(r'123|234|345|456|567|678|789|890', password):
            feedback.append('Evite sequências numéricas')
            suggestions.append('Use números aleatórios')
            common_patterns.append('sequencia_numerica')
            score -= 15
        
        # Verificar repetições
        if re.search(r'(.)\1{2,}', password):
            feedback.append('Evite caracteres repetidos')
            suggestions.append('Use caracteres variados')
            common_patterns.append('caracteres_repetidos')
            score -= 10
        
        # Verificar teclado
        keyboard_patterns = ['qwerty', 'asdfgh', 'zxcvbn', '123456']
        for pattern in keyboard_patterns:
            if pattern in password.lower():
                feedback.append('Evite padrões do teclado')
                suggestions.append('Use combinações aleatórias')
                common_patterns.append('padrao_teclado')
                score -= 20
        
        return score
    
    def _validate_context(self, password: str, username: str, email: str, feedback: List[str], suggestions: List[str]) -> int:
        """Verifica contexto da senha"""
        score = 0
        
        if username and username.lower() in password.lower():
            feedback.append('Senha não deve conter o nome de usuário')
            suggestions.append('Use informações não relacionadas ao usuário')
            score -= 25
        
        if email:
            email_parts = email.lower().split('@')[0]
            if email_parts in password.lower():
                feedback.append('Senha não deve conter partes do email')
                suggestions.append('Evite usar informações pessoais')
                score -= 20
        
        return score
    
    def _validate_repetitions(self, password: str, feedback: List[str], suggestions: List[str]) -> int:
        """Verifica repetições excessivas"""
        score = 0
        
        # Verificar repetições de caracteres
        for char in set(password):
            if password.count(char) > len(password) * 0.3:
                feedback.append('Muitos caracteres repetidos')
                suggestions.append('Use mais variedade de caracteres')
                score -= 10
        
        # Verificar repetições de padrões
        for i in range(2, len(password) // 2 + 1):
            for j in range(len(password) - i + 1):
                pattern = password[j:j+i]
                if password.count(pattern) > 1:
                    feedback.append('Padrões repetidos detectados')
                    suggestions.append('Evite repetir padrões')
                    score -= 5
                    break
        
        return score
    
    def _validate_sequences(self, password: str, feedback: List[str], suggestions: List[str]) -> int:
        """Verifica sequências"""
        score = 0
        
        # Sequências alfabéticas
        if re.search(r'abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz', password.lower()):
            feedback.append('Evite sequências alfabéticas')
            suggestions.append('Use letras em ordem aleatória')
            score -= 15
        
        # Sequências numéricas reversas
        if re.search(r'987|876|765|654|543|432|321', password):
            feedback.append('Evite sequências numéricas reversas')
            suggestions.append('Use números aleatórios')
            score -= 15
        
        return score
    
    def _check_breaches(self, password: str, feedback: List[str], suggestions: List[str]) -> int:
        """Verifica vazamentos de senha (simulado)"""
        # Em produção, integrar com API como HaveIBeenPwned
        # Por enquanto, simulação
        
        # Simular verificação de hash
        password_hash = hashlib.sha1(password.encode()).hexdigest().upper()
        
        # Lista simulada de hashes vazados
        breached_hashes = {
            '5BAA61E4C9B93F3F0682250B6CF8331B7EE68FD8',  # password
            '7C4A8D09CA3762AF61E59520943DC26494F8941B',  # 123456
        }
        
        if password_hash in breached_hashes:
            feedback.append('Esta senha foi encontrada em vazamentos de dados')
            suggestions.append('Use uma senha única que nunca foi vazada')
            return -50
        
        return 10
    
    def _determine_strength(self, score: int) -> PasswordStrength:
        """Determina força da senha baseada no score"""
        if score >= 80:
            return PasswordStrength.VERY_STRONG
        elif score >= 60:
            return PasswordStrength.STRONG
        elif score >= 40:
            return PasswordStrength.MEDIUM
        elif score >= 20:
            return PasswordStrength.WEAK
        else:
            return PasswordStrength.VERY_WEAK
    
    def _is_valid_password(self, score: int, feedback: List[str]) -> bool:
        """Determina se a senha é válida"""
        # Senha é válida se score >= 40 e não há feedback crítico
        critical_feedback = [
            'Senha muito comum',
            'Esta senha foi encontrada em vazamentos',
            'Senha deve ter pelo menos'
        ]
        
        has_critical = any(critical in ' '.join(feedback) for critical in critical_feedback)
        
        return score >= 40 and not has_critical
    
    def generate_strong_password(self, length: int = 16) -> str:
        """Gera uma senha forte"""
        import secrets
        import string
        
        if length < 8:
            length = 8
        
        # Caracteres disponíveis
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special = '!@#$%^&*()_+-=[]{}|;:,.<>?'
        
        # Garantir pelo menos um de cada tipo
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(special)
        ]
        
        # Completar com caracteres aleatórios
        all_chars = lowercase + uppercase + digits + special
        for _ in range(length - 4):
            password.append(secrets.choice(all_chars))
        
        # Embaralhar
        password_list = list(password)
        secrets.SystemRandom().shuffle(password_list)
        
        return ''.join(password_list)
    
    def get_strength_description(self, strength: PasswordStrength) -> str:
        """Retorna descrição da força da senha"""
        descriptions = {
            PasswordStrength.VERY_WEAK: "Muito fraca - deve ser alterada imediatamente",
            PasswordStrength.WEAK: "Fraca - precisa de melhorias",
            PasswordStrength.MEDIUM: "Média - aceitável mas pode ser melhorada",
            PasswordStrength.STRONG: "Forte - boa segurança",
            PasswordStrength.VERY_STRONG: "Muito forte - excelente segurança"
        }
        return descriptions.get(strength, "Desconhecida")

# Instância global
password_validator = PasswordStrengthValidator() 