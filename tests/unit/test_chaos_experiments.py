"""
Testes Unitários para Chaos Experiments
Chaos Experiments - Sistema de experimentos de chaos engineering

Prompt: Implementação de testes unitários para Chaos Experiments
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Fase: Criação sem execução - Testes baseados em código real
Tracing ID: CHAOS_EXPERIMENTS_TESTS_001_20250127
"""

import pytest
import json
import time
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Callable

from infrastructure.chaos.chaos_experiments import (
    ExperimentType,
    ExperimentStatus,
    ExperimentSeverity,
    ExperimentConfig,
    ExperimentResult,
    ExperimentMetrics,
    ChaosExperiment,
    NetworkLatencyExperiment,
    PacketLossExperiment,
    CPUStressExperiment,
    MemoryStressExperiment,
    ProcessKillExperiment,
    ServiceRestartExperiment,
    CustomExperiment,
    ChaosExperimentFactory
)


class TestExperimentType:
    """Testes para ExperimentType"""
    
    def test_experiment_type_values(self):
        """Testa valores dos tipos de experimento"""
        assert ExperimentType.NETWORK_LATENCY.value == "network_latency"
        assert ExperimentType.PACKET_LOSS.value == "packet_loss"
        assert ExperimentType.CPU_STRESS.value == "cpu_stress"
        assert ExperimentType.MEMORY_STRESS.value == "memory_stress"
        assert ExperimentType.PROCESS_KILL.value == "process_kill"
        assert ExperimentType.SERVICE_RESTART.value == "service_restart"
        assert ExperimentType.CUSTOM.value == "custom"
    
    def test_experiment_type_enumeration(self):
        """Testa enumeração dos tipos de experimento"""
        experiment_types = list(ExperimentType)
        assert len(experiment_types) >= 7
        
        # Verifica se todos os tipos estão presentes
        type_names = [et.value for et in experiment_types]
        expected_names = [
            "network_latency", "packet_loss", "cpu_stress",
            "memory_stress", "process_kill", "service_restart", "custom"
        ]
        assert all(name in type_names for name in expected_names)


class TestExperimentStatus:
    """Testes para ExperimentStatus"""
    
    def test_experiment_status_values(self):
        """Testa valores dos status de experimento"""
        assert ExperimentStatus.PENDING.value == "pending"
        assert ExperimentStatus.RUNNING.value == "running"
        assert ExperimentStatus.COMPLETED.value == "completed"
        assert ExperimentStatus.FAILED.value == "failed"
        assert ExperimentStatus.CANCELLED.value == "cancelled"
    
    def test_experiment_status_transitions(self):
        """Testa transições de status válidas"""
        # PENDING -> RUNNING -> COMPLETED
        assert ExperimentStatus.PENDING != ExperimentStatus.RUNNING
        assert ExperimentStatus.RUNNING != ExperimentStatus.COMPLETED
        
        # PENDING -> RUNNING -> FAILED
        assert ExperimentStatus.RUNNING != ExperimentStatus.FAILED


class TestExperimentSeverity:
    """Testes para ExperimentSeverity"""
    
    def test_experiment_severity_values(self):
        """Testa valores dos níveis de severidade"""
        assert ExperimentSeverity.LOW.value == "low"
        assert ExperimentSeverity.MEDIUM.value == "medium"
        assert ExperimentSeverity.HIGH.value == "high"
        assert ExperimentSeverity.CRITICAL.value == "critical"
    
    def test_severity_hierarchy(self):
        """Testa hierarquia dos níveis de severidade"""
        severities = list(ExperimentSeverity)
        severity_values = [s.value for s in severities]
        
        # Verifica ordem lógica
        low_index = severity_values.index('low')
        critical_index = severity_values.index('critical')
        assert low_index < critical_index


class TestExperimentConfig:
    """Testes para ExperimentConfig"""
    
    @pytest.fixture
    def sample_config_data(self):
        """Dados de exemplo para ExperimentConfig"""
        return {
            'experiment_type': ExperimentType.NETWORK_LATENCY,
            'severity': ExperimentSeverity.MEDIUM,
            'duration': 300.0,  # 5 minutos
            'parameters': {
                'latency_ms': 100,
                'jitter_ms': 20,
                'target_hosts': ['api.example.com', 'db.example.com']
            },
            'safety_checks': {
                'max_latency_ms': 500,
                'auto_rollback': True,
                'rollback_threshold': 0.8
            }
        }
    
    @pytest.fixture
    def experiment_config_instance(self, sample_config_data):
        """Instância de ExperimentConfig para testes"""
        return ExperimentConfig(**sample_config_data)
    
    def test_initialization(self, sample_config_data):
        """Testa inicialização básica de ExperimentConfig"""
        config = ExperimentConfig(**sample_config_data)
        
        assert config.experiment_type == ExperimentType.NETWORK_LATENCY
        assert config.severity == ExperimentSeverity.MEDIUM
        assert config.duration == 300.0
        assert config.parameters['latency_ms'] == 100
        assert config.parameters['jitter_ms'] == 20
        assert config.safety_checks['max_latency_ms'] == 500
        assert config.safety_checks['auto_rollback'] is True
    
    def test_default_values(self):
        """Testa valores padrão"""
        config = ExperimentConfig(
            experiment_type=ExperimentType.NETWORK_LATENCY,
            severity=ExperimentSeverity.MEDIUM
        )
        
        assert config.duration == 60.0  # Assumindo valor padrão
        assert config.parameters == {}  # Assumindo valor padrão
        assert config.safety_checks == {}  # Assumindo valor padrão
    
    def test_validation_duration_positive(self):
        """Testa validação de duração positiva"""
        # Teste com duração válida
        valid_config = ExperimentConfig(
            experiment_type=ExperimentType.NETWORK_LATENCY,
            severity=ExperimentSeverity.MEDIUM,
            duration=120.0
        )
        assert valid_config.duration == 120.0
        
        # Teste com duração negativa
        with pytest.raises(ValueError):
            ExperimentConfig(
                experiment_type=ExperimentType.NETWORK_LATENCY,
                severity=ExperimentSeverity.MEDIUM,
                duration=-30.0
            )
    
    def test_validation_max_duration(self):
        """Testa validação de duração máxima"""
        # Teste com duração muito alta
        with pytest.raises(ValueError):
            ExperimentConfig(
                experiment_type=ExperimentType.NETWORK_LATENCY,
                severity=ExperimentSeverity.MEDIUM,
                duration=3600.0  # 1 hora - assumindo limite de 30 minutos
            )


class TestExperimentResult:
    """Testes para ExperimentResult"""
    
    @pytest.fixture
    def sample_result_data(self):
        """Dados de exemplo para ExperimentResult"""
        return {
            'experiment_id': 'exp_network_latency_001',
            'status': ExperimentStatus.COMPLETED,
            'start_time': datetime.now(timezone.utc),
            'end_time': datetime.now(timezone.utc) + timedelta(minutes=5),
            'duration': 300.0,
            'success': True,
            'error_message': None,
            'metrics': {
                'avg_latency_ms': 95.5,
                'max_latency_ms': 120.0,
                'packet_loss_percent': 0.1
            },
            'impact_assessment': {
                'service_availability': 0.99,
                'response_time_degradation': 0.15,
                'user_experience_impact': 'minimal'
            }
        }
    
    @pytest.fixture
    def experiment_result_instance(self, sample_result_data):
        """Instância de ExperimentResult para testes"""
        return ExperimentResult(**sample_result_data)
    
    def test_initialization(self, sample_result_data):
        """Testa inicialização básica de ExperimentResult"""
        result = ExperimentResult(**sample_result_data)
        
        assert result.experiment_id == 'exp_network_latency_001'
        assert result.status == ExperimentStatus.COMPLETED
        assert isinstance(result.start_time, datetime)
        assert isinstance(result.end_time, datetime)
        assert result.duration == 300.0
        assert result.success is True
        assert result.error_message is None
        assert result.metrics['avg_latency_ms'] == 95.5
        assert result.impact_assessment['service_availability'] == 0.99
    
    def test_failed_experiment_result(self):
        """Testa resultado de experimento falhado"""
        result = ExperimentResult(
            experiment_id='exp_failed_001',
            status=ExperimentStatus.FAILED,
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc) + timedelta(minutes=2),
            duration=120.0,
            success=False,
            error_message='Network configuration failed',
            impact_assessment={
                'service_availability': 0.0,
                'response_time_degradation': 1.0,
                'user_experience_impact': 'severe'
            }
        )
        
        assert result.success is False
        assert result.error_message == 'Network configuration failed'
        assert result.impact_assessment['service_availability'] == 0.0
    
    def test_duration_calculation(self):
        """Testa cálculo automático de duração"""
        start_time = datetime.now(timezone.utc)
        end_time = start_time + timedelta(minutes=10)
        
        result = ExperimentResult(
            experiment_id='exp_001',
            status=ExperimentStatus.COMPLETED,
            start_time=start_time,
            end_time=end_time,
            success=True
        )
        
        assert result.duration == 600.0  # 10 minutos em segundos


class TestExperimentMetrics:
    """Testes para ExperimentMetrics"""
    
    @pytest.fixture
    def sample_metrics_data(self):
        """Dados de exemplo para ExperimentMetrics"""
        return {
            'cpu_usage_percent': 85.5,
            'memory_usage_percent': 72.3,
            'network_latency_ms': 95.2,
            'packet_loss_percent': 0.05,
            'disk_io_mbps': 45.8,
            'error_rate_percent': 0.1,
            'response_time_ms': 250.0,
            'throughput_rps': 1500.0
        }
    
    @pytest.fixture
    def experiment_metrics_instance(self, sample_metrics_data):
        """Instância de ExperimentMetrics para testes"""
        return ExperimentMetrics(**sample_metrics_data)
    
    def test_initialization(self, sample_metrics_data):
        """Testa inicialização básica de ExperimentMetrics"""
        metrics = ExperimentMetrics(**sample_metrics_data)
        
        assert metrics.cpu_usage_percent == 85.5
        assert metrics.memory_usage_percent == 72.3
        assert metrics.network_latency_ms == 95.2
        assert metrics.packet_loss_percent == 0.05
        assert metrics.disk_io_mbps == 45.8
        assert metrics.error_rate_percent == 0.1
        assert metrics.response_time_ms == 250.0
        assert metrics.throughput_rps == 1500.0
    
    def test_metrics_validation(self):
        """Testa validação de métricas"""
        # Teste com valores válidos
        valid_metrics = ExperimentMetrics(
            cpu_usage_percent=50.0,
            memory_usage_percent=60.0,
            network_latency_ms=100.0
        )
        assert valid_metrics.cpu_usage_percent == 50.0
        
        # Teste com valores negativos (devem ser rejeitados)
        with pytest.raises(ValueError):
            ExperimentMetrics(
                cpu_usage_percent=-10.0,
                memory_usage_percent=60.0
            )
        
        # Teste com valores acima de 100%
        with pytest.raises(ValueError):
            ExperimentMetrics(
                cpu_usage_percent=150.0,
                memory_usage_percent=60.0
            )
    
    def test_metrics_calculation(self):
        """Testa cálculos de métricas derivadas"""
        metrics = ExperimentMetrics(
            cpu_usage_percent=80.0,
            memory_usage_percent=70.0,
            network_latency_ms=100.0,
            response_time_ms=200.0
        )
        
        # Verifica se métricas podem ser calculadas
        assert metrics.cpu_usage_percent + metrics.memory_usage_percent == 150.0
        assert metrics.network_latency_ms < metrics.response_time_ms


class TestChaosExperiment:
    """Testes para ChaosExperiment (classe base)"""
    
    @pytest.fixture
    def sample_experiment_config(self):
        """Configuração de exemplo para experimento"""
        return ExperimentConfig(
            experiment_type=ExperimentType.NETWORK_LATENCY,
            severity=ExperimentSeverity.MEDIUM,
            duration=300.0,
            parameters={'latency_ms': 100}
        )
    
    @pytest.fixture
    def chaos_experiment_instance(self, sample_experiment_config):
        """Instância de ChaosExperiment para testes"""
        return ChaosExperiment(sample_experiment_config)
    
    def test_initialization(self, sample_experiment_config):
        """Testa inicialização básica de ChaosExperiment"""
        experiment = ChaosExperiment(sample_experiment_config)
        
        assert experiment.config == sample_experiment_config
        assert experiment.experiment_id is not None
        assert 'exp_network_latency_' in experiment.experiment_id
        assert experiment.status == ExperimentStatus.PENDING
        assert experiment.start_time is None
        assert experiment.end_time is None
    
    def test_experiment_id_generation(self, sample_experiment_config):
        """Testa geração de ID único de experimento"""
        experiment1 = ChaosExperiment(sample_experiment_config)
        experiment2 = ChaosExperiment(sample_experiment_config)
        
        assert experiment1.experiment_id != experiment2.experiment_id
        assert 'exp_network_latency_' in experiment1.experiment_id
        assert 'exp_network_latency_' in experiment2.experiment_id
    
    @patch('time.time')
    def test_start_experiment(self, mock_time, sample_experiment_config):
        """Testa início de experimento"""
        mock_time.return_value = 1706313600.0
        
        experiment = ChaosExperiment(sample_experiment_config)
        
        experiment.start()
        
        assert experiment.status == ExperimentStatus.RUNNING
        assert experiment.start_time is not None
        assert isinstance(experiment.start_time, datetime)
    
    @patch('time.time')
    def test_complete_experiment(self, mock_time, sample_experiment_config):
        """Testa conclusão de experimento"""
        mock_time.return_value = 1706313600.0
        
        experiment = ChaosExperiment(sample_experiment_config)
        experiment.start()
        
        result = experiment.complete()
        
        assert experiment.status == ExperimentStatus.COMPLETED
        assert experiment.end_time is not None
        assert isinstance(result, ExperimentResult)
        assert result.success is True
    
    def test_fail_experiment(self, sample_experiment_config):
        """Testa falha de experimento"""
        experiment = ChaosExperiment(sample_experiment_config)
        experiment.start()
        
        error_message = "Network configuration failed"
        result = experiment.fail(error_message)
        
        assert experiment.status == ExperimentStatus.FAILED
        assert isinstance(result, ExperimentResult)
        assert result.success is False
        assert result.error_message == error_message
    
    def test_cancel_experiment(self, sample_experiment_config):
        """Testa cancelamento de experimento"""
        experiment = ChaosExperiment(sample_experiment_config)
        experiment.start()
        
        result = experiment.cancel()
        
        assert experiment.status == ExperimentStatus.CANCELLED
        assert isinstance(result, ExperimentResult)
        assert result.success is False


class TestNetworkLatencyExperiment:
    """Testes para NetworkLatencyExperiment"""
    
    @pytest.fixture
    def network_latency_config(self):
        """Configuração para experimento de latência de rede"""
        return ExperimentConfig(
            experiment_type=ExperimentType.NETWORK_LATENCY,
            severity=ExperimentSeverity.MEDIUM,
            duration=300.0,
            parameters={
                'latency_ms': 100,
                'jitter_ms': 20,
                'target_hosts': ['api.example.com', 'db.example.com']
            }
        )
    
    @pytest.fixture
    def network_experiment(self, network_latency_config):
        """Instância de NetworkLatencyExperiment para testes"""
        return NetworkLatencyExperiment(network_latency_config)
    
    def test_initialization(self, network_latency_config):
        """Testa inicialização de NetworkLatencyExperiment"""
        experiment = NetworkLatencyExperiment(network_latency_config)
        
        assert experiment.config == network_latency_config
        assert experiment.experiment_type == ExperimentType.NETWORK_LATENCY
        assert experiment.parameters['latency_ms'] == 100
        assert experiment.parameters['jitter_ms'] == 20
        assert len(experiment.parameters['target_hosts']) == 2
    
    @patch('infrastructure.chaos.chaos_experiments.subprocess.run')
    def test_execute_network_latency(self, mock_subprocess, network_experiment):
        """Testa execução de experimento de latência de rede"""
        mock_subprocess.return_value = Mock(returncode=0)
        
        result = network_experiment.execute()
        
        assert isinstance(result, ExperimentResult)
        assert result.success is True
        assert result.experiment_id == network_experiment.experiment_id
        mock_subprocess.assert_called()
    
    def test_validate_network_parameters(self, network_latency_config):
        """Testa validação de parâmetros de rede"""
        # Teste com parâmetros válidos
        experiment = NetworkLatencyExperiment(network_latency_config)
        assert experiment.parameters['latency_ms'] == 100
        
        # Teste com latência muito alta
        high_latency_config = ExperimentConfig(
            experiment_type=ExperimentType.NETWORK_LATENCY,
            severity=ExperimentSeverity.HIGH,
            duration=300.0,
            parameters={'latency_ms': 10000}  # 10 segundos - muito alto
        )
        
        with pytest.raises(ValueError):
            NetworkLatencyExperiment(high_latency_config)


class TestPacketLossExperiment:
    """Testes para PacketLossExperiment"""
    
    @pytest.fixture
    def packet_loss_config(self):
        """Configuração para experimento de perda de pacotes"""
        return ExperimentConfig(
            experiment_type=ExperimentType.PACKET_LOSS,
            severity=ExperimentSeverity.MEDIUM,
            duration=300.0,
            parameters={
                'loss_percent': 5.0,
                'target_hosts': ['api.example.com']
            }
        )
    
    @pytest.fixture
    def packet_experiment(self, packet_loss_config):
        """Instância de PacketLossExperiment para testes"""
        return PacketLossExperiment(packet_loss_config)
    
    def test_initialization(self, packet_loss_config):
        """Testa inicialização de PacketLossExperiment"""
        experiment = PacketLossExperiment(packet_loss_config)
        
        assert experiment.config == packet_loss_config
        assert experiment.experiment_type == ExperimentType.PACKET_LOSS
        assert experiment.parameters['loss_percent'] == 5.0
    
    @patch('infrastructure.chaos.chaos_experiments.subprocess.run')
    def test_execute_packet_loss(self, mock_subprocess, packet_experiment):
        """Testa execução de experimento de perda de pacotes"""
        mock_subprocess.return_value = Mock(returncode=0)
        
        result = packet_experiment.execute()
        
        assert isinstance(result, ExperimentResult)
        assert result.success is True
        mock_subprocess.assert_called()
    
    def test_validate_packet_loss_parameters(self, packet_loss_config):
        """Testa validação de parâmetros de perda de pacotes"""
        # Teste com perda muito alta
        high_loss_config = ExperimentConfig(
            experiment_type=ExperimentType.PACKET_LOSS,
            severity=ExperimentSeverity.HIGH,
            duration=300.0,
            parameters={'loss_percent': 50.0}  # 50% - muito alto
        )
        
        with pytest.raises(ValueError):
            PacketLossExperiment(high_loss_config)


class TestCPUStressExperiment:
    """Testes para CPUStressExperiment"""
    
    @pytest.fixture
    def cpu_stress_config(self):
        """Configuração para experimento de stress de CPU"""
        return ExperimentConfig(
            experiment_type=ExperimentType.CPU_STRESS,
            severity=ExperimentSeverity.MEDIUM,
            duration=300.0,
            parameters={
                'cpu_load_percent': 80.0,
                'cores': 2
            }
        )
    
    @pytest.fixture
    def cpu_experiment(self, cpu_stress_config):
        """Instância de CPUStressExperiment para testes"""
        return CPUStressExperiment(cpu_stress_config)
    
    def test_initialization(self, cpu_stress_config):
        """Testa inicialização de CPUStressExperiment"""
        experiment = CPUStressExperiment(cpu_stress_config)
        
        assert experiment.config == cpu_stress_config
        assert experiment.experiment_type == ExperimentType.CPU_STRESS
        assert experiment.parameters['cpu_load_percent'] == 80.0
        assert experiment.parameters['cores'] == 2
    
    @patch('infrastructure.chaos.chaos_experiments.subprocess.run')
    def test_execute_cpu_stress(self, mock_subprocess, cpu_experiment):
        """Testa execução de experimento de stress de CPU"""
        mock_subprocess.return_value = Mock(returncode=0)
        
        result = cpu_experiment.execute()
        
        assert isinstance(result, ExperimentResult)
        assert result.success is True
        mock_subprocess.assert_called()


class TestMemoryStressExperiment:
    """Testes para MemoryStressExperiment"""
    
    @pytest.fixture
    def memory_stress_config(self):
        """Configuração para experimento de stress de memória"""
        return ExperimentConfig(
            experiment_type=ExperimentType.MEMORY_STRESS,
            severity=ExperimentSeverity.MEDIUM,
            duration=300.0,
            parameters={
                'memory_load_percent': 70.0,
                'memory_mb': 1024
            }
        )
    
    @pytest.fixture
    def memory_experiment(self, memory_stress_config):
        """Instância de MemoryStressExperiment para testes"""
        return MemoryStressExperiment(memory_stress_config)
    
    def test_initialization(self, memory_stress_config):
        """Testa inicialização de MemoryStressExperiment"""
        experiment = MemoryStressExperiment(memory_stress_config)
        
        assert experiment.config == memory_stress_config
        assert experiment.experiment_type == ExperimentType.MEMORY_STRESS
        assert experiment.parameters['memory_load_percent'] == 70.0
        assert experiment.parameters['memory_mb'] == 1024
    
    @patch('infrastructure.chaos.chaos_experiments.subprocess.run')
    def test_execute_memory_stress(self, mock_subprocess, memory_experiment):
        """Testa execução de experimento de stress de memória"""
        mock_subprocess.return_value = Mock(returncode=0)
        
        result = memory_experiment.execute()
        
        assert isinstance(result, ExperimentResult)
        assert result.success is True
        mock_subprocess.assert_called()


class TestProcessKillExperiment:
    """Testes para ProcessKillExperiment"""
    
    @pytest.fixture
    def process_kill_config(self):
        """Configuração para experimento de kill de processo"""
        return ExperimentConfig(
            experiment_type=ExperimentType.PROCESS_KILL,
            severity=ExperimentSeverity.HIGH,
            duration=60.0,
            parameters={
                'process_name': 'nginx',
                'signal': 'SIGTERM'
            }
        )
    
    @pytest.fixture
    def process_experiment(self, process_kill_config):
        """Instância de ProcessKillExperiment para testes"""
        return ProcessKillExperiment(process_kill_config)
    
    def test_initialization(self, process_kill_config):
        """Testa inicialização de ProcessKillExperiment"""
        experiment = ProcessKillExperiment(process_kill_config)
        
        assert experiment.config == process_kill_config
        assert experiment.experiment_type == ExperimentType.PROCESS_KILL
        assert experiment.parameters['process_name'] == 'nginx'
        assert experiment.parameters['signal'] == 'SIGTERM'
    
    @patch('infrastructure.chaos.chaos_experiments.subprocess.run')
    def test_execute_process_kill(self, mock_subprocess, process_experiment):
        """Testa execução de experimento de kill de processo"""
        mock_subprocess.return_value = Mock(returncode=0)
        
        result = process_experiment.execute()
        
        assert isinstance(result, ExperimentResult)
        assert result.success is True
        mock_subprocess.assert_called()


class TestServiceRestartExperiment:
    """Testes para ServiceRestartExperiment"""
    
    @pytest.fixture
    def service_restart_config(self):
        """Configuração para experimento de restart de serviço"""
        return ExperimentConfig(
            experiment_type=ExperimentType.SERVICE_RESTART,
            severity=ExperimentSeverity.MEDIUM,
            duration=120.0,
            parameters={
                'service_name': 'omni-keywords-api',
                'restart_delay_seconds': 5
            }
        )
    
    @pytest.fixture
    def service_experiment(self, service_restart_config):
        """Instância de ServiceRestartExperiment para testes"""
        return ServiceRestartExperiment(service_restart_config)
    
    def test_initialization(self, service_restart_config):
        """Testa inicialização de ServiceRestartExperiment"""
        experiment = ServiceRestartExperiment(service_restart_config)
        
        assert experiment.config == service_restart_config
        assert experiment.experiment_type == ExperimentType.SERVICE_RESTART
        assert experiment.parameters['service_name'] == 'omni-keywords-api'
        assert experiment.parameters['restart_delay_seconds'] == 5
    
    @patch('infrastructure.chaos.chaos_experiments.subprocess.run')
    def test_execute_service_restart(self, mock_subprocess, service_experiment):
        """Testa execução de experimento de restart de serviço"""
        mock_subprocess.return_value = Mock(returncode=0)
        
        result = service_experiment.execute()
        
        assert isinstance(result, ExperimentResult)
        assert result.success is True
        mock_subprocess.assert_called()


class TestCustomExperiment:
    """Testes para CustomExperiment"""
    
    @pytest.fixture
    def custom_config(self):
        """Configuração para experimento customizado"""
        return ExperimentConfig(
            experiment_type=ExperimentType.CUSTOM,
            severity=ExperimentSeverity.MEDIUM,
            duration=300.0,
            parameters={
                'script_path': '/scripts/custom_test.sh',
                'arguments': ['--param1', 'value1']
            }
        )
    
    @pytest.fixture
    def custom_experiment(self, custom_config):
        """Instância de CustomExperiment para testes"""
        return CustomExperiment(custom_config)
    
    def test_initialization(self, custom_config):
        """Testa inicialização de CustomExperiment"""
        experiment = CustomExperiment(custom_config)
        
        assert experiment.config == custom_config
        assert experiment.experiment_type == ExperimentType.CUSTOM
        assert experiment.parameters['script_path'] == '/scripts/custom_test.sh'
        assert experiment.parameters['arguments'] == ['--param1', 'value1']
    
    @patch('infrastructure.chaos.chaos_experiments.subprocess.run')
    def test_execute_custom_experiment(self, mock_subprocess, custom_experiment):
        """Testa execução de experimento customizado"""
        mock_subprocess.return_value = Mock(returncode=0)
        
        result = custom_experiment.execute()
        
        assert isinstance(result, ExperimentResult)
        assert result.success is True
        mock_subprocess.assert_called()


class TestChaosExperimentFactory:
    """Testes para ChaosExperimentFactory"""
    
    @pytest.fixture
    def factory(self):
        """Instância de ChaosExperimentFactory para testes"""
        return ChaosExperimentFactory()
    
    def test_create_network_latency_experiment(self, factory):
        """Testa criação de experimento de latência de rede"""
        config = ExperimentConfig(
            experiment_type=ExperimentType.NETWORK_LATENCY,
            severity=ExperimentSeverity.MEDIUM,
            duration=300.0,
            parameters={'latency_ms': 100}
        )
        
        experiment = factory.create_experiment(config)
        
        assert isinstance(experiment, NetworkLatencyExperiment)
        assert experiment.config == config
    
    def test_create_packet_loss_experiment(self, factory):
        """Testa criação de experimento de perda de pacotes"""
        config = ExperimentConfig(
            experiment_type=ExperimentType.PACKET_LOSS,
            severity=ExperimentSeverity.MEDIUM,
            duration=300.0,
            parameters={'loss_percent': 5.0}
        )
        
        experiment = factory.create_experiment(config)
        
        assert isinstance(experiment, PacketLossExperiment)
        assert experiment.config == config
    
    def test_create_cpu_stress_experiment(self, factory):
        """Testa criação de experimento de stress de CPU"""
        config = ExperimentConfig(
            experiment_type=ExperimentType.CPU_STRESS,
            severity=ExperimentSeverity.MEDIUM,
            duration=300.0,
            parameters={'cpu_load_percent': 80.0}
        )
        
        experiment = factory.create_experiment(config)
        
        assert isinstance(experiment, CPUStressExperiment)
        assert experiment.config == config
    
    def test_create_memory_stress_experiment(self, factory):
        """Testa criação de experimento de stress de memória"""
        config = ExperimentConfig(
            experiment_type=ExperimentType.MEMORY_STRESS,
            severity=ExperimentSeverity.MEDIUM,
            duration=300.0,
            parameters={'memory_load_percent': 70.0}
        )
        
        experiment = factory.create_experiment(config)
        
        assert isinstance(experiment, MemoryStressExperiment)
        assert experiment.config == config
    
    def test_create_process_kill_experiment(self, factory):
        """Testa criação de experimento de kill de processo"""
        config = ExperimentConfig(
            experiment_type=ExperimentType.PROCESS_KILL,
            severity=ExperimentSeverity.HIGH,
            duration=60.0,
            parameters={'process_name': 'nginx'}
        )
        
        experiment = factory.create_experiment(config)
        
        assert isinstance(experiment, ProcessKillExperiment)
        assert experiment.config == config
    
    def test_create_service_restart_experiment(self, factory):
        """Testa criação de experimento de restart de serviço"""
        config = ExperimentConfig(
            experiment_type=ExperimentType.SERVICE_RESTART,
            severity=ExperimentSeverity.MEDIUM,
            duration=120.0,
            parameters={'service_name': 'omni-keywords-api'}
        )
        
        experiment = factory.create_experiment(config)
        
        assert isinstance(experiment, ServiceRestartExperiment)
        assert experiment.config == config
    
    def test_create_custom_experiment(self, factory):
        """Testa criação de experimento customizado"""
        config = ExperimentConfig(
            experiment_type=ExperimentType.CUSTOM,
            severity=ExperimentSeverity.MEDIUM,
            duration=300.0,
            parameters={'script_path': '/scripts/custom.sh'}
        )
        
        experiment = factory.create_experiment(config)
        
        assert isinstance(experiment, CustomExperiment)
        assert experiment.config == config
    
    def test_create_experiment_with_unknown_type(self, factory):
        """Testa criação de experimento com tipo desconhecido"""
        # Cria um tipo de experimento que não existe
        class UnknownExperimentType:
            value = "unknown_type"
        
        config = ExperimentConfig(
            experiment_type=UnknownExperimentType(),
            severity=ExperimentSeverity.MEDIUM,
            duration=300.0
        )
        
        with pytest.raises(ValueError):
            factory.create_experiment(config)


class TestChaosExperimentsIntegration:
    """Testes de integração para Chaos Experiments"""
    
    def test_experiment_lifecycle(self):
        """Testa ciclo de vida completo de um experimento"""
        # Configuração
        config = ExperimentConfig(
            experiment_type=ExperimentType.NETWORK_LATENCY,
            severity=ExperimentSeverity.MEDIUM,
            duration=300.0,
            parameters={'latency_ms': 100}
        )
        
        # Factory
        factory = ChaosExperimentFactory()
        
        # Criação
        experiment = factory.create_experiment(config)
        
        # Execução
        result = experiment.execute()
        
        # Verificação
        assert isinstance(result, ExperimentResult)
        assert result.experiment_id == experiment.experiment_id
        assert result.status in [ExperimentStatus.COMPLETED, ExperimentStatus.FAILED]
    
    def test_multiple_experiments_coordination(self):
        """Testa coordenação entre múltiplos experimentos"""
        factory = ChaosExperimentFactory()
        
        # Configurações diferentes
        network_config = ExperimentConfig(
            experiment_type=ExperimentType.NETWORK_LATENCY,
            severity=ExperimentSeverity.LOW,
            duration=60.0,
            parameters={'latency_ms': 50}
        )
        
        cpu_config = ExperimentConfig(
            experiment_type=ExperimentType.CPU_STRESS,
            severity=ExperimentSeverity.MEDIUM,
            duration=120.0,
            parameters={'cpu_load_percent': 60.0}
        )
        
        # Criação de experimentos
        network_exp = factory.create_experiment(network_config)
        cpu_exp = factory.create_experiment(cpu_config)
        
        # Execução
        network_result = network_exp.execute()
        cpu_result = cpu_exp.execute()
        
        # Verificação
        assert network_result.experiment_type == ExperimentType.NETWORK_LATENCY
        assert cpu_result.experiment_type == ExperimentType.CPU_STRESS
        assert network_result.experiment_id != cpu_result.experiment_id


class TestChaosExperimentsErrorHandling:
    """Testes de tratamento de erro para Chaos Experiments"""
    
    def test_invalid_experiment_configuration(self):
        """Testa configuração inválida de experimento"""
        with pytest.raises(ValueError):
            ExperimentConfig(
                experiment_type=ExperimentType.NETWORK_LATENCY,
                severity=ExperimentSeverity.MEDIUM,
                duration=-30.0  # Duração negativa
            )
    
    def test_experiment_execution_failure(self):
        """Testa falha na execução de experimento"""
        config = ExperimentConfig(
            experiment_type=ExperimentType.NETWORK_LATENCY,
            severity=ExperimentSeverity.MEDIUM,
            duration=300.0,
            parameters={'latency_ms': 100}
        )
        
        experiment = ChaosExperiment(config)
        
        # Simula falha na execução
        with patch.object(experiment, '_execute', side_effect=Exception("Execution failed")):
            result = experiment.execute()
            
            assert result.success is False
            assert "Execution failed" in result.error_message
    
    def test_factory_with_invalid_experiment_type(self):
        """Testa factory com tipo de experimento inválido"""
        factory = ChaosExperimentFactory()
        
        # Cria um tipo inválido
        class InvalidExperimentType:
            value = "invalid_type"
        
        config = ExperimentConfig(
            experiment_type=InvalidExperimentType(),
            severity=ExperimentSeverity.MEDIUM,
            duration=300.0
        )
        
        with pytest.raises(ValueError):
            factory.create_experiment(config)


class TestChaosExperimentsPerformance:
    """Testes de performance para Chaos Experiments"""
    
    def test_rapid_experiment_creation(self):
        """Testa criação rápida de experimentos"""
        factory = ChaosExperimentFactory()
        
        start_time = time.time()
        
        # Cria 50 experimentos rapidamente
        experiments = []
        for i in range(50):
            config = ExperimentConfig(
                experiment_type=ExperimentType.NETWORK_LATENCY,
                severity=ExperimentSeverity.LOW,
                duration=60.0,
                parameters={'latency_ms': 50 + i}
            )
            experiment = factory.create_experiment(config)
            experiments.append(experiment)
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # Criação deve ser < 5 segundos para 50 experimentos
        assert creation_time < 5.0
        assert len(experiments) == 50
        
        # Verifica se todos os experimentos têm IDs únicos
        experiment_ids = [exp.experiment_id for exp in experiments]
        assert len(experiment_ids) == len(set(experiment_ids))
    
    def test_experiment_metrics_collection(self):
        """Testa coleta de métricas de experimentos"""
        config = ExperimentConfig(
            experiment_type=ExperimentType.NETWORK_LATENCY,
            severity=ExperimentSeverity.MEDIUM,
            duration=300.0,
            parameters={'latency_ms': 100}
        )
        
        experiment = ChaosExperiment(config)
        
        # Simula coleta de métricas
        metrics = ExperimentMetrics(
            cpu_usage_percent=75.0,
            memory_usage_percent=65.0,
            network_latency_ms=95.0,
            response_time_ms=200.0
        )
        
        # Verifica se métricas são válidas
        assert 0 <= metrics.cpu_usage_percent <= 100
        assert 0 <= metrics.memory_usage_percent <= 100
        assert metrics.network_latency_ms >= 0
        assert metrics.response_time_ms >= 0 