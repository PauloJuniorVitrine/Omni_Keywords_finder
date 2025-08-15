"""
Retry Configuration
==================

Configurações centralizadas para estratégias de retry.
Define perfis específicos para diferentes tipos de operação.

Tracing ID: RETRY_CONFIG_001_20250127
Ruleset: enterprise_control_layer.yaml
Execução: 2025-01-27T10:00:00Z
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Type

from .retry_strategy import RetryConfig, RetryStrategy
from .exponential_backoff import ExponentialBackoffConfig


@dataclass
class RetryProfile:
    """Perfil de configuração para retry."""
    name: str
    max_attempts: int
    base_delay: float
    max_delay: float
    strategy: RetryStrategy
    jitter: bool
    jitter_factor: float
    retryable_exceptions: List[Type[Exception]]
    description: str


class RetryConfigurationManager:
    """Gerenciador de configurações de retry."""
    
    def __init__(self):
        self._profiles: Dict[str, RetryProfile] = {}
        self._load_default_profiles()
    
    def _load_default_profiles(self):
        """Carrega perfis padrão de retry."""
        
        # Perfil para APIs do Google
        self._profiles["google_api"] = RetryProfile(
            name="google_api",
            max_attempts=5,
            base_delay=2.0,
            max_delay=30.0,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            jitter=True,
            jitter_factor=0.15,
            retryable_exceptions=[
                ConnectionError, TimeoutError, OSError, Exception
            ],
            description="Configuração otimizada para APIs do Google com rate limiting"
        )
        
        # Perfil para APIs do YouTube
        self._profiles["youtube_api"] = RetryProfile(
            name="youtube_api",
            max_attempts=4,
            base_delay=1.0,
            max_delay=20.0,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            jitter=True,
            jitter_factor=0.1,
            retryable_exceptions=[
                ConnectionError, TimeoutError, OSError, Exception
            ],
            description="Configuração otimizada para APIs do YouTube"
        )
        
        # Perfil para APIs do Reddit
        self._profiles["reddit_api"] = RetryProfile(
            name="reddit_api",
            max_attempts=6,
            base_delay=3.0,
            max_delay=45.0,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            jitter=True,
            jitter_factor=0.2,
            retryable_exceptions=[
                ConnectionError, TimeoutError, OSError, Exception
            ],
            description="Configuração otimizada para APIs do Reddit com rate limiting agressivo"
        )
        
        # Perfil para operações de banco de dados
        self._profiles["database"] = RetryProfile(
            name="database",
            max_attempts=3,
            base_delay=1.0,
            max_delay=10.0,
            strategy=RetryStrategy.LINEAR_BACKOFF,
            jitter=False,
            jitter_factor=0.0,
            retryable_exceptions=[
                ConnectionError, TimeoutError
            ],
            description="Configuração para operações de banco de dados"
        )
        
        # Perfil para operações de arquivo
        self._profiles["file_operation"] = RetryProfile(
            name="file_operation",
            max_attempts=3,
            base_delay=0.5,
            max_delay=5.0,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            jitter=True,
            jitter_factor=0.1,
            retryable_exceptions=[
                OSError, IOError, PermissionError
            ],
            description="Configuração para operações de arquivo"
        )
        
        # Perfil para operações de rede
        self._profiles["network"] = RetryProfile(
            name="network",
            max_attempts=4,
            base_delay=1.0,
            max_delay=15.0,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            jitter=True,
            jitter_factor=0.1,
            retryable_exceptions=[
                ConnectionError, TimeoutError, OSError,
                ConnectionRefusedError, ConnectionResetError
            ],
            description="Configuração para operações de rede"
        )
        
        # Perfil para operações críticas
        self._profiles["critical"] = RetryProfile(
            name="critical",
            max_attempts=7,
            base_delay=1.0,
            max_delay=60.0,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            jitter=True,
            jitter_factor=0.15,
            retryable_exceptions=[Exception],
            description="Configuração para operações críticas com máximo de tentativas"
        )
        
        # Perfil para operações rápidas
        self._profiles["fast"] = RetryProfile(
            name="fast",
            max_attempts=2,
            base_delay=0.1,
            max_delay=1.0,
            strategy=RetryStrategy.LINEAR_BACKOFF,
            jitter=False,
            jitter_factor=0.0,
            retryable_exceptions=[
                ConnectionError, TimeoutError
            ],
            description="Configuração para operações rápidas com retry mínimo"
        )
    
    def get_profile(self, name: str) -> RetryProfile:
        """Obtém um perfil de retry por nome."""
        if name not in self._profiles:
            raise ValueError(f"Retry profile '{name}' not found")
        return self._profiles[name]
    
    def get_retry_config(self, profile_name: str) -> RetryConfig:
        """Obtém configuração de retry baseada em um perfil."""
        profile = self.get_profile(profile_name)
        return RetryConfig(
            max_attempts=profile.max_attempts,
            base_delay=profile.base_delay,
            max_delay=profile.max_delay,
            strategy=profile.strategy,
            jitter=profile.jitter,
            jitter_factor=profile.jitter_factor,
            retryable_exceptions=profile.retryable_exceptions
        )
    
    def get_exponential_backoff_config(self, profile_name: str) -> ExponentialBackoffConfig:
        """Obtém configuração de exponential backoff baseada em um perfil."""
        profile = self.get_profile(profile_name)
        return ExponentialBackoffConfig(
            base_delay=profile.base_delay,
            max_delay=profile.max_delay,
            exponential_base=2.0,
            max_attempts=profile.max_attempts,
            jitter=profile.jitter,
            jitter_factor=profile.jitter_factor
        )
    
    def list_profiles(self) -> List[str]:
        """Lista todos os perfis disponíveis."""
        return list(self._profiles.keys())
    
    def add_profile(self, profile: RetryProfile):
        """Adiciona um novo perfil de retry."""
        self._profiles[profile.name] = profile
    
    def update_profile(self, name: str, **kwargs):
        """Atualiza um perfil existente."""
        if name not in self._profiles:
            raise ValueError(f"Retry profile '{name}' not found")
        
        current_profile = self._profiles[name]
        for key, value in kwargs.items():
            if hasattr(current_profile, key):
                setattr(current_profile, key, value)
    
    def remove_profile(self, name: str):
        """Remove um perfil de retry."""
        if name not in self._profiles:
            raise ValueError(f"Retry profile '{name}' not found")
        del self._profiles[name]


# Instância global do gerenciador de configuração
retry_config_manager = RetryConfigurationManager()


# Configurações específicas para diferentes serviços
GOOGLE_KEYWORD_PLANNER_CONFIG = retry_config_manager.get_retry_config("google_api")
YOUTUBE_SEARCH_CONFIG = retry_config_manager.get_retry_config("youtube_api")
REDDIT_SEARCH_CONFIG = retry_config_manager.get_retry_config("reddit_api")
DATABASE_CONFIG = retry_config_manager.get_retry_config("database")
FILE_OPERATION_CONFIG = retry_config_manager.get_retry_config("file_operation")
NETWORK_CONFIG = retry_config_manager.get_retry_config("network")
CRITICAL_OPERATION_CONFIG = retry_config_manager.get_retry_config("critical")
FAST_OPERATION_CONFIG = retry_config_manager.get_retry_config("fast")


# Configurações de exponential backoff específicas
GOOGLE_KEYWORD_PLANNER_BACKOFF_CONFIG = retry_config_manager.get_exponential_backoff_config("google_api")
YOUTUBE_SEARCH_BACKOFF_CONFIG = retry_config_manager.get_exponential_backoff_config("youtube_api")
REDDIT_SEARCH_BACKOFF_CONFIG = retry_config_manager.get_exponential_backoff_config("reddit_api")
CRITICAL_OPERATION_BACKOFF_CONFIG = retry_config_manager.get_exponential_backoff_config("critical")


# Configurações baseadas em variáveis de ambiente
def get_environment_based_config(service_name: str) -> RetryConfig:
    """Obtém configuração baseada em variáveis de ambiente."""
    base_profile = retry_config_manager.get_profile(service_name)
    
    # Sobrescreve com variáveis de ambiente se disponíveis
    max_attempts = int(os.getenv(f"{service_name.upper()}_MAX_ATTEMPTS", base_profile.max_attempts))
    base_delay = float(os.getenv(f"{service_name.upper()}_BASE_DELAY", base_profile.base_delay))
    max_delay = float(os.getenv(f"{service_name.upper()}_MAX_DELAY", base_profile.max_delay))
    
    return RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        strategy=base_profile.strategy,
        jitter=base_profile.jitter,
        jitter_factor=base_profile.jitter_factor,
        retryable_exceptions=base_profile.retryable_exceptions
    )


# Configurações dinâmicas baseadas em ambiente
GOOGLE_API_CONFIG_ENV = get_environment_based_config("google_api")
YOUTUBE_API_CONFIG_ENV = get_environment_based_config("youtube_api")
REDDIT_API_CONFIG_ENV = get_environment_based_config("reddit_api")
DATABASE_CONFIG_ENV = get_environment_based_config("database") 