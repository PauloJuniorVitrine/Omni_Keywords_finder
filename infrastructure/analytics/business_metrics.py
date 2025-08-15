#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 BUSINESS METRICS - OMNİ KEYWORDS FINDER

Tracing ID: business-metrics-2025-01-27-001
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

Sistema avançado de métricas de negócio com:
- User engagement metrics
- Conversion funnels
- Revenue impact tracking
- A/B testing metrics
- Cohort analysis
- Retention metrics
"""

import os
import json
import time
import logging
import asyncio
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import threading
from enum import Enum
import sqlite3
from pathlib import Path

# Dependências opcionais
try:
    import pandas as pd
    import numpy as np
    from scipy import stats
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricCategory(Enum):
    """Categorias de métricas"""
    REVENUE = "revenue"
    USERS = "users"
    KEYWORDS = "keywords"
    CONVERSION = "conversion"
    ENGAGEMENT = "engagement"
    SYSTEM = "system"
    AB_TESTING = "ab_testing"
    COHORT = "cohort"

class MetricType(Enum):
    """Tipos de métricas"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    CUSTOM = "custom"

@dataclass
class BusinessMetric:
    """Estrutura de métrica de negócio"""
    name: str
    value: float
    unit: str
    category: MetricCategory
    timestamp: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    experiment_id: Optional[str] = None
    variant: Optional[str] = None
    trend: str = "stable"  # up, down, stable
    change_percent: float = 0.0
    target_value: Optional[float] = None
    alert_threshold: Optional[float] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ConversionFunnel:
    """Estrutura de funil de conversão"""
    name: str
    stages: List[str]
    values: List[int]
    conversion_rates: List[float]
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class CohortAnalysis:
    """Estrutura de análise de coorte"""
    cohort_date: date
    cohort_size: int
    retention_data: Dict[int, float]  # day -> retention_rate
    churn_data: Dict[int, float]      # day -> churn_rate
    revenue_data: Dict[int, float]    # day -> avg_revenue
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ABTestResult:
    """Estrutura de resultado de A/B test"""
    experiment_id: str
    variant_a: str
    variant_b: str
    metric_name: str
    variant_a_stats: Dict[str, float]
    variant_b_stats: Dict[str, float]
    p_value: float
    confidence_level: float
    lift: float
    statistical_power: float
    sample_size: int
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class BusinessMetricsCollector:
    """Coletor principal de métricas de negócio"""
    
    def __init__(self, 
                 db_path: str = "data/business_metrics.db",
                 enable_persistence: bool = True,
                 enable_real_time: bool = True):
        """
        Inicializa o coletor de métricas
        
        Args:
            db_path: Caminho para banco de dados
            enable_persistence: Habilita persistência em banco
            enable_real_time: Habilita processamento em tempo real
        """
        self.db_path = db_path
        self.enable_persistence = enable_persistence
        self.enable_real_time = enable_real_time
        
        # Inicializar banco de dados
        if self.enable_persistence:
            self._init_database()
        
        # Cache em memória
        self.metrics_cache = defaultdict(deque)
        self.funnels_cache = defaultdict(deque)
        self.cohorts_cache = defaultdict(deque)
        self.ab_tests_cache = defaultdict(deque)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Configurações
        self.config = {
            "max_cache_size": 10000,
            "retention_days": 90,
            "batch_size": 100,
            "flush_interval": 60,  # segundos
            "enable_aggregation": True
        }
        
        # Inicializar processamento em tempo real
        if self.enable_real_time:
            self._start_real_time_processing()
        
        logger.info("Business Metrics Collector inicializado")
    
    def _init_database(self):
        """Inicializa banco de dados"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabela de métricas
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS business_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        value REAL NOT NULL,
                        unit TEXT,
                        category TEXT NOT NULL,
                        timestamp DATETIME NOT NULL,
                        user_id TEXT,
                        session_id TEXT,
                        experiment_id TEXT,
                        variant TEXT,
                        trend TEXT,
                        change_percent REAL,
                        target_value REAL,
                        alert_threshold REAL,
                        metadata TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabela de funis de conversão
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS conversion_funnels (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        stages TEXT NOT NULL,
                        values TEXT NOT NULL,
                        conversion_rates TEXT NOT NULL,
                        timestamp DATETIME NOT NULL,
                        metadata TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabela de coortes
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS cohort_analyses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cohort_date DATE NOT NULL,
                        cohort_size INTEGER NOT NULL,
                        retention_data TEXT NOT NULL,
                        churn_data TEXT NOT NULL,
                        revenue_data TEXT NOT NULL,
                        metadata TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabela de A/B tests
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ab_test_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        experiment_id TEXT NOT NULL,
                        variant_a TEXT NOT NULL,
                        variant_b TEXT NOT NULL,
                        metric_name TEXT NOT NULL,
                        variant_a_stats TEXT NOT NULL,
                        variant_b_stats TEXT NOT NULL,
                        p_value REAL NOT NULL,
                        confidence_level REAL NOT NULL,
                        lift REAL NOT NULL,
                        statistical_power REAL NOT NULL,
                        sample_size INTEGER NOT NULL,
                        timestamp DATETIME NOT NULL,
                        metadata TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Índices para performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_name ON business_metrics(name)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_category ON business_metrics(category)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON business_metrics(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_user ON business_metrics(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_experiment ON business_metrics(experiment_id)")
                
                conn.commit()
                
            logger.info(f"Banco de dados inicializado: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de dados: {e}")
            self.enable_persistence = False
    
    def _start_real_time_processing(self):
        """Inicia processamento em tempo real"""
        def real_time_worker():
            while True:
                try:
                    time.sleep(self.config["flush_interval"])
                    self._flush_cache_to_db()
                except Exception as e:
                    logger.error(f"Erro no processamento em tempo real: {e}")
        
        thread = threading.Thread(target=real_time_worker, daemon=True)
        thread.start()
        logger.info("Processamento em tempo real iniciado")
    
    def record_metric(self, metric: BusinessMetric):
        """Registra uma métrica de negócio"""
        try:
            with self._lock:
                # Adicionar ao cache
                self.metrics_cache[metric.name].append(metric)
                
                # Limitar tamanho do cache
                if len(self.metrics_cache[metric.name]) > self.config["max_cache_size"]:
                    self.metrics_cache[metric.name].popleft()
                
                # Salvar no banco se persistência estiver habilitada
                if self.enable_persistence:
                    self._save_metric_to_db(metric)
                
                # Processar agregações em tempo real
                if self.config["enable_aggregation"]:
                    self._process_real_time_aggregations(metric)
                
        except Exception as e:
            logger.error(f"Erro ao registrar métrica {metric.name}: {e}")
    
    def _save_metric_to_db(self, metric: BusinessMetric):
        """Salva métrica no banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO business_metrics 
                    (name, value, unit, category, timestamp, user_id, session_id, 
                     experiment_id, variant, trend, change_percent, target_value, 
                     alert_threshold, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metric.name,
                    metric.value,
                    metric.unit,
                    metric.category.value,
                    metric.timestamp.isoformat(),
                    metric.user_id,
                    metric.session_id,
                    metric.experiment_id,
                    metric.variant,
                    metric.trend,
                    metric.change_percent,
                    metric.target_value,
                    metric.alert_threshold,
                    json.dumps(metric.metadata)
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Erro ao salvar métrica no banco: {e}")
    
    def _process_real_time_aggregations(self, metric: BusinessMetric):
        """Processa agregações em tempo real"""
        # Implementar agregações como médias móveis, tendências, etc.
        pass
    
    def _flush_cache_to_db(self):
        """Flush do cache para banco de dados"""
        # Implementar flush em lote para melhor performance
        pass
    
    # Métricas de User Engagement
    def track_user_engagement(self, 
                            user_id: str,
                            session_id: str,
                            action_type: str,
                            duration: Optional[float] = None,
                            page_views: Optional[int] = None,
                            **kwargs):
        """Registra engajamento do usuário"""
        metric = BusinessMetric(
            name="user_engagement",
            value=1.0,
            unit="actions",
            category=MetricCategory.ENGAGEMENT,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            session_id=session_id,
            metadata={
                "action_type": action_type,
                "duration": duration,
                "page_views": page_views,
                **kwargs
            }
        )
        self.record_metric(metric)
    
    def track_session_duration(self, 
                             user_id: str,
                             session_id: str,
                             duration: float):
        """Registra duração da sessão"""
        metric = BusinessMetric(
            name="session_duration",
            value=duration,
            unit="seconds",
            category=MetricCategory.ENGAGEMENT,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            session_id=session_id
        )
        self.record_metric(metric)
    
    def track_page_views(self, 
                        user_id: str,
                        session_id: str,
                        page: str,
                        time_on_page: Optional[float] = None):
        """Registra visualizações de página"""
        metric = BusinessMetric(
            name="page_views",
            value=1.0,
            unit="views",
            category=MetricCategory.ENGAGEMENT,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            session_id=session_id,
            metadata={
                "page": page,
                "time_on_page": time_on_page
            }
        )
        self.record_metric(metric)
    
    # Métricas de Conversão
    def track_conversion_funnel(self, 
                               funnel_name: str,
                               stages: List[str],
                               values: List[int]):
        """Registra funil de conversão"""
        if len(stages) != len(values):
            raise ValueError("Número de estágios deve ser igual ao número de valores")
        
        # Calcular taxas de conversão
        conversion_rates = []
        for index in range(len(values)):
            if index == 0:
                conversion_rates.append(100.0)  # Primeiro estágio sempre 100%
            else:
                rate = (values[index] / values[0]) * 100 if values[0] > 0 else 0
                conversion_rates.append(rate)
        
        funnel = ConversionFunnel(
            name=funnel_name,
            stages=stages,
            values=values,
            conversion_rates=conversion_rates,
            timestamp=datetime.utcnow()
        )
        
        # Adicionar ao cache
        with self._lock:
            self.funnels_cache[funnel_name].append(funnel)
            
            # Salvar no banco
            if self.enable_persistence:
                self._save_funnel_to_db(funnel)
    
    def _save_funnel_to_db(self, funnel: ConversionFunnel):
        """Salva funil no banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO conversion_funnels 
                    (name, stages, values, conversion_rates, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    funnel.name,
                    json.dumps(funnel.stages),
                    json.dumps(funnel.values),
                    json.dumps(funnel.conversion_rates),
                    funnel.timestamp.isoformat(),
                    json.dumps(funnel.metadata)
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Erro ao salvar funil no banco: {e}")
    
    # Métricas de Receita
    def track_revenue(self, 
                     amount: float,
                     user_id: Optional[str] = None,
                     source: Optional[str] = None,
                     product: Optional[str] = None):
        """Registra receita"""
        metric = BusinessMetric(
            name="revenue",
            value=amount,
            unit="USD",
            category=MetricCategory.REVENUE,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            metadata={
                "source": source,
                "product": product
            }
        )
        self.record_metric(metric)
    
    def track_conversion_value(self, 
                             value: float,
                             user_id: str,
                             conversion_type: str):
        """Registra valor de conversão"""
        metric = BusinessMetric(
            name="conversion_value",
            value=value,
            unit="USD",
            category=MetricCategory.CONVERSION,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            metadata={
                "conversion_type": conversion_type
            }
        )
        self.record_metric(metric)
    
    # Métricas de A/B Testing
    def track_ab_test_event(self, 
                           experiment_id: str,
                           variant: str,
                           user_id: str,
                           event_type: str,
                           value: Optional[float] = None):
        """Registra evento de A/B test"""
        metric = BusinessMetric(
            name=f"ab_test_{event_type}",
            value=value or 1.0,
            unit="events",
            category=MetricCategory.AB_TESTING,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            experiment_id=experiment_id,
            variant=variant,
            metadata={
                "event_type": event_type
            }
        )
        self.record_metric(metric)
    
    def record_ab_test_result(self, result: ABTestResult):
        """Registra resultado de A/B test"""
        with self._lock:
            self.ab_tests_cache[result.experiment_id].append(result)
            
            if self.enable_persistence:
                self._save_ab_test_to_db(result)
    
    def _save_ab_test_to_db(self, result: ABTestResult):
        """Salva resultado de A/B test no banco"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO ab_test_results 
                    (experiment_id, variant_a, variant_b, metric_name, variant_a_stats,
                     variant_b_stats, p_value, confidence_level, lift, statistical_power,
                     sample_size, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    result.experiment_id,
                    result.variant_a,
                    result.variant_b,
                    result.metric_name,
                    json.dumps(result.variant_a_stats),
                    json.dumps(result.variant_b_stats),
                    result.p_value,
                    result.confidence_level,
                    result.lift,
                    result.statistical_power,
                    result.sample_size,
                    result.timestamp.isoformat(),
                    json.dumps(result.metadata)
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Erro ao salvar A/B test no banco: {e}")
    
    # Análise de Coortes
    def calculate_cohort_analysis(self, 
                                cohort_date: date,
                                cohort_size: int,
                                retention_data: Dict[int, float],
                                churn_data: Dict[int, float],
                                revenue_data: Dict[int, float]):
        """Calcula análise de coorte"""
        cohort = CohortAnalysis(
            cohort_date=cohort_date,
            cohort_size=cohort_size,
            retention_data=retention_data,
            churn_data=churn_data,
            revenue_data=revenue_data
        )
        
        with self._lock:
            self.cohorts_cache[cohort_date.isoformat()].append(cohort)
            
            if self.enable_persistence:
                self._save_cohort_to_db(cohort)
    
    def _save_cohort_to_db(self, cohort: CohortAnalysis):
        """Salva coorte no banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO cohort_analyses 
                    (cohort_date, cohort_size, retention_data, churn_data, revenue_data, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    cohort.cohort_date.isoformat(),
                    cohort.cohort_size,
                    json.dumps(cohort.retention_data),
                    json.dumps(cohort.churn_data),
                    json.dumps(cohort.revenue_data),
                    json.dumps(cohort.metadata)
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Erro ao salvar coorte no banco: {e}")
    
    # Consultas e Análises
    def get_metrics(self, 
                   metric_names: Optional[List[str]] = None,
                   category: Optional[MetricCategory] = None,
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None,
                   user_id: Optional[str] = None) -> Dict[str, List[BusinessMetric]]:
        """Obtém métricas filtradas"""
        try:
            with self._lock:
                if start_time is None:
                    start_time = datetime.utcnow() - timedelta(hours=24)
                if end_time is None:
                    end_time = datetime.utcnow()
                
                # Filtrar do cache primeiro
                result = {}
                for name, metrics in self.metrics_cache.items():
                    if metric_names and name not in metric_names:
                        continue
                    
                    filtered_metrics = [
                        m for m in metrics
                        if start_time <= m.timestamp <= end_time
                        and (category is None or m.category == category)
                        and (user_id is None or m.user_id == user_id)
                    ]
                    
                    if filtered_metrics:
                        result[name] = filtered_metrics
                
                # Se não encontrou no cache, buscar no banco
                if not result and self.enable_persistence:
                    result = self._get_metrics_from_db(
                        metric_names, category, start_time, end_time, user_id
                    )
                
                return result
                
        except Exception as e:
            logger.error(f"Erro ao obter métricas: {e}")
            return {}
    
    def _get_metrics_from_db(self, 
                           metric_names: Optional[List[str]],
                           category: Optional[MetricCategory],
                           start_time: datetime,
                           end_time: datetime,
                           user_id: Optional[str]) -> Dict[str, List[BusinessMetric]]:
        """Obtém métricas do banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT name, value, unit, category, timestamp, user_id, session_id,
                           experiment_id, variant, trend, change_percent, target_value,
                           alert_threshold, metadata
                    FROM business_metrics
                    WHERE timestamp BETWEEN ? AND ?
                """
                params = [start_time.isoformat(), end_time.isoformat()]
                
                if metric_names:
                    placeholders = ','.join(['?' for _ in metric_names])
                    query += f" AND name IN ({placeholders})"
                    params.extend(metric_names)
                
                if category:
                    query += " AND category = ?"
                    params.append(category.value)
                
                if user_id:
                    query += " AND user_id = ?"
                    params.append(user_id)
                
                query += " ORDER BY timestamp DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                result = defaultdict(list)
                for row in rows:
                    metric = BusinessMetric(
                        name=row[0],
                        value=row[1],
                        unit=row[2],
                        category=MetricCategory(row[3]),
                        timestamp=datetime.fromisoformat(row[4]),
                        user_id=row[5],
                        session_id=row[6],
                        experiment_id=row[7],
                        variant=row[8],
                        trend=row[9],
                        change_percent=row[10],
                        target_value=row[11],
                        alert_threshold=row[12],
                        metadata=json.loads(row[13]) if row[13] else {}
                    )
                    result[metric.name].append(metric)
                
                return dict(result)
                
        except Exception as e:
            logger.error(f"Erro ao obter métricas do banco: {e}")
            return {}
    
    def get_conversion_funnels(self, 
                              funnel_name: Optional[str] = None,
                              start_time: Optional[datetime] = None,
                              end_time: Optional[datetime] = None) -> List[ConversionFunnel]:
        """Obtém funis de conversão"""
        try:
            with self._lock:
                if start_time is None:
                    start_time = datetime.utcnow() - timedelta(days=7)
                if end_time is None:
                    end_time = datetime.utcnow()
                
                result = []
                for name, funnels in self.funnels_cache.items():
                    if funnel_name and name != funnel_name:
                        continue
                    
                    filtered_funnels = [
                        f for f in funnels
                        if start_time <= f.timestamp <= end_time
                    ]
                    result.extend(filtered_funnels)
                
                return result
                
        except Exception as e:
            logger.error(f"Erro ao obter funis de conversão: {e}")
            return []
    
    def get_cohort_analyses(self, 
                           start_date: Optional[date] = None,
                           end_date: Optional[date] = None) -> List[CohortAnalysis]:
        """Obtém análises de coorte"""
        try:
            with self._lock:
                if start_date is None:
                    start_date = date.today() - timedelta(days=30)
                if end_date is None:
                    end_date = date.today()
                
                result = []
                for cohort_date_str, cohorts in self.cohorts_cache.items():
                    cohort_date = date.fromisoformat(cohort_date_str)
                    if start_date <= cohort_date <= end_date:
                        result.extend(cohorts)
                
                return result
                
        except Exception as e:
            logger.error(f"Erro ao obter análises de coorte: {e}")
            return []
    
    def get_ab_test_results(self, 
                           experiment_id: Optional[str] = None,
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None) -> List[ABTestResult]:
        """Obtém resultados de A/B tests"""
        try:
            with self._lock:
                if start_time is None:
                    start_time = datetime.utcnow() - timedelta(days=30)
                if end_time is None:
                    end_time = datetime.utcnow()
                
                result = []
                for exp_id, results in self.ab_tests_cache.items():
                    if experiment_id and exp_id != experiment_id:
                        continue
                    
                    filtered_results = [
                        r for r in results
                        if start_time <= r.timestamp <= end_time
                    ]
                    result.extend(filtered_results)
                
                return result
                
        except Exception as e:
            logger.error(f"Erro ao obter resultados de A/B tests: {e}")
            return []
    
    # Relatórios e Análises
    def generate_revenue_report(self, 
                              start_date: date,
                              end_date: date) -> Dict[str, Any]:
        """Gera relatório de receita"""
        try:
            start_time = datetime.combine(start_date, datetime.min.time())
            end_time = datetime.combine(end_date, datetime.max.time())
            
            metrics = self.get_metrics(
                metric_names=["revenue", "conversion_value"],
                category=MetricCategory.REVENUE,
                start_time=start_time,
                end_time=end_time
            )
            
            # Calcular métricas agregadas
            total_revenue = sum(m.value for metrics_list in metrics.values() for m in metrics_list)
            avg_revenue = total_revenue / len([m for metrics_list in metrics.values() for m in metrics_list]) if metrics else 0
            
            # Calcular crescimento
            previous_start = start_date - timedelta(days=(end_date - start_date).days)
            previous_end = start_date - timedelta(days=1)
            previous_metrics = self.get_metrics(
                metric_names=["revenue"],
                category=MetricCategory.REVENUE,
                start_time=datetime.combine(previous_start, datetime.min.time()),
                end_time=datetime.combine(previous_end, datetime.max.time())
            )
            
            previous_revenue = sum(m.value for metrics_list in previous_metrics.values() for m in metrics_list)
            growth_rate = ((total_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "total_revenue": total_revenue,
                "average_revenue": avg_revenue,
                "growth_rate": growth_rate,
                "transaction_count": len([m for metrics_list in metrics.values() for m in metrics_list]),
                "metrics": metrics
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório de receita: {e}")
            return {"error": str(e)}
    
    def generate_user_engagement_report(self, 
                                      start_date: date,
                                      end_date: date) -> Dict[str, Any]:
        """Gera relatório de engajamento de usuários"""
        try:
            start_time = datetime.combine(start_date, datetime.min.time())
            end_time = datetime.combine(end_date, datetime.max.time())
            
            metrics = self.get_metrics(
                metric_names=["user_engagement", "session_duration", "page_views"],
                category=MetricCategory.ENGAGEMENT,
                start_time=start_time,
                end_time=end_time
            )
            
            # Calcular métricas de engajamento
            total_actions = sum(m.value for metrics_list in metrics.values() for m in metrics_list)
            unique_users = len(set(m.user_id for metrics_list in metrics.values() for m in metrics_list if m.user_id))
            avg_session_duration = sum(m.value for metrics_list in metrics.values() for m in metrics_list if m.name == "session_duration") / len([m for metrics_list in metrics.values() for m in metrics_list if m.name == "session_duration"]) if any(m.name == "session_duration" for metrics_list in metrics.values() for m in metrics_list) else 0
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "total_actions": total_actions,
                "unique_users": unique_users,
                "average_session_duration": avg_session_duration,
                "actions_per_user": total_actions / unique_users if unique_users > 0 else 0,
                "metrics": metrics
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório de engajamento: {e}")
            return {"error": str(e)}
    
    def generate_conversion_report(self, 
                                 start_date: date,
                                 end_date: date) -> Dict[str, Any]:
        """Gera relatório de conversão"""
        try:
            start_time = datetime.combine(start_date, datetime.min.time())
            end_time = datetime.combine(end_date, datetime.max.time())
            
            # Obter funis de conversão
            funnels = self.get_conversion_funnels(
                start_time=start_time,
                end_time=end_time
            )
            
            # Obter métricas de conversão
            metrics = self.get_metrics(
                metric_names=["conversion_value"],
                category=MetricCategory.CONVERSION,
                start_time=start_time,
                end_time=end_time
            )
            
            # Calcular métricas agregadas
            total_conversion_value = sum(m.value for metrics_list in metrics.values() for m in metrics_list)
            conversion_count = len([m for metrics_list in metrics.values() for m in metrics_list])
            avg_conversion_value = total_conversion_value / conversion_count if conversion_count > 0 else 0
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "total_conversion_value": total_conversion_value,
                "conversion_count": conversion_count,
                "average_conversion_value": avg_conversion_value,
                "funnels": [asdict(funnel) for funnel in funnels],
                "metrics": metrics
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório de conversão: {e}")
            return {"error": str(e)}
    
    def export_data(self, 
                   format_type: str = "json",
                   start_date: Optional[date] = None,
                   end_date: Optional[date] = None,
                   categories: Optional[List[MetricCategory]] = None) -> str:
        """Exporta dados de métricas"""
        try:
            if start_date is None:
                start_date = date.today() - timedelta(days=30)
            if end_date is None:
                end_date = date.today()
            
            start_time = datetime.combine(start_date, datetime.min.time())
            end_time = datetime.combine(end_date, datetime.max.time())
            
            # Obter métricas
            metrics = self.get_metrics(
                start_time=start_time,
                end_time=end_time
            )
            
            # Filtrar por categoria se especificado
            if categories:
                filtered_metrics = {}
                for name, metric_list in metrics.items():
                    filtered_list = [m for m in metric_list if m.category in categories]
                    if filtered_list:
                        filtered_metrics[name] = filtered_list
                metrics = filtered_metrics
            
            # Converter para formato desejado
            if format_type == "json":
                return json.dumps(metrics, default=str, indent=2)
            elif format_type == "csv" and PANDAS_AVAILABLE:
                # Converter para DataFrame e exportar CSV
                all_metrics = []
                for metric_name, metric_list in metrics.items():
                    for metric in metric_list:
                        all_metrics.append({
                            "name": metric.name,
                            "value": metric.value,
                            "unit": metric.unit,
                            "category": metric.category.value,
                            "timestamp": metric.timestamp.isoformat(),
                            "user_id": metric.user_id,
                            "trend": metric.trend,
                            "change_percent": metric.change_percent,
                            "metadata": json.dumps(metric.metadata)
                        })
                
                df = pd.DataFrame(all_metrics)
                csv_path = f"exports/business_metrics_{start_date.strftime('%Y%m%data')}_{end_date.strftime('%Y%m%data')}.csv"
                os.makedirs("exports", exist_ok=True)
                df.to_csv(csv_path, index=False)
                return csv_path
            else:
                return f"Formato não suportado: {format_type}"
                
        except Exception as e:
            logger.error(f"Erro ao exportar dados: {e}")
            return f"Erro na exportação: {e}"

# Instância global
_collector_instance = None

def get_business_metrics_collector() -> BusinessMetricsCollector:
    """Obtém instância global do coletor"""
    global _collector_instance
    if _collector_instance is None:
        _collector_instance = BusinessMetricsCollector()
    return _collector_instance

def record_business_metric(name: str, value: float, unit: str = "", 
                          category: MetricCategory = MetricCategory.GENERAL, **kwargs):
    """Função de conveniência para registrar métrica"""
    collector = get_business_metrics_collector()
    metric = BusinessMetric(
        name=name,
        value=value,
        unit=unit,
        category=category,
        timestamp=datetime.utcnow(),
        **kwargs
    )
    collector.record_metric(metric)

if __name__ == "__main__":
    # Exemplo de uso
    collector = BusinessMetricsCollector()
    
    # Registrar métricas de exemplo
    record_business_metric("daily_revenue", 15000.0, "USD", MetricCategory.REVENUE)
    record_business_metric("active_users", 1250, "users", MetricCategory.USERS)
    record_business_metric("keywords_processed", 5000, "keywords", MetricCategory.KEYWORDS)
    record_business_metric("conversion_rate", 3.2, "%", MetricCategory.CONVERSION)
    
    # Registrar engajamento
    collector.track_user_engagement("user123", "session456", "page_view", duration=120)
    collector.track_session_duration("user123", "session456", 1800)
    
    # Registrar funil de conversão
    collector.track_conversion_funnel(
        "signup_funnel",
        ["Visitas", "Registros", "Ativações", "Pagamentos"],
        [1000, 100, 50, 25]
    )
    
    # Gerar relatórios
    revenue_report = collector.generate_revenue_report(
        date.today() - timedelta(days=30),
        date.today()
    )
    print("Relatório de Receita:", revenue_report) 