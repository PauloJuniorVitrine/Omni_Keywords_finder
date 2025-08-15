"""
Configuração Avançada de Database - Omni Keywords Finder

Tracing ID: IMP002_DATABASE_CONFIG_001
Data: 2025-01-27
Versão: 1.0
Status: Em Implementação

Implementa configurações otimizadas para database:
- Connection pooling
- Query optimization
- Performance tuning
- Backup configuration
- Monitoring settings
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class DatabaseType(Enum):
    """Tipos de database suportados"""
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"


@dataclass
class ConnectionPoolConfig:
    """Configuração do connection pool"""
    max_connections: int = 20
    min_connections: int = 5
    connection_timeout: int = 30
    health_check_interval: int = 300
    max_lifetime: int = 3600
    idle_timeout: int = 600


@dataclass
class QueryCacheConfig:
    """Configuração do cache de queries"""
    max_size: int = 1000
    ttl: int = 3600
    enable_select_cache: bool = True
    enable_explain_cache: bool = True
    cache_invalidation_strategy: str = "lru"


@dataclass
class BackupConfig:
    """Configuração de backup"""
    enabled: bool = True
    backup_dir: str = "backups"
    retention_days: int = 30
    backup_interval_hours: int = 24
    compression_enabled: bool = True
    encryption_enabled: bool = False


@dataclass
class PerformanceConfig:
    """Configuração de performance"""
    slow_query_threshold: float = 1.0
    enable_query_logging: bool = True
    enable_explain_analysis: bool = True
    auto_index_creation: bool = True
    index_recommendation_threshold: int = 8


@dataclass
class MonitoringConfig:
    """Configuração de monitoramento"""
    enabled: bool = True
    metrics_interval: int = 60
    alert_thresholds: Dict[str, float] = None
    enable_real_time_monitoring: bool = True
    log_performance_metrics: bool = True


class DatabaseConfig:
    """Configuração principal de database"""
    
    def __init__(self):
        self.db_type = DatabaseType.SQLITE
        self.connection_pool = ConnectionPoolConfig()
        self.query_cache = QueryCacheConfig()
        self.backup = BackupConfig()
        self.performance = PerformanceConfig()
        self.monitoring = MonitoringConfig()
        
        # Carrega configurações do ambiente
        self._load_environment_config()
    
    def _load_environment_config(self):
        """Carrega configurações do ambiente"""
        # Database type
        db_type_str = os.getenv('DATABASE_TYPE', 'sqlite').lower()
        if db_type_str == 'postgresql':
            self.db_type = DatabaseType.POSTGRESQL
        elif db_type_str == 'mysql':
            self.db_type = DatabaseType.MYSQL
        else:
            self.db_type = DatabaseType.SQLITE
        
        # Connection pool
        self.connection_pool.max_connections = int(os.getenv('DB_MAX_CONNECTIONS', 20))
        self.connection_pool.min_connections = int(os.getenv('DB_MIN_CONNECTIONS', 5))
        self.connection_pool.connection_timeout = int(os.getenv('DB_CONNECTION_TIMEOUT', 30))
        self.connection_pool.health_check_interval = int(os.getenv('DB_HEALTH_CHECK_INTERVAL', 300))
        
        # Query cache
        self.query_cache.max_size = int(os.getenv('DB_CACHE_MAX_SIZE', 1000))
        self.query_cache.ttl = int(os.getenv('DB_CACHE_TTL', 3600))
        self.query_cache.enable_select_cache = os.getenv('DB_ENABLE_SELECT_CACHE', 'true').lower() == 'true'
        
        # Backup
        self.backup.enabled = os.getenv('DB_BACKUP_ENABLED', 'true').lower() == 'true'
        self.backup.backup_dir = os.getenv('DB_BACKUP_DIR', 'backups')
        self.backup.retention_days = int(os.getenv('DB_BACKUP_RETENTION_DAYS', 30))
        self.backup.backup_interval_hours = int(os.getenv('DB_BACKUP_INTERVAL_HOURS', 24))
        
        # Performance
        self.performance.slow_query_threshold = float(os.getenv('DB_SLOW_QUERY_THRESHOLD', 1.0))
        self.performance.enable_query_logging = os.getenv('DB_ENABLE_QUERY_LOGGING', 'true').lower() == 'true'
        self.performance.auto_index_creation = os.getenv('DB_AUTO_INDEX_CREATION', 'true').lower() == 'true'
        
        # Monitoring
        self.monitoring.enabled = os.getenv('DB_MONITORING_ENABLED', 'true').lower() == 'true'
        self.monitoring.metrics_interval = int(os.getenv('DB_METRICS_INTERVAL', 60))
        self.monitoring.enable_real_time_monitoring = os.getenv('DB_REAL_TIME_MONITORING', 'true').lower() == 'true'
        
        # Alert thresholds
        self.monitoring.alert_thresholds = {
            'slow_query_threshold': float(os.getenv('DB_ALERT_SLOW_QUERY', 2.0)),
            'cache_hit_ratio_threshold': float(os.getenv('DB_ALERT_CACHE_HIT_RATIO', 0.5)),
            'pool_hit_ratio_threshold': float(os.getenv('DB_ALERT_POOL_HIT_RATIO', 0.8)),
            'connection_error_threshold': int(os.getenv('DB_ALERT_CONNECTION_ERRORS', 10))
        }
    
    def get_sqlite_config(self) -> Dict[str, Any]:
        """Retorna configurações específicas para SQLite"""
        return {
            'journal_mode': 'WAL',
            'synchronous': 'NORMAL',
            'cache_size': 10000,
            'temp_store': 'MEMORY',
            'mmap_size': 268435456,  # 256MB
            'foreign_keys': 'ON',
            'checkpoint_timeout': 300000,  # 5 minutos
            'wal_autocheckpoint': 1000,
            'busy_timeout': 30000,  # 30 segundos
        }
    
    def get_postgresql_config(self) -> Dict[str, Any]:
        """Retorna configurações específicas para PostgreSQL"""
        return {
            'pool_size': self.connection_pool.max_connections,
            'max_overflow': self.connection_pool.max_connections * 2,
            'pool_timeout': self.connection_pool.connection_timeout,
            'pool_recycle': self.connection_pool.max_lifetime,
            'pool_pre_ping': True,
            'echo': False,
            'echo_pool': False,
        }
    
    def get_mysql_config(self) -> Dict[str, Any]:
        """Retorna configurações específicas para MySQL"""
        return {
            'pool_size': self.connection_pool.max_connections,
            'max_overflow': self.connection_pool.max_connections * 2,
            'pool_timeout': self.connection_pool.connection_timeout,
            'pool_recycle': self.connection_pool.max_lifetime,
            'pool_pre_ping': True,
            'echo': False,
            'echo_pool': False,
        }
    
    def get_optimization_config(self) -> Dict[str, Any]:
        """Retorna configurações de otimização"""
        return {
            'connection_pool': {
                'max_connections': self.connection_pool.max_connections,
                'min_connections': self.connection_pool.min_connections,
                'connection_timeout': self.connection_pool.connection_timeout,
                'health_check_interval': self.connection_pool.health_check_interval,
                'max_lifetime': self.connection_pool.max_lifetime,
                'idle_timeout': self.connection_pool.idle_timeout,
            },
            'query_cache': {
                'max_size': self.query_cache.max_size,
                'ttl': self.query_cache.ttl,
                'enable_select_cache': self.query_cache.enable_select_cache,
                'enable_explain_cache': self.query_cache.enable_explain_cache,
                'cache_invalidation_strategy': self.query_cache.cache_invalidation_strategy,
            },
            'backup': {
                'enabled': self.backup.enabled,
                'backup_dir': self.backup.backup_dir,
                'retention_days': self.backup.retention_days,
                'backup_interval_hours': self.backup.backup_interval_hours,
                'compression_enabled': self.backup.compression_enabled,
                'encryption_enabled': self.backup.encryption_enabled,
            },
            'performance': {
                'slow_query_threshold': self.performance.slow_query_threshold,
                'enable_query_logging': self.performance.enable_query_logging,
                'enable_explain_analysis': self.performance.enable_explain_analysis,
                'auto_index_creation': self.performance.auto_index_creation,
                'index_recommendation_threshold': self.performance.index_recommendation_threshold,
            },
            'monitoring': {
                'enabled': self.monitoring.enabled,
                'metrics_interval': self.monitoring.metrics_interval,
                'alert_thresholds': self.monitoring.alert_thresholds,
                'enable_real_time_monitoring': self.monitoring.enable_real_time_monitoring,
                'log_performance_metrics': self.monitoring.log_performance_metrics,
            }
        }
    
    def validate_config(self) -> bool:
        """Valida configurações"""
        errors = []
        
        # Valida connection pool
        if self.connection_pool.max_connections < self.connection_pool.min_connections:
            errors.append("max_connections deve ser maior que min_connections")
        
        if self.connection_pool.max_connections > 100:
            errors.append("max_connections não deve exceder 100")
        
        # Valida query cache
        if self.query_cache.max_size < 1:
            errors.append("cache max_size deve ser maior que 0")
        
        if self.query_cache.ttl < 60:
            errors.append("cache TTL deve ser pelo menos 60 segundos")
        
        # Valida backup
        if self.backup.retention_days < 1:
            errors.append("backup retention_days deve ser pelo menos 1")
        
        if self.backup.backup_interval_hours < 1:
            errors.append("backup interval deve ser pelo menos 1 hora")
        
        # Valida performance
        if self.performance.slow_query_threshold < 0.1:
            errors.append("slow_query_threshold deve ser pelo menos 0.1 segundos")
        
        # Valida monitoring
        if self.monitoring.metrics_interval < 10:
            errors.append("metrics_interval deve ser pelo menos 10 segundos")
        
        if errors:
            raise ValueError(f"Configuração inválida: {'; '.join(errors)}")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte configuração para dicionário"""
        return {
            'db_type': self.db_type.value,
            'connection_pool': {
                'max_connections': self.connection_pool.max_connections,
                'min_connections': self.connection_pool.min_connections,
                'connection_timeout': self.connection_pool.connection_timeout,
                'health_check_interval': self.connection_pool.health_check_interval,
                'max_lifetime': self.connection_pool.max_lifetime,
                'idle_timeout': self.connection_pool.idle_timeout,
            },
            'query_cache': {
                'max_size': self.query_cache.max_size,
                'ttl': self.query_cache.ttl,
                'enable_select_cache': self.query_cache.enable_select_cache,
                'enable_explain_cache': self.query_cache.enable_explain_cache,
                'cache_invalidation_strategy': self.query_cache.cache_invalidation_strategy,
            },
            'backup': {
                'enabled': self.backup.enabled,
                'backup_dir': self.backup.backup_dir,
                'retention_days': self.backup.retention_days,
                'backup_interval_hours': self.backup.backup_interval_hours,
                'compression_enabled': self.backup.compression_enabled,
                'encryption_enabled': self.backup.encryption_enabled,
            },
            'performance': {
                'slow_query_threshold': self.performance.slow_query_threshold,
                'enable_query_logging': self.performance.enable_query_logging,
                'enable_explain_analysis': self.performance.enable_explain_analysis,
                'auto_index_creation': self.performance.auto_index_creation,
                'index_recommendation_threshold': self.performance.index_recommendation_threshold,
            },
            'monitoring': {
                'enabled': self.monitoring.enabled,
                'metrics_interval': self.monitoring.metrics_interval,
                'alert_thresholds': self.monitoring.alert_thresholds,
                'enable_real_time_monitoring': self.monitoring.enable_real_time_monitoring,
                'log_performance_metrics': self.monitoring.log_performance_metrics,
            }
        }


# Instância global da configuração
db_config = DatabaseConfig()


def get_database_config() -> DatabaseConfig:
    """Retorna instância da configuração de database"""
    return db_config


def get_optimization_config() -> Dict[str, Any]:
    """Retorna configurações de otimização"""
    return db_config.get_optimization_config()


def validate_database_config() -> bool:
    """Valida configuração de database"""
    return db_config.validate_config()


# Configurações específicas por ambiente
def get_development_config() -> DatabaseConfig:
    """Configuração para desenvolvimento"""
    config = DatabaseConfig()
    config.connection_pool.max_connections = 10
    config.connection_pool.min_connections = 2
    config.query_cache.max_size = 500
    config.query_cache.ttl = 1800  # 30 minutos
    config.backup.enabled = False
    config.monitoring.enabled = False
    config.performance.slow_query_threshold = 0.5
    return config


def get_production_config() -> DatabaseConfig:
    """Configuração para produção"""
    config = DatabaseConfig()
    config.connection_pool.max_connections = 50
    config.connection_pool.min_connections = 10
    config.query_cache.max_size = 2000
    config.query_cache.ttl = 7200  # 2 horas
    config.backup.enabled = True
    config.backup.retention_days = 90
    config.monitoring.enabled = True
    config.performance.slow_query_threshold = 2.0
    return config


def get_staging_config() -> DatabaseConfig:
    """Configuração para staging"""
    config = DatabaseConfig()
    config.connection_pool.max_connections = 20
    config.connection_pool.min_connections = 5
    config.query_cache.max_size = 1000
    config.query_cache.ttl = 3600  # 1 hora
    config.backup.enabled = True
    config.backup.retention_days = 7
    config.monitoring.enabled = True
    config.performance.slow_query_threshold = 1.0
    return config


# Função para obter configuração baseada no ambiente
def get_environment_config() -> DatabaseConfig:
    """Retorna configuração baseada no ambiente"""
    env = os.getenv('FLASK_ENV', 'development').lower()
    
    if env == 'production':
        return get_production_config()
    elif env == 'staging':
        return get_staging_config()
    else:
        return get_development_config() 