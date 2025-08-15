"""
Plataforma Centralizada de Observabilidade - Omni Keywords Finder
================================================================

Sistema enterprise para centralização de observabilidade com:
- Unificação de logs, métricas e traces
- Correlation IDs automáticos
- Dashboard centralizado
- Análise correlacionada
- APM integrado
- Detecção de anomalias

Prompt: CHECKLIST_SISTEMA_PREENCHIMENTO_LACUNAS.md - Fase 3
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-27
Versão: 1.0.0
Tracing ID: CENTRALIZED_OBSERVABILITY_014
"""

import uuid
import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import logging
from contextlib import contextmanager

# Integração com sistemas existentes
from infrastructure.monitoring.observability_complete import ObservabilityManager
from infrastructure.monitoring.performance_monitor import PerformanceMonitor

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventType(Enum):
    """Tipos de eventos observáveis"""
    LOG = "log"
    METRIC = "metric"
    TRACE = "trace"
    ALERT = "alert"
    BUSINESS = "business"
    SECURITY = "security"
    PERFORMANCE = "performance"


class Severity(Enum):
    """Níveis de severidade"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class CorrelationContext:
    """Contexto de correlação"""
    correlation_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None
    service_name: Optional[str] = None
    operation_name: Optional[str] = None
    timestamp: Optional[datetime] = None


@dataclass
class ObservabilityEvent:
    """Evento de observabilidade"""
    event_id: str
    event_type: EventType
    correlation_context: CorrelationContext
    data: Dict[str, Any]
    severity: Severity
    timestamp: datetime
    source: str
    tags: Dict[str, str]


class CentralizedObservabilityPlatform:
    """
    Plataforma centralizada de observabilidade
    """
    
    def __init__(self):
        self.events: deque = deque(maxlen=10000)
        self.correlation_map: Dict[str, List[str]] = defaultdict(list)
        self.anomaly_detectors: Dict[str, 'AnomalyDetector'] = {}
        self.performance_monitor = PerformanceMonitor()
        self.observability_manager = ObservabilityManager()
        
        # Thread para processamento assíncrono
        self.processing_thread = threading.Thread(target=self._process_events, daemon=True)
        self.processing_thread.start()
        
        logger.info("Plataforma centralizada de observabilidade inicializada")
    
    def generate_correlation_id(self) -> str:
        """Gerar ID de correlação único"""
        return str(uuid.uuid4())
    
    def create_correlation_context(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        service_name: Optional[str] = None,
        operation_name: Optional[str] = None
    ) -> CorrelationContext:
        """Criar contexto de correlação"""
        return CorrelationContext(
            correlation_id=self.generate_correlation_id(),
            user_id=user_id,
            session_id=session_id,
            request_id=request_id,
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            service_name=service_name,
            operation_name=operation_name,
            timestamp=datetime.utcnow()
        )
    
    def log_event(
        self,
        event_type: EventType,
        correlation_context: CorrelationContext,
        data: Dict[str, Any],
        severity: Severity = Severity.INFO,
        source: str = "unknown",
        tags: Optional[Dict[str, str]] = None
    ) -> str:
        """Registrar evento na plataforma centralizada"""
        event_id = str(uuid.uuid4())
        
        event = ObservabilityEvent(
            event_id=event_id,
            event_type=event_type,
            correlation_context=correlation_context,
            data=data,
            severity=severity,
            timestamp=datetime.utcnow(),
            source=source,
            tags=tags or {}
        )
        
        # Adicionar à fila de eventos
        self.events.append(event)
        
        # Mapear correlação
        self.correlation_map[correlation_context.correlation_id].append(event_id)
        
        # Detectar anomalias se aplicável
        if event_type in [EventType.METRIC, EventType.PERFORMANCE]:
            self._detect_anomalies(event)
        
        logger.debug(f"Evento registrado: {event_id} - {event_type.value}")
        return event_id
    
    def log_api_request(
        self,
        correlation_context: CorrelationContext,
        method: str,
        path: str,
        status_code: int,
        duration: float,
        user_id: Optional[str] = None,
        request_size: Optional[int] = None,
        response_size: Optional[int] = None
    ):
        """Log de requisição API"""
        data = {
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration": duration,
            "user_id": user_id,
            "request_size": request_size,
            "response_size": response_size
        }
        
        # Log como evento de performance
        self.log_event(
            event_type=EventType.PERFORMANCE,
            correlation_context=correlation_context,
            data=data,
            severity=Severity.INFO if status_code < 400 else Severity.ERROR,
            source="api",
            tags={"endpoint": path, "method": method}
        )
        
        # Métrica de latência
        self.log_event(
            event_type=EventType.METRIC,
            correlation_context=correlation_context,
            data={
                "metric_name": "api_request_duration_seconds",
                "value": duration,
                "labels": {"method": method, "path": path, "status_code": str(status_code)}
            },
            severity=Severity.INFO,
            source="api"
        )
    
    def log_business_event(
        self,
        correlation_context: CorrelationContext,
        event_name: str,
        user_id: str,
        business_data: Dict[str, Any]
    ):
        """Log de evento de negócio"""
        data = {
            "event_name": event_name,
            "user_id": user_id,
            "business_data": business_data
        }
        
        self.log_event(
            event_type=EventType.BUSINESS,
            correlation_context=correlation_context,
            data=data,
            severity=Severity.INFO,
            source="business",
            tags={"event_name": event_name}
        )
    
    def log_security_event(
        self,
        correlation_context: CorrelationContext,
        event_name: str,
        severity: Severity,
        security_data: Dict[str, Any]
    ):
        """Log de evento de segurança"""
        data = {
            "event_name": event_name,
            "security_data": security_data
        }
        
        self.log_event(
            event_type=EventType.SECURITY,
            correlation_context=correlation_context,
            data=data,
            severity=severity,
            source="security",
            tags={"event_name": event_name}
        )
    
    def get_correlated_events(self, correlation_id: str) -> List[ObservabilityEvent]:
        """Obter eventos correlacionados"""
        event_ids = self.correlation_map.get(correlation_id, [])
        return [event for event in self.events if event.event_id in event_ids]
    
    def get_events_by_type(
        self,
        event_type: EventType,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[ObservabilityEvent]:
        """Obter eventos por tipo"""
        start_time = start_time or datetime.utcnow() - timedelta(hours=1)
        end_time = end_time or datetime.utcnow()
        
        return [
            event for event in self.events
            if event.event_type == event_type
            and start_time <= event.timestamp <= end_time
        ]
    
    def get_events_by_severity(
        self,
        severity: Severity,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[ObservabilityEvent]:
        """Obter eventos por severidade"""
        start_time = start_time or datetime.utcnow() - timedelta(hours=1)
        end_time = end_time or datetime.utcnow()
        
        return [
            event for event in self.events
            if event.severity == severity
            and start_time <= event.timestamp <= end_time
        ]
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Obter dados para dashboard centralizado"""
        now = datetime.utcnow()
        last_hour = now - timedelta(hours=1)
        
        # Estatísticas por tipo de evento
        event_stats = defaultdict(int)
        for event in self.events:
            if event.timestamp >= last_hour:
                event_stats[event.event_type.value] += 1
        
        # Estatísticas por severidade
        severity_stats = defaultdict(int)
        for event in self.events:
            if event.timestamp >= last_hour:
                severity_stats[event.severity.value] += 1
        
        # Eventos críticos recentes
        critical_events = self.get_events_by_severity(Severity.CRITICAL, last_hour, now)
        
        # Performance metrics
        performance_events = self.get_events_by_type(EventType.PERFORMANCE, last_hour, now)
        avg_response_time = 0
        if performance_events:
            avg_response_time = sum(
                event.data.get("duration", 0) for event in performance_events
            ) / len(performance_events)
        
        return {
            "timestamp": now.isoformat(),
            "event_stats": dict(event_stats),
            "severity_stats": dict(severity_stats),
            "critical_events_count": len(critical_events),
            "avg_response_time": avg_response_time,
            "total_events_last_hour": len([e for e in self.events if e.timestamp >= last_hour]),
            "correlation_count": len(self.correlation_map),
            "anomalies_detected": len([e for e in self.events if "anomaly" in e.tags])
        }
    
    def _detect_anomalies(self, event: ObservabilityEvent):
        """Detectar anomalias em eventos"""
        if event.event_type == EventType.METRIC:
            metric_name = event.data.get("metric_name")
            value = event.data.get("value")
            
            if metric_name and value is not None:
                if metric_name not in self.anomaly_detectors:
                    self.anomaly_detectors[metric_name] = AnomalyDetector()
                
                detector = self.anomaly_detectors[metric_name]
                if detector.detect_anomaly(value):
                    # Marcar como anomalia
                    event.tags["anomaly"] = "true"
                    event.tags["anomaly_type"] = "metric_threshold"
                    
                    # Log da anomalia
                    logger.warning(f"Anomalia detectada: {metric_name} = {value}")
    
    def _process_events(self):
        """Processar eventos em background"""
        while True:
            try:
                # Processar eventos pendentes
                if self.events:
                    # Limpar eventos antigos (mais de 24h)
                    cutoff_time = datetime.utcnow() - timedelta(hours=24)
                    self.events = deque(
                        [e for e in self.events if e.timestamp > cutoff_time],
                        maxlen=10000
                    )
                
                time.sleep(60)  # Processar a cada minuto
                
            except Exception as e:
                logger.error(f"Erro no processamento de eventos: {e}")
                time.sleep(60)


class AnomalyDetector:
    """Detector de anomalias usando Isolation Forest"""
    
    def __init__(self, contamination: float = 0.1):
        self.contamination = contamination
        self.history = deque(maxlen=1000)
        self.model = None
        self.is_trained = False
    
    def detect_anomaly(self, value: float) -> bool:
        """Detectar se um valor é anômalo"""
        self.history.append(value)
        
        # Treinar modelo se tiver dados suficientes
        if len(self.history) >= 100 and not self.is_trained:
            try:
                from sklearn.ensemble import IsolationForest
                import numpy as np
                
                X = np.array(list(self.history)).reshape(-1, 1)
                self.model = IsolationForest(contamination=self.contamination)
                self.model.fit(X)
                self.is_trained = True
                
            except ImportError:
                # Fallback para detecção simples
                return self._simple_anomaly_detection(value)
        
        # Detectar anomalia
        if self.is_trained and self.model:
            try:
                import numpy as np
                prediction = self.model.predict([[value]])
                return prediction[0] == -1
            except:
                return self._simple_anomaly_detection(value)
        
        return self._simple_anomaly_detection(value)
    
    def _simple_anomaly_detection(self, value: float) -> bool:
        """Detecção simples de anomalia baseada em percentis"""
        if len(self.history) < 10:
            return False
        
        values = list(self.history)
        mean = sum(values) / len(values)
        std = (sum((x - mean) ** 2 for x in values) / len(values)) ** 0.5
        
        if std == 0:
            return False
        
        z_score = abs(value - mean) / std
        return z_score > 3  # 3 desvios padrão


class CorrelationMiddleware:
    """Middleware para adicionar correlation IDs automaticamente"""
    
    def __init__(self, platform: CentralizedObservabilityPlatform):
        self.platform = platform
    
    def __call__(self, request):
        """Middleware para Flask/FastAPI"""
        # Gerar correlation context
        correlation_context = self.platform.create_correlation_context(
            service_name="api",
            operation_name=f"{request.method} {request.path}"
        )
        
        # Adicionar ao contexto da requisição
        request.correlation_context = correlation_context
        
        # Adicionar header de resposta
        def add_correlation_header(response):
            response.headers['X-Correlation-ID'] = correlation_context.correlation_id
            return response
        
        return add_correlation_header


# Instância global da plataforma
_platform = None

def get_platform() -> CentralizedObservabilityPlatform:
    """Obter instância da plataforma centralizada"""
    global _platform
    if _platform is None:
        _platform = CentralizedObservabilityPlatform()
    return _platform


@contextmanager
def correlation_context(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    service_name: Optional[str] = None,
    operation_name: Optional[str] = None
):
    """Context manager para correlation context"""
    platform = get_platform()
    context = platform.create_correlation_context(
        user_id=user_id,
        session_id=session_id,
        service_name=service_name,
        operation_name=operation_name
    )
    
    try:
        yield context
    finally:
        pass


# Exemplo de uso
if __name__ == "__main__":
    platform = get_platform()
    
    # Exemplo de log de API
    with correlation_context(user_id="user123", service_name="api", operation_name="GET /keywords") as ctx:
        platform.log_api_request(
            correlation_context=ctx,
            method="GET",
            path="/api/keywords",
            status_code=200,
            duration=0.15,
            user_id="user123"
        )
    
    # Exemplo de log de negócio
    with correlation_context(user_id="user123", service_name="business") as ctx:
        platform.log_business_event(
            correlation_context=ctx,
            event_name="keyword_collected",
            user_id="user123",
            business_data={"keyword": "python", "source": "google"}
        )
    
    # Dashboard data
    dashboard_data = platform.get_dashboard_data()
    print(f"Dados do dashboard: {json.dumps(dashboard_data, indent=2, default=str)}") 