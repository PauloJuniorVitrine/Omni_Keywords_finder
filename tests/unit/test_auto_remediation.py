"""
Testes Unitários - Sistema de Automação de Respostas
Testes abrangentes para o AutoRemediationEngine

Tracing ID: TEST_AUTO_REMEDIATION_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: 🟡 ALTO - Testes de Automação de Respostas

Baseado no código real do sistema Omni Keywords Finder
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Dict, Any

from infrastructure.aiops.automation.auto_remediation import (
    AutoRemediationEngine,
    RemediationRule,
    RemediationAction,
    ActionType,
    ActionStatus
)
from infrastructure.intelligent_collector import Event, EventType, EventSeverity
from infrastructure.aiops.ml_models.anomaly_detector import AnomalyResult, AnomalyType

class TestAutoRemediationEngine:
    """Testes para o AutoRemediationEngine"""
    
    @pytest.fixture
    def engine(self):
        """Fixture para criar engine de teste"""
        config = {
            'enabled': True,
            'max_concurrent_actions': 3,
            'action_timeout': 60,
            'success_rate_threshold': 0.8
        }
        return AutoRemediationEngine(config)
    
    @pytest.fixture
    def sample_events(self):
        """Fixture para eventos de teste baseados no sistema real"""
        base_time = datetime.now()
        
        return [
            # Evento de CPU alto
            Event(
                id="cpu_high_001",
                type=EventType.SYSTEM_METRIC,
                severity=EventSeverity.HIGH,
                timestamp=base_time,
                source="omni_keywords_finder_app",
                data={
                    'metric_name': 'cpu_usage',
                    'value': 90.5,
                    'unit': 'percent'
                }
            ),
            # Evento de query lenta
            Event(
                id="slow_query_001",
                type=EventType.DATABASE_QUERY,
                severity=EventSeverity.MEDIUM,
                timestamp=base_time,
                source="database",
                data={
                    'query': 'SELECT * FROM keywords WHERE domain = %s',
                    'execution_time': 7500,  # 7.5s
                    'rows_affected': 1500
                }
            ),
            # Evento de erro de conexão
            Event(
                id="connection_error_001",
                type=EventType.ERROR_EVENT,
                severity=EventSeverity.HIGH,
                timestamp=base_time,
                source="database_service",
                data={
                    'error': 'Connection timeout to database',
                    'error_code': 'DB_CONN_TIMEOUT',
                    'retry_count': 3
                }
            ),
            # Evento de cache cheio
            Event(
                id="cache_full_001",
                type=EventType.SYSTEM_METRIC,
                severity=EventSeverity.MEDIUM,
                timestamp=base_time,
                source="redis_cache",
                data={
                    'metric_name': 'cache_usage',
                    'value': 95.2,
                    'unit': 'percent'
                }
            ),
            # Evento de segurança
            Event(
                id="security_attack_001",
                type=EventType.SECURITY_EVENT,
                severity=EventSeverity.CRITICAL,
                timestamp=base_time,
                source="firewall",
                data={
                    'attack_type': 'sql_injection',
                    'source_ip': '192.168.1.100',
                    'target_endpoint': '/api/keywords/search'
                }
            )
        ]
    
    @pytest.fixture
    def sample_anomalies(self):
        """Fixture para anomalias de teste"""
        return [
            AnomalyResult(
                id="anomaly_001",
                event_id="cpu_high_001",
                anomaly_type=AnomalyType.PERFORMANCE,
                score=0.95,
                confidence=0.88,
                detected_at=datetime.now(),
                description="CPU usage anomaly detected"
            )
        ]
    
    @pytest.fixture
    def sample_correlations(self):
        """Fixture para correlações de teste"""
        return [
            {
                'id': 'correlation_001',
                'events': ['cpu_high_001', 'slow_query_001'],
                'confidence': 0.85,
                'pattern': 'performance_degradation'
            }
        ]
    
    def test_engine_initialization(self, engine):
        """Testa inicialização do engine"""
        assert engine.is_enabled is True
        assert engine.max_concurrent_actions == 3
        assert engine.action_timeout == 60
        assert engine.success_rate_threshold == 0.8
        assert len(engine.rules) > 0  # Deve ter regras padrão
    
    def test_default_rules_creation(self, engine):
        """Testa criação das regras padrão"""
        rule_ids = [rule.id for rule in engine.rules]
        
        # Verificar se as regras padrão foram criadas
        assert 'cpu_high_scale_up' in rule_ids
        assert 'slow_query_optimize' in rule_ids
        assert 'connection_error_restart' in rule_ids
        assert 'cache_full_clear' in rule_ids
        assert 'security_attack_block' in rule_ids
        
        # Verificar se todas as regras estão habilitadas
        for rule in engine.rules:
            assert rule.enabled is True
            assert rule.priority > 0
            assert rule.max_executions > 0
            assert rule.cooldown_minutes > 0
    
    def test_rule_conditions_structure(self, engine):
        """Testa estrutura das condições das regras"""
        cpu_rule = next(rule for rule in engine.rules if rule.id == 'cpu_high_scale_up')
        
        assert 'event_type' in cpu_rule.conditions
        assert 'metric_name' in cpu_rule.conditions
        assert 'threshold' in cpu_rule.conditions
        assert 'duration_minutes' in cpu_rule.conditions
        
        assert cpu_rule.conditions['event_type'] == EventType.SYSTEM_METRIC.value
        assert cpu_rule.conditions['metric_name'] == 'cpu_usage'
        assert cpu_rule.conditions['threshold'] == 85.0
        assert cpu_rule.conditions['duration_minutes'] == 5
    
    def test_rule_actions_structure(self, engine):
        """Testa estrutura das ações das regras"""
        cpu_rule = next(rule for rule in engine.rules if rule.id == 'cpu_high_scale_up')
        
        assert len(cpu_rule.actions) > 0
        action = cpu_rule.actions[0]
        
        assert 'type' in action
        assert 'target' in action
        assert 'parameters' in action
        
        assert action['type'] == ActionType.SCALE_UP.value
        assert action['target'] == 'omni_keywords_finder_app'
        assert 'replicas' in action['parameters']
    
    @pytest.mark.asyncio
    async def test_cooldown_check(self, engine):
        """Testa verificação de cooldown"""
        rule = engine.rules[0]
        
        # Deve permitir execução inicialmente
        assert engine._check_cooldown(rule) is True
        
        # Simular ação executada recentemente
        action = RemediationAction(
            id="test_action",
            rule_id=rule.id,
            action_type=ActionType.SCALE_UP,
            status=ActionStatus.SUCCESS,
            target="test",
            parameters={},
            started_at=datetime.now() - timedelta(minutes=5),  # Dentro do cooldown
            completed_at=datetime.now(),
            result={},
            error_message=None,
            execution_time=10.0
        )
        engine.executed_actions.append(action)
        
        # Deve bloquear execução durante cooldown
        assert engine._check_cooldown(rule) is False
        
        # Limpar ações para outros testes
        engine.executed_actions.clear()
    
    @pytest.mark.asyncio
    async def test_execution_limit_check(self, engine):
        """Testa verificação de limite de execuções"""
        rule = engine.rules[0]
        
        # Deve permitir execução inicialmente
        assert engine._check_execution_limit(rule) is True
        
        # Simular ações executadas até o limite
        for i in range(rule.max_executions):
            action = RemediationAction(
                id=f"test_action_{i}",
                rule_id=rule.id,
                action_type=ActionType.SCALE_UP,
                status=ActionStatus.SUCCESS,
                target="test",
                parameters={},
                started_at=datetime.now(),
                completed_at=datetime.now(),
                result={},
                error_message=None,
                execution_time=10.0
            )
            engine.executed_actions.append(action)
        
        # Deve bloquear execução após atingir limite
        assert engine._check_execution_limit(rule) is False
        
        # Limpar ações para outros testes
        engine.executed_actions.clear()
    
    @pytest.mark.asyncio
    async def test_cpu_high_condition_evaluation(self, engine, sample_events):
        """Testa avaliação de condição de CPU alto"""
        cpu_events = [event for event in sample_events if event.type == EventType.SYSTEM_METRIC and event.data.get('metric_name') == 'cpu_usage']
        
        conditions = {
            'event_type': EventType.SYSTEM_METRIC.value,
            'metric_name': 'cpu_usage',
            'threshold': 85.0,
            'duration_minutes': 5
        }
        
        # Deve retornar True para eventos de CPU alto
        result = await engine._evaluate_conditions(conditions, cpu_events)
        assert result is True
        
        # Deve retornar False para threshold muito alto
        conditions['threshold'] = 95.0
        result = await engine._evaluate_conditions(conditions, cpu_events)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_slow_query_condition_evaluation(self, engine, sample_events):
        """Testa avaliação de condição de query lenta"""
        query_events = [event for event in sample_events if event.type == EventType.DATABASE_QUERY]
        
        conditions = {
            'event_type': EventType.DATABASE_QUERY.value,
            'execution_time_threshold': 5000,  # 5s
            'frequency_threshold': 1
        }
        
        # Deve retornar True para queries lentas
        result = await engine._evaluate_conditions(conditions, query_events)
        assert result is True
        
        # Deve retornar False para threshold muito baixo
        conditions['execution_time_threshold'] = 10000  # 10s
        result = await engine._evaluate_conditions(conditions, query_events)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_connection_error_condition_evaluation(self, engine, sample_events):
        """Testa avaliação de condição de erro de conexão"""
        error_events = [event for event in sample_events if event.type == EventType.ERROR_EVENT]
        
        conditions = {
            'event_type': EventType.ERROR_EVENT.value,
            'error_pattern': 'connection',
            'severity': EventSeverity.HIGH.value,
            'frequency_threshold': 1
        }
        
        # Deve retornar True para erros de conexão
        result = await engine._evaluate_conditions(conditions, error_events)
        assert result is True
        
        # Deve retornar False para padrão inexistente
        conditions['error_pattern'] = 'nonexistent'
        result = await engine._evaluate_conditions(conditions, error_events)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_security_attack_condition_evaluation(self, engine, sample_events):
        """Testa avaliação de condição de ataque de segurança"""
        security_events = [event for event in sample_events if event.type == EventType.SECURITY_EVENT]
        
        conditions = {
            'event_type': EventType.SECURITY_EVENT.value,
            'attack_type': ['sql_injection', 'xss'],
            'severity': EventSeverity.CRITICAL.value
        }
        
        # Deve retornar True para ataques de segurança
        result = await engine._evaluate_conditions(conditions, security_events)
        assert result is True
        
        # Deve retornar False para tipos de ataque inexistentes
        conditions['attack_type'] = ['nonexistent_attack']
        result = await engine._evaluate_conditions(conditions, security_events)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_restart_service_action(self, engine):
        """Testa ação de reiniciar serviço"""
        action = RemediationAction(
            id="test_restart",
            rule_id="test_rule",
            action_type=ActionType.RESTART_SERVICE,
            status=ActionStatus.PENDING,
            target="database_service",
            parameters={
                'service_name': 'postgresql',
                'restart_type': 'graceful',
                'timeout': 60
            },
            started_at=datetime.now(),
            completed_at=None,
            result=None,
            error_message=None,
            execution_time=None
        )
        
        # Executar ação
        success = await engine._restart_service(action)
        
        assert success is True
        assert action.status == ActionStatus.SUCCESS
        assert action.result is not None
        assert 'service_name' in action.result
        assert action.result['service_name'] == 'postgresql'
    
    @pytest.mark.asyncio
    async def test_scale_up_action(self, engine):
        """Testa ação de scale up"""
        action = RemediationAction(
            id="test_scale_up",
            rule_id="test_rule",
            action_type=ActionType.SCALE_UP,
            status=ActionStatus.PENDING,
            target="omni_keywords_finder_app",
            parameters={
                'replicas': 3,
                'resource_type': 'cpu',
                'increment': 1
            },
            started_at=datetime.now(),
            completed_at=None,
            result=None,
            error_message=None,
            execution_time=None
        )
        
        # Executar ação
        success = await engine._scale_up(action)
        
        assert success is True
        assert action.status == ActionStatus.SUCCESS
        assert action.result is not None
        assert 'target' in action.result
        assert action.result['target'] == 'omni_keywords_finder_app'
    
    @pytest.mark.asyncio
    async def test_clear_cache_action(self, engine):
        """Testa ação de limpar cache"""
        action = RemediationAction(
            id="test_clear_cache",
            rule_id="test_rule",
            action_type=ActionType.CLEAR_CACHE,
            status=ActionStatus.PENDING,
            target="redis_cache",
            parameters={
                'cache_type': 'redis',
                'clear_pattern': 'temp:*',
                'preserve_critical': True
            },
            started_at=datetime.now(),
            completed_at=None,
            result=None,
            error_message=None,
            execution_time=None
        )
        
        # Executar ação
        success = await engine._clear_cache(action)
        
        assert success is True
        assert action.status == ActionStatus.SUCCESS
        assert action.result is not None
        assert 'cache_type' in action.result
        assert action.result['cache_type'] == 'redis'
    
    @pytest.mark.asyncio
    async def test_block_ip_action(self, engine):
        """Testa ação de bloquear IP"""
        action = RemediationAction(
            id="test_block_ip",
            rule_id="test_rule",
            action_type=ActionType.BLOCK_IP,
            status=ActionStatus.PENDING,
            target="firewall",
            parameters={
                'block_duration': 3600,
                'block_type': 'ip',
                'reason': 'security_attack'
            },
            started_at=datetime.now(),
            completed_at=None,
            result=None,
            error_message=None,
            execution_time=None
        )
        
        # Executar ação
        success = await engine._block_ip(action)
        
        assert success is True
        assert action.status == ActionStatus.SUCCESS
        assert action.result is not None
        assert 'block_duration' in action.result
        assert action.result['block_duration'] == 3600
    
    @pytest.mark.asyncio
    async def test_send_alert_action(self, engine):
        """Testa ação de enviar alerta"""
        action = RemediationAction(
            id="test_send_alert",
            rule_id="test_rule",
            action_type=ActionType.SEND_ALERT,
            status=ActionStatus.PENDING,
            target="security_team",
            parameters={
                'alert_type': 'security_incident',
                'priority': 'high',
                'channels': ['slack', 'email']
            },
            started_at=datetime.now(),
            completed_at=None,
            result=None,
            error_message=None,
            execution_time=None
        )
        
        # Executar ação
        success = await engine._send_alert(action)
        
        assert success is True
        assert action.status == ActionStatus.SUCCESS
        assert action.result is not None
        assert 'alert_type' in action.result
        assert action.result['alert_type'] == 'security_incident'
    
    @pytest.mark.asyncio
    async def test_process_events_with_cpu_high(self, engine, sample_events):
        """Testa processamento de eventos com CPU alto"""
        cpu_events = [event for event in sample_events if event.data.get('metric_name') == 'cpu_usage']
        
        # Processar eventos
        actions = await engine.process_events(cpu_events)
        
        # Deve executar ações para CPU alto
        assert len(actions) > 0
        
        # Verificar se a ação foi executada
        cpu_action = next((action for action in actions if action.action_type == ActionType.SCALE_UP), None)
        assert cpu_action is not None
        assert cpu_action.status == ActionStatus.SUCCESS
    
    @pytest.mark.asyncio
    async def test_process_events_with_slow_queries(self, engine, sample_events):
        """Testa processamento de eventos com queries lentas"""
        query_events = [event for event in sample_events if event.type == EventType.DATABASE_QUERY]
        
        # Processar eventos
        actions = await engine.process_events(query_events)
        
        # Deve executar ações para queries lentas
        assert len(actions) > 0
        
        # Verificar se a ação foi executada
        query_action = next((action for action in actions if action.action_type == ActionType.OPTIMIZE_QUERY), None)
        assert query_action is not None
        assert query_action.status == ActionStatus.SUCCESS
    
    @pytest.mark.asyncio
    async def test_process_events_with_security_attack(self, engine, sample_events):
        """Testa processamento de eventos com ataque de segurança"""
        security_events = [event for event in sample_events if event.type == EventType.SECURITY_EVENT]
        
        # Processar eventos
        actions = await engine.process_events(security_events)
        
        # Deve executar ações para ataques de segurança
        assert len(actions) > 0
        
        # Verificar se as ações foram executadas
        block_action = next((action for action in actions if action.action_type == ActionType.BLOCK_IP), None)
        alert_action = next((action for action in actions if action.action_type == ActionType.SEND_ALERT), None)
        
        assert block_action is not None
        assert alert_action is not None
        assert block_action.status == ActionStatus.SUCCESS
        assert alert_action.status == ActionStatus.SUCCESS
    
    @pytest.mark.asyncio
    async def test_process_events_with_anomalies(self, engine, sample_events, sample_anomalies):
        """Testa processamento de eventos com anomalias"""
        # Processar eventos com anomalias
        actions = await engine.process_events(sample_events, sample_anomalies)
        
        # Deve executar ações baseadas em anomalias
        assert len(actions) > 0
    
    @pytest.mark.asyncio
    async def test_process_events_with_correlations(self, engine, sample_events, sample_correlations):
        """Testa processamento de eventos com correlações"""
        # Processar eventos com correlações
        actions = await engine.process_events(sample_events, correlations=sample_correlations)
        
        # Deve executar ações baseadas em correlações
        assert len(actions) > 0
    
    @pytest.mark.asyncio
    async def test_disabled_engine(self):
        """Testa engine desabilitado"""
        config = {'enabled': False}
        disabled_engine = AutoRemediationEngine(config)
        
        events = [Mock()]
        actions = await disabled_engine.process_events(events)
        
        assert len(actions) == 0
    
    @pytest.mark.asyncio
    async def test_max_concurrent_actions_limit(self, engine, sample_events):
        """Testa limite de ações concorrentes"""
        engine.max_concurrent_actions = 1
        
        # Processar eventos que gerariam múltiplas ações
        actions = await engine.process_events(sample_events)
        
        # Deve respeitar o limite
        assert len(actions) <= engine.max_concurrent_actions
    
    def test_get_statistics(self, engine):
        """Testa obtenção de estatísticas"""
        stats = engine.get_statistics()
        
        assert 'total_actions' in stats
        assert 'successful_actions' in stats
        assert 'failed_actions' in stats
        assert 'success_rate' in stats
        assert 'enabled_rules' in stats
        assert 'total_rules' in stats
        assert 'is_enabled' in stats
        assert 'max_concurrent_actions' in stats
        assert 'action_timeout' in stats
        
        assert stats['total_actions'] == 0  # Inicialmente vazio
        assert stats['success_rate'] == 0.0
        assert stats['is_enabled'] is True
        assert stats['max_concurrent_actions'] == 3
    
    def test_add_rule(self, engine):
        """Testa adição de nova regra"""
        initial_count = len(engine.rules)
        
        new_rule = RemediationRule(
            id="test_rule",
            name="Test Rule",
            description="Test rule for unit testing",
            conditions={'test': True},
            actions=[{'type': 'test'}],
            priority=1,
            enabled=True,
            max_executions=1,
            cooldown_minutes=5,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        engine.add_rule(new_rule)
        
        assert len(engine.rules) == initial_count + 1
        assert any(rule.id == "test_rule" for rule in engine.rules)
    
    def test_update_rule(self, engine):
        """Testa atualização de regra existente"""
        rule = engine.rules[0]
        original_name = rule.name
        
        updates = {'name': 'Updated Rule Name'}
        success = engine.update_rule(rule.id, updates)
        
        assert success is True
        assert rule.name == 'Updated Rule Name'
        assert rule.name != original_name
    
    def test_delete_rule(self, engine):
        """Testa remoção de regra"""
        initial_count = len(engine.rules)
        rule_id = engine.rules[0].id
        
        success = engine.delete_rule(rule_id)
        
        assert success is True
        assert len(engine.rules) == initial_count - 1
        assert not any(rule.id == rule_id for rule in engine.rules)
    
    def test_delete_nonexistent_rule(self, engine):
        """Testa remoção de regra inexistente"""
        initial_count = len(engine.rules)
        
        success = engine.delete_rule("nonexistent_rule")
        
        assert success is False
        assert len(engine.rules) == initial_count
    
    @pytest.mark.asyncio
    async def test_action_timeout(self, engine):
        """Testa timeout de ações"""
        # Criar ação que simula timeout
        action = RemediationAction(
            id="timeout_test",
            rule_id="test_rule",
            action_type=ActionType.CUSTOM_SCRIPT,
            status=ActionStatus.PENDING,
            target="test",
            parameters={'script_path': '/slow/script'},
            started_at=datetime.now(),
            completed_at=None,
            result=None,
            error_message=None,
            execution_time=None
        )
        
        # Simular timeout
        with patch.object(engine, '_execute_custom_script', side_effect=asyncio.TimeoutError):
            success = await engine._execute_action(action)
            
            assert success is False
            assert action.status == ActionStatus.FAILED
            assert action.error_message is not None
    
    @pytest.mark.asyncio
    async def test_error_handling_in_action_execution(self, engine):
        """Testa tratamento de erros na execução de ações"""
        action = RemediationAction(
            id="error_test",
            rule_id="test_rule",
            action_type=ActionType.RESTART_SERVICE,
            status=ActionStatus.PENDING,
            target="test",
            parameters={},
            started_at=datetime.now(),
            completed_at=None,
            result=None,
            error_message=None,
            execution_time=None
        )
        
        # Simular erro na execução
        with patch.object(engine, '_restart_service', side_effect=Exception("Test error")):
            success = await engine._execute_action(action)
            
            assert success is False
            assert action.status == ActionStatus.FAILED
            assert action.error_message == "Test error"
    
    def test_rule_priority_ordering(self, engine):
        """Testa ordenação de regras por prioridade"""
        # Verificar se as regras estão ordenadas por prioridade (menor = mais alta)
        priorities = [rule.priority for rule in engine.rules]
        
        # Prioridades devem estar em ordem crescente (mais alta primeiro)
        assert priorities == sorted(priorities)
        
        # Verificar se há regras com prioridades diferentes
        assert len(set(priorities)) > 1
    
    @pytest.mark.asyncio
    async def test_multiple_events_same_rule(self, engine, sample_events):
        """Testa múltiplos eventos que ativam a mesma regra"""
        # Criar múltiplos eventos de CPU alto
        cpu_events = []
        for i in range(3):
            event = Event(
                id=f"cpu_high_{i}",
                type=EventType.SYSTEM_METRIC,
                severity=EventSeverity.HIGH,
                timestamp=datetime.now(),
                source="omni_keywords_finder_app",
                data={
                    'metric_name': 'cpu_usage',
                    'value': 90.0 + i,
                    'unit': 'percent'
                }
            )
            cpu_events.append(event)
        
        # Processar eventos
        actions = await engine.process_events(cpu_events)
        
        # Deve executar apenas uma ação por regra (evitar duplicação)
        scale_up_actions = [action for action in actions if action.action_type == ActionType.SCALE_UP]
        assert len(scale_up_actions) <= 1  # Máximo uma ação por regra
    
    @pytest.mark.asyncio
    async def test_rule_disabled(self, engine, sample_events):
        """Testa regra desabilitada"""
        # Desabilitar primeira regra
        engine.rules[0].enabled = False
        
        # Processar eventos
        actions = await engine.process_events(sample_events)
        
        # Não deve executar ações da regra desabilitada
        disabled_rule_actions = [action for action in actions if action.rule_id == engine.rules[0].id]
        assert len(disabled_rule_actions) == 0 