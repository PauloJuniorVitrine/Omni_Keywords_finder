"""
Testes Unitários para Injection Strategies
Chaos Engineering - Estratégias de injeção de falhas

Prompt: Implementação de testes unitários para injection_strategies.py
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Fase: Criação sem execução - Testes baseados em código real
Tracing ID: TEST_INJECTION_STRATEGIES_001_20250127
"""

import pytest
import asyncio
import subprocess
import threading
import time
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from infrastructure.chaos.injection_strategies import (
    InjectionType,
    InjectionMode,
    InjectionResult,
    InjectionStrategy,
    NetworkLatencyStrategy,
    NetworkPacketLossStrategy,
    CPUStressStrategy,
    MemoryStressStrategy,
    ServiceFailureStrategy,
    StrategyFactory,
    InjectionOrchestrator,
    create_injection_orchestrator
)


class TestInjectionType:
    """Testes para InjectionType"""

    def test_injection_type_values(self):
        """Testa valores dos tipos de injeção"""
        assert InjectionType.NETWORK_LATENCY.value == "network_latency"
        assert InjectionType.NETWORK_PACKET_LOSS.value == "network_packet_loss"
        assert InjectionType.NETWORK_BANDWIDTH_LIMIT.value == "network_bandwidth_limit"
        assert InjectionType.CPU_STRESS.value == "cpu_stress"
        assert InjectionType.MEMORY_STRESS.value == "memory_stress"
        assert InjectionType.DISK_STRESS.value == "disk_stress"
        assert InjectionType.SERVICE_FAILURE.value == "service_failure"
        assert InjectionType.DATABASE_FAILURE.value == "database_failure"
        assert InjectionType.CACHE_FAILURE.value == "cache_failure"
        assert InjectionType.DEPENDENCY_FAILURE.value == "dependency_failure"
        assert InjectionType.PROCESS_KILL.value == "process_kill"
        assert InjectionType.CONTAINER_FAILURE.value == "container_failure"

    def test_injection_type_enumeration(self):
        """Testa enumeração completa"""
        expected_types = [
            "network_latency", "network_packet_loss", "network_bandwidth_limit",
            "cpu_stress", "memory_stress", "disk_stress", "service_failure",
            "database_failure", "cache_failure", "dependency_failure",
            "process_kill", "container_failure"
        ]
        actual_types = [injection_type.value for injection_type in InjectionType]
        assert actual_types == expected_types


class TestInjectionMode:
    """Testes para InjectionMode"""

    def test_injection_mode_values(self):
        """Testa valores dos modos de injeção"""
        assert InjectionMode.CONTINUOUS.value == "continuous"
        assert InjectionMode.INTERMITTENT.value == "intermittent"
        assert InjectionMode.RANDOM.value == "random"
        assert InjectionMode.BURST.value == "burst"
        assert InjectionMode.GRADUAL.value == "gradual"

    def test_injection_mode_enumeration(self):
        """Testa enumeração completa"""
        expected_modes = ["continuous", "intermittent", "random", "burst", "gradual"]
        actual_modes = [injection_mode.value for injection_mode in InjectionMode]
        assert actual_modes == expected_modes


class TestInjectionResult:
    """Testes para InjectionResult"""

    @pytest.fixture
    def sample_injection_result_data(self):
        """Dados de exemplo para resultado de injeção"""
        return {
            'success': True,
            'injection_id': 'test_injection_001',
            'start_time': datetime.now(),
            'end_time': datetime.now() + timedelta(seconds=30),
            'duration': 30.0,
            'error_message': None,
            'impact_metrics': {'cpu_usage': 0.8, 'memory_usage': 0.6},
            'recovery_time': 5.0
        }

    def test_injection_result_initialization(self, sample_injection_result_data):
        """Testa inicialização de InjectionResult"""
        result = InjectionResult(**sample_injection_result_data)

        assert result.success is True
        assert result.injection_id == 'test_injection_001'
        assert result.duration == 30.0
        assert result.error_message is None
        assert result.impact_metrics['cpu_usage'] == 0.8
        assert result.impact_metrics['memory_usage'] == 0.6
        assert result.recovery_time == 5.0

    def test_injection_result_failed_injection(self):
        """Testa InjectionResult para injeção falhada"""
        result = InjectionResult(
            success=False,
            injection_id='failed_injection_001',
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration=0.0,
            error_message='Test error occurred',
            impact_metrics={},
            recovery_time=None
        )

        assert result.success is False
        assert result.error_message == 'Test error occurred'
        assert result.impact_metrics == {}
        assert result.recovery_time is None

    def test_injection_result_ongoing_injection(self):
        """Testa InjectionResult para injeção em andamento"""
        result = InjectionResult(
            success=True,
            injection_id='ongoing_injection_001',
            start_time=datetime.now(),
            end_time=None,
            duration=None,
            error_message=None,
            impact_metrics={'test_metric': 0.5},
            recovery_time=None
        )

        assert result.success is True
        assert result.end_time is None
        assert result.duration is None
        assert result.recovery_time is None


class TestInjectionStrategy:
    """Testes para InjectionStrategy (classe base)"""

    def test_injection_strategy_initialization(self):
        """Testa inicialização da classe base"""
        config = {'test_param': 'test_value'}
        
        # Criar uma implementação concreta para teste
        class TestStrategy(InjectionStrategy):
            async def inject(self) -> InjectionResult:
                return InjectionResult(
                    success=True,
                    injection_id=self.injection_id,
                    start_time=datetime.now(),
                    end_time=None,
                    duration=None,
                    error_message=None,
                    impact_metrics={}
                )
            
            async def stop(self) -> bool:
                return True
            
            def validate_config(self) -> List[str]:
                return []

        strategy = TestStrategy(config)

        assert strategy.config == config
        assert strategy.injection_id.startswith('TestStrategy_')
        assert strategy.is_active is False
        assert strategy.start_time is None
        assert strategy.stop_time is None
        assert isinstance(strategy.lock, threading.RLock)

    def test_injection_strategy_get_status(self):
        """Testa obtenção de status"""
        class TestStrategy(InjectionStrategy):
            async def inject(self) -> InjectionResult:
                return InjectionResult(
                    success=True,
                    injection_id=self.injection_id,
                    start_time=datetime.now(),
                    end_time=None,
                    duration=None,
                    error_message=None,
                    impact_metrics={}
                )
            
            async def stop(self) -> bool:
                return True
            
            def validate_config(self) -> List[str]:
                return []

        strategy = TestStrategy({'test': 'config'})
        
        # Status inicial
        status = strategy.get_status()
        assert status['injection_id'] == strategy.injection_id
        assert status['is_active'] is False
        assert status['start_time'] is None
        assert status['stop_time'] is None
        assert status['duration'] is None

        # Status após ativação
        strategy.is_active = True
        strategy.start_time = datetime.now()
        strategy.stop_time = datetime.now() + timedelta(seconds=10)
        
        status = strategy.get_status()
        assert status['is_active'] is True
        assert status['start_time'] is not None
        assert status['stop_time'] is not None
        assert status['duration'] is not None


class TestNetworkLatencyStrategy:
    """Testes para NetworkLatencyStrategy"""

    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo"""
        return {
            'latency_ms': 100,
            'jitter_ms': 10,
            'target_interface': 'eth0'
        }

    @pytest.fixture
    def network_latency_strategy(self, sample_config):
        """Instância de NetworkLatencyStrategy para testes"""
        return NetworkLatencyStrategy(sample_config)

    def test_network_latency_strategy_initialization(self, sample_config):
        """Testa inicialização de NetworkLatencyStrategy"""
        strategy = NetworkLatencyStrategy(sample_config)

        assert strategy.latency_ms == 100
        assert strategy.jitter_ms == 10
        assert strategy.target_interface == 'eth0'
        assert strategy.tc_process is None
        assert strategy.injection_id.startswith('NetworkLatencyStrategy_')

    def test_network_latency_strategy_validate_config_valid(self, network_latency_strategy):
        """Testa validação de configuração válida"""
        errors = network_latency_strategy.validate_config()
        assert len(errors) == 0

    def test_network_latency_strategy_validate_config_invalid(self):
        """Testa validação de configuração inválida"""
        # Configuração com latência negativa
        config = {'latency_ms': -10, 'jitter_ms': 5, 'target_interface': 'eth0'}
        strategy = NetworkLatencyStrategy(config)
        errors = strategy.validate_config()
        assert len(errors) > 0
        assert any('Latência deve ser maior ou igual a zero' in error for error in errors)

        # Configuração com jitter negativo
        config = {'latency_ms': 100, 'jitter_ms': -5, 'target_interface': 'eth0'}
        strategy = NetworkLatencyStrategy(config)
        errors = strategy.validate_config()
        assert len(errors) > 0
        assert any('Jitter deve ser maior ou igual a zero' in error for error in errors)

        # Configuração com latência muito alta
        config = {'latency_ms': 15000, 'jitter_ms': 10, 'target_interface': 'eth0'}
        strategy = NetworkLatencyStrategy(config)
        errors = strategy.validate_config()
        assert len(errors) > 0
        assert any('Latência muito alta' in error for error in errors)

    @pytest.mark.asyncio
    async def test_network_latency_strategy_inject_success(self, network_latency_strategy):
        """Testa injeção bem-sucedida de latência"""
        with patch.object(network_latency_strategy, '_check_tc_available', return_value=True), \
             patch('subprocess.Popen') as mock_popen, \
             patch('asyncio.sleep') as mock_sleep:

            # Configurar mock
            mock_process = Mock()
            mock_process.poll.return_value = None
            mock_popen.return_value = mock_process

            result = await network_latency_strategy.inject()

            assert result.success is True
            assert result.injection_id == network_latency_strategy.injection_id
            assert result.error_message is None
            assert result.impact_metrics['latency_ms'] == 100
            assert result.impact_metrics['jitter_ms'] == 10
            assert network_latency_strategy.is_active is True
            assert network_latency_strategy.start_time is not None

    @pytest.mark.asyncio
    async def test_network_latency_strategy_inject_tc_unavailable(self, network_latency_strategy):
        """Testa injeção quando tc não está disponível"""
        with patch.object(network_latency_strategy, '_check_tc_available', return_value=False):

            result = await network_latency_strategy.inject()

            assert result.success is False
            assert 'tc (traffic control) não está disponível' in result.error_message

    @pytest.mark.asyncio
    async def test_network_latency_strategy_stop_success(self, network_latency_strategy):
        """Testa parada bem-sucedida de latência"""
        # Simular injeção ativa
        network_latency_strategy.is_active = True
        network_latency_strategy.start_time = datetime.now()
        network_latency_strategy.tc_process = Mock()

        with patch('subprocess.run') as mock_run:
            result = await network_latency_strategy.stop()

            assert result is True
            assert network_latency_strategy.is_active is False
            assert network_latency_strategy.stop_time is not None
            assert mock_run.called

    @pytest.mark.asyncio
    async def test_network_latency_strategy_stop_not_active(self, network_latency_strategy):
        """Testa parada quando não está ativo"""
        result = await network_latency_strategy.stop()
        assert result is True

    def test_network_latency_strategy_check_tc_available(self, network_latency_strategy):
        """Testa verificação de disponibilidade do tc"""
        with patch('subprocess.run') as mock_run:
            # tc disponível
            mock_run.return_value.returncode = 0
            assert network_latency_strategy._check_tc_available() is True

            # tc não disponível
            mock_run.return_value.returncode = 1
            assert network_latency_strategy._check_tc_available() is False

            # tc não encontrado
            mock_run.side_effect = FileNotFoundError()
            assert network_latency_strategy._check_tc_available() is False


class TestNetworkPacketLossStrategy:
    """Testes para NetworkPacketLossStrategy"""

    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo"""
        return {
            'loss_percentage': 5.0,
            'target_interface': 'eth0'
        }

    @pytest.fixture
    def packet_loss_strategy(self, sample_config):
        """Instância de NetworkPacketLossStrategy para testes"""
        return NetworkPacketLossStrategy(sample_config)

    def test_packet_loss_strategy_initialization(self, sample_config):
        """Testa inicialização de NetworkPacketLossStrategy"""
        strategy = NetworkPacketLossStrategy(sample_config)

        assert strategy.loss_percentage == 5.0
        assert strategy.target_interface == 'eth0'
        assert strategy.tc_process is None

    def test_packet_loss_strategy_validate_config_valid(self, packet_loss_strategy):
        """Testa validação de configuração válida"""
        errors = packet_loss_strategy.validate_config()
        assert len(errors) == 0

    def test_packet_loss_strategy_validate_config_invalid(self):
        """Testa validação de configuração inválida"""
        # Percentual negativo
        config = {'loss_percentage': -5.0, 'target_interface': 'eth0'}
        strategy = NetworkPacketLossStrategy(config)
        errors = strategy.validate_config()
        assert len(errors) > 0
        assert any('Percentual de perda deve estar entre 0 e 100' in error for error in errors)

        # Percentual muito alto
        config = {'loss_percentage': 75.0, 'target_interface': 'eth0'}
        strategy = NetworkPacketLossStrategy(config)
        errors = strategy.validate_config()
        assert len(errors) > 0
        assert any('Percentual de perda muito alto' in error for error in errors)

    @pytest.mark.asyncio
    async def test_packet_loss_strategy_inject_success(self, packet_loss_strategy):
        """Testa injeção bem-sucedida de perda de pacotes"""
        with patch.object(packet_loss_strategy, '_check_tc_available', return_value=True), \
             patch('subprocess.Popen') as mock_popen, \
             patch('asyncio.sleep') as mock_sleep:

            mock_process = Mock()
            mock_process.poll.return_value = None
            mock_popen.return_value = mock_process

            result = await packet_loss_strategy.inject()

            assert result.success is True
            assert result.error_message is None
            assert result.impact_metrics['loss_percentage'] == 5.0
            assert packet_loss_strategy.is_active is True


class TestCPUStressStrategy:
    """Testes para CPUStressStrategy"""

    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo"""
        return {
            'cpu_load': 0.7,
            'cores': 2
        }

    @pytest.fixture
    def cpu_stress_strategy(self, sample_config):
        """Instância de CPUStressStrategy para testes"""
        return CPUStressStrategy(sample_config)

    def test_cpu_stress_strategy_initialization(self, sample_config):
        """Testa inicialização de CPUStressStrategy"""
        strategy = CPUStressStrategy(sample_config)

        assert strategy.cpu_load == 0.7
        assert strategy.cores == 2
        assert strategy.stress_processes == []

    def test_cpu_stress_strategy_validate_config_valid(self, cpu_stress_strategy):
        """Testa validação de configuração válida"""
        with patch('psutil.cpu_count', return_value=4):
            errors = cpu_stress_strategy.validate_config()
            assert len(errors) == 0

    def test_cpu_stress_strategy_validate_config_invalid(self):
        """Testa validação de configuração inválida"""
        with patch('psutil.cpu_count', return_value=4):
            # Carga de CPU inválida
            config = {'cpu_load': 1.5, 'cores': 2}
            strategy = CPUStressStrategy(config)
            errors = strategy.validate_config()
            assert len(errors) > 0
            assert any('Carga de CPU deve estar entre 0 e 1' in error for error in errors)

            # Número de cores inválido
            config = {'cpu_load': 0.7, 'cores': 0}
            strategy = CPUStressStrategy(config)
            errors = strategy.validate_config()
            assert len(errors) > 0
            assert any('Número de cores deve ser maior que zero' in error for error in errors)

            # Cores excedem CPUs disponíveis
            config = {'cpu_load': 0.7, 'cores': 8}
            strategy = CPUStressStrategy(config)
            errors = strategy.validate_config()
            assert len(errors) > 0
            assert any('Número de cores excede CPUs disponíveis' in error for error in errors)

    @pytest.mark.asyncio
    async def test_cpu_stress_strategy_inject_success(self, cpu_stress_strategy):
        """Testa injeção bem-sucedida de stress de CPU"""
        with patch('subprocess.Popen') as mock_popen, \
             patch('asyncio.sleep') as mock_sleep:

            mock_process = Mock()
            mock_process.poll.return_value = None
            mock_popen.return_value = mock_process

            result = await cpu_stress_strategy.inject()

            assert result.success is True
            assert result.error_message is None
            assert result.impact_metrics['cpu_load'] == 0.7
            assert result.impact_metrics['cores'] == 2
            assert cpu_stress_strategy.is_active is True
            assert len(cpu_stress_strategy.stress_processes) == 2

    @pytest.mark.asyncio
    async def test_cpu_stress_strategy_stop_success(self, cpu_stress_strategy):
        """Testa parada bem-sucedida de stress de CPU"""
        # Simular processos ativos
        cpu_stress_strategy.is_active = True
        cpu_stress_strategy.start_time = datetime.now()
        cpu_stress_strategy.stress_processes = [Mock(), Mock()]

        result = await cpu_stress_strategy.stop()

        assert result is True
        assert cpu_stress_strategy.is_active is False
        assert cpu_stress_strategy.stop_time is not None
        assert len(cpu_stress_strategy.stress_processes) == 0


class TestMemoryStressStrategy:
    """Testes para MemoryStressStrategy"""

    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo"""
        return {
            'memory_mb': 512
        }

    @pytest.fixture
    def memory_stress_strategy(self, sample_config):
        """Instância de MemoryStressStrategy para testes"""
        return MemoryStressStrategy(sample_config)

    def test_memory_stress_strategy_initialization(self, sample_config):
        """Testa inicialização de MemoryStressStrategy"""
        strategy = MemoryStressStrategy(sample_config)

        assert strategy.memory_mb == 512
        assert strategy.stress_process is None

    def test_memory_stress_strategy_validate_config_valid(self, memory_stress_strategy):
        """Testa validação de configuração válida"""
        with patch('psutil.virtual_memory') as mock_vm:
            mock_vm.return_value.available = 2048 * 1024 * 1024  # 2GB disponível
            errors = memory_stress_strategy.validate_config()
            assert len(errors) == 0

    def test_memory_stress_strategy_validate_config_invalid(self):
        """Testa validação de configuração inválida"""
        with patch('psutil.virtual_memory') as mock_vm:
            mock_vm.return_value.available = 1024 * 1024 * 1024  # 1GB disponível

            # Memória solicitada excede limite
            config = {'memory_mb': 900}
            strategy = MemoryStressStrategy(config)
            errors = strategy.validate_config()
            assert len(errors) > 0
            assert any('Memória solicitada excede 80%' in error for error in errors)

            # Memória zero ou negativa
            config = {'memory_mb': 0}
            strategy = MemoryStressStrategy(config)
            errors = strategy.validate_config()
            assert len(errors) > 0
            assert any('Memória deve ser maior que zero' in error for error in errors)

    @pytest.mark.asyncio
    async def test_memory_stress_strategy_inject_success(self, memory_stress_strategy):
        """Testa injeção bem-sucedida de stress de memória"""
        with patch('psutil.virtual_memory') as mock_vm, \
             patch('subprocess.Popen') as mock_popen, \
             patch('asyncio.sleep') as mock_sleep:

            mock_vm.return_value.available = 2048 * 1024 * 1024  # 2GB disponível
            mock_process = Mock()
            mock_process.poll.return_value = None
            mock_popen.return_value = mock_process

            result = await memory_stress_strategy.inject()

            assert result.success is True
            assert result.error_message is None
            assert result.impact_metrics['memory_mb'] == 512
            assert memory_stress_strategy.is_active is True

    @pytest.mark.asyncio
    async def test_memory_stress_strategy_inject_insufficient_memory(self, memory_stress_strategy):
        """Testa injeção com memória insuficiente"""
        with patch('psutil.virtual_memory') as mock_vm:
            mock_vm.return_value.available = 100 * 1024 * 1024  # 100MB disponível

            result = await memory_stress_strategy.inject()

            assert result.success is False
            assert 'Memória solicitada' in result.error_message


class TestServiceFailureStrategy:
    """Testes para ServiceFailureStrategy"""

    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo"""
        return {
            'service_name': 'test-service',
            'failure_rate': 0.3,
            'failure_pattern': 'random'
        }

    @pytest.fixture
    def service_failure_strategy(self, sample_config):
        """Instância de ServiceFailureStrategy para testes"""
        return ServiceFailureStrategy(sample_config)

    def test_service_failure_strategy_initialization(self, sample_config):
        """Testa inicialização de ServiceFailureStrategy"""
        strategy = ServiceFailureStrategy(sample_config)

        assert strategy.service_name == 'test-service'
        assert strategy.failure_rate == 0.3
        assert strategy.failure_pattern == 'random'
        assert strategy.original_service_state is None

    def test_service_failure_strategy_validate_config_valid(self, service_failure_strategy):
        """Testa validação de configuração válida"""
        errors = service_failure_strategy.validate_config()
        assert len(errors) == 0

    def test_service_failure_strategy_validate_config_invalid(self):
        """Testa validação de configuração inválida"""
        # Nome do serviço vazio
        config = {'service_name': '', 'failure_rate': 0.3, 'failure_pattern': 'random'}
        strategy = ServiceFailureStrategy(config)
        errors = strategy.validate_config()
        assert len(errors) > 0
        assert any('Nome do serviço é obrigatório' in error for error in errors)

        # Taxa de falha inválida
        config = {'service_name': 'test', 'failure_rate': 1.5, 'failure_pattern': 'random'}
        strategy = ServiceFailureStrategy(config)
        errors = strategy.validate_config()
        assert len(errors) > 0
        assert any('Taxa de falha deve estar entre 0 e 1' in error for error in errors)

        # Padrão de falha inválido
        config = {'service_name': 'test', 'failure_rate': 0.3, 'failure_pattern': 'invalid'}
        strategy = ServiceFailureStrategy(config)
        errors = strategy.validate_config()
        assert len(errors) > 0
        assert any('Padrão de falha deve ser' in error for error in errors)

    @pytest.mark.asyncio
    async def test_service_failure_strategy_inject_success(self, service_failure_strategy):
        """Testa injeção bem-sucedida de falha de serviço"""
        with patch.object(service_failure_strategy, '_service_exists', return_value=True), \
             patch.object(service_failure_strategy, '_get_service_state', return_value='active'), \
             patch.object(service_failure_strategy, '_apply_random_failure') as mock_apply:

            result = await service_failure_strategy.inject()

            assert result.success is True
            assert result.error_message is None
            assert result.impact_metrics['service_name'] == 'test-service'
            assert result.impact_metrics['failure_rate'] == 0.3
            assert service_failure_strategy.is_active is True
            assert mock_apply.called

    @pytest.mark.asyncio
    async def test_service_failure_strategy_inject_service_not_found(self, service_failure_strategy):
        """Testa injeção com serviço não encontrado"""
        with patch.object(service_failure_strategy, '_service_exists', return_value=False):

            result = await service_failure_strategy.inject()

            assert result.success is False
            assert 'não encontrado' in result.error_message

    def test_service_failure_strategy_service_exists(self, service_failure_strategy):
        """Testa verificação de existência do serviço"""
        with patch('subprocess.run') as mock_run:
            # Serviço existe
            mock_run.return_value.returncode = 0
            assert service_failure_strategy._service_exists() is True

            # Serviço não existe
            mock_run.return_value.returncode = 1
            assert service_failure_strategy._service_exists() is False

    def test_service_failure_strategy_get_service_state(self, service_failure_strategy):
        """Testa obtenção do estado do serviço"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = 'active\n'
            mock_run.return_value.returncode = 0

            state = service_failure_strategy._get_service_state()
            assert state == 'active'

    @pytest.mark.asyncio
    async def test_service_failure_strategy_apply_random_failure(self, service_failure_strategy):
        """Testa aplicação de falha aleatória"""
        with patch.object(service_failure_strategy, '_stop_service') as mock_stop, \
             patch('random.random', return_value=0.1):  # Menor que failure_rate (0.3)

            await service_failure_strategy._apply_random_failure()
            assert mock_stop.called

        with patch.object(service_failure_strategy, '_stop_service') as mock_stop, \
             patch('random.random', return_value=0.5):  # Maior que failure_rate (0.3)

            await service_failure_strategy._apply_random_failure()
            assert not mock_stop.called


class TestStrategyFactory:
    """Testes para StrategyFactory"""

    def test_strategy_factory_create_strategy_network_latency(self):
        """Testa criação de estratégia de latência de rede"""
        config = {'latency_ms': 100, 'jitter_ms': 10}
        strategy = StrategyFactory.create_strategy(InjectionType.NETWORK_LATENCY, config)

        assert isinstance(strategy, NetworkLatencyStrategy)
        assert strategy.latency_ms == 100
        assert strategy.jitter_ms == 10

    def test_strategy_factory_create_strategy_cpu_stress(self):
        """Testa criação de estratégia de stress de CPU"""
        config = {'cpu_load': 0.7, 'cores': 2}
        strategy = StrategyFactory.create_strategy(InjectionType.CPU_STRESS, config)

        assert isinstance(strategy, CPUStressStrategy)
        assert strategy.cpu_load == 0.7
        assert strategy.cores == 2

    def test_strategy_factory_create_strategy_unsupported_type(self):
        """Testa criação de estratégia não suportada"""
        config = {'test': 'config'}
        
        with pytest.raises(ValueError, match="Tipo de injeção não suportado"):
            StrategyFactory.create_strategy(InjectionType.DATABASE_FAILURE, config)

    def test_strategy_factory_get_available_strategies(self):
        """Testa obtenção de estratégias disponíveis"""
        strategies = StrategyFactory.get_available_strategies()

        assert InjectionType.NETWORK_LATENCY in strategies
        assert InjectionType.NETWORK_PACKET_LOSS in strategies
        assert InjectionType.CPU_STRESS in strategies
        assert InjectionType.MEMORY_STRESS in strategies
        assert InjectionType.SERVICE_FAILURE in strategies
        assert InjectionType.DATABASE_FAILURE not in strategies  # Não implementado


class TestInjectionOrchestrator:
    """Testes para InjectionOrchestrator"""

    @pytest.fixture
    def orchestrator(self):
        """Instância de InjectionOrchestrator para testes"""
        return InjectionOrchestrator()

    def test_injection_orchestrator_initialization(self, orchestrator):
        """Testa inicialização de InjectionOrchestrator"""
        assert len(orchestrator.active_injections) == 0
        assert len(orchestrator.injection_history) == 0
        assert isinstance(orchestrator.lock, threading.RLock)
        assert orchestrator.executor is not None

    @pytest.mark.asyncio
    async def test_injection_orchestrator_inject_failure_success(self, orchestrator):
        """Testa injeção bem-sucedida"""
        config = {'latency_ms': 100, 'jitter_ms': 10}
        
        with patch.object(NetworkLatencyStrategy, 'inject') as mock_inject:
            mock_inject.return_value = InjectionResult(
                success=True,
                injection_id='test_injection_001',
                start_time=datetime.now(),
                end_time=None,
                duration=None,
                error_message=None,
                impact_metrics={'latency_ms': 100}
            )

            result = await orchestrator.inject_failure(InjectionType.NETWORK_LATENCY, config)

            assert result.success is True
            assert result.injection_id == 'test_injection_001'
            assert len(orchestrator.active_injections) == 1
            assert len(orchestrator.injection_history) == 1

    @pytest.mark.asyncio
    async def test_injection_orchestrator_inject_failure_invalid_config(self, orchestrator):
        """Testa injeção com configuração inválida"""
        config = {'latency_ms': -10}  # Configuração inválida

        result = await orchestrator.inject_failure(InjectionType.NETWORK_LATENCY, config)

        assert result.success is False
        assert 'Configuração inválida' in result.error_message

    @pytest.mark.asyncio
    async def test_injection_orchestrator_stop_injection_success(self, orchestrator):
        """Testa parada bem-sucedida de injeção"""
        # Adicionar injeção ativa
        strategy = Mock()
        strategy.stop.return_value = True
        orchestrator.active_injections['test_injection_001'] = strategy

        result = await orchestrator.stop_injection('test_injection_001')

        assert result is True
        assert 'test_injection_001' not in orchestrator.active_injections

    @pytest.mark.asyncio
    async def test_injection_orchestrator_stop_injection_not_found(self, orchestrator):
        """Testa parada de injeção inexistente"""
        result = await orchestrator.stop_injection('nonexistent_injection')
        assert result is False

    @pytest.mark.asyncio
    async def test_injection_orchestrator_stop_all_injections(self, orchestrator):
        """Testa parada de todas as injeções"""
        # Adicionar injeções ativas
        strategy1 = Mock()
        strategy1.stop.return_value = True
        strategy2 = Mock()
        strategy2.stop.return_value = True
        
        orchestrator.active_injections['injection_1'] = strategy1
        orchestrator.active_injections['injection_2'] = strategy2

        result = await orchestrator.stop_all_injections()

        assert result is True
        assert len(orchestrator.active_injections) == 0

    def test_injection_orchestrator_get_active_injections(self, orchestrator):
        """Testa obtenção de injeções ativas"""
        # Adicionar injeção ativa
        strategy = Mock()
        strategy.__class__.__name__ = 'TestStrategy'
        strategy.get_status.return_value = {'status': 'active'}
        orchestrator.active_injections['test_injection'] = strategy

        active_injections = orchestrator.get_active_injections()

        assert len(active_injections) == 1
        assert active_injections[0]['injection_id'] == 'test_injection'
        assert active_injections[0]['strategy_type'] == 'TestStrategy'

    def test_injection_orchestrator_get_injection_history(self, orchestrator):
        """Testa obtenção do histórico de injeções"""
        # Adicionar resultados ao histórico
        result1 = InjectionResult(
            success=True,
            injection_id='injection_1',
            start_time=datetime.now(),
            end_time=None,
            duration=None,
            error_message=None,
            impact_metrics={}
        )
        result2 = InjectionResult(
            success=False,
            injection_id='injection_2',
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration=0.0,
            error_message='Test error',
            impact_metrics={}
        )
        
        orchestrator.injection_history = [result1, result2]

        # Obter todo o histórico
        history = orchestrator.get_injection_history()
        assert len(history) == 2

        # Obter histórico com limite
        history = orchestrator.get_injection_history(limit=1)
        assert len(history) == 1

    def test_injection_orchestrator_get_statistics(self, orchestrator):
        """Testa obtenção de estatísticas"""
        # Adicionar dados de teste
        orchestrator.injection_history = [
            InjectionResult(success=True, injection_id='1', start_time=datetime.now(), 
                          end_time=None, duration=None, error_message=None, impact_metrics={}),
            InjectionResult(success=True, injection_id='2', start_time=datetime.now(), 
                          end_time=None, duration=None, error_message=None, impact_metrics={}),
            InjectionResult(success=False, injection_id='3', start_time=datetime.now(), 
                          end_time=datetime.now(), duration=0.0, error_message='Error', impact_metrics={})
        ]
        orchestrator.active_injections['active_1'] = Mock()

        stats = orchestrator.get_statistics()

        assert stats['total_injections'] == 3
        assert stats['successful_injections'] == 2
        assert stats['failed_injections'] == 1
        assert stats['success_rate'] == 2/3
        assert stats['active_injections'] == 1


class TestCreateInjectionOrchestrator:
    """Testes para função create_injection_orchestrator"""

    def test_create_injection_orchestrator(self):
        """Testa criação de orquestrador"""
        orchestrator = create_injection_orchestrator()

        assert isinstance(orchestrator, InjectionOrchestrator)
        assert len(orchestrator.active_injections) == 0
        assert len(orchestrator.injection_history) == 0


class TestInjectionStrategiesIntegration:
    """Testes de integração para Injection Strategies"""

    @pytest.mark.asyncio
    async def test_full_injection_workflow(self):
        """Testa workflow completo de injeção"""
        orchestrator = InjectionOrchestrator()

        # 1. Injetar falha de rede
        network_config = {'latency_ms': 50, 'jitter_ms': 5}
        
        with patch.object(NetworkLatencyStrategy, 'inject') as mock_inject, \
             patch.object(NetworkLatencyStrategy, 'stop') as mock_stop:
            
            mock_inject.return_value = InjectionResult(
                success=True,
                injection_id='network_injection_001',
                start_time=datetime.now(),
                end_time=None,
                duration=None,
                error_message=None,
                impact_metrics={'latency_ms': 50}
            )
            mock_stop.return_value = True

            result = await orchestrator.inject_failure(InjectionType.NETWORK_LATENCY, network_config)
            assert result.success is True

            # 2. Verificar injeção ativa
            active_injections = orchestrator.get_active_injections()
            assert len(active_injections) == 1

            # 3. Parar injeção
            stop_result = await orchestrator.stop_injection('network_injection_001')
            assert stop_result is True

            # 4. Verificar estatísticas
            stats = orchestrator.get_statistics()
            assert stats['total_injections'] == 1
            assert stats['successful_injections'] == 1
            assert stats['active_injections'] == 0


class TestInjectionStrategiesErrorHandling:
    """Testes de tratamento de erro para Injection Strategies"""

    @pytest.mark.asyncio
    async def test_strategy_injection_exception_handling(self):
        """Testa tratamento de exceções durante injeção"""
        config = {'latency_ms': 100, 'jitter_ms': 10}
        strategy = NetworkLatencyStrategy(config)

        with patch.object(strategy, '_check_tc_available', side_effect=Exception("Test error")):
            result = await strategy.inject()

            assert result.success is False
            assert 'Test error' in result.error_message

    @pytest.mark.asyncio
    async def test_orchestrator_exception_handling(self):
        """Testa tratamento de exceções no orquestrador"""
        orchestrator = InjectionOrchestrator()
        config = {'invalid': 'config'}

        with patch.object(StrategyFactory, 'create_strategy', side_effect=Exception("Factory error")):
            result = await orchestrator.inject_failure(InjectionType.NETWORK_LATENCY, config)

            assert result.success is False
            assert 'Factory error' in result.error_message


class TestInjectionStrategiesPerformance:
    """Testes de performance para Injection Strategies"""

    def test_orchestrator_memory_usage(self):
        """Testa uso de memória do orquestrador"""
        orchestrator = InjectionOrchestrator()

        # Adicionar muitas injeções
        for i in range(100):
            strategy = Mock()
            orchestrator.active_injections[f'injection_{i}'] = strategy
            orchestrator.injection_history.append(Mock())

        # Verificar que não houve vazamento de memória
        assert len(orchestrator.active_injections) == 100
        assert len(orchestrator.injection_history) == 100

    @pytest.mark.asyncio
    async def test_concurrent_injection_handling(self):
        """Testa manipulação de injeções concorrentes"""
        orchestrator = InjectionOrchestrator()

        async def inject_failure():
            config = {'latency_ms': 100, 'jitter_ms': 10}
            with patch.object(NetworkLatencyStrategy, 'inject') as mock_inject:
                mock_inject.return_value = InjectionResult(
                    success=True,
                    injection_id=f'injection_{id(orchestrator)}',
                    start_time=datetime.now(),
                    end_time=None,
                    duration=None,
                    error_message=None,
                    impact_metrics={}
                )
                return await orchestrator.inject_failure(InjectionType.NETWORK_LATENCY, config)

        # Executar injeções concorrentes
        results = await asyncio.gather(*[inject_failure() for _ in range(10)])

        # Verificar que todas foram bem-sucedidas
        assert all(result.success for result in results)
        assert len(orchestrator.active_injections) == 10 