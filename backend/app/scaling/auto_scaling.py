"""
Sistema de Auto Scaling
Ajusta recursos automaticamente baseado na demanda
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import psutil
import os

logger = logging.getLogger(__name__)


class ScalingAction(Enum):
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    MAINTAIN = "maintain"


class ResourceType(Enum):
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    CONNECTIONS = "connections"
    CUSTOM = "custom"


class ScalingPolicy(Enum):
    TARGET_TRACKING = "target_tracking"
    STEP_SCALING = "step_scaling"
    SIMPLE_SCALING = "simple_scaling"


@dataclass
class ResourceMetrics:
    resource_type: ResourceType
    current_value: float
    target_value: float
    min_value: float
    max_value: float
    unit: str
    timestamp: datetime


@dataclass
class ScalingRule:
    id: str
    name: str
    resource_type: ResourceType
    policy: ScalingPolicy
    target_value: float
    scale_up_threshold: float
    scale_down_threshold: float
    scale_up_cooldown: int = 300  # 5 minutos
    scale_down_cooldown: int = 300  # 5 minutos
    min_capacity: int = 1
    max_capacity: int = 10
    step_size: int = 1
    enabled: bool = True
    metadata: Dict[str, Any] = None


@dataclass
class ScalingAction:
    id: str
    rule_id: str
    action_type: ScalingAction
    current_capacity: int
    target_capacity: int
    reason: str
    timestamp: datetime
    executed: bool = False
    success: bool = False


@dataclass
class AutoScalingMetrics:
    current_capacity: int
    target_capacity: int
    min_capacity: int
    max_capacity: int
    scale_up_actions: int
    scale_down_actions: int
    total_actions: int
    success_rate: float
    avg_scaling_time: float


class AutoScaler:
    """
    Sistema de auto scaling com múltiplas políticas
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.rules: Dict[str, ScalingRule] = {}
        self.actions: List[ScalingAction] = []
        self.current_capacity = self.config.get('initial_capacity', 1)
        self.min_capacity = self.config.get('min_capacity', 1)
        self.max_capacity = self.config.get('max_capacity', 10)
        
        # Métricas
        self.metrics = AutoScalingMetrics(
            current_capacity=self.current_capacity,
            target_capacity=self.current_capacity,
            min_capacity=self.min_capacity,
            max_capacity=self.max_capacity,
            scale_up_actions=0,
            scale_down_actions=0,
            total_actions=0,
            success_rate=0.0,
            avg_scaling_time=0.0
        )
        
        # Cooldowns
        self.last_scale_up = datetime.now()
        self.last_scale_down = datetime.now()
        
        # Callbacks
        self.scale_up_callback: Optional[Callable] = None
        self.scale_down_callback: Optional[Callable] = None
        self.metrics_callback: Optional[Callable] = None
        
        # Monitoramento
        self.monitoring_task = None
        self.is_running = False
        self._lock = threading.Lock()
    
    async def start(self):
        """Inicia o auto scaler"""
        if self.is_running:
            return
        
        self.is_running = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Auto scaler started")
    
    async def stop(self):
        """Para o auto scaler"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Auto scaler stopped")
    
    def add_scaling_rule(self, rule: ScalingRule) -> bool:
        """Adiciona regra de scaling"""
        try:
            self.rules[rule.id] = rule
            logger.info(f"Scaling rule added: {rule.name}")
            return True
        except Exception as e:
            logger.error(f"Error adding scaling rule: {e}")
            return False
    
    def remove_scaling_rule(self, rule_id: str) -> bool:
        """Remove regra de scaling"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Scaling rule removed: {rule_id}")
            return True
        return False
    
    def set_scale_up_callback(self, callback: Callable):
        """Define callback para scale up"""
        self.scale_up_callback = callback
    
    def set_scale_down_callback(self, callback: Callable):
        """Define callback para scale down"""
        self.scale_down_callback = callback
    
    def set_metrics_callback(self, callback: Callable):
        """Define callback para coleta de métricas"""
        self.metrics_callback = callback
    
    async def _monitoring_loop(self):
        """Loop de monitoramento"""
        while self.is_running:
            try:
                await self._check_scaling_rules()
                await asyncio.sleep(self.config.get('check_interval', 30))
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)
    
    async def _check_scaling_rules(self):
        """Verifica regras de scaling"""
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            
            # Coletar métricas
            metrics = await self._collect_metrics(rule.resource_type)
            if not metrics:
                continue
            
            # Verificar se precisa escalar
            action = self._evaluate_scaling_rule(rule, metrics)
            if action:
                await self._execute_scaling_action(action)
    
    async def _collect_metrics(self, resource_type: ResourceType) -> Optional[ResourceMetrics]:
        """Coleta métricas do recurso"""
        try:
            if self.metrics_callback:
                return await self.metrics_callback(resource_type)
            
            # Métricas padrão
            if resource_type == ResourceType.CPU:
                return ResourceMetrics(
                    resource_type=resource_type,
                    current_value=psutil.cpu_percent(interval=1),
                    target_value=70.0,
                    min_value=0.0,
                    max_value=100.0,
                    unit="%",
                    timestamp=datetime.now()
                )
            
            elif resource_type == ResourceType.MEMORY:
                memory = psutil.virtual_memory()
                return ResourceMetrics(
                    resource_type=resource_type,
                    current_value=memory.percent,
                    target_value=80.0,
                    min_value=0.0,
                    max_value=100.0,
                    unit="%",
                    timestamp=datetime.now()
                )
            
            elif resource_type == ResourceType.DISK:
                disk = psutil.disk_usage('/')
                return ResourceMetrics(
                    resource_type=resource_type,
                    current_value=disk.percent,
                    target_value=85.0,
                    min_value=0.0,
                    max_value=100.0,
                    unit="%",
                    timestamp=datetime.now()
                )
            
            elif resource_type == ResourceType.NETWORK:
                # Métricas de rede (simplificado)
                return ResourceMetrics(
                    resource_type=resource_type,
                    current_value=0.0,  # Implementar métricas de rede
                    target_value=1000.0,
                    min_value=0.0,
                    max_value=10000.0,
                    unit="MB/s",
                    timestamp=datetime.now()
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error collecting metrics for {resource_type}: {e}")
            return None
    
    def _evaluate_scaling_rule(self, rule: ScalingRule, metrics: ResourceMetrics) -> Optional[ScalingAction]:
        """Avalia regra de scaling"""
        current_time = datetime.now()
        
        # Verificar cooldowns
        if rule.policy == ScalingPolicy.SIMPLE_SCALING:
            if (current_time - self.last_scale_up).total_seconds() < rule.scale_up_cooldown:
                return None
            if (current_time - self.last_scale_down).total_seconds() < rule.scale_down_cooldown:
                return None
        
        # Verificar thresholds
        if metrics.current_value > rule.scale_up_threshold:
            if self.current_capacity < rule.max_capacity:
                return ScalingAction(
                    id=str(uuid.uuid4()),
                    rule_id=rule.id,
                    action_type=ScalingAction.SCALE_UP,
                    current_capacity=self.current_capacity,
                    target_capacity=min(self.current_capacity + rule.step_size, rule.max_capacity),
                    reason=f"{rule.resource_type.value} usage {metrics.current_value}{metrics.unit} > {rule.scale_up_threshold}{metrics.unit}",
                    timestamp=current_time
                )
        
        elif metrics.current_value < rule.scale_down_threshold:
            if self.current_capacity > rule.min_capacity:
                return ScalingAction(
                    id=str(uuid.uuid4()),
                    rule_id=rule.id,
                    action_type=ScalingAction.SCALE_DOWN,
                    current_capacity=self.current_capacity,
                    target_capacity=max(self.current_capacity - rule.step_size, rule.min_capacity),
                    reason=f"{rule.resource_type.value} usage {metrics.current_value}{metrics.unit} < {rule.scale_down_threshold}{metrics.unit}",
                    timestamp=current_time
                )
        
        return None
    
    async def _execute_scaling_action(self, action: ScalingAction):
        """Executa ação de scaling"""
        start_time = time.time()
        
        try:
            with self._lock:
                if action.action_type == ScalingAction.SCALE_UP:
                    success = await self._scale_up(action.target_capacity)
                    if success:
                        self.last_scale_up = datetime.now()
                        self.metrics.scale_up_actions += 1
                else:
                    success = await self._scale_down(action.target_capacity)
                    if success:
                        self.last_scale_down = datetime.now()
                        self.metrics.scale_down_actions += 1
            
            action.executed = True
            action.success = success
            
            # Atualizar métricas
            scaling_time = time.time() - start_time
            self.metrics.total_actions += 1
            self.metrics.avg_scaling_time = (
                (self.metrics.avg_scaling_time * (self.metrics.total_actions - 1) + scaling_time) 
                / self.metrics.total_actions
            )
            
            if self.metrics.total_actions > 0:
                self.metrics.success_rate = (
                    (self.metrics.scale_up_actions + self.metrics.scale_down_actions) 
                    / self.metrics.total_actions
                )
            
            logger.info(f"Scaling action executed: {action.action_type.value} to {action.target_capacity}")
            
        except Exception as e:
            action.executed = True
            action.success = False
            logger.error(f"Error executing scaling action: {e}")
    
    async def _scale_up(self, target_capacity: int) -> bool:
        """Executa scale up"""
        try:
            if self.scale_up_callback:
                success = await self.scale_up_callback(self.current_capacity, target_capacity)
            else:
                # Implementação padrão (simulada)
                success = await self._default_scale_up(target_capacity)
            
            if success:
                self.current_capacity = target_capacity
                self.metrics.current_capacity = target_capacity
                self.metrics.target_capacity = target_capacity
            
            return success
            
        except Exception as e:
            logger.error(f"Error in scale up: {e}")
            return False
    
    async def _scale_down(self, target_capacity: int) -> bool:
        """Executa scale down"""
        try:
            if self.scale_down_callback:
                success = await self.scale_down_callback(self.current_capacity, target_capacity)
            else:
                # Implementação padrão (simulada)
                success = await self._default_scale_down(target_capacity)
            
            if success:
                self.current_capacity = target_capacity
                self.metrics.current_capacity = target_capacity
                self.metrics.target_capacity = target_capacity
            
            return success
            
        except Exception as e:
            logger.error(f"Error in scale down: {e}")
            return False
    
    async def _default_scale_up(self, target_capacity: int) -> bool:
        """Implementação padrão de scale up"""
        # Simular criação de instâncias
        await asyncio.sleep(2)  # Simular tempo de criação
        logger.info(f"Default scale up: {self.current_capacity} -> {target_capacity}")
        return True
    
    async def _default_scale_down(self, target_capacity: int) -> bool:
        """Implementação padrão de scale down"""
        # Simular remoção de instâncias
        await asyncio.sleep(1)  # Simular tempo de remoção
        logger.info(f"Default scale down: {self.current_capacity} -> {target_capacity}")
        return True
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtém métricas do auto scaler"""
        return asdict(self.metrics)
    
    def get_scaling_rules(self) -> List[Dict[str, Any]]:
        """Obtém lista de regras de scaling"""
        return [
            {
                'id': rule.id,
                'name': rule.name,
                'resource_type': rule.resource_type.value,
                'policy': rule.policy.value,
                'target_value': rule.target_value,
                'scale_up_threshold': rule.scale_up_threshold,
                'scale_down_threshold': rule.scale_down_threshold,
                'min_capacity': rule.min_capacity,
                'max_capacity': rule.max_capacity,
                'enabled': rule.enabled
            }
            for rule in self.rules.values()
        ]
    
    def get_scaling_actions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtém histórico de ações de scaling"""
        recent_actions = sorted(self.actions, key=lambda x: x.timestamp, reverse=True)[:limit]
        return [
            {
                'id': action.id,
                'rule_id': action.rule_id,
                'action_type': action.action_type.value,
                'current_capacity': action.current_capacity,
                'target_capacity': action.target_capacity,
                'reason': action.reason,
                'timestamp': action.timestamp.isoformat(),
                'executed': action.executed,
                'success': action.success
            }
            for action in recent_actions
        ]


class PredictiveAutoScaler(AutoScaler):
    """
    Auto scaler com predição de demanda
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.demand_history: List[Dict[str, Any]] = []
        self.prediction_window = 300  # 5 minutos
        self.prediction_confidence = 0.8
    
    async def _predict_demand(self) -> Optional[int]:
        """Prediz demanda futura"""
        if len(self.demand_history) < 10:
            return None
        
        # Implementar algoritmo de predição
        # Por simplicidade, usar média móvel
        recent_demand = [
            entry['capacity'] for entry in self.demand_history[-10:]
        ]
        
        predicted_demand = sum(recent_demand) / len(recent_demand)
        return int(predicted_demand)
    
    async def _check_scaling_rules(self):
        """Verifica regras com predição"""
        # Predição de demanda
        predicted_demand = await self._predict_demand()
        
        # Verificar regras normais
        await super()._check_scaling_rules()
        
        # Verificar predição
        if predicted_demand and predicted_demand > self.current_capacity:
            if predicted_demand > self.max_capacity:
                predicted_demand = self.max_capacity
            
            action = ScalingAction(
                id=str(uuid.uuid4()),
                rule_id="predictive",
                action_type=ScalingAction.SCALE_UP,
                current_capacity=self.current_capacity,
                target_capacity=predicted_demand,
                reason=f"Predicted demand: {predicted_demand}",
                timestamp=datetime.now()
            )
            
            await self._execute_scaling_action(action)
    
    def record_demand(self, capacity: int, timestamp: datetime = None):
        """Registra demanda para predição"""
        self.demand_history.append({
            'capacity': capacity,
            'timestamp': timestamp or datetime.now()
        })
        
        # Manter apenas últimos 100 registros
        if len(self.demand_history) > 100:
            self.demand_history = self.demand_history[-100:]


class CostOptimizedAutoScaler(AutoScaler):
    """
    Auto scaler otimizado para custo
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cost_per_instance = kwargs.get('cost_per_instance', 1.0)
        self.cost_threshold = kwargs.get('cost_threshold', 100.0)
        self.current_cost = 0.0
    
    async def _evaluate_scaling_rule(self, rule: ScalingRule, metrics: ResourceMetrics) -> Optional[ScalingAction]:
        """Avalia regra considerando custo"""
        action = await super()._evaluate_scaling_rule(rule, metrics)
        
        if action and action.action_type == ScalingAction.SCALE_UP:
            # Verificar se o custo adicional é aceitável
            additional_cost = (action.target_capacity - action.current_capacity) * self.cost_per_instance
            if self.current_cost + additional_cost > self.cost_threshold:
                logger.warning(f"Scale up blocked due to cost threshold: {self.current_cost + additional_cost}")
                return None
        
        return action
    
    async def _scale_up(self, target_capacity: int) -> bool:
        """Scale up com controle de custo"""
        success = await super()._scale_up(target_capacity)
        if success:
            additional_cost = (target_capacity - self.current_capacity) * self.cost_per_instance
            self.current_cost += additional_cost
        
        return success
    
    async def _scale_down(self, target_capacity: int) -> bool:
        """Scale down com controle de custo"""
        success = await super()._scale_down(target_capacity)
        if success:
            reduced_cost = (self.current_capacity - target_capacity) * self.cost_per_instance
            self.current_cost = max(0, self.current_cost - reduced_cost)
        
        return success


# Funções utilitárias
def create_auto_scaler(config: Optional[Dict] = None) -> AutoScaler:
    """Cria auto scaler"""
    return AutoScaler(config)


def create_predictive_auto_scaler(config: Optional[Dict] = None) -> PredictiveAutoScaler:
    """Cria auto scaler preditivo"""
    return PredictiveAutoScaler(**(config or {}))


def create_cost_optimized_auto_scaler(config: Optional[Dict] = None) -> CostOptimizedAutoScaler:
    """Cria auto scaler otimizado para custo"""
    return CostOptimizedAutoScaler(**(config or {}))


# Instância global
auto_scaler = AutoScaler()


# Decorator para auto scaling
def with_auto_scaling(func):
    """Decorator para usar auto scaling"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Registrar demanda
        if hasattr(auto_scaler, 'record_demand'):
            auto_scaler.record_demand(auto_scaler.current_capacity)
        
        # Executar função
        result = await func(*args, **kwargs)
        
        return result
    
    return wrapper 