"""
Chaos Engineering Injection Monitor
==================================

Sistema de monitoramento de injeções de falhas para chaos engineering com:
- Tracking de impacto das injeções
- Análise de resultados em tempo real
- Métricas de performance durante injeções
- Alertas baseados em thresholds
- Relatórios de impacto detalhados

Author: Paulo Júnior
Date: 2025-01-27
Tracing ID: CHAOS_INJECTION_MONITOR_001_20250127
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
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MonitorStatus(Enum):
    """Status do monitor"""
    IDLE = "idle"
    MONITORING = "monitoring"
    ALERTING = "alerting"
    STOPPED = "stopped"


class ImpactLevel(Enum):
    """Níveis de impacto"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class InjectionMetrics:
    """Métricas de uma injeção"""
    injection_id: str
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_io: float
    network_io: float
    response_time: float
    error_rate: float
    throughput: float
    availability: float
    impact_score: float
    custom_metrics: Dict[str, Any]


@dataclass
class InjectionImpact:
    """Impacto de uma injeção"""
    injection_id: str
    start_time: datetime
    end_time: datetime
    duration: float
    
    # Métricas de impacto
    max_cpu_impact: float
    max_memory_impact: float
    max_disk_impact: float
    max_network_impact: float
    max_response_time_impact: float
    max_error_rate_impact: float
    min_availability: float
    
    # Análise de impacto
    impact_level: ImpactLevel
    recovery_time: Optional[float]
    baseline_deviation: float
    
    # Estatísticas
    avg_cpu_impact: float
    avg_memory_impact: float
    avg_error_rate_impact: float
    
    # Recomendações
    recommendations: List[str]
    issues_found: List[str]


class MonitorConfig(BaseModel):
    """Configuração do monitor"""
    enabled: bool = Field(True, description="Monitor habilitado")
    metrics_interval: int = Field(5, description="Intervalo de coleta em segundos")
    retention_period: int = Field(3600, description="Período de retenção em segundos")
    
    # Thresholds de alerta
    cpu_threshold: float = Field(0.8, description="Threshold de CPU (0-1)")
    memory_threshold: float = Field(0.8, description="Threshold de memória (0-1)")
    disk_threshold: float = Field(0.9, description="Threshold de disco (0-1)")
    error_rate_threshold: float = Field(0.1, description="Threshold de taxa de erro")
    response_time_threshold: float = Field(3.0, description="Threshold de tempo de resposta (s)")
    availability_threshold: float = Field(0.9, description="Threshold de disponibilidade")
    
    # Configurações de impacto
    impact_calculation_window: int = Field(60, description="Janela para cálculo de impacto (s)")
    baseline_window: int = Field(300, description="Janela para baseline (s)")
    recovery_timeout: int = Field(300, description="Timeout para recuperação (s)")
    
    # Configurações de alerta
    alert_on_high_impact: bool = Field(True, description="Alertar sobre impacto alto")
    alert_on_slow_recovery: bool = Field(True, description="Alertar sobre recuperação lenta")
    alert_on_baseline_deviation: bool = Field(True, description="Alertar sobre desvio do baseline")


class InjectionMonitor:
    """
    Monitor de injeções de falhas
    """
    
    def __init__(self, config: Optional[MonitorConfig] = None):
        self.config = config or MonitorConfig()
        self.status = MonitorStatus.IDLE
        self.monitoring_task: Optional[asyncio.Task] = None
        self.stop_monitoring_flag = False
        
        # Armazenamento de dados
        self.injection_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.baseline_metrics: Optional[InjectionMetrics] = None
        self.impact_analysis: Dict[str, InjectionImpact] = {}
        
        # Callbacks
        self.impact_callbacks: List[Callable] = []
        self.alert_callbacks: List[Callable] = []
        self.metrics_callbacks: List[Callable] = []
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Estatísticas
        self.stats = {
            'injections_monitored': 0,
            'metrics_collected': 0,
            'alerts_generated': 0,
            'impact_analyses': 0
        }
        
        logger.info("InjectionMonitor initialized")
    
    async def start_monitoring(self, injection_id: str) -> None:
        """Inicia monitoramento de uma injeção"""
        if self.status == MonitorStatus.MONITORING:
            logger.warning("Monitor already running")
            return
        
        self.status = MonitorStatus.MONITORING
        self.stop_monitoring_flag = False
        
        # Estabelecer baseline se não existir
        if not self.baseline_metrics:
            await self._establish_baseline()
        
        # Iniciar loop de monitoramento
        self.monitoring_task = asyncio.create_task(
            self._monitoring_loop(injection_id)
        )
        
        with self.lock:
            self.stats['injections_monitored'] += 1
        
        logger.info(f"Started monitoring injection: {injection_id}")
    
    async def stop_monitoring(self) -> None:
        """Para o monitoramento"""
        self.stop_monitoring_flag = True
        self.status = MonitorStatus.STOPPED
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Injection monitoring stopped")
    
    async def _monitoring_loop(self, injection_id: str) -> None:
        """Loop principal de monitoramento"""
        start_time = time.time()
        
        while not self.stop_monitoring_flag:
            try:
                # Coletar métricas
                metrics = await self._collect_metrics(injection_id)
                
                # Armazenar métricas
                with self.lock:
                    self.injection_metrics[injection_id].append(metrics)
                    self.stats['metrics_collected'] += 1
                
                # Verificar alertas
                await self._check_alerts(metrics)
                
                # Notificar callbacks
                await self._notify_callbacks(metrics)
                
                # Aguardar próximo ciclo
                await asyncio.sleep(self.config.metrics_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.config.metrics_interval)
        
        # Finalizar análise de impacto
        await self._finalize_impact_analysis(injection_id)
    
    async def _establish_baseline(self) -> None:
        """Estabelece baseline do sistema"""
        logger.info("Establishing system baseline")
        
        # Coletar métricas por alguns ciclos para estabelecer baseline
        baseline_metrics = []
        for _ in range(5):  # 5 ciclos
            metrics = await self._collect_system_metrics()
            baseline_metrics.append(metrics)
            await asyncio.sleep(self.config.metrics_interval)
        
        # Calcular média das métricas
        avg_cpu = sum(m['cpu_usage'] for m in baseline_metrics) / len(baseline_metrics)
        avg_memory = sum(m['memory_usage'] for m in baseline_metrics) / len(baseline_metrics)
        avg_disk = sum(m['disk_io'] for m in baseline_metrics) / len(baseline_metrics)
        avg_network = sum(m['network_io'] for m in baseline_metrics) / len(baseline_metrics)
        avg_response = sum(m['response_time'] for m in baseline_metrics) / len(baseline_metrics)
        avg_error_rate = sum(m['error_rate'] for m in baseline_metrics) / len(baseline_metrics)
        avg_throughput = sum(m['throughput'] for m in baseline_metrics) / len(baseline_metrics)
        avg_availability = sum(m['availability'] for m in baseline_metrics) / len(baseline_metrics)
        
        self.baseline_metrics = InjectionMetrics(
            injection_id="baseline",
            timestamp=datetime.now(),
            cpu_usage=avg_cpu,
            memory_usage=avg_memory,
            disk_io=avg_disk,
            network_io=avg_network,
            response_time=avg_response,
            error_rate=avg_error_rate,
            throughput=avg_throughput,
            availability=avg_availability,
            impact_score=0.0,
            custom_metrics={}
        )
        
        logger.info("System baseline established")
    
    async def _collect_metrics(self, injection_id: str) -> InjectionMetrics:
        """Coleta métricas do sistema"""
        timestamp = datetime.now()
        
        # Métricas do sistema
        system_metrics = await self._collect_system_metrics()
        
        # Métricas da aplicação
        app_metrics = await self._collect_application_metrics()
        
        # Calcular impacto
        impact_score = self._calculate_impact_score(system_metrics, app_metrics)
        
        # Métricas customizadas
        custom_metrics = await self._collect_custom_metrics()
        
        return InjectionMetrics(
            injection_id=injection_id,
            timestamp=timestamp,
            cpu_usage=system_metrics['cpu_usage'],
            memory_usage=system_metrics['memory_usage'],
            disk_io=system_metrics['disk_io'],
            network_io=system_metrics['network_io'],
            response_time=app_metrics['response_time'],
            error_rate=app_metrics['error_rate'],
            throughput=app_metrics['throughput'],
            availability=app_metrics['availability'],
            impact_score=impact_score,
            custom_metrics=custom_metrics
        )
    
    async def _collect_system_metrics(self) -> Dict[str, float]:
        """Coleta métricas do sistema"""
        try:
            # CPU
            cpu_usage = psutil.cpu_percent(interval=1) / 100.0
            
            # Memória
            memory = psutil.virtual_memory()
            memory_usage = memory.percent / 100.0
            
            # Disco I/O
            disk_io = psutil.disk_io_counters()
            disk_io_rate = (disk_io.read_bytes + disk_io.write_bytes) / (1024 * 1024) if disk_io else 0
            
            # Rede I/O
            network_io = psutil.net_io_counters()
            network_io_rate = (network_io.bytes_sent + network_io.bytes_recv) / (1024 * 1024)
            
            return {
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage,
                'disk_io': disk_io_rate,
                'network_io': network_io_rate
            }
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return {
                'cpu_usage': 0.0,
                'memory_usage': 0.0,
                'disk_io': 0.0,
                'network_io': 0.0
            }
    
    async def _collect_application_metrics(self) -> Dict[str, float]:
        """Coleta métricas da aplicação"""
        try:
            # Simular métricas da aplicação
            # Em produção, isso seria baseado em métricas reais
            response_time = await self._measure_response_time()
            error_rate = await self._measure_error_rate()
            throughput = await self._measure_throughput()
            availability = await self._measure_availability()
            
            return {
                'response_time': response_time,
                'error_rate': error_rate,
                'throughput': throughput,
                'availability': availability
            }
            
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
            return {
                'response_time': 0.0,
                'error_rate': 0.0,
                'throughput': 0.0,
                'availability': 1.0
            }
    
    async def _measure_response_time(self) -> float:
        """Mede tempo de resposta"""
        try:
            start_time = time.time()
            await asyncio.sleep(0.01)  # Simular latência
            return time.time() - start_time
        except Exception:
            return 0.0
    
    async def _measure_error_rate(self) -> float:
        """Mede taxa de erro"""
        try:
            # Simular taxa de erro
            return 0.02  # 2% de erro simulado
        except Exception:
            return 0.0
    
    async def _measure_throughput(self) -> float:
        """Mede throughput"""
        try:
            # Simular throughput
            return 150.0  # 150 requests/s simulado
        except Exception:
            return 0.0
    
    async def _measure_availability(self) -> float:
        """Mede disponibilidade"""
        try:
            # Simular disponibilidade
            return 0.98  # 98% de disponibilidade simulado
        except Exception:
            return 1.0
    
    async def _collect_custom_metrics(self) -> Dict[str, Any]:
        """Coleta métricas customizadas"""
        try:
            return {
                "cache_hit_rate": 0.85,
                "database_connections": 25,
                "queue_size": 15,
                "memory_heap_usage": 0.65
            }
        except Exception:
            return {}
    
    def _calculate_impact_score(self, system_metrics: Dict[str, float], 
                               app_metrics: Dict[str, float]) -> float:
        """Calcula score de impacto"""
        try:
            if not self.baseline_metrics:
                return 0.0
            
            # Calcular desvios do baseline
            cpu_deviation = abs(system_metrics['cpu_usage'] - self.baseline_metrics.cpu_usage)
            memory_deviation = abs(system_metrics['memory_usage'] - self.baseline_metrics.memory_usage)
            error_deviation = abs(app_metrics['error_rate'] - self.baseline_metrics.error_rate)
            response_deviation = abs(app_metrics['response_time'] - self.baseline_metrics.response_time)
            availability_deviation = abs(app_metrics['availability'] - self.baseline_metrics.availability)
            
            # Pesos para diferentes métricas
            weights = {
                'cpu': 0.2,
                'memory': 0.2,
                'error_rate': 0.3,
                'response_time': 0.2,
                'availability': 0.1
            }
            
            # Normalizar desvios
            normalized_cpu = min(cpu_deviation * 2, 1.0)  # Dobrar o impacto
            normalized_memory = min(memory_deviation * 2, 1.0)
            normalized_error = min(error_deviation * 10, 1.0)  # 10x o impacto
            normalized_response = min(response_deviation / 5.0, 1.0)  # Normalizar para 5s
            normalized_availability = availability_deviation
            
            # Calcular score ponderado
            impact_score = (
                weights['cpu'] * normalized_cpu +
                weights['memory'] * normalized_memory +
                weights['error_rate'] * normalized_error +
                weights['response_time'] * normalized_response +
                weights['availability'] * normalized_availability
            )
            
            return min(impact_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating impact score: {e}")
            return 0.0
    
    async def _check_alerts(self, metrics: InjectionMetrics) -> None:
        """Verifica e gera alertas"""
        try:
            alerts = []
            
            # Verificar thresholds
            if metrics.cpu_usage > self.config.cpu_threshold:
                alerts.append({
                    'type': 'high_cpu',
                    'value': metrics.cpu_usage,
                    'threshold': self.config.cpu_threshold,
                    'message': f"CPU usage high: {metrics.cpu_usage:.2%}"
                })
            
            if metrics.memory_usage > self.config.memory_threshold:
                alerts.append({
                    'type': 'high_memory',
                    'value': metrics.memory_usage,
                    'threshold': self.config.memory_threshold,
                    'message': f"Memory usage high: {metrics.memory_usage:.2%}"
                })
            
            if metrics.error_rate > self.config.error_rate_threshold:
                alerts.append({
                    'type': 'high_error_rate',
                    'value': metrics.error_rate,
                    'threshold': self.config.error_rate_threshold,
                    'message': f"Error rate high: {metrics.error_rate:.2%}"
                })
            
            if metrics.response_time > self.config.response_time_threshold:
                alerts.append({
                    'type': 'slow_response',
                    'value': metrics.response_time,
                    'threshold': self.config.response_time_threshold,
                    'message': f"Response time slow: {metrics.response_time:.2f}s"
                })
            
            if metrics.availability < self.config.availability_threshold:
                alerts.append({
                    'type': 'low_availability',
                    'value': metrics.availability,
                    'threshold': self.config.availability_threshold,
                    'message': f"Availability low: {metrics.availability:.2%}"
                })
            
            # Verificar impacto alto
            if self.config.alert_on_high_impact and metrics.impact_score > 0.7:
                alerts.append({
                    'type': 'high_impact',
                    'value': metrics.impact_score,
                    'threshold': 0.7,
                    'message': f"High impact detected: {metrics.impact_score:.2%}"
                })
            
            # Notificar alertas
            for alert in alerts:
                await self._notify_alert(alert, metrics)
                
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
    
    async def _notify_alert(self, alert: Dict[str, Any], metrics: InjectionMetrics) -> None:
        """Notifica sobre alerta"""
        with self.lock:
            self.stats['alerts_generated'] += 1
        
        # Notificar callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert, metrics)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
    
    async def _notify_callbacks(self, metrics: InjectionMetrics) -> None:
        """Notifica callbacks de métricas"""
        for callback in self.metrics_callbacks:
            try:
                callback(metrics)
            except Exception as e:
                logger.error(f"Error in metrics callback: {e}")
    
    async def _finalize_impact_analysis(self, injection_id: str) -> None:
        """Finaliza análise de impacto"""
        try:
            with self.lock:
                metrics_list = list(self.injection_metrics[injection_id])
            
            if not metrics_list:
                logger.warning(f"No metrics found for injection {injection_id}")
                return
            
            # Calcular métricas de impacto
            start_time = metrics_list[0].timestamp
            end_time = metrics_list[-1].timestamp
            duration = (end_time - start_time).total_seconds()
            
            # Máximos
            max_cpu_impact = max(m.cpu_usage for m in metrics_list)
            max_memory_impact = max(m.memory_usage for m in metrics_list)
            max_disk_impact = max(m.disk_io for m in metrics_list)
            max_network_impact = max(m.network_io for m in metrics_list)
            max_response_time_impact = max(m.response_time for m in metrics_list)
            max_error_rate_impact = max(m.error_rate for m in metrics_list)
            min_availability = min(m.availability for m in metrics_list)
            
            # Médias
            avg_cpu_impact = sum(m.cpu_usage for m in metrics_list) / len(metrics_list)
            avg_memory_impact = sum(m.memory_usage for m in metrics_list) / len(metrics_list)
            avg_error_rate_impact = sum(m.error_rate for m in metrics_list) / len(metrics_list)
            
            # Calcular desvio do baseline
            baseline_deviation = sum(m.impact_score for m in metrics_list) / len(metrics_list)
            
            # Calcular tempo de recuperação
            recovery_time = self._calculate_recovery_time(metrics_list)
            
            # Classificar nível de impacto
            impact_level = self._classify_impact_level(
                max_cpu_impact, max_memory_impact, max_error_rate_impact,
                max_response_time_impact, min_availability
            )
            
            # Gerar recomendações
            recommendations = self._generate_recommendations(
                max_cpu_impact, max_memory_impact, max_error_rate_impact,
                max_response_time_impact, min_availability
            )
            
            # Identificar problemas
            issues_found = self._identify_issues(
                max_cpu_impact, max_memory_impact, max_error_rate_impact,
                max_response_time_impact, min_availability
            )
            
            # Criar análise de impacto
            impact_analysis = InjectionImpact(
                injection_id=injection_id,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                max_cpu_impact=max_cpu_impact,
                max_memory_impact=max_memory_impact,
                max_disk_impact=max_disk_impact,
                max_network_impact=max_network_impact,
                max_response_time_impact=max_response_time_impact,
                max_error_rate_impact=max_error_rate_impact,
                min_availability=min_availability,
                impact_level=impact_level,
                recovery_time=recovery_time,
                baseline_deviation=baseline_deviation,
                avg_cpu_impact=avg_cpu_impact,
                avg_memory_impact=avg_memory_impact,
                avg_error_rate_impact=avg_error_rate_impact,
                recommendations=recommendations,
                issues_found=issues_found
            )
            
            # Armazenar análise
            with self.lock:
                self.impact_analysis[injection_id] = impact_analysis
                self.stats['impact_analyses'] += 1
            
            # Notificar callbacks de impacto
            for callback in self.impact_callbacks:
                try:
                    callback(impact_analysis)
                except Exception as e:
                    logger.error(f"Error in impact callback: {e}")
            
            logger.info(f"Impact analysis completed for injection {injection_id}")
            
        except Exception as e:
            logger.error(f"Error finalizing impact analysis: {e}")
    
    def _calculate_recovery_time(self, metrics_list: List[InjectionMetrics]) -> Optional[float]:
        """Calcula tempo de recuperação"""
        try:
            if not self.baseline_metrics:
                return None
            
            # Encontrar quando o sistema se recuperou
            for i, metrics in enumerate(metrics_list):
                if (abs(metrics.cpu_usage - self.baseline_metrics.cpu_usage) < 0.05 and
                    abs(metrics.error_rate - self.baseline_metrics.error_rate) < 0.01 and
                    abs(metrics.response_time - self.baseline_metrics.response_time) < 0.5):
                    
                    recovery_time = (metrics.timestamp - metrics_list[0].timestamp).total_seconds()
                    return recovery_time
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating recovery time: {e}")
            return None
    
    def _classify_impact_level(self, max_cpu: float, max_memory: float,
                              max_error_rate: float, max_response_time: float,
                              min_availability: float) -> ImpactLevel:
        """Classifica nível de impacto"""
        # Calcular score de impacto
        impact_score = (
            max_cpu + max_memory + max_error_rate + 
            min(max_response_time / 5.0, 1.0) + (1.0 - min_availability)
        ) / 5.0
        
        if impact_score < 0.2:
            return ImpactLevel.NONE
        elif impact_score < 0.4:
            return ImpactLevel.LOW
        elif impact_score < 0.6:
            return ImpactLevel.MEDIUM
        elif impact_score < 0.8:
            return ImpactLevel.HIGH
        else:
            return ImpactLevel.CRITICAL
    
    def _generate_recommendations(self, max_cpu: float, max_memory: float,
                                 max_error_rate: float, max_response_time: float,
                                 min_availability: float) -> List[str]:
        """Gera recomendações baseadas no impacto"""
        recommendations = []
        
        if max_cpu > 0.8:
            recommendations.append("Considerar escalabilidade horizontal para reduzir carga de CPU")
        
        if max_memory > 0.8:
            recommendations.append("Otimizar uso de memória e implementar garbage collection")
        
        if max_error_rate > 0.1:
            recommendations.append("Implementar circuit breakers e estratégias de retry")
        
        if max_response_time > 3.0:
            recommendations.append("Otimizar queries e implementar cache")
        
        if min_availability < 0.9:
            recommendations.append("Implementar health checks e redundância de serviços")
        
        return recommendations
    
    def _identify_issues(self, max_cpu: float, max_memory: float,
                        max_error_rate: float, max_response_time: float,
                        min_availability: float) -> List[str]:
        """Identifica problemas encontrados"""
        issues = []
        
        if max_cpu > 0.9:
            issues.append(f"CPU usage critically high: {max_cpu:.2%}")
        
        if max_memory > 0.9:
            issues.append(f"Memory usage critically high: {max_memory:.2%}")
        
        if max_error_rate > 0.2:
            issues.append(f"Error rate critically high: {max_error_rate:.2%}")
        
        if max_response_time > 5.0:
            issues.append(f"Response time critically slow: {max_response_time:.2f}s")
        
        if min_availability < 0.8:
            issues.append(f"Availability critically low: {min_availability:.2%}")
        
        return issues
    
    def add_impact_callback(self, callback: Callable) -> None:
        """Adiciona callback para análise de impacto"""
        self.impact_callbacks.append(callback)
    
    def add_alert_callback(self, callback: Callable) -> None:
        """Adiciona callback para alertas"""
        self.alert_callbacks.append(callback)
    
    def add_metrics_callback(self, callback: Callable) -> None:
        """Adiciona callback para métricas"""
        self.metrics_callbacks.append(callback)
    
    def get_metrics(self, injection_id: str, limit: Optional[int] = None) -> List[InjectionMetrics]:
        """Obtém métricas de uma injeção"""
        with self.lock:
            metrics = list(self.injection_metrics.get(injection_id, []))
            if limit:
                metrics = metrics[-limit:]
            return metrics
    
    def get_impact_analysis(self, injection_id: str) -> Optional[InjectionImpact]:
        """Obtém análise de impacto de uma injeção"""
        with self.lock:
            return self.impact_analysis.get(injection_id)
    
    def get_all_impact_analyses(self) -> List[InjectionImpact]:
        """Obtém todas as análises de impacto"""
        with self.lock:
            return list(self.impact_analysis.values())
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas do monitor"""
        with self.lock:
            return {
                'status': self.status.value,
                'injections_monitored': self.stats['injections_monitored'],
                'metrics_collected': self.stats['metrics_collected'],
                'alerts_generated': self.stats['alerts_generated'],
                'impact_analyses': self.stats['impact_analyses'],
                'active_injections': len(self.injection_metrics),
                'baseline_established': self.baseline_metrics is not None
            }
    
    def export_metrics(self, injection_id: str, format: str = "json") -> str:
        """Exporta métricas de uma injeção"""
        with self.lock:
            metrics = list(self.injection_metrics.get(injection_id, []))
            metrics_data = [asdict(m) for m in metrics]
            
            if format.lower() == "json":
                return json.dumps(metrics_data, indent=2, default=str)
            else:
                return str(metrics_data)
    
    def export_impact_analysis(self, injection_id: str, format: str = "json") -> str:
        """Exporta análise de impacto"""
        with self.lock:
            impact = self.impact_analysis.get(injection_id)
            if not impact:
                return "{}"
            
            impact_data = asdict(impact)
            
            if format.lower() == "json":
                return json.dumps(impact_data, indent=2, default=str)
            else:
                return str(impact_data)
    
    def cleanup(self) -> None:
        """Limpa recursos"""
        self.stop_monitoring_flag = True
        logger.info("InjectionMonitor cleaned up")


# Função de conveniência para criar monitor
def create_injection_monitor(config: Optional[MonitorConfig] = None) -> InjectionMonitor:
    """Cria uma instância do injection monitor"""
    return InjectionMonitor(config) 