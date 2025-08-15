"""
Sistema de Coleta Inteligente - Omni Keywords Finder
Coleta inteligente de eventos para AIOps

Tracing ID: INTELLIGENT_COLLECTOR_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: 🟡 ALTO - Sistema de Coleta Inteligente

Baseado no código real do sistema Omni Keywords Finder
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import aioredis
from prometheus_client import Counter, Histogram, Gauge
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import pandas as pd

from ..monitoring.metrics_collector import MetricsCollector
from ..logging.structured_logger import StructuredLogger
from ..ml.anomaly.anomaly_detector import AnomalyDetector
from ..cache.redis_manager import RedisManager

# Configuração de logging
logger = logging.getLogger(__name__)

class EventType(Enum):
    """Tipos de eventos suportados"""
    SYSTEM_METRIC = "system_metric"
    APPLICATION_LOG = "application_log"
    DATABASE_QUERY = "database_query"
    API_REQUEST = "api_request"
    ERROR_EVENT = "error_event"
    PERFORMANCE_METRIC = "performance_metric"
    SECURITY_EVENT = "security_event"
    USER_ACTION = "user_action"
    BUSINESS_METRIC = "business_metric"
    INFRASTRUCTURE_ALERT = "infrastructure_alert"

class EventSeverity(Enum):
    """Severidades de eventos"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Event:
    """Estrutura de evento padronizada"""
    id: str
    type: EventType
    source: str
    severity: EventSeverity
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class DataSource:
    """Interface para fontes de dados"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.is_active = False
        self.last_collection = None
        self.error_count = 0
        self.success_count = 0
    
    async def connect(self) -> bool:
        """Conecta à fonte de dados"""
        raise NotImplementedError
    
    async def collect(self) -> List[Event]:
        """Coleta eventos da fonte"""
        raise NotImplementedError
    
    async def disconnect(self):
        """Desconecta da fonte de dados"""
        raise NotImplementedError
    
    def get_health_status(self) -> Dict[str, Any]:
        """Retorna status de saúde da fonte"""
        return {
            'name': self.name,
            'is_active': self.is_active,
            'last_collection': self.last_collection,
            'error_count': self.error_count,
            'success_count': self.success_count,
            'error_rate': self.error_count / (self.error_count + self.success_count) if (self.error_count + self.success_count) > 0 else 0
        }

class SystemMetricsSource(DataSource):
    """Fonte de dados para métricas do sistema"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("system_metrics", config)
        self.metrics_collector = MetricsCollector()
        self.collection_interval = config.get('collection_interval', 60)
        self.metrics = config.get('metrics', ['cpu', 'memory', 'disk', 'network'])
    
    async def connect(self) -> bool:
        """Conecta ao sistema de métricas"""
        try:
            await self.metrics_collector.initialize()
            self.is_active = True
            logger.info(f"Conectado à fonte de métricas do sistema: {self.name}")
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar à fonte de métricas: {str(e)}")
            self.error_count += 1
            return False
    
    async def collect(self) -> List[Event]:
        """Coleta métricas do sistema"""
        events = []
        try:
            metrics_data = await self.metrics_collector.collect_system_metrics()
            
            for metric_name, metric_value in metrics_data.items():
                if metric_name in self.metrics:
                    event = Event(
                        id=f"sys_{int(time.time())}_{metric_name}",
                        type=EventType.SYSTEM_METRIC,
                        source=self.name,
                        severity=self._determine_severity(metric_name, metric_value),
                        timestamp=datetime.now(),
                        data={
                            'metric_name': metric_name,
                            'value': metric_value,
                            'unit': self._get_metric_unit(metric_name)
                        },
                        metadata={
                            'collection_interval': self.collection_interval,
                            'thresholds': self.config.get('thresholds', {})
                        }
                    )
                    events.append(event)
            
            self.last_collection = datetime.now()
            self.success_count += 1
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas do sistema: {str(e)}")
            self.error_count += 1
        
        return events
    
    async def disconnect(self):
        """Desconecta do sistema de métricas"""
        self.is_active = False
        logger.info(f"Desconectado da fonte de métricas: {self.name}")
    
    def _determine_severity(self, metric_name: str, value: float) -> EventSeverity:
        """Determina severidade baseada no valor da métrica"""
        thresholds = self.config.get('thresholds', {})
        metric_thresholds = thresholds.get(metric_name, {})
        
        if metric_name == 'cpu_usage':
            if value > metric_thresholds.get('critical', 90):
                return EventSeverity.CRITICAL
            elif value > metric_thresholds.get('high', 80):
                return EventSeverity.HIGH
            elif value > metric_thresholds.get('medium', 70):
                return EventSeverity.MEDIUM
            else:
                return EventSeverity.LOW
        
        elif metric_name == 'memory_usage':
            if value > metric_thresholds.get('critical', 95):
                return EventSeverity.CRITICAL
            elif value > metric_thresholds.get('high', 85):
                return EventSeverity.HIGH
            elif value > metric_thresholds.get('medium', 75):
                return EventSeverity.MEDIUM
            else:
                return EventSeverity.LOW
        
        return EventSeverity.LOW
    
    def _get_metric_unit(self, metric_name: str) -> str:
        """Retorna unidade da métrica"""
        units = {
            'cpu_usage': '%',
            'memory_usage': '%',
            'disk_usage': '%',
            'network_io': 'MB/s',
            'response_time': 'ms'
        }
        return units.get(metric_name, '')

class ApplicationLogSource(DataSource):
    """Fonte de dados para logs da aplicação"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("application_logs", config)
        self.log_file_path = config.get('log_file_path', '/var/log/omni_keywords_finder/app.log')
        self.log_levels = config.get('log_levels', ['ERROR', 'WARNING', 'INFO'])
        self.batch_size = config.get('batch_size', 100)
        self.last_position = 0
    
    async def connect(self) -> bool:
        """Conecta ao arquivo de log"""
        try:
            # Simular conexão com arquivo de log
            self.is_active = True
            logger.info(f"Conectado à fonte de logs da aplicação: {self.name}")
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar à fonte de logs: {str(e)}")
            self.error_count += 1
            return False
    
    async def collect(self) -> List[Event]:
        """Coleta logs da aplicação"""
        events = []
        try:
            # Simular leitura de logs
            log_entries = self._simulate_log_entries()
            
            for entry in log_entries:
                if entry['level'] in self.log_levels:
                    event = Event(
                        id=f"log_{int(time.time())}_{entry['id']}",
                        type=EventType.APPLICATION_LOG,
                        source=self.name,
                        severity=self._map_log_level_to_severity(entry['level']),
                        timestamp=datetime.fromisoformat(entry['timestamp']),
                        data={
                            'message': entry['message'],
                            'level': entry['level'],
                            'module': entry.get('module', ''),
                            'function': entry.get('function', '')
                        },
                        metadata={
                            'log_file': self.log_file_path,
                            'line_number': entry.get('line_number'),
                            'thread_id': entry.get('thread_id')
                        },
                        correlation_id=entry.get('correlation_id'),
                        user_id=entry.get('user_id')
                    )
                    events.append(event)
            
            self.last_collection = datetime.now()
            self.success_count += 1
            
        except Exception as e:
            logger.error(f"Erro ao coletar logs da aplicação: {str(e)}")
            self.error_count += 1
        
        return events
    
    async def disconnect(self):
        """Desconecta do arquivo de log"""
        self.is_active = False
        logger.info(f"Desconectado da fonte de logs: {self.name}")
    
    def _simulate_log_entries(self) -> List[Dict[str, Any]]:
        """Simula entradas de log para teste"""
        return [
            {
                'id': '1',
                'timestamp': datetime.now().isoformat(),
                'level': 'ERROR',
                'message': 'Database connection failed',
                'module': 'database',
                'function': 'connect',
                'line_number': 45,
                'thread_id': 'thread-1',
                'correlation_id': 'corr-123',
                'user_id': 'user-456'
            },
            {
                'id': '2',
                'timestamp': datetime.now().isoformat(),
                'level': 'WARNING',
                'message': 'High memory usage detected',
                'module': 'monitoring',
                'function': 'check_memory',
                'line_number': 78,
                'thread_id': 'thread-2'
            },
            {
                'id': '3',
                'timestamp': datetime.now().isoformat(),
                'level': 'INFO',
                'message': 'User login successful',
                'module': 'auth',
                'function': 'login',
                'line_number': 23,
                'thread_id': 'thread-3',
                'user_id': 'user-789'
            }
        ]
    
    def _map_log_level_to_severity(self, log_level: str) -> EventSeverity:
        """Mapeia nível de log para severidade"""
        mapping = {
            'ERROR': EventSeverity.HIGH,
            'WARNING': EventSeverity.MEDIUM,
            'INFO': EventSeverity.LOW,
            'DEBUG': EventSeverity.LOW
        }
        return mapping.get(log_level, EventSeverity.LOW)

class DatabaseQuerySource(DataSource):
    """Fonte de dados para queries do banco de dados"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("database_queries", config)
        self.slow_query_threshold = config.get('slow_query_threshold', 1000)  # ms
        self.query_patterns = config.get('query_patterns', [])
        self.collection_interval = config.get('collection_interval', 30)
    
    async def connect(self) -> bool:
        """Conecta ao sistema de monitoramento de queries"""
        try:
            # Simular conexão com sistema de monitoramento
            self.is_active = True
            logger.info(f"Conectado à fonte de queries do banco: {self.name}")
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar à fonte de queries: {str(e)}")
            self.error_count += 1
            return False
    
    async def collect(self) -> List[Event]:
        """Coleta queries do banco de dados"""
        events = []
        try:
            # Simular coleta de queries
            queries = self._simulate_database_queries()
            
            for query in queries:
                if query['execution_time'] > self.slow_query_threshold:
                    event = Event(
                        id=f"db_{int(time.time())}_{query['id']}",
                        type=EventType.DATABASE_QUERY,
                        source=self.name,
                        severity=self._determine_query_severity(query['execution_time']),
                        timestamp=datetime.fromisoformat(query['timestamp']),
                        data={
                            'query': query['query'],
                            'execution_time': query['execution_time'],
                            'rows_affected': query.get('rows_affected', 0),
                            'database': query.get('database', 'omni_keywords_finder')
                        },
                        metadata={
                            'slow_query_threshold': self.slow_query_threshold,
                            'query_type': query.get('type', 'SELECT'),
                            'connection_id': query.get('connection_id')
                        },
                        correlation_id=query.get('correlation_id'),
                        user_id=query.get('user_id')
                    )
                    events.append(event)
            
            self.last_collection = datetime.now()
            self.success_count += 1
            
        except Exception as e:
            logger.error(f"Erro ao coletar queries do banco: {str(e)}")
            self.error_count += 1
        
        return events
    
    async def disconnect(self):
        """Desconecta do sistema de monitoramento"""
        self.is_active = False
        logger.info(f"Desconectado da fonte de queries: {self.name}")
    
    def _simulate_database_queries(self) -> List[Dict[str, Any]]:
        """Simula queries do banco para teste"""
        return [
            {
                'id': '1',
                'timestamp': datetime.now().isoformat(),
                'query': 'SELECT * FROM users WHERE email = ?',
                'execution_time': 1500,  # 1.5s - lento
                'rows_affected': 1,
                'type': 'SELECT',
                'database': 'omni_keywords_finder',
                'connection_id': 'conn-1',
                'correlation_id': 'corr-123',
                'user_id': 'user-456'
            },
            {
                'id': '2',
                'timestamp': datetime.now().isoformat(),
                'query': 'UPDATE keywords SET status = ? WHERE id = ?',
                'execution_time': 2500,  # 2.5s - muito lento
                'rows_affected': 1,
                'type': 'UPDATE',
                'database': 'omni_keywords_finder',
                'connection_id': 'conn-2',
                'correlation_id': 'corr-124',
                'user_id': 'user-789'
            }
        ]
    
    def _determine_query_severity(self, execution_time: int) -> EventSeverity:
        """Determina severidade baseada no tempo de execução"""
        if execution_time > 5000:  # 5s
            return EventSeverity.CRITICAL
        elif execution_time > 2000:  # 2s
            return EventSeverity.HIGH
        elif execution_time > 1000:  # 1s
            return EventSeverity.MEDIUM
        else:
            return EventSeverity.LOW

class IntelligentCollector:
    """Sistema de coleta inteligente de eventos"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.sources: List[DataSource] = []
        self.is_running = False
        self.redis_manager = RedisManager()
        self.anomaly_detector = AnomalyDetector()
        self.structured_logger = StructuredLogger()
        
        # Métricas Prometheus
        self.events_collected = Counter('aiops_events_collected_total', 'Total events collected', ['source', 'type'])
        self.collection_duration = Histogram('aiops_collection_duration_seconds', 'Collection duration', ['source'])
        self.active_sources = Gauge('aiops_active_sources', 'Number of active data sources')
        self.collection_errors = Counter('aiops_collection_errors_total', 'Collection errors', ['source'])
        
        # Configuração
        self.collection_interval = config.get('collection_interval', 60)
        self.batch_size = config.get('batch_size', 1000)
        self.enable_anomaly_detection = config.get('enable_anomaly_detection', True)
        self.enable_correlation = config.get('enable_correlation', True)
        
        # Cache para eventos recentes
        self.recent_events: List[Event] = []
        self.max_recent_events = config.get('max_recent_events', 10000)
        
        # Inicializar fontes de dados
        self._initialize_sources()
    
    def _initialize_sources(self):
        """Inicializa fontes de dados baseado na configuração"""
        sources_config = self.config.get('sources', {})
        
        # Sistema de métricas
        if sources_config.get('system_metrics', {}).get('enabled', True):
            system_metrics_config = sources_config['system_metrics']
            self.sources.append(SystemMetricsSource(system_metrics_config))
        
        # Logs da aplicação
        if sources_config.get('application_logs', {}).get('enabled', True):
            app_logs_config = sources_config['application_logs']
            self.sources.append(ApplicationLogSource(app_logs_config))
        
        # Queries do banco
        if sources_config.get('database_queries', {}).get('enabled', True):
            db_queries_config = sources_config['database_queries']
            self.sources.append(DatabaseQuerySource(db_queries_config))
        
        logger.info(f"Inicializadas {len(self.sources)} fontes de dados")
    
    async def start(self):
        """Inicia o sistema de coleta"""
        try:
            logger.info("Iniciando sistema de coleta inteligente")
            
            # Conectar ao Redis
            await self.redis_manager.connect()
            
            # Conectar às fontes de dados
            for source in self.sources:
                await source.connect()
            
            self.is_running = True
            self.active_sources.set(len([s for s in self.sources if s.is_active]))
            
            # Iniciar loop de coleta
            await self._collection_loop()
            
        except Exception as e:
            logger.error(f"Erro ao iniciar sistema de coleta: {str(e)}")
            await self.stop()
    
    async def stop(self):
        """Para o sistema de coleta"""
        logger.info("Parando sistema de coleta inteligente")
        self.is_running = False
        
        # Desconectar fontes de dados
        for source in self.sources:
            await source.disconnect()
        
        # Desconectar do Redis
        await self.redis_manager.disconnect()
        
        self.active_sources.set(0)
    
    async def _collection_loop(self):
        """Loop principal de coleta"""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Coletar eventos de todas as fontes
                all_events = []
                for source in self.sources:
                    if source.is_active:
                        events = await self._collect_from_source(source)
                        all_events.extend(events)
                
                # Processar eventos coletados
                if all_events:
                    await self._process_events(all_events)
                
                # Aguardar próximo ciclo
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Erro no loop de coleta: {str(e)}")
                await asyncio.sleep(10)  # Aguardar antes de tentar novamente
    
    async def _collect_from_source(self, source: DataSource) -> List[Event]:
        """Coleta eventos de uma fonte específica"""
        start_time = time.time()
        
        try:
            events = await source.collect()
            
            # Registrar métricas
            duration = time.time() - start_time
            self.collection_duration.labels(source=source.name).observe(duration)
            
            for event in events:
                self.events_collected.labels(source=source.name, type=event.type.value).inc()
            
            logger.debug(f"Coletados {len(events)} eventos da fonte {source.name}")
            return events
            
        except Exception as e:
            self.collection_errors.labels(source=source.name).inc()
            logger.error(f"Erro ao coletar da fonte {source.name}: {str(e)}")
            return []
    
    async def _process_events(self, events: List[Event]):
        """Processa eventos coletados"""
        try:
            # Adicionar eventos ao cache recente
            self.recent_events.extend(events)
            
            # Manter apenas os eventos mais recentes
            if len(self.recent_events) > self.max_recent_events:
                self.recent_events = self.recent_events[-self.max_recent_events:]
            
            # Detecção de anomalias
            if self.enable_anomaly_detection:
                anomalies = await self._detect_anomalies(events)
                if anomalies:
                    await self._handle_anomalies(anomalies)
            
            # Correlação de eventos
            if self.enable_correlation:
                correlations = await self._correlate_events(events)
                if correlations:
                    await self._handle_correlations(correlations)
            
            # Armazenar eventos no Redis
            await self._store_events(events)
            
            # Log estruturado
            await self._log_events(events)
            
        except Exception as e:
            logger.error(f"Erro ao processar eventos: {str(e)}")
    
    async def _detect_anomalies(self, events: List[Event]) -> List[Event]:
        """Detecta anomalias nos eventos"""
        anomalies = []
        
        try:
            # Preparar dados para detecção de anomalias
            event_data = []
            for event in events:
                if event.type in [EventType.SYSTEM_METRIC, EventType.PERFORMANCE_METRIC]:
                    if 'value' in event.data:
                        event_data.append({
                            'event_id': event.id,
                            'value': event.data['value'],
                            'timestamp': event.timestamp.timestamp(),
                            'type': event.type.value
                        })
            
            if event_data:
                # Detectar anomalias usando o detector existente
                anomaly_results = await self.anomaly_detector.detect_anomalies(event_data)
                
                for result in anomaly_results:
                    if result['is_anomaly']:
                        # Encontrar evento correspondente
                        for event in events:
                            if event.id == result['event_id']:
                                event.metadata['anomaly_score'] = result['score']
                                event.metadata['anomaly_type'] = result['type']
                                anomalies.append(event)
                                break
            
        except Exception as e:
            logger.error(f"Erro na detecção de anomalias: {str(e)}")
        
        return anomalies
    
    async def _correlate_events(self, events: List[Event]) -> List[Dict[str, Any]]:
        """Correlaciona eventos relacionados"""
        correlations = []
        
        try:
            # Agrupar eventos por correlation_id
            events_by_correlation = {}
            for event in events:
                if event.correlation_id:
                    if event.correlation_id not in events_by_correlation:
                        events_by_correlation[event.correlation_id] = []
                    events_by_correlation[event.correlation_id].append(event)
            
            # Identificar correlações
            for correlation_id, correlated_events in events_by_correlation.items():
                if len(correlated_events) > 1:
                    # Ordenar por timestamp
                    correlated_events.sort(key=lambda x: x.timestamp)
                    
                    correlation = {
                        'correlation_id': correlation_id,
                        'events': correlated_events,
                        'start_time': correlated_events[0].timestamp,
                        'end_time': correlated_events[-1].timestamp,
                        'duration': (correlated_events[-1].timestamp - correlated_events[0].timestamp).total_seconds(),
                        'event_types': list(set(e.type.value for e in correlated_events)),
                        'severities': list(set(e.severity.value for e in correlated_events))
                    }
                    correlations.append(correlation)
            
        except Exception as e:
            logger.error(f"Erro na correlação de eventos: {str(e)}")
        
        return correlations
    
    async def _handle_anomalies(self, anomalies: List[Event]):
        """Processa anomalias detectadas"""
        for anomaly in anomalies:
            try:
                # Criar alerta de anomalia
                alert_data = {
                    'type': 'anomaly_detected',
                    'event_id': anomaly.id,
                    'source': anomaly.source,
                    'severity': anomaly.severity.value,
                    'timestamp': anomaly.timestamp.isoformat(),
                    'anomaly_score': anomaly.metadata.get('anomaly_score'),
                    'anomaly_type': anomaly.metadata.get('anomaly_type'),
                    'data': anomaly.data
                }
                
                # Armazenar alerta no Redis
                await self.redis_manager.set(
                    f"alert:anomaly:{anomaly.id}",
                    json.dumps(alert_data),
                    expire=3600  # 1 hora
                )
                
                logger.warning(f"Anomalia detectada: {anomaly.id} - Score: {anomaly.metadata.get('anomaly_score')}")
                
            except Exception as e:
                logger.error(f"Erro ao processar anomalia {anomaly.id}: {str(e)}")
    
    async def _handle_correlations(self, correlations: List[Dict[str, Any]]):
        """Processa correlações de eventos"""
        for correlation in correlations:
            try:
                # Criar registro de correlação
                correlation_data = {
                    'type': 'event_correlation',
                    'correlation_id': correlation['correlation_id'],
                    'event_count': len(correlation['events']),
                    'start_time': correlation['start_time'].isoformat(),
                    'end_time': correlation['end_time'].isoformat(),
                    'duration': correlation['duration'],
                    'event_types': correlation['event_types'],
                    'severities': correlation['severities']
                }
                
                # Armazenar correlação no Redis
                await self.redis_manager.set(
                    f"correlation:{correlation['correlation_id']}",
                    json.dumps(correlation_data),
                    expire=7200  # 2 horas
                )
                
                logger.info(f"Correlação detectada: {correlation['correlation_id']} - {len(correlation['events'])} eventos")
                
            except Exception as e:
                logger.error(f"Erro ao processar correlação {correlation['correlation_id']}: {str(e)}")
    
    async def _store_events(self, events: List[Event]):
        """Armazena eventos no Redis"""
        try:
            for event in events:
                # Armazenar evento individual
                event_key = f"event:{event.id}"
                event_data = {
                    'id': event.id,
                    'type': event.type.value,
                    'source': event.source,
                    'severity': event.severity.value,
                    'timestamp': event.timestamp.isoformat(),
                    'data': event.data,
                    'metadata': event.metadata,
                    'correlation_id': event.correlation_id,
                    'user_id': event.user_id,
                    'session_id': event.session_id
                }
                
                await self.redis_manager.set(
                    event_key,
                    json.dumps(event_data),
                    expire=86400  # 24 horas
                )
                
                # Adicionar à lista de eventos por tipo
                type_key = f"events:type:{event.type.value}"
                await self.redis_manager.lpush(type_key, event.id)
                await self.redis_manager.expire(type_key, 86400)
                
                # Adicionar à lista de eventos por severidade
                severity_key = f"events:severity:{event.severity.value}"
                await self.redis_manager.lpush(severity_key, event.id)
                await self.redis_manager.expire(severity_key, 86400)
                
        except Exception as e:
            logger.error(f"Erro ao armazenar eventos: {str(e)}")
    
    async def _log_events(self, events: List[Event]):
        """Registra eventos usando logger estruturado"""
        try:
            for event in events:
                log_data = {
                    'event_id': event.id,
                    'event_type': event.type.value,
                    'source': event.source,
                    'severity': event.severity.value,
                    'timestamp': event.timestamp.isoformat(),
                    'data': event.data,
                    'correlation_id': event.correlation_id,
                    'user_id': event.user_id
                }
                
                await self.structured_logger.log_event(log_data)
                
        except Exception as e:
            logger.error(f"Erro ao registrar eventos: {str(e)}")
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Retorna status de saúde do sistema"""
        return {
            'is_running': self.is_running,
            'active_sources': len([s for s in self.sources if s.is_active]),
            'total_sources': len(self.sources),
            'recent_events_count': len(self.recent_events),
            'collection_interval': self.collection_interval,
            'sources_health': [source.get_health_status() for source in self.sources]
        }
    
    async def get_events_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Retorna resumo dos eventos das últimas horas"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Filtrar eventos recentes
            recent_events = [
                event for event in self.recent_events
                if event.timestamp >= cutoff_time
            ]
            
            # Estatísticas por tipo
            events_by_type = {}
            for event in recent_events:
                event_type = event.type.value
                if event_type not in events_by_type:
                    events_by_type[event_type] = 0
                events_by_type[event_type] += 1
            
            # Estatísticas por severidade
            events_by_severity = {}
            for event in recent_events:
                severity = event.severity.value
                if severity not in events_by_severity:
                    events_by_severity[severity] = 0
                events_by_severity[severity] += 1
            
            # Estatísticas por fonte
            events_by_source = {}
            for event in recent_events:
                source = event.source
                if source not in events_by_source:
                    events_by_source[source] = 0
                events_by_source[source] += 1
            
            return {
                'period_hours': hours,
                'total_events': len(recent_events),
                'events_by_type': events_by_type,
                'events_by_severity': events_by_severity,
                'events_by_source': events_by_source,
                'start_time': cutoff_time.isoformat(),
                'end_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter resumo de eventos: {str(e)}")
            return {
                'period_hours': hours,
                'total_events': 0,
                'events_by_type': {},
                'events_by_severity': {},
                'events_by_source': {},
                'error': str(e)
            } 