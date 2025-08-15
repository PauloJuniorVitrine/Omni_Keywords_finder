"""
Chaos Engineering Injection Strategies
=====================================

Sistema de estratégias de injeção de falhas para chaos engineering com:
- Estratégias de falha de rede
- Estratégias de falha de recursos
- Estratégias de falha de serviços
- Estratégias de falha de dependências
- Parâmetros configuráveis e seguros

Author: Paulo Júnior
Date: 2025-01-27
Tracing ID: CHAOS_INJECTION_STRATEGIES_001_20250127
"""

import asyncio
import logging
import random
import subprocess
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable
from concurrent.futures import ThreadPoolExecutor

import psutil
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class InjectionType(Enum):
    """Tipos de injeção de falhas"""
    NETWORK_LATENCY = "network_latency"
    NETWORK_PACKET_LOSS = "network_packet_loss"
    NETWORK_BANDWIDTH_LIMIT = "network_bandwidth_limit"
    CPU_STRESS = "cpu_stress"
    MEMORY_STRESS = "memory_stress"
    DISK_STRESS = "disk_stress"
    SERVICE_FAILURE = "service_failure"
    DATABASE_FAILURE = "database_failure"
    CACHE_FAILURE = "cache_failure"
    DEPENDENCY_FAILURE = "dependency_failure"
    PROCESS_KILL = "process_kill"
    CONTAINER_FAILURE = "container_failure"


class InjectionMode(Enum):
    """Modos de injeção"""
    CONTINUOUS = "continuous"
    INTERMITTENT = "intermittent"
    RANDOM = "random"
    BURST = "burst"
    GRADUAL = "gradual"


@dataclass
class InjectionResult:
    """Resultado de uma injeção de falha"""
    success: bool
    injection_id: str
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[float]
    error_message: Optional[str]
    impact_metrics: Dict[str, Any]
    recovery_time: Optional[float] = None


class InjectionStrategy(ABC):
    """Classe base para estratégias de injeção"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.injection_id = f"{self.__class__.__name__}_{int(time.time())}"
        self.is_active = False
        self.start_time: Optional[datetime] = None
        self.stop_time: Optional[datetime] = None
        self.lock = threading.RLock()
        
    @abstractmethod
    async def inject(self) -> InjectionResult:
        """Executa a injeção de falha"""
        pass
    
    @abstractmethod
    async def stop(self) -> bool:
        """Para a injeção de falha"""
        pass
    
    @abstractmethod
    def validate_config(self) -> List[str]:
        """Valida a configuração da estratégia"""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Obtém status da injeção"""
        with self.lock:
            return {
                'injection_id': self.injection_id,
                'is_active': self.is_active,
                'start_time': self.start_time,
                'stop_time': self.stop_time,
                'duration': (self.stop_time - self.start_time).total_seconds() if self.stop_time and self.start_time else None
            }


class NetworkLatencyStrategy(InjectionStrategy):
    """Estratégia de injeção de latência de rede"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.latency_ms = config.get('latency_ms', 100)
        self.jitter_ms = config.get('jitter_ms', 10)
        self.target_interface = config.get('target_interface', 'eth0')
        self.tc_process: Optional[subprocess.Popen] = None
    
    async def inject(self) -> InjectionResult:
        """Injeta latência de rede"""
        try:
            with self.lock:
                self.is_active = True
                self.start_time = datetime.now()
            
            # Verificar se tc está disponível
            if not self._check_tc_available():
                raise RuntimeError("tc (traffic control) não está disponível")
            
            # Configurar latência usando tc
            cmd = [
                'tc', 'qdisc', 'add', 'dev', self.target_interface,
                'root', 'netem', 'delay', f'{self.latency_ms}ms', f'{self.jitter_ms}ms'
            ]
            
            self.tc_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            
            # Aguardar um pouco para aplicar
            await asyncio.sleep(1)
            
            if self.tc_process.poll() is not None:
                raise RuntimeError("Falha ao aplicar latência de rede")
            
            logger.info(f"Network latency injected: {self.latency_ms}ms ± {self.jitter_ms}ms")
            
            return InjectionResult(
                success=True,
                injection_id=self.injection_id,
                start_time=self.start_time,
                end_time=None,
                duration=None,
                error_message=None,
                impact_metrics={'latency_ms': self.latency_ms, 'jitter_ms': self.jitter_ms}
            )
            
        except Exception as e:
            logger.error(f"Error injecting network latency: {e}")
            return InjectionResult(
                success=False,
                injection_id=self.injection_id,
                start_time=self.start_time or datetime.now(),
                end_time=datetime.now(),
                duration=0.0,
                error_message=str(e),
                impact_metrics={}
            )
    
    async def stop(self) -> bool:
        """Remove latência de rede"""
        try:
            with self.lock:
                if not self.is_active:
                    return True
                
                self.is_active = False
                self.stop_time = datetime.now()
            
            # Remover configuração do tc
            if self.tc_process:
                self.tc_process.terminate()
                self.tc_process.wait()
            
            # Limpar configuração
            cmd = ['tc', 'qdisc', 'del', 'dev', self.target_interface, 'root']
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            logger.info("Network latency injection stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping network latency: {e}")
            return False
    
    def validate_config(self) -> List[str]:
        """Valida configuração"""
        errors = []
        
        if self.latency_ms < 0:
            errors.append("Latência deve ser maior ou igual a zero")
        
        if self.jitter_ms < 0:
            errors.append("Jitter deve ser maior ou igual a zero")
        
        if self.latency_ms > 10000:  # 10 segundos
            errors.append("Latência muito alta (> 10s)")
        
        return errors
    
    def _check_tc_available(self) -> bool:
        """Verifica se tc está disponível"""
        try:
            result = subprocess.run(['tc', '--version'], 
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.returncode == 0
        except FileNotFoundError:
            return False


class NetworkPacketLossStrategy(InjectionStrategy):
    """Estratégia de injeção de perda de pacotes"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.loss_percentage = config.get('loss_percentage', 5.0)
        self.target_interface = config.get('target_interface', 'eth0')
        self.tc_process: Optional[subprocess.Popen] = None
    
    async def inject(self) -> InjectionResult:
        """Injeta perda de pacotes"""
        try:
            with self.lock:
                self.is_active = True
                self.start_time = datetime.now()
            
            # Verificar se tc está disponível
            if not self._check_tc_available():
                raise RuntimeError("tc (traffic control) não está disponível")
            
            # Configurar perda de pacotes usando tc
            cmd = [
                'tc', 'qdisc', 'add', 'dev', self.target_interface,
                'root', 'netem', 'loss', f'{self.loss_percentage}%'
            ]
            
            self.tc_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            
            # Aguardar um pouco para aplicar
            await asyncio.sleep(1)
            
            if self.tc_process.poll() is not None:
                raise RuntimeError("Falha ao aplicar perda de pacotes")
            
            logger.info(f"Packet loss injected: {self.loss_percentage}%")
            
            return InjectionResult(
                success=True,
                injection_id=self.injection_id,
                start_time=self.start_time,
                end_time=None,
                duration=None,
                error_message=None,
                impact_metrics={'loss_percentage': self.loss_percentage}
            )
            
        except Exception as e:
            logger.error(f"Error injecting packet loss: {e}")
            return InjectionResult(
                success=False,
                injection_id=self.injection_id,
                start_time=self.start_time or datetime.now(),
                end_time=datetime.now(),
                duration=0.0,
                error_message=str(e),
                impact_metrics={}
            )
    
    async def stop(self) -> bool:
        """Remove perda de pacotes"""
        try:
            with self.lock:
                if not self.is_active:
                    return True
                
                self.is_active = False
                self.stop_time = datetime.now()
            
            # Remover configuração do tc
            if self.tc_process:
                self.tc_process.terminate()
                self.tc_process.wait()
            
            # Limpar configuração
            cmd = ['tc', 'qdisc', 'del', 'dev', self.target_interface, 'root']
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            logger.info("Packet loss injection stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping packet loss: {e}")
            return False
    
    def validate_config(self) -> List[str]:
        """Valida configuração"""
        errors = []
        
        if not 0 <= self.loss_percentage <= 100:
            errors.append("Percentual de perda deve estar entre 0 e 100")
        
        if self.loss_percentage > 50:
            errors.append("Percentual de perda muito alto (> 50%)")
        
        return errors
    
    def _check_tc_available(self) -> bool:
        """Verifica se tc está disponível"""
        try:
            result = subprocess.run(['tc', '--version'], 
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.returncode == 0
        except FileNotFoundError:
            return False


class CPUStressStrategy(InjectionStrategy):
    """Estratégia de stress de CPU"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.cpu_load = config.get('cpu_load', 0.7)  # 70% de carga
        self.cores = config.get('cores', 2)
        self.stress_processes: List[subprocess.Popen] = []
    
    async def inject(self) -> InjectionResult:
        """Injeta stress de CPU"""
        try:
            with self.lock:
                self.is_active = True
                self.start_time = datetime.now()
            
            # Criar processos de stress
            for i in range(self.cores):
                cmd = [
                    'stress', '--cpu', '1', '--timeout', '3600'  # 1 hora
                ]
                
                process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                self.stress_processes.append(process)
            
            # Aguardar um pouco para aplicar
            await asyncio.sleep(2)
            
            # Verificar se processos estão rodando
            for process in self.stress_processes:
                if process.poll() is not None:
                    raise RuntimeError("Falha ao iniciar stress de CPU")
            
            logger.info(f"CPU stress injected: {self.cores} cores at {self.cpu_load*100}% load")
            
            return InjectionResult(
                success=True,
                injection_id=self.injection_id,
                start_time=self.start_time,
                end_time=None,
                duration=None,
                error_message=None,
                impact_metrics={'cpu_load': self.cpu_load, 'cores': self.cores}
            )
            
        except Exception as e:
            logger.error(f"Error injecting CPU stress: {e}")
            return InjectionResult(
                success=False,
                injection_id=self.injection_id,
                start_time=self.start_time or datetime.now(),
                end_time=datetime.now(),
                duration=0.0,
                error_message=str(e),
                impact_metrics={}
            )
    
    async def stop(self) -> bool:
        """Para stress de CPU"""
        try:
            with self.lock:
                if not self.is_active:
                    return True
                
                self.is_active = False
                self.stop_time = datetime.now()
            
            # Parar processos de stress
            for process in self.stress_processes:
                process.terminate()
                process.wait()
            
            self.stress_processes.clear()
            
            logger.info("CPU stress injection stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping CPU stress: {e}")
            return False
    
    def validate_config(self) -> List[str]:
        """Valida configuração"""
        errors = []
        
        if not 0 < self.cpu_load <= 1:
            errors.append("Carga de CPU deve estar entre 0 e 1")
        
        if self.cores <= 0:
            errors.append("Número de cores deve ser maior que zero")
        
        if self.cores > psutil.cpu_count():
            errors.append("Número de cores excede CPUs disponíveis")
        
        if self.cpu_load > 0.9:
            errors.append("Carga de CPU muito alta (> 90%)")
        
        return errors


class MemoryStressStrategy(InjectionStrategy):
    """Estratégia de stress de memória"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.memory_mb = config.get('memory_mb', 512)  # 512MB
        self.stress_process: Optional[subprocess.Popen] = None
    
    async def inject(self) -> InjectionResult:
        """Injeta stress de memória"""
        try:
            with self.lock:
                self.is_active = True
                self.start_time = datetime.now()
            
            # Verificar memória disponível
            available_memory = psutil.virtual_memory().available / (1024 * 1024)  # MB
            if self.memory_mb > available_memory * 0.8:
                raise RuntimeError(f"Memória solicitada ({self.memory_mb}MB) excede 80% da disponível ({available_memory:.0f}MB)")
            
            # Criar processo de stress
            cmd = [
                'stress', '--vm', '1', '--vm-bytes', f'{self.memory_mb}M', '--timeout', '3600'
            ]
            
            self.stress_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            
            # Aguardar um pouco para aplicar
            await asyncio.sleep(2)
            
            if self.stress_process.poll() is not None:
                raise RuntimeError("Falha ao iniciar stress de memória")
            
            logger.info(f"Memory stress injected: {self.memory_mb}MB")
            
            return InjectionResult(
                success=True,
                injection_id=self.injection_id,
                start_time=self.start_time,
                end_time=None,
                duration=None,
                error_message=None,
                impact_metrics={'memory_mb': self.memory_mb}
            )
            
        except Exception as e:
            logger.error(f"Error injecting memory stress: {e}")
            return InjectionResult(
                success=False,
                injection_id=self.injection_id,
                start_time=self.start_time or datetime.now(),
                end_time=datetime.now(),
                duration=0.0,
                error_message=str(e),
                impact_metrics={}
            )
    
    async def stop(self) -> bool:
        """Para stress de memória"""
        try:
            with self.lock:
                if not self.is_active:
                    return True
                
                self.is_active = False
                self.stop_time = datetime.now()
            
            # Parar processo de stress
            if self.stress_process:
                self.stress_process.terminate()
                self.stress_process.wait()
                self.stress_process = None
            
            logger.info("Memory stress injection stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping memory stress: {e}")
            return False
    
    def validate_config(self) -> List[str]:
        """Valida configuração"""
        errors = []
        
        if self.memory_mb <= 0:
            errors.append("Memória deve ser maior que zero")
        
        # Verificar se não excede 80% da memória disponível
        available_memory = psutil.virtual_memory().available / (1024 * 1024)  # MB
        if self.memory_mb > available_memory * 0.8:
            errors.append(f"Memória solicitada excede 80% da disponível ({available_memory:.0f}MB)")
        
        return errors


class ServiceFailureStrategy(InjectionStrategy):
    """Estratégia de falha de serviço"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.service_name = config.get('service_name', '')
        self.failure_rate = config.get('failure_rate', 0.3)  # 30% de falha
        self.failure_pattern = config.get('failure_pattern', 'random')
        self.original_service_state = None
    
    async def inject(self) -> InjectionResult:
        """Injeta falha de serviço"""
        try:
            with self.lock:
                self.is_active = True
                self.start_time = datetime.now()
            
            # Verificar se serviço existe
            if not self._service_exists():
                raise RuntimeError(f"Serviço '{self.service_name}' não encontrado")
            
            # Salvar estado original
            self.original_service_state = self._get_service_state()
            
            # Aplicar falha baseada no padrão
            if self.failure_pattern == 'stop':
                await self._stop_service()
            elif self.failure_pattern == 'restart':
                await self._restart_service()
            elif self.failure_pattern == 'random':
                await self._apply_random_failure()
            else:
                raise ValueError(f"Padrão de falha desconhecido: {self.failure_pattern}")
            
            logger.info(f"Service failure injected: {self.service_name} ({self.failure_pattern})")
            
            return InjectionResult(
                success=True,
                injection_id=self.injection_id,
                start_time=self.start_time,
                end_time=None,
                duration=None,
                error_message=None,
                impact_metrics={'service_name': self.service_name, 'failure_rate': self.failure_rate}
            )
            
        except Exception as e:
            logger.error(f"Error injecting service failure: {e}")
            return InjectionResult(
                success=False,
                injection_id=self.injection_id,
                start_time=self.start_time or datetime.now(),
                end_time=datetime.now(),
                duration=0.0,
                error_message=str(e),
                impact_metrics={}
            )
    
    async def stop(self) -> bool:
        """Restaura serviço"""
        try:
            with self.lock:
                if not self.is_active:
                    return True
                
                self.is_active = False
                self.stop_time = datetime.now()
            
            # Restaurar estado original
            if self.original_service_state:
                await self._restore_service_state()
            
            logger.info(f"Service failure injection stopped: {self.service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping service failure: {e}")
            return False
    
    def validate_config(self) -> List[str]:
        """Valida configuração"""
        errors = []
        
        if not self.service_name:
            errors.append("Nome do serviço é obrigatório")
        
        if not 0 <= self.failure_rate <= 1:
            errors.append("Taxa de falha deve estar entre 0 e 1")
        
        if self.failure_pattern not in ['stop', 'restart', 'random']:
            errors.append("Padrão de falha deve ser 'stop', 'restart' ou 'random'")
        
        return errors
    
    def _service_exists(self) -> bool:
        """Verifica se serviço existe"""
        try:
            result = subprocess.run(['systemctl', 'status', self.service_name],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def _get_service_state(self) -> str:
        """Obtém estado atual do serviço"""
        try:
            result = subprocess.run(['systemctl', 'is-active', self.service_name],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  text=True)
            return result.stdout.strip()
        except Exception:
            return "unknown"
    
    async def _stop_service(self) -> None:
        """Para o serviço"""
        subprocess.run(['systemctl', 'stop', self.service_name],
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    async def _restart_service(self) -> None:
        """Reinicia o serviço"""
        subprocess.run(['systemctl', 'restart', self.service_name],
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    async def _apply_random_failure(self) -> None:
        """Aplica falha aleatória"""
        if random.random() < self.failure_rate:
            await self._stop_service()
    
    async def _restore_service_state(self) -> None:
        """Restaura estado original do serviço"""
        if self.original_service_state == 'active':
            subprocess.run(['systemctl', 'start', self.service_name],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)


class StrategyFactory:
    """Factory para criar estratégias de injeção"""
    
    _strategies = {
        InjectionType.NETWORK_LATENCY: NetworkLatencyStrategy,
        InjectionType.NETWORK_PACKET_LOSS: NetworkPacketLossStrategy,
        InjectionType.CPU_STRESS: CPUStressStrategy,
        InjectionType.MEMORY_STRESS: MemoryStressStrategy,
        InjectionType.SERVICE_FAILURE: ServiceFailureStrategy,
    }
    
    @classmethod
    def create_strategy(cls, injection_type: InjectionType, config: Dict[str, Any]) -> InjectionStrategy:
        """Cria uma estratégia de injeção"""
        if injection_type not in cls._strategies:
            raise ValueError(f"Tipo de injeção não suportado: {injection_type}")
        
        strategy_class = cls._strategies[injection_type]
        return strategy_class(config)
    
    @classmethod
    def get_available_strategies(cls) -> List[InjectionType]:
        """Obtém estratégias disponíveis"""
        return list(cls._strategies.keys())


class InjectionOrchestrator:
    """Orquestrador de injeções de falhas"""
    
    def __init__(self):
        self.active_injections: Dict[str, InjectionStrategy] = {}
        self.injection_history: List[InjectionResult] = []
        self.lock = threading.RLock()
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        logger.info("InjectionOrchestrator initialized")
    
    async def inject_failure(self, injection_type: InjectionType, 
                           config: Dict[str, Any]) -> InjectionResult:
        """Executa injeção de falha"""
        try:
            # Criar estratégia
            strategy = StrategyFactory.create_strategy(injection_type, config)
            
            # Validar configuração
            errors = strategy.validate_config()
            if errors:
                raise ValueError(f"Configuração inválida: {', '.join(errors)}")
            
            # Executar injeção
            result = await strategy.inject()
            
            if result.success:
                with self.lock:
                    self.active_injections[strategy.injection_id] = strategy
            
            # Registrar no histórico
            with self.lock:
                self.injection_history.append(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in failure injection: {e}")
            return InjectionResult(
                success=False,
                injection_id=f"failed_{int(time.time())}",
                start_time=datetime.now(),
                end_time=datetime.now(),
                duration=0.0,
                error_message=str(e),
                impact_metrics={}
            )
    
    async def stop_injection(self, injection_id: str) -> bool:
        """Para uma injeção específica"""
        with self.lock:
            if injection_id not in self.active_injections:
                return False
            
            strategy = self.active_injections[injection_id]
        
        try:
            success = await strategy.stop()
            
            if success:
                with self.lock:
                    del self.active_injections[injection_id]
            
            return success
            
        except Exception as e:
            logger.error(f"Error stopping injection {injection_id}: {e}")
            return False
    
    async def stop_all_injections(self) -> bool:
        """Para todas as injeções ativas"""
        try:
            injection_ids = list(self.active_injections.keys())
            results = []
            
            for injection_id in injection_ids:
                result = await self.stop_injection(injection_id)
                results.append(result)
            
            return all(results)
            
        except Exception as e:
            logger.error(f"Error stopping all injections: {e}")
            return False
    
    def get_active_injections(self) -> List[Dict[str, Any]]:
        """Obtém injeções ativas"""
        with self.lock:
            return [
                {
                    'injection_id': injection_id,
                    'strategy_type': strategy.__class__.__name__,
                    'status': strategy.get_status()
                }
                for injection_id, strategy in self.active_injections.items()
            ]
    
    def get_injection_history(self, limit: Optional[int] = None) -> List[InjectionResult]:
        """Obtém histórico de injeções"""
        with self.lock:
            history = list(self.injection_history)
            if limit:
                history = history[-limit:]
            return history
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas"""
        with self.lock:
            total_injections = len(self.injection_history)
            successful_injections = len([r for r in self.injection_history if r.success])
            active_injections = len(self.active_injections)
            
            return {
                'total_injections': total_injections,
                'successful_injections': successful_injections,
                'failed_injections': total_injections - successful_injections,
                'success_rate': successful_injections / total_injections if total_injections > 0 else 0,
                'active_injections': active_injections
            }


# Função de conveniência para criar orquestrador
def create_injection_orchestrator() -> InjectionOrchestrator:
    """Cria uma instância do injection orchestrator"""
    return InjectionOrchestrator() 