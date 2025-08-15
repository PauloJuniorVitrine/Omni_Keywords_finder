"""
Sistema APM Completo - Omni Keywords Finder
==========================================

Sistema enterprise de Application Performance Monitoring com:
- Performance monitoring em tempo real
- Distributed tracing
- Error tracking
- User experience monitoring
- Database performance
- Custom metrics
- Real-time alerts

Prompt: CHECKLIST_SISTEMA_PREENCHIMENTO_LACUNAS.md - Fase 3
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-27
Versão: 1.0.0
Tracing ID: APM_SYSTEM_014
"""

import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import logging
from contextlib import contextmanager
import traceback
import psutil
import os

# Integração com plataforma centralizada
from infrastructure.observability.centralized_platform import (
    CentralizedObservabilityPlatform,
    CorrelationContext,
    EventType,
    Severity
)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APMMetricType(Enum):
    """Tipos de métricas APM"""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    DATABASE_QUERY = "database_query"
    EXTERNAL_CALL = "external_call"
    CUSTOM = "custom"


class APMErrorType(Enum):
    """Tipos de erros APM"""
    EXCEPTION = "exception"
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    VALIDATION_ERROR = "validation_error"
    BUSINESS_ERROR = "business_error"
    SYSTEM_ERROR = "system_error"


@dataclass
class APMMetric:
    """Métrica APM"""
    name: str
    value: float
    metric_type: APMMetricType
    timestamp: datetime
    labels: Dict[str, str]
    correlation_id: Optional[str] = None


@dataclass
class APMError:
    """Erro APM"""
    error_type: APMErrorType
    message: str
    stack_trace: Optional[str] = None
    timestamp: datetime
    correlation_id: Optional[str] = None
    context: Dict[str, Any]
    severity: Severity


@dataclass
class APMTransaction:
    """Transação APM"""
    transaction_id: str
    name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    status: str = "running"
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    tags: Dict[str, str]
    metrics: List[APMMetric]
    errors: List[APMError]


class APMSystem:
    """
    Sistema completo de APM
    """
    
    def __init__(self, platform: CentralizedObservabilityPlatform):
        self.platform = platform
        self.transactions: Dict[str, APMTransaction] = {}
        self.metrics_history: deque = deque(maxlen=10000)
        self.errors_history: deque = deque(maxlen=1000)
        self.performance_thresholds: Dict[str, Dict[str, float]] = {}
        
        # Thread para monitoramento de sistema
        self.system_monitor_thread = threading.Thread(target=self._monitor_system, daemon=True)
        self.system_monitor_thread.start()
        
        logger.info("Sistema APM inicializado")
    
    def start_transaction(
        self,
        name: str,
        correlation_context: CorrelationContext,
        user_id: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> str:
        """Iniciar transação APM"""
        transaction_id = f"txn_{int(time.time() * 1000000)}"
        
        transaction = APMTransaction(
            transaction_id=transaction_id,
            name=name,
            start_time=datetime.utcnow(),
            correlation_id=correlation_context.correlation_id,
            user_id=user_id,
            tags=tags or {},
            metrics=[],
            errors=[]
        )
        
        self.transactions[transaction_id] = transaction
        
        # Log da transação iniciada
        self.platform.log_event(
            event_type=EventType.TRACE,
            correlation_context=correlation_context,
            data={
                "transaction_id": transaction_id,
                "transaction_name": name,
                "action": "started"
            },
            severity=Severity.INFO,
            source="apm"
        )
        
        return transaction_id
    
    def end_transaction(
        self,
        transaction_id: str,
        status: str = "success",
        error: Optional[Exception] = None
    ):
        """Finalizar transação APM"""
        if transaction_id not in self.transactions:
            logger.warning(f"Transação não encontrada: {transaction_id}")
            return
        
        transaction = self.transactions[transaction_id]
        transaction.end_time = datetime.utcnow()
        transaction.duration = (transaction.end_time - transaction.start_time).total_seconds()
        transaction.status = status
        
        # Adicionar erro se houver
        if error:
            apm_error = APMError(
                error_type=APMErrorType.EXCEPTION,
                message=str(error),
                stack_trace=traceback.format_exc(),
                timestamp=datetime.utcnow(),
                correlation_id=transaction.correlation_id,
                context={"transaction_id": transaction_id},
                severity=Severity.ERROR
            )
            transaction.errors.append(apm_error)
            self.errors_history.append(apm_error)
        
        # Log da transação finalizada
        correlation_context = CorrelationContext(
            correlation_id=transaction.correlation_id or "unknown"
        )
        
        self.platform.log_event(
            event_type=EventType.TRACE,
            correlation_context=correlation_context,
            data={
                "transaction_id": transaction_id,
                "transaction_name": transaction.name,
                "duration": transaction.duration,
                "status": status,
                "action": "ended"
            },
            severity=Severity.INFO if status == "success" else Severity.ERROR,
            source="apm"
        )
        
        # Remover da memória após um tempo
        threading.Timer(300, lambda: self._cleanup_transaction(transaction_id)).start()
    
    def add_metric(
        self,
        transaction_id: str,
        name: str,
        value: float,
        metric_type: APMMetricType,
        labels: Optional[Dict[str, str]] = None
    ):
        """Adicionar métrica à transação"""
        if transaction_id not in self.transactions:
            logger.warning(f"Transação não encontrada: {transaction_id}")
            return
        
        transaction = self.transactions[transaction_id]
        
        metric = APMMetric(
            name=name,
            value=value,
            metric_type=metric_type,
            timestamp=datetime.utcnow(),
            labels=labels or {},
            correlation_id=transaction.correlation_id
        )
        
        transaction.metrics.append(metric)
        self.metrics_history.append(metric)
        
        # Log da métrica
        correlation_context = CorrelationContext(
            correlation_id=transaction.correlation_id or "unknown"
        )
        
        self.platform.log_event(
            event_type=EventType.METRIC,
            correlation_context=correlation_context,
            data={
                "metric_name": name,
                "value": value,
                "metric_type": metric_type.value,
                "labels": labels or {},
                "transaction_id": transaction_id
            },
            severity=Severity.INFO,
            source="apm"
        )
    
    def add_error(
        self,
        transaction_id: str,
        error_type: APMErrorType,
        message: str,
        exception: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """Adicionar erro à transação"""
        if transaction_id not in self.transactions:
            logger.warning(f"Transação não encontrada: {transaction_id}")
            return
        
        transaction = self.transactions[transaction_id]
        
        apm_error = APMError(
            error_type=error_type,
            message=message,
            stack_trace=traceback.format_exc() if exception else None,
            timestamp=datetime.utcnow(),
            correlation_id=transaction.correlation_id,
            context=context or {},
            severity=Severity.ERROR
        )
        
        transaction.errors.append(apm_error)
        self.errors_history.append(apm_error)
        
        # Log do erro
        correlation_context = CorrelationContext(
            correlation_id=transaction.correlation_id or "unknown"
        )
        
        self.platform.log_event(
            event_type=EventType.ALERT,
            correlation_context=correlation_context,
            data={
                "error_type": error_type.value,
                "message": message,
                "transaction_id": transaction_id,
                "context": context or {}
            },
            severity=Severity.ERROR,
            source="apm"
        )
    
    def set_performance_threshold(
        self,
        metric_name: str,
        warning_threshold: float,
        error_threshold: float,
        critical_threshold: float
    ):
        """Definir thresholds de performance"""
        self.performance_thresholds[metric_name] = {
            "warning": warning_threshold,
            "error": error_threshold,
            "critical": critical_threshold
        }
    
    def get_transaction_summary(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Obter resumo da transação"""
        if transaction_id not in self.transactions:
            return None
        
        transaction = self.transactions[transaction_id]
        
        return {
            "transaction_id": transaction_id,
            "name": transaction.name,
            "start_time": transaction.start_time.isoformat(),
            "end_time": transaction.end_time.isoformat() if transaction.end_time else None,
            "duration": transaction.duration,
            "status": transaction.status,
            "user_id": transaction.user_id,
            "tags": transaction.tags,
            "metrics_count": len(transaction.metrics),
            "errors_count": len(transaction.errors),
            "correlation_id": transaction.correlation_id
        }
    
    def get_performance_metrics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Obter métricas de performance agregadas"""
        start_time = start_time or datetime.utcnow() - timedelta(hours=1)
        end_time = end_time or datetime.utcnow()
        
        # Filtrar métricas por período
        recent_metrics = [
            m for m in self.metrics_history
            if start_time <= m.timestamp <= end_time
        ]
        
        # Agregar por tipo
        aggregated = defaultdict(list)
        for metric in recent_metrics:
            aggregated[metric.metric_type.value].append(metric.value)
        
        # Calcular estatísticas
        result = {}
        for metric_type, values in aggregated.items():
            if values:
                result[metric_type] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "p95": sorted(values)[int(len(values) * 0.95)],
                    "p99": sorted(values)[int(len(values) * 0.99)]
                }
        
        return result
    
    def get_error_summary(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Obter resumo de erros"""
        start_time = start_time or datetime.utcnow() - timedelta(hours=1)
        end_time = end_time or datetime.utcnow()
        
        # Filtrar erros por período
        recent_errors = [
            e for e in self.errors_history
            if start_time <= e.timestamp <= end_time
        ]
        
        # Agregar por tipo
        error_counts = defaultdict(int)
        for error in recent_errors:
            error_counts[error.error_type.value] += 1
        
        return {
            "total_errors": len(recent_errors),
            "error_types": dict(error_counts),
            "error_rate": len(recent_errors) / 3600  # erros por hora
        }
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Obter dados para dashboard APM"""
        now = datetime.utcnow()
        last_hour = now - timedelta(hours=1)
        
        # Métricas de performance
        performance_metrics = self.get_performance_metrics(last_hour, now)
        
        # Resumo de erros
        error_summary = self.get_error_summary(last_hour, now)
        
        # Transações ativas
        active_transactions = [
            t for t in self.transactions.values()
            if t.status == "running"
        ]
        
        # Métricas de sistema
        system_metrics = self._get_system_metrics()
        
        return {
            "timestamp": now.isoformat(),
            "performance_metrics": performance_metrics,
            "error_summary": error_summary,
            "active_transactions_count": len(active_transactions),
            "total_transactions": len(self.transactions),
            "system_metrics": system_metrics,
            "alerts": self._check_performance_alerts()
        }
    
    def _monitor_system(self):
        """Monitorar métricas do sistema"""
        while True:
            try:
                # Métricas de sistema
                system_metrics = self._get_system_metrics()
                
                # Log das métricas
                correlation_context = CorrelationContext(correlation_id="system_monitor")
                
                for metric_name, value in system_metrics.items():
                    self.platform.log_event(
                        event_type=EventType.METRIC,
                        correlation_context=correlation_context,
                        data={
                            "metric_name": metric_name,
                            "value": value,
                            "metric_type": "system"
                        },
                        severity=Severity.INFO,
                        source="apm_system"
                    )
                
                time.sleep(60)  # Monitorar a cada minuto
                
            except Exception as e:
                logger.error(f"Erro no monitoramento do sistema: {e}")
                time.sleep(60)
    
    def _get_system_metrics(self) -> Dict[str, float]:
        """Obter métricas do sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memória
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Processo atual
            process = psutil.Process(os.getpid())
            process_memory = process.memory_info().rss / 1024 / 1024  # MB
            process_cpu = process.cpu_percent()
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent,
                "process_memory_mb": process_memory,
                "process_cpu_percent": process_cpu
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter métricas do sistema: {e}")
            return {}
    
    def _check_performance_alerts(self) -> List[Dict[str, Any]]:
        """Verificar alertas de performance"""
        alerts = []
        
        for metric_name, thresholds in self.performance_thresholds.items():
            # Buscar métrica mais recente
            recent_metrics = [
                m for m in self.metrics_history
                if m.name == metric_name
                and m.timestamp > datetime.utcnow() - timedelta(minutes=5)
            ]
            
            if recent_metrics:
                latest_value = recent_metrics[-1].value
                
                if latest_value >= thresholds["critical"]:
                    alerts.append({
                        "metric_name": metric_name,
                        "value": latest_value,
                        "threshold": thresholds["critical"],
                        "severity": "critical"
                    })
                elif latest_value >= thresholds["error"]:
                    alerts.append({
                        "metric_name": metric_name,
                        "value": latest_value,
                        "threshold": thresholds["error"],
                        "severity": "error"
                    })
                elif latest_value >= thresholds["warning"]:
                    alerts.append({
                        "metric_name": metric_name,
                        "value": latest_value,
                        "threshold": thresholds["warning"],
                        "severity": "warning"
                    })
        
        return alerts
    
    def _cleanup_transaction(self, transaction_id: str):
        """Limpar transação da memória"""
        if transaction_id in self.transactions:
            del self.transactions[transaction_id]


@contextmanager
def apm_transaction(
    apm: APMSystem,
    name: str,
    correlation_context: CorrelationContext,
    user_id: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None
):
    """Context manager para transação APM"""
    transaction_id = apm.start_transaction(name, correlation_context, user_id, tags)
    
    try:
        yield transaction_id
        apm.end_transaction(transaction_id, "success")
    except Exception as e:
        apm.end_transaction(transaction_id, "error", e)
        raise


# Instância global do APM
_apm = None

def get_apm() -> APMSystem:
    """Obter instância do sistema APM"""
    global _apm
    if _apm is None:
        platform = CentralizedObservabilityPlatform()
        _apm = APMSystem(platform)
    return _apm


# Decorator para APM
def apm_monitor(
    name: Optional[str] = None,
    user_id: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None
):
    """Decorator para monitorar função com APM"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            apm = get_apm()
            
            # Gerar correlation context
            correlation_context = CorrelationContext(
                correlation_id=apm.platform.generate_correlation_id(),
                service_name="function",
                operation_name=name or func.__name__
            )
            
            with apm_transaction(apm, name or func.__name__, correlation_context, user_id, tags) as transaction_id:
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    
                    # Adicionar métrica de duração
                    duration = time.time() - start_time
                    apm.add_metric(
                        transaction_id,
                        "function_duration",
                        duration,
                        APMMetricType.RESPONSE_TIME,
                        {"function": func.__name__}
                    )
                    
                    return result
                    
                except Exception as e:
                    # Adicionar erro
                    apm.add_error(
                        transaction_id,
                        APMErrorType.EXCEPTION,
                        str(e),
                        e,
                        {"function": func.__name__}
                    )
                    raise
        
        return wrapper
    return decorator


# Exemplo de uso
if __name__ == "__main__":
    apm = get_apm()
    
    # Definir thresholds
    apm.set_performance_threshold("function_duration", 1.0, 5.0, 10.0)
    
    # Exemplo de função monitorada
    @apm_monitor(name="example_function", tags={"service": "example"})
    def example_function():
        time.sleep(0.1)  # Simular trabalho
        return "success"
    
    # Executar função
    result = example_function()
    print(f"Resultado: {result}")
    
    # Dashboard data
    dashboard_data = apm.get_dashboard_data()
    print(f"Dados do dashboard APM: {json.dumps(dashboard_data, indent=2, default=str)}") 