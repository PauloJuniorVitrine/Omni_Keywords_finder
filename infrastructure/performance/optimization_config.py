#!/usr/bin/env python3
"""
🎯 Configuração de Otimização de Performance - IMP-016
======================================================

Tracing ID: OPTIMIZATION_CONFIG_IMP016_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Arquivo de configuração centralizado para:
- Configurações de performance
- Parâmetros de otimização
- Thresholds e limites
- Configurações de cache
- Configurações de queries

Prompt: CHECKLIST_CONFIABILIDADE.md - IMP-016
Ruleset: enterprise_control_layer.yaml
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class Environment(Enum):
    """Ambientes disponíveis."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


@dataclass
class PerformanceThresholds:
    """Thresholds de performance."""
    # Response time thresholds
    response_time_warning: float = 1.0  # segundos
    response_time_critical: float = 3.0  # segundos
    
    # Memory thresholds
    memory_warning: float = 0.7  # 70%
    memory_critical: float = 0.9  # 90%
    
    # CPU thresholds
    cpu_warning: float = 0.6  # 60%
    cpu_critical: float = 0.8  # 80%
    
    # Cache thresholds
    cache_hit_rate_warning: float = 0.7  # 70%
    cache_hit_rate_critical: float = 0.5  # 50%
    
    # Query thresholds
    query_time_warning: float = 0.5  # segundos
    query_time_critical: float = 2.0  # segundos
    
    # Error rate thresholds
    error_rate_warning: float = 0.05  # 5%
    error_rate_critical: float = 0.1  # 10%


@dataclass
class CacheConfig:
    """Configuração de cache."""
    # Estratégias
    default_strategy: str = "adaptive"
    enable_layered_cache: bool = True
    enable_compression: bool = True
    
    # Tamanhos
    l1_max_size: int = 1000
    l2_max_size: int = 10000
    l3_max_size: int = 100000
    
    # TTLs
    l1_ttl: int = 300  # 5 minutos
    l2_ttl: int = 3600  # 1 hora
    l3_ttl: int = 86400  # 24 horas
    
    # Otimizações
    enable_preloading: bool = True
    enable_pattern_analysis: bool = True
    compression_threshold: int = 1024  # bytes
    adaptive_learning_rate: float = 0.1


@dataclass
class QueryConfig:
    """Configuração de queries."""
    # Thresholds
    slow_query_threshold: float = 1.0  # segundos
    max_query_history: int = 10000
    
    # Otimizações
    enable_auto_optimization: bool = True
    enable_index_suggestions: bool = True
    enable_query_rewriting: bool = True
    max_suggestions_per_query: int = 5
    
    # Análise
    complexity_threshold: float = 0.7
    analysis_interval: int = 300  # 5 minutos
    
    # Limites
    max_query_length: int = 10000  # caracteres
    max_tables_per_query: int = 10
    max_joins_per_query: int = 5


@dataclass
class MonitoringConfig:
    """Configuração de monitoramento."""
    # Intervals
    metrics_collection_interval: int = 60  # segundos
    optimization_interval: int = 300  # 5 minutos
    report_generation_interval: int = 3600  # 1 hora
    
    # Storage
    max_metrics_history: int = 10000
    max_optimization_history: int = 1000
    
    # Alerts
    enable_alerts: bool = True
    alert_cooldown: int = 300  # 5 minutos
    
    # Logging
    enable_detailed_logging: bool = True
    log_level: str = "INFO"


@dataclass
class OptimizationConfig:
    """Configuração principal de otimização."""
    # Ambiente
    environment: Environment = Environment.DEVELOPMENT
    
    # Thresholds
    thresholds: PerformanceThresholds = field(default_factory=PerformanceThresholds)
    
    # Configurações específicas
    cache: CacheConfig = field(default_factory=CacheConfig)
    query: QueryConfig = field(default_factory=QueryConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # Funcionalidades
    enable_auto_optimization: bool = True
    enable_performance_monitoring: bool = True
    enable_cache_optimization: bool = True
    enable_query_optimization: bool = True
    enable_memory_optimization: bool = True
    
    # Segurança
    max_optimization_duration: int = 30  # segundos
    enable_rollback: bool = True
    optimization_timeout: int = 60  # segundos


class OptimizationConfigManager:
    """
    Gerenciador de configurações de otimização.
    
    Responsável por:
    - Carregar configurações de arquivos
    - Gerenciar configurações por ambiente
    - Validar configurações
    - Fornecer configurações padrão
    """
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> OptimizationConfig:
        """Carrega configuração do arquivo ou usa padrão."""
        if self.config_file and os.path.exists(self.config_file):
            return self._load_from_file()
        else:
            return self._get_default_config()
    
    def _load_from_file(self) -> OptimizationConfig:
        """Carrega configuração de arquivo."""
        try:
            import yaml
            
            with open(self.config_file, 'r') as f:
                config_data = yaml.safe_load(f)
            
            return self._parse_config_data(config_data)
            
        except Exception as e:
            print(f"Erro ao carregar configuração: {e}")
            return self._get_default_config()
    
    def _parse_config_data(self, data: Dict[str, Any]) -> OptimizationConfig:
        """Converte dados do arquivo em configuração."""
        try:
            # Ambiente
            environment = Environment(data.get('environment', 'development'))
            
            # Thresholds
            thresholds_data = data.get('thresholds', {})
            thresholds = PerformanceThresholds(
                response_time_warning=thresholds_data.get('response_time_warning', 1.0),
                response_time_critical=thresholds_data.get('response_time_critical', 3.0),
                memory_warning=thresholds_data.get('memory_warning', 0.7),
                memory_critical=thresholds_data.get('memory_critical', 0.9),
                cpu_warning=thresholds_data.get('cpu_warning', 0.6),
                cpu_critical=thresholds_data.get('cpu_critical', 0.8),
                cache_hit_rate_warning=thresholds_data.get('cache_hit_rate_warning', 0.7),
                cache_hit_rate_critical=thresholds_data.get('cache_hit_rate_critical', 0.5),
                query_time_warning=thresholds_data.get('query_time_warning', 0.5),
                query_time_critical=thresholds_data.get('query_time_critical', 2.0),
                error_rate_warning=thresholds_data.get('error_rate_warning', 0.05),
                error_rate_critical=thresholds_data.get('error_rate_critical', 0.1)
            )
            
            # Cache
            cache_data = data.get('cache', {})
            cache = CacheConfig(
                default_strategy=cache_data.get('default_strategy', 'adaptive'),
                enable_layered_cache=cache_data.get('enable_layered_cache', True),
                enable_compression=cache_data.get('enable_compression', True),
                l1_max_size=cache_data.get('l1_max_size', 1000),
                l2_max_size=cache_data.get('l2_max_size', 10000),
                l3_max_size=cache_data.get('l3_max_size', 100000),
                l1_ttl=cache_data.get('l1_ttl', 300),
                l2_ttl=cache_data.get('l2_ttl', 3600),
                l3_ttl=cache_data.get('l3_ttl', 86400),
                enable_preloading=cache_data.get('enable_preloading', True),
                enable_pattern_analysis=cache_data.get('enable_pattern_analysis', True),
                compression_threshold=cache_data.get('compression_threshold', 1024),
                adaptive_learning_rate=cache_data.get('adaptive_learning_rate', 0.1)
            )
            
            # Query
            query_data = data.get('query', {})
            query = QueryConfig(
                slow_query_threshold=query_data.get('slow_query_threshold', 1.0),
                max_query_history=query_data.get('max_query_history', 10000),
                enable_auto_optimization=query_data.get('enable_auto_optimization', True),
                enable_index_suggestions=query_data.get('enable_index_suggestions', True),
                enable_query_rewriting=query_data.get('enable_query_rewriting', True),
                max_suggestions_per_query=query_data.get('max_suggestions_per_query', 5),
                complexity_threshold=query_data.get('complexity_threshold', 0.7),
                analysis_interval=query_data.get('analysis_interval', 300),
                max_query_length=query_data.get('max_query_length', 10000),
                max_tables_per_query=query_data.get('max_tables_per_query', 10),
                max_joins_per_query=query_data.get('max_joins_per_query', 5)
            )
            
            # Monitoring
            monitoring_data = data.get('monitoring', {})
            monitoring = MonitoringConfig(
                metrics_collection_interval=monitoring_data.get('metrics_collection_interval', 60),
                optimization_interval=monitoring_data.get('optimization_interval', 300),
                report_generation_interval=monitoring_data.get('report_generation_interval', 3600),
                max_metrics_history=monitoring_data.get('max_metrics_history', 10000),
                max_optimization_history=monitoring_data.get('max_optimization_history', 1000),
                enable_alerts=monitoring_data.get('enable_alerts', True),
                alert_cooldown=monitoring_data.get('alert_cooldown', 300),
                enable_detailed_logging=monitoring_data.get('enable_detailed_logging', True),
                log_level=monitoring_data.get('log_level', 'INFO')
            )
            
            # Configuração principal
            config = OptimizationConfig(
                environment=environment,
                thresholds=thresholds,
                cache=cache,
                query=query,
                monitoring=monitoring,
                enable_auto_optimization=data.get('enable_auto_optimization', True),
                enable_performance_monitoring=data.get('enable_performance_monitoring', True),
                enable_cache_optimization=data.get('enable_cache_optimization', True),
                enable_query_optimization=data.get('enable_query_optimization', True),
                enable_memory_optimization=data.get('enable_memory_optimization', True),
                max_optimization_duration=data.get('max_optimization_duration', 30),
                enable_rollback=data.get('enable_rollback', True),
                optimization_timeout=data.get('optimization_timeout', 60)
            )
            
            return config
            
        except Exception as e:
            print(f"Erro ao parsear configuração: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> OptimizationConfig:
        """Retorna configuração padrão."""
        return OptimizationConfig()
    
    def get_config(self) -> OptimizationConfig:
        """Retorna a configuração atual."""
        return self.config
    
    def update_config(self, new_config: OptimizationConfig):
        """Atualiza a configuração."""
        self.config = new_config
    
    def save_config(self, file_path: Optional[str] = None):
        """Salva configuração em arquivo."""
        try:
            import yaml
            
            save_path = file_path or self.config_file or 'optimization_config.yaml'
            
            config_data = {
                'environment': self.config.environment.value,
                'thresholds': {
                    'response_time_warning': self.config.thresholds.response_time_warning,
                    'response_time_critical': self.config.thresholds.response_time_critical,
                    'memory_warning': self.config.thresholds.memory_warning,
                    'memory_critical': self.config.thresholds.memory_critical,
                    'cpu_warning': self.config.thresholds.cpu_warning,
                    'cpu_critical': self.config.thresholds.cpu_critical,
                    'cache_hit_rate_warning': self.config.thresholds.cache_hit_rate_warning,
                    'cache_hit_rate_critical': self.config.thresholds.cache_hit_rate_critical,
                    'query_time_warning': self.config.thresholds.query_time_warning,
                    'query_time_critical': self.config.thresholds.query_time_critical,
                    'error_rate_warning': self.config.thresholds.error_rate_warning,
                    'error_rate_critical': self.config.thresholds.error_rate_critical
                },
                'cache': {
                    'default_strategy': self.config.cache.default_strategy,
                    'enable_layered_cache': self.config.cache.enable_layered_cache,
                    'enable_compression': self.config.cache.enable_compression,
                    'l1_max_size': self.config.cache.l1_max_size,
                    'l2_max_size': self.config.cache.l2_max_size,
                    'l3_max_size': self.config.cache.l3_max_size,
                    'l1_ttl': self.config.cache.l1_ttl,
                    'l2_ttl': self.config.cache.l2_ttl,
                    'l3_ttl': self.config.cache.l3_ttl,
                    'enable_preloading': self.config.cache.enable_preloading,
                    'enable_pattern_analysis': self.config.cache.enable_pattern_analysis,
                    'compression_threshold': self.config.cache.compression_threshold,
                    'adaptive_learning_rate': self.config.cache.adaptive_learning_rate
                },
                'query': {
                    'slow_query_threshold': self.config.query.slow_query_threshold,
                    'max_query_history': self.config.query.max_query_history,
                    'enable_auto_optimization': self.config.query.enable_auto_optimization,
                    'enable_index_suggestions': self.config.query.enable_index_suggestions,
                    'enable_query_rewriting': self.config.query.enable_query_rewriting,
                    'max_suggestions_per_query': self.config.query.max_suggestions_per_query,
                    'complexity_threshold': self.config.query.complexity_threshold,
                    'analysis_interval': self.config.query.analysis_interval,
                    'max_query_length': self.config.query.max_query_length,
                    'max_tables_per_query': self.config.query.max_tables_per_query,
                    'max_joins_per_query': self.config.query.max_joins_per_query
                },
                'monitoring': {
                    'metrics_collection_interval': self.config.monitoring.metrics_collection_interval,
                    'optimization_interval': self.config.monitoring.optimization_interval,
                    'report_generation_interval': self.config.monitoring.report_generation_interval,
                    'max_metrics_history': self.config.monitoring.max_metrics_history,
                    'max_optimization_history': self.config.monitoring.max_optimization_history,
                    'enable_alerts': self.config.monitoring.enable_alerts,
                    'alert_cooldown': self.config.monitoring.alert_cooldown,
                    'enable_detailed_logging': self.config.monitoring.enable_detailed_logging,
                    'log_level': self.config.monitoring.log_level
                },
                'enable_auto_optimization': self.config.enable_auto_optimization,
                'enable_performance_monitoring': self.config.enable_performance_monitoring,
                'enable_cache_optimization': self.config.enable_cache_optimization,
                'enable_query_optimization': self.config.enable_query_optimization,
                'enable_memory_optimization': self.config.enable_memory_optimization,
                'max_optimization_duration': self.config.max_optimization_duration,
                'enable_rollback': self.config.enable_rollback,
                'optimization_timeout': self.config.optimization_timeout
            }
            
            with open(save_path, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            
            print(f"Configuração salva em: {save_path}")
            
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")
    
    def validate_config(self) -> bool:
        """Valida a configuração atual."""
        try:
            # Validar thresholds
            if self.config.thresholds.response_time_warning >= self.config.thresholds.response_time_critical:
                print("Erro: response_time_warning deve ser menor que response_time_critical")
                return False
            
            if self.config.thresholds.memory_warning >= self.config.thresholds.memory_critical:
                print("Erro: memory_warning deve ser menor que memory_critical")
                return False
            
            if self.config.thresholds.cpu_warning >= self.config.thresholds.cpu_critical:
                print("Erro: cpu_warning deve ser menor que cpu_critical")
                return False
            
            # Validar cache
            if self.config.cache.l1_max_size <= 0:
                print("Erro: l1_max_size deve ser maior que 0")
                return False
            
            if self.config.cache.l2_max_size <= self.config.cache.l1_max_size:
                print("Erro: l2_max_size deve ser maior que l1_max_size")
                return False
            
            # Validar query
            if self.config.query.slow_query_threshold <= 0:
                print("Erro: slow_query_threshold deve ser maior que 0")
                return False
            
            if self.config.query.max_query_history <= 0:
                print("Erro: max_query_history deve ser maior que 0")
                return False
            
            # Validar monitoring
            if self.config.monitoring.metrics_collection_interval <= 0:
                print("Erro: metrics_collection_interval deve ser maior que 0")
                return False
            
            if self.config.monitoring.optimization_interval <= 0:
                print("Erro: optimization_interval deve ser maior que 0")
                return False
            
            print("Configuração válida!")
            return True
            
        except Exception as e:
            print(f"Erro na validação: {e}")
            return False


# Configurações por ambiente
def get_environment_config(environment: Environment) -> OptimizationConfig:
    """Retorna configuração específica para o ambiente."""
    if environment == Environment.DEVELOPMENT:
        return OptimizationConfig(
            environment=Environment.DEVELOPMENT,
            thresholds=PerformanceThresholds(
                response_time_warning=2.0,
                response_time_critical=5.0,
                memory_warning=0.8,
                memory_critical=0.95
            ),
            cache=CacheConfig(
                l1_max_size=500,
                l2_max_size=5000,
                l3_max_size=50000
            ),
            query=QueryConfig(
                slow_query_threshold=2.0,
                max_query_history=5000
            ),
            monitoring=MonitoringConfig(
                metrics_collection_interval=120,
                optimization_interval=600
            )
        )
    
    elif environment == Environment.PRODUCTION:
        return OptimizationConfig(
            environment=Environment.PRODUCTION,
            thresholds=PerformanceThresholds(
                response_time_warning=0.5,
                response_time_critical=1.0,
                memory_warning=0.6,
                memory_critical=0.8
            ),
            cache=CacheConfig(
                l1_max_size=2000,
                l2_max_size=20000,
                l3_max_size=200000
            ),
            query=QueryConfig(
                slow_query_threshold=0.5,
                max_query_history=20000
            ),
            monitoring=MonitoringConfig(
                metrics_collection_interval=30,
                optimization_interval=180
            )
        )
    
    else:
        return OptimizationConfig(environment=environment)


# Instância global
_global_config_manager: Optional[OptimizationConfigManager] = None


def get_global_config_manager() -> OptimizationConfigManager:
    """Obtém o gerenciador de configuração global."""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = OptimizationConfigManager()
    return _global_config_manager


def set_global_config_manager(manager: OptimizationConfigManager):
    """Define o gerenciador de configuração global."""
    global _global_config_manager
    _global_config_manager = manager 