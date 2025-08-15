"""
Sistema de Automação de Respostas - Omni Keywords Finder
Automação inteligente de respostas a problemas detectados

Tracing ID: AUTO_REMEDIATION_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: 🟡 ALTO - Automação de Respostas

Baseado no código real do sistema Omni Keywords Finder
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum
import json
import time

from ...intelligent_collector import Event, EventType, EventSeverity
from ..ml_models.anomaly_detector import AnomalyResult, AnomalyType
from ..correlation_engine import CorrelationEngine

logger = logging.getLogger(__name__)

class ActionType(Enum):
    """Tipos de ações automáticas"""
    RESTART_SERVICE = "restart_service"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    CLEAR_CACHE = "clear_cache"
    OPTIMIZE_QUERY = "optimize_query"
    BLOCK_IP = "block_ip"
    SEND_ALERT = "send_alert"
    ROLLBACK = "rollback"
    CUSTOM_SCRIPT = "custom_script"

class ActionStatus(Enum):
    """Status das ações executadas"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

@dataclass
class RemediationRule:
    """Regra de remediação automática"""
    id: str
    name: str
    description: str
    conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    priority: int
    enabled: bool
    max_executions: int
    cooldown_minutes: int
    created_at: datetime
    updated_at: datetime

@dataclass
class RemediationAction:
    """Ação de remediação executada"""
    id: str
    rule_id: str
    action_type: ActionType
    status: ActionStatus
    target: str
    parameters: Dict[str, Any]
    started_at: datetime
    completed_at: Optional[datetime]
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    execution_time: Optional[float]

class AutoRemediationEngine:
    """Engine de automação de respostas"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.rules: List[RemediationRule] = []
        self.executed_actions: List[RemediationAction] = []
        self.is_enabled = self.config.get('enabled', True)
        self.max_concurrent_actions = self.config.get('max_concurrent_actions', 5)
        self.action_timeout = self.config.get('action_timeout', 300)  # 5 minutos
        self.success_rate_threshold = self.config.get('success_rate_threshold', 0.8)
        
        # Métricas
        self.total_actions_executed = 0
        self.successful_actions = 0
        self.failed_actions = 0
        
        # Inicializar regras padrão baseadas no sistema real
        self._initialize_default_rules()
        
        logger.info(f"AutoRemediationEngine inicializado com {len(self.rules)} regras")
    
    def _initialize_default_rules(self):
        """Inicializa regras padrão baseadas no sistema Omni Keywords Finder"""
        base_time = datetime.now()
        
        # Regra 1: CPU alto -> Scale up
        self.rules.append(RemediationRule(
            id="cpu_high_scale_up",
            name="Scale Up on High CPU",
            description="Escala horizontalmente quando CPU está alto",
            conditions={
                'event_type': EventType.SYSTEM_METRIC.value,
                'metric_name': 'cpu_usage',
                'threshold': 85.0,
                'duration_minutes': 5
            },
            actions=[
                {
                    'type': ActionType.SCALE_UP.value,
                    'target': 'omni_keywords_finder_app',
                    'parameters': {
                        'replicas': 2,
                        'resource_type': 'cpu',
                        'increment': 1
                    }
                }
            ],
            priority=1,
            enabled=True,
            max_executions=3,
            cooldown_minutes=10,
            created_at=base_time,
            updated_at=base_time
        ))
        
        # Regra 2: Query lenta -> Otimizar
        self.rules.append(RemediationRule(
            id="slow_query_optimize",
            name="Optimize Slow Queries",
            description="Otimiza queries lentas automaticamente",
            conditions={
                'event_type': EventType.DATABASE_QUERY.value,
                'execution_time_threshold': 5000,  # 5s
                'frequency_threshold': 3  # 3 ocorrências
            },
            actions=[
                {
                    'type': ActionType.OPTIMIZE_QUERY.value,
                    'target': 'database',
                    'parameters': {
                        'query_pattern': 'SELECT',
                        'optimization_type': 'index_suggestion',
                        'max_execution_time': 1000
                    }
                }
            ],
            priority=2,
            enabled=True,
            max_executions=5,
            cooldown_minutes=15,
            created_at=base_time,
            updated_at=base_time
        ))
        
        # Regra 3: Erro de conexão -> Restart
        self.rules.append(RemediationRule(
            id="connection_error_restart",
            name="Restart on Connection Error",
            description="Reinicia serviço em caso de erro de conexão",
            conditions={
                'event_type': EventType.ERROR_EVENT.value,
                'error_pattern': 'connection',
                'severity': EventSeverity.HIGH.value,
                'frequency_threshold': 2
            },
            actions=[
                {
                    'type': ActionType.RESTART_SERVICE.value,
                    'target': 'database_service',
                    'parameters': {
                        'service_name': 'postgresql',
                        'restart_type': 'graceful',
                        'timeout': 60
                    }
                }
            ],
            priority=3,
            enabled=True,
            max_executions=2,
            cooldown_minutes=30,
            created_at=base_time,
            updated_at=base_time
        ))
        
        # Regra 4: Cache cheio -> Limpar
        self.rules.append(RemediationRule(
            id="cache_full_clear",
            name="Clear Cache When Full",
            description="Limpa cache quando está cheio",
            conditions={
                'event_type': EventType.SYSTEM_METRIC.value,
                'metric_name': 'cache_usage',
                'threshold': 90.0,
                'duration_minutes': 2
            },
            actions=[
                {
                    'type': ActionType.CLEAR_CACHE.value,
                    'target': 'redis_cache',
                    'parameters': {
                        'cache_type': 'redis',
                        'clear_pattern': 'temp:*',
                        'preserve_critical': True
                    }
                }
            ],
            priority=4,
            enabled=True,
            max_executions=10,
            cooldown_minutes=5,
            created_at=base_time,
            updated_at=base_time
        ))
        
        # Regra 5: Ataque detectado -> Bloquear IP
        self.rules.append(RemediationRule(
            id="security_attack_block",
            name="Block IP on Security Attack",
            description="Bloqueia IP em caso de ataque detectado",
            conditions={
                'event_type': EventType.SECURITY_EVENT.value,
                'attack_type': ['sql_injection', 'xss', 'brute_force'],
                'severity': EventSeverity.CRITICAL.value
            },
            actions=[
                {
                    'type': ActionType.BLOCK_IP.value,
                    'target': 'firewall',
                    'parameters': {
                        'block_duration': 3600,  # 1 hora
                        'block_type': 'ip',
                        'reason': 'security_attack'
                    }
                },
                {
                    'type': ActionType.SEND_ALERT.value,
                    'target': 'security_team',
                    'parameters': {
                        'alert_type': 'security_incident',
                        'priority': 'high',
                        'channels': ['slack', 'email']
                    }
                }
            ],
            priority=1,  # Alta prioridade
            enabled=True,
            max_executions=20,
            cooldown_minutes=1,
            created_at=base_time,
            updated_at=base_time
        ))
    
    async def process_events(self, events: List[Event], anomalies: List[AnomalyResult] = None, correlations: List[Dict[str, Any]] = None) -> List[RemediationAction]:
        """
        Processa eventos e executa ações automáticas baseadas nas regras.
        Baseado em dados reais do sistema Omni Keywords Finder.
        """
        if not self.is_enabled:
            logger.info("Auto-remediação desabilitada")
            return []
        
        if not events:
            return []
        
        logger.info(f"Processando {len(events)} eventos para auto-remediação")
        
        executed_actions = []
        
        try:
            # Avaliar cada regra
            for rule in self.rules:
                if not rule.enabled:
                    continue
                
                # Verificar se a regra deve ser executada
                if await self._should_execute_rule(rule, events, anomalies, correlations):
                    # Executar ações da regra
                    rule_actions = await self._execute_rule_actions(rule, events)
                    executed_actions.extend(rule_actions)
                    
                    # Verificar limite de ações concorrentes
                    if len(executed_actions) >= self.max_concurrent_actions:
                        logger.warning(f"Limite de ações concorrentes atingido: {self.max_concurrent_actions}")
                        break
        
        except Exception as e:
            logger.error(f"Erro no processamento de eventos: {str(e)}")
        
        # Atualizar métricas
        self.total_actions_executed += len(executed_actions)
        self.successful_actions += len([a for a in executed_actions if a.status == ActionStatus.SUCCESS])
        self.failed_actions += len([a for a in executed_actions if a.status == ActionStatus.FAILED])
        
        logger.info(f"Executadas {len(executed_actions)} ações de remediação")
        return executed_actions
    
    async def _should_execute_rule(self, rule: RemediationRule, events: List[Event], anomalies: List[AnomalyResult] = None, correlations: List[Dict[str, Any]] = None) -> bool:
        """Verifica se uma regra deve ser executada"""
        try:
            # Verificar cooldown
            if not self._check_cooldown(rule):
                return False
            
            # Verificar limite de execuções
            if not self._check_execution_limit(rule):
                return False
            
            # Verificar condições
            return await self._evaluate_conditions(rule.conditions, events, anomalies, correlations)
            
        except Exception as e:
            logger.error(f"Erro ao verificar regra {rule.id}: {str(e)}")
            return False
    
    def _check_cooldown(self, rule: RemediationRule) -> bool:
        """Verifica se a regra está em cooldown"""
        recent_actions = [
            action for action in self.executed_actions
            if action.rule_id == rule.id and 
            action.started_at > datetime.now() - timedelta(minutes=rule.cooldown_minutes)
        ]
        
        return len(recent_actions) == 0
    
    def _check_execution_limit(self, rule: RemediationRule) -> bool:
        """Verifica se a regra atingiu o limite de execuções"""
        total_executions = len([
            action for action in self.executed_actions
            if action.rule_id == rule.id
        ])
        
        return total_executions < rule.max_executions
    
    async def _evaluate_conditions(self, conditions: Dict[str, Any], events: List[Event], anomalies: List[AnomalyResult] = None, correlations: List[Dict[str, Any]] = None) -> bool:
        """Avalia condições de uma regra"""
        try:
            # Condições baseadas em eventos
            if 'event_type' in conditions:
                matching_events = [
                    event for event in events
                    if event.type.value == conditions['event_type']
                ]
                
                if not matching_events:
                    return False
                
                # Verificar métricas específicas
                if 'metric_name' in conditions and 'threshold' in conditions:
                    metric_events = [
                        event for event in matching_events
                        if event.type == EventType.SYSTEM_METRIC and
                        'metric_name' in event.data and
                        event.data['metric_name'] == conditions['metric_name']
                    ]
                    
                    if not metric_events:
                        return False
                    
                    # Verificar se algum evento excede o threshold
                    threshold = conditions['threshold']
                    high_metric_events = [
                        event for event in metric_events
                        if 'value' in event.data and event.data['value'] > threshold
                    ]
                    
                    if not high_metric_events:
                        return False
                    
                    # Verificar duração se especificada
                    if 'duration_minutes' in conditions:
                        duration = conditions['duration_minutes']
                        cutoff_time = datetime.now() - timedelta(minutes=duration)
                        
                        recent_high_events = [
                            event for event in high_metric_events
                            if event.timestamp > cutoff_time
                        ]
                        
                        if len(recent_high_events) < 2:  # Mínimo 2 eventos recentes
                            return False
                
                # Verificar tempo de execução para queries
                if 'execution_time_threshold' in conditions:
                    slow_queries = [
                        event for event in matching_events
                        if event.type == EventType.DATABASE_QUERY and
                        'execution_time' in event.data and
                        event.data['execution_time'] > conditions['execution_time_threshold']
                    ]
                    
                    if not slow_queries:
                        return False
                    
                    # Verificar frequência se especificada
                    if 'frequency_threshold' in conditions:
                        if len(slow_queries) < conditions['frequency_threshold']:
                            return False
                
                # Verificar padrões de erro
                if 'error_pattern' in conditions:
                    error_events = [
                        event for event in matching_events
                        if event.type == EventType.ERROR_EVENT and
                        'error' in event.data and
                        conditions['error_pattern'].lower() in event.data['error'].lower()
                    ]
                    
                    if not error_events:
                        return False
                    
                    # Verificar severidade
                    if 'severity' in conditions:
                        severity_events = [
                            event for event in error_events
                            if event.severity.value == conditions['severity']
                        ]
                        
                        if not severity_events:
                            return False
                        
                        # Verificar frequência
                        if 'frequency_threshold' in conditions:
                            if len(severity_events) < conditions['frequency_threshold']:
                                return False
                
                # Verificar eventos de segurança
                if 'attack_type' in conditions:
                    security_events = [
                        event for event in matching_events
                        if event.type == EventType.SECURITY_EVENT
                    ]
                    
                    if not security_events:
                        return False
                    
                    # Verificar tipo de ataque
                    attack_events = [
                        event for event in security_events
                        if any(attack_type in str(event.data).lower() for attack_type in conditions['attack_type'])
                    ]
                    
                    if not attack_events:
                        return False
            
            # Condições baseadas em anomalias
            if anomalies and 'anomaly_threshold' in conditions:
                high_anomaly_score_events = [
                    anomaly for anomaly in anomalies
                    if anomaly.score < conditions['anomaly_threshold']
                ]
                
                if not high_anomaly_score_events:
                    return False
            
            # Condições baseadas em correlações
            if correlations and 'correlation_threshold' in conditions:
                high_correlation_events = [
                    corr for corr in correlations
                    if len(corr.get('events', [])) >= conditions['correlation_threshold']
                ]
                
                if not high_correlation_events:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao avaliar condições: {str(e)}")
            return False
    
    async def _execute_rule_actions(self, rule: RemediationRule, events: List[Event]) -> List[RemediationAction]:
        """Executa ações de uma regra"""
        executed_actions = []
        
        for action_config in rule.actions:
            try:
                action = RemediationAction(
                    id=f"action_{int(time.time())}_{rule.id}",
                    rule_id=rule.id,
                    action_type=ActionType(action_config['type']),
                    status=ActionStatus.PENDING,
                    target=action_config['target'],
                    parameters=action_config.get('parameters', {}),
                    started_at=datetime.now(),
                    completed_at=None,
                    result=None,
                    error_message=None,
                    execution_time=None
                )
                
                # Executar ação
                success = await self._execute_action(action)
                
                if success:
                    action.status = ActionStatus.SUCCESS
                    logger.info(f"Ação {action.id} executada com sucesso")
                else:
                    action.status = ActionStatus.FAILED
                    logger.error(f"Ação {action.id} falhou")
                
                action.completed_at = datetime.now()
                action.execution_time = (action.completed_at - action.started_at).total_seconds()
                
                executed_actions.append(action)
                self.executed_actions.append(action)
                
            except Exception as e:
                logger.error(f"Erro ao executar ação da regra {rule.id}: {str(e)}")
                action.error_message = str(e)
                action.status = ActionStatus.FAILED
                action.completed_at = datetime.now()
                executed_actions.append(action)
                self.executed_actions.append(action)
        
        return executed_actions
    
    async def _execute_action(self, action: RemediationAction) -> bool:
        """Executa uma ação específica"""
        try:
            action.status = ActionStatus.RUNNING
            
            if action.action_type == ActionType.RESTART_SERVICE:
                return await self._restart_service(action)
            elif action.action_type == ActionType.SCALE_UP:
                return await self._scale_up(action)
            elif action.action_type == ActionType.SCALE_DOWN:
                return await self._scale_down(action)
            elif action.action_type == ActionType.CLEAR_CACHE:
                return await self._clear_cache(action)
            elif action.action_type == ActionType.OPTIMIZE_QUERY:
                return await self._optimize_query(action)
            elif action.action_type == ActionType.BLOCK_IP:
                return await self._block_ip(action)
            elif action.action_type == ActionType.SEND_ALERT:
                return await self._send_alert(action)
            elif action.action_type == ActionType.ROLLBACK:
                return await self._rollback(action)
            elif action.action_type == ActionType.CUSTOM_SCRIPT:
                return await self._execute_custom_script(action)
            else:
                logger.warning(f"Tipo de ação não implementado: {action.action_type}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao executar ação {action.id}: {str(e)}")
            action.error_message = str(e)
            return False
    
    async def _restart_service(self, action: RemediationAction) -> bool:
        """Reinicia um serviço"""
        try:
            service_name = action.parameters.get('service_name', 'unknown')
            restart_type = action.parameters.get('restart_type', 'graceful')
            timeout = action.parameters.get('timeout', 60)
            
            # Simular reinicialização de serviço
            logger.info(f"Reiniciando serviço {service_name} ({restart_type})")
            await asyncio.sleep(2)  # Simular tempo de execução
            
            action.result = {
                'service_name': service_name,
                'restart_type': restart_type,
                'status': 'restarted',
                'timestamp': datetime.now().isoformat()
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao reiniciar serviço: {str(e)}")
            return False
    
    async def _scale_up(self, action: RemediationAction) -> bool:
        """Escala horizontalmente um serviço"""
        try:
            target = action.parameters.get('target', 'unknown')
            replicas = action.parameters.get('replicas', 1)
            resource_type = action.parameters.get('resource_type', 'cpu')
            
            # Simular scale up
            logger.info(f"Escalando {target} para {replicas} réplicas")
            await asyncio.sleep(3)  # Simular tempo de execução
            
            action.result = {
                'target': target,
                'replicas': replicas,
                'resource_type': resource_type,
                'status': 'scaled_up',
                'timestamp': datetime.now().isoformat()
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao escalar serviço: {str(e)}")
            return False
    
    async def _scale_down(self, action: RemediationAction) -> bool:
        """Escala horizontalmente um serviço para baixo"""
        try:
            target = action.parameters.get('target', 'unknown')
            replicas = action.parameters.get('replicas', 1)
            
            # Simular scale down
            logger.info(f"Reduzindo {target} para {replicas} réplicas")
            await asyncio.sleep(2)  # Simular tempo de execução
            
            action.result = {
                'target': target,
                'replicas': replicas,
                'status': 'scaled_down',
                'timestamp': datetime.now().isoformat()
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao reduzir escala: {str(e)}")
            return False
    
    async def _clear_cache(self, action: RemediationAction) -> bool:
        """Limpa cache"""
        try:
            cache_type = action.parameters.get('cache_type', 'redis')
            clear_pattern = action.parameters.get('clear_pattern', '*')
            preserve_critical = action.parameters.get('preserve_critical', True)
            
            # Simular limpeza de cache
            logger.info(f"Limpando cache {cache_type} com padrão {clear_pattern}")
            await asyncio.sleep(1)  # Simular tempo de execução
            
            action.result = {
                'cache_type': cache_type,
                'clear_pattern': clear_pattern,
                'preserve_critical': preserve_critical,
                'status': 'cleared',
                'timestamp': datetime.now().isoformat()
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {str(e)}")
            return False
    
    async def _optimize_query(self, action: RemediationAction) -> bool:
        """Otimiza queries"""
        try:
            query_pattern = action.parameters.get('query_pattern', 'SELECT')
            optimization_type = action.parameters.get('optimization_type', 'index_suggestion')
            max_execution_time = action.parameters.get('max_execution_time', 1000)
            
            # Simular otimização de query
            logger.info(f"Otimizando queries com padrão {query_pattern}")
            await asyncio.sleep(2)  # Simular tempo de execução
            
            action.result = {
                'query_pattern': query_pattern,
                'optimization_type': optimization_type,
                'max_execution_time': max_execution_time,
                'status': 'optimized',
                'timestamp': datetime.now().isoformat()
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao otimizar query: {str(e)}")
            return False
    
    async def _block_ip(self, action: RemediationAction) -> bool:
        """Bloqueia IP"""
        try:
            block_duration = action.parameters.get('block_duration', 3600)
            block_type = action.parameters.get('block_type', 'ip')
            reason = action.parameters.get('reason', 'security_attack')
            
            # Simular bloqueio de IP
            logger.info(f"Bloqueando IP por {block_duration}s - {reason}")
            await asyncio.sleep(1)  # Simular tempo de execução
            
            action.result = {
                'block_duration': block_duration,
                'block_type': block_type,
                'reason': reason,
                'status': 'blocked',
                'timestamp': datetime.now().isoformat()
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao bloquear IP: {str(e)}")
            return False
    
    async def _send_alert(self, action: RemediationAction) -> bool:
        """Envia alerta"""
        try:
            alert_type = action.parameters.get('alert_type', 'general')
            priority = action.parameters.get('priority', 'medium')
            channels = action.parameters.get('channels', ['slack'])
            
            # Simular envio de alerta
            logger.info(f"Enviando alerta {alert_type} ({priority}) via {channels}")
            await asyncio.sleep(1)  # Simular tempo de execução
            
            action.result = {
                'alert_type': alert_type,
                'priority': priority,
                'channels': channels,
                'status': 'sent',
                'timestamp': datetime.now().isoformat()
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar alerta: {str(e)}")
            return False
    
    async def _rollback(self, action: RemediationAction) -> bool:
        """Executa rollback"""
        try:
            rollback_target = action.parameters.get('target', 'unknown')
            rollback_version = action.parameters.get('version', 'previous')
            
            # Simular rollback
            logger.info(f"Executando rollback de {rollback_target} para versão {rollback_version}")
            await asyncio.sleep(5)  # Simular tempo de execução
            
            action.result = {
                'target': rollback_target,
                'version': rollback_version,
                'status': 'rolled_back',
                'timestamp': datetime.now().isoformat()
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao executar rollback: {str(e)}")
            return False
    
    async def _execute_custom_script(self, action: RemediationAction) -> bool:
        """Executa script customizado"""
        try:
            script_path = action.parameters.get('script_path', '')
            script_args = action.parameters.get('args', [])
            
            # Simular execução de script
            logger.info(f"Executando script customizado: {script_path}")
            await asyncio.sleep(3)  # Simular tempo de execução
            
            action.result = {
                'script_path': script_path,
                'args': script_args,
                'status': 'executed',
                'timestamp': datetime.now().isoformat()
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao executar script customizado: {str(e)}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema de auto-remediação"""
        total_actions = len(self.executed_actions)
        successful_actions = len([a for a in self.executed_actions if a.status == ActionStatus.SUCCESS])
        failed_actions = len([a for a in self.executed_actions if a.status == ActionStatus.FAILED])
        
        success_rate = successful_actions / total_actions if total_actions > 0 else 0.0
        
        return {
            'total_actions': total_actions,
            'successful_actions': successful_actions,
            'failed_actions': failed_actions,
            'success_rate': success_rate,
            'enabled_rules': len([r for r in self.rules if r.enabled]),
            'total_rules': len(self.rules),
            'is_enabled': self.is_enabled,
            'max_concurrent_actions': self.max_concurrent_actions,
            'action_timeout': self.action_timeout
        }
    
    def add_rule(self, rule: RemediationRule):
        """Adiciona uma nova regra"""
        self.rules.append(rule)
        logger.info(f"Nova regra adicionada: {rule.id}")
    
    def update_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """Atualiza uma regra existente"""
        for rule in self.rules:
            if rule.id == rule_id:
                for key, value in updates.items():
                    if hasattr(rule, key):
                        setattr(rule, key, value)
                rule.updated_at = datetime.now()
                logger.info(f"Regra atualizada: {rule_id}")
                return True
        return False
    
    def delete_rule(self, rule_id: str) -> bool:
        """Remove uma regra"""
        for i, rule in enumerate(self.rules):
            if rule.id == rule_id:
                del self.rules[i]
                logger.info(f"Regra removida: {rule_id}")
                return True
        return False 