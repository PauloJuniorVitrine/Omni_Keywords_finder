"""
🧪 Chaos Engineering Experiments Tests
📅 Generated: 2025-01-27
🎯 Purpose: Comprehensive tests for chaos engineering experiments
📋 Tracing ID: TEST_CHAOS_EXPERIMENTS_001_20250127
"""

import unittest
import asyncio
import time
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Dict, Any

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from infrastructure.chaos.chaos_experiments import (
    ChaosExperiment, NetworkLatencyExperiment, PacketLossExperiment,
    CPUStressExperiment, MemoryStressExperiment, ProcessKillExperiment,
    ServiceRestartExperiment, CustomExperiment, ChaosExperimentFactory,
    ExperimentConfig, ExperimentType, ExperimentStatus, ExperimentSeverity,
    ExperimentResult, ExperimentMetrics, create_experiment, run_experiment,
    get_experiment, list_experiments, cancel_experiment
)


class TestChaosExperiment(unittest.TestCase):
    """Test cases for base ChaosExperiment class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = ExperimentConfig(
            experiment_type=ExperimentType.NETWORK_LATENCY,
            duration=1,  # Short duration for tests
            severity=ExperimentSeverity.MEDIUM,
            target_hosts=["localhost"],
            parameters={"latency_ms": 50, "jitter_ms": 5}
        )
        
        # Create a concrete implementation for testing
        class TestExperiment(ChaosExperiment):
            async def _execute_experiment(self):
                # Simple test implementation
                await asyncio.sleep(0.1)
        
        self.experiment = TestExperiment(self.config)
    
    def test_experiment_creation(self):
        """Test experiment creation and initialization"""
        self.assertIsNotNone(self.experiment.experiment_id)
        self.assertEqual(self.experiment.status, ExperimentStatus.PENDING)
        self.assertEqual(self.experiment.config.experiment_type, ExperimentType.NETWORK_LATENCY)
        self.assertEqual(self.experiment.config.duration, 1)
        self.assertEqual(self.experiment.config.severity, ExperimentSeverity.MEDIUM)
    
    def test_experiment_id_generation(self):
        """Test experiment ID generation"""
        experiment_id = self.experiment.experiment_id
        self.assertIsInstance(experiment_id, str)
        self.assertTrue(experiment_id.startswith("chaos_network_latency_"))
        self.assertIn("_", experiment_id)
    
    @patch('infrastructure.chaos.chaos_experiments.psutil.cpu_percent')
    @patch('infrastructure.chaos.chaos_experiments.psutil.virtual_memory')
    @patch('infrastructure.chaos.chaos_experiments.psutil.disk_usage')
    async def test_collect_baseline_metrics(self, mock_disk, mock_memory, mock_cpu):
        """Test baseline metrics collection"""
        # Mock system metrics
        mock_cpu.return_value = 25.5
        mock_memory.return_value.percent = 60.0
        mock_disk.return_value.percent = 45.0
        
        metrics = await self.experiment._collect_baseline_metrics()
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('cpu_usage', metrics)
        self.assertIn('memory_usage', metrics)
        self.assertIn('disk_usage', metrics)
        self.assertIn('timestamp', metrics)
        self.assertEqual(metrics['cpu_usage'], 25.5)
        self.assertEqual(metrics['memory_usage'], 60.0)
        self.assertEqual(metrics['disk_usage'], 45.0)
    
    @patch('infrastructure.chaos.chaos_experiments.psutil.cpu_percent')
    @patch('infrastructure.chaos.chaos_experiments.psutil.virtual_memory')
    @patch('infrastructure.chaos.chaos_experiments.psutil.disk_usage')
    async def test_monitor_during_experiment(self, mock_disk, mock_memory, mock_cpu):
        """Test monitoring during experiment"""
        # Mock system metrics
        mock_cpu.return_value = 75.0
        mock_memory.return_value.percent = 80.0
        mock_disk.return_value.percent = 55.0
        
        metrics = await self.experiment._monitor_during_experiment()
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('cpu_usage', metrics)
        self.assertIn('memory_usage', metrics)
        self.assertIn('disk_usage', metrics)
        self.assertEqual(metrics['cpu_usage'], 75.0)
        self.assertEqual(metrics['memory_usage'], 80.0)
        self.assertEqual(metrics['disk_usage'], 55.0)
    
    @patch('infrastructure.chaos.chaos_experiments.psutil.cpu_percent')
    @patch('infrastructure.chaos.chaos_experiments.psutil.virtual_memory')
    @patch('infrastructure.chaos.chaos_experiments.psutil.disk_usage')
    async def test_collect_final_metrics(self, mock_disk, mock_memory, mock_cpu):
        """Test final metrics collection"""
        # Mock system metrics
        mock_cpu.return_value = 30.0
        mock_memory.return_value.percent = 65.0
        mock_disk.return_value.percent = 50.0
        
        metrics = await self.experiment._collect_final_metrics()
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('cpu_usage', metrics)
        self.assertIn('memory_usage', metrics)
        self.assertIn('disk_usage', metrics)
        self.assertEqual(metrics['cpu_usage'], 30.0)
        self.assertEqual(metrics['memory_usage'], 65.0)
        self.assertEqual(metrics['disk_usage'], 50.0)
    
    def test_calculate_impact_score(self):
        """Test impact score calculation"""
        metrics_before = {
            'cpu_usage': 20.0,
            'memory_usage': 50.0,
            'network_latency': 10.0
        }
        
        metrics_during = {
            'cpu_usage': 80.0,
            'memory_usage': 90.0,
            'network_latency': 100.0
        }
        
        metrics_after = {
            'cpu_usage': 25.0,
            'memory_usage': 55.0,
            'network_latency': 15.0
        }
        
        impact_score = self.experiment._calculate_impact_score(
            metrics_before, metrics_during, metrics_after
        )
        
        self.assertIsInstance(impact_score, float)
        self.assertGreater(impact_score, 0.0)
        self.assertLessEqual(impact_score, 1.0)
    
    async def test_rollback_experiment(self):
        """Test experiment rollback"""
        # Add a mock rollback handler
        mock_handler = AsyncMock()
        self.experiment.rollback_handlers.append(mock_handler)
        
        result = await self.experiment._rollback_experiment()
        
        self.assertTrue(result)
        mock_handler.assert_called_once()
    
    async def test_rollback_experiment_with_error(self):
        """Test experiment rollback with error"""
        # Add a rollback handler that raises an exception
        def failing_handler():
            raise Exception("Rollback failed")
        
        self.experiment.rollback_handlers.append(failing_handler)
        
        result = await self.experiment._rollback_experiment()
        
        self.assertFalse(result)
    
    def test_add_rollback_handler(self):
        """Test adding rollback handler"""
        handler = lambda: None
        self.experiment.add_rollback_handler(handler)
        
        self.assertIn(handler, self.experiment.rollback_handlers)
    
    def test_add_monitoring_callback(self):
        """Test adding monitoring callback"""
        callback = lambda: None
        self.experiment.add_monitoring_callback(callback)
        
        self.assertIn(callback, self.experiment.monitoring_callbacks)


class TestNetworkLatencyExperiment(unittest.TestCase):
    """Test cases for NetworkLatencyExperiment"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = ExperimentConfig(
            experiment_type=ExperimentType.NETWORK_LATENCY,
            duration=1,
            target_hosts=["localhost"],
            parameters={"latency_ms": 100, "jitter_ms": 10}
        )
        self.experiment = NetworkLatencyExperiment(self.config)
    
    @patch('asyncio.create_subprocess_exec')
    async def test_execute_experiment(self, mock_subprocess):
        """Test network latency experiment execution"""
        # Mock subprocess
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value=("", ""))
        mock_subprocess.return_value = mock_process
        
        await self.experiment._execute_experiment()
        
        # Verify tc command was called
        mock_subprocess.assert_called()
        call_args = mock_subprocess.call_args[0]
        self.assertIn('tc', call_args)
        self.assertIn('qdisc', call_args)
        self.assertIn('add', call_args)
    
    @patch('asyncio.create_subprocess_exec')
    async def test_remove_latency(self, mock_subprocess):
        """Test latency removal"""
        # Mock subprocess
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value=("", ""))
        mock_subprocess.return_value = mock_process
        
        await self.experiment._remove_latency()
        
        # Verify tc command was called
        mock_subprocess.assert_called()
        call_args = mock_subprocess.call_args[0]
        self.assertIn('tc', call_args)
        self.assertIn('qdisc', call_args)
        self.assertIn('del', call_args)


class TestPacketLossExperiment(unittest.TestCase):
    """Test cases for PacketLossExperiment"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = ExperimentConfig(
            experiment_type=ExperimentType.NETWORK_PACKET_LOSS,
            duration=1,
            target_hosts=["localhost"],
            parameters={"loss_percent": 5.0}
        )
        self.experiment = PacketLossExperiment(self.config)
    
    @patch('asyncio.create_subprocess_exec')
    async def test_execute_experiment(self, mock_subprocess):
        """Test packet loss experiment execution"""
        # Mock subprocess
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value=("", ""))
        mock_subprocess.return_value = mock_process
        
        await self.experiment._execute_experiment()
        
        # Verify tc command was called
        mock_subprocess.assert_called()
        call_args = mock_subprocess.call_args[0]
        self.assertIn('tc', call_args)
        self.assertIn('loss', call_args)
    
    @patch('asyncio.create_subprocess_exec')
    async def test_remove_packet_loss(self, mock_subprocess):
        """Test packet loss removal"""
        # Mock subprocess
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value=("", ""))
        mock_subprocess.return_value = mock_process
        
        await self.experiment._remove_packet_loss()
        
        # Verify tc command was called
        mock_subprocess.assert_called()
        call_args = mock_subprocess.call_args[0]
        self.assertIn('tc', call_args)
        self.assertIn('del', call_args)


class TestCPUStressExperiment(unittest.TestCase):
    """Test cases for CPUStressExperiment"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = ExperimentConfig(
            experiment_type=ExperimentType.CPU_STRESS,
            duration=1,
            parameters={"cpu_load": 80, "cores": 2}
        )
        self.experiment = CPUStressExperiment(self.config)
    
    @patch('asyncio.create_subprocess_exec')
    async def test_execute_experiment(self, mock_subprocess):
        """Test CPU stress experiment execution"""
        # Mock subprocess
        mock_process = AsyncMock()
        mock_subprocess.return_value = mock_process
        
        await self.experiment._execute_experiment()
        
        # Verify stress-ng command was called
        mock_subprocess.assert_called()
        call_args = mock_subprocess.call_args[0]
        self.assertIn('stress-ng', call_args)
        self.assertIn('--cpu', call_args)
    
    async def test_stop_cpu_stress(self):
        """Test stopping CPU stress"""
        # Mock stress process
        self.experiment.stress_process = AsyncMock()
        self.experiment.stress_process.terminate = Mock()
        self.experiment.stress_process.wait = AsyncMock()
        
        await self.experiment._stop_cpu_stress()
        
        self.experiment.stress_process.terminate.assert_called_once()
        self.experiment.stress_process.wait.assert_called_once()


class TestMemoryStressExperiment(unittest.TestCase):
    """Test cases for MemoryStressExperiment"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = ExperimentConfig(
            experiment_type=ExperimentType.MEMORY_STRESS,
            duration=1,
            parameters={"memory_mb": 512}
        )
        self.experiment = MemoryStressExperiment(self.config)
    
    @patch('asyncio.create_subprocess_exec')
    async def test_execute_experiment(self, mock_subprocess):
        """Test memory stress experiment execution"""
        # Mock subprocess
        mock_process = AsyncMock()
        mock_subprocess.return_value = mock_process
        
        await self.experiment._execute_experiment()
        
        # Verify stress-ng command was called
        mock_subprocess.assert_called()
        call_args = mock_subprocess.call_args[0]
        self.assertIn('stress-ng', call_args)
        self.assertIn('--vm', call_args)
    
    async def test_stop_memory_stress(self):
        """Test stopping memory stress"""
        # Mock stress process
        self.experiment.stress_process = AsyncMock()
        self.experiment.stress_process.terminate = Mock()
        self.experiment.stress_process.wait = AsyncMock()
        
        await self.experiment._stop_memory_stress()
        
        self.experiment.stress_process.terminate.assert_called_once()
        self.experiment.stress_process.wait.assert_called_once()


class TestProcessKillExperiment(unittest.TestCase):
    """Test cases for ProcessKillExperiment"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = ExperimentConfig(
            experiment_type=ExperimentType.PROCESS_KILL,
            duration=1,
            parameters={"process_names": ["test_process"]}
        )
        self.experiment = ProcessKillExperiment(self.config)
    
    @patch('psutil.process_iter')
    async def test_execute_experiment(self, mock_process_iter):
        """Test process kill experiment execution"""
        # Mock process
        mock_process = Mock()
        mock_process.info = {'pid': 12345, 'name': 'test_process'}
        mock_process.terminate = Mock()
        mock_process_iter.return_value = [mock_process]
        
        await self.experiment._execute_experiment()
        
        # Verify process was terminated
        mock_process.terminate.assert_called_once()
        self.assertIn((12345, 'test_process'), self.experiment.killed_processes)
    
    async def test_restart_processes(self):
        """Test process restart"""
        self.experiment.killed_processes = [(12345, 'test_process')]
        
        # This is a simplified test since actual restart logic would depend on service management
        await self.experiment._restart_processes(['test_process'])
        
        # Should not raise any exceptions


class TestServiceRestartExperiment(unittest.TestCase):
    """Test cases for ServiceRestartExperiment"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = ExperimentConfig(
            experiment_type=ExperimentType.SERVICE_RESTART,
            duration=1,
            parameters={"services": ["test-service"]}
        )
        self.experiment = ServiceRestartExperiment(self.config)
    
    @patch('asyncio.create_subprocess_exec')
    async def test_execute_experiment(self, mock_subprocess):
        """Test service restart experiment execution"""
        # Mock subprocess
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value=("", ""))
        mock_subprocess.return_value = mock_process
        
        await self.experiment._execute_experiment()
        
        # Verify systemctl commands were called
        self.assertEqual(mock_subprocess.call_count, 2)  # stop and start
        
        # Check stop command
        stop_call = mock_subprocess.call_args_list[0]
        self.assertIn('systemctl', stop_call[0])
        self.assertIn('stop', stop_call[0])
        
        # Check start command
        start_call = mock_subprocess.call_args_list[1]
        self.assertIn('systemctl', start_call[0])
        self.assertIn('start', start_call[0])


class TestCustomExperiment(unittest.TestCase):
    """Test cases for CustomExperiment"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_script = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.temp_script.write("#!/bin/bash\necho 'test script'\nexit 0")
        self.temp_script.close()
        os.chmod(self.temp_script.name, 0o755)
        
        self.config = ExperimentConfig(
            experiment_type=ExperimentType.CUSTOM,
            duration=1,
            custom_script=self.temp_script.name
        )
        self.experiment = CustomExperiment(self.config)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_script.name):
            os.unlink(self.temp_script.name)
    
    async def test_execute_experiment(self):
        """Test custom experiment execution"""
        await self.experiment._execute_experiment()
        # Should not raise any exceptions
    
    async def test_execute_experiment_missing_script(self):
        """Test custom experiment with missing script"""
        self.experiment.config.custom_script = "/nonexistent/script.sh"
        
        with self.assertRaises(ValueError):
            await self.experiment._execute_experiment()


class TestChaosExperimentFactory(unittest.TestCase):
    """Test cases for ChaosExperimentFactory"""
    
    def test_create_network_latency_experiment(self):
        """Test creating network latency experiment"""
        config = ExperimentConfig(experiment_type=ExperimentType.NETWORK_LATENCY)
        experiment = ChaosExperimentFactory.create_experiment(config)
        
        self.assertIsInstance(experiment, NetworkLatencyExperiment)
        self.assertEqual(experiment.config.experiment_type, ExperimentType.NETWORK_LATENCY)
    
    def test_create_packet_loss_experiment(self):
        """Test creating packet loss experiment"""
        config = ExperimentConfig(experiment_type=ExperimentType.NETWORK_PACKET_LOSS)
        experiment = ChaosExperimentFactory.create_experiment(config)
        
        self.assertIsInstance(experiment, PacketLossExperiment)
        self.assertEqual(experiment.config.experiment_type, ExperimentType.NETWORK_PACKET_LOSS)
    
    def test_create_cpu_stress_experiment(self):
        """Test creating CPU stress experiment"""
        config = ExperimentConfig(experiment_type=ExperimentType.CPU_STRESS)
        experiment = ChaosExperimentFactory.create_experiment(config)
        
        self.assertIsInstance(experiment, CPUStressExperiment)
        self.assertEqual(experiment.config.experiment_type, ExperimentType.CPU_STRESS)
    
    def test_create_memory_stress_experiment(self):
        """Test creating memory stress experiment"""
        config = ExperimentConfig(experiment_type=ExperimentType.MEMORY_STRESS)
        experiment = ChaosExperimentFactory.create_experiment(config)
        
        self.assertIsInstance(experiment, MemoryStressExperiment)
        self.assertEqual(experiment.config.experiment_type, ExperimentType.MEMORY_STRESS)
    
    def test_create_process_kill_experiment(self):
        """Test creating process kill experiment"""
        config = ExperimentConfig(experiment_type=ExperimentType.PROCESS_KILL)
        experiment = ChaosExperimentFactory.create_experiment(config)
        
        self.assertIsInstance(experiment, ProcessKillExperiment)
        self.assertEqual(experiment.config.experiment_type, ExperimentType.PROCESS_KILL)
    
    def test_create_service_restart_experiment(self):
        """Test creating service restart experiment"""
        config = ExperimentConfig(experiment_type=ExperimentType.SERVICE_RESTART)
        experiment = ChaosExperimentFactory.create_experiment(config)
        
        self.assertIsInstance(experiment, ServiceRestartExperiment)
        self.assertEqual(experiment.config.experiment_type, ExperimentType.SERVICE_RESTART)
    
    def test_create_custom_experiment(self):
        """Test creating custom experiment"""
        config = ExperimentConfig(experiment_type=ExperimentType.CUSTOM)
        experiment = ChaosExperimentFactory.create_experiment(config)
        
        self.assertIsInstance(experiment, CustomExperiment)
        self.assertEqual(experiment.config.experiment_type, ExperimentType.CUSTOM)
    
    def test_create_unsupported_experiment(self):
        """Test creating unsupported experiment type"""
        config = ExperimentConfig(experiment_type=ExperimentType.DATABASE_FAILURE)
        
        with self.assertRaises(ValueError):
            ChaosExperimentFactory.create_experiment(config)


class TestGlobalFunctions(unittest.TestCase):
    """Test cases for global functions"""
    
    def test_create_experiment(self):
        """Test creating experiment via global function"""
        config = ExperimentConfig(experiment_type=ExperimentType.NETWORK_LATENCY)
        experiment = create_experiment(config)
        
        self.assertIsInstance(experiment, NetworkLatencyExperiment)
        self.assertIsNotNone(experiment.experiment_id)
    
    def test_get_experiment(self):
        """Test getting experiment by ID"""
        config = ExperimentConfig(experiment_type=ExperimentType.NETWORK_LATENCY)
        experiment = create_experiment(config)
        
        retrieved_experiment = get_experiment(experiment.experiment_id)
        self.assertEqual(retrieved_experiment, experiment)
    
    def test_get_nonexistent_experiment(self):
        """Test getting nonexistent experiment"""
        experiment = get_experiment("nonexistent_id")
        self.assertIsNone(experiment)
    
    def test_list_experiments(self):
        """Test listing experiments"""
        # Clear existing experiments
        from infrastructure.chaos.chaos_experiments import get_experiment_manager
        manager = get_experiment_manager()
        manager.clear()
        
        # Create some experiments
        config1 = ExperimentConfig(experiment_type=ExperimentType.NETWORK_LATENCY)
        config2 = ExperimentConfig(experiment_type=ExperimentType.CPU_STRESS)
        
        experiment1 = create_experiment(config1)
        experiment2 = create_experiment(config2)
        
        experiment_ids = list_experiments()
        
        self.assertIn(experiment1.experiment_id, experiment_ids)
        self.assertIn(experiment2.experiment_id, experiment_ids)
    
    def test_cancel_experiment(self):
        """Test canceling experiment"""
        config = ExperimentConfig(experiment_type=ExperimentType.NETWORK_LATENCY)
        experiment = create_experiment(config)
        
        # Set experiment to running
        experiment.status = ExperimentStatus.RUNNING
        
        result = cancel_experiment(experiment.experiment_id)
        self.assertTrue(result)
        self.assertEqual(experiment.status, ExperimentStatus.CANCELLED)
    
    def test_cancel_nonexistent_experiment(self):
        """Test canceling nonexistent experiment"""
        result = cancel_experiment("nonexistent_id")
        self.assertFalse(result)


class TestExperimentResult(unittest.TestCase):
    """Test cases for ExperimentResult"""
    
    def test_experiment_result_creation(self):
        """Test creating experiment result"""
        result = ExperimentResult(
            experiment_id="test_id",
            experiment_type=ExperimentType.NETWORK_LATENCY,
            status=ExperimentStatus.COMPLETED,
            start_time=time.time(),
            end_time=time.time() + 10,
            duration=10.0,
            success=True,
            impact_score=0.5
        )
        
        self.assertEqual(result.experiment_id, "test_id")
        self.assertEqual(result.experiment_type, ExperimentType.NETWORK_LATENCY)
        self.assertEqual(result.status, ExperimentStatus.COMPLETED)
        self.assertTrue(result.success)
        self.assertEqual(result.impact_score, 0.5)


class TestExperimentMetrics(unittest.TestCase):
    """Test cases for ExperimentMetrics"""
    
    def test_experiment_metrics_creation(self):
        """Test creating experiment metrics"""
        metrics = ExperimentMetrics(
            timestamp=time.time(),
            cpu_usage=50.0,
            memory_usage=75.0,
            disk_usage=60.0,
            network_latency=25.0,
            error_rate=2.5,
            response_time=150.0,
            throughput=1000.0,
            availability=99.5
        )
        
        self.assertEqual(metrics.cpu_usage, 50.0)
        self.assertEqual(metrics.memory_usage, 75.0)
        self.assertEqual(metrics.disk_usage, 60.0)
        self.assertEqual(metrics.network_latency, 25.0)
        self.assertEqual(metrics.error_rate, 2.5)
        self.assertEqual(metrics.response_time, 150.0)
        self.assertEqual(metrics.throughput, 1000.0)
        self.assertEqual(metrics.availability, 99.5)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2) 