"""
Sistema de Feature Flags Avançados - IMP-014
Tracing ID: IMP014_FEATURE_FLAGS_001_20241227
Data: 2024-12-27
Status: Implementação Inicial

Sistema enterprise-grade de feature flags com:
- Gerenciamento centralizado
- Rollout gradual (A/B testing)
- Configuração por usuário/ambiente/contexto
- Cache inteligente
- Auditoria completa
- Integração com logs estruturados
"""

import json
import os
import time
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from functools import wraps
import redis
import yaml

# Importar sistema de logs
try:
    from infrastructure.logging.advanced_structured_logger import (
        AdvancedStructuredLogger,
        set_logging_context
    )
except ImportError:
    # Fallback se sistema de logs não estiver disponível
    import logging
    AdvancedStructuredLogger = logging.getLogger
    set_logging_context = lambda **kwargs: None

class FeatureType(Enum):
    """Tipos de feature flags"""
    BOOLEAN = "boolean"
    PERCENTAGE = "percentage"
    GRADUAL = "gradual"
    TARGETED = "targeted"
    TIME_BASED = "time_based"

class RolloutStrategy(Enum):
    """Estratégias de rollout"""
    ALL_OR_NOTHING = "all_or_nothing"
    PERCENTAGE = "percentage"
    GRADUAL = "gradual"
    TARGETED_USERS = "targeted_users"
    TARGETED_ENVIRONMENTS = "targeted_environments"

@dataclass
class FeatureFlag:
    """Definição de uma feature flag"""
    name: str
    description: str
    feature_type: FeatureType
    enabled: bool = False
    rollout_strategy: RolloutStrategy = RolloutStrategy.ALL_OR_NOTHING
    rollout_percentage: float = 0.0
    target_users: List[str] = None
    target_environments: List[str] = None
    target_attributes: Dict[str, Any] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None
    created_by: str = "system"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.target_users is None:
            self.target_users = []
        if self.target_environments is None:
            self.target_environments = []
        if self.target_attributes is None:
            self.target_attributes = {}
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()

@dataclass
class FeatureContext:
    """Contexto para avaliação de feature flags"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    environment: str = "development"
    user_attributes: Dict[str, Any] = None
    request_attributes: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.user_attributes is None:
            self.user_attributes = {}
        if self.request_attributes is None:
            self.request_attributes = {}

@dataclass
class FeatureEvaluation:
    """Resultado da avaliação de uma feature flag"""
    feature_name: str
    enabled: bool
    context: FeatureContext
    evaluation_time: datetime
    cache_hit: bool = False
    rollout_percentage: float = 0.0
    reason: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class FeatureFlagCache:
    """Cache inteligente para feature flags"""
    
    def __init__(self, ttl_seconds: int = 300, max_size: int = 1000):
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self.cache = {}
        self.timestamps = {}
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[FeatureFlag]:
        """Obtém feature flag do cache"""
        with self.lock:
            if key in self.cache:
                timestamp = self.timestamps.get(key, 0)
                if time.time() - timestamp < self.ttl_seconds:
                    return self.cache[key]
                else:
                    # Expirou, remover
                    del self.cache[key]
                    del self.timestamps[key]
            return None
    
    def set(self, key: str, value: FeatureFlag):
        """Define feature flag no cache"""
        with self.lock:
            # Implementar LRU se necessário
            if len(self.cache) >= self.max_size:
                # Remover item mais antigo
                oldest_key = min(self.timestamps.keys(), key=lambda key: self.timestamps[key])
                del self.cache[oldest_key]
                del self.timestamps[oldest_key]
            
            self.cache[key] = value
            self.timestamps[key] = time.time()
    
    def clear(self):
        """Limpa cache"""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do cache"""
        with self.lock:
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "ttl_seconds": self.ttl_seconds,
                "keys": list(self.cache.keys())
            }

class FeatureFlagAuditor:
    """Auditor de feature flags"""
    
    def __init__(self, logger: AdvancedStructuredLogger):
        self.logger = logger
        self.evaluations = []
        self.lock = threading.RLock()
    
    def log_evaluation(self, evaluation: FeatureEvaluation):
        """Registra avaliação de feature flag"""
        with self.lock:
            self.evaluations.append(evaluation)
            
            # Log estruturado
            self.logger.business(
                f"Feature flag '{evaluation.feature_name}' avaliada",
                "feature_flag_evaluation",
                {
                    "feature_name": evaluation.feature_name,
                    "enabled": evaluation.enabled,
                    "user_id": evaluation.context.user_id,
                    "environment": evaluation.context.environment,
                    "cache_hit": evaluation.cache_hit,
                    "rollout_percentage": evaluation.rollout_percentage,
                    "reason": evaluation.reason,
                    "evaluation_time": evaluation.evaluation_time.isoformat()
                }
            )
    
    def get_evaluations(self, feature_name: Optional[str] = None, 
                       user_id: Optional[str] = None,
                       limit: int = 100) -> List[FeatureEvaluation]:
        """Obtém avaliações filtradas"""
        with self.lock:
            filtered = self.evaluations
            
            if feature_name:
                filtered = [e for e in filtered if e.feature_name == feature_name]
            
            if user_id:
                filtered = [e for e in filtered if e.context.user_id == user_id]
            
            return filtered[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas de auditoria"""
        with self.lock:
            if not self.evaluations:
                return {"total_evaluations": 0}
            
            feature_stats = {}
            for eval in self.evaluations:
                if eval.feature_name not in feature_stats:
                    feature_stats[eval.feature_name] = {
                        "total": 0,
                        "enabled": 0,
                        "disabled": 0
                    }
                
                feature_stats[eval.feature_name]["total"] += 1
                if eval.enabled:
                    feature_stats[eval.feature_name]["enabled"] += 1
                else:
                    feature_stats[eval.feature_name]["disabled"] += 1
            
            return {
                "total_evaluations": len(self.evaluations),
                "feature_stats": feature_stats,
                "last_evaluation": self.evaluations[-1].evaluation_time.isoformat() if self.evaluations else None
            }

class AdvancedFeatureFlags:
    """Sistema avançado de feature flags"""
    
    def __init__(
        self,
        config_file: Optional[str] = None,
        redis_url: Optional[str] = None,
        cache_ttl: int = 300,
        enable_audit: bool = True,
        logger: Optional[AdvancedStructuredLogger] = None
    ):
        self.config_file = config_file
        self.redis_url = redis_url
        self.features: Dict[str, FeatureFlag] = {}
        self.cache = FeatureFlagCache(ttl_seconds=cache_ttl)
        self.enable_audit = enable_audit
        self.logger = logger or AdvancedStructuredLogger(name="feature_flags")
        self.auditor = FeatureFlagAuditor(self.logger) if enable_audit else None
        
        # Conectar Redis se configurado
        self.redis_client = None
        if redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
                self.redis_client.ping()
                self.logger.info("Redis conectado para feature flags")
            except Exception as e:
                self.logger.warning(f"Falha ao conectar Redis: {e}")
        
        # Carregar configuração inicial
        self.load_configuration()
    
    def load_configuration(self, config_file: Optional[str] = None):
        """Carrega configuração de feature flags"""
        file_path = config_file or self.config_file
        if not file_path or not os.path.exists(file_path):
            self.logger.info("Arquivo de configuração não encontrado, usando configuração padrão")
            self._load_default_configuration()
            return
        
        try:
            with open(file_path, 'r') as f:
                if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                    config = yaml.safe_load(f)
                else:
                    config = json.load(f)
            
            self._parse_configuration(config)
            self.logger.info(f"Configuração carregada de {file_path}")
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar configuração: {e}")
            self._load_default_configuration()
    
    def _load_default_configuration(self):
        """Carrega configuração padrão"""
        default_features = [
            {
                "name": "new_ui",
                "description": "Nova interface do usuário",
                "feature_type": "boolean",
                "enabled": False,
                "rollout_strategy": "all_or_nothing"
            },
            {
                "name": "advanced_analytics",
                "description": "Analytics avançados",
                "feature_type": "percentage",
                "enabled": True,
                "rollout_strategy": "percentage",
                "rollout_percentage": 25.0
            },
            {
                "name": "beta_features",
                "description": "Recursos em beta",
                "feature_type": "targeted",
                "enabled": True,
                "rollout_strategy": "targeted_users",
                "target_users": ["admin", "beta_tester"]
            }
        ]
        
        self._parse_configuration({"features": default_features})
    
    def _parse_configuration(self, config: Dict[str, Any]):
        """Parse configuração para objetos FeatureFlag"""
        features_config = config.get("features", [])
        
        for feature_config in features_config:
            try:
                feature = FeatureFlag(
                    name=feature_config["name"],
                    description=feature_config["description"],
                    feature_type=FeatureType(feature_config["feature_type"]),
                    enabled=feature_config.get("enabled", False),
                    rollout_strategy=RolloutStrategy(feature_config.get("rollout_strategy", "all_or_nothing")),
                    rollout_percentage=feature_config.get("rollout_percentage", 0.0),
                    target_users=feature_config.get("target_users", []),
                    target_environments=feature_config.get("target_environments", []),
                    target_attributes=feature_config.get("target_attributes", {}),
                    created_by=feature_config.get("created_by", "system"),
                    metadata=feature_config.get("metadata", {})
                )
                
                # Parse datas se presentes
                if "start_date" in feature_config:
                    feature.start_date = datetime.fromisoformat(feature_config["start_date"])
                if "end_date" in feature_config:
                    feature.end_date = datetime.fromisoformat(feature_config["end_date"])
                
                self.features[feature.name] = feature
                
            except Exception as e:
                self.logger.error(f"Erro ao parse feature {feature_config.get('name', 'unknown')}: {e}")
    
    def is_enabled(self, feature_name: str, context: Optional[FeatureContext] = None) -> bool:
        """Verifica se uma feature está habilitada"""
        if context is None:
            context = FeatureContext()
        
        # Verificar cache primeiro
        cache_key = f"{feature_name}:{context.user_id}:{context.environment}"
        cached_feature = self.cache.get(cache_key)
        
        if cached_feature:
            evaluation = FeatureEvaluation(
                feature_name=feature_name,
                enabled=cached_feature.enabled,
                context=context,
                evaluation_time=datetime.utcnow(),
                cache_hit=True,
                reason="cached"
            )
            if self.auditor:
                self.auditor.log_evaluation(evaluation)
            return cached_feature.enabled
        
        # Obter feature
        feature = self.features.get(feature_name)
        if not feature:
            evaluation = FeatureEvaluation(
                feature_name=feature_name,
                enabled=False,
                context=context,
                evaluation_time=datetime.utcnow(),
                reason="feature_not_found"
            )
            if self.auditor:
                self.auditor.log_evaluation(evaluation)
            return False
        
        # Verificar se está habilitada
        if not feature.enabled:
            evaluation = FeatureEvaluation(
                feature_name=feature_name,
                enabled=False,
                context=context,
                evaluation_time=datetime.utcnow(),
                reason="feature_disabled"
            )
            if self.auditor:
                self.auditor.log_evaluation(evaluation)
            return False
        
        # Verificar datas
        now = datetime.utcnow()
        if feature.start_date and now < feature.start_date:
            evaluation = FeatureEvaluation(
                feature_name=feature_name,
                enabled=False,
                context=context,
                evaluation_time=datetime.utcnow(),
                reason="before_start_date"
            )
            if self.auditor:
                self.auditor.log_evaluation(evaluation)
            return False
        
        if feature.end_date and now > feature.end_date:
            evaluation = FeatureEvaluation(
                feature_name=feature_name,
                enabled=False,
                context=context,
                evaluation_time=datetime.utcnow(),
                reason="after_end_date"
            )
            if self.auditor:
                self.auditor.log_evaluation(evaluation)
            return False
        
        # Aplicar estratégia de rollout
        enabled = self._apply_rollout_strategy(feature, context)
        
        # Cache resultado
        self.cache.set(cache_key, feature)
        
        # Registrar avaliação
        evaluation = FeatureEvaluation(
            feature_name=feature_name,
            enabled=enabled,
            context=context,
            evaluation_time=datetime.utcnow(),
            rollout_percentage=feature.rollout_percentage,
            reason="rollout_strategy"
        )
        if self.auditor:
            self.auditor.log_evaluation(evaluation)
        
        return enabled
    
    def _apply_rollout_strategy(self, feature: FeatureFlag, context: FeatureContext) -> bool:
        """Aplica estratégia de rollout"""
        if feature.rollout_strategy == RolloutStrategy.ALL_OR_NOTHING:
            return True
        
        elif feature.rollout_strategy == RolloutStrategy.PERCENTAGE:
            if not context.user_id:
                return False
            
            # Gerar hash determinístico baseado no user_id
            hash_value = int(hashlib.md5(context.user_id.encode()).hexdigest(), 16)
            user_percentage = (hash_value % 100) + 1
            
            return user_percentage <= feature.rollout_percentage
        
        elif feature.rollout_strategy == RolloutStrategy.TARGETED_USERS:
            return context.user_id in feature.target_users
        
        elif feature.rollout_strategy == RolloutStrategy.TARGETED_ENVIRONMENTS:
            return context.environment in feature.target_environments
        
        elif feature.rollout_strategy == RolloutStrategy.GRADUAL:
            # Implementar rollout gradual baseado em tempo
            if not feature.start_date:
                return False
            
            elapsed = datetime.utcnow() - feature.start_date
            days_elapsed = elapsed.days
            
            # Aumentar gradualmente a porcentagem
            current_percentage = min(feature.rollout_percentage * (days_elapsed / 30), 100)
            
            if not context.user_id:
                return False
            
            hash_value = int(hashlib.md5(context.user_id.encode()).hexdigest(), 16)
            user_percentage = (hash_value % 100) + 1
            
            return user_percentage <= current_percentage
        
        return False
    
    def get_feature(self, feature_name: str) -> Optional[FeatureFlag]:
        """Obtém definição de uma feature"""
        return self.features.get(feature_name)
    
    def list_features(self) -> List[FeatureFlag]:
        """Lista todas as features"""
        return list(self.features.values())
    
    def add_feature(self, feature: FeatureFlag):
        """Adiciona nova feature"""
        feature.updated_at = datetime.utcnow()
        self.features[feature.name] = feature
        
        # Limpar cache relacionado
        self.cache.clear()
        
        # Log da operação
        self.logger.business(
            f"Feature '{feature.name}' adicionada",
            "feature_flag_added",
            {
                "feature_name": feature.name,
                "feature_type": feature.feature_type.value,
                "enabled": feature.enabled,
                "rollout_strategy": feature.rollout_strategy.value,
                "created_by": feature.created_by
            }
        )
    
    def update_feature(self, feature_name: str, updates: Dict[str, Any]):
        """Atualiza feature existente"""
        if feature_name not in self.features:
            raise ValueError(f"Feature '{feature_name}' não encontrada")
        
        feature = self.features[feature_name]
        
        # Aplicar updates
        for key, value in updates.items():
            if hasattr(feature, key):
                setattr(feature, key, value)
        
        feature.updated_at = datetime.utcnow()
        
        # Limpar cache relacionado
        self.cache.clear()
        
        # Log da operação
        self.logger.business(
            f"Feature '{feature_name}' atualizada",
            "feature_flag_updated",
            {
                "feature_name": feature_name,
                "updates": updates,
                "updated_at": feature.updated_at.isoformat()
            }
        )
    
    def delete_feature(self, feature_name: str):
        """Remove feature"""
        if feature_name not in self.features:
            raise ValueError(f"Feature '{feature_name}' não encontrada")
        
        del self.features[feature_name]
        
        # Limpar cache relacionado
        self.cache.clear()
        
        # Log da operação
        self.logger.business(
            f"Feature '{feature_name}' removida",
            "feature_flag_deleted",
            {"feature_name": feature_name}
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do sistema"""
        stats = {
            "total_features": len(self.features),
            "enabled_features": len([f for f in self.features.values() if f.enabled]),
            "cache_stats": self.cache.get_stats(),
            "feature_types": {},
            "rollout_strategies": {}
        }
        
        # Estatísticas por tipo
        for feature in self.features.values():
            feature_type = feature.feature_type.value
            stats["feature_types"][feature_type] = stats["feature_types"].get(feature_type, 0) + 1
            
            strategy = feature.rollout_strategy.value
            stats["rollout_strategies"][strategy] = stats["rollout_strategies"].get(strategy, 0) + 1
        
        # Estatísticas de auditoria
        if self.auditor:
            stats["audit_stats"] = self.auditor.get_stats()
        
        return stats

def feature_flag(feature_name: str, fallback: bool = False):
    """Decorator para feature flags"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Obter instância global ou criar nova
            feature_flags = getattr(wrapper, '_feature_flags', None)
            if feature_flags is None:
                feature_flags = AdvancedFeatureFlags()
                wrapper._feature_flags = feature_flags
            
            # Criar contexto básico
            context = FeatureContext()
            
            # Verificar se feature está habilitada
            if feature_flags.is_enabled(feature_name, context):
                return func(*args, **kwargs)
            else:
                return fallback
        
        return wrapper
    return decorator

# Instância global
_global_feature_flags = None

def get_feature_flags() -> AdvancedFeatureFlags:
    """Obtém instância global de feature flags"""
    global _global_feature_flags
    if _global_feature_flags is None:
        _global_feature_flags = AdvancedFeatureFlags()
    return _global_feature_flags

def is_feature_enabled(feature_name: str, context: Optional[FeatureContext] = None) -> bool:
    """Verifica se feature está habilitada (função de conveniência)"""
    return get_feature_flags().is_enabled(feature_name, context)

if __name__ == "__main__":
    # Exemplo de uso
    feature_flags = AdvancedFeatureFlags()
    
    # Criar contexto
    context = FeatureContext(
        user_id="user123",
        environment="production"
    )
    
    # Verificar features
    print(f"New UI enabled: {feature_flags.is_enabled('new_ui', context)}")
    print(f"Advanced Analytics enabled: {feature_flags.is_enabled('advanced_analytics', context)}")
    print(f"Beta Features enabled: {feature_flags.is_enabled('beta_features', context)}")
    
    # Estatísticas
    print(f"Stats: {feature_flags.get_stats()}") 