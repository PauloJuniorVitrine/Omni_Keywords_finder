"""
Healing Configuration - Configuração do Sistema de Auto-Cura

Tracing ID: HEALING_CONFIG_001_20250127
Versão: 1.0
Data: 2025-01-27
Objetivo: Configurações centralizadas para o sistema de self-healing

Este módulo contém todas as configurações necessárias para o sistema
de self-healing, incluindo timeouts, limites e estratégias.
"""

import os
import yaml
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class HealingConfig:
    """Configuração principal do sistema de healing"""
    
    # Configurações gerais
    enabled: bool = True
    debug_mode: bool = False
    log_level: str = "INFO"
    
    # Configurações de monitoramento
    check_interval: int = 30  # segundos
    max_workers: int = 10
    timeout: int = 10  # segundos
    
    # Configurações de recuperação
    max_recovery_attempts: int = 3
    max_strategy_attempts: int = 2
    strategy_cooldown: int = 60  # segundos
    recovery_timeout: int = 300  # segundos
    
    # Configurações de limpeza
    cleanup_interval: int = 3600  # segundos (1 hora)
    history_retention_hours: int = 24
    
    # Configurações de cache
    cache_enabled: bool = True
    health_cache_ttl: int = 30  # segundos
    metrics_cache_ttl: int = 15  # segundos
    
    # Configurações de alertas
    alerting_enabled: bool = True
    alert_threshold: float = 0.8  # 80% de falhas
    alert_cooldown: int = 300  # segundos
    
    # Configurações de métricas
    metrics_enabled: bool = True
    metrics_export_interval: int = 60  # segundos
    prometheus_enabled: bool = True
    
    # Configurações de serviços padrão
    default_services: List[Dict[str, Any]] = field(default_factory=list)
    
    # Configurações de estratégias
    strategies_config: Dict[str, Any] = field(default_factory=dict)
    
    # Configurações de notificações
    notifications: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Inicialização pós-criação"""
        if not self.default_services:
            self.default_services = self._get_default_services()
        
        if not self.strategies_config:
            self.strategies_config = self._get_default_strategies()
        
        if not self.notifications:
            self.notifications = self._get_default_notifications()
    
    def _get_default_services(self) -> List[Dict[str, Any]]:
        """Retorna lista de serviços padrão para monitoramento"""
        return [
            {
                "name": "execucao_service",
                "endpoint": "http://localhost:8000",
                "health_check_url": "http://localhost:8000/health/execucao",
                "check_interval": 30,
                "timeout": 10,
                "max_retries": 3,
                "type": "api"
            },
            {
                "name": "validation_service",
                "endpoint": "http://localhost:8000",
                "health_check_url": "http://localhost:8000/health/validation",
                "check_interval": 30,
                "timeout": 10,
                "max_retries": 3,
                "type": "api"
            },
            {
                "name": "onboarding_service",
                "endpoint": "http://localhost:8000",
                "health_check_url": "http://localhost:8000/health/onboarding",
                "check_interval": 30,
                "timeout": 10,
                "max_retries": 3,
                "type": "api"
            },
            {
                "name": "database_service",
                "endpoint": "localhost:5432",
                "health_check_url": None,
                "check_interval": 60,
                "timeout": 5,
                "max_retries": 3,
                "type": "database"
            },
            {
                "name": "redis_service",
                "endpoint": "localhost:6379",
                "health_check_url": None,
                "check_interval": 60,
                "timeout": 5,
                "max_retries": 3,
                "type": "cache"
            }
        ]
    
    def _get_default_strategies(self) -> Dict[str, Any]:
        """Retorna configurações padrão das estratégias"""
        return {
            "service_restart": {
                "enabled": True,
                "max_attempts": 3,
                "cooldown": 60,
                "timeout": 120,
                "grace_period": 30
            },
            "connection_recovery": {
                "enabled": True,
                "max_attempts": 5,
                "cooldown": 30,
                "timeout": 60,
                "retry_delay": 5
            },
            "resource_cleanup": {
                "enabled": True,
                "max_attempts": 2,
                "cooldown": 300,
                "cleanup_threshold": 0.9,  # 90% de uso
                "retention_days": 7
            },
            "configuration_reload": {
                "enabled": True,
                "max_attempts": 2,
                "cooldown": 300,
                "backup_enabled": True,
                "rollback_on_failure": True
            }
        }
    
    def _get_default_notifications(self) -> Dict[str, Any]:
        """Retorna configurações padrão de notificações"""
        return {
            "slack": {
                "enabled": False,
                "webhook_url": os.getenv("SLACK_WEBHOOK_URL", ""),
                "channel": "#alerts",
                "username": "Self-Healing Bot"
            },
            "email": {
                "enabled": False,
                "smtp_server": os.getenv("SMTP_SERVER", ""),
                "smtp_port": int(os.getenv("SMTP_PORT", "587")),
                "username": os.getenv("SMTP_USERNAME", ""),
                "password": os.getenv("SMTP_PASSWORD", ""),
                "from_email": os.getenv("FROM_EMAIL", ""),
                "to_emails": os.getenv("TO_EMAILS", "").split(",") if os.getenv("TO_EMAILS") else []
            },
            "webhook": {
                "enabled": False,
                "url": os.getenv("WEBHOOK_URL", ""),
                "timeout": 10,
                "retry_count": 3
            }
        }
    
    @classmethod
    def from_file(cls, config_path: str) -> 'HealingConfig':
        """
        Carrega configuração de um arquivo YAML
        
        Args:
            config_path: Caminho para o arquivo de configuração
            
        Returns:
            Instância de HealingConfig
        """
        try:
            if not os.path.exists(config_path):
                logger.warning(f"Arquivo de configuração não encontrado: {config_path}")
                return cls()
            
            with open(config_path, 'r', encoding='utf-8') as file:
                config_data = yaml.safe_load(file)
            
            return cls.from_dict(config_data)
        
        except Exception as e:
            logger.error(f"Erro ao carregar configuração de {config_path}: {e}")
            return cls()
    
    @classmethod
    def from_dict(cls, config_data: Dict[str, Any]) -> 'HealingConfig':
        """
        Cria configuração a partir de um dicionário
        
        Args:
            config_data: Dados de configuração
            
        Returns:
            Instância de HealingConfig
        """
        # Extrair configurações básicas
        config = cls(
            enabled=config_data.get('enabled', True),
            debug_mode=config_data.get('debug_mode', False),
            log_level=config_data.get('log_level', 'INFO'),
            check_interval=config_data.get('check_interval', 30),
            max_workers=config_data.get('max_workers', 10),
            timeout=config_data.get('timeout', 10),
            max_recovery_attempts=config_data.get('max_recovery_attempts', 3),
            max_strategy_attempts=config_data.get('max_strategy_attempts', 2),
            strategy_cooldown=config_data.get('strategy_cooldown', 60),
            recovery_timeout=config_data.get('recovery_timeout', 300),
            cleanup_interval=config_data.get('cleanup_interval', 3600),
            history_retention_hours=config_data.get('history_retention_hours', 24),
            cache_enabled=config_data.get('cache_enabled', True),
            health_cache_ttl=config_data.get('health_cache_ttl', 30),
            metrics_cache_ttl=config_data.get('metrics_cache_ttl', 15),
            alerting_enabled=config_data.get('alerting_enabled', True),
            alert_threshold=config_data.get('alert_threshold', 0.8),
            alert_cooldown=config_data.get('alert_cooldown', 300),
            metrics_enabled=config_data.get('metrics_enabled', True),
            metrics_export_interval=config_data.get('metrics_export_interval', 60),
            prometheus_enabled=config_data.get('prometheus_enabled', True)
        )
        
        # Configurar serviços
        if 'services' in config_data:
            config.default_services = config_data['services']
        
        # Configurar estratégias
        if 'strategies' in config_data:
            config.strategies_config = config_data['strategies']
        
        # Configurar notificações
        if 'notifications' in config_data:
            config.notifications = config_data['notifications']
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte configuração para dicionário
        
        Returns:
            Dicionário com configurações
        """
        return {
            'enabled': self.enabled,
            'debug_mode': self.debug_mode,
            'log_level': self.log_level,
            'check_interval': self.check_interval,
            'max_workers': self.max_workers,
            'timeout': self.timeout,
            'max_recovery_attempts': self.max_recovery_attempts,
            'max_strategy_attempts': self.max_strategy_attempts,
            'strategy_cooldown': self.strategy_cooldown,
            'recovery_timeout': self.recovery_timeout,
            'cleanup_interval': self.cleanup_interval,
            'history_retention_hours': self.history_retention_hours,
            'cache_enabled': self.cache_enabled,
            'health_cache_ttl': self.health_cache_ttl,
            'metrics_cache_ttl': self.metrics_cache_ttl,
            'alerting_enabled': self.alerting_enabled,
            'alert_threshold': self.alert_threshold,
            'alert_cooldown': self.alert_cooldown,
            'metrics_enabled': self.metrics_enabled,
            'metrics_export_interval': self.metrics_export_interval,
            'prometheus_enabled': self.prometheus_enabled,
            'services': self.default_services,
            'strategies': self.strategies_config,
            'notifications': self.notifications
        }
    
    def save_to_file(self, config_path: str) -> bool:
        """
        Salva configuração em arquivo YAML
        
        Args:
            config_path: Caminho para salvar o arquivo
            
        Returns:
            True se salvou com sucesso
        """
        try:
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as file:
                yaml.dump(self.to_dict(), file, default_flow_style=False, indent=2)
            
            logger.info(f"Configuração salva em: {config_path}")
            return True
        
        except Exception as e:
            logger.error(f"Erro ao salvar configuração em {config_path}: {e}")
            return False
    
    def get_service_config(self, service_name: str) -> Optional[Dict[str, Any]]:
        """
        Obtém configuração de um serviço específico
        
        Args:
            service_name: Nome do serviço
            
        Returns:
            Configuração do serviço ou None
        """
        for service in self.default_services:
            if service.get('name') == service_name:
                return service
        return None
    
    def get_strategy_config(self, strategy_name: str) -> Optional[Dict[str, Any]]:
        """
        Obtém configuração de uma estratégia específica
        
        Args:
            strategy_name: Nome da estratégia
            
        Returns:
            Configuração da estratégia ou None
        """
        return self.strategies_config.get(strategy_name)
    
    def is_strategy_enabled(self, strategy_name: str) -> bool:
        """
        Verifica se uma estratégia está habilitada
        
        Args:
            strategy_name: Nome da estratégia
            
        Returns:
            True se habilitada
        """
        strategy_config = self.get_strategy_config(strategy_name)
        return strategy_config and strategy_config.get('enabled', False)
    
    def validate(self) -> List[str]:
        """
        Valida a configuração
        
        Returns:
            Lista de erros encontrados
        """
        errors = []
        
        # Validar intervalos
        if self.check_interval < 5:
            errors.append("check_interval deve ser >= 5 segundos")
        
        if self.timeout < 1:
            errors.append("timeout deve ser >= 1 segundo")
        
        if self.max_recovery_attempts < 1:
            errors.append("max_recovery_attempts deve ser >= 1")
        
        if self.max_workers < 1:
            errors.append("max_workers deve ser >= 1")
        
        # Validar thresholds
        if not 0 <= self.alert_threshold <= 1:
            errors.append("alert_threshold deve estar entre 0 e 1")
        
        # Validar serviços
        for service in self.default_services:
            if not service.get('name'):
                errors.append("Serviço deve ter um nome")
            
            if service.get('check_interval', 0) < 5:
                errors.append(f"Serviço {service.get('name')} deve ter check_interval >= 5")
        
        return errors


def load_healing_config(config_path: Optional[str] = None) -> HealingConfig:
    """
    Carrega configuração do sistema de healing
    
    Args:
        config_path: Caminho opcional para o arquivo de configuração
        
    Returns:
        Configuração carregada
    """
    if not config_path:
        # Tentar encontrar arquivo de configuração padrão
        possible_paths = [
            "config/healing/healing_config.yaml",
            "infrastructure/healing/healing_config.yaml",
            "healing_config.yaml"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                config_path = path
                break
    
    if config_path and os.path.exists(config_path):
        config = HealingConfig.from_file(config_path)
        logger.info(f"Configuração carregada de: {config_path}")
    else:
        config = HealingConfig()
        logger.info("Usando configuração padrão")
    
    # Validar configuração
    errors = config.validate()
    if errors:
        logger.warning("Problemas encontrados na configuração:")
        for error in errors:
            logger.warning(f"  - {error}")
    
    return config


# Configuração padrão para uso imediato
DEFAULT_CONFIG = HealingConfig() 