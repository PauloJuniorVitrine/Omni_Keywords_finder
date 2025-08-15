"""
📊 Advanced Metrics API
🎯 Objetivo: Endpoints para métricas avançadas com agregação e cache
📅 Data: 2025-01-27
🔗 Tracing ID: ADVANCED_METRICS_API_001
📋 Ruleset: enterprise_control_layer.yaml
"""

import json
import time
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
from collections import defaultdict, deque
import asyncio
from functools import wraps

from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
import redis
from sqlalchemy import text, func
from sqlalchemy.orm import sessionmaker

from infrastructure.monitoring.metrics_collector import MetricsCollector
from infrastructure.cache.intelligent_cache import IntelligentCache
from infrastructure.observability.opentelemetry_config import get_tracer

# Configuração de logging
logger = logging.getLogger(__name__)

# Blueprint para métricas avançadas
advanced_metrics_bp = Blueprint('advanced_metrics', __name__, url_prefix='/api/metrics')

# Tipos de métricas
class MetricType(Enum):
    """Tipos de métricas disponíveis"""
    PERFORMANCE = "performance"
    BUSINESS = "business"
    INFRASTRUCTURE = "infrastructure"
    USER = "user"
    SECURITY = "security"
    CUSTOM = "custom"

class AggregationType(Enum):
    """Tipos de agregação"""
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    PERCENTILE_95 = "p95"
    PERCENTILE_99 = "p99"

@dataclass
class MetricDefinition:
    """Definição de uma métrica"""
    name: str
    type: MetricType
    unit: str
    description: str
    aggregation_types: List[AggregationType]
    retention_days: int
    alert_thresholds: Dict[str, float]
    tags: List[str]

@dataclass
class MetricDataPoint:
    """Ponto de dados de métrica"""
    metric_name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str]
    source: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AggregatedMetric:
    """Métrica agregada"""
    metric_name: str
    aggregation_type: AggregationType
    value: float
    timestamp: datetime
    interval: str
    tags: Dict[str, str]
    data_points_count: int

class AdvancedMetricsService:
    """Serviço para métricas avançadas"""
    
    def __init__(self, cache: Optional[IntelligentCache] = None):
        self.cache = cache or IntelligentCache()
        self.metrics_collector = MetricsCollector()
        self.tracer = get_tracer()
        
        # Armazenamento em memória para métricas recentes
        self.recent_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.metric_definitions: Dict[str, MetricDefinition] = {}
        
        # Inicializar métricas padrão
        self._initialize_default_metrics()
    
    def _initialize_default_metrics(self):
        """Inicializa métricas padrão do sistema"""
        default_metrics = [
            MetricDefinition(
                name="response_time",
                type=MetricType.PERFORMANCE,
                unit="ms",
                description="Tempo de resposta das APIs",
                aggregation_types=[AggregationType.AVG, AggregationType.P95, AggregationType.P99],
                retention_days=30,
                alert_thresholds={"warning": 500, "critical": 1000},
                tags=["endpoint", "method", "status_code"]
            ),
            MetricDefinition(
                name="error_rate",
                type=MetricType.PERFORMANCE,
                unit="%",
                description="Taxa de erro das APIs",
                aggregation_types=[AggregationType.AVG, AggregationType.MAX],
                retention_days=30,
                alert_thresholds={"warning": 5.0, "critical": 10.0},
                tags=["endpoint", "error_type"]
            ),
            MetricDefinition(
                name="active_users",
                type=MetricType.USER,
                unit="",
                description="Usuários ativos no sistema",
                aggregation_types=[AggregationType.COUNT, AggregationType.AVG],
                retention_days=7,
                alert_thresholds={"warning": 1000, "critical": 500},
                tags=["user_type", "region"]
            ),
            MetricDefinition(
                name="cpu_usage",
                type=MetricType.INFRASTRUCTURE,
                unit="%",
                description="Uso de CPU dos servidores",
                aggregation_types=[AggregationType.AVG, AggregationType.MAX],
                retention_days=7,
                alert_thresholds={"warning": 80, "critical": 95},
                tags=["server", "instance_type"]
            ),
            MetricDefinition(
                name="memory_usage",
                type=MetricType.INFRASTRUCTURE,
                unit="%",
                description="Uso de memória dos servidores",
                aggregation_types=[AggregationType.AVG, AggregationType.MAX],
                retention_days=7,
                alert_thresholds={"warning": 85, "critical": 95},
                tags=["server", "instance_type"]
            ),
            MetricDefinition(
                name="database_connections",
                type=MetricType.INFRASTRUCTURE,
                unit="",
                description="Conexões ativas no banco de dados",
                aggregation_types=[AggregationType.COUNT, AggregationType.AVG],
                retention_days=7,
                alert_thresholds={"warning": 80, "critical": 95},
                tags=["database", "connection_type"]
            ),
            MetricDefinition(
                name="revenue",
                type=MetricType.BUSINESS,
                unit="R$",
                description="Receita gerada",
                aggregation_types=[AggregationType.SUM, AggregationType.AVG],
                retention_days=90,
                alert_thresholds={"warning": 10000, "critical": 5000},
                tags=["product", "region", "payment_method"]
            ),
            MetricDefinition(
                name="conversion_rate",
                type=MetricType.BUSINESS,
                unit="%",
                description="Taxa de conversão",
                aggregation_types=[AggregationType.AVG, AggregationType.MAX],
                retention_days=30,
                alert_thresholds={"warning": 2.0, "critical": 1.0},
                tags=["funnel_step", "campaign"]
            )
        ]
        
        for metric in default_metrics:
            self.metric_definitions[metric.name] = metric
    
    def record_metric(self, metric_name: str, value: float, tags: Dict[str, str] = None, metadata: Dict[str, Any] = None):
        """
        Registra uma nova métrica
        
        Args:
            metric_name: Nome da métrica
            value: Valor da métrica
            tags: Tags associadas
            metadata: Metadados adicionais
        """
        try:
            with self.tracer.start_as_current_span("record_metric") as span:
                span.set_attribute("metric.name", metric_name)
                span.set_attribute("metric.value", value)
                
                data_point = MetricDataPoint(
                    metric_name=metric_name,
                    value=value,
                    timestamp=datetime.utcnow(),
                    tags=tags or {},
                    source="api",
                    metadata=metadata
                )
                
                # Armazenar em memória
                self.recent_metrics[metric_name].append(data_point)
                
                # Armazenar no cache
                cache_key = f"metric:{metric_name}:{int(time.time())}"
                self.cache.set(cache_key, asdict(data_point), ttl=3600)
                
                # Registrar no coletor de métricas
                self.metrics_collector.record_metric(metric_name, value, tags)
                
                logger.debug(f"[METRICS] Métrica registrada: {metric_name} = {value}")
                
        except Exception as e:
            logger.error(f"[METRICS] Erro ao registrar métrica {metric_name}: {str(e)}")
    
    def get_metric_data(
        self, 
        metric_name: str, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        aggregation: Optional[AggregationType] = None,
        interval: str = "1h",
        tags: Optional[Dict[str, str]] = None
    ) -> List[AggregatedMetric]:
        """
        Obtém dados de uma métrica com agregação
        
        Args:
            metric_name: Nome da métrica
            start_time: Tempo de início
            end_time: Tempo de fim
            aggregation: Tipo de agregação
            interval: Intervalo de agregação
            tags: Filtros de tags
            
        Returns:
            Lista de métricas agregadas
        """
        try:
            with self.tracer.start_as_current_span("get_metric_data") as span:
                span.set_attribute("metric.name", metric_name)
                span.set_attribute("metric.aggregation", aggregation.value if aggregation else "none")
                
                # Definir intervalo padrão se não especificado
                if not start_time:
                    start_time = datetime.utcnow() - timedelta(hours=24)
                if not end_time:
                    end_time = datetime.utcnow()
                
                # Tentar obter do cache primeiro
                cache_key = f"aggregated_metric:{metric_name}:{start_time.isoformat()}:{end_time.isoformat()}:{aggregation.value if aggregation else 'raw'}:{interval}"
                cached_data = self.cache.get(cache_key)
                
                if cached_data:
                    logger.debug(f"[METRICS] Dados obtidos do cache: {metric_name}")
                    return [AggregatedMetric(**data) for data in cached_data]
                
                # Obter dados da memória
                data_points = self._get_data_points_in_range(metric_name, start_time, end_time, tags)
                
                if not data_points:
                    return []
                
                # Aplicar agregação se especificada
                if aggregation:
                    aggregated_data = self._aggregate_data(data_points, aggregation, interval)
                else:
                    # Retornar dados brutos
                    aggregated_data = [
                        AggregatedMetric(
                            metric_name=dp.metric_name,
                            aggregation_type=AggregationType.COUNT,
                            value=dp.value,
                            timestamp=dp.timestamp,
                            interval="raw",
                            tags=dp.tags,
                            data_points_count=1
                        )
                        for dp in data_points
                    ]
                
                # Armazenar no cache
                self.cache.set(cache_key, [asdict(agg) for agg in aggregated_data], ttl=300)
                
                return aggregated_data
                
        except Exception as e:
            logger.error(f"[METRICS] Erro ao obter dados da métrica {metric_name}: {str(e)}")
            return []
    
    def _get_data_points_in_range(
        self, 
        metric_name: str, 
        start_time: datetime, 
        end_time: datetime, 
        tags: Optional[Dict[str, str]] = None
    ) -> List[MetricDataPoint]:
        """Obtém pontos de dados em um intervalo de tempo"""
        data_points = []
        
        # Obter da memória
        if metric_name in self.recent_metrics:
            for dp in self.recent_metrics[metric_name]:
                if start_time <= dp.timestamp <= end_time:
                    # Aplicar filtros de tags
                    if tags:
                        if all(dp.tags.get(key) == value for key, value in tags.items()):
                            data_points.append(dp)
                    else:
                        data_points.append(dp)
        
        return data_points
    
    def _aggregate_data(
        self, 
        data_points: List[MetricDataPoint], 
        aggregation_type: AggregationType, 
        interval: str
    ) -> List[AggregatedMetric]:
        """Agrega dados por intervalo de tempo"""
        if not data_points:
            return []
        
        # Agrupar por intervalo
        grouped_data = defaultdict(list)
        
        for dp in data_points:
            # Calcular bucket de tempo baseado no intervalo
            bucket_time = self._get_bucket_time(dp.timestamp, interval)
            grouped_data[bucket_time].append(dp)
        
        # Aplicar agregação
        aggregated_data = []
        
        for bucket_time, points in grouped_data.items():
            values = [dp.value for dp in points]
            
            if aggregation_type == AggregationType.SUM:
                value = sum(values)
            elif aggregation_type == AggregationType.AVG:
                value = statistics.mean(values)
            elif aggregation_type == AggregationType.MIN:
                value = min(values)
            elif aggregation_type == AggregationType.MAX:
                value = max(values)
            elif aggregation_type == AggregationType.COUNT:
                value = len(values)
            elif aggregation_type == AggregationType.PERCENTILE_95:
                value = statistics.quantiles(values, n=20)[18] if len(values) > 1 else values[0]
            elif aggregation_type == AggregationType.PERCENTILE_99:
                value = statistics.quantiles(values, n=100)[98] if len(values) > 1 else values[0]
            else:
                value = statistics.mean(values)
            
            # Usar tags do primeiro ponto (assumindo que são consistentes no bucket)
            tags = points[0].tags if points else {}
            
            aggregated_data.append(AggregatedMetric(
                metric_name=points[0].metric_name,
                aggregation_type=aggregation_type,
                value=value,
                timestamp=bucket_time,
                interval=interval,
                tags=tags,
                data_points_count=len(points)
            ))
        
        return sorted(aggregated_data, key=lambda value: value.timestamp)
    
    def _get_bucket_time(self, timestamp: datetime, interval: str) -> datetime:
        """Calcula o bucket de tempo para agregação"""
        if interval == "1m":
            return timestamp.replace(second=0, microsecond=0)
        elif interval == "5m":
            minutes = (timestamp.minute // 5) * 5
            return timestamp.replace(minute=minutes, second=0, microsecond=0)
        elif interval == "1h":
            return timestamp.replace(minute=0, second=0, microsecond=0)
        elif interval == "1d":
            return timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            return timestamp.replace(second=0, microsecond=0)
    
    def get_metric_summary(self, metric_name: str) -> Dict[str, Any]:
        """Obtém resumo de uma métrica"""
        try:
            # Obter dados das últimas 24 horas
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=24)
            
            data_points = self._get_data_points_in_range(metric_name, start_time, end_time)
            
            if not data_points:
                return {
                    "metric_name": metric_name,
                    "current_value": 0,
                    "avg_value": 0,
                    "min_value": 0,
                    "max_value": 0,
                    "trend": "stable",
                    "data_points_count": 0
                }
            
            values = [dp.value for dp in data_points]
            current_value = values[-1] if values else 0
            
            # Calcular tendência
            if len(values) >= 2:
                recent_avg = statistics.mean(values[-10:]) if len(values) >= 10 else values[-1]
                previous_avg = statistics.mean(values[-20:-10]) if len(values) >= 20 else values[0]
                trend = "up" if recent_avg > previous_avg else "down" if recent_avg < previous_avg else "stable"
            else:
                trend = "stable"
            
            return {
                "metric_name": metric_name,
                "current_value": current_value,
                "avg_value": statistics.mean(values),
                "min_value": min(values),
                "max_value": max(values),
                "trend": trend,
                "data_points_count": len(data_points),
                "last_updated": data_points[-1].timestamp.isoformat() if data_points else None
            }
            
        except Exception as e:
            logger.error(f"[METRICS] Erro ao obter resumo da métrica {metric_name}: {str(e)}")
            return {}
    
    def get_system_health(self) -> Dict[str, Any]:
        """Obtém saúde geral do sistema"""
        try:
            health_metrics = {}
            
            # Verificar métricas críticas
            critical_metrics = ["response_time", "error_rate", "cpu_usage", "memory_usage"]
            
            for metric_name in critical_metrics:
                summary = self.get_metric_summary(metric_name)
                if summary:
                    health_metrics[metric_name] = summary
            
            # Calcular score geral de saúde
            health_score = 100
            alerts = []
            
            for metric_name, summary in health_metrics.items():
                if metric_name in self.metric_definitions:
                    definition = self.metric_definitions[metric_name]
                    current_value = summary.get("current_value", 0)
                    
                    # Verificar thresholds
                    if "critical" in definition.alert_thresholds:
                        if current_value > definition.alert_thresholds["critical"]:
                            health_score -= 25
                            alerts.append({
                                "type": "critical",
                                "metric": metric_name,
                                "value": current_value,
                                "threshold": definition.alert_thresholds["critical"]
                            })
                    elif "warning" in definition.alert_thresholds:
                        if current_value > definition.alert_thresholds["warning"]:
                            health_score -= 10
                            alerts.append({
                                "type": "warning",
                                "metric": metric_name,
                                "value": current_value,
                                "threshold": definition.alert_thresholds["warning"]
                            })
            
            return {
                "health_score": max(0, health_score),
                "status": "healthy" if health_score >= 80 else "warning" if health_score >= 60 else "critical",
                "metrics": health_metrics,
                "alerts": alerts,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[METRICS] Erro ao obter saúde do sistema: {str(e)}")
            return {"health_score": 0, "status": "unknown", "error": str(e)}

# Instância global do serviço
metrics_service = AdvancedMetricsService()

# Decorator para métricas
def track_metric(metric_name: str, tags: Optional[Dict[str, str]] = None):
    """Decorator para rastrear métricas de funções"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                response_time = (time.time() - start_time) * 1000
                
                # Registrar métrica de sucesso
                metric_tags = tags or {}
                metric_tags.update({"status": "success"})
                metrics_service.record_metric(f"{metric_name}_response_time", response_time, metric_tags)
                metrics_service.record_metric(f"{metric_name}_success_count", 1, metric_tags)
                
                return result
            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                
                # Registrar métrica de erro
                metric_tags = tags or {}
                metric_tags.update({"status": "error", "error_type": type(e).__name__})
                metrics_service.record_metric(f"{metric_name}_response_time", response_time, metric_tags)
                metrics_service.record_metric(f"{metric_name}_error_count", 1, metric_tags)
                
                raise
        return wrapper
    return decorator

# Endpoints da API
@advanced_metrics_bp.route('/record', methods=['POST'])
@cross_origin()
@track_metric("record_metric")
def record_metric():
    """Endpoint para registrar uma nova métrica"""
    try:
        data = request.get_json()
        
        if not data or 'name' not in data or 'value' not in data:
            return jsonify({"error": "Dados inválidos"}), 400
        
        metric_name = data['name']
        value = float(data['value'])
        tags = data.get('tags', {})
        metadata = data.get('metadata', {})
        
        metrics_service.record_metric(metric_name, value, tags, metadata)
        
        return jsonify({"message": "Métrica registrada com sucesso"}), 201
        
    except Exception as e:
        logger.error(f"[METRICS_API] Erro ao registrar métrica: {str(e)}")
        return jsonify({"error": "Erro interno"}), 500

@advanced_metrics_bp.route('/data/<metric_name>', methods=['GET'])
@cross_origin()
@track_metric("get_metric_data")
def get_metric_data(metric_name: str):
    """Endpoint para obter dados de uma métrica"""
    try:
        # Parâmetros da query
        start_time_str = request.args.get('start_time')
        end_time_str = request.args.get('end_time')
        aggregation_str = request.args.get('aggregation')
        interval = request.args.get('interval', '1h')
        tags_str = request.args.get('tags')
        
        # Converter parâmetros
        start_time = datetime.fromisoformat(start_time_str) if start_time_str else None
        end_time = datetime.fromisoformat(end_time_str) if end_time_str else None
        aggregation = AggregationType(aggregation_str) if aggregation_str else None
        tags = json.loads(tags_str) if tags_str else None
        
        # Obter dados
        data = metrics_service.get_metric_data(
            metric_name, 
            start_time, 
            end_time, 
            aggregation, 
            interval, 
            tags
        )
        
        return jsonify({
            "metric_name": metric_name,
            "data": [asdict(data) for data in data],
            "count": len(data)
        })
        
    except Exception as e:
        logger.error(f"[METRICS_API] Erro ao obter dados da métrica {metric_name}: {str(e)}")
        return jsonify({"error": "Erro interno"}), 500

@advanced_metrics_bp.route('/summary/<metric_name>', methods=['GET'])
@cross_origin()
@track_metric("get_metric_summary")
def get_metric_summary(metric_name: str):
    """Endpoint para obter resumo de uma métrica"""
    try:
        summary = metrics_service.get_metric_summary(metric_name)
        return jsonify(summary)
        
    except Exception as e:
        logger.error(f"[METRICS_API] Erro ao obter resumo da métrica {metric_name}: {str(e)}")
        return jsonify({"error": "Erro interno"}), 500

@advanced_metrics_bp.route('/health', methods=['GET'])
@cross_origin()
@track_metric("get_system_health")
def get_system_health():
    """Endpoint para obter saúde do sistema"""
    try:
        health = metrics_service.get_system_health()
        return jsonify(health)
        
    except Exception as e:
        logger.error(f"[METRICS_API] Erro ao obter saúde do sistema: {str(e)}")
        return jsonify({"error": "Erro interno"}), 500

@advanced_metrics_bp.route('/definitions', methods=['GET'])
@cross_origin()
@track_metric("get_metric_definitions")
def get_metric_definitions():
    """Endpoint para obter definições de métricas"""
    try:
        definitions = {
            name: asdict(definition) 
            for name, definition in metrics_service.metric_definitions.items()
        }
        return jsonify(definitions)
        
    except Exception as e:
        logger.error(f"[METRICS_API] Erro ao obter definições: {str(e)}")
        return jsonify({"error": "Erro interno"}), 500

@advanced_metrics_bp.route('/types', methods=['GET'])
@cross_origin()
def get_metric_types():
    """Endpoint para obter tipos de métricas disponíveis"""
    try:
        return jsonify({
            "types": [t.value for t in MetricType],
            "aggregations": [a.value for a in AggregationType]
        })
        
    except Exception as e:
        logger.error(f"[METRICS_API] Erro ao obter tipos: {str(e)}")
        return jsonify({"error": "Erro interno"}), 500

# Testes unitários (não executar)
def test_advanced_metrics():
    """Testes para o sistema de métricas avançadas"""
    
    def test_metric_recording():
        """Testa registro de métricas"""
        service = AdvancedMetricsService()
        service.record_metric("test_metric", 100.0, {"tag1": "value1"})
        
        # Verificar se métrica foi registrada
        data_points = service._get_data_points_in_range(
            "test_metric", 
            datetime.utcnow() - timedelta(minutes=1), 
            datetime.utcnow()
        )
        
        assert len(data_points) > 0
        assert data_points[0].value == 100.0
        
    def test_metric_aggregation():
        """Testa agregação de métricas"""
        service = AdvancedMetricsService()
        
        # Registrar múltiplas métricas
        for index in range(10):
            service.record_metric("test_metric", float(index))
        
        # Obter dados agregados
        aggregated = service.get_metric_data(
            "test_metric",
            aggregation=AggregationType.AVG,
            interval="1h"
        )
        
        assert len(aggregated) > 0
        assert aggregated[0].aggregation_type == AggregationType.AVG
        
    def test_system_health():
        """Testa cálculo de saúde do sistema"""
        service = AdvancedMetricsService()
        health = service.get_system_health()
        
        assert "health_score" in health
        assert "status" in health
        assert "metrics" in health

if __name__ == "__main__":
    # Exemplo de uso
    print("📊 Advanced Metrics API - Carregado com sucesso")
    
    # Registrar algumas métricas de exemplo
    metrics_service.record_metric("response_time", 245.5, {"endpoint": "/api/users"})
    metrics_service.record_metric("error_rate", 1.2, {"endpoint": "/api/users"})
    metrics_service.record_metric("active_users", 1247, {"region": "BR"})
    
    # Obter resumo
    summary = metrics_service.get_metric_summary("response_time")
    print(f"📈 Resumo da métrica response_time: {summary}")
    
    # Obter saúde do sistema
    health = metrics_service.get_system_health()
    print(f"🏥 Saúde do sistema: {health['health_score']}% - {health['status']}") 