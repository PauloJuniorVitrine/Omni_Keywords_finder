#!/usr/bin/env python3
"""
Feature Flags para Integrações Externas - Omni Keywords Finder

Tracing ID: FF-001
Data/Hora: 2024-12-19 23:45:00 UTC
Versão: 1.0
Status: Implementação Inicial

Sistema de feature flags para controle granular de integrações externas,
permitindo rollout gradual, fallbacks automáticos e configuração por ambiente.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import uuid

# Configuração de logging
logger = logging.getLogger(__name__)

# Import Redis com fallback
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("[FF-001] Redis não disponível. Cache local será usado.")

class Environment(Enum):
    """Ambientes suportados"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class IntegrationType(Enum):
    """Tipos de integração suportados"""
    GOOGLE_TRENDS = "google_trends"
    GOOGLE_SEARCH_CONSOLE = "google_search_console"
    SEMRUSH = "semrush"
    AHREFS = "ahrefs"
    MAJESTIC = "majestic"
    WEBHOOK = "webhook"
    PAYMENT_GATEWAY = "payment_gateway"
    NOTIFICATION = "notification"
    BACKUP = "backup"
    ANALYTICS = "analytics"

class RolloutStrategy(Enum):
    """Estratégias de rollout"""
    IMMEDIATE = "immediate"
    PERCENTAGE = "percentage"
    GRADUAL = "gradual"
    CANARY = "canary"
    A_B_TEST = "a_b_test"

@dataclass
class FeatureFlagConfig:
    """Configuração de feature flag"""
    name: str
    integration_type: IntegrationType
    enabled: bool = False
    rollout_strategy: RolloutStrategy = RolloutStrategy.IMMEDIATE
    rollout_percentage: float = 100.0
    rollout_start_time: Optional[datetime] = None
    rollout_end_time: Optional[datetime] = None
    fallback_enabled: bool = True
    fallback_config: Optional[Dict[str, Any]] = None
    environment: Environment = Environment.DEVELOPMENT
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()

class IntegrationFeatureFlags:
    """
    Sistema de feature flags para integrações externas
    """
    
    def __init__(self, redis_url: Optional[str] = None, environment: Environment = Environment.DEVELOPMENT):
        """
        Inicializa o sistema de feature flags
        
        Args:
            redis_url: URL do Redis para cache (opcional)
            environment: Ambiente atual
        """
        self.environment = environment
        self.redis_client = None
        self.cache_ttl = 300  # 5 minutos
        
        # Configuração do Redis
        if redis_url and REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(redis_url)
                logger.info(f"[FF-001] Redis conectado para feature flags - {environment.value}")
            except Exception as e:
                logger.warning(f"[FF-001] Falha ao conectar Redis: {e}")
        
        # Cache local
        self._local_cache: Dict[str, FeatureFlagConfig] = {}
        self._cache_timestamp: Dict[str, datetime] = {}
        
        # Configurações padrão por integração
        self._default_configs = self._initialize_default_configs()
        
        logger.info(f"[FF-001] Sistema de feature flags inicializado - {environment.value}")

    def _initialize_default_configs(self) -> Dict[str, FeatureFlagConfig]:
        """Inicializa configurações padrão por integração"""
        configs = {}
        
        for integration in IntegrationType:
            configs[integration.value] = FeatureFlagConfig(
                name=f"{integration.value}_feature_flag",
                integration_type=integration,
                enabled=True if self.environment == Environment.DEVELOPMENT else False,
                rollout_strategy=RolloutStrategy.IMMEDIATE,
                rollout_percentage=100.0,
                fallback_enabled=True,
                fallback_config=self._get_default_fallback_config(integration),
                environment=self.environment,
                metadata={
                    "description": f"Feature flag para integração {integration.value}",
                    "owner": "devops-team",
                    "priority": "medium"
                }
            )
        
        return configs

    def _get_default_fallback_config(self, integration: IntegrationType) -> Dict[str, Any]:
        """Retorna configuração de fallback padrão por integração"""
        fallbacks = {
            IntegrationType.GOOGLE_TRENDS: {
                "fallback_provider": "mock_data",
                "cache_duration": 3600,
                "retry_attempts": 3
            },
            IntegrationType.GOOGLE_SEARCH_CONSOLE: {
                "fallback_provider": "cached_data",
                "cache_duration": 7200,
                "retry_attempts": 2
            },
            IntegrationType.SEMRUSH: {
                "fallback_provider": "alternative_api",
                "cache_duration": 1800,
                "retry_attempts": 1
            },
            IntegrationType.WEBHOOK: {
                "fallback_provider": "queue_system",
                "retry_attempts": 5,
                "retry_delay": 60
            },
            IntegrationType.PAYMENT_GATEWAY: {
                "fallback_provider": "alternative_gateway",
                "retry_attempts": 3,
                "retry_delay": 30
            }
        }
        
        return fallbacks.get(integration, {
            "fallback_provider": "mock_data",
            "cache_duration": 3600,
            "retry_attempts": 3
        })

    def is_enabled(self, integration_type: Union[str, IntegrationType], 
                   user_id: Optional[str] = None, 
                   context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Verifica se uma feature flag está habilitada
        
        Args:
            integration_type: Tipo de integração
            user_id: ID do usuário (para rollout gradual)
            context: Contexto adicional
            
        Returns:
            True se habilitada, False caso contrário
        """
        try:
            # Normalizar tipo de integração
            if isinstance(integration_type, str):
                integration_type = IntegrationType(integration_type)
            
            # Obter configuração
            config = self.get_config(integration_type)
            if not config:
                logger.warning(f"[FF-001] Configuração não encontrada para {integration_type.value}")
                return False
            
            # Verificar se está habilitada
            if not config.enabled:
                return False
            
            # Aplicar estratégia de rollout
            return self._apply_rollout_strategy(config, user_id, context)
            
        except Exception as e:
            logger.error(f"[FF-001] Erro ao verificar feature flag: {e}")
            return False

    def _apply_rollout_strategy(self, config: FeatureFlagConfig, 
                               user_id: Optional[str], 
                               context: Optional[Dict[str, Any]]) -> bool:
        """Aplica estratégia de rollout"""
        
        if config.rollout_strategy == RolloutStrategy.IMMEDIATE:
            return True
        
        elif config.rollout_strategy == RolloutStrategy.PERCENTAGE:
            return self._check_percentage_rollout(config, user_id)
        
        elif config.rollout_strategy == RolloutStrategy.GRADUAL:
            return self._check_gradual_rollout(config)
        
        elif config.rollout_strategy == RolloutStrategy.CANARY:
            return self._check_canary_rollout(config, user_id, context)
        
        elif config.rollout_strategy == RolloutStrategy.A_B_TEST:
            return self._check_ab_test_rollout(config, user_id)
        
        return False

    def _check_percentage_rollout(self, config: FeatureFlagConfig, user_id: Optional[str]) -> bool:
        """Verifica rollout por porcentagem"""
        if not user_id:
            return config.rollout_percentage >= 100.0
        
        # Hash do user_id para distribuição consistente
        user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        user_percentage = (user_hash % 100) + 1
        
        return user_percentage <= config.rollout_percentage

    def _check_gradual_rollout(self, config: FeatureFlagConfig) -> bool:
        """Verifica rollout gradual baseado no tempo"""
        now = datetime.utcnow()
        
        if not config.rollout_start_time or not config.rollout_end_time:
            return True
        
        if now < config.rollout_start_time:
            return False
        
        if now > config.rollout_end_time:
            return True
        
        # Calcular progresso do rollout
        total_duration = (config.rollout_end_time - config.rollout_start_time).total_seconds()
        elapsed = (now - config.rollout_start_time).total_seconds()
        progress = min(elapsed / total_duration, 1.0)
        
        return progress * 100 <= config.rollout_percentage

    def _check_canary_rollout(self, config: FeatureFlagConfig, 
                             user_id: Optional[str], 
                             context: Optional[Dict[str, Any]]) -> bool:
        """Verifica rollout canary"""
        if not user_id:
            return False
        
        # Verificar se é usuário canary
        canary_users = context.get('canary_users', []) if context else []
        return user_id in canary_users

    def _check_ab_test_rollout(self, config: FeatureFlagConfig, user_id: Optional[str]) -> bool:
        """Verifica rollout A/B test"""
        if not user_id:
            return False
        
        # Usar user_id para determinar grupo A ou B
        user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        return user_hash % 2 == 0  # 50% para grupo A

    def get_config(self, integration_type: Union[str, IntegrationType]) -> Optional[FeatureFlagConfig]:
        """Obtém configuração de feature flag"""
        try:
            if isinstance(integration_type, str):
                integration_type = IntegrationType(integration_type)
            
            # Verificar cache local
            cache_key = f"ff_config_{integration_type.value}_{self.environment.value}"
            if self._is_cache_valid(cache_key):
                return self._local_cache.get(cache_key)
            
            # Verificar Redis
            if self.redis_client:
                cached_config = self._get_from_redis(cache_key)
                if cached_config:
                    self._local_cache[cache_key] = cached_config
                    self._cache_timestamp[cache_key] = datetime.utcnow()
                    return cached_config
            
            # Usar configuração padrão
            default_config = self._default_configs.get(integration_type.value)
            if default_config:
                self._local_cache[cache_key] = default_config
                self._cache_timestamp[cache_key] = datetime.utcnow()
                
                # Salvar no Redis
                if self.redis_client:
                    self._save_to_redis(cache_key, default_config)
            
            return default_config
            
        except Exception as e:
            logger.error(f"[FF-001] Erro ao obter configuração: {e}")
            return None

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Verifica se cache local é válido"""
        if cache_key not in self._cache_timestamp:
            return False
        
        elapsed = (datetime.utcnow() - self._cache_timestamp[cache_key]).total_seconds()
        return elapsed < self.cache_ttl

    def _get_from_redis(self, cache_key: str) -> Optional[FeatureFlagConfig]:
        """Obtém configuração do Redis"""
        try:
            if not self.redis_client:
                return None
            
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                config_dict = json.loads(cached_data)
                return self._dict_to_config(config_dict)
            
            return None
            
        except Exception as e:
            logger.error(f"[FF-001] Erro ao obter do Redis: {e}")
            return None

    def _save_to_redis(self, cache_key: str, config: FeatureFlagConfig):
        """Salva configuração no Redis"""
        try:
            if not self.redis_client:
                return
            
            config_dict = asdict(config)
            # Converter datetime para string
            config_dict['created_at'] = config_dict['created_at'].isoformat()
            config_dict['updated_at'] = config_dict['updated_at'].isoformat()
            if config_dict['rollout_start_time']:
                config_dict['rollout_start_time'] = config_dict['rollout_start_time'].isoformat()
            if config_dict['rollout_end_time']:
                config_dict['rollout_end_time'] = config_dict['rollout_end_time'].isoformat()
            
            self.redis_client.setex(
                cache_key, 
                self.cache_ttl, 
                json.dumps(config_dict)
            )
            
        except Exception as e:
            logger.error(f"[FF-001] Erro ao salvar no Redis: {e}")

    def _dict_to_config(self, config_dict: Dict[str, Any]) -> FeatureFlagConfig:
        """Converte dicionário para FeatureFlagConfig"""
        # Converter strings de volta para datetime
        if config_dict.get('created_at'):
            config_dict['created_at'] = datetime.fromisoformat(config_dict['created_at'])
        if config_dict.get('updated_at'):
            config_dict['updated_at'] = datetime.fromisoformat(config_dict['updated_at'])
        if config_dict.get('rollout_start_time'):
            config_dict['rollout_start_time'] = datetime.fromisoformat(config_dict['rollout_start_time'])
        if config_dict.get('rollout_end_time'):
            config_dict['rollout_end_time'] = datetime.fromisoformat(config_dict['rollout_end_time'])
        
        # Converter enums
        config_dict['integration_type'] = IntegrationType(config_dict['integration_type'])
        config_dict['rollout_strategy'] = RolloutStrategy(config_dict['rollout_strategy'])
        config_dict['environment'] = Environment(config_dict['environment'])
        
        return FeatureFlagConfig(**config_dict)

    def update_config(self, integration_type: Union[str, IntegrationType], 
                     updates: Dict[str, Any]) -> bool:
        """
        Atualiza configuração de feature flag
        
        Args:
            integration_type: Tipo de integração
            updates: Atualizações a serem aplicadas
            
        Returns:
            True se atualizado com sucesso
        """
        try:
            if isinstance(integration_type, str):
                integration_type = IntegrationType(integration_type)
            
            config = self.get_config(integration_type)
            if not config:
                return False
            
            # Aplicar atualizações
            for key, value in updates.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            
            config.updated_at = datetime.utcnow()
            
            # Limpar cache
            cache_key = f"ff_config_{integration_type.value}_{self.environment.value}"
            if cache_key in self._local_cache:
                del self._local_cache[cache_key]
            if cache_key in self._cache_timestamp:
                del self._cache_timestamp[cache_key]
            
            # Salvar no Redis
            if self.redis_client:
                self._save_to_redis(cache_key, config)
            
            logger.info(f"[FF-001] Configuração atualizada: {integration_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"[FF-001] Erro ao atualizar configuração: {e}")
            return False

    def get_fallback_config(self, integration_type: Union[str, IntegrationType]) -> Optional[Dict[str, Any]]:
        """Obtém configuração de fallback"""
        config = self.get_config(integration_type)
        if config and config.fallback_enabled:
            return config.fallback_config
        return None

    def get_all_configs(self) -> Dict[str, FeatureFlagConfig]:
        """Obtém todas as configurações"""
        configs = {}
        for integration in IntegrationType:
            config = self.get_config(integration)
            if config:
                configs[integration.value] = config
        return configs

    def get_health_status(self) -> Dict[str, Any]:
        """Obtém status de saúde do sistema"""
        try:
            redis_status = "connected" if self.redis_client and self.redis_client.ping() else "disconnected"
            
            configs = self.get_all_configs()
            enabled_count = sum(1 for config in configs.values() if config.enabled)
            
            return {
                "status": "healthy",
                "environment": self.environment.value,
                "redis_status": redis_status,
                "total_configs": len(configs),
                "enabled_configs": enabled_count,
                "cache_ttl": self.cache_ttl,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[FF-001] Erro ao obter status de saúde: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

# Instância global
_integration_flags: Optional[IntegrationFeatureFlags] = None

def get_integration_flags() -> IntegrationFeatureFlags:
    """Obtém instância global do sistema de feature flags"""
    global _integration_flags
    
    if _integration_flags is None:
        redis_url = os.getenv('REDIS_URL')
        environment = Environment(os.getenv('ENVIRONMENT', 'development'))
        _integration_flags = IntegrationFeatureFlags(redis_url, environment)
    
    return _integration_flags

def is_integration_enabled(integration_type: Union[str, IntegrationType], 
                          user_id: Optional[str] = None, 
                          context: Optional[Dict[str, Any]] = None) -> bool:
    """
    Função de conveniência para verificar se integração está habilitada
    
    Args:
        integration_type: Tipo de integração
        user_id: ID do usuário
        context: Contexto adicional
        
    Returns:
        True se habilitada, False caso contrário
    """
    flags = get_integration_flags()
    return flags.is_enabled(integration_type, user_id, context)

def get_integration_fallback(integration_type: Union[str, IntegrationType]) -> Optional[Dict[str, Any]]:
    """
    Função de conveniência para obter configuração de fallback
    
    Args:
        integration_type: Tipo de integração
        
    Returns:
        Configuração de fallback ou None
    """
    flags = get_integration_flags()
    return flags.get_fallback_config(integration_type) 