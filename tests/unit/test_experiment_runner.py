"""
Testes Unitários para ExperimentRunner
ExperimentRunner - Sistema de execução de experimentos de chaos engineering

Prompt: Implementação de testes unitários para ExperimentRunner
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Fase: Criação sem execução - Testes baseados em código real
Tracing ID: TEST_EXPERIMENT_RUNNER_001_20250127
"""

import pytest
import json
import asyncio
import threading
import time
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml

from infrastructure.chaos.experiment_runner import (
    ExperimentRunner,
    ExperimentExecution,
    ExperimentStatus,
    ExperimentType,
    ExperimentPhase,
    ExperimentMetrics,
    ExperimentResult,
    ExperimentConfig,
    create_experiment_runner
)


class TestExperimentStatus:
    """Testes para ExperimentStatus"""
    
    def test_experiment_status_values(self):
        """Testa valores dos status de experimento"""
        assert ExperimentStatus.PENDING.value == "pending"
        assert ExperimentStatus.RUNNING.value == "running"
        assert ExperimentStatus.COMPLETED.value == "completed"
        assert ExperimentStatus.FAILED.value == "failed"
        assert ExperimentStatus.CANCELLED.value == "cancelled"
        assert ExperimentStatus.ROLLBACK.value == "rollback"
    
    def test_experiment_status_enumeration(self):
        """Testa enumeração completa dos status"""
        expected_statuses = [
            "pending", "running", "completed", "failed", 
            "cancelled", "rollback"
        ]
        actual_statuses = [status.value for status in ExperimentStatus]
        assert actual_statuses == expected_statuses


class TestExperimentType:
    """Testes para ExperimentType"""
    
    def test_experiment_type_values(self):
        """Testa valores dos tipos de experimento"""
        assert ExperimentType.NETWORK_LATENCY.value == "network_latency"
        assert ExperimentType.NETWORK_PACKET_LOSS.value == "network_packet_loss"
        assert ExperimentType.CPU_STRESS.value == "cpu_stress"
        assert ExperimentType.MEMORY_STRESS.value == "memory_stress"
        assert ExperimentType.DISK_STRESS.value == "disk_stress"
        assert ExperimentType.SERVICE_FAILURE.value == "service_failure"
        assert ExperimentType.DATABASE_FAILURE.value == "database_failure"
        assert ExperimentType.CACHE_FAILURE.value == "cache_failure"
        assert ExperimentType.LOAD_BALANCER_FAILURE.value == "load_balancer_failure"
        assert ExperimentType.DEPENDENCY_FAILURE.value == "dependency_failure"
    
    def test_experiment_type_enumeration(self):
        """Testa enumeração completa dos tipos"""
        expected_types = [
            "network_latency", "network_packet_loss", "cpu_stress",
            "memory_stress", "disk_stress", "service_failure",
            "database_failure", "cache_failure", "load_balancer_failure",
            "dependency_failure"
        ]
        actual_types = [exp_type.value for exp_type in ExperimentType]
        assert actual_types == expected_types


class TestExperimentPhase:
    """Testes para ExperimentPhase"""
    
    def test_experiment_phase_values(self):
        """Testa valores das fases de experimento"""
        assert ExperimentPhase.PREPARATION.value == "preparation"
        assert ExperimentPhase.STEADY_STATE.value == "steady_state"
        assert ExperimentPhase.CHAOS_INJECTION.value == "chaos_injection"
        assert ExperimentPhase.OBSERVATION.value == "observation"
        assert ExperimentPhase.RECOVERY.value == "recovery"
        assert ExperimentPhase.ANALYSIS.value == "analysis"
    
    def test_experiment_phase_sequence(self):
        """Testa sequência lógica das fases"""
        phases = list(ExperimentPhase)
        assert len(phases) == 6
        assert phases[0] == ExperimentPhase.PREPARATION
        assert phases[-1] == ExperimentPhase.ANALYSIS


class TestExperimentMetrics:
    """Testes para ExperimentMetrics"""
    
    @pytest.fixture
    def sample_metrics_data(self):
        """Dados de exemplo para métricas"""
        return {
            "timestamp": datetime.now(),
            "cpu_usage": 45.5,
            "memory_usage": 67.2,
            "response_time": 125.0,
            "error_rate": 0.02,
            "throughput": 1500.0,
            "availability": 99.8,
            "custom_metrics": {
                "queue_size": 25,
                "active_connections": 150
            }
        }
    
    def test_experiment_metrics_initialization(self, sample_metrics_data):
        """Testa inicialização de métricas"""
        metrics = ExperimentMetrics(**sample_metrics_data)
        
        assert metrics.timestamp == sample_metrics_data["timestamp"]
        assert metrics.cpu_usage == 45.5
        assert metrics.memory_usage == 67.2
        assert metrics.response_time == 125.0
        assert metrics.error_rate == 0.02
        assert metrics.throughput == 1500.0
        assert metrics.availability == 99.8
        assert metrics.custom_metrics["queue_size"] == 25
        assert metrics.custom_metrics["active_connections"] == 150
    
    def test_experiment_metrics_validation(self):
        """Testa validação de métricas"""
        # Teste com valores válidos
        valid_metrics = ExperimentMetrics(
            timestamp=datetime.now(),
            cpu_usage=50.0,
            memory_usage=75.0,
            response_time=100.0,
            error_rate=0.01,
            throughput=2000.0,
            availability=99.9,
            custom_metrics={}
        )
        assert valid_metrics.cpu_usage == 50.0
        
        # Teste com valores extremos
        extreme_metrics = ExperimentMetrics(
            timestamp=datetime.now(),
            cpu_usage=100.0,
            memory_usage=100.0,
            response_time=10000.0,
            error_rate=1.0,
            throughput=0.0,
            availability=0.0,
            custom_metrics={"test": "value"}
        )
        assert extreme_metrics.cpu_usage == 100.0
        assert extreme_metrics.error_rate == 1.0


class TestExperimentResult:
    """Testes para ExperimentResult"""
    
    @pytest.fixture
    def sample_result_data(self):
        """Dados de exemplo para resultado"""
        return {
            "experiment_id": "test_exp_001",
            "status": ExperimentStatus.COMPLETED,
            "start_time": datetime.now(),
            "end_time": datetime.now() + timedelta(minutes=5),
            "duration": 300.0,
            "phases_completed": [ExperimentPhase.PREPARATION, ExperimentPhase.STEADY_STATE],
            "metrics": [],
            "hypothesis_validated": True,
            "issues_found": ["High memory usage detected"],
            "recommendations": ["Increase memory allocation"],
            "rollback_required": False,
            "rollback_successful": None
        }
    
    def test_experiment_result_initialization(self, sample_result_data):
        """Testa inicialização de resultado"""
        result = ExperimentResult(**sample_result_data)
        
        assert result.experiment_id == "test_exp_001"
        assert result.status == ExperimentStatus.COMPLETED
        assert result.hypothesis_validated is True
        assert len(result.issues_found) == 1
        assert len(result.recommendations) == 1
        assert result.rollback_required is False
    
    def test_experiment_result_with_failure(self):
        """Testa resultado com falha"""
        result = ExperimentResult(
            experiment_id="failed_exp_001",
            status=ExperimentStatus.FAILED,
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(minutes=2),
            duration=120.0,
            phases_completed=[ExperimentPhase.PREPARATION],
            metrics=[],
            hypothesis_validated=None,
            issues_found=["Service timeout", "Connection refused"],
            recommendations=["Check network connectivity", "Verify service health"],
            rollback_required=True,
            rollback_successful=True
        )
        
        assert result.status == ExperimentStatus.FAILED
        assert result.rollback_required is True
        assert result.rollback_successful is True
        assert len(result.issues_found) == 2


class TestExperimentConfig:
    """Testes para ExperimentConfig"""
    
    @pytest.fixture
    def sample_config_data(self):
        """Dados de exemplo para configuração"""
        return {
            "name": "network_latency_test",
            "description": "Test network latency impact on API response",
            "type": ExperimentType.NETWORK_LATENCY,
            "hypothesis": "Adding 100ms latency will increase error rate by 5%",
            "duration": 300,
            "steady_state_duration": 60,
            "chaos_duration": 120,
            "observation_duration": 60,
            "max_impact": 0.3,
            "auto_rollback": True,
            "rollback_threshold": 0.5,
            "metrics_interval": 5,
            "alert_thresholds": {
                "error_rate": 0.1,
                "response_time": 500.0
            },
            "parameters": {
                "latency_ms": 100,
                "packet_loss_percent": 0.0
            }
        }
    
    def test_experiment_config_initialization(self, sample_config_data):
        """Testa inicialização de configuração"""
        config = ExperimentConfig(**sample_config_data)
        
        assert config.name == "network_latency_test"
        assert config.type == ExperimentType.NETWORK_LATENCY
        assert config.duration == 300
        assert config.max_impact == 0.3
        assert config.auto_rollback is True
        assert config.parameters["latency_ms"] == 100
    
    def test_experiment_config_defaults(self):
        """Testa valores padrão da configuração"""
        minimal_config = {
            "name": "minimal_test",
            "description": "Minimal configuration test",
            "type": ExperimentType.CPU_STRESS,
            "hypothesis": "CPU stress will impact performance"
        }
        
        config = ExperimentConfig(**minimal_config)
        
        assert config.duration == 300  # default
        assert config.steady_state_duration == 60  # default
        assert config.chaos_duration == 120  # default
        assert config.observation_duration == 60  # default
        assert config.max_impact == 0.3  # default
        assert config.auto_rollback is True  # default
        assert config.rollback_threshold == 0.5  # default
        assert config.metrics_interval == 5  # default
        assert config.alert_thresholds == {}  # default
        assert config.parameters == {}  # default
    
    def test_experiment_config_validation(self):
        """Testa validação de configuração"""
        # Configuração válida
        valid_config = ExperimentConfig(
            name="valid_test",
            description="Valid configuration",
            type=ExperimentType.MEMORY_STRESS,
            hypothesis="Memory stress test",
            max_impact=0.5,
            rollback_threshold=0.7
        )
        assert valid_config.max_impact == 0.5
        
        # Teste com valores extremos
        extreme_config = ExperimentConfig(
            name="extreme_test",
            description="Extreme values test",
            type=ExperimentType.DISK_STRESS,
            hypothesis="Disk stress test",
            max_impact=1.0,
            rollback_threshold=0.1
        )
        assert extreme_config.max_impact == 1.0


class TestExperimentRunner:
    """Testes para ExperimentRunner"""
    
    @pytest.fixture
    def mock_config_file(self, tmp_path):
        """Arquivo de configuração mock"""
        config_data = {
            "experiments": [
                {
                    "name": "test_network_latency",
                    "description": "Test network latency",
                    "type": "network_latency",
                    "hypothesis": "Network latency affects performance",
                    "duration": 300,
                    "max_impact": 0.3,
                    "auto_rollback": True
                },
                {
                    "name": "test_cpu_stress",
                    "description": "Test CPU stress",
                    "type": "cpu_stress",
                    "hypothesis": "CPU stress impacts response time",
                    "duration": 180,
                    "max_impact": 0.4,
                    "auto_rollback": True
                }
            ]
        }
        
        config_file = tmp_path / "chaos_experiments.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        return str(config_file)
    
    @pytest.fixture
    def experiment_runner(self, mock_config_file):
        """Instância do ExperimentRunner para testes"""
        with patch('infrastructure.chaos.experiment_runner.Path') as mock_path:
            mock_path.return_value.exists.return_value = True
            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = """
                experiments:
                  - name: test_network_latency
                    description: Test network latency
                    type: network_latency
                    hypothesis: Network latency affects performance
                    duration: 300
                    max_impact: 0.3
                    auto_rollback: true
                """
                
                runner = ExperimentRunner(config_path=mock_config_file)
                return runner
    
    def test_experiment_runner_initialization(self, experiment_runner):
        """Testa inicialização do ExperimentRunner"""
        assert experiment_runner.config_path is not None
        assert isinstance(experiment_runner.experiments, dict)
        assert isinstance(experiment_runner.running_experiments, dict)
        assert isinstance(experiment_runner.completed_experiments, dict)
        assert isinstance(experiment_runner.lock, threading.RLock)
        assert isinstance(experiment_runner.executor, type(experiment_runner.executor))
        assert isinstance(experiment_runner.monitoring_callbacks, list)
        assert isinstance(experiment_runner.rollback_handlers, dict)
    
    @patch('infrastructure.chaos.experiment_runner.Path')
    def test_experiment_runner_config_file_not_found(self, mock_path):
        """Testa comportamento quando arquivo de configuração não existe"""
        mock_path.return_value.exists.return_value = False
        
        runner = ExperimentRunner(config_path="nonexistent.yaml")
        assert len(runner.experiments) == 0
    
    @patch('infrastructure.chaos.experiment_runner.Path')
    @patch('builtins.open', create=True)
    def test_experiment_runner_load_experiments_error(self, mock_open, mock_path):
        """Testa tratamento de erro ao carregar experimentos"""
        mock_path.return_value.exists.return_value = True
        mock_open.side_effect = Exception("File read error")
        
        runner = ExperimentRunner(config_path="error.yaml")
        assert len(runner.experiments) == 0
    
    def test_experiment_runner_setup_rollback_handlers(self, experiment_runner):
        """Testa configuração dos handlers de rollback"""
        expected_handlers = [
            ExperimentType.NETWORK_LATENCY,
            ExperimentType.NETWORK_PACKET_LOSS,
            ExperimentType.CPU_STRESS,
            ExperimentType.MEMORY_STRESS,
            ExperimentType.DISK_STRESS,
            ExperimentType.SERVICE_FAILURE,
            ExperimentType.DATABASE_FAILURE,
            ExperimentType.CACHE_FAILURE,
            ExperimentType.LOAD_BALANCER_FAILURE,
            ExperimentType.DEPENDENCY_FAILURE
        ]
        
        for exp_type in expected_handlers:
            assert exp_type in experiment_runner.rollback_handlers
            assert callable(experiment_runner.rollback_handlers[exp_type])
    
    @patch.object(ExperimentRunner, '_run_experiment_async')
    async def test_run_experiment_success(self, mock_run_async, experiment_runner):
        """Testa execução bem-sucedida de experimento"""
        # Mock do experimento
        experiment_runner.experiments["test_exp"] = ExperimentConfig(
            name="test_exp",
            description="Test experiment",
            type=ExperimentType.NETWORK_LATENCY,
            hypothesis="Test hypothesis"
        )
        
        mock_run_async.return_value = None
        
        experiment_id = await experiment_runner.run_experiment("test_exp")
        
        assert experiment_id is not None
        assert "test_exp_" in experiment_id
        mock_run_async.assert_called_once()
    
    async def test_run_experiment_not_found(self, experiment_runner):
        """Testa execução de experimento inexistente"""
        with pytest.raises(ValueError, match="Experiment 'nonexistent' not found"):
            await experiment_runner.run_experiment("nonexistent")
    
    async def test_stop_experiment(self, experiment_runner):
        """Testa parada de experimento"""
        # Mock de experimento em execução
        mock_execution = AsyncMock()
        mock_execution.stop.return_value = True
        experiment_runner.running_experiments["test_id"] = mock_execution
        
        result = await experiment_runner.stop_experiment("test_id")
        
        assert result is True
        mock_execution.stop.assert_called_once()
    
    async def test_stop_experiment_not_found(self, experiment_runner):
        """Testa parada de experimento inexistente"""
        result = await experiment_runner.stop_experiment("nonexistent")
        assert result is False
    
    async def test_get_experiment_status(self, experiment_runner):
        """Testa obtenção de status de experimento"""
        # Mock de experimento em execução
        mock_execution = AsyncMock()
        mock_execution.result.status = ExperimentStatus.RUNNING
        experiment_runner.running_experiments["test_id"] = mock_execution
        
        status = await experiment_runner.get_experiment_status("test_id")
        
        assert status == ExperimentStatus.RUNNING
    
    async def test_get_experiment_status_not_found(self, experiment_runner):
        """Testa obtenção de status de experimento inexistente"""
        status = await experiment_runner.get_experiment_status("nonexistent")
        assert status is None
    
    def test_get_experiment_result(self, experiment_runner):
        """Testa obtenção de resultado de experimento"""
        # Mock de resultado
        mock_result = ExperimentResult(
            experiment_id="test_id",
            status=ExperimentStatus.COMPLETED,
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration=300.0,
            phases_completed=[],
            metrics=[],
            hypothesis_validated=True,
            issues_found=[],
            recommendations=[],
            rollback_required=False,
            rollback_successful=None
        )
        experiment_runner.completed_experiments["test_id"] = mock_result
        
        result = experiment_runner.get_experiment_result("test_id")
        
        assert result == mock_result
        assert result.status == ExperimentStatus.COMPLETED
    
    def test_get_experiment_result_not_found(self, experiment_runner):
        """Testa obtenção de resultado de experimento inexistente"""
        result = experiment_runner.get_experiment_result("nonexistent")
        assert result is None
    
    def test_list_experiments(self, experiment_runner):
        """Testa listagem de experimentos"""
        # Adicionar experimentos mock
        experiment_runner.experiments["exp1"] = ExperimentConfig(
            name="exp1",
            description="Experiment 1",
            type=ExperimentType.NETWORK_LATENCY,
            hypothesis="Hypothesis 1"
        )
        experiment_runner.experiments["exp2"] = ExperimentConfig(
            name="exp2",
            description="Experiment 2",
            type=ExperimentType.CPU_STRESS,
            hypothesis="Hypothesis 2"
        )
        
        experiments = experiment_runner.list_experiments()
        
        assert len(experiments) == 2
        assert experiments[0]["name"] == "exp1"
        assert experiments[1]["name"] == "exp2"
    
    def test_list_running_experiments(self, experiment_runner):
        """Testa listagem de experimentos em execução"""
        # Mock de experimentos em execução
        mock_execution1 = Mock()
        mock_execution1.experiment_id = "running1"
        mock_execution1.config.name = "Running Experiment 1"
        
        mock_execution2 = Mock()
        mock_execution2.experiment_id = "running2"
        mock_execution2.config.name = "Running Experiment 2"
        
        experiment_runner.running_experiments["running1"] = mock_execution1
        experiment_runner.running_experiments["running2"] = mock_execution2
        
        running = experiment_runner.list_running_experiments()
        
        assert len(running) == 2
        assert running[0]["experiment_id"] == "running1"
        assert running[1]["experiment_id"] == "running2"
    
    def test_add_monitoring_callback(self, experiment_runner):
        """Testa adição de callback de monitoramento"""
        callback = Mock()
        
        experiment_runner.add_monitoring_callback(callback)
        
        assert callback in experiment_runner.monitoring_callbacks
        assert len(experiment_runner.monitoring_callbacks) == 1
    
    def test_rollback_handlers(self, experiment_runner):
        """Testa handlers de rollback"""
        # Testar que todos os handlers retornam boolean
        for handler in experiment_runner.rollback_handlers.values():
            result = handler("test_experiment_id")
            assert isinstance(result, bool)


class TestExperimentExecution:
    """Testes para ExperimentExecution"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo para execução"""
        return ExperimentConfig(
            name="test_execution",
            description="Test execution",
            type=ExperimentType.NETWORK_LATENCY,
            hypothesis="Test hypothesis",
            duration=300,
            auto_rollback=True
        )
    
    @pytest.fixture
    def mock_runner(self):
        """Runner mock para execução"""
        return Mock(spec=ExperimentRunner)
    
    @pytest.fixture
    def experiment_execution(self, sample_config, mock_runner):
        """Instância de ExperimentExecution para testes"""
        with patch('infrastructure.chaos.experiment_runner.FailureInjector'):
            with patch('infrastructure.chaos.experiment_runner.ChaosMonitor'):
                execution = ExperimentExecution(sample_config, mock_runner)
                return execution
    
    def test_experiment_execution_initialization(self, experiment_execution, sample_config):
        """Testa inicialização da execução"""
        assert experiment_execution.config == sample_config
        assert experiment_execution.experiment_id.startswith("test_execution_")
        assert experiment_execution.current_phase is None
        assert experiment_execution.stop_requested is False
        assert experiment_execution.result.experiment_id == experiment_execution.experiment_id
        assert experiment_execution.result.status == ExperimentStatus.PENDING
    
    @patch('infrastructure.chaos.experiment_runner.FailureInjector')
    @patch('infrastructure.chaos.experiment_runner.ChaosMonitor')
    async def test_run_experiment_success(self, mock_monitor, mock_injector, experiment_execution):
        """Testa execução bem-sucedida de experimento"""
        # Mock das fases
        experiment_execution._run_phase = AsyncMock()
        experiment_execution._perform_rollback = AsyncMock()
        
        await experiment_execution.run()
        
        # Verificar que todas as fases foram executadas
        assert experiment_execution._run_phase.call_count == 6
        assert experiment_execution.result.status == ExperimentStatus.COMPLETED
    
    @patch('infrastructure.chaos.experiment_runner.FailureInjector')
    @patch('infrastructure.chaos.experiment_runner.ChaosMonitor')
    async def test_run_experiment_failure(self, mock_monitor, mock_injector, experiment_execution):
        """Testa execução com falha"""
        # Mock de falha
        experiment_execution._run_phase = AsyncMock(side_effect=Exception("Test error"))
        experiment_execution._perform_rollback = AsyncMock()
        
        await experiment_execution.run()
        
        assert experiment_execution.result.status == ExperimentStatus.FAILED
        assert "Test error" in experiment_execution.result.issues_found
        experiment_execution._perform_rollback.assert_called_once()
    
    async def test_run_phase(self, experiment_execution):
        """Testa execução de fase individual"""
        phase_func = AsyncMock()
        
        await experiment_execution._run_phase(ExperimentPhase.PREPARATION, phase_func)
        
        assert experiment_execution.current_phase == ExperimentPhase.PREPARATION
        assert ExperimentPhase.PREPARATION in experiment_execution.result.phases_completed
        phase_func.assert_called_once()
    
    async def test_prepare_experiment(self, experiment_execution):
        """Testa fase de preparação"""
        experiment_execution._check_prerequisites = AsyncMock()
        
        await experiment_execution._prepare_experiment()
        
        experiment_execution._check_prerequisites.assert_called_once()
    
    async def test_measure_steady_state(self, experiment_execution):
        """Testa medição do estado estável"""
        experiment_execution.monitor.collect_metrics = AsyncMock()
        experiment_execution.config.steady_state_duration = 1  # 1 segundo para teste
        
        await experiment_execution._measure_steady_state()
        
        # Verificar que métricas foram coletadas
        assert len(experiment_execution.result.metrics) > 0
    
    async def test_inject_chaos(self, experiment_execution):
        """Testa injeção de caos"""
        experiment_execution.failure_injector.inject_failure = AsyncMock()
        experiment_execution.monitor.collect_metrics = AsyncMock()
        experiment_execution.config.chaos_duration = 1  # 1 segundo para teste
        
        await experiment_execution._inject_chaos()
        
        experiment_execution.failure_injector.inject_failure.assert_called()
    
    async def test_observe_system(self, experiment_execution):
        """Testa observação do sistema"""
        experiment_execution.monitor.collect_metrics = AsyncMock()
        experiment_execution.config.observation_duration = 1  # 1 segundo para teste
        
        await experiment_execution._observe_system()
        
        # Verificar que métricas foram coletadas
        assert len(experiment_execution.result.metrics) > 0
    
    async def test_recover_system(self, experiment_execution):
        """Testa recuperação do sistema"""
        experiment_execution.failure_injector.revert_failure = AsyncMock()
        experiment_execution.monitor.collect_metrics = AsyncMock()
        
        await experiment_execution._recover_system()
        
        experiment_execution.failure_injector.revert_failure.assert_called()
    
    async def test_analyze_results(self, experiment_execution):
        """Testa análise de resultados"""
        # Adicionar métricas mock
        experiment_execution.result.metrics = [
            ExperimentMetrics(
                timestamp=datetime.now(),
                cpu_usage=50.0,
                memory_usage=60.0,
                response_time=100.0,
                error_rate=0.01,
                throughput=1000.0,
                availability=99.9,
                custom_metrics={}
            )
        ]
        
        await experiment_execution._analyze_results()
        
        # Verificar que análise foi realizada
        assert experiment_execution.result.hypothesis_validated is not None
    
    def test_should_rollback(self, experiment_execution):
        """Testa decisão de rollback"""
        # Métricas que indicam necessidade de rollback
        high_impact_metrics = ExperimentMetrics(
            timestamp=datetime.now(),
            cpu_usage=95.0,
            memory_usage=90.0,
            response_time=2000.0,
            error_rate=0.8,
            throughput=100.0,
            availability=50.0,
            custom_metrics={}
        )
        
        should_rollback = experiment_execution._should_rollback(high_impact_metrics)
        
        assert should_rollback is True
    
    def test_is_system_recovered(self, experiment_execution):
        """Testa verificação de recuperação do sistema"""
        # Métricas de sistema recuperado
        recovered_metrics = ExperimentMetrics(
            timestamp=datetime.now(),
            cpu_usage=30.0,
            memory_usage=40.0,
            response_time=150.0,
            error_rate=0.01,
            throughput=1200.0,
            availability=99.5,
            custom_metrics={}
        )
        
        is_recovered = experiment_execution._is_system_recovered(recovered_metrics)
        
        assert is_recovered is True
    
    async def test_stop_execution(self, experiment_execution):
        """Testa parada de execução"""
        experiment_execution.stop_requested = False
        
        result = await experiment_execution.stop()
        
        assert result is True
        assert experiment_execution.stop_requested is True


class TestExperimentRunnerIntegration:
    """Testes de integração para ExperimentRunner"""
    
    @patch('infrastructure.chaos.experiment_runner.Path')
    @patch('builtins.open', create=True)
    async def test_full_experiment_lifecycle(self, mock_open, mock_path):
        """Testa ciclo completo de vida de um experimento"""
        # Mock de configuração
        mock_path.return_value.exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = """
        experiments:
          - name: integration_test
            description: Integration test
            type: network_latency
            hypothesis: Integration test hypothesis
            duration: 10
            steady_state_duration: 2
            chaos_duration: 3
            observation_duration: 2
            max_impact: 0.5
            auto_rollback: true
        """
        
        # Criar runner
        runner = ExperimentRunner(config_path="test_config.yaml")
        
        # Executar experimento
        experiment_id = await runner.run_experiment("integration_test")
        
        # Verificar que experimento foi iniciado
        assert experiment_id is not None
        assert "integration_test_" in experiment_id
        
        # Aguardar um pouco para execução
        await asyncio.sleep(0.1)
        
        # Verificar status
        status = await runner.get_experiment_status(experiment_id)
        assert status in [ExperimentStatus.RUNNING, ExperimentStatus.COMPLETED, ExperimentStatus.FAILED]


class TestExperimentRunnerErrorHandling:
    """Testes de tratamento de erro para ExperimentRunner"""
    
    @patch('infrastructure.chaos.experiment_runner.Path')
    async def test_experiment_runner_with_invalid_config(self, mock_path):
        """Testa comportamento com configuração inválida"""
        mock_path.return_value.exists.return_value = True
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.side_effect = yaml.YAMLError("Invalid YAML")
            
            runner = ExperimentRunner(config_path="invalid.yaml")
            assert len(runner.experiments) == 0
    
    async def test_experiment_execution_with_invalid_phase(self, sample_config, mock_runner):
        """Testa execução com fase inválida"""
        with patch('infrastructure.chaos.experiment_runner.FailureInjector'):
            with patch('infrastructure.chaos.experiment_runner.ChaosMonitor'):
                execution = ExperimentExecution(sample_config, mock_runner)
                
                # Mock de fase que falha
                execution._run_phase = AsyncMock(side_effect=Exception("Phase error"))
                
                await execution.run()
                
                assert execution.result.status == ExperimentStatus.FAILED
                assert "Phase error" in execution.result.issues_found


class TestExperimentRunnerPerformance:
    """Testes de performance para ExperimentRunner"""
    
    @patch('infrastructure.chaos.experiment_runner.Path')
    @patch('builtins.open', create=True)
    async def test_experiment_runner_initialization_performance(self, mock_open, mock_path):
        """Testa performance de inicialização"""
        mock_path.return_value.exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = "experiments: []"
        
        start_time = time.time()
        runner = ExperimentRunner(config_path="perf_test.yaml")
        end_time = time.time()
        
        # Inicialização deve ser rápida (< 1 segundo)
        assert (end_time - start_time) < 1.0
    
    async def test_experiment_execution_performance(self, sample_config, mock_runner):
        """Testa performance de execução"""
        with patch('infrastructure.chaos.experiment_runner.FailureInjector'):
            with patch('infrastructure.chaos.experiment_runner.ChaosMonitor'):
                execution = ExperimentExecution(sample_config, mock_runner)
                
                # Configurar durações mínimas para teste
                execution.config.steady_state_duration = 0.1
                execution.config.chaos_duration = 0.1
                execution.config.observation_duration = 0.1
                
                start_time = time.time()
                await execution.run()
                end_time = time.time()
                
                # Execução deve ser rápida para teste
                assert (end_time - start_time) < 5.0


def test_create_experiment_runner():
    """Testa função factory create_experiment_runner"""
    with patch('infrastructure.chaos.experiment_runner.ExperimentRunner') as mock_runner_class:
        mock_runner = Mock()
        mock_runner_class.return_value = mock_runner
        
        runner = create_experiment_runner("test_config.yaml")
        
        assert runner == mock_runner
        mock_runner_class.assert_called_once_with(config_path="test_config.yaml") 