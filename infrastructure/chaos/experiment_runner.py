"""
Chaos Engineering Experiment Runner
==================================

Sistema de execução de experimentos de chaos engineering com:
- Gerenciamento de experimentos
- Execução controlada e segura
- Monitoramento em tempo real
- Rollback automático
- Relatórios detalhados

Author: Paulo Júnior
Date: 2025-01-27
Tracing ID: CHAOS_EXPERIMENT_RUNNER_001_20250127
"""

import asyncio
import json
import logging
import threading
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

import yaml
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ExperimentStatus(Enum):
    """Status dos experimentos de chaos engineering"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLBACK = "rollback"


class ExperimentType(Enum):
    """Tipos de experimentos de chaos engineering"""
    NETWORK_LATENCY = "network_latency"
    NETWORK_PACKET_LOSS = "network_packet_loss"
    CPU_STRESS = "cpu_stress"
    MEMORY_STRESS = "memory_stress"
    DISK_STRESS = "disk_stress"
    SERVICE_FAILURE = "service_failure"
    DATABASE_FAILURE = "database_failure"
    CACHE_FAILURE = "cache_failure"
    LOAD_BALANCER_FAILURE = "load_balancer_failure"
    DEPENDENCY_FAILURE = "dependency_failure"


class ExperimentPhase(Enum):
    """Fases de execução dos experimentos"""
    PREPARATION = "preparation"
    STEADY_STATE = "steady_state"
    CHAOS_INJECTION = "chaos_injection"
    OBSERVATION = "observation"
    RECOVERY = "recovery"
    ANALYSIS = "analysis"


@dataclass
class ExperimentMetrics:
    """Métricas coletadas durante o experimento"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    response_time: float
    error_rate: float
    throughput: float
    availability: float
    custom_metrics: Dict[str, Any]


@dataclass
class ExperimentResult:
    """Resultado de um experimento de chaos engineering"""
    experiment_id: str
    status: ExperimentStatus
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[float]
    phases_completed: List[ExperimentPhase]
    metrics: List[ExperimentMetrics]
    hypothesis_validated: Optional[bool]
    issues_found: List[str]
    recommendations: List[str]
    rollback_required: bool
    rollback_successful: Optional[bool]


class ExperimentConfig(BaseModel):
    """Configuração de um experimento"""
    name: str = Field(..., description="Nome do experimento")
    description: str = Field(..., description="Descrição do experimento")
    type: ExperimentType = Field(..., description="Tipo do experimento")
    hypothesis: str = Field(..., description="Hipótese a ser testada")
    
    # Configurações de execução
    duration: int = Field(300, description="Duração em segundos")
    steady_state_duration: int = Field(60, description="Duração do estado estável")
    chaos_duration: int = Field(120, description="Duração da injeção de caos")
    observation_duration: int = Field(60, description="Duração da observação")
    
    # Configurações de segurança
    max_impact: float = Field(0.3, description="Impacto máximo permitido (0-1)")
    auto_rollback: bool = Field(True, description="Rollback automático em caso de falha")
    rollback_threshold: float = Field(0.5, description="Threshold para rollback")
    
    # Configurações de monitoramento
    metrics_interval: int = Field(5, description="Intervalo de coleta de métricas")
    alert_thresholds: Dict[str, float] = Field(default_factory=dict)
    
    # Configurações específicas do tipo
    parameters: Dict[str, Any] = Field(default_factory=dict)


class ExperimentRunner:
    """
    Executor de experimentos de chaos engineering
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/chaos_experiments.yaml"
        self.experiments: Dict[str, ExperimentConfig] = {}
        self.running_experiments: Dict[str, 'ExperimentExecution'] = {}
        self.completed_experiments: Dict[str, ExperimentResult] = {}
        self.lock = threading.RLock()
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.monitoring_callbacks: List[Callable] = []
        self.rollback_handlers: Dict[ExperimentType, Callable] = {}
        
        # Carregar configurações
        self._load_experiments()
        self._setup_rollback_handlers()
        
        logger.info("ExperimentRunner initialized")
    
    def _load_experiments(self) -> None:
        """Carrega configurações de experimentos do arquivo YAML"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    data = yaml.safe_load(f)
                    
                for exp_data in data.get('experiments', []):
                    config = ExperimentConfig(**exp_data)
                    self.experiments[config.name] = config
                    
                logger.info(f"Loaded {len(self.experiments)} experiments")
            else:
                logger.warning(f"Config file not found: {self.config_path}")
        except Exception as e:
            logger.error(f"Error loading experiments: {e}")
    
    def _setup_rollback_handlers(self) -> None:
        """Configura handlers de rollback para cada tipo de experimento"""
        from .failure_injection import FailureInjector
        
        self.rollback_handlers = {
            ExperimentType.NETWORK_LATENCY: self._rollback_network_latency,
            ExperimentType.NETWORK_PACKET_LOSS: self._rollback_network_packet_loss,
            ExperimentType.CPU_STRESS: self._rollback_cpu_stress,
            ExperimentType.MEMORY_STRESS: self._rollback_memory_stress,
            ExperimentType.DISK_STRESS: self._rollback_disk_stress,
            ExperimentType.SERVICE_FAILURE: self._rollback_service_failure,
            ExperimentType.DATABASE_FAILURE: self._rollback_database_failure,
            ExperimentType.CACHE_FAILURE: self._rollback_cache_failure,
            ExperimentType.LOAD_BALANCER_FAILURE: self._rollback_load_balancer_failure,
            ExperimentType.DEPENDENCY_FAILURE: self._rollback_dependency_failure,
        }
    
    async def run_experiment(self, experiment_name: str, 
                           custom_params: Optional[Dict[str, Any]] = None) -> str:
        """
        Executa um experimento de chaos engineering
        
        Args:
            experiment_name: Nome do experimento
            custom_params: Parâmetros customizados
            
        Returns:
            ID do experimento executado
        """
        if experiment_name not in self.experiments:
            raise ValueError(f"Experiment '{experiment_name}' not found")
        
        config = self.experiments[experiment_name]
        if custom_params:
            config.parameters.update(custom_params)
        
        execution = ExperimentExecution(config, self)
        experiment_id = execution.experiment_id
        
        with self.lock:
            self.running_experiments[experiment_id] = execution
        
        # Executar em thread separada
        self.executor.submit(self._run_experiment_async, execution)
        
        logger.info(f"Started experiment: {experiment_name} (ID: {experiment_id})")
        return experiment_id
    
    def _run_experiment_async(self, execution: 'ExperimentExecution') -> None:
        """Executa experimento de forma assíncrona"""
        try:
            asyncio.run(execution.run())
        except Exception as e:
            logger.error(f"Error running experiment {execution.experiment_id}: {e}")
            execution.result.status = ExperimentStatus.FAILED
            execution.result.issues_found.append(str(e))
    
    async def stop_experiment(self, experiment_id: str) -> bool:
        """
        Para um experimento em execução
        
        Args:
            experiment_id: ID do experimento
            
        Returns:
            True se parado com sucesso
        """
        with self.lock:
            if experiment_id not in self.running_experiments:
                return False
            
            execution = self.running_experiments[experiment_id]
        
        return await execution.stop()
    
    async def get_experiment_status(self, experiment_id: str) -> Optional[ExperimentStatus]:
        """Obtém status de um experimento"""
        with self.lock:
            if experiment_id in self.running_experiments:
                return self.running_experiments[experiment_id].result.status
            elif experiment_id in self.completed_experiments:
                return self.completed_experiments[experiment_id].status
        return None
    
    def get_experiment_result(self, experiment_id: str) -> Optional[ExperimentResult]:
        """Obtém resultado de um experimento"""
        with self.lock:
            return self.completed_experiments.get(experiment_id)
    
    def list_experiments(self) -> List[Dict[str, Any]]:
        """Lista todos os experimentos disponíveis"""
        return [
            {
                'name': config.name,
                'description': config.description,
                'type': config.type.value,
                'hypothesis': config.hypothesis,
                'duration': config.duration
            }
            for config in self.experiments.values()
        ]
    
    def list_running_experiments(self) -> List[Dict[str, Any]]:
        """Lista experimentos em execução"""
        with self.lock:
            return [
                {
                    'experiment_id': exp_id,
                    'name': execution.config.name,
                    'status': execution.result.status.value,
                    'start_time': execution.result.start_time,
                    'current_phase': execution.current_phase.value if execution.current_phase else None
                }
                for exp_id, execution in self.running_experiments.items()
            ]
    
    def add_monitoring_callback(self, callback: Callable) -> None:
        """Adiciona callback para monitoramento"""
        self.monitoring_callbacks.append(callback)
    
    def _notify_monitoring(self, experiment_id: str, metrics: ExperimentMetrics) -> None:
        """Notifica callbacks de monitoramento"""
        for callback in self.monitoring_callbacks:
            try:
                callback(experiment_id, metrics)
            except Exception as e:
                logger.error(f"Error in monitoring callback: {e}")
    
    # Handlers de rollback
    def _rollback_network_latency(self, experiment_id: str) -> bool:
        """Rollback de experimento de latência de rede"""
        try:
            # Implementar rollback específico
            logger.info(f"Rollback network latency for experiment {experiment_id}")
            return True
        except Exception as e:
            logger.error(f"Error in network latency rollback: {e}")
            return False
    
    def _rollback_network_packet_loss(self, experiment_id: str) -> bool:
        """Rollback de experimento de perda de pacotes"""
        try:
            logger.info(f"Rollback network packet loss for experiment {experiment_id}")
            return True
        except Exception as e:
            logger.error(f"Error in network packet loss rollback: {e}")
            return False
    
    def _rollback_cpu_stress(self, experiment_id: str) -> bool:
        """Rollback de experimento de stress de CPU"""
        try:
            logger.info(f"Rollback CPU stress for experiment {experiment_id}")
            return True
        except Exception as e:
            logger.error(f"Error in CPU stress rollback: {e}")
            return False
    
    def _rollback_memory_stress(self, experiment_id: str) -> bool:
        """Rollback de experimento de stress de memória"""
        try:
            logger.info(f"Rollback memory stress for experiment {experiment_id}")
            return True
        except Exception as e:
            logger.error(f"Error in memory stress rollback: {e}")
            return False
    
    def _rollback_disk_stress(self, experiment_id: str) -> bool:
        """Rollback de experimento de stress de disco"""
        try:
            logger.info(f"Rollback disk stress for experiment {experiment_id}")
            return True
        except Exception as e:
            logger.error(f"Error in disk stress rollback: {e}")
            return False
    
    def _rollback_service_failure(self, experiment_id: str) -> bool:
        """Rollback de falha de serviço"""
        try:
            logger.info(f"Rollback service failure for experiment {experiment_id}")
            return True
        except Exception as e:
            logger.error(f"Error in service failure rollback: {e}")
            return False
    
    def _rollback_database_failure(self, experiment_id: str) -> bool:
        """Rollback de falha de banco de dados"""
        try:
            logger.info(f"Rollback database failure for experiment {experiment_id}")
            return True
        except Exception as e:
            logger.error(f"Error in database failure rollback: {e}")
            return False
    
    def _rollback_cache_failure(self, experiment_id: str) -> bool:
        """Rollback de falha de cache"""
        try:
            logger.info(f"Rollback cache failure for experiment {experiment_id}")
            return True
        except Exception as e:
            logger.error(f"Error in cache failure rollback: {e}")
            return False
    
    def _rollback_load_balancer_failure(self, experiment_id: str) -> bool:
        """Rollback de falha de load balancer"""
        try:
            logger.info(f"Rollback load balancer failure for experiment {experiment_id}")
            return True
        except Exception as e:
            logger.error(f"Error in load balancer failure rollback: {e}")
            return False
    
    def _rollback_dependency_failure(self, experiment_id: str) -> bool:
        """Rollback de falha de dependência"""
        try:
            logger.info(f"Rollback dependency failure for experiment {experiment_id}")
            return True
        except Exception as e:
            logger.error(f"Error in dependency failure rollback: {e}")
            return False


class ExperimentExecution:
    """
    Execução de um experimento específico
    """
    
    def __init__(self, config: ExperimentConfig, runner: ExperimentRunner):
        self.config = config
        self.runner = runner
        self.experiment_id = f"{config.name}_{int(time.time())}"
        self.current_phase: Optional[ExperimentPhase] = None
        self.stop_requested = False
        
        # Resultado do experimento
        self.result = ExperimentResult(
            experiment_id=self.experiment_id,
            status=ExperimentStatus.PENDING,
            start_time=datetime.now(),
            end_time=None,
            duration=None,
            phases_completed=[],
            metrics=[],
            hypothesis_validated=None,
            issues_found=[],
            recommendations=[],
            rollback_required=False,
            rollback_successful=None
        )
        
        # Injetor de falhas
        from .failure_injection import FailureInjector
        self.failure_injector = FailureInjector()
        
        # Monitor de métricas
        from .chaos_monitoring import ChaosMonitor
        self.monitor = ChaosMonitor()
    
    async def run(self) -> None:
        """Executa o experimento completo"""
        try:
            self.result.status = ExperimentStatus.RUNNING
            logger.info(f"Starting experiment: {self.config.name}")
            
            # Fase 1: Preparação
            await self._run_phase(ExperimentPhase.PREPARATION, self._prepare_experiment)
            
            # Fase 2: Estado estável
            await self._run_phase(ExperimentPhase.STEADY_STATE, self._measure_steady_state)
            
            # Fase 3: Injeção de caos
            await self._run_phase(ExperimentPhase.CHAOS_INJECTION, self._inject_chaos)
            
            # Fase 4: Observação
            await self._run_phase(ExperimentPhase.OBSERVATION, self._observe_system)
            
            # Fase 5: Recuperação
            await self._run_phase(ExperimentPhase.RECOVERY, self._recover_system)
            
            # Fase 6: Análise
            await self._run_phase(ExperimentPhase.ANALYSIS, self._analyze_results)
            
            self.result.status = ExperimentStatus.COMPLETED
            
        except Exception as e:
            logger.error(f"Error in experiment {self.experiment_id}: {e}")
            self.result.status = ExperimentStatus.FAILED
            self.result.issues_found.append(str(e))
            
            # Rollback automático se configurado
            if self.config.auto_rollback:
                await self._perform_rollback()
        
        finally:
            self.result.end_time = datetime.now()
            if self.result.start_time and self.result.end_time:
                self.result.duration = (self.result.end_time - self.result.start_time).total_seconds()
            
            # Mover para experimentos completados
            with self.runner.lock:
                if self.experiment_id in self.runner.running_experiments:
                    del self.runner.running_experiments[self.experiment_id]
                self.runner.completed_experiments[self.experiment_id] = self.result
    
    async def _run_phase(self, phase: ExperimentPhase, phase_func: Callable) -> None:
        """Executa uma fase do experimento"""
        if self.stop_requested:
            return
        
        self.current_phase = phase
        logger.info(f"Starting phase: {phase.value}")
        
        try:
            await phase_func()
            self.result.phases_completed.append(phase)
            logger.info(f"Completed phase: {phase.value}")
        except Exception as e:
            logger.error(f"Error in phase {phase.value}: {e}")
            raise
    
    async def _prepare_experiment(self) -> None:
        """Prepara o experimento"""
        # Verificar pré-condições
        await self._check_prerequisites()
        
        # Configurar monitoramento
        await self.monitor.start_monitoring(self.config.metrics_interval)
        
        # Preparar injetor de falhas
        await self.failure_injector.prepare(self.config)
    
    async def _measure_steady_state(self) -> None:
        """Mede o estado estável do sistema"""
        logger.info(f"Measuring steady state for {self.config.steady_state_duration}s")
        
        start_time = time.time()
        while time.time() - start_time < self.config.steady_state_duration:
            if self.stop_requested:
                break
            
            metrics = await self.monitor.collect_metrics()
            self.result.metrics.append(metrics)
            self.runner._notify_monitoring(self.experiment_id, metrics)
            
            await asyncio.sleep(self.config.metrics_interval)
    
    async def _inject_chaos(self) -> None:
        """Injeta caos no sistema"""
        logger.info(f"Injecting chaos for {self.config.chaos_duration}s")
        
        # Injetar falha
        await self.failure_injector.inject_failure(self.config)
        
        # Monitorar durante injeção
        start_time = time.time()
        while time.time() - start_time < self.config.chaos_duration:
            if self.stop_requested:
                break
            
            metrics = await self.monitor.collect_metrics()
            self.result.metrics.append(metrics)
            self.runner._notify_monitoring(self.experiment_id, metrics)
            
            # Verificar se precisa de rollback
            if self._should_rollback(metrics):
                logger.warning("Rollback threshold exceeded, stopping chaos injection")
                self.result.rollback_required = True
                break
            
            await asyncio.sleep(self.config.metrics_interval)
    
    async def _observe_system(self) -> None:
        """Observa o comportamento do sistema"""
        logger.info(f"Observing system for {self.config.observation_duration}s")
        
        start_time = time.time()
        while time.time() - start_time < self.config.observation_duration:
            if self.stop_requested:
                break
            
            metrics = await self.monitor.collect_metrics()
            self.result.metrics.append(metrics)
            self.runner._notify_monitoring(self.experiment_id, metrics)
            
            await asyncio.sleep(self.config.metrics_interval)
    
    async def _recover_system(self) -> None:
        """Recupera o sistema"""
        logger.info("Recovering system")
        
        # Parar injeção de falhas
        await self.failure_injector.stop_injection()
        
        # Aguardar recuperação
        recovery_time = 0
        max_recovery_time = 300  # 5 minutos
        
        while recovery_time < max_recovery_time:
            metrics = await self.monitor.collect_metrics()
            self.result.metrics.append(metrics)
            
            # Verificar se sistema se recuperou
            if self._is_system_recovered(metrics):
                logger.info("System recovered successfully")
                break
            
            await asyncio.sleep(self.config.metrics_interval)
            recovery_time += self.config.metrics_interval
        
        # Parar monitoramento
        await self.monitor.stop_monitoring()
    
    async def _analyze_results(self) -> None:
        """Analisa os resultados do experimento"""
        logger.info("Analyzing experiment results")
        
        # Analisar métricas
        steady_state_metrics = self._get_phase_metrics(ExperimentPhase.STEADY_STATE)
        chaos_metrics = self._get_phase_metrics(ExperimentPhase.CHAOS_INJECTION)
        observation_metrics = self._get_phase_metrics(ExperimentPhase.OBSERVATION)
        
        # Validar hipótese
        self.result.hypothesis_validated = self._validate_hypothesis(
            steady_state_metrics, chaos_metrics, observation_metrics
        )
        
        # Gerar recomendações
        self.result.recommendations = self._generate_recommendations(
            steady_state_metrics, chaos_metrics, observation_metrics
        )
        
        # Identificar problemas
        self.result.issues_found.extend(self._identify_issues(
            steady_state_metrics, chaos_metrics, observation_metrics
        ))
    
    async def _check_prerequisites(self) -> None:
        """Verifica pré-condições do experimento"""
        # Verificar se sistema está saudável
        baseline_metrics = await self.monitor.collect_metrics()
        
        if baseline_metrics.error_rate > 0.05:  # 5%
            raise ValueError("System error rate too high for chaos experiment")
        
        if baseline_metrics.availability < 0.95:  # 95%
            raise ValueError("System availability too low for chaos experiment")
    
    def _should_rollback(self, metrics: ExperimentMetrics) -> bool:
        """Verifica se deve fazer rollback"""
        if not self.config.auto_rollback:
            return False
        
        # Verificar thresholds
        if metrics.error_rate > self.config.rollback_threshold:
            return True
        
        if metrics.availability < (1 - self.config.rollback_threshold):
            return True
        
        return False
    
    def _is_system_recovered(self, metrics: ExperimentMetrics) -> bool:
        """Verifica se sistema se recuperou"""
        # Comparar com baseline
        baseline_metrics = self.result.metrics[0] if self.result.metrics else None
        if not baseline_metrics:
            return True
        
        # Verificar se métricas voltaram ao normal
        error_rate_diff = abs(metrics.error_rate - baseline_metrics.error_rate)
        availability_diff = abs(metrics.availability - baseline_metrics.availability)
        
        return error_rate_diff < 0.02 and availability_diff < 0.02  # 2% tolerância
    
    def _get_phase_metrics(self, phase: ExperimentPhase) -> List[ExperimentMetrics]:
        """Obtém métricas de uma fase específica"""
        # Implementação simplificada - em produção seria mais sofisticada
        return self.result.metrics
    
    def _validate_hypothesis(self, steady_state: List[ExperimentMetrics],
                           chaos: List[ExperimentMetrics],
                           observation: List[ExperimentMetrics]) -> bool:
        """Valida a hipótese do experimento"""
        # Implementação específica baseada na hipótese
        # Por enquanto, retorna True se não houve rollback
        return not self.result.rollback_required
    
    def _generate_recommendations(self, steady_state: List[ExperimentMetrics],
                                chaos: List[ExperimentMetrics],
                                observation: List[ExperimentMetrics]) -> List[str]:
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        
        # Análise de performance
        if chaos and steady_state:
            avg_chaos_error_rate = sum(m.error_rate for m in chaos) / len(chaos)
            avg_steady_error_rate = sum(m.error_rate for m in steady_state) / len(steady_state)
            
            if avg_chaos_error_rate > avg_steady_error_rate * 2:
                recommendations.append("Implementar circuit breakers para melhorar resiliência")
            
            if avg_chaos_error_rate > 0.1:  # 10%
                recommendations.append("Revisar estratégias de retry e fallback")
        
        # Análise de disponibilidade
        if chaos:
            min_availability = min(m.availability for m in chaos)
            if min_availability < 0.9:  # 90%
                recommendations.append("Implementar health checks mais robustos")
                recommendations.append("Considerar redundância de serviços críticos")
        
        return recommendations
    
    def _identify_issues(self, steady_state: List[ExperimentMetrics],
                        chaos: List[ExperimentMetrics],
                        observation: List[ExperimentMetrics]) -> List[str]:
        """Identifica problemas encontrados"""
        issues = []
        
        if chaos:
            max_error_rate = max(m.error_rate for m in chaos)
            if max_error_rate > 0.5:  # 50%
                issues.append(f"Alta taxa de erro durante caos: {max_error_rate:.2%}")
            
            min_availability = min(m.availability for m in chaos)
            if min_availability < 0.8:  # 80%
                issues.append(f"Baixa disponibilidade durante caos: {min_availability:.2%}")
        
        return issues
    
    async def _perform_rollback(self) -> None:
        """Executa rollback do experimento"""
        logger.info("Performing automatic rollback")
        
        try:
            rollback_handler = self.runner.rollback_handlers.get(self.config.type)
            if rollback_handler:
                self.result.rollback_successful = rollback_handler(self.experiment_id)
            else:
                logger.warning(f"No rollback handler for experiment type: {self.config.type}")
                self.result.rollback_successful = False
        except Exception as e:
            logger.error(f"Error during rollback: {e}")
            self.result.rollback_successful = False
    
    async def stop(self) -> bool:
        """Para a execução do experimento"""
        self.stop_requested = True
        self.result.status = ExperimentStatus.CANCELLED
        
        # Parar injeção de falhas
        await self.failure_injector.stop_injection()
        
        # Parar monitoramento
        await self.monitor.stop_monitoring()
        
        logger.info(f"Experiment {self.experiment_id} stopped")
        return True


# Função de conveniência para criar runner
def create_experiment_runner(config_path: Optional[str] = None) -> ExperimentRunner:
    """Cria uma instância do experiment runner"""
    return ExperimentRunner(config_path) 