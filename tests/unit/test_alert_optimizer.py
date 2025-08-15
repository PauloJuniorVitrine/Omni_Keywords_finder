"""
Testes Unitários - Sistema de Otimização de Alertas
Testes abrangentes para o AlertOptimizer

Tracing ID: TEST_ALERT_OPTIMIZER_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: 🟡 ALTO - Testes de Otimização de Alertas

Baseado no código real do sistema Omni Keywords Finder
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Dict, Any

from infrastructure.aiops.automation.alert_optimizer import (
    AlertOptimizer,
    SuppressionRule,
    AlertGroup,
    OptimizedAlert,
    AlertStatus,
    SuppressionReason,
    GroupingStrategy
)
from infrastructure.intelligent_collector import Event, EventType, EventSeverity
from infrastructure.aiops.ml_models.anomaly_detector import AnomalyResult, AnomalyType

class TestAlertOptimizer:
    """Testes para o AlertOptimizer"""
    
    @pytest.fixture
    def optimizer(self):
        """Fixture para criar optimizer de teste"""
        config = {
            'enabled': True,
            'grouping_window_minutes': 5,
            'suppression_threshold': 0.8,
            'max_alerts_per_group': 10,
            'pattern_detection_window': 60
        }
        return AlertOptimizer(config)
    
    @pytest.fixture
    def sample_alerts(self):
        """Fixture para alertas de teste baseados no sistema real"""
        base_time = datetime.now()
        
        return [
            # Alerta de CPU alto
            {
                'id': 'cpu_high_001',
                'type': 'system_metric',
                'severity': EventSeverity.HIGH.value,
                'source': 'omni_keywords_finder_app',
                'message': 'CPU usage exceeded 90% threshold',
                'timestamp': base_time,
                'user_impact': True,
                'impact_type': 'performance_degradation',
                'affected_users': 150,
                'duration_minutes': 15
            },
            # Alerta de query lenta
            {
                'id': 'slow_query_001',
                'type': 'database_query',
                'severity': EventSeverity.MEDIUM.value,
                'source': 'database_service',
                'message': 'Query execution time exceeded 5 seconds',
                'timestamp': base_time,
                'user_impact': False,
                'impact_type': 'performance_degradation',
                'affected_users': 0,
                'duration_minutes': 5
            },
            # Alerta de erro de conexão
            {
                'id': 'connection_error_001',
                'type': 'error_event',
                'severity': EventSeverity.HIGH.value,
                'source': 'database_service',
                'message': 'Database connection timeout',
                'timestamp': base_time,
                'user_impact': True,
                'impact_type': 'service_outage',
                'affected_users': 500,
                'duration_minutes': 30
            },
            # Alerta de cache cheio
            {
                'id': 'cache_full_001',
                'type': 'system_metric',
                'severity': EventSeverity.MEDIUM.value,
                'source': 'redis_cache',
                'message': 'Cache usage exceeded 95%',
                'timestamp': base_time,
                'user_impact': False,
                'impact_type': 'performance_degradation',
                'affected_users': 0,
                'duration_minutes': 10
            },
            # Alerta de segurança
            {
                'id': 'security_attack_001',
                'type': 'security_event',
                'severity': EventSeverity.CRITICAL.value,
                'source': 'firewall',
                'message': 'SQL injection attempt detected',
                'timestamp': base_time,
                'user_impact': True,
                'impact_type': 'security_breach',
                'affected_users': 1000,
                'duration_minutes': 5
            },
            # Alerta de baixa severidade (deve ser suprimido)
            {
                'id': 'low_severity_001',
                'type': 'health_check',
                'severity': EventSeverity.LOW.value,
                'source': 'health_check_service',
                'message': 'Health check failed',
                'timestamp': base_time,
                'user_impact': False,
                'impact_type': 'unknown',
                'affected_users': 0,
                'duration_minutes': 1
            },
            # Alerta duplicado (deve ser suprimido)
            {
                'id': 'duplicate_001',
                'type': 'system_metric',
                'severity': EventSeverity.MEDIUM.value,
                'source': 'omni_keywords_finder_app',
                'message': 'CPU usage exceeded 90% threshold',
                'timestamp': base_time,
                'user_impact': True,
                'impact_type': 'performance_degradation',
                'affected_users': 150,
                'duration_minutes': 15
            }
        ]
    
    @pytest.fixture
    def sample_events(self):
        """Fixture para eventos de teste"""
        base_time = datetime.now()
        
        return [
            Event(
                id="event_001",
                type=EventType.SYSTEM_METRIC,
                severity=EventSeverity.HIGH,
                timestamp=base_time,
                source="omni_keywords_finder_app",
                data={'metric_name': 'cpu_usage', 'value': 95.0}
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
    
    def test_optimizer_initialization(self, optimizer):
        """Testa inicialização do optimizer"""
        assert optimizer.is_enabled is True
        assert optimizer.grouping_window_minutes == 5
        assert optimizer.suppression_threshold == 0.8
        assert optimizer.max_alerts_per_group == 10
        assert optimizer.pattern_detection_window == 60
        assert len(optimizer.suppression_rules) > 0  # Deve ter regras padrão
    
    def test_default_suppression_rules_creation(self, optimizer):
        """Testa criação das regras de supressão padrão"""
        rule_ids = [rule.id for rule in optimizer.suppression_rules]
        
        # Verificar se as regras padrão foram criadas
        assert 'low_severity_frequent' in rule_ids
        assert 'duplicate_alerts' in rule_ids
        assert 'maintenance_window' in rule_ids
        assert 'known_false_positives' in rule_ids
        assert 'frequent_patterns' in rule_ids
        
        # Verificar se todas as regras estão habilitadas
        for rule in optimizer.suppression_rules:
            assert rule.enabled is True
            assert rule.duration_minutes > 0
            assert rule.reason in SuppressionReason
    
    def test_suppression_rule_structure(self, optimizer):
        """Testa estrutura das regras de supressão"""
        low_severity_rule = next(rule for rule in optimizer.suppression_rules if rule.id == 'low_severity_frequent')
        
        assert 'severity' in low_severity_rule.conditions
        assert 'frequency_threshold' in low_severity_rule.conditions
        assert 'time_window_minutes' in low_severity_rule.conditions
        assert 'source_patterns' in low_severity_rule.conditions
        
        assert low_severity_rule.conditions['severity'] == EventSeverity.LOW.value
        assert low_severity_rule.conditions['frequency_threshold'] == 5
        assert low_severity_rule.conditions['time_window_minutes'] == 10
        assert low_severity_rule.reason == SuppressionReason.LOW_SEVERITY
    
    @pytest.mark.asyncio
    async def test_priority_score_calculation(self, optimizer, sample_alerts):
        """Testa cálculo de score de prioridade"""
        critical_alert = next(alert for alert in sample_alerts if alert['severity'] == EventSeverity.CRITICAL.value)
        low_alert = next(alert for alert in sample_alerts if alert['severity'] == EventSeverity.LOW.value)
        
        # Score de alerta crítico deve ser maior
        critical_score = optimizer._calculate_priority_score(critical_alert)
        low_score = optimizer._calculate_priority_score(low_alert)
        
        assert critical_score > low_score
        assert 0.0 <= critical_score <= 1.0
        assert 0.0 <= low_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_impact_score_calculation(self, optimizer, sample_alerts):
        """Testa cálculo de score de impacto"""
        security_alert = next(alert for alert in sample_alerts if alert['impact_type'] == 'security_breach')
        performance_alert = next(alert for alert in sample_alerts if alert['impact_type'] == 'performance_degradation')
        
        # Score de alerta de segurança deve ser maior
        security_score = optimizer._calculate_impact_score(security_alert)
        performance_score = optimizer._calculate_impact_score(performance_alert)
        
        assert security_score > performance_score
        assert 0.0 <= security_score <= 1.0
        assert 0.0 <= performance_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_alert_similarity_detection(self, optimizer, sample_alerts):
        """Testa detecção de similaridade entre alertas"""
        alert1 = sample_alerts[0]  # CPU high
        alert2 = sample_alerts[6]  # Duplicate
        
        # Alertas similares devem ser detectados
        similarity = optimizer._are_alerts_similar(alert1, alert2)
        assert similarity is True
        
        # Alertas diferentes devem ser detectados
        alert3 = sample_alerts[1]  # Slow query
        similarity = optimizer._are_alerts_similar(alert1, alert3)
        assert similarity is False
    
    @pytest.mark.asyncio
    async def test_similarity_score_calculation(self, optimizer, sample_alerts):
        """Testa cálculo de score de similaridade"""
        alert1 = sample_alerts[0]  # CPU high
        alert2 = sample_alerts[6]  # Duplicate
        
        # Score de similaridade deve ser alto para alertas similares
        similarity_score = optimizer._calculate_alert_similarity(alert1, alert2)
        assert similarity_score >= 0.8
        
        # Score de similaridade deve ser baixo para alertas diferentes
        alert3 = sample_alerts[1]  # Slow query
        similarity_score = optimizer._calculate_alert_similarity(alert1, alert3)
        assert similarity_score < 0.8
    
    @pytest.mark.asyncio
    async def test_maintenance_window_condition(self, optimizer):
        """Testa condição de janela de manutenção"""
        # Simular domingo às 3h da manhã
        with patch('infrastructure.aiops.automation.alert_optimizer.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 26, 3, 0, 0)  # Domingo 3h
            
            conditions = {
                'maintenance_windows': [
                    {'day': 'sunday', 'start': '02:00', 'end': '06:00'}
                ]
            }
            
            result = await optimizer._check_maintenance_window_condition(conditions)
            assert result is True
        
        # Simular segunda-feira às 3h da manhã (fora da janela)
        with patch('infrastructure.aiops.automation.alert_optimizer.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 27, 3, 0, 0)  # Segunda 3h
            
            conditions = {
                'maintenance_windows': [
                    {'day': 'sunday', 'start': '02:00', 'end': '06:00'}
                ]
            }
            
            result = await optimizer._check_maintenance_window_condition(conditions)
            assert result is False
    
    @pytest.mark.asyncio
    async def test_frequency_condition_check(self, optimizer, sample_alerts):
        """Testa verificação de condição de frequência"""
        alert = sample_alerts[0]
        
        # Simular alertas similares recentes
        for i in range(5):
            similar_alert = OptimizedAlert(
                id=f"similar_{i}",
                original_alert_id=f"similar_{i}",
                status=AlertStatus.ACTIVE,
                suppression_reason=None,
                group_id=None,
                priority_score=0.5,
                impact_score=0.3,
                created_at=datetime.now() - timedelta(minutes=5),
                updated_at=datetime.now(),
                metadata={'original_alert': alert}
            )
            optimizer.optimized_alerts[similar_alert.id] = similar_alert
        
        conditions = {
            'frequency_threshold': 5,
            'time_window_minutes': 10
        }
        
        result = await optimizer._check_frequency_condition(alert, conditions)
        assert result is True
        
        # Limpar para outros testes
        optimizer.optimized_alerts.clear()
    
    @pytest.mark.asyncio
    async def test_duplicate_condition_check(self, optimizer, sample_alerts):
        """Testa verificação de condição de duplicatas"""
        alert = sample_alerts[0]
        
        # Simular alertas duplicados recentes
        for i in range(3):
            duplicate_alert = OptimizedAlert(
                id=f"duplicate_{i}",
                original_alert_id=f"duplicate_{i}",
                status=AlertStatus.ACTIVE,
                suppression_reason=None,
                group_id=None,
                priority_score=0.5,
                impact_score=0.3,
                created_at=datetime.now() - timedelta(minutes=2),
                updated_at=datetime.now(),
                metadata={'original_alert': alert}
            )
            optimizer.optimized_alerts[duplicate_alert.id] = duplicate_alert
        
        conditions = {
            'duplicate_threshold': 3,
            'time_window_minutes': 5,
            'similarity_threshold': 0.9
        }
        
        result = await optimizer._check_duplicate_condition(alert, conditions)
        assert result is True
        
        # Limpar para outros testes
        optimizer.optimized_alerts.clear()
    
    @pytest.mark.asyncio
    async def test_pattern_frequency_condition_check(self, optimizer, sample_alerts):
        """Testa verificação de condição de frequência de padrões"""
        alert = sample_alerts[0]
        
        # Simular alertas com padrão similar recentes
        for i in range(10):
            pattern_alert = OptimizedAlert(
                id=f"pattern_{i}",
                original_alert_id=f"pattern_{i}",
                status=AlertStatus.ACTIVE,
                suppression_reason=None,
                group_id=None,
                priority_score=0.5,
                impact_score=0.3,
                created_at=datetime.now() - timedelta(minutes=20),
                updated_at=datetime.now(),
                metadata={'original_alert': {'type': 'performance_degradation'}}
            )
            optimizer.optimized_alerts[pattern_alert.id] = pattern_alert
        
        conditions = {
            'pattern_frequency_threshold': 10,
            'pattern_time_window_minutes': 30,
            'pattern_types': ['performance_degradation']
        }
        
        result = await optimizer._check_pattern_frequency_condition(alert, conditions)
        assert result is True
        
        # Limpar para outros testes
        optimizer.optimized_alerts.clear()
    
    @pytest.mark.asyncio
    async def test_suppression_rule_evaluation(self, optimizer, sample_alerts):
        """Testa avaliação de regras de supressão"""
        low_severity_alert = next(alert for alert in sample_alerts if alert['severity'] == EventSeverity.LOW.value)
        
        rule = next(rule for rule in optimizer.suppression_rules if rule.id == 'low_severity_frequent')
        
        # Simular alertas similares para ativar a regra
        for i in range(5):
            similar_alert = OptimizedAlert(
                id=f"similar_{i}",
                original_alert_id=f"similar_{i}",
                status=AlertStatus.ACTIVE,
                suppression_reason=None,
                group_id=None,
                priority_score=0.5,
                impact_score=0.3,
                created_at=datetime.now() - timedelta(minutes=5),
                updated_at=datetime.now(),
                metadata={'original_alert': low_severity_alert}
            )
            optimizer.optimized_alerts[similar_alert.id] = similar_alert
        
        result = await optimizer._evaluate_suppression_rule(rule, low_severity_alert, [], [])
        assert result is True
        
        # Limpar para outros testes
        optimizer.optimized_alerts.clear()
    
    @pytest.mark.asyncio
    async def test_single_alert_processing(self, optimizer, sample_alerts):
        """Testa processamento de alerta individual"""
        alert = sample_alerts[0]  # CPU high alert
        
        optimized_alert = await optimizer._process_single_alert(alert, [], [])
        
        assert optimized_alert is not None
        assert optimized_alert.original_alert_id == alert['id']
        assert optimized_alert.status == AlertStatus.ACTIVE
        assert optimized_alert.suppression_reason is None
        assert optimized_alert.group_id is None
        assert 0.0 <= optimized_alert.priority_score <= 1.0
        assert 0.0 <= optimized_alert.impact_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_alert_suppression(self, optimizer, sample_alerts):
        """Testa supressão de alertas"""
        low_severity_alert = next(alert for alert in sample_alerts if alert['severity'] == EventSeverity.LOW.value)
        
        # Simular alertas similares para ativar supressão
        for i in range(5):
            similar_alert = OptimizedAlert(
                id=f"similar_{i}",
                original_alert_id=f"similar_{i}",
                status=AlertStatus.ACTIVE,
                suppression_reason=None,
                group_id=None,
                priority_score=0.5,
                impact_score=0.3,
                created_at=datetime.now() - timedelta(minutes=5),
                updated_at=datetime.now(),
                metadata={'original_alert': low_severity_alert}
            )
            optimizer.optimized_alerts[similar_alert.id] = similar_alert
        
        optimized_alert = await optimizer._process_single_alert(low_severity_alert, [], [])
        
        assert optimized_alert.status == AlertStatus.SUPPRESSED
        assert optimized_alert.suppression_reason == SuppressionReason.LOW_SEVERITY
        
        # Limpar para outros testes
        optimizer.optimized_alerts.clear()
    
    @pytest.mark.asyncio
    async def test_group_by_source(self, optimizer, sample_alerts):
        """Testa agrupamento por fonte"""
        # Criar alertas otimizados
        optimized_alerts = []
        for alert in sample_alerts[:3]:  # Primeiros 3 alertas
            optimized_alert = OptimizedAlert(
                id=f"opt_{alert['id']}",
                original_alert_id=alert['id'],
                status=AlertStatus.ACTIVE,
                suppression_reason=None,
                group_id=None,
                priority_score=0.5,
                impact_score=0.3,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                metadata={'original_alert': alert}
            )
            optimized_alerts.append(optimized_alert)
            optimizer.optimized_alerts[optimized_alert.id] = optimized_alert
        
        await optimizer._group_by_source(optimized_alerts)
        
        # Verificar se grupos foram criados
        assert len(optimizer.alert_groups) > 0
        
        # Verificar se alertas foram agrupados
        grouped_alerts = [alert for alert in optimized_alerts if alert.group_id is not None]
        assert len(grouped_alerts) > 0
        
        # Limpar para outros testes
        optimizer.optimized_alerts.clear()
        optimizer.alert_groups.clear()
    
    @pytest.mark.asyncio
    async def test_group_by_type(self, optimizer, sample_alerts):
        """Testa agrupamento por tipo"""
        # Criar alertas otimizados
        optimized_alerts = []
        for alert in sample_alerts[:3]:  # Primeiros 3 alertas
            optimized_alert = OptimizedAlert(
                id=f"opt_{alert['id']}",
                original_alert_id=alert['id'],
                status=AlertStatus.ACTIVE,
                suppression_reason=None,
                group_id=None,
                priority_score=0.5,
                impact_score=0.3,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                metadata={'original_alert': alert}
            )
            optimized_alerts.append(optimized_alert)
            optimizer.optimized_alerts[optimized_alert.id] = optimized_alert
        
        await optimizer._group_by_type(optimized_alerts)
        
        # Verificar se grupos foram criados
        assert len(optimizer.alert_groups) > 0
        
        # Verificar se alertas foram agrupados
        grouped_alerts = [alert for alert in optimized_alerts if alert.group_id is not None]
        assert len(grouped_alerts) > 0
        
        # Limpar para outros testes
        optimizer.optimized_alerts.clear()
        optimizer.alert_groups.clear()
    
    @pytest.mark.asyncio
    async def test_group_by_impact(self, optimizer, sample_alerts):
        """Testa agrupamento por impacto"""
        # Criar alertas otimizados com diferentes impactos
        optimized_alerts = []
        for alert in sample_alerts[:3]:  # Primeiros 3 alertas
            optimized_alert = OptimizedAlert(
                id=f"opt_{alert['id']}",
                original_alert_id=alert['id'],
                status=AlertStatus.ACTIVE,
                suppression_reason=None,
                group_id=None,
                priority_score=0.5,
                impact_score=0.7,  # Alto impacto
                created_at=datetime.now(),
                updated_at=datetime.now(),
                metadata={'original_alert': alert}
            )
            optimized_alerts.append(optimized_alert)
            optimizer.optimized_alerts[optimized_alert.id] = optimized_alert
        
        await optimizer._group_by_impact(optimized_alerts)
        
        # Verificar se grupos foram criados
        assert len(optimizer.alert_groups) > 0
        
        # Verificar se alertas foram agrupados
        grouped_alerts = [alert for alert in optimized_alerts if alert.group_id is not None]
        assert len(grouped_alerts) > 0
        
        # Limpar para outros testes
        optimizer.optimized_alerts.clear()
        optimizer.alert_groups.clear()
    
    @pytest.mark.asyncio
    async def test_full_alert_optimization(self, optimizer, sample_alerts, sample_events, sample_anomalies):
        """Testa otimização completa de alertas"""
        # Processar todos os alertas
        optimized_alerts = await optimizer.optimize_alerts(sample_alerts, sample_events, sample_anomalies)
        
        # Verificar se alertas foram processados
        assert len(optimized_alerts) > 0
        
        # Verificar se alguns alertas foram suprimidos
        suppressed_alerts = [alert for alert in optimized_alerts if alert.status == AlertStatus.SUPPRESSED]
        assert len(suppressed_alerts) > 0
        
        # Verificar se alguns alertas foram agrupados
        grouped_alerts = [alert for alert in optimized_alerts if alert.group_id is not None]
        assert len(grouped_alerts) > 0
        
        # Verificar métricas
        stats = optimizer.get_statistics()
        assert stats['total_alerts_processed'] > 0
        assert stats['alerts_suppressed'] > 0
        assert stats['alerts_grouped'] > 0
        assert stats['suppression_rate_percentage'] > 0
    
    @pytest.mark.asyncio
    async def test_disabled_optimizer(self):
        """Testa optimizer desabilitado"""
        config = {'enabled': False}
        disabled_optimizer = AlertOptimizer(config)
        
        alerts = [{'id': 'test', 'severity': EventSeverity.HIGH.value}]
        optimized_alerts = await disabled_optimizer.optimize_alerts(alerts)
        
        assert len(optimized_alerts) == 0
    
    def test_get_statistics(self, optimizer):
        """Testa obtenção de estatísticas"""
        stats = optimizer.get_statistics()
        
        assert 'total_alerts_processed' in stats
        assert 'alerts_suppressed' in stats
        assert 'alerts_grouped' in stats
        assert 'alerts_optimized' in stats
        assert 'suppression_rate_percentage' in stats
        assert 'grouping_rate_percentage' in stats
        assert 'optimization_rate_percentage' in stats
        assert 'active_suppression_rules' in stats
        assert 'total_suppression_rules' in stats
        assert 'active_alert_groups' in stats
        assert 'total_alert_groups' in stats
        assert 'is_enabled' in stats
        
        assert stats['total_alerts_processed'] == 0  # Inicialmente vazio
        assert stats['suppression_rate_percentage'] == 0.0
        assert stats['is_enabled'] is True
        assert stats['active_suppression_rules'] > 0
    
    def test_add_suppression_rule(self, optimizer):
        """Testa adição de nova regra de supressão"""
        initial_count = len(optimizer.suppression_rules)
        
        new_rule = SuppressionRule(
            id="test_rule",
            name="Test Rule",
            description="Test rule for unit testing",
            conditions={'test': True},
            reason=SuppressionReason.FALSE_POSITIVE,
            duration_minutes=30,
            enabled=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        optimizer.add_suppression_rule(new_rule)
        
        assert len(optimizer.suppression_rules) == initial_count + 1
        assert any(rule.id == "test_rule" for rule in optimizer.suppression_rules)
    
    def test_update_suppression_rule(self, optimizer):
        """Testa atualização de regra de supressão existente"""
        rule = optimizer.suppression_rules[0]
        original_name = rule.name
        
        updates = {'name': 'Updated Rule Name'}
        success = optimizer.update_suppression_rule(rule.id, updates)
        
        assert success is True
        assert rule.name == 'Updated Rule Name'
        assert rule.name != original_name
    
    def test_delete_suppression_rule(self, optimizer):
        """Testa remoção de regra de supressão"""
        initial_count = len(optimizer.suppression_rules)
        rule_id = optimizer.suppression_rules[0].id
        
        success = optimizer.delete_suppression_rule(rule_id)
        
        assert success is True
        assert len(optimizer.suppression_rules) == initial_count - 1
        assert not any(rule.id == rule_id for rule in optimizer.suppression_rules)
    
    def test_delete_nonexistent_suppression_rule(self, optimizer):
        """Testa remoção de regra de supressão inexistente"""
        initial_count = len(optimizer.suppression_rules)
        
        success = optimizer.delete_suppression_rule("nonexistent_rule")
        
        assert success is False
        assert len(optimizer.suppression_rules) == initial_count
    
    def test_impact_level_calculation(self, optimizer):
        """Testa cálculo de nível de impacto"""
        assert optimizer._get_impact_level(0.9) == 'critical'
        assert optimizer._get_impact_level(0.7) == 'high'
        assert optimizer._get_impact_level(0.5) == 'medium'
        assert optimizer._get_impact_level(0.3) == 'low'
    
    def test_highest_severity_calculation(self, optimizer, sample_alerts):
        """Testa cálculo de maior severidade"""
        # Criar alertas otimizados com diferentes severidades
        alert_ids = []
        for alert in sample_alerts[:3]:
            optimized_alert = OptimizedAlert(
                id=f"opt_{alert['id']}",
                original_alert_id=alert['id'],
                status=AlertStatus.ACTIVE,
                suppression_reason=None,
                group_id=None,
                priority_score=0.5,
                impact_score=0.3,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                metadata={'original_alert': alert}
            )
            optimizer.optimized_alerts[optimized_alert.id] = optimized_alert
            alert_ids.append(optimized_alert.id)
        
        highest_severity = optimizer._get_highest_severity(alert_ids)
        assert highest_severity in [EventSeverity.CRITICAL.value, EventSeverity.HIGH.value, EventSeverity.MEDIUM.value, EventSeverity.LOW.value]
        
        # Limpar para outros testes
        optimizer.optimized_alerts.clear()
    
    def test_average_priority_calculation(self, optimizer):
        """Testa cálculo de média de prioridade"""
        # Criar alertas otimizados com diferentes prioridades
        alert_ids = []
        for i in range(3):
            optimized_alert = OptimizedAlert(
                id=f"opt_{i}",
                original_alert_id=f"alert_{i}",
                status=AlertStatus.ACTIVE,
                suppression_reason=None,
                group_id=None,
                priority_score=0.2 + (i * 0.3),  # 0.2, 0.5, 0.8
                impact_score=0.3,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                metadata={'original_alert': {}}
            )
            optimizer.optimized_alerts[optimized_alert.id] = optimized_alert
            alert_ids.append(optimized_alert.id)
        
        average_priority = optimizer._get_average_priority(alert_ids)
        assert average_priority == 0.5  # (0.2 + 0.5 + 0.8) / 3
        
        # Limpar para outros testes
        optimizer.optimized_alerts.clear()
    
    def test_average_impact_calculation(self, optimizer):
        """Testa cálculo de média de impacto"""
        # Criar alertas otimizados com diferentes impactos
        alert_ids = []
        for i in range(3):
            optimized_alert = OptimizedAlert(
                id=f"opt_{i}",
                original_alert_id=f"alert_{i}",
                status=AlertStatus.ACTIVE,
                suppression_reason=None,
                group_id=None,
                priority_score=0.5,
                impact_score=0.1 + (i * 0.2),  # 0.1, 0.3, 0.5
                created_at=datetime.now(),
                updated_at=datetime.now(),
                metadata={'original_alert': {}}
            )
            optimizer.optimized_alerts[optimized_alert.id] = optimized_alert
            alert_ids.append(optimized_alert.id)
        
        average_impact = optimizer._get_average_impact(alert_ids)
        assert average_impact == 0.3  # (0.1 + 0.3 + 0.5) / 3
        
        # Limpar para outros testes
        optimizer.optimized_alerts.clear()
    
    @pytest.mark.asyncio
    async def test_error_handling_in_optimization(self, optimizer):
        """Testa tratamento de erros na otimização"""
        # Alerta com dados inválidos
        invalid_alert = {'invalid': 'data'}
        
        optimized_alert = await optimizer._process_single_alert(invalid_alert, [], [])
        
        # Deve retornar None para alertas inválidos
        assert optimized_alert is None
    
    @pytest.mark.asyncio
    async def test_empty_alerts_list(self, optimizer):
        """Testa processamento de lista vazia de alertas"""
        optimized_alerts = await optimizer.optimize_alerts([], [], [])
        
        assert len(optimized_alerts) == 0
    
    @pytest.mark.asyncio
    async def test_alert_group_creation(self, optimizer):
        """Testa criação de grupos de alertas"""
        # Criar grupo manualmente
        group = AlertGroup(
            id="test_group",
            strategy=GroupingStrategy.BY_SOURCE,
            alerts=["alert_1", "alert_2"],
            summary={'source': 'test', 'alert_count': 2},
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=True
        )
        
        optimizer.alert_groups[group.id] = group
        
        assert group.id in optimizer.alert_groups
        assert optimizer.alert_groups[group.id].strategy == GroupingStrategy.BY_SOURCE
        assert len(optimizer.alert_groups[group.id].alerts) == 2
        
        # Limpar para outros testes
        optimizer.alert_groups.clear() 