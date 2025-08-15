"""
🔍 Chaos Engineering Experiments System
📅 Generated: 2025-01-27
🎯 Purpose: Controlled chaos experiments to test system resilience
📋 Tracing ID: CHAOS_EXPERIMENTS_001_20250127
"""

import logging
import time
import asyncio
import random
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import threading
from datetime import datetime, timedelta
import psutil
import os
import signal
import subprocess
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class ExperimentType(Enum):
    """Types of chaos experiments"""
    NETWORK_LATENCY = "network_latency"
    NETWORK_PACKET_LOSS = "network_packet_loss"
    NETWORK_PARTITION = "network_partition"
    CPU_STRESS = "cpu_stress"
    MEMORY_STRESS = "memory_stress"
    DISK_STRESS = "disk_stress"
    PROCESS_KILL = "process_kill"
    SERVICE_RESTART = "service_restart"
    DATABASE_FAILURE = "database_failure"
    CACHE_FAILURE = "cache_failure"
    DEPENDENCY_FAILURE = "dependency_failure"
    TIMEOUT_INJECTION = "timeout_injection"
    ERROR_INJECTION = "error_injection"
    CUSTOM = "custom"


class ExperimentStatus(Enum):
    """Experiment execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLBACK = "rollback"


class ExperimentSeverity(Enum):
    """Experiment severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ExperimentConfig:
    """Configuration for chaos experiments"""
    experiment_type: ExperimentType
    duration: int = 300  # seconds
    severity: ExperimentSeverity = ExperimentSeverity.MEDIUM
    target_services: List[str] = field(default_factory=list)
    target_hosts: List[str] = field(default_factory=list)
    target_ports: List[int] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    auto_rollback: bool = True
    rollback_timeout: int = 60  # seconds
    monitoring_enabled: bool = True
    alert_on_failure: bool = True
    custom_script: Optional[str] = None
    environment: str = "staging"


@dataclass
class ExperimentResult:
    """Result of chaos experiment"""
    experiment_id: str
    experiment_type: ExperimentType
    status: ExperimentStatus
    start_time: float
    end_time: Optional[float] = None
    duration: float = 0.0
    success: bool = False
    error_message: str = ""
    metrics_before: Dict[str, Any] = field(default_factory=dict)
    metrics_during: Dict[str, Any] = field(default_factory=dict)
    metrics_after: Dict[str, Any] = field(default_factory=dict)
    rollback_successful: bool = True
    impact_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExperimentMetrics:
    """Metrics collected during experiment"""
    timestamp: float
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    network_latency: float = 0.0
    error_rate: float = 0.0
    response_time: float = 0.0
    throughput: float = 0.0
    availability: float = 100.0
    custom_metrics: Dict[str, Any] = field(default_factory=dict)


class ChaosExperiment:
    """
    Base class for chaos experiments
    """
    
    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.experiment_id = self._generate_experiment_id()
        self.status = ExperimentStatus.PENDING
        self.start_time = 0.0
        self.end_time = None
        self.metrics_collector = None
        self.rollback_handlers = []
        self.monitoring_callbacks = []
        
    def _generate_experiment_id(self) -> str:
        """Generate unique experiment ID"""
        timestamp = int(time.time())
        random_suffix = random.randint(1000, 9999)
        return f"chaos_{self.config.experiment_type.value}_{timestamp}_{random_suffix}"
    
    async def run(self) -> ExperimentResult:
        """Run the chaos experiment"""
        try:
            logger.info(f"Starting chaos experiment: {self.experiment_id}")
            self.status = ExperimentStatus.RUNNING
            self.start_time = time.time()
            
            # Collect baseline metrics
            metrics_before = await self._collect_baseline_metrics()
            
            # Execute experiment
            await self._execute_experiment()
            
            # Monitor during experiment
            metrics_during = await self._monitor_during_experiment()
            
            # Wait for experiment duration
            await asyncio.sleep(self.config.duration)
            
            # Rollback if enabled
            rollback_successful = True
            if self.config.auto_rollback:
                rollback_successful = await self._rollback_experiment()
            
            # Collect final metrics
            metrics_after = await self._collect_final_metrics()
            
            # Calculate impact
            impact_score = self._calculate_impact_score(metrics_before, metrics_during, metrics_after)
            
            self.status = ExperimentStatus.COMPLETED
            self.end_time = time.time()
            
            result = ExperimentResult(
                experiment_id=self.experiment_id,
                experiment_type=self.config.experiment_type,
                status=self.status,
                start_time=self.start_time,
                end_time=self.end_time,
                duration=self.end_time - self.start_time,
                success=True,
                metrics_before=metrics_before,
                metrics_during=metrics_during,
                metrics_after=metrics_after,
                rollback_successful=rollback_successful,
                impact_score=impact_score
            )
            
            logger.info(f"Chaos experiment completed: {self.experiment_id}")
            return result
            
        except Exception as e:
            logger.error(f"Chaos experiment failed: {self.experiment_id} - {e}")
            self.status = ExperimentStatus.FAILED
            self.end_time = time.time()
            
            # Attempt rollback
            rollback_successful = await self._rollback_experiment()
            
            return ExperimentResult(
                experiment_id=self.experiment_id,
                experiment_type=self.config.experiment_type,
                status=self.status,
                start_time=self.start_time,
                end_time=self.end_time,
                duration=self.end_time - self.start_time if self.end_time else 0.0,
                success=False,
                error_message=str(e),
                rollback_successful=rollback_successful
            )
    
    async def _execute_experiment(self):
        """Execute the specific experiment"""
        raise NotImplementedError("Subclasses must implement _execute_experiment")
    
    async def _rollback_experiment(self) -> bool:
        """Rollback the experiment"""
        try:
            logger.info(f"Rolling back experiment: {self.experiment_id}")
            
            for handler in self.rollback_handlers:
                try:
                    await handler()
                except Exception as e:
                    logger.error(f"Rollback handler failed: {e}")
            
            return True
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    async def _collect_baseline_metrics(self) -> Dict[str, Any]:
        """Collect baseline metrics before experiment"""
        metrics = ExperimentMetrics(timestamp=time.time())
        
        # System metrics
        metrics.cpu_usage = psutil.cpu_percent(interval=1)
        metrics.memory_usage = psutil.virtual_memory().percent
        metrics.disk_usage = psutil.disk_usage('/').percent
        
        # Network metrics
        try:
            metrics.network_latency = await self._measure_network_latency()
        except Exception as e:
            logger.warning(f"Failed to measure network latency: {e}")
        
        # Custom metrics
        for callback in self.monitoring_callbacks:
            try:
                custom_metrics = await callback("before")
                metrics.custom_metrics.update(custom_metrics)
            except Exception as e:
                logger.warning(f"Custom metrics callback failed: {e}")
        
        return metrics.__dict__
    
    async def _monitor_during_experiment(self) -> Dict[str, Any]:
        """Monitor system during experiment"""
        metrics = ExperimentMetrics(timestamp=time.time())
        
        # Collect metrics during experiment
        metrics.cpu_usage = psutil.cpu_percent(interval=1)
        metrics.memory_usage = psutil.virtual_memory().percent
        metrics.disk_usage = psutil.disk_usage('/').percent
        
        # Custom monitoring
        for callback in self.monitoring_callbacks:
            try:
                custom_metrics = await callback("during")
                metrics.custom_metrics.update(custom_metrics)
            except Exception as e:
                logger.warning(f"Custom monitoring callback failed: {e}")
        
        return metrics.__dict__
    
    async def _collect_final_metrics(self) -> Dict[str, Any]:
        """Collect final metrics after experiment"""
        metrics = ExperimentMetrics(timestamp=time.time())
        
        # System metrics
        metrics.cpu_usage = psutil.cpu_percent(interval=1)
        metrics.memory_usage = psutil.virtual_memory().percent
        metrics.disk_usage = psutil.disk_usage('/').percent
        
        # Network metrics
        try:
            metrics.network_latency = await self._measure_network_latency()
        except Exception as e:
            logger.warning(f"Failed to measure network latency: {e}")
        
        # Custom metrics
        for callback in self.monitoring_callbacks:
            try:
                custom_metrics = await callback("after")
                metrics.custom_metrics.update(custom_metrics)
            except Exception as e:
                logger.warning(f"Custom metrics callback failed: {e}")
        
        return metrics.__dict__
    
    async def _measure_network_latency(self) -> float:
        """Measure network latency to target hosts"""
        if not self.config.target_hosts:
            return 0.0
        
        latencies = []
        for host in self.config.target_hosts:
            try:
                start_time = time.time()
                # Simple ping-like measurement
                process = await asyncio.create_subprocess_exec(
                    'ping', '-c', '1', host,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
                end_time = time.time()
                latencies.append((end_time - start_time) * 1000)  # Convert to ms
            except Exception as e:
                logger.warning(f"Failed to ping {host}: {e}")
        
        return statistics.mean(latencies) if latencies else 0.0
    
    def _calculate_impact_score(self, metrics_before: Dict[str, Any], 
                               metrics_during: Dict[str, Any], 
                               metrics_after: Dict[str, Any]) -> float:
        """Calculate impact score of the experiment"""
        impact_score = 0.0
        
        # CPU impact
        if 'cpu_usage' in metrics_before and 'cpu_usage' in metrics_during:
            cpu_impact = abs(metrics_during['cpu_usage'] - metrics_before['cpu_usage'])
            impact_score += cpu_impact * 0.2
        
        # Memory impact
        if 'memory_usage' in metrics_before and 'memory_usage' in metrics_during:
            memory_impact = abs(metrics_during['memory_usage'] - metrics_before['memory_usage'])
            impact_score += memory_impact * 0.2
        
        # Network impact
        if 'network_latency' in metrics_before and 'network_latency' in metrics_during:
            latency_impact = abs(metrics_during['network_latency'] - metrics_before['network_latency'])
            impact_score += min(latency_impact / 100, 1.0) * 0.3  # Normalize to 0-1
        
        # Recovery score
        if 'cpu_usage' in metrics_after and 'cpu_usage' in metrics_before:
            recovery_score = 1.0 - abs(metrics_after['cpu_usage'] - metrics_before['cpu_usage']) / 100
            impact_score += recovery_score * 0.3
        
        return min(impact_score, 1.0)
    
    def add_rollback_handler(self, handler: Callable):
        """Add rollback handler"""
        self.rollback_handlers.append(handler)
    
    def add_monitoring_callback(self, callback: Callable):
        """Add monitoring callback"""
        self.monitoring_callbacks.append(callback)


class NetworkLatencyExperiment(ChaosExperiment):
    """Network latency injection experiment"""
    
    async def _execute_experiment(self):
        """Inject network latency"""
        latency_ms = self.config.parameters.get('latency_ms', 100)
        jitter_ms = self.config.parameters.get('jitter_ms', 10)
        
        logger.info(f"Injecting network latency: {latency_ms}ms ± {jitter_ms}ms")
        
        # Use tc (traffic control) to inject latency
        for host in self.config.target_hosts:
            try:
                # Add latency using tc
                cmd = [
                    'tc', 'qdisc', 'add', 'dev', 'eth0', 'root', 'netem',
                    'delay', f'{latency_ms}ms', f'{jitter_ms}ms'
                ]
                
                process = await asyncio.create_subprocess_exec(
                    *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
                
                # Add rollback handler
                self.add_rollback_handler(self._remove_latency)
                
            except Exception as e:
                logger.error(f"Failed to inject latency for {host}: {e}")
    
    async def _remove_latency(self):
        """Remove network latency"""
        try:
            cmd = ['tc', 'qdisc', 'del', 'dev', 'eth0', 'root']
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
        except Exception as e:
            logger.error(f"Failed to remove latency: {e}")


class PacketLossExperiment(ChaosExperiment):
    """Network packet loss injection experiment"""
    
    async def _execute_experiment(self):
        """Inject packet loss"""
        loss_percent = self.config.parameters.get('loss_percent', 5.0)
        
        logger.info(f"Injecting packet loss: {loss_percent}%")
        
        for host in self.config.target_hosts:
            try:
                # Add packet loss using tc
                cmd = [
                    'tc', 'qdisc', 'add', 'dev', 'eth0', 'root', 'netem',
                    'loss', f'{loss_percent}%'
                ]
                
                process = await asyncio.create_subprocess_exec(
                    *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
                
                # Add rollback handler
                self.add_rollback_handler(self._remove_packet_loss)
                
            except Exception as e:
                logger.error(f"Failed to inject packet loss for {host}: {e}")
    
    async def _remove_packet_loss(self):
        """Remove packet loss"""
        try:
            cmd = ['tc', 'qdisc', 'del', 'dev', 'eth0', 'root']
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
        except Exception as e:
            logger.error(f"Failed to remove packet loss: {e}")


class CPUStressExperiment(ChaosExperiment):
    """CPU stress experiment"""
    
    async def _execute_experiment(self):
        """Stress CPU"""
        cpu_load = self.config.parameters.get('cpu_load', 80)
        cores = self.config.parameters.get('cores', psutil.cpu_count())
        
        logger.info(f"Stressing CPU: {cpu_load}% load on {cores} cores")
        
        # Start stress-ng process
        cmd = ['stress-ng', '--cpu', str(cores), '--cpu-load', str(cpu_load)]
        
        self.stress_process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        
        # Add rollback handler
        self.add_rollback_handler(self._stop_cpu_stress)
    
    async def _stop_cpu_stress(self):
        """Stop CPU stress"""
        if hasattr(self, 'stress_process'):
            try:
                self.stress_process.terminate()
                await self.stress_process.wait()
            except Exception as e:
                logger.error(f"Failed to stop CPU stress: {e}")


class MemoryStressExperiment(ChaosExperiment):
    """Memory stress experiment"""
    
    async def _execute_experiment(self):
        """Stress memory"""
        memory_mb = self.config.parameters.get('memory_mb', 1024)
        
        logger.info(f"Stressing memory: {memory_mb}MB")
        
        # Start stress-ng process
        cmd = ['stress-ng', '--vm', '1', '--vm-bytes', f'{memory_mb}M']
        
        self.stress_process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        
        # Add rollback handler
        self.add_rollback_handler(self._stop_memory_stress)
    
    async def _stop_memory_stress(self):
        """Stop memory stress"""
        if hasattr(self, 'stress_process'):
            try:
                self.stress_process.terminate()
                await self.stress_process.wait()
            except Exception as e:
                logger.error(f"Failed to stop memory stress: {e}")


class ProcessKillExperiment(ChaosExperiment):
    """Process kill experiment"""
    
    async def _execute_experiment(self):
        """Kill target processes"""
        process_names = self.config.parameters.get('process_names', [])
        
        logger.info(f"Killing processes: {process_names}")
        
        killed_processes = []
        
        for process_name in process_names:
            try:
                # Find processes by name
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info['name'] == process_name:
                        proc.terminate()
                        killed_processes.append((proc.info['pid'], process_name))
                        logger.info(f"Killed process: {process_name} (PID: {proc.info['pid']})")
                
                # Add rollback handler
                self.add_rollback_handler(lambda: self._restart_processes(process_names))
                
            except Exception as e:
                logger.error(f"Failed to kill process {process_name}: {e}")
        
        self.killed_processes = killed_processes
    
    async def _restart_processes(self, process_names: List[str]):
        """Restart killed processes"""
        for process_name in process_names:
            try:
                # This is a simplified restart - in production you'd want proper service management
                logger.info(f"Attempting to restart process: {process_name}")
                # Add your service restart logic here
            except Exception as e:
                logger.error(f"Failed to restart process {process_name}: {e}")


class ServiceRestartExperiment(ChaosExperiment):
    """Service restart experiment"""
    
    async def _execute_experiment(self):
        """Restart target services"""
        services = self.config.parameters.get('services', [])
        
        logger.info(f"Restarting services: {services}")
        
        for service in services:
            try:
                # Stop service
                stop_cmd = ['systemctl', 'stop', service]
                process = await asyncio.create_subprocess_exec(
                    *stop_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
                
                # Wait a bit
                await asyncio.sleep(2)
                
                # Start service
                start_cmd = ['systemctl', 'start', service]
                process = await asyncio.create_subprocess_exec(
                    *start_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
                
                logger.info(f"Restarted service: {service}")
                
            except Exception as e:
                logger.error(f"Failed to restart service {service}: {e}")


class CustomExperiment(ChaosExperiment):
    """Custom experiment using external script"""
    
    async def _execute_experiment(self):
        """Execute custom script"""
        script_path = self.config.custom_script
        
        if not script_path or not os.path.exists(script_path):
            raise ValueError(f"Custom script not found: {script_path}")
        
        logger.info(f"Executing custom script: {script_path}")
        
        # Execute custom script
        process = await asyncio.create_subprocess_exec(
            script_path, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError(f"Custom script failed: {stderr.decode()}")
        
        logger.info(f"Custom script executed successfully: {stdout.decode()}")


class ChaosExperimentFactory:
    """Factory for creating chaos experiments"""
    
    @staticmethod
    def create_experiment(config: ExperimentConfig) -> ChaosExperiment:
        """Create experiment based on type"""
        if config.experiment_type == ExperimentType.NETWORK_LATENCY:
            return NetworkLatencyExperiment(config)
        elif config.experiment_type == ExperimentType.NETWORK_PACKET_LOSS:
            return PacketLossExperiment(config)
        elif config.experiment_type == ExperimentType.CPU_STRESS:
            return CPUStressExperiment(config)
        elif config.experiment_type == ExperimentType.MEMORY_STRESS:
            return MemoryStressExperiment(config)
        elif config.experiment_type == ExperimentType.PROCESS_KILL:
            return ProcessKillExperiment(config)
        elif config.experiment_type == ExperimentType.SERVICE_RESTART:
            return ServiceRestartExperiment(config)
        elif config.experiment_type == ExperimentType.CUSTOM:
            return CustomExperiment(config)
        else:
            raise ValueError(f"Unsupported experiment type: {config.experiment_type}")


# Global experiment manager
_experiment_manager: Optional[Dict[str, ChaosExperiment]] = None


def get_experiment_manager() -> Dict[str, ChaosExperiment]:
    """Get global experiment manager"""
    global _experiment_manager
    if _experiment_manager is None:
        _experiment_manager = {}
    return _experiment_manager


def create_experiment(config: ExperimentConfig) -> ChaosExperiment:
    """Create and register a new experiment"""
    manager = get_experiment_manager()
    
    experiment = ChaosExperimentFactory.create_experiment(config)
    manager[experiment.experiment_id] = experiment
    
    return experiment


async def run_experiment(config: ExperimentConfig) -> ExperimentResult:
    """Run a chaos experiment"""
    experiment = create_experiment(config)
    return await experiment.run()


def get_experiment(experiment_id: str) -> Optional[ChaosExperiment]:
    """Get experiment by ID"""
    manager = get_experiment_manager()
    return manager.get(experiment_id)


def list_experiments() -> List[str]:
    """List all experiment IDs"""
    manager = get_experiment_manager()
    return list(manager.keys())


def cancel_experiment(experiment_id: str) -> bool:
    """Cancel a running experiment"""
    experiment = get_experiment(experiment_id)
    if experiment and experiment.status == ExperimentStatus.RUNNING:
        experiment.status = ExperimentStatus.CANCELLED
        return True
    return False 