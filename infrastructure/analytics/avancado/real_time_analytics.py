"""
Sistema de Analytics em Tempo Real
==================================

Este módulo implementa um sistema completo de analytics em tempo real para o Omni Keywords Finder,
fornecendo métricas avançadas, processamento de eventos e dashboards interativos.

Características:
- Processamento de eventos em tempo real
- Métricas de negócio avançadas
- Dashboards interativos
- Exportação de dados
- Integração com observabilidade

Autor: Paulo Júnior
Data: 2024-12-19
Tracing ID: ANALYTICS_001
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import threading
import logging
from enum import Enum

# Integração com observabilidade
from infrastructure.observability.telemetry import TelemetryManager
from infrastructure.observability.metrics import MetricsCollector
from infrastructure.observability.tracing import TracingManager

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventType(Enum):
    """Tipos de eventos suportados pelo sistema de analytics."""
    USER_LOGIN = "user_login"
    KEYWORD_SEARCH = "keyword_search"
    EXECUTION_START = "execution_start"
    EXECUTION_COMPLETE = "execution_complete"
    EXPORT_DATA = "export_data"
    ERROR_OCCURRED = "error_occurred"
    FEATURE_USAGE = "feature_usage"
    PERFORMANCE_METRIC = "performance_metric"


@dataclass
class AnalyticsEvent:
    """Estrutura de dados para eventos de analytics."""
    event_type: EventType
    user_id: Optional[str]
    session_id: str
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o evento para dicionário."""
        return {
            "event_type": self.event_type.value,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "metadata": self.metadata
        }


@dataclass
class RealTimeMetric:
    """Métrica em tempo real."""
    name: str
    value: Union[int, float]
    timestamp: datetime
    tags: Dict[str, str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a métrica para dicionário."""
        return {
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags
        }


class RealTimeAnalytics:
    """
    Sistema de analytics em tempo real com processamento de eventos
    e métricas avançadas.
    """
    
    def __init__(self, max_events: int = 10000, flush_interval: int = 60):
        """
        Inicializa o sistema de analytics.
        
        Args:
            max_events: Número máximo de eventos em memória
            flush_interval: Intervalo em segundos para flush dos dados
        """
        self.max_events = max_events
        self.flush_interval = flush_interval
        self.events = deque(maxlen=max_events)
        self.metrics = defaultdict(lambda: defaultdict(int))
        self.real_time_data = defaultdict(dict)
        self.lock = threading.RLock()
        self.running = False
        self.flush_thread = None
        
        # Métricas específicas
        self.user_sessions = defaultdict(set)
        self.feature_usage = defaultdict(int)
        self.error_counts = defaultdict(int)
        self.performance_metrics = defaultdict(list)
        
        logger.info(f"[ANALYTICS] Sistema inicializado - Max eventos: {max_events}, Flush: {flush_interval}string_data")
    
    def start(self):
        """Inicia o sistema de analytics."""
        if not self.running:
            self.running = True
            self.flush_thread = threading.Thread(target=self._flush_loop, daemon=True)
            self.flush_thread.start()
            logger.info("[ANALYTICS] Sistema iniciado com sucesso")
    
    def stop(self):
        """Para o sistema de analytics."""
        self.running = False
        if self.flush_thread:
            self.flush_thread.join(timeout=5)
        logger.info("[ANALYTICS] Sistema parado")
    
    def track_event(self, event: AnalyticsEvent):
        """
        Registra um evento no sistema de analytics.
        
        Args:
            event: Evento a ser registrado
        """
        with self.lock:
            self.events.append(event)
            self._process_event(event)
        
        logger.debug(f"[ANALYTICS] Evento registrado: {event.event_type.value}")
    
    def _process_event(self, event: AnalyticsEvent):
        """Processa um evento e atualiza métricas."""
        # Métricas gerais
        self.metrics["total_events"][event.event_type.value] += 1
        self.metrics["events_by_hour"][event.timestamp.strftime("%Y-%m-%data %H:00")] += 1
        
        # Sessões de usuário
        if event.user_id:
            self.user_sessions[event.user_id].add(event.session_id)
        
        # Uso de features
        if event.event_type == EventType.FEATURE_USAGE:
            feature = event.data.get("feature", "unknown")
            self.feature_usage[feature] += 1
        
        # Contagem de erros
        if event.event_type == EventType.ERROR_OCCURRED:
            error_type = event.data.get("error_type", "unknown")
            self.error_counts[error_type] += 1
        
        # Métricas de performance
        if event.event_type == EventType.PERFORMANCE_METRIC:
            metric_name = event.data.get("metric_name", "unknown")
            metric_value = event.data.get("value", 0)
            self.performance_metrics[metric_name].append(metric_value)
            
            # Manter apenas os últimos 100 valores
            if len(self.performance_metrics[metric_name]) > 100:
                self.performance_metrics[metric_name] = self.performance_metrics[metric_name][-100:]
    
    def _flush_loop(self):
        """Loop de flush dos dados para persistência."""
        while self.running:
            time.sleep(self.flush_interval)
            self._flush_data()
    
    def _flush_data(self):
        """Flush dos dados para persistência."""
        try:
            with self.lock:
                # Aqui você pode implementar persistência em banco de dados
                # Por enquanto, apenas logamos as métricas
                logger.info(f"[ANALYTICS] Flush - Total eventos: {len(self.events)}")
                logger.info(f"[ANALYTICS] Flush - Usuários ativos: {len(self.user_sessions)}")
                logger.info(f"[ANALYTICS] Flush - Features mais usadas: {dict(sorted(self.feature_usage.items(), key=lambda value: value[1], reverse=True)[:5])}")
        except Exception as e:
            logger.error(f"[ANALYTICS] Erro no flush: {e}")
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """
        Retorna métricas em tempo real.
        
        Returns:
            Dicionário com métricas atualizadas
        """
        with self.lock:
            now = datetime.now()
            last_hour = now - timedelta(hours=1)
            
            # Eventos da última hora
            recent_events = [
                event for event in self.events 
                if event.timestamp >= last_hour
            ]
            
            # Usuários ativos (última hora)
            active_users = len([
                user_id for user_id, sessions in self.user_sessions.items()
                if any(event.timestamp >= last_hour for event in self.events if event.user_id == user_id)
            ])
            
            # Performance média
            avg_performance = {}
            for metric_name, values in self.performance_metrics.items():
                if values:
                    avg_performance[metric_name] = sum(values) / len(values)
            
            return {
                "timestamp": now.isoformat(),
                "total_events": len(self.events),
                "events_last_hour": len(recent_events),
                "active_users": active_users,
                "total_users": len(self.user_sessions),
                "feature_usage": dict(self.feature_usage),
                "error_counts": dict(self.error_counts),
                "avg_performance": avg_performance,
                "events_by_type": {
                    event_type.value: self.metrics["total_events"][event_type.value]
                    for event_type in EventType
                }
            }
    
    def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """
        Retorna analytics específicos de um usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dicionário com analytics do usuário
        """
        with self.lock:
            user_events = [
                event for event in self.events
                if event.user_id == user_id
            ]
            
            if not user_events:
                return {"error": "Usuário não encontrado"}
            
            # Primeira e última atividade
            first_activity = min(event.timestamp for event in user_events)
            last_activity = max(event.timestamp for event in user_events)
            
            # Features mais usadas
            user_features = defaultdict(int)
            for event in user_events:
                if event.event_type == EventType.FEATURE_USAGE:
                    feature = event.data.get("feature", "unknown")
                    user_features[feature] += 1
            
            return {
                "user_id": user_id,
                "first_activity": first_activity.isoformat(),
                "last_activity": last_activity.isoformat(),
                "total_sessions": len(self.user_sessions.get(user_id, set())),
                "total_events": len(user_events),
                "most_used_features": dict(sorted(user_features.items(), key=lambda value: value[1], reverse=True)),
                "recent_events": [
                    event.to_dict() for event in user_events[-10:]  # Últimos 10 eventos
                ]
            }
    
    def export_data(self, format_type: str = "json", filters: Optional[Dict[str, Any]] = None) -> Union[str, bytes]:
        """
        Exporta dados de analytics.
        
        Args:
            format_type: Tipo de formato (json, csv)
            filters: Filtros para exportação
            
        Returns:
            Dados exportados no formato especificado
        """
        with self.lock:
            data = {
                "export_timestamp": datetime.now().isoformat(),
                "metrics": dict(self.metrics),
                "feature_usage": dict(self.feature_usage),
                "error_counts": dict(self.error_counts),
                "performance_metrics": dict(self.performance_metrics),
                "user_sessions": {
                    user_id: list(sessions) 
                    for user_id, sessions in self.user_sessions.items()
                }
            }
            
            if format_type.lower() == "json":
                return json.dumps(data, indent=2, default=str)
            elif format_type.lower() == "csv":
                # Implementar exportação CSV
                return self._export_csv(data)
            else:
                raise ValueError(f"Formato não suportado: {format_type}")
    
    def _export_csv(self, data: Dict[str, Any]) -> bytes:
        """Exporta dados em formato CSV."""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow(["Metric", "Value", "Timestamp"])
        
        # Dados
        for metric, value in data.items():
            if isinstance(value, dict):
                for sub_metric, sub_value in value.items():
                    writer.writerow([f"{metric}.{sub_metric}", sub_value, data["export_timestamp"]])
            else:
                writer.writerow([metric, value, data["export_timestamp"]])
        
        return output.getvalue().encode('utf-8')
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Retorna dados para dashboard interativo.
        
        Returns:
            Dados formatados para dashboard
        """
        metrics = self.get_real_time_metrics()
        
        # Dados para gráficos
        chart_data = {
            "events_timeline": self._get_events_timeline(),
            "feature_usage_chart": self._get_feature_usage_chart(),
            "error_distribution": self._get_error_distribution(),
            "performance_trends": self._get_performance_trends()
        }
        
        return {
            "metrics": metrics,
            "charts": chart_data,
            "last_updated": datetime.now().isoformat()
        }
    
    def _get_events_timeline(self) -> List[Dict[str, Any]]:
        """Gera dados para timeline de eventos."""
        with self.lock:
            timeline = defaultdict(int)
            for event in self.events:
                hour = event.timestamp.strftime("%Y-%m-%data %H:00")
                timeline[hour] += 1
            
            return [
                {"hour": hour, "count": count}
                for hour, count in sorted(timeline.items())
            ]
    
    def _get_feature_usage_chart(self) -> List[Dict[str, Any]]:
        """Gera dados para gráfico de uso de features."""
        return [
            {"feature": feature, "usage": count}
            for feature, count in sorted(self.feature_usage.items(), key=lambda value: value[1], reverse=True)
        ]
    
    def _get_error_distribution(self) -> List[Dict[str, Any]]:
        """Gera dados para distribuição de erros."""
        return [
            {"error_type": error_type, "count": count}
            for error_type, count in sorted(self.error_counts.items(), key=lambda value: value[1], reverse=True)
        ]
    
    def _get_performance_trends(self) -> Dict[str, List[Dict[str, Any]]]:
        """Gera dados para tendências de performance."""
        trends = {}
        for metric_name, values in self.performance_metrics.items():
            if len(values) >= 2:
                trends[metric_name] = [
                    {"index": index, "value": value}
                    for index, value in enumerate(values[-20:])  # Últimos 20 valores
                ]
        return trends


# Decorador para tracking automático
def track_analytics_event(event_type: EventType, **event_data):
    """
    Decorador para tracking automático de eventos de analytics.
    
    Args:
        event_type: Tipo do evento
        **event_data: Dados adicionais do evento
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Aqui você pode extrair user_id e session_id dos argumentos
            # Por simplicidade, usamos valores padrão
            event = AnalyticsEvent(
                event_type=event_type,
                user_id=None,  # Extrair dos args/kwargs
                session_id="session_123",  # Extrair dos args/kwargs
                timestamp=datetime.now(),
                data=event_data,
                metadata={"function": func.__name__, "module": func.__module__}
            )
            
            # Aqui você pode acessar a instância global do analytics
            # analytics.track_event(event)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Instância global (pode ser configurada via dependency injection)
analytics = RealTimeAnalytics()


if __name__ == "__main__":
    # Exemplo de uso
    analytics.start()
    
    # Simular alguns eventos
    events = [
        AnalyticsEvent(
            event_type=EventType.USER_LOGIN,
            user_id="user_123",
            session_id="session_456",
            timestamp=datetime.now(),
            data={"login_method": "email"},
            metadata={"ip": "192.168.1.1"}
        ),
        AnalyticsEvent(
            event_type=EventType.KEYWORD_SEARCH,
            user_id="user_123",
            session_id="session_456",
            timestamp=datetime.now(),
            data={"keywords": ["python", "analytics"], "results_count": 150},
            metadata={"search_time_ms": 250}
        ),
        AnalyticsEvent(
            event_type=EventType.FEATURE_USAGE,
            user_id="user_123",
            session_id="session_456",
            timestamp=datetime.now(),
            data={"feature": "export_csv"},
            metadata={}
        )
    ]
    
    for event in events:
        analytics.track_event(event)
    
    # Obter métricas
    metrics = analytics.get_real_time_metrics()
    print("Métricas em tempo real:", json.dumps(metrics, indent=2))
    
    # Obter dados do dashboard
    dashboard_data = analytics.get_dashboard_data()
    print("Dados do dashboard:", json.dumps(dashboard_data, indent=2))
    
    analytics.stop() 