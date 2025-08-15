"""
Log Levels - Configurable Logging Levels by Environment

Prompt: CHECKLIST_RESOLUCAO_GARGALOS.md - Fase 3.3.2
Ruleset: enterprise_control_layer.yaml
Date: 2025-01-27
Tracing ID: CHECKLIST_RESOLUCAO_GARGALOS_20250127_001
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Union
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path
import yaml

class LogLevel(Enum):
    """Níveis de log padronizados"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogCategory(Enum):
    """Categorias de log para organização"""
    SYSTEM = "system"
    API = "api"
    DATABASE = "database"
    CACHE = "cache"
    SECURITY = "security"
    PERFORMANCE = "performance"
    BUSINESS = "business"
    EXTERNAL = "external"

@dataclass
class LogLevelConfig:
    """Configuração de nível de log para categoria"""
    category: LogCategory
    level: LogLevel
    enabled: bool = True
    include_traceback: bool = True
    include_extra: bool = True

@dataclass
class EnvironmentLogConfig:
    """Configuração de logs por ambiente"""
    environment: str
    default_level: LogLevel
    category_levels: Dict[LogCategory, LogLevelConfig]
    global_settings: Dict[str, Any]

class LogLevelManager:
    """Gerenciador de níveis de log configuráveis"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/logging.yaml"
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.configs: Dict[str, EnvironmentLogConfig] = {}
        self.current_config: Optional[EnvironmentLogConfig] = None
        self.loggers: Dict[str, logging.Logger] = {}
        
        self._load_configs()
        self._apply_environment_config()
    
    def _load_configs(self) -> None:
        """Carrega configurações de log"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                    self._parse_configs(config_data)
            else:
                # Configuração padrão se arquivo não existir
                self._create_default_configs()
        except Exception as e:
            print(f"Erro ao carregar configuração de logs: {e}")
            self._create_default_configs()
    
    def _parse_configs(self, config_data: Dict[str, Any]) -> None:
        """Parse das configurações do arquivo"""
        for env_name, env_config in config_data.get('environments', {}).items():
            category_levels = {}
            
            # Parse configurações por categoria
            for cat_name, cat_config in env_config.get('categories', {}).items():
                try:
                    category = LogCategory(cat_name)
                    level = LogLevel(cat_config.get('level', 'INFO'))
                    enabled = cat_config.get('enabled', True)
                    include_traceback = cat_config.get('include_traceback', True)
                    include_extra = cat_config.get('include_extra', True)
                    
                    category_levels[category] = LogLevelConfig(
                        category=category,
                        level=level,
                        enabled=enabled,
                        include_traceback=include_traceback,
                        include_extra=include_extra
                    )
                except ValueError as e:
                    print(f"Erro ao parse categoria {cat_name}: {e}")
            
            # Cria configuração do ambiente
            default_level = LogLevel(env_config.get('default_level', 'INFO'))
            global_settings = env_config.get('global_settings', {})
            
            self.configs[env_name] = EnvironmentLogConfig(
                environment=env_name,
                default_level=default_level,
                category_levels=category_levels,
                global_settings=global_settings
            )
    
    def _create_default_configs(self) -> None:
        """Cria configurações padrão"""
        default_configs = {
            'development': {
                'default_level': 'DEBUG',
                'categories': {
                    'system': {'level': 'DEBUG', 'enabled': True},
                    'api': {'level': 'INFO', 'enabled': True},
                    'database': {'level': 'DEBUG', 'enabled': True},
                    'cache': {'level': 'INFO', 'enabled': True},
                    'security': {'level': 'WARNING', 'enabled': True},
                    'performance': {'level': 'INFO', 'enabled': True},
                    'business': {'level': 'INFO', 'enabled': True},
                    'external': {'level': 'WARNING', 'enabled': True}
                },
                'global_settings': {
                    'include_traceback': True,
                    'include_extra': True,
                    'log_to_file': False,
                    'log_to_console': True
                }
            },
            'production': {
                'default_level': 'INFO',
                'categories': {
                    'system': {'level': 'WARNING', 'enabled': True},
                    'api': {'level': 'INFO', 'enabled': True},
                    'database': {'level': 'WARNING', 'enabled': True},
                    'cache': {'level': 'INFO', 'enabled': True},
                    'security': {'level': 'ERROR', 'enabled': True},
                    'performance': {'level': 'INFO', 'enabled': True},
                    'business': {'level': 'INFO', 'enabled': True},
                    'external': {'level': 'ERROR', 'enabled': True}
                },
                'global_settings': {
                    'include_traceback': True,
                    'include_extra': False,
                    'log_to_file': True,
                    'log_to_console': False
                }
            },
            'testing': {
                'default_level': 'WARNING',
                'categories': {
                    'system': {'level': 'ERROR', 'enabled': True},
                    'api': {'level': 'WARNING', 'enabled': True},
                    'database': {'level': 'ERROR', 'enabled': True},
                    'cache': {'level': 'WARNING', 'enabled': True},
                    'security': {'level': 'ERROR', 'enabled': True},
                    'performance': {'level': 'WARNING', 'enabled': True},
                    'business': {'level': 'WARNING', 'enabled': True},
                    'external': {'level': 'ERROR', 'enabled': True}
                },
                'global_settings': {
                    'include_traceback': False,
                    'include_extra': False,
                    'log_to_file': False,
                    'log_to_console': False
                }
            }
        }
        
        for env_name, env_config in default_configs.items():
            category_levels = {}
            
            for cat_name, cat_config in env_config['categories'].items():
                category = LogCategory(cat_name)
                level = LogLevel(cat_config['level'])
                enabled = cat_config['enabled']
                
                category_levels[category] = LogLevelConfig(
                    category=category,
                    level=level,
                    enabled=enabled,
                    include_traceback=env_config['global_settings']['include_traceback'],
                    include_extra=env_config['global_settings']['include_extra']
                )
            
            self.configs[env_name] = EnvironmentLogConfig(
                environment=env_name,
                default_level=LogLevel(env_config['default_level']),
                category_levels=category_levels,
                global_settings=env_config['global_settings']
            )
    
    def _apply_environment_config(self) -> None:
        """Aplica configuração do ambiente atual"""
        if self.environment not in self.configs:
            print(f"Configuração para ambiente '{self.environment}' não encontrada. Usando 'development'.")
            self.environment = 'development'
        
        self.current_config = self.configs[self.environment]
        self._configure_loggers()
    
    def _configure_loggers(self) -> None:
        """Configura loggers baseado na configuração atual"""
        if not self.current_config:
            return
        
        # Configura logging root
        logging.basicConfig(
            level=getattr(logging, self.current_config.default_level.value),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Configura loggers por categoria
        for category, config in self.current_config.category_levels.items():
            if config.enabled:
                logger_name = f"omni_keywords_finder.{category.value}"
                logger = logging.getLogger(logger_name)
                logger.setLevel(getattr(logging, config.level.value))
                
                # Remove handlers existentes
                logger.handlers.clear()
                
                # Adiciona handler baseado na configuração global
                if self.current_config.global_settings.get('log_to_console', True):
                    console_handler = logging.StreamHandler()
                    console_handler.setLevel(getattr(logging, config.level.value))
                    logger.addHandler(console_handler)
                
                if self.current_config.global_settings.get('log_to_file', False):
                    log_file = f"logs/{category.value}.log"
                    Path("logs").mkdir(exist_ok=True)
                    file_handler = logging.FileHandler(log_file)
                    file_handler.setLevel(getattr(logging, config.level.value))
                    logger.addHandler(file_handler)
                
                self.loggers[logger_name] = logger
    
    def get_logger(self, category: LogCategory) -> logging.Logger:
        """Obtém logger para categoria específica"""
        logger_name = f"omni_keywords_finder.{category.value}"
        
        if logger_name not in self.loggers:
            # Cria logger se não existir
            logger = logging.getLogger(logger_name)
            
            # Aplica configuração da categoria
            if category in self.current_config.category_levels:
                config = self.current_config.category_levels[category]
                logger.setLevel(getattr(logging, config.level.value))
            else:
                logger.setLevel(getattr(logging, self.current_config.default_level.value))
            
            self.loggers[logger_name] = logger
        
        return self.loggers[logger_name]
    
    def set_level(self, category: LogCategory, level: LogLevel) -> None:
        """Define nível de log para categoria específica"""
        if not self.current_config:
            return
        
        # Atualiza configuração
        if category in self.current_config.category_levels:
            self.current_config.category_levels[category].level = level
        else:
            self.current_config.category_levels[category] = LogLevelConfig(
                category=category,
                level=level
            )
        
        # Atualiza logger
        logger = self.get_logger(category)
        logger.setLevel(getattr(logging, level.value))
    
    def enable_category(self, category: LogCategory) -> None:
        """Habilita logging para categoria"""
        if not self.current_config:
            return
        
        if category in self.current_config.category_levels:
            self.current_config.category_levels[category].enabled = True
        else:
            self.current_config.category_levels[category] = LogLevelConfig(
                category=category,
                level=self.current_config.default_level
            )
    
    def disable_category(self, category: LogCategory) -> None:
        """Desabilita logging para categoria"""
        if not self.current_config:
            return
        
        if category in self.current_config.category_levels:
            self.current_config.category_levels[category].enabled = False
            
            # Remove logger se existir
            logger_name = f"omni_keywords_finder.{category.value}"
            if logger_name in self.loggers:
                del self.loggers[logger_name]
    
    def get_current_config(self) -> Dict[str, Any]:
        """Retorna configuração atual em formato dicionário"""
        if not self.current_config:
            return {}
        
        return {
            'environment': self.current_config.environment,
            'default_level': self.current_config.default_level.value,
            'categories': {
                cat.value: {
                    'level': config.level.value,
                    'enabled': config.enabled,
                    'include_traceback': config.include_traceback,
                    'include_extra': config.include_extra
                }
                for cat, config in self.current_config.category_levels.items()
            },
            'global_settings': self.current_config.global_settings
        }
    
    def reload_config(self) -> None:
        """Recarrega configurações"""
        self._load_configs()
        self._apply_environment_config()
    
    def save_config(self) -> None:
        """Salva configuração atual em arquivo"""
        if not self.current_config:
            return
        
        config_data = {
            'environments': {
                self.current_config.environment: {
                    'default_level': self.current_config.default_level.value,
                    'categories': {
                        cat.value: {
                            'level': config.level.value,
                            'enabled': config.enabled,
                            'include_traceback': config.include_traceback,
                            'include_extra': config.include_extra
                        }
                        for cat, config in self.current_config.category_levels.items()
                    },
                    'global_settings': self.current_config.global_settings
                }
            }
        }
        
        # Garante que o diretório existe
        config_dir = Path(self.config_path).parent
        config_dir.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2)

# Instância global do gerenciador
log_level_manager = LogLevelManager()

def get_logger(category: LogCategory) -> logging.Logger:
    """Função conveniente para obter logger"""
    return log_level_manager.get_logger(category)

def set_log_level(category: LogCategory, level: LogLevel) -> None:
    """Função conveniente para definir nível de log"""
    log_level_manager.set_level(category, level)

def enable_log_category(category: LogCategory) -> None:
    """Função conveniente para habilitar categoria"""
    log_level_manager.enable_category(category)

def disable_log_category(category: LogCategory) -> None:
    """Função conveniente para desabilitar categoria"""
    log_level_manager.disable_category(category)

def get_log_config() -> Dict[str, Any]:
    """Função conveniente para obter configuração atual"""
    return log_level_manager.get_current_config()

# Decorator para logging automático com nível configurável
def log_with_level(category: LogCategory, level: LogLevel = LogLevel.INFO):
    """Decorator para logging automático com nível configurável"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger(category)
            
            # Verifica se o nível está habilitado
            if logger.isEnabledFor(getattr(logging, level.value)):
                logger.log(
                    getattr(logging, level.value),
                    f"Function {func.__name__} called with args: {args}, kwargs: {kwargs}"
                )
            
            try:
                result = func(*args, **kwargs)
                
                if logger.isEnabledFor(getattr(logging, level.value)):
                    logger.log(
                        getattr(logging, level.value),
                        f"Function {func.__name__} completed successfully"
                    )
                
                return result
            except Exception as e:
                if logger.isEnabledFor(logging.ERROR):
                    logger.error(f"Function {func.__name__} failed: {e}")
                raise
        
        return wrapper
    return decorator

# Exemplo de uso
"""
# Configuração básica
logger = get_logger(LogCategory.API)
logger.info("API request received")

# Mudança de nível dinâmica
set_log_level(LogCategory.DATABASE, LogLevel.DEBUG)

# Habilitação/desabilitação de categorias
enable_log_category(LogCategory.PERFORMANCE)
disable_log_category(LogCategory.SECURITY)

# Decorator com nível configurável
@log_with_level(LogCategory.BUSINESS, LogLevel.INFO)
def process_user_data(user_id: str):
    # ... lógica da função ...
    pass

# Obtenção da configuração atual
config = get_log_config()
print(json.dumps(config, indent=2))
"""

# Configurações predefinidas por ambiente
ENVIRONMENT_CONFIGS = {
    'development': {
        'default_level': 'DEBUG',
        'verbose_logging': True,
        'log_to_console': True,
        'log_to_file': False
    },
    'staging': {
        'default_level': 'INFO',
        'verbose_logging': False,
        'log_to_console': True,
        'log_to_file': True
    },
    'production': {
        'default_level': 'WARNING',
        'verbose_logging': False,
        'log_to_console': False,
        'log_to_file': True
    }
} 