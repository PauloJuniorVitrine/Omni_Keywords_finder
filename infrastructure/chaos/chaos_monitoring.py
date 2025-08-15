"""
Chaos Engineering Monitoring System
==================================

Sistema de monitoramento para chaos engineering com:
- Coleta de métricas em tempo real
- Análise de impacto dos experimentos
- Alertas baseados em thresholds
- Integração com sistemas de observabilidade
- Relatórios de impacto

Author: Paulo Júnior
Date: 2025-01-27
Tracing ID: CHAOS_MONITORING_001_20250127
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
from collections import deque, defaultdict

import psutil
import requests
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Tipos de métricas"""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_IO = "network_io"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    AVAILABILITY = "availability"
    CUSTOM = "custom"


class AlertSeverity(Enum):
    """Severidade dos alertas"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class SystemMetrics:
    """Métricas do sistema"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_sent: float
    network_recv: float
    disk_read: float
    disk_write: float


@dataclass
class ApplicationMetrics:
    """Métricas da aplicação"""
    timestamp: datetime
    response_time: float
    error_rate: float
    throughput: float
    availability: float
    active_connections: int
    queue_size: int
    custom_metrics: Dict[str, Any]


@dataclass
class ChaosMetrics:
    """Métricas específicas do chaos engineering"""
    timestamp: datetime
    experiment_id: str
    phase: str
    system_metrics: SystemMetrics
    application_metrics: ApplicationMetrics
    impact_score: float
    baseline_deviation: float
    recovery_time: Optional[float] = None


@dataclass
class Alert:
    """Alerta do sistema"""
    id: str
    timestamp: datetime
    severity: AlertSeverity
    metric_type: MetricType
    metric_value: float
    threshold: float
    message: str
    experiment_id: Optional[str] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class ImpactAnalysis(BaseModel):
    """Análise de impacto de um experimento"""
    experiment_id: str
    start_time: datetime
    end_time: datetime
    duration: float
    
    # Métricas de impacto
    max_cpu_impact: float
    max_memory_impact: float
    max_error_rate_impact: float
    max_response_time_impact: float
    availability_impact: float
    
    # Análise de recuperação
    recovery_time: Optional[float]
    recovery_successful: bool
    baseline_deviation: float
    
    # Classificação de impacto
    impact_level: str  # low, medium, high, critical
    recommendations: List[str]


class MonitoringConfig(BaseModel):
    """Configuração de monitoramento"""
    enabled: bool = Field(True, description="Monitoramento habilitado")
    metrics_interval: int = Field(5, description="Intervalo de coleta em segundos")
    retention_period: int = Field(3600, description="Período de retenção em segundos")
    
    # Métricas a coletar
    collect_system_metrics: bool = Field(True, description="Coletar métricas do sistema")
    collect_application_metrics: bool = Field(True, description="Coletar métricas da aplicação")
    collect_custom_metrics: bool = Field(True, description="Coletar métricas customizadas")
    
    # Thresholds de alerta
    cpu_threshold: float = Field(0.8, description="Threshold de CPU (0-1)")
    memory_threshold: float = Field(0.8, description="Threshold de memória (0-1)")
    disk_threshold: float = Field(0.9, description="Threshold de disco (0-1)")
    error_rate_threshold: float = Field(0.05, description="Threshold de taxa de erro")
    response_time_threshold: float = Field(2.0, description="Threshold de tempo de resposta (s)")
    availability_threshold: float = Field(0.95, description="Threshold de disponibilidade")
    
    # Configurações de análise
    baseline_window: int = Field(300, description="Janela para baseline em segundos")
    impact_calculation_window: int = Field(60, description="Janela para cálculo de impacto")
    recovery_timeout: int = Field(300, description="Timeout para recuperação (s)")
    
    # Configurações de exportação
    export_to_prometheus: bool = Field(True, description="Exportar para Prometheus")
    export_to_grafana: bool = Field(True, description="Exportar para Grafana")
    export_to_logs: bool = Field(True, description="Exportar para logs")


class ChaosMonitor:
    """
    Monitor de chaos engineering
    """
    
    def __init__(self, config: Optional[MonitoringConfig] = None):
        self.config = config or MonitoringConfig()
        self.metrics_buffer: deque = deque(maxlen=1000)
        self.alerts: Dict[str, Alert] = {}
        self.baseline_metrics: Optional[ChaosMetrics] = None
        self.current_experiment: Optional[str] = None
        self.monitoring_task: Optional[asyncio.Task] = None
        self.stop_monitoring_flag = False
        
        # Callbacks
        self.alert_callbacks: List[Callable] = []
        self.metrics_callbacks: List[Callable] = []
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Estatísticas
        self.stats = {
            'metrics_collected': 0,
            'alerts_generated': 0,
            'experiments_monitored': 0,
            'total_monitoring_time': 0
        }
        
        logger.info("ChaosMonitor initialized")
    
    async def start_monitoring(self, interval: Optional[int] = None) -> None:
        """Inicia o monitoramento"""
        if self.monitoring_task and not self.monitoring_task.done():
            logger.warning("Monitoring already started")
            return
        
        self.stop_monitoring_flag = False
        interval = interval or self.config.metrics_interval
        
        self.monitoring_task = asyncio.create_task(
            self._monitoring_loop(interval)
        )
        logger.info(f"Started monitoring with interval {interval}s")
    
    async def stop_monitoring(self) -> None:
        """Para o monitoramento"""
        self.stop_monitoring_flag = True
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Monitoring stopped")
    
    async def _monitoring_loop(self, interval: int) -> None:
        """Loop principal de monitoramento"""
        start_time = time.time()
        
        while not self.stop_monitoring_flag:
            try:
                # Coletar métricas
                metrics = await self.collect_metrics()
                
                # Armazenar métricas
                with self.lock:
                    self.metrics_buffer.append(metrics)
                    self.stats['metrics_collected'] += 1
                
                # Verificar alertas
                await self._check_alerts(metrics)
                
                # Notificar callbacks
                await self._notify_callbacks(metrics)
                
                # Aguardar próximo ciclo
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval)
        
        self.stats['total_monitoring_time'] = time.time() - start_time
    
    async def collect_metrics(self) -> ChaosMetrics:
        """Coleta métricas do sistema e aplicação"""
        timestamp = datetime.now()
        
        # Métricas do sistema
        system_metrics = await self._collect_system_metrics()
        
        # Métricas da aplicação
        application_metrics = await self._collect_application_metrics()
        
        # Calcular impacto
        impact_score = self._calculate_impact_score(system_metrics, application_metrics)
        baseline_deviation = self._calculate_baseline_deviation(system_metrics, application_metrics)
        
        # Criar métricas de chaos
        metrics = ChaosMetrics(
            timestamp=timestamp,
            experiment_id=self.current_experiment or "baseline",
            phase=self._get_current_phase(),
            system_metrics=system_metrics,
            application_metrics=application_metrics,
            impact_score=impact_score,
            baseline_deviation=baseline_deviation
        )
        
        return metrics
    
    async def _collect_system_metrics(self) -> SystemMetrics:
        """Coleta métricas do sistema"""
        try:
            # CPU
            cpu_usage = psutil.cpu_percent(interval=1) / 100.0
            
            # Memória
            memory = psutil.virtual_memory()
            memory_usage = memory.percent / 100.0
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_usage = (disk.total - disk.free) / disk.total
            
            # Rede
            network = psutil.net_io_counters()
            network_sent = network.bytes_sent
            network_recv = network.bytes_recv
            
            # I/O do disco
            disk_io = psutil.disk_io_counters()
            disk_read = disk_io.read_bytes if disk_io else 0
            disk_write = disk_io.write_bytes if disk_io else 0
            
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network_sent=network_sent,
                network_recv=network_recv,
                disk_read=disk_read,
                disk_write=disk_write
            )
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                network_sent=0.0,
                network_recv=0.0,
                disk_read=0.0,
                disk_write=0.0
            )
    
    async def _collect_application_metrics(self) -> ApplicationMetrics:
        """Coleta métricas da aplicação"""
        try:
            # Métricas básicas (simuladas para demonstração)
            response_time = await self._measure_response_time()
            error_rate = await self._measure_error_rate()
            throughput = await self._measure_throughput()
            availability = await self._measure_availability()
            active_connections = await self._count_active_connections()
            queue_size = await self._get_queue_size()
            
            # Métricas customizadas
            custom_metrics = await self._collect_custom_metrics()
            
            return ApplicationMetrics(
                timestamp=datetime.now(),
                response_time=response_time,
                error_rate=error_rate,
                throughput=throughput,
                availability=availability,
                active_connections=active_connections,
                queue_size=queue_size,
                custom_metrics=custom_metrics
            )
            
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
            return ApplicationMetrics(
                timestamp=datetime.now(),
                response_time=0.0,
                error_rate=0.0,
                throughput=0.0,
                availability=1.0,
                active_connections=0,
                queue_size=0,
                custom_metrics={}
            )
    
    async def _measure_response_time(self) -> float:
        """Mede tempo de resposta da aplicação"""
        try:
            # Simular medição de tempo de resposta
            # Em produção, isso seria uma chamada real para a aplicação
            start_time = time.time()
            await asyncio.sleep(0.01)  # Simular latência
            return time.time() - start_time
        except Exception:
            return 0.0
    
    async def _measure_error_rate(self) -> float:
        """Mede taxa de erro da aplicação"""
        try:
            # Simular medição de taxa de erro
            # Em produção, isso seria baseado em logs ou métricas reais
            return 0.01  # 1% de erro simulado
        except Exception:
            return 0.0
    
    async def _measure_throughput(self) -> float:
        """Mede throughput da aplicação"""
        try:
            # Simular medição de throughput
            # Em produção, isso seria baseado em métricas reais
            return 100.0  # 100 requests/s simulado
        except Exception:
            return 0.0
    
    async def _measure_availability(self) -> float:
        """Mede disponibilidade da aplicação"""
        try:
            # Simular verificação de disponibilidade
            # Em produção, isso seria um health check real
            return 0.99  # 99% de disponibilidade simulado
        except Exception:
            return 1.0
    
    async def _count_active_connections(self) -> int:
        """Conta conexões ativas"""
        try:
            # Simular contagem de conexões
            # Em produção, isso seria baseado em métricas reais
            return 50  # 50 conexões ativas simuladas
        except Exception:
            return 0
    
    async def _get_queue_size(self) -> int:
        """Obtém tamanho da fila"""
        try:
            # Simular tamanho da fila
            # Em produção, isso seria baseado em métricas reais
            return 10  # 10 itens na fila simulado
        except Exception:
            return 0
    
    async def _collect_custom_metrics(self) -> Dict[str, Any]:
        """Coleta métricas customizadas"""
        try:
            # Métricas customizadas específicas da aplicação
            return {
                "cache_hit_rate": 0.85,
                "database_connections": 20,
                "api_calls_per_minute": 1200,
                "memory_heap_usage": 0.6
            }
        except Exception:
            return {}
    
    def _calculate_impact_score(self, system_metrics: SystemMetrics, 
                               application_metrics: ApplicationMetrics) -> float:
        """Calcula score de impacto"""
        try:
            # Pesos para diferentes métricas
            weights = {
                'cpu': 0.2,
                'memory': 0.2,
                'error_rate': 0.3,
                'response_time': 0.2,
                'availability': 0.1
            }
            
            # Normalizar métricas
            cpu_impact = system_metrics.cpu_usage
            memory_impact = system_metrics.memory_usage
            error_impact = application_metrics.error_rate
            response_impact = min(application_metrics.response_time / 5.0, 1.0)  # Normalizar para 5s
            availability_impact = 1.0 - application_metrics.availability
            
            # Calcular score ponderado
            impact_score = (
                weights['cpu'] * cpu_impact +
                weights['memory'] * memory_impact +
                weights['error_rate'] * error_impact +
                weights['response_time'] * response_impact +
                weights['availability'] * availability_impact
            )
            
            return min(impact_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating impact score: {e}")
            return 0.0
    
    def _calculate_baseline_deviation(self, system_metrics: SystemMetrics,
                                     application_metrics: ApplicationMetrics) -> float:
        """Calcula desvio do baseline"""
        if not self.baseline_metrics:
            return 0.0
        
        try:
            # Calcular desvio para cada métrica
            cpu_deviation = abs(system_metrics.cpu_usage - self.baseline_metrics.system_metrics.cpu_usage)
            memory_deviation = abs(system_metrics.memory_usage - self.baseline_metrics.system_metrics.memory_usage)
            error_deviation = abs(application_metrics.error_rate - self.baseline_metrics.application_metrics.error_rate)
            response_deviation = abs(application_metrics.response_time - self.baseline_metrics.application_metrics.response_time)
            
            # Média ponderada dos desvios
            deviation = (cpu_deviation + memory_deviation + error_deviation + response_deviation) / 4.0
            
            return deviation
            
        except Exception as e:
            logger.error(f"Error calculating baseline deviation: {e}")
            return 0.0
    
    def _get_current_phase(self) -> str:
        """Obtém fase atual do experimento"""
        if not self.current_experiment:
            return "baseline"
        
        # Em produção, isso seria baseado no estado real do experimento
        return "chaos_injection"
    
    async def _check_alerts(self, metrics: ChaosMetrics) -> None:
        """Verifica e gera alertas"""
        try:
            alerts = []
            
            # Verificar thresholds de sistema
            if metrics.system_metrics.cpu_usage > self.config.cpu_threshold:
                alerts.append(self._create_alert(
                    MetricType.CPU_USAGE,
                    metrics.system_metrics.cpu_usage,
                    self.config.cpu_threshold,
                    AlertSeverity.WARNING,
                    f"CPU usage high: {metrics.system_metrics.cpu_usage:.2%}"
                ))
            
            if metrics.system_metrics.memory_usage > self.config.memory_threshold:
                alerts.append(self._create_alert(
                    MetricType.MEMORY_USAGE,
                    metrics.system_metrics.memory_usage,
                    self.config.memory_threshold,
                    AlertSeverity.WARNING,
                    f"Memory usage high: {metrics.system_metrics.memory_usage:.2%}"
                ))
            
            if metrics.system_metrics.disk_usage > self.config.disk_threshold:
                alerts.append(self._create_alert(
                    MetricType.DISK_USAGE,
                    metrics.system_metrics.disk_usage,
                    self.config.disk_threshold,
                    AlertSeverity.ERROR,
                    f"Disk usage critical: {metrics.system_metrics.disk_usage:.2%}"
                ))
            
            # Verificar thresholds de aplicação
            if metrics.application_metrics.error_rate > self.config.error_rate_threshold:
                alerts.append(self._create_alert(
                    MetricType.ERROR_RATE,
                    metrics.application_metrics.error_rate,
                    self.config.error_rate_threshold,
                    AlertSeverity.ERROR,
                    f"Error rate high: {metrics.application_metrics.error_rate:.2%}"
                ))
            
            if metrics.application_metrics.response_time > self.config.response_time_threshold:
                alerts.append(self._create_alert(
                    MetricType.RESPONSE_TIME,
                    metrics.application_metrics.response_time,
                    self.config.response_time_threshold,
                    AlertSeverity.WARNING,
                    f"Response time slow: {metrics.application_metrics.response_time:.2f}s"
                ))
            
            if metrics.application_metrics.availability < self.config.availability_threshold:
                alerts.append(self._create_alert(
                    MetricType.AVAILABILITY,
                    metrics.application_metrics.availability,
                    self.config.availability_threshold,
                    AlertSeverity.CRITICAL,
                    f"Availability low: {metrics.application_metrics.availability:.2%}"
                ))
            
            # Adicionar alertas
            for alert in alerts:
                self._add_alert(alert)
                
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
    
    def _create_alert(self, metric_type: MetricType, value: float, threshold: float,
                     severity: AlertSeverity, message: str) -> Alert:
        """Cria um novo alerta"""
        return Alert(
            id=f"alert_{int(time.time())}_{metric_type.value}",
            timestamp=datetime.now(),
            severity=severity,
            metric_type=metric_type,
            metric_value=value,
            threshold=threshold,
            message=message,
            experiment_id=self.current_experiment
        )
    
    def _add_alert(self, alert: Alert) -> None:
        """Adiciona alerta ao sistema"""
        with self.lock:
            self.alerts[alert.id] = alert
            self.stats['alerts_generated'] += 1
        
        # Notificar callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
    
    async def _notify_callbacks(self, metrics: ChaosMetrics) -> None:
        """Notifica callbacks de métricas"""
        for callback in self.metrics_callbacks:
            try:
                callback(metrics)
            except Exception as e:
                logger.error(f"Error in metrics callback: {e}")
    
    def set_baseline(self, metrics: ChaosMetrics) -> None:
        """Define baseline para comparação"""
        with self.lock:
            self.baseline_metrics = metrics
        logger.info("Baseline metrics set")
    
    def set_current_experiment(self, experiment_id: str) -> None:
        """Define experimento atual"""
        with self.lock:
            self.current_experiment = experiment_id
            self.stats['experiments_monitored'] += 1
        logger.info(f"Current experiment set to: {experiment_id}")
    
    def clear_current_experiment(self) -> None:
        """Limpa experimento atual"""
        with self.lock:
            self.current_experiment = None
        logger.info("Current experiment cleared")
    
    def add_alert_callback(self, callback: Callable) -> None:
        """Adiciona callback para alertas"""
        self.alert_callbacks.append(callback)
    
    def add_metrics_callback(self, callback: Callable) -> None:
        """Adiciona callback para métricas"""
        self.metrics_callbacks.append(callback)
    
    def get_metrics(self, limit: Optional[int] = None) -> List[ChaosMetrics]:
        """Obtém métricas coletadas"""
        with self.lock:
            metrics = list(self.metrics_buffer)
            if limit:
                metrics = metrics[-limit:]
            return metrics
    
    def get_alerts(self, severity: Optional[AlertSeverity] = None, 
                  resolved: Optional[bool] = None) -> List[Alert]:
        """Obtém alertas"""
        with self.lock:
            alerts = list(self.alerts.values())
            
            if severity:
                alerts = [a for a in alerts if a.severity == severity]
            
            if resolved is not None:
                alerts = [a for a in alerts if a.resolved == resolved]
            
            return alerts
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve um alerta"""
        with self.lock:
            if alert_id in self.alerts:
                self.alerts[alert_id].resolved = True
                self.alerts[alert_id].resolved_at = datetime.now()
                return True
            return False
    
    def get_impact_analysis(self, experiment_id: str) -> Optional[ImpactAnalysis]:
        """Obtém análise de impacto de um experimento"""
        try:
            # Filtrar métricas do experimento
            experiment_metrics = [
                m for m in self.metrics_buffer
                if m.experiment_id == experiment_id
            ]
            
            if not experiment_metrics:
                return None
            
            # Calcular métricas de impacto
            max_cpu_impact = max(m.system_metrics.cpu_usage for m in experiment_metrics)
            max_memory_impact = max(m.system_metrics.memory_usage for m in experiment_metrics)
            max_error_rate_impact = max(m.application_metrics.error_rate for m in experiment_metrics)
            max_response_time_impact = max(m.application_metrics.response_time for m in experiment_metrics)
            
            # Calcular impacto na disponibilidade
            min_availability = min(m.application_metrics.availability for m in experiment_metrics)
            availability_impact = 1.0 - min_availability
            
            # Análise de recuperação
            recovery_time = self._calculate_recovery_time(experiment_metrics)
            recovery_successful = recovery_time is not None
            
            # Calcular desvio do baseline
            baseline_deviation = sum(m.baseline_deviation for m in experiment_metrics) / len(experiment_metrics)
            
            # Classificar nível de impacto
            impact_level = self._classify_impact_level(
                max_cpu_impact, max_memory_impact, max_error_rate_impact,
                max_response_time_impact, availability_impact
            )
            
            # Gerar recomendações
            recommendations = self._generate_recommendations(
                max_cpu_impact, max_memory_impact, max_error_rate_impact,
                max_response_time_impact, availability_impact
            )
            
            return ImpactAnalysis(
                experiment_id=experiment_id,
                start_time=experiment_metrics[0].timestamp,
                end_time=experiment_metrics[-1].timestamp,
                duration=(experiment_metrics[-1].timestamp - experiment_metrics[0].timestamp).total_seconds(),
                max_cpu_impact=max_cpu_impact,
                max_memory_impact=max_memory_impact,
                max_error_rate_impact=max_error_rate_impact,
                max_response_time_impact=max_response_time_impact,
                availability_impact=availability_impact,
                recovery_time=recovery_time,
                recovery_successful=recovery_successful,
                baseline_deviation=baseline_deviation,
                impact_level=impact_level,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error generating impact analysis: {e}")
            return None
    
    def _calculate_recovery_time(self, metrics: List[ChaosMetrics]) -> Optional[float]:
        """Calcula tempo de recuperação"""
        try:
            if not self.baseline_metrics:
                return None
            
            # Encontrar quando o sistema se recuperou
            for i, metric in enumerate(metrics):
                if (abs(metric.system_metrics.cpu_usage - self.baseline_metrics.system_metrics.cpu_usage) < 0.05 and
                    abs(metric.application_metrics.error_rate - self.baseline_metrics.application_metrics.error_rate) < 0.01):
                    
                    recovery_time = (metric.timestamp - metrics[0].timestamp).total_seconds()
                    return recovery_time
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating recovery time: {e}")
            return None
    
    def _classify_impact_level(self, cpu_impact: float, memory_impact: float,
                              error_impact: float, response_impact: float,
                              availability_impact: float) -> str:
        """Classifica nível de impacto"""
        # Calcular score de impacto
        impact_score = (cpu_impact + memory_impact + error_impact + response_impact + availability_impact) / 5.0
        
        if impact_score < 0.2:
            return "low"
        elif impact_score < 0.5:
            return "medium"
        elif impact_score < 0.8:
            return "high"
        else:
            return "critical"
    
    def _generate_recommendations(self, cpu_impact: float, memory_impact: float,
                                 error_impact: float, response_impact: float,
                                 availability_impact: float) -> List[str]:
        """Gera recomendações baseadas no impacto"""
        recommendations = []
        
        if cpu_impact > 0.8:
            recommendations.append("Considerar escalabilidade horizontal para reduzir carga de CPU")
        
        if memory_impact > 0.8:
            recommendations.append("Otimizar uso de memória e implementar garbage collection")
        
        if error_impact > 0.1:
            recommendations.append("Implementar circuit breakers e estratégias de retry")
        
        if response_impact > 3.0:
            recommendations.append("Otimizar queries e implementar cache")
        
        if availability_impact > 0.1:
            recommendations.append("Implementar health checks e redundância de serviços")
        
        return recommendations
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas do monitoramento"""
        with self.lock:
            return {
                'metrics_collected': self.stats['metrics_collected'],
                'alerts_generated': self.stats['alerts_generated'],
                'experiments_monitored': self.stats['experiments_monitored'],
                'total_monitoring_time': self.stats['total_monitoring_time'],
                'current_buffer_size': len(self.metrics_buffer),
                'active_alerts': len([a for a in self.alerts.values() if not a.resolved]),
                'current_experiment': self.current_experiment
            }
    
    def export_metrics(self, format: str = "json") -> str:
        """Exporta métricas"""
        with self.lock:
            metrics_data = [asdict(m) for m in self.metrics_buffer]
            
            if format.lower() == "json":
                return json.dumps(metrics_data, indent=2, default=str)
            else:
                # Implementar outros formatos se necessário
                return str(metrics_data)
    
    def cleanup(self) -> None:
        """Limpa recursos"""
        self.stop_monitoring_flag = True
        logger.info("ChaosMonitor cleaned up")


# Função de conveniência para criar monitor
def create_chaos_monitor(config: Optional[MonitoringConfig] = None) -> ChaosMonitor:
    """Cria uma instância do chaos monitor"""
    return ChaosMonitor(config) 