"""
Testes Unitários para Auto Scaling
Sistema de Scaling Automático - Omni Keywords Finder

Prompt: Implementação de testes unitários para sistema de auto scaling
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from infrastructure.scaling.auto_scaling import (
    AutoScalingManager, ScalingPolicy, ScalingAction, ScalingThresholds,
    ResourceMetrics, ScalingDecision, create_auto_scaling_manager
)


class TestAutoScalingManager:
    """Testes para AutoScalingManager"""
    
    @pytest.fixture
    def sample_thresholds(self):
        """Limites de exemplo para testes"""
        return ScalingThresholds(
            cpu_scale_up=80.0,
            cpu_scale_down=30.0,
            memory_scale_up=85.0,
            memory_scale_down=40.0,
            request_scale_up=1000.0,
            request_scale_down=200.0,
            response_time_scale_up=2000.0,
            response_time_scale_down=500.0,
            error_rate_scale_up=0.05,
            cooldown_period=300,
            min_instances=2,
            max_instances=20,
            scale_up_factor=1.5,
            scale_down_factor=0.7
        )
    
    @pytest.fixture
    def sample_metrics(self):
        """Métricas de exemplo para testes"""
        return ResourceMetrics(
            cpu_usage=50.0,
            memory_usage=60.0,
            disk_usage=45.0,
            network_io=1024.0,
            request_rate=500.0,
            response_time=800.0,
            error_rate=0.02,
            active_connections=100
        )
    
    @pytest.fixture
    def high_load_metrics(self):
        """Métricas de alta carga para testes"""
        return ResourceMetrics(
            cpu_usage=90.0,
            memory_usage=95.0,
            disk_usage=80.0,
            network_io=2048.0,
            request_rate=1500.0,
            response_time=2500.0,
            error_rate=0.08,
            active_connections=200
        )
    
    @pytest.fixture
    def low_load_metrics(self):
        """Métricas de baixa carga para testes"""
        return ResourceMetrics(
            cpu_usage=20.0,
            memory_usage=25.0,
            disk_usage=30.0,
            network_io=512.0,
            request_rate=100.0,
            response_time=300.0,
            error_rate=0.01,
            active_connections=50
        )
    
    @pytest.fixture
    def auto_scaling_manager(self, sample_thresholds):
        """Instância de AutoScalingManager para testes"""
        return AutoScalingManager(
            thresholds=sample_thresholds,
            policy=ScalingPolicy.HYBRID,
            enable_cost_optimization=True,
            enable_prediction=True
        )
    
    def test_auto_scaling_manager_initialization(self, sample_thresholds):
        """Testa inicialização do AutoScalingManager"""
        manager = AutoScalingManager(
            thresholds=sample_thresholds,
            policy=ScalingPolicy.HYBRID,
            enable_cost_optimization=True,
            enable_prediction=True
        )
        
        assert manager.thresholds == sample_thresholds
        assert manager.policy == ScalingPolicy.HYBRID
        assert manager.enable_cost_optimization is True
        assert manager.enable_prediction is True
        assert manager.current_instances == sample_thresholds.min_instances
        assert manager.last_scaling_action is None
        assert len(manager.metrics_history) == 0
        assert len(manager.scaling_history) == 0
        assert manager.is_cooldown is False
        assert manager.cooldown_start is None
    
    def test_auto_scaling_manager_with_different_policies(self, sample_thresholds):
        """Testa inicialização com diferentes políticas"""
        policies = [
            ScalingPolicy.CPU_BASED,
            ScalingPolicy.MEMORY_BASED,
            ScalingPolicy.REQUEST_BASED,
            ScalingPolicy.CUSTOM_METRIC,
            ScalingPolicy.HYBRID
        ]
        
        for policy in policies:
            manager = AutoScalingManager(
                thresholds=sample_thresholds,
                policy=policy
            )
            assert manager.policy == policy
    
    @pytest.mark.asyncio
    async def test_update_metrics(self, auto_scaling_manager, sample_metrics):
        """Testa atualização de métricas"""
        await auto_scaling_manager.update_metrics(sample_metrics)
        
        assert len(auto_scaling_manager.metrics_history) == 1
        assert auto_scaling_manager.metrics_history[0] == sample_metrics
    
    @pytest.mark.asyncio
    async def test_update_metrics_history_limit(self, auto_scaling_manager):
        """Testa limite do histórico de métricas"""
        # Adicionar mais métricas que o limite
        for i in range(auto_scaling_manager.max_history_size + 10):
            metrics = ResourceMetrics(
                cpu_usage=float(i),
                memory_usage=float(i),
                disk_usage=float(i),
                network_io=float(i),
                request_rate=float(i),
                response_time=float(i),
                error_rate=0.01,
                active_connections=i
            )
            await auto_scaling_manager.update_metrics(metrics)
        
        # Verificar se o histórico não excede o limite
        assert len(auto_scaling_manager.metrics_history) == auto_scaling_manager.max_history_size
    
    @pytest.mark.asyncio
    async def test_evaluate_scaling_no_metrics(self, auto_scaling_manager):
        """Testa avaliação de scaling sem métricas"""
        decision = await auto_scaling_manager.evaluate_scaling()
        assert decision is None
    
    @pytest.mark.asyncio
    async def test_evaluate_scaling_during_cooldown(self, auto_scaling_manager, sample_metrics):
        """Testa avaliação de scaling durante cooldown"""
        # Adicionar métricas
        await auto_scaling_manager.update_metrics(sample_metrics)
        
        # Forçar cooldown
        auto_scaling_manager.is_cooldown = True
        auto_scaling_manager.cooldown_start = datetime.utcnow()
        
        decision = await auto_scaling_manager.evaluate_scaling()
        assert decision is None
    
    @pytest.mark.asyncio
    async def test_evaluate_cpu_based_scaling_scale_up(self, sample_thresholds):
        """Testa scaling baseado em CPU - scale up"""
        manager = AutoScalingManager(
            thresholds=sample_thresholds,
            policy=ScalingPolicy.CPU_BASED
        )
        
        # Adicionar métricas com CPU alto
        high_cpu_metrics = ResourceMetrics(
            cpu_usage=85.0,
            memory_usage=60.0,
            disk_usage=45.0,
            network_io=1024.0,
            request_rate=500.0,
            response_time=800.0,
            error_rate=0.02,
            active_connections=100
        )
        
        # Adicionar várias métricas para estabilidade
        for _ in range(10):
            await manager.update_metrics(high_cpu_metrics)
        
        decision = await manager.evaluate_scaling()
        
        assert decision is not None
        assert decision.action == ScalingAction.SCALE_UP
        assert decision.current_instances == sample_thresholds.min_instances
        assert decision.target_instances > decision.current_instances
        assert "CPU usage alto" in decision.reason
        assert decision.confidence > 0.5
    
    @pytest.mark.asyncio
    async def test_evaluate_cpu_based_scaling_scale_down(self, sample_thresholds):
        """Testa scaling baseado em CPU - scale down"""
        manager = AutoScalingManager(
            thresholds=sample_thresholds,
            policy=ScalingPolicy.CPU_BASED
        )
        
        # Definir instâncias atuais
        manager.current_instances = 5
        
        # Adicionar métricas com CPU baixo
        low_cpu_metrics = ResourceMetrics(
            cpu_usage=20.0,
            memory_usage=60.0,
            disk_usage=45.0,
            network_io=1024.0,
            request_rate=500.0,
            response_time=800.0,
            error_rate=0.02,
            active_connections=100
        )
        
        # Adicionar várias métricas para estabilidade
        for _ in range(10):
            await manager.update_metrics(low_cpu_metrics)
        
        decision = await manager.evaluate_scaling()
        
        assert decision is not None
        assert decision.action == ScalingAction.SCALE_DOWN
        assert decision.current_instances == 5
        assert decision.target_instances < decision.current_instances
        assert "CPU usage baixo" in decision.reason
        assert decision.confidence > 0.5
    
    @pytest.mark.asyncio
    async def test_evaluate_memory_based_scaling(self, sample_thresholds):
        """Testa scaling baseado em memória"""
        manager = AutoScalingManager(
            thresholds=sample_thresholds,
            policy=ScalingPolicy.MEMORY_BASED
        )
        
        # Adicionar métricas com memória alta
        high_memory_metrics = ResourceMetrics(
            cpu_usage=50.0,
            memory_usage=90.0,
            disk_usage=45.0,
            network_io=1024.0,
            request_rate=500.0,
            response_time=800.0,
            error_rate=0.02,
            active_connections=100
        )
        
        for _ in range(10):
            await manager.update_metrics(high_memory_metrics)
        
        decision = await manager.evaluate_scaling()
        
        assert decision is not None
        assert decision.action == ScalingAction.SCALE_UP
        assert "Memory usage alto" in decision.reason
    
    @pytest.mark.asyncio
    async def test_evaluate_request_based_scaling(self, sample_thresholds):
        """Testa scaling baseado em requests"""
        manager = AutoScalingManager(
            thresholds=sample_thresholds,
            policy=ScalingPolicy.REQUEST_BASED
        )
        
        # Adicionar métricas com alta taxa de requests
        high_request_metrics = ResourceMetrics(
            cpu_usage=50.0,
            memory_usage=60.0,
            disk_usage=45.0,
            network_io=1024.0,
            request_rate=1200.0,
            response_time=2500.0,
            error_rate=0.02,
            active_connections=100
        )
        
        for _ in range(10):
            await manager.update_metrics(high_request_metrics)
        
        decision = await manager.evaluate_scaling()
        
        assert decision is not None
        assert decision.action == ScalingAction.SCALE_UP
        assert "High load" in decision.reason
    
    @pytest.mark.asyncio
    async def test_evaluate_hybrid_scaling(self, sample_thresholds):
        """Testa scaling híbrido"""
        manager = AutoScalingManager(
            thresholds=sample_thresholds,
            policy=ScalingPolicy.HYBRID
        )
        
        # Adicionar métricas com múltiplos indicadores altos
        hybrid_high_metrics = ResourceMetrics(
            cpu_usage=85.0,
            memory_usage=90.0,
            disk_usage=45.0,
            network_io=1024.0,
            request_rate=1200.0,
            response_time=2500.0,
            error_rate=0.08,
            active_connections=100
        )
        
        for _ in range(10):
            await manager.update_metrics(hybrid_high_metrics)
        
        decision = await manager.evaluate_scaling()
        
        assert decision is not None
        assert decision.action == ScalingAction.SCALE_UP
        assert "Hybrid score alto" in decision.reason
        assert decision.confidence > 0.5
    
    @pytest.mark.asyncio
    async def test_cost_optimization(self, sample_thresholds):
        """Testa otimização de custos"""
        manager = AutoScalingManager(
            thresholds=sample_thresholds,
            policy=ScalingPolicy.CPU_BASED,
            enable_cost_optimization=True
        )
        
        # Adicionar métricas com CPU muito alto
        very_high_cpu_metrics = ResourceMetrics(
            cpu_usage=95.0,
            memory_usage=60.0,
            disk_usage=45.0,
            network_io=1024.0,
            request_rate=500.0,
            response_time=800.0,
            error_rate=0.02,
            active_connections=100
        )
        
        for _ in range(10):
            await manager.update_metrics(very_high_cpu_metrics)
        
        decision = await manager.evaluate_scaling()
        
        assert decision is not None
        assert decision.action == ScalingAction.SCALE_UP
        assert decision.estimated_cost_impact > 0
        # Verificar se o scaling foi limitado por custo
        assert decision.target_instances <= decision.current_instances + 2
    
    @pytest.mark.asyncio
    async def test_load_prediction(self, sample_thresholds):
        """Testa predição de carga"""
        manager = AutoScalingManager(
            thresholds=sample_thresholds,
            policy=ScalingPolicy.CPU_BASED,
            enable_prediction=True
        )
        
        # Adicionar métricas com tendência crescente
        for i in range(20):
            metrics = ResourceMetrics(
                cpu_usage=70.0 + i,  # Tendência crescente
                memory_usage=60.0,
                disk_usage=45.0,
                network_io=1024.0,
                request_rate=500.0,
                response_time=800.0,
                error_rate=0.02,
                active_connections=100
            )
            await manager.update_metrics(metrics)
        
        decision = await manager.evaluate_scaling()
        
        assert decision is not None
        assert decision.action == ScalingAction.SCALE_UP
        assert "predição: carga aumentando" in decision.reason
    
    @pytest.mark.asyncio
    async def test_instance_limits(self, sample_thresholds):
        """Testa limites de instâncias"""
        manager = AutoScalingManager(
            thresholds=sample_thresholds,
            policy=ScalingPolicy.CPU_BASED
        )
        
        # Definir instâncias atuais no máximo
        manager.current_instances = sample_thresholds.max_instances
        
        # Adicionar métricas com CPU alto
        high_cpu_metrics = ResourceMetrics(
            cpu_usage=95.0,
            memory_usage=60.0,
            disk_usage=45.0,
            network_io=1024.0,
            request_rate=500.0,
            response_time=800.0,
            error_rate=0.02,
            active_connections=100
        )
        
        for _ in range(10):
            await manager.update_metrics(high_cpu_metrics)
        
        decision = await manager.evaluate_scaling()
        
        assert decision is not None
        assert decision.action == ScalingAction.SCALE_UP
        assert decision.target_instances == sample_thresholds.max_instances
        assert "limitado ao máximo" in decision.reason
    
    @pytest.mark.asyncio
    async def test_execute_scaling_success(self, auto_scaling_manager, sample_metrics):
        """Testa execução de scaling bem-sucedida"""
        # Adicionar métricas
        await auto_scaling_manager.update_metrics(sample_metrics)
        
        # Criar decisão de scaling
        decision = ScalingDecision(
            action=ScalingAction.SCALE_UP,
            reason="Test scaling",
            current_instances=2,
            target_instances=3,
            metrics=sample_metrics,
            policy=ScalingPolicy.HYBRID,
            confidence=0.8
        )
        
        # Executar scaling
        result = await auto_scaling_manager.execute_scaling(decision)
        
        assert result is True
        assert auto_scaling_manager.current_instances == 3
    
    @pytest.mark.asyncio
    async def test_execute_scaling_no_action(self, auto_scaling_manager, sample_metrics):
        """Testa execução de scaling sem ação"""
        decision = ScalingDecision(
            action=ScalingAction.NO_ACTION,
            reason="No action needed",
            current_instances=2,
            target_instances=2,
            metrics=sample_metrics,
            policy=ScalingPolicy.HYBRID,
            confidence=0.5
        )
        
        result = await auto_scaling_manager.execute_scaling(decision)
        
        assert result is True
        assert auto_scaling_manager.current_instances == 2  # Não deve mudar
    
    def test_get_scaling_history(self, auto_scaling_manager):
        """Testa obtenção do histórico de scaling"""
        # Adicionar algumas decisões de scaling
        for i in range(5):
            decision = ScalingDecision(
                action=ScalingAction.SCALE_UP,
                reason=f"Test {i}",
                current_instances=i,
                target_instances=i+1,
                metrics=ResourceMetrics(
                    cpu_usage=50.0,
                    memory_usage=60.0,
                    disk_usage=45.0,
                    network_io=1024.0,
                    request_rate=500.0,
                    response_time=800.0,
                    error_rate=0.02,
                    active_connections=100
                ),
                policy=ScalingPolicy.HYBRID,
                confidence=0.8
            )
            auto_scaling_manager.scaling_history.append(decision)
        
        # Testar com limite
        history = auto_scaling_manager.get_scaling_history(limit=3)
        assert len(history) == 3
        
        # Testar sem limite
        history = auto_scaling_manager.get_scaling_history()
        assert len(history) == 5
    
    def test_get_metrics_summary(self, auto_scaling_manager, sample_metrics):
        """Testa obtenção do resumo de métricas"""
        # Adicionar métricas
        auto_scaling_manager.metrics_history.append(sample_metrics)
        
        summary = auto_scaling_manager.get_metrics_summary()
        
        assert "current_instances" in summary
        assert "avg_cpu_usage" in summary
        assert "avg_memory_usage" in summary
        assert "avg_request_rate" in summary
        assert "avg_response_time" in summary
        assert "avg_error_rate" in summary
        assert "last_scaling_action" in summary
        assert "is_cooldown" in summary
        assert "total_scaling_actions" in summary
    
    def test_reset(self, auto_scaling_manager, sample_metrics):
        """Testa reset do gerenciador"""
        # Adicionar dados
        auto_scaling_manager.metrics_history.append(sample_metrics)
        auto_scaling_manager.current_instances = 5
        auto_scaling_manager.is_cooldown = True
        auto_scaling_manager.cooldown_start = datetime.utcnow()
        
        # Resetar
        auto_scaling_manager.reset()
        
        assert len(auto_scaling_manager.metrics_history) == 0
        assert len(auto_scaling_manager.scaling_history) == 0
        assert auto_scaling_manager.current_instances == auto_scaling_manager.thresholds.min_instances
        assert auto_scaling_manager.is_cooldown is False
        assert auto_scaling_manager.cooldown_start is None


class TestScalingThresholds:
    """Testes para ScalingThresholds"""
    
    def test_scaling_thresholds_initialization(self):
        """Testa inicialização de ScalingThresholds"""
        thresholds = ScalingThresholds()
        
        assert thresholds.cpu_scale_up == 80.0
        assert thresholds.cpu_scale_down == 30.0
        assert thresholds.memory_scale_up == 85.0
        assert thresholds.memory_scale_down == 40.0
        assert thresholds.request_scale_up == 1000.0
        assert thresholds.request_scale_down == 200.0
        assert thresholds.response_time_scale_up == 2000.0
        assert thresholds.response_time_scale_down == 500.0
        assert thresholds.error_rate_scale_up == 0.05
        assert thresholds.cooldown_period == 300
        assert thresholds.min_instances == 2
        assert thresholds.max_instances == 20
        assert thresholds.scale_up_factor == 1.5
        assert thresholds.scale_down_factor == 0.7
    
    def test_scaling_thresholds_custom_values(self):
        """Testa ScalingThresholds com valores customizados"""
        thresholds = ScalingThresholds(
            cpu_scale_up=90.0,
            cpu_scale_down=20.0,
            memory_scale_up=90.0,
            memory_scale_down=30.0,
            min_instances=1,
            max_instances=50
        )
        
        assert thresholds.cpu_scale_up == 90.0
        assert thresholds.cpu_scale_down == 20.0
        assert thresholds.memory_scale_up == 90.0
        assert thresholds.memory_scale_down == 30.0
        assert thresholds.min_instances == 1
        assert thresholds.max_instances == 50
    
    def test_scaling_thresholds_validation_cpu(self):
        """Testa validação de thresholds de CPU"""
        with pytest.raises(ValueError, match="CPU scale up deve ser maior que scale down"):
            ScalingThresholds(cpu_scale_up=30.0, cpu_scale_down=80.0)
    
    def test_scaling_thresholds_validation_memory(self):
        """Testa validação de thresholds de memória"""
        with pytest.raises(ValueError, match="Memory scale up deve ser maior que scale down"):
            ScalingThresholds(memory_scale_up=40.0, memory_scale_down=85.0)
    
    def test_scaling_thresholds_validation_requests(self):
        """Testa validação de thresholds de requests"""
        with pytest.raises(ValueError, match="Request scale up deve ser maior que scale down"):
            ScalingThresholds(request_scale_up=200.0, request_scale_down=1000.0)
    
    def test_scaling_thresholds_validation_response_time(self):
        """Testa validação de thresholds de response time"""
        with pytest.raises(ValueError, match="Response time scale up deve ser maior que scale down"):
            ScalingThresholds(response_time_scale_up=500.0, response_time_scale_down=2000.0)
    
    def test_scaling_thresholds_validation_min_instances(self):
        """Testa validação de min instances"""
        with pytest.raises(ValueError, match="Min instances deve ser pelo menos 1"):
            ScalingThresholds(min_instances=0)
    
    def test_scaling_thresholds_validation_max_instances(self):
        """Testa validação de max instances"""
        with pytest.raises(ValueError, match="Max instances deve ser maior que min instances"):
            ScalingThresholds(min_instances=10, max_instances=5)
    
    def test_scaling_thresholds_validation_scale_up_factor(self):
        """Testa validação de scale up factor"""
        with pytest.raises(ValueError, match="Scale up factor deve ser maior que 1.0"):
            ScalingThresholds(scale_up_factor=0.5)
    
    def test_scaling_thresholds_validation_scale_down_factor(self):
        """Testa validação de scale down factor"""
        with pytest.raises(ValueError, match="Scale down factor deve ser menor que 1.0"):
            ScalingThresholds(scale_down_factor=1.5)


class TestResourceMetrics:
    """Testes para ResourceMetrics"""
    
    def test_resource_metrics_initialization(self):
        """Testa inicialização de ResourceMetrics"""
        metrics = ResourceMetrics(
            cpu_usage=50.0,
            memory_usage=60.0,
            disk_usage=45.0,
            network_io=1024.0,
            request_rate=500.0,
            response_time=800.0,
            error_rate=0.02,
            active_connections=100
        )
        
        assert metrics.cpu_usage == 50.0
        assert metrics.memory_usage == 60.0
        assert metrics.disk_usage == 45.0
        assert metrics.network_io == 1024.0
        assert metrics.request_rate == 500.0
        assert metrics.response_time == 800.0
        assert metrics.error_rate == 0.02
        assert metrics.active_connections == 100
        assert isinstance(metrics.timestamp, datetime)
    
    def test_resource_metrics_validation_cpu(self):
        """Testa validação de CPU usage"""
        with pytest.raises(ValueError, match="CPU usage deve estar entre 0 e 100"):
            ResourceMetrics(
                cpu_usage=150.0,
                memory_usage=60.0,
                disk_usage=45.0,
                network_io=1024.0,
                request_rate=500.0,
                response_time=800.0,
                error_rate=0.02,
                active_connections=100
            )
    
    def test_resource_metrics_validation_memory(self):
        """Testa validação de memory usage"""
        with pytest.raises(ValueError, match="Memory usage deve estar entre 0 e 100"):
            ResourceMetrics(
                cpu_usage=50.0,
                memory_usage=-10.0,
                disk_usage=45.0,
                network_io=1024.0,
                request_rate=500.0,
                response_time=800.0,
                error_rate=0.02,
                active_connections=100
            )
    
    def test_resource_metrics_validation_error_rate(self):
        """Testa validação de error rate"""
        with pytest.raises(ValueError, match="Error rate deve estar entre 0 e 1"):
            ResourceMetrics(
                cpu_usage=50.0,
                memory_usage=60.0,
                disk_usage=45.0,
                network_io=1024.0,
                request_rate=500.0,
                response_time=800.0,
                error_rate=1.5,
                active_connections=100
            )


class TestScalingDecision:
    """Testes para ScalingDecision"""
    
    def test_scaling_decision_initialization(self):
        """Testa inicialização de ScalingDecision"""
        metrics = ResourceMetrics(
            cpu_usage=50.0,
            memory_usage=60.0,
            disk_usage=45.0,
            network_io=1024.0,
            request_rate=500.0,
            response_time=800.0,
            error_rate=0.02,
            active_connections=100
        )
        
        decision = ScalingDecision(
            action=ScalingAction.SCALE_UP,
            reason="Test decision",
            current_instances=2,
            target_instances=3,
            metrics=metrics,
            policy=ScalingPolicy.HYBRID,
            confidence=0.8,
            estimated_cost_impact=5.0,
            estimated_performance_impact=0.2
        )
        
        assert decision.action == ScalingAction.SCALE_UP
        assert decision.reason == "Test decision"
        assert decision.current_instances == 2
        assert decision.target_instances == 3
        assert decision.metrics == metrics
        assert decision.policy == ScalingPolicy.HYBRID
        assert decision.confidence == 0.8
        assert decision.estimated_cost_impact == 5.0
        assert decision.estimated_performance_impact == 0.2
        assert isinstance(decision.timestamp, datetime)
    
    def test_scaling_decision_validation_confidence(self):
        """Testa validação de confidence"""
        metrics = ResourceMetrics(
            cpu_usage=50.0,
            memory_usage=60.0,
            disk_usage=45.0,
            network_io=1024.0,
            request_rate=500.0,
            response_time=800.0,
            error_rate=0.02,
            active_connections=100
        )
        
        with pytest.raises(ValueError, match="Confidence deve estar entre 0 e 1"):
            ScalingDecision(
                action=ScalingAction.SCALE_UP,
                reason="Test decision",
                current_instances=2,
                target_instances=3,
                metrics=metrics,
                policy=ScalingPolicy.HYBRID,
                confidence=1.5
            )
    
    def test_scaling_decision_validation_target_instances(self):
        """Testa validação de target instances"""
        metrics = ResourceMetrics(
            cpu_usage=50.0,
            memory_usage=60.0,
            disk_usage=45.0,
            network_io=1024.0,
            request_rate=500.0,
            response_time=800.0,
            error_rate=0.02,
            active_connections=100
        )
        
        with pytest.raises(ValueError, match="Target instances não pode ser negativo"):
            ScalingDecision(
                action=ScalingAction.SCALE_UP,
                reason="Test decision",
                current_instances=2,
                target_instances=-1,
                metrics=metrics,
                policy=ScalingPolicy.HYBRID,
                confidence=0.8
            )


class TestCreateAutoScalingManager:
    """Testes para função create_auto_scaling_manager"""
    
    def test_create_auto_scaling_manager_default(self):
        """Testa criação com configurações padrão"""
        manager = create_auto_scaling_manager()
        
        assert manager.policy == ScalingPolicy.HYBRID
        assert manager.enable_cost_optimization is True
        assert manager.enable_prediction is True
        assert isinstance(manager.thresholds, ScalingThresholds)
    
    def test_create_auto_scaling_manager_custom_policy(self):
        """Testa criação com política customizada"""
        manager = create_auto_scaling_manager(policy=ScalingPolicy.CPU_BASED)
        
        assert manager.policy == ScalingPolicy.CPU_BASED
        assert manager.enable_cost_optimization is True
        assert manager.enable_prediction is True
    
    def test_create_auto_scaling_manager_disabled_features(self):
        """Testa criação com features desabilitadas"""
        manager = create_auto_scaling_manager(
            enable_cost_optimization=False,
            enable_prediction=False
        )
        
        assert manager.enable_cost_optimization is False
        assert manager.enable_prediction is False


class TestAutoScalingIntegration:
    """Testes de integração para Auto Scaling"""
    
    @pytest.mark.asyncio
    async def test_complete_scaling_cycle(self):
        """Testa ciclo completo de scaling"""
        manager = create_auto_scaling_manager(policy=ScalingPolicy.CPU_BASED)
        
        # Simular carga baixa
        low_metrics = ResourceMetrics(
            cpu_usage=20.0,
            memory_usage=30.0,
            disk_usage=40.0,
            network_io=512.0,
            request_rate=100.0,
            response_time=300.0,
            error_rate=0.01,
            active_connections=50
        )
        
        # Adicionar métricas baixas
        for _ in range(10):
            await manager.update_metrics(low_metrics)
        
        # Avaliar scaling
        decision = await manager.evaluate_scaling()
        
        if decision and decision.action != ScalingAction.NO_ACTION:
            # Executar scaling
            success = await manager.execute_scaling(decision)
            assert success is True
        
        # Simular carga alta
        high_metrics = ResourceMetrics(
            cpu_usage=90.0,
            memory_usage=95.0,
            disk_usage=80.0,
            network_io=2048.0,
            request_rate=1500.0,
            response_time=2500.0,
            error_rate=0.08,
            active_connections=200
        )
        
        # Aguardar cooldown
        await asyncio.sleep(0.1)
        
        # Adicionar métricas altas
        for _ in range(10):
            await manager.update_metrics(high_metrics)
        
        # Avaliar scaling novamente
        decision = await manager.evaluate_scaling()
        
        if decision and decision.action != ScalingAction.NO_ACTION:
            # Executar scaling
            success = await manager.execute_scaling(decision)
            assert success is True
    
    @pytest.mark.asyncio
    async def test_multiple_policies_comparison(self):
        """Testa comparação entre diferentes políticas"""
        policies = [
            ScalingPolicy.CPU_BASED,
            ScalingPolicy.MEMORY_BASED,
            ScalingPolicy.REQUEST_BASED,
            ScalingPolicy.HYBRID
        ]
        
        test_metrics = ResourceMetrics(
            cpu_usage=85.0,
            memory_usage=90.0,
            disk_usage=45.0,
            network_io=1024.0,
            request_rate=1200.0,
            response_time=2500.0,
            error_rate=0.08,
            active_connections=100
        )
        
        decisions = []
        
        for policy in policies:
            manager = create_auto_scaling_manager(policy=policy)
            
            # Adicionar métricas
            for _ in range(10):
                await manager.update_metrics(test_metrics)
            
            # Avaliar scaling
            decision = await manager.evaluate_scaling()
            if decision:
                decisions.append((policy, decision))
        
        # Verificar se pelo menos algumas políticas geraram decisões
        assert len(decisions) > 0
        
        # Verificar se as decisões são consistentes (scale up)
        for policy, decision in decisions:
            if decision.action != ScalingAction.NO_ACTION:
                assert decision.action == ScalingAction.SCALE_UP


if __name__ == "__main__":
    pytest.main([__file__]) 