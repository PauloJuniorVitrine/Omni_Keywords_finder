"""
🔐 Validador de Senha Robusto

Tracing ID: PASSWORD_VALIDATOR_20250127_001
Data/Hora: 2025-01-27 16:15:00 UTC
Versão: 1.0
Status: 🔲 CRIADO MAS NÃO EXECUTADO

Validador de senha seguindo diretrizes NIST e boas práticas de segurança.
"""

import re
import hashlib
import requests
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class PasswordValidationResult:
    """Resultado da validação de senha."""
    is_valid: bool
    score: int  # 0-100
    strength: str  # 'very_weak', 'weak', 'medium', 'strong', 'very_strong'
    issues: List[str]
    suggestions: List[str]


class PasswordValidator:
    """Validador de senha robusto seguindo diretrizes NIST."""
    
    def __init__(self):
        """Inicializa o validador de senha."""
        self.min_length = 8
        self.max_length = 128
        self.common_passwords_file = "common_passwords.txt"
        self.pwned_api_url = "https://api.pwnedpasswords.com/range/"
        
        # Carregar senhas comuns
        self.common_passwords = self._load_common_passwords()
        
        # Padrões de validação
        self.patterns = {
            'uppercase': r'[A-Z]',
            'lowercase': r'[a-z]',
            'digit': r'\d',
            'special': r'[!@#$%^&*(),.?":{}|<>]',
            'consecutive_chars': r'(.)\1{2,}',  # 3+ caracteres consecutivos
            'keyboard_patterns': r'(qwerty|asdf|zxcv|123|abc|password|admin)',
            'repeating_patterns': r'(.)\1{3,}',  # 4+ caracteres repetidos
        }
    
    def _load_common_passwords(self) -> set:
        """Carrega lista de senhas comuns."""
        try:
            # Em produção, usar arquivo real ou API
            common_passwords = {
                'password', '123456', '123456789', 'qwerty', 'abc123',
                'password123', 'admin', 'admin123', 'root', 'user',
                'test', 'guest', 'welcome', 'login', 'pass123',
                '12345678', 'qwerty123', 'password1', 'admin1234',
                'letmein', 'monkey', 'dragon', 'master', 'sunshine'
            }
            return common_passwords
        except Exception as e:
            logger.warning(f"Erro ao carregar senhas comuns: {e}")
            return set()
    
    def validate_password(self, password: str, username: str = None, email: str = None) -> PasswordValidationResult:
        """
        Valida senha seguindo diretrizes NIST e boas práticas.
        
        Args:
            password: Senha a ser validada
            username: Username do usuário (opcional)
            email: Email do usuário (opcional)
            
        Returns:
            PasswordValidationResult com resultado da validação
        """
        issues = []
        suggestions = []
        score = 0
        
        # Validações básicas
        if not password:
            issues.append("Senha não pode estar vazia")
            return PasswordValidationResult(False, 0, "very_weak", issues, suggestions)
        
        # Comprimento
        if len(password) < self.min_length:
            issues.append(f"Senha deve ter pelo menos {self.min_length} caracteres")
            suggestions.append(f"Adicione pelo menos {self.min_length - len(password)} caracteres")
        elif len(password) > self.max_length:
            issues.append(f"Senha deve ter no máximo {self.max_length} caracteres")
            suggestions.append("Reduza o comprimento da senha")
        else:
            score += 20  # Pontos por comprimento adequado
        
        # Verificar se é senha comum
        if password.lower() in self.common_passwords:
            issues.append("Senha muito comum, escolha uma senha mais única")
            suggestions.append("Evite senhas comuns como 'password', '123456', etc.")
        else:
            score += 15  # Pontos por não ser comum
        
        # Verificar caracteres especiais suspeitos
        suspicious_chars = ['<', '>', '"', "'", '&', 'script', 'javascript']
        for char in suspicious_chars:
            if char in password.lower():
                issues.append("Senha contém caracteres não permitidos")
                suggestions.append("Remova caracteres especiais suspeitos")
                break
        
        # Verificar padrões de teclado
        if re.search(self.patterns['keyboard_patterns'], password.lower()):
            issues.append("Senha contém padrões de teclado comuns")
            suggestions.append("Evite padrões de teclado como 'qwerty', '123', etc.")
        else:
            score += 10  # Pontos por não ter padrões de teclado
        
        # Verificar caracteres consecutivos
        if re.search(self.patterns['consecutive_chars'], password):
            issues.append("Senha contém caracteres consecutivos")
            suggestions.append("Evite caracteres repetidos como 'aaa', '111', etc.")
        else:
            score += 10  # Pontos por não ter caracteres consecutivos
        
        # Verificar complexidade
        complexity_score = 0
        
        if re.search(self.patterns['uppercase'], password):
            complexity_score += 1
        else:
            issues.append("Senha deve conter pelo menos uma letra maiúscula")
            suggestions.append("Adicione pelo menos uma letra maiúscula (A-Z)")
        
        if re.search(self.patterns['lowercase'], password):
            complexity_score += 1
        else:
            issues.append("Senha deve conter pelo menos uma letra minúscula")
            suggestions.append("Adicione pelo menos uma letra minúscula (a-z)")
        
        if re.search(self.patterns['digit'], password):
            complexity_score += 1
        else:
            issues.append("Senha deve conter pelo menos um número")
            suggestions.append("Adicione pelo menos um número (0-9)")
        
        if re.search(self.patterns['special'], password):
            complexity_score += 1
        else:
            issues.append("Senha deve conter pelo menos um caractere especial")
            suggestions.append("Adicione pelo menos um caractere especial (!@#$%^&*)")
        
        # Pontos por complexidade
        score += complexity_score * 10
        
        # Verificar se contém informações pessoais
        if username and username.lower() in password.lower():
            issues.append("Senha não deve conter o nome de usuário")
            suggestions.append("Não use seu nome de usuário na senha")
        else:
            score += 5
        
        if email:
            email_local = email.split('@')[0].lower()
            if email_local in password.lower():
                issues.append("Senha não deve conter parte do email")
                suggestions.append("Não use parte do seu email na senha")
            else:
                score += 5
        
        # Verificar se foi comprometida (opcional)
        if self._check_pwned_password(password):
            issues.append("Esta senha foi comprometida em vazamentos de dados")
            suggestions.append("Escolha uma senha única que não foi usada em outros serviços")
        else:
            score += 10  # Pontos por não estar comprometida
        
        # Determinar força
        strength = self._determine_strength(score)
        
        # Senha é válida se não há issues críticos
        is_valid = len(issues) == 0 or all(
            issue not in [
                "Senha não pode estar vazia",
                "Senha deve ter pelo menos 8 caracteres",
                "Senha contém caracteres não permitidos"
            ] for issue in issues
        )
        
        return PasswordValidationResult(is_valid, score, strength, issues, suggestions)
    
    def _determine_strength(self, score: int) -> str:
        """Determina a força da senha baseada no score."""
        if score >= 80:
            return "very_strong"
        elif score >= 60:
            return "strong"
        elif score >= 40:
            return "medium"
        elif score >= 20:
            return "weak"
        else:
            return "very_weak"
    
    def _check_pwned_password(self, password: str) -> bool:
        """
        Verifica se a senha foi comprometida usando HaveIBeenPwned API.
        
        Args:
            password: Senha a ser verificada
            
        Returns:
            True se a senha foi comprometida, False caso contrário
        """
        try:
            # Hash SHA-1 da senha
            password_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
            prefix = password_hash[:5]
            suffix = password_hash[5:]
            
            # Fazer requisição para a API
            response = requests.get(f"{self.pwned_api_url}{prefix}", timeout=5)
            
            if response.status_code == 200:
                # Verificar se o suffix está na resposta
                return suffix in response.text
            else:
                logger.warning(f"Erro ao verificar senha comprometida: {response.status_code}")
                return False
                
        except Exception as e:
            logger.warning(f"Erro ao verificar senha comprometida: {e}")
            return False
    
    def generate_password_suggestions(self) -> List[str]:
        """Gera sugestões de senhas seguras."""
        return [
            "Use uma frase memorável com números e símbolos",
            "Combine palavras não relacionadas com números",
            "Use acrônimos de frases pessoais",
            "Substitua letras por números similares (a=4, e=3, i=1)",
            "Adicione símbolos no início, meio e fim",
            "Use pelo menos 12 caracteres para maior segurança",
            "Evite informações pessoais como datas de nascimento",
            "Não reutilize senhas de outros serviços"
        ]
    
    def validate_password_policy(self, password: str, policy: Dict) -> Tuple[bool, List[str]]:
        """
        Valida senha contra uma política específica.
        
        Args:
            password: Senha a ser validada
            policy: Dicionário com regras da política
            
        Returns:
            Tuple com (é_válida, lista_de_erros)
        """
        errors = []
        
        # Aplicar regras da política
        if 'min_length' in policy and len(password) < policy['min_length']:
            errors.append(f"Senha deve ter pelo menos {policy['min_length']} caracteres")
        
        if 'max_length' in policy and len(password) > policy['max_length']:
            errors.append(f"Senha deve ter no máximo {policy['max_length']} caracteres")
        
        if 'require_uppercase' in policy and policy['require_uppercase']:
            if not re.search(self.patterns['uppercase'], password):
                errors.append("Senha deve conter pelo menos uma letra maiúscula")
        
        if 'require_lowercase' in policy and policy['require_lowercase']:
            if not re.search(self.patterns['lowercase'], password):
                errors.append("Senha deve conter pelo menos uma letra minúscula")
        
        if 'require_digit' in policy and policy['require_digit']:
            if not re.search(self.patterns['digit'], password):
                errors.append("Senha deve conter pelo menos um número")
        
        if 'require_special' in policy and policy['require_special']:
            if not re.search(self.patterns['special'], password):
                errors.append("Senha deve conter pelo menos um caractere especial")
        
        if 'forbid_common' in policy and policy['forbid_common']:
            if password.lower() in self.common_passwords:
                errors.append("Senha muito comum, escolha uma senha mais única")
        
        return len(errors) == 0, errors


# Instância global do validador
password_validator = PasswordValidator()


def validate_password_strength(password: str, username: str = None, email: str = None) -> PasswordValidationResult:
    """
    Função de conveniência para validar força de senha.
    
    Args:
        password: Senha a ser validada
        username: Username do usuário (opcional)
        email: Email do usuário (opcional)
        
    Returns:
        PasswordValidationResult com resultado da validação
    """
    return password_validator.validate_password(password, username, email)


def is_password_strong_enough(password: str, min_score: int = 60) -> bool:
    """
    Verifica se a senha é forte o suficiente.
    
    Args:
        password: Senha a ser verificada
        min_score: Score mínimo aceitável (0-100)
        
    Returns:
        True se a senha é forte o suficiente, False caso contrário
    """
    result = password_validator.validate_password(password)
    return result.score >= min_score


def get_password_suggestions() -> List[str]:
    """
    Retorna sugestões de senhas seguras.
    
    Returns:
        Lista de sugestões
    """
    return password_validator.generate_password_suggestions() 