"""
Self-Healing Service - Sistema de Auto-Cura para Serviços

Tracing ID: SELF_HEALING_001_20250127
Versão: 1.0
Data: 2025-01-27
Objetivo: Detectar e corrigir automaticamente problemas em serviços

Este módulo implementa um sistema de self-healing que monitora serviços
e aplica correções automáticas quando detecta problemas.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import traceback
from concurrent.futures import ThreadPoolExecutor
import threading

from .healing_strategies import HealingStrategy, ServiceRestartStrategy, ConnectionRecoveryStrategy
from .healing_monitor import HealingMonitor
from .healing_config import HealingConfig

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Status dos serviços monitorados"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    RECOVERING = "recovering"
    UNKNOWN = "unknown"


class ProblemType(Enum):
    """Tipos de problemas detectados"""
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    MEMORY_LEAK = "memory_leak"
    CPU_SPIKE = "cpu_spike"
    DISK_FULL = "disk_full"
    SERVICE_CRASH = "service_crash"
    API_ERROR = "api_error"
    DATABASE_ERROR = "database_error"
    CACHE_ERROR = "cache_error"
    NETWORK_ERROR = "network_error"


@dataclass
class ServiceInfo:
    """Informações sobre um serviço monitorado"""
    name: str
    endpoint: str
    health_check_url: Optional[str] = None
    check_interval: int = 30
    timeout: int = 10
    max_retries: int = 3
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_check: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    failure_count: int = 0
    recovery_attempts: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProblemReport:
    """Relatório de problema detectado"""
    service_name: str
    problem_type: ProblemType
    severity: str
    description: str
    timestamp: datetime
    metrics: Dict[str, Any]
    context: Dict[str, Any]


class SelfHealingService:
    """
    Serviço principal de self-healing que monitora e corrige problemas automaticamente
    """
    
    def __init__(self, config: HealingConfig):
        """
        Inicializa o serviço de self-healing
        
        Args:
            config: Configuração do sistema de healing
        """
        self.config = config
        self.monitor = HealingMonitor(config)
        self.services: Dict[str, ServiceInfo] = {}
        self.strategies: Dict[ProblemType, HealingStrategy] = {}
        self.is_running = False
        self.executor = ThreadPoolExecutor(max_workers=config.max_workers)
        self.lock = threading.RLock()
        
        # Inicializar estratégias de healing
        self._initialize_strategies()
        
        # Histórico de problemas e correções
        self.problem_history: List[ProblemReport] = []
        self.correction_history: List[Dict[str, Any]] = []
        
        logger.info(f"[SELF_HEALING] Serviço inicializado com {len(self.strategies)} estratégias")
    
    def _initialize_strategies(self):
        """Inicializa as estratégias de healing disponíveis"""
        self.strategies[ProblemType.SERVICE_CRASH] = ServiceRestartStrategy(self.config)
        self.strategies[ProblemType.CONNECTION_ERROR] = ConnectionRecoveryStrategy(self.config)
        self.strategies[ProblemType.TIMEOUT] = ServiceRestartStrategy(self.config)
        self.strategies[ProblemType.API_ERROR] = ServiceRestartStrategy(self.config)
        self.strategies[ProblemType.DATABASE_ERROR] = ConnectionRecoveryStrategy(self.config)
        self.strategies[ProblemType.CACHE_ERROR] = ConnectionRecoveryStrategy(self.config)
        
        logger.info(f"[SELF_HEALING] Estratégias inicializadas: {list(self.strategies.keys())}")
    
    def register_service(self, service_info: ServiceInfo) -> None:
        """
        Registra um serviço para monitoramento
        
        Args:
            service_info: Informações do serviço
        """
        with self.lock:
            self.services[service_info.name] = service_info
            logger.info(f"[SELF_HEALING] Serviço registrado: {service_info.name}")
    
    def unregister_service(self, service_name: str) -> None:
        """
        Remove um serviço do monitoramento
        
        Args:
            service_name: Nome do serviço
        """
        with self.lock:
            if service_name in self.services:
                del self.services[service_name]
                logger.info(f"[SELF_HEALING] Serviço removido: {service_name}")
    
    async def start_monitoring(self) -> None:
        """Inicia o monitoramento de todos os serviços registrados"""
        if self.is_running:
            logger.warning("[SELF_HEALING] Monitoramento já está em execução")
            return
        
        self.is_running = True
        logger.info("[SELF_HEALING] Iniciando monitoramento de serviços")
        
        # Iniciar monitor em thread separada
        asyncio.create_task(self._monitoring_loop())
        
        # Iniciar limpeza periódica
        asyncio.create_task(self._cleanup_loop())
    
    async def stop_monitoring(self) -> None:
        """Para o monitoramento de serviços"""
        self.is_running = False
        logger.info("[SELF_HEALING] Parando monitoramento de serviços")
    
    async def _monitoring_loop(self) -> None:
        """Loop principal de monitoramento"""
        while self.is_running:
            try:
                await self._check_all_services()
                await asyncio.sleep(self.config.check_interval)
            except Exception as e:
                logger.error(f"[SELF_HEALING] Erro no loop de monitoramento: {e}")
                await asyncio.sleep(5)  # Aguardar antes de tentar novamente
    
    async def _check_all_services(self) -> None:
        """Verifica todos os serviços registrados"""
        tasks = []
        
        with self.lock:
            for service_info in self.services.values():
                if self._should_check_service(service_info):
                    task = asyncio.create_task(self._check_service(service_info))
                    tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def _should_check_service(self, service_info: ServiceInfo) -> bool:
        """Verifica se um serviço deve ser verificado"""
        if not service_info.last_check:
            return True
        
        time_since_check = datetime.now() - service_info.last_check
        return time_since_check.total_seconds() >= service_info.check_interval
    
    async def _check_service(self, service_info: ServiceInfo) -> None:
        """
        Verifica um serviço específico
        
        Args:
            service_info: Informações do serviço
        """
        try:
            # Atualizar timestamp da verificação
            service_info.last_check = datetime.now()
            
            # Verificar saúde do serviço
            health_status = await self.monitor.check_service_health(service_info)
            
            # Atualizar status do serviço
            old_status = service_info.status
            service_info.status = health_status
            
            # Se o serviço está saudável, resetar contadores
            if health_status == ServiceStatus.HEALTHY:
                if old_status != ServiceStatus.HEALTHY:
                    logger.info(f"[SELF_HEALING] Serviço {service_info.name} recuperado")
                service_info.failure_count = 0
                service_info.recovery_attempts = 0
            else:
                # Incrementar contador de falhas
                service_info.failure_count += 1
                service_info.last_failure = datetime.now()
                
                # Detectar problema
                problem = await self._detect_problem(service_info, health_status)
                if problem:
                    await self._handle_problem(problem)
        
        except Exception as e:
            logger.error(f"[SELF_HEALING] Erro ao verificar serviço {service_info.name}: {e}")
            service_info.status = ServiceStatus.UNKNOWN
    
    async def _detect_problem(self, service_info: ServiceInfo, status: ServiceStatus) -> Optional[ProblemReport]:
        """
        Detecta problemas baseado no status e métricas
        
        Args:
            service_info: Informações do serviço
            status: Status atual do serviço
            
        Returns:
            Relatório do problema detectado ou None
        """
        try:
            # Coletar métricas do serviço
            metrics = await self.monitor.collect_service_metrics(service_info)
            
            # Analisar métricas para detectar problemas
            problem_type = self._analyze_metrics(metrics, status)
            
            if problem_type:
                problem = ProblemReport(
                    service_name=service_info.name,
                    problem_type=problem_type,
                    severity=self._determine_severity(problem_type, service_info.failure_count),
                    description=self._generate_problem_description(problem_type, metrics),
                    timestamp=datetime.now(),
                    metrics=metrics,
                    context={
                        "failure_count": service_info.failure_count,
                        "recovery_attempts": service_info.recovery_attempts,
                        "last_failure": service_info.last_failure.isoformat() if service_info.last_failure else None
                    }
                )
                
                self.problem_history.append(problem)
                return problem
            
            return None
        
        except Exception as e:
            logger.error(f"[SELF_HEALING] Erro ao detectar problema: {e}")
            return None
    
    def _analyze_metrics(self, metrics: Dict[str, Any], status: ServiceStatus) -> Optional[ProblemType]:
        """
        Analisa métricas para determinar o tipo de problema
        
        Args:
            metrics: Métricas coletadas
            status: Status do serviço
            
        Returns:
            Tipo de problema detectado ou None
        """
        if status == ServiceStatus.FAILED:
            # Verificar tipo específico de falha
            if metrics.get("connection_error"):
                return ProblemType.CONNECTION_ERROR
            elif metrics.get("timeout_error"):
                return ProblemType.TIMEOUT
            elif metrics.get("api_error"):
                return ProblemType.API_ERROR
            elif metrics.get("database_error"):
                return ProblemType.DATABASE_ERROR
            elif metrics.get("cache_error"):
                return ProblemType.CACHE_ERROR
            else:
                return ProblemType.SERVICE_CRASH
        
        elif status == ServiceStatus.DEGRADED:
            # Verificar degradação
            if metrics.get("memory_usage", 0) > 90:
                return ProblemType.MEMORY_LEAK
            elif metrics.get("cpu_usage", 0) > 95:
                return ProblemType.CPU_SPIKE
            elif metrics.get("disk_usage", 0) > 95:
                return ProblemType.DISK_FULL
        
        return None
    
    def _determine_severity(self, problem_type: ProblemType, failure_count: int) -> str:
        """
        Determina a severidade do problema
        
        Args:
            problem_type: Tipo do problema
            failure_count: Número de falhas consecutivas
            
        Returns:
            Severidade do problema (low, medium, high, critical)
        """
        if failure_count >= 5:
            return "critical"
        elif failure_count >= 3:
            return "high"
        elif failure_count >= 2:
            return "medium"
        else:
            return "low"
    
    def _generate_problem_description(self, problem_type: ProblemType, metrics: Dict[str, Any]) -> str:
        """
        Gera descrição do problema
        
        Args:
            problem_type: Tipo do problema
            metrics: Métricas coletadas
            
        Returns:
            Descrição do problema
        """
        descriptions = {
            ProblemType.TIMEOUT: f"Timeout detectado (limite: {metrics.get('timeout_limit', 'N/A')}s)",
            ProblemType.CONNECTION_ERROR: "Erro de conexão detectado",
            ProblemType.MEMORY_LEAK: f"Uso de memória alto: {metrics.get('memory_usage', 0)}%",
            ProblemType.CPU_SPIKE: f"Uso de CPU alto: {metrics.get('cpu_usage', 0)}%",
            ProblemType.DISK_FULL: f"Disco quase cheio: {metrics.get('disk_usage', 0)}%",
            ProblemType.SERVICE_CRASH: "Serviço não está respondendo",
            ProblemType.API_ERROR: f"Erro de API: {metrics.get('api_error_code', 'N/A')}",
            ProblemType.DATABASE_ERROR: "Erro de conexão com banco de dados",
            ProblemType.CACHE_ERROR: "Erro de conexão com cache",
            ProblemType.NETWORK_ERROR: "Erro de rede detectado"
        }
        
        return descriptions.get(problem_type, f"Problema desconhecido: {problem_type.value}")
    
    async def _handle_problem(self, problem: ProblemReport) -> None:
        """
        Trata um problema detectado
        
        Args:
            problem: Relatório do problema
        """
        try:
            logger.warning(f"[SELF_HEALING] Problema detectado: {problem.service_name} - {problem.problem_type.value}")
            
            # Verificar se há estratégia para este tipo de problema
            strategy = self.strategies.get(problem.problem_type)
            if not strategy:
                logger.warning(f"[SELF_HEALING] Nenhuma estratégia para problema: {problem.problem_type.value}")
                return
            
            # Verificar se não excedeu o limite de tentativas
            service_info = self.services.get(problem.service_name)
            if service_info and service_info.recovery_attempts >= self.config.max_recovery_attempts:
                logger.error(f"[SELF_HEALING] Limite de tentativas excedido para {problem.service_name}")
                return
            
            # Aplicar estratégia de correção
            success = await strategy.apply(problem)
            
            # Registrar tentativa de correção
            correction_record = {
                "service_name": problem.service_name,
                "problem_type": problem.problem_type.value,
                "strategy": strategy.__class__.__name__,
                "success": success,
                "timestamp": datetime.now().isoformat(),
                "problem_id": len(self.problem_history)
            }
            
            self.correction_history.append(correction_record)
            
            if success:
                logger.info(f"[SELF_HEALING] Problema corrigido: {problem.service_name}")
                if service_info:
                    service_info.recovery_attempts = 0
            else:
                logger.error(f"[SELF_HEALING] Falha na correção: {problem.service_name}")
                if service_info:
                    service_info.recovery_attempts += 1
        
        except Exception as e:
            logger.error(f"[SELF_HEALING] Erro ao tratar problema: {e}")
    
    async def _cleanup_loop(self) -> None:
        """Loop de limpeza de histórico antigo"""
        while self.is_running:
            try:
                await asyncio.sleep(self.config.cleanup_interval)
                self._cleanup_old_records()
            except Exception as e:
                logger.error(f"[SELF_HEALING] Erro no loop de limpeza: {e}")
    
    def _cleanup_old_records(self) -> None:
        """Remove registros antigos do histórico"""
        cutoff_time = datetime.now() - timedelta(hours=self.config.history_retention_hours)
        
        # Limpar histórico de problemas
        self.problem_history = [
            problem for problem in self.problem_history
            if problem.timestamp > cutoff_time
        ]
        
        # Limpar histórico de correções
        self.correction_history = [
            correction for correction in self.correction_history
            if datetime.fromisoformat(correction["timestamp"]) > cutoff_time
        ]
        
        logger.debug(f"[SELF_HEALING] Limpeza concluída. Problemas: {len(self.problem_history)}, Correções: {len(self.correction_history)}")
    
    def get_service_status(self, service_name: str) -> Optional[ServiceInfo]:
        """
        Obtém status de um serviço específico
        
        Args:
            service_name: Nome do serviço
            
        Returns:
            Informações do serviço ou None
        """
        return self.services.get(service_name)
    
    def get_all_services_status(self) -> Dict[str, ServiceInfo]:
        """
        Obtém status de todos os serviços
        
        Returns:
            Dicionário com status de todos os serviços
        """
        return self.services.copy()
    
    def get_problem_history(self, service_name: Optional[str] = None) -> List[ProblemReport]:
        """
        Obtém histórico de problemas
        
        Args:
            service_name: Nome do serviço (opcional)
            
        Returns:
            Lista de problemas
        """
        if service_name:
            return [p for p in self.problem_history if p.service_name == service_name]
        return self.problem_history.copy()
    
    def get_correction_history(self, service_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtém histórico de correções
        
        Args:
            service_name: Nome do serviço (opcional)
            
        Returns:
            Lista de correções
        """
        if service_name:
            return [c for c in self.correction_history if c["service_name"] == service_name]
        return self.correction_history.copy()
    
    def get_health_summary(self) -> Dict[str, Any]:
        """
        Obtém resumo da saúde do sistema
        
        Returns:
            Resumo da saúde
        """
        total_services = len(self.services)
        healthy_services = sum(1 for s in self.services.values() if s.status == ServiceStatus.HEALTHY)
        failed_services = sum(1 for s in self.services.values() if s.status == ServiceStatus.FAILED)
        degraded_services = sum(1 for s in self.services.values() if s.status == ServiceStatus.DEGRADED)
        
        return {
            "total_services": total_services,
            "healthy_services": healthy_services,
            "failed_services": failed_services,
            "degraded_services": degraded_services,
            "health_percentage": (healthy_services / total_services * 100) if total_services > 0 else 0,
            "recent_problems": len([p for p in self.problem_history if p.timestamp > datetime.now() - timedelta(hours=1)]),
            "recent_corrections": len([c for c in self.correction_history if datetime.fromisoformat(c["timestamp"]) > datetime.now() - timedelta(hours=1)]),
            "is_monitoring": self.is_running
        } 