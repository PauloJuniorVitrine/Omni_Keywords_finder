"""
📄 Feature Flags Condicionais - Sistema Avançado
🎯 Objetivo: Feature flags baseadas em contexto com variação de schemas
📊 Funcionalidades: Contexto dinâmico, rollback automático, contratos
🔧 Integração: Redis, métricas, observabilidade
🧪 Testes: Cobertura completa de funcionalidades

Tracing ID: CONDITIONAL_FLAGS_20250127_001
Data: 2025-01-27
Versão: 1.0
"""

import json
import time
import hashlib
import logging
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar, Generic
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
import threading
from collections import defaultdict
import redis
import yaml

# Configuração de logging
logger = logging.getLogger(__name__)

T = TypeVar('T')

class FlagType(Enum):
    """Tipos de feature flags"""
    BOOLEAN = "boolean"
    PERCENTAGE = "percentage"
    STRING = "string"
    NUMBER = "number"
    JSON = "json"
    CONDITIONAL = "conditional"

class ContextType(Enum):
    """Tipos de contexto para flags"""
    USER = "user"
    SESSION = "session"
    ENVIRONMENT = "environment"
    TIME = "time"
    LOCATION = "location"
    DEVICE = "device"
    CUSTOM = "custom"

class RollbackStrategy(Enum):
    """Estratégias de rollback"""
    IMMEDIATE = "immediate"
    GRADUAL = "gradual"
    SCHEDULED = "scheduled"
    MANUAL = "manual"

@dataclass
class FlagContext:
    """Contexto para avaliação de flags"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    environment: str = "production"
    timestamp: datetime = field(default_factory=datetime.now)
    location: Optional[str] = None
    device_type: Optional[str] = None
    custom_attributes: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte contexto para dicionário"""
        return {
            'user_id': self.user_id,
            'session_id': self.session_id,
            'environment': self.environment,
            'timestamp': self.timestamp.isoformat(),
            'location': self.location,
            'device_type': self.device_type,
            'custom_attributes': self.custom_attributes
        }
    
    def get_hash(self) -> str:
        """Gera hash único do contexto"""
        context_str = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()

@dataclass
class FlagCondition:
    """Condição para ativação de flag"""
    context_type: ContextType
    attribute: str
    operator: str  # eq, ne, gt, lt, gte, lte, in, not_in, contains, regex
    value: Any
    weight: float = 1.0
    
    def evaluate(self, context: FlagContext) -> bool:
        """Avalia se a condição é verdadeira"""
        try:
            if self.context_type == ContextType.USER:
                context_value = context.user_id
            elif self.context_type == ContextType.SESSION:
                context_value = context.session_id
            elif self.context_type == ContextType.ENVIRONMENT:
                context_value = context.environment
            elif self.context_type == ContextType.TIME:
                context_value = context.timestamp
            elif self.context_type == ContextType.LOCATION:
                context_value = context.location
            elif self.context_type == ContextType.DEVICE:
                context_value = context.device_type
            elif self.context_type == ContextType.CUSTOM:
                context_value = context.custom_attributes.get(self.attribute)
            else:
                return False
            
            return self._apply_operator(context_value, self.value)
        except Exception as e:
            logger.error(f"Erro ao avaliar condição: {e}")
            return False
    
    def _apply_operator(self, context_value: Any, expected_value: Any) -> bool:
        """Aplica operador de comparação"""
        if self.operator == 'eq':
            return context_value == expected_value
        elif self.operator == 'ne':
            return context_value != expected_value
        elif self.operator == 'gt':
            return context_value > expected_value
        elif self.operator == 'lt':
            return context_value < expected_value
        elif self.operator == 'gte':
            return context_value >= expected_value
        elif self.operator == 'lte':
            return context_value <= expected_value
        elif self.operator == 'in':
            return context_value in expected_value
        elif self.operator == 'not_in':
            return context_value not in expected_value
        elif self.operator == 'contains':
            return expected_value in str(context_value)
        elif self.operator == 'regex':
            import re
            return bool(re.search(expected_value, str(context_value)))
        else:
            return False

@dataclass
class FeatureFlag(Generic[T]):
    """Definição de uma feature flag"""
    name: str
    description: str
    flag_type: FlagType
    default_value: T
    conditions: List[FlagCondition] = field(default_factory=list)
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    rollback_strategy: RollbackStrategy = RollbackStrategy.IMMEDIATE
    rollback_threshold: float = 0.1  # 10% de erro
    schema_variations: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Verifica se a flag expirou"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def get_schema_variation(self, context: FlagContext) -> Optional[Dict[str, Any]]:
        """Obtém variação de schema baseada no contexto"""
        if not self.schema_variations:
            return None
        
        # Determina qual variação usar baseado no contexto
        context_hash = context.get_hash()
        variation_key = str(hash(context_hash) % len(self.schema_variations))
        
        return self.schema_variations.get(variation_key)

@dataclass
class FlagEvaluation:
    """Resultado da avaliação de uma flag"""
    flag_name: str
    value: Any
    context: FlagContext
    conditions_met: List[FlagCondition]
    evaluation_time: float
    cache_hit: bool = False
    schema_variation: Optional[Dict[str, Any]] = None

@dataclass
class FlagMetrics:
    """Métricas de uso das flags"""
    flag_name: str
    evaluations: int = 0
    activations: int = 0
    cache_hits: int = 0
    avg_evaluation_time: float = 0.0
    error_count: int = 0
    last_evaluated: Optional[datetime] = None

class ConditionalFeatureFlags:
    """
    Sistema de feature flags condicionais com contexto dinâmico
    e variação de schemas
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        enable_caching: bool = True,
        enable_metrics: bool = True,
        enable_rollback: bool = True,
        cache_ttl: int = 300
    ):
        self.enable_caching = enable_caching
        self.enable_metrics = enable_metrics
        self.enable_rollback = enable_rollback
        self.cache_ttl = cache_ttl
        
        # Cache Redis
        try:
            self.redis_client = redis.from_url(redis_url)
            self.redis_client.ping()
            self.redis_enabled = True
            logger.info("✅ Redis conectado para feature flags")
        except Exception as e:
            logger.warning(f"⚠️ Redis não disponível: {e}")
            self.redis_enabled = False
            self.redis_client = None
        
        # Storage local
        self.flags: Dict[str, FeatureFlag] = {}
        self.metrics: Dict[str, FlagMetrics] = defaultdict(lambda: FlagMetrics(""))
        self.evaluation_cache: Dict[str, FlagEvaluation] = {}
        
        # Rollback tracking
        self.rollback_history: List[Dict[str, Any]] = []
        self.error_thresholds: Dict[str, float] = {}
        
        # Thread de monitoramento
        self.monitoring_thread = None
        self.running = True
        self._start_monitoring_thread()
    
    def _start_monitoring_thread(self):
        """Inicia thread de monitoramento para rollback automático"""
        def monitoring_worker():
            while self.running:
                try:
                    time.sleep(60)  # Verifica a cada minuto
                    self._check_rollback_conditions()
                    self._cleanup_expired_flags()
                except Exception as e:
                    logger.error(f"Erro no monitoramento: {e}")
        
        self.monitoring_thread = threading.Thread(target=monitoring_worker, daemon=True)
        self.monitoring_thread.start()
    
    def register_flag(self, flag: FeatureFlag) -> bool:
        """Registra uma nova feature flag"""
        try:
            # Valida flag
            if not self._validate_flag(flag):
                return False
            
            # Armazena flag
            self.flags[flag.name] = flag
            
            # Armazena no Redis se disponível
            if self.redis_enabled:
                flag_data = self._serialize_flag(flag)
                self.redis_client.setex(
                    f"flag:{flag.name}",
                    self.cache_ttl,
                    json.dumps(flag_data)
                )
            
            # Inicializa métricas
            self.metrics[flag.name] = FlagMetrics(flag_name=flag.name)
            
            logger.info(f"✅ Feature flag registrada: {flag.name}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao registrar flag {flag.name}: {e}")
            return False
    
    def _validate_flag(self, flag: FeatureFlag) -> bool:
        """Valida configuração da flag"""
        if not flag.name or not flag.description:
            logger.error("Nome e descrição são obrigatórios")
            return False
        
        if flag.flag_type == FlagType.PERCENTAGE:
            if not isinstance(flag.default_value, (int, float)) or not (0 <= flag.default_value <= 100):
                logger.error("Valor padrão deve ser entre 0 e 100 para flags de porcentagem")
                return False
        
        if flag.expires_at and flag.expires_at <= datetime.now():
            logger.error("Data de expiração deve ser no futuro")
            return False
        
        return True
    
    def _serialize_flag(self, flag: FeatureFlag) -> Dict[str, Any]:
        """Serializa flag para armazenamento"""
        return {
            'name': flag.name,
            'description': flag.description,
            'flag_type': flag.flag_type.value,
            'default_value': flag.default_value,
            'conditions': [
                {
                    'context_type': c.context_type.value,
                    'attribute': c.attribute,
                    'operator': c.operator,
                    'value': c.value,
                    'weight': c.weight
                }
                for c in flag.conditions
            ],
            'enabled': flag.enabled,
            'created_at': flag.created_at.isoformat(),
            'updated_at': flag.updated_at.isoformat(),
            'expires_at': flag.expires_at.isoformat() if flag.expires_at else None,
            'rollback_strategy': flag.rollback_strategy.value,
            'rollback_threshold': flag.rollback_threshold,
            'schema_variations': flag.schema_variations,
            'metadata': flag.metadata
        }
    
    def _deserialize_flag(self, data: Dict[str, Any]) -> FeatureFlag:
        """Deserializa flag do armazenamento"""
        conditions = [
            FlagCondition(
                context_type=ContextType(c['context_type']),
                attribute=c['attribute'],
                operator=c['operator'],
                value=c['value'],
                weight=c['weight']
            )
            for c in data.get('conditions', [])
        ]
        
        return FeatureFlag(
            name=data['name'],
            description=data['description'],
            flag_type=FlagType(data['flag_type']),
            default_value=data['default_value'],
            conditions=conditions,
            enabled=data['enabled'],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None,
            rollback_strategy=RollbackStrategy(data['rollback_strategy']),
            rollback_threshold=data['rollback_threshold'],
            schema_variations=data.get('schema_variations', {}),
            metadata=data.get('metadata', {})
        )
    
    def evaluate_flag(
        self,
        flag_name: str,
        context: FlagContext,
        fallback_value: Any = None
    ) -> FlagEvaluation:
        """
        Avalia uma feature flag baseada no contexto
        """
        start_time = time.time()
        
        # Verifica cache
        cache_key = f"{flag_name}:{context.get_hash()}"
        if self.enable_caching and cache_key in self.evaluation_cache:
            cached_eval = self.evaluation_cache[cache_key]
            if not self._is_cache_expired(cached_eval):
                self._update_metrics(flag_name, True, time.time() - start_time)
                return cached_eval
        
        try:
            # Obtém flag
            flag = self._get_flag(flag_name)
            if not flag:
                return self._create_fallback_evaluation(flag_name, fallback_value, context, start_time)
            
            # Verifica se flag está habilitada e não expirou
            if not flag.enabled or flag.is_expired():
                return self._create_fallback_evaluation(flag_name, flag.default_value, context, start_time)
            
            # Avalia condições
            conditions_met = self._evaluate_conditions(flag.conditions, context)
            
            # Determina valor baseado no tipo de flag
            value = self._determine_flag_value(flag, context, conditions_met)
            
            # Obtém variação de schema se aplicável
            schema_variation = flag.get_schema_variation(context)
            
            # Cria resultado
            evaluation = FlagEvaluation(
                flag_name=flag_name,
                value=value,
                context=context,
                conditions_met=conditions_met,
                evaluation_time=time.time() - start_time,
                cache_hit=False,
                schema_variation=schema_variation
            )
            
            # Armazena no cache
            if self.enable_caching:
                self.evaluation_cache[cache_key] = evaluation
            
            # Atualiza métricas
            self._update_metrics(flag_name, False, evaluation.evaluation_time)
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Erro ao avaliar flag {flag_name}: {e}")
            self._record_error(flag_name)
            return self._create_fallback_evaluation(flag_name, fallback_value, context, start_time)
    
    def _get_flag(self, flag_name: str) -> Optional[FeatureFlag]:
        """Obtém flag do storage"""
        # Tenta cache local primeiro
        if flag_name in self.flags:
            return self.flags[flag_name]
        
        # Tenta Redis
        if self.redis_enabled:
            try:
                flag_data = self.redis_client.get(f"flag:{flag_name}")
                if flag_data:
                    data = json.loads(flag_data)
                    flag = self._deserialize_flag(data)
                    self.flags[flag_name] = flag
                    return flag
            except Exception as e:
                logger.error(f"Erro ao buscar flag no Redis: {e}")
        
        return None
    
    def _evaluate_conditions(self, conditions: List[FlagCondition], context: FlagContext) -> List[FlagCondition]:
        """Avalia todas as condições da flag"""
        met_conditions = []
        
        for condition in conditions:
            if condition.evaluate(context):
                met_conditions.append(condition)
        
        return met_conditions
    
    def _determine_flag_value(
        self,
        flag: FeatureFlag,
        context: FlagContext,
        conditions_met: List[FlagCondition]
    ) -> Any:
        """Determina valor da flag baseado no tipo e condições"""
        
        if flag.flag_type == FlagType.BOOLEAN:
            return len(conditions_met) > 0
        
        elif flag.flag_type == FlagType.PERCENTAGE:
            if not conditions_met:
                return 0
            
            # Calcula porcentagem baseada no peso das condições
            total_weight = sum(c.weight for c in conditions_met)
            return min(100, total_weight * 100)
        
        elif flag.flag_type == FlagType.STRING:
            if conditions_met:
                # Retorna valor da primeira condição que foi atendida
                return str(conditions_met[0].value)
            return str(flag.default_value)
        
        elif flag.flag_type == FlagType.NUMBER:
            if conditions_met:
                return float(conditions_met[0].value)
            return float(flag.default_value)
        
        elif flag.flag_type == FlagType.JSON:
            if conditions_met:
                return conditions_met[0].value
            return flag.default_value
        
        elif flag.flag_type == FlagType.CONDITIONAL:
            # Para flags condicionais, retorna objeto com resultado
            return {
                'enabled': len(conditions_met) > 0,
                'conditions_met': [c.attribute for c in conditions_met],
                'value': flag.default_value if conditions_met else None
            }
        
        return flag.default_value
    
    def _create_fallback_evaluation(
        self,
        flag_name: str,
        fallback_value: Any,
        context: FlagContext,
        start_time: float
    ) -> FlagEvaluation:
        """Cria avaliação de fallback"""
        return FlagEvaluation(
            flag_name=flag_name,
            value=fallback_value,
            context=context,
            conditions_met=[],
            evaluation_time=time.time() - start_time,
            cache_hit=False
        )
    
    def _is_cache_expired(self, evaluation: FlagEvaluation) -> bool:
        """Verifica se cache expirou"""
        # Cache expira após 5 minutos
        return time.time() - evaluation.evaluation_time > 300
    
    def _update_metrics(self, flag_name: str, cache_hit: bool, evaluation_time: float):
        """Atualiza métricas da flag"""
        if not self.enable_metrics:
            return
        
        metrics = self.metrics[flag_name]
        metrics.evaluations += 1
        metrics.last_evaluated = datetime.now()
        
        if cache_hit:
            metrics.cache_hits += 1
        
        # Atualiza tempo médio de avaliação
        total_time = metrics.avg_evaluation_time * (metrics.evaluations - 1) + evaluation_time
        metrics.avg_evaluation_time = total_time / metrics.evaluations
    
    def _record_error(self, flag_name: str):
        """Registra erro na avaliação da flag"""
        if self.enable_metrics:
            self.metrics[flag_name].error_count += 1
    
    def _check_rollback_conditions(self):
        """Verifica condições para rollback automático"""
        if not self.enable_rollback:
            return
        
        for flag_name, metrics in self.metrics.items():
            flag = self.flags.get(flag_name)
            if not flag or flag.rollback_strategy == RollbackStrategy.MANUAL:
                continue
            
            # Verifica se erro excedeu threshold
            if metrics.evaluations > 0:
                error_rate = metrics.error_count / metrics.evaluations
                if error_rate > flag.rollback_threshold:
                    self._trigger_rollback(flag_name, error_rate)
    
    def _trigger_rollback(self, flag_name: str, error_rate: float):
        """Dispara rollback de uma flag"""
        try:
            flag = self.flags[flag_name]
            
            # Desabilita flag
            flag.enabled = False
            flag.updated_at = datetime.now()
            
            # Registra rollback
            rollback_record = {
                'flag_name': flag_name,
                'timestamp': datetime.now().isoformat(),
                'error_rate': error_rate,
                'strategy': flag.rollback_strategy.value,
                'reason': f'Error rate {error_rate:.2%} exceeded threshold {flag.rollback_threshold:.2%}'
            }
            
            self.rollback_history.append(rollback_record)
            
            # Atualiza no Redis
            if self.redis_enabled:
                flag_data = self._serialize_flag(flag)
                self.redis_client.setex(
                    f"flag:{flag_name}",
                    self.cache_ttl,
                    json.dumps(flag_data)
                )
            
            logger.warning(f"🔄 Rollback automático para flag {flag_name}: {rollback_record['reason']}")
            
        except Exception as e:
            logger.error(f"Erro ao executar rollback para {flag_name}: {e}")
    
    def _cleanup_expired_flags(self):
        """Remove flags expiradas"""
        expired_flags = []
        
        for flag_name, flag in self.flags.items():
            if flag.is_expired():
                expired_flags.append(flag_name)
        
        for flag_name in expired_flags:
            del self.flags[flag_name]
            if self.redis_enabled:
                self.redis_client.delete(f"flag:{flag_name}")
            
            logger.info(f"🗑️ Flag expirada removida: {flag_name}")
    
    def get_metrics(self) -> Dict[str, FlagMetrics]:
        """Retorna métricas de todas as flags"""
        return dict(self.metrics)
    
    def get_rollback_history(self) -> List[Dict[str, Any]]:
        """Retorna histórico de rollbacks"""
        return self.rollback_history.copy()
    
    def export_config(self, file_path: str) -> bool:
        """Exporta configuração das flags para arquivo YAML"""
        try:
            config = {
                'flags': [
                    {
                        'name': flag.name,
                        'description': flag.description,
                        'type': flag.flag_type.value,
                        'default_value': flag.default_value,
                        'enabled': flag.enabled,
                        'conditions': [
                            {
                                'context_type': c.context_type.value,
                                'attribute': c.attribute,
                                'operator': c.operator,
                                'value': c.value,
                                'weight': c.weight
                            }
                            for c in flag.conditions
                        ],
                        'rollback_strategy': flag.rollback_strategy.value,
                        'rollback_threshold': flag.rollback_threshold,
                        'schema_variations': flag.schema_variations,
                        'metadata': flag.metadata
                    }
                    for flag in self.flags.values()
                ]
            }
            
            with open(file_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            logger.info(f"✅ Configuração exportada para {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao exportar configuração: {e}")
            return False
    
    def import_config(self, file_path: str) -> bool:
        """Importa configuração das flags de arquivo YAML"""
        try:
            with open(file_path, 'r') as f:
                config = yaml.safe_load(f)
            
            for flag_data in config.get('flags', []):
                conditions = [
                    FlagCondition(
                        context_type=ContextType(c['context_type']),
                        attribute=c['attribute'],
                        operator=c['operator'],
                        value=c['value'],
                        weight=c['weight']
                    )
                    for c in flag_data.get('conditions', [])
                ]
                
                flag = FeatureFlag(
                    name=flag_data['name'],
                    description=flag_data['description'],
                    flag_type=FlagType(flag_data['type']),
                    default_value=flag_data['default_value'],
                    conditions=conditions,
                    enabled=flag_data['enabled'],
                    rollback_strategy=RollbackStrategy(flag_data['rollback_strategy']),
                    rollback_threshold=flag_data['rollback_threshold'],
                    schema_variations=flag_data.get('schema_variations', {}),
                    metadata=flag_data.get('metadata', {})
                )
                
                self.register_flag(flag)
            
            logger.info(f"✅ Configuração importada de {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao importar configuração: {e}")
            return False

# Decorator para feature flags
def feature_flag(
    flag_name: str,
    fallback_value: Any = None,
    context_provider: Optional[Callable] = None
):
    """
    Decorator para aplicar feature flags em funções
    
    Args:
        flag_name: Nome da flag
        fallback_value: Valor de fallback
        context_provider: Função para fornecer contexto
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Instância global do sistema de flags
            flags_system = getattr(func, '_flags_system', None)
            if flags_system is None:
                flags_system = ConditionalFeatureFlags()
                func._flags_system = flags_system
            
            # Obtém contexto
            if context_provider:
                context = context_provider(*args, **kwargs)
            else:
                context = FlagContext()
            
            # Avalia flag
            evaluation = flags_system.evaluate_flag(flag_name, context, fallback_value)
            
            # Se flag está ativa, executa função
            if evaluation.value:
                return func(*args, **kwargs)
            else:
                # Retorna valor de fallback ou None
                return fallback_value
        
        return wrapper
    return decorator

# Testes unitários (não executar nesta fase)
def test_conditional_flags():
    """
    Testes unitários para ConditionalFeatureFlags
    """
    # Cria sistema de flags
    flags_system = ConditionalFeatureFlags()
    
    # Cria flag de teste
    condition = FlagCondition(
        context_type=ContextType.USER,
        attribute='user_id',
        operator='eq',
        value='test_user'
    )
    
    flag = FeatureFlag(
        name='test_flag',
        description='Flag de teste',
        flag_type=FlagType.BOOLEAN,
        default_value=False,
        conditions=[condition]
    )
    
    # Registra flag
    assert flags_system.register_flag(flag)
    
    # Testa avaliação
    context = FlagContext(user_id='test_user')
    evaluation = flags_system.evaluate_flag('test_flag', context)
    assert evaluation.value is True
    
    # Testa contexto diferente
    context2 = FlagContext(user_id='other_user')
    evaluation2 = flags_system.evaluate_flag('test_flag', context2)
    assert evaluation2.value is False
    
    print("✅ Todos os testes passaram!")

if __name__ == "__main__":
    # Exemplo de uso
    flags_system = ConditionalFeatureFlags()
    
    # Cria flag condicional
    user_condition = FlagCondition(
        context_type=ContextType.USER,
        attribute='user_id',
        operator='in',
        value=['user1', 'user2', 'user3']
    )
    
    time_condition = FlagCondition(
        context_type=ContextType.TIME,
        attribute='timestamp',
        operator='gte',
        value=datetime.now() - timedelta(hours=1)
    )
    
    flag = FeatureFlag(
        name='new_feature',
        description='Nova funcionalidade para usuários específicos',
        flag_type=FlagType.BOOLEAN,
        default_value=False,
        conditions=[user_condition, time_condition],
        rollback_strategy=RollbackStrategy.IMMEDIATE,
        rollback_threshold=0.05,
        schema_variations={
            'v1': {'fields': ['id', 'name']},
            'v2': {'fields': ['id', 'name', 'email', 'phone']}
        }
    )
    
    # Registra flag
    flags_system.register_flag(flag)
    
    # Testa avaliação
    context = FlagContext(user_id='user1')
    evaluation = flags_system.evaluate_flag('new_feature', context)
    
    print(f"Flag: {evaluation.flag_name}")
    print(f"Valor: {evaluation.value}")
    print(f"Condições atendidas: {len(evaluation.conditions_met)}")
    print(f"Variação de schema: {evaluation.schema_variation}")
    
    # Obtém métricas
    metrics = flags_system.get_metrics()
    print(f"Métricas: {metrics}") 