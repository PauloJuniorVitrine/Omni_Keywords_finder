"""
🧪 INT-011: Advanced Load Testing - Omni Keywords Finder

Tracing ID: INT_011_ADVANCED_LOAD_TESTING_001
Data/Hora: 2025-01-27 17:00:00 UTC
Versão: 1.0
Status: 🚀 EM IMPLEMENTAÇÃO

Objetivo: Implementar testes de carga avançados com cenários de stress,
spike testing, endurance testing e auto-scaling validation para o sistema Omni Keywords Finder.
"""

import os
import time
import json
import random
import threading
import asyncio
import logging
import statistics
import requests
import aiohttp
import concurrent.futures
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import yaml
import psutil
import matplotlib.pyplot as plt
import numpy as np
from dataclasses_json import dataclass_json

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoadTestType(Enum):
    """Tipos de teste de carga."""
    STRESS = "stress"
    SPIKE = "spike"
    ENDURANCE = "endurance"
    VOLUME = "volume"
    SCALABILITY = "scalability"
    BREAKPOINT = "breakpoint"
    SOAK = "soak"
    BURST = "burst"

class LoadPattern(Enum):
    """Padrões de carga."""
    CONSTANT = "constant"
    RAMP_UP = "ramp_up"
    RAMP_DOWN = "ramp_down"
    STEP = "step"
    SPIKE = "spike"
    RANDOM = "random"
    SINUSOIDAL = "sinusoidal"

class TestStatus(Enum):
    """Status do teste."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass_json
@dataclass
class LoadTestConfig:
    """Configuração de teste de carga."""
    # Configurações básicas
    test_type: LoadTestType
    load_pattern: LoadPattern
    duration: int = 300  # segundos
    timeout: int = 600  # segundos
    
    # Configurações de usuários
    initial_users: int = 10
    max_users: int = 1000
    ramp_up_time: int = 60  # segundos
    ramp_down_time: int = 60  # segundos
    
    # Configurações de requisições
    requests_per_second: int = 100
    concurrent_requests: int = 50
    think_time: float = 1.0  # segundos
    
    # Configurações de endpoints
    base_url: str = "http://localhost:8000"
    endpoints: List[str] = field(default_factory=lambda: ["/api/v1/keywords", "/api/v1/analytics"])
    
    # Configurações de dados
    test_data: Dict[str, Any] = field(default_factory=dict)
    data_variation: bool = True
    
    # Configurações de monitoramento
    monitoring_enabled: bool = True
    metrics_collection: bool = True
    real_time_monitoring: bool = True
    
    # Configurações de thresholds
    response_time_threshold: int = 2000  # ms
    error_rate_threshold: float = 0.05  # 5%
    throughput_threshold: int = 100  # req/string_data
    
    # Configurações de auto-scaling
    auto_scaling_enabled: bool = True
    scaling_threshold: float = 0.8  # 80%
    scaling_cooldown: int = 300  # segundos
    
    # Configurações de reporting
    report_enabled: bool = True
    report_format: str = "json"  # json, yaml, html
    report_path: str = "load_test_reports"
    generate_charts: bool = True

@dataclass_json
@dataclass
class LoadTestResult:
    """Resultado de teste de carga."""
    test_id: str
    test_type: LoadTestType
    load_pattern: LoadPattern
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    status: TestStatus = TestStatus.PENDING
    success: Optional[bool] = None
    error_message: Optional[str] = None
    
    # Métricas de performance
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    avg_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    p50_response_time: float = 0.0
    p90_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    
    # Métricas de throughput
    requests_per_second: float = 0.0
    peak_rps: float = 0.0
    avg_rps: float = 0.0
    
    # Métricas de erro
    error_rate: float = 0.0
    error_types: Dict[str, int] = field(default_factory=dict)
    
    # Métricas de sistema
    cpu_usage: List[float] = field(default_factory=list)
    memory_usage: List[float] = field(default_factory=list)
    network_io: List[Dict[str, float]] = field(default_factory=list)
    
    # Métricas de auto-scaling
    scaling_events: List[Dict[str, Any]] = field(default_factory=list)
    scaling_success_rate: float = 0.0
    
    # Detalhes do teste
    concurrent_users: List[int] = field(default_factory=list)
    response_times: List[float] = field(default_factory=list)
    throughput_history: List[float] = field(default_factory=list)
    
    # Logs e eventos
    events: List[Dict[str, Any]] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)

class LoadGenerator:
    """Gerador de carga para testes."""
    
    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.session = None
        self.running = False
        self.current_users = 0
        self.request_count = 0
        self.response_times = []
        self.errors = defaultdict(int)
        self.start_time = None
        
    async def start_session(self):
        """Inicia sessão HTTP."""
        connector = aiohttp.TCPConnector(limit=1000, limit_per_host=100)
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
    
    async def close_session(self):
        """Fecha sessão HTTP."""
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, data: Dict[str, Any] = None) -> Tuple[bool, float, str]:
        """Faz uma requisição HTTP."""
        if not self.session:
            return False, 0.0, "Session not initialized"
        
        url = f"{self.config.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if data:
                async with self.session.post(url, json=data) as response:
                    response_time = (time.time() - start_time) * 1000  # ms
                    return response.status < 400, response_time, str(response.status)
            else:
                async with self.session.get(url) as response:
                    response_time = (time.time() - start_time) * 1000  # ms
                    return response.status < 400, response_time, str(response.status)
                    
        except Exception as e:
            response_time = (time.time() - start_time) * 1000  # ms
            return False, response_time, str(e)
    
    def generate_test_data(self) -> Dict[str, Any]:
        """Gera dados de teste."""
        if not self.config.data_variation:
            return self.config.test_data
        
        # Varia dados para simular cenários reais
        base_data = self.config.test_data.copy()
        
        # Adiciona variações
        if 'keywords' in base_data:
            base_data['keywords'] = f"test_keyword_{random.randint(1, 1000)}"
        
        if 'user_id' in base_data:
            base_data['user_id'] = f"user_{random.randint(1, 10000)}"
        
        return base_data

class LoadPatternGenerator:
    """Gerador de padrões de carga."""
    
    def __init__(self, config: LoadTestConfig):
        self.config = config
    
    def get_user_count(self, elapsed_time: float) -> int:
        """Calcula número de usuários baseado no padrão de carga."""
        pattern = self.config.load_pattern
        
        if pattern == LoadPattern.CONSTANT:
            return self.config.max_users
        
        elif pattern == LoadPattern.RAMP_UP:
            if elapsed_time <= self.config.ramp_up_time:
                progress = elapsed_time / self.config.ramp_up_time
                return int(self.config.initial_users + (self.config.max_users - self.config.initial_users) * progress)
            return self.config.max_users
        
        elif pattern == LoadPattern.RAMP_DOWN:
            if elapsed_time >= (self.config.duration - self.config.ramp_down_time):
                remaining_time = self.config.duration - elapsed_time
                progress = remaining_time / self.config.ramp_down_time
                return int(self.config.initial_users + (self.config.max_users - self.config.initial_users) * progress)
            return self.config.max_users
        
        elif pattern == LoadPattern.STEP:
            step_size = self.config.duration / 5
            step = int(elapsed_time / step_size)
            return min(self.config.initial_users + step * 200, self.config.max_users)
        
        elif pattern == LoadPattern.SPIKE:
            # Simula picos de carga
            spike_time = self.config.duration / 2
            if abs(elapsed_time - spike_time) < 30:
                return int(self.config.max_users * 1.5)
            return self.config.max_users
        
        elif pattern == LoadPattern.RANDOM:
            return random.randint(self.config.initial_users, self.config.max_users)
        
        elif pattern == LoadPattern.SINUSOIDAL:
            # Padrão sinusoidal
            progress = elapsed_time / self.config.duration
            sine_value = np.sin(progress * 2 * np.pi)
            return int(self.config.initial_users + (self.config.max_users - self.config.initial_users) * (0.5 + 0.5 * sine_value))
        
        return self.config.initial_users

class MetricsCollector:
    """Coletor de métricas durante testes de carga."""
    
    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.metrics_history = deque(maxlen=10000)
    
    def collect_system_metrics(self) -> Dict[str, float]:
        """Coleta métricas do sistema."""
        try:
            return {
                'timestamp': time.time(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'network_sent': psutil.net_io_counters().bytes_sent,
                'network_recv': psutil.net_io_counters().bytes_recv
            }
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {}
    
    def collect_application_metrics(self, response_times: List[float], errors: Dict[str, int]) -> Dict[str, Any]:
        """Coleta métricas da aplicação."""
        if not response_times:
            return {}
        
        return {
            'timestamp': time.time(),
            'avg_response_time': statistics.mean(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'p50_response_time': statistics.quantiles(response_times, n=2)[0] if len(response_times) > 1 else response_times[0],
            'p90_response_time': statistics.quantiles(response_times, n=10)[8] if len(response_times) > 9 else response_times[-1],
            'p95_response_time': statistics.quantiles(response_times, n=20)[18] if len(response_times) > 19 else response_times[-1],
            'p99_response_time': statistics.quantiles(response_times, n=100)[98] if len(response_times) > 99 else response_times[-1],
            'total_requests': len(response_times),
            'error_count': sum(errors.values()),
            'error_rate': sum(errors.values()) / len(response_times) if response_times else 0
        }

class AutoScalingValidator:
    """Validador de auto-scaling."""
    
    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.scaling_events = []
        self.last_scaling_check = 0
    
    def check_scaling_needed(self, metrics: Dict[str, Any]) -> bool:
        """Verifica se auto-scaling é necessário."""
        if not self.config.auto_scaling_enabled:
            return False
        
        current_time = time.time()
        if current_time - self.last_scaling_check < self.config.scaling_cooldown:
            return False
        
        # Verifica métricas para determinar se scaling é necessário
        cpu_usage = metrics.get('cpu_percent', 0)
        response_time = metrics.get('avg_response_time', 0)
        error_rate = metrics.get('error_rate', 0)
        
        scaling_needed = (
            cpu_usage > (self.config.scaling_threshold * 100) or
            response_time > self.config.response_time_threshold or
            error_rate > self.config.error_rate_threshold
        )
        
        if scaling_needed:
            self.scaling_events.append({
                'timestamp': current_time,
                'trigger': {
                    'cpu_usage': cpu_usage,
                    'response_time': response_time,
                    'error_rate': error_rate
                }
            })
            self.last_scaling_check = current_time
        
        return scaling_needed
    
    def simulate_scaling(self) -> bool:
        """Simula auto-scaling."""
        try:
            # Em produção, chamaria APIs de auto-scaling
            logger.info("Auto-scaling triggered")
            return True
        except Exception as e:
            logger.error(f"Auto-scaling failed: {e}")
            return False

class ReportGenerator:
    """Gerador de relatórios de teste de carga."""
    
    def __init__(self, config: LoadTestConfig):
        self.config = config
        if self.config.report_enabled:
            os.makedirs(self.config.report_path, exist_ok=True)
    
    def generate_report(self, result: LoadTestResult) -> str:
        """Gera relatório completo do teste."""
        if not self.config.report_enabled:
            return ""
        
        report_data = {
            'test_info': {
                'test_id': result.test_id,
                'test_type': result.test_type.value,
                'load_pattern': result.load_pattern.value,
                'start_time': result.start_time.isoformat(),
                'end_time': result.end_time.isoformat() if result.end_time else None,
                'duration': result.duration,
                'success': result.success,
                'status': result.status.value
            },
            'performance_metrics': {
                'total_requests': result.total_requests,
                'successful_requests': result.successful_requests,
                'failed_requests': result.failed_requests,
                'avg_response_time': result.avg_response_time,
                'min_response_time': result.min_response_time,
                'max_response_time': result.max_response_time,
                'p50_response_time': result.p50_response_time,
                'p90_response_time': result.p90_response_time,
                'p95_response_time': result.p95_response_time,
                'p99_response_time': result.p99_response_time,
                'requests_per_second': result.requests_per_second,
                'peak_rps': result.peak_rps,
                'error_rate': result.error_rate
            },
            'system_metrics': {
                'avg_cpu_usage': statistics.mean(result.cpu_usage) if result.cpu_usage else 0,
                'max_cpu_usage': max(result.cpu_usage) if result.cpu_usage else 0,
                'avg_memory_usage': statistics.mean(result.memory_usage) if result.memory_usage else 0,
                'max_memory_usage': max(result.memory_usage) if result.memory_usage else 0
            },
            'scaling_metrics': {
                'scaling_events': result.scaling_events,
                'scaling_success_rate': result.scaling_success_rate
            },
            'thresholds': {
                'response_time_threshold': self.config.response_time_threshold,
                'error_rate_threshold': self.config.error_rate_threshold,
                'throughput_threshold': self.config.throughput_threshold
            },
            'events': result.events
        }
        
        # Salva relatório
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"load_test_{result.test_type.value}_{timestamp}.{self.config.report_format}"
        filepath = os.path.join(self.config.report_path, filename)
        
        with open(filepath, 'w') as f:
            if self.config.report_format == 'json':
                json.dump(report_data, f, indent=2)
            elif self.config.report_format == 'yaml':
                yaml.dump(report_data, f, default_flow_style=False)
        
        # Gera gráficos se habilitado
        if self.config.generate_charts:
            self._generate_charts(result, filepath)
        
        logger.info(f"Load test report saved: {filepath}")
        return filepath
    
    def _generate_charts(self, result: LoadTestResult, report_path: str):
        """Gera gráficos do teste."""
        try:
            # Gráfico de response time
            plt.figure(figsize=(12, 8))
            
            plt.subplot(2, 2, 1)
            plt.plot(result.response_times)
            plt.title('Response Time Over Time')
            plt.xlabel('Request Number')
            plt.ylabel('Response Time (ms)')
            plt.grid(True)
            
            # Gráfico de throughput
            plt.subplot(2, 2, 2)
            plt.plot(result.throughput_history)
            plt.title('Throughput Over Time')
            plt.xlabel('Time')
            plt.ylabel('Requests per Second')
            plt.grid(True)
            
            # Gráfico de CPU
            plt.subplot(2, 2, 3)
            plt.plot(result.cpu_usage)
            plt.title('CPU Usage Over Time')
            plt.xlabel('Time')
            plt.ylabel('CPU Usage (%)')
            plt.grid(True)
            
            # Gráfico de usuários concorrentes
            plt.subplot(2, 2, 4)
            plt.plot(result.concurrent_users)
            plt.title('Concurrent Users Over Time')
            plt.xlabel('Time')
            plt.ylabel('Number of Users')
            plt.grid(True)
            
            plt.tight_layout()
            
            # Salva gráfico
            chart_path = report_path.replace(f'.{self.config.report_format}', '_charts.png')
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Load test charts saved: {chart_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate charts: {e}")

class AdvancedLoadTesting:
    """
    Sistema avançado de testes de carga com funcionalidades enterprise-grade.
    
    Implementa:
    - Múltiplos tipos de teste de carga
    - Padrões de carga realistas
    - Validação de auto-scaling
    - Coleta de métricas detalhadas
    - Relatórios e gráficos
    """
    
    def __init__(self, config: LoadTestConfig):
        """
        Inicializar sistema de testes de carga.
        
        Args:
            config: Configuração do teste
        """
        self.config = config
        
        # Inicializar componentes
        self.load_generator = LoadGenerator(config)
        self.pattern_generator = LoadPatternGenerator(config)
        self.metrics_collector = MetricsCollector(config)
        self.scaling_validator = AutoScalingValidator(config)
        self.report_generator = ReportGenerator(config)
        
        # Estado do teste
        self.current_test: Optional[LoadTestResult] = None
        self.test_history: List[LoadTestResult] = []
        
        # Threading
        self.lock = threading.RLock()
        self.running = False
        
        # Métricas em tempo real
        self.real_time_metrics = deque(maxlen=1000)
        
        logger.info({
            "event": "advanced_load_testing_initialized",
            "status": "success",
            "source": "AdvancedLoadTesting.__init__",
            "details": {
                "test_type": config.test_type.value,
                "load_pattern": config.load_pattern.value,
                "duration": config.duration,
                "max_users": config.max_users
            }
        })
    
    async def run_load_test(self) -> LoadTestResult:
        """
        Executa teste de carga.
        
        Returns:
            Resultado do teste
        """
        with self.lock:
            if self.running:
                raise Exception("Load test already running")
            
            self.running = True
            self.current_test = LoadTestResult(
                test_id=f"load_test_{int(time.time())}",
                test_type=self.config.test_type,
                load_pattern=self.config.load_pattern,
                start_time=datetime.now()
            )
        
        try:
            logger.info(f"Starting load test: {self.config.test_type.value}")
            
            # Inicializa sessão HTTP
            await self.load_generator.start_session()
            
            # Executa teste baseado no tipo
            if self.config.test_type == LoadTestType.STRESS:
                await self._run_stress_test()
            elif self.config.test_type == LoadTestType.SPIKE:
                await self._run_spike_test()
            elif self.config.test_type == LoadTestType.ENDURANCE:
                await self._run_endurance_test()
            elif self.config.test_type == LoadTestType.VOLUME:
                await self._run_volume_test()
            elif self.config.test_type == LoadTestType.SCALABILITY:
                await self._run_scalability_test()
            elif self.config.test_type == LoadTestType.BREAKPOINT:
                await self._run_breakpoint_test()
            elif self.config.test_type == LoadTestType.SOAK:
                await self._run_soak_test()
            elif self.config.test_type == LoadTestType.BURST:
                await self._run_burst_test()
            else:
                raise ValueError(f"Unknown load test type: {self.config.test_type}")
            
            # Finaliza teste
            self.current_test.end_time = datetime.now()
            self.current_test.duration = (self.current_test.end_time - self.current_test.start_time).total_seconds()
            self.current_test.status = TestStatus.COMPLETED
            self.current_test.success = True
            
            # Calcula métricas finais
            self._calculate_final_metrics()
            
            # Gera relatório
            if self.config.report_enabled:
                self.report_generator.generate_report(self.current_test)
            
            logger.info(f"Load test completed successfully: {self.config.test_type.value}")
            
        except Exception as e:
            logger.error(f"Load test failed: {e}")
            self.current_test.status = TestStatus.FAILED
            self.current_test.success = False
            self.current_test.error_message = str(e)
            
        finally:
            # Fecha sessão HTTP
            await self.load_generator.close_session()
            
            with self.lock:
                self.running = False
                if self.current_test:
                    self.test_history.append(self.current_test)
        
        return self.current_test
    
    async def _run_stress_test(self):
        """Executa teste de stress."""
        logger.info("Running stress test")
        
        start_time = time.time()
        tasks = []
        
        while time.time() - start_time < self.config.duration and self.running:
            elapsed_time = time.time() - start_time
            current_users = self.pattern_generator.get_user_count(elapsed_time)
            
            # Cria tarefas para usuários concorrentes
            for _ in range(current_users):
                task = asyncio.create_task(self._user_workload())
                tasks.append(task)
            
            # Aguarda um pouco antes da próxima iteração
            await asyncio.sleep(1)
        
        # Aguarda todas as tarefas terminarem
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _run_spike_test(self):
        """Executa teste de spike."""
        logger.info("Running spike test")
        
        # Fase 1: Carga normal
        await self._run_phase(60, self.config.initial_users, "normal_load")
        
        # Fase 2: Spike de carga
        await self._run_phase(30, self.config.max_users * 2, "spike_load")
        
        # Fase 3: Retorno à carga normal
        await self._run_phase(60, self.config.initial_users, "recovery")
    
    async def _run_endurance_test(self):
        """Executa teste de endurance."""
        logger.info("Running endurance test")
        
        start_time = time.time()
        tasks = []
        
        while time.time() - start_time < self.config.duration and self.running:
            # Mantém carga constante por longo período
            for _ in range(self.config.max_users):
                task = asyncio.create_task(self._user_workload())
                tasks.append(task)
            
            await asyncio.sleep(10)  # Verifica a cada 10 segundos
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _run_volume_test(self):
        """Executa teste de volume."""
        logger.info("Running volume test")
        
        # Aumenta volume gradualmente
        for volume in range(self.config.initial_users, self.config.max_users, 100):
            await self._run_phase(30, volume, f"volume_{volume}")
    
    async def _run_scalability_test(self):
        """Executa teste de escalabilidade."""
        logger.info("Running scalability test")
        
        # Testa diferentes níveis de carga para validar auto-scaling
        for load_level in [10, 50, 100, 200, 500, 1000]:
            await self._run_phase(60, load_level, f"scalability_{load_level}")
    
    async def _run_breakpoint_test(self):
        """Executa teste de breakpoint."""
        logger.info("Running breakpoint test")
        
        # Aumenta carga até encontrar o ponto de quebra
        load_level = self.config.initial_users
        
        while load_level <= self.config.max_users and self.running:
            await self._run_phase(30, load_level, f"breakpoint_{load_level}")
            
            # Verifica se sistema quebrou
            if self.current_test.error_rate > 0.1:  # 10% de erro
                logger.info(f"Breakpoint found at {load_level} users")
                break
            
            load_level *= 2
    
    async def _run_soak_test(self):
        """Executa teste de soak."""
        logger.info("Running soak test")
        
        # Mantém carga moderada por muito tempo
        await self._run_phase(self.config.duration, self.config.max_users // 2, "soak")
    
    async def _run_burst_test(self):
        """Executa teste de burst."""
        logger.info("Running burst test")
        
        # Bursts curtos de alta carga
        for _ in range(10):
            await self._run_phase(5, self.config.max_users, "burst")
            await asyncio.sleep(10)  # Pausa entre bursts
    
    async def _run_phase(self, duration: int, users: int, phase_name: str):
        """Executa uma fase do teste."""
        start_time = time.time()
        tasks = []
        
        while time.time() - start_time < duration and self.running:
            # Cria tarefas para usuários
            for _ in range(users):
                task = asyncio.create_task(self._user_workload())
                tasks.append(task)
            
            await asyncio.sleep(1)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _user_workload(self):
        """Simula workload de um usuário."""
        while self.running:
            try:
                # Seleciona endpoint aleatório
                endpoint = random.choice(self.config.endpoints)
                
                # Gera dados de teste
                test_data = self.load_generator.generate_test_data()
                
                # Faz requisição
                success, response_time, status = await self.load_generator.make_request(endpoint, test_data)
                
                # Atualiza métricas
                with self.lock:
                    self.current_test.total_requests += 1
                    self.current_test.response_times.append(response_time)
                    
                    if success:
                        self.current_test.successful_requests += 1
                    else:
                        self.current_test.failed_requests += 1
                        self.current_test.error_types[status] += 1
                    
                    # Atualiza métricas de response time
                    self.current_test.total_response_time += response_time
                    self.current_test.min_response_time = min(self.current_test.min_response_time, response_time)
                    self.current_test.max_response_time = max(self.current_test.max_response_time, response_time)
                
                # Think time
                await asyncio.sleep(self.config.think_time)
                
            except Exception as e:
                logger.error(f"User workload error: {e}")
                break
    
    def _calculate_final_metrics(self):
        """Calcula métricas finais do teste."""
        if not self.current_test.response_times:
            return
        
        # Calcula percentis
        sorted_times = sorted(self.current_test.response_times)
        self.current_test.p50_response_time = statistics.quantiles(sorted_times, n=2)[0]
        self.current_test.p90_response_time = statistics.quantiles(sorted_times, n=10)[8]
        self.current_test.p95_response_time = statistics.quantiles(sorted_times, n=20)[18]
        self.current_test.p99_response_time = statistics.quantiles(sorted_times, n=100)[98]
        
        # Calcula métricas finais
        self.current_test.avg_response_time = statistics.mean(sorted_times)
        self.current_test.requests_per_second = self.current_test.total_requests / self.current_test.duration
        self.current_test.error_rate = self.current_test.failed_requests / self.current_test.total_requests
        
        # Calcula peak RPS
        if self.current_test.throughput_history:
            self.current_test.peak_rps = max(self.current_test.throughput_history)
    
    def get_test_history(self) -> List[LoadTestResult]:
        """Obtém histórico de testes."""
        return self.test_history.copy()
    
    def get_current_test(self) -> Optional[LoadTestResult]:
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
                self.current_test.status = TestStatus.CANCELLED
                logger.info("Load test stopped")

def create_load_test(config: LoadTestConfig) -> AdvancedLoadTesting:
    """
    Cria e retorna teste de carga.
    
    Args:
        config: Configuração do teste
        
    Returns:
        Teste de carga configurado
    """
    return AdvancedLoadTesting(config)

def load_load_scenarios(filepath: str) -> List[LoadTestConfig]:
    """
    Carrega cenários de carga de arquivo YAML.
    
    Args:
        filepath: Caminho do arquivo YAML
        
    Returns:
        Lista de configurações de cenários
    """
    with open(filepath, 'r') as f:
        scenarios_data = yaml.safe_load(f)
    
    scenarios = []
    for scenario_data in scenarios_data.get('scenarios', []):
        config = LoadTestConfig(
            test_type=LoadTestType(scenario_data['test_type']),
            load_pattern=LoadPattern(scenario_data['load_pattern']),
            duration=scenario_data.get('duration', 300),
            max_users=scenario_data.get('max_users', 1000),
            requests_per_second=scenario_data.get('requests_per_second', 100)
        )
        scenarios.append(config)
    
    return scenarios

async def run_load_test_suite(scenarios: List[LoadTestConfig]) -> List[LoadTestResult]:
    """
    Executa suite de testes de carga.
    
    Args:
        scenarios: Lista de cenários para executar
        
    Returns:
        Lista de resultados dos testes
    """
    results = []
    
    for scenario in scenarios:
        try:
            load_test = create_load_test(scenario)
            result = await load_test.run_load_test()
            results.append(result)
            
            # Aguarda entre testes
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"Failed to run load test for scenario {scenario.test_type.value}: {e}")
    
    return results 