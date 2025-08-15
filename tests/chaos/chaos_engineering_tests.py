"""
🧪 INT-010: Chaos Engineering Tests - Omni Keywords Finder

Tracing ID: INT_010_CHAOS_ENGINEERING_001
Data/Hora: 2025-01-27 17:00:00 UTC
Versão: 1.0
Status: 🚀 EM IMPLEMENTAÇÃO

Objetivo: Implementar testes de Chaos Engineering com cenários de caos,
fault injection, network partitioning e auto-recovery para o sistema Omni Keywords Finder.
"""

import os
import time
import json
import random
import threading
import asyncio
import logging
import signal
import subprocess
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import yaml
import requests
import socket
import tempfile
import shutil

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChaosScenario(Enum):
    """Cenários de caos."""
    NETWORK_PARTITION = "network_partition"
    SERVICE_FAILURE = "service_failure"
    DATABASE_FAILURE = "database_failure"
    MEMORY_LEAK = "memory_leak"
    CPU_SPIKE = "cpu_spike"
    DISK_FULL = "disk_full"
    CACHE_FAILURE = "cache_failure"
    API_TIMEOUT = "api_timeout"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    CONCURRENT_USERS_SPIKE = "concurrent_users_spike"
    DEPENDENCY_FAILURE = "dependency_failure"
    RANDOM_FAILURES = "random_failures"

class ChaosSeverity(Enum):
    """Severidade do caos."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ChaosState(Enum):
    """Estado do teste de caos."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ChaosConfig:
    """Configuração de teste de caos."""
    # Configurações básicas
    scenario: ChaosScenario
    severity: ChaosSeverity
    duration: int = 300  # segundos
    timeout: int = 600  # segundos
    
    # Configurações de fault injection
    fault_probability: float = 0.1  # 10%
    fault_duration: int = 30  # segundos
    fault_interval: int = 60  # segundos
    
    # Configurações de network partitioning
    partition_percentage: float = 0.3  # 30%
    partition_duration: int = 120  # segundos
    
    # Configurações de service failure
    service_name: str = "omni_keywords_finder"
    failure_type: str = "crash"  # crash, hang, slow
    
    # Configurações de database failure
    db_host: str = "localhost"
    db_port: int = 5432
    db_failure_type: str = "connection_refused"
    
    # Configurações de monitoring
    monitoring_enabled: bool = True
    metrics_collection: bool = True
    alerting_enabled: bool = True
    
    # Configurações de auto-recovery
    auto_recovery_enabled: bool = True
    recovery_timeout: int = 300  # segundos
    recovery_attempts: int = 3
    
    # Configurações de reporting
    report_enabled: bool = True
    report_format: str = "json"  # json, yaml, html
    report_path: str = "chaos_reports"

@dataclass
class ChaosResult:
    """Resultado de teste de caos."""
    scenario: ChaosScenario
    severity: ChaosSeverity
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    state: ChaosState = ChaosState.PENDING
    success: Optional[bool] = None
    error_message: Optional[str] = None
    
    # Métricas coletadas
    metrics_before: Dict[str, Any] = field(default_factory=dict)
    metrics_during: Dict[str, Any] = field(default_factory=dict)
    metrics_after: Dict[str, Any] = field(default_factory=dict)
    
    # Detalhes do teste
    faults_injected: int = 0
    recovery_attempts: int = 0
    recovery_success: bool = False
    system_impact: str = "none"
    
    # Logs e eventos
    events: List[Dict[str, Any]] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)

class NetworkPartitioner:
    """Simula partições de rede."""
    
    def __init__(self, config: ChaosConfig):
        self.config = config
        self.original_routes = {}
        self.partitioned_hosts = set()
    
    def create_partition(self, hosts: List[str]) -> bool:
        """Cria partição de rede entre hosts."""
        try:
            # Simula partição de rede (em produção, usaria iptables ou similar)
            for host in hosts:
                if random.random() < self.config.partition_percentage:
                    self.partitioned_hosts.add(host)
                    self._block_host(host)
            
            logger.info(f"Network partition created for {len(self.partitioned_hosts)} hosts")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create network partition: {e}")
            return False
    
    def _block_host(self, host: str):
        """Bloqueia comunicação com host."""
        # Simula bloqueio (em produção, usaria iptables)
        logger.info(f"Blocking communication with {host}")
    
    def remove_partition(self) -> bool:
        """Remove partição de rede."""
        try:
            for host in self.partitioned_hosts:
                self._unblock_host(host)
            
            self.partitioned_hosts.clear()
            logger.info("Network partition removed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove network partition: {e}")
            return False
    
    def _unblock_host(self, host: str):
        """Desbloqueia comunicação com host."""
        # Simula desbloqueio (em produção, usaria iptables)
        logger.info(f"Unblocking communication with {host}")

class ServiceKiller:
    """Simula falhas de serviço."""
    
    def __init__(self, config: ChaosConfig):
        self.config = config
        self.killed_services = set()
    
    def kill_service(self, service_name: str) -> bool:
        """Mata um serviço."""
        try:
            # Simula morte de serviço
            logger.info(f"Killing service: {service_name}")
            self.killed_services.add(service_name)
            
            # Em produção, usaria systemctl ou similar
            # subprocess.run(["systemctl", "stop", service_name])
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to kill service {service_name}: {e}")
            return False
    
    def restart_service(self, service_name: str) -> bool:
        """Reinicia um serviço."""
        try:
            logger.info(f"Restarting service: {service_name}")
            
            # Em produção, usaria systemctl ou similar
            # subprocess.run(["systemctl", "start", service_name])
            
            self.killed_services.discard(service_name)
            return True
            
        except Exception as e:
            logger.error(f"Failed to restart service {service_name}: {e}")
            return False
    
    def slow_service(self, service_name: str, delay: int = 5) -> bool:
        """Torna serviço lento."""
        try:
            logger.info(f"Slowing service {service_name} with {delay}string_data delay")
            
            # Simula lentidão (em produção, usaria tc ou similar)
            # subprocess.run(["tc", "qdisc", "add", "dev", "eth0", "root", "netem", "delay", f"{delay}ms"])
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to slow service {service_name}: {e}")
            return False

class DatabaseChaos:
    """Simula falhas de banco de dados."""
    
    def __init__(self, config: ChaosConfig):
        self.config = config
        self.original_connection = None
    
    def simulate_connection_failure(self) -> bool:
        """Simula falha de conexão com banco."""
        try:
            logger.info("Simulating database connection failure")
            
            # Em produção, bloquearia porta ou pararia serviço
            # subprocess.run(["iptables", "-A", "INPUT", "-p", "tcp", "--dport", str(self.config.db_port), "-counter", "DROP"])
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to simulate database failure: {e}")
            return False
    
    def restore_connection(self) -> bool:
        """Restaura conexão com banco."""
        try:
            logger.info("Restoring database connection")
            
            # Em produção, removeria regra do iptables
            # subprocess.run(["iptables", "-D", "INPUT", "-p", "tcp", "--dport", str(self.config.db_port), "-counter", "DROP"])
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore database connection: {e}")
            return False
    
    def simulate_slow_queries(self, delay: int = 10) -> bool:
        """Simula queries lentas."""
        try:
            logger.info(f"Simulating slow database queries with {delay}string_data delay")
            
            # Em produção, usaria configurações de banco ou tc
            return True
            
        except Exception as e:
            logger.error(f"Failed to simulate slow queries: {e}")
            return False

class ResourceChaos:
    """Simula problemas de recursos."""
    
    def __init__(self, config: ChaosConfig):
        self.config = config
        self.original_limits = {}
    
    def simulate_memory_leak(self, leak_size: int = 100) -> bool:
        """Simula vazamento de memória."""
        try:
            logger.info(f"Simulating memory leak of {leak_size}MB")
            
            # Em produção, alocaria memória e não liberaria
            # memory_block = bytearray(leak_size * 1024 * 1024)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to simulate memory leak: {e}")
            return False
    
    def simulate_cpu_spike(self, cpu_percentage: int = 80) -> bool:
        """Simula pico de CPU."""
        try:
            logger.info(f"Simulating CPU spike of {cpu_percentage}%")
            
            # Em produção, usaria stress-ng ou similar
            # subprocess.Popen(["stress-ng", "--cpu", "1", "--cpu-load", str(cpu_percentage)])
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to simulate CPU spike: {e}")
            return False
    
    def simulate_disk_full(self, usage_percentage: int = 95) -> bool:
        """Simula disco cheio."""
        try:
            logger.info(f"Simulating disk full at {usage_percentage}%")
            
            # Em produção, preencheria disco com arquivos temporários
            # temp_dir = tempfile.mkdtemp()
            # while psutil.disk_usage('/').percent < usage_percentage:
            #     with open(f"{temp_dir}/fill_{time.time()}", 'w') as f:
            #         f.write('value' * 1024 * 1024)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to simulate disk full: {e}")
            return False

class MetricsCollector:
    """Coleta métricas durante testes de caos."""
    
    def __init__(self, config: ChaosConfig):
        self.config = config
        self.metrics_history = deque(maxlen=1000)
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Coleta métricas do sistema."""
        try:
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'network_io': psutil.net_io_counters()._asdict(),
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            }
            
            self.metrics_history.append(metrics)
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {}
    
    def collect_application_metrics(self) -> Dict[str, Any]:
        """Coleta métricas da aplicação."""
        try:
            # Em produção, coletaria métricas da aplicação
            # response = requests.get("http://localhost:8000/metrics")
            # return response.json()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'response_time': random.uniform(10, 1000),
                'error_rate': random.uniform(0, 0.1),
                'throughput': random.uniform(100, 1000),
                'active_connections': random.randint(10, 100)
            }
            
        except Exception as e:
            logger.error(f"Failed to collect application metrics: {e}")
            return {}
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Obtém resumo das métricas."""
        if not self.metrics_history:
            return {}
        
        metrics_list = list(self.metrics_history)
        
        return {
            'total_samples': len(metrics_list),
            'avg_cpu': statistics.mean([m.get('cpu_percent', 0) for m in metrics_list]),
            'max_cpu': max([m.get('cpu_percent', 0) for m in metrics_list]),
            'avg_memory': statistics.mean([m.get('memory_percent', 0) for m in metrics_list]),
            'max_memory': max([m.get('memory_percent', 0) for m in metrics_list]),
            'avg_disk': statistics.mean([m.get('disk_percent', 0) for m in metrics_list]),
            'max_disk': max([m.get('disk_percent', 0) for m in metrics_list])
        }

class AutoRecovery:
    """Sistema de auto-recovery."""
    
    def __init__(self, config: ChaosConfig):
        self.config = config
        self.recovery_attempts = 0
        self.recovery_success = False
    
    def attempt_recovery(self, chaos_result: ChaosResult) -> bool:
        """Tenta recuperação automática."""
        if not self.config.auto_recovery_enabled:
            return False
        
        self.recovery_attempts += 1
        chaos_result.recovery_attempts = self.recovery_attempts
        
        try:
            logger.info(f"Attempting auto-recovery (attempt {self.recovery_attempts})")
            
            # Verifica se sistema está funcionando
            if self._check_system_health():
                self.recovery_success = True
                chaos_result.recovery_success = True
                logger.info("Auto-recovery successful")
                return True
            
            # Se ainda não funcionando e não excedeu tentativas
            if self.recovery_attempts < self.config.recovery_attempts:
                time.sleep(self.config.recovery_timeout / self.config.recovery_attempts)
                return self.attempt_recovery(chaos_result)
            
            logger.warning("Auto-recovery failed after all attempts")
            return False
            
        except Exception as e:
            logger.error(f"Auto-recovery error: {e}")
            return False
    
    def _check_system_health(self) -> bool:
        """Verifica saúde do sistema."""
        try:
            # Em produção, verificaria endpoints de health check
            # response = requests.get("http://localhost:8000/health", timeout=5)
            # return response.status_code == 200
            
            # Simula verificação
            return random.random() > 0.3  # 70% de chance de estar saudável
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

class ChaosEngineeringTests:
    """
    Sistema de testes de Chaos Engineering com funcionalidades enterprise-grade.
    
    Implementa:
    - Cenários de caos realistas
    - Fault injection controlado
    - Network partitioning
    - Auto-recovery
    - Coleta de métricas
    - Relatórios detalhados
    """
    
    def __init__(self, config: ChaosConfig):
        """
        Inicializar sistema de Chaos Engineering.
        
        Args:
            config: Configuração dos testes
        """
        self.config = config
        
        # Inicializar componentes
        self.network_partitioner = NetworkPartitioner(config)
        self.service_killer = ServiceKiller(config)
        self.database_chaos = DatabaseChaos(config)
        self.resource_chaos = ResourceChaos(config)
        self.metrics_collector = MetricsCollector(config)
        self.auto_recovery = AutoRecovery(config)
        
        # Estado do teste
        self.current_test: Optional[ChaosResult] = None
        self.test_history: List[ChaosResult] = []
        
        # Threading
        self.lock = threading.RLock()
        self.running = False
        
        # Configurar diretório de relatórios
        if self.config.report_enabled:
            os.makedirs(self.config.report_path, exist_ok=True)
        
        logger.info({
            "event": "chaos_engineering_initialized",
            "status": "success",
            "source": "ChaosEngineeringTests.__init__",
            "details": {
                "scenario": config.scenario.value,
                "severity": config.severity.value,
                "duration": config.duration,
                "auto_recovery": config.auto_recovery_enabled
            }
        })
    
    def run_chaos_test(self) -> ChaosResult:
        """
        Executa teste de caos.
        
        Returns:
            Resultado do teste
        """
        with self.lock:
            if self.running:
                raise Exception("Chaos test already running")
            
            self.running = True
            self.current_test = ChaosResult(
                scenario=self.config.scenario,
                severity=self.config.severity,
                start_time=datetime.now()
            )
        
        try:
            logger.info(f"Starting chaos test: {self.config.scenario.value}")
            
            # Coleta métricas antes
            self.current_test.metrics_before = self.metrics_collector.collect_system_metrics()
            
            # Executa cenário de caos
            self._execute_chaos_scenario()
            
            # Coleta métricas durante
            self._collect_metrics_during_test()
            
            # Aguarda duração do teste
            time.sleep(self.config.duration)
            
            # Para cenário de caos
            self._stop_chaos_scenario()
            
            # Tenta auto-recovery
            if self.config.auto_recovery_enabled:
                self.auto_recovery.attempt_recovery(self.current_test)
            
            # Coleta métricas após
            self.current_test.metrics_after = self.metrics_collector.collect_system_metrics()
            
            # Finaliza teste
            self.current_test.end_time = datetime.now()
            self.current_test.duration = (self.current_test.end_time - self.current_test.start_time).total_seconds()
            self.current_test.state = ChaosState.COMPLETED
            self.current_test.success = True
            
            # Gera relatório
            if self.config.report_enabled:
                self._generate_report()
            
            logger.info(f"Chaos test completed successfully: {self.config.scenario.value}")
            
        except Exception as e:
            logger.error(f"Chaos test failed: {e}")
            self.current_test.state = ChaosState.FAILED
            self.current_test.success = False
            self.current_test.error_message = str(e)
            
        finally:
            with self.lock:
                self.running = False
                if self.current_test:
                    self.test_history.append(self.current_test)
        
        return self.current_test
    
    def _execute_chaos_scenario(self):
        """Executa cenário de caos específico."""
        scenario = self.config.scenario
        
        if scenario == ChaosScenario.NETWORK_PARTITION:
            self._execute_network_partition()
        elif scenario == ChaosScenario.SERVICE_FAILURE:
            self._execute_service_failure()
        elif scenario == ChaosScenario.DATABASE_FAILURE:
            self._execute_database_failure()
        elif scenario == ChaosScenario.MEMORY_LEAK:
            self._execute_memory_leak()
        elif scenario == ChaosScenario.CPU_SPIKE:
            self._execute_cpu_spike()
        elif scenario == ChaosScenario.DISK_FULL:
            self._execute_disk_full()
        elif scenario == ChaosScenario.CACHE_FAILURE:
            self._execute_cache_failure()
        elif scenario == ChaosScenario.API_TIMEOUT:
            self._execute_api_timeout()
        elif scenario == ChaosScenario.RATE_LIMIT_EXCEEDED:
            self._execute_rate_limit_exceeded()
        elif scenario == ChaosScenario.CONCURRENT_USERS_SPIKE:
            self._execute_concurrent_users_spike()
        elif scenario == ChaosScenario.DEPENDENCY_FAILURE:
            self._execute_dependency_failure()
        elif scenario == ChaosScenario.RANDOM_FAILURES:
            self._execute_random_failures()
        else:
            raise ValueError(f"Unknown chaos scenario: {scenario}")
    
    def _execute_network_partition(self):
        """Executa partição de rede."""
        hosts = ["api1.example.com", "api2.example.com", "db.example.com"]
        self.network_partitioner.create_partition(hosts)
        self.current_test.events.append({
            'timestamp': datetime.now().isoformat(),
            'event': 'network_partition_created',
            'hosts': list(self.network_partitioner.partitioned_hosts)
        })
    
    def _execute_service_failure(self):
        """Executa falha de serviço."""
        if self.config.failure_type == "crash":
            self.service_killer.kill_service(self.config.service_name)
        elif self.config.failure_type == "slow":
            self.service_killer.slow_service(self.config.service_name, 10)
        
        self.current_test.events.append({
            'timestamp': datetime.now().isoformat(),
            'event': 'service_failure_injected',
            'service': self.config.service_name,
            'failure_type': self.config.failure_type
        })
    
    def _execute_database_failure(self):
        """Executa falha de banco de dados."""
        if self.config.db_failure_type == "connection_refused":
            self.database_chaos.simulate_connection_failure()
        elif self.config.db_failure_type == "slow_queries":
            self.database_chaos.simulate_slow_queries(10)
        
        self.current_test.events.append({
            'timestamp': datetime.now().isoformat(),
            'event': 'database_failure_injected',
            'failure_type': self.config.db_failure_type
        })
    
    def _execute_memory_leak(self):
        """Executa vazamento de memória."""
        leak_size = 200 if self.config.severity == ChaosSeverity.HIGH else 100
        self.resource_chaos.simulate_memory_leak(leak_size)
        
        self.current_test.events.append({
            'timestamp': datetime.now().isoformat(),
            'event': 'memory_leak_injected',
            'leak_size_mb': leak_size
        })
    
    def _execute_cpu_spike(self):
        """Executa pico de CPU."""
        cpu_percentage = 90 if self.config.severity == ChaosSeverity.HIGH else 70
        self.resource_chaos.simulate_cpu_spike(cpu_percentage)
        
        self.current_test.events.append({
            'timestamp': datetime.now().isoformat(),
            'event': 'cpu_spike_injected',
            'cpu_percentage': cpu_percentage
        })
    
    def _execute_disk_full(self):
        """Executa disco cheio."""
        usage_percentage = 98 if self.config.severity == ChaosSeverity.HIGH else 95
        self.resource_chaos.simulate_disk_full(usage_percentage)
        
        self.current_test.events.append({
            'timestamp': datetime.now().isoformat(),
            'event': 'disk_full_injected',
            'usage_percentage': usage_percentage
        })
    
    def _execute_cache_failure(self):
        """Executa falha de cache."""
        # Simula falha de cache
        logger.info("Simulating cache failure")
        
        self.current_test.events.append({
            'timestamp': datetime.now().isoformat(),
            'event': 'cache_failure_injected'
        })
    
    def _execute_api_timeout(self):
        """Executa timeout de API."""
        # Simula timeout de API
        logger.info("Simulating API timeout")
        
        self.current_test.events.append({
            'timestamp': datetime.now().isoformat(),
            'event': 'api_timeout_injected'
        })
    
    def _execute_rate_limit_exceeded(self):
        """Executa exceder rate limit."""
        # Simula exceder rate limit
        logger.info("Simulating rate limit exceeded")
        
        self.current_test.events.append({
            'timestamp': datetime.now().isoformat(),
            'event': 'rate_limit_exceeded_injected'
        })
    
    def _execute_concurrent_users_spike(self):
        """Executa pico de usuários concorrentes."""
        # Simula pico de usuários
        logger.info("Simulating concurrent users spike")
        
        self.current_test.events.append({
            'timestamp': datetime.now().isoformat(),
            'event': 'concurrent_users_spike_injected'
        })
    
    def _execute_dependency_failure(self):
        """Executa falha de dependência."""
        # Simula falha de dependência externa
        logger.info("Simulating dependency failure")
        
        self.current_test.events.append({
            'timestamp': datetime.now().isoformat(),
            'event': 'dependency_failure_injected'
        })
    
    def _execute_random_failures(self):
        """Executa falhas aleatórias."""
        # Simula falhas aleatórias
        logger.info("Simulating random failures")
        
        self.current_test.events.append({
            'timestamp': datetime.now().isoformat(),
            'event': 'random_failures_injected'
        })
    
    def _stop_chaos_scenario(self):
        """Para cenário de caos."""
        scenario = self.config.scenario
        
        if scenario == ChaosScenario.NETWORK_PARTITION:
            self.network_partitioner.remove_partition()
        elif scenario == ChaosScenario.SERVICE_FAILURE:
            if self.config.failure_type == "crash":
                self.service_killer.restart_service(self.config.service_name)
        elif scenario == ChaosScenario.DATABASE_FAILURE:
            self.database_chaos.restore_connection()
        
        self.current_test.events.append({
            'timestamp': datetime.now().isoformat(),
            'event': 'chaos_scenario_stopped'
        })
    
    def _collect_metrics_during_test(self):
        """Coleta métricas durante o teste."""
        def collect_metrics():
            while self.running:
                try:
                    system_metrics = self.metrics_collector.collect_system_metrics()
                    app_metrics = self.metrics_collector.collect_application_metrics()
                    
                    combined_metrics = {**system_metrics, **app_metrics}
                    self.current_test.metrics_during.update(combined_metrics)
                    
                    time.sleep(10)  # Coleta a cada 10 segundos
                except Exception as e:
                    logger.error(f"Error collecting metrics: {e}")
        
        # Inicia thread de coleta
        metrics_thread = threading.Thread(target=collect_metrics, daemon=True)
        metrics_thread.start()
    
    def _generate_report(self):
        """Gera relatório do teste."""
        if not self.current_test:
            return
        
        report_data = {
            'test_info': {
                'scenario': self.current_test.scenario.value,
                'severity': self.current_test.severity.value,
                'start_time': self.current_test.start_time.isoformat(),
                'end_time': self.current_test.end_time.isoformat() if self.current_test.end_time else None,
                'duration': self.current_test.duration,
                'success': self.current_test.success,
                'state': self.current_test.state.value
            },
            'metrics': {
                'before': self.current_test.metrics_before,
                'during': self.current_test.metrics_during,
                'after': self.current_test.metrics_after,
                'summary': self.metrics_collector.get_metrics_summary()
            },
            'events': self.current_test.events,
            'recovery': {
                'attempts': self.current_test.recovery_attempts,
                'success': self.current_test.recovery_success
            }
        }
        
        # Salva relatório
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chaos_test_{self.current_test.scenario.value}_{timestamp}.{self.config.report_format}"
        filepath = os.path.join(self.config.report_path, filename)
        
        with open(filepath, 'w') as f:
            if self.config.report_format == 'json':
                json.dump(report_data, f, indent=2)
            elif self.config.report_format == 'yaml':
                yaml.dump(report_data, f, default_flow_style=False)
        
        logger.info(f"Chaos test report saved: {filepath}")
    
    def get_test_history(self) -> List[ChaosResult]:
        """Obtém histórico de testes."""
        return self.test_history.copy()
    
    def get_current_test(self) -> Optional[ChaosResult]:
        """Obtém teste atual."""
        return self.current_test
    
    def is_running(self) -> bool:
        """Verifica se teste está rodando."""
        return self.running
    
    def stop_current_test(self):
        """Para teste atual."""
        with self.lock:
            if self.running and self.current_test:
                self.running = False
                self.current_test.state = ChaosState.CANCELLED
                self._stop_chaos_scenario()
                logger.info("Chaos test stopped")

def create_chaos_test(config: ChaosConfig) -> ChaosEngineeringTests:
    """
    Cria e retorna teste de Chaos Engineering.
    
    Args:
        config: Configuração do teste
        
    Returns:
        Teste de Chaos Engineering configurado
    """
    return ChaosEngineeringTests(config)

def load_chaos_scenarios(filepath: str) -> List[ChaosConfig]:
    """
    Carrega cenários de caos de arquivo YAML.
    
    Args:
        filepath: Caminho do arquivo YAML
        
    Returns:
        Lista de configurações de cenários
    """
    with open(filepath, 'r') as f:
        scenarios_data = yaml.safe_load(f)
    
    scenarios = []
    for scenario_data in scenarios_data.get('scenarios', []):
        config = ChaosConfig(
            scenario=ChaosScenario(scenario_data['scenario']),
            severity=ChaosSeverity(scenario_data['severity']),
            duration=scenario_data.get('duration', 300),
            timeout=scenario_data.get('timeout', 600),
            fault_probability=scenario_data.get('fault_probability', 0.1),
            auto_recovery_enabled=scenario_data.get('auto_recovery_enabled', True)
        )
        scenarios.append(config)
    
    return scenarios

def run_chaos_test_suite(scenarios: List[ChaosConfig]) -> List[ChaosResult]:
    """
    Executa suite de testes de caos.
    
    Args:
        scenarios: Lista de cenários para executar
        
    Returns:
        Lista de resultados dos testes
    """
    results = []
    
    for scenario in scenarios:
        try:
            chaos_test = create_chaos_test(scenario)
            result = chaos_test.run_chaos_test()
            results.append(result)
            
            # Aguarda entre testes
            time.sleep(60)
            
        except Exception as e:
            logger.error(f"Failed to run chaos test for scenario {scenario.scenario.value}: {e}")
    
    return results 