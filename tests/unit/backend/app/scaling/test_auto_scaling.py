"""
Testes Unitários para AutoScaling
AutoScaling - Sistema de auto scaling com múltiplas políticas

Prompt: Implementação de testes unitários para AutoScaling
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Fase: Criação sem execução - Testes baseados em código real
Tracing ID: TEST_AUTO_SCALING_20250127_001
"""

import pytest
import asyncio
import time
import uuid
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from backend.app.scaling.auto_scaling import (
    ScalingAction,
    ResourceType,
    ResourceMetrics,
    ScalingRule,
    ScalingPolicy,
    AutoScaler
)


class TestScalingAction:
    """Testes para ScalingAction (Enum)"""
    
    def test_enum_values(self):
        """Testa valores do enum ScalingAction"""
        assert ScalingAction.SCALE_UP == "scale_up"
        assert ScalingAction.SCALE_DOWN == "scale_down"
        assert ScalingAction.MAINTAIN == "maintain"
    
    def test_enum_membership(self):
        """Testa pertencimento ao enum"""
        assert "scale_up" in ScalingAction
        assert "scale_down" in ScalingAction
        assert "maintain" in ScalingAction
        assert "invalid_action" not in ScalingAction


class TestResourceType:
    """Testes para ResourceType (Enum)"""
    
    def test_enum_values(self):
        """Testa valores do enum ResourceType"""
        assert ResourceType.CPU == "cpu"
        assert ResourceType.MEMORY == "memory"
    
    def test_enum_membership(self):
        """Testa pertencimento ao enum"""
        assert "cpu" in ResourceType
        assert "memory" in ResourceType
        assert "disk" not in ResourceType


class TestResourceMetrics:
    """Testes para ResourceMetrics"""
    
    @pytest.fixture
    def sample_metrics_data(self):
        """Dados de exemplo para ResourceMetrics"""
        return {
            "resource_type": ResourceType.CPU,
            "current_value": 75.5,
            "min_value": 0.0,
            "max_value": 100.0,
            "unit": "%",
            "timestamp": datetime.now()
        }
    
    @pytest.fixture
    def metrics(self, sample_metrics_data):
        """Instância de ResourceMetrics para testes"""
        return ResourceMetrics(**sample_metrics_data)
    
    def test_initialization(self, sample_metrics_data):
        """Testa inicialização básica"""
        metrics = ResourceMetrics(**sample_metrics_data)
        
        assert metrics.resource_type == ResourceType.CPU
        assert metrics.current_value == 75.5
        assert metrics.min_value == 0.0
        assert metrics.max_value == 100.0
        assert metrics.unit == "%"
        assert metrics.timestamp == sample_metrics_data["timestamp"]
    
    def test_cpu_metrics(self):
        """Testa métricas de CPU"""
        metrics = ResourceMetrics(
            resource_type=ResourceType.CPU,
            current_value=85.0,
            min_value=0.0,
            max_value=100.0,
            unit="%",
            timestamp=datetime.now()
        )
        
        assert metrics.resource_type == ResourceType.CPU
        assert metrics.current_value == 85.0
        assert metrics.unit == "%"
    
    def test_memory_metrics(self):
        """Testa métricas de memória"""
        metrics = ResourceMetrics(
            resource_type=ResourceType.MEMORY,
            current_value=2048.0,
            min_value=0.0,
            max_value=8192.0,
            unit="MB",
            timestamp=datetime.now()
        )
        
        assert metrics.resource_type == ResourceType.MEMORY
        assert metrics.current_value == 2048.0
        assert metrics.unit == "MB"
    
    def test_value_validation(self):
        """Testa validação de valores"""
        # Valor dentro do range
        metrics = ResourceMetrics(
            resource_type=ResourceType.CPU,
            current_value=50.0,
            min_value=0.0,
            max_value=100.0,
            unit="%",
            timestamp=datetime.now()
        )
        assert metrics.current_value == 50.0
        
        # Valor negativo (deve ser aceito mas com warning)
        metrics = ResourceMetrics(
            resource_type=ResourceType.CPU,
            current_value=-10.0,
            min_value=0.0,
            max_value=100.0,
            unit="%",
            timestamp=datetime.now()
        )
        assert metrics.current_value == -10.0


class TestScalingRule:
    """Testes para ScalingRule"""
    
    @pytest.fixture
    def sample_rule_data(self):
        """Dados de exemplo para ScalingRule"""
        return {
            "id": "rule_cpu_high",
            "name": "CPU High Scaling Rule",
            "resource_type": ResourceType.CPU,
            "policy": ScalingPolicy.SIMPLE_SCALING,
            "target_value": 70.0,
            "scale_up_threshold": 80.0,
            "scale_down_threshold": 30.0,
            "scale_up_cooldown": 300,
            "scale_down_cooldown": 300,
            "min_capacity": 1,
            "max_capacity": 10,
            "step_size": 1,
            "enabled": True
        }
    
    @pytest.fixture
    def rule(self, sample_rule_data):
        """Instância de ScalingRule para testes"""
        return ScalingRule(**sample_rule_data)
    
    def test_initialization(self, sample_rule_data):
        """Testa inicialização básica"""
        rule = ScalingRule(**sample_rule_data)
        
        assert rule.id == "rule_cpu_high"
        assert rule.name == "CPU High Scaling Rule"
        assert rule.resource_type == ResourceType.CPU
        assert rule.policy == ScalingPolicy.SIMPLE_SCALING
        assert rule.target_value == 70.0
        assert rule.scale_up_threshold == 80.0
        assert rule.scale_down_threshold == 30.0
        assert rule.scale_up_cooldown == 300
        assert rule.scale_down_cooldown == 300
        assert rule.min_capacity == 1
        assert rule.max_capacity == 10
        assert rule.step_size == 1
        assert rule.enabled is True
        assert rule.metadata is None
    
    def test_default_values(self):
        """Testa valores padrão"""
        rule = ScalingRule(
            id="test_rule",
            name="Test Rule",
            resource_type=ResourceType.CPU,
            policy=ScalingPolicy.SIMPLE_SCALING,
            target_value=50.0,
            scale_up_threshold=80.0,
            scale_down_threshold=20.0
        )
        
        assert rule.scale_up_cooldown == 300
        assert rule.scale_down_cooldown == 300
        assert rule.min_capacity == 1
        assert rule.max_capacity == 10
        assert rule.step_size == 1
        assert rule.enabled is True
        assert rule.metadata is None
    
    def test_metadata_support(self):
        """Testa suporte a metadados"""
        metadata = {"description": "Test rule", "tags": ["cpu", "scaling"]}
        
        rule = ScalingRule(
            id="test_rule",
            name="Test Rule",
            resource_type=ResourceType.CPU,
            policy=ScalingPolicy.SIMPLE_SCALING,
            target_value=50.0,
            scale_up_threshold=80.0,
            scale_down_threshold=20.0,
            metadata=metadata
        )
        
        assert rule.metadata == metadata
        assert rule.metadata["description"] == "Test rule"
        assert "cpu" in rule.metadata["tags"]


class TestScalingPolicy:
    """Testes para ScalingPolicy (Enum)"""
    
    def test_enum_values(self):
        """Testa valores do enum ScalingPolicy"""
        assert ScalingPolicy.SIMPLE_SCALING == "simple_scaling"
        assert ScalingPolicy.STEP_SCALING == "step_scaling"
        assert ScalingPolicy.TARGET_TRACKING == "target_tracking"
    
    def test_enum_membership(self):
        """Testa pertencimento ao enum"""
        assert "simple_scaling" in ScalingPolicy
        assert "step_scaling" in ScalingPolicy
        assert "target_tracking" in ScalingPolicy
        assert "invalid_policy" not in ScalingPolicy


class TestAutoScaler:
    """Testes para AutoScaler"""
    
    @pytest.fixture
    def mock_metrics_collector(self):
        """Mock do coletor de métricas"""
        collector = Mock()
        collector.collect_cpu_metrics = AsyncMock(return_value=ResourceMetrics(
            resource_type=ResourceType.CPU,
            current_value=75.0,
            min_value=0.0,
            max_value=100.0,
            unit="%",
            timestamp=datetime.now()
        ))
        collector.collect_memory_metrics = AsyncMock(return_value=ResourceMetrics(
            resource_type=ResourceType.MEMORY,
            current_value=2048.0,
            min_value=0.0,
            max_value=8192.0,
            unit="MB",
            timestamp=datetime.now()
        ))
        return collector
    
    @pytest.fixture
    def auto_scaler(self, mock_metrics_collector):
        """Instância de AutoScaler para testes"""
        return AutoScaler(metrics_collector=mock_metrics_collector)
    
    @pytest.fixture
    def sample_rule(self):
        """Regra de scaling de exemplo"""
        return ScalingRule(
            id="test_rule",
            name="Test Scaling Rule",
            resource_type=ResourceType.CPU,
            policy=ScalingPolicy.SIMPLE_SCALING,
            target_value=70.0,
            scale_up_threshold=80.0,
            scale_down_threshold=30.0,
            min_capacity=1,
            max_capacity=5,
            step_size=1
        )
    
    def test_initialization(self, mock_metrics_collector):
        """Testa inicialização do AutoScaler"""
        scaler = AutoScaler(metrics_collector=mock_metrics_collector)
        
        assert scaler.metrics_collector == mock_metrics_collector
        assert scaler.rules == {}
        assert scaler.current_capacity == 1
        assert scaler.last_scale_up == datetime.min
        assert scaler.last_scale_down == datetime.min
        assert scaler.scaling_history == []
    
    def test_register_rule(self, auto_scaler, sample_rule):
        """Testa registro de regra"""
        auto_scaler.register_rule(sample_rule)
        
        assert "test_rule" in auto_scaler.rules
        assert auto_scaler.rules["test_rule"] == sample_rule
    
    def test_register_duplicate_rule(self, auto_scaler, sample_rule):
        """Testa registro de regra duplicada"""
        auto_scaler.register_rule(sample_rule)
        auto_scaler.register_rule(sample_rule)  # Sobrescreve
        
        assert len(auto_scaler.rules) == 1
        assert "test_rule" in auto_scaler.rules
    
    def test_unregister_rule(self, auto_scaler, sample_rule):
        """Testa remoção de regra"""
        auto_scaler.register_rule(sample_rule)
        auto_scaler.unregister_rule("test_rule")
        
        assert "test_rule" not in auto_scaler.rules
        assert len(auto_scaler.rules) == 0
    
    def test_unregister_nonexistent_rule(self, auto_scaler):
        """Testa remoção de regra inexistente"""
        # Não deve gerar erro
        auto_scaler.unregister_rule("nonexistent_rule")
        assert len(auto_scaler.rules) == 0
    
    @pytest.mark.asyncio
    async def test_collect_metrics_cpu(self, auto_scaler, mock_metrics_collector):
        """Testa coleta de métricas de CPU"""
        metrics = await auto_scaler._collect_metrics(ResourceType.CPU)
        
        assert metrics is not None
        assert metrics.resource_type == ResourceType.CPU
        assert metrics.current_value == 75.0
        assert metrics.unit == "%"
        
        mock_metrics_collector.collect_cpu_metrics.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_collect_metrics_memory(self, auto_scaler, mock_metrics_collector):
        """Testa coleta de métricas de memória"""
        metrics = await auto_scaler._collect_metrics(ResourceType.MEMORY)
        
        assert metrics is not None
        assert metrics.resource_type == ResourceType.MEMORY
        assert metrics.current_value == 2048.0
        assert metrics.unit == "MB"
        
        mock_metrics_collector.collect_memory_metrics.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_collect_metrics_failure(self, auto_scaler, mock_metrics_collector):
        """Testa falha na coleta de métricas"""
        mock_metrics_collector.collect_cpu_metrics.side_effect = Exception("Collection failed")
        
        metrics = await auto_scaler._collect_metrics(ResourceType.CPU)
        
        assert metrics is None
    
    def test_evaluate_scaling_rule_scale_up(self, auto_scaler, sample_rule):
        """Testa avaliação de regra para scale up"""
        metrics = ResourceMetrics(
            resource_type=ResourceType.CPU,
            current_value=85.0,  # Acima do threshold
            min_value=0.0,
            max_value=100.0,
            unit="%",
            timestamp=datetime.now()
        )
        
        action = auto_scaler._evaluate_scaling_rule(sample_rule, metrics)
        
        assert action is not None
        assert action.action_type == ScalingAction.SCALE_UP
        assert action.current_capacity == 1
        assert action.target_capacity == 2
        assert "CPU usage" in action.reason
    
    def test_evaluate_scaling_rule_scale_down(self, auto_scaler, sample_rule):
        """Testa avaliação de regra para scale down"""
        auto_scaler.current_capacity = 3
        
        metrics = ResourceMetrics(
            resource_type=ResourceType.CPU,
            current_value=20.0,  # Abaixo do threshold
            min_value=0.0,
            max_value=100.0,
            unit="%",
            timestamp=datetime.now()
        )
        
        action = auto_scaler._evaluate_scaling_rule(sample_rule, metrics)
        
        assert action is not None
        assert action.action_type == ScalingAction.SCALE_DOWN
        assert action.current_capacity == 3
        assert action.target_capacity == 2
        assert "CPU usage" in action.reason
    
    def test_evaluate_scaling_rule_no_action(self, auto_scaler, sample_rule):
        """Testa avaliação de regra sem ação necessária"""
        metrics = ResourceMetrics(
            resource_type=ResourceType.CPU,
            current_value=50.0,  # Dentro do range normal
            min_value=0.0,
            max_value=100.0,
            unit="%",
            timestamp=datetime.now()
        )
        
        action = auto_scaler._evaluate_scaling_rule(sample_rule, metrics)
        
        assert action is None
    
    def test_evaluate_scaling_rule_cooldown(self, auto_scaler, sample_rule):
        """Testa avaliação de regra durante cooldown"""
        # Simular scale up recente
        auto_scaler.last_scale_up = datetime.now() - timedelta(seconds=60)  # Dentro do cooldown
        
        metrics = ResourceMetrics(
            resource_type=ResourceType.CPU,
            current_value=85.0,
            min_value=0.0,
            max_value=100.0,
            unit="%",
            timestamp=datetime.now()
        )
        
        action = auto_scaler._evaluate_scaling_rule(sample_rule, metrics)
        
        assert action is None  # Deve respeitar o cooldown
    
    def test_evaluate_scaling_rule_max_capacity(self, auto_scaler, sample_rule):
        """Testa avaliação de regra no limite máximo de capacidade"""
        auto_scaler.current_capacity = 5  # Máximo
        
        metrics = ResourceMetrics(
            resource_type=ResourceType.CPU,
            current_value=85.0,
            min_value=0.0,
            max_value=100.0,
            unit="%",
            timestamp=datetime.now()
        )
        
        action = auto_scaler._evaluate_scaling_rule(sample_rule, metrics)
        
        assert action is None  # Não pode escalar além do máximo
    
    def test_evaluate_scaling_rule_min_capacity(self, auto_scaler, sample_rule):
        """Testa avaliação de regra no limite mínimo de capacidade"""
        auto_scaler.current_capacity = 1  # Mínimo
        
        metrics = ResourceMetrics(
            resource_type=ResourceType.CPU,
            current_value=20.0,
            min_value=0.0,
            max_value=100.0,
            unit="%",
            timestamp=datetime.now()
        )
        
        action = auto_scaler._evaluate_scaling_rule(sample_rule, metrics)
        
        assert action is None  # Não pode escalar abaixo do mínimo
    
    @pytest.mark.asyncio
    async def test_execute_scaling_action_success(self, auto_scaler, sample_rule):
        """Testa execução bem-sucedida de ação de scaling"""
        action = ScalingAction(
            id=str(uuid.uuid4()),
            rule_id=sample_rule.id,
            action_type=ScalingAction.SCALE_UP,
            current_capacity=1,
            target_capacity=2,
            reason="Test scaling",
            timestamp=datetime.now()
        )
        
        with patch.object(auto_scaler, '_perform_scaling', new_callable=AsyncMock, return_value=True):
            success = await auto_scaler._execute_scaling_action(action)
            
            assert success is True
            assert auto_scaler.current_capacity == 2
            assert len(auto_scaler.scaling_history) == 1
            assert auto_scaler.scaling_history[0] == action
    
    @pytest.mark.asyncio
    async def test_execute_scaling_action_failure(self, auto_scaler, sample_rule):
        """Testa falha na execução de ação de scaling"""
        action = ScalingAction(
            id=str(uuid.uuid4()),
            rule_id=sample_rule.id,
            action_type=ScalingAction.SCALE_UP,
            current_capacity=1,
            target_capacity=2,
            reason="Test scaling",
            timestamp=datetime.now()
        )
        
        with patch.object(auto_scaler, '_perform_scaling', new_callable=AsyncMock, return_value=False):
            success = await auto_scaler._execute_scaling_action(action)
            
            assert success is False
            assert auto_scaler.current_capacity == 1  # Não deve ter mudado
            assert len(auto_scaler.scaling_history) == 0
    
    @pytest.mark.asyncio
    async def test_perform_scaling_scale_up(self, auto_scaler):
        """Testa execução de scale up"""
        with patch.object(auto_scaler, '_scale_up_instances', new_callable=AsyncMock, return_value=True):
            success = await auto_scaler._perform_scaling(ScalingAction.SCALE_UP, 1, 2)
            
            assert success is True
            auto_scaler._scale_up_instances.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_perform_scaling_scale_down(self, auto_scaler):
        """Testa execução de scale down"""
        with patch.object(auto_scaler, '_scale_down_instances', new_callable=AsyncMock, return_value=True):
            success = await auto_scaler._perform_scaling(ScalingAction.SCALE_DOWN, 2, 1)
            
            assert success is True
            auto_scaler._scale_down_instances.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_perform_scaling_maintain(self, auto_scaler):
        """Testa execução de maintain"""
        success = await auto_scaler._perform_scaling(ScalingAction.MAINTAIN, 1, 1)
        
        assert success is True  # Sempre bem-sucedido para maintain
    
    @pytest.mark.asyncio
    async def test_scale_up_instances(self, auto_scaler):
        """Testa scale up de instâncias"""
        # Mock da implementação real
        with patch('backend.app.scaling.auto_scaling.logger') as mock_logger:
            success = await auto_scaler._scale_up_instances(2)
            
            # Por enquanto, sempre retorna True (implementação mock)
            assert success is True
            mock_logger.info.assert_called()
    
    @pytest.mark.asyncio
    async def test_scale_down_instances(self, auto_scaler):
        """Testa scale down de instâncias"""
        # Mock da implementação real
        with patch('backend.app.scaling.auto_scaling.logger') as mock_logger:
            success = await auto_scaler._scale_down_instances(1)
            
            # Por enquanto, sempre retorna True (implementação mock)
            assert success is True
            mock_logger.info.assert_called()
    
    @pytest.mark.asyncio
    async def test_evaluate_all_rules(self, auto_scaler, sample_rule):
        """Testa avaliação de todas as regras"""
        auto_scaler.register_rule(sample_rule)
        
        with patch.object(auto_scaler, '_collect_metrics', new_callable=AsyncMock) as mock_collect:
            mock_collect.return_value = ResourceMetrics(
                resource_type=ResourceType.CPU,
                current_value=85.0,
                min_value=0.0,
                max_value=100.0,
                unit="%",
                timestamp=datetime.now()
            )
            
            with patch.object(auto_scaler, '_execute_scaling_action', new_callable=AsyncMock):
                await auto_scaler.evaluate_all_rules()
                
                mock_collect.assert_called_once_with(ResourceType.CPU)
    
    def test_get_scaling_history(self, auto_scaler, sample_rule):
        """Testa obtenção do histórico de scaling"""
        # Adicionar algumas ações ao histórico
        action1 = ScalingAction(
            id=str(uuid.uuid4()),
            rule_id=sample_rule.id,
            action_type=ScalingAction.SCALE_UP,
            current_capacity=1,
            target_capacity=2,
            reason="Test 1",
            timestamp=datetime.now()
        )
        
        action2 = ScalingAction(
            id=str(uuid.uuid4()),
            rule_id=sample_rule.id,
            action_type=ScalingAction.SCALE_DOWN,
            current_capacity=2,
            target_capacity=1,
            reason="Test 2",
            timestamp=datetime.now()
        )
        
        auto_scaler.scaling_history = [action1, action2]
        
        history = auto_scaler.get_scaling_history()
        
        assert len(history) == 2
        assert history[0] == action1
        assert history[1] == action2
    
    def test_get_scaling_history_limit(self, auto_scaler, sample_rule):
        """Testa limite do histórico de scaling"""
        # Adicionar muitas ações
        for i in range(100):
            action = ScalingAction(
                id=str(uuid.uuid4()),
                rule_id=sample_rule.id,
                action_type=ScalingAction.SCALE_UP,
                current_capacity=i,
                target_capacity=i+1,
                reason=f"Test {i}",
                timestamp=datetime.now()
            )
            auto_scaler.scaling_history.append(action)
        
        history = auto_scaler.get_scaling_history(limit=10)
        
        assert len(history) == 10
        assert history[0].current_capacity == 90  # Mais recentes primeiro


class TestAutoScalerIntegration:
    """Testes de integração para AutoScaler"""
    
    @pytest.mark.asyncio
    async def test_full_scaling_cycle(self, mock_metrics_collector):
        """Testa ciclo completo de scaling"""
        scaler = AutoScaler(metrics_collector=mock_metrics_collector)
        
        # Registrar regra
        rule = ScalingRule(
            id="test_rule",
            name="Test Rule",
            resource_type=ResourceType.CPU,
            policy=ScalingPolicy.SIMPLE_SCALING,
            target_value=70.0,
            scale_up_threshold=80.0,
            scale_down_threshold=30.0,
            min_capacity=1,
            max_capacity=5,
            step_size=1
        )
        scaler.register_rule(rule)
        
        # Simular métricas altas
        mock_metrics_collector.collect_cpu_metrics.return_value = ResourceMetrics(
            resource_type=ResourceType.CPU,
            current_value=85.0,
            min_value=0.0,
            max_value=100.0,
            unit="%",
            timestamp=datetime.now()
        )
        
        # Executar avaliação
        with patch.object(scaler, '_execute_scaling_action', new_callable=AsyncMock):
            await scaler.evaluate_all_rules()
            
            # Verificar se tentou executar scaling
            scaler._execute_scaling_action.assert_called_once()


class TestAutoScalerErrorHandling:
    """Testes de tratamento de erro para AutoScaler"""
    
    def test_invalid_rule_data(self, auto_scaler):
        """Testa dados de regra inválidos"""
        with pytest.raises(TypeError):
            auto_scaler.register_rule(None)
    
    def test_metrics_collection_failure(self, auto_scaler, mock_metrics_collector):
        """Testa falha na coleta de métricas"""
        mock_metrics_collector.collect_cpu_metrics.side_effect = Exception("Collection failed")
        
        # Não deve gerar erro, apenas retornar None
        assert auto_scaler._collect_metrics(ResourceType.CPU) is None
    
    @pytest.mark.asyncio
    async def test_scaling_execution_failure(self, auto_scaler, sample_rule):
        """Testa falha na execução de scaling"""
        action = ScalingAction(
            id=str(uuid.uuid4()),
            rule_id=sample_rule.id,
            action_type=ScalingAction.SCALE_UP,
            current_capacity=1,
            target_capacity=2,
            reason="Test",
            timestamp=datetime.now()
        )
        
        with patch.object(auto_scaler, '_perform_scaling', new_callable=AsyncMock, side_effect=Exception("Scaling failed")):
            success = await auto_scaler._execute_scaling_action(action)
            
            assert success is False


class TestAutoScalerPerformance:
    """Testes de performance para AutoScaler"""
    
    def test_large_number_of_rules(self, mock_metrics_collector):
        """Testa performance com muitas regras"""
        scaler = AutoScaler(metrics_collector=mock_metrics_collector)
        
        # Registrar 1000 regras
        for i in range(1000):
            rule = ScalingRule(
                id=f"rule_{i}",
                name=f"Rule {i}",
                resource_type=ResourceType.CPU,
                policy=ScalingPolicy.SIMPLE_SCALING,
                target_value=70.0,
                scale_up_threshold=80.0,
                scale_down_threshold=30.0
            )
            scaler.register_rule(rule)
        
        assert len(scaler.rules) == 1000
    
    def test_scaling_history_memory_usage(self, mock_metrics_collector):
        """Testa uso de memória do histórico de scaling"""
        scaler = AutoScaler(metrics_collector=mock_metrics_collector)
        
        # Adicionar muitas ações ao histórico
        for i in range(10000):
            action = ScalingAction(
                id=str(uuid.uuid4()),
                rule_id="test_rule",
                action_type=ScalingAction.SCALE_UP,
                current_capacity=i,
                target_capacity=i+1,
                reason=f"Test {i}",
                timestamp=datetime.now()
            )
            scaler.scaling_history.append(action)
        
        # Verificar se o sistema continua funcionando
        assert len(scaler.scaling_history) == 10000 